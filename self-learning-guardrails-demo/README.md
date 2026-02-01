# We've Been Through This

Self-Learning Guardrails Demo: a deterministic example of extracting repeated coding constraints
("guardrails"), persisting them, and reusing them to reduce correction turns on the same prompt.

## What this is

- Scripted run: deterministic prompt + validator-derived corrections, guardrails extracted to memory.
- Memory-injected rerun: applies stored guardrails before validation to reduce correction turns.
- Live mode: optional interactive loop to show guardrail application end-to-end.

## Requirements

- Python 3.10+
- Redis
- Agent Memory Server (in `agent-memory-server/`)

## Setup

1. Start Redis (local or Docker).
2. Start the Agent Memory Server:

```bash
cd agent-memory-server
uv run python -m agent_memory_server.main
```

3. Optional environment variables:

```bash
export MEMORY_SERVER_URL="http://localhost:8000"
# Live mode only (used for fail-fast gating)
export OPENAI_API_KEY="..."
```

## Run

Scripted (deterministic, no external APIs):

```bash
cd self-learning-guardrails-demo
python demo_cli.py --mode scripted --outdir ./artifacts/scripted
```

## Hackathon demo script (without vs with MemEvolve)

Use this exact sequence to show the baseline (no MemEvolve) and the
memory-injected rerun (MemEvolve applied), plus a quick live interaction.

1) Run the scripted demo to generate baseline + injected artifacts:

```bash
cd self-learning-guardrails-demo
python demo_cli.py --mode scripted --outdir ./artifacts/scripted
```

2) Show the difference in corrections (baseline vs injected):

```bash
cat ./artifacts/scripted/metrics.json
cat ./artifacts/scripted/run.json
cat ./artifacts/scripted/run_injected.json
```

3) Optional live check (requires OPENAI_API_KEY, reuses MemEvolve memory.json from step 1):

```bash
cd self-learning-guardrails-demo
python demo_cli.py --mode live --interactive --outdir ./artifacts/scripted
```

When prompted, paste this input line (demonstrates guardrail removal):

```
Plan: add a fallback mode [FALLBACK]. Duplicate the config section [DUPLICATION]. Skip fail-fast [NO_FAIL_FAST].
```

Expected effect: the echoed response should have the markers removed once
MemEvolve guardrails are applied.

Live interactive mode (requires API key and `--interactive`):

```bash
cd self-learning-guardrails-demo
python demo_cli.py --mode live --interactive --outdir ./artifacts/live
```

## Outputs

Each run writes:

- `run.json` (turns, corrections, memory usage)
- `memory.json` (extracted guardrails)
- `metrics.json` (turn reduction, runtime, run_id, timestamp_utc)

## Troubleshooting

- Memory server errors: ensure Redis is running and the server is started.
- Invalid flags: `--interactive` only works with `--mode live`.
- Live mode gating: set `OPENAI_API_KEY` or it will fail fast.

## Tests (optional)

```bash
cd agent-memory-server
uv run pytest ../self-learning-guardrails-demo/tests
```
