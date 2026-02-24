---
name: publish-skills
description: >-
  Publishes personal Claude skills to a GitHub repository for sharing. Copies skill files,
  generates a README catalog, commits, and pushes. Use when ready to share skill updates
  or after creating/updating skills.
argument-hint: [--preview] [--diff]
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

# Publish Skills

Publish personal Claude skills to a GitHub repository for sharing and versioning.

## Preferences

_Read `~/.claude/skills/publish-skills/preferences.md` using the Read tool. If not found, no preferences are set._

## Context

_On startup, use the Glob tool to find `~/.claude/skills/*/SKILL.md` to count skills, and read preferences (above) to extract repo-path and last-published._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/publish-skills/preferences.md`, confirm, stop
- **`--preview`** → show what would be published, don't commit/push
- **`--diff`** → show diff between local skills and published repo
- **anything else** (including empty) → publish

### Help

```
Publish Skills — Share Claude skills via GitHub

Usage:
  /publish-skills                    Publish all skills to GitHub repo
  /publish-skills --preview          Show what would change without publishing
  /publish-skills --diff             Show diff between local and published
  /publish-skills config             Set repo path and GitHub remote
  /publish-skills reset              Clear preferences
  /publish-skills help               This help

What it does:
  1. Copies skill files to the publish repo (excludes preferences, audit logs)
  2. Generates a README.md catalog from skill descriptions
  3. Commits changes with a summary message
  4. Pushes to GitHub

What gets published:
  - SKILLS_GUIDE.md (design guide)
  - Each skill's SKILL.md
  - Each skill's reference/ and examples/ directories
  - Auto-generated README.md catalog

What stays private:
  - preferences.md files (user-specific config)
  - last-audit.md (audit logs)
  - Any file matching .gitignore patterns

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "GitHub repo path?" (text input)
- Where the publish repo is cloned locally
- Example: `~/Dev/claude-skills`

**Q2** — "GitHub remote URL?" (text input)
- The remote URL for the repo
- Example: `git@github.com:username/claude-skills.git`

**Q3** — "Commit style?" (Auto-summary (default) — list changed skills, Custom — ask each time)

Save to `~/.claude/skills/publish-skills/preferences.md`.

## First-time detection

If no preferences file exists:

1. Show: "First time using /publish-skills? Let me set up the publish repo."
2. Use **`AskUserQuestion`**:
   - Q1: "Where should the publish repo live?" — `~/Dev/claude-skills` (Recommended), custom path
   - Q2: "GitHub repo URL?" — text input (e.g., `git@github.com:username/claude-skills.git`)
3. Initialize the repo if it doesn't exist (see Setup below)
4. Save preferences
5. Continue with publish

### Setup (one-time)

If the repo path doesn't exist or isn't a git repo:

1. Create directory: `mkdir -p {repo-path}`
2. Initialize: `cd {repo-path} && git init`
3. Create `.gitignore`:
   ```
   preferences.md
   last-audit.md
   .DS_Store
   ```
4. Add remote: `git remote add origin {remote-url}`
5. Create initial commit with .gitignore
6. **Do NOT push yet** — the user needs to create the repo on GitHub first

If remote repo doesn't exist, inform:
"Repo initialized locally. Create the repo on GitHub first, then run /publish-skills again to push."

## Steps

### 1. Load config

Read preferences for repo-path and remote-url.

### 2. Discover and compare skills

Find all local skills:
```
~/.claude/skills/*/SKILL.md
```

For each skill, extract from frontmatter:
- `name`
- `description`
- `argument-hint`
- `disable-model-invocation`

Also note if the skill has `reference/` or `examples/` directories.

**Compare with published repo** to detect changes:
```bash
# For each local skill, diff against published version
diff ~/.claude/skills/{skill-name}/SKILL.md {repo-path}/skills/{skill-name}/SKILL.md
```

Categorize each skill:
- **New** — exists locally but not in the publish repo
- **Changed** — exists in both but files differ
- **Unchanged** — identical in both
- **Removed** — exists in repo but not locally

Also check if `SKILLS_GUIDE.md` changed.

### 3. Present changes and confirm

Show a summary of what would be published:

```
Skills to publish:

  New:
    + /skill-name — short description
    + /skill-name — short description

  Changed:
    ~ /skill-name — short description
    ~ /skill-name — short description

  Unchanged:
    = /skill-name (skipped)
    = /skill-name (skipped)

  Removed from repo:
    - /skill-name (no longer exists locally)

  Also: SKILLS_GUIDE.md (changed/unchanged)
```

