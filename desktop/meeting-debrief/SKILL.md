---
name: meeting-debrief
description: >-
  Captures what happened after a meeting — pulls the Calendar event, attendees,
  and any linked Drive docs or Gmail threads, then turns the user's brief verbal
  recap into a structured debrief: decisions made, action items with owner and
  deadline, and a ready-to-send follow-up email. Use after a meeting, when asked
  to write up a meeting, capture outcomes, document decisions, draft a follow-up,
  or send meeting notes to attendees. Trigger phrases: "debrief that meeting",
  "capture what we decided", "write up the meeting", "send meeting notes",
  "what did we agree on", "follow-up from the call".
---

# Meeting Debrief

Every meeting produces three things worth capturing: what was decided, who owns what, and what to communicate to the people who weren't there. This skill pulls the Calendar event and any linked context, asks for a brief verbal recap, and turns it into a clean debrief doc and a ready-to-send follow-up email — before the memory fades.

## Process

### 1. Identify the Meeting

Ask the user which meeting to debrief, or detect from context if a recent Calendar event is obvious:

> Which meeting should I debrief? (Name, time, or paste the invite — I'll pull the details.)

If Google Calendar is connected, search recent events (last 3 hours) for meetings with attendees. Present the most likely candidate:

> I see you had "Q3 Roadmap Review" ending at 2:30 PM. Is that the one?

Accept confirmation or a manual description.

### 2. Pull Context

Once the meeting is identified, gather available context in parallel:

**Google Calendar:**
- Event title, date, time, duration
- Attendees list with names/emails
- Meeting description or agenda (if present)
- Any attached documents or links in the invite

**Google Drive:**
- Search for docs shared in the last 48 hours matching the meeting title or participants
- Look for decks, agendas, or briefs referenced in the invite description

**Gmail:**
- Search for the meeting invite thread and any pre-meeting discussion
- Look for relevant threads in the last 7 days mentioning meeting keywords or attendee names

Report what was found:
```
Context pulled:
  ✅ Calendar — "Q3 Roadmap Review", 2:00–2:30 PM, 5 attendees
  ✅ Drive — found "Q3 Roadmap Draft v2.pdf" (shared yesterday)
  ✅ Gmail — found invite thread with pre-meeting comments from Sarah
  ❌ Slack — not connected
```

### 3. Gather Outcomes from the User

Ask for the meeting's key outcomes in one open question. Keep it conversational:

> Quick recap: what were the main decisions, and who's doing what?

Accept any format — bullet points, stream of consciousness, a voice-memo transcript. Extract from what the user provides:

- **Decisions**: things the group agreed on ("we're going with option A")
- **Action items**: tasks with an implied or stated owner and timeline
- **Deferred items**: things explicitly pushed to a later date
- **Open questions**: things discussed but not resolved

If an action item is missing an owner or deadline, flag it:

> "Deploy new auth flow" — who owns this, and by when?

### 4. Build the Debrief

Produce a structured debrief in this order:

```
Meeting: [Title]
Date: [Date], [Start]–[End]
Attendees: [Name 1], [Name 2], ...
---

## Decisions
- [Decision 1 — one sentence, present tense]
- [Decision 2]

## Action Items
| Owner | Task | Due |
|-------|------|-----|
| Sarah | Send revised API spec to the team | Fri May 31 |
| Alex  | Schedule follow-up with design     | Mon Jun 2  |

## Deferred
- [Topic pushed to next sprint / next meeting / no date]

## Open Questions
- [Unresolved question — tag the person who will answer if known]
```

Rules:
- Decisions in present tense, single sentence ("We're using OAuth 2.0, not session tokens")
- Action items: one owner per row, no "TBD" owners, propose a deadline if none was stated and flag it
- Skip the agenda summary — attendees were there; focus on outcomes
- Maximum 300 words for the debrief body

### 5. Draft the Follow-Up Email

Draft a follow-up email ready to send to attendees:

```
Subject: [Meeting Title] — recap + next steps

Hi [first names],

Thanks for the time today. Quick summary:

**Decided:** [1–2 bullet decisions]

**Next steps:**
- [Owner]: [Task] by [date]
- [Owner]: [Task] by [date]

[Any deferred item or open question if relevant]

Let me know if I missed anything.

[User's first name]
```

Keep it under 150 words. The debrief doc has the full detail; the email is for quick acknowledgment and accountability anchoring.

### 6. Confirm and Send

Present both the debrief doc and the draft email. Ask:

> Here's the debrief and the follow-up email. Ready to send, or want to edit anything first?

Options:
- **Send email** — send via Gmail to all attendees (confirm list first)
- **Edit** — let the user modify before sending
- **Copy only** — copy the debrief to clipboard, don't send the email
- **Save to Drive** — create a new Google Doc with the debrief content

**Never send the email without explicit confirmation.** Always show the draft and recipient list before sending.

## Guidelines

- **Confirm recipients before sending.** Show the To: list explicitly — some attendees may not want the full group on the follow-up.
- **One owner per action item.** If a task was assigned to "the team", ask who specifically owns it. Shared ownership means no ownership.
- **Propose deadlines when none were set.** Use the next logical business day or end-of-week. Flag proposed deadlines so the user can adjust.
- **Don't invent decisions.** If the user's recap is ambiguous, ask before writing "we decided X."
- **Graceful degradation.** If Calendar or Gmail aren't connected, ask the user to paste the invite or attendee list. Don't block.
- **Skip the agenda.** The debrief is about outcomes, not what was on the agenda. Attendees know what was discussed; they need to know what was decided.

## Example

**User:** "Debrief the architecture review we just had"

**Skill pulls:** Calendar event "Architecture Review" (2:00–3:00 PM, 4 attendees), linked Drive doc "System Design v3", Gmail invite thread.

**Skill asks:** "Quick recap: what were the main decisions, and who's doing what?"

**User says:** "We're going with the event-driven approach. Jordan's rewriting the queue service by end of sprint. Maria's updating the ADR this week. We're not sure yet about the retry policy — Jordan will look into it."

**Output:**
```
Meeting: Architecture Review
Date: May 29, 2026, 2:00–3:00 PM
Attendees: Jordan, Maria, Sam, you

## Decisions
- Event-driven architecture selected over request/response for the queue service.

## Action Items
| Owner  | Task                          | Due    |
|--------|-------------------------------|--------|
| Jordan | Rewrite queue service         | Jun 6  |
| Maria  | Update ADR                    | Jun 2  |

## Open Questions
- Retry policy for failed events — Jordan investigating; bring to next review.
```

Draft follow-up email ready to send to all 4 attendees.
