# Claude Skills

Personal collection of Claude Code skills for developer workflows.

## Quick Start

To use these skills, copy them to your `~/.claude/skills/` directory:

```bash
# Clone and copy all skills
git clone git@github.com:mostafa-drz/claude-skills.git
cp -r claude-skills/code/* ~/.claude/skills/

# Or copy a single skill
cp -r claude-skills/code/whats-next ~/.claude/skills/
```

## Skills Catalog

### Code Skills

| Skill | Description |
|-------|-------------|
| [`/address-pr-comments`](code/address-pr-comments/SKILL.md) | Fetches unresolved PR comments, categorizes them (must-fix, suggestion, question, nit), proposes fixes or replies for each, and executes approved actions. |
| [`/audit-skills`](code/audit-skills/SKILL.md) | Audits all personal Claude skills against the SKILLS_GUIDE.md manifest, latest official Claude skills documentation, and best practices. |
| [`/build-incremental`](code/build-incremental/SKILL.md) | Implements code in progressive, verified increments -- auto-detects the project's toolchain, builds each unit, runs checks (typecheck, lint, test), fixes errors, and commits with semantic messages. |
| [`/compliance-audit`](code/compliance-audit/SKILL.md) | Audits codebases against compliance frameworks (SOC2, HIPAA, PCI-DSS, GDPR, ISO27001, etc.) using parallel agents per subdirectory/sub-repo. |
| [`/create-pr`](code/create-pr/SKILL.md) | Creates a well-structured pull request with product-focused summary, change highlights, and test steps. |
| [`/daily-brief`](code/daily-brief/SKILL.md) | Surfaces recent updates relevant to you from GitHub, Linear, Slack, and other configured sources -- PR reviews, new assignments, ticket changes, mentions, and CI failures. |
| [`/enrich-message`](code/enrich-message/SKILL.md) | Enriches a draft message with code references, Linear tickets, GitHub links, and factual data from the codebase and all available integrations. |
| [`/exploration-to-spec`](code/exploration-to-spec/SKILL.md) | Converts an exploration conversation into a structured technical specification document (roadmap, design doc, ADR, or RFC). |
| [`/get-up-to-speed`](code/get-up-to-speed/SKILL.md) | Reviews the latest git history, branch state, Linear ticket, and open work to build a concise situational summary. |
| [`/git-cleanup`](code/git-cleanup/SKILL.md) | Identifies and removes stale git branches, orphaned remote branches, and unused worktrees. |
| [`/guide-from-screenshots`](code/guide-from-screenshots/SKILL.md) | Generates polished markdown guides from a directory of screenshots and a narrative. |
| [`/investigate-ci`](code/investigate-ci/SKILL.md) | Investigates GitHub Actions workflow failures for any repo. |
| [`/organize-screenshots`](code/organize-screenshots/SKILL.md) | Scans a folder for recent screenshots, visually classifies which ones are relevant to current work, and organizes them into a target directory with descriptive filenames. |
| [`/post-pr-for-review`](code/post-pr-for-review/SKILL.md) | Generates a contextual Slack message for posting a PR to the team's review channel. |
| [`/post-ticket-summary`](code/post-ticket-summary/SKILL.md) | Posts a structured implementation summary comment to a Linear issue -- what was built, key decisions, reuse patterns, and how to test. |
| [`/publish-skills`](code/publish-skills/SKILL.md) | Publishes personal Claude skills to a GitHub repository for sharing. |
| [`/repo-timeline`](code/repo-timeline/SKILL.md) | Analyzes a repository or branch and generates an engineer-friendly timeline of changes grouped into logical units. |
| [`/respond-to-message`](code/respond-to-message/SKILL.md) | Crafts a response to a pasted message (LinkedIn, Slack, Gmail, Teams, etc.) in the user's configured tone and voice. |
| [`/shop-research`](code/shop-research/SKILL.md) | Researches products across Amazon, Google Shopping, and specialty sites via the Claude-in-Chrome extension; produces a 2026 single-file HTML report with pros/cons, reviews, and picks. Learns from feedback to personalize future searches. |
| [`/skill-creator`](code/skill-creator/SKILL.md) | Creates new Claude Code skills interactively by asking contextual questions about purpose, side effects, tools, and workflow. |
| [`/slack-to-ticket`](code/slack-to-ticket/SKILL.md) | Creates a Linear issue from a pasted Slack thread. |
| [`/smoke-test`](code/smoke-test/SKILL.md) | Traces and verifies that something works end-to-end in any environment. |
| [`/sync-branch`](code/sync-branch/SKILL.md) | Merges one branch into another with conflict handling. |
| [`/thread-to-action`](code/thread-to-action/SKILL.md) | Parses a pasted thread (Slack, email, GitHub, Teams), analyzes it against current git, Linear, and session context, and suggests actionable next steps. |
| [`/weather`](code/weather/SKILL.md) | Checks the current weather for the user's location using live online data. |
| [`/whats-next`](code/whats-next/SKILL.md) | Suggests the 3 most impactful next actions based on full developer context -- git, Linear, PRs, and current conversation. |
| [`/workday-summary`](code/workday-summary/SKILL.md) | Summarizes work done today into timesheet-ready bullet points from conversation history, git, Linear, and GitHub. |

