---
name: project-updates
description: >-
  Drafts Linear project status updates for each project the user leads, following
  the Done / In Progress / Next / Blockers template. Gathers context from Linear
  issues and comments, git history across configured repos, GitHub PRs, Slack
  mentions, Notion edits, and Gmail/Calendar. Never auto-posts — always shows the
  draft so the user can paste it into Linear. Learns from edits over time.
  Use when preparing daily or end-of-day Linear project updates, writing project
  status, prepping for standup, or when the user asks "what should my project
  updates say today".
argument-hint: [--since "24h"] [--projects "slug1,slug2"] [--sources linear,git,github,slack,notion] [--project <slug>] [--dry-run]
disable-model-invocation: true
context: fork
agent: Explore
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - mcp__claude_ai_Linear__list_projects
  - mcp__claude_ai_Linear__get_project
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_comments
  - mcp__claude_ai_Linear__list_teams
  - mcp__claude_ai_Linear__get_user
  - mcp__claude_ai_Linear__list_users
  - mcp__claude_ai_Linear__get_status_updates
  - mcp__claude_ai_Notion__notion-search
  - mcp__claude_ai_Notion__notion-fetch
  - mcp__claude_ai_Slack__slack_search_public_and_private
  - mcp__claude_ai_Slack__slack_read_thread
  - mcp__claude_ai_Slack__slack_read_channel
  - mcp__claude_ai_Gmail__search_threads
  - mcp__claude_ai_Gmail__get_thread
  - mcp__claude_ai_Google_Calendar__list_events
---

# Project Updates

Draft Linear project status updates — one per project, in the team template (Done / In Progress / Next / Blockers) — from everything I did today, across every tool I use. Show drafts, capture edits, learn patterns.

## Preferences

_On startup, use the Read tool on `~/.claude/skills/project-updates/preferences.md`. If not found, no preferences are set._

## Learnings

_On startup, use the Read tool on `~/.claude/skills/project-updates/learnings.md`. If not found, treat as empty. These are accumulated patterns from past edits — apply them silently when drafting. Do not mention the learnings file to the user unless adding to it._

## Context

_On startup, use Bash to gather (skip any that fail):_
- _Current date: `date +%Y-%m-%d`_
- _Git user email: `git config --global user.email`_
- _GitHub username: `gh api user -q .login 2>/dev/null`_
- _Linear user (from MCP): `mcp__claude_ai_Linear__get_user` with self_

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help, stop
- **`config`** → interactive setup, stop
- **`reset`** → delete `preferences.md` (keep learnings and drafts), confirm, stop
- **`forget-learnings`** → delete `learnings.md`, confirm, stop
- **`show-learnings`** → print `learnings.md` contents, stop
- **anything else** (including empty) → run the skill

### Flags

Parse from `$ARGUMENTS`:
- **`--since <time>`** — lookback window (e.g., `24h`, `48h`, `yesterday`, `monday`). Default: from preferences, else `24h`.
- **`--projects <list>`** — comma-separated Linear project slugs/names to include (overrides default set).
- **`--project <slug>`** — shortcut for a single project.
- **`--sources <list>`** — comma-separated: `linear,git,github,slack,notion,gmail,calendar`. Default: all available.
- **`--dry-run`** — draft only; skip writing to `drafts/` and skip learnings capture.
- **`--no-feedback`** — skip the per-draft feedback prompt.
- **`--format <style>`** — `template` (default: Done/In Progress/Next/Blockers) or `narrative` (paragraph style).

### Help

```
Project Updates — Draft Linear project status updates from all your signals

Usage:
  /project-updates                         All projects I lead, last 24h
  /project-updates --since 48h             Last 48 hours
  /project-updates --project fast-signals  One specific project
  /project-updates --sources linear,git    Only these sources
  /project-updates --dry-run               Draft only, don't save
  /project-updates show-learnings          Print accumulated learnings
  /project-updates forget-learnings        Wipe learnings.md
  /project-updates config                  Set preferences
  /project-updates reset                   Clear preferences
  /project-updates help                    This help

Template (Done / In Progress / Next / Blockers):
  Done:
  In Progress:
  Next:
  Blockers:

Sources (auto-detected, graceful skip):
  linear    Assigned issues, project activity, comments, status updates
  git       Commits across configured repos (see `repos-root` + `default-repos` in preferences) touching project branches
  github    PRs opened, merged, reviewed; linked to Linear IDs
  slack     Mentions, threads where I participated
  notion    Pages I edited or that reference project IDs
  gmail     Threads I replied to
  calendar  Meetings attended (supplementary)

Current preferences:
  (read from preferences.md)
```

### Config

Use **`AskUserQuestion`** for these:

**Q1 — Default lookback window?**
Options: `24h (default)`, `48h`, `since last run`, `custom`

**Q2 — Which Linear projects do you lead or contribute to regularly?**
Free-text or multiSelect populated from `list_projects` (member == me). These become the default project set.

