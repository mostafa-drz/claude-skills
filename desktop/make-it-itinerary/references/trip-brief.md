# From conversation to trip brief

How to read what's already been said, find what's missing, and ask only what changes the
plan. Read this before asking the user anything.

## Contents
- Harvest: what the conversation already decided
- The brief
- Rank the gaps
- Ask like a good travel agent, not a form
- When to stop asking
- Worked gap analyses

## Harvest: what the conversation already decided

The skill usually starts mid-conversation. The user has been asking about a place, and
earlier replies may already hold options, picks and rejections. Read the **whole**
conversation before asking anything, and sort what you find into four piles:

| pile | example | what the plan does with it |
|---|---|---|
| **Committed** | "we'll take the second hotel" · "we booked the Airbnb in Baddeck" | keep it exactly. Plan around it. Don't swap it for something "better" |
| **Liked** | "the whale watching sounds great" | include it unless it conflicts with a commitment |
| **Rejected** | "no, too far" · "we're not into museums" | leave it out, and don't bring it back as an alternative |
| **Floated, not decided** | options an earlier reply listed that the user never answered | treat as candidates, not decisions |

Two rules come from how these conversations actually go:

- **Earlier replies weren't verified.** An option suggested ten messages ago may have been
  from memory, so it gets checked like anything else (see `verification.md`). Its being in
  the conversation isn't evidence that it's right.
- **The user's words beat your inferences.** If they said "4 of us" and later mentioned
  "the kids", the party is 4 with children of unknown ages. That doesn't make it 2 adults
  and 2 kids with ages you guessed.

## The brief

Everything the plan depends on. Each field records its **origin**, and the page shows
the origin next to the value, so the user can see what they told you and what you
assumed:

| origin | meaning | example |
|---|---|---|
| `said` | the user said it | "we're going Oct 9–12" |
| `inferred` | follows directly from what they said | "family of 4" + "the kids" → there are children |
| `asked` | they answered your question | "ages 6 and 9" |
| `assumed` | a stated default, with a `why` they can overrule | pace: relaxed, *because two young kids* |

Fields, roughly in the order they shape a plan:

1. **When**: exact dates, or length + rough dates. Season decides what's even open.
2. **Who**: adults, children and their ages, and anyone with mobility, dietary or
   medical needs that change what's possible.
3. **Where from and how**: arrival point and time, and whether there's a car. This sets
   day 1 and every transfer.
4. **Base**: where they're staying, if decided. One base or several.
5. **Pace**: relaxed · balanced · packed.
6. **Budget**: budget · mid · premium. Only when it changes the choices.
7. **Interests and must-dos**: what the trip is *for*.
8. **Avoid**: what they don't want.
9. **Output**: page (default), PDF, calendar, text to paste.

## Rank the gaps

Not every unknown is worth a question. Sort each missing field into one of three tiers:

| tier | test | what to do |
|---|---|---|
| **Blocking** | without it, the plan would be wrong, not just less tailored | **ask** |
| **Shaping** | the plan changes a lot depending on the answer | ask **only** if there's no sensible default. Otherwise assume it and say so |
| **Polish** | the plan barely changes | assume it silently, and record it as `assumed` in the brief |

Almost always blocking: **when** (a seasonal destination can be closed in the month
they're going) and **who** (children's ages change pace, activities and meal times). Often
blocking: **how they're getting around** (a plan built for a car doesn't work on transit).

Everything else is usually shaping or polish. Budget is only blocking when the user has
signalled it matters, or when the options differ by an order of magnitude.

## Ask like a good travel agent, not a form

- **One round, at most three questions.** Put a proposed default in every question, so
  a one-word reply ("yes", "go") answers all of them.
- **Show the plan's shape first.** People answer faster when they see what the answer
  changes: *"I'm thinking 4 days based in Baddeck, the Cabot Trail on day 2. Before I
  lock it in:"*
- **Ask about their trip, not your schema.** "Will you have a car?" rather than
  "transport mode?".
- **Always offer the way out:** *"…or say 'just go' and I'll use my defaults and mark
  them on the page."*

Example of one good round:

> I've got Ottawa, a family of 4, the downtown hotel you picked, and kayaking on the list. Three quick
> things before I build it:
>
> 1. **Dates?** Your earlier messages sound like mid-October. Is that the 9th–12th?
> 2. **The kids' ages?** That decides how long each stretch can be.
> 3. **Car or no car?** I'll assume a car, since Dow's Lake and the Gatineau side are
>    easier by car.
>
> Or say "just go" and I'll use those defaults.

## When to stop asking

Stop as soon as **every blocking gap is answered or impossible to answer**, and every
other gap has a stated default. That's usually one round, and never more than two.

- If the user says "just go", "you decide" or "surprise me", stop and assume. **Unknown
  dates are the one exception.** A seasonal plan built on guessed dates can be entirely
  wrong. Plan for the most likely dates, and write the assumption in the page header,
  not in small print.
- A second round is justified only when an answer **opens** a new blocking gap. For
  example, "we're flying in" raises the question of which airport, and when.
- Never ask something the conversation already answered. Re-asking tells the user you
  didn't read it, and that's the moment they stop trusting the plan.

## Worked gap analyses

**Cold start**: the skill was invoked with no travel conversation at all.
Everything is a gap. Ask the blocking three (where, when, who), and offer the rest as
defaults. The rest of the flow is the same.

**Rich conversation, few gaps** (the User B case in `examples.md`): the
destination, party, hotel, meals and an outdoor activity are all known. Only the dates
and the children's ages are missing, so ask those two and nothing else.

**Contradiction in the conversation**: "we'll be there 3 days" early on, and "our 4-day
trip" later. Ask this one directly, and make it the first question, because it changes
everything else.
