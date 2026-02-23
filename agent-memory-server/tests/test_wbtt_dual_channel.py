# TEST-004
from pathlib import Path

import pytest


@pytest.fixture
def prompt_texts():
    base = Path(__file__).parent / "fixtures" / "wbtt" / "prompts"
    distill = (base / "memory_distillation_prompt.txt").read_text(encoding="utf-8")
    ker = (base / "ker_prompt.txt").read_text(encoding="utf-8")
    return distill, ker


@pytest.mark.parametrize("case_id", [pytest.param("case", id="TEST-004")])
def test_dual_channel_outputs(prompt_texts, case_id):
    # TEST-004
    from agent_memory_server.wbtt import dual_channel

    distill_prompt, ker_prompt = prompt_texts
    result = dual_channel.run_dual_channel(
        trace_id="weave-wbtt-hist-002",
        artifact_text="selected_pipeline=legacy_fallback\n[WARNING] fallback warning",
        distillation_prompt=distill_prompt,
        ker_prompt=ker_prompt,
    )

    assert "memevolve_artifact" in result
    assert "ker_output" in result
    assert result["memevolve_artifact"]["source_trace_id"] == "weave-wbtt-hist-002"
    assert "Known Error Record" in result["ker_output"]
