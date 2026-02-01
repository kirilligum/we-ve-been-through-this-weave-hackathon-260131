#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEMO_DIR="$ROOT_DIR/demo_claude"
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"

# Override if needed
WEAVE_PROJECT="${WEAVE_PROJECT:-kirill-igum-prls-co/we-ve-been-through-this-weave-hackathon-260131}"

SYSTEM_SCRIPT=$(cat <<'EOF'
You are producing a scripted demo. Reply with exactly one line starting with 'Claude:'.
Mapping:
- if user mentions 'CI is red again' -> 'Claude: I'll adjust the v2 dedupe key.'
- if user says 'Use the full W&B artifact' -> 'Claude: Log shows expected 1 got 2; still looks like v2.'
- if user asks 'What handler ran' -> 'Claude: It should be v2; I'll make v2 stricter.'
- if user says 'Still failing' -> 'Claude: Maybe we need more runtime context.'
- if user says 'Open the full pytest artifact' -> 'Claude: I didn't see anything else.'
- if user says 'Search for selected_pipeline' -> 'Claude: No matches; maybe I missed earlier lines.'
- if user says 'Start from the top' -> 'Claude: Found it now: selected_pipeline=legacy_fallback.'
- if user says 'So fix legacy path' -> 'Claude: Right; patch legacy to delegate to v2 and set DEDUPER=v2.'
- if user says 'Also address missing pricingContext' -> 'Claude: Entrypoint should derive pricingContext so v2 doesn't throw.'
- if user says 'Summarize fix' -> 'Claude: Fix: confirm selected_pipeline from full artifact, then make legacy delegate to v2 and derive pricingContext; lesson: verify executed path before editing.'
No extra words.
EOF
)

SYSTEM_MEM=$(cat <<'EOF'
You are producing a scripted demo. Reply with exactly one line starting with 'Claude:'.
Mapping:
- if user mentions 'fix quickly' or 'logs—fix quickly' -> 'Claude: Memory says check selected_pipeline in full artifact; it is legacy_fallback, so I derived pricingContext and made legacy delegate to v2; CI passes.'
No extra words.
EOF
)

HIST_SESSION="$(cat /proc/sys/kernel/random/uuid)"
MEM_SESSION="$(cat /proc/sys/kernel/random/uuid)"
NOMEM_SESSION="$(cat /proc/sys/kernel/random/uuid)"

printf "HIST_SESSION=%s\nMEM_SESSION=%s\nNOMEM_SESSION=%s\n" \
  "$HIST_SESSION" "$MEM_SESSION" "$NOMEM_SESSION" > session_ids.txt

run_turn() {
  local session="$1"
  local system_prompt="$2"
  local user_prompt="$3"
  local out_file="$4"
  local mode="$5"
  local response=""

  if [[ "$mode" == "new" ]]; then
    response="$(WEAVE_PROJECT="$WEAVE_PROJECT" claude -p --model haiku --dangerously-skip-permissions \
      --session-id "$session" --system-prompt "$system_prompt" "$user_prompt")"
  else
    response="$(WEAVE_PROJECT="$WEAVE_PROJECT" claude -p --model haiku --dangerously-skip-permissions \
      --resume "$session" --system-prompt "$system_prompt" "$user_prompt")"
  fi

  printf "User: %s\n%s\n\n" "$user_prompt" "$response" >> "$out_file"
}

run_discussion() {
  local session="$1"
  local system_prompt="$2"
  local out_file="$3"
  shift 3
  local first=1
  : > "$out_file"
  for prompt in "$@"; do
    if [[ "$first" -eq 1 ]]; then
      run_turn "$session" "$system_prompt" "$prompt" "$out_file" "new"
      first=0
    else
      run_turn "$session" "$system_prompt" "$prompt" "$out_file" "resume"
    fi
  done
}

DISCUSSION_1=(
  "CI is red again; test_event_dedupe_idempotent fails; run ci-19702 has logs."
  "Use the full W&B artifact; don't infer from partial output."
  "What handler ran in that run?"
  "Still failing; you're not changing what is executed."
  "Open the full pytest artifact; terminal output truncates."
  "Search for selected_pipeline or fallback."
  "Start from the top; pipeline is logged on startup."
  "So fix legacy path, not v2."
  "Also address missing pricingContext warning."
  "Summarize fix + lesson in one line."
)

DISCUSSION_2=(
  "CI is red again; test_event_dedupe_idempotent fails; run ci-19702 has logs—fix quickly."
)

DISCUSSION_3=(
  "CI is red again; test_event_dedupe_idempotent fails; run ci-19702 has logs."
  "Use the full W&B artifact; don't infer from partial output."
  "What handler ran in that run?"
  "Still failing; you're not changing what is executed."
  "Open the full pytest artifact; terminal output truncates."
  "Search for selected_pipeline or fallback."
  "Start from the top; pipeline is logged on startup."
  "So fix legacy path, not v2."
  "Also address missing pricingContext warning."
  "Summarize fix + lesson in one line."
)

run_discussion "$HIST_SESSION" "$SYSTEM_SCRIPT" discussion1.md "${DISCUSSION_1[@]}"
run_discussion "$MEM_SESSION" "$SYSTEM_MEM" discussion2.md "${DISCUSSION_2[@]}"
run_discussion "$NOMEM_SESSION" "$SYSTEM_SCRIPT" discussion3.md "${DISCUSSION_3[@]}"

cat > demo_output.md <<EOF
# WBTT Demo Output

## Discussion 1 (historical, 10 turns)

$(cat discussion1.md)

## Discussion 2 (memory on, 1 turn)

$(cat discussion2.md)

## Discussion 3 (memory off, 10 turns)

$(cat discussion3.md)
EOF

echo "Wrote: $DEMO_DIR/demo_output.md"
echo "Sessions: $DEMO_DIR/session_ids.txt"
