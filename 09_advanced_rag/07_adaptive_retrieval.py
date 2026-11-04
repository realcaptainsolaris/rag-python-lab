"""
07_adaptive_retrieval.py
Experiment 9.07: Adaptive Retrieval

Route questions to no retrieval, single retrieval, or decomposed retrieval.

An LLM selects a retrieval strategy based on the information need.
Python executes the selected strategy against the Teralune collection.

Workflow:
    1. Open the existing Teralune collection.
    2. Classify each question and select a retrieval strategy.
    3. Generate search queries for the selected strategy.
    4. Retrieve evidence only when the strategy requires it.
    5. Display the strategy and retrieved chunk IDs.

Expected result:
    A calculation needs no retrieval, a factual corpus question needs
    one search, and a compound question may need multiple searches.
    Routing decisions are model predictions, not guarantees.

Run:
    uv run python 09_advanced_rag/07_adaptive_retrieval.py
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
TOP_K = 3

QUESTIONS = [
    "What is 12 multiplied by 8?",
    "How long does Orbit 3.0 retry failed webhook deliveries?",
    (
        "How long does Orbit 3.0 retry failed webhook deliveries, "
        "and how long should receivers retain deduplication records?"
    ),
    (
        "How long does Orbit 3.0 retry failed webhook deliveries, "
        "and what changed in the product's access control model?"
    ),
]

ROUTING_FORMAT = {
    "type": "json_schema",
    "name": "adaptive_retrieval_route",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "strategy": {
                "type": "string",
                "enum": [
                    "no_retrieval",
                    "single_retrieval",
                    "decomposed_retrieval",
                ],
            },
            "queries": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["strategy", "queries"],
        "additionalProperties": False,
    },
}

ROUTING_QUERY = (
    "Choose no_retrieval for simple self-contained calculations; "
    "single_retrieval for one factual information need about Teralune; "
    "decomposed_retrieval for multiple independent factual needs. "
    "Return no queries for no_retrieval, one for single_retrieval, "
    "and two or three standalone subquestions for decomposed_retrieval. "
    "Preserve product names and versions. Do not answer the question."
)


def choose_strategy(
    client: OpenAI,
    question: str,
) -> tuple[str, list[str]]:
    """Choose a strategy and generate corresponding search queries."""
    response = client.responses.create(
        model=QUERY_MODEL,
        instructions=ROUTING_QUERY,
        input=question,
        text={"format": ROUTING_FORMAT},
    )
    decision = json.loads(response.output_text)
    return decision["strategy"], decision["queries"]


def retrieve(
    client: OpenAI,
    collection: chromadb.Collection,
    query: str,
) -> list[str]:
    """Return ranked chunk IDs for a semantic search query."""
    embedding = (
        client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query,
        )
        .data[0]
        .embedding
    )

    result = collection.query(
        query_embeddings=[embedding],
        n_results=TOP_K,
    )
    return result["ids"][0]


def main() -> None:
    """Compare adaptive routing decisions across three questions."""
    client = OpenAI()

    # 1. Open the existing Teralune collection.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        name=COLLECTION_NAME
    )

    # 2. Classify each question and select a retrieval strategy.
    decisions = [choose_strategy(client, question) for question in QUESTIONS]

    # 3. Generate search queries for the selected strategy.
    for question, (strategy, queries) in zip(QUESTIONS, decisions, strict=True):
        print(f"\nQuestion: {question}")
        print(f"Strategy: {strategy}")

        if strategy == "no_retrieval":
            queries = []
        elif strategy == "single_retrieval":
            queries = queries[:1]
        else:
            queries = queries[:3]

        # 4. Retrieve evidence only when the strategy requires it.
        rankings = [retrieve(client, collection, query) for query in queries]

        # 5. Display the strategy and retrieved chunk IDs.
        for index, (query, ranking) in enumerate(
            zip(queries, rankings, strict=True),
            start=1,
        ):
            print(f"  Query {index}: {query}")
            print(f"  Hits {index}: {', '.join(ranking)}")

        if not queries:
            print("  Retrieval skipped")


if __name__ == "__main__":
    main()
