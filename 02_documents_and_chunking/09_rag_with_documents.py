"""
Führt eine vollständige RAG-Abfrage über mehrere Dokumente aus.

Die Dokumente werden strukturorientiert gechunkt, mit Metadaten versehen,
eingebettet und anhand ihrer Ähnlichkeit zur Benutzerfrage durchsucht.
Die relevantesten Chunks bilden anschließend den Kontext für das LLM.
"""

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus"

DOCUMENT_FILES: list[Path] = [
    CORPUS_DIR / "public" / "D002.md",
    CORPUS_DIR / "public" / "D022.md",
]

QUESTION = (
    "The reader paused for 20 minutes. What are the lifetimes of the "
    "cursor and the Orbit 3 token, and is renewing the token enough "
    "to continue?"
)

TOP_K = 3

load_dotenv()
client = OpenAI()


@dataclass
class Chunk:
    """Repräsentiert einen Text-Chunk mit seinen Dokumentmetadaten."""

    document_id: str
    chunk_number: int
    source: str
    headings: list[str]
    text: str


@dataclass
class RetrievalResult:
    """Repräsentiert einen gefundenen Chunk mit seinem Ähnlichkeitswert."""

    chunk: Chunk
    score: float


def structure_chunks(text: str, document_file: Path) -> list[Chunk]:
    """Zerlegt Markdown-Text anhand seiner Überschriftenstruktur in Chunks."""
    chunks: list[Chunk] = []
    headings: dict[int, str] = {}
    current_level: int | None = None
    current_lines: list[str] = []

    def add_chunk() -> None:
        """Fügt den aktuellen Abschnitt als Chunk hinzu."""
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
    """Erzeugt den Text, der für das Embedding eines Chunks verwendet wird."""
    heading_path: str = " > ".join(chunk.headings)
    return f"{heading_path}\n\n{chunk.text}"


def embed(texts: list[str]) -> list[list[float]]:
    """Erzeugt Embeddings für eine Liste von Texten."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    return [item.embedding for item in response.data]


def retrieve(question: str, chunks: list[Chunk], top_k: int) -> list[RetrievalResult]:
    """Ermittelt die semantisch ähnlichsten Chunks für eine Frage."""
    question_embedding: list[float] = embed([question])[0]

    chunk_embeddings: list[list[float]] = embed(
        [embedding_text(chunk) for chunk in chunks]
    )

    scores = cosine_similarity(
        [question_embedding],
        chunk_embeddings,
    )[0]

    results: list[RetrievalResult] = [
        RetrievalResult(chunk=chunk, score=float(score))
        for chunk, score in zip(chunks, scores)
    ]

    return sorted(
        results,
        key=lambda result: result.score,
        reverse=True,
    )[:top_k]


chunks: list[Chunk] = []

for document_file in DOCUMENT_FILES:
    text: str = document_file.read_text(encoding="utf-8")
    chunks.extend(structure_chunks(text, document_file))

results: list[RetrievalResult] = retrieve(
    QUESTION,
    chunks,
    TOP_K,
)

print(f"Question: {QUESTION}")
print(f"Documents: {len(DOCUMENT_FILES)}")
print(f"Chunks: {len(chunks)}")

print("\nRetrieved context:")

for rank, result in enumerate(results, start=1):
    print("\n" + "=" * 70)
    print(f"{rank}. {result.chunk.document_id} | score={result.score:.4f}")
    print(f"Headings: {' > '.join(result.chunk.headings)}")
    print(result.chunk.text)

context: str = "\n\n".join(
    (
        f"Source: {result.chunk.document_id}\n"
        f"Section: {' > '.join(result.chunk.headings)}\n"
        f"{result.chunk.text}"
    )
    for result in results
)

response = client.responses.create(
    model="gpt-4.1-mini",
    instructions=(
        "Answer the user's question using only the provided context. "
        "If the context is insufficient, say so. "
        "Mention the source document IDs that support the answer."
    ),
    input=f"Context:\n{context}\n\nQuestion:\n{QUESTION}",
)

print("\n" + "=" * 70)
print("ANSWER")
print("=" * 70)
print(response.output_text)
