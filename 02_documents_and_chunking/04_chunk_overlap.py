"""
Zerlegt ein Markdown-Dokument in überlappende Token-Chunks.

Durch den Overlap wird ein Teil des vorherigen Chunks im nächsten
wiederholt. Dadurch geht an Chunk-Grenzen weniger Kontext verloren.
"""

from pathlib import Path

import tiktoken

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_FILE = (
    PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus" / "public" / "D022.md"
)

CHUNK_SIZE = 150
CHUNK_OVERLAP = 30

text = DOCUMENT_FILE.read_text(encoding="utf-8")

encoding = tiktoken.get_encoding("o200k_base")
tokens = encoding.encode(text)

chunks = []
step_size = CHUNK_SIZE - CHUNK_OVERLAP

for start in range(0, len(tokens), step_size):
    chunk_tokens = tokens[start : start + CHUNK_SIZE]

    if not chunk_tokens:
        break

    chunks.append(encoding.decode(chunk_tokens))

print(f"Document: {DOCUMENT_FILE.name}")
print(f"Tokens: {len(tokens)}")
print(f"Chunk size: {CHUNK_SIZE}")
print(f"Overlap: {CHUNK_OVERLAP}")
print(f"Chunks: {len(chunks)}")

for number, chunk in enumerate(chunks, start=1):
    print("\n" + "=" * 60)
    print(f"CHUNK {number}")
    print("=" * 60)
    print(chunk)
