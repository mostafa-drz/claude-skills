---
name: triage-board
description: >-
  Generates a structured triage artifact from the current conversation's
  findings — a self-contained Desktop folder with a JSON Schema, schema-conformant
  report.json, prose markdown, and a single-file HTML viewer. Viewer ships with
  MD / CSV / JSON download buttons in the header and a per-finding "Copy as
  Markdown" action that produces a GitHub/Linear/Notion-ready ticket block.
  Stateless — triage state lives in the user's ticket system, not in the viewer.
  Use after a beginner-mind audit, QA exploration, code review, or any session
  where the user accumulated discrete findings worth handing off. Triggers:
  "generate test report", "create triage doc", "extract findings", "export this
  audit", "make a viewer", "save findings for review".
argument-hint: [--topic <slug>] [--findings <path>]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Bash
---

# Triage Board

Turn an exploration session into a triage artifact: a `~/Desktop/triage-boards/<topic>-<YYYY-MM-DD>/` folder containing the **same data** in three forms — prose `report.md` for skimming, structured `report.json` for tools, and a self-contained `viewer.html` for the user (or a developer) to triage interactively in their browser. Tracking state (status, comments, tickets, screenshots) lives in **localStorage** keyed by report+date, so reviewers can each have their own annotations without a backend.

## Preferences

_On startup, use the `Read` tool to load `~/.claude/skills/triage-board/preferences.md`. If missing, use sensible defaults._

## Context

_On startup, use Bash to verify_ `~/Desktop/triage-boards/schema/triage-board.schema.json` _exists. If missing, copy from_ `~/.claude/skills/triage-board/templates/schema.json` _on first run._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help, then stop
- **`config`** → interactive setup via `AskUserQuestion`, then stop
- **`reset`** → delete `~/.claude/skills/triage-board/preferences.md`, confirm, stop
- **`--topic <slug>`** → use as the topic slug (skip Q1)
- **`--findings <path>`** → read findings JSON from path (skip Q2/Q3 — assume pre-built)
- **anything else (including empty)** → run the skill

### Help

```
triage-board — Generate a structured triage artifact from session findings

Usage:
  /triage-board                       Build a new report from current conversation
  /triage-board --topic <slug>        Use a specific topic slug (skips topic prompt)
  /triage-board --findings <path>     Use a pre-built findings JSON file
  /triage-board config                Set preferences
  /triage-board reset                 Clear preferences
  /triage-board help                  This help

Output (always at ~/Desktop/triage-boards/<topic>-<YYYY-MM-DD>/):
  report.md      — Prose mirror for skimming / sharing
  report.json    — Schema-conformant structured findings
  viewer.html    — Single-file interactive triage UI (works from file://)

Examples:
  /triage-board                       After a beginner-mind PMI audit
  /triage-board --topic pmi-bulk-flows
```

## First-time experience

If `preferences.md` is missing, show once: `First time using /triage-board? Run /triage-board config to set defaults, or continue with sensible defaults.` Then proceed.

---

## Workflow

### Step 1 — Confirm topic + scope

If `--topic` was passed, use it. Otherwise ask the user via `AskUserQuestion`:

1. **Topic slug** — kebab-case identifier for the folder (e.g. `pmi-beginner-mind`, `auth-flow-audit`). Suggest one based on conversation context; let them edit.
2. **Date** — default today (`date +%Y-%m-%d`); offer to override.

Final folder path: `~/Desktop/triage-boards/<topic>-<YYYY-MM-DD>/`.

### Step 2 — Gather findings

If `--findings <path>` was provided, read that JSON file (must conform to the schema; validate before proceeding).

Otherwise, **mine the current conversation** for discrete findings. Look for:
- Things the user (or you) flagged as bugs, UX gaps, content issues, perf issues, a11y issues
- Things with a clear `where / symptom / impact / repro / triage` shape, even if not all five are present
- Items the user explicitly named (`B1`, `U7`, etc.) — preserve those IDs

