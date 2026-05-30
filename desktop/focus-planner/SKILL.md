---
name: focus-planner
description: >-
  Plans focus blocks for the upcoming week by reading Google Calendar for open
  slots, asking which projects need deep-work time, and scheduling protected
  sessions with your approval. Surfaces exactly how many uninterrupted hours are
  available — not just the gaps, but the ones worth protecting.
  Use when planning the week, protecting focus time, time-blocking for a project,
  scheduling deep work, doing weekly planning, or when your calendar feels too
  packed to make real progress on anything.
---

# Focus Planner

Monday morning: the calendar is already dense with meetings, and the work that
actually needs to happen — the spec, the design review, the writing — has no
time assigned to it. Without a deliberate plan, focus time gets colonized by
whatever feels urgent at 9am. This skill reads the upcoming week, finds the
viable focus windows, maps them to your active projects, and creates named
calendar events — so protected time shows up in the schedule, not just in
your intentions.

## Configuration

```
week_start: next_monday      # next_monday | tomorrow | today
block_min_minutes: 90        # minimum window length worth scheduling
block_max_minutes: 180       # cap a single session at this; split longer gaps
preferred_hours: 8-13        # preferred window for deep work (24h format)
buffer_minutes: 15           # margin to preserve before/after meetings
```

## Process

### 1. Ask for projects

Before reading the calendar, ask one question:

> What are the 2–4 things that need real, uninterrupted focus time this week?
> For each, roughly how many hours?

Accept a quick list: "API spec (3h), code review (2h), essay draft (4h)".
If the user says "just block me time" or similar, proceed with a default of
three 90-minute sessions and ask for project names at the confirmation step.

### 2. Read the calendar

Fetch all events for the configured week (Mon–Fri of `week_start`):

- Title, start time, end time, attendee count, all-day flag
- Identify events already marked as focus blocks (look for "Focus", "Deep work",
  "Block", "Writing", "No meetings" in titles — skip these when calculating gaps)
- Skip all-day events

Report a brief summary before continuing:

```
Week of May 27:
  Scheduled: 13h across 9 events
  Existing focus blocks: 0h
  Scanning for available windows...
```

### 3. Identify viable windows

Extract all gaps that meet the following criteria:

- Net length ≥ `block_min_minutes` after applying `buffer_minutes` on both sides
- Falls within `preferred_hours`
- Not part of a day where back-to-back meetings leave less than `buffer_minutes`
  of breathing room (flag these days as "no viable focus time")

Trim windows longer than `block_max_minutes` into two adjacent sessions when
the gap is large enough, rather than scheduling one marathon block.

### 4. Propose a plan

Match the user's requested project time to available windows. Prioritize:

- Longer windows → highest-hours project
- Morning slots (before noon by default) → cognitively demanding work
- Consecutive days → projects that benefit from context carryover

Present the plan as a table:

```
Proposed focus plan — week of May 27
──────────────────────────────────────────────────
Day        Time             Duration   Project
──────────────────────────────────────────────────
Monday     9:00 – 11:30     2h 30m     API spec
Tuesday    9:00 – 10:30     1h 30m     API spec
Wednesday  9:00 – 11:00     2h 00m     essay draft
Thursday   9:00 – 11:00     2h 00m     essay draft
Friday     10:00 – 12:00    2h 00m     code review
──────────────────────────────────────────────────
Total: 10h 00m
Requested: API spec 3h ✅  essay draft 4h ✅  code review 2h ✅
Shortfall: none

⚠ Thursday has 4 back-to-back meetings from 1–5pm — afternoon
  focus slots were not available that day.
```

If total available time is less than requested, surface the gap clearly:
"There are only 6h 30m of viable focus time this week — 2h 30m short of
your request. Here's the best allocation of what's available."

### 5. Confirm and create events

Ask:

> Create these calendar blocks? You can edit times before confirming.

Accept: yes / adjust [specific change] / skip [day].

On confirmation, create each Google Calendar event:

- **Title:** `Focus: [Project name]`
- **Attendees:** none
- **Status:** Busy
- **Description:** `Protected focus time via focus-planner.`

Create one event at a time and confirm each before moving to the next.
After all events are created, show a final summary with links or event titles.

## Guidelines

- **Never create calendar events without explicit confirmation.** Always show
  the full plan first.
- **Surface honest constraints.** A packed Tuesday is a packed Tuesday — say so
  rather than squeezing in a 20-minute sliver.
- **Prefer morning.** Default to early-day slots; most people's best thinking
  happens before noon. Only use afternoon slots when morning is unavailable.
- **Mon–Fri only.** Skip weekends unless the user explicitly asks.
- **No calendar access?** If Google Calendar is not connected, output the plan
  as a formatted table the user can copy into their calendar manually. Don't stop.
- **Teach the constraint.** If the week genuinely has no viable focus time, say
  so plainly and suggest which meetings might be declined or shortened to create
  space — but don't push; the user decides.

## Example

**User:** "Plan my focus time this week. Need 4h on the product spec, 2h on
the design review doc, 3h on inbox zero."

**Skill:** Reads calendar → finds Mon 9–11:30, Tue 9–11, Wed 9–10:30, Fri 9–11
free → proposes Mon + Tue for product spec (3h total, notes 1h short), Wed for
design review, Thu blocked (back-to-backs), Fri for inbox zero → creates 4
calendar events labeled "Focus: Product Spec", "Focus: Design Review", "Focus:
Inbox Zero" on confirmation.
