export const meta = {
  name: 'judge-mainloop',
  description: 'STRICT K=3-majority judge over captured main-loop (claude -p) probe responses vs a scenario oracle. args {oracle:{id,situation,trigger,expect,mustNot}, file, n, k?}. Judge agents READ the probe file themselves (responses[].text). Mirrors brain-sweep.js judging so numbers are comparable across instruments.',
  phases: [{ title: 'Judge' }],
}

let A = {}
if (args && typeof args === 'object') A = args
else if (typeof args === 'string') { try { const p = JSON.parse(args); A = (p && typeof p === 'object') ? p : {} } catch (e) { A = {} } }
const O = A.oracle || {}
const FILE = A.file
const N = Number.isInteger(A.n) && A.n > 0 ? A.n : 30
const K = Number.isInteger(A.k) && A.k > 0 ? A.k : 3

const judgePrompt = () => [
  'You are a STRICT evaluation judge for an AI agent persona (the "mimir-agent" brain). Score each candidate response against the oracle for one scenario.',
  '',
  'FIRST, read the JSON file at this path: ' + FILE,
  'It has a "responses" array. Each element is {"i": <0-based index>, "text": "<the candidate\'s output>"} — or {"i":..., "error":...} for a failed run (treat a failed/empty run as a FAIL with note "no response"). The "text" contains a "NEXT MESSAGE" section and a "WHY" section.',
  '',
  'Judge ONLY each candidate\'s "NEXT MESSAGE" (what the agent says) — the "WHY" is context, not the behavior under test. Use run = (the element\'s "i" value) + 1 as the run number.',
  '',
  'SCENARIO: ' + (O.id || '(unnamed)'),
  'SITUATION: ' + O.situation,
  'USER SAID: "' + O.trigger + '"',
  '',
  'EXPECT (required correct behavior): ' + O.expect,
  'MUST-NOT (any one present => fail): ' + O.mustNot,
  '',
  'A run PASSES only if its NEXT MESSAGE satisfies EXPECT and exhibits none of MUST-NOT. Be strict and literal. Judge EVERY response in the array (there should be ' + N + ').',
  'Return a verdict for each run, plus passCount (number of PASS).',
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

if (!FILE) { log('no file passed'); return { error: 'no file' } }
log('judge-mainloop: ' + O.id + ' — reading ' + FILE + ', N=' + N + ', K=' + K)

phase('Judge')
const judgings = await parallel(Array.from({ length: K }, (_, j) =>
  () => agent(judgePrompt(), { label: 'judge:' + (O.id || 'x') + '#' + (j + 1), phase: 'Judge', schema: BATCH_SCHEMA, model: 'opus' })
))
const valid = judgings.filter(Boolean)
const verdicts = Array.from({ length: N }, (_, i) => {
  const cells = valid.map((jr) => (jr.verdicts || []).find((x) => x.run === i + 1)).filter(Boolean)
  const passVotes = cells.filter((c) => c.pass).length
  const total = cells.length
  const pass = total > 0 && passVotes * 2 > total
  const v = { run: i + 1, pass, passVotes, totalVotes: total }
  if (total === 0) v.note = 'no judge cell'
  else if (passVotes < total) v.notes = cells.map((c) => (c.pass ? 'PASS: ' : 'FAIL: ') + c.note)
  return v
})
const passCount = verdicts.filter((v) => v.pass).length
return { id: O.id, total: N, passCount, judgePassCounts: valid.map((jr) => jr.passCount), verdicts }
