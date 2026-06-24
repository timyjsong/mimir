#!/usr/bin/env python3
# PreToolUse hook (matcher Write|Edit) — the PROFILE BUDGET (housekeeping for USER.md).
#
# Mimir's cross-project user model lives at ~/.claude/mimir/USER.md and is read when orienting.
# Like any always-considered doc it must stay LEAN — an unbounded profile buries its own
# load-bearing entries (the exact bloat problem the audit found). This hook hard-stops a write
# that would GROW USER.md past its cap, with a reason telling Mimir to consolidate first. So the
# profile self-curates on every write instead of accreting forever.
#
# Policy: deny ONLY growth-past-cap. A shrinking or same-size edit is ALWAYS allowed, so
# consolidation is never blocked even when already over. Mirror of memory-budget-hook.py.
# FAIL-OPEN: any uncertainty/error -> allow. Eval-guarded by MIMIR_NO_GUARD / MIMIR_NO_METER.
#
# Caps tunable: MIMIR_PROFILE_HARDCAP (bytes, default 6500 ~= 1.6K tokens),
# MIMIR_PROFILE_HARDLINES (default 120). Lean, but not as tight as the 600-tok resident docs.
import json, os, sys


def allow():
    sys.exit(0)


try:
    if os.environ.get("MIMIR_NO_GUARD") or os.environ.get("MIMIR_NO_METER"):
        allow()
    data = json.load(sys.stdin)
    ti = (data.get("tool_input") or {})
    path = ti.get("file_path") or ti.get("path") or ""
    norm = path.replace("\\", "/")
    # Only police the user profile (USER.md inside a .../mimir/ dir).
    if os.path.basename(norm) != "USER.md" or "/mimir/" not in norm:
        allow()

    try:
        cur_bytes = os.path.getsize(path)
        with open(path, "rb") as f:
            cur_lines = f.read().count(b"\n")
    except OSError:
        cur_bytes, cur_lines = 0, 0

    def blen(s):
        return len((s or "").encode("utf-8"))

    def nlines(s):
        return (s or "").count("\n")

    tool = data.get("tool_name", "")
    if tool == "Write":
        new_bytes = blen(ti.get("content", ""))
        new_lines = nlines(ti.get("content", ""))
    elif tool == "Edit":
        if ti.get("replace_all"):
            allow()  # can't size a replace_all confidently -> fail open
        new_bytes = cur_bytes - blen(ti.get("old_string", "")) + blen(ti.get("new_string", ""))
        new_lines = cur_lines - nlines(ti.get("old_string", "")) + nlines(ti.get("new_string", ""))
    else:
        allow()  # MultiEdit / other -> fail open

    HARD_BYTES = int(os.environ.get("MIMIR_PROFILE_HARDCAP", "6500"))
    HARD_LINES = int(os.environ.get("MIMIR_PROFILE_HARDLINES", "120"))
    grew_b = new_bytes > cur_bytes and new_bytes > HARD_BYTES
    grew_l = new_lines > cur_lines and new_lines > HARD_LINES
    if grew_b or grew_l:
        over = []
        if grew_b:
            over.append("%.1fK > %.1fK" % (new_bytes / 1024.0, HARD_BYTES / 1024.0))
        if grew_l:
            over.append("%d > %d lines" % (new_lines, HARD_LINES))
        reason = (
            "This write would grow USER.md to " + " and ".join(over) + ", past its lean cap. "
            "The profile must stay absorbable. Consolidate FIRST: merge duplicate traits, drop the "
            "lowest-evidence / least load-bearing entries, and move anything superseded to "
            "USER.archive.md (never delete). Then retry with the tightened profile."
        )
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))
        sys.exit(0)
    allow()
except Exception:
    allow()  # fail-open: a malfunctioning guard must never block a write
