# Claude Skills

Personal collection of Claude Code skills for developer workflows.

> 🤖 **Automation**: a new Claude Desktop skill is added here every morning by the [Daily Skill Factory](./automation/README.md) — a routine running on Claude infrastructure that researches one workflow, builds the skill, and opens a PR for review.

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
| [`/address-pr-feedback`](code/address-pr-feedback/SKILL.md) | Comprehensive PR-feedback workflow: parallel agents critique each comment, then implement fixes with incremental commits and browser validation. Heavier due-diligence variant of `/address-pr-comments`. |
| [`/audit-skills`](code/audit-skills/SKILL.md) | Audits all personal Claude skills against the SKILLS_GUIDE.md manifest, latest official Claude skills documentation, and best practices. |
| [`/audit-ui-e2e`](code/audit-ui-e2e/SKILL.md) | Runs a beginner-mind end-to-end UI audit of any running app — local dev, staging, prod, or any URL. Drives Chrome through interactive elements, collects structured findings, and hands off to `/triage-board` for the Desktop folder + viewer. |
| [`/build-incremental`](code/build-incremental/SKILL.md) | Implements code in progressive, verified increments -- auto-detects the project's toolchain, builds each unit, runs checks (typecheck, lint, test), fixes errors, and commits with semantic messages. |
| [`/capture-screens`](code/capture-screens/SKILL.md) | Drives a web app through Playwright MCP and takes context-aware named screenshots per feature state. Outputs manifest.json + summary. Composable primitive — other skills (user-guide, demo-docs) consume its manifest. |
| <img src="code/chunk-pr/icon.svg" width="22" height="22" alt="/chunk-pr icon" valign="middle"> &nbsp; [`/chunk-pr`](code/chunk-pr/SKILL.md) | Analyzes a big PR, branch, or commit range and proposes a sequence of smaller, dependency-aware, merge-safe PRs. Suggests a plan; on approval, creates chunk branches, cherry-picks commits, pushes, and opens draft PRs. Parent branch stays untouched. |
| <img src="code/clean-copy/icon.svg" width="22" height="22" alt="/clean-copy icon" valign="middle"> &nbsp; [`/clean-copy`](code/clean-copy/SKILL.md) | Cleans terminal-formatted text (uniform indent, trailing whitespace, soft-wrapped paragraphs) and copies it to the macOS clipboard formatted for the target platform — Gmail, Slack, LinkedIn, plain, or markdown. |
| [`/compliance-audit`](code/compliance-audit/SKILL.md) | Audits codebases against compliance frameworks (SOC2, HIPAA, PCI-DSS, GDPR, ISO27001, etc.) using parallel agents per subdirectory/sub-repo. |
| [`/create-pr`](code/create-pr/SKILL.md) | Creates a well-structured pull request with product-focused summary, change highlights, and test steps. |
| [`/daily-brief`](code/daily-brief/SKILL.md) | Surfaces recent updates relevant to you from GitHub, Linear, Slack, and other configured sources -- PR reviews, new assignments, ticket changes, mentions, and CI failures. |
| <img src="code/docs-doctor/icon.svg" width="22" height="22" alt="/docs-doctor icon" valign="middle"> &nbsp; [`/docs-doctor`](code/docs-doctor/SKILL.md) | Audits a repository's documentation for unused docs, wrong details, missing coverage, inaccurate data, broken structure, and writing best-practices. Generates a severity-ranked markdown report (HTML optional) with optional `--fix` for low-risk auto-fixes (broken links, frontmatter, stale dates). Supports modes (main / comprehensive / focused / quick) and per-profile templates (open-source, internal-docs, blog, nextjs-app). |
| <img src="code/emotional-recap/icon.svg" width="22" height="22" alt="/emotional-recap icon" valign="middle"> &nbsp; [`/emotional-recap`](code/emotional-recap/SKILL.md) | Reviews recent Claude Code conversations from a wellbeing perspective — sentiment, tone, emotional arc, recurring patterns — and generates a supportive, science-grounded Markdown + HTML report. Uses Plutchik, Ekman, Russell's circumplex, and Pennebaker linguistic markers; cites the science behind every observation. Supportive, not diagnostic. |
| [`/enrich-message`](code/enrich-message/SKILL.md) | Enriches a draft message with code references, Linear tickets, GitHub links, and factual data from the codebase and all available integrations. |
| [`/exploration-to-spec`](code/exploration-to-spec/SKILL.md) | Converts an exploration conversation into a structured technical specification document (roadmap, design doc, ADR, or RFC). |
| <img src="code/extract-skill/icon.svg" width="22" height="22" alt="/extract-skill icon" valign="middle"> &nbsp; [`/extract-skill`](code/extract-skill/SKILL.md) | Scans the current conversation for patterns worth turning into a reusable skill or memory rule — feedback, workflows, corrections, best practices. Classifies each candidate as skill (multi-step workflow) or memory (single rule), cross-checks against existing skills + MEMORY.md, then hands off to `/skill-creator` or writes the memory entry directly. |
| [`/get-up-to-speed`](code/get-up-to-speed/SKILL.md) | Reviews the latest git history, branch state, Linear ticket, and open work to build a concise situational summary. |
| [`/git-cleanup`](code/git-cleanup/SKILL.md) | Identifies and removes stale git branches, orphaned remote branches, and unused worktrees. |
| [`/next-steps`](code/next-steps/SKILL.md) | Generates a stakeholder-aligned next-steps checklist for a multi-stakeholder project from the current conversation and connected context (Linear, PR, Slack, Notion). Grouped by owner, prioritised, pasteable into Slack/Notion/Linear. |
| [`/guide-from-screenshots`](code/guide-from-screenshots/SKILL.md) | Generates polished markdown guides from a directory of screenshots and a narrative. |
| [`/investigate-ci`](code/investigate-ci/SKILL.md) | Investigates GitHub Actions workflow failures for any repo. |
| [`/organize-screenshots`](code/organize-screenshots/SKILL.md) | Scans a folder for recent screenshots, visually classifies which ones are relevant to current work, and organizes them into a target directory with descriptive filenames. |
| [`/post-pr-for-review`](code/post-pr-for-review/SKILL.md) | Generates a contextual Slack message for posting a PR to the team's review channel. |
| [`/post-ticket-summary`](code/post-ticket-summary/SKILL.md) | Posts a structured implementation summary comment to a Linear issue -- what was built, key decisions, reuse patterns, and how to test. |
| [`/project-updates`](code/project-updates/SKILL.md) | Drafts Linear project status updates (Done / In Progress / Next / Blockers) for each project you lead, gathering context from Linear, git, GitHub, Slack, Notion, Gmail, Calendar. All site-specific values (repos, project list, Linear org) configured via preferences. Never auto-posts. |
| [`/publish-skills`](code/publish-skills/SKILL.md) | Publishes personal Claude skills to a GitHub repository for sharing. |
| [`/release-notes`](code/release-notes/SKILL.md) | Generates brief, truth-based release notes for a release PR by listing each squash-merged PR with a one-paragraph summary and linked tracker tickets. Tracker-agnostic — Linear, Jira, GitHub Issues, Asana, ClickUp, Shortcut, Plane, or any tracker via a URL template. |
| [`/repo-timeline`](code/repo-timeline/SKILL.md) | Analyzes a repository or branch and generates an engineer-friendly timeline of changes grouped into logical units. |
| [`/respond-to-message`](code/respond-to-message/SKILL.md) | Crafts a response to a pasted message (LinkedIn, Slack, Gmail, Teams, etc.) in the user's configured tone and voice. |
| <img src="code/shop-research/icon.svg" width="22" height="22" alt="/shop-research icon" valign="middle"> &nbsp; [`/shop-research`](code/shop-research/SKILL.md) | Researches products across Amazon, Google Shopping, and specialty sites via the Claude-in-Chrome extension; produces a 2026 single-file HTML report with pros/cons, reviews, and picks. Learns from feedback to personalize future searches. |
| <img src="code/should-i-buy/icon.svg" width="22" height="22" alt="/should-i-buy icon" valign="middle"> &nbsp; [`/should-i-buy`](code/should-i-buy/SKILL.md) | Takes product URLs you're considering, asks two sharp clarifying questions, opens each in real Chrome to extract price/specs/reviews/returns, cross-checks independent reviews, and ships a 2026 HTML report with a clear verdict — buy, wait, pick X, or skip. Learns from thumbs-up/down and past regrets. |
| [`/skill-creator`](code/skill-creator/SKILL.md) | Creates new Claude Code skills interactively by asking contextual questions about purpose, side effects, tools, and workflow. |
| [`/slack-to-ticket`](code/slack-to-ticket/SKILL.md) | Creates a Linear issue from a pasted Slack thread. |
| [`/smoke-test`](code/smoke-test/SKILL.md) | Traces and verifies that something works end-to-end in any environment. |
| [`/svg-art`](code/svg-art/SKILL.md) | Generates artistic SVGs directly as code — minimal line icons, geometric marks, generative patterns, hand-drawn compositions — plus a 2026 HTML gallery preview. Learns aesthetic preferences from per-session feedback. |
| [`/sync-branch`](code/sync-branch/SKILL.md) | Merges one branch into another with conflict handling. |
| [`/thread-to-action`](code/thread-to-action/SKILL.md) | Parses a pasted thread (Slack, email, GitHub, Teams), analyzes it against current git, Linear, and session context, and suggests actionable next steps. |
| <img src="code/triage-board/icon.svg" width="22" height="22" alt="/triage-board icon" valign="middle"> &nbsp; [`/triage-board`](code/triage-board/SKILL.md) | Generates a structured triage artifact from session findings — a Desktop folder with JSON Schema, report.json, prose markdown, and a single-file HTML viewer that exports MD/CSV/JSON and offers a per-finding "Copy as Markdown" for pasting into Linear/GitHub/Notion. |
| [`/ui-test`](code/ui-test/SKILL.md) | Runs UI tests described in plain English by driving real Chrome via the Claude-in-Chrome extension. Covers e2e flows (clicks, forms, assertions), visual checks (screenshot + optional baseline diff), accessibility (axe-core), performance (Web Vitals + light Lighthouse-style metrics), plus an interactive `--debug` mode that tails console + network. Accepts inline descriptions or `./tests/ui/*.md` files. Per-run folder with artifacts plus a single-file 2026 dashboard report (verdict-forward, bento-grid). Learns from per-run feedback. |
| [`/ux-interview`](code/ux-interview/SKILL.md) | Plays the role of a real user in an interview-style usability test — drives real Chrome via the claude-in-chrome extension to explore a product think-aloud style, flags confusion / friction / delight, captures GIFs and screenshots of friction moments, and produces a severity-ranked UX report with prioritized recommendations. Learns over time which findings count as signal vs noise. |
| [`/weather`](code/weather/SKILL.md) | Checks the current weather for the user's location using live online data. |
| [`/whats-next`](code/whats-next/SKILL.md) | Suggests the 3 most impactful next actions based on full developer context -- git, Linear, PRs, and current conversation. |
| [`/workday-summary`](code/workday-summary/SKILL.md) | Summarizes work done today into timesheet-ready bullet points from conversation history, git, Linear, and GitHub. |
| [`/workflow-advisor`](code/workflow-advisor/SKILL.md) | Analyzes recent Claude Code conversations and local Claude state, researches the latest Claude Code features, and suggests one workflow improvement at a time with reasoning and a concrete action item. |

