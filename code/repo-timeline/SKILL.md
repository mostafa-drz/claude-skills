---
name: repo-timeline
description: >-
  Analyzes a repository or branch and generates a meaningful, engineer-friendly
  timeline of changes — grouping commits into logical units with short and
  detailed descriptions, using git history, changelogs, GitHub PRs, and Linear
  tickets. Use when you want to understand what changed, when, and why in a
  codebase.
argument-hint: "[branch] [--since \"time\"] [--focus \"areas\"] [--depth brief|detailed] [--sources git,github,linear]"
context: fork
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_comments
  - mcp__claude_ai_Linear__list_teams
  - mcp__claude_ai_Linear__get_user
---

# Repo Timeline

Visualize the history of a repository or branch as a meaningful, grouped timeline — not raw git log, but an engineer-friendly narrative of what changed, when, and why.

## Preferences

_On startup, use the Read tool to load `~/.claude/skills/repo-timeline/preferences.md`. If it doesn't exist, use defaults._

## Context

_On startup, use Bash to detect: current git branch, repo root (`git rev-parse --show-toplevel`), repo name (`basename $(git rev-parse --show-toplevel)`), remote URL (`git remote get-url origin`), and GitHub repo name (`gh repo view --json nameWithOwner -q .nameWithOwner`). Skip any that fail._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/repo-timeline/preferences.md`, confirm, stop
- **branch name** — if argument looks like a branch name (no `--` prefix), use it as the target branch
- **flags** — parse `--since`, `--until`, `--focus`, `--depth`, `--sources`
- **empty** — use current branch with defaults

### Flags

Parse from `$ARGUMENTS`:
- **`--since <time>`** — start of time range (e.g., "2 weeks ago", "2026-01-01", "last tag")
- **`--until <time>`** — end of time range (defaults to now)
- **`--focus <areas>`** — comma-separated paths or areas to emphasize (e.g., "api,auth,frontend")
- **`--depth brief|detailed`** — "brief" for one-liners, "detailed" for full descriptions (default from preferences)
- **`--sources <list>`** — comma-separated sources: git, github, linear, changelog (default: all available)

### Help

```
Repo Timeline — Engineer-friendly timeline of repository changes

Usage:
  /repo-timeline                              Current branch, full history
  /repo-timeline feature/auth                 Specific branch
  /repo-timeline --since "2 weeks ago"        Time-bounded timeline
  /repo-timeline --focus "api,auth"           Focus on specific areas
  /repo-timeline --depth brief                One-liners only
  /repo-timeline --depth detailed             Full descriptions with context
  /repo-timeline --sources git,github         Only specific sources
  /repo-timeline config                       Set preferences
  /repo-timeline reset                        Clear preferences
  /repo-timeline help                         This help

Flags:
  --since <time>          Start of time range (e.g., "1 month ago", "v2.0.0")
  --until <time>          End of time range (default: now)
  --focus <areas>         Comma-separated paths/areas to emphasize
  --depth brief|detailed  Level of detail (default: from preferences)
  --sources <list>        Sources to use: git, github, linear, changelog

Examples:
  /repo-timeline                              Full timeline of current branch
  /repo-timeline main --since "last month"    Main branch, last month
  /repo-timeline --focus "src/api" --depth detailed
  /repo-timeline --since "v1.0.0" --until "v2.0.0"   Between releases
  /repo-timeline develop --sources git,github

Current preferences:
  (read from preferences.md)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Default timeline depth?" (Brief — one-liner per group, Detailed — with descriptions and file lists, Auto — brief for large ranges, detailed for short)

**Q2** — "Which sources to include by default?" (multiSelect: true)
- Git (commits, tags, branches)
- GitHub (PR titles, descriptions, labels via `gh`)
- Linear (linked tickets and context via MCP)
- Changelog (CHANGELOG.md, HISTORY.md, release notes)

**Q3** — "Default time range?" (Full history, Last 30 days, Last sprint / 2 weeks, Since last tag/release)

**Q4** — "Grouping strategy?" (By time period — weekly/daily buckets, By topic — features/fixes/refactors, By release — between tags, Auto-detect)

Save to `~/.claude/skills/repo-timeline/preferences.md`.

### Reset

