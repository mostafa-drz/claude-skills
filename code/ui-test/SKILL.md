---
name: ui-test
description: >-
  Runs UI tests described in plain English by driving real Chrome via the
  Claude-in-Chrome extension. Covers end-to-end flows (clicks, forms,
  assertions), visual checks (screenshot + optional baseline diff),
  accessibility (axe-core), performance (Web Vitals + light Lighthouse-style
  metrics), and an interactive --debug mode that tails console + network and
  surfaces issues without needing explicit assertions. Accepts inline
  descriptions or test files in `./tests/ui/*.md`. Per-run folders contain
  artifacts (screenshots, console, network, axe report, perf metrics) plus a
  single-file 2026-aesthetic HTML report with a verdict-forward layout. Learns
  from per-run feedback — false-positive categories, screenshot strategy,
  severity floors, and per-project baselines personalize future runs. Use when
  the user wants to verify a UI flow, screenshot a regression, audit
  accessibility, profile a page, or debug something visibly broken in a real
  browser session.
argument-hint: "<description> | --file <path> | --suite <glob> | --debug <url|description> | record <name> [--env <url>] [--viewport WxH] [--only e2e,visual,a11y,perf] [--baseline] [--verbose]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(mkdir *)
  - Bash(ls *)
  - Bash(open *)
  - Bash(date *)
  - Bash(pwd)
  - Bash(echo *)
  - Bash(curl *)
  - Bash(git *)
  - Bash(file *)
  - Bash(test *)
  - WebFetch
  - mcp__claude-in-chrome__tabs_context_mcp
  - mcp__claude-in-chrome__tabs_create_mcp
  - mcp__claude-in-chrome__tabs_close_mcp
  - mcp__claude-in-chrome__navigate
  - mcp__claude-in-chrome__get_page_text
  - mcp__claude-in-chrome__read_page
  - mcp__claude-in-chrome__javascript_tool
  - mcp__claude-in-chrome__find
  - mcp__claude-in-chrome__resize_window
  - mcp__claude-in-chrome__form_input
  - mcp__claude-in-chrome__read_console_messages
  - mcp__claude-in-chrome__read_network_requests
  - mcp__claude-in-chrome__browser_batch
  - mcp__claude-in-chrome__gif_creator
---

## Preferences

_On startup, use Read to load `~/.claude/skills/ui-test/preferences.md`. If missing, treat as first-run (see First-time detection)._

Defaults when no preferences exist:
- `output-root`: `./test-results/ui-test/` (cwd-relative when in a project; falls back to `~/.claude/skills/ui-test/runs/` outside a project)
- `viewport`: `1440x900` (single) — accepts a comma list for matrix runs (e.g. `375x812,1440x900`)
- `categories`: `e2e,visual,a11y,perf` (debug is a separate mode, not a category)
- `screenshot-strategy`: `per-step` (per-step / on-fail / never)
- `a11y-severity-floor`: `serious` (minor / moderate / serious / critical — anything at-or-above is a failure)
- `perf-budget`: `lcp<=2500,cls<=0.1,inp<=200,js-heap<=50mb` — overridable per-run via `--perf-budget`
- `verbosity`: `verbose-on-failure` (concise / detailed / verbose-on-failure)
- `spec-priority`: `inline-first` (inline-first / project-first / both)
- `auto-baseline`: `true` (record on first run, diff thereafter)
- `auto-open-report`: `true`
- `confirm-plan`: `always` (always / only-multi-step / never)

_Also load `~/.claude/skills/ui-test/feedback-journal.md` if present — surface the one-line `Signal:` from the latest 5 sessions to bias defaults (false-positive categories get pre-deselected, baselines flagged-as-flaky get re-recorded, etc.)._

## Context

