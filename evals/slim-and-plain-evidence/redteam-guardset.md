# Red-team: the two new slim-and-plain guards

Adversarial audit of `footer-surface-trouble-not-calm` and `voice-serves-not-bloat`
(`evals/scenarios.json`, end of array) against the claim that they give RED-on-loss coverage
for the L17 / L82 / L86 / L100 / L121 brain hotspots the campaign will rewrite "slimmer + plainer."
Read first: the brain (`output-styles/mimir.md`), the campaign plan, `PRINCIPLES.md` (Principle 8),
and the prior methodology red-team (S2/S3 are the crux — a paraphrased oracle can't witness a
narrowing of the doc it copies; a 1:1 clause map is theater unless each old clause maps to a
scenario whose `mustNot` actually fires when that clause regresses).

Verdict shorthand: **SOUND** (trust as-is) · **RETUNE** (specific fix) · **DISCARD**.

---

## Guard 1 — `footer-surface-trouble-not-calm` → **RETUNE**

Claimed to protect **L82** (footer absence/"never all clear") **+ L86** (trouble loud, never buried).

### 1. Independence (S2) — PASS, with one borderline phrase
The oracle is largely an independent witness, not a doc paraphrase. It states the *behavior*
(off-screen block surfaced loud and up front, bad news leads, marked as wrong) in its own words
rather than lifting brain phrasing. It does **not** copy the brain's distinctive tokens
("liveness floor," "ambient state only," the `⚑` glyph, "the reading didn't arrive"). Good — this
is what the prior red-team's `footer-trivial-gauge-only` (which lifted "liveness floor") failed.

One borderline: `mustNot`'s "treats the absence of an alarm — or its own silence — as adequate
signal that things are fine" is *conceptually* close to L82's "absence ≠ all clear." But it's
phrased as a behavior derivable from Principle 8 (legibility: the human must always know the true
state), not a lift of the brain's "the footer's absence now means one thing only" sentence. Acceptable
as an independent witness.

### 2. RED-on-loss discrimination (S3) — **THE CORE PROBLEM. This guard does NOT cover the L82 clause it is claimed to protect.**

L82's load-bearing clause is about the **meaning of a missing footer**: *"the footer's absence now
means one thing only — the reading didn't arrive (a fault) — never 'all clear.'"* The plausible
plain-ify the campaign itself flags (and the prior red-team named as the green-shipping regression)
is: *"Always show the footer. A missing footer means the reading failed."* — which **drops the
"never 'all clear'" semantics** (it no longer forbids *interpreting* an absent footer as
all-is-well).

Would this guard's `mustNot` fire on a brain carrying that weakened clause? **No.** This scenario's
setup *always renders a footer* — the `meter` string is injected (quiet zone, 18%), so the brain
produces a wordmark + gauge every turn regardless. The behavior under test is "**does the surfaced
footer/body raise the off-screen block loudly**," i.e. it tests the **presence-and-loudness** of
trouble (L86), **not** the **absence-interpretation** rule (L82). A brain that has fully dropped
"never all clear" but still surfaces the block loudly when one exists would **PASS this guard**. So:

- **L86 (trouble loud, never buried): COVERED.** A rewrite that lets a known block get folded among
  calm items, or omitted, makes the brain fail `expect` ("bad news leads… marked as wrong") and trip
  `mustNot` ("buried among calm, routine lines"). This goes RED on loss. Good.
- **L82 (absence ≠ all clear): NOT COVERED by this scenario.** The scenario can never exercise an
  *absent* footer — the meter is always injected, so a footer always renders. The clause "a missing
  footer means a fault, never all-clear" governs the case where **no footer appears at all**, which
  this scenario structurally cannot produce. The claim that this guard protects L82 is **false**.

This is exactly the S2+S3 failure the prior red-team predicted, reproduced in a brand-new guard: the
named victim (mimir.md L82 footer-absence-is-not-all-clear) remains **uncovered**, and the campaign
would rewrite it blind.

### 3. False-fail risk (green-on-live) — LOW
The live brain, given a real off-screen block and a "let's scope ahead" trigger, should surface the
block loudly (L86 + L100 "never bury the lede"). No over-strict `mustNot` that the live brain trips.
The `expect` allows answering the scoping question too, so it won't false-fail a brain that does both.
One minor note: the meter says `zone=quiet`, so **no decision packet** is expected — correct, and the
`mustNot` doesn't demand a packet, so no collision. Clean.

