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

_On startup, use Bash to detect: current git branch, uncommitted changes (`git status --short`), unstaged working tree changes (`git diff --stat`), staged changes (`git diff --cached --stat`), recent commits (`git log --oneline -5`), ahead/behind upstream, your open PRs (`gh pr list --author @me --state open --limit 10`), review requests for you (`gh pr list --search "review-requested:@me" --state open --limit 5`), and recently modified files in `client-mission/` directories (`find client-mission/ -type f -mmin -60 2>/dev/null | head -20`). Skip any that fail._

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
  2. Session     — continue/finish the active task in this conversation
  3. Unblocked   — items just became ready
  4. Momentum    — continue active work
  5. Stale       — PRs/tickets aging
  6. Deadlines   — approaching due dates

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

### 1. Detect session context

Before gathering external context, determine whether this conversation has an **active task in progress**. Session context exists when ANY of these are true:

- There are uncommitted changes in the working tree (`git diff --stat` returns output)
- There are staged but uncommitted changes (`git diff --cached --stat` returns output)
- Files in `client-mission/` were modified in the last 60 minutes
- The current conversation has prior tool calls (files read, edits made, commands run)
- A PR was recently created or merged in this session
- A skill or process was planned/designed but not yet implemented

**Set `HAS_SESSION_CONTEXT = true`** if any of the above are detected. This flag controls scoring behavior in Step 3.

### 2. Gather context (parallel where possible)

Git and PR context is pre-injected above.

**Linear context** (fetch via MCP tools):
- In-progress issues: `list_issues` with assignee "me", state "In Progress"
- In-review issues: `list_issues` with assignee "me", state "In Review"
- Recently updated assigned issues: `list_issues` with assignee "me", limit 10, orderBy "updatedAt"

**Session context**:
- What was discussed in current conversation
- Decisions made, actions completed, pending items
- Files modified or investigated

### 3. Score and rank

#### Session-aware scoring

When `HAS_SESSION_CONTEXT = true`, apply these rules BEFORE general scoring. The current session's work should almost always be suggestion #1:

| Session signal | Auto-suggestion | Priority |
|---|---|---|
| Uncommitted changes on current branch | "Commit your changes and open a PR" | Force #1 |
| client-mission files recently modified | "Upload demo data and test in browser" | Force #1 |
| PR was just created or merged | "Verify deployment / close the Linear ticket / test staging" | Force #1 |
| A skill, plan, or design was just discussed | "Implement the planned changes" | Force #1 |
| Active file edits in conversation (no uncommitted git changes) | "Continue: [describe the in-progress task from conversation]" | Force #1 |

Only ONE of the above becomes #1 (pick the most specific match). Slots #2 and #3 are filled from general scoring below.

When `HAS_SESSION_CONTEXT = false` (fresh conversation, no prior work), skip this section entirely and use general scoring for all 3 slots.

#### General scoring

For each potential action, score using weighted signals:

| Signal | Weight (no session context) | Weight (with session context) | Examples |
|---|---|---|---|
| Blocking others | 5 | 5 | Approved PR not merged, ticket blocking another |
| Just unblocked | 4 | 4 | Blocker resolved, failing checks now pass |
| Active momentum | 3 | **5** | On related branch, uncommitted changes, current task |
| Staleness | 2 | 2 | PR open >2 days, ticket in-progress >3 days |
| Approaching deadline | 2 | 2 | Due date within 3 days, sprint ending |
| Recency | 1 | 1 | Recently updated, from current session |

If focus area provided in `$ARGUMENTS`, boost matching items but still show high-scoring non-matches (blockers).

Apply priority weighting mode from preferences if set.

### 4. Present top 3

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

When session context was detected, add a note after #1:
`(continuing from this session)`

### 5. Offer interaction

Use **`AskUserQuestion`** (multiSelect: false):
- "Execute #1" / "Execute #2" / "Execute #3"
- "Expand details" — full context for all 3
- "Refresh" — re-gather and re-rank
- "Skip all"

**If executing**: Announce → execute → report → offer updated suggestions.
**If expanding**: Show links, related tickets, files, full reasoning.

## Principles

- **3 items max**: Avoid decision fatigue.
- **Session continuity first**: When there's active work in the conversation, the #1 suggestion MUST relate to finishing or advancing that work. Never ignore the elephant in the room.
- **Actionable, not informational**: Every suggestion has a clear next step.
- **Context-first**: Connect dots the developer might miss.
- **No repeats**: Don't re-suggest dismissed/completed items in same session.
- **Show reasoning**: Briefly explain WHY each item is suggested.
- **Be fast**: Gather context in parallel, don't over-read.
