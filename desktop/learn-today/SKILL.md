---
name: learn-today
description: >-
  Builds a daily deck of 3-5 learning picks (videos, articles, podcasts) for your work,
  business and life goals, with why and summary, learning from your feedback. Use for
  "what should I learn today".
metadata:
  side_effects: true
  trigger: "Asking what to learn, watch, read or listen to today; wanting learning picks matched to their goals; setting up a daily learning routine in a project."
  tags: "learning, growth, recommendations, youtube, podcasts, articles, life-areas, daily-routine, memory, feedback, scheduled-task, project, desktop"
---

# Learn today

A short, swipeable deck of things worth your time today: a talk, an article, a podcast
episode, a course lesson. Each card says **why it's for you** (tied to a goal or something
you're working on), **what you'll get** in three lines, and **one thing to try** after.
It mixes work, business and life the way you've asked, and it gets better every day from
your 👍 and 👎.

It starts automatically when the request matches: "what should I learn today?", "give me
something to watch on pricing", "today's learning deck". It's not a research report (use
research-assistant) or a course plan.

One reference, **read it every run**: [`picking.md`](./references/picking.md) (signals,
search, verify, write, learn). Data shape: [`evals/example-deck.json`](./evals/example-deck.json).
Defaults: [Configuration](#configuration), at the end of this file.

---

## The flow

```
Deck progress:
- [ ] 0. Settings: the chat, then saved settings in memory, then Configuration
- [ ] 1. Feedback: fold in what the user said about the last deck
- [ ] 2. Signals: goals, feedback, history, style + what's live in connected sources
- [ ] 3. Find: web search for candidates, open each one, keep the verified ones
- [ ] 4. Pick 3-5 for the mix, and write why, summary and one thing to try
- [ ] 5. Write deck.json → validate → render → show the deck
- [ ] 6. Learn: save the deck and anything new, in one line
```

### 0. Settings

Look in memory for the line starting **"learn-today settings:"**. **What the user says in
this chat wins, then the saved settings, then [Configuration](#configuration).**

### 1. Feedback first

Before anything else, look for feedback on the last deck: in this chat ("1 👍, 3 too
long"), in a pasted **learn-today feedback** line (the deck's last card makes one), or in
memory. Save it now (step 6 rules), because it changes today's picks. The strongest signal
is a reason: "too basic", "loved the speaker", "no more podcasts".

### 2. Signals

Gather in parallel, using only what's connected in this conversation. Never assume a
source from an earlier run, and never mention one you didn't read.

- **Memory and past chats**: goals per area, earlier decks and their feedback, format and
  length preferences, the level the user is at, topics they said they're done with.
- **Project context** when run inside a project: its instructions and files (a goals doc,
  a reading list) are the user's own words and outrank everything else.
- **Live context** from connectors, read lightly (titles and dates, never bodies): what's on
  the calendar this week (a pitch Thursday → a talk on pitching), what's in progress in
  Linear or Notion, newsletters the user actually opens.

Turn these into 3-6 **needs**, each a line like "pricing a B2B product (work goal, Memory)"
and tagged with an area. What to pull from each source, and what to skip, is in
[`picking.md`](./references/picking.md#signals). Record each source read in
`sources_checked` (with `Memory`, `Past chats` and `Project files` when read), and each
that failed or isn't connected in `sources_missing`. **A failed read isn't an empty one.**

**First run with nothing to go on** (no memory, no project files, nothing connected): in
a live chat, ask one line: "What are you trying to get better at, in work, business and
life? One line each is plenty." Then build the deck from the answer, citing `You`. In a
scheduled run, build a broad starter deck, and make one card the user's chance to steer:
say so in `adjusted`.

### 3. Find and verify

This step needs **web search**. Search for each need, preferring sources the user has liked
before. Then **open every candidate** before it goes in the deck:

- **YouTube**: fetch `https://www.youtube.com/oembed?url=<video url>&format=json`. A 200
  gives the real title and channel; anything else drops the video. Use the description or
  transcript for the summary when you can read it.
- **Anything else**: fetch the page and confirm it is the thing (title, author, date).

Record how in `verified_by` (`oembed` or `opened`) and what the summary was written from in
`summary_from` (`transcript`, `page` or `description`). **Never put a link in the deck that
you didn't open this run, and never write a summary of content you couldn't read**: when
you only have the description, say so with `summary_from: description`. If search isn't
available, say so and stop. A deck of guessed links is worse than no deck.

Skip anything in the history (memory says it was in a deck in the last 90 days), anything
behind a paywall unless the user said they subscribe, and anything over the time budget.

### 4. Pick the deck

Follow [`picking.md`](./references/picking.md#pick). In short: **3-5 cards**, the first is
the **top pick** (the best fit for today), the mix follows the settings (default: work,
business, life), formats are varied unless the user prefers one, and the whole deck fits
the daily budget if they did only the top pick plus one more.

For each card write:
- **why**: one or two sentences tying it to a need, backed by 1-3 `because` lines, each
  naming its source. No evidence, no claim.
- **summary**: 2-3 lines of what you'll actually learn, specific enough to decide whether
  to open it. Not "a great talk about leadership".
- **try**: one small action to take after, of 15 minutes or less.

Fill `adjusted` with up to three lines on what changed because of feedback ("Fewer
podcasts: you skipped the last three"). This is how the user sees the deck learning.

**Privacy.** Cite a subject line or a calendar title, never a message body. Health goals
are fine; diagnoses, results and medications never go on a card or into memory.

### 5. Build the deck

Write `deck.json` (shape: [`evals/example-deck.json`](./evals/example-deck.json)) in the
conversation's language, with `lang`, and `labels` when it isn't English. Then validate:

```bash
python3 scripts/validate_deck.py deck.json
```

It exits non-zero with a fix per error. **Fix and re-run until it passes.** Standard
library only.

**Write the page once.** With artifacts available, create the HTML artifact directly:
[`assets/deck-template.html`](./assets/deck-template.html) copied unchanged, except for
the JSON inside `<script type="application/json" id="deck-data">`. Get that JSON from
`python3 scripts/render_page.py deck.json --data`, which prints it with every `<`
already escaped, and paste it as printed. Don't also render a file.

Without artifacts, run `python3 scripts/render_page.py deck.json deck.html`, share the
file, and give the cards as text.

The deck is one card per screen: swipe, arrow keys or the buttons. Each card has **Open**,
👍 **More like this**, 👎 **Not for me**, and ✓ **Done**. The last card turns those taps
into a one-line **learn-today feedback** summary with a **Copy** button. Taps are saved on
the page (artifact storage, else the browser), but **the page can't tell Claude**, so the
copied line pasted in any chat in the project is how they reach memory.

Close in **two lines at most**: the sources read (and any that failed), and "Tap 👍 / 👎
as you go, then paste the line from the last card here, or just tell me."

### 6. Learn

The skill improves only through memory. Save briefly, tag lines with their area, and save
only what's new (rules in [`picking.md`](./references/picking.md#learning)):

- the deck, one line: `Learn 2026-10-23: [work] <title> (<url>); [life] …`, which is
  also the no-repeat history;
- feedback when it comes, with the reason when there is one;
- a preference (format, length, level, a creator) only after it repeats three times, or
  at once when the user states it.

Say in one line what you saved. Memory can come back empty (incognito, memory off, a new
project): say once that the deck starts fresh, and why.

---

## Make it a daily routine (in a project)

The best home is a **Cowork project**: it has its own instructions, files, memory and
scheduled tasks, and what Claude learns there stays there
([projects](https://support.claude.com/en/articles/14116274-organize-your-tasks-with-projects-in-claude-cowork)).
Put a short goals note in the project's files or instructions and the deck uses it every
day.

On "schedule it" or "every morning", propose it in **one message**, with defaults the user
can accept with "yes":

- name "Learn today", frequency **daily**, time **07:00** local
- approval mode **auto-approve**, because it only reads, searches and writes to memory;
  otherwise the run waits for a go-ahead
- instruction: "Run learn-today for today. Lead with a five-line text list (title, format,
  minutes, link), then the deck."
- any saved settings that differ from the defaults, so the run keeps them even if memory
  is off

Create it once the user agrees, in the project, using the scheduling this surface offers
from chat. Otherwise, point to the project's **Scheduled** section → **New task** →
**Create with Claude** or **Set up manually**
([scheduled tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)).
Scheduled tasks run in the cloud even when the computer is asleep, with connectors and
skills, on paid plans. **Never say it's scheduled unless you saw it created.**

A scheduled run can't ask questions. It never blocks on feedback, uses whatever feedback
reached memory, and leads with text in case the deck can't be shown there.

---

## Honesty rules

- **Every link was opened this run.** No link from memory of the web, no guessed URL, no
  "search YouTube for…" placeholder.
- **Every summary says what it was written from.** A description isn't the video.
- **Every why cites something read** this run, the user's words, or memory.
- **Fewer is fine.** Three good cards beat five padded ones; on a thin day, say so.

## Conventions

**`help`**: one sentence on what this does, which sources are connected now, the current
settings, and the things to say: "what should I learn today", "more on X", "less like
card 3", "schedule it", `config`, `reset`.

**`config`**: change settings in one round, showing the current value for each: area mix,
cards per deck, daily minutes, formats, levels, sources to skip, favourite and blocked
creators, language, schedule. Save them to memory as one "learn-today settings:" line,
replacing the old one. Offer to update the schedule's instruction too.

**`reset`**: removes the "learn-today settings:" line, back to
[Configuration](#configuration). **It never touches your goals, feedback or deck
history.** Say so when confirming. **"Forget my learning history"** is separate: it lists
what it would remove and removes it only after a yes.

**Tone**: curious, specific, a little warm, like a friend who reads a lot and knows what
you're working on. One line to open, the deck, two lines to close.

## Configuration

Defaults. Saved settings live in memory as one line, "learn-today settings: …". **What you
say in the chat beats saved settings, which beat these defaults.**

- mix: `work, business, life`, at least one card each when there are 3+ cards
- cards: 4 (allowed 3-5)
- daily minutes: 30 (the top pick plus one more should fit)
- formats: any (video, article, podcast, course, paper, book, tool), varied
- level: inferred from memory, else "practitioner"
- no-repeat window: 90 days
- paywalls: skip, unless the user says they subscribe
- sources: every connected one; skip: none
- feedback storage: `artifact`, falling back to `browser`
- schedule: daily 07:00, auto-approve, in the project
- language: the conversation's

Fixed, and enforced by the validator:
- 3-5 cards, no duplicate links, each https and verified (`oembed` or `opened`)
- a summary of 2-3 lines, a why with 1-3 cited reasons, a try of 15 minutes or less
- reasons cite only sources read this run, or `You`