### Desktop Skills

| Skill | Description |
|-------|-------------|
| [`inbox-catchup`](desktop/inbox-catchup/SKILL.md) | Scans all connected communication channels -- Gmail, Slack, Calendar, and any available integrations -- then produces a prioritized catchup briefing. |
| [`research-assistant`](desktop/research-assistant/SKILL.md) | Researches a topic systematically and produces a structured briefing. |
| <img src="desktop/weekly-plan/icon.svg" width="22" height="22" alt="weekly-plan icon" valign="middle"> &nbsp; [`weekly-plan`](desktop/weekly-plan/SKILL.md) | Synthesizes a forward-looking week plan from Calendar, Gmail, and Linear — meeting density, top 3 outcomes, focus windows, and a defer list. |

## Skill Details

### `/address-pr-comments`

Fetches unresolved PR comments, categorizes them (must-fix, suggestion, question, nit), proposes fixes or replies for each, and executes approved actions. Use when addressing PR review feedback or when someone requests changes on your PR.

**Usage:** `/address-pr-comments <PR number or URL>`

[View SKILL.md ->](code/address-pr-comments/SKILL.md)

---

### `/address-pr-feedback`

Comprehensively addresses PR feedback by fetching all comments, deploying parallel agents for critical analysis of each suggestion, making implementation decisions, then systematically implementing fixes with incremental commits and browser validation. Use when you need to systematically process and implement all PR review feedback with due-diligence validation — distinct from `/address-pr-comments`, which is the lighter triage variant.

