from __future__ import annotations

from typing import Iterable, List


def format_injection(prompt_text: str, evidence_lines: Iterable[str]) -> str:
    if not prompt_text or not prompt_text.strip():
        raise ValueError("prompt_text_empty")

    normalized = _normalize_lines(evidence_lines)
    evidence_block = "\n".join([f"- {line}" for line in normalized])
    if evidence_block.strip():
        evidence_block = "\nEvidence lines\n" + evidence_block

    return f"{prompt_text}\n{evidence_block}".strip() + "\n"


def _normalize_lines(lines: Iterable[str]) -> List[str]:
    return [line.strip() for line in lines if line and line.strip()]
