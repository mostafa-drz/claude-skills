# /build-until-agreed

Build toward a goal you agreed on up front, and let independent auditors — not the builder
— decide when it's done.

> **Status: draft (v0).** The design comes from one real run and published research, both
> below. It hasn't been run end to end as a skill yet. Treat the defaults as starting points.

## The problem

When an agent works for hours, "done" gets decided by the one party least able to judge it:
the agent that did the work. Agents rate their own output generously. Adding a reviewer
helps, but a reviewer asked to find gaps will always find some — and chasing every one turns
a lean project into an over-engineered one.

This came out of building [tokens-per-ticket](https://github.com/mostafa-drz/tokens-per-ticket):
ten rounds of two independent reviewers, run until neither reported a high-severity problem.
It worked. It also showed exactly where a naive review loop wastes time:

| what happened | how this skill handles it |
|---|---|
| Reviewers flagged deliberate scope choices as HIGH, round after round | The contract has a **Decisions & scope** section; auditors are told those aren't defects, and verifiers return `DECISION` for them |
| About a third of the fixes were added, then cut in a later round because they protected nothing | Every blocking finding is **verified** before it's fixed, and each fix must name what it protects — otherwise it's cut |
| Fixes landed while one reviewer was still reading, so it judged a moving target | **Freeze**: commit before a round, no edits until all auditors return, and the tree is re-checked afterwards |
| Reviewers with write access fixed the same bug on parallel branches and conflicted | Auditors and verifiers are **read-only**; one orchestrator fixes |
| Reports got truncated and lost their verdict | Word cap plus a fixed last line: `VERDICT goal_met=… high=…` |
| The external bot's 5/5 went stale after 70 more commits | The review-bot gate records the **SHA** each score belongs to and re-triggers after new commits |
| Round history was lost to context compaction | The **ledger** is a file on disk that `resume` reads. It's git-ignored, so it never lands in the commit range auditors read, or in your PR |

## How it works

```
contract ──► build a slice ──► freeze ──► N blind auditors (parallel, read-only)
   ▲                                              │
   │                                  verify each blocking finding (separate verifier)
   │                                              │
   └──── fix confirmed / cut ◄── decide: harness pass · 0 confirmed blocking · >half say goal met?
                                                  │ yes
                                         optional review-bot gate ──► report (never merge)
```

1. **Contract.** Who hurts, what hurts, why now, checkable acceptance criteria, the harness
   command, declared decisions, a bar (`poc` or `production`), and a round budget. No
   problem, no contract — the skill won't build for the sake of building.
2. **Build** the smallest slice that moves a criterion.
3. **Blind audit.** Three auditors by default, each with a different lens — *adopter*,
   *correctness*, *risk & simplicity*. They get the contract, the diff and the harness, and
   nothing else. They never see each other or the ledger of earlier rounds.
4. **Verify.** Each blocking finding goes to a fresh verifier that tries to reproduce it:
   `CONFIRMED`, `REFUTED`, or `DECISION`. Only confirmed ones get fixed. What blocks depends
   on the bar: `poc` blocks on HIGH only; `production` blocks on HIGH and MEDIUM.
5. **Decide.** Agreed when the harness passes, nothing confirmed still blocks, and more than
   half the auditors say the goal is met. It hands back to you on the round cap, on thrash,
   or when a finding needs a scope decision only you can make.
6. **Review bot** (optional). Greptile or similar, as a final gate whose findings go through
   the same verification.

After every round it prints a short block: what passed, what was raised, confirmed, refuted,
fixed, cut, and why the loop continues.

## Why not debate?

The note this started from said "debate and consensus". The evidence points the other way:

- Agents that see each other's reasoning drift toward agreement, even onto wrong answers
  ([arXiv 2509.05396](https://arxiv.org/abs/2509.05396)); most of the gain credited to
  debate comes from plain majority voting ([arXiv 2508.17536](https://arxiv.org/abs/2508.17536), NeurIPS 2025).
- So auditors vote **blind**, and the only thing that happens between them is verification.
  The same pattern — parallel reviewers, then one validator per issue — runs in Anthropic's
  own [`code-review` plugin](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md).
- Keeping the builder and the judge separate, with "done" agreed before any code, is what
  Anthropic found made long builds hold up
  ([harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)).

**The honest limit:** auditors running on the same model make correlated mistakes
([arXiv 2506.07962](https://arxiv.org/abs/2506.07962)), so three agreeing auditors are not
three independent proofs. Blindness is also partly instructed rather than enforced: what
auditors are *given* holds no past rounds, but a determined agent could still browse the
disk. That's why the real harness and the verifier carry the weight, the vote is only a
sanity check, and the human still reviews and merges.

## What already exists, and the gap

- [`/goal`](https://code.claude.com/docs/en/goal.md) and the
  [Ralph Wiggum plugin](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)
  keep a session going until a condition holds. The judge is one model reading the
  transcript, or a completion promise.
- The `code-review` plugin gives you independent, validated review of a diff, but it
  doesn't loop and has no goal.
- Community review loops iterate until a review comes back clean.

The gap this fills is **goal-anchored** review. The contract is written before the build,
auditors judge "is the goal met, with evidence", deliberate trade-offs are protected, and a
local ledger explains every round. If `/goal` plus `code-review` is enough for your
task, use them — they're lighter. Rule of thumb: a change that fits in one session and
already has a test suite that defines "done" → `/goal`. A multi-session build, a new
boilerplate, or anything where "done" includes *would someone else adopt this* → this skill.

## Install

```bash
git clone https://github.com/mostafa-drz/claude-skills.git
cp -r claude-skills/code/build-until-agreed ~/.claude/skills/
```

```
/build-until-agreed "CSV import that never silently drops rows" --bar production
/build-until-agreed status
/build-until-agreed resume
```

## Cost

Agents per round with the defaults: **3 auditors + 1 verifier per blocking finding**, for up
to 5 rounds — so a run that needs three rounds with two blocking findings each spawns about
15 agents. At `--bar production` MEDIUMs are verified too, so expect more verifiers. The round
block prints the running count. The run this skill came from used 2
reviewers for 10 rounds over about three hours. Start with `--rounds 3` on a small goal.

The skill's tool grant lasts only until your next message, and it never covers your test
command. After the contract questions, expect prompts for `git`, `gh`, the harness and the
auditors' commands unless you allow them for the session.

## Safety

- Stops if the working tree has uncommitted changes. Never stashes or resets your work.
- Works on a feature branch. Never pushes to the default branch and **never merges**.
- Asks before pushing or opening a PR.
- `reset` clears preferences only. Contracts and ledgers stay.
- The contract is committed to the branch under `.build-until-agreed/`; keep it or remove it
  before merging — your call. The ledger is git-ignored and stays local.
