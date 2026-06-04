---
name: standup-drafter
description: >-
  Drafts an async standup update by pulling yesterday's Calendar events, Linear
  tickets touched, Gmail threads contributed to, and Slack activity — then formats
  it for Slack, Linear, or Notion in under 30 seconds.
  Use when writing a daily standup, preparing an async update, saying "what did I
  do yesterday?", prepping for a sync standup call, or drafting a status message
  for the team.
---

# Standup Drafter

Async standups take longer than they should. The part that takes time isn't the writing — it's recalling what you actually did across five different surfaces. This skill pulls that context, synthesizes it into a yesterday / today / blockers draft, and hands you something ready to paste.

## Configuration

```
format: slack              # slack | linear | notion | markdown
window: yesterday          # yesterday | today-so-far | custom
include_blockers: prompt   # prompt | omit | include-open-linear
```

## Process

### 1. Detect Available Sources

Check what integrations are connected in this session:

- **Google Calendar** — meetings attended yesterday
- **Linear** — tickets moved, commented on, or closed
- **Gmail** — threads you replied to or initiated
- **Slack** (if connected via MCP) — messages and threads you contributed to

Report what's connected:

```
Connected sources:
  ✅ Google Calendar
  ✅ Gmail
  ✅ Linear (via MCP)
  ❌ Slack — not connected
```

If no work-related sources are connected, explain what to link in Settings > Connected apps and stop.

### 2. Ask for Scope (first use each conversation)

> **Which standup?**
> A) Yesterday → Today (default)
> B) Today so far
> C) Custom range

Accept brief answers. If the user says "just go" or similar, use option A.

### 3. Gather Yesterday's Activity

Pull from each connected source within the time window:

**Calendar:**
Meetings attended. Filter out purely passive attendance (all-hands, recurring standups the user doesn't lead). Include: 1:1s, working sessions, meetings where the user led or presented.

**Linear:**
Tickets you moved (status change), commented on, or created. Note the status transition: "closed", "moved to in-progress", "unblocked by". Include ticket IDs.

**Gmail:**
Threads where you sent a reply or a new email. Exclude newsletters, automated notifications, and calendar invites.

**Slack (if connected):**
Channels and DMs where you sent substantive messages. Focus on work threads, not social.

### 4. Draft the Update

Structure as three sections:

```
**Yesterday**
• [2–4 bullets — what moved, with ticket IDs where available]

**Today**
• [2–3 bullets — inferred from open Linear tickets + today's calendar]

**Blockers**
• None  (or 1–2 bullets pulled from Linear blocked items)
```

Format rules:
- Bullets are one line each
- Yesterday: past tense ("Shipped X", "Reviewed Y", "Moved Z to review")
- Today: forward tense ("Finishing X", "Pairing on Y at 2pm")
- Ticket IDs always included: "[LIN-42]", not just "the auth migration"

Apply the configured format (Slack markdown `*bold*`, Linear comment style, Notion block, plain markdown).

### 5. Review and Refine

Show the draft and ask:

> Does this look right? Say "add X", "remove Y", or "done" when ready.

Accept freeform edits. When the user says "done" or "send it", output the final version as a clean copyable block.

**Never post automatically.** The user pastes; this skill drafts.

## Guidelines

- **Yesterday is the whole point** — the "today" section is a projection from open tickets and calendar. If context is thin, generate a reasonable projection rather than asking the user to fill it in.
- **Filter calendar noise** — recurring daily standups, all-hands, and passive large-group meetings are context, not output. Include meetings where the user had a role.
- **Ticket IDs make it useful** — always include Linear ticket IDs. "Shipped auth migration" is less useful than "Shipped auth migration [LIN-42]".
- **Short is better** — three bullets per section is the target. Five is the ceiling. If there's more, pick the most impactful.
- **Blockers default to None** — many engineers genuinely have none. Don't force a blocker.
- **Graceful degradation** — if Linear isn't connected, build from Calendar and Gmail alone. A shorter standup from fewer sources beats no standup.

## Example

**User:** "Draft my standup"

**Output (Slack format):**

```
*Yesterday*
• Merged auth service rate-limiting [LIN-42] — after two rounds of review
• Reviewed and approved the notification service refactor PR
• Synced with design on Q3 onboarding spec, resolved progressive disclosure question

*Today*
• Finishing API docs for the rate-limiting endpoint [LIN-67]
• Sprint planning at 10am

*Blockers*
• None
```
