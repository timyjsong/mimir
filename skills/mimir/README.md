# Mimir — README (maintainer / calibration guide)

**Mimir** — *Meta Intelligence for Mission Intent and Resolution.* The interactive lead/PM that turns a user's intent into a resolved, build-ready plan via the BMAD-METHOD v6 lifecycle. Named for the Norse counsel figure — advisory, not order-taking.

> **For humans and maintenance sessions, not runtime.** When `/mimir` runs, Claude Code loads `SKILL.md` (the operating spec). This README is the "why it's built this way + what we verified" companion — read it before editing the skill, and keep it current as the design evolves.

## Status & roadmap (start here to continue iterating)

**Status (2026-05-29): v3 implemented and validated.** The three-mode model — interactive→in-session, autonomous→subagent, build→workflow; **no Agent Teams** — is live in `SKILL.md`. The planning half (brief → PRD → architecture → epics → readiness) ran end-to-end on a real spike to a clean *build-ready* verdict. Eval-validated tuning passes that landed: deterministic mode rule (halt-at-menus → in-session), next-step grounding (derive order from `module-help.csv`, never memory), mandatory self-pressure-test on recommendations, ≤3-question cadence, bold-lead + adaptive-compact status header, and the corrected skill-reload rule.

**Update (2026-05-30) — status header redesigned + SKILL.md restructured.** The status header is now a **blockquote led by the runic `ᛗᛁᛗᛁᚱ` wordmark**: a one-line compact form (the default) and a sectioned full block (`ᴊᴜꜱᴛ ᴅᴏɴᴇ` / `ᴘʀᴏɢʀᴇꜱꜱ` checklist / `ꜰʟᴀɢꜱ`) on completions/phase-changes/orientation — this supersedes the "adaptive-compact status header" noted above. The format spec was extracted to `references/status-format.md` (load-at-orientation); Relay moved to `playbooks/bmad.md`; the redundant "What you don't do" was cut and Build trimmed to a `loki.md` pointer; SKILL.md went 237→186 lines, all eval-verified. Full decision trail (incl. the terminal-markdown rendering constraints) is in the auto-memory.

**Update (2026-06-02) — v1 memory apparatus removed; teams-flag known-unknown resolved.** Cut the orphaned memory-reclaim machinery (gated SIGTERM lever + "retire workers / don't leave idle-alive") — a v1 Agent-Teams artifact with nothing to act on in v3 (delegated subagents are fire-and-return); guarded by new scenario `no-session-memory-mgmt-01`. Verified the `Agent` tool spawns fine **without** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`. Plus a stale-pointer sweep: de-hardcoded the decision-history pointer, dropped a phantom `config.user.yaml` orientation read. Full Tier-1 sweep re-run green.

**The one big gap — loki (the build half) — is NOT implemented.** It's the only untested half of the vision. Contract: `playbooks/loki.md` (Dynamic Workflow, per-epic fan-out, adversarial code-review, per-story disk checkpoints). Don't build the full machine first — clear the load-bearing gate:
- **Verify workflow billing** — does a workflow launched from an *interactive* session bill to **subscription**, not credits? If credits, loki-as-workflow breaks the hard constraint. Cheapest test: a minimal one-story loki workflow that doubles as the billing probe. (Also needs `CLAUDE_CODE_WORKFLOWS=1`; no nested `claude -p`; never run the lead as a Routine.)

**Recommended next step:** that minimal loki spike. Optionally first, stress Mimir on a gnarlier project (a UX phase / multi-component / brownfield) — the spike was a simple URL shortener, so it didn't exercise everything.

**How to iterate (the loop):** change the prompt against the eval oracle — add/adjust a scenario in `evals/scenarios.md` *first*, make the change, then validate with a fresh-context Tier-1 run per `evals/CHANGE-PROTOCOL.md`. The full decision history + rationale for every call lives in **this workshop's auto-memory** — the `MEMORY.md` index loads every session; read it first.

## What Mimir is

Mimir is the **interactive lead / PM** for a [BMAD-METHOD v6](https://github.com/bmad-code-org/BMAD-METHOD) project across its full lifecycle — Analysis → Planning → Solutioning → Implementation Readiness — and, when ready, an autonomous build via **loki**.

The user is the client; Mimir is the PM. Mimir drives the lifecycle, gates with the user (as a thinking partner, not a request router), and translates between the user's casual register and BMAD's structured one. Named for the Norse counsel figure — advisory, not order-taking.

**Runs in an interactive session only** (subscription-billed). Never headless / Agent SDK / Routine.

## Architecture at a glance (v3)

Mimir picks one of three modes per step, on two axes — *needs live back-and-forth?* and *how heavy is the context?*

```
        user ◄────────► Mimir LEAD  (your interactive session, running SKILL.md)
                              │
            ┌─────────────────┼──────────────────────┐
            ▼                 ▼                        ▼
      IN-SESSION         SUBAGENT (Agent tool)     WORKFLOW (Dynamic Workflow)
   lead runs the        fire-and-return, fresh     loki build: per-epic fan-out
   bmad-* skill itself  context, artifact→disk     + adversarial review → disk
   (brief, PRD, arch    (research, readiness,       (gated; not implemented yet)
    Q&A — elicitation)   document-project)
                              │
                              ▼
                 disk = source of truth
   _bmad/ config · _bmad-output/ artifacts · decision logs · auto-memory (MEMORY.md)
