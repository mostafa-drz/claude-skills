---
name: daily-brief
description: >-
  Surfaces recent updates relevant to you from GitHub, Linear, Slack, and other
  configured sources — PR reviews, new assignments, ticket changes, mentions, and
  CI failures. Use when starting work, catching up after being away, or prepping
  for standup.
argument-hint: [--since "yesterday"] [--sources github,linear]
context: fork
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_comments
  - mcp__claude_ai_Linear__list_teams
  - mcp__claude_ai_Linear__get_user
  - mcp__claude_ai_Linear__list_users
  - mcp__claude_ai_Linear__list_projects
  - mcp__claude_ai_Notion__notion-search
  - mcp__claude_ai_Notion__notion-fetch
---

# Daily Brief

Surface what changed since you last looked — PR reviews, ticket updates, new assignments, mentions — from all your project tools.

## Preferences

_Read `~/.claude/skills/daily-brief/preferences.md` using the Read tool. If not found, no preferences are set._

## Context

_On startup, use Bash to gather: current git branch (`git branch --show-current`), repo name (`gh repo view --json nameWithOwner -q .nameWithOwner`), and GitHub username (`gh api user -q .login`). Skip any that fail._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/daily-brief/preferences.md`, confirm, stop
- **anything else** (including empty) → run the brief

### Flags

Parse from `$ARGUMENTS`:
- **`--since <time>`** — override lookback window (e.g., "2h", "yesterday", "monday")
- **`--sources <list>`** — comma-separated list to check only specific sources (github, linear, git, notion, slack)
- **`--verbose`** — show full details for each item

### Help

```
Daily Brief — What changed since you last looked

Usage:
  /daily-brief                         Full brief from all sources
  /daily-brief --since "2h"            Only last 2 hours
  /daily-brief --sources github,linear Only specific sources
  /daily-brief --verbose               Show full details per item
  /daily-brief config                  Configure sources and defaults
  /daily-brief reset                   Clear preferences
  /daily-brief help                    This help

Sources (auto-detected):
  GitHub    PR reviews, review requests, mentions, CI failures
  Linear    Assigned ticket changes, new assignments, comments
  Git       Uncommitted work, unpushed commits, stale branches
  Notion    Recently updated pages (if MCP configured)
  Slack     Mentions and DMs (if MCP configured)

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Default lookback window?" (Last 24 hours (default), Last 8 hours, Since last brief, Custom)

**Q2** — "Which sources to include by default?" (multiSelect: true)
- GitHub (PRs, reviews, CI)
- Linear (tickets, assignments)
- Git (local repo state)
- Notion (page updates)
- Slack (mentions, DMs)

**Q3** — "GitHub organization to focus on?" (detect from current repo, always ask, specific org)

**Q4** — "Brief format?" (Concise — one line per item (default), Detailed — full context per item)

Save to `~/.claude/skills/daily-brief/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /daily-brief? Run `/daily-brief config` to choose sources and defaults, or continue — I'll auto-detect available sources."

Then proceed.

## Steps

### 1. Detect available sources

Check which sources are accessible:

**Always available:**
- **GitHub** — verify `gh` CLI: `gh auth status 2>&1`
- **Git** — verify git repo: `git rev-parse --git-dir 2>&1`

**MCP-dependent (try and gracefully skip if unavailable):**
- **Linear** — try `list_teams` to verify access
- **Notion** — try `notion-search` to verify access
- **Slack** — check if any Slack MCP tools are available in the session

Report which sources were found:
```
Sources available: GitHub, Linear, Git
Sources skipped: Notion (not configured), Slack (not configured)
```

If `--sources` flag is set, only use those sources (and warn if any are unavailable).

### 2. Determine time window

In order of priority:
1. `--since` flag if provided
2. `last-brief-timestamp` from preferences (if "since last brief" mode)
3. Default from preferences (or 24 hours)

Convert to ISO timestamp for API queries.

### 3. Fetch updates (parallel where possible)

#### GitHub (via `gh` CLI)

Run these in parallel:

**PR reviews on my PRs:**
```bash
gh api graphql -f query='{ viewer { pullRequests(first: 20, states: OPEN) { nodes { number title url reviews(last: 5, states: [APPROVED, CHANGES_REQUESTED, COMMENTED]) { nodes { author { login } state submittedAt body } } } } } }' 2>/dev/null
```
Filter reviews submitted after the time window.

**Review requests for me:**
```bash
gh pr list --search "review-requested:@me" --state open --limit 10 --json number,title,url,updatedAt,repository
```

**Mentions in issues/PRs:**
```bash
gh api notifications --paginate -q '.[] | select(.reason == "mention" or .reason == "review_requested" or .reason == "assign")' 2>/dev/null
```

**CI failures on my recent PRs:**
```bash
gh pr list --author @me --state open --limit 10 --json number,title,headRefName,statusCheckRollup
```
Filter for PRs with failing checks.

#### Linear (via MCP)

**Recently updated assigned issues:**
Use `list_issues` with filter: assignee is me, updated after time window, ordered by updatedAt.

**New assignments:**
Use `list_issues` with filter: assignee is me, created after time window.

**Comments on my issues:**
For each recently updated issue, use `list_comments` to find new comments by others.

#### Git (local)

```bash
# Uncommitted changes
git status --short 2>/dev/null

