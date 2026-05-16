---
name: audit-ui-e2e
description: >-
  Runs a beginner-mind end-to-end UI audit of any running app — local dev
  server, staging, production, or a specific URL. Drives Chrome through every
  interactive element on the target surface, collects structured findings
  (severity, category, where, symptom, impact, repro, triage), and hands the
  result off to `/triage-board` which produces the Desktop folder (schema +
  JSON + Markdown + single-file HTML viewer with MD/CSV/JSON exports and a
  per-finding Copy as Markdown button). Use when you want fresh-eyes
  verification of a feature, page, modal, flow, branch, or whole app — before
  shipping, before review, before a demo, or any time the UI deserves a
  careful poke.
argument-hint: "[<url-or-path>] [--depth quick|standard|thorough] [--scope <what-to-audit>] [--include-destructive] | help | config | reset"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - ToolSearch
---

# Audit UI End-to-End

Walk a running UI with beginner's mind. Drive the browser through every interactive surface inside the target scope, log each rough edge as a structured finding, and ship a triage-board the user can hand to a teammate or paste into a ticket system.

The target can be **anything reachable in a browser** — a local dev server, staging, production, a specific route, a single modal, an entire flow, a deployed PR preview. Branch context is detected and used as enrichment when the URL is on `localhost`, but isn't required.

## Preferences

_On startup, use the `Read` tool to load `~/.claude/skills/audit-ui-e2e/preferences.md`. If missing, use defaults._

Defaults:
- `default-depth`: `standard`
- `auto-open-triage`: `true` (open the resulting viewer in Chrome at the end)
- `destructive-default`: `skip` (Delete / Purge / Drop / Wipe buttons skipped unless `--include-destructive`)
- `localhost-port-hint`: `3000` (used only to ask "should I start the dev server" when localhost is the target and the port is dead)

## Context

_On startup, use Bash to detect (best-effort, skip on failure):_
- _Whether the user is currently in a git repo (`git rev-parse --is-inside-work-tree`)_
- _If so: current branch, recent commits ahead of main, files changed_
- _A Linear/Jira ticket key from the branch name if pattern matches (e.g. `feat/ais-2060-…`)_
- _If the target URL is on `localhost`: whether the port is listening_

_These are used to seed the audit's metadata + plan, not as preconditions. The skill works fine on any URL with no git context._

## Command routing

Check `$ARGUMENTS`:

- `help` → show help, then stop
- `config` → interactive setup, then stop
- `reset` → delete preferences, confirm, then stop
- bare URL or path as first arg → target (e.g. `/audit-ui-e2e https://app.example.com/dashboard` or `/audit-ui-e2e /w/30/meetings`)
- `--scope <description>` → free-text scope hint (e.g. `--scope "the new export buttons in the header"`)
- `--depth quick|standard|thorough` → override default depth
- `--include-destructive` → don't skip destructive actions; clicks Delete/Purge/etc. but honors confirmation dialogs (missing confirms become findings)
- anything else (including empty) → run the audit, ask for target

### Help

```
audit-ui-e2e — Beginner-mind end-to-end UI audit of any running app

Usage:
  /audit-ui-e2e                                Ask for target, then audit
  /audit-ui-e2e <url-or-path>                  Audit a specific URL (or localhost path)
  /audit-ui-e2e <url> --scope "checkout flow"  Narrow the audit to a named surface
  /audit-ui-e2e <url> --depth quick            Hit the headline surfaces only (~5 min)
  /audit-ui-e2e <url> --depth thorough         Walk every reachable interactive (~30+ min)
  /audit-ui-e2e <url> --include-destructive    Test Delete/Drop/Purge (confirms honored)
  /audit-ui-e2e config                         Set defaults
  /audit-ui-e2e reset                          Clear preferences
  /audit-ui-e2e help                           This help

Target accepts:
  - Full URL:    https://app.example.com/dashboard, https://staging.acme.io
  - Local path:  /w/30/meetings  (resolves against localhost:<port-hint>)
  - Just /:      /  (the app root on localhost)

Output: Hands findings to /triage-board, which produces
  ~/Desktop/triage-boards/<scope-or-host>-<YYYY-MM-DD>/
    ├── report.json      — schema-conformant findings
    ├── report.md        — prose mirror
    └── viewer.html      — single-file viewer (MD/CSV/JSON exports + per-finding Copy as Markdown)
```

## First-time experience

