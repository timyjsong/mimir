# This repo: the mimir skill (+ its workshop)

This repo **is** the mimir skill. The source lives here — `skills/mimir/` (the
skill) and `agents/` (its fire-and-return worker defs) — and is **symlinked into
`~/.claude/`**, so edits go live in any Claude Code session immediately. Every
session here exists to improve, refine, and tune that skill.

**Dev loop:** edit here → it hot-reloads live (same bytes, through the symlinks) →
`git commit` / `push`. No copy, no sync step — the repo is the single source of
truth. (A brand-new `~/.claude/skills/mimir` symlink needs one CC restart to
attach the first time; live thereafter.)

**Public-destined — no secrets.** Treat everything in this repo as eventually public; keep it clean (no secrets/credentials). Private context + decision history live in this project's **auto-memory** (`~/.claude/`, local, not git-backed) — by design.

## Orient before you act

This file is intentionally stateless: no status, no roadmap, no file map. Current
truth lives in three places, in this order:

- **The skill's own docs** — it ships its own maintainer/calibration doc (why it's
  built this way + verified facts) and an eval substrate (the change oracle). Read
  the maintainer doc before touching the skill.
- **Your auto-memory** — the `MEMORY.md` index loads each session; decision history
  and what's been verified. (Memory drifts from disk — re-check a named file before
  trusting it.)
- **git** — for what actually changed (the skill is version-controlled here now).

This directory also doubles as scratch space for exercising the live skill (spike
BMAD installs, throwaway app builds); a stray `_bmad/` or `node_modules/` here is
expected, not rot.

## What mimir is

An interactive, advisory lead/PM that drives a project through the BMAD-METHOD v6
lifecycle — personal, single-user, mostly greenfield, runs in an interactive
session. Advisory, not order-taking.

It is **not** the archived legacy mimir product (the old web-app build / research
spikes). Never use that as a reference for the skill.

## Working on the skill

It's a **coupled system** — its runtime spec, playbooks, references, worker defs,
and evals state one contract across several files. Read its own maintainer and
change docs before editing; a change in one place usually implies others.

Change it through its **eval substrate**, not by feel: pin the expected behavior
*before* the edit, make the smallest change that flips it, then validate in a
fresh context. Removing beats adding — the runtime spec is the lead's hot path.

**Reconsider before you refactor.** Much of the skill's complexity works around
older platform limits. Before polishing a mechanism, check whether a recent
platform release makes it unnecessary — don't refine a workaround you might delete.

**Trust what it has already verified.** The skill records empirically-settled
facts and open unknowns; don't re-derive the settled ones, and update those
records when something changes.

Keep my turns tight — a few high-value questions at a time, not long multi-topic
batches. (The skill's own elicitation cadence is itself something we tune — treat
it as live, not fixed.)
