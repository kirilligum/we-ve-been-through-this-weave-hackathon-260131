# TEST-001
from pathlib import Path

import pytest


@pytest.fixture
def artifact_text():
    fixture_path = Path(__file__).parent / "fixtures" / "wbtt" / "pytest_artifact_sample.txt"
    return fixture_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("case_id", [pytest.param("case", id="TEST-001")])
def test_extractor_finds_pipeline_and_fallback(artifact_text, case_id):
    # TEST-001
    from agent_memory_server.wbtt import extract

    evidence = extract.extract_evidence_lines(artifact_text)
    assert "selected_pipeline" in evidence
    assert "fallback_warning" in evidence
    assert "selected_pipeline=legacy_fallback" in evidence["selected_pipeline"]
    assert "fallback warning" in evidence["fallback_warning"]
