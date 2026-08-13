# Memory store schema

The memory is a plain, git-versioned folder. Everything here is human-readable and
hand-editable — the user can open, fix, or revert any file. Load this reference when
you need the exact shapes; the SKILL.md summary is enough for normal syncs.

```
{memory-root}/
├── memory.json              ← the index (source of truth for what's synced)
├── notes/                   ← one Markdown file per extracted page
│   └── {id}.md
├── clusters/
│   └── {cluster-slug}/
│       ├── cluster.md       ← human-readable cluster summary + member list
│       ├── index.html       ← rendered single-file view (2026 aesthetic)
│       └── assets/          ← thumbnails/copies used by this cluster's page
├── assets/                  ← raw synced page renders + embedded sketches/images
│   └── {notebook-slug}-p{n}.png
├── corrections.md           ← append-only log of every human correction
├── extraction-guide.md      ← learned handwriting/shorthand guide (read every sync)
└── html/
    └── index.html           ← top-level cluster browser
```

## `memory.json`

The index. Keep it small and stable — it's what makes sync idempotent and query fast.

```json
{
  "version": 1,
  "memory_root": "~/remarkable-memory",
  "last_sync": "2026-08-12T10:04:00Z",
  "notes": [
    {
      "id": "2026-08-12-human-memory-p3-encoding-loop",
      "file": "notes/2026-08-12-human-memory-p3-encoding-loop.md",
      "page_key": "a1b2c3:3:2026-08-11T21:15:00Z",   // rm_doc_id : page : modified-timestamp — the idempotency key
      "notebook": "Human Memory",
      "page": 3,
      "confidence": 0.62,
      "type": "idea",
      "tags": ["human-memory", "encoding"],
      "entities": ["hippocampus"],
      "cluster": "human-memory-posts",
      "assets": ["assets/human-memory-p3.png"],
      "reviewed": false,
      "modified": "2026-08-11T21:15:00Z",
      "synced": "2026-08-12"
    }
  ],
  "clusters": [
    {
      "slug": "human-memory-posts",
      "title": "Human Memory — post ideas",
      "style": "project",
      "note_ids": ["2026-08-12-human-memory-p3-encoding-loop"],
      "entities": ["hippocampus", "encoding", "recall"],
      "date_range": ["2026-07-30", "2026-08-11"],
      "avg_confidence": 0.71,
      "updated": "2026-08-12"
    }
  ]
}
```

**Idempotency rule:** `page_key = {rm_doc_id}:{page}:{modified}` — the source's
modification timestamp, taken straight from the MCP/rmapi metadata. On sync, if a
page's key already exists, the page is unchanged → **skip it without pulling the
render** (that's the point: avoid re-extracting unchanged pages). If the doc id +
page exist but `modified` advanced, re-extract and replace the note (keeping its
id). Timestamps are cheap and stable; a content hash of the PNG render is avoided
on purpose — it would force an expensive pull just to compare, and renders aren't
byte-stable across renderer versions, so they'd churn with no ink change.

## Note file frontmatter

```yaml
---
id: 2026-08-12-human-memory-p3-encoding-loop   # {date}-{notebook-slug}-p{page}-{short-slug}
source:
  notebook: "Human Memory"
  page: 3
  rm_doc_id: "a1b2c3..."
  modified: 2026-08-11T21:15:00Z
  synced: 2026-08-12
confidence: 0.62            # 0-1, honest. < threshold ⇒ flagged for review
type: idea                  # idea | note | todo | quote | sketch | diagram | design | list
tags: [human-memory, encoding, blog-idea]
entities: [hippocampus]     # people, places, projects, named things
cluster: human-memory-posts
assets: [assets/human-memory-p3.png]
reviewed: false             # true once a human has confirmed/corrected it
---
```

Body = the transcription as clean Markdown. Conventions:

- Preserve structure: bullets, numbered lists, headings, checkboxes (`- [ ]`).
- Arrows → `→`. Boxed/circled emphasis → **bold**.
- **Uncertain words stay in place, marked** `⟨uncertain: recal?⟩` — never silently
  guess. This is what the review pass fixes, and what teaches the reader.
- If a page is mostly visual (a sketch/diagram), transcribe any labels and add a
  one-line description of the drawing; the asset image carries the rest.

## `cluster.md`

```markdown
# Human Memory — post ideas

Post ideas and neuroscience notes for the Human Memory series. Spans encoding,
consolidation, and recall; several pages sketch figure ideas.

- Range: 2026-07-30 → 2026-08-11
- Notes: 6 · Avg confidence: 0.71
- Key entities: hippocampus, encoding, recall, consolidation

## Notes
- [p3 — encoding loop](../../notes/2026-08-12-human-memory-p3-encoding-loop.md) · 0.62 ⚠
- ...
```

## Asset paths (avoid 404s in the HTML)

A note's `assets` are stored relative to `{memory-root}` (e.g.
`assets/human-memory-p3.png`). But a cluster page lives at
`clusters/<slug>/index.html`, so referencing `assets/…` there would resolve to
`clusters/<slug>/assets/…` and 404. At render time, **copy each referenced asset
into `{memory-root}/clusters/<slug>/assets/`** and reference it relative to the
cluster page. The top-level `html/index.html` copies (or reaches `../`) its own
thumbnails the same way. Never hotlink to the raw `{memory-root}/assets/` from a
nested page.

## `corrections.md` (the learning signal)

Append-only. Each entry ties a specific miss to a general lesson.

```markdown
## 2026-08-12-human-memory-p3-encoding-loop — 2026-08-12
- Notebook/page: Human Memory p3
- I read:   "recal loop via HM"
- Correct:  "recall loop via hippocampus"
- Lesson:   user abbreviates hippocampus as "HM"; double-l "recall" often written open
```

## `extraction-guide.md` (read on every sync)

The stable, promoted patterns. Start minimal; grow it only from recurring lessons.

```markdown
# Handwriting & shorthand guide — {user}

Fed to the extractor on every sync. Human-editable.

## Shorthand
- "HM" → hippocampus (in Human Memory notebook context)
- "LR" → living room (in Home/design notebooks)
- "→" → leads to / therefore

## Letterforms the reader tends to miss
- Open double-l can look like single-l ("recall", "still")
- Terminal "g" often looks like "q"

## Labels & conventions
- Boxed items = layout components; circled = priority
```
