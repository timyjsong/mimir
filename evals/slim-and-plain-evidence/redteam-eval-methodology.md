# Red-team: the plain-language eval methodology

Adversarial review of the eval plan in `plain-language-plan.md`. I read the actual
substrate (`evals/mainloop-probe.js`, `judge-mainloop.js`, `judge-sweep.js`,
`judge-substance.js`, `scenarios.json`) before critiquing. The methodology is better than
most — control-calibration and a structural check are real instincts — but it has a
structural blind spot that lets a real plain-language regression ship green. Ranked by
severity.

## How the substrate actually works (so the critique is grounded, not assumed)

- The oracle is **hand-written prose** per scenario: `{situation, trigger, expect, mustNot}`
  in `scenarios.json` (53 scenarios). The judge is an LLM (K=3, opus, majority) reading
  `expect`/`mustNot` and voting pass/fail on the candidate's NEXT MESSAGE.
- The probe (`mainloop-probe.js`) runs the brain as a real output-style under `claude -p`
  with the brain swappable via `outputStyle` override. **It swaps only the brain.** The
  rule docs (`align`, `verify`, `honor`, `diag`), `USER.md`, and project `CLAUDE.md` load
  from the live `~/.claude` — they are **NOT swapped per-candidate**. This matters a lot
  (see S1).
- The judge reads the SAME oracle prose for control and live runs. The oracle is the only
  thing standing between a rewrite and a green light.

---

## S1 — CRITICAL: the probe can't isolate a rule-doc rewrite; phase-2 has no real candidate dance

**The exploit.** `mainloop-probe.js` only swaps `outputStyle` (the brain). The rule docs
(`align-before-executing.md`, `verify-before-asserting.md`, `honor-slash-commands.md`) and
`USER.md` are loaded from live `~/.claude` by every `claude -p` process regardless. So when
you "rewrite verify-before-asserting and eval it," there is **no candidate/live A/B** the
way there is for the brain. To test the rewrite you must **edit the live file in place**,
run the probe, and compare to a baseline captured before. That means:

