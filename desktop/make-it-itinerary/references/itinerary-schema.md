# The itinerary file

Every plan is held as one JSON document, `itinerary.json`. The page, the PDF and the
calendar file are all rendered from it, so they can't disagree, and an edit is a change
to the data followed by a re-render.

## Contents
- Why a file and not just a page
- The shape
- Field rules
- The check block: what "verified" means in data
- A minimal valid example

## Why a file and not just a page

- **It can be validated.** `scripts/validate_itinerary.py` catches the mistakes that make
  a plan unusable on the day: overlapping times, a day missing from the date range, a
  "verified" badge with no source behind it. A validator can check a file. It can't check
  prose.
- **One source, many outputs.** The HTML page, PDF, `.ics` and Markdown all come from the
  same data, so fixing a time once fixes it everywhere.
- **Edits stay small.** "Swap Tuesday and Wednesday" becomes a change to two dates, then a
  re-render, not a rewrite of the whole page.

## The shape

```json
{
  "schema": 1,
  "title": "Ottawa with the kids — 4 days",
  "generated_on": "2026-09-20",
  "trip": {
    "destination": "Ottawa, Ontario",
    "start": "2026-10-09",
    "end": "2026-10-12",
    "timezone": "America/Toronto",
    "party": { "adults": 2, "children": [6, 9], "notes": "one car seat" },
    "travel_mode": "car",
    "pace": "relaxed",
    "budget": "mid",
    "interests": ["outdoors", "museums"],
    "avoid": ["long drives after 6pm"]
  },
  "brief": [
    { "field": "party", "value": "2 adults, kids 6 and 9", "origin": "said" },
    { "field": "pace", "value": "relaxed", "origin": "assumed",
      "why": "two young kids; say 'make it busier' to change" }
  ],
  "days": [
    {
      "date": "2026-10-09",
      "title": "Arrive, settle in, ByWard Market",
      "base": "Downtown hotel",
      "items": [
        {
          "start": "15:00", "end": "15:30", "kind": "stay",
          "title": "Check in", "place": "The hotel you picked",
          "booking": "required",
          "check": { "status": "verified", "claim": "Check-in from 15:00",
                     "source": "https://example-hotel.com/policies",
                     "checked_on": "2026-09-20" }
        }
      ],
      "if_it_rains": "Swap the market walk for the Museum of Nature (indoor)."
    }
  ],
  "stays": [],
  "before_you_go": ["Reserve kayaks — weekends sell out (see day 3)."]
}
```

## Field rules

| field | rule |
|---|---|
| `schema` | always `1`. Bump it only when the shape changes |
| `generated_on` | the date the plan was checked, ISO `YYYY-MM-DD`. Every `checked_on` is on or before it |
| `trip.start` / `trip.end` | ISO dates, inclusive. `days` has exactly one entry per date in that range, in order |
| `trip.timezone` | an IANA zone (`America/Halifax`), used by the `.ics` export. `null` if unknown. The calendar then falls back to floating local times and says so |
| `trip.party.children` | ages as numbers, `[]` if none. Ages drive pacing, so an unknown age is `null`, never a guess |
| `trip.pace` | `relaxed` · `balanced` · `packed` |
| `trip.budget` | `budget` · `mid` · `premium` · `null` |
| `brief[].origin` | `said` (the user said it) · `inferred` (follows from what they said) · `asked` (answered a question) · `assumed` (a default; needs `why`) |
| `items[].start` / `end` | `HH:MM`, 24-hour, local to the destination. `end` after `start`. Items in a day are in time order and don't overlap |
| `items[].kind` | `activity` · `meal` · `travel` · `stay` · `free` |
| `items[].booking` | `required` · `recommended` · `walk-in` · `unknown` |
| `items[].cost` | free text with a currency and a range ("CA$18–24 per adult"). Omit it rather than invent one |
| `if_it_rains` | optional per day. Include it for any day that depends on weather |
| `before_you_go` | things that must happen **before** the trip: bookings, passes, tickets that sell out |

A value you don't know is `null` or left out. **Never fill a field to make the page look
complete.** An empty field tells the user something is missing, and a made-up one hides it.

## The check block

`check` is how the page decides which badge to show, so its rules are strict:

| `status` | requires | means |
|---|---|---|
| `verified` | `claim`, `source` (an `http(s)` URL you actually opened this session), `checked_on` | a source you read confirms the claim **for the trip dates** |
| `unverified` | `claim` optional | you couldn't confirm it, or search wasn't available |
| `conflict` | `claim` describing the disagreement, `source` for at least one side | sources disagree. The page shows both sides and the user decides |

- `claim` is the **specific** thing confirmed, such as "open Sat 10–17 in October". "It's a
  nice place" isn't a claim.
- A page that only proves the place exists doesn't verify its October hours. Put the
  claim at the level the source actually supports.
- Items the user already committed to (a hotel they booked) still get a check, on the
  facts the plan depends on: check-in time, distance to day 1.

## A minimal valid example

The smallest file the validator accepts: a one-day plan with a single unverified item.

```json
{
  "schema": 1,
  "title": "Day trip",
  "generated_on": "2026-09-20",
  "trip": { "destination": "Wakefield, Quebec", "start": "2026-10-03",
            "end": "2026-10-03", "timezone": "America/Toronto",
            "party": { "adults": 1, "children": [] }, "pace": "balanced" },
  "brief": [],
  "days": [
    { "date": "2026-10-03", "title": "Village and covered bridge",
      "items": [
        { "start": "10:00", "end": "12:00", "kind": "activity",
          "title": "Walk to the covered bridge", "booking": "walk-in",
          "check": { "status": "unverified" } }
      ] }
  ]
}
```
