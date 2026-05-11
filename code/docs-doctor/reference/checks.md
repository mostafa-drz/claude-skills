# Check catalogue

Each check has: **key**, **category**, **default severity**, **scope** (which file types it applies to), **how it runs**, and **suggested fix** (when safe).

Categories: `unused-docs`, `wrong-details`, `missing-docs`, `inaccurate-data`, `missing-structure`, `best-practices`.

Comprehensive-mode adds: `freshness-vs-git`, `external-link-check`, `code-doc-drift`, `onboarding-flow`, `search-ability`.

---

## Category: unused-docs

### `orphan-doc`
- **Severity:** warn
- **Scope:** markdown, mdx
- **How:** for each doc file, grep the repo for inbound references (relative links, `import`, `require`, framework manifests like `next.config`, `mkdocs.yml`, `_sidebar.md`). If zero inbound references AND the file is not at a well-known entry point (`README.md`, `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md`, top-level CLAUDE.md), flag it.
- **Suggested fix:** none (manual decision — archive or link)

### `superseded-doc`
- **Severity:** info
- **Scope:** markdown
- **How:** flag pairs where two docs share >70% of headings AND one is older by git mtime. Likely duplicate after a refactor.
- **Suggested fix:** none

### `dead-section`
- **Severity:** info
- **Scope:** markdown
- **How:** sections (H2+) with fewer than 3 non-empty lines OR a TODO/TBD/Coming-Soon marker older than 90 days.
- **Suggested fix:** none

---

## Category: wrong-details

### `broken-internal-link`
- **Severity:** error
- **Scope:** markdown, mdx
- **How:** for every relative link or image, check the target exists at the resolved path. Anchor links checked against the target doc's headings.
- **Suggested fix:** if a single nearby file matches (Levenshtein ≤2 on filename), propose the rename. Otherwise no fix.

### `missing-file-reference`
- **Severity:** warn
- **Scope:** markdown, agent-instructions
- **How:** detect inline file paths in prose (e.g. `src/lib/foo.ts`) and verify they exist. Skip anything inside fenced code blocks unless it's in a "files" or "structure" section heading.
- **Suggested fix:** none

### `phantom-command`
- **Severity:** warn
- **Scope:** markdown, agent-instructions
- **How:** detect `npm run <x>` / `pnpm <x>` / `make <x>` / `just <x>` in prose or code fences. Cross-check against `package.json` scripts / `Makefile` targets / `justfile` rules. Flag commands that don't exist.
- **Suggested fix:** none

### `phantom-env-var`
- **Severity:** info
- **Scope:** markdown
- **How:** find `process.env.X` / `os.environ["X"]` / shell `$X` references in docs and verify they're declared in `.env.example`, `wrangler.toml`, `next.config`, or actually referenced in source. Flag undeclared ones.
- **Suggested fix:** none

### `outdated-version-claim`
- **Severity:** warn
- **Scope:** markdown
- **How:** detect version strings (`Next.js 14`, `React 18`, `Node 18+`) and compare against `package.json` / lockfile / `engines`. Flag mismatches.
- **Suggested fix:** propose the current version (interactive only, not auto-fix).

---

## Category: missing-docs

### `public-export-no-doc`
- **Severity:** warn (comprehensive only — gated to comprehensive mode unless scope=code-docs)
- **Scope:** code-docs (`.ts`, `.tsx`, `.js`, `.py`)
- **How:** find exported symbols without an adjacent JSDoc/TSDoc/docstring block. Filter to top-level exports (skip internal helpers).
- **Suggested fix:** none

### `route-no-page-doc`
- **Severity:** info
- **Scope:** Next.js / SvelteKit / Remix repos
- **How:** for each route file (e.g. `app/**/page.tsx`), check that an adjacent or `/docs/`-located page documents its purpose. Flag routes with no doc.
- **Suggested fix:** none

### `cli-command-no-help`
- **Severity:** info
- **Scope:** code-docs
- **How:** detect CLI entry-points (`bin` in package.json, files in `cmd/` for Go) and check for `--help` output or README-level command reference.
- **Suggested fix:** none

### `repo-missing-essentials`
- **Severity:** warn
- **Scope:** repo root
- **How:** flag absence of any of: `README.md`, `LICENSE`, `CONTRIBUTING.md` (open-source template), `CHANGELOG.md`, `.env.example` (if `.env` patterns referenced).
- **Suggested fix:** none

### `agent-instructions-stale`
- **Severity:** info
- **Scope:** agent-instructions (CLAUDE.md / AGENT.md)
- **How:** check that referenced scripts, directories, and conventions in CLAUDE.md still exist in the repo. Re-uses `phantom-command` + `missing-file-reference` logic, scoped to agent files.
- **Suggested fix:** none

