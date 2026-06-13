#!/usr/bin/env python3
"""context-meter — empirical context usage + window size for a Claude Code session.

No hardcoded window, no statusline plumbing. Everything comes from the session transcript
(+ ~/.claude.json as a fallback):

  USAGE  = the last assistant `usage` block (input + cache_creation + cache_read).
           Verified 2026-06-11 to match `/context` to within a hair.

  WINDOW = resolved in three tiers (first that fires wins), then a physical backstop:
    1. The LAST `/model` "Set model to <id>" line — read ONLY from real command-stdout
       entries (`<local-command-stdout>`), never from message prose. Two real formats are
       handled (see parse_set_model): the raw id (`...claude-opus-4-8[1m]</...>`) and the
       friendly ANSI-wrapped label (`...\x1b[1mOpus 4.8 (1M context)\x1b[22m and saved...`).
       Switch-aware; carries the [1m] / "1M context" marker that per-message `message.model`
       drops.
    2. Else: cross-ref ~/.claude.json projects[<cwd>].lastModelUsage — if a `<base>[1m]`
       variant of the current base model was used in this project, assume [1m]. Catches
       bare-launch sessions that never /model-switched.
    3. Else: the base model's default window (~200k), LABELED as a lookup.

  BACKSTOP (all tiers): a request's context physically cannot exceed its window, so if
  `used > 200k` the window MUST be the 1M variant — we infer it and tag the source
  `...+used>200k`. This corrects an under-detected window (the old 169.8% artifact) rather
  than cosmetically clamping it.

  Suffix `[1m]` / label "1M context" => 1,000,000; every base id => 200,000 (the only
  distinction that exists in practice for current Claude models). The genuinely ambiguous
  case — a project that used BOTH opus-200k and opus[1m] with no /model this session and
  used <= 200k — is labeled (`[src:lookup?]`), not guessed.

Usage:  context-meter.py <transcript.jsonl>
        context-meter.py --session-dir <~/.claude/projects/<slug>>   # newest transcript

Pure detection logic (strip_ansi / parse_set_model / window_for_model / resolve) is unit-
tested in test_context_meter.py — run `python3 tools/test_context_meter.py`.
"""
import json, sys, os, glob, re

WIN_1M, WIN_BASE = 1_000_000, 200_000
BURN_WINDOW = 5   # turns to average burn over; last turn alone is noisy (66K->3K). Tunable.

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


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(s):
    return ANSI_RE.sub("", s)


SYSREMINDER_RE = re.compile(r"^(?:\s*<system-reminder>.*?</system-reminder>)+\s*", re.DOTALL)


def strip_system_reminders(s):
    """Drop leading <system-reminder>...</system-reminder> wrapper(s) so the genuine prompt
    underneath is visible. The harness prefixes real prompts with a 'Message sent at ...'
    reminder; without stripping it, the prompt-boundary check mistakes the prompt for
    non-prompt '<'-wrapped content and silently drops the turn."""
    return SYSREMINDER_RE.sub("", s).lstrip()


def parse_set_model(content):
    """Extract the current model id/label from a /model command-stdout content block.

    Returns the cleaned model string (last switch wins = current), or None. Only trusts
    real `<local-command-stdout>` blocks, never message prose. Handles both observed
    formats:
      raw id      -> "Set model to claude-opus-4-8[1m]</local-command-stdout>"
      friendly    -> "Set model to \\x1b[1mOpus 4.8 (1M context)\\x1b[22m and saved as ..."

    A real switch is a message whose content STARTS WITH `<local-command-stdout>` (the whole
    content is the command block). Requiring `startswith` — not just "contains" — rejects
    prose/code/tool-output that merely quotes the phrase (e.g. a session about this tool,
    where the literal text "\\x1b[1m" appears un-stripped because it isn't a real ESC byte).
    """
    if not content.lstrip().startswith("<local-command-stdout>"):
        return None
    text = strip_ansi(content)
    model = None
    # Non-greedy capture bounded by the first terminator (closing tag, the trailing
    # "and saved..." prose, or newline/end) so each switch is matched separately and the
    # LAST one wins. Then drop a trailing "(default)" note.
    for mm in re.finditer(r"Set model to\s+(.+?)(?=</|\band saved\b|[\r\n]|$)", text):
        rest = re.sub(r"\s*\(default\)\s*$", "", mm.group(1).strip()).strip()
        if rest and not rest.startswith("<"):   # skip the "<id>" prose placeholder
            model = rest
    return model


