"""
09_rag_with_chroma.py
Runs a complete RAG pipeline using the persistent Chroma index.

The script creates only a query embedding. Document embeddings and chunks
already exist in Chroma and are reused.

Retrieval is restricted to current Orbit 3.0 documents before the retrieved
chunks are passed to the language model as context.
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"

QUESTION = "How long is an Orbit 3 access token valid?"
TOP_K = 3


def embed(client: OpenAI, text: str) -> list[float]:
    """Create an embedding for a single query."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )

    return response.data[0].embedding


def build_context(results: dict) -> str:
    """Build the LLM context from retrieved Chroma results."""
    context_parts: list[str] = []

    for chunk_id, document, metadata in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
    ):
        context_parts.append(
            "\n".join(
                [
                    f"Chunk: {chunk_id}",
                    f"Document: {metadata['document_id']}",
                    f"Version: {metadata['version']}",
                    f"Section: {metadata['headings']}",
                    "",
                    document,
                ]
            )
        )

    return "\n\n---\n\n".join(context_parts)


def answer_question(
    client: OpenAI,
    question: str,
    context: str,
) -> str:
    """Answer a question using only the retrieved context."""
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "Answer the question using only the provided context. "
            "If the context does not contain enough information, "
            "say that the question cannot be answered from the "
            "provided context. Do not use outside knowledge."
        ),
        input=(f"Question:\n{question}\n\nContext:\n{context}"),
    )

    return response.output_text


def main() -> None:
    """Run retrieval and generation against the persistent index."""
    load_dotenv()

    openai_client = OpenAI()

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME,
    )

    query_embedding: list[float] = embed(
        openai_client,
        QUESTION,
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        where={
            "$and": [
                {"version": "3.0"},
                {"status": "current"},
            ]
        },
    )

    print(f"Question: {QUESTION}")
    print("\nRetrieved chunks:")

    for rank, (chunk_id, distance, metadata) in enumerate(
        zip(
            results["ids"][0],
            results["distances"][0],
            results["metadatas"][0],
        ),
        start=1,
    ):
        print(f"{rank}. {chunk_id} | distance={distance:.4f} | {metadata['headings']}")

    context: str = build_context(results)

    answer: str = answer_question(
        openai_client,
        QUESTION,
        context,
    )

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    main()
