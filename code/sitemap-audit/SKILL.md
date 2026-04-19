---
name: sitemap-audit
description: >-
  Audits a website's SEO discoverability by cross-referencing the codebase with live production.
  Catches sitemap, robots.txt, and canonical inconsistencies, framework-specific anti-patterns
  (Next.js App Router metadata cascade, Astro/Nuxt equivalents), redirect-chain issues, and
  Google Search Console stuck states. Produces a prioritized, evidence-backed report with
  suggested fixes. Use when Search Console shows "Couldn't fetch", pages aren't being indexed,
  or you want an SEO health check before a launch or after a routing refactor.
argument-hint: [url-or-subcommand]
context: fork
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - WebFetch
---

# sitemap-audit

Diagnostic SEO audit. **Report only** — never modifies code or Search Console state. Cross-references the codebase with live production to catch issues that live-only tools miss (like framework metadata cascade bugs).

## Preferences

_Read `~/.claude/skills/sitemap-audit/preferences.md` using the Read tool. If not found, proceed with onboarding._

## Context

_On startup, use Bash to detect (skip any that fail):_
- _Current repo path: `pwd`_
- _Framework fingerprint: `package.json` (Next.js / Astro / Nuxt / SvelteKit / generic), `astro.config.*`, `nuxt.config.*`_
- _Has `src/app/` (App Router) or `pages/` (Pages Router)_
- _Git state: `git status`, `git log -1 --format=%h`_

## Command Routing

Check `$ARGUMENTS` for subcommands:

### `help`

Display:

```
sitemap-audit — SEO health check across codebase + live production

Usage:
  /sitemap-audit                              Audit site from preferences
  /sitemap-audit <url>                        Audit a specific URL (one-off)
  /sitemap-audit config                       Set preferences
  /sitemap-audit reset                        Clear preferences
  /sitemap-audit help                         This help

What it checks:
  1. Sitemap fetchability + XML validity + URL count
  2. robots.txt content + sitemap pointer consistency
  3. Every URL in sitemap: 200 status, self-canonical match
  4. Response headers: Content-Type, X-Robots-Tag, HSTS
  5. Apex ↔ www redirect chain depth + consistency
  6. Codebase anti-patterns (framework-specific)
  7. SSR vs JS-only rendering (Googlebot compatibility)
  8. DNS: site verification TXT records for GSC
  9. (Optional, with permission) Live GSC check via Chrome extension

Output: prioritized report (P0 blocks indexing / P1 hurts rankings / P2 nice-to-have).

Current preferences: [read from preferences.md or "none — will onboard"]
```

Then stop.

### `config`

Use **`AskUserQuestion`** to collect:

**Q1** — "Production URL to audit? (e.g. `https://www.example.com`)"
- Free text.

**Q2** — "Repo path for codebase-aware checks?"
- Options: "Current directory (`pwd`)", "Specify path", "Skip codebase checks"

**Q3** — "Do you have a Google Search Console property you want the skill to explore? (optional, requires Claude for Chrome extension)"
- Options: "Yes, and I'll grant browser access when asked", "No / skip GSC check", "Later — remind me in each run"

**Q4** — "Save report to a file after each run?"
- Options: "No — just print to chat", "Yes — `.sitemap-audit/report-<date>.md` in repo", "Yes — custom path"

Save to `~/.claude/skills/sitemap-audit/preferences.md`. Summary. Stop.

### `reset`

Delete `~/.claude/skills/sitemap-audit/preferences.md`. Confirm: `Preferences cleared.` Stop.

### First-time experience (no preferences, no subcommand)

