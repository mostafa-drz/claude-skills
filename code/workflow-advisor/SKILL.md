---
name: workflow-advisor
description: >-
  Analyzes recent Claude Code conversations and local Claude state (skills, settings, memory files,
  CLAUDE.md), researches the latest Claude Code features and best practices online, and suggests
  one workflow improvement at a time with reasoning and a concrete action item. Can save accepted
  suggestions to memory for tracking. Use when you want to discover underused Claude Code features,
  improve your development workflow, stay current with the latest Claude Code capabilities, or
  get a periodic workflow health-check.
argument-hint: [--all] [--count <n>]
disable-model-invocation: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - WebSearch
  - WebFetch
  - AskUserQuestion
---

## Preferences

On startup, use the Read tool to load `~/.claude/skills/workflow-advisor/preferences.md`.
If the file does not exist, treat as "no preferences set" and proceed with defaults.

---

## Context

_On startup:_
1. **Active conversation**: The current conversation history is already in scope — use it directly.
2. **Conversation files**: Use Bash to list recent conversation files:
   ```
   ls -lt ~/.claude/projects/*/conversations/ 2>/dev/null | head -20
   ```
   Fall back to: `find ~/.claude/projects -name "*.jsonl" -newer /tmp -type f 2>/dev/null`
   Skip gracefully if no files found.
3. **Local state**: Use Glob to find: `~/.claude/settings*.json`, `~/.claude/skills/*/SKILL.md`, `~/.claude/projects/*/memory/MEMORY.md`, `CLAUDE.md` files in the current project.
4. **Date filter**: Default to today unless `--all` flag is set or user specifies a range.

---

## Command routing

Check `$ARGUMENTS`:
- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/workflow-advisor/preferences.md`, confirm, stop
- **`--all`** → scan all available conversations (not just today)
- **`--count <n>`** → present N suggestions at once instead of one at a time
- **anything else** (including empty) → run the skill

### Help

```
Workflow Advisor — Claude Code workflow improvement suggestions

Usage:
  /workflow-advisor                  Analyze today's conversations + suggest 1 improvement
  /workflow-advisor --all            Scan all conversations (not just today)
  /workflow-advisor --count <n>      Get N suggestions at once
  /workflow-advisor config           Set preferences
  /workflow-advisor reset            Clear preferences
  /workflow-advisor help             This help

What it does:
  1. Reads your recent Claude conversations (current session first)
  2. Checks your local Claude state: skills, settings, memory, CLAUDE.md
  3. Searches for the latest Claude Code features and updates
  4. Suggests one workflow improvement at a time with reasoning + action item
  5. Optionally saves accepted suggestions to memory

Current preferences:
  (shown from ~/.claude/skills/workflow-advisor/preferences.md)
```

### Config

Use `AskUserQuestion` to collect:
- **Q1: Default conversation scope** — Today only / Last 7 days / All conversations
- **Q2: Suggestions per run** — One at a time (interactive) / All at once (summary)
- **Q3: Auto-save accepted suggestions to memory** — Yes / No

Save answers to `~/.claude/skills/workflow-advisor/preferences.md`.

### Reset

Delete `~/.claude/skills/workflow-advisor/preferences.md` and confirm: "Preferences cleared. Using defaults."

---

## First-time detection

If no preferences file exists, show:

> First time using /workflow-advisor? Run `/workflow-advisor config` to set defaults, or just continue — defaults are: today's scope, one suggestion at a time.

Then proceed normally.

---

## Workflow

### Step 1 — Gather conversation context

- If the **current session** has meaningful conversation history (more than a few turns), use that as the primary input.
- Otherwise, use Bash to find today's (or scoped) conversation `.jsonl` files under `~/.claude/projects/`.
- If `--all` is set, scan all available conversations.
- Read the 3 most recent conversation files if files are found (don't read all — keep it fast).
- **If in doubt whether to use session history vs. files**, use `AskUserQuestion` to confirm with the user.

### Step 2 — Read local Claude state

Use Glob + Read to collect:
1. `~/.claude/settings.json` and `~/.claude/settings.local.json` — installed MCP servers, hooks, permissions
2. `~/.claude/skills/*/SKILL.md` — skill names, purposes, tools used
3. `~/.claude/projects/*/memory/MEMORY.md` — any saved memory relevant to workflow
4. `CLAUDE.md` in current project — project-level rules and constraints

Summarize internally: which skills exist, which MCP tools are configured, what rules are in place.

### Step 3 — Research latest Claude Code features

Use WebSearch + WebFetch to check for recent updates:
- Search: `"Claude Code" changelog features 2026`
- Search: `Claude Code hooks MCP tools new features`
- Fetch the Claude Code docs changelog if available
- Look for: new slash commands, new hook events, new MCP integrations, model updates, SDK changes

Compile a short internal list of features/capabilities that exist in the latest Claude Code but are not reflected in the user's current setup.

### Step 4 — Identify improvement opportunities

Cross-reference what you found in Steps 1–3 against what the user is doing now. Look for:

- **Unused built-in commands** — `/insight`, `/memory`, `/doctor`, etc. not being used
- **Missing skills** — common workflows done manually that could be a skill
- **Outdated patterns** — skills or CLAUDE.md rules that conflict with newer Claude Code behavior
- **MCP opportunities** — available MCP servers (GitHub, Notion, Slack, etc.) not yet configured
- **Hook opportunities** — pre/post tool hooks that could automate repetitive steps
- **Model/context gaps** — not using extended context, or using the wrong model for a task type
- **Workflow friction** — patterns in conversations suggesting repeated manual steps

Rank by impact × ease. Prepare suggestions in order.

### Step 5 — Present suggestions (one at a time by default)

For each suggestion, use this exact format:

```
## Suggestion: [Short Title]

**Why**: [One sentence — what pattern or gap triggered this, grounded in what you saw]

**Action**: [Specific, concrete step — a command to run, a skill to create, a setting to add]

**Impact**: [One line — what friction this removes or capability it unlocks]
```

After presenting one suggestion, ask:

> Next: **[Next suggestion title]** — want to see it, save this one to memory, or stop?

Options via `AskUserQuestion`:
- "Next suggestion"
- "Save this to memory + next"
- "Save this to memory + stop"
- "Skip + next"
- "Done"

### Step 6 — Save accepted suggestions (if requested)

If the user chose to save a suggestion, append to `~/.claude/projects/<current-project>/memory/MEMORY.md`
or `~/.claude/skills/workflow-advisor/saved-suggestions.md` if no project memory exists.

Format to save:
```
## Workflow Improvement — [Date]: [Title]
- **Action**: [action item]
- **Status**: Pending
```

Confirm: "Saved to memory. You can track this in your next session."

---

## Principles

1. **One suggestion at a time** — don't overwhelm. Each suggestion should be immediately actionable in under 10 minutes.
2. **Ground every suggestion in evidence** — cite the conversation pattern, local state, or doc source that triggered it. No generic advice.
3. **Concrete over vague** — "Add a `/standup` skill that reads your Linear issues" beats "consider automating standups".
4. **Don't suggest what's already in place** — check existing skills and CLAUDE.md before suggesting something the user has already done.
5. **Respect preferences** — if the user has explicit rules in CLAUDE.md (e.g., "never run pnpm dev"), don't suggest workflows that conflict with them.