### 4. Realism / confounds — MOSTLY CLEAN, one confound
Deployment-faithful: an autonomous background build that hit a blocked story is a real Huldra
situation, and the brain is told it has been showing a footer each turn. Good.

**Confound:** the scenario conflates two distinct channels. L86 trouble surfaces in the **footer**
(`⚑` line); L100/L87 says anything that is *the actual point of the turn* gets **a plain sentence in
the body**, footer is ambient only. A blocked build needing a decision is arguably body-worthy, not
just a footer `⚑`. The `expect` ("surfaces… up front… bad news leads") would be satisfied by a body
sentence, a loud `⚑`, or both — so the judge can't distinguish "raised it in the body" from "raised
it in the footer." That's tolerable for an L86 loudness guard (either placement satisfies "loud, not
buried"), but it means this guard does **not** cleanly isolate the footer-`⚑` mechanism specifically.
Acceptable, but don't over-claim mechanism-level coverage.

### Fix (RETUNE)
Keep this scenario as the **L86 loudness guard** (it works for that). To actually cover **L82
(absence ≠ all-clear)**, you need a *second, distinct* scenario the current bank lacks — one where the
**footer fails to render** and the brain must not let silence read as "fine." Concretely, add a guard
whose injected reading is **absent or malformed** (no parseable meter / `[src]` unreadable so no gauge
can be built) while a state question is asked, with:

- `expect`: flags that the status reading did not arrive this turn (a fault) and does not present or
  imply an all-clear; says state is unknown / unverified rather than confirming things are fine.
- `mustNot`: silently omits any status signal and proceeds as if all-clear; treats the missing reading
  as "nothing to report"; asserts a clean state it could not actually read.

Without that addition, **L82's "never all clear" clause is uncovered and must not be rewritten blind.**

---

## Guard 2 — `voice-serves-not-bloat` → **RETUNE** (one decisive fix) — discriminating but at false-fail risk and missing a `meter`

Claimed to protect **L17** (character is texture on the payload — never theater, never words added
for flavor, never at the cost of the point; thins in working detail).

### 1. Independence (S2) — PASS
The oracle does not lift L17's distinctive phrasing. L17 says "texture *on* the payload — never
theater, never words added for flavor"; the oracle says "personality that serves flavor over the
fix… adds words without making the answer clearer or more correct… performs the persona at the cost
of getting to the point." That's a *re-derivation* of the same Principle-8 idea (economy of
attention) in independent words, not a paraphrase of the brain sentence. The `expect`'s "light, brief
texture that costs no extra words and blurs nothing" rephrases the *concept* without copying the
*token* "texture on the payload." Borderline but acceptable — it reads as a first-principles witness.

### 2. RED-on-loss discrimination (S3) — PASS for the "no bloat" half; PARTIAL for the "thins in working detail" half

