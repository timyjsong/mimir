# Mimir

**An opinionated AI engineering lead that fronts your [Claude Code](https://www.claude.com/product/claude-code) sessions — and a case study in building a reliable LLM agent through *evaluation*, not vibes.**

Most AI coding assistants are order-takers: you ask, they do. Mimir is built to behave
like a senior engineering lead instead — it reads what you're actually trying to do,
recommends an approach (and tells you when your premise is wrong), holds its ground under
pushback on things it can verify, defers on the calls that are genuinely yours, and is
disciplined about *how* code gets built. On trivial work it gets out of the way entirely;
it's a strict **superset** of the default assistant, never more friction on a one-liner.

It's delivered as a Claude Code **output style** (an always-on persona layer) plus a small
org of specialized workers. This repository is the full source — and, deliberately, the
full engineering record of how it was built and tuned.

---

## What it does

- **Reads the room, then scales to the task.** A typo gets fixed; a real build gets real
  rigor. The visible footprint scales to what the work warrants — judgment is always on,
  but it only *speaks up* when there's a decision to make.
- **Advises with a spine.** It makes a call and gives the one or two reasons that matter.
  Under pushback it reconsiders honestly, then **holds** on what it can verify (a fact, a
  sequence, how the code actually works) and **defers** on what lives in your domain
  (product, taste, market) — caving only to a genuine counter-argument or an informed
  override, never to repetition.
- **Never hand-builds under a contract.** When a real build is underway, Mimir is the lead,
  not the bricklayer: every change — down to a one-line fix — rides a ticket with numbered
  acceptance criteria through an autonomous build forge with independent review.

## Architecture — a small org with separate rooms

Mimir delegates by *interactivity × context weight*. Heavy or autonomous work leaves the
lead's context and goes to a purpose-built room:

| Role | Who | What it owns |
|---|---|---|
| **The lead** | Mimir | judgment, the read, the spine, alignment with the user |
| **The forge** | **Huldra** (a Dynamic Workflow) | the autonomous build: **Brok** builds each story → **Sindri** reviews it adversarially against the ACs → **Heimdall** certifies the whole suite independently |
| **The studio** | **Freya** | taste-led visual/design iteration, in a separate conversational room |
| **The Hand** | *(faceless)* | one-shot autonomous reads — research, audits, codebase cartography — returns an artifact, holds no opinions |

On-demand **playbooks** load only when intent calls for them: the full BMAD-METHOD v6
greenfield lifecycle, or a **brownfield** playbook for understanding and safely extending a
codebase Mimir didn't build.

## How it's built — eval-driven, not vibe-driven

The interesting part isn't the persona; it's the **discipline used to make it reliable.**
Prompt changes here are treated like code changes to a system under test:

- **A behavior bank as the oracle.** [`evals/scenarios.json`](evals/scenarios.json) pins the
  expected behavior for dozens of situations (intent triage, the spine, proportional gates,
  brownfield routing, …).
- **Deployment-faithful measurement.** Scenarios run through the *real* output style on the
  *real* main agent loop (`claude -p`), not a role-played proxy — so the eval measures what
  ships. ([`evals/mainloop-probe.js`](evals/mainloop-probe.js))
- **Adversarial, multi-judge scoring.** Each run is graded by a strict **K=3 majority** of
  independent judges against explicit *expect* / *must-not* criteria, at N≈30 per scenario —
  enough to catch single-judge variance. ([`evals/judge-mainloop.js`](evals/judge-mainloop.js))
- **A change protocol.** Pin the new behavior as a scenario *before* the edit → make the
  smallest change that flips it → validate in a fresh context. **Removing beats adding:** the
  brain is the lead's hot path, so the bar to put a line there is high.
- **A constitution.** Every architecture decision must pass [`PRINCIPLES.md`](PRINCIPLES.md) —
  a ratified set of principles, each earned by a real observed failure or corroborated by
  published practice.

> **A representative result.** The brownfield capability was added by first writing four
> scenarios and baselining them against the *unedited* brain — which already passed all four.
> The eval proved the general dispositions had already generalized, so the change shipped as a
> one-line capability *pointer* plus an on-demand playbook, not a rewrite of the hot path. The
> same pass was then validated live by running the codebase-mapper against two real
> repositories and confirming it tagged every claim *verified-in-code* vs *claimed-in-docs* —
> refusing to report a docs-only plan as "built." (See [`DESIGN.md`](DESIGN.md) §10.)

## Repo map

| Path | What's there |
|---|---|
| [`output-styles/mimir-agent.md`](output-styles/mimir-agent.md) | **the brain** — the always-on persona spec |
| [`PRINCIPLES.md`](PRINCIPLES.md) | the constitution every decision must pass |
| [`DESIGN.md`](DESIGN.md) | the design blueprint + decision rationale |
| [`forge/huldra.js`](forge/huldra.js) | the autonomous build workflow (build → adversarial review → certify) |
| [`skills/mimir-bmad/`](skills/mimir-bmad) · [`brownfield/`](brownfield) | on-demand playbooks |
| [`studio/`](studio) · [`agents/`](agents) | the design room (Freya) and the faceless worker (the Hand) |
| [`evals/`](evals) | the behavior bank + the deployment-faithful test harness |

## Status & framing

A personal R&D project — single-user, built and tuned in the open as an exploration of how
to give an AI agent durable judgment and make that judgment *measurable*. It runs on a Claude
Code subscription in an interactive session; the autonomous build forge has been exercised
end-to-end on real multi-epic builds. The naming is [Norse](https://en.wikipedia.org/wiki/Mímir) —
Mimir is the keeper of wisdom; Huldra, Brok, Sindri, Heimdall, and Freya each keep their own lane.
