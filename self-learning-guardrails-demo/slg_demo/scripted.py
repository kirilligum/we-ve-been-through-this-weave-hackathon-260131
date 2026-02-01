from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from slg_demo.guardrails import (
    GuardrailMemory,
    apply_guardrails,
    detect_violations,
    extract_guardrails,
)
from slg_demo.utils import read_json, utc_now_iso, write_json


@dataclass
class ScriptedResult:
    run_id: str
    prompt_id: str
    memory_id: str
    memory_namespace: str
    baseline_corrections: list[str]
    injected_corrections: list[str]


def load_prompt(prompt_path: Path) -> dict:
    return read_json(prompt_path)


def _build_turns(prompt: str, response: str) -> list[dict]:
    return [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
    ]


def run_scripted_demo(
    *,
    prompt_path: Path,
    outdir: Path,
    run_id: str,
    memory_id: str,
    memory_namespace: str,
    memory_backend,
) -> ScriptedResult:
    start = time.time()
    prompt_data = load_prompt(prompt_path)
    prompt_id = prompt_data["prompt_id"]
    prompt_text = prompt_data["prompt"]
    baseline_response = prompt_data["candidate_response"]
    compliant_response = prompt_data.get("compliant_response")

    baseline_corrections = detect_violations(baseline_response)
    guardrails = extract_guardrails(baseline_corrections)
    guardrails_dict = guardrails.to_dict()

    memory_backend.store_guardrails(memory_id, guardrails_dict)

    # Memory-injected response
    if compliant_response:
        injected_response = compliant_response
    else:
        injected_response = apply_guardrails(baseline_response, guardrails)

    injected_corrections = detect_violations(injected_response)

    run_payload = {
        "run_id": run_id,
        "mode": "scripted",
        "prompt_id": prompt_id,
        "turns": _build_turns(prompt_text, baseline_response),
        "corrections": baseline_corrections,
        "turn_count": 2,
        "correction_turn_count": len(baseline_corrections),
        "violations": list(baseline_corrections),
        "memory_applied": False,
        "memory_namespace": memory_namespace,
    }

    injected_run_payload = {
        "run_id": run_id,
        "mode": "scripted",
        "prompt_id": prompt_id,
        "turns": _build_turns(prompt_text, injected_response),
        "corrections": injected_corrections,
        "turn_count": 2,
        "correction_turn_count": len(injected_corrections),
        "violations": list(injected_corrections),
        "memory_applied": True,
        "memory_namespace": memory_namespace,
    }

    before = len(baseline_corrections)
    after = len(injected_corrections)
    if before > 0:
        turn_reduction_pct = 100 * (before - after) / before
    else:
        turn_reduction_pct = 0.0

    metrics_payload = {
        "run_id": run_id,
        "timestamp_utc": utc_now_iso(),
        "correction_turns_before": before,
        "correction_turns_after": after,
        "turn_reduction_pct": turn_reduction_pct,
        "runtime_sec": max(0.0, time.time() - start),
    }

    write_json(outdir / "run.json", run_payload)
    write_json(outdir / "run_injected.json", injected_run_payload)
    write_json(outdir / "memory.json", guardrails_dict)
    write_json(outdir / "metrics.json", metrics_payload)

    return ScriptedResult(
        run_id=run_id,
        prompt_id=prompt_id,
        memory_id=memory_id,
        memory_namespace=memory_namespace,
        baseline_corrections=baseline_corrections,
        injected_corrections=injected_corrections,
    )
