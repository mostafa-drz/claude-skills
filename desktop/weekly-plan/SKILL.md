---
name: weekly-plan
description: >-
  Synthesizes a forward-looking week plan from Calendar, Gmail, and Linear.
  Scans the coming seven days of meetings, surfaces email threads that need
  action this week, and pulls current-cycle Linear priorities, then produces a
  structured plan: meeting density by day, the top three outcomes to own, open
  focus windows, and a short defer list. Use when planning the week ahead,
  asking what to focus on this week, Monday morning planning, weekly review,
  preparing for standup, or when asked 'what's my week look like'.
---

# Weekly Plan

Every week starts as a pile: Calendar full of overlapping events, inbox threads silently waiting, Linear tickets queued with no sense of when. This skill turns that pile into a clear week plan — where your time is actually going, what has to ship, and which windows are genuinely free for the work that matters.

## Process

### 1. Detect available sources

Check which integrations are reachable in this session:

```
Connected sources:
  ✅ Google Calendar — via Google Workspace
  ✅ Gmail — via Google Workspace
  ✅ Linear — via MCP
  ❌ Notion — not connected
```

Proceed with whatever is available. If neither Calendar nor Linear is connected, explain what to connect and stop.

### 2. Gather the week's raw data

Pull data for the next 7 calendar days (Mon–Sun, or today through day 7 if mid-week):

**Calendar** — all events: title, time, duration, attendees, any linked docs.

**Gmail** — threads where:
- User is in To: (not just CC:)
- Thread is unread or has a reply in the last 3 days
- Subject or sender suggests a decision, approval, or deliverable this week

**Linear** — for the active cycle (current sprint):
- In Progress tickets assigned to the user
- Unstarted tickets assigned to the user, ordered by priority
- Overdue tickets (past due date, not done)

### 3. Map meeting density

Show the meeting load day by day:

```
Mon  ████░░░░  3 events (4.5h)  → heavy
Tue  ██░░░░░░  1 event  (1.0h)  → light
Wed  █████░░░  4 events (5.0h)  → heavy
Thu  ███░░░░░  2 events (2.0h)  → medium
Fri  █░░░░░░░  1 event  (0.5h)  → light
```

Heavy days (>3h of meetings) are low-output days. Surface this explicitly — they're useful for async reviews and logistics, not deep work.

### 4. Find focus windows

For each day, identify unscheduled continuous blocks of ≥ 90 minutes:

```
Tue  9:00–12:00  → 3h focus window  ⭐ best slot
Thu  14:00–17:00 → 3h focus window
Fri  9:00–16:30  → open (protect one block)
```

Recommend exactly **one** focus block to treat as non-negotiable this week — prefer the earliest large block in the week. One recommendation, clearly marked.

### 5. Surface email actions

From Gmail, pull threads that need a reply or decision this week. Cap at 5 items:

```
📧 Jordan – "Q3 tooling budget" — waiting for your approval
📧 Design – "Figma handoff for checkout" — question about the spec
```

One-line context only. No quoting message content. Privacy-first.

### 6. Propose top 3 outcomes

Cross-reference Linear priorities and email signals. Propose 3 concrete **outcomes** to own this week — shipped results, not tasks:

```
1. Ship auth-token PR to staging (Linear AIS-342, unblocks QA)
2. Approve Q3 tooling budget (thread from Jordan)
3. Close 2 overdue P1 tickets (AIS-318, AIS-327)
```

Ask the user to confirm or adjust. The user's correction here is the most important signal — save it if it reveals a pattern (recurring priority, a team dependency).

### 7. Build the week plan

After confirmation, produce the final plan:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Week of June 16 – 20, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Top 3 outcomes this week
  1. Ship auth-token PR to staging
  2. Approve Q3 tooling budget
  3. Close AIS-318 + AIS-327 (overdue P1)

⏱️ Focus windows
  ★ Tue 9–12    (3h) ← protect this — deep work slot
    Thu 14–17   (3h) ← secondary
    Fri (TBD)   schedule a block if the above slips

📅 Day by day
  Mon  Heavy (4.5h mtgs) — async/reviews/email only
  Tue  Light ★          — auth-token PR (deep work)
  Wed  Heavy (5.0h mtgs) — standups + design sync
  Thu  Medium            — close AIS-318
  Fri  Light             — close AIS-327, Jordan reply

📧 Email actions (2)
  • Jordan — Q3 budget (approve or push back by Wed)
  • Design — Figma handoff question (reply Tue EOD)

📌 Defer to next cycle
  AIS-405 (low priority, no deadline)
  Newsletter re: pricing — not time-sensitive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then ask: "Want me to block Tuesday 9–12 on your Calendar as focus time?"

### 8. Optional: Create focus block on Calendar

If the user confirms, create a Calendar event for the recommended focus window:
- Title: `Focus: [outcome]`
- No attendees, no invite
- Description: the top outcome it's reserved for

Confirm the event details before creating. One event only.

## Guidelines

- **Forward only** — scans the coming week, not the past. Don't summarize yesterday unless mid-week.
- **Outcomes, not tasks** — the top 3 should be things that move the needle if shipped; not a task list.
- **One focus block recommendation** — always pick one, clearly starred. Three equal suggestions is not a recommendation.
- **Confirm before acting** — never create Calendar events without explicit user approval.
- **Privacy-aware** — email items get one-line context max. Don't quote thread content in the plan.
- **Graceful degradation** — if Linear isn't connected, derive outcomes from Calendar + email alone. If Gmail isn't connected, skip the email section and note it.
- **Mid-week runs** — if today is Wednesday or later, acknowledge the partial week and plan remaining days only. Don't pretend Monday is still ahead.

## Example

**User:** "Plan my week"

**Output:** A week plan showing Monday and Wednesday as heavy-meeting days, Tuesday 9–12 as the protected focus block, three outcomes drawn from open Linear tickets and a pending email approval, and a short defer list of two items that won't fit without dropping something important.
