Title and Metadata
- Project: We've Been Through This (WBTT)
- Version: 0.2.0
- Owners: Research-Engineering PM, Demo Engineer, Agent Integration Engineer
- Date: 2026-02-01
- Document ID: WBTT-SRS-PLAN-001
- Summary: Build a fully working, no-Docker demo pipeline that captures Claude Code debugging traces in Weave, distills MemEvolve-style memory artifacts, creates a manual KER artifact in parallel, stores memory in Redis via agent-memory-server MCP, and retrieves it to reduce multi-step debugging to one or two steps. The plan includes a scripted fallback and standards-aligned requirements, tests, and evaluation gates.

Design Consensus & Trade-offs
- Topic: End-to-end live pipeline vs scripted-only
  - Verdict: FOR live end-to-end, WITH scripted fallback
  - Rationale: Demo must show real Weave traces and Redis memory injection; scripted backup mitigates runtime risk
- Topic: Weave trace source
  - Verdict: FOR live W&B traces and artifacts
  - Rationale: Demonstrates sponsor usage and real tool outputs with full pytest artifacts
- Topic: Memory artifact format
  - Verdict: FOR full MemEvolve-style artifact with evidence and steps
  - Rationale: Aligns with MemEvolve prompts and README; makes memory auditable and reusable
- Topic: Manual KER creation
  - Verdict: FOR parallel KER artifact creation (dual-channel distillation)
  - Rationale: Produces an operator-grade knowledge record alongside agent memory; aligns with KER prompt requirements
 - Topic: Prompt quality for artifacts
  - Verdict: FOR evidence-first, Claude-Code-specific prompts
  - Rationale: Ensures structured, trace-grounded outputs that are retrieval-friendly and demo-stable
- Topic: Redis integration path
  - Verdict: FOR agent-memory-server MCP tools
  - Rationale: Uses sponsor tooling, supports memory_prompt injection, and is agentic; align with agent-memory-server/examples/memory_editing_agent.py
- Topic: Claude Code integration
  - Verdict: FOR MCP-based memory_prompt retrieval
  - Rationale: Cleanest injection point without wrapper services; align with weave/weave/integrations/claude_plugin and claude-weave-readme-fix.txt
- Topic: Container usage
  - Verdict: AGAINST Docker
  - Rationale: Constraint requires local services or user-launched servers

PRD (IEEE 29148 Stakeholder/System Needs)
- Problem: LLM coding assistants repeatedly spend 10-30 turns on recurring debugging issues because they lack memory of prior successful resolutions and rely on truncated logs
- Users: SWEs using Claude Code; hackathon judges assessing self-learning agents
- Value: Reduces debugging turns, tokens, and time; improves evidence-driven debugging
- Business Goals: Demonstrate sponsor tooling (W&B Weave, Redis MCP) and self-improving agent behavior in a live demo
- Success Metrics:
  - Memory-on runs resolve in <=2 turns
  - Memory-off runs resolve in >=8 turns on same prompt
  - Weave trace shows tool call evidence for memory retrieval and log access
  - KER artifact is created in ./ker/ and displayed
- Scope:
  - End-to-end demo pipeline with Weave traces, MemEvolve-style memory artifact, Redis MCP storage, memory_prompt retrieval, KER creation, and demo transcripts
- Non-goals:
  - Full MemEvolve training/evolution pipeline on large datasets
  - Production-grade multi-tenant memory governance
- Dependencies:
  - W&B Weave tracing via weave/weave/integrations/claude_plugin
  - Claude Code hook config reference in claude-weave-readme-fix.txt
  - Redis running locally or managed URL
  - agent-memory-server MCP interface; use agent-memory-server/examples/memory_editing_agent.py as reference for create/edit flows
  - MemEvolve/ (README and prompts) as reference for memory artifact schema and distillation
- Risks:
  - Live service instability or missing artifacts
  - Memory retrieval mismatch due to weak tags or cues
  - KER prompt output missing required fields
- Assumptions:
  - Claude Code hooks are configured and Weave project is set
  - Redis and agent-memory-server are available locally or via user-provided endpoints

