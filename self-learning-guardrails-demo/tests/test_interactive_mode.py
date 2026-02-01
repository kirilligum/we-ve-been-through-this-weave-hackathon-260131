from pathlib import Path

import demo_cli
from slg_demo.memory_backend import InMemoryBackend


# TEST-004

def test_interactive_fail_fast(monkeypatch, tmp_path: Path):
    backend = InMemoryBackend()

    def _fake_backend(_namespace: str):
        return backend

    monkeypatch.setattr(demo_cli, "get_memory_backend", _fake_backend)

    # Invalid combination should fail fast
    code = demo_cli.main(
        ["--mode", "scripted", "--interactive", "--outdir", str(tmp_path)]
    )
    assert code != 0

    # Missing key should fail fast in live mode
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    code = demo_cli.main(
        ["--mode", "live", "--interactive", "--outdir", str(tmp_path)]
    )
    assert code != 0