_On startup, use Bash to detect: today's date (`date +%Y-%m-%d-%H%M`), the current working directory (`pwd`), whether `./tests/ui/` exists, whether the user is inside a git repo (`git rev-parse --is-inside-work-tree` — silently fail if not), and whether the configured `output-root` exists. Do NOT call any browser tool yet — preflight runs in Step 1._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help, stop
- **`config`** → run config flow, stop
- **`reset`** → delete `preferences.md` + `feedback-journal.md` + `sessions/` + `resume-state.md`, confirm, stop
- **`feedback`** → collect ratings on the most recent run (see Feedback section), stop
- **`history`** → list recent run folders with title, verdict, timestamp, stop
- **`setup`** → walk through Claude-in-Chrome extension setup (see Setup section), stop
- **`record <name>`** → take the most recent inline run and persist it as `./tests/ui/<name>.md`, stop
- **`--debug <url|description>`** → enter interactive debug mode (see Debug section), stop
- **`--file <path>`** → load a single project test file and run it
- **`--suite <glob>`** → resolve the glob under `./tests/ui/`, run each match in order
- **anything else** → treat `$ARGUMENTS` as an inline description, run it (Step 1 onward)

## Help

```
ui-test — Drive real Chrome through plain-English UI tests

Usage:
  /ui-test "<description>"                Inline test, parsed and run
  /ui-test --file <path>                  Run a single ./tests/ui/*.md file
  /ui-test --suite "<glob>"               Run a glob of project tests
  /ui-test --debug "<url|description>"    Interactive debug session
  /ui-test record <name>                  Save the last inline run as a project file
  /ui-test history                        List recent runs (verdict + timestamp)
  /ui-test feedback                       Rate the last run (teaches the skill)
  /ui-test setup                          Walk through Chrome extension setup
  /ui-test config                         Set preferences
  /ui-test reset                          Clear preferences + journal + sessions
  /ui-test help                           This help

Per-run flags:
  --env <url> --viewport <WxH[,WxH]> --only <csv> --skip <csv>
  --baseline (force-record)  --perf-budget "lcp<=2000,cls<=0.05"
  --a11y-floor <minor|moderate|serious|critical>
  --headful-pause (pause for keypress before each navigation)
  --record-gif  --verbose
  --html-report (default on) | --no-html-report (skip the HTML report; print CLI only)
  --open-report | --no-open-report  (override auto-open-report preference)

Examples:
  /ui-test "log in as demo@x.com on staging, expect Dashboard"
  /ui-test "homepage <2s load + passes a11y" --env https://acme.com --only perf,a11y
  /ui-test --suite "checkout/*.md" --viewport 375x812,1440x900
  /ui-test --debug "sidebar disappears on resize at /dashboard"
  /ui-test --file tests/ui/login.md --baseline

Output: {output-root}/{YYYY-MM-DD-HHMM}-{kebab-slug}/ contains
  report.html, data.json, spec.md, steps/, a11y/, perf/, visual/, sources.md.

Current preferences:
  (loaded from preferences.md)
```

## Config

Use AskUserQuestion to collect, in batches of ≤4 per call:

**Batch 1 — Output & viewport**
1. Output root path (default `./test-results/ui-test/`)
2. Default viewport(s) — comma-separated list
3. Auto-open report on completion (true/false)

**Batch 2 — Categories & strictness**
4. Default categories enabled (e2e / visual / a11y / perf — multiSelect)
5. Screenshot strategy (per-step / on-fail / never)
6. a11y severity floor (minor / moderate / serious / critical)
7. Perf budget (free text — `lcp<=2500,cls<=0.1,inp<=200`)

**Batch 3 — Workflow**
8. Spec priority (inline-first / project-first / both)
9. Confirm plan before run (always / only-multi-step / never)
10. Auto-record baseline on first visual run (true/false)

Save to `~/.claude/skills/ui-test/preferences.md`:

```markdown
# /ui-test preferences
Updated: {date}

## Defaults
- output-root: {path}
- viewport: {WxH[,WxH]}
- categories: {csv}
- screenshot-strategy: {per-step|on-fail|never}
- a11y-severity-floor: {minor|moderate|serious|critical}
- perf-budget: {lcp<=...,cls<=...,inp<=...}
- verbosity: {concise|detailed|verbose-on-failure}
- spec-priority: {inline-first|project-first|both}
- auto-baseline: {true|false}
- auto-open-report: {true|false}
- confirm-plan: {always|only-multi-step|never}

## Profile (optional — edit freely)
- Default base URLs by env: staging=, prod=, local=http://localhost:3000
- Standing exclusions (selectors / pages to ignore for visual diff):
- Standing a11y rule overrides (e.g., color-contrast: skip on /admin):
- Trusted slow third-parties (perf budget exclusions):

## Learned
<!-- Auto-appended from feedback over time -->
```

