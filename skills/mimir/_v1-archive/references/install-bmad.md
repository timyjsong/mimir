# BMAD install procedure

Read this when the "BMAD not installed" startup case in SKILL.md fires and the user has confirmed the install folder.

## The install command

Install is a one-shot shell command, not a BMAD workflow. **The lead runs it directly via Bash with `run_in_background: true`** — no worker needed. (Workers exist for BMAD/loki workflows; install is bootstrap, not a workflow.)

Command:

```
npx -y bmad-method install --yes --modules bmm --tools claude-code --directory <absolute-project-path>
```

Substitute:
- `<absolute-project-path>` — the user-confirmed absolute path (e.g. `/home/tim/projects/my-project`).

Flag meanings:
- `-y` (on `npx`) — suppress the package-resolve confirmation.
- `--yes` (on `bmad-method install`) — suppress the installer's interactive prompts; we already gated on user confirmation.
- `--modules bmm` — install the Build/Make/Maintain module. Product-development core (brief, PRD, architecture, epics/stories, readiness). Default for general use. Power users wanting `bmb` (module authoring) or `cis` (creative workflows) can install them outside this skill.
- `--tools claude-code` — register the project-scoped `bmad-*` skills under `.claude/skills/` so Claude Code picks them up.
- `--directory` — target the install at the specified folder.

## Why Bash, not a worker

The install:
- Runs once and exits
- Doesn't read `_bmad/` (doesn't exist yet)
- Doesn't run a `bmad-*` skill
- Doesn't produce structured content to relay back

A worker would add ceremony (team-member slot, handoff file pattern, retirement) for no benefit. Bash with `run_in_background: true` is sufficient: lead doesn't block, gets a completion notification, then verifies on disk.

Note: team creation is deferred until *after* install completes, since the team name (`mimir-<project-slug>`) is derived from `_bmad/bmm/config.yaml` which doesn't exist until install finishes.

## Post-install verification

After the background Bash command completes, **you must verify the install on disk** before proceeding:

1. Confirm `_bmad/` exists at the project root.
2. Confirm `_bmad/bmm/config.yaml` exists and is readable.
3. If either is missing or malformed, the install failed — surface the npx output to the user with a clear "install didn't complete" message. Don't proceed to orientation.

## After successful verification — proceed via worker delegation (no restart)

The install wrote the `bmad-*` skills to `.claude/skills/`. Claude Code scans skills at **session startup**, so they are NOT loaded in *your* (the lead's) session — you can't invoke `bmad-help` or any `bmad-*` skill directly here. **But freshly-spawned workers re-scan `.claude/skills/` at spawn and CAN invoke them** (verified). Since mimir works entirely by delegating `bmad-*` work to fresh workers, the install flow proceeds **without a restart**:

1. **Skip your own `bmad-help`.** You don't need it — a fresh install is definitionally "installed, zero artifacts," and you just created that state. The next step is the product brief.
2. Create the team + claim latest (orientation step 6), then brief the user: "BMAD installed at `<path>`, fresh project — I'd start with the product brief. Proceed?"
3. On green-light, delegate to a fresh `bmad-worker` per `playbooks/bmad.md`. The worker rescans skills on spawn → it runs `bmad-product-brief` fine. No restart.
4. If you ever need `bmad-help` itself this session, delegate *that* to a worker too — your own session can't run it until a future startup, but a worker can.

(This relies on the verified fact that spawned workers rescan project skills. Defensive fallback: if a worker ever reports "skill not found" right after an install, tell the user to `/clear` + `/mimir`.)
