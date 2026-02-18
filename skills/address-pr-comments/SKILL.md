---
name: address-pr-comments
description: >-
  Fetches unresolved PR comments, categorizes them (must-fix, suggestion, question, nit),
  proposes fixes or replies for each, and executes approved actions. Use when addressing
  PR review feedback or when someone requests changes on your PR.
argument-hint: <PR number or URL>
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude_ai_Linear__update_issue
  - mcp__claude_ai_Linear__create_comment
---

# Address PR Comments

Fetch unresolved PR comments, understand the code context, categorize feedback, and address each item interactively.

## Preferences

_Read `~/.claude/skills/address-pr-comments/preferences.md` using the Read tool. If not found, no preferences are set._

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Repo: !`gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "unknown"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/address-pr-comments/preferences.md`, confirm, stop
- **anything else** → process as PR review

### Help

```
Review PR — Address PR review comments interactively

Usage:
  /address-pr-comments <number>              Review PR in current repo
  /address-pr-comments <number> <repo>       Review PR in specific repo
  /address-pr-comments <github-url>          Review PR from URL
  /address-pr-comments config                Set defaults
  /address-pr-comments reset                 Clear preferences
  /address-pr-comments help                  This help

What it does:
  1. Fetches all unresolved review and conversation comments
  2. Reads code context for each comment
  3. Categorizes: must-fix, suggestion, question, nit
  4. Presents summary with proposed actions
  5. Executes approved fixes, posts replies
  6. Commits and pushes changes

Comment sources:
  - Inline review comments
  - PR conversation comments
  - Automated review tools (Claude, Copilot)

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Default repository?" (Current repo (detect), Always ask)
**Q2** — "Which comments to include?" (Unresolved only (default), All comments, Latest review round only)
**Q3** — "Auto-commit after fixes?" (Yes — commit and push (default), No — stage only, Ask each time)

Save to `~/.claude/skills/address-pr-comments/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /address-pr-comments? Run `/address-pr-comments config` to set defaults, or continue — I'll review unresolved comments in the current repo."

Then proceed.

## Steps

### 1. Parse input

From `$ARGUMENTS`:
- **PR number**: Numeric ID
- **Repository**: From URL, second arg, or current git remote
- **Organization**: From URL or git remote

If only a number, detect repo from pre-injected context above.

### 2. Gather context (parallel)

**PR details:**
```
gh pr view <number> --repo <org/repo> --json title,body,headRefName,baseRefName,state,reviewDecision,files
```

**Review comments (inline):**
```
gh api repos/<org>/<repo>/pulls/<number>/comments --paginate
```

**Conversation comments (top-level):**
```
gh api repos/<org>/<repo>/issues/<number>/comments --paginate
```

**Changed files:**
```
gh pr diff <number> --repo <org/repo> --name-only
```

**Branch check:** Note if you're on the PR branch or not.

### 3. Filter and categorize

**Filter:**
- Exclude resolved review threads
- Exclude purely informational bot comments (CI, deploy URLs)
- Include automated review tools (Claude Code Review, Copilot) — they have actionable feedback

**Categorize each comment:**
1. Read the code at the commented location
2. Understand the suggestion
3. Assess category:
   - **Must-fix**: Bugs, security issues, logic errors, breaking changes
   - **Suggestion**: Improvements, better patterns, refactoring
   - **Question**: Reviewer needs clarification
   - **Nit**: Style, naming, minor preferences
4. Draft action: code change, reply, or explanation

### 4. Present summary

```
PR #N: [title]
Branch: [branch]
Comments: X unresolved (Y must-fix, Z suggestions, W questions, V nits)

Must-fix:
  1. [file:line] @reviewer — "issue description"
     → Proposed fix: [change]

Suggestions:
  2. [file:line] @reviewer — "description"
     → Proposed change: [change]

Questions:
  3. [file:line] @reviewer — "question"
     → Draft reply: [explanation]

Nits:
  4. [file:line] @reviewer — "nit"
     → Proposed change: [change]
```

### 5. Confirm actions

Use **`AskUserQuestion`** (multiSelect: true):
- One option per comment action
- "Address all"
- "Skip all"

### 6. Execute

**For code changes:**
1. Read current file at relevant lines
2. Apply the edit
3. Show diff
4. Batch changes in same file

**For replies:**
```
gh api repos/<org>/<repo>/pulls/<number>/comments/<id>/replies -f body="<reply>"
```

**After all actions** (based on preference):
- Stage changed files
- Commit with message referencing the review
- Push to PR branch
- Optionally reply to addressed comments

### 7. Summary

```
Review complete for PR #N

  Applied: X changes
  Replied: Y comments
  Skipped: Z items

Changes committed: [hash] "[message]"
Pushed to: [branch]

Remaining unresolved: [count]
```

### 8. Learn

If user consistently skips nits, note preference.
If user prefers certain reply styles, save pattern.

## Principles

- **Read before acting**: Always read code context before proposing fixes.
- **Respect the reviewer**: Treat each comment as valid. Explain disagreements respectfully.
- **Atomic changes**: Minimal, targeted fixes. Don't refactor surrounding code.
- **Batch smartly**: Group changes in the same file.
- **Don't auto-resolve**: Let reviewers resolve their own comments.
- **Preserve intent**: Don't change the approach unless explicitly asked.