Show one-line invitation (don't block):

```
First time running /sitemap-audit? Run `/sitemap-audit config` for persistent setup,
or answer a couple of one-off questions to continue.
```

Then ask (via AskUserQuestion or inline) ONLY: **production URL** (required), **codebase path** (default: cwd). Skip GSC on first run.

### Default — run the audit

Continue to **Audit steps** below.

---

## Audit steps

Execute these in order. Run independent curls in parallel. Every finding must cite evidence (exact curl output, file:line, or DNS record).

### 1. Fetch baseline (live production)

Record HTTP status + final URL + Content-Type + first hop for each:
```bash
curl -sI <url>/
curl -sI <url>/sitemap.xml
curl -sI <url>/robots.txt
curl -sI <url-apex>/                  # if www is canonical, or vice versa
curl -sIL <url-apex>/sitemap.xml      # follow to detect redirect chain depth
```

Flag P0 if:
- Sitemap returns non-200
- Sitemap Content-Type is not `application/xml` or `text/xml`
- robots.txt returns non-200
- Redirect chain depth > 1 (multiple hops slow Googlebot)

### 2. Validate sitemap XML

```bash
curl -s <sitemap-url> | xmllint --noout -   # VALID or error
curl -s <sitemap-url> | grep -c "<loc>"     # URL count
```

Flag P0 if XML invalid. Flag P1 if URL count is 0 or exceeds 50,000 (sitemap split needed).

### 3. Audit every URL in sitemap

For each `<loc>`:
- HEAD request — expect 200
- GET + extract `<link rel="canonical">`
- Compare canonical to the URL itself (self-canonical)

Count: **correct canonical** (matches own URL), **no canonical** (Google self-canonicals by default, acceptable), **WRONG canonical** (points elsewhere — P0).

Classify wrong canonicals by where they point:
- All → same root URL? → **framework cascade bug** (e.g., Next.js root layout `alternates.canonical` leaking)
- Inconsistent wrong targets? → per-page hardcoding issue

### 4. Headers audit

On homepage + sitemap + a sample article:
- `X-Robots-Tag` — any `noindex` here silently de-indexes the URL. P0 if found unexpectedly.
- `Strict-Transport-Security` — presence is good.
- `Content-Type` — `text/html; charset=utf-8` expected for pages.

### 5. Canonical / host consistency

If site has both apex and www:
- Which one is canonical? (check `<link rel="canonical">` on homepage)
- Does DNS/redirect match the canonical? Both should agree.
- Does the sitemap use the canonical host? (Sitemap URLs mismatching canonical host → Google treats sitemap URLs as non-canonical alternates.)
- Does robots.txt's `Sitemap:` pointer use the canonical host?

**Common P0 pattern:** sitemap + robots canonicalize one host, but page-level `<link rel="canonical">` points to the other. Seen in Next.js sites that fix sitemap/robots but forget `metadataBase` or hardcoded URLs in layouts.

### 6. Codebase anti-pattern scan

**Only if codebase path is set.** Detect framework from package.json, run framework-specific checks.

#### Next.js App Router (15+)

Read these files:
- `next.config.*`, `next.config.ts`
- `src/app/layout.tsx` (root) — scan for `metadata.alternates.canonical`
- `src/app/sitemap.ts` — check `baseUrl` consistency with production canonical host
- `src/app/robots.ts` — check `sitemap:` pointer matches
- `src/lib/metadata.ts` or similar — grep for hardcoded URLs: `grep -rn "https?://<apex-domain>" src/`

Anti-patterns to flag:
- **P0 — Root canonical cascade:** `alternates.canonical` set in `src/app/layout.tsx` cascades to every child route that doesn't override. Result: every page claims to be the homepage. Fix: remove root canonical; let pages self-canonical or add explicit per-route.
- **P0 — Host mismatch:** `siteUrl` in `src/lib/metadata.ts` is apex but sitemap/robots/redirect canonicalize to www (or vice versa). Grep: `grep -rn "https://<apex>" src/ --include="*.ts" --include="*.tsx"`.
- **P1 — Missing `metadataBase`:** root layout has no `metadataBase`, so relative URLs in metadata won't resolve.
- **P1 — Dynamic sitemap using filesystem at runtime:** `readdirSync(join(process.cwd(),...))` in `sitemap.ts` can fail in serverless if files not bundled. Prefer compile-time aggregation.
- **P2 — `lastModified` omitted:** sitemap entries without `lastModified` give Google no crawl-priority signal.

#### Next.js Pages Router

- Check `pages/sitemap.xml.ts` or similar; flag if missing.
- Check `<Head>` in `_document.js` / `_app.js` for canonical setup.
- Flag P1 if canonical is set in `_document` (applies site-wide, same cascade trap).

#### Astro

- Check `astro.config.mjs` for `site` (required for canonical URLs).
- Check `@astrojs/sitemap` integration — flag P1 if site has >20 pages and no sitemap integration.
- Check `<BaseHead>` or layout for canonical.

#### Nuxt

- Check `nuxt.config.ts` → `site` or `@nuxtjs/sitemap` module.
- Check `useHead` canonical usage.

#### SvelteKit

- Check `svelte.config.js` → `kit.prerender`.
- Check `+layout.svelte` `<svelte:head>` for canonical.

#### Generic / unknown framework

- Grep for `<link rel="canonical"` patterns in source.
- Skip framework-specific checks, report "framework not auto-detected".

### 7. SSR / rendering check

```bash
curl -s <url>/ | grep -oE "<h1|<article|<main" | head -5
curl -s <url>/ | grep -c "<meta\|<link"
```

Flag P0 if the HTML response is essentially empty (client-rendered SPA). Googlebot renders JS but delays indexing.

### 8. DNS / verification check

```bash
dig +short <apex-domain> A
dig +short <apex-domain> TXT
dig +short www.<apex-domain> CNAME
```

Flag:
- P2 (info) — presence of `google-site-verification=...` TXT. If present, Domain property is set up in GSC (ideal).
- P1 — apex has no A record but www does (or vice versa) — bots that pick the "wrong" host will fail.
- P2 — multiple google-site-verification TXT (usually harmless but worth flagging).

### 9. Optional — Google Search Console live check

Only if user granted permission in preferences or this run.

Using the Claude for Chrome extension (`mcp__claude-in-chrome__*`):
1. Navigate to `https://search.google.com/search-console/sitemaps?resource_id=sc-domain%3A<domain>` (or `?resource_id=<encoded-url>` for URL-prefix properties)
2. Use `get_page_text` to read the sitemaps table
3. Report: property type, submitted sitemaps, status, last read date, discovered pages count

**Do NOT** modify GSC state (no remove/resubmit). Read-only.

If any sitemap shows "Couldn't fetch" and production verifies healthy → flag as P1 with explicit user action: "remove + resubmit sitemap in GSC (use trailing slash trick to cache-bust if removal alone doesn't clear it)."

### 10. Build the report

Format:

```
╔═══════════════════════════════════════════════════════════════╗
║  sitemap-audit — <domain>                                     ║
║  <date> · <framework> · <N urls> in sitemap                   ║
╚═══════════════════════════════════════════════════════════════╝

SUMMARY
  P0 (blocks indexing):  <n>
  P1 (hurts rankings):   <n>
  P2 (nice-to-have):     <n>

P0 — Blocks indexing
  • <finding>
    Evidence: <file:line or curl output>
    Fix:      <specific action>

P1 — Hurts rankings
  • ...

P2 — Nice-to-have
  • ...

CLEAN PASSES
  ✓ Sitemap XML valid
  ✓ All <N> URLs return 200
  ✓ robots.txt consistent
  ...

NEXT ACTIONS (prioritized)
  1. [P0] <most important fix>
  2. [P0] <next>
  3. [P1] <next>

GSC ACTIONS (manual — skill does not modify GSC)
  • <specific click path if applicable>
```

### 11. Offer follow-up

After displaying the report, ask:

> **Want me to open a fix PR for P0/P1 findings?**
> This would modify code only — never GSC. You'll review the PR before merge.

If yes:
- Create branch `fix/seo-sitemap-audit-<date>`
- Apply per-framework fixes (e.g., remove Next.js root canonical, fix host mismatch)
- Include detailed commit message citing evidence
- Open PR with before/after expected canonical count
- **Do not merge** — hand back for review.

If no: done.

If preferences.md has `saveReport: true`: write the report to the configured path.

## Memory and preferences

Save to `~/.claude/skills/sitemap-audit/preferences.md`:

```markdown
# /sitemap-audit preferences
Updated: <date>

## Defaults
- url: https://www.example.com
- repoPath: /Users/x/Dev/myproject
- gscMode: ask-per-run | always-skip | always-run
- saveReport: false | path
- framework: nextjs-app | nextjs-pages | astro | nuxt | sveltekit | generic
```

Learn silently:
- User corrects detected framework → save.
- User always skips GSC → switch to `always-skip`.
- User always requests PR at the end → save as default.

## Content guidelines

- Every finding needs evidence (curl output, file:line, or DNS record). No vibes-based claims.
- Use three tiers: P0 / P1 / P2. Don't invent more.
- Cite the Next.js version when reporting framework-specific issues (read from package.json).
- When a finding is framework-specific, name the pattern (e.g., "Next.js App Router root layout canonical cascade").
- If a check can't run (tool unavailable, permission denied), note it in the report, don't silently skip.

## Limits

- Does **not** fix Google Search Console state (GSC is shared; user must click).
- Does **not** modify production directly (only via a PR for review).
- Does **not** require API keys (everything is curl + read-only DOM).
- Will **not** auto-submit sitemaps or request indexing — GSC quotas and user intent.
