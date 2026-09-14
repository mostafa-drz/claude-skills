# The dashboard artifact

Loaded when the user asks to see their plants. Rendered fresh from the store every
time — it is a **view**, never a second copy of the data.

## Two views, one file

From the original sketch: a searchable list, and a detail view per plant.

**List** — one card per plant: photo thumbnail, display name, species (with a
confidence badge when it is uncertain), room, status, and *when it next needs water*
— which is the thing actually being looked for. A search box filters by name,
species or room.

**Detail** — opens from a card: the profile, the care baseline with the reasoning
behind the cadence, toxicity if known, the photo history newest first, and the care
log as a timeline.

Build it as a single self-contained HTML artifact: no external scripts, fonts or
images, inline vanilla JS only. It has to work on a phone.

## What the design has to get right

**Status must be honest.** `thriving` / `ok` / `struggling` / `critical` comes from
the log, not from optimism. A plant with an unresolved `issue` entry is not
`thriving` because nobody has looked at it since.

**Surface uncertainty, don't hide it.** A species identified at 0.6 shows its
confidence on the card. The dashboard is where a wrong identification gets noticed
and corrected — burying it defeats that.

**"Needs water" is a prediction, not a fact.** It is `last_watered + water_every_days`
against a cadence that was itself an estimate. Show it as due/overdue, not as a
command, and let the detail view show what the cadence was based on.

**Toxicity is visible at a glance.** If a plant is toxic to pets, that belongs on the
card, not three taps away. Someone with a new kitten should be able to scan the list.

**Empty states say what to do.** No plants yet: say how to add one (send a photo). No
photos for a plant: say that, rather than rendering a broken image.

## Look

Match the other memory skills so the family is recognisable: system font stack,
generous whitespace, 12–16px radii, pill badges, hairline borders. Dark `#121212`
ground with `#ff5722` primary and `#03a9f4` secondary; light and dark via
`prefers-color-scheme`, CSS variables only, explicit `body` background.

Single column on a phone. Photos are the point — give them room, and lazy-load them.

## What it must not do

- **Never write to the store.** The dashboard is read-only. Edits go through
  conversation, so they get logged.
- **Never invent a field to fill a layout.** A missing pot size renders as absent,
  not as a guess.
- **Never show a photo's location metadata** — it was stripped on the way in, and
  nothing in the view should reintroduce it.
