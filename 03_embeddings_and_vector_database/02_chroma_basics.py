"""
Demonstrates the basic workflow of a persistent Chroma vector database.

The script creates a collection, stores a few texts with embeddings and
metadata, and performs a semantic search against the stored vectors.
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "rag_basics"

DOCUMENTS: list[str] = [
    "Orbit retries failed webhook deliveries for 72 hours.",
    "Orbit access tokens are valid for 60 minutes.",
    "Orbit retains telemetry data for 90 days.",
]

QUESTION = "How long is an Orbit access token valid?"

load_dotenv()

openai_client = OpenAI()
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))


def embed(texts: list[str]) -> list[list[float]]:
    """Create embeddings for a list of texts."""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    return [item.embedding for item in response.data]


collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
)

document_embeddings: list[list[float]] = embed(DOCUMENTS)

collection.upsert(
    ids=[
        "webhook-retries",
        "access-token",
        "telemetry-retention",
    ],
    documents=DOCUMENTS,
    embeddings=document_embeddings,
    metadatas=[
        {"topic": "webhooks"},
        {"topic": "authentication"},
        {"topic": "telemetry"},
    ],
)

question_embedding: list[float] = embed([QUESTION])[0]

results = collection.query(
    query_embeddings=[question_embedding],
    n_results=3,
)

print(f"Collection: {COLLECTION_NAME}")
print(f"Stored documents: {collection.count()}")
print(f"Question: {QUESTION}")

print("\nResults:")

for document_id, document, distance, metadata in zip(
    results["ids"][0],
    results["documents"][0],
    results["distances"][0],
    results["metadatas"][0],
):
    print()
    print(f"ID: {document_id}")
    print(f"Distance: {distance:.4f}")
    print(f"Topic: {metadata['topic']}")
    print(f"Text: {document}")
