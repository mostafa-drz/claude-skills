---
name: post-pr-for-review
description: >-
  Generates a contextual Slack message for posting a PR to the team's review channel.
  Pulls context from PR diff, Linear ticket, session conversation, and related PRs to
  write a concise, informative review request. Configurable tone, detail level, and format.
argument-hint: <PR number or URL> [repo-name]
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - AskUserQuestion
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude_ai_Linear__list_comments
---

# Post PR for Review

Generate a contextual Slack message for posting a PR to the team's review channel.

## Preferences

_Read `~/.claude/skills/post-pr-for-review/preferences.md` using the Read tool. If not found, no preferences are set — using defaults._

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Current repo: !`basename $(git rev-parse --show-toplevel 2>/dev/null) 2>/dev/null || echo "unknown"`
- Org: !`gh repo view --json owner -q .owner.login 2>/dev/null || echo "unknown"`
- My open PRs: !`gh pr list --author @me --state open --limit 5 --json number,title,url,headRefName -q '.[] | "#\(.number) \(.title) [\(.headRefName)]"' 2>/dev/null || echo "none"`

## Command Routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete preferences, confirm, stop
- **anything else** → generate the Slack message

### Help

If `$ARGUMENTS` is "help" (case-insensitive), display:

```
Post PR for Review

Generate a Slack message for posting a PR to the team's review channel.

Usage:
  /post-pr-for-review 393                    PR in current repo
  /post-pr-for-review 393 ai-assemble        PR in specific repo
  /post-pr-for-review <github-url>           PR from full URL
  /post-pr-for-review config                 Configure defaults
  /post-pr-for-review reset                  Clear preferences
  /post-pr-for-review help                   Show this help

Context sources:
  PR          Title, description, diff, files changed
  Linear      Linked ticket objective, project, status
  Session     Current conversation, decisions made, files discussed
  Related     Other open PRs in the same project/initiative

Configurable:
  Detail level    Minimal (1 line) | Standard (1-3 lines) | Detailed (with context)
  Tone            Neutral | Conversational
  Extras          Reviewer tags, related PRs, testing notes, side effects
```

Then stop.

### Config

If `$ARGUMENTS` is "config" or "configure" (case-insensitive), use **`AskUserQuestion`**:

**Q1** — "Default detail level?" (multiSelect: false)
- Standard (1-3 sentences) (Recommended)
- Minimal (1 sentence)
- Detailed (with testing notes, side effects, related PRs)

**Q2** — "Default tone?" (multiSelect: false)
- Conversational (Recommended) — natural, like talking to a teammate
- Neutral — factual, no personality

**Q3** — "What to include by default?" (multiSelect: true)
- Linear ticket link (Recommended)
- Related/dependent PRs
- Reviewer tags
- Testing notes
- Side effects / migration notes

**Q4** — "Default GitHub org?" (multiSelect: false)
- A-Teams-Network (Recommended)
- Detect from git remote
- Always ask

Save to `~/.claude/skills/post-pr-for-review/preferences.md`.

Then stop.

### Reset

If `$ARGUMENTS` is "reset" (case-insensitive), delete `~/.claude/skills/post-pr-for-review/preferences.md`, confirm deletion, stop.

### Default

If `$ARGUMENTS` is anything else, proceed below.

## Step 1: Parse Input

Extract from `$ARGUMENTS`:
- **PR number**: Numeric ID
- **Repository**: Second argument, URL, or detect from current git remote

If only a number is given, detect the repo from `gh repo view --json nameWithOwner`.
If a full GitHub URL, parse org/repo/number from it.
If no number given but current branch has an open PR, use that PR automatically.

## Step 2: Gather Context (parallel where possible)

### PR Context
```bash
gh pr view <number> --repo <org/repo> --json title,body,headRefName,baseRefName,url,files,commits,reviewRequests,labels
```

### Linear Context
Extract issue ID from branch name (pattern: `ais-NNN` or `AIS-NNN`).
If found, fetch via `get_issue` with identifier `AIS-NNN`:
- Issue title and objective
- Project name
- Current status
- Related/blocking issues

### Session Context
Review the current conversation for:
- What was discussed about this PR or related work
- Decisions made, trade-offs considered
- Side effects or caveats mentioned
- Testing done or testing notes
- Other PRs that depend on or relate to this one

