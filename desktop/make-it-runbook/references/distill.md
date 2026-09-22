# Distilling a conversation into a runbook

The page is the easy half. This is the half that decides whether the runbook is right. A
setup conversation is a draft written in public: advice gets corrected, values change, the
order it was discussed in isn't the order it's done in, and tangents sit in the middle.
The runbook holds **the final agreed state only, in true execution order, with forced
waits where they actually block**.

## Contents
- 1. Read everything, then build a ledger
- 2. Resolve: the last agreed word wins
- 3. Order by execution, not by conversation
- 4. Find the waits
- 5. Steps, notes, or neither
- 6. Literal values
- 7. Unresolved: ask or flag, never guess
- 8. Phases
- 9. Self-check before writing JSON

## 1. Read everything, then build a ledger

Read the **whole** conversation before writing anything, including the messages after the
point where the plan first looked finished. Corrections come late.

List every instruction, value and constraint as a ledger line, with the turn it came from:

```
T1  add domain as user alias domain          → superseded by T5
T3  DMARC v=DMARC1; p=reject; ...            → superseded by T7
T4  DNSSEC off before switching nameservers   ✓
T5  add both as SECONDARY domains             ✓ (corrects T1)
T5  MX: Type MX Name @ Server ... Priority 1  ✓ literal
T5  DKIM blocked 24–72 h after Gmail activation   wait
T9  booking pages need Business Standard+     note
T10 mirror domain "decide later"              unresolved
T2  logo colours                               tangent, drop
```

The ledger is scratch work: don't show it unless the user asks how you got there.

## 2. Resolve: the last agreed word wins

- **A correction replaces, it doesn't add.** When advice changes ("actually, do Y"), only
  Y survives. X appears nowhere, not even as "don't do X", unless the conversation made
  avoiding X a real risk worth a note (then one note, and Y is still the step).
- **A changed value replaces the old one everywhere**, including inside other steps that
  quoted it.
- **The user's choice beats the assistant's suggestion.** If the user said "I'll use the
  other host", the runbook uses the other host, even when the assistant argued for its
  own.
- **"Agreed" means the user accepted it or didn't push back.** Something the assistant
  floated that the user rejected or ignored in favour of another option isn't agreed.
- **Don't re-advise.** The runbook reorganises what was decided. It doesn't add your own
  better idea. If you see a real problem (a step that will fail), raise it once in the
  closing lines, and let the user decide whether it changes the runbook.

## 3. Order by execution, not by conversation

Put each step where it has to happen, by its dependencies: you can't verify a domain you
haven't added, and you can't add DMARC before SPF and DKIM settle. Where the conversation
gave an order explicitly, keep it. Where two steps don't depend on each other, keep the
conversation's order: it's the one the user has in their head.

**Steps implied by the agreed plan are fine; new advice isn't.** "Wait for the domain to
show Active" is part of the agreed nameserver step, even if it wasn't said as a separate
instruction. A step the conversation never implied belongs in the closing lines as a
suggestion, not in the runbook.

## 4. Find the waits

A wait is **forced time** that blocks a later step: propagation, a provider's cooldown, a
review window, a warm-up period, paint drying. Look for "until", "after", "hours", "days",
"can't … before", "give it".

- Put the wait **right after the step that starts the clock**, and set `blocks` to the
  first step it holds up.
- Say what to do meanwhile when there's something: "Do Phase 3 while you wait." That
  sentence turns a dead stop into a plan, and it's often why a phase exists at all.
- A short wait the user just watches ("usually under an hour, check it shows Active") is
  a **step**, because they tick it when it's done.
- A long activity ("warm it up for three weeks") is a step with the duration in its
  detail, not a wait. A wait has nothing to do.

## 5. Steps, notes, or neither

| it is | it becomes |
|---|---|
| something the user does and could tick off | a **step** |
| a decision, constraint or warning that changes how or whether they do something | a **note**, placed in the phase where it bites |
| forced time between steps | a **wait** |
| background, rationale, a tangent, small talk | nothing. The runbook isn't a transcript |

A note is short: a bold lead-in saying what to check or know, then one or two sentences.
If a note says "do X", it's probably a step.

Standing context the user will look up repeatedly (which account, which domain is for
what) goes in `footer`.

## 6. Literal values

Anything the user will type or paste goes in a step's `values`, **exactly as agreed**:
DNS records, commands, config lines, amounts, account names, file paths.

- **Never paraphrase, reformat, "fix" or complete a literal.** Not the spacing, not the
  quoting, not a placeholder. If the agreed value has a placeholder (`<your-token>`), keep
  it, and say in the detail where the real value comes from.
- **Never invent one.** If the conversation says "add the TXT record the console shows",
  the runbook says that too. It doesn't make up a plausible record.
- Short literals inside a sentence (`p=none`, a menu item name) can go inline in
  backticks. Anything long, or anything to paste, goes in `values`.
- One value per box, labelled with what it is and where it goes ("TXT, each domain").

## 7. Unresolved: ask or flag, never guess

Some things are still open at the end of a conversation: "maybe later", two options with
no decision, a value never given.

- **If it blocks the runbook's shape** (which of two different routes to take), ask before
  building. One round, at most three questions, each with a proposed default, so "just
  go" answers them all.
- **Otherwise build, and flag it on the step**: `confirm` says what to settle before doing
  it. For an "if you want" extra, also set `optional: true`.
- Never silently include an undecided step as if it were agreed, and never silently drop
  it.

## 8. Phases

Group steps into **3–8 phases**, each one a stretch of work in **one place**: a site, an
app, a room. `where` names that place ("admin console · DNS host"), because switching
places is where people lose their spot. A phase split by a wait is fine; so is a phase
that exists only to fill a wait ("While you wait").

Title phases by outcome ("Add the domains to Workspace"), not by tool. Fewer than 3
phases usually means the runbook is really a list; more than 8, that phases are
really steps.

## 9. Self-check before writing JSON

- [ ] Every superseded instruction and value is gone. Search the draft for the old words.
- [ ] Steps are in execution order; every dependency points backwards.
- [ ] Every forced wait is a wait bar right after the step that starts its clock.
- [ ] Every literal matches the conversation character for character.
- [ ] Warnings are notes, not checkboxes; tangents are gone.
- [ ] Every open question is either asked, or flagged with `confirm`.
- [ ] Nothing in the runbook is new advice the conversation didn't agree.
