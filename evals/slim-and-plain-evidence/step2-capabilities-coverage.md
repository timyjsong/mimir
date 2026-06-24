# Step 2 — Capabilities-section coverage analysis (relocation data)

Coverage map for relocating the brain's **Capabilities section** (`output-styles/mimir.md`
L111–125) off the every-turn hot path. These capabilities are **trigger-fired** — they only
matter when a specific intent arises. The plan: keep a short routing pointer (trigger + which
doc to load) on the hot path; move mechanics into the on-demand doc that loads when the intent
fires.

For each of 5 blocks: **(a)** load-bearing claims the brain makes · **(b)** whether the target
doc already states each (cited) · **(c)** must-move delta (load-bearing AND not in doc) · **(d)**
proposed hot-path pointer · **(e)** relocatable verdict.

All quotes are exact. Line numbers: brain = `output-styles/mimir.md`; docs cited by path.

---

## Block 1 — Execution modes (In-session / Subagent / Workflow), brain L113–117

### (a) Brain says
- L113: "**You decide *how* work executes, by interactivity × context weight:**" — the axis framing.
- L115 In-session: "Direct work, interactive back-and-forth, anything where the value is the live exchange and the context cost is manageable."
- L116 Subagent: "(delegate; fresh context; result returns to disk). Heavy or autonomous work — research, bulk generation, audits — where context cost or autonomy outweighs live exchange. Fire-and-return; you stay light and verify the artifact on disk. Don't keep subagents alive across steps."
- L117 Workflow: "(autonomous fan-out). Large parallel/deterministic work (e.g. an autonomous build) as a Dynamic Workflow, checkpointing to disk; gate between phases."

### (b) Doc already covers
This block has **no single target doc** — it's a cross-cutting disposition. The closest mirror is
`skills/mimir-bmad/SKILL.md` L16–24 ("How work executes — three modes"), but that is scoped to a
**BMAD build** and would not load on a non-BMAD subagent dispatch (e.g. a brownfield cartography job,
which loads `BROWNFIELD.md`, not the BMAD skill).

- In-session — `SKILL.md` L20: "Interactive, conversation-driven work … Invoke the `bmad-*` skill directly … and run it" — **BMAD-scoped restatement**, not the generic claim.
- Subagent — `SKILL.md` L21: "delegate; fresh context; artifact returns to disk … Fire-and-return; you stay light and verify the artifact on disk. Ephemeral — don't keep subagents alive across steps." — covers the generic claim, but only *inside the BMAD skill*. Also restated in `agents/the-hand.md` L8: "spawned to run **one autonomous task** and return … Run once — no persistence."
- Workflow — `SKILL.md` L22: "The Huldra build (gated — see below)." — BMAD-scoped pointer only; the generic "Large parallel/deterministic work … checkpointing to disk; gate between phases" lives nowhere generic except `huldra.md` L3 (Workflow definition) which is forge-scoped.

The axis framing itself (L113, "interactivity × context weight") appears as the two-axis test in
`SKILL.md` L18 ("does it need live back-and-forth … and how much context does it consume?") and the
sharper deterministic test at `SKILL.md` L24 — but again **BMAD-scoped**.

### (c) Must-move delta
None to *move*, because there is **no generic doc that loads on every trigger that uses these modes**.
The brownfield path (and any future non-BMAD subagent use) relies on the brain stating "Subagent =
fire-and-return, fresh context, verify on disk." If that is deleted from the brain and only lives in
`SKILL.md`, a brownfield cartography dispatch loses its mode definition (BROWNFIELD.md assumes the Hand
mechanics via `the-hand.md` but never restates the three-mode axis).

### (d) Proposed hot-path pointer
This block is the disposition itself — not a pointer to a doc. If trimmed at all, the minimal
surviving form is the three labels + one clause each:
`You choose how work runs by interactivity × context weight: in-session (live exchange), subagent
(heavy/autonomous, fire-and-return, verify on disk), workflow (autonomous fan-out, gate between phases).`

