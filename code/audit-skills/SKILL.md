---
name: audit-skills
description: >-
  Audits all personal Claude skills against the SKILLS_GUIDE.md manifest, latest
  official Claude skills documentation, and best practices. Reports issues, missing
  patterns, and improvement suggestions per skill. Use to keep skills healthy, consistent,
  and up-to-date with the latest standards.
argument-hint: [skill-name] [--fix] [--verbose]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
---

# Audit Skills

Audit personal Claude skills for consistency, best practices, and up-to-date standards.

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`--fix [skill-name]`** → auto-fix issues (see Fix mode)
- **`--verbose [skill-name]`** → show full details for every check (not just failures)
- **`<skill-name>`** → audit a single skill
- **empty** → audit all skills

### Help

```
Doctor — Audit personal Claude skills for health and consistency

Usage:
  /audit-skills                      Audit all personal skills
  /audit-skills <skill-name>         Audit a single skill
  /audit-skills --fix                Auto-fix all skills
  /audit-skills --fix <skill-name>   Auto-fix a specific skill
  /audit-skills --verbose            Full detail for every check
  /audit-skills help                 This help

Checks performed:
  Manifest    Does the skill follow SKILLS_GUIDE.md conventions?
  Frontmatter Are all required/recommended fields present and correct?
  Content     Is the skill under 500 lines? Are references bundled?
  Tools       Are allowed-tools minimal? Any duplicates? Any contradictions?
  UX          Does it have help/config/reset? First-time detection? Memory?
  Docs        Is the description third-person with trigger keywords?
  Security    Does disable-model-invocation match the side-effect profile?
  Upstream    Does it follow latest official Claude skills documentation?

Output:
  [PASS] Check passed
  [WARN] Non-critical suggestion
  [FAIL] Violates manifest or best practice
  [INFO] Informational note

Example output:
  /slack-to-ticket
    [PASS] Third-person description
    [PASS] disable-model-invocation: true (has side effects)
    [WARN] SKILL.md is 120 lines — fine, but has inline examples that could be bundled
    [FAIL] Missing help subcommand
    [PASS] Preferences memory pattern present
```

## Step 1: Load references

### Local manifest

Read `~/.claude/skills/SKILLS_GUIDE.md` — this is the source of truth for local conventions.

### Latest upstream docs

Search the web for the latest Claude Code skills documentation:

ultrathink

Search for:
- `site:code.claude.com skills` — official skill format docs
- `site:platform.claude.com agent-skills best-practices` — authoring best practices
- `claude code skills 2026` — any new features or changes

Fetch and read the top results. Extract:
- Any NEW frontmatter fields not in our manifest
- Any CHANGED best practices (naming, descriptions, tool restrictions)
- Any DEPRECATED patterns we're still using
- Any NEW features we should adopt

Compile a checklist of **upstream checks** in addition to the manifest checks.

If web search is unavailable, proceed with manifest-only checks and note: "Could not fetch upstream docs — manifest checks only."

## Step 2: Discover skills

```
~/.claude/skills/*/SKILL.md
```

List all found skills. If a specific skill-name was given in `$ARGUMENTS`, filter to just that one.

## Step 3: Audit each skill

For each skill, run every check below. Track results as PASS/WARN/FAIL/INFO.

### Frontmatter checks

| Check | PASS | FAIL |
|---|---|---|
| `name` present | Has name | Missing |
| `description` present | Has description | Missing |
| `description` is third-person | Starts with verb in third person ("Creates", "Analyzes") | Imperative/second person ("Create", "Analyze") |
| `description` has trigger keywords | Contains "Use when" or similar usage hint | No usage context |
| `description` length | ≤1024 chars | Over 1024 |
| `argument-hint` present | Has hint | WARN: missing (optional but recommended) |
| `disable-model-invocation` | `true` if skill has side effects (check allowed-tools for Write, Edit, Bash, MCP create/update tools) | Missing when side effects present |
| `allowed-tools` present | Listed | WARN: missing (broad permissions) |

### Tool checks

| Check | PASS | FAIL |
|---|---|---|
| No duplicate MCP tools | Single prefix per service | Both `mcp__linear-server__*` and `mcp__claude_ai_Linear__*` |
| MCP tools use canonical prefix | Uses `mcp__claude_ai_Linear__*` | Uses `mcp__linear-server__*` |
| No contradictory tools | Read-only skills don't have Write/Edit | Read-only principle violated |
| Minimal tools | Only tools actually referenced in body | Tools listed but never used |

