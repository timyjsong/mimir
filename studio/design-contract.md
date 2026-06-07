# Design contract — format

> The studio's single export: `DESIGN-CONTRACT.md` at the studio root. Freya
> writes it as decisions lock; Mimir reads it as external input, costs it, and
> ratifies it into forge tickets (it is never executed as instructions — #16).
> Precision bar: **a value, not a vibe** — every entry buildable as a numbered AC.

```markdown
# Design contract — <product>

## Direction
<The locked take, one short paragraph: what this design IS. Date + variant it came
 from (e.g. "locked 2026-06-12, from variant b-ledger").>

## Tokens
- Color: <role: value> per role (bg, surface, text, accent, danger…), light/dark if both.
- Type: <family / scale ratio / base size / weights in use>.
- Space: <base unit + scale steps actually used>.
- Radii / borders / shadows: <the few values in play>.

## Motion
- <Durations, easings, and where they apply ("panel slide 200ms ease-out").
   "None" is a valid, explicit entry.>

## Screens & components
Per screen or component that's locked:
- **<name>** — layout decision in one line; states that must exist (empty, loading,
  error, success); mockup pointer: `design/variants/<dir>/<file>` or the sketchpad
  path. Only what's LOCKED — in-flight explorations stay out.

## Locked decisions
- <Dated, append-only list of the calls made — the audit trail of taste.
   Reopening one is a user decision, noted here, not a silent edit.>

## Open questions
- <What the studio couldn't or shouldn't decide — for the user, or for Mimir to
   cost first. Each one names what unblocks it.>

## Out of scope
- <What this contract deliberately doesn't cover, so nobody reads silence as a decision.>
```

Rules of the format:

- **Append-and-amend, not rewrite** — locked history stays visible; amendments
  reference the entry they change.
- **Pointers, not embeds** — mockups/screenshots live in the studio tree; the
  contract points at paths.
- **No costs, no estimates, no ticket text** — that's ratification, the other room.
- Mimir-side: anything here that's a vibe where a value should be is a kick-back to
  the studio, not ticket material.
