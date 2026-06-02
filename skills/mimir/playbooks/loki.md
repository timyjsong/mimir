# loki build playbook (Dynamic Workflow)

Read this before the build phase. **loki is a Dynamic Workflow, not a subagent** — the autonomous build is the one place that escapes the lead's in-process memory cost (workflows run in the background runtime while the session stays responsive).

## Status

**loki is not implemented yet, and workflows are research-preview.** This is the forward contract — what the build will look like when it ships. Today, advise "build-ready" but say the build can't start. (`~/.claude/agents/loki-worker.md` is a superseded stub — do not spawn it; the build is a workflow.)

## Shape

- **One workflow per epic.** The workflow (JS-orchestrated) fans out story-builder subagents, runs **adversarial multi-vote code review** before a story is accepted, and **checkpoints per story to disk** (a `completedStories` manifest in the epic's output dir).
- **Workflows don't resume across sessions** — if the session exits mid-build, a fresh launch must read the checkpoint manifest and **re-run only the incomplete stories**. The script is written to skip completed work on re-entry.
- The lead **launches per epic, monitors** (`/workflows`), and **gates between epics**: read the epic's outputs from disk, review against the plan (drift check), brief the user, then launch the next epic.

## Gates before committing to loki-as-workflow

1. **Billing (load-bearing — verify first-party):** confirm a workflow launched from an *interactive* session bills to **subscription, not credits**. If credits — do not use it; it breaks the interactive/subscription requirement.
2. **`CLAUDE_CODE_WORKFLOWS=1`** (or the `/config` toggle) must be enabled. If not, surface it — don't fake a build.
3. **No nested `claude -p`** inside the build (credit-billed). **Never run the lead as a Routine** (cloud/programmatic surface).
4. Readiness verdict "go" AND your own judgment the docs are sufficient for autonomous build AND explicit user go.

## What to pass at launch

- **Epic** to build (id/name) — loki is per-epic.
- **Scope guards** the user flagged ("stay in module X", "don't touch Y").
- **Artifact inputs** — the planning docs the build reads (PRD, architecture, epic/story files).
- **Review policy** — vote count / acceptance threshold; retry policy on a failed review (default: one retry, then surface).

## Monitoring

While the workflow runs in the background, stay responsive. On "how's the build?": read the latest checkpoint/outputs on disk + check `/workflows`; brief with both signals. Don't poll on a schedule.

## Per-epic completion

Workflow reports the epic done → read story outcomes from disk, verify, brief the user, gate. On go, launch the next epic's workflow.
