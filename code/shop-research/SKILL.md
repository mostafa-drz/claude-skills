---
name: shop-research
description: >-
  Researches products across Amazon, Google Shopping, and relevant specialty
  sites using the Claude-in-Chrome browser extension. Finds candidates matching
  user-specified criteria (gift, gadget, gear, home goods, etc.), captures
  screenshots and key data per candidate, then generates a modern 2026 HTML
  report with pros/cons, review highlights, metrics, and recommendations. Saves
  each research session to its own semantically-named folder. Learns from
  user feedback over time — preferences, favored brands, budget style, and
  thumbs-up/down on past picks personalize future searches. Use when the user
  wants to shop for something, compare products, find a gift, or research
  purchases before buying.
argument-hint: "[what to find] [--for <recipient>] [--budget <range>] [--sites <list>] [--max-candidates <N>] [--notes <text>]"
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
  - Bash(rm *)
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
  - mcp__claude-in-chrome__form_input
  - mcp__claude-in-chrome__resize_window
---

## Preferences

_On startup, use Read to load `~/.claude/skills/shop-research/preferences.md`. If missing, treat as first-run (see First-time detection below)._

Defaults when no preferences exist:
- `output-root`: `~/Desktop/shop-research/` (confirmed on first run)
- `default-sites`: `amazon`, `google-shopping`
- `max-candidates`: `5`
- `currency`: `USD`
- `tone`: `friendly-cli` (terse, direct, warm — not corporate)
- `open-report`: `true` (auto-open the HTML report when done)

_Also load `~/.claude/skills/shop-research/feedback-journal.md` if present — it contains thumbs-up/down on past recommendations. Summarize its signal (e.g., "prefers minimal aesthetic", "avoids fast-fashion brands") and carry that into ranking._

## Context

_On startup, use Bash to detect: today's date (`date +%Y-%m-%d`), and whether `~/Desktop/shop-research/` exists (`ls` or absence)._

## Command routing

Check `$ARGUMENTS`:
- `help` → show help, stop
- `config` → run config flow, stop
- `reset` → delete preferences + feedback journal, confirm, stop
- `feedback` → collect thumbs-up/down on the most recent research (see Feedback section), stop
- `history` → list recent research folders with titles and dates, stop
- `setup` or `preflight` → run the Chrome extension setup/onboarding flow (see Setup section), stop
- anything else → run the skill (starts with a preflight check — see Step 0)

## Help

```
shop-research — Product research across Amazon, Google & specialty sites with a 2026 HTML report

Usage:
  /shop-research [what to find]                    Interactive research
  /shop-research [...] --for <recipient>           Who is this for? (e.g., "mom, loves gardening")
  /shop-research [...] --budget <range>            e.g., "under $50", "$100-200"
  /shop-research [...] --sites <list>              Override default sites (amazon,google,etsy,rei,...)
  /shop-research [...] --max-candidates <N>        How many finalists to include (default 5)
  /shop-research [...] --notes <text>              Extra criteria, preferences, exclusions
  /shop-research config                            Set preferences
  /shop-research reset                             Clear preferences + feedback journal
  /shop-research feedback                          Rate the last research (teaches the skill)
  /shop-research history                           List past research folders
  /shop-research setup                             Walk through Chrome extension setup
  /shop-research help                              This help

Examples:
  /shop-research "birthday gift for my dad — loves woodworking, under $75"
  /shop-research "standing desk" --budget "$300-600" --notes "manual crank ok, no glass tops"
  /shop-research "running shoes" --for "me, neutral arch, marathon training" --sites amazon,rei

Output:
  {output-root}/{YYYY-MM-DD}-{kebab-title}/
    ├── report.html              ← modern 2026 single-file report (open in browser)
    ├── data.json                ← structured data (products, reviews, scores)
    ├── candidates/
    │   ├── {slug-1}/
    │   │   ├── hero.png         ← product image
    │   │   ├── page.png         ← screenshot of listing
    │   │   └── notes.md
    │   └── ...
    └── sources.md               ← all URLs visited + reasoning trail

Current preferences:
  (loaded from preferences.md)
```

## Config

Use AskUserQuestion to collect:

1. **Output root** — where should research folders live? (default: `~/Desktop/shop-research/`)
2. **Default sites** — which e-commerce sites to search by default? (Amazon, Google Shopping, Etsy, eBay, specialty)
3. **Max candidates** — how many finalists per research? (3 / 5 / 8)
4. **Currency & region** — currency symbol and Amazon TLD (amazon.com / .co.uk / .de / ...)
5. **Ethical filters** — any brands or categories to always exclude? (free text)
6. **Tone** — friendly-CLI (terse, warm), detailed (more explanation), minimal (facts only)

Save to `~/.claude/skills/shop-research/preferences.md` in the format:

```markdown
# /shop-research preferences
Updated: {date}

## Defaults
- output-root: {path}
- default-sites: {comma-list}
- max-candidates: {N}
- currency: {USD|EUR|...}
- amazon-tld: {com|co.uk|...}
- tone: {friendly-cli|detailed|minimal}
- exclusions: {free text}

## Profile (optional — the user can edit)
- Favored brands:
- Avoided brands:
- Aesthetic: (minimal, maximalist, vintage, etc.)
- Sustainability: (important / nice-to-have / not a factor)
- Gift-giving style: (practical / sentimental / experiential)

## Learned
- (auto-appended as patterns emerge)
```

After saving, confirm with a warm one-liner: "Saved. I'll remember these for next time — and I'll keep learning as you give feedback."

## Reset

Delete both `~/.claude/skills/shop-research/preferences.md` and `~/.claude/skills/shop-research/feedback-journal.md`. Confirm: "All cleared. I'll start fresh on the next research."

## First-time detection

If no preferences file exists, show a warm onboarding (not a blocker):

```
First time running /shop-research — quick intro:

  I search Amazon, Google Shopping, and specialty sites in a real Chrome
  window you control. For each research I create a folder on your Desktop
  with screenshots, a data.json, and a single-file HTML report you can open
  anywhere.

  I get smarter over time. After each research you can run `/shop-research
  feedback` to tell me what worked — I save that and factor it into future picks.

  To browse the web, I need the Claude in Chrome extension. If you haven't
  set it up yet, run:  /shop-research setup
  Otherwise, continue and I'll auto-check the connection.
```

Then proceed to Step 0 (preflight). After the first successful research, ask inline if they want to save any quick prefs (budget style, aesthetic, sustainability priority) — don't force the full config flow.

## Setup — Chrome extension onboarding

When invoked as `/shop-research setup` (or when Step 0 preflight fails and the user asks for help), walk through the Chrome extension setup. Reference: the official docs at `https://code.claude.com/docs/en/chrome`.

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
      (click the extension icon → settings). At minimum, allow:
        amazon.com, google.com, shopping.google.com
      Plus any specialty sites you plan to search (etsy.com, rei.com, etc.)
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

Native messaging host config (only relevant if deeper troubleshooting needed):
- **macOS (Chrome)**: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **macOS (Edge)**: `~/Library/Application Support/Microsoft Edge/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **Linux (Chrome)**: `~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`

### Confirm it works

Once the user says they're set up, run the preflight (Step 0 below). If it passes, say:

```
Connection good. You're ready — try:
  /shop-research "birthday gift for my dad — loves woodworking, under $75"
```

## Workflow

### Step 0 — Preflight (Chrome extension check)

Before anything else, verify the Claude-in-Chrome extension is connected. Without it, the research can't run.

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

Need the full walkthrough?  Run:  /shop-research setup
```

Then stop. Don't attempt the research without a working extension — it will only produce an empty folder.

**One retry allowed**: after showing the message, if the user replies "retry" or "try again", call `tabs_context_mcp` once more. If it still fails, route them to `/shop-research setup`.

### Step 1 — Understand the ask

Parse `$ARGUMENTS` for:
- **What** — free text before any `--flag` (e.g., "birthday gift for my dad — woodworking")
- `--for <recipient>` — who it's for (include context about them)
- `--budget <range>` — budget constraint
- `--sites <list>` — override default sites
- `--max-candidates <N>` — override default candidate count
- `--notes <text>` — additional criteria or exclusions

If **what** is missing or vague, ask ONE concise AskUserQuestion with 2-4 clarifying options (recipient, vibe, budget). Don't interrogate — pick the one clarification that most shapes the search.

