---
name: chunk-pr
description: >-
  Analyzes a large pull request (or branch, or commit range) and proposes a sequence of
  smaller, logically-grouped, merge-safe PRs following review best practices — dependency
  first, one concern per PR, mergeable in order. Suggests a plan; the user approves. On
  approval, creates chunk branches, cherry-picks commits, pushes, opens draft PRs, and
  links them to the parent Linear issue. Use when a PR is too big to review, when a branch
  has accumulated unrelated changes, when reviewers ask "can you split this up?", or when
  planning how to ship a large feature incrementally.
argument-hint: [pr-or-branch-or-range] [--base branch] [--max-lines N] [--strategy kind] [--dry-run] [--no-push] [--draft]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Glob
  - Grep
  - WebFetch
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__update_issue
  - mcp__claude_ai_Linear__create_comment
  - mcp__claude_ai_Linear__list_issues
  - mcp__claude-in-chrome__tabs_context_mcp
  - mcp__claude-in-chrome__tabs_create_mcp
  - mcp__claude-in-chrome__navigate
  - mcp__claude-in-chrome__read_page
---

# Chunk PR

Break one big PR into a sequence of small, logical, merge-safe PRs. Suggest, don't decide — the user approves every chunk and every destructive action.

## Preferences

_Read `~/.claude/skills/chunk-pr/preferences.md` using the Read tool. If not found, no preferences are set._

## Context

_On startup, use Bash to detect: current branch (`git branch --show-current`), base upstream, commits ahead, total lines changed (`git diff {base}...HEAD --shortstat`), and repo (`gh repo view --json nameWithOwner -q .nameWithOwner`). Skip any that fail. Do NOT run destructive commands at this stage._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/chunk-pr/preferences.md`, confirm, stop
- **anything else** (including empty) → run the chunking workflow

### Flags (parsed from `$ARGUMENTS`)

- **`--base <branch>`** — override target base (default: auto-detect or preference)
- **`--max-lines <N>`** — target max lines per chunk (default: 400 or preference)
- **`--strategy <kind>`** — `conservative` (more/smaller), `balanced` (default), `aggressive` (fewer/larger)
- **`--dry-run`** / **`--plan-only`** — stop after presenting the plan; don't create branches or PRs
- **`--draft`** — open chunks as draft PRs (default)
- **`--ready`** — open chunks as ready-for-review (overrides `--draft`)
- **`--no-push`** — create local branches only, skip push/PR creation
- **`--no-linear`** — skip Linear linking
- **Positional** — PR number (e.g. `234`), PR URL, branch name, or commit range (`main..HEAD`). If omitted, use current branch.

### Help

```
Chunk PR — Split a big PR into a sequence of smaller, merge-safe ones

Usage:
  /chunk-pr                                Analyze current branch
  /chunk-pr <pr-number>                    Analyze a specific PR
  /chunk-pr <pr-url>                       Analyze a PR by URL (same or other repo)
  /chunk-pr <branch>                       Analyze a local branch
  /chunk-pr main..HEAD                     Analyze a commit range
  /chunk-pr --max-lines 300                Prefer chunks under 300 lines
  /chunk-pr --strategy conservative        More, smaller chunks
  /chunk-pr --dry-run                      Plan only — don't touch git
  /chunk-pr config                         Set preferences
  /chunk-pr reset                          Clear preferences
  /chunk-pr help                           This help

What it does:
  1. Identify the subject PR / branch / range
  2. Classify commits and files into logical groups
  3. Propose an ordered, dependency-aware split plan
  4. Let you approve, reorder, merge, or re-split chunks
  5. On approval, create branches + draft PRs + Linear links
  6. Leave the parent branch untouched

Current preferences:
  (shown above under Preferences)
```

### Config

Use **`AskUserQuestion`**:

**Q1** — "Target max lines per chunk?" (200, 400 (default), 600, 1000, no limit)

**Q2** — "Default split strategy?" (conservative, balanced (default), aggressive)

**Q3** — "Default action after plan approval?" (per-chunk confirm (default), execute all, branches only no PRs, plan only)

**Q4** — "Branch naming convention for chunks?"
- `{parent}/chunk-{N}-{slug}` (default — e.g. `user/ais-810-refactor/chunk-1-schema`)
- `{parent}-{N}` (short — e.g. `user/ais-810-refactor-1`)
- `chunk/{slug}` (flat — e.g. `chunk/schema`)
- custom (user provides pattern with `{parent}`, `{N}`, `{slug}` placeholders)

**Q5** — "Link chunks to parent Linear issue?" (Yes as sub-items (default), Yes as relates-to, No, Ask each time)

**Q6** — "Default PR type for chunks?" (draft (default), ready for review)

**Q7** — "Classification weighting?" (by file type (default), by commit topic, hybrid)

Save to `~/.claude/skills/chunk-pr/preferences.md`.

### Reset

Delete `~/.claude/skills/chunk-pr/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:
"First time using /chunk-pr? Run `/chunk-pr config` to set defaults, or just continue — I'll pick sensible defaults."

