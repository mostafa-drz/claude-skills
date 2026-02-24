---
name: enrich-message
description: >-
  Enriches a draft message with code references, Linear tickets, GitHub links, and
  factual data from the codebase and all available integrations. Outputs polished
  markdown with proper links, ready to copy-paste. Use when responding to PR reviews,
  Slack threads, or any discussion where you want referenceable, factual responses.
argument-hint: [url] [--brief] [--no-linear]
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__list_comments
  - mcp__claude_ai_Linear__list_projects
  - mcp__claude_ai_Linear__get_project
  - mcp__claude_ai_Linear__list_teams
---

# Enrich Message

Enrich a draft message with code references, ticket links, and factual data. Outputs copy-pasteable markdown.

## Preferences

Before starting, use the `Read` tool to read `~/.claude/skills/enrich-message/preferences.md`. If the file does not exist, treat as "no preferences set" and use defaults.

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Remotes: !`git remote -v 2>/dev/null | head -4 || echo "none"`
- Repo root: !`git rev-parse --show-toplevel 2>/dev/null || echo "unknown"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "none"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete preferences, confirm, stop
- **anything else** (including empty) → run the skill

### Help

```
Enrich Message — Enriches draft messages with code references, tickets, and facts

Usage:
  /enrich-message                    Enrich draft from conversation context
  /enrich-message <url>              Enrich with a specific thread URL pre-loaded
  /enrich-message --brief            Keep enrichment concise
  /enrich-message --no-linear        Skip Linear ticket search
  /enrich-message config             Set preferences
  /enrich-message reset              Clear preferences
  /enrich-message help               This help

Examples:
  /enrich-message                    Paste your draft + context in chat, then run
  /enrich-message https://github.com/org/repo/pull/123#discussion_r456
                                     Pre-fetch this PR discussion thread

Current preferences:
  (from preferences.md or defaults)
```

### Config

Use `AskUserQuestion` to collect:

- **Q1: Default GitHub org** — e.g., `A-Teams-Network` (used to resolve short PR refs)
- **Q2: Writing style** — Professional / Casual / Match original tone
- **Q3: Reference depth** — Minimal (links only) / Standard (links + brief context) / Deep (links + code snippets + explanation)

Save to `~/.claude/skills/enrich-message/preferences.md`.

### Reset

Delete `~/.claude/skills/enrich-message/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:

> First time using /enrich-message? Run `/enrich-message config` to set defaults, or just continue with sensible defaults.

Then proceed normally.

## Workflow

### Step 1: Parse inputs

Scan the current conversation for:
- **Draft text** — the user's draft response/comment (may be pasted as text or visible in a screenshot)
- **Context URL(s)** — GitHub PR comment links, Slack thread URLs, or any reference links
- **Screenshots** — read any images the user shared for additional context (comment threads, code diffs)
- **Explicit instructions** — any guidance like "add code references for X" or "mention the ticket for Y"

If `$ARGUMENTS` contains a URL, treat it as the primary context URL.

If inputs are ambiguous, ask:
> I see your draft. What's the context? (paste a URL or describe the thread)

### Step 2: Fetch thread context

Based on the context URL type:

**GitHub PR comment** (`github.com/.../pull/N#discussion_rNNN`):
- Extract owner, repo, PR number, and comment ID from the URL
- Run `gh api repos/{owner}/{repo}/pulls/{pr}/comments` to get the full comment thread
- Run `gh pr view {pr} --repo {owner}/{repo} --json title,body,files,headRefName` for PR context
- Identify the specific file and lines under discussion

**GitHub PR review** (`github.com/.../pull/N#pullrequestreview-NNN`):
- Run `gh api repos/{owner}/{repo}/pulls/{pr}/reviews/{review_id}/comments` for review comments
- Run `gh pr view` for PR context

**GitHub issue** (`github.com/.../issues/N`):
- Run `gh issue view {n} --repo {owner}/{repo} --json title,body,comments`