SRS (IEEE 29148 Canonical Requirements)
4.1 Functional Requirements
- REQ-001 (type: func): Capture Claude Code sessions as Weave traces, including tool calls and artifact references
- REQ-002 (type: func): Extract evidence lines from W&B pytest artifacts, including selected_pipeline and fallback warnings
- REQ-003 (type: func): Distill a MemEvolve-style memory artifact with evidence, root cause, and fix steps
- REQ-004 (type: func): Store memory artifact in Redis via agent-memory-server MCP
- REQ-005 (type: func): Retrieve memory via memory_prompt and inject into a new Claude Code prompt
- REQ-006 (type: func): Produce scripted fallback transcripts for demo reliability
- REQ-007 (type: func): Provide a demo context block describing the target codebase assumptions
- REQ-008 (type: func): Create a manual KER artifact in ./ker/ using the KER prompt and conversation evidence
- REQ-009 (type: func): Run dual-channel distillation so MemEvolve artifact and KER are produced from the same trace

4.2 Non-functional Requirements
- REQ-101 (type: nfr): Memory retrieval latency <= 1.5s for local Redis
- REQ-102 (type: nfr): Memory artifacts must be versioned and traceable to a Weave trace ID
- REQ-103 (type: nfr): Demo must run without Docker

4.3 Interfaces/APIs
- REQ-201 (type: int): Weave Claude plugin hooks must record session and tool-call traces; reference weave/weave/integrations/claude_plugin
- REQ-202 (type: int): agent-memory-server MCP tools used: memory_prompt, create_long_term_memory, edit_long_term_memory; reference agent-memory-server/examples/memory_editing_agent.py
- REQ-203 (type: int): Environment variables: WEAVE_PROJECT, MEMORY_SERVER_URL, REDIS_URL, WBTT_USER_ID, WBTT_SESSION_ID

4.4 Data Requirements
- REQ-301 (type: data): Memory artifact schema must include evidence_to_check and fix_steps; align with MemEvolve prompt templates under MemEvolve/Flash-Searcher-main/MemEvolve/prompts/
- REQ-302 (type: data): Artifacts must include tags for retrieval cues and source_trace_id
- REQ-303 (type: data): Demo transcripts must be stored as deterministic fixtures for scripted fallback
- REQ-304 (type: data): KER files must be stored in ./ker/ with filename format ./ker/YYYYMMDD-primary-symptom-root-cause.md
 - REQ-305 (type: data): Memory injection prompt must require mandatory evidence checks and anti-pattern warnings

4.5 Error & Telemetry Expectations
- REQ-401 (type: nfr): Log explicit errors for missing artifact lines, Redis connectivity, and MCP failures
- REQ-402 (type: nfr): Emit telemetry counters for memory_hit, memory_miss, fallback_triggered, ker_created

4.6 Acceptance Criteria
- Live demo shows Weave trace tree for historical run with full pytest artifact evidence
- Memory-on run resolves in <=2 turns using memory_prompt retrieval
- Memory-off run shows >=8 turns and repeated log discovery
- MemEvolve artifact displayed with evidence and fix steps
- KER artifact created in ./ker/ and displayed
- No Docker usage in instructions or setup

4.7 System Architecture Diagram
```mermaid
graph TD
  A[Claude Code] --> B[Weave Claude Plugin]
  B --> C[Weave Trace + W&B Artifact]
  C --> D[MemEvolve Distiller]
  C --> K[KER Creator]
  D --> E[Redis Agent Memory Server (MCP)]
  A -->|memory_prompt| E
  E --> A
  K --> F[./ker/ Knowledge Artifact]
```
C4-style ASCII
- System: WBTT
  - Container: Claude Code session
    - Component: Weave plugin hook
  - Container: Weave trace service
    - Component: trace tree + artifact store
  - Container: MemEvolve distiller
    - Component: artifact schema builder
  - Container: KER creator
    - Component: KER markdown writer
  - Container: Redis agent-memory-server
    - Component: MCP memory_prompt + long-term storage

Iterative Implementation & Test Plan (ISO/IEC/IEEE 12207 + 29119-3)
- Phase Strategy: split by complexity and isolate evidence extraction, artifact shaping, KER creation, storage, retrieval, and demo orchestration
- Verification-first: evaluation metrics are binding tests
- Compute Policy:
  - branch_limits: max 3 parallel branches
  - reflection_passes: 2 per phase
  - early_stop%: 15% (stop phase if >=15% of steps fail twice)
- Governance:
  - Any change to a metric threshold requires a documented ADR
- State Safety:
  - Create a git tag before each phase transition: wbtt-pxx-ready