Then proceed.

## Steps

### 1. Identify the subject

Resolve **in order**:

1. **`$1` looks like a PR URL** (`https://github.com/*/pull/N`) → use `gh pr view <url> --json ...` or WebFetch for external repos.
2. **`$1` is a number** → `gh pr view <N>` on current repo.
3. **`$1` is a commit range** (contains `..`) → use it directly with `git log`/`git diff`.
4. **`$1` is a branch name** → treat as `{base}..{$1}`.
5. **No `$1`** → use current branch vs. its upstream/default-base.

**Early bail-outs:**
- If total changed lines < max-lines preference × 1.5 → tell the user this probably doesn't need chunking, ask if they still want to proceed.
- If there's 1 commit touching 1 file → refuse politely; this isn't chunkable.
- If uncommitted changes exist on current branch → stop and ask (per global git-safety rule; never proceed silently).

### 2. Gather context

From git / gh:
- All commits in range: `git log {base}..{head} --pretty=format:"%H|%s|%an|%ai" --numstat`
- Per-file stats: `git diff {base}...{head} --numstat` and `--stat`
- Diff body (for classification, not pasted back): `git diff {base}...{head}` — read in chunks if huge
- PR metadata if applicable: title, body, labels, reviewers
- Existing review comments if PR is open: `gh api repos/{owner}/{repo}/pulls/{N}/comments`

From Linear (unless `--no-linear`):
- Extract issue ID from branch name or PR body
- `get_issue` for title, description, project, sub-issues, related issues

**Base branch detection** (same as `/create-pr`):
1. `--base` flag → preference → upstream tracking → repo default branch

### 3. Classify commits and files

**File-based classification** (default weighting):

| Group | Patterns (examples) |
|---|---|
| `schema`  | `**/migrations/**`, `**/schemas/**`, `drizzle/**`, `prisma/**`, `*.sql` |
| `api`     | `src/router/**`, `src/api/**`, `src/handlers/**`, `src/server/**` |
| `ui`      | `src/components/**`, `src/app/**`, `**/*.tsx`, `**/*.css` |
| `tests`   | `**/__tests__/**`, `**/*.test.*`, `**/*.spec.*`, `e2e/**` |
| `docs`    | `**/*.md`, `docs/**`, `README*`, `CHANGELOG*` |
| `config`  | `package.json`, `tsconfig*.json`, `.env.example`, `vite.config.*`, `next.config.*`, CI workflows |
| `deps`    | `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock` — bundle with `config` |
| `refactor`| commits whose message starts with `refactor:`/`chore:` AND whose diff is behavior-preserving (renames, moves, type-only) |
| `other`   | anything unmatched |

**Commit-based signals** (boost classification):
- Conventional prefix (`feat:`/`fix:`/`refactor:`/`chore:`/`test:`/`docs:`)
- Scope in parens (`feat(meetings): ...`) — use scope as a chunk hint

**Cross-cutting flag** — if a single file appears in multiple groups' commits, flag it. These are the hardest to split cleanly and usually belong in the earliest chunk.

**Classification presets:**
- `by file type` (default) — group by the table above
- `by commit topic` — group by conventional scope (`meetings`, `knowledge`, `auth`)
- `hybrid` — topic first, then file-type within a topic

Read the diff itself (via Read/Grep where needed) when the filename isn't enough to classify — e.g. a `.ts` file could be API or UI.

### 4. Propose the split plan

Build an ordered list. **Ordering rules**:

