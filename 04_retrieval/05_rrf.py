"""
05_rrf.py
Experiment 4.05: Reciprocal Rank Fusion (RRF)

Combine dense retrieval and BM25 rankings into one hybrid ranking.

Both methods search the same Teralune documents. RRF combines their
rank positions without comparing their different scoring systems.

Expected result:
    The output shows the top three results from each search method
    and a combined top-five ranking with RRF scores. Documents found
    by both methods can move higher in the final ranking.

Run:
    uv run python 04_retrieval/05_rrf.py
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
RRF_K = 60

QUESTION = "How long is an Orbit 3 access token valid?"


def tokenize(text: str) -> list[str]:
    """Split text into words while preserving technical identifiers."""
    return re.findall(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", text.lower())


def dense_search(collection, client: OpenAI, question: str) -> list[str]:
    """Return chunks ranked by semantic similarity."""
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
    """Return chunks ranked by keyword matching."""
    scores = bm25.get_scores(tokenize(question))

    ranked = sorted(
        range(len(chunk_ids)),
        key=lambda i: (-scores[i], chunk_ids[i]),
    )

    return [chunk_ids[i] for i in ranked if scores[i] > 0][:TOP_K]


def reciprocal_rank_fusion(
    rankings: list[list[str]],
    k: int = RRF_K,
) -> list[tuple[str, float]]:
    """Combine rankings using reciprocal rank scores."""
    scores: dict[str, float] = {}

    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (k + rank)

    return sorted(
        scores.items(),
        key=lambda item: (-item[1], item[0]),
    )


def main() -> None:
    load_dotenv(PROJECT_DIR / ".env")

    client = OpenAI()

    # 1. Open the existing Chroma collection.
    collection = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
    ).get_collection(COLLECTION_NAME)

    # 2. Build a BM25 index from the same documents.
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

    # 3. Retrieve two independent rankings.
    dense_results = dense_search(collection, client, QUESTION)
    bm25_results = bm25_search(bm25, chunk_ids, QUESTION)

    # 4. Combine their rank positions using RRF.
    hybrid_results = reciprocal_rank_fusion([dense_results, bm25_results])

    # 5. Display the rankings.
    print(f"Question: {QUESTION}")

    print("\nDense Top 3:")
    for rank, chunk_id in enumerate(dense_results[:3], start=1):
        print(f"  {rank}. {chunk_id} | {headings[chunk_id]}")

    print("\nBM25 Top 3:")
    for rank, chunk_id in enumerate(bm25_results[:3], start=1):
        print(f"  {rank}. {chunk_id} | {headings[chunk_id]}")

    print("\nHybrid RRF Top 5:")
    for rank, (chunk_id, score) in enumerate(hybrid_results[:5], start=1):
        print(f"  {rank}. {chunk_id} | RRF={score:.4f}")
        print(f"     {headings[chunk_id]}")


if __name__ == "__main__":
    main()
