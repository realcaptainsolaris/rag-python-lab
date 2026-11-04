"""
07_filtered_hybrid.py
Experiment 4.07: Filtered Hybrid Search

Restrict hybrid retrieval to current Orbit 3 documents.

Dense retrieval and BM25 search the same documents, and RRF combines
their rankings. A metadata filter limits both methods to documents
with version="3.0" and status="current".


Workflow:
    1. Load document chunks and metadata from Chroma.
    2. Generate an embedding for the search question.
    3. Run hybrid retrieval without metadata filtering.
    4. Repeat with version="3.0" and status="current".
    5. Display the top five results for both configurations.

Expected result:
    The output compares unfiltered and filtered hybrid rankings.
    Historical documents can appear without filtering but are
    excluded when both retrieval methods apply the metadata filter.

Run:
    uv run python 04_retrieval/07_filtered_hybrid.py
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

METADATA_FILTER = {
    "$and": [
        {"version": "3.0"},
        {"status": "current"},
    ]
}


def tokenize(text: str) -> list[str]:
    """Split text into words while preserving technical identifiers."""
    return re.findall(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", text.lower())


def dense_search(
    collection,
    embedding: list[float],
    where: dict | None = None,
) -> list[str]:
    """Search Chroma with an optional metadata filter."""
    results = collection.query(
        query_embeddings=[embedding],
        n_results=TOP_K,
        where=where,
    )

    return results["ids"][0]


def bm25_search(
    chunks: list[dict],
    question: str,
) -> list[str]:
    """Build a BM25 index from the eligible documents."""
    bm25 = BM25Okapi([tokenize(chunk["text"]) for chunk in chunks])
    scores = bm25.get_scores(tokenize(question))

    ranked = sorted(
        range(len(chunks)),
        key=lambda i: (-scores[i], chunks[i]["id"]),
    )

    return [chunks[i]["id"] for i in ranked if scores[i] > 0][:TOP_K]


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

    # 1. Load document chunks and metadata from Chroma.
    collection = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
    ).get_collection(COLLECTION_NAME)

    stored = collection.get(include=["documents", "metadatas"])

    chunks = [
        {
            "id": chunk_id,
            "text": text,
            "metadata": metadata,
        }
        for chunk_id, text, metadata in zip(
            stored["ids"],
            stored["documents"],
            stored["metadatas"],
        )
    ]

    chunk_lookup = {chunk["id"]: chunk for chunk in chunks}

    # 2. Generate an embedding for the search question.
    embedding = (
        client.embeddings.create(
            model="text-embedding-3-small",
            input=QUESTION,
        )
        .data[0]
        .embedding
    )

    print(f"Question: {QUESTION}")

    # 3. Run hybrid retrieval without metadata filtering.
    # 4. Repeat with version="3.0" and status="current".
    for filtered in (False, True):
        if filtered:
            # BM25 must search only eligible documents.
            eligible = [
                chunk
                for chunk in chunks
                if chunk["metadata"]["version"] == "3.0"
                and chunk["metadata"]["status"] == "current"
            ]

            # Chroma applies the same filter during vector search.
            where = METADATA_FILTER
            label = "FILTERED"
        else:
            eligible = chunks
            where = None
            label = "UNFILTERED"

        dense_results = dense_search(collection, embedding, where)
        bm25_results = bm25_search(eligible, QUESTION)

        hybrid_results = reciprocal_rank_fusion([dense_results, bm25_results])

        # 5. Display the top five results for both configurations.
        print(f"\n{label} | Eligible chunks: {len(eligible)}")

        for rank, chunk_id in enumerate(hybrid_results[:5], start=1):
            metadata = chunk_lookup[chunk_id]["metadata"]

            print(
                f"  {rank}. {chunk_id} "
                f"| version={metadata['version']} "
                f"| status={metadata['status']}"
            )
            print(f"     {metadata['headings']}")


if __name__ == "__main__":
    main()
