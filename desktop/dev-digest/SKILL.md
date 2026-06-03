---
name: dev-digest
description: >-
  Scans the web for ecosystem signals on the technologies you care about —
  recent releases, Hacker News threads, GitHub activity, official changelog
  highlights — and delivers a structured tech pulse brief. Use when you want
  to know what changed in a technology this week, when asking what's new in
  Rust or React or any tool you follow, when checking for major dependency
  releases, or when you want a curated weekly signal sweep instead of manually
  scanning HN, GitHub trending, and every project blog yourself.
---

# Dev Digest

Every week there are things worth knowing across the technologies you work
with. New releases, lively HN debates, ecosystem shifts, a repo quietly going
viral. Without a deliberate scan, these slip by — or you find them two months
later when a colleague mentions them. This skill does the scan: you say which
technologies matter to you, and it surfaces what actually changed.

## Configuration

```
topics:        # Comma-separated — e.g. "Rust, React, PostgreSQL, Nix"
               # Required on first run; saved to preferences for future runs
time_window: 7d  # How far back to look (default: 7 days)
depth: standard  # "quick" (releases + top HN only) or "standard" (+ GitHub trends + blogs)
```

## Process

### 1. Get Topics

If topics are saved in preferences, confirm them:

> Running dev-digest for: **Rust, React, PostgreSQL** (saved from last run)
> Change topics? Or just run?

If no saved topics, ask:

> Which technologies should I track this week?
> Examples: "TypeScript, Go, Postgres" or "React 19, Bun, Deno, Tailwind"
> I'll remember these for next time.

Accept free-form input. Save the list to preferences after confirming.

### 2. Scan Each Technology

For each topic, run a focused sweep of three signal sources:

**Releases & Changelogs**
- Search for `{topic} release changelog {current_week_or_month} 2026`
- Target: official project blog, GitHub Releases page, or major version announcement
- Extract: version number, headline features, notable breaking changes

**Community Pulse (Hacker News)**
- Search for recent HN threads: `site:news.ycombinator.com {topic}`
- Look for threads with substantial engagement (100+ points, active comments)
- Extract: the core argument or observation the thread surfaced, not just the headline

**Ecosystem Activity (GitHub)**
- Search for trending repositories or significant projects related to the topic
- Look for "X alternative written in Y" announcements, newly viral libs, project migrations
- Extract: what the repo does, why it's gaining traction

Skip a source if it returns nothing relevant. Note the gap rather than fabricating.

### 3. Score Each Signal

For each extracted item, assign a signal strength:

- **🔴 High** — official release with new capabilities, or a thread that surfaced a genuine debate or shift in best practice
- **🟡 Medium** — notable but not actionable yet (RC/beta, exploratory discussion, interesting repo but nascent)
- **⚪ Low / Noise** — minor patch, vendor marketing post, announcement without substance

Only surface High and Medium signals in the main brief. Low signals go in a brief "also noted" footer, if any.

### 4. Present the Brief

```
⚡ Dev Digest — week of Jun 2–8, 2026

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rust
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 Rust 1.89 released (Jun 5)
   Key additions: precise capturing in impl Trait, trait upcasting stable.
   The precise-capture RFC was debated for 2 years — worth reading the
   release notes if you use `impl Trait` in return position.
   → https://blog.rust-lang.org/...

🟡 HN thread: "Why I moved my data pipeline from Polars back to DuckDB"
   500 pts, 280 comments. The author found Polars' lazy eval semantics
   surprising at scale; commenters largely disagree but surface real
   edge cases in join behavior. Useful if you're evaluating either.
   → https://news.ycombinator.com/...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
React
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 React Compiler now stable in React 19.1 RC
   The auto-memoization compiler shipped as stable in the RC. Framework
   teams (Next, Remix) are enabling it by default — worth checking if
   your app has any rules-of-hooks violations before upgrading.

⚪ Also noted: new article on React Server Components caching behavior
   (no new information, re-explains existing docs)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PostgreSQL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 pgvector 0.9 drops in-memory HNSW indexing
   No more IVFFlat tuning for most vector workloads. The thread on this
   is worth reading — the accuracy/latency benchmarks are clear.
   → GitHub release link

Nothing else significant in Postgres ecosystem this week.

──────────────────────────────────
3 topics scanned · 5 signals found (2 high, 2 medium, 1 low)
Time window: Jun 2–8, 2026
```

### 5. Save Preferences

After presenting the brief, update the topic list in preferences if the user
modified it. Note the date of the last run so the next invocation can use
`since last run` as the default time window.

## Guidelines

- **Concrete beats current** — a well-explained 2-week-old release is more useful than a vague headline from yesterday. Prioritize signal clarity over recency for its own sake.
- **Don't repeat what the headline says** — extract the *implication*: what should the user do differently, what changed in the ecosystem, what debate was settled.
- **One source per item** — if an HN thread and a blog post cover the same release, merge them into one item, not two.
- **Honest gaps** — if a technology had no meaningful news this week, say so in one line. Don't pad.
- **No marketing posts** — vendor "X is now Y times faster" posts without benchmarks or methodology are noise, not signal.
- **Save topics to memory** — the skill is most useful when you don't have to re-specify your stack every time.

## Example

**User:** "Dev digest for Bun, Deno, and Node"

→ Searches for releases across all three runtimes, finds the recent Bun 2.0 announcement
and a lively HN thread comparing startup time with Deno 2. Node had a quiet week.
Presents a brief with 3 items: one high (Bun 2.0), one medium (the HN comparison thread),
and notes that Node had no significant news. Done in about two minutes.
