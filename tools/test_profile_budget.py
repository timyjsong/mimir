#!/usr/bin/env python3
# Local test for profile-budget-hook.py — verifies cap enforcement on USER.md.
import json, subprocess, sys, os, tempfile

HOOK = os.path.join(os.path.dirname(__file__), "profile-budget-hook.py")
TMP = tempfile.mkdtemp(prefix="profile-test-")
UP = os.path.join(TMP, "mimir", "USER.md")
os.makedirs(os.path.dirname(UP))


def run(payload, env=None):
    e = dict(os.environ)
    e.pop("MIMIR_NO_GUARD", None)
    e.pop("MIMIR_NO_METER", None)
    e["MIMIR_PROFILE_HARDCAP"] = str(CAP)   # pin so the test is independent of the hook default
    e["MIMIR_PROFILE_HARDLINES"] = "120"
    if env:
        e.update(env)
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                       capture_output=True, text=True, env=e)
    out = p.stdout.strip()
    if not out:
        return None  # allow
    try:
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"]
    except Exception:
        return "<malformed:%r>" % out


CAP = 6500
big = "x" * (CAP + 800)
small = "x" * 2000

fails = []

def chk(label, got, want):
    if got != want:
        fails.append((label, want, got))


# Write growing past cap -> deny; under cap -> allow
chk("write over cap -> deny", run({"tool_name": "Write", "tool_input": {"file_path": UP, "content": big}}), "deny")
chk("write under cap -> allow", run({"tool_name": "Write", "tool_input": {"file_path": UP, "content": small}}), None)
# line cap
manylines = "a\n" * 200
chk("write over line-cap -> deny", run({"tool_name": "Write", "tool_input": {"file_path": UP, "content": manylines}}), "deny")

# Edit on an already-over file: shrink allowed, grow-past denied
with open(UP, "w") as f:
    f.write("y" * (CAP + 2000))  # already over
chk("shrink edit when over -> allow",
    run({"tool_name": "Edit", "tool_input": {"file_path": UP, "old_string": "y" * 3000, "new_string": "z" * 10}}), None)
chk("grow edit when over -> deny",
    run({"tool_name": "Edit", "tool_input": {"file_path": UP, "old_string": "y" * 5, "new_string": "z" * 500}}), "deny")
chk("replace_all -> allow (can't size)",
    run({"tool_name": "Edit", "tool_input": {"file_path": UP, "old_string": "y", "new_string": "z", "replace_all": True}}), None)

# non-profile paths untouched
chk("other USER.md (not in mimir/) -> allow",
    run({"tool_name": "Write", "tool_input": {"file_path": "/tmp/USER.md", "content": big}}), None)
chk("other file -> allow",
    run({"tool_name": "Write", "tool_input": {"file_path": os.path.join(TMP, "mimir", "notes.md"), "content": big}}), None)

# fail-open / guards
chk("non-write tool -> allow", run({"tool_name": "Read", "tool_input": {"file_path": UP}}), None)
chk("malformed -> allow (fail-open)", run({"garbage": True}), None)
chk("eval-guard -> allow",
    run({"tool_name": "Write", "tool_input": {"file_path": UP, "content": big}}, env={"MIMIR_NO_GUARD": "1"}), None)
# malformed stdin
e = dict(os.environ); e.pop("MIMIR_NO_GUARD", None); e.pop("MIMIR_NO_METER", None)
p = subprocess.run([sys.executable, HOOK], input="{bad", capture_output=True, text=True, env=e)
chk("malformed stdin -> silent allow", (p.stdout.strip() == "", p.returncode), (True, 0))

total = 12
if fails:
    print("FAIL %d/%d:" % (len(fails), total))
    for label, want, got in fails:
        print("  [%s] want %r got %r" % (label, want, got))
    sys.exit(1)
print("PASS %d/%d (cap, line-cap, shrink-ok, scope, fail-open all verified)" % (total, total))
