---
name: investigate-ci
description: >-
  Investigates GitHub Actions workflow failures for any repo. Fetches recent runs,
  identifies failures, extracts error logs, diagnoses root causes, and suggests fixes.
  Use when a deploy or CI workflow fails and you need to understand why.
argument-hint: <repo, workflow URL, or run URL>
context: fork
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - WebFetch
---

# Investigate CI

Investigate GitHub Actions failures — fetch logs, diagnose root causes, suggest fixes.

## Preferences

_Read `~/.claude/skills/investigate-ci/preferences.md` using the Read tool. If not found, no preferences are set._

## Context

- Current repo: !`gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "not in a repo"`
- Default org: !`gh repo view --json owner -q .owner.login 2>/dev/null || echo "unknown"`

## Command Routing

Check `$ARGUMENTS` for subcommands:

### `help`

If `$ARGUMENTS` is "help" (case-insensitive), display:

```
Investigate CI — diagnose GitHub Actions failures

Usage:
  /investigate-ci <workflow-url>                  Investigate a specific workflow
  /investigate-ci <run-url>                       Investigate a specific run
  /investigate-ci <repo> [workflow]               Investigate by repo name
  /investigate-ci config                          Set preferences
  /investigate-ci reset                           Clear preferences
  /investigate-ci help                            This help

Examples:
  /investigate-ci https://github.com/org/repo/actions/workflows/deploy.yml
  /investigate-ci https://github.com/org/repo/actions/runs/12345678
  /investigate-ci ai-stacks deploy.yml
  /investigate-ci ai-stacks                       All failing workflows
  /investigate-ci 12345678                        Run ID (uses current/default repo)

Current preferences:
  [show from preferences.md or "defaults"]
```

Then stop.

### `config`

If `$ARGUMENTS` is "config" or "configure", use **`AskUserQuestion`**:

**Question 1** — "Default organization?" (multiSelect: false)
- Detect from current repo
- Always ask

**Question 2** — "How many recent runs to check?" (multiSelect: false)
- 5 (quick)
- 10 (default)
- 20 (thorough)

**Question 3** — "Default branch filter?" (multiSelect: false)
- All branches (default)
- Main/prod only
- Current branch

Save to `~/.claude/skills/investigate-ci/preferences.md`. Display summary. Then stop.

### `reset`

If `$ARGUMENTS` is "reset", delete preferences.md. Confirm: "Preferences cleared. Using defaults." Then stop.

### Default (investigate)

If `$ARGUMENTS` is anything else, proceed below.

## Step 1: Parse Input

Extract from `$ARGUMENTS`:

**Full workflow URL** — e.g., `https://github.com/org/repo/actions/workflows/deploy.yml`
- Extract: org, repo, workflow filename

**Full run URL** — e.g., `https://github.com/org/repo/actions/runs/12345678`
- Extract: org, repo, run ID → skip to Step 3 (single run investigation)

**Repo + workflow** — e.g., `ai-stacks deploy.yml`
- Resolve org from preferences or current repo context
- If repo is a short name (no `/`), prepend the detected org

**Repo only** — e.g., `ai-stacks`
- List all workflows, filter to those with recent failures

**Run ID only** — e.g., `12345678`
- Use current repo or default org/repo from preferences

If ambiguous, use `AskUserQuestion` to clarify.

## Step 2: Fetch Recent Runs

```bash
gh run list --repo <org/repo> --workflow <workflow> --limit <N> --json databaseId,status,conclusion,headBranch,event,createdAt,displayTitle,headSha
```

If no workflow specified, list all workflows first:
```bash
gh workflow list --repo <org/repo> --json name,id,state
```
Then fetch runs for workflows with recent failures.

### Present overview

```
Workflow: deploy.yml (org/repo)
Recent runs (last N):

  [FAIL]  #123 — "Deploy to prod" — main — 2h ago
  [PASS]  #122 — "Deploy to staging" — main — 5h ago
  [FAIL]  #121 — "Deploy to prod" — main — 1d ago
  [PASS]  #120 — "Feature X" — feature/x — 1d ago
```

