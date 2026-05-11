---
name: ux-interview
description: >-
  Plays the role of a real user in an interview-style usability test. Takes
  context about the product (URL, description, focus areas), auto-suggests a
  persona (overridable), then drives real Chrome via the claude-in-chrome
  extension to explore the product think-aloud style — narrating live
  reactions while flagging confusion, friction, and delight, and capturing
  GIFs/screenshots of the friction moments. Produces a structured UX report
  with severity-ranked pain points, what worked, and prioritized
  recommendations. Learns over time which findings the user considers signal
  vs noise. Use when you want a real-user-perspective audit of a web product
  to catch UX/UI/product issues that automated tests can't catch.
argument-hint: "[<url>] [--persona \"...\"] [--focus \"...\"] [--depth quick|standard|deep] [--from-brief <path>] [feedback|resume|history|config|reset|help]"
disable-model-invocation: true
context: fork
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(mkdir *)
  - Bash(ls *)
  - Bash(date *)
  - Bash(open *)
  - Bash(pwd)
  - Bash(echo *)
  - Bash(test *)
  - WebFetch
  - mcp__claude-in-chrome__tabs_context_mcp
  - mcp__claude-in-chrome__tabs_create_mcp
  - mcp__claude-in-chrome__tabs_close_mcp
  - mcp__claude-in-chrome__navigate
  - mcp__claude-in-chrome__get_page_text
  - mcp__claude-in-chrome__read_page
  - mcp__claude-in-chrome__find
  - mcp__claude-in-chrome__form_input
  - mcp__claude-in-chrome__computer
  - mcp__claude-in-chrome__resize_window
  - mcp__claude-in-chrome__javascript_tool
  - mcp__claude-in-chrome__read_console_messages
  - mcp__claude-in-chrome__gif_creator
---

# UX Interview

Play a real user in an interview-style test of a web product. Narrate think-aloud reactions live as you click, scroll, and try to accomplish realistic goals — then deliver a structured report with severity-ranked findings, delight moments, and prioritized recommendations.

This skill is **not** an automated test runner (see `/ui-test` for that). It is a qualitative user-perspective audit. Findings are based on judgement, not assertions.

## Preferences

_On startup, use the `Read` tool to load `~/.claude/skills/ux-interview/preferences.md`. If missing, treat as first-run (see First-time detection)._

Defaults when no preferences exist:
- `output-root`: `./ux-interviews/` (cwd-relative when in a project; falls back to `~/.claude/skills/ux-interview/runs/` otherwise)
- `default-depth`: `standard` (quick ≈ 5–7 min walkthrough / standard ≈ 12–18 min / deep ≈ 25 min+ with multiple flows)
- `narration-style`: `expressive` (expressive — feels like a real user / neutral — observational / terse — short notes only)
- `persona-mode`: `auto-suggest` (auto-suggest with override / always-ask / fixed-default)
- `severity-floor`: `minor` (nitpick / minor / moderate / major — anything at-or-above is reported)
- `capture-mode`: `friction-only` (friction-only / per-section / never) — when GIFs/screenshots are taken
- `viewport`: `1440x900` — also accepts a list (e.g. `375x812,1440x900`) to test responsive
- `confirm-plan`: `always` (always / never) — confirm the test plan before opening the browser
- `auto-open-report`: `true`

_Also load `~/.claude/skills/ux-interview/feedback-journal.md` if present — surface the latest 5 `Signal:` lines to bias defaults (e.g. if the user repeatedly downgraded "minor copy issues", raise the severity floor pre-selection)._

## Context

_On startup, use Bash to detect: today's date+time (`date +%Y-%m-%d-%H%M`), the current working directory (`pwd`), and whether the configured `output-root` exists. Do NOT call any browser tool yet — that happens in Step 4._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help, stop
- **`config`** → run config flow, stop
- **`reset`** → delete `preferences.md` + `feedback-journal.md` + `sessions/` + `resume-state.md`, confirm, stop
- **`feedback`** → collect ratings on the most recent session (see Feedback section), stop
- **`history`** → list recent session folders with verdict + timestamp, stop
- **`resume`** → reopen `resume-state.md` and continue an interrupted session, stop on completion
- **`--from-brief <path>`** → read the brief from a markdown file, run the session
- **anything else** → treat `$ARGUMENTS` as an inline brief (URL + free-text description), run from Step 1