If `preferences.md` is missing, show:
> First time using /audit-ui-e2e — quick context: I drive Chrome (via the
> claude-in-chrome MCP) through any URL you point me at. I won't click anything
> destructive unless you pass `--include-destructive`. Output lands in
> `~/Desktop/triage-boards/` via the `/triage-board` skill — open the viewer,
> click any card's `Copy as Markdown` to paste into Linear/GitHub/Notion.
>
> Run `/audit-ui-e2e config` for setup, or continue with defaults (standard
> depth, destructive skipped).

Then proceed.

---

## Workflow

### Step 1 — Confirm target + scope

Inputs determine what's asked:

- **URL/path was provided** as first arg → use it. Resolve `/relative-path` against `http://localhost:<port-hint>` only if a server is listening; otherwise ask.
- **`--scope`** was provided → use it as the audit's narrative goal (e.g. "the new export buttons in the header").
- **Otherwise** → ask via `AskUserQuestion`:
  1. Target — a URL, path, or short description (e.g. "the meeting selector dropdown on /w/30/meetings").
  2. Scope hint — what specifically to focus on, or "broad walkthrough".
  3. Depth — quick / standard / thorough.
  4. Destructive — skip (default) / include.

Show a concise plan derived from the target + scope + (optional) branch context:

```
Target:  http://localhost:3000/w/30/meetings
Scope:   delete-meeting modal flow (recent PR work)
Depth:   standard
Skipping: Upload Transcript (destructive opted-out)

Plan:
  1. Baseline render at the target
  2. Three-dot menu → Delete Meeting → modal open / X / Esc / Cancel
  3. Bulk select + bulk-action header
  4. Cross-check: insight drawer behavior, filter pills, tab counts

Go?
```

If the target is `localhost` and the port is dead, ask: should we start the dev server? (Detect command from `package.json` — `pnpm run dev` / `npm run dev` / `yarn dev`.)

### Step 2 — Load browser tools, attach to a tab

Use `ToolSearch` to load the Chrome MCP tools that aren't already in context:

```
ToolSearch(query: "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__find,mcp__claude-in-chrome__read_console_messages,mcp__claude-in-chrome__read_network_requests,mcp__claude-in-chrome__browser_batch")
```

Then `tabs_context_mcp` to find or create a tab. Prefer reusing an existing tab on the target host; create new only if no match.

### Step 3 — Drive the browser

For each plan bullet:

1. `navigate` to the relevant URL
2. `screenshot` baseline (in-memory — used by the agent to read state, never persisted)
3. Drive the interaction via `computer` / `browser_batch` (click, type, key)
4. `read_console_messages` if anomalies are suspected (filter to `error|warn|TypeError|Hydration`)
5. `read_network_requests` if a fetch is expected and might be silently absent or 4xx/5xx
6. `screenshot` after the interaction (in-memory)
7. On every observed rough edge → record a finding (see Step 4) with a precise `where` + `repro` so the developer can reproduce it without the screenshot

**Beginner-mind heuristics** (what to look for):
- Empty states with "yet" copy on filtered views (implies "no data ever", not "no results for this filter")
- Sticky toasts (not auto-dismissing) — accumulate as wallpaper
- Buttons that look disabled but have no tooltip explaining why
- Mutations that fire success toasts but don't update the visible state
- Destructive actions without confirmation modals
- Stat badges that disappear instead of showing `0`
- Console warnings: a11y, deprecation, missing aria-describedby, React hydration mismatches
- Dropdowns/filters with no clear "active" indicator or no Clear/All option
- Same UI used for semantically-different concepts (Owner field on Decisions vs Action Items)
- URL state inconsistencies (some filters in URL, others not — breaks deep-linking)
- Inputs that clip long values without scroll/wrap
- Buttons placed dangerously close to destructive ones
- Form fields with no required-indicator + no validation feedback
- Modals that don't auto-close on success
- Mismatched terminology across surfaces (button says X, modal title says Y)

