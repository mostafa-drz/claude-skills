# /change-timeline: help, first run, questions, preferences

Templates used verbatim. Kept out of SKILL.md because they're needed on only a few runs.

- [Help](#help)
- [First run](#first-run)
- [Scope questions](#scope-questions)
- [Confirm](#confirm)
- [Style preview](#style-preview)
- [Config](#config)
- [Preferences](#preferences)

## Help

```
/change-timeline: code changes as a visual timeline, every item backed by SHAs and PRs

Usage:
  /change-timeline                        this branch vs its base (or the last 30 days on main)
  /change-timeline main..feature/auth     a range
  /change-timeline v2.3.0..v2.4.0         between releases
  /change-timeline #142                   one PR, as a review walkthrough
  /change-timeline --since "2 weeks ago"  a period
  /change-timeline --path services/api    only changes under a path
  /change-timeline --view lanes           start on a layout: timeline | lanes | chapters | walkthrough
  /change-timeline style                  preview and change your page style
  /change-timeline config                 defaults
  /change-timeline reset                  clear preferences (your repos and pages are untouched)

Every run: research → your OK on the plan and style → the page.
Read-only: it never commits, pushes or comments.
```

Append the current preferences, or "No preferences yet."

## First run

One line, then carry on:

> First run: I'll show you a quick style preview before the full page, and remember what you pick. `/change-timeline style` changes it later.

## Scope questions

One `AskUserQuestion` call, only the questions still open, each with the default first and
marked "(Recommended)".

- **Range** (header `Range`): "Which changes?" with options *This branch vs main*, *Last 2
  weeks on main*, *Since the last tag (vX)*, *A specific PR*.
- **Goal** (header `Goal`): "What's this for?" with options *Understand*: timeline and
  chapters, newest first; *Review*: walkthrough in reading order with things to check.
- **Depth** (header `Depth`), only above ~40 PRs: *Notable changes* folds small fixes into
  one item per area; *Every PR*.

Without a question tool, ask the same in plain text, defaults in brackets.

## Confirm

Show the outline first, as a fenced block:

```
main · Aug 13 – Oct 23 · 14 commits · 14 PRs → 11 changes · layout: timeline · style: dark, compact, #ff6b3d

 1 feat      /learn-today: a daily learning deck…        e289ced         #56
 2 feat      /which-chart: one chart pick, drawn from…    b344b31         #55
 3 security  Real names in example data replaced…         af07241         #48
 …
 why: 4 quoted · 2 inferred · 5 not stated
```

The last line matters: it tells the user how much of the page is sourced.

Then one question (header `Plan`): "Render this?" with options:
- **Render** (Recommended): build the full page as shown.
- **Change grouping**: merge, split, rename or drop items.
- **Change layout**: timeline, lanes, chapters or walkthrough.
- **Change style**: open the style preview.

## Style preview

Publish the preview page (3 real items), then one call with up to three questions:

- **Look** (header `Style`): "Does this look right?" with options *Looks right* or *Adjust*.
- **Accent** (header `Accent`), when they pick Adjust: the three accents in DESIGN.md §3,
  each named with its hex.
- **Density** (header `Density`): *Compact* or *Comfortable*. **Mode** (header `Mode`):
  *Dark first*, *Light first* or *Follow system*.

Re-publish the preview after each change until they choose *Looks right*. Save `style`
immediately.

## Config

One `AskUserQuestion` call:

1. `Layout`: default layout: Timeline / Lanes / Chapters / Walkthrough.
2. `Order`: Newest first / Oldest first.
3. `Range`: default range on the main branch: Last 30 days / Last 2 weeks / Since last tag.
4. `Sources`: multiSelect: PR bodies and reviews / Linked issues / CHANGELOG.

## Preferences

`~/.claude/skills/change-timeline/preferences.md`. Never inside the skill directory.

```markdown
# /change-timeline preferences
Updated: YYYY-MM-DD

## Defaults
- layout: timeline
- order: newest
- default_range: last 30 days
- sources: pr-bodies, reviews, issues

## Style
<!-- approved in the style preview; the page reads these -->
- approved: YYYY-MM-DD
- mode: dark
- density: compact
- accent: #ff6b3d

## Learned
<!-- promoted after 3 consistent signals; editable by hand -->
```

No `## Style` block, or no `approved` date → step 4b runs before the full page.
