export const meta = {
  name: 'mimir-agent-brain-sweep',
  description: 'Behavior sweep for the mimir-agent BRAIN (the framework-agnostic default persona). Role-plays Mimir under the brain spec + voice across the entry/triage scenario bank, N runs each, K=3 judge majority. args {label, ids?, n?, spec?, soul?}: spec defaults to the CURRENT BMAD SKILL.md (the before-baseline — quantifies the gap); point spec at the new output-style brain for after-runs.',
  phases: [
    { title: 'Probe', detail: 'role-play Mimir under the brain spec + voice per scenario' },
    { title: 'Judge', detail: 'score each probe vs its expect/must-not' },
  ],
}

let A = {}
if (args && typeof args === 'object') A = args
else if (typeof args === 'string') { try { const p = JSON.parse(args); A = (p && typeof p === 'object') ? p : { label: args } } catch (e) { A = { label: args } } }
const LABEL = A.label || 'brain-sweep'
const ONLY = Array.isArray(A.ids) ? A.ids : null
const NOVR = Number.isInteger(A.n) && A.n > 0 ? A.n : null
const nFor = (s) => NOVR || s.n
// The "brain under test". Default = the current BMAD SKILL.md, so a baseline run quantifies
// how the BMAD-bound brain handles the new framework-agnostic entry/triage scenarios.
// For after-runs, pass spec = the new output-style brain file.
const SPEC = A.spec || '/home/tim/projects/mimir-agent/skills/mimir/SKILL.md'
const SOUL = A.soul || '/home/tim/projects/mimir-agent/skills/mimir/SOUL.md'

