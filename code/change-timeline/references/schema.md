# timeline.json

The one input to the page. A complete, validated example built from this repository's real
history: [`../evals/example-timeline.json`](../evals/example-timeline.json).

```jsonc
{
  "version": 1,
  "title": "Auth rewrite and billing v2",          // what the range is about, not "Timeline"
  "subtitle": "One or two sentences: the shape of the range.",
  "repo": {
    "name": "owner/repo",
    "url": "https://github.com/owner/repo",
    "commit_url": "https://github.com/owner/repo/commit/{sha}"   // from collect.py; https + {sha}
  },
  "range": { "label": "main · Oct 1 – 26, 2026", "base": "v2.3.0", "head": "main",
             "from": "2026-10-01", "to": "2026-10-26" },
  "view": "timeline",            // timeline | lanes | chapters | walkthrough  (starting layout)
  "order": "newest",             // newest | oldest  (walkthrough always uses step order)
  "generated": "2026-10-26",
  "theme": { "mode": "dark", "density": "compact", "accent": "#ff6b3d" },  // the approved style
  "sources": ["git", "GitHub PRs", "reviews"],
  "stats": { "commits": 42, "prs": 9, "authors": 4, "additions": 3120, "deletions": 1480 },
  "areas":    [ { "key": "api", "label": "API" } ],
  "chapters": [ { "key": "v2.4.0", "title": "v2.4.0", "date": "2026-10-12",
                  "summary": "One sentence." } ],
  "items": [
    {
      "id": "session-cookies",                     // kebab-case, unique
      "title": "Session tokens move to httpOnly cookies",
      "type": "security",                          // feat fix refactor perf security docs test chore revert
      "area": "api",                               // a key in areas
      "chapter": "v2.4.0",                         // a key in chapters (optional)
      "date": "2026-10-24",                        // the day it landed (latest commit)
      "impact": "breaking",                        // optional: breaking | notable | minor
      "step": 3,                                   // optional: walkthrough order
      "what": "Tokens leave localStorage; the API sets and reads an httpOnly cookie.",
      "why": "localStorage tokens were readable by any injected script.",
      "why_inferred": false,                       // true → shown as Claude's reading
      "commits": [ { "sha": "<full 40-char sha>", "subject": "…", "author": "…",
                     "date": "2026-10-24", "additions": 120, "deletions": 40 } ],
      "prs": [ { "number": 142, "title": "…", "url": "https://github.com/owner/repo/pull/142",
                 "state": "merged" } ],
      "evidence": [ { "kind": "pr-body", "source": "PR #142",
                      "url": "https://github.com/owner/repo/pull/142",
                      "text": "The shortest verbatim sentence that proves the why." } ],
      "files": [ { "path": "src/auth/session.ts", "additions": 90, "deletions": 30 } ],
      "review": { "risk": "Clients on the old SDK lose their session on deploy.",
                  "check": ["Log in on SDK 3.x after deploy", "Cookie is SameSite=Lax"] }
    }
  ]
}
```

## The why, three ways

| situation | `why` | `why_inferred` | `evidence` | page shows |
|---|---|---|---|---|
| a source states the reason | the reason | `false` | ≥1 quote | the reason |
| you read it off the diff | your reading | `true` | optional (`kind: diff`) | the reason + **inferred** |
| nothing supports one | `null` | | | *Not stated in the PR or commits* |

## Rules the validator enforces

- ≥1 commit per item; every SHA hex, and with `--repo`, a real commit there.
- `why` without `why_inferred: true` needs ≥1 evidence quote.
- Every URL `https://`; `commit_url` contains `{sha}`.
- `area` and `chapter` resolve; `id` unique; `type`, `view`, `order`, `theme` from their
  enums; `theme.accent` a 6-digit hex.

Warnings (fix, but they don't block): abbreviated SHAs, a commit cited by two items, a
missing `why` key, a title over 90 characters, a walkthrough step with no `review`.

`files` is optional; keep the 4–8 with the most churn. `stats` covers the whole range,
including folded commits.
