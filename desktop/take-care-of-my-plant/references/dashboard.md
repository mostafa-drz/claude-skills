# The dashboard artifact

Loaded when the user asks to see their plants. The store stays the source of truth:
regenerate the dashboard rather than updating a stale one.

**It is a published page.** A self-contained artifact necessarily embeds the plant
records it displays, so it starts private and should only be shared deliberately —
worth one line to the user rather than a silent assumption.

## Two views, one file

From the original sketch: a searchable list, and a detail view per plant.

**Sort by most-overdue-first.** The spec calls next-water "the thing actually being
looked for" — so it decides the order. On a phone that ordering *is* the list's value;
search is secondary (nobody searches ten plants, and the keyboard eats half the screen).

**Put the build date in the header.** People screenshot this and look at it on Thursday.

**List** — one card per plant: display name, species (with a confidence badge when it is
uncertain), room, status, toxicity, and *when it next needs water* — which is the thing
actually being looked for. A search box filters by name, species or room.

**Detail** — opens from a card: the profile, the care baseline with the reasoning behind
the cadence, toxicity with its basis, and the care log as a timeline.

There are no photo thumbnails: the skill does not store photos (see SKILL.md
"Photos"). The log's written observations carry the visual history instead — render
those in full rather than truncating, since they are all there is to compare against.

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

**Toxicity is visible at a glance, including when it is unknown.** Toxic belongs on the
card — someone with a new kitten should be able to scan the list. So does `unknown`,
rendered as its own visible state: if it falls back to blank, an unknown plant looks
identical to a safe one. And never badge toxicity more confidently than the species ID
it was inherited from.

**Archived plants are hidden by default**, reachable behind a toggle, and never counted
in "needs water". A plant that died should not nag every week.

**Empty states say what to do.** No plants yet: say how to add one (send a photo). No log
entries yet: say that, rather than rendering an empty timeline.

## Look

Match the other memory skills so the family is recognisable: system font stack,
generous whitespace, 12–16px radii, pill badges, hairline borders. Dark `#121212`
ground with `#ff5722` primary and `#03a9f4` secondary; light and dark via
`prefers-color-scheme`, CSS variables only, explicit `body` background.

Single column on a phone. Photos are the point — give them room, and lazy-load them.

## What it must not do

- **Never write to the store.** The dashboard is read-only. Edits go through
  conversation, so they get logged. But **close the loop**: a card showing "overdue 2
  days" should say the sentence that fixes it — *say "watered the big monstera" to log
  it*. Read-only is right; leaving the user to work out the next move is not.
- **Detail is a full-screen view with a thumb-reachable back control**, not a modal.
- **Never invent a field to fill a layout.** A missing pot size renders as absent,
  not as a guess.
- **Never render a field the store does not have.** A missing pot size is absent, not a
  guess — and an absent toxicity value is `unknown`, not blank.
