# /screenshots-memory — sample output

What the skill produces, so you can see its output before running a sync.

- **[sample-cluster.html](sample-cluster.html)** — a real, working cluster page. Six
  fabricated notes across four kinds; every chip filters (several at once, they union);
  the ⚠ Needs review switch ANDs with them; one card is flagged, one shows a confirmed ✓,
  one is a sensitive capture whose contents were deliberately not recorded, and one has an
  `⟨uncertain⟩` marker. Open a **Review** popover and it behaves exactly as the live skill
  does — Save stays disabled until you actually edit, and **Copy for Claude** produces the
  real `review --apply` payload.

- [Quickstart](quickstart.html) — copy-paste recipes for everyday use: creating the
  store, the Desktop sweep, asking the memory, handing it to another skill, and
  teaching it your apps. Filterable, with a copy button on every command.

The live skill writes cluster pages into `{memory-root}/clusters/<slug>/index.html` and
a top-level `{memory-root}/html/index.html` browser, using
[`reference/report-template.html`](../reference/report-template.html).

A rendered cluster page carries, per capture: the screenshot thumbnail, the extracted
summary, a kind badge, the kind-specific fields as a definition list, an honest
confidence badge, and the provenance line (📸 app · captured date). Every chip is a live
filter — several can be on at once and they union — and the **⚠ Needs review** switch
ANDs with them to narrow to flagged captures about a given subject.

Each card's **Review** popover captures a correction against the actual image and hands
the batch back via **Copy for Claude**, which you paste into
`/screenshots-memory review --apply`. The page never writes to the store itself.