def window_for_model(model_str):
    """200k vs 1M from a model id/label. `[1m]` suffix or '1M context' label => 1M."""
    low = (model_str or "").lower()
    return WIN_1M if ("[1m]" in low or "1m context" in low) else WIN_BASE


def resolve(used, set_model, msg_model, lmu_1m):
    """Pure window resolution. Returns (window, src, current_model_str).

    lmu_1m is the precomputed tier-2 result (True / False / None) so this stays pure and
    unit-testable. The used>200k backstop is applied last and overrides any 200k call.
    """
    if set_model is not None:                                    # tier 1
        return _backstop(used, window_for_model(set_model), "model-log", set_model)
    base = (msg_model or "").replace("[1m]", "")
    if lmu_1m is True:                                           # tier 2
        return _backstop(used, WIN_1M, "lastModelUsage", base + "[1m]")
    if lmu_1m is None:                                           # tier 3 (ambiguous/unknown)
        return _backstop(used, WIN_BASE, "lookup?", msg_model)
    return _backstop(used, WIN_BASE, "base-default", msg_model)


def _backstop(used, window, src, current):
    # A context cannot exceed its window; >200k used => the window is the 1M variant.
    if window == WIN_BASE and used > WIN_BASE:
        window, src = WIN_1M, src + "+used>200k"
    return window, src, current


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
    usage = msg_model = set_model = cwd = None
    cur_total = 0
    boundaries = []   # context-token total at each genuine user-prompt (turn) boundary
    with open(transcript) as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            cwd = o.get("cwd") or cwd
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
            c = m.get("content", "")
            if isinstance(c, list):
                c = " ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in c)
            if isinstance(c, str):
                pm = parse_set_model(c)
                if pm:
                    set_model = pm   # last wins = current
    return usage, boundaries, msg_model, set_model, cwd


def project_used_1m(cwd, base):
    """Tier 2: did this project ever use the [1m] variant of `base`? (ambiguity-aware)"""
    if not cwd or not base:
        return None
    try:
        d = json.load(open(os.path.expanduser("~/.claude.json")))
    except Exception:
        return None
    lmu = (d.get("projects", {}).get(cwd, {}) or {}).get("lastModelUsage", {}) or {}
    keys = list(lmu.keys())
    has_1m = (base + "[1m]") in keys
    has_base = base in keys
    if has_1m and not has_base:
        return True            # unambiguous: only the 1M variant used here
    if has_1m and has_base:
        return None            # ambiguous: both used, no /model this session -> can't tell
    return False if has_base else None


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

    usage, boundaries, msg_model, set_model, cwd = read(transcript)
    if not usage:
        print("no usage block found", file=sys.stderr); sys.exit(1)
    used = tokens(usage)
    last_burn, avg_burn = burn_stats(boundaries, BURN_WINDOW)

    base = (msg_model or "").replace("[1m]", "")
    lmu_1m = None if set_model is not None else project_used_1m(cwd, base)
    window, src, current = resolve(used, set_model, msg_model, lmu_1m)

    pct = used / window * 100
    disp = (current or "?").replace("[1m]", "").removeprefix("claude-")
    if last_burn is None:
        burn_str = ""
    else:
        sgn = lambda x: f"{'+' if x >= 0 else '-'}{fmt(abs(x))}"
        burn_str = f"  burn {sgn(last_burn)}"                      # line-1 fact: the last turn's actual burn
        if min(BURN_WINDOW, len(boundaries) - 1) >= 2:            # >1 turn averaged -> emit the smoothed rate
            burn_str += f"  avg ~{sgn(round(avg_burn))}/turn"     # projection basis for the cost: line
    measured = src.split("+")[0] in ("model-log", "lastModelUsage") or "used>200k" in src
    note = "" if measured else f"  (window={src} — not measured)"
    print(f"{fmt(used)} / {fmt(window)} ({pct:.1f}%)  model={disp}{burn_str}  [src:{src}]{note}")


if __name__ == "__main__":
    main()
