# Report structure & templates

> **DESIGN.md is the canonical source for tokens, type, palette, anti-patterns, and renderer guarantees.** This file is the implementation-level spec — section ordering, SVG render math, ASCII fallbacks. When this file shows a hex value or a hard-coded property, treat it as a placeholder for the equivalent `var(--*)` token from DESIGN.md §3. Renderers must emit token references in the final HTML; the renderer must additionally pre-compute any `color-mix()` expressions to solid hex values (DESIGN.md §7).
>
> Audit signals (2026-05-13) folded in across this file: C1 scatter jitter+density-bin, C2 three-layer anonymisation, H1 SVG aria, H2 focusable tooltips, H3 AA-compliant text tokens, H4 non-colour redundancy (size, weight, underline), H5 Fraunces + Plex, H6 contiguous 01–11 numbering, M1 no `color-mix()` in output, M2 no font-smoothing, M3 SVG fills via tokens, M4 44px touch targets, M7 hero scale legend.

Both Markdown and HTML reports share the same logical structure. The HTML version is **visual-first** — multiple charts and inline SVGs so the reader can scan in seconds. The Markdown version is text-first with ASCII fallbacks.

---

## Shared logical structure

**Information architecture is fold-by-fold** per DESIGN.md §4: a brief at the very top, scannable engaging items just below, an insights carousel in the middle, then heavier raw-data charts for users who want to dig in. Citations and caveats at the bottom.

| Zone           | #  | Section              | Required | Visual element (HTML)                                                |
|----------------|----|----------------------|----------|----------------------------------------------------------------------|
| **Brief**      | 01 | At a glance          | yes      | 2-3 sentence brief + hero valence + scale legend + quadrant chip + 4 stat tiles + day-badges row |
| **Highlights** | 02 | Highlights           | yes      | Compact grid of 3–5 bright-spot chip-cards (quote + date)            |
| **Insights**   | 03 | Insights             | yes      | **Horizontal carousel** of pattern cards (observation / details science / reframe) — scroll-snap, no JS |
| **Anchors**    | 04 | Worth trying         | yes      | Numbered list of 2–4 evidence-informed micro-experiments. Each anchored to a real citation. **Never prescriptive.** May render empty with explanatory line. |
| **Raw data** _(every chart carries `chart-source` caption with citation)_ | 05 | Emotional arc | yes | Twin sparklines (valence + arousal) with focusable data points |
|                | 06 | Affect map           | yes      | Russell scatter with jitter + density-bin fallback + per-quadrant tint |
|                | 07 | Dominant emotions    | yes      | Plutchik wheel + size-redundant outer dot ring + ranked bars + quotes |
|                | 08 | Day rhythm           | yes      | 24-hour horizontal strip with focusable hour cells                   |
|                | 09 | By project           | yes      | Diverging valence bars (centred at zero), opacity ∝ message count    |
|                | 10 | Word weather         | yes      | Typographic vocabulary block (Fraunces italic) — colour + weight + underline-on-negative |
| **Reference**  | 11 | Citations            | yes      | Compact reference list, per `citation_depth`                         |
|                | 12 | Caveats              | yes      | Footnote-style, muted                                                |

The IA reordering — Highlights up to §02, Insights carousel at §03, Worth trying at §04, heavy charts pushed below — was signalled by the user across 2026-05-13-1150 (IA) and 2026-05-13-1209 (science-based actions + provenance on every chart) and is now enforced by DESIGN.md §4. Twelve sections, numbered 01–12 contiguously. Renderers that emit sections in a different order, drop the Worth-trying header even when empty, or omit chart-source captions violate the contract.

Section headers are identical across both formats so users can compare side-by-side.

---

## Markdown template

```markdown
# Emotional Recap — {window} · {scope}

_Generated {timestamp}_

## At a glance
- **Vibe**: {one_line_summary}
- **Conversations**: {n_conversations} across {n_projects} project(s)
- **Messages analysed**: {n_messages}
- **Dominant quadrant**: {quadrant_name} (valence {valence_mean:+.2f}, arousal {arousal_mean:.2f})

## Emotional arc

Valence: {ascii_sparkline_valence}   range {valence_min:+.2f} → {valence_max:+.2f}
Arousal: {ascii_sparkline_arousal}   range {arousal_min:.2f} → {arousal_max:.2f}

Daily: {day_1_emoji} {day_1} · {day_2_emoji} {day_2} · {day_3_emoji} {day_3}    (🟡 calm-positive · 🟢 high-positive · 🟣 low-negative · 🔴 high-negative)

{2-3 sentence narrative of the arc}

## Affect map (Russell circumplex)

```
            arousal ↑ (activated)
   tense    │    excited
 ━━━━━━━━━━┿━━━━━━━━━━ ▶ valence
   tired    │    calm
            ↓ (low arousal)
