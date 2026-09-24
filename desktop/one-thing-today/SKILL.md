---
name: one-thing-today
description: >-
  Picks the one thing to focus on today, and says why and how. Reads every connected
  source (calendar, email, chat, docs, tickets, tasks) plus Claude's memory and past chats,
  then chooses a single focus: the move that unblocks others, beats a real deadline, or
  compounds. Renders it as a bold, minimal page with the focus, cited reasons and at most
  three small steps. The first step is under 25 minutes. Learns from each day's outcome
  through memory, and can be set up as a daily scheduled task. Against perfectionism: it
  says what "good enough" is and what can wait. Use when the user says "one thing today",
  "/one-thing-today", "what should I focus on today", "what's my one thing", "I'm
  overwhelmed, where do I start", or wants a daily focus routine. Not for a full day plan,
  a to-do list or a schedule.
metadata:
  side_effects: true
  trigger: "Asking what to focus on today, feeling overwhelmed and wanting one place to start, or setting up a daily focus routine."
  tags: "focus, productivity, prioritization, anti-perfectionism, daily-routine, memory, scheduled-task, desktop"
---

# One thing today

Getting 1% better every day beats a perfect plan that never starts. This skill reads
everything you've connected, then gives you **one** thing: what it is, why it's the one,
and how to start in the next 25 minutes. Everything else can wait, and the page says so.

It starts automatically on a matching request in Claude Desktop and claude.ai. "What's my
one thing today?" is the natural trigger.

One reference, **read it every run**: [`choosing.md`](./references/choosing.md) (how to
gather, how to pick, how to learn). Data shape: the `focus.json` example in
[`evals/example-focus.json`](./evals/example-focus.json).

---

## The flow

```
Focus progress:
- [ ] 1. Close yesterday (one question, only if there was a yesterday)
- [ ] 2. Gather: every connected source + memory + past chats, today's window only
- [ ] 3. Pick one (choosing.md), and write why with evidence
- [ ] 4. Write focus.json → validate → render → show the page
- [ ] 5. Learn: save what changed, in one line
```

### 1. Close yesterday

Search memory and past chats for the last one-thing-today focus. If there is one from the
last few days and its outcome is unknown, ask **one** question before anything else:
"Yesterday's one thing was *X*. Did it happen? (done / partly / no)". Accept any answer,
including no answer, and record it as `yesterday.outcome` (`unknown` if they skip).
**Never guilt.** A "no" is data about what gets in the way, not a failure.

In a scheduled run nobody is there to answer, so don't ask. Use `unknown`, or evidence of
completion if you can see it (the email was sent, the ticket closed).

### 2. Gather

Probe every connected source, in parallel where you can. Use whatever is connected in
this conversation: never assume a source from a previous run, and never mention a source
you didn't read. What to pull from each, and the time window, is in
[`choosing.md`](./references/choosing.md).

Record every source you actually read in `sources_checked` and every one that failed or
isn't connected in `sources_missing`. **A failed read is not an empty inbox.** Say it
failed rather than choosing as if nothing were there.

If **nothing** is connected and memory is empty, don't guess. Ask one question: "What's on
your mind for today? Paste it or list it, I'll pick one." Then pick from that, with
`You` as the source.

### 3. Pick one

Follow the rubric in [`choosing.md`](./references/choosing.md). In short: the thing that
**unblocks someone**, **beats a real deadline**, or **compounds**, weighted by what the
user said matters to them (memory), and discounted if it's busywork dressed as progress.

- **One thing.** Not two joined by "and". If two tie, pick the one with the earlier
  consequence and put the other in `not_today`.
- **Why** is two or three plain sentences a person would say out loud, backed by 1–4
  `evidence` lines, each naming the source it came from. No evidence, no claim.
- **How** is at most three steps. The first is small enough to start now (≤25 min) and
  concrete enough to need no further thinking: which file, which person, which sentence.
- **Done when** is observable. **Good enough** names the bar and what to skip: this is
  where perfectionism gets cut. **Not today** lists up to three tempting things that can
  wait, so letting go of them is a decision, not a leak.

Private content stays private: quote a subject line, not an email body. Never put a
password, a code or a medical detail on the page.

### 4. Build the page

Write `focus.json` (shape: [`evals/example-focus.json`](./evals/example-focus.json)), then:

```bash
python3 scripts/validate_focus.py focus.json
python3 scripts/render_page.py focus.json focus.html
```

The validator exits non-zero with a fix per error: a focus over 90 characters, more than
three steps, a first step over 25 minutes, or an evidence line citing a source not in
`sources_checked`. **Fix and re-run until it passes.** Standard library only.

Show `focus.html` as an HTML artifact. It's self-contained, phone-first, light and dark,
and has a **Mark it done** button saved in that browser. If artifacts aren't available,
give the same content as text: the focus in bold, why in two lines, the steps numbered.

Close in **two lines at most**: which sources were read (and any that failed), and the one
thing that almost won, so the user can overrule it.

### 5. Learn

The skill improves only through memory, so this step is not optional when memory is on.
Save to memory, briefly and only what's new (rules in
[`choosing.md`](./references/choosing.md#learning)):

- today's focus and date, and yesterday's outcome if you learned it;
- a pattern, only once it has repeated (three "no"s on afternoon focuses → "mornings work
  better");
- anything the user corrected: "not that, the board deck matters more" is the strongest
  signal there is.

Say in one line what you saved ("Noted: you'd rather start with writing."). If memory is
off, say once that it will start fresh each day, and that turning on memory in Settings
lets it learn.

---

## Make it a daily routine

On `schedule` (or "do this every morning"), set up a **Cowork scheduled task**. These run
in the cloud on a daily or weekdays cadence, even when the computer is asleep or the app
is closed, with connectors and skills available. They need a paid plan
([help center](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)).

1. Propose it in one message, with defaults the user can accept with "yes":
   **name** "One thing today", **cadence** weekdays, **time** 07:30 local,
   **instruction** "Run one-thing-today for today. Don't ask about yesterday; mark it
   unknown unless you can see it was done."
2. If this surface offers to schedule from chat, use it once the user agrees. Otherwise
   give the manual path: **Cowork → Scheduled → New task → Set up manually**, with the
   values above to paste.
3. **Never claim it's scheduled unless you saw it created.** Past and upcoming runs, and
   pausing, live in the Scheduled section.

---

## Honesty rules

- **Never invent evidence.** Every reason points to something read this run, the user's
  own words, or memory. A thin day gets a thin why, not a made-up deadline.
- **Don't pretend to know priorities you can't see.** When the sources don't settle it,
  say so and pick the smallest move that keeps the most important thread alive.
- **One is the point.** Don't sneak a second focus into the steps or the why.
- **The done button is per browser.** It doesn't reach Claude; the page says to tell
  Claude tomorrow.

## Conventions

**`help`**: one sentence on what this does, which sources are connected right now, and the
three things to say: "one thing today", "schedule it", "that's not it, it's X".

**`config`**: for this conversation, in one round: time window (default: today, plus
tomorrow morning), sources to skip, tone (default: calm and direct). Desktop skills can't
save settings between conversations. Say so, and offer to save the preference to memory
instead, which the next run reads.

**`reset`**: forgets this conversation's config and the one-thing-today entries in
memory, after naming what will be removed and getting a yes. It never touches the user's
email, calendar, tasks or any other source.

**Tone**: calm, direct, a little warm. One line to open, the page, two lines to close.