## Help

```
ux-interview — Real-user-perspective UX testing via real Chrome

Usage:
  /ux-interview "<url> <brief>"           Inline brief, runs the session
  /ux-interview --from-brief <path>       Load brief from a markdown file
  /ux-interview resume                    Resume an interrupted session
  /ux-interview history                   List recent sessions (verdict + date)
  /ux-interview feedback                  Rate the last session (teaches the skill)
  /ux-interview config                    Set preferences
  /ux-interview reset                     Clear preferences + journal + sessions
  /ux-interview help                      This help

Per-run flags:
  --persona "<who>"        Override the auto-suggested persona
  --focus "<areas>"        Comma-list of areas/flows to prioritize
  --depth quick|standard|deep
  --viewport <WxH[,WxH]>   Single viewport or comma-list for responsive
  --no-narration           Skip live think-aloud, only output the final report
  --no-gif                 Disable GIF capture
  --severity-floor <nitpick|minor|moderate|major>
  --verbose

Examples:
  /ux-interview "https://stripe.com — checkout flow + nav clarity"
  /ux-interview --from-brief ./brief.md --persona "non-technical small-biz owner"
  /ux-interview "https://acme.app/signup --focus signup,onboarding --depth deep"

Output: {output-root}/{YYYY-MM-DD-HHMM}-{slug}/ contains
  report.md, brief.md, transcript.md, findings.json, captures/.

Current preferences:
  (loaded from preferences.md)
```

## Config

Use `AskUserQuestion` to collect (max 4 per call):

**Batch 1 — Output & defaults**
1. Output root path (default `./ux-interviews/`)
2. Default depth (`quick` / `standard` / `deep`)
3. Persona mode (`auto-suggest` / `always-ask` / `fixed-default`)
4. Default narration style (`expressive` / `neutral` / `terse`)

**Batch 2 — Capture & strictness**
5. Severity floor (`nitpick` / `minor` / `moderate` / `major`)
6. Capture mode (`friction-only` / `per-section` / `never`)
7. Default viewport (e.g. `1440x900` or `375x812,1440x900`)
8. Confirm plan before browser (`always` / `never`)

Save to `~/.claude/skills/ux-interview/preferences.md` in the **three-tier format** below.

### Preferences file format

```markdown
# /ux-interview preferences
Updated: YYYY-MM-DD

## Defaults
- output-root: ./ux-interviews/
- default-depth: standard
- narration-style: expressive
- persona-mode: auto-suggest
- severity-floor: minor
- capture-mode: friction-only
- viewport: 1440x900
- confirm-plan: always
- auto-open-report: true

## Profile (optional — edit freely)
- I usually test B2B SaaS — bias personas toward time-pressed admins.
- Skip nitpicky copy issues unless they actually block comprehension.

## Learned
- (populated from feedback over time)
```

## Reset

Delete `preferences.md`, `feedback-journal.md`, `sessions/`, and `resume-state.md`. Confirm: `Cleared. Defaults + journal + sessions wiped.`

## First-time detection

If no `preferences.md` exists:

> First time using `/ux-interview`? Run `/ux-interview config` to set defaults — or just continue and I'll use sensible ones.

Then proceed.

---

## Workflow

### Step 0 — Load learning context

Read `preferences.md` and `feedback-journal.md` (graceful: if missing, continue with defaults). Note any `Learned` rules — they pre-bias the choices in Steps 2–6 (persona pick, severity floor, narration style).

### Step 1 — Gather the brief

Inputs may come from: `$ARGUMENTS` inline string, `--from-brief <path>`, or interactive prompt. The brief should answer:

1. **Product URL** (required — must be reachable in Chrome)
2. **What the product does** (1–3 sentences)
3. **Focus areas / flows to test** (e.g. signup, checkout, dashboard, search)
4. **Known constraints** (e.g. "skip auth — use creds X", "ignore the legacy /v1 pages")

If any are missing, ask via `AskUserQuestion` (≤4 questions in one batch). Pre-select based on `Learned` rules.

