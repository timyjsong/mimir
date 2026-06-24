#!/usr/bin/env python3
# PreToolUse hook (matcher Bash) — the ACTION GATE (guard #1).
#
# Externalizes the "gate-before-irreversible-actions" disposition: the rm/push/migrate token
# IS the trigger, matched deterministically out-of-band, so the gate fires even if a resident
# rule was never "remembered". permissionDecision "ask" (pause-and-confirm), never "deny".
#
# False-positive control: QUOTES and #COMMENTS are stripped before matching, so a scary token
# inside an echo/grep string or a trailing comment never fires. Patterns are tight (genuinely
# irreversible / high-blast) to avoid the over-gating painpoint; a miss is recoverable, a
# false-positive costs one confirm.
# Known accepted gaps: a real danger fully wrapped in quotes (bash -c "rm -rf x") evades by
# design (the cost of the quote-strip FP defense); DB-via-client (psql -c 'drop ...') is not
# gated (the prompt-cue + the SQL itself in quotes are out of scope here).
#
# FAIL-OPEN: any error -> allow(). Eval-guarded by MIMIR_NO_GUARD / MIMIR_NO_METER.
import json, os, re, sys


def allow():
    sys.exit(0)


def strip_quotes(s):
    s = re.sub(r"'[^']*'", "''", s)
    s = re.sub(r'"[^"]*"', '""', s)
    return s


def strip_comments(s):
    return re.sub(r"#[^\n]*", "", s)  # run AFTER strip_quotes so quoted '#' is already blanked


def dangerous_rm(c):
    for m in re.finditer(r"\brm\b([^\n;&|]*)", c):
        args = m.group(1)
        has_r = bool(re.search(r"(?:^|\s)-[a-zA-Z]*r", args)) or "--recursive" in args
        has_f = bool(re.search(r"(?:^|\s)-[a-zA-Z]*f", args)) or "--force" in args
        if has_r and has_f:
            return True
    return False


# git, with optional global opts (-C <path>, -c k=v, -p, --no-pager ...) before the subcommand
_GIT = r"\bgit\s+(?:-[cC]\s+\S+\s+|--[A-Za-z][\w-]*(?:=\S+)?\s+|-[A-Za-z]\s+)*"

# Matched against the QUOTE+COMMENT-stripped command (real shell tokens). Case-SENSITIVE
# (shell flags are case-significant: git branch -D force-deletes, -d is safe).
_TOKEN = [
    ("git force-push",          _GIT + r"push\b[^\n]*(\s--force\b|\s--force-with-lease\b|\s-f\b|\s\+\S)"),
    ("git push --mirror",       _GIT + r"push\b[^\n]*--mirror\b"),
    ("git hard reset",          _GIT + r"reset\b[^\n]*--hard\b"),
    ("git clean force",         _GIT + r"clean\b[^\n]*\s-[a-z]*f"),
    ("git history rewrite",     _GIT + r"(filter-branch|filter-repo)\b"),
    ("git force-delete branch", _GIT + r"branch\b[^\n]*\s-D\b"),
    ("recursive disk delete",   r"\bfind\b[^\n]*\s-delete\b"),
    ("shred",                   r"\bshred\s+-?\S"),
    ("truncate to zero",        r"\btruncate\b[^\n]*\s-s\s*0\b"),
    ("disk format",             r"\bmkfs(\.\w+)?\b[^\n]*/dev/"),
    ("raw disk write",          r"\bdd\b[^\n]*\bof=/dev/"),
    ("pipe-to-shell",           r"\b(curl|wget)\b[^|\n]*\|\s*(sudo\s+)?(ba|z)?sh\b"),
]
# Matched against QUOTE+COMMENT-stripped command, case-INSENSITIVE (SQL/ops keywords).
# `dropdb` is a common word -> anchored to a command position (start or after ; && || |).
_STMT = r"(?:^|[\n;&|]\s*)(?:sudo\s+)?"
_FULL = [
    ("dropdb",                       _STMT + r"dropdb\b"),
    ("destructive db migrate/reset", r"\b(db:reset|db:drop|migrate\s+reset|migrate:reset|prisma\s+migrate\s+reset|db:migrate:reset)\b"),
    ("redis flush",                  r"\bredis-cli\b[^\n|]*\bflush(all|db)\b"),
    ("terraform destroy",            r"\bterraform\s+destroy\b"),
    ("kubectl delete namespace",     r"\bkubectl\s+delete\s+(ns|namespace)\b"),
    ("aws s3 remove-bucket --force", r"\baws\s+s3\s+rb\b[^\n]*--force\b"),
]
_TOKEN = [(l, re.compile(p)) for l, p in _TOKEN]
_FULL = [(l, re.compile(p, re.IGNORECASE)) for l, p in _FULL]

# DB-client exec of a drop/truncate: matched on the ORIGINAL command (the SQL is legitimately
# quoted) but gated TIGHT — a db client at statement-start WITH a -c/-e exec flag AND drop. This
# fires on `psql -c 'drop database'` yet not on `grep "drop table"` (no client) or an echo'd
# example (client not at statement-start).
_PSQL_EXEC = re.compile(
    r"(?:^|[\n;&|]\s*)(?:sudo\s+)?(psql|mysql|mariadb|mongosh?|cockroach)\b[^\n;&|]*"
    r"\s-(?:c\b|e\b|-command\b|-execute\b|-eval\b)[^\n;&|]*\b(drop|truncate)\b", re.IGNORECASE)


def main():
    if os.environ.get("MIMIR_NO_GUARD") or os.environ.get("MIMIR_NO_METER"):
        allow()
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        allow()
    cmd = (data.get("tool_input") or {}).get("command", "") or ""
    if not cmd.strip():
        allow()
    clean = strip_comments(strip_quotes(cmd))
    hits = []
    if dangerous_rm(clean):
        hits.append("recursive force-delete (rm -rf)")
    hits += [label for label, rx in _TOKEN if rx.search(clean)]
    hits += [label for label, rx in _FULL if rx.search(clean)]
    if _PSQL_EXEC.search(cmd):
        hits.append("db client drop/truncate")
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
