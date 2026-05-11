---
name: open-source
description: >-
  Audit profile for a public open-source repository. Emphasises README quality,
  CONTRIBUTING completeness, LICENSE presence, public API doc coverage, and
  broken external links. Strict on missing essentials.
inputs:
  mode: { type: string, default: comprehensive }
  scope: { type: list, default: [markdown, frontmatter, code-docs, agent-instructions] }
  severity_threshold: { type: string, default: warn+ }
  fix_policy: { type: string, default: interactive }
tasks:
  - unused-docs
  - wrong-details
  - missing-docs
  - inaccurate-data
  - missing-structure
  - best-practices
  - external-link-check
  - onboarding-flow
constraints:
  - repo-missing-essentials severity = error (CONTRIBUTING, LICENSE, README)
  - onboarding-flow severity = error
  - external-link-check cap = 100 URLs
ignored_paths:
  - node_modules/**
  - dist/**
  - build/**
  - .next/**
  - vendor/**
  - coverage/**
postProcesses:
  - open-report
---

# Template: open-source

## When to use
A public repo on GitHub/GitLab where new contributors and users land on the README. Bar is higher: missing essentials and broken external links matter more than they would internally.

## Flow (default tasks)
1. **Discover docs** — full markdown scope plus code-doc surface for public exports.
2. **Run core categories** — all 6 main categories.
3. **Run comprehensive add-ons** — external link check (cap 100), onboarding flow.
4. **Score with elevated severity** — missing essentials and onboarding gaps are errors, not warns.
5. **Report** — markdown + optionally HTML for sharing in a PR comment.

## Default constraints (why each one)
- **Missing essentials = error** — these block contribution; surface them at the top.
- **Onboarding flow = error** — first-time-user experience is the brand.
- **External link cap 100** — full coverage on a small repo; tune up via flags for larger repos.

## Examples
- Use case: pre-1.0 release audit, or response to "the README is confusing" feedback.
