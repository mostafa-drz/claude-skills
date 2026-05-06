---
name: address-pr-feedback
description: >-
  Comprehensively addresses PR feedback by fetching all comments, deploying parallel agents 
  for critical analysis of each suggestion, making implementation decisions, then systematically 
  implementing fixes with incremental commits and browser validation. Use when you need to 
  systematically process and implement all PR review feedback with due diligence validation.
argument-hint: <pr-number|url> [--dry-run] [--auto-push] [--no-browser]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Edit  
  - Glob
  - Grep
  - Bash(git *)
  - Bash(gh *)
  - Agent
  - mcp__claude-in-chrome__tabs_context_mcp
  - mcp__claude-in-chrome__tabs_create_mcp
  - mcp__claude-in-chrome__navigate
  - mcp__claude-in-chrome__read_page
  - mcp__claude-in-chrome__find
  - mcp__claude-in-chrome__computer
---

# Address PR Feedback

Comprehensive PR review workflow that fetches all comments, uses parallel agents for critical analysis, makes implementation decisions, then systematically addresses valid concerns with incremental commits and browser validation.

## Preferences

_On startup, use Read to load `~/.claude/skills/address-pr-feedback/preferences.md`. If file doesn't exist, use defaults._

## Context

_On startup, use Bash to detect: current git branch, git status, repo name, and check for localhost development server. Skip any that fail._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop  
- **`reset`** → delete preferences file, confirm, stop
- **PR number/URL with optional flags** → run the workflow

### Help

```
Address PR Feedback — Systematic PR review implementation with agent validation

Usage:
  /address-pr-feedback <pr-number|url>              Process all PR feedback
  /address-pr-feedback #123 --dry-run              Analyze only, no changes
  /address-pr-feedback #123 --auto-push            Skip push confirmation
  /address-pr-feedback #123 --no-browser           Skip browser validation
  /address-pr-feedback config                      Set preferences
  /address-pr-feedback reset                       Clear preferences
  /address-pr-feedback help                        This help

Examples:
  /address-pr-feedback #123                        Full workflow for PR 123
  /address-pr-feedback https://github.com/owner/repo/pull/456
  /address-pr-feedback #789 --dry-run --no-browser

Current preferences:
  localhost-port: 3000 (or "auto-detect")
  browser-validation: enabled (or "disabled")  
  auto-commit: true (or "false")
  agent-analysis: parallel (or "sequential")
```

### Config

Use `AskUserQuestion` to collect:

- **Q1: Default localhost port** — 3000, 3001, 4000, auto-detect
- **Q2: Browser validation** — Always validate, Skip for non-UI changes, Always skip
- **Q3: Commit behavior** — Auto-commit after each fix, Ask before each commit
- **Q4: Agent analysis** — Parallel (faster), Sequential (more thorough)

Save responses to `~/.claude/skills/address-pr-feedback/preferences.md`.

### Reset

Delete `~/.claude/skills/address-pr-feedback/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:

> First time using /address-pr-feedback? Run `/address-pr-feedback config` to set defaults, or just continue with sensible defaults.

Then proceed with the workflow.

## Workflow

### 1. Gather PR context

- Parse PR number/URL from `$ARGUMENTS`
- Use `gh pr view <number> --repo <repo> --json comments,files,title,body` to fetch all data
- Check git status and current branch
- Validate we're in the right repository

### 2. Organize feedback table

Create table with all comments:

| # | Author | File:Line | Comment |
|---|--------|-----------|---------|
| 1 | reviewer1 | src/app.ts:42 | This function could be optimized... |
| 2 | claude | README.md:15 | Missing installation steps |

Display table to user for visibility.

### 3. Deploy parallel agents

For each comment row:
- Spawn `Agent` with specific analysis prompt
- Task: "Critically analyze this PR comment. Is it valid? What's the implementation effort? What are the risks if ignored?"
- Run all agents in parallel for efficiency
- Collect responses when complete

### 4. Collect agent analysis  

Create enhanced table:

| # | Author | File:Line | Comment | Agent Opinion | Implementation Effort |
|---|--------|-----------|---------|---------------|---------------------|
| 1 | reviewer1 | src/app.ts:42 | This function... | Valid concern, performance impact | Medium - refactor needed |
| 2 | claude | README.md:15 | Missing steps | Critical for users | Low - add 3 lines |

### 5. Make implementation decisions

Review agent analysis and decide what to address:

| # | Action | Reasoning | Change Summary |
|---|--------|-----------|---------------|
| 1 | ✅ Address | Performance critical, user-facing | Refactor function, add caching |
| 2 | ✅ Address | Documentation gap blocks users | Add installation section |
| 3 | ❌ Skip | Edge case, minimal value | N/A |

Ask user to confirm the implementation plan before proceeding.

### 6. Implement fixes incrementally

For each ✅ item:

1. **Make the change** - Edit files as needed
2. **Validate syntax** - Run `npm run typecheck` or equivalent  
3. **Browser test** - Navigate to localhost, verify the change works
4. **Clean commit** - `git add <specific-files>` and `git commit -m "fix: <specific-issue>"`
5. **Progress update** - Mark item complete, move to next

Stop and ask user if any change seems complex or risky.

### 7. Final verification & summary

- **Complete browser test** - Full app walkthrough on localhost
- **Run all checks** - TypeScript, ESLint, tests if available  
- **Summary table** - Show what was completed

| Item | Status | Files Changed | Commit |
|------|--------|---------------|--------|
| Function optimization | ✅ Done | src/app.ts | abc1234 |
| README updates | ✅ Done | README.md | def5678 |

### 8. Reply to comment threads

For each ✅ addressed item with a specific comment ID:

- Use GitHub API to add reply to the original comment thread
- **NEVER edit original reviewer comments** - always add replies
- Format: `gh api repos/<org>/<repo>/pulls/<pr>/comments --method POST --field body="✅ **FIXED** in commit [SHA](link)" --field in_reply_to=<comment_id>`
- One reply per comment thread showing exactly which commit addressed the feedback

### 9. Push changes

- Show `git log --oneline -n <count>` of new commits
- Ask for push confirmation (unless `--auto-push` flag used)  
- `git push origin <current-branch>`
- Report success and suggest next actions (merge, request re-review)

## Flag handling

- **`--dry-run`** - Stop after step 5 (implementation decisions), don't make changes
- **`--auto-push`** - Skip final push confirmation in step 8
- **`--no-browser`** - Skip browser validation in step 6, only run syntax checks

## Error handling

- **No PR comments found** - Report "No feedback to address" and exit gracefully
- **Agent spawn failures** - Continue with manual analysis for failed items
- **Browser validation fails** - Stop, show error, ask user how to proceed
- **Git conflicts** - Stop, guide user to resolve, offer to resume

## Principles

1. **One commit per logical fix** - Each addressed comment gets its own clean commit with descriptive message
2. **Always validate before proceeding** - Browser test after every change, TypeScript check before commits  
3. **Fail fast on complexity** - If a change seems large or risky, stop and ask user for guidance
4. **Preserve agent analysis** - Show tables throughout so user can see the reasoning behind decisions
5. **Non-destructive by default** - Use `--dry-run` to analyze first, then implement with full visibility
6. **Never edit original reviewer comments** - Always add replies to comment threads, never modify someone else's feedback