- Risk Register:
  - Risk: W&B artifact missing selected_pipeline
    - Trigger: extractor fails to find evidence line
    - Mitigation: fixture-based fallback and explicit error messaging
  - Risk: MCP tool unavailability in Claude Code
    - Trigger: memory_prompt call fails
    - Mitigation: scripted fallback and manual injection instructions
  - Risk: Redis unavailable
    - Trigger: connection error
    - Mitigation: check before demo; prompt user to start local Redis
  - Risk: KER output missing required sections
    - Trigger: KER validation test fails
    - Mitigation: adjust KER prompt and regenerate
- Suspension/Resumption Criteria:
  - Suspend if: memory_prompt retrieval fails twice or Weave traces not visible
  - Resume after: connectivity verified and at least one successful memory_prompt call

### Phase P00: Evidence Fixture and Log Extractor
- Scope and Objectives:
  - Establish fixtures and extract evidence lines from W&B pytest artifacts
  - Impacted REQs: REQ-002, REQ-301
  - Reference: MemEvolve/Flash-Searcher-main/MemEvolve/prompts/ for evidence cues
- Iterative Execution Steps:
  - Step 1 (RED): Create TEST-001 in agent-memory-server/tests/test_wbtt_extractor.py with tag # TEST-001; add fixture file agent-memory-server/tests/fixtures/wbtt/pytest_artifact_sample.txt with tag # TEST-001 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_extractor.py -k TEST-001 -> expected: FAIL because extractor missing
  - Step 2 (GREEN): Implement minimal extractor in agent-memory-server/agent_memory_server/wbtt/extract.py -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Normalize parser into pure functions -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run eval EVAL-001 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_extractor.py -k TEST-001 -> expected: thresholds met
- Exit Gate Rules:
  - Green: TEST-001 pass; EVAL-001 pass
  - Yellow: TEST-001 pass, eval within 10%
  - Red: TEST-001 fails
- Phase Metrics:
  - Confidence 78%
  - Long-term robustness 62%
  - Internal interactions 2
  - External interactions 0
  - Complexity 22%
  - Feature creep 10%
  - Technical debt 15%
  - YAGNI score 20%
  - MoSCoW: Must
  - Local/Non-local scope: Local
  - Architectural changes count: 1

### Phase P01: MemEvolve Artifact Schema and Distillation
- Scope and Objectives:
  - Define MemEvolve artifact schema and distill from trace evidence
  - Impacted REQs: REQ-003, REQ-301, REQ-302
  - Reference: MemEvolve/README.md and MemEvolve/Flash-Searcher-main/MemEvolve/prompts/
- Iterative Execution Steps:
  - Step 0 (RED): Create artifact prompt fixture at agent-memory-server/tests/fixtures/wbtt/prompts/memory_distillation_prompt.txt with tag # TEST-002 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_memevolve_artifact.py -k TEST-002 -> expected: FAIL because prompt fixture missing
  - Step 1 (RED): Create TEST-002 in agent-memory-server/tests/test_wbtt_memevolve_artifact.py with tag # TEST-002 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_memevolve_artifact.py -k TEST-002 -> expected: FAIL because schema validator missing
  - Step 2 (GREEN): Implement schema validator in agent-memory-server/agent_memory_server/wbtt/memevolve_artifact.py -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Add strict field checks and tag requirements -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run eval EVAL-002 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_memevolve_artifact.py -k TEST-002 -> expected: thresholds met
- Exit Gate Rules:
  - Green: TEST-002 pass; EVAL-002 pass
  - Yellow: TEST-002 pass, eval within 10%
  - Red: TEST-002 fails
- Phase Metrics:
  - Confidence 76%
  - Long-term robustness 65%
  - Internal interactions 2
  - External interactions 0
  - Complexity 28%
  - Feature creep 12%
  - Technical debt 12%
  - YAGNI score 20%
  - MoSCoW: Must
  - Local/Non-local scope: Local
  - Architectural changes count: 1

### Phase P02: Manual KER Artifact Creation and Validation
- Scope and Objectives:
  - Create and validate KER artifact in ./ker/ using the provided KER prompt
  - Impacted REQs: REQ-008, REQ-304
  - Reference: KER prompt specification and ./ker/ convention
