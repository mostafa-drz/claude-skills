---
name: emotional-recap
description: >-
  Reviews the user's past Claude Code conversations from a wellbeing
  perspective — sentiment, tone, emotional arc, recurring patterns — and
  generates a supportive, science-grounded report in both Markdown and HTML.
  Default lookback is 48 hours across all projects. Uses recognised emotion
  frameworks (Plutchik, Ekman, Russell's circumplex, Pennebaker linguistic
  markers) and cites the science behind every observation. Learns the user's
  baseline tone over time so future reports flag genuine shifts, not noise.
  Use when the user asks for an emotional/wellbeing recap, mood check,
  sentiment review, or wants to understand their own ups and downs across
  recent work sessions.
argument-hint: "[--window=48h] [--scope=all|current|<slug>] [--format=both|md|html] [--last=N] [feedback|config|reset|resume|help]"
disable-model-invocation: true
context: fork
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Emotional Recap

Generate a wellbeing-focused review of the user's recent Claude Code conversations. The skill reads conversation transcripts, performs sentiment / tone / emotion analysis using established psychological frameworks, surfaces patterns (time-of-day, project, streaks, vocabulary), and writes a supportive Markdown + HTML report grounded in cited research.

This skill is **supportive, not diagnostic.** It surfaces observations and reframes them with science; it never pathologises, prescribes treatment, or replaces a professional. Wellness is a long game — this is one signal among many.

## Preferences

_On startup, use the `Read` tool to load `~/.claude/skills/emotional-recap/preferences.md`. If missing, treat as "no preferences set" and apply Defaults from this file._

## Design contract

_On startup, use the `Read` tool to load `~/.claude/skills/emotional-recap/DESIGN.md`. This file is the **renderer contract**: aesthetic direction, type system, colour tokens, layout, visualisation principles, anti-patterns, renderer guarantees, component patterns. Apply its tokens and rules to every emitted HTML / SVG / Markdown artefact. Renderer guarantees in DESIGN.md §7 are non-negotiable — they fail closed (refuse to write if violated)._

_When DESIGN.md and `preferences.md` conflict: **DESIGN.md wins for renderer guarantees** (a11y, anti-patterns, token shape); **`preferences.md` wins for user-tunable knobs** (tone, citation depth, framework choice, auto_open, etc.). If `DESIGN.md` is missing, fall back to the inline spec in `reference/report-structure.md` and flag once._

## Context

_On startup, use Bash to detect: current working directory, current project slug (cwd path with `/` → `-`, prefixed with `-`), today's date in `YYYY-MM-DD`. Skip any that fail._

