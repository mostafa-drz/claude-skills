---
name: git-cleanup
description: >-
  Identifies and removes stale git branches, orphaned remote branches, and
  unused worktrees. Cross-references with Linear (or other integrations) to
  check issue status before deleting. Use when your repos have accumulated
  stale branches and you want to tidy up.
argument-hint: [repo-path or natural language instructions]
disable-model-invocation: true
context: fork
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_projects
---

# Git Cleanup

Intelligently identify and remove stale branches, orphaned remotes, and unused worktrees — with confirmation at every step.

## Preferences

Before starting, use the `Read` tool to read `~/.claude/skills/git-cleanup/preferences.md`. If the file does not exist, treat as "no preferences set".

## Context

- Working directory: !`echo $PWD`
- Git repos in cwd: !`ls -d */ 2>/dev/null | while read d; do [ -d "$d/.git" ] && echo "$d"; done | tr '\n' ', '`
- Current repo branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/git-cleanup/preferences.md`, confirm, stop
- **anything else** → parse as natural language or repo path, then run

### Help

```
Git Cleanup — Smart cleanup of stale branches, remotes, and worktrees

Usage:
  /git-cleanup                              Auto-detect repos, clean everything
  /git-cleanup ai-assemble                  Clean a specific repo
  /git-cleanup just local branches          Natural language — local only
  /git-cleanup dry run                      Show what would be deleted
  /git-cleanup skip linear                  Skip Linear issue checks
  /git-cleanup ai-assemble remote only      Clean only remote branches
  /git-cleanup config                       Set preferences
  /git-cleanup reset                        Clear preferences
  /git-cleanup help                         This help

Smart detection:
  - If inside a git repo, uses that repo
  - If in a parent directory, scans for git repos and lets you pick
  - If one repo found, uses it automatically

Current preferences:
  (shown above under Preferences)
```

### Config

Use `AskUserQuestion` to collect:

- **Q1: Protected branches** — branches to never delete (default: `main, all-demos, develop`)
- **Q2: Linear integration** — Enable Linear issue status checks? (default: Yes)
- **Q3: Ticket pattern** — regex to extract ticket IDs from branch names (default: `AIS-\d+`)
- **Q4: Auto-confirm merged** — Auto-delete branches already merged into base? (default: No — always ask)

Save to `~/.claude/skills/git-cleanup/preferences.md`.

### Reset

Delete `~/.claude/skills/git-cleanup/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:

> First time using /git-cleanup? Run `/git-cleanup config` to set defaults, or just continue with sensible defaults.

Then proceed with defaults:
- Protected branches: `main`, `all-demos`, `develop`
- Linear integration: enabled
- Ticket pattern: `AIS-\d+`
- Auto-confirm merged: no

## Workflow

### Step 1: Parse arguments and find repos

Parse `$ARGUMENTS` as natural language. Extract:
- **Repo path** — explicit path, or auto-detect
- **Scope modifiers** — "local only", "remote only", "worktrees only"
- **Dry run** — "dry run", "preview", "just show"
- **Skip integrations** — "skip linear", "no linear", "no ticket check"

**Smart repo detection:**
1. If `$ARGUMENTS` contains a path or directory name → use it
2. If currently inside a git repo (`.git` exists) → use current directory
3. If in a parent directory → scan child directories for `.git`
   - If exactly one repo found → use it automatically
   - If multiple found → ask user which to clean (or "all")
   - If none found → error and stop

### Step 2: Gather git state

For each repo, collect:

```bash
# Protected branches (from prefs or defaults)
PROTECTED="main|all-demos|develop"

# Local branches and their merge status
git branch --format='%(refname:short) %(upstream:track)'
git branch --merged main
git branch --merged all-demos

# Remote branches
git branch -r --format='%(refname:short)'

# Worktrees
git worktree list

# Stale remote tracking
git remote prune origin --dry-run
```