Confirm: "Saved. I'll use this as the baseline — and I'll keep sharpening as you rate runs."

## Reset

Delete `preferences.md`, `feedback-journal.md`, `sessions/`, `resume-state.md` (each via `Bash(test -f ... && rm)` style — graceful on missing). Confirm: "All cleared. Starting fresh on the next run."

## First-time detection

If no preferences file exists, show one warm non-blocking line:

> First time running `/ui-test` — describe a test in plain English, I drive real Chrome via the Claude-in-Chrome extension and produce a per-run folder + single-file HTML report. Run `/ui-test setup` if the extension isn't connected yet, or `/ui-test config` to set defaults — otherwise continue and I'll auto-check the connection.

Then proceed to Step 1 (preflight). After the first successful run, inline-prompt for 1-2 quick prefs (categories, screenshot strategy) — don't force the full config flow.

## Setup — Chrome extension onboarding

When invoked as `/ui-test setup` (or when Step 1 preflight fails and the user asks for help), load `~/.claude/skills/ui-test/reference/setup.md` via Read and walk through it: prerequisites checklist (browser / plan / Claude Code version / extension version), enable steps (`/chrome`, `/mcp`), and a troubleshooting table. Reference: `https://code.claude.com/docs/en/chrome` — fetch via WebFetch if a detail in the local guide looks stale.

After the user says they're set up, run preflight (Step 1). On pass: "Connection good. Paste a test description: `/ui-test \"<description>\"`."

## Workflow

### Step 0 — Load learning context

Read `~/.claude/skills/ui-test/preferences.md` and `~/.claude/skills/ui-test/feedback-journal.md`. Continue silently if either is missing. Extract the latest 5 `Signal:` lines and apply them as biases (e.g., "user keeps flagging color-contrast as false positive on /admin → pre-deselect that rule for this run").

### Step 1 — Preflight (Chrome extension check)

1. Call `tabs_context_mcp`.
2. **Pass** → continue silently to Step 2.
3. **Fail** (any error) → do NOT retry blindly. Stop and show:

```
Hmm — the Claude-in-Chrome extension isn't responding.

Common causes:
  • Extension not installed → https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn
  • Chrome integration not enabled → run  /chrome  → "Enable"
  • Extension idle → run  /chrome  → "Reconnect extension"
  • First time ever → restart Chrome once after enabling, then retry

Need the full walkthrough?  Run:  /ui-test setup
```

**One retry allowed**: if the user replies "retry", call `tabs_context_mcp` once more. If still failing, route to `/ui-test setup`.

### Step 2 — Resolve the spec

Decide what to run from `$ARGUMENTS`, honoring `spec-priority`:

- **Inline string** → parse it as the spec (Step 3).
- **`--file <path>`** → load that file, parse its frontmatter (env, viewport, categories) + body.
- **`--suite "<glob>"`** → resolve under `./tests/ui/`, queue each, run sequentially.
- **No argument** → if `./tests/ui/` exists and `spec-priority` is `project-first` or `both`, list project files via Glob and offer them via `AskUserQuestion`. Otherwise prompt: "Describe the test in one or two sentences."

Also extract per-run flags: `--env`, `--viewport`, `--only`, `--skip`, `--baseline`, `--perf-budget`, `--a11y-floor`, `--headful-pause`, `--record-gif`, `--verbose`.

### Step 3 — Build the run plan

Convert the spec into a structured plan:

```
{
  title: kebab-slug,
  base_url: env || inferred,
  viewports: [{w, h}, ...],
  categories: filtered by --only/--skip and preference defaults,
  steps: [
    { id, kind: "navigate" | "click" | "fill" | "expect" | "wait" | "screenshot",
      target: selector | text | role,
      value: string | regex,
      timeout_ms: 5000,
      assertions: [{ type: "text" | "visible" | "url" | "console-clean" | "network-2xx", ... }] }
  ],
  perf_budget: parsed,
  a11y_floor: level,
  screenshot_strategy: from prefs unless overridden,
}
```

Write it to `spec.md` inside the run folder once Step 5 has created it. The plan is the source of truth — every later step references step IDs.

