"""
Indexes Teralune document chunks in a persistent Chroma collection.

The script loads Markdown documents, creates structure-aware chunks,
generates embeddings, and stores the chunks together with their metadata
in Chroma.
"""

from dataclasses import dataclass
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus"
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_chunks"

DOCUMENT_FILES: list[Path] = [
    CORPUS_DIR / "public" / "D002.md",
    CORPUS_DIR / "public" / "D022.md",
]

load_dotenv()

openai_client = OpenAI()
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))


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


def embed(texts: list[str]) -> list[list[float]]:
    """Create embeddings for a list of texts."""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    return [item.embedding for item in response.data]


collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
)

chunks: list[Chunk] = []

for document_file in DOCUMENT_FILES:
    text: str = document_file.read_text(encoding="utf-8")
    chunks.extend(structure_chunks(text, document_file))

texts: list[str] = [embedding_text(chunk) for chunk in chunks]

embeddings: list[list[float]] = embed(texts)

ids: list[str] = [f"{chunk.document_id}-chunk-{chunk.chunk_number}" for chunk in chunks]

metadatas: list[dict[str, str | int]] = [
    {
        "document_id": chunk.document_id,
        "chunk_number": chunk.chunk_number,
        "source": chunk.source,
        "headings": " > ".join(chunk.headings),
    }
    for chunk in chunks
]

collection.upsert(
    ids=ids,
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas,
)

print(f"Collection: {COLLECTION_NAME}")
print(f"Documents processed: {len(DOCUMENT_FILES)}")
print(f"Chunks indexed: {len(chunks)}")
print(f"Chunks stored: {collection.count()}")

print("\nIndexed chunks:")

for chunk_id, chunk in zip(ids, chunks):
    print(f"{chunk_id} | {' > '.join(chunk.headings)}")
