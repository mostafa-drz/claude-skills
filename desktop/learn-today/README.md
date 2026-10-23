# learn-today

A daily deck of 3-5 things worth learning (a talk, an article, a podcast episode) picked
for your goals in work, business and life, with **why it's for you**, **what you'll get**
and **one thing to try**. It learns from your 👍 and 👎.

> **Status: draft (v0).** Built from the official docs; scripts and page tested locally.
> Not yet run end to end in Claude Desktop. The seven scenarios in
> [`evals/evals.json`](./evals/evals.json) are the acceptance test for that first run.

## How it works

```
feedback from last deck ──► signals: project goals · memory · past chats · calendar/Linear (light)
                                                         │
     deck ◄── render ◄── validate deck.json ◄── pick 3-5 ◄── web search → open every link
       │                                         (top pick · mix · varied formats · budget)
       └──► 👍 / 👎 / ✓ on each card ──► last card: Copy feedback ──► paste in chat ──► memory
```

## Set it up (about five minutes)

1. Zip and upload it, with **code execution** and **web search** on:
   `cd claude-skills/desktop && zip -r learn-today.zip learn-today/`, then **Customize →
   Skills** ([using skills](https://support.claude.com/en/articles/12512180-using-skills-in-claude)).
2. Create a **project** (Projects → +). Add a short goals note to its files or
   instructions: one line each for work, business and life. A project keeps its own
   instructions, files, memory and scheduled tasks
   ([projects](https://support.claude.com/en/articles/14116274-organize-your-tasks-with-projects-in-claude-cowork)).
3. In that project, ask **"what should I learn today?"**, then say **"do this every
   morning"**. It proposes a daily 07:00 task with auto-approve and creates it after your
   yes. By hand: the project's **Scheduled → New task**
   ([scheduled tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)).

| field | value |
|---|---|
| Name | Learn today |
| Frequency | Daily |
| Time | 07:00 |
| Approval mode | Auto-approve |
| Instructions | Run learn-today for today. Lead with a five-line text list (title, format, minutes, link), then the deck. |

## The deck

Cover (what it tuned for you, and the list) → one card per pick → a feedback card. Swipe,
arrow keys or buttons. Each card: area, format and minutes; the title and creator; **why
for you**, with the sources behind it; **what you'll get**, and what the summary was
written from; **try after**; **Open**; 👍 **More like this** · 👎 **Not for me** · ✓
**Done**. Phone first, light and dark.

## How it learns

The page can't write to Claude's memory (nothing in the
[artifact docs](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)
supports it), so the last card turns your taps into one **learn-today feedback** line
with a Copy button. Paste it in any chat in the project, or just say "more like 1, the
podcast was too slow". The next run reads it from project memory, and the cover's
**Tuned for you** shows what changed. Reasons beat taps; a pattern needs three repeats;
past decks are the no-repeat history (90 days).

## Settings

`config` changes them, `help` shows them, `reset` restores the defaults and never touches
your goals, feedback or history. Full list: [`SKILL.md` → Configuration](./SKILL.md#configuration).
Mix (default work, business, life), cards (4), daily minutes (30), formats, level,
paywalls, creators to favour or block.

## Design decisions

- **Same shape as [`one-thing-today`](../one-thing-today/)**: data file → stdlib
  validator → template page, so the rules that keep it honest are checks, not hopes.
- **Every link is opened this run.** YouTube via its public oEmbed endpoint, everything
  else by fetching the page. The validator requires `verified_by` and `summary_from` on
  every card, so a summary written from a description says so.
- **Project + memory, not files.** Project memory works in cloud scheduled runs; writing to
  local files would make the task run only locally.
- **A 198-character description**, under claude.ai's 200-character upload cap.
- **`side_effects: true`**: it writes to memory and can create a scheduled task, only
  after a yes.

## Honest limits

- **Needs web search.** Without it, it stops rather than guess links.
- **Feedback taps stay on the page** until you paste the line or tell Claude.
- **Scheduled runs can't ask questions**, so a cold start builds a broad deck and asks
  for your goals on the cover.
- **Summaries from descriptions** are weaker than from transcripts, and labelled as such.

## Layout

```
learn-today/
├── SKILL.md                    the workflow, and Configuration
├── references/picking.md       signals, search, pick, write, learn
├── scripts/validate_deck.py    the deck rules as checks
├── scripts/render_page.py      --data for the artifact; a full file when no artifacts
├── assets/deck-template.html   the swipeable deck
├── evals/evals.json            seven acceptance scenarios
├── evals/example-deck.json     a fictional deck (placeholder links)
└── icon.svg
```

## Tested locally

- The validator passes the example and rejects: 2 or 6 cards, duplicate links, http
  links, a missing `verified_by` or `summary_from`, a citation of an unread source (in a
  card or in `adjusted`), a top pick over budget, one summary line, two stretch cards, a
  boolean `minutes`, an unknown format or label.
- The page, screenshotted in light and dark at phone width (cover, card, feedback card). A
  hostile title (`</script><img onerror=…>`) renders as text, and a `javascript:` link
  gets no Open button.
