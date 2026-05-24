---
name: pending-radar
description: >-
  Scans Gmail sent threads awaiting reply, Calendar meetings with unresolved
  action items, and Drive docs with open to-dos to surface what's fallen
  through the cracks. Produces a two-list breakdown: what you're waiting on
  others for and what you still owe. Use when asking "what's pending",
  "what needs follow-up", "what am I waiting on", "what did I promise",
  "what's overdue", or "what's fallen through the cracks".
---

# Pending Radar

Every few days there's a moment where something slipped: an email sent and never heard back on, an action item from a meeting three weeks ago, a doc with checkboxes no one ticked. Pending Radar scans your connected sources, finds those threads, and puts them in front of you before they become problems.

## Process

### 1. Detect Available Sources

Check what's accessible in this session:

- **Gmail** — required for sent-mail scanning
- **Google Calendar** — for recent past meetings with linked docs
- **Google Drive** — for docs with open action items

Report what was found:

```
Connected sources:
  ✅ Gmail — via Google Workspace
  ✅ Google Calendar — via Google Workspace
  ✅ Google Drive — via Google Workspace
```

If Gmail is not connected, explain that it's required (Gmail scans the sent-mail queue for pending replies) and stop. If Calendar or Drive are missing, proceed without them and note the gap.

### 2. Set the Scan Window

If not specified by the user, ask once:

> How far back should I look? (default: 7 days)

Accept natural answers: "this week", "since Monday", "14 days". Default to 7 days.

### 3. Scan Gmail — Threads Awaiting Reply

Search sent mail for threads where:
- You sent the last message and received no subsequent reply
- The thread falls within the scan window
- The recipient is not yourself (no self-notes or drafts)
- The sender pattern is not an automated service, newsletter, or no-reply address

For each thread found, note:

```
To: recipient name / email
Subject: thread subject
Sent: N days ago
Context: one-line summary of what you asked or requested
```

Rank by age — oldest unanswered first, since those are most likely forgotten.

### 4. Scan Calendar — Meetings with Open Action Items

For past Calendar events within the scan window:

1. Look for attached or linked Drive documents (meeting notes, agendas, summaries)
2. In those documents, scan for unchecked items: `[ ]`, `- [ ]`, `TODO:`, or similar markers
3. Note items that appear assigned to you, or unassigned items from meetings you ran

For each finding, note the meeting name, date, and the to-do text verbatim.

### 5. Scan Drive — Open To-Dos in Recent Docs

Search Drive for documents edited within the scan window that contain unchecked action items:

- Look for `[ ]`, `TODO`, `Action:`, or `@yourname` markers
- Prioritize docs shared with you by others (likely waiting on your input)
- Skip archived or read-only docs

### 6. Build the Breakdown

Organize everything into two lists:

**⏳ Waiting On** — things others owe you (you're the one waiting)

```
1. [Gmail] Alex — "Proposal review" — sent 5 days ago, no reply
2. [Calendar → Notes] "Q3 budget meeting" (May 19) — finance approval still pending
3. [Drive] "Design spec v3" — Maria marked TODO: your sign-off on error states
```

**✅ You Owe** — commitments you made that aren't done yet

```
1. [Gmail] Zara — "API migration doc" — you said you'd share by last Friday
2. [Calendar → Notes] "Team sync" (May 21) — you committed to sending the timeline
3. [Drive] "Onboarding guide" — TODO: deployment steps section (assigned to you)
```

If a source returned no results, say so explicitly: "Gmail: no unanswered threads in the last 7 days."

### 7. Present and Offer Follow-ups

Show the breakdown, then offer:

> Want me to draft a follow-up nudge for any "Waiting On" items? I'll keep them brief — one sentence, no pressure.

For each approved follow-up:
1. Show the drafted message
2. Confirm before sending
3. Never send without explicit approval

## Guidelines

- **Only report what's actually found.** No hallucinated items. If nothing is pending, say "All clear — nothing pending in the last N days."
- **Rank by staleness.** Oldest unanswered items first — the longest-forgotten are most likely to have consequences.
- **Classify carefully.** The "Waiting On" vs "You Owe" distinction is the point. An item where you both sent the email and promised a follow-up goes in "You Owe."
- **Skip noise.** Auto-replies, read receipts, mailing lists, newsletters, and calendar notification emails are not pending threads.
- **Respect the scope.** Only surface items within the requested scan window. Don't expand scope without asking.
- **Confirm before any send.** Follow-up drafts are proposals only. The user decides whether and when to send.

## Example

> "What's fallen through the cracks this week?"

```
Pending Radar — last 7 days
Sources: Gmail ✅  Calendar ✅  Drive ✅

⏳ Waiting On (3)
  1. [Gmail] Zara — "Contract terms" — sent 6 days ago, no reply
  2. [Gmail] Dev team — "Auth endpoint question" — sent 4 days ago, no reply
  3. [Calendar → Notes] "Design review" (May 19) — Figma update requested from Maria

✅ You Owe (2)
  1. [Drive] "Onboarding doc" — TODO: add deployment steps (last edited May 20)
  2. [Calendar → Notes] "Stakeholder sync" (May 21) — you said you'd share Q2 report

Draft a follow-up nudge for the contract email? (yes / skip / stop)
```