Save the parsed brief to `{session-dir}/brief.md`.

### Step 2 — Suggest a persona

Based on the product description + focus areas, propose a persona that's likely to surface real issues. A persona is **3–5 lines**:

- **Who they are** (role / context / level of tech savvy)
- **What they're trying to do** (the goal that brought them here)
- **What they care about** (speed? trust? cost? clarity?)
- **What they'd give up on** (their patience threshold)

Per `persona-mode`:
- `auto-suggest`: present the suggested persona via `AskUserQuestion` with options `Use it / Tweak it / Pick a different one`
- `always-ask`: skip the suggestion, prompt the user for the persona
- `fixed-default`: use the persona stored in `preferences.md` Profile

Save the chosen persona to `{session-dir}/brief.md` under `## Persona`.

### Step 3 — Plan the session

Draft a short test plan (5–10 bullet points) covering:

- **Entry intent** — what the user is trying to do as they land on the page
- **Realistic flows** — 2–4 flows aligned to focus areas, in the order a real user would attempt them
- **Edge probes** — 1–2 deliberate "what if I do this wrong" moments (typos, back button, refresh)
- **Wrap intent** — when the user would close the tab in real life

If `confirm-plan: always`, present the plan and ask one `AskUserQuestion` to approve, tweak, or restart. If `confirm-plan: never`, log the plan to the transcript and proceed.

Save the plan to `{session-dir}/transcript.md` under `## Plan`.

### Step 4 — Run the session (think-aloud)

