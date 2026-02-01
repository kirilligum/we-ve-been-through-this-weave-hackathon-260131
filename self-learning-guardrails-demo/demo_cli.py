from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from slg_demo.guardrails import apply_guardrails, detect_violations
from slg_demo.memory_backend import InMemoryBackend, MemoryServerBackend
from slg_demo.scripted import run_scripted_demo
from slg_demo.utils import deterministic_id, read_json, utc_now_iso, write_json


DEMO_ROOT = Path(__file__).resolve().parent
DEFAULT_PROMPT = DEMO_ROOT / "prompts" / "prompt_a.json"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Self-Learning Guardrails Demo")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["scripted", "live"],
        help="Run mode (scripted or live).",
    )
    parser.add_argument(
        "--outdir",
        required=True,
        help="Output directory for artifacts.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive loop in live mode.",
    )
    return parser


def get_memory_backend(memory_namespace: str):
    base_url = os.getenv("MEMORY_SERVER_URL", "http://localhost:8000")
    return MemoryServerBackend(base_url=base_url, namespace=memory_namespace)


def _fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def _run_live_interactive(
    *,
    outdir: Path,
    memory_namespace: str,
    memory_backend,
) -> int:
    if not os.getenv("OPENAI_API_KEY"):
        return _fail(
            "OPENAI_API_KEY is required for live interactive mode. "
            "Set it and retry."
        )

    # Basic interactive loop (deterministic placeholder).
    turns = []
    corrections = []

    print("Live mode started. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            break
        if user_input.lower() in {"exit", "quit"}:
            break
        turns.append({"role": "user", "content": user_input})
        response = f"Echo: {user_input}"

        memory_file = outdir / "memory.json"
        if memory_file.exists():
            guardrails = read_json(memory_file)
            response = apply_guardrails(response, _memory_to_guardrails(guardrails))

        turns.append({"role": "assistant", "content": response})
        corrections.extend(detect_violations(response))

    run_payload = {
        "run_id": f"live-{utc_now_iso()}",
        "mode": "live",
        "prompt_id": "live",
        "turns": turns,
        "corrections": corrections,
        "turn_count": len(turns),
        "correction_turn_count": len(corrections),
        "violations": list(corrections),
        "memory_applied": False,
        "memory_namespace": memory_namespace,
    }

    metrics_payload = {
        "run_id": run_payload["run_id"],
        "timestamp_utc": utc_now_iso(),
        "correction_turns_before": len(corrections),
        "correction_turns_after": len(corrections),
        "turn_reduction_pct": 0.0,
        "runtime_sec": 0.0,
    }

    write_json(outdir / "run.json", run_payload)
    write_json(outdir / "metrics.json", metrics_payload)
    return 0


def _memory_to_guardrails(memory_dict: dict):
    from slg_demo.guardrails import GuardrailMemory

    return GuardrailMemory(
        hard_constraints=list(memory_dict.get("hard_constraints", [])),
        architecture_preferences=list(memory_dict.get("architecture_preferences", [])),
        clarifying_triggers=list(memory_dict.get("clarifying_triggers", [])),
        verification_rules=list(memory_dict.get("verification_rules", [])),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.mode == "scripted" and args.interactive:
        return _fail("--interactive is only valid with --mode live")

    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    seed = int(os.getenv("RANDOM_SEED", "42"))
    prompt_data = read_json(DEFAULT_PROMPT)
    run_id = deterministic_id(seed, prompt_data["prompt_id"])
    memory_namespace = f"slg-{run_id}"
    memory_id = f"guardrails-{run_id}"

    memory_backend = get_memory_backend(memory_namespace)
    memory_backend.health_check()

    if args.mode == "scripted":
        run_scripted_demo(
            prompt_path=DEFAULT_PROMPT,
            outdir=outdir,
            run_id=run_id,
            memory_id=memory_id,
            memory_namespace=memory_namespace,
            memory_backend=memory_backend,
        )
        return 0

    if args.mode == "live":
        if not args.interactive:
            return _fail("Live mode requires --interactive")
        return _run_live_interactive(
            outdir=outdir, memory_namespace=memory_namespace, memory_backend=memory_backend
        )

    return _fail("Unsupported mode")


if __name__ == "__main__":
    raise SystemExit(main())
