"""Shared deterministic source access and explicit authorization policy."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def fact(key: str, facts: dict[str, Any]) -> Any:
    """Resolve dotted paths with longest-key matching for versions and event names."""
    value: Any = facts
    remaining = key
    while remaining:
        if not isinstance(value, dict):
            raise KeyError(key)
        candidates = [
            k for k in value if remaining == k or remaining.startswith(k + ".")
        ]
        if not candidates:
            raise KeyError(key)
        match = max(candidates, key=len)
        value = value[match]
        remaining = remaining[len(match) :].removeprefix(".")
    return value


def display(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(map(str, value))
    if isinstance(value, dict):
        return ", ".join(f"{k}: {display(v)}" for k, v in value.items())
    return str(value)


def resolve(text: str, facts: dict[str, Any]) -> str:
    return re.sub(r"\{\{([^}]+)\}\}", lambda m: display(fact(m[1], facts)), text)


def allowed(document: dict[str, Any], user: dict[str, Any]) -> bool:
    """Deny by default. Roles are not a hierarchy and staff has no tenant bypass."""
    access = document["access"]
    if access == "PUBLIC":
        return True
    if access == "CUSTOMER":
        return (
            user["kind"] == "customer"
            and user["organization"] == document["organization"]
        )
    if access == "INTERNAL":
        return user["kind"] == "staff" and document["team"] in user["teams"]
    if access == "RESTRICTED":
        return (
            user["kind"] == "staff"
            and document["team"] in user["teams"]
            and set(document["required_roles"]).issubset(user["roles"])
        )
    return False