**Usage:** `/address-pr-feedback <pr-number|url> [--dry-run] [--auto-push] [--no-browser]`

[View SKILL.md ->](code/address-pr-feedback/SKILL.md)

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

### `/capture-screens`

Automatically navigates a web app using Playwright MCP and captures context-aware named screenshots at each product feature state. Names each file semantically (e.g., `checkout-payment-form-filled.png`), outputs a `manifest.json` mapping filenames to descriptions, and a summary report. Use when documenting product features, generating demo screenshots, building user guides, or creating visual test assets for any web application. Composable primitive — other skills (user-guide, demo-docs) consume its `manifest.json` output.

**Usage:** `/capture-screens [context-description] [--url <url>] [--features <list>] [--output <dir>] [--no-highlight] [--viewport <WxH>] [--auth <instructions>] [--inject-js <file>]`

[View SKILL.md ->](code/capture-screens/SKILL.md)

---

### `/chunk-pr`

Analyzes a large pull request, branch, or commit range and proposes a sequence of smaller, dependency-aware, merge-safe PRs following review best practices — schema before API before UI, refactor before feature, one concern per PR. Suggests a plan; the user approves. On approval, creates chunk branches, cherry-picks commits, pushes, opens draft PRs, and links them to the parent Linear issue. The parent branch stays untouched. Use when a PR is too big to review, when reviewers ask "can you split this up?", or when planning how to ship a large feature incrementally.

