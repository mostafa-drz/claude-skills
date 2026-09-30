# Choosing a chart

Read every run. Contents:

1. [The brief](#the-brief): the four things that decide a chart
2. [Relationships](#relationships): the FT Visual Vocabulary, as a first cut
3. [Ranking candidates](#ranking-candidates): perception, data fit, surface
4. [Playbook: ordered categories over time](#playbook-ordered-categories-over-time): sentiment, ratings, Likert
5. [Colour](#colour): the validated palette
6. [Anti-patterns](#anti-patterns)
7. [Vega-Lite patterns](#vega-lite-patterns): tested specs to start from
8. [Sources](#sources): the list reasons cite

---

## The brief

Four things, following the Power BI "choosing the right visual" checklist (data type, goal,
audience, available space) [S7]:

| part | what to settle | typical default |
|---|---|---|
| **question** | the one thing a viewer must answer at a glance, in their words | the most common reading of the use case |
| **audience** | who looks, how often, how chart-literate | the team that owns the dashboard, daily glance |
| **surface** | tile, panel, full page, report, slide; rough size | dashboard panel, about 600×280 |
| **data** | fields, types, grain, category counts, time span, counts vs shares | read from what was shared |

The question outranks the data. The same sentiment table gives three different picks for
"is it getting better or worse?", "how loud was it?" and "what's the balance right now?".

## Relationships

The FT Visual Vocabulary sorts charts by the relationship they show [S1]. Name one, at most
two, before thinking of chart types:

| relationship | the question sounds like | forms to consider (FT) |
|---|---|---|
| deviation | above/below a reference, better or worse than zero | diverging bar, line against a zero rule |
| correlation | does X move with Y | scatter, connected scatter, heatmap |
| ranking | which is biggest, the order | sorted bar, dot strip, slope |
| distribution | how spread, where the bulk is | histogram, box, violin, strip |
| change-over-time | trend, when it turned | line, column, area, slope, calendar heatmap |
| magnitude | how much, compared | bar or column, paired bars |
| part-to-whole | what share each part has | stacked column, proportional stacked bar, treemap (pie only for very few parts) |
| spatial | where | choropleth, dot map |
| flow | from where to where | Sankey, chord |

## Ranking candidates

**1. Perception.** People judge these most to least accurately: position along a common
scale; position along non-aligned scales; length, direction and angle; area; volume and
curvature; shading and colour saturation (Cleveland & McGill) [S2]. Encode the comparison
the question is about as high on that list as you can. That's why a bar or a line beats
a pie for comparing shares, and why a series of pies over time fails: its angles don't
share a baseline [S3].

**2. Data fit.**
- **Categories**: 1–3 series are comfortable in colour alone; at 4, label directly; past
  6–7, fold into "Other", facet into small multiples, or use a table.
- **Ordered categories** (negative → positive, low → high) keep their order in the stack,
  the legend and the colour. Never sort them alphabetically.
- **Counts vs shares**: shares hide volume, counts hide the mix. If both matter, it's two
  views (total above, parts below) [S3], never two y-axes [S4].
- **Many time points** (over about 30): lines, not columns. **Few** (under about 8):
  columns or a slope chart.
- **Stacked area** only reads the total and the bottom band. Use it only when the total is
  the story and the parts are rough context [S3].

**3. Surface.** A small tile holds one line or one number (a KPI tile plus sparkline often
beats any chart there). Two aligned panels need a full panel. A slide wants one message and
a direct label, not a legend hunt.

**4. Audience.** For a daily glance, pick the familiar form that answers the question. For
an analyst, the more precise form is fine if it answers better.

## Playbook: ordered categories over time

Sentiment (negative, neutral, positive), ratings and Likert answers are **ordered
categories that sum to a whole**, tracked over time. The candidates, and when each wins:

| question | pick | why | cost |
|---|---|---|---|
| better or worse, when did it turn | **diverging stacked columns**, one per period, neutral straddling zero | recommended for rating scales; each side grows away from the centre, a spike reads instantly [S5][S6] | shares only, no volume |
| how loud, and how the mix moved | **total line above share lines**, aligned on time | recommended for time series plus part-to-whole; every part gets a common baseline [S3] | needs height for two panels |
| the balance right now, in a tile | **net line** (positive share − negative share) against a zero rule | a deviation from a fixed reference [S1] | hides neutral and volume; "net sentiment" is a convention, so define it on the dashboard |
| compare brands or channels | **small multiples** of the pick, one per brand, shared y scale | same form repeated, so comparison is position | needs width; cap at 6–8 panels |

**Neutral, a real disagreement.** Robbins & Heiberger centre neutral across zero in grey
[S5]. Datawrapper argues for setting neutral aside, since it pushes the outer categories off
a common baseline (seen as a search snippet only; the page couldn't be fetched). If the
question is about positive vs negative and neutral is large, name this cost, and consider
the net line or share lines as the alternative. Say which you chose and why.

**Avoid here**: a pie or donut per period [S3][S5], volume and sentiment on two y-axes [S4],
and red vs green as the only difference between negative and positive [S8][S9].

## Colour

Colour comes last, after form. Use these values, which were checked for colour-vision
separation (OKLab ΔE, deutan and protan simulation) against the page's surfaces. The page
swaps each light value for its dark step by itself, so **write the light hex in specs**.

| role | light | dark |
|---|---|---|
| categorical 1–8, in this order | `#2a78d6` `#eb6834` `#1baf7a` `#eda100` `#e87ba4` `#008300` `#4a3aa7` `#e34948` | `#3987e5` `#d95926` `#199e70` `#c98500` `#d55181` `#008300` `#9085e9` `#e66767` |
| sentiment positive / neutral / negative | `#2a78d6` / `#bdbcb5` / `#e34948` | `#3987e5` / `#57564f` / `#e66767` |
| single series, emphasis | `#2a78d6` | `#3987e5` |
| context series, muted rule | `#52514e`, `#898781` | `#c3c2b7`, `#898781` |
| chart surface (2px gap stroke) | `#fcfcfb` | `#1a1a19` |

Rules:
- **Diverging = two opposite hues plus a grey middle** (ColorBrewer: light middle, dark
  contrasting extremes) [S10]. Blue↔red is warm/cool. Never red↔green [S8].
- The neutral grey is deliberately low-contrast, so it recedes. Always keep the legend and
  the table view: colour is never the only way to tell categories apart [S9].
- **Colour follows the entity**: a filter that removes a series never repaints the rest.
- One highlighted series in blue and the rest in grey often beats eight colours when the
  story is one series.

## Anti-patterns

Put one in `avoid` when the user is likely to reach for it: it's in their screenshot, it's
their tool's default, or they asked about it.

| don't | because | instead |
|---|---|---|
| a pie or donut per period | angles across separate circles can't be compared; "fails in every respect" for change over time [S3] | columns or lines on one time axis |
| a pie for many or close values | angle and area are judged far less accurately than length [S2][S11] | a sorted bar |
| two y-axes | the scales' alignment is arbitrary and suggests false correlations [S4] | two aligned charts, or index both to 100 |
| 3D | distorts the slices and bars it draws [S11] | flat |
| a bar axis not starting at zero | bar length *is* the value [S12] | start at zero (a line axis may not, if it's labelled) |
| red vs green as the only encoding | the most common colour-vision deficiency can't separate them [S8] | blue vs red, plus labels [S9] |
| stacked area when parts matter | only the bottom band has a baseline [S3] | share lines, or diverging columns |

## Vega-Lite patterns

Every spec: `"$schema": "https://vega.github.io/schema/vega-lite/v6.json"`,
`"data": {"name": "table"}`, no `width` (the page fits it to the card), a `height`, and a
`tooltip`. Stacks list categories in their real order, with a 2px surface stroke between
segments. The first three patterns are the worked example in
[`evals/example-reco.json`](../evals/example-reco.json): copy them from there and change the
field names.

- **Diverging stacked columns** (`options[0]`). Per period: `joinaggregate` a total, compute
  `share`, set an `order` (negative 1, neutral 2, positive 3) and a `below` value (the
  negative share plus half of neutral), `stack` share sorted by order, subtract the summed
  `below` as an offset, and draw a `bar` with `y`/`y2` plus a zero `rule`. This follows the
  Vega-Lite gallery's diverging example [S6], using the stack transform [S13].
- **Total above shares** (`options[1]`). A `vconcat` of a total line and share lines, with
  the x scale shared. The page sizes each panel's width.
- **Net line** (`options[2]`). Compute a signed count, `aggregate` by period, divide by the
  total, and `layer` a zero `rule` under a `line`.
- **100% stacked columns**: `"y": {"aggregate": "sum", "field": "<measure>", "stack":
  "normalize", "axis": {"format": ".0%"}}` with `color` and `order` on the category [S14].
- **Sorted bar (ranking)**: `"y": {"field": "<cat>", "type": "nominal", "sort": "-x"}`,
  `"x": {"field": "<measure>", "type": "quantitative"}`, a single colour `#2a78d6`.
- **Small multiples**: wrap a single-view spec as `{"facet": {"field": "<cat>"}, "columns":
  3, "spec": {…, "height": 110}}`; `columns` sits at the top level. The page sizes the
  cells to the card (`evals/example-reco-ranking.json`, `options[2]`).
- **Dates.** Date-only strings ("2026-06-29") parse as UTC and display in local time, so
  labels slip a day or a month back. Use `utc` time units (`utcyearmonthdate`), or
  `"scale": {"type": "utc"}` plus `"formatType": "utc"` on a formatted temporal axis or
  tooltip. The validator warns when this is missing.

After validating, if the page shows "Couldn't draw this spec", the message is Vega's error:
fix the spec rather than dropping the option.

## Sources

Copy the ones you cite into `reco.json` → `sources`, and cite them by their position in
**that** list (1-based), not by these S-numbers.

- S1: Financial Times, Visual Vocabulary: https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary
- S2: Cleveland & McGill (1984), Graphical Perception, JASA: https://doi.org/10.1080/01621459.1984.10478080
- S3: Few (2011), Displays for Combining Time-Series and Part-to-Whole: https://www.perceptualedge.com/articles/visual_business_intelligence/displays_for_combining_time-series_and_part-to-whole.pdf
- S4: Few (2008), Dual-Scaled Axes in Graphs: https://www.perceptualedge.com/articles/visual_business_intelligence/dual-scaled_axes.pdf
- S5: Robbins & Heiberger (2011), Plotting Likert and Other Rating Scales: http://www.asasrms.org/Proceedings/y2011/Files/300784_64164.pdf
- S6: Vega-Lite example, diverging stacked bar: https://vega.github.io/vega-lite/examples/bar_diverging_stack_transform.html
- S7: Microsoft, Power BI visualization types: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a
- S8: Okabe & Ito, Color Universal Design: https://jfly.uni-koeln.de/color/
- S9: W3C, WCAG 2.2 Understanding 1.4.1 Use of Color: https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html
- S10: ColorBrewer, schemes: https://colorbrewer2.org/learnmore/schemes_full.html
- S11: Few (2007), Save the Pies for Dessert: https://www.perceptualedge.com/articles/visual_business_intelligence/save_the_pies_for_dessert.pdf
- S12: Storytelling with Data, Bar charts must have a zero baseline: https://www.storytellingwithdata.com/blog/2012/09/bar-charts-must-have-zero-baseline
- S13: Vega-Lite, stack transform: https://vega.github.io/vega-lite/docs/stack.html
- S14: Vega-Lite example, normalized stacked bar: https://vega.github.io/vega-lite/examples/stacked_bar_normalize.html

A claim these don't cover is your judgement: give that reason `"judgement": true` and no
`cites` (the page marks it), and never attach a source that doesn't say it.
