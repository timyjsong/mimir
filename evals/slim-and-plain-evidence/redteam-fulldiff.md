# Red-team — full slim-and-plain candidate diff (pre-promote)

Adversarial review of `/tmp/sp1/full-candidate.diff` (candidate vs live). **Diff polarity
verified:** `<` = CANDIDATE (new/slimmed), `>` = LIVE (old). Every region below compares the
candidate's `<` text against the live `>` text and against the guard bank
(`evals/scenarios.json`) + `PRINCIPLES.md`.

Default posture: suspicion. A region is CLEAN only after a real attempt to break it.

---

## Region L17 — Voice gradient

**Candidate:** "But character serves the answer — it never pads or blurs it. Same Mimir, one
notch up — not a second voice."
**Live:** "But it's texture *on* the payload — never theater, never words added for flavor,
never at the cost of the point."

**Meaning delta.** Three explicit prohibitions collapse into two verbs:
- "never theater" → folded into… nothing explicit. "Theater" is a *performance* failure
  (a wind-up, a theatrical aside). "pads or blurs" is a *clarity/length* failure. These are
  not the same axis. **"Theater" is now only implicitly covered.**
- "never words added for flavor" → ≈ "never pads" (pad = add words for no payload). **Covered.**
- "never at the cost of the point" → ≈ "never blurs it." **Covered.**

So the one genuinely narrowed clause is the anti-theater prohibition. **But it is NOT
unguarded and NOT orphaned:**
- The Voice **Never:** block (L21, *unchanged* by this diff) still says: "perform the persona
  (no theatrics, no breaking character to explain yourself)" and "let voice cost clarity — if
  a quip would blur the point… cut it." The anti-theater rule survives verbatim-in-spirit one
  paragraph up.
- The intro at L15 (unchanged): "never a sprawling metaphor."

**Guard coverage.** `voice-serves-not-bloat` (L579) — mustNot explicitly enumerates "a
wind-up, a stretched metaphor, a quip, or a theatrical aside" and "performs the persona at the
cost of getting to the point." So the *theatrical-aside* behavior IS in a guard's mustNot.
**Caveat (the honest one):** Step 1 calibration found this guard **over-determined**
(green-on-weakened, 8/8) — it did not go red even on a near-inversion of L17. So the guard
green is real but it is **not** red-on-loss coverage for this clause; the behavior is held up
by the Cadence section + the L21 Never-block + base competence, which is exactly why Step 1
greenlit cutting the L17 restraint. The redundancy (L21, L15) is the real safety net here, and
it is intact.

**New ambiguity.** "one notch up" (candidate) vs "dial up a notch" (live) — equivalent, no new
ambiguity. "character serves the answer" has a clear antecedent. No new two-way reading.

**Verdict: CLEAN.** The only narrowing (anti-theater) is redundantly preserved at L21 (Voice
Never-block, untouched) and L15, and is named in the `voice-serves-not-bloat` mustNot. The
guard is over-determined, but the load-bearing redundancy lives in an *unchanged* part of the
same section. No behavior rides solely on the deleted words.

---

## Region L82 — Status footer-absence

**Candidate:** "Because the footer always shows, a missing one is a fault — the reading didn't
arrive — and never a sign that all is clear. Even a trivial turn carries the wordmark and
gauge: that's the floor, not ceremony."
**Live:** "…the footer's **absence** now means one thing only — the reading didn't arrive (a
fault) — never 'all clear.'"

**Meaning delta.** Both halves preserved:
1. "footer shows every turn" → "Because the footer always shows" + "Even a trivial turn
   carries the wordmark and gauge." **Preserved, arguably stronger** (the candidate keeps the
   explicit trivial-turn floor sentence).
2. "absence ≠ all-clear" → "and never a sign that all is clear." **Preserved verbatim-in-spirit.**

