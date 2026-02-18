---
name: skill-creator
description: >-
  Creates new Claude Code skills interactively by asking contextual questions
  about purpose, side effects, tools, and workflow. Generates a complete SKILL.md
  following all conventions from SKILLS_GUIDE.md. Use when creating a new skill
  or when asking to scaffold a skill.
argument-hint: [skill-name] [--from-description "..."]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
---

# Skill Creator

Create new Claude Code skills interactively, following all conventions from SKILLS_GUIDE.md.

## Preferences

Before starting, use the `Read` tool to read `~/.claude/skills/skill-creator/preferences.md`. If the file does not exist, treat as "no preferences set".

## Context

Before starting, use the `Glob` tool to discover existing skills at `~/.claude/skills/*/SKILL.md` and check if `~/.claude/skills/SKILLS_GUIDE.md` exists (read it in Step 3).

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/skill-creator/preferences.md`, confirm, stop
- **`--from-description "..."`** → skip Q1, use the quoted text as the skill's purpose
- **anything else** (including empty) → run the skill

### Help

```
Skill Creator — Creates new Claude Code skills interactively

Usage:
  /skill-creator                             Interactive skill creation
  /skill-creator <name>                      Start with a name pre-filled
  /skill-creator --from-description "..."    Start from a plain-text description
  /skill-creator config                      Set preferences
  /skill-creator reset                       Clear preferences
  /skill-creator help                        This help

Examples:
  /skill-creator                             Full interactive walkthrough
  /skill-creator deploy-preview              Create a skill named "deploy-preview"
  /skill-creator --from-description "A skill that checks my PR for common issues before I submit it"

Current preferences:
  (shown above under Preferences)
```

### Config

Use `AskUserQuestion` to collect:

- **Q1: Default skill location** — `~/.claude/skills/` (standard) or custom path
- **Q2: Auto-update inventory** — Yes/No — whether to update SKILLS_GUIDE.md inventory after creation
- **Q3: Publish repo path** — path to the GitHub publish repo (e.g., `~/Dev/claude-skills`), or "none"

Save to `~/.claude/skills/skill-creator/preferences.md`.

### Reset

Delete `~/.claude/skills/skill-creator/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:

> First time using /skill-creator? Run `/skill-creator config` to set defaults, or just continue with sensible defaults.

Then proceed.

## Step 1: Understand the skill's purpose

If `$ARGUMENTS` contains `--from-description`, use that text. If `$ARGUMENTS` is a bare name, pre-fill the name and ask the rest. Otherwise, ask everything.

Use **AskUserQuestion** — single question:

> **What should this skill do?** Describe the workflow in a sentence or two. Example: "Fetch my open PRs, check which ones have failing CI, and offer to investigate."

After the user answers, extract:
- **Working name** — derive a kebab-case name (or use the one from `$ARGUMENTS`)
- **Core verb** — what it does (creates, analyzes, fetches, organizes, etc.)
- **Trigger** — when should a user reach for this skill

Confirm with the user:
> I'll call this **`/skill-name`** — a skill that _[one-liner]_. Sound right?

## Step 2: Determine side effects and context

Based on the description, infer whether the skill has side effects and whether it needs conversation context. Then confirm with the user using **AskUserQuestion** (2 questions):

**Q1: Side effects** — Does this skill create, modify, push, or post anything?
- "Yes — it writes/creates/modifies things" → `disable-model-invocation: true`
- "No — read-only, just analyzes and reports" → omit `disable-model-invocation`
- Pre-select based on the description (if it mentions "create", "post", "push", "update", "write", "deploy", default to Yes)

**Q2: Context needs** — Does this skill need the current conversation history?
- "Yes — it builds on what we've been discussing" → no `context` field
- "No — it's self-contained, works from its own inputs" → `context: fork`
- Pre-select: if the skill processes external input (pasted text, URLs, file paths), default to fork

## Step 3: Identify tools needed

Read `~/.claude/skills/SKILLS_GUIDE.md` to reference the conventions.

Based on the skill's purpose, determine the minimal set of tools. Walk through categories with **AskUserQuestion** (multiSelect, 1 question):

> **Which capabilities does this skill need?** (select all that apply)

Options:
- **Read files** — Read, Glob, Grep (for analyzing code, configs, logs)
- **Edit files** — Write, Edit (for modifying code, creating files)
- **Run commands** — Bash (for git, npm, CLI tools, API calls)
- **Ask questions** — AskUserQuestion (for interactive decisions during the skill)
- **Web access** — WebSearch, WebFetch (for looking up docs, APIs, external data)
- **Linear integration** — Linear MCP tools (for issues, projects, comments)
- **Vercel integration** — Vercel MCP tools (for deployments, logs, projects)

