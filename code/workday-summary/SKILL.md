---
name: workday-summary
description: >-
  Summarizes work done today into timesheet-ready bullet points. Analyzes
  conversation history, git commits, Linear tickets, and GitHub PRs. Use when
  ending a session, filling a timesheet, preparing for standup, writing a daily
  log, wrapping up for the day, or when asked what was worked on.
argument-hint: [--today | --yesterday | --week | --since "date"] [--format bullets|table|full-markdown|plain]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash(git *)
  - Bash(gh *)
  - Bash(date *)
  - Bash(find *)
  - Bash(fc *)
  - Bash(pbcopy *)
  - Bash(echo *)
  - Read
  - Glob
  - Grep
  - Write
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_teams
  - mcp__claude_ai_Linear__get_user
---

# Workday Summary

Summarize everything you worked on into clean, grouped bullet points — ready for timesheets, standups, or end-of-day logs.

## Preferences

_Read `~/.claude/skills/workday-summary/preferences.md` using the Read tool. If not found, no preferences are set._

## Context

_On startup, use Bash to gather: current date, git user email (`git config user.email`), GitHub username (`gh api user -q .login`), and any git repos under the working directory. Skip any that fail._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/workday-summary/preferences.md`, confirm, stop
- **anything else** (including empty) → run the summary

### Flags

Parse from `$ARGUMENTS` (use `$0`, `$1` shorthand for positional args):
- **`--today`** (default) — summarize today's work
- **`--yesterday`** — summarize yesterday's work
- **`--week`** — summarize this week's work
- **`--since "date"`** — summarize since a specific date/time
- **`--format <fmt>`** — output format: `bullets` (default), `table`, `full-markdown`, `plain`
- **`--group-by <mode>`** — grouping: `ticket` (default), `project`, `chronological`, `none`
- **`--no-time-estimates`** — omit time estimates from output
- **`--sources <list>`** — comma-separated: `conversation`, `git`, `linear`, `github` (default: all)
- **`--concise`** — summary only, no evidence
- **`--detailed`** — show evidence for each item

### Help

```
Workday Summary — Summarize today's work for timesheets and standups

Usage:
  /workday-summary                       Summarize today's session
  /workday-summary --yesterday           Yesterday's work
  /workday-summary --week                This week's work
  /workday-summary --since "2026-02-28"  Since a specific date
  /workday-summary --format table        Output as timesheet table
  /workday-summary config                Set preferences
  /workday-summary reset                 Clear preferences
  /workday-summary help                  This help

Options:
  --today                  Default. Summarize today.
  --yesterday              Summarize yesterday.
  --week                   Summarize this week (Mon-now).
  --since "date"           Since a specific date or time.
  --format <fmt>           bullets | table | full-markdown | plain
  --group-by <mode>        ticket | project | chronological | none
  --no-time-estimates      Omit time estimates
  --sources <list>         conversation,git,linear,github
  --concise                Summary only
  --detailed               Show evidence for each item

Examples:
  /workday-summary                       End-of-day summary
  /workday-summary --format table        Timesheet-ready table
  /workday-summary --week --concise      Quick weekly recap
  /workday-summary --sources git,linear  Only git + Linear data

Current preferences:
  (read from preferences.md)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Output format?" (Bullets (default), Table, Full Markdown, Plain text)

**Q2** — "Group by?" (Ticket/project (default), Chronological, No grouping)

**Q3** — "Include time estimates?" (Yes (default), No)

**Q4** — "Which sources to include?" (multiSelect: true)
- Conversation history
- Git commits
- Linear tickets
- GitHub PRs

**Q5** — "Detail level?" (Concise — high-level only, Detailed — show evidence (default))

**Q6** — "Auto-copy to clipboard?" (Yes, No (default))

**Q7** — "Save summary to file? If yes, provide path." (No (default), or a path)

Save to `~/.claude/skills/workday-summary/preferences.md`.

### Reset

