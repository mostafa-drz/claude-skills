---
name: blog
description: >-
  Audit profile for a content/blog repo. Emphasises frontmatter completeness,
  broken images, draft markers, date hygiene, inconsistent proper-noun casing,
  and writing best-practices. Skips code-doc checks entirely.
inputs:
  mode: { type: string, default: main }
  scope: { type: list, default: [markdown, frontmatter] }
  severity_threshold: { type: string, default: warn+ }
  fix_policy: { type: string, default: interactive }
tasks:
  - wrong-details
  - missing-structure
  - inaccurate-data
  - best-practices
constraints:
  - frontmatter-missing-required severity = error
  - future-dated severity = error (catches accidental scheduled posts)
  - skip missing-docs category (not relevant)
  - skip unused-docs (content lives in its own world; orphans = drafts)
ignored_paths:
  - node_modules/**
  - .next/**
  - dist/**
  - build/**
required_frontmatter:
  - title
  - description
  - date
postProcesses:
  - open-report
---

# Template: blog

## When to use
A blog or content repo (e.g. Next.js MDX, Astro, Hugo). The risk is meta: missing covers, broken image paths, drafts marked but accidentally published, dates set in the future after a typo.

## Flow (default tasks)
1. **Discover** — markdown + MDX + frontmatter only.
2. **wrong-details** — image links, broken internal links between posts.
3. **missing-structure** — required frontmatter, H1, intro.
4. **inaccurate-data** — future-dated posts, stale lastUpdated, inconsistent author/tag casing.
5. **best-practices** — wall-of-text, marketing fluff (since content is public-facing).

## Default constraints (why each one)
- **Frontmatter required = error** — a post without title/description breaks RSS, OG, SEO.
- **Future-dated = error** — typically a typo; rarely intentional.
- **No missing-docs / unused-docs** — blogs don't have "missing" content the way code does.

## Examples
- Pre-publish audit before a new post lands.
- Bulk audit across the whole blog after a migration.
