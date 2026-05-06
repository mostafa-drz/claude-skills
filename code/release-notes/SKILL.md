---
name: release-notes
description: >-
  Generates brief, truth-based release notes for a release PR (typically main → prod)
  by listing each squash-merged PR, a one-paragraph summary drawn from each PR body,
  and the linked issue-tracker tickets (Linear, Jira, GitHub Issues, Asana, ClickUp,
  Shortcut, Plane, etc. — any tracker, configured via a URL template). Use when
  opening or updating a release PR.
argument-hint: [pr-number]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
---

# Release Notes

Generate release notes for a release PR. Brief, truth-based, no fabrication.

## Configuration

_On startup, use the `Read` tool to load `~/.claude/skills/release-notes/preferences.md`._

Tracker-agnostic — works with **any** issue tracker (Linear, Jira, GitHub Issues, Asana, ClickUp, Shortcut, Plane, Notion, custom). You configure two things: how to *detect* ticket IDs in PR bodies, and how to *link* them.

Expected keys:

```markdown
- ticket-prefix: <PREFIX>                    # Optional. Tracker key — e.g., ENG, PROJ, ABC, JIRA. Used to detect IDs as <PREFIX>-NNNN. If unset, falls back to the generic regex [A-Z]{2,5}-\d+ (any uppercase prefix + dash + digits).
- ticket-url-template: <url-with-{TICKET}>   # Optional. URL template with literal `{TICKET}` placeholder. Examples:
                                             #   Linear:        https://linear.app/myorg/issue/{TICKET}
                                             #   Jira:          https://myteam.atlassian.net/browse/{TICKET}
                                             #   GitHub Issues: https://github.com/myorg/myrepo/issues/{TICKET}
                                             #   Asana:         https://app.asana.com/0/{TICKET}
                                             #   Shortcut:      https://app.shortcut.com/myorg/story/{TICKET}
                                             #   Plane:         https://app.plane.so/myorg/projects/.../issues/{TICKET}
                                             # If unset, ticket IDs render as bare text without links.
```

Behavior when keys are missing:
- No `ticket-prefix` → use the generic regex `[A-Z]{2,5}-\d+`. Works for most trackers.
- No `ticket-url-template` → render bare ticket IDs (e.g., `Closes ENG-1234.`). Mention once at the end: "Set `ticket-url-template` in preferences.md to enable clickable ticket links."

## Hard rules

1. **Truth only.** Every claim must be sourced from a merged PR's actual title/body. Never invent features, motivations, or impact statements that aren't in the source PRs.
2. **Brief.** Each PR section is **1–3 sentences max**. Cut file enumerations, architecture diagrams, dead-code lists, "what changed" prose blocks. Mirror the source PR's `## Summary`, not its full body.
3. **Never `git add -A`** and never push the release notes without showing them to the user first and getting explicit approval.
4. **No drive-bys.** Do not add commentary, suggestions, or "follow-ups" the source PRs didn't flag.

## Steps

### 1. Resolve the release PR

- If `$ARGUMENTS` is a number → that's the PR.
- Else → `gh pr list --base prod --state open --limit 5 --json number,title,headRefName` and ask the user which one if multiple, or use the only open one.
- Capture: `number`, `title`, `baseRefName`, `headRefName`, `url`.

### 2. List the squash-merged PRs in the release

```bash
gh pr view <release-pr> --json commits --jq '.commits[].messageHeadline'
```

Each squash-merged commit headline ends in `(#NNN)` — extract the PR numbers. If `commits` is sparse (squash-merge collapsed history), fall back to:

```bash
git log origin/<base>..origin/<head> --oneline
```

and grep `(#\d+)` from the headlines.

### 3. Fetch each child PR

For each PR number, in parallel:

```bash
gh pr view <num> --json title,body,number,url,labels
```

Extract from each:
- `title` (use as section heading after stripping conventional-commit prefix if helpful)
- `## Summary` paragraph (or first 1-3 sentences of the body if no Summary section)
- Issue-tracker ticket IDs from anywhere in the body — match `<TICKET-PREFIX>-NNNN` (where `TICKET-PREFIX` comes from preferences, falling back to `[A-Z]{2,5}-\d+`). When `ticket-url-template` is set, substitute `{TICKET}` to build the link; otherwise render the bare ticket ID.
- PR URL (for the `#NNN` link, GitHub auto-links)

If a PR's Summary is more than ~3 sentences, **halve it, then halve again**. Keep only the user-visible/product-visible bits. Cut implementation prose ("service-side normalizers", "Zod widens", file paths) unless that *is* the product change.

### 4. Build the body

Template:

```markdown
## What's in this release

**1. <Short topic — strip cc-prefix> — #<PR>**
<1–3 sentence summary, sourced from the PR body. User-visible framing.>

Closes [<TICKET>](<ticket-url-template with {TICKET} substituted>)<` · [<TICKET-2>](...)` if multiple>. If no template configured, render as `Closes <TICKET>.` (no link).

**2. <Short topic> — #<PR>**
<1–3 sentences.>

Closes [<TICKET>](...).

## How to test

- <One bullet per PR — pulled from that PR's test plan, simplified to the manual-verify path.>
- <...>
```

If — and only if — a source PR explicitly flags a follow-up that *blocks* prod (deploy ordering, flag flip, infra step), add:

```markdown
## Follow-ups

- <The blocking item, verbatim from the source PR.>
```

Otherwise, skip the Follow-ups section. Do not invent follow-ups.

### 5. Title

Format: `Release YYYY-MM-DD — <2–6 word theme>`

The theme should name the 1–2 biggest user-visible changes (e.g., "PMI UI + migration cleanup"). Use today's date.

### 6. Show, then push

Print the full proposed title + body to the user. Then ask:

> Push this to PR #<num>? (yes / edit / no)

- **yes** → write the body to a temp file, then push via REST (works around the Projects-classic GraphQL deprecation that blocks `gh pr edit` on this org):
  ```bash
  gh api -X PATCH "repos/<org>/<repo>/pulls/<num>" \
    -f title="<title>" \
    -F body=@/tmp/pr-<num>-body.md \
    --jq '"OK: " + .title + " — " + .html_url'
  ```
  Try `gh pr edit` first if you prefer; if it errors with `Projects (classic) is being deprecated`, fall back to the REST call above. The edit *does not* land on the GraphQL failure — always verify via `gh pr view <num> --json title --jq .title`.
- **edit** → ask what to change, regenerate, ask again
- **no** → leave the PR alone, exit

### 7. Verify

After push, `gh pr view <num> --json title,body --jq '.title'` to confirm the edit landed. Report the URL.

## Style reminders (drawn from user prefs)

- Cut: file paths, line counts, "Adds/Removes/Migrates" tables, architecture diagrams, Figma node IDs, internal scaffolding details.
- Keep: what changed *for the user*, what it closes, how to verify it on staging.
- If a source PR is purely internal (refactor, test infra, dep bump) and has no user-visible surface, still list it but flag it as such in one sentence: "Internal — <one-liner>." No padding.
- If two source PRs are part of the same chunked feature, group them under one numbered section with both `#NNN` links rather than splitting.