### Step 3: Categorize branches

Sort every branch into one of these categories:

**Safe to delete (green):**
- Local branches fully merged into a protected branch
- Local branches with `[gone]` upstream (remote deleted)
- Remote branches with no corresponding local branch AND no open PR

**Probably safe (yellow):**
- Branches matching a ticket pattern where the Linear issue is Done/Canceled/Duplicate
- Branches older than 90 days with no recent commits
- Worktrees pointing to branches in the "safe" category

**Needs review (red):**
- Branches with unmerged commits
- Branches matching a ticket pattern where the Linear issue is still open/in-progress
- The current branch (never auto-delete)
- Protected branches (never delete)

### Step 4: Check Linear context (unless skipped)

For branches matching the ticket pattern (e.g., `mostafa/ais-921-...` → `AIS-921`):

1. Extract ticket ID from branch name using the configured pattern
2. Use `mcp__claude_ai_Linear__get_issue` to fetch issue status
3. Map status:
   - **Done, Canceled, Duplicate** → "probably safe" (issue is closed)
   - **In Progress, In Review, Todo** → "needs review" (issue is active)
   - **Not found** → "needs review" (can't confirm)

Present the Linear context alongside each branch.

### Step 5: Present cleanup plan

Show a categorized summary:

```
Git Cleanup Plan — ai-assemble

SAFE TO DELETE (merged/gone):
  Local:
    - feature/old-thing          (merged into main)
    - fix/typo                   (remote gone)
  Remote:
    - origin/feature/old-thing   (no local, no PR)

PROBABLY SAFE (closed tickets):
  Local:
    - mostafa/ais-800-old-task   (AIS-800: Done ✓)
  Worktrees:
    - .pilot-worktree            (branch deleted)

NEEDS REVIEW:
    - mostafa/ais-922-refactor   (AIS-922: In Progress)

PROTECTED (never touched):
    - main, all-demos, develop
```

If `--dry-run` / "dry run" was specified, show this plan and stop.

### Step 6: Confirm and execute

Use `AskUserQuestion` to confirm each category:

**Q1:** "Delete N safe-to-delete branches?" → Yes all / Pick individually / Skip
**Q2:** "Delete N probably-safe branches?" → Yes all / Pick individually / Skip
**Q3:** "Any needs-review branches to delete?" → Pick individually / Skip all

For each confirmed deletion:
- Local branch: `git branch -d <branch>` (safe delete) or `git branch -D <branch>` if needed
- Remote branch: `git push origin --delete <branch>`
- Worktree: `git worktree remove <path>`
- Stale remotes: `git remote prune origin`

Report each deletion as it happens.

### Step 7: Report results

```
Git Cleanup Complete — ai-assemble

  Local branches deleted:   3
  Remote branches deleted:  2
  Worktrees removed:        1
  Stale remotes pruned:     yes

  Skipped (needs review):   2
  Protected:                3
```

## Extensibility

The skill is designed to work with any ticketing integration. The core pattern is:
1. Extract ticket ID from branch name using a configurable regex
2. Look up ticket status via an integration (Linear MCP, GitHub issues, Jira, etc.)
3. Map status to safe/unsafe categories

To add a new integration:
- Update config to allow selecting the integration type
- Add the appropriate MCP tools to `allowed-tools`
- Add a status lookup step in Step 4

## Principles

- **Never delete without confirmation** — every deletion is explicitly confirmed by the user, even "safe" ones (unless auto-confirm is configured).
- **Never touch protected branches** — main, all-demos, develop, and any configured protected branches are untouchable.
- **Context over heuristics** — prefer Linear/ticketing status over age-based heuristics when deciding if a branch is safe to delete.
- **Show the reasoning** — always explain WHY a branch is categorized as safe/probably-safe/needs-review.
- **Graceful without integrations** — if Linear is unavailable or skipped, fall back to git-only heuristics (merge status, remote tracking, age).