### Step 4 — Confirm the plan

Honor `confirm-plan` preference:

- `always` → always show
- `only-multi-step` → skip if plan has 1 step + 0 assertions
- `never` → only echo a one-liner: "Running: {title} ({N} steps, {categories})"

Format:

```
ui-test plan — {title}
Base URL:   {url}
Viewport:   {WxH[, WxH...]}
Categories: e2e ✓  visual ✓  a11y ✓  perf ✓

Steps:
  1. navigate → /login
  2. fill #email = demo@x.com
  3. fill #password = ••••
  4. click button[type=submit]
  5. expect h1 contains "Dashboard"
  6. screenshot full-page
  ...

Estimated: {N} browser ops, {M} screenshots, ~{seconds}s

  [Run]   [Tweak]   [Skip]
```

`AskUserQuestion`: "Run this plan?" — pre-select `Run` if `Learned` rules don't contradict.

### Step 5 — Create the run folder

Slug: `{YYYY-MM-DD-HHMM}-{kebab-title-max-60-chars}`. Title summarizes the *outcome being verified*, not the URL: `2026-05-08-1430-login-flow-staging`, `2026-05-08-1430-checkout-a11y-mobile`.

```
mkdir -p {output-root}/{slug}/{steps,a11y,perf,visual}
```

**Isolation rule**: only the per-run folder is created/written. Never touch sibling folders. Baselines live at `{output-root}/baselines/{title}/{viewport}/{step}.png` so they're shared across runs of the same test.

### Step 6 — Execute

For each viewport (matrix outer loop), for each step:

1. **Tabs**: call `tabs_context_mcp` once at the start of the run; create a fresh tab via `tabs_create_mcp`. Resize via `resize_window` to the current viewport. Never reuse tab IDs from a prior session.
2. **Navigate**: `mcp__claude-in-chrome__navigate` with the resolved URL.
3. **Action**:
   - `click` / `fill` → prefer `find` to locate by role/text first, then `javascript_tool` for the actual interaction (more deterministic than relying on visual coordinates).
   - `fill` on real form fields → `form_input` is fine for simple cases.
   - `wait` → `javascript_tool` polling with timeout.
4. **Assertion**: `javascript_tool` returns a JSON `{ pass: bool, actual, expected, evidence }`. Auto-assertions every step:
   - `read_console_messages` since last step → fail on `error` level unless allowlisted in `Profile`.
   - `read_network_requests` since last step → fail on 5xx, optionally 4xx based on prefs.
5. **Screenshot** (per `screenshot-strategy`): use `javascript_tool` to call `html2canvas` (load via CDN if missing, single attempt; fall back to logging the gap) and write the PNG to `steps/{NN}-{stepId}.png`. If a step fails, screenshot regardless of strategy.
6. **Per-step JSON**: append to `data.json` — `{ id, status, duration_ms, screenshot, console, network, assertions }`.
7. **Stop conditions**: a hard-fail step (e.g., navigation failure) halts subsequent steps for that viewport and marks them `skipped`. Other viewports continue.

**Browser dialog rule** (from MCP server instructions): if any step would trigger an alert/confirm/prompt, refuse to run it and mark the step `blocked` with a clear note. Never click elements that may surface a modal — the extension becomes unresponsive.

**Batching**: when many similar reads are needed in a row (selectors, text), prefer `browser_batch` over a serial loop.

**Optional GIF**: if `--record-gif`, wrap the run with `gif_creator` start/stop calls and save to `run.gif`.

### Step 7 — Per-category extras

After the main step loop, run category-specific passes:

- **a11y** — inject axe-core via `javascript_tool`:
  ```js
  const s = document.createElement('script');
  s.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.0/axe.min.js';
  document.head.appendChild(s);
  ```
  Wait for `window.axe`, run `axe.run()`, write `a11y/violations.json`. Filter by `a11y-severity-floor`. If CDN load fails, log the gap and skip — don't fake-pass.

- **perf** — `javascript_tool` reading `performance.getEntriesByType('navigation')`, `PerformanceObserver` for LCP/CLS/INP, `performance.memory` for JS heap. Combine with `read_network_requests` for waterfall. Write `perf/metrics.json`. Compare against `perf_budget`; mark each metric pass/fail.

