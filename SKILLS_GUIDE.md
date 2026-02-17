# Personal Claude Skills — Design Guide

Standards and conventions for all personal skills in `~/.claude/skills/`.

---

## Frontmatter conventions

```yaml
---
name: skill-name                          # lowercase, hyphens, max 64 chars
description: >-                           # MUST be third person, include trigger keywords
  Creates X from Y. Analyzes Z and suggests actions.
  Use when [trigger scenario].
argument-hint: <arg> [optional-arg]       # shown in autocomplete
disable-model-invocation: true            # REQUIRED for skills with side effects
allowed-tools:                            # only tools the skill actually needs
  - AskUserQuestion
  - Bash
---
```

### Rules

1. **Descriptions are third person** — they're injected into the system prompt as metadata. "Creates..." not "Create...".
2. **`disable-model-invocation: true`** — required for any skill that creates, modifies, pushes, or posts anything (PRs, tickets, comments, branches, files outside the repo).
3. **`allowed-tools`** — list only what's needed. Don't grant `Write`/`Edit` to read-only skills.
4. **MCP tools** — use `mcp__claude_ai_Linear__*` as the canonical Linear prefix (cloud-hosted, always available). Do NOT duplicate with `mcp__linear-server__*`.

---

## Subcommand pattern

Every skill supports these subcommands via `$ARGUMENTS`:

```
/skill help       Show usage, examples, current preferences
/skill config     Interactive setup via AskUserQuestion
/skill reset      Clear saved preferences
/skill [args]     Run the skill (default)
```

### Help format

```
Skill Name — one-line description

Usage:
  /skill [args]              Default behavior
  /skill config              Set preferences
  /skill reset               Clear preferences
  /skill help                This help

Options:
  --flag                     What it does

Examples:
  /skill something           Concrete example

Current preferences:
  key: value (or "default")
```

### Config

- Use `AskUserQuestion` with clear options
- Display summary after collecting answers
- Save to preferences file (see Memory section)

### Reset

- Delete the preferences file
- Confirm: "Preferences cleared. Using defaults."

---

## Memory and preferences

Each skill persists preferences at:

```
~/.claude/skills/<skill-name>/preferences.md
```

### Format

```markdown
# /<skill-name> preferences
Updated: 2026-02-17

## Defaults
- key: value
- key: value

## Learned
- Pattern observed from user behavior
```

### How it works

1. **Read on startup** via `!`cat ~/.claude/skills/<name>/preferences.md 2>/dev/null``
2. **Write after config** — save explicitly chosen preferences
3. **Learn silently** — when the user corrects a default (changes base branch, removes a section, picks a different format), save that preference and mention it: "Noted: you prefer X. Saved for next time."
4. **Human-readable** — the user can edit the file directly

### What to save

- Explicit config choices (base branch, template style, default source folder)
- Corrections to defaults (user changed something the skill inferred)
- Recurring patterns (user always skips a section, always picks the same team)

### What NOT to save

- Session-specific state (current task, in-progress work)
- Sensitive data (API keys, tokens, credentials)
- One-off choices that don't indicate a pattern

---

## First-time experience

On first invocation, detect if `preferences.md` exists. If not:

1. Show a one-liner suggestion (not a blocker):
   ```
   First time using /skill? Run `/skill config` to set defaults, or just continue with sensible defaults.
   ```
2. Proceed with the skill normally — don't force setup
3. After completion, if the user made choices worth saving, save them silently

---

## Dynamic context injection

Use `!`command`` to pre-fetch context before Claude sees the prompt. This saves tool calls.

```markdown
## Context
- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Status: !`git status --short 2>/dev/null || echo "clean"`
- Stack: !`ls package.json Cargo.toml pyproject.toml go.mod 2>/dev/null || echo "unknown"`
```

Use for: git state, project detection, file existence checks.
Don't use for: large outputs, commands that may hang, anything requiring auth.

---

## Content guidelines

1. **Under 500 lines** — move reference material to bundled files (`examples/`, `reference/`)
2. **Don't repeat what Claude knows** — skip generic instructions about JSON format, git basics, etc.
3. **Numbered checklists** for workflows — easier to follow than prose
4. **Validation loops** — after any action, verify it worked before moving on
5. **Graceful degradation** — if a tool/command isn't available, skip and continue

---

## File structure

```
~/.claude/skills/
├── SKILLS_GUIDE.md              ← this file
├── skill-name/
│   ├── SKILL.md                 ← main instructions (under 500 lines)
│   ├── preferences.md           ← persisted user preferences (auto-managed)
│   ├── examples/                ← reference examples (loaded on demand)
│   │   └── sample.md
│   └── reference/               ← detailed docs (loaded on demand)
│       └── patterns.md
```

---

## Skill inventory

| Skill | Purpose | Side effects | MCP |
|---|---|---|---|
| `/aws-mfa` | AWS MFA authentication | Yes (writes AWS config) | No |
| `/slack-to-ticket` | Slack thread → Linear issue | Yes (creates issue) | Linear |
| `/thread-to-action` | Thread → suggested actions | Yes (executes actions) | Linear |
| `/smoke-test` | E2E trace and verification | No (read-only) | No |
| `/whats-next` | Suggest top 3 next actions | Yes (executes actions) | Linear |
| `/address-pr-comments` | PR comment review + fixes | Yes (edits code, posts replies) | Linear |
| `/build-incremental` | Incremental verified coding | Yes (commits code) | No |
| `/create-pr` | Create structured PRs | Yes (creates PR) | Linear |
| `/organize-screenshots` | Organize screenshots | Yes (copies files) | No |
| `/post-ticket-summary` | Post impl summary to Linear | Yes (posts comment) | Linear |
| `/sync-branch` | Merge branches | Yes (pushes) | No |
| `/investigate-ci` | Diagnose GitHub Actions failures | No (read-only) | No |
| `/audit-skills` | Audit skills against manifest + upstream docs | No (read-only, fix mode optional) | No |
| `/publish-skills` | Publish skills to GitHub repo | Yes (commits, pushes) | No |
