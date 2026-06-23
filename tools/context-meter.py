#!/usr/bin/env python3
"""context-meter — empirical context usage + window size for a Claude Code session.

USAGE  = the last assistant `usage` block (input + cache_creation + cache_read), summed off the
         session transcript. Verified to match `/context` to within a hair. Burn rate is the
         per-turn delta across genuine user-prompt boundaries.

WINDOW = read AUTHORITATIVELY from the statusLine sensor (tools/context-meter-statusline.sh).
         The harness hands a statusLine command the real `context_window.context_window_size`
         (200000 or 1000000) on every status render; the sensor caches it per session to
         <CACHE_DIR>/mimir-meter-<session_id>.json. This meter reads that cache by session id
         (= the transcript's basename). The window is constant per session, so one render is
         enough; a /model switch re-renders and refreshes the cache.

         Why the sensor at all: the harness STRIPS the `[1m]` marker before it reaches the
         transcript (`message.model` is always the bare id) and records no current-model field
         in ~/.claude.json. The statusLine payload is therefore the ONLY authoritative window
         signal — so we read it directly instead of inferring the window from indirect history
         (the old three-tier scheme defaulted to 200K whenever inference came up empty, which
         was the common case and the 200K-on-a-1M-session bug).

         Fallback (cache absent — only the cold-start micro-window before the first status
         render): the configured default window, tagged `— not measured`. A physical backstop
         bumps to 1M if usage exceeds the resolved window.

Usage:  context-meter.py <transcript.jsonl>
        context-meter.py --session-dir <~/.claude/projects/<slug>>   # newest transcript

Pure logic (cached_window / resolve_window / parse_window / burn_stats / thresholds) is unit-
tested in test_context_meter.py — run `python3 tools/test_context_meter.py`.
"""
import json, sys, os, glob, re

WIN_1M, WIN_BASE = 1_000_000, 200_000
BURN_WINDOW = 5   # turns to average burn over; last turn alone is noisy (66K->3K). Tunable.

# Where the statusLine sensor writes per-session window caches (mimir-meter-<sid>.json). The
# sensor and this reader both honor MIMIR_METER_CACHE_DIR; default /tmp — session-scoped and
# self-pruning (a session never outlives a reboot, so stale files can't accumulate).
CACHE_DIR = os.environ.get("MIMIR_METER_CACHE_DIR", "/tmp")


def parse_window(spec, fallback=WIN_1M):
    """Window size from a config string: '1M'->1_000_000, '200K'->200_000, '1000000'->1_000_000.
    Garbage / empty -> fallback (1M)."""
    s = (spec or "").strip().lower()
    try:
        if s.endswith("k"):
            return int(float(s[:-1]) * 1_000)
        if s.endswith("m"):
            return int(float(s[:-1]) * 1_000_000)
        return int(s)
    except ValueError:
        return fallback


# Default window when the authoritative cache isn't present yet (cold start, before the first
# status render). 1M because the harness strips the [1m] marker — absence of evidence is the
# norm, not evidence of 200K — and bare-launch sessions here run 1M. Tunable via
# MIMIR_DEFAULT_WINDOW (e.g. "200K") with NO code edit.
DEFAULT_WINDOW = parse_window(os.environ.get("MIMIR_DEFAULT_WINDOW", "1M"))

# Decision-zone threshold: the context level at/above which the footer's clear/hand-off `rec:`
# goes live. Set as a percentage ("50%") or an absolute token count ("200K"/"200000"/"1M").
# Tunable HERE or via env with NO brain edit / eval — the brain keys off the emitted `zone=`
# signal + `thr=` value, not a number baked into its prose. See project-status-footer-spec.
SURFACE_THRESHOLD = os.environ.get("MIMIR_CONTEXT_THRESHOLD", "40%")


def fmt(n):
    """Human K/M token count: 402014 -> '402K', 1_000_000 -> '1M', 1_400_000 -> '1.4M'."""
    n = int(n)
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".") + "M"
    return f"{round(n / 1000)}K"


def tokens(u):
    """Total context tokens in a usage block (input + cache_creation + cache_read)."""
    u = u or {}
    return u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)


SYSREMINDER_RE = re.compile(r"^(?:\s*<system-reminder>.*?</system-reminder>)+\s*", re.DOTALL)


def strip_system_reminders(s):
    """Drop leading <system-reminder>...</system-reminder> wrapper(s) so the genuine prompt
    underneath is visible. The harness prefixes real prompts with a 'Message sent at ...'
    reminder; without stripping it, the prompt-boundary check mistakes the prompt for
    non-prompt '<'-wrapped content and silently drops the turn."""
    return SYSREMINDER_RE.sub("", s).lstrip()


def session_id_from_transcript(transcript):
    """The session id is the transcript filename without its .jsonl suffix."""
    b = os.path.basename(transcript or "")
    return b[:-6] if b.endswith(".jsonl") else b


def cached_window(transcript):
    """Authoritative context-window size the statusLine sensor cached for THIS session
    (keyed by session id = transcript basename). Returns the int token size, or None if the
    cache is absent/unreadable (cold start before the first status render)."""
    try:
        path = os.path.join(CACHE_DIR, f"mimir-meter-{session_id_from_transcript(transcript)}.json")
        with open(path) as f:
            w = json.load(f).get("context_window_size")
        return int(w) if w else None
    except Exception:
        return None


