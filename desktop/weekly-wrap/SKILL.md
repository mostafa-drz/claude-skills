---
name: weekly-wrap
description: >-
  Synthesizes a structured end-of-week summary from Google Calendar events,
  key Gmail exchanges, and recently edited Drive documents over the past 7 days.
  Produces a ready-to-paste accomplishments report organized into delivered work,
  key discussions, open carry-forwards, and next-week priorities.
  Use when asking "what did I do this week?", "write my weekly status update",
  "summarize my week", "prep my Friday wrap-up", "weekly recap", or
  "what should I put in my weekly report".
---

# Weekly Wrap

Every week ends with the same question: what actually happened? This skill pulls
your Calendar events, key Gmail threads, and Drive activity from the past 7 days,
then organizes them into a structured summary you can paste directly into a
standup update, status email, or personal work log.

## Configuration

Edit these defaults before uploading, or override at runtime.

```
time_window: 7d             # Days to look back: 5d, 7d, or "this week"
output_format: standup      # standup | email | log | bullets
include_next_week: true     # Pull upcoming Calendar events for "next week" section
max_items_per_section: 5    # Cap on items per section to keep output focused
```

## Process

### 1. Determine the Time Window

Default: the past 7 calendar days (or "this week" = last Monday through today).
If the user specifies a range ("last week", "past 5 days"), use that instead.

Ask only if the request is genuinely ambiguous — don't ask if the default is obvious.

### 2. Gather Calendar Events

Fetch all calendar events within the time window:

- Filter out: declined events, solo focus blocks, commute/lunch entries
- Group the remaining events by theme or project where possible
- Note: duration, attendees, any agenda or notes attached to the event

```
Calendar summary:
  3 × product meetings (2.5h) — Q3 planning, design review, roadmap sync
  2 × 1:1s (1h) — Sarah, Alex
  1 × external call (45m) — vendor evaluation
  1 × team standup (30m/day × 4 days)
```

### 3. Gather Gmail Key Exchanges

Search Gmail for sent + received threads in the time window:

- **Sent mail**: find emails where the user initiated a conversation or made a commitment
- **Received + replied**: threads where the user responded and decisions were made
- Exclude: calendar invite confirmations, automated system emails, newsletters, receipts
- Limit to 10 most significant threads; summarize each in one line

```
Key Gmail exchanges:
  → Sent: "Proposal: API versioning approach" — shared recommendation with team
  → Replied: "Hiring pipeline update" — confirmed interview panel, set timeline
  → Replied: "Budget approval for Q3 tooling" — approved $4k request
```

### 4. Gather Drive Activity

Search Google Drive for documents created or modified in the time window:

- Filter to documents the user edited (not just viewed)
- Limit to 5 most recent
- Show: title, last modified date, context (shared / project doc / personal)

```
Drive activity:
  • "Q3 Roadmap v3" — edited Jun 7 — added 2026 H2 priorities
  • "Interview Rubric — Backend" — created Jun 6 — new hire rubric
  • "Weekly Team Sync Notes" — edited Jun 5 — captured decisions from sync
```

### 5. Synthesize the Weekly Summary

Organize findings into four output sections:

```
✅ Delivered this week
  [Concrete outputs, shipped things, completed decisions]

🗣️ Key discussions & decisions
  [Important conversations — meetings + email — with outcomes noted]

🔄 Carry-forwards (open items)
  [Things started or discussed but not yet closed]

🔜 Up next
  [Calendar events already on the books for next week, if include_next_week is on]
```

**Output format mapping:**

- `standup`: short bullets, one sentence each, no prose
- `email`: short paragraphs per section, suitable for a team update email
- `log`: full bullets with dates, suitable for a personal work log or Notion page
- `bullets`: flat list of accomplishments only, suitable for a resume/timesheet

Show the summary. Then offer:

> Want me to copy this to a new Google Doc, or draft it as a Slack message / email?

Wait for confirmation before taking any write action.

### 6. Offer Refinements

Common follow-ups — handle without asking:

- "Add more detail on the product meetings" → expand that section from Calendar notes
- "Remove the next-week section" → drop it and reshow
- "Make it shorter / longer" → adjust depth and reshow
- "Format it for Slack" → reformat as Slack-flavored markdown

## Guidelines

- **Signal over completeness** — 5 meaningful items beat 15 marginal ones. Filter aggressively.
- **Outcomes, not activities** — "Approved the Q3 budget" beats "Attended budget meeting." Infer outcomes from email replies and calendar notes where possible.
- **Read-only unless asked** — never create docs, send emails, or post messages without explicit user approval.
- **Graceful degradation** — if Calendar, Gmail, or Drive isn't connected, use what's available and note the gap. Don't fabricate data.
- **Respect privacy** — summarize email content; don't quote verbatim. The user may be pasting this into a shared channel.
- **Handle sparse weeks** — if the week was light (vacation, few meetings), say so and produce what context exists. Don't pad.

## Example

**User:** "Summarize my week"

**Skill flow:**
1. Fetches Calendar for Jun 2–9 → finds 8 events grouped into 3 themes
2. Scans Gmail sent/replied → finds 5 significant threads (proposal, hiring, approvals)
3. Checks Drive → finds 3 docs edited this week
4. Produces standup-format summary

**Output shape (standup format):**
```
✅ Delivered this week
  • Finalized Q3 roadmap v3 and shared with leadership
  • Hired panel for backend role — 3 interviewers confirmed, loop starts Mon
  • Approved Q3 tooling budget ($4k)
  • Shipped API versioning recommendation — team aligned

🗣️ Key discussions & decisions
  • Design review: decided to defer the redesigned onboarding to Q4
  • Vendor eval call: shortlisted 2 of 4 vendors; RFP responses due Jun 15

🔄 Carry-forwards
  • Roadmap sign-off from VP — waiting on async review
  • Interview rubric needs one more reviewer sign-off

🔜 Up next
  • Mon: backend interview loop kickoff
  • Wed: Q3 planning final review
  • Fri: vendor RFP deadline
```
