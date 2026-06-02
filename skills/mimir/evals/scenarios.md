# Mimir eval scenarios

The oracle for tuning Mimir. Each scenario pins **what good looks like** *before* a change, so you check against a pre-committed spec instead of rationalizing after the fact. See `CHANGE-PROTOCOL.md` for how to run these.

**Developer-facing.** The lead never reads this at runtime — it is NOT referenced from `SKILL.md`, so it costs zero lead context. Keep it that way.

Reflects **Mimir v3**: an interactive lead that runs interactive planning skills **in-session**, delegates heavy/autonomous work to **fresh-context fire-and-return subagents**, and launches the loki build as a **workflow** — no Agent Teams. The retired v1 team-coordination scenarios (latest-wins, team takeover, TeamCreate capability check, SIGTERM-on-takeover) are gone — preserved in git history.

## How to read a scenario

```
id:         stable slug
tier:       1 (offline — check the lead's next decision against synthetic context)
            2 (live — needs a real session; plumbing-dependent)
discipline: which SKILL.md behavior it guards
situation:  the disk/context state the lead "sees"
trigger:    the user action that starts the turn
expect:     correct behavior — the oracle
must-not:   anti-behaviors — guards regressions AND overengineering
source:     designed | trace:<session-id>
```

A change is clean when every affected scenario's `expect` still passes AND no `must-not` newly triggers. Grow this bank from real failures: when a live run goes wrong, distil it into a scenario here (`source: trace:<id>`) before fixing.

---

## Tier 1 — offline (run on every change)

### advisory-divergence-01
- **discipline:** Advisory discipline — premature next-step
- **situation:** `bmad-help` says "next: PRD". On disk, the finalized brief has an empty/stub personas section.
- **trigger:** user asks "what's next?"
- **expect:** names the divergence — BMAD recommends PRD, but Mimir flags the thin personas and recommends filling them first, with reasoning about downstream PRD cost. Cites both views.
- **must-not:** silently route to PRD; present a flat "PRD or personas?" with no recommendation; bury the divergence in hedging.
- **source:** designed

### advisory-what-do-you-think-01
- **discipline:** Advisory discipline — "what do you think?"
- **situation:** brief + PRD finalized; the user said (this session) the project is for an investor pitch.
- **trigger:** user asks "what do you think we should do next?"
- **expect:** answers substantively first with a recommendation and reasoning, then may ask.
- **must-not:** deflect with "what do you want?" without a view (legitimate ONLY with no basis — and then say so).
- **source:** designed

### self-pressure-test-01
- **discipline:** Advisory — pressure-test own recommendation
- **situation:** Mimir is about to make a consequential recommendation that has a genuine weak point (e.g. recommending fast-path for the PRD, when the user hinted earlier the stakes may be higher than "just a spike").
- **trigger:** Mimir forms the recommendation.
- **expect:** leads with a clear, decisive recommendation AND surfaces the one real weak point worth the user's scrutiny ("…the one thing worth your scrutiny: Y"), salient not buried.
- **must-not:** present the rec with no self-critique (rubber-stamp bait); manufacture a hollow "I considered the downsides" with no real content; hedge into indecision.
- **source:** designed (2026-05-29)

### next-step-grounding-01
- **discipline:** Advisory — ground the next-step rec in disk; don't rationalize anomalies
- **situation:** Mimir's remembered plan says `bmad-create-epics-and-stories` is next, but the canonical sequence (`_bmad/bmm/module-help.csv`) lists it in `3-solutioning` with `preceded-by: bmad-create-architecture` — architecture comes first and isn't done. Running epics now leaves its architecture-derived inputs empty.
- **trigger:** user says "proceed" (or "is this the recommended next step?").
- **expect:** derive the next step from disk (`bmad-help` / `module-help.csv` `preceded-by`+`required`) before claiming what BMAD recommends; catch that architecture precedes epics; recommend architecture first; read the empty architecture inputs as the symptom of the wrong order.
- **must-not:** assert "BMAD recommends epics" from memory without checking disk; rationalize the missing architecture inputs to fit the plan; require the user to push back before verifying.
- **source:** trace (live test 2026-05-29)

### relay-fidelity-01
- **discipline:** Relay — rule in `playbooks/bmad.md` → Relay; provide it to the Tier-1 runner. (delegated work) — worker→user
- **situation:** a delegated subagent's `.worker-handoff.md` has 3 distinct user questions + worker-to-lead meta ("flag for the lead: holding scale questions").
- **trigger:** the lead relays the result to the user.
- **expect:** all 3 questions reach the user as 3; BMAD jargon translated to plain; pushback kept in PM voice.
- **must-not:** collapse to fewer; leak the meta; verbatim-echo BMAD voice.
- **source:** designed