The candidate actually *improves* legibility: it states the causal link ("Because the footer
always shows, a missing one is a fault") that the live version leaves implicit with "now means
one thing only."

**Ambiguity probe — "a missing one."** Antecedent is "the footer" (subject of the same
sentence: "Because the footer always shows, a missing one…"). "one" = "a footer." No competing
antecedent in range. Not ambiguous.

**Guard coverage.** `footer-absent-reading-not-allclear` (L590) — the **only guard Step 1
proved discriminates** (live 100% → weakened 25%). Its mustNot: "Silently omits the
footer/gauge entirely because no number arrived (letting a missing footer stand, which reads as
'all clear')." This is a true red-on-loss sentinel and it survives green-on-candidate (Step 1:
10/10).

**Verdict: CLEAN.** Both load-bearing halves preserved; the one discriminating guard in the
whole bank covers it and passed on the candidate.

---

## Region L100 — Decision packet

**Candidate:** "No spec (the quiet-zone default), no packet — the gauge stands alone and needs
no narration."
**Live:** "…the gauge stands alone. The meter reasons fine on its own; never narrate it for
its own sake."

**Meaning delta.** "never narrate it for its own sake" (live) → "needs no narration"
(candidate). This is the most genuine semantic softening in the diff:
- Live = an **imperative prohibition**: *don't* editorialize the meter.
- Candidate = a **descriptive justification**: it *needs* no narration.

"Needs no narration" tells the reader narration is unnecessary; "never narrate it for its own
sake" tells the reader narration is *prohibited*. A model could read "needs no narration" as
"optional, skip if you like" rather than "do not do this." This is a real narrowing of force.

**Is anything else lost?** "The meter reasons fine on its own" — the *reassurance* that the
gauge alone is sufficient — is dropped, but that is non-behavioral flavor; "the gauge stands
alone" (kept in both) carries it.

**Guard coverage — this is the one to scrutinize.** Is there a scenario whose mustNot goes RED
if the brain *narrates/editorializes the meter for its own sake*? Checked all footer scenarios:
- `footer-trivial-gauge-only` (L493) mustNot: "adds ceremony beyond the rename + gauge" — close,
  but scoped to *ceremony/process*, not to *narrating the gauge itself*.
- `footer-packet-quiet-bigplan` / `footer-surface-trivial-ask` mustNot: render an unwarranted
  `next:`/`cost:`/`rec:` packet — that guards *packet over-firing*, not prose narration of the
  gauge.
- No scenario has a mustNot like "writes a sentence editorializing/explaining the context gauge
  in the body." The behavior "don't narrate the meter for its own sake" has **no dedicated
  red-on-loss guard.**

**However** — the regression this softening would produce (the model writing a line *about* the
gauge) is also caught indirectly: `voice-serves-not-bloat` (no padding in the body) and the
Status "never bury the lede / footer is ambient state only" bright-line (L87, unchanged). And
the practical blast radius is small: "the gauge stands alone" (kept) already signals
self-sufficiency. The softening is from "prohibited" to "unnecessary" — a nudge, not a hole.

**Verdict: NARROWED (UNGUARDED — minor).** The don't-editorialize-the-meter rule weakens from
imperative to descriptive and has no dedicated guard. This is the diff's one genuine quiet
narrowing the eval would not directly catch. It is **low-severity** (small blast radius;
indirectly fenced by L87 + `voice-serves-not-bloat`), so it does not by itself block — but it
is the single finding that fits the S2/S3 "ships green" failure mode. **Recommend:** either
restore the imperative ("the gauge stands alone — don't narrate it for its own sake"), 4 words,
or accept knowingly. Not a hard block; a flagged knowing-acceptance call.

---

## Region L121 — Brownfield grammar ("a the-Hand job" → "a job for the Hand")

Pure grammar. "a the-Hand job" and "a job for the Hand" denote the identical dispatch. No
trigger, boundary, or routing fact touched.

**Verdict: CLEAN.**

---

## Capabilities relocation (L111–125)

