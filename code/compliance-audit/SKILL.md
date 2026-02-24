---
name: compliance-audit
description: >-
  Audits codebases against compliance frameworks (SOC2, HIPAA, PCI-DSS, GDPR, ISO27001, etc.)
  using parallel agents per subdirectory/sub-repo. Produces a detailed markdown report with
  line-level code references. Use when you need to check a directory or monorepo for compliance
  violations before an audit or review.
argument-hint: <standard> [--output <path>] [--dir <path>] [--severity <level>] [extra context...]
disable-model-invocation: true
context: fork
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - Edit
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Task
---

# Compliance Audit

Scan a codebase directory (single repo, multi-repo, or monorepo) against a compliance framework. Each subdirectory gets a parallel audit agent. Output is a structured markdown report where **every finding references specific code lines**.

## Preferences

_On startup, use Read to load `~/.claude/skills/compliance-audit/preferences.md`. If it does not exist, treat as "no preferences set"._

## Context

_On startup, use Bash to detect:_
1. _Current working directory_
2. _Whether the target directory is a git repo (and its remote URL for code references)_
3. _Directory structure: list top-level subdirectories, identify monorepo packages or multi-repo layout_
4. _Tech stacks present: look for package.json, requirements.txt, Cargo.toml, go.mod, Dockerfile, .env files, etc._

_Skip any detection that fails._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/compliance-audit/preferences.md`, confirm, stop
- **anything else** → parse arguments and run the audit

### Help

```
Compliance Audit — Scan codebases against compliance frameworks

Usage:
  /compliance-audit <standard>                          Audit current directory
  /compliance-audit <standard> --dir <path>             Audit a specific directory
  /compliance-audit <standard> --output <path>          Write report to specific path
  /compliance-audit <standard> --severity <level>       Filter by minimum severity
  /compliance-audit config                              Set preferences
  /compliance-audit reset                               Clear preferences
  /compliance-audit help                                This help

Standards:
  SOC2, HIPAA, PCI-DSS, GDPR, ISO27001, NIST-CSF, OWASP, CIS, FedRAMP
  (or any compliance framework — latest requirements fetched from web)

Severity levels:
  critical, high, medium, low (default: low — shows everything)

Examples:
  /compliance-audit SOC2
  /compliance-audit HIPAA --dir ./backend --output ./reports
  /compliance-audit PCI-DSS --severity high "focus on payment processing modules"
  /compliance-audit GDPR "check data retention and consent flows"

Current preferences:
  (read from ~/.claude/skills/compliance-audit/preferences.md)
```

### Config

Use `AskUserQuestion` to collect:

- **Q1: Default output directory** — current directory, `./reports/`, or custom path
- **Q2: Default severity threshold** — low (show all), medium, high, critical
- **Q3: Report format extras** — include remediation suggestions? include compliance score? include executive summary?

Save to `~/.claude/skills/compliance-audit/preferences.md`.

### Reset

Delete `~/.claude/skills/compliance-audit/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:

> First time using /compliance-audit? Run `/compliance-audit config` to set defaults, or just continue with sensible defaults.

Then proceed normally.

## Workflow

### Step 1: Parse inputs

Extract from `$ARGUMENTS`:
- **`<standard>`** — required. The compliance framework name (e.g., SOC2, HIPAA, PCI-DSS, GDPR)
- **`--output <path>`** — optional. Directory to write the report. Default: current directory
- **`--dir <path>`** — optional. Target directory to audit. Default: current directory
- **`--severity <level>`** — optional. Minimum severity: critical, high, medium, low. Default: low
- **Extra text** — any remaining text is treated as additional context/focus areas for the audit

If `<standard>` is missing, use `AskUserQuestion` to ask which framework to audit against.

### Step 2: Detect directory structure

1. Use Bash to check if the target directory is a git repo. If yes, capture the remote URL (for code line references).
2. Use Glob to list top-level contents and identify the layout:
   - **Single repo** — one project root with src/, lib/, app/, etc.
   - **Monorepo** — packages/, apps/, services/, or workspace config (pnpm-workspace.yaml, lerna.json, nx.json, Cargo workspace)
   - **Multi-repo** — multiple subdirectories each with their own .git
3. For each identified unit (repo, package, service), detect its tech stack by looking for:
   - `package.json` (Node/JS/TS), `requirements.txt`/`pyproject.toml` (Python), `Cargo.toml` (Rust), `go.mod` (Go), `Dockerfile`, `docker-compose.yml`, `.env`/`.env.example`, CI configs
4. Build a map: `{ directory: string, stack: string[], hasGit: boolean, remoteUrl?: string }`

### Step 3: Fetch compliance requirements

Use WebSearch and WebFetch to retrieve the **latest version** of the specified compliance framework's technical controls:

- Search for: `"{standard} latest version technical controls checklist {year}"`
- Focus on official sources (e.g., AICPA for SOC2, HHS for HIPAA, PCI SSC for PCI-DSS)
- Extract the relevant technical/code-level controls (not organizational/process controls unless code-related)
- Build a checklist of controls to verify, organized by category (e.g., Access Control, Encryption, Logging, Data Handling)

If the standard is not recognized or no good source is found, use `AskUserQuestion` to clarify.

### Step 4: Parallel audit