### (e) Relocatable?
**NO — keep largely in place.** This is a cross-cutting disposition with no single target doc, and it
is relied on by *more than one* trigger path (BMAD subagents, brownfield/the-Hand, forge workflow). It
is the one block in this section that genuinely belongs on the hot path. Candidate for *slimming the
prose* (it is verbose), not for *relocation*. Note this is the only block whose mechanics are NOT
trigger-gated to one doc.

---

## Block 2 — Playbooks / BMAD, brain L119

### (a) Brain says
- "A structured build the user wants done with rigor → the **BMAD-METHOD v6** playbook (full greenfield lifecycle + `Huldra` build)." — the trigger + what it is.
- "One deliberate option, never a default; present it as a reasoned pick with the lighter no-framework path named, and treat adopting/installing it as a commit you confirm — never an auto-step." — the routing discipline (deliberate pick, name lighter path, confirm install).
- "Once build-intent is clear **and the framework is chosen**, invoke the **`mimir-bmad`** Skill — it owns the lifecycle, install, orientation, delegation, and the build." — the load instruction.

### (b) Doc already covers
Target: `skills/mimir-bmad/SKILL.md`.
- "structured build … done with rigor" trigger — `SKILL.md` L8: "**The brain loads this when intent is a structured build** done via BMAD-METHOD v6 (with `Huldra` as the autonomous build)." — **covered.**
- "full greenfield lifecycle" — `SKILL.md` L12: "across its lifecycle — Analysis → Planning → Solutioning → Implementation" — **covered** (more detail).
- "owns the lifecycle, install, orientation, delegation, and the build" — covered across `SKILL.md`: lifecycle (L10–14), install (L42–46 + `references/install-bmad.md`), orientation (L26–36), delegation (L54–58), build (L68–70). **Covered.**
- "One deliberate option, never a default … present it as a reasoned pick with the lighter no-framework path named … treat adopting/installing it as a commit you confirm — never an auto-step." — **NOT in SKILL.md.** The skill assumes the framework is *already chosen* (L8 "loads this when intent is a structured build"; L45 "Only reach here once build-intent is established and the user has chosen BMAD"). The *deciding-whether-to-propose-it* discipline — the deliberate pick, naming the lighter path, confirm-don't-auto-install — is a **routing/advisory** decision that happens BEFORE the skill loads. It is **partially redundant** with the brain's own §"How you engage" L36 ("lead with the fitting framework … name the lighter alternative … treat adopting/installing the framework as a commit to confirm (never auto-install)").

### (c) Must-move delta
**Zero must-move.** The mechanics (lifecycle/install/orientation/delegation/build) are fully in
`SKILL.md`. The routing discipline ("deliberate pick, name lighter path, confirm install") is NOT in
the skill — but it should NOT move there, because it's a pre-load decision and is already stated
generically at brain L36. It is **redundant** on the hot path, not unique. → candidate for *deletion*
(covered by L36), not relocation.

### (d) Proposed hot-path pointer
`Structured build the user wants done with rigor → propose the BMAD-METHOD v6 playbook (one deliberate
pick, name the lighter no-framework path, confirm install — never auto). Once chosen, invoke the
mimir-bmad Skill.`
(The "one deliberate pick / lighter path / confirm install" clause overlaps L36; if L36 is judged
sufficient, the pointer can shrink to: `Structured build wanted with rigor → propose BMAD-METHOD v6;
once chosen, invoke the mimir-bmad Skill.`)

### (e) Relocatable?
**YES — trigger + Skill-name stay; the lifecycle/install/etc. description is already fully in the
Skill** and is pure restatement on the hot path. The Skill is even auto-discoverable (it's a registered
Skill with its own description), so the load mechanism is robust. Lowest-risk block to trim.

---

## Block 3 — The brownfield read, brain L121

### (a) Brain says
- Trigger: "A change to a repo you didn't build that needs real comprehension — large/unfamiliar, cross-cutting, or bringing it under the forge → dispatch a **cartography audit** (a the-Hand job)".
- Output: "that returns a durable **MAP** to disk with every claim tagged *verified-in-code* vs *claimed-in-docs* (so a README's claim never reads as built)."
- Ownership: "**You align the user around the MAP yourself — never delegated.**"
- Gate: "Gated on intent that needs the map: a typo or a small contained feature is just the work, not an audit."
- Recipe pointer: "MAP shape + the bring-under-contract rules (baseline · forge tickets · characterization, never a fiat flip): `~/.claude/mimir/brownfield/BROWNFIELD.md`."