```
Centroid: ({valence_mean:+.2f}, {arousal_mean:.2f}) — **{quadrant_name}**

## Dominant emotions

1. **{emotion_1}** ({pct_1}%) — "{example_1}"
2. **{emotion_2}** ({pct_2}%) — "{example_2}"
3. **{emotion_3}** ({pct_3}%) — "{example_3}"

## Day rhythm (24h, valence per hour)

```
00 ░░░░  06 ▒▒▒▒  12 ▓▓▓▓  18 ▓▓▓░  22 ░░  (lighter = more negative, darker = more positive)
```
Peak hour: {peak_hour}.  Dip hour: {dip_hour}.

## By project

- **{project_1}** ({n_msgs_1} msgs) — valence {v_1:+.2f}  {ascii_bar_1}
- **{project_2}** ({n_msgs_2} msgs) — valence {v_2:+.2f}  {ascii_bar_2}

## Word weather

Top emotional vocabulary this window:
{top_words_inline}   _(font weight in HTML scales with frequency)_

## Patterns I noticed

### {pattern_1_title}
**Observed:** {observation}
**Science:** {one sentence with citation}
**Worth asking:** {one reframing question}

### {pattern_2_title}
...

## Bright spots

⭐ {high-valence moment 1}
⭐ {high-valence moment 2}
⭐ {moment of gratitude / curiosity / accomplishment}

## Citations

{per citation_depth}

## Caveats

- Text-only analysis. Sarcasm, context, and intent are easy to miss.
- Frustration in debugging is engaged cognitive work, not distress (Csikszentmihalyi, 1990).
- Your felt sense overrides the analysis — this is a mirror, not a verdict, and not clinical advice.
```

**ASCII sparkline rule**: use unicode block characters `▁▂▃▄▅▆▇█` mapped from min→max of the daily means.

---

## HTML template (visual-first)

