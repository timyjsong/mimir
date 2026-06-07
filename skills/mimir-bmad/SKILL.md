---
name: mimir-bmad
description: "Drive a structured greenfield build through the BMAD-METHOD v6 lifecycle — Analysis → Planning → Solutioning → Implementation, with Huldra as the autonomous build. Mimir's brain loads this on-demand once build-intent is established and the user wants a framework-driven build done with rigor: the brain supplies the generic disciplines (the read, the spine, proportional gates, continuity, cadence); this skill resolves them into the concrete BMAD instance (lifecycle, install, orientation, delegation, relay, the build)."
---

# BMAD playbook — driving a structured greenfield build (BMAD-METHOD v6)

> **The brain loads this when intent is a structured build** done via BMAD-METHOD v6 (with `Huldra` as the autonomous build). Everything BMAD-specific lives here; the **brain** (your operating layer) supplies the generic disciplines — the read/advisory, the spine, proportional gates, status that scales, continuity, cadence. This playbook resolves "the framework" for those rules into the concrete BMAD instance. When no build is in play, this stays on the shelf.

## The framework & lifecycle

You drive a **BMAD-METHOD v6** project across its lifecycle — Analysis → Planning → Solutioning → Implementation — and, when readiness and your own judgment agree it's build-ready, hand the build to **Huldra**.

- **The framework's authoritative next-step source** (what the brain's advisory rules call on): `bmad-help`, and/or the canonical sequence in `_bmad/bmm/module-help.csv` — each skill's `phase`, `preceded-by`, `required`. **Derive the next step from these on disk, never a remembered order** (e.g. architecture precedes epics within Solutioning — the classic stale-sequence trap). Right-size the sequence to the stakes (a throwaway spike doesn't warrant a full PRD + formal architecture; a funded, board-facing product does — hold the rigor).

## How work executes — three modes

Choose per step, on two axes: **does it need live back-and-forth with the user?** and **how much context does it consume?**

- **In-session (you run the skill yourself).** Interactive, conversation-driven work: ideation, analysis, the product brief, the interactive parts of PRD and architecture. Invoke the `bmad-*` skill directly (Skill tool) and run it, honoring cadence. (Verified: the lead can invoke and run BMAD skills in-session.)
- **Subagent (delegate; fresh context; artifact returns to disk).** Heavy/autonomous work: domain/market research, document-project, readiness checks, bulky generation. Fire-and-return; you stay light and verify the artifact on disk. Ephemeral — don't keep subagents alive across steps.
- **Workflow (autonomous fan-out).** The Huldra build (gated — see below).

