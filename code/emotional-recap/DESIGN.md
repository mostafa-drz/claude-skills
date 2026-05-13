# /emotional-recap design

This file is the **renderer contract** for the emotional-recap skill. Every HTML, SVG, or Markdown artefact produced by the skill must conform to the tokens, principles, and guarantees below.

It is distinct from `preferences.md`. DESIGN.md is the skill's aesthetic contract (versioned, identical for every user). `preferences.md` is the user's runtime configuration (per-machine, free-edit). On conflict: **DESIGN.md wins for renderer guarantees (a11y, anti-patterns, token shape); preferences wins for user-tunable knobs** (tone of voice, citation depth, framework choice).

Updated after the 2026-05-13 audit. See `feedback-journal.md` for the audit signals folded in.

---

## 1. Aesthetic direction

The report is a **personal editorial spread**, not a SaaS analytics dashboard. It is intended to be re-read, screenshotted, possibly printed. It speaks to one reader (the user themselves) about a sensitive subject (their emotional state), and so the visual language must be:

- **Quietly confident.** Generous whitespace. Few but decisive moves. The hero is the only loud thing on the page.
- **Editorial, not corporate.** Closer to a long-read magazine page (The Atlantic, MIT Tech Review, The Browser) than a Mixpanel dashboard.
- **Warm without being cute.** Paper-warm backgrounds, sage / gold / indigo / rose accent palette. No emoji headers, no gamification, no fitness-app energy.
- **Designed to be re-read.** Type for sustained attention. Citations and caveats are first-class, not footnotes.

References (look-and-feel only — do not literally copy):
- Edward Tufte's small-multiples plates
- Jonathan Hoefler's typographic specimens
- Massimo Vignelli's NYC subway diagrams (restraint, hierarchy)
- The Browser newsletter's typesetting
- 1960s scientific monograph plates (data + serif body + clear caveats)

This is NOT:
- A productivity dashboard ("you completed 14 sprints!")
- A mood-tracker app ("track your streak!")
- An analytics report ("KPI ↑ 4.2% MoM")
- A diagnostic tool ("you scored 67/100 on emotional regulation")

---

## 2. Type system

### Family

| Role     | Family                                      | Fallback                                                                                            |
|----------|---------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Display  | **Fraunces** (variable serif, opsz + wght)  | `"Iowan Old Style", "Charter", Georgia, serif`                                                      |
| Body     | **IBM Plex Sans**                           | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`                                 |
| Mono     | **IBM Plex Mono**                           | `ui-monospace, "SF Mono", Menlo, monospace`                                                         |
| Editorial italic (word weather, pull-quotes) | **Fraunces italic, opsz 144**     | Fraunces fallback above with italic + 600 weight                                                    |

Reasoning: per skill-creator manifest item 30 and frontend-design's "BOLD aesthetic direction," Inter / Roboto / Arial / system-only stacks are slop tells. Fraunces (display) + Plex (body) is a distinctive, editorial pairing. Both are open-source and embeddable.

**Self-containment policy**: if the report is generated with `embed_fonts: true` (a new preference, default `false`), inline WOFF2 data-URIs for Fraunces and Plex into the HTML `<style>` block. When `false`, fall back to the system stack — the renderer must verify visual hierarchy still reads correctly without the custom fonts.

### Scale (rem-based, root = 16px)

| Token            | Size      | Weight | Line | Letter-spacing | Use                                                    |
|------------------|-----------|--------|------|----------------|--------------------------------------------------------|
| `--t-hero`       | 5.5rem    | 300    | 0.9  | -0.04em        | Hero valence number (one per report)                   |
| `--t-display`    | 1.625rem  | 400    | 1.3  | -0.01em        | Vibe sentence under hero                               |
| `--t-h2`         | 0.75rem   | 600    | 1.2  | 0.18em UPPER   | Section heads                                          |
| `--t-h3`         | 1.0625rem | 600    | 1.4  | -0.005em       | Subsection / pattern titles                            |
| `--t-body`       | 1rem      | 400    | 1.65 | 0              | Paragraphs                                             |
| `--t-meta`       | 0.875rem  | 400    | 1.5  | 0              | Captions, range labels, project meta                   |
| `--t-micro`      | 0.75rem   | 500    | 1.4  | 0.08em         | Stat keys, eyebrows, axis labels                       |
| `--t-cite`       | 0.8125rem | 400    | 1.55 | 0              | Citations list                                         |

Tabular figures (`font-feature-settings: "tnum"`) wherever a numeric value lives — stat tiles, sparkline ranges, percentages, project metrics.

**Removed from the previous design** (audit fixes M2, M8):
- `font-feature-settings: "ss01", "cv11"` — only applies to Inter, dead code on Fraunces / Plex.
- `-webkit-font-smoothing: antialiased` — harms low-vision readers; let the browser handle font rendering.

---

## 3. Colour tokens

All text-bearing tokens must clear **WCAG AA (4.5:1 contrast)** against their default background. Decorative-only tokens (axis grid, faint markers) are allowed lower contrast but must be marked `aria-hidden="true"`.

### Light mode

```css
--bg:           #f5f1ea;   /* warm paper, was #faf8f5 */
--bg-elev:      #ffffff;   /* card surface */
--ink:          #1c1c24;   /* body text */
--ink-soft:     #4a4a55;   /* muted text — AA: 7.2:1 on --bg (was #6a6a78, 4.6:1) */
--ink-faint:    #6e6c72;   /* decorative only, aria-hidden */
--rule:         #e0dad0;   /* hairlines, borders */
--grid:         #e8e4db;   /* chart background grid */
```

### Quadrant palette (Russell circumplex — used everywhere)

Each quadrant gets three tones: a **fill** (for backgrounds, low-contrast), an **ink** (AA-compliant text), and a **line** (chart strokes, primary accent).

```css
/* Q1 — high arousal, positive valence — "excited / engaged" */
--q1-fill: #f0d29a;   --q1-ink: #6b4a14;   --q1-line: #b08338;

