# Status header — format spec (v3)

The exact format for Mimir's status header. **Loaded at orientation, every session** — the header appears on essentially every turn, so this is foundational, not on-demand. SKILL.md carries the *when* (which form fires); this doc carries the *how* (the exact format). Follow the glyphs verbatim — `ᛗᛁᛗᛁᚱ` is a fixed runic wordmark (the "Mimir" signature), not phonetic text, and is unreadable as "Mimir" by design.

## When each form fires

- **Compact line** — the default, almost every turn: mid-elicitation, within-phase gates, "your call" turns, delegating to a background worker, mid-build status checks.
- **Full block** — only on a **completion** (a step finished — install, an artifact finalized, a delegated check returned), a **phase change**, or **first orientation**. A delegated worker's *return* is a completion, so it gets the block.

## Compact line

`> ᛗᛁᛗᛁᚱ · <what's going on>` — a one-line blockquote: the runic wordmark, a spaced mid-dot, then the live status. No phase (the full block carries it at transitions), no `you`/`worker` court tag (the wording implies whose turn — an ask is yours; a "running…/I'll brief you" is the worker's).

> ᛗᛁᛗᛁᚱ · two questions before I draft the brief

> ᛗᛁᛗᛁᚱ · review the brief, or start the PRD

> ᛗᛁᛗᛁᚱ · domain research running; I'll brief you when it lands

> ᛗᛁᛗᛁᚱ · building epic 2; ask me for status anytime

## Full block

A blockquote led by the `# ᛗᛁᛗᛁᚱ` wordmark (h1 — renders large, draws no rule), then up to three sections whose **full small-caps labels sit flush with the wordmark**, items nested one blockquote level (`>>`) beneath, detail lines tabbed with `&nbsp;`-indent + `└` (italic). Sections separate with a blank `>` line — no horizontal rules, no `next:` line (the `▸`-current item + the prose carry what's next). Each section is omit-when-empty.

> # ᛗᛁᛗᛁᚱ
>
> ᴊᴜꜱᴛ ᴅᴏɴᴇ
>> ✓ domain research complete
>> &nbsp;&nbsp;&nbsp;└ *4 tools surveyed*
>> &nbsp;&nbsp;&nbsp;└ *2 [ASSUMPTION] tags*
>
> ᴘʀᴏɢʀᴇꜱꜱ
>> ✓ brief
>> ✓ PRD
>> ▸ architecture
>> ○ epics + stories
>> ○ readiness
>
> ꜰʟᴀɢꜱ
>> ⚑ settle-up rounding rule still open

### The three sections

- **`ᴊᴜꜱᴛ ᴅᴏɴᴇ`** — *ephemeral* "what just completed this turn," for **off-spine** finishes that have no checklist slot (install, research, validation, sharding, document-project). One `✓` per item; supporting detail tabs under it with `└`, italic, one per line (counts, paths, versions, verdicts). Gone next turn.
- **`ᴘʀᴏɢʀᴇꜱꜱ`** — the lifecycle checklist; carries the phase and the artifact set in one element (no separate phase line, no growing path list). Markers: `✓` done · `▸` current (= where we are = what's next) · `○` pending. Canonical spine: brief → PRD → architecture → epics + stories → readiness. When a *spine* item just finished, its detail tabs under that `✓` with `└`. In build the unit switches from docs to **epics/stories** (finite).
- **`ꜰʟᴀɢꜱ`** — *persistent* open items that outlive the turn: `[ASSUMPTION]` tags, an open risk from a readiness check, a conflict with a prior decision. One `⚑` per line. Omit when nothing's open.

## Variants

**Spine completion** — architecture just finished; its detail rides the checklist item, so there's no `ᴊᴜꜱᴛ ᴅᴏɴᴇ`:

> # ᛗᛁᛗᛁᚱ
>
> ᴘʀᴏɢʀᴇꜱꜱ
>> ✓ brief
>> ✓ PRD
>> ✓ architecture
>> &nbsp;&nbsp;&nbsp;└ *event-log ledger over local JSON*
>> ▸ epics + stories
>> ○ readiness

**Fresh install** — first orientation; only `ᴊᴜꜱᴛ ᴅᴏɴᴇ`, nothing on the spine yet:

> # ᛗᛁᛗᛁᚱ
>
> ᴊᴜꜱᴛ ᴅᴏɴᴇ
>> ✓ BMAD installed
>> &nbsp;&nbsp;&nbsp;└ *bmad v<version>*
>> &nbsp;&nbsp;&nbsp;└ *_bmad/ at <abs-path>*
>> ✓ skills loaded
>> &nbsp;&nbsp;&nbsp;└ *44 skills*
>> &nbsp;&nbsp;&nbsp;└ *module bmm*
>> ✓ reload verified

**Pre-install gate** — no `_bmad/` yet; thin, the install ask lives in the prose:

> # ᛗᛁᛗᛁᚱ
>
> ꜰʟᴀɢꜱ
>> ⚑ no _bmad/ at <abs-path> — install needed

**Readiness "go"** — build inflection:

> # ᛗᛁᛗᛁᚱ
>
> ᴘʀᴏɢʀᴇꜱꜱ
>> ✓ brief
>> ✓ PRD
>> ✓ architecture
>> ✓ epics + stories
>> ✓ readiness
>> &nbsp;&nbsp;&nbsp;└ *verdict: go*
>
> ꜰʟᴀɢꜱ
>> ⚑ build-ready — project toolchain not installed yet (gate the install before launching Huldra)

**Build phase** — the `ᴘʀᴏɢʀᴇꜱꜱ` unit switches to epics/stories:

> # ᛗᛁᛗᛁᚱ
>
> ᴊᴜꜱᴛ ᴅᴏɴᴇ
>> ✓ story 2.3 settle-up algorithm
>> &nbsp;&nbsp;&nbsp;└ *6 tests passing*
>
> ᴘʀᴏɢʀᴇꜱꜱ
>> ✓ epic 1 · ledger core
>> ▸ epic 2 · split + settle
>> &nbsp;&nbsp;&nbsp;└ *4 of 6 stories*
>> ○ epic 3 · shareable summary

## Notes

- Paths are illustrative — real ones resolve from `_bmad/bmm/config.yaml`.
- `ᛗᛁᛗᛁᚱ` is the display mark; capitalize "Mimir" in prose; the `/mimir` command and `name: mimir` identifier stay lowercase.
