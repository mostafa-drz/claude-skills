---
name: remarkable-memory
description: >-
  Turns handwritten reMarkable notes into a queryable semantic memory. Syncs
  pages from a reMarkable tablet (via the reMarkable MCP server, rmapi, or a
  USB/SSH bridge), renders each page to an image and reads the handwriting with
  Claude vision — no OCR key — then extracts each page into confidence-scored,
  human-editable Markdown + JSON with full provenance (which notebook, which
  page, when synced). Clusters notes by topic and project, renders a clean
  single-file HTML view per cluster, and answers natural-language questions
  against the memory ("extract my notes about the Amsterdam music festival",
  "show layouts inspired by my living-room design from the past 20 days"). Flags
  low-confidence extractions for review, and learns the user's handwriting and
  shorthand from every correction. Use when the user wants to sync, extract,
  organize, search, or reason over their reMarkable notes, or build a second
  brain from handwritten pages.
argument-hint: "[sync|review|clusters|browse|feedback|config|setup|reset|help] [--notebook <name>] [--project <name>] [--since <Nd>] [--min-confidence <0-1>] [--yes] [text query...]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(mkdir *)
  - Bash(cp *)
  - Bash(ls *)
  - Bash(date *)
  - Bash(pwd)
  - Bash(echo *)
  - Bash(git *)
  - Bash(rmapi *)
  - Bash(open *)
  - Bash(xdg-open *)
# The reMarkable data source is an MCP server (SamMorrowDrums/remarkable-mcp,
# remarkdown, or a fork). Its tool names vary by server and can't be pre-listed
# here — approve them at runtime the first time a sync runs. See Setup.
---

# reMarkable Memory

Sync handwritten reMarkable notes into a git-versioned semantic memory, cluster
them by topic, render clean HTML per cluster, answer questions over them, and get
sharper at reading your hand every time you correct an extraction.

_New here? [`README.md`](./README.md) is the human-facing overview, and
[`examples/quickstart.html`](./examples/quickstart.html) has copy-paste recipes for
everyday use._

## Preferences

_On startup, use Read to load `~/.claude/skills/remarkable-memory/preferences.md`.
If it's missing, treat this as first-run (see **First-time detection**)._

