# Plant records — one shape, three stores

Loaded when onboarding a plant, writing a log entry, or reading the library.

- [The shape](#the-shape)
- [profile.json](#profilejson)
- [log.jsonl](#logjsonl)
- [index.json](#indexjson)
- [Filesystem and Google Drive](#filesystem-and-google-drive)
- [Notion](#notion)
- [Rules that hold in every store](#rules-that-hold-in-every-store)

## The shape

Three things per plant: **who it is** (profile, changes rarely), **what happened to
it** (log, append-only), and **what it looked like** (photos, accumulate).

```
index.json                       the library — one row per plant
settings.json                    store preference, units, calendar on/off
plants/<id>/profile.json
plants/<id>/log.jsonl
plants/<id>/photos/YYYY-MM-DD.jpg
```

`<id>` is a slug: `monstera-deliciosa-living-room`. Species plus location, because
two of the same species in different rooms are different plants with different needs.

## profile.json

```json
{
  "id": "monstera-deliciosa-living-room",
  "display_name": "The big monstera",
  "species": {
    "common_name": "Swiss cheese plant",
    "botanical_name": "Monstera deliciosa",
    "confidence": 0.86,
    "uncertain_because": "could be a Monstera borsigiana — the leaf fenestration pattern is similar at this size",
    "identified_from": "photos/2026-09-14.jpg"
  },
  "environment": {
    "room": "living room",
    "indoor": true,
    "light": "bright indirect, ~2m from a south window",
    "drafts": null
  },
  "pot": { "diameter_cm": 24, "material": "terracotta", "drainage": true },
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
    "pets": "Toxic to cats and dogs if chewed — calcium oxalate crystals.",
    "confidence": "high for the genus; ask a vet for anything actually ingested"
  },
  "status": "thriving",
  "created": "2026-09-14",
  "updated": "2026-09-14"
}
```

**Every field may be `null`.** A profile with gaps is honest; one with invented
values is not. `species.confidence` and `uncertain_because` are required whenever
identification came from a photo — a record that loses the uncertainty gives wrong
care advice with full confidence for as long as it exists.

`care_baseline.source` says why the cadence is what it is, so it can be argued with
later.

## log.jsonl

One JSON object per line, append-only, newest last.

```jsonl
{"date":"2026-09-14","kind":"onboarded","detail":"Added from a photo.","photo":"photos/2026-09-14.jpg"}
{"date":"2026-09-14","kind":"watered","detail":"Soil dry 3cm down."}
{"date":"2026-09-21","kind":"issue","detail":"Two lower leaves yellowing.","photo":"photos/2026-09-21.jpg"}
{"date":"2026-09-21","kind":"diagnosis","detail":"Most likely overwatering: 6 days since last water, terracotta still damp.","confidence":0.7}
{"date":"2026-10-02","kind":"correction","detail":"Was spider mites, not overwatering.","supersedes":"2026-09-21 diagnosis"}
```

`kind` is one of: `onboarded`, `watered`, `fed`, `repotted`, `rotated`, `pruned`,
`moved`, `photo`, `issue`, `diagnosis`, `correction`, `note`.

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
    { "id": "monstera-deliciosa-living-room", "display_name": "The big monstera",
      "species": "Monstera deliciosa", "room": "living room", "status": "thriving",
      "last_watered": "2026-09-14", "water_every_days": 9, "photos": 3 }
  ]
}
```

`store` records which backend wrote this. On a later run, a different detected store
means the library is elsewhere — stop and say so rather than starting an empty one.

The index is derived. If it disagrees with a profile, **the profile wins** and the
index gets rebuilt.

## Filesystem and Google Drive

The layout above, literally. Root is `~/plants/` (Filesystem) or a `Plants` folder
(Drive). Drive: keep one folder per plant so photos stay next to their record.

## Notion

Notion has no files, so the same shape maps onto a database:

| record | Notion |
|---|---|
| `index.json` | the database itself — one page per plant |
| `profile.json` | page properties (see mapping below) |
| `log.jsonl` | a child database on the page, one row per entry, sorted by date |
| `photos/` | images in the page body, captioned with their date |
| `settings.json` | a single settings page in the same parent |

Property mapping: `display_name` → title · `species.botanical_name` → text ·
`species.confidence` → number · `room` → select · `indoor` → checkbox ·
`status` → select · `last_watered` → date · `water_every_days` → number ·
`toxicity.pets` → text.

Nested objects flatten with a dot (`pot.diameter_cm` → `Pot diameter (cm)`). Keep
`uncertain_because` as a visible text property, not buried in the page body — it is
the field most likely to matter and most likely to be forgotten.

## Rules that hold in every store

1. **Check for an existing plant before creating one.** Match on species plus room;
   ask when unsure. Two records for one plant splits its history in half.
2. **The log only grows.** Corrections supersede, never overwrite.
3. **Strip EXIF before storing a photo.** Phone photos carry GPS — the user's home.
4. **Write the profile and its first log entry together.** A profile with no
   `onboarded` entry looks like a plant that has never been cared for.
5. **Never invent a value to fill a field.** `null` is a real answer.
6. **Stores do not migrate.** Moving from Drive to Notion leaves the plants in Drive.
   Say it plainly; offer to export rather than pretending the library moved.
