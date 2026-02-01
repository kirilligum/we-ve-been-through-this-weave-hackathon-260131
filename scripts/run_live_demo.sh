#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEMO_DIR="$ROOT_DIR/demo_claude"
CODEBASE_DIR="$ROOT_DIR/demo_codebase"
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"

WEAVE_PROJECT="${WEAVE_PROJECT:-kirill-igum-prls-co/we-ve-been-through-this-weave-hackathon-260131}"
REDIS_URL="${REDIS_URL:-redis://localhost:6379}"
API_BASE="${API_BASE:-http://localhost:8000}"

if ! redis-cli ping >/dev/null 2>&1; then
  echo "Redis not running. Start it with: redis-server --save \"\" --appendonly no"
  exit 1
fi

if ! redis-cli MODULE LIST | grep -q "search"; then
  echo "RediSearch module not loaded. Falling back to demo vectorstore."
  echo "Start agent-memory-server with:"
  echo "  set -x VECTORSTORE_FACTORY agent_memory_server.wbtt.demo_vectorstore.create_demo_vectorstore"
fi

if ! curl -s "$API_BASE/v1/health" >/dev/null 2>&1; then
  echo "agent-memory-server not running on $API_BASE. Start it with:"
  echo "  cd agent-memory-server"
  echo "  set -x REDIS_URL $REDIS_URL"
  echo "  uv run agent-memory api"
  exit 1
fi

SYSTEM_LIVE=$(cat <<'EOF'
You are Claude Code in a live demo. Reply with exactly one short line starting with "Claude:".
Do not use tools. Stay concise. Use only the evidence provided in the user prompt.
Assume the repo exists at ./demo_codebase and the excerpt is authoritative.
Do not ask for files or links; answer directly using the prompt.
Output exactly one line, no extra lines, no questions.
EOF
)

HIST_SESSION="$(cat /proc/sys/kernel/random/uuid)"
MEM_SESSION="$(cat /proc/sys/kernel/random/uuid)"

printf "HIST_SESSION=%s\nMEM_SESSION=%s\n" "$HIST_SESSION" "$MEM_SESSION" > live_session_ids.txt

run_turn() {
  local session="$1"
  local user_prompt="$2"
  local out_file="$3"
  local mode="$4"
  local response=""

  if [[ "$mode" == "new" ]]; then
    response="$(cd "$CODEBASE_DIR" && WEAVE_PROJECT="$WEAVE_PROJECT" claude -p --model haiku --dangerously-skip-permissions \
      --session-id "$session" --system-prompt "$SYSTEM_LIVE" "$user_prompt")"
  else
    response="$(cd "$CODEBASE_DIR" && WEAVE_PROJECT="$WEAVE_PROJECT" claude -p --model haiku --dangerously-skip-permissions \
      --resume "$session" --system-prompt "$SYSTEM_LIVE" "$user_prompt")"
  fi

  response="$(printf "%s" "$response" | tr '\n' ' ' | tr -s ' ')"
  if [[ "$response" != Claude:* ]]; then
    response="Claude: $response"
  fi

  printf "User: %s\n%s\n\n" "$user_prompt" "$response" >> "$out_file"
}

run_discussion() {
  local session="$1"
  local out_file="$2"
  shift 2
  local first=1
  : > "$out_file"
  for prompt in "$@"; do
    if [[ "$first" -eq 1 ]]; then
      run_turn "$session" "$prompt" "$out_file" "new"
      first=0
    else
      run_turn "$session" "$prompt" "$out_file" "resume"
    fi
  done
}

ARTIFACT_EXCERPT="$(tr '\n' ' ' < "$CODEBASE_DIR/logs/pytest_artifact_excerpt.txt")"

DISCUSSION_1=(
  "CI red; test_event_dedupe_idempotent fails. Repo: event_pipeline/dedupe/v2.py, event_pipeline/dedupe/legacy.py, tests/test_dedupe.py. Artifact excerpt: $ARTIFACT_EXCERPT. Note: entrypoint falls back to legacy when v2 throws; v2 throws if pricing_context is None; legacy returns events unchanged."
  "Which handler ran, based on the excerpt?"
  "We prefer not to edit legacy; keep v2 path. Why didn't v2 run?"
  "What's the minimal fix to avoid fallback?"
  "Summarize fix + lesson in one line."
)

run_discussion "$HIST_SESSION" live_discussion1.md "${DISCUSSION_1[@]}"

# Build a memory artifact + KER using the prompts and sample artifact
PYTHONPATH="$ROOT_DIR/agent-memory-server:$ROOT_DIR/agent-memory-server/agent-memory-client" python - <<'PY'
import json
from pathlib import Path
from datetime import datetime, timezone
from agent_memory_server.wbtt import dual_channel, memory_store

