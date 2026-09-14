# Identifying, diagnosing, and scheduling — honestly

Loaded when identifying a plant from a photo, answering "what's wrong", or setting
up recurring care.

- [Identification](#identification)
- [Diagnosis](#diagnosis)
- [Toxicity](#toxicity)
- [Treatment safety](#treatment-safety)
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

- **How long they have had it.** Under about eight weeks, **acclimation is the most
  likely answer** — a plant dropping its oldest leaves a few weeks into a new home is
  usually nursery-to-home transition, not a problem. Check this first.
- **When it was last watered**, and the cadence it is on
- **Whether water sits underneath** — a cachepot or an undrained saucer is the single
  most common houseplant killer, and it looks exactly like underwatering
- **Light** — direction, distance from window, indoor or out
- **Pot and soil** — terracotta dries far faster than plastic
- **How fast it is progressing.** Rate is what separates normal ageing from a problem,
  and the log cannot answer it unless you ask: one leaf a month, or three this week?
- **What changed recently** — moved, repotted, fed, a cold draft, the season turning
- **Earlier issues** on this plant, whether they were resolved, and **`home.md`** —
  what you have already been wrong about in this home

Then answer in this shape:

1. **The most likely cause**, and the history that points to it
2. **What would confirm it** — something the user can check in a minute
3. **What to do**, smallest effective action first
4. **What to watch**, and when to look again

Where the photo and the history disagree, say so out loud. "The leaves look
underwatered but you watered two days ago — which makes root rot or a pot with no
drainage more likely than thirst" is the kind of answer only a record enables.

**A diagnosis is a hypothesis.** Give a confidence. Log it either way — being wrong and
later corrected is exactly what makes the next diagnosis better.

**Say when the history is thin.** Under about a month, or fewer than three log entries,
the answer is mostly general knowledge rather than this plant's record — and the
skill's whole promise is the opposite. Name which parts you are inferring and which you
would actually know in a few months. That honesty also explains why the log is worth
keeping.

**Escalate honestly.** Pests that spread (spider mites, thrips, scale) need naming
early and treating properly. If a plant is likely beyond saving, say so kindly
rather than prescribing a month of futile misting.

## Toxicity

This is a **safety claim**, not plant trivia. Someone is asking because a cat, a dog or
a toddler lives there.

**Record it per audience, typed, never free text.** `pets` and `humans` are separate
fields, each `toxic` / `irritant` / `non-toxic` / `unknown` with its own basis, because
the answers genuinely differ — a plant can be dangerous to a cat and merely unpleasant to
an adult. One blended verdict shown as general safety is how someone with a new kitten
gets reassured by a value that was about humans.

The third value matters as much as the first two: in free text, "we don't know" and "it's
fine" both end up blank, and a blank card reads as safe. `unknown` must be visible and
explicit, on the dashboard as well as in the record.

**Never claim toxicity more confidently than the identification it rests on.** A species
identified at 0.6 cannot yield a confident toxicity badge; the badge inherits the lower
confidence and says so.

**If something has already been eaten, that comes first — before any identification
discussion.** Say to go now and bring a piece of the plant.

| who | where to go |
|---|---|
| a child or adult | Poison control, or local emergency services. In the US: **1-800-222-1222**. Elsewhere, tell them to search "poison control" plus their country, or call the local emergency number |
| a pet | A vet, or an animal poison line — in the US the ASPCA line is **1-888-426-4435** (a fee applies) |

Do not wait to be asked, do not finish identifying first, and do not soften it. For
everything else: answer with the basis and its limits, and say plainly when you are not
certain. "I'm not sure" is a safe answer; "probably fine" is not.

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

- **Where does it live** — room, and how far from which window. **Most people do not
  know which way their windows face**, so do not leave them stuck: ask when the sun
  actually reaches it. Morning means east; mid-afternoon means west or south; never
  direct means north or something shading it. Record what they told you, and the
  inference separately — the observation is the fact.
- **When did you get it**, and has it been repotted since
- **What is the pot** — size and material, if it is not clear from the photo

That is usually enough. Resist the full intake form: an onboarding that takes four
questions gets used, one that takes twelve does not, and the missing details can be
filled in later when they actually matter.

**Anything not answered stays `null`.** Do not offer a default and record it as
fact — a guessed pot size silently distorts every watering cadence derived from it.

## Treatment safety

A skill this careful about what a plant does to a person should be equally careful about
what a treatment does.

- **Before recommending any pesticide** — neem, insecticidal soap, systemics — ask
  whether pets or small children share the room, and say what the product means for them.
  A systemic in a home with a cat that chews leaves is a worse problem than the pest.
- **Name the handling hazard** where one exists. Euphorbia and ficus sap is a genuine eye
  and skin irritant: say to wear gloves and keep it away from the face before suggesting
  a prune, not after.
- **Prefer the smallest effective intervention** — isolate, wipe down, correct the
  watering — before anything chemical.
