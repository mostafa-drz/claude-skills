---
name: should-i-buy
description: >-
  Helps the user decide on a purchase by taking the product links they're
  considering, asking a couple of sharp clarifying questions about their needs
  and circumstances, then opening each link in real Chrome via the
  Claude-in-Chrome extension to extract price, specs, ratings, reviews, return
  policy, and shipping. Produces a modern 2026 HTML report with a side-by-side
  comparison, pros/cons per option, an external-review pulse-check, and a clear
  verdict (buy / wait / pick X over Y / skip). Saves each decision session to
  its own folder. Learns from thumbs-up/down feedback — brand, budget style,
  deal-breakers, and past regrets personalize future verdicts. Use when the
  user pastes one or more product URLs and wants a second opinion before
  buying, wants a comparison between links they already shortlisted, or asks
  "should I buy this / which one should I get?".
argument-hint: "<url> [more urls...] [--for <context>] [--budget <range>] [--use <use-case>] [--deadline <when>] [--notes <text>]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Bash(mkdir *)
  - Bash(ls *)
  - Bash(open *)
  - Bash(curl *)
  - Bash(date *)
  - Bash(pwd)
  - Bash(echo *)
  - WebSearch
  - WebFetch
  - mcp__claude-in-chrome__tabs_context_mcp
  - mcp__claude-in-chrome__tabs_create_mcp
  - mcp__claude-in-chrome__navigate
  - mcp__claude-in-chrome__get_page_text
  - mcp__claude-in-chrome__read_page
  - mcp__claude-in-chrome__javascript_tool
  - mcp__claude-in-chrome__find
  - mcp__claude-in-chrome__resize_window
---

## Preferences

_On startup, use Read to load `~/.claude/skills/should-i-buy/preferences.md`. If missing, treat as first-run (see First-time detection below)._

Defaults when no preferences exist:
- `output-root`: `~/Desktop/should-i-buy/` (confirmed on first run)
- `currency`: `USD`
- `budget-style`: `value` (value / premium / bargain — shapes the verdict weighting)
- `tone`: `friendly-cli` (terse, direct, warm — like a friend who actually knows the category)
- `open-report`: `true` (auto-open the HTML report when done)
- `verdict-style`: `decisive` (decisive / balanced — decisive means I pick one and say why; balanced lays out the trade-off)

_Also load `~/.claude/skills/should-i-buy/feedback-journal.md` if present — it contains thumbs-up/down on past verdicts. Summarize its signal (e.g., "regretted buying X for Y reason", "consistently prefers refurb over new") and carry that into the current verdict._

## Context

_On startup, use Bash to detect: today's date (`date +%Y-%m-%d`), and whether the output-root folder exists (`ls` or absence). Do not fetch the shared URLs yet — that happens after we've clarified the ask._

## Command routing

Check `$ARGUMENTS`:
- `help` → show help, stop
- `config` → run config flow, stop
- `reset` → delete preferences + feedback journal, confirm, stop
- `feedback` → collect thumbs-up/down on the most recent decision (see Feedback section), stop
- `history` → list recent decision folders with titles and dates, stop
- `setup` or `preflight` → run the Chrome extension setup/onboarding flow (see Setup section), stop
- anything else (one or more URLs, optionally with flags) → run the skill (starts with a preflight check — see Step 0)

## Help

```
should-i-buy — Paste links, get a verdict with a 2026-aesthetic comparison report

Usage:
  /should-i-buy <url> [more urls...]                 One or more product links
  /should-i-buy [...] --for <context>                Who/what this is for (e.g., "me, daily driver")
  /should-i-buy [...] --budget <range>               Budget constraint (e.g., "under $200")
  /should-i-buy [...] --use <use-case>               How you'll actually use it
  /should-i-buy [...] --deadline <when>              "by Friday", "this month" — affects wait-for-sale advice
  /should-i-buy [...] --notes <text>                 Constraints, dealbreakers, leanings
  /should-i-buy config                               Set preferences
  /should-i-buy reset                                Clear preferences + feedback journal
  /should-i-buy feedback                             Rate the last verdict (teaches the skill)
  /should-i-buy history                              List past decision folders
  /should-i-buy setup                                Walk through Chrome extension setup
  /should-i-buy help                                 This help

Examples:
  /should-i-buy https://www.amazon.com/dp/B0XXXXXX https://www.rei.com/product/123
    --for "me, weekend hiking" --budget "under $180"
  /should-i-buy https://bestbuy.com/... --use "home office, 2 monitors" --notes "USB-C PD required"
  /should-i-buy https://apple.com/shop/buy-mac/mac-mini --deadline "before WWDC"

Output:
  {output-root}/{YYYY-MM-DD}-{kebab-title}/
    ├── report.html              ← modern 2026 single-file report with verdict
    ├── data.json                ← structured data (options, scores, verdict)
    ├── options/
    │   ├── {slug-1}/
    │   │   ├── hero.png         ← product image
    │   │   ├── page.png         ← screenshot of listing (best-effort)
    │   │   └── notes.md
    │   └── ...
    └── sources.md               ← URLs visited + reasoning trail

Current preferences:
  (loaded from preferences.md)
```

