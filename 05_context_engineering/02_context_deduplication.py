"""
02_context_deduplication.py
Experiment 5.02: Context Deduplication

Remove exact duplicate chunks before building the LLM context.

Three existing Orbit 3 chunks provide a small, reproducible example.
A simulated copy consumes context tokens without adding new evidence.
Deduplication preserves independently authored sources.


Workflow:
    1. Load three current Orbit 3 chunks from Chroma.
    2. Simulate an exact duplicate of the first chunk.
    3. Remove duplicate content while preserving source order.
    4. Compare context selection within the same token budget.

Expected result:
    The duplicate consumes space without deduplication.
    Removing it makes room for an additional distinct source.
    The Chroma collection remains unchanged.

Run:
    uv run python 05_context_engineering/02_context_deduplication.py
"""

from pathlib import Path

import chromadb
import tiktoken
from dotenv import load_dotenv
from tiktoken import Encoding

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "teralune_corpus"
GENERATION_MODEL = "gpt-4.1-mini"
CHUNK_IDS = ["D002-chunk-1", "D033-chunk-1", "D005-chunk-1"]


def token_count(chunk: tuple[str, str], encoding: Encoding) -> int:
    """Count tokens in a source-labeled context entry."""
    chunk_id, content = chunk
    return len(encoding.encode(f"[Source: {chunk_id}]\n{content}\n\n"))


def select_chunks(
    chunks: list[tuple[str, str]], budget: int, encoding: Encoding
) -> list[str]:
    """Keep complete chunks in order until the token budget is exhausted."""
    selected: list[str] = []
    used = 0
    for chunk in chunks:
        size = token_count(chunk, encoding)
        if used + size <= budget:
            selected.append(chunk[0])
            used += size
    return selected


def main() -> None:
    """Compare budget selection before and after exact deduplication."""
    load_dotenv(PROJECT_DIR / ".env")

    # 1. Load three current Orbit 3 chunks from Chroma.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        COLLECTION_NAME
    )
    records = collection.get(ids=CHUNK_IDS, include=["documents", "metadatas"])
    found = {
        chunk_id: (document, metadata)
        for chunk_id, document, metadata in zip(
            records["ids"], records["documents"] or [], records["metadatas"] or []
        )
    }
    if any(chunk_id not in found for chunk_id in CHUNK_IDS):
        raise RuntimeError("Required chunks are missing. Rebuild the Chroma index.")
    if any(found[chunk_id][1].get("version") != "3.0" for chunk_id in CHUNK_IDS):
        raise RuntimeError("Expected Orbit 3.0 chunks.")
    chunks = [(chunk_id, found[chunk_id][0]) for chunk_id in CHUNK_IDS]

    # 2. Simulate an exact duplicate of the first chunk.
    duplicate = ("D002-copy", chunks[0][1])
    with_duplicate = [chunks[0], duplicate, *chunks[1:]]

    # 3. Remove duplicate content while preserving source order.
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for chunk in with_duplicate:
        normalized = " ".join(chunk[1].split()).casefold()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(chunk)

    # 4. Compare context selection within the same token budget.
    encoding = tiktoken.encoding_for_model(GENERATION_MODEL)
    budget = sum(token_count(chunk, encoding) for chunk in chunks)
    before = select_chunks(with_duplicate, budget, encoding)
    after = select_chunks(unique, budget, encoding)
    print(f"Context budget: {budget} tokens")
    print(f"Without deduplication: {', '.join(before)}")
    print(f"With deduplication:    {', '.join(after)}")
    print(f"Duplicates removed:   {len(with_duplicate) - len(unique)}")


if __name__ == "__main__":
    main()