---

## Category: inaccurate-data

### `stale-last-updated`
- **Severity:** info
- **Scope:** frontmatter
- **How:** compare frontmatter `lastUpdated` / `updatedAt` / `date` with git's most recent commit date for the file. If git is newer by >30 days, flag.
- **Suggested fix:** bump frontmatter date to today **only** if file changed since the stamped date (auto-fixable when `fix_policy = auto-low-risk`).

### `future-dated`
- **Severity:** warn
- **Scope:** frontmatter
- **How:** any date field set to a date > today.
- **Suggested fix:** none (could be intentional for scheduled content).

### `unverifiable-stat`
- **Severity:** info
- **Scope:** markdown
- **How:** detect prose claims with bare numbers (e.g. "10x faster", "saves 40% of time", "used by 500 teams") with no inline source/link. Heuristic — uses a regex for `\b\d+(?:\.\d+)?(?:x|%|k|m|million|billion)\b` near a verb.
- **Suggested fix:** none

### `inconsistent-name`
- **Severity:** info
- **Scope:** markdown
- **How:** detect multiple casings of the same proper-noun term in the same doc (e.g. "Nextjs", "NextJS", "Next.js"). Flag inconsistent ones.
- **Suggested fix:** none (style decision)

---

## Category: missing-structure

### `frontmatter-missing-required`
- **Severity:** warn
- **Scope:** frontmatter
- **How:** missing required fields. Required set is configurable per template; default for blog: `title, description, date`; default for docs: `title`.
- **Suggested fix:** add missing keys with safe defaults: `title` from H1, `date` from git first-commit date, `description` left blank with TODO marker. Auto-fixable.

### `frontmatter-key-disorder`
- **Severity:** info
- **Scope:** frontmatter
- **How:** keys not in canonical order (configurable). Useful for repos that enforce a key order across all posts.
- **Suggested fix:** reorder keys. Auto-fixable.

### `no-h1`
- **Severity:** warn
- **Scope:** markdown
- **How:** doc has no top-level H1, OR has multiple H1s.
- **Suggested fix:** none

### `heading-skip`
- **Severity:** info
- **Scope:** markdown
- **How:** heading hierarchy skips a level (H2 → H4).
- **Suggested fix:** none

### `no-intro`
- **Severity:** info
- **Scope:** markdown
- **How:** first content under H1 is a heading (no intro paragraph). Readers benefit from a one-line summary before sub-sections.
- **Suggested fix:** none

### `long-doc-no-toc`
- **Severity:** info
- **Scope:** markdown
- **How:** doc has 6+ H2s and no table of contents.
- **Suggested fix:** none

---

## Category: best-practices

### `wall-of-text`
- **Severity:** info
- **Scope:** markdown
- **How:** paragraph with >8 sentences or >120 words AND no break / list / example.
- **Suggested fix:** none

### `passive-voice-heavy`
- **Severity:** info
- **Scope:** markdown
- **How:** heuristic regex for `\b(is|was|were|been|being|are|be)\s+\w+ed\b` density > 25% of sentences.
- **Suggested fix:** none

### `no-examples`
- **Severity:** info
- **Scope:** markdown
- **How:** how-to / reference doc with zero code fences AND >300 words.
- **Suggested fix:** none

### `marketing-fluff`
- **Severity:** info
- **Scope:** markdown
- **How:** detect cliché phrases ("blazing fast", "world-class", "seamless", "robust", "best-in-class") near verbs.
- **Suggested fix:** none

### `jargon-without-link`
- **Severity:** info
- **Scope:** markdown
- **How:** capitalised multi-word terms used once with no link or definition (likely an internal acronym).
- **Suggested fix:** none

---

## Comprehensive-mode-only

### `freshness-vs-git`
- **Category:** inaccurate-data extension
- **Severity:** info
- **How:** doc not modified in 12+ months but references files that have changed. Suggests review.

### `external-link-check`
- **Category:** wrong-details extension
- **Severity:** warn
- **How:** HEAD request via `WebFetch` to external URLs. Capped to 25 per run (or 100 in comprehensive). 4xx/5xx → flag.
- **Suggested fix:** none

### `code-doc-drift`
- **Category:** missing-docs extension
- **Severity:** warn
- **How:** for documented exports, parse the signature and compare to current source. Flag signature changes since last doc edit.

### `onboarding-flow`
- **Category:** missing-structure extension
- **Severity:** warn
- **How:** README must include (in some form): install, run, test, contribute, license. Flag missing sections.

### `search-ability`
- **Category:** best-practices extension
- **Severity:** info
- **How:** doc lacks descriptive headings (e.g. "Overview", "Details" — too generic) OR frontmatter `description` is missing/short (<40 chars).
