"""
Shows the cost of repeatedly embedding a document collection.

The script loads multiple Markdown documents, creates structure-aware
chunks, and measures how many texts and tokens would need to be processed
when recomputing all embeddings.
"""

from dataclasses import dataclass
from pathlib import Path

import tiktoken

PROJECT_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus"

DOCUMENT_FILES: list[Path] = [
    CORPUS_DIR / "public" / "D002.md",
    CORPUS_DIR / "public" / "D022.md",
]


@dataclass
class Chunk:
    """Represents a text chunk with its document metadata."""

    document_id: str
    chunk_number: int
    source: str
    headings: list[str]
    text: str


def structure_chunks(text: str, document_file: Path) -> list[Chunk]:
    """Split Markdown text into chunks based on its heading structure."""
    chunks: list[Chunk] = []
    headings: dict[int, str] = {}
    current_level: int | None = None
    current_lines: list[str] = []

    def add_chunk() -> None:
        """Add the current section as a chunk."""
        content: str = "\n".join(current_lines).strip()

        if current_level is None or not content:
            return

        heading_path: list[str] = [headings[level] for level in sorted(headings)]

        chunks.append(
            Chunk(
                document_id=document_file.stem,
                chunk_number=len(chunks) + 1,
                source=str(document_file.relative_to(PROJECT_DIR)),
                headings=heading_path,
                text=content,
            )
        )

    for line in text.splitlines():
        if line.startswith("#"):
            add_chunk()

            level: int = len(line) - len(line.lstrip("#"))
            heading: str = line[level:].strip()

            headings[level] = heading

            for deeper_level in list(headings):
                if deeper_level > level:
                    del headings[deeper_level]

            current_level = level
            current_lines = []
        else:
            current_lines.append(line)

    add_chunk()

    return chunks


def embedding_text(chunk: Chunk) -> str:
    """Build the text used to create the embedding for a chunk."""
    heading_path: str = " > ".join(chunk.headings)
    return f"{heading_path}\n\n{chunk.text}"


encoding = tiktoken.get_encoding("o200k_base")

chunks: list[Chunk] = []

for document_file in DOCUMENT_FILES:
    text: str = document_file.read_text(encoding="utf-8")
    chunks.extend(structure_chunks(text, document_file))

embedding_texts: list[str] = [embedding_text(chunk) for chunk in chunks]

token_counts: list[int] = [len(encoding.encode(text)) for text in embedding_texts]

print(f"Documents: {len(DOCUMENT_FILES)}")
print(f"Chunks: {len(chunks)}")
print(f"Tokens to embed: {sum(token_counts)}")

print("\nChunks:")

for chunk, token_count in zip(chunks, token_counts):
    print(
        f"{chunk.document_id}:{chunk.chunk_number} "
        f"| tokens={token_count:>4} "
        f"| {' > '.join(chunk.headings)}"
    )

print("\nIf the program starts again, all these chunks")
print("would be embedded again with our current approach.")