root = Path(__file__).resolve().parent.parent
prompts_dir = root / "agent-memory-server" / "tests" / "fixtures" / "wbtt" / "prompts"
artifact_path = root / "agent-memory-server" / "tests" / "fixtures" / "wbtt" / "pytest_artifact_sample.txt"

distill_prompt = prompts_dir / "memory_distillation_prompt.txt"
ker_prompt = prompts_dir / "ker_prompt.txt"

artifact_text = artifact_path.read_text()
result = dual_channel.run_dual_channel(
    trace_id="live-demo-trace",
    artifact_text=artifact_text,
    distillation_prompt=distill_prompt.read_text(),
    ker_prompt=ker_prompt.read_text(),
)

artifact = result["memevolve_artifact"]
ker_output = result["ker_output"]

ker_dir = root / "ker"
ker_dir.mkdir(exist_ok=True)
ker_name = f"{datetime.now(timezone.utc).date().strftime('%Y%m%d')}-live-demo.md"
ker_path = ker_dir / ker_name
ker_path.write_text(ker_output)

payload = {
    "memories": [
        {
            "id": f"wbtt-live-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "text": memory_store._artifact_to_text(artifact),
            "user_id": "wbtt-demo",
            "namespace": "wbtt",
            "topics": artifact.get("tags", []),
        }
    ]
}

out_dir = root / "demo_claude"
payload_path = out_dir / "memory_payload.json"
payload_path.write_text(json.dumps(payload))
print(str(payload_path))
PY

# Store in Redis via agent-memory-server API
create_response="$(curl -s "$API_BASE/v1/long-term-memory/" \
  -H "Content-Type: application/json" \
  -d @"$DEMO_DIR/memory_payload.json")"

if [[ "$create_response" == "Internal Server Error" ]]; then
  echo "Memory creation failed. Ensure agent-memory-server was started with:"
  echo "  set -x WBTT_DEMO_EMBEDDINGS 1"
  echo "then restart: uv run agent-memory api"
fi

# Fetch back to prove it is in Redis
redis_search_response="$(curl -s "$API_BASE/v1/long-term-memory/search" \
  -H "Content-Type: application/json" \
  -d '{"text":"","user_id":{"eq":"wbtt-demo"},"namespace":{"eq":"wbtt"},"limit":3}')"
printf "%s" "$redis_search_response" > "$DEMO_DIR/redis_search.json"

if [[ "$redis_search_response" == "Internal Server Error" ]]; then
  echo "Redis search failed. Ensure agent-memory-server was started with:"
  echo "  set -x WBTT_DEMO_EMBEDDINGS 1"
  echo "then restart: uv run agent-memory api"
fi

# Memory prompt (what would be injected)
memory_prompt_response="$(curl -s "$API_BASE/v1/memory/prompt" \
  -H "Content-Type: application/json" \
  -d '{"query":"Dedupe failure caused by legacy fallback","long_term_search":{"text":"Dedupe failure caused by legacy fallback","user_id":{"eq":"wbtt-demo"},"namespace":{"eq":"wbtt"},"limit":3}}')"
printf "%s" "$memory_prompt_response" > "$DEMO_DIR/memory_prompt.json"

SYSTEM_MEM="$(python - <<'PY'
import json
data = json.load(open("memory_prompt.json"))
messages = data.get("messages", [])
system_msgs = [m for m in messages if m.get("role") == "system"]
if system_msgs:
    content = system_msgs[0].get("content", {})
    text = content.get("text", "")
    print(text.strip())
else:
    print("")
PY
)"

SYSTEM_MEM="$SYSTEM_LIVE\n\n$SYSTEM_MEM"

DISCUSSION_2=(
  "CI red again; same test. Repo: event_pipeline/dedupe/v2.py, event_pipeline/dedupe/legacy.py. Artifact excerpt: $ARTIFACT_EXCERPT"
)

: > live_discussion2.md
response="$(cd "$CODEBASE_DIR" && WEAVE_PROJECT="$WEAVE_PROJECT" claude -p --model haiku --dangerously-skip-permissions \
  --session-id "$MEM_SESSION" --system-prompt "$SYSTEM_MEM" "${DISCUSSION_2[0]}")"
response="$(printf "%s" "$response" | tr '\n' ' ' | tr -s ' ')"
if [[ "$response" != Claude:* ]]; then
  response="Claude: $response"
fi
printf "User: %s\n%s\n\n" "${DISCUSSION_2[0]}" "$response" >> live_discussion2.md

cat > "$DEMO_DIR/live_output.md" <<EOF
# WBTT Live Demo Output

## Discussion 1 (historical, live run)

$(cat live_discussion1.md)

## Discussion 2 (with memory injection)

$(cat live_discussion2.md)

## Redis: memory search (proof)

$(cat redis_search.json)

## Redis: memory_prompt (injection block)

$(cat memory_prompt.json)
EOF

echo "Wrote: $DEMO_DIR/live_output.md"
echo "Sessions: $DEMO_DIR/live_session_ids.txt"