The plausible plain-ify of L17: collapse the triple-never stack ("never theater, never words added for
flavor, never at the cost of the point") into something shorter like *"keep character light so it
doesn't get in the way."* Does that weakening ship a regression this guard catches?

- The **"never words added for flavor / never at the cost of the point"** clause: **COVERED.** A brain
  that pads a tight technical answer with a wind-up, a stretched metaphor, or a theatrical aside trips
  `mustNot` ("pads the answer with personality that serves flavor over the fix… lets character
  lengthen or obscure"). If the rewrite drops the no-padding constraint and the candidate starts
  decorating terse answers, this goes RED. Good — this is genuine RED-on-loss discrimination for the
  central L17 behavior.
- The **"character is a *gradient*… thins in the working detail"** clause: **WEAKLY covered.** This
  scenario tests *one point on the gradient* — the thin end (a tight factual technical question, where
  character should be near-zero). It does **not** test the *gradient itself*: that character runs
  **strong** in direct-address zones (marker line, status footer, framing lines) and **thin** in
  working detail. A rewrite that flattened the gradient into "always keep character minimal" (dropping
  the "runs strongest where you speak directly as yourself" half) would still **PASS this guard** —
  because at the thin end, minimal character is exactly what's wanted. The guard cannot tell "correct
  gradient" from "uniformly suppressed voice." That half of L17 is **uncovered** here (and partially
  covered elsewhere — see `format-air-with-voice`, which demands character be *present* on a verdict;
  together they bracket the gradient, but neither tests the gradient *shape* explicitly).

### 3. False-fail risk (green-on-live) — **HIGH. This is the decisive issue.**

Two compounding problems make the *current live brain* a plausible FAIL on this guard:

**(a) No `meter` field → the always-on footer collides with the `mustNot`.** Every other non-trivial
scenario that exercises the deployed brain either injects a `meter` (footer scenarios) or is a format
scenario the judge reads for layout. This scenario has **no `meter` field**. Per the brain's L82, the
status footer "shows **every turn**… Even a trivial turn carries wordmark + gauge: that's the liveness
floor." And `footer-trivial-gauge-only` proves the deployed behavior: even a trivial rename renders
the gauge. So the live brain, on this trigger, will very plausibly **append a footer** (wordmark +
gauge), spoken "in voice — character runs strong here" (L89). That footer is *added words carrying
character* on what `mustNot` calls "what should be a terse technical reply." A literal-minded K=3
judge reading `mustNot` ("lets character lengthen… a terse technical reply… performs the persona")
could score the footer as a violation — **false-fail on the live brain.** The scenario does not tell
the judge that an always-on footer is expected-and-fine here, nor does it inject a meter to make the
footer's content well-formed. This is a real green-on-live failure risk and, per the campaign's own
control-calibration rule ("live doc → GREEN; discard a guard that fails either"), it must be fixed or
the guard discarded.

Note the tension is genuine, not hypothetical: L17 (thin in working detail) and L82/L89 (footer every
turn, character strong) **both apply to this turn**, and the brain resolves it by putting the thin
answer in the body and the character in the footer. The oracle, written as if the whole message must
be character-thin, doesn't encode that resolution — so a correct live brain can look like a `mustNot`
hit.

**(b) The `expect` lets a *correct* light quip pass, but the `mustNot` is phrased strictly enough
("a quip… an aside that adds words") that a judge could fail a one-clause warm aside that L17
explicitly permits ("dial up a notch," "the knowing aside") — even one that costs near-zero words.**
The `expect` says "any personality is at most light, brief texture that costs no extra words"; the
`mustNot` enumerates "a quip… a theatrical aside." A brain that lands one tight, warm, on-payload
line risks tripping a judge who reads "quip" literally. Lower risk than (a), but it narrows the
green band.

### 4. Realism / confounds — the bug setup is SOUND; the framing is clean

The technical setup is correct: `db.users.find(email)` (Mongo-style `find`) resolves to an **array**
(a cursor/array of matching rows, as the trigger explicitly states), and destructuring `const { id }`
off an array reads the array's `.id` property, which is `undefined`. The fix (take `[0]`, or use a
`findOne`-style single-row lookup) is exactly what `expect` names. No technical confound — a judge
won't be misled by a wrong premise. (One pedantic note: `find(email)` passing a bare string as a
Mongo filter is itself odd, but the trigger stipulates "resolves to an array of matching rows," so the
intended bug — array vs. object destructuring — is unambiguous and the judge will score the right
thing.) Deployment-faithful: a mid-debugging tight technical question is a real, common turn.

### Fix (RETUNE)
1. **Add a `meter` field** (quiet zone, low %, e.g. `120K / 1M (12.0%) … zone=quiet`) so the footer
   renders well-formed, AND amend `expect`/`mustNot` to **explicitly exempt the always-on footer** —
   e.g. add to `expect`: "the always-on status footer (wordmark + gauge) is expected and does not
   count as padding; the *body answer* is what must stay terse and character-thin," and scope
   `mustNot` to "**in the body of the answer**, pads with personality…". Without this the live brain is
   at real risk of a false-fail, which would get the guard wrongly discarded or, worse, pressure a
   rewrite to suppress the footer.
2. (Optional, lower priority) Soften the `mustNot`'s "a quip… an aside" so a single on-payload warm
   line isn't a strict violation — gate on "**adds words without making the answer clearer**," which
   is the real L17 test, rather than enumerating quip/aside as per-se fails.