/* Q2 — high arousal, negative valence — "tense / frustrated" */
--q2-fill: #f0c8c8;   --q2-ink: #882727;   --q2-line: #b85959;

/* Q3 — low arousal, negative valence — "tired / low" */
--q3-fill: #d8d6e3;   --q3-ink: #3f3f5a;   --q3-line: #6b6b8a;

/* Q4 — low arousal, positive valence — "calm / focused" */
--q4-fill: #cfdcd1;   --q4-ink: #2f4f3a;   --q4-line: #5d7c66;
```

All `--q?-ink` tokens are verified ≥4.5:1 against `--bg`. Use these for any quadrant-coloured text (e.g. bright-spots heading, word-weather word polarity). The previous palette failed AA — fixed per audit H3.

### Dark mode

```css
--bg:           #14141b;
--bg-elev:      #1d1d27;
--ink:          #ece9e2;
--ink-soft:     #b5b3bc;
--ink-faint:    #6a6872;
--rule:         #2a2a37;
--grid:         #232330;

/* Quadrant inks brighten; fills stay close-to-bg for ambient washes */
--q1-fill: #3a2e16; --q1-ink: #e8c277; --q1-line: #d4a04a;
--q2-fill: #3a1e1e; --q2-ink: #e89a9a; --q2-line: #c66b6b;
--q3-fill: #25253a; --q3-ink: #b0b0d0; --q3-line: #8a8aaa;
--q4-fill: #1f3025; --q4-ink: #9bb59f; --q4-line: #7a9580;
```

Dark-mode SVG quadrant fills use these tokens (not hard-coded hex with `fill-opacity`). Per audit M3, SVG `<rect>` elements use `fill="var(--q1-fill)"` etc. so the chart actually adapts.

### `color-mix()` policy (theme-parity rule)

Per audit M1: `color-mix()` is **forbidden in emitted CSS**. But the obvious-looking fix — "pre-compute the mix to a hex literal and bake it into the rule" — silently breaks dark mode (1225 bug). Hex literals don't change with `prefers-color-scheme`, so any element whose background is a baked-in light-mode mix becomes broken when a dark-mode reader opens the file.

**Mandatory replacement pattern**: every renderer pre-compute generates **both** light and dark variants and emits them as theme-scoped CSS custom properties. UI selectors then use `var(--*)`, and the cascade picks the right value per theme.

```css
:root {
  --hl-card-bg: #ebebe3;   /* renderer pre-computed: mix(q4-fill 60%, bg-elev) for LIGHT */
}
@media (prefers-color-scheme: dark) {
  :root {
    --hl-card-bg: #1f2a23;  /* renderer pre-computed: same mix for DARK tokens */
  }
}
.hl-card {
  background: var(--hl-card-bg);   /* NEVER background: #ebebe3 — that locks the theme */
}
```

**Forbidden in emitted CSS**: any hex literal as a background/colour/border of an element that holds text or visible surface. All such surfaces must resolve through a `var(--*)` whose value is theme-scoped. Renderer self-audit item 15 enforces this with a regex grep.

This rule applies to every renderer pre-compute. There are no exceptions for "small" mixes like a 5% tint.

---

## 4. Layout

### Information architecture (the fold-by-fold contract)

The report reads top-to-bottom in **four density zones**: brief → highlights → insights → raw data. The intent is that a reader who only sees the top 20% of the document gets the headline; a reader who scrolls one screen gets the patterns; a reader who scrolls to the bottom gets the data plates. Citations and caveats live at the very bottom.

| Zone           | §  | Section            | Density | Visual shape                                                  |
|----------------|----|--------------------|---------|---------------------------------------------------------------|
| **Brief**      | 01 | At a glance        | High    | Hero number + scale legend + vibe sentence + 4 stat tiles + day-badges row + quadrant chip |
| **Highlights** | 02 | Highlights         | High    | Compact grid of 3 "bright spot" chip-cards (quotes + date)    |
| **Insights**   | 03 | Insights           | Medium  | **Horizontal carousel** of pattern cards (observation / science / reframe). 3–7 cards, snap-scroll, no JS |
| **Anchors**    | 04 | Worth trying       | Medium  | Numbered list of 2–4 evidence-informed micro-experiments, each anchored to a real citation. **Not prescriptions** — the framing is "research suggests X, your felt sense leads." |
| **Raw data**   | 05 | Emotional arc      | Low     | Twin sparklines + arc narrative                               |
|                | 06 | Affect map         | Low     | Russell scatter (jitter + density-bin fallback)               |
|                | 07 | Dominant emotions  | Low     | Plutchik wheel + ranked bars + quoted examples                |
|                | 08 | Day rhythm         | Low     | 24h focusable strip                                           |
|                | 09 | By project         | Low     | Diverging bars                                                |
|                | 10 | Word weather       | Low     | Typographic vocabulary cloud                                  |
| **Reference**  | 11 | Citations          | Ref     | Bibliographic list                                            |
|                | 12 | Caveats            | Ref     | Disclaimers                                                   |

The reordering — moving the engaging items (Highlights, Insights, Worth trying) above the heavy charts — is signalled by the user (2026-05-13-1150 feedback; reinforced 1209 with "science-based recommended actions") and now enforced by this DESIGN.md. The renderer must emit sections in this order. Reports that bury the carousel or actions below charts violate the contract.

**Twelve sections, numbered 01–12 contiguously.** The previous 01–11 contract was widened by one to admit Worth trying. No gaps; the `.num` span is `aria-hidden="true"` on every `h2`.

**The "anchors" zone is supportive, never directive.** Per the skill's first Principle ("supportive, not diagnostic"), the Worth trying section must NEVER read as a prescription. It frames each option as research-anchored, the user-led ("worth trying if it fits"), and is explicitly skippable. See §6 anti-patterns for the language guardrails.

### Geometry & rhythm

- **Max content width**: 720px.
- **Side padding**: 24px mobile, 32px desktop.
- **Vertical rhythm**: 56px between major sections; 24px within a section; 12px between paragraph and chart.
- **Section dividers**: top border on `h2`, not card chrome on every section. Cards are reserved for charts that *need* a contained surface.
- **Section numbering**: every `h2` carries a numeric prefix `<span class="num" aria-hidden="true">01</span>`. **No gaps in numbering** (per audit H6). Eleven sections, numbered 01–11.
- **Hero asymmetry**: the hero number may bleed 24px to the left of the body column on viewports ≥820px. This is the **one spatial moment of asymmetry**; everything else is structured. Per frontend-design guidance: don't sprinkle asymmetry, commit to one moment.
- **No nested cards.** Anti-pattern. If a section needs a card AND a chart, the chart is unboxed inside the section card; do not wrap the chart in a second card.
- **Carousel scroll**: section 03 is the one horizontal-scroll moment. The rest of the document scrolls vertically only. Per `prefers-reduced-motion: reduce`, the carousel still scrolls but without smooth-scroll behaviour.

---

## 5. Visualisation principles

### Universal rules

1. **Colour is never the sole encoding.** Always pair with size, shape, position, weight, or texture (audit H4).
2. **Dense or uniform data → degrade gracefully.** Detect at render time:
   - If ≥85% of scatter points fall in the same 20×20px cell, **switch from per-dot rendering to a 2D heatmap grid** (each cell shaded by density, with a small legend).
   - If `n_days < 2` or all values identical, render text inside the SVG: `<text x="…" y="…" fill="var(--ink-soft)">Not enough data yet — check back after another day.</text>`
3. **Tooltips must be focusable AND visible.** No `title=""`-only tooltips (audit H2). Hour cells, project bars, scatter dots become `<g tabindex="0" role="button" aria-label="…">` with inline-revealed details on focus/hover.
4. **Every SVG has** (audit H1):
   - `role="img"`
   - `<title>` (short label)
   - `<desc>` (1–2 sentence description of the data shown)
   - `aria-describedby` if the surrounding caption is the description
5. **Per-section visual identity** (audit M9). Each chart binds to its semantically appropriate accent — valence sparkline uses `--q-by-dominant-quadrant`; the arousal sparkline uses `--ink-soft`; project bars use `--q4-line` for positive, `--q2-line` for negative. Don't paint everything sage.
6. **Touch targets** (audit M4). Interactive chart elements (hour cells, project rows, focusable dots) are minimum 44×44px on touch viewports. On desktop, hour cells may be smaller; on `(pointer: coarse)` they expand or collapse the strip into a 2-row 12-hour format.
7. **Hero number context** (audit M7). The hero valence number must be paired with a micro-legend immediately below: `−1 negative · 0 neutral · +1 positive`. Non-negotiable.

### Russell scatter — special rules

This is the chart the audit broke. Specific fixes:

1. **Jitter every dot by ±6px in both axes** (audit C1). If two dots share the same `(valence, arousal)`, they will still spread visibly.
2. **Cap render count at 200 dots**; if more, deterministically subsample (every Nth message) and emit a caption `"N of M messages plotted"`.
3. **Density-bin mode**: if after jitter ≥85% of dots still cluster in one 32×32px cell, switch encoding entirely. Emit a 10×10 grid heatmap with cell opacity = `messages_in_cell / max_cell_count`. Show the centroid + 3 quartile rings instead of individual dots.
4. **Per-message quadrant tint**: each dot uses the line colour of *its own* quadrant — Q1 dots are `--q1-line`, Q2 dots `--q2-line`, etc. This adds a non-colour signal? No — it's *more* colour but tied to position, so colour reinforces position rather than being the sole channel. Combined with size variation (r=2 for low confidence, r=3 for high), this gives two redundant signals.

### Sparklines — special rules

- Centred zero-line for valence; bottom-anchored for arousal.
- Single accent colour (the dominant-quadrant line). Data points marked with `r=3` filled circles + invisible 12px hit area for focus.
- Range label appears below the sparkline with explicit axis hint: `Valence range: +0.01 → +0.08 · scale −1 to +1`. The current report's `+0.01 → +0.08` without scale is half a label.

### Day rhythm strip — special rules

- 24 cells, each `<g tabindex="0">` with `<title>` (short) and inline-revealed `<text>` on focus (long).
- On `prefers-reduced-motion: no-preference`, focus reveals an animated underline; otherwise instant.
- Empty hours (no data) render as `--grid` with `aria-label="0 messages"`; never as the same colour as a valence reading.
- Below the strip: textual summary of peak / dip hours with sample-size warning if either band has fewer than 5 messages.

### Plutchik wheel — special rules

- 8 wedges with opacity scaled by emotion frequency. Add a redundant ring of small filled circles outside the wheel, sized by frequency, so size is a non-colour signal of dominance.
- Wedge labels (joy, ant, …) are `--t-micro` placed outside the perimeter; do not abbreviate to 3-letter codes if the perimeter has room — readability over decoration.

### Word weather — special rules

- Polarity carried by **both colour AND weight**:
  - Positive: `--q4-ink` + weight 500
  - Negative: `--q2-ink` + weight 500 + underline (`text-decoration-thickness: 1px; text-decoration-color: currentColor`)
  - Neutral: `--ink` + weight 400
- Per audit H4, the underline on negative words provides a non-colour channel.
- Size range: 14px → 36px linear by log-frequency.

---

## 6. Anti-patterns to avoid

Universal slop list (from skill-creator manifest item 30):
- Inter / Roboto / Arial / `system-ui` as primary font choice — already replaced (§2).
- Purple gradients on white — n/a; palette is sage/gold/indigo/rose by design.
- Glassmorphism / backdrop-blur for decoration — none used; do not add.
- Hero metrics without scale legend — fixed (§5 universal rule 7).
- Color-only encoding — fixed (§5 universal rule 1).
- `title=""`-only tooltips — fixed (§5 universal rule 3).
- Nested cards — fixed (§4).
- Bounce / spring easing on a wellness report — none used; do not add.
- `font-feature-settings: "ss01"` on fallback fonts — removed (§2).
- `-webkit-font-smoothing: antialiased` — removed (§2).

Skill-specific don'ts:
- **Don't gamify.** No streaks, no scores, no "level up" language. The data is observational; framing is editorial.
- **Don't emoji-prefix section heads.** Eyebrow numbering carries the visual signal.
- **Don't render the whole report as one giant card.** Long unboxed flow with selective card surfaces around charts.
- **Don't surface client / brand names in quoted text** (audit C2). The anonymiser is mandatory; see §7.
- **Don't say "you should"** anywhere — patterns end with a question, the Worth-trying section ends with an _invitation_ anchored to research. The skill's first Principle (supportive, not diagnostic) is encoded in the language of every section.

Language guardrails for the **Worth trying** section (§04). The section is the *only* place the report makes forward-looking suggestions, and it has the tightest constraints:

- **Never** use: "you should", "you must", "do X", "stop doing Y", "this will fix", "this is the answer".
- **Always** use: "research suggests…", "studies indicate…", "worth trying if…", "an option anchored in…", "this is one experiment, not a prescription".
- **Always cite.** Every Worth-trying item carries one specific real citation from `reference/citations.md`. If a candidate suggestion has no citation in the file, **drop the suggestion** — do not generate folk-psychology advice and then fabricate a source.
- **Never medicalise.** No "treatment", "therapy", "intervention", "symptom", "disorder". This is text-based pattern observation; the language stays in the editorial register.
- **Limit to 2–4 items per report.** A long list reads as a prescription pad. Two well-grounded options beat six generic ones.
- **Include the "skip with no judgement" line** in the section footer: _"None of these are required. Skip any that don't fit; your felt sense leads."_
- **Generate suggestions only from the patterns detected in this run.** No generic wellness tips ("drink more water"). Every Worth-trying item must be a direct response to a pattern flagged in §03 Insights, with a paper from the citation file backing it.

---

## 7. Renderer contract (hard guarantees)

The renderer **must** satisfy all of the following before writing an HTML file. If any check fails, abort the write and report the specific failure to the user.

### Accessibility
1. Every `<svg>` has `role="img"`, `<title>`, `<desc>`, and `aria-labelledby` or `aria-describedby` wiring those into the surrounding context.
2. Every decorative inline element (section number `.num`, swatch `.dot`, the `★` glyph) has `aria-hidden="true"`.
3. All text-bearing tokens used clear WCAG AA (≥4.5:1) against the default background. Renderer verifies before emit; fails closed.
4. No `title=""`-only tooltips. Any per-element hidden detail is exposed via focusable container with inline-revealed text on focus and hover.
5. Heading hierarchy is contiguous: H1 once, H2 numbered 01–11 with no gaps, H3 within sections.
6. Touch targets for interactive chart elements ≥44×44px on `(pointer: coarse)`.

### Privacy / anonymisation (audit C2)
The anonymiser runs as a **three-layer pipeline** in this order:

1. **Deny-list** (loaded from `~/.claude/skills/emotional-recap/anonymise.deny` + project memory): exact-match strings to redact and replace with `<client>`, `<person>`, `<project>`, or category tag. Seeded with known client/brand names from the user's memory (e.g. `verizon`, `unilever`, `morgan`).
2. **Heuristic strip**: tokens matching `[A-Z][a-z]{2,}` that aren't in the English dictionary OR aren't in a small whitelist of common words → redact to `<name>`.
3. **Structural strip** (already in place): file paths, URLs, secret-shaped strings, code blocks → paraphrase.

If a quote would be reduced to <40% of its original length after anonymisation, drop the quote and use a paraphrase ("a debugging exchange about the build pipeline").

### Browser compatibility
1. `color-mix()` is **forbidden in emitted CSS** (audit M1). Renderer pre-computes for both themes and emits theme-scoped CSS custom properties — never a baked hex on a rule (1225 bug fix; see §3 "color-mix policy").
2. No `prefers-color-scheme` dependency for critical contrast — both light and dark mode token sets must pass AA independently, and the renderer self-audit must verify this independently per theme (item 16).
3. Sized hero (`5.5rem`) must remain readable at viewports ≥320px wide. On `(max-width: 360px)`, hero size drops to `3.75rem`.

### Visual integrity
1. Russell scatter overplotting guard active (audit C1): jitter + cap + density-bin mode.
2. Sparse-data fallback active for sparklines, scatter, rhythm strip.
3. SVG fills bound to CSS custom properties, never hard-coded hex (audit M3).
4. No reliance on inline `style=""` for renderer-critical layout (audit L7) — utility classes only. Inline `style=""` allowed for runtime data values (e.g. `style="width: 60%"` for a bar fill) but not for layout / colour decisions.

### Provenance (every chart grounded in a real citation)
Per the 2026-05-13-1209 feedback _"for all charts and data grounded in truth"_: every chart-bearing section emits a `<p class="chart-source">` caption directly under the SVG, naming the framework or method and the real citation from `reference/citations.md`. The renderer fails closed if any chart is missing its source line.

| Section            | Required caption                                                                                       |
|--------------------|--------------------------------------------------------------------------------------------------------|
| 05 Emotional arc   | _Method: daily mean valence and arousal across the window. Scale: −1 to +1 valence, 0 to 1 arousal._    |
| 06 Affect map      | _Framework: Russell circumplex of affect (1980)._                                                       |
| 07 Dominant emotions | _Framework: Plutchik wheel of emotions (1980). Lexicon: NRC Emotion (Mohammad & Turney, 2013)._       |
| 08 Day rhythm      | _Method: hourly mean valence aggregation. Circadian framing per Walker (2017); see also Yoo et al. (2007)._ |
| 09 By project      | _Method: per-project valence mean, in-window. Opacity ∝ message count._                                |
| 10 Word weather    | _Lexicon: NRC Emotion (Mohammad & Turney, 2013). Linguistic markers: LIWC-style (Tausczik & Pennebaker, 2010)._ |
| 04 Worth trying    | Each item carries its own inline citation (Anchor: <ref>). Section footer cites the same papers used for that run's patterns. |

### Renderer self-audit
Before writing the file, the renderer prints a one-line self-audit report:
```
Renderer audit: 16/16 contract items satisfied. Report: <path>.
```
The audit has grown over time as bugs surfaced:
- **1209**: added 13 (every chart-bearing section emits a `chart-source` caption with a real citation) and 14 (Worth trying section integrity — 2–4 items, each cited, no prescriptive language).
- **1225 (this update)**: added 15 (**theme-parity check** — no hex literal appears as `background`, `color`, or `border-color` on a text-bearing rule; every such surface must resolve via a `var(--*)`. Regex-grep the emitted CSS to enforce.) and 16 (**per-theme contrast check** — for every text-on-surface pairing, compute the contrast ratio independently in light and in dark mode tokens; fail if either ratio < 4.5:1).

If any item fails, print which one and refuse to write. The user can override with `--force` but the default is fail-closed.

The audit is not a substitute for visual inspection. If a render passes 16/16 but still _looks_ wrong, the audit needs another item — file a journal entry and grow the checklist. Quality is the union of "passes the rules" + "looks right in the actual theme the reader uses."

---

## 8. Component patterns

Each component below is the canonical HTML snippet. **All colour and font references use tokens.** Renderers must not deviate without updating this section.

### Hero

```html
<header class="hero" role="banner">
  <div class="eyebrow">Emotional recap · {window} · {scope}</div>
  <div class="hero-row">
    <div>
      <div class="hero-num" aria-label="Mean valence {valence_value} on a scale of negative one to positive one">
        <span class="sign" aria-hidden="true">{sign}</span>{valence_abs}
      </div>
      <div class="hero-legend" aria-hidden="true">−1 negative · 0 neutral · +1 positive</div>
      <div class="hero-meta">Mean valence · arousal {arousal_mean}</div>
    </div>
    <div class="hero-chip">
      <span class="dot" aria-hidden="true" style="background: var(--{quadrant}-line);"></span>
      {quadrant_label}
    </div>
  </div>
  <p class="vibe">{vibe_one_liner}</p>
  <p class="timestamp"><time datetime="{iso}">{human_timestamp}</time></p>