## Config

Use AskUserQuestion to collect:

1. **Output root** — where should decision folders live? (default: `~/Desktop/should-i-buy/`)
2. **Currency & region** — currency symbol and Amazon TLD (amazon.com / .co.uk / .ca / .de / ...)
3. **Budget style** — value (best bang-for-buck), premium (quality first, price second), bargain (cheapest that clears the bar)
4. **Verdict style** — decisive (I pick one and say why) or balanced (I lay out the trade-off and let you choose)
5. **Standing dealbreakers** — categories/brands to always flag negatively (free text)
6. **Tone** — friendly-CLI (terse, warm), detailed (more explanation), minimal (facts only)

Save to `~/.claude/skills/should-i-buy/preferences.md` in the format:

```markdown
# /should-i-buy preferences
Updated: {date}

## Defaults
- output-root: {path}
- currency: {USD|EUR|CAD|...}
- amazon-tld: {com|co.uk|ca|...}
- budget-style: {value|premium|bargain}
- verdict-style: {decisive|balanced}
- tone: {friendly-cli|detailed|minimal}
- dealbreakers: {free text}

## Profile (optional — edit freely)
- Favored brands:
- Avoided brands:
- Aesthetic: (minimal, maximalist, vintage, tech-forward, etc.)
- Sustainability: (important / nice-to-have / not a factor)
- Risk tolerance: (safe/proven only / will try new/indie)
- Return behavior: (rarely returns / returns if imperfect — affects how heavily return policy weighs)
- Past regrets: (free text — things you wish you hadn't bought and why)

## Learned
<!-- Patterns auto-appended as they emerge from feedback journal -->
```

After saving, confirm with a warm one-liner: "Saved. I'll use this as the baseline — and I'll keep sharpening as you rate my verdicts."

## Reset

Delete both `~/.claude/skills/should-i-buy/preferences.md` and `~/.claude/skills/should-i-buy/feedback-journal.md`. Confirm: "All cleared. I'll start from scratch on the next decision."

## First-time detection

If no preferences file exists, show a warm onboarding (not a blocker):

```
First time running /should-i-buy — quick intro:

  Paste me one or more product links and I'll help you decide. I open each
  link in a real Chrome window you control, pull price / specs / reviews /
  return policy, cross-check a few independent reviews, and write a single-file
  HTML report with a clear verdict (buy / wait / pick X / skip).

  I ask at most two sharp questions up front — your context and your
  dealbreakers — then I get out of your way.

  I get smarter over time. After each decision you can run
  `/should-i-buy feedback` and tell me if I called it right. I save that and
  factor it into future verdicts (past regrets are especially useful signal).

  To browse the web, I need the Claude in Chrome extension. If you haven't
  set it up yet, run:  /should-i-buy setup
  Otherwise, continue and I'll auto-check the connection.
```

Then proceed to Step 0 (preflight). After the first successful decision, ask inline if they want to save any quick prefs (budget style, verdict style, dealbreakers) — don't force the full config flow.

## Setup — Chrome extension onboarding

When invoked as `/should-i-buy setup` (or when Step 0 preflight fails and the user asks for help), walk through the Chrome extension setup. Reference: the official docs at `https://code.claude.com/docs/en/chrome`.

### Prerequisites checklist (print this)

```
Before we go:

  1. Browser        Google Chrome or Microsoft Edge
                    (Brave, Arc, other Chromium browsers: not yet supported)
                    Windows WSL: not supported

  2. Plan           A direct Anthropic plan — Pro, Max, Team, or Enterprise
                    (Free tier and third-party providers like Bedrock/Vertex
                     don't have Chrome integration)

  3. Claude Code    Version 2.0.73 or higher
                    Check:  claude --version

  4. Extension      "Claude" by Anthropic, version 1.0.36 or higher
                    Install:
                    https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn
                    After install, pin it via the puzzle-piece icon.
```

Use Bash to run `claude --version` and surface the result so the user knows where they stand.

### Enable Chrome in Claude Code

