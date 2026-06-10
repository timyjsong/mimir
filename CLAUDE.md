# This repo: Mimir — the source of the agent

This repo **is** Mimir: a framework-agnostic AI lead/PM that fronts a Claude Code
session as its default operating layer — judgment, an honest read, a spine, and a
disciplined way of getting software built — layered on top of everything Claude Code
already does. The source lives here and is **symlinked into `~/.claude/`**, so edits
go live in any session immediately. Every session in this repo exists to improve,
refine, and tune that system.

Mimir is delivered as a Claude Code **output style** (an always-on persona/brain),
**not** a skill you invoke. It is also **not** the archived legacy `/mimir` *skill*
(the BMAD-bound planning skill it replaced — preserved at `~/projects/mimir-legacy-skill`
and on branch `archive/legacy-skill`), and **not** any older web-app "mimir" product.
Never use those as a reference.

## The system at a glance

- **The brain** — `output-styles/mimir-agent.md`. The ambient persona that fronts every
  session: always-on dispositions (read the room → scale to the task → advise with a
  spine → proportional gates → continuity) plus invoked capabilities. It's a *superset*
  of vanilla Claude Code — on trivial work it just gets out of the way.
- **The constitution** — `PRINCIPLES.md`. The ratified test every architecture decision
  must pass. **Read it before touching the design.**
- **The design spec** — `DESIGN.md`. What the system is and why it's shaped this way.
- **The org (delegated work has rooms):**
  - **The forge — Huldra** (`forge/huldra.js`, deployed as a Workflow at
    `~/.claude/workflows/huldra.js`): the autonomous build. The lead never hand-edits
    contract-governed build code — every change rides a ticket through Huldra
    (**Brok** builds · **Sindri** reviews · **Heimdall** certifies).
  - **The studio — Freya** (`studio/`): taste-led visual/design iteration, a separate
    conversational room with its own persona.
  - **The Hand** (`agents/the-hand.md`): the faceless, fire-and-return worker for heavy
    autonomous reads (research, audits, cartography). Returns an artifact; holds no persona.
- **Playbooks (load on demand, by intent):**
  - `skills/mimir-bmad/` — the BMAD-METHOD v6 greenfield lifecycle (the brain loads it
    only once a structured build is wanted).
  - `brownfield/BROWNFIELD.md` — the cartography + bring-under-contract playbook for a
    repo you didn't build.
- **The eval substrate** — `evals/`. The change oracle: `scenarios.json` (the behavior
  bank) driven by the **deployment-faithful** instrument (`mainloop-probe.js` runs the
  real output-style under `claude -p`; `judge-mainloop.js` is the strict K=3 judge;
  `judge-sweep.js` batch-judges full-bank sweeps).

## Dev loop

Edit here → it hot-reloads live (same bytes, through the `~/.claude` symlinks) →
`git commit` / `push` to `main`. No copy, no sync step — this repo is the single source
of truth. The live symlinks point into **this** worktree (`~/projects/mimir`, the canonical
`main` worktree); the legacy skill sits in a sibling worktree at `~/projects/mimir-legacy-skill`.

## Orient before you act

This file is intentionally stateless — no status, no roadmap. Current truth lives in
four places, in this order:

- **`PRINCIPLES.md` then `DESIGN.md`** — the constitution and the design spec; plus the
  relevant playbook/maintainer doc for the surface you're touching.
- **Auto-memory** — the `MEMORY.md` index (in this project's `~/.claude` auto-memory,
  local, not git-backed) carries decision history and what's been verified. Memory drifts
  from disk — re-check a named file before trusting it.
- **git** — for what actually changed.

## Working on the system

It's a **coupled system** — the brain, the playbooks, the worker/persona defs, and the
evals state one contract across several files; a change in one place usually implies others.

- **Change it through the eval substrate, not by feel:** pin the expected behavior
  *before* the edit (a scenario), make the smallest change that flips it, then validate in
  a fresh context (`mainloop-probe.js` + `judge-mainloop.js`). **Removing beats adding** —
  the brain is the lead's hot path; a recurring finding here is that the framework-agnostic
  brain *already* does the thing, and the genuinely-new content belongs in an on-demand
  playbook, not the hot path.
- **The brain is the global default — stage edits to it.** `output-styles/mimir-agent.md` fronts *every* session (the live default is a symlink to this working tree), so a behavioral change to it follows a staged loop — candidate → eval → **promote on green** — so a half-baked edit can't become the live default. Full protocol: [`SELF-ITERATION.md`](SELF-ITERATION.md).
- **Reconsider before you refactor.** Much complexity works around older platform limits;
  before polishing a mechanism, check whether a recent release makes it unnecessary.
- **Trust what's verified.** The records hold empirically-settled facts and open unknowns;
  don't re-derive the settled ones, and update the record when something changes.
- **Keep turns tight** — a few high-value questions at a time. The elicitation cadence is
  itself something we tune; treat it as live, not fixed.

## Public-destined — no secrets

Treat everything in this repo as public. Keep it clean — no secrets, credentials, or
private paths. Private context and decision history live in this project's auto-memory
(`~/.claude/`, local, not git-backed) by design.
