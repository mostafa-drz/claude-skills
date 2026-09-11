# Memory schema

The store is plain files. This is the contract — for the skill, for the user editing by
hand, and for **other skills that read this memory as input** (a flashcard generator, a
todo board, a shopping assistant). Treat it as a public interface: additive changes are
fine, renames and removals are breaking.

`version` in `memory.json` exists so a consumer can tell which shape it's reading.
Current version: **1**.

---

## Store layout

```
{memory-root}/                    ← git repo, NO REMOTE, never pushed
├── memory.json                   ← the index
├── notes/<id>.md                 ← one per screenshot
├── clusters/<slug>/
│   ├── cluster.md
│   ├── index.html
│   └── assets/                   ← copies, so the page resolves standalone
├── assets/
│   ├── <id>.png                  ← the canonical image for each note
│   └── originals/                ← originals swept out of the inbox
├── corrections.md                ← every human correction, append-only
├── extraction-guide.md           ← learned guide, fed to the extractor each sync
├── kinds.md                      ← live kind registry
├── html/index.html               ← top-level browser
└── .gitignore                    ← .DS_Store
```

---

## Note file

`notes/2026-09-11-slack-diego-abi-deadline.md`

```markdown
---
id: 2026-09-11-slack-diego-abi-deadline
hash: sha256:9f2c4b1e…                  # identity — survives rename, copy, move
kind: chat                              # course | chat | product | ui | other | <learned>
app: Slack                              # read from pixels; "unknown" is valid
captured: 2026-09-11T16:46:23Z          # kMDItemContentCreationDate — the moment
extracted_at: 2026-09-11T18:20:00Z      # when THIS text was produced — bumps on re-extraction
capture_type: selection                 # selection | window | display | imported
origin_path: ~/Desktop/Screenshot 2026-09-11 at 12.46.18 PM.png
asset: assets/2026-09-11-slack-diego-abi-deadline.png
pixels: [1416, 1096]
confidence: 0.88                        # how well the pixels were read — nothing else
sensitive: false
reviewed: false
cluster: ateam-client-work
tags: [abi, deadline, canada]
entities: [Diego, ABI]
summary: Diego asking for the ABI Canada requirements doc before Friday.
fields:                                 # shape depends on `kind` — see kinds.md
  who: Diego
  channel: "#abi-canada"
  ask: Confirm the Canada requirements doc
  due: 2026-09-13
---

Diego asked in **#abi-canada** whether the requirements doc is confirmed:

> "can you confirm the Canada requirements doc before Friday? legal wants it signed off"

Thread also mentions ⟨uncertain: Priya?⟩ is handling the legal review.
```

### Field rules

| field | rule |
|---|---|
| `id` | `YYYY-MM-DD-<app-or-source>-<slug>`, unique across the store |
| `hash` | `sha256:` + the file digest. **The identity.** Two files with one hash are one note. |
| `confidence` | 0-1, honest, about legibility only. A human confirming it does **not** raise it. |
| `reviewed` | `false` until a human has looked. **This** is what clears the review flag. |
| `sensitive` | `true` → `text` and `fields` are absent by design. Never quote such a note. |
| `captured` | from macOS metadata, not file mtime (mtime changes on copy) |
| `extracted_at` | set every time the note body is (re)generated. **Not** the same as `hash`: `hash` identifies the image and never changes, so it cannot detect a re-extraction. This is what the review staleness check compares. |
| `fields` | keys defined by `kind` in `kinds.md`; absent keys mean "not visible in the capture", never "unknown value invented" |

Body text is **structured extraction plus key quotes** — the lines that carry meaning
verbatim, the rest summarised. Not an OCR dump. `⟨uncertain: word?⟩` marks a genuine
ambiguity and renders as a dotted underline in HTML.

---

## `memory.json`

```json
{
  "version": 1,
  "memory_root": "~/screenshots-memory",
  "last_sync": "2026-09-11T18:20:00Z",
  "notes": [
    {
      "id": "2026-09-11-slack-diego-abi-deadline",
      "hash": "sha256:9f2c4b1e…",
      "extracted_at": "2026-09-11T18:20:00Z",
      "kind": "chat",
      "app": "Slack",
      "captured": "2026-09-11T16:46:23Z",
      "confidence": 0.88,
      "sensitive": false,
      "reviewed": false,
      "cluster": "ateam-client-work",
      "tags": ["abi", "deadline"],
      "entities": ["Diego", "ABI"],
      "summary": "Diego asking for the ABI Canada requirements doc before Friday.",
      "asset": "assets/2026-09-11-slack-diego-abi-deadline.png"
    }
  ],
  "clusters": [
    {
      "slug": "ateam-client-work",
      "title": "A-team client work",
      "summary": "Client asks, deadlines and requirements across ABI and Heineken.",
      "notes": ["2026-09-11-slack-diego-abi-deadline"],
      "kinds": {"chat": 6, "course": 1},
      "entities": ["Diego", "ABI", "Heineken"],
      "date_range": ["2026-08-02", "2026-09-11"],
      "avg_confidence": 0.81
    }
  ]
}
```

`notes[]` is a denormalised index for fast filtering — the note file is the source of
truth. If they disagree, the file wins and the index should be rebuilt.

---

## Reading this memory from another skill

The supported read path, in order of preference:

1. **`memory.json`** for filtering — kind, date, cluster, tags, entities, confidence.
2. **`notes/<id>.md`** for the content of a specific note.
3. **`assets/<id>.png`** for the image itself.

Two rules for consumers:

- **Honour `sensitive: true`.** Those notes have no text on purpose. Don't infer it from
  the image and write it somewhere else.
- **Respect `confidence` and `reviewed`.** A note at 0.6 that nobody has checked is a
  reasonable thing to surface with a caveat, and a poor thing to assert as fact.

A consumer should never write into this store. Corrections flow through
`/screenshots-memory review`, which keeps `corrections.md` and the git history coherent.
