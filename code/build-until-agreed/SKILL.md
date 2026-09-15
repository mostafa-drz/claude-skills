---
name: build-until-agreed
description: >-
  Builds toward a goal agreed up front, then has independent read-only auditors
  judge whether it is actually met — looping build → blind audit → verify →
  fix until the harness passes, no verified blocking finding remains, and more
  than half of the auditors agree the goal is met. Starts from the user's
  problem, not the feature: writes a short contract (who hurts, acceptance
  criteria, harness command, declared decisions, severity bar, round budget)
  before any code. Auditors never see each other, earlier rounds, or the
  builder's reasoning; every blocking finding is re-checked by a separate
  verifier before anything is fixed, so deliberate trade-offs and unreproducible
  claims don't drive churn. Keeps a per-round ledger, prefers cutting to adding,
  stops and hands back on thrash or the round cap, and can finish with an
  external review-bot gate. Never merges. Use for long-running or exploratory
  builds, boilerplates, or any change where "done" should be checked by someone
  other than the builder.
argument-hint: "[\"goal\"|resume|status|config|reset|help] [--auditors <n>] [--rounds <n>] [--bar poc|production] [--no-bot]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
  - Monitor
  - Bash(git *)
  - Bash(gh *)
  - Bash(rm ~/.claude/skills/build-until-agreed/preferences.md)
metadata:
  trigger: "Building toward a goal where done should be judged by independent auditors, not the builder — long-running or exploratory builds, boilerplates, POCs heading to a PR."
  tags: "coding, agents, review, quality, testing, automation"
---

# Build Until Agreed

The builder is the worst judge of whether the work is done. This skill writes down what
"done" means *before* building, then lets independent auditors decide — and checks their
claims before acting on them.

**Standing rules — they hold for the whole run, every round:**

1. **Problem first.** No contract without a named user and the pain it removes. If there
   isn't one, say so and stop — we don't build for the sake of building.
2. **Auditors are blind and read-only.** Fresh, **unnamed** subagent each round. They get
   the contract file, the commit range and the harness — never the ledger, the builder's
   reasoning, earlier findings, or each other's verdicts. Never use a `fork` subagent as an
   auditor: it inherits this context. Named subagents share a sibling roster and can message
   each other.
3. **Nothing is fixed until it is verified.** A blocking finding is a claim until a separate
   verifier reproduces it. Documented decisions are not defects.
4. **Freeze while auditing.** Commit before a round; no edits until every auditor returns.
5. **Prefer cutting to adding.** Before each fix, name what it protects. If nothing, cut.
6. **Never merge. Never push to the default branch.** Work on a branch; the human merges.
   This is enforced here, in the workflow — `Bash(git *)` does not enforce it.
7. **Explain progress.** After every round, print the round block (see
   `reference/contract-and-ledger.md`) so the user always knows where things stand and why.

## Preferences

_On startup, use Read to load `~/.claude/skills/build-until-agreed/preferences.md`. If it
is missing, use these defaults and show the first-run intro from
`reference/contract-and-ledger.md`. Write the file after the first completed round._

- `auditors`: 3 · `max-rounds`: 5 · `bar`: `poc` · `review-bot`: `greptile` or `off` (asked in the contract)
- `lenses`: `adopter`, `correctness`, `risk-and-simplicity` (defined in `reference/auditors.md`)
- `ledger-dir`: `.build-until-agreed/` in the target repo

Flags override for one run. `## Learned` holds trade-offs the user accepted in past runs;
offer them as Decisions when drafting a contract.

## Command routing

Check `$ARGUMENTS`:
- `help` → print the help block from `reference/contract-and-ledger.md`, stop
- `config` → one `AskUserQuestion` (auditors, max-rounds, bar, review-bot); save; stop
- `reset` → delete **only** the preferences file; contracts and ledgers in repos are project
  history and are never touched. Say exactly that. Stop
- `status` → find the newest ledger (below), print its last round block, stop
- `resume` → find the newest ledger, run Step 0, continue at the step in its `next` column
- anything else → the goal, in plain words. Empty → ask for it

**Finding a ledger.** Ledgers are committed on the feature branch, so look in
`{ledger-dir}` on the current branch first. If there is none, list branches that have one
(`git log --all --format=%D -- {ledger-dir}`) and ask which to use. Switching branches
follows Step 0's clean-tree rule.

## Step 0 — Safety and context

1. `git rev-parse --show-toplevel` — not a repo → stop and say why.
2. `git status --porcelain` — uncommitted changes → **stop and ask**. Never stash, reset or
   commit someone else's work.
3. Current branch is the default branch → create `feat/<slug>` before any write.
4. Read the repo's own conventions (CLAUDE.md, CONTRIBUTING, README, test/lint config). The
   harness should be *their* commands, not new ones.
