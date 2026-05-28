---
name: sprint-planner
description: >-
  Prepares a suggested sprint scope by pulling prioritized backlog issues from
  Linear, computing capacity from team Calendar availability, and proposing what
  to commit to this sprint — with carry-over, blocker flags, and a risk summary.
  Use when starting sprint planning, grooming the backlog before a cycle kickoff,
  entering a planning meeting, or asked "what should we commit to this sprint?"
---

# Sprint Planner

Sprint planning without prep means starting the meeting with the full backlog open and negotiating live — which takes 90 minutes and ends with scope that wasn't really thought through. This skill does the prep: pulls the backlog, checks who's actually available, and hands you a capacity-adjusted scope proposal to walk in with.

## Configuration

```
sprint_duration: 2w          # "1w", "2w", or explicit dates "YYYY-MM-DD:YYYY-MM-DD"
velocity_buffer: 0.8         # fraction of capacity to commit (0.0–1.0); 0.8 = plan to 80%
team_members: []             # Linear usernames; empty = just the current user
include_wip: true            # include In Progress issues as carry-over
```

## Process

### 1. Confirm the sprint window

Ask or infer:
- If the user specifies dates or a cycle name, use those
- If not, default to the next full workweek (1w) or next two weeks (2w)

State the dates before pulling any data: "Planning sprint May 26 – Jun 6."

### 2. Pull from Linear

Fetch issues assigned to team members (or the current user if `team_members` is empty):

**Carry-over** — issues currently In Progress or that weren't completed in the last cycle. These are non-negotiable inclusions.

**Backlog candidates** — issues in Backlog or Todo status, sorted by priority. For each:
- ID, title, estimate (story points or t-shirt), project/cycle, assignee
- Flag any with active blockers

**Last cycle velocity** — if Linear provides it, note the average points completed per sprint (used to calibrate the capacity calculation).

```
Carry-over (N issues):
  🔄 [ENG-ID] title — N pts — @assignee

Backlog (N candidates, by priority):
  🟥 [ENG-ID] title — N pts — [project] — @assignee
  🟧 [ENG-ID] title — N pts — [project]
  🟨 ...
```

### 3. Check team availability

For each team member, pull Calendar events in the sprint window:

- **OOO / time-off** — all-day events containing "OOO", "vacation", "leave", "off", "holiday"
- **Heavy meeting days** — days with >4h of scheduled meetings (reduces focus capacity by 0.5 days)
- **Available focus-days** = sprint workdays − OOO days − (heavy-meeting days × 0.5)

```
Availability:
  @alice: 10/10 days (100%)
  @bob:    6/10 days (OOO Mon–Wed wk1)
  @carol:  9/10 days (1 heavy-meeting day)
  Team total: 25 focus-days
```

### 4. Compute capacity

```
Capacity:
  Team focus-days: 25
  Buffer (80%): 20 effective days
  Historical velocity: ~N pts/sprint (from last cycle, if available)
  Estimated throughput: ~N pts
```

If issues have no story point estimates, skip the throughput math and present a priority-ranked list instead. Never fabricate a number.

### 5. Propose the sprint scope

Fill capacity in this order:

1. All carry-over (In Progress) first — always included
2. Backlog candidates by priority until capacity is reached
3. Reserve 15% of effective capacity for unplanned work (bugs, urgent requests)
4. Flag ⚠️ any included issue with a known blocker

```
Proposed Sprint Scope (N pts / 20 days):

🔄 Carry-over (N pts):
  [ENG-148] API rate-limit docs — 5 pts — @alice ⚠️ blocked: design spec pending

📋 New scope (N pts):
  [ENG-171] Notification settings — 8 pts — @carol
  [ENG-172] Password reset flow — 5 pts — @alice
  [ENG-175] Search autocomplete — 8 pts — @bob

📦 Next in backlog (not included):
  [ENG-180] Export to CSV — 5 pts
  [ENG-182] Dark mode — 8 pts
```

### 6. Surface risks

Before the team commits, flag:

- Blocked issues in proposed scope — list the blocker and suggest resolving before sprint start
- Any team member at <60% availability with more than one issue assigned
- Any single issue larger than 3 days of work (split risk — suggest breaking it down)
- More than 30% of scope concentrated on one person

## Guidelines

- **Estimates or no math** — if issues have no story points, present a priority-ranked list without capacity numbers. Don't fabricate throughput.
- **80% buffer is real** — plan to 80% of capacity so the team can absorb unplanned work without slipping. Don't recommend filling higher than 0.9.
- **Blockers are load-bearing** — if a blocker is unresolved before the sprint, those points are theoretical. Surface it prominently; don't quietly include.
- **Carry-over is mandatory** — in-progress work carries to the next sprint regardless of capacity. Account for it first.
- **This is a proposal, not a commitment** — make that explicit at the top of the output. The team owns the final scope decision.
- **Calendar is a hint** — OOO data may lag reality. Present availability as an estimate.

## Example

**Invocation:** "Help me plan the sprint" or "What should we commit to this sprint?"

**Output shape:**

```
📅 Sprint Planning Prep — May 26–Jun 6
Team: @alice, @bob, @carol
Sources: Linear ✅  Calendar ✅

Availability: 25 focus-days → 20 effective (80% buffer)
Historical velocity: ~40 pts/sprint

🔄 Carry-over (8 pts):
  [ENG-148] API rate-limit docs — 5 pts — @alice ⚠️ blocked: design spec pending
  [ENG-163] Login redirect fix — 3 pts — @bob

📋 New scope (32 pts):
  [ENG-171] Notification settings — 8 pts — @carol
  [ENG-172] Password reset flow — 5 pts — @alice
  [ENG-175] Search autocomplete — 8 pts — @bob
  [ENG-178] Onboarding flow polish — 5 pts — @carol
  [ENG-179] Error state redesign — 6 pts — @alice

📦 Left in backlog:
  [ENG-180] Export to CSV — 5 pts
  [ENG-182] Dark mode — 8 pts

⚠️ Risks:
  • ENG-148 has an active blocker — resolve or descope before committing
  • @bob is OOO Mon–Wed wk1 (60% available) with 11 pts assigned — consider rebalancing

This is a proposal. Bring it to the planning meeting to validate estimates and confirm scope.
```
