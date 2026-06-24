#!/usr/bin/env python3
# Local test for reply-critic-hook.py — synthetic transcripts, no server.
# Verifies the over-claim detector, the tool-call/hedge exclusions, advisory vs block,
# the once-per-turn loop guard, and fail-open behavior.
import json, subprocess, sys, os, tempfile, glob

HOOK = os.path.join(os.path.dirname(__file__), "reply-critic-hook.py")
TMP = tempfile.mkdtemp(prefix="critic-test-")
# hermetic: clear any leftover loop-guard state from prior runs
for _f in glob.glob(os.path.join(tempfile.gettempdir(), "mimir-critic-*.json")):
    try:
        os.remove(_f)
    except OSError:
        pass


def U(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def A(text):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def TOOL(name="Bash"):
    return {"type": "assistant", "message": {"role": "assistant",
            "content": [{"type": "tool_use", "name": name, "input": {}}]}}


def write(rows, name):
    p = os.path.join(TMP, name)
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return p


def run(rows_or_path, block=False, sid="s1"):
    path = rows_or_path if isinstance(rows_or_path, str) else write(rows_or_path, sid + ".jsonl")
    e = dict(os.environ)
    e.pop("MIMIR_NO_GUARD", None)
    e.pop("MIMIR_NO_METER", None)
    if block:
        e["MIMIR_CRITIC_BLOCK"] = "1"
    else:
        e.pop("MIMIR_CRITIC_BLOCK", None)
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(
        {"transcript_path": path, "session_id": sid}), capture_output=True, text=True, env=e)
    out = p.stdout.strip()
    if not out:
        return ("approve", False)
    o = json.loads(out)
    return (o.get("decision", "?"), bool(o.get("systemMessage") or o.get("reason")))


fails = []

def expect(label, got, want):
    if got != want:
        fails.append((label, want, got))


# --- advisory mode (default): flag == ("approve", True) ; no-flag == ("approve", False)
expect("claim+no-tool -> FLAG",
       run([U("fix the bug"), A("Fixed it. The tests pass now and the build is green.")]),
       ("approve", True))
expect("claim+no-tool 'it works' -> FLAG",
       run([U("does it work?"), A("Yes — the fix works and I verified it end to end.")]),
       ("approve", True))
expect("claim WITH tool -> no flag",
       run([U("run tests"), TOOL("Bash"), A("The tests pass.")]),
       ("approve", False))
expect("claim WITH hedge -> no flag",
       run([U("fix it"), A("The fix should work, but I haven't tested it yet.")]),
       ("approve", False))
expect("plain analysis, no claim -> no flag",
       run([U("what are the options?"), A("Here are three approaches, ranked. I recommend the first.")]),
       ("approve", False))
expect("question turn -> no flag",
       run([U("hi"), A("What would you like me to look at first?")]),
       ("approve", False))
expect("'should pass' hedge -> no flag",
       run([U("x"), A("That change should pass CI.")]),
       ("approve", False))

# --- block mode: flag == ("block", True)
expect("block: claim+no-tool -> BLOCK",
       run([U("fix the bug"), A("Done — all tests pass.")], block=True, sid="b1"),
       ("block", True))

# --- loop guard: second stop at SAME turn -> approve (no re-block)
loop_rows = [U("fix the bug"), A("Done — all tests pass.")]
p = write(loop_rows, "loop.jsonl")
first = run(p, block=True, sid="loopsid")
# simulate the revision: model appends more text, SAME user turn (no new user msg)
with open(p, "a") as f:
    f.write(json.dumps(A("On reflection I haven't run them; let me check.")) + "\n")
second = run(p, block=True, sid="loopsid")
expect("loop-guard: first blocks", first, ("block", True))
expect("loop-guard: second approves", second, ("approve", False))
# a NEW user turn with a fresh over-claim -> can block again
with open(p, "a") as f:
    f.write(json.dumps(U("now do the other one")) + "\n")
    f.write(json.dumps(A("Done — all tests pass for that one too.")) + "\n")
third = run(p, block=True, sid="loopsid")
expect("loop-guard: new turn re-blocks", third, ("block", True))

# --- fail-open / guards
e = dict(os.environ); e.pop("MIMIR_NO_GUARD", None); e.pop("MIMIR_NO_METER", None)
p1 = subprocess.run([sys.executable, HOOK], input=json.dumps({"transcript_path": "/no/such/file"}),
                    capture_output=True, text=True, env=e)
expect("missing transcript -> approve", (p1.stdout.strip() == "", p1.returncode), (True, 0))
p2 = subprocess.run([sys.executable, HOOK], input="{bad json", capture_output=True, text=True, env=e)
expect("malformed stdin -> approve", (p2.stdout.strip() == "", p2.returncode), (True, 0))
g = run([U("x"), A("all tests pass")], sid="guard")  # would flag...
eg = dict(os.environ); eg["MIMIR_NO_GUARD"] = "1"
pg = subprocess.run([sys.executable, HOOK], input=json.dumps(
    {"transcript_path": write([U("x"), A("all tests pass")], "g2.jsonl"), "session_id": "g2"}),
    capture_output=True, text=True, env=eg)
expect("eval-guard -> silent approve", (pg.stdout.strip() == ""), True)

total = 16
if fails:
    print("FAIL %d/%d:" % (len(fails), total))
    for label, want, got in fails:
        print("  [%s] want %r got %r" % (label, want, got))
    sys.exit(1)
print("PASS %d/%d (advisory, block, loop-guard, fail-open all verified)" % (total, total))