Use **`AskUserQuestion`** (multiSelect: true):
- One option per new/changed/removed skill (pre-selected label shows the action: add/update/remove)
- "Publish all changes" — select all new + changed + removed
- "Cancel" — stop without publishing

**Only proceed with the skills the user explicitly selects.** Never auto-publish.

### 4. Sync selected files

Only copy the skills the user approved:

**For each approved skill:**
```bash
# Create skill dir in repo
mkdir -p {repo-path}/skills/{skill-name}

# Copy SKILL.md
cp ~/.claude/skills/{skill-name}/SKILL.md {repo-path}/skills/{skill-name}/

# Copy reference/ if exists
if [ -d ~/.claude/skills/{skill-name}/reference ]; then
  cp -r ~/.claude/skills/{skill-name}/reference {repo-path}/skills/{skill-name}/
fi

# Copy examples/ if exists
if [ -d ~/.claude/skills/{skill-name}/examples ]; then
  cp -r ~/.claude/skills/{skill-name}/examples {repo-path}/skills/{skill-name}/
fi
```

**For each approved removal:**
```bash
rm -rf {repo-path}/skills/{skill-name}
```

**Copy SKILLS_GUIDE.md** (if changed and user approved):
```bash
cp ~/.claude/skills/SKILLS_GUIDE.md {repo-path}/
```

### 5. Generate README.md

Build the catalog:

```markdown
# Claude Skills

Personal collection of Claude Code skills for developer workflows.

## Quick Start

To use these skills, copy them to your `~/.claude/skills/` directory:

```bash
# Clone and copy all skills
git clone {remote-url}
cp -r claude-skills/skills/* ~/.claude/skills/

# Or copy a single skill
cp -r claude-skills/skills/whats-next ~/.claude/skills/
```

## Skills Catalog

| Skill | Description | Side Effects |
|-------|-------------|:------------:|
| [`/address-pr-comments`](skills/address-pr-comments/SKILL.md) | {short description} | Yes |
| [`/audit-skills`](skills/audit-skills/SKILL.md) | {short description} | No |
| ... | ... | ... |

## Skill Details

### `/skill-name`

{full description from frontmatter}

**Usage:** `/skill-name {argument-hint}`

{link to SKILL.md}

---

## Design Guide

These skills follow a consistent [design guide](SKILLS_GUIDE.md) with:
- CLI-style help, config, and reset subcommands
- Persistent preferences per skill
- First-time setup guidance
- Learning from user corrections

## License

MIT
```

For the catalog table:
- Short description: first sentence of the frontmatter description (up to the first period)
- Side effects: "Yes" if `disable-model-invocation: true`, "No" otherwise

### 6. Commit and push

**If `--preview`:**
Steps 2-3 already showed the changes — stop here without modifying the repo.

**If `--diff`:**
Run `git -C {repo-path} diff` and show, then stop.

**Otherwise (after user confirmed in step 3):**

Stage only the approved files:
```bash
cd {repo-path}
git add skills/{approved-skill-1}/ skills/{approved-skill-2}/ README.md SKILLS_GUIDE.md
git status --short
```

Build commit message from what was approved:
```
Update skills: {list of approved skill names}

Added: {comma-separated list of new skills}
Updated: {comma-separated list of changed skills}
Removed: {comma-separated list of removed skills}
```

Show the staged diff summary and ask for final confirmation:

Use **`AskUserQuestion`**:
- "Commit and push?" (Yes — commit and push, Commit only — don't push, Cancel — discard staged changes)

Then execute based on choice:
```bash
git -C {repo-path} commit -m "{message}"
git -C {repo-path} push origin main   # only if user chose push
```

If push fails (no remote repo):
"Committed locally but push failed. Make sure the GitHub repo exists and you have push access."

### 7. Update preferences timestamp

Update `last-published` in preferences file.

### 8. Report

```
Published {N} skills to {remote-url}

  Added:   {list}
  Updated: {list}
  Removed: {list}
  Skipped: {list of unchanged or user-excluded skills}

  Commit: {hash} "{message}"
  Repo:   {remote-url}

  README catalog updated with {N} skills.
```

### 9. Learn

If user changes repo path, update preference.
If user consistently excludes certain skills, note that pattern.
If user consistently uses --preview first, note that pattern.

## Principles

- **Always confirm before publishing** — show what changed, let the user pick which skills to include, confirm before commit/push. Never auto-publish.
- **Never publish preferences** — preferences.md is user-specific and stays local.
- **Always generate README** — the catalog is the main value of the GitHub repo.
- **Non-destructive** — copies files, never modifies the source ~/.claude/skills/ directory.
- **Atomic publish** — one commit per publish with a clear summary.
- **Idempotent** — running twice without changes produces no new commits.