- Iterative Execution Steps:
  - Step 0 (RED): Create KER prompt fixture at agent-memory-server/tests/fixtures/wbtt/prompts/ker_prompt.txt with tag # TEST-003 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_ker.py -k TEST-003 -> expected: FAIL because prompt fixture missing
  - Step 1 (RED): Create TEST-003 in agent-memory-server/tests/test_wbtt_ker.py with tag # TEST-003 to validate ./ker/ file naming and required headings -> run cd agent-memory-server && uv run pytest tests/test_wbtt_ker.py -k TEST-003 -> expected: FAIL because ./ker/ file missing
  - Step 2 (GREEN): Create KER file in ./ker/ with required structure -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Normalize KER headings and add grep-friendly tags -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run eval EVAL-003 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_ker.py -k TEST-003 -> expected: thresholds met
- Exit Gate Rules:
  - Green: TEST-003 pass; EVAL-003 pass
  - Yellow: TEST-003 pass, eval within 10%
  - Red: TEST-003 fails
- Phase Metrics:
  - Confidence 70%
  - Long-term robustness 58%
  - Internal interactions 1
  - External interactions 0
  - Complexity 20%
  - Feature creep 10%
  - Technical debt 10%
  - YAGNI score 25%
  - MoSCoW: Must
  - Local/Non-local scope: Local
  - Architectural changes count: 0

### Phase P03: Dual-channel Distillation Orchestration
- Scope and Objectives:
  - Ensure MemEvolve artifact and KER are produced from the same trace
  - Impacted REQs: REQ-009, REQ-303
- Iterative Execution Steps:
  - Step 1 (RED): Create TEST-004 in agent-memory-server/tests/test_wbtt_dual_channel.py with tag # TEST-004 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_dual_channel.py -k TEST-004 -> expected: FAIL because orchestration missing
  - Step 2 (GREEN): Implement orchestrator in agent-memory-server/agent_memory_server/wbtt/dual_channel.py -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Separate trace ingestion from artifact writing -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run eval EVAL-004 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_dual_channel.py -k TEST-004 -> expected: thresholds met
- Exit Gate Rules:
  - Green: TEST-004 pass; EVAL-004 pass
  - Yellow: TEST-004 pass, eval within 10%
  - Red: TEST-004 fails
- Phase Metrics:
  - Confidence 68%
  - Long-term robustness 55%
  - Internal interactions 2
  - External interactions 0
  - Complexity 30%
  - Feature creep 18%
  - Technical debt 15%
  - YAGNI score 30%
  - MoSCoW: Must
  - Local/Non-local scope: Local
  - Architectural changes count: 1

### Phase P04: Memory Storage via MCP
- Scope and Objectives:
  - Store MemEvolve artifact in Redis using MCP tools
  - Impacted REQs: REQ-004, REQ-202
  - Reference: agent-memory-server/examples/memory_editing_agent.py
- Iterative Execution Steps:
  - Step 1 (RED): Create TEST-005 in agent-memory-server/tests/test_wbtt_memory_store.py with tag # TEST-005; mock MemoryAPIClient -> run cd agent-memory-server && uv run pytest tests/test_wbtt_memory_store.py -k TEST-005 -> expected: FAIL because storage adapter missing
  - Step 2 (GREEN): Implement storage adapter in agent-memory-server/agent_memory_server/wbtt/memory_store.py -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Add typed interfaces and error handling -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run eval EVAL-005 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_memory_store.py -k TEST-005 -> expected: thresholds met
- Exit Gate Rules:
  - Green: TEST-005 pass; EVAL-005 pass
  - Yellow: TEST-005 pass, eval within 10%
  - Red: TEST-005 fails
- Phase Metrics:
  - Confidence 72%
  - Long-term robustness 66%
  - Internal interactions 2
  - External interactions 1
  - Complexity 32%
  - Feature creep 15%
  - Technical debt 18%
  - YAGNI score 25%
  - MoSCoW: Must
  - Local/Non-local scope: Non-local
  - Architectural changes count: 1

### Phase P05: Memory Prompt Retrieval and Injection
- Scope and Objectives:
  - Retrieve memory via memory_prompt and inject into prompt flow
  - Impacted REQs: REQ-005, REQ-101
- Iterative Execution Steps:
  - Step 0 (RED): Create injection prompt fixture at agent-memory-server/tests/fixtures/wbtt/prompts/memory_injection_prompt.txt with tag # TEST-006 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_memory_prompt.py -k TEST-006 -> expected: FAIL because injection prompt missing
  - Step 1 (RED): Create TEST-006 in agent-memory-server/tests/test_wbtt_memory_prompt.py with tag # TEST-006 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_memory_prompt.py -k TEST-006 -> expected: FAIL because injection formatter missing
  - Step 2 (GREEN): Implement injection formatter in agent-memory-server/agent_memory_server/wbtt/memory_prompt.py -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Add latency instrumentation -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run eval EVAL-006 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_memory_prompt.py -k TEST-006 -> expected: thresholds met
