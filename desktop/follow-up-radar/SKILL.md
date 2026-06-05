---
name: follow-up-radar
description: >-
  Scans Gmail sent mail to surface threads awaiting a reply — emails you sent
  where the last message is yours and no response has arrived. Groups results by
  wait time, drafts a concise follow-up for each, and presents a report before
  anything is sent. Use when you haven't heard back and want to follow up, when
  you feel like something fell through the cracks, when auditing unanswered
  outreach, or when doing an end-of-week email review.
---

# Follow-Up Radar

Every few weeks the same thing happens: a decision stalls because someone never replied, or an action item slips because a sent email got buried. Follow-Up Radar scans Gmail sent mail, identifies threads where you're still the last sender, and drafts short follow-ups — grouped by how long they've been waiting, ready to review before anything goes out.

## Configuration

```
lookback_days: 14       # How far back to scan sent mail (default: 14 days)
stale_threshold_days: 5 # Minimum age before a thread is surfaced (default: 5 days)
max_threads: 40         # Maximum sent threads to review in one run
```

## Process

1. **Search sent mail** — Search Gmail with `in:sent` restricted to the lookback window. Retrieve threads sorted by date, oldest first. Stop after `max_threads` threads.

2. **Identify unanswered threads** — For each thread, check whether the most recent message was sent by you. If anyone else replied after your last message, the thread is answered — skip it. If your message is still the last one and it is older than `stale_threshold_days`, mark it as **waiting**.

3. **Filter noise** — Skip threads that look like one-way sends with no expected reply:
   - Subject starts with "Invitation:", "Receipt:", "Your order", "Confirmation", "Unsubscribe"
   - The sole recipient is a `noreply@` or `no-reply@` address
   - You are the only participant in the thread (sent-to-self)
   - The original message contained calendar attachments only

4. **Group by age**:
   - **Overdue** (> 7 days old): likely forgotten — surface first
   - **Due** (5–7 days old): worth a nudge — surface second

5. **Draft a follow-up for each** — Read the subject line and up to the first 100 words of your last sent message in the thread. Draft a 2–3 sentence follow-up that:
   - References the original ask in plain language — no quoted blocks, no "As per my previous email"
   - Is direct but not pressuring: "Just checking in", "Happy to answer questions if helpful"
   - Matches the tone of the original (formal vs. casual)
   - Includes your name sign-off if the original had one

6. **Present the report** — Show results grouped by bucket:

   ```
   Found 4 threads waiting (scanned 2026-05-22 → 2026-06-05)

   OVERDUE (> 7 days)
   1. "Q3 roadmap sync — agenda" → alice@example.com — sent 11 days ago
      Draft: "Hi Alice, just checking in on the roadmap sync agenda — happy to adjust if timing is tight."

   2. "Invoice #4821 — payment terms" → billing@vendor.com — sent 9 days ago
      Draft: "Following up on invoice #4821 — wanted to confirm receipt and check if anything is needed."

   DUE (5–7 days)
   3. "Intro: Mostafa ↔ Jordan" → jordan@example.com — sent 6 days ago
      Draft: "Hi Jordan, circling back on the intro — let me know if you'd like to connect."

   Which would you like to send? (e.g. "Send 1 and 3", "Send all overdue", "Edit 2 then send")
   ```

7. **Send on approval** — For each approved follow-up, reply to the original Gmail thread. Confirm before sending each one individually or confirm once before sending a named group. After sending: "Sent 2 of 4 follow-ups."

## Guidelines

- **Never send without explicit approval.** Always show the draft and wait for a decision. Do not assume silence means "go ahead."
- **One follow-up per thread per run.** If the thread already has a follow-up you sent within the lookback window, skip it — you've already nudged once.
- **Respect one-way sends.** If the original email closed with "no need to reply" or was a pure announcement, skip the thread without surfacing it.
- **Preserve tone.** If the original was terse and professional, the follow-up should be terse and professional. If it was warm, match that.
- **When ambiguous, surface with a note.** If it's unclear whether a reply is expected (e.g. a long cc'd thread), include the thread in the report but flag it: "Unsure if reply expected — review before sending."
- **Overdue bucket first.** If the user only has time for a few, start with overdue threads — those are the ones most likely to have real consequences.

## Example

**Invocation:** "Check my follow-ups from the last two weeks"

**What happens:** Claude searches Gmail sent mail from 2026-05-22 to 2026-06-05, finds 18 sent threads, filters out 14 (answered, noise, calendar-only), and surfaces 4 waiting threads. It groups them into overdue (2) and due (2), drafts a short follow-up for each, and presents the report. The user says "Send 1 and 3, skip the rest." Claude replies to threads 1 and 3 and confirms: "Sent 2 follow-ups. Threads 2 and 4 untouched."
