---
name: project-context-pack
description: >-
  Pulls together all available context on a named project — Drive documents,
  Gmail threads, and Calendar meetings — into a single structured brief.
  Surfaces recent decisions, open questions, key contributors, and relevant docs
  so you can re-engage quickly after time away.
  Use when picking up a project you haven't touched in a while, onboarding to
  someone else's work, preparing for a project review, or when asked to catch up
  on, summarize, or brief yourself on any project.
---

# Project Context Pack

Assembles a "what's the state of this thing" brief by searching Drive, Gmail, and
Calendar for everything connected to a project name or topic. Useful any time you
need to re-enter a project without 20 minutes of manual tab-juggling across your inbox,
file browser, and calendar.

## Configuration

```
email_lookback_days: 60      # How far back to scan Gmail for project threads
calendar_lookback_days: 30   # How far back to look for Calendar meetings on this topic
max_docs: 6                  # Maximum Drive documents to surface
```

## Process

### 1. Identify the Project

Extract the project name or topic from the user's message. If ambiguous:
- Ask one clarifying question: "Do you mean [option A] or [option B]?" — show the
  candidates, don't ask open-ended questions.
- If there's only one reasonable interpretation, proceed without asking.

Use the project name as the primary search keyword throughout the rest of the process.

### 2. Search Drive

Search Google Drive for documents related to the project:
- Title contains the project name or close variants
- Recently modified documents shared with collaborators
- Docs the user has opened or edited recently that match the topic

For each result, capture: title, last modified date, last editor, one-line description.
Surface the top `max_docs` results, most recently modified first.

### 3. Search Gmail

Search Gmail for email threads mentioning the project name in the last `email_lookback_days`:
- Threads where the user sent or replied
- Threads with the project name in the subject line
- Threads mentioning key collaborators alongside the project topic

For each relevant thread:
- Summarize in one sentence: who, what decision or question
- Flag threads with no reply or an unresolved ask as open items
- Note the most recent activity date

### 4. Search Calendar

Search Calendar for meetings related to the project in the last `calendar_lookback_days`:
- Events whose title or description mentions the project name
- Recurring meetings about the project

For each meeting: title, date, attendees, any attached doc or agenda.
Note patterns: how often does this project get discussed? Who is usually in the room?

### 5. Build the Brief

Output:

```
📦 Project Context Pack — [Project Name]
Brief as of [date]

Overview
  [1–2 sentences: what this project is and where it appears to stand]

Key People
  • [Name] — [role/context: owner, reviewer, last touched this on <date>]

Recent Docs
  • [Title] — [one-line description] (modified [date] by [name])

Email Threads
  • "[Subject]" — [one-sentence summary] ([date])
    Open: [unresolved question or pending reply, if any]

Recent Meetings
  • [Meeting title] — [date] ([attendees])

Open Items
  • [Unresolved threads, outstanding decisions, or pending follow-ups]

Last Activity
  [Date of the most recent email, doc edit, or meeting on this topic]
```

Omit any section for which nothing was found. If no Drive docs are found, say so.
If no email history exists, say so. Don't pad with filler.

### 6. Offer Follow-Up

After presenting the brief, offer:

> Want me to: (a) pull the full content of any doc, (b) draft a catch-up email to any
> contributor, or (c) search for a specific detail within these results?

Wait for explicit confirmation before taking any action.

## Guidelines

- **Confirm when ambiguous** — if the project name matches multiple things (a Drive folder,
  a Gmail label, and a meeting series by different names), surface the candidates and ask.
- **Infer don't fabricate** — summarize what's actually in the sources. Don't speculate on
  project status beyond what the docs and emails reveal.
- **Last Activity is the anchor** — always include when the most recent signal was. A brief
  that doesn't tell you "last touched 3 weeks ago" vs "yesterday" is incomplete.
- **Skip gracefully** — if Drive or Gmail isn't connected, note the missing source and
  continue. Calendar-only or Gmail-only briefs are still valuable.
- **No side effects** — reads and summarizes only. Never sends emails, modifies docs,
  or creates calendar events without explicit user instruction.

## Example

**User:** "Catch me up on the Orion redesign"

```
📦 Project Context Pack — Orion Redesign
Brief as of Jun 16, 2026

Overview
  A product redesign effort with active doc work and email discussion over the past
  6 weeks. Last meeting was 8 days ago; last doc edit was 2 days ago.

Key People
  • Maya Chen — last edited the design doc (Jun 14)
  • Jordan Lee — organizes the weekly sync; last email Jun 10
  • You — replied to Maya's feedback thread Jun 8, no follow-up since

Recent Docs
  • Orion Redesign — Component Spec v3 — Maya's latest pass, last modified Jun 14
  • Orion — Q3 Scope & Constraints — last modified Jun 2 by Jordan

Email Threads
  • "Orion: nav pattern decision" — Team debating sticky vs. scrolling nav; you
    said you'd check with the iOS team. (Jun 8)
    Open: no follow-up from you yet.
  • "Orion kickoff recap" — Summary of the Jun 3 kickoff. No open items.

Recent Meetings
  • Orion weekly sync — Jun 8 (Maya, Jordan, Priya, you)
  • Orion kickoff — Jun 3 (full team)

Open Items
  • Follow up with iOS team on sticky nav question (Jun 8 thread)

Last Activity
  Jun 14 — Maya edited Component Spec v3
```
