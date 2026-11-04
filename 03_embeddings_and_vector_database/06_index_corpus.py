"""
06_index_corpus.py
Indexes all Markdown documents from the Teralune corpus in Chroma.

Document content is loaded only from the corpus directory. Authoritative
metadata such as version, language, access level, status, and authority
is loaded separately from the document manifest.

Evaluation data, authoring material, and source documents are intentionally
excluded from the indexed document content.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent

TERALUNE_DIR = PROJECT_DIR / "data" / "teralune-rag-corpus"
CORPUS_DIR = TERALUNE_DIR / "corpus"
MANIFEST_FILE = TERALUNE_DIR / "source" / "document_manifest.json"

CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"


@dataclass
class Chunk:
    """Represents a text chunk and its structural metadata."""

    document_id: str
    chunk_number: int
    source: str
    headings: list[str]
    text: str


def load_manifest() -> dict[str, dict[str, Any]]:
    """Load authoritative document metadata indexed by document ID."""
    data: list[dict[str, Any]] = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))

    return {document["id"]: document for document in data}


def structure_chunks(
    text: str,
    document_file: Path,
) -> list[Chunk]:
    """Split a Markdown document into chunks based on heading structure."""
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
    """Build the text representation used to create the embedding."""
    heading_path: str = " > ".join(chunk.headings)
    return f"{heading_path}\n\n{chunk.text}"


def embed(
    client: OpenAI,
    texts: list[str],
) -> list[list[float]]:
    """Create embeddings for multiple texts in one request."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    return [item.embedding for item in response.data]


def main() -> None:
    """Build and persist the Markdown corpus index."""
    load_dotenv()

    openai_client = OpenAI()

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    manifest: dict[str, dict[str, Any]] = load_manifest()

    document_files: list[Path] = sorted(CORPUS_DIR.rglob("*.md"))

    chunks: list[Chunk] = []

    for document_file in document_files:
        document_id: str = document_file.stem

        if document_id not in manifest:
            raise ValueError(f"Document {document_id} is missing from the manifest.")

        text: str = document_file.read_text(encoding="utf-8")

        chunks.extend(
            structure_chunks(
                text,
                document_file,
            )
        )

    print(f"Markdown documents found: {len(document_files)}")
    print(f"Chunks created: {len(chunks)}")

    texts: list[str] = [embedding_text(chunk) for chunk in chunks]

    print("Creating embeddings...")

    embeddings: list[list[float]] = embed(
        openai_client,
        texts,
    )

    ids: list[str] = [
        f"{chunk.document_id}-chunk-{chunk.chunk_number}" for chunk in chunks
    ]

    metadatas: list[dict[str, str | int]] = []

    for chunk in chunks:
        document_metadata: dict[str, Any] = manifest[chunk.document_id]

        metadatas.append(
            {
                "document_id": chunk.document_id,
                "chunk_number": chunk.chunk_number,
                "source": chunk.source,
                "headings": " > ".join(chunk.headings),
                "version": document_metadata["version"],
                "language": document_metadata["language"],
                "access": document_metadata["access"],
                "status": document_metadata["status"],
                "authority": document_metadata["authority"],
                "document_type": document_metadata["document_type"],
            }
        )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
    )

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Collection: {COLLECTION_NAME}")
    print(f"Chunks stored: {collection.count()}")

    access_counts: dict[str, int] = {}

    for chunk in chunks:
        access: str = manifest[chunk.document_id]["access"]

        access_counts[access] = access_counts.get(access, 0) + 1

    print("\nAccess levels:")

    for access, count in sorted(access_counts.items()):
        print(f"{access}: {count} chunks")


if __name__ == "__main__":
    main()
