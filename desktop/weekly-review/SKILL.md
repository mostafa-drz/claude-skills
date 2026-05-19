---
name: weekly-review
description: >-
  Runs a structured end-of-week review by pulling the past 7 days from Google
  Calendar, Gmail, and Google Drive, then synthesizing a Markdown review
  document: how time was spent, key conversations and commitments, what got
  done vs. what slipped, and what to carry into next week. Use when doing a
  weekly review, end-of-week reflection, personal retrospective, checking what
  happened this week, reviewing the week, or preparing for the week ahead.
---

# Weekly Review

Every week has a rhythm: meetings pile up, emails accumulate, documents get
touched — and Friday arrives without a clear picture of what actually happened.
This skill pulls the past 7 days from Calendar, Gmail, and Drive and synthesizes
a structured review you can read in under 5 minutes.

## Configuration

```
review_window: 7d               # Days to look back: 7d, 5d (work week), or custom
include_sources: all            # "all" or comma-separated: calendar, gmail, drive
meeting_threshold_minutes: 30   # Events shorter than this aren't counted as meetings
carry_forward: true             # Surface unresolved commitments from email threads
```

## Process

### 1. Detect available sources

Check which Google Workspace integrations are connected in this session:

```
Connected sources:
  ✅ Google Calendar — weekly event history
  ✅ Gmail — key threads and commitments
  ✅ Google Drive — documents touched this week
  ❌ Slack — not connected (skip)
```

If no sources are connected at all, explain how to enable Google Workspace in
Desktop settings, then stop.

### 2. Set the review window

Default: the 7 calendar days ending today. If today is Saturday or Sunday, end
on the most recent Friday. Ask only if the user specifies a different range.
Otherwise, proceed without asking.

### 3. Pull calendar data

From Google Calendar, fetch all events in the review window:

- Total event count and total meeting time
- Events by type: 1:1s, team meetings, external calls, focus blocks, cancelled
- Events moved or rescheduled from a prior week into this one
- Events already booked in the next 7 days (upcoming commitments)

Estimate **focus time** = total working hours (assume 8h/day × work days) minus
meeting time. Use as a rough signal, not a precise tracker.

### 4. Pull Gmail threads

Fetch threads active in the review window (sent or received):

- Threads where the user sent a reply → commitments made
- Threads awaiting a reply from the user → unresolved
- Threads with external stakeholders → surface first

Extract explicit commitment language: "I'll send this by…", "Let's schedule…",
"I'll review…", or questions directed at the user that haven't been answered.

### 5. Pull Drive activity

List documents created or modified this week. Group by type (doc, sheet, slide,
other). This surfaces work that isn't visible in calendar or email alone.

### 6. Synthesize the weekly review

Produce a single Markdown document:

```markdown
# Weekly Review — [date range]

## Week at a Glance
- [N] calendar events · [Xh Ym] in meetings · ~[Zh] estimated focus time
- [N] emails sent · [N] threads still waiting on me

## What Happened
[3–5 bullets summarizing major activities, inferred from event names and email
subjects. Group by theme where possible.]

## Key Conversations
[For each significant thread or commitment:]
- **[Thread subject]** — [1-line summary and outcome]
  → [Status: ✅ Resolved / ⏳ Pending (waiting on me) / 🕐 Waiting on them]

## What Got Done
[Items where calendar + email signal completion: decisions made, docs sent,
meetings with clear outcomes, PRs reviewed.]

## What Slipped
[Events rescheduled into next week, threads with no resolution, items
mentioned but not followed through.]

## Carry Forward to Next Week
[Ranked list: upcoming deadlines from email, booked events needing prep,
unresolved threads that need action.]

## This Week's Numbers
| | |
|---|---|
| Meetings | [N] ([Xh Ym]) |
| Focus blocks | ~[Zh] |
| Emails sent | [N] |
| Documents touched | [N] |
| Commitments made | [N] |
| Commitments pending | [N] |

---
*Generated [date and time] — sources: [list of connected sources]*
```

### 7. Offer follow-ups

After presenting the review, ask:

> Want me to: (a) draft replies for any pending threads, (b) add prep items to
> next week's calendar, or (c) save this review to Drive as a doc?

Wait for explicit confirmation before taking any action.

## Guidelines

- **Calendar is ground truth.** How time looked on the calendar is more reliable
  than memory or email.
- **Extract commitments, don't infer them.** Only surface a promise if there's
  explicit language in an email thread. Don't guess.
- **Slippage is information, not failure.** Report what moved or didn't happen
  neutrally — this is a thinking tool, not a performance review.
- **Confirm before acting.** Never send an email, create a calendar event, or
  write to Drive without an explicit yes.
- **Graceful degradation.** If a source fails or returns nothing, note it and
  continue. A partial review is better than none.
- **One document, then follow-ups.** Present the complete review first. Ask
  about actions after — not during synthesis.

## Example

**User:** "Do my weekly review"
*(also: "review my week", "what happened this week", "end of week recap")*

**Output:**

```markdown
# Weekly Review — May 12–18, 2026

## Week at a Glance
- 11 calendar events · 7h 30m in meetings · ~12h estimated focus time
- 23 emails sent · 4 threads still waiting on me

## What Happened
- Shipped the auth refactor — design review, PR merge session, post-deploy check
- Two discovery calls for the new onboarding flow
- Weekly 1:1s with Alex, Jordan, and Sam

## Key Conversations
- **"Schema proposal review"** (with Alex) — Agreed to review by Friday
  → ⏳ Pending (waiting on me)
- **"Q2 investor metrics"** (from Jordan) — Q2 data requested by May 22
  → ⏳ Pending (waiting on me)
- **"Auth endpoint question"** (from Maria) — Answered Tuesday
  → ✅ Resolved

## What Got Done
- Auth PR merged (Tuesday)
- Sprint planning completed (Wednesday)
- Q1 retrospective doc finalized and shared with team

## What Slipped
- Schema proposal review → moved to next week
- Design handoff for onboarding flow → no progress this week

## Carry Forward to Next Week
- May 22: Q2 metrics → Jordan
- May 20: Schema review → Alex
- May 21: Sprint retrospective (needs prep)

## This Week's Numbers
| | |
|---|---|
| Meetings | 11 (7h 30m) |
| Focus blocks | ~12h |
| Emails sent | 23 |
| Documents touched | 6 |
| Commitments made | 3 |
| Commitments pending | 2 |

---
*Generated 2026-05-18 17:04 — sources: Calendar, Gmail, Drive*
```
