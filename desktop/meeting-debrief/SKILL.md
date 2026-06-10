---
name: meeting-debrief
description: >-
  Generates a structured post-meeting debrief from Google Calendar, Drive docs, and Gmail context.
  Captures decisions made, action items with owners and due dates, open questions, and next steps.
  Drafts follow-up emails to action item owners. Use after a meeting ends, when asked to write
  meeting notes, capture what was decided, summarize a call, debrief a standup or planning session,
  assign ownership to action items, or draft follow-up emails from a meeting.
---

# Meeting Debrief

After every meeting there's a version of the same 20-minute scramble: open Calendar to remember who was there, find the agenda doc in Drive, reconstruct what got decided, and draft individual follow-ups to the people who left with action items. This skill collapses that into a single flow — gathering context from connected sources and turning rough notes or memory into a clean, shareable debrief.

## Configuration

```
meeting_notes_folder: My Drive   # Google Drive folder for saved note docs ("" = don't save)
followup_tone: professional      # professional, direct, warm
include_open_questions: true     # include an "Open Questions" section in the debrief
```

## Process

### 1. Identify the Meeting

Ask the user which meeting to debrief, or detect the most recently ended calendar event:

> Which meeting are we debriefing? I can look up your recent calendar, or describe it.

If Google Calendar is available, list the 3 most recently completed events today and let the user pick.
If Calendar isn't connected, ask for: meeting name, date/time, and attendee names.

### 2. Gather Context from Calendar and Drive

Once the meeting is identified, pull what's available:

- **Calendar event**: title, description, attendee list, time, location/video link
- **Drive docs**: scan the event description and body for Google Drive links (agendas, pre-reads, shared notes) — read each and note key agenda items and pre-meeting context
- **Gmail thread** (optional): search for an email thread matching the subject and attendees from the past 7 days

Report what was found:

```
Context gathered:
  ✅ Calendar: "Q3 Planning — Engineering" (10:00–11:00, 6 attendees)
  ✅ Agenda doc: "Q3 Planning Agenda v2" (Drive)
  ✅ Pre-read: "Infrastructure Proposal" (Drive)
  ❌ Gmail thread: not found
```

If nothing is connected, skip to step 3 — the skill still works from user input alone.

### 3. Collect What Happened

Claude wasn't in the meeting. Get the actual content one of two ways:

**If the user has notes or a transcript:**
> Paste your notes or transcript — I'll structure them.

**If they're working from memory:**
Ask three focused questions, one at a time:
1. "What were the key decisions made?"
2. "What are the action items, and who owns each?"
3. "What was left unresolved or needs a follow-up discussion?"

Accept short, conversational answers. Don't ask for anything beyond these three unless a specific item needs clarification (e.g., an action item with no owner).

### 4. Generate the Structured Debrief

Produce a clean debrief document:

```markdown
## Meeting Debrief — [Meeting Title]
**Date:** [date]  **Duration:** [duration]  **Attendees:** [names]

### Decisions Made
- [Decision 1] — rationale if mentioned
- [Decision 2]

### Action Items
| Owner | Action | Due |
|-------|--------|-----|
| Alex  | Draft the migration plan | Fri Jun 13 |
| Jordan | Review infrastructure proposal | EOD today |

### Open Questions
- [Question deferred to a follow-up]
- [Decision that needs more input]

### Next Steps
- [What happens from here at the team/project level]
```

Omit "Open Questions" if `include_open_questions` is false, or if there are none.

### 5. Offer to Save and Send

Present two options after showing the debrief:

**Option A — Save to Drive:**
> Create a Google Doc with these notes in [configured folder]?

If yes: create the doc, return the link.

**Option B — Draft follow-up emails:**
> Draft follow-up emails to the action item owners?

If yes: for each person with an action item, draft a short email:

```
To: [owner]
Subject: Action item from [Meeting Title] — [action in 6 words]

Hi [name],

Quick note from today's [meeting title] — you're down for: [action] by [due date].

[Optional: link to notes doc if one was created]

Let me know if you have questions.
```

Show each draft before sending. Wait for explicit approval on each. Never send without confirmation.

## Guidelines

- **Claude wasn't there** — never invent meeting content. If the user's notes are sparse, ask a targeted follow-up before guessing.
- **Confirm before sending** — every follow-up email requires explicit user approval. Show the draft, wait for "send it" or an edit.
- **Action items need owners** — if the user describes an action without naming who owns it, ask: "Who's responsible for that one?"
- **Detect, don't assume** — only use Calendar and Drive data that's actually accessible. If an integration isn't connected, explain what's missing rather than fabricating context.
- **Graceful degradation** — if Calendar and Drive aren't available, the skill works from manual input. Don't block on missing integrations.
- **Keep the debrief scannable** — decisions are one line each. The action-items table should fit on a phone screen.

## Example

**User:** "Debrief my 10am planning meeting"

**Skill output:**
```
Context gathered:
  ✅ Calendar: "Q3 Planning — Engineering" (10:00–11:00, 6 attendees)
  ✅ Agenda doc found in Drive

What happened? Paste your notes or transcript, or I'll ask three questions.
```

After notes are provided:
- Shows the structured debrief with decisions table and action items
- Offers to save the doc to Drive
- Drafts follow-up emails for the 2 people with action items; shows each before sending
