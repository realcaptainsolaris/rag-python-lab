"""
01_dense_baseline.py
Experiment 01: Dense Retrieval Baseline

Explore semantic search using the existing Teralune corpus.

The script creates query embeddings and searches for similar document
chunks in Chroma. Existing document embeddings are reused.

No metadata filtering is applied, so historical documents can appear
in the results.

Expected result:
    The output shows ranked document chunks with similarity distances.
    Some questions retrieve outdated documents, demonstrating that
    semantic similarity does not guarantee correct or current information.

Run:
    uv run python 04_retrieval/01_dense_baseline.py
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"
TOP_K = 5

QUESTIONS: list[tuple[str, str]] = [
    (
        "semantic",
        "How long does a cursor remain valid?",
    ),
    (
        "version",
        "How long is an Orbit 3 access token valid?",
    ),
    (
        "exact",
        "/api/v3",
    ),
    (
        "webhook",
        "How long does Orbit retry failed webhook deliveries?",
    ),
]


def embed(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Create embeddings for multiple search queries."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    return [item.embedding for item in response.data]


def main() -> None:
    """Run the dense retrieval baseline."""
    load_dotenv()

    openai_client = OpenAI()

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME,
    )

    questions: list[str] = [question for _, question in QUESTIONS]

    query_embeddings: list[list[float]] = embed(
        openai_client,
        questions,
    )

    print(f"Collection: {COLLECTION_NAME}")
    print(f"Stored chunks: {collection.count()}")
    print(f"Top k: {TOP_K}")

    for (query_type, question), query_embedding in zip(
        QUESTIONS,
        query_embeddings,
    ):
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K,
        )

        print()
        print("=" * 80)
        print(f"Query type: {query_type}")
        print(f"Question: {question}")

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
                f"| {metadata['headings']}"
            )


if __name__ == "__main__":
    main()
