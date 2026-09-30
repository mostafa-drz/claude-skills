---
name: which-chart
description: >-
  Recommends the right chart for your data and use case: reads data or screenshots, asks up to 3 questions, then gives one pick and alternatives drawn from your rows. For "which chart should I use?"
metadata:
  side_effects: false
  trigger: "Sharing data, screenshots or a use case and asking which chart or visualization fits, e.g. 'how should I show sentiment over time on my dashboard?'"
  tags: "data-visualization, charts, dashboard, chart-selection, vega-lite, sentiment, design, accessibility, desktop"
---

# Which chart

You have data and a question for it, say brand sentiment over time for an engagement
dashboard, and a dozen chart types that could plausibly show it. This skill reads what you
share, asks only what it can't work out, and answers with **one pick**, the alternatives
that win in other situations, and what to avoid. Every option is drawn from your own rows,
so you judge the real thing, not a thumbnail from a gallery.

It starts automatically on a matching request: "which chart for this?", "how should I
visualize sentiment over time?", or data and screenshots shared with that intent.

One reference, **read it every run**: [`choosing.md`](./references/choosing.md) (the
brief, the matching rules, colour, anti-patterns, and the source list to cite). The data
shape is [`evals/example-reco.json`](./evals/example-reco.json), a complete worked example.

---

## The flow

```
Chart progress:
- [ ] 1. Read what was shared: data, screenshots, use case
- [ ] 2. Ask only what's missing (one round, ≤3 questions, each with a default)
- [ ] 3. Match: relationship → candidates → one pick, 1–3 alternatives, what to avoid
- [ ] 4. Write reco.json → validate → page
- [ ] 5. Close in two lines
```

### 1. Read what was shared

