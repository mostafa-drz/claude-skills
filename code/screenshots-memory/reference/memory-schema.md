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
├── assets/<id>.<ext>             ← the one canonical image per note (source extension kept)
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
asset: assets/2026-09-11-slack-diego-abi-deadline.png   # source extension, not always .png
pixels: [1416, 1096]
confidence: 0.88                        # how well the pixels were read — nothing else
sensitive: false
reviewed: false
applied_rules: [slack-sidebar]          # guide rules used on this note; [] if none
cluster: ateam-client-work
tags: [abi, deadline, canada]
entities: [Diego, ABI]
summary: Diego asking for the ABI Canada requirements doc before Friday.
fields:                                 # shape depends on `kind` — see kinds.md
  who: Diego
  channel: "#abi-canada"
  ask: Confirm the Canada requirements doc
  due: 2026-09-13
  status: open                          # open | done — only on a chat note with an ask
  done_at: null                         # set when it's marked done
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
| `status` | `open` or `done`, present **only** on a `chat` note whose `ask` is non-null, defaulting to `open`. Screenshots of Slack asks are obligations; without a way to tick one off, the memory can list what was asked but never what's outstanding. Set by `/screenshots-memory done`. |
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
  "skipped": [
    { "hash": "sha256:4a1b…", "declined": "2026-09-11" }
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

`skipped[]` records captures the user declined during the sensitive round: hash and date
only, no text and no image. Sync consults it alongside `notes[]` so a declined capture is
never re-read or re-prompted. It is the one place the memory records something it
deliberately did **not** keep.

`notes[]` is a denormalised index for fast filtering — the note file is the source of
truth. If they disagree, the file wins and the index should be rebuilt.

---

## Reading this memory from another skill

The supported read path, in order of preference:

1. **`memory.json`** for filtering — kind, date, cluster, tags, entities, confidence.
2. **`notes/<id>.md`** for the content of a specific note.
3. **The path in the note's `asset` field** for the image itself — the copy git tracks, and
   the only one once
   the user's Trash is emptied.

Two rules for consumers:

- **Honour `sensitive: true`.** Those notes have no text on purpose. Don't infer it from
  the image and write it somewhere else.
- **Respect `confidence` and `reviewed`.** A note at 0.6 that nobody has checked is a
  reasonable thing to surface with a caveat, and a poor thing to assert as fact.

A consumer should never write into this store. Corrections flow through
`/screenshots-memory review`, which keeps `corrections.md` and the git history coherent.

## Why deletion verifies the committed bytes

Step 8 deletes the user's original once the store provably holds it. Two checks that look
sufficient are not, and both fail silently:

**Hashing the working-tree asset proves nothing about the commit.** With
git-lfs or any clean filter — including one installed globally, needing nothing in this
repo — the committed blob is a pointer, not the image. The working-tree hash matches, the
commit exists, the note exists, the original is deleted, and the picture is gone.

**`git log -- <path>` answers truthily for a path HEAD no longer contains.** A file
committed and later removed still returns its deletion commit.

Both collapse into one check that reads the bytes actually stored:

```bash
blob=$(git -C {memory-root} rev-parse HEAD:{asset})   # {asset} from the note; proves HEAD holds it
git -C {memory-root} cat-file blob "$blob" | shasum -a 256    # proves the committed bytes
```

This is also the only check that touches the blob, so it is the only one that would notice
on-disk corruption. `rev-parse` and `git log` read commit and tree objects and never look
at a rotted blob.

Deletion then goes to the system trash rather than `rm`, because every failure mode here is
silent at the moment of deletion and discovered days later, when the user goes looking for a
screenshot that isn't there. Once the trash is emptied, git history is the only copy — and a
later `reset --hard` or `gc` can take that.
