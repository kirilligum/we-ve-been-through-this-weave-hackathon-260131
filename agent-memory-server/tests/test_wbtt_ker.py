# TEST-003
from pathlib import Path

import pytest


@pytest.fixture
def ker_prompt_text():
    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "wbtt"
        / "prompts"
        / "ker_prompt.txt"
    )
    return fixture_path.read_text(encoding="utf-8")


@pytest.fixture
def ker_path():
    return Path(__file__).parents[1] / "ker" / "20260201-test-fails-legacy-fallback.md"


@pytest.mark.parametrize("case_id", [pytest.param("case", id="TEST-003")])
def test_ker_file_naming_and_sections(ker_prompt_text, ker_path, case_id):
    # TEST-003
    assert ker_path.exists()

    content = ker_path.read_text(encoding="utf-8")
    assert "Known Error Record:" in content
    assert "Problem Record" in content
    assert "Trigger patterns" in content
    assert "Root cause" in content
