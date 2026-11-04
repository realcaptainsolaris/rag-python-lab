"""
01_retrieval_evaluation.py
Experiment 6.01: Retrieval Evaluation

Evaluate dense retrieval against the Teralune smoke questions.

The experiment maps curated evidence IDs to indexed Chroma chunks
and measures retrieval quality across multiple answerable questions.
Questions without complete gold evidence in the index are excluded.

Workflow:
    1. Load smoke questions and the evidence-to-chunk mapping.
    2. Load the persistent Chroma collection and its chunk IDs.
    3. Select answerable questions with complete indexed gold evidence.
    4. Retrieve the top five chunks for each eligible question.
    5. Calculate and display retrieval metrics and exclusion reasons.

Expected result:
    Report eligible questions, exclusion reasons, Hit Rate@5,
    Precision@5, Recall@5, and MRR@5.

Run:
    uv run python 06_evaluation_and_debugging/01_retrieval_evaluation.py
"""

import json
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "teralune_corpus"

EVALUATION_DIR = PROJECT_DIR / "data" / "teralune-rag-corpus" / "evaluation"
QUESTIONS_PATH = EVALUATION_DIR / "smoke_questions.jsonl"
MAPPING_PATH = PROJECT_DIR / "data" / "evidence_mapping.json"

TOP_K = 5
EMBEDDING_MODEL = "text-embedding-3-small"

load_dotenv(PROJECT_DIR / ".env")
client = OpenAI()


def load_jsonl(path: Path) -> list[dict]:
    """Load JSON objects from a JSON Lines file."""
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def embed(text: str) -> list[float]:
    """Generate an embedding for a search question."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def calculate_metrics(
    retrieved: list[str],
    relevant: set[str],
) -> tuple[float, float, float, float]:
    """Calculate Hit Rate, Precision, Recall, and reciprocal rank."""
    hits = [chunk_id in relevant for chunk_id in retrieved]

    hit_rate = float(any(hits))
    precision = sum(hits) / TOP_K
    recall = sum(hits) / len(relevant)
    reciprocal_rank = next(
        (1.0 / rank for rank, hit in enumerate(hits, start=1) if hit),
        0.0,
    )

    return hit_rate, precision, recall, reciprocal_rank


def main() -> None:
    """Evaluate dense retrieval on eligible smoke questions."""

    # 1. Load smoke questions and the evidence-to-chunk mapping.
    questions = load_jsonl(QUESTIONS_PATH)
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))

    # 2. Load the persistent Chroma collection and its chunk IDs.
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    indexed_chunks = set(collection.get(include=[])["ids"])

    # 3. Select answerable questions with complete indexed gold evidence.
    eligible: list[tuple[str, set[str]]] = []
    excluded_behavior = 0
    excluded_mapping = 0
    excluded_index = 0

    for question in questions:
        if question["expected_behavior"] != "answer":
            excluded_behavior += 1
            continue

        evidence_ids = [
            evidence_id
            for evidence_id, relevance in question["relevance"].items()
            if relevance > 0
        ]

        if not evidence_ids or any(
            mapping.get(evidence_id, {}).get("status") != "exact"
            or not mapping[evidence_id]["chunks"]
            for evidence_id in evidence_ids
        ):
            excluded_mapping += 1
            continue

        relevant_chunks = {
            chunk_id
            for evidence_id in evidence_ids
            for chunk_id in mapping[evidence_id]["chunks"]
        }

        if not relevant_chunks <= indexed_chunks:
            excluded_index += 1
            continue

        eligible.append((question["question"], relevant_chunks))

    if not eligible:
        raise ValueError("No eligible questions found.")

    # 4. Retrieve the top five chunks for each eligible question.
    scores: list[tuple[float, float, float, float]] = []

    for question, relevant_chunks in eligible:
        results = collection.query(
            query_embeddings=[embed(question)],
            n_results=TOP_K,
        )
        scores.append(calculate_metrics(results["ids"][0], relevant_chunks))

    # 5. Calculate and display retrieval metrics and exclusion reasons.
    averages = [
        sum(score[index] for score in scores) / len(scores) for index in range(4)
    ]

    print(f"Smoke questions:      {len(questions)}")
    print(f"Eligible questions:   {len(eligible)}")
    print(f"Excluded (behavior):  {excluded_behavior}")
    print(f"Excluded (mapping):   {excluded_mapping}")
    print(f"Excluded (index):     {excluded_index}")
    print(f"Hit Rate@5:           {averages[0]:.3f}")
    print(f"Precision@5:          {averages[1]:.3f}")
    print(f"Recall@5:             {averages[2]:.3f}")
    print(f"MRR@5:                {averages[3]:.3f}")


if __name__ == "__main__":
    main()
