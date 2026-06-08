---
name: week-review
description: >-
  Synthesizes the past week from Google Calendar, Gmail, and Google Drive into a
  structured weekly recap. Compiles meetings attended, decisions made, notable email
  threads, documents updated, and open loops not yet resolved. Previews next week's
  commitments. Use when doing a weekly review, end-of-week wind-down, Monday morning
  catchup, or any time the question is "what happened last week and what's coming?"
---

# Week Review

By Friday afternoon the mental model of the week is already fragmenting — meeting
decisions buried in calendar invites, email threads with outstanding asks, a Drive
doc from Tuesday half-forgotten. Reconstructing it all requires opening five tabs and
twenty minutes. This skill does that synthesis in one pass.

## Configuration

```
time_window: last_week     # "last_week" (Mon–Sun) or "last_7_days"
include_gmail: true        # Scan notable email threads from the week
include_drive: true        # Include recently modified Google Drive docs
next_week_preview: true    # Append a snapshot of the coming week
max_meetings: 12           # Cap on meetings shown in the recap
```

## Process

### 1. Detect Available Sources

Check which Google Workspace integrations are active:

```
Connected sources:
  ✅ Google Calendar — required
  ✅ Gmail — optional
  ✅ Google Drive — optional
  ❌ Slack — not connected (skip)
```

If Calendar is unavailable, stop and explain what's needed. Note any missing optional
sources at the top of the recap — don't bury it.

### 2. Gather the Week's Data

**Date range**: Default to last Monday 00:00 – last Sunday 23:59 in the user's calendar
timezone. If `time_window: last_7_days`, use today − 7 days instead.

**Calendar** — pull all events in range:
- Include: meetings with ≥2 attendees, 1:1s, recurring standups, ad-hoc calls.
- Skip: all-day personal blocks ("OOO", "Focus time", "Lunch") unless they span
  multiple days or have attendees.
- For each meeting: title, duration, attendees (names only), linked agenda doc if any.

**Gmail** (if connected):
- Find threads where the user was in To: (not just CC:) that had activity this week.
- Limit to the 6 most active by reply count.
- Exclude: newsletters, automated notifications, GitHub/Linear digest emails.
- One-line summary per thread.

**Drive** (if connected):
- Files modified by or shared with the user during the week.
- Exclude: auto-generated exports, files the user only viewed without editing.
- Filename and last-modified date are enough — no need to read file content.

### 3. Build the Recap

Organize into four sections:

**📅 Meetings & Decisions**

List chronologically. For meetings with a recorded agenda doc or clear outcome, add a
one-line outcome note. Mark meetings where a commitment was made or a decision landed.
If a meeting has no notes and no follow-up visible, say "(no recorded outcome)."

```
Mon — Sprint kickoff (60 min, team)
  → Agreed to carry over auth migration; picked up 5 new tickets
Tue — 1:1 with manager (30 min)
  (no recorded outcome)
Wed — Vendor sync (45 min, external)
  → Demo scheduled for next Thursday
```

**📨 Notable Exchanges**

3–5 email threads, one line each. Flag threads with an unanswered ask with ⚠️.

**📄 Documents Touched**

Drive files from the week. One line each. Connect to a meeting where the link is
obvious (e.g., the doc is named after the same project discussed in a meeting).

**🔴 Open Loops**

This is the most valuable section. Surface:
- Meetings with no recorded outcome and no visible follow-up
- Email threads with an outstanding question that had no reply yet
- Drive docs with "[Draft]" or "WIP" in the title and no calendar event to finalize them
- Any visible commitment that doesn't have a follow-up thread or event

Format:
```
• Jordan's API quota question (Gmail, Tue) — no reply yet
• "Onboarding redesign spec [Draft]" — still open, no finalize date in calendar
```

If no open loops are found, say so — it's good news.

### 4. Preview Next Week

Pull Calendar events for the coming Mon–Fri. Show:
- Total number of meetings
- Heaviest day
- Any meeting that needs prep (external guests, linked deliverable docs)
- Largest clear focus window

```
Next week (Jun 9–13): 11 events — heaviest Wednesday (4 meetings)
  Needs prep: Board demo Thursday 2pm
  Best focus window: Tuesday morning (3h clear)
```

### 5. Offer Next Steps

After presenting the recap, ask once:

> Want me to:
> 1. **Save this** — create a Google Doc titled "Week Review — [date range]"
> 2. **Draft replies** — compose replies for flagged open-loop email threads
> 3. **Nothing** — recap only

Only act after an explicit selection. Never auto-save or send.

## Guidelines

- **Don't invent outcomes.** If a meeting has no notes or agenda doc, say "(no recorded
  outcome)" — never guess what was decided.
- **Proportional depth.** A short week (holiday, PTO) → a shorter recap. A dense week
  → more entries, still one sentence per item.
- **No email body quoting.** Summaries only. The user may be on a shared screen.
- **Honest about coverage.** If Drive returned no results or Gmail is not connected,
  say so at the top of the recap, not in a footnote.
- **No auto-save, no auto-send.** Every write action requires explicit user selection
  in Step 5.

## Example

**User:** "Weekly review please"

**Output:**

```
Week Review — Jun 2–6, 2026
Sources: Calendar ✅ Gmail ✅ Drive ✅

📅 Meetings & Decisions (8 meetings, 9.5h total)
  Mon — Sprint kickoff (60 min, team)
    → Carried over auth migration; picked up 5 new tickets
  Tue — 1:1 with Sarah (30 min)
    (no recorded outcome)
  Thu — Vendor sync (45 min, external)
    → Demo confirmed for next Thursday
  ... (5 more)

📨 Notable Exchanges
  • Jordan: "Quota limits for new endpoint?" — ⚠️ no reply yet
  • DevOps: "New deploy process live" — acknowledged, no action

📄 Documents Touched
  • "Q3 Roadmap v2.1" — updated Wed (linked to roadmap planning)
  • "[Draft] Onboarding redesign spec" — last edited Thu, still draft

🔴 Open Loops
  • Jordan's quota question (Gmail, Tue) — unanswered
  • Onboarding spec still draft — no finalize event in calendar

Next week (Jun 9–13): 11 events — heaviest Wednesday
  Needs prep: Board demo Thursday 2pm
  Best focus window: Tuesday morning

Want me to: 1) Save this  2) Draft replies  3) Nothing
```