</header>
```

### Stats grid + day badges (section 01 — At a glance)

```html
<section aria-labelledby="s01">
  <h2 id="s01"><span class="num" aria-hidden="true">01</span> At a glance</h2>
  <p class="brief">{2-3 sentence summary — the headline of the whole report.}</p>
  <div class="stats">
    <div class="stat"><div class="k">Conversations</div><div class="v">{n}</div></div>
    <!-- repeat 4 -->
  </div>
  <div class="badges" role="list" aria-label="Daily mood">
    <div class="badge" role="listitem" style="--badge-color: var(--{q}-line);">
      <div class="swatch" aria-hidden="true"></div>
      <div class="day">{day_short}</div>
      <div class="day-val">{valence}</div>
    </div>
    <!-- repeat per day -->
  </div>
</section>
```

The 2–3 sentence brief is **the most important addition from the 2026-05-13-1150 feedback**: a top-of-document executive summary. Renderer generates this from the patterns + vibe + dominant quadrant. Keep it to <60 words.

### Highlights strip (section 02 — was Bright spots)

Compact chip-cards moved from the bottom of the report to the top fold. Three to five quotes maximum. Each card is small, scannable, and self-contained.

**Visual weight policy (1225 bug fix)**: highlight cards use the **same neutral surface as insight cards** (`--bg-elev`) with a 3px `--q4-line` left-border accent. No full tint. Heavy tinted blocks were dominating the dark-mode page and hiding the quotes inside them (light text on a light pre-computed mix). The lighter treatment is consistent with the rest of the report's card vocabulary and works in both themes.

```html
<section aria-labelledby="s02">
  <h2 id="s02"><span class="num" aria-hidden="true">02</span> Highlights</h2>
  <ul class="highlights" role="list">
    <li class="hl-card" aria-label="Bright spot from {date}">
      <span class="hl-glyph" aria-hidden="true">★</span>
      <div class="hl-body">
        <p class="hl-quote">"{anonymised excerpt}"</p>
        <p class="hl-meta">{date}</p>
      </div>
    </li>
    <!-- 2-4 more -->
  </ul>
  <p class="t-meta">Quick approvals compound — Fredrickson (2001) on broaden-and-build.</p>