Conversation transcripts live at `~/.claude/projects/<project-slug>/<uuid>.jsonl`. Each line is one event (user message, assistant message, tool result, system reminder). The skill operates on user-authored text only — assistant output, tool outputs, and system reminders are excluded from sentiment analysis (they are not the user's emotional signal).

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display Help block, stop
- **`config`** → interactive setup, stop
- **`reset`** → delete `preferences.md`, `feedback-journal.md`, `sessions/`, `resume-state.md`, `reports/`, confirm, stop
- **`feedback`** → run Feedback subcommand (see `## Feedback & learning`)
- **`resume`** → if `resume-state.md` exists, continue the previous unfinished run
- **`--window=<dur>`** → override lookback (e.g. `24h`, `7d`, `30d`)
- **`--scope=<all|current|slug>`** → override conversation scope
- **`--format=<both|md|html>`** → override report format
- **`--last=N`** → limit to N most recent conversations (after window filter)
- **`--dry-run`** → analyse + print summary only, skip writing report
- **anything else / empty** → run the main workflow

### Help

```
emotional-recap — Wellbeing review of recent Claude Code conversations

Usage:
  /emotional-recap                            Default: all projects, last 48h, both formats
  /emotional-recap --window=7d                Last 7 days
  /emotional-recap --scope=current            Only the current project's conversations
  /emotional-recap --format=html              HTML report only
  /emotional-recap --last=10                  Last 10 conversations (after window filter)
  /emotional-recap --dry-run                  Analyse + print summary, no file written
  /emotional-recap feedback                   Rate the most recent report
  /emotional-recap config                     Set preferences
  /emotional-recap resume                     Continue an interrupted run
  /emotional-recap reset                      Clear preferences + journal + reports
  /emotional-recap help                       This help

Current preferences:
  (loaded from ~/.claude/skills/emotional-recap/preferences.md)
```

### Config

Use `AskUserQuestion` to collect (in two batches of ≤4 questions):

**Batch 1 — Scope & output**
- **Q1** — Default lookback window: `24h` / `48h` / `7d` / `30d`
- **Q2** — Default scope: `all projects` / `current project only` / `ask each time`
- **Q3** — Default format: `both md+html` / `md only` / `html only`
- **Q4** — Report directory: `~/.claude/skills/emotional-recap/reports/` (default) / `~/Desktop/wellness/` / custom path

**Batch 2 — Tone & depth**
- **Q5** — Auto-open HTML in browser after generation: `yes` / `no`
- **Q6** — Tone of voice: `warm & supportive` (default) / `clinical & neutral` / `direct & terse`
- **Q7** — Citation depth: `minimal` (1-line refs) / `standard` (full APA inline, ~5 refs) / `academic` (full reference list, ~10 refs)
- **Q8** — Primary emotion framework: `Plutchik wheel` (8 primary emotions) / `Ekman basic` (6 emotions) / `Russell circumplex` (valence×arousal) / `combined` (use all three contextually)

Write to `~/.claude/skills/emotional-recap/preferences.md` in **three-tier format**:

```markdown
# /emotional-recap preferences
Updated: YYYY-MM-DD

## Defaults
- window: 48h
- scope: all
- format: both
- report_dir: ~/.claude/skills/emotional-recap/reports/
- auto_open: yes
- tone: warm
- citation_depth: standard
- framework: combined

## Profile (optional — edit freely)
- (free-form lines the user can edit to nudge defaults — e.g. "avoid mentioning sleep; I work nights by choice")

## Learned
- (populated from feedback over time)
```

### Reset

Delete in order, with confirmation:
1. `~/.claude/skills/emotional-recap/preferences.md`
2. `~/.claude/skills/emotional-recap/feedback-journal.md`
3. `~/.claude/skills/emotional-recap/sessions/`
4. `~/.claude/skills/emotional-recap/resume-state.md`
5. Ask before deleting `~/.claude/skills/emotional-recap/reports/` — these are user-facing artefacts.

Confirm: `Preferences, journal, sessions, and resume state cleared. Reports kept unless you opted in. Using defaults.`

## First-time detection

If `~/.claude/skills/emotional-recap/preferences.md` does not exist:

> First time using `/emotional-recap`? I'll use sensible defaults (last 48h across all projects, both md+html, warm tone, combined emotion frameworks). Run `/emotional-recap config` anytime to tune. Continuing…

Then proceed.

---

## Workflow

### Step 0 — Load learning context and design contract

1. Read `~/.claude/skills/emotional-recap/preferences.md` → apply Defaults, then Profile overrides, then Learned overrides.
2. **Read `~/.claude/skills/emotional-recap/DESIGN.md`** — the renderer contract. Hold its tokens, anti-patterns, and renderer guarantees in working memory for Step 5. If missing, fall back to `reference/report-structure.md` and flag once.
3. Read `~/.claude/skills/emotional-recap/feedback-journal.md` if present — scan the last ~10 entries for `Signal:` lines and silently apply them as soft biases for this run.
4. If `resume-state.md` exists and `$ARGUMENTS` is not `resume`, mention once: `A previous run was interrupted — run /emotional-recap resume to continue, or ignore to start fresh.` Continue with the new run regardless.

Continue silently on missing files — graceful degradation is mandatory.

### Step 1 — Resolve scope and window

1. Parse flags from `$ARGUMENTS`; fall back to preferences; fall back to Defaults.
2. Compute window cutoff: `now - window` (e.g. now - 48h).
3. Determine projects to scan:
   - `scope=all` → glob `~/.claude/projects/*/`
   - `scope=current` → only the current project slug
   - `scope=<explicit-slug>` → that one directory
4. List JSONL files inside each project directory, filter by `mtime >= cutoff`.
5. If `--last=N`, sort by mtime desc and take top N.
6. **If zero files match** → print a warm note and stop. Example: `No conversations found in the last <window>. Either nothing's happened, or you're not using Claude Code through it — enjoy the quiet.`

Print a one-line confirmation: `Scanning N conversations across M projects from <date> to <date>.`

### Step 2 — Extract user-authored text

For each JSONL file:

1. Read line by line. Each line is JSON.
2. Keep only events where the author is the user (typically `type == "user"` with a `message.content` that is a string or has text parts). **Exclude**:
   - Assistant messages
   - Tool results / tool outputs (e.g. `tool_use_result`, `tool_result`)
   - System reminders and `<command-*>` tag payloads
   - Slash command bodies (lines starting with `<command-name>` blocks) — keep only the natural-language fragments the user typed
   - Empty / whitespace-only messages
3. Capture per message: `timestamp`, `project_slug`, `conversation_id`, `text`.
4. Skip files that fail to parse — log a soft warning but continue.

Aggregate stats: total messages, total tokens (approx word count × 1.3), distinct conversations, distinct projects, span (first → last timestamp).

### Step 3 — Sentiment, emotion, and tone analysis

Apply the user's chosen framework(s) — see `~/.claude/skills/emotional-recap/reference/frameworks.md` for the full reference. Summary:

- **Plutchik (1980)** — 8 primary emotions: joy, trust, fear, surprise, sadness, disgust, anger, anticipation. Tag each meaningful user message with 0-2 primary emotions.
- **Ekman (1992)** — 6 basic emotions: happiness, sadness, fear, anger, surprise, disgust. Useful when Plutchik feels too granular.
- **Russell circumplex (1980)** — every message gets a `valence` (−1 unpleasant → +1 pleasant) and `arousal` (0 calm → 1 activated) score.
- **Pennebaker LIWC-style markers** (2003) — track linguistic categories: 1st-person pronouns (self-focus), negative emotion words, cognitive complexity ("because", "however"), certainty markers ("never", "always"), social references.

For each message produce a compact record:
```
{ts, project, valence, arousal, plutchik: [...], dominant_tone, markers: {...}}
```

**Important reading caveats** (include in every report):
- This is text-only analysis. It misses sarcasm, context, and intent. Treat it as a mirror, not a verdict.
- Short technical messages ("fix the bug", "ok") are tone-neutral, not negative. Don't over-read.
- Frustration in debugging is normal cognitive work, not distress — see Csikszentmihalyi's flow (1990): productive struggle has the same surface markers as suffering.

### Step 4 — Pattern detection

Surface the patterns that actually matter. Look for:

1. **Temporal arc** — day-by-day mean valence + arousal. Highlight the trend (rising / falling / flat) and the variance (stable / volatile).
2. **Time-of-day** — bucket into morning (06-12), afternoon (12-18), evening (18-22), late-night (22-06). Flag if late-night dominates AND valence drops there.
3. **Project correlation** — mean valence per project. Flag if one project is >0.4 below the user's overall mean (a meaningful gap, not noise).
4. **Streaks** — 3+ consecutive sessions in the same emotional quadrant (Russell circumplex). E.g. "3 sessions in high-arousal / low-valence — frustration cluster."
5. **Vocabulary shifts** — compare this window's top emotional words against the journal's baseline (if learned). New words = new state.
6. **Self-focus drift** — Pennebaker: rising 1st-person pronoun frequency correlates with rumination / depressive ideation. Flag only if change >50% from baseline, never on first run.
7. **Cognitive complexity** — falling "because/however/although" use can indicate fatigue or stress narrowing thinking.

**Pattern presentation rule:** every flagged pattern must include (a) the observation, (b) the science behind why it matters, (c) one supportive reframe or question — never an instruction. Example:

> _Your messages got shorter and more 1st-person after 11pm on May 11 and 12. Pennebaker (2003) found rising self-focus often tracks with fatigue or rumination. Worth noticing — what was happening those nights?_

### Step 5 — Generate the report

Render both formats from a single shared structure. **Bind every visual decision to a `DESIGN.md` token** — no hard-coded hex, no inline `style=""` for colour or layout (data-driven values like `width: 60%` for a bar fill are allowed). Use the component patterns in `DESIGN.md §8` and the renderer rules in `reference/report-structure.md`.

**Before writing the file**, run the 16-item renderer self-audit (DESIGN.md §7 → "Renderer self-audit"):
1. Every SVG has `role="img"`, `<title>`, `<desc>`.
2. Every decorative span has `aria-hidden="true"`.
3. No `color-mix()` in emitted CSS — pre-compute mixes for **both themes** and emit as theme-scoped CSS vars (see item 15).
4. No `title=""`-only tooltips on interactive elements.
5. Russell scatter passes the overplotting guard (jitter applied; density-bin mode triggered if needed).
6. Anonymisation pipeline ran: deny-list + heuristic + structural strip. No client / brand names in quotes.
7. Section numbering 01–12 contiguous (no gaps).
8. Hero number paired with `−1 negative · 0 neutral · +1 positive` legend.
9. All text-bearing colour tokens used clear AA contrast against their background.
10. SVG fills bound to `var(--*)` tokens, not literal hex.
11. Sparse-data fallbacks emit "Not enough data" text inside affected SVG regions instead of misleading charts.
12. Touch-target sizes ≥44px on `(pointer: coarse)` viewports for interactive chart elements.
13. **Chart provenance** — every chart-bearing section (§05–§10) emits a `<p class="chart-source">` caption with framework/method + a real citation drawn from `reference/citations.md`. Per DESIGN.md §7 provenance table.
14. **Worth-trying integrity** — if §04 is non-empty: 2–4 items, each with one citation from `reference/citations.md`, no prescriptive phrases ("you should", "you must", "fix", "stop", "treatment", "therapy"). If §04 is empty, the section header still renders with the "no standout options this window" line; do not silently skip.
15. **Theme-parity** (1225 bug fix) — grep the emitted CSS for hex literals (`#[0-9a-fA-F]{3,8}`) appearing as `background`, `color`, or `border-color` values on selectors that hold text or visible surface. Allowed locations for hex literals: inside `:root { … }` and `@media (prefers-color-scheme: dark) :root { … }` blocks ONLY. Anywhere else → fail.
16. **Per-theme contrast check** — for every text-on-surface pairing (e.g. `.hl-quote` color on `.hl-card` background), compute the contrast ratio using the **light-mode** token values and again using the **dark-mode** token values. Fail if either ratio is < 4.5:1 for normal text or < 3:1 for large text (≥18pt or ≥14pt bold).

If any item fails, **refuse to write** and report which check failed. The user may override with `--force` but the default is fail-closed.

The audit is not a substitute for visual inspection. If a render passes 16/16 but still looks wrong in the reader's theme, the audit needs another item — log a journal entry and grow the checklist. Quality is the union of "passes the rules" + "looks right in the actual theme the reader uses."

**Section order** (DESIGN.md §4 IA — _fold-by-fold_: brief → highlights → insights → anchors → raw data → reference; 12 sections numbered 01–12 contiguously; both md + html unless noted):

_— Brief —_
01. **At a glance** — 2-3 sentence brief + hero valence with scale legend + quadrant chip + 4 stat tiles + daily badge row. The whole top-fold story.

_— Highlights —_
02. **Highlights** — compact grid of 3–5 bright-spot chip-cards (anonymised quote + date). Promoted from bottom to top fold per 2026-05-13-1150 feedback. **Required** (Fredrickson, 2001).

_— Insights —_
03. **Insights** — horizontal carousel of pattern cards (observation / science as `<details>` / reframe). 3–7 cards. Scroll-snap, no JS, accessible in source order. This is the report's middle act — the main signal.

_— Anchors —_
04. **Worth trying** — numbered list of 2–4 evidence-informed micro-experiments, each anchored to a real citation from `reference/citations.md`. **Never prescriptive** — the language is "research suggests…" / "studies indicate…" / "worth trying if it fits". Per DESIGN.md §6 language guardrails. Section may render empty (with the "no standout options" line) if no pattern this run admits a research-backed action.

_— Raw data — every chart carries a `chart-source` caption with framework + citation —_
05. **Emotional arc** — twin sparklines (valence + arousal) + arc narrative.
06. **Affect map** — _(HTML)_ Russell scatter with jitter + density-bin fallback + per-quadrant tint + size variation. _(MD)_ ASCII quadrant.
07. **Dominant emotions** — _(HTML)_ Plutchik wheel + size-redundant outer dot ring + ranked bars + quoted examples. _(MD)_ ranked list with %.
08. **Day rhythm** — 24-hour focusable strip with peak/dip callouts and sample-size warnings.
09. **By project** — diverging horizontal bars centred at zero; opacity scaled by message count.
10. **Word weather** — typographic vocabulary block (Fraunces italic). Polarity = colour + weight + underline-on-negative + aria-label.

_— Reference —_
11. **Citations** — bibliographic list per the user's citation_depth setting. Pull from `reference/citations.md`.
12. **Caveats** — text-analysis caveats from Step 3 + the "this is not clinical advice" line.

**HTML design requirements** — see `DESIGN.md` for the canonical contract (tokens, type, palette, anti-patterns, renderer guarantees). The high-level shape:
- **Visual-first.** Every section (except 08, 10, 11) leads with a chart, SVG, or typographic visualisation. <10-second scan target.
- **Type system** per DESIGN.md §2: Fraunces (display) + IBM Plex Sans (body) + IBM Plex Mono (mono). No Inter. No `-webkit-font-smoothing: antialiased`. No `font-feature-settings: "ss01"` on fallback fonts.
- **One display number per report** — the hero valence at `--t-hero` (5.5rem). Always paired with `−1 negative · 0 neutral · +1 positive` legend below.
- **Tabular figures** (`font-feature-settings: "tnum"`) on every numeric value.
- **Section numbering 01–11 contiguous** with `.num` span marked `aria-hidden="true"`. No gaps.
- **Quadrant palette** per DESIGN.md §3 — each chart binds to its appropriate `--q?-line` / `--q?-ink` / `--q?-fill` tokens. AA-compliant text tokens only.
- **`color-mix()` forbidden in emitted CSS** — renderer pre-computes mixes to hex.
- **Inline SVG only** — no external assets. Every SVG has `role="img"`, `<title>`, `<desc>`.
- **Interactive chart elements** are `<g tabindex="0">` with focus-visible state + inline-revealed details. No `title=""`-only tooltips.
- **Single `<style>` block in `<head>`. Dark mode via `prefers-color-scheme: dark` with mirror token set.
- **Max-width 720px**, hero allowed one asymmetric left-bleed on viewports ≥820px (DESIGN.md §4).
- **Anonymisation pipeline mandatory** per DESIGN.md §7 — three-layer (deny-list → heuristic → structural). No client / brand names in quotes.

**Tone of voice**: per preferences (`warm` default).
- Warm: "I noticed your evenings have been heavier this week — your mornings sounded brighter. That kind of swing is common when sleep gets short (Walker, 2017)."
- Clinical: "Mean valence in evening sessions: −0.18; mornings: +0.21. Diurnal mood variation correlates with sleep architecture (Walker, 2017)."
- Direct: "Evenings are dragging. Mornings are fine. Sleep matters here — see Walker (2017)."

**File naming**: `reports/YYYY-MM-DD-HHMM-recap.md` and `.html`.

### Step 6 — Save, log, and (optionally) open

1. `mkdir -p` the report directory if needed.
2. Write both files (per format preference).
3. Append to `~/.claude/skills/emotional-recap/sessions/YYYY-MM-DD-HHMM.md`:
   ```markdown
   # Session YYYY-MM-DD HH:MM
   - window: <value>
   - scope: <value>
   - conversations: N
   - dominant_quadrant: <Russell quadrant>
   - mean_valence: <x>
   - mean_arousal: <y>
   - top_emotions: [...]
   - patterns_flagged: [<short list>]
   - report_md: <path>
   - report_html: <path>
   ```
4. If `auto_open` is true and the format includes html, run `open <path>` (macOS) / `xdg-open` (Linux). Skip silently on failure.

### Step 7 — Summarise to the user

Print, in chat (≤6 lines):
- One-line vibe summary
- Top 2 patterns
- File paths

Example:
> Window: last 48h, 14 conversations across 3 projects. Mean tone: slight positive, moderately activated.
> 2 patterns to consider: (1) evening valence drop, (2) frustration streak in `azad` repo (3 sessions).
> Saved: `~/.claude/skills/emotional-recap/reports/2026-05-13-1430-recap.md` (+ .html)

### Step 8 — Invite feedback

Final line:
> Run `/emotional-recap feedback` — even one rating sharpens the next report. This is a mirror, not a diagnosis — your felt sense always overrides the analysis.

---

## Feedback & learning

When invoked as `/emotional-recap feedback`:

1. Find the most recent `sessions/YYYY-MM-DD-HHMM.md`. If none → say `No recent session found.` and stop.
2. Print a one-line summary of that session (vibe + top pattern).
3. Ask via `AskUserQuestion` (4 questions, one batch):
   - **Q1 — Tone fit**: warm / clinical / direct / preachy / off
   - **Q2 — Reading accuracy**: matched my experience / mostly right / off-base / can't tell
   - **Q3 — Pattern usefulness**: insightful / generic / missed the real thing / too many flags
   - **Q4 — HTML design**: loved / fine / cluttered / didn't open
4. Append to `~/.claude/skills/emotional-recap/feedback-journal.md`:
   ```markdown
   ## YYYY-MM-DD-HHMM
   - tone_fit: <answer>
   - accuracy: <answer>
   - usefulness: <answer>
   - design: <answer>
   - Signal: <one-line generalisation, e.g. "user finds 'warm' tone preachy; bias to 'clinical' next run">
   ```
5. **Promotion rule**: when 3+ sessions show the same `Signal`, promote it to `## Learned` in `preferences.md`. Mention once: `Noticed you consistently <signal>. Saved as a standing default — change anytime in /emotional-recap config.`
6. **Drift correction**: when a Learned rule is contradicted in 2 newer sessions, demote it (move out of `## Learned`, log the demotion in the journal with a `Demoted:` line). Never leave stale rules.

**Pre-selection bias**: in Step 5 of the main workflow, the tone-of-voice choice and pattern-density threshold are biased by current `## Learned` rules. E.g. if Learned says "user wants ≤3 flags per report", cap pattern flags at 3.

---

## Resume

If `~/.claude/skills/emotional-recap/resume-state.md` exists and `$ARGUMENTS == resume`:

1. Read the state file. Expected keys: `step`, `window`, `scope`, `files_processed`, `intermediate_path`.
2. Resume from the noted step using the saved scope. Skip files already processed.
3. On success, delete `resume-state.md`.

The main workflow writes `resume-state.md` only when it processes ≥10 files — small runs are not worth resuming. State is overwritten on each run.

---

## Principles

1. **Supportive, not diagnostic.** This skill is a mirror, not a medical tool. Every observation has a science citation and a reframing question, not a prescription. Mental health concerns belong with a professional.
2. **Graceful degradation.** Missing `preferences.md` / `feedback-journal.md` / failed JSONL parse — continue with defaults. Never block.
3. **User text only.** Only user-authored messages are analysed. Tool outputs and assistant messages are not the user's emotional signal.
4. **Cite the science.** Every pattern flagged must include a referenced finding. No folk psychology, no horoscope language.
5. **Bright spots are required.** Wellbeing reports that only flag problems become a negativity loop. Always include positive markers.
6. **Learn quietly.** Promote a `Learned` rule only after 3+ consistent signals. Mention once when promoting.
7. **Drift correction over staleness.** A `Learned` rule contradicted twice gets demoted. Never carry rules that no longer fit.
8. **Destructive actions need confirmation.** `reset` always asks before deleting `reports/` (they are user artefacts, not skill state).
9. **Self-awareness over self-judgement.** The point is noticing patterns, not scoring the user. Frame everything as observation + curiosity.
10. **Stop means stop.** If the user halts mid-run on a ≥10-file analysis, save resume state. Don't silently keep working.

---

## Self-audit notes

- Three-tier preferences: ✅ Defaults / Profile / Learned in Config block.
- `feedback`, `resume`, `config`, `reset`, `help` subcommands: ✅ all routed.
- Session logs + feedback journal + promotion + drift correction: ✅ in Feedback & learning section.
- Pre-selection bias from Learned: ✅ called out in Step 5.
- Configurability knobs (≥3): ✅ window, scope, format, report_dir, auto_open, tone, citation_depth, framework (8 knobs).
- Reference material externalised: `reference/frameworks.md`, `reference/citations.md`, `reference/report-structure.md` to keep this file under 500 lines.
