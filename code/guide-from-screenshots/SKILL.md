---
name: guide-from-screenshots
description: >-
  Generates polished markdown guides from a directory of screenshots and a narrative.
  Visually reads each image, filters out redundant or irrelevant captures, organizes
  them contextually, and produces a Notion-compatible markdown file with image
  placeholders and structured sections. Use when you have screenshots and want to
  create a product guide, demo walkthrough, or tool guide.
argument-hint: <screenshot-dir> [--name GUIDE.md] [--type product|demo|tool]
disable-model-invocation: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# Guide from Screenshots

Turns a directory of screenshots + a narrative into a structured markdown guide.

## Preferences

_On startup, use Read to load `~/.claude/skills/guide-from-screenshots/preferences.md`. If it doesn't exist, use defaults._

## Command routing

Check `$ARGUMENTS`:

- **`help`** — display help then stop
- **`config`** — interactive setup then stop
- **`reset`** — delete preferences file, confirm, stop
- **anything else** — run the skill

### Help

```
Guide from Screenshots — Generate markdown guides from screenshots + narrative

Usage:
  /guide-from-screenshots <dir>                     Generate guide from screenshots in <dir>
  /guide-from-screenshots <dir> --name OUTPUT.md    Custom output filename
  /guide-from-screenshots <dir> --type demo         Preset guide type (product|demo|tool)
  /guide-from-screenshots config                    Set preferences
  /guide-from-screenshots reset                     Clear preferences
  /guide-from-screenshots help                      This help

The narrative/context comes from your conversation — describe what the screenshots
show before running the skill, or provide it when prompted.

Examples:
  /guide-from-screenshots ~/Desktop/onboarding-screenshots
  /guide-from-screenshots ./data/demo-screenshots --type demo --name DEMO_GUIDE.md

Current preferences:
  (read from preferences.md or defaults)
```

### Config

Use AskUserQuestion to collect:

- **Q1: Default guide type** — product / demo / tool / ask each time
- **Q2: Default tone** — formal / conversational / technical
- **Q3: Image reference format** — relative path (`./image.png`) or just filename (`image.png`)
- **Q4: Include table of contents** — yes / no

Save to `~/.claude/skills/guide-from-screenshots/preferences.md`.

### Reset

