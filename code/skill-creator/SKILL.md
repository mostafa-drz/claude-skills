---
name: skill-creator
description: >-
  Creates new Claude Code skills interactively, enforcing every convention in
  SKILLS_GUIDE.md plus the learning, configurability, and feedback patterns
  used by the best in-tree skills (svg-art, should-i-buy, step-through). Asks
  contextual questions about purpose, side effects, tools, and workflow, then
  generates a complete SKILL.md with three-tier preferences (Defaults /
  Profile / Learned), a feedback subcommand, a session log, and a feedback
  journal — unless the skill is genuinely stateless. Use when creating a new
  skill or scaffolding one.
argument-hint: [skill-name] [--from-description "..."]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
---

# Skill Creator

Create new Claude Code skills interactively, following all conventions from `SKILLS_GUIDE.md` **and** the learning/configurability/feedback patterns proven in the best existing skills.

## Preferences

_On startup, use the `Read` tool to load `~/.claude/skills/skill-creator/preferences.md`. If missing, treat as "no preferences set"._

## Context

Before starting:
- Use the `Glob` tool to discover existing skills at `~/.claude/skills/*/SKILL.md` (so you don't reinvent or collide with a name).
- Read `~/.claude/skills/SKILLS_GUIDE.md` once at Step 3 — it's the canonical manifest.
- Treat `svg-art`, `should-i-buy`, and `step-through` as the gold-standard reference for learning + feedback patterns.

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help, then stop
- **`config`** → interactive setup, then stop
- **`reset`** → delete `~/.claude/skills/skill-creator/preferences.md`, confirm, stop
- **`--from-description "..."`** → skip Q1, use the quoted text as the skill's purpose
- **anything else** (including empty) → run the skill

### Help

```
Skill Creator — Creates Claude Code skills, manifest-compliant by default

Usage:
  /skill-creator                             Interactive skill creation
  /skill-creator <name>                      Start with a name pre-filled
  /skill-creator --from-description "..."    Start from a plain-text description
  /skill-creator config                      Set preferences
  /skill-creator reset                       Clear preferences
  /skill-creator help                        This help

Examples:
  /skill-creator                             Full interactive walkthrough
  /skill-creator deploy-preview              Create a skill named "deploy-preview"
  /skill-creator --from-description "A skill that triages PR comments"

Current preferences:
  (loaded from ~/.claude/skills/skill-creator/preferences.md)
```

### Config

Use `AskUserQuestion` to collect:

- **Q1** — Default skill location: `~/.claude/skills/` (standard) or custom path
- **Q2** — Auto-update inventory in `SKILLS_GUIDE.md` after creation: yes/no
- **Q3** — Publish repo path (e.g. `~/Dev/claude-skills`) or "none"
- **Q4** — Default learning posture: `learning-on` (include feedback + journal + sessions) / `learning-off` (stateless tool by default) / `ask-each-time`

Save to `~/.claude/skills/skill-creator/preferences.md`.

### Reset

Delete `~/.claude/skills/skill-creator/preferences.md` and confirm: `Preferences cleared. Using defaults.`

## First-time detection

If no preferences file exists:

> First time using `/skill-creator`? Run `/skill-creator config` to set defaults, or just continue with sensible defaults.

Then proceed.

---

## Manifest patterns reference (read once, apply every time)

Every generated SKILL.md **must** satisfy these — no exceptions unless explicitly justified to the user.

### Required (from `SKILLS_GUIDE.md`)

1. **Frontmatter** — `name` (kebab-case, ≤64 chars), `description` (third-person, "Use when …" trigger, ≤1024 chars), `argument-hint`, minimal `allowed-tools`.
2. **`disable-model-invocation: true`** — required for any skill that creates / modifies / pushes / posts.
3. **`AskUserQuestion`** in `allowed-tools` — every skill needs it for help/config/reset.
4. **Subcommand pattern** — `help`, `config`, `reset`, default behaviour.
5. **`Read` of preferences on startup** — never `!` backtick interpolation for `~/.claude/` paths.
6. **First-time detection** — warm one-liner, never blocking.
7. **No `!` backtick interpolation** — use runtime "_On startup, use Bash to …_" instructions instead.
8. **Under 500 lines** — push reference material to `reference/` or `examples/`.
9. **Numbered workflow** — checklists, not prose.
10. **Graceful degradation** — every external read/tool call must have a fallback.
11. **Validation loops** — after any action, verify before moving on.

### Required for skills with discrete sessions / outputs (default ON unless stateless)

12. **Three-tier preferences format**:
    ```markdown
    # /<skill> preferences
    Updated: YYYY-MM-DD

    ## Defaults
    - knob: value

    ## Profile (optional — edit freely)
    - user-editable bias

    ## Learned
    - (populated from feedback over time)
    ```
13. **`feedback` subcommand** — `/skill feedback` collects ratings on the most recent session via `AskUserQuestion`.
14. **`feedback-journal.md`** — append a per-session block with a `Signal:` one-liner generalisation.
15. **`sessions/YYYY-MM-DD-HHMM.md`** — incremental session log when the skill has discrete invocations worth tracking.
16. **Promotion rule** — when 3+ sessions show the same signal, promote it to `## Learned` in `preferences.md`. Mention once: "Noticed you consistently … Saved as standing default."
17. **Drift correction** — when a Learned rule is contradicted in 2 newer sessions, demote it (log the demotion in the journal). Never leave stale rules.
18. **`Step 0 — Load learning context`** — read `preferences.md` and `feedback-journal.md` before the main workflow. Continue silently on missing files.
19. **Invite feedback line** at the end of the workflow: `Run /<skill> feedback — even one rating helps me sharpen defaults.`
20. **Reset clears the lot** — `preferences.md`, `feedback-journal.md`, `sessions/`, any `resume-state.md`.

### Recommended (apply when relevant)

21. **`resume-state.md` + `/<skill> resume`** — for any skill where the user can stop mid-flow.
22. **Confirmation policy** — destructive-only by default; configurable to "every action" via preferences.
23. **Pre-selection logic in `AskUserQuestion`** — bias the default option using `Learned` rules.
24. **Configurability ≥ 3 knobs** — depth, verbosity, output format, source selection, confirmation policy. A skill with only 1 knob is under-specified.
25. **Templates (`templates/<name>.md`)** — when a skill has a recurring "preset workflow" with parameterized inputs (e.g. `/publish-note --from-template=raw-idea "<idea>"`), expose it as a template file inside the skill directory. Each template is a YAML-frontmatter + markdown file declaring `inputs`, `tasks`, `constraints`, `tools`, `postProcesses`. The skill should support `--from-template=<name>` routing in addition to its standard flow. See `~/.claude/skills/publish-note/templates/raw-idea.md` for the canonical example. Templates are how a skill compresses an entire conversational workflow ("I want X, with these constraints, ending in Y") into a single command.

### When to skip the learning tier (12–20)

Skip only if **all** of the following are true:
- The skill has no per-session output worth rating (e.g. `aws-mfa` writes a credential file — there's nothing to thumbs-up).
- The skill is purely procedural and identical every run.
- There's no per-severity / per-output category that could be biased over time.

If skipping, document it in the SKILL.md's Principles section: `Stateless by design — no feedback loop because [reason].`

---

## Step 1 — Understand the skill's purpose

If `$ARGUMENTS` contains `--from-description`, use that text. If `$ARGUMENTS` is a bare name, pre-fill the name and ask the rest. Otherwise, ask:

> **What should this skill do?** Describe the workflow in a sentence or two.

Extract:
- **Working name** (kebab-case)
- **Core verb** (creates, analyses, fetches, organises, walks through, …)
- **Trigger phrase** (when should the user reach for it)

Confirm with the user: `I'll call this /skill-name — a skill that [one-liner]. Sound right?`

## Step 2 — Determine side effects, context, and learning posture

Use **AskUserQuestion** with **3 questions in one batch**:

**Q1 — Side effects:** Does this skill create, modify, push, or post anything?
- `Yes` → `disable-model-invocation: true`
- `No (read-only)` → omit `disable-model-invocation`
- Pre-select Yes if the description mentions create/post/push/update/write/deploy.

**Q2 — Context needs:** Does this skill need the current conversation history?
- `Yes` (builds on what we've discussed) → no `context` field
- `No` (self-contained, works from its own inputs) → `context: fork`
- Pre-select fork if the skill processes external input only (URLs, file paths, pasted text).

**Q3 — Learning posture:** Should this skill learn from per-session feedback?
- `Yes — full learning tier` (preferences + journal + sessions + feedback subcommand) — pre-select for any skill with discrete outputs, decisions, or judgement calls
- `No — stateless tool` — pre-select only for purely procedural skills (e.g. credential refresh, fixed pipeline runners)
- If `Yes`, items 12–20 of the manifest reference are now mandatory.

## Step 3 — Identify tools needed

Read `~/.claude/skills/SKILLS_GUIDE.md` to confirm conventions.

Use **AskUserQuestion** (multiSelect):

> **Which capabilities does this skill need?**

- **Read files** → `Read`, `Glob`, `Grep`
- **Edit files** → `Write`, `Edit`
- **Run commands** → `Bash` (use `Bash(git *)` / `Bash(gh *)` glob patterns when scoping)
- **Ask questions** → `AskUserQuestion` (always include — auto-add even if not picked)
- **Web access** → `WebSearch`, `WebFetch`
- **Linear** → use `mcp__claude_ai_Linear__*` (NOT `mcp__linear-server__*`):
  - Read: `list_issues`, `get_issue`, `list_comments`, `list_projects`, `get_project`, `list_teams`
  - Write: above + `create_issue`, `update_issue`, `create_comment`
- **Vercel / Slack / Notion / Chrome / Playwright** → pick specific MCP tools by action

Always include `AskUserQuestion`. Always keep the list **minimal** — granting `Write`/`Edit` to a read-only skill is a bug.

## Step 4 — Design the workflow

Apply the manifest reference. Draft a numbered workflow that includes (in order, when learning tier is on):

1. **Step 0 — Load learning context** (read preferences + journal)
2. Domain-specific steps (4–8 of them)
3. **Step N–1 — Final summary**
4. **Step N — Invite feedback** (one-line pointer to `/<skill> feedback`)

For stateless skills, drop steps 0 and N.

Identify ≥3 configurability knobs (depth, verbosity, format, source, confirmation policy, …). Identify the 1–3 decision points that get an `AskUserQuestion`. Identify what the `feedback` subcommand will rate (per-severity defaults? per-output style? per-source pace?).

Present the outline:
> Here's the workflow:
> 1. Load learning context
> 2. …
> N. Invite feedback
>
> Configurability knobs: [list]. Feedback dimensions: [list]. Want to adjust?

## Step 5 — Determine arguments and flags

Propose:
- Positional argument (if any)
- Standard flags: `--filter`, `--start`, `--from`, `--dry-run`, `--verbose` (only those that fit)
- Subcommands beyond the standard four: `feedback`, `resume` (if applicable)

Confirm via `AskUserQuestion` or inline.

## Step 5.5 — Templates (optional, ask once)

Ask once via `AskUserQuestion`:

> **Will this skill have parameterized preset workflows (templates)?**
> - **Yes** — I expect users to invoke this with a recurring pattern of inputs/constraints (e.g. "raw idea → finished output with these tools and constraints"). Add `templates/<name>.md` directory + `--from-template=<name>` routing.
> - **No** — single workflow only.
> - **Maybe later** — leave the directory off; can be added later via `/skill-templates` (planned skill).

If **Yes**:
1. Create `~/.claude/skills/<skill-name>/templates/` directory.
2. For each template the user names, scaffold `templates/<name>.md` with the canonical frontmatter:
   ```markdown
   ---
   name: <template-name>
   description: >-
     <one-liner — what this template does, what it skips, what it adds>
   inputs:
     <input>:
       type: string | list
       required: true | false
       default: <value>  # if not required
   tasks: [<ordered list of step keywords>]
   constraints: [<rules the run must respect>]
   tools: [<preferred tools>]
   postProcesses: [<actions after main work>]
   ---

   # Template: <name>

   ## When to use
   <trigger scenario>

   ## Flow (default tasks)
   1. **<task>** — <how to execute>
   ...

   ## Default constraints (why each one)
   - **<constraint>** — <reason>

   ## Examples (from prior runs)
   - <date>: <what happened>
   ```
3. Add `templates` and `--from-template=<name>` routes to the skill's Command routing block.
4. Add a `## Templates` section in the SKILL.md explaining the convention and how the skill loads/parses templates.

Reference: `~/.claude/skills/publish-note/templates/raw-idea.md` is the canonical example.

## Step 6 — Generate the SKILL.md

Assemble. Use the structure checklist below. Walk through it top to bottom — every box must be ticked or explicitly justified as "skip" with a Principles note.

### Structure checklist

**Frontmatter**
- [ ] `name` — kebab-case, matches directory
- [ ] `description` — third-person, includes "Use when …" trigger, ≤1024 chars, mentions learning if applicable
- [ ] `argument-hint` — reflects positional + flags + subcommands
- [ ] `disable-model-invocation: true` — set if side effects confirmed in Step 2
- [ ] `context: fork` — set if confirmed self-contained in Step 2
- [ ] `allowed-tools` — minimal list from Step 3, includes `AskUserQuestion`

**Top-level sections**
- [ ] `## Preferences` — runtime Read instruction for `preferences.md` + Defaults list
- [ ] `## Context` — runtime Bash/Read instructions, no `!` backticks
- [ ] `## Command routing` — help / config / reset / **feedback** (if learning) / **resume** (if applicable) / default
- [ ] `### Help` block — CLI format with Current preferences line
- [ ] `### Config` block — `AskUserQuestion` + write to `preferences.md` in **three-tier format**
- [ ] `### Reset` block — deletes preferences + **journal + sessions + resume-state** when learning tier is on
- [ ] `## First-time detection` — warm one-liner, non-blocking

**Workflow**
- [ ] `### Step 0 — Load learning context` (skip only for stateless)
- [ ] Numbered domain steps (4–8)
- [ ] `### Step N — Final summary` with one follow-up `AskUserQuestion`
- [ ] `### Step N+1 — Invite feedback` line (skip only for stateless)

**Learning tier (when on)**
- [ ] `## Feedback & learning` section with: `feedback` subcommand handler, journal append format with `Signal:`, **promotion rule** (3+ sessions), **drift correction** (2 contradictions → demote)
- [ ] Pre-selection in domain `AskUserQuestion`s biased by `Learned` rules

**Templates (when Step 5.5 = Yes)**
- [ ] `templates/` directory exists with at least one scaffolded template
- [ ] Each `templates/<name>.md` has the canonical frontmatter (`inputs`, `tasks`, `constraints`, `tools`, `postProcesses`)
- [ ] `## Templates` section in SKILL.md documents loading + parsing
- [ ] Command routing handles `templates` (list) and `--from-template=<name>` (run)

**Closing**
- [ ] `## Principles` — 5–8 rules. Always include: "Graceful degradation on missing learning state" and "Destructive actions still need confirmation" if any side effects
- [ ] Total ≤500 lines (push reference material to `reference/` if over)

### Dynamic context injection

Never use `` !`...` `` backtick interpolation in personal skills. Use runtime instructions:

```markdown
## Context
_On startup, use Bash to detect: current git branch, git status, repo name. Skip any that fail._
```

### Preferences file format (mandatory three-tier when learning tier is on)

```markdown
# /<skill-name> preferences
Updated: YYYY-MM-DD

## Defaults
- knob: value
- knob: value

## Profile (optional — edit freely)
- user-editable bias lines

## Learned
- (populated from feedback over time)
```

### Feedback subcommand template (when learning tier is on)

```markdown
## Feedback & learning

When invoked as `/<skill> feedback`:

1. Find the most recent `sessions/YYYY-MM-DD-HHMM.md`. If none, say `No recent session found.` and stop.
2. Print a one-line summary of that session.
3. Ask via `AskUserQuestion` (3–4 questions in one batch). Tailor questions to the skill's output dimensions.
4. Append to `~/.claude/skills/<skill>/feedback-journal.md`:
   ```
   ## {session slug} — {date}
   - {dimension}: {answer}
   - Signal: {one-line generalisation}
   ```
5. Promotion rule: 3+ sessions same signal → promote to `## Learned` in `preferences.md`. Mention once.
6. Drift correction: 2 contradictions on a Learned rule → demote, log in journal.
```

### Principles starter set

Include these by default; cull or rewrite as needed:

- **Graceful degradation** — continue with built-in defaults if `preferences.md` / `feedback-journal.md` can't be read
- **Learn quietly** — promote a rule only after 3+ consistent signals; mention once when promoting
- **No fabricated structure** — if input is ambiguous, ask rather than invent
- **Destructive actions need confirmation** — auto mode does not bypass file deletes / pushes / external posts
- **Stop means stop** — when user halts, save resume state if applicable, do not continue in-flight work
- **Skill orchestrates, does not re-judge** — preserve user inputs verbatim where applicable

## Step 7 — Write the files

1. Create `~/.claude/skills/<skill-name>/`.
2. Write `SKILL.md`.
3. If reference material exceeds 100 lines, split into `reference/` files.
4. Do **not** pre-create `preferences.md`, `feedback-journal.md`, or `sessions/` — those are created on first use.

## Step 8 — Self-audit (mandatory)

After writing, **re-read the generated `SKILL.md`** and tick every box in the Structure checklist (Step 6). For each box that is unticked, either:
- Edit the SKILL.md to fix it, or
- Add a one-line note in the Principles section justifying the skip (e.g. `Stateless by design — no feedback loop because [reason]`).

Then run a quick line-count check via Bash. If over 500 lines, propose a split into `reference/`.

Print the audit result to the user:

```
Manifest audit: 23/24 boxes ticked.
Skipped: feedback subcommand — stateless by design (per Step 2 Q3).
File: ~/.claude/skills/<skill-name>/SKILL.md (LINE_COUNT lines)
```

## Step 9 — Post-creation actions

Present options via **AskUserQuestion**:

- **Test it** — `Run /<skill-name> help to verify the help output`
- **Configure it** — `Run /<skill-name> config to set initial preferences`
- **Update inventory** — only if a publish repo is configured: copy skill to publish repo, add row to `SKILLS_GUIDE.md` inventory table, add section to `README.md`. Don't commit.
- **Done** — `All set! Your new skill is ready at ~/.claude/skills/<skill-name>/`

## Step 10 — Learn from this session

Silently update `~/.claude/skills/skill-creator/preferences.md` if the user:
- Renamed the skill (record the rename pattern, e.g. "user prefers verb-led names")
- Removed/added tools you proposed (record the trim/add bias)
- Toggled learning posture against your pre-selection (record the override)
- Cut sections from your draft (record what they consider unnecessary)

Mention once: `Noted: you prefer X. Saved for next time.`

---

## Principles

1. **Manifest first.** Every generated skill ticks the Structure checklist — no exceptions without an explicit Principles-section justification.
2. **Three-tier preferences are the default.** Defaults / Profile / Learned, even for small skills. Stateless is the exception, not the rule.
3. **Feedback loop is the default.** A skill without a `/feedback` subcommand should be the rare case. Bias toward learning-on in Step 2 Q3.
4. **Self-audit is non-negotiable.** Step 8 is a checkpoint, not a formality. Don't ship a skill that fails its own audit.
5. **Minimal viable skill.** Start with the simplest version that works — but "simplest" still includes the learning tier when applicable.
6. **Show before write.** Always present the planned workflow, knobs, and feedback dimensions before generating the file.
7. **Learn and improve.** Save patterns from user corrections to make future skill creation faster and more aligned to their style.
