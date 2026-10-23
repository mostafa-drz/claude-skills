# Picking today's deck

Contents: [Signals](#signals) · [Search](#search) · [Pick](#pick) · [Write it](#write-it) · [Learning](#learning)

## Signals

A good pick answers a **need**: something the user is trying to get better at, or about
to face. Build 3-6 needs, each tagged with an area (`work`, `business`, `life`, or the
user's own), from these sources, strongest first:

| source | pull | skip |
|---|---|---|
| This chat | goals, "more on X", "less of Y", feedback on the last deck | |
| Project files and instructions | a goals note, a reading list, a "levels" note | anything unrelated to learning |
| Memory | goals per area, feedback lines, preferences (formats, length, level, creators), the deck history | lines from other projects' topics |
| Past chats | what the user has been asking Claude to explain or help with lately: a strong sign of a live need | |
| Calendar | the next 7 days: talks, pitches, interviews, first meetings in a new domain, a trip | recurring meetings |
| Linear / Jira / Notion | projects in progress, a new area the user just took on | ticket details |
| Email | newsletters the user subscribes to (their taste), course or event sign-ups | message bodies |
| Meeting notes (Granola, Fathom) | topics the user said they want to learn or felt unsure about | the rest of the transcript |

Tool names differ by surface; use what's there and read lightly. **Live context beats
standing goals on the day**: a pitch on Thursday makes a pitching talk today's top pick
even if the standing goal is leadership.

## Search

For each need, search with the need and the level ("B2B pricing tiers practitioner talk",
"how to give feedback to a senior engineer"), not just the topic. Prefer:

- creators and outlets the user has 👍 before, and the format they 👍 most;
- primary sources: the person who did the thing, a well-known practitioner, a university
  lecture, official docs, over listicles and content farms;
- recent when the topic moves fast (AI, tools, markets); timeless is fine for craft and
  life skills.

Keep 2-3 candidates per need, then **open each one** (SKILL.md step 3). Note the real
length: the video duration or the reading time from the page. If the length can't be
found, estimate from the word count and say "~".

## Pick

From the verified candidates, choose 3-5:

1. **Top pick first**: the best fit for today, usually a live need (an event soon) or the
   most important standing goal. It must fit the daily minutes on its own.
2. **Cover the mix**: with 3+ cards, at least one per area in the mix setting, unless the
   user asked for one area today.
3. **Vary the format**: no more than two of one format, unless the user prefers it.
4. **Respect feedback**: never a creator or format the user blocked; lean to what got 👍;
   move away from what got 👎 with the same reason twice.
5. **One stretch card at most**: a little outside the usual topics, labelled `stretch`, so
   the deck doesn't narrow into a bubble.
6. **Budget**: the top pick plus any one other card fit the daily minutes. Long things
   (a 2-hour podcast) are fine as a non-top card when the summary names the best part
   with a timestamp.

Thin day? Three cards is the floor. If fewer than three verify, give what you have as
text and say why; don't pad.

## Write it

- **title**: the real title, ≤100 characters, trimmed of clickbait capitals.
- **creator**: the channel, author or outlet.
- **url**: the canonical https link that was opened. For YouTube, `youtube.com/watch?v=`
  or `youtu.be/`, with `&t=` for a timestamp when the summary points to a part.
- **format**: `video`, `article`, `podcast`, `course`, `paper`, `book`, `tool`.
- **minutes**: whole minutes, 1-240.
- **area**: from the mix, ≤24 characters. **stretch**: true for the stretch card.
- **why**: ≤240 characters. Name the need and why *this* piece answers it. "You pitch to
  Northwind on Thursday; this is a 12-minute teardown of exactly that kind of pitch."
- **because**: 1-3 `{source, fact}`, `source` exactly as in `sources_checked`, or `You`.
- **summary**: 2-3 lines, each ≤160 characters, of concrete takeaways, not praise.
- **try**: ≤140 characters, one action of 15 minutes or less, done after the piece.
- **verified_by**: `oembed` or `opened`. **summary_from**: `transcript`, `page`,
  `description`.
- **adjusted** (deck-level): 0-3 lines, each `{change, source}`, on what feedback changed.
- **intro** (deck-level): one sentence for the cover, ≤160 characters.

## Learning

Memory is the only thing that carries across days. Write to it deliberately and sparingly.

| save | example | when |
|---|---|---|
| the deck | `Learn 2026-10-23: [work] Pricing tiers teardown (https://…); [life] …` | every run |
| feedback | `Learn feedback 2026-10-23: 👍 pricing teardown (great examples); 👎 sleep podcast (too long)` | when the user gives it |
| a preference | `[all] Learn: prefers videos under 20 min` | stated once, or seen 3 times |
| a goal | `[business] Learn goal: get better at B2B sales calls` | when the user says it |
| a block | `[all] Learn: no more content from <creator>` | when the user says it |
| settings | `learn-today settings: mix work, business, life; cards 4; minutes 30` | on `config`; one line, replaced |

Rules:

- **A reason beats a tap.** "Too basic" moves the level; a bare 👎 only moves away from
  that piece.
- **A repeat is a pattern.** Promote a 👍 or 👎 pattern to a preference after three.
- **Done counts as interest**, not as a 👍.
- **Merge, don't append**: restate a preference by replacing its line.
- **History is the deck lines.** Use them to skip repeats within the no-repeat window.
- **Nothing sensitive** goes into memory. Tell the user what you saved, in one line.
