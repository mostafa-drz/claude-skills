---
name: organize-screenshots
description: >-
  Scans a folder for recent screenshots, visually classifies which ones are relevant
  to current work, and organizes them into a target directory with descriptive filenames.
  Use when collecting screenshots for PRs, bug reports, docs, or Linear issues.
argument-hint: <target-dir> [--source dir] [--days N]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
---

# Organize Screenshots

Scan for recent screenshots, visually classify them, and organize with descriptive names.

## Preferences

!`cat ~/.claude/skills/organize-screenshots/preferences.md 2>/dev/null || echo "_no preferences set_"`

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Recent screenshots: !`find ~/Desktop -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) -mtime -3 2>/dev/null | wc -l | tr -d ' '`

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/organize-screenshots/preferences.md`, confirm, stop
- **anything else** → process screenshots

### Flags

Parse from `$ARGUMENTS`:
- **`--source <dir>`** — override source folder (default: ~/Desktop or preference)
- **`--days <N>`** — look back N days (default: 3 or preference)
- **`--move`** — move instead of copy
- **`--all`** — skip classification, take everything
- **Remaining text** — target directory

### Help

```
Screenshots — Scan, classify, and organize screenshots

Usage:
  /organize-screenshots <target-dir>                     Scan Desktop, organize into target
  /organize-screenshots <target-dir> --source ~/Downloads Scan specific folder
  /organize-screenshots <target-dir> --days 1             Only last 24 hours
  /organize-screenshots <target-dir> --move               Move instead of copy
  /organize-screenshots <target-dir> --all                Skip classification, take all
  /organize-screenshots config                            Set defaults
  /organize-screenshots reset                             Clear preferences
  /organize-screenshots help                              This help

Examples:
  /organize-screenshots ./docs/images
  /organize-screenshots ./pr-assets --days 1
  /organize-screenshots ~/bug-report --source ~/Downloads --move

What it does:
  1. Finds recent screenshots in source folder
  2. Visually reviews each one (reads the image)
  3. Classifies: relevant to current work or not
  4. Suggests descriptive filenames
  5. Copies (or moves) to target with new names

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Default source folder?" (~/Desktop (default), ~/Downloads, custom path)
**Q2** — "Lookback days?" (1 day, 3 days (default), 7 days)
**Q3** — "Default action?" (Copy (default), Move)
**Q4** — "Naming style?" (descriptive — feature-what-it-shows (default), timestamp — YYYY-MM-DD-description, sequential — 01-description)

Save to `~/.claude/skills/organize-screenshots/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /organize-screenshots? Run `/organize-screenshots config` to set source folder and defaults, or continue — scanning ~/Desktop for the last 3 days."

Then proceed.

## Steps

### 1. Identify work context

Read context to understand what's relevant:
- Current branch name and recent commits (from pre-injected context)
- CLAUDE.md if present (for project/feature names)
- Any files discussed in current conversation

Build a mental model of what screenshots to look for.

### 2. Find screenshots

Scan source folder for images modified within lookback period:
```
find {source} -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) -mtime -{days}
```

If none found → inform user, stop.
If >20 found → ask if user wants to narrow time range or proceed.

### 3. Visual review

For each image:
1. **Read the image** using Read tool (multimodal)
2. **Classify**: Is it related to current work context?
   - Related: shows project UI, relevant code, error messages, terminal output matching current work
   - Unrelated: random browser tabs, personal content, unrelated apps
3. **Describe** if relevant: generate a short descriptive filename

If `--all` flag, skip classification — include everything.

### 4. Present findings

```
Found {N} screenshots in {source} from the last {days} days.
{M} appear related to current work:

  1. Screenshot 2026-02-17 at 11.19.00 AM.png
     → {descriptive-name}.png
     Shows: {brief description}

  2. Screenshot 2026-02-17 at 11.24.00 AM.png
     → {descriptive-name}.png
     Shows: {brief description}

  Skipped {K} unrelated screenshots.
```

Use **`AskUserQuestion`** to confirm:
- "Organize these screenshots?" (Approve all, Exclude specific ones, Include skipped ones, Cancel)

### 5. Organize

Create target directory:
```
mkdir -p {target}
```

Copy (or move) each approved screenshot. **Important:** macOS screenshot filenames contain a Unicode narrow no-break space (U+202F) before AM/PM. Always use `find` with timestamp wildcards:

```
# CORRECT — use find with wildcards:
find {source} -maxdepth 1 -name "*2026-02-17*11.19*" -exec cp {} "{target}/{descriptive-name}.png" \;

# WRONG — will fail due to Unicode:
cp "Screenshot 2026-02-17 at 11.19.00 AM.png" dest/name.png
```

### 6. Naming convention

```
{context}-{what-it-shows}.{ext}
```

- All lowercase, hyphens as separators
- Context first (feature, page, component), then what's shown
- No dates or timestamps in filename (unless timestamp naming style preference)
- Under 60 characters
- Preserve original extension

Examples:
- `settings-page-form-validation.png`
- `api-error-500-response.png`
- `dashboard-metrics-overview.png`
- `terminal-test-failures.png`

### 7. Report

```
Organized {M} screenshots:

  {target}/
  ├── {name-1}.png
  ├── {name-2}.png
  └── {name-3}.png

  Originals: {preserved in source / moved}

Next steps:
  1. Review in {target}/
  2. Upload to PR, Linear, or docs as needed
```

### 8. Learn

If user renames files after organizing, note the naming pattern.
If user changes source folder, save preference.

## Principles

- **Always copy by default** — originals stay. User decides when to delete.
- **Ask before acting** — present classification, get confirmation before copying.
- **Be conservative** — when in doubt, include and let user exclude.
- **Respect privacy** — skip screenshots with personal info, don't describe their contents.
