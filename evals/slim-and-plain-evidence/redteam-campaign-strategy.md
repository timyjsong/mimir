# Red-team — Plain-Language Campaign strategy/scope/risk

Isolated adversarial review. Verified against the live files, not the plan's self-description.
Severity-ranked. Each item ties to a file/phase and ends with a recommended action.

---

## S1 (highest) — The premise is asserted, never tested, and may be net-negative

The whole campaign rests on one claim: **"the register of the docs primes the agent's own
output register."** The plan treats this as settled (goal line, scan line 3). It is not
verified anywhere. No eval, no A/B, no citation. The entire work-package is justified by an
untested causal hypothesis — which is exactly the failure `verify-before-asserting.md` and
USER.md `[high] Verification is non-negotiable` exist to stop. The campaign violates the
system's own first rule about itself.

Steelman that it's net-negative (the plan never does this honestly):
- **Density is often load-bearing compression, not register leakage.** USER.md L18-19,
  `verify-before-asserting` L3-5, `align` L3 are dense *because each clause is a distinct
  hard-won constraint* (USER.md's own `Lean instructions` rule: "cutting a load-bearing rule
  reintroduces the failure it prevents"). The 25-word/one-idea-per-sentence rubric (scan
  rubric #1, #2) will pressure a rewriter to drop or soften clauses to hit the limit. The
  plan's own crack #2 admits this tension but resolves it with a *judgment call* ("meaning is
  sacred, length negotiable") — i.e. it removes the mechanical guard precisely where the risk
  is highest and replaces it with reviewer discretion under a word-count incentive.
- **"Plainer docs → plainer output" is plausibly backwards for precision.** The behaviors the
  team most wants (spine, verify-each-link, gate-on-cost) are encoded in the *exact dense
  phrasings* that survived prior eval campaigns (the commit log shows these rules were tuned
  through evals: `b7e86a1`, `e2bfa7a`, `1f5e24e`). A register shift toward "plain" risks
  shifting the agent toward *casual confidence* — the opposite of the calibrated hedging
  `verify-before-asserting` enforces. The plan has no measurement that would distinguish
  "output got plainer" (intended) from "output got looser / more assertive" (regression),
  because its register measurement (crack #1) scores *readability*, which improves in both cases.
- **Rationalization risk is structural.** The team has a register-improvement judge that
  *wants* to see improvement (crack #1 makes "register improved" a pass condition). When the
  neutrality eval is noisy (K=3 majority on N≈30, the system's own floor) and the register
  judge is positive, the natural read of a borderline result is "register up, behavior held" —
  the plan has built an oracle that is biased toward shipping.

**Recommendation:** Before any rewrite, run the cheapest possible premise test: take 2-3
existing scenarios, rewrite *only* the brain's Voice/register-adjacent lines plain, run the
mainloop probe, and measure whether *output* register actually moved while behavior held. If
the priming effect is small or null, the entire campaign is unjustified and should be cut to
a one-doc opportunistic cleanup. Do not green-light 8 docs on an unmeasured premise.

---

## S2 — "File-splitting first: no" is wrong; trigger-fired prose still sits on the hot path

The plan's locked decision (line 21): structural splits are done, so the plain pass touches
only "text that STAYS." **Verified false in two places.**

1. **The brain's capability prose is still resident, not relocated.** Brain lines 111-125
   (`## Capabilities`, 15 lines) plus the brownfield (L121, ~5 lines), forge (L123, ~8 lines),
   and studio (L125, ~4 lines) paragraphs are full descriptive prose, loaded **every
   session** — but each describes a capability that only fires conditionally (brownfield: only
   on an unfamiliar repo; forge: only when a manifest governs the code; studio: only on design
   work). The plan claims step-2 (`e7d88f6`) already "thinned to dispatch pointers." It did
   not — these are still multi-line explanations, not pointers. This is a direct violation of
   the user's own `[high] Architecture by volatility` rule (USER.md L18: "mechanisms delivered
   by their own trigger (hook / on-demand), not parked in the hot path"). **Plain-ifying this
   prose in place is wasted work** — it should relocate behind its trigger first, after which
   the surviving hot-path line is a one-line pointer that needs no plain pass at all.

2. **"step-3 Continuity relocation done" is false.** The only `relocate` commit (`5e6feeb`)
   moved the *context-packet*, not Continuity. The `## Continuity & integrity` section (brain
   L102-109) is fully resident and always-loaded. The plan itself contradicts its own locked
   decision: line 22 says the Continuity *trim* "folds into the phase-1 brain pass" — i.e. it's
   a pending trim, not a finished relocation. The locked-decisions block is internally
   inconsistent.

**Recommendation:** Re-audit what is actually trigger-fireable on the always-loaded brain
*before* phase 1. The Capabilities/brownfield/forge/studio blocks are the prime candidates to
push behind triggers (or to one-line pointers) — relocate, then don't plain-ify what's no
longer there. This likely *shrinks* phase-1 scope, which is the right direction.

---

## S3 — Global blast radius: the eval structurally cannot catch a cross-project regression

Phase 2 rewrites `~/.claude/rules/*` — `align`, `verify`, `honor` — which load in **every
project on the machine**, not just Mimir. The plan flags the blast radius but claims
"eval-sanity" covers it. **It does not, and I verified why.**

`mainloop-probe.js` runs `claude -p --settings '{outputStyle: mimir}'` from a neutral temp
dir. Globals load regardless of cwd (the probe's own comment confirms), so the rules *are*
present — **but the Mimir brain is also always present in every one of the 53 scenarios.**
There is no scenario that runs a bare `claude -p` with no Mimir output-style, in a foreign
project, exercising a rewritten rule on its own. So:

- A rewrite that subtly weakens `verify-before-asserting` or `align` could be **masked** in
  every eval because the Mimir brain re-states the same disciplines (the brain has its own
  "verify load-bearing claims" and proportional-gate language). The eval would stay green while
  the rule is broken *for every non-Mimir project* — vanilla Claude Code in some other repo
  now gates less, or asserts unchecked facts more. That regression is invisible to this bank
  by construction.
- The most dangerous single edit in the whole campaign is `align-before-executing` L5 (the
  informed-override bar) and `verify-before-asserting` L5 (the no-chaining rule). Both are
  terse encodings of behaviors that took eval campaigns to land. A "plainer" rewrite that
  splits L5's "engaged the stated cost" clause loses the precise condition under which an
  override counts — and nothing in the Mimir bank tests override-counting *outside* the Mimir
  spine scenarios.

**Recommendation:** Either (a) descope `~/.claude/rules/*` out of the campaign entirely —
they are global, terse, and already rated "dense but correct"; the priming benefit on
*Mimir's* output is marginal since the brain dominates register anyway — or (b) before
touching them, add a control: a bare-`claude -p` (no output-style) probe on 2-3 override /
verify / gate situations, run against old-rule vs new-rule, and require behavioral parity.
Without (b), "eval-sanity" on rules is a false-green generator. Default recommendation: **(a),
don't touch the global rules.** The cost/benefit is upside-down — high blast radius, marginal
priming gain, no real safety net.

---

## S4 — The applied-but-un-evaled USER.md header should roll back (or at minimum be frozen)

Confirmed live: USER.md mtime is **today (2026-06-24 09:11)**; the merge/regrade/contradiction
header (L8-12) is applied. It is **not git-tracked** (lives in `~/.claude/mimir`, outside any
repo) — so there is no clean `git revert`; rollback is a manual re-edit and the prior text may
be unrecoverable if not stashed.

Worse than the plan admits: this header is **not inert documentation**. The
`profile-budget-hook.py` is **wired live** (verified in `~/.claude/settings.json`, PreToolUse
Write|Edit). The header rules now govern an automated housekeeping path that fires on every
USER.md write. So an un-evaled rule-change is already shaping live behavior, on a global
always-loaded file, with no test and no easy undo. This is the exact `[high] Honor
verification` / eval-gate violation the plan's own crack #4 names — and the plan's proposed
fix is to "bring it into eval scope before we call it done," i.e. *keep it live and validate
later*. That inverts the order the system insists on everywhere else (candidate → eval →
promote).

**Recommendation:** Snapshot the current header to a `.bak` now (so it's recoverable), then
**roll the live header back to the last evaled/known-good USER.md state** until the
merge/regrade/contradiction rules pass a control-calibrated scenario. The cost of rollback is
near-zero (the old behavior was the status quo for months); the cost of leaving an un-evaled
rule driving a live hook on a global file is a silent, hard-to-attribute drift in how the
user-model gets written. The plan's "validate later" is the wrong call by the team's own rules.
(If the header is genuinely low-risk, that's an argument it didn't need to ship hot either —
either way, eval-then-promote, don't promote-then-eval.)

Note also crack #5 is correct and should be acted on, not just noted: the "long silence
downgrades" grade has no clock/trigger and is unenforceable — ship the contradiction-regrade,
**cut** the silence-decay from the header text so the doc doesn't carry a rule nothing fires.

---

## S5 — Scope is unbounded; "done" is soft; phase 3 hides the creep

- **The scan already found 14+ docs with hotspots, not 8.** The named-8 framing
  (goal) collides with the scan's per-doc evidence: DESIGN §9, PRINCIPLES #15, huldra.md L15,
  BROWNFIELD L46-50, freya.md L47, SKILL.md, context-packet-spec, SELF-ITERATION all carry
  flagged hotspots. Phase 3 is where every one of these lives. The "done line" (line 70:
  "phases 1-2 are the must, phase 3 is nice-to-have") is the creep vector — "nice-to-have"
  with a written hotspot list is a backlog that will pull the campaign for weeks. There is no
  acceptance criterion that says *when* the campaign is allowed to stop with phase 3
  untouched.
- **Phase 3 is not cleanly deferrable as claimed.** PRINCIPLES.md is *both* the eval
  expected-behavior source *and* a phase-3 target (the plan's own crack #3). The plan
  "freezes semantics," but a plain-ification of a principle's wording that the eval traces to
  is a live risk even if "semantics frozen" is the intent — wording *is* what the rewriter
  changes, and the eval's expected-behaviors are stated in that wording. Deferring phase 3
  doesn't remove this; it just delays the collision. Better to **declare PRINCIPLES.md
  permanently out of scope** (like the forge prompts already are), not "frozen but eventually
  rewritten."
- **The register-improvement judge (crack #1) is a new bad oracle.** The plan asks "does this
  create a new bad oracle?" — yes. A judge whose pass condition is "register improved" will
  reward change-for-its-own-sake and has no ground truth (unlike behavioral scenarios, which
  trace to a principle). USER.md `[high] eval-rigor` and the bank philosophy is "expected
  behavior traces to a principle, never status quo" — a readability score traces to nothing
  but the rubric the same team wrote. It will rubber-stamp the campaign.

**Recommendation:** Hard-bound the campaign to phases 1-2, and *within* phase 2 only USER.md
body + project CLAUDE.md (drop the global rules per S3). Declare phase 3 and PRINCIPLES.md
out of scope, not deferred. Drop the register-improvement judge; if you want a register check,
use the user's eyeball (taste, per USER.md `eval-rigor`: judges score function, Tim's eyeball
scores taste) — not a synthetic judge.

---

## S6 — The biggest thing the plan misses: opportunity cost + irreversibility asymmetry

The plan never asks *what this campaign costs against the alternative of not doing it.* Every
doc it rewrites is currently working — these are battle-tested, eval-passed instruction
surfaces. The expected upside is a *register nudge* whose existence is unproven (S1). The
downside is a silent regression in a discipline (spine, verify, gate) that the team only
catches if a scenario happens to cover that exact phrasing — and the bank has **53 scenarios
covering Mimir-context behavior only** (verified: zero cover the global rules in a
non-Mimir context, zero cover the new USER.md header rules). The risk is asymmetric: the
gain is bounded and speculative; a missed regression on `align`/`verify` is unbounded and
global and may go unnoticed for weeks because nothing in the loop exercises it.

The lead also misses that **the brain already dominates the agent's output register** — it's
22KB of voice-and-cadence loaded every turn, with an explicit Voice section. If register
priming is real, the brain is ~90% of it; the rules and specs are noise on top. That argues
the *entire* phase 2/3 surface is low-leverage and the campaign should be **one doc: the
brain.** Do the brain (phase 1) under full staged eval, measure whether output register
actually moved, and *stop*. If it moved, you've got your win at 1/8th the blast radius. If it
didn't, the premise is dead and you saved seven rewrites.

**Recommendation:** Collapse the campaign to: (1) premise test on the brain, (2) if positive,
brain-only plain pass under the existing staged loop, (3) re-measure, (4) stop. Treat
everything else as a separate, later, opt-in cleanup — not this campaign.

---

## Summary of recommended actions

- **Don't do** the global `~/.claude/rules/*` rewrites (S3) — upside-down cost/benefit, no
  safety net.
- **Don't do** phase 3 / PRINCIPLES.md as part of this — declare out of scope (S5).
- **Roll back** the live un-evaled USER.md header until evaled; snapshot first; cut the
  unenforceable silence-decay clause (S4).
- **Re-audit** trigger-fireable hot-path prose (Capabilities/brownfield/forge/studio,
  Continuity) and relocate *before* plain-ifying — the "splitting is done" claim is false (S2).
- **Test the premise first** on the brain; collapse the whole campaign to brain-only unless
  the priming effect is measured and real (S1, S6).
- **Drop** the register-improvement judge (new bad oracle); use the user's eyeball for taste.
