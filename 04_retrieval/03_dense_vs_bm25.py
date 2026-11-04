"""
03_dense_vs_bm25.py
Experiment 03: Dense Retrieval vs. BM25

Compare semantic search and keyword search on the same documents.

Dense retrieval uses the existing embeddings stored in Chroma.
BM25 searches the original document text for matching terms.

Both methods receive exactly the same question.

Expected result:
    The output shows two ranked lists of document chunks for each
    question, making the differences between semantic and keyword
    search immediately visible.

Run:
    uv run python 04_retrieval/03_dense_vs_bm25.py
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

QUESTIONS = [
    "How long does a cursor remain valid?",
    "/api/v3",
]


def tokenize(text: str) -> list[str]:
    """Split text into words while preserving technical identifiers."""
    return re.findall(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", text.lower())


def dense_search(collection, client: OpenAI, question: str) -> list[str]:
    """Find similar chunks using their existing vector embeddings."""

    # Only the question needs a new embedding.
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
    """Rank chunks by lexical matches with the question."""

    scores = bm25.get_scores(tokenize(question))

    # Higher BM25 scores indicate stronger lexical matches.
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
    metadatas = stored["metadatas"]

    # BM25 needs tokenized text, not embeddings.
    bm25 = BM25Okapi([tokenize(text) for text in documents])

    # Use headings to make the search results readable.
    headings = {
        chunk_id: metadata["headings"]
        for chunk_id, metadata in zip(chunk_ids, metadatas)
    }

    print(f"Searching {len(chunk_ids)} Teralune chunks")

    # 3. Compare both methods on identical questions.
    for question in QUESTIONS:
        dense_results = dense_search(collection, client, question)
        bm25_results = bm25_search(bm25, chunk_ids, question)

        print(f"\nQuestion: {question}")

        print("\nDense retrieval:")
        for rank, chunk_id in enumerate(dense_results, start=1):
            print(f"  {rank}. {chunk_id} | {headings[chunk_id]}")

        print("\nBM25:")
        for rank, chunk_id in enumerate(bm25_results, start=1):
            print(f"  {rank}. {chunk_id} | {headings[chunk_id]}")


if __name__ == "__main__":
    main()