**Slack thread** (if URL provided):
- Note: Slack MCP not available — ask the user to paste the thread content

**No URL / screenshot only**:
- Extract context from the screenshot content
- Use visible file paths, function names, and discussion text as search seeds

### Step 3: Analyze the topic

From the draft and context, identify:
- **Key claims** — what technical assertions does the draft make? (e.g., "we concatenate files on frontend")
- **Technical concepts** — function names, component names, patterns, architecture decisions mentioned
- **Missing references** — where the draft says something factual but doesn't link to evidence
- **Search seeds** — keywords, file paths, function names to search for in the codebase

### Step 4: Search codebase

For each search seed identified:
1. Use `Grep` to find relevant code across the repo (function definitions, variable names, patterns)
2. Use `Read` to examine matched files for surrounding context
3. Note file paths and line numbers for each reference found

Build code references as GitHub permalink URLs:
- Format: `https://github.com/{owner}/{repo}/blob/{branch}/{path}#L{line}`
- Use the current branch or `main` as appropriate
- If the code is from a PR branch, use that branch's ref

### Step 5: Search Linear (unless --no-linear)

Search Linear for tickets related to the discussion topic:
1. Use `mcp__claude_ai_Linear__list_issues` with keywords from the topic
2. For relevant matches, get details with `mcp__claude_ai_Linear__get_issue`
3. Note ticket identifiers (e.g., AIS-123) and URLs for linking

### Step 6: Search GitHub for related work

Look for additional context:
1. `gh pr list --repo {owner}/{repo} --search "{keywords}" --state all --limit 5` — find related PRs
2. `gh search commits "{keywords}" --repo {owner}/{repo} --limit 5` — find related commits
3. Check other branches if the discussion mentions work-in-progress or upcoming changes

### Step 7: Compose enriched message

Rewrite the draft with enrichments:

1. **Preserve the author's intent** — keep the core message and tone intact
2. **Add inline code references** — link to specific files/lines: `[`filename.ts#L42`](permalink)`
3. **Add ticket references** — mention Linear tickets: `[AIS-123](url)` where relevant
4. **Add PR/commit references** — link related PRs: `[PR #123](url)` or commits
5. **Improve clarity** — fix grammar, tighten phrasing, but don't over-formalize unless configured
6. **Format for the platform**:
   - GitHub comments: use GitHub-flavored markdown, `<details>` blocks for long code snippets
   - Slack: use simpler markdown (bold, links, code blocks)
   - Default: GitHub markdown

Writing style rules:
- Match the formality of the original draft unless preferences say otherwise
- Keep it concise — `--brief` means links only, no extra explanation
- Every factual claim should have a reference (code link, ticket, PR)
- Use relative references where natural ("as implemented in `meetings-tab.tsx`") with the link on the filename

### Step 8: Present output

**Always copy to clipboard** — write the enriched message to `/tmp/enriched-message.md` using the `Write` tool, then run `pbcopy < /tmp/enriched-message.md` via `Bash`. This ensures the user can directly Cmd+V without losing markdown formatting.

After copying, confirm briefly:

> Copied to clipboard. {N} code references, {N} Linear tickets, {N} PR links.
>
> Sources: {list of repos/branches checked}

If any references couldn't be found, mention:
> Could not find code references for: {list}

## Principles

- **Factual, not fabricated** — only reference code, tickets, and links that actually exist. Never invent file paths or line numbers. If a reference can't be found, say so.
- **Preserve the author's voice** — enrich, don't rewrite. The output should sound like the user, just better-sourced.
- **Links must be valid** — every `[text](url)` must point to a real, accessible URL. Use GitHub permalinks with actual commit SHAs or branch names.
- **Read-only** — never post, comment, or modify anything. The user decides when and where to paste.
- **Platform-aware formatting** — GitHub comments support full GFM; Slack needs simpler markdown. Format accordingly.
