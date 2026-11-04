"""
01_query_rewriting.py
Experiment 9.01: Query Rewriting

Compare dense retrieval for an original question and an LLM-rewritten query.

The same embedding model and Chroma collection are used for both searches.
The experiment shows changes in retrieved chunks, not proven relevance gains.


Workflow:
    1. Load the existing Teralune collection from Chroma.
    2. Rewrite the original question with a language model.
    3. Retrieve the top five chunks for the original question.
    4. Retrieve the top five chunks for the rewritten query.
    5. Display both rankings and their overlap.

Expected result:
    The output shows the original and rewritten questions, both rankings,
    and the number of shared and unique chunks. Different results do not
    necessarily mean that the rewritten query is better.

Run:
    uv run python 09_advanced_rag/01_query_rewriting.py
"""

from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "teralune_corpus"
EMBEDDING_MODEL = "text-embedding-3-small"
REWRITING_MODEL = "gpt-4.1-mini"
TOP_K = 5
QUESTION = "Why are my webhooks not arriving?"


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    distance: float
    preview: str


def rewrite_query(client: OpenAI, question: str) -> str:
    """Rewrite a question for retrieval without inventing details."""
    response = client.responses.create(
        model=REWRITING_MODEL,
        instructions=(
            "Rewrite the user's question as a concise semantic search query. "
            "Preserve intent and constraints. Do not assume a product or version. "
            "Do not answer the question. Return only the search query."
        ),
        input=question,
    )
    return response.output_text.strip() or question


def retrieve(client: OpenAI, collection: Collection, query: str) -> list[RetrievalHit]:
    """Retrieve the nearest chunks for a query using dense embeddings."""
    embedding = (
        client.embeddings.create(model=EMBEDDING_MODEL, input=query).data[0].embedding
    )
    result = collection.query(
        query_embeddings=[embedding],
        n_results=min(TOP_K, collection.count()),
        include=["documents", "distances"],
    )
    ids = result["ids"][0]
    documents = (result["documents"] or [[]])[0]
    distances = (result["distances"] or [[]])[0]
    return [
        RetrievalHit(chunk_id, distance, " ".join(document.split())[:90])
        for chunk_id, document, distance in zip(ids, documents, distances)
    ]


def print_hits(label: str, hits: list[RetrievalHit]) -> None:
    """Print a compact ranked list of retrieved chunks."""
    print(f"\n{label}:")
    for rank, hit in enumerate(hits, 1):
        print(f"  {rank}. {hit.chunk_id} | distance={hit.distance:.3f}")
        print(f"     {hit.preview}")


def main() -> None:
    """Compare dense retrieval before and after query rewriting."""
    client = OpenAI()

    # 1. Load the existing Teralune collection from Chroma.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        COLLECTION_NAME
    )
    if collection.count() == 0:
        raise RuntimeError("The Teralune collection is empty.")

    # 2. Rewrite the original question with a language model.
    rewritten_query = rewrite_query(client, QUESTION)
    print(f"Original:  {QUESTION}")
    print(f"Rewritten: {rewritten_query}")

    # 3. Retrieve the top five chunks for the original question.
    original_hits = retrieve(client, collection, QUESTION)

    # 4. Retrieve the top five chunks for the rewritten query.
    rewritten_hits = retrieve(client, collection, rewritten_query)

    # 5. Display both rankings and their overlap.
    print_hits("Baseline", original_hits)
    print_hits("Rewritten", rewritten_hits)
    original_ids = {hit.chunk_id for hit in original_hits}
    rewritten_ids = {hit.chunk_id for hit in rewritten_hits}
    print(f"\nShared chunks: {len(original_ids & rewritten_ids)}")
    print(f"New chunks:    {len(rewritten_ids - original_ids)}")


if __name__ == "__main__":
    main()
