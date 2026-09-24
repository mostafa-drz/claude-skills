# Choosing the one thing

Contents: [Gather](#gather) · [Pick](#pick) · [Write it](#write-it) · [Learning](#learning)

Everything here applies within the run's **area** (work, personal, health, family,
learning, a side project, or `all`). Only the area's sources are read, only the area's
candidates compete, and only the area's memory applies (plus lines tagged `all`).

## Gather

**Window:** today, plus anything due or happening before noon on the next working day. On
a Friday, that's Monday morning. Look back 7 days for threads and promises that are waiting
on the user. Older things count as context, not candidates, with two exceptions: memory
holds them as a standing goal, or, outside work, **a long silence is itself the signal**
("haven't called mum in three weeks").

Pull what signals *pressure* or *importance*, and skip the rest:

| source | pull | ignore |
|---|---|---|
| Calendar | today's events that need prep; deadlines; appointments to book or get to; birthdays; out-of-office and holidays (they make it an off day) | recurring meetings with nothing to prepare |
| Email | threads where someone asked for something and has no reply; dated asks; bills, renewals and forms with a due date | newsletters, notifications, plain receipts |
| Slack / Teams | direct asks and mentions with no answer; threads the user promised to follow up on | channel chatter |
| Linear / Jira / GitHub | assigned and in progress, blocked on the user, due soon; reviews requested | backlog |
| Todoist / tasks | due today or overdue; priority 1; tasks the user keeps rescheduling; the area's own project (Personal, Health…) | someday lists, unless memory names one as a goal |
| Notion / Drive / Docs | docs the user edited recently and left unfinished; docs shared for review | everything else |
| Meeting notes (Granola, Fathom, Zoom) | action items the user took in the last week | the rest of the transcript |
| Memory | goals for this area, what the user said matters, what works for them, the area map and day rules | lines from other areas |
| Past chats | earlier one-thing-today runs in this area and their outcomes; plans made in chat | |

Tool names differ by surface and connector; use what's there. Read in parallel and keep a
short candidate list (5–12 items), each with its source and a one-line fact. **Never show
message bodies or private details.**

## Pick

Ask four questions of each candidate. Don't compute a score to look rigorous. Rank by the
answers, and be able to say the winning one in a sentence.

1. **Who's waiting?** A colleague, a client, a partner, a friend, a kid, or a promise the
   user made to themselves. Someone waiting beats something nobody is waiting on.
2. **What slips if it waits a day?** A real, dated consequence: a meeting, a launch, a bill,
   a booking window, a birthday. It beats a soft one.
3. **Does it compound?** It moves a stated goal, removes a recurring pain, or makes tomorrow
   easier. This is the 1% question.
4. **Has it been avoided?** Rescheduled three times, "80% done" for days, or "I keep
   meaning to". Avoided important things are usually the right pick, and that's where
   perfectionism hides.

Then discount:

- **Busywork**: tidying, reorganising, inbox zero, tweaking a template, *unless* that
  thing is the area's stated goal ("clear the spare room" can be a personal focus). These
  go in `not_today`.
- **Too big to start today**: pick its first finishable slice ("draft the outline", not
  "write the report").
- **Out of the user's hands**: waiting on someone else isn't a focus, but nudging them
  might be.

**Weigh what the user said matters** in this area (memory, a correction yesterday) above
what looks urgent in an inbox. When nothing stands out, pick the smallest step on their
most important stated goal for the area.

**An event isn't the one thing.** Preparing for a meeting, booking an appointment, or
getting to one can be.

**Off days.** On a weekend, a holiday or an out-of-office day, a `work` or `all` run
starts from "Nothing needs you today", with the calendar entry (or the day) as evidence.
Don't dig up work to fill it. **Stay in the area**: a `work` run's focus is a rest ("Take
the day off"), never a personal task labelled as work. Only an `all` run may suggest a
small personal step.

## Write it

- **focus**: an imperative with a concrete object, and a person when there is one. ≤90
  characters. "Send the pricing draft to Priya", "Call mum", "Book the physio follow-up".
  Not "Make progress on pricing".
- **why**: 2–3 sentences, plain, the way a friend who's good at priorities would put it.
  Name the consequence. No hype, no "crucial", no "unlock".
- **evidence**: 1–4 lines, each `{source, fact}`. `source` is exactly a name from
  `sources_checked` (which includes `Memory` and `Past chats` when read), or `You`. Facts are short and specific: a
  subject line, an event time, a status, a date last done.
- **how**: 1–3 steps. Each is one physical action of 140 characters or less, with
  `minutes`. The first is 25 minutes or less and names the exact thing to open or do.
- **done_when**: something you could check. **good_enough**: the bar, plus what to skip.
- **not_today**: up to 3 tempting things **from the same area** that can wait.
- **area**: the run's area, ≤24 characters. **yesterday**: `{focus, outcome, day}`.
  `outcome` is `done`, `partial`, `not_done` or `unknown`; `day` is "Yesterday",
  "Friday", and so on.
- **lang**, **labels**, **done_storage**: see SKILL.md step 4.

## Learning

Memory is the only thing that carries across days, so write to it deliberately and
sparingly. **Every line carries its area** in brackets.

| save | example | when |
|---|---|---|
| the run | `One thing 2026-09-24 [work]: send pricing draft to Priya` | every run |
| the outcome | `… [work]: done` | when the user says so (including "done" in chat) or you can see it |
| a correction | `[work] Board deck outranks client email this month` | whenever the user overrules the pick |
| a pattern | `[personal] Evening focuses get done; mornings don't` | only after it has happened 3 times in that area |
| a goal | `[health] Run three times a week` | when the user says it |
| settings | `one-thing-today settings: skip Slack; Sat–Sun: personal; areas: work = …` | on `config`; one line, replaced, never appended |

Rules:

- **Apply only this area's lines, plus `[all]` lines.** A work pattern never steers a
  personal pick.
- **A correction beats a pattern.** When the user says "not that", save the reason and use
  it tomorrow.
- **One outcome is a note; a repeat is a pattern.** Promote only after three, within the
  area.
- **Keep it short.** A handful of lines per week, not a diary. Merge rather than append
  when a pattern is restated.
- **Nothing sensitive.** No email contents, diagnoses, results or medications. A health
  goal is fine, a health detail isn't.
- **Tell the user what you saved**, in one line. They can say "forget that".