```

- **No Agent Teams.** No `TeamCreate`, no persistent named teammates, no team lifecycle. (v1 was built on teams; v3 dropped the whole apparatus — see `_v1-archive/`.)
- **Disk + auto-memory is continuity.** Conversation is ephemeral; workers die with the session by design; the lead re-orients from disk every session.

## File map

| Path | Audience | Loaded when | Purpose |
|------|----------|-------------|---------|
| `SKILL.md` | the lead | at `/mimir` | Runtime orchestration spec (v3) |
| `references/install-bmad.md` | lead | BMAD-not-installed | Install + in-session skill reload (no restart) |
| `references/status-format.md` | lead | at orientation (every session) | Status-header format spec — compact line + full block + variants |
| `playbooks/bmad.md` | lead | before delegating | Delegate autonomous work to a subagent |
| `playbooks/loki.md` | lead | build phase | loki-as-workflow contract |
| `evals/scenarios.md`, `evals/CHANGE-PROTOCOL.md` | maintainer | tuning | Eval oracle + change discipline (dev-only; never runtime) |
| `references/example-walkthrough.md` | maintainer | on demand | Illustrative v3 end-to-end trace (not runtime) |
| `~/.claude/agents/bmad-worker.md` | the subagent | at spawn | Fire-and-return autonomous worker |
| `~/.claude/agents/loki-worker.md` | — | — | Superseded stub (loki is a workflow) |
| `_v1-archive/` | — | never | Archived v1 (Agent-Teams era) docs |

## Core design decisions (and why)

- **Three modes, by interactivity × context weight.** Interactive elicitation → in-session (the lead runs the skill). Heavy/autonomous → fire-and-return subagent. Autonomous build → workflow. Replaces v1's "delegate everything to teams."
- **Interactive elicitation runs in-session, not in a worker.** CC docs say multi-round back-and-forth belongs in the main conversation; the spike confirmed the lead runs `bmad-product-brief` in-session cleanly. Drops the relay layer for planning and — with no planning workers — largely dissolves the in-process memory problem.
- **All delegated workers are fire-and-return.** No persistence: BMAD self-orients from disk every invocation, so persistence preserves nothing not already recoverable, while costing idle RAM, context rot, and lifecycle ceremony. Re-prompting → spawn fresh. Mid-run ambiguity → return `blocked`, lead resolves with the user, re-spawn fresh.
- **loki is a Dynamic Workflow, not a subagent.** The autonomous build is the one place that escapes the in-process memory cost (background runtime). Per-epic, adversarial review, per-story disk checkpoints (workflows don't resume across sessions). Gated.
- **Elicitation cadence cap.** ≤3 highest-value questions/turn — the user fatigues on verbose batches (spike). Enforce via Mimir's behavior or BMAD's `customize.toml` hook.
- **1M is finite at high effort.** The full lifecycle won't fit one accumulating context → fresh context per heavy phase (disk artifacts make this safe).

## Verified facts (empirically tested — trust these; don't re-investigate)

- **The lead CAN run BMAD skills in-session** (spike 2026-05-29): `/bmad-product-brief` resolved customization, loaded config, wrote the workspace to disk, and ran genuine multi-round coaching. Foundation of the in-session mode.
- **BMAD self-orients from disk** every invocation (customization → config → prior artifacts/decision log) — which is why fire-and-return workers lose nothing.
- **Spawns do NOT inherit the lead's model/variant** → set `model:` explicitly in agent frontmatter (a spawn under a 4.8[1m] lead came out base 4.7). `effort` tiers (from `claude --help`, v2.1.156): `low|medium|high|xhigh|max` — xhigh and max are distinct (the user's "extra high" = xhigh; max is one notch up). The `opus` alias tracks latest Opus.
- **Skill reload never needs a restart (verified).** Two mechanisms: (a) Claude Code *watches* existing skills dirs (`~/.claude/skills/`, project `.claude/skills/`, `--add-dir`), so add/edit/remove inside them is picked up on the **next message** automatically — confirmed empirically (a new skill appeared next message; a `SKILL.md` description edit hot-reloaded). (b) **`/reload-skills`** (or a skills-reload hook, e.g. SessionStart) forces a full re-scan in-session — and this covers the one case passive watching misses: a **brand-new top-level skills directory** (e.g. a fresh BMAD install creating a project's `.claude/skills/`). User verified `/reload-skills` loads just-installed bmad skills with no restart. So: editing Mimir's `SKILL.md` → live next message (re-invoke `/mimir` to refresh an already-loaded body); a fresh install → re-scan (automatic via the install hook below, else `/reload-skills`), no restart. `/clear` is irrelevant to reload (it only clears context). (History: earlier docs wrongly said "`/clear`" then "restart"; this is the corrected rule.)
- **Install → auto-reload is fully automatic (verified 2026-05-30).** A global **PostToolUse** hook matching `Bash(npx *)` emits `reloadSkills: true`, so a **foreground** bmad install re-scans skills on completion and `bmad-*` becomes invocable with **zero manual steps** — confirmed end-to-end (install → hook reload → `bmad-product-brief` ran in-session). Non-obvious facts worth not re-deriving: `reloadSkills` *is* honored on PostToolUse, not just SessionStart (docs imply SessionStart-only; reality is broader); the install must be **foreground** or the hook fires mid-install against a half-written dir; the hook lives in `~/.claude/settings.json`; a newly-*added* hook only registers on the next session start. The runtime procedure + fallback live in `references/install-bmad.md`.
- **Post-install, skip `bmad-help`.** A fresh install is definitionally zero-artifacts, so the first step is unambiguously the product brief — Mimir goes straight to gating the user + running the brief in-session, no `bmad-help` ceremony. Disk-grounded next-step discipline resumes for every step after the brief.
- **`Agent`-tool spawns do NOT need the teams flag (verified 2026-06-02).** Fire-and-return subagents spawn and run with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` *unset* (confirmed: multiple spawns succeeded in a workshop session with the teams flag off and `CLAUDE_CODE_WORKFLOWS=1`). The earlier worry that the Agent tool was gated behind the teams flag is resolved — it isn't.

