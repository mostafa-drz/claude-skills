---
name: newsletter-digest
description: >-
  Scans Gmail for newsletter emails from the past week, groups them by publication,
  extracts key insights and headlines, and produces a curated reading digest with
  three tiers: must-reads, quick takes, and low-signal sources worth unsubscribing
  from. Use when catching up on newsletters, asking what you missed this week, or
  wanting a reading digest, curated summary, or "what should I read" from email.
---

# Newsletter Digest

Every week the same stack of unread newsletters accumulates. They're not urgent — so
inbox-catchup skips them. They're not tasks — so they stay unread. The ritual of opening
each one manually, deciding whether it's worth reading, and extracting anything useful takes
45+ minutes a week, so most people skip it entirely. This skill does that filtering pass in
one invocation: searches Gmail for newsletters, reads them, curates by signal, and delivers
a digest that takes two minutes to scan.

## Configuration

```
time_window: 7d             # How far back to scan (default: last 7 days)
topics: all                 # Comma-separated topic filters: tech, design, business,
                            # science, culture, policy — or "all" (default)
min_items_per_source: 2     # Flag a source as low-signal if it sends fewer than N
                            # meaningful items per month (default: 2)
save_to_drive: ask          # "ask", "always", or "never"
```

## Process

### 1. Detect Sources

Confirm Gmail is connected. If not, explain how to enable Google Workspace in Desktop
settings and stop.

```
Connected: Gmail ✅
Scanning: last 7 days (May 14–21, 2026)
```

### 2. Search for Newsletters

Search Gmail using multiple patterns to catch newsletters regardless of sender platform:

- `label:newsletters` — if the user has a newsletters label
- `from:substack.com OR from:mail.beehiiv.com OR from:ghost.io` — known newsletter platforms
- `"unsubscribe" in:inbox -from:me` — universal newsletter indicator (one-click unsubscribe)
- `subject:digest OR subject:newsletter OR subject:issue` — editorial titles

Deduplicate by thread. Skip replies, forwards, and anything the user sent themselves.

Report the count before proceeding:

```
Found 14 newsletters from 9 publications (May 14–21)
```

If zero are found: explain the search strategy used, suggest adding a `newsletters` Gmail
label, and stop.

### 3. Extract Content

For each newsletter thread, read the email and extract:

- **Source**: publication name / sender
- **Headline**: what is the main story or theme this issue?
- **Key insight**: one sentence — what's the most useful thing in it?
- **Topic tag**: tech / design / business / science / culture / policy / other

Do not quote or reproduce full newsletter content. Extract signal only.

### 4. Rank and Curate

Score each item:

- **Topic match**: does it align with the user's configured topics? (if `topics: all`,
  everything qualifies)
- **Insight density**: does the extracted key insight contain a concrete fact, finding,
  or perspective — or is it vague ("here are some tips")?
- **Source consistency**: has this publication delivered useful content before in this
  conversation?

Split into three tiers:

**🔖 Must Read** — 2–4 items max. Highest topic match + concise, concrete insight.
If more than 4 qualify, pick the 4 with the densest insight. Force-rank; do not list 8.

**⚡ Quick Takes** — up to 8 items. Worth a headline-level skim; not urgent.

**📭 Low Signal** — sources that this week produced vague, promotional, or thin content.
Show the source name + one-line reason. Suggest reviewing the subscription.

### 5. Present the Digest

```
📰 Newsletter Digest — May 14–21, 2026
Scanned: 14 newsletters from 9 sources

🔖 Must Read (3)
  1. The Pragmatic Engineer — "AI coding assistants and the senior engineer gap"
     Topic: tech
     Key insight: Engineers with 10+ YOE are adopting AI tools at half the rate of
     juniors — not from resistance but from different bottlenecks (architecture,
     reviews, context). The leverage point is shifting.

  2. Dense Discovery — "Why your calendar is making you worse at decisions"
     Topic: design / productivity
     Key insight: Decision fatigue sets in 4.1 hours into a meeting-heavy day; the
     correlation with calendar fragmentation (vs. block scheduling) is stronger than
     sleep deficit in the cited study.

  3. Import AI — "Diffusion models for structured data"
     Topic: tech
     Key insight: New ICLR paper shows 40% better table-completion accuracy vs.
     fine-tuned LLMs for relational data. The authors open-sourced the eval benchmark.

⚡ Quick Takes (6)
  • Morning Brew — Tariff update: 90-day pause extended to July. (business)
  • Lenny's Newsletter — Cohort retention benchmark: week-1 below 40% is a red flag for
    most B2C apps. (business)
  • TLDR — Meta open-sources a new video foundation model. (tech)
  • UX Collective — Contrast ratios in dark mode: the 3:1 floor is wrong for small text.
    (design)
  • SemiAnalysis — TSMC N2 yield curve update. (tech)
  • The Diff — VC dry powder is at 2019 levels. (business)

📭 Low Signal — consider reviewing these subscriptions
  • GrowthHackers Weekly — This issue was 3 sponsored content items and a vague "top tips"
    roundup. No concrete insight.
  • AI Tools Report — Thin product announcements, no analysis.
```

Then optionally ask:

> Want me to save this digest to Drive? I'll title it
> "Newsletter Digest — May 14–21, 2026" and keep it private.

### 6. Save to Drive (if requested)

Create a new Google Doc with the digest content. Title: `Newsletter Digest — [date range]`.
Sharing: just me. Return the doc link.

## Guidelines

- **Extract, don't reproduce** — summarize what's useful, not the newsletter body verbatim.
  Respects copyright; keeps the digest scannable.
- **Force-rank must-reads** — the point is curation. Three items with tension beats a list
  of eight. If everything qualifies, nothing does.
- **Name the low signal** — naming underperforming sources is more useful than silently
  omitting them. The user decides whether to unsubscribe.
- **No promotional content** — skip sponsored sections, vendor announcements without editorial
  framing, and "best of" roundups with no analysis.
- **Graceful on empty** — if the scan returns nothing, report the searches used and suggest
  adding a `newsletters` Gmail label to improve future detection.
- **Confirm before saving** — never create a Drive doc without explicit confirmation.

## Example

**User:** "Give me a newsletter digest for this week"

→ Runs the above process and presents a tiered digest like the one in §5.

**User:** "What should I read this week?"

→ Same output, triggered by a different natural phrase.
