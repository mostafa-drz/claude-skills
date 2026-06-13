---
name: week-ahead
description: >-
  Builds a structured week-ahead briefing by scanning Google Calendar for the
  next 7 days, surfacing linked Drive documents per event, and checking Gmail
  for pending threads with attendees. Produces a day-by-day plan with per-meeting
  prep notes, pending action items, and suggested focus blocks.
  Use when planning the week, preparing for Monday, asking what's coming up this
  week, wanting a Sunday-evening preview, or saying "what do I have this week."
---

# Week Ahead

Takes a forward look at the next seven days: pulls every calendar event, surfaces the Drive docs and Gmail threads that belong to each one, and assembles a single brief you can scan in under five minutes. The goal is to arrive at any morning already knowing where your attention belongs — not discovering it mid-meeting.

## Configuration

```
lookahead_days: 7           # How many days forward to scan (3–14)
include_weekends: false     # Include Saturday/Sunday events
focus_threshold: 60         # Events shorter than this (minutes) shown condensed
max_threads_per_event: 3    # Max email threads to surface per meeting
draft_agenda: false         # Auto-draft agenda questions for meetings you organize
```

## Process

### 1. Detect Available Integrations

Check which sources are connected in this session:

```
Sources found:
  ✅ Google Calendar
  ✅ Gmail
  ✅ Google Drive
  ❌ Slack — not connected
```

If Calendar is not connected, explain that Google Workspace integration is required (Settings > Connected apps in Claude) and stop.

### 2. Ask for Scope (First Time per Session)

Before fetching, ask once:

> **Quick setup:**
> 1. How many days ahead? (default: 7)
> 2. Include weekends? (default: no)
>
> Or just say "go" to use defaults.

Accept any brief answer. One-word responses like "go" or "yes" should proceed immediately with defaults.

### 3. Fetch Calendar Events

Pull all events for the configured lookahead window. For each event, capture:
- Title, date/time, duration
- Attendees and their roles (organizer vs. invited)
- Event description (may contain Drive doc links or agenda text)
- Video call links (Google Meet, Zoom, etc.)

Skip declined events. Flag events the user is organizing (higher prep burden, marked ★).

### 4. Surface Context per Event

For each event with >1 external attendee or >30 min duration:

**Drive docs:** Search the event description and title for Google Drive URLs. Also search Drive for documents shared with attendees that match event keywords.

**Gmail threads:** Search Gmail for recent threads involving attendees with subject keywords from the event title. Limit to `max_threads_per_event` most recent.

Present each event with its context:

```
📅 Product Roadmap Review — Wed 11:00 AM (60 min)
  With: Sarah Chen, Alex Park, Jordan Kim
  Doc: "Q3 Roadmap — Draft.gdoc" (last edited 2 days ago by Sarah)
  Thread: "Roadmap review agenda" — 3 messages, last reply yesterday
  Call: meet.google.com/abc-defg-hij
```

If nothing is found for an event, note "No docs or threads found" — don't leave it blank.

### 5. Check Pending Action Items

Before building the day view, scan Gmail for items that need attention this week:

- Emails addressed directly to the user with no reply sent in the last 5 days
- Emails where the user was the last sender but received no response (follow-up candidates)
- Emails containing action-request language ("can you", "please send", "by when", "waiting on you")

Surface up to 5 of these in a "Before the Week Starts" block.

### 6. Build the Week Brief

Organize into a clean day-by-day view. Use this structure:

```
📋 Week Ahead — Jun 9–15, 2026
Scanned: Calendar · Gmail · Drive

BEFORE THE WEEK STARTS
  ⚠️  Reply pending: Jordan asked about API timeline (3 days ago)
  ⚠️  Follow up needed: no reply from design team on mockup request

MONDAY, JUN 9
  9:00 AM  Daily standup (15 min)
  11:00 AM  Product Kickoff (90 min) ★
    Doc: "Kickoff brief.gdoc" — not yet viewed by most attendees
    Thread: "Kickoff agenda" — you sent the last message, no replies yet

TUESDAY, JUN 10
  (no meetings scheduled)
  → Suggested focus block

WEDNESDAY, JUN 11
  11:00 AM  Roadmap Review (60 min)
    Doc: "Q3 Roadmap Draft.gdoc" — edited 2 days ago
    Thread: "Roadmap agenda" — Sarah sent notes yesterday

THURSDAY, JUN 12
  3:00 PM  1:1 with manager (30 min) ★
    No linked docs.  Thread: "1:1 June" — last reply 1 week ago

FRIDAY, JUN 13
  2:00 PM  Weekly retro (30 min)
    No docs or threads found.
```

Legend:
- ★ = you are the organizer — prep is your responsibility
- (no meetings) = candidate focus block, suggest protecting it

### 7. Offer Follow-up Actions

After presenting the brief:

> **What next?**
> A) Prep notes or talking points for a specific meeting
> B) Draft agenda questions for a meeting you're organizing
> C) Draft a reply to a pending action item
> D) Done — I have what I need

Handle one selection at a time. After completing it, offer the menu again.

## Guidelines

- **Forward only.** Events that have already started or ended are excluded.
- **No fabrication.** If Drive or Gmail returns no results, say so explicitly — don't guess at doc names or invent thread summaries.
- **Organizer events get ★.** When the user is the organizer they have a prep burden others don't — flag it every time.
- **Keep it scannable.** The brief should be readable in under 5 minutes. Summarize email threads in one line; don't paste full content.
- **Confirm before acting.** If the user asks to draft a reply or send anything, always show the draft first and wait for explicit approval.
- **Graceful degradation.** If Drive search fails, skip it, note the error, and continue. One broken integration shouldn't block the whole brief.
- **Respect the focus blocks.** Days with no meetings are productivity assets. Don't fill them with noise — highlight them.

## Example

**User:** "What's my week looking like?"

**Claude:** Detects Calendar, Gmail, Drive → asks scope (or uses defaults) → fetches 5 events across 4 days → finds linked docs for 2 of them → detects 2 pending reply threads → outputs a day-by-day brief with prep notes for the two prep-heavy meetings and a ★ on the one the user is organizing → offers to draft talking points for the kickoff.
