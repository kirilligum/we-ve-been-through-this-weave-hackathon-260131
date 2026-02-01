from pathlib import Path

import demo_cli
from slg_demo.memory_backend import InMemoryBackend
from slg_demo.utils import read_json


# TEST-002

def test_scripted_replay_outputs(monkeypatch, tmp_path: Path):
    backend = InMemoryBackend()

    def _fake_backend(_namespace: str):
        return backend

    monkeypatch.setattr(demo_cli, "get_memory_backend", _fake_backend)

    exit_code = demo_cli.main(
        ["--mode", "scripted", "--outdir", str(tmp_path)]
    )
    assert exit_code == 0

    run_path = tmp_path / "run.json"
    memory_path = tmp_path / "memory.json"
    metrics_path = tmp_path / "metrics.json"

    assert run_path.exists()
    assert memory_path.exists()
    assert metrics_path.exists()

    run_payload = read_json(run_path)
    metrics_payload = read_json(metrics_path)

    assert "run_id" in run_payload
    assert "prompt_id" in run_payload
    assert "turns" in run_payload
    assert "corrections" in run_payload
    assert "turn_count" in run_payload
    assert "correction_turn_count" in run_payload
    assert "violations" in run_payload
    assert "memory_applied" in run_payload
    assert "memory_namespace" in run_payload

    assert "run_id" in metrics_payload
    assert "timestamp_utc" in metrics_payload
    assert "correction_turns_before" in metrics_payload
    assert "correction_turns_after" in metrics_payload
    assert "turn_reduction_pct" in metrics_payload

    help_text = demo_cli.build_arg_parser().format_help()
    assert "scripted" in help_text
    assert "live" in help_text
    assert "fallback" not in help_text.lower()
    assert "mock" not in help_text.lower()
