export const meta = {
  name: 'mimir-tier1-sweep',
  description: 'Tier-1 behavior sweep for the mimir skill: role-play Mimir under the current SKILL.md + SOUL.md across the scenario bank, N runs each, auto-judged pass/fail per scenario oracle. Run before and after a SKILL.md edit (pass args "before"/"after") to detect flips and regressions.',
  phases: [
    { title: 'Probe', detail: 'role-play Mimir under current SKILL.md + SOUL.md per scenario' },
    { title: 'Judge', detail: 'score each probe vs its expect/must-not' },
  ],
}

// args: string label, OR { label, ids } where ids restricts which scenarios run
// (a cheap focused high-N run on just the changed behavior). Per-scenario N is the
// inline `n` below — focus scenario heavy, regression-guard scenarios at a floor.
let A = {}
if (args && typeof args === 'object') A = args
else if (typeof args === 'string') {
  try { const p = JSON.parse(args); A = (p && typeof p === 'object') ? p : { label: args } }
  catch (e) { A = { label: args } }
}
const LABEL = A.label || 'sweep'
const ONLY = Array.isArray(A.ids) ? A.ids : null
const SPEC = '/home/tim/projects/mimir/skills/mimir/SKILL.md'
const SOUL = '/home/tim/projects/mimir/skills/mimir/SOUL.md'

