---
name: make-it-runbook
description: >-
  Turns the current conversation into a trackable, phase-by-phase runbook: a page with a
  checkbox per step, a progress bar, amber bars for forced waits, notes for warnings, and
  copyable literal values (commands, DNS records, amounts). Distills the chat first, so
  only the final agreed state survives: advice that was later corrected, changed values
  and tangents are dropped, steps run in real execution order, and each wait sits where it
  actually blocks. Ticks persist in the browser; prints to PDF with empty boxes. Use when
  the user says "make it a runbook", "/make-it-runbook", "turn this into a checklist I can
  track", "give me a step-by-step I can follow", "make this trackable", or wants setup
  steps, a migration or any multi-step plan discussed in the chat as something to work
  through. Not for a plain answer, a to-do app, or a project or team task tracker.
metadata:
  side_effects: false
  trigger: "Saying 'make it a runbook' after working out a setup or plan in the chat, or asking for a checklist to track the steps discussed."
  tags: "runbook, checklist, setup, instructions, distillation, progress-tracking, html, pdf, desktop"
---

# Make it a runbook

You worked something out in the chat: an email setup, a migration, a move. The steps are
scattered across twenty messages, some were corrected halfway, and a couple of them have
to wait a day. This turns that into one page you can work through: tick as you go, come
back tomorrow, and never follow the advice that was later taken back.

In Claude Desktop and claude.ai the skill starts automatically on a matching request, with
no slash command. "Make it a runbook" is the natural trigger.

Two references, loaded when a step needs them:
[`distill.md`](./references/distill.md) (turning a messy conversation into the final agreed
steps: **read it every time**) · [`runbook-schema.md`](./references/runbook-schema.md) (the
data the page renders from, and the id rules).

---

## The flow

`conversation → distill → runbook.json → validate → page`. Copy this checklist into your
reply and tick it off, because the distillation is where a confident-looking runbook goes
wrong:

```
Runbook progress:
- [ ] 1. Distill: ledger → final agreed steps, execution order, waits, notes, literals
- [ ] 2. Ask only what blocks the shape (≤3 questions, defaults) or flag it on the step
- [ ] 3. Write runbook.json
- [ ] 4. Validate
- [ ] 5. Render and deliver
```

### 1. Distill

**This is the job; the page is the easy half.** Follow
[`distill.md`](./references/distill.md). The rules that matter most:

- **Read the whole conversation first**, including everything after the plan first looked
  done. Corrections come late.
- **The last agreed word wins.** A correction replaces, it doesn't add: when advice went
  from X to Y, only Y is in the runbook. A changed value is changed everywhere.
- **Execution order, not conversation order.** Every step comes after what it depends on.
- **A forced wait goes right after the step that starts its clock**, blocking the first
  step it holds up, and says what to do meanwhile.
- **Warnings and decisions are notes, not checkboxes. Tangents are dropped.**
- **Literal values are copied exactly**, character for character, into `values`. Never
  paraphrased, completed or invented.
- **Reorganise, don't re-advise.** Nothing goes in that the conversation didn't agree. A
  real problem you spot is raised once, in the closing lines.

Starting cold, with nothing discussed, isn't this skill's job. Say so in one line and offer
to work out the steps together first.

### 2. Ask, or flag

**Ask only when an open question changes the runbook's shape**, such as two different
routes with no decision. Then one round, at most three questions, each with a proposed
default, so "just go" answers them all. Ask in plain text, because a question tool may not
exist on this surface. **Never re-ask what the conversation already settled.**

Anything else still open gets built and flagged on its step: `confirm` says what to settle
first, and `optional: true` marks an "if you want" extra. Never silently include an
undecided step, and never silently drop one.

### 3. Write runbook.json

Shape and rules in [`runbook-schema.md`](./references/runbook-schema.md). In short: 3–8
phases, each with a `where` (the site, app or place it happens in), and an ordered list of
`step`, `wait` and `note` items. Steps are `s1 … sN` in document order. Pick a `key` slug
once; it never changes. The title is a name ("Harbor Pottery Email Runbook"), not a
sentence.

A step's `action` is the imperative, short enough to scan. The `detail` holds the exact
menu path, which option, and why it matters.

### 4. Validate

```bash
python3 scripts/validate_runbook.py runbook.json
```

It exits non-zero on errors, and each message names the item and the fix. **Fix and re-run
until it passes.** Read the warnings too. Standard library only, so no installs are needed.

### 5. Render and deliver

```bash
python3 scripts/render_page.py runbook.json runbook.html
```

Show `runbook.html` to the user as an HTML artifact. It's self-contained, works on a phone,
follows the system's light/dark setting, saves ticks in their browser, and has a **Print /
save PDF** button with a print layout (empty boxes, waits and notes kept, values wrapped).
If this surface can't display artifacts, share the file for download.

Then close in **three lines at most**: how many steps and phases, what was dropped as
superseded (one line, so the user can object), and anything flagged to confirm. Offer the
PDF in the same breath.

### PDF: only when asked

Use this environment's PDF capability to build a file with the same phases, empty boxes,
wait bars and notes as the page. If file creation isn't available, point to the page's
**Print / save PDF** button, whose print layout is built for this.

### Changing the runbook

When steps change after feedback, **edit runbook.json and re-render the same artifact**.
Never regenerate from scratch: unexplained changes elsewhere cost trust, and the ids are
what keep the user's ticks attached to the right steps.

1. Copy the current file to `runbook.prev.json` before editing.
2. **Keep every step's id**, even when it moves or is reworded. A new step gets a number
   above every id ever used, even in the middle of a phase. A removed step's id goes into
   `retired_ids` and is never reused. A step whose meaning changed is a removal plus a new
   step, because a tick on the old meaning isn't a tick on the new.
3. Add 1 to `revision`, then validate against the last delivery:
   `python3 scripts/validate_runbook.py runbook.json --previous runbook.prev.json`
4. Render, show the same artifact again, and state what changed in one or two lines.

---

## Honesty rules

- **Never invent a value, a menu path or a step** to make the runbook look complete. A gap
  shows as a gap, or as a `confirm`.
- **Never carry superseded advice.** When unsure which of two versions was final, it's an
  open question: ask or flag it, don't pick.
- **Don't check or change the facts silently.** The runbook reflects the conversation. If
  something looks wrong or out of date, say so once and let the user decide.
- **Ticks live in this browser only.** The page says so. Don't promise they sync.

## Privacy

A runbook often holds account names, domains and internal details. The artifact is private
unless the user shares it. When they ask to share it, say in one line what it contains.
Never put a password, token or secret in the runbook, even when one appeared in the
conversation: write where to get it instead, and say in the closing lines that you left it
out.

---

## Conventions

**`help`**: what this does (one sentence), how to trigger it ("make it a runbook"), and
the outputs (page, PDF on request).

**`config`**: defaults for this conversation, asked in one round: phase count preference,
default output. Desktop skills can't save settings between conversations. To make a
default permanent, edit **Configuration** below and re-upload the skill. Say so rather
than implying the choice will be remembered.

**`reset`**: drops this conversation's config and returns to the defaults below. It never
touches a runbook you already have or the ticks saved in your browser.

## Configuration

Edit these, re-zip and re-upload to change the defaults.

- phases: 3–8, as few as the work allows
- default output: HTML page
- PDF: only when asked

**Tone**: brief. One line to open, the runbook, three lines to close.