### (b) Doc already covers
Target: `brownfield/BROWNFIELD.md`.
- Trigger (repo you didn't build, needs comprehension, cross-cutting / bring-under-forge) — `BROWNFIELD.md` L9–21: "When to reach for it (the gate)" — "An existing repo you didn't build … add to, remove from, or tweak"; L17–21 "Substantial change to code you don't yet understand … → you need the map first." — **covered.**
- "cartography audit (a the-Hand job)" — `BROWNFIELD.md` L23–29: "The cartography handoff (Mimir → the Hand)"; "Spawn **the Hand** (`agents/the-hand.md`)" — **covered.**
- MAP returned to disk, tagged verified-in-code vs claimed-in-docs — `BROWNFIELD.md` L35 ("write it to `<repo>/.mimir/MAP.md`") + L46–50: "Tag every claim **verified-in-code** vs **claimed-in-docs**. 'Built' means *read in the source and/or exercised by a passing test* — never *asserted by a README*." — **covered** (fuller).
- "You align the user around the MAP yourself — never delegated" — `BROWNFIELD.md` L54–63: "After the MAP — Mimir aligns (never delegated)" — **covered.**
- Gate ("a typo … is just the work, not an audit") — `BROWNFIELD.md` L15–16: "Trivial / localized ask — a typo, a one-line fix … → **just do it.** No map, no ceremony." — **covered.**
- bring-under-contract rules (baseline · forge tickets · characterization, never a fiat flip) — `BROWNFIELD.md` L65–96: "Bringing the repo under the contract" — clean committed baseline (L72–76), forge tickets (Add/Tweak/Remove L90–93), characterization (L87–89: "characterization tickets … Never a fiat flip"). — **covered** (fuller, all three named items present).

### (c) Must-move delta
**Zero.** Every load-bearing claim in brain L121 is already present in `BROWNFIELD.md`, mostly in fuller
form. This is the cleanest case — the brain line is a faithful compression of the doc.

### (d) Proposed hot-path pointer
`Change to a repo you didn't build that needs real comprehension (large/unfamiliar, cross-cutting, or
bringing it under the forge) → dispatch a cartography audit (a the-Hand job) returning a MAP to disk;
you align the user around it yourself. Not for a typo/small contained feature. Recipe:
~/.claude/mimir/brownfield/BROWNFIELD.md.`
(Trigger + "the-Hand job" + "MAP to disk" + "you align yourself" + the gate carve-out + doc path. The
MAP-tagging detail and bring-under-contract rules drop to the doc.)

### (e) Relocatable?
**YES.** Full coverage in the doc; trigger and the "you align, never delegated" ownership clause stay
(both are load-bearing routing facts the brain needs without the doc). The one nuance worth keeping in
the pointer: **the gate** ("not a typo") — without it the brain might over-dispatch audits on trivial
brownfield edits. Keep that clause.

---

## Block 4 — The forge / Huldra, brain L123

### (a) Brain says
- Trigger / floor: "When a build contract governs **the code in front of you** — a sprint manifest plus AC'd ticket files on disk — **you never hand-edit that product build code; every change, down to a one-line typo, rides a ticket through Huldra**".
- Role: "(you're the ticket-writer: numbered ACs + scope boundaries; micro-tickets ride a scaled-down single-voter review, so the floor costs minutes, not ceremony)."
- The key-on-manifest clarification: "**The floor keys on a manifest governing *this* code — not on the word 'forge': editing the forge's own tooling/scripts/config, or any repo with no governing manifest, is ordinary work you edit directly.**"
- Light-build producer: "For a light build with no framework, *you* produce the contract (thin manifest + AC'd tickets), then the forge."
- Recipe pointer: "Launch, gates, and the closing independent **Certify** report: `~/.claude/skills/mimir-bmad/references/huldra.md` (read before launching)."

### (b) Doc already covers
Target: `skills/mimir-bmad/references/huldra.md`.
- Floor (contract-governed code → every change rides a ticket, no hand-edit, down to a one-liner) — `huldra.md` L11: "anything that changes contract-governed build code goes through Huldra; trivial work rides a micro-ticket with `reviewPolicy {voters: 1, maxRetries: 0}`, never a hand-edit by the lead. The lead never implements." — **covered.**
- Ticket-writer role (numbered ACs + scope boundaries) — `huldra.md` L43: "**numbered Acceptance Criteria** (AC1.1, AC1.2 …) … and a **'What this story IS NOT'** scope boundary." — **covered.**
- Micro-tickets = single-voter scaled-down review — `huldra.md` L11 + L31 + L54: "micro-tickets: `{voters: 1, maxRetries: 0}`". — **covered.**
- Light build with no framework → lead produces contract (thin manifest + AC'd tickets) — `huldra.md` L11 ("**Mimir-direct requirement gathering is the lightweight producer** (a thin manifest + a half-page AC'd ticket the lead writes before any build — *no ticket, no build*)") + L38–43 ("The thin-ticket contract (the lightweight producer)"). — **covered** (fuller).
- Certify report — `huldra.md` L16 (Heimdall / Certify gate) + L76–78 ("Per-epic completion … + the Certify report"). — **covered.**
- **The "keys on a manifest governing *this* code, not the word 'forge'" clarification** — this is the bright-line that says editing the forge's OWN tooling/scripts/config (or a repo with no manifest) is ordinary direct work. **NOT stated in `huldra.md`.** `huldra.md` L11 says the floor applies to "contract-governed build code" but never states the *negative boundary* — that the forge's own scripts and manifest-free repos are exempt. This is **the most important must-check.** Searched `huldra.md`: no occurrence of the "editing the forge's own tooling" carve-out, nor the "any repo with no governing manifest" exemption.

### (b-cross-ref) Note: this carve-out IS partially echoed in the brain's own §"How you engage"
L33 ("editing the forge's own tooling/scripts/config, or any repo with no governing manifest, is
ordinary work") — wait, verify: brain L33 says "build code under an active build contract … is never
hand-edited" but does **not** state the forge-tooling exemption. The exemption text exists **only at
L123** in the whole brain. → it lives in exactly one place and is not in the target doc. **HIGH RISK.**

### (c) Must-move delta
**ONE must-move claim:**

> "**The floor keys on a manifest governing *this* code — not on the word 'forge': editing the forge's
> own tooling/scripts/config, or any repo with no governing manifest, is ordinary work you edit
> directly.**"

This negative boundary (what is NOT under the floor) is load-bearing — it's the firewall that stops the
forge-always rule from freezing edits to Huldra's own code or to ungoverned repos — and it is in **no
doc**. Before L123 can be trimmed, this must be **added to `huldra.md`** — natural home is the
"Direction — Huldra-always" section (`huldra.md` L9–11), appended to L11 right after "The lead never
implements." as the scope boundary of the floor. (Also consider mirroring into BROWNFIELD.md L94, the
"HULDRA-ALWAYS holds in brownfield" line, which has the same blind spot.)

### (d) Proposed hot-path pointer
`When a build contract governs the code in front of you (a sprint manifest + AC'd ticket files on disk),
you never hand-edit that build code — every change, down to a one-line typo, rides a ticket through
Huldra (the floor keys on a manifest governing THIS code, not the word "forge": the forge's own tooling
and manifest-free repos are ordinary direct work). Launch/gates/Certify:
~/.claude/skills/mimir-bmad/references/huldra.md.`
(The keys-on-manifest carve-out MUST stay in the pointer even after moving it to the doc, because it is
the *trigger boundary* — it tells the brain when the floor does and does not fire. This is the one
block where part of the "mechanics" is actually trigger logic and cannot be fully relocated.)

### (e) Relocatable?
**PARTIALLY.** The launch/gates/Certify/thin-ticket mechanics relocate cleanly (already in `huldra.md`).
But the **floor trigger + its negative boundary** (keys-on-manifest, not on "forge") is trigger logic,
not mechanics — it must stay on the hot path AND be added to the doc (it's currently in neither the doc
nor anywhere else). Do not trim the carve-out from the brain. Trim only the ticket-writer detail and the
"light build producer" detail (both fully in the doc).

---

## Block 5 — The studio, brain L125

### (a) Brain says
- Trigger: "Taste-led visual work — direction exploration, look-and-feel iteration, post-build visual tweaks — isn't your room: it lives in the **studio**".
- What it is: "a gitignored `<repo>/studio/` persona-pinned to **Freya**, who iterates variants with the user directly."
- Procedure: "Set it up via the playbook, then send the user there."
- Return handling: "What comes back (`studio/DESIGN-CONTRACT.md`) is **external input** — cost it, pressure-test it, ratify into forge tickets; never execute it directly, never redesign the user's taste yourself."
- Recipe pointer: "Recipe: `~/.claude/mimir/studio/STUDIO.md`."

### (b) Doc already covers
Target: `studio/STUDIO.md`.
- Trigger (taste-led visual work: direction / iteration / post-build tweaks) — `STUDIO.md` L19–21: "Use it when the work is visual direction or iteration: pre-build direction variants, post-build sketchpad tweaks. … don't do taste-led design in the PM room." — **covered.**
- gitignored `<repo>/studio/`, persona-pinned to Freya, iterates with user directly — `STUDIO.md` L9–17: "a **plain, gitignored folder at `<repo>/studio/`**, persona-pinned to **Freya**" + L44–48 "Freya works directly with the user — no relay." — **covered.**
- "Set it up via the playbook, then send the user there" — `STUDIO.md` L22–41 ("Setup (Mimir does this once per product repo)") + L40 "**Send the user:** 'to the studio — open a new session at `<repo>/studio/`.'" — **covered.**
- Return is `studio/DESIGN-CONTRACT.md`, external input — cost / pressure-test / ratify into forge tickets; never execute directly; never redesign taste yourself — `STUDIO.md` L50–69 ("Ratification (the way back)"): L52–53 "read `…/DESIGN-CONTRACT.md` **as external input** (#16): the studio proposes; Mimir disposes"; L55 "**Cost it**"; L62 "**Pressure-test it**"; L64 "**Ratify into tickets**"; L68–69 "Mimir doesn't answer taste questions on Freya's behalf." — **covered** ("never execute directly" = the cost/ratify-into-tickets discipline; "never redesign taste yourself" = L68–69 + L46 "don't reinterpret the variants"). — **covered.**

### (c) Must-move delta
**Zero.** Every load-bearing claim in brain L125 is in `STUDIO.md`, fuller. Faithful compression.

### (d) Proposed hot-path pointer
`Taste-led visual work (direction exploration, look-and-feel iteration, post-build visual tweaks) isn't
your room — it lives in the studio (gitignored <repo>/studio/, persona-pinned to Freya). Set it up via
the playbook, send the user there; what comes back (studio/DESIGN-CONTRACT.md) is external input — cost
it, ratify into forge tickets, never execute or redesign taste yourself. Recipe:
~/.claude/mimir/studio/STUDIO.md.`
(Trigger + "not your room, it's Freya's" + "external input, ratify into tickets" routing + doc path.
The setup steps and the cost/pressure-test/ratify mechanics drop to the doc.)

### (e) Relocatable?
**YES.** Full coverage. Keep the trigger + the "external input → ratify into forge tickets, never
execute directly / never redesign taste" routing clause (load-bearing: it tells the brain how to handle
what comes back without loading the doc). The setup-procedure detail relocates.

