#!/usr/bin/env node
// FAITHFUL main-loop probe: runs the brain as a REAL output-style on `claude -p`
// (the actual main agent loop + inherited global ~/.claude config, injected via
// system-reminder exactly as in a live interactive session) — NOT a subagent and
// NOT a role-played spec. Deployment-faithful instrument; carrier/role-play are proxies.
//
// Reads evals/scenarios.json (single source of truth for the behavior bank) for
// each scenario's situation/trigger and the outputStyle it should run under (mimir,
// or freya for designer scenarios). Each probe is a fresh `claude -p` process, so brain
// variants hot-reload with no CC restart. Globals load from ~/.claude regardless of cwd;
// we run from a neutral temp dir so no project CLAUDE.md interferes.
//
// Usage: node mainloop-probe.js <scenarioId> <N> [outFile] [brainStyleOverride]
//   brainStyleOverride: deploy-name of an output style to test IN PLACE OF the live
//   'mimir' brain (e.g. 'mimir-candidate' for staged self-iteration — see
//   ../SELF-ITERATION.md). Only the brain is swapped; non-brain scenarios (e.g. freya) keep theirs.
//   env CONC=<n> caps concurrent claude processes (default 6)
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

const SCENARIOS = JSON.parse(fs.readFileSync(path.join(__dirname, 'scenarios.json'), 'utf8'));
const byId = Object.fromEntries(SCENARIOS.map((s) => [s.id, s]));

function probePrompt(s) {
  return [
    'This is an offline decision probe of your OWN next action — you are operating as yourself; your system prompt is your operating identity. Produce your actual next turn. Do not run any tool, workflow, or skill; just output the message.',
    '',
    'Your current knowledge of disk/project state:',
    s.situation,
    '',
    'The user\'s latest message to you:',
    '"' + s.trigger + '"',
    '',
    'Output exactly:',
    '1. NEXT MESSAGE - what you say back to the user this turn, verbatim.',
    '2. WHY - brief reasoning.',
    '',
    'Be concise.',
  ].join('\n');
}

const id = process.argv[2];
const N = parseInt(process.argv[3] || '15', 10);
const outfile = process.argv[4] || `/tmp/rebaseline/${id}.json`;
const CONCURRENCY = parseInt(process.env.CONC || '6', 10);
const CWD = '/tmp/mimir-mainloop-probe';

const s = byId[id];
if (!s) { console.error('unknown scenario', id, '— have:', Object.keys(byId).join(',')); process.exit(1); }
// Optional brain-style override (argv[5]): test a candidate brain (e.g. 'mimir-candidate')
// in place of the live 'mimir'. Only the brain is swapped — non-mimir scenarios
// (e.g. freya designer scenarios) keep their own style. See ../SELF-ITERATION.md.
const styleOverride = process.argv[5];
const baseStyle = s.outputStyle || 'mimir';
const outputStyle = (styleOverride && baseStyle === 'mimir') ? styleOverride : baseStyle;
fs.mkdirSync(CWD, { recursive: true });
fs.mkdirSync(path.dirname(outfile), { recursive: true });
const prompt = probePrompt(s);

function runOne(i) {
  return new Promise((resolve) => {
    execFile('claude',
      ['-p', '--model', 'opus', '--settings', JSON.stringify({ outputStyle }), prompt],
      { cwd: CWD, maxBuffer: 10 * 1024 * 1024, timeout: 180000, env: { ...process.env, MIMIR_NO_METER: '1' } },
      (err, stdout, stderr) => {
        if (err) resolve({ i, error: String(err).slice(0, 300), stderr: String(stderr).slice(0, 300), text: stdout || '' });
        else resolve({ i, text: stdout });
      });
  });
}

(async () => {
  const results = [];
  let next = 0;
  async function worker() {
    while (next < N) { const i = next++; const r = await runOne(i); results.push(r); process.stderr.write(r.error ? 'x' : '.'); }
  }
  await Promise.all(Array.from({ length: Math.min(CONCURRENCY, N) }, worker));
  results.sort((a, b) => a.i - b.i);
  const ok = results.filter((r) => !r.error).length;
  fs.writeFileSync(outfile, JSON.stringify({ scenario: id, outputStyle, n: N, ok, responses: results }, null, 2));
  process.stderr.write(`\n${id} [${outputStyle}]: wrote ${outfile} (${ok}/${N} ok)\n`);
})();
