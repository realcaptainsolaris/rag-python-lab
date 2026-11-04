"""
Erzeugt Chunks anhand der Überschriftenstruktur eines Markdown-Dokuments.

Übergeordnete Überschriften werden in den Chunk übernommen, damit
Unterabschnitte ihren Dokumentkontext behalten.
"""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_FILE = (
    PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus" / "public" / "D022.md"
)


def structure_chunks(text):
    chunks = []
    headings = {}

    current_level = None
    current_lines = []

    for line in text.splitlines():
        if line.startswith("#"):
            if current_level is not None and "\n".join(current_lines).strip():
                chunks.append(
                    {
                        "headings": dict(headings),
                        "level": current_level,
                        "text": "\n".join(current_lines).strip(),
                    }
                )

            level = len(line) - len(line.lstrip("#"))
            heading = line[level:].strip()

            headings[level] = heading

            for deeper_level in list(headings):
                if deeper_level > level:
                    del headings[deeper_level]

            current_level = level
            current_lines = []
        else:
            current_lines.append(line)

    if current_level is not None and "\n".join(current_lines).strip():
        chunks.append(
            {
                "headings": dict(headings),
                "level": current_level,
                "text": "\n".join(current_lines).strip(),
            }
        )

    return chunks


text = DOCUMENT_FILE.read_text(encoding="utf-8")
chunks = structure_chunks(text)

print(f"Document: {DOCUMENT_FILE.name}")
print(f"Chunks: {len(chunks)}")

for number, chunk in enumerate(chunks, start=1):
    heading_path = [chunk["headings"][level] for level in sorted(chunk["headings"])]

    print("\n" + "=" * 60)
    print(f"CHUNK {number}")
    print("=" * 60)
    print(" > ".join(heading_path))
    print()
    print(chunk["text"])
