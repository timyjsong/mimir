# Hermes Agent — Memory System Study & Mimir Mapping

**Date:** 2026-06-15
**Subject repo:** `github.com/NousResearch/hermes-agent` (Python, default branch `main`, last push 2026-06-15, ~193k★, repo size ~335 MB) — `[verified-in-source: gh api repos/NousResearch/hermes-agent]`
**For:** Mimir (framework-agnostic AI lead delivered as a Claude Code output-style; rides CC as runtime)
**Standing rule honored:** borrow Hermes's ARCHITECTURE/PATTERNS, not its STACK. CC is the runtime; in-session continuity is CC's native auto-compaction. This study focuses on **durable cross-session memory**.

**Sources read (on disk in `/tmp/hermes-study/`):**
- Docs: `doc_memory.md` (287 ln), `doc_curator.md` (278 ln), `doc_honcho.md` (238 ln), `doc_memory-providers.md` (571 ln), `doc_context-compression-and-caching.md` (376 ln), `doc_memory-provider-plugin.md`, `doc_profile-builder.md`
- Source: `src_memory_manager.py` (917 ln), `src_memory_provider.py` (296 ln), `src_context_engine.py`, `src_memory_monitor.py`, `src_turn_context.py`

**Epistemic note:** Every claim below is tagged `[verified-in-source: <file>]` (I read the actual doc/code line) or `[inferred]`. The marketing landing page (`hermes-agent.nousresearch.com`) was nearly content-free on memory — all substance came from the repo docs + source.

---

## HEADLINE FINDING

Hermes is an unusually **direct architectural sibling** of Mimir's memory layer, not a distant analogy. Its built-in durable memory is **literally `MEMORY.md` + `USER.md`** — the same two files Mimir uses, same intent split (agent-notes vs user-model), even the same `§`-delimited entry format. Crucially, **Hermes has already engineered solutions to the exact three problems the handoff names for Mimir:**

1. **Unbounded growth** → a **hard character budget** per store, enforced as a *write-time error* (no silent compaction), forcing the agent to consolidate-in-turn.
2. **Manual hygiene** → the **Curator**, a background, inactivity-triggered maintenance pass (`active → stale → archived` lifecycle + LLM consolidation) — applied to *skills* today, but the pattern transfers cleanly to memory.
3. **Drift** → a **frozen-snapshot read model** + **substring `replace`/`remove`** (edit-in-place not append) + **duplicate rejection** + **iterative re-summarization that drops obsolete items**.

This is **not overhyped** — the built-in tier is simple, well-bounded, and load-tested by a large user base; it earns its "bounded, curated memory" billing. The *sophistication* (vector/semantic/knowledge-graph/dialectic) lives in **optional external providers** (Honcho et al.), which are infra-bound and mostly SKIP for Mimir. The honest read: the parts that are genuinely good for Mimir are the **simple bounding + curation disciplines**, not the fancy provider stack. See §"Honest read" at the end.

---

## 1. STRUCTURE — tiers/types of memory

Hermes has **three durable tiers** (plus optional external):

| Tier | What | Where | Bounded? | `[tag]` |
|---|---|---|---|---|
| **A. Curated memory** (`MEMORY.md`) | Agent's personal notes: environment facts, conventions, tool quirks, completed-work diary, lessons | `~/.hermes/memories/MEMORY.md` | **Yes — 2,200 chars (~800 tok)** | `[verified-in-source: doc_memory.md]` |
| **B. User profile** (`USER.md`) | Model-of-the-user: name/role/tz, comms style, pet peeves, skill level | `~/.hermes/memories/USER.md` | **Yes — 1,375 chars (~500 tok)** | `[verified-in-source: doc_memory.md]` |
| **C. Session archive** (FTS5) | Every CLI/messaging session stored verbatim | `~/.hermes/state.db` (SQLite + FTS5) | **No — unlimited; not in prompt** | `[verified-in-source: doc_memory.md]` |
| **D. Skills** (procedural memory) | `SKILL.md` packages the agent writes for itself | `~/.hermes/skills/` | Curated by the Curator | `[verified-in-source: doc_curator.md]` |
| **(opt) External provider** | Honcho/Mem0/Hindsight/etc.: knowledge graph, semantic search, dialectic user-modeling | server/API | provider-defined | `[verified-in-source: doc_memory.md, doc_honcho.md]` |