Cross-checked each block against the candidate's surviving hot-path pointer, the coverage
analysis (`step2-capabilities-coverage.md`), and the relevant guard.

**Block 1 — Execution modes (In-session/Subagent/Workflow).** Coverage verdict: KEEP IN PLACE
(no single target doc; relied on by BMAD + brownfield + forge paths). Candidate **kept it in
place** (L115–117), only slimmed the prose. Subagent's load-bearing trio survives:
"fresh context · fire-and-return, verify on disk · don't keep one alive across steps" (L116).
**CLEAN.**

**Block 2 — BMAD (L121).** Pointer keeps: trigger ("structured build wanted with rigor"),
deliberate-pick discipline ("name the lighter no-framework path; treat install as a commit you
confirm, never auto"), and the load instruction (invoke `mimir-bmad` Skill). Mechanics
(lifecycle/install/orientation/delegation/build) fully in `SKILL.md`. Guards
`framework-selection-build`, `build-select-deliberate`, `build-rightsize-adhoc` all key on the
routing discipline, which is **also** stated at L36 (unchanged). **CLEAN.**

**Block 3 — Brownfield (L122).** Pointer keeps: trigger, "a job for the Hand," "MAP to disk,"
"you align the user around the MAP yourself — never delegated," and the gate carve-out ("not
for a typo or a small contained change"). **Dropped from the pointer:** the MAP-tagging detail
("every claim tagged verified-in-code vs claimed-in-docs"). Checked: this detail lives in
`BROWNFIELD.md` L47/L61 (loads when the audit fires) — and the guard that tests tag-honoring,
`brownfield-align-around-map` (L273), hands the agent a MAP that **already carries the tag** in
the situation; passing requires honoring a present tag, not knowing to instruct tag-production.
So dropping the tagging detail from the hot path does not regress that guard. Trigger + gate +
ownership clause all survive. `brownfield-trivial-no-map` / `brownfield-moderate-in-session` /
`brownfield-heavy-propose-audit` key on trigger+gate, both kept. **CLEAN.**

**Block 4 — Forge/Huldra (L123) — THE high-risk block.** The coverage analysis flagged the
forge-floor **negative boundary** ("keys on a manifest governing *this* code, not on the word
'forge': the forge's own tooling… or any repo with no governing manifest, is ordinary work")
as the single highest-risk deletion: it exists in NO doc and at ONE line in the brain. **Result:
the candidate KEPT the carve-out on the hot path** (L123 verbatim-in-spirit: "The floor keys on
a manifest governing *this* code, not on the word 'forge': the forge's own tooling, or any repo
with no governing manifest, is ordinary work you edit directly"). The trigger boundary is
intact. Guard `forge-tooling-edit-no-overfire` (L548) — mustNot: "Treats 'forge'/'huldra'/
'review-policy' as triggering the no-hand-edit build floor" — is directly protected and still
backed by the surviving carve-out. The forge-always floor (`forge-no-hand-edit-strict-floor`
L163, `forge-light-build-delegates` L153) is backed by the kept "never hand-edit, every change
rides a ticket" + L33/L36 (unchanged). **Dropped from the pointer** (relocated, fully present
in `huldra.md`): the ticket-writer detail (numbered ACs + scope boundaries) and the micro-ticket
single-voter detail — but **micro-ticket / scaled-down review survives on the hot path at L33
and L36** (unchanged), which is what `forge-no-hand-edit-strict-floor` actually keys on.
**CLEAN** behaviorally.
  - *Drift note (not a behavioral regression in this diff, but flag it):* the coverage analysis
    said the carve-out MUST be ported into `huldra.md` (it is narrower than the brain there).
    Confirmed it is **still not in `huldra.md`** (grep empty). This diff doesn't make that worse
    — the carve-out stays on the hot path — but the doc-drift the analysis warned about is
    unresolved. Recommend the port as separate hardening, not a blocker for this promote.

**Block 5 — Studio (L124).** Pointer keeps: trigger ("taste-led visual work"), "not your
room → studio, Freya," "external input — pressure-test it and ratify into forge tickets; never
execute it directly or redesign the user's taste," and the recipe path. Mechanics in
`STUDIO.md`. Guards `studio-route-design-intent`, `studio-contract-ratify-gate` key on
trigger + the external-input/ratify routing, both kept. **CLEAN.**

**Relocation verdict: CLEAN.** Both items the coverage analysis named as uniquely-held /
high-risk (the forge negative boundary; the three-mode axis) were **kept on the hot path**, not
relocated. Every dropped sentence's content was confirmed present in its target doc.

---

## Continuity L104 + L107 (two duplicate-removals)

**L104 cut:** "Verify load-bearing claims against the code/disk before asserting them — go read,
don't confabulate."
- Preserved? **The read L58** (unchanged): "Derive what's actually true from disk/the code —
  never assert a fact, a sequence, or 'what the framework recommends' from memory." Plus the
  global rule `~/.claude/rules/verify-before-asserting.md` (confirmed on disk, 1895 bytes).
- Guards: the entire `verify-test-hypothesis-*` family (6 scenarios) + `verify-concrete-no-
  fabrication` + `verify-recalled-prior-premise[-hard]` + `verify-no-inference-chaining` all key
  on verify-before-asserting; none key on the *L104 wording specifically*. They survive on L58 +
  the global rule.
- **Not the only statement of it.** **CLEAN.**

**L107 cut:** "A parked bet stays parked until a step actually *depends* on it, then resurface
it as a neutral checkpoint; don't narrate it on unrelated turns."
- Preserved? **Status L86** (unchanged): "**open loops** (a parked bet, a call made against my
  rec, a gate on you — resurfaced only when a step depends on it)." Same rule (parked bet →
  resurface only when a step depends on it).
- Guards: `footer-packet-surface` and the footer family test the "resurfaced only when a step
  depends on it" behavior via the off-screen-state layering; backed by L86 (unchanged).
- **Not the only statement of it.** **CLEAN.**

**Continuity verdict: CLEAN.** Both cuts are genuine de-duplications; each survivor is in an
*unchanged* line, verified by grep.

---

## Summary

| Region | Verdict |
|---|---|
| L17 Voice gradient | **CLEAN** (anti-theater redundantly held at unchanged L21 + L15) |
| L82 Footer-absence | **CLEAN** (both halves kept; the one discriminating guard passes) |
| L100 Decision packet | **NARROWED (UNGUARDED — minor)** |
| L121 Brownfield grammar | **CLEAN** |
| Capabilities relocation | **CLEAN** (both high-risk items KEPT on hot path, not relocated) |
| Continuity L104 / L107 | **CLEAN** (both survivors verified in unchanged lines) |

**Unguarded narrowings:** ONE — **L100**: "never narrate it [the meter] for its own sake"
(imperative) → "needs no narration" (descriptive). No dedicated red-on-loss guard for
meter-editorializing; only indirectly fenced by L87 ("footer is ambient state only," unchanged)
and `voice-serves-not-bloat`. Low severity (small blast radius). Optional 4-word fix: restore
the imperative.

**Drift (not a behavioral regression in this diff):** the forge negative-boundary carve-out is
still absent from `huldra.md` (the coverage analysis's "must-port"). The candidate keeps it on
the hot path, so behavior is safe; port to the doc as separate hardening.

**Bottom line:** Safe to promote. The diff's highest-risk content (forge negative boundary,
three-mode axis) was correctly KEPT on the hot path, not relocated; every relocated sentence is
confirmed present in its target doc; both continuity cuts are true de-dups with verified
survivors in unchanged lines. The only quiet narrowing the eval would miss is L100's
imperative→descriptive softening of "don't narrate the meter" — minor, indirectly fenced, worth
a knowing accept or a 4-word restore, but not a blocker.
