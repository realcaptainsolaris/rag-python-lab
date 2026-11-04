"""
Experiment 5.05: Missing and Conflicting Evidence

Test how an LLM responds to missing and contradictory evidence.

The first scenario provides context without the requested information.
The second scenario combines a real Teralune source with a simulated
source that contradicts the documented token lifetime.


Workflow:
    1. Load relevant document chunks from Chroma.
    2. Create contexts with missing and conflicting evidence.
    3. Ask the LLM to answer using only the supplied evidence.
    4. Display the answers for both scenarios.

Expected result:
    The model should acknowledge missing evidence in the first scenario.
    In the second scenario, it should identify the conflicting token
    lifetimes rather than silently selecting one value.

Run:
    uv run python 05_context_engineering/05_missing_and_conflicting_evidence.py
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"
MODEL = "gpt-4.1-mini"

QUESTION = "How long is an Orbit 3 access token valid?"


def ask_model(client: OpenAI, context: str) -> str:
    """Generate an answer grounded in the supplied context."""
    response = client.responses.create(
        model=MODEL,
        instructions=(
            "Answer using only the supplied context. "
            "If the information is missing, say so. "
            "If sources contradict each other, explicitly describe "
            "the conflict. Do not guess or resolve conflicts without "
            "supporting evidence. Cite source IDs."
        ),
        input=f"Context:\n{context}\n\nQuestion: {QUESTION}",
    )
    return response.output_text


def main() -> None:
    """Compare model behavior with missing and conflicting evidence."""
    load_dotenv(PROJECT_DIR / ".env")
    client = OpenAI()

    # 1. Load relevant document chunks from Chroma.
    chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = chroma.get_collection(COLLECTION_NAME)

    result = collection.get(
        ids=["D002-chunk-1", "D033-chunk-2"],
        include=["documents"],
    )

    documents = dict(zip(result["ids"], result["documents"]))
    required_ids = {"D002-chunk-1", "D033-chunk-2"}

    if not required_ids.issubset(documents):
        raise ValueError("Required Teralune chunks are missing.")

    # 2. Create contexts with missing and conflicting evidence.
    missing_context = f"[Source: D033-chunk-2]\n{documents['D033-chunk-2']}"

    conflicting_context = (
        f"[Source: D002-chunk-1]\n"
        f"{documents['D002-chunk-1']}\n\n"
        "[Source: SIMULATED-CONFLICT]\n"
        "Orbit 3.0 access tokens are valid for 90 minutes."
    )

    # 3. Ask the LLM to answer using only the supplied evidence.
    missing_answer = ask_model(client, missing_context)
    conflicting_answer = ask_model(client, conflicting_context)

    # 4. Display the answers for both scenarios.
    print(f"Question: {QUESTION}\n")
    print(f"Missing evidence: {missing_answer}\n")
    print(f"Conflicting evidence: {conflicting_answer}")


if __name__ == "__main__":
    main()
