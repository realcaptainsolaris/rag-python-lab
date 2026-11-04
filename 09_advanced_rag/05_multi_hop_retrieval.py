"""
05_multi_hop_retrieval.py
Experiment 9.05: Multi-Hop Retrieval

Resolve a conflict between an imported note and an authoritative contract.

The first retrieval finds an imported receiver note. Its product identity
determines the second retrieval, which finds the corresponding contract.

Workflow:
    1. Open the existing Teralune collection.
    2. Retrieve the imported receiver note.
    3. Extract the product, version, and claimed retry duration.
    4. Retrieve the corresponding authoritative delivery contract.
    5. Extract the contract duration and compare both claims.

Expected result:
    The imported note claims a 24-hour retry window for Orbit 3.0.
    The authoritative contract specifies 72 hours instead.
    The second retrieval depends on information extracted in the first.

Run:
    uv run python 09_advanced_rag/05_multi_hop_retrieval.py
"""

import json
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "teralune_corpus"
EMBEDDING_MODEL = "text-embedding-3-small"
QUERY_MODEL = "gpt-4.1-mini"
TOP_K = 5

QUESTION = (
    "According to an imported receiver note, how long are Orbit 3.0 "
    "webhook deliveries retried, and what does the authoritative "
    "delivery contract specify instead?"
)

EXTRACTION_FORMAT = {
    "type": "json_schema",
    "name": "webhook_retry_fact",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "product": {"type": "string"},
            "version": {"type": "string"},
            "retry_hours": {"type": ["integer", "null"]},
        },
        "required": ["product", "version", "retry_hours"],
        "additionalProperties": False,
    },
}
EXTRACTION_PROMPT = (
    "Extract the product name, version, and webhook retry duration "
    "in hours from the provided document. Use only explicit facts. "
    "Return null for a missing retry duration."
)


def retrieve(
    client: OpenAI,
    collection: chromadb.Collection,
    query: str,
) -> list[tuple[str, str]]:
    """Retrieve ranked chunk IDs and document texts."""
    embedding = (
        client.embeddings.create(model=EMBEDDING_MODEL, input=query).data[0].embedding
    )
    results = collection.query(
        query_embeddings=[embedding],
        n_results=TOP_K,
        include=["documents"],
    )
    return list(zip(results["ids"][0], results["documents"][0], strict=True))


def extract_fact(client: OpenAI, document: str) -> dict[str, str | int | None]:
    """Extract a product identity and retry duration from a document."""
    response = client.responses.create(
        model=QUERY_MODEL,
        instructions=EXTRACTION_PROMPT,
        input=document,
        text={"format": EXTRACTION_FORMAT},
    )
    return json.loads(response.output_text)


def select_chunk(
    chunks: list[tuple[str, str]], expected_heading: str
) -> tuple[str, str]:
    """Select a retrieved chunk by its document heading."""
    for chunk_id, document in chunks:
        if document.startswith(expected_heading):
            return chunk_id, document
    raise ValueError(f"Document not found: {expected_heading}")


def main() -> None:
    """Compare dependent retrieval results from two source types."""
    client = OpenAI()

    # 1. Open the existing Teralune collection.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        name=COLLECTION_NAME
    )

    # 2. Retrieve the imported receiver note.
    first_query = "imported receiver note webhook retry duration"
    first_hits = retrieve(client, collection, first_query)
    note_id, note_text = select_chunk(first_hits, "Imported Receiver Note")
    print(f"Hop 1 query: {first_query}")
    print(f"Hop 1 source: {note_id}")

    # 3. Extract the product, version, and claimed retry duration.
    note = extract_fact(client, note_text)
    print(f"Claimed retry duration: {note['retry_hours']} hours")
    print(f"Product: {note['product']} {note['version']}")

    # 4. Retrieve the corresponding authoritative delivery contract.
    second_query = (
        f"{note['product']} {note['version']} webhook delivery contract retry duration"
    )
    second_hits = retrieve(client, collection, second_query)
    contract_id, contract_text = select_chunk(second_hits, "Webhook Delivery Contract")
    print(f"\nHop 2 query: {second_query}")
    print(f"Hop 2 source: {contract_id}")

    # 5. Extract the contract duration and compare both claims.
    contract = extract_fact(client, contract_text)
    if (note["product"], note["version"]) != (contract["product"], contract["version"]):
        raise ValueError("Product or version mismatch between sources")
    print(f"Contract retry duration: {contract['retry_hours']} hours")
    print(f"Claims agree: {note['retry_hours'] == contract['retry_hours']}")
    print("Authority: delivery contract takes precedence over imported note")


if __name__ == "__main__":
    main()
