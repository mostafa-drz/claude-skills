---
name: step-through
description: >-
  Walks the user through a long enumerated response (numbered findings, audit
  list, refactor plan, bug list, PR review, recommendations, action items)
  one item at a time. For each item, lets the user dive deeper, take action,
  defer, or skip — instead of staring at the whole wall of text. Learns the
  user's per-severity defaults from feedback. Use when an assistant has just
  produced a long list and the user says "let's go through these one by one",
  "step me through", "walk me through", "let's triage", "next item", or
  otherwise wants interactive per-item review of a previous response. Works
  on any enumerated content — not just PR reviews.
argument-hint: [--filter <severity>] [--from <hint>] [--start <n>]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Glob
  - Grep
  - Bash
  - Edit
  - Write
  - WebSearch
  - WebFetch
---

# /step-through

Take a long enumerated response and walk through it interactively, one item at a time, with a decision per item — and learn the user's per-severity habits over sessions.

## Preferences

_On startup, use the `Read` tool to load `~/.claude/skills/step-through/preferences.md`. If missing, treat as first-run (see First-time detection below)._

Defaults when no preferences exist:

- **default-depth:** `concise` — one paragraph plus 1–2 references on dive deeper
- **show-outline:** `yes` — print the outline before starting
- **persist-session-log:** `yes` — append decisions to `sessions/<date>.md`
- **auto-pick-source:** `most-recent` — most recent enumerated assistant message
- **action-confirmation:** `destructive-only` — confirm before file deletes / branch ops / pushes / external posts; everything else proceeds
- **resume-on-stop:** `yes` — when a session is stopped mid-way, save resume state so the next invocation can pick up where it left off
- **per-severity-defaults:** none yet (filled by Learned over time)

## Context

_Do NOT pre-load anything on startup. The skill works against the current conversation's recent assistant messages. Run Bash/Read only when the user picks "dive deeper" or "take action" on a specific item — at that point, fetch only what's needed for that item._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help, then stop
- **`config`** → interactive setup, then stop
- **`reset`** → delete `~/.claude/skills/step-through/preferences.md` AND `feedback-journal.md` AND `sessions/`, confirm, stop
- **`feedback`** → collect thumbs-up/down on the most recent walkthrough (see Feedback & learning), stop
- **`resume`** → continue the most recent stopped walkthrough using saved resume state, stop if none
- **anything else** (including empty) → run the skill

### Help

```
/step-through — Walk through a long enumerated response item-by-item

Usage:
  /step-through                    Walk through the most recent enumerated response
  /step-through --filter blockers  Only walk through items in that section/severity
  /step-through --start 3          Resume from item N
  /step-through --from "<hint>"    Pick a different message by short description
  /step-through resume             Continue the most recent stopped walkthrough
  /step-through feedback           Rate the last walkthrough (improves future defaults)
  /step-through config             Set preferences
  /step-through reset              Clear preferences + feedback journal + sessions
  /step-through help               This help

Per-item options:
  Dive deeper        Pull code / docs / context to better understand
  Take action        Edit, run, research, or fix right now
  Note & defer       Capture decision (e.g. "address with AIS-XXXX"), move on
  Skip               Drop without action
  Stop               End the walkthrough, summarise

Examples:
  /step-through                              After a long PR review
  /step-through --filter blockers            Only critical items
  /step-through --start 7                    Resume mid-list

Current preferences:
  (loaded from ~/.claude/skills/step-through/preferences.md)
```

### Config

Use `AskUserQuestion` to collect 5 preferences in one batch:

1. **Default depth on Dive deeper** — `concise` (one paragraph + 1–2 refs) vs `thorough` (open files, web, full context)
2. **Show outline first** — `yes, always show outline` vs `skip, jump to item 1`
3. **Persist session log** — `yes, write to sessions/<date>.md` vs `no, summary in chat only`
4. **Source selection** — `auto: most-recent enumerated message` vs `always ask which message`
5. **Confirmation policy on Take action** — `destructive only` (file deletes, pushes, external posts) vs `every action` (confirm any edit/command)

Save to `~/.claude/skills/step-through/preferences.md` in this format:

```markdown
# /step-through preferences
Updated: YYYY-MM-DD

## Defaults
- default-depth: concise
- show-outline: yes
- persist-session-log: yes
- auto-pick-source: most-recent
- action-confirmation: destructive-only
- resume-on-stop: yes

## Profile (optional — edit freely)
- preferred severity to start with: blockers
- usual filter: none
- typical action style: minimal-edit, prefer linking a Linear ticket over inline fix

## Learned
- (populated by feedback over time — e.g. "follow-up severity → defer by default")
```

After save, print a one-line summary: `Saved. /step-through will use these defaults from now on.`

### Reset

