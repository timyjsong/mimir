# bmad delegation playbook (subagent — heavy / autonomous work)

Read this before delegating a `bmad-*` workflow to a subagent. **Only autonomous/heavy work is delegated.** Interactive elicitation (product brief, PRD create, architecture Q&A, story shaping) is run by the lead **in-session** (SKILL.md → "Running a skill in-session"), not delegated.

## Delegate vs. run in-session — the test

**Does the skill halt for user input mid-run (menus, step-by-step elicitation)?**

- **Yes → run in-session (lead).** A fire-and-return subagent can't answer its menus — it would hang at the first one, or answer them itself and defeat the collaboration. BMAD's interactive, menu/step-driven skills: `bmad-product-brief`, `bmad-prd` (create), `bmad-create-epics-and-stories`, `bmad-create-story`, `bmad-create-architecture`. (Tell: the skill greets the user, presents menus, and says "halt and wait for user input.")
- **No → delegate to a subagent (fire-and-return).** Runs autonomously to completion: `bmad-domain-research`, `bmad-market-research`, `bmad-document-project`, `bmad-check-implementation-readiness`, validation/sharding (`bmad-validate-prd`, `bmad-shard-doc`), `bmad-generate-project-context`.
- **Unsure?** Read the skill's `SKILL.md` — if its workflow halts at menus / waits for user selection, it's in-session; if it runs end-to-end, it's a subagent.
- **Interactive *and* heavy** (e.g. a large PRD or epics list): still in-session — manage the budget (SKILL.md → Context budget); never trade the user out of the loop to save context.

## How to spawn

- **`Agent` tool, fresh context, ephemeral** (no persistent name). Fresh per task — never carry a subagent across tasks (context rots).
- Subagent type: `bmad-worker` (generic `bmad-*` runner) — see `~/.claude/agents/bmad-worker.md`. The skill self-orients from `_bmad/`; don't pre-load context.
- Mode: **background** for genuinely autonomous work — don't block, verify on disk on completion. **Foreground** only if it might surface a question.
- **Model:** spawns do NOT inherit the lead's model/effort (verified). Set it explicitly if the work needs a specific model.

## Hand-off must contain (delegation hygiene)

1. **Skill to run** — exact `bmad-*` name.
2. **The task** — intent (research / validate / check / document) and what to produce.
3. **User's decisions verbatim** — scope, options, constraints in the user's words when decision-bearing.
4. **User-provided source material** (if any) — BMAD can't discover it otherwise.
5. **Return shape** — short result + artifact path(s) on disk; for richer handback, a `.worker-handoff.md` the lead reads before relaying.

If you can't write a complete hand-off, gate first — you don't have enough from the user.

## On completion

Read the produced artifact from disk before briefing (don't trust the returned prose). If the subagent left a handoff file, read it and translate per **Relay** (below). The subagent is ephemeral — it's done; nothing to retire. Background subagents can't surface mid-run questions, so check for `[ASSUMPTION]` tags or visible gaps.

## Relay (worker ↔ user)

In-session work needs no relay — you're running it; just keep the cadence and PM voice. For **subagent**-delegated work, you are the PM between the user and the worker:

- **Read the handoff file / artifact from disk before relaying.** A subagent's returned message is a pointer; the content is on disk.
- **Worker → user:** preserve every concrete question/option/decision (N questions → N questions); translate BMAD jargon to plain; keep the substance of pushback in PM voice; strip worker-to-lead meta ("flag for the lead", "holding for next round").
- **User → worker:** convey every decision; quote literal text when wording is decision-bearing; address every question; add nothing the user didn't say.