Single self-contained file. No external assets. All visuals as inline SVG.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Emotional Recap — {date}</title>
<style>
  :root {
    --bg: #faf8f5;
    --fg: #1f1f29;
    --muted: #6a6a78;
    --faint: #b5b3ac;
    --card: #ffffff;
    --border: #ece9e2;
    --accent: {swatch_color};        /* picked from dominant Russell quadrant */
    --sage: #7a9580;
    --rose: #c66b6b;
    --indigo: #6b6b8a;
    --gold: #d4a04a;
    --grid: #e7e3da;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #16161e;
      --fg: #ece9e2;
      --muted: #8f8d96;
      --faint: #4d4d58;
      --card: #1f1f2a;
      --border: #2a2a37;
      --grid: #2a2a37;
    }
  }
  * { box-sizing: border-box; }
  html { -webkit-font-smoothing: antialiased; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
    font-feature-settings: "ss01", "cv11", "tnum";
    background: var(--bg);
    color: var(--fg);
    line-height: 1.6;
    font-size: 16px;
    font-weight: 400;
  }
  .wrap { max-width: 760px; margin: 0 auto; padding: 56px 24px 96px; }

  /* ── Eyebrow + hero ───────────────────────────── */
  .eyebrow {
    font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; margin-bottom: 18px;
  }
  .hero { display: flex; align-items: flex-end; gap: 24px; flex-wrap: wrap; margin-bottom: 8px; }
  .hero-num {
    font-size: 88px; font-weight: 200; letter-spacing: -0.04em; line-height: 0.9;
    font-feature-settings: "tnum";
  }
  .hero-num .sign { color: var(--accent); font-weight: 300; }
  .hero-label {
    font-size: 13px; letter-spacing: 0.06em; text-transform: uppercase;
    color: var(--muted); margin-top: 12px;
  }
  .hero-chip {
    display: inline-flex; align-items: center; gap: 10px;
    background: color-mix(in srgb, var(--accent) 12%, transparent);
    border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
    border-radius: 999px; padding: 8px 16px;
    font-size: 13px; font-weight: 500;
  }
  .hero-chip .dot {
    width: 10px; height: 10px; border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 18%, transparent);
  }
  .vibe { font-size: 22px; font-weight: 400; margin: 28px 0 8px; letter-spacing: -0.01em; }
  .timestamp { font-size: 13px; color: var(--muted); }

  /* ── Section heads ────────────────────────────── */
  h2 {
    font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
    font-weight: 600; color: var(--muted);
    margin: 56px 0 14px; border-top: 1px solid var(--border); padding-top: 28px;
  }
  h2 .num { display: inline-block; width: 22px; color: var(--faint); font-weight: 500; }
  h3 { font-size: 16px; font-weight: 600; margin: 22px 0 6px; letter-spacing: -0.005em; }

  /* ── Stats grid ───────────────────────────────── */
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 12px 0 4px; }
  .stat { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
  .stat .k { font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
  .stat .v { font-size: 26px; font-weight: 300; margin-top: 6px; font-feature-settings: "tnum"; letter-spacing: -0.02em; }

  /* ── Sparkline card ──────────────────────────── */
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 22px 24px; margin: 12px 0; }
  .card-row { display: flex; gap: 28px; align-items: center; flex-wrap: wrap; }
  .spark { display: block; width: 100%; height: 80px; }
  .spark-label { font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); font-weight: 600; margin: 14px 0 4px; }
  .spark-range { font-size: 12px; color: var(--muted); font-feature-settings: "tnum"; }

  /* ── Daily badges row ────────────────────────── */
  .badges { display: flex; gap: 12px; margin: 18px 0 4px; flex-wrap: wrap; }
  .badge { display: flex; flex-direction: column; align-items: center; min-width: 56px; }
  .badge .swatch { width: 36px; height: 36px; border-radius: 50%; box-shadow: 0 0 0 4px color-mix(in srgb, currentColor 12%, transparent); }
  .badge .day { font-size: 11px; color: var(--muted); margin-top: 8px; letter-spacing: 0.04em; }

  /* ── Plutchik wheel + ranked bars ────────────── */
  .emotions { display: grid; grid-template-columns: 220px 1fr; gap: 24px; align-items: center; }
  @media (max-width: 600px) { .emotions { grid-template-columns: 1fr; } }
  .wheel { width: 220px; height: 220px; }
  .ebar { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
  .ebar .name { width: 88px; font-size: 13px; font-weight: 500; }
  .ebar .track { flex: 1; height: 8px; background: var(--grid); border-radius: 4px; overflow: hidden; }
  .ebar .fill { height: 100%; background: var(--accent); border-radius: 4px; }
  .ebar .pct { font-size: 12px; color: var(--muted); width: 36px; text-align: right; font-feature-settings: "tnum"; }

  /* ── Quote ───────────────────────────────────── */
  .quote { font-style: italic; color: var(--muted); border-left: 2px solid var(--border); padding: 4px 0 4px 14px; margin: 10px 0; font-size: 14px; }

  /* ── 24h rhythm strip ────────────────────────── */
  .rhythm { display: grid; grid-template-columns: repeat(24, 1fr); gap: 2px; margin: 16px 0 8px; height: 36px; }
  .rhythm .h { background: var(--grid); border-radius: 3px; }
  .rhythm-axis { display: grid; grid-template-columns: repeat(24, 1fr); font-size: 10px; color: var(--muted); font-feature-settings: "tnum"; }
  .rhythm-axis span { text-align: center; }

  /* ── By-project bars ─────────────────────────── */
  .pbar { display: grid; grid-template-columns: 140px 1fr 80px; gap: 12px; align-items: center; margin: 8px 0; }
  .pbar .pname { font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .pbar .ptrack { position: relative; height: 22px; background: var(--grid); border-radius: 4px; overflow: hidden; }
  .pbar .pfill { position: absolute; top: 0; bottom: 0; }
  .pbar .pmeta { font-size: 12px; color: var(--muted); text-align: right; font-feature-settings: "tnum"; }

  /* ── Word weather ────────────────────────────── */
  .words {
    line-height: 1.9; padding: 8px 0;
    font-family: "Iowan Old Style", "Charter", Georgia, serif;
  }
  .w {
    display: inline-block; margin: 0 8px 4px 0;
    transition: opacity 0.2s;
  }
  .w.pos { color: var(--sage); }
  .w.neg { color: var(--rose); }
  .w.neu { color: var(--muted); }

  /* ── Patterns ────────────────────────────────── */
  .pattern { margin: 18px 0; padding: 18px 22px; border-left: 3px solid var(--accent); background: color-mix(in srgb, var(--accent) 5%, transparent); border-radius: 0 10px 10px 0; }
  .pattern h3 { margin-top: 0; }
  .pattern .label { font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); font-weight: 600; margin-top: 10px; }
  .pattern .label::before { content: "▸ "; color: var(--accent); }

  /* ── Bright spots ────────────────────────────── */
  .bright {
    background: color-mix(in srgb, var(--sage) 10%, transparent);
    border: 1px solid color-mix(in srgb, var(--sage) 25%, transparent);
    border-radius: 14px; padding: 20px 26px; margin: 18px 0;
  }
  .bright h2 { margin: 0 0 12px; border: none; padding: 0; color: var(--sage); }
  .bright li { list-style: none; padding: 4px 0 4px 28px; position: relative; }
  .bright li::before {
    content: "★"; position: absolute; left: 0; color: var(--sage);
    font-size: 14px;
  }
  .bright ul { padding: 0; margin: 0; }

  /* ── Citations & caveats ─────────────────────── */
  .citations { font-size: 12.5px; color: var(--muted); }
  .citations p { margin: 6px 0; }
  .caveats { font-size: 12.5px; color: var(--muted); border-top: 1px solid var(--border); padding-top: 24px; margin-top: 56px; }

  a { color: var(--fg); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }
</style>
</head>
<body>
<div class="wrap">

  <!-- ─── Eyebrow + hero ───────────────────────── -->
  <div class="eyebrow">Emotional recap · {window} · {scope}</div>
  <div class="hero">
    <div>
      <div class="hero-num"><span class="sign">{valence_sign}</span>{valence_abs}</div>
      <div class="hero-label">Mean valence · arousal {arousal_mean}</div>
    </div>
    <div class="hero-chip"><span class="dot"></span>{quadrant_name}</div>
  </div>
  <p class="vibe">{vibe_one_liner}</p>
  <p class="timestamp">{timestamp_human}</p>

  <!-- ─── 01 At a glance ───────────────────────── -->
  <h2><span class="num">01</span> At a glance</h2>
  <div class="stats">
    <div class="stat"><div class="k">Conversations</div><div class="v">{n_conversations}</div></div>
    <div class="stat"><div class="k">Messages</div><div class="v">{n_messages}</div></div>
    <div class="stat"><div class="k">Projects</div><div class="v">{n_projects}</div></div>
    <div class="stat"><div class="k">Volatility</div><div class="v">{volatility_label}</div></div>
  </div>

  <!-- ─── 02 Emotional arc ─────────────────────── -->
  <h2><span class="num">02</span> Emotional arc</h2>
  <div class="card">
    <div class="spark-label">Valence · daily mean</div>
    <svg class="spark" viewBox="0 0 600 80" preserveAspectRatio="none">{svg_polyline_valence}</svg>
    <div class="spark-range">{valence_min} → {valence_max}</div>

    <div class="spark-label">Arousal · daily mean</div>
    <svg class="spark" viewBox="0 0 600 80" preserveAspectRatio="none">{svg_polyline_arousal}</svg>
    <div class="spark-range">{arousal_min} → {arousal_max}</div>

    <div class="badges">{daily_badge_blocks}</div>
    <p class="muted" style="margin-top:14px;">{arc_narrative}</p>
  </div>

  <!-- ─── 03 Affect map (Russell scatter) ──────── -->
  <h2><span class="num">03</span> Affect map</h2>
  <div class="card">
    <svg viewBox="0 0 320 320" width="100%" style="max-width:320px; display:block; margin:0 auto;">
      <!-- Quadrant fills (faint) -->
      <rect x="160" y="0"   width="160" height="160" fill="color-mix(in srgb, {gold}  8%, transparent)"/>
      <rect x="0"   y="0"   width="160" height="160" fill="color-mix(in srgb, {rose}  8%, transparent)"/>
      <rect x="0"   y="160" width="160" height="160" fill="color-mix(in srgb, {indigo} 8%, transparent)"/>
      <rect x="160" y="160" width="160" height="160" fill="color-mix(in srgb, {sage}  8%, transparent)"/>
      <!-- Axes -->
      <line x1="0"   y1="160" x2="320" y2="160" stroke="var(--border)" stroke-width="1"/>
      <line x1="160" y1="0"   x2="160" y2="320" stroke="var(--border)" stroke-width="1"/>
      <!-- Axis labels -->
      <text x="160" y="14"   text-anchor="middle" font-size="10" fill="var(--muted)" letter-spacing="1">ACTIVATED</text>
      <text x="160" y="314"  text-anchor="middle" font-size="10" fill="var(--muted)" letter-spacing="1">CALM</text>
      <text x="6"   y="164"  font-size="10" fill="var(--muted)" letter-spacing="1">UNPLEASANT</text>
      <text x="314" y="164"  text-anchor="end" font-size="10" fill="var(--muted)" letter-spacing="1">PLEASANT</text>
      <!-- Quadrant words -->
      <text x="240" y="80"  text-anchor="middle" font-size="11" fill="var(--muted)">excited</text>
      <text x="80"  y="80"  text-anchor="middle" font-size="11" fill="var(--muted)">tense</text>
      <text x="80"  y="248" text-anchor="middle" font-size="11" fill="var(--muted)">tired</text>
      <text x="240" y="248" text-anchor="middle" font-size="11" fill="var(--muted)">calm</text>
      <!-- Scatter dots (one per analysed message) -->
      {svg_scatter_dots}
      <!-- Centroid -->
      <circle cx="{centroid_x}" cy="{centroid_y}" r="7" fill="var(--accent)" stroke="var(--bg)" stroke-width="3"/>
    </svg>
    <p class="muted" style="text-align:center; margin-top:6px; font-size:12px;">Each dot is one message. Filled circle = centroid.</p>
  </div>

  <!-- ─── 04 Dominant emotions ─────────────────── -->
  <h2><span class="num">04</span> Dominant emotions</h2>
  <div class="card">
    <div class="emotions">
      <svg class="wheel" viewBox="0 0 200 200">
        <!-- 8 Plutchik spokes; opacity scales with frequency -->
        {svg_plutchik_spokes}
        <circle cx="100" cy="100" r="22" fill="var(--card)" stroke="var(--border)"/>
        <text x="100" y="105" text-anchor="middle" font-size="11" fill="var(--muted)">PLUTCHIK</text>
      </svg>
      <div>
        {emotion_bar_blocks}
      </div>
    </div>
    <div style="margin-top:18px;">
      <div class="quote">"{example_1}" — <span class="muted">{emotion_1}</span></div>
      <div class="quote">"{example_2}" — <span class="muted">{emotion_2}</span></div>
      <div class="quote">"{example_3}" — <span class="muted">{emotion_3}</span></div>
    </div>
  </div>

  <!-- ─── 05 Day rhythm ────────────────────────── -->
  <h2><span class="num">05</span> Day rhythm</h2>
  <div class="card">
    <div class="rhythm">{rhythm_hour_cells}</div>
    <div class="rhythm-axis">
      <span>0</span><span></span><span></span><span></span><span></span><span></span>
      <span>6</span><span></span><span></span><span></span><span></span><span></span>
      <span>12</span><span></span><span></span><span></span><span></span><span></span>
      <span>18</span><span></span><span></span><span></span><span></span><span></span>
    </div>
    <p class="muted" style="font-size:12.5px; margin-top:14px;">
      Peak <strong style="color:var(--fg);">{peak_hour}</strong> · Dip <strong style="color:var(--fg);">{dip_hour}</strong>.
      Cells shaded by mean valence for that hour across the window.
    </p>
  </div>

  <!-- ─── 06 By project ────────────────────────── -->
  <h2><span class="num">06</span> By project</h2>
  <div class="card">
    {project_bar_blocks}
    <!-- each block:
      <div class="pbar">
        <div class="pname">{slug}</div>
        <div class="ptrack"><div class="pfill" style="left:{left}%; width:{width}%; background:{color};"></div></div>
        <div class="pmeta">{n_msgs} msgs · {valence:+.2f}</div>
      </div>
    -->
  </div>

  <!-- ─── 07 Word weather ──────────────────────── -->
  <h2><span class="num">07</span> Word weather</h2>
  <div class="card words">
    {word_weather_spans}
    <!-- each:
      <span class="w {pos|neg|neu}" style="font-size:{size}px; font-weight:{weight};">{word}</span>
      sizes: min 14px → max 38px, mapped from frequency
      weights: 300 / 400 / 500 / 600 by quartile
    -->
  </div>
  <p class="muted" style="font-size:12px; margin-top:8px;">Sage = positive · rose = negative · grey = neutral. Size = frequency this window.</p>

  <!-- ─── 08 Patterns I noticed ────────────────── -->
  <h2><span class="num">08</span> Patterns I noticed</h2>
  <div class="pattern">
    <h3>{pattern_1_title}</h3>
    <p>{observation_1}</p>
    <div class="label">Science</div>
    <p class="muted">{science_1}</p>
    <div class="label">Worth asking</div>
    <p>{reframe_1}</p>
  </div>
  <!-- repeat -->

  <!-- ─── 09 Bright spots ──────────────────────── -->
  <div class="bright">
    <h2>★ Bright spots</h2>
    <ul>
      <li>{bright_1}</li>
      <li>{bright_2}</li>
      <li>{bright_3}</li>
    </ul>
  </div>

  <!-- ─── 10 Citations ─────────────────────────── -->
  <h2><span class="num">10</span> Citations</h2>
  <div class="citations">
    {citation_list_html}
  </div>

  <!-- ─── 11 Caveats ───────────────────────────── -->
  <div class="caveats">
    <p>Text-only analysis — sarcasm, context, and intent are easy to miss.</p>
    <p>Frustration during debugging is engaged cognitive work, not distress (Csikszentmihalyi, 1990).</p>
    <p>Your felt sense overrides the analysis. This is a mirror, not a verdict — and not clinical advice. If you're struggling, talk to a professional.</p>
  </div>

</div>
</body>
</html>
```

---

## SVG renderer notes (per visualisation)

### Sparklines (section 02)

Renderer contract: each SVG gets `role="img"`, `<title>`, `<desc>` (DESIGN.md §7 ¶1).

1. Bucket data points by day. Compute daily mean.
2. Map to SVG `viewBox="0 0 600 80"`:
   - `x = (day_index / max(n_days-1, 1)) * 580 + 10`
   - Valence (`[-1,1]`): `y = 40 - (mean * 30)` (centred at 40, range ±30)
   - Arousal (`[0,1]`):  `y = 70 - (mean * 60)`
3. Emit `<polyline fill="none" stroke="var(--{q}-line)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" points="x1,y1 x2,y2 …"/>` where `{q}` is the dominant-quadrant token (`q1` / `q2` / `q3` / `q4`).
4. Wrap each data point in a focusable group (audit H2):
   ```html
   <g tabindex="0" role="button" aria-label="{date}: valence {value}">
     <circle cx="x" cy="y" r="3" fill="var(--{q}-line)"/>
     <circle cx="x" cy="y" r="12" fill="transparent"/>  <!-- 24px hit area -->
   </g>
   ```
5. Zero-line for valence: `<line x1="10" y1="40" x2="590" y2="40" stroke="var(--rule)" stroke-dasharray="3,3"/>`
6. **Sparse-data fallback** (audit M11): if `n_days < 2`, render `<text x="300" y="40" text-anchor="middle" fill="var(--ink-soft)" font-size="13">Not enough days for a trend yet — check back after another day.</text>` instead.
7. Range label below the SVG: `Valence range: {min} → {max} · scale −1 to +1` (audit M7 — every number gets a scale).

### Daily badge row (section 02)
For each day in the window:
```html
<div class="badge" style="color: {day_color};">
  <div class="swatch" style="background: {day_color};"></div>
  <div class="day">{day_short}</div>
</div>
```
`day_color` = quadrant colour for that day's centroid (sage / gold / indigo / rose).

### Russell scatter (section 03)

Renderer contract: this is the chart the 2026-05-13 audit broke (C1). The rules below are the fixes — they are non-negotiable.

- 320×320 viewBox. SVG wrapper: `role="img"` + `<title>` + `<desc>` describing the centroid quadrant and (if active) the density-bin mode.
- Quadrant fills use tokens (not hex): `<rect ... fill="var(--q1-fill)"/>` etc. (audit M3 — fills now adapt to dark mode).

**Per-dot mode (default)**:
1. For each analysed message, compute base coordinates:
   - `cx = 160 + (valence * 150)` → range `[10, 310]`
   - `cy = 235 - (arousal * 150)` → range `[85, 235]` (high arousal goes up)
2. **Apply jitter** (audit C1): add `random_uniform(-6, 6)` to both `cx` and `cy` deterministically — use a stable hash of `{ts}+{conversation_id}` as the seed so re-renders are identical.
3. **Per-message quadrant tint**: each dot uses `var(--{q}-line)` for *its own* quadrant, not a single global accent. This couples colour to position so colour reinforces rather than encodes alone.
4. **Size variation**: `r=2` for low-confidence reads (short messages, ambiguous), `r=3` for normal, `r=4` for high-confidence emotionally-charged messages. Two redundant signals (colour + size).
5. Wrap each dot in `<g tabindex="0" aria-label="…">` — focusable for keyboard users (audit H2).
6. **Render cap**: 200 dots maximum. If `n_messages > 200`, deterministically subsample (every `ceil(n/200)`-th message) and emit caption `{rendered} of {total} messages plotted`.

**Density-bin mode (auto-triggered)**:
After jitter, compute per-cell density on a 10×10 grid. If any single cell holds ≥85% of points, **switch encoding entirely**:
1. Drop the per-dot rendering.
2. Render a 10×10 grid of `<rect>` cells; each cell's `fill-opacity = messages_in_cell / max_cell_count`, fill is the dominant-quadrant line token.
3. Show three quartile rings (25 / 50 / 75 percentile by distance from centroid) instead of individual dots.
4. Emit caption: `Density mode — {n} messages clustered too tightly for a per-dot view. Cell shade ∝ count.`

**Centroid (both modes)**: `<circle cx="{cx}" cy="{cy}" r="7" fill="var(--{q}-line)" stroke="var(--bg)" stroke-width="3"/>` with `<title>Centroid: valence {v}, arousal {a}</title>`.

### Plutchik wheel (section 04)
- 200×200 viewBox.
- 8 spokes at 45° intervals (joy=top, anticipation=top-right, anger=right, disgust=bottom-right, sadness=bottom, surprise=bottom-left, fear=left, trust=top-left).
- For each spoke, render a wedge: `<path d="M100,100 L{x1},{y1} A78,78 0 0,1 {x2},{y2} Z" fill="{plutchik_color[emotion]}" opacity="{frequency_pct/100}"/>`
- Plutchik canonical palette:
  - joy `#f7c548`, trust `#8fc7a4`, fear `#5f8a76`, surprise `#5d97c9`, sadness `#7191c4`, disgust `#9367a8`, anger `#d57171`, anticipation `#e89a5d`
- Outer ring stroke + emotion labels in 9px around the perimeter (optional, skip if cluttered).

### Emotion ranked bars (section 04)
For each of the top 5 emotions:
```html
<div class="ebar">
  <span class="name">{emotion}</span>
  <span class="track"><span class="fill" style="width: {pct}%; background: {plutchik_color[emotion]};"></span></span>
  <span class="pct">{pct}%</span>
</div>
```

### 24-hour rhythm strip (section 05)
24 cells, one per hour. For each hour:
- Mean valence across all messages in that hour bucket (over the window).
- Background colour: interpolate sage (positive) → grid-grey (neutral) → rose (negative). If no messages in hour, leave at `--grid`.
```html
<div class="h" style="background: {hour_color};" title="{hour}h · v {v:+.2f}"></div>
```
Cell colour mapping function:
- `v >= 0.3`  → `#7a9580` (sage)
- `v >= 0.0`  → `color-mix(sage 50%, grid)`
- `v >= -0.3` → `color-mix(rose 50%, grid)`
- else        → `#c66b6b` (rose)

### Per-project bars (section 06)
For each project (sorted by message count, desc):
- Bar centred at 50% (zero valence).
- If `valence >= 0`: fill grows right from 50%. `left=50%, width=valence*50%, background=var(--sage)`
- If `valence < 0`: fill grows left from 50%. `left=(50 + valence*50)%, width=|valence|*50%, background=var(--rose)`
- Bar opacity: scale by `min(n_msgs / max_n_msgs, 1)` so noisy projects dominate visually.

### Word weather (section 07)
1. Tokenise all user messages. Lowercase, strip punctuation, drop stopwords.
2. **Run the anonymisation pipeline** (DESIGN.md §7 — three layers):
   - Deny-list match against `~/.claude/skills/emotional-recap/anonymise.deny` → drop the token entirely from word weather (it carries no emotional signal).
   - Heuristic: drop tokens matching `[A-Z][a-z]{2,}` unless they're in the common-words whitelist.
   - Structural: drop tokens >20 chars, containing `/` / `.` / `_` patterns, or matching paths.
3. Tag each remaining word as `pos` / `neg` / `neu` using the NRC Emotion Lexicon categories from `frameworks.md`. Words not in any lexicon → `neu`, but only include `neu` words that appear ≥3× and aren't stopwords.
4. Take top 30-40 by frequency.
5. Map frequency to:
   - `font-size`: linear `14px → 36px` across min→max frequency
   - `font-weight`: `400 / 500` by polarity (neutral gets 400; pos / neg get 500 for emphasis)
6. **Polarity rendering** (audit H4 — non-colour redundancy):
   - Positive: `color: var(--q4-ink); font-weight: 500;`
   - Negative: `color: var(--q2-ink); font-weight: 500; text-decoration: underline; text-decoration-thickness: 1px;`
   - Neutral: `color: var(--ink); font-weight: 400;`
7. Render each as:
   ```html
   <span class="w {pos|neg|neu}" style="font-size:{px}px;"
         aria-label="{word}, {polarity}, {frequency} occurrences">{word}</span>
   ```
   The `aria-label` carries polarity textually so screen readers don't depend on colour.

---

## Accent swatch / dominant-quadrant binding

Based on the dominant Russell quadrant (centroid of all message points):

| Quadrant | Condition                                | Tokens (DESIGN.md §3)                       |
|----------|------------------------------------------|---------------------------------------------|
| Q1       | valence ≥ 0, arousal ≥ 0.5 (excited)     | `--q1-fill` / `--q1-ink` / `--q1-line`      |
| Q2       | valence < 0, arousal ≥ 0.5 (tense)       | `--q2-fill` / `--q2-ink` / `--q2-line`      |
| Q3       | valence < 0, arousal < 0.5 (tired)       | `--q3-fill` / `--q3-ink` / `--q3-line`      |
| Q4       | valence ≥ 0, arousal < 0.5 (calm)        | `--q4-fill` / `--q4-ink` / `--q4-line`      |

The renderer adds a single CSS rule mapping the dominant quadrant to convenience aliases:
```css
:root {
  --accent:      var(--{q}-line);
  --accent-ink:  var(--{q}-ink);
  --accent-bg:   var(--{q}-fill);
}
```

This keeps the per-section quadrant tokens explicit (audit M9 — different chart families bind to their own appropriate quadrant) while letting the hero chip and primary accent default to the dominant.

---

## Anonymisation rule (applies to quotes + word weather)

**Three-layer pipeline** (DESIGN.md §7). Runs in this order before any user text is emitted:

1. **Layer 1 — Deny-list** (mandatory). Load `~/.claude/skills/emotional-recap/anonymise.deny`. For each entry, case-insensitive substring match; replace with the entry's category tag (e.g. `<client>`, `<project>`, `<person>`). Update the deny-list as new sensitive terms appear.
2. **Layer 2 — Heuristic strip**. Tokens matching `[A-Z][a-z]{2,}` are redacted to `<name>` unless they're in a small whitelist of common capitalised words (e.g. "I", "Tuesday", "Monday", "January", "OK", "Claude", "GitHub" — keep the whitelist tight).
3. **Layer 3 — Structural strip**. File paths, URLs, secret-shaped strings, code blocks (containing triple backticks or `function`/`class`/`const`/`def`/`import`) → replace with a paraphrase (e.g. "a debugging exchange about the build pipeline"). Truncate excerpts to ≤120 chars with trailing `…`.

**Post-pipeline guard**: if a quote was reduced to <40% of its original length after anonymisation, **drop the quote entirely** and substitute a paraphrase. A heavily-redacted quote `"ok let's go through <project> for <client> client -<project> so we can…"` is less useful than `"a planning conversation about a client project"`.

**Never** quote anything that mentions other people by name (even if not in the deny-list — let the heuristic catch them).

The report is local to the user, but anonymisation keeps it safe to screenshot or share.

---

## Changelog

- **2026-05-13 v4** — added §04 **Worth trying** (evidence-informed micro-experiments anchored to real citations; never prescriptive — language guardrails in DESIGN.md §6). Every chart-bearing section (§05–§10) now emits a `.chart-source` caption naming the framework + citation per DESIGN.md §7 provenance table. Renderer self-audit grew to 14 items (added 13 chart-provenance, 14 worth-trying-integrity). Citations.md gained 6 new refs for action anchoring (Ariga & Lleras 2011, Leroy 2009, Lieberman et al. 2007, Mauss et al. 2011, Sonnentag & Fritz 2007, Killingsworth & Gilbert 2010). 12 sections, numbered 01–12.
- **2026-05-13 v3** — information architecture rebuilt per user feedback (1150 session). Fold-by-fold: brief → highlights → insights → raw data → reference. Highlights moved from §09 to §02 (compact chip strip). Patterns reshaped into an **Insights carousel** at §03 with CSS scroll-snap, no JS, `<details>` progressive disclosure, full source-order accessibility. Raw-data charts pushed below the carousel for users who want to dig in. New brief paragraph at top of §01.
- **2026-05-13 v2** — audit fixes folded in across sparklines (focusable points, scale labels, sparse-data fallback), Russell scatter (jitter + density-bin + per-quadrant tint + size variation + 200-cap), word weather (three-layer anonymisation, underline for negatives, aria-label polarity), accent binding (tokens instead of hex), and anonymisation pipeline (deny-list + heuristic + post-pipeline guard). DESIGN.md introduced as canonical source for tokens.
- **2026-05-13 v1** — initial structure with 11 sections, two sparklines, single accent.


---

## Typographic principles

- **One display number per report.** The hero valence (88px, weight 200) is the only oversized element. Everything else stays in a 10-26px range.
- **Tabular figures everywhere numbers live** (`font-feature-settings: "tnum"`). Stats must align.
- **Eyebrows are uppercase, 11px, letter-spacing 0.12-0.16em, weight 600.** Used for section heads and meta-labels.
- **Body weight is 400.** Italics reserved for quotes. Bold (600) reserved for emphasis inside paragraphs.
- **Word weather uses a serif** (Iowan Old Style / Charter / Georgia) for tactile contrast against the rest of the report's sans-serif. It's the one moment of personality.
- **Section divisions are top borders, not bottom.** A 1px line above each `h2` plus generous padding-top creates rhythm without boxing every block.
- **Numbered sections.** The faint `01 / 02 / …` prefix on each `h2` gives scannability and signals "this is structured, not arbitrary."
