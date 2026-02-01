from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


DEFAULT_HARD_CONSTRAINTS = [
    "Single deterministic path only; no fallback modes.",
    "Avoid duplicated logic or redundant steps.",
    "Fail fast on missing configuration or required inputs.",
]

DEFAULT_ARCH_PREFERENCES = [
    "Prefer one clear execution path with explicit modes.",
    "Keep demo artifacts minimal and deterministic.",
]

DEFAULT_TRIGGERS = [
    {
        "trigger_terms": ["ambiguous", "unclear", "unspecified"],
        "question": "What exact constraint or output format should be used?",
    }
]

DEFAULT_VERIFICATION_RULES = [
    "Reject outputs that include fallback or retry paths.",
    "Reject outputs that duplicate steps or sections.",
    "Ensure missing required env vars cause a hard error.",
]


MARKER_VIOLATIONS = [
    ("[FALLBACK]", "Remove fallback paths; single deterministic path only."),
    ("[DUPLICATION]", "Eliminate duplicated steps or sections."),
    ("[NO_FAIL_FAST]", "Add fail-fast checks for missing configuration."),
]


MARKER_CONSTRAINT_KEYWORDS = {
    "[FALLBACK]": "fallback",
    "[DUPLICATION]": "duplicate",
    "[NO_FAIL_FAST]": "fail fast",
}


@dataclass(frozen=True)
class GuardrailMemory:
    hard_constraints: list[str]
    architecture_preferences: list[str]
    clarifying_triggers: list[dict]
    verification_rules: list[str]

    def to_dict(self) -> dict:
        return {
            "hard_constraints": list(self.hard_constraints),
            "architecture_preferences": list(self.architecture_preferences),
            "clarifying_triggers": list(self.clarifying_triggers),
            "verification_rules": list(self.verification_rules),
        }


def _unique_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def detect_violations(text: str) -> list[str]:
    violations: list[str] = []
    for marker, correction in MARKER_VIOLATIONS:
        if marker in text:
            violations.append(correction)
    return violations


def extract_guardrails(corrections: list[str]) -> GuardrailMemory:
    constraints: list[str] = []
    for correction in corrections:
        lower = correction.lower()
        if "fallback" in lower:
            constraints.append("Single deterministic path only; no fallback modes.")
        if "duplicate" in lower or "duplicat" in lower:
            constraints.append("Avoid duplicated logic or redundant steps.")
        if "fail fast" in lower or "missing" in lower:
            constraints.append("Fail fast on missing configuration or required inputs.")

    constraints = _unique_preserve_order(constraints)
    if len(constraints) < 3:
        constraints = _unique_preserve_order(constraints + DEFAULT_HARD_CONSTRAINTS)

    memory = GuardrailMemory(
        hard_constraints=constraints,
        architecture_preferences=list(DEFAULT_ARCH_PREFERENCES),
        clarifying_triggers=list(DEFAULT_TRIGGERS),
        verification_rules=list(DEFAULT_VERIFICATION_RULES),
    )
    return memory


def apply_guardrails(response: str, memory: GuardrailMemory) -> str:
    updated = response
    for marker, keyword in MARKER_CONSTRAINT_KEYWORDS.items():
        if any(keyword in rule.lower() for rule in memory.hard_constraints):
            updated = updated.replace(marker, "")
    # Normalize whitespace for deterministic output
    updated = " ".join(updated.split())
    return updated.strip()


def validate_guardrails_schema(memory_dict: dict) -> None:
    required = [
        "hard_constraints",
        "architecture_preferences",
        "clarifying_triggers",
        "verification_rules",
    ]
    for key in required:
        if key not in memory_dict:
            raise ValueError(f"Missing required key: {key}")
    if len(memory_dict["hard_constraints"]) < 3:
        raise ValueError("hard_constraints must contain at least 3 rules")
    triggers = memory_dict.get("clarifying_triggers", [])
    if not triggers:
        raise ValueError("clarifying_triggers must contain at least 1 entry")
    for trigger in triggers:
        if not trigger.get("trigger_terms"):
            raise ValueError("Each trigger must include non-empty trigger_terms")