### Desktop Skills

| Skill | Description |
|-------|-------------|
| [`inbox-catchup`](desktop/inbox-catchup/SKILL.md) | Scans all connected communication channels -- Gmail, Slack, Calendar, and any available integrations -- then produces a prioritized catchup briefing. |
| [`research-assistant`](desktop/research-assistant/SKILL.md) | Researches a topic systematically and produces a structured briefing. |

## Skill Details

### `/address-pr-comments`

Fetches unresolved PR comments, categorizes them (must-fix, suggestion, question, nit), proposes fixes or replies for each, and executes approved actions. Use when addressing PR review feedback or when someone requests changes on your PR.

**Usage:** `/address-pr-comments <PR number or URL>`

[View SKILL.md ->](code/address-pr-comments/SKILL.md)

---

### `/audit-skills`

Audits all personal Claude skills against the SKILLS_GUIDE.md manifest, latest official Claude skills documentation, and best practices. Reports issues, missing patterns, and improvement suggestions per skill. Use to keep skills healthy, consistent, and up-to-date with the latest standards.

**Usage:** `/audit-skills [skill-name] [--fix] [--verbose]`

[View SKILL.md ->](code/audit-skills/SKILL.md)

---

### `/build-incremental`

Implements code in progressive, verified increments -- auto-detects the project's toolchain, builds each unit, runs checks (typecheck, lint, test), fixes errors, and commits with semantic messages. Use when building features, implementing milestones, or making multi-step changes.

**Usage:** `/build-incremental <what to build>`

[View SKILL.md ->](code/build-incremental/SKILL.md)

---

### `/compliance-audit`

Audits codebases against compliance frameworks (SOC2, HIPAA, PCI-DSS, GDPR, ISO27001, etc.) using parallel agents per subdirectory/sub-repo. Produces a detailed markdown report with line-level code references. Use when you need to check a directory or monorepo for compliance violations before an audit or review.

**Usage:** `/compliance-audit <standard> [--output <path>] [--dir <path>] [--severity <level>] [extra context...]`

[View SKILL.md ->](code/compliance-audit/SKILL.md)

---

### `/create-pr`

Creates a well-structured pull request with product-focused summary, change highlights, and test steps. Auto-detects base branch, links Linear issues from branch name, and pushes if needed. Use when ready to open a PR or when asking to create a pull request.

**Usage:** `/create-pr [issue-id] [--base branch] [--draft]`

[View SKILL.md ->](code/create-pr/SKILL.md)

---

### `/daily-brief`

Surfaces recent updates relevant to you from GitHub, Linear, Slack, and other configured sources -- PR reviews, new assignments, ticket changes, mentions, and CI failures. Use when starting work, catching up after being away, or prepping for standup.

**Usage:** `/daily-brief [--since "yesterday"] [--sources github,linear]`

[View SKILL.md ->](code/daily-brief/SKILL.md)

---

### `/enrich-message`

Enriches a draft message with code references, Linear tickets, GitHub links, and factual data from the codebase and all available integrations. Outputs polished markdown with proper links, ready to copy-paste. Use when responding to PR reviews, Slack threads, or any discussion where you want referenceable, factual responses.

