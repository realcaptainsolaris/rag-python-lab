"""
Experiment 9.02: Context-Aware Query Rewriting

Compare retrieval for an ambiguous question with and without context.

A short conversation context identifies the product and topic. The
rewriter must resolve references without inventing technical facts.


Workflow:
    1. Open the existing Teralune collection.
    2. Rewrite the question without additional context.
    3. Rewrite the question using conversation context.
    4. Retrieve the top five chunks for all three queries.
    5. Compare rankings and overlapping chunk IDs.

Expected result:
    Context can turn an ambiguous question into a specific search
    query. Different rankings alone do not prove better relevance.

Run:
    uv run python 09_advanced_rag/02_context_aware_rewriting.py
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "teralune_corpus"
EMBEDDING_MODEL = "text-embedding-3-small"
REWRITING_MODEL = "gpt-4.1-mini"
TOP_K = 5

QUESTION = "Why are they not arriving?"
CONTEXT = (
    "Current product: Orbit 3.0. "
    "Previous user message: I am troubleshooting webhook deliveries."
)


def rewrite_query(client: OpenAI, question: str, context: str = "") -> str:
    """Resolve references in a question without adding unsupported facts."""
    instructions = (
        "Rewrite the user's question as one standalone semantic search query. "
        "Use context only to resolve references and clarify the topic. "
        "Preserve uncertainty; do not invent causes, solutions, or facts. "
        "Do not answer the question. Return only the query."
    )
    prompt = f"Context: {context or '(none)'}\nQuestion: {question}"
    response = client.responses.create(
        model=REWRITING_MODEL,
        instructions=instructions,
        input=prompt,
    )
    return response.output_text.strip() or question


def retrieve(
    client: OpenAI,
    collection: chromadb.Collection,
    query: str,
) -> list[tuple[str, float]]:
    """Return ranked chunk IDs and distances for a search query."""
    embedding = (
        client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query,
        )
        .data[0]
        .embedding
    )
    results = collection.query(
        query_embeddings=[embedding],
        n_results=TOP_K,
        include=["distances"],
    )
    ids = results["ids"][0]
    distances = results["distances"][0]
    return list(zip(ids, distances, strict=True))


def print_ranking(label: str, hits: list[tuple[str, float]]) -> None:
    """Print a compact ranking of chunk IDs and distances."""
    print(f"\n{label}:")
    for rank, (chunk_id, distance) in enumerate(hits, start=1):
        print(f"  {rank}. {chunk_id} | distance={distance:.3f}")


def main() -> None:
    """Compare baseline, plain rewriting, and context-aware rewriting."""
    client = OpenAI()

    # 1. Open the existing Teralune collection.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        name=COLLECTION_NAME
    )

    # 2. Rewrite the question without additional context.
    plain_query = rewrite_query(client, QUESTION)

    # 3. Rewrite the question using conversation context.
    contextual_query = rewrite_query(client, QUESTION, CONTEXT)
    print(f"Original:   {QUESTION}")
    print(f"Plain:      {plain_query}")
    print(f"Contextual: {contextual_query}")

    # 4. Retrieve the top five chunks for all three queries.
    rankings = {
        "Baseline": retrieve(client, collection, QUESTION),
        "Plain rewrite": retrieve(client, collection, plain_query),
        "Context rewrite": retrieve(client, collection, contextual_query),
    }
    for label, hits in rankings.items():
        print_ranking(label, hits)

    # 5. Compare rankings and overlapping chunk IDs.
    baseline_ids = {chunk_id for chunk_id, _ in rankings["Baseline"]}
    for label in ("Plain rewrite", "Context rewrite"):
        ids = {chunk_id for chunk_id, _ in rankings[label]}
        print(
            f"{label}: shared={len(ids & baseline_ids)}, new={len(ids - baseline_ids)}"
        )


if __name__ == "__main__":
    main()
