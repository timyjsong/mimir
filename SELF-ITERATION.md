# Self-iteration — how Mimir safely changes itself

> Mimir is the **global default** output style now: every Claude Code session starts as Mimir.
> This repo is its source, and the live brain (`~/.claude/output-styles/mimir-agent.md`) is a
> **symlink into this repo's working tree** — so an edit to `output-styles/mimir-agent.md`
> becomes the default for the *next* session, in *any* project. This is the protocol that keeps
> self-modification safe. (It specializes the general change-discipline in `CLAUDE.md` for the
> one surface that's now load-bearing for the whole environment.)

## Mimir drives this — it's not a human runbook

This is the loop **Mimir runs itself** when asked to improve itself. The human sets the goal
("get sharper at X", "stop doing Y") and rules on the genuine judgment calls Mimir surfaces — an
ambiguous result, a regression worth a tradeoff, a design fork, or the promote itself if it's
worth gating. Everything mechanical below — seeding the candidate, making the edit, spawning the
eval probes (`claude -p`) and the judges, reading the deltas, promoting on green — Mimir does
**autonomously, with its own tools** (it can run the helper, spawn the probes, and launch the
judge workflow exactly as in any other task). Autonomy is the point: the agent runs its own
process; it doesn't hand the human a chore.

## The two facts that frame it

- **What makes it safe:** an output style loads *once*, at session start. Editing the brain does
  **not** change the session doing the editing — changes take effect on the *next* session, or on
  a fresh `claude -p`. There's no runaway self-modification, and brain changes are tested on fresh
  processes (that's exactly why `evals/mainloop-probe.js` spawns `claude -p`).
- **What makes it risky:** the live default is a *symlink to this working tree*. A half-baked edit
  to `output-styles/mimir-agent.md` is the live brain for the next session you open **anywhere** —
  until you fix it. A regression here hits everything, not an opt-in skill.

## The rule

**Never hand-edit the live `output-styles/mimir-agent.md` for a behavioral change.** Stage it on a
candidate, prove it on evals, and *promote* on green. (Trivial/cosmetic edits — a comment typo —
can go direct; proportional. Anything that changes behavior takes the loop below.)

## Setup & the name gotcha

The staging slot is the `mimir-candidate` output style — a deployed style nothing uses by
default, so the eval can target it without touching the live default. Seed it with the helper:

```sh
evals/brain-candidate.sh seed   # live -> candidate (+ deploy). Re-run anytime to reset to current live.
```

> **Why the helper, not a bare `cp`:** Claude Code resolves an output style by its **`name:`
> frontmatter**, not its filename. A plain `cp` leaves `name: mimir-agent` in the candidate — so a
> probe targeting `mimir-candidate` **silently falls back to the *live* brain** (a *false green*),
> and two files both claiming `name: mimir-agent` can even corrupt the live default's own
> resolution. The helper rewrites the name on both seed *and* promote so you can't hit that.
> (Sanity check after a fresh seed: make one distinct edit and probe once — it should *visibly*
> differ from live before you trust any green run.)

## The loop (per behavioral change)

1. **Pin the behavior first.** Add or adjust a scenario in `evals/scenarios.json` that captures
   what should change — and the regression-guard scenarios that must *not* move. The eval is the
   oracle; pin before you edit.
2. **Baseline the live brain** on the affected scenarios (no override → tests live `mimir-agent`):
   ```sh
   node evals/mainloop-probe.js <scenario-id> <N> /tmp/iter/base-<id>.json
   ```
3. **Seed + edit the candidate.** Reset to current live with `evals/brain-candidate.sh seed`,
   then make the **smallest** change in `output-styles/mimir-candidate.md`. Removing beats
   adding — the brain is the hot path.
4. **Eval the candidate** on the same scenarios, targeting it by name:
   ```sh
   node evals/mainloop-probe.js <scenario-id> <N> /tmp/iter/cand-<id>.json mimir-candidate
   ```
   Then judge both runs with `judge-mainloop` (K=3 majority) and compare: the target scenario
   should flip to ceiling, the guards should hold.
5. **Promote on green — and only on green.** When the candidate passes (clean flip + no regression):
   ```sh
   evals/brain-candidate.sh promote && git add -A && git commit
   ```
   **That promote is the only moment the global default changes** (it copies candidate → live and
   restores `name: mimir-agent`). Until then, a half-baked candidate is *structurally* unable to
   become the live default — it isn't in the live file.

## When you stop

**Leave the live brain green.** `output-styles/mimir-agent.md` is the default for your next session
anywhere — don't walk away with a broken or experimental *live* brain. (The candidate scratch can
stay dirty; it's never the default.)

## If a bad brain does go live

- **Uncommitted:** `git checkout output-styles/mimir-agent.md` — instantly restores the
  last-committed brain; the next session is back to normal.
- **A bad *committed* brain:** `git revert <sha>` (or check out the previous version of the file and
  commit). It's all git + a symlink — recovery is one command.

## Scope

This protocol is for **the brain** (`output-styles/mimir-agent.md`) specifically, because it's the
global default — the highest-stakes, every-session surface. Other surfaces follow ordinary
eval-driven discipline (pin → smallest change → validate) without the candidate dance: the on-demand
playbooks (`skills/mimir-bmad`, `brownfield/`) load only when intent calls them, and
`forge/huldra.js` runs only when you launch a build — a bad edit there can't break session *startup*
the way a malformed brain file can. (Do still sanity-check that the brain's YAML frontmatter parses
after a big edit — a broken style file fails to load globally.)
