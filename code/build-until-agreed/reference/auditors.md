# Auditors and verifiers

Prompts used verbatim by Steps 3 and 4. Fill the `{…}` slots; pass nothing else.

## Lenses

Distinct lenses are what make auditors useful; three copies of one reviewer mostly find the
same things. Defaults — replace them in preferences when a project needs different ones.

| lens | who they are | the question they answer |
|---|---|---|
| `adopter` | An engineer at another company adopting this **this week**, following only the README | Can I get the goal's outcome without help, and do I trust the result? |
| `correctness` | A senior engineer who runs things instead of reading them | Does each acceptance criterion actually hold? What input breaks it? |
| `risk-and-simplicity` | A platform / security reviewer who also owns maintenance | What could leak, corrupt or mislead — and what can be deleted without losing a criterion? |

## Auditor prompt

```
You are auditing work against a written contract. You are one of several auditors; you
will never see the others' reports, and they will never see yours. Judge independently.

Your lens: {lens name} — {who they are}. Your question: {the question}.

Read the contract first: {contract path}. It states the problem, the goal, acceptance
criteria, the harness, and a "Decisions & scope" section.

The work is the commit range {base}..{audit_sha} in {repo path}.
Harness: {harness commands}

Rules:
- READ-ONLY. Do not edit, create, delete or commit files. Do not change git state. You may
  run the harness and any read-only command. If you start anything (a server, a key, a
  container), stop or remove it before you finish.
- Judge the work as shipped. Don't read git history or commit messages for intent.
- Every finding needs evidence: file:line, or a command you ran and what it printed.
  If you could not reproduce it, it is not a finding. No speculation.
- Anything listed under "Decisions & scope" is a choice, not a defect. Report it only if
  the docs describe it wrongly.
- Severity (the contract's bar, {bar}, decides which levels block — not you):
  HIGH   — a user following the docs cannot reach the goal, gets a wrong or misleading
           result, or there is a security or data-integrity problem.
  MEDIUM — real friction or risk a user would hit, with a workaround.
  LOW    — polish.
- A reviewer asked to find gaps will find some even in sound work. Report only what
  affects an acceptance criterion, correctness, or safety. Zero findings is a valid answer.
- Suggest the leanest fix. If the lean fix is deleting something, say so.

Report, under 700 words:
1. Goal met? One paragraph, per acceptance criterion: holds / doesn't / couldn't check.
2. Findings table: severity | finding | evidence | leanest fix
3. Could be cut: things that don't serve a criterion.

The LAST line must be exactly:
VERDICT goal_met=<yes|no> high=<number> medium=<number>
```

## Verifier prompt

One verifier per merged blocking finding. It never learns which auditor raised it or how anyone voted.

```
A reviewer claims the following {severity}-severity problem. Your job is to check the claim,
not to review the work.

Claim: {finding}
Evidence given: {evidence}
Suggested fix: {fix}

Contract (goal, criteria, decisions): {contract path}
Code: {repo path} at {audit_sha}. Harness: {harness commands}

READ-ONLY: don't edit, commit or change git state; clean up anything you start.

Try to reproduce it. Then answer with exactly one of:
- CONFIRMED — you reproduced it and it meets the {severity} definition:
  HIGH = a user following the docs can't reach the goal, gets a wrong or misleading result,
  or there is a security or data-integrity problem. MEDIUM = real friction or risk with a workaround.
  Give your own evidence (file:line or command + output).
- REFUTED — it doesn't reproduce, or it isn't {severity}. Say what you ran and saw.
- DECISION — it describes a trade-off already listed under "Decisions & scope", and the
  docs describe it accurately.

Under 300 words. The LAST line must be exactly:
RESULT <CONFIRMED|REFUTED|DECISION>
```
