"""
04_query_decomposition.py
Experiment 9.04: Query Decomposition

Split a compound question into independently retrievable subquestions.

An LLM identifies the information needs, and Chroma retrieves evidence
for each subquestion separately without combining their rankings.


Workflow:
    1. Open the existing Teralune collection.
    2. Decompose the compound question into subquestions.
    3. Retrieve the baseline and subquestion rankings.
    4. Compare evidence coverage with the baseline.

Expected result:
    Different subquestions may retrieve different supporting chunks.
    Decomposition does not verify answers or perform multi-hop reasoning.

Run:
    uv run python 09_advanced_rag/04_query_decomposition.py
"""

import json
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "teralune_corpus"
EMBEDDING_MODEL = "text-embedding-3-small"
QUERY_MODEL = "gpt-4.1-mini"
QUESTION = (
    "How long does Orbit 3.0 retry failed webhook deliveries, "
    "and what should the receiver do when delivery fails?"
)
TOP_K = 5

DECOMPOSITION_PROMPT = (
    "Decompose the user's question into the smallest set of independent "
    "factual subquestions needed to answer it completely. "
    "Create between two and four subquestions. Each must be understandable "
    "without the original question and suitable for document retrieval. "
    "Preserve product names, versions, and explicit constraints. "
    "Do not invent facts, answer the questions, or add unrelated topics. "
    "Return only a JSON array of strings."
)

DECOMPOSITION_FORMAT = {
    "type": "json_schema",
    "name": "query_decomposition",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "subquestions": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "required": ["subquestions"],
        "additionalProperties": False,
    },
}


def decompose_question(client: OpenAI, question: str) -> list[str]:
    """Decompose a compound question into factual subquestions."""
    response = client.responses.create(
        model=QUERY_MODEL,
        instructions=DECOMPOSITION_PROMPT,
        input=question,
        text={"format": DECOMPOSITION_FORMAT},
    )

    return json.loads(response.output_text)["subquestions"]


def retrieve(
    client: OpenAI,
    collection: chromadb.Collection,
    query: str,
) -> list[tuple[str, str]]:
    """Retrieve chunk IDs and text excerpts for one subquestion."""
    embedding = (
        client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query,
        )
        .data[0]
        .embedding
    )

    results = collection.query(
        query_embeddings=[embedding],
        n_results=TOP_K,
        include=["documents"],
    )

    ids = results["ids"][0]
    documents = results["documents"][0]

    return [
        (chunk_id, " ".join(document.split())[:250])
        for chunk_id, document in zip(ids, documents, strict=True)
    ]


def main() -> None:
    """Inspect the retrieval coverage of decomposed subquestions."""
    client = OpenAI()

    # 1. Open the existing Teralune collection.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        name=COLLECTION_NAME
    )

    # 2. Decompose the compound question into subquestions.
    subquestions = decompose_question(client, QUESTION)
    print(f"Question: {QUESTION}")
    for index, question in enumerate(subquestions, start=1):
        print(f"Subquestion {index}: {question}")

    # 3. Retrieve the baseline and subquestion rankings.
    baseline = retrieve(client, collection, QUESTION)
    rankings = [retrieve(client, collection, question) for question in subquestions]

    print("\nBaseline:")
    for rank, (chunk_id, excerpt) in enumerate(baseline, start=1):
        print(f"  {rank}. {chunk_id}")
        print(f"     {excerpt}...")

    for index, ranking in enumerate(rankings, start=1):
        print(f"\nSubquestion {index}:")
        for rank, (chunk_id, excerpt) in enumerate(ranking, start=1):
            print(f"  {rank}. {chunk_id}")
            print(f"     {excerpt}...")

    # 4. Compare evidence coverage with the baseline.
    baseline_ids = {chunk_id for chunk_id, _ in baseline}
    subquestion_ids = [{chunk_id for chunk_id, _ in ranking} for ranking in rankings]

    unique_chunks = set.union(*subquestion_ids)
    shared_chunks = set.intersection(*subquestion_ids)
    new_chunks = unique_chunks - baseline_ids

    print(f"\nBaseline chunks: {len(baseline_ids)}")
    print(f"Unique decomposition chunks: {len(unique_chunks)}")
    print(f"Chunks shared by all subquestions: {len(shared_chunks)}")
    print(f"Additional chunks: {len(new_chunks)}")
    print(f"Additional chunk IDs: {', '.join(sorted(new_chunks)) or 'None'}")


if __name__ == "__main__":
    main()
