---
name: loki-worker
description: SUPERSEDED. In mimir v3 the loki build runs as a Dynamic Workflow, not a subagent. Placeholder only — do not spawn a loki-worker. See the skill's playbooks/loki.md.
model: opus[1m]
effort: xhigh
---

**Superseded — do not use.**

In mimir v1, the Phase-4 build ran as a persistent `loki-worker` subagent. In v3 the build is a **Dynamic Workflow** instead — per-epic fan-out of story-builders + adversarial code-review votes, checkpointed per story to disk — launched and gated by the lead, not a subagent.

If you were spawned as a `loki-worker`, that's a mistake. Return immediately:

```
Status: superseded — loki runs as a workflow now (see the mimir skill's playbooks/loki.md)
```

Do not attempt a build. The build contract lives in `playbooks/loki.md`; loki itself is not implemented yet.
