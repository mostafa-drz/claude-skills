# Researching and picking

Contents: [Sources](#sources) · [Prices](#prices) · [Rows](#rows) · [Pick](#pick) · [Follow-ups](#follow-ups)

## Sources

Read in this order, and stop when the rows are filled:

| rank | source | use it for | `kind` |
|---|---|---|---|
| 1 | The maker's spec page, manual or datasheet | every published number: size, weight, capacity, ports, warranty | `maker` |
| 2 | Independent measurement reviews (lab-style sites that publish test methods) | what spec sheets can't say: measured battery, noise, brightness, real range | `review` |
| 3 | Retailer listings in the user's country | price, stock, the retailer's warranty or return window | `retailer` |
| 4 | What the user pasted or said ("it has to fit my 40 cm shelf") | constraints and their own measurements | `user` |
| 5 | Claude's own knowledge, only with no web access | a starting point, marked unverified | `claude` |

- **One source entry per page read**, with its URL. Cite it by `id` on every value it
  supports.
- **Maker claims vs measured.** When a review measures something the maker also states
  (battery hours), prefer the measurement for the row, and put the claim in `note`:
  "Maker says 40 h". Say which one the row is in its label if it matters: "Battery
  (tested)".
- **Model names are traps.** Check the exact model, generation and region: "Gen 2",
  "2025", "(EU)". A spec from the previous generation is a wrong value, not an
  approximation.
- **Owner reviews and forums** are for patterns ("hinge cracks after a year" reported
  widely), never for numbers. Put a pattern in `cons` only with a source that shows it's
  common, and phrase it as reported.
- **A fetch that fails** (blocked, paywalled, 404) goes in `sources_missing`. Don't cite
  a page you couldn't open.

## Prices

- Read the price from the maker's store or a major retailer **in the user's country**,
  today. Record `where` and `as_of`. Use the same currency for every product so the price
  row can compare; if a product is only sold elsewhere, convert and say so in
  `assumptions`.
- Configurable products (storage, colour, size): the configuration that matches the
  comparison, or the cheapest with `"from": true`.
- A temporary sale price is fine, but say so in `price.note`: "Sale, list $449". Don't predict sales. If asked, say what's known (typical sale
  seasons) as general knowledge, not a promise.
- No price found: `price: null` with `price_note` ("Not sold in Canada yet").

## Rows

Aim for 8–14; the validator allows 3–20.

1. **The user's priorities first.** Each gets a row; name the row the way they said it
   when possible ("Quiet on flights" → "Noise reduction (low rumble)").
2. **Rows where they differ** in a way someone would notice: weight, battery, size,
   ports, repairability, warranty, running costs (ink, filters, subscriptions).
3. **Deal-breaker checks** for the category: fits the space, works with their phone or
   system, needs a subscription, region lock.
4. **Drop** rows every product shares, unless the user asked. Two or three shared rows are
   fine as reassurance ("all three have multipoint"); more is noise, and the validator
   warns.

Units: one unit per row (`g`, `h`, `dB`, `W`, `yr`), converted if sources differ. Set
`better` only when more (or less) is plainly better for everyone: weight lower, battery
higher. Leave it off for taste rows (colour, size when bigger isn't better).

Groups: 3–6 plain names in the order a person thinks: what it does, how long it lasts,
how it fits their life, what it costs to own.

## Pick

1. **Filter.** Drop anything that fails a hard constraint (over budget, doesn't fit,
   incompatible). If that removes all but one, that's the pick, and the headline says why.
2. **Priorities, in order.** Who wins the first priority, and by how much? A small win
   (5%) on priority one can lose to a big win on priority two. Say the size of the gap in
   `why`, in plain units ("5 dB", "40 g", "$50").
3. **Price.** Between near-equals, the cheaper one wins, unless the user said price
   doesn't matter.
4. **Everything else** only breaks ties.
5. **Write it.** `headline`: the product and the reason in one line. `why`: two or three
   sentences with the trade-off stated honestly. `because`: the 1–4 rows that decided
   it. `runner_up.when`: the one condition that would flip the pick, in the user's terms.
6. **`best_for`** labels are earned by winning a row ("Lightest" needs the lowest weight).
   Every label names its `row`, and the validator checks the product wins it. A row
   where any product's value is unknown has no winner: the unknown one might be better.

No priorities given? Pick for the most common reason people buy the category, say that
in `assumptions`, and make the runner-up condition the other common reason.

## Follow-ups

Prompts pasted from the page look like "About the Aria 2 (from my which-to-buy comparison
of Noise-cancelling headphones: …): <question>". Answer in the chat from the same data,
reading more only when the question needs it. If the answer changes a value, a price or
the pick, update `compare.json`, validate, and re-render the page, then say in one line
what changed.
