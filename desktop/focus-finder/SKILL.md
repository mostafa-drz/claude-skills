---
name: focus-finder
description: >-
  Analyzes the next 7–14 days of Google Calendar to find contiguous focus
  blocks — stretches of 90+ minutes without any meetings — and surfaces them
  sorted by day and cognitive quality (morning prime blocks first). Labels each
  block by duration and time-of-day tier. Optionally suggests which type of
  work to slot into each block. Use when asking "when do I have focus time this
  week", "find me a 2-hour block", "where can I do deep work", "what days look
  light", "when should I schedule a focus session", or "map my free time".
---

# Focus Finder

Scans the next 7–14 days of Google Calendar and surfaces every contiguous free window long enough to actually do something hard. Sorted by day and time-of-day quality so the best blocks rise to the top.

## Configuration

```
time_window: 7d           # Days ahead to scan: 7d, 14d, or a date range
min_block: 90m            # Minimum block length to surface: 60m, 90m, 2h, 3h
workday_start: 09:00      # Focus blocks counted only after this time
workday_end: 18:00        # Focus blocks counted only before this time
```

## Process

### 1. Confirm Scope

Ask: "How far out should I look and what's the minimum block you need? (default: next 7 days, 90-minute minimum)"

Accept natural language: "this week", "next 2 weeks", a number of days, or a date range. For minimum: "1 hour", "2 hours", "90 minutes", or "just go" for defaults.

If Google Calendar is not connected, explain and stop:

> Google Calendar is not connected. Go to Claude Desktop Settings → Connected Apps → Google Workspace and enable Calendar access, then re-run.

### 2. Fetch Events

Retrieve all events in the window. Include confirmed single events and recurring meetings. Exclude events the user has declined, cancelled occurrences, and all-day administrative holds (vacation, OOO) — note those days as blocked.

Treat tentative events as free unless the user says otherwise.

### 3. Find Free Windows

For each day, compute the gaps between events within [workday_start, workday_end]. Keep only gaps ≥ min_block. A window that starts before workday_start is trimmed to workday_start; one ending after workday_end is trimmed similarly.

### 4. Classify by Cognitive Tier

| Tier | Time of day | Best for |
|------|-------------|----------|
| 🟢 Prime | 09:00–12:00 | Complex work, technical problems, creative writing |
| 🟡 Solid | 12:00–16:00 | Code reviews, structured planning, communication |
| ⚪ Light | 16:00+ | Admin, email triage, low-stakes decisions |

### 5. Present the Focus Map

Show a scannable summary grouped by tier, newest day first within each tier:

```
🎯 Focus Finder — Mon May 18 → Sun May 24

🟢 Prime blocks (morning, 90+ min)
  Mon  09:00–11:30  2h 30m
  Wed  09:00–12:00  3h 00m
  Fri  09:30–11:00  1h 30m

🟡 Solid blocks (afternoon, 90+ min)
  Mon  14:00–16:30  2h 30m
  Thu  13:00–15:30  2h 30m

⚪ Light blocks (late afternoon, 90+ min)
  Tue  16:00–18:00  2h 00m

Days with no qualifying block: Tue morning, Thu morning — back-to-back meetings.
```

Then ask: "Want me to suggest what type of work to slot into these blocks?"

### 6. Suggest Work Allocation (Optional)

If the user says yes, or names specific projects, suggest allocation by cognitive demand:

```
Suggested allocation:
  Mon 09:00–11:30 🟢 → Your most demanding work (design, complex code, writing)
  Wed 09:00–12:00 🟢 → Top priority project — your biggest block this week
  Thu 13:00–15:30 🟡 → PR reviews, planning, async coordination
  Tue 16:00–18:00 ⚪ → Inbox triage, short tasks, prep for tomorrow
```

If the user names projects, slot heavier technical/creative work into Prime blocks and lighter coordination into Solid/Light.

## Guidelines

- **Gaps only, not meetings.** Surface free time. Don't name or describe surrounding meetings.
- **Trim, don't drop.** If a 3-hour window starts at 07:30 and workday starts at 09:00, show it as a 1.5-hour block from 09:00 — only if ≥ min_block.
- **Tentative = free by default.** Assuming a tentative block is busy overstates the user's meeting load.
- **Note blocked days explicitly.** If a day has a vacation/OOO hold or zero qualifying blocks, say so rather than omitting it silently.
- **No scheduling.** This skill finds and presents blocks — it doesn't create calendar events or move meetings.

## Example

**User:** "When do I have focus time this week?"

**Skill does:** Fetches Mon–Sun calendar. Finds 6 free windows ≥ 90 min across 5 days. Sorts: 3 Prime (morning), 2 Solid (afternoon), 1 Light. Presents the map with durations. Asks if the user wants work suggestions. If yes, slots the user's current project into the largest Prime block.