- Exit Gate Rules:
  - Green: TEST-006 pass; EVAL-006 pass
  - Yellow: TEST-006 pass, eval within 10%
  - Red: TEST-006 fails
- Phase Metrics:
  - Confidence 70%
  - Long-term robustness 60%
  - Internal interactions 2
  - External interactions 1
  - Complexity 35%
  - Feature creep 18%
  - Technical debt 20%
  - YAGNI score 30%
  - MoSCoW: Must
  - Local/Non-local scope: Non-local
  - Architectural changes count: 1

### Phase P06: Demo Transcripts and Context Pack
- Scope and Objectives:
  - Provide demo transcripts and context block for memory-on and memory-off runs
  - Impacted REQs: REQ-006, REQ-007, REQ-303
- Iterative Execution Steps:
  - Step 1 (RED): Create TEST-007 in agent-memory-server/tests/test_wbtt_transcripts.py with tag # TEST-007 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_transcripts.py -k TEST-007 -> expected: FAIL because transcripts missing
  - Step 2 (GREEN): Add transcript fixtures under agent-memory-server/tests/fixtures/wbtt/transcripts/ -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Normalize transcript templates -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run eval EVAL-007 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_transcripts.py -k TEST-007 -> expected: thresholds met
- Exit Gate Rules:
  - Green: TEST-007 pass; EVAL-007 pass
  - Yellow: TEST-007 pass, eval within 10%
  - Red: TEST-007 fails
- Phase Metrics:
  - Confidence 72%
  - Long-term robustness 58%
  - Internal interactions 1
  - External interactions 0
  - Complexity 22%
  - Feature creep 12%
  - Technical debt 12%
  - YAGNI score 25%
  - MoSCoW: Must
  - Local/Non-local scope: Local
  - Architectural changes count: 0

### Phase P07: Documentation and No-Docker Runbook
- Scope and Objectives:
  - Ensure README and runbook reflect no-Docker setup and reference hooks
  - Impacted REQs: REQ-103, REQ-201
  - Reference: claude-weave-readme-fix.txt and weave/weave/integrations/claude_plugin/
- Iterative Execution Steps:
  - Step 1 (RED): Create TEST-008 in agent-memory-server/tests/test_wbtt_readme.py with tag # TEST-008 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_readme.py -k TEST-008 -> expected: FAIL
  - Step 2 (GREEN): Update README.md at repo root with no-Docker instructions and local Redis start -> run same command -> expected: PASS
  - Step 3 (REFACTOR): Ensure README includes live vs scripted demo steps and references -> run same command -> expected: PASS
  - Step 4 (MEASURE): Run eval EVAL-008 -> run cd agent-memory-server && uv run pytest tests/test_wbtt_readme.py -k TEST-008 -> expected: thresholds met
- Exit Gate Rules:
  - Green: TEST-008 pass; EVAL-008 pass
  - Yellow: TEST-008 pass, eval within 10%
  - Red: TEST-008 fails
- Phase Metrics:
  - Confidence 78%
  - Long-term robustness 65%
  - Internal interactions 1
  - External interactions 0
  - Complexity 18%
  - Feature creep 10%
  - Technical debt 8%
  - YAGNI score 10%
  - MoSCoW: Must
  - Local/Non-local scope: Local
  - Architectural changes count: 0