If you have feedback-journal.md, mention in one line which past signal is shaping this: e.g., "Biasing toward [X] based on past thumbs-up."

### Step 2 — Draft a search plan

Before opening the browser, draft a plan and show it:

```
Plan:
  ├── Query strategies: [2-3 search phrasings]
  ├── Sites: {default-sites or --sites override}
  ├── Shortlist target: {max-candidates} candidates
  └── Scoring criteria: [3-5 factors derived from the ask]

Reply 'go' to start, or tweak any of the above.
```

Wait for confirmation (or a tweak). This is the only hard gate — keep it fast.

### Step 3 — Create the research folder

Generate a slug from the ask: `{YYYY-MM-DD}-{kebab-summary-max-60chars}`. Examples:
- `2026-04-18-dad-birthday-woodworking-under-75`
- `2026-04-18-standing-desk-300-600`

```
mkdir -p {output-root}/{slug}/candidates
```

**Clear policy**: only the per-research folder is created fresh. Never delete sibling folders or anything outside `{output-root}/{slug}/`.

### Step 4 — Open Chrome and orient

1. Call `tabs_context_mcp` first to see what tabs exist — never reuse a prior session's tab IDs.
2. Create new tabs with `tabs_create_mcp` as needed (Amazon search URL + Google Shopping URL to start).
3. `resize_window` to a predictable viewport (e.g., 1440x900) for consistent screenshots.

### Step 5 — Gather candidates

For each site in the plan:

1. **Navigate** to the search URL for that site (e.g., `https://www.amazon.com/s?k=<url-encoded-query>`).
2. **Extract listings** via `javascript_tool`: return an array of `{title, url, price, rating, reviewCount, imageUrl}` from the top results. Prefer structured extraction over raw `get_page_text`.
3. **Score** each listing against the criteria (use the factors from Step 2). Keep the top N.
4. **Per-candidate deep dive** — navigate to the product page, extract:
   - Full title, brand, price (current + MSRP if on sale)
   - Key specs / attributes
   - Rating + review count + review-score distribution if visible
   - 3-5 top positive review snippets (highest-rated helpful reviews)
   - 3-5 top negative / critical review snippets
   - Notable flags: return policy, shipping, warranty
5. **Save hero image**: use `javascript_tool` to extract the main image URL, then `curl -L -o {candidates}/{slug}/hero.png "<url>"`.
6. **Capture a page snapshot**: use `javascript_tool` to capture the visible viewport as PNG (via `html2canvas` loaded dynamically, or serialize as data-URL and decode with Bash). Save as `{candidates}/{slug}/page.png`. If capture fails, log and continue — the hero image alone is sufficient.
7. **Write `{candidates}/{slug}/notes.md`** — one short file per candidate with all extracted fields.

**Cross-source reviews (optional, adds depth)**: for each finalist, run one `WebSearch` for `"<product name>" review` to surface independent reviews (Wirecutter, Reddit, YouTube summaries). Quote 1-2 excerpts in the report.

**Graceful degradation**: if a site blocks extraction, log the issue in `sources.md` and skip — don't abort the whole research.

### Step 6 — Score, rank, and pick a winner

Compute a composite score per candidate (0-100) from the scoring criteria. Produce:
- **Top pick** — best overall
- **Runner-up** — close second with a different trade-off
- **Budget pick** — cheapest that clears the quality bar (if price range spans widely)
- **Splurge pick** — highest-quality option if budget allows

Write `data.json` with the full structured data: candidates, scores, picks, sources, query metadata.

### Step 7 — Generate the HTML report

Generate a single self-contained `report.html` (no external JS dependencies — inline everything). Aesthetic targets:

- **Modern 2026** — clean typography (system font stack + Inter-style weights), generous whitespace, soft shadows, subtle gradients, rounded corners (12-16px), pill badges
- **Light + dark mode** via `prefers-color-scheme` — CSS variables only
- **Mobile-responsive** — single-column layout on small screens
- **Intuitive** — hero at top (top pick with verdict), then candidates grid, then detail pages per candidate accessible via in-page anchors
- **Data-dense but scannable** — pill chips for key specs, inline stars for ratings, mini bar charts for review distribution (pure CSS, no libs)
- **No emoji soup** — use color + typography to signal meaning, not emoji

