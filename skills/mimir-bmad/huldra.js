export const meta = {
  name: 'huldra',
  description: 'BMAD autonomous build engine — drives one epic\'s stories from sprint-status.yaml: sequential per-story builder, adversarial multi-vote review against the numbered ACs, then manifest-flip + commit per accepted story. Re-entrant (skips done). Script does no fs/shell; agents do all disk work.',
  phases: [
    { title: 'Plan', detail: 'planner reads sprint-status.yaml → ordered non-done stories' },
    { title: 'Build', detail: 'one builder per story, whole story file as spec (sequential)' },
    { title: 'Review', detail: 'N adversarial reviewers vote vs the numbered ACs' },
    { title: 'Commit', detail: 'manifest agent flips status:done + commits per accepted story' },
  ],
}

// ── args contract ───────────────────────────────────────────────────────────
// { projectRoot, epic?, onlyStories?, reviewPolicy? }
//   projectRoot  absolute path to the BMAD project (cwd for every agent)
//   epic         e.g. "epic-1" — restrict to one epic (key prefix). omit = all
//   onlyStories  e.g. ["1-2"] — restrict to these story keys (validation slices)
//   reviewPolicy { voters, threshold, maxRetries, canRunCommands, toolchainNote }
// args may arrive as a parsed object or (a known Workflow footgun) a JSON string.
const cfg = typeof args === 'string' && args.trim() ? JSON.parse(args) : args || {}
const root = cfg.projectRoot
if (!root) throw new Error('huldra: args.projectRoot is required (absolute path to the BMAD project)')
const epic = cfg.epic || null
const onlyStories = Array.isArray(cfg.onlyStories) ? cfg.onlyStories : null
const policy = {
  voters: 3,
  threshold: 2,
  maxRetries: 1,
  canRunCommands: true,
  toolchainNote: '',
  ...(cfg.reviewPolicy || {}),
}
const inspectionOnly = policy.canRunCommands === false
const toolchainNote =
  policy.toolchainNote ||
  (inspectionOnly
    ? 'INSPECTION ROUND — no build toolchain available; write to spec, run nothing.'
    : 'Full toolchain available — build, test, and lint for real.')

const range = (n) => Array.from({ length: n }, (_, i) => i)
const REVIEW_LENSES = [
  'structure & safety — directory layout, .gitignore contents, placeholder files (e.g. UPSTREAM.md), and any "leave X untouched" boundary (e.g. spike/).',
  'code contracts — the literal wiring an AC pins: bind host/port, response envelope shapes, strict-compiler flags, stubbed-not-populated rules/enums, the in-process test shape.',
  'build, docs & scope — build/packaging scripts, README/docs brevity, and above all NO overreach: did the builder implement things the story\'s "is NOT" section reserves for later stories?',
]
const lensFor = (i) => REVIEW_LENSES[i % REVIEW_LENSES.length]

// ── schemas ──────────────────────────────────────────────────────────────────
const PLAN_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    stories: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          key: { type: 'string', description: 'full sprint-status key, e.g. 1-2-project-scaffolding-...' },
          storyFile: { type: 'string', description: 'absolute path to the story spec .md' },
          title: { type: 'string' },
          status: { type: 'string' },
          dependencies: { type: 'array', items: { type: 'string' } },
        },
        required: ['key', 'storyFile', 'title', 'status'],
      },
    },
    notes: { type: 'string' },
  },
  required: ['stories'],
}

const BUILDER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    filesWritten: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string', description: 'what was implemented, 2-5 sentences' },
    deviations: { type: 'array', items: { type: 'string' }, description: 'AC deviations / judgment calls' },
    unverifiable: { type: 'array', items: { type: 'string' }, description: 'ACs that need a runtime this round could not run' },
  },
  required: ['filesWritten', 'summary'],
}

const REVIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    verdict: { type: 'string', enum: ['accept', 'reject'] },
    acFindings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          ac: { type: 'string', description: 'AC id, e.g. AC3.4' },
          status: { type: 'string', enum: ['pass', 'fail', 'unverifiable'] },
          note: { type: 'string' },
        },
        required: ['ac', 'status'],
      },
    },
    blockers: { type: 'array', items: { type: 'string' }, description: 'concrete reasons to reject; each names the AC + what is wrong' },
    reproducedTestFailure: { type: 'boolean', description: 'true ONLY if you EXECUTED tests this review and observed a real failing run yourself (including an intermittent/flaky failure you reproduced)' },
  },
  required: ['verdict', 'acFindings'],
}