### Content checks

| Check | PASS | FAIL |
|---|---|---|
| Under 500 lines | ≤500 | WARN: over 500 |
| No redundant instructions | Doesn't tell Claude how to use JSON, git basics, etc. | WARN: generic instructions |
| Uses numbered checklists for workflows | Steps are numbered | WARN: prose-only workflow |
| References bundled files if >100 lines of examples | Examples in separate files | WARN: large inline examples |

### UX checks (from manifest conventions)

| Check | PASS | FAIL |
|---|---|---|
| `help` subcommand | Body handles `$ARGUMENTS` = "help" | Missing |
| `config` subcommand | Body handles `$ARGUMENTS` = "config" | Missing |
| `reset` subcommand | Body handles `$ARGUMENTS` = "reset" | Missing |
| First-time detection | Checks for preferences file existence | Missing |
| Preferences memory | References `preferences.md` file | Missing |
| Dynamic context injection | Uses `!`backtick`` preprocessing | WARN: missing where applicable |

### Upstream checks (from fetched docs)

Apply any new checks discovered in Step 1. Common ones:

| Check | PASS | FAIL |
|---|---|---|
| `context: fork` for self-contained skills | Set when skill doesn't need conversation history | WARN: could benefit from fork |
| `model` field for reasoning-heavy skills | Set for complex analysis skills | INFO: could benefit from model override |
| Positional args `$0`, `$1` | Used for structured inputs | INFO: could use positional args |
| Skill directory structure | Has SKILL.md + optional reference/examples | Non-standard structure |

### Inventory check (only on full audit)

- Compare discovered skills against `SKILLS_GUIDE.md` inventory table
- Report any skills not in the inventory (WARN)
- Report any inventory entries with no matching skill (WARN)

## Step 4: Present results

### Per-skill report

```
/skill-name
  [PASS] 8 checks passed
  [WARN] 2 warnings
  [FAIL] 1 failure

  Failures:
    - disable-model-invocation missing (skill creates Linear issues)

  Warnings:
    - No dynamic context injection (could pre-fetch git branch)
    - SKILL.md is 180 lines with inline examples (consider bundling)
```

### Summary (full audit only)

```
Doctor Summary — {date}

Skills audited: {N}
  [PASS] {N} fully healthy
  [WARN] {N} with warnings
  [FAIL] {N} with failures

Top issues:
  1. {most common failure across skills}
  2. {second most common}

Upstream updates:
  {Any new features/changes from official docs worth adopting}
  (or "All skills are up-to-date with latest docs")

Inventory:
  {N} skills in SKILLS_GUIDE.md
  {N} skill directories found
  {discrepancies if any}
```

## Step 5: Offer fixes (if `--fix` flag)

If `--fix` was passed:

1. For each FAIL, propose a specific edit
2. For each WARN, propose a fix (optional)
3. Use **`AskUserQuestion`** (multiSelect: true):
   - One option per proposed fix
   - "Apply all fixes"
   - "Skip all"
4. Apply approved fixes using Edit tool
5. Update `SKILLS_GUIDE.md` inventory if new skills were found
6. Report what was changed

Without `--fix`: just report findings.

## Step 6: Save audit results

Write a timestamped audit log to:
```
~/.claude/skills/audit-skills/last-audit.md
```

Format:
```markdown
# Skill Audit — {date}

## Summary
- Skills: {N}
- Pass: {N}, Warn: {N}, Fail: {N}

## Per-skill results
{compact results}

## Upstream notes
{anything new from docs}
```

This allows comparing across audits to track improvement.

## Principles

- **Non-destructive by default**: Only report, never modify without `--fix` and user confirmation.
- **Manifest is local truth**: SKILLS_GUIDE.md defines what "good" means for this user.
- **Upstream is advisory**: New features from official docs are INFO/WARN, not FAIL (unless the user's manifest adopts them).
- **Be specific**: Every FAIL/WARN includes exactly what's wrong and how to fix it.
- **Fast**: Don't re-read files unnecessarily. Parse frontmatter first, skip deep content checks if frontmatter fails.
