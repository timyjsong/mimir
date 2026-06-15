# Mimir Durable Memory — FINAL SURVIVOR Design

**One-line architecture:** *Make CC's silent 25 KB memory cliff a felt budget on the hook
Mimir already runs; keep the index live-only so it's bounded by construction; kill the
drift class by dropping self-imposed frontmatter; and consolidate via an **owned,
rail-protected `/consolidate-memory` skill** (pattern borrowed from CC's Claude-Desktop
skill, but **we author and control it**) that runs **manually when the budget nudges** —
never auto-fired, never unattended over decision-history. Zero brain clauses; the
deliverable is one shell-hook addition, file conventions, deletions, and one owned skill
guarded by snapshot + never-delete archive + pin + audit.*

This is the synthesis **after the blind red-team**. The headline pivot of the prior draft —
*"don't build a janitor, CC ships one (`consolidate-memory`)"* — is **dead** (see §0). The
survivor keeps Design 1's discipline-first minimalism (felt budget, live index, dumb body,
one rolling resume) and Design 2's safety rails + per-type decay/pin, and **re-adopts D2's
owned-curator stance** for the consolidation prose — because the borrowed skill is not
reachable and not safe to point at this store unmodified.

---

## 0. What the red-team killed/wounded — and the verified ground truth

Every claim below re-verified on disk in this session (`claude --version` = **2.1.177**).

### KILL — the native `consolidate-memory` skill is NOT invocable from a Mimir CC session
- It exists **only** under `/home/tim/.claude/remote/plugins/*/skills/consolidate-memory/`
  (468 path hits; the tree's `plugin.json` self-describes as **`anthropic-skills` —
  "Anthropic-managed skills for Claude Desktop"**, sibling to `ccd-cli`/`srv`/`run` = the
  **cloud / remote-agent runtime**). `[verified: grep -rl + cat plugin.json, this session]`
- The locally-installed marketplace is **`claude-plugins-official`** and does **NOT** contain
  it. `find … -name SKILL.md` over the non-remote tree returns **nothing** for "consolidate".
  `[verified: ls + find, this session]`
- It is **NOT** in this session's available-skills list (mimir-bmad, deep-research, huldra,
  verify, code-review, … — no `consolidate-memory`). `[verified: skills list]`
- It has **never fired** here: no `.dream-state.json`, no `.archive/`, no `.snapshots/`,
  no `.dream-log` in the memory dir. `[verified: find, this session]`

**Consequence:** the prior design's One-Line Architecture and its 5/5 CC-compat win
("uses the native skill — the literal borrow-don't-rebuild win") are **unfounded**. Tier 2
as written builds an auto-trigger + rails harness around a skill that **isn't there**.
Stripped of that premise, the right move is exactly what D2 proposed and the prior draft
wrongly rejected: **own the consolidation prose.** We borrow the *pattern* (the 3-phase
reflective pass), not the *stack* — which is the standing rule, correctly applied.

