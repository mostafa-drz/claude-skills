# one-thing-today

One thing to focus on today, for work, personal life or any area: what, why, and how to
start in the next 25 minutes.

> **Status: draft (v0).** Built from the official docs, then audited by three independent
> reviewers: life areas, configurability, and Desktop UX against current docs. The
> scripts and page are tested locally. It hasn't yet been run end to end inside Claude
> Desktop. The ten scenarios in [`evals/evals.json`](./evals/evals.json) are the
> acceptance test for that first run.

## The problem

We overthink. A morning starts with a calendar, forty emails, a task list and three
half-done documents, and the first hour goes on deciding. The usual fix is a better plan,
which is more of the same. Getting 1% better every day needs something smaller: pick one
thing, start it, and let the rest wait on purpose.

| what usually goes wrong | how this skill handles it |
|---|---|
| Every tool shouts, none decides | Reads your connected sources and memory, then names **one** thing |
| Work swallows everything | **Areas**: ask for "one thing for personal life". Saved rules like "weekends: personal only" keep work off the page |
| "Priorities" that are really busywork | Discounts tidying and inbox zero, unless that *is* your goal. The rest goes under **Can wait** |
| A focus you can't start | At most three steps, and the **first is 25 minutes or less** |
| Perfectionism: the draft sits at 80% for days | **Good enough** states the bar and what to skip; avoided things rank up |
| An AI that sounds sure about things it made up | Every reason cites a source it actually read, and the validator rejects anything else |
| Starting from zero every morning | Learns from outcomes and corrections through Claude's memory, per area |
| Guilt | The last focus is labelled by its day and asked about once, gently. "Nothing needs you today" is a valid answer |

## How it works

```
settings (chat › memory › defaults) ──► area ──► read that area's sources + memory + past chats
                                                               │
     page ◄── render ◄── validate focus.json ◄── pick one (who's waiting · what slips ·
       │                                           compounds · been avoided)
       └──► "did X happen?" + save what changed to memory ──► tomorrow's pick is better
```

## What you get

A single page:
- the date and **your one thing** (with its area) in large type;
- **Why this**, with the evidence behind it, each line tagged with its source;
- **How**, as up to three numbered steps with minutes;
- **Done when** and **Good enough**;
- a **Mark it done** button;
- **Can wait**.

It works in light and dark mode, is built for a phone first, and follows the chat's
language.

## Install (Claude Desktop / claude.ai)

```bash
cd claude-skills/desktop
zip -r one-thing-today.zip one-thing-today/
```