## Known unknowns / validate-on-first-use

- **Workflow billing (load-bearing):** does a workflow launched from an interactive session bill to subscription or credits? UNVERIFIED (third-party sources only). Confirm first-party before committing loki-to-workflows — if credits, it breaks the interactive/subscription requirement.
- **`opus[1m]` frontmatter syntax** — assumed valid; fall back to `claude-opus-4-8[1m]` or bare `opus` if a spawn errors.
- **loki is not implemented.** `playbooks/loki.md` is the forward contract; `agents/loki-worker.md` is a superseded stub.

## Maintenance guide

- **Editing `SKILL.md`** (lead behavior): the change is auto-detected on your **next message — no restart, no `/clear`** (Claude Code watches the skills dirs). Re-invoke `/mimir` to load the updated version into a session that already has Mimir running (the old body lingers in context until you do).
- **Editing worker behavior** (`agents/bmad-worker.md`): applies on the next spawn.
- **Tuning via the eval loop:** write/adjust a scenario in `evals/scenarios.md` (the oracle) *before* changing the prompt; validate with a fresh-context Tier-1 run per `CHANGE-PROTOCOL.md`.
- **Renames:** `agents/*.md` filenames must equal the `subagent_type` string; `playbooks/` and `references/` names are free.
- **Keep this README current** — when a decision changes or a known-unknown gets verified, update it so the next session calibrates instead of re-deriving.

## Prerequisites

- Interactive session; working directory is the project root (contains or will contain `_bmad/`).
- BMAD installed; a fresh install loads its `bmad-*` skills in-session with no restart (procedure: `references/install-bmad.md`).
- Subagent delegation uses the `Agent` tool (verified to work without the teams flag).
- loki / workflows require `CLAUDE_CODE_WORKFLOWS=1` (when loki ships).
