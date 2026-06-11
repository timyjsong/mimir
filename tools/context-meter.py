#!/usr/bin/env python3
"""context-meter — empirical context usage + window size for a Claude Code session.

No hardcoded window, no statusline plumbing. Everything comes from the session transcript
(+ ~/.claude.json as a fallback):

  USAGE  = the last assistant `usage` block (input + cache_creation + cache_read).
           Verified 2026-06-11 to match `/context` to within a hair.

  WINDOW = resolved in three tiers (first that fires wins):
    1. The LAST `/model` "Set model to <id>" line — read ONLY from real command-stdout
       entries (`<local-command-stdout>`), never from message prose (a 2026-06-11 test
       caught the regex matching the agent's own quoted text). This carries the [1m]
       variant that per-message `message.model` drops, and it's switch-aware (proven
       across 4 live switches incl. a variant-only opus->opus[1m] change).
    2. Else: cross-ref ~/.claude.json projects[<cwd>].lastModelUsage — if a `<base>[1m]`
       variant of the current base model was used in this project, assume [1m]. Catches
       bare-launch sessions that never /model-switched (where the suffix is nowhere in
       the transcript).
    3. Else: the base model's default window (~200k), LABELED as a lookup.

  Suffix `[1m]` => 1,000,000; every base id => 200,000 (the only distinction that exists
  in practice for current Claude models). The genuinely ambiguous case — a project that
  used BOTH opus-200k and opus[1m] with no /model this session — is labeled, not guessed.

Usage:  context-meter.py <transcript.jsonl>
        context-meter.py --session-dir <~/.claude/projects/<slug>>   # newest transcript
"""
import json, sys, os, glob, re

WIN_1M, WIN_BASE = 1_000_000, 200_000


def read(transcript):
    usage = msg_model = set_model = cwd = None
    with open(transcript) as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            cwd = o.get("cwd") or cwd
            m = o.get("message", {}) or {}
            u = m.get("usage") or o.get("usage")
            if isinstance(u, dict) and u.get("input_tokens") is not None:
                usage = u
            if m.get("model"):
                msg_model = m["model"]
            c = m.get("content", "")
            if isinstance(c, list):
                c = " ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in c)
            # ONLY trust "Set model to" inside a real /model command-stdout block,
            # never in ordinary message prose.
            if isinstance(c, str) and "local-command-stdout" in c:
                mm = re.search(r"Set model to ([^\s<]+)", c)
                if mm:
                    set_model = mm.group(1)  # last wins = current
    return usage, msg_model, set_model, cwd


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

    usage, msg_model, set_model, cwd = read(transcript)
    if not usage:
        print("no usage block found", file=sys.stderr); sys.exit(1)
    used = usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0) + usage.get("cache_read_input_tokens", 0)

    # tier 1: /model switch log (exact, has variant) ; else base id from message.model
    current = set_model or msg_model
    base = (set_model or msg_model or "").replace("[1m]", "")

    if set_model is not None:                         # tier 1
        window, src = (WIN_1M if set_model.endswith("[1m]") else WIN_BASE), "model-log"
    else:
        used1m = project_used_1m(cwd, base)           # tier 2
        if used1m is True:
            window, src, current = WIN_1M, "lastModelUsage", base + "[1m]"
        elif used1m is None:
            window, src = WIN_BASE, "lookup?"         # tier 3 (ambiguous / unknown)
        else:
            window, src = WIN_BASE, "base-default"

    pct = used / window * 100
    note = "" if src in ("model-log", "lastModelUsage") else f"  (window={src} — not measured)"
    print(f"{used:,} / {window:,} ({pct:.1f}%)  model={current or '?'}  [src:{src}]{note}")


if __name__ == "__main__":
    main()
