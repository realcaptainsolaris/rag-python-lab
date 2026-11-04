"""
03_context_ordering.py
Experiment 5.03: Context Ordering

Measure where key evidence appears within the assembled LLM context.

Five existing Orbit 3 chunks form two contexts with identical content.
Moving the answer-bearing chunk from the middle to the beginning changes
its token position without changing the available evidence.


Workflow:
    1. Load five current Orbit 3 chunks from Chroma.
    2. Place the answer-bearing chunk in the middle of the context.
    3. Move the same chunk to the beginning of the context.
    4. Compare its token position in both arrangements.

Expected result:
    Both contexts contain the same five chunks and the same evidence.
    The answer-bearing chunk appears earlier after reordering.
    Token positions alone do not establish model answer quality.

Run:
    uv run python 05_context_engineering/03_context_ordering.py
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
CHUNK_IDS = [
    "D033-chunk-2",
    "D005-chunk-1",
    "D002-chunk-1",
    "D033-chunk-1",
    "D001-chunk-3",
]
EVIDENCE_ID = "D002-chunk-1"


def format_chunk(chunk: tuple[str, str]) -> str:
    """Format a source-labeled chunk for the model context."""
    chunk_id, content = chunk
    return f"[Source: {chunk_id}]\n{content}\n\n"


def evidence_position(
    chunks: list[tuple[str, str]], encoding: Encoding
) -> tuple[int, int]:
    """Return the evidence start offset and total context length in tokens."""
    context = "".join(format_chunk(chunk) for chunk in chunks)
    prefix = ""
    for chunk in chunks:
        if chunk[0] == EVIDENCE_ID:
            break
        prefix += format_chunk(chunk)
    else:
        raise ValueError("Evidence chunk is missing from the context.")
    return len(encoding.encode(prefix)), len(encoding.encode(context))


def main() -> None:
    """Compare evidence placement in two contexts with identical chunks."""
    load_dotenv(PROJECT_DIR / ".env")

    # 1. Load five current Orbit 3 chunks from Chroma.
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

    # 2. Place the answer-bearing chunk in the middle of the context.
    middle_order = chunks

    # 3. Move the same chunk to the beginning of the context.
    first_order = [chunks[2], *chunks[:2], *chunks[3:]]

    # 4. Compare its token position in both arrangements.
    encoding = tiktoken.encoding_for_model(GENERATION_MODEL)
    for label, ordered in [("Middle", middle_order), ("First", first_order)]:
        offset, total = evidence_position(ordered, encoding)
        print(
            f"{label:6} | evidence starts at token {offset:4} / {total} "
            f"({offset / total:.0%} of context)"
        )
    print(f"Same sources: {set(middle_order) == set(first_order)}")
    print("Note: Token position is not a measure of answer accuracy.")


if __name__ == "__main__":
    main()
