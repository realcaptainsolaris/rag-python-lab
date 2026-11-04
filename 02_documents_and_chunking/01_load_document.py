"""
Lädt ein echtes Markdown-Dokument aus dem Teralune-Corpus.

Das Beispiel zeigt den ersten Schritt einer RAG-Pipeline:
Aus einer Datei wird zunächst Text, der anschließend weiterverarbeitet
und in geeignete Retrieval-Einheiten zerlegt werden kann.
"""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_FILE = (
    PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus" / "public" / "D022.md"
)

text = DOCUMENT_FILE.read_text(encoding="utf-8")

print(f"Document: {DOCUMENT_FILE.name}")
print(f"Characters: {len(text)}")

print("\nFirst 1000 characters:\n")
print(text[:1000])