Work out the four parts of the brief (the checklist in [`choosing.md`](./references/choosing.md#the-brief)):
**the question** the viewer must answer at a glance, **the audience**, **the surface**
(tile, panel, report, slide) and **the data**.

- **Data files or pasted rows.** Profile them with code: columns, types, the grain (one row
  per what?), cardinality of each category, time span and interval, gaps, and whether
  values are counts or already shares. Aggregate to the grain the chart will show; the page
  takes at most 1,500 rows.
- **Screenshots.** Say what you see: the current chart, its fields, its problems, the look
  of the surrounding dashboard. If a screenshot shows data, read values from it only when
  they're legible, and mark them as read from an image. Each goes in `screenshots` as
  *seen* and *verdict*.
- **Only a description.** Build illustrative rows with the right shape (same fields,
  realistic ranges, one visible event so differences between charts show). Set
  `illustrative: true`. The page then says plainly that the trend is made up.

**Never read a trend into illustrative data**, and never present values read off a blurry
screenshot as exact.

### 2. Ask only what's missing

**The question comes first**: it decides the chart more than the data does. When the
request and the shared material settle it, don't ask. Otherwise ask **one round, at most
three questions, each with a proposed default**, so "go" answers them all. Use plain text:
a question tool may not exist on this surface. The usual three:

1. **The one question** the viewer must answer at a glance. Offer 2–4 readings of their
   use case, for sentiment over time: *is it getting better or worse · how loud and how
   it splits · the balance right now · compare brands*.
2. **The surface**: small tile, full panel, report or slide.
3. **The stack**, only when they'll build it: React/Recharts, D3, a BI tool… (default:
   Vega-Lite spec, portable).

Record any default that stood in for an answer in `brief.assumed`; the page marks it.
**Never re-ask what the user already said**, and never ask about colours, titles or
anything you can decide.

### 3. Match

Follow [`choosing.md`](./references/choosing.md). In short:

1. Name the **relationship** (FT Visual Vocabulary: change over time, part-to-whole,
   deviation…). Most real questions are one, sometimes two.
2. Shortlist the forms that show it, then **rank by the question**, using the perceptual
   ranking: position on a common scale beats length, which beats angle and area.
3. Filter by **data fit** (number of categories, points, ordered or not, counts or
   shares) and **surface** (a tile fits one line, not two panels).
4. Choose **one pick** and 1–3 **alternatives**, each with *choose this if…* so the user
   knows when to switch. List up to three things to **avoid**, preferring the ones they're
   likely to reach for (the chart in their screenshot, a pie per period, a dual axis).

Every reason cites a source from [`choosing.md`](./references/choosing.md#sources) by
number. Where research disagrees (for example where *neutral* goes in a sentiment chart),
say so and pick for their question rather than hiding the disagreement. Every option also
gets 1–3 honest **costs**.

### 4. Build the page

Write `reco.json` in the conversation's language (set `lang`; add `labels` for the page
headings if it isn't English). Each option's `spec` is a **Vega-Lite v6 spec** reading
`"data": {"name": "table"}`. The page supplies the rows, so don't inline them. Start from
the tested patterns in [`choosing.md`](./references/choosing.md#vega-lite-patterns), and
use the colours there: the page steps them for dark mode by itself.

```bash
python3 scripts/validate_reco.py reco.json
```

It exits non-zero with a fix per error: exactly one pick, fields that exist, citations that
resolve, illustrative data labelled, no dual axes or pies over time. **Fix and re-run until
it passes.** Standard library only.

**Write the page once.** With artifacts available, create the HTML artifact directly from
[`assets/page-template.html`](./assets/page-template.html), copied unchanged except for
the JSON inside `<script type="application/json" id="reco-data">`. Get that JSON from
`python3 scripts/render_page.py reco.json --data`, which prints it with `</` escaped, and
paste it as printed. Without artifacts, run `python3 scripts/render_page.py reco.json
reco.html`, share the file, and give the pick and its reasons as text.

The page draws every option with Vega-Lite from a CDN, follows light and dark mode, works
on a phone, and has **Copy Vega-Lite spec**, **Show spec** and **Show table** on each
option. If the scripts can't load, it shows each spec instead.

### 5. Close

**Two lines at most**: the pick and the one thing that would change it ("if volume matters
as much as mood, take the two-panel option"), then an offer: port the pick to their stack,
or try it on their real data if this run used illustrative rows.

---

## Follow-ups

- **"Show it in Recharts / D3 / Power BI…"**: port the pick into their stack as code,
  keeping the colours, order and transforms. Say what doesn't carry over.
- **"What about a ___?"**: evaluate it against the same brief. If it wins, it becomes the
  pick; if not, say why in one or two lines and add it to `avoid` if they're likely to
  build it anyway.
- **New data or a changed question**: edit `reco.json` and re-render the same artifact.
  State what changed.

## Honesty rules

- **Cite or don't claim.** A reason without a source from the list is an opinion; say so,
  or drop it. Never invent a study or a statistic.
- **One pick.** "It depends" is only an answer with the dependency named, as *choose this
  if*.
- **Illustrative is illustrative.** Made-up rows show a form, never a finding.
- **The page shows your data, not a finished chart.** Axis titles, formats and sizes are a
  starting point for their build.

## Privacy

Shared data can be customer or company data. Keep only the columns the chart needs, and
aggregate before putting rows in the page. Never put personal data (names, emails,
handles, message text) in `rows`: count it, don't list it. The artifact is private unless
the user shares it; if they ask to share, say in one line what data it contains.

---

## Conventions

**`help`**: what this does (one sentence), what to share (data, screenshots, a sentence
about the use case), and the follow-ups: "port it to Recharts", "what about a ___?".

**`config`**: defaults for this conversation, asked in one round: default stack, surface,
question count (0–3). Desktop skills can't keep settings between conversations. To make a
default permanent, edit **Configuration** below and re-upload. Say so rather than implying
the choice will be remembered.

**`reset`**: drops this conversation's config and returns to the defaults below. It never
touches a page you already have.

**Tone**: a sharp colleague who has built a lot of dashboards: direct, specific, no
lecture. One line to open, the page, two lines to close.

## Configuration

Edit these, re-zip and re-upload to change the defaults.

- questions: at most 3, one round, each with a default; none when the brief is settled
- alternatives: 1–3; avoid: up to 3
- spec: Vega-Lite v6; stack for ports: ask only if the user will build it
- rows on the page: at most 1,500, aggregated to the chart's grain
- colours: the palette in `choosing.md` (sentiment: blue positive, grey neutral, red
  negative)
- language: the conversation's
