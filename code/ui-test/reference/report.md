# `report.html` — aesthetic + structure

Loaded on demand by Step 8. Single self-contained HTML file. No external scripts. CSS variables only. Inline JS ≤200 lines, vanilla.

## Layout

1. **Header** — title, run timestamp, base URL, environment chip, verdict pill (green / amber / red).
2. **Verdict hero** — large card with the verdict label and 2–3 sentence rationale. On failure, two-column layout: first-failing-step screenshot ~280–320px on the left, prose on the right. Stacks on mobile.
3. **Step timeline** — vertical, expandable rows. Per row: status icon, name, duration, viewport tag. Click → expands to per-step screenshot, console output, network calls, assertion details.
4. **Category panels** (collapsible, one per enabled category):
   - **a11y** — violations grouped by severity; each row has the axe rule URL, code locator, and the offending HTML snippet. Counts per severity in the panel header.
   - **perf** — metric cards (LCP, CLS, INP, JS heap) with pass/fail vs budget; tiny SVG waterfall (no libs). One sparkline if multi-viewport.
   - **visual** — diff strip per snapshot: baseline | current | diff. Slider on the diff overlay (vanilla `<input type=range>`). Pixel-delta % shown.
5. **Coverage gaps** — yellow panel listing anything that didn't run and why (e.g., "axe-core CDN blocked, a11y skipped"). Always render this panel; if empty, show a small "Full coverage" check.
6. **Filter chips** — `[All] [Failed only] [Slow] [a11y] [Perf]`. Inline JS toggles row visibility.
7. **Footer** — sources visited, environment summary, "Rate this run → `/ui-test feedback`" link.

## Aesthetic targets

- **Modern 2026** — clean type (system font stack + Inter-style weight ramp), generous whitespace, soft shadows, subtle gradients, 12-16px corners, pill chips.
- **Light + dark** via `prefers-color-scheme` — CSS variables only, no JS theme switch needed.
- **Mobile-responsive** — single-column under ~720px.
- **Verdict-forward** — the hero of the page IS the verdict, not the grid of data.
- **Data-dense but scannable** — pill chips for key metrics, inline mini bar charts for distributions (pure CSS), expandable rows for the timeline.
- **No emoji soup** — use color + typography for meaning.
- **Open anywhere** — single file. Inline `<script>` only. Never split into multiple HTML files.

## Inline JS responsibilities

Keep ≤200 lines, no framework:
- Read run data from a `<script type="application/json" id="run-data">` payload embedded in the page.
- Wire click handlers on filter chips and step rows (toggle expanded class).
- Visual diff slider — clip-path on the diff layer driven by the range input.
- Live re-filter of the step timeline based on chip selection.

## Interactive chips (optional, if `confirm-plan: never`)

If the run was triggered without confirmation, render the parsed inputs as chips at the top:
- `Categories: e2e ✓ visual ✓ a11y ✓ perf ✓` — each clickable to filter the panels in the report.
- `Viewport: 1440×900` — clickable if multi-viewport, switches the visible viewport tab.
- These are display + filter, NOT recompute. The verdict on the page is the verdict that ran. Re-running with different inputs requires a fresh `/ui-test` invocation.

## Template file (optional)

If `~/.claude/skills/ui-test/reference/report-template.html` exists, load it as the skeleton and fill placeholders. Otherwise generate from scratch following this guide.