### WOUND — even if reachable, the borrowed skill is a destructive consumer-assistant tidier
- Read on disk: framed for a **personal-assistant user-model** ("who they work with, what
  they're focused on, how they like things done"); verbs are **destructive with no
  recoverability** — *"retire the file"*, *"cut it"*, *"Drop what's easy to re-find"*,
  *"Remove pointers to retired memories"*. `grep` for archive|snapshot|pin|decay shows the
  skill knows **none** of Mimir's rails. `[verified: cat SKILL.md, this session]`
- Mimir's store is the **opposite**: decision history whose value is the dated, settled,
  counterintuitive record (`prior-suppresses-verification RESOLVED — does NOT reproduce`,
  `override counts only when cost engaged`, `register quarantined — rhetoric tanked spine
  29→25`). A pass told to "retire dated/done files and drop re-findable facts" is **actively
  misaligned** with a store whose dated/done entries are the asset.

### WOUND — the "net-neutral / net-negative brain cost" was fabricated
- `grep -niE "index|frontmatter|condense|consolidat|archive|prune|topic file|metadata"` over
  `output-styles/mimir.md` (139 lines) returns **NOTHING**. There is **no manual-index-
  management prose in the brain to delete.** `[verified: grep, this session]`
- This repo has **measured** that added brain text degrades unrelated behavior (register/
  spine firewall finding; rhetoric tanked spine). So new hot-path clauses are pure additive
  bloat, not a wash. **Decision: ship ZERO brain clauses** (§3).

### WOUND — Component A (Stop-hook auto-trigger) buys nothing and fights the platform/footer
- A hook **cannot launch a skill** `[verified: hooks docs]` — so A was always "nudge the
  model," identical in kind to the existing UserPromptSubmit budget nudge (B).
- Stop fires at **end of every turn**; the design's own dual-gate re-fires every turn while
  over budget → a memory-chore nudge on a one-line grep turn, colliding with the brain's
  proportional-engagement + just-shipped footer discipline ("trivial work gets no footer,
  ever"; *more cumbersome than vanilla = a failure*).
- Stop hooks have **no documented `stop_hook_active` loop guard** and the docs warn against
  recursion; "nudge to do work before stopping" is the recursion-prone shape.
- **Decision: CUT Component A entirely.** The felt budget on the existing channel (B) drives
  consolidation; no second global hook, no `.dream-state.json`, no every-turn injection.

### WOUND — index-is-live + strip-frontmatter desync / decay-signal / discoverability
- Topic files carry `metadata.type` in frontmatter today; the decay table keys on type +
  open/closed glyph (▶/🗒️/DONE) that lives in the **index line**. Dropping settled entries
  from the index **and** stripping frontmatter would leave a kept-but-settled note with
  **no state signal** (filename class ≠ open/closed state), and an **un-summarized cold blob**.
  `[verified: frontmatter present on disk; glyphs live in MEMORY.md index lines]`
- **Fix (in §3):** (a) keep a thin **pinned "Standing records" section** in the index so
  load-bearing settled notes stay *volunteered*, not grep-only; (b) every cold file keeps a
  **one-line H1-adjacent hook** as its first body line (the summary that *was* the index
  line moves into the file when the index line drops) — so grep returns an identifiable line,
  not a blob; (c) the decay signal lives in the **filename prefix + the index glyph while
  live**; once settled-and-dropped, decay no longer needs a state signal (it's already cold).

### SCRATCH — auto-fire precondition, USER.md cross-scope, dual-gate mis-fires day one
- Folded in: no auto-trigger at all (A cut) ⇒ the "is CC already auto-firing?" gating
  question is **moot**. USER.md gets a **convention header only** (no trigger plumbing).
  The day-one over-budget (23.6 KB now) is handled by B's nudge → a **real first manual pass**.

---

## 1. Current state (verified this session)
- `MEMORY.md` = **58 lines / 23,606 bytes** — already over a sane felt budget, right under
  CC's 25 KB / 200-line **silent** load cliff. The **byte cap bites first.**
- ~53 topic `.md` files, all carrying Mimir's self-imposed `name`/`description`/`metadata`
  frontmatter (CC requires none — "plain markdown" `[verified: docs]`).
- **Two** `resume_*.md` notes (accretion pattern).
- `USER.md` = `/home/tim/.claude/mimir/USER.md` — **53 lines / 12,204 bytes**, growing.
- Live hooks: `UserPromptSubmit` (reload-skills + **`tools/context-meter-hook.sh`** —
  real path `/home/tim/projects/mimir/tools/context-meter-hook.sh`) and a `PostToolUse`
  reload-skills matcher. No memory hook, no archive, no snapshots.

---

## 2. The survivor architecture

```
            HOT (auto-loaded every session — CC hard-caps at 200 lines / 25 KB, SILENT)
 ┌────────────────────────────────────────────────────────────────────────┐
 │ MEMORY.md — bounded LIVE INDEX + a thin pinned STANDING-RECORDS section  │
 │   · one line per LIVE entry (active work, open loops, ▶▶ resume ptr)     │ felt budget 20K/180ln
 │   · 📌 STANDING RECORDS: load-bearing settled notes kept VOLUNTEERED     │ (floor under CC's 25K cliff)
 │     (PRINCIPLES-adjacent 🏛️, reference_*, settled guards) — never dropped │
 │   · other settled/closed/superseded → index line DROPS (file stays)      │
 └────────────────────────────────────────────────────────────────────────┘
    ▲ memory-meter (UserPromptSubmit — SAME hook as context-meter): "memory-index 86% —
    │  consolidate before adding"   ← the ONLY trigger. No Stop hook.
    ▼
            COLD (CC-native on-demand grep/glob/Read — never auto-loaded)
 ┌────────────────────────────────────────────────────────────────────────┐
 │ topic_*.md  — one fact each; DUMB body; NO frontmatter; FIRST body line  │ unbounded; CC reads
 │              is a ≤150-char hook (so grep returns an identifiable line)   │ on demand; filename
 │ resume.md   — ONE rolling handoff, updated in place, never stacked        │ prefix = the grep
 │ .archive/   — retired entries, MOVED never rm (recoverable)               │ index for cold tier
 │ .snapshots/ — pre-pass tarballs (keep 5)   ·   .consolidate-log          │
 └────────────────────────────────────────────────────────────────────────┘
   the consolidator = an OWNED /consolidate-memory skill (we author it), run MANUALLY
   when the budget nudges, guarded by snapshot + never-delete + pin + audit. NOT auto-fired.
```

| # | Component | Lives as | Tier | Fixes |
|---|---|---|---|---|
| **B** | Felt memory budget below CC's silent cliff | +~10 lines in existing `context-meter-hook.sh` (UserPromptSubmit) | **1** | growth (loud bound) + surfaces the consolidate trigger |
| **C** | Index = live-only + thin pinned standing-records section | `MEMORY.md` header convention | **1** | growth (#1 lever) — without losing recall |
| **D** | Dumb body, no frontmatter, first-line hook, single-source, edit-in-place | file-format convention | **1** | drift (structural), killed at rest |
| **G** | One rolling `resume.md`, update-don't-stack | convention + one-time tidy | **1** | growth (resume accretion) |
| **F** | Safety rails: `.archive/` (never rm), pre-pass snapshot, audit log | shell in the owned skill + conventions | **1**(archive) / **2**(snapshot) | makes any consolidation pass safe |
| **K** | **Owned `/consolidate-memory` skill** (pattern borrowed, prose authored by us) | `skills/consolidate-memory/SKILL.md` in this repo | **2** | hygiene (the ACT) — manual, rail-guarded |
| **E** | Per-type decay + 📌 pin rules the OWNED skill follows | rules inside skill K + `MEMORY.md` header | **2** | growth by category + load-bearing safety |

**Net brain text: ZERO clauses.** All bookkeeping lives in the hook, the file conventions,
and the owned skill — which CC's own docs say is where always-loaded procedural detail
belongs (not the every-turn prompt).

---

## 3. Tier 1 — cheap, low-risk, do first (no skill, no auto-trigger)

Closes growth + drift with **one shell-hook addition, conventions, deletions, and ZERO
brain clauses.** Ship and live with it before building the consolidator.

### T1.1 — Felt memory budget (Component B) — *growth*
Extend the **existing** `context-meter-hook.sh` (UserPromptSubmit, every turn) by ~10 lines:
`wc -c MEMORY.md`, compare to a **20 KB / 180-line budget** (a ~5 KB / 20-line floor under
CC's 25 KB / 200-line **silent** cliff, so the nudge fires while the tail still loads):
- below 80%: **silent** (matches the footer ethos; trivial turns stay clean).
- 80–99%: `memory-index: 86% (17.2/20K) — consolidate the longest index lines before adding`.
- ≥100%: `memory-index: OVER (20.8/20K) — CC silently drops past 25K. Run /consolidate-memory.`

Tunable via env (`MIMIR_MEMORY_THRESHOLD`); eval-guarded by the existing `MIMIR_NO_METER`
(also suppresses it for fired subagents — noise, not correctness); fail-silent (exit 0 on
any error). This is Hermes's budget-as-felt-pressure adapted to CC's reality (no `memory`
write-intercept exists). **Brain cost: zero** — the existing footer disposition already
reacts to injected meter lines; this is one more line on the same channel.

### T1.2 — Index is a live index + a thin pinned standing-records section (Component C) — *growth, #1 lever, recall-safe*
Today `MEMORY.md` is a full catalog of ~53 files → monotonic growth → guaranteed cliff.
Convention (a header comment in `MEMORY.md`; **no brain clause**):

> `MEMORY.md` has two parts: **(1) LIVE** — active work, open loops, the `resume.md`
> pointer; an entry drops from LIVE the turn it settles (its topic file stays on disk,
> found by grep on the filename prefix). **(2) 📌 STANDING RECORDS** — a short pinned list
> of *settled but load-bearing* notes (PRINCIPLES-adjacent 🏛️, `reference_*`, settled
> guards) that must stay **volunteered** to a fresh session. Standing records are one line
> each and are **never auto-dropped.** Everything else settled lives cold.

This directly answers the red-team's strongest WwOUND on C: **dropping settled-but-load-
bearing records to grep-only kills the "don't re-derive the settled ones" recall CLAUDE.md
relies on.** The pinned standing-records section keeps exactly those volunteered, while the
long tail of `✅ DONE` ephemera drops out. Index size becomes a function of *what's live +
a bounded pin list*, not *everything that ever happened*.

### T1.3 — Dumb body, no frontmatter, first-line hook (Component D) — *drift, structural, at rest*
- New topic files: **no frontmatter.** Line 1 = `# Title`. **Line 2 = a ≤150-char hook**
  (the same text that would be the index line). When the index line later drops, the file is
  still **self-identifying to grep** — answering the red-team's "cold file becomes an
  un-summarized blob" WOUND.
- The one-line summary is **single-sourced**: while LIVE it's the index line; once dropped it
  lives as the file's line-2 hook. Body never restates it elsewhere → they **cannot** drift.
- Edits are **in-place** (correct the line/file; never stack a contradicting note).
- **Frontmatter strip is lazy + amortized** by the owned skill (Tier 2) and by any hand-edit
  (an edit drops it). CC ignores inert frontmatter, so a mixed dir is harmless.
- **Decay signal survives the strip:** it rides the **filename prefix** (`backlog_`/`feedback_`
  /`reference_`/`project_`) + the **glyph in the LIVE index line while the entry is live**.
  A settled-and-dropped entry needs no state signal — it's already cold by definition. This
  closes the red-team's "strip destroys the type/state signal the decay table needs" WOUND:
  decay only acts on LIVE entries (which still carry the glyph) and on filename class.

> **Conflict resolved (verified):** CC does **not** require topic-file frontmatter — "plain
> markdown" `[verified: docs]`. D2's "CC writes that frontmatter so stripping fights the
> runtime" premise is wrong. **Strip it.** Residual: a stored *fact* going stale vs. the
> world (a moved path) is **not** prevented at rest — caught at read by the brain's
> eval-proven verify-before-asserting disposition. Honest scope: structural drift killed;
> world-drift caught at read.

### T1.4 — One rolling resume + the `.archive/` rail (Components G + F-lite)
- **G:** collapse `resume_*.md` → a single `resume.md`, updated in place each checkpoint
  (move done→archive, drop superseded lines, never stack a dated file). The ▶▶ pointer always
  names the one `resume.md`. One-time: move the two existing dated notes to `.archive/`.
  Folds into the brain's **existing** continuity disposition — **no new brain word.**
- **F-lite:** create `memory/.archive/` and adopt **never-delete → move-to-archive** as the
  convention now. `.archive/` + git history is the Tier-1 rollback; tarball snapshots arrive
  with the consolidator (Tier 2). This is the one Hermes rail worth having *before* any pass
  that retires files.

**Tier-1 brain text: ZERO.** All of T1 is hook + conventions + a one-time tidy. (The prior
draft's "≤2 brain lines, net-negative after deleting manual-index prose" is dropped — that
prose does not exist; adding clauses is pure bloat.)

---

## 4. Tier 2 — the deliberate build (the OWNED consolidator + decay/pin + full rails)

Tier 2 makes consolidation an **actual capability** — but **manual and owned**, not an
autonomous auto-fired rewrite. This is the corrected stance: **CC's `consolidate-memory` is
not reachable from a Mimir session, so we author our own skill**, borrowing only the 3-phase
*pattern* and hardening it for decision-history.

> **Discipline-first gate (from the backlogs, verbatim):** *"Discipline-first; build a
> mechanism only if the discipline proves insufficient."* So **Tier 1 ships first and we
> measure.** Tier 2 is built **only if** the felt budget + manual cleanup proves
> insufficient over real sessions. The consolidator below is the *plan* for that build, not a
> same-day deliverable.

### T2.1 — The owned `/consolidate-memory` skill (Component K) — *hygiene, the ACT, controlled*
A skill **we author** at `skills/consolidate-memory/SKILL.md` (in this repo, symlinked
live like the rest of Mimir). It borrows CC's 3-phase shape (take stock → consolidate →
tidy index) but is **rewritten for Mimir's store** and **wraps the destructive verbs in
rails it executes itself.** It runs in the **interactive session** (subscription-safe;
never `claude -p` `[verified: billing-split locked]`), invoked by the model or Tim **when the
budget meter nudges** — never auto-fired by a hook.

**Mimir-specific framing (the part the borrowed skill lacked):**
> *This store is **decision history**, not a user-model. Its dated, settled, counterintuitive
> records are the asset — do **not** "retire because done." Retire an entry ONLY if its LIVE
> index line has already been dropped per the live-index convention AND it is not a 📌
> standing record. **Never** fold or retire `reference_*`, PRINCIPLES-adjacent 🏛️, or
> settled guards. When uncertain, keep — bias to keep, never to prune.*

**The pass, with rails the skill performs deterministically first:**
1. `tar czf memory/.snapshots/<ts>.tgz memory/` (keep last 5) — **pre-pass snapshot**.
2. **Take stock:** list dir, read `MEMORY.md` (incl. the decay/pin header), skim topic files.
3. **Consolidate (rail-bounded):** merge true duplicates (keep the richer path); strip
   frontmatter on any file it touches (folding the summary into the line-2 hook); fix
   relative→absolute dates; **move** (never `rm`) a retired file to `.archive/`, only when the
   keep/retire rules above permit.
4. **Tidy index:** keep `MEMORY.md` ≤ 180 lines / 20 KB; drop pointers to archived files;
   ensure the 📌 standing-records section is intact.
5. **Audit:** append a touched-files summary to `memory/.consolidate-log`.

Because the skill is **ours**, the red-team's central WOUND — *"safety depends on the LLM
overriding the fixed skill's own 'retire/cut' text every pass"* — **disappears**: there is no
contradicting text to override. The skill's own instructions ARE the rail-honoring ones.

### T2.2 — Per-type decay + 📌 pin rules (Component E) — *growth by category + safety*
The keep/retire rules live **in the skill** and are mirrored in the `MEMORY.md` header, keyed
on the filename prefix + (for live entries) the index glyph — **no `.usage.json` sidecar**:

| class | rule |
|---|---|
| `resume*` | keep **one** live; archive when superseded |
| `backlog_*` | archive when the entry is DONE/closed **and** already dropped from LIVE |
| `feedback_*` | archive when superseded; else durable |
| `reference_*`, PRINCIPLES-adjacent / 🏛️, settled guards | **📌 standing record — never auto-retired, kept volunteered** |
| `project_*` (open ▶/🗒️) | LIVE while open; archive when settled (unless load-bearing → standing record) |

**Liberal pinning is the shield.** The red-team's note — "pin most of the high-value store and
the autonomous pass operates on the residual" — is **the point**: we *want* the pass to act
mostly on ephemera, because it runs over decision history. Shrinking the win toward "felt
budget + occasional safe merge" is the *correct, conservative* outcome.

### T2.3 — Full safety rails (Component F) — already specified in T2.1
Deterministic shell (uncorruptible by the LLM doing the pass): **pre-pass snapshot + rollback**
(`.snapshots/`, keep 5), **never-delete → `.archive/`**, **audit trail** (`.consolidate-log`),
**git** as the deeper repo-level backstop. Every pass is one `tar -x` from reversible.

### T2.4 — USER.md (global) — convention header only, NO trigger
`USER.md` lives **outside** the per-project memory dir; a user-trait rarely goes stale by
time. **Decision (per red-team):** give it a **convention header only** — *merge-don't-append,
confidence-decay, soft cap ~60 lines / one screen* (per `backlog_usermodel_housekeeping.md`) —
and let the brain's **existing** write discipline ("write only what generalizes; treat as a
checked overlay") + an **occasional manual `/consolidate-memory USER.md`** handle it. **No
cross-scope trigger plumbing** (the prior draft's "fold USER.md into the per-project pass" is
dropped as architecturally muddy). Optionally extend meter B to `wc` USER.md against the soft
cap. The known content tension (USER.md "peer-not-podium" vs. the brain's quarantined-rhetoric
finding) is reconciled as a **content edit**, not a mechanism.

---

## 5. What this lets us delete / close
- `backlog_memory_autohygiene.md` → **closed by B + C** (felt bound + live index); the ACT
  is the **manual owned consolidator** (Tier 2), not an auto-fire.
- `backlog_usermodel_housekeeping.md` → **mostly closed** by the USER.md convention header.
- `backlog_handoff_mechanism.md` resume accretion → **closed by G** (one rolling resume).
- `backlog_scalable_bookkeeping.md` → its memory/index/USER.md arms handled here; MAPs /
  contracts / evidence remain forge/playbook-owned (out of scope).

Net deliverable: **deletions + one hook addition + conventions + one owned skill (Tier 2).**
No subagent, no DB, no daemon, no SQLite, no provider layer, no auto-trigger, no brain edit.

---

## 6. Traceability — each pain → fix
| Pain | Tier-1 | Tier-2 | Residual |
|---|---|---|---|
| **(1) Unbounded growth** | B felt budget + C live index (+pinned standing records) + G one resume | E per-type decay/archive via owned skill | cold tier grows — fine; CC never loads it; grep + line-2 hook find it |
| **(2) Manual hygiene** | B nudge surfaces it | **owned `/consolidate-memory`** (manual, rail-guarded) | the pass is operator-run, not auto — by design (safety > automation over decision history) |
| **(3) Drift** | **D no frontmatter** + first-line hook + single-source + edit-in-place | skill fixes stale time refs / merges dups under rails | world-drift (stale facts) caught at read by verify-disposition, not prevented at rest |

---

## 7. Failure modes / residual risk
- **The budget nudge is advisory** (hooks can't enforce writes). *Mitigations:* the 20 KB
  floor leaves 5 KB cushion under CC's silent cliff; the byte high-water re-fires every turn
  until acted on; the footer-honoring disposition is proven live. *Escalation only if proven
  insufficient:* a `PreToolUse` hook on `Write`/`Edit` of `MEMORY.md` that blocks a write
  pushing it over budget (heavier — build only on evidence).
- **The owned consolidator is still an LLM pass → it can mis-merge.** *Contained by F:*
  snapshot + never-delete `.archive/` + liberal 📌 pins + audit log make every pass reversible
  and load-bearing notes exempt. **The single biggest residual risk is the detection gap** —
  a *plausible-but-lossy merge* that reads fine in the audit summary and is never rolled back,
  on a rarely-audited local dir. *Mitigation:* (a) bias-to-keep + liberal pinning shrink the
  unprotected surface to ephemera; (b) the pass is **manual**, so a human is in the loop at
  invocation; (c) the `.consolidate-log` + git diff on the memory dir make a periodic review
  cheap. This is **reduced, not eliminated** — it is the honest cost of any consolidation.
- **Live-vs-settled mis-judged → entry dropped from index too early.** File never leaves disk
  (only the line drops) → grep-recoverable via filename prefix + line-2 hook; 📌 standing
  records and the ▶▶ resume pointer are never dropped.
- **CC ships a reachable native consolidator later** (or starts auto-firing one). *This is the
  good outcome* — retire our owned skill and point at the native one. Revisit-against-new-
  capabilities applies; re-check each CC release. Our skill is one file to delete.
- **Hook fan-out to subagents** — gate the new meter line behind `MIMIR_NO_META`/`MIMIR_NO_METER`
  like the existing meter (noise-suppression; subagents have their own memory).

---

## 8. Build cost
- **Tier 1:** ~10-line addition to the existing meter hook (B) + two `MEMORY.md` header
  conventions (C, D) + one-time `.archive/` tidy + collapse resume notes (G). **ZERO brain
  clauses.** ~half a day, almost all in one shell file + conventions.
- **Tier 2 (only if Tier 1 proves insufficient):** author `skills/consolidate-memory/SKILL.md`
  (~1 page, borrowed pattern + Mimir framing + the 5-step rail-bounded pass) + the
  decay/pin header (E) + the USER.md convention header (T2.4). **No hook, no state file, no
  subagent.** ~half to one day.

**Total ≤ ~1 day, no new storage engine, no auto-trigger, no brain edit.** The opposite of a
rebuild — and, unlike the prior draft, it depends on **nothing that isn't reachable.**

---

## 9. Open questions (for Tim)
1. **Tier-1-then-measure (recommended) vs. build both now?** Ship Tier 1, live a few sessions,
   build the owned consolidator only if manual cleanup proves insufficient (discipline-first).
2. **Budget numbers:** 20 KB / 180-line soft cap (5 KB / 20-line headroom) — right margins?
   The index is at 23.6 KB now, so the *first* manual consolidation is a real condense.
3. **Frontmatter:** lazy-strip (proposed, zero-risk) vs. a one-shot `sed` over 53 files now
   (clean dir immediately — a flagged bulk write, git-reversible).
4. **Standing-records section:** confirm the pinned-classes list (🏛️ / `reference_*` / settled
   guards) — this is the recall-safety valve; err toward including more.
5. **USER.md:** convention header + occasional manual pass (proposed) vs. a dedicated soft-cap
   meter line. And: reconcile peer-not-podium vs. quarantined rhetoric in that pass or
   separately?
