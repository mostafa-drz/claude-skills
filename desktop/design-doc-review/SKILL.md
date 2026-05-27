---
name: design-doc-review
description: >-
  Reads and reviews a design document — RFC, ADR, tech spec, PRD, or architecture
  proposal — and produces a structured review brief with prioritized open questions,
  structural gaps, and flagged risks. Applies the right review lens per doc type.
  Use when asked to review a design doc, give feedback on an RFC, prepare for a
  design review meeting, critique an architecture proposal, check what's missing
  in a tech spec, or review a technical document someone shared with you.
---

# Design Doc Review

Reviewing a design doc properly means reading it end to end, tracking down referenced
context across tabs, and writing useful comments from scratch — easily 45 minutes of
context-loading before you get to the actual thinking. This skill reads the document,
classifies its type, and produces a structured review brief: what the doc claims,
questions by priority, structural gaps, and flagged risks.

## Process

1. **Get the document**
   - Accepts a Google Drive link (reads via Drive integration), a URL, or text pasted
     directly into the conversation.
   - If given a Drive link, read the full document content before proceeding.
   - Ask one clarifying question only if the source is ambiguous.

2. **Classify the doc type**
   Identify from the document's own headings and content:
   - **RFC** — proposes a change. Lens: is the change bounded, reversible, and motivated?
   - **ADR** — records a decision. Lens: are alternatives documented and trade-offs recorded?
   - **Tech spec / design doc** — describes how to build something. Lens: is scope clear
     and the implementation path sound?
   - **PRD / product spec** — describes what to build and why. Lens: is the problem clear,
     success measurable, and edge cases covered?

3. **Read fully before commenting**
   Scan every section, including appendices, open questions, and referenced diagrams
   described in the text. Do not comment on the first half only.

4. **Look up referenced context if needed**
   If the doc cites prior decisions, external systems, or standards, do up to two targeted
   web searches to calibrate. More than two is rabbit-holing.

5. **Produce the review brief**

   **Summary** — One paragraph: what the doc proposes, what the author claims is solved,
   and the single most important open issue you see.

   **Questions** — Two tiers, each prefixed with the relevant section:
   - `[MUST ASK]` — the doc can't advance without this being answered. Typical triggers:
     undefined scope, missing failure modes, unaddressed at-least-once/idempotency, no
     rollback plan, security or privacy left open.
   - `[GOOD TO ASK]` — sharpening questions that improve the doc but aren't blockers.

   **Gaps** — Structural absences in the doc, grouped by category. Only list categories
   that genuinely apply to this doc:
   - Observability (metrics, logging, alerting)
   - Rollback / failure recovery
   - Data migration (if applicable)
   - Security and access control
   - Performance under load
   - Dependencies and sequencing

   **Risks** — 3–5 bullets. Each: the risk + why it matters + one mitigation to suggest.

6. **Offer to post as comments**
   After the brief: "Should I post these as comments on the doc, or is this for your notes?"
   - If posting: create one comment per question/gap, anchored to the relevant section.
     Do not dump the full brief as a single comment block.
   - Confirm before posting. A review posted to the wrong doc is hard to recall.

## Guidelines

- Classify first, comment second. A PRD and an RFC need different review lenses.
- Lead the Summary with the biggest concern, not with praise.
- Questions should be answerable. "Have you considered X?" beats "What about X?"
- Gaps are structural absences, not disagreements with the author's choices.
- Don't restate what the doc already says. Every review sentence should be new information.
- If a gap is already addressed in a section you initially missed, silently retract it.
- Don't ask more than 5 must-ask questions. More than that means the doc needs a rewrite,
  not a review — say so instead.

## Example

**Trigger:** "Can you review this design doc? [Drive link]"

**Output shape:**

**Summary**
This RFC proposes migrating the notification service from polling to Cloud Pub/Sub,
claiming an 80% tail-latency reduction. The doc is well scoped, but the biggest gap
is message deduplication — Pub/Sub is at-least-once, and this is never addressed.

**Questions**
[MUST ASK] §3 Delivery: How does the consumer handle duplicate messages? At-least-once
delivery is not acknowledged anywhere in the doc.
[MUST ASK] §5 Rollback: There is no rollback plan described for a migration incident.
[GOOD TO ASK] §2 Alternatives: Why Pub/Sub over Kafka? The trade-off isn't discussed.

**Gaps**
- Observability: No metrics specified for consumer lag or message age.
- Data migration: What happens to already-queued notifications at cutover?

**Risks**
- Fan-out explosion: push may trigger far more downstream writes than polling did.
  Mitigate: load-test with production-scale fan-out before cutover.
- Managed-service dependency: current system is self-hosted; Pub/Sub adds an external
  SLA dependency. Mitigate: add a circuit breaker for Pub/Sub unavailability.
