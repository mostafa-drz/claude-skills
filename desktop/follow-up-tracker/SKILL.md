---
name: follow-up-tracker
description: >-
  Scans Gmail to surface threads where the user sent the last message and no
  reply has arrived yet, then groups them by age and inferred urgency. Optionally
  drafts a polite follow-up nudge for any stuck thread. Gmail has no native
  "waiting for reply" view — this fills that gap. Use when asked "what am I
  still waiting on", "who hasn't replied to me", "any pending emails I should
  chase", "check my unanswered follow-ups", "what conversations are stuck", or
  before going on leave, at the end of a sprint, or at the start of a new week.
---

# Follow-Up Tracker

Gmail shows what landed in your inbox. It doesn't show what's stuck in someone
else's. Threads you sent last week — asking for a decision, a review, a
confirmation — sit invisible until you happen to remember them. This skill
searches your Sent folder, identifies threads where no reply came back, and
surfaces them sorted by how long they've been waiting.

## Configuration

```
lookback_days: 21              # how far back to scan sent messages (default: 3 weeks)
min_wait_days: 2               # ignore sends less than N days old (too fresh)
exclude_self: true             # exclude threads where you sent to yourself
flag_personal: true            # flag threads that look non-work (newsletters, receipts)
```

## Process

### 1. Clarify Scope

Ask (or infer from context):

1. **Time window** — default to the last 21 days; override if the user says "last month" or a range
2. **Contacts to prioritize** — any names or domains that should always surface first
3. **Categories to skip** — if the user only cares about a specific context (e.g., "external partners only")

If the user says "just go," proceed with defaults.

### 2. Find Candidate Sent Threads

Search Gmail Sent for messages the user composed (not auto-replies or forwards) sent
within the lookback window:

```
in:sent after:YYYY/MM/DD before:YYYY/MM/DD
```

Exclude obvious automated sends:
- Messages where the To: address contains `noreply`, `no-reply`, `donotreply`, `notifications`, `alerts`
- Messages the user sent to mailing lists (if detectable from To: pattern)
- Auto-generated calendar invite notifications

Collect up to 60 candidate threads.

### 3. Check Each Thread for a Reply

For each candidate thread, check whether a message arrived from the recipient(s)
after the user's sent message:

- **No reply found** → thread is awaiting a response. Keep it.
- **Reply exists** → thread is resolved. Discard it.
- **Only the user replied again** → the user already followed up. Note this and keep it
  (they may still be waiting).

If the Gmail MCP does not support per-thread inspection, approximate by searching for
incoming messages from the same sender domains within the same date range and matching
on subject/thread ID.

### 4. Enrich Each Pending Thread

For each thread remaining:

| Field | What to extract |
|-------|----------------|
| Recipient | Name + email address |
| Subject | Thread subject line |
| Sent | Date the user's message was sent |
| Days waiting | Today minus sent date |
| User already followed up | Yes / No |
| Urgency signal | Inferred from subject: deadline keywords, question marks, direct asks |

### 5. Group and Rank

Sort pending threads into urgency tiers:

```
🔴 Overdue — no reply in 14+ days
🟡 Aging   — no reply in 7–13 days
🟢 Pending — no reply in 2–6 days  (informational; not urgent yet)
```

Within each tier, sort by: priority contacts first, then by descending days waiting.

### 6. Present the Summary

```
Follow-Up Tracker — week of May 17 2026
Sent in last 21 days: 47 threads  |  Awaiting reply: 11  |  Already followed up: 3

🔴 Overdue (3 — 14+ days)
  1. Marcus Chen — "Q2 budget approval" — sent 19 days ago
     Sent a direct ask for sign-off. No reply.
  2. product@client.co — "Integration spec questions" — sent 16 days ago
     Three open questions. No reply.
  3. hr@company.com — "PTO request for June" — sent 14 days ago
     Waiting on confirmation.

🟡 Aging (5 — 7–13 days)
  4. Sara Kovacs — "PR review request" — sent 10 days ago
  5. engineering-team — "RFC: caching strategy" — sent 9 days ago  [already followed up once]
  ...

🟢 Pending (3 — 2–6 days)
  8. design@studio.co — "Feedback on mockups" — sent 5 days ago
  ...
```

Then ask:
> Want me to draft a follow-up for any of these? Just name the number or say "all overdue."

### 7. Draft Follow-Ups (On Request)

For each requested thread:

1. Read the original sent message for context
2. Draft a brief, non-pushy nudge (2–4 sentences max):
   - Acknowledge the original thread
   - Restate what's needed in one sentence
   - Offer a softer ask if appropriate ("happy to chat if easier")
3. Show the draft and ask:
   - **Send** — send the reply (requires Gmail send permission)
   - **Edit** — let the user modify, then re-confirm
   - **Skip** — move to the next

**Never send without explicit user confirmation.**

## Guidelines

- **Detect, don't invent** — only surface threads that actually appear in Sent. Never fabricate entries.
- **Confirm before sending** — every draft must be shown and approved. No silent sends.
- **Flag the follow-up-already cases** — if the user already sent a second message, mark it. Two unanswered follow-ups need a different tone than a first nudge.
- **Filter automated noise** — receipts, newsletter confirmations, calendar notifications, and alerts are not follow-up candidates. Surface only human-to-human threads.
- **Respect cadence** — the `min_wait_days` setting exists to avoid chasing something sent yesterday. Default 2 days; adjust if the user's context is faster-moving.
- **Gmail not connected** — explain how to connect Google Workspace (Settings > Connected apps) and stop. Don't proceed without Gmail access.

## Example

**User:** "What am I still waiting on from last week?"

**Skill:** Scans Sent for the last 21 days, finds 9 threads with no reply. Surfaces:
2 overdue (16+ days), 4 aging (7–13 days), 3 pending (3–6 days). User asks to
draft follow-ups for the 2 overdue threads. Shows both drafts for approval.