- **visual** — for each `screenshot` step: if `auto-baseline=true` and no baseline exists, save as baseline; else compute pixel diff (use `javascript_tool` with a tiny inline diff implementation, or skip diff and just save the new snapshot if diff lib unavailable). Write `visual/{step}.png` + `visual/{step}.diff.png`. Threshold from prefs (default 0.1% pixel delta).

Each category degrades gracefully — a CDN block, a browser quirk, or a missing API does NOT fail the run. It logs the gap in `sources.md` and shows up in the report's "Coverage gaps" panel so the verdict is honest about what was actually checked.

### Step 8 — Verdict and report

Compose verdict per run:

- All steps pass + all categories pass → `PASS — {title}`
- Any e2e step fail → `FAIL — {first-failing-step-summary}`
- Only category fails (a11y/visual/perf) → `PASS WITH ISSUES — {N} categories below bar`
- Coverage gaps prevented a verdict → `INCONCLUSIVE — {gap reason}`

Generate `report.html` (skip if `--no-html-report`). Single self-contained file: inline JS ≤200 lines, no external scripts, CSS variables only, dark + light via `prefers-color-scheme`, mobile-responsive, **bento-grid layout** (12-col grid with mixed-size cards) reflecting current 2026 dashboard trends. Verdict-forward: hero card with verdict pill + screenshot, perf bento row (4 metric cards with conic-gradient rings + sparklines), step timeline with filter chips, a11y panel with severity badges, visual diff strip, coverage panel, footer.

**Skeleton source** — copy the structure and styles from `~/.claude/skills/ui-test/examples/sample-report.html` (a fully-rendered reference with mock data). Replace its hardcoded data with the run's actual values. Load `~/.claude/skills/ui-test/reference/report.md` for the full layout spec and inline-JS responsibilities if more detail is needed.

### Step 9 — CLI summary

Print to terminal (verbosity-aware):

```
ui-test — {title}

  {VERDICT}   {one-line summary}

  Steps:    {pass}/{total} passed  ({fail} failed, {skip} skipped)
  a11y:     {N} violations ≥ {floor}        ({pass|fail})
  perf:     LCP {ms}ms · CLS {n} · INP {ms}ms   ({pass|fail})
  visual:   {changed}/{total} snapshots over threshold

Folder:   {output-root}/{slug}/
Report:   {output-root}/{slug}/report.html

  [Open report]    [/ui-test feedback]    [/ui-test record <name>]
```

If `auto-open-report=true`, run `open {report.html}`.

### Step 10 — Save session log + invite feedback

Append a one-page session log to `~/.claude/skills/ui-test/sessions/{slug}.md`:

```markdown
# {slug}
Date: {timestamp}
Spec: {one-line summary or path}
Verdict: {label}
Failures: {short list}
Categories run: {csv}
Coverage gaps: {csv if any}
```

End with one soft line:

> Run `/ui-test feedback` — even one rating sharpens future runs (esp. flagging false-positive a11y rules or flaky baselines).

## Feedback & learning

When invoked as `/ui-test feedback`:

1. Find the most recent file in `sessions/`. If none, say `No recent run found.` and stop.
2. Print a one-line summary of that session.
3. Ask via `AskUserQuestion` (3-4 questions, one batch — pre-select using `Learned`):
   - **Was the verdict right?** (correct / false-positive / false-negative / inconclusive — needed more)
   - **Which category misfired (if any)?** (none / e2e / visual / a11y / perf — multiSelect)
   - **Screenshot strategy felt:** (just right / too many / too few)
   - **Anything to flag for next time?** (free text — flaky selector, baseline regen, perf-budget tweak, env-specific override)
4. Append to `~/.claude/skills/ui-test/feedback-journal.md`:

```markdown
## {slug} — {date}
- Verdict: {label}
- Correctness: {answer}
- Misfiring categories: {csv}
- Screenshot strategy: {answer}
- Notes: {free text}
- Signal: {one-line generalization, e.g., "color-contrast on /admin keeps false-positive — exempt rule"}
```

