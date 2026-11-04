"""
05_metadata_filtering.py
Demonstrates metadata filtering during vector search.

The script compares an unrestricted semantic search with a search that
is restricted to chunks from a specific document.
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_chunks"
QUESTION = "How long is it valid?"
TOP_K = 3

load_dotenv()

openai_client = OpenAI()
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = chroma_client.get_collection(
    name=COLLECTION_NAME,
)


def embed(text: str) -> list[float]:
    """Create an embedding for a single text."""
    response = openai_client.embeddings.create(
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
        print(f"{rank}. {chunk_id} | distance={distance:.4f} | {metadata['headings']}")


query_embedding: list[float] = embed(QUESTION)

unfiltered_results = collection.query(
    query_embeddings=[query_embedding],
    n_results=TOP_K,
)

filtered_results = collection.query(
    query_embeddings=[query_embedding],
    n_results=TOP_K,
    where={"document_id": "D022"},
)

print(f"Question: {QUESTION}")

print_results(
    "Unfiltered search:",
    unfiltered_results,
)

print_results(
    "Filtered to D022:",
    filtered_results,
)
