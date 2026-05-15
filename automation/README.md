# Automation — Daily Skill Factory

This folder holds the routines that run **on Claude infrastructure** (not my laptop) and keep this repo alive on a daily cadence.

Today there is one routine:

| Routine | What it does | Spec |
|---|---|---|
| **Daily Skill Factory** | Every morning, researches one real-world workflow that a Claude Desktop skill can solve, builds the skill end-to-end (SKILL.md + SVG icon + README + index entries) in my voice, opens a PR here for review. The next morning, if the previous PR was merged, opens a follow-up PR on [`mostafa-xyz`](https://github.com/mostafa-drz/mostafa-xyz) with a short note announcing the skill. | [`daily-skill-routine.md`](./daily-skill-routine.md) |

## Why a spec, not just a cron prompt

The cron prompt is the trigger. The spec is the contract. Future agents (or future me) opening this repo cold can read the spec, understand exactly how the factory thinks, what the quality bar is, and how to change it — without having to reverse-engineer the cron settings.

When the routine changes, change the spec in a PR. The cron prompt should stay almost trivial — it just says "follow the spec in `automation/daily-skill-routine.md` from this commit, today's date is X."

## Where everything lives

```
automation/
├── README.md                    ← you are here
├── daily-skill-routine.md       ← the contract the routine follows
├── runs.md                      ← append-only log of every run (queryable history)
└── docs-cache/                  ← dated snapshots of upstream Claude Skills docs
    └── YYYY-MM-DD.md            ← one per run; what was true that morning
```

## How runs are tracked

Every run appends a row to [`runs.md`](./runs.md). Each row carries the date, the skill produced, the PR link, its status, and the corresponding mostafa-xyz announcement PR (if any). The routine reads yesterday's row at the start of each run to decide whether Phase A (sync to blog) should fire.

## How to change the routine

1. Edit [`daily-skill-routine.md`](./daily-skill-routine.md) on a branch.
2. Open a PR. Review like any other change.
3. On merge, the next cron firing picks it up automatically — the cron prompt always reads HEAD.

To change the schedule itself (time of day, cadence), update the remote routine via the `/schedule` skill locally — that's the only thing not version-controlled here, by design (it's a deployment concern, not a spec concern).

## Manual override

Want to trigger the factory now instead of waiting for tomorrow? Run the cron's underlying prompt locally — it's just markdown, it works the same way invoked by hand.
