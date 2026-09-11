---
name: day-timeline
description: >-
  Builds an evidence-based, reference-linked timeline of a single workday by
  merging every connected source — calendar, email, Slack and other chat,
  issue trackers, docs, and Claude Code sessions — into one chronological
  view, rendered as both Markdown and an elegant minimal HTML page. For TODAY
  it also adds status-verified recommendations and a 3-day follow-up scan; for
  PAST days it produces the timeline only. Use when asked what they did today
  or on a given date, for a daily recap, standup prep, or a
  what-happened-in-my-day view.
argument-hint: '[today | yesterday | YYYY-MM-DD]'
metadata:
  side_effects: true
  trigger: "Use when asked what they did today or on a given date, for a daily recap, standup prep, or a what-happened-in-my-day view."
---

# Day Timeline

Reconstruct one workday, hour by hour, from every connected source — grounded in
truth, every entry traceable to its evidence. Output is a Markdown file plus a
self-contained HTML page.

This timeline is **holistic and source-agnostic**. It is not a coding log. A day
is made of meetings, decisions, messages, emails, reviews, writing, research and
errands as much as it is of code. Weight every kind of work equally; let the
evidence — not an assumption about what the user does — decide what fills the day.

## Core principles (do not skip)

1. **Evidence-based, reference-based.** Every timeline entry must trace to a real
   artifact — a calendar event, an email, a chat message, a tracker ticket, a
   doc, a commit or PR, a Claude Code session. Quote verbatim; never paraphrase
   into invention.
2. **One timezone.** Sources disagree: many APIs (email, chat, Claude Code
   sessions) return UTC; calendars usually return local time. Determine the
   user's local zone, convert everything to it before sorting. This is the #1
   source of ordering bugs — get it right.
3. **Snapshots ≠ current state.** Where a session, doc, or thread *ended* is not
   where the work *is*. Before recommending anything, verify live status
   (see Phase 5).
4. **Pull holistically, then reconcile.** No single source is the truth — each
   has gaps another fills. Gather all connected sources, cross-reference,
   reconcile. Do not privilege one tool as the spine of the day.
5. **Recommendations are not only dev work.** A recommended action can be a
   decision, a message, a reply, a review, a nudge, meeting prep, an errand —
   whatever the day actually left open.

## Input

Resolve the argument to one date:
- `today` (default) · `yesterday` · or an explicit `YYYY-MM-DD`.
- **Today vs. past day** decides the output shape:
  - **Today** → timeline + recommendations + follow-ups.
  - **Past day** → timeline only (recommendations and follow-ups are
    forward-looking and only meaningful for the current day).

## Phase 1 — Pull every source for the day

First, take stock of what is actually connected — calendar, email, one or more
chat tools (Slack, Teams, iMessage…), issue/project trackers (Linear, Jira,
Asana…), doc tools (Notion, Google Docs…), Claude Code sessions, local repos.
Then gather, in parallel, all scoped to the target date in the user's local zone.
Adapt to whatever the user has; the table below is illustrative, not a fixed set.

| Source | How | Notes |
|---|---|---|
| Calendar | list events for the date | Already local time. Drop declined events; respect any standing exclusions the user has stated. |
| Email | search threads on the date | Convert UTC → local. Keep substantive threads; drop automated/newsletter/vendor noise. |
| Chat (Slack/Teams/etc.) | search the user's own messages on the date | Search timestamps are often abbreviated — order is reliable, exact clock times may not be. Place by relative order + content correlation, mark `≈`. |
| Issue/project tracker | issues assigned to or touched by the user | For ticket states + what was created/completed/updated that day. |
| Docs | pages authored or edited that day | Notion / Google Docs / etc. |
| Claude Code sessions | filesystem MCP over `~/.claude/projects/` | Read each `.jsonl`'s event `timestamp` fields (UTC). A session is in-scope if any event falls on the target date. Extract start/end, first prompt, summary, artifacts referenced. One source among many — not the backbone. |
| Code hosting | commits / PRs on the date | Direct (GitHub/GitLab MCP) or via the tracker as a proxy. |

If a source is not connected, simply skip it — never invent entries to fill a
gap, and note in "Data notes" which sources were unavailable.

## Phase 2 — Normalize & merge

- Convert all UTC timestamps to the user's local zone. Calendar is already local.
- An item that started before midnight local belongs to the *previous* day —
  surface it as a short "carried in from last night" note, not a main entry.
- Merge all sources into one list, sorted strictly by local clock time.
- Tag every entry by source type (Meeting · Email · Chat · Tracker · Doc · Code
  · Claude Code · etc.). Use a consistent tag set across both outputs.

## Phase 3 — Write the Markdown timeline

- One chronological entry per event with: time (local), source tag, title,
  2–3 sentence description, and its references (event link, ticket ID, PR #,
  doc URL, message permalink, session UUID — whatever applies).
- A short "what today added up to" synthesis paragraph that reflects the *whole*
  day across all kinds of work, not just one category.
- An "Excluded" note (anything the user asked to leave out, automated noise,
  personal detours).
- A "Data notes" note (timezone conversion; approximate times; sources not
  connected or returning nothing).

## Phase 4 — Render the HTML

Self-contained single HTML file, modern-minimal-accessible:
- CSS custom properties; `prefers-color-scheme` dark mode.
- Vertical timeline rail with node dots; one card per entry.
- Distinct color-coding per source type, with a legend.
- Pills for context (ticket, status, branch, attendees) — status colors:
  done/shipped green, in-progress amber.
- Semantic HTML (`main`/`article`/`time`/`ol`), visible focus outlines,
  WCAG-AA contrast, responsive from phone width up.

If the user has a prior `day_timeline_*.html` they liked, match its design.

## Phase 5 — Recommendations (TODAY ONLY)

Skip entirely for past days.

1. Collect candidate next-actions from what the day left open — across *all*
   work types, not just code.
2. **Verify live status before recommending each one** — check the tracker
   ticket state, the latest message on the thread, the PR status, whatever the
   system of record is. A session or thread ending mid-stream is not evidence
   the work stopped. Drop anything already done.
3. Recommend **3** items. For each, give:
   - **Status** (verified, with source + timestamp).
   - **Why it's grounded in the user's goals** — tie to the user's role and
     priorities (read from memory), positions they stated in the day's own
     record, deadline pressure, and the cost of letting it slip. Never generic.
   - Action type may be anything — a decision, a message, a review, dev work,
     meeting prep, an errand.
4. Give a suggested order with reasoning.
5. Add a "watching, not on you yet" note for items gated on others.
6. Stamp the section with what was verified and when, e.g. "Status verified
   against <system of record>, <datetime>".

## Phase 6 — Follow-ups (TODAY ONLY)

Skip for past days. Scan a **rolling 3-day window** (target date minus 2):

- Commitments the user made — "I'll…", "I'll keep you updated", "coming soon",
  "on my list" — in chat or email.
- Threads / mentions / comments awaiting the user's reply.
- Meeting prep for imminent calendar events.

For each: who/what, the verbatim quote, the source + date, suggested action.
Note anything that has since closed itself (don't leave it dangling).

## Output

Write both files to the user's working/project folder:
- `day_timeline_YYYY-MM-DD.md`
- `day_timeline_YYYY-MM-DD.html`

Share `computer://` links. Keep the closing message short.

## Reference

- User profile, role, priorities, collaborators, local timezone, standing
  exclusions: auto-memory (`MEMORY.md` and linked files). Read it first — it is
  what makes the timeline and recommendations specific to this user rather than
  generic.
- Standing rule — verify status + pull holistically before recommending: memory
  `feedback_verify_status_before_recommending.md`.
