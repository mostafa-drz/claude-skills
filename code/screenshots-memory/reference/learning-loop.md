# The learning loop

_Everything here writes to the store and commits, so the Step 0 safety preflight in
SKILL.md applies — most importantly the no-remote check. Do not commit past it._

Loaded on demand during `review`, `review --apply`, and whenever a sync meets a capture
that fits no known kind. This is everything the memory uses to get better at reading THIS
user's screen, in the order it happens: record a correction, promote what recurs, apply a
batch from the page.

A new kind is a learning event too — the proposal mechanic lives in
[`kinds.md`](./kinds.md); when one is added, record it here in `corrections.md` along
with the captures that prompted it.

## 1. Record the correction

Every correction is recorded, whether it came from the terminal or from the page. Append
to `{memory-root}/corrections.md`:

```markdown
## {note id} — {date}
- Capture: {app} · {captured date} · {kind}
- I read:   "{original extraction snippet}"
- Correct:  "{user's fix}"
- Lesson:   {one-line generalization — e.g. "the dark sidebar with # channels is Slack, not Discord"}
```

## 2. Promote what recurs

**One rule, both paths.** `corrections.md` records everything; `extraction-guide.md` —
the file the extractor reads on every sync — gets only what will still be true next time:

- a lesson that has now appeared **more than once** (an app that keeps being
  misidentified, a shorthand, a client name read as a typo), **or**
- a lesson the user stated as a general rule rather than a one-off fix ("ABI is always
  the client, never a typo").

A single idiosyncratic fix stays in `corrections.md` and does not become a standing
instruction — that is what stops the guide filling with noise that degrades extraction.

When you promote one, say so: "Learned: {pattern}. I'll apply it going forward." Then
`git commit`, so the learning history is versioned too.

## 3. Apply a batch from the page

`review --apply` receives the block a cluster page's **Copy for Claude** button
produces: the command line, then a fenced ```json block. Parse the array inside the
fence and ignore the repeated command line.

```json
[
  { "id": "2026-09-11-slack-diego-abi-deadline",
    "hash": "sha256:9f2c…", "app": "Slack", "kind": "chat",
    "captured": "2026-09-11T16:46:23Z", "extracted_at": "2026-09-11T18:20:00Z",
    "savedAt": "2026-09-11T18:41:02.512Z",
    "verdict": "fix",
    "text": "Diego needs the ABI Canada requirements doc confirmed by Friday.",
    "reassign": null,
    "lesson": "ABI is a client, not a typo" }
]
```

Every entry carries the same keys. `text` and `reassign` are **mutually exclusive** —
exactly one is non-null, decided by `verdict` — and `lesson` is optional on all three.

**Resolve the note before writing anything.** Match on `id`, falling back to `hash`.

Then compare the entry's `extracted_at` against the note's stored `extracted_at`. If they
differ, the note was re-extracted after this review was saved — the user was reading an
older render — so **skip the entry as stale**, name it, and ask them to re-review that
card. Never write a note body from an entry you could not confirm points at the version
the user actually saw.

**It must be `extracted_at`, not `hash`.** `hash` is the sha256 of the *image*, and the
image does not change when a note is re-extracted — adding a new kind re-extracts captures
against it, which is exactly the case this guard exists to catch. Comparing hashes would
match every time and catch nothing.

| `verdict` | Payload | What to do |
|---|---|---|
| `ok` | both null | The extraction read correctly. Set `reviewed: true` and **leave `confidence` unchanged**. Change nothing else. |
| `fix` | `text` = corrected extraction | Replace the note body with `text`, set `reviewed: true`, set `confidence: 1.0` — the text is now the human's, not the reader's. Log before/after to `corrections.md`. |
| `meta` | `reassign` = an instruction, e.g. `kind: product; cluster: home-design` | The extraction is fine — only the classification is wrong. Apply it, leave the body and `confidence` untouched, set `reviewed: true`, and re-render **both** the old and new cluster. |

**Guard against replay.** The page can't know you applied a batch — it keeps the reviews
until the user clicks "Discard all", and a re-rendered page reloads them. Before
writing, check whether the entry already landed: if the note is already `reviewed: true`
**and** its body already equals `text` (or the `reassign` is already reflected), this is
a re-paste. Skip it silently, count it separately, and say "N already applied". Never
re-apply a `fix` over a note that has changed since.

**A null `extracted_at` or `hash` means unverifiable — skip and report, never apply.** The
staleness check is only a guard if it can run; an entry missing either field cannot be
confirmed to target the version the user saw, and treating null as "nothing to compare"
would bypass the guard on precisely the entries that are most broken.

The page guarantees five things about this payload — trust them, and fail loudly if they
don't hold: every `verdict` was explicitly clicked by a human; the field its verdict
requires holds content the human supplied (for `fix`, text **actually edited** away from
the rendered extraction); every entry has an `id`; no two entries share one; and every entry carries a non-null `extracted_at` and `hash`,
since Review is disabled on any card missing them. An entry
violating any of these is malformed — skip it and say so.

**Never invent the missing half.** If a `meta` entry's `reassign` is empty, or a `fix`
entry's `text` is empty, don't guess and don't mark it reviewed — report it and move on.

**`reviewed: true` is what clears the flag — never a confidence bump.** `confidence`
records how well the machine read the pixels; a human agreeing doesn't make the reading
better, so `ok` leaves it alone. Only `fix` moves it, and only to `1.0`. This also keeps
the two review queues identical: the page's ⚠ Needs review switch and the terminal's
`reviewed: false` **and** `confidence < threshold` must select the same notes.

Then run stages 1 and 2 exactly as the terminal path does: append every change to
`corrections.md`, and promote a `lesson` into `extraction-guide.md` **only** when it
recurs or is stated as a general rule. Re-render the touched clusters — this is what
clears confirmed cards out of the page's ⚠ Needs review view, so it is load-bearing, not
cosmetic — then `git commit`.

Finally, **tell the user to click "Discard all"** on the page — the browser copy is the
only thing still holding the applied batch. Report what changed and what you learned:

```
Applied 6 reviews — 4 confirmed, 2 corrected.
  Learned: the dark sidebar with # channels is Slack (added to extraction-guide.md)
  Click "Discard all" on the cluster page to clear the batch.
```

