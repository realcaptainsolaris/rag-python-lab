"""
Zerlegt ein Markdown-Dokument in gleich große Token-Chunks.

Die Dokumentstruktur wird dabei bewusst ignoriert. Das Beispiel dient
als einfache Baseline für spätere Chunking-Strategien.
"""

from pathlib import Path

import tiktoken

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_FILE = (
    PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus" / "public" / "D022.md"
)

CHUNK_SIZE = 150

text = DOCUMENT_FILE.read_text(encoding="utf-8")

encoding = tiktoken.get_encoding("o200k_base")
tokens = encoding.encode(text)

chunks = []

for start in range(0, len(tokens), CHUNK_SIZE):
    chunk_tokens = tokens[start : start + CHUNK_SIZE]
    chunk_text = encoding.decode(chunk_tokens)
    chunks.append(chunk_text)

print(f"Document: {DOCUMENT_FILE.name}")
print(f"Tokens: {len(tokens)}")
print(f"Chunk size: {CHUNK_SIZE}")
print(f"Chunks: {len(chunks)}")

for number, chunk in enumerate(chunks, start=1):
    print("\n" + "=" * 60)
    print(f"CHUNK {number}")
    print("=" * 60)
    print(chunk)
