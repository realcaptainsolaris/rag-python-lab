"""
07_vector_search_corpus.py
Runs multiple semantic searches against the persistent Teralune corpus.

The document embeddings already exist in Chroma. Only the query embeddings
are created during this script.
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"
TOP_K = 3

QUESTIONS: list[str] = [
    "How long does a cursor remain valid?",
    "What happens when webhook delivery fails?",
    "How long is an Orbit 3 access token valid?",
    "How long does Orbit retain telemetry data?",
]

load_dotenv()

openai_client = OpenAI()
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = chroma_client.get_collection(
    name=COLLECTION_NAME,
)


def embed(texts: list[str]) -> list[list[float]]:
    """Create embeddings for multiple texts."""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    return [item.embedding for item in response.data]


query_embeddings: list[list[float]] = embed(QUESTIONS)

for question, query_embedding in zip(
    QUESTIONS,
    query_embeddings,
):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
    )

    print()
    print("=" * 80)
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
            f"| authority={metadata['authority']} "
            f"| access={metadata['access']} "
            f"| {metadata['headings']}"
        )
