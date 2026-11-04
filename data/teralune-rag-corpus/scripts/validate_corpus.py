"""Validate source, emitted files, qrels and ACL; fail closed on broken references."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from typing import Any

from common import ROOT, allowed, fact, load, resolve


def read_jsonl(path: str) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines()
        if line
    ]


class HTMLText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def normalize(text: str) -> str:
    return " ".join(text.split())


def extract(path: Any) -> str:
    if path.suffix == ".pdf":
        from pypdf import PdfReader

        return "\n".join(p.extract_text() for p in PdfReader(path).pages)
    if path.suffix == ".docx":
        from docx import Document

        d = Document(path)
        return "\n".join(
            [p.text for p in d.paragraphs]
            + [c.text for t in d.tables for r in t.rows for c in r.cells]
        )
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".html":
        parser = HTMLText()
        parser.feed(text)
        return " ".join(parser.parts)
    return text


EXPECTED_BEHAVIORS = {"answer", "clarify", "no_answer", "deny"}
META_PATTERNS = [
    r"\bsynthetic\b",
    r"\bfictional\b",
    r"\bfictitious\b",
    r"\bfiktiv\w*\b",
    r"\bsecurity[ _-]+fixture\b",
    r"\bdeliberately\s+(?:incorrect|false)\b",
    r"\bintentionally\s+(?:incorrect|false|untrusted)\b",
    r"\b(?:test|training|evaluation)[ _-]+(?:dataset|corpus|fixture)\b",
    r"\b(?:designed|constructed)\s+to\s+test\b",
    r"\bfor\s+(?:this|the)\s+dataset\b",
    r"für\s+diesen\s+Datensatz",
    r"\b(?:absichtlich|bewusst)\s+(?:falsch|veraltet|widersprüchlich)",
]


def validate_content(text: str) -> None:
    """Known editorial leakage patterns only; not a general semantic detector."""
    for pattern in META_PATTERNS:
        assert not re.search(pattern, text, re.IGNORECASE), (
            f"corpus meta text: {pattern}"
        )


def validate_question(
    q: dict[str, Any],
    facts: dict[str, Any],
    tax: dict[str, Any],
    es: dict[str, dict[str, Any]],
    ms: dict[str, dict[str, Any]],
    us: dict[str, dict[str, Any]],
) -> None:
    """Check behavior independently of byte/plan equality so mutations test semantics."""
    assert "answerable" not in q and "expected_action" not in q, (
        "obsolete behavior schema"
    )
    behavior = q["expected_behavior"]
    assert behavior in EXPECTED_BEHAVIORS, "invalid expected_behavior"
    assert q["category"] in tax["categories"] and q["user_id"] in us
    assert q["language"] in tax["languages"]
    if behavior == "clarify":
        assert q["product_version"] is None or q["product_version"] in facts["versions"]
        assert q.get("clarification_field") in [
            "version",
            "plan",
            "role",
            "credential_type",
            "event_type",
        ]
        if q["clarification_field"] in ["version", "credential_type"]:
            assert q["product_version"] is None, (
                "clarify must not force an unknown target version"
            )
    else:
        assert q["product_version"] in facts["versions"]
    assert set(q["evidence_ids"]) <= set(es), "missing evidence reference"
    assert q["evidence_documents"] == sorted(
        set(es[e]["document_id"] for e in q["evidence_ids"])
    )
    assert set(q["relevance"]) == set(q["evidence_ids"])
    assert all(v in [1, 2] for v in q["relevance"].values())
    for ref in q["fact_refs"]:
        fact(ref, facts)
    supported = {r for e in q["evidence_ids"] for r in es[e]["fact_refs"]}
    assert set(q["fact_refs"]) <= supported, "question facts not bound in evidence"
    for e in q["evidence_ids"]:
        assert allowed(ms[es[e]["document_id"]], us[q["user_id"]]), (
            "positive qrel leaks unauthorized document"
        )
    blocked = q.get("blocked_evidence_ids", [])
    if behavior == "answer":
        assert q["expected_facts"] and q["evidence_ids"], (
            "answer needs positive evidence"
        )
        assert q["category"] not in ["ambiguous", "unanswerable"] and not blocked
    else:
        assert (
            not q["expected_facts"] and not q["evidence_ids"] and not q["fact_refs"]
        ), "non-answer has positive ground truth"
        assert not q["evidence_documents"] and not q["relevance"]
        if behavior == "clarify":
            assert (
                q["category"] == "ambiguous" and q.get("clarification") and not blocked
            )
        elif behavior == "no_answer":
            assert q["category"] == "unanswerable" and not blocked
        elif behavior == "deny":
            assert (
                q["category"] == "access_restricted"
                and blocked
                and q.get("response_constraint")
            )
    for e in blocked:
        assert e in es and not allowed(ms[es[e]["document_id"]], us[q["user_id"]]), (
            "invalid ACL negative"
        )


def validate_splits(questions: list[dict[str, Any]]) -> None:
    """Partition without exact question/context duplication or accidental ACL leakage."""
    split = load("source/evaluation_splits.json")
    smoke = read_jsonl("evaluation/smoke_questions.jsonl")
    test = read_jsonl("evaluation/test_questions.jsonl")
    assert 20 <= len(smoke) <= 30
    assert set(split) == {"smoke", "test"}
    assert len(split["smoke"]) == len(set(split["smoke"]))
    assert len(split["test"]) == len(set(split["test"]))
    assert not set(split["smoke"]) & set(split["test"])
    assert set(split["smoke"]) | set(split["test"]) == {q["id"] for q in questions}
    for name, rows in [("smoke", smoke), ("test", test)]:
        assert rows == [q for q in questions if q["id"] in split[name]]
        assert all(q["split"] == name for q in rows)
    from collections import defaultdict

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for q in questions:
        groups[normalize(q["question"]).casefold()].append(q)
    for group in groups.values():
        if len(group) > 1:
            assert len({q["user_id"] for q in group}) == len(group), (
                "duplicate question/context"
            )
            assert len({q.get("acl_pair") for q in group}) == 1 and group[0].get(
                "acl_pair"
            )
            assert len({q["split"] for q in group}) == 1, (
                "paired ACL question split across sets"
            )
            assert {q["expected_behavior"] for q in group} == {"answer", "deny"}


def check_duplicates(extracted: dict[str, str]) -> dict[str, Any]:
    """Deterministic text duplicate guard using normalized five-word shingles."""
    from itertools import combinations

    bodies = {k: normalize(v).casefold() for k, v in extracted.items()}

    def shingles(text: str) -> set[tuple[str, ...]]:
        words = re.findall(r"\w+", text)
        return {tuple(words[i : i + 5]) for i in range(max(0, len(words) - 4))}

    sets = {k: shingles(v) for k, v in bodies.items()}
    max_similarity = 0.0
    closest: list[str] = []
    for a, b in combinations(bodies, 2):
        assert bodies[a] != bodies[b], "duplicate documents"
        union = sets[a] | sets[b]
        similarity = len(sets[a] & sets[b]) / len(union) if union else 0
        assert similarity < 0.65, f"near duplicate: {a} {b}"
        if similarity > max_similarity:
            max_similarity = similarity
            closest = [a, b]
    return {
        "method": "normalized five-word shingle Jaccard",
        "rejection_threshold": 0.65,
        "max_similarity": round(max_similarity, 4),
        "closest_documents": closest,
    }


def validate() -> dict[str, Any]:
    facts = load("source/facts.yaml")
    tax = load("source/taxonomy.json")
    manifest = load("source/document_manifest.json")
    documents = load("source/documents.json")
    questions = read_jsonl("evaluation/questions.jsonl")
    evidence = read_jsonl("evaluation/evidence.jsonl")
    users = load("evaluation/users.json")

    def unique(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        result = {i["id"]: i for i in items}
        assert len(result) == len(items), "duplicate IDs"
        return result

    ms = unique(manifest)
    ds = unique(documents)
    qs = unique(questions)
    es = unique(evidence)
    us = unique(users)
    assert len(ms) == len(ds) == 48 and 100 <= len(qs) <= 150
    assert set(ms) == set(ds)
    assert set(m["path"] for m in manifest) == {
        str(p.relative_to(ROOT)) for p in (ROOT / "corpus").rglob("*") if p.is_file()
    }
    checksums = load("evaluation/content_checksums.json")
    valid_roles = set(facts["roles"]) | {"support", "engineer", "security_admin"}
    for u in users:
        assert set(u["roles"]) <= valid_roles, "unknown user role"
        assert u["kind"] in ["anonymous", "customer", "staff"]
    extracted = {}
    for m in manifest:
        assert m["version"] in facts["versions"]
        assert m["access"] in tax["access"] and m["language"] in tax["languages"]
        assert set(m["rag_features"]) <= set(tax["features"])
        assert set(m["required_roles"]) <= valid_roles
        assert m["phase"] == "release" and m["synthetic"] is True
        assert m["status"] in ["current", "historical", "unreviewed"]
        if m["access"] == "CUSTOMER":
            assert m["organization"] in ["org-amber", "org-cobalt"]
        if m["access"] in ["INTERNAL", "RESTRICTED"]:
            assert m["team"]
        d = ds[m["id"]]
        path = ROOT / m["path"]
        assert path.is_file()
        for key in [
            "version",
            "access",
            "language",
            "status",
            "authority",
            "security_fixture",
            "intentional_conflicts",
            "fixture_notes",
        ]:
            assert m.get(key) == d.get(key), f"metadata drift: {m['id']} {key}"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == checksums[m["path"]], (
            "checksum drift"
        )
        assert load(m["source_path"]) == d, "editable source drift"
        text = extract(path)
        extracted[m["id"]] = text
        validate_content(text)
        assert "{{" not in text, "unresolved template"
        assert m["evidence_ids"] == [s["id"] for s in d["sections"]]
        for section in d["sections"]:
            e = es[section["id"]]
            assert e["document_id"] == d["id"] and e["text"] == resolve(
                section["text"], facts
            )
            assert e["heading"] == section["heading"]
            assert section.get("level", 2) in [2, 3]
            if "parent_evidence_id" in section:
                parent = section["parent_evidence_id"]
                assert parent in m["evidence_ids"] and parent != section["id"]
                assert e.get("parent_evidence_id") == parent
                assert m["evidence_ids"].index(parent) < m["evidence_ids"].index(
                    section["id"]
                )
            assert e["canonical_values"] == {
                r: fact(r, facts) for r in section["fact_refs"]
            }
            # Every canonical binding must occur as a template or structured table/role value.
            for ref in section["fact_refs"]:
                assert "{{" + ref + "}}" in section["text"] + json.dumps(
                    section.get("table", {})
                ), f"unbound fact {ref}"
            if d["format"] != "csv":
                assert normalize(e["text"]) in normalize(text), (
                    f"passage absent from emitted document: {e['id']}"
                )
            if "table" in section:
                table = section["table"]
                resolved = {
                    "headers": table["headers"],
                    "rows": [
                        [resolve(str(cell), facts) for cell in row]
                        for row in table["rows"]
                    ],
                }
                assert e["table"] == resolved, "table evidence drift"
                if d["format"] != "csv":
                    for row in resolved["rows"]:
                        for cell in row:
                            assert normalize(cell) in normalize(text), (
                                "table cell absent"
                            )
        if d["format"] == "csv":
            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
            expected = es[d["sections"][0]["id"]]["table"]
            assert rows == [expected["headers"], *expected["rows"]], (
                "emitted CSV differs from canonical table"
            )
        if "prompt_injection" in d["rag_features"]:
            assert d.get("security_fixture") and d["authority"] == "untrusted"
        if d["document_type"] == "security_fixture":
            assert (
                d.get("security_fixture") is True and m.get("security_fixture") is True
            )
            assert d.get("fixture_notes") and m.get("fixture_notes")
        if d.get("intentional_conflicts"):
            assert d.get("security_fixture") and d["status"] == "unreviewed"
            for c in d["intentional_conflicts"]:
                assert c["claim"] in text and c["reason"] and fact(c["fact_ref"], facts)
    assert set(es) == {s["id"] for d in documents for s in d["sections"]}
    assert questions == load("source/question_plan.json"), "question plan drift"
    validate_splits(questions)
    duplicate_report = check_duplicates(extracted)
    schema = load("source/evaluation_schema.json")
    assert schema["schema_version"] == "1.1"
    assert set(schema["expected_behavior"]) == EXPECTED_BEHAVIORS
    for q in questions:
        validate_question(q, facts, tax, es, ms, us)
    review = unique(load("evaluation/question_review.json"))
    assert set(review) == set(qs)
    assert all(
        review[q["id"]]["reviewed"]
        and review[q["id"]]["expected_behavior"] == q["expected_behavior"]
        for q in questions
    )
    assert set(tax["categories"]) <= set(q["category"] for q in questions)
    return {
        "documents": len(ds),
        "planned_total": len(ms),
        "evidence_passages": len(es),
        "questions": len(qs),
        "languages": {
            lang: sum(d["language"] == lang for d in documents)
            for lang in tax["languages"]
        },
        "formats": sorted(set(d["format"] for d in documents)),
        "body_words": sum(len(e["text"].split()) for e in evidence),
        "version": (ROOT / "VERSION").read_text().strip(),
        "behaviors": {
            b: sum(q["expected_behavior"] == b for q in questions)
            for b in sorted(EXPECTED_BEHAVIORS)
        },
        "duplicates": duplicate_report,
        "validation": "PASS",
        "scope": "Structural checks, canonical bindings, emitted text and ACL. Not an independent semantic review.",
    }


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Do not run validator with python -O")
    try:
        print(json.dumps(validate(), ensure_ascii=False, indent=2))
    except (AssertionError, KeyError, ValueError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)
