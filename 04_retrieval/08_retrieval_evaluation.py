"""
08_retrieval_evaluation.py
Experiment 4.08: Retrieval Evaluation

Check whether dense retrieval finds a known relevant document.

Workflow:
    1. Define the question and expected document chunk.
    2. Connect to the existing Chroma collection.
    3. Generate the question embedding.
    4. Retrieve the top three chunks.
    5. Check whether the expected chunk was retrieved (Hit@3).

Expected result:
    The output shows the three retrieved chunks and whether
    the expected document appears among them.

Run:
    uv run python 04_retrieval/08_retrieval_evaluation.py
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

# 1. Define the question and expected document chunk.
QUESTION = "How long does a cursor remain valid?"
EXPECTED_CHUNK = "D022-chunk-2"
TOP_K = 3


def main() -> None:
    load_dotenv(PROJECT_DIR / ".env")

    # 2. Connect to the existing Chroma collection.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        "teralune_corpus"
    )

    # 3. Generate the question embedding.
    embedding = (
        OpenAI()
        .embeddings.create(
            model="text-embedding-3-small",
            input=QUESTION,
        )
        .data[0]
        .embedding
    )

    # 4. Retrieve the three nearest chunks.
    results = collection.query(
        query_embeddings=[embedding],
        n_results=TOP_K,
        include=["metadatas"],
    )

    retrieved_ids = results["ids"][0]
    metadatas = results["metadatas"][0]

    # 5. Check whether the expected chunk was retrieved (Hit@3).
    hit = EXPECTED_CHUNK in retrieved_ids

    print(f"Question: {QUESTION}")
    print(f"Expected chunk: {EXPECTED_CHUNK}")
    print(f"\nDense Top {TOP_K}:")

    for rank, (chunk_id, metadata) in enumerate(zip(retrieved_ids, metadatas), start=1):
        marker = " <-- EXPECTED" if chunk_id == EXPECTED_CHUNK else ""
        print(f"  {rank}. {chunk_id} | {metadata['headings']}{marker}")

    print(f"\nHit@{TOP_K}: {'YES' if hit else 'NO'}")


if __name__ == "__main__":
    main()
