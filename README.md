# We've Been Through This (WBTT) -- WeaveHacks 3 -- Self-Improving Agents

One-liner: Self-learning system-architecture and engineering memory for LLM coding assistants that turns historical long discussions into one-shot fixes.

## Summary (2-3 sentences)

WBTT captures real multi-step debugging conversations from Claude Code in W&B Weave, distills them into reusable memory artifacts with MemEvolve, and stores them in Redis. When a similar issue appears later, the assistant retrieves that abstract memory via MCP and resolves the problem in one or two steps instead of 10-30. This demonstrates self-learning agents that improve their software engineering and system-architecture efficiency over time.

## What it does / why it is useful

- Eliminates repeated multi-turn debugging loops for recurring issues.
- Forces evidence-driven debugging by retrieving full logs from W&B artifacts instead of guessing.
- Injects a proven fix path into the LCA via Redis-backed memory, reducing token/time waste.

## System architecture

```
Claude Code
  -> Weave Claude plugin (hooks) -> Weave traces + W&B run artifacts
  -> MemEvolve distillation (memory artifact)
  -> Redis Agent Memory Server (MCP)
  -> memory_prompt injection back into Claude Code
```

## How it is built (agentic logic, data flow, MCP)

1. Claude Code session is traced to W&B Weave using the claude_plugin hooks (session, user prompts, tool calls).
2. The historical trace is distilled into a MemEvolve-style memory artifact (evidence + decision path + fix).
3. The artifact is stored as long-term memory in Redis via agent-memory-server MCP tools.
4. For a new prompt, Claude Code calls `memory_prompt` to retrieve relevant memory.
5. The injected memory guides the assistant to the correct log evidence and the correct code path.

MCP servers/A2A:

- Redis agent-memory-server exposes MCP tools like `memory_prompt`, `create_long_term_memory`, and `edit_long_term_memory`.
- Claude Code uses MCP to retrieve the memory artifact and inject it into the prompt.

## Sponsor tools/protocols used (critical)

- **Weights & Biases Weave**: traces Claude Code sessions and tool calls; W&B run artifacts contain full pytest logs used for evidence.
- **Redis (agent-memory-server + MCP)**: stores MemEvolve memory artifacts and serves `memory_prompt` injections.
- **MCP protocol**: used for memory retrieval and management between Claude Code and Redis agent-memory-server.

## Creativity

WBTT turns real debugging traces into a living playbook. The memory is not static documentation; it evolves from successful trajectories and is injected into future agent runs, reducing confusion and duplication.

## Self-improving-ness

Yes. Each solved debugging session creates a new memory artifact. Subsequent similar prompts become faster and more accurate as the memory base grows.

## Utility

High. Developers waste millions of tokens on repeated multi-step debugging loops. WBTT converts that into a single-step fix path using historical evidence.

## Technical execution

The pipeline is end-to-end: Claude Code traces -> Weave artifacts -> MemEvolve memory artifact -> Redis MCP retrieval -> Claude Code injection. The demo also includes a scripted fallback if live services are unavailable.

## Demo context (used by the LCA)

Context: We are in an event ingestion repo. The failing test is `tests/test_event_dedupe_idempotent.py`.
There are two dedupe implementations: `dedupe/v2/` and `dedupe/legacy/`.
Pipeline selection is logged on startup as `selected_pipeline=...` (top of the W&B pytest artifact).
If `DEDUPER=v2` is unset or v2 throws, the system falls back to `legacy_fallback`.
v2 expects `event.metadata.pricingContext.currency`; if missing it throws, which triggers fallback.
Legacy and v2 are duplicated; editing the wrong path will not affect runtime.
The full pytest artifact is stored in the W&B run; terminal snippets are truncated.
Key fix pattern: derive minimal `pricingContext` at entrypoint + make legacy a shim to v2 or set `DEDUPER=v2` for tests.

## Demo script (hybrid fallback + pipeline selection)

### Discussion 1 (historical, 10 iterations, creates memory)

