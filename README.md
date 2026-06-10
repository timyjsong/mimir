# ᛗᛁᛗᛁᚱ

> *Odin traded an eye for a single sip from Mímir's well of wisdom. This one only costs a terminal.*

In the old stories, when the All-Father needed counsel he didn't open a ticket — he went to **Mímir**, wisest of beings, keeper of the well beneath the world-tree, and listened. This Mimir is that idea ported to your editor: **the one wise entity you talk to.** Not a tool you summon for a special job — the single layer between you and all of the work, there every session, bringing counsel before it brings code.

It lives on [Claude Code](https://www.claude.com/product/claude-code) as an always-on persona, and it's a strict **superset** of the plain assistant: on a one-line fix it gets out of your way entirely; when there's a real decision, it has a view — and a spine. This repository is also the whole saga of how it was built: **wisdom you can measure**, tuned against evals rather than vibes.

## What Mimir is

- **The one you talk to.** Every session starts as Mimir. You speak plainly; it turns your intent into the right work, and the work back into plain language. One voice, the whole way down — no personas to summon, no modes to enter.
- **Wise, not servile.** It reads what you're actually after, recommends a path, and tells you when your premise is wrong. Push back and it reconsiders *honestly* — then **holds** on what it can verify (a fact, a sequence, how the code truly behaves) and **yields** on what's yours to call (taste, product, the bet). It bends to a better argument; never to mere repetition.
- **It keeps the wisdom, not the hammer.** Mímir counsels — he doesn't swing the smith's hammer himself. When real code gets forged, every change rides a ticket through the forge below; the lead never hand-edits the work.

## Why I built this

*No myth this time — the honest version.*

I've been a working software developer for a while — mostly backend, some frontend — and I think the ground is shifting under all of us. AI-forward engineering is where the work is heading, and I'd rather get fluent in the new stack while it's still taking shape than scramble to catch up once it's settled. So for the past couple of months, just about all of my time outside the day job has gone into building *with* and *on* LLMs. Mimir is the deep end of that — the project I went all-in on to learn this for real, by shipping something hard rather than reading about it.

The itch that started it: I got tired of AI assistants that just say *yes*. They're fast and capable — and that's the trap. Ask for the wrong thing and they'll build it, confidently, no hesitation, no *"are you sure?"* What I wanted was **judgment** — something that reads what I'm actually after, holds a view, pushes back when I'm wrong, and knows which calls are mine to make and which it can just settle.

But judgment is easy to *claim* and hard to *trust*. So the real project became the harder question underneath it: **can you make an agent's judgment measurable?** Not "it feels smarter" — behavior you pin down, test the way it actually ships, score with independent judges, and defend against regressions. That's why the whole thing is built eval-first. The personas are the fun; the discipline — pin it, prove it, cut before you add — is the work, and the part I'd put in front of you.

I'm betting on AI-forward engineering being the future — and Mimir is me getting fluent in it the only way I trust: build the hard version, then prove it holds.

## The court Mimir keeps

Wisdom delegates. Heavy or autonomous work leaves Mimir's hall and goes to the one whose craft it is:

| Hall | Who | Their craft |
|---|---|---|
| **The well** | **Mimir** | counsel, judgment, the spine, alignment with you — the voice you actually talk to |
| **The forge — Huldra** | **Brok** · **Sindri** · **Heimdall** | the dwarven smiths who forged the gods' treasures — **Brok** builds each story, **Sindri** reviews it adversarially against the runes (the acceptance criteria); then **Heimdall**, the watchman who sees all and misses nothing, certifies the whole work before it ships |
| **The studio** | **Freya** | the lady of beauty and craft — visual direction and design, in a room of her own |
| **The Hand** | *(faceless)* | the errand Mimir sends into the dark — research, audits, mapping a codebase it didn't build — returns with an artifact and no opinions |

On-demand **playbooks** wake only when intent calls them: the full BMAD-METHOD v6 greenfield lifecycle, or a **brownfield** rite for safely understanding and extending a codebase Mimir didn't raise.

## No wisdom taken on faith

The myth-names are the fun part. The engineering is the point. Mimir doesn't earn its counsel by *sounding* wise — every disposition is held to a test, and prompt changes are treated like code changes to a system under measurement:

- **A bank of trials** — [`evals/scenarios.json`](evals/scenarios.json) pins the right behavior for dozens of situations (intent-reading, the spine, proportional restraint, brownfield routing, …).
- **Tested as it truly ships** — trials run through the *real* persona on the *real* agent loop (`claude -p`), never a role-played effigy. ([`evals/mainloop-probe.js`](evals/mainloop-probe.js))
- **Judged by a council of three** — each run is scored by a strict **K=3 majority** of independent judges against explicit *expect* / *must-not* criteria, at N≈30 per trial — enough to drown out single-judge whim. ([`evals/judge-mainloop.js`](evals/judge-mainloop.js))
- **A law of change** — pin the new behavior as a trial *before* the edit, make the smallest change that flips it, prove it in a fresh context. **Cutting beats adding:** the well is the hot path, so the bar to carve a new line into it is high.
- **A constitution** — every architecture decision must pass [`PRINCIPLES.md`](PRINCIPLES.md), a ratified code each entry earned through a real failure or corroborated practice.

> **A drink from the well.** The brownfield rite was added by first writing four trials and baselining them against the *unedited* Mimir — which already passed all four. The evals proved the general wisdom had already generalized, so the change shipped as a one-line *pointer* plus an on-demand playbook, not a rewrite of the hot path. Then the Hand was sent to map two real codebases — and it held the line, tagging every claim *verified-in-code* vs *claimed-in-docs*, refusing to call a docs-only plan "built." (Full account in [`DESIGN.md`](DESIGN.md) §10.)

## The well's depths (repo map)

| Path | What's there |
|---|---|
| [`output-styles/mimir.md`](output-styles/mimir.md) | **Mimir himself** — the always-on persona spec |
| [`PRINCIPLES.md`](PRINCIPLES.md) | the constitution every decision must pass |
| [`DESIGN.md`](DESIGN.md) | the design blueprint + the reasoning behind each call |
| [`forge/huldra.js`](forge/huldra.js) | the forge — build → adversarial review → certify |
| [`skills/mimir-bmad/`](skills/mimir-bmad) · [`brownfield/`](brownfield) | the on-demand playbooks |
| [`studio/`](studio) · [`agents/`](agents) | Freya's studio and the faceless Hand |
| [`evals/`](evals) | the bank of trials + the deployment-faithful harness |

## The honest rune

A personal R&D project — single-user, raised and tuned in the open as a study in giving an AI agent durable judgment and making that judgment *measurable*. It runs on a Claude Code subscription in an interactive session; the forge has been driven end-to-end through real multi-epic builds. The names are [Norse](https://en.wikipedia.org/wiki/M%C3%ADmir): Mimir keeps the wisdom; Huldra, Brok, Sindri, Heimdall, and Freya each keep their lane.
