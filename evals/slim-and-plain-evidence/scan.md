# Mimir instruction-doc plain-language survey

A register scan of every instruction/persona/spec doc the Mimir agent reads. Goal: find passages that are *hard to read* — dense, jargon-packed, run-on, coined shorthand left unpacked — because the register of these docs primes the register of the agent's own output. **Not a rewrite.** Voice/wit/imagery stays; the target is only what forces a reread. "Plain" never means "more words" — a genuine hotspot is *both* dense *and* shortenable.

Ratings: **plain** (reads on first pass) · **mixed** (mostly clear, pockets of density) · **dense** (sustained jargon/run-ons that force rereads).

---

## Rating table

| Doc | Load freq | Rating | Plain-ify keeps it ≤ length? |
|---|---|---|---|
| `output-styles/mimir.md` (the brain) | every session | **mixed** | yes — mostly shorter |
| `~/.claude/mimir/USER.md` | every session | **dense** | yes — shorter |
| `/home/tim/.claude/CLAUDE.md` (global) | every session | **plain** | n/a (already plain) |
| `~/.claude/rules/align-before-executing.md` | every session | **dense** | yes — shorter |
| `~/.claude/rules/verify-before-asserting.md` | every session | **dense** | yes — shorter |
| `~/.claude/rules/honor-slash-commands.md` | every session | **mixed** | yes |
| `~/.claude/rules/diag-logs.md` | every session | **plain** | n/a |
| `projects/mimir/CLAUDE.md` (project) | every session in repo | **mixed** | yes |
| `PRINCIPLES.md` | on design work | **mixed** | yes |
| `DESIGN.md` | on design work | **dense** | yes — shorter |
| `skills/mimir-bmad/SKILL.md` | on build intent | **mixed** | yes |
| `skills/mimir-bmad/references/huldra.md` | before a build | **mixed** | yes |
| `skills/mimir-bmad/references/install-bmad.md` | on install | **plain** | n/a |
| `brownfield/BROWNFIELD.md` | on brownfield work | **mixed** | yes |
| `studio/STUDIO.md` | on design-room work | **plain** | n/a |
| `studio/freya.md` (persona) | in studio sessions | **mixed** | yes |
| `studio/design-contract.md` | on ratification | **plain** | n/a |
| `agents/the-hand.md` (persona) | per Hand spawn | **plain** | n/a |
| `forge/huldra.js` agent prompts | per build agent | **plain** | n/a (tight by design) |
| `SELF-ITERATION.md` (extra) | on self-iteration | **mixed** | yes |
| `tools/context-packet-spec.md` (extra) | when context high | **dense** | yes — shorter |
| `README.md` (extra, human-facing) | n/a (not agent-read) | **plain** | n/a |

---

## Per-doc evidence

### `output-styles/mimir.md` — the brain — MIXED (highest impact)
Loaded every session; its register most directly primes the agent's output. Largely well-written and skimmable, but carries the system's densest coined shorthand stacked line-on-line. Offending lines:

- L17: *"But it's texture *on* the payload — never theater, never words added for flavor, never at the cost of the point. Same Mimir, dial up a notch; not a second voice."* — "texture on the payload" is an abstract metaphor; the triple "never… never… never…" is anti-instruction phrasing the global CLAUDE.md itself bans.
- L82: *"Everything else layers on top of that baseline, and the footer's **absence** now means one thing only — the reading didn't arrive (a fault) — never 'all clear.'"* — nested dashes + double negation; needs a reread to extract "absence = fault, not all-clear."
- L100: *"The meter reasons fine on its own; never narrate it for its own sake."* — "the meter reasons" personifies a number; reads as insider shorthand.
- L121: *"dispatch a **cartography audit** (a the-Hand job) that returns a durable **MAP**"* — "a the-Hand job" is ungrammatical insider compression.

Plain-ify: shorter. Most fixes collapse the triple-negatives and unpack one metaphor per spot; net removal.

### `~/.claude/mimir/USER.md` — DENSE (every session)
The most jargon-dense always-loaded doc. Each bullet is a comma-spliced run-on packing 3–4 ideas with coined labels. Offending lines:

