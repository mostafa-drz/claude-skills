---
name: whats-next
description: >-
  Suggests the 3 most impactful next actions based on full developer context — git,
  Linear, PRs, and current conversation. Prioritizes blockers, unblocked items, and momentum.
  Use when deciding what to work on next or after finishing a task.
argument-hint: [optional focus area]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
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

# What's Next

Surface the 3 most impactful things to do right now based on all available context.

## Preferences

_Read `~/.claude/skills/whats-next/preferences.md` using the Read tool. If not found, no preferences are set._

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Uncommitted: !`git status --short 2>/dev/null || echo "clean"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "no history"`
- Ahead/behind: !`git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || echo "no upstream"`
- My PRs: !`gh pr list --author @me --state open --limit 10 2>/dev/null || echo "gh not available"`
- Review requests: !`gh pr list --search "review-requested:@me" --state open --limit 5 2>/dev/null || echo "none"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/whats-next/preferences.md`, confirm, stop
- **anything else** (including empty) → analyze and suggest

### Help

```
What's Next — Top 3 actions based on your full context

Usage:
  /whats-next                    Analyze everything, suggest top 3
  /whats-next <focus>            Focus on area (e.g., "frontend", "AIS-922", "cleanup")
  /whats-next config             Set priority weighting and sources
  /whats-next reset              Clear preferences
  /whats-next help               This help

Context sources:
  Git       Branch, uncommitted changes, ahead/behind remote
  PRs       Your open PRs, review requests, stale PRs
  Linear    In-progress, blocked, assigned to you
  Session   Current conversation, decisions, files discussed

Priority signals (highest to lowest):
  1. Blockers    — things others wait on you for
  2. Unblocked   — items just became ready
  3. Momentum    — continue active work
  4. Stale       — PRs/tickets aging
  5. Deadlines   — approaching due dates

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Which context sources to use?" (multiSelect: true)
- Git (branch, status, commits)
- GitHub PRs (open, reviews, stale)
- Linear (in-progress, blocked, assigned)
- Session (conversation context)

**Q2** — "Priority weighting?" (multiSelect: false)
- Balanced (default) — all signals equal
- Ship mode — favor finishing in-progress work
- Unblock mode — favor items blocking others

Save to `~/.claude/skills/whats-next/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /whats-next? Run `/whats-next config` to customize sources and priority mode, or continue with defaults (all sources, balanced)."

Then proceed.

## Steps

### 1. Gather context (parallel where possible)

Git and PR context is pre-injected above.

**Linear context** (fetch via MCP tools):
- In-progress issues: `list_issues` with assignee "me", state "In Progress"
- In-review issues: `list_issues` with assignee "me", state "In Review"
- Recently updated assigned issues: `list_issues` with assignee "me", limit 10, orderBy "updatedAt"

**Session context**:
- What was discussed in current conversation
- Decisions made, actions completed, pending items
- Files modified or investigated

### 2. Score and rank

For each potential action, score using weighted signals:

| Signal | Weight | Examples |
|---|---|---|
| Blocking others | 5 | Approved PR not merged, ticket blocking another |
| Just unblocked | 4 | Blocker resolved, failing checks now pass |
| Active momentum | 3 | On related branch, uncommitted changes, current task |
| Staleness | 2 | PR open >2 days, ticket in-progress >3 days |
| Approaching deadline | 2 | Due date within 3 days, sprint ending |
| Recency | 1 | Recently updated, from current session |

If focus area provided in `$ARGUMENTS`, boost matching items but still show high-scoring non-matches (blockers).

Apply priority weighting mode from preferences if set.

### 3. Present top 3

```
What's next for you:

1. [Action title]
   [Why — one sentence connecting to context]
   → [Concrete next step]

2. [Action title]
   [Why]
   → [Next step]

3. [Action title]
   [Why]
   → [Next step]
```

Each card: imperative action title, real signal explanation, literal command/action.

### 4. Offer interaction

Use **`AskUserQuestion`** (multiSelect: false):
- "Execute #1" / "Execute #2" / "Execute #3"
- "Expand details" — full context for all 3
- "Refresh" — re-gather and re-rank
- "Skip all"

**If executing**: Announce → execute → report → offer updated suggestions.
**If expanding**: Show links, related tickets, files, full reasoning.

## Principles

- **3 items max**: Avoid decision fatigue.
- **Actionable, not informational**: Every suggestion has a clear next step.
- **Context-first**: Connect dots the developer might miss.
- **No repeats**: Don't re-suggest dismissed/completed items in same session.
- **Show reasoning**: Briefly explain WHY each item is suggested.
- **Be fast**: Gather context in parallel, don't over-read.
