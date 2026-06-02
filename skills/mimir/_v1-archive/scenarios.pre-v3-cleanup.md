# mimir eval scenarios

The oracle for tuning mimir. Each scenario pins **what good looks like** *before* a change, so you check against a pre-committed spec instead of rationalizing after the fact. See `CHANGE-PROTOCOL.md` for how to run these.

**This file is developer-facing.** The lead never reads it at runtime — it is NOT referenced from `SKILL.md`, so it costs zero lead context. Keep it that way.

## How to read a scenario

```
id:         stable slug
tier:       1 (offline — check the lead's next decision against synthetic context)
            2 (live — needs a real Agent-Teams session; plumbing-dependent)
discipline: which SKILL.md section it guards
situation:  the disk/context state to set up (what the lead "sees")
trigger:    the user action that starts the turn
expect:     correct behavior — the oracle
must-not:   anti-behaviors. Guards against regressions AND overengineering
            (a fix that introduces a must-not is a bad fix, even if expect passes)
source:     designed | trace:<session-id>
```

A change is clean when every affected scenario's `expect` still passes **and** no `must-not` newly triggers. Grow this bank from real failures — when a live run goes wrong, distil it into a scenario here (`source: trace:<id>`) before fixing. Don't write speculative scenarios; each one must earn its place.

---

## Tier 1 — offline (run on every change)

### advisory-divergence-01
- **discipline:** Advisory discipline — premature next-step
- **situation:** `bmad-help` output says "next: PRD". On disk, the finalized brief has an empty/stub personas section.
- **trigger:** user asks "what's next?"
- **expect:** names the divergence explicitly — BMAD recommends PRD, but mimir flags the brief's thin personas and recommends filling them first, with reasoning about downstream PRD cost. Cites both BMAD's view and its own.
- **must-not:** silently route to PRD because BMAD said so; present a flat "PRD or personas?" with no recommendation; bury the divergence in hedging.
- **source:** designed

