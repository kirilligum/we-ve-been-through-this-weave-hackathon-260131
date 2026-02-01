Title and Metadata
- Project name: Self-Learning Guardrails Demo
- Version: v0.1
- Owners: Principal Research-Engineering PM (plan owner), Engineering (implementation), Product (demo validation)
- Date: 2026-02-01
- Document ID: SLG-PLAN-2026-02-01
- Summary: Build a fast, deterministic hackathon demo that shows a self-learning agent storing repeated coding constraints as durable memory and using them to reduce correction turns. The demo runs on the local Redis-backed Agent Memory Server, uses a scripted replay first, and then supports a realistic interactive mode for live prompting.

Design Consensus & Trade-offs (Derived from Chat Context)
- Topic: Benchmark choice
  - Verdict: AGAINST long benchmark suites
  - Rationale: Large MemEvolve benchmarks take too long for hackathon timelines; demo must run in minutes.
- Topic: Demo location in repo
  - Verdict: FOR separate folder at repository root
  - Rationale: Hackathon root is /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131; demo should live alongside projects, not inside agent-memory-server.
- Topic: Demo mode ordering
  - Verdict: FOR scripted replay first, live interactive later
  - Rationale: Scripted replay guarantees deterministic, fast demo; live mode is added after behavior is stable.
- Topic: Memory system integration
  - Verdict: FOR Agent Memory Server with Redis
  - Rationale: Existing repo includes agent-memory-server with Redis-backed memory APIs and tooling.
- Topic: Prompt tuning
  - Verdict: FOR iterative prompt adjustment
  - Rationale: After scripted demo, prompt is tuned to achieve desired behavior in realistic runs.

PRD (IEEE 29148 Stakeholder/System Needs)
- Problem: Coding agents repeat the same correction loops (no fallbacks, no duplication, fail-fast), wasting time in hackathon demos.
- Users: Hackathon judges, builders, and maintainers running local demos.
- Value: Demonstrates self-learning agents that persist and reuse guardrails, reducing corrections and improving first-pass quality.
- Business Goals: Show a compelling, fast, reproducible demo; align with “self-learning agents” theme.
- Success Metrics:
  - Scripted demo turn reduction >= 50% from baseline run
  - Demo runtime <= 2 minutes in mock mode
  - All required artifacts generated with deterministic content
- Scope:
  - New demo folder at repo root with README, scripts, and tests
  - Scripted replay with fixed corrections and memory extraction
  - Memory-injected rerun with metrics comparison
  - Optional interactive mode for live runs
- Non-goals:
  - Reproducing MemEvolve benchmark results
  - Implementing full EvolveLab or Flash-Searcher integration
- Dependencies:
  - agent-memory-server (Python, uv, pytest)
  - Redis (for real runs), optional in mock mode
- Risks:
  - LLM nondeterminism in live mode
  - Missing OPENAI_API_KEY for live mode
- Assumptions:
  - Demo is executed from the hackathon repo root
  - agent-memory-server is available locally

SRS (IEEE 29148 Canonical Requirements)
4.1 Functional Requirements
- REQ-001 (func): Create demo folder at /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo with README and runnable scripts.
- REQ-002 (func): Provide a scripted replay that simulates Prompt A + corrections and stores guardrail memory.
- REQ-003 (func): Provide a memory injection rerun that uses stored guardrails to reduce correction turns.
- REQ-004 (func): Emit structured artifacts (run logs, memory artifact, metrics summary) per run.
- REQ-005 (func): Provide a CLI entrypoint for scripted runs and a mock mode that avoids external APIs.
- REQ-006 (func): Provide an optional interactive mode for live prompting when API keys are present.

4.2 Non-functional Requirements
- REQ-007 (nfr): Demo runtime <= 2 minutes in mock mode on a laptop.
- REQ-008 (nfr): Deterministic scripted results with fixed seeds in mock mode.
- REQ-009 (nfr): Fail-fast on missing config or required env vars in live mode.

4.3 Interfaces/APIs
- REQ-010 (int): CLI interface in demo folder with flags: --mode (mock|live), --outdir, --interactive.
- REQ-011 (int): Memory server interface via agent_memory_client (search_memory, eagerly_create_long_term_memory, edit/delete as needed).

