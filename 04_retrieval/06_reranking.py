"""
06_reranking.py
Experiment 4.06: Cross-Encoder Reranking

Improve a hybrid search ranking using a local Cross-Encoder.

Dense retrieval and BM25 find candidates, RRF combines their rankings,
and a Cross-Encoder evaluates each question-document pair.

Expected result:
    The output shows the RRF top-five ranking and the new Cross-Encoder
    ranking, making changes in document positions immediately visible.

Install:
    uv add sentence-transformers

Run:
    uv run python 04_retrieval/06_reranking.py
"""

import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"

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
) -> list[str]:
    """Combine rankings using reciprocal rank scores."""
    scores = {}

    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (RRF_K + rank)

    ranked = sorted(
        scores.items(),
        key=lambda item: (-item[1], item[0]),
    )

    return [chunk_id for chunk_id, _ in ranked]


def main() -> None:
    load_dotenv(PROJECT_DIR / ".env")

    client = OpenAI()

    # 1. Load the existing documents.
    collection = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
    ).get_collection(COLLECTION_NAME)

    stored = collection.get(include=["documents", "metadatas"])

    chunk_ids = stored["ids"]
    documents = stored["documents"]

    texts = dict(zip(chunk_ids, documents))

    headings = {
        chunk_id: metadata["headings"]
        for chunk_id, metadata in zip(
            chunk_ids,
            stored["metadatas"],
        )
    }

    # 2. Retrieve candidates using dense search and BM25.
    bm25 = BM25Okapi([tokenize(text) for text in documents])

    dense_results = dense_search(collection, client, QUESTION)
    bm25_results = bm25_search(bm25, chunk_ids, QUESTION)

    # 3. Combine both rankings using RRF.
    rrf_results = reciprocal_rank_fusion([dense_results, bm25_results])[:TOP_K]

    # 4. Score each question-document pair with a Cross-Encoder.
    reranker = CrossEncoder(RERANKER_MODEL)

    pairs = [(QUESTION, texts[chunk_id]) for chunk_id in rrf_results]

    scores = reranker.predict(pairs, show_progress_bar=False)

    # 5. Sort candidates by their Cross-Encoder scores.
    reranked = sorted(
        zip(rrf_results, scores),
        key=lambda item: (-float(item[1]), item[0]),
    )

    # 6. Display both rankings.
    print(f"Question: {QUESTION}")

    print("\nRRF Top 5:")
    for rank, chunk_id in enumerate(rrf_results, start=1):
        print(f"  {rank}. {chunk_id} | {headings[chunk_id]}")

    print("\nCross-Encoder Top 5:")
    for rank, (chunk_id, score) in enumerate(reranked, start=1):
        previous_rank = rrf_results.index(chunk_id) + 1

        print(
            f"  {rank}. {chunk_id} "
            f"| previous rank={previous_rank} "
            f"| score={float(score):.3f}"
        )
        print(f"     {headings[chunk_id]}")


if __name__ == "__main__":
    main()
