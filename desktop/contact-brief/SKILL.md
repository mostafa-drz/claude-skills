---
name: contact-brief
description: >-
  Researches a person before you reach out to them — compiling professional
  background, recent work, and any prior Gmail or Calendar history into a
  scannable contact brief. Use when about to send a cold email, message someone
  on LinkedIn, prepare for a first networking call, research someone before an
  interview, or scope a potential partnership or hiring conversation.
---

# Contact Brief

Every meaningful cold outreach needs context you don't have yet. Looking someone up across four browser tabs — web, Gmail, Calendar, LinkedIn — takes 20 minutes and still leaves gaps. This skill consolidates that into one brief.

## Process

### 1. Gather intent

Ask for:
- **Name** of the person (and company/role if known)
- **Purpose**: cold email, networking coffee, interview, partnership, hiring, other
- **Tone**: warm/casual, professional, brief

### 2. Web research — background and recent work

Search for the person by name and company. Extract:
- Current role and company
- Career trajectory (2–3 prior roles)
- Notable recent work: talks, articles, open-source, publications — focus on the last 12 months
- Any public positions or opinions relevant to the outreach purpose

Flag if public presence is sparse — set expectations accordingly.

### 3. Gmail — past interactions

Search Gmail for threads with or about this person. Report:
- Date and subject of the last interaction (if any)
- Any unresolved threads or pending items
- **If none found**: state "No past email history found." explicitly — cold is different from warm.

### 4. Calendar — past meetings

Check Calendar for any past or upcoming meetings with this person. Note them if found; skip this section if nothing surfaces.

### 5. Compile the brief

```
## Contact Brief: [Name]

**Current role**: [Role at Company]
**Web presence**: [LinkedIn URL / personal site / GitHub]

### Background
[2–3 sentences on career trajectory and area of focus]

### Recent work (last 12 months)
- [Article/talk/project title — source, date, link]
- [...]

### Past interactions
[Last email: date, subject — or "No past email or meeting history found."]

### Conversation angles
- [Specific hook tied to their recent work or a shared context]
- [Timing signal or connection point — why now makes sense]

### Suggested opener
[One sentence — a concrete first line grounded in the research, not a template]
```

## Guidelines

- **Research first, draft second.** This skill compiles context. Drafting the full message is a separate step unless explicitly asked.
- **Name cold vs. warm.** Prior history changes the tone completely. State it clearly.
- **Cite sources.** When referencing a recent article or talk, include the title and a link — not just "they wrote about X."
- **No fabrication.** If recent work is sparse, leave that section thin and say so. Gaps are fine.
- **Specific angles beat flattery.** "You wrote about X in March and we hit the same problem" beats "Your work is impressive."
- **One opener, not a full draft.** The suggested opener is one sentence — a hook. The user writes the email.

## Example

**Invocation**: "I want to cold email Sarah Chen at Vercel — she spoke at Next.js Conf about edge caching. Professional but not stiff."

**Output shape**:
```
## Contact Brief: Sarah Chen

**Current role**: Staff Engineer, Vercel
**Web presence**: sarahchen.dev, github.com/sarahc

### Background
Spent 4 years on edge infrastructure, joining Vercel from Cloudflare where
she worked on Workers routing. Writing consistently focuses on tradeoffs
over hype — practitioner angle, not advocate.

### Recent work (last 12 months)
- "Cache invalidation at the edge" — Next.js Conf, Nov 2025 [link]
- "Why stale-while-revalidate isn't enough" — sarahchen.dev, Feb 2026 [link]

### Past interactions
No past email or meeting history found.

### Conversation angles
- Her Nov 2025 talk covers a caching problem my team debugged all of Q4 —
  specific shared problem, not a generic compliment
- She writes from a skeptic's angle — match that register, skip superlatives

### Suggested opener
"Caught your Next.js Conf talk on edge cache invalidation — we hit almost
exactly the stale SWR problem you described in a Q4 migration."
```