4.4 Data Requirements
- REQ-012 (data): Guardrail memory artifact schema includes hard_constraints, preferences, triggers, and verification rules.
- REQ-013 (data): Run log schema includes turn counts, violations, and memory usage indicators.

4.5 Error & Telemetry Expectations
- REQ-014 (nfr): Structured error messages for missing keys, server unreachable, or invalid config.
- REQ-015 (nfr): Emit metrics JSON with timestamps and run IDs for each run.

4.6 Acceptance Criteria
- Scripted demo runs end-to-end without external APIs.
- Memory injection run shows turn count reduction >= 50% compared to baseline scripted run.
- README contains setup, run commands, and expected outputs.

4.7 System Architecture Diagram
```mermaid
flowchart LR
  U[User/Script] --> CLI[demo_cli.py]
  CLI --> MEM[Memory Engine]
  MEM --> AMS[agent-memory-server + Redis]
  CLI --> ART[Artifacts: logs/metrics]
  CLI --> LLM[LLM API (live mode only)]
```
```
C4-style (ASCII)
System: Self-Learning Guardrails Demo
  Container: demo_cli.py (Python CLI)
  Container: memory_engine (policy extraction + retrieval)
  Container: agent-memory-server (Redis-backed memory APIs)
  Container: llm_api (optional external model for live mode)
  Data: artifacts/ (run logs, metrics, memory JSON)
```

Iterative Implementation & Test Plan (ISO/IEC/IEEE 12207 + 29119-3)
- Phase Strategy: Split by complexity: scaffolding, memory extraction, scripted replay, memory-injected evaluation, live mode.
- Risk Register:
  - Risk: Live mode nondeterminism
    - Trigger: Metric regression in live run
    - Mitigation: Default to mock mode, keep live optional
  - Risk: Redis/Memory server not running
    - Trigger: Connection errors
    - Mitigation: Mock mode and explicit fail-fast checks
  - Risk: Prompt drift
    - Trigger: Behavior deviates from constraints
    - Mitigation: Configurable prompt files and retriable memory extraction
- Suspension/Resumption Criteria:
  - Suspend if any phase exit gate is Red or if eval thresholds fail twice.
  - Resume after addressing root cause and updating execution log.

### Phase P00: Demo scaffolding and README
- Scope and Objectives (Impacted REQ-001, REQ-010)
- Iterative Execution Steps
  - Step 1 (RED): Create/update TEST-000 in self-learning-guardrails-demo/tests/test_readme_exists.py for REQ-001 -> run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_readme_exists.py -k test_readme_exists` -> expected: FAIL (README missing)
  - Step 2 (GREEN): Create demo folder and README with required sections -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Normalize README structure and paths -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_readme_exists.py -k test_readme_exists` -> expected: PASS and runtime < 10s
- Exit Gate Rules
  - Green: TEST-000 passes
  - Yellow: README exists but missing one non-critical section
  - Red: README missing or test fails
- Phase Metrics
  - Confidence 70%, Long-term robustness 40%, Internal interactions 1, External interactions 0, Complexity 15%, Feature creep 10%, Technical debt 5%, YAGNI score 20%, MoSCoW: Must, Local/Non-local scope: Local, Architectural changes count: 0

### Phase P01: Guardrail memory extraction and schema
- Scope and Objectives (Impacted REQ-002, REQ-012)
- Iterative Execution Steps
  - Step 1 (RED): Create/update TEST-001 in self-learning-guardrails-demo/tests/test_guardrails_memory.py for REQ-002, REQ-012 -> run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_guardrails_memory.py -k test_extract_guardrails` -> expected: FAIL (function missing)
  - Step 2 (GREEN): Implement minimal extraction function and schema -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Consolidate schema constants and add validation helper -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_guardrails_memory.py -k test_extract_guardrails` -> expected: PASS and runtime < 10s
- Exit Gate Rules
  - Green: TEST-001 passes and schema validation succeeds
  - Yellow: TEST-001 passes but schema validation warnings present
  - Red: TEST-001 fails
