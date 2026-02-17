---
name: create-pr
description: >-
  Creates a well-structured pull request with product-focused summary, change highlights,
  and test steps. Auto-detects base branch, links Linear issues from branch name, and
  pushes if needed. Use when ready to open a PR or when asking to create a pull request.
argument-hint: [issue-id] [--base branch] [--draft]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__update_issue
---

# Create PR

Create a well-structured, product-focused pull request.

## Preferences

!`cat ~/.claude/skills/create-pr/preferences.md 2>/dev/null || echo "_no preferences set_"`

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Upstream: !`git rev-parse --abbrev-ref @{upstream} 2>/dev/null || echo "no upstream"`
- Ahead: !`git rev-list --count @{upstream}..HEAD 2>/dev/null || echo "unknown"`
- Repo: !`gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "unknown"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/create-pr/preferences.md`, confirm, stop
- **anything else** (including empty) → create PR

### Flags

Parse from `$ARGUMENTS`:
- **`--base <branch>`** — override base branch
- **`--draft`** — create as draft PR
- **`--no-linear`** — skip Linear integration
- **Remaining text** — treated as Linear issue ID if it matches pattern (e.g., `AIS-810`)

### Help

```
PR — Create a well-structured pull request

Usage:
  /create-pr                         Create PR from current branch
  /create-pr<issue-id>               Create PR and link Linear issue
  /create-pr--base develop           Override base branch
  /create-pr--draft                  Create as draft
  /create-pr--no-linear              Skip Linear linking
  /create-prconfig                   Set PR preferences
  /create-prreset                    Clear preferences
  /create-prhelp                     This help

Examples:
  /pr
  /create-prAIS-810
  /create-pr--base develop --draft
  /create-prAIS-810 --base main

What it does:
  1. Detects base branch (or uses preference/flag)
  2. Reads commits, diff, and Linear issue
  3. Builds product-focused PR description
  4. Pushes branch if needed
  5. Creates PR and links to Linear

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Default base branch?" (auto-detect (default), main, develop, custom)
- Auto-detect: checks tracking branch, falls back to repo default branch

**Q2** — "Link Linear issues?" (Yes — from branch name (default), No)

**Q3** — "PR template?" (standard (default), minimal, detailed)

**Q4** — "Auto-push before creating?" (Yes (default), No — just create locally)

**Q5** — "Default PR type?" (Ready for review (default), Draft)

Save to `~/.claude/skills/create-pr/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /pr? Run `/create-prconfig` to set defaults (base branch, template, Linear linking), or continue — I'll auto-detect."

Then proceed.

## Steps

### 1. Gather context

**From git:**
- Current branch (pre-injected)
- Commits on this branch: `git log <base>..HEAD --oneline`
- Diff stat: `git diff <base>...HEAD --stat`
- Full diff summary: `git diff <base>...HEAD` (for understanding changes)

**Base branch detection** (in order):
1. `--base` flag if provided
2. Saved preference if set
3. Tracking branch upstream
4. Repo default branch: `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`

**Linear issue** (unless `--no-linear`):
- Extract issue ID from branch name (pattern: `user/ais-NNN-*` or `ais-NNN-*`)
- If found, fetch via `get_issue` for title, description, project

**Remote check:**
- Is branch pushed? If not, needs pushing.

### 2. Branch alignment

If a Linear issue was found, check if branch name matches `issue.gitBranchName`.
If mismatch, rename the branch to match (team convention):
```
git branch -m {old} {new}
git push origin --delete {old}  # if old was pushed
git push -u origin {new}
```

### 3. Push if needed

If branch isn't pushed (or was renamed):
```
git push -u origin {branch}
```

Skip if `--no-push` or preference says no.

### 4. Build PR content

**Title format:** Under 70 chars, conventional prefix.
- `feat: Description` for new features
- `fix: Description` for bug fixes
- `refactor: Description` for refactoring
- `chore: Description` for maintenance

**Body template (standard):**

```markdown
## Summary

{1-2 sentences: what this does and why. Product value first.}

**Linear:** [{issue-id}]({url}) (if available)

## What's New

- **{Feature/Change}** — {one sentence, user perspective}
- **{Feature/Change}** — {one sentence}

## How to Test

1. {Step}
2. {Step}
3. {Step}
```

**Body template (minimal):**

```markdown
{1-2 sentences: what and why}

Linear: [{issue-id}]({url})
```

**Body template (detailed):**

```markdown
## Summary

{1-2 sentences}

**Linear:** [{issue-id}]({url})

## What's New

- **{Feature}** — {description}

## Architecture

- {How it's structured}
- {What was reused}
- {Data flow}

## How to Test

1. {Step}
2. {Step}
```

### 5. Create the PR

```
gh pr create --base {base} --title "{title}" --body "$(cat <<'EOF'
{body}
EOF
)"
```

Add `--draft` if flag set or preference is draft.

### 6. Link to Linear

If Linear issue found, attach PR via `update_issue` with link:
```
url:   https://github.com/{org}/{repo}/pull/{number}
title: PR #{number} — {title}
```

### 7. Report

```
PR created: {url}

  Base:   {base}
  Head:   {branch}
  Title:  {title}
  Linear: {issue-id} (linked ✓) or "none"
  Type:   Ready / Draft

  Commits: {count}
  Files:   {count}
```

### 8. Learn

- If user changes base branch, save preference
- If user edits the generated title pattern, save style preference
- If user consistently uses draft, save as default