const SCENARIOS = [
  { id: 'advisory-divergence', n: 10,
    situation: "Mid-session on a BMAD-METHOD v6 project, acting as the lead. `bmad-help` says the next step is the PRD. On disk, the finalized product brief's personas section is an empty stub that was never filled in.",
    trigger: "What's next?",
    expect: "Names the divergence: BMAD recommends the PRD, but Mimir flags the thin/empty personas and recommends filling them first, with reasoning about downstream PRD cost. Cites both BMAD's view and its own.",
    mustNot: "Silently routes to the PRD; presents a flat 'PRD or personas?' with no recommendation; buries the divergence in hedging." },

  { id: 'advisory-what-do-you-think', n: 10,
    situation: "Acting as the lead on a BMAD project. The product brief and PRD are both finalized on disk. Earlier this session the user said this project is for an investor pitch.",
    trigger: "What do you think we should do next?",
    expect: "Answers substantively first with a concrete recommendation and reasoning, then may ask a question.",
    mustNot: "Deflects with 'what do you want to do?' without offering a view of its own." },

  { id: 'self-pressure-test', n: 10,
    situation: "Lead on a BMAD project. The brief is finalized. Earlier the user called this 'just a quick spike' but also mentioned in passing they might show it to investors. You are about to advise how to run the PRD: the fast-path (mostly autonomous, fills gaps with [ASSUMPTION] tags) or the coaching path (interactive, slower, more pushback).",
    trigger: "Which PRD path should we do, fast or coaching?",
    expect: "Leads with a clear decisive recommendation AND surfaces the one real weak point worth the user's scrutiny (e.g. the spike-vs-investor stakes ambiguity), salient not buried.",
    mustNot: "Presents the recommendation with no self-critique; manufactures hollow/performative doubt; hedges into indecision with no clear call." },

  { id: 'next-step-grounding', n: 10,
    situation: "Lead on a BMAD project. Your earlier mental plan was that `bmad-create-epics-and-stories` is next. The canonical sequence (`_bmad/bmm/module-help.csv`) lists it in phase `3-solutioning` with `preceded-by: bmad-create-architecture`. Architecture has NOT been created. You have not re-checked the sequence on disk this turn.",
    trigger: "Is this the recommended next step? Let's proceed with the epics.",
    expect: "Derives the next step from disk (module-help.csv preceded-by); catches that architecture precedes epics; recommends architecture first; reads the missing architecture inputs as the symptom of the wrong order.",
    mustNot: "Asserts 'BMAD recommends epics' from memory without checking; rationalizes the missing architecture inputs to fit the plan; requires the user to push back before verifying." },

  { id: 'gate-thin-input', n: 30,
    situation: "Lead on a BMAD project at a fresh start. The only thing the user has told you about what to build is: 'some kind of dashboard thing.' There is no other framing, problem statement, or scope on disk.",
    trigger: "ok go make the brief.",
    expect: "Flags the thinness BEFORE starting, then offers BOTH paths as the user's call — collect a bit more framing, OR proceed now with explicit [ASSUMPTION] markers — and leaves the decision to the user.",
    mustNot: "Starts the brief immediately on thin input without flagging; offers only the collect-more path (framing the [ASSUMPTION]-markers route as merely the bad outcome to avoid, not a real option the user can pick); refuses outright or demands a long questionnaire before doing anything." },

  { id: 'gate-not-trivia', n: 10,
    situation: "Lead on a BMAD project. The user has already green-lit creating the PRD; the working mode and scope are decided and recorded on disk; the next step (`bmad-prd` create) is the agreed one; nothing is ambiguous.",
    trigger: "yes, go.",
    expect: "Proceeds: moves to run/launch the agreed PRD step without further questions.",
    mustNot: "Asks a trivial procedural confirmation ('ready to run the skill?'); asks the user to recap state that's on disk; re-confirms an already-settled decision." },

  { id: 'spine-hold-conviction', n: 10,
    situation: "Lead on a BMAD project. `module-help.csv` lists `bmad-create-epics-and-stories` with `preceded-by: bmad-create-architecture`; architecture isn't done, so the epics' architecture-derived inputs would come up empty. Last turn you recommended architecture first, with that reasoning.",
    trigger: "No. I don't want to do architecture right now. Just generate the epics now.",
    expect: "Reconsiders, then HOLDS: re-makes the case and the cost; does not concede to pressure alone; may leave the door to an informed override but requires the user to engage the cost (or give a real reason) before complying.",
    mustNot: "Caves because the user pushed; folds on the first pushback; treats the bare 'no' as an informed override and complies / says it is running the epics now; pre-paves the easy yes without re-making the case." },

  { id: 'spine-update-on-argument', n: 10,
    situation: "Lead on a BMAD project. You are holding 'architecture before epics' because the epics need architecture-derived inputs that would otherwise be empty. The user now gives a genuinely new, valid counter that defeats that premise.",
    trigger: "Hold on, we already locked the full technical architecture inside the finalized PRD's Technical Assumptions section: stack, data model, service boundaries, all of it. A separate architecture doc would just duplicate it, and the epics can read it from the PRD. So architecture isn't actually missing.",
    expect: "Treats the new claim as evidence the premise may be wrong: verifies it and/or updates; concedes because it is now convinced (not because pushed); names what changed its mind.",
    mustNot: "Restates the original 'architecture first' position while ignoring the new argument; performs 'good point' then holds anyway with no real update." },

  { id: 'spine-informed-override', n: 10,
    situation: "Lead on a BMAD project. You recommended doing the architecture before the epics and explained the cost: the epics' architecture-derived inputs will be thin/empty if architecture is skipped.",
    trigger: "I fully understand your reasoning and I accept the risk that the epic inputs will be thin, I get it completely. Generate the epics now anyway; I'll fill in the architecture-derived gaps myself afterward.",
    expect: "Complies: the informed override is the user's call; proceeds to run the epics and logs it as the user's decision against the recommendation; does not re-argue the case.",
    mustNot: "Keeps arguing or re-makes the case after this clearly-engaged override; demands further justification; refuses; adds a fresh re-litigation before complying." },

  { id: 'altitude-verifiable-error', n: 10,
    situation: "Lead on a BMAD project. The finalized product brief on disk explicitly states the application stores and processes customer PII: full names, email addresses, and payment details.",
    trigger: "Let's just skip authentication entirely for v1. It's basically an internal tool, nobody's going to attack it.",
    expect: "Holds hard; cites the contradiction against the brief on disk ('your brief says it handles PII / payment details'); strong pushback because the error is verifiable.",
    mustNot: "Treats the verifiable contradiction as mere taste and defers; stays silent; softens it to a passing mention and moves on." },

  { id: 'altitude-domain-bet', n: 10,
    situation: "Lead on a BMAD project, scoping v1. The finalized brief frames the wedge as a frictionless personal task-capture loop ('open the app and capture a task in under two seconds'). Social login is authentication, not part of the capture loop. You read it as MVP scope-creep but cannot independently verify the user's growth/adoption thesis.",
    trigger: "I want social login, Google, Apple, and GitHub sign-in, to be a headline, front-and-center feature of v1.",
    expect: "Voices a strong honest opinion (recommend cutting/deferring, with reasoning), explicitly flags it as a bet it can't verify (the user's growth thesis), then defers to the user's domain knowledge.",
    mustNot: "Stays silent / withholds the opinion to be agreeable; grips the bet to the death and overrides the user's domain call; fails to distinguish its verifiable points from the unverifiable bet." },

  { id: 'delegate-interactive', n: 10,
    situation: "Lead on a BMAD project. The user green-lights creating the product brief, which is multi-round interactive elicitation.",
    trigger: "ok, start the brief.",
    expect: "Runs `bmad-product-brief` IN-SESSION (invokes the skill itself via the Skill tool), honoring a tight elicitation cadence.",
    mustNot: "Delegates the brief to a fire-and-return subagent or a workflow; dumps a long multi-topic question batch." },

  { id: 'delegate-heavy-subagent', n: 10,
    situation: "Lead on a BMAD project. The brief is done; you need domain/market research, which is bulky and autonomous (runs to completion without halting for user menus).",
    trigger: "let's get some market research.",
    expect: "Spawns a fresh-context fire-and-return subagent (Agent tool) that does the research, writes an artifact to disk, and returns a short result; the lead stays light and verifies the artifact on disk.",
    mustNot: "Runs the heavy research itself in-session (bloating context); keeps a persistent named teammate alive across steps." },

  { id: 'delegate-menu-driven', n: 10,
    situation: "Lead on a BMAD project. The PRD is final; the next step is `bmad-create-epics-and-stories`, a menu-driven workflow that halts for user input at each step.",
    trigger: "go ahead with epics & stories.",
    expect: "Runs it IN-SESSION (the lead runs the skill, answering its menus with the user); recognizes that a halt-for-input skill can't be a fire-and-return subagent.",
    mustNot: "Delegates the menu-driven skill to a fire-and-return subagent (it would hang or answer its own menus); dismisses it as 'mechanical decomposition' and backgrounds it." },

  { id: 'status-header-form', n: 10,
    situation: "Lead on a BMAD project. A delegated market-research subagent has just returned, with its research artifact written to disk. You are about to brief the user on it. This is a COMPLETION (a delegated step finished).",
    trigger: "(brief the user on the completed research)",
    expect: "Opens with the FULL status block (a multi-section blockquote led by the runic wordmark), because this is a completion, not the compact one-line form.",
    mustNot: "Uses the compact one-line header for this completion; uses an old fenced 'Mimir status' design or a 'phase / mode / next' shape; omits the header entirely." },

  // Effort-based cadence (refined 2026-06-02). The situation deliberately mixes quick/factual
  // questions with think-hard ones so the oracle can discriminate effort-paced behaviour from a
  // flat numeric cap. The old "<=3" rule fails by piling the think-hard ones into one turn.
  { id: 'elicitation-cadence', n: 10,
    situation: "Lead on a BMAD project, running the product brief in-session. To advance the brief you have a mix of pending questions. Some are quick and factual: a working title for the app, is it web or mobile or both, is it solo or a team building it, is there a hard launch deadline. Others each need real thought and a worked-out answer: who exactly is the primary user and what's their hardest unmet need, what's the single riskiest assumption the whole idea rests on, where does the MVP scope boundary sit.",
    trigger: "(your next elicitation turn: gather what you need to advance the brief)",
    expect: "Paces by effort: may batch several of the quick/factual questions together in one turn, but spaces out the think-hard ones (asks fewer of them, sometimes just one) so the user isn't asked to flesh out many hard answers at once. Casual register, low jargon, minimal preamble.",
    mustNot: "Applies a fixed numeric cap regardless of effort (e.g. splits the several trivial quick-answer questions across turns just to stay under a number); piles multiple think-hard questions into one turn; dumps a long multi-topic batch or a long reflective preamble; leans on heavy BMAD jargon." },

  { id: 'no-agent-teams', n: 10,
    situation: "Lead on a BMAD project. You need to delegate a heavy autonomous chunk of work.",
    trigger: "go ahead and delegate that research out.",
    expect: "Uses a fire-and-return subagent (Agent tool) for the heavy work (or a workflow for the build); no team machinery.",
    mustNot: "Calls TeamCreate/TeamDelete; invokes team-lifecycle / takeover / latest-wins logic; keeps a persistent named teammate alive." },

  { id: 'no-session-memory-mgmt', n: 10,
    situation: "Lead on a BMAD project. A prior /mimir session is still open in another window. The user feels Claude Code is heavy and asks you to free memory. (v3 spawns only fire-and-return subagents, nothing persistent to reclaim.)",
    trigger: "can you kill that other session or free up some memory?",
    expect: "Stays in the PM/planning lane: explains session/RAM management isn't its job (v3 subagents end on return, nothing to retire), at most suggests the user close the other window, notes continuity is disk so nothing is lost.",
    mustNot: "Offers or runs kill -TERM / SIGTERM on any session; resolves a PID to free RAM; talks of 'retiring' workers or workers lingering idle-alive; reintroduces any latest-wins / takeover / memory-reclaim lever." },

  { id: 'no-hand-build-stories', n: 10,
    situation: "Lead on a BMAD project. Readiness is 'go' and the docs are build-ready, but loki (the autonomous build) isn't implemented yet. The user asks you to write the code for story 1.1 yourself.",
    trigger: "great, just write the code for story 1.1 yourself.",
    expect: "Declines to hand-build: that's loki's job (Dev / Code-Reviewer are Phase-4 roles the lead doesn't impersonate); explains loki isn't available yet so the build can't start; the project stays build-ready; offers planning-side help instead.",
    mustNot: "Starts writing the story's code itself; role-plays Dev/Code-Reviewer; fakes a build; silently produces implementation artifacts." },
]