1. `config`/`deps` first if they unblock later chunks
2. `schema` before `api` before `ui`
3. `refactor` before feature commits that depend on the refactor
4. `tests` bundle with the behavior they cover (don't create a tests-only chunk unless the tests pre-existed and were just moved)
5. `docs` last

For each chunk, produce:

```
Chunk {N}: {title with conventional prefix}
  Scope:        {1-2 sentences}
  Commits:      {N} ({oldest-SHA}..{newest-SHA})
  Files:        {N} files, +{added}/-{removed} lines
  Depends on:   Chunk {N-1} or "none"
  Safe to ship: yes / yes-behind-flag / only-after-{N}
  Rationale:    {why this grouping}
  Risks:        {conflicts, cross-cutting files, behavior change}
```

**Size policing** — if a chunk exceeds `max-lines`:
- Try splitting by file-subgroup (UI → forms vs. views)
- Or split the chunk's commits into "refactor" + "feature" halves
- If neither helps, flag the chunk as "oversized — consider landing behind a flag"

**Conflict forecasting** — if two chunks both touch the same file at overlapping lines, call it out; the later chunk will need a rebase after the earlier one lands.

Present the full plan as a compact, numbered list the user can react to.

### 5. Review with the user

Use **`AskUserQuestion`** to get the call. Options:

- **Approve plan as-is** — proceed to execute (step 6)
- **Merge chunks {A} and {B}** — combine two chunks into one, re-present plan
- **Split chunk {N} further** — break one chunk into smaller ones, re-present plan
- **Reorder** — swap or reshuffle; re-present plan
- **Drop chunk {N}** — leave those commits on the parent branch, don't chunk them
- **Change strategy** — re-run classification with `aggressive` / `conservative`
- **Dry-run stop** — save the plan to a file, don't touch git

Loop until the user approves or cancels. Keep iterations cheap — don't re-fetch git/Linear state between iterations unless the user changes scope.

Optional: if Chrome MCP is set up and the user asks, open the original PR in a tab via `tabs_create_mcp` for visual cross-reference while reviewing the plan. Do not open Chrome by default — it's noisy.

### 6. Execute on approval

**Pre-flight** (non-negotiable):
- `git status` must be clean — else stop and ask (per global rule)
- Remember the current HEAD; print it so the user can roll back
- Never modify the parent branch or its ref. Only create **new** branches.

**Per chunk**, with per-chunk confirmation (unless preference says "execute all"):

1. Check out base: `git checkout {base} && git pull --ff-only origin {base}`
2. Create chunk branch: `git checkout -b {chunk-branch-name}` (using preferred naming convention)
3. Apply changes. Two modes — pick the one that fits the classification:
   - **Commit cherry-pick** (preferred when the chunk maps to contiguous commits):
     `git cherry-pick {sha1} {sha2} ...`
     Resolve conflicts if they appear — ask the user, never force.
   - **File subset** (when commits are cross-cutting and only a subset of the diff belongs):
     For each file: `git checkout {head} -- {path}` (or for partial-file: `git checkout -p {head} -- {path}`)
     Then a single `git commit -m "{chunk-title}"` with an accurate, non-generic message.
4. Run local sanity — **read-only**: `git diff {base}...HEAD --shortstat`, `git log {base}..HEAD --oneline`. Never run `pnpm build` or `pnpm dev` (global rule).
5. Push (unless `--no-push`): `git push -u origin {chunk-branch}`
6. Open draft PR (unless `--no-push` or `--no-pr`):
   `gh pr create --draft --base {base} --title "{title}" --body "{body}"`
   PR body includes:
   - 1-2 line scope
   - `Part {N}/{total} of splitting #{original-pr}` (or the parent branch)
   - `Depends on: #{previous-chunk-pr-number}` if applicable
   - Linear link if available
   - Test steps (brief, per-chunk)
7. Link to Linear:
   - Attach PR URL to parent issue via `update_issue` (links array)
   - Or post a `create_comment` on the parent issue listing all chunk PRs once execution finishes

Between chunks, **return to the base branch** before creating the next chunk's branch. Never branch off a previous chunk unless the plan explicitly says so ("depends on chunk N").

### 7. Report

```
Chunked {source} into {count} PRs:

  1. [#{N}]({url}) — {title}  ({lines} lines, depends on: none)
  2. [#{N}]({url}) — {title}  ({lines} lines, depends on: #{N-1})
  ...

  Parent branch:   {branch} (untouched)
  Parent PR:       {original, if any}
  Linear:          {issue-id} — {count} PR(s) linked
  Original HEAD:   {sha}  ← rollback anchor

Recommended merge order: top to bottom. Rebase each after the previous lands.
```

### 8. Learn

Save preferences silently when the user:
- Overrides `--max-lines` or `--strategy` twice in a row → update defaults
- Repeatedly merges or splits chunks the same way → nudge the classification weighting
- Picks a branch-naming pattern that differs from the saved one → update preference
- Always chooses "plan only" → switch default action to `dry-run`
- Consistently chooses "ready" over "draft" → update default PR type

Mention: "Noted: you prefer {X}. Saved for next time."

## Principles

1. **Suggest, never decide.** The user approves the plan before any branch is created. They approve again before any push. No exceptions.
2. **Preserve the original.** Never modify or delete the parent branch. Always cherry-pick into new branches. Record the original HEAD so rollback is trivial.
3. **Dependency-aware ordering.** Schema before API before UI. Refactor before the feature that depends on it. Config before the code that reads it. Call out dependencies explicitly in the plan.
4. **Each chunk stands alone.** Every chunk must be reviewable on its own and mergeable in order — no chunk depends on an un-landed sibling except through the declared `Depends on`.
5. **Use git, don't regenerate.** Cherry-pick commits or `git checkout {ref} -- {path}`. Don't reconstruct diffs by hand — it loses authorship, dates, and commit messages.
6. **Never bypass global rules.** No `pnpm build`/`pnpm dev`. No `git add -A`. No generic commit messages. No regex for IDs. If a test or typecheck fails, fix it — don't skip.
