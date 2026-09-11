# Rendering cluster pages

Loaded on demand by `/screenshots-memory` when it renders or re-renders HTML.
This is the canonical description of the cluster page: its layout, the filter-chip
behaviour, and the review popovers that hand corrections back to the agent.

## The cluster page

Generate a **single self-contained** `index.html` per cluster and a top-level
`{memory-root}/html/index.html` browser. Load `reference/report-template.html` on
demand; it carries the canonical CSS and JS, so pages can never drift from each other.

- **Modern 2026** — system font stack, generous whitespace, soft shadows, 12-16px
  radii, pill badges. Dark `#121212` ground, `#ff5722` primary accent, `#03a9f4`
  secondary, hairline borders.
- **Light + dark** via `prefers-color-scheme`, CSS variables only, explicit `body`
  background.
- **Mobile-responsive**, single column on small screens.
- **Inline the icon** from `icon.svg` at ~32px next to the H1, coloured with the accent.
- **No external scripts or fonts** — one file, opens anywhere, works offline.

**Assets must resolve.** Cluster pages live at `clusters/<slug>/index.html`, so copy
each referenced image into `{memory-root}/clusters/<slug>/assets/` and reference it
relative to the cluster page.

Per-cluster page:
1. **Header** — title, one-line summary, date range, note count, avg-confidence meter.
2. **Note cards** — the screenshot thumbnail, the summary, the kind badge, the
   extracted `fields` as a compact definition list, a **confidence badge** (green ≥
   threshold, amber below), the provenance line (📸 app · captured date · original
   filename), and tag chips. Cards below threshold get an amber left-border and a
   "flagged — low confidence" label. `⟨uncertain: word?⟩` renders as a dotted A card is flagged only when
   `confidence < threshold` **AND** `reviewed` is false; every card also carries
   `data-reviewed="true|false"`. Confidence alone would be wrong — a verdict of `ok`
   leaves confidence untouched by design, so a confirmed note would never leave the
   ⚠ Needs review view.
   underline. A `sensitive` note shows its thumbnail and a plain "contents not
   recorded by choice" line instead of text.
3. **Entities** — a chip row of the people, products and projects in this cluster.
   A card with `reviewed: true` renders a ✓ beside its confidence badge, so the user can
   see what they already confirmed even with the ⚠ Needs review switch off.
4. **Provenance is always visible** — every card says exactly which capture it came
   from and when.

### Chips are filters, not labels

Every chip — entity chips in the header, tag chips and the **kind** badge on each card
— is a real toggle:

```html
<button class="chip" data-facet="product" aria-pressed="false">product</button>
```

- **Several can be on at once**, and matches **union (OR)**: `product` + `ui` shows
  either. AND would empty the page after two clicks — the point is to widen.
- Each card carries `data-facets="kind|tag|tag|Entity"` (pipe-separated, matched
  case-insensitively), so the filter needs no lookup table.
- The **⚠ Needs review** switch is a quality facet, not a subject one, so it **ANDs**
  with the chips: "flagged captures about Amsterdam".
- A chip in both header and card stays in sync (`aria-pressed` is the single source of
  truth; CSS hangs off it).
- The toolbar shows a live `showing N of M`, a **Clear filters** button that appears
  only while filtering, and the grid says "No notes match those filters." rather than
  going blank.

### Review popovers

Every card gets a **Review** button opening a native `[popover]` (light-dismiss and Esc
for free). Inside: a verdict — **Reads correctly** / **Fix the text** / **Wrong kind,
tags or cluster** — plus an optional one-line **lesson** for the extractor.

Each verdict reveals only the field it needs:
- **Reads correctly** — no field.
- **Fix the text** — a textarea pre-filled with the current extraction, so a fix is an
  edit rather than a retype. Exported as `text`.
- **Wrong kind / tags / cluster** — a one-line instruction. Exported as `reassign`,
  **never** as `text` — the extraction isn't the correction here, and an agent handed
  the extraction would have nothing to act on.

Because this payload drives destructive edits to real notes, the page is deliberately
hard to use carelessly:

- **Save stays disabled** until a verdict is chosen *and* the human supplied what it
  needs, with an inline reason. For **Fix the text** that means an **actual edit** — a
  textarea still holding the prefill is not a correction, and sending it back would
  overwrite the note with a re-flowed copy of itself at full confidence.
- **Abandoning a popover restores it.** Esc, clicking away, or Discard resets to the
  last saved state, so a half-finished edit never looks like a decision.
- **Switching verdict warns** when it would drop text you typed.
- **Anything that can't round-trip is disabled, not ignored**: a card with no
  `data-note-id`, or two sharing one, get Review disabled with the reason in the
  tooltip. A browser that won't persist (private mode, blocked storage) says so in the
  handoff bar instead of pretending the batch is safe.
- **The draft store is versioned** — `{ schema: N, entries: {…} }`. A draft written by
  an older page is discarded on load rather than exported, and the bar says how many
  were dropped. Bump `SCHEMA` whenever the entry shape changes.

Saved verdicts persist in `localStorage` (keyed by page path), and a sticky **handoff
bar** appears: *"3 reviews ready — Copy for Claude"*. The page **never writes to the
memory store** — it hands the batch back to the agent, which applies and commits it.

Top-level `html/index.html`: a card grid of all clusters (title, note count, kind mix,
date range, avg confidence, top entities), sorted by most-recently-touched. Inline
vanilla JS only — no framework, no build step.

## The page is a snapshot

A cluster page reflects the memory at render time and cannot update itself. Re-rendering
after `review --apply` is therefore **load-bearing, not cosmetic**: it is what moves
newly-confirmed cards out of the ⚠ Needs review view and refreshes `data-extracted-at` on
anything re-extracted. Skip it and the user re-reviews notes that were already applied,
and the replay guard silently discards the result.
