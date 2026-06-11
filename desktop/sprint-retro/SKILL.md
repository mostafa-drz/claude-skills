---
name: sprint-retro
description: >-
  Prepares a data-grounded sprint retrospective by pulling the completed
  sprint's shipped tickets, incomplete items, blockers, and cycle-time signals
  from Linear, then framing the What Went Well / What Didn't / What to Try
  structure with actual evidence instead of recollection. Use when preparing a
  sprint retrospective, running a team retro, or when asked what shipped last
  sprint, what stalled, what the velocity was, or what to change next sprint.
---

# Sprint Retro

The retrospective that runs on vague memory produces vague outcomes. This skill
pulls the completed sprint's data from Linear — closed tickets, incomplete
items, blockers, cycle-time outliers — and uses it to frame the classic
What Went Well / What Didn't / What to Try structure with evidence rather
than guesswork. The retro prep that used to take 20–30 minutes of manual
Linear querying takes 30 seconds to trigger.

## Configuration

```
sprint: latest               # "latest" or a specific cycle name / number
team: all                    # team name if the workspace has multiple teams
action_items: 3              # max action items to propose (keep it ≤3)
```

## Process

### 1. Detect Sources

Check what's accessible in this session:

- **Linear** — required (sprint/cycle data, ticket details)
- **Google Calendar** — optional (sprint ceremony dates, unplanned meetings)
- **Gmail** — optional (incident threads, unplanned requests during the sprint)

```
Connected:
  ✅ Linear — sprint data available
  ✅ Google Calendar — ceremony dates
  ⚠️ Gmail — not connected (skipping incident context)
```

If Linear is not connected, explain that this skill requires Linear (Settings →
MCP servers) and stop.

### 2. Identify the Sprint

Determine which cycle to review:

1. Ask Linear for the most recently completed cycle for the team.
2. Confirm with the user: "Reviewing sprint [name], [start]–[end]. Is that right?"
3. If the user names a different sprint, fetch that one instead.

### 3. Pull Sprint Data from Linear

For the identified cycle, gather:

**Completed (Done):**
- Total tickets closed, total story points (if tracked)
- List of completed tickets with title and assignee

**Incomplete:**
- Tickets that were in the cycle but were NOT completed
- For each: days in the cycle, last status update, whether it's blocked

**Blockers and outliers:**
- Tickets that spent >3 days in a single status without moving
- Tickets explicitly marked as blocked

**Velocity signal:**
- Story points completed vs. planned (if point estimates exist)
- Cycle time for completed tickets (if Linear tracks it)

Produce a data snapshot:

```
📊 Sprint data — [Sprint Name], [DD Mon – DD Mon]

Completed (8 tickets):
  ✅ LIN-201 Auth refactor — 3 pts, @alex
  ✅ LIN-203 Dashboard charts — 2 pts, @priya
  ... (6 more)

Incomplete (3 tickets):
  ⚠️ LIN-204 Payment migration — stalled 7 days, last move: In Review
  ⚠️ LIN-207 Onboarding redesign — not started (pulled in mid-sprint)
  ⚠️ LIN-209 Data export — blocked (dependency on LIN-210)

Velocity: 21/28 pts planned (75%)
Cycle-time outlier: LIN-204 spent 7 days in a single status
```

### 4. Gather Context (Optional)

If Google Calendar is connected, pull the sprint window:
- Unplanned events that consumed team time (incidents, all-hands, urgent meetings)
- Whether the retrospective meeting is already on the calendar

If Gmail is connected, scan for the sprint date range:
- Threads with subjects like "incident", "urgent", "hotfix", "outage"
- Flag any that correlated with the stalled or incomplete tickets

### 5. Frame the Retrospective

Organize findings into the three classic retro columns:

```
✅ What Went Well

• Auth refactor shipped cleanly — clear spec, no scope creep
• [from data: 8/11 tickets completed, highest completion rate in 3 sprints]
• Daily standups stayed under 15 minutes (Calendar data)

⚠️ What Didn't

• LIN-204 (Payment migration) stalled 7 days in In Review — no reviewer assigned
• LIN-207 was pulled in mid-sprint without removing anything — added 3 pts to scope
• Dependency on LIN-210 blocked LIN-209; dependency wasn't flagged at planning

💡 What to Try

• For any ticket moving to In Review: assign a reviewer at the time of the move
• "One in, one out" rule: if a ticket is added mid-sprint, one is explicitly deferred
• Surface cross-ticket dependencies during sprint planning, not during the sprint
```

### 6. Propose Action Items

From the "What to Try" list, propose ≤3 concrete, ownable actions for next sprint:

- Specific (not "improve code review" — "assign a reviewer before moving to In Review")
- One owner per action
- Measurable in the next sprint

Ask: "Want me to create these as Linear tickets for next sprint?"
If yes, draft them (show the draft first, don't create without confirmation).

## Guidelines

- **Ground it in data** — every "what didn't" item should reference an actual
  ticket, date, or metric. Don't invent problems.
- **Positive first** — always lead with what went well. Psychological safety
  in retros depends on not starting with the blame list.
- **Max 3 action items** — more than 3 rarely get done. Better to do fewer well.
- **Confirm before creating tickets** — never create Linear issues without
  showing the draft and getting explicit approval.
- **Neutral framing** — attribute problems to process and system, not people.
  "LIN-204 had no reviewer assigned" not "Alex didn't review LIN-204."

## Example

> "Let's prep the retro" or "sprint retrospective" or "what should we cover in the retro?"

1. Fetches latest completed Linear cycle
2. Pulls shipped, incomplete, and blocked tickets + velocity
3. Checks Calendar for context (unplanned events)
4. Produces the three-column retrospective above
5. Proposes ≤3 action items based on observed patterns
6. Offers to create action items as Linear tickets for next sprint
