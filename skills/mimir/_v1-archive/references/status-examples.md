# Status header — additional examples

Read this if you are uncertain how to format the status block for an unusual state. The canonical mid-round example lives inline in SKILL.md; this file holds the other patterns.

Paths in these examples are illustrative — actual paths resolve from `_bmad/bmm/config.yaml` in your project.

## Between workflows, no workers active

```
mimir status
────────────
phase:     planning
team:      mimir-news-agg
artifacts: <latest-finalized-artifact>
next:      spawn prd-worker for bmad-prd (create) — awaiting your go
```

## Fresh project, BMAD not installed

```
mimir status
────────────
phase:     install
team:      not yet created (BMAD not installed)
next:      you — confirm install at /home/tim/projects/foo or redirect
```

## Install in progress (lead-spawned via Bash, no worker)

```
mimir status
────────────
phase:     install
team:      not yet created (waiting on install)
next:      lead — running npx bmad-method install in background
```

## Background-ephemeral research worker running

```
mimir status
────────────
phase:     solutioning
team:      mimir-news-agg
workers:
  • (unnamed, background)  — bmad-domain-research · running, notify on completion
next:      worker — awaiting research report
```

## Loki build in progress (persistent + background)

```
mimir status
────────────
phase:     build
team:      mimir-news-agg
workers:
  • loki-worker  — autonomous build · running epic 2, last update at <timestamp>
artifacts: <latest-story-artifact>
next:      worker — building; you can ask me for status anytime
```

## At the planning-vs-build inflection (loki not yet implemented)

```
mimir status
────────────
phase:     readiness
team:      mimir-news-agg
artifacts: <readiness-report-path> (verdict: go)
next:      you — ready for build, but loki not yet implemented; planning-only project for now
```

## Post team-rebuild

```
mimir status
────────────
phase:     planning
team:      mimir-news-agg (rebuilt — no workers active)
artifacts: <prd-path> (finalized)
next:      spawn arch-worker for bmad-create-architecture — awaiting your go
```

## At the project boundary, post-teardown

```
mimir status
────────────
phase:     boundary (project complete)
team:      torn down
artifacts: <last-implementation-artifact>
next:      out of scope — re-invoke /mimir for refinements
```

## Superseding a recently-active prior session (fresh marker)

```
mimir status
────────────
phase:     planning
team:      mimir-news-agg  ⚠ prior session active seconds ago
next:      you — I'm the latest now; OK to stop the old session? (frees ~250MB, reopenable) — or leave it
```

(If the marker were old/stale, mimir just takes over — rm the old team + recreate — and offers to free the prior session's memory without flagging a conflict. Newest invocation always wins; the prior session will halt on its next input.)
