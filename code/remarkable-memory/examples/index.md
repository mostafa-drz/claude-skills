# /remarkable-memory — sample output

What a rendered cluster page looks like, so you can see the skill's output without
owning a reMarkable or running a sync.

- [Quickstart](quickstart.html) — copy-paste recipes for everyday use: connecting a
  tablet, the morning sync-and-reflect ritual, asking the memory, handing a topic to
  another agent, and teaching it your handwriting. Filterable, with a copy button on
  every command.
- [Human Memory — post ideas](human-memory-posts.html) — a topic cluster of 5
  handwritten pages: confidence badges, provenance on every card, inline
  `⟨uncertain⟩` markers, and two pages flagged for review. **Everything works** —
  click any chip to filter (several at once, they union), flip on ⚠ Needs review to
  narrow to the flagged pages, or hit **Review** on a card to correct it and
  **Copy for Claude** — then paste that block into Claude Code, where
  `review --apply` writes the corrections and commits them. Self-contained — open it in any browser (thumbnails are
  inline SVG stand-ins for real page renders).

The live skill writes these into `{memory-root}/clusters/<slug>/index.html` and a
top-level `{memory-root}/html/index.html` browser, using
`reference/report-template.html`.