Evaluations (AI/Agentic Specific)
```yaml
evals:
  - id: EVAL-001
    purpose: dev
    metrics:
      evidence_line_recall: ">= 0.9"
    thresholds:
      evidence_line_recall: 0.9
    seeds: [1]
    runtime_budget: "2m"
  - id: EVAL-002
    purpose: dev
    metrics:
      artifact_field_coverage: ">= 1.0"
    thresholds:
      artifact_field_coverage: 1.0
    seeds: [1]
    runtime_budget: "2m"
  - id: EVAL-003
    purpose: dev
    metrics:
      ker_required_sections: ">= 1.0"
    thresholds:
      ker_required_sections: 1.0
    seeds: [1]
    runtime_budget: "2m"
  - id: EVAL-004
    purpose: dev
    metrics:
      dual_channel_outputs: ">= 2"
    thresholds:
      dual_channel_outputs: 2
    seeds: [1]
    runtime_budget: "2m"
  - id: EVAL-005
    purpose: dev
    metrics:
      memory_store_success_rate: ">= 0.9"
    thresholds:
      memory_store_success_rate: 0.9
    seeds: [1]
    runtime_budget: "3m"
  - id: EVAL-006
    purpose: dev
    metrics:
      memory_prompt_latency_ms_p95: "<= 1500"
    thresholds:
      memory_prompt_latency_ms_p95: 1500
    seeds: [1]
    runtime_budget: "3m"
  - id: EVAL-007
    purpose: dev
    metrics:
      turns_saved_ratio: ">= 0.7"
    thresholds:
      turns_saved_ratio: 0.7
    seeds: [1]
    runtime_budget: "2m"
  - id: EVAL-008
    purpose: dev
    metrics:
      doc_completeness: ">= 0.9"
    thresholds:
      doc_completeness: 0.9
    seeds: [1]
    runtime_budget: "1m"
```

Tests (ISO/IEC/IEEE 29119-3)
7.1 Test Inventory (Repo-Grounded)
- agent-memory-server pytest
  - Runner: uv + pytest
  - Command: cd agent-memory-server && uv run pytest
- weave-pipecat/client static lint
  - Runner: next lint
  - Command: cd weave-pipecat/client && npm run lint

7.2 Test Suites Overview
- Unit
  - Runner: uv run pytest
  - Command: cd agent-memory-server && uv run pytest tests/test_wbtt_extractor.py -k TEST-001
  - Runtime budget: 2m
  - When: pre-commit and CI
- Integration
  - Runner: uv run pytest
  - Command: cd agent-memory-server && uv run pytest tests/test_wbtt_dual_channel.py -k TEST-004
  - Runtime budget: 3m
  - When: CI
- Static
  - Runner: next lint
  - Command: cd weave-pipecat/client && npm run lint
  - Runtime budget: 2m
  - When: pre-commit

7.3 Test Definitions
- id: TEST-001
  - name: wbtt_extractor_finds_pipeline_and_fallback
  - type: unit
  - verifies: REQ-002
  - location: agent-memory-server/tests/test_wbtt_extractor.py
  - command: cd agent-memory-server && uv run pytest tests/test_wbtt_extractor.py -k TEST-001
  - fixtures/mocks/data: agent-memory-server/tests/fixtures/wbtt/pytest_artifact_sample.txt
  - deterministic controls: WBTT_OFFLINE=1, PYTHONHASHSEED=0
  - pass_criteria: extractor returns selected_pipeline line and fallback warning line
  - expected_runtime: 10s
  - tag: test file includes # TEST-001
- id: TEST-002
  - name: wbtt_memevolve_artifact_schema_required_fields
  - type: unit
  - verifies: REQ-003, REQ-301, REQ-302
  - location: agent-memory-server/tests/test_wbtt_memevolve_artifact.py
  - command: cd agent-memory-server && uv run pytest tests/test_wbtt_memevolve_artifact.py -k TEST-002
  - fixtures/mocks/data: agent-memory-server/tests/fixtures/wbtt/pytest_artifact_sample.txt; agent-memory-server/tests/fixtures/wbtt/prompts/memory_distillation_prompt.txt
  - deterministic controls: WBTT_OFFLINE=1, PYTHONHASHSEED=0
  - pass_criteria: artifact validates required fields and tags; missing fields raise ValueError
  - expected_runtime: 10s
  - tag: test file includes # TEST-002
- id: TEST-003
  - name: wbtt_ker_file_naming_and_sections
  - type: integration
  - verifies: REQ-008, REQ-304
  - location: agent-memory-server/tests/test_wbtt_ker.py
  - command: cd agent-memory-server && uv run pytest tests/test_wbtt_ker.py -k TEST-003
  - fixtures/mocks/data: ./ker/YYYYMMDD-primary-symptom-root-cause.md; agent-memory-server/tests/fixtures/wbtt/prompts/ker_prompt.txt
  - deterministic controls: WBTT_OFFLINE=1
  - pass_criteria: KER file exists, filename matches format, required headings present
  - expected_runtime: 10s
  - tag: test file includes # TEST-003
