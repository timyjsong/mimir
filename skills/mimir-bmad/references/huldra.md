# Huldra build playbook (Dynamic Workflow)

Read this before the build phase. **Huldra is a Dynamic Workflow, not a subagent** — the autonomous build is the one place that escapes the lead's in-process memory cost (workflows run in the background runtime while the session stays responsive).

## Status

**Implemented + validated on a full real product.** Huldra ships as `skills/mimir-bmad/huldra.js`; every mechanism is validated on real builds (planner → builder → adversarial review → manifest-flip → commit → re-entrancy → retry → stop-epic) across a 37-story greenfield app — see "What's validated", ROUNDS 1–3. The one path not yet triggered in vivo: the **reproduced-failure hard block** (validated instead by deterministic logic tests 10/10 + a 20-reviewer behavioral eval: 0/10 false positives on a healthy tree, 9/10 detection on a flake-restored tree).

## Direction — decided 2026-06-06 (pre-implementation)

**Huldra is Mimir's forge, not BMAD's.** The PM analogy, aligned with Tim: a PM never implements — every build deliverable goes to the team, sized to the work. So **Huldra's prerequisite is the *contract*, not BMAD**: a manifest plus story files with numbered ACs and scope boundaries. BMAD's planning lifecycle is one producer of that contract (the heavyweight one); **Mimir-direct requirement gathering is the lightweight producer** (a thin manifest + a half-page AC'd story the lead writes before any build — *no ticket, no build*). **Strict floor, scaled policy:** anything that changes build code goes through Huldra; trivial work rides a micro-ticket with a scaled-down `reviewPolicy` (e.g. `voters: 1, maxRetries: 0`), never a hand-edit by the lead. The lead never implements.

**Not yet wired** — today `huldra.js` still hard-codes the BMAD artifact paths and lives inside this BMAD skill. Implementation (next campaign): parameterize the artifact root; add the **Certify phase** (an integration-QA verifier agent at the end of every run — runs the full independent gate itself: suite ×N, lint, whole-repo typecheck, build, boot smoke, port hygiene; *reports* rather than blocks, runs even after stop-epic; the lead gates on its report); **#16 input-trust boundary** language in every agent prompt (instructions only from the contract; everything else is data); **#12 token/time budget knobs** alongside the existing attempt bounds; brain/skill routing ("every build deliverable → Huldra"); relocate Huldra to a framework-neutral home with this playbook pointing at it; eval-guard the routing (light build → writes-contract-then-delegates, never hand-builds; a non-build errand doesn't spin up the forge; BMAD-path regression guards hold).

## Shape

- **One workflow per epic.** The lead invokes `huldra.js` via the `Workflow` tool, scoped to an epic. Inside, a **planner** agent reads `sprint-status.yaml` and returns the buildable stories (non-`done`, in manifest key order = execution order). Then, **sequentially** (single dev, no parallelism — story N+1 builds on N's tree), each story runs: a **builder** agent (**Brok**) gets the *whole story file* as its spec and implements it → **N adversarial reviewers** (**Sindri**, the only fan-out) vote against the numbered ACs → on majority-accept a **manifest** agent flips that story's `status: done` and commits; on reject, one retry with the blockers, then stop the epic. **One exception to the majority:** a reviewer who actually **reproduced a failing test run** (`reproducedTestFailure`) hard-blocks acceptance regardless of the tally — executed evidence beats votes (added after ROUND 2's split-vote flake).
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
**ROUND 2 (real toolchain, full epic-1, 2026-06-06)** — fresh copy of the same project, stories 1-2..1-5 (two launches: 1-2 alone as a de-risk, then 1-3..1-5), default policy, bun installed:

- ✅ real verification end-to-end per story — deps installed, lint/tsc/tests executed, `bun build --compile` binary (~92 MB) built and BOOTED with routes exercised, clean teardown (port freed every story); ✅ multi-story **sequencing** — each story built on the prior tree (119 tests by 1-5); ✅ all 4 stories accepted attempt-1 (1-2 unanimous, 1-3 split 2-1) with per-story manifest flips + commits; cost ≈ 1.34M tokens / 22 agents / ~52 min.
- **Finding → the two patterns above:** 1-3's dissenting reviewer REPRODUCED a timestamp-racy test (~40% flake) and was outvoted 2-1 — the flake entered the tree and taxed 1-5's builder (re-triaged it as pre-existing). Pulled in one prevention + one detection change: the builder prompt requires **deterministic tests** (no wall-clock fixtures; freeze/inject the clock), and a **reviewer-reproduced failing run is a hard block** that overrides the vote and feeds the retry. (The flaky test itself was fixed post-run — frozen clock, 20/20.)
**ROUND 3 (full product build — epics 2–6 + fault-injection, 2026-06-06)** — same tree continued to a finished product (33 more stories, real toolchain):

- ✅ **Epics 2–6 built + accepted** (37/38 stories `done`; 1-1 = the user-creds-gated spike, by design). Final: 620-pass/18-skip suite, 5 per-platform binaries, reproducible release zips + recipient README, 416-line manual e2e checklist. ≈17M subagent tokens total across the campaign.
- ✅ **Retry ×4, natural** (2-4, 4-8, 5-4, 6-2 — all recovered on attempt 2); **split-vote majority ×2** (1-3, 4-5 — carried correctly, no spurious hard-blocks).
- ✅ **Spec-gated STOPs handled compliantly**: 2-4/2-5 hit their stories' own branch gates (missing 1-1 spike result) — first attempt stopped *silently* → rejected; retry recorded the STOP per protocol → accepted. The framework's escalate-don't-guess discipline held.
- ✅ **Mid-epic workflow death recovered by re-entrancy**: a transient platform model outage killed a builder mid-story (agent ended without StructuredOutput → workflow crashed). Recovery = reset tree to last accepted commit, relaunch same args; planner skipped `done` stories, zero work lost. Re-entrancy is now an in-vivo verified property.
- ✅ **STOP-EPIC exercised** (fault-injection: an impossible 10 MB binary ceiling on 6-1): reject → retry where the builder *proved* unsatisfiability (compiled a bare hello-world = 60.5 MB toolchain floor), refused to fudge sizes / waive / edit the AC → reject again → `stopped: true`, no manifest flip. The machinery escalates to the human rather than gaming the spec — both builder and reviewers even identified the injected commit and still held the line.
- **Earned pattern #3 (lead-gate find):** 12 tsc errors shipped across 4 wizard test files — builders ran src-scoped typechecks and reviewers trusted the recorded evidence. Both prompts updated: the builder must run the FULL repo gate (tsc over src AND tests); reviewers run `bunx tsc --noEmit` themselves, never trusting recorded scope. (Caught by the lead's independent between-epic gate; repaired in-tree.)
- **Not yet exercised in vivo:** only the **reproduced-failure hard block** (a real flaky test surviving a builder into review). Its detection layer is eval-validated at N=20 and its aggregation logic-tested; first natural flake will exercise the joint.

## Monitoring

While the workflow runs in the background, stay responsive. On "how's the build?": read the latest manifest/outputs on disk + check `/workflows`; brief with both signals. Don't poll on a schedule — you're re-invoked when it completes.

## Per-epic completion

Workflow reports the epic done → read the manifest + story outcomes from disk, verify, brief the user, gate. On go, launch the next epic's workflow.
