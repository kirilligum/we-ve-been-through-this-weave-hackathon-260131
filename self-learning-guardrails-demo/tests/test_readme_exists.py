from pathlib import Path


# TEST-000

def test_readme_exists():
    repo_root = Path(__file__).resolve().parents[2]
    readme = repo_root / "self-learning-guardrails-demo" / "README.md"
    assert readme.exists(), "README.md missing in demo folder"
    text = readme.read_text(encoding="utf-8")
    assert "Setup" in text, "README missing Setup section"
    assert "Run" in text, "README missing Run section"