1 User: CI is red; test_event_dedupe_idempotent fails; use W&B run logs.
1 Claude: I will open the full pytest artifact from W&B.
2 User: Don't guess; open run ci-18421 artifact, not terminal snippets.
2 Claude: I already have the stack trace; it points to v2 dedupe.
3 User: Output is truncated; open the full artifact.
3 Claude: Full artifact shows "expected 1, got 2" plus a fallback warning.
4 User: What path executed per logs?
4 Claude: Looks like v2; I will tighten the dedupe key.
5 User: Rerun still fails; your change didn't affect runtime behavior.
5 Claude: Then I may be editing the wrong entrypoint; I'll search for fallback flags.
6 User: Search the artifact for selected_pipeline or fallback.
6 Claude: I didn't see it; maybe I missed earlier lines.
7 User: Open the top of the artifact; pipeline is logged on startup.
7 Claude: Found it: selected_pipeline=legacy_fallback because DEDUPER wasn't set.
8 User: So you edited the wrong file/path.
8 Claude: Yes; legacy path ran. We should make legacy a shim to v2 or set DEDUPER=v2.
9 User: There's also a warning about missing pricingContext; why?
9 Claude: v2 threw missing pricingContext.currency, triggering fallback; entrypoint must derive context.
10 User: Summarize the fix and the lesson.
10 Claude: Fix: derive pricingContext at entrypoint + legacy delegates to v2 + set DEDUPER=v2; lesson: verify executed path via full artifact and lines above fallback warning.

### Discussion 2 (new prompt with MemEvolve injection, 1 iteration)

1 User: CI is red again; test_event_dedupe_idempotent fails; run ci-19702 has logs.
1 Claude: Memory says check selected_pipeline in full artifact; it is legacy_fallback and v2 threw missing pricingContext; I derived context, made legacy shim to v2, set DEDUPER=v2, reran, and CI passes.

### Discussion 3 (same prompt without memory, 10 iterations)

1 User: CI is red again; test_event_dedupe_idempotent fails; run ci-19702 has logs.
1 Claude: I will adjust the v2 dedupe key.
2 User: Use the full W&B artifact; don't infer from partial output.
2 Claude: Log shows "expected 1, got 2"; still looks like v2.
3 User: What handler ran in that run?
3 Claude: It should be v2; I'll make v2 stricter.
4 User: Still failing; you're not changing what is executed.
4 Claude: Maybe we need more runtime context; are there additional logs?
5 User: Yes, open the full pytest artifact; terminal output truncates.
5 Claude: I looked already; I didn't notice anything else.
6 User: Search for selected_pipeline or fallback.
6 Claude: No matches; maybe I missed earlier lines.
7 User: Start from the top; pipeline is logged on startup.
7 Claude: Found it now: selected_pipeline=legacy_fallback due to missing env config.
8 User: So fix legacy path, not v2.
8 Claude: Right; patch legacy to delegate to v2 and set DEDUPER=v2.
9 User: Also address the missing pricingContext warning.
9 Claude: Entry point should derive pricingContext so v2 doesn't throw.
10 User: This 10-step loop is the token waste we're demoing.
10 Claude: Agreed; without memory we repeat the same missing-logs and wrong-path cycle.

## How to run (live demo)

### 1) Start Redis
```
redis-server --save "" --appendonly no
```
Confirm Redis is running:
```
redis-cli ping
```

### 2) Start the Agent Memory Server (Redis + MCP)

```
cd agent-memory-server
uv run agent-memory api
```

### 3) Enable Claude Code -> Weave tracing

Add Claude Code hooks to `~/.claude/settings.json` and enable Weave tracing:

```
python -m weave.integrations.claude_plugin.config enable --global
export WEAVE_PROJECT="your-entity/your-project"
```

(See `claude-weave-readme-fix.txt` for the full hook config example.)

### 4) Run the historical prompt (creates memory)

- Start a Claude Code session with Weave tracing on.
- Run Discussion 1 and confirm the trace appears in W&B.
- Distill a MemEvolve memory artifact from the trace and store it in Redis via MCP tools.

### 5) Run the new prompt (memory on)

- Use the same `user_id`/`session_id` to retrieve memory via `memory_prompt`.
- Run Discussion 2 and show the 1-step resolution.

### 6) Run the new prompt (memory off)

- Use a fresh `user_id`/`session_id` with no memories, or disable memory_prompt.
- Run Discussion 3 to show the 10-step thrash.

## Repo layout

- `MemEvolve/` - MemEvolve paper implementation (memory distillation).
- `agent-memory-server/` - Redis-backed memory server with MCP tools.
- `weave/` - Weave tracing and Claude Code integration.
- `weave-pipecat/` - UI and supporting services (optional).

## License

Apache-2.0 (see LICENSE).
