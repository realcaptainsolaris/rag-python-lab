"""
08_graph_rag.py
Experiment 9.08: Graph-Based Retrieval

Use a small knowledge graph to retrieve related Teralune facts.

The graph is manually constructed from known corpus facts.
Each relationship points to a supporting document chunk in Chroma.

Workflow:
    1. Open the existing Teralune collection.
    2. Build a small knowledge graph.
    3. Find relationships connected to Orbit 3.0 webhooks.
    4. Retrieve supporting document chunks from Chroma.
    5. Display relationships and their source evidence.

Expected result:
    Graph traversal connects the webhook retry window, receiver
    deduplication lifetime, and a conflicting imported note.
    The graph provides candidate evidence, not verified truth.

Run:
    uv run python 09_advanced_rag/08_graph_rag.py
"""

from dataclasses import dataclass
from pathlib import Path

import chromadb
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "teralune_corpus"


@dataclass(frozen=True)
class Edge:
    """Represent a relationship with its supporting source chunk."""

    source: str
    relation: str
    target: str
    chunk_id: str


def build_graph() -> list[Edge]:
    """Build a small graph from known Teralune corpus facts."""
    return [
        Edge(
            "Orbit 3.0",
            "defines",
            "Webhook Delivery Contract",
            "D003-chunk-1",
        ),
        Edge(
            "Webhook Delivery Contract",
            "retry_window",
            "72 hours",
            "D003-chunk-1",
        ),
        Edge(
            "Webhook Delivery Contract",
            "deduplication_lifetime",
            "96 hours",
            "D003-chunk-4",
        ),
        Edge(
            "Orbit 3.0",
            "mentioned_in",
            "Imported Receiver Note",
            "D011-chunk-1",
        ),
        Edge(
            "Imported Receiver Note",
            "claims_retry_window",
            "24 hours",
            "D011-chunk-1",
        ),
    ]


def traverse(
    edges: list[Edge],
    start: str,
    max_hops: int,
) -> list[Edge]:
    """Find relationships reachable from a starting entity."""
    visited = {start}
    frontier = {start}
    found: list[Edge] = []

    for _ in range(max_hops):
        next_frontier: set[str] = set()

        for edge in edges:
            if edge.source not in frontier:
                continue

            found.append(edge)

            if edge.target not in visited:
                next_frontier.add(edge.target)
                visited.add(edge.target)

        frontier = next_frontier

        if not frontier:
            break

    return found


def load_evidence(
    collection: chromadb.Collection,
    chunk_ids: list[str],
) -> dict[str, str]:
    """Load source documents by their exact chunk IDs."""
    result = collection.get(
        ids=chunk_ids,
        include=["documents"],
    )

    return dict(
        zip(
            result["ids"],
            result["documents"],
            strict=True,
        )
    )


def main() -> None:
    """Traverse a knowledge graph and inspect source evidence."""

    # 1. Open the existing Teralune collection.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        name=COLLECTION_NAME
    )

    # 2. Build a small knowledge graph.
    graph = build_graph()
    print(f"Graph relationships: {len(graph)}")

    # 3. Find relationships connected to Orbit 3.0 webhooks.
    start = "Orbit 3.0"
    relationships = traverse(graph, start, max_hops=2)

    print(f"\nStarting entity: {start}")
    print(f"Relationships found: {len(relationships)}")

    for edge in relationships:
        print(f"  {edge.source} --[{edge.relation}]--> {edge.target} ({edge.chunk_id})")

    # 4. Retrieve supporting document chunks from Chroma.
    chunk_ids = list(dict.fromkeys(edge.chunk_id for edge in relationships))
    evidence = load_evidence(collection, chunk_ids)

    # 5. Display relationships and their source evidence.
    print("\nSource evidence:")

    for chunk_id in chunk_ids:
        document = evidence.get(chunk_id)

        if document is None:
            print(f"  {chunk_id}: NOT FOUND")
            continue

        excerpt = " ".join(document.split())[:300]
        print(f"\n  {chunk_id}: {excerpt}...")


if __name__ == "__main__":
    main()
