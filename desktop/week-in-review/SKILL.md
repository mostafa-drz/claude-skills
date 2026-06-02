---
name: week-in-review
description: >-
  Synthesizes the past week from Google Calendar, Gmail, and Drive into a
  structured personal retrospective. Reconstructs what was worked on,
  decisions made, and items still open — without manual tab-switching.
  Use when doing a weekly review, preparing a team update, writing a weekly
  log, recapping the week, or when asked "what happened this week",
  "summarize my week", "weekly retro", or "give me a week in review".
---

# Week in Review

Every Friday afternoon, pulling together a coherent picture of the past week means opening Calendar, scanning Gmail, hunting for meeting notes in Drive — 20 to 30 minutes of context reconstruction scattered across tabs. This skill does that in one pass: reads the week's Calendar events, surfaces linked Drive docs and email threads for each, and produces a structured weekly retrospective ready to share or build a team update from.

## Configuration

```
week_window: 7d            # days to look back: 5d, 7d, or custom date range
include_weekends: false    # include Saturday/Sunday events
min_event_duration: 15     # skip events shorter than N minutes
output_format: narrative   # narrative | bullets | doc (creates Google Doc)
highlight_decisions: true  # flag threads/events where a decision was made
```

## Process

### 1. Detect Available Sources

Check which Google Workspace integrations are accessible:

```
Connected sources:
  ✅ Google Calendar — events from last 7 days
  ✅ Gmail — threads from last 7 days
  ✅ Google Drive — linked docs from calendar events
```

If no Google Workspace connection exists, explain how to connect it (Settings → Connected apps) and stop.

### 2. Pull the Week's Calendar

Fetch all Calendar events from the past `week_window` days:

- Skip declined events and events shorter than `min_event_duration` minutes
- Group by day (Mon → Fri, or Mon → Sun if weekends included)
- For each event, note: title, duration, attendees, any linked Drive docs in the description, whether it was a meeting vs. a focus block

### 3. Enrich Each Meeting

For each event that had other attendees:

- **Google Drive**: read any docs linked in the event description (agenda, notes, deck)
- **Gmail**: search for threads referencing the event title or attendees within ±1 day of the event
- Extract: likely topic, any visible decisions or action items from linked docs

If a meeting has no linked docs and no email trail, note it from calendar data only — never invent content.

### 4. Scan Gmail for Week Threads

Beyond meetings, scan Gmail for threads where the user:

- Is in the To: field (direct recipient, not just CC)
- Sent a reply (active threads they participated in)
- Received a reply to something they initiated

Flag threads that appear to contain decisions, agreements, or open questions.

### 5. Synthesize the Retrospective

Build the review in four sections:

**What I Worked On** — grouped by day, factual

```
Monday
  Focus: API auth refactor
  • Sync with [name] — reviewed PR feedback, settled on token-based approach
  • 1:1 with manager — Q3 priorities, aligned on launch timing

Tuesday
  Focus: Deep work (3h uninterrupted)
  • Design review for dashboard — open question on mobile breakpoints
```

**Decisions Made** — concrete resolutions from meetings or email threads

```
• Token-based auth over session cookies (Monday sync)
• Q3 launch pushed 2 weeks pending accessibility audit (Thursday all-hands)
```

**Still Open** — items that surfaced but haven't resolved

```
• Feedback on migration PR from [name] — no reply yet
• Mobile breakpoint strategy from Tuesday design review
```

**Time Distribution** — rough breakdown if calendar data is rich enough

```
~40% meetings  ~45% focus work  ~15% async/email
```

### 6. Present and Offer Next Step

Show the full retrospective, then ask:

> Want me to:
> - **Draft a team update** — trim this to a Slack or email-ready weekly summary
> - **Save as Google Doc** — create a dated doc in Drive
> - **Just use this** — copy and go

## Guidelines

- **Facts only.** Report what happened; never add editorial adjectives like "productive" or "exhausting."
- **Detect, don't fabricate.** If a meeting has no linked docs or email trail, describe it from calendar data only.
- **Respect privacy.** Summarize email content — don't quote body text verbatim. The output may be shared.
- **Graceful degradation.** If Gmail or Drive isn't connected, produce a calendar-only review and note what's missing.
- **Confirm before creating.** If the user asks for a Google Doc, confirm the destination folder before writing.
- **One pass.** Start pulling data immediately — don't ask upfront questions unless something is genuinely ambiguous (e.g., week window spans a company holiday).

## Example

**User:** "Give me my week in review"

**Output:** A structured retrospective covering the past 5 work days — grouped by day with meetings and focus blocks, a decisions section, open items, and a rough time split. Ends with an offer to draft the team update or save to Drive.