</section>
```

CSS — all surfaces resolve through `var(--*)`, never a baked hex:

```css
.highlights {
  list-style: none; padding: 0; margin: 16px 0 8px;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}
.hl-card {
  display: flex; gap: 12px; align-items: flex-start;
  background: var(--bg-elev);            /* same surface as insight cards */
  border: 1px solid var(--rule);
  border-left: 3px solid var(--q4-line); /* accent stripe */
  border-radius: 10px;
  padding: 14px 16px;
}
.hl-glyph {
  color: var(--q4-line);                 /* line token, not fill — always visible accent */
  font-size: 0.95rem; line-height: 1.4;
  flex-shrink: 0; margin-top: 1px;
}
.hl-body { min-width: 0; flex: 1; }
.hl-quote {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 0.9375rem; line-height: 1.45;
  color: var(--ink);                     /* ink on bg-elev → AA in both themes */
  margin: 0;
}
.hl-meta {
  font-family: var(--font-mono);
  font-size: 0.6875rem; letter-spacing: 0.04em;
  color: var(--ink-soft);
  margin: 6px 0 0;
}
```

**Empty-content guard** (1225-adjacent): if anonymisation reduces a candidate quote below 3 visible words, the entire card is dropped (not rendered empty). If fewer than 3 highlight quotes survive, render a single explanatory chip: _"Quiet window — no standout positive markers this run. Highlights aren't every-window guaranteed."_ Renderer self-audit item 14 (Worth trying integrity) is paralleled here implicitly — don't render shells.

The compact grid pattern (`auto-fit minmax(240px, 1fr)`) gives one column on mobile, two on tablet, two-three on wide desktop. No JS needed.

### Chart source caption (universal — applies to every chart-bearing section)

Every chart-bearing section (§05 Arc, §06 Affect map, §07 Dominant emotions, §08 Day rhythm, §09 By project, §10 Word weather) emits this footer immediately after the SVG / chart:

```html
<p class="chart-source">
  <span class="chart-source-label" aria-hidden="true">Source</span>
  {framework or method} <span class="chart-source-cite">— {citation}</span>
