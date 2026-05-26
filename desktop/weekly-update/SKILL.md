---
name: weekly-update
description: >-
  Synthesizes the past week's activity from Google Calendar, Gmail, and Google
  Drive into a structured status update ready to share with a manager or team.
  Scans meetings attended, emails sent, and documents created to surface
  what was done, what's in progress, and what's blocked — without manual
  tab-switching. Use when asked to write a weekly update, prepare a status
  report, draft an end-of-week summary, recap the week for a manager, or
  answer "what did I work on this week?"
---

# Weekly Update

Every week the same ritual: open Calendar, scroll back through the week, open Gmail, try to remember which threads were significant, check Drive for docs created. Twenty minutes of tab-switching later the update is still missing half of what happened. This skill does that sweep in seconds and drafts the update.

## Configuration

```
time_window: this_week          # "this_week" (Mon–today) or "last_7_days"
format: done_in_progress_next   # done_in_progress_next | bullets | narrative
audience: manager               # manager | team | personal
output: slack                   # slack | email | plain
```

Override any setting at runtime: "last week's update in email format for the team."

## Process

### 1. Detect Available Sources

Check which Google Workspace integrations are connected:

```
Connected sources:
  ✅ Google Calendar — via Google Workspace
  ✅ Gmail — via Google Workspace
  ✅ Google Drive — via Google Workspace
  ❌ [other] — not connected
```

If no Workspace sources are detected, explain how to connect them (Settings > Connected apps) and stop. Don't fabricate activity.

### 2. Ask One Setup Question (First Use Each Conversation)

If preferences haven't been set this session, ask a single compound question:

> **Quick setup:** Time window? (default: this week Mon–today) / Format? (done-in-progress-next, bullets, narrative) / Audience? (manager, team, personal) / Output? (Slack, email, plain)

Accept "just go" — fall back to defaults from the Configuration section.

### 3. Gather This Week's Activity

Pull activity from each connected source for the configured time window:

**Google Calendar:**
- Events where the user is organizer or accepted attendee (skip declined events)
- Note: meeting title, attendees (count or names), whether it recurs
- Ignore: all-day events that are blocks (OOO, focus time) unless notable

**Gmail:**
- Emails **sent** (not received) — these represent decisions, deliverables, responses
- Look for: threads where user's reply resolved something, external communications, announcements
- Skip: automated notifications, newsletters, calendar confirmations

**Google Drive:**
- Documents, sheets, or presentations created or last-edited by the user this week
- Note: doc title and what kind of work it represents (spec, report, deck, spreadsheet)
- Skip: docs where user only made minor edits or comments

### 4. Classify Activity Into Buckets

Sort gathered items into:

- **Done** — work that reached a completion point this week: shipped, sent, decided, published, handed off
- **In Progress** — active work that continues into next week: drafts, ongoing projects, work in review
- **Next** — explicitly planned or committed work for the coming week
- **Blocked** — items waiting on someone else's input, approval, or dependency

Not every item needs to appear. Filter to what's meaningful — 3–6 bullets per section at most. Don't list routine recurring meetings as accomplishments.

### 5. Draft the Update

Format per configuration:

**done_in_progress_next (default):**
```
Weekly Update — [Date Range]

✅ Done
• [Deliverable] — [one-line context]
• [Deliverable] — [one-line context]

🔄 In Progress
• [Work item] — [where it stands, expected finish]

🔜 Next
• [Planned work]

🔴 Blocked
• [Item] — waiting on [person/thing]
```

**bullets:**
```
Week of [dates]:
- Completed [X]
- Still working on [Y]
- Starting [Z] next week
```

**narrative:** Two short paragraphs. First: what was accomplished and why it mattered. Second: what's coming up and any blockers.

Apply output formatting:
- **Slack**: use `*bold*` for section headers, trim to 8 bullets max
- **email**: plain prose headers, suitable for copy-paste into Gmail
- **plain**: no special formatting, just clean text

### 6. Present and Offer Edits

Show the draft, then ask:

> Looks good to send, or want me to adjust anything? (add/remove items, change tone, swap format, add context for a specific item)

Make any requested edits. Never send directly — output is always for the user to paste.

## Guidelines

- **Detect, don't assume** — only use sources that are actually connected. Never invent activity.
- **Filter ruthlessly** — three strong bullets beat ten weak ones. If an item doesn't answer "so what?", drop it.
- **Done ≠ attended** — a meeting alone is not a deliverable. Surface the outcome or decision, not the event.
- **Blockers are useful signal** — don't soften them. If something is blocked, say it plainly.
- **One question, then go** — don't stall with setup. Defaults exist so the first run requires zero configuration.
- **Respect the audience** — manager format is outcome-focused; team format can include more context; personal is a log.
- **Graceful degradation** — if Drive or Gmail is unavailable, note it and continue with what's connected. Don't block the whole update.

## Example

**User:** "Write my weekly update"

**Output:**

```
Weekly Update — May 19–23

✅ Done
• Shipped auth refactor PR — merged Thursday, unblocks SSO work
• Sent Q2 roadmap draft to leadership for review
• Resolved billing edge-case bug reported by support (root-caused to timezone handling)

🔄 In Progress
• SSO integration — 70% done, tests pending, targeting EOD next Tuesday
• Design review for onboarding redesign — doc circulated, awaiting design feedback

🔜 Next
• Start mobile push notification spike
• Kick off Q3 planning doc

🔴 Blocked
• Staging environment cert renewal — waiting on ops to rotate the cert
```