For each finding, assemble:
- `id` — `[A-Z]+[0-9]+` (B# bugs, U# ux, C# console/perf/a11y). Stable across re-runs.
- `severity` — one of: critical | high | medium | low | info
- `category` — one of: bug | ux | accessibility | content | performance | console
- `title` — one-line summary
- `where` — file/route/component
- `symptom` — what the tester saw
- `impact` — why it matters to a user
- `repro` — step-by-step
- `triage` — suggested fix direction (not prescriptive)

Also gather optional:
- `positives` — what worked well (array of strings)
- `notes` — side effects of testing (data destroyed, accounts created, etc.)

### Step 3 — Confirm the finding set

Show a compact table (severity + id + title only) and let the user accept / drop items via `AskUserQuestion` with `multiSelect: true`. Default = all selected.

### Step 4 — Write the schema (if missing)

```bash
if [ ! -f ~/Desktop/triage-boards/schema/triage-board.schema.json ]; then
  mkdir -p ~/Desktop/triage-boards/schema
  cp ~/.claude/skills/triage-board/templates/schema.json \
     ~/Desktop/triage-boards/schema/triage-board.schema.json
fi
```

### Step 5 — Write `report.json`

`~/Desktop/triage-boards/<topic>-<YYYY-MM-DD>/report.json`. Must validate against the schema. Include:
- `schemaVersion: "1"`
- `meta` — title / date / tester / surface / branch / scopeIncluded / scopeExcluded
- `findings` — array (accepted in Step 3)
- `positives` — array
- `notes` — array

### Step 6 — Write `report.md`

Prose mirror of the JSON. Use the same severity tiers (Critical / High / Medium / Low / Info). One section per severity, findings in order of ID within the section. Each finding gets a `### <id> — <title>` heading with the same fields formatted as `**Where:** … / **Symptom:** … / **Impact:** … / **Repro:** … / **Triage:** …`.

End with **Things that worked well**, **Notes / side effects**, and a **Severity summary** table.

### Step 7 — Write `viewer.html`

Copy `~/.claude/skills/triage-board/templates/viewer.template.html` and inline the JSON at the marker `/*REPORT_JSON_START*/…/*REPORT_JSON_END*/`. Use Python or sed for the substitution (Python preferred — handles edge cases):

```bash
python3 <<'PYEOF'
import re, json, pathlib
report = pathlib.Path('<dest>/report.json').read_text()
json.loads(report)  # validate
template = pathlib.Path('~/.claude/skills/triage-board/templates/viewer.template.html').expanduser().read_text()
out = re.sub(r'/\*REPORT_JSON_START\*/.*?/\*REPORT_JSON_END\*/',
             '/*REPORT_JSON_START*/' + report.strip() + '/*REPORT_JSON_END*/',
             template, flags=re.DOTALL)
pathlib.Path('<dest>/viewer.html').write_text(out)
PYEOF
```

### Step 8 — Open + report

- `open -a "Google Chrome" <dest>/viewer.html` to launch.
- Print the folder path + summary: count by severity, count of positives/notes.
- Pipe the folder path to `pbcopy` so the user can `cmd+v` it elsewhere.

---

## Viewer features (what's in `templates/viewer.template.html`)

Stateless, single-file HTML with vanilla JS (~25 KB). No localStorage, no tracker, no build step. The findings JSON is the only source of truth; the viewer just renders it.

1. **Header export buttons** — three `↓ MD / ↓ CSV / ↓ JSON` buttons in the top-right of the header. Each generates the artifact from the in-page REPORT object and triggers a download (`report-<date>.md`, `report-<date>.csv`, `report-<date>.json`).
2. **Stats pills** — counts per severity + total.
3. **Filter bar** (sticky) — severity / category / search-by-id-or-title-or-details.
4. **Cards** — severity-tinted left border, ID chip + category chip + title. Click to expand → Where / Symptom / Impact / Repro / Triage.
5. **`Copy as Markdown` per card** — primary action inside each expanded card. Copies the finding as a GitHub/Linear/Notion-ready markdown block to the clipboard:
   ```markdown
   ## [B8] Bulk Delete has NO confirmation modal

   **Severity:** `critical` · **Category:** `bug`

   **Where**

   Bulk-select header on Action Items / Decisions / Questions

   **Symptom**

   Clicking `Delete` in the bulk-action header immediately destroys all selected items…

   **Impact**

   Data loss in one click. Contradicts the pattern PR #977 just shipped…

   **Repro**

   Open any meeting → tick the header select-all checkbox → click Delete…

   **Triage**

   Wire bulk Delete into a confirmation modal using MeetingModalLayout…

   ---
   _From: PMI Beginner-Mind Audit · 2026-05-15 · /w/30/meetings_
   ```
   Button shows `✓ Copied!` briefly after click. Falls back to `document.execCommand("copy")` if the Clipboard API is blocked.
6. **Aesthetic** — gradient header (blue→pink glass, matching the design system), severity-colored chips, system font stack. Minimal.

---

## Schema (at `templates/schema.json`)

JSON Schema draft-07. Key constraints:
- `id` must match `^[A-Z]+[0-9]+$`
- `severity` enum: critical | high | medium | low | info
- `category` enum: bug | ux | accessibility | content | performance | console
- `meta.title`, `meta.date`, `meta.surface` required
- `findings[].id`, `findings[].severity`, `findings[].category`, `findings[].title` required

No tracker state in the schema or viewer — when reviewers want to act on a finding, they click `Copy as Markdown` and paste into their ticket system of choice (Linear, GitHub, Notion, Slack). Triage state lives in the ticket system, not the report.

---

## Principles

1. **Stateless viewer, single-file output** — must work from `file://` with no network, no build, no localStorage. JSON is inlined at write time and is the only source of truth.
2. **Quote the source** — every finding's `symptom` / `repro` should be specific enough that a developer can reproduce without asking. Vague findings are noise.
3. **Triage lives in the user's ticket system, not the viewer** — the viewer's job is to make findings *easy to move out* (one-click `Copy as Markdown`, plus MD/CSV/JSON exports in the header). Status and ownership belong to Linear / GitHub / Notion, not localStorage.
4. **Three formats, one shape** — MD, CSV, JSON all reflect the same findings. The user picks the format for the destination (MD for tickets and Slack, CSV for spreadsheets, JSON for tools).
5. **Pragmatic, not over-engineered** — no tracker, no comments, no screenshots-in-viewer. If the user wants screenshots, attach them to tickets after pasting the Markdown.

---

## Learned

_Auto-managed. The skill silently adds preferences here when the user corrects a default (chose a different topic slug pattern, dropped a section, etc.). Surface once when adding: "Noted: <pattern>. Saved for next time."_