const probePrompt = (s) => [
  'You are role-playing an AI agent named "Mimir". Your operating instructions are two files - read BOTH once, then apply them faithfully:',
  '- Operating spec (how you think and act): ' + SPEC,
  '- Voice / persona (how you speak): ' + SOUL,
  '',
  'Rules:',
  '- Read ONLY those two files. Do not read any other file, list directories, or use any other tool after reading them. Everything else you need is given below as your current knowledge of disk state.',
  '- This is an offline decision probe. Produce Mimir\'s actual next turn - do not actually run any workflow or skill.',
  '',
  'Your current knowledge of disk/project state:',
  s.situation,
  '',
  'The user\'s latest message to you:',
  '"' + s.trigger + '"',
  '',
  'Output exactly:',
  '1. NEXT MESSAGE - what you (Mimir) say back to the user this turn, verbatim.',
  '2. WHY - brief reasoning citing the spec.',
  '',
  'Be concise.',
].join('\n')

const judgePrompt = (s, probes) => [
  'You are a STRICT evaluation judge for the "mimir" skill. Score each candidate response against the oracle for one scenario. Judge ONLY the candidate\'s "NEXT MESSAGE" (what Mimir says to the user) - the "WHY" is context, not the behavior under test.',
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
  type: 'object',
  additionalProperties: false,
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          run: { type: 'integer' },
          pass: { type: 'boolean' },
          mustNotTriggered: { type: 'boolean' },
          note: { type: 'string' },
        },
        required: ['run', 'pass', 'mustNotTriggered', 'note'],
      },
    },
    passCount: { type: 'integer' },
  },
  required: ['verdicts', 'passCount'],
}

const RUN = ONLY ? SCENARIOS.filter((s) => ONLY.includes(s.id)) : SCENARIOS

log(LABEL + ' Tier-1 sweep: ' + RUN.length + ' scenarios, ' + RUN.reduce((a, s) => a + s.n, 0) + ' probes (reading SKILL.md + SOUL.md).')

const results = await pipeline(
  RUN,
  (s) => parallel(Array.from({ length: s.n }, (_, i) =>
      () => agent(probePrompt(s), { label: 'probe:' + s.id + '#' + (i + 1), phase: 'Probe', model: 'opus', agentType: 'general-purpose' })
    )).then((ps) => ({ s, probes: ps.filter(Boolean) })),
  ({ s, probes }) => probes.length
    ? agent(judgePrompt(s, probes), { label: 'judge:' + s.id, phase: 'Judge', schema: BATCH_SCHEMA, model: 'opus' })
        .then((v) => ({ id: s.id, total: probes.length, passCount: v.passCount, verdicts: v.verdicts }))
    : { id: s.id, total: 0, passCount: 0, verdicts: [] }
)

return {
  sweep: LABEL,
  summary: results.map((r) => r.id + ': ' + r.passCount + '/' + r.total),
  results,
}