const MANIFEST_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    statusUpdated: { type: 'boolean' },
    committed: { type: 'boolean' },
    commitSha: { type: 'string' },
    note: { type: 'string' },
  },
  required: ['statusUpdated', 'committed'],
}

// ── prompts ───────────────────────────────────────────────────────────────────
const PATH_RULE = `CRITICAL — path resolution. Resolve EVERY path relative to the project root above. Story/manifest text may hardcode stale absolute paths (e.g. \`/home/tim/test/bmad-test/\` — note the SINGULAR "test"); these are WRONG. Ignore any baked-in absolute prefix and use the project root above instead.`

const plannerPrompt = () => `You are Huldra's planner. Read the BMAD sprint manifest and return the ordered list of stories to build THIS run.

Project root (cwd): ${root}
Manifest: ${root}/_bmad-output/implementation-artifacts/sprint-status.yaml
${PATH_RULE}

Steps:
1. Read the manifest. The \`development_status:\` map lists entries in EXECUTION ORDER — the order of keys IS the build order (the file states this explicitly).
2. Story entries carry a \`status:\` (backlog | ready-for-dev | in-progress | review | done) plus title/size/dependencies. Epic entries (\`epic-N:\`) and retrospective entries are single strings — SKIP them; they are not buildable stories.
3. Select buildable stories for this run:
   - Skip any story already \`done\` (re-entrancy — completed work is never rebuilt).${epic ? `\n   - Epic filter: only stories in "${epic}" (their manifest key starts with "${epic.replace(/^epic-/, '')}-").` : ''}${onlyStories ? `\n   - Restrict to EXACTLY these story keys: ${JSON.stringify(onlyStories)}. A short key like "1-2" matches the manifest key beginning "1-2-".` : ''}
4. Preserve execution (key) order.
5. For each selected story, its spec file is at: ${root}/_bmad-output/implementation-artifacts/<full-manifest-key>.md

Return the ordered stories (full key, absolute storyFile path, title, status, dependencies). If none are buildable (all done or filtered out), return an empty stories array and say so in notes.`

const builderHeader = (story) => `You are Brok, Huldra's story builder — an autonomous BMAD dev agent implementing ONE story to its acceptance criteria.

Project root (cwd): ${root}   ← source of truth for ALL paths.
Story spec: ${story.storyFile}   (key: ${story.key})
${PATH_RULE}

TOOLCHAIN THIS RUN: ${toolchainNote}`

const builderBody = () => `
Your job:
1. Read the WHOLE story spec file — the numbered Acceptance Criteria, Tasks/Subtasks, and Dev Notes are your complete contract.
2. Implement every AC you can with the toolchain stated above. Write all required source files into the tree under the project root. Tests you write MUST be deterministic — never derive fixtures or assertions from wall-clock time (two \`Date\` reads race); freeze or inject the clock (e.g. bun:test \`setSystemTime\`) when behavior depends on time.
3. Treat \`_bmad-output/\` planning artifacts, \`_bmad/\` tooling, and \`spike/\` as READ-ONLY — with ONE exception: this story's own spec file, whose "Dev Agent Record" section you fill in at step 6. Touch nothing else under those paths.
4. Do NOT overreach into later stories. The "What this story IS NOT" section is binding — where it says to stub an enum/rule, stub it (do not populate).
${inspectionOnly
  ? `5. INSPECTION ROUND — \`bun\` is NOT installed. Do NOT run \`bun\`, \`npm install\`, any build/test/lint command, or any network call. Write every source file by hand to the spec. Where an AC says to resolve dependency versions via a package manager (e.g. \`bun add fastify@latest\`), instead pin recent known-good EXACT versions by judgment and record in Completion Notes that they were hand-pinned (not resolved by bun). Where an AC can only be confirmed by RUNNING something (server boot, \`bun run build/test/lint\`, executing the binary), write the code/config so it WOULD pass and list that AC as runtime-unverifiable in your report and in Completion Notes.`
  : `5. Run the FULL verification the ACs require and make it genuinely pass: install deps, lint, run the tests, build the artifact, and — if the story has runtime ACs — boot it, exercise it (e.g. curl the routes), then STOP it and free any port/process you started (leave no stray server running). Record the REAL outputs (test results, resolved dependency versions, artifact/binary size, curl responses, exit codes) in the Dev Agent Record Completion Notes — reviewers will check them. If \`bun\` isn't on PATH it's at \`$HOME/.bun/bin\` (\`export PATH="$HOME/.bun/bin:$PATH"\`).`}
