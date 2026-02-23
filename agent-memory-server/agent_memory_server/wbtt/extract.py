from __future__ import annotations

from typing import Dict


def extract_evidence_lines(artifact_text: str) -> Dict[str, str]:
    """Extract key evidence lines from a pytest artifact text."""
    selected_pipeline = _find_first_line_containing(artifact_text, "selected_pipeline=")
    fallback_warning = _find_first_line_containing(artifact_text, "fallback warning")

    evidence = {}
    if selected_pipeline:
        evidence["selected_pipeline"] = selected_pipeline
    if fallback_warning:
        evidence["fallback_warning"] = fallback_warning

    return evidence


def _find_first_line_containing(text: str, needle: str) -> str | None:
    needle_lower = needle.lower()
    for line in text.splitlines():
        if needle_lower in line.lower():
            return line.strip()
    return None
