# Claude Skills

Personal collection of Claude Code skills for developer workflows.

## Quick Start

To use these skills, copy them to your `~/.claude/skills/` directory:

```bash
# Clone and copy all skills
git clone git@github.com:mosiesta/claude-skills.git
cp -r claude-skills/skills/* ~/.claude/skills/

# Or copy a single skill
cp -r claude-skills/skills/whats-next ~/.claude/skills/
```

Each skill supports `/skill-name help` for usage details, `/skill-name config` for preferences, and learns from your corrections over time.

## Skills Catalog

| Skill | Description | Side Effects |
|-------|-------------|:------------:|
| [`/address-pr-comments`](skills/address-pr-comments/SKILL.md) | Fetches unresolved PR comments, categorizes and addresses them | Yes |
| [`/audit-skills`](skills/audit-skills/SKILL.md) | Audits skills against manifest and upstream docs | Yes |
| [`/build-incremental`](skills/build-incremental/SKILL.md) | Implements code in progressive, verified increments | Yes |
| [`/create-pr`](skills/create-pr/SKILL.md) | Creates well-structured pull requests with Linear linking | Yes |
| [`/investigate-ci`](skills/investigate-ci/SKILL.md) | Investigates GitHub Actions workflow failures | No |
| [`/organize-screenshots`](skills/organize-screenshots/SKILL.md) | Scans and organizes screenshots with descriptive names | Yes |
| [`/post-ticket-summary`](skills/post-ticket-summary/SKILL.md) | Posts implementation summary to Linear issues | Yes |
| [`/publish-skills`](skills/publish-skills/SKILL.md) | Publishes skills to a GitHub repo for sharing | Yes |
| [`/slack-to-ticket`](skills/slack-to-ticket/SKILL.md) | Creates Linear issues from Slack threads | Yes |
| [`/smoke-test`](skills/smoke-test/SKILL.md) | Traces and verifies E2E in any environment | Yes |
| [`/sync-branch`](skills/sync-branch/SKILL.md) | Merges branches with conflict handling | Yes |
| [`/thread-to-action`](skills/thread-to-action/SKILL.md) | Parses threads and suggests developer actions | Yes |
| [`/whats-next`](skills/whats-next/SKILL.md) | Suggests top 3 next actions from full context | No |

## Skill Details

### `/address-pr-comments`

Fetches unresolved PR comments, categorizes them (must-fix, suggestion, question, nit), proposes fixes or replies for each, and executes approved actions. Use when addressing PR review feedback or when someone requests changes on your PR.

**Usage:** `/address-pr-comments <PR number or URL>`

---

### `/audit-skills`

Audits all personal Claude skills against the SKILLS_GUIDE.md manifest, latest official Claude skills documentation, and best practices. Reports issues, missing patterns, and improvement suggestions per skill. Use to keep skills healthy, consistent, and up-to-date with the latest standards.

**Usage:** `/audit-skills [skill-name] [--fix] [--verbose]`

---

### `/build-incremental`

Implements code in progressive, verified increments — auto-detects the project's toolchain, builds each unit, runs checks (typecheck, lint, test), fixes errors, and commits with semantic messages. Use when building features, implementing milestones, or making multi-step changes.

**Usage:** `/build-incremental <what to build>`

---

### `/create-pr`

Creates a well-structured pull request with product-focused summary, change highlights, and test steps. Auto-detects base branch, links Linear issues from branch name, and pushes if needed. Use when ready to open a PR or when asking to create a pull request.

**Usage:** `/create-pr [issue-id] [--base branch] [--draft]`

---

### `/investigate-ci`

Investigates GitHub Actions workflow failures for any repo. Fetches recent runs, identifies failures, extracts error logs, diagnoses root causes, and suggests fixes. Use when a deploy or CI workflow fails and you need to understand why.

**Usage:** `/investigate-ci <repo, workflow URL, or run URL>`

---

### `/organize-screenshots`

Scans a folder for recent screenshots, visually classifies which ones are relevant to current work, and organizes them into a target directory with descriptive filenames. Use when collecting screenshots for PRs, bug reports, docs, or Linear issues.

**Usage:** `/organize-screenshots <target-dir> [--source dir] [--days N]`

---

### `/post-ticket-summary`

Posts a structured implementation summary comment to a Linear issue — what was built, key decisions, reuse patterns, and how to test. Use after completing work on a ticket to document the implementation for the team.

**Usage:** `/post-ticket-summary <issue-id> [--preview] [--minimal]`

---

### `/publish-skills`

Publishes personal Claude skills to a GitHub repository for sharing. Copies skill files, generates a README catalog, commits, and pushes. Use when ready to share skill updates or after creating/updating skills.

**Usage:** `/publish-skills [--preview] [--diff]`

---

### `/slack-to-ticket`

Creates a Linear issue from a pasted Slack thread. Parses the conversation, infers title, priority, category, and description, checks for duplicates, and creates a clean ticket. Use when pasting a Slack thread to turn it into a trackable issue.

**Usage:** `/slack-to-ticket <paste slack thread here>`

---

### `/smoke-test`

Traces and verifies that something works end-to-end in any environment. Builds a check plan from natural language input, confirms it, then runs each check reporting pass/fail. Use when validating deployments, pipelines, features, or migrations.

**Usage:** `/smoke-test <describe what to verify>`

---

### `/sync-branch`

Merges one branch into another with conflict handling. Stashes work, updates both branches, merges, resolves conflicts preserving both sides, pushes, and restores state. Use when keeping a long-lived branch in sync with its upstream.

**Usage:** `/sync-branch [source] [target] [--no-push] [--dry-run]`

---

### `/thread-to-action`

Parses a pasted thread (Slack, email, GitHub, Teams), analyzes it against current git, Linear, and session context, and suggests actionable next steps — then executes them with confirmation. Use when pasting a conversation that implies developer actions.

**Usage:** `/thread-to-action <paste thread here>`

---

### `/whats-next`

Suggests the 3 most impactful next actions based on full developer context — git, Linear, PRs, and current conversation. Prioritizes blockers, unblocked items, and momentum. Use when deciding what to work on next or after finishing a task.

**Usage:** `/whats-next [optional focus area]`

---

## Design Guide

These skills follow a consistent [design guide](SKILLS_GUIDE.md) with:
- CLI-style help, config, and reset subcommands
- Persistent preferences per skill
- First-time setup guidance
- Learning from user corrections

## License

MIT
