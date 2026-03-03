---
name: exploration-to-spec
description: >-
  Converts an exploration conversation (architecture discussions, codebase
  analysis, design decisions) into a structured technical specification document.
  Generates a comprehensive but concise product-engineering doc suitable for PMs,
  tech leads, designers, frontend/backend engineers, and QA. Use when you've
  finished exploring and want to formalize decisions into a shareable deliverable.
argument-hint: "[output-path] [--format roadmap|design-doc|adr|rfc] [--audience pm|engineering|all]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
---

# Exploration to Spec

Convert exploration conversations into structured, professional technical documents that satisfy the needs of an entire startup product team — from PM to QA.

## Preferences

_On startup, use the Read tool to load `~/.claude/skills/exploration-to-spec/preferences.md`. If it doesn't exist, use defaults._

## Context

_On startup, use Bash to detect: current git branch, repo name, and working directory. Check if `~/.claude/skills/exploration-to-spec/reference/` exists for templates._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/exploration-to-spec/preferences.md`, confirm, stop
- **output path provided** → use as the file destination
- **empty** → ask where to save

### Help

```
Exploration to Spec — Convert conversations into technical specifications

Usage:
  /exploration-to-spec                                    Interactive (asks for output path)
  /exploration-to-spec ./docs/design.md                   Write to specific path
  /exploration-to-spec --format roadmap                   Use roadmap template
  /exploration-to-spec --format design-doc                Use design document template
  /exploration-to-spec --format adr                       Architecture Decision Record
  /exploration-to-spec --format rfc                       Request for Comments
  /exploration-to-spec --audience pm                      Optimize for product managers
  /exploration-to-spec --audience engineering             Optimize for engineers
  /exploration-to-spec --audience all                     Full cross-functional doc (default)
  /exploration-to-spec config                             Set preferences
  /exploration-to-spec reset                              Clear preferences
  /exploration-to-spec help                               This help

Examples:
  /exploration-to-spec ./technical-docs/insight-engine.md
  /exploration-to-spec --format roadmap --audience all ./docs/roadmap.md
  /exploration-to-spec --format adr                       (asks for output path)

Current preferences:
  (read from preferences.md)
```

### Config

Use `AskUserQuestion`:

**Q1** — "Default document format?" (Roadmap, Design Doc, ADR, RFC)

**Q2** — "Default audience?" (Product — executive summary focus, Engineering — schema/API focus, All — cross-functional)

**Q3** — "Default output directory?" (text input, e.g., `./technical-docs/`)

**Q4** — "Include diagrams style?" (ASCII art — works everywhere, Mermaid — rendered in GitHub/Notion, Both)

Save to `~/.claude/skills/exploration-to-spec/preferences.md`.

### Reset

Delete `~/.claude/skills/exploration-to-spec/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:
"First time using /exploration-to-spec? Run `/exploration-to-spec config` to set defaults, or continue — I'll use sensible defaults."

Then proceed.

## Steps

### 1. Analyze conversation context

Scan the current conversation to extract:

- **Decisions made** — architecture choices, tech stack, patterns chosen
- **Systems explored** — repos, services, APIs, databases analyzed
- **Schemas defined** — data models, table structures, field mappings
- **Diagrams drawn** — system overviews, data flows, component maps
- **Components identified** — what's new vs reuse vs extend
- **Open questions** — unresolved items, decisions deferred
- **Phases/sequencing** — if implementation phases were discussed

Build an internal outline of the key content areas.

### 2. Determine format and audience

If not specified via flags, use preferences. If no preferences, ask via **AskUserQuestion**:

**Q1: Document format**
- Roadmap — phased delivery plan with architecture, schemas, API contracts, UI specs
- Design Doc — deep technical design for a single system/feature
- ADR — Architecture Decision Record (problem, options, decision, consequences)
- RFC — Request for Comments (proposal with alternatives and trade-offs)

**Q2: Primary audience**
- All (cross-functional) — sections for PM, engineering, design, QA
- Product — executive summary, business value, phases, open questions
- Engineering — architecture, schemas, APIs, implementation details

### 3. Determine output path

If provided in `$ARGUMENTS`, use it. Otherwise ask:

> Where should I save this document? (e.g., `./technical-docs/my-spec.md`)

### 4. Generate the document

Apply the selected template structure. Every document must follow these rules:

**Principles:**
- ASCII diagrams (work everywhere — terminals, GitHub, Slack, Notion)
- Tables over prose (scannable, concise)
- Each section works standalone (PM reads 1-2, engineer reads 3-5, designer reads 6)
- No fluff — every line earns its place
- Cross-reference schemas end-to-end (source → storage → API → UI)
- Include component inventory (new vs reuse vs extend)

**Template structures by format:**

#### Roadmap
```
1. Executive Summary          ← PM: what & why in one paragraph
2. Current State              ← Context for anyone new
   2.1 What exists today
   2.2 What was explored/prototyped
   2.3 Gap analysis (table)
3. Architecture               ← Tech leads, engineers
   3.1 System overview (diagram)
   3.2 Data flow (step-by-step)
   3.3 Component inventory (new/reuse/extend table)
   3.4 Storage strategy
4. Schema Design              ← Backend, QA
   4.1 Source → target mappings
   4.2 Table definitions (SQL)
   4.3 Cross-reference table (source → storage → API → UI)
5. API Contracts              ← Backend + frontend
   5.1 Ingest APIs
   5.2 Query APIs
   5.3 Events
6. UI Requirements            ← Design, frontend
   6.1 Component specs with ASCII mockups
   6.2 Field mapping tables
   6.3 Pages & routes
7. Implementation Phases      ← PM, project managers
   Phase N: Goal, tasks table, acceptance criteria
8. Testing Strategy           ← QA
   Per-phase test matrix (type, test, owner)
9. Open Questions             ← Everyone
   Numbered table with impact and status
```

#### Design Doc
```
1. Overview                   ← Problem, goals, non-goals
2. Background                 ← Current state, prior art
3. Architecture               ← System design with diagrams
4. Detailed Design            ← Schemas, APIs, algorithms
5. Alternatives Considered    ← What else was evaluated and why not
6. Cross-cutting Concerns     ← Security, observability, migration
7. Implementation Plan        ← Sequencing, dependencies
8. Open Questions
```

#### ADR
```
# ADR-NNN: [Title]
Status: [Proposed | Accepted | Deprecated]
Date: YYYY-MM-DD

## Context                    ← What situation led to this decision
## Decision                   ← What was decided and why
## Options Considered         ← Alternatives with trade-offs
## Consequences               ← What follows from this decision
## References                 ← Related docs, tickets, conversations
```

#### RFC
```
# RFC: [Title]
Author: [name] | Date: YYYY-MM-DD | Status: Draft

## Summary                    ← One paragraph
## Motivation                 ← Why this change is needed
## Proposal                   ← Detailed design
## Alternatives               ← What else was considered
## Risks & Mitigations        ← What could go wrong
## Rollout Plan               ← How to ship it
## Open Questions             ← What needs resolving
```

### 5. Review and refine

After generating, do a self-review pass:

- Remove any section that's empty or has only placeholder text
- Verify all diagrams are valid ASCII (no broken boxes)
- Ensure cross-reference tables are complete (no "TBD" unless genuinely unresolved)
- Check that every schema field in the UI mockup has a data source
- Verify component inventory covers everything discussed

### 6. Write the file

Write the document to the specified path.

Report:
```
Document written to: [path]
Format: [format]
Audience: [audience]
Sections: [count]
Lines: [count]
```

### 7. Offer follow-ups

Via **AskUserQuestion**:

- "Open in editor" — suggest the user opens the file
- "Generate a summary slide" — create a 5-bullet executive summary
- "Create Linear tickets from phases" — extract tasks into ticket format
- "Done" — finish

### 8. Learn

If the user made corrections:
- Changed the format or structure
- Added/removed sections
- Preferred different diagram style
- Chose a different output path pattern

Save patterns to preferences.

## Principles

- **Conversation is the source of truth** — extract decisions from the discussion, don't invent new ones. If something wasn't discussed, flag it as an open question.
- **Every audience in one doc** — PMs read the summary, engineers read the schemas, designers read the UI specs. One document, multiple entry points.
- **Tables beat paragraphs** — a well-structured table communicates more than three paragraphs. Use tables for mappings, inventories, comparisons, and test matrices.
- **Diagrams are ASCII** — they must render correctly in terminals, GitHub markdown, Slack, and Notion. No external image dependencies.
- **Pragmatic over perfect** — this is a working document, not a thesis. Include enough detail to start implementation, flag gaps as open questions, and move on.