Delete `~/.claude/skills/repo-timeline/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:
"First time using /repo-timeline? Run `/repo-timeline config` to set defaults, or continue — I'll auto-detect the best settings."

Then proceed with defaults:
- Depth: auto
- Sources: all available
- Time range: full history (capped at 200 commits)
- Grouping: auto-detect

## Steps

### 1. Gather repo context and available sources

Detect available sources in parallel:

**Git (always):**
```bash
git rev-parse --git-dir
git branch --show-current
git tag --sort=-creatordate --format='%(refname:short) %(creatordate:short)' | head -10
```

**GitHub (check gh CLI):**
```bash
gh auth status 2>&1
```

**Linear (try MCP):**
Try `list_teams` to verify access. If it fails, skip gracefully.

**Changelog files:**
Use Glob to check for: `CHANGELOG.md`, `CHANGELOG`, `HISTORY.md`, `CHANGES.md`, `RELEASES.md`, `release-notes/`.

Report: `Sources available: Git, GitHub, Linear, Changelog` (or whichever are found).

If `--sources` flag is set, filter to only those.

### 2. Determine scope

Apply flags and preferences to determine:
- **Branch**: from argument or current branch
- **Time range**: from `--since`/`--until`, or preference default, or auto (full history capped at 200 commits)
- **Focus filter**: from `--focus` — will be used to filter/highlight relevant changes

If `--since` references a tag (e.g., "v1.0.0"), resolve it:
```bash
git log -1 --format=%ai v1.0.0
```

### 3. Collect raw data

#### Git history
```bash
git log [branch] --since="<time>" --until="<time>" --format="%H|%h|%ai|%an|%s|%b" --no-merges
git log [branch] --since="<time>" --until="<time>" --format="%H|%h|%ai|%an|%s" --merges
```

Also collect file-level stats:
```bash
git log [branch] --since="<time>" --until="<time>" --stat --format="%h"
```

And tags in range:
```bash
git tag --sort=creatordate --contains <start-commit> --no-contains <end-commit>
```

#### GitHub PRs (if available)
```bash
gh pr list --state merged --base <branch> --limit 50 --json number,title,body,labels,mergedAt,author,headRefName
```

If a time range is set, filter merged PRs within that window.

#### Linear tickets (if available)
Extract ticket IDs from commit messages and PR branch names (pattern: `AIS-\d+`, or configured prefix).

For each unique ticket ID found, fetch:
- `get_issue` — title, status, description
- `list_comments` — recent comments for context

#### Changelog (if available)
Read CHANGELOG.md or equivalent. Parse entries that fall within the time range.

### 4. Analyze and group

Cluster the raw data into meaningful groups. Strategy depends on preference or auto-detection:

**By topic (default for short ranges):**
- Analyze commit messages, PR titles, and file paths
- Group into categories: Features, Bug Fixes, Refactoring, Infrastructure, Documentation, Tests
- Within each category, sub-group by feature area (auth, API, frontend, etc.)

**By time period (default for long ranges):**
- Bucket into weeks or months depending on range length
- Within each bucket, sub-group by topic

**By release (when tags are present):**
- Group between consecutive tags
- Within each release, sub-group by topic

For each group:
- **Short summary**: one-line description of the group's changes
- **Long summary**: 2-3 sentence description with key details (if depth is detailed)
- **Key files**: most-changed files in this group
- **Contributors**: authors involved
- **Linked context**: PR numbers, Linear tickets, changelog entries

If `--focus` is set, highlight groups that match the focus areas and de-emphasize others.

### 5. Generate timeline

Produce the timeline in this format:

```markdown
## Timeline: [repo-name] / [branch]
Period: [start] — [end] | [N] commits | [N] contributors

---

### [Release Tag / Time Period / Topic Group]
_[date range]_ | [N commits] | by [authors]

**[Short summary — one line describing the group]**

[If detailed depth:]
[Long summary — 2-3 sentences with key details, linked PRs, tickets]

Key changes:
- [Bullet point per significant change]
- [PR #123 — title] [AIS-456]
- [File/area affected]

---

### [Next group...]
...

---

## Summary
- **Total**: [N] commits across [time range]
- **Contributors**: [list]
- **Focus areas**: [if --focus was used, show what matched]
- **Sources used**: Git, GitHub PRs, Linear tickets, Changelog
```

### 6. Present and offer drill-down

Display the timeline. Then offer follow-up options via **AskUserQuestion**:

- "Zoom into a specific period" — narrow the time range
- "Zoom into a specific area" — re-run with a focus filter
- "Show more detail on group N" — expand a specific group
- "Export as markdown" — (note: read-only skill, just output the raw markdown for copy)
- "Done" — finish

If the user picks a drill-down, re-run steps 3-5 with the narrowed scope and present again.

### 7. Learn

- If user consistently uses a specific depth, save as default
- If user always focuses on certain areas, note it
- If user prefers a specific grouping strategy, save it
- If user uses a specific time range pattern, save it

## Principles

- **Narrative over noise** — group and summarize. Never dump raw git log. An engineer should understand what happened by reading the timeline, not by decoding commit hashes.
- **Read-only** — never modify files, branches, or tickets. Only observe and report.
- **Graceful degradation** — if GitHub/Linear/changelog isn't available, produce the timeline from git alone. Always produce something useful.
- **Context-rich** — correlate commits with PRs, tickets, changelogs, and tags. The more connections, the more meaningful the timeline.
- **Respect focus** — when the user specifies focus areas, make those prominent and de-emphasize the rest. Don't filter out, just re-prioritize.
