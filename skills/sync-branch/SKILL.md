---
name: sync-branch
description: >-
  Merges one branch into another with conflict handling. Stashes work, updates both
  branches, merges, resolves conflicts preserving both sides, pushes, and restores state.
  Use when keeping a long-lived branch in sync with its upstream.
argument-hint: [source] [target] [--no-push] [--dry-run]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
---

# Sync Branch

Merge one branch into another, handling conflicts and preserving work in progress.

## Preferences

!`cat ~/.claude/skills/sync-branch/preferences.md 2>/dev/null || echo "_no preferences set_"`

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Status: !`git status --short 2>/dev/null || echo "clean"`
- Remote: !`git remote get-url origin 2>/dev/null || echo "no remote"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/sync-branch/preferences.md`, confirm, stop
- **anything else** → sync branches

### Flags

Parse from `$ARGUMENTS`:
- **`--no-push`** — merge locally, don't push
- **`--dry-run`** — show what would happen without executing
- **Positional args**: `$0` = source branch, `$1` = target branch

### Help

```
Sync Branch — Merge one branch into another

Usage:
  /sync-branch                          Merge default source into current branch
  /sync-branch <source>                 Merge source into current branch
  /sync-branch <source> <target>        Merge source into target
  /sync-branch --no-push <source>       Merge without pushing
  /sync-branch --dry-run <source>       Preview without executing
  /sync-branch config                   Set defaults
  /sync-branch reset                    Clear preferences
  /sync-branch help                     This help

Examples:
  /sync-branch main
  /sync-branch main all-demos
  /sync-branch --dry-run main feature/auth
  /sync-branch --no-push develop

How it works:
  1. Stashes uncommitted work (if any)
  2. Updates source and target branches from remote
  3. Merges source into target
  4. Resolves conflicts (preserving both sides)
  5. Pushes target (unless --no-push)
  6. Restores original branch and stash

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Default source branch?" (main (default), develop, custom)
**Q2** — "Auto-push after merge?" (Yes (default), No)
**Q3** — "Conflict resolution style?" (preserve-both (default) — keep changes from both sides, ask-each — show each conflict and ask, prefer-source — favor source branch, prefer-target — favor target branch)

Save to `~/.claude/skills/sync-branch/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /sync-branch? Run `/sync-branch config` to set defaults, or continue — I'll merge main into your current branch."

Then proceed.

## Steps

### 1. Resolve branches

- **Source**: `$0` if provided, else saved default, else `main`
- **Target**: `$1` if provided, else current branch
- **Direction**: Always source → target

If source == target, error and stop.

### 2. Dry run check

If `--dry-run`:
```
git fetch origin
git log {target}..origin/{source} --oneline
```
Show what commits would be merged, then stop.

### 3. Stash uncommitted work

If working tree is dirty:
```
git stash --include-untracked
```
Record that a stash was created.

Record which branch the user was on originally.

### 4. Update source

```
git checkout {source}
git pull origin {source}
```
If pull fails → restore state, report error, stop.

### 5. Update and merge into target

```
git checkout {target}
git pull origin {target}
git merge {source} --no-edit
```

### 6. Handle conflicts

If merge reports conflicts:

1. List conflicts: `git diff --name-only --diff-filter=U`
2. Based on conflict resolution preference:
   - **preserve-both**: Read each file, resolve keeping both sides
   - **ask-each**: Show conflict to user via `AskUserQuestion`, let them decide
   - **prefer-source/target**: Auto-resolve favoring chosen side
3. `git add` each resolved file
4. `git commit --no-edit`

### 7. Push

Unless `--no-push` or preference says no:
```
git push origin {target}
```

### 8. Restore state

1. Checkout original branch (if different from target)
2. If stash was created: `git stash pop`

### 9. Report

```
Synced {source} → {target}

  {source}:  {short sha} {subject}
  {target}:  {short sha} {subject}
  Conflicts: {count} ({file list} or "none")
  Pushed:    {yes/no}
```

### 10. Learn

If user changes source branch, save preference.
If user changes conflict style, save preference.
