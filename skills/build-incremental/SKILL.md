---
name: build-incremental
description: >-
  Implements code in progressive, verified increments — auto-detects the project's toolchain,
  builds each unit, runs checks (typecheck, lint, test), fixes errors, and commits with
  semantic messages. Use when building features, implementing milestones, or making multi-step changes.
argument-hint: <what to build>
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# Build

Implement code in progressive, verified increments. Each unit is built, checked, and committed before moving to the next.

## Preferences

!`cat ~/.claude/skills/build-incremental-incremental/preferences.md 2>/dev/null || echo "_no preferences set_"`

## Project context

- Stack: !`ls package.json Cargo.toml pyproject.toml go.mod Makefile 2>/dev/null || echo "unknown"`
- CLAUDE.md: !`test -f CLAUDE.md && echo "present" || echo "not found"`
- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Status: !`git status --short 2>/dev/null || echo "clean"`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/build-incremental-incremental/preferences.md`, confirm, stop
- **`--dry-run <description>`** → show the plan without executing then stop
- **`--no-commit <description>`** → build and verify but don't commit
- **`--skip-lint <description>`** → skip linting, only run type checks
- **anything else** → proceed with build

### Help

```
Build — Implement code in verified increments

Usage:
  /build-incremental <what to build>             Build incrementally with checks + commits
  /build-incremental --dry-run <description>     Show plan without executing
  /build-incremental --no-commit <description>   Build and verify, don't commit
  /build-incremental --skip-lint <description>   Skip lint, only typecheck
  /build-incremental config                      Set toolchain and commit preferences
  /build-incremental reset                       Clear preferences
  /build-incremental help                        This help

Examples:
  /build-incremental add user settings page with form validation
  /build-incremental Milestone 2 from IMPLEMENTATION_PLAN.md
  /build-incremental --dry-run refactor auth middleware

How it works:
  1. Detects your toolchain (or reads from preferences)
  2. Breaks work into committable units
  3. For each unit: implement → check → fix → commit
  4. Reports summary with all commits

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Type check command?" (auto-detect (default), custom command)
- Auto-detect looks for: `pnpm typecheck`, `npm run typecheck`, `tsc --noEmit`, `cargo check`, `go vet`, `mypy .`, `pyright`

**Q2** — "Lint command?" (auto-detect (default), custom command, skip)
- Auto-detect looks for: `pnpm lint`, `npm run lint`, `cargo clippy`, `golangci-lint run`, `ruff check`

**Q3** — "Lint fix command?" (auto-detect (default), custom command, skip)
- Auto-detect looks for: `pnpm lint:fix`, `npm run lint:fix`, `cargo clippy --fix`, `ruff check --fix`

**Q4** — "Commit style?" (conventional (default) — `feat:`, `fix:`, etc.; simple — plain messages; project-default — read from CLAUDE.md)

**Q5** — "Unit size?" (small — 1-2 files per commit; medium — 3-5 files (default); large — whole milestone)

Save to `~/.claude/skills/build-incremental-incremental/preferences.md`.

## First-time detection

If no preferences file exists:

1. Auto-detect the toolchain from project files:
   - `package.json` → check for `typecheck`, `lint`, `lint:fix` scripts, detect `pnpm`/`npm`/`yarn` from lockfile
   - `Cargo.toml` → `cargo check`, `cargo clippy`
   - `pyproject.toml` / `requirements.txt` → `mypy`, `ruff`, `pyright`
   - `go.mod` → `go vet`, `golangci-lint`
   - `Makefile` → check for `lint`, `check` targets

2. Show: "Detected: [toolchain]. Run `/build-incremental config` to customize, or continue with these defaults."

3. Proceed normally.

## Build process

### Step 1: Understand scope

1. Read context:
   - CLAUDE.md for project conventions
   - IMPLEMENTATION_PLAN.md if it exists and `$ARGUMENTS` references a milestone
   - Existing code in the target area
   - Related components for pattern consistency
2. Break work into committable units (size based on preference)
3. Order: types/interfaces first → logic/providers → components → pages/routes

If `--dry-run`, show the plan and stop.

### Step 2: Implement one unit

Write the code for one unit. Follow project conventions from CLAUDE.md. Read existing code before modifying.

### Step 3: Verify

Run checks in this order:

**Type check:**
```
{typecheck command from preferences or auto-detected}
```
If fails: read errors, fix, re-run until passing.

**Lint:**
```
{lint command}
```
If fails:
1. Run lint fix: `{lint fix command}`
2. Fix remaining issues manually
3. Re-run until passing (warnings OK, errors not)

Skip lint if `--skip-lint` flag.

### Step 4: Commit

Skip if `--no-commit` flag.

- Stage specific files (never `git add -A` or `git add .`)
- Commit with semantic message based on style preference:
  - **conventional**: `feat(scope): description`, `fix(scope): description`, `refactor: description`
  - **simple**: plain descriptive message
  - **project-default**: follow CLAUDE.md conventions
- Under 72 characters
- Describe what changed, not which files

### Step 5: Repeat or complete

Check if more units remain. If yes → Step 2. If no → summary.

## Completion summary

```
Build complete: {description}

Commits:
  1. {hash} {message}
  2. {hash} {message}

Verification:
  ✓ Type check: no errors
  ✓ Lint: no errors

{If milestone: Next milestone: {name} or "none remaining"}
```

## Rules

- **Never skip verification** — every commit must pass checks
- **Never commit unrelated changes together** — one unit per commit
- **Never use `git add .`** — always add specific files
- **Never amend previous commits** unless explicitly asked
- **Fix forward** — if checks fail, fix and re-verify, don't revert
- **Read before writing** — always read existing code first
- **Ask when uncertain** — if scope is ambiguous, ask before implementing