### Related PRs
If the Linear ticket has related issues, check if any have open PRs:
```bash
gh pr list --state open --limit 10 --json number,title,headRefName,url
```
Filter for PRs whose branch contains a related ticket ID.

## Step 3: Understand the Changes

Build understanding from richest to thinnest source:

1. **Session context** — if we discussed this PR in the current conversation, use that understanding first (it's the most accurate)
2. **PR description** — if it has a good summary, use it
3. **Linear ticket** — objective and deliverables
4. **Diff** — if description is thin and no session context, scan the diff:
   ```bash
   gh pr diff <number> --repo <org/repo> | head -200
   ```
5. **Files changed** — infer scope from file paths (e.g., "touches bot tools", "updates service layer")

## Step 4: Write the Slack Message

Apply preferences (or defaults: standard detail, conversational tone).

### Format by Detail Level

**Minimal:**
```
[1 sentence: what changed]
<PR URL>
```

**Standard (default):**
```
[1-3 sentences: what changed, why it matters, notable detail]
<PR URL>
```

**Detailed:**
```
[1-3 sentences: what changed, why it matters]

[Optional: side effects, testing notes, or reviewer guidance — 1-2 lines]
[Optional: Related: PR #NNN (description)]
[Optional: Linear: AIS-NNN link]

<PR URL>
```

### Writing Rules

- Lead with the *what*, not the ticket ID or PR number
- Use plain language — describe the change as you'd explain it to a teammate
- Mention business impact or user-facing effect when relevant
- Include technical details only if they help reviewers understand scope or risk
- If there are specific reviewers to tag (from preferences or PR reviewRequests), add `@name` naturally
- End with the bare PR URL (Slack will unfurl it)
- Plain text only — no markdown headers, bold, or bullet points (Slack mrkdwn is OK: `*bold*`, `_italic_`, `<url|text>`)
- No emoji unless preferences say otherwise

### Contextual Extras (when preferences enable them)

**Related PRs:** If there are dependent PRs or PRs in the same project, mention them:
```
This is the second of two PRs — first one is #393 (shared service layer).
```

**Testing notes:** If session context includes testing information:
```
Checked Vercel logs on pilot, looks good. Full e2e testing once in prod.
```

**Side effects:** If session context mentions caveats:
```
Note: artifacts created before this week show null for meeting title/date — only affects old data.
```

**Reviewer guidance:** If specific reviewers are relevant:
```
@Anibal — would appreciate a look at the bot tool changes, no functional changes to responses.
```

### Good Examples

```
Deprecates the meetings Supabase table — all meeting data now comes from artifacts API via a shared service layer. Zero blob fetches for meeting insights.
https://github.com/A-Teams-Network/ai-assemble/pull/393
```

```
Refactors Teams bot MPR tools to use the shared meetings service. Removes raw fetch() with hardcoded API keys, reads metadata from artifact instead of blob. Backward compatible — tool input/output shapes unchanged.
https://github.com/A-Teams-Network/ai-assemble/pull/395
```

```
Adds fast signals metrics (impressions, CPM, clicks) via Clickhouse integration.
https://github.com/A-Teams-Network/ai-assemble/pull/307
```

**Detailed example:**
```
Deprecates the meetings Supabase table — all meeting data now comes from artifacts API via a shared service layer. Zero blob fetches for meeting insights.

Builds on Dade's artifact metadata PR (#318). Artifacts before that PR show null for title/date — low priority, can backfill.
Related: #395 (Teams bot refactor using same service layer)
Linear: https://linear.app/ateam-ai/issue/AIS-921

https://github.com/A-Teams-Network/ai-assemble/pull/393
```

### Bad Examples (avoid these)

```
# PR Review Request
**Ticket:** AIS-921
**Summary:** This PR updates the meeting insights handler...
```
Too formatted, leads with ticket ID, uses markdown headers.

```
Please review this PR when you get a chance. It makes some changes to the meetings code.
```
Too vague, no useful information.

## Step 5: Output

Display the generated message in a copyable code block:

```
[generated message here]
```

Then use **`AskUserQuestion`** to offer:
- "Looks good" — done
- "Shorter" — trim to minimal (1 sentence + URL)
- "More detail" — expand with testing notes, side effects, related PRs
- "Add reviewer tags" — ask who to tag
- "Regenerate" — rewrite with different angle

If the user picks "Looks good", confirm and stop.
For other options, apply the adjustment, show the updated message, and offer the same choices again.
