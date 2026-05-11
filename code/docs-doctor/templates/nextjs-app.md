---
name: nextjs-app
description: >-
  Audit profile for a Next.js (App Router) project. Emphasises CLAUDE.md
  sanity, route documentation coverage, README accuracy against package.json,
  phantom-command detection (npm scripts), and broken internal links across
  /docs and /content.
inputs:
  mode: { type: string, default: main }
  scope: { type: list, default: [markdown, frontmatter, agent-instructions] }
  severity_threshold: { type: string, default: warn+ }
  fix_policy: { type: string, default: interactive }
tasks:
  - wrong-details
  - missing-docs
  - inaccurate-data
  - missing-structure
  - best-practices
constraints:
  - phantom-command severity = error (catches scripts that no longer exist)
  - outdated-version-claim severity = warn (active concern in JS ecosystem)
  - agent-instructions-stale severity = warn
  - route-no-page-doc severity = info (don't be too strict by default)
  - skip external-link-check unless --mode=comprehensive
ignored_paths:
  - node_modules/**
  - .next/**
  - .turbo/**
  - dist/**
  - build/**
  - coverage/**
  - out/**
postProcesses:
  - open-report
---

# Template: nextjs-app

## When to use
A Next.js App Router repo (React 18/19, TypeScript) where docs are a mix of `README.md`, `CLAUDE.md`, and any `/docs` or `/content` markdown. The most common failure modes are: README claiming an `npm run` script that was renamed, CLAUDE.md pointing at directories that moved, and version drift on the framework.

## Flow (default tasks)
1. **Discover** — markdown + frontmatter + CLAUDE.md/AGENT.md files. Skip code-docs by default (gate to comprehensive).
2. **wrong-details** — phantom commands (most common bug class), broken internal links, outdated version claims against `package.json`.
3. **missing-docs** — only repo-essentials (README), not per-route docs.
4. **inaccurate-data** — stale `lastUpdated` in blog/content frontmatter.
5. **missing-structure** — frontmatter, H1, intro.
6. **best-practices** — light touch.

## Default constraints (why each one)
- **Phantom command = error** — `npm run dev` works, but `README` saying `npm run start-server` doesn't. Misleads new contributors immediately.
- **Outdated version = warn** — JS ecosystem drift is real; flag but don't error since the doc may still be correct in spirit.
- **CLAUDE.md sanity check** — for repos where AI agents are part of the workflow, drift in agent instructions silently degrades everything.

## Examples
- Pre-release audit on `mostafa.xyz` before merging to `main`.
- After a significant refactor that renamed scripts, moved files, or upgraded Next/React.
