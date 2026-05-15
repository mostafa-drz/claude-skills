# Daily Skill Factory — Routine Spec

**Status**: active
**Runs on**: Claude infrastructure (cron, no laptop dependency)
**Cadence**: once per morning
**Owner**: [@mostafa-drz](https://github.com/mostafa-drz)

This document is the contract the routine follows every morning. The cron prompt is intentionally minimal — it just says "follow this spec from HEAD, today's date is X." All the thinking lives here, version-controlled, reviewable in a PR.

---

## 1. Purpose

Build one new Claude **Desktop** skill per day, end-to-end, in my voice, and surface it for review as a PR. The next morning, if yesterday's PR was merged, open a follow-up PR on [`mostafa-xyz`](https://github.com/mostafa-drz/mostafa-xyz) with a short note announcing it — so the repo and the blog stay in sync without manual work.

The bar: every skill that ships from this routine should be indistinguishable from one I wrote by hand. If a skill looks generic, the routine is broken — not the skill is "good enough."

---

## 2. Daily flow

Two phases. Phase A runs first because it depends on yesterday's outcome.

### Phase A — Sync yesterday to the blog (conditional)

1. Read [`runs.md`](./runs.md). Find the most recent row where `status = merged` **and** `note_pr` is empty.
2. If no such row exists → skip Phase A. Go to Phase B.
3. Otherwise: clone [`mostafa-xyz`](https://github.com/mostafa-drz/mostafa-xyz), branch `note/skill-<skill-slug>`, write a new MDX note at `src/content/notes/introducing-<skill-slug>.mdx`. See §5 for the note contract.
4. Open the PR. Title: `note: introducing /<skill-slug>`. Body: short summary, link to merged skills PR, link to the SKILL.md on `main`, embedded SVG preview.
5. Update yesterday's row in `runs.md`: set `note_pr` to the new PR URL.
6. Commit `runs.md` to the same skills-PR branch from Phase B (or a standalone bump commit on `main` if Phase B is also skipped — rare).

**Do not auto-merge.** Both PRs always wait for human review. Memory rule: never merge a PR until I review and approve.

### Phase B — Build today's new skill

1. **Refresh upstream docs** — Fetch the three canonical Claude Skills docs (see §3), write a dated snapshot to `automation/docs-cache/YYYY-MM-DD.md` with: source URL, fetch timestamp, key sections, diff vs the previous cache file (what changed since last run). If the API moved, surface it in the PR body.
2. **Pick a topic** — Web research, 3–6 sources, find one specific workflow a Claude Desktop skill could meaningfully solve **given current Desktop capabilities** (sandboxed VM, Google Workspace, MCP, code execution). See §4 for selection rules.
3. **Reject duplicates** — Scan `desktop/` and `code/` for existing skills with overlapping scope. If a near-duplicate exists, pick a different topic. Don't ship a remix.
4. **Build the skill** — Create `desktop/<skill-slug>/` with:
   - `SKILL.md` — see §5 for the contract.
   - `icon.svg` — see §6 for the SVG contract.
   - `DESIGN.md` — only if the skill has a renderer or report output. Skip otherwise.
5. **Update indexes**:
   - Add a row to the "Desktop Skills" table in root [`README.md`](../README.md).
   - Add the skill description to `skills.json`.
   - Append a row to [`runs.md`](./runs.md) with today's date, skill slug, the (about-to-be-created) PR placeholder.
6. **Open the PR** — Branch: `skill/desktop-<skill-slug>`. Title: `desktop: add <skill-slug>`. Body must include:
   - One-paragraph rationale ("why this skill, why today")
   - The research sources (URLs + tier labels per §4)
   - Required integrations (none / Google Workspace / specific MCP)
   - Embedded SVG icon preview
   - "What I rejected" — 1–2 lines on duplicates avoided
   - Link back to this spec at the commit SHA the routine ran from
7. **Update `runs.md`** with the real PR URL. Commit the update to the same PR branch.

---

## 3. Source-of-truth docs

The routine refreshes these every morning before doing anything else. The dated cache in `automation/docs-cache/` lets future agents see what was true on day N.

| URL | What it covers |
|---|---|
| https://support.claude.com/en/articles/12512180-using-skills-in-claude | End-user usage of skills in Claude.ai / Desktop |
| https://support.claude.com/en/articles/12512198-how-to-create-custom-skills | Authoring guide (frontmatter, structure, upload) |
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | Platform/API view of skills |
| https://github.com/anthropics/skills | Official example skills (compare structure, avoid copying ideas wholesale) |

If any URL 404s or moved, fetch the new canonical URL via web search, update this table in a follow-up PR, and continue with the new URL.

---

## 4. Topic selection rules

The routine must surface a genuinely useful, non-obvious workflow. Generic "AI assistant for X" topics are rejected.

### Source credibility tiers (mandatory — applies to all research)

Classify each source before citing:

- **Tier 1 — Primary**: official docs, standards bodies, peer-reviewed research, original developer blogs from the maintainer org. Cite freely.
- **Tier 2 — Practitioner**: well-known engineer/founder blogs with named authors, conference talks, GitHub repos with clear lineage. Cite with attribution.
- **Tier 3 — Synthesis**: high-quality aggregators (Hacker News threads with substantive comments, mature StackOverflow answers, well-edited Wikipedia). Use as signal, trace claims to Tier 1/2 before citing.
- **Tier 4 — Reject**: vendor marketing pages, SEO content farms, Medium posts without author credentials, "ultimate guide" pages, AI-generated listicles. Never cite. If a stat only appears on a marketing page, drop it.

### Topic must

- Solve a workflow that **breaks down today** without a skill (not "make X faster" — but "X currently requires 5 manual tabs and 20 minutes").
- Be feasible inside Claude Desktop's sandbox: no local filesystem, no shell, but **does** have Google Workspace, web search, sandboxed code execution, MCP integrations.
- Survive the "would I personally use this twice this month?" test.
- Not duplicate any of: existing `desktop/*` skills, the obvious `code/*` skills, or the Anthropic example skills.

### Topic must not

- Be a thin wrapper around a single API call.
- Require integrations the user doesn't plausibly have (niche enterprise SaaS).
- Be a content-generation skill that the model already does well by default (e.g., "summarize this article" — Claude already does that).

---

## 5. SKILL.md contract (Desktop)

Desktop skills are simpler than Code skills — no `allowed-tools`, no `disable-model-invocation`, no `$ARGUMENTS`. The full reference is in [../SKILLS_GUIDE.md](../SKILLS_GUIDE.md), but for routine-built skills the contract is:

### Frontmatter

```yaml
---
name: skill-slug                # lowercase, hyphens, ≤ 64 chars, matches folder
description: >-                  # THIRD PERSON, pushy, trigger-keyword-rich, ≤ 1024 chars
  Does X when the user asks for Y. <One concrete capability sentence.>
  <One "what it's for" sentence with trigger keywords.>
  Use when <trigger scenario 1>, <trigger 2>, or <trigger 3>.
---
```

Rules:
- **Third person.** "Researches…" not "I research…". The description is metadata, not narrative.
- **Pushy / broad triggers.** Claude under-fires on skill activation. Spell out the trigger phrases a user would naturally say.
- **No marketing fluff.** "Generates a structured briefing" beats "powerful AI-driven insights."

### Body structure (in order)

1. **`# Skill Name`** — title case, matches the slug.
2. One short paragraph framing what the skill does and when. Composite, not hypothetical (see §7 voice rules).
3. **`## Configuration`** — only if there are user-tunable defaults. Shown as a fenced block of `key: value` lines.
4. **`## Process`** — numbered steps. This is the bulk of the skill. Each step should be self-contained, scannable, with sub-bullets where helpful. Show example output shapes inline with fenced blocks.
5. **`## Guidelines`** — bullet list of principles ("Confirm before sending", "Detect, don't assume"). These are the rules that govern edge cases the Process doesn't enumerate.
6. **`## Example`** — one realistic invocation + expected output shape. Optional but recommended.

### Length budget

≤ 200 lines for Desktop skills. If it's longer, the process is too prescriptive — trust the model more.

---

## 6. SVG icon contract

Match the existing aesthetic in `code/should-i-buy/icon.svg`, `code/docs-doctor/icon.svg`, `code/sitemap-audit/icon.svg`, `code/emotional-recap/icon.svg`. The rules:

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="1.5"
     stroke-linecap="round"
     stroke-linejoin="round">
  <title><concept short — what the icon means></title>
  <!-- monochrome geometry on currentColor -->
  <!-- 1–3 small accent dots in the brand palette for state/meaning -->
</svg>
```

Conventions:
- **Canvas**: 24×24 viewBox (matches Lucide/Feather lineage).
- **Stroke**: 1.5 base, occasional 0.75 for grid/secondary lines, no thicker than 2.
- **Color**: monochrome `currentColor` for geometry. **Accent dots only** in brand palette:
  - Primary: `#ff5722` (mostafa.xyz brand)
  - Secondary: `#0ea5e9` (info blue)
  - Success: `#16a34a` (green)
  - Warning: `#f59e0b` / `#fbbf24`
  - Danger: `#dc2626`
- **Meaning**: every shape and dot should mean something. Include a `<title>` element explaining the concept in one line. No decorative noise.
- **Style**: line-icon discipline — minimal, geometric, readable at 22px. Not generative art, not hand-drawn.

If the SVG looks decorative or generic, redo it. The icon is part of the skill, not packaging.

---

## 7. mostafa-xyz note contract (Phase A)

A note announcing a new skill should feel like any other note on the site — reflective, observation-driven, useful — not a release-notes blurb.

### Frontmatter

```yaml
---
title: "Introducing /<skill-slug>: <one-line hook in my voice>"
description: "<one sentence, ≤ 160 chars, says what the skill does and why I made it>"
date: "YYYY-MM-DD"   # the day the note PR is opened
cover: "<URL to the SVG icon raw on GitHub, or a Cloudinary upload if available>"
---
```

### Body

1. **Open with a composite scene**, not an invented anecdote. Pattern: "The question I keep getting…" / "Every time I [recurring action], I…". Memory rule: composite openings, not single-person stories.
2. **The first image in the body is the cover.** Memory rule: cover = first image in post body, never a closing/decorative image. Use the SVG icon (large, framed) or a Cloudinary upload if the skill has a richer hero.
3. **Body sections** (loose, not mandatory):
   - What was breaking before
   - How the skill works (one paragraph, not a full SKILL.md repeat)
   - One honest limitation
   - A link to the GitHub skill folder
4. **Voice**: first person, reflective, neuroscience/research-backed where genuinely relevant. No "powerful", no "game-changing", no consultant framing. Memory rule: no client names, no consultant/contractor positioning — say "engineer", "project", "product".
5. **Length**: 250–500 words. This is a note, not an essay.
6. **Closing**: one short reflection, optionally a pull-quote. No CTA.

### PR

Title: `note: introducing /<skill-slug>`. Body links the skills PR, the SKILL.md on `main`, and a one-line summary. Auto-deploy on merge handles the rest — but the memory rule "verify in prod after merge" says: after the PR is merged, the routine should curl prod and confirm the note returns 200 with the right title. Do this check **inside the next morning's run** rather than blocking the current run.

---

## 8. runs.md schema

`runs.md` is the routine's memory. Append-only, parseable. One row per run, newest at the bottom (so daily appends don't churn the diff).

```markdown
| date       | skill_slug          | skills_pr                                       | status | note_pr                                    | notes |
|------------|---------------------|-------------------------------------------------|--------|--------------------------------------------|-------|
| 2026-05-15 | desktop/meeting-prep | https://github.com/mostafa-drz/claude-skills/pull/52 | open   |                                            |       |
```

- `status` ∈ `open`, `merged`, `closed`. The routine reads PR state from GitHub at the start of each run and refreshes this column for the last 7 rows.
- `note_pr` is filled by Phase A when the announcement note is opened.
- `notes` is freeform — failures, manual overrides, anomalies.

---

## 9. Failure modes

When the routine gets stuck, it should **not** force a low-quality skill through. Better to skip a day than ship junk.

| Situation | Routine behavior |
|---|---|
| Can't find a topic that passes §4 | Skip Phase B. Append a row to `runs.md` with `status = skipped` and a 1-line `notes` reason. Don't open a PR. |
| Docs cache fetch fails (all 3 URLs down) | Skip Phase B. Skill authoring without current docs risks shipping outdated frontmatter. Append `status = skipped`. |
| Yesterday's skills PR was closed (not merged) | Phase A: skip. Routine doesn't argue with rejections. Notes column: "yesterday rejected, no announce." |
| Yesterday's skills PR is still open | Phase A: skip. Don't pre-announce. |
| Repo has uncommitted changes on `main` (from a manual edit) | STOP. Open an issue describing the dirty state. Don't branch off dirty `main`. Memory rule: never silently overwrite uncommitted work. |
| New skill duplicates an existing one (caught after authoring) | Discard, pick a new topic, retry once. If retry also duplicates, skip the day. |

Every failure path **writes to `runs.md`** so the trail is visible.

---

## 10. What this routine deliberately doesn't do

- **No auto-merge.** Every PR waits for me. This is the whole point of the routine — surface for review, don't decide.
- **No mass output.** One skill per day. Not three, not a batch on weekends. Cadence > volume.
- **No silent edits to existing skills.** This routine only **adds**. If an existing skill needs work, that's a separate task.
- **No cross-posting to LinkedIn / X / etc.** The mostafa-xyz note is the surface; further amplification is a separate decision.
- **No vendor links in skill bodies.** Skills should work against the user's own integrations, not steer them to specific products.

---

## 11. Worked example (illustrative)

> **Day 1 — 2026-05-15, Phase B only (first run)**
>
> 1. Refreshes docs → writes `docs-cache/2026-05-15.md`. No prior cache, so no diff section.
> 2. Researches: "what's a workflow that breaks for people running multiple recurring meetings without a dedicated EA?" Lands on a **meeting-prep** skill that pulls Calendar + relevant Drive docs + Gmail thread + Linear context for the next meeting, into a 30-second brief.
> 3. Checks `desktop/` and `code/` — no overlap. `inbox-catchup` is broader; this is focused per-meeting.
> 4. Writes `desktop/meeting-prep/SKILL.md`, `desktop/meeting-prep/icon.svg` (calendar grid with a single accent dot on "now").
> 5. Updates root README and `skills.json`.
> 6. Appends `runs.md` row.
> 7. Opens PR. Title: `desktop: add meeting-prep`.
>
> **Day 2 — 2026-05-16**
>
> - Phase A: checks `runs.md`. Yesterday's PR is **merged**. Branches `mostafa-xyz`, writes `introducing-meeting-prep.mdx`. Composite opening: "Every Monday I open Calendar and feel a tiny dread — three 1:1s before noon and I haven't read any of the docs yet." Cover = the SVG. Opens PR.
> - Phase B: refreshes docs, picks a new topic (e.g. `desktop/expense-export` — pulls Gmail receipts + Drive + builds a CSV ready for accounting), authors, opens PR.

---

## 12. Changing the routine

1. Edit this file on a branch.
2. Open a PR. Review like any other change.
3. On merge, the next cron firing picks it up — the cron prompt always reads HEAD.

The cron's schedule (time of day, timezone, cadence) is **not** version-controlled here. That's a deployment concern, managed via the `/schedule` skill locally. If the schedule changes, leave a one-line note in [`README.md`](./README.md) recording when and why.
