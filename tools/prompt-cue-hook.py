#!/usr/bin/env python3
# UserPromptSubmit hook — the PROMPT CUE (guard #2).
#
# Reads the user's prompt and injects a SHORT advisory cue (additionalContext) only for
# high-precision, outward-cued cases — the dispositions whose trigger genuinely lives in
# the user's words and where a miss is cheap:
#   - state/orientation question  -> derive-from-disk reminder
#   - small scoped ask            -> don't-over-process reminder
#   - user names an irreversible op -> gate-awareness reminder (complements the tool-boundary gate)
# Deliberately NOT hold-your-ground / reframe: those fire on the model's own output, have no
# reliable prompt signature, and a silent miss IS the painpoint — they stay resident.
#
# FAIL-SILENT: any error -> exit 0, no output (never blocks or perturbs a turn).
# Eval-guarded by MIMIR_NO_GUARD / MIMIR_NO_METER.
import json, os, re, sys


def nothing():
    sys.exit(0)


def main():
    if os.environ.get("MIMIR_NO_GUARD") or os.environ.get("MIMIR_NO_METER"):
        nothing()
    data = json.load(sys.stdin)
    # CC's UserPromptSubmit stdin key is documented as user_prompt, but read both so a key
    # mismatch can't silently make this a no-op.
    prompt = (data.get("prompt") or data.get("user_prompt") or "").strip()
    if not prompt:
        nothing()
    low = prompt.lower()
    cards = []

    derive = re.search(
        r"\b(what(?:'?s| is| are) the (state|status)|where are we|where did we leave off|catch (me )?up|"
        r"get caught up|bring me up to speed|orient( me)?|status update)\b", low)
    if derive:
        cards.append("[cue] State/orientation question — reconstruct from disk + git first; "
                     "don't answer from memory, and verify load-bearing facts before asserting.")

    # Standalone-scary verbs, OR a delete/remove/wipe/drop aimed at a WEIGHTY object. The weighty
    # gate keeps ordinary code edits ("delete this line", "remove the unused import") from firing.
    scary = re.search(
        r"\b(rm\s+-[a-z]*r[a-z]*|force[- ]push|reset\s+--hard|nuke|purge|tear down|"
        r"destroy|deploy(\s+to)?\s+prod)\b", low)
    weighty = re.search(
        r"\b(delete|remove|wipe|drop|clear)\b[^\n]{0,24}\b(database|table|schema|branch|"
        r"prod|production|repo|repositor|director|folder|everything|server|deployment|"
        r"volume|bucket|namespace|cluster|migration)\b", low)
    destructive = scary or weighty
    if destructive:
        cards.append("[cue] You're being asked to do something irreversible / outward-facing — "
                     "confirm the target and that it's recoverable; gate unless the user has engaged "
                     "the cost. (The tool-boundary gate also catches the command itself.)")

    # Scale cue fires ONLY when not already a state-question or a destructive ask (avoid telling
    # the model to 'just do it' on something that needs care).
    wc = len(prompt.split())
    complex_marker = re.search(
        r"\b(plan|design|architect|should we|options|trade-?off|compare|why|analyz|strateg|"
        r"refactor|investigate|debug|root cause|figure out)\b", low)
    if not derive and not destructive and wc <= 7 and "?" not in prompt and not complex_marker:
        cards.append("[cue] Small, scoped ask — match effort to it; don't over-process or over-gate "
                     "a simple request. Lead with the result.")

    if not cards:
        nothing()
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "\n".join(cards),
    }}))


try:
    main()
except Exception:
    nothing()  # fail-silent: never block or perturb a turn
