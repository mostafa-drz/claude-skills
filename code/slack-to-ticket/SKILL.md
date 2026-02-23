---
name: slack-to-ticket
description: >-
  Creates a Linear issue from a pasted Slack thread. Parses the conversation,
  infers title, priority, category, and description, checks for duplicates, and creates a clean ticket.
  Use when pasting a Slack thread to turn it into a trackable issue.
argument-hint: <paste slack thread here>
disable-model-invocation: true
context: fork
allowed-tools:
  - AskUserQuestion
  - mcp__claude_ai_Linear__create_issue
  - mcp__claude_ai_Linear__list_projects
  - mcp__claude_ai_Linear__list_teams
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude_ai_Linear__list_issue_labels
  - mcp__claude_ai_Linear__list_issue_statuses
---

# Slack Thread → Linear Ticket

Creates a structured Linear issue from a pasted Slack conversation.

## Preferences

_Read `~/.claude/skills/slack-to-ticket/preferences.md` using the Read tool. If not found, no preferences are set._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/slack-to-ticket/preferences.md`, confirm, stop
- **anything else** → process as Slack thread

### Help

```
Slack to Ticket — Create a Linear issue from a Slack thread

Usage:
  /slack-to-ticket <paste thread>    Parse and create issue
  /slack-to-ticket config            Set default team, project, preferences
  /slack-to-ticket reset             Clear preferences
  /slack-to-ticket help              This help

What it does:
  1. Parses the thread for topic, urgency, action items
  2. Checks Linear for duplicate issues
  3. Shows inferred fields for review
  4. Asks for team and project
  5. Creates issue with natural description

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Default Linear team?" (options from `list_teams`, max 4, + "Ask each time")
**Q2** — "Default project?" (options from `list_projects`, max 4, + "None", + "Ask each time")
**Q3** — "Default priority when no urgency signals?" (Normal (default), Low, Ask each time)

Save to `~/.claude/skills/slack-to-ticket/preferences.md`.

## First-time detection

If no preferences file exists, show:
"First time using /slack-to-ticket? Run `/slack-to-ticket config` to set default team/project, or continue — I'll ask as needed."

Then proceed normally.

## Steps

### 1. Parse the Slack thread

Analyze `$ARGUMENTS` and extract:
- **Topic**: Core subject being discussed
- **Category**: `Bug`, `Feature`, `Improvement`, or `Task`
- **Action items**: Concrete next steps mentioned or implied
- **Participants**: Names/handles of people involved
- **Reporter**: Who started the thread
- **Urgency**: Map signals (urgent, blocking, ASAP, P0, deadlines) to Linear priority: Urgent (1), High (2), Normal (3), Low (4). Default from preferences or Normal (3).

### 2. Fetch Linear context

In parallel:
- **`list_teams`** — get available teams
- **`list_projects`** — get active projects

Then search for duplicates:
- **`list_issues`** — search with keywords from the parsed topic

If duplicate found, warn the user and let them decide.

### 3. Validate labels

Use **`list_issue_labels`** to check if inferred category label exists. Include only if valid match. If no match, omit.

### 4. Present summary and ask questions

Show inferred fields:

```
Inferred from Slack thread:
- Title: {title}
- Category: {category}
- Priority: {priority} ({reason})
- Action items: {count} found
- Participants: {names}
{if duplicate: ⚠️ Possible duplicate: {issue ID} — {title}}
```

Use a **single `AskUserQuestion`** call to ask:
- **Team**: Which team? (use saved default as first option if set, otherwise options from `list_teams`)
- **Project**: Which project? (use saved default if set)
- **Assignee** (only if someone volunteered): Assign to {name}?

Do NOT ask about title, priority, description, or labels — those are inferred.

### 5. Create the issue

Use **`create_issue`** with:
- **title**: Concise, imperative (e.g., "Fix timeout in data pipeline sync")
- **team**: From user's answer
- **project**: From user's answer (omit if "None")
- **priority**: Inferred priority number (1-4)
- **labels**: Validated label (if found)
- **assignee**: From user's answer (if applicable)
- **state**: Find "Todo" state from `list_issue_statuses`. If not found, omit.
- **description**: Natural ticket description (see guidelines below)

#### Description guidelines

Write like a human engineer wrote it:
1. **Why** — What's the problem and why does it matter?
2. **What** — What needs to happen? (action items as checkboxes)
3. **How** — Only if thread contains agreed approach

Rules:
- No "Context (from Slack)" headers or AI framing
- Don't paste the full conversation
- No participant lists or "Reported by" lines
- Concise and scannable
- If Slack thread link provided, add as reference: `_ref: [Slack thread](url)_`

### 6. Report

Show:
- Issue identifier (e.g., `AIS-123`)
- Direct URL to the issue
- Team, project, priority, labels applied

### 7. Learn

If user chose a team/project different from saved preferences, update silently.
Mention: "Noted: you prefer team {X}. Saved for next time."