Defaults when no preferences exist:
- `memory-root`: `~/remarkable-memory/` (confirmed on first run; git-init'd so every change is diffable and revertible)
- `connection`: `mcp` (`mcp` = reMarkable MCP server · `rmapi` = ddvk/juruen CLI · `remarkdown` = hosted MCP)
- `extract-engine`: `vision` (render each page to an image via the source's page-image tool and read it directly — best on messy/cursive, no API key. Never call a server's OCR-text tool on Claude Code; see **Sync Step 3**. Alternative: `myscript`, reMarkable's own conversion, if the user prefers it.)
- `confidence-threshold`: `0.75` (extractions below this are flagged for `review`, never silently trusted)
- `cluster-style`: `topic` (`topic` = by subject · `project` = by notebook/project · `hybrid`)
- `open-html`: `true` (auto-open the cluster HTML when a sync finishes)
- `tone`: `friendly-cli` (terse, warm, direct)

_The learned handwriting guide and the corrections log live in the **memory
store** (`{memory-root}/extraction-guide.md`, `{memory-root}/corrections.md`), not
the skill dir — so they're versioned with the user's data and survive `reset`. On
startup, if `{memory-root}/extraction-guide.md` exists, load it and treat it as
ground truth about **this user's** hand and shorthand (e.g. "HM = hippocampus",
"boxes tagged 'LR' are living-room layouts"). Feed it to the extractor on every
sync — it's what makes the memory read the user better over time._

## Context

_On startup, use Bash to detect: today's date (`date +%Y-%m-%d`), whether
`memory-root` exists and is a git repo (`ls`, `git -C … rev-parse`), and the OS
(for auto-open: `open` on macOS, `xdg-open` on Linux). Do NOT connect to the tablet
yet — that happens inside `sync`/`setup` after a preflight._

## Command routing

Check `$ARGUMENTS`:
- `help` → show Help, stop
- `config` → run Config, stop
- `reset` → delete **skill preferences only** (see **Reset**); the memory store is preserved. Confirm first, stop
- `setup` / `preflight` → run the connection setup/onboarding flow (see **Setup**), stop
- `sync` → ingest new/changed pages into memory (see **Sync**)
- `review` → walk low-confidence extractions and capture corrections (see **Review & learning**)
- `clusters` / `browse` → (re)render and open the HTML cluster views (see **Render**)
- `feedback` → rate the last answer/extraction quality (see **Review & learning**)
- anything else (free text, optionally with flags) → treat as a **query** against the memory (see **Query**)

**Every command that reaches the tablet starts with the Step 0 preflight.**

## Help

```
remarkable-memory — Handwritten reMarkable notes → a queryable semantic memory

Usage:
  /remarkable-memory sync [--notebook <name>] [--project <name>] [--since <Nd>] [--yes]
                                          Pull new/changed pages, extract, cluster
  /remarkable-memory <question>            Ask the memory in plain language
  /remarkable-memory review [--min-confidence <0-1>]
                                          Correct low-confidence extractions (teaches the reader)
  /remarkable-memory clusters | browse     Re-render + open the HTML cluster browser
  /remarkable-memory feedback              Rate the last answer/extraction
  /remarkable-memory config                Set preferences
  /remarkable-memory setup                 Connect a reMarkable (MCP / rmapi / hosted)
  /remarkable-memory reset                 Clear skill preferences (your memory is preserved)
  /remarkable-memory help                  This help

Examples:
  /remarkable-memory sync --notebook "Human Memory" --since 30d
  /remarkable-memory extract my notes about the Amsterdam music festival
  /remarkable-memory show layouts inspired by my living-room design from the past 20 days
  /remarkable-memory review --min-confidence 0.8

Memory store (git-versioned, human-editable):
  {memory-root}/
    ├── memory.json              ← index: every note, cluster, confidence, provenance
    ├── notes/                   ← one Markdown file per extracted page
    ├── clusters/<slug>/         ← cluster.md + index.html + assets/ (thumbnails)
    ├── assets/                  ← raw synced page renders / sketches / images
    ├── corrections.md           ← every human correction (the learning signal)
    ├── extraction-guide.md      ← learned handwriting/shorthand guide (fed to the extractor)
    └── html/index.html          ← top-level memory browser (all clusters)

Current preferences:
  (loaded from preferences.md)
```

## Config

Fire ONE `AskUserQuestion` (multi-question) to collect:

1. **Memory root** — where the memory store lives (default `~/remarkable-memory/`)
2. **Connection** — `mcp` (reMarkable MCP server, free/open-source), `rmapi` (CLI), or `remarkdown` (hosted, zero-install, paid)
3. **Cluster style** — `topic` / `project` / `hybrid`
4. **Confidence threshold** — how sure the reader must be before a note is trusted vs flagged (default `0.75`)
5. **Tone** — `friendly-cli` / `detailed` / `minimal`

Save to `~/.claude/skills/remarkable-memory/preferences.md`:

```markdown
# /remarkable-memory preferences
Updated: {date}

## Defaults
- memory-root: {path}
- connection: {mcp|rmapi|remarkdown}
- extract-engine: {vision|myscript}
- confidence-threshold: {0-1}
- cluster-style: {topic|project|hybrid}
- open-html: {true|false}
- tone: {friendly-cli|detailed|minimal}

## Projects (optional — edit freely)
<!-- Map reMarkable notebooks/folders to project names, e.g.: -->
<!-- - "Human Memory" notebook  → project: human-memory-posts -->
<!-- - "Home" folder            → project: living-room-design -->
```

The learned patterns live in `{memory-root}/extraction-guide.md`, not here.
Confirm warmly: "Saved. I'll use this as the baseline and keep sharpening as you correct extractions."

## Reset

`reset` deletes **only** `~/.claude/skills/remarkable-memory/preferences.md`.
It **never** touches the memory store (`{memory-root}`) — your notes, corrections,
and learned handwriting guide are your data and stay put (and remain git-versioned).
Confirm exactly what was deleted and remind the user their memory is intact:
"Cleared skill preferences. Your memory store at {memory-root} — notes, corrections,
and the learned guide — is untouched."

## First-time detection

If no preferences file exists, show a warm, non-blocking intro:

```
First time running /remarkable-memory — here's the shape of it:

  I turn your handwritten reMarkable pages into a memory you can actually query.
  On each sync I pull new pages, render each to an image and read the handwriting
  (Claude vision — I'm good at messy and cursive, and I don't need an OCR key),
  and save each page as a small Markdown file with a confidence score and a note
  of exactly where it came from. I group notes into topic/project clusters and
  render a clean HTML page for each one.

  Then you just ask:
    /remarkable-memory extract my notes about the Amsterdam music festival
    /remarkable-memory show layouts inspired by my living-room design, last 20 days

  Anything I'm unsure about I flag instead of guessing. When you run
  `/remarkable-memory review` and fix an extraction, I save that correction and
  read your hand better next time.

  Your memory is a plain, git-versioned folder — every note is a file you can
  open, edit, or revert. Nothing is a black box.

  To reach your tablet I need a connection. If you haven't set one up:
    /remarkable-memory setup
  Otherwise, continue and I'll preflight it for you.
```

Then proceed to Step 0. After the first successful sync, offer to save a couple of
quick prefs (memory root, cluster style) inline — don't force the full config flow.

## Setup — connect a reMarkable

When invoked as `/remarkable-memory setup` (or when Step 0 preflight fails and the
user asks for help), walk them through connecting a tablet. Load
`reference/connection-setup.md` for the full, device-level detail (it includes the
concrete USB happy-path). The short version:

```
Three ways to connect your reMarkable — pick one:

  1. reMarkable MCP server  (recommended, free, open-source)
     Reads your tablet and hands pages to me directly. Works over USB (no
     subscription), SSH (developer mode), or cloud (needs reMarkable Connect).
     Install: github.com/SamMorrowDrums/remarkable-mcp — then add it to your
     MCP config.  ⚠ Restart Claude Code afterwards — new MCP tools only load at
     session start, so a same-session preflight will fail until you do.

  2. rmapi  (CLI, free)
     A Go tool for the reMarkable cloud API. One-time pairing code from
     my.remarkable.com. Note: rmapi returns reMarkable's .rm lines format —
     good for typed text + metadata, but the handwriting-image path needs the
     MCP server (or a local .rm→PNG renderer). Prefer Option 1 for handwriting.

  3. remarkdown  (hosted, zero-install, paid)
     Nothing to run locally; pair once with a code. Hands pages to me as images
     I read directly. Easiest, but a paid service holding a token server-side.
     remarkdown.org  (check current pricing)

Reality checks:
  • Wireless/cloud sync needs reMarkable Connect (~$3.99/mo). USB and SSH are free.
  • The cloud API is community-reverse-engineered and can change — if a sync
    suddenly fails, that's usually why, not your notes.
  • First-time MCP setup: add the server, RESTART the client, then re-run setup.
```

After the user restarts and says they're connected, run the Step 0 preflight. If it
passes: "Connection good. Try `/remarkable-memory sync` to pull your first pages."

## Sync — ingest pages into memory

### Step 0 — Preflight (connection check)

Before touching the tablet, verify the chosen `connection` is live:
- `mcp` / `remarkdown` → confirm a reMarkable MCP tool is available in this session
  (look for a `mcp__*remarkable*` read/list tool). If none, the server isn't
  connected **in this session** — most often it was added without restarting the
  client. Route to `/remarkable-memory setup` (restart step).
- `rmapi` → `rmapi account` (or `rmapi ls`) succeeds.

If the preflight **fails**, do NOT retry blindly. Show the cause and route to
`/remarkable-memory setup`. One retry allowed if the user says "retry".

### Step 1 — Scope the sync (with notebook discovery)

Parse flags from `$ARGUMENTS`:
- `--notebook <name>` — limit to one reMarkable notebook/folder (e.g. "Human Memory")
- `--project <name>` — tag everything synced with this project (maps via preferences → Projects)
- `--since <Nd>` — only pages modified in the last N days
- `--yes` — skip the plan confirmation (for trusted repeat syncs)
- No flags → sync everything changed since the last sync (read `memory.json → last_sync`)

**Resolve the notebook name before syncing** — a mistyped name must never silently
sync nothing:
1. List the source's notebooks/folders (via the MCP list tool or `rmapi ls`).
2. If `--notebook` is given, fuzzy-match it (case-insensitive, ignore folder
   nesting). On an exact/clear match, proceed. On **no match**, stop and show what
   exists: "I don't see a notebook called '{name}'. I see: {list}. Which one?"
   On multiple plausible matches, ask which.

Echo a crisp plan and wait for `go` (skip this gate if `--yes`):

```
Sync plan:
  ├── Source:     {resolved notebook or "all notebooks"}
  ├── Window:     {since Nd or "changed since last sync (YYYY-MM-DD)"}
  ├── Project:    {project or "auto (inferred per notebook)"}
  ├── Engine:     {vision (page-image) | myscript}
  └── New/changed pages detected: {N}   (I'll skip unchanged pages)

Reply 'go' to extract, or tweak the scope.  (add --yes next time to skip this)
```

### Step 2 — Pull pages + assets (idempotent)

For each in-scope page:
1. Fetch page content via the connection. Typed (Type Folio) text comes back as
   text directly. Handwritten pages: request the source's **page-image render**
   (e.g. a `remarkable_image`-style tool) so the page arrives as an image.
2. **Assets** — pull embedded images/sketches and the page render into
   `{memory-root}/assets/{notebook-slug}-p{page}.png`. (This is what "sync all
   assets from my Human Memory notebook" means — the visuals, not just words.)
3. Record provenance: notebook name, page number, reMarkable doc id, modified
   timestamp.

**Idempotency (cheap, no image hashing):** key each page by
`{rm_doc_id}:{page}:{modified}` using the source's modification timestamp. If that
key already exists in `memory.json`, the page is unchanged — **skip it without
pulling the render** (the whole point is to avoid re-extracting unchanged pages). If
the doc id + page exist but `modified` advanced, re-extract and replace the note,
keeping its id. Never duplicate a page.

### Step 3 — Extract (Claude vision + learned guide)

**Read the page image directly — do not call a server OCR-text tool.** The keyless
"Claude reads your handwriting" promise only holds via the image path: the source
hands over a page render and *you* (Claude) read it in context. On Claude Code,
server-side sampling OCR is unavailable and a server's own OCR backend needs a
Google Vision key or degrades to Tesseract — so ignore those tools and read the
image yourself. (On Claude Desktop, server-side sampling also works, but the image
path is still the simplest and is what the Desktop companion uses.)

**Load `{memory-root}/extraction-guide.md` first** and treat it as ground truth
about this user's hand and shorthand. For each page produce:

- `text` — the transcribed content, cleaned into readable Markdown (preserve lists,
  headings, arrows→"→", checkboxes)
- `type` — one of `idea | note | todo | quote | sketch | diagram | design | list`
- `confidence` — 0-1, honest: legible print → high; messy cursive, ambiguous
  words, or a mostly-visual page → lower. When unsure of a specific word, keep it
  and mark it `⟨uncertain: word?⟩` inline rather than silently guessing.
- `tags`, `entities` — topics and named things (people, places, projects)
- `summary` — one line

Write one file per page to `{memory-root}/notes/` (schema in
`reference/memory-schema.md`), with frontmatter carrying `id`, `source` (notebook,
page, rm_doc_id, modified, synced), `confidence`, `type`, `tags`, `entities`,
`cluster`, `assets`, and `reviewed: false`.

### Step 4 — Cluster

Assign each note to a cluster per `cluster-style`:
- `topic` → semantic subject (e.g. `human-memory`, `amsterdam-music-festival`,
  `living-room-design`)
- `project` → the mapped project/notebook
- `hybrid` → project as the top group, topic as sub-cluster

Reuse an existing cluster when the subject matches (check `memory.json → clusters`);
only create a new one when nothing fits. Write/update
`{memory-root}/clusters/{slug}/cluster.md` (title, one-paragraph summary, member
note ids, key entities, date range).

### Step 5 — Update index + render + commit

1. Update `memory.json`: append/replace notes, refresh clusters, set `last_sync`.
2. Render HTML (see **Render**) for touched clusters + the top-level index.
3. `git -C {memory-root} add -A && git commit -m "sync: {scope} — +{N} notes, {M} clusters"`
   so every sync is a revertible checkpoint.
4. Report:

```
Synced {N} pages → {new} new notes, {updated} updated.
  Clusters touched:  {list}
  ⚠ Flagged for review ({k}, confidence < {threshold}):  {short list}

Next:
  Review the flagged ones →  /remarkable-memory review
  Browse the clusters      →  /remarkable-memory clusters
```

If `open-html: true`, open `{memory-root}/html/index.html` (`open` on macOS,
`xdg-open` on Linux; best-effort — skip silently if neither exists).

## Query — ask the memory

For free-text input (the default route), answer from the memory, not from thin air.

1. **Retrieve** — `Grep`/`Glob` across `{memory-root}/notes/` and read
   `memory.json` for tags, entities, clusters, and dates. Honor filters embedded in
   the ask ("past 20 days" → date window on `source.modified`; "living-room design"
   → cluster/entity match). Prefer recall over precision here — gather candidates,
   then read the note files.
2. **Empty-memory bridge** — if the memory has **no matching notes** (common on a
   fresh install, and note that "extract my notes about X" reads like a fetch but
   searches local memory), don't dead-end. Say so and offer to sync: "I don't have
   notes on {topic} yet. Want me to sync the notebook they're in? Which notebook?"
   Then hand off to Sync with that scope.
3. **Ground every claim** — cite the source note id + notebook/page for anything
   you assert. Never invent a note.
4. **Reason / synthesize** — match the ask:
   - "extract my notes about X" → collect matching notes, present them grouped, and
     offer to promote them into their own cluster.
   - "show layouts inspired by my living-room design, last 20 days" → retrieve the
     relevant design notes/sketches in the window, then *synthesize* new layout
     ideas that build on them (clearly labeled as generated, with the source notes
     they draw on).
   - "sync … so you get the latest" → this is really a `sync` request; run Sync
     scoped to that notebook, then answer.
5. **Confidence-aware** — when an answer leans on a low-confidence note, flag it:
   "(from a page I only read at 0.6 — worth a `review`)".
6. Offer to render the result as a cluster HTML page if it's substantial.

## Render — HTML per cluster

Generate a **single self-contained** `index.html` per cluster and a top-level
`{memory-root}/html/index.html` browser. Load
`reference/report-template.html` on demand; otherwise generate to this aesthetic
(a rendered sample lives in `examples/human-memory-posts.html`):

- **Modern 2026** — system font stack, generous whitespace, soft shadows, 12-16px
  radii, pill badges. Match the site vocabulary: dark `#121212` ground, `#ff5722`
  primary accent, `#03a9f4` secondary, hairline borders, faint surfaces.
- **Light + dark** via `prefers-color-scheme`, CSS variables only. Explicit
  background on `body`.
- **Mobile-responsive**, single column on small screens.
- **Inline the icon** from `~/.claude/skills/remarkable-memory/icon.svg` at ~32px
  next to the H1, colored with the accent so it themes.
- **No external scripts/fonts** — one file, opens anywhere.

**Assets must resolve.** Cluster pages live at `clusters/<slug>/index.html`, so a
root-relative `assets/foo.png` would 404. Before rendering a cluster, `cp` each
referenced asset into `{memory-root}/clusters/<slug>/assets/` and reference it as
`assets/foo.png` **relative to the cluster page**. The top-level `html/index.html`
similarly references `../assets/...` or its own copied thumbnails.

Per-cluster page:
1. **Header** — cluster title, one-line summary, date range, note count, an
   "avg confidence" meter.
2. **Note cards** — one card per note: the transcribed text (Markdown → HTML), a
   **confidence badge** (green ≥ threshold, amber below), the provenance line
   (📓 notebook · p.N · synced date), tag chips, and any asset thumbnail. Cards
   below the threshold get a subtle amber left-border and a non-interactive
   "flagged — run /remarkable-memory review" hint. `⟨uncertain: word?⟩` markers
   render as a dotted-underline highlight.
3. **Entities** — a chip row of the people/places/projects in this cluster.
4. **Provenance is always visible** — every card says exactly which page it came
   from. The memory is auditable by design.

Top-level `html/index.html`: a card grid of all clusters (title, note count, date
range, avg confidence, top entities), sorted by most-recently-touched, each linking
to its cluster page. Inline vanilla JS only for filter/sort — no framework.

## Review & learning

The learning loop is the point: corrections make the reader better, and it's all
human-readable and revertible.

### `/remarkable-memory review`

1. Find notes with `reviewed: false` and `confidence < confidence-threshold`
   (or `--min-confidence`). Sort lowest-confidence first.
2. **Offer a batch path first.** If more than ~5 are flagged, render/refresh the
   affected cluster HTML and point the user at its "⚠ Needs review" filter so they
   can eyeball all flagged pages at once, then ask: "Bulk-accept the ones that read
   correctly, and we'll walk only the genuinely ambiguous ones?" Bulk-accepted notes
   get `reviewed: true` with a small confidence bump.
3. For each remaining (one at a time), show the page asset + the current
   transcription, then ask via `AskUserQuestion`:
   - **Looks right?** → mark `reviewed: true`, bump confidence, move on.
   - **Fix the text** → the user edits; save the corrected note.
   - **Wrong cluster / tags** → re-assign.
   - **Skip** / **Stop**.
4. On any correction, append to `{memory-root}/corrections.md`:

```markdown
## {note id} — {date}
- Notebook/page: {notebook} p{n}
- I read:   "{original transcription snippet}"
- Correct:  "{user's fix}"
- Lesson:   {one-line generalization — e.g. "user's 'rm' means reMarkable, not remove"}
```

5. **Promote stable patterns.** When the same lesson recurs (a shorthand, a label
   convention, a letterform the reader keeps missing), add it to
   `{memory-root}/extraction-guide.md` — the file the extractor reads on every
   sync. Tell the user: "Learned: {pattern}. I'll apply it going forward."
6. `git commit` the corrections so the learning history is itself versioned.

### `/remarkable-memory feedback`

Rate the most recent answer/extraction (nailed it / close / missed) plus a free-text
note. Append to `{memory-root}/corrections.md` and promote clear signal to
`extraction-guide.md`. Both files are human-editable — respect whatever the user
writes there directly.

## Principles

1. **Provenance or it didn't happen.** Every extracted note records its notebook,
   page, doc id, and sync date. Every answer cites the notes it stands on. Never
   assert something the memory doesn't contain.
2. **Confidence is honest, low confidence is visible.** A page you half-read is
   flagged, never silently trusted. Uncertain words are marked inline, not guessed.
3. **The memory is plain files, git-versioned.** Markdown + JSON in a folder the
   user owns, edits, and reverts. No black box, no lock-in.
4. **Corrections are the product.** The system gets better by reading the user's
   hand, learning their shorthand from real fixes — captured in a human-editable
   guide in the memory store, not a hidden model.
5. **Read the image, not a server's OCR text.** Extract by reading the page render
   with Claude vision; it's better on messy/cursive and needs no third-party key.
   Never route through a server OCR tool on Claude Code (it needs a key or degrades).
6. **Idempotent sync.** Key pages by `doc_id:page:modified`; re-syncing skips
   unchanged pages without even pulling their render.
7. **Reuse clusters, don't shred.** Match into existing clusters; create new ones
   only when nothing fits.
8. **Honest about the platform.** The reMarkable cloud API is community-maintained
   and can break; say so when a sync fails instead of blaming the user's notes.
9. **Never delete the user's data.** `reset` clears skill preferences only; the
   memory store (notes, corrections, learned guide) is sacrosanct.
10. **Warm, terse CLI tone.** One friendly line to open and close; the work speaks
    for itself.
