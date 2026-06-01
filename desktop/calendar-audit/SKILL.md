---
name: calendar-audit
description: >-
  Analyzes Google Calendar for the next two weeks and produces a structured
  meeting-hygiene report. Detects back-to-back meeting blocks, overloaded days
  (more than 4 hours of meetings), missing deep-focus windows, and recurring
  meetings that are strong candidates for async conversion.
  Returns a ranked action plan: specific events to decline, meetings to shorten
  or convert to async, and recommended focus blocks to protect on the calendar.
  Use when the calendar feels overloaded, preparing for a new sprint or quarter,
  or when asked to audit my meetings, review my schedule, find focus time,
  check if my schedule is sustainable, or identify meetings to cut.
---

# Calendar Audit

Every knowledge worker has had the Monday morning feeling: open the calendar, see the next two weeks are a wall of meetings, each one reasonable in isolation, impossible together. This skill does the analysis that rarely gets done manually — it pulls the calendar data, measures what's actually there, and surfaces specific actions rather than generic advice to "have fewer meetings."

## Process

### 1. Fetch Calendar Data

Pull all events from Google Calendar for the next 14 days:

- Event title, start/end time, duration, day of week
- Attendees (count and organizer)
- Recurrence flag (one-off vs. recurring series)
- Description/agenda content if present
- The user's RSVP status (accepted, tentative, declined)

Skip: all-day events, events marked as "free", events the user already declined.

### 2. Build the Daily Picture

For each day, compute:

- **Total meeting hours** — sum of accepted meeting durations
- **Back-to-back blocks** — sequences of meetings with <15 min between them
- **Longest focus window** — largest uninterrupted gap within the workday (9am–6pm)
- **Meeting count** — number of distinct events

Assign each day a status:

```
🔴 Overloaded  — >4 hours of meetings, OR longest focus window <60 min
🟡 Heavy       — 3–4 hours of meetings, OR 2+ back-to-back blocks
🟢 Manageable  — <3 hours, with at least one 90-min uninterrupted window
```

### 3. Classify Each Meeting

Check each event against these heuristics:

**Async candidate** — flag if:
- Title contains "standup", "status", "update", "sync", "check-in", or "weekly" with no substantive agenda in the description
- ≤30 min duration with 4+ attendees (status-sharing pattern, not discussion)
- Recurring meeting with no agenda evolution (description unchanged across occurrences)

**Decline candidate** — flag if:
- User is not the organizer and no agenda item requires their input or decision
- User is marked as optional
- 8+ attendees with no clear presenter, decision-maker, or discussant role for the user

**Shorten candidate** — flag if:
- 60-min 1:1 that recurs weekly with no agenda (most 1:1s work at 30 min)
- 60-min two-person meeting that appears to be status or planning only

**Keep** — do not flag if:
- 1:1 with direct manager or team member (relationship infrastructure)
- Meeting the user organizes with a substantive agenda
- Cross-team decision meeting where the user is a required stakeholder

### 4. Measure Focus Health

Across both weeks, compute:

- **Continuous focus hours/week** — hours in uninterrupted blocks of ≥90 min
- **Fragmented focus hours/week** — hours in broken <60 min windows (high context-switch tax)

Benchmark: knowledge workers need 10–15 hours/week of uninterrupted time for deep work.
Flag if the weekly average is below 10 hours.

### 5. Generate the Audit Report

Present in this structure:

**Two-week snapshot**

```
Week 1: Mon 🔴  Tue 🟢  Wed 🔴  Thu 🟡  Fri 🟡
  Avg: 4.8h meetings/day | Continuous focus: 6h  ⚠️

Week 2: Mon 🟢  Tue 🔴  Wed 🟢  Thu 🟡  Fri 🟢
  Avg: 3.2h meetings/day | Continuous focus: 11h  ✅
```

**Action plan (ranked by focus-time impact)**

1. **Decline** — specific events to decline, one-line reason each
2. **Convert to async** — specific recurring meetings, with a concrete async alternative
   (daily standup post, shared doc, Loom, project tracker instead of live sync)
3. **Shorten** — specific events and the shorter duration to propose
4. **Protect focus blocks** — two or three specific recurring windows to block
   (e.g., "9–12am Tuesday and Thursday — currently unscheduled most weeks")

**Recurring meeting audit** (if any recurring series has run >4 weeks)

List each with the question: "If this meeting disappeared tomorrow, what would actually break?" If the honest answer is "nothing" or "I'd figure it out within a day," it's a candidate for cancellation.

### 6. Offer Follow-Through

After presenting the report, ask:

> Want me to draft the decline message, the async-conversion proposal, or the focus block invite? I'll take them one at a time.

For each action the user confirms:
- **Decline**: draft a polite reply ("Thanks for including me — based on the agenda I don't think I add value here. I'll catch the notes.")
- **Async conversion**: draft the message proposing the switch and the alternative format
- **Focus block**: draft the recurring calendar event with a clear "do not schedule over this" description

**Never send an email or create a calendar event without explicit user approval.**

## Guidelines

- **Show data, not opinions.** Every recommendation must trace to a specific event or measured pattern. "Wednesday has 5.5 hours of meetings with no gap over 30 minutes" is a finding. "You have too many meetings" is not.
- **Protect 1:1s.** Recurring 1:1s with managers or direct reports are relationship infrastructure. Do not flag them for removal — flag for shortening only if genuinely overlong.
- **Async is not always better.** Only recommend async conversion for status-sharing and info-only meetings. Brainstorming, conflict resolution, onboarding, and difficult feedback conversations stay synchronous.
- **Graceful degradation.** If Google Calendar returns no data or access is not connected, explain what integration is needed and stop. Note partial data gaps in the report header.
- **Respect workday boundaries.** Only count 9am–6pm (or ask the user for their actual hours) as the analysis window. Don't count pre-work or after-hours as "available focus time."

## Example

**User:** "Audit my calendar, it's been brutal lately"

**Output:**

```
📅 Calendar Audit — Jun 1–14, 2026

Week 1: Mon 🔴 Tue 🟡 Wed 🔴 Thu 🔴 Fri 🟡
  Avg 5.1h meetings/day | Continuous focus: 5.5h ⚠️ (target: 10h+)

Week 2: Mon 🟢 Tue 🔴 Wed 🟢 Thu 🟡 Fri 🟢
  Avg 3.0h meetings/day | Continuous focus: 12h ✅

Action Plan:

1. Decline: "Product Roadmap Update – All Engineering" (Fri Jun 6, 60 min, 42 people)
   Reason: No agenda item requiring your input; notes shared async after.

2. Convert to async: "Weekly Status Sync – Mobile" (every Mon, 30 min, 7 people)
   Replace with: async standup post each Monday morning in the team Slack channel.

3. Shorten: "1:1 with Jordan" (every Wed, 60 min)
   Proposed: 30 min — covers the same ground with a shared agenda doc.

4. Protect focus: Block 9–12am on Tuesdays and Thursdays
   Currently clear most weeks; three recurring meetings could move to the afternoon.

Want me to draft any of the follow-up messages?
```
