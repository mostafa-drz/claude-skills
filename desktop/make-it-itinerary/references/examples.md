# Worked examples

The two journeys from the original sketch, walked end to end, plus the two situations
that most often go wrong: an edit after delivery, and planning with no web search. Read
the one that matches the situation. They show the judgment, and the other references
give the rules.

Facts below about real places are **placeholders for what you'd check**, not claims.
Verify them as usual for the trip dates.

## Contents
- A: thin conversation (Cape Breton)
- B: rich conversation (Ottawa, family of 4)
- C: changing the plan after delivery
- D: no web search in this chat

## A: thin conversation (Cape Breton)

**The conversation so far**

> **User:** What's Cape Breton like, and what's around it?
> *(an overview reply)*
> **User:** Where are the best places to stay?
> *(a reply listing a few areas: Baddeck, Chéticamp, Ingonish)*
> **User:** make it an itinerary

**Harvest.** Committed: nothing. Liked: nothing explicit. Floated: three base areas.
Known: the destination. Unknown: when, who, how long, and whether there's a car.

**Gap round.** Show the shape of the plan, then ask the blocking questions with defaults:

> Here's the shape I'd suggest: two bases so you're not doubling back, Baddeck and then
> the Chéticamp side, with the Cabot Trail as the centrepiece. Three things first:
>
> 1. **When, and for how long?** Cape Breton is very seasonal, so this matters most.
> 2. **Who's going?** Adults only, or kids, and their ages?
> 3. **Driving?** I'll assume a car. The Trail really needs one.
>
> Or say "just go": I'll assume 4 days next month, 2 adults and a car, and mark those
> assumptions on the page.

**What gets verified.** The season is what can break this trip, so check it first: which
of the floated stays and attractions are open on the actual dates, sunset time (it
decides where the Trail drive has to end each day), and anything on the route with a
seasonal closure. Hotels are *suggested*, not picked, so check they're open and give a
price band.

**The plan's shape.** Day 1 arrive and settle in, day 2 the Trail in the direction that
puts the viewpoints on your side of the road (check it; don't just assert it), day 3 a
hike with a rain alternative, day 4 a slow morning and the drive out. Every scenic day
gets an `if_it_rains`.

**Deliver.** The page, then one line: what was assumed, what couldn't be verified, and
what to book first. Offer the PDF, because the user in the sketch asked for one.

## B: rich conversation (Ottawa, family of 4)

**The conversation so far**

> **User:** Tell me about Ottawa and the area around it.
> **User:** We're visiting with the family, 4 of us. Where should we stay?
> *(a reply with three hotel options)*
> **User:** We'll take the second one. Where should we eat?
> *(the assistant asked about preferences, then suggested restaurants)*
> **User:** make it an itinerary, and we want to do some kayaking

**Harvest.**

| pile | contents |
|---|---|
| committed | the second hotel (stays exactly as picked), the family of 4 |
| liked | the restaurants the user reacted to well |
| floated | restaurants they didn't respond to, attractions from the first reply |
| new | kayaking |
| unknown | dates, children's ages (they said "family of 4", not how old) |

**Gap round.** Two questions. Everything else is already answered:

> I've got the hotel, the restaurants you liked, and kayaking. Two things:
> 1. **Which dates?**
> 2. **How old are the kids?** Kayak rentals often have age or size rules, and it
>    changes how long each outing can be.

**What gets verified.** The kayak operator's season and **its** age policy for those
dates. That's the item most likely to fail, so check it first. Then the chosen hotel's
check-in time and its distance to each day's stops, and whether the liked restaurants are
open on the days they're scheduled. Don't re-evaluate the hotel. It was picked.

**The plan's shape.** Kayaking in the morning, when water and wind are usually calmer
(verify for that spot), with the rain alternative indoors nearby. Restaurants placed near
where the family will be at mealtime, not in the order they came up in the chat.
`before_you_go`: reserve the kayaks and any timed-entry museum tickets.

## C: changing the plan after delivery

> **User:** can we swap days 2 and 3, and add something for a rainy afternoon?

1. Change the data. Swap the two days' `items`, and keep each day's `date` in place.
2. **Re-check what the swap moved.** An attraction verified as open on Saturday isn't
   verified for Sunday. Anything whose `claim` was specific to a day goes back to
   verification.
3. Add the `if_it_rains` options, verified like any other item.
4. Validate, re-render **the same artifact**, and state what changed in one or two
   lines: *"Swapped days 2 and 3. The museum is closed Mondays, so I moved it to the
   afternoon of day 2."*

Never regenerate the whole plan for a small edit. The user has already read it, and
unexplained changes elsewhere cost their trust.

## D: no web search in this chat

> **User:** make it an itinerary

Web search isn't available. Say so first, and give the choice:

> Web search is off in this chat, so I can't check opening hours or seasons. You can
> turn it on and ask again for a verified plan, or I can build it now from what I know,
> with everything marked "not verified".

If they go ahead: build it, set every place-specific item to `unverified`, leave out
`source`, keep costs as rough bands or leave them out, and make the page header meter
honest (0 of N checked). In `before_you_go`, add one line: "Confirm hours and seasons
for each stop; this plan wasn't checked online."
