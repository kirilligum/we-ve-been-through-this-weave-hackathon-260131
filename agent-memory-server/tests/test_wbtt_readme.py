# TEST-008
from pathlib import Path

import pytest


@pytest.mark.parametrize("case_id", [pytest.param("case", id="TEST-008")])
def test_readme_no_docker_and_run_steps_present(case_id):
    # TEST-008
    repo_root = None
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            repo_root = parent
    assert repo_root is not None

    readme_path = repo_root / "README.md"
    content = readme_path.read_text(encoding="utf-8").lower()

    assert "docker run" not in content
    assert "docker-compose" not in content
    assert "redis-server" in content or "redis server" in content
