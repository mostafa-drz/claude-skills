---
name: docs-doctor
description: >-
  Audits a repository's documentation for unused docs, wrong details, missing
  coverage, inaccurate data, broken structure, and writing best-practices.
  Generates a markdown report (HTML optional) with severity ratings. Supports
  modes (main, comprehensive, focused, quick), per-profile templates
  (open-source, internal-docs, blog, nextjs-app), optional --fix for low-risk
  auto-fixes (broken links, frontmatter, stale dates), and a /feedback
  subcommand that promotes recurring signals into Learned defaults. Use when
  you want a "docs doctor" pass on a repo before a release, after a refactor,
  or as a recurring DX health check.
argument-hint: "[--mode=<main|comprehensive|focused|quick>] [--from-template=<name>] [--category=<key>] [--scope=<key,...>] [--fix] [--html] [help|config|reset|feedback|templates|resume]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebFetch
---

# Docs Doctor

Audit a repository's documentation like a doctor: triage what's missing, wrong, stale, structurally broken, or written badly. Produce a severity-ranked report; optionally apply low-risk fixes. Configurable by mode, scope, and template profile. Learns from your feedback over time.

## Preferences

_On startup, use the `Read` tool to load `~/.claude/skills/docs-doctor/preferences.md`. If missing, treat as "no preferences set" and continue with Defaults below._

## Context

_On startup, use the `Bash` tool to detect: git repo root (`git rev-parse --show-toplevel`), current branch, and whether `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` is present (for code-doc check selection). Use the `Glob` tool to list `**/*.md`, `**/*.mdx`, and any `CLAUDE.md` / `AGENT.md` files. Skip any detection step that fails — do not abort._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help, then stop
- **`config`** → interactive setup, then stop
- **`reset`** → delete `~/.claude/skills/docs-doctor/preferences.md`, `feedback-journal.md`, `sessions/`, `resume-state.md`, confirm, stop
- **`feedback`** → run the feedback flow (see § Feedback & learning), then stop
- **`templates`** → list available templates from `~/.claude/skills/docs-doctor/templates/`, then stop
- **`resume`** → if `resume-state.md` exists, continue the last interrupted run; else say `No session to resume.`
- **`--from-template=<name>`** → load template, merge with flags, run
- **anything else** (including empty) → run the audit

### Help

```
Docs Doctor — audits repository documentation and produces a severity-ranked report

Usage:
  /docs-doctor                                  Interactive audit (asks for mode)
  /docs-doctor --mode=main                      Default audit (6 core categories)
  /docs-doctor --mode=comprehensive             Adds link-check, code-doc drift, freshness vs git
  /docs-doctor --mode=quick                     Smoke check (broken links + frontmatter + stale dates)
  /docs-doctor --mode=focused --category=missing-docs
                                                Run a single category
  /docs-doctor --from-template=nextjs-app       Use a preset profile
  /docs-doctor --scope=markdown,frontmatter     Limit doc types audited
  /docs-doctor --fix                            Apply low-risk auto-fixes after report
  /docs-doctor --html                           Also emit interactive HTML report
  /docs-doctor templates                        List available templates
  /docs-doctor feedback                         Rate the most recent session
  /docs-doctor resume                           Continue an interrupted run
  /docs-doctor config                           Set preferences
  /docs-doctor reset                            Clear preferences + journal + sessions
  /docs-doctor help                             This help

Categories (for --category):
  unused-docs, wrong-details, missing-docs, inaccurate-data,
  missing-structure, best-practices

Current preferences:
  (loaded from ~/.claude/skills/docs-doctor/preferences.md)
```

### Config

Use `AskUserQuestion` to collect:

- **Q1** — Default mode: `main` / `comprehensive` / `quick`
- **Q2** — Default scope (multiSelect): markdown, frontmatter, code-docs, agent-instructions
- **Q3** — Default output: markdown / html / both
- **Q4** — Severity threshold (what's shown in report): `info+` / `warn+` / `error-only`
- **Q5** — Fix policy: `never` (report only) / `interactive` (ask per fix) / `auto-low-risk` (apply allowed fixes without prompt)
- **Q6** — Ignored path globs (comma-separated, e.g. `node_modules/**, vendor/**, .next/**`)

Write to `~/.claude/skills/docs-doctor/preferences.md` in the three-tier format (see § Preferences file format below).

### Reset

Use the `Bash` tool to delete the skill's state files:
- `~/.claude/skills/docs-doctor/preferences.md`
- `~/.claude/skills/docs-doctor/feedback-journal.md`
- `~/.claude/skills/docs-doctor/sessions/`
- `~/.claude/skills/docs-doctor/resume-state.md`

Confirm: `State cleared. Using defaults next run.`

## First-time detection

If `preferences.md` does not exist:

> First time using `/docs-doctor`? Run `/docs-doctor config` to set defaults, or continue with sensible defaults (mode=main, scope=markdown+frontmatter+agent-instructions, output=markdown, severity=warn+, fix=never).

Then proceed.

---

## Defaults

- mode: `main`
- scope: `markdown, frontmatter, agent-instructions`
- output: `markdown`
- severity threshold: `warn+`
- fix policy: `never`
- ignored paths: `node_modules/**, vendor/**, dist/**, build/**, .next/**, .turbo/**, coverage/**`

## Workflow

### Step 0 — Load learning context

1. `Read` `~/.claude/skills/docs-doctor/preferences.md` — apply Defaults / Profile / Learned in that order (Learned wins).
2. `Read` `~/.claude/skills/docs-doctor/feedback-journal.md` — note any recurring `Signal:` lines to bias severity and category emphasis.
3. If either file is missing, continue silently with Defaults.

### Step 1 — Resolve run config

1. Parse flags from `$ARGUMENTS`.
2. If `--from-template=<name>`: `Read` `~/.claude/skills/docs-doctor/templates/<name>.md`, merge template values under flags (flags override template).
3. If `--mode` is unset and not in preferences: use `AskUserQuestion` to pick mode. Pre-select the `Learned` mode if one exists, else `main`.
4. If `--category` is set but `--mode` is not `focused`, set `--mode=focused`.
5. Compute final config object: `{ mode, scope, output, severity_threshold, fix_policy, ignored_paths, categories, target_files }`.

### Step 2 — Discover docs

1. Use `Glob` to enumerate candidate files based on scope:
   - `markdown`: `**/*.md`, `**/*.mdx`
   - `frontmatter`: subset of markdown that starts with `---`
   - `code-docs`: `**/*.{ts,tsx,js,jsx,py,rs,go}` (filter by detected project type)
   - `agent-instructions`: `**/CLAUDE.md`, `**/AGENT.md`, `**/AGENTS.md`
2. Remove anything matching `ignored_paths`.
3. If zero files: stop with `No docs found in scope. Check --scope or --ignored.`

### Step 3 — Run checks

For each enabled category, run the corresponding checks defined in `reference/checks.md`. Categories enabled by mode:

| Mode          | Categories                                                                                          |
|---------------|-----------------------------------------------------------------------------------------------------|
| quick         | wrong-details (broken-links subset), missing-structure (frontmatter only), inaccurate-data (dates) |
| main          | all 6 core: unused-docs, wrong-details, missing-docs, inaccurate-data, missing-structure, best-practices |
| comprehensive | main + freshness-vs-git, external-link-check, code-doc-drift, onboarding-flow, search-ability      |
| focused       | only the category passed via `--category`                                                            |

Each check returns findings with: `{ file, line?, category, severity, rule, message, suggested_fix? }`.

Run checks in parallel where independent (e.g. file-level reads can batch). Use `Grep` for pattern checks across files, `Read` for per-file inspection. Defer external network checks (`WebFetch`) to last; cap to 25 URLs per run unless `--mode=comprehensive`.

### Step 4 — Score and rank

1. Apply severity rules from `reference/severity.md`.
2. Filter out findings below `severity_threshold`.
3. Sort by severity (error → warn → info), then by category, then by file.
4. Compute summary counts: total, by severity, by category.

### Step 5 — Write report

1. Create `<repo>/.docs-doctor/` if missing. Ensure it's in `.gitignore` (offer to add if not).
2. Write markdown report to `<repo>/.docs-doctor/report-<YYYY-MM-DD-HHMM>.md` with sections:
   - Header (mode, scope, severity threshold, ignored paths)
   - Executive summary (counts, top 5 issues)
   - Findings grouped by category, each with severity badge, file:line, rule, message, suggested fix
   - Fix plan (if `--fix` requested)
3. If `--html` or output preference is `html`/`both`, also write `<repo>/.docs-doctor/report-<ts>.html` — single-file HTML with chip filters per severity/category (matches Decision Report pattern: hero summary, inline JS filters, gray-out-on-change).
4. Save session log: `~/.claude/skills/docs-doctor/sessions/<YYYY-MM-DD-HHMM>.md` with: config used, counts, top findings, decisions taken, follow-ups.

### Step 6 — Optional `--fix` pass

If `--fix` was passed and `fix_policy ≠ never`:

1. Filter findings to those with `suggested_fix` AND rule in the auto-fixable allowlist:
   - `broken-internal-link`
   - `frontmatter-missing-required` (only safe defaults)
   - `frontmatter-key-disorder`
   - `stale-last-updated`
2. If `fix_policy = interactive`: for each fix, show diff via `AskUserQuestion` (Apply / Skip / Apply all remaining).
3. If `fix_policy = auto-low-risk`: apply all allowlisted fixes without prompting; record them in the report.
4. Use `Edit` for file changes. Never `Write` over a file unless creating a new doc the user approved.
5. After all fixes, re-run only the touched checks to confirm.
6. Append a "Fixes applied" section to the report.

Destructive or wide-blast fixes (deleting whole docs, rewriting paragraphs) are never auto-applied — always require explicit confirmation.

### Step 7 — Final summary

Print to chat:
```
Docs Doctor: <mode> mode on <N> files
  Errors: X · Warnings: Y · Info: Z
  Top issues: <one-liners for top 3>
  Report: .docs-doctor/report-<ts>.md
  Fixes applied: <count>  (if --fix)
```

Then ask via `AskUserQuestion`:
- **Open report?** Yes / Open in browser (HTML) / No

### Step 8 — Invite feedback

End with one line:

> Run `/docs-doctor feedback` — even one rating helps me sharpen severity and category emphasis for this repo.

---

## Templates

Templates live in `~/.claude/skills/docs-doctor/templates/<name>.md`. Each template declares default flags as YAML frontmatter:

```yaml
---
name: <template-name>
description: <one-liner>
inputs: { mode, scope, severity_threshold, fix_policy }
tasks: [ordered-check-keys]
constraints: [rules]
ignored_paths: [globs]
postProcesses: [open-report, append-to-changelog]
---
```

Loading: when `--from-template=<name>` is passed, `Read` the file, parse the frontmatter, merge values under the workflow config (CLI flags still win).

Shipped templates:

- `open-source.md` — emphasises README, CONTRIBUTING, LICENSE, public API docs
- `internal-docs.md` — emphasises onboarding, runbooks, ADRs
- `blog.md` — content-first: frontmatter completeness, broken images, draft markers, dates
- `nextjs-app.md` — Next.js conventions: route-level docs, app/page coverage, CLAUDE.md sanity

To add a template: drop a new file in `templates/` matching the schema above. List them via `/docs-doctor templates`.

## Preferences file format

```markdown
# /docs-doctor preferences
Updated: YYYY-MM-DD

## Defaults
- mode: main
- scope: markdown, frontmatter, agent-instructions
- output: markdown
- severity_threshold: warn+
- fix_policy: never
- ignored_paths: node_modules/**, dist/**, .next/**

## Profile (optional — edit freely)
- (user-editable lines: bias which categories matter, custom severity per repo)

## Learned
- (populated from feedback; promoted after 3+ consistent signals)
```

## Feedback & learning

When invoked as `/docs-doctor feedback`:

1. Find the most recent `~/.claude/skills/docs-doctor/sessions/<YYYY-MM-DD-HHMM>.md`. If none, say `No recent session found.` and stop.
2. Print a one-line summary of that session (mode, file count, top issues).
3. Ask via `AskUserQuestion` in one batch (4 questions):
   - **Category usefulness** (multiSelect): which categories were signal vs noise?
   - **Severity calibration**: too strict / about right / too lenient
   - **Auto-fix accuracy** (only if `--fix` was used): all correct / some wrong / no fixes applied
   - **Output format preference**: keep markdown / prefer HTML / want both / want shorter summary
4. Append to `~/.claude/skills/docs-doctor/feedback-journal.md`:
   ```
   ## <session slug> — <YYYY-MM-DD>
   - Mode: <mode>
   - Useful categories: <list>
   - Noisy categories: <list>
   - Severity calibration: <answer>
   - Auto-fix accuracy: <answer>
   - Output preference: <answer>
   - Signal: <one-line generalisation of the takeaway>
   ```
5. **Promotion rule:** when 3+ sessions share the same `Signal:`, promote it to `## Learned` in `preferences.md` and tell the user once: `Noticed you consistently <signal>. Saved as standing default.`
6. **Drift correction:** when a `Learned` rule is contradicted in 2 newer sessions, demote it back to inactive and log the demotion in the journal as `Signal: demoted "<rule>" — contradicted by <session-1>, <session-2>`.

## Principles

1. **Manifest first** — every audit run produces a report file; the conversation is the index, not the source of truth.
2. **Graceful degradation** — missing preferences / journal / templates never block a run; fall back to Defaults silently.
3. **Learn quietly** — promote a rule only after 3+ consistent signals; mention once, never twice.
4. **No fabricated structure** — if scope or mode is ambiguous, ask via `AskUserQuestion` rather than invent.
5. **Destructive actions need confirmation** — auto-fix is gated to a strict allowlist; anything else asks first.
6. **Stop means stop** — if the user halts mid-audit, write `resume-state.md` with progress so `/docs-doctor resume` can continue.
7. **Skill orchestrates, does not re-judge** — when fixing, preserve user-authored content; never rewrite prose silently.
8. **Detail lives in reference/** — keep this SKILL.md under 500 lines; deep check definitions live in `reference/checks.md` and `reference/severity.md`.
