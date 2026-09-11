# /screenshots-memory

Turns the screenshots scattered across your machine into a git-versioned memory you can
query in plain language — and that reads your particular apps better every time you
correct it.

**→ [Quickstart: copy-paste recipes](examples/quickstart.html)** — open in any browser.

---

## What it does

You screenshot things because they matter in that moment: a slide from a course, a
Slack message asking you for something, a product you liked, a UI worth stealing. Then
they scatter across your Desktop and stop being findable.

This skill reads each capture with Claude vision (no OCR key, nothing uploaded), works
out **what kind of thing it is**, and pulls the fields that matter for that kind — a
course slide gets `concept` and `definition`, a Slack capture gets `who`, `ask` and
`due`. Each becomes a small Markdown file with a confidence score and exact provenance.
Notes cluster by topic and render as single-file HTML you can open anywhere.

The whole memory is a plain folder of Markdown and JSON under git. Nothing leaves your
machine.

## Install

```bash
cp -r claude-skills/code/screenshots-memory ~/.claude/skills/
```

Then in Claude Code:

```
/screenshots-memory setup        # creates the store, verifies it has no remote
/screenshots-memory sync         # sweeps ~/Desktop
```

## Three promises, because this skill touches your files

**Your memory store is local and stays local.** It's a git repo with **no remote**, and
the skill refuses to run if one ever appears. It holds full-resolution pictures of your
screen — that only makes sense if it can never be pushed.

**Originals are deleted last, and only once the store provably has them.** With
`originals: move`, a screenshot leaves your Desktop only *after* its note is written, its
image committed into the store, and that commit verified — the hash has to match and git
has to have it. Then the inbox copy is deleted and **the store is the only copy**. If
anything fails, nothing is deleted. Only files the sync actually wrote a note for are ever
touched: never a folder, never something it skipped, never something you told it to leave
alone. Prefer `originals: copy` if you'd rather keep both.

**Sensitive captures are asked about, not assumed.** Anything that looks like
credentials, banking, medical info or a private DM is flagged during extraction, and you
get asked about all of them in **one round** at the end. You can extract it normally,
store the image with no text, or skip it entirely. The default when you don't choose is
image-only.

## Commands

| | |
|---|---|
| `/screenshots-memory sync [path]` | Pull new screenshots, extract, cluster. No path → sweeps `~/Desktop`. |
| `/screenshots-memory <question>` | Ask the memory in plain language. |
| `/screenshots-memory clusters` | Re-render and open the HTML browser. |
| `/screenshots-memory review` | Correct low-confidence reads — this is what teaches it. |
| `/screenshots-memory review --apply` | Apply a batch of reviews collected in the HTML page. |
| `/screenshots-memory config` | Set preferences. |
| `/screenshots-memory reset` | Clear skill preferences. **Your memory is preserved.** |

```
/screenshots-memory sync ~/Downloads --since 7d
/screenshots-memory what did Slack ask me to do last week
/screenshots-memory products I saved in August
/screenshots-memory everything from the Claude skills course
```

## Kinds

Classification happens first, because it decides which fields are worth extracting.

| kind | what gets pulled out |
|---|---|
| `course` | topic · concept · definition · source |
| `chat` | who · channel · ask · due |
| `product` | product · price · vendor · url · why |
| `ui` | pattern · notable · reusable_idea |
| `other` | note |

**Kinds are yours to extend.** When captures don't fit — or the same unfamiliar shape
shows up three times in one sync — the skill proposes a new kind rather than quietly
filing them under `other`. The registry is a plain Markdown file at
`{memory-root}/kinds.md` you can edit directly.

## How it gets better

Every extraction carries an honest confidence score. Anything below your threshold is
**flagged**, never silently trusted, and an ambiguous word is marked `⟨uncertain: word?⟩`
inline rather than guessed.

When you fix one, the correction is saved to `corrections.md`, and recurring patterns
get promoted into `extraction-guide.md` — the file the extractor reads on every sync.
That's how it learns that the dark sidebar with `#` channels is your Slack, that "ABI"
is a client and not a typo, and how your course platform lays out its slides.

Both files are plain Markdown. Edit them directly if you'd rather just tell it.

Reviewing is fastest in the browser: open a cluster, flip **⚠ Needs review**, and each
card gets a Review popover you fill in against the actual image. Hit **Copy for Claude**
and paste the batch back with `/screenshots-memory review --apply`.

## The store

```
~/screenshots-memory/            ← git, no remote, never pushed
├── memory.json                  ← the index (other skills can read this)
├── notes/                       ← one Markdown file per screenshot
├── clusters/<slug>/             ← cluster.md + index.html + assets/
├── assets/                      ← the screenshots themselves
├── corrections.md               ← every correction you've made
├── extraction-guide.md          ← what it has learned about your screen
├── kinds.md                     ← your kind registry
└── html/index.html              ← the browser
```

Every note is a file you can open, edit, or revert. Nothing is a black box.

## Built to be read by other skills

`memory.json` and the note frontmatter are a documented contract
([`reference/memory-schema.md`](reference/memory-schema.md)), so another skill can build
on this memory — flashcards from your `course` captures, a todo board from your `chat`
ones, a shopping shortlist from `product`.

Two rules for anything consuming it: honour `sensitive: true` (those notes have no text
on purpose), and respect `confidence` / `reviewed` — an unreviewed 0.6 is fine to
surface with a caveat and poor to assert as fact.

## Related skills

- **`/organize-screenshots`** — one-shot: file a folder of screenshots for a PR or bug
  report. Use it when you want files tidied *now*. Use `/screenshots-memory` when you
  want them **remembered**.
- **`/capture-screens`** — generates screenshots from a web app via Playwright. A
  producer; this is a consumer.
- **`/shop-research`** — researches products properly. This just remembers the ones you
  screenshotted.

## Requirements

- macOS for automatic inbox discovery (uses Spotlight's `kMDItemIsScreenCapture`).
  On Linux it falls back to filename patterns and tells you it did.
- `git`. No API keys, no OCR service, no network.
