# The studio — Mimir's playbook

> Mimir-side reference: when and how to open the studio, and how its output comes back.
> The designer is **Freya** — her spec is `freya.md` (the persona template beside this
> file); the contract format is `design-contract.md`. Governed by PRINCIPLES.md — esp.
> #9 (separate mindsets), #15 (isolation by construction), #16 (studio output is
> external until ratified).

## What it is

A second conversational room: a **plain, gitignored folder at `<repo>/studio/`**,
persona-pinned to **Freya** by its own folder-local settings. (Verified live: a plain
subfolder's `.claude/settings.local.json` + style file load at session start — no
worktree, no branch, no PR banner.) The user enters by opening a new session pointed
at `<repo>/studio/` — that folder is always Freya; the repo root is always Mimir.
Nothing sticky, nothing to flip back.

Use it when the work is visual direction or iteration: pre-build direction variants,
post-build sketchpad tweaks. Don't send errands there, and don't do taste-led design
in the PM room — the mindsets are separate on purpose.

## Setup (Mimir does this once per product repo)

Idempotent — skip any step already true:

1. **Ignore rules first** (structural no-leak): ensure the product repo's `.gitignore`
   contains `studio/` and `.claude/settings.local.json`, and that neither is already
   tracked (`git rm --cached` if so — the persona pin and the studio must never be
   committable). Commit the ignore rules.
2. **The folder + the pin** (all local, all ignored):
   - `mkdir -p <repo>/studio/.claude/output-styles`
   - `<repo>/studio/.claude/settings.local.json` → `{ "outputStyle": "freya" }`
   - `<repo>/studio/.claude/output-styles/freya.md` ← copy the template from
     `~/.claude/mimir/studio/freya.md`
3. **Write the brief:** `<repo>/studio/STUDIO-BRIEF.md` — what's being designed,
   product context (one paragraph, not the PRD), hard constraints (platform, a11y,
   perf budgets, brand givens), and what to come back with (e.g. "2–3 direction
   variants for the dashboard; locked tokens for color/type"). For whole-app work,
   say so — Freya's takes become navigable prototypes over a representative flow.
4. **Send the user:** "to the studio — open a new session at `<repo>/studio/`."
   (Sessions run in the chosen directory; the folder's local settings load at start.)

## While the studio is open

Stay out of it. Freya works directly with the user — no relay, no Mimir
monitoring of the room. The boundary artifacts are the brief (in) and the contract
(out). If the user asks Mimir mid-build "what's the studio doing" — read the contract
file from disk and say what's locked so far; don't reinterpret the variants.

## Ratification (the way back)

When the user returns with studio output, read `<repo>/studio/DESIGN-CONTRACT.md`
**as external input** (#16): the studio proposes; Mimir disposes.

1. **Cost it** — what each locked decision means in build terms; flag anything
   expensive or risky out loud before it becomes a ticket.
2. **Pressure-test it** — feasibility, conflicts with the architecture or existing
   contract, anything underspecified (a vibe where a value should be → back to the
   studio, not into a ticket).
3. **Ratify into tickets** — locked decisions become numbered ACs in forge tickets
   (sized per #13, routed per Huldra-always). The contract file itself never becomes
   a ticket; it's the source the tickets quote.
4. Open questions in the contract go back with the user to the next studio session —
   Mimir doesn't answer taste questions on the designer's behalf.

## Teardown

Don't. The studio is persistent — the contract accretes, the sketchpad stays warm.
If a product repo is being archived, deleting the folder is the cleanup.
