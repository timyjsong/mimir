#!/usr/bin/env python3
# PreToolUse hook (matcher Write|Edit): HARD-STOP on MEMORY.md growth past CC's
# silent ~25K / 200-line load cliff (verified: code.claude.com/docs/en/memory —
# "first 200 lines or first 25KB, whichever comes first; content beyond is not
# loaded", silently). Denies a Write/Edit whose RESULT would GROW MEMORY.md past
# the cap, with a reason surfaced to the model so it consolidates and retries.
#
# Policy: deny ONLY growth-past-cap. A shrinking or same-size edit is ALWAYS
# allowed, so consolidation itself is never blocked even when the file is already
# over (the index is at ~24.7K today). FAIL-OPEN: any uncertainty/parse error ->
# allow (never lose a memory write). Eval-guarded by MIMIR_NO_METER.
#
# Caps tunable: MIMIR_MEMORY_HARDCAP (bytes, default 24500), MIMIR_MEMORY_HARDLINES
# (default 195) — both a hair under the real 25K/200 cliff. The soft gauge in
# context-meter-hook.sh warns earlier (20K/180); this is the wall.
import json, os, sys


def allow():
    sys.exit(0)  # no stdout = allow (normal permission flow)


try:
    if os.environ.get("MIMIR_NO_METER"):
        allow()
    data = json.load(sys.stdin)
    ti = (data.get("tool_input") or {})
    path = ti.get("file_path") or ti.get("path") or ""
    norm = path.replace("\\", "/")
    # Only police the auto-memory INDEX (MEMORY.md inside a .../memory/ dir).
    if os.path.basename(norm) != "MEMORY.md" or "/memory/" not in norm:
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

    HARD_BYTES = int(os.environ.get("MIMIR_MEMORY_HARDCAP", "24500"))
    HARD_LINES = int(os.environ.get("MIMIR_MEMORY_HARDLINES", "195"))
    # Deny ONLY if the write GROWS the file AND lands over a cap. Shrink/same -> allow.
    grew_b = new_bytes > cur_bytes and new_bytes > HARD_BYTES
    grew_l = new_lines > cur_lines and new_lines > HARD_LINES
    if grew_b or grew_l:
        over = []
        if grew_b:
            over.append("%.1fK > %.0fK" % (new_bytes / 1024.0, HARD_BYTES / 1024.0))
        if grew_l:
            over.append("%d > %d lines" % (new_lines, HARD_LINES))
        reason = (
            "This write would grow MEMORY.md to " + " and ".join(over) + ", past CC's silent "
            "~25K/200-line load cliff (content beyond it is dropped at session start, with no "
            "warning). Consolidate FIRST: remove settled entries' index lines (the topic file "
            "stays on disk and is grep-findable) or move them to .archive/, keeping the index "
            "live-only plus a small pinned standing-records section. Then retry the add."
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