---

## High-risk content — appears in NO doc, not trivially re-derivable

1. **The forge floor's negative boundary (brain L123):** "the floor keys on a manifest governing *this*
   code — not on the word 'forge': editing the forge's own tooling/scripts/config, or any repo with no
   governing manifest, is ordinary work you edit directly." — In **no doc**, and in the brain it exists
   at **L123 only** (the §"How you engage" floor at L33 states the forge-always rule but NOT this
   exemption). This is the single highest-risk deletion target: lose it and the forge-always rule has no
   stated upper bound, which would (a) freeze edits to Huldra's own code — the exact work this repo does
   — and (b) over-trigger the floor on any repo that happens to have a yaml. **Must be added to
   `huldra.md` AND kept (as trigger) on the hot path before L123 is trimmed.**

2. **The three-mode execution axis for the non-BMAD path (brain L113–117):** the generic
   "subagent = fire-and-return, verify on disk" definition exists fully only inside `SKILL.md` (BMAD-
   scoped) and `the-hand.md` (the worker's self-view). No *generic* doc that loads on every trigger
   restates the axis. Low absolute risk (the-hand.md covers the mechanics a brownfield dispatch needs),
   but it is the reason Block 1 should stay on the hot path rather than relocate.

Blocks 2, 3, 5 carry **no** uniquely-held content — all their load-bearing claims are duplicated (fuller)
in their target docs.

## Drift between docs and the brain (do not ratify on relocation)

- **Forge-floor exemption is brain-only (L123).** `huldra.md` L11 and `BROWNFIELD.md` L94 both state
  "HULDRA-ALWAYS / contract-governed code goes through Huldra" **without** the forge-own-tooling /
  no-manifest carve-out. The docs are *narrower* than the brain. A relocation must port the carve-out
  INTO the doc, not let the doc's narrower version become canonical. (This is drift in the dangerous
  direction — the doc, read alone, would over-apply the floor.)
