---
name: incident-debrief
description: >-
  Drafts a structured post-incident review (post-mortem) by reconstructing the
  incident timeline from Slack threads, Linear tickets, and GitHub deploys, then
  producing a root-cause analysis, impact summary, and action items. Use when an
  incident, outage, or production bug is resolved, when asked to write a
  post-mortem, when asked "can you help with the incident review?", when
  preparing the timeline for an incident report, or when drafting action items
  after a production issue.
---

# Incident Debrief

After an incident is resolved, the instinct is to close the Slack thread and
move on. The debrief almost always comes later — when the adrenaline is gone and
the details are fading. Reconstructing a timeline from Slack scrollback, a
Linear ticket with a dozen comments, and a deploy log from three different
people's perspectives takes two or three hours if you do it honestly. This skill
does the reconstruction; the analysis falls out of what's already there.

## Process

1. **Confirm the incident.** Ask for:
   - The incident identifier (Linear ticket, Slack thread URL, or a brief
     description like "auth outage at 14:30 UTC June 19")
   - Approximate start and end time, or "still ongoing"
   - The team or service affected

2. **Reconstruct the timeline.**
   - Search Slack for the incident channel or thread. Extract timestamped
     messages: first report, escalation, mitigation actions, resolution.
   - Pull the Linear ticket (if it exists): description, comments, label history,
     status transitions and their timestamps.
   - If GitHub context is accessible, look for emergency deploys, reverts, or
     hotfix PRs merged during the incident window.
   - Sort all events chronologically. Flag gaps where activity is missing.

   Timeline format:
   ```
   14:22 UTC  First user report in #support: "login is broken"
   14:31 UTC  AIS-501 created (P0); assigned to @alice
   14:38 UTC  Root cause identified: null pointer in auth token refresh
   14:45 UTC  Hotfix PR #289 merged to main
   14:52 UTC  Deploy completed; monitoring green
   15:05 UTC  All-clear posted in #incidents
   ```

3. **Identify root cause.** Based on the timeline:
   - What was the proximate cause (the direct failure)?
   - What was the contributing cause (the condition that made it possible)?
   - If the timeline doesn't answer this definitively, say so — a post-mortem
     with an honest "root cause unclear, needs follow-up" is better than a
     confident wrong answer.

4. **Assess impact.** Summarize:
   - Duration of impact window
   - Which users/services were affected and how
   - Any data loss, security implications, or SLA breach
   - Derive from the timeline; don't guess

5. **Draft the post-mortem** in standard structure:

   ```
   ## Incident: <Title>
   **Date:** YYYY-MM-DD  **Duration:** Xh Ym  **Severity:** P0/P1/P2

   ### Summary
   One paragraph: what happened, who was affected, how it was resolved.

   ### Timeline
   [Reconstructed from Step 2]

   ### Root Cause
   Proximate: …
   Contributing: …

   ### Impact
   - Users: …
   - Services: …
   - SLA: …

   ### Action Items
   | # | Action | Owner | Due |
   |---|--------|-------|-----|
   | 1 | Add null check to token refresh path | eng | YYYY-MM-DD |
   | 2 | Add alert for auth error rate > 1% | infra | YYYY-MM-DD |
   ```

6. **Ask about destination** before finalizing:
   - **Notion** — structured page ready to paste
   - **Linear** — comment on the incident ticket
   - **Confluence / Google Doc** — markdown export
   - **Slack** — condensed summary for the incident channel

7. **Show the draft. Wait for review.** The post-mortem is a team document.
   Never post or share automatically.

## Guidelines

- **Blameless by default.** Describe system and process failures, not individual
  failures. "The deploy pipeline skipped the staging gate" not "Alice didn't
  test in staging."
- **Timeline before analysis.** Get the facts right before drawing conclusions.
  Don't let the narrative shape the timeline; let the timeline shape the narrative.
- **Honest gaps.** If the Slack thread is incomplete or the ticket has no
  comments, say what's missing. Don't fill gaps with assumptions.
- **Action items must be specific.** "Improve monitoring" is not an action item.
  "Add a PagerDuty alert when auth error rate exceeds 1% for 5 minutes" is.
- **Severity from impact, not drama.** Use the team's existing severity definitions
  if known. Don't upgrade severity to make the post-mortem feel more serious.
- **Confirm scope before pulling.** Incidents can span multiple Slack threads and
  tickets. Confirm which channels/tickets to include before searching.

## Example

**User:** "Help me write the post-mortem for the login outage yesterday — it was
in #incidents and ticket AIS-501."

**Skill output (excerpt):**

```
## Incident: Auth Token Refresh Null Pointer
**Date:** 2026-06-19  **Duration:** 43m  **Severity:** P1

### Summary
A null pointer exception in the token refresh path caused login failures for
users with expired sessions. Approximately 12% of active users were unable to
log in between 14:22 and 15:05 UTC. Root cause was a missing null check
introduced in PR #284 (merged 2026-06-18). Resolved by reverting to the prior
token handler in a hotfix deploy.

### Timeline
14:22 UTC  First report in #support: "can't log in, getting 500"
14:28 UTC  @on-call confirmed: auth service error rate 18%, spiking
14:31 UTC  AIS-501 created (P1); @alice begins investigation
14:38 UTC  Root identified: null ref in token_refresh() added in PR #284
14:43 UTC  PR #289 (revert of #284) opened and approved
14:45 UTC  Hotfix merged to main; deploy initiated
14:52 UTC  Deploy complete; error rate back to baseline
15:05 UTC  All-clear confirmed; AIS-501 moved to Done

### Root Cause
Proximate: `token_refresh()` threw NullPointerException when `refresh_token`
field was absent (valid for users who signed in via OAuth before June 10).
Contributing: PR #284 changed the token handling logic without a null guard
and the staging environment had no OAuth-authenticated test accounts, so the
path was untested before merge.

### Action Items
| # | Action | Owner | Due |
|---|--------|-------|-----|
| 1 | Add null guard to token_refresh() | @alice | 2026-06-21 |
| 2 | Add OAuth test account to staging fixtures | @bob | 2026-06-24 |
| 3 | Alert when auth error rate exceeds 1% for 3m | @infra | 2026-06-28 |
```