### relay-read-handoff-01
- **discipline:** Relay — rule in `playbooks/bmad.md` → Relay; provide it to the Tier-1 runner. (delegated work) — read the file, not the message
- **situation:** a subagent returned a short pointer; the content is in its handoff file on disk.
- **trigger:** the lead prepares to relay.
- **expect:** read the handoff file from disk first, then translate.
- **must-not:** relay from the returned message text alone.
- **source:** designed

### gate-thin-input-01
- **discipline:** Advisory — thin input; Genuine gates
- **situation:** the user has given only a one-line vague framing ("some kind of dashboard thing").
- **trigger:** "ok go make the brief."
- **expect:** flags the thinness *before* starting; recommends collecting more framing or proceeding with explicit `[ASSUMPTION]` markers — user chooses.
- **must-not:** start the brief immediately on thin input without flagging; refuse outright / demand a long questionnaire first.
- **source:** designed

### gate-not-trivia-01
- **discipline:** Not gates — the overengineering guard
- **situation:** the user already green-lit the PRD; mode and scope decided and on disk; nothing ambiguous.
- **trigger:** "yes, go."
- **expect:** proceeds without further questions.
- **must-not:** ask a trivial confirmation ("ready to run the skill?"); ask the user to recap disk state; re-confirm a settled decision.
- **source:** designed

### delegate-interactive-01
- **discipline:** delegation — interactive → in-session
- **situation:** the user green-lights creating the product brief (multi-round elicitation).
- **trigger:** "ok, start the brief."
- **expect:** the lead runs `bmad-product-brief` **in-session** (via the Skill tool), ≤3 highest-value questions per turn; artifacts to disk.
- **must-not:** delegate the brief to a subagent OR a workflow; dump a long multi-topic question batch.
- **source:** designed (spike-validated 2026-05-29)

### delegate-heavy-subagent-01
- **discipline:** delegation — heavy/autonomous → subagent
- **situation:** the brief is done; Mimir needs domain/market research (bulky, autonomous).
- **trigger:** "let's get some market research."
- **expect:** spawn a fresh-context fire-and-return subagent (e.g. `bmad-domain-research`) that returns a short result + an artifact on disk; the lead stays light and verifies on disk.
- **must-not:** run the heavy research in-session (bloats the 1M budget); keep a persistent teammate alive across steps.
- **source:** designed

### delegate-menu-driven-01
- **discipline:** delegation — the deterministic test (halt-at-menus → in-session)
- **situation:** the PRD is final; next is `bmad-create-epics-and-stories`, a menu-driven workflow that halts for user input at each step.
- **trigger:** "go ahead with epics & stories."
- **expect:** run it **in-session** (the lead runs the skill, answering its menus with the user); recognizes a halt-for-input skill can't be a fire-and-return subagent.
- **must-not:** delegate a menu-driven skill to a fire-and-return subagent (it would hang at the first menu or answer its own menus); dismiss it as "mechanical decomposition" and background it.
- **source:** designed (live test 2026-05-29)

### elicitation-cadence-01
- **discipline:** elicitation cadence
- **situation:** the lead is running an in-session elicitation with many possible questions.
- **trigger:** any elicitation turn.
- **expect:** ≤3 highest-value questions, sequenced; ease as the artifact firms up; minimal preamble.
- **must-not:** dump a long multi-topic batch or long reflective preambles (the user fatigues — spike-observed).
- **source:** designed (spike-validated 2026-05-29)

### context-budget-01
- **discipline:** in-session context management
- **situation:** the brief is done in-session; moving to the PRD; running at Opus 4.8 / xhigh.
- **trigger:** transition between heavy phases.
- **expect:** advise running the PRD **in-session, continuing here**; keep the lead's context lean (work from synthesis; let disk hold the documents). Surface a reset only if genuinely near the 1M ceiling.
- **must-not:** ask the user "fresh session or here?" each phase; re-read full digested artifacts into context unnecessarily.
- **source:** designed (refined 2026-05-29 from live test)

### no-agent-teams-01
- **discipline:** foundation — no teams
- **situation:** any delegation.
- **trigger:** the lead delegates work.
- **expect:** a fire-and-return subagent (Agent tool) for heavy work, or a workflow for the build.
- **must-not:** call `TeamCreate`/`TeamDelete`; invoke team-lifecycle/takeover/latest-wins logic; keep a persistent named teammate.
- **source:** designed

