---
name: decision-brief
description: >-
  Researches the options in a significant decision and produces a structured
  one-page brief with a recommendation. Applies a lightweight criteria-based
  framework, pulls relevant Drive docs and Gmail threads for context, and
  surfaces tradeoffs instead of leaving you to hold them in your head.
  Use when choosing between job offers, vendors, tools, architectural approaches,
  or any decision where the options deserve honest comparison rather than gut
  feeling — especially when you need to explain the reasoning to someone else.
---

# Decision Brief

Significant choices rarely fail because of missing information. They fail because
the information is scattered across five browser tabs and never organized against
clear criteria. This skill gathers what you already have (Drive, Gmail) and what
you don't yet know (web research), applies a simple criteria-weighted comparison,
and produces a one-page brief you can think with — or share for a second opinion.

## Process

### 1. Frame the Decision

Ask:
- What are you deciding? (1 sentence)
- What are the options? (2–5; names or brief descriptions)
- When do you need to decide?
- What matters most to you? (up to 5 criteria — e.g., cost, risk, speed,
  reversibility, team fit, long-term upside)

If the user gives vague criteria ("I just want the best one"), prompt with
examples: cost, time, risk, reversibility, team/culture fit, long-term viability.

Accept partial answers. Don't block on gaps — note them and proceed.

### 2. Establish Criteria Weights

Confirm the relative importance of each criterion:
```
Criteria:
  Long-term upside .... high
  Learning ............ high
  Stability ........... medium
  Short-term comp ..... low
```

If the user says "use your judgment," apply reasonable defaults and show them.

### 3. Research Each Option

For each option, run web searches to find:
- Current reputation, known tradeoffs, practitioner reviews
- Pricing or cost signals (where relevant and available)
- Known failure modes or "gotchas" from independent sources
- Recent news: funding, EOL announcements, major changes

Use only Tier 1–3 sources (official docs, named practitioners, established
publications). Reject vendor marketing pages and SEO content farms.

If an option is internal or proprietary (e.g., "our current vendor," "Option A
is staying in my current role"), skip web search for it and rely on the user's
context alone.

### 4. Pull Personal Context

If Google Drive is connected, search for docs related to the decision topic:
contracts, requirements, prior evaluation notes, existing commitments.

If Gmail is connected, search for threads mentioning the options or the decision
subject: prior negotiations, offers, recommendations from people you trust.

List what was found with 1-line descriptions. Note explicitly if nothing turned up.

### 5. Score the Options

Build a simple comparison matrix. Score each option per criterion, 1–5:

```
                  Long-term   Learning   Stability   Short-term
                   upside                              comp
Option A (startup)    5          4           2           3      → 4.3
Option B (big co)     3          3           5           4      → 3.5
```

Show which weights were applied. Be transparent about any judgment calls in scoring.

### 6. Write the Brief

```markdown
## Decision Brief — [Title]
Prepared: [date] | Deadline: [date or "flexible"]

### Situation
[1–2 sentences on what's being decided and why it matters now]

### Options
- **[Option A]**: [1-line description]
- **[Option B]**: [1-line description]

### Criteria & Weights
[List from Step 2]

### Comparison
[Scoring matrix from Step 5]

### Key Tradeoffs
- [Most important tension between top options]
- [Second tradeoff worth naming]

### Recommendation
**[Option X]** — [2-sentence rationale tied directly to the top-weighted criteria].

One honest caveat: [the strongest argument for the other option, or the one
piece of information that would change this recommendation]

### Sources & Context
[Web sources used, Drive docs found, Gmail threads referenced — or "none found"]
```

Then ask: "Want to dig deeper on any option, adjust the criteria weights, or
draft a message to explain this decision to someone else?"

## Guidelines

- **Show the matrix.** A recommendation without visible reasoning is an opinion.
  The criteria scores make the call auditable and changeable.
- **Surface the anti-recommendation.** One honest caveat is required — the
  strongest argument against the recommended option. Decisions that skip
  dissent usually skip thought.
- **Never fabricate research.** If web search doesn't surface practitioner-level
  data for an option, say "limited independent data found" — don't invent reviews.
- **Respect stated weights.** If the user said cost matters most, the
  recommendation must account for it or explicitly explain why it didn't prevail.
- **Detect, don't assume tools.** Only reference Drive and Gmail sections when
  those integrations are actually connected. Note any that are missing.

## Example

**User:** "Two job offers. Startup (Series B): great equity, uncertain, more
learning. Big tech: stable, lower equity. I care most about long-term earnings
and learning."

**Output:** A brief comparing both on upside, learning environment, risk, and
stability — with web research on each company's trajectory, a matrix weighted
to the user's priorities, and a clear recommendation with one honest caveat
(what information would flip the call).
