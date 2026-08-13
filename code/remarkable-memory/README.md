# /remarkable-memory

Turns handwritten reMarkable pages into a git-versioned semantic memory you can query
in plain language — and that reads your handwriting better every time you correct it.

**→ [Quickstart: copy-paste recipes](examples/quickstart.html)** — open in any browser.
Ten recipes with copy buttons, drawn from real day-to-day use.

---

## What it does

Syncs pages from a reMarkable tablet, reads the handwriting with Claude vision (no OCR
key, no third-party service), and writes each page to a small Markdown file carrying a
confidence score and exact provenance. Pages are clustered by topic, rendered as
single-file HTML, and answerable in natural language. Corrections you make are saved
and fed back into every future extraction.

The whole memory is a plain folder of Markdown and JSON under git. Nothing leaves your
machine.

## Install

```bash
cp -r claude-skills/code/remarkable-memory ~/.claude/skills/
```

Then connect a tablet — USB, SSH, or cloud:

```
/remarkable-memory setup
```

See [`reference/connection-setup.md`](reference/connection-setup.md) for device-level
detail.

## The five commands

| Command | What it does |
|---|---|
| `/remarkable-memory sync [--notebook <name>] [--since <Nd>] [--yes]` | Pull new/changed pages, extract, cluster |
| `/remarkable-memory <question>` | Ask the memory in plain language |
| `/remarkable-memory review [--min-confidence <0-1>]` | Correct low-confidence pages — this is what teaches it |
| `/remarkable-memory clusters` | Re-render and open the HTML browser |
| `/remarkable-memory help` | Usage, your preferences, and current memory stats |

Plus `config`, `feedback`, `setup`, and `reset` (which clears preferences only — never
your notes).

## Three things worth knowing before you start

**Start with one notebook.** `sync --notebook "Daily Log" --since 30d` lets you judge
extraction quality on your own handwriting before committing to a full library pull.
Re-syncing is free — pages are keyed by `doc_id:page:modified`, so unchanged pages are
skipped without even fetching the render.

**Run `review` early.** It's the step that compounds. Corrections land in
`corrections.md`, and recurring patterns get promoted into `extraction-guide.md` — a
plain file the extractor reads on every sync. Skip it and the reader never learns your
shorthand; average confidence just sits where it started. You can also seed the guide
by hand.

**Low confidence is a feature.** A half-read page is flagged rather than silently
trusted, and uncertain words are marked `⟨uncertain: word?⟩` inline instead of guessed.
Every answer cites the notebook and page it stands on.

## Memory layout

```
~/remarkable-memory/                 ← git repo, yours
├── memory.json                      ← index: notes, clusters, confidence, provenance
├── notes/                           ← one Markdown file per page (YAML frontmatter)
├── clusters/<slug>/                 ← cluster.md + index.html + assets/
├── assets/                          ← page renders
├── corrections.md                   ← every correction you've made
├── extraction-guide.md              ← learned handwriting/shorthand guide
└── html/index.html                  ← top-level browser
```

Schema: [`reference/memory-schema.md`](reference/memory-schema.md).
Sample rendered output: [`examples/index.md`](examples/index.md).

## Requirements

- A reMarkable tablet reachable over USB, SSH, or the reMarkable cloud
- The [reMarkable MCP server](https://github.com/SamMorrowDrums/remarkable-mcp)
  (recommended), `rmapi`, or a hosted equivalent
- Claude Code with the MCP server registered — **restart after adding it**; MCP tools
  only load at session start

Wireless/cloud sync needs a reMarkable Connect subscription. USB and SSH are free.