</p>
```

```css
.chart-source {
  font-size: 0.75rem; line-height: 1.5;
  color: var(--ink-soft);
  margin: 10px 0 0;
  display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap;
  border-top: 1px dashed var(--rule); padding-top: 8px;
}
.chart-source-label {
  font-size: 0.625rem; letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--ink-faint); font-weight: 600;
  font-family: var(--font-mono);
  flex-shrink: 0;
}
.chart-source-cite { font-style: italic; color: var(--ink-soft); }
```

The exact caption text for each section is defined in DESIGN.md §7 "Provenance" table. Renderer must emit the caption or the self-audit fails (item 13).

### Worth trying (section 04 — evidence-informed options)

A numbered list of 2–4 micro-experiments, each tied to a real citation. Visual identity uses the Q1 (anticipation / forward-looking) token palette to distinguish from the Insights carousel (which uses the dominant-quadrant accent).

```html
<section aria-labelledby="s04">
  <h2 id="s04"><span class="num" aria-hidden="true">04</span> Worth trying</h2>
  <p class="t-meta">Evidence-informed options, one per pattern above. None of these are required — your felt sense leads.</p>
  <ol class="actions">
    <li class="action">
      <div class="action-title">{title}</div>
      <p class="action-body">{What the option is + why it might fit the pattern. Phrased as "research suggests" or "studies indicate", never "you should". 1–2 sentences.}</p>
      <p class="action-anchor">
        <span class="action-anchor-label" aria-hidden="true">Anchor</span>
        {full inline citation, e.g. "Ariga & Lleras (2011) — brief mental breaks restore vigilance"}
      </p>
    </li>
    <!-- 1-3 more action items, maximum 4 total -->
  </ol>
  <p class="t-meta action-footer">Anchored in the patterns above and the citations at §11. Skip any that don't fit.</p>
