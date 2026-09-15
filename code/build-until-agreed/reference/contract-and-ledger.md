# Contract, ledger and output blocks

Two files per goal, both committed in the target repo so they survive context compaction:

- `{ledger-dir}/<slug>.contract.md` — what auditors read. Nothing about past rounds.
- `{ledger-dir}/<slug>.ledger.md` — round history for the user, `status` and `resume`.
  **Never passed to auditors or verifiers**: it holds votes and findings that would anchor them.

## Contents
1. Contract and ledger templates
2. Round block (printed after every round)
3. Final block
4. Help
5. First-run intro

## 1. Templates

### `<slug>.contract.md`

~~~markdown
# <Goal, in a few words>

## Problem
- **Who:** <the person who hurts — a role, not "users">
- **What hurts today:** <the concrete pain, ideally observed>
- **Why now:** <what makes it worth building now>

## Goal
<One or two sentences: the outcome, from that person's point of view.>

## Acceptance criteria
- [ ] <checkable by a stranger — a command, an observable result, a number>
- [ ] …

## Harness
```bash
<commands that exit non-zero on failure — the repo's own test/lint/typecheck/smoke>
```

## Decisions & scope
<!-- Choices, not defects. Auditors are told not to report these. Add to it whenever the
     user accepts a trade-off during the loop. -->
- <decision> — <why>

## Bar & budget
- **Bar:** poc | production   (poc: only HIGH blocks · production: HIGH and MEDIUM block)
- **Auditors:** 3 · **Max rounds:** 5 · **Review bot:** greptile | off
~~~

### `<slug>.ledger.md`

~~~markdown
# Ledger — <goal>
Branch: feat/<slug>

| round | audit sha | harness | goal_met | blocking raised → confirmed | confirmed (titles) | fixed / cut | agents | next |
|---|---|---|---|---|---|---|---|---|
| 1 | abc1234 | pass | 1/3 | 4 → 2 | token leaks in logs; import drops last row | 2 fixed, 1 cut | 3 + 4 | Step 2 |

## Accepted (non-blocking)
- <finding> — accepted at bar `poc` on <date>
~~~

## 2. Round block

Printed after every round. Plain, short, and says *why* the loop continues or stops.

```
Round {n} of {max} — {verdict: continuing | agreed | handing back}
  Harness        {pass|fail}  ({command that failed, if any})
  Goal met       {yes}/{auditors} auditors   ({lens}: no — "{one-line reason}")
  Blocking       {raised} raised → {confirmed} confirmed · {refuted} refuted · {decision} were documented decisions
  Fixing         {short list, each with what it protects}
  Cutting        {short list, or —}
  Not blocking   {n} listed, not auto-fixed (bar: {bar})
  Agents         {auditors} auditors + {verifiers} verifiers this round · {total} so far
  Why next       {one sentence — e.g. "2 confirmed findings in the auth path; re-auditing after fixes"}
```

## 3. Final block

```
Agreed after {n} rounds — {branch}
  Criteria       {k}/{k} hold · harness passes at {sha}
  Blocking/round {r1} → {r2} → … → 0
  Agents         {total} spawned across {n} rounds
  Verified       {confirmed} confirmed · {refuted} refuted (would have been churn)
  Cut            {what was removed}
  Accepted       {n} non-blocking findings (see ledger) · {n} decisions recorded
  Review bot     {score} at {sha} | skipped
  PR             {url | none}

Auditors share a model, so their agreement means "checked", not "proven".
The merge is yours.
```

When handing back instead, replace the first line with `Handing back after round {n} —
{reason}` and end with the specific question the user needs to answer.

## 4. Help

```
build-until-agreed — Build toward an agreed goal; independent auditors decide when it's done

Usage:
  /build-until-agreed "<goal in plain words>"   Contract → build → blind audit → verify → repeat
  /build-until-agreed resume                    Continue from the newest ledger
  /build-until-agreed status                    Show the last round
  /build-until-agreed config                    Auditors, rounds, bar, review bot
  /build-until-agreed reset                     Clear preferences (ledgers are kept)
  /build-until-agreed help                      This help

Flags:
  --auditors <n>   Parallel auditors per round (default 3)
  --rounds <n>     Round budget before handing back (default 5)
  --bar poc|production
  --no-bot         Skip the review-bot gate

Examples:
  /build-until-agreed "a boilerplate that attributes AI token spend to Linear tickets"
  /build-until-agreed "CSV import that never silently drops rows" --bar production
```

## 5. First-run intro

```
First time running /build-until-agreed — here's the shape of it:

  Before any code, we write down who this is for, what "done" means, and the command
  that proves it. Then I build in small slices. Each round, a few auditors I can't
  influence look at the work — blind to each other and to my reasoning — and say
  whether the goal is met. Every serious finding gets checked by a separate verifier
  before I touch anything, so we fix real problems, not confident guesses.

  I stop when the checks pass and the auditors agree — or I hand back to you if we're
  going in circles. I never merge.

  Heads-up: each round runs several agents (by default 3 auditors plus one verifier per
  blocking finding), so it costs more than a normal session. Their read-only commands and
  your test command will ask for permission unless you allow them for this session.
```
