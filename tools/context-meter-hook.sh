#!/usr/bin/env bash
# UserPromptSubmit hook -> inject the live context-meter reading as additionalContext.
#
# Runs in EVERY session globally, so it is fail-silent by design: any failure exits 0
# with no output and can never block or perturb a turn. The reading is model-facing
# (additionalContext) — Mimir surfaces it in the status footer; it is not shown raw to
# the user.
#
# Wiring: ~/.claude/settings.json hooks.UserPromptSubmit -> command:
#   bash /home/tim/projects/mimir/tools/context-meter-hook.sh
set -uo pipefail

# Eval guard: the deployment-faithful probe harness sets MIMIR_NO_METER=1 so this
# injection never contaminates a `claude -p` eval run. Skip silently when set.
[ -n "${MIMIR_NO_METER:-}" ] && exit 0

METER="/home/tim/projects/mimir/tools/context-meter.py"
input="$(cat)"

field() { printf '%s' "$input" | python3 -c "import json,sys; print(json.load(sys.stdin).get('$1',''))" 2>/dev/null; }

line=""
transcript="$(field transcript_path)"
if [ -n "$transcript" ] && [ -f "$transcript" ]; then
  line="$(python3 "$METER" "$transcript" 2>/dev/null)" || line=""
fi

# Fallback (primary produced no reading): resolve ONLY the current session's own
# transcript, keyed by session id — NEVER newest-by-mtime. On a cold first turn the
# current transcript has no usage yet, and "newest in the project dir" then resolves
# to the PREVIOUS session, leaking its number (the 59.6%-on-a-fresh-session bug). The
# session id is the transcript's basename; take it from the hook's session_id field
# (if present), else from transcript_path itself. No match -> emit nothing.
if [ -z "$line" ]; then
  sid="$(field session_id)"
  [ -n "$sid" ] || { [ -n "$transcript" ] && sid="$(basename "$transcript" .jsonl)"; }
  cwd="$(field cwd)"
  dir="$HOME/.claude/projects/$(printf '%s' "$cwd" | sed 's#/#-#g')"
  if [ -n "$sid" ] && [ -f "$dir/$sid.jsonl" ]; then
    line="$(python3 "$METER" "$dir/$sid.jsonl" 2>/dev/null)" || line=""
  fi
fi

[ -n "$line" ] || exit 0
python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"context-meter: "+sys.argv[1]}}))' "$line"