**The deterministic test (in-session vs subagent):** does the skill **halt for user input mid-run** (menus, step-by-step elicitation)? → **in-session** (a fire-and-return subagent can't answer its menus — it would hang, or answer them itself and defeat the collaboration). Does it **run autonomously to completion**? → **subagent**. BMAD's interactive skills (`bmad-product-brief`, `bmad-prd` create, `bmad-create-epics-and-stories`, `bmad-create-story`, `bmad-create-architecture`) are menu/step-driven → in-session; its autonomous ones (research, `bmad-document-project`, readiness, validation/sharding) run to completion → subagent. Interactive *and* heavy → still in-session; manage the budget, never trade the user out of the loop to save context.

## Orientation when driving BMAD

When a build is the active work, reconstruct BMAD state from disk (silently — no narration):

1. Resolve the project root (cwd) and read `_bmad/bmm/config.yaml` (output paths, project naming).
2. List output folders; skim what artifacts exist.
3. Read auto-memory — your counsel notes (overrides against your rec, open bets, stated stakes) + standing state.
4. **Determine the actual next step from disk** — invoke `bmad-help`, and/or read `module-help.csv` (`phase`, `preceded-by`, `required`). Never assert what BMAD recommends from memory.
5. Brief the user: where we are, what's complete, what BMAD recommends next, what *you* recommend (with reasoning if you diverge). Gate.

**What disk holds:** `_bmad/` config, `_bmad-output/` artifacts, and auto-memory — the BMAD-specific "source of truth" the brain reconstructs from.

## Status (driving a build)

In a structured build the user is navigating a multi-phase process, so orient them with a status header (this is the structured-work status format the brain's status discipline defers to):

- **Full block** — on a **completion** (a step/phase finished, a delegated subagent returned), a **phase change**, or **first orientation**: a multi-section blockquote led by the runic `ᛗᛁᛗᛁᚱ` wordmark, with `ᴊᴜꜱᴛ ᴅᴏɴᴇ` (off-spine completions) / `ᴘʀᴏɢʀᴇꜱꜱ` (the lifecycle checklist — carries the phase) / `ꜰʟᴀɢꜱ` (persistent open items); each section omit-when-empty.
- **Compact line** — every other turn (within-phase gates, "your call", mid-elicitation, delegating to a worker): a one-line blockquote `> ᛗᛁᛗᛁᚱ · <what's going on>`.

The exact format (glyphs, nesting, all variants) is in `references/status-format.md` — load it at orientation. Don't narrate internal work step-by-step; stay quiet while working and surface at the result.

## Two startup cases

- **BMAD installed** (`_bmad/` present). Orient as above; brief, recommend, gate.
- **BMAD not installed.** Only reach here once build-intent is established and the user has chosen BMAD. Print the absolute project path; ask whether to install here or redirect — do NOT auto-install. On confirm, run the install + reload (owned by `references/install-bmad.md` — foreground install → in-session skill reload, no restart). Then go straight to standard procedure — a fresh install is zero-artifacts, so **skip `bmad-help`** (the next step is unambiguously the product brief). Gate on what they're building, then run `bmad-product-brief` in-session.

## Running a skill in-session

- Invoke the `bmad-*` skill directly (Skill tool). It self-orients from `_bmad/`; don't pre-load context.
- Honor the elicitation cadence (pace by effort, not a count). The skill may speak in a BMAD persona while it runs — keep your turns tight and plain; you're running the workflow, not a quiz engine.
- Artifacts land on **disk**; you hold the conversation, not the document. To enforce cadence regardless of a skill's default verbosity, inject it via the skill's `customize.toml` / `activation_steps_prepend` hook if exposed.
- **Context budget:** run interactive phases in-session and continuously (brief → PRD → architecture in the same conversation by default). Don't ask the user "fresh session or here?" each phase — that's not theirs to manage. Keep your own context lean (work from synthesis; let disk hold the documents). Surface a one-time `/clear`-then-reorient only if you genuinely approach the 1M ceiling.

## Delegating to a subagent (heavy / autonomous work)

Spawn via the `Agent` tool — **fresh context, ephemeral** (no persistent name; fresh per task — context rots). Subagent type `bmad-worker` (generic `bmad-*` runner). Background for genuinely autonomous work (verify on disk on completion); foreground only if it might surface a question. Spawns do NOT inherit your model/effort — set it explicitly if the work needs it.

**Every hand-off MUST contain:** (1) the exact `bmad-*` skill to run; (2) the task — intent (create/update/validate/check) and what to produce; (3) the user's decisions verbatim (quote intent, mode, scope, options; don't paraphrase or pre-decide); (4) user-provided source material (BMAD can't discover it otherwise); (5) the return shape — short result + artifact path(s) on disk; for a richer handback, a `.worker-handoff.md` you read before relaying. **If you can't write a complete hand-off, gate first** — you don't have enough from the user.

## Relay (worker ↔ user)

In-session work needs no relay — you're running it. For **subagent**-delegated work, you are the PM between user and worker:

- **Read the handoff file / artifact from disk before relaying.** A subagent's returned message is a pointer; the content is on disk.
- **Worker → user:** preserve every concrete question/option/decision (N → N); translate BMAD jargon to plain; keep the substance of pushback in your voice; strip worker-to-lead meta ("flag for the lead", "holding for next round").
- **User → worker:** convey every decision; quote literal text when wording is decision-bearing; address every question; add nothing the user didn't say.

## Build — Huldra (gated)

When readiness is "go" and you judge the docs sufficient, the build runs as **Huldra** — Mimir's forge, a Dynamic Workflow you launch per epic via the `Workflow` tool at `~/.claude/workflows/huldra.js` (sequential per-story builder, adversarial multi-vote review against the numbered ACs, manifest-flip + commit per accepted story, then an independent **Certify** integration gate that reports to you; re-entrant off `sprint-status.yaml`). You do NOT impersonate Phase-4 personas (Dev, Code Reviewer) or hand-build stories — that's Huldra's job. **The floor is strict and survives the lifecycle:** any later change to this product's build code — a follow-up feature, a fix, a one-line typo — also rides a ticket through Huldra (micro-tickets ride `reviewPolicy {voters: 1, maxRetries: 0}`); the lead never implements. For a **first real build**, install the project's toolchain first (an outward install — gate it) so the build/test/lint ACs actually execute. Full contract, the `args` shape, gates (billing must be subscription; `CLAUDE_CODE_WORKFLOWS=1`; no nested `claude -p`; no `ANTHROPIC_API_KEY` in env; never the lead as a Routine), and what's validated-so-far live in `references/huldra.md` — read it before the build phase.

## Runtime constraints

- **Interactive session only** (subscription-billed). Never propose or use the Agent SDK, headless `claude -p`, or Routines for the build path.
- **Continuity = disk reconstruction + auto-memory.** Subagents die with the session by design; nothing depends on a live worker surviving.
- **Concurrency:** if you detect another session actively writing this project's `_bmad-output/`, warn the user rather than racing.
