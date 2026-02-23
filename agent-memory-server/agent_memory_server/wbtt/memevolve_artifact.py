from __future__ import annotations

from typing import Any, List


REQUIRED_KEYS = [
    "title",
    "trigger_cues",
    "evidence_to_check",
    "root_cause",
    "fix_steps",
    "anti_patterns",
    "tags",
    "confidence",
    "source_trace_id",
    "created_at",
]

LIST_KEYS = {"trigger_cues", "evidence_to_check", "fix_steps", "anti_patterns", "tags"}


def validate_artifact(artifact: dict[str, Any], prompt_text: str) -> List[str]:
    """Validate MemEvolve-style memory artifact fields."""
    errors: List[str] = []

    if _is_blank(prompt_text):
        errors.append("prompt_text_empty")

    for key in REQUIRED_KEYS:
        if key not in artifact:
            errors.append(f"missing_{key}")
            continue
        value = artifact[key]
        if key in LIST_KEYS:
            if not isinstance(value, list) or not value:
                errors.append(f"invalid_{key}")
        else:
            if value is None or (isinstance(value, str) and _is_blank(value)):
                errors.append(f"invalid_{key}")

    return errors


def _is_blank(value: str) -> bool:
    return not value or not value.strip()