**Usage:** `/chunk-pr [pr-or-branch-or-range] [--base branch] [--max-lines N] [--strategy conservative|balanced|aggressive] [--dry-run] [--draft]`

[View SKILL.md ->](code/chunk-pr/SKILL.md)

---

### `/clean-copy`

Cleans terminal-formatted text and copies it to the macOS clipboard formatted for the target platform (Gmail, Slack, LinkedIn, plain, markdown). Strips uniform leading indentation, trailing whitespace, and soft-wrapped paragraphs that come from copying out of a terminal, then applies platform conventions (Slack `*bold*` vs Gmail plain prose, etc.). Use when the user wants to paste a draft from chat into Gmail, Slack, LinkedIn, or another tool without nightmare terminal formatting coming along.

**Usage:** `/clean-copy <platform> [--source last|paste|file:<path>] [--no-reflow] [--preview]`

[View SKILL.md ->](code/clean-copy/SKILL.md)

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

### `/extract-skill`

Scans the current conversation for patterns worth turning into a reusable skill or memory rule — feedback you've given Claude, workflows you've walked through, corrections, best practices, recurring setups. Proposes candidates, classifies each as skill (multi-step workflow) or memory (single rule), cross-checks against existing skills and MEMORY.md to avoid duplicates, then hands off to `/skill-creator` (for skills) or writes the memory entry directly. Use when the conversation contains reusable knowledge you don't want to teach Claude again.

**Usage:** `/extract-skill [--memory-only] [--skill-only] [--dry-run]`

[View SKILL.md ->](code/extract-skill/SKILL.md)

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

### `/next-steps`

Generates a stakeholder-aligned next-steps checklist for a multi-stakeholder project from the current Claude conversation and any connected context (Linear ticket, PR, Slack thread, Notion doc). Output is grouped by owner (PM, design, engineering, leadership), prioritised, and pasteable into Slack/Notion/Linear. Use when you've just had a working session and now need to align teammates on what happens next, who owns it, and what's blocked.

**Usage:** `/next-steps [scope-hint]`

[View SKILL.md ->](code/next-steps/SKILL.md)

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

### `/project-updates`

Drafts Linear project status updates for each project the user leads, following the Done / In Progress / Next / Blockers template. Gathers context from Linear issues and comments, git history across configured repos, GitHub PRs, Slack mentions, Notion edits, and Gmail/Calendar. Never auto-posts — always shows the draft so the user can paste it into Linear. All site-specific values (repos root, repo list, Linear org slug) are configured via `preferences.md` — no hardcoded paths. Use when preparing daily or end-of-day Linear updates, writing project status, or prepping for standup.

**Usage:** `/project-updates [--since "24h"] [--projects "slug1,slug2"] [--sources linear,git,github,slack,notion] [--project <slug>] [--dry-run]`

[View SKILL.md ->](code/project-updates/SKILL.md)

---

### `/publish-skills`

Publishes personal Claude skills to a GitHub repository for sharing. Copies skill files, generates a README catalog, commits, and pushes. Use when ready to share skill updates or after creating/updating skills.

**Usage:** `/publish-skills [--preview] [--diff]`

[View SKILL.md ->](code/publish-skills/SKILL.md)

---

### `/release-notes`

