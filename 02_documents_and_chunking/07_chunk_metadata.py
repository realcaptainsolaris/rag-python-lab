"""
Modelliert Chunks als strukturierte Python-Objekte mit Metadaten.

Eine Dataclass beschreibt, welche Informationen zu einem Chunk gehören.
Neben dem eigentlichen Text bleiben Quelle, Position und Überschriftenpfad
für spätere Retrieval-Schritte erhalten.
"""

from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_FILE = (
    PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus" / "public" / "D022.md"
)


@dataclass
class Chunk:
    """Repräsentiert einen Text-Chunk mit seinen Dokumentmetadaten."""

    document_id: str
    chunk_number: int
    source: str
    headings: list[str]
    text: str


def structure_chunks(text: str, document_file: Path) -> list[Chunk]:
    """Zerlegt Markdown-Text anhand seiner Überschriftenstruktur in Chunks.

    Übergeordnete Überschriften bleiben als Kontext erhalten. Jeder Chunk
    enthält zusätzlich Metadaten zur Quelle und seiner Position im Dokument.
    """
    chunks: list[Chunk] = []
    headings: dict[int, str] = {}
    current_level: int | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("#"):
            content = "\n".join(current_lines).strip()

            if current_level is not None and content:
                heading_path = [headings[level] for level in sorted(headings)]

                chunks.append(
                    Chunk(
                        document_id=document_file.stem,
                        chunk_number=len(chunks) + 1,
                        source=str(document_file.relative_to(PROJECT_DIR)),
                        headings=heading_path,
                        text=content,
                    )
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

    content = "\n".join(current_lines).strip()

    if current_level is not None and content:
        heading_path = [headings[level] for level in sorted(headings)]

        chunks.append(
            Chunk(
                document_id=document_file.stem,
                chunk_number=len(chunks) + 1,
                source=str(document_file.relative_to(PROJECT_DIR)),
                headings=heading_path,
                text=content,
            )
        )

    return chunks


text = DOCUMENT_FILE.read_text(encoding="utf-8")
chunks = structure_chunks(text, DOCUMENT_FILE)

for chunk in chunks:
    print("\n" + "=" * 60)
    print(f"Document: {chunk.document_id}")
    print(f"Chunk: {chunk.chunk_number}")
    print(f"Source: {chunk.source}")
    print(f"Headings: {' > '.join(chunk.headings)}")
    print()
    print(chunk.text[:300])
