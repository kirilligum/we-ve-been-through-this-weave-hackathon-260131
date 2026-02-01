from pathlib import Path

import demo_cli
from slg_demo.memory_backend import InMemoryBackend
from slg_demo.utils import read_json


# TEST-003

def test_turn_reduction(monkeypatch, tmp_path: Path):
    backend = InMemoryBackend()

    def _fake_backend(_namespace: str):
        return backend

    monkeypatch.setattr(demo_cli, "get_memory_backend", _fake_backend)

    exit_code = demo_cli.main(
        ["--mode", "scripted", "--outdir", str(tmp_path)]
    )
    assert exit_code == 0

    metrics_payload = read_json(tmp_path / "metrics.json")
    before = metrics_payload["correction_turns_before"]
    after = metrics_payload["correction_turns_after"]

    assert before >= 1
    assert after <= before * 0.5