**Usage:** `/enrich-message [url] [--brief] [--no-linear]`

[View SKILL.md ->](code/enrich-message/SKILL.md)

---

### `/exploration-to-spec`

Converts an exploration conversation (architecture discussions, codebase analysis, design decisions) into a structured technical specification document. Supports roadmaps, design docs, ADRs, and RFCs. Use when an exploration conversation has produced enough clarity to write a spec, design doc, ADR, or RFC.

**Usage:** `/exploration-to-spec [--type roadmap|design|adr|rfc] [--output path]`

[View SKILL.md ->](code/exploration-to-spec/SKILL.md)

---

### `/get-up-to-speed`

Reviews the latest git history, branch state, Linear ticket, and open work to build a concise situational summary. Use when picking up work after another agent, resuming a session, or onboarding to a branch mid-flight.

**Usage:** `/get-up-to-speed [AIS-XXXX | extra context]`

[View SKILL.md ->](code/get-up-to-speed/SKILL.md)

---

### `/git-cleanup`

Identifies and removes stale git branches, orphaned remote branches, and unused worktrees. Cross-references with Linear (or other integrations) to check issue status before deleting. Use when your repos have accumulated stale branches and you want to tidy up.

**Usage:** `/git-cleanup [repo-path or natural language instructions]`

[View SKILL.md ->](code/git-cleanup/SKILL.md)

---

### `/guide-from-screenshots`

Generates polished markdown guides from a directory of screenshots and a narrative. Visually reads each image, filters out redundant or irrelevant captures, organizes them contextually, and produces a Notion-compatible markdown file with image placeholders and structured sections. Use when you have screenshots and want to create a product guide, demo walkthrough, or tool guide.

**Usage:** `/guide-from-screenshots <screenshot-dir> [--name GUIDE.md] [--type product|demo|tool]`

[View SKILL.md ->](code/guide-from-screenshots/SKILL.md)

---

### `/investigate-ci`

Investigates GitHub Actions workflow failures for any repo. Fetches recent runs, identifies failures, extracts error logs, diagnoses root causes, and suggests fixes. Use when a deploy or CI workflow fails and you need to understand why.

**Usage:** `/investigate-ci <repo, workflow URL, or run URL>`

[View SKILL.md ->](code/investigate-ci/SKILL.md)

---

### `/organize-screenshots`

Scans a folder for recent screenshots, visually classifies which ones are relevant to current work, and organizes them into a target directory with descriptive filenames. Use when collecting screenshots for PRs, bug reports, docs, or Linear issues.

**Usage:** `/organize-screenshots <target-dir> [--source dir] [--days N]`

[View SKILL.md ->](code/organize-screenshots/SKILL.md)

---

### `/post-pr-for-review`

Generates a contextual Slack message for posting a PR to the team's review channel. Pulls context from PR diff, Linear ticket, session conversation, and related PRs to write a concise, informative review request. Configurable tone, detail level, and format.

**Usage:** `/post-pr-for-review <PR number or URL> [repo-name]`

[View SKILL.md ->](code/post-pr-for-review/SKILL.md)

---

### `/post-ticket-summary`

Posts a structured implementation summary comment to a Linear issue -- what was built, key decisions, reuse patterns, and how to test. Use after completing work on a ticket to document the implementation for the team.

**Usage:** `/post-ticket-summary <issue-id> [--preview] [--minimal]`

[View SKILL.md ->](code/post-ticket-summary/SKILL.md)

---

### `/publish-skills`

Publishes personal Claude skills to a GitHub repository for sharing. Copies skill files, generates a README catalog, commits, and pushes. Use when ready to share skill updates or after creating/updating skills.

**Usage:** `/publish-skills [--preview] [--diff]`

[View SKILL.md ->](code/publish-skills/SKILL.md)

---

### `/repo-timeline`

Analyzes a repository or branch and generates a meaningful, engineer-friendly timeline of changes — grouping commits into logical units with short and detailed descriptions, using git history, changelogs, GitHub PRs, and Linear tickets. Use when you want to understand what changed, when, and why in a codebase.

**Usage:** `/repo-timeline [branch] [--since date] [--depth N]`

[View SKILL.md ->](code/repo-timeline/SKILL.md)

