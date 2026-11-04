"""
03_multi_query.py
Experiment 9.03: Multi-Query Retrieval

Compare one semantic search with dynamically generated search perspectives.

An LLM creates complementary queries without predefined topics. Their
retrieval rankings are combined using reciprocal rank fusion (RRF).


Workflow:
    1. Open the existing Teralune collection.
    2. Generate three complementary queries from the user question.
    3. Retrieve baseline and per-query rankings.
    4. Fuse the generated-query rankings using RRF.
    5. Compare candidate coverage and final top-five results.

Expected result:
    The generated queries explore different aspects of the question.
    Multiple searches may expand the candidate pool, but additional
    candidates do not guarantee more relevant final results.

Run:
    uv run python 09_advanced_rag/03_multi_query.py
"""

import json
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "teralune_corpus"
EMBEDDING_MODEL = "text-embedding-3-small"
QUERY_MODEL = "gpt-4.1-mini"
QUESTION = "Why are my Orbit 3.0 webhooks not arriving?"
TOP_K = 5
RRF_K = 60

MULTI_QUERY_PROMPT = (
    "Generate exactly three complementary semantic search queries for "
    "the user's information need. Determine distinct useful search "
    "perspectives dynamically from the question. Each query must target "
    "a different relevant aspect rather than repeat synonyms. "
    "Preserve explicitly stated product names, versions, and constraints. "
    "Treat possible explanations as search directions, not established "
    "facts. Do not answer the question or invent product details. "
    "Return only a JSON array containing exactly three strings."
)


def generate_queries(client: OpenAI, question: str) -> list[str]:
    """Generate three distinct search queries for one information need."""
    response = client.responses.create(
        model=QUERY_MODEL, instructions=MULTI_QUERY_PROMPT, input=question
    )
    queries: object = json.loads(response.output_text)
    if (
        not isinstance(queries, list)
        or len(queries) != 3
        or not all(isinstance(query, str) and query.strip() for query in queries)
    ):
        raise ValueError("Expected exactly three nonempty query strings")
    cleaned = [query.strip() for query in queries]
    if len(set(cleaned)) != 3:
        raise ValueError("Generated queries must be distinct")
    return cleaned


def retrieve(client: OpenAI, collection: chromadb.Collection, query: str) -> list[str]:
    """Retrieve ranked chunk IDs for a single query."""
    embedding = (
        client.embeddings.create(model=EMBEDDING_MODEL, input=query).data[0].embedding
    )
    results = collection.query(query_embeddings=[embedding], n_results=TOP_K)
    return results["ids"][0]


def fuse_rankings(rankings: list[list[str]]) -> list[tuple[str, float]]:
    """Fuse rankings using reciprocal rank fusion."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (RRF_K + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


def main() -> None:
    """Compare baseline retrieval with dynamic multi-query retrieval."""
    client = OpenAI()

    # 1. Open the existing Teralune collection.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        name=COLLECTION_NAME
    )

    # 2. Generate three complementary queries from the user question.
    queries = generate_queries(client, QUESTION)
    print(f"Question: {QUESTION}")
    for index, query in enumerate(queries, start=1):
        print(f"Query {index}: {query}")

    # 3. Retrieve baseline and per-query rankings.
    baseline = retrieve(client, collection, QUESTION)
    rankings = [retrieve(client, collection, query) for query in queries]
    print(f"\nBaseline: {', '.join(baseline)}")
    for index, ranking in enumerate(rankings, start=1):
        print(f"Query {index} hits: {', '.join(ranking)}")

    # 4. Fuse the generated-query rankings using RRF.
    fused = fuse_rankings(rankings)[:TOP_K]

    # 5. Compare candidate coverage and final top-five results.
    candidates = set().union(*(set(ranking) for ranking in rankings))
    baseline_ids = set(baseline)
    fused_ids = {chunk_id for chunk_id, _ in fused}
    print(f"\nUnique multi-query candidates: {len(candidates)}")
    print(f"Candidates absent from baseline: {len(candidates - baseline_ids)}")
    print("Multi-query RRF top five:")
    for rank, (chunk_id, score) in enumerate(fused, start=1):
        print(f"  {rank}. {chunk_id} | RRF={score:.4f}")
    print(f"Shared top-five chunks: {len(fused_ids & baseline_ids)}")
    print(f"New top-five chunks:    {len(fused_ids - baseline_ids)}")


if __name__ == "__main__":
    main()