- Phase Metrics
  - Confidence 65%, Long-term robustness 50%, Internal interactions 2, External interactions 0, Complexity 25%, Feature creep 10%, Technical debt 10%, YAGNI score 25%, MoSCoW: Must, Local/Non-local scope: Local, Architectural changes count: 1

### Phase P02: Scripted replay runner and artifacts
- Scope and Objectives (Impacted REQ-003, REQ-004, REQ-005)
- Iterative Execution Steps
  - Step 1 (RED): Create/update TEST-002 in self-learning-guardrails-demo/tests/test_scripted_replay.py for REQ-003, REQ-004 -> run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_scripted_replay.py -k test_scripted_replay_outputs` -> expected: FAIL (runner missing)
  - Step 2 (GREEN): Implement scripted replay runner in demo_cli.py with mock mode and artifact output -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Separate I/O, memory client, and prompt replay modules -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_scripted_replay.py -k test_scripted_replay_outputs` -> expected: PASS and runtime < 15s
- Exit Gate Rules
  - Green: TEST-002 passes and artifacts created
  - Yellow: TEST-002 passes but artifacts missing one optional file
  - Red: TEST-002 fails
- Phase Metrics
  - Confidence 60%, Long-term robustness 55%, Internal interactions 3, External interactions 0, Complexity 35%, Feature creep 15%, Technical debt 10%, YAGNI score 30%, MoSCoW: Must, Local/Non-local scope: Local, Architectural changes count: 1

### Phase P03: Memory-injected rerun and evaluation
- Scope and Objectives (Impacted REQ-003, REQ-007, REQ-015)
- Iterative Execution Steps
  - Step 1 (RED): Create/update TEST-003 in self-learning-guardrails-demo/tests/test_memory_injection.py for REQ-003, REQ-007 -> run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_memory_injection.py -k test_turn_reduction` -> expected: FAIL (no injection)
  - Step 2 (GREEN): Implement memory-injected rerun that reduces correction turns in mock mode -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Extract evaluation logic and thresholds to config -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_memory_injection.py -k test_turn_reduction` -> expected: PASS and turn reduction >= 50%
- Exit Gate Rules
  - Green: TEST-003 passes with thresholds met
  - Yellow: TEST-003 passes but reduction < 50%
  - Red: TEST-003 fails
- Phase Metrics
  - Confidence 55%, Long-term robustness 60%, Internal interactions 3, External interactions 0, Complexity 40%, Feature creep 20%, Technical debt 15%, YAGNI score 35%, MoSCoW: Must, Local/Non-local scope: Local, Architectural changes count: 1

### Phase P04: Interactive mode and fail-fast validation
- Scope and Objectives (Impacted REQ-006, REQ-009, REQ-014)
- Iterative Execution Steps
  - Step 1 (RED): Create/update TEST-004 in self-learning-guardrails-demo/tests/test_interactive_mode.py for REQ-006, REQ-009 -> run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_interactive_mode.py -k test_interactive_fail_fast` -> expected: FAIL (flag missing)
  - Step 2 (GREEN): Implement --interactive flag with fail-fast env checks and clear error messages -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Consolidate env validation in a shared helper -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_interactive_mode.py -k test_interactive_fail_fast` -> expected: PASS and runtime < 10s
- Exit Gate Rules
  - Green: TEST-004 passes and errors are actionable
  - Yellow: TEST-004 passes but error message missing remediation text
  - Red: TEST-004 fails
- Phase Metrics
  - Confidence 50%, Long-term robustness 65%, Internal interactions 2, External interactions 1, Complexity 30%, Feature creep 20%, Technical debt 15%, YAGNI score 40%, MoSCoW: Should, Local/Non-local scope: Local, Architectural changes count: 1

Evaluations (AI/Agentic Specific)
```yaml
evals:
  - id: eval_guardrails_scripted
    purpose: dev
    metrics:
      turn_reduction_pct: ">=50"
      runtime_sec: "<=120"
    thresholds:
      turn_reduction_pct: 50
      runtime_sec: 120
    seeds: [42]
    runtime_budget: 120
  - id: eval_guardrails_live
    purpose: holdout
    metrics:
      turn_reduction_pct: ">=30"
      runtime_sec: "<=180"
    thresholds:
      turn_reduction_pct: 30
      runtime_sec: 180
    seeds: [42]
    runtime_budget: 180
```

