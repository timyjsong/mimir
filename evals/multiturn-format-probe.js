#!/usr/bin/env node
// FAITHFUL multi-turn FORMAT probe: does the "write for air" layout hold across a
// working session, or decay back into dense prose by turn 3? Same instrument as
// multiturn-probe.js (claude -p + output-style, session resume for turns 2-3), but the
// turns are ordinary substantive work — no pushback. Judge each turn file against the
// air oracle (short stacked paragraphs, blank-line separated, no welded clause-chains);
// the question is whether turn 3 still passes.
//
// Usage: node multiturn-format-probe.js <N> <outputStyleName> <outPrefix>
//   env CONC=<n> caps concurrent conversations (default 5)
// Writes <outPrefix>-turn{1,2,3}.json (each {responses:[{i,text}]} — judge-mainloop format)
// + <outPrefix>-conversations.json (full record).
const { execFile } = require('child_process');
const fs = require('fs');

const SITUATION = "You are Mimir, the user's default AI agent for this Claude Code session. Ordinary repo work in a Node API service the user knows well. The team deployed yesterday; p95 latency has roughly doubled since. Known facts: the deploy included an ORM version bump and a new per-request feature-flag lookup; CPU is flat; db connection count is up ~3x.";
const TURNS = [
  'This is an offline decision probe — you are operating as yourself; produce your actual next turn, do not run any tool, just output your message.\n\nYour current knowledge of disk/project state: ' + SITUATION + '\n\nThe user\'s latest message: "ok walk me through your read — why did p95 double after yesterday\'s deploy?"',
  '(still an offline probe — just give your next message, no tools.) "interesting. what would you check first, concretely, and what would each result tell us?"',
  '(still an offline probe — just give your next message, no tools.) "we confirmed it — the pool is getting exhausted by the flag lookups. walk me through the fix approach and what could bite us."',
];

const N = parseInt(process.argv[2] || '10', 10);
const outputStyle = process.argv[3] || 'mimir';
const prefix = process.argv[4] || `/tmp/ml-mtfmt-${outputStyle}`;
const CONCURRENCY = parseInt(process.env.CONC || '5', 10);
const CWD = '/tmp/mimir-mainloop-probe';
fs.mkdirSync(CWD, { recursive: true });

function claude(extraArgs, prompt) {
  return new Promise((resolve) => {
    execFile('claude', [...extraArgs, '--model', 'opus', '--output-format', 'json', prompt],
      { cwd: CWD, maxBuffer: 10 * 1024 * 1024, timeout: 180000 },
      (err, stdout) => {
        if (err) return resolve({ error: String(err).slice(0, 200) });
        try { const j = JSON.parse(stdout); resolve({ text: j.result, sid: j.session_id }); }
        catch (e) { resolve({ error: 'parse: ' + String(e).slice(0, 120), raw: String(stdout).slice(0, 200) }); }
      });
  });
}

async function runConversation(convId) {
  const sid = require('crypto').randomUUID();
  const turns = [];
  let r = await claude(['-p', '--session-id', sid, '--settings', JSON.stringify({ outputStyle })], TURNS[0]);
  turns.push(r);
  for (let t = 1; t < TURNS.length; t++) {
    if (turns[t - 1].error) { turns.push({ error: 'skipped: prior turn failed' }); continue; }
    r = await claude(['-p', '--resume', sid, '--settings', JSON.stringify({ outputStyle })], TURNS[t]);
    turns.push(r);
  }
  process.stderr.write(turns.some((t) => t.error) ? 'x' : '.');
  return { convId, turns };
}

(async () => {
  const conversations = [];
  let next = 0;
  async function worker() {
    while (next < N) { const i = next++; conversations.push(await runConversation(i)); }
  }
  await Promise.all(Array.from({ length: Math.min(CONCURRENCY, N) }, worker));
  conversations.sort((a, b) => a.convId - b.convId);
  for (let t = 0; t < TURNS.length; t++) {
    const responses = conversations.map((c) => (c.turns[t].error
      ? { i: c.convId, error: c.turns[t].error }
      : { i: c.convId, text: c.turns[t].text }));
    fs.writeFileSync(`${prefix}-turn${t + 1}.json`, JSON.stringify({ scenario: `multiturn-format-turn${t + 1}`, outputStyle, n: N, responses }, null, 2));
  }
  fs.writeFileSync(`${prefix}-conversations.json`, JSON.stringify({ outputStyle, n: N, conversations }, null, 2));
  process.stderr.write(`\nwrote ${prefix}-turn{1,2,3}.json (+conversations)\n`);
})();
