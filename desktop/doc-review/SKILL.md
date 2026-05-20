---
name: doc-review
description: >-
  Reviews a Google Doc, pasted spec, proposal, or memo before it gets shared
  — surfaces missing context, unstated assumptions, unclear decisions, and
  gaps a first reader would hit. Produces categorized feedback with specific
  quotes and a concise fix-list. Use when preparing to share a doc, asking
  "is this ready to send?", wanting a second opinion on a spec, reviewing a
  proposal before a meeting, or checking if a memo is clear before it goes to
  stakeholders.
---

# Doc Review

Reads a document — from Drive, a shared link, or pasted text — then applies a structured critique: unclear purpose, missing context, unstated assumptions, decisions presented without rationale, and action items without owners. Produces targeted feedback organized by category rather than line-by-line rewrites. Best suited for working documents: specs, proposals, memos, briefs, and roadmaps. Not a grammar checker.

## Process

### 1. Locate the Document

Ask the user for the document:

> Share the doc — paste the text, drop a Drive link, or describe it and I'll search Drive.

If the user pastes text: read it as-is.

If the user shares a Drive URL or says "it's in Drive": open and read the document.

If the user describes a document ("the Q3 roadmap I wrote"): search Drive for a recent match, show the top result for confirmation before reading.

If nothing is found, ask the user to paste the content directly.

### 2. Identify Document Type and Audience

Before reviewing, establish context:

- **Type**: technical spec / proposal / memo / meeting brief / roadmap / other?
- **Audience**: who is the intended reader — engineers, executives, customers, a specific person?
- **Goal**: what should a reader do or decide after reading this?

Ask if not obvious from the document itself. Do not guess silently.

### 3. Apply the Review Lens

Review the document against six categories. For each, quote specific text where an issue exists.

**Purpose and scope**
- Is the goal stated in the first paragraph?
- Is the scope clear — what's in and what's out?
- Would a reader know what to do with this document after reading it?

**Assumptions**
- What does this assume the reader already knows?
- Which assumptions are unstated but required to follow the argument?
- Are any assumptions likely to be contested?

**Decision transparency**
- Are decisions explained (not just stated)?
- Where choices were made, is the reasoning present? Or only the conclusion?

**Gap detection**
- What questions will a reader have that the document doesn't answer?
- Are any sections referenced that don't exist yet?
- Is critical information promised but not delivered?

**Action clarity**
- Are next steps present?
- Does each action have a clear owner?
- Are timelines or milestones stated or implied?

**Structure and readability**
- Does the document flow logically?
- Are the section headers representative of what's in each section?
- Is any section doing two unrelated jobs?

### 4. Build the Feedback Report

Organize findings into three tiers:

**🔴 Must-address before sharing**
Issues that will confuse or block a reader: missing goal, undefined terms the audience won't know, decisions with no rationale, actions with no owner.

**🟡 Worth fixing**
Things that will generate questions or slow reading: implicit assumptions, thin sections, unclear scope boundaries, inconsistent terminology.

**🟢 Optional polish**
Structural improvements, flow suggestions, redundant sections — worth considering but not blocking.

For each item, show:
```
Category: [category]
Issue: [one sentence]
Where: "[quoted text from the document]"
Suggestion: [one concrete fix]
```

End with a short verdict:
```
Ready to share? [Yes / Yes, with minor fixes / No — address the 🔴 items first]
```

### 5. Offer to Apply Fixes

After delivering the report, ask:

> Want me to draft fixes for any of these, or suggest a revised version of a specific section?

If yes: produce a suggested rewrite for the requested section only. Do not rewrite the whole document unsolicited.

## Guidelines

- **Quote, don't paraphrase** — when citing an issue, use the actual text from the document. Paraphrasing is imprecise.
- **Categorize, don't dump** — a long list of issues is harder to act on than a tiered report. Keep the 🔴 list short and defensible.
- **Don't rewrite unless asked** — the review job is to surface problems, not to replace the author's voice. Only produce rewrites if explicitly requested.
- **Respect the doc type** — a quick internal memo doesn't need the same treatment as a customer-facing proposal. Calibrate expectations to the stated audience and goal.
- **No style pedantry** — skip comma placement, sentence length preferences, and stylistic opinions unless they materially affect clarity. Focus on what a reader would need, not what reads elegantly.
- **Graceful degradation** — if Drive isn't connected or the doc can't be read, ask the user to paste the content rather than stopping.

## Example

**User:** "Review my spec before I share it with the team — Drive link: [link]"

**Doc type:** Technical spec — new API endpoint design, audience: backend engineers

**Review output:**
```
🔴 Must-address (2)
  Purpose and scope
    Issue: Goal is not stated in the opening.
    Where: "This document describes the /events endpoint."
    Suggestion: Add one sentence before this: what problem does the endpoint solve, and who will call it?

  Action clarity
    Issue: Migration path has no owner or timeline.
    Where: "Existing clients will need to be updated."
    Suggestion: Specify who owns the migration and the expected completion date.

🟡 Worth fixing (1)
  Decision transparency
    Issue: Pagination strategy is stated without rationale.
    Where: "We will use cursor-based pagination."
    Suggestion: Add one sentence on why cursor over offset — schema compatibility, performance, etc.

🟢 Optional polish (1)
  Structure: Section 3 (Error Codes) and Section 4 (Rate Limiting) are both about failure behavior.
  Suggestion: Consider merging into a single "Failure Behavior" section for a cleaner read.

Ready to share? Yes, with minor fixes — address the 2 🔴 items first.
```