**Q3a — Where do your local repos live?** (`repos-root`)
Free-text path. Default: `~/Dev/`. The skill expects each configured repo to be a direct subdirectory of this root (e.g., `<repos-root>/<repo-name>`).

**Q3b — Which local repos to scan for git history?** (`default-repos`)
Free-text comma-separated list of repo directory names under `repos-root`. No defaults — this is per-user. Example input: `acme-frontend, acme-api, design-system`.

**Q4 — Which sources to include by default?** (multiSelect)
- Linear (required)
- Git (local commits)
- GitHub (PRs)
- Slack (mentions)
- Notion (page edits)
- Gmail (thread replies)
- Calendar (meetings)

**Q5 — Default output format?**
Options: `template (Done/In Progress/Next/Blockers)` (default) or `narrative (paragraph)`

**Q6 — Auto-copy first draft to clipboard?** Yes / No (default: No)

**Q7 — Confirm: this skill NEVER auto-posts to Linear, right?**
Options: `Correct — always show me first` (expected), `Actually, allow auto-post with confirmation` (switches behavior)

Save to `~/.claude/skills/project-updates/preferences.md`.

### Reset

Delete `~/.claude/skills/project-updates/preferences.md`. Confirm: "Preferences cleared. Learnings and drafts preserved."

### Forget-learnings

Delete `~/.claude/skills/project-updates/learnings.md`. Confirm: "Learnings wiped. Future drafts will start fresh."

### Show-learnings

Read `~/.claude/skills/project-updates/learnings.md` and print its contents verbatim. Then stop.

## First-time detection

If no `preferences.md` exists, show:
"First time using /project-updates? Run `/project-updates config` to set defaults, or continue — I'll auto-detect projects from Linear (assignee == you) and use sensible defaults."

Then proceed.

## Workflow

### 1. Resolve time window

Priority:
1. `--since` flag
2. `last-run-timestamp` in preferences (if `since last run` mode)
3. Default from preferences, else `24h`

Compute absolute ISO timestamps (`since_iso`, `until_iso=now`).

### 2. Resolve project set

Priority:
1. `--project <slug>` — one project
2. `--projects a,b,c` — explicit list
3. `default-projects` from preferences
4. Fallback: query `mcp__claude_ai_Linear__list_projects` with `member: "me"`, filter to active projects (state != completed/cancelled)

For each project, collect: `id`, `name`, `slug`, `url`, and the most recent existing status update (via `get_status_updates` filtered to that project, limit 3) — used as anchor ("progress since last update").

### 3. Detect available sources

Apply `--sources` override if given, else use configured set intersected with runtime availability:
- `git` — verify at least one configured repo exists under `<repos-root>/` (from preferences). If `repos-root` is unset, skip git source with a one-line note.
- `github` — `gh auth status` must succeed
- `linear`, `notion`, `slack`, `gmail`, `calendar` — ping the MCP (try one cheap read; skip on failure)

Report once at top of output:
```
Sources: linear, git, github, slack  |  Skipped: notion (not configured), gmail (no matches today)
```

### 4. Gather signals per project (parallel)

For each project, run collectors in parallel. All collectors must be scoped to `[since_iso, until_iso]`.

#### Linear
- `list_issues` with `project: <id>`, `updatedAt: -P<window>`, order by `updatedAt`
- For each issue updated in window: `list_comments` to extract comments by me or tagged @me
- Filter to: status transitions, my comments, my assignments/reassignments, completed issues
- Also query `get_status_updates` (type: project, project: id) to see what the last posted update already covered — DO NOT re-report work already posted

#### Git (across configured repos)
For each repo in config:
```bash
cd <repo> && git log --since="<since_iso>" --author="<email>" --pretty=format:'%h|%s|%ad' --date=iso 2>/dev/null
```
Cross-reference commit messages / branch names for Linear issue IDs (regex `[A-Z]{2,4}-\d+`). Bucket each commit to a project by the issue ID → project mapping from Linear.

Also check uncommitted WIP: `git status --short` per repo (surface as "in progress").

