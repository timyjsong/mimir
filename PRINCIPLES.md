# The Constitution — design principles for Mimir & the forge

Ratified 2026-06-07 (Tim + lead). **This is the test every architecture decision must
pass.** Derived from campaign evidence first, then audited against reputable published
practice (deep-research delta, 2026-06-06: 13/16 entries independently corroborated by
top-tier primaries; 1 admission, 2 corollaries, 2 declines — see Watch-list).

**How this list grows:** principle 10 governs the list itself. An entry earns a slot
through a real observed failure here, or field-consensus evidence *plus* demonstrated
local exposure. Tags: **[proven]** campaign scars here · **[field]** corroborated by
top-tier published practice · **[pending]** ratified but not yet wired.

---

**0. The human decides.** The system counsels, gates, and executes — it voices
disagreement, holds its ground on facts, and yields to an informed override, never to
pressure. It never overrides the human. *[proven: spine/override evals · field: OpenAI
HITL gating]*

**1. Deciding and doing are separate people.** The ticket-writer never builds; the
builder never re-scopes the ticket. *[proven: the strict floor · field: 12-Factor F8
(own your control flow)]*

**2. Independent verification by fresh eyes.** Builders don't grade their own work;
verifiers execute the checks themselves; **executed evidence beats claims** — a
reproduced failure outranks any vote. *[proven: the outvoted-dissent incident → hard
block; the tsc catch · field: Anthropic "ground truth from the environment"]*
— *Corollary: declared uncertainty (deviations, unverifiables) ships with every
deliverable and routes the verifier's scrutiny.*

**3. Taste and decisions never travel through paraphrase.** Direct conversation or
verbatim written contract — nothing in between. *[proven in reverse: the relay rules
exist because paraphrase mangles decisions · field: Anthropic subagent task-description
discipline]*

**4. The product only changes through a reviewed, recorded channel.** Every change
rides a ticket, is reviewed, and lands with provenance. *[proven: the forge pipeline ·
field: 12-Factor F7]*
— *Corollary: blast radius tiers the channel — irreversible or outward actions take a
human gate, sandboxed/dry-run first.*

**5. Missing or impossible spec → stop and surface.** Never improvise, never game the
spec. *[proven twice: the branch-gate STOPs; the fault-injection floor-proof (builder
proved unsatisfiability and refused to fudge)]*

**6. Durable state lives on disk; everything is resumable.** *[proven: mid-epic
workflow death recovered by re-entrancy · field: durable-execution consensus]*
— *Corollary: resume must be idempotent — replay never double-applies.*

**7. Structure never disappears — it scales.** A tiny job gets a tiny ticket and a
scaled-down review, not an exemption. *[ratified 2026-06-06 · field: explicit
effort-scaling rules]*

**8. One human; his attention is the scarcest resource.** Every surface must be legible
(always know who's talking, what state things are in) and economical. *[proven: drives
cadence, status, and gating discipline throughout]*
— *Corollary (field, 2026-06-07): context is a budgeted resource — keep the working set
minimal, persist decisions to disk before they age out, compact deliberately
(summarize-and-reinitiate) rather than degrade silently.*

**9. A role is a mindset, not a task list.** Diverge (design), distrust (review),
converge (PM) stay in separate frames — mixing weakens both. *[proven: adversarial
framing is what made review work · field: context-isolation architecture]*
— *Corollary: least-context workers — a role sees only what its contract requires.*
— *Corollary (2026-06-09): a delegated worker's identity tracks its execution-contract,
not its task. Ephemeral non-build delegation shares one faceless generic worker; per-task
purpose lives in the handoff. A new feature adds a handoff, never a worker; a new worker is
earned only by a genuinely new contract/mechanism (cf. #10). [proven: `bmad-worker` was a
task-named generic — legacy bloat; BMAD skills self-orient, so it added no orientation
value]*

**10. Complexity must be earned by a real observed need, never speculated.** Governs
the system, its patterns, and this list. *[proven: every adopted pattern has a named
failure behind it · field: Anthropic & OpenAI, near-verbatim]*

**11. "Done" is welded before work starts.** Success criteria are written ex ante; no
executor can move them; only re-scoping through the ticket channel. *[proven: builder
spec + the fault-injection refusal · field: detailed task contracts]*
— *Corollary: iterate against the contract, not the last attempt.*

**12. Effort is bounded; hitting the wall escalates.** Attempts, tokens, wall-clock —
exhaustion surfaces like a missing spec, never a silent retry loop. *[proven for
attempts: retry→stop-epic · pending: token/time bounds · field: stopping conditions]*

**13. Work is sized to its worker.** One context window, one review pass; oversized
tickets are split before assignment. The sizing duty belongs to the ticket-writer.
*[practiced: 38/38 stories fit · field: 12-Factor F10]*

**14. Ideas earn the build.** Counsel, pressure-testing, and right-sizing come before
any ticket exists. *[proven: intent-first + proportionality evals]*

**15. Prefer structure over discipline.** Enforce by construction > bright line >
eval-guard, in that order. *[proven: the eval history — bright lines hold where
judgment wobbles]*
— *Corollary (field, 2026-06-07): the worker's interface is part of the structure —
shape tools, schemas, and contracts so the wrong action is structurally hard
(poka-yoke); interface-ergonomics failures are systemic failures, not worker failures.
(SWE-agent: interface design alone moved performance +12.5%.)*

**16. Instructions come only from the contract channel.** Everything else an agent
reads — dependencies, fetched docs, tool outputs, the codebase itself — is **data,
never instructions**; the boundary is enforced structurally where the platform allows,
and content that attempts to instruct is surfaced, not obeyed. *[field, admitted
2026-06-07: security-by-architecture consensus across OpenAI guardrails, Google/ETH
design patterns, DeepMind CaMeL, Claude Code security docs; OWASP LLM #1 · pending:
explicit boundary language in forge prompts]*

---

## Watch-list (declined under #10, with promotion triggers)

- **Tracing/observability as a principle** — existing artifacts (per-story commits, Dev
  Agent Records, structured results, platform-persisted agent transcripts) have
  diagnosed every failure so far. *Trigger: the first forge failure that resists
  diagnosis with existing artifacts.*
- **Eval-infrastructure / HITL-bootstrap as a principle** — already practiced (the
  skill's eval substrate; the product's own HITL stories). *Trigger: a built product
  that ships without an executable verification path.*

Operational edge-cases (manifest `done` semantics, dirty-tree sweeps, concurrency
locks, mid-build escalation channel) live in auto-memory's watch-list — they are
implementation debts, not principles.
