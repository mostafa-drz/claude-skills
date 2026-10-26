---
name: change-timeline
description: >-
  Visualizes code changes as an evidence-backed timeline artifact: every item has a title,
  what changed, why, and the commit SHAs and PRs that prove it. Researches git history, PR
  bodies, reviews and linked issues first, asks only what it cannot work out, then shows the
  plan and a style preview for your OK before rendering one of four review templates:
  vertical timeline, swimlanes by area, release chapters, or a step-by-step review
  walkthrough, in your saved design style. Use to understand what changed in a branch, PR,
  release or period, or to review a branch before merge.
argument-hint: "[BASE..HEAD | #PR | branch] [--since WHEN] [--view timeline|lanes|chapters|walkthrough] [--path DIR] | help | config | style | reset"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Glob
  - Grep
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git diff *)
  - Bash(git rev-list *)
  - Bash(git rev-parse *)
  - Bash(git merge-base *)
  - Bash(git tag *)
  - Bash(git remote *)
  - Bash(git branch *)
  - Bash(gh pr view *)
  - Bash(gh pr list *)
  - Bash(python3 ~/.claude/skills/change-timeline/scripts/*)
  - mcp__github__pull_request_read
  - mcp__github__list_pull_requests
  - mcp__github__issue_read
metadata:
  trigger: "Wanting to see or review what changed in a branch, PR, release or time period as a visual timeline where every item links to its commits and PRs."
  tags: "git, github, code review, timeline, visualization, artifacts, pull-requests, history"
---

# Change timeline

Turns a range of code changes into a page you can read and review: each change is a card
with a **title**, **what changed**, **why**, and the **SHAs and PRs** it is built from. Four
layouts over the same data: **Timeline**, **Lanes** (by area), **Chapters** (by release or
phase), **Walkthrough** (review steps with a "reviewed" tick).

`/repo-timeline` gives a quick text narrative; this skill is the visual, evidence-first one.

## Standing rules (hold for the whole run)

1. **Evidence or nothing.** Every item cites at least one commit SHA that you read from git
   *in this run*. Never type a SHA from memory or shorten one by hand: copy full SHAs from
   `collect.py` output. The validator runs with `--repo` and rejects any SHA that does not
   resolve.
2. **The why is quoted, labelled or absent.** A reason stated in a PR body, commit body,
   review or linked issue goes in `why` with the quote in `evidence`. A reason you read off
   the diff goes in `why` with `why_inferred: true`. If nothing supports one, set
   `why: null`, and the page says so. A missing reason is useful to a reviewer; an invented
   one misleads them.
3. **The UI is confirmed with the user, every run.** Never publish the final page before the
   user has OK'd the plan and the style in this run (step 4). The first run, or any run
   without an approved style, shows a style preview first. Auto mode does not skip this.
4. **Read-only on the repository.** Never commit, push, comment on a PR or change a ticket.
   The only files written are `timeline.json` and the page, in the scratchpad (or the
   current directory when there is none).
5. **Minimal, and in the user's style.** Apply [`DESIGN.md`](./DESIGN.md) and the approved
   `style` from preferences. One accent, no decoration, type chips carry text as well as
   colour.

## Startup

- Read `~/.claude/skills/change-timeline/preferences.md` if it exists (format and keys:
  [`references/help.md`](./references/help.md#preferences)). Missing file → first run: show
  the one-line intro from the same reference and continue. Never block on setup.
- Read [`DESIGN.md`](./DESIGN.md) before writing anything visual.
- `git rev-parse --show-toplevel`, current branch, default branch
  (`git rev-parse --abbrev-ref origin/HEAD`), `git remote get-url origin`. Not a git repo →
  say so and stop.

## Routing on `$ARGUMENTS`

- `help` → print the help block from [`references/help.md`](./references/help.md#help); stop.
- `config` → the config questions in the same reference; save; stop.
- `style` → run the style preview (step 4b) on the last or example timeline; save; stop.
- `reset` → delete `preferences.md` and say: "Preferences cleared, including your approved
  style. Your repositories and pages are untouched." Stop.
- `BASE..HEAD` → that range. `#123` or a PR URL → **PR mode** (its commits, walkthrough
  default). A branch name → `merge-base(default, branch)..branch`. `--since`, `--until`,
  `--path`, `--view` as named.
- Nothing → on a feature branch: `merge-base..HEAD` (walkthrough default). On the default
  branch: last 30 days, or the preference `default_range`.

## The flow

```
- [ ] 1. Scope: resolve the range; ask only what is ambiguous (one round, ≤3, defaults)
- [ ] 2. Research: collect.py, then every PR, review and linked issue in the range
- [ ] 3. Synthesize: group commits into changes; title, what, why, evidence, area, chapter
- [ ] 4. Confirm: plan outline + style preview → user OK  (never skipped)
- [ ] 5. Write timeline.json → validate --repo → fix until OK
- [ ] 6. Render the artifact
- [ ] 7. Close in two lines; learn
```

### 1. Scope

Resolve the range to concrete refs and say it in one line ("`main`, Aug 13 – Oct 23, 14
commits"). Ask only when it is genuinely unclear, in **one round of at most three
questions, each with a default**, so "go" answers them all (formats in
[`references/help.md`](./references/help.md#scope-questions)):

1. **Range**, when no argument and the branch gives no obvious one.
2. **Goal**: *understand* (Timeline/Chapters) or *review* (Walkthrough). Skip when the
   argument settles it: PR mode and feature branches mean review.
3. **Depth**, only above ~40 PRs: every PR, or the notable ones with the rest folded.

Over 300 commits, propose a narrower range before collecting.

### 2. Research (deep, before writing anything)

Follow [`references/research.md`](./references/research.md). In short:

```bash
python3 ~/.claude/skills/change-timeline/scripts/collect.py --range BASE..HEAD > raw.json
```

(or `--since`/`--until`, `--path`). It returns full SHAs, dates, subjects, bodies, per-file
numstat, PR numbers attributed by squash subject, merge subject and merge ancestry, tags,
and suggested areas. Then, for **every PR** in `raw.json`: title, body, labels, reviews,
review comments and linked issues, via `gh pr view N --json …` or the GitHub connector
(`pull_request_read` get / get_reviews / get_review_comments, `issue_read`). Read the diff
(`git show --stat`, then the hunks) wherever the PR text does not explain the change. More
than ~15 PRs: fan out read-only subagents, each returning `{pr, why_quote, risks, issues}`.

### 3. Synthesize

Rules and examples: [`references/research.md`](./references/research.md#grouping). The
shape:

- **One item = one logical change**, usually one PR. Fold fixups and review-response
  commits into their parent. Split a PR into several items only for a walkthrough, where
  each step must be reviewable on its own.
- **Title**: the outcome, ≤70 characters, present tense ("Session tokens move to httpOnly
  cookies"), never "Update auth.ts" or "Various fixes".
- **What**: 1–2 plain sentences a teammate who missed the PR would follow.
- **Why**: rule 2. **Evidence**: the 1–3 shortest quotes that prove the why or a risk, each
  with its source and link.
- **Type** from the conventional prefix if present, else from the diff. **Area** from paths
  (rename `suggested_areas` to words people use; 3–7 lanes). **Chapter** from tags in
  range, else 2–4 phases you can name from the history.
- **Review** (walkthrough, or any risky item): `risk` in one line, and `check`: concrete
  things to verify, drawn from the diff and reviews, not generic advice.

### 4. Confirm the plan and the UI (never skipped)

**a. Plan.** Show the outline in chat, compact: one line per item, `type · title · SHAs ·
#PRs`, then the view and style that will be used. Ask once, via `AskUserQuestion` (format
in [`references/help.md`](./references/help.md#confirm)): **Render** / **Change grouping** /
**Change layout** / **Change style**. Apply changes and re-show only what changed.

**b. Style preview**, when `preferences.md` has no approved `style`, or the user picked
*Change style*. Render the real page with **3 representative items**, publish it as a
preview, and ask: **Looks right** / **Accent** / **Density** / **Light or dark first**.
Offer at most three accents from DESIGN.md §3. Save the approved `style` to preferences the
moment it is approved, then build the full page. Mention once that `style` re-opens this.

### 5. Write and validate

Write `timeline.json` to the schema in [`references/schema.md`](./references/schema.md),
with `theme` from the approved style and `view` from step 4.

```bash
python3 ~/.claude/skills/change-timeline/scripts/validate_timeline.py timeline.json --repo "$(git rev-parse --show-toplevel)"
```

It names each error and its fix: missing SHAs, SHAs that don't exist, an unbacked why,
non-https links, unknown areas or chapters. **Fix and re-run until it prints OK.** Treat
warnings as review notes; fix the ones about abbreviated SHAs and missing reasons.

### 6. Render

```bash
python3 ~/.claude/skills/change-timeline/scripts/render_page.py timeline.json timeline.html
```

With the Artifact tool available, publish `timeline.html` as an artifact (icon: `timeline`)
and re-publish **the same file path** for every revision, so the link stays the same.
Otherwise share the HTML file. The page is self-contained, follows dark and light, works at
phone width, and has **Copy as Markdown** per item and for the whole timeline, so a review
can continue in the conversation.

### 7. Close and learn

Two lines: the shape of the range in one sentence (the busiest area, the one change worth
reading first), then the offer: *switch layout · drill into an item · review it here*. On
"drill into X": read that item's full diff and reviews, and answer in chat.

Write `preferences.md` after the first successful run. Under `## Learned`, after 3
consistent signals only: the layout they switch to, a default range, areas they always
rename, an accent they keep. Mention a promotion once.

## Principles

- **Evidence first.** A timeline is only as good as its links; one wrong SHA costs the
  whole page its trust.
- **Research before drafting.** Read the PRs and reviews before naming a single item.
  Titles written from subjects alone read like `git log` with nicer fonts.
- **Ask once, with defaults.** The user's time goes to reviewing the page, not answering a
  questionnaire.
- **Confirm the UI, every run.** It is the user's page in the user's style.
- **Graceful degradation.** No `gh` and no connector → git only, say so once, and mark
  every why that can't be checked. No artifacts → an HTML file.
- **Never write to the repository.** Read-only, always.