Delete `~/.claude/skills/workday-summary/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:
"First time using /workday-summary? Run `/workday-summary config` to set defaults, or continue — I'll use sensible defaults."

Then proceed.

## Workflow

### 1. Determine time window

Based on flags (in priority order):
1. `--since "date"` — parse the date
2. `--yesterday` — yesterday 00:00 to yesterday 23:59
3. `--week` — Monday 00:00 to now
4. `--today` or empty — today 00:00 to now

Use Bash to compute the ISO date string for the window start:
```bash
date -v-0d +%Y-%m-%d  # today
date -v-1d +%Y-%m-%d  # yesterday
date -v-monday +%Y-%m-%d  # this week's monday
```

### 2. Gather context (parallel where possible)

Run all source collection in parallel. Skip any that fail.

#### A. Conversation history (most important source)

This skill has FULL access to the conversation context. Analyze the conversation to identify:
- **Files read or edited** — infer what feature/bug they relate to
- **Bash commands run** — what was being tested, built, deployed
- **Tool calls** — what MCP tools were used and why
- **Decisions made** — architectural choices, debugging conclusions
- **Problems solved** — errors encountered and how they were resolved

Do NOT just list "read file X" or "ran command Y". Synthesize into accomplishments:
- "Investigated auth flow to understand token refresh behavior" (not "read auth.ts")
- "Fixed pagination bug in search results" (not "edited search.tsx line 45")
- "Set up email notification templates for meeting summaries" (not "wrote 3 files")

#### B. Git commits

For each git repo the user worked in, run:
```bash
git log --since="{window_start} 00:00" --oneline --author="$(git config user.email)" 2>/dev/null
```

Also check for uncommitted work:
```bash
git diff --stat 2>/dev/null
git diff --cached --stat 2>/dev/null
```

If multiple repos exist under the working directory, scan each. Use Bash to find them:
```bash
find /Users/mostafa/Dev/ateam -maxdepth 2 -name .git -type d 2>/dev/null
```

#### C. Linear (if MCP available)

Try to fetch issues assigned to me, updated within the time window:
- Use `list_issues` with assignee "me", updatedAt filter
- Note ticket IDs, titles, and status changes

If Linear MCP is unavailable, skip gracefully.

#### D. GitHub (if `gh` CLI available)

```bash
gh pr list --author @me --state all --limit 20 --json number,title,state,updatedAt,url 2>/dev/null
```

Filter to PRs updated within the time window.

Also check for PR reviews given:
```bash
gh api graphql -f query='{ viewer { contributionsCollection { pullRequestReviewContributions(first: 20) { nodes { pullRequest { number title url repository { nameWithOwner } } } } } } }' 2>/dev/null
```

#### E. Recent shell activity (supplementary)

Check bash/zsh history for additional signals:
```bash
fc -l -t '%Y-%m-%d %H:%M' -200 2>/dev/null
```

Filter entries from the time window. Look for patterns (deploy commands, test runs, build commands) that indicate work done.

### 3. Synthesize

Merge signals from all sources, deduplicating:
- If a git commit and a conversation both reference the same file/feature, combine them
- If a Linear ticket and a git branch match (by ticket ID in branch name), group together
- Prefer the highest-context description (conversation > git message > ticket title)

Group results according to `--group-by` preference:
- **ticket** — group by Linear ticket or project, with an "Other" bucket for ungrouped work
- **project** — group by repo or project name
- **chronological** — order by time
- **none** — flat list

### 4. Format output

Apply the `--format` preference:

#### bullets (default)
```markdown
## Today's Work — {date}

### What I accomplished
- [High-level accomplishment 1]
- [High-level accomplishment 2]
- [High-level accomplishment 3]

### By Ticket / Project
**AIS-XXX: Ticket Name**
- Specific thing done
- Another thing done

**Codebase Work** (git-based, no ticket)
- Fixed X in file Y
- Added feature Z

### For Timesheet
| Task | Category | Est. Time |
|------|----------|-----------|
| AIS-XXX: Description | Dev | ~2h |
| Code review: PR #123 | Review | ~30m |
| Debugging pipeline issue | Debug | ~1h |
```

#### table
```markdown
## Today's Work — {date}

| Task | Category | Est. Time | Source |
|------|----------|-----------|--------|
| AIS-XXX: Did thing | Dev | ~2h | Git + Linear |
| Reviewed PR #123 | Review | ~30m | GitHub |
| ... | ... | ... | ... |
| **Total** | | **~Xh** | |
```

#### full-markdown
Full version with all sections, evidence links, and detailed descriptions.

#### plain
Minimal plain text, no markdown — suitable for pasting into time tracking tools.

### 5. Present summary

Output the formatted summary.

If `--detailed`, include evidence for each item:
- Git commit hashes
- File names changed
- Linear ticket URLs
- PR URLs

### 6. Offer post-actions

Use **`AskUserQuestion`** (multiSelect: false):

- **"Copy to clipboard"** — copy the summary using `pbcopy` (macOS)
- **"Save to file"** — save to a specified path (default: `~/Desktop/workday-summary-{date}.md`)
- **"Change format"** — re-render in a different format
- **"Add/remove items"** — let the user edit the summary
- **"Done"** — finish

If the user picks "Copy to clipboard":
```bash
echo "{summary}" | pbcopy
```
Confirm: "Summary copied to clipboard."

If the user picks "Save to file", ask for path (or use default), then write the file.

If the user picks "Add/remove items", let them specify what to change, re-render, and re-offer actions.

### 7. Learn

Save useful patterns to preferences:
- If user always uses a specific format, save it
- If user removes time estimates, save `no-time-estimates: true`
- If user always picks specific sources, save as defaults
- If user corrects a grouping or categorization, note the pattern

Mention what was learned: "Noted: you prefer table format. Saved for next time."

## Principles

- **Accomplishments, not activities** — say "Fixed pagination bug" not "Edited search.tsx". Synthesize raw signals into meaningful work items.
- **Read-only** — this skill only reads conversation history, git logs, and API data. It never modifies code, tickets, or branches.
- **Conversation context is king** — the conversation history is the richest source of what was actually done. Git and Linear are supplementary.
- **Graceful degradation** — if a source is unavailable, skip it. Never fail because one source is down.
- **Timesheet-ready** — the output should be directly pasteable into time tracking tools with minimal editing.
- **Fast** — gather all sources in parallel. Don't block on slow API calls.
