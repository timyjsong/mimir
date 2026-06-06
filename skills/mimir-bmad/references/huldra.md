# Huldra build playbook (Dynamic Workflow)

Read this before the build phase. **Huldra is a Dynamic Workflow, not a subagent** — the autonomous build is the one place that escapes the lead's in-process memory cost (workflows run in the background runtime while the session stays responsive).

## Status

**Implemented.** Huldra ships as `skills/mimir-bmad/huldra.js` and the mechanism is validated end-to-end (planner → builder → adversarial review → manifest-flip → commit → re-entrancy). What's still owed: a **real-toolchain build** (the validation so far was an *inspection round* with no build tools installed — see "What's validated"), and the **reject → retry → stop-epic** path is written but unexercised. (`~/.claude/agents/loki-worker.md` is a superseded stub — do not spawn it; the build is a workflow.)

## Shape

- **One workflow per epic.** The lead invokes `huldra.js` via the `Workflow` tool, scoped to an epic. Inside, a **planner** agent reads `sprint-status.yaml` and returns the buildable stories (non-`done`, in manifest key order = execution order). Then, **sequentially** (single dev, no parallelism — story N+1 builds on N's tree), each story runs: a **builder** agent (**Brok**) gets the *whole story file* as its spec and implements it → **N adversarial reviewers** (**Sindri**, the only fan-out) vote against the numbered ACs → on majority-accept a **manifest** agent flips that story's `status: done` and commits; on reject, one retry with the blockers, then stop the epic.
- **The script does no fs/shell — agents do all disk work** (planner reads, builder writes, reviewers inspect, manifest agent edits the yaml + commits). This is a hard constraint of the Workflow runtime.
- **Checkpoint = the BMAD-native manifest.** `status: done` in `sprint-status.yaml` is the checkpoint; per-story commits land on a build branch. **Re-entrant by construction**: a fresh launch's planner skips `done` stories and resumes at the first non-done key.
- The lead **launches per epic, monitors** (`/workflows`), and **gates between epics**: read the epic's outputs from disk, review against the plan (drift check), brief the user, then launch the next epic.

## Invocation

`Workflow({ scriptPath: '<skill>/huldra.js', args: {...} })`. The `args` object:

- `projectRoot` (**required**) — absolute path to the BMAD project; every agent resolves paths from here. **Builders ignore stale absolute paths baked into story text** (BMAD story specs sometimes hardcode a wrong root) and resolve from `projectRoot`.
- `epic` — e.g. `"epic-1"`; restrict to one epic (Huldra is per-epic).
- `onlyStories` — e.g. `["1-2"]`; restrict to specific story keys (used for validation slices).
- `reviewPolicy` — `{ voters, threshold, maxRetries, canRunCommands, toolchainNote }`. Defaults: 3 voters, threshold 2 (majority), 1 retry, `canRunCommands: true`. Set `canRunCommands: false` for an **inspection round** (no build toolchain): the builder writes to spec and runs nothing; reviewers mark runtime-only ACs `unverifiable` rather than `fail`.

**`args` footgun:** the Workflow tool may deliver `args` as a JSON *string*. `huldra.js` defensively `JSON.parse`s a string arg, but prefer passing a real object.

## Gates before committing to Huldra-as-workflow

1. **Billing (load-bearing — researched & supported; empirical confirm owed):** a workflow launched from an *interactive* session bills to **subscription, not credits** per first-party docs (workflow runs count "like any other session"; interactive Claude Code stays on subscription through the 2026-06-15 split; subagents inherit the launching session's surface). Confidence medium-high — confirm empirically on/after June 15 via `/usage` (spend lands on plan-usage, NOT the `/usage-credits` meter). If it ever shows credits — do not use it; it breaks the interactive/subscription requirement.
2. **`CLAUDE_CODE_WORKFLOWS=1`** (or the `/config` toggle) must be enabled. If not, surface it — don't fake a build.
3. **Keep the billing surface interactive — three guards.** **No nested `claude -p`** inside the build (credit-billed) — huldra.js uses only `agent()`/`parallel()`, never a CLI shell-out or the SDK. **Never run the lead as a Routine** (cloud/programmatic surface). **No `ANTHROPIC_API_KEY` in the env** — it authenticates pay-go API at full rates, bypassing BOTH subscription and credits regardless of surface (the silent footgun); confirm it's unset/absent before launch.
4. Readiness verdict "go" AND your own judgment the docs are sufficient for autonomous build AND explicit user go. For a **first real build**, install the project's toolchain first (an outward install — gate it) so the build/test/lint ACs actually execute.

## What to pass at launch

- **Epic** to build (`epic`) — Huldra is per-epic.
- **Scope guards** the user flagged ("stay in module X", "don't touch Y").
- **Project root** (`projectRoot`) — the build reads the planning docs (PRD, architecture, epic/story files) and the manifest from here.
- **Review policy** — vote count / acceptance threshold; retry policy (default: one retry, then stop the epic and surface). `canRunCommands: false` only for an inspection dry-run.

## What's validated (and what isn't)

**ROUND 1 (inspection round, 2026-06-05)** — on an isolated copy of a real 6-epic greenfield BMAD project, story 1-2 (scaffolding), `canRunCommands: false`, no build tools installed:

- ✅ planner reads the manifest, selects in key order, honors the filters; ✅ builder reads the whole story, resolves paths from cwd (dodged a stale baked-in root), wrote the full scaffold to spec, respected scope boundaries (stubbed what later stories own, no overreach), filled the Dev Agent Record; ✅ 3 reviewers unanimously accepted, correctly marking the boot/build/test/lint ACs `unverifiable` rather than `fail`; ✅ manifest agent surgically flipped only that story to `done` and committed; ✅ re-entrancy — a re-run built nothing and reported the skip.
- **Not yet exercised:** a real-toolchain build (ROUND 2 — build/test/lint actually run; needs the project's toolchain installed); the **reject → retry → stop-epic** path (the story accepted first try); multi-story **sequencing** (only one story ran).

## Monitoring

While the workflow runs in the background, stay responsive. On "how's the build?": read the latest manifest/outputs on disk + check `/workflows`; brief with both signals. Don't poll on a schedule — you're re-invoked when it completes.

## Per-epic completion

Workflow reports the epic done → read the manifest + story outcomes from disk, verify, brief the user, gate. On go, launch the next epic's workflow.
