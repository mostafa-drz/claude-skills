# make-it-itinerary

Turn the trip you've been chatting about into a plan you can actually travel with.

> **Status: draft (v0).** Built from a handwritten spec and the official skills docs, with
> the scripts and page tested locally. It hasn't yet been run end to end inside Claude
> Desktop. The four scenarios in [`evals/evals.json`](./evals/evals.json) are the
> acceptance test for that first run.

## The problem

Travel planning with Claude usually happens as a conversation: *what's Cape Breton like,
where should we stay, where do we eat*. By the end the useful decisions are scattered
across twenty messages, some of the suggestions came from memory rather than a check, and
nothing is in a shape you can use on the day.

Asking for "an itinerary" at that point tends to fail in predictable ways:

| what usually goes wrong | how this skill handles it |
|---|---|
| The plan ignores what you already decided, like the hotel you picked | Reads the whole chat first and sorts it into **committed · liked · rejected · floated**. Committed choices are kept exactly |
| A wall of questions before anything happens | **One round, at most three questions, each with a default.** "just go" always works. Only dates are never silently assumed |
| Confident details that turn out wrong: closed for the season, booked out | Every stop is **checked online for the actual trip dates**, with the source and check date recorded |
| "Verified" meaning nothing | A validator refuses a verified badge without a source URL, a specific claim and a date |
| Days that zig-zag across town, with no travel time | Stops clustered by area, real transfer items, a pace limit per day, and rain plans |
| A plan stuck in the chat | A page that works on a phone, prints one day per page, and exports to your calendar |

## How it works

```
conversation ──► harvest ──► fill gaps (≤3 questions, defaults) ──► draft days
                                                                       │
        page · PDF · .ics · text  ◄── render ◄── validate ◄── verify each stop
                     ▲                                        (for the trip dates)
                     └──────────── "swap day 2 and 3" edits the data ──────┘
```

1. **Harvest** what the conversation already decided.
2. **Fill the gaps.** Only what blocks the plan gets asked (usually *when* and *who*),
   and everything else gets a stated default.
3. **Draft** days clustered by geography, with one anchor per day, pace limits,
   real transfers and a rain alternative.
4. **Verify** each stop for the trip dates: season, hours, booking, age limits. The
   operator's own site wins, and disagreements are shown rather than hidden.
5. **Validate** `itinerary.json`, the single source every output renders from.
6. **Deliver** an HTML page, and on request a PDF, a calendar file or text for a group chat.

## What you get

A self-contained page (light and dark, phone-first):

- **What I planned around**: every input marked *from your chat*, *you answered* or
  *I assumed (because…)*, so you can overrule an assumption at a glance.
- **Before you go**: what to book, and why. Ticking items off is remembered in your browser.
- **Each day**: times, map links, booking and cost pills, and a badge per stop:
  **Checked** (with source and date), **Not verified**, or **Sources disagree**.
- A **"Only things to book or confirm"** filter, and a print layout for PDF.
- During the trip it opens on today's date.

## Install (Claude Desktop / claude.ai)

```bash
cd claude-skills/desktop
zip -r make-it-itinerary.zip make-it-itinerary/
```

Then go to **Settings → Capabilities**, make sure **Code execution and file creation**
is on, and upload the zip under **Skills**. For verified plans, web search also needs to
be on in the chat. Without it, the skill says so and marks everything unverified.

Start it by saying **"make it an itinerary"** at any point in a travel conversation.

## Design decisions, and where they come from

- **No slash command.** The help center documents `/` for picking a skill only in the
  Microsoft 365 add-ins. In claude.ai and Claude Desktop chat, "Claude determines skill
  usage automatically based on context"
  ([Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)).
  So the trigger is the phrase, and the description front-loads it, including the
  literal `/make-it-itinerary` for people who type it out of habit.
- **Verification degrades honestly.** Skills on claude.ai run with full, partial or no
  network access depending on settings
  ([Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#runtime-environment-constraints)),
  so the skill checks what's available and never presents an unchecked item as checked.
- **Deterministic steps are scripts.** Validation, page rendering and `.ics` export are
  small standard-library Python scripts, following the docs' guidance to prefer scripts
  for fragile, repeatable operations and to use a plan-validate-execute loop
  ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
  Standard library only, because runtime package installs depend on the surface.
- **One data file, many outputs.** The page, PDF, calendar and text all render from
  `itinerary.json`, so fixing a time fixes it everywhere, and an edit is a small data
  change rather than a rewrite.
- **Calendar times are converted to UTC through the trip's timezone**, so a phone still
  on home time before the trip shows each stop at the right local hour
  ([RFC 5545](https://www.rfc-editor.org/rfc/rfc5545)).
- **Nothing persists between conversations.** Desktop skills can't write local
  preferences, so `config` covers one conversation, and permanent defaults live in the
  **Configuration** section of `SKILL.md`.

## Honest limits

- **Checked means checked on that day.** Hours and seasons change, and the page prints
  the check date for that reason.
- **Travel times are estimates.** The skill can't query a routing API from the sandbox,
  so transfers are rounded-up ranges, marked "about".
- **It never books anything.** It tells you what to book and when.
- **Search quality varies by destination.** Small operators often have no current
  website, and those stops stay "Not verified" rather than being given a guessed badge.

## Layout

```
make-it-itinerary/
├── SKILL.md                      the workflow (what Claude reads on trigger)
├── references/
│   ├── trip-brief.md             harvesting the chat, ranking gaps, asking well
│   ├── verification.md           what to check, how, which source wins
│   ├── itinerary-schema.md       the itinerary.json contract
│   └── examples.md               Cape Breton, Ottawa, edits, no web search
├── scripts/
│   ├── validate_itinerary.py     errors + warnings, exit 1 on errors
│   ├── render_page.py            itinerary.json → self-contained HTML
│   └── make_ics.py               itinerary.json → calendar file
├── assets/itinerary-template.html
├── evals/evals.json              four acceptance scenarios
└── icon.svg
```

## Testing

The scripts are checked locally. The validator has to reject a file seeded with each
error class, the `.ics` output has to parse with the `icalendar` library, and the page is
screenshotted at 390px and 900px in both themes and printed to PDF.

The skill itself is tested with the four scenarios in `evals/evals.json`. Run each in a
fresh Claude Desktop conversation with the skill enabled, and check the listed
behaviours. Per the docs' recommendation, run them on each model you plan to use it with.
