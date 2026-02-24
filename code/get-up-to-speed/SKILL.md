---
name: get-up-to-speed
description: >-
  Reviews the latest git history, branch state, Linear ticket, and open work
  to build a concise situational summary. Use when picking up work after
  another agent, resuming a session, or onboarding to a branch mid-flight.
argument-hint: [AIS-XXXX | extra context]
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - AskUserQuestion
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_comments
  - mcp__claude_ai_Linear__get_project
---

# Get Up to Speed

Quickly build situational awareness for a branch/ticket so work can continue without re-reading everything.

## Preferences

_On startup, use the Read tool to load `~/.claude/skills/get-up-to-speed/preferences.md`. If it doesn't exist, use defaults._

## Context

_On startup, use Bash to detect: current git branch, repo root, and git remote URL. Skip any that fail._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete preferences file, confirm, stop
- **`AIS-XXXX`** — if argument looks like a Linear issue ID, use it as the ticket
- **anything else** — treat as extra context to include in the summary
- **empty** — auto-detect ticket from branch name

### Help

```
Get Up to Speed — Situational summary of branch, git history, and ticket

Usage:
  /get-up-to-speed                      Auto-detect ticket from branch name
  /get-up-to-speed AIS-1043             Specify a ticket explicitly
  /get-up-to-speed "extra context"      Add context for the summary
  /get-up-to-speed config               Set preferences
  /get-up-to-speed reset                Clear preferences
  /get-up-to-speed help                 This help

Examples:
  /get-up-to-speed                      Summarize current branch + ticket
  /get-up-to-speed AIS-810              Summarize with a specific ticket
  /get-up-to-speed "focus on the settings panel changes"

Current preferences:
  (read from preferences.md)
```

### Config

Use `AskUserQuestion` to collect:

- **Q1: Summary depth** — "Brief" (last 10 commits, ticket title) or "Detailed" (last 30 commits, ticket description, comments, plan file)
- **Q2: Auto-read plan files** — Yes/No — whether to check `.claude/plans/` for active plans

Save to `~/.claude/skills/get-up-to-speed/preferences.md`.

### Reset

Delete `~/.claude/skills/get-up-to-speed/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, proceed with defaults:
- Summary depth: Detailed
- Auto-read plan files: Yes

## Workflow

### 1. Detect branch and ticket

Use Bash to get:
```bash
git branch --show-current
git remote get-url origin
```

Extract the Linear ticket ID from the branch name. Pattern: `*/ais-{number}-*` → `AIS-{number}`.

If `$ARGUMENTS` contains an `AIS-XXXX` pattern, use that instead.

If no ticket ID found, note it and continue without Linear data.

### 2. Gather git state

Run these in parallel:

- **Recent commits** — `git log --oneline -20` (or -30 for detailed mode)
- **Uncommitted changes** — `git status --short`
- **Diff stats** — `git diff --stat` (unstaged) and `git diff --cached --stat` (staged)
- **Branch divergence** — `git log --oneline main..HEAD` to see what's unique to this branch
- **Latest commit details** — `git log -1 --format="%H%n%s%n%b"` for the most recent commit message and body

### 3. Fetch Linear ticket

If a ticket ID was found, use the Linear MCP tools:

1. **Get the issue** — `mcp__claude_ai_Linear__get_issue` with the issue ID
2. **Get recent comments** — `mcp__claude_ai_Linear__list_comments` for the issue

Extract: title, status, description summary, assignee, project, and last 3-5 comments.

If Linear tools aren't available or the call fails, skip gracefully.

### 4. Check for plan files

If auto-read plans is enabled, check for active plan files:

```bash
ls -t .claude/plans/*.md 2>/dev/null | head -3
```

If a plan file exists, read it and note its status (complete, in-progress, pending).

### 5. Check memory and project context

Read these if they exist (skip if not found):
- Project `CLAUDE.md` — scan for relevant sections
- Auto-memory `MEMORY.md` — check for notes related to the current branch or ticket

Don't dump the full contents — just extract what's relevant to the current branch/ticket.

### 6. Read extra context

If `$ARGUMENTS` contained extra context (not a ticket ID, not a subcommand), incorporate it as a focus area for the summary.

### 7. Synthesize and present

Output a structured summary in this format:

```markdown
## Up to Speed: [branch-name]

**Ticket:** [AIS-XXXX — Title] ([Status])
**Project:** [Project name]
**Branch:** `branch-name` — [N commits ahead of main]

### What's been done
- [Bullet summary of completed work from commits + ticket description]
- [Group related commits into logical chunks, not 1:1 commit list]

### Current state
- [Uncommitted changes if any]
- [What the last few commits were doing — the trajectory]
- [Active plan file summary if exists]

### What's pending
- [Open items from ticket description/checklist]
- [Unresolved comments from Linear]
- [Any items flagged in plan as not yet started]

### Key files touched
- [List of most-changed files from git log, grouped by feature area]

### Context notes
- [Relevant memory entries]
- [Extra context from arguments]
- [Any warnings: merge conflicts, stale branch, failing checks, etc.]
```

Keep it concise — this is a briefing, not a novel. Focus on what someone needs to know to start working RIGHT NOW.

## Principles

- **Read-only** — never modify files, branches, or tickets. Only observe and report.
- **Fast over thorough** — better to give a useful summary in 15 seconds than a perfect one in 2 minutes. Skip slow operations.
- **Graceful degradation** — if Linear is unavailable, git is weird, or files are missing, skip that section and note it. Never fail completely.
- **Group, don't list** — synthesize commits into logical work chunks ("built the settings panel with 6 sections") instead of listing every commit message.
- **Highlight blockers** — if there are uncommitted changes, merge conflicts, or the branch is behind main, call it out prominently.
