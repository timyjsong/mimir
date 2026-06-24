# Step 1 — premise test results (GREEN)

The premise — *plain-ifying the brain's dense hotspots does not regress behavior* — **holds**.
Slim+plain rewrite of 4 hotspots is behavior-neutral and precision-neutral. Awaiting user go for Step 2.

## Guards authored (the highest-risk artifact)
Three guards added to `scenarios.json`, derived from Principle 8 (legibility + economy),
phrased independently of the brain's wording (the red-team S2 fix — an oracle that paraphrases
the doc can't witness a narrowing of it):
- `footer-absent-reading-not-allclear` — L82: a missing reading must still render a flagged footer; absence ≠ all-clear.
- `footer-surface-trouble-not-calm` — L86: off-screen trouble surfaced loud, not buried among calm items.
- `voice-serves-not-bloat` — L17: character never pads/blurs the working detail.

Red-team of the guard set (`redteam-guardset.md`) caught two real issues, both fixed:
- the trouble guard injects a meter (footer always renders) → it protects L86, not L82 → added the dedicated L82 absent-reading guard;
- the voice guard had no meter → the always-on footer could read as "padding" → added a quiet-zone meter + scoped the mustNot to the answer body.

## Calibration (control: RED-on-weakened / GREEN-on-live)
One weakened candidate with three over-aggressive plain-ifies (L17 → "character everywhere";
L82 → "footer only when something to report"; L86 → trouble folded into a neutral catch-all).

| Guard | live | weakened | verdict |
|---|---|---|---|
| footer-absent-reading-not-allclear | 12/12 (100%) | 2/8 (25%) | **discriminates** |
| footer-surface-trouble-not-calm | 12/12 (100%) | 8/8 (100%) | over-determined |
| voice-serves-not-bloat | 15/15 (100%) | 8/8 (100%, 1-judge ×2)¹ | over-determined |

**Key finding:** footer-absent collapsing (100%→25%) on the *same* candidate is the built-in
positive control — it proves the candidate genuinely loaded. So the other two greens-on-weak are
real: **a near-inversion of L17's restraint and L86's "loud, never buried" did not change behavior.**
Those behaviors are over-determined by the Cadence section + the "never bury the lede" bright-line +
base competence — *not* primarily by the L17/L86 clauses. → L17-restraint and L86-emphasis are
candidates for **cutting** (slim win), to be eval-gated against the full bank in Step 2. Their guards
remain green-on-live regression sentinels but are not claimed as red-on-loss coverage.

¹ The voice-weak 3-judge re-run lost 2 judges to persistent 529s on the workflow-agent path (the
`claude -p` probes ran clean every time). 8/8 held across both 1-judge runs; not chased further.

## The rewrite (candidate, 4 hotspots, −26 words / −152 chars)
- **L17** — killed the "texture on the payload" metaphor + the triple-`never` stack; split the run-on. ("…character serves the answer — it never pads or blurs it.")
- **L82** — unwound the double-negation, kept the "never all-clear" semantics the guard protects. ("Because the footer always shows, a missing one is a fault … and never a sign that all is clear.")
- **L100** — de-personified "the meter reasons fine on its own" → "the gauge stands alone and needs no narration."
- **L121** — "a the-Hand job" → "a job for the Hand."

## Premise test (rewritten candidate vs live, K=3 majority, per-slot retry)
All six neutral; precision (style-earn-not-podium) held at 10/10.

| Scenario | live | candidate |
|---|---|---|
| footer-absent-reading-not-allclear | 12/12 | 10/10 |
| voice-serves-not-bloat | 15/15 | 9/10² |
| footer-trivial-gauge-only | 10/10 | 10/10 |
| format-air-with-voice | 10/10 | 10/10 |
| footer-packet-quiet-bigplan | 10/10 | 10/10 |
| style-earn-not-podium | 10/10 | 10/10 |

² The single non-pass is run 10, a probe subprocess error (not a behavior fail); 9/9 clean runs passed.

## State at PAUSE
- `scenarios.json`: +3 guards (56 total), **verified** → committable sub-seam (not yet committed).
- `output-styles/mimir-candidate.md`: 4-hotspot slim+plain rewrite, **NOT promoted** (gitignored scratch).
- `output-styles/mimir.md` (live): untouched at HEAD.
- Calibration/premise probe artifacts in `/tmp/sp1/` (ephemeral).
