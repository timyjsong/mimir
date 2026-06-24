#!/usr/bin/env python3
# Local test for prompt-cue-hook.py — verifies which cue(s) fire per prompt. No server.
import json, subprocess, sys, os

HOOK = os.path.join(os.path.dirname(__file__), "prompt-cue-hook.py")


def cues(prompt):
    e = dict(os.environ)
    e.pop("MIMIR_NO_GUARD", None)
    e.pop("MIMIR_NO_METER", None)
    p = subprocess.run([sys.executable, HOOK], input=json.dumps({"user_prompt": prompt}),
                       capture_output=True, text=True, env=e)
    out = p.stdout.strip()
    if not out:
        return set()
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    tags = set()
    if "State/orientation" in ctx:
        tags.add("derive")
    if "irreversible" in ctx:
        tags.add("destruct")
    if "Small, scoped" in ctx:
        tags.add("scale")
    return tags


# (prompt, expected set of cue tags)
CASES = [
    ("what's the state of the build?", {"derive"}),
    ("what is the state of the build?", {"derive"}),
    ("where are we", {"derive"}),
    ("catch me up", {"derive"}),
    ("get caught up on where we left off", {"derive"}),
    ("delete the prod database", {"destruct"}),
    ("force push to main", {"destruct"}),
    ("can you rm -rf the build dir", {"destruct"}),
    ("nuke the old branches", {"destruct"}),
    ("fix the typo", {"scale"}),
    ("run the tests", {"scale"}),
    ("bump the version", {"scale"}),
    ("rename this file", {"scale"}),
    # complex / questions / longer -> no scale card
    ("should we refactor the auth module?", set()),
    ("plan the data migration", set()),
    ("why is this query slow?", set()),
    ("investigate the flaky test in CI and figure out root cause", set()),
    # mutual exclusion
    ("delete the table", {"destruct"}),          # not scale
    ("what's the status?", {"derive"}),          # not scale
    # M5: code-edit deletes are NOT destructive (no weighty object)
    ("delete this line", {"scale"}),
    ("remove the unused import", {"scale"}),
    # nothing
    ("here's a long description of a feature I want you to build with several parts and details", set()),
    ("", set()),
]

fails = []
for prompt, exp in CASES:
    got = cues(prompt)
    if got != exp:
        fails.append((prompt, exp, got))
# malformed input -> fail-silent
e = dict(os.environ); e.pop("MIMIR_NO_GUARD", None); e.pop("MIMIR_NO_METER", None)
p = subprocess.run([sys.executable, HOOK], input="{not json", capture_output=True, text=True, env=e)
if p.stdout.strip() or p.returncode != 0:
    fails.append(("<malformed input>", "silent exit 0", "out=%r rc=%d" % (p.stdout, p.returncode)))
# eval-guard
p = subprocess.run([sys.executable, HOOK], input=json.dumps({"user_prompt": "delete the database"}),
                   capture_output=True, text=True, env={**os.environ, "MIMIR_NO_GUARD": "1"})
if p.stdout.strip():
    fails.append(("<eval-guard>", "silent", p.stdout))

# M7: hook must also read the 'prompt' key (not only 'user_prompt') -> can't be a silent no-op
e7 = dict(os.environ); e7.pop("MIMIR_NO_GUARD", None); e7.pop("MIMIR_NO_METER", None)
p7 = subprocess.run([sys.executable, HOOK], input=json.dumps({"prompt": "what's the state?"}),
                    capture_output=True, text=True, env=e7)
if "State/orientation" not in p7.stdout:
    fails.append(("<M7 prompt-key>", "derive cue via 'prompt' key", p7.stdout))

total = len(CASES) + 3
if fails:
    print("FAIL %d/%d:" % (len(fails), total))
    for prompt, exp, got in fails:
        print("  %r expected %s got %s" % (prompt, exp, got))
    sys.exit(1)
print("PASS %d/%d" % (total, total))
