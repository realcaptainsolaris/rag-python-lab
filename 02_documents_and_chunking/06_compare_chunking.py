"""
Vergleicht drei Chunking-Strategien mit derselben Retrieval-Frage.

Alle Chunks werden mit demselben Embedding-Modell eingebettet und
anschließend per Cosine Similarity mit der Frage verglichen.
"""

from pathlib import Path

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_FILE = (
    PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus" / "public" / "D022.md"
)

CHUNK_SIZE = 150
CHUNK_OVERLAP = 30

QUESTION = "Darf ich während einer Cursorfolge den Gerätefilter ändern?"

load_dotenv()
client = OpenAI()
encoding = tiktoken.get_encoding("o200k_base")


def fixed_chunks(text):
    tokens = encoding.encode(text)

    return [
        encoding.decode(tokens[start : start + CHUNK_SIZE])
        for start in range(0, len(tokens), CHUNK_SIZE)
    ]


def overlap_chunks(text):
    tokens = encoding.encode(text)
    step_size = CHUNK_SIZE - CHUNK_OVERLAP

    return [
        encoding.decode(tokens[start : start + CHUNK_SIZE])
        for start in range(0, len(tokens), step_size)
    ]


def structure_chunks(text):
    chunks = []
    headings = {}
    current_level = None
    current_lines = []

    for line in text.splitlines():
        if line.startswith("#"):
            content = "\n".join(current_lines).strip()

            if current_level is not None and content:
                heading_path = " > ".join(headings[level] for level in sorted(headings))
                chunks.append(f"{heading_path}\n\n{content}")

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
        heading_path = " > ".join(headings[level] for level in sorted(headings))
        chunks.append(f"{heading_path}\n\n{content}")

    return chunks


def embed(texts):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]


def compare(name, chunks, question_embedding):
    chunk_embeddings = embed(chunks)
    scores = cosine_similarity(
        [question_embedding],
        chunk_embeddings,
    )[0]

    ranking = sorted(
        zip(scores, chunks),
        reverse=True,
        key=lambda item: item[0],
    )

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    for rank, (score, chunk) in enumerate(ranking[:3], start=1):
        preview = chunk.replace("\n", " ")[:180]

        print(f"{rank}. score={score:.4f}")
        print(f"   {preview}")


text = DOCUMENT_FILE.read_text(encoding="utf-8")

question_embedding = embed([QUESTION])[0]

strategies = {
    "FIXED SIZE": fixed_chunks(text),
    "FIXED SIZE + OVERLAP": overlap_chunks(text),
    "STRUCTURE-AWARE": structure_chunks(text),
}

print(f"Question: {QUESTION}")

for name, chunks in strategies.items():
    compare(name, chunks, question_embedding)