If multiple failures, use `AskUserQuestion`:
- "Which run to investigate?" — list failed runs as options + "Most recent failure (Recommended)"

If only one failure, investigate it directly.

## Step 3: Investigate Failed Run

### 3a. Fetch run details

```bash
gh run view <run-id> --repo <org/repo> --json jobs,conclusion,headBranch,headSha,event,createdAt,updatedAt,displayTitle
```

### 3b. Identify failed jobs

For each failed job, fetch logs:
```bash
gh run view <run-id> --repo <org/repo> --log-failed 2>&1
```

This returns only the logs from failed steps — much more targeted than full logs.

### 3c. Parse errors

From the failed step logs, extract:
- **Error messages**: Lines containing `error`, `Error`, `FAILED`, `fatal`, `Exception`, exit codes
- **Stack traces**: Consecutive indented lines following an error
- **Context**: The 5 lines before the first error (often shows what was being attempted)

### 3d. Check the triggering commit

```bash
gh api repos/<org>/<repo>/commits/<sha> --jq '{message: .commit.message, author: .commit.author.name, date: .commit.author.date, files: [.files[].filename]}'
```

## Step 4: Diagnose

Analyze the error and categorize:

| Category | Signals | Common fixes |
|---|---|---|
| **Dependency** | `ModuleNotFoundError`, `npm ERR!`, `Could not resolve` | Lock file out of sync, missing package |
| **Build** | `tsc`, `SyntaxError`, `TypeError`, compilation errors | Type errors, syntax issues in changed files |
| **Test** | `FAIL`, `AssertionError`, test file paths | Failing tests, snapshot mismatches |
| **Deploy** | `AccessDenied`, `timeout`, `connection refused` | Permissions, infra issues, env vars |
| **Config** | `invalid workflow`, `yaml`, secrets references | Workflow syntax, missing secrets |
| **Flaky** | Same commit passed before, timing-related errors | Re-run, increase timeout |

Cross-reference with:
- The files changed in the triggering commit (do they relate to the error?)
- Whether this workflow passed for the same branch before (regression vs. new issue?)
- Whether main is also failing (systemic vs. branch-specific?)

## Step 5: Present Findings

```
CI Investigation: <workflow> — Run #<id>

Trigger:  <event> on <branch> by <author> (<relative time>)
Commit:   <sha_short> "<commit message>"
Duration: <time>

Failed job: <job name>
Failed step: <step name>

Error:
  <extracted error message, formatted>

Root cause:
  <one-paragraph diagnosis>

Changed files in trigger commit:
  - file1.py
  - file2.ts

Related:
  - [Previous run on same branch: PASS/FAIL]
  - [Main branch status: PASS/FAIL]
```

## Step 6: Suggest Actions

Use `AskUserQuestion` (multiSelect: true):

Options based on diagnosis:
- "Re-run failed job" — `gh run rerun <id> --repo <org/repo> --failed`
- "View full logs" — `gh run view <id> --repo <org/repo> --log`
- "Open in browser" — `gh run view <id> --repo <org/repo> --web`
- "Check if main is also failing" — investigate main branch runs
- "Skip" — done investigating

For code-related failures, also suggest:
- "Read the failing file" — open the file at the error location
- "Compare with last passing run" — diff the commits

## Principles

- **Logs are noisy — extract signal**: Don't dump raw logs. Parse and present the relevant error with context.
- **Always check the commit**: The triggering commit often explains the failure. Show which files changed.
- **Detect patterns**: If the same workflow failed multiple times recently, note it. If main is also broken, flag it as systemic.
- **Read-only by default**: Only re-run jobs if the user explicitly asks. Investigation is safe; re-runs cost compute.
- **Fast first pass**: Show the error quickly. Deep investigation (reading source files, comparing runs) is opt-in via the action menu.
- **Cross-repo capable**: Don't assume the current directory matches the failing repo. Always use `--repo` flags.
