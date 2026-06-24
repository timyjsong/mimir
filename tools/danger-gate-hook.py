#!/usr/bin/env python3
# PreToolUse hook (matcher Bash) — the ACTION GATE (guard #1).
#
# Externalizes the "gate-before-irreversible-actions" disposition: instead of hoping a
# resident rule fires, the rm/push/migrate token IS the trigger, matched deterministically
# out-of-band, so the gate fires even if the rule was never "remembered" in context.
#
# Policy: permissionDecision "ask" (surface a confirm to the user), NOT "deny" — a gate is
# a pause-and-confirm, not a refusal. Patterns are deliberately TIGHT (genuinely irreversible
# / high-blast-radius) so this can't become the over-gating painpoint. A miss is recoverable
# (CC's normal permission flow still applies); a false-positive only costs one confirm.
#
# False-positive control: quoted substrings are blanked before matching the shell-token
# patterns, so a keyword inside an echo/grep/comment string ('rm -rf', 'drop table') never
# fires. DB-destructive ops are matched on the FULL command but gated by a db-client name,
# because `psql -c 'drop database'` legitimately carries its SQL in quotes.
#
# FAIL-OPEN: any error -> allow(). A malfunctioning guard must never block a command.
# Eval-guarded by MIMIR_NO_GUARD (and the shared MIMIR_NO_METER).
import json, os, re, sys


def allow():
    sys.exit(0)  # no stdout = allow (normal permission flow)


def strip_quotes(s):
    s = re.sub(r"'[^']*'", "''", s)
    s = re.sub(r'"[^"]*"', '""', s)
    return s


def dangerous_rm(unq):
    # rm is dangerous when it carries BOTH recursive AND force (in any flag arrangement).
    for m in re.finditer(r"\brm\b([^\n;&|]*)", unq):
        args = m.group(1)
        has_r = bool(re.search(r"(?:^|\s)-[a-zA-Z]*r", args)) or "--recursive" in args
        has_f = bool(re.search(r"(?:^|\s)-[a-zA-Z]*f", args)) or "--force" in args
        if has_r and has_f:
            return True
    return False


# Matched against the QUOTE-STRIPPED command (real shell tokens, never legit inside quotes).
_TOKEN = [
    ("git force-push",          r"\bgit\s+push\b[^\n]*(\s--force\b|\s--force-with-lease\b|\s-f\b)"),
    ("git push --mirror",       r"\bgit\s+push\b[^\n]*--mirror\b"),
    ("git hard reset",          r"\bgit\s+reset\b[^\n]*--hard\b"),
    ("git clean force",         r"\bgit\s+clean\b[^\n]*\s-[a-z]*f"),
    ("git history rewrite",     r"\bgit\s+(filter-branch|filter-repo)\b"),
    ("git force-delete branch", r"\bgit\s+branch\b[^\n]*\s-D\b"),
    ("disk format",             r"\bmkfs(\.\w+)?\b[^\n]*/dev/"),
    ("raw disk write",          r"\bdd\b[^\n]*\bof=/dev/"),
    ("pipe-to-shell",           r"\b(curl|wget)\b[^|\n]*\|\s*(sudo\s+)?(ba|z)?sh\b"),
]
# Matched against the FULL command (danger legitimately quoted), gated by a client/cmd name.
_FULL = [
    ("db drop/truncate", r"\b(psql|mysql|mariadb|sqlite3|mongosh?|cockroach)\b[^\n]*\b(drop|truncate)\b"),
    ("dropdb",           r"\bdropdb\b"),
    ("destructive migrate-reset", r"\b(db:reset|db:drop|migrate\s+reset|migrate:reset|prisma\s+migrate\s+reset)\b"),
]
_TOKEN = [(l, re.compile(p)) for l, p in _TOKEN]
_FULL = [(l, re.compile(p)) for l, p in _FULL]


def main():
    if os.environ.get("MIMIR_NO_GUARD") or os.environ.get("MIMIR_NO_METER"):
        allow()
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        allow()
    cmd = (data.get("tool_input") or {}).get("command", "") or ""
    if not cmd.strip():
        allow()
    unq = strip_quotes(cmd)
    hits = []
    if dangerous_rm(unq):
        hits.append("recursive force-delete (rm -rf)")
    hits += [label for label, rx in _TOKEN if rx.search(unq)]
    hits += [label for label, rx in _FULL if rx.search(cmd)]
    if not hits:
        allow()
    reason = (
        "GATE — irreversible / high-blast-radius command (" + ", ".join(sorted(set(hits))) + "). "
        "Before it runs: right target? recoverable if wrong? has the user okayed THIS action "
        "(an override counts only once they've engaged the actual cost)? If you're acting under a "
        "standing explicit 'go' for exactly this, proceed; otherwise confirm with the user first."
    )
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


try:
    main()
except Exception:
    allow()  # fail-open: a malfunctioning guard must never block a command
