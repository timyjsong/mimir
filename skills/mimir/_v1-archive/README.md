# mimir — README (maintainer / calibration guide)

> **This file is for humans and maintenance sessions, not runtime.** When `/mimir` runs, Claude Code loads `SKILL.md` (the operating spec). This README is the "why it's built this way + what we verified" companion — read it to calibrate before editing the skill, and keep it current as the design evolves.

## What mimir is

mimir is the **lead** of a Claude Code Agent Teams orchestration that drives a [BMAD-METHOD v6](https://github.com/bmad-code-org/BMAD-METHOD) project across its full lifecycle — Analysis → Planning → Solutioning → Implementation Readiness — and, when ready, hands off to **loki** for autonomous build (Phase 4).

The defining metaphor: **mimir is the PM**. The user is the client; the workers are the engineering team. mimir never runs BMAD/loki workflows itself — it gates conversation with the user, decides what to do next (as a thinking partner, not a request router), and delegates each workflow to a fresh worker. It translates between the user's casual register and the workers' structured/BMAD-voice register.

Named after the Norse counsel figure — the posture is advisory, not order-taking.

## Architecture at a glance

```
        user  ◄──────────►  mimir (LEAD)  ◄── SendMessage ──►  workers (subagents)
                            = your session,                      = bmad-worker / loki-worker,
                              running SKILL.md                      spawned per workflow
                                   │
                                   ▼
                    disk = source of truth
        _bmad/ config · _bmad-output/ artifacts · decision logs · .worker-handoff.md · .mimir-notes.md
```

- **Lead** = the session you talk to (the one running the skill). Not a subagent. Runs only `bmad-help` directly; delegates everything else.
- **Workers** = subagents spawned via the `Agent` tool, addressed via `SendMessage`. Two types: `bmad-worker` (any `bmad-*` workflow) and `loki-worker` (Phase 4 build).
- **Disk is truth.** Conversation is ephemeral; workers don't survive a session. Every restart re-orients from disk.

## File map

| Path | Audience | Loaded when | Purpose |
|------|----------|-------------|---------|
| `SKILL.md` | the lead (mimir) | at `/mimir` invocation | Runtime orchestration spec |
| `references/install-bmad.md` | lead | BMAD-not-installed case | Install procedure + no-restart flow |
| `references/status-examples.md` | lead | unusual status-header states | Status block patterns |
| `references/example-walkthrough.md` | maintainers | on demand | Illustrative full-lifecycle trace (unreferenced) |
| `playbooks/bmad.md` | lead | before each BMAD delegation | How to delegate to `bmad-worker` |
| `playbooks/loki.md` | lead | before build delegation | How to delegate to `loki-worker` |
| `~/.claude/agents/bmad-worker.md` | the bmad-worker subagent | at each spawn | Worker's identity, comms protocol, scope |
| `~/.claude/agents/loki-worker.md` | the loki-worker subagent | at each spawn | Same, + model config (Opus 1M + xhigh) |

**Audience split is deliberate**: `agents/*.md` are loaded into the *worker's* context (its system prompt); `playbooks/*.md` are read by the *lead* to know how to delegate. Same worker type, two docs, two readers. Don't merge them — each party would inherit the other's irrelevant instructions.

## Core design decisions (and why)

- **PM layer / advisory discipline.** mimir thinks and recommends; it doesn't just route. It cites both BMAD's recommendation and its own (with reasoning) and surfaces divergence. Rationale: mimir has asymmetric context (the conversation, cross-workflow signal) that `bmad-help` (disk-only) lacks.
- **One generic `bmad-worker`, not per-role specs.** Originally there were 6 specialized worker docs; collapsed to one. BMAD skills self-orient from `_bmad/`, so we don't pre-encode per-workflow context. Mode (persistent/ephemeral, fg/bg) is judged at delegation time from `bmad-help` + the skill's nature — **no hardcoded skill→mode table to maintain.**
- **`loki-worker` is separate** (distinct subagent type + heavier model config). Phase 4 build is qualitatively different; fresh-per-epic to avoid context rot.
- **Handoff file pattern.** Worker SendMessages are short pointers; rich content (questions, options, relay guidance) goes to `<run-dir>/.worker-handoff.md`. Keeps the user's chat clean (the original problem) while preserving fidelity for the lead to translate. Overwrite each round; bulk-cleaned at loki transition / project teardown (not at each retirement).
- **Latest-invocation-wins concurrency** (not last-active-wins). The newest `/mimir` claims "latest" once at startup; superseded sessions halt and inform the user — they never reclaim/flip. Rationale: last-active-wins caused costly re-orient churn and fought the kill-old-session lever. Latest-wins makes a superseded session a clean dead-end.
- **Disk reconstruction, never worker sharing.** Workers can't be shared/adopted across sessions (verified). Continuity comes from `bmad-help` + decision logs + handoffs + the notes marker.
- **Gated SIGTERM memory reclaim.** In the user's auto/bypass mode, `kill -TERM <pid>` (target by `--resume <session-id>`) is the one programmatic lever to free a stale session's RAM — offered, never silent; non-destructive (session reopens fine).
- **Explicit model config.** `bmad-worker` and `loki-worker` both `model: opus[1m]` + `effort: xhigh`. Explicit because spawns do NOT inherit the lead's model/variant (verified — a spawn under a 4.8[1m] lead came out base 4.7). `opus` alias tracks the latest Opus → no version maintenance.
- **No hard scope boundary.** mimir advises at runtime whether more planning is warranted vs. ready for loki. (loki isn't implemented yet — mimir says so at the inflection.)

## Verified facts (empirically tested this build — trust these; don't re-investigate)

These cost real investigation. They're true for the Claude Code GUI / `ccd-cli` + daemon environment.

- **Workers are in-process** (`backendType: in-process`, no separate PID). They die with their lead session. You cannot kill/free a worker independently of its lead.
- **One team per session** (hard platform constraint). A session leads exactly one team.
- **No cross-session worker addressing.** Even with both sessions alive, SendMessage is gated to your own team; a worker in another session's team is unreachable. (Tested twice in GUI.)
- **No worker adoption.** Only `TeamCreate`/`TeamDelete` tools exist (no join/adopt). Same-name `TeamCreate` errors "already exists." In-process execution can't be re-pointed via files.
- **`TeamDelete` is self-scoped** — only deletes your own session's team. Taking over another session's stale team requires filesystem `rm -rf ~/.claude/teams/<name>` (+ `tasks/`).
- **Team config is ephemeral** — Claude Code auto-removes `~/.claude/teams/<name>/config.json` when the leading session dies. So a dead prior session usually leaves no collision.
- **Spawns don't inherit the lead's model/variant** → explicit `model:` frontmatter is required to guarantee Opus + 1M.
- **`effort` is the reasoning field** (`low|medium|high|xhigh`; `xhigh` = max). `maxThinkingTokens` is deprecated. `--effort` is a real CLI flag too.
- **`archive_session` is blocked in auto/bypass (unsupervised) mode** — returns "unavailable in unsupervised mode" even if an approval panel is clicked. NOT escapable by spawning a `mode: default` worker (the block is session-level) nor by self mode-switch (there is no agent-callable `SetPermissionMode`).
- **`kill -TERM <pid>` works and is non-destructive** — frees a session's RAM (~250-320MB each), daemon does NOT respawn it, and the session reopens cleanly on access. Available from any permission mode (it's Bash).
- **The daemon reaps settled *background* workers under memory pressure** (observed in `daemon.log`), but NOT an interactive session's in-process teammates.
- **Each ccd-cli session ≈ 250-320MB RSS** (lead + its in-process teammates).
- **Workers re-scan `.claude/skills/` at spawn** — a worker spawned right after a mid-session BMAD install has the new skills even though the lead doesn't. This is what lets the install flow proceed without a restart.
- **Team tools are deferred** — must `ToolSearch "select:TeamCreate,Agent,SendMessage"` before first use. And `TeamCreate` will loop (and can crash via an interleaved-thinking API error) if retried on "already exists" — call it once.
- **Project memory path**: Claude Code stores per-project memory at `~/.claude/projects/<cwd-with-/-as->/memory/MEMORY.md` (e.g. `/home/tim/drafts/automation` → `-home-tim-drafts-automation`). Distinct from mimir's `_bmad-output/.mimir-notes.md`.

## Known unknowns / validate-on-first-use

- **`opus[1m]` alias+variant syntax** — assumed valid for "latest Opus, 1M context." If a spawn errors, fall back to a pinned `claude-opus-4-8[1m]` or bare `opus` (default context).
- **`effort: xhigh` in agent frontmatter** — `effort` is a confirmed field/flag, but its exact frontmatter behavior for subagents wasn't load-tested. Verify on first loki spawn.
- **Persistent + background spawn for loki** — the combo (named, addressable, `run_in_background: true`) is assumed; validate when loki ships.
- **`TeamDelete` from inside the team** — used at teardown/rebuild; defensive fallback (tell user to exit + re-invoke) is in SKILL.md if it errors.
- **Interactive-session idle reaping by the daemon** — unconfirmed whether an idle-but-open GUI session is reaped (background ones are). Doesn't affect the design (gated kill + manual archive cover it).
- **loki is not implemented yet.** `loki-worker` exists as a spawn target; spawning it today is a no-op. Revisit `playbooks/loki.md` + `agents/loki-worker.md` assumptions when loki ships.

## Maintenance guide

- **Editing worker behavior** (worker docs / subagent definitions): changes apply on the next worker spawn, or after a `rebuild team`. No full restart needed.
- **Editing SKILL.md** (lead behavior): a running session won't pick it up — the user must `/clear` + `/mimir` to reload. (Worker-doc changes hot-apply; lead-spec changes don't.)
- **New BMAD skills shipping**: handled automatically — mimir judges mode from `bmad-help` + the skill's nature. No table to update.
- **When loki ships**: update `playbooks/loki.md` (the "not yet implemented" notes + the assumed flow) and `agents/loki-worker.md` (capability check, per-story loop). Re-verify the persistent+background spawn combo.
- **Renames**: `agents/*.md` filenames must equal the `subagent_type` string (Claude Code convention). `playbooks/`, `references/` filenames are free.
- **Keep this README current.** When a design decision changes or a "known unknown" gets verified, update the relevant section here so the next session calibrates correctly instead of re-deriving.

## Prerequisites

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set at startup (mimir checks for the team tools and stops if absent).
- Working directory is the project root (contains or will contain `_bmad/`).
- mimir runs on whatever model the user launches it with; the user runs it on Opus 1M / high-effort by default.
