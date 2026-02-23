# TEST-006
from pathlib import Path

import pytest


@pytest.fixture
def injection_prompt_text():
    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "wbtt"
        / "prompts"
        / "memory_injection_prompt.txt"
    )
    return fixture_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("case_id", [pytest.param("case", id="TEST-006")])
def test_memory_prompt_injection(injection_prompt_text, case_id):
    # TEST-006
    from agent_memory_server.wbtt import memory_prompt

    injection = memory_prompt.format_injection(
        injection_prompt_text,
        evidence_lines=["selected_pipeline=legacy_fallback"],
    )

    assert "selected_pipeline=legacy_fallback" in injection
    assert "Mandatory evidence" in injection