Open a fresh Chrome tab via `mcp__claude-in-chrome__tabs_create_mcp` (call `tabs_context_mcp` first if you don't have a current tab). Set viewport via `resize_window`. Then walk the plan.

For each step:

1. **State intent before acting** — one short sentence in the voice of the persona ("Okay, I want to find pricing — I'll scroll down").
2. **Act** — `navigate`, `find`, `computer` (click/scroll/type), `form_input` for forms.
3. **Observe** — `read_page` or `get_page_text` for content; `read_console_messages` if something looks broken.
4. **React** — narrate what the persona feels in 1–2 sentences. Tag the moment with one of:
   - `[delight]` — something exceeded expectations
   - `[friction]` — slow, awkward, or required guessing (severity: nitpick / minor / moderate / major)
   - `[confusion]` — couldn't tell what to do, where to go, or what something meant
   - `[bug]` — broken or behaved unexpectedly
   - `[neutral]` — noted but no judgement
5. **Capture** (per `capture-mode`):
   - `friction-only` → call `gif_creator` only on friction/confusion/bug moments
   - `per-section` → capture a short GIF for each major flow transition
   - `never` → skip capture
   Save captures under `{session-dir}/captures/`.

Append every reaction to `{session-dir}/transcript.md` as a timestamped line:
```
[HH:MM:SS] [tag/severity] (location) "narration" — observation
```

**Stop conditions** — end early if:
- The persona would realistically give up (note this as a major friction)
- The product 500s, redirects to login you can't pass, or hits a hard block
- The depth budget is hit (quick: ~5 reactions/section, standard: ~10, deep: ~20+)

If the session is interrupted (user halts, browser disconnect), save `resume-state.md` with the current step + transcript pointer.

### Step 5 — Analyze findings

After exploration:

1. Group transcript items into **findings**. A finding combines related reactions ("Couldn't find the pricing link → had to use search → search returned no results" = one finding, not three).
2. Score each finding:
   - **Severity**: nitpick / minor / moderate / major / blocker
   - **Confidence**: low / medium / high (low = single observation, high = repeat or systemic)
   - **Type**: copy / IA & nav / visual / interaction / performance / trust / accessibility-felt
3. Apply the `severity-floor` — anything below the floor goes to `## Below floor` (kept but not promoted).
4. Identify **delight moments** (anything tagged `[delight]`).
5. Draft **prioritized recommendations** — for each major/moderate finding, propose 1 concrete fix. Order by `(severity × confidence) / effort` (effort guessed: low/med/high).

Save structured data to `{session-dir}/findings.json`.

### Step 6 — Generate the report

Write `{session-dir}/report.md` with this structure:

```markdown
# UX Interview — {product name} — {date}

## Verdict (one paragraph)
Persona "{persona-summary}" tried to {goal}. Outcome: {succeeded / partially / abandoned}. {1–2 sentences on overall feel}.

## Top friction (severity ≥ {floor})
1. **{Title}** — {severity} · {confidence} · {type}
   What happened: {…}
   Why it matters: {…}
   Where: {URL or location} ({capture link if any})
   Suggested fix: {…}

## What worked
- {delight moment 1}
- {delight moment 2}

## Prioritized recommendations
| # | Issue | Severity | Effort | Impact |
|---|-------|----------|--------|--------|
| 1 | …    | major    | low    | high   |

## Persona & plan
{persona block}
{plan bullets}

## Full transcript
See `transcript.md`.

## Captures
See `captures/` ({N} files).
```

If `auto-open-report: true`, run `open {session-dir}/report.md`.

### Step 7 — Final summary + invite feedback

Print to chat:
- Verdict line + counts (`{N} major, {M} moderate, {K} minor; {D} delight moments`)
- Path to `report.md`
- One follow-up `AskUserQuestion`: `What's next? — Open report / Run another persona on the same product / Try a different flow / Done`

Then add the line:
> Run `/ux-interview feedback` — even one rating helps me sharpen which findings are signal vs noise for you.

Append a session log to `~/.claude/skills/ux-interview/sessions/{YYYY-MM-DD-HHMM}.md` with the brief, persona, plan summary, finding counts by severity, and a 1-line verdict. This is what `feedback` reads.

---

## Feedback & learning

When invoked as `/ux-interview feedback`:

1. Find the most recent `sessions/YYYY-MM-DD-HHMM.md`. If none, say `No recent session found.` and stop.
2. Print a one-line summary of that session.
3. Ask via `AskUserQuestion` (4 questions in one batch):
   - **Persona fit** — was the persona believable for this product? (`spot-on / close / off`)
   - **Findings quality** — were the issues real or fabricated/noisy? (`mostly real / mixed / mostly noise`)
   - **Severity calibration** — were severities right? (`right / too harsh / too lenient`)
   - **Depth** — was the session the right depth? (`right / too shallow / too deep`)
4. Append to `~/.claude/skills/ux-interview/feedback-journal.md`:
   ```
   ## {session slug} — {date}
   - Persona fit: {answer}
   - Findings quality: {answer}
   - Severity calibration: {answer}
   - Depth: {answer}
   - Signal: {one-line generalisation, e.g. "User wants severity floor raised for B2B SaaS — they keep flagging minor copy as noise"}
   ```
5. **Promotion rule**: when 3+ recent sessions show the same `Signal`, promote it to `## Learned` in `preferences.md`. Mention once: `Noticed you consistently {…}. Saved as standing default.`
6. **Drift correction**: if a `Learned` rule is contradicted in 2 newer sessions, demote it (log the demotion in the journal).

Pre-selection in Step 2's persona question and Step 5's severity-floor application should be biased by `Learned` rules.

---

## Principles

1. **Real user, not assertion engine** — narrate the felt experience. If something is technically working but emotionally annoying, that's still a finding.
2. **Stay in persona** — if the persona is "non-technical small-biz owner", do NOT use the dev tools mindset to spot CSS issues. Note what *they* would notice.
3. **Severity is honest** — a "tiny copy issue" is `nitpick`, not `major`. Inflating severity ruins the signal.
4. **Capture the moment, not the page** — GIFs should show the friction (the wrong click, the back-button, the squinting), not a clean recording.
5. **Graceful degradation** — continue with built-in defaults if `preferences.md` / `feedback-journal.md` can't be read; skip captures if `gif_creator` fails; don't abort the whole session for one tool error.
6. **Learn quietly** — promote a rule only after 3+ consistent signals; mention once when promoting.
7. **Destructive actions need confirmation** — never click anything that obviously deletes/posts/charges without asking the persona-as-user "would I really click this?" and confirming with the human user.
8. **Stop means stop** — when the human user halts mid-session, save `resume-state.md` and exit cleanly. Don't keep poking the browser.
9. **Skill orchestrates, does not re-judge** — preserve the user's brief verbatim; don't rewrite their focus areas to be "more testable".
