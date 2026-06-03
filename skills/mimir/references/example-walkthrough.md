# Mimir v3 — end-to-end walkthrough

Illustrative trace of a full v3 lifecycle. **Maintainer doc — not loaded at runtime** (not referenced from `SKILL.md`); read it to see how the three modes fit together in practice. Paths are illustrative (real paths resolve from `_bmad/bmm/config.yaml`). Scenario: a greenfield project, **splitwise-lite** — a local-first expense-splitting CLI.

---

## Phase 0 — first invocation, install needed

User runs `/mimir` in an empty dir. Mimir orients silently (no `_bmad/`), then:

> # ᛗᛁᛗᛁᚱ
>
> ꜰʟᴀɢꜱ
>> ⚑ no _bmad/ at /home/user/projects/splitwise-lite — install needed

Project root is /home/user/projects/splitwise-lite. BMAD isn't installed here. Install it, or did you mean a different folder?

User: "install here." Mimir runs the install via Bash (`references/install-bmad.md`), verifies `_bmad/` + config on disk, then:

> BMAD is installed — the foreground install auto-reloaded the `bmad-*` skills into this session (no restart). Starting from the product brief.

(Install auto-reloads the skills in-session — no restart; see `references/install-bmad.md` for the mechanism and fallback.)

---

## Phase 1 — the brief (IN-SESSION)

Fresh session. Mimir orients from disk + auto-memory, sees a fresh install:

> # ᛗᛁᛗᛁᚱ
>
> ᴘʀᴏɢʀᴇꜱꜱ
>> ▸ brief
>> ○ PRD
>> ○ architecture
>> ○ epics + stories
>> ○ readiness

Fresh project. bmad-help recommends the brief; I agree — it locks the WHAT before the HOW. I'll run it here in our conversation. Go?

User: "go." Mimir invokes `bmad-product-brief` **in-session** (Skill tool) and runs the elicitation itself — questions paced by effort, not a fixed count. Starting in-session work is within-phase, so the turn is just a compact line, not a block:

> ᛗᛁᛗᛁᚱ · two questions before I draft

Two things before I draft:
1. Who's the user — just you, or other people splitting expenses too?
2. "Local-first" — files you own, no cloud at all? Or sync optional?

No worker, no relay — Mimir *is* running the skill, in PM voice. The brief is written to disk as it firms up; turns stay tight across rounds.

---

## Phase 2 — PRD / architecture (in-session, fresh context per phase)

Brief done on disk. For the PRD, rather than pile its conversation on top of the brief's, Mimir starts in **fresh context** (the `brief.md` on disk + auto-memory make this lossless — `/clear` + `/mimir` clears context and re-orients, skill still loaded). Same in-session pattern, same cadence. Architecture follows the same way.

(Why: at Opus 4.8 / high effort, brief + PRD + architecture in one accumulating context would overflow 1M. Fresh-per-phase keeps each turn light; disk is the durable record.)

---

## Phase 3 — domain research (SUBAGENT, fire-and-return)

Mid-solutioning, Mimir needs market/domain research — bulky and autonomous. Not in-session (it'd bloat the lead's context). Delegation rides the compact line — the action wording signals the hand-off, no block:

> ᛗᛁᛗᛁᚱ · research running; I'll brief you when it lands

Mimir spawns a fresh-context `bmad-worker` (per `playbooks/bmad.md`) with skill + task + user decisions verbatim. The worker runs autonomously, writes its report to disk, returns one short result:

```
Status:   complete
Artifact: /home/user/.../research/domain-report.md
Summary:  4 comparable tools surveyed; key gap is offline-first; 2 [ASSUMPTION] tags on pricing.
```

Mimir reads the report from disk (not just the summary), flags the assumptions, briefs the user. The worker is gone — fire-and-return, nothing to retire.

---

## Phase 4 — readiness (SUBAGENT, autonomous)

`bmad-check-implementation-readiness` runs the same way — a background fire-and-return subagent. It returns a verdict; Mimir reads the report from disk and applies its own judgment on top:

> # ᛗᛁᛗᛁᚱ
>
> ᴘʀᴏɢʀᴇꜱꜱ
>> ✓ brief
>> ✓ PRD
>> ✓ architecture
>> ✓ epics + stories
>> ✓ readiness
>> &nbsp;&nbsp;&nbsp;└ *verdict: go*
>
> ꜰʟᴀɢꜱ
>> ⚑ build-ready, but loki isn't implemented yet

Readiness: go, and I agree — artifacts are coherent. One thing: loki (the workflow build) isn't implemented yet, so we can advise build-ready but can't start the build today.

---

## Phase 5 — build (WORKFLOW — gated, future)

When loki ships and the gates clear (workflow billing verified = subscription; `CLAUDE_CODE_WORKFLOWS=1`), the build runs as a **Dynamic Workflow**, one per epic:

> # ᛗᛁᛗᛁᚱ
>
> ᴘʀᴏɢʀᴇꜱꜱ
>> ▸ epic 1 · ledger core
>> ○ epic 2 · split + settle
>> ○ epic 3 · shareable summary

The workflow fans out story-builders + adversarial review, checkpointing per story to disk. Mimir monitors via `/workflows`, then **gates between epics**: reads the outputs from disk, reviews against the plan (drift check), briefs the user, launches the next epic. If the session exits mid-build, a fresh launch reads the checkpoint manifest and re-runs only incomplete stories.

---

## Patterns this demonstrates

1. **Mode per step** — interactive (brief) in-session; heavy/autonomous (research, readiness) to fire-and-return subagents; build to a workflow.
2. **In-session elicitation** — the lead runs the skill; no worker, no relay; questions paced by effort.
3. **Fresh context per heavy phase** — disk artifacts make brief→PRD→architecture lossless across resets; nothing accumulates past 1M.
4. **Fire-and-return** — delegated workers run once, write to disk, return a short result; no persistence, no teams.
5. **Disk is truth** — Mimir reads artifacts from disk before briefing; every session re-orients from disk + auto-memory.
6. **Advisory + gating** — Mimir cites BMAD's view and its own, and gates at every phase boundary.
