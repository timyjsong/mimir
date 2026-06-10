export const meta = {
  name: 'judge-sweep',
  description: 'Batch STRICT K=3-majority judge over a full main-loop re-baseline sweep. Each judge agent reads scenarios.json (oracle by id) + the per-scenario response file in <dir>. args {scenariosFile, dir, ids:[...], n, k}. Mirrors judge-mainloop scoring so numbers are comparable.',
  phases: [{ title: 'Judge' }],
}

let A = {}
if (args && typeof args === 'object') A = args
else if (typeof args === 'string') { try { const p = JSON.parse(args); A = (p && typeof p === 'object') ? p : {} } catch (e) { A = {} } }
const SF = A.scenariosFile
const DIR = A.dir
const IDS = Array.isArray(A.ids) ? A.ids : []
const N = Number.isInteger(A.n) && A.n > 0 ? A.n : 15
const K = Number.isInteger(A.k) && A.k > 0 ? A.k : 3

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

const judgePrompt = (id) => [
  'You are a STRICT evaluation judge for an AI agent persona (default the "mimir" brain; designer scenarios are the "freya" persona). You will score ONE scenario.',
  '',
  'STEP 1 — load the oracle: Read the JSON array file at ' + SF + ' and find the object whose "id" === "' + id + '". Use its fields: situation, trigger, expect (the REQUIRED correct behavior), mustNot (any one present => FAIL).',
  'STEP 2 — load candidates: Read the file ' + DIR + '/' + id + '.json; it has a "responses" array of {"i": <0-based>, "text": "<candidate output>"} (or {"i":..., "error":...} for a failed run — treat as FAIL, note "no response"). Each text has a "NEXT MESSAGE" section and a "WHY" section.',
  '',
  'Judge ONLY each candidate\'s "NEXT MESSAGE" (what the agent says) — the "WHY" is context, not the behavior under test. A run PASSES only if its NEXT MESSAGE satisfies EXPECT and exhibits none of MUST-NOT. Be strict and literal. Judge EVERY response (there should be ' + N + '). Use run = (the element\'s "i") + 1.',
  'Return a verdict for each run, plus passCount (number of PASS).',
].join('\n')

if (!SF || !DIR || !IDS.length) { log('missing args (need scenariosFile, dir, ids)'); return { error: 'args' } }
log('judge-sweep: ' + IDS.length + ' scenarios, N=' + N + ', K=' + K + ' — reading oracles from ' + SF)

phase('Judge')
const results = await parallel(IDS.map((id) => () =>
  parallel(Array.from({ length: K }, (_, j) =>
    () => agent(judgePrompt(id), { label: 'judge:' + id + '#' + (j + 1), phase: 'Judge', schema: BATCH_SCHEMA, model: 'opus' })
  )).then((js) => {
    const valid = js.filter(Boolean)
    const verdicts = Array.from({ length: N }, (_, i) => {
      const cells = valid.map((jr) => (jr.verdicts || []).find((x) => x.run === i + 1)).filter(Boolean)
      const pv = cells.filter((c) => c.pass).length
      const tot = cells.length
      const pass = tot > 0 && pv * 2 > tot
      const v = { run: i + 1, pass, passVotes: pv, totalVotes: tot }
      if (tot && pv < tot) v.notes = cells.map((c) => (c.pass ? 'PASS: ' : 'FAIL: ') + c.note)
      return v
    })
    return { id, total: N, passCount: verdicts.filter((v) => v.pass).length, judgePassCounts: valid.map((jr) => jr.passCount), verdicts }
  })
))
return { summary: results.map((r) => r.id + ': ' + r.passCount + '/' + r.total), results }
