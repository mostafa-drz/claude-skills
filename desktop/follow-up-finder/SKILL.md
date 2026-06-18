---
name: follow-up-finder
description: >-
  Scans Gmail sent mail for threads where you sent the last message and received
  no reply, then surfaces a prioritized follow-up queue grouped by how overdue
  each one is. Drafts follow-up messages on request — never sends automatically.
  Use when asked to check pending emails, find unanswered messages, see what's
  still waiting for a reply, review follow-ups, or catch up on outbound threads.
  Triggers on: "what emails are waiting", "follow up check", "did anyone reply
  to X", "what am I still waiting on", "pending replies", "unanswered emails".
---

# Follow-up Finder

Every sent folder is a graveyard of conversations that quietly died. Some were deliberate — you moved on. Others weren't — a request got lost, a question went unread, a decision stalled because nobody pushed. The difference is hard to see without a systematic scan.

This skill finds the threads where you sent last and nobody replied, groups them by how long they've been waiting, and helps you decide: follow up, let it go, or note it as resolved.

## Configuration

Edit these defaults in the SKILL.md before uploading, or override at the start of a conversation.

```
lookback_days: 30          # How far back to search in sent mail
at_risk_threshold: 3       # Days without reply before flagging as At-Risk
overdue_threshold: 7       # Days without reply before flagging as Overdue
max_threads: 40            # Maximum threads to scan (performance limit)
default_tone: professional # Follow-up draft tone: professional, friendly, brief
skip_newsletters: true     # Skip threads to newsletters / no-reply addresses
```

## Process

### 1. Check Gmail Connection

Confirm Gmail is accessible in this session. If not:

```
❌ Gmail not connected.
To connect: Settings > Connected apps > Google account.
Can't scan sent mail without Gmail access.
```

Stop here if Gmail is unavailable.

### 2. Ask Preferences (First Use Each Conversation)

On first run, ask:

> **Quick setup:**
> 1. How far back should I check? (default: 30 days)
> 2. Flag as overdue after how many days? (default: 7 days)
> 3. Any senders or topics to skip?

Accept brief answers. "Just go" or similar → use config defaults.

### 3. Scan Sent Threads

Search Gmail for recently sent threads:

- Query: `in:sent after:<date lookback_days ago>`
- Limit to `max_threads` results
- For each thread, fetch message list and check: **is the last message from me?**
  - If yes → no reply received → candidate for the queue
  - If no → someone replied → skip

Calculate thread age = days since my last sent message in the thread.

Skip threads where:
- The recipient address contains `noreply`, `no-reply`, `donotreply`, `newsletter`, `notifications`, or `alerts`
- Subject contains `[automated]`, `[notification]`, or `Unsubscribe`
- The original message was a CC (I wasn't the primary sender)

### 4. Build the Follow-up Queue

Group surviving threads into three tiers:

**🔴 Overdue** — No reply for `overdue_threshold`+ days. Likely needs a nudge or close.

**🟡 At-Risk** — No reply for `at_risk_threshold` to `overdue_threshold` days. Worth watching.

**🟢 Sent Recently** — No reply yet, but within `at_risk_threshold` days. May just be early.

For each thread show:
```
[age] To: recipient — subject
  Sent: <relative time>
  Preview: first 80 chars of my last message
```

### 5. Present the Queue

```
📤 Follow-up Queue — <today's date>
Scanned: last <lookback> days of sent mail (<N> threads checked)

🔴 Overdue (N)
  1. 12 days — To: Sarah Chen — "Feedback on Q3 design proposal"
     Sent June 6 — "Hi Sarah, wanted to get your thoughts on the…"
  2. 9 days  — To: ops@vendorco.com — "Contract renewal question"
     Sent June 9 — "Could you confirm the auto-renewal date before…"

🟡 At-Risk (N)
  3. 5 days — To: Marcus — "Introduction: Aisha from Anthropic"
     Sent June 13 — "Marcus, I wanted to introduce you to Aisha who…"

🟢 Sent Recently (N)
  4. 1 day — To: hiring@company.com — "Application: Senior Engineer role"
     Sent June 17 — "Please find my application attached…"
```

Then ask:
> Want me to help draft follow-ups? I'll take them one at a time. Or tell me which number to start with.

### 6. Draft Follow-ups (One at a Time)

For each selected thread:

1. Show the full original message and any context from the thread
2. Draft a follow-up in the configured tone — short, not pushy, gives them an easy out:
   - Reference the original: "Following up on my note from X days ago…"
   - Restate the ask in one sentence
   - Offer a simple response path: "A yes/no would help me know how to proceed"
   - Don't apologize for following up
3. Present the draft and ask:
   - **Send** — (you send it from Gmail — skill never sends)
   - **Edit** — revise, then confirm
   - **Skip** — move to next item
   - **Mark resolved** — remove from queue mentally, no follow-up needed
   - **Stop** — finish session

**Never send any message without explicit user approval.** The skill drafts; the user sends.

### 7. Wrap-up

```
✅ Follow-up session complete
  Drafts prepared: N
  Skipped: N
  Marked resolved: N
  Still pending: N (overdue), N (at-risk)
```

## Guidelines

- **Detect, don't assume** — only scan sources that are actually accessible. If Gmail isn't connected, say so clearly.
- **Confirm before sending** — drafts are shown first, always. The user clicks send in Gmail. The skill never triggers a send action.
- **Short follow-ups win** — drafts should be 3–5 sentences. Shorter is less annoying and more likely to get a reply.
- **Give them an out** — every draft should make it easy to say "no" or "not now". Pushy follow-ups damage relationships.
- **Skip automated noise** — if a thread looks like a ticket confirmation, newsletter, or auto-reply, skip it. The user wants human threads.
- **Respect recent sends** — don't push urgency on 🟢 items. Surface them for awareness only.
- **No fabrication** — if you can't fetch a thread's full content, show what you have and note the limitation.

## Example

**User:** "Check what emails I'm still waiting on"

**Skill activates:** Scans last 30 days of Gmail sent folder. Finds 28 threads where I sent last. Filters 8 (newsletters, no-reply, ticket confirmations). Surfaces 20 candidates.

**Output:**
```
📤 Follow-up Queue — June 18, 2026
Scanned: last 30 days (28 threads → 20 candidates after filtering)

🔴 Overdue (3)
  1. 14 days — To: Alex — "Proposal: workshop structure for July sprint"
     Sent June 4 — "Hey Alex, here's the outline I mentioned…"
  ...

🟡 At-Risk (5)
  ...
```

**User:** "Draft a follow-up for #1"

**Skill drafts:**
> Hi Alex, following up on the workshop outline I sent June 4th. Happy to adjust the structure — just wanted to check if this direction works before booking facilitators. A quick yes/no would help me move forward. Thanks
