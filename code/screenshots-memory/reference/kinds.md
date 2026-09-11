# Kind registry

A **kind** is what a screenshot fundamentally *is*. It is decided first, before any
other extraction, because it determines which fields are worth pulling out. A wrong
kind is a worse error than a slightly wrong transcription — it sends the capture into
the wrong shape entirely.

This file ships as the starter registry. On `setup` it is copied to
`{memory-root}/kinds.md`, which becomes the live, user-editable version. **The copy in
the memory store wins.** Respect whatever the user writes there.

---

## How to classify

1. Read the whole image before deciding. The chrome (sidebar, tab bar, toolbar) usually
   says more about the kind than the content does.
2. Pick the kind that makes the *fields* useful. A screenshot of a product inside a
   Slack message is a `product` if the point was the product, and a `chat` if the point
   was that someone asked about it. When genuinely torn, pick the one whose fields you
   can actually fill.
3. `other` is a legitimate answer. Never stretch a capture into a kind it doesn't fit
   just to avoid it — that's exactly the signal that a new kind is needed.
4. Record the kind at the confidence you actually have. A blurry capture that is
   *probably* a course slide is still `course`, but with lower confidence.

---

## Shipped kinds

### `course` — study and reference material

Slides, lesson pages, documentation, certification material, diagrams being taught.
The feedstock for flashcards and revision.

| field | meaning |
|---|---|
| `topic` | the subject area — "Claude Skills", "SOC2 controls" |
| `concept` | the specific thing being taught on this slide |
| `definition` | the claim or definition itself, quoted closely where it matters |
| `source` | course/book/site name, module or lesson number if visible |

Extraction notes: keep the definition close to verbatim — the exact wording is the
point. Capture diagram labels as a list rather than describing the picture in prose.

---

### `chat` — conversations, asks, reminders

Slack, Teams, iMessage, WhatsApp, email threads, comment threads. These are frequently
**actions with a deadline**, not just notes, and should be extracted that way.

| field | meaning |
|---|---|
| `who` | who is asking or speaking — the person, not the handle, where you can tell |
| `channel` | channel, thread, or conversation name |
| `ask` | the actual request, in one imperative line. Null if nothing is being asked. |
| `due` | any date or deadline mentioned, resolved to `YYYY-MM-DD` against the capture date |
| `status` | `open` on extraction whenever `ask` is non-null; `/screenshots-memory done` flips it |

Extraction notes: "by Friday" on a capture from Wednesday 2026-09-09 resolves to
2026-09-11 — resolve it, and say you did. If the thread has several messages, the `ask`
is the one addressed to *this user*. Personal DMs are frequently `sensitive`.

---

### `product` — things worth buying or remembering

Product pages, listings, price comparisons, a thing spotted in a feed.

| field | meaning |
|---|---|
| `product` | name and model |
| `price` | as shown, with currency; null if not visible |
| `vendor` | shop or site |
| `url` | if a URL bar is visible in the capture — never invent one |
| `why` | why this was worth capturing, if the capture makes it inferable |

Extraction notes: never reconstruct a URL from a logo. Either it's legible in the
capture or it's null.

---

### `ui` — interface and design inspiration

Screens, components, layouts, animations, anything captured because of how it looks or
works rather than what it says.

| field | meaning |
|---|---|
| `pattern` | the interaction or layout pattern — "split-pane diff", "inline empty state" |
| `notable` | what specifically is good here |
| `reusable_idea` | the transferable lesson, in one line |

Extraction notes: describe mechanism, not decoration. "Filters persist in the URL so a
view is shareable" beats "clean modern design".

---

### `other` — genuinely doesn't fit

| field | meaning |
|---|---|
| `note` | one line on what this is |

Not a dumping ground. Three or more `other` captures of the same shape in one sync is
the trigger to propose a new kind.

---

## Learning new kinds

When a capture fits nothing, or the same unfamiliar shape appears **three or more times
in one sync**, propose a kind rather than quietly filing it under `other`:

```
5 captures don't fit the current kinds — they all look like recipes
(title, ingredients, steps).

Add a `recipe` kind?  fields: dish · ingredients · steps · source
```

On approval:
1. Append the kind and its field table to `{memory-root}/kinds.md`.
2. Re-extract those captures against the new schema.
3. Say what was added and how many notes changed.

A rejected proposal is recorded too — append it under `## Rejected kinds` in the store's
`kinds.md` with the date, so the same suggestion isn't made every sync.

## Adding a kind by hand

The user can edit `{memory-root}/kinds.md` directly. A kind needs a heading, a one-line
description, and a field table. Anything following that shape is picked up on the next
sync, no config step required.