For each directory unit identified in Step 2, launch a **Task agent** (subagent_type: "general-purpose") in parallel. Each agent receives:

- The directory path to scan
- The compliance checklist from Step 3
- The tech stack detected for that directory
- The remote URL (if available) for building code references
- Any extra context from the user's prompt

**Each agent MUST:**
1. Scan all source files in its assigned directory using Read, Glob, and Grep
2. For each compliance control, check whether the codebase satisfies or violates it
3. For every finding (pass or fail), record:
   - **Control ID** — the compliance control being checked
   - **Status** — Pass / Fail / Warning / Not Applicable
   - **Severity** — Critical / High / Medium / Low / Info
   - **Description** — what was found or missing
   - **Code reference** — MANDATORY. Format:
     - For git repos with remote: `[file:line](https://remote-url/blob/branch/file#Lline)`
     - For non-git directories: `file:line`
   - **Recommendation** — how to fix (for failures/warnings)
4. Return structured findings as a list

**CRITICAL: No finding without a code reference.** If a control cannot be mapped to a specific code location (e.g., "no encryption library found"), reference the most relevant file (e.g., package.json for missing dependencies, or the entry point file).

### Step 5: Aggregate findings

1. Collect results from all parallel agents
2. Deduplicate findings that appear across multiple directories (e.g., same dependency vulnerability)
3. Categorize by severity: Critical → High → Medium → Low → Info
4. Calculate summary stats:
   - Total controls checked
   - Pass / Fail / Warning / N/A counts
   - Compliance score: `(pass / (pass + fail + warning)) * 100`
5. Apply `--severity` filter if specified

### Step 6: Generate report

Write a markdown report with this structure:

```markdown
# Compliance Audit Report: {STANDARD}

**Date:** {date}
**Target:** {directory path}
**Standard:** {standard} ({version if known})
**Overall Score:** {score}% ({pass}/{total} controls passed)

## Executive Summary

{2-3 sentences summarizing the compliance posture, top risks, and priority actions}

## Summary

| Severity | Count |
|----------|-------|
| Critical | {n}   |
| High     | {n}   |
| Medium   | {n}   |
| Low      | {n}   |
| Info     | {n}   |
| Passed   | {n}   |

## Critical & High Findings

### {Control ID}: {Control Name}
- **Severity:** Critical/High
- **Status:** Fail
- **Directory:** {subdirectory}
- **Finding:** {description}
- **Evidence:** [{file}:{line}]({remote-url}) or `{file}:{line}`
- **Recommendation:** {how to fix}

{repeat for each critical/high finding}

## Medium & Low Findings

{same format, grouped}

## Passed Controls

{brief list of controls that passed, with code references showing compliance}

## Per-Directory Breakdown

### {subdirectory-name}
- **Stack:** {detected tech stack}
- **Controls checked:** {n}
- **Score:** {score}%
- **Key findings:** {top 3 bullet points}

{repeat for each directory}

## Recommendations

1. {Priority-ordered action items}
2. ...

## Methodology

- Standard: {standard} {version}
- Source: {URL where requirements were fetched}
- Scanned: {list of directories}
- Date: {date}
```

### Step 7: Write output

1. Determine output path:
   - If `--output` specified: write to `{output}/compliance-audit-{standard}-{date}.md`
   - Otherwise: write to `./compliance-audit-{standard}-{date}.md`
2. Use Write to save the report
3. Confirm: "Report written to `{path}`"

### Step 8: Summary and next actions

Present a brief summary in the conversation:

```
Audit complete: {standard} compliance check on {directory}
Score: {score}% — {critical} critical, {high} high, {medium} medium, {low} low findings
Report: {output path}
```

Use `AskUserQuestion` to offer:
- **Review critical findings** — walk through the critical issues one by one
- **Start fixing** — begin addressing findings in priority order
- **Re-audit** — run again after fixes
- **Done** — finish

## Supported Standards Reference

The skill should handle at minimum these frameworks (fetch latest from web):
- **SOC2** — Trust Services Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy)
- **HIPAA** — Technical Safeguards (Access Control, Audit Controls, Integrity, Transmission Security)
- **PCI-DSS** — Payment Card Industry Data Security Standard (all 12 requirements)
- **GDPR** — General Data Protection Regulation (technical measures)
- **ISO 27001** — Information Security Management (Annex A controls)
- **NIST CSF** — Cybersecurity Framework (Identify, Protect, Detect, Respond, Recover)
- **OWASP Top 10** — Web application security risks
- **CIS Benchmarks** — Center for Internet Security hardening guides
- **FedRAMP** — Federal Risk and Authorization Management Program

For any standard not listed, search the web for its latest technical controls.

## Principles

1. **Evidence-based only** — every finding MUST reference specific code lines with URLs (for git repos) or file:line (for non-repos). No vague findings.
2. **Latest standards always** — always fetch the current version of compliance requirements from the internet. Never rely on cached/outdated knowledge.
3. **Non-destructive** — the skill only reads code and writes a report. It never modifies source code unless the user explicitly asks to start fixing.
4. **Parallel for speed** — use Task agents in parallel for each subdirectory. Never audit sequentially when parallel is possible.
5. **Graceful degradation** — if a subdirectory can't be scanned (binary files, empty, access denied), note it in the report and continue with others.
