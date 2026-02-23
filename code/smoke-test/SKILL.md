---
name: smoke-test
description: >-
  Traces and verifies that something works end-to-end in any environment.
  Builds a check plan from natural language input, confirms it, then runs each check
  reporting pass/fail. Use when validating deployments, pipelines, features, or migrations.
argument-hint: <describe what to verify>
disable-model-invocation: true
context: fork
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - WebFetch
  - WebSearch
---

# Smoke Test

Trace a resource, event, or feature through the system and verify it works end-to-end.

## Preferences

_Read `~/.claude/skills/smoke-test/preferences.md` using the Read tool. If not found, no preferences are set._

## Project context

- CLAUDE.md: !`test -f CLAUDE.md && echo "present" || echo "not found"`
- Stack: !`ls package.json Cargo.toml pyproject.toml go.mod requirements.txt 2>/dev/null || echo "unknown"`
- Git branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/smoke-test/preferences.md`, confirm, stop
- **anything else** → run smoke test

### Help

```
Smoke Test — Trace and verify something works end-to-end

Usage:
  /smoke-test <natural language>       Build and run a trace plan
  /smoke-test config                   Set environment and verbosity defaults
  /smoke-test reset                    Clear preferences
  /smoke-test help                     This help

Examples:
  /smoke-test uploaded a file to workspace 30 in prod, check the pipeline
  /smoke-test verify login flow on staging
  /smoke-test did my migration run correctly in production?
  /smoke-test check webhook fires after order creation in dev

How it works:
  1. Reads project context (CLAUDE.md, repo structure, APIs)
  2. Builds a trace plan — ordered checks
  3. Confirms the plan with you
  4. Runs each check, reporting pass/fail
  5. Summarizes with diagnosis

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Default environment?" (Production, Staging/Dev, Local, Ask each time (default))
**Q2** — "Trace output verbosity?" (Concise, Detailed, Verbose on failure (default))

Save to `~/.claude/skills/smoke-test/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /smoke-test? Run `/smoke-test config` to set default environment and verbosity, or continue — I'll auto-detect."

Then proceed normally.

## Steps

### 1. Understand the project

Read project context silently:
- CLAUDE.md for conventions, endpoints, commands
- Repo structure (`ls` top-level)
- Tech stack from config files
- API base URLs from CLAUDE.md, .env, or config files
- Integration test files for endpoint patterns
- Available MCP tools in the session

### 2. Parse the request

From `$ARGUMENTS`, extract:
- **What to verify**: Resource, event, or feature to trace
- **Environment**: Where to check (use preference default or detect from input)
- **Identifiers**: IDs, names, values to trace
- **Expected behavior**: What "working" means

If critical info is missing, ask via `AskUserQuestion`.

### 3. Build the trace plan

Build an ordered list of checks. Each check:
- **Check name**: Short description
- **How**: Command or API call
- **Expected**: What passing looks like
- **Depends on**: Previous checks that must pass first

See `reference/check-patterns.md` for heuristics on what to check.

### 4. Confirm the plan

```
Smoke test plan for: [what we're verifying]
Environment: [env]

Checks:
  1. [Check name] — [how, briefly]
  2. [Check name] — [how, briefly]
  3. [Check name] — [how, briefly]

Estimated: [N] API calls
```

Use **`AskUserQuestion`**: "Run this trace plan?" (Run all, Select specific, Add a check, Skip)

### 5. Execute

Run each check sequentially (respecting dependencies):

```
[PASS] Check name
       Key details: value

[FAIL] Check name
       Expected: X
       Got: Y

[SKIP] Check name
       Depends on failed check
```

On failure: show expected vs actual, suggest likely cause, ask to continue or stop.

Output patterns by verbosity preference:
- **Concise**: pass/fail + one-liner
- **Detailed**: full API responses
- **Verbose on failure**: concise for pass, detailed for fail

### 6. Summary

```
Smoke Test Results: [what was verified]
Environment: [env]

  [PASS] X/N checks passed
  [FAIL] Y/N checks failed
  [SKIP] Z/N checks skipped

Failed:
  - [Check]: [one-line reason]

Diagnosis:
  [Root cause or pattern if identifiable]

Suggested next steps:
  - [Action per failure]
```

## Principles

- **Read-only by default**: Never write, mutate, or delete. This is a tracing tool.
- **Be resourceful**: Use curl, gh, MCP tools, database CLIs, log files.
- **Be adaptive**: Every project is different. Use CLAUDE.md and repo structure.
- **Ask when stuck**: Rather than guess, ask. But try hard first.
- **Show your work**: Show commands run and explain what you're checking.
