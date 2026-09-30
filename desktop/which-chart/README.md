# which-chart

Share your data, a screenshot or a sentence about your use case. Get the chart that fits,
drawn from your own rows, with the reasons and the alternatives.

> **Status: draft (v0).** Built from the sources listed below. The scripts and page were
> tested locally in Chrome: light and dark mode, 1200px and 390px wide, offline, and with
> hostile input. It hasn't yet been run end to end inside Claude Desktop. The six
> scenarios in [`evals/evals.json`](./evals/evals.json) are the acceptance test for that
> first run.

## The problem

"How should I show sentiment over time on this dashboard?" has a dozen plausible answers,
including a donut per month, a stacked area, three lines, a net score or diverging bars. The
usual ways to decide are a gallery of thumbnails that aren't your data, or whatever the
chart library puts first.

| what usually goes wrong | how this skill handles it |
|---|---|
| Picking by looks, from a gallery | Starts from **the question** the viewer must answer, then the relationship (FT Visual Vocabulary), then perception (Cleveland & McGill) |
| A long questionnaire before any help | **At most three questions, one round, each with a default.** None when what you shared already answers them |
| "It depends" with no answer | **One pick**, plus alternatives that each say *choose this if…* |
| Advice you can't check | Every reason **cites a source** (or is marked as judgement), and the validator rejects anything else |
| Judging a chart from a thumbnail | Every option is **drawn from your rows**, live, in light and dark mode |
| Advice you then have to rebuild | Each option is a **copyable Vega-Lite spec**, and the skill ports the pick to Recharts, D3 or your BI tool on request |
| Made-up data mistaken for a finding | Illustrative rows are flagged, and the page says so in a banner |
| Colour-blind-hostile defaults | A palette checked for colour-vision separation; never red vs green; legend and table view always on |

## How it works

```
data · screenshots · use case ──► brief (question · audience · surface · data)
                                        │  ask only what's missing (≤3, with defaults)
                                        ▼
        relationship ──► candidates ──► rank by perception, data fit, surface
                                        │
     page ◄── render ◄── validate reco.json ◄── one pick · 1–3 alternatives · avoid
       │
       └─► "port it to Recharts" · "what about a stacked area?" · real data instead of illustrative
```

## What you get

One page:
- **your question** in large type, with the audience, the surface and the stack (assumed
  values marked);
- **the pick**, drawn from your data, with *why* (cited) and *what it costs*;
- **alternatives**, each with *choose this if…*;
- **avoid**: the charts you're likely to reach for, and why not;
- **what it read from your screenshots**, **your data** profile, **build notes** (colours,
  order, porting hints) and the **sources**;
- on every chart: **Copy Vega-Lite spec**, **Show spec**, **Show table**.

For the sentiment example in [`evals/example-reco.json`](./evals/example-reco.json), the
pick is **diverging stacked columns by week**. The alternatives are **total mentions above
share lines** (when volume matters) and a **net sentiment line** (for a small tile).

## Install (Claude Desktop / claude.ai)

```bash
cd claude-skills/desktop
zip -r which-chart.zip which-chart/
```

Go to **Settings → Capabilities**, make sure **Code execution and file creation** is on,
and upload the zip under **Skills**. Then ask something like *"how should I visualize
sentiment over time for my brand dashboard?"* and attach what you have.

## Design decisions, and where they come from

- **The question before the data.** The FT Visual Vocabulary organises charts by the
  relationship they show
  ([FT](https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary)), and
  Power BI's guidance starts from goal, audience and space
  ([Microsoft](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a)).
  So the one question the skill asks, when it asks, is *what must the viewer answer at a
  glance*.
- **Perception decides between candidates.** Cleveland & McGill's ranking of elementary
  tasks, with position on a common scale first
  ([JASA 1984](https://doi.org/10.1080/01621459.1984.10478080)).
- **Sentiment over time** draws on Robbins & Heiberger's diverging stacked bars for rating
  scales ([2011](http://www.asasrms.org/Proceedings/y2011/Files/300784_64164.pdf)) and
  Few's total-above-parts form for time series plus part-to-whole
  ([2011](https://www.perceptualedge.com/articles/visual_business_intelligence/displays_for_combining_time-series_and_part-to-whole.pdf)).
  Where sources disagree (where neutral goes), the skill says so rather than hiding it.
- **Vega-Lite for every option.** One declarative spec is both the preview and the handoff:
  portable, editable in the [online editor](https://vega.github.io/editor/), and easy to
  port. Rendered with vega-embed (`actions: false`, SVG) from jsDelivr, as in the
  [embed docs](https://vega.github.io/vega-lite/usage/embed.html), but pinned to **exact
  versions with Subresource Integrity** hashes
  ([MDN](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity)):
  the page holds your rows, so a changed CDN file fails to load instead of running.
  Without the scripts, each card shows its spec.
- **Colour**: warm/cool diverging poles with a grey middle
  ([ColorBrewer](https://colorbrewer2.org/learnmore/schemes_full.html)), no red vs green
  ([Okabe & Ito](https://jfly.uni-koeln.de/color/)), and never colour alone
  ([WCAG 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)). The hexes
  were run through a CVD validator (OKLab ΔE under protan and deutan simulation) in both
  modes. The neutral grey is deliberately low-contrast, so the legend and table view stay
  on.
- **Same shape as the other Desktop skills here**: one JSON file, a stdlib validator, a
  template renderer. The validator turns "one pick", "cite your reasons" and "no dual
  axes" from promises into checks. It also catches a subtle bug found in testing:
  date-only strings drawn a day early in time zones west of UTC.

## Honest limits

- **Previews need the network** for the Vega scripts. Offline, you get the specs.
- **It recommends; it doesn't build your dashboard.** The spec is a starting point for your
  stack, not production code.
- **Screenshots are read, not measured.** Values read from an image are approximate and
  marked as such.
- **Settings don't persist** between conversations on Desktop; edit *Configuration* in
  `SKILL.md` to change defaults.

## Layout

```
which-chart/
├── SKILL.md                        the workflow (what Claude reads on trigger)
├── references/choosing.md          brief, matching rules, playbook, colour, patterns, sources
├── scripts/
│   ├── validate_reco.py            errors + warnings, each with the fix
│   └── render_page.py              reco.json → self-contained page (or --data for artifacts)
├── assets/page-template.html
├── evals/
│   ├── evals.json                  six acceptance scenarios
│   ├── example-reco.json           brand sentiment over time (illustrative)
│   └── example-reco-ranking.json   support tickets by channel: sorted bar, 100% stack, facets
└── icon.svg
```

## Testing

Checked locally:

- Both examples pass the validator. It rejects zero or two picks, unknown fields, any
  nested `data` other than the user's table, citations
  that don't resolve, unlabelled illustrative data, independent y scales on a layer, and
  pies over time. It warns on red-plus-green ranges and on date-only fields without UTC
  handling.
- Pages rendered in headless Chrome: light and dark, 1200px, and 390px in an iframe (no
  horizontal scroll). Every chart type in the patterns was drawn: diverging columns, vconcat
  panels, net line, 100% stack, sorted bar, facets.
- With the CDN blocked, or a script whose hash doesn't match, each card shows its spec and
  a message instead of a chart.
- A hostile title, option name and data value (`</script>`, `<img onerror>`) render as
  text.
