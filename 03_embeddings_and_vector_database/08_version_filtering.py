"""
08_version_filtering.py
Compares unfiltered vector search with version-aware metadata filtering.

The same query embedding is used for both searches. The filtered search
restricts retrieval to current Orbit 3.0 documents.
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"
QUESTION = "How long is an Orbit 3 access token valid?"
TOP_K = 5


def embed(client: OpenAI, text: str) -> list[float]:
    """Create an embedding for a single text."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )

    return response.data[0].embedding


def print_results(title: str, results: dict) -> None:
    """Print ranked Chroma search results."""
    print(f"\n{title}")

    for rank, (chunk_id, distance, metadata) in enumerate(
        zip(
            results["ids"][0],
            results["distances"][0],
            results["metadatas"][0],
        ),
        start=1,
    ):
        print(
            f"{rank}. {chunk_id} "
            f"| distance={distance:.4f} "
            f"| version={metadata['version']} "
            f"| status={metadata['status']} "
            f"| authority={metadata['authority']} "
            f"| {metadata['headings']}"
        )


def main() -> None:
    """Compare unrestricted and version-aware retrieval."""
    load_dotenv()

    openai_client = OpenAI()

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME,
    )

    query_embedding: list[float] = embed(
        openai_client,
        QUESTION,
    )

    unfiltered_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
    )

    filtered_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        where={
            "$and": [
                {"version": "3.0"},
                {"status": "current"},
            ]
        },
    )

    print(f"Question: {QUESTION}")

    print_results(
        "Unfiltered search:",
        unfiltered_results,
    )

    print_results(
        "Filtered to version 3.0 and status current:",
        filtered_results,
    )


if __name__ == "__main__":
    main()
