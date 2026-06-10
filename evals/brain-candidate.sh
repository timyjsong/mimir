#!/usr/bin/env bash
# Staging helper for safe self-iteration on the brain — see ../SELF-ITERATION.md.
#
# Claude Code resolves an output style by its `name:` FRONTMATTER, not its filename. So the
# candidate must declare `name: mimir-candidate` or the eval silently falls back to the LIVE
# brain (a false green), and a stray second `name: mimir` file can even corrupt the live
# default's resolution. This helper does the name-rewrites correctly on both sides so you can't
# forget them.
#
#   brain-candidate.sh seed     # live -> candidate (name -> mimir-candidate) + deploy it
#   brain-candidate.sh promote  # candidate -> live (name -> mimir). Run ONLY after evals are green.
set -euo pipefail
cd "$(dirname "$0")/.."                      # repo root
LIVE="output-styles/mimir.md"
CAND="output-styles/mimir-candidate.md"      # gitignored scratch
DEPLOY="$HOME/.claude/output-styles/mimir-candidate.md"

case "${1:-}" in
  seed)
    cp "$LIVE" "$CAND"
    sed -i 's/^name: mimir$/name: mimir-candidate/' "$CAND"
    ln -sfn "$PWD/$CAND" "$DEPLOY"
    grep -q '^name: mimir-candidate$' "$CAND" || { echo "ERROR: name rewrite failed (live frontmatter changed?)"; exit 1; }
    echo "seeded $CAND from live + deployed as style 'mimir-candidate'."
    echo "edit it, then: node evals/mainloop-probe.js <scenario-id> <N> <out> mimir-candidate"
    ;;
  promote)
    grep -q '^name: mimir-candidate$' "$CAND" || { echo "ERROR: $CAND missing/not a candidate — seed first"; exit 1; }
    cp "$CAND" "$LIVE"
    sed -i 's/^name: mimir-candidate$/name: mimir/' "$LIVE"
    grep -q '^name: mimir$' "$LIVE" || { echo "ERROR: live name rewrite failed — CHECK $LIVE before committing"; exit 1; }
    echo "promoted candidate -> $LIVE (name restored to mimir). Now: git add -A && git commit"
    ;;
  *)
    echo "usage: $0 {seed|promote}"; exit 1 ;;
esac
