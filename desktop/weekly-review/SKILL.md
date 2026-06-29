---
name: weekly-review
description: >-
  Pulls this week's Calendar events, Gmail threads, and any connected
  integrations into a structured retrospective. Synthesizes what shipped,
  what slipped, and what patterns emerged across the week, then produces a
  forward-look for next week. Use when doing a weekly review, end-of-week
  reflection, GTD weekly review, Friday retrospective, weekly planning, or
  when asked to recap the week or prepare for the week ahead.
---

# Weekly Review

Every week ends with the same scattered ritual: open Calendar and scroll through five days of events, switch to Gmail and hunt for threads that needed a reply, vaguely remember a conversation from Tuesday that changed something important, and try to hold all of it in working memory long enough to make a plan. This skill pulls those threads together automatically — sources, synthesizes, and hands back a clean retrospective plus one forward focus.

## Configuration

```
week: current                # "current" or ISO date of any Monday (YYYY-MM-DD)
sources: all                 # "all" or comma-separated: calendar, gmail, slack
reply_tone: direct           # direct, reflective, casual
save_to_drive: false         # true = save the output as a dated Google Doc
```

## Process

### 1. Detect Available Sources

Check what integrations are accessible in this session:

```
Connected sources:
  ✅ Google Calendar — via Google Workspace
  ✅ Gmail — via Google Workspace
  ✅ Slack — via MCP server
  ❌ Linear — not connected
```

If no Calendar or Gmail is connected: explain what's needed and stop. Don't fabricate events or messages.

### 2. Clarify the Week

Default to the most recently completed work week (Mon–Fri). If today is Monday or Tuesday, default to last week. Otherwise default to the current week through today.

Ask once, briefly:

> Reviewing **[Mon DD – Fri DD]** — or specify a different week?

Accept "yes", "go", or a specific date range. Don't ask further.

### 3. Gather Data

For the target week, collect in parallel:

**Google Calendar:**
- All events where the user was organizer or attendee
- Skip declined events, all-day administrative blocks (OOO, holidays), and 1-person focus blocks

**Gmail:**
- Threads where the user is in To: (not just CC:) sent or received this week
- Threads with recent replies from the user
- Ignore newsletters, automated notifications, and mailing lists

**Slack (if connected):**
- DMs the user sent or received
- Threads the user replied to or was mentioned in

Note: be transparent about what was found. "Scanned 47 calendar events, 23 Gmail threads" builds trust.

### 4. Synthesize the Week

Organize findings into four lenses. Be specific — name real events, real senders, real topics:

**📦 Shipped**
Concrete things completed: meetings that produced a decision, tasks finished, documents sent, responses given. Use active past tense: "Closed the API contract with Jordan", "Shipped the nav redesign PR", "Finalized Q3 roadmap draft."

**🔁 Slipped**
Things that didn't happen. Distinguish clearly:
- *Slipped by choice* — deprioritized knowingly
- *Blocked* — waiting on someone else
- *Dropped* — quietly fell off the list

**💬 Key Conversations**
2–4 threads or meetings that shaped the week — decisions made, context shared, alignment achieved. Not a message log; only what matters.

**🔍 Patterns**
One or two observations that cut across the week. Examples: "Three meetings that could have been emails", "Reactive most of Tuesday and Wednesday", "Async decisions are working faster than sync ones right now." Only write this if something genuine emerges — skip the section if nothing does.

### 5. Forward Look

Produce three concrete items for next week. Each item should be:
- Specific enough to act on ("Follow up with Jordan on contract signature" not "deal with contracts")
- Owned by the user, not blocked on others
- Sequenced — if item 3 depends on item 1, say so

Then surface one open question:

> ❓ **Open question to resolve:** [One decision, ambiguity, or unclear owner that will shape next week if left open]

### 6. Present and Save

Show the full retrospective. Then ask:

> Save this as a Google Doc for your records? (yes / no)

If yes, create a dated Doc titled `Weekly Review — Week of [Mon DD, YYYY]` in Drive root (or a folder named "Weekly Reviews" if it already exists). Include the full retrospective text.

## Guidelines

- **Specific beats comprehensive.** Three real observations beat ten vague ones. If the data doesn't yield a genuine pattern, don't invent one.
- **Distinguish slipped-by-choice from blocked.** This matters for accountability. If it was blocked, say who or what is blocking.
- **One forward question is the most valuable output.** The retrospective is context; the open question is what actually unsticks the next week.
- **Privacy-aware.** If the user might be on a shared screen, avoid quoting sensitive message content verbatim — paraphrase instead.
- **Don't ask more than one clarifying question.** Gather what's available, note gaps, proceed.
- **Graceful degradation.** If Gmail returns no results, continue with Calendar data. Note the gap.

## Example

**User:** "Do my weekly review"

**Output:**

```
📅 Weekly Review — Mon Jun 23 – Fri Jun 27 2026
Scanned: 34 calendar events · 41 Gmail threads · 28 Slack threads

📦 Shipped
• Closed auth redesign PR (merged Thursday)
• Shipped Q2 analytics report to stakeholders
• Resolved the CORS issue blocking the mobile team
• Had a productive 1:1 with Priya; aligned on roadmap priorities

🔁 Slipped
• [Blocked] Updated deployment docs — waiting on DevOps to confirm new env vars
• [Slipped by choice] Dependency audit deferred to next sprint
• [Dropped] Slack thread with Alex from Tuesday — needs a reply

💬 Key Conversations
• Tuesday: Roadmap session → decided to push native auth to Q4
• Wednesday: Sync with Jordan confirmed API contract going ahead
• Friday: Incident retro surfaced a gap in our on-call rotation

🔍 Patterns
Three of this week's blockers came from missing context at handoff — not wrong decisions, just undocumented ones.

🗓️ Next Week
1. Write up the auth redesign decision doc before it gets fuzzy (blocks the Q4 planning)
2. Reply to Alex about the Slack thread and close the loop
3. Follow up with DevOps on deployment env vars (unblocks docs)

❓ Open question: Who owns on-call rotation coverage after Sam's departure?
```
