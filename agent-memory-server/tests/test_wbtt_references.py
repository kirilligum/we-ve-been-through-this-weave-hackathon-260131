# TEST-009
from pathlib import Path

import pytest


@pytest.mark.parametrize("case_id", [pytest.param("case", id="TEST-009")])
def test_weave_claude_plugin_reference_present(case_id):
    # TEST-009
    repo_root = None
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            repo_root = parent
    assert repo_root is not None
    assert (repo_root / "weave" / "weave" / "integrations" / "claude_plugin").exists()
    assert (repo_root / "claude-weave-readme-fix.txt").exists()