- id: TEST-004
  - name: wbtt_dual_channel_outputs
  - type: integration
  - verifies: REQ-009
  - location: agent-memory-server/tests/test_wbtt_dual_channel.py
  - command: cd agent-memory-server && uv run pytest tests/test_wbtt_dual_channel.py -k TEST-004
  - fixtures/mocks/data: agent-memory-server/tests/fixtures/wbtt/pytest_artifact_sample.txt
  - deterministic controls: WBTT_OFFLINE=1
  - pass_criteria: both MemEvolve artifact and KER output are produced for the same trace input
  - expected_runtime: 15s
  - tag: test file includes # TEST-004
- id: TEST-005
  - name: wbtt_memory_store_roundtrip_mock
  - type: integration
  - verifies: REQ-004, REQ-202
  - location: agent-memory-server/tests/test_wbtt_memory_store.py
  - command: cd agent-memory-server && uv run pytest tests/test_wbtt_memory_store.py -k TEST-005
  - fixtures/mocks/data: mocked MemoryAPIClient
  - deterministic controls: WBTT_OFFLINE=1
  - pass_criteria: create_long_term_memory called with tags and source_trace_id
  - expected_runtime: 20s
  - tag: test file includes # TEST-005
- id: TEST-006
  - name: wbtt_memory_prompt_injection
  - type: integration
  - verifies: REQ-005, REQ-101, REQ-305
  - location: agent-memory-server/tests/test_wbtt_memory_prompt.py
  - command: cd agent-memory-server && uv run pytest tests/test_wbtt_memory_prompt.py -k TEST-006
  - fixtures/mocks/data: mocked MemoryAPIClient; agent-memory-server/tests/fixtures/wbtt/prompts/memory_injection_prompt.txt
  - deterministic controls: WBTT_OFFLINE=1
  - pass_criteria: memory_prompt output is injected into prompt template; latency measurement recorded
  - expected_runtime: 20s
  - tag: test file includes # TEST-006
