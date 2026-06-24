# Red-team: USER.md writer-header

Reviewed `/home/tim/.claude/mimir/USER.md` HEADER block (lines 8–12) — the rules governing the agent-as-writer.

## Findings (severity-ranked)

### S1 — No merge-vs-append rule. The single most likely failure.
The block says "capture only what generalizes" and "one fact per line" but never tells the writer to look for an existing entry on the same topic first. Default LLM behavior on "write what you learned" is to **append a new bullet**. The body already shows the cost: there are clusters that are really one topic (e.g. the two `[high]` design entries at lines 44 + 46; verification spread across 25/28). Without an explicit "merge into the existing entry, don't append a near-duplicate" instruction, this file degrades into overlapping restatements — exactly the append-only burying the user bans elsewhere (line 30). This is the highest-value missing rule.

### S2 — No contradiction-handling rule. Silent drift on the most important writes.
"Superseded → USER.archive.md" covers a *clean replace*, but not the common case: a new observation **partially contradicts or qualifies** an existing graded entry. Nothing tells the writer to (a) reconcile rather than add a competing line, or (b) treat a contradiction as evidence that downgrades the old entry's confidence. A contradicted `[high]` left standing is the worst outcome this file can produce — it makes the agent confidently wrong about the person. Must be covered.

### S3 — Confidence grades are defined but their *dynamics* aren't.
Line 10 defines the three grades as static labels. It never says **when to move between them**: confirmation upgrades, a contradiction or long silence downgrades, a single new sighting does NOT jump `[low]`→`[high]`. Without the dynamics, every entry freezes at whatever grade it was born with, and the grade stops tracking reality — which kills the "re-verify a load-bearing entry" discipline the top blurb leans on.

### S4 — Archive vs delete is asserted, not distinguished.
"Superseded → USER.archive.md" gives one disposition but never says **delete is not an option** / never hard-delete a fact. The user's whole memory doctrine (CLAUDE.md "Never delete — retire to `.archive/`") is that nothing is dropped, only retired. A writer reading only this header could reasonably `rm` a stale line. One clause fixes it.

### S5 — Two readers share one header; the writer rules sit under a blurb addressed to neither cleanly.
Lines 3–6 are read-to-apply guidance; lines 8–12 are write-to-update. The `✍️` heading does separate them, which is good. The residual risk: a *reader* (the common case — every project opens this to apply it) has to skim past write rules every load, and a *writer* has to notice the read blurb governs it too (the "what he says now wins" / "re-verify" disciplines are writer-relevant — a contradiction from "now" should trigger a write). Neither header points at the other. Low severity because the split is already mostly clean; worth one cross-reference word at most, not a restructure.

### Misweighting
- **Over-weighted:** "each word earning its place" (line 12) is style advice competing for attention with load-bearing rules. The file's risk is wrong/duplicated content, not verbosity. It's also self-evident given the rest.
- **Under-weighted:** the merge and contradiction cases (S1, S2) — the two highest-frequency write decisions — get *zero* words while the rarer clean-supersession case gets an explicit arrow.

### Trigger strength
A flat dashed list under a bold line reads as ordinary file prose and will be skimmed on a write — especially since the agent opened the file to *apply* it, not to edit it, so it's already in read-mode. Levers that fire harder without adding words:
- **Imperative verb-first lines.** "Merge, don't append." "Downgrade on contradiction." A bare imperative is parsed as an instruction; a descriptive sentence ("entries should generally be merged") is parsed as content.
- **Keep the `✍️` + the literal "before you edit"** — that's the one cue that converts a reader into a writer; it's doing real work, keep it.
- **Front-load the decision rules** (merge / contradict / regrade) above the style rule, so the first thing a writer hits is a branch on what they're about to do.

## Relevance tracking — RULING: (c), neither counter nor date stamp.

Pick **(c)**: rely on the confidence grade made *dynamic* (S3) plus the existing re-verify discipline.

Reasoning:
- **(b) date stamp is barred** by the user's standing rule — operative docs carry no inline date/attribution stamps; provenance lives in a separate log. This file is the operative doc the agent reads every session; a `last-confirmed: 2026-06-…` on every line is exactly the inline provenance the rule prohibits. Nothing here justifies an exception: the file already has a designated provenance sink (`USER.archive.md`) for superseded facts, so the separate-log mechanism the rule assumes already exists.
- **(a) times-confirmed counter** is a redundant second freshness axis bolted next to the confidence grade — they encode the same thing (confirmation count) in two places, which invites drift (the exact single-source failure the project's memory doctrine warns against). It also can't represent *staleness* (a counter only goes up; an entry confirmed 8× then contradicted still reads "8").
- **(c)** the confidence grade *already is* the freshness signal once its dynamics are written down (S3): confirmation upgrades, contradiction/silence downgrades. That folds recency into the one axis the reader already consults, costs no new per-line syntax, and respects the no-inline-stamp rule. The cleaner mechanism isn't a new field — it's making the field already present actually move.

## Proposed header replacement (equal-or-shorter)

Current writer block is 4 bullets. Replacement keeps it to 4 lines (style rule folded into line 4), adds merge + contradiction + regrade dynamics, and front-loads the decision branches:

```
**✍️ Writing — read before you edit:**
- **Merge, don't append.** Find the entry on this topic first; sharpen it in place. New line only for a genuinely new fact. Capture only what **generalizes** — a one-off stays a one-off.
- **Regrade as evidence moves:** `[low]` provisional → `[med]` seen a few times → `[high]` repeatedly confirmed. Confirmation upgrades; a contradiction or long silence downgrades.
- **On a contradiction:** reconcile the existing entry, don't add a competing one. Cleanly superseded → `USER.archive.md` (retire, never delete).
- **Out of scope:** project-specific facts → that repo's auto-memory (counsel). One fact per line.
```

Line count: 4 → 4. Adds the three missing high-frequency rules (merge, regrade-dynamics, contradiction+no-delete) by absorbing the words spent on the static grade definition and the self-evident "each word earning its place." The grade *definition* is preserved (it's now inline in the regrade line, doing double duty as definition + dynamics).
