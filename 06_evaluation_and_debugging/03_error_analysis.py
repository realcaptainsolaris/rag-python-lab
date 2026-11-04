"""
03_error_analysis.py
Experiment 6.03: Error Analysis

Distinguish retrieval failures from generation failures in a RAG pipeline.

Controlled scenarios demonstrate how the same question can produce
different outcomes depending on the retrieved evidence and the answer.
A deterministic diagnostic function classifies each scenario.

Workflow:
    1. Define the expected fact and controlled test scenarios.
    2. Check whether the required evidence is present in the context.
    3. Check whether the generated answer contains the expected fact.
    4. Classify the outcome and display the diagnostic results.

Expected result:
    Identify one successful run, one retrieval failure, one generation
    failure, and one correct answer without supporting evidence.

Run:
    uv run python 06_evaluation_and_debugging/03_error_analysis.py
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    """Represent a controlled RAG diagnostic scenario."""

    name: str
    context: str
    answer: str


def diagnose(
    evidence_present: bool,
    answer_correct: bool,
) -> str:
    """Classify a RAG outcome using evidence and answer correctness."""
    if not evidence_present:
        if answer_correct:
            return "UNSUPPORTED_CORRECT_ANSWER"
        return "RETRIEVAL_FAILURE"

    if not answer_correct:
        return "GENERATION_FAILURE"

    return "SUCCESS"


def main() -> None:
    """Diagnose controlled retrieval and generation outcomes."""

    # 1. Define the expected fact and controlled test scenarios.
    expected_fact = "72 hours"

    scenarios = [
        Scenario(
            name="Successful RAG run",
            context="Orbit 3.0 retries failed webhooks for 72 hours.",
            answer="Orbit 3.0 retries failed webhooks for 72 hours.",
        ),
        Scenario(
            name="Retrieval failure",
            context="Orbit 2.4 retries failed webhooks for 24 hours.",
            answer="Orbit 3.0 retries failed webhooks for 24 hours.",
        ),
        Scenario(
            name="Generation failure",
            context="Orbit 3.0 retries failed webhooks for 72 hours.",
            answer="Orbit 3.0 retries failed webhooks for 48 hours.",
        ),
        Scenario(
            name="Correct answer without evidence",
            context="The supplied documents do not specify webhook retry duration.",
            answer="Orbit 3.0 retries failed webhooks for 72 hours.",
        ),
    ]

    for scenario in scenarios:
        # 2. Check whether the required evidence is present in the context.
        evidence_present = expected_fact in scenario.context

        # 3. Check whether the generated answer contains the expected fact.
        answer_correct = expected_fact in scenario.answer

        # 4. Classify the outcome and display the diagnostic results.
        diagnosis = diagnose(evidence_present, answer_correct)

        print(f"\nScenario: {scenario.name}")
        print(f"Evidence present: {evidence_present}")
        print(f"Answer correct:   {answer_correct}")
        print(f"Diagnosis:        {diagnosis}")


if __name__ == "__main__":
    main()