Structure:
1. **Header** — brand mark + research title, date, budget, criteria summary (as pill chips). Inline the SVG from `~/.claude/skills/shop-research/icon.svg` at ~32px next to the H1 with `color: var(--accent)` so it themes with light/dark mode. The icon is the grid-pick mark — a 3×3 dot grid with one cell haloed, signaling "N candidates → one pick" which matches this skill's behavior.
2. **TL;DR** — one-paragraph verdict + the top pick card with hero image, price, score ring, "why this won" (3 bullets)
3. **Quick comparison table** — all candidates, sortable by score/price/rating (client-side JS inline)
4. **Candidate deep-dives** — one section per candidate with:
   - Hero image
   - Price, rating, review count, score
   - Pros (3-5 bullets) and Cons (3-5 bullets)
   - Positive review quote + critical review quote
   - External review excerpt (if found)
   - "Good to know" metrics row (warranty, return window, shipping)
   - Link to the product page
5. **Footer** — sources, criteria recap, "rate this research" link to `/shop-research feedback`

Reference `~/.claude/skills/shop-research/reference/report-template.html` if it exists (load on demand; otherwise generate from scratch following the aesthetic above).

### Step 8 — Finalize and open

1. Write `sources.md` — every URL visited + one-line rationale per decision.
2. Print the final CLI report:

```
Done — {N} candidates researched in {duration}

  Top pick:     {title}  →  ${price}
  Runner-up:    {title}
  Budget pick:  {title}

Folder:   {output-root}/{slug}/
Report:   {output-root}/{slug}/report.html

Open it?  (y/N)  — or rate with:  /shop-research feedback
```

If `open-report: true`, run `open {output-root}/{slug}/report.html`.

### Step 9 — Invite feedback

End with a soft prompt (not a blocker):

> When you've had a look, run `/shop-research feedback` and tell me what worked. I'll keep getting sharper at your taste.

## Feedback & learning

When invoked as `/shop-research feedback`:

1. Find the most recent research folder under `{output-root}/`.
2. Ask via AskUserQuestion:
   - **Did the top pick feel right?** (yes / yes with caveats / no, missed the mark)
   - **What to weight more next time?** (price / quality / brand / aesthetic / reviews / other)
   - **Anything to avoid in future research?** (free text)
3. Append to `~/.claude/skills/shop-research/feedback-journal.md`:

```markdown
## {research slug} — {date}
- Verdict: {yes/caveats/no}
- Weight more: {factors}
- Avoid: {free text}
- Signal extracted: {one-line generalization, e.g., "prefers quieter/minimal aesthetic over bold"}
```

4. If a clear pattern emerges across 3+ sessions (same brand avoided, same price sensitivity, same aesthetic), promote it from the journal to the `## Learned` section of `preferences.md`. Mention the promotion: "Noticed you consistently avoid X — saving that as a standing preference."

The journal is human-editable. Respect whatever the user writes there directly.

## Filename / folder naming rules

- Research folder: `{YYYY-MM-DD}-{kebab-summary}` — 60 chars max in the summary half
- Candidate folder: `{kebab-product-short-name}` — 40 chars max, derived from product title (not a counter)
- Never append `-2`, `-3` — if two candidates would collide, differentiate by brand or model number

## Principles

1. **Real Chrome, explicit tabs** — always `tabs_context_mcp` first; always create a new tab with `tabs_create_mcp` rather than reusing one from a prior session
2. **Structured over scraped** — prefer `javascript_tool` returning clean JSON over dumping `get_page_text`. Smaller context, higher accuracy
3. **Per-research isolation** — one folder per session; never delete or overwrite anything outside the current research folder
4. **Non-interrogating onboarding** — ask the minimum clarifying question that unblocks the search; save prefs silently as patterns emerge
5. **Learning is explicit and editable** — feedback lives in a human-readable journal; the user can read, edit, or wipe it anytime
6. **Graceful degradation** — a blocked site or a failed screenshot is logged and skipped; the research completes with what was possible
7. **Stop on dialogs** — never click elements that trigger browser alerts/confirms/prompts; the extension becomes unresponsive if a modal appears
8. **Warm, terse CLI tone** — direct sentences, no corporate filler, no emoji-heavy output; one friendly line at start and end is enough
