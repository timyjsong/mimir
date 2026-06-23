#!/usr/bin/env bash
# statusLine SENSOR — harvest the authoritative context-window size into a per-session cache.
#
# Claude Code hands a statusLine command a rich JSON payload on stdin that includes
# `context_window.context_window_size` (200000 or 1000000) and `session_id` — the ONLY
# authoritative window signal available locally (the harness strips the `[1m]` marker before
# it reaches the transcript or ~/.claude.json). The context-meter reads the window from this
# cache instead of inferring it. The window is constant per session, so any single render
# suffices; a /model switch re-renders and refreshes it.
#
# This is a pure SENSOR: it prints NOTHING to the status bar (Mimir's footer stays the visible
# surface). It runs on every status render in EVERY session globally, so it is cheap and
# strictly fail-silent — one short-lived python process, atomic write, never errors out.
#
# Wiring: ~/.claude/settings.json -> statusLine.command:
#   bash /home/tim/projects/mimir/tools/context-meter-statusline.sh
# Cache dir honors MIMIR_METER_CACHE_DIR (default /tmp); MUST match context-meter.py's CACHE_DIR.
set -uo pipefail

python3 -c '
import json, sys, os, tempfile
try:
    d = json.load(sys.stdin)
    sid = d.get("session_id") or ""
    cws = (d.get("context_window") or {}).get("context_window_size")
    if sid and cws:
        cache_dir = os.environ.get("MIMIR_METER_CACHE_DIR", "/tmp")
        path = os.path.join(cache_dir, "mimir-meter-%s.json" % sid)
        fd, tmp = tempfile.mkstemp(dir=cache_dir, prefix="mimir-meter-", suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump({"context_window_size": int(cws)}, f)
        os.replace(tmp, path)   # atomic — the reader never sees a half-written file
except Exception:
    pass
' 2>/dev/null

# Print nothing visible to the status bar.
printf ''