5. Tell the user once: the harness and the auditors' read-only commands aren't pre-approved
   by this skill, so they'll prompt unless allowed for the session (e.g. the test command
   and `git diff`/`git log`).

## Step 1 — The contract

Draft `{ledger-dir}/<slug>.contract.md` from the template in
`reference/contract-and-ledger.md`: **Problem** (who, what hurts, why now) · **Goal** ·
**Acceptance criteria** (each one checkable) · **Harness** (commands that exit non-zero on
failure) · **Decisions & scope** (trade-offs auditors must not report as defects) · **Bar** ·
**Budget** · **Review bot**.

Confirm with one `AskUserQuestion` round (max 4 questions, headers ≤ 12 chars): criteria
right? · bar · budget · review bot at the end. Anything vague ("works well", "is secure")
gets rewritten as something a stranger could check. Create the empty
`{ledger-dir}/<slug>.ledger.md` alongside it (with the branch name), and commit both:
`docs(agreed): contract for <slug>`.

**The bar decides what blocks.** `poc`: only HIGH blocks; MEDIUMs are listed and accepted.
`production`: HIGH **and** MEDIUM block, and both go through verification.

## Step 2 — Build an increment

Build the smallest slice that moves an acceptance criterion. Run the harness. Commit small
and conventional. A slice is ready for audit when the harness passes locally or the
remaining failure is itself the thing to audit.

## Step 3 — Blind audit round

1. Commit everything. Record `HEAD` as the audit SHA.
2. Spawn `auditors` subagents **in one message** (parallel), `subagent_type:
   general-purpose`, unnamed, each with a different lens, using the auditor prompt in
   `reference/auditors.md`. Pass the contract path (never the ledger), the base..audit SHA
   range, and the harness — nothing else.
3. Wait for all of them. Do not edit meanwhile.
4. Check `git rev-parse HEAD` and `git status --porcelain --untracked-files=no` (build output
   from the harness is not a write). If either changed, the round is void: discard **every**
   verdict from it, report what changed, and ask before touching the tree.
5. Parse each report's last line: `VERDICT goal_met=<yes|no> high=<n> medium=<n>`. A report
   without it is incomplete — `SendMessage` that auditor once for the line, else count it as `no`.

## Step 4 — Verify before fixing

1. Collect the **blocking** findings for the bar (Step 1). Merge duplicates (same file or
   behaviour) across auditors; keep every auditor's evidence.
2. For each, spawn one unnamed verifier (parallel) with the verifier prompt in
   `reference/auditors.md`. It gets the finding, the contract, the SHA — not the auditor's
   identity or vote.
3. Each returns `CONFIRMED`, `REFUTED`, or `DECISION` (it matches a documented decision).
   Only `CONFIRMED` findings block.
4. Non-blocking findings are not verified or auto-fixed. List them in the round block.

## Step 5 — Decide

Run the harness yourself at the audit SHA. "Majority" means **more than half** of the
auditors whose reports counted.

| Harness | Confirmed blocking | Majority `goal_met=yes` | → |
|---|---|---|---|
| pass | 0 | yes | **Agreed.** Go to Step 6 |
| pass | 0 | no | Read the `no` reasons. A missing criterion → Step 2. Disagreement about the goal itself → ask the user |
| any | > 0 | any | Fix confirmed findings (rule 5), re-run harness, commit, next round |
| fail | 0 | any | Fix the harness failure, next round |

**Stop and hand back to the user** — don't grind — when:
- the round cap is reached;
- a finding confirmed in an earlier round (its title is in the ledger) is confirmed again
  after its fix (thrash);
- a finding can only be resolved by a scope decision → ask, then record it under Decisions
  in the contract and commit before the next round;
- auditors keep reporting a trade-off the user already accepted → add it to Decisions and
  offer to save it to `## Learned`.

After every round, including the last: append a ledger row (with one-line titles of each
confirmed finding, and `next` as a step name) and print the round block.

## Step 6 — Optional review-bot gate

Only if the contract says `greptile` and the user agrees. Pushing a branch and opening a PR
is outward-facing: confirm first, and never target or push the default branch.

Follow `reference/review-bot.md`. The PR body is the final block from
`reference/contract-and-ledger.md` plus links to the contract and ledger. Bot findings go
through **Step 4** like any auditor's. Any commit after a score makes it stale.

## Step 7 — Report

Print the final block from `reference/contract-and-ledger.md`. State the honest limit:
auditors on the same model make correlated mistakes, so "agreed" means *checked*, not
*proven* — the harness and the human review are still the real gates. End with: "The merge
is yours."