Delete:
- `~/.claude/skills/step-through/preferences.md`
- `~/.claude/skills/step-through/feedback-journal.md`
- `~/.claude/skills/step-through/sessions/` (entire directory if exists)
- `~/.claude/skills/step-through/resume-state.md` (if exists)

Confirm: `All cleared. Starting fresh next time.`

## First-time detection

If no preferences file exists, show a warm one-liner (do not block):

> First time using `/step-through`? I'll walk you through the most recent long response one item at a time. After your first walkthrough, run `/step-through feedback` so I can learn your defaults. Or run `/step-through config` first to tune behaviour.

Then proceed with defaults.

---

## Workflow

### Step 0 — Load learning context

Before anything else:

1. Read `preferences.md` — carry **Defaults**, **Profile**, and **Learned** forward into the session.
2. Read `feedback-journal.md` if it exists — scan for any "Signal" lines that match the current source (e.g. severity terminology, source style). These quietly bias the per-item pre-selection in step 4b.
3. If `--filter`, `--start`, or `--from` are present in `$ARGUMENTS`, parse them now.

If any file fails to read, continue silently with defaults — never block on missing learning state.

### Step 1 — Locate the source response

Default behaviour: **the most recent assistant message in this conversation that contains an enumerated list.** Look for any of:

- Numbered items (`1.`, `2.`, …) at line start
- Markdown bullets at the same indent level (3 or more)
- Section headers like `### N. Something` or `🔴 Blockers` / `🟠 Major` / `🟡 Follow-up`
- Lists under headings like "Findings", "Issues", "Recommendations", "Items", "Tasks", "Next steps"

If `--from "<hint>"` is set, scan back for an assistant message whose contents loosely match the hint (substring or theme) and use that.

If preference `auto-pick-source` is `always-ask`, list up to 3 candidate messages with one-line summaries and ask which one to use.

If nothing enumerable is found in recent context: stop and tell the user — `I can't see a long enumerated response in this conversation. Paste it, or tell me which message to use.` Do **not** fabricate items.

### Step 2 — Parse items

Extract a structured list. For each item capture:

- `index` — 1-based position in the list
- `severity` — if the source uses sections like Blockers / Major / Follow-up / Nice-to-have, capture the section as severity. Otherwise leave blank.
- `title` — short label (first line / heading)
- `body` — the full text of the item (verbatim, do not paraphrase)
- `references` — any `path/to/file.ts:LN` citations, URLs, or doc links found in the body

If `--filter <severity>` is passed (e.g. `blockers`, `major`, `follow-up`), keep only matching items. Match case-insensitively against the section the item came from.

If `--start <n>` is passed, drop items with `index < n`.

### Step 3 — Show the outline (unless preference says skip)

Print a single compact outline so the user knows the scope:

```
14 items found in the last response. Walking through:
  1. [BLOCKER] Client Sentry init missing environment + release
  2. [BLOCKER] global-error.tsx was deleted
  3. [BLOCKER] Triple Sentry ingestion via structuredLog
  …
```

Titles only — never reproduce the full bodies here. Then say one line: `Starting with item 1.` and move on (no permission prompt — the user invoked the skill).

### Step 4 — Per-item loop

For **each item in order**:

#### 4a. Present the item

Print the item exactly as it appeared in the source response — verbatim body, references included. Add one header line:

```
Item N of M — [SEVERITY] — Title
```

Do **not** rewrite, summarise, or "improve" the item text on first presentation. The user already chose to walk through this content as-is.

#### 4b. Ask what to do — single AskUserQuestion

Use `AskUserQuestion` with these 5 fixed options (in this order):

1. **Dive deeper** — pull supporting context (read referenced files, fetch docs, web search)
2. **Take action** — fix it / run a command / draft a change right now
3. **Note & defer** — capture a one-line decision and move on
4. **Skip** — drop without action
5. **Stop** — end the walkthrough early and summarise

Header: `Item N of M`.

**Pre-selection logic** (apply in priority order, top wins):
1. If preferences `Learned` has a per-severity rule matching this item's severity, pre-select that.
2. Else if the item has file/URL references, pre-select **Dive deeper**.
3. Else pre-select **Note & defer**.

#### 4c. Execute the choice

- **Dive deeper:**
  - Pull every referenced file/path. Use `Read` for paths, `Bash(git *)` for blame/log if relevant, `WebFetch` for URLs in the item, `Grep`/`Glob` for symbol lookups.
  - Respect the user's `default-depth` preference (concise vs thorough).
  - After presenting findings, ask the user **the same 5 options again** for this item — they may now want to take action, defer, or skip.

- **Take action:**
  - Use the smallest set of tools needed: `Edit`/`Write` for code, `Bash` for commands, `WebSearch`/`WebFetch` for verification.
  - Confirmation: if `action-confirmation: every`, confirm in chat before any edit/command. If `destructive-only`, confirm only before file deletes, branch operations, pushes, or external posts. Auto mode does **not** bypass destructive-only confirmation.
  - After the action, briefly state what was done in 1–3 lines, then move to the next item without asking again. Do not loop on the same item.