Tell the user exactly what to type (they run these themselves — you can't run slash commands for them):

```
Next:

  A.  Inside Claude Code, type:   /chrome
      Select "Enable" — or "Enabled by default" to auto-enable every session.

  B.  To verify, type:            /mcp
      Look for "claude-in-chrome" in the list.

  C.  Site permissions are managed inside the Chrome extension itself
      (click the extension icon → settings). Allow whichever sites you
      actually shop on — common ones:
        amazon.com, apple.com, bestbuy.com, rei.com, bhphotovideo.com,
        target.com, walmart.com, costco.com, and any specialty retailer
        your links point to.
```

### Quick troubleshooting

If the user reports trouble, walk through in this order (from the official docs):

| Symptom | Fix |
|---|---|
| "Extension not detected" | Open `chrome://extensions`, confirm it's installed and enabled. Update if version < 1.0.36. |
| "Browser extension is not connected" | Restart Chrome and Claude Code, then run `/chrome` → "Reconnect extension". |
| Works once, then dies after a pause | Extension service worker went idle. Run `/chrome` → "Reconnect extension". |
| "Receiving end does not exist" | Same as above — reconnect. |
| "No tab available" | Ask Claude to create a new tab, then retry. |
| First-time connection fails | Restart Chrome — the native messaging host config is picked up on Chrome startup. |

### Confirm it works

Once the user says they're set up, run the preflight (Step 0 below). If it passes, say:

```
Connection good. You're ready — paste your links:
  /should-i-buy <url> [more urls...]
```

## Workflow

### Step 0 — Preflight (Chrome extension check)

Before anything else, verify the Claude-in-Chrome extension is connected. Without it, the decision can't run.

1. Call `mcp__claude-in-chrome__tabs_context_mcp`.
2. **If it succeeds** → extension is live. Continue silently to Step 1.
3. **If it fails** (any error — "extension not detected", "receiving end does not exist", etc.) → do NOT retry blindly. Stop and show:

```
Hmm — the Claude-in-Chrome extension isn't responding.

Common causes:
  • Extension not installed  → https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn
  • Chrome integration not enabled in this session  → run  /chrome  and select "Enable"
  • Extension idle  → run  /chrome  → "Reconnect extension"
  • First time ever  → restart Chrome once after enabling, then retry

Need the full walkthrough?  Run:  /should-i-buy setup
```

Then stop. **One retry allowed**: if the user replies "retry" or "try again", call `tabs_context_mcp` once more. If it still fails, route them to `/should-i-buy setup`.

### Step 1 — Parse the ask

Extract from `$ARGUMENTS`:
- **URLs** — every token starting with `http://` or `https://` (dedupe, preserve order)
- `--for <context>` — who/what this is for
- `--budget <range>` — budget constraint
- `--use <use-case>` — concrete usage scenario
- `--deadline <when>` — urgency (affects wait-for-sale advice)
- `--notes <text>` — extra constraints or leanings

**Validation gates (fail fast):**
- No URLs → ask once: "Paste one or more product links and I'll take it from there." Stop.
- One URL → single-option mode (verdict is buy/wait/skip, no comparison).
- 2-5 URLs → comparison mode (the sweet spot).
- 6+ URLs → warn: "That's a lot to compare. Want me to shortlist the top 4 after a quick glance, or run the full gauntlet?" — default to full if the user says go.

### Step 2 — Ask the two sharp questions

Fire **one** AskUserQuestion call with up to two questions. Skip any question that's already answered by flags. The goal is minimum interruption, maximum signal.

- **Q1 (context)** — "What's the single thing that most matters here?" Options tailored to the category if detectable from the URLs (e.g., for laptops: battery life / raw performance / portability / screen quality / price). If category is unclear, offer: price / quality / specific feature / aesthetic / speed of delivery / other.
- **Q2 (dealbreakers)** — "Anything that would make an option an instant no?" Options: price over budget / brand I don't trust / no good return policy / out of stock / poor reviews on my use case / none of the above.

If the user has a feedback-journal with strong signal, mention it in one line before asking: e.g., "Your past regrets say you over-index on brand reputation — I'll weight that. Still want to answer:"

### Step 3 — Echo the plan

Show a crisp plan and wait for `go` (or a tweak):

```
Plan:
  ├── Options: {N} links ({domains summary})
  ├── What matters most: {answer}
  ├── Dealbreakers: {answer}
  ├── Scoring factors: {derived — 3-5, weighted per answers}
  └── Verdict style: {decisive|balanced}

Reply 'go' to open the links, or tweak any of the above.
```

This is the only hard gate. Keep it fast.

### Step 4 — Create the decision folder

Generate a slug from the ask: `{YYYY-MM-DD}-{kebab-summary-max-60chars}`. Summary should capture the decision, not just the product, e.g.:
- `2026-04-19-standing-desk-under-500-rei-vs-amazon`
- `2026-04-19-macbook-air-m4-13-vs-15`
- `2026-04-19-hiking-boots-weekend-use`

```
mkdir -p {output-root}/{slug}/options
```

**Clear policy**: only the per-decision folder is created fresh. Never delete sibling folders or anything outside `{output-root}/{slug}/`.

### Step 5 — Open each link and extract

1. Call `tabs_context_mcp` to see current tabs — never reuse a prior session's tab IDs.
2. For each URL, create a new tab with `tabs_create_mcp`. Resize to `1440x900` on the first tab for consistent screenshots.
3. For each option page, extract via `javascript_tool` (prefer structured JSON over `get_page_text`):
   - Full title, brand, model
   - Current price + MSRP + any on-sale signal
   - Key specs (category-aware — for a laptop: CPU/RAM/storage/screen/battery; for a chair: dimensions/weight-capacity/materials; etc.)
   - Rating + review count + star-distribution if visible
   - 3-5 top positive review snippets (highest-rated helpful reviews, verified purchase if marked)
   - 3-5 top negative/critical review snippets
   - Return window + shipping cost + ship-by date
   - Stock status (in stock / low stock / backorder / out)
   - Warranty if surfaced
4. **Save hero image**: extract the main image URL via `javascript_tool`, then `curl -L -o {options}/{slug}/hero.png "<url>"`.
5. **Capture a page snapshot** (best-effort): try via `javascript_tool` with `html2canvas` dynamically loaded, or skip silently if it fails.
6. **Write `{options}/{slug}/notes.md`** — one short file per option with all extracted fields.

**Cross-source reviews** (adds credibility, do for each finalist):
- Run one `WebSearch` for `"<exact product name>" review` — look for Wirecutter, Rtings, Consumer Reports, Reddit threads, reputable YouTubers.
- Quote 1-2 short excerpts in the report.
- For deal-check: one `WebSearch` for `"<product>" price history` or `"<product>" sale` — helps the wait-vs-buy-now call.

**Graceful degradation**: if a page blocks extraction (common on some retailers), log the gap in `sources.md` and continue with partial data. Note the gap in the report so the verdict is honest about what's known.

### Step 6 — Score, compare, and verdict

Compute a composite score per option (0-100) using the weighted factors from Step 3. Then compose the verdict using the user's `verdict-style`:

**Decisive style** — pick one and say why in 2-3 sentences. Always name the runner-up and what would flip the call.

**Balanced style** — lay out the trade-off matrix (option A wins on X, option B wins on Y) and surface the decision criterion back to the user.

**Special verdicts** to consider:
- **Wait** — if price history shows a regular sale pattern and deadline allows, say so.
- **Skip all** — if none clear the dealbreakers, say so directly; don't force a pick.
- **One clear winner** — if score gap > 15 points, be direct about it.
- **Near-tie** — if top two are within 5 points, say "coin flip on specs — pick the one with the better return policy."

Write `data.json` with the full structured data: options, specs, scores, verdict, reasoning, sources, query metadata.

### Step 7 — Generate the HTML report

Generate a single self-contained `report.html` (no external JS dependencies — inline everything). Aesthetic targets:

- **Modern 2026** — clean typography (system font stack + Inter-style weights), generous whitespace, soft shadows, subtle gradients, rounded corners (12-16px), pill badges
- **Light + dark mode** via `prefers-color-scheme` — CSS variables only
- **Mobile-responsive** — single-column layout on small screens
- **Verdict-forward** — the hero of the page IS the verdict, not the product grid
- **Data-dense but scannable** — pill chips for key specs, inline stars for ratings, mini bar charts for review distribution (pure CSS, no libs), side-by-side spec table for comparison mode
- **No emoji soup** — use color + typography to signal meaning

Structure:
1. **Header** — inline the SVG from `~/.claude/skills/should-i-buy/icon.svg` at ~32px next to the H1 with `color: var(--accent)` so it themes with light/dark mode. Title reflects the decision (e.g., "Standing desk under $500 — REI vs. Amazon"). Date, context, budget as pill chips.
2. **Verdict hero** — big, unmissable. One of:
   - `BUY THIS: {option}` + 2-3 bullet reasons + score
   - `PICK {option A} OVER {option B}` + the single deciding factor
   - `WAIT — {reason}` + recommended trigger ("buy when it drops under $X")
   - `SKIP ALL — {reason}` + one-line advice on what to search for instead
3. **Side-by-side comparison table** (if 2+ options) — spec-by-spec, with winner per row lightly highlighted
4. **Option deep-dives** — one section per option with:
   - Hero image
   - Price, rating, review count, score ring
   - Pros (3-5 bullets) and Cons (3-5 bullets)
   - One positive + one critical review quote
   - External review excerpt (if found) — cite the source
   - "Good to know" row: warranty, return window, shipping, stock
   - Deep link to the product page
5. **Deal intel** (if price history gathered) — sparkline of price trend, note any upcoming sale events
6. **Footer** — sources, criteria recap, "rate this verdict" prompt → `/should-i-buy feedback`

Reference `~/.claude/skills/should-i-buy/reference/report-template.html` if it exists (load on demand; otherwise generate from scratch following the aesthetic above).

### Step 8 — Finalize and open

1. Write `sources.md` — every URL visited + one-line rationale per extraction decision.
2. Print the final CLI report (match tone preference):

```
Verdict — {kebab decision}

  {one-line verdict}

  Top pick:     {title}  →  ${price}   (score {N}/100)
  Runner-up:    {title}
  {optional third line — "Skip:" or "Wait until:"}

Folder:   {output-root}/{slug}/
Report:   {output-root}/{slug}/report.html

Open it?  (y/N)  — or rate the call with:  /should-i-buy feedback
```

If `open-report: true`, run `open {output-root}/{slug}/report.html`.

### Step 9 — Invite feedback

End with a soft prompt (not a blocker):

> When you've decided (or bought it and lived with it a week), run `/should-i-buy feedback` and tell me if I called it right. Honest signal here makes future verdicts sharper — especially if you regret something I approved.

## Feedback & learning

When invoked as `/should-i-buy feedback`:

1. Find the most recent decision folder under `{output-root}/`.
2. Ask via AskUserQuestion (fire once, multi-question):
   - **Did I call it right?** (nailed it / close / missed / bought something else entirely / haven't decided yet)
   - **What should I weight more next time?** (price / brand reputation / reviews / return policy / specs-for-use-case / aesthetic / other)
   - **Any regret signal?** (free text — e.g., "returned it, too heavy", "bought option B instead because X")
3. Append to `~/.claude/skills/should-i-buy/feedback-journal.md`:

```markdown
## {decision slug} — {date}
- Verdict given: {what I recommended}
- User outcome: {nailed/close/missed/different/pending}
- Weight more: {factors}
- Regret / correction: {free text}
- Signal extracted: {one-line generalization, e.g., "over-weighted brand, under-weighted in-hand weight for mobile gear"}
```

4. If a clear pattern emerges across 3+ sessions (same dealbreaker hit, same brand regret, same wait-vs-buy miscall), promote it from the journal to the `## Learned` section of `preferences.md`. Mention the promotion: "Noticed {pattern} across recent decisions — saving that as a standing signal."

The journal is human-editable. Respect whatever the user writes there directly.

## Filename / folder naming rules

- Decision folder: `{YYYY-MM-DD}-{kebab-summary}` — 60 chars max in the summary half, frame around the *decision* not the product (e.g., `standing-desk-under-500-rei-vs-amazon`, not just `standing-desk`)
- Option folder: `{kebab-product-short-name}` — 40 chars max, derived from product title (not a counter); for Amazon items without a clean name, fall back to `{brand}-{model}`
- Never append `-2`, `-3` — if two options would collide, differentiate by brand or model number

## Principles

1. **Verdict-forward** — the report exists to deliver a decision, not to present data neutrally. Say what to do, then justify.
2. **Minimum interruption onboarding** — at most two sharp questions up front; infer the rest from URLs and feedback history.
3. **Real Chrome, explicit tabs** — always `tabs_context_mcp` first; always create a new tab with `tabs_create_mcp` rather than reusing one from a prior session.
4. **Structured over scraped** — prefer `javascript_tool` returning clean JSON over dumping `get_page_text`. Smaller context, higher accuracy.
5. **Per-decision isolation** — one folder per session; never delete or overwrite anything outside the current decision folder.
6. **Honest about gaps** — if a page blocked extraction, say so in the report; don't fake confidence.
7. **Learning is explicit and editable** — feedback lives in a human-readable journal; the user can read, edit, or wipe it anytime. Past regrets are the single highest-signal input for future verdicts.
8. **Graceful degradation** — a blocked page or a failed screenshot is logged and skipped; the verdict ships with what was possible.
9. **Stop on dialogs** — never click elements that trigger browser alerts/confirms/prompts; the extension becomes unresponsive if a modal appears.
10. **Warm, terse CLI tone** — direct sentences, no corporate filler, no emoji-heavy output; one friendly line at start and end is enough.