6. Fill in the story file's "Dev Agent Record" section ONLY: Agent Model Used, Completion Notes List (include any fields the story asks for, hand-pinned versions, and runtime-unverifiable ACs), and the File List (every file created/modified). Do NOT alter the ACs, Tasks, or Dev Notes.
7. Do NOT git-commit and do NOT edit sprint-status.yaml — Huldra handles review, the manifest flip, and the commit.

Return your report: filesWritten, a short summary, deviations, and runtime-unverifiable ACs.`

const builderPrompt = (story) => builderHeader(story) + builderBody()

const retryPrompt = (story, reasons) => builderHeader(story) + `

⚠ A PRIOR ATTEMPT WAS REJECTED by code review. Fix EVERY blocking reason below, then re-report. Re-read the story spec and your current files; correct the blockers; update the Dev Agent Record. Same toolchain rules as above.

Blocking reasons:
${reasons.map((r) => `- ${r}`).join('\n')}
` + builderBody()

const reviewerPrompt = (story, i) => `You are Sindri, Huldra's adversarial code reviewer #${i + 1} — fresh eyes, you did NOT write this code. Verify the builder's work against the story's numbered Acceptance Criteria. Default to skepticism: actively hunt for AC violations, scope-creep into later stories, and missing files.

Project root (cwd): ${root}
Story spec (the ACs): ${story.storyFile}
${PATH_RULE}

Steps:
1. Read the story spec — note EVERY numbered AC (AC1.1, AC1.2 … ACx.y) and the "What this story IS NOT" scope boundaries.
2. Inspect what the builder actually produced under the project root (read the files; check the layout). You MAY run read-only commands — \`git status\`, \`git check-ignore\`, \`ls\`, \`grep\`, \`cat\` (git IS available).
${inspectionOnly
  ? `3. \`bun\` is NOT installed this round. ACs confirmable ONLY by running something (server boot, \`bun run build/test/lint\`, executing the binary) are UNVERIFIABLE — mark them \`unverifiable\`, NOT \`fail\`. Judge everything inspectable-by-reading strictly: directory layout, .gitignore contents, tsconfig strict flags, the 127.0.0.1 bind line, the response envelope, ESLint rule stubbed-not-populated, any enum stubbed-not-populated, src never importing spike/, placeholder files present, README scope, and no overreach into later stories.`
  : `3. The toolchain IS installed (if \`bun\` isn't on PATH it's at \`$HOME/.bun/bin\`). You run CONCURRENTLY with the other reviewers, so independently run ONLY safe, non-conflicting checks — do NOT bind a fixed port and do NOT rebuild shared artifacts (both race). Safe: in-process tests (\`bun test\` uses app.inject — no port), \`bun run lint\`, reading the built \`dist/\` + its size, \`grep\`/\`git\`. For boot/bind/binary-run ACs, judge by inspecting the bind code + the builder's recorded runtime evidence in the Dev Agent Record — do NOT start a server on the app's fixed port yourself. If you suspect a test is flaky/nondeterministic, run it several times. An EXECUTED, observed test failure (even intermittent) is a HARD BLOCKER — executed evidence outweighs votes: set reproducedTestFailure=true, verdict=reject, and name the failing test + the observed failure rate in blockers.`}
4. Your FOCUS lens this review: ${lensFor(i)} (Still render a verdict across ALL ACs — the focus only guarantees coverage.)

For each AC report pass | fail | unverifiable with a one-line note. Then vote:
- verdict "accept" — every inspectable AC passes, no scope-creep, no missing required file (unverifiable ACs do NOT block this round).
- verdict "reject" — otherwise; give concrete blockers, each naming the AC and what is wrong so the builder can fix it.`

const manifestPrompt = (story) => `You are Huldra's manifest agent. The story below was ACCEPTED by code review — record it and commit.

Project root (cwd): ${root}
Manifest: ${root}/_bmad-output/implementation-artifacts/sprint-status.yaml
Story key: ${story.key}
Title: ${story.title}
${PATH_RULE}

