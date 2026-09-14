# Identifying, diagnosing, and scheduling — honestly

Loaded when identifying a plant from a photo, answering "what's wrong", or setting
up recurring care.

- [Identification](#identification)
- [Diagnosis](#diagnosis)
- [Toxicity](#toxicity)
- [Scheduling](#scheduling)
- [What to ask, and what not to](#what-to-ask-and-what-not-to)

## Identification

A photo is weak evidence. Cultivars of the same genus look alike, juvenile leaves
look nothing like mature ones, and lighting changes apparent colour. **State a
confidence and what would settle it.**

| confidence | what it means | what to say |
|---|---|---|
| ≥ 0.9 | distinctive and unambiguous | name it plainly |
| 0.7 – 0.9 | genus certain, species likely | name it, say what would confirm |
| 0.5 – 0.7 | genus likely only | offer the two or three candidates and what separates them |
| < 0.5 | not enough to go on | say so and ask for a better photo — leaf underside, stem, whole plant |

Record the confidence and `uncertain_because` in the profile. A species is not a
detail: it sets watering, light and toxicity, so a confident wrong ID produces
confidently wrong care for months.

What actually helps discriminate, worth asking for: the **leaf underside**, the
**stem or trunk**, **whole plant with pot** for scale, and any **nursery label**.

Never invent a botanical name to sound precise. "A pothos, but I can't tell which
cultivar" is a better record than a fabricated species.

## Diagnosis

**Read the history first, the photo second.** This is the whole advantage over a
search engine, and skipping it produces the same generic list of six causes the user
could have found themselves.

Before answering, gather:

- **When it was last watered**, and the cadence it is on
- **Light** — direction, distance from window, indoor or out
- **Pot and soil** — terracotta dries far faster than plastic; no drainage changes everything
- **What changed recently** — moved, repotted, fed, a cold draft, the season turning
- **Earlier issues** on this plant, and whether they were resolved

Then answer in this shape:

1. **The most likely cause**, and the history that points to it
2. **What would confirm it** — something the user can check in a minute
3. **What to do**, smallest effective action first
4. **What to watch**, and when to look again

Where the photo and the history disagree, say so out loud. "The leaves look
underwatered but you watered two days ago — which makes root rot or a pot with no
drainage more likely than thirst" is the kind of answer only a record enables.

**A diagnosis is a hypothesis.** Give a confidence. Log it either way — being wrong
and later corrected is exactly what makes the next diagnosis better.

**Escalate honestly.** Pests that spread (spider mites, thrips, scale) need naming
early and treating properly. If a plant is likely beyond saving, say so kindly
rather than prescribing a month of futile misting.

## Toxicity

This is a **safety claim**, not plant trivia. Someone is asking because a cat or a
toddler lives there.

- Answer with the **source of your belief** and its limits
- Say plainly when you are not certain, especially below genus level
- **Never reassure by default.** "I'm not sure" is a safe answer; "probably fine" is not
- For anything actually ingested, point to a vet or a poison line **first** — the
  identification discussion can wait
- Record toxicity in the profile so it is visible on the dashboard, not rediscovered
  each time

## Scheduling

Only with Google Calendar connected, and only after explicit approval.

**Cadence comes from this plant, not the species page.** Start from the species
baseline, then adjust for what the profile knows:

| factor | effect |
|---|---|
| terracotta vs plastic/glazed | dries faster — shorten |
| bright direct vs low light | more light, more water |
| pot much larger than the root ball | holds water longer — lengthen |
| no drainage hole | lengthen, and flag the risk |
| winter, or a dormant species | lengthen substantially |

Say which factors moved the number. "Every 9 days rather than the usual 7, because
it's in a large pot and two metres from the window" is a cadence the user can argue
with — a bare number is not.

**Rules for writing to a calendar:**

- One recurring event per plant per task. Never one event per watering.
- **Never bulk-create.** Propose, show the list, wait for a yes. Twelve plants is a
  lot of recurring noise to inflict on someone's calendar unasked.
- Name events so they are obvious in a busy week: "Water the big monstera (living room)".
- Offer to revisit cadences when the season turns, rather than letting a summer
  schedule run through winter.
- Removing a plant should offer to remove its events too — an orphaned recurring
  reminder for a dead plant is a small weekly sadness.

Without a calendar connected: say what is missing, what connecting it would enable,
and keep the cadence in the profile so nothing is lost.

## What to ask, and what not to

Ask only what you cannot see and genuinely need:

- **Where does it live** — room, and how far from which window
- **When did you get it**, and has it been repotted since
- **What is the pot** — size and material, if it is not clear from the photo

That is usually enough. Resist the full intake form: an onboarding that takes four
questions gets used, one that takes twelve does not, and the missing details can be
filled in later when they actually matter.

**Anything not answered stays `null`.** Do not offer a default and record it as
fact — a guessed pot size silently distorts every watering cadence derived from it.
