# Brain Slim-and-Plain Campaign — Converged Plan

> Durable plan for making the Mimir brain BOTH slimmer and plainer, in ONE pass with ONE eval —
> not two campaigns over the same text. Written for a fresh/autonomous session to execute.
> Reconcile against disk before trusting (memory drifts). Evidence that shaped it:
> `evals/slim-and-plain-evidence/` (the doc scan + three red-team findings).

## Goal — two moves, one pass
The brain (`output-styles/mimir.md`) gets rewritten **once** to be both:
- **Slimmer** — cut redundancy, relocate trigger-fired content off the every-turn path, drop pure
  rationale. This is the minimal-instruction principle ("highest quality with the LEAST
  instruction; bloat degrades") — already ratified, **no premise to prove**, but guarded so a cut
  never drops a load-bearing rule.
- **Plainer** — reword what remains in natural, precise language. **Plain AND precise:** a sentence
  that reads two ways fails even if it's plain; plain is never a license to add words. This half
  rests on an **unproven theory** (doc register primes Mimir's output register), so it gets
  premise-tested first.

Both happen in one rewrite, section by section (cut, then reword) → ONE candidate, ONE eval
baseline. Two separate passes would mean trimming twice and re-baselining twice — the exact waste
the campaign avoids everywhere else.

## The plain half is unproven — so we test it first
"Plainer docs → plainer Mimir" is an assumption, not a verified fact, and could even backfire
(some density packs hard-won rules; "simplifying" could drop one or make Mimir sloppier). We test
it on the brain before committing. If it fails where the effect is strongest, it isn't worth
chasing elsewhere. Test-before-believe is the system's own first rule (`verify-before-asserting`).
(Slim needs no such test — it's already ratified; it rides under the neutrality + completeness guards.)

## Scope & priority (non-brain docs are NOT off-limits)
- **The brain is the priority and the core.** Loads every turn, ~90% of Mimir's register, and the
  only doc the eval sandbox can test the clean way (candidate → eval → promote; see `SELF-ITERATION.md`).
- **Non-brain Mimir docs** (USER.md, playbooks, studio, the-hand) — **in scope as a lighter
  follow-on, not banned.** No sandbox candidate, so **validate-after**: edit, run the relevant
  scenarios live, revert if behavior slips (what `SELF-ITERATION.md` prescribes for non-brain
  surfaces). Pick by whether they're actually dense enough to be worth it.
- **Global rules (`~/.claude/rules/`)** — touchable but need care: they also govern **subagents,
  which run WITHOUT the brain**, while the main-loop eval always runs WITH it on top — so the bank
  is blind to a subagent regression. Touch only with a subagent-side check or an eyes-open accept.
- **PRINCIPLES.md is permanently out of scope** — it's the eval's answer key; don't rewrite the
  measuring stick.
- Nothing is permanently off-limits. The brain is where the payoff is and where we start.

## Eval discipline (protects BOTH the cut and the reword)
- **Neutrality is the only hard gate** — does Mimir still behave correctly after the rewrite?
  It covers BOTH its disciplines holding AND its precision/calibration not degrading (Step 1's (a)
  and (c) are the two faces of this one gate, not two separate gates). Pass/fail; guards the reword
  and the cut equally.
- **The structural-completeness check is what makes aggressive slimming safe:** for every rule in
  the old version there must be a scenario that goes RED if that rule goes missing — so a cut that
  drops a real constraint is caught. A rule with no such scenario is "uncovered," not "covered."
- **Plainness and slimness are advisory, never gates** — the user's eyeball for plain, a line/token
  count for slim. A "plainer/slimmer" score is satisfied by deleting clauses, which is the exact
  dangerous edit neutrality + completeness must catch, so neither drives promote.
- Guards authored from PRINCIPLES, independent of the doc. Control-calibrate each (feed it a
  plausibly-plain-but-weakened doc → must go RED; live doc → GREEN; discard a guard that fails
  either). Re-baseline against the live brain immediately before the pass. Multi-turn probe for the
  Continuity rewrite (single-turn misses orientation regressions).

## Don't give up easily (explicit user directive)
If a test underperforms, the FIRST hypothesis is "the rewrite/instruction is poorly worded," not
"the approach is wrong." Reword and re-test a couple of times before concluding. Applies to the
USER.md header (a weak result may just mean the header is badly instructed) and to the premise test
(a weak neutrality result may be a bad rewrite, not a false theory).

## USER.md header — keep-and-test (decided)
The improved header (merge / regrade / contradiction) STAYS. Its write-behavior is covered by no
scenario yet, so ADD one: exercise a write-to-user-model and check the agent **merges** (not
appends), **regrades** on contradiction, **routes** a project-specific fact to counsel (not the
user-model), and does **not** promote a one-off. Validate-after (USER.md isn't the brain).
Silence-decay clause already cut. Weak result → reword the header first. (A test write to USER.md
trips the live `profile-budget-hook` in `settings.json` — expected; it's a size-cap, not a blocker.)

## The plan, in order

**This run is milestone-gated — NOT fully autonomous 0→100.** You decide the mechanical, verifiable
calls (does a guard discriminate, did a probe pass, is a citation right); the **user** decides the
go/no-go milestones. At each **⏸ PAUSE** below, STOP, report what you found, and wait for the user's
go before proceeding. Never cross a PAUSE on your own.

- **Step 0 — done:** silence-decay clause cut from the USER.md header.
- **Step 1 — premise test (go/no-go for the whole campaign).**
  **First, author the guards** (per *Eval discipline* above) — they do NOT exist yet, this is Step 1's
  first deliverable, before any rewrite: write the neutrality scenarios from PRINCIPLES independent of
  the brain text, control-calibrate each (red-on-broken / green-on-live; discard any that fail a
  control), **red-team the guard set in isolation** (it's the highest-risk artifact — a bad guard
  ships a regression green), and re-baseline the live brain. THEN, on `mimir-candidate` (via the `SELF-ITERATION.md`
  loop), rewrite 2-3 dense brain hotspots **both slimmer and plainer** (scan's top brain picks: L82
  footer-absence double-negation, L17 voice/triple-never stack, L100/121 compressions). Probe live
  vs candidate and judge:
  - (a) **disciplines neutral** — the control-calibrated guards hold;
  - (c) **precision/calibration NOT degraded** — it doesn't get sloppier or overconfident;
  - (a)+(c) ARE the one hard gate (both are behavioral correctness) — the autonomous agent decides these.
  - (b) **plainer + shorter** is advisory, NOT a gate: the agent computes the line/token delta
    (objective) and **surfaces the plainness samples for the user's eyeball** — it never self-certifies
    "reads plainer," and never blocks the run waiting on the eyeball.
  GREEN on (a)+(c) → premise holds. RED on (a) or (c) → iterate the rewrites first (don't-give-up);
  if still red, the campaign is moot and not doing it was the win.
  **⏸ PAUSE — user gate.** Whether green or red, STOP here: report the neutrality verdict, the size
  delta, and the plainness samples, and wait for the user's go before starting Step 2. The premise
  verdict decides whether the whole campaign proceeds — that's the user's call, not yours.
- **Step 2 — if green, the brain pass (slim + plain together, full rigor):**
  1. Relocate the trigger-fired Capabilities / forge / studio / brownfield descriptions (L111-125)
     off the every-turn path into their on-demand docs, leaving one-line routing pointers. (The
     biggest single slim win — and you don't polish text that's about to move.)
  2. Fold in the staged step-3 Continuity trim (cut the verify-overlap with *The read* §58 and the
     parked-bet-overlap with *Status* §86; keep the dispositions). (Slim.)
  3. For every remaining section: cut redundancy first, then reword plainly per the rubric. (Slim + plain.)
  4. Independent guards, re-baseline, multi-turn probe, red-team the candidate before promote.
  If a candidate regresses, bisect cut-only vs reword to localize the cause, then fix.
  **⏸ PAUSE — user gate (the hard one).** NEVER promote to the live brain on your own. Present the
  candidate diff, the red-team result, and the eval deltas, and wait for the user's explicit
  approval. Promote changes the global default brain for every next session until reverted.
- **Step 3 — measure, then stop.** Report the slim delta (lines/tokens), the register read, and the
  neutrality result. Non-brain docs and global rules are an opt-in follow-on (validate-after /
  subagent-care), decided separately — not auto-swept.

## The rubric (the rewrite contract)
The 8 scan tests (no sentence over ~25 words · one idea per sentence · every coined term unpacked on
first use or cut · plain verb over nominalization · no "never X, never Y, never Z" stacks · no
metaphor where a literal phrase is shorter · references resolved inline · net size must not grow to
add words) **+ undeniable-intent** (exactly one reading, clean grammar) **+ the tiebreak:** meaning
is sacred, wording is negotiable, length is a strong preference — not a hard cap. For a slim+plain
pass: **prefer reduction** where content is redundant or relocatable; the floor on cutting is the
completeness check (every rule keeps a red-on-loss guard), not a character target.

## Red-team cadence
Isolated red-team at each phase that introduces new risk: **the guard set when it's authored
(Step 1)** and **every brain-candidate diff before promote.** One round per converged candidate; a
second only if the first found something material. The user is token-ample and wants frequent
independent review — when in doubt, spawn the isolated check.

## State at handoff
- Brain `output-styles/mimir.md`: untouched, 125 lines, at committed HEAD. The Continuity trim is
  staged-in-plan only, applied in Step 2.
- `~/.claude/mimir/USER.md`: header is the keep-and-test version, silence-decay cut. NOT git-tracked
  (lives outside the repo) — its state is not captured by repo git.
- Scan + red-team evidence: `evals/slim-and-plain-evidence/`.