- **Note & defer:** ask one short follow-up — `Note?` — capture the user's reply (or accept empty) and move on.

- **Skip:** record as skipped, move on.

- **Stop:** break the loop, jump to step 5. If `resume-on-stop: yes`, write resume state (see step 6) before summarising.

#### 4d. Track the decision

Maintain an in-memory record per item:

```
{ index, severity, title, decision: "deeper|action|defer|skip", note?: string, action_summary?: string }
```

If `persist-session-log: yes`, also append to `~/.claude/skills/step-through/sessions/YYYY-MM-DD-HHMM.md` after each decision (incremental write, not at the end). Header line on first write should include the source — message hash, date, and total item count.

### Step 5 — Final summary

When the loop ends (all items processed, or user picked Stop), print one compact block:

```
Walkthrough complete — N items.

  Action taken:   [list of indices + 1-line action summaries]
  Deferred:       [indices + notes]
  Skipped:        [indices]
  Not reached:    [indices, if Stop was used]
```

Then ask **one** follow-up question via `AskUserQuestion`:

- **Open a Linear ticket for deferred items?** (only if any deferred)
- **Open a PR for action-taken items?** (only if files were edited)
- **Done** — exit cleanly.

Do not auto-create tickets/PRs without explicit confirmation.

### Step 6 — Save resume state (only if Stop was used)

If the user picked Stop and `resume-on-stop: yes`, write `~/.claude/skills/step-through/resume-state.md` with: source identifier, processed indices, remaining indices, decisions so far. Tell the user: `Run /step-through resume to continue from item N.`

If the loop completed normally, delete any stale `resume-state.md`.

### Step 7 — Invite feedback

End with one short line:

> When you're done, run `/step-through feedback` — even one rating helps me sharpen per-severity defaults for next time.

Do not ask interactively here. Feedback is opt-in via the dedicated subcommand.

---

## Feedback & learning

When invoked as `/step-through feedback`:

1. Find the most recent session log (`sessions/YYYY-MM-DD-HHMM.md`). If none, say `No recent walkthrough found.` and stop.
2. Print a one-line summary of that session (item counts by decision).
3. Ask via `AskUserQuestion` (4 questions, one batch):
   - **Did the per-item flow feel right?** — `yes, smooth` / `too slow` / `too fast` / `wrong defaults`
   - **Which decisions felt wrong, if any?** — free text (item indices + what should have happened)
   - **For follow-up severity items, what's your usual call?** — `defer by default` / `skip by default` / `dive deeper first` / `varies`
   - **For blocker severity items, what's your usual call?** — `dive deeper first` / `take action immediately` / `defer with ticket` / `varies`
4. Append to `~/.claude/skills/step-through/feedback-journal.md`:

```markdown
## {session slug} — {date}
- Pace: {smooth|too-slow|too-fast|wrong-defaults}
- Wrong calls: {indices + user text}
- Follow-up default: {answer}
- Blocker default: {answer}
- Signal: {one-line generalization, e.g. "user defers all follow-ups, dives deeper on blockers"}
```

5. **Promotion rule:** when 3+ sessions show a consistent answer for the same severity, promote it to `## Learned` in `preferences.md` as a rule like `follow-up severity → defer by default`. Mention once: `Noticed you consistently defer follow-up items. Saved as standing default.` These rules feed step 4b's pre-selection.

6. **Drift correction:** if a Learned rule is contradicted in 2 newer sessions, demote it (remove from Learned, log in journal as `## Demoted: {rule} — too unstable`). Never leave stale rules.

---

## Principles

1. **Preserve the source.** Show item bodies verbatim on first presentation. The user trusts the original wording — don't paraphrase, condense, or "improve" it.
2. **One decision at a time.** Never batch decisions across multiple items, never ask "should I handle 1, 2, and 5?". Single item, single question, single action.
3. **The skill orchestrates — it doesn't review.** Not a re-review of the source. No new findings, severity downgrades, or "your reviewer was wrong about #6" commentary. The user owns judgement; the skill provides flow.
4. **No fabricated structure.** If the source response isn't actually enumerated, stop and ask — don't invent items.
5. **Destructive actions still need confirmation.** `disable-model-invocation: true` makes the skill user-triggered, but file deletes, branch ops, pushes, and external posts always require an explicit yes — auto mode does not bypass that.
6. **Stop means stop.** When the user picks Stop, do not continue any in-flight per-item work. Skip to the summary, save resume state.
7. **Learn quietly.** Promote a rule only after 3+ consistent feedback signals. Mention once when promoting, never lecture. Demote unstable rules instead of accumulating clutter.
8. **Graceful degradation.** If `preferences.md` or `feedback-journal.md` can't be read, continue with built-in defaults — never block on missing learning state.
