export const meta = {
  name: 'judge-substance',
  description: 'SUBSTANCE-fidelity judge: for each scenario with a `substance` checklist, check whether every load-bearing CONTENT element is present and undistorted in each candidate output — ignoring style/formatting entirely. This is the correctness GATE (Tim non-negotiable), separate from judge-sweep.js (which scores style/behavior). args {scenariosFile, dir, ids:[...], n, k}.',
  phases: [{ title: 'Substance' }],
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
      properties: {
        run: { type: 'integer' },
        pass: { type: 'boolean' },              // true only if EVERY substance element is present & undistorted
        missing: { type: 'array', items: { type: 'string' } },   // elements omitted
        distorted: { type: 'array', items: { type: 'string' } }, // elements present but wrong/misrepresented
        note: { type: 'string' },
      },
      required: ['run', 'pass', 'missing', 'distorted', 'note'] } },
    passCount: { type: 'integer' },
  },
  required: ['verdicts', 'passCount'],
}

const judgePrompt = (id) => [
  'You are a strict SUBSTANCE-FIDELITY judge for an AI agent. You check CONTENT only — never style, tone, layout, or formatting.',
  '',
  'STEP 1 — load the substance checklist: Read the JSON array at ' + SF + ', find the object whose "id" === "' + id + '". Use its "substance" array: the load-bearing CONTENT elements the answer MUST carry to be correct and complete. Also read "situation" and "trigger" for context.',
  'STEP 2 — load candidates: Read ' + DIR + '/' + id + '.json; its "responses" array holds {"i": <0-based>, "text": "..."} (or {"i":..,"error":..} => treat as FAIL, missing=["no response"]). Judge the "NEXT MESSAGE" portion; "WHY" is context.',
  '',
  'For EACH response, check EVERY substance element: is it PRESENT and ACCURATELY represented? An element OMITTED goes in "missing"; an element present but wrong, contradicted, or distorted goes in "distorted". Where the checklist names a calculation, verify the arithmetic — a wrong number is "distorted".',
  'A run PASSES only if missing AND distorted are both empty. IGNORE all matters of style, brevity, airiness, headers, tone, register — a terse answer that carries every element PASSES; a beautifully written one that drops an element FAILS. Be strict and literal about content; do not reward presentation.',
  'Judge EVERY response (there should be ' + N + '). Use run = (the element\'s "i") + 1. Return a verdict per run plus passCount (number of PASS).',
].join('\n')

if (!SF || !DIR || !IDS.length) { log('missing args (need scenariosFile, dir, ids)'); return { error: 'args' } }
log('judge-substance: ' + IDS.length + ' scenarios, N=' + N + ', K=' + K + ' — substance checklists from ' + SF)

phase('Substance')
const results = await parallel(IDS.map((id) => () =>
  parallel(Array.from({ length: K }, (_, j) =>
    () => agent(judgePrompt(id), { label: 'subst:' + id + '#' + (j + 1), phase: 'Substance', schema: BATCH_SCHEMA, model: 'opus' })
  )).then((js) => {
    const valid = js.filter(Boolean)
    const verdicts = Array.from({ length: N }, (_, i) => {
      const cells = valid.map((jr) => (jr.verdicts || []).find((x) => x.run === i + 1)).filter(Boolean)
      const pv = cells.filter((c) => c.pass).length
      const tot = cells.length
      const pass = tot > 0 && pv * 2 > tot
      const v = { run: i + 1, pass, passVotes: pv, totalVotes: tot }
      // surface the union of flagged omissions/distortions when judges dock a run
      if (tot && pv < tot) {
        const miss = [...new Set(cells.flatMap((c) => c.missing || []))]
        const dist = [...new Set(cells.flatMap((c) => c.distorted || []))]
        if (miss.length) v.missing = miss
        if (dist.length) v.distorted = dist
      }
      return v
    })
    return { id, total: N, passCount: verdicts.filter((v) => v.pass).length, judgePassCounts: valid.map((jr) => jr.passCount), verdicts }
  })
))
return { summary: results.map((r) => r.id + ': ' + r.passCount + '/' + r.total + ' substance-clean'), results }