Generates brief, truth-based release notes for a release PR (typically main → prod) by listing each squash-merged PR with a one-paragraph summary drawn from each PR body, plus the linked issue-tracker tickets. **Tracker-agnostic** — works with Linear, Jira, GitHub Issues, Asana, ClickUp, Shortcut, Plane, Notion, or any tracker via a configurable `ticket-url-template` with a `{TICKET}` placeholder. If no template is configured, ticket IDs render as plain text. Use when opening or updating a release PR.

**Usage:** `/release-notes [pr-number]`

[View SKILL.md ->](code/release-notes/SKILL.md)

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

### `/svg-art`

Generates artistic SVGs directly as code — minimal line icons, geometric marks, generative patterns, or hand-drawn compositions — and assembles a modern 2026 HTML gallery preview. Saves each session to its own semantically named folder. Learns from feedback across sessions: which styles landed, which compositions were rejected, which stroke weights and palettes you return to. The aesthetic gets more personalized each session. Use when you want icons for a product, a branded mark, a generative poster, or a set of decorative SVGs for a page, blog, or app.

**Usage:** `/svg-art [what to generate] [--style mode] [--count N] [--palette colors] [--stroke px] [--canvas WxH] [--notes text]`

[View SKILL.md ->](code/svg-art/SKILL.md)

---

### `/thread-to-action`

Parses a pasted thread (Slack, email, GitHub, Teams), analyzes it against current git, Linear, and session context, and suggests actionable next steps -- then executes them with confirmation. Use when pasting a conversation that implies developer actions.

**Usage:** `/thread-to-action <paste thread here>`

[View SKILL.md ->](code/thread-to-action/SKILL.md)

---

### `/ui-test`

Runs UI tests described in plain English by driving real Chrome via the Claude-in-Chrome extension. Covers end-to-end flows (clicks, forms, assertions), visual checks (screenshot + optional baseline diff), accessibility (axe-core), performance (Web Vitals + light Lighthouse-style metrics), and an interactive `--debug` mode that tails console + network and surfaces issues without explicit assertions. Accepts inline descriptions or test files in `./tests/ui/*.md`. Per-run folders contain artifacts (screenshots, console, network, axe report, perf metrics) plus a single-file 2026 HTML report with a verdict-forward bento-grid layout (dark + light, mobile-responsive, no external scripts). Learns from per-run feedback to bias future runs (false-positive a11y rules, flaky baselines, screenshot strategy). Use when verifying a UI flow, screenshotting a regression, auditing accessibility, profiling a page, or debugging something visibly broken in a real browser session.

**Usage:** `/ui-test "<description>" | --file <path> | --suite <glob> | --debug <url|description> | record <name>`

[View SKILL.md ->](code/ui-test/SKILL.md)

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

### `/workflow-advisor`

Analyzes recent Claude Code conversations and local Claude state (skills, settings, memory files, CLAUDE.md), researches the latest Claude Code features and best practices online, and suggests one workflow improvement at a time with reasoning and a concrete action item. Can save accepted suggestions to memory for tracking. Use when you want to discover underused Claude Code features, improve your development workflow, stay current with the latest Claude Code capabilities, or get a periodic workflow health-check.

**Usage:** `/workflow-advisor [--all] [--count <n>]`

[View SKILL.md ->](code/workflow-advisor/SKILL.md)

---

### `inbox-catchup` (Desktop)

Scans all connected communication channels -- Gmail, Slack, Calendar, and any available integrations -- then produces a prioritized catchup briefing. Helps triage messages and draft replies. Use when starting the day, returning from a break, or needing to quickly catch up on communications.

[View SKILL.md ->](desktop/inbox-catchup/SKILL.md)

---

### `research-assistant` (Desktop)

Researches a topic systematically and produces a structured briefing. Gathers key facts, perspectives, and sources into a clear summary. Use when asked to research something, prepare a briefing, or compile background on a topic.

[View SKILL.md ->](desktop/research-assistant/SKILL.md)

---

### `weekly-plan` (Desktop)

Synthesizes a forward-looking week plan from Calendar, Gmail, and Linear. Scans the coming seven days of meetings, surfaces email threads needing action, and pulls current-cycle Linear priorities, then produces a structured plan: meeting density by day, top 3 outcomes to own, open focus windows, and a defer list. Use when planning the week ahead, asking what to focus on this week, Monday morning planning, or preparing for standup.

[View SKILL.md ->](desktop/weekly-plan/SKILL.md)

---

## Design Guide

These skills follow a consistent [design guide](SKILLS_GUIDE.md).

## License

MIT