- L18: *"On always-loaded cores: a stable kernel + mechanisms delivered by their own trigger (hook / on-demand), not parked in the hot path."* — "stable kernel", "hot path" both unpacked-nowhere; telegraphic.
- L19: *"The dumber a stage, the more its output interface must carry."* — abstract to the point of opacity on first read.
- L34: *"Absolute/punchy-past-the-evidence reads as trading credibility for flourish — dial rhetoric down, assumption/tradeoff exposure up."* — slash-compounds ("punchy-past-the-evidence", "assumption/tradeoff exposure") and a metaphor stacked in one line.

Plain-ify: shorter. The lean-instruction rule is already honored on *content*; the loss is *readability*, and unpacking the slash-compounds into short clauses trims characters.

### `/home/tim/.claude/CLAUDE.md` (global) — PLAIN
Numbered sections, bold lead lines, short sentences, concrete examples. The model for what the others should read like. No hotspots.

### `~/.claude/rules/align-before-executing.md` — DENSE (every session)
Two paragraphs, each one enormous sentence. Offending lines:

- L3: a single ~70-word sentence — *"Gate first — wait for your go-ahead — when the work is irreversible or outward-facing (delete, deploy, send/post, force-push, migrate, spend real money, hard-to-undo git ops), even if it's tiny and explicitly asked for; OR large in scope or effort (…); OR underspecified (…)."* — three OR-clauses welded with semicolons; the reader has to hold the whole thing.
- L5: *"An override counts only when I've engaged the stated cost — named the tradeoff back or explicitly accepted it in this conversation; a bare 'just do it' … does not."* — correct but dense; nested dashes inside a long clause.

Plain-ify: shorter or equal. Splitting the OR-list into a short bulleted set removes connective words.

### `~/.claude/rules/verify-before-asserting.md` — DENSE (every session)
The single longest sentences in the rule set. Offending lines:

- L3: an ~80-word opening sentence chaining "does X exist, is Y standard, does this code do Z, a number/date/name/citation from memory, or a version-specific fact…" through to "run the cheap check first." One idea per sentence is violated wholesale.
- L5: *"A fact you just verified does NOT license an adjacent claim that merely sounds connected; one citation's authority must not carry to the next."* — clear-ish but abstract; "license an adjacent claim" and "one citation's authority must not carry" are restated three ways in the paragraph.

Plain-ify: shorter. The link-by-link rule is repeated ~3× in different metaphors; collapsing to one crisp statement removes words.

### `~/.claude/rules/honor-slash-commands.md` — MIXED
One long sentence with a parenthetical pile-up. Offending line:

- L3: *"If it doesn't actually run — Skill errors, didn't fire (landed as plain text), errored partway, or genuinely isn't installed — stop and tell me…"* — the four-way dash-list mid-sentence forces a parse. Otherwise direct.

Plain-ify: equal length, easier read (break the dash-list to a short list).

### `~/.claude/rules/diag-logs.md` — PLAIN
Three sentences, concrete, one idea each. No hotspots.

### `projects/mimir/CLAUDE.md` (project) — MIXED
Mostly clear with good headers, but pockets of stacked coined terms. Offending lines:

- L92–94: *"a recurring finding here is that the framework-agnostic brain *already* does the thing, and the genuinely-new content belongs in an on-demand playbook, not the hot path."* — "the hot path", "does the thing" lean on insider shorthand.
- L66–68 (memory hygiene): *"a soft gauge warns near 20KB/180ln, a hard-stop (`tools/memory-budget-hook.py`) blocks a write that would grow it past the cliff."* — "the cliff", "soft gauge", "hard-stop" are coined but mostly self-evident in context.

Plain-ify: equal/shorter. These are minor; the doc is largely fine.

### `PRINCIPLES.md` — MIXED
Each principle's headline is plain and strong; the `[proven]`/`[field]` provenance tails are dense and citation-packed (but those are a deliberate audit trail, not instruction). One genuine in-instruction hotspot:

