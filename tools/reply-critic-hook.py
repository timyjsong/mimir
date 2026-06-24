#!/usr/bin/env python3
# Stop hook — the REPLY CRITIC (guard #3, the keystone).
#
# Escapes the circularity problem for the internally-triggered "verify-before-asserting"
# reflex: instead of the model catching itself mid-thought (the failure the audit names),
# an EXTERNAL detector reads the just-finished turn POST-HOC and flags the over-claim
# signature — a completion/success/verification CLAIM made with NO check run this turn.
#
# Two modes:
#   - advisory (default): decision "approve" + systemMessage nudge. Cannot loop or block;
#     safe to wire live globally. Surfaces "you claimed X without checking."
#   - block (MIMIR_CRITIC_BLOCK=1): decision "block" + reason, forcing one revision before
#     the user sees the turn. Loop-guarded to fire AT MOST ONCE per user-turn.
#
# FAIL-OPEN: any error -> approve (exit 0, no output). A broken critic must never trap a turn.
# Eval-guarded by MIMIR_NO_GUARD / MIMIR_NO_METER. Transcript read is tail-bounded for speed.
import json, os, re, sys, tempfile

TAIL_BYTES = 1_000_000  # bound work per stop (server-cognizant)

CLAIM = re.compile(
    r"\b(tests?|test suite|build|lint|type-?check|ci|the suite)\s+"
    r"(pass(es|ed)?|succeed(s|ed)?|are green|is green|run clean)\b"
    r"|\ball (tests?\s+)?(pass(ing|ed)?|green)\b"
    r"|\b(it|that|this|the (fix|change|code|feature|patch|bug ?fix))\s+"
    r"(works|worked|is working|now works|is fixed|is verified)\b"
    r"|\b(i (have )?(verified|confirmed|tested)|verified (that|it)|confirmed (that|it|working)|"
    r"tested and (it )?(works|passes))\b"
    r"|\b(works as expected|working as expected|fixed and (working|verified)|"
    r"successfully (ran|tested|built|verified))\b", re.IGNORECASE)

HEDGE = re.compile(
    r"\b(should (work|pass)|haven'?t (tested|verified|run)|not (yet )?(tested|verified)|"
    r"untested|unverified|to be (tested|verified)|needs? (testing|verification|a test)|"
    r"i'?ll (test|verify|check|run)|let me (test|verify|check|run)|would (work|pass)|"
    r"in theory|presumably|i think|i believe|likely (works|passes)|can'?t verify)\b", re.IGNORECASE)


def approve():
    sys.exit(0)  # no output == approve (let the stop proceed)


def genuine_user(o):
    if o.get("type") != "user" or o.get("isSidechain") or o.get("isMeta"):
        return False
    m = o.get("message") or {}
    if m.get("role") != "user":
        return False
    c = m.get("content")
    if isinstance(c, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            return False
        txt = " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    elif isinstance(c, str):
        txt = c
    else:
        return False
    txt = txt.strip()
    if len(txt) < 2:
        return False
    inj = ("<task-notification", "<system-reminder", "<command-name", "<local-command",
           "<post-tool-use", "<user-prompt-submit-hook", "caveat: the messages below")
    if txt[:40].lower().startswith(inj):
        return False
    return True


def read_tail(path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        if size > TAIL_BYTES:
            f.seek(size - TAIL_BYTES)
            f.readline()  # drop partial line
        data = f.read()
    rows = []
    for line in data.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def main():
    if os.environ.get("MIMIR_NO_GUARD") or os.environ.get("MIMIR_NO_METER"):
        approve()
    data = json.load(sys.stdin)
    tpath = data.get("transcript_path")
    if not tpath or not os.path.isfile(tpath):
        approve()
    rows = read_tail(tpath)
    if not rows:
        approve()

    # turn_id = number of genuine user turns seen (used for the once-per-turn loop guard)
    turn_id = sum(1 for o in rows if genuine_user(o))
    # last genuine-user index -> everything after it is THIS turn
    last_u = max((i for i, o in enumerate(rows) if genuine_user(o)), default=-1)
    turn = rows[last_u + 1:]

    text_parts, tool_calls = [], 0
    for o in turn:
        if o.get("type") != "assistant" or o.get("isSidechain"):
            continue
        c = (o.get("message") or {}).get("content")
        if isinstance(c, list):
            for b in c:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text":
                    text_parts.append(b.get("text", ""))
                elif b.get("type") == "tool_use":
                    tool_calls += 1
        elif isinstance(c, str):
            text_parts.append(c)
    text = "\n".join(text_parts)

    # FLAG only the clean signature: a success/verification claim, with NO tool call this
    # turn and NO hedge. (A turn that ran any tool did empirical work; a hedged claim is
    # already honest about its uncertainty.)
    if tool_calls > 0 or not CLAIM.search(text) or HEDGE.search(text):
        approve()

    nudge = ("[verify] This turn asserts something works / passed / is verified, but ran no check "
             "this turn. Either run the check (Bash/Read/test) and report the actual result, or "
             "downgrade the claim to its real confidence. Don't state a checkable specific you "
             "haven't checked — and don't chain a further claim on it.")

    block = os.environ.get("MIMIR_CRITIC_BLOCK") == "1"
    if not block:
        print(json.dumps({"decision": "approve", "systemMessage": nudge}))
        return

    # block mode: fire at most once per user-turn (loop guard)
    sid = data.get("session_id") or os.path.basename(tpath)
    statef = os.path.join(tempfile.gettempdir(), "mimir-critic-%s.json" % re.sub(r"\W", "_", sid))
    last_blocked = None
    try:
        last_blocked = json.load(open(statef)).get("turn_id")
    except Exception:
        pass
    if last_blocked == turn_id:
        approve()  # already nudged this turn -> let the revision through
    try:
        json.dump({"turn_id": turn_id}, open(statef, "w"))
    except Exception:
        pass
    print(json.dumps({"decision": "block", "reason": nudge}))


try:
    main()
except Exception:
    approve()  # fail-open: a broken critic must never trap a turn
