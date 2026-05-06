---
name: extract-skill
description: >-
  Scans the current conversation for patterns worth turning into a reusable skill or memory rule —
  feedback you've given Claude, workflows you've walked through, corrections, best practices, recurring
  setups. Proposes candidates, classifies each as skill (multi-step workflow) or memory (single rule),
  cross-checks against existing skills + MEMORY.md to avoid duplicates, then hands off to
  /skill-creator (for skills) or writes the memory entry directly. Use when the conversation contains
  reusable knowledge you don't want to teach Claude again — "we just figured this out, capture it",
  "turn this into a skill", "save this workflow", "from experience to skill".
argument-hint: "[--memory-only] [--skill-only] [--dry-run]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(ls *)
  - Bash(mkdir *)
  - Bash(cat *)
  - Bash(git *)
  - Bash(wc *)
---

# extract-skill

Turn the **current conversation** into a reusable skill or memory rule. From experience → reusable artifact.

## Preferences

_On startup, use Read to load `~/.claude/skills/extract-skill/preferences.md`. If it does not exist, treat as "no preferences set" — proceed with sensible defaults._

## Context

_On startup, use Bash to:_
1. _List existing skills: `ls ~/.claude/skills/`_
2. _Read `~/.claude/skills/SKILLS_GUIDE.md` (inventory + conventions)_
3. _Read `~/.claude/projects/<project-slug>/memory/MEMORY.md` if accessible (the user's auto-memory index)_

_Skip any that fail. The point is to know what already exists so we don't propose duplicates._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup, then stop
- **`reset`** → delete `~/.claude/skills/extract-skill/preferences.md`, confirm, stop
- **`--memory-only`** → only propose memory entries, never skills
- **`--skill-only`** → only propose skills, never memory entries
- **`--dry-run`** → print candidates + classification, do not create anything
- **anything else (including empty)** → run the skill

### Help

```
extract-skill — Capture conversation learnings as a skill or memory rule

Usage:
  /extract-skill                Scan this conversation, propose skill/memory candidates
  /extract-skill --memory-only  Only propose memory entries (single-rule preferences)
  /extract-skill --skill-only   Only propose skills (multi-step workflows)
  /extract-skill --dry-run      Print candidates + classification, do not create anything
  /extract-skill config         Set preferences
  /extract-skill reset          Clear preferences
  /extract-skill help           This help

Examples:
  /extract-skill                After a chat where you taught Claude how to do X
  /extract-skill --dry-run      Preview what would be captured before committing

Current preferences:
  (loaded from preferences.md, shown above)
```

### Config

Use `AskUserQuestion` to collect:

- **Q1: Default routing** — When a candidate is ambiguous (could be skill or memory), default to: ask each time / route to skill / route to memory
- **Q2: Skill creation handoff** — Always hand off to `/skill-creator` / let me choose per skill
- **Q3: Memory project path** — Auto-detect from current project / always use a fixed path
- **Q4: Minimum signal threshold** — How strong must a pattern be to surface it? (any mention / repeated 2+ times / explicit "save this" only)

Save to `~/.claude/skills/extract-skill/preferences.md`.

### Reset

Delete `~/.claude/skills/extract-skill/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:

> First time using /extract-skill? Run `/extract-skill config` to set defaults, or just continue with sensible defaults.

Then proceed.

---

## Step 1: Scan the conversation for signal

Look back over the conversation we're in **right now**. You don't need to read transcripts — you have the messages in context. Categorize what you see into these signal types:

### Signal types

| Type | Example phrasing in chat | Likely artifact |
|---|---|---|
| **Feedback / correction** | "don't do X", "stop doing Y", "always use Z" | Memory (single rule) |
| **Preference / convention** | "we use pnpm not npm", "kebab-case for components" | Memory (single rule) |
| **Workflow walkthrough** | User taught Claude a multi-step procedure ("first do X, then Y, then Z, then…") | **Skill** |
| **Repeated request** | User asked for the same kind of output 2+ times in similar way | **Skill** |
| **Setup / configuration ritual** | "every time I start, I do X, Y, Z" | **Skill** (or memory if 1 step) |
| **Best practice shared** | User explained why an approach is correct | Memory (with **Why:**) |
| **Tooling / integration** | User showed how to use a specific MCP or external tool | **Skill** |
| **Explicit "save this"** | "remember this", "turn this into a skill", "capture this" | Whatever the user named |

### What counts as signal vs noise

**Signal** (capture):
- Rules the user articulated explicitly ("always", "never", "we do it this way")
- Multi-step procedures the user walked through and validated
- Corrections to Claude's default behavior
- Preferences the user expressed with reasoning (the **Why:**)

**Noise** (skip):
- Casual chatter
- One-off task details ("fix this typo on line 42")
- Stuff already in MEMORY.md (cross-check before surfacing)
- Stuff already covered by an existing skill (cross-check inventory)

## Step 2: Classify — skill vs memory

For each candidate, decide:

- **Memory** — single rule, declarative, no procedure. "Always X." "Never Y." "We use Z." → goes into a memory file with frontmatter (type: feedback / user / project / reference) per the user's auto-memory format.
- **Skill** — multi-step workflow, has inputs/outputs/decision points, worth invoking explicitly with `/<name>`. → handed off to `/skill-creator`.
- **Both** — rare but real. A skill `/post-pr` might pair with a memory rule "PRs always use HEREDOC syntax".
- **Already exists** — flag it. Show the existing skill or memory entry instead of duplicating.
- **Skip** — not enough signal yet, or too task-specific.

If the user passed `--memory-only` or `--skill-only`, filter the output accordingly.

## Step 3: Cross-reference existing artifacts

Before surfacing any candidate:

1. **Check existing skills inventory** — search `~/.claude/skills/SKILLS_GUIDE.md` and the directory listing. If a skill already covers this workflow, mention it instead of proposing a duplicate.
2. **Check MEMORY.md** — search the user's auto-memory index for matching rules. If the rule already exists, propose an **update** (e.g., add a **Why:** line, sharpen wording) rather than a new entry.
3. **Check Claude Code built-ins** — don't propose a skill for things like `/init`, `/review`, `/loop` that already ship with Claude Code.

## Step 4: Present candidates to the user

Use `AskUserQuestion` to show 1–4 candidates at once. Each option should include:

- **Type** — Skill / Memory / Update existing / Skip
- **Name** (kebab-case for skills, descriptive title for memory)
- **One-liner** — what it does or what the rule says
- **Trigger** — when this applies / when to invoke
- **Source** — 1–2 quotes from the conversation showing the signal

Example layout:

```
Candidate 1: SKILL — extract-skill
  One-liner: Scans current conversation, proposes skill/memory candidates, routes to /skill-creator or writes memory.
  Trigger:   After a chat where the user taught Claude something reusable.
  Source:    "from experience to skills, best practices my latest, learning, feedback…"
            "I want to create a skill which basically when I call it looks at context available in a chat…"

Candidate 2: MEMORY — Always confirm name + scope before generating SKILL.md
  Rule:      Skill creation must confirm name and side-effect scope before writing files.
  Why:       Past skills were generated with wrong defaults that the user had to revise.
  How to apply: When invoked, ask name + side-effects Q before any Write tool call.
```

Let the user pick which to proceed with (multi-select). Default-select all that look high-confidence.

## Step 5a: Skill candidates → hand off to /skill-creator

For each candidate the user accepted as a **skill**:

1. Build a single, self-contained `--from-description` brief: `"<one-liner>. Trigger: <when>. Key behaviors: <bullets>. Inputs: <args/flags>. Side effects: <yes/no + what>."`
2. Tell the user: _"Handing off to `/skill-creator --from-description \"…\"` — it will walk you through name, tools, and workflow with its own conventions."_
3. **Do not invoke `/skill-creator` yourself via tool** — slash commands aren't tool-callable from another skill. Print the exact command for the user to run, or to copy/paste.
4. If the user prefers direct creation (set in config), generate `SKILL.md` inline using SKILLS_GUIDE.md conventions — but flag this as the non-DRY path.

### The brief format (paste into /skill-creator)

```
/skill-creator --from-description "<purpose in 1–2 sentences>. Trigger: <when user reaches for it>. Key behaviors: <3–5 bullets>. Side effects: <yes/no — what does it create or modify?>. Tools: <best-guess list>."
```

## Step 5b: Memory candidates → write directly

For each candidate the user accepted as a **memory** entry:

1. Determine memory type from content:
   - `feedback` — user corrections, preferences, do/don't rules
   - `user` — facts about the user's role / context
   - `project` — facts about ongoing work
   - `reference` — pointers to external systems
2. Pick a filename (kebab-case): `feedback_<topic>.md`, `project_<topic>.md`, etc.
3. Write the file with frontmatter:

   ```markdown
   ---
   name: <Title>
   description: <one-line, specific>
   type: feedback | user | project | reference
   ---

   <Lead with the rule/fact.>

   **Why:** <reason — often an incident or strong preference>

   **How to apply:** <when/where this kicks in>
   ```

4. Add a one-line index entry to `MEMORY.md` under an appropriate heading:

   ```markdown
   ## <Short title> (MANDATORY / PREFERENCE / ACTIVE)
   - See `memory/<filename>.md`
   - <one-line hook capturing the essence>
   ```

5. Use `Edit` (not `Write`) on `MEMORY.md` so existing entries aren't clobbered.

### Where to write memory files

The auto-memory directory is per-project. Detect via:

```bash
git rev-parse --show-toplevel
```

Then map to: `~/.claude/projects/<encoded-path>/memory/`. If the directory doesn't exist or isn't accessible, fall back to asking the user for the path.

## Step 6: Update existing entries

If a candidate matches something already in MEMORY.md or an existing skill:

- **Memory match** — show the existing entry alongside the new signal. Ask: keep existing / sharpen wording / add **Why:** line / add **How to apply:** line.
- **Skill match** — show the existing skill name + description. Ask: extend it (rare — usually means editing its SKILL.md) / leave alone / propose a sibling skill.

## Step 7: Confirm and report

After all writes:

1. List what was created/updated:
   - Skills proposed (with the exact `/skill-creator …` command to run)
   - Memory files written (with paths)
   - MEMORY.md entries added
2. Show 1–3 lines per artifact — no walls of text.
3. End with a single suggestion: "Run `<command>` to finalize the skill" or "Memory takes effect next conversation — nothing else to do".

## Step 8: Learn

If the user corrected your classification (e.g., "no, that's a memory not a skill", "use this name instead"), silently save to `preferences.md` under `## Learned`. Surface once: _"Noted: <pattern>. Saved for next time."_

---

## Principles

- **DRY across the meta-system** — defer to `/skill-creator` for skill generation; defer to MEMORY.md for memory routing. This skill is a router + classifier, not a re-implementation.
- **Cross-reference before proposing** — duplicate skills and duplicate memory entries are worse than missed captures. Always check inventory + MEMORY.md first.
- **Prefer memory for single rules, skills for workflows** — a one-liner like "always use pnpm" is memory. A 5-step "release a new note" procedure is a skill.
- **Quote the source** — every candidate must show 1–2 lines from the conversation that justify it. No hallucinated patterns.
- **Don't auto-invoke other skills** — print the exact `/skill-creator` command for the user. Side-effect chains shouldn't fire silently.
- **Confirm before writing** — every Write/Edit happens after explicit user accept. `--dry-run` prints without writing.
- **Keep the bar high** — if a pattern was mentioned once in passing, skip it. Strong signal = explicit rule, repeated request, or "save this" instruction.
