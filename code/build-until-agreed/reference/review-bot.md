# Review-bot gate (Step 6)

Optional. Runs **after** the internal loop agrees, never instead of it. Written for
Greptile; other bots that post a score on the PR fit the same shape.

## 1. Open or reuse the PR

- Confirm with the user before `git push` or `gh pr create` — both publish.
- Push the feature branch only. Refuse if the branch is the default branch.
- Reuse an open PR for the branch (`gh pr view --json number,url`) instead of opening a
  second one. The PR body gets the final block from `contract-and-ledger.md` and a link to
  the ledger file.

## 2. Wait for the review

- Poll reviews and comments (`gh pr view <n> --json reviews,comments`) every ~30s.
- After ~8 minutes with no bot activity, comment `@greptileai review` once.
- After ~30 minutes, stop waiting and hand back: the bot may not be installed on the repo.

## 3. Read the score

- Greptile writes `Confidence Score: <n>/5` in its summary. Record the score **and the SHA
  it reviewed**.
- A score only describes the SHA it saw. Any later commit makes it stale: re-trigger and
  re-read before quoting it.

## 4. Route findings through verification

Treat the bot as one more auditor:
1. Collect its inline comments. Anything it marks as blocking (P0/P1) is a HIGH candidate.
2. Send each HIGH candidate through **Step 4** verification like any auditor finding.
3. Fix confirmed ones (rule 5: prefer cutting), re-run the harness, commit.
4. Reply on each thread with the fix commit, or why it was refuted or is a documented
   decision. Replies are public: keep them factual.
5. Bot fixes can break what the auditors agreed on. If the fixes touched more than a line
   or two, run one more blind audit round before re-triggering the bot.

## 5. Stop

- Target score reached on the current HEAD → report it.
- Same finding back after a fix, or two re-triggers without movement → hand back with the
  open threads listed.
- **Never merge**, whatever the score.
