# one-thing-today

One thing to focus on today: what, why, and how to start in the next 25 minutes.

> **Status: draft (v0).** Built from the official docs, with the scripts and page tested
> locally. It hasn't yet been run end to end inside Claude Desktop. The six scenarios in
> [`evals/evals.json`](./evals/evals.json) are the acceptance test for that first run.

## The problem

We overthink. A morning starts with a calendar, forty emails, a task list and three
half-done documents, and the first hour goes on deciding. The usual fix is a better plan,
which is more of the same. Getting 1% better every day needs something smaller: pick one
thing, start it, and let the rest wait on purpose.

| what usually goes wrong | how this skill handles it |
|---|---|
| Every tool shouts, none decides | Reads all connected sources and memory, then names **one** thing |
| "Priorities" that are really busywork | Discounts tidying and inbox zero; they go under **Can wait** |
| A focus you can't start | At most three steps, and the **first is 25 minutes or less** |
| Perfectionism: the draft sits at 80% for days | **Good enough** states the bar and what to skip; avoided work ranks up |
| An AI that sounds sure about things it made up | Every reason cites a source it actually read. The validator rejects the rest |
| Starting from zero every morning | Learns from outcomes and corrections through Claude's memory |

## How it works

```
yesterday? (one question) ──► read every connected source + memory + past chats
                                                   │
      page ◄── render ◄── validate focus.json ◄── pick one (who's waiting · what slips ·
        │                                          compounds · been avoided)
        └──► save what changed to memory ──► tomorrow's pick is better
```

## What you get

A single page: the date, **your one thing** in large type, **Why this** with the evidence
behind it (each line tagged with its source), **How** as up to three numbered steps with
minutes, **Done when**, **Good enough**, a **Mark it done** button, and **Can wait**.
Light and dark, phone-first. The done state is saved in your browser.

## Install (Claude Desktop / claude.ai)

```bash
cd claude-skills/desktop
zip -r one-thing-today.zip one-thing-today/
```

Then go to **Settings → Capabilities**, make sure **Code execution and file creation** is
on, and upload the zip under **Skills**. Connect whatever you use (Google Workspace,
Slack, Notion, Linear, Todoist…). Turn on **memory** so it can learn. Then ask **"what's my
one thing today?"**

## Make it a daily routine

Say **"do this every morning"** after a run, and it proposes a
[Cowork scheduled task](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork).
To set one up by hand: **Cowork → Scheduled → New task → Set up manually**, then:

| field | value |
|---|---|
| Name | One thing today |
| Frequency | Weekdays (or Daily) |
| Time | 07:30 |
| Instructions | Run one-thing-today for today. Don't ask about yesterday; mark it unknown unless you can see it was done. |

Scheduled tasks run in the cloud even when your computer is asleep or the app is closed,
with your connectors and skills. They need a paid plan. Past runs and the pause switch are
in **Scheduled**.

## Design decisions, and where they come from

- **Same shape as [`make-it-runbook`](../make-it-runbook/)**: data file → stdlib
  validator → template renderer. The limits that make it a *focus* (one line, three steps,
  a first step of 25 minutes or less, evidence only from sources read) are checks, not
  hopes.
- **Memory is the learning store.** Desktop skills can't keep files between
  conversations. Claude's memory is read and updated during conversations, and Claude
  can search past chats
  ([chat search and memory](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)).
  Memory also works in cloud Cowork tasks, which is what makes a scheduled run learn too.
- **A Cowork scheduled task, not a local one.** Claude Code Desktop's local tasks only fire
  while the app is open and the computer is awake
  ([docs](https://code.claude.com/docs/en/desktop-scheduled-tasks)). A morning focus has to
  be there before you are.
- **No slash command in chat.** Skills trigger from context in claude.ai and Desktop
  ([using skills](https://support.claude.com/en/articles/12512180-using-skills-in-claude)),
  so the description leads with the phrases people actually say.
- **`side_effects: true`** because it writes to memory and can create a scheduled task.
  It only schedules on a yes, and says what it saved to memory every time.

## Honest limits

- **It only knows what's connected.** A priority that lives in your head needs to be said
  once, and memory keeps it after that.
- **Learning needs memory on.** Without it, every day starts fresh, and it says so.
- **The done button stays in your browser.** Tell Claude, or let tomorrow's run ask.
- **Scheduled runs can't ask questions**, so yesterday's outcome is `unknown` unless the
  run can see it happened.

## Layout

```
one-thing-today/
├── SKILL.md                    the workflow (what Claude reads on trigger)
├── references/choosing.md      gather, pick, write, learn
├── scripts/
│   ├── validate_focus.py       the focus rules as checks
│   └── render_page.py          focus.json → self-contained HTML
├── assets/focus-template.html
├── evals/
│   ├── evals.json              six acceptance scenarios
│   └── example-focus.json      a reference focus (fictional)
└── icon.svg
```

## Testing

Checked locally:

- The validator passes `evals/example-focus.json`, and rejects a focus over 90
  characters, four steps, a first step of 60 minutes, no evidence, a bad yesterday
  outcome, and an evidence line citing a source that wasn't read. It warns on a focus
  that joins two things.
- The page was rendered and screenshotted in dark mode. A hostile focus
  (`</script><img onerror=…>`) is escaped by the renderer and set with `textContent`.
- Not yet checked: light mode at phone width, and the done button across a reload.

The skill itself is tested with `evals/evals.json`: run each scenario in a fresh Claude
Desktop conversation with the skill enabled and check the listed behaviours.