# Unpushed commits
git log @{upstream}..HEAD --oneline 2>/dev/null

# Branches with recent activity
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:relative)' refs/heads/ --count=5 2>/dev/null
```

#### Notion (via MCP, if available)

Use `notion-search` with filter for recently edited pages. Show titles and last edited time.

#### Slack (via MCP, if available)

If Slack MCP tools are available in the session, fetch recent mentions and DMs. Otherwise, skip gracefully.

### 4. Filter and rank

For each update, assign a priority:

| Signal | Priority | Example |
|---|---|---|
| Changes requested on my PR | High | Reviewer wants fixes |
| New review request for me | High | Someone waiting on me |
| CI failing on my PR | High | Blocking merge |
| New assignment | Medium | New work to plan |
| Comment on my ticket | Medium | Discussion to engage |
| Mention | Medium | Someone needs my input |
| Approved PR | Low | Ready to merge |
| Ticket status change | Low | FYI update |
| Notion page edit | Low | Background awareness |

Remove duplicates (same item from multiple sources).
Sort by priority, then recency.

### 5. Present the digest

```
Daily Brief — {date}, since {time window}

Sources: GitHub, Linear, Git {Notion, Slack if available}

Needs attention:
  1. [PR] Changes requested on #394 "Refactor auth" by @reviewer — 3h ago
  2. [PR] Review requested: #401 "Add caching layer" by @teammate — 5h ago
  3. [CI] Failing checks on #398 "Fix pipeline" — 2 jobs failed

Updates:
  4. [Linear] AIS-950 "Email notifications" moved to In Review — 6h ago
  5. [Linear] New comment on AIS-948 by @teammate — "Can we also..."
  6. [PR] #393 approved by @reviewer — ready to merge

Local:
  7. [Git] 3 uncommitted files on branch mostafa/ais-950-email
  8. [Git] 2 unpushed commits

{Notion/Slack sections if available and have updates}

No updates: {list of sources with nothing new}
```

If `--verbose`, expand each item with full context (PR description, comment text, CI error summary, etc.).

### 6. Offer actions

Use **`AskUserQuestion`** (multiSelect: false):

Options based on what's in the digest:
- "Investigate #N" — drill into a specific item (read PR, check CI, open ticket)
- "Merge approved PRs" — if any PRs are approved and ready
- "Open in browser" — open a specific item's URL
- "Refresh" — re-run the brief
- "Done" — finish

If the user picks an item, provide full context and offer relevant follow-up actions. Then re-offer the action menu.

### 7. Update timestamp

After the brief completes, save the current timestamp to preferences as `last-brief-timestamp` so the next run can use "since last brief" mode.

### 8. Learn

- If user consistently filters to specific sources, save that as default
- If user always uses a specific time window, save it
- If user always drills into the same type of item first, note the priority pattern

## Principles

- **Fast and scannable** — the whole point is a quick catchup. Keep items to one line. Details on demand.
- **Read-only** — never modify anything. This is a notification digest, not an action tool.
- **Graceful degradation** — if a source is unavailable, skip it and continue. Never fail because one source is down.
- **No duplicates** — the same PR or ticket showing in GitHub and Linear should appear once, with the richest context.
- **Respect time** — default to 24h lookback. Don't drown the user in week-old updates.