**Safety rules:**
- Default: do NOT click anything labeled Delete / Drop / Purge / Wipe / Reset / Disconnect / Sign out / Cancel subscription. Skip and log "destructive — not tested".
- If `--include-destructive`, click them but honor confirmation dialogs. **If a confirmation dialog is missing, that itself is a finding** (this is how PMI's bulk-delete bug was caught).
- Never enter real credentials, real card numbers, real personal data.
- Never click through third-party OAuth/SSO "Approve" / "Authorize" buttons.
- Never submit forms that send real notifications (Slack/email/SMS) unless the user explicitly approved.

### Step 4 — Capture findings

Maintain an in-memory `findings[]` array as the audit progresses. Each finding:

```json
{
  "id": "B1",
  "severity": "critical | high | medium | low | info",
  "category": "bug | ux | accessibility | content | performance | console",
  "title": "One-line summary",
  "where": "specific surface / route / component",
  "symptom": "what you saw (be concrete — quote labels, name elements)",
  "impact": "why it matters to a user",
  "repro": "step-by-step — precise enough that a developer can reproduce in their own browser without the agent's screenshot",
  "triage": "suggested fix direction (not prescriptive)"
}
```

ID convention: `B#` for bugs, `U#` for UX gaps, `C#` for console/perf/a11y. Number sequentially within each prefix as findings are discovered.

Severity calibration:
- **critical** — data loss, security, breaks a primary user journey, or correctness bug on a destructive action
- **high** — silent failure (toast lies, state doesn't update), schema mismatch, blocking ambiguity
- **medium** — cosmetic but real (sticky toast, contradictory labels, badge disappears)
- **low** — accumulated rough edges (missing tooltips, weak active state, copy nits)
- **info** — console noise from 3rd-party, low-priority observations

Findings are text-only. The `repro` field is the contract — a developer reading the report should be able to reproduce the issue in their own browser without ever seeing a screenshot. If you can't write a clean repro, the finding isn't well-scoped yet.

### Step 5 — Synthesize positives + notes

Before handing off to `/triage-board`, collect:
- `positives[]` — things that worked well (deep-linking, drawer behavior, focus rings, etc.). Keep short — 3-8 lines.
- `notes[]` — side effects of testing if any (data destroyed when `--include-destructive`, accounts created, test uploads, etc.). Be specific — name what was modified.

### Step 6 — Hand off to /triage-board

Build the `report.json` payload conforming to the triage-board schema:

```json
{
  "schemaVersion": "1",
  "meta": {
    "title": "<derived from --scope or target host/path>",
    "date": "<today>",
    "tester": "<git user.name or 'agent'>",
    "surface": "<entry URL + brief description>",
    "branch": "<git branch IF localhost AND inside a repo>",
    "scopeIncluded": [...plan bullets that ran...],
    "scopeExcluded": [...skipped items (destructive, unrelated)...]
  },
  "findings": [ ... ],
  "positives": [ ... ],
  "notes": [ ... ]
}
```

Topic slug for the folder, in priority order:
1. `--scope` value (kebab-cased)
2. Linear/Jira ticket key from branch (if detected)
3. Hostname + path slug (e.g. `app-example-com-dashboard`)
4. `ui-audit` as final fallback

Invoke `/triage-board --findings <path-to-report.json> --topic <slug>` (or write the folder directly using triage-board's template at `~/.claude/skills/triage-board/templates/`).

### Step 7 — Open + report

If `auto-open-triage` is on, `open <triage-folder>/viewer.html`. Print a tight summary:

```
Audited {target} — {N} findings, {scope} scope

  Critical: {n}  High: {n}  Medium: {n}  Low: {n}  Info: {n}

Folder:  ~/Desktop/triage-boards/{slug}-{date}/
Viewer:  ~/Desktop/triage-boards/{slug}-{date}/viewer.html

Hand off: open the viewer, click any card's "Copy as Markdown" to paste into Linear/GitHub/Notion.
```

---

## Principles

1. **Beginner's mind, not test plan** — the value is fresh eyes, not exhaustive coverage. Don't pretend to test what you can't; call out what you skipped (`scopeExcluded`).
2. **Capture, don't fix** — this skill audits; it does NOT touch code. Findings go to a triage doc; fixes are the user's decision (or another skill's).
3. **Default safe** — destructive actions are skipped unless explicitly opted in. The user can `--include-destructive` for a more thorough pass when they're on test data.
4. **Any URL, any time** — works on localhost, staging, prod, PR previews, anywhere a browser can reach. Branch + ticket context is enrichment, not a precondition.
5. **Composable with triage-board** — this skill produces structured findings; `/triage-board` produces the artifact. Keep the boundary clean.
6. **Repro is the contract** — text-only findings. A developer reading the report should be able to reproduce the issue in their own browser using just the `where` + `repro` fields, without ever seeing what the agent saw.
7. **No real credentials, no real data** — credentials, personal info, payment methods, and side-effecting third-party flows are off-limits. Always.

## Learned

_Auto-managed. The skill silently adds preferences here when the user corrects a default (e.g. always include destructive, always start at a specific route on this host). Surface once when adding: "Noted: <pattern>. Saved for next time."_