#### GitHub
```bash
gh pr list --author @me --state all --search "updated:>=<since_iso>" --json number,title,state,url,mergedAt,headRefName,body
gh pr list --search "review-requested:@me updated:>=<since_iso>" --state all --json number,title,state,url
```
Parse PR body/branch for Linear IDs → bucket to project. Distinguish: opened, merged, in review (mine), reviewed-by-me (someone else's).

#### Slack
Use `slack_search_public_and_private` with query `from:@me after:<date>` and secondary queries per project (project name, Linear ID prefix). Keep to threads with substantive messages (>= 20 chars, not just reactions).

#### Notion
Use `notion-search` with project name as query, filter to pages edited in window. Fetch each to extract the change.

#### Gmail (optional)
`search_threads` with `after:<date> from:me`. Bucket by recipient/project only if the project name or Linear ID appears.

#### Calendar (optional)
`list_events` for meetings in window where user attended. Supplementary context for "In Progress" (e.g., "Aligned with <reviewer> on <topic>").

### 5. Synthesize drafts

For each project, feed all collected signals + the last posted status update + the learnings file into the draft model. Produce one draft per project using the user's preferred format.

**Template format (default):**
```
## {Project Name} ({slug})

**Done:**
- <concrete thing shipped, with PR# or Linear ID>

**In Progress:**
- <current work, with ownership if shared>

**Next:**
- <next concrete step, not vague>

**Blockers:**
- <blocker with who/what needed to unblock, or "none">
```

**Drafting rules (hard):**
- Every bullet ≤ 1 line. If it needs two, split or simplify.
- Always include Linear IDs and PR numbers when available (link markdown).
- Never claim work someone else led. Co-ownership → name the other person.
- Don't repeat content from the last posted status update — start from "since <last update date>".
- Omit empty sections silently (e.g., no "Blockers: none" unless the user's learnings say to keep it).
- Apply every rule currently in `learnings.md`.

**Narrative format (if selected):** 2-4 sentence paragraph per project, same rules.

### 6. Present drafts

Show drafts one project at a time with source-count footer:
```
Project: <Project Name from Linear>
Since: <ISO timestamp of your last update>
Signals: <N Linear comments, M PRs merged, K PR in review, J Slack threads>

Done:
- <repo> #<PR> merged — <one-line user-visible summary from the PR body>
- <repo> #<PR> opened, in review (<one-line summary>)

In Progress:
- <currently-open work item, anchored to a Linear issue or PR>

Next:
- <upcoming work, scoped from `next` Linear column or open PRs>

Blockers:
- <blocker, with the responsible reviewer/owner if known>

[Linear: https://linear.app/<linear-org>/project/<slug>]
```

### 7. Feedback capture per draft

For each draft, prompt via **`AskUserQuestion`** unless `--no-feedback`:

- `Accept` — copy to clipboard, move on
- `Edit` — user provides corrected text; skill diffs original vs edit and extracts patterns
- `Skip` — no copy, move on
- `Open Linear` — print the project activity URL for pasting

On **Edit**:
1. Accept the user's rewritten draft
2. Compare original vs edited line-by-line
3. For each meaningful delta (phrasing change, added detail, removed content, reordering), ask:
   > "Detected pattern: `<concise description>`. Save as learning? (y / n / reword)"
4. If `y` or `reword`, append to `learnings.md` under the right section (Style / Phrasing / Per-project / Per-source). Include date.
5. Skip trivial deltas (typos, whitespace).

Copy the edited draft to clipboard with `pbcopy` if preference says auto-copy, or after "Accept".

### 8. Save daily draft history

Unless `--dry-run`, write all drafts (original + edited) for the day to:
```
~/.claude/skills/project-updates/drafts/<YYYY-MM-DD>.md
```

This is the audit trail — useful for debugging bad learnings later. Append mode if the file exists (multiple runs per day).

### 9. Update preferences

- Set `last-run-timestamp` to now (for `since last run` mode)
- If user consistently skipped a source, nudge: "You've skipped Notion 5 runs in a row — remove from default sources? [y/n]"
- If user always edits in the same direction, confirm the pattern is captured in `learnings.md`

### 10. Summary

End with a one-line tally:
```
Drafted 3 projects · 2 accepted, 1 edited · 2 new learnings saved · Run again tomorrow to continue.
```

## Learnings file format

`~/.claude/skills/project-updates/learnings.md`:

```markdown
# /project-updates Learnings
Last updated: YYYY-MM-DD

## Style
- <rule> — saved <date>

## Phrasing
- <rule> — saved <date>

## Per-project
### <project slug>
- <rule> — saved <date>

## Per-source
### git
- <rule>
### linear
- <rule>

## Corrections log
- <date>: <what was corrected and what pattern was learned>
```

When the file exceeds ~200 lines, consolidate duplicates and archive the rest to `learnings.archive.md` (do this silently, mention once).

## Principles

- **Never auto-post.** Show the draft. User pastes. Non-negotiable — violates the user's stated constraint.
- **Template is law.** Done / In Progress / Next / Blockers in that order, every time, unless `--format narrative`. The four-section template is the default; configure via preferences if your team uses a different ordering.
- **Anchor to last update.** Every draft starts from "what changed since the last posted status update" — no duplicate work credited twice.
- **Graceful degradation.** If Slack/Notion/Gmail are unavailable, skip them. The draft can be made from Linear + git alone.
- **Learnings are earned, not assumed.** Only add to `learnings.md` when the user explicitly confirms a pattern, or when a correction is repeated across runs. Avoid cluttering the file with one-off edits.
- **Claim only your work.** If a PR was reviewed by me but authored by someone else, it's "reviewed X's PR", not "shipped X". Co-ownership always named.
- **Terse beats complete.** One-line bullets win. Detail belongs in the linked PR or ticket.
