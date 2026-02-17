---
name: thread-to-action
description: >-
  Parses a pasted thread (Slack, email, GitHub, Teams), analyzes it against current
  git, Linear, and session context, and suggests actionable next steps — then executes
  them with confirmation. Use when pasting a conversation that implies developer actions.
argument-hint: <paste thread here>
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
  - mcp__claude_ai_Linear__create_issue
  - mcp__claude_ai_Linear__update_issue
  - mcp__claude_ai_Linear__list_teams
  - mcp__claude_ai_Linear__list_projects
  - mcp__claude_ai_Linear__list_issue_labels
  - mcp__claude_ai_Linear__list_issue_statuses
  - mcp__claude_ai_Linear__create_comment
  - mcp__claude_ai_Linear__list_comments
---

# Thread → Action

Analyze a pasted conversation thread and suggest concrete developer actions, then execute them with confirmation.

## Preferences

!`cat ~/.claude/skills/thread-to-action/preferences.md 2>/dev/null || echo "_no preferences set_"`

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "no git history"`
- Git status: !`git status --short 2>/dev/null || echo "clean"`
- Open PRs: !`gh pr list --author @me --state open --limit 5 2>/dev/null || echo "gh not available"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/thread-to-action/preferences.md`, confirm, stop
- **anything else** → process as thread

### Help

```
Thread → Action — Parse a thread and suggest developer actions

Usage:
  /thread-to-action <paste thread>    Analyze and suggest actions
  /thread-to-action config            Configure context sources and action types
  /thread-to-action reset             Clear preferences
  /thread-to-action help              This help

Context sources:
  Git:     branch, recent commits, status, open PRs
  Linear:  active issues, recent issues assigned to me
  Session: working directory, CLAUDE.md, prior conversation

Action types: Git/PR, Linear, Code, Cleanup
  See reference/action-types.md for full list

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Which context sources should be active?" (multiSelect: true)
- Git context (branch, commits, status, PRs)
- Linear context (active issues, recent issues)
- Session context (working directory, CLAUDE.md)

**Q2** — "Default Linear filters?" (multiSelect: false)
- Use my assignments (default)
- Use specific team/project
- No Linear filtering

**Q3** — "Which action types to suggest?" (multiSelect: true)
- Git/PR actions
- Linear actions
- Code actions
- Cleanup actions

Save to `~/.claude/skills/thread-to-action/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /thread-to-action? Run `/thread-to-action config` to customize, or continue with defaults (all sources, all action types)."

Then proceed normally.

## Steps

### 1. Parse the thread

Analyze `$ARGUMENTS` and extract:
- **Participants**: Who and what roles
- **Topic**: Core subject
- **Decisions made**: Anything agreed upon
- **Action items**: Explicit or implied next steps
- **Links**: URLs to PRs, issues, docs — fetch and understand them
- **Blockers resolved**: Was something unblocked?
- **Status changes**: Did work item status change? ("merged it", "PR is ready", "deployed")

### 2. Fetch Linear context

Fetch in parallel (if Linear is enabled in preferences):
- Active issues assigned to me (state "In Progress" or "In Review")
- Recent issues I created (limit 5)

### 3. Cross-reference with context

Match thread content against gathered context:
- Do mentioned PRs match open PRs from git context?
- Do mentioned tickets match active Linear issues?
- Does the thread resolve a blocker for current work?
- Does it introduce new work needing tracking?
- Is the current branch related to the discussion?

### 4. Generate suggested actions

Suggest a numbered list. Each action has:
- **What**: Clear description
- **Why**: Connection to the thread
- **How**: Tool/command to use

See `reference/action-types.md` for common action types. Infer from context — the list is not exhaustive.

### 5. Present and confirm

```
Based on the thread, I suggest these actions:

1. [Action] — [Why]
2. [Action] — [Why]
3. [Action] — [Why]
```

Use **`AskUserQuestion`** (multiSelect: true):
- One option per action
- "Skip all"

### 6. Execute

For each confirmed action:
1. Announce what you're about to do
2. Execute it
3. Report result (success/failure, link to resource)
4. If failure, ask whether to continue

### 7. Summary

```
Actions completed: X
Actions skipped: Y
Actions failed: Z (with reasons)
Follow-up items: [if any]
```

### 8. Learn

If user consistently skips certain action types, note it in preferences.
If user corrects a suggestion pattern, save the preference silently.
