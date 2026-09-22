# make-it-runbook

Turn the setup you worked out in the chat into a runbook you can tick through.

> **Status: draft (v0).** Built from a written proposal and a hand-made runbook that worked
> well in practice, with the scripts and page tested locally. It hasn't yet been run end to
> end inside Claude Desktop. The five scenarios in [`evals/evals.json`](./evals/evals.json)
> are the acceptance test for that first run.

## The problem

Setup work with Claude happens as a conversation: *how do I point the domain, what record
goes where, wait, that was wrong, use this one instead*. By the end the real plan is
spread over twenty messages, one piece of advice was taken back halfway, a value changed,
and two steps can't happen until a day has passed. Scrolling back to follow it is how you
end up applying the version that was corrected.

| what usually goes wrong | how this skill handles it |
|---|---|
| The checklist follows advice that was later corrected | Distills first: builds a ledger of every instruction and keeps only the **last agreed word**. A correction replaces, it doesn't add |
| Steps in the order they were discussed, not the order they run | Orders by dependency; conversation order only breaks ties |
| A forced wait buried in a paragraph | An **amber wait bar** right after the step that starts the clock, saying what to do meanwhile |
| A DNS record or command retyped slightly wrong | Literal values copied **character for character** into monospace boxes with a Copy button |
| Warnings mixed in with the steps | **Notes** for decisions and warnings; checkboxes only for things you do |
| Undecided extras quietly included, or dropped | Flagged on the step: *Confirm before doing*, *Optional* |
| Losing your place, or losing ticks after an edit | Ticks saved in the browser; ids that survive every edit, enforced by a validator |

## How it works

```
conversation ──► distill (ledger → final agreed steps) ──► ask only what changes the shape
                                                                        │
          page · PDF  ◄── render ◄── validate runbook.json ◄────────────┘
              ▲                          │
              └── "add a backup step" edits the data; ids kept, new ids appended
```

1. **Distill**: every instruction and value becomes a ledger line; superseded ones drop,
   tangents drop, the rest is ordered by what depends on what.
2. **Ask or flag**: a question only when an open choice changes the runbook's shape (one
   round, ≤3 questions, defaults). Anything else open is built and flagged on its step.
3. **Validate** `runbook.json`, the one file the page renders from.
4. **Deliver** the page, and a PDF on request.

## What you get

A self-contained page (light and dark, phone-first), in the look of the runbook it was
modelled on:

- **Phases**, each with where it happens (`admin console · DNS host`).
- **Steps** as checkbox rows: the action in bold, the exact specifics beneath. Ticked steps
  strike through; a finished phase gets a check.
- A **progress bar** ("5 of 13 done") and a **Next:** link that jumps to the first
  unticked step.
- **Wait bars** with a duration chip, **notes**, and **copyable values**.
- **Print / save PDF**: empty boxes, wait bars and notes kept in colour, long values
  wrapped, phases kept whole where they fit.

## Install (Claude Desktop / claude.ai)

```bash
cd claude-skills/desktop
zip -r make-it-runbook.zip make-it-runbook/
```

Then go to **Settings → Capabilities**, make sure **Code execution and file creation** is
on, and upload the zip under **Skills**. Start it by saying **"make it a runbook"** once
the steps have been worked out in the chat.

## Design decisions, and where they come from

- **Built on the same shape as [`make-it-itinerary`](../make-it-itinerary/)**:
  conversation → one JSON file → stdlib validator → template renderer. The proposal this
  came from had the agent edit HTML by hand. A data file plus a validator turns "ids must
  never be reused" from a promise into a check.
- **No slash command.** In claude.ai and Claude Desktop chat, "Claude determines skill
  usage automatically based on context"
  ([Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)),
  so the trigger is the phrase, and the description front-loads it.
- **Deterministic steps are scripts**, following the docs' guidance to prefer scripts for
  fragile, repeatable operations and to use a plan-validate-execute loop
  ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
  Standard library only, because runtime package installs depend on the surface
  ([runtime constraints](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#runtime-environment-constraints)).
- **PDF comes from the page's print layout** (or the environment's own PDF capability)
  rather than a headless-browser script, since neither Chromium nor weasyprint can be
  assumed in the sandbox.
- **Ticks live in `localStorage`, behind try/catch.** Storage can be blocked, and the page
  works the same without it. The storage key is the runbook's `key`, not its title, so
  renaming a runbook doesn't lose anyone's progress.
- **Values are rendered as text, never HTML.** A command containing `</script>` or `<b>`
  shows as typed.

## Honest limits

- **Ticks are per browser.** Another device, or a cleared browser, starts from zero.
- **It reflects the conversation, not the world.** It doesn't re-check menu paths or
  values online; if the conversation was wrong, the runbook is too. It says so when
  something looks off, once.
- **An edit keeps ticks attached only if ids are kept.** The validator's `--previous`
  check enforces it, and it only runs if the agent runs it.

## Layout

```
make-it-runbook/
├── SKILL.md                     the workflow (what Claude reads on trigger)
├── references/
│   ├── distill.md               conversation → final agreed steps
│   └── runbook-schema.md        the runbook.json contract and id rules
├── scripts/
│   ├── validate_runbook.py      errors + warnings, --previous for republishes
│   └── render_page.py           runbook.json → self-contained HTML
├── assets/runbook-template.html
├── evals/
│   ├── evals.json               five acceptance scenarios
│   ├── fixture-conversation.md  a messy setup chat with its traps listed
│   └── expected-runbook.json    the runbook it should produce
└── icon.svg
```

## Testing

Checked locally:

- The validator passes `evals/expected-runbook.json`, and rejects a file seeded with each
  error class: duplicate, malformed or retired ids, a wait blocking an earlier or unknown
  step, an empty note or value, a bad key, no steps. On republish it rejects a changed
  key, a revision that didn't go up, a vanished id that wasn't retired, and a retired id
  brought back.
- The page was screenshotted at 390px and 900px in light and dark, printed to PDF, and
  loaded with a hostile title and detail (`</script><img onerror=…>`), which rendered as
  text.
- Ticking persists across reloads, and the page still works with `localStorage` throwing.

The skill itself is tested with the scenarios in `evals/evals.json`. Run each in a fresh
Claude Desktop conversation with the skill enabled (for `superseded-advice`, paste the
fixture conversation first) and check the listed behaviours.