**How they relate** `[verified-in-source: doc_memory.md §"session_search vs memory"]`:
- Tiers A+B are **always in the system prompt** (small, fixed ~1,300-tok cost, instant). They are the "critical facts always available" layer.
- Tier C is **on-demand recall** ("did we discuss X last week?") — searched via a tool, *no LLM call*, ~20ms FTS5 query. Explicitly the unlimited counterweight to the bounded A/B.
- The design intent is a **deliberate split: bounded-hot vs unbounded-cold-searchable.** This is the key structural idea for Mimir (see Mapping #2).

**Orchestration** `[verified-in-source: src_memory_manager.py]`: A single `MemoryManager` fronts a list of `MemoryProvider`s (builtin always first; **at most one external** to avoid tool bloat / conflicting backends, ln 8-9, 342-355). Providers expose lifecycle hooks: `prefetch` (recall), `sync_turn` (write), and optional `on_pre_compress`, `on_memory_write`, `on_session_switch`, `on_session_end`, `on_delegation` (ln 673-833, `src_memory_provider.py` ln 154-243).

---

## 2. WRITE / CONSOLIDATION — when & how memories are created

**Write path (built-in, agent-curated)** `[verified-in-source: doc_memory.md §"Memory Tool Actions", "What to Save"]`:
- The agent **writes its own memory via a `memory` tool** with three actions: `add`, `replace`, `remove`. **There is no `read` action** — memory is auto-injected at session start (ln 63).
- Writes are **proactive and unprompted** — "The agent saves automatically — you don't need to ask." Triggers: learning a user preference, an environment fact, a *correction*, a convention, completed work, or an explicit "remember this" (ln 102-111).
- A **"Skip These" list** keeps trivia out: vague info, easily-re-discoverable facts, raw data dumps, session ephemera, anything already in context files (ln 113-119).

**Consolidation triggers** (two mechanisms, this is the important part):
1. **Overflow-forced, in-turn** `[verified-in-source: doc_memory.md §"What Happens When Memory is Full"]`: when an `add` would exceed the char budget, the tool **returns an error** (not a silent drop) listing `current_entries` and instructing: *"Consolidate now: use 'replace' to merge overlapping entries into shorter ones or 'remove' stale entries… then retry this add — all in this turn."* (ln 130-149). Best-practice nudge: consolidate when >80% (visible in the prompt header). `replace` is *also* budget-bound — swapping in a longer entry can still overflow (ln 26-29).
2. **Background self-improvement review** `[verified-in-source: doc_memory.md §write_approval; doc_curator.md ln 24, 148]`: a **forked `AIAgent`** runs a periodic review (~every 10 agent turns for skills) in its **own prompt cache**, never touching the live conversation. It can write memory (gated by `write_approval`). This is the autonomous-hygiene engine.

**Compression-time extraction** `[verified-in-source: src_memory_provider.py ln 219-229]`: `on_pre_compress(messages) -> str` lets a provider extract durable insights from messages about to be discarded by in-session compaction, returning text folded into the compaction summary. (In-session — SKIP for Mimir, CC owns this — but the *principle* "harvest durable facts at the seam before discarding" maps to Mimir's handoff/clear seam.)

---

## 3. RETRIEVAL / RECALL — how memory is found & injected

Two distinct mechanisms, by tier:

- **A/B (curated):** **No retrieval step.** The whole of `MEMORY.md` + `USER.md` is **injected verbatim into the system prompt at session start** as a frozen block (ln 32-53). Because it's hard-bounded (~1,300 tok), it's cheap to just always include all of it. The header even shows live capacity: `MEMORY (your personal notes) [67% — 1,474/2,200 chars]` (ln 38). `[verified-in-source: doc_memory.md]`
- **C (session archive):** **Keyword full-text search** via SQLite **FTS5**, exposed as the `session_search` tool — returns *actual messages, no LLM summarization, no truncation*; the agent can also scroll forward/back inside a found session. ~20 ms query, **free (no LLM call)** (ln 182-194). `[verified-in-source: doc_memory.md]`
- **External providers:** add **semantic / vector search** and (Honcho) **dialectic-reasoned context injection** — base context (who-is-this-user) refreshed every N turns + an LLM-synthesized "what matters now" supplement, both budget-truncated (`contextTokens`) (doc_honcho.md ln 54-83). Recall via `prefetch()` (background recall, returns cached) (`src_memory_provider.py` ln 93-113). `[verified-in-source: doc_honcho.md, src_memory_provider.py]`

**Key insight for Mimir:** for the bounded hot tier, Hermes deliberately **avoids retrieval entirely** — the budget is small enough to always inject in full. Mimir's `MEMORY.md` index already follows this (loaded each session); the lesson is to keep it *small enough that full-injection stays cheap*, and push the rest to a searchable cold tier.

---

## 4. BOUNDING / PRUNING / DECAY — **THE KEY QUESTION**

Hermes attacks unbounded growth with **four independent mechanisms**:

### (a) Hard character budgets enforced at write time — NOT auto-compaction `[verified-in-source: doc_memory.md ln 22-30, 122-149]`
- `memory` = 2,200 chars (~8–15 entries); `user` = 1,375 chars (~5–10 entries). Configurable (`memory_char_limit`, `user_char_limit`).
- **Critical design choice (ln 23-25):** *"Memory does **not** auto-compact: when a write would exceed the limit, the `memory` tool returns an error instead of silently dropping entries. The agent then makes room itself."* The model is forced to make the keep/merge/drop judgment **in the same turn**, with `current_entries` shown to it. → growth is bounded *by construction* and the agent owns the trade-off.

### (b) The Curator — background lifecycle + LLM consolidation `[verified-in-source: doc_curator.md]`
Applied today to **agent-created skills**, but the mechanism is the generic answer to "X piles up forever":
- **Trigger:** inactivity-gated, *not* a cron daemon — runs on session start + a recurring gateway tick, only if `interval_hours` (default **7d**) elapsed **and** agent idle ≥ `min_idle_hours` (default **2h**) (ln 18-24). First-run deferred a full interval (ln 26-30).
- **Phase 1 — deterministic auto-transitions (no LLM):** unused `stale_after_days` (30) → `stale`; unused `archive_after_days` (90) → moved to `.archive/` (ln 32-34). **A `active → stale → archived` decay ladder keyed on last-use time.**
- **Phase 2 — LLM review (single aux-model pass, `max_iterations=8`):** a forked agent surveys items, **consolidates overlapping ones, patches drift, or archives** (ln 35). Cheap aux model configurable (ln 55-78).
- **Never deletes** — worst case is recoverable `.archive/` (ln 13). **Pre-run tar.gz snapshot** + one-command `rollback` (itself reversible); snapshots pruned to `keep: 5` (ln 107-129).
- **Pinning** exempts an item from all auto-transitions + tool deletion (ln 178-197); **protected built-ins** are hardcoded never-archivable (ln 195).
- **Usage telemetry sidecar** `~/.hermes/skills/.usage.json`: `use_count`, `view_count`, `last_used_at`, `patch_count`, `created_at`, `state`, `pinned`, `archived_at` — the LRU signal driving decay (ln 199-226).
- **Per-run report** (`run.json` + `REPORT.md`) + a **rename map** (`old → new`) when consolidations land, for auditability (ln 228-252).

### (c) Iterative re-summarization that *drops obsolete* content `[verified-in-source: doc_context-compression-and-caching.md ln 232-240]`
In-session compaction (CC's job for Mimir, so SKIP the mechanism) but the *principle* is sharp: on each re-compress, the **previous summary is fed back with instructions to UPDATE not regenerate** — items move In-Progress → Done, **obsolete info is removed**, not just appended. This is the anti-accretion discipline that keeps a rolling summary from growing.

### (d) Capacity visibility as a steering signal `[verified-in-source: doc_memory.md ln 38, 149]`
The live `[67% — 1,474/2,200 chars]` header + the >80% "consolidate before adding" best-practice make the budget a *continuous* pressure the agent feels every turn, not a cliff.

**Net:** Hermes keeps the hot tier finite by (i) a hard byte budget, (ii) refusing to silently drop, (iii) a time-decay + LLM-consolidation janitor, and (iv) routing the unbounded stuff to a cold searchable store that never enters the prompt.

---

## 5. SCHEMA / FORMAT — shape of a memory entry

**Built-in `MEMORY.md` / `USER.md`** `[verified-in-source: doc_memory.md ln 36-53, 151-171]`:
- **Flat plain-text entries separated by `§` (section sign).** Entries can be multiline. **No per-entry frontmatter, no IDs, no timestamps** in the file itself — the entry *is* its content.
- Rendered into the prompt under a header line: `══…══ / MEMORY (your personal notes) [67% — 1,474/2,200 chars] / ══…══`.
- **Entry-quality contract (the "good entry" spec):** *compact, information-dense, packs multiple related facts, specific & actionable.* Explicit good/bad examples — e.g. good: *"Project ~/code/api uses Go 1.22, sqlc, chi router. Run tests with 'make test'. CI via GitHub Actions."*; bad: vague ("User has a project") or verbose-narrative dated prose (ln 153-171).
- **Edit addressing:** `replace`/`remove` take an `old_text` **short unique substring** (not the full entry); ambiguous match → error asking for specificity (ln 65-76).

**Skills telemetry sidecar** (the *metadata* lives beside the content, not inside it) `[verified-in-source: doc_curator.md ln 203-218]`: JSON with `use_count / view_count / last_used_at / last_viewed_at / patch_count / last_patched_at / created_at / state / pinned / archived_at`.

**Provider write metadata** `[verified-in-source: src_memory_provider.py ln 279-296]`: `on_memory_write` carries provenance — `write_origin`, `execution_context`, `session_id`, `parent_session_id`, `platform`, `tool_name`.

**Takeaway for Mimir:** Hermes keeps the **content file dumb (no frontmatter)** and puts **lifecycle metadata in a separate sidecar**. This is the *opposite* of Mimir's "frontmatter in the topic file" — and notably it's the design that **can't drift between frontmatter and body**, because there is no frontmatter in the body to drift from (see Mapping #5).

---

## 6. CONSISTENCY / DRIFT — keeping memory true

`[verified-in-source: doc_memory.md unless noted]`
- **Frozen-snapshot read model (ln 32-53):** the prompt injection is captured once at session start and never mutates mid-session (preserves prefix cache). Writes persist to disk immediately but only *appear* next session. **Tool responses always show live state.** → one authoritative on-disk source; no two-copy drift within a session.
- **Edit-in-place, not append (ln 55-76):** `replace`/`remove` by unique substring means correcting a fact *updates the entry* rather than stacking a contradicting new one. The whole API is biased away from append-only accretion.
- **Duplicate rejection (ln 173-175):** exact-duplicate `add` is refused with a "no duplicate added" success — automatic dedup at the door.
- **Iterative-update summaries (§4c):** obsolete items are actively removed on re-summarization, not carried forward.
- **Curator LLM pass "patches drift" (doc_curator.md ln 9, 35):** explicit mandate to detect and fix staleness/contradiction across the library, + consolidate near-duplicates.
- **Security/injection scan (ln 177-179):** entries are scanned for prompt-injection / exfiltration / invisible-Unicode before acceptance (because they land in the system prompt). `[verified-in-source: doc_memory.md; src_memory_manager.py ln 111-127 sanitize_context + StreamingContextScrubber confirm fenced-context handling]`
- **`write_approval` gate (ln 209-246):** optional human-in-loop — `true` stages all writes (esp. the unprompted background ones) for `/memory approve|reject`. The documented answer to *"the agent saved a wrong assumption about me."*

**What Hermes does NOT have** `[inferred from absence across all read files]`: no automatic "re-verify a stored fact against current reality" (e.g. re-checking that a recorded file path still exists). Drift-prevention is **structural** (edit-in-place, dedup, dropping-on-resummary, LLM review) rather than **active reconciliation against the world**. This is the one gap relevant to Mimir's "note contradicting its own body" problem — Hermes sidesteps it by having no body-vs-frontmatter split, not by reconciling.

---

## MAPPING — ADOPT / ADAPT / SKIP for Mimir

Mimir's durable layer = `MEMORY.md` (one-line index, loaded each session) + per-topic markdown files (one fact each, with `name/description/type` frontmatter) + global `USER.md` + ad-hoc resume notes. Mimir rides CC; in-session continuity is CC auto-compaction.

| # | Hermes pattern | Verdict | How it applies to Mimir | Fixes |
|---|---|---|---|---|
| 1 | **Hard char/token budget per store, enforced at write as an ERROR (no silent compaction); agent consolidates in-turn** `[v: doc_memory.md]` | **ADOPT** | Put an explicit byte/entry budget on `MEMORY.md`-index and on `USER.md`. Mimir can't intercept its own file writes (no `memory` tool), so encode the budget as a **brain discipline + the session-start hook**: when the index exceeds budget, the hook surfaces "INDEX at N/limit — consolidate the K longest before adding." Mimir already *detects* oversize at session start (per memory notes) — this makes the budget explicit and the consolidation **mandatory before the next add**, in-turn. | **Unbounded growth** |
| 2 | **Bounded-hot + unbounded-cold-searchable split** (small always-injected memory vs FTS5 session archive recalled on demand) `[v: doc_memory.md]` | **ADOPT** | This is exactly Mimir's `MEMORY.md`-index (hot) vs per-topic files (cold) — but Mimir injects the *whole index* each session, which is the thing that grows. Reframe: the index is the **bounded hot tier** (cap it, see #1); topic files are the **cold tier, recalled on demand** (grep/glob, which CC already does well) **not loaded up front**. Stop treating the index as a complete catalog; treat it as a bounded "what's hot + how to find the rest." | **Unbounded growth** (the #1 leverage point) |
| 3 | **The Curator: inactivity-triggered background janitor — deterministic decay ladder (`active→stale→archived` by last-use) + LLM consolidation pass, never-delete/recoverable-archive, snapshot+rollback, pinning, usage-telemetry sidecar** `[v: doc_curator.md]` | **ADAPT** | The single highest-value transplant. Mimir has no daemon, but **CC has a `Stop`/session hooks and the Workflow substrate, and Mimir already runs its own evals/forge autonomously.** Build a **memory-curator routine** (a fired-and-returned Hand or a scheduled routine): Phase-1 deterministic — topic files untouched past `stale_after_days` get a `stale` marker, past `archive_after_days` move to a `memory/.archive/`; Phase-2 — a cheap-model pass that **merges near-duplicate topic notes, condenses the longest index lines, and flags drift**, writing a `REPORT.md` + rename map. Adopt **never-delete + snapshot/rollback + pin** verbatim — they're the safety rails that make autonomous pruning acceptable. *Subscription-safe note:* run the LLM pass via a subagent/Workflow (interactive lineage), NOT `claude -p`, per Mimir's billing-split rule. | **Manual hygiene** + **growth** + **drift** |
| 4 | **Time-decay keyed on a usage-telemetry sidecar** (`last_used_at`, `use_count`, `state`, `pinned`) — content file stays dumb, lifecycle metadata lives beside it `[v: doc_curator.md, doc_memory.md schema]` | **ADAPT** | Give each Mimir topic file a lightweight **sidecar** (one JSON, or a column in the index) tracking `last_referenced`, `created`, `state`, `pinned`. This is the **signal the curator (#3) needs** to decay. Adapt, don't copy: Mimir's "use" = the note being read/cited at orientation; a `pinned` flag protects the load-bearing notes (PRINCIPLES-adjacent records) from auto-archive. | **growth/decay** |
| 5 | **Dumb content file + sidecar metadata = no frontmatter-vs-body drift; edit-in-place (substring replace) not append; duplicate rejection** `[v: doc_memory.md, schema]` | **ADOPT** | Directly targets Mimir's named drift bug (*"frontmatter contradicting its own body after a partial edit"*). Two options: (a) **move the `name/description/type` frontmatter OUT of topic files into a sidecar/the index** so the body can't contradict its own header (Hermes's actual design); or (b) if frontmatter stays, make the **index line the single source of the one-liner** and the topic body never restate it. Plus: bias the brain toward **edit-the-existing-note** over **append-a-new-one**, and a dedup check before adding an index line. | **Drift** + growth |
| 6 | **Iterative-update summarization: feed prior summary back, UPDATE-don't-regenerate, actively DROP obsolete items** `[v: doc_context-compression-and-caching.md]` | **ADAPT** | Skip the in-session compaction *mechanism* (CC owns it). **Adopt the principle for resume/handoff notes:** when Mimir writes a new resume note, it should **update the prior one and delete superseded lines**, not stack a fresh dated note each clear. This is the discipline that stops resume-note accretion. | **growth (resume notes)** |
| 7 | **Capacity visibility as a live steering signal** (`[67% — 1,474/2,200 chars]` header every turn; >80% → consolidate) `[v: doc_memory.md]` | **ADOPT** | Mimir already prints an empirical context-% footer every turn — extend that footer (or the session-start hook) with a **MEMORY index fill %**. Same proven nudge: make the budget continuously felt so consolidation happens *before* the cliff. Cheap, hot-path-light, directly reuses Mimir's existing footer/meter machinery. | **growth/hygiene** |
| 8 | **`write_approval` staging gate for unprompted/background writes** (`/memory pending|approve|reject`) `[v: doc_memory.md]` | **ADAPT** | Mimir's writes are already human-visible (in-session, Tim reads them) so a full staging queue is overkill for *foreground*. But if the curator (#3) runs autonomously, adopt a **lightweight "curator staged these changes, review before they land"** gate for the *background* pass specifically — matching Hermes's insight that the dangerous writes are the unprompted ones. | hygiene safety |
| 9 | **`MemoryManager` / `MemoryProvider` plugin abstraction, one-external-provider cap, background sync executor, lifecycle hooks** `[v: src_memory_manager.py, src_memory_provider.py]` | **SKIP** | Pure runtime/stack — Python orchestration, thread executors, tool-schema injection. CC is Mimir's runtime; this is exactly the "borrow patterns not stack" line. No transplant. | n/a |
| 10 | **FTS5 SQLite session archive + `session_search` tool** `[v: doc_memory.md]` | **SKIP (mostly)** | The *concept* (searchable cold store) is already covered by #2 via CC's native grep/glob over topic files + the transcript. Standing up a SQLite/FTS5 store is stack Mimir doesn't need — CC already gives full-text search over the repo and Mimir's memory dir. (ADOPT only the *idea*, which is #2.) | n/a |
| 11 | **Honcho external provider: dialectic user-modeling (post-turn LLM derives insights about the user across passes: cold/warm → self-audit → reconcile), semantic search, knowledge graph, peer isolation** `[v: doc_honcho.md]` | **SKIP** (one idea ADAPT-able) | Infra-bound (external server, API key, vector backend) — out of scope and against the stack rule. **One transferable idea:** the **multi-pass reconcile step** ("check for contradictions between prior passes, produce a final synthesis") is a nice template for the curator's drift-patch pass on `USER.md` — derive the user-model *and* reconcile contradictions, rather than just append observations. Take the *principle*, not Honcho. | (drift, indirectly) |
| 12 | **Injection/exfiltration + invisible-Unicode scan on entries before accept** `[v: doc_memory.md, src_memory_manager.py]` | **SKIP** | Hermes needs it because *any user* can poison a system-prompt-injected memory in a shared/gateway deployment. Mimir is single-user (Tim), memory is Tim's own — threat model doesn't apply. Note and move on. | n/a |
| 13 | **In-session dual-compression (50% agent / 85% gateway), structured-summary template, prompt-cache breakpoints** `[v: doc_context-compression-and-caching.md]` | **SKIP** | CC's native auto-compaction owns in-session continuity for Mimir — explicitly out of scope per the handoff. (The *structured-summary template* — Goal/Constraints/Progress/Decisions/Files/Next/Critical — is a decent shape for a **resume/handoff note**, a minor ADAPT, overlaps #6.) | n/a |

---

## SINGLE HIGHEST-LEVERAGE IDEA

**Build Mimir a Curator (#3) + the budget-as-error discipline (#1), driven by a usage sidecar (#4).** Everything else is a refinement of these. Mimir's three named pains — unbounded growth, manual hygiene, drift — are *one* missing capability: **an autonomous, safe, time-decay + LLM-consolidation janitor over the memory dir, with a hard budget it's forced to respect.** Hermes has already built and shipped exactly this for skills; the transplant is "point the same machine at `MEMORY.md`-index + topic files + resume notes." The safety rails that make autonomous pruning *acceptable* (never-delete → recoverable archive, pre-run snapshot + one-command rollback, pinning of load-bearing notes, an audit REPORT.md) are the non-obvious, hard-won parts — adopt them verbatim, they're why the curator can be trusted to run unattended.

---

## HONEST READ — is Hermes's memory "very good" or overhyped?

**Verdict: genuinely good *for what it is*, and a near-perfect reference for Mimir specifically — but the goodness is in discipline, not sophistication.**

- **What's legitimately strong** `[verified-in-source]`: the **bounding model** (hard budget + error-on-overflow + forced in-turn consolidation) is the cleanest answer to unbounded-growth I've seen stated this plainly — it refuses to silently lose data *and* refuses to grow. The **Curator** is a mature, safety-railed (snapshot/rollback/pin/never-delete/audit-report) autonomous-hygiene system that has clearly absorbed real production lessons (the inactivity gate, first-run deferral, protected built-ins, the rename map all read as scar tissue from real incidents). The **edit-in-place + dedup + dumb-file/sidecar-metadata** combination structurally prevents whole classes of drift. The **bounded-hot / unbounded-cold split** is the right architecture.
- **What's plain, not fancy:** the built-in tier is **two flat text files with `§` delimiters and no embeddings**. That's a feature (cheap, debuggable, no vector infra) but it's not the "AI-native memory" the marketing gestures at — the *semantic/graph/dialectic* sophistication is **entirely in optional external providers** (Honcho et al.), which are infra-heavy and which most users likely never enable.
- **The one real gap:** no **active reconciliation against reality** — nothing re-checks that a stored fact is still true (a recorded path/version going stale isn't auto-detected). Drift defense is structural + LLM-review, not world-grounded. (Mimir shares this gap; worth noting, not solved here.)
- **Marketing vs substance:** the landing page's *"never forgets how it solved a problem"* / "AI-native memory" framing is **mild overhype** — the durable built-in memory is deliberately *forgetful by budget* and decidedly non-AI-native; the impressive engineering is in the *curation discipline*, not the recall tech. For Mimir's purposes that's exactly the right kind of good: **the transferable value is the discipline, and it transfers almost 1:1 because Mimir already uses the same MEMORY.md/USER.md substrate.**

---

## OPEN QUESTIONS (for the lead to resolve with the user)

1. **Curator trigger on CC.** Hermes uses an inactivity-gated daemon-ish tick. Mimir has no daemon. Should the memory-curator fire from a CC **`SessionStart`/`Stop` hook**, a **scheduled routine** (subscription-safe via subagent, not `claude -p`), or a **manual `/curate-memory`**? Each has different autonomy/cost trade-offs. `[ASSUMPTION made in mapping: a fired-and-returned Hand or hook-triggered subagent; needs Tim's call.]`
2. **Frontmatter: move out, or enforce-don't-restate?** Mapping #5 offers two fixes for the body-vs-frontmatter drift. Hermes's actual design (no frontmatter in body; metadata in sidecar) is the cleaner one but is a bigger migration of existing topic files. Which does Tim want?
3. **Budget numbers.** Hermes picked 2,200 / 1,375 chars empirically. What's the right hard budget for Mimir's *index* and `USER.md`? (Mimir's index is already larger than Hermes's whole memory store — so the cold-tier split #2 matters more than the raw number.)
4. **Decay windows.** Hermes uses 30d→stale, 90d→archive. Mimir's notes have very different half-lives (a PRINCIPLES record never goes stale; a "RESUME HERE" note is stale in days). Decay almost certainly needs a **per-`type` window** (the `type` frontmatter Mimir already has could drive it) + liberal **pinning**.
5. **Does Mimir even want a separate cold tier, or is grep-over-topic-files enough?** #2/#10 assume CC's native search is the cold tier. Worth confirming that's sufficient vs. anything more structured.

---

*All Hermes claims in this document are tagged with the on-disk source file under `/tmp/hermes-study/` (downloaded from the live repo on 2026-06-15) or marked `[inferred]`. The landing page contributed no memory substance; everything load-bearing came from the repo docs + the actual Python source.*
