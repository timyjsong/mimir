# End-to-end walkthrough

A concrete example of a full mimir lifecycle from first `/mimir` invocation through readiness verdict. Used for orientation, not referenced from any other doc. Read this when you want to see how the pieces fit together in practice.

The scenario: user starts a new project called `news-agg`. The directory is empty of BMAD state. They invoke `/mimir`.

(Paths below are illustrative — actual output paths resolve from `_bmad/bmm/config.yaml`. This single-session happy path doesn't exercise concurrency/latest-wins or the loki build phase; see SKILL.md for those.)

---

## Phase 0 — First invocation, install needed

### Step 1: User types `/mimir`

The mimir SKILL loads into the current session. The session becomes the lead.

### Step 2: Mimir orients (silent — steps 1–6 of Orientation)

```
[silent] cwd = /home/user/projects/news-agg
[silent] check _bmad/ — does not exist
[silent] BMAD not installed → defer team creation, skip bmad-help (no _bmad/ to orient against)
```

### Step 3: Mimir's first user-facing turn (Orientation step 7)

```
mimir status
────────────
phase:     install
team:      not yet created (BMAD not installed)
next:      you — confirm install at /home/user/projects/news-agg or redirect

Project root is /home/user/projects/news-agg. BMAD isn't installed here yet.

Install BMAD into this folder, or did you mean a different directory?
```

### Step 4: User responds

> yeah install here

### Step 5: Mimir runs install via Bash (background)

```
[silent, but maybe one starting signal] "OK, installing — back when it's done."

Bash(
  command: "npx -y bmad-method install --yes --modules bmm --tools claude-code --directory /home/user/projects/news-agg",
  run_in_background: true
)
```

Mimir is notified on completion. Then:

```
[silent] check _bmad/ exists — yes
[silent] check _bmad/bmm/config.yaml exists — yes
```

### Step 6: Mimir completes orientation (steps 3–6)

```
[silent] read _bmad/bmm/config.yaml — project name "news-agg", output paths resolved
[silent] list output dirs — empty (no artifacts yet)
[silent] invoke bmad-help — output: "no workflow in progress; recommend starting with bmad-product-brief"
[silent] read _bmad-output/.mimir-notes.md — doesn't exist (fresh project)
[silent] load team tools (ToolSearch select:TeamCreate,Agent,SendMessage); check ~/.claude/teams/mimir-news-agg/config.json — doesn't exist
[silent] TeamCreate(team_name: "mimir-news-agg") — team created, no workers yet
[silent] write {session-id, timestamp} to _bmad-output/.mimir-notes.md — claim latest
```

### Step 7: Mimir briefs the user

```
mimir status
────────────
phase:     analysis
team:      mimir-news-agg
next:      you — confirm next step

BMAD installed. No artifacts yet — fresh project.

bmad-help recommends the product brief next. I agree — brief locks the WHAT (problem, users, scope) before we get into HOW. The brief workflow is coaching-style by default: section-by-section drafting, pushback on thin answers. Suits a serious project.

If you want fast-path (assumption-heavy, less back-and-forth), say so before we spawn. Otherwise I'll go with coaching.

Proceed?
```

---

## Phase 1 — First workflow: product brief

### Step 8: User confirms

> yeah coaching path. project is a news aggregator i want to build for myself, local-first

### Step 9: Mimir delegates

```
[silent] read playbooks/bmad.md — judge mode
[silent] bmad-product-brief is elicitation-heavy (interactive section-by-section) → persistent + foreground
[silent] stable name "brief-worker"
[silent] Agent({
  subagent_type: "bmad-worker",
  name: "brief-worker",
  team_name: "mimir-news-agg",
  prompt: "
    Run bmad-product-brief in this project. Intent: create.
    Working mode: coaching path.
    User's framing (verbatim): 'project is a news aggregator i want to build for myself, local-first'
    Trust BMAD orientation — the skill self-loads context from _bmad/.
    Report: short SendMessage with status, artifact path, handoff path. Rich content in handoff file.
  "
})
```

### Step 10: brief-worker spawns and ack-SendMessages

User sees a short tool result in their chat:

```
[brief-worker] Spawned as brief-worker. Beginning bmad-product-brief (create).
```

### Step 11: brief-worker runs the skill, produces round 1

The BMAD skill enters Discovery and produces 3 questions for the user. brief-worker writes:

```
File: /home/user/projects/news-agg/_bmad/bmm/output/briefs/brief-news-agg-2026-05-28/.worker-handoff.md

# Round 1 · 2026-05-28T14:32:18Z

## Questions

### Q1 — Product framing
The user said "news aggregator for myself, local-first." Two product shapes possible:
(a) Reader app — pulls from RSS/sites, presents in a personal feed
(b) Research tool — pulls and synthesizes/summarizes
Need user's specific framing.

[relay guidance: needs literal user words — product shape changes everything downstream]

### Q2 — "Local-first" scope
"Local-first" could mean: data lives locally (sync optional), runs locally (no cloud at all), or self-hosted (any infra is the user's).

[relay guidance: lead can present options, user picks; doesn't need literal wording]

### Q3 — Stakes
Personal tool — what does "working" mean? Daily use? Weekly? Replacing an existing tool?

[relay guidance: open prompt, any phrasing fine]

## Holding for next round
Volume/scale, monetization (probably none for personal), engagement features.
```

Then SendMessages mimir (the part user sees in chat):

```
[brief-worker] Round 1 ready. 3 open.
Status: in-progress
Artifact: /home/user/.../brief.md (skeleton)
Handoff: /home/user/.../briefs/brief-news-agg-2026-05-28/.worker-handoff.md
```

### Step 12: Mimir reads the handoff silently

```
[silent] Read /home/user/projects/news-agg/_bmad/bmm/output/briefs/brief-news-agg-2026-05-28/.worker-handoff.md
```

### Step 13: Mimir translates for the user

```
mimir status
────────────
phase:     analysis (mid-brief, Round 1)
team:      mimir-news-agg
workers:
  • brief-worker  — bmad-product-brief (create) · awaiting your answers below
artifacts: brief skeleton + decision log
next:      you — three Discovery questions

brief-worker has three questions before drafting the brief sections.

**Q1 — Product framing.** "News aggregator for myself, local-first" leaves two shapes open: (a) reader app — pulls from RSS/sites, presents in a personal feed; (b) research tool — pulls and synthesizes/summarizes. Your wording matters here — pick one or describe in your own words.

**Q2 — What does "local-first" mean to you?** Three flavors: data lives locally (sync optional), runs locally (no cloud at all), or self-hosted (any infra you choose). Pick one.

**Q3 — What does "working" look like?** Daily use? Weekly? Replacing an existing tool you've outgrown?
```

The user only sees this and the short brief-worker SendMessage. The 30-line handoff file stays on disk.

### Step 14: User answers

> Q1: reader app, basically a personalized feed. Q2: runs locally, no cloud. Q3: replacing Feedly which i pay for but barely use the smart features

### Step 15: Mimir SendMessages brief-worker

```
[silent] SendMessage({
  to: "brief-worker",
  message: "
    User responses, Round 1:
    Q1 (literal): 'reader app, basically a personalized feed'
    Q2: runs locally, no cloud
    Q3 (literal): 'replacing Feedly which i pay for but barely use the smart features'

    Continue.
  "
})
```

### Step 16: Loop continues across rounds

brief-worker runs the next round, writes a new handoff (overwriting the previous), SendMessages a pointer. Mimir reads, translates, relays. User answers. Repeat.

Eventually the brief converges. brief-worker SendMessages:

```
[brief-worker] Brief complete. Workflow done.
Status: workflow-complete
Artifact: /home/user/.../briefs/brief-news-agg-2026-05-28/brief.md (finalized)
Handoff: /home/user/.../briefs/brief-news-agg-2026-05-28/.worker-handoff.md
```

### Step 17: Mimir reads the artifact, briefs user

```
[silent] Read /home/user/.../brief.md (full, finalized)
[silent] Read handoff for completion summary
```

Mimir's user-facing turn:

```
mimir status
────────────
phase:     analysis (brief complete)
team:      mimir-news-agg
artifacts: brief.md (finalized)
next:      you — review brief or proceed to PRD

Brief is done. Captured: personalized RSS reader, runs locally, replacing Feedly. Personas thin (only one — you), but that's right for a personal tool. Scope is "MVP that I'd actually use daily."

Take a look at /home/user/.../brief.md if you want to review.

Next up is the PRD (bmad-prd, create intent). I'd recommend it. Want me to spawn prd-worker now, or review the brief first?
```

### Step 18: User reviews, then proceeds

> brief looks good. yeah go to PRD

### Step 19: Mimir retires brief-worker

```
[silent] SendMessage({to: "brief-worker", message: {type: "shutdown_request"}})
[silent] await shutdown_response from brief-worker
[silent] team config now has 0 active workers
```

(The handoff file is NOT deleted at retirement — it's bulk-cleaned later, at the loki transition or project teardown. The worker overwrote it each round during the workflow, so nothing accumulated mid-flow.)

---

## Phase 2 — PRD, architecture, readiness

Same pattern: persistent foreground worker, multi-round elicitation, handoff per round, retire + delete handoff at completion.

```
prd-worker  →  bmad-prd (create)  →  prd.md
arch-worker →  bmad-create-architecture  →  architecture.md
```

Between workflows, mimir's status shows `team: mimir-news-agg (no workers active)` with `next: spawn <next-worker> — awaiting your go`.

---

## Phase 3 — Readiness verdict

### Step 20: Spawn readiness check (ephemeral background, autonomous)

```
[silent] read playbooks/bmad.md — bmad-check-implementation-readiness is autonomous (judges artifacts, no user input expected) → ephemeral + background
[silent] Agent({
  subagent_type: "bmad-worker",
  team_name: "mimir-news-agg",
  run_in_background: true,
  prompt: "Run bmad-check-implementation-readiness. ... return short SendMessage + handoff file."
})
```

Mimir doesn't block. User can chat with mimir while readiness runs.

### Step 21: Readiness reports back

```
[readiness-worker, unnamed bg] Verdict ready: go
Status: workflow-complete
Artifact: /home/user/.../readiness/v0001/report.md
Handoff: /home/user/.../readiness/v0001/.worker-handoff.md
```

### Step 22: Mimir reads, judges, briefs

```
[silent] Read report.md and handoff
```

Mimir applies advisor discipline — even though BMAD says "go", mimir looks at the artifacts holistically. Maybe NFRs are thin, maybe a persona is missing. In this case, mimir agrees with go.

```
mimir status
────────────
phase:     readiness
team:      mimir-news-agg
artifacts: readiness report (verdict: go)
next:      you — ready for build, but loki not yet implemented

Readiness verdict: go. I agree — artifacts are coherent, key risks documented, no obvious gaps. We're build-ready.

One thing: loki (the build orchestrator) isn't implemented yet. So "ready for build" is the state; we can't actually start the build today. Planning side is wrapped.

When loki ships, /mimir will pick up here and spawn loki-worker. For now, the project is paused at ready-for-build. Anything else you want to revisit on the planning side, or call this a wrap?
```

### Step 23: User wraps

> wrap it for now. thanks

### Step 24: Mimir tears down

```
[silent] no active workers
[silent] bulk-delete all .worker-handoff.md files under _bmad-output/ (residual cleanup)
[silent] TeamDelete()  — own team, self-scoped
```

Final user-facing turn:

```
mimir status
────────────
phase:     boundary (project paused — ready for build)
team:      torn down
artifacts: all planning artifacts finalized; readiness verdict on disk
next:      out of scope until loki ships; re-invoke /mimir to revisit planning
```

Session ends. All disk state persists; future `/mimir` invocations re-orient from disk.

---

## Key patterns this walkthrough demonstrates

1. **Orientation happens silently.** Steps 1–6 produce no user-facing text. Only step 7 hands back.
2. **Team is created during orientation.** By the time the user sees the first brief, team exists.
3. **Worker SendMessages stay short.** The verbose elicitation content lives in `.worker-handoff.md` on disk.
4. **Mimir reads handoff silently, translates cleanly.** User sees mimir's PM-voice translation, not the worker's BMAD-voice raw output.
5. **Handoff files are ephemeral.** Worker overwrites each round (never appends); bulk-cleaned at the loki transition or project teardown, not at each retirement.
6. **Mimir judges mode at runtime.** No hardcoded skill→mode table. Mimir reads `bmad-help` and the skill's nature to pick persistent vs ephemeral, fg vs bg.
7. **Mimir advises on top of BMAD's recommendations.** When mimir's asymmetric context surfaces something BMAD didn't, mimir says so.
8. **State lives on disk.** Conversation can end at any point; next session resumes from `_bmad/` + decision logs.
9. **Build phase is gated.** Loki is recommended only after readiness "go" AND mimir's own assessment AND user confirmation.