Tests (ISO/IEC/IEEE 29119-3)
7.1 Test Inventory (Repo-Grounded)
- Runner: pytest via `cd agent-memory-server && uv run pytest`
- Commands available (Makefile):
  - make test
  - make test-unit
  - make test-integration
  - make lint (ruff)
- Test locations:
  - agent-memory-server/tests/ and agent-memory-server/tests/unit/

7.2 Test Suites Overview
- Unit
  - Runner: pytest
  - Command: `cd agent-memory-server && uv run pytest`
  - Runtime budget: 2-5 minutes
  - When: pre-commit and CI
- Integration
  - Runner: pytest
  - Command: `cd agent-memory-server && uv run pytest tests/integration/`
  - Runtime budget: 5-10 minutes
  - When: CI/nightly
- Static
  - Runner: ruff
  - Command: `cd agent-memory-server && uv run ruff check .`
  - Runtime budget: 1-2 minutes
  - When: pre-commit and CI

7.3 Test Definitions
- TEST-000
  - name: readme_exists
  - type: unit
  - verifies: REQ-001
  - location: self-learning-guardrails-demo/tests/test_readme_exists.py (to be created)
  - command: `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_readme_exists.py -k test_readme_exists`
  - fixtures/mocks/data: none
  - deterministic controls: none
  - pass_criteria: README exists at ../self-learning-guardrails-demo/README.md and contains Setup and Run sections
  - expected_runtime: 5s
  - traceability tag: add `# TEST-000` in the test file
- TEST-001
  - name: extract_guardrails
  - type: unit
  - verifies: REQ-002, REQ-012
  - location: self-learning-guardrails-demo/tests/test_guardrails_memory.py (to be created)
  - command: `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_guardrails_memory.py -k test_extract_guardrails`
  - fixtures/mocks/data: fixed corrections list in test file
  - deterministic controls: set RANDOM_SEED=42 in test
  - pass_criteria: output JSON includes hard_constraints list with at least 3 required rules and triggers list with at least 1 entry
  - expected_runtime: 10s
  - traceability tag: add `# TEST-001` in the test file
- TEST-002
  - name: scripted_replay_outputs
  - type: integration
  - verifies: REQ-003, REQ-004, REQ-005
  - location: self-learning-guardrails-demo/tests/test_scripted_replay.py (to be created)
  - command: `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_scripted_replay.py -k test_scripted_replay_outputs`
  - fixtures/mocks/data: mock mode enabled via env GUARDRAILS_DEMO_MODE=mock
  - deterministic controls: set RANDOM_SEED=42 and fixed prompt file
  - pass_criteria: artifacts directory contains run.json, memory.json, metrics.json with expected keys
  - expected_runtime: 20s
  - traceability tag: add `# TEST-002` in the test file
- TEST-003
  - name: turn_reduction
  - type: integration
  - verifies: REQ-003, REQ-007
  - location: self-learning-guardrails-demo/tests/test_memory_injection.py (to be created)
  - command: `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_memory_injection.py -k test_turn_reduction`
  - fixtures/mocks/data: mock mode enabled via env GUARDRAILS_DEMO_MODE=mock
  - deterministic controls: set RANDOM_SEED=42 and fixed prompt file
  - pass_criteria: metrics.json shows correction_turns_after <= correction_turns_before * 0.5
  - expected_runtime: 20s
  - traceability tag: add `# TEST-003` in the test file
- TEST-004
  - name: interactive_fail_fast
  - type: unit
  - verifies: REQ-006, REQ-009, REQ-014
  - location: self-learning-guardrails-demo/tests/test_interactive_mode.py (to be created)
  - command: `cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_interactive_mode.py -k test_interactive_fail_fast`
  - fixtures/mocks/data: unset OPENAI_API_KEY
  - deterministic controls: none
  - pass_criteria: CLI exits with non-zero and prints missing key remediation text
  - expected_runtime: 10s
  - traceability tag: add `# TEST-004` in the test file

7.4 Manual Checks (Optional)
- CHECK-001: Run `cd self-learning-guardrails-demo && python demo_cli.py --mode live --interactive` with valid API key and confirm memory injection reduces corrections in a free-form prompt.

