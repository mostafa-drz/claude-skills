---
name: inbox-catchup
description: >-
  Scans all connected communication channels — Gmail, Slack, Calendar, and any
  available integrations — then produces a prioritized catchup briefing.
  Helps triage messages and draft replies. Use when starting the day, returning
  from a break, or needing to quickly catch up on communications.
---

# Inbox Catchup

Scan connected communication sources, build a prioritized briefing, and help triage and respond.

## Configuration

Edit these defaults before uploading, or override at runtime when prompted.

```
sources: all                    # "all" or comma-separated: gmail, calendar, slack
time_window: 4h                 # How far back to scan: 1h, 4h, today, yesterday
priority_contacts: []           # Names/emails that always surface first
reply_tone: professional        # professional, casual, brief
auto_draft: true                # Offer to draft replies for items that need response
```

## Process

### 1. Detect Available Sources

Check what communication integrations and tools are accessible in this session:

- **Google Workspace** — Gmail (unread/recent emails), Google Calendar (upcoming events)
- **MCP servers** — Check for any connected messaging tools (Slack, Teams, Discord, etc.)
- **Other integrations** — Any other data sources available

Report what was found:

```
Connected sources:
  ✅ Gmail — via Google Workspace
  ✅ Google Calendar — via Google Workspace
  ✅ Slack — via MCP server
  ❌ Messages — not connected
```

If no communication sources are detected, explain what integrations are needed and how to connect them (Settings > Connected apps for Google Workspace, or configure MCP servers in Desktop settings). Then stop.

### 2. Ask Preferences (First Use Each Conversation)

If this is the first time running in this conversation, ask:

> **Quick setup for this catchup:**
> 1. Which sources to scan? (default: all connected)
> 2. Time window? (default: last 4 hours)
> 3. Any priority contacts to surface first?

Accept brief answers. If the user says "just go" or similar, use the defaults from the Configuration section above.

### 3. Scan All Sources

For each connected source, gather recent items within the time window:

**Gmail:**
- Unread emails in inbox
- Emails where the user is in To: (not just CC:)
- Threads with recent replies

**Google Calendar:**
- Events in the next 4 hours
- Events that started in the last hour (may have missed)
- Events with attachments or agenda docs

**Slack (if connected via MCP):**
- Unread DMs
- Mentions in channels
- Threads the user is part of with new replies

**Other MCP sources:**
- Follow the same pattern: unread, mentions, direct messages

### 4. Build the Briefing

Organize everything into three priority tiers:

**🔴 Needs Reply** — Messages directly to the user that appear to expect a response. Sort by sender importance (priority contacts first), then recency.

For each item show:
```
[Source] From: sender — subject/preview
  Received: time ago
  Context: 1-line summary of what they're asking/saying
```

**🟡 FYI — Worth Reading** — Informational messages, CC'd threads, channel activity. No response expected but may be relevant.

For each item show:
```
[Source] subject/channel — 1-line summary
  Why it matters: brief reason this was flagged
```

**🟢 Upcoming** — Calendar events in the next few hours.

For each item show:
```
[Calendar] event title — time
  With: attendees
  Prep: any linked docs or agenda items
```

### 5. Present the Briefing

Show a clean summary:

```
📬 Inbox Catchup — [date/time]
Scanned: Gmail, Calendar, Slack (last 4 hours)

🔴 Needs Reply (3)
  1. [Gmail] Sarah — "Quick question about the API migration"
     30 min ago — Asking which endpoint to use for the new auth flow
  2. [Slack DM] Alex — "Can you review my PR?"
     1h ago — Wants review on #342 before EOD
  3. [Gmail] Jordan — "Meeting reschedule"
     2h ago — Proposing Thursday instead of Wednesday

🟡 FYI (5)
  • [Slack #engineering] Deploy discussion — team debating rollback strategy
  • [Gmail] Newsletter from TechCrunch — AI funding roundup
  • ... (3 more)

🟢 Upcoming (2)
  • 10:30 AM — Sprint planning (with: team)
  • 1:00 PM — 1:1 with manager (agenda doc linked)
```

Then ask:

> Want me to help draft replies? I'll take them one at a time, starting with the most urgent.

### 6. Interactive Triage

For each "Needs Reply" item (in priority order):

1. Show the full message content
2. Draft a reply matching the configured tone
3. Present the draft and ask:
   - **Send as-is** — send the reply
   - **Edit** — let the user modify, then confirm
   - **Skip** — move to the next item
   - **Stop** — end triage, show remaining items

**Never send a reply without explicit user confirmation.** Always show the draft first.

### 7. Wrap Up

After triage (or if the user chose not to reply):

```
✅ Catchup complete
  Replied: 2 messages
  Skipped: 1 message
  Still pending: 0

  Next event: Sprint planning in 45 min
```

## Guidelines

- **Detect, don't assume** — only use sources that are actually connected. Never fabricate messages or pretend a source is available when it isn't.
- **Confirm before sending** — every reply must be shown to the user and explicitly approved before sending. No auto-send, ever.
- **Respect priority contacts** — if configured, always surface messages from these people first regardless of recency.
- **Be concise in summaries** — the briefing should be scannable in under 30 seconds. Save detail for when the user drills into a specific item.
- **Graceful degradation** — if a source fails or returns no results, note it and continue with the others. Don't block the entire catchup because one source is down.
- **Privacy-aware** — don't summarize or quote message content beyond what's needed for triage. The user may be on a shared screen.
