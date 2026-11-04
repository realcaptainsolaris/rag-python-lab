"""
04_regression_testing.py
Experiment 6.04: Regression Testing

Compare two dense retrieval configurations on the same evaluation set.

The experiment evaluates top-three and top-five retrieval using
identical Teralune smoke questions and gold evidence mappings.
It identifies improvements and regressions at the question level.

Workflow:
    1. Load smoke questions and evidence mappings.
    2. Load Chroma and select questions with indexed gold evidence.
    3. Retrieve five chunks per question and evaluate both cutoffs.
    4. Compare aggregate scores and individual question outcomes.
    5. Display improvements, regressions, and unchanged results.

Expected result:
    Compare Hit Rate@3 and Hit Rate@5, and identify questions
    whose retrieval outcome changes between configurations.

Run:
    uv run python 06_evaluation_and_debugging/04_regression_testing.py
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

BASELINE_K = 3
CANDIDATE_K = 5

load_dotenv(PROJECT_DIR / ".env")
client = OpenAI()


def embed(text: str) -> list[float]:
    """Generate an embedding for a search question."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def hit_at_k(
    retrieved: list[str],
    relevant: set[str],
    k: int,
) -> bool:
    """Check whether the first k results contain relevant evidence."""
    return bool(set(retrieved[:k]) & relevant)


def precision_at_k(
    retrieved: list[str],
    relevant: set[str],
    k: int,
) -> float:
    """Calculate the fraction of retrieved chunks matching gold evidence."""
    return sum(chunk_id in relevant for chunk_id in retrieved[:k]) / k


def main() -> None:
    """Compare retrieval configurations on identical smoke questions."""

    # 1. Load smoke questions and evidence mappings.
    questions = [
        json.loads(line)
        for line in QUESTIONS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))

    # 2. Load Chroma and select questions with indexed gold evidence.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        name=COLLECTION_NAME
    )

    indexed = set(collection.get(include=[])["ids"])
    eligible: list[tuple[str, str, set[str]]] = []

    for question in questions:
        if question["expected_behavior"] != "answer":
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
            continue

        relevant = {
            chunk_id
            for evidence_id in evidence_ids
            for chunk_id in mapping[evidence_id]["chunks"]
        }

        if relevant <= indexed:
            eligible.append((question["id"], question["question"], relevant))

    if not eligible:
        raise ValueError("No eligible questions found.")

    # 3. Retrieve five chunks per question and evaluate both cutoffs.
    outcomes: list[tuple[str, bool, bool, float, float]] = []

    for question_id, question_text, relevant in eligible:
        result = collection.query(
            query_embeddings=[embed(question_text)],
            n_results=CANDIDATE_K,
        )
        retrieved = result["ids"][0]

        outcomes.append(
            (
                question_id,
                hit_at_k(retrieved, relevant, BASELINE_K),
                hit_at_k(retrieved, relevant, CANDIDATE_K),
                precision_at_k(retrieved, relevant, BASELINE_K),
                precision_at_k(retrieved, relevant, CANDIDATE_K),
            )
        )

    # 4. Compare aggregate scores and individual question outcomes.
    count = len(outcomes)

    baseline_hits = sum(row[1] for row in outcomes)
    candidate_hits = sum(row[2] for row in outcomes)

    baseline_precision = sum(row[3] for row in outcomes) / count
    candidate_precision = sum(row[4] for row in outcomes) / count

    improvements = [row[0] for row in outcomes if not row[1] and row[2]]
    regressions = [row[0] for row in outcomes if row[1] and not row[2]]

    precision_regressions = [row[0] for row in outcomes if row[4] < row[3]]

    # 5. Display improvements, regressions, and unchanged results.
    print(f"Evaluated questions:  {count}")
    print(f"Baseline Hit@3:      {baseline_hits / count:.3f}")
    print(f"Candidate Hit@5:     {candidate_hits / count:.3f}")
    print(f"Baseline Precision@3: {baseline_precision:.3f}")
    print(f"Candidate Precision@5: {candidate_precision:.3f}")

    print(f"\nHit improvements:    {len(improvements)}")
    print(f"Hit regressions:     {len(regressions)}")
    print(f"Precision decreases: {len(precision_regressions)}")

    print(f"\nImproved questions:  {improvements}")
    print(f"Regressed questions: {regressions}")
    print(f"Lower precision:     {precision_regressions}")

    print("\nContext budget:")
    print(f"Baseline:  {BASELINE_K} chunks per question")
    print(f"Candidate: {CANDIDATE_K} chunks per question")
    print(f"Increase:  {(CANDIDATE_K / BASELINE_K - 1) * 100:.1f}%")


if __name__ == "__main__":
    main()
