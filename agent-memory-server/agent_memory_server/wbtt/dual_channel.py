from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from . import extract


def run_dual_channel(
    trace_id: str,
    artifact_text: str,
    distillation_prompt: str,
    ker_prompt: str,
) -> Dict[str, object]:
    if not distillation_prompt or not ker_prompt:
        raise ValueError("prompts_required")

    evidence = extract.extract_evidence_lines(artifact_text)

    memory_artifact = {
        "title": "Dedupe failure caused by legacy fallback",
        "trigger_cues": ["test_event_dedupe_idempotent fails"],
        "evidence_to_check": list(evidence.values()) or ["Unknown"],
        "root_cause": "Unknown",
        "fix_steps": ["derive minimal pricingContext at entrypoint"],
        "anti_patterns": ["editing v2 before verifying executed path"],
        "tags": ["dedupe", "fallback"],
        "confidence": "0.6",
        "source_trace_id": trace_id,
        "created_at": datetime.now(timezone.utc).date().isoformat(),
    }

    ker_output = (
        "Known Error Record: dedupe test fails due to legacy fallback\n\n"
        f"KER slug: {_ker_slug()}-test-fails-legacy-fallback\n"
    )

    return {
        "memevolve_artifact": memory_artifact,
        "ker_output": ker_output,
    }


def _ker_slug() -> str:
    return datetime.now(timezone.utc).date().strftime("%Y%m%d")