Delete `~/.claude/skills/guide-from-screenshots/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:

> First time using /guide-from-screenshots? Run `/guide-from-screenshots config` to set defaults, or just continue with sensible defaults.

Then proceed normally.

## Workflow

### Step 1: Parse inputs

Extract from `$ARGUMENTS`:
- **Directory path** (required) — the screenshot folder
- **--name** (optional) — output filename, default `GUIDE.md`
- **--type** (optional) — `product`, `demo`, or `tool` (overrides preference)

If no directory is provided, ask with AskUserQuestion.

### Step 2: Scan the directory

Use Glob to find all image files in the directory:
- Patterns: `*.png`, `*.jpg`, `*.jpeg`, `*.gif`, `*.webp`, `*.PNG`, `*.JPG`
- Sort by filename (which typically reflects chronological order)
- Count the total images found

If zero images found, report and stop.

### Step 3: Gather narrative context

Check the conversation history for narrative context the user has provided. If no narrative is apparent, ask:

> I found **N screenshots** in `<dir>`. What's the story? Describe what these screenshots show — the product, the flow, the audience. I'll use this to write the guide.

### Step 4: Visually read each screenshot

Use the Read tool to view each image file. For each screenshot, note:
- What UI/screen/page is shown
- Key elements visible (buttons, data, navigation, forms)
- Where it fits in the flow (setup, action, result, etc.)
- Any text or labels visible in the image

### Step 5: Filter and deduplicate

After reading all screenshots, identify candidates for exclusion:
- **Duplicates** — screenshots showing the same screen/state with negligible differences
- **Irrelevant captures** — screenshots that don't relate to the narrative (desktop clutter, unrelated apps, notification popups)
- **Partial/broken** — screenshots that are cut off or too blurry to be useful
- **Redundant transitions** — if 3 screenshots show nearly the same state, suggest keeping only the clearest one

**Always confirm before filtering.** Present the full list to the user:

> Here's what I found in **Y screenshots**:
>
> 1. `screenshot-01.png` — Login page → **Keep**
> 2. `screenshot-02.png` — Login page (same as #1) → **Drop** (duplicate)
> 3. `screenshot-03.png` — Dashboard overview → **Keep**
> ...
>
> I'd suggest dropping **X** screenshots. Want to adjust?

Use AskUserQuestion to let the user confirm or override. Never silently drop screenshots.

### Step 6: Determine guide structure

Based on the guide type (from args, preferences, or inference):

**Product Guide:**
- Overview / Introduction
- Key Features (one section per logical group of screenshots)
- How It Works (step-by-step with screenshots)
- Summary / Next Steps

**Demo Walkthrough:**
- Context / Setup
- Numbered walkthrough steps (1 screenshot = 1 step typically)
- Key Highlights
- Wrap-up

**Tool Guide:**
- What This Tool Does
- Getting Started
- Step-by-step Usage
- Tips & Tricks
- Reference

If no type was specified and it can't be inferred, ask with AskUserQuestion.

### Step 7: Generate the markdown guide

Write the guide following these rules:

**Markdown format (Notion-compatible):**
- Use `#`, `##`, `###` headers (Notion converts these cleanly)
- Use `>` blockquotes for callouts and highlights
- Use `-` for bullet lists, `1.` for numbered steps
- Use `---` for section dividers
- Use `**bold**` for emphasis on key terms
- Use checkbox `- [ ]` only when listing actionable items

**Screenshot references:**
```markdown
![Step 1: Brief description of what this shows](./screenshot-filename.png)
```
- Use descriptive alt text that explains what the screenshot shows
- Reference images with relative paths from the guide's location
- Place each screenshot immediately after the paragraph that describes it

**Section structure:**
- Each section starts with a brief paragraph explaining what happens
- Then the screenshot
- Then any additional detail or notes
- Smooth transitions between sections

**Writing style:**
- Match the tone from preferences (default: conversational but professional)
- Use the narrative as the backbone — weave screenshots into the story
- Be concise — the screenshots do most of the talking
- Address the reader directly ("you'll see...", "click on...", "notice how...")

### Step 8: Write the output

Write the generated markdown to `<dir>/<output-name>` (default: `<dir>/GUIDE.md`).

### Step 9: Summary

After writing, show:

```
Guide created: <path>

Structure:
  1. Section Name (2 screenshots)
  2. Section Name (3 screenshots)
  ...

Screenshots used: X of Y (Z filtered out)
Total sections: N
Word count: ~NNNN
```

Offer next actions:
- "Review and edit the guide"
- "Regenerate with different structure"
- "Done"

## Principles

1. **When in doubt, ask** — if unsure about anything (whether to include a screenshot, how to interpret it, what section it belongs to, the right tone, the guide structure), always ask the user. Never guess or assume. This applies to filtering, ordering, grouping, and every other decision.
2. **Screenshots tell the story** — the guide should flow naturally from one screenshot to the next. Don't over-explain what's visible; describe what matters.
3. **Filter with confirmation** — propose which screenshots to exclude and why, but always confirm with the user before dropping anything. Present a numbered list of screenshots with your recommendation (keep/drop + reason) and let the user decide.
4. **Notion-first markdown** — every formatting choice should render cleanly in Notion. Avoid HTML, complex tables, or non-standard markdown extensions.
5. **Narrative drives structure** — the user's narrative determines the order and grouping, not just the filename sort order. Reorder screenshots if the narrative flow demands it.
6. **Non-destructive** — never modify or delete the original screenshots. Only create the guide file.