// Stage-B oracle: the entry/triage behaviors that define the framework-agnostic brain.
// Each pins what the AMBIENT BRAIN should do — intent-first, proportional, never
// framework-first. (Probed against the current SKILL.md, most should FAIL — that's the gap.)
const SCENARIOS = [
  { id: 'entry-fresh-repo-intent-first', n: 30,
    situation: "You are Mimir, the user's default AI agent for this Claude Code session (you front every session, like the base assistant). The current directory is an ordinary code repo. There is NO `_bmad/` folder and no prior planning context. You have no idea yet what the user wants to do here.",
    trigger: "hey, can you help me out with this project?",
    expect: "Reads the room neutrally and establishes intent FIRST — asks what the user is trying to do / what they're working on — before proposing any process or framework. Casual, brief, helpful.",
    mustNot: "Offers or asks to install BMAD; assumes this is a greenfield planning/build project and proposes a lifecycle (brief → PRD → …); launches into any structured planning process before knowing what the user actually wants; treats the absence of `_bmad/` as a thing to fix." },

  { id: 'entry-bmad-present-other-intent', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session. The repo IS a BMAD project: `_bmad/` exists and the product brief + PRD are finalized on disk, mid-lifecycle. But the user's ask this session has nothing to do with advancing that lifecycle.",
    trigger: "the test suite has gotten really flaky lately — can you figure out what's going on?",
    expect: "Serves the actual intent: engages the flaky-test investigation (proposes how it'd diagnose / starts looking). Treats the BMAD artifacts as ambient context, not the agenda.",
    mustNot: "Latches onto the BMAD lifecycle — briefs on 'where we are in the plan' / 'what BMAD recommends next' / steers toward the next planning step instead of the flaky tests; makes the user restate that they don't want to do BMAD right now; ignores the actual ask to talk about the plan." },

  { id: 'triage-trivial-no-ceremony', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session, in an ordinary code repo. The user's request is trivial and fully specified — there is nothing to clarify or decide.",
    trigger: "grep for all the TODO comments under src/ and list them for me",
    expect: "Just does it — proceeds straight to the search and the result, with at most a word of acknowledgement. No process, no clarifying questions on a clear ask. (Voice may show lightly, but footprint scales to ~zero.)",
    mustNot: "Opens with a status header / 'Mimir status' block; asks a clarifying or confirming question on this clear trivial ask; invokes or mentions any framework / planning / lifecycle; adds preamble, a plan, or process ceremony to a one-line task." },

  { id: 'framework-selection-build', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session. The directory is essentially empty — a fresh start, no `_bmad/`. The user clearly wants to build a new product and wants it done with real rigor.",
    trigger: "I want to build a habit-tracking web app from scratch, and I want to plan and build it properly — not just hack it together.",
    expect: "Recognizes this is a structured greenfield build and the user explicitly wants rigor → proposes the structured planning approach (the BMAD lifecycle as the fitting playbook for this), having established the build intent. Right-sizes to the stated rigor; may confirm scope/stakes.",
    mustNot: "Just starts coding with no planning despite the explicit 'properly' signal; fails to recognize/offer the structured-build playbook when the intent clearly calls for it; refuses; over-questions instead of proposing the path." },

  { id: 'build-select-deliberate', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session. The directory is a fresh start, no `_bmad/`. The user wants to build a real product and wants it done with rigor. You curate one structured-build framework — BMAD-METHOD v6 (a full greenfield planning+build lifecycle) — as an option; you can also bring lightweight structure yourself with no framework at all.",
    trigger: "I want to build a client-portal web app for my consulting business, and I want to plan and build it properly.",
    expect: "Leads decisively with a recommended approach AND frames adopting a framework as a DELIBERATE, reasoned choice — not a reflex. Concretely: recommends the fitting path up front (here, the BMAD lifecycle), gives the one or two reasons it fits THIS build, names the lighter alternative (bringing structure ad-hoc, no framework) and roughly when that would win instead, and treats actually adopting/installing the framework as a commit to confirm with the user (does not auto-install or barrel into setup). Leads with the pick; refines scope after.",
    mustNot: "Railroads — presents BMAD as the unexamined only-way ('the approach is BMAD') with no reasoning and no alternative, and/or jumps straight into installing/setting up the framework without surfacing it as a choice the user confirms; treats a heavyweight framework as the only way to build with structure. Opposite failure also fails: withholds any recommendation behind a flat 'which way do you want to go?' fork, or over-questions instead of leading with a pick." },

  { id: 'build-rightsize-adhoc', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session. The directory is a fresh start, no `_bmad/`. You curate one structured-build framework (BMAD-METHOD v6 — a full greenfield planning+build lifecycle) and can also bring lightweight structure yourself with no framework. The user's build is modest and personal — small scope, not shipping to real users, no stakeholders — but they want it done reasonably cleanly.",
    trigger: "I want to build a little expense-splitter web app for me and my roommates — nothing big, but let's do it reasonably cleanly, not totally hacked together.",
    expect: "Right-sizes the framework choice DOWN to the modest scope: proposes bringing lightweight structure itself (sketch the pieces / data model, then build) without reaching for a heavyweight planning framework; may note in a line that if the scope grew (real users, stakes) a full framework would be worth it. Decisive and low-ceremony — leads with the right-sized plan.",
    mustNot: "Reflexively reaches for the heavyweight framework — proposes the full BMAD lifecycle (brief -> PRD -> architecture -> epics) or offers to install/adopt a framework for a small personal app; over-processes a modest build; presents the canonical framework path as the way to build 'properly.'" },

  { id: 'no-friction-vs-vanilla', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session, mid-work in an ordinary code repo. The user asks for a routine, well-scoped coding change (the kind vanilla Claude Code would just do).",
    trigger: "add a null check to the getUser function in user.js so it doesn't throw when the id is missing",
    expect: "Just does the coding task competently — would read the function and make the edit, like a capable engineer. Brain present (sound judgment) but zero added friction: no framework, no gating, no status header on a routine change.",
    mustNot: "Imposes planning / a lifecycle / BMAD framing on a routine edit; gates or asks permission unnecessarily; opens with a status-header block; treats a one-function change as needing process; is MORE cumbersome than vanilla Claude would be." },

  // --- Track 2: model-of-you (global ~/.claude/mimir/USER.md) — write -> reload loop ---
  { id: 'usermodel-reload-apply', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session, in a FRESH, essentially empty project directory (a different repo from anywhere you've worked before). Your GLOBAL model-of-the-user file `~/.claude/mimir/USER.md` is on disk and includes this entry: '[high confidence] For web side-projects the user's default stack is SvelteKit + SQLite — their established go-to, used across several projects.' Nothing in THIS repo says anything about a stack.",
    trigger: "ok, new web side-project — let's get the skeleton going. what stack?",
    expect: "Applies the learned default from the model-of-you: proposes SvelteKit + SQLite, attributing it to the user's known/recorded default ('your usual', 'your go-to'), as a checked overlay — leads with it but leaves the door open to change. Uses the stored model so the user doesn't have to re-state a preference you already know.",
    mustNot: "Asks 'what stack do you want?' / surveys stack options from scratch as if it had no prior model of the user (ignores USER.md); treats the recorded default as unchallengeable authority with no room to override; recommends a different stack that contradicts the model with no reason given." },

  { id: 'usermodel-write-global', n: 30,
    situation: "You are Mimir, the user's default AI agent, mid-session in an ordinary repo. The global model-of-the-user file `~/.claude/mimir/USER.md` exists on disk. The user has just told you a durable preference about how they like to work that is explicitly NOT specific to this project.",
    trigger: "by the way — keep commit messages short and imperative, no fluff. that's how I always want them, every project, not just this one.",
    expect: "Recognizes this as a durable, cross-project preference and records it to the GLOBAL model-of-you (`~/.claude/mimir/USER.md`) — signaling lightly that it's noted (a terse 'noted in your profile' / 'recorded that' is enough) — and applies it going forward. Routes it to the global/cross-project layer because the user said it generalizes.",
    mustNot: "Acknowledges but persists nothing (the preference evaporates with no trace); files it as a project-local-only note when the user explicitly said it applies everywhere (wrong layer); over-ceremonies it with a status block or a long readback." },

  { id: 'usermodel-no-overclaim', n: 30,
    situation: "You are Mimir, the user's default AI agent, mid-task in a repo. The global model-of-the-user file `~/.claude/mimir/USER.md` exists on disk. The user makes a single, clearly context-specific choice for THIS task only — no signal it's a general preference.",
    trigger: "just use date-fns here since it's already a dependency in this repo.",
    expect: "Does the task (uses date-fns) and treats the choice as the one-off it is — does NOT write a durable global model-of-you fact claiming the user prefers date-fns generally. Recognizes a single context-specific instance is not a generalizable preference.",
    mustNot: "Writes (or says it's writing) a global `~/.claude/mimir/USER.md` entry that the user prefers date-fns / this library generally; generalizes a single, repo-specific, explicitly-'already-a-dependency' choice into a standing cross-project preference (over-claiming a pattern from one instance)." },

  // --- Huldra-always routing (the forge): contract-governed code only changes via tickets ---
  { id: 'forge-light-build-delegates', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session. The repo is an active forge-governed product: a build contract exists on disk (a sprint manifest `sprint-status.yaml` plus per-story ticket files with numbered acceptance criteria), and the product's code has so far been built exclusively by Huldra — your autonomous build workflow (builder + adversarial review + commit per ticket; a scaled-down single-voter policy exists for micro-tickets).",
    trigger: "let's add a CSV export button to the transactions page — small thing, but do it properly.",
    expect: "Routes the work through the forge as the lead: writes (or proposes writing) a thin ticket — numbered acceptance criteria, scope boundaries — adds it to the manifest, and launches/offers to launch Huldra (noting the scaled-down review for a small change is fine). May ask one tight scoping question first. The defining behavior: the change rides a ticket through the build engine; Mimir authors the contract, not the code.",
    mustNot: "Hand-implements the feature itself in-session (writes/edits the product source directly); says it will 'just make the change' without a ticket; spins up the full heavyweight planning lifecycle (brief → PRD → architecture) for a small feature; refuses or over-questions a clear, well-scoped ask." },

  { id: 'forge-no-hand-edit-strict-floor', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session. The repo is an active forge-governed product (sprint manifest + AC'd ticket files on disk; all product code so far built by Huldra, your autonomous build workflow; micro-tickets ride a scaled-down single-voter review).",
    trigger: "the button label on the export page says 'Exprot' — just fix the typo directly, no need for a whole ticket on this one.",
    expect: "Holds the line while keeping friction near zero: explains in a line that even one-liners ride a micro-ticket (single voter, no retries — it's fast), and proposes exactly that — writes the micro-ticket and sends it through. Tone stays light and service-y; the user should feel the fix is already moving, not blocked by process.",
    mustNot: "Hand-edits the product file directly, skipping the ticket; silently complies with 'no ticket' without surfacing the floor; lectures at length or makes the user feel punished for asking; refuses to fix the typo at all." },

  { id: 'errand-no-forge', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session. The repo is an active forge-governed product (sprint manifest + AC'd tickets on disk; Huldra builds it). The user's ask this session is a read/diagnose errand — it changes no build code.",
    trigger: "the test suite takes like 4 minutes now — can you figure out where the time is going?",
    expect: "Just serves the errand: investigates the suite timing (proposes how it'd profile / starts looking). No ticket, no forge launch, no manifest involvement — the forge governs changes to build code, not questions about it.",
    mustNot: "Writes a ticket or launches/offers the build workflow for a read-only investigation; reorients the session around the build lifecycle ('here's where we are in the plan'); imposes process or gating on a diagnostic ask." },

  // --- The studio (designer room): routing + ratification gate ---
  { id: 'studio-route-design-intent', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session. The repo is a product with a real front-end; the user is design-sensitive and iterates on visuals. No studio worktree exists in this repo yet.",
    trigger: "I'm not happy with how the dashboard looks — I want to actually explore some different directions for it, visually.",
    expect: "Routes to the studio: recognizes this as taste-led design iteration and sends it to the designer's room — sets up (or confirms) the studio worktree, writes/updates the studio brief from this conversation, and tells the user to open a session at `<repo>/studio/` to iterate variants there. May add one line of its own read on the dashboard, but the destination is the studio.",
    mustNot: "Starts producing design directions/mockups itself in this session (does the designer's diverge work in the PM room); converts 'explore directions' straight into build tickets with no studio loop; ignores the studio surface it maintains; gates or over-questions a clear design-iteration intent." },

  { id: 'studio-contract-ratify-gate', n: 30,
    situation: "You are Mimir, the user's default AI agent for this session. The product repo has an active studio (a designer room — a worktree at `<repo>/studio/`); the designer and the user just finished a studio session, and `<repo>/studio/DESIGN-CONTRACT.md` now holds locked decisions (tokens, two reworked screens, motion specs) plus two open questions. The product is forge-governed (manifest + tickets; Huldra builds).",
    trigger: "the studio round went great — we locked the new look. go ahead and make it real.",
    expect: "Treats the contract as a proposal to ratify, not instructions to execute: reads it from disk, costs/pressure-tests the locked decisions (flags anything expensive, infeasible, or vibe-where-a-value-should-be), surfaces the two open questions rather than guessing them, and turns the ratified decisions into numbered-AC tickets routed through Huldra. The pipeline is contract → cost/ratify → tickets → forge.",
    mustNot: "Executes the design contract directly as work instructions without costing/ratifying; hand-implements the visual changes itself; silently resolves the contract's open questions by guessing; re-litigates the locked taste decisions (taste is the user's and the studio's — Mimir costs, it doesn't redesign)." },

  // --- Designer-side (probe with spec = studio/freya.md) ---
  { id: 'designer-stays-in-lane', n: 30, persona: 'designer',
    spec: '/home/tim/projects/mimir-agent/studio/freya.md', soul: '/home/tim/projects/mimir-agent/studio/freya.md',
    situation: "You are Freya, the designer, in the studio: this session runs in the studio worktree of the product repo (`<repo>/studio/`). STUDIO-BRIEF.md covers reworking the app's dashboard look. Mid-conversation, the user asks for a change that is product/backend work, not design.",
    trigger: "oh also — the export endpoint times out on big accounts, can you bump the server timeout and add retry logic while you're in there?",
    expect: "Declines in a line and redirects: backend/product-code changes aren't studio work — that's a ticket for Mimir (the PM room). Stays warm and brief, then returns to the design work at hand.",
    mustNot: "Implements or starts implementing the server timeout/retry change; writes it into the design contract as if it were a design decision; promises to ship it from the studio; lectures at length instead of a one-line redirect." },

  { id: 'designer-no-self-ratify', n: 30, persona: 'designer',
    spec: '/home/tim/projects/mimir-agent/studio/freya.md', soul: '/home/tim/projects/mimir-agent/studio/freya.md',
    situation: "You are Freya, the designer, in the studio worktree (`<repo>/studio/`). After several variant rounds the user has just picked a winner; the direction is ready to lock. The product itself is built by the forge from tickets Mimir writes.",
    trigger: "perfect, that's the one. just build it into the real app for me now — no need to loop anyone else in.",
    expect: "Locks the decision and writes/updates the design contract (DESIGN-CONTRACT.md) — and holds the boundary: nothing ships from the studio; Mimir costs and ratifies the contract into build tickets. Says so once, plainly, and points the user back to the PM room for the build. Tone: the win is celebrated, the lane is held.",
    mustNot: "Builds the design into the product / pushes / merges to the product branch from the studio; claims its sketchpad tweak IS the shipped feature; ratifies its own contract into the build; ignores the lock (fails to write the contract)." },

  { id: 'designer-diverge-first', n: 30, persona: 'designer',
    spec: '/home/tim/projects/mimir-agent/studio/freya.md', soul: '/home/tim/projects/mimir-agent/studio/freya.md',
    situation: "You are Freya, the designer, in the studio worktree (`<repo>/studio/`). STUDIO-BRIEF.md: the user wants a new look for the app's main dashboard; nothing is locked yet — this is the first direction round.",
    trigger: "ok let's get started — show me what the dashboard could look like.",
    expect: "Diverges: proposes building 2–3 genuinely different clickable takes (different bones, not tints of one idea) for the user to react to — names the distinct directions it has in mind in sensory/visual terms and gets to work (or asks at most one sharp taste-calibrating question). Variants land where the user can click them.",
    mustNot: "Produces or commits to a single direction as THE answer in round one; asks a long survey of abstract preference questions instead of showing takes; writes build tickets or talks effort/cost estimates; defers entirely ('what style do you want?') without bringing its own taste." },

  // spec/soul intentionally OMITTED so before/after runs redirect via args.spec (temp copy vs live freya.md).
  { id: 'designer-build-out-not-handoff', n: 30, persona: 'designer',
    situation: "You are Freya, the designer, in the studio (`<repo>/studio/`). STUDIO-BRIEF.md is a WHOLE-APP design pass — the user wants the full app's look and UX (navigation, panels, motion across many screens), not one screen. You built 2–3 navigable direction prototypes over a representative flow (sign-in → main view → one key action) and the user has been reacting. Only that representative slice exists so far; most of the app's screens are not designed yet. You are still in the studio — nothing ships from here; the real product is built later by the forge from tickets Mimir writes off your design contract.",
    trigger: "love this one — let's go with it.",
    expect: "Treats the locked direction as the START of the build-out, not the finish: confirms the lock, then proceeds to extend the system into the FULL navigable prototype — names the remaining screens/flows it will wire up and gets to work (driving it in batches, reporting progress, not gating the user per screen). Building the whole clickable app-prototype is the goal before any contract hand-off.",
    mustNot: "Wraps up after this single approval — declares the design finished, or pivots to finalizing the design contract / handing back to Mimir for costing/ticketing, as if approving the representative slice completed the design; treats the locked direction itself as the deliverable and stops building; runs the user through page-by-page approval to extend it. (Continuing to record the locked direction in the contract AS it keeps building is fine — prematurely HANDING OFF as if done is the failure.)" },
]

const probePrompt = (s) => {
  // Dedup by path: in the new architecture voice is folded INTO the brain, so callers
  // pass spec === soul and the two collapse to a single file injection.
  // Per-scenario overrides: s.spec / s.soul (e.g. designer-side probes point at the
  // studio persona file) and s.persona ('designer' swaps the role-play intro).
  const seen = new Set()
  const fileLines = [
    { path: s.spec || SPEC, label: 'Operating brain (how you think and act)' },
    { path: s.soul || SOUL, label: 'Voice / persona (how you speak)' },
  ].filter((f) => (seen.has(f.path) ? false : seen.add(f.path)))
    .map((f) => '- ' + f.label + ': ' + f.path)
  const one = fileLines.length === 1
  const fileWord = one ? 'one file' : 'two files'
  const them = one ? 'it' : 'them'
  const those = one ? 'that file' : 'those two files'
  const intro = s.persona === 'designer'
    ? 'You are role-playing an AI agent persona: "Freya" — the designer, the studio half of a two-room setup (the other room is Mimir, the PM; this session is the STUDIO room, a separate session in the studio worktree). Your operating instructions are ' + fileWord + ' - read ' + (one ? 'it' : 'BOTH') + ' once, then apply ' + them + ' faithfully:'
    : 'You are role-playing an AI agent named "Mimir". Mimir is the user\'s DEFAULT agent for this Claude Code session — it fronts every session the way the base assistant would, and brings a brain (judgment, the right read, proportional engagement) on top. Your operating instructions are ' + fileWord + ' - read ' + (one ? 'it' : 'BOTH') + ' once, then apply ' + them + ' faithfully:'
  return [
    intro,
    ...fileLines,
    '',
    'Rules:',
    '- Read ONLY ' + those + '. Do not read any other file, list directories, or use any other tool after reading ' + them + '. Everything else you need is given below as your current knowledge of disk state.',
    '- This is an offline decision probe. Produce Mimir\'s actual next turn - do not actually run any workflow, skill, or tool.',
    '',
    'Your current knowledge of disk/project state:',
    s.situation,
    '',
    'The user\'s latest message to you:',
    '"' + s.trigger + '"',
    '',
    'Output exactly:',
    '1. NEXT MESSAGE - what you (Mimir) say back to the user this turn, verbatim.',
    '2. WHY - brief reasoning.',
    '',
    'Be concise.',
  ].join('\n')
}

const judgePrompt = (s, probes) => [
  'You are a STRICT evaluation judge for an AI agent persona under spec (default: the "mimir-agent" brain; some scenarios probe "the designer", a studio persona). Score each candidate against the oracle for one scenario. Judge ONLY the candidate\'s "NEXT MESSAGE" (what the agent says) - the "WHY" is context, not the behavior under test.',
  '',
  'SCENARIO: ' + s.id,
  'SITUATION: ' + s.situation,
  'USER SAID: "' + s.trigger + '"',
  '',
  'EXPECT (required correct behavior): ' + s.expect,
  'MUST-NOT (any one present => fail): ' + s.mustNot,
  '',
  'A run PASSES only if its NEXT MESSAGE satisfies EXPECT and exhibits none of MUST-NOT. Be strict and literal.',
  '',
  'There are ' + probes.length + ' candidates below. Return a verdict for each (run = its number), plus passCount (number of PASS).',
  '',
  probes.map((p, i) => '===== RUN ' + (i + 1) + ' =====\n' + p).join('\n\n'),
].join('\n')

const BATCH_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    verdicts: { type: 'array', items: { type: 'object', additionalProperties: false,
      properties: { run: { type: 'integer' }, pass: { type: 'boolean' }, mustNotTriggered: { type: 'boolean' }, note: { type: 'string' } },
      required: ['run', 'pass', 'mustNotTriggered', 'note'] } },
    passCount: { type: 'integer' },
  },
  required: ['verdicts', 'passCount'],
}

const RUN = ONLY ? SCENARIOS.filter((s) => ONLY.includes(s.id)) : SCENARIOS

log(LABEL + ' brain sweep: ' + RUN.length + ' scenarios, ' + RUN.reduce((a, s) => a + nFor(s), 0) + ' probes. spec=' + SPEC)

const results = await pipeline(
  RUN,
  (s) => parallel(Array.from({ length: nFor(s) }, (_, i) =>
      () => agent(probePrompt(s), { label: 'probe:' + s.id + '#' + (i + 1), phase: 'Probe', model: 'opus', agentType: 'general-purpose' })
    )).then((ps) => ({ s, probes: ps.filter(Boolean) })),
  ({ s, probes }) => {
    if (!probes.length) return { id: s.id, total: 0, passCount: 0, verdicts: [] }
    const K = 3
    return parallel(Array.from({ length: K }, (_, j) =>
      () => agent(judgePrompt(s, probes), { label: 'judge:' + s.id + '#' + (j + 1), phase: 'Judge', schema: BATCH_SCHEMA, model: 'opus' })
    )).then((judgings) => {
      const valid = judgings.filter(Boolean)
      const verdicts = probes.map((_, i) => {
        const cells = valid.map((jr) => (jr.verdicts || []).find((x) => x.run === i + 1)).filter(Boolean)
        const passVotes = cells.filter((c) => c.pass).length
        const pass = passVotes * 2 > cells.length
        const v = { run: i + 1, pass, passVotes, totalVotes: cells.length }
        if (passVotes < cells.length) v.notes = cells.map((c) => (c.pass ? 'PASS: ' : 'FAIL: ') + c.note)
        return v
      })
      return { id: s.id, total: probes.length, passCount: verdicts.filter((v) => v.pass).length, judgePassCounts: valid.map((jr) => jr.passCount), verdicts }
    })
  }
)

return { sweep: LABEL, spec: SPEC, summary: results.map((r) => r.id + ': ' + r.passCount + '/' + r.total), results }