- id: TEST-007
  - name: wbtt_transcripts_memory_on_off
  - type: integration
  - verifies: REQ-006, REQ-007, REQ-303
  - location: agent-memory-server/tests/test_wbtt_transcripts.py
  - command: cd agent-memory-server && uv run pytest tests/test_wbtt_transcripts.py -k TEST-007
  - fixtures/mocks/data: agent-memory-server/tests/fixtures/wbtt/transcripts/*.txt
  - deterministic controls: WBTT_OFFLINE=1
  - pass_criteria: memory-on transcript <=2 turns; memory-off transcript >=8 turns
  - expected_runtime: 15s
  - tag: test file includes # TEST-007
- id: TEST-008
  - name: readme_no_docker_and_run_steps_present
  - type: static
  - verifies: REQ-103
  - location: agent-memory-server/tests/test_wbtt_readme.py
  - command: cd agent-memory-server && uv run pytest tests/test_wbtt_readme.py -k TEST-008
  - fixtures/mocks/data: README.md
  - deterministic controls: none
  - pass_criteria: README contains local Redis start and no Docker instructions
  - expected_runtime: 5s
  - tag: test file includes # TEST-008
- id: TEST-009
  - name: weave_claude_plugin_reference_present
  - type: static
  - verifies: REQ-001, REQ-201
  - location: agent-memory-server/tests/test_wbtt_references.py
  - command: cd agent-memory-server && uv run pytest tests/test_wbtt_references.py -k TEST-009
  - fixtures/mocks/data: weave/weave/integrations/claude_plugin/, claude-weave-readme-fix.txt
  - deterministic controls: none
  - pass_criteria: reference paths exist and are readable
  - expected_runtime: 5s
  - tag: test file includes # TEST-009

7.4 Manual Checks
- CHECK-001
  - Verify Weave trace tree shows tool calls for memory_prompt and log retrieval in the live demo

Data Contract
- Memory Artifact Schema
  - Fields: title, trigger_cues[], evidence_to_check[], root_cause, fix_steps[], anti_patterns[], tags[], confidence, source_trace_id, created_at
  - Invariants:
    - trigger_cues and evidence_to_check must be non-empty lists
    - tags must include at least one of: dedupe, fallback, pipeline-selection
    - source_trace_id must match Weave trace ID format
  - Quality:
    - evidence_to_check lines must be exact substrings from artifacts
    - fix_steps must be imperative and ordered
- KER Schema
  - Location: ./ker/
  - Filename: ./ker/YYYYMMDD-primary-symptom-root-cause.md
  - Required sections: Known Error Record title, Trigger patterns, Problem Record, Known Error Record
  - Invariants:
    - KER must include a Git reference line (can be Unknown + How to confirm)
    - KER must include Diagnostic decision path steps

Reproducibility
- OS: Linux (Ubuntu 22.04+)
- Python: 3.12+ with uv
- Node: 18+ for Next.js lint
- Seeds: PYTHONHASHSEED=0
- Containers: none

RTM (Requirements Traceability Matrix)
| Phase | REQ-### | TEST-### | Test Path | Command |
| P00 | REQ-002 | TEST-001 | agent-memory-server/tests/test_wbtt_extractor.py | cd agent-memory-server && uv run pytest tests/test_wbtt_extractor.py -k TEST-001 |
| P01 | REQ-003 | TEST-002 | agent-memory-server/tests/test_wbtt_memevolve_artifact.py | cd agent-memory-server && uv run pytest tests/test_wbtt_memevolve_artifact.py -k TEST-002 |
| P01 | REQ-301 | TEST-002 | agent-memory-server/tests/test_wbtt_memevolve_artifact.py | cd agent-memory-server && uv run pytest tests/test_wbtt_memevolve_artifact.py -k TEST-002 |
| P02 | REQ-008 | TEST-003 | agent-memory-server/tests/test_wbtt_ker.py | cd agent-memory-server && uv run pytest tests/test_wbtt_ker.py -k TEST-003 |
| P02 | REQ-304 | TEST-003 | agent-memory-server/tests/test_wbtt_ker.py | cd agent-memory-server && uv run pytest tests/test_wbtt_ker.py -k TEST-003 |
| P03 | REQ-009 | TEST-004 | agent-memory-server/tests/test_wbtt_dual_channel.py | cd agent-memory-server && uv run pytest tests/test_wbtt_dual_channel.py -k TEST-004 |
| P04 | REQ-004 | TEST-005 | agent-memory-server/tests/test_wbtt_memory_store.py | cd agent-memory-server && uv run pytest tests/test_wbtt_memory_store.py -k TEST-005 |
| P05 | REQ-005 | TEST-006 | agent-memory-server/tests/test_wbtt_memory_prompt.py | cd agent-memory-server && uv run pytest tests/test_wbtt_memory_prompt.py -k TEST-006 |
| P06 | REQ-006 | TEST-007 | agent-memory-server/tests/test_wbtt_transcripts.py | cd agent-memory-server && uv run pytest tests/test_wbtt_transcripts.py -k TEST-007 |
| P06 | REQ-007 | TEST-007 | agent-memory-server/tests/test_wbtt_transcripts.py | cd agent-memory-server && uv run pytest tests/test_wbtt_transcripts.py -k TEST-007 |
| P07 | REQ-103 | TEST-008 | agent-memory-server/tests/test_wbtt_readme.py | cd agent-memory-server && uv run pytest tests/test_wbtt_readme.py -k TEST-008 |
| P07 | REQ-001 | TEST-009 | agent-memory-server/tests/test_wbtt_references.py | cd agent-memory-server && uv run pytest tests/test_wbtt_references.py -k TEST-009 |
| P07 | REQ-201 | TEST-009 | agent-memory-server/tests/test_wbtt_references.py | cd agent-memory-server && uv run pytest tests/test_wbtt_references.py -k TEST-009 |
| P04 | REQ-202 | TEST-005 | agent-memory-server/tests/test_wbtt_memory_store.py | cd agent-memory-server && uv run pytest tests/test_wbtt_memory_store.py -k TEST-005 |
| P06 | REQ-303 | TEST-007 | agent-memory-server/tests/test_wbtt_transcripts.py | cd agent-memory-server && uv run pytest tests/test_wbtt_transcripts.py -k TEST-007 |

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
- ADR-001: Use Weave traces and W&B artifacts as evidence source
- ADR-002: Use Redis agent-memory-server MCP for memory storage and retrieval
- ADR-003: No Docker usage; local services only
- ADR-004: Full MemEvolve-style memory artifact schema
- ADR-005: Dual-channel distillation with KER in ./ker/

Consistency Check
- RTM covers all REQ-### listed in this plan
- Every phase includes explicit RED -> GREEN -> REFACTOR -> MEASURE steps with commands
- Every TEST-### has a concrete path and command
