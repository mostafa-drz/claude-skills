# Severity tiers

Each finding gets one of three severities. The user's `severity_threshold` filters what appears in the report.

## error
A reader of the docs will hit a wall. Examples:
- broken internal link
- referenced file does not exist (in a "files" section)
- broken table or unclosed code fence

Errors should be near-zero in a healthy repo. Always shown.

## warn
The docs are misleading or incomplete in a way that costs reader time, but they can still proceed. Examples:
- phantom command (`npm run X` that doesn't exist)
- outdated version claim
- frontmatter missing required field
- missing essential doc (LICENSE, CONTRIBUTING for OSS)
- missing H1

Warns are the bread and butter of a useful audit. Shown by default.

## info
Style, polish, or judgement calls. Reader can absolutely succeed but the docs could be sharper. Examples:
- inconsistent proper-noun casing
- passive voice density
- no TOC on a long doc
- unverifiable stat
- orphan doc that might still be intentional

Info findings are great signal in `comprehensive` mode and noise in `quick` mode. Default threshold is `warn+` so info is hidden unless requested.

## Promotion across severities

When the user's feedback consistently flags a category as too strict (3+ sessions in journal say "too strict on best-practices"), the skill should:
- demote the affected category's default severity by one tier (warn → info, info → off)
- log the demotion in the journal as a `Signal:` line

Conversely, if a category is consistently called out as "important — surface more", promote it (info → warn).

These adjustments live under `## Learned` in `preferences.md` as explicit per-category severity overrides, e.g.:
- `severity_override: best-practices=info`
- `severity_override: missing-docs=error`

Apply overrides after the default severity is computed but before the threshold filter.

## Auto-fix allowlist (independent of severity)

These rules are safe to auto-apply under `fix_policy = auto-low-risk`:
- `broken-internal-link` — only when a unique nearby file matches by Levenshtein ≤2
- `frontmatter-missing-required` — only safe defaults (title from H1, date from git)
- `frontmatter-key-disorder` — pure reorder, no value changes
- `stale-last-updated` — only when file changed since the stamped date

Everything else requires `fix_policy = interactive` and explicit user approval per fix.