Map selections to specific `allowed-tools` entries:
- Read files → `Read`, `Glob`, `Grep`
- Edit files → `Write`, `Edit`
- Run commands → `Bash`
- Ask questions → `AskUserQuestion`
- Web access → `WebSearch`, `WebFetch`
- Linear → determine which Linear MCP tools based on the skill's actions:
  - Reading: `mcp__claude_ai_Linear__list_issues`, `mcp__claude_ai_Linear__get_issue`, `mcp__claude_ai_Linear__list_comments`, `mcp__claude_ai_Linear__list_projects`, `mcp__claude_ai_Linear__get_project`, `mcp__claude_ai_Linear__list_teams`
  - Writing: above + `mcp__claude_ai_Linear__create_issue`, `mcp__claude_ai_Linear__update_issue`, `mcp__claude_ai_Linear__create_comment`
- Vercel → determine which Vercel MCP tools based on the skill's actions

Always include `AskUserQuestion` — every skill needs it for help/config/reset at minimum.

## Step 4: Design the workflow

Think through the skill's steps. Consider:

1. **What context does it need upfront?** → dynamic context injection candidates
2. **What's the happy-path workflow?** → numbered steps
3. **What are the decision points?** → where to use AskUserQuestion
4. **What could go wrong?** → graceful degradation
5. **What's worth learning?** → preferences to save

Draft the workflow as numbered steps. Keep it to 4-8 steps. Present the outline to the user:

> Here's the workflow I'm planning:
>
> 1. Gather context (branch, status, etc.)
> 2. [Step specific to this skill]
> 3. ...
> N. Report results / offer next actions
>
> Want to adjust anything?

## Step 5: Determine arguments and flags

Based on the workflow, propose:
- **Positional argument** — the main input (if any)
- **Flags** — optional modifiers (e.g., `--dry-run`, `--verbose`, `--preview`)

Confirm with the user via **AskUserQuestion** or inline confirmation.

## Step 6: Generate the SKILL.md

Assemble the complete SKILL.md following all conventions:

### Structure checklist

- [ ] YAML frontmatter with all required fields
- [ ] `name` — kebab-case, matches directory name
- [ ] `description` — third-person, includes "Use when" trigger
- [ ] `argument-hint` — reflects arguments and flags
- [ ] `disable-model-invocation` — set if side effects confirmed
- [ ] `context: fork` — set if confirmed self-contained
- [ ] `allowed-tools` — minimal list from Step 3
- [ ] Preferences section with dynamic injection
- [ ] Context section with relevant `!`backtick`` commands
- [ ] Command routing (help, config, reset, default)
- [ ] Help block in CLI format
- [ ] Config block with AskUserQuestion
- [ ] Reset block
- [ ] First-time detection
- [ ] Numbered workflow steps from Step 4
- [ ] Principles section (3-5 rules specific to this skill)
- [ ] Under 500 lines total

### Dynamic context injection

Choose relevant pre-fetch commands based on the skill's needs:
- Git-aware skills: branch, status, recent commits, remotes
- Project-aware skills: package.json, Cargo.toml, etc.
- PR-aware skills: open PRs, current PR
- Linear-aware skills: skip (fetch at runtime via MCP)

### Config questions

Design 2-4 config questions specific to this skill's configurable aspects (default branch, output format, verbosity, etc.).

### Principles

Write 3-5 principles that capture the skill's core behavioral rules. Examples:
- "Non-destructive by default" for tools that could delete things
- "Always confirm before posting" for skills that publish externally
- "Fail fast on missing context" for skills that need specific inputs

## Step 7: Write the files

1. Create the directory: `~/.claude/skills/<skill-name>/`
2. Write `SKILL.md` with the generated content
3. If reference material exceeds 100 lines, split into `reference/` files
4. Show the user a summary of what was created

## Step 8: Post-creation actions

Present options via **AskUserQuestion**:

- **Test it** — "Run `/skill-name help` to verify the help output"
- **Configure it** — "Run `/skill-name config` to set initial preferences"
- **Update inventory** — if a publish repo is configured, offer to update SKILLS_GUIDE.md and README.md
- **Done** — "All set! Your new skill is ready at `~/.claude/skills/<skill-name>/`"

If the user chose "Update inventory" and a publish repo is configured:
1. Copy the new skill directory to the publish repo
2. Add an entry to SKILLS_GUIDE.md inventory table
3. Add a section to README.md
4. Report what was updated (don't commit — leave that to the user or `/publish-skills`)

## Step 9: Learn

If the user made any corrections during the process (renamed the skill, changed tools, adjusted workflow), silently save those patterns to preferences:

```markdown
# /skill-creator preferences
Updated: {date}

## Defaults
- skill-location: ~/.claude/skills/
- auto-update-inventory: yes/no
- publish-repo: path or none

## Learned
- User prefers [pattern observed]
```

Mention: "Noted: you prefer X. Saved for next time."

## Principles

- **Convention over configuration** — follow SKILLS_GUIDE.md strictly; don't let the user accidentally create a non-conforming skill.
- **Ask, don't assume** — when the skill's purpose is ambiguous (side effects unclear, tools uncertain), ask rather than guess.
- **Minimal viable skill** — start with the simplest version that works. The user can always add complexity later.
- **Show before write** — always present the planned workflow and key decisions before generating the file.
- **Learn and improve** — save patterns from user corrections to make future skill creation faster.