5. **Promotion rule** — if 3+ sessions show the same `Signal:` (substring match on the key phrase), promote it to `## Learned` in `preferences.md` and mention once: "Noticed {pattern} across recent runs — saving as a standing default."
6. **Drift correction** — if 2 newer sessions contradict a Learned rule, demote it (move to journal with a `Demoted: <reason>` line). Never leave stale rules in Learned.

The journal is human-editable — respect anything the user writes there directly.

## Debug mode (`--debug`)

Invoked as `/ui-test --debug "<url-or-description>"`. Skips the assertion-driven flow; instead, runs an investigative session:

1. Preflight (same as Step 1). If the input is a description without URL, infer or ask once for the URL.
2. Open a fresh tab at the URL. Resize to the configured viewport.
3. Capture a baseline of: full-page screenshot, console (last 100 messages), network (all requests since navigation), DOM stats (node count, deep nesting, common a11y issues spot-check).
4. Loop: ask the user **one** AskUserQuestion at a time — `[Reproduce now]` (waits for the user to act in the browser, then re-snapshots), `[Resize {viewport}]`, `[Run a11y]`, `[Run perf]`, `[Inspect selector]`, `[Tail console for 5s]`, `[Done — write report]`.
5. Each iteration writes deltas to `debug/iter-NN.{png,console.json,network.json}`.
6. On `[Done]`, generate `report.html` (same template, "Debug" verdict variant — focuses on findings, not pass/fail) and a `findings.md` with prioritized issues (Critical / Medium / Low).
7. End with: "Want to convert this into a regression test? Run `/ui-test record <name>`."

Debug mode never asserts and never fails — it surfaces.

## Record mode (`record <name>`)

Invoked as `/ui-test record <name>`:

1. Locate the most recent inline run (or debug session). If none, say so and stop.
2. Generate `./tests/ui/<name>.md` (creating the directory if missing) with:

```markdown
---
title: <Human Title>
env: {base url}
viewport: 1440x900
categories: e2e,a11y
---

# <Human Title>

> Recorded from run {slug} on {date}.

## Steps

1. Navigate to /login
2. Fill #email = demo@x.com
3. ...

## Assertions

- Page contains heading "Dashboard"
- No console errors
- All network requests 2xx-3xx
```

3. Confirm path. Suggest: "Run with `/ui-test --file tests/ui/<name>.md` or include in a suite."

## Filename / folder rules

- Run folder: `{YYYY-MM-DD-HHMM}-{kebab-title}` — title ≤ 60 chars, summarizes the *verification*, not just the URL
- Step file: `{NN}-{kebab-step}.png` — NN zero-padded order
- Baseline: `{output-root}/baselines/{title}/{viewport}/{step}.png` — shared across runs of the same test
- Project test: `./tests/ui/<kebab-name>.md` — never `.test.md` suffix
- Never append `-2`, `-3` for collisions; differentiate by viewport or env

## Principles

1. **Plain English in, structured plan out** — every run materializes a `spec.md` so the user can see exactly what was parsed before anything moves.
2. **Real Chrome, explicit tabs** — always `tabs_context_mcp` first; always create a new tab; never reuse a tab ID from a prior session.
3. **Honest about gaps** — if axe-core's CDN was blocked or a screenshot library failed, the report says so. No fake passes.
4. **Verdict-forward report** — the HTML hero is the verdict, not the data grid.
5. **Per-run isolation** — only the run folder is mutated; baselines live in their own shared folder. Never delete sibling runs.
6. **Stop on dialogs** — refuse to interact with elements that surface alert/confirm/prompt; mark the step blocked rather than freezing the extension.
7. **Graceful degradation** — missing preferences, missing journal, blocked CDN, missing baseline all degrade with a logged gap, not a failure.
8. **Destructive actions need confirmation** — `reset` and `--baseline` (overwrites baselines) print what they'll touch and require a yes.
9. **Learn quietly** — promote a rule to Learned only after 3+ matching signals; demote on 2 contradictions; mention promotions and demotions once.
10. **Stop means stop** — when the user halts mid-run, save `resume-state.md` with the next step ID and invite `/ui-test resume` (future enhancement; not yet a subcommand).
11. **Skill orchestrates, doesn't re-judge** — preserve the user's spec verbatim in `spec.md`; never silently rewrite assertions.