- L95–98 (#15 corollary): *"shape tools, schemas, and contracts so the wrong action is structurally hard (poka-yoke); interface-ergonomics failures are systemic failures…"* — "poka-yoke" is an unglossed loanword; "interface-ergonomics failures are systemic failures" is a nominalization stack.

Plain-ify: the headlines need nothing; only the one corollary trims. Mostly leave as-is — the density is in the provenance log, which is reference, not a live instruction.

### `DESIGN.md` — DENSE (on design work)
The longest sustained density in the set — §9/§10 are multi-clause paragraphs of locked decisions. Offending lines:

- L188–197 (§9 delegation): *"the Hand **executes and fetches, never counsels**: Mimir sends the Hand, the Hand brings back the work; it never recommends, decides, or holds an opinion (the instant it takes a verb of judgment, purpose-conflation is back)."* — "a verb of judgment", "purpose-conflation is back" are coined and abstract; the surrounding paragraph runs ~10 lines without a break.
- L21: *"never one notch more friction"* and *"impose ceremony"* — fine as voice, but stacked with "the superset bar (non-negotiable)" reads as jargon density.

Plain-ify: shorter. This is a spec, loaded rarely, so lower priority — but §9 is the densest prose in the repo.

### `skills/mimir-bmad/SKILL.md` — MIXED
Clear structure, but the mode-routing paragraphs pack conditionals. Offending lines:

- L24: *"Interactive *and* heavy → still in-session; manage the budget, never trade the user out of the loop to save context."* — arrow-notation + compressed clause; readable but dense.
- L8 (blockquote): a single ~60-word sentence defining what the brain supplies vs what the skill resolves.

Plain-ify: equal length. Minor.

### `skills/mimir-bmad/references/huldra.md` — MIXED
Operational and mostly clear, but heavy with parentheticals and coined role-names assumed known. Offending lines:

- L15: a ~90-word run-on describing the per-story sequence (planner → builder → reviewers → manifest → commit) in one breath.
- L11: *"Strict floor, scaled policy"* and *"the lead never implements"* — coined but defined nearby.

Plain-ify: shorter (break the L15 run-on into steps). Lower priority (read once, before a build).

### `skills/mimir-bmad/references/install-bmad.md` — PLAIN
Procedural, numbered, concrete commands. No hotspots.

### `brownfield/BROWNFIELD.md` — MIXED
Well-organized; a few dense definitional lines. Offending lines:

- L81 (header): *"The manifest is a forward ledger, not an inventory"* — coined metaphor, but immediately unpacked, so it lands.
- L46–50: the epistemic-spine paragraph stacks "verified-in-code vs claimed-in-docs", "a cold worker will report a doc's claim as built", "#16 input-trust boundary" — three coined terms in one bullet.

Plain-ify: equal length. Minor.

### `studio/STUDIO.md` — PLAIN
Numbered setup steps, plain prose, concrete paths. No hotspots.

### `studio/freya.md` (persona) — MIXED
Strong voice (good — that stays). Density is in the zero-JS medium section, which is necessarily technical. One borderline line:

- L47: a single ~120-word sentence on building out the whole prototype ("Do NOT, on the strength of one approval, declare the design done…"). Long, but it's one cohesive instruction; splitting helps readability without adding words.

Plain-ify: shorter at L47. The voice lines are not targets.

### `studio/design-contract.md` — PLAIN
Format template + short rule list. No hotspots.

### `agents/the-hand.md` (persona) — PLAIN
Short sentences, numbered duties, plain. The persona is deliberately flat (no character) and reads cleanly. No hotspots.

### `forge/huldra.js` agent prompts — PLAIN (don't touch)
Imperative, numbered, CAPS for hard constraints. Dense in places (`TRUST_RULE` is one long sentence) but this is machine-facing build-agent instruction where the density is load-bearing precision, not insider register. Not a priming surface for the conversational agent. Leave as-is.

### `SELF-ITERATION.md` (extra) — MIXED
Clear protocol; pockets of campaign jargon ("false green", "the hot path", "clean flip + no regression"). Mostly fine; loaded only during self-iteration.

### `tools/context-packet-spec.md` (extra) — DENSE
Four long lines, each a single run-on with nested parentheticals and arrow-notation. This *is* read into the brain's status behavior, so its register matters more than its rare-load status suggests. Offending line:

- L3 (`cost:`): *"~K turns × ~avg/turn → ~Z% landing — ONLY for a substantial multi-step plan (…): include it then — the interactive design + ticketing burns context now even if the heavy build later runs off in the forge — but OMIT for a one- or two-step task."* — one ~55-word sentence with three dash-clauses.

Plain-ify: shorter. Each line is one rule wrapped in three caveats; flattening the caveats to a short clause trims it.

### `README.md` (extra) — PLAIN (human-facing, not agent-read)
Deliberately literary (the Mímir myth framing). Reads beautifully; not an instruction surface, so it sets no register for the agent. No action.

---

## Ranked hotspot list (impact × density)

Always-loaded docs weighted heaviest. The top tier is where a rewrite pays the most, because these prime the agent's register on *every* turn.

1. **`USER.md` — whole doc** (every session). Densest always-loaded instruction; slash-compounds and coined kernel/hot-path shorthand throughout. Highest impact-per-fix.
2. **`~/.claude/rules/verify-before-asserting.md` L3, L5** (every session). ~80-word opening sentence; the link-by-link rule restated 3× in different metaphors.
3. **`~/.claude/rules/align-before-executing.md` L3** (every session). ~70-word three-OR-clause sentence; split to a bulleted gate-list.
4. **`output-styles/mimir.md` L82** (every session, top-impact doc). Footer-absence double-negation ("absence means one thing only… never 'all clear'") forces a reread.
5. **`output-styles/mimir.md` L17** (every session). "texture on the payload" metaphor + triple-`never` anti-instruction stack.
6. **`output-styles/mimir.md` L100, L121** (every session). "the meter reasons fine on its own"; "a the-Hand job" ungrammatical compression.
7. **`tools/context-packet-spec.md` L3** (feeds brain status behavior). One ~55-word rule wrapped in three dash-caveats; flatten the caveats.
8. **`projects/mimir/CLAUDE.md` L92–94** (every in-repo session). "the brain already does the thing… not the hot path" — coined shorthand.
9. **`DESIGN.md` §9 L188–197** (design work only). Densest prose in the repo: "a verb of judgment", "purpose-conflation is back", 10-line unbroken paragraph. Lower load-freq → lower rank despite top density.
10. **`skills/mimir-bmad/references/huldra.md` L15** (before a build). ~90-word per-story-sequence run-on; break into steps.

(Honorable mentions, low priority: `freya.md` L47 long sentence; `BROWNFIELD.md` L46–50 triple-coined bullet; `PRINCIPLES.md` #15 "poka-yoke" gloss.)

---

## Plain-language rubric (apply uniformly on rewrite)

Checkable tests. A passage fails if it trips any of these *and* is rewritable at equal-or-shorter length. Voice lines (the marker, the status footer, framing lines, persona character) are exempt — flag only what is hard to *read*, never what has personality.

1. **Sentence length — none over ~25 words.** If a sentence runs longer, it almost always packs >1 idea; split it. (Targets the rules-file and DESIGN run-ons.)
2. **One idea per sentence.** No more than one OR-list, one comma-splice chain, or one nested dash-clause per sentence. Lists become bullets, not semicolons.
3. **Every coined term unpacked on first use — or cut.** "hot path", "the floor", "the read", "kernel", "altitude", "the forge", "poka-yoke", "purpose-conflation": gloss it once in plain words at first appearance, or replace it. If it can't be glossed briefly, it's hiding meaning.
4. **Plain verb over nominalization.** "decide" not "make the decision"; "fails" not "is a systemic failure"; "verify each link" not "link-by-link verification of each claim's authority."
5. **No anti-instruction stacks.** State the positive rule once. Replace "never X, never Y, never Z" triples with the single thing to do (this is already the owner's standing CLAUDE.md rule — apply it to the brain too).
6. **No metaphor where a literal phrase is shorter.** "texture on the payload" → "stays out of the working detail." Keep a metaphor only when it's *terser and clearer* than the literal (the system's own rule: imagery only when terse).
7. **Resolve references inline.** No "the thing", "a the-Hand job", "does the thing" — name what it is. (The owner's standalone-reference discipline.)
8. **Net characters must not grow.** After a rewrite, the passage is equal-or-shorter. "Plain" is a readability fix, never a verbosity license — if it got longer, you over-corrected.
