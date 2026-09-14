# Plant records — one shape, three stores

Loaded when onboarding a plant, writing a log entry, or reading the library.

- [The shape](#the-shape)
- [profile.json](#profilejson)
- [log.jsonl](#logjsonl)
- [index.json](#indexjson)
- [Filesystem](#filesystem)
- [Google Drive](#google-drive)
- [Notion](#notion)
- [Rules that hold in every store](#rules-that-hold-in-every-store)

## The shape

One thing about the **home** (`home.md` — the learning loop, see SKILL.md) and two
things per plant: **who it is** (profile, changes rarely) and **what happened to
it** (log, append-only). Photos are read in conversation and described into the log as
text — the runtime cannot store them, so nothing here references a photo file.

```
index.json                       the library — one row per plant
home.md                          what's true about this home — read before every diagnosis
settings.json                    store preference, units, calendar on/off
plants/<id>/profile.json
plants/<id>/log.jsonl
plants/<id>/            (photos are NOT stored — see SKILL.md "Photos")
```

`<id>` is **opaque and permanent**: `plant-01`, `plant-02`. Never derived from species
or room. Both of those are expected to change — the dashboard exists partly so a wrong
identification gets corrected, and `moved` is a first-class log kind — and an id built
from them either becomes a lie or forces renaming every path that references it. Worse,
two monsteras on the same shelf would collide on one id and get merged into a single
record, which is exactly the history-destroying bug the duplicate check exists to prevent.

`display_name`, species and room are attributes. Identity is the id alone.

## profile.json

```json
{
  "id": "plant-01",
  "display_name": "The big monstera",
  "aliases": ["the big one", "the living room monstera"],
  "species": {
    "common_name": "Swiss cheese plant",
    "botanical_name": "Monstera deliciosa",
    "confidence": 0.86,
    "uncertain_because": "could be a Monstera borsigiana — the leaf fenestration pattern is similar at this size",
    "identified_from": "photo seen 2026-09-14 — large fenestrated leaves, thick petioles, aerial root at the base"
  },
  "environment": {
    "room": "living room",
    "indoor": true,
    "light": "bright indirect, ~2m from a south window",
    "drafts": null
  },
  "pot": { "diameter_cm": 24, "estimated_from": "photo", "material": "terracotta",
           "drainage": true, "sits_in_cachepot": false },
  "soil": "peat-free houseplant mix",
  "acquired": "2026-04-02",
  "last_repotted": "2026-04-02",
  "care_baseline": {
    "water_every_days": 9,
    "feed_every_days": 30,
    "rotate_every_days": 14,
    "humidity": "average room humidity is fine",
    "source": "species baseline, adjusted for terracotta and bright light"
  },
  "toxicity": {
    "pets":   { "risk": "toxic",   "basis": "calcium oxalate crystals, documented across the genus" },
    "humans": { "risk": "irritant", "basis": "same crystals — mouth and throat irritation if chewed" },
    "confidence": 0.86,
    "inherited_from_species_confidence": true
  },
  "status": "thriving",
  "archived": false,
  "calendar": [
    { "task": "water", "calendar_id": "primary", "event_id": "abc123",
      "rrule": "RRULE:FREQ=DAILY;INTERVAL=9", "created": "2026-09-14" }
  ],
  "created": "2026-09-14",
  "updated": "2026-09-14"
}
```

**Any field may carry `estimated_from`.** People do not know their pot diameter, and
cadence is derived from it — so the choice is not "guess or lose the input". Record the
estimate *and* its source (`"photo"`, `"user's rough guess"`). An estimate marked as one
is honest; an unmarked estimate is the invention the rules forbid.

**Every field may be `null`.** A profile with gaps is honest; one with invented
values is not. `species.confidence` and `uncertain_because` are required whenever
identification came from a photo — a record that loses the uncertainty gives wrong
care advice with full confidence for as long as it exists.

`care_baseline.source` says why the cadence is what it is, so it can be argued with
later.

## log.jsonl

One JSON object per line, append-only, newest last.

```jsonl
{"id":"e001","at":"2026-09-14T10:32:00Z","kind":"onboarded","detail":"Added from a photo: large fenestrated leaves, one new shoot, soil dry at the surface."}
{"id":"e002","at":"2026-09-14T10:33:00Z","kind":"watered","detail":"Soil dry 3cm down."}
{"id":"e003","at":"2026-09-21T08:10:00Z","kind":"issue","detail":"Two lower leaves yellowing from the tip inward."}
{"id":"e004","at":"2026-09-21T08:12:00Z","kind":"diagnosis","detail":"Most likely overwatering: 6 days since last water, terracotta still damp.","confidence":0.7}
{"id":"e005","at":"2026-10-02T19:04:00Z","kind":"correction","detail":"Was spider mites, not overwatering.","supersedes":"e004"}
```

Each entry carries an **id** and a full **timestamp**. A date alone cannot order two
waterings on the same day, and `"supersedes": "2026-09-21 diagnosis"` is ambiguous the
moment there are two that day — `supersedes` references an id.

`kind` is one of: `onboarded`, `watered`, `fed`, `repotted`, `rotated`, `pruned`,
`moved`, `issue`, `diagnosis`, `resolved`, `correction`, `note`.

**`resolved` closes an `issue`** and carries `"closes": "e003"`. Without it there is no
way to record "I did the thing and it worked", and since the dashboard treats an
unresolved issue as "not thriving", every plant that ever had a problem would stay
marked struggling forever.

**`status` is derived, and the log owns it.** It lives in the profile for fast reads,
but it is recomputed from the log after every entry: an open `issue` means `struggling`
(or `critical` if that is what the diagnosis said); a `resolved` that closes the last
open issue returns it to `ok`, and `thriving` is earned by new growth, not by silence.

**Never edit or delete a line.** A wrong diagnosis is corrected by appending a
`correction` that names what it supersedes. The history of being wrong is what makes
later diagnosis better — and silently rewriting it means the same mistake repeats.

## index.json

The registry, so the library can be listed without opening every profile.

```json
{
  "store": "google-drive",
  "updated": "2026-09-14",
  "plants": [
    { "id": "plant-01", "display_name": "The big monstera",
      "species": "Monstera deliciosa", "room": "living room", "status": "thriving",
      "last_watered": "2026-09-14", "water_every_days": 9, "log_entries": 5,
      "archived": false }
  ]
}
```

`store` records which backend wrote this. On a later run, a different detected store
means the library is elsewhere — stop and say so rather than starting an empty one.

The index is derived. If it disagrees with a profile, **the profile wins** and the
index gets rebuilt.

## Filesystem

The layout above, literally, rooted at `~/plants/`. The only store where an append is
a real append. **Desktop-only** — invisible from a phone, so say that before creating a
library here.

## Google Drive

Drive cannot do three things the layout assumes, and each one has to be worked around
explicitly rather than discovered at runtime.

**1. There is no content update.** `update_file` changes "only title and parent_id".
Editing a file means creating a replacement. So the log is **one file per entry**:

```
plants/plant-01/log/2026-09-14T103200Z-e001.json
plants/plant-01/log/2026-09-14T103300Z-e002.json
```

That is genuinely append-only — every write is a create, nothing is ever rewritten, and
a failed write loses one entry instead of the whole history. Read the log by listing
the folder and sorting by name.

**Everything that is not a log entry is rewritten whole**, because Drive offers no other
option: `profile.json`, `index.json`, `settings.json`, and `home.md`. `home.md` matters
most — it is appended on every correction, and it is the learning loop, so losing it
loses everything the skill has learned about this home.

The replacement protocol, in this order every time:

1. Create the new file as `<name>.new` with the full intended content.
2. Confirm it exists and reads back correctly.
3. Trash the old `<name>`.
4. Rename `<name>.new` → `<name>` (`update_file` does change titles).

Never trash first. A failure between steps leaves a recoverable state rather than
nothing, and each one is identifiable:

| what you find | what happened | what to do |
|---|---|---|
| `home.md` and `home.md.new` | interrupted between 2 and 3 | `.new` is the newer content — finish steps 3-4 |
| `home.md.new` only | interrupted after 3 | rename it; nothing is lost |
| two files both titled `home.md` | a duplicate write (Drive allows duplicate titles) | **stop** and show both — do not guess which is current |

Check for a stray `.new` at the start of any Drive run and finish or report it, rather
than writing on top of an interrupted update.

**2. Uploads are silently converted.** `create_file` states that "supported content will
be converted to Google first-party mime types" — a `text/plain` JSON upload becomes a
Google Doc, and what comes back is not what went in. Every write must set
`contentMimeType: "application/json"` **and** `disableConversionToGoogleType: true`.

**3. `read_file_content` cannot read these files.** Its supported types are Google-native,
PDF, Office, ODF and images — not JSON or plain text — and it returns "a natural language
representation" whose "format will change over time". That is unusable for parsing a care
record. Use **`download_file_content`** and base64-decode. Never `read_file_content` for
store data.

Duplicate titles are legal in Drive, so a second `index.json` can appear silently. If a
search returns two, stop and say so rather than picking one.

## Notion

Notion has no files, so the same shape maps onto a database:

| record | Notion |
|---|---|
| `index.json` | the database itself — one page per plant |
| `profile.json` | page properties (see mapping below) |
| `log.jsonl` | a child database on the page, one row per entry, sorted by date |
| _(no photos)_ | the skill cannot store images — visual observations are log entries, as in every other store |
| `home.md` | the body of the **Library page** below |
| `settings.json` | a single **Library page** in the same parent, which also carries `store`, `updated`, and each plant's `log_entries` count — a database of plant rows has nowhere to put library-level values, and the store-detection rule depends on them |

Map **every** profile field, not a convenient subset — a partial mapping cannot render
the dashboard, which needs `care_baseline.source` to explain a cadence and
`species.confidence` to badge an uncertain ID:

`display_name` → title · `aliases` → multi-select (this is how "the big one" resolves
to a plant; without it every lookup falls back to the title) · `species.botanical_name`,
`species.common_name`, `uncertain_because`, `identified_from` → text ·
`species.confidence` → number ·
`room` → **text, not select** (select options are fixed at schema creation, so a new
room would need a schema change) · `indoor`, `pot.drainage`, `pot.sits_in_cachepot`,
`archived`, `toxicity.inherited_from_species_confidence` → checkbox ·
`light`, `environment.drafts`, `soil`, `pot.material`, `pot.estimated_from`,
`care_baseline.humidity`, `care_baseline.source` → text ·
`status` → select · `acquired`, `last_repotted`, `last_watered`, `created`,
`updated` → date ·
`pot.diameter_cm`, `water_every_days`, `feed_every_days`, `rotate_every_days`,
`toxicity.confidence` → number · `calendar` → text (JSON).

**Toxicity needs four properties, not one.** The risk is per audience, and a pet-safe
plant that irritates a child is a different answer from a plant safe for both:

| field | Notion property | type |
|---|---|---|
| `toxicity.pets.risk` | `Toxicity — pets` | select (`toxic` / `irritant` / `non-toxic` / `unknown`) |
| `toxicity.pets.basis` | `Toxicity basis — pets` | text |
| `toxicity.humans.risk` | `Toxicity — humans` | select (same options) |
| `toxicity.humans.basis` | `Toxicity basis — humans` | text |

Collapsing these into one property loses the audience, and a record that cannot say
*who* a plant is dangerous to answers "is this safe around the cat?" with a guess. If
either audience is unknown, set that select to `unknown` — never copy the other
audience's value across, and never leave the property absent, which reads as safe.
`toxicity.confidence` and `inherited_from_species_confidence` apply to both.

Each plant's log is a child database; **record its `data_source_id` as a property on the
plant page**, or every log read costs a page fetch first to find it.

Nested objects flatten with a dot (`pot.diameter_cm` → `Pot diameter (cm)`). Keep
`uncertain_because` as a visible text property, not buried in the page body — it is
the field most likely to matter and most likely to be forgotten.

## Rules that hold in every store

1. **Check for an existing plant before creating one.** Match on species plus room;
   ask when unsure. Two records for one plant splits its history in half.
2. **The log only grows.** Corrections supersede, never overwrite.
3. **Write in one order: profile → log → index.** The index is disposable and can be
   rebuilt from the profiles, so it goes last. If a write fails, say which step failed
   and what state the plant is in — never report success for a partial write.
4. **Never invent a value to fill a field.** `null` is a real answer.
5. **Stores do not migrate.** Moving from Drive to Notion leaves the plants in Drive.
   Say it plainly; offer to export rather than pretending the library moved.
6. **Photos are not stored anywhere.** They are read in conversation and described into
   the log. Nothing in this schema points at an image file.