1. Make sure **code execution** is on in **Settings → Capabilities**.
2. Upload the zip under **Customize → Skills**
   ([using skills](https://support.claude.com/en/articles/12512180-using-skills-in-claude)).
3. Connect whatever you use: Google Workspace, Slack, Notion, Linear, Todoist and so on.
4. Turn on **memory** so it can learn.
5. Ask **"what's my one thing today?"**

## Settings

Say `config` to change the settings, `help` to see the current ones, and `reset` to go
back to the defaults. Settings are saved to Claude's memory as one line. What you say in
a chat beats saved settings, and saved settings beat the defaults. Full list:
[`SKILL.md` → Configuration](./SKILL.md#configuration).

- **Areas.** Map sources to areas (`work = Gmail (work), Slack, Linear`) and add day
  rules (`Sat–Sun: personal`).
- **Done storage.** `artifact` is the default: the artifact's own storage, which
  [persists between sessions](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them).
  If that storage isn't there, it falls back to `browser`.
- **Window, sources to skip, tone, schedule.**
- **Fixed on purpose:** one focus, at most three steps, a first step of 25 minutes or
  less, and evidence only from sources that were read.

`reset` clears settings only. Your history, outcomes, corrections and goals stay;
"forget my one-thing history" clears those, after a yes.

## Make it a daily routine

Say **"do this every morning"** after a run, and it proposes a
[scheduled task](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork).
With more than one area, it proposes a pair. To set them up by hand, open **Scheduled** in
the sidebar (in Cowork, if your app still shows it separately), then **New task → Set up
manually**:

| field | work | personal |
|---|---|---|
| Name | One thing today · work | One thing today · personal |
| Frequency | Weekdays | Daily (the instruction limits it to Sat–Sun) |
| Time | 07:30 | 09:00 |
| Approval mode | Auto-approve | Auto-approve |
| Instructions | Run one-thing-today for today, area: work. Lead with a five-line text version, then the page. | On Saturday and Sunday only: run one-thing-today for today, area: personal. Lead with a five-line text version, then the page. On other days, reply "Not today" and stop. |

Scheduled tasks run in the cloud, even when your computer is asleep or the app is closed,
with your connectors and skills, on paid plans. You get a push notification when a run
finishes. Auto-approve matters: without it, the 07:30 run waits for your go-ahead.

## Design decisions, and where they come from

- **Same shape as [`make-it-runbook`](../make-it-runbook/)**: data file → stdlib
  validator → template renderer. The limits that make it a *focus* are checks, not hopes.
- **Areas are free text, not a fixed list.** One optional field, rules saved in memory,
  and memory lines tagged by area. No new script. Personal and work sources never mix on
  one page.
- **Memory is the learning store and the settings store.** Desktop skills can't keep files
  between conversations. Claude reads and updates memory during chats and can search past
  chats
  ([chat search and memory](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)).
  Memory "works across chat and Cowork in the cloud"
  ([release notes, 2026-08-25](https://support.claude.com/en/articles/12138966-release-notes)).
  Each project has its own memory, and past-chat search needs a paid plan, so the skill
  says when history comes back empty and why.
- **Cloud scheduled tasks.** A morning focus has to be ready before you are, so it has to
  run with the machine asleep. That rules out Claude Code Desktop's local tasks, which
  "only fire while the app is open and your computer is awake"
  ([docs](https://code.claude.com/docs/en/desktop-scheduled-tasks)).
- **A 192-character description.** The claude.ai help center caps upload descriptions at
  200 characters
  ([custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)),
  stricter than the platform's 1,024. Trigger phrases come first; the rest is in the body.
- **Artifact storage with a browser fallback.** The help center documents per-artifact
  personal storage but not its script API. The page looks for `window.storage` and falls
  back to `localStorage`, guarding every call, so it works either way.
- **The page is generated once.** Claude writes the artifact as the template plus the data
  block, which `render_page.py --data` prints already escaped. A full rendered file is only
  made when artifacts aren't available, so the page is never written twice.
- **`side_effects: true`**, because it writes to memory and can create a scheduled task.
  It only schedules after a yes, and says what it saved every time.

## Honest limits

- **It only knows what's connected.** A priority that lives in your head needs to be said
  once, and memory keeps it after that.
- **Learning needs memory on**, outside incognito, and in the same project each time.
- **Done on the page doesn't reach Claude.** Say "done" in the chat, or answer the next
  run's question.
- **Scheduled runs can't ask questions.** The last focus shows as *unknown* unless the run
  can see it happened.

## Layout

```
one-thing-today/
├── SKILL.md                         the workflow, and Configuration
├── references/choosing.md           gather, pick, write, learn (area-aware)
├── scripts/
│   ├── validate_focus.py            the focus rules as checks
│   └── render_page.py               --data for the artifact; a full file when no artifacts
├── assets/focus-template.html
├── evals/
│   ├── evals.json                   ten acceptance scenarios
│   ├── example-focus.json           a work focus (fictional)
│   └── example-focus-personal.json  a personal focus on a Saturday (fictional)
└── icon.svg
```

## Testing

Checked locally:

- **Validator.** Both examples pass. It rejects each of these:
  - a focus over 90 characters
  - four steps, a first step of 60 minutes, or `"minutes": true`
  - no evidence, or evidence citing a source that wasn't read (Memory and Past chats included)
  - a bad outcome value or an empty day
  - an area over 24 characters
  - an unknown `done_storage`
  - an unknown label key

  It warns on a focus that joins two things, and on non-English pages with no labels.
- **Page.** Screenshotted in dark mode (work) and light mode (personal). A hostile focus
  (`</script><img onerror=…>`) is escaped by the renderer (`--data` and full-file modes) and set with `textContent`.
- **Done state.** It survives a reload with browser storage. Each save is timestamped and
  the newest copy wins, tested with a stand-in `window.storage`:
  - a click during a slow storage read stays done;
  - after a failed artifact write and a reload, the newer browser copy wins;
  - a newer value from another device wins;
  - the page still works when storage throws, or doesn't exist.
- **Accessibility.** The focus ring uses `--ink` (3:1 or better in both themes), and the
  done-state text meets 4.5:1.

Run each scenario in `evals/evals.json` in a fresh Claude Desktop conversation with the
skill enabled, and check the listed behaviours.