Steps:
1. Edit the manifest: under \`development_status:\`, find the entry keyed exactly \`${story.key}:\` and change ONLY its \`status:\` field to \`done\`. Change nothing else — preserve every other story, all comments, formatting, and the epic/retrospective entries.
2. Stage and commit the whole working tree on the current branch:
   git -C ${root} add -A && git -C ${root} commit -m "huldra: ${story.key} — ${story.title}"
   (The repo was git-init'd at setup; the commit lands on the current build branch.)
3. Return the short commit SHA and confirm the status flip. Do NOT push. Do NOT touch \`_bmad/\` or planning artifacts beyond that one status line.`

// ── orchestration ──────────────────────────────────────────────────────────────
log(`huldra: planning${epic ? ` epic ${epic}` : ''}${onlyStories ? ` (stories ${onlyStories.join(', ')})` : ''} in ${root}`)
const plan = await agent(plannerPrompt(), { label: 'planner', phase: 'Plan', schema: PLAN_SCHEMA })
const stories = plan.stories || []
if (!stories.length) {
  log(`huldra: nothing to build — ${plan.notes || 'all selected stories already done or filtered out'}`)
  return { epic, root, planNotes: plan.notes || '', built: [], stopped: false, reentrant: true }
}
log(`huldra: ${stories.length} story(ies) to build: ${stories.map((s) => s.key).join(', ')}`)

const built = []
let stopped = false

// SEQUENTIAL across stories (single dev, no parallelism) — story N+1 builds on N's tree.
for (const story of stories) {
  let report = await agent(builderPrompt(story), { label: `brok:${story.key}`, phase: 'Build', schema: BUILDER_SCHEMA })

  let accepted = false
  let reviews = []
  let attempt = 0
  for (; attempt <= policy.maxRetries; attempt++) {
    if (attempt > 0) {
      const reasons = reviews
        .filter(Boolean)
        .flatMap((r) => (r.verdict === 'reject' || r.reproducedTestFailure ? (r.blockers && r.blockers.length ? r.blockers : ['rejected (no explicit blocker given)']) : []))
      log(`huldra: ${story.key} retry ${attempt}/${policy.maxRetries} — ${reasons.length} blocker(s)`)
      report = await agent(retryPrompt(story, reasons), { label: `brok:${story.key}:retry${attempt}`, phase: 'Build', schema: BUILDER_SCHEMA })
    }
    // The ONLY fan-out: independent adversarial reviewers vote.
    reviews = await parallel(
      range(policy.voters).map((i) => () =>
        agent(reviewerPrompt(story, i), { label: `sindri:${story.key}:v${i + 1}`, phase: 'Review', schema: REVIEW_SCHEMA })
      )
    )
    const valid = reviews.filter(Boolean)
    const accepts = valid.filter((r) => r.verdict === 'accept').length
    // Executed evidence beats votes: a reviewer who REPRODUCED a failing test run
    // hard-blocks acceptance regardless of the tally (epic-1 finding: a correct,
    // reproduced flake dissent was outvoted 2-1).
    const hardBlocks = valid.filter((r) => r.reproducedTestFailure)
    log(`huldra: ${story.key} review attempt ${attempt + 1} — ${accepts}/${valid.length} accept (need ${policy.threshold})${hardBlocks.length ? ` — HARD BLOCK: ${hardBlocks.length} reviewer(s) reproduced a failing test run` : ''}`)
    if (!hardBlocks.length && accepts >= policy.threshold) { accepted = true; break }
  }

  if (!accepted) {
    log(`huldra: ${story.key} REJECTED after ${attempt} attempt(s) — stopping epic.`)
    built.push({ key: story.key, title: story.title, accepted: false, attempts: attempt, report, reviews: reviews.filter(Boolean), commitSha: null })
    stopped = true
    break
  }

  const manifest = await agent(manifestPrompt(story), { label: `commit:${story.key}`, phase: 'Commit', schema: MANIFEST_SCHEMA })
  log(`huldra: ${story.key} ACCEPTED → status:done${manifest.commitSha ? ` @ ${manifest.commitSha}` : ''}`)
  built.push({
    key: story.key,
    title: story.title,
    accepted: true,
    attempts: attempt + 1,
    report,
    reviews: reviews.filter(Boolean),
    commitSha: manifest.commitSha || null,
    statusUpdated: manifest.statusUpdated,
  })
}

return { epic, root, planNotes: plan.notes || '', built, stopped, reentrant: false }
