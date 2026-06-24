# Step 2 — full brain pass results (GREEN, awaiting promote approval)

The slim half. Candidate = live + Step 1 hotspots + Capabilities relocation + Continuity trim + L100 fix.
**Behavior-neutral across all tested sections; red-team cleared SAFE TO PROMOTE.** Promote is user-gated.

## Edits in the candidate (cumulative −222 words / −1474 chars off the hot path)
- **Step 1** (already committed `e1e25a4` as guards; brain edits ride this promote): L17/L82/L100/L121 slim+plain.
- **Step 2a — Capabilities relocation** (the big slim win): BMAD / brownfield / forge / studio *mechanics*
  moved off the every-turn path into their on-demand docs; trigger-only pointers kept. Execution-modes
  block kept (cross-cutting, no single target doc), prose slimmed. The forge "keys-on-a-manifest"
  negative boundary + the execution-mode axis were KEPT on the hot path (coverage analysis flagged them
  as uniquely-held / highest-risk). Analysis: `step2-capabilities-coverage.md`.
- **Step 2b — Continuity trim** (de-dup): cut verify-tail from L104 (survives at The read L58 + the
  always-loaded global verify-before-asserting.md) and the parked-bet resurfacing sentence from L107
  (survives at Status L86). Kept the disk-source/reconstruct-state disposition + the override-signal rule.
- **L100 fix** (post red-team): restored the imperative ("don't narrate it for its own sake") while
  keeping the de-personification — the red-team's one finding.

## Decisions
- **Forge-floor dedup: SKIPPED.** The floor is stated 3× (L33 proportionality / L36 routing / relocated
  pointer) because it's the highest-stakes line; the three serve three decision contexts. Protective
  reinforcement, not bloat — not worth softening to save ~20 words.
- **Over-determination cuts (L17-restraint / L86-emphasis): SKIPPED.** Step 1 showed them over-determined,
  but cutting entirely is a bigger claim than 2 scenarios cover; ~16 words for real risk. Kept the slimmed
  reworded versions.

## Gates passed
- **Full-diff red-team: SAFE TO PROMOTE** (`redteam-fulldiff.md`). All 6 regions CLEAN except L100
  (narrowed → fixed). Confirmed: every relocated sentence's content present in its target doc; both
  Continuity cuts have verified survivors in unchanged lines; forge boundary intact at the hot path.
- **Final neutrality sweep (K=3, per-slot retry): 8/8 NEUTRAL**, candidate = live at 100% each.
  footer-absent (12/12 → 10/10), voice (15/15 → 10/10), forge-tooling-boundary (10/10 → 10/10),
  verify-recalled (10/10), verify-no-inference-chaining (10/10), spine-informed-override (10/10),
  usermodel-write-global (10/10), style-earn-not-podium (10/10).
- Multi-turn: not run — the diff touches no orientation/multi-turn behavior (those dispositions kept
  verbatim); the only multi-turn-ish cut (parked-bet) is a duplicate preserved at Status L86.

## NOT yet done
- **PROMOTE** — gated on Tim's explicit approval (changes the live default brain for every session).
  On approval: `evals/brain-candidate.sh promote && git add -A && git commit` (brain + Step-2 evidence
  as one seam; bank already committed at `e1e25a4`).
- **Doc-drift hygiene (follow-on):** port the forge "keys-on-a-manifest" carve-out into `huldra.md` +
  `BROWNFIELD.md` (currently state forge-always narrower; brain stays canonical, so safe).