1. The phase-2 "candidate → eval → promote" loop the plan implies **does not exist
   mechanically** for non-brain docs. The plan even half-says this for the pilot ("it does
   NOT de-risk the brain's candidate-dance") but doesn't notice the inverse: the *rules*
   have no candidate dance either. You are evaling the live file, i.e. you've already
   shipped it to every concurrent session and every other probe before the judge returns.
2. Worse: the probe runs the brain, and the brain's behavior depends on the rule docs as
   *ambient* context, not as the system prompt under test. A rule-doc regression shows up
   only if a brain-driven scenario happens to route through that rule. Many won't.

**Why both controls still pass.** Your negative control is "sabotage the doc → guard goes
RED." If you sabotage `verify-before-asserting.md` live and the verify-scenarios go red,
great — but you've proven the *scenario* is sensitive to *gross* sabotage of that file,
not that your probe harness isolates the rewrite. The positive control (live doc → green)
is trivially true because the live doc *is* what's loaded. Both controls pass; neither
tells you the rewrite you're about to ship is neutral, because the thing under test was
never a swappable artifact.

**Fix.** Before phase 2, extend `mainloop-probe.js` to inject candidate rule-doc text the
same deployment-faithful way the meter spec is injected (it already appends
`context-packet-spec.md` via a system-reminder for footer scenarios — same mechanism).
Pass candidate rule bodies as additional system-reminder context and confirm they override
the live ones in precedence. If that can't be made faithful, the honest statement is "phase
2 is tested by live-edit + before/after baseline, accepting that the candidate is briefly
live" — and the commit seam must be *immediately* after a green, not batched.

---

## S2 — CRITICAL (the deepest hole): the oracle prose quietly re-derives from the doc being rewritten

**Name the doc/behavior:** `output-styles/mimir.md` L82 (the footer-absence rule) and the
`footer-*` scenarios; and `verify-before-asserting.md` + `verify-no-inference-chaining`.

The oracle `expect`/`mustNot` strings were written by the same author, in the same register,
often paraphrasing the very doc under rewrite. Concretely:

- `verify-no-inference-chaining` oracle EXPECT says: *"The verified neighbor sharpens what
  to check; it does not stand in for checking B."* That is a near-verbatim lift of the rule
  doc's own phrasing (*"A fact you just verified does NOT license an adjacent claim"*). The
  oracle and the doc are **not independent** — they're two copies of the same sentence.
- `footer-trivial-gauge-only` oracle EXPECT enumerates *"the ᛗᛁᛗᛁᚱ wordmark + the one-line
  context gauge only (the liveness floor)"* — lifted from mimir.md L82's "liveness floor"
  language.

**The exploit.** A plain-language rewrite that subtly narrows a rule will still pass,
because the judge isn't checking the candidate against the *old behavior* — it's checking
against `expect`, which is prose that itself can be (and in places is) a paraphrase of the
doc. If the rewrite drops a clause, and the oracle never encoded that clause as a hard
`mustNot`, the judge has nothing to fail on. The control-calibration doesn't catch this:
your negative control sabotages the *doc*, not the *oracle*. You never test whether the
oracle is strong enough to detect a subtle narrowing — you only test whether the scenario
fires on a gross break.

**Concrete green-shipping regression.** Take mimir.md L82: *"the footer's absence now means
one thing only — the reading didn't arrive (a fault) — never 'all clear.'"* The scan flags
this exact line as a double-negation hotspot to plain-ify. Suppose the rewrite becomes:
*"Always show the footer. A missing footer means the reading failed."* Reads plainer. But
it **drops the "never 'all clear'" semantics** — the original forbids *interpreting* absence
as all-clear; the rewrite only says absence = failure, losing the instruction about how the
agent must *not reason* about a missing footer. Is there a scenario whose `mustNot`
encodes "must not treat a missing footer as all-clear"? No — `footer-trivial-gauge-only`
tests that the footer is *present and minimal*, not the absence-interpretation rule. The
regression ships green because **no oracle encodes the dropped clause.**

**Fix.** (a) The structural-completeness check (S3) must produce, for every dropped/merged
clause, a *named scenario whose `mustNot` would go red if that clause's behavior regressed* —
and if none exists, that clause is **uncovered** and the rewrite of it is unguarded, full
stop. (b) Re-author oracles for the rewrite targets from PRINCIPLES.md / first principles,
NOT from the doc, so oracle and doc are independent witnesses. An oracle paraphrased from
the doc cannot witness the doc.

---

## S3 — HIGH: structural-completeness check is theater as specified

The plan: "every load-bearing clause in the old doc maps to one in the new — a mechanical
second oracle." As written this is a **mapping existence check**, and mapping existence is
not behavior preservation. Three failure modes:

1. **Who decides "load-bearing"?** If the rewriter (human or agent) classifies clauses, the
   clause it's about to weaken is exactly the one it'll rank non-load-bearing or fold into a
   neighbor. Self-grading the completeness of your own edit is the same conflict the studio
   doc bans (no self-ratify). The check must be run by an agent that hasn't seen the rewrite
   rationale, against the OLD doc only, producing the clause list *before* the rewrite.
2. **"Maps to one" hides meaning-drift.** Clause A ("verify each link against a source about
   that exact case; a verified fact does not license an adjacent claim") can "map to" a new
   clause ("check each claim separately") — 1:1 mapping satisfied, but the new clause lost
   *"a source about that exact case"* and *"does not license an adjacent claim,"* which is
   the whole anti-transitive-trust point (`verify-no-inference-chaining`). Mapping is
   present; meaning is gone. The check passes; the behavior regresses.
3. **No verb of consequence.** A structural check that emits "mapped / not mapped" with no
   downstream gate is decorative. It must hard-block: an unmapped or weakened clause **fails
   the campaign** until either re-added or explicitly waived against a principle.

**Fix.** Make it a behavioral diff, not a textual one: for each old clause, the check must
name (a) the behavior it produces and (b) the scenario that would catch its loss (ties into
S2's fix). "Maps to a sentence" is not acceptance; "maps to a guarded behavior" is.

---

## S4 — HIGH: register-improvement is a genuine NEW bad oracle, and it can veto a correct neutral rewrite

The plan asks: does scoring "did it get plainer?" create a new bad oracle? **Yes.**

1. **"Plainer" is judge-gameable in the regression-friendly direction.** The rubric proxies
   plainness with mechanical tests (sentence ≤25 words, one idea per sentence, coined terms
   unpacked, no anti-instruction stacks, net chars not growing). Every one of those is
   satisfiable by **cutting a qualifying clause.** "Verify each link against a source about
   that exact case" → "Verify each link." Shorter, fewer ideas, no coined term — **scores
   better on register** while losing the exact-case constraint. So the register oracle and
   the neutrality oracle don't just disagree; the register oracle actively *rewards* the
   edit that the neutrality oracle should (but per S2 may not) punish. The two oracles point
   in opposite directions on precisely the dangerous edits.

2. **Contradictory verdicts — which wins?** The plan never says. If register is a gate
   ("must IMPROVE while neutrality holds"), then a rewrite that is *correctly* neutral but
   only modestly plainer FAILS the campaign and gets reworked — and the rework pressure is
   toward cutting words, i.e. toward the S2 regression. The gate's incentive gradient runs
   *away* from safety. **Neutrality must be a hard gate; register must be at most a
   soft/advisory score**, never a gate that can force a second, more-aggressive cut. State
   the precedence explicitly: neutrality RED kills the rewrite regardless of register;
   register-not-improved is a note, not a block.

3. **Self-judging register with the same rubric that wrote the rewrite.** If the rewrite was
   produced to satisfy the 8 rubric tests and then scored by a judge applying the same 8
   tests, the score is circular — it measures "did you follow the rubric," not "did a reader
   find it plainer." If register matters, it needs an *independent* readability signal
   (different judge, different prompt, ideally "which of these two reads more plainly" blind
   A/B), not a re-run of the authoring checklist.

**Fix.** Demote register to advisory. Keep neutrality as the only gate. If you want a
register gate, make it blind-pairwise ("A vs B, which is plainer, are they same meaning?")
and require the *same* judge to also affirm same-meaning — so the plainness vote can't be
won by a meaning-losing cut.

---

## S5 — HIGH: PRINCIPLES-freeze is a policy, not a mechanism — nothing enforces it

The plan "freezes PRINCIPLES.md semantics" and traces expected behaviors to the frozen
meaning. But PRINCIPLES.md is also a phase-3 rewrite target. The freeze is enforced by…
intention. Concretely:

- There is no test that the post-rewrite PRINCIPLES.md is **semantically identical** to the
  frozen one. The campaign's own tool for "did meaning change?" is the neutrality eval — but
  the neutrality eval's oracles *trace to PRINCIPLES* (plan crack #3). So if a "wording-only"
  plain-ify of PRINCIPLES silently shifts meaning, the oracles derived from it shift too, and
  the eval happily certifies the brain against the *drifted* principle. **The measuring stick
  is inside the thing being measured.** A bent ruler that bends its own gradations reads
  straight.
- "Wording-only" is undecidable for the cases that matter. The scan flags PRINCIPLES #15
  corollary ("poka-yoke"; "interface-ergonomics failures are systemic failures"). Plain-ify
  "shape tools so the wrong action is structurally hard" and you may narrow "structurally
  hard" (prevent) to "discouraged" (warn) without noticing — and there's no scenario that
  pins poka-yoke-strength behavior to catch it.

**Fix.** Freeze PRINCIPLES.md by **content hash** for the campaign and forbid editing it at
all until phases 1–2 are promoted (the plan already calls phase 3 deferrable — defer
PRINCIPLES *entirely* out of this campaign). When you do rewrite it, the acceptance test is
a semantic-equivalence judge over old-vs-new PRINCIPLES *with the eval frozen on the OLD
text*, never the new. The oracle source and the rewrite target must never be the same
revision.

---

## S6 — MEDIUM: the applied USER.md header is un-evaled AND uncoverable by the current bank

Plan crack #4 admits the USER.md merge/regrade/contradiction header was applied live without
eval. I checked the bank: **no scenario exercises the write-trigger mechanics.**
`usermodel-write-global` only tests "route a durable cross-project pref to the global file";
`usermodel-no-overclaim` tests "don't over-generalize a one-off." Neither tests merge (new
fact vs existing), regrade (confidence up/down on contradiction), or the contradiction rule.
The two scenarios whose oracle prose mentions "regrade/merge" (`designer-no-self-ratify`,
`footer-packet-surface`) are unrelated.

So the header is not just un-evaled — there's no guard to calibrate against. And the plan's
own crack #5 concedes the silence-decay half of the grade has **no firing mechanism**
(no clock), meaning a chunk of the header is dead instruction that no eval can fire on
because the behavior can't occur. You'd be control-calibrating a guard for a behavior the
system can't exhibit.

**Fix.** Either (a) roll back the header until a focus scenario exists that drives a
contradiction through orient→USER.md re-read→regrade and pins the merge/contradiction
outcome in `mustNot`; or (b) accept it as explicitly un-guarded and log it as a known
uncovered surface — don't let the campaign's "control-calibrated" framing imply it's
covered. Drop the silence-decay clause (crack #5 is right; it's aspirational and unfireable).

---

## S7 — MEDIUM: K=3 majority + same-author oracle gives correlated, not independent, votes

`judge-mainloop.js` runs K=3 opus judges and takes majority. This guards against *judge
variance*, not *oracle error*. All three judges read the same `expect`/`mustNot`. If the
oracle under-specifies the dropped clause (S2), all three judges agree to PASS — 3/3 green,
maximal confidence, wrong. The plan treats "history-proven guards trusted as-is" (cost-skip
17%, forge over-fire ~50%) as settled, but those calibrations were taken against the OLD
doc register; a plain rewrite changes the candidate's surface form, which can change how the
judge reads `mustNot` (e.g. a plainer answer that drops the hedge may read as more confident
and trip a `mustNot` it didn't before, or vice-versa). Trusting old pass-rates as the
baseline assumes judge behavior is invariant to register — the very thing you're changing.

**Fix.** Re-baseline the trusted guards against the LIVE (pre-rewrite) doc immediately before
the campaign, so the comparison is rewrite-vs-current-judge, not rewrite-vs-historical-number.
Same N, same K, same session.

---

## S8 — LOW: probe prompt asks for an offline single turn — multi-turn regressions invisible

`probePrompt` elicits ONE next message ("Produce your actual next turn… Do not run any
tool"). Rewrites to continuity/orientation language (the Continuity trim folded into phase 1)
produce regressions that only manifest across turns (re-reading USER.md on orient, carrying a
prior across a gap). A single-turn probe can't see them. The `multiturn-probe.js` exists but
the plan's eval loop names only the single-turn instrument.

**Fix.** For the Continuity/orientation rewrites specifically, route through the multiturn
probe, not the single-turn one. Name it in the plan.

---

## Bottom line

The single most likely way this ships a regression green: **S2 + S3 acting together** — a
plain rewrite drops a qualifying sub-clause (the "exact-case"/"never all-clear"/"does not
license an adjacent claim" kind), the structural check sees a 1:1 sentence mapping and waves
it through, and the neutrality oracle — paraphrased from the very doc being rewritten and
never encoding that sub-clause as a hard `mustNot` — votes 3/3 PASS. Both controls passed
(they only ever tested gross sabotage), register-improvement *rewarded* the cut, and the
campaign certifies a quietly-narrowed `verify-before-asserting` or footer-absence rule as
behavior-neutral. The named victims: `verify-no-inference-chaining` (anti-transitive-trust
clause) and mimir.md L82 (footer-absence-is-not-all-clear).

The fix that closes the most surface at once: **oracles for rewrite targets must be authored
independently of the doc (from PRINCIPLES/first principles), and the structural check must
map each old clause to a scenario that would go RED on its loss — a clause with no such
scenario is declared uncovered, not "mapped."** Everything else is secondary to breaking the
oracle's dependence on the artifact it's supposed to witness.