---

### `/respond-to-message`

Crafts a response to a pasted message (LinkedIn, Slack, Gmail, Teams, etc.) in the user's configured tone and voice. Loads platform-specific context and formatting rules, generates a response matching the platform's conventions, and copies it to clipboard. Use when you receive a message and need to reply in your own voice.

**Usage:** `/respond-to-message [--platform slack|linkedin|email|teams]`

[View SKILL.md ->](code/respond-to-message/SKILL.md)

---

### `/skill-creator`

Creates new Claude Code skills interactively by asking contextual questions about purpose, side effects, tools, and workflow. Generates a complete SKILL.md following all conventions from SKILLS_GUIDE.md. Use when creating a new skill or when asking to scaffold a skill.

**Usage:** `/skill-creator [skill-name] [--from-description "..."]`

[View SKILL.md ->](code/skill-creator/SKILL.md)

---

### `/slack-to-ticket`

Creates a Linear issue from a pasted Slack thread. Parses the conversation, infers title, priority, category, and description, checks for duplicates, and creates a clean ticket. Use when pasting a Slack thread to turn it into a trackable issue.

**Usage:** `/slack-to-ticket <paste slack thread here>`

[View SKILL.md ->](code/slack-to-ticket/SKILL.md)

---

### `/smoke-test`

Traces and verifies that something works end-to-end in any environment. Builds a check plan from natural language input, confirms it, then runs each check reporting pass/fail. Use when validating deployments, pipelines, features, or migrations.

**Usage:** `/smoke-test <describe what to verify>`

[View SKILL.md ->](code/smoke-test/SKILL.md)

---

### `/sync-branch`

Merges one branch into another with conflict handling. Stashes work, updates both branches, merges, resolves conflicts preserving both sides, pushes, and restores state. Use when keeping a long-lived branch in sync with its upstream.

**Usage:** `/sync-branch [source] [target] [--no-push] [--dry-run]`

[View SKILL.md ->](code/sync-branch/SKILL.md)

---

### `/thread-to-action`

Parses a pasted thread (Slack, email, GitHub, Teams), analyzes it against current git, Linear, and session context, and suggests actionable next steps -- then executes them with confirmation. Use when pasting a conversation that implies developer actions.

**Usage:** `/thread-to-action <paste thread here>`

[View SKILL.md ->](code/thread-to-action/SKILL.md)

---

### `/weather`

Checks the current weather for the user's location using live online data. Asks for location on first use and saves it for future runs. Use when you want a quick weather check or forecast.

**Usage:** `/weather [city name]`

[View SKILL.md ->](code/weather/SKILL.md)

---

### `/whats-next`

Suggests the 3 most impactful next actions based on full developer context -- git, Linear, PRs, and current conversation. Prioritizes blockers, unblocked items, and momentum. Use when deciding what to work on next or after finishing a task.

**Usage:** `/whats-next [optional focus area]`

[View SKILL.md ->](code/whats-next/SKILL.md)

---

### `/workday-summary`

Summarizes work done today into timesheet-ready bullet points. Analyzes conversation history, git commits, Linear tickets, and GitHub PRs to infer accomplishments. Use when ending a session, filling a timesheet, preparing for standup, writing a daily log, or when asked what was worked on.

**Usage:** `/workday-summary [--today | --yesterday | --week | --since "date"] [--format bullets|table|full-markdown|plain]`

[View SKILL.md ->](code/workday-summary/SKILL.md)

---

### `inbox-catchup` (Desktop)

Scans all connected communication channels -- Gmail, Slack, Calendar, and any available integrations -- then produces a prioritized catchup briefing. Helps triage messages and draft replies. Use when starting the day, returning from a break, or needing to quickly catch up on communications.

[View SKILL.md ->](desktop/inbox-catchup/SKILL.md)

---

### `research-assistant` (Desktop)

Researches a topic systematically and produces a structured briefing. Gathers key facts, perspectives, and sources into a clear summary. Use when asked to research something, prepare a briefing, or compile background on a topic.

[View SKILL.md ->](desktop/research-assistant/SKILL.md)

---

## Design Guide

These skills follow a consistent [design guide](SKILLS_GUIDE.md).

## License

MIT
