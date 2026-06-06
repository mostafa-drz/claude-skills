---
name: meeting-prep
description: >-
  Retrieves the next upcoming meeting from Google Calendar, pulls related Drive
  documents and recent Gmail threads from attendees, and delivers a focused
  briefing so you walk in prepared. Use when about to join a call, asking "prep
  me for my 3pm", "what's my next meeting?", "brief me before [meeting name]",
  "what do I need to know for the design review", or any request to surface
  context before a scheduled event.
---

# Meeting Prep

Every meeting with a calendar invite, a set of attendees, and a shared doc trail has a briefable context — the trick is pulling it together in under a minute. This skill reads the next (or named) event from Calendar, retrieves linked Drive docs and recent email threads from attendees, and outputs a scannable brief you can read while the dial-in loads.

## Configuration

```
look_ahead: 4h          # How far ahead to search for the next meeting
gmail_window: 7d        # How far back to scan Gmail threads with attendees
max_docs: 5             # Max Drive docs to surface
max_threads: 4          # Max Gmail threads to include
suggest_questions: true # Offer to draft talking points / questions after briefing
```

## Process

### 1. Find the Meeting

Check Google Calendar for events in the next `look_ahead` window (default: 4 hours). If the user named a specific meeting ("my 3pm", "the design review"), find the best match by title, time, or attendee.

If no meeting is found in the window, ask:
> "No events found in the next 4 hours. Want me to look at the rest of today, or is there a specific meeting you'd like me to prep for?"

If multiple events are found, list them and ask which to brief.

### 2. Extract Event Details

From the matched event, collect:

```
Title: <event title>
Time: <start> – <end> (<timezone>)
Attendees: <list with email addresses>
Location / link: <video URL or room>
Attached docs: <any Google Drive links or attachments in event body>
Organizer: <who created the event>
```

Note who the organizer is — their framing of the meeting topic matters for the brief.

### 3. Retrieve Calendar-Linked Docs

For each Drive link found in the event body or attachments:

- Open and skim the doc (title, headings, last-modified date, brief summary)
- Flag any doc modified within the last 24h as "recently updated"

Show them first in the briefing — the organizer put them there intentionally.

### 4. Search Gmail for Attendee Threads

Search Gmail for recent threads involving this meeting's attendees and topic:

- Sender or recipient: any attendee email
- Subject or body: meeting title keywords, or project/topic words from the event
- Date range: last `gmail_window` days (default: 7 days)

Pick the `max_threads` most relevant threads (prioritize threads with the meeting organizer, then recency). For each thread show:

```
[Gmail] <sender> → <subject> (<time ago>)
  Summary: <1-line of what was said or decided>
```

Skip threads that are obviously unrelated (newsletter digests, automated notifications).

### 5. Search Drive for Supporting Docs

If fewer than `max_docs` docs were found in step 3, search Drive for additional relevant files:

- Search by: attendee names, meeting title keywords, shared-with-attendees filter
- Prefer docs modified in the last 14 days
- Skip docs that are clearly unrelated (templates, old archived files)

For each doc surfaced:

```
[Drive] <title> — <type> — modified <date>
  Summary: <1-line of what it covers>
```

### 6. Build and Present the Briefing

Output a clean, scannable brief:

```
📅 [Meeting title] — [time] ([duration])
   With: [attendee names]
   Link: [join URL if available]

📎 Key Docs ([n] found)
   1. [Doc title] — last modified [date]
      [1-line summary]
   2. ...

✉️ Recent Context ([n] threads)
   1. [Sender] → "[Subject]" (3 days ago)
      [1-line summary]
   2. ...

💡 Things to be aware of
   [1–3 observations: unresolved threads, recent doc edits, open questions from email]
```

Keep the "Things to be aware of" section honest — only flag something if it genuinely warrants attention. If everything looks routine, say "Nothing flagged — looks like a routine check-in."

### 7. Offer Talking Points

If `suggest_questions` is true, ask:

> "Want me to draft a few talking points or questions to bring to this meeting?"

If yes, generate 3–5 talking points grounded in the docs and email context found — not generic agenda items. Label each point with its source (doc name, email thread) so the user can trace it.

## Guidelines

- **Detect availability first** — only search Gmail and Drive if those integrations are connected. Report what's available at the start.
- **Confirm before long searches** — if the meeting is more than 2 hours away and the brief isn't time-sensitive, note it and proceed (don't ask for permission to do the core job).
- **Attendees over keywords** — when Gmail search is ambiguous, filtering by attendee email is more reliable than topic keywords.
- **No fabricated agenda** — only surface agenda items or talking points that are grounded in the docs or email context retrieved. Don't invent plausible-sounding items.
- **Privacy-aware** — the briefing may be displayed on a shared screen. Keep email summaries factual and brief; don't reproduce long sensitive passages verbatim.
- **Graceful degradation** — if Drive or Gmail search returns nothing, say so clearly. A briefing with just Calendar details is still useful.
- **One meeting, one brief** — don't batch multiple meetings into one output unless explicitly asked. Depth beats breadth here.

## Example

**User:** "Prep me for my next meeting"

**Output:**

```
📅 Quarterly API Review — 2:00 – 3:00 PM (1h)
   With: Sarah (PM), Alex (Eng), Jordan (Design)
   Link: https://meet.google.com/abc-defg-hij

📎 Key Docs (2 found)
   1. Q2 API Roadmap (Google Doc) — modified 2 days ago
      Covers planned endpoints for auth v2 and the deprecation timeline for /v1/tokens.
   2. API Review Template (Google Doc) — modified 1 week ago
      Structured agenda with blanks for status, blockers, and decisions.

✉️ Recent Context (3 threads)
   1. Sarah → "Re: /v1/tokens deprecation" (yesterday)
      Sarah flagged that two partners haven't migrated yet; she wants a decision on the cutoff date.
   2. Alex → "PR #284 — auth v2 draft" (3 days ago)
      PR is open and needs review before the meeting; Jordan commented asking about mobile flows.
   3. Jordan → "Design spec update" (4 days ago)
      Shared updated Figma link; mobile auth screens are revised and ready to present.

💡 Things to be aware of
   - The /v1/tokens deprecation cutoff hasn't been decided yet — likely to be the main discussion.
   - PR #284 is unreviewed and Jordan has open questions about mobile auth.
```

> "Want me to draft a few talking points for this meeting?"
