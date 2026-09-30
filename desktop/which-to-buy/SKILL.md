---
name: which-to-buy
description: >-
  Compares 2-5 products side by side on one page: specs, prices, visual differences, and a
  pick for what matters to you. Use for "which should I buy", "X vs Y" or "compare these".
metadata:
  side_effects: true
  trigger: "Choosing between products to buy, asking 'X vs Y', 'which should I get', or pasting product links to compare."
  tags: "shopping, comparison, decision, specs, visualization, recommendation, artifact, desktop"
---

# Which to buy

Buying something shouldn't take eleven tabs. This skill researches 2–5 products, lines
their specs up side by side on one calm page, shows **where they actually differ**, and
puts a recommendation on top that's picked for **what matters to you**, not for a
generic "best". When you want to dig in, every product and question on the page copies a
ready-made prompt you paste back into this chat.

It starts automatically when the request matches: "Sony XM6 vs Bose QC Ultra", "which
robot vacuum should I get under $500?", "compare these three" plus links. It's not for
browsing a whole category (it asks you to narrow to five), and it never buys anything.

One reference, **read it every run**: [`research.md`](./references/research.md) (where
specs and prices come from, what to compare, how to pick). Data shape:
[`evals/example-compare.json`](./evals/example-compare.json). Defaults:
[Configuration](#configuration), at the end of this file.

---

## The flow

```
Compare progress:
- [ ] 0. Settings: the chat, then saved settings in memory, then Configuration
- [ ] 1. Frame: what, which candidates (2-5), what matters, budget
- [ ] 2. Research: specs and prices, each value with its source (research.md)
- [ ] 3. Choose rows: what differs and what matters, 8-14 rows
- [ ] 4. Pick: for this person's priorities, with the rows that decide it
- [ ] 5. Write compare.json → validate → render → show the page
- [ ] 6. Close: two lines, then stay in the chat for follow-ups
```

### 0. Settings

Look in memory for the line starting **"which-to-buy settings:"** (country, currency,
stores to skip, standing priorities such as "quiet matters more than power"). **What the
user says in this chat wins, then the saved settings, then
[Configuration](#configuration).**

### 1. Frame

Work out, from the chat first:

- **What** is being bought, and **the candidates**. Use the ones named or linked. If only
  a category is given ("a robot vacuum"), shortlist 3 from current, well-reviewed options
  in the budget and say why each made the list. More than five named: ask which to drop,
  or keep the five closest to the stated priorities and say which were left out.
- **What matters**: 1–4 priorities in the user's words ("quiet", "battery", "fits carry-on
  luggage"). These become `priorities`, and each maps to a row.
- **Budget** and **country** (prices and availability differ by market).

If priorities or budget are missing and would change the pick, ask **one** message with
at most two questions ("What's the budget, and what matters most: noise, battery or
comfort?"), offering "just compare" as an answer. Otherwise don't ask; say what you
assumed on the page (`assumptions`).

### 2. Research

Follow [`research.md`](./references/research.md). The short version:

- **Specs** from the maker's own spec page or manual first; reputable reviews for what a
  spec sheet can't tell (real battery life, noise, reliability). Record each source once in
  `sources` and cite its `id` on every value.
- **Prices** from a retailer or the maker in the user's country, with the date read. Say
  "from" when prices vary by configuration.
- **Unknown stays unknown.** A value you couldn't find is `null` with a `note`, shown as
  "—". Never fill a gap with a guess, an older model's number, or "typical" values.
- No web access in this conversation? Say so, compare only from what the user pasted and
  your knowledge, set `offline: true`, and cite a source of kind `claude` for those
  values. The page shows a banner.

### 3. Choose rows

Aim for 8–14 rows (the validator allows 3–20), grouped (`Price`, `Performance`, `Battery`, `Size & weight`…). Keep a row if
it **differs** between products or is a stated **priority**; drop rows every product
shares, unless the user asked about it. Numeric rows set `better` (`higher` or `lower`) so
the page can draw the difference. Yes/no features use `true` / `false`.

### 4. Pick

The rubric is in [`research.md`](./references/research.md#pick). In short:

- **One pick** (`verdict.pick`), for *this* person. Start from their priorities, then
  price, then everything else. A headline of 90 characters or less, and a `why` of two or
  three plain sentences.
- **`because`**: 1–4 row keys that decide it. The page highlights them. If the pick loses
  on one of its own `because` rows, it's the wrong reason; the validator warns.
- **`runner_up`** with the one condition that flips it ("if you fly a lot").
- **`best_for`**: up to three honest labels such as "Lowest price" or "Lightest", each
  with the `row` it wins outright. A row with an unknown value has no winner.
- **Deal-breakers** go in the pick's `cons`, not hidden.
- If it's genuinely a toss-up, say so in the headline and let the runner-up condition do
  the work. Never manufacture a winner.

### 5. Write, validate, render

1. Write `compare.json` in the shape of
   [`evals/example-compare.json`](./evals/example-compare.json).
2. `python3 scripts/validate_compare.py compare.json`. Fix every ERROR and re-run until it
   passes. WARNINGs are worth reading.
3. **With artifacts available**: create one HTML artifact, the contents of
   [`assets/compare-template.html`](./assets/compare-template.html) with its
   `<script id="compare-data">` contents replaced by the output of
   `python3 scripts/render_page.py compare.json --data`. Write the page once; don't also
   render a full file.
4. **Without artifacts**: `python3 scripts/render_page.py compare.json compare.html` and
   share the file.

The page has: the verdict on top (pick, why, the deciding rows, runner-up, best-for
tags), a product strip with prices, the **side-by-side table** with a bar in each numeric
cell and the winner of each row marked, a **differences only** toggle, pros and cons, and
**Ask Claude** buttons. It works in light and dark mode and on a phone.

### 6. Close, and keep chatting

Two lines after the page: the sources that mattered most (and any that failed), and the
single thing most likely to change the pick. Then stay in the chat.

**Coming back to chat is the point.** An artifact can't post into the chat
([artifacts](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)
documents calling Claude and storage, nothing that sends to the conversation), so each
**Ask Claude** button copies a prompt that names the comparison and the product. When a
pasted prompt arrives ("About the Aria 2 in my which-to-buy comparison: …"), answer in
this chat, from the same `compare.json`.

Follow-ups that change the page **re-render it** rather than answering only in text:

- "add the X" / "drop the Y" → research the new one to the same rows, re-pick
- "battery matters more than price" → re-order priorities, re-pick, say what changed
- "I'm in the UK" → re-price, re-pick if the order changed
- "show me only what differs" → the page's toggle already does it; say so

Say "remember that" to save a standing preference (see [`config`](#conventions)).

---

## Honesty rules

- **Every value has a source.** Specs cite a source id; the validator rejects a value
  without one. Unknown is `null`, shown as "—".
- **Prices are dated and placed.** "$349 at Best Buy, 30 Sep". Prices move; the page says
  when it was read.
- **Reviews are opinions; label them.** A reviewer's measured battery life is `Tested by
  RTINGS`, not the spec.
- **No invented scores.** The page counts row wins; it never shows a made-up "8.7/10".
- **No affiliate framing, no urgency.** No "deal ends soon", no referral links; link to the
  maker's page or the retailer you read.
- **Say what you couldn't check.** Failed fetches and blocked sites go in
  `sources_missing`.

## Conventions

**`help`**: one sentence on what this does, whether web search is on, the current
settings, and the things to say: "X vs Y", "compare these", "add Z", "what matters is
…", `config`, `reset`.

**`config`**: change settings in one round, showing the current value of each: country
and currency, stores to prefer or skip, standing priorities per category, and the number
of candidates to shortlist. Save them to memory as one "which-to-buy settings:" line,
replacing the old one. Desktop skills can't keep files between chats; memory is what the
next run reads.

**`reset`**: removes the "which-to-buy settings:" line and this chat's changes, going
back to [Configuration](#configuration). It never touches anything else in memory.

**Tone**: calm and plain, like a friend who reads spec sheets for fun and doesn't care
which one you buy. One line to open, the page, two lines to close.

## Configuration

Defaults. Saved settings live in memory as one line, "which-to-buy settings: …".
**What you say in the chat beats saved settings, which beat these defaults.** To change a
default for everyone, edit this list, re-zip and re-upload.

- country and currency: from the conversation; ask only if prices would differ
- shortlist size (category only): 3
- stores: the maker's own store and major retailers in the country; skip: none
- rows: 8-14 (3-20 allowed), differences and priorities first
- ask before comparing: only when budget or priorities would change the pick (one message)
- tone: calm, plain
- language: the conversation's

These are fixed, not settings, and the validator enforces them:
- 2 to 5 products
- every value cites a source that's listed, or is `null`
- one pick, with 1-4 deciding rows that exist
- a dated price for each product (or `null` with a note)
