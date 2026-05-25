---
name: upgrade-brief
description: >-
  Researches a library or package upgrade from one version to another. Fetches
  the changelog, identifies breaking changes, surfaces migration guides and
  codemods, and produces a structured upgrade brief with a migration checklist.
  Use when upgrading a dependency, planning a major version bump, reviewing
  what changed in a package between versions, asking "what broke in X v2",
  or preparing for a breaking-change migration.
---

# Upgrade Brief

Every non-trivial package upgrade follows the same manual loop: open the
changelog, navigate to the right version range, read dozens of entries, find
the breaking changes, check GitHub issues for known regressions, assemble
notes. This skill handles that loop — provide the package and version range,
get a structured brief ready to act on.

## Process

### 1. Identify the Package and Version Range

Accept from context, a pasted snippet, or by asking:

- **Package name** — e.g. `react`, `axios`, `next`, `pydantic`, `zod`
- **Current version** — e.g. `17.0.2`
- **Target version** — e.g. `18.3.0` or `latest`

If target is "latest", web-search the current published version first.
If the user pastes a `package.json` or `requirements.txt` excerpt, extract
the relevant package from it.

### 2. Locate the Changelog

Search in order:

1. Official release page: `github.com/<org>/<repo>/releases`
2. Changelog file: `github.com/<org>/<repo>/blob/main/CHANGELOG.md`
3. Package registry page: npmjs.com or PyPI changelog links
4. Official migration guide (for frameworks, e.g. `react.dev/blog/...`)
5. Web search: `<package> changelog <old version> to <new version>`

Use code execution to fetch, parse, and filter changelog content when the
raw text is long. Extract only the sections between the two version tags.

### 3. Extract the Relevant Version Range

Filter to entries between current and target version only.
If the changelog follows Keep a Changelog format, sections are headed
`## [x.y.z]` — extract all between the two bounds (inclusive of target,
exclusive of current).

```
Version range: 17.0.2 → 18.3.0
Sections found: 18.3.0, 18.2.0, 18.1.0, 18.0.0
```

### 4. Classify Breaking Changes

Within each version section, label every change:

- `⚠️ Breaking` — API removed, signature changed, behaviour changed
- `📦 Dep change` — peer dependency added, updated, or dropped
- `🔄 API changed` — signature or type changed; usually adapter-fixable
- `🛠 Codemod` — automated migration available
- `✅ Added / Fixed` — additive; no migration needed

### 5. Find Migration Resources

Web-search for:

- Official migration guide: `<package> v<old> to v<new> migration guide`
- Codemod tool: `<package> codemod`
- Known regressions: GitHub issues labelled `breaking-change` or `regression`

Prioritise Tier 1 (official docs, maintainer blog) over community posts.

### 6. Produce the Upgrade Brief

```
📦 Upgrade Brief: <package> <old> → <new>
Generated: <date>

## Summary
<2–3 sentences: how significant, what's the theme>

## Breaking Changes (<n>)
1. ⚠️ <change> — <what to do>
2. ⚠️ <change> — <what to do>

## Changed APIs (<n>)
- 🔄 <change> — <note>

## Migration Steps
1. <step>
2. <step>

## Resources
- [Official migration guide](<url>) — <1-line summary>
- [Codemod](<url>) — automates step N

## Known Issues
- <issue title> (<url>) — open / fixed in <version>

## Testing Checklist
- [ ] Run existing tests after upgrade
- [ ] Verify <area affected by breaking change>
- [ ] Check peer dependency compatibility
```

If the changelog is sparse or missing for a version range, say so — don't
guess at what changed.

## Guidelines

- **Breaking changes first.** The most important information goes at the top.
- **One step per line.** Don't combine "update X and also Y" — the checklist
  must be atomic so each item can be checked off independently.
- **Codemods are worth surfacing.** Many popular packages ship codemods that
  automate tedious migrations. Flag them even if the user didn't ask.
- **Scope strictly.** Only include changes within the requested version range.
  Do not summarise older history.
- **Honest about gaps.** If the changelog doesn't cover a version, note which
  source was checked and what was missing.

## Example

**User:** "I need to upgrade axios from 0.27.2 to 1.6.0"

**Output:**

```
📦 Upgrade Brief: axios 0.27.2 → 1.6.0
Generated: 2026-05-25

## Summary
Major version bump (0.x → 1.x). Axios 1.0 tightened TypeScript types and
restructured error objects. Small surface area overall — 2 breaking changes,
both fixable in under an hour.

## Breaking Changes (2)
1. ⚠️ Error type — catch blocks now receive AxiosError; use
   `axios.isAxiosError(e)` guard before accessing `e.response`.
2. ⚠️ CJS/ESM dual package — bundlers that manually alias axios may need
   resolver config updates.

## Changed APIs (1)
- 🔄 AxiosResponse<T> generics tightened — affects code that casts through
  `any`.

## Migration Steps
1. Add `axios.isAxiosError(e)` guards in all catch blocks using `e.response`.
2. Run TypeScript compiler and address generic type errors.
3. Verify bundler output resolves the correct CJS/ESM entry.

## Resources
- [Axios 1.0 release](https://github.com/axios/axios/releases/tag/v1.0.0)
- [Community migration notes](https://github.com/axios/axios/issues/4890)

## Known Issues
- No open regressions at 1.6.0 for the patterns above.

## Testing Checklist
- [ ] Run unit tests with upgraded axios
- [ ] Verify error-handling paths in all API client code
- [ ] Check bundler output for duplicate axios copies
```
