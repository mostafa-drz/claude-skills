---
name: next-steps
description: Generate a stakeholder-aligned next-steps checklist for a multi-stakeholder project from the current conversation and connected context. Use when the user has just had a working session and now needs to align teammates (PM, design, engineering, leadership) on what happens next, who owns it, and what's blocked. Output is grouped by owner, prioritised, and pasteable into Slack/Notion/Linear.
user-invocable: true
arguments: [scope-hint]
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - WebFetch
  - AskUserQuestion
---

# Next Steps — Stakeholder Alignment Checklist

## What it does

Reads the current conversation (and optional connected context: Linear, Slack
thread, Notion doc, git/PR state) and produces **one consolidated checklist of
next steps grouped by owner**, ranked by priority, with explicit dependencies
and open questions. Designed to be pasted into a Slack thread, a Linear
comment, or a Notion update so everyone sees the same picture.

The point isn't to enumerate every possible task — it's to surface what
*unblocks the next move forward*, so multiple stakeholders can self-serve.

## When to use

- After a working session, before posting a status update.
- When a Slack/Linear thread has multiple unresolved threads — you need to
  consolidate.
- When the user says things like *"so what are next steps"*, *"align everyone
  on next items"*, *"summarise what each person owes"*.

Do NOT use this for: timesheet recaps (use `/workday-summary`), retrospective
status posts (use `/project-updates`), or commit-by-commit breakdowns.

## Inputs

Required:
- **The current Claude conversation** — the primary signal. The model already
  has this in context.

Optional (from the `scope-hint` arg or follow-up questions):
- A **Linear ticket ID** (e.g. `ENG-1234`) — fetch via `mcp__linear-server__get_issue` to anchor scope and check current state/assignee.
- A **PR number** (e.g. `#822`) — fetch via `gh pr view` for state, reviewers, blocking checks.
- A **Slack thread permalink** — read via Slack MCP to extract stakeholder asks.
- A **Notion doc URL** — read via WebFetch / Notion MCP for narrative context.

If the conversation already contains these references (it usually does), pull
them automatically. Only ask the user when scope is genuinely ambiguous.

## Workflow

### 1. Anchor the scope
Identify, in one sentence, *what project / piece of work* this is for. Pull it
from the conversation. If multiple candidates exist, ask the user which one.

### 2. Identify stakeholders
List every named person and role that has appeared in the conversation or in
referenced tickets/threads. Mark each as one of:
- **Owner** — has work to do
- **Decider** — owes a call/answer that unblocks others
- **FYI** — needs to know but has no action

Don't invent stakeholders. Use names actually mentioned.

### 3. Extract candidate items
Walk the conversation and any fetched docs. For each item, capture:
- **Action** — concrete, verb-led, ≤ 1 line
- **Owner** — exactly one person
- **Why / context** — one short clause; cite source if non-obvious (PR #, Linear ID, "from Vineet's reply")
- **Priority** — `P0` (blocks demo / today), `P1` (this week), `P2` (next pass)
- **Dependency** — blocked-by note if applicable

Apply ranking ruthlessly: an item that *unblocks another stakeholder* outranks
an item that's purely internal polish.

### 4. Separate open questions
Anything that's a *decision needed* — not a task — goes into a separate
**Open questions** section, attributed to the decider. These are the things
that, once answered, generate concrete tasks. Don't merge them with action items.

### 5. Render

```markdown
# Next steps — {project / scope}

## {Owner name or @handle}
- [ ] **P0** — {action}. _{context, source}_
- [ ] **P1** — {action}. _Blocked on: {dep}_

## {Next owner}
- [ ] **P1** — {action}.

## Open questions
- **{Decider}**: {question}. _Why it matters: {one clause}_

## Out of scope (parking lot)
- {item} — revisit when {trigger}
```

Hard rules:
- **Owner-grouped, not priority-grouped.** A stakeholder skimming for their own
  name should see all their items in one block.
- **Cap at 5 items per owner.** If more, the user is using this skill wrong —
  flag it and ask which to drop.
- **Single-line items.** Detail belongs in the linked source.
- **Never include items already done** unless explicitly asked. This is forward-only.
- **Always include source citations** for non-obvious items (PR #, Linear ID,
  "Vineet on Apr 27", "see Notion guide §3").

### 6. Present and confirm

Show the rendered checklist in chat. Ask:
1. Did I miss anyone?
2. Did I miss any action you mentioned earlier in the session?
3. Anything to bump up/down in priority?

Iterate once, then offer:
- **Copy to clipboard** (`pbcopy`) for Slack/Notion paste
- **Post as Linear comment** on the anchored ticket (only with explicit user
  approval — never auto-post)
- **Save to a file** (e.g. `~/Desktop/next-steps-{slug}.md`) for sharing

## Style

- Direct and operational. *"Wire up Source Linkage un-merge"* — not *"explore
  options for un-merge functionality"*.
- Cite the human, not the AI. *"@Vineet to call IA placement"* not *"per
  conversation, the IA placement question is open"*.
- Match the team's existing project-update voice: pragmatic, product-visible
  outcomes, no engineering minutiae.

## Anti-patterns

- **Don't restate the conversation.** This is a checklist, not a recap.
- **Don't dump every TODO from the codebase.** Only items that map to the
  current scope and a real stakeholder.
- **Don't invent priorities.** If the conversation didn't establish urgency,
  default to P1 and flag *"priority unconfirmed"*.
- **Don't pad sections.** Empty sections (no open questions, no parking lot)
  should be omitted, not filled with "none".