Data Contract
- memory.json
  - schema:
    - hard_constraints: list[str]
    - architecture_preferences: list[str]
    - clarifying_triggers: list[{trigger_terms: list[str], question: str}]
    - verification_rules: list[str]
  - invariants:
    - hard_constraints length >= 3
    - trigger_terms non-empty for each trigger
- run.json
  - schema:
    - run_id: str
    - mode: mock|live
    - prompt_id: str
    - turns: list[{role: str, content: str}]
    - corrections: list[str]
- metrics.json
  - schema:
    - correction_turns_before: int
    - correction_turns_after: int
    - turn_reduction_pct: float
    - runtime_sec: float
  - invariants:
    - turn_reduction_pct = 100 * (before - after) / before

Reproducibility
- Seeds: RANDOM_SEED=42, PYTHONHASHSEED=0
- Hardware: laptop class CPU, no GPU required
- OS: macOS/Linux/WSL supported in mock mode
- Container: none required; uses uv + python3.10+ from agent-memory-server

RTM (Requirements Traceability Matrix)
| Phase | REQ-### | TEST-### | Test Path | Command |
| P00 | REQ-001 | TEST-000 | self-learning-guardrails-demo/tests/test_readme_exists.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_readme_exists.py -k test_readme_exists |
| P01 | REQ-002 | TEST-001 | self-learning-guardrails-demo/tests/test_guardrails_memory.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_guardrails_memory.py -k test_extract_guardrails |
| P02 | REQ-003 | TEST-002 | self-learning-guardrails-demo/tests/test_scripted_replay.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_scripted_replay.py -k test_scripted_replay_outputs |
| P02 | REQ-004 | TEST-002 | self-learning-guardrails-demo/tests/test_scripted_replay.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_scripted_replay.py -k test_scripted_replay_outputs |
| P02 | REQ-005 | TEST-002 | self-learning-guardrails-demo/tests/test_scripted_replay.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_scripted_replay.py -k test_scripted_replay_outputs |
| P03 | REQ-007 | TEST-003 | self-learning-guardrails-demo/tests/test_memory_injection.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_memory_injection.py -k test_turn_reduction |
| P04 | REQ-006 | TEST-004 | self-learning-guardrails-demo/tests/test_interactive_mode.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_interactive_mode.py -k test_interactive_fail_fast |
| P04 | REQ-009 | TEST-004 | self-learning-guardrails-demo/tests/test_interactive_mode.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_interactive_mode.py -k test_interactive_fail_fast |
| P04 | REQ-014 | TEST-004 | self-learning-guardrails-demo/tests/test_interactive_mode.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_interactive_mode.py -k test_interactive_fail_fast |
| P01 | REQ-012 | TEST-001 | self-learning-guardrails-demo/tests/test_guardrails_memory.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_guardrails_memory.py -k test_extract_guardrails |
| P03 | REQ-015 | TEST-003 | self-learning-guardrails-demo/tests/test_memory_injection.py | cd /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/agent-memory-server && uv run pytest /home/kirill/hachathons/we-ve-been-through-this-weave-hackathon-260131/self-learning-guardrails-demo/tests/test_memory_injection.py -k test_turn_reduction |

Execution Log (Living Document Template)
- Phase Status (Pending/Done):
- Completed Steps:
- Quantitative Results (Metrics mean +/- std, 95% CI):
- Issues/Resolutions (What went wrong, how it was solved):
- Failed Attempts (What was tried and discarded):
- Deviations (Changes from original plan):
- Lessons Learned:
- ADR Updates (Link to new decisions):

Appendix: ADR Index
- ADR-001: Use short scripted demo instead of long benchmarks
- ADR-002: Place demo in repository root as a separate folder
- ADR-003: Scripted replay first, interactive mode later
- ADR-004: Mock mode required for deterministic tests
- ADR-005: Fail-fast required for missing config or API keys

Consistency Check
- RTM covers all REQs: REQ-001..REQ-015 mapped to TEST-000..TEST-004
- Every Phase has metrics populated: P00..P04 metrics present
- Execution steps include explicit verification commands: all RED/GREEN/REFACTOR/MEASURE steps include runnable commands
