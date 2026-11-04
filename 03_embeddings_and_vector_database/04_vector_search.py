"""
Searches the persistent Teralune Chroma collection.

The script embeds only the user question. Document embeddings are loaded
from the persistent Chroma collection and are not recomputed.
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_chunks"

QUESTION = "The reader paused for 20 minutes. What happens to the cursor?"

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


query_embedding: list[float] = embed(QUESTION)

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=TOP_K,
)

print(f"Collection: {COLLECTION_NAME}")
print(f"Stored chunks: {collection.count()}")
print(f"Question: {QUESTION}")
print(f"Top k: {TOP_K}")

print("\nResults:")

for rank, (chunk_id, document, distance, metadata) in enumerate(
    zip(
        results["ids"][0],
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0],
    ),
    start=1,
):
    print()
    print(f"Rank: {rank}")
    print(f"ID: {chunk_id}")
    print(f"Distance: {distance:.4f}")
    print(f"Document: {metadata['document_id']}")
    print(f"Headings: {metadata['headings']}")
    print(f"Source: {metadata['source']}")
    print(f"Text: {document}")
