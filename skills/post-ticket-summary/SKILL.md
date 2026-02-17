---
name: post-ticket-summary
description: >-
  Posts a structured implementation summary comment to a Linear issue — what was built,
  key decisions, reuse patterns, and how to test. Use after completing work on a ticket
  to document the implementation for the team.
argument-hint: <issue-id> [--preview] [--minimal]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_comments
  - mcp__claude_ai_Linear__create_comment
  - mcp__claude_ai_Linear__get_project
---

# Post Ticket Summary

Add a structured implementation summary comment to a Linear issue after completing work.

## Preferences

!`cat ~/.claude/skills/post-ticket-summary/preferences.md 2>/dev/null || echo "_no preferences set_"`

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Recent commits: !`git log --oneline -20 2>/dev/null || echo "no history"`
- Repo: !`gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "unknown"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/post-ticket-summary/preferences.md`, confirm, stop
- **`--preview <issue-id>`** → show comment without posting then stop
- **`--minimal <issue-id>`** → use minimal template
- **anything else** → post summary

### Help

```
Post Summary — Document implementation on a Linear issue

Usage:
  /post-ticket-summary <issue-id>               Post full summary
  /post-ticket-summary --preview <issue-id>     Show without posting
  /post-ticket-summary --minimal <issue-id>     Short summary (skip architecture/reuse)
  /post-ticket-summary config                   Set template preferences
  /post-ticket-summary reset                    Clear preferences
  /post-ticket-summary help                     This help

Examples:
  /post-ticket-summary AIS-810
  /post-ticket-summary --preview AIS-810
  /post-ticket-summary --minimal AIS-810

What it does:
  1. Reads the Linear issue and codebase
  2. Analyzes recent commits and changed files
  3. Builds structured summary comment
  4. Posts to the Linear issue

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Default template?" (full (default), minimal)
**Q2** — "Which sections to include?" (multiSelect: true)
- Implementation summary
- Key decisions / architecture
- What was reused
- How to test
- Notes

**Q3** — "Auto-detect issue from branch?" (Yes (default), No — always ask)

Save to `~/.claude/skills/post-ticket-summary/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /post-ticket-summary? Run `/post-ticket-summary config` to customize template sections, or continue with full template."

Then proceed.

## Steps

### 1. Resolve issue

- If issue ID provided in `$ARGUMENTS`, use it
- If no ID and auto-detect is on, extract from branch name (pattern: `user/ais-NNN-*`)
- If still no ID, ask via `AskUserQuestion`

Fetch the issue: title, description, project, status.

### 2. Check for existing summary

Fetch comments on the issue. If an implementation summary comment already exists, ask:
"An implementation summary already exists. Replace it, or skip?"

### 3. Gather implementation details

**From the codebase:**
- Recent commits on current branch (pre-injected)
- Key files changed: `git diff main...HEAD --stat` (or appropriate base)
- Read the main changed files to understand what was built

**From project context:**
- CLAUDE.md for conventions
- README.md for project overview

**Ask user** (optional — use `AskUserQuestion` with all optional):
- Loom URL or recording link (or placeholder)
- Live/staging URL for testing
- Any additional context worth documenting

If user says "skip", use placeholders.

### 4. Build comment

**Full template:**

```markdown
## Implementation Summary

{1-2 paragraphs: what was built and the product goal. Focus on business value.}

### What Was Reused

| Component | Source | Adaptation |
|-----------|--------|------------|
| {component} | {origin} | {what changed} |

---

## How to Test

**Branch:** `{branch}`
**Live URL:** {url or N/A}

### Steps
1. {step}
2. {step}
3. {step}

---

## Features

### 1. {Feature Name}

{2-3 sentences from user perspective. What they see, what they can do, business value.}

### 2. {Feature Name}

{Same structure}

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| {decision} | {why} |

---

## Notes

- {Additional context}
```

**Minimal template:**

```markdown
## Implementation Summary

{1-2 paragraphs}

## How to Test

**Branch:** `{branch}`

1. {step}
2. {step}

## Notes

- {anything important}
```

Apply section toggles from preferences.

### Content guidelines

- **Summary**: Lead with the problem, then what the implementation does.
- **Features**: User perspective — what they see and do. No file paths.
- **Key Decisions**: Focus on the "why" behind non-obvious choices.
- **Reuse**: Show what was leveraged vs built new.

### 5. Post or preview

If `--preview`: display the comment and stop.

Otherwise: post via `create_comment`.

### 6. Report

```
Posted implementation summary to {issue-id}.

Sections: {list of included sections}

Next steps:
  1. Record Loom and update the link
  2. Add screenshots if relevant
  3. Replace any [PLACEHOLDER] markers
```

### 7. Learn

If user removes sections consistently, update preferences.
If user adds custom sections, note the pattern.
