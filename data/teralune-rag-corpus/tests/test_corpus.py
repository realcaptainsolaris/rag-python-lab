"""Meaningful negative checks for authorization and broken ground truth."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_corpus as validator
from common import allowed, load


class CorpusTests(unittest.TestCase):
    def test_full_validation(self) -> None:
        self.assertEqual(validator.validate()["validation"], "PASS")

    def test_acl_is_not_a_role_hierarchy(self) -> None:
        docs = {d["id"]: d for d in load("source/document_manifest.json")}
        users = {u["id"]: u for u in load("evaluation/users.json")}
        self.assertTrue(allowed(docs["D008"], users["customer_basic"]))
        self.assertFalse(allowed(docs["D008"], users["customer_cobalt"]))
        self.assertFalse(allowed(docs["D008"], users["teralune_support"]))
        self.assertTrue(allowed(docs["D009"], users["teralune_engineer"]))
        self.assertFalse(allowed(docs["D009"], users["customer_admin"]))
        self.assertFalse(allowed(docs["D010"], users["teralune_engineer"]))
        self.assertTrue(allowed(docs["D010"], users["security_admin"]))
        self.assertFalse(allowed(dict(access="UNKNOWN"), users["security_admin"]))

    def corrupt_question(self, change: object) -> None:
        original = validator.read_jsonl

        def read(path: str) -> list[dict]:
            data = copy.deepcopy(original(path))
            if path == "evaluation/questions.jsonl":
                change(data)
            return data

        with patch.object(validator, "read_jsonl", read):
            with self.assertRaises((AssertionError, KeyError)):
                validator.validate()

    def test_missing_evidence_is_rejected(self) -> None:
        self.corrupt_question(lambda qs: qs[0]["evidence_ids"].append("D999-E01"))

    def test_no_answer_cannot_gain_positive_evidence(self) -> None:
        self.corrupt_question(lambda qs: qs[12]["evidence_ids"].append("D003-E01"))

    def test_canonical_drift_is_rejected(self) -> None:
        original = validator.load

        def load_changed(path: str) -> object:
            value = copy.deepcopy(original(path))
            if path == "source/facts.yaml":
                value["versions"]["3.0"]["webhook_retry_hours"] = 73
            return value

        with patch.object(validator, "load", load_changed):
            with self.assertRaises(AssertionError):
                validator.validate()

    def test_unknown_feature_is_rejected(self) -> None:
        original = validator.load

        def load_changed(path: str) -> object:
            value = copy.deepcopy(original(path))
            if path == "source/document_manifest.json":
                value[0]["rag_features"].append("typo_feature")
            return value

        with patch.object(validator, "load", load_changed):
            with self.assertRaises(AssertionError):
                validator.validate()

    def check_question(self, number: int, **changes: object) -> None:
        q = copy.deepcopy(load("source/question_plan.json")[number - 1])
        q.update(changes)
        validator.validate_question(
            q,
            load("source/facts.yaml"),
            load("source/taxonomy.json"),
            {e["id"]: e for e in validator.read_jsonl("evaluation/evidence.jsonl")},
            {m["id"]: m for m in load("source/document_manifest.json")},
            {u["id"]: u for u in load("evaluation/users.json")},
        )

    def test_only_four_behaviors_are_valid(self) -> None:
        for invalid in ["abstain", "unknown", "", None]:
            with self.subTest(invalid=invalid), self.assertRaises(AssertionError):
                self.check_question(1, expected_behavior=invalid)

    def test_no_answer_positive_evidence_fails_semantic_check(self) -> None:
        with self.assertRaises(AssertionError):
            self.check_question(
                13,
                evidence_ids=["D003-E01"],
                evidence_documents=["D003"],
                relevance={"D003-E01": 2},
            )

    def test_clarify_cannot_become_a_normal_answer(self) -> None:
        with self.assertRaises(AssertionError):
            self.check_question(12, expected_behavior="answer")
        with self.assertRaises(AssertionError):
            self.check_question(12, product_version="3.0")

    def test_clarify_and_no_answer_are_not_interchangeable(self) -> None:
        with self.assertRaises(AssertionError):
            self.check_question(
                12, expected_behavior="no_answer", product_version="3.0"
            )
        with self.assertRaises(AssertionError):
            self.check_question(
                13,
                expected_behavior="clarify",
                product_version=None,
                clarification="Version?",
            )

    def test_deny_requires_inaccessible_evidence(self) -> None:
        with self.assertRaises(AssertionError):
            self.check_question(16, blocked_evidence_ids=[])
        with self.assertRaises(AssertionError):
            self.check_question(16, user_id="teralune_engineer")

    def test_evidence_references_fail_semantic_check(self) -> None:
        with self.assertRaises(AssertionError):
            self.check_question(1, evidence_ids=["D999-E01"])

    def test_fixture_markers_required_in_metadata(self) -> None:
        original = validator.load

        def changed(path: str) -> object:
            value = copy.deepcopy(original(path))
            if path == "source/document_manifest.json":
                value[9]["security_fixture"] = False
            return value

        with (
            patch.object(validator, "load", changed),
            self.assertRaises(AssertionError),
        ):
            validator.validate()

    def test_known_meta_phrases_rejected(self) -> None:
        for text in [
            "SECURITY FIXTURE",
            "deliberately incorrect",
            "SYNTHETIC FICTION",
            "This was designed to test retrieval.",
            "für diesen Datensatz erfunden",
        ]:
            with self.subTest(text=text), self.assertRaises(AssertionError):
                validator.validate_content(text)
        # Operational language must not be overblocked.
        validator.validate_content(
            "This archived contract applies to Orbit 2.4. Test the receiver before cutover."
        )

    def test_meta_check_applies_to_emitted_content(self) -> None:
        original = validator.extract
        with patch.object(
            validator, "extract", lambda p: original(p) + " SECURITY FIXTURE"
        ):
            with self.assertRaises(AssertionError):
                validator.validate()

    def test_all_questions_reviewed_and_expected_distribution(self) -> None:
        from collections import Counter

        qs = load("source/question_plan.json")
        self.assertEqual(
            Counter(q["expected_behavior"] for q in qs),
            {"answer": 99, "clarify": 6, "no_answer": 6, "deny": 9},
        )
        review = load("evaluation/question_review.json")
        self.assertEqual({q["id"] for q in qs}, {q["id"] for q in review})
        self.assertTrue(all(q["reviewed"] for q in review))
        self.assertEqual(
            {q["id"]: q["expected_behavior"] for q in qs},
            {q["id"]: q["expected_behavior"] for q in review},
        )

    def test_complete_manifest(self) -> None:
        manifest = load("source/document_manifest.json")
        documents = load("source/documents.json")
        self.assertEqual(len(manifest), 48)
        self.assertEqual({m["id"] for m in manifest}, {d["id"] for d in documents})
        self.assertTrue(all(m["phase"] == "release" for m in manifest))

    def test_splits_are_disjoint_and_complete(self) -> None:
        questions = validator.read_jsonl("evaluation/questions.jsonl")
        validator.validate_splits(questions)
        self.assertEqual(
            len(validator.read_jsonl("evaluation/smoke_questions.jsonl")), 25
        )
        self.assertEqual(
            len(validator.read_jsonl("evaluation/test_questions.jsonl")), 95
        )

    def test_overlap_between_splits_is_rejected(self) -> None:
        original = validator.load

        def changed(path: str) -> object:
            data = copy.deepcopy(original(path))
            if path == "source/evaluation_splits.json":
                data["test"].append(data["smoke"][0])
            return data

        with (
            patch.object(validator, "load", changed),
            self.assertRaises(AssertionError),
        ):
            validator.validate_splits(
                validator.read_jsonl("evaluation/questions.jsonl")
            )

    def test_duplicate_document_guard(self) -> None:
        with self.assertRaises(AssertionError):
            validator.check_duplicates(
                {
                    "D001": "same text copied here exactly",
                    "D002": "same text copied here exactly",
                }
            )
        with self.assertRaises(AssertionError):
            validator.check_duplicates(
                {
                    "D001": " ".join(str(i) for i in range(100)),
                    "D002": " ".join(str(i) for i in range(99)) + " changed",
                }
            )

    def test_dotted_event_key_resolution(self) -> None:
        from common import fact

        self.assertEqual(
            fact("event_catalog.alert.suppressed.delivery", load("source/facts.yaml")),
            "audit only",
        )
        self.assertEqual(
            fact("versions.1.8.api_prefix", load("source/facts.yaml")), "/api/v1"
        )

    def test_clarify_can_retain_known_generation(self) -> None:
        self.check_question(110)  # plan is missing, not the known 3.0 generation

    def test_release_build_is_byte_reproducible(self) -> None:
        import hashlib
        import shutil
        import subprocess
        import tempfile

        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "corpus-release"
            shutil.copytree(
                root, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
            )

            def snapshot() -> dict[str, str]:
                files = list((target / "corpus").rglob("*")) + list(
                    (target / "source_documents").glob("*.json")
                )
                files += [
                    target / "evaluation" / name
                    for name in [
                        "evidence.jsonl",
                        "questions.jsonl",
                        "smoke_questions.jsonl",
                        "test_questions.jsonl",
                        "content_checksums.json",
                    ]
                ]
                return {
                    str(p.relative_to(target)): hashlib.sha256(
                        p.read_bytes()
                    ).hexdigest()
                    for p in files
                    if p.is_file()
                }

            initial = snapshot()
            subprocess.run(
                [sys.executable, str(target / "scripts/build_corpus.py")],
                check=True,
                capture_output=True,
            )
            first = snapshot()
            subprocess.run(
                [sys.executable, str(target / "scripts/build_corpus.py")],
                check=True,
                capture_output=True,
            )
            self.assertEqual(initial, first)
            self.assertEqual(first, snapshot())


if __name__ == "__main__":
    unittest.main()
