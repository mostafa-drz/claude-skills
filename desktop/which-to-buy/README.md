# which-to-buy

Two to five products on one calm page: the specs side by side, the differences you can
see at a glance, and a pick on top chosen for what matters to you. When you want to dig
in, copy a question from the page and keep going in the chat.

> **Status: draft (v0).** Built from the official docs. The scripts and page are tested
> locally. It hasn't been run end to end inside Claude Desktop yet. The eight scenarios
> in [`evals/evals.json`](./evals/evals.json) are the acceptance test for that first run.

## The problem

Buying something turns into eleven tabs, three review sites that disagree, and a spec
sheet where the one number you care about is on page four. By the end you know more
and have decided less.

| what usually goes wrong | how this skill handles it |
|---|---|
| Too many options | 2 to 5 products, enforced. A category gets a shortlist of 3 |
| Spec sheets list everything | Only rows that **differ** or that **you said matter**, plus a *differences only* switch |
| Numbers that are hard to compare | A bar in every numeric cell, and the winner of each row marked |
| "Best overall" lists that don't know you | The pick is argued from **your** priorities, with the gap in plain units ("5 dB", "$50") |
| Made-up specs and stale prices | Every value cites a source that was read; unknown is "—"; prices say where and when |
| Scores that mean nothing | No "8.7/10". The page counts which product wins each of your priorities |
| Getting stuck after the verdict | **Ask Claude** buttons copy a question with the comparison's context, to paste in the chat |

## How it works

```
settings (chat › memory › defaults) ──► frame: what, 2-5 candidates, what matters, budget
                                                             │
    page ◄── render ◄── validate compare.json ◄── pick ◄── rows ◄── research (maker → lab → retailer)
      │
      └──► "Ask Claude" copies a prompt ──► paste in the chat ──► answer, re-render if it changes
```

## What you get

A single page:
- **Our pick for you**, in large type, with the headline, why, the rows that decided it,
  the runner-up and when it wins instead, and up to three *best for* labels;
- **What matters to you**: your priorities, and how many each product wins;
- product cards with the price, where and when it was read, a link, and **Ask Claude**;
- the **side-by-side table**, grouped, with bars, winners, notes and source numbers, and
  a *differences only* switch;
- pros and cons, suggested questions, and the numbered sources.

It works in light and dark mode, is built for a phone first (the table scrolls inside
its box with the spec names pinned), and follows the chat's language.

## Install (Claude Desktop / claude.ai)

```bash
cd claude-skills/desktop
zip -r which-to-buy.zip which-to-buy/
```

1. Make sure **code execution** is on in **Settings → Capabilities**.
2. Upload the zip under **Customize → Skills**
   ([using skills](https://support.claude.com/en/articles/12512180-using-skills-in-claude)).
3. Turn on **web search**, so specs and prices are current.
4. Ask **"Sony XM6 vs Bose QC Ultra, which should I get?"**

## Settings

Say `config` to change settings, `help` to see them, `reset` to go back to the defaults.
Settings are one line in Claude's memory. What you say in a chat beats saved settings,
which beat the defaults. Full list: [`SKILL.md` → Configuration](./SKILL.md#configuration).

- **Country and currency**, for prices and availability.
- **Stores** to prefer or skip.
- **Standing priorities**, per category ("quiet matters more than power").
- **Fixed on purpose:** 2 to 5 products, a source for every value, one pick with the
  rows that decide it, and a dated price.

## Design decisions, and where they come from

- **Same shape as [`one-thing-today`](../one-thing-today/)** and
  [`make-it-runbook`](../make-it-runbook/): data file → stdlib validator → template
  renderer. The rules that keep a comparison honest are checks, not hopes.
- **"Ask Claude" copies a prompt, and doesn't send one.** The help center documents
  artifacts that call Claude and artifacts with storage, but nothing that posts into the
  conversation
  ([artifacts](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)).
  The page sits next to the chat, so a copied prompt with the comparison's context is the
  shortest way back. When the clipboard is blocked, the prompt is shown selected, ready
  to copy by hand.
- **No in-page AI chat.** An artifact can call Claude (`window.claude.complete`), but that
  call doesn't see this conversation, your memory or web search. Follow-ups belong in the
  chat, where all of those are.
- **Counts, not scores.** Weighting specs into one number hides the trade-off the person
  has to make. Counting row wins on the user's own priorities is derived from the data
  and can't be tuned to look decisive.
- **A 177-character description.** The claude.ai help center caps upload descriptions
  at 200 characters
  ([custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)).
  Trigger phrases come first; the rest is in the body.
- **The page is generated once.** Claude writes the artifact as the template plus the
  data block, which `render_page.py --data` prints already escaped. A full file is only
  made when artifacts aren't available.
- **`side_effects: true`**, because `config` and "remember that" write one line to
  memory. It never buys, adds to cart or signs up for anything.

## Honest limits

- **Prices move.** The page says where and when each was read; check before you pay.
- **Some sites block reading.** Those go under *Couldn't read*, and the comparison uses
  what was reachable.
- **Reviews disagree.** The table uses measured values where they exist and says so;
  taste (sound, feel, looks) stays in pros and cons.
- **Copying is one extra step.** Paste the copied prompt into the chat; the page can't
  do it for you.

## Layout

```
which-to-buy/
├── SKILL.md                      the workflow, and Configuration
├── references/research.md        sources, prices, rows, how to pick, follow-ups
├── scripts/
│   ├── validate_compare.py       the honesty rules as checks
│   └── render_page.py            --data for the artifact; a full file when no artifacts
├── assets/compare-template.html
├── evals/
│   ├── evals.json                eight acceptance scenarios
│   └── example-compare.json      three headphones (fictional brands and URLs)
└── icon.svg
```

## Testing

Checked locally:

- **Validator.** The example passes. It rejects each of these:
  - one product, or six
  - a value citing a source that isn't listed
  - an unknown value with no note saying why
  - a price with no date
  - a pick, runner-up, priority or deciding row that doesn't exist, or a runner-up that
    is the pick
  - a *best for* label with no row, or one the product doesn't win (including "Lowest
    price"), or on a row with an unknown value, which has no winner
  - text in a numeric row, a row keyed `price` (reserved), or an unknown label key
  - every source from Claude's knowledge but `offline` not set

  It warns when the pick loses on one of its own deciding rows, when prices mix
  currencies, when more than three rows are identical across products, and when some
  sources are Claude's knowledge (the page then shows a banner and marks those values
  *Unverified*).
- **No winner on an unknown.** A row where any product's value is "—" marks no winner and
  counts toward nobody's priorities.
- **Page.** Screenshotted at 1200 px and at 375 px (inside an iframe, since headless
  Chrome won't size a window that narrow): no horizontal page scroll, the table scrolls
  in its box with the spec column pinned.
- **Hostile data.** A product name, title and why containing
  `</script><img onerror=…>` render as text: `render_page.py` escapes `</`, and every
  value is set with `textContent`. No element is created.

Run each scenario in `evals/evals.json` in a fresh Claude Desktop conversation with the
skill enabled, and check the listed behaviours.
