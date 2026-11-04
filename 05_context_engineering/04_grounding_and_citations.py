"""
04_grounding_and_citations.py
Experiment 5.04: Grounding and Citations

Generate a source-cited answer and check its references.

Three current Orbit 3 chunks provide evidence for an access-token question.
The experiment checks whether cited chunk IDs belong to the supplied context
and separately verifies one known fact. Valid IDs alone do not prove grounding.


Workflow:
    1. Load three current Orbit 3 chunks from Chroma.
    2. Assemble a context with explicit source identifiers.
    3. Generate a concise answer with source citations.
    4. Validate cited identifiers and the expected token lifetime.
    5. Demonstrate that a valid citation can accompany a false claim.

Expected result:
    The generated answer should state a 60-minute lifetime and cite sources.
    The checks distinguish valid source identifiers from factual support.
    A deliberately false example fails the factual check despite a valid ID.

Run:
    uv run python 05_context_engineering/04_grounding_and_citations.py
"""

import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "teralune_corpus"
GENERATION_MODEL = "gpt-4.1-mini"
QUESTION = "How long is an Orbit 3 access token valid?"
CHUNK_IDS = ["D002-chunk-1", "D033-chunk-1", "D005-chunk-1"]
CITATION_PATTERN = r"\[(D\d{3}-chunk-\d+)\]"


def inspect_answer(answer: str, allowed_ids: set[str]) -> tuple[bool, bool]:
    """Check citation membership and the expected 60-minute answer."""
    cited_ids = set(re.findall(CITATION_PATTERN, answer))
    citations_valid = bool(cited_ids) and cited_ids <= allowed_ids
    fact_matches = bool(re.search(r"\b60[ -]minutes?\b", answer, re.I))
    return citations_valid, fact_matches


def main() -> None:
    """Compare citation validity with a narrow factual grounding check."""
    load_dotenv(PROJECT_DIR / ".env")

    # 1. Load three current Orbit 3 chunks from Chroma.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        COLLECTION_NAME
    )
    records = collection.get(ids=CHUNK_IDS, include=["documents", "metadatas"])
    chunks = {
        chunk_id: (document, metadata)
        for chunk_id, document, metadata in zip(
            records["ids"], records["documents"] or [], records["metadatas"] or []
        )
    }
    if set(chunks) != set(CHUNK_IDS):
        raise RuntimeError("Required chunks are missing from Chroma.")
    if any(chunks[chunk_id][1].get("version") != "3.0" for chunk_id in CHUNK_IDS):
        raise RuntimeError("Expected Orbit 3.0 documents.")

    # 2. Assemble a context with explicit source identifiers.
    context = "\n\n".join(
        f"[{chunk_id}]\n{chunks[chunk_id][0]}" for chunk_id in CHUNK_IDS
    )

    # 3. Generate a concise answer with source citations.
    client = OpenAI()
    response = client.responses.create(
        model=GENERATION_MODEL,
        instructions=(
            "Answer using only the provided sources. Cite factual claims "
            "using exact source IDs in square brackets, e.g. [D002-chunk-1]. "
            "If the sources do not answer the question, say so."
        ),
        input=f"Sources:\n{context}\n\nQuestion: {QUESTION}",
    )
    answer = response.output_text.strip()

    # 4. Validate cited identifiers and the expected token lifetime.
    valid_ids, correct_fact = inspect_answer(answer, set(CHUNK_IDS))
    print(f"Answer: {answer}")
    print(f"Citations reference supplied chunks: {valid_ids}")
    print(f"Expected fact (60 minutes) present: {correct_fact}")

    # 5. Demonstrate that a valid citation can accompany a false claim.
    false_answer = "The token lasts 90 minutes [D002-chunk-1]."
    false_ids, false_fact = inspect_answer(false_answer, set(CHUNK_IDS))
    print(f"False claim: valid citation={false_ids}, expected fact={false_fact}")
    print(
        "Note: This fact check is specific to this question, not general verification."
    )


if __name__ == "__main__":
    main()
