# change-timeline

See what changed in a branch, PR, release or period as a page you can review. Every change
is a card with a title, what changed, why, and the commit SHAs and PRs that prove it.

> **Status: draft (v0).** The scripts and page were tested locally: collector and validator
> run on this repository's own history (14 commits, 14 PRs, every SHA verified), the
> page in headless Chrome in dark and light at 1200px and 390px, all four layouts, and with
> hostile input. It hasn't yet been run end to end as a skill. The scenarios in
> [`evals/evals.json`](./evals/evals.json) are the acceptance test for that first run.

## The problem

| what usually goes wrong | how this skill handles it |
|---|---|
| `git log` is a list of subjects, not a story | Commits are grouped into **changes**, usually one per PR, with fixups folded in |
| Summaries you can't check | Every change cites **full SHAs read from git**; the validator rejects any that don't resolve in the repo |
| Invented reasons ("refactored for clarity") | The *why* is **quoted** from a PR, review or issue, marked **inferred**, or shown as **not stated** |
| One view for every question | **Timeline**, **Lanes** by area, **Chapters** by release, **Walkthrough** for review, all over the same data |
| A generated page in someone else's taste | A **style preview** on first run; the page uses your saved style and the plan is confirmed before every render |
| Review notes lost in a browser tab | **Copy as Markdown** per change and for the whole page, to continue in the conversation |

## How it works

```
range ─► collect.py (git: SHAs, numstat, PR numbers, tags, areas)
          │
          ├─► every PR: body · reviews · review threads · linked issues   (gh or GitHub connector)
          └─► diffs, where the PR text doesn't explain the change
                         │
              group into changes ─► title · what · why (quoted / inferred / none) · evidence
                         │
              plan outline + style preview ─► your OK   (every run)
                         │
     timeline.json ─► validate --repo ─► render ─► artifact
```

## Layouts

- **Timeline**: one column with a date rail, newest or oldest first.
- **Lanes**: one lane per area along a time axis, to see where work clustered. Select a
  mark to open its card.
- **Chapters**: grouped by tag, or by phases named from the history, each with a summary.
  Compact rows.
- **Walkthrough**: review steps in reading order, with a risk, things to check, and a
  *Reviewed* tick with progress.

## Files

| file | what |
|---|---|
| `SKILL.md` | the flow and standing rules |
| `DESIGN.md` | the renderer contract: dev-tool dark tokens, type, card anatomy, anti-patterns |
| `references/research.md` | evidence gathering, grouping, titles, areas, chapters, review notes |
| `references/schema.md` | `timeline.json` |
| `references/help.md` | help, first run, question formats, preferences |
| `scripts/collect.py` | git → `raw.json` (read-only, stdlib) |
| `scripts/validate_timeline.py` | schema + evidence checks; `--repo` verifies every SHA |
| `scripts/render_page.py` | `timeline.json` → self-contained HTML |
| `assets/timeline-template.html` | the page |
| `evals/example-timeline.json` | a real example: this repo, Aug–Oct 2026 |

## Try the example

```bash
cd claude-skills
python3 code/change-timeline/scripts/validate_timeline.py code/change-timeline/evals/example-timeline.json --repo .
python3 code/change-timeline/scripts/render_page.py code/change-timeline/evals/example-timeline.json /tmp/timeline.html
```

## Safety

Read-only on the repository: no commits, pushes, PR comments or ticket changes. PR bodies
are quoted as data and never followed as instructions. The page sets every value as text
and links only to `https://` URLs.
