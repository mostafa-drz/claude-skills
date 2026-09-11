---
name: screenshots-memory
description: >-
  Turns scattered screenshots into a queryable, git-versioned memory. Syncs
  captures from ~/Desktop or any folder or file you point at, reads each image
  with Claude vision — no OCR key, no upload — and extracts it into a
  confidence-scored Markdown note with full provenance: when it was captured,
  which app it came from, where it lived. Classifies every capture by kind —
  course material, chat and reminders, products, UI inspiration, or kinds the
  user defines — and pulls kind-specific fields from each. Clusters by topic,
  renders a single-file HTML page per cluster, and answers plain-language
  questions ("what did Slack ask me to do last week", "products I saved in
  August"). Asks before writing down anything sensitive, flags low-confidence
  reads for review, and learns the user's apps from every correction. Use when
  the user wants to sync, extract, organize, search, declutter, or reason over
  their screenshots, turn a messy Desktop into a searchable memory, or build a
  second brain from the things they screenshot.
argument-hint: "[sync|review|clusters|browse|feedback|config|setup|reset|help] [path|glob] [--since <Nd>] [--kind <name>] [--min-confidence <0-1>] [--yes] [text query...]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(mdfind *)
  - Bash(mdls *)
  - Bash(shasum *)
  - Bash(git *)
  - Bash(mkdir *)
  - Bash(cp *)
  - Bash(ls *)
  - Bash(date *)
  - Bash(open *)
  - Bash(xdg-open *)
  - Bash(df *)
  - Bash(rm *)
---

# Screenshots Memory

Sync screenshots from anywhere on disk into a git-versioned semantic memory, read each
one with Claude vision, extract kind-aware structured notes with real provenance,
cluster them by topic, render clean HTML per cluster, answer questions over them, and
get sharper at reading your particular apps every time you correct an extraction.

A screenshot is a snapshot of a moment you cared about. This skill stops those moments
from rotting in a folder.

_New here? [`README.md`](./README.md) is the human-facing overview, and
[`examples/quickstart.html`](./examples/quickstart.html) has copy-paste recipes for
everyday use._

## Preferences

_On startup, use Read to load `~/.claude/skills/screenshots-memory/preferences.md`.
If it's missing, treat this as first-run (see **First-time detection**)._

Defaults when no preferences exist:
- `memory-root`: `~/screenshots-memory/` (confirmed on first run; git-init'd so every change is diffable and revertible)
- `inbox`: `~/Desktop` (where loose screenshots pile up; synced when no path is given)
- `originals`: `move` (`move` = once the store's copy is committed and hash-verified, the inbox original is **deleted** — the store becomes the only copy · `copy` = inbox original left alone)
- `confidence-threshold`: `0.75` (extractions below this are flagged for `review`, never silently trusted)
- `cluster-style`: `topic` (subject-based; `kind` is a filter chip on the page, not a folder)
- `sensitive-policy`: `ask-batched` (flag during extraction, ask about all of them in one round at the end)
- `open-html`: `true` (auto-open the cluster HTML when a sync finishes)
- `tone`: `friendly-cli` (terse, warm, direct)

_The extraction guide, kind registry and corrections log live in the **memory store**,
not the skill dir — so they're versioned with the user's data and survive `reset`. On
startup, load `{memory-root}/extraction-guide.md` if it exists and treat it as ground
truth about **this user's** screen: which apps they use, that "ABI" is a client and not
a typo. Feeding it to the extractor every sync is what makes the memory improve._

## Context

_On startup, use Bash to detect today's date (`date +%Y-%m-%d`), whether `memory-root`
exists and is a git repo, and the OS (`open` on macOS, `xdg-open` on Linux). Do NOT scan
for screenshots yet — that happens inside `sync`, after the safety preflight._

## Command routing

Check `$ARGUMENTS`:
- `help` → show Help, stop
- `config` → run Config, stop
- `reset` → delete **skill preferences only** (see **Reset**); the memory store is preserved. Confirm first, stop
- `setup` → create and verify the memory store (see **Setup**), stop
- `sync` → ingest new screenshots into memory (see **Sync**)
- `review --apply` → **test before plain `review`** — `--apply` is followed by a fenced
  ```json block from a cluster page's popovers; apply that batch in one pass
- `review` (no `--apply`) → walk low-confidence extractions one at a time (see **Review & learning**)
- `clusters` / `browse` → (re)render and open the HTML cluster views (see **Render**)
- `feedback` → rate the last answer/extraction (see **Review & learning**)
- anything else → if it resolves to an existing path or glob, treat as a **scoped sync**;
  otherwise treat as a **query** (see **Query**)

**Every command that writes starts with the Step 0 safety preflight.**

## Help

Load [`reference/interface.md`](./reference/interface.md) and print the usage block it
carries, filling in the user's actual preferences and current store stats (capture count,
cluster count, how many are flagged for review).

## Config

Fire ONE `AskUserQuestion` (multi-question) collecting memory root, inbox, originals
policy, confidence threshold and tone — the defaults are listed under **Preferences**
above. Save the answers to `~/.claude/skills/screenshots-memory/preferences.md` in the
file format given in [`reference/interface.md`](./reference/interface.md). The kind
registry lives in `{memory-root}/kinds.md`, not here.

Confirm warmly: "Saved. I'll use this as the baseline and keep sharpening as you correct
extractions."

## Reset

`reset` deletes **only** `~/.claude/skills/screenshots-memory/preferences.md`. It
**never** touches the memory store — notes, screenshots, corrections and the learned
guide are the user's data and stay put, still git-versioned. Confirm exactly that:
"Cleared skill preferences. Your memory store at {memory-root} is untouched."

## First-time detection

If no preferences file exists, show a warm, non-blocking intro:

```
First time running /screenshots-memory — here's the shape of it:

  You screenshot things because they matter in that moment. Then they scatter across
  your Desktop and stop being findable. I turn them into a memory you can query.

  On each sync I read every new screenshot with Claude vision (no OCR key, nothing
  uploaded), work out what KIND it is — course notes, a Slack ask, a product, a UI
  worth stealing — and pull the fields that matter for that kind. Each becomes a
  small Markdown file with a confidence score and exact provenance. I group them into
  topic clusters and render a clean HTML page per cluster you can browse.

  Then you ask:  /screenshots-memory what did Slack ask me to do last week

  Three promises, because this skill touches your files:
    · Your memory store is a LOCAL git repo with no remote. It is never pushed.
    · An original leaves your Desktop only after its note is committed and verified.
    · Anything sensitive gets flagged and I ask before writing it down.

  Nothing I'm unsure about gets silently guessed — it gets flagged. When you run
  `/screenshots-memory review` and fix an extraction, I save that correction and read
  your screen better next time.

  Ready? `/screenshots-memory setup`, or just `sync` and I'll set it up as we go.
```

Then proceed. After the first successful sync, offer to save a couple of quick prefs
(memory root, originals policy) inline — don't force the full config flow.

## Setup — create and verify the store

1. Create `{memory-root}` and `git init` it. `git init` on an existing repo is a no-op,
   so the directory may already be one — possibly one with a remote.
2. **Check for a remote before writing anything.** If `git -C {memory-root} remote` is
   non-empty, stop: this store would be pushable. Never commit first and check after.
   If the directory is already a repo **with commits**, this is not a fresh setup — say
   so and ask, rather than writing a starter `kinds.md` over the user's own.
3. Write the starter `kinds.md` (copy from `reference/kinds.md`), an empty
   `corrections.md`, an empty `extraction-guide.md`, a `memory.json` skeleton
   (`{"version": 1, "notes": [], "clusters": [], "last_sync": null}`), and a
   `.gitignore` containing `.DS_Store`.
4. Commit: `chore: initialize screenshots memory`.
5. Re-run the full **Step 0 preflight** and report the result.

Tell the user plainly what now exists and where, and that it has no remote.

## Sync — ingest screenshots into memory

### Step 0 — Safety preflight (run before anything writes)

Four checks, in order. Any failure stops the sync — do not work around them.

1. **Store exists and is a git repo.** If not, offer `setup`.
2. **The store has NO git remote.** `git -C {memory-root} remote` must be empty. This
   check is the *only* thing enforcing it: `allowed-tools` cannot express "git but never
   push" for a `git -C <path>` invocation, so the guarantee lives in this step's logic,
   not in the permission layer. Treat it as load-bearing and never skip it.
   If a remote exists, **STOP** and say so:
   "{memory-root} has a remote ({name} → {url}). This store holds full-resolution
   screenshots of your screen and must never be pushed. Remove the remote
   (`git -C {memory-root} remote remove {name}`) and re-run, or point me at a
   different store." Never push, never add a remote, never commit past this check.
3. **The store's working tree is clean.** Uncommitted changes mean a previous run was
   interrupted or the user edited notes by hand. Show them and ask before proceeding —
   never discard. Every command that writes into the store commits before it returns, so
   a dirty tree is genuinely unexpected and should never be routine.
4. **Enough disk headroom** — ~1 MB per screenshot, roughly doubled by the commit.

### Step 1 — Scope the sync

Parse `$ARGUMENTS`:
- a **path, folder or glob** → sync exactly that
- `--since <Nd>` → only captures created in the last N days
- `--kind <name>` → only ingest captures that classify as this kind
- `--yes` → skip the plan confirmation (for trusted repeat syncs)
- no path → sweep the **inbox** (`~/Desktop` by default)

**Discovery rules differ by scope, deliberately:**
- **Inbox sweep** — only what macOS itself calls a screenshot:
  `mdfind -onlyin {inbox} 'kMDItemIsScreenCapture == 1'`. This is what makes a sweep
  safe: it can never pick up a folder, a document, or a photo the user merely saved there.
- **Explicit path** — any image (`png jpg jpeg heic webp`). Pointing at a photographed
  whiteboard or a saved product image is a deliberate choice, and it's honoured.

On Linux, or if `mdfind` returns nothing on a folder that clearly holds screenshots, fall
back to filename patterns (`Screenshot*`, `Screen Shot*`, `CleanShot*`) **and say you
did** — never sync a folder by a different rule than the one you announced.

### Step 2 — Identify and deduplicate

For each candidate, compute `shasum -a 256 <file>`.

Skip anything whose hash is in `memory.json`'s `notes` **or** its `skipped[]` list.

**The hash is the identity** — not the path, not the filename. Screenshots get renamed,
copied and duplicated; a content hash makes the same capture one note however many copies
exist. If the hash is already in `memory.json`, skip the file, and say it's a duplicate of
an existing note so the user can delete it with confidence.

Read the provenance macOS already stores (verify per file; don't assume):

```bash
mdls -name kMDItemContentCreationDate -name kMDItemScreenCaptureType \
     -name kMDItemIsScreenCapture -name kMDItemPixelWidth -name kMDItemPixelHeight <file>
```

`kMDItemContentCreationDate` is the capture moment — more trustworthy than mtime, which
changes on copy. macOS does **not** record the source app, window title or URL; those come
from reading the pixels in Step 4.

### Step 3 — Plan gate

Echo a crisp plan and wait for `go` (skip only if `--yes`):

```
Sync plan:
  ├── Source:      {resolved path or "inbox (~/Desktop)"}
  ├── Window:      {since Nd or "all"}
  ├── Found:       {N} screenshots  ({D} already in memory, skipped)
  ├── To read:     {M} images · ~{X} MB
  ├── Originals:   DELETED from {source} once the store's copy is committed and
  │                hash-verified — the store becomes the only copy. This is the only
  │                irreversible thing I do. (Set `originals: copy` to leave them.)
  └── Store:       {memory-root}  (local git, no remote)

Reply 'go' to extract, or tweak the scope.  (add --yes next time to skip this)
```

**Be honest when the batch is big.** Every screenshot is a vision read. Above ~40, say so
and offer to narrow with `--since` or run in batches — a first sync against a neglected
folder can be hundreds of images.

### Step 4 — Extract (Claude vision + learned guide)

**Read each image directly.** No OCR service, no API key, nothing leaves the machine.

**Load `{memory-root}/extraction-guide.md` and `{memory-root}/kinds.md` first** and
treat them as ground truth about this user's screen. For each screenshot produce:

1. **`kind`** — classify first; it decides everything downstream. Ships with `course`,
   `chat`, `product`, `ui`, `other`. If a capture fits none well, say so and propose a
   new kind rather than forcing a bad fit — see [`reference/kinds.md`](./reference/kinds.md).
2. **`app`** — the application or site, read from the visible chrome (Slack's sidebar, a
   browser URL bar, a terminal prompt). `unknown` is an honest answer; a guess is not.
3. **`summary`** — one line: what this capture *is*, in the user's terms.
4. **`fields`** — the kind-specific payload, per that kind's schema in
   [`reference/kinds.md`](./reference/kinds.md). A field not visible in the capture is
   omitted, never invented.
5. **`text`** — **structured extraction plus key quotes**, not a transcription. Keep the
   lines that carry the meaning verbatim and summarise the rest: a long article becomes
   its claim and two quotable lines, not four paragraphs of OCR. Mark a genuinely
   ambiguous word `⟨uncertain: word?⟩` inline rather than guessing it.
6. **`tags`, `entities`** — topics and named things (people, products, projects, clients).
7. **`confidence`** — 0-1, honest. Crisp UI text → high; low-contrast, tiny, cropped
   mid-word or mostly-visual → lower. It measures *how well you read the pixels*, nothing else.
8. **`sensitive`** — true for credentials, tokens, banking or card details, medical
   information, private DMs, or anything else that shouldn't become plain text in a repo.
   **Flag, keep going — do not ask yet.**

### Step 5 — Sensitive review (one batched round)

If anything was flagged, ask about **all of it in a single round** before writing those
notes — never one interruption per screenshot:

```
3 of 27 captures look sensitive. The image is stored unless you skip it entirely;
otherwise this is only about whether I write the text into the repo.

  1. Banking dashboard — RBC, balance visible      (Screenshot … 1.22.32 PM)
  2. DM with Diego — appears personal              (Screenshot … 9.28.31 AM)
  3. Terminal showing what looks like an API token (Screenshot … 10.16.52 AM)
```

Offer per item: **Extract normally** · **Store image only** (keeps kind, date and
provenance, no text) · **Skip entirely** (not ingested; original left where it is).
Default to **Store image only** if the user declines to choose.

**Record a skip.** Append `{hash, declined: {date}}` to `skipped[]` in `memory.json` — no
text, no image, no note. Step 2 honours that list alongside the notes, so a capture the
user declined is never re-read, never re-prompted, and never costs another vision read.
Without this it sits in the inbox and the next sync asks again, forever. An image-only note is a
real note with `sensitive: true` and no `text`/`fields` — findable by date and kind
without leaking its contents.

### Step 6 — Cluster

Assign each note to a **topic** cluster — the subject, not the kind. Since `kind` is a
filter chip, a product shot of a lamp and a UI shot of a room planner can share a
`home-design` cluster. Reuse an existing cluster when the subject matches (check
`memory.json → clusters`); create one only when nothing fits. Write/update
`{memory-root}/clusters/{slug}/cluster.md` (title, summary, member ids, entities, kind
mix, date range).

### Step 7 — Write, render, commit

1. Write one note file per screenshot to `{memory-root}/notes/` (schema in
   [`reference/memory-schema.md`](./reference/memory-schema.md)), setting
   `extracted_at` to now. **Set it again on every re-extraction** — adding a kind and
   re-running captures against it counts — because that field is what lets a later
   `review --apply` tell a stale correction from a current one.
2. Copy the image to `{memory-root}/assets/{id}.png`.
3. Update `memory.json`: append notes, refresh clusters, set `last_sync`.
4. Render HTML (see **Render**) for touched clusters + the top-level index.
5. Commit **the paths this sync touched** — `notes/`, `assets/`, `memory.json`,
   `clusters/`, `html/` — not `add -A`. Check 3 can be waived by the user, and `-A` would
   then sweep their unrelated hand edits into the sync commit.

**The tree must be clean when this step ends.** Verify with `git -C {memory-root} status
--porcelain` and stop if it isn't — a sync that leaves the store dirty makes the next
sync's preflight check 3 fire falsely, which trains the user to wave it through.

### Step 8 — Delete the inbox originals (last, never first)

The capture now lives in the store, committed, at `assets/{id}.png`. Only if
`originals: move`, the inbox original is redundant and is **deleted**. Say "deleted", not
"moved" or "retired" — the user is entitled to know the store is now the only copy.

**Verify before removing anything.** For each original, all three must hold:
`shasum -a 256 {memory-root}/assets/{id}.png` equals the note's recorded hash (strip its
`sha256:` prefix first, or nothing ever matches) · `git -C {memory-root} log --oneline -1
-- assets/{id}.png` returns a commit · the note file exists. Only then `rm` the inbox
original; if any check fails, leave it, say why, and carry on.

- Delete **only** files this sync wrote a note for — never a folder, never a skipped file,
  never anything the discovery rule didn't select.
- A capture that couldn't be read still gets a flagged note and is still deleted, so
  nothing is silently abandoned *or* silently lost.
- A capture the user chose to **skip entirely** stays exactly where it is.
- If Step 7's commit failed, **delete nothing**. Say so and stop.

This creates no new files, so the tree stays clean. The sweep is **resumable and
idempotent**: a failed file is reported and left alone without aborting the batch, and an
interruption between Step 7 and here is harmless — the note and asset are already
committed, so re-running dedupes by hash and deletes whatever is left.

Then report:

```
Synced {N} screenshots → {new} new notes, {dupes} already known.
  Kinds:      course {a} · chat {b} · product {c} · ui {d}
  Clusters:   {list}
  Sensitive:  {s} stored image-only, {d} declined
  Inbox:      {M} originals deleted (store is now the only copy) · {left} left in place
  ⚠ Flagged for review ({f}, confidence < {threshold}):  {short list}

Next:  /screenshots-memory review   ·   /screenshots-memory clusters
```

If `open-html: true`, open `{memory-root}/html/index.html`.

## Query — ask the memory

For free-text input that isn't a path, answer from the memory, not from thin air.

1. **Retrieve** — `Grep`/`Glob` across `{memory-root}/notes/` and read `memory.json` for
   kinds, tags, entities, clusters and dates. Honour filters in the ask ("last week" →
   date window on `captured`; "products" → `kind: product`; "from Slack" → `app: Slack`).
   Prefer recall over precision, then read the note files.
2. **Empty-memory bridge** — if nothing matches (common on a fresh install), don't dead-end:
   "I don't have anything on {topic} yet. Want me to sync a folder? Which one?" Then hand
   off to Sync with that scope.
3. **Ground every claim** — cite the note id and capture date. Never invent a capture.
4. **Match the shape of the ask** — a `chat` question wants actions with `who`/`ask`/`due`
   ordered by due date, not prose; `product` wants a table grouped by vendor with prices;
   a course cluster wants capture order, so it reads as a study sequence.
5. **Confidence-aware** — when an answer leans on a low-confidence note, say so:
   "(from a capture I only read at 0.6 — worth a `review`)".
6. **Respect `sensitive`** — never quote an image-only note. Say it exists, when it was
   captured, and that its contents were deliberately not recorded.
7. Offer to render the result as a cluster page if it's substantial.

## Render — HTML per cluster

Generate a **single self-contained** `index.html` per cluster plus a top-level
`{memory-root}/html/index.html` browser, using `reference/report-template.html` for the
canonical CSS and JS so pages can never drift from each other.

**Load [`reference/render.md`](./reference/render.md) before rendering.** It carries the
page layout, the note-card anatomy, the filter-chip contract (chips OR together; the
⚠ Needs review switch ANDs), and the review-popover rules that keep a half-finished
correction from ever reaching the store.

**Rendering writes into the store, so it commits.** Every re-render path — sync,
`review --apply`, or a bare `clusters`/`browse` — commits `clusters/` and `html/` when
anything changed and says "already current" when nothing did. Uncommitted render output
would make the next preflight fire falsely.

**`flag` means low-confidence AND unreviewed — never low-confidence alone**, and every
card carries `data-reviewed`. Since a verdict of `ok` deliberately leaves `confidence`
untouched, flagging on confidence alone would strand every confirmed note in the review
view forever and drift the two review queues apart.

The one thing that silently breaks a page: cluster pages live at
`clusters/<slug>/index.html`, so every referenced image must be copied into that
cluster's own `assets/` and referenced relatively, or it 404s.

## Review & learning

The learning loop is the point: corrections make the extractor better, and it's all
human-readable and revertible.

### `/screenshots-memory review`

1. Find notes with `reviewed: false` and `confidence < confidence-threshold` (or
   `--min-confidence`). Sort lowest-confidence first.
2. **Offer the page first.** If more than ~5 are flagged, render/refresh the affected
   cluster HTML and send the user there: the **⚠ Needs review** switch shows only
   flagged captures, and each card's Review popover captures a verdict against the
   actual image — far faster than walking them in the terminal. Tell them to hit **Copy
   for Claude** when done and paste it back. Then stop and wait.
   If they'd rather stay in the terminal, continue with step 3.
3. For each remaining (one at a time), show the screenshot and the current extraction,
   then ask via `AskUserQuestion`:
   - **Looks right?** → mark `reviewed: true`, move on.
   - **Fix the text** → the user edits; save the corrected note.
   - **Wrong kind / tags / cluster** → re-assign.
   - **Skip** / **Stop**.
4. **On any correction**, record it and learn from it — append to
   `{memory-root}/corrections.md`, promote it (a lesson the user typed into the lesson
   field promotes immediately; one you inferred waits for a second occurrence) into
   `{memory-root}/extraction-guide.md` (the file the extractor reads every sync), tell
   the user "Learned: {pattern}. I'll apply it going forward.", and `git commit` so the
   learning history is versioned too. Formats and the promotion rule:
   [`reference/learning-loop.md`](./reference/learning-loop.md) — load it when reviewing.

### Applying reviews from the page

`review --apply` receives what a cluster page's **Copy for Claude** button produces: the
command line, then a fenced ```json block. Parse the array inside the fence.

**Load [`reference/learning-loop.md`](./reference/learning-loop.md) before applying a
batch** — entry schema, per-verdict write rules, the staleness check (entry
`extracted_at` vs the note's, **not** `hash`, which digests the image and never changes
on re-extraction), and the replay guard against a re-pasted batch.

Three rules too important to leave in reference:
- **`reviewed: true` clears the flag — never a confidence bump.** `confidence` records how
  well the machine read the pixels; a human agreeing doesn't improve the reading. Only
  `fix` moves it, and only to `1.0`.
- **Never invent the missing half.** An empty `reassign` on a `meta`, or empty `text` on a
  `fix`, is malformed — report it, don't guess, don't mark it reviewed.
- **Tell the user to click "Discard all"** when you're done. The browser copy is the only
  thing still holding the applied batch.

### `/screenshots-memory feedback`

Rate the most recent answer or extraction (nailed it / close / missed) plus a free-text
note. Append to `corrections.md`; promote to `extraction-guide.md` under the same rule as
stage 2 of the loop — only what recurs or is stated as a general rule. Both files are
human-editable; respect whatever the user writes there.

## Principles

1. **The store is local and stays local.** A git repo with no remote, holding pictures of
   the user's screen. The preflight enforces it; nothing here ever pushes.
2. **Move last, never first.** A file leaves its folder only after its note is committed
   and that commit verified. A failed commit means nothing moves, and only files this sync
   wrote a note for are ever touched.
3. **Provenance or it didn't happen.** Every note records its hash, capture time, app and
   original path. Every answer cites the captures it stands on.
4. **Confidence is honest, low confidence is visible.** A capture you half-read is flagged,
   never silently trusted; uncertain words are marked inline, not guessed. `reviewed` is
   what clears a flag — a human agreeing doesn't improve how well the pixels were read.
5. **Sensitive means asked, not assumed.** Flag during extraction, ask once in a batch, and
   when in doubt store the image without the text.
6. **Kind first, structure over verbatim.** Classification decides which fields matter — a
   wrong kind is worse than a slightly wrong transcription. Capture what a screenshot
   *means* plus the lines worth quoting, not an OCR dump nobody reads.
7. **The hash is the identity.** Renames, copies and duplicates collapse to one note.
8. **Corrections are the product.** The memory improves by learning this user's apps and
   shorthand from real fixes, in human-editable plain files they own, edit and revert —
   not a hidden model. Warm, terse tone throughout; the work speaks for itself.
