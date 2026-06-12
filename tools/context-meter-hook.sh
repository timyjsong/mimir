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

# Fallback: derive the project dir from cwd if transcript_path was absent/unusable.
if [ -z "$line" ]; then
  cwd="$(field cwd)"
  dir="$HOME/.claude/projects/$(printf '%s' "$cwd" | sed 's#/#-#g')"
  if [ -n "$cwd" ] && [ -d "$dir" ]; then
    line="$(python3 "$METER" --session-dir "$dir" 2>/dev/null)" || line=""
  fi
fi

[ -n "$line" ] || exit 0
python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"context-meter: "+sys.argv[1]}}))' "$line"
