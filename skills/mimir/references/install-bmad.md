# BMAD install procedure

Read this when the "BMAD not installed" startup case in SKILL.md fires and the user has confirmed the install folder.

## The install command

Install is a one-shot shell command. The lead runs it directly via Bash **in the foreground** (not backgrounded) — no worker.

**Run it foreground on purpose.** You must wait for the install to finish before doing anything (verify `_bmad/` on disk, then run the brief), so there's no value in backgrounding this one-time ~1-min step. It also matters for skill reload: a `PostToolUse` hook fires when the Bash *tool call completes* — for a foreground command that's after the install actually finishes (files on disk), so the auto re-scan sees the new skills. A backgrounded call "completes" the instant the job launches, which would fire the re-scan mid-install against a half-written `.claude/skills/`.

```
npx -y bmad-method install --yes --modules bmm --tools claude-code --directory <absolute-project-path>
```

- `<absolute-project-path>` — the user-confirmed absolute path.
- `--modules bmm` — the Build/Make/Maintain module (brief, PRD, architecture, epics/stories, readiness).
- `--tools claude-code` — registers the `bmad-*` skills under the project's `.claude/skills/`.

## Post-install verification

After the install command completes, verify on disk before proceeding:

1. `_bmad/` exists at the project root.
2. `_bmad/bmm/config.yaml` exists and is readable.
3. If either is missing or malformed, the install failed — surface the npx output with a clear "install didn't complete" message; don't proceed.

## After a successful install — skills load in-session, no restart

The `bmad-*` skills become invocable in **this same session — never a restart**. A fresh install creates a new top-level `.claude/skills/`, which passive skill-watching alone doesn't catch, so it needs an explicit re-scan — which happens one of two ways:

- **Automatic (this environment).** The foreground install (see "Run it foreground on purpose" above) fires the `PostToolUse Bash(npx *)` reload hook on completion, so the skills re-scan and are **already loaded** — just proceed.
- **Manual fallback.** If that hook isn't present, have the user run **`/reload-skills`** once. Last resort if neither is available: relaunch `claude` in the project (a fresh startup scans the new skills).

Then go straight to standard procedure:

1. Read `_bmad/bmm/config.yaml`; confirm zero artifacts (it's a fresh install).
2. **Skip `bmad-help`.** A fresh install is definitionally zero-artifacts, so the next step is unambiguously the product brief — no need to run the just-installed help to be told that.
3. Gate the user — "BMAD installed at `<path>`, fresh project — I'd start with the product brief. What are you building?" — then run `bmad-product-brief` **in-session** (interactive elicitation — see SKILL.md → "Running a skill in-session"), honoring the cadence.

(Disk-grounded next-step discipline still applies to every step *after* the brief — `bmad-help` / `module-help.csv` once artifacts exist.)