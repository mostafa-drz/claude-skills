---
name: meeting-followup
description: >-
  Drafts group and individual follow-up emails after a meeting, drawing from
  Google Calendar event details, linked Drive notes, and the attendee list.
  Produces a group recap (decisions made, action items table with owners and
  due dates) and a concise personalized message for each action owner.
  All drafts are shown for approval before anything is sent.
  Use after a meeting, call, or standup to send follow-ups, recap a session,
  document what was decided, capture action items, or summarize agreements
  for the team. Triggers on: "follow up on my meeting", "send recap",
  "draft follow-ups from my call", "post-meeting summary", "email action items".
---

# Meeting Follow-Up

Every meeting produces decisions and commitments. Getting them written down and into the right inboxes within the hour is the difference between things happening and things being forgotten. This skill finds the meeting, reads any linked notes, and drafts the messages — group recap and personalized follow-ups — for you to approve before anything sends.

## Process

### 1. Detect Available Integrations

Check what's accessible in this session:

```
Connected:
  ✅ Google Calendar — event lookup, attendees, linked docs
  ✅ Google Drive — read linked notes docs
  ✅ Gmail — draft and send follow-up messages
  ❌ [missing integration] — note and continue without it
```

If Calendar is not connected, ask the user to paste the meeting details (title, attendees, key points) and skip to step 4.

### 2. Find the Meeting

If the user named a meeting (e.g., "my 2pm with the product team"), search Calendar for it. Otherwise, fetch the most recently completed event from the past 4 hours.

Show a one-line confirmation before proceeding:

```
Found: "Q3 Roadmap Sync" — today 2:00–3:00 PM
Attendees: Sarah (sarah@…), Alex (alex@…), Jordan (jordan@…)
Linked doc: Q3 Roadmap Notes (Drive)
Proceed? [yes / pick a different meeting]
```

If multiple matches exist, list them and ask which one.

### 3. Retrieve Event Details and Notes

From the Calendar event:
- Title, date/time, duration
- Full attendee list (names + emails)
- Description field (often contains agenda or doc links)
- Any attached or linked Drive documents

From the linked Drive doc (if present):
- Read the full document
- Extract: decisions made, action items with owners, open questions, key context

If no Drive doc is linked, note that and proceed — the user will fill in the details in step 4.

### 4. Ask for Corrections and Additions

Present what was found and ask once:

```
From "Q3 Roadmap Sync":

Decisions:
  • Shipping auth redesign in Q3 (not Q4)
  • Jordan owns the API migration

Action items:
  • Sarah — finalize wireframes by June 26
  • Alex — draft migration plan by June 23
  • Jordan — schedule follow-up with backend team

Open questions: none captured

Anything to add, correct, or remove before I draft?
```

Accept free-form corrections. If the user says "looks good" or similar, proceed.

### 5. Draft the Group Recap Email

Write a reply-all email to all attendees. Keep it scannable — this is a reference document, not prose.

```
Subject: [Recap] Q3 Roadmap Sync — June 19

Hi team,

Quick recap from today's Q3 Roadmap Sync.

**Decisions**
- Auth redesign moves to Q3 (not Q4). Shipping target: end of August.
- Jordan leads the API migration.

**Action Items**
| Who    | What                              | By         |
|--------|-----------------------------------|------------|
| Sarah  | Finalize wireframes               | June 26    |
| Alex   | Draft migration plan              | June 23    |
| Jordan | Schedule backend follow-up        | EOW        |

**Open Questions**
None — all items resolved or assigned.

Let me know if I missed anything.
[Name]
```

Tone: direct, factual. No "per my last email" energy. No padding.

### 6. Draft Individual Follow-Ups

For each person with an action item, write a short personal message:

```
To: Sarah
Subject: Your action from Q3 Roadmap Sync

Hey Sarah — quick note from today's call.

Your action: finalize wireframes by June 26.

Context: we locked auth redesign for Q3, so the wireframes are now on the critical path. Let me know if anything changed.

[Name]
```

Keep individual messages to 3–5 lines. Personalize only based on their specific item. Do not CC the whole group.

### 7. Present All Drafts for Approval

Show drafts in order:
1. Group recap (to all attendees)
2. Individual follow-ups (one per action owner)

For each draft, ask:
- **Send** — send it
- **Edit** — show the draft text for the user to modify, then confirm
- **Skip** — don't send this one

Do not send any message until the user explicitly says "send" for that specific draft.

### 8. Send Approved Messages

Send each approved message via Gmail. After each send, confirm:

```
✅ Sent group recap to 3 attendees.
✅ Sent individual note to Sarah.
⏭ Skipped Alex (you chose to skip).
```

## Guidelines

- **Never send without explicit per-draft approval.** Show every message before it goes.
- **Don't fabricate action items.** Only include what appears in the notes doc or what the user states. If uncertain about an owner, assign TBD.
- **If no Drive doc exists**, work only from what the user tells you in step 4. Don't guess at decisions.
- **Respect missing integrations.** If Gmail is not connected, present the drafts as copy-paste text the user can send manually.
- **Short individual messages.** The recap email is the record; individual messages are prompts, not summaries.
- **If an event has no action items**, say so and offer only the group recap (decisions only).

## Example

**User:** "Follow up on my 3pm product sync"

**Skill finds:** "Product Sync" at 3pm, 4 attendees, linked doc with 2 decisions and 3 action items.

**Output:** Group recap email with decision bullets and action table, plus 3 individual notes (one per action owner). User approves all → 4 messages sent.