</section>
```

```css
.actions {
  list-style: none; padding: 0; margin: 16px 0;
  display: flex; flex-direction: column; gap: 12px;
  counter-reset: action-counter;
}
.action {
  counter-increment: action-counter;
  position: relative;
  padding: 16px 20px 16px 56px;
  background: var(--bg-elev);
  border: 1px solid var(--rule);
  border-left: 3px solid var(--q1-line);
  border-radius: 12px;
}
.action::before {
  content: counter(action-counter, decimal-leading-zero);
  position: absolute; left: 18px; top: 16px;
  font-family: var(--font-mono);
  font-size: 0.8125rem; letter-spacing: 0.04em;
  color: var(--q1-ink); font-weight: 600;
}
.action-title { font-weight: 600; font-size: 1rem; margin: 0 0 6px; line-height: 1.35; }
.action-body { font-size: 0.9375rem; margin: 0 0 10px; }
.action-anchor {
  font-size: 0.8125rem; line-height: 1.55;
  color: var(--ink-soft);
  margin: 0; padding-top: 10px;
  border-top: 1px dashed var(--rule);
  display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap;
}
.action-anchor-label {
  font-size: 0.6875rem; letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--q1-line); font-weight: 600;
  font-family: var(--font-mono);
  flex-shrink: 0;
}
.action-footer { margin-top: 12px; font-style: italic; }
```

**Renderer rules for Worth trying**:
1. **Match items to detected patterns 1:1 where possible.** If §03 Insights surfaced 4 patterns, generate 2–4 actions that each respond to one of those patterns. Don't generate generic wellness advice; don't action a pattern that wasn't detected.
2. **Drop suggestions without citations.** If no real citation in `reference/citations.md` supports a candidate action, drop the action entirely. Never fabricate a reference.
3. **Citation diversity.** Don't repeat the same citation across all action items in one report. If two actions point to Csikszentmihalyi (1990), reframe or drop one.
4. **Language audit pre-write.** Scan all action-title and action-body text against the forbidden phrases in §6 ("you should", "you must", "stop", "fix", "treatment", "therapy", "intervention", "symptom"). Any match → refuse to write.
5. **2–4 items maximum.** Less is more. A long list reads prescriptive.
6. **Empty Worth-trying is allowed.** If the patterns this run don't admit a research-backed action with a real citation, render the section header with an `<p class="t-meta">No standout options this window — the patterns above weren't ones with strong evidence-based experiments. Skip ahead.</p>` and move on. Don't fill the slot with weak suggestions.

