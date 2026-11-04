"""
04_hybrid_search.py
Experiment 4.04: Hybrid Search

Combine the results of dense retrieval and BM25.

Both methods search the same Teralune documents. Their results are
combined into a set of unique candidates without calculating a new ranking.

Expected result:
    The output shows which chunks both methods retrieve, which chunks
    only one method finds, and how many unique candidates remain.

Run:
    uv run python 04_retrieval/04_hybrid_search.py
"""

import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"
TOP_K = 5

QUESTION = "How long is an Orbit 3 access token valid?"


def tokenize(text: str) -> list[str]:
    """Split text into words while preserving technical identifiers."""
    return re.findall(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", text.lower())


def dense_search(collection, client: OpenAI, question: str) -> list[str]:
    """Retrieve semantically similar chunks from Chroma."""
    embedding = (
        client.embeddings.create(
            model="text-embedding-3-small",
            input=question,
        )
        .data[0]
        .embedding
    )

    results = collection.query(
        query_embeddings=[embedding],
        n_results=TOP_K,
    )

    return results["ids"][0]


def bm25_search(
    bm25: BM25Okapi,
    chunk_ids: list[str],
    question: str,
) -> list[str]:
    """Retrieve chunks with matching search terms."""
    scores = bm25.get_scores(tokenize(question))

    ranked = sorted(
        range(len(chunk_ids)),
        key=lambda i: (-scores[i], chunk_ids[i]),
    )

    return [chunk_ids[i] for i in ranked if scores[i] > 0][:TOP_K]


def main() -> None:
    load_dotenv(PROJECT_DIR / ".env")

    client = OpenAI()

    # 1. Open the existing Chroma collection.
    collection = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
    ).get_collection(COLLECTION_NAME)

    # 2. Load the same chunks for BM25.
    stored = collection.get(include=["documents", "metadatas"])

    chunk_ids = stored["ids"]
    documents = stored["documents"]

    bm25 = BM25Okapi([tokenize(text) for text in documents])

    headings = {
        chunk_id: metadata["headings"]
        for chunk_id, metadata in zip(
            chunk_ids,
            stored["metadatas"],
        )
    }

    # 3. Search with both methods.
    dense_results = dense_search(collection, client, QUESTION)
    bm25_results = bm25_search(bm25, chunk_ids, QUESTION)

    # 4. Combine the results without duplicates.
    dense_ids = set(dense_results)
    bm25_ids = set(bm25_results)

    shared = dense_ids & bm25_ids
    dense_only = dense_ids - bm25_ids
    bm25_only = bm25_ids - dense_ids
    combined = dense_ids | bm25_ids

    # 5. Display the candidate sets.
    print(f"Question: {QUESTION}")
    print(f"\nDense candidates: {len(dense_ids)}")
    print(f"BM25 candidates:  {len(bm25_ids)}")
    print(f"Shared:           {len(shared)}")
    print(f"Dense only:       {len(dense_only)}")
    print(f"BM25 only:        {len(bm25_only)}")
    print(f"Combined:         {len(combined)}")

    print("\nShared candidates:")
    for chunk_id in sorted(shared):
        print(f"  {chunk_id} | {headings[chunk_id]}")

    print("\nDense-only candidates:")
    for chunk_id in sorted(dense_only):
        print(f"  {chunk_id} | {headings[chunk_id]}")

    print("\nBM25-only candidates:")
    for chunk_id in sorted(bm25_only):
        print(f"  {chunk_id} | {headings[chunk_id]}")


if __name__ == "__main__":
    main()