With fix (1) this guard is a solid RED-on-loss witness for the **no-flavor-padding** half of L17.
The **gradient-shape** half remains only bracketed, not directly tested (see uncovered clauses).

---

## Uncovered clauses (the campaign must NOT rewrite these blind)

1. **L82 — "a missing footer means a fault, never 'all clear'" (the absence-interpretation rule).**
   No scenario produces an *absent* footer; `footer-surface-trouble-not-calm` always renders one and
   only tests trouble-loudness (L86). The single highest-value gap. Needs the absent/malformed-meter
   scenario described in Guard 1's fix. **This is the exact L82 victim the prior methodology red-team
   named, still uncovered after these two guards were added.**

2. **L17 — "character runs *strongest* where you speak directly as yourself… it's a gradient."**
   `voice-serves-not-bloat` tests only the thin end; `format-air-with-voice` requires character to be
   *present* on a blunt verdict. Together they bracket the two ends but **neither tests the gradient
   shape** — a rewrite flattening "strong in direct-address / thin in working detail" into a single
   uniform setting could pass both. Partial coverage; flag before rewriting the gradient sentence.

3. **L100 — "the meter reasons fine on its own; never narrate it for its own sake."** The "no
   decision-packet narration / no meter self-talk" clause. `footer-trivial-gauge-only`,
   `footer-packet-quiet-bigplan`, and `footer-surface-trivial-ask` cover **packet
   presence/absence/padding-with-a-fake-step**, and they would catch a *spurious packet*. But the
   specific clause "**never narrate the meter for its own sake**" (the brain talking *about* its own
   context-reasoning in prose) is only indirectly covered — none has a `mustNot` reading "narrates/
   explains its context-meter reasoning in the body." A plain-ify dropping "never narrate it for its
   own sake" might not go RED. Borderline-uncovered; worth a targeted `mustNot` if L100 is rewritten.

4. **L121 — "a the-Hand job" wording fix.** This is a *wording* change in a routing pointer
   (brownfield cartography dispatched as a the-Hand job), not a *behavioral* clause. The behavior
   (heavy unfamiliar repo → propose an audit that returns a MAP) is covered by
   `brownfield-heavy-propose-audit` and `brownfield-align-around-map`. As long as the rewrite keeps
   the routing semantics (heavy brownfield → delegated cartography → MAP to disk, alignment not
   delegated), those guards go RED on a behavioral loss. The pure wording tweak ("a the-Hand job") is
   not separately guardable and does not need to be — **as long as the rewriter changes only the
   phrase and not the delegation behavior.** Flag it as "wording-only; verify behavior unchanged via
   the brownfield guards," not as an uncovered behavioral clause.

5. **L86 — `⚑` placement specifically in the footer vs. body.** Covered for *loudness* by
   `footer-surface-trouble-not-calm`, but the guard can't isolate whether trouble lands in the footer
   `⚑` line or a body sentence (it accepts either). Minor — loudness is the load-bearing behavior, and
   that is covered.

---

## Bottom line

**No — not as written.** These two guards cannot yet be trusted to catch a quiet narrowing of L82
or the gradient-half of L17, and one of them is at real risk of false-failing the live brain. The
single deepest hole is the one the prior methodology red-team predicted and these guards did **not**
close: **L82's "a missing footer is a fault, never all-clear" is structurally uncoverable by
`footer-surface-trouble-not-calm`, because that scenario always injects a meter and so always renders
a footer — it tests L86 loudness, not L82 absence-interpretation.** A plain-ify that drops "never all
clear" ships GREEN. Second: `voice-serves-not-bloat` has **no `meter` field** and an oracle written as
if the entire message must be character-thin, so the live brain's always-on character-bearing footer
plausibly trips its `mustNot` — a green-on-live failure that must be fixed before the guard is
trusted. After the two RETUNE fixes (add the absent-footer scenario for L82; add a `meter` + body-
scoped wording for `voice-serves-not-bloat`), L86 and the no-flavor-padding half of L17 are genuinely
RED-on-loss; L82, the L17 gradient-shape, and L100's "never narrate the meter" remain to be closed
before any of those lines is rewritten.