### Insights carousel (section 03 — was Patterns I noticed)

The middle-of-report carousel. Horizontal scroll with CSS snap; works without JS. Each card is fully accessible in source order — screen readers and keyboard users get the full list linearly.

```html
<section aria-labelledby="s03">
  <h2 id="s03"><span class="num" aria-hidden="true">03</span> Insights</h2>
  <p class="t-meta">{n} pattern{s} from the window. Scroll →</p>
  <div class="carousel" role="region" aria-label="Pattern insights">
    <article class="insight-card" aria-labelledby="i1">
      <div class="insight-num" aria-hidden="true">01 / {n}</div>
      <h3 id="i1">{pattern_title}</h3>
      <p class="insight-observation">{observation}</p>
      <details class="insight-science">
        <summary>Why this matters</summary>
        <p>{science_with_inline_citation}</p>
      </details>
      <p class="insight-reframe"><span class="reframe-label">Worth asking</span> {reframe_question}</p>
    </article>
    <!-- repeat -->
  </div>
</section>
```

CSS:
```css
.carousel {
  display: flex; gap: 16px;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  scroll-snap-type: x mandatory;
  scrollbar-width: thin;
  scrollbar-color: var(--rule) transparent;
  padding: 4px 0 16px;
  margin: 12px -24px 0;   /* full-bleed on mobile */
  padding-left: 24px; padding-right: 24px;
  -webkit-overflow-scrolling: touch;
  /* edge-fade affordance */
  mask-image: linear-gradient(to right, transparent 0, #000 24px, #000 calc(100% - 24px), transparent 100%);
}
@media (prefers-reduced-motion: reduce) { .carousel { scroll-behavior: auto; } }
.carousel::-webkit-scrollbar { height: 6px; }
.carousel::-webkit-scrollbar-thumb { background: var(--rule); border-radius: 3px; }

.insight-card {
  flex: 0 0 min(320px, 86%);
  scroll-snap-align: start;
  display: flex; flex-direction: column; gap: 10px;
  padding: 18px 20px;
  background: var(--bg-elev);
  border: 1px solid var(--rule);
  border-left: 3px solid var(--accent);
  border-radius: 12px;
}
.insight-card .insight-num {
  font-family: var(--font-mono);
  font-size: 0.6875rem; letter-spacing: 0.12em;
  color: var(--ink-soft);
}
.insight-card h3 { margin: 0; font-size: 1rem; font-weight: 600; line-height: 1.35; }
.insight-card .insight-observation { margin: 0; font-size: 0.9375rem; }
.insight-card details { font-size: 0.875rem; }
.insight-card summary {
  color: var(--ink-soft); cursor: pointer; padding: 4px 0;
  list-style: none;
}
.insight-card summary::before { content: "▸ "; color: var(--accent); }
.insight-card details[open] summary::before { content: "▾ "; }
.insight-card .insight-reframe {
  margin: 0; padding-top: 10px;
  border-top: 1px solid var(--rule);
  font-size: 0.9375rem;
}
.insight-card .reframe-label {
  display: block;
  font-size: 0.6875rem; letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--ink-soft); font-weight: 600; margin-bottom: 4px;
}
```

