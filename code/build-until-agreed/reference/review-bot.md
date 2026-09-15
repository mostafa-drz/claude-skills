# Review-bot gate (Step 6)

Optional. Runs **after** the internal loop agrees, never instead of it. Written for
Greptile; any bot that posts a score on the PR fits the same shape.

1. **PR.** Confirm with the user before `git push` or `gh pr create` — both publish. Push
   the feature branch only; refuse if it is the default branch. Reuse an open PR for the
   branch (`gh pr view --json number,url`) rather than opening a second.
2. **Wait.** Watch for the bot's review with `Monitor` (poll `gh pr view <n> --json
   reviews,comments` about every 30s; foreground `sleep` is blocked). After ~8 minutes of
   silence, comment `@greptileai review` once. After ~30 minutes, hand back — the bot may
   not be installed on the repo.
3. **Score.** Greptile writes `Confidence Score: <n>/5` in its summary. Record the score
   **and the SHA it reviewed**. Any later commit makes it stale: re-trigger before quoting it.
4. **Findings.** Treat the bot as one more auditor: its blocking comments go through Step 4
   verification; fix confirmed ones (prefer cutting), re-run the harness, commit. If the bot
   only re-scores after replies, reply on each thread with the fix commit or why it was
   refuted — replies are public, so keep them factual.
5. **Stop.** The contract's target score on the current HEAD → report it. The same finding back after a
   fix, or two re-triggers without movement → hand back with the open threads listed.
   **Never merge**, whatever the score.
