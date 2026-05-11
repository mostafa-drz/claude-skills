---
name: internal-docs
description: >-
  Audit profile for internal-only docs (handbooks, runbooks, ADRs, onboarding).
  Emphasises orphan detection, stale freshness vs git, missing structure, and
  agent-instruction sanity. Less strict on marketing/best-practices.
inputs:
  mode: { type: string, default: main }
  scope: { type: list, default: [markdown, frontmatter, agent-instructions] }
  severity_threshold: { type: string, default: warn+ }
  fix_policy: { type: string, default: interactive }
tasks:
  - unused-docs
  - wrong-details
  - missing-docs
  - inaccurate-data
  - missing-structure
  - freshness-vs-git
constraints:
  - orphan-doc severity = warn (was info)
  - freshness-vs-git enabled even in main mode
  - skip external-link-check (too noisy on internal URLs)
  - best-practices category disabled by default (tune to taste)
ignored_paths:
  - node_modules/**
  - dist/**
  - build/**
postProcesses:
  - open-report
---

# Template: internal-docs

## When to use
Internal docs sites (Docusaurus, MkDocs, internal Notion exports converted to markdown). Concerned with rot, orphans, and accuracy — not prose polish.

## Flow (default tasks)
1. **Discover** — markdown + agent-instructions; skip code-docs unless asked.
2. **Core categories minus best-practices** — internal docs don't need passive-voice nagging.
3. **Add freshness-vs-git** — surface stale runbooks; the most common internal-docs failure mode.
4. **Score with orphan = warn** — orphaned internal docs are likely dead.
5. **Report markdown only** — internal review, no PR-sharing needed.

## Default constraints (why each one)
- **Orphans are warns, not info** — internal docs rot via abandonment more than via being wrong.
- **No external link check** — internal URLs are unreliable to probe (VPN, auth) and the noise is high.
- **Best-practices off** — internal audience tolerates rough prose; don't be that linter.

## Examples
- Quarterly health check on a runbook repo, or before an org-wide content migration.