A11y guarantees for the carousel:
1. Wrapping `<div role="region" aria-label>` makes it a discoverable landmark.
2. Cards are `<article>` in source order — screen readers get the full list, no scroll needed.
3. Each card has its own `aria-labelledby` pointing to its `<h3>`.
4. `<details>`/`<summary>` provides progressive disclosure for the Science paragraph — defaults closed so cards stay scannable.
5. Keyboard tab order traverses cards linearly; arrow keys are NOT custom-handled (default browser behaviour preserved).
6. No dots indicator — they require JS to sync with scroll position. The scrollbar + edge-fade + "Scroll →" instruction provide affordance.
7. Per `prefers-reduced-motion: reduce`, smooth scrolling disabled.

### Arc card (sparkline)

```html
<section aria-labelledby="s02">
  <h2 id="s02"><span class="num" aria-hidden="true">02</span> Emotional arc</h2>
  <div class="card">
    <div class="t-micro">Valence · daily mean</div>
    <svg class="spark" viewBox="0 0 600 80" preserveAspectRatio="none"
         role="img" aria-labelledby="s02-vt s02-vd">
      <title id="s02-vt">Valence sparkline</title>
      <desc id="s02-vd">Daily mean valence ranging from {min} to {max} over {n_days} days. Trend: {trend}.</desc>
      <line x1="10" y1="40" x2="590" y2="40" stroke="var(--rule)" stroke-dasharray="3,3"/>
      <polyline fill="none" stroke="var(--{q}-line)" stroke-width="2.5" stroke-linecap="round" points="…"/>
      <!-- focusable point groups -->
    </svg>
    <div class="t-meta">Valence range: {min} → {max} · scale −1 to +1</div>
    <!-- arousal sparkline parallel structure -->
  </div>
</section>
```

### Affect map (Russell scatter)

```html
<section aria-labelledby="s03">
  <h2 id="s03"><span class="num" aria-hidden="true">03</span> Affect map</h2>
  <div class="card">
    <svg viewBox="0 0 320 320" role="img" aria-labelledby="s03-t s03-d" style="width:100%; max-width:480px;">
      <title id="s03-t">Affect map — Russell circumplex scatter</title>
      <desc id="s03-d">
        {n_messages} messages plotted across valence and arousal axes. Centroid at quadrant {q}.
        {mode_note}  <!-- e.g. "Density-binned because most messages clustered near the centroid." -->
      </desc>
      <!-- quadrant fills bound to tokens -->
      <rect x="160" y="0" width="160" height="160" fill="var(--q1-fill)"/>
      <!-- … axes, labels …  -->
      <!-- per-dot OR per-cell density mode (see §5) -->
      <circle cx="{x}" cy="{y}" r="{r}" fill="var(--{q}-line)" opacity="0.5"/>
      <!-- centroid -->
      <circle cx="{cx}" cy="{cy}" r="7" fill="var(--{q}-line)" stroke="var(--bg)" stroke-width="3"/>
    </svg>
    <p class="t-meta caption">{mode_caption}</p>
  </div>
</section>
```

### Day rhythm strip (focusable hours)

```html
<div class="rhythm" role="group" aria-label="Hourly valence">
  <g class="h" tabindex="0" role="button"
     aria-label="{hour}:00 — {n_msgs} messages, mean valence {valence}"
     style="background: {pre_computed_hex};">
    <!-- visual content -->
  </g>
  <!-- ×24 -->
</div>
<p class="t-meta">Peak {peak_hour} · Dip {dip_hour}{sparse_note}</p>
```

### Pattern card (observation / science / reframe)

```html
<article class="pattern" aria-labelledby="p1">
  <h3 id="p1">{n}. {title}</h3>
  <p>{observation}</p>
  <div class="label" aria-hidden="true">Science</div>
  <p class="t-meta">{science_with_citation}</p>
  <div class="label" aria-hidden="true">Worth asking</div>
  <p>{reframe_question}</p>
</article>
```

### Word weather span

```html
<span class="w {pos|neg|neu}" style="font-size:{px}px;" aria-label="{word}, {polarity}, {frequency} occurrences">{word}</span>
```

Renderer notes: the visual style for `.w.neg` includes underline (CSS, not inline). The `aria-label` carries polarity textually so screen readers don't need to parse the colour.

---

## Provenance

This DESIGN.md was authored after the 2026-05-13 audit of the first generated report. Audit signals folded in: C1 (scatter overplotting), C2 (anonymisation), H1 (SVG aria), H2 (title tooltips), H3 (palette contrast), H4 (color-only encoding), H5 (Inter font), H6 (numbering), M1–M9, L1–L8. See the audit report in conversation history.

Future audits should append a `## Provenance` entry below this line rather than rewriting it — keep the history of why each rule exists.
