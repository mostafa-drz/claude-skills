---
name: svg-art
description: >-
  Generates artistic SVGs directly as code — minimal line icons, geometric
  marks, generative patterns, or hand-drawn compositions — and assembles a
  modern 2026 HTML gallery preview. Saves each session to its own semantically
  named folder on the Desktop. Learns from feedback: which styles you loved,
  which compositions you rejected, which stroke weights and palettes you
  return to. The tone and aesthetic get more personalized each session.
  Use when you want icons for a product, a branded mark, a generative poster,
  or a set of decorative SVGs for a page, blog, or app.
argument-hint: "[what to generate] [--style <mode>] [--count <N>] [--palette <colors>] [--stroke <px>] [--canvas <WxH>] [--notes <text>]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Bash(mkdir *)
  - Bash(ls *)
  - Bash(open *)
  - Bash(date *)
  - Bash(pwd)
  - Bash(echo *)
  - WebSearch
  - WebFetch
---

## Preferences

_On startup, use Read to load `~/.claude/skills/svg-art/preferences.md`. If missing, treat as first-run._

Defaults when no preferences exist:
- `output-root`: `~/Desktop/svg-art/` (confirmed on first run)
- `default-style`: `line-icon` (minimal, consistent stroke)
- `default-count`: `9` (3×3 grid feels complete, not overwhelming)
- `default-stroke`: `1.5` (px, relative to a 24px canvas)
- `canvas`: `24x24` for icons, `400x400` for compositions
- `palette-mode`: `currentColor` (monochrome, themeable) — alternates: `duotone`, `brand-palette`
- `tone`: `friendly-cli` (matches user's global tone preference)
- `open-gallery`: `true`

_Also load `~/.claude/skills/svg-art/feedback-journal.md` if present — contains per-session likes/dislikes and extracted aesthetic signals. Summarize the signal (e.g., "prefers asymmetric compositions, negative space over fills, avoids radial symmetry") and let it shape this session's generation._

## Context

_On startup, use Bash to detect today's date (`date +%Y-%m-%d`) and whether the output root exists._

## Command routing

Check `$ARGUMENTS`:
- `help` → show help, stop
- `config` → run config flow, stop
- `reset` → delete preferences + feedback journal, confirm, stop
- `feedback` → rate the most recent set (teaches the skill), stop
- `history` → list past sessions with titles and dates, stop
- `styles` → print a quick reference of available style modes, stop
- anything else → generate

## Help

```
svg-art — Artistic SVG generation with a 2026 HTML gallery

Usage:
  /svg-art [what to generate]                      Interactive generation
  /svg-art [...] --style <mode>                    Override default style mode
  /svg-art [...] --count <N>                       How many SVGs (default 9)
  /svg-art [...] --palette <colors>                e.g., "monochrome", "warm-duotone", "#0a2a6b,#e8eefa"
  /svg-art [...] --stroke <px>                     Stroke width in relative px
  /svg-art [...] --canvas <WxH>                    Canvas size, default 24x24 for icons
  /svg-art [...] --notes <text>                    Extra constraints, references, exclusions
  /svg-art config                                  Set preferences
  /svg-art reset                                   Clear preferences + feedback journal
  /svg-art feedback                                Rate the last set (teaches the skill)
  /svg-art history                                 List past sessions
  /svg-art styles                                  Reference of style modes
  /svg-art help                                    This help

Style modes:
  line-icon     Minimal outlined icons, consistent stroke, Feather/Lucide lineage
  geometric     Bauhaus-inspired: circles, squares, triangles, Swiss-design composition
  mark          Logomarks — single-concept, tightly composed, memorable at small sizes
  generative    Math-driven: Voronoi, waves, spirals, noise fields, grid deviations
  organic       Hand-drawn feel: variable stroke, jittered paths, soft imperfection
  duotone       Two-color compositions with intentional overlap / transparency
  animated      SMIL or CSS-animated — subtle breathing motion, not full animation

Examples:
  /svg-art "9 icons for a gardening app"
  /svg-art "generative poster for a music night" --style generative --canvas 800x1200
  /svg-art "brand mark for 'Northwind' — compass / wind motif" --style mark --count 4
  /svg-art "icon set: finance dashboard" --style line-icon --stroke 1.75

Output:
  {output-root}/{YYYY-MM-DD}-{kebab-title}/
    ├── gallery.html         ← 2026 aesthetic single-file preview
    ├── data.json            ← metadata per SVG (concept, style, size, palette)
    ├── svgs/
    │   ├── 01-{name}.svg
    │   ├── 02-{name}.svg
    │   └── ...
    └── sources.md           ← design system for the set + any inspiration refs

Current preferences:
  (loaded from preferences.md)
```

## Config

Use AskUserQuestion to collect:

1. **Output root** — where should sessions save? (default: `~/Desktop/svg-art/`)
2. **Default style mode** — which aesthetic feels most "you"? (line-icon / geometric / generative / organic / mixed)
3. **Default canvas size** — 24x24 for icons, 48x48 for detailed marks, 400x400+ for compositions
4. **Palette approach** — monochrome (`currentColor`) / duotone / a specific brand palette (hex list)
5. **Tone** — friendly-CLI (terse/warm), detailed (more commentary), minimal (facts only)

Save to `~/.claude/skills/svg-art/preferences.md`:

```markdown
# /svg-art preferences
Updated: {date}

## Defaults
- output-root: {path}
- default-style: {mode}
- default-count: {N}
- default-stroke: {px}
- canvas: {WxH}
- palette-mode: {monochrome|duotone|palette}
- palette-hex: {optional comma-separated list}
- tone: {friendly-cli|detailed|minimal}

## Aesthetic profile (optional — editable)
- Likes: (e.g., negative space, asymmetry, thin strokes, cool palettes)
- Dislikes: (e.g., radial symmetry, busy compositions, gradients)
- Reference artists / libraries: (e.g., Lucide, Dieter Rams, Bauhaus, Muriel Cooper)

## Learned
- (auto-appended as patterns emerge from feedback journal)
```

## Reset

Delete both `preferences.md` and `feedback-journal.md`. Confirm: "All cleared. Starting fresh next time."

## First-time detection

If no preferences file exists, show a warm onboarding:

```
First time running /svg-art — quick intro:

  I generate SVGs directly as code — no image API required. I'm good at
  minimal/geometric/generative territory; weaker at photorealistic or organic
  chaos. SVG scales infinitely, edits cleanly, and themes via currentColor.

  Each session gets a Desktop folder with the SVGs, a data.json, and a
  single-file HTML gallery you can open anywhere.

  I learn from feedback. After a session, run `/svg-art feedback` to tell me
  what worked — over 3-5 sessions I develop a clear sense of your aesthetic.

  Run `/svg-art config` for quick setup, or continue and I'll use defaults.
```

Then proceed. After the first successful session, ask inline if they want to save any quick prefs (default style, palette, stroke).

## Workflow

### Step 0 — Load learning context

1. Read `preferences.md` — carry defaults and aesthetic profile forward
2. Read `feedback-journal.md` — extract a one-line bias signal like:
   > "Past sessions: leans asymmetric, thin strokes (1.25-1.5px), prefers cool monochrome, avoids radial/mirror symmetry"

If a signal exists, announce it briefly at the start:
> "Biasing toward [signal] based on past sessions. Override with flags if you want something different."

### Step 1 — Parse the brief

Parse `$ARGUMENTS` for:
- **What** — free text before any `--flag` (the concept / subject / motif)
- `--style <mode>` — override default style
- `--count <N>` — how many SVGs
- `--palette <colors>` — color approach
- `--stroke <px>` — stroke weight
- `--canvas <WxH>` — dimensions
- `--notes <text>` — extra constraints

If **what** is missing, ask ONE AskUserQuestion with 2-4 concrete options (subject, style, count). Don't interrogate.

### Step 2 — Draft the visual system

Before generating, commit to a *system* that will give the set coherence. Write out:

```
Visual system:
  Subject:        [interpretation of the brief]
  Style:          [mode — e.g., line-icon minimal, 1.5px stroke]
  Canvas:         [WxH]
  Palette:        [monochrome / hex list / duotone relationship]
  Composition:    [3-5 rules — e.g., single focal point, 10% negative-space margin, stroke caps rounded]
  Concepts (N):   [list of N distinct ideas that will become SVGs]

Reply 'go' to generate, or tweak any of the above.
```

Wait for confirmation — this is the one gate. The system prevents the set from feeling like N unrelated drawings.

### Step 3 — Create the session folder

Slug: `{YYYY-MM-DD}-{kebab-summary-max-60chars}`. Examples:
- `2026-04-18-gardening-app-icons`
- `2026-04-18-northwind-brand-marks`

```
mkdir -p {output-root}/{slug}/svgs
```

Per-session isolation — never delete siblings.

### Step 4 — Generate the SVGs

For each concept in the visual system, write one SVG file directly.

**SVG authoring rules**:
- Start with `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 W H" fill="none" stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">` for line icons
- Use `currentColor` for monochrome so the icon inherits text color on any page
- Prefer `<path d="...">` over many primitives for cleaner files
- Round coordinates to 0.5 or 1 — avoid 12 decimal places of noise
- Add `<title>` inside each SVG for accessibility + self-documentation
- For duotone, layer two `<path>` groups with explicit `fill`/`stroke` rather than gradients (cleaner, more themeable)
- For generative patterns, deterministic math > random seeds; if random, note the seed in a comment

**Naming**: `{NN}-{kebab-concept}.svg` where NN is a zero-padded index. Use content-derived names, not counters (e.g., `03-watering-can.svg`, not `03-icon.svg`).

**Per-SVG metadata** — capture in memory for `data.json`:
```json
{
  "file": "03-watering-can.svg",
  "concept": "watering can",
  "style": "line-icon",
  "canvas": "24x24",
  "palette": "monochrome",
  "stroke": 1.5,
  "notes": "tilted 15° for dynamism, spout follows the composition's diagonal"
}
```

**Quality bar** — before saving each SVG:
- viewBox is present and correct
- No stray fill="black" when we intended stroke-only
- All paths close properly (`Z` where appropriate)
- File size < 2KB for icons, < 15KB for compositions (simplicity check)

### Step 5 — Build the gallery

Generate `gallery.html` — single self-contained file. Aesthetic mirrors the `/shop-research` report (same CSS variable system, light/dark mode, generous whitespace, pill chips).

Structure:
1. **Header** — session title, brief, visual-system summary (as pill chips)
2. **Grid** — the SVGs rendered inline (not `<img>` src — paste the SVG markup so `currentColor` picks up the theme). Each tile shows the SVG on a subtle backdrop, concept name, and size.
3. **Copy buttons** — each tile has a "Copy SVG" button (tiny inline JS that copies the SVG source to clipboard)
4. **Download all** — link to a zipped download is overkill; instead, show the folder path prominently
5. **Footer** — system summary + "rate this set" link to `/svg-art feedback`

Dark mode: SVGs using `currentColor` automatically invert with theme. That's the point.

### Step 6 — Write data.json + sources.md

`data.json`:
```json
{
  "session": { "slug": "...", "date": "...", "brief": "...", "style": "...", "count": 9 },
  "visual_system": { "palette": "...", "stroke": 1.5, "canvas": "24x24", "composition_rules": [...] },
  "svgs": [ {...metadata per SVG...} ]
}
```

`sources.md` — design system rationale, any WebSearch references used for inspiration, decisions the user can re-apply manually later.

### Step 7 — Report + open

```
Generated {N} SVGs — {style} · {canvas} · {palette}

  Concepts: {list of names}

Folder:   {output-root}/{slug}/
Gallery:  {output-root}/{slug}/gallery.html

Open it?  (y/N)  — or rate with:  /svg-art feedback
```

If `open-gallery: true`, run `open {gallery.html}`.

### Step 8 — Invite feedback

End with:
> When you've had a look, run `/svg-art feedback`. Even a quick "liked #2 and #5, disliked #7" helps me sharpen your style.

## Feedback & learning

When invoked as `/svg-art feedback`:

1. Find the most recent session folder.
2. List the SVGs and their concepts.
3. Ask via AskUserQuestion (or free-text):
   - **Which did you love?** (pick multiple — e.g., "#2, #5")
   - **Which missed the mark?** (free text)
   - **What do you want more of?** (more negative space / thinner stroke / warmer palette / looser composition / other)
   - **What to avoid?** (free text)
4. Append to `~/.claude/skills/svg-art/feedback-journal.md`:

```markdown
## {session slug} — {date}
- Loved: {list} — pattern: {inferred — e.g., "asymmetric + single focal"}
- Missed: {list} — pattern: {inferred — e.g., "too busy; radial symmetry"}
- Want more of: {user text}
- Avoid: {user text}
- Signal: {one-line generalization, e.g., "prefers asymmetric, thin-stroke, single-subject compositions; avoid radial + fills"}
```

5. When 3+ sessions show a consistent pattern, promote it to the `## Learned` section of `preferences.md`. Mention: "Noticed you consistently prefer X — saving that as standing bias."

## Style mode reference (quick)

Full details in `reference/styles.md` (generate on first session if not present).

- **line-icon**: Stroke-only, `currentColor`, rounded caps, 1.25-2px stroke, tight composition
- **geometric**: Primitive shapes (circles, rects, triangles), composed into a balanced grid, reductive
- **mark**: One idea, one mark — reads clearly at 16px and 200px, negative-space awareness
- **generative**: Deterministic or seeded math — Voronoi, waves, spirals, L-systems, noise
- **organic**: Jittered paths, variable stroke widths, slight asymmetries — "hand-drawn by a designer, not an artist"
- **duotone**: Two colors, intentional overlap, sometimes a tint layer — think Saul Bass posters, reductive
- **animated**: Subtle CSS `@keyframes` or SMIL — one element breathes, rotates, or draws in

## Principles

1. **SVG is code — write it directly** — no image API, no PNG round-trip. Paste-ready, edit-friendly.
2. **A system, not a grab-bag** — commit to stroke weight, palette, and composition rules upfront; consistency across the set matters more than any single SVG being perfect.
3. **`currentColor` is the default** — themeable for free; override only when duotone or brand-palette is explicit.
4. **Small files, round numbers** — 1KB is the goal for icons; 12-decimal coords are a smell.
5. **Learn quietly** — the feedback journal is the brain; after 3-5 sessions the bias should be visibly sharper without the user having to configure anything.
6. **Warm, terse CLI tone** — one friendly line at start and end; no corporate filler, no emoji-heavy output.
7. **Graceful degradation** — if a concept won't fit the style (e.g., "photorealistic portrait" in line-icon mode), say so upfront and propose an alternative rather than producing a weak SVG.
