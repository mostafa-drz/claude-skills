# runbook.json

The one file the page renders from. Write it after distilling, run
`scripts/validate_runbook.py` on it, and only then render. Edits change this file, never
the HTML.

## Contents
- Shape
- Items: step, wait, note
- Inline text
- Ids: the rule that keeps saved progress honest
- What the validator checks

## Shape

```json
{
  "schema": 1,
  "key": "northwind-email-setup",
  "title": "Northwind Email Runbook",
  "subtitle": "Domains → DNS → mailboxes → authentication. The amber bars are forced waits.",
  "revision": 1,
  "generated_on": "2026-09-22",
  "retired_ids": [],
  "phases": [
    {
      "title": "Point the domain at the DNS host",
      "where": "registrar · dns host",
      "items": [
        { "type": "step", "id": "s1", "action": "Create the DNS host account",
          "detail": "Turn on 2FA before adding anything." },
        { "type": "step", "id": "s2", "action": "Add the MX record",
          "values": [ { "label": "MX", "text": "Type MX   Name @   Server mx.example.net   Priority 1" } ] },
        { "type": "wait", "duration": "24–72 h", "blocks": "s5",
          "text": "The provider won't issue a signing key until then. Start Phase 2 meanwhile." },
        { "type": "note", "title": "Pick one sending domain.",
          "text": "Outreach lives on `example-mail.com`; client mail never does." }
      ]
    }
  ],
  "footer": ["Domains: example.com (client-facing), example-mail.com (sending only)"]
}
```

| field | rule |
|---|---|
| `schema` | always `1` |
| `key` | lowercase slug, set once and **never changed**: saved progress is stored under it |
| `title` | a name, 2–5 words (`<Project> <Task> Runbook`), not a sentence |
| `subtitle` | one line: the route through the phases, and how to read the page |
| `revision` | `1` on first delivery, +1 on every republish |
| `generated_on` | ISO date of this revision |
| `retired_ids` | step ids that existed in an earlier revision and were removed. Never reused |
| `phases` | 1–12, usually 3–8, in execution order |
| `phase.where` | where the phase happens: a site, an app, a room ("admin console · dns host") |
| `footer` | optional lines of standing context (accounts, which domain is for what) |

## Items: step, wait, note

A phase's `items` is one ordered list, so a wait or a note sits exactly where it applies.

**step**: something the user does and can tick.

| field | rule |
|---|---|
| `id` | `s` + number, unique. See **Ids** |
| `action` | imperative, the thing to do, shown bold. Under ~90 characters |
| `detail` | optional. The specifics: menu path, which option, why it matters |
| `values` | optional list of `{label?, text}`: literal values to copy (records, commands, amounts). `text` is shown verbatim in monospace with a Copy button |
| `confirm` | optional. Set when the conversation left this step unresolved: what to confirm before doing it. Shown in amber |
| `optional` | optional `true` for steps agreed as "if you want". Shown with an *Optional* tag |

**wait**: a forced wait that blocks later steps. Not tickable.

| field | rule |
|---|---|
| `duration` | short chip text: `24–72 h`, `+48 h`, `~1 week` |
| `text` | one sentence: what's being waited for, and what to do meanwhile |
| `blocks` | optional. The id of the first step the wait blocks; must come later in the runbook |

**note**: a decision, warning or constraint that isn't an action.

| field | rule |
|---|---|
| `title` | optional bold lead-in |
| `text` | the note itself |

## Inline text

`action`, `detail`, note `text` and wait `text` support two marks, nothing else:
`` `code` `` for short literals inline, and `**bold**` for emphasis. Everything is rendered
as text, never as HTML, so `<` and `&` are safe. Anything long, or anything the user will
paste, goes in `values`, not inline.

## Ids: the rule that keeps saved progress honest

Ticked boxes are saved in the viewer's browser as `{id: true}` under `key`. The id is the
only link between a saved tick and a step, so:

- **First revision:** `s1 … sN` in document order.
- **A step keeps its id for life**, even when it moves, is reworded or changes phase.
- **A new step gets a new number above every id ever used**, including retired ones, even
  when it's inserted in the middle. `s24` between `s9` and `s10` is correct.
- **A removed step's id goes into `retired_ids`** and is never used again. Reusing it
  would show a different step as already done.
- **A step whose meaning changes** ("add the TXT record" → "add the CNAME record") is a
  removed step plus a new one, because a tick on the old meaning is not a tick on the new.

## What the validator checks

```bash
python3 scripts/validate_runbook.py runbook.json
python3 scripts/validate_runbook.py runbook.json --previous runbook.prev.json   # on republish
```

Errors (exit 1): missing or malformed fields, a duplicate or badly-formed id, an id listed
in `retired_ids` still in use, a wait that `blocks` an unknown or earlier step, an empty
note, a runbook with no steps. With `--previous`: a changed `key`, a revision that didn't
go up, a previous id that vanished without being retired, a new id not numbered above
every id ever used.

Warnings: fewer than 3 or more than 8 phases, a first revision whose ids aren't `s1…sN` in
order, a long `action`, a phase with more than 12 steps, an unmatched backtick.