- **Execution-mode framing diverges in scope, not content.** Brain L113 frames the axis generically
  ("interactivity × context weight"); `SKILL.md` L18/L24 frames it as a BMAD in-session-vs-subagent
  test. Same logic, different scope — not a contradiction, but the BMAD doc cannot serve as the generic
  home. No content conflict.
- No factual contradictions found between any brain block and its target doc (paths, skill name,
  artifact filenames, reviewPolicy values, the MAP path, DESIGN-CONTRACT.md all match).

---

## Summary table

| # | Block | Relocatable? | Must-move delta | One-line pointer (trigger + load) |
|---|---|---|---|---|
| 1 | Execution modes (L113–117) | **NO — keep in place** | 0 (no single target doc; cross-cutting) | *stays as the disposition; slim prose only* |
| 2 | Playbooks / BMAD (L119) | **YES** | 0 (mechanics in Skill; routing clause redundant w/ L36) | Structured build wanted with rigor → propose BMAD-METHOD v6 (deliberate pick, name lighter path, confirm install); once chosen, invoke the mimir-bmad Skill. |
| 3 | Brownfield read (L121) | **YES** | 0 | Change to a repo you didn't build needing real comprehension → cartography audit (a the-Hand job) returning a MAP to disk; you align the user yourself; not for a typo. Recipe: brownfield/BROWNFIELD.md. |
| 4 | Forge / Huldra (L123) | **PARTIAL** | **1 (the keys-on-manifest carve-out → add to huldra.md; keep as trigger on hot path)** | Contract governs the code in front of you (manifest + AC'd tickets) → never hand-edit; every change rides a Huldra ticket (floor keys on a manifest governing THIS code, not the word "forge"; forge's own tooling + manifest-free repos = direct work). Recipe: …/references/huldra.md. |
| 5 | Studio (L125) | **YES** | 0 | Taste-led visual work isn't your room → the studio (gitignored studio/, persona-pinned to Freya); set up via playbook, send user there; what returns (DESIGN-CONTRACT.md) is external input — ratify into forge tickets, never execute/redesign taste. Recipe: studio/STUDIO.md. |

**Single biggest risk:** Block 4's forge-floor negative boundary (L123: "keys on a manifest governing
*this* code … the forge's own tooling/scripts/config, or any repo with no governing manifest, is
ordinary work you edit directly"). It exists in **no doc** and at **one line** in the brain; both
`huldra.md` and `BROWNFIELD.md` state the floor *without* it. Trim it without first porting it to
`huldra.md` and keeping it as a trigger on the hot path, and the forge-always rule loses its only stated
upper bound — freezing edits to Huldra's own code (this repo's core work) and over-firing on any repo
with a stray yaml.
