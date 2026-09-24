---
name: one-thing-today
description: >-
  Picks the ONE thing to focus on today, for work, personal life or any area, from connected
  apps and memory, with why and a first step. Use for "what's my one thing today" or "I'm
  overwhelmed".
metadata:
  side_effects: true
  trigger: "Asking what to focus on today (for work, personal life or any area), feeling overwhelmed, or setting up a daily focus routine."
  tags: "focus, productivity, prioritization, anti-perfectionism, life-areas, daily-routine, memory, scheduled-task, desktop"
---

# One thing today

Getting 1% better every day beats a perfect plan that never starts. This skill reads what
you've connected and what Claude remembers about you, then gives you **one** thing for
today: what it is, why it's the one, and how to start in the next 25 minutes. It works for
any part of life: work, personal, health, family, learning, a side project. Everything
else can wait, and the page says so.

It starts automatically when the request matches: "what's my one thing today?", "one
thing for personal life today", "I'm overwhelmed, where do I start?". It's not for a full
day plan, a to-do list or a schedule.

One reference, **read it every run**: [`choosing.md`](./references/choosing.md) (gather,
pick, write, learn). Data shape: [`evals/example-focus.json`](./evals/example-focus.json).
Defaults: [Configuration](#configuration), at the end of this file.

---

## The flow

```
Focus progress:
- [ ] 0. Settings: the chat, then saved settings in memory, then Configuration
- [ ] 1. Area: which part of life this run is for
- [ ] 2. Gather: the area's sources + memory + past chats (+ last focus, same area)
- [ ] 3. Pick one (choosing.md), and write why with evidence
- [ ] 4. Write focus.json → validate → render → show the page
- [ ] 5. Learn: save what changed, in one line
```

### 0. Settings

Look in memory for the line starting **"one-thing-today settings:"**. **What the user says
in this chat wins, then the saved settings, then [Configuration](#configuration).** A
saved "skip Slack" holds until the user changes it; the "never assume a source" rule below
is about what's *connected*, not about preferences.

### 1. Area

The area is free text (`work`, `personal`, `health`, `family`, `side project`…), or
`all`. Resolve it in this order: the request ("my one thing for personal life"), the
scheduled task's instruction, a saved day rule ("Sat–Sun: personal"), then `all`.

The area decides three things: **which sources are read** (the saved area map, for example
`work = Gmail (work), Slack, Linear`), **which candidates can win**, and **what goes on the
page**. On a personal page, nothing from work appears, not even under *Can wait* or in
the sources footer. With no map saved, use judgement: a work Slack isn't personal, a
family calendar isn't work. Say which sources you counted as the area in the closing line,
and offer to save the map.

### 2. Gather

Probe the area's connected sources, in parallel where you can. Use whatever is connected
in this conversation: never assume a source from a previous run, and never mention a
source you didn't read. What to pull, and the time window, is in
[`choosing.md`](./references/choosing.md).

Record each source actually read in `sources_checked`, including `Memory` and `Past chats`
when you read them, and each that failed or isn't
connected in `sources_missing`. Name the account when it matters: "Gmail (personal)".
**A failed read is not an empty inbox.** Say it failed, rather than choosing as if nothing
were there.

**The last focus.** In the same pass, look in memory and past chats for the most recent
one-thing-today focus **for the same area** within the last 7 days. Put it in
`yesterday`, with `day` set to the day it was for ("Friday" on a Monday, "Yesterday"
otherwise). Its outcome is `unknown` unless the user said, or you can see it happened (the
email was sent, the ticket closed).

If nothing is connected and memory is empty, don't guess. Ask one question: "What's on your
mind for today? List it or paste it, I'll pick one." Then pick from that, with `You` as the
source.

### 3. Pick one

Follow the rubric in [`choosing.md`](./references/choosing.md). In short: the thing that
**someone is waiting on** (a colleague, family, or a promise to yourself), that **slips
with a real consequence**, that **compounds**, or that **keeps getting avoided**. Weigh it
by what the user said matters in this area, and discount busywork.

- **One thing.** Not two joined by "and". If two tie, pick the one with the earlier
  consequence and put the other in `not_today`.
- **Why** is two or three plain sentences backed by 1–4 `evidence` lines, each naming
  its source. No evidence, no claim.
- **How** is at most three steps. The first takes 25 minutes or less and needs no further
  thinking: which file, which person, which sentence.
- **Done when** is observable. **Good enough** names the bar and what to skip: this is
  where perfectionism gets cut. **Not today** lists up to three tempting things from the
  same area that can wait.
- **An off day is a valid answer.** On a weekend, a holiday or a calendar out-of-office
  day, or when nothing is pressing, say so, and **stay in the run's area**. A `work` run
  says "No work needs you today", with a rest focus such as "Take the day off", and
  nothing personal. Only an `all` run may offer one small, optional personal step, such as
  a goal or a walk.

**Privacy.** Quote a subject line, not an email body. A health *goal* or *task* is fine
("book the physio follow-up", "run three times a week"). Diagnoses, results,
medications, passwords and codes never go on the page or into memory.

### 4. Build the page

Write `focus.json` (shape: [`evals/example-focus.json`](./evals/example-focus.json)) in
the conversation's language. Set `lang`, and when it isn't English, add `labels` for the
page headings. Set `done_storage` from settings. Then validate:

```bash
python3 scripts/validate_focus.py focus.json
```

It exits non-zero with a fix per error. **Fix and re-run until it passes.** It uses the
standard library only.

**Write the page once.** With artifacts available, create the HTML artifact directly:
[`assets/focus-template.html`](./assets/focus-template.html) copied unchanged, except for
the JSON inside `<script type="application/json" id="focus-data">`. Get that JSON from
`python3 scripts/render_page.py focus.json --data`, which prints it with `</` already
escaped, and paste it as printed. Don't also render a file.

Without artifacts, run `python3 scripts/render_page.py focus.json focus.html`, share the
file, and give the same content as text.

The page works on a phone, follows light and dark mode, and shows the area and the last
focus. **Mark it done** saves to the artifact's own storage when this surface provides it,
otherwise to the browser, so the page works either way.

Close in **two lines at most**:
- the sources read (and any that failed), and the one thing that almost won, so the user
  can overrule it;
- when there's a last focus with an unknown outcome, ask "Did *X* happen?" in the same
  message. Offer *done / partly / not this time*, and never guilt: a "no" is information
  about what gets in the way.

### 5. Learn

The skill improves only through memory, so this step isn't optional when memory is on.
Save briefly, **tag every line with its area**, and save only what's new (rules in
[`choosing.md`](./references/choosing.md#learning)):

- today's focus, for example `One thing 2026-09-24 [work]: …`, and the last focus's outcome
  when you learn it, including "done" said in chat;
- a correction ("not that, the board deck matters more"), which is the strongest signal;
- a pattern, but only after it has repeated three times in that area.

Say in one line what you saved. Memory can come back empty: in a project (each project has
its own memory), in incognito, with memory turned off, or on a free plan (no past-chat
search). If so, say once that it will start fresh, and why.

---

## Make it a daily routine

On "schedule it" or "do this every morning", set up a **scheduled task**. These run in the
cloud, even when the computer is asleep or the app is closed, with connectors and skills
available, on paid plans. Where memory is on, a cloud run uses it too
([scheduled tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork),
[release notes](https://support.claude.com/en/articles/12138966-release-notes)).

1. **Propose it in one message**, with defaults the user can accept with "yes":
   - name "One thing today"
   - frequency weekdays
   - time 07:30 local
   - **approval mode: auto-approve**, because this task only reads and writes to memory.
     Otherwise the 07:30 run waits for a go-ahead.
   - instruction: "Run one-thing-today for today, area: work. Lead with a five-line text
     version, then the page."
   - any saved settings that differ from the defaults, such as "Skip Slack", so the run
     keeps them even without memory

   **Offer a pair** when the user has more than one area: *weekdays 07:30, area: work*, and
   *daily 09:00, area: personal, on Saturday and Sunday only*. There's no weekends
   frequency (the options are hourly, daily, weekly, weekdays or manual), so the personal
   task's instruction starts "On Saturday and Sunday only: … On other days, reply 'Not
   today' and stop." Name them "One thing today · work" and "… · personal".
2. **Create it once the user agrees**, using the scheduling this surface offers from chat.
   Otherwise, point to the **Scheduled** section in the sidebar (in Cowork, if the app
   still shows it separately). There, **New task → Create with Claude** or **Set up
   manually** takes the same values.
3. **Never say it's scheduled unless you saw it created.** Runs, edits and the pause switch
   are in **Scheduled**, and a push notification arrives when a run finishes.

A scheduled run can't ask questions. It never asks about the last focus, and leads with
text in case the page can't be shown there.

---

## Honesty rules

- **Never invent evidence.** Every reason points to something read this run, the user's
  own words, or memory. A thin day gets a thin why, not a made-up deadline.
- **Don't pretend to know priorities you can't see.** When the sources don't settle it,
  say so and pick the smallest move that keeps the most important thread alive.
- **One is the point.** Don't sneak a second focus into the steps or the why.
- **Stay in the area.** A personal page never carries work items, and the other way round.

## Conventions

**`help`**: one sentence on what this does, which sources are connected now, the current
settings, and the things to say: "one thing today", "one thing for personal", "that's not
it, it's X", "schedule it", `config`, `reset`.

**`config`**: change settings in one round, with the current value shown for each: areas
and their sources, day rules, sources to skip, window, tone, done storage, schedule. Save
them to memory as a single "one-thing-today settings:" line, replacing the old one. Desktop
skills can't keep files, and memory is what the next run reads. If the user has a
schedule, offer to update its instruction too.

**`reset`**: removes the "one-thing-today settings:" line and this chat's changes, going
back to [Configuration](#configuration). **It never touches your history, outcomes,
corrections or goals**, nor any email, calendar or task. Say so when confirming.
**"Forget my one-thing history"** is separate: it lists the entries it would remove and
removes them only after a yes.

**Tone**: calm, direct and a little warm, like a friend who's good at priorities. One line
to open, the page, two lines to close.

## Configuration

Defaults. Saved settings live in memory as one line, "one-thing-today settings: …".
**What you say in the chat beats saved settings, which beat these defaults.** To change a
default for everyone, edit this list, re-zip and re-upload.

- area: `all`. Day rules: none (suggest "Sat–Sun: personal" when the user has areas)
- areas map: none (judgement, then offer to save one)
- window: today, plus anything due before noon on the next working day
- lookback: 7 days, for threads and promises waiting on you
- sources: every connected one in the area; skip: none
- done storage: `artifact` (the artifact's own storage), falling back to `browser`
- ask about the last focus: yes, in the closing lines (never in a scheduled run)
- tone: calm, direct, a little warm
- schedule: weekdays 07:30, area work; daily 09:00, area personal, Sat–Sun only (a pair)
- language: the conversation's

These are fixed, not settings, and the validator enforces them:
- one focus of 90 characters or less
- at most 3 steps, with a first step of 25 minutes or less
- evidence that cites only sources read in this run
