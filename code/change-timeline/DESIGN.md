# /change-timeline design

The renderer contract for every page this skill emits. `assets/timeline-template.html`
implements it; change the two together.

DESIGN.md is the skill's fixed aesthetic and accessibility contract. The user's approved
`style` in `preferences.md` (mode, density, accent) is the tunable part. On conflict,
**DESIGN.md wins for guarantees** (contrast, evidence visibility, no colour-only encoding)
and **preferences win for the knobs**.

## 1. Aesthetic direction

**Dev-tool dark.** Chosen by the user on 2026-10-26, over *Swiss minimal* and *quiet
editorial*. The page should feel like a well-made code tool (Linear, GitHub's commit view),
not a marketing timeline:

- **Dense but calm.** Compact rows, generous line height, one accent. Nothing animates.
- **Evidence is the texture.** SHAs and PR numbers in mono are the page's visual rhythm;
  they are never hidden behind a click.
- **Dark first, light equal.** Light mode is a full theme, not an afterthought.
- **Minimal.** No gradients, no shadows, no icons beyond `↗` on external links, no emoji.

The style preview tunes this direction (mode, density, accent); it does not switch to
another one. The other two directions offered when the skill was designed, *Swiss
minimal* and *quiet editorial*, are not built. Adding one means a `theme.direction` field,
its token set in the template, and a validator enum, in one change.

## 2. Type

| role | stack | size / weight |
|---|---|---|
| UI and body | `ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` | 14px / 1.55 |
| SHAs, dates, stats, chips | `ui-monospace, "SF Mono", Menlo, Consolas, monospace` | 12px, tabular figures |
| Page title | sans | clamp(22px, 4vw, 30px) / 700, −0.02em |
| Item title | sans | 16px / 600 (14.5px compact) |
| Labels (WHY, REVIEW, chips) | mono | 10.5–11px / 600–700, uppercase, 0.06em |

System stacks only: the page must render offline inside an artifact, with no font fetch.

## 3. Colour tokens

Defined on `:root` (light) and redefined under `prefers-color-scheme: dark`, guarded by
`:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]`. Every
surface uses `var(--*)`; no hex literal styles a visible element.

| token | light | dark | use |
|---|---|---|---|
| `--bg` | `#f7f7f8` | `#0d0e10` | page |
| `--surface` | `#ffffff` | `#15171a` | cards |
| `--surface-2` | `#f0f1f3` | `#1c1f23` | SHA chips, review box |
| `--line` / `--line-2` | `#e3e5e8` / `#d3d6db` | `#26292e` / `#33373d` | borders, rail |
| `--ink` | `#16181c` | `#e6e8eb` | text |
| `--ink-2` | `#4a5059` | `#a8aeb6` | secondary text |
| `--muted` | `#626973` | `#868d96` | labels, dates (≥4.5:1 on `--bg`) |
| `--accent` | `#c2410c` | `#ff6b3d` | PR links, selection, progress |

**Accent choices** offered in the style preview: `#ff6b3d` ember (default), `#6ea8fe`
signal blue, `#7dd3a0` mint. The page accepts any 6-digit hex in `theme.accent`; the
validator rejects anything else. The accent is used as-is in dark mode and darkened in
light mode until it clears 4.5:1 on white.

**Type colours** (chip text and border, rail dot): feat `--t-feat` blue, fix amber,
refactor violet, perf teal, security and revert rose, docs, chore grey, test green. Each
chip **always carries its word**, so colour is never the only encoding.

## 4. Layout

- Content max 920px; 16px side gutter; no horizontal page scroll at 390px. Lanes scroll
  inside their own box.
- Header: eyebrow (repo · range, mono, accent bar) → title → subtitle (≤66ch) → stats.
- Sticky toolbar: layout tabs · type filters · order · Copy as Markdown · Light/Dark.
- **Timeline**: date column (76px, hidden under 560px, where the date moves into the card) ·
  rail with a type-coloured ring · card.
- **Lanes**: one lane per area, marks placed by date, rows packed to avoid overlap, an axis
  with 6 ticks; selecting a mark opens its full card below.
- **Chapters**: chapter header (title, date, count) + summary + compact rows; details open
  to the full what/why/evidence.
- **Walkthrough**: numbered steps in `step` order, review box always open, a *Reviewed*
  tick stored per viewer, and a progress bar.

## 5. The card (the unit every layout reuses)

1. Row: type chip · BREAKING flag if any · area · (mobile) date
2. Title
3. What
4. **WHY** label + reason, with an `inferred` tag, or *Not stated in the PR or commits*
5. Evidence row: SHA chips (link to the commit) · PR chips `#142 ↗` · `+a −d` right-aligned
6. `Evidence ·` disclosure: quotes with linked sources, commits table, files table, review
7. Copy as Markdown

Rows 4 and 5 are never removed, in any layout or density: they are the point of the page.

## 6. Anti-patterns

- A why with no source and no `inferred` tag.
- SHAs truncated by CSS, hidden in a tooltip, or typed by hand.
- Colour as the only difference between types, or red vs green as the only encoding.
- Decorative charts (commit-count sparklines, pie of types) that answer no question.
- Gradients, glows, drop shadows, glassmorphism, emoji headers, "🚀 Features".
- Inter/Roboto web-font fetches; any network dependency.
- Marketing voice ("powerful", "seamless"), "This PR…", or generic titles.
- Card inside a card.

## 7. Renderer guarantees

- Every string from the JSON is set with `textContent`; links only when the URL matches
  `^https://`. `render_page.py` escapes `</` in the data block.
- Works offline; no external scripts or fonts.
- `localStorage` only for per-viewer conveniences (theme, last layout, reviewed ticks),
  every access in `try/catch`; the page renders fully without it.
- `prefers-reduced-motion` respected; print stylesheet hides the toolbar and opens details.
- Focus visible on every control; tabs, filters and marks are buttons with pressed or
  selected state.

## 8. Changing the design

A change to tokens or layout updates this file, the template, and the screenshots in the
README test notes in the same commit. A change the user asks for at runtime goes into
`preferences.md`, not here.
