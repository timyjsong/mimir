# Mimir change protocol

How to change Mimir without (a) fixing the wrong thing, (b) overengineering, or (c) regressing. The discipline that turns "run it and tune in the session" into a loop with a pre-committed oracle and a fresh-context check.

Developer-facing. Not loaded by the lead at runtime.

## The three failure modes this defends against

| Failure | Defense |
|---|---|
| Fixed the wrong thing | Diagnose from a real trace and cite the exact instruction violated/missing — don't guess from a vibe. |
| Overengineered | Smallest edit that flips the scenario. Prefer relocate/delete over add. Watch the `must-not` lines. |
| Introduced new problems | Re-run the affected scenarios in a fresh context before calling it done. |

## The loop

```
real run surfaces a problem
   │
   ▼
DIAGNOSE from the trace
   │   cite the exact SKILL.md / agent-def line that was violated or missing.
   │   if you can't point to a line, you don't understand the bug yet.
   ▼
WRITE / UPDATE a scenario in scenarios.md  (source: trace:<session-id>)
   │   this is the oracle. write expect + must-not BEFORE editing the prompt.
   ▼
MINIMAL change
   │   smallest edit that flips the scenario. relocate/delete beats add.
   │   adding lines to SKILL.md is suspect — it's the lead's hot path.
   ▼
RUN affected scenarios — Tier 1, fresh context
   │   does expect pass? did any must-not newly trigger?
   ▼
LIVE smoke (Tier 2) — only if you touched plumbing
   │   install / workflow billing+prereq / epic-gate / subagent spawn
   ▼
commit  →  new failures become new scenarios
```

## Running Tier 1 (offline) — no codebase required

The cheap, repeatable check. For each affected scenario:

1. Spawn a **fresh** subagent (`Agent` tool) — fresh context is the point; you're testing the prompt, not your memory of intent.
2. Give it: the current `SKILL.md` (and the relevant agent def, if the scenario is worker-side) as the instructions under test, the scenario's `situation` as synthetic context (fake disk state, marker contents, `bmad-help` output), and the `trigger`.
3. Ask only: **"what is your next action, and why?"** — capture the answer; don't let it run the whole lifecycle.
4. Check the answer against `expect` and `must-not`.

Optionally add a second **judge** subagent: feed it the scenario + the captured answer + the relevant SKILL.md discipline, ask it to score pass/fail per `expect` and flag any `must-not`. Start manual; add the judge only when scenario volume makes hand-checking tedious.

**Fidelity gap to remember:** Tier 1 tests decision logic, not live tool plumbing. It won't catch "does it actually call ToolSearch / does the `Agent` spawn or workflow launch fire correctly." Those are Tier 2.

## Running Tier 2 (live) — before a release

A handful of real `/mimir` sessions, for the behaviors that only exist live: install flow, workflow billing + prerequisite check, epic-gate review, subagent spawn. Slow and manual — run only when a change touched that plumbing, or periodically as a smoke test.

## Guardrails

- **The bank grows only from earned scenarios** — a real failure, or a discipline you're actively changing. No speculative scenario-writing (that's overengineering the eval system itself).
- **Oracle before edit.** If you change the prompt first and write the scenario after, you've defeated the pre-commitment.
- **One discipline at a time.** Bundling unrelated changes makes regression attribution impossible.
- **Removing beats adding.** Especially in `SKILL.md`. If a fix grows the lead's hot path, ask whether the real problem is elsewhere.