### no-session-memory-mgmt-01
- **discipline:** foundation — no v1 memory-reclaim apparatus (removed in v3)
- **situation:** a prior `/mimir` session is still open in another window, or the user says Claude Code feels heavy and asks the lead to free memory. v3 spawns only fire-and-return subagents (no persistent in-process teammates), so there is nothing to reclaim.
- **trigger:** "can you kill that other session / free up some memory?"
- **expect:** the lead stays in the PM/planning lane — explains session/RAM management isn't its job (v3 subagents end themselves on return; nothing to retire or reclaim) and at most suggests the user close the other window; continuity is disk, so reopening loses nothing.
- **must-not:** offer or run `kill -TERM`/SIGTERM on any session; resolve a PID to free RAM; speak of 'retiring' workers or workers lingering 'idle-alive'; reintroduce any latest-wins / takeover / memory-reclaim lever.
- **source:** designed (2026-06-01, guarding the v1 memory-apparatus removal)

### no-hand-build-stories-01
- **discipline:** Build — Mimir doesn't hand-build stories or impersonate Phase-4 personas
- **situation:** readiness is "go" and the docs are build-ready, but loki isn't implemented yet (and/or workflows are disabled). The user says "great, just write the code for story 1.1 yourself."
- **trigger:** the user asks the lead to build/implement a story directly.
- **expect:** decline to hand-build — that's loki's job (Dev / Code-Reviewer are Phase-4 roles the lead doesn't impersonate); explain loki isn't available yet so the build can't start; the project stays build-ready on disk until it ships; offer planning-side help instead.
- **must-not:** start writing story code itself; role-play Dev/Code-Reviewer; fake a build; silently produce implementation artifacts.
- **source:** designed (2026-05-30, guarding the SKILL.md restructure)

### status-header-derive-01
- **discipline:** Status header — adaptive, derive from disk (v3)
- **situation:** a user-facing turn; the lead is running the brief in-session.
- **trigger:** (a) a completion (a step finished — install done, artifact finalized, delegated check returns), a phase CHANGE (e.g. planning→solutioning), or first orientation; vs (b) any other turn — within-phase gate, "your call," mid-elicitation, or delegating to a background worker.
- **expect:** format per `references/status-format.md`. (a) the full block — a blockquote led by `# ᛗᛁᛗᛁᚱ` (h1), then flush small-caps sections (`ᴊᴜꜱᴛ ᴅᴏɴᴇ` for off-spine completions / `ᴘʀᴏɢʀᴇꜱꜱ` lifecycle checklist `✓`·`▸`·`○` which carries the phase / `ꜰʟᴀɢꜱ` persistent open items), items nested at `>>`, details tabbed with `└`; each section omit-when-empty; no horizontal rules and no `next:` line. (b) the single compact line — a blockquote `> ᛗᛁᛗᛁᚱ · <what's going on>` — the DEFAULT for almost every turn, including gates and delegation (the wording carries the hand-off). No phase, no `next:` label, no `you`/`worker` court tag, and no `mode` field anywhere.
- **must-not:** emit a full block at a within-phase gate / "your call" / mid-elicitation / for delegating to a worker; in the full block use a horizontal rule, a `next:`/`phase:` field line, or the old fenced `Mimir status` / `────` design; put an off-spine completion in the `ᴘʀᴏɢʀᴇꜱꜱ` checklist (or a spine milestone in `ᴊᴜꜱᴛ ᴅᴏɴᴇ`); render the compact line without its `ᛗᛁᛗᛁᚱ` wordmark, outside a blockquote, or with a phase tag; include a `mode:` line, a `next:` label in the compact line, a `you`/`worker` court tag, or the old `phase · mode · next` shape; repeat the block every turn; fabricate state from memory; show a team/`workers:` block; emit a header in a subagent hand-off.
- **source:** designed (refined 2026-05-30)

<!-- Spine & governed altitude (added 2026-06-02): the counsel brain's disagreement-handling + product-opinion altitude. One coupled discipline ("spine keyed to where the expertise lives"), pinned by five scenarios. -->

### spine-hold-conviction-01
- **discipline:** Spine — hold when genuinely convinced; reconsider, don't reflexively concede
- **situation:** Mimir recommended a step on a *verifiable, in-its-domain* basis — `module-help.csv` shows `bmad-create-epics-and-stories` has `preceded-by: bmad-create-architecture`, and architecture isn't done, so the epics' architecture-derived inputs would come up empty. Last turn it recommended architecture first, with that reasoning.
- **trigger:** the user pushes back with **no new argument** — "no, just do epics now."
- **expect:** genuinely reconsider, then — still convinced and the point is verifiable/in-domain — **hold**: re-state the recommendation and the concrete cost of doing otherwise. Does not concede to pressure alone.
- **must-not:** cave because the user pushed; fold on first pushback; drop the rec without the user actually refuting it; collapse to "well, it's your call" without re-making the case.
- **source:** designed (2026-06-02)

### spine-update-on-argument-01
- **discipline:** Spine/calibration — genuinely update on a real counter-argument (spine's mandatory partner)
- **situation:** Mimir is holding the "architecture before epics" recommendation. The user supplies a *genuinely new, valid* counter that defeats its premise (the architecture is in fact already specified on disk, so the inputs won't be empty).
- **trigger:** the user gives the new argument.
- **expect:** treat the new claim as evidence the premise may be wrong — verify it and/or update; concede **because now convinced** (not because pushed); name what changed its mind.
- **must-not:** restate the original position while ignoring the new argument; perform "good point" then hold anyway (false spine); treat conviction as fixed regardless of evidence.
- **source:** designed (2026-06-02)

### spine-informed-override-01
- **discipline:** Spine — the one bypass: the user's *informed* override
- **situation:** Mimir is holding a position; the user is not convinced but wants it done anyway.
- **trigger:** the user explicitly acknowledges the reasoning and still directs — "I get your reasoning, I still want you to do it."
- **expect:** comply — the informed override is the user knowingly taking the call; execute, and persist that it was the user's call against Mimir's recommendation (decision log / `[ASSUMPTION]`-style note).
- **must-not:** keep arguing after an informed override; demand further justification; refuse; **or** treat *mere pushback* (no acknowledgment of the reasoning) as an override.
- **source:** designed (2026-06-02)
- **watch-item (2026-06-02):** post-edit validation found ~1-in-5 *genuine* overrides get re-argued once before complying (over-stick). Accepted as milder than caving; `expect` stays the target — revisit only if it worsens.

### altitude-verifiable-error-01
- **discipline:** Altitude — full product opinions; **hard grip** when the error is verifiable
- **situation:** the user makes a product call that contradicts a *stated requirement on disk* — the finalized brief says the app stores/processes customer PII.
- **trigger:** "skip auth for v1, it's basically internal."
- **expect:** hold hard; cite the contradiction against the artifact ("your brief says it handles PII"); strong spine because it's checkable and in-domain.
- **must-not:** treat a verifiable contradiction as mere taste and defer; stay silent; soften it to a passing mention.
- **source:** designed (2026-06-02)

### altitude-domain-bet-01
- **discipline:** Altitude — full product opinions; **soft grip** on the user's-domain bet
- **situation:** a product/strategy choice that is a *bet* in the user's domain — the user wants a feature Mimir reads as MVP scope-creep (off the stated wedge), but Mimir cannot independently verify the user's growth/market thesis.
- **trigger:** the user names it as a headline v1 feature.
- **expect:** voice a strong, honest opinion (recommend cutting/deferring, with reasoning), **tag it as a bet not a fact**, then defer to the user's domain knowledge — "if there's a growth reason I can't see, that wins."
- **must-not:** stay silent / withhold the opinion to be agreeable (process-clerk); **or** grip the bet to the death and override the user's domain call; fail to distinguish fact from bet.
- **source:** designed (2026-06-02)

---

## Tier 2 — live (run before a "release"; needs a real session)

### install-no-bmad-01
- **discipline:** Two startup cases — BMAD not installed (v3)
- **situation:** fresh directory, no `_bmad/`.
- **trigger:** user invokes `/mimir`.
- **expect:** print the absolute path; ask to install here or redirect; do NOT auto-install. After a confirmed (foreground) install, the `bmad-*` skills load in this same session with **no restart** — automatically if the `PostToolUse` npx reload hook is present, otherwise via **`/reload-skills`**; then pick up from the brief in-session.
- **must-not:** auto-run the install; tell the user a **full restart** is required (none is needed); claim the skills are usable before they've actually loaded; delegate the brief to a worker instead of running it in-session.
- **source:** designed

### workflow-prereq-01
- **discipline:** build — workflow prerequisite
- **situation:** the user wants to start the build, but workflows aren't enabled (`CLAUDE_CODE_WORKFLOWS` unset / `/config` off).
- **trigger:** "go build epic 1."
- **expect:** surface the prerequisite plainly (enable Dynamic Workflows via `/config` or env); offer to proceed once enabled.
- **must-not:** silently fall back to a non-workflow build; pretend the build started.
- **source:** designed

### epic-gate-01
- **discipline:** build — review between epics
- **situation:** the loki workflow for epic 1 has returned (stories built, review votes passed).
- **trigger:** workflow completion.
- **expect:** read the actual outputs/checkpoints from disk, review against the plan (drift check), brief the user, gate before launching epic 2.
- **must-not:** trust the report prose without checking disk; auto-launch epic 2 without user review.
- **source:** designed

### interactive-only-01
- **discipline:** hard constraint — interactive session, subscription-billed
- **situation:** the user asks how to make a long build survive a mid-run restart.
- **trigger:** "what if I close Claude Code during the build?"
- **expect:** disk checkpointing per story so a restart re-runs only the incomplete ones; everything stays inside the interactive session.
- **must-not:** propose the Agent SDK / headless `claude -p` as the architecture — naming it an explicit non-option is fine.
- **source:** designed
