---
name: remarkable-memory
description: >-
  Turns handwritten reMarkable notes into a queryable semantic memory, on Claude
  Desktop. Pulls pages from a reMarkable tablet through a connected reMarkable MCP
  server (or remarkdown), reads the handwriting with Claude vision — no OCR key —
  and extracts each page into confidence-scored, provenance-tagged notes stored in
  a connected memory (Filesystem, Google Drive, or Notion). Clusters notes by topic
  and project, renders a clean HTML artifact per cluster, and answers plain-language
  questions over them ("extract my notes about the Amsterdam music festival", "show
  layouts inspired by my living-room design from the past 20 days"). Flags
  low-confidence reads for review and learns your handwriting and shorthand from
  every correction. Use when the user wants to sync, extract, organize, search, or
  reason over their reMarkable notes and build a second brain from handwritten pages.
---

# reMarkable Memory (Desktop)

Turn handwritten reMarkable pages into a queryable, confidence-scored memory —
clustered, cited, and rendered as clean HTML artifacts — right inside Claude
Desktop. This is the connector-based companion to the `/remarkable-memory` Claude
Code skill; both share one philosophy: **provenance always, low confidence
visible, corrections are the product, memory is human-editable.**

## What you need connected

Detect these at the start of every run and report what's present:

- **A source** — a reMarkable MCP server (e.g. `SamMorrowDrums/remarkable-mcp`) or
  `remarkdown` (hosted). This is how pages reach the conversation. Look for
  `mcp__*remarkable*` tools.
- **A memory store** — one persistence connector so the memory survives across
  conversations: **Filesystem**, **Google Drive**, or **Notion** (in that
  preference order). Without one, you can still extract and render for this
  session, but say clearly that nothing will persist.

```
Connected:
  ✅ Source:  reMarkable MCP (USB mode)
  ✅ Memory:  Google Drive  → folder "reMarkable Memory"
  ❌ Notion:  not connected
```

If no source is connected, stop and walk the user through connecting one:

```
Connect a reMarkable source (pick one):
  • reMarkable MCP server (free) — enable "USB web interface" on the tablet
    (Settings → Storage), plug in, confirm http://10.11.99.1 loads, then add the
    server in Settings → Connectors.
  • remarkdown (hosted, paid) — pair once with a code, add its connector. It hands
    pages to me as images I read directly (works well on Desktop).

Then add a memory connector (Filesystem / Google Drive / Notion) so the memory
persists across conversations.

⚠ After adding any connector, RESTART Claude Desktop — connectors load at startup,
so I won't see a just-added source until you relaunch.
```

Reality checks: USB/SSH are free; cloud sync needs reMarkable Connect (~$3.99/mo);
SSH needs developer mode, which factory-resets the tablet. The community cloud API
can change — if a sync breaks, that's usually why, not the notes.

**Extraction:** read each page as an **image** and transcribe it yourself. Claude
Desktop supports MCP sampling, but the image path is simplest and avoids any
server-side OCR key — use it.

## Memory layout (in the connected store)

Mirror the Code skill so a user can move between the two:

```
reMarkable Memory/
├── memory.json          ← index: notes, clusters, confidence, provenance, last_sync
├── notes/               ← one Markdown note per page (frontmatter + transcription)
├── clusters/<slug>/     ← cluster.md + a rendered HTML artifact
├── assets/              ← page renders + sketches/images
├── corrections.md       ← every human correction (the learning signal)
└── extraction-guide.md  ← learned handwriting/shorthand guide, read on every sync
```

Note frontmatter carries: `id`, `source` (notebook, page, doc id, modified, synced),
`confidence` (0-1), `type`, `tags`, `entities`, `cluster`, `assets`, `reviewed`.
Uncertain words stay inline as `⟨uncertain: word?⟩` — never silently guessed.

## Process

### 1. Sync

- Ask (or infer) the scope: a specific notebook ("Human Memory"), a project, or a
  time window ("last 20 days"). Echo a one-line plan and get a go-ahead.
- Pull each in-scope page through the source connector. Typed pages come as text;
  handwritten pages render to images. Pull embedded **sketches and images** too —
  "sync all assets from my Human Memory notebook" means the visuals, not just words.
- **Idempotency:** key each page by doc id + page + a content hash held in
  `memory.json`. Skip unchanged pages; never duplicate.

### 2. Extract (Claude vision + learned guide)

- Read `extraction-guide.md` from the memory store first; treat it as ground truth
  about this user's hand and shorthand.
- Read each page image directly. Produce clean Markdown, a `type`, an honest
  `confidence`, `tags`, `entities`, and a one-line summary. Mark uncertain words
  inline; flag anything below the user's threshold (default 0.75) for review.
- Write one note file per page into `notes/` and update `memory.json`.

### 3. Cluster

- Group notes by topic (default), project, or hybrid. Reuse an existing cluster
  when the subject matches; create a new one only when nothing fits. Write
  `clusters/<slug>/cluster.md`.

### 4. Render — HTML artifact per cluster

_A rendered sample of the cluster look lives in the Code skill at
`code/remarkable-memory/examples/human-memory-posts.html`._


Produce a **single self-contained HTML artifact** (no external scripts/fonts) with
light + dark support via `prefers-color-scheme`, using the site's vocabulary (dark
`#121212`, primary `#ff5722`, secondary `#03a9f4`, hairline borders, faint
surfaces). Each note is a card showing: the transcription, a **confidence badge**
(green ≥ threshold, amber below), the **provenance line** (📓 notebook · p.N ·
synced date), tag chips, and any asset thumbnail. Below-threshold cards get an amber
left border and a non-interactive "run review" hint.

**Thumbnails in the artifact must be inline.** A claude.ai artifact is sandboxed
(strict CSP, no local filesystem), so `assets/*.png` or `file://` paths won't load —
embed each thumbnail as a base64 `data:` URI directly in the `<img src>` (keep them
small; mind the artifact size budget). Alternatively omit images from the artifact
and keep them only in the persisted store. Also render a top-level index artifact: a
card grid of all clusters. Save the HTML back into the memory store so it persists.

### 5. Query

For a plain-language question, answer **from the memory, with citations** — never
invent a note. Honor filters in the ask (dates, cluster, entity). When the ask is
generative ("show layouts inspired by my living-room design"), retrieve the relevant
notes/sketches first, then synthesize new ideas clearly labeled as generated, naming
the source notes they build on. If an answer leans on a low-confidence note, say so.

### 6. Review & learning

- Surface low-confidence, unreviewed notes one at a time with their page image.
  Let the user confirm, fix the text, or re-cluster.
- On every correction, append to `corrections.md` (what you read → the fix → the
  one-line lesson). When a lesson recurs, promote it to `extraction-guide.md` so the
  next sync applies it. Tell the user what you learned. Both files are
  human-editable — respect direct edits.

## Guidelines

- **Detect, don't assume** — only use connectors that are actually present; never
  fabricate a note or claim a source is connected when it isn't.
- **Cite everything** — every card and every answer names the page it came from.
- **Confidence is honest** — flag what you half-read; mark uncertain words; don't
  guess to look confident.
- **Confirm before anything irreversible** — deleting or overwriting notes needs an
  explicit OK. `reset`-style actions never touch the user's memory store.
- **Graceful degradation** — if the source or a page fails, note it and continue
  with what you got; be honest about gaps in the render.
- **Privacy-aware** — handwritten notes are personal; keep summaries to what the
  task needs and don't over-quote on a shared screen.