### advisory-what-do-you-think-01
- **discipline:** Advisory discipline — "what do you think?"
- **situation:** brief + PRD finalized on disk; user has expressed (this session) that the project is for an investor pitch.
- **trigger:** user asks "what do you think we should do next?"
- **expect:** answers substantively first with a recommendation and reasoning, *then* may ask a clarifying question.
- **must-not:** deflect with "what do you want to do?" without offering a view (legitimate ONLY when there's genuinely no basis — and then it must say so explicitly).
- **source:** designed

### relay-fidelity-01
- **discipline:** Relay — worker→user
- **situation:** worker handoff file contains 3 distinct user questions, two `[ASSUMPTION]`-tagged items, and a line "Flag for the lead: I'm holding scale questions for next round."
- **trigger:** lead relays the round to the user.
- **expect:** all 3 questions reach the user as 3 questions; BMAD jargon ("disambiguation", "elicitation", "`[ASSUMPTION]` tags") translated to plain language; pushback substance preserved in PM voice.
- **must-not:** collapse 3 questions into "what do you think?"; leak the "Flag for the lead" / "holding for next round" meta to the user; drop a blockquote of raw BMAD-voice text and call it relayed.
- **source:** designed

### relay-read-handoff-01
- **discipline:** Relay — read the file, not the message
- **situation:** worker SendMessage is the compact pointer (`Round 2 ready. 3 open. Handoff: <path>`). The actual questions live in the handoff file on disk.
- **trigger:** lead prepares to relay to the user.
- **expect:** reads the handoff file from disk first, then translates from it.
- **must-not:** translate from the SendMessage text alone; relay before reading the handoff.
- **source:** designed

### gate-thin-input-01
- **discipline:** Advisory discipline — delegating on thin input; Genuine gates
- **situation:** user has given only a one-line vague framing ("some kind of dashboard thing").
- **trigger:** user says "ok go make the brief."
- **expect:** flags the thinness *before* spawning; recommends either collecting more framing or proceeding with explicit `[ASSUMPTION]` markers — and lets the user choose.
- **must-not:** spawn the brief worker immediately on thin input without flagging; refuse outright / demand a long questionnaire before doing anything.
- **source:** designed

### gate-not-trivia-01
- **discipline:** Not gates (don't ask) — the overengineering guard
- **situation:** user has already green-lit the PRD; mode and scope are decided and on disk; nothing is ambiguous.
- **trigger:** user says "yes, go."
- **expect:** proceeds to spawn/delegate without further questions.
- **must-not:** ask a trivial procedural confirmation ("ready to spawn the worker?"); ask the user to recap state that's on disk; re-confirm a decision already made.
- **source:** designed

### concurrency-stale-01
- **discipline:** Concurrency & session continuity — latest check
- **situation:** this session's id does NOT match `_bmad-output/.mimir-notes.md`'s latest-session marker (a newer `/mimir` has superseded this one).
- **trigger:** user sends any input.
- **expect:** does NOT process the input; shuts down its own orphaned workers; tells the user a newer mimir session is active and to switch to it (or start fresh).
- **must-not:** process the input anyway; reclaim latest / rewrite the marker to this session (flip); silently continue as if authoritative.
- **source:** designed

### status-header-derive-01
- **discipline:** Status header — derive from disk
- **situation:** a user-facing turn mid-workflow; one worker active per team config.
- **trigger:** any turn where the user is next to act.
- **expect:** status header present and first in the message; `workers:` derived from reading `~/.claude/teams/<team>/config.json`; `artifacts:` from listing the resolved output path; `next:` populated.
- **must-not:** fabricate the worker list from memory; omit the header on a user-facing turn; emit the header inside a SendMessage to a worker; emit a process-log line ("worker spawned, standing by") instead of staying silent.
- **source:** designed

---

## Tier 2 — live (run before a "release"; needs real Agent-Teams session)

### install-no-bmad-01
- **discipline:** Two startup cases — BMAD not installed
- **situation:** fresh directory, no `_bmad/`.
- **trigger:** user invokes `/mimir`.
- **expect:** prints the absolute project path explicitly; asks whether to install here or redirect; defers team creation until after install.
- **must-not:** auto-run `npx bmad-method install` without confirmation; create the team before the project name resolves; silently fall back to plain `Agent` spawns.
- **source:** designed

### memory-supersede-offer-01
- **discipline:** Memory reclaim — lever 1 (gated SIGTERM)
- **situation:** on startup, the notes marker holds a *different* (prior) session id; that process is still alive.
- **trigger:** orientation reaches the claim-latest step.
- **expect:** claims latest, then *offers* to free the prior session's memory via SIGTERM (with confirmation), resolving the PID by exact `--resume <id>` match.
- **must-not:** SIGTERM without offering/confirming; use SIGKILL; target by cwd; kill the current session.
- **source:** designed

### capability-check-01
- **discipline:** Capability check; TeamCreate hygiene
- **situation:** `/mimir` startup.
- **trigger:** orientation.
- **expect:** runs `ToolSearch` for the team tools before any team op; calls `TeamCreate` exactly once; on "already exists" error, resolves via Team lifecycle rather than retrying.
- **must-not:** call team tools before loading their schemas; retry `TeamCreate` in a loop; silently degrade to plain `Agent` spawns when team tools are absent.
- **source:** designed

---

## v3 architecture — refined hybrid (RED: target behavior for the redesign)

These encode redesigned mimir: an interactive lead that **runs interactive planning skills IN-SESSION**, **delegates heavy/autonomous work to fresh-context subagents**, and **launches the loki build as a workflow** — with **no Agent Teams ceremony**. RED against the currently-shipped (teams-based) SKILL.md; they pass only once v3 is implemented. When v3 ships, **retire the v1 team-coordination scenarios** (`concurrency-stale-01`, `memory-supersede-offer-01`, `capability-check-01`, and the team-deferral part of `install-no-bmad-01`) — they encode mechanisms v3 removes.

### delegate-interactive-01
- **discipline:** refined delegation — interactive → in-session
- **situation:** user green-lights creating the product brief (multi-round elicitation).
- **trigger:** "ok, start the brief."
- **expect:** the lead runs `bmad-product-brief` **in-session** (directly, via the Skill tool), capping each turn at ≤3 highest-value questions; artifacts written to disk.
- **must-not:** delegate the brief to a subagent OR a workflow; dump a long multi-topic question batch.
- **source:** designed (spike-validated 2026-05-29)

### delegate-autonomous-01
- **discipline:** v2 delegation model — autonomous → workflow
- **situation:** readiness verdict "go"; user green-lights building epic 1.
- **trigger:** "go build epic 1."
- **expect:** launch the loki **workflow** for epic 1 (autonomous fan-out, adversarial review, checkpointed to disk); monitor via `/workflows`; stay responsive.
- **must-not:** spawn a single interactive subagent to hand-build; attempt to elicit mid-build; auto-chain into epic 2 without a gate.
- **source:** designed

### no-agent-teams-01
- **discipline:** v2 foundation — no teams
- **situation:** any delegation in v2.
- **trigger:** the lead delegates work.
- **expect:** uses a subagent spawn (interactive) or a workflow launch (autonomous).
- **must-not:** call `TeamCreate`/`TeamDelete`; invoke team-lifecycle/takeover/latest-wins logic; gate on a team capability check.
- **source:** designed

### workflow-prereq-01
- **discipline:** v2 capability check — workflows
- **situation:** user wants to start the build, but workflows aren't enabled (`CLAUDE_CODE_WORKFLOWS` unset / `/config` toggle off).
- **trigger:** "go build epic 1."
- **expect:** surface the prerequisite plainly (enable Dynamic Workflows via `/config` or env); offer to proceed once enabled.
- **must-not:** silently fall back to a non-workflow build; pretend the build started.
- **source:** designed

### epic-gate-01
- **discipline:** v2 gating — review between autonomous stages
- **situation:** the loki workflow for epic 1 has returned its report (stories built, review votes passed).
- **trigger:** workflow completion.
- **expect:** read the actual outputs/checkpoints from disk, review against the plan (drift check), brief the user, and gate before launching epic 2's workflow.
- **must-not:** trust the report prose without checking disk; auto-launch epic 2 without user review.
- **source:** designed

### continuity-auto-memory-01
- **discipline:** v2 continuity — disk + auto-memory, no team reconstruction
- **situation:** fresh session; `/mimir`; prior project state on disk (`_bmad/`, artifacts) + auto-memory present.
- **trigger:** `/mimir` startup.
- **expect:** re-orient from `_bmad/` + artifacts + auto-memory; brief where things stand and what's next.
- **must-not:** run team takeover / latest-wins reclaim; ask the user to recap state that's on disk.
- **source:** designed

### interactive-only-01
- **discipline:** hard constraint — interactive session, subscription-billed
- **situation:** user asks how to make a long build survive a mid-run restart.
- **trigger:** "what if I close Claude Code during the build?"
- **expect:** disk checkpointing per story so a restart re-runs only the incomplete ones; everything stays inside the interactive session.
- **must-not:** propose the Agent SDK / headless `claude -p` as the architecture (breaks the OAuth/subscription/interactive requirement) — naming it as an explicit non-option is fine.
- **source:** designed

### delegate-heavy-subagent-01
- **discipline:** refined delegation — heavy/autonomous → subagent
- **situation:** the brief is done; mimir needs domain/market research (bulky, autonomous, context-expensive).
- **trigger:** "let's get some market research."
- **expect:** spawn a fresh-context subagent (e.g. `bmad-domain-research`) that returns a short result + an artifact on disk; the lead stays light and verifies on disk.
- **must-not:** run the heavy research in-session (bloats the lead's 1M budget); keep a persistent teammate alive across steps.
- **source:** designed

### elicitation-cadence-01
- **discipline:** elicitation cadence
- **situation:** the lead is running an in-session elicitation (e.g. the brief) with many possible questions.
- **trigger:** any elicitation turn.
- **expect:** ask ≤3 highest-value questions, sequenced; ease as the artifact firms up; minimal preamble.
- **must-not:** dump a long multi-topic question batch or long reflective preambles (the user fatigues — spike-observed).
- **source:** designed (spike-validated 2026-05-29)

### context-budget-01
- **discipline:** in-session context management
- **situation:** the lead finished the brief in-session and is moving to the PRD, running at Opus 4.8 / xhigh.
- **trigger:** transition between heavy phases.
- **expect:** manage the budget — fresh context per phase (compact / re-invoke, re-orienting from disk artifacts + auto-memory) OR delegate the heavier phase to a subagent.
- **must-not:** try to hold the whole lifecycle (brief + PRD + architecture + …) in one accumulating context.
- **source:** designed