def resolve_window(used, cached, default):
    """Resolve the window. The authoritative cache wins; else the configured default (tagged
    not-measured). A physical backstop bumps to 1M if usage somehow exceeds the resolved
    window — a safety net for the default path; it cannot fire against the authoritative cache.
    Returns (window, src)."""
    if cached:
        window, src = cached, "statusline"
    else:
        window, src = default, "default"
    if used > window:
        window, src = WIN_1M, src + "+used>" + fmt(window)
    return window, src


def is_user_prompt(o):
    """A genuine typed user prompt (a turn boundary) — NOT a tool result or command-stdout."""
    if o.get("type") != "user" or o.get("toolUseResult") is not None:
        return False
    m = o.get("message", {}) or {}
    if m.get("role") != "user":
        return False
    c = m.get("content", "")
    if isinstance(c, list):
        return not any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c)
    if isinstance(c, str):
        c = strip_system_reminders(c)            # a genuine prompt may be wrapped in a leading reminder
        return bool(c) and not c.startswith("<")  # else <local-command-stdout> etc. (empty == reminder-only)
    return False


def read(transcript):
    """Parse the transcript for the last usage block, the turn boundaries (for burn), and the
    last seen message.model (bare id, for display). The window is NOT derived here — it comes
    from the statusLine sensor cache (see cached_window)."""
    usage = msg_model = None
    cur_total = 0
    boundaries = []   # context-token total at each genuine user-prompt (turn) boundary
    with open(transcript) as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            if is_user_prompt(o):
                boundaries.append(cur_total)   # = end-of-previous-turn total
            m = o.get("message", {}) or {}
            if m.get("model") == "<synthetic>":
                continue   # interrupt/placeholder entry — no real usage or model; would zero the meter
            u = m.get("usage") or o.get("usage")
            if isinstance(u, dict) and u.get("input_tokens") is not None:
                usage = u
                cur_total = tokens(u)
            if m.get("model"):
                msg_model = m["model"]
    return usage, boundaries, msg_model


def parse_threshold(spec):
    """Parse a surface-threshold config into (kind, value).

    '50%' -> ('pct', 50.0)   compared against the reading's percentage
    '200K'/'200000'/'1M' -> ('abs', tokens)   compared against absolute used
    Garbage / empty -> ('pct', 50.0) (the safe default). Tunable knob — see SURFACE_THRESHOLD.
    """
    s = (spec or "").strip().lower()
    try:
        if s.endswith("%"):
            return ("pct", float(s[:-1]))
        if s.endswith("k"):
            return ("abs", int(float(s[:-1]) * 1_000))
        if s.endswith("m"):
            return ("abs", int(float(s[:-1]) * 1_000_000))
        return ("abs", int(s))
    except ValueError:
        return ("pct", 50.0)


def in_surface_zone(used, window, spec):
    """True if the reading is at/over the surface threshold (the decision zone where `rec:` lives)."""
    kind, val = parse_threshold(spec)
    return (used / window * 100) >= val if kind == "pct" else used >= val


def burn_stats(boundaries, window):
    """Per-turn context growth from the prompt boundaries: (last_turn_delta, rolling_avg).

    rolling_avg = mean of the last `window` completed turns' deltas (telescoped:
    (boundaries[-1] - boundaries[-1-k]) / k, where k = turns actually available). The
    average is the planning-grade rate; the last delta alone is too noisy to estimate on.
    Returns (None, None) with < 2 boundaries — no completed turn yet.
    """
    if len(boundaries) < 2:
        return None, None
    last = boundaries[-1] - boundaries[-2]
    k = min(window, len(boundaries) - 1)
    avg = (boundaries[-1] - boundaries[-1 - k]) / k
    return last, avg


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: context-meter.py <transcript.jsonl> | --session-dir <dir>", file=sys.stderr)
        sys.exit(2)
    if args[0] == "--session-dir":
        cands = sorted(glob.glob(os.path.join(args[1], "*.jsonl")), key=os.path.getmtime)
        if not cands:
            print("no transcript found", file=sys.stderr); sys.exit(1)
        transcript = cands[-1]
    else:
        transcript = args[0]

    usage, boundaries, msg_model = read(transcript)
    if not usage:
        print("no usage block found", file=sys.stderr); sys.exit(1)
    used = tokens(usage)
    last_burn, avg_burn = burn_stats(boundaries, BURN_WINDOW)

    window, src = resolve_window(used, cached_window(transcript), DEFAULT_WINDOW)

    pct = used / window * 100
    disp = (msg_model or "?").replace("[1m]", "").removeprefix("claude-")
    if last_burn is None:
        burn_str = ""
    else:
        sgn = lambda x: f"{'+' if x >= 0 else '-'}{fmt(abs(x))}"
        burn_str = f"  burn {sgn(last_burn)}"                      # line-1 fact: the last turn's actual burn
        if min(BURN_WINDOW, len(boundaries) - 1) >= 2:            # >1 turn averaged -> emit the smoothed rate
            burn_str += f"  avg ~{sgn(round(avg_burn))}/turn"     # projection basis for the cost: line
    measured = src.split("+")[0] == "statusline" or "used>" in src
    note = "" if measured else f"  (window={src} — not measured)"
    zone = "surface" if in_surface_zone(used, window, SURFACE_THRESHOLD) else "quiet"
    print(f"{fmt(used)} / {fmt(window)} ({pct:.1f}%)  model={disp}{burn_str}  "
          f"zone={zone} thr={SURFACE_THRESHOLD}  [src:{src}]{note}")


if __name__ == "__main__":
    main()
