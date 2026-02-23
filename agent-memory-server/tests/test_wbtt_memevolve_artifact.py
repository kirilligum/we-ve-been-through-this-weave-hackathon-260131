# TEST-002
from pathlib import Path

import pytest


@pytest.fixture
def prompt_text():
    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "wbtt"
        / "prompts"
        / "memory_distillation_prompt.txt"
    )
    return fixture_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("case_id", [pytest.param("case", id="TEST-002")])
def test_memevolve_artifact_schema_required_fields(prompt_text, case_id):
    # TEST-002
    from agent_memory_server.wbtt import memevolve_artifact

    artifact = {
        "title": "Dedupe failure caused by legacy fallback",
        "trigger_cues": ["test_event_dedupe_idempotent fails"],
        "evidence_to_check": ["selected_pipeline=legacy_fallback"],
        "root_cause": "v2 throws missing pricingContext.currency",
        "fix_steps": ["derive pricingContext at entrypoint"],
        "anti_patterns": ["editing v2 before verifying executed path"],
        "tags": ["dedupe", "fallback"],
        "confidence": "0.78",
        "source_trace_id": "weave-wbtt-hist-002",
        "created_at": "2026-02-01",
    }

    errors = memevolve_artifact.validate_artifact(artifact, prompt_text)
    assert errors == []
