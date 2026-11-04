"""
02_bm25_basics.py
Experiment 02: BM25 Basics

Explore keyword-based retrieval using BM25 on the Teralune corpus.

The script loads existing document chunks from Chroma and builds
a BM25 index to rank them by matching search terms.

Unlike dense retrieval, BM25 does not use embeddings.

Expected result:
    The output shows ranked document chunks with BM25 scores.
    Some questions rank less relevant documents first, while
    exact technical identifiers produce only a few positive matches.

Run:
    uv run python 04_retrieval/02_bm25_basics.py
"""

import re
from pathlib import Path

import chromadb
from rank_bm25 import BM25Okapi

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"
TOP_K = 5

QUESTIONS: list[tuple[str, str]] = [
    ("semantic", "How long does a cursor remain valid?"),
    ("version", "How long is an Orbit 3 access token valid?"),
    ("exact", "/api/v3"),
    ("webhook", "How long does Orbit retry failed webhook deliveries?"),
]


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words and technical identifiers."""
    return re.findall(
        r"[a-z0-9]+(?:[._/-][a-z0-9]+)*",
        text.lower(),
    )


def main() -> None:
    """Build an in-memory BM25 index and run lexical searches."""
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME,
    )

    stored = collection.get(
        include=["documents", "metadatas"],
    )

    ids: list[str] = stored["ids"]
    documents: list[str] = stored["documents"]
    metadatas: list[dict] = stored["metadatas"]

    tokenized_corpus: list[list[str]] = [tokenize(document) for document in documents]

    bm25 = BM25Okapi(tokenized_corpus)

    print(f"Collection: {COLLECTION_NAME}")
    print(f"Indexed chunks: {len(documents)}")
    print(f"Top k: {TOP_K}")

    for query_type, question in QUESTIONS:
        query_tokens: list[str] = tokenize(question)

        scores = bm25.get_scores(query_tokens)

        ranked_indices: list[int] = sorted(
            range(len(scores)),
            key=lambda index: (-scores[index], ids[index]),
        )

        print()
        print("=" * 80)
        print(f"Query type: {query_type}")
        print(f"Question: {question}")
        print(f"Query tokens: {query_tokens}")

        for rank, index in enumerate(
            ranked_indices[:TOP_K],
            start=1,
        ):
            metadata = metadatas[index]

            print(
                f"{rank}. {ids[index]} "
                f"| score={scores[index]:.4f} "
                f"| version={metadata['version']} "
                f"| status={metadata['status']} "
                f"| {metadata['headings']}"
            )


if __name__ == "__main__":
    main()
