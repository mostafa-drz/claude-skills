# Skills design guide

House conventions for the skills in this repo.

**This guide deliberately does not restate the official spec.** The frontmatter
reference, permission syntax and packaging rules live at
[code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) and
[agentskills.io/specification](https://agentskills.io/specification) — append `.md` to any
docs URL for raw markdown. A local copy of a spec rots silently while the original updates;
this guide previously carried one and drifted. What follows is only what those docs don't
cover: the decisions that are ours, and the rules these skills learned the hard way.

---

## 1. The conventions that are actually ours

**Subcommands.** Every skill answers `help`, `config` and `reset` in addition to its main
job. `reset` clears skill preferences and never touches user data — say so explicitly when
confirming, because "reset" reads as destructive.

**Preferences** live at `~/.claude/skills/<name>/preferences.md`, never in the skill
directory in git (it is gitignored for exactly this reason — publishing a skill must not
publish your paths).

```markdown
# /<skill-name> preferences
Updated: YYYY-MM-DD

## Defaults
- key: value

## Learned
<!-- patterns observed from the user's choices; editable by hand -->
```

Read it at startup. Write it **after the first successful run**, not only when the user
runs `config` — a first-run intro that keys off the file existing will otherwise greet
them forever.

**First run** is a warm, non-blocking orientation, never a wizard that must be completed
before anything works.

**Tone**: one friendly line to open and close. The work speaks for itself.

**Output templates** — help text, first-run intros, prompt formats, report formats — go in
`references/`, not in SKILL.md. They are consumed verbatim on a small fraction of
invocations, and SKILL.md is a recurring token cost on every one. The test: could an agent
that never loads the reference still route correctly? If yes, the move is right.

---

## 2. Frontmatter decisions

The full field list is in the official docs. These are the choices to make.

**`description` — write to 1,024 characters.** Two different caps exist and conflating
them wastes effort:

| cap | applies to | mechanism |
|---|---|---|
| **1,024** | `description` alone | **hard validation** — the portable spec, the Skills API and claude.ai uploads *reject* a longer one |
| 1,536 | `description` + `when_to_use` combined | soft truncation in Claude Code's listing only, configurable |

Writing to 1,024 satisfies both and keeps the skill portable. Third person always —
"Creates…", never "Create…" or "I can help you…" — because it is injected into the system
prompt and mixed point-of-view breaks matching. Front-load the trigger keywords: a
**separate** budget caps the whole listing at ~1% of the context window, and on overflow
Claude Code drops the descriptions of least-used skills entirely while keeping their names.
A rarely-used skill can silently lose the words that make it findable.

**`disable-model-invocation: true` is required for any skill that writes** — files, PRs,
tickets, messages, anything outside the conversation. `make check` enforces this.

**`when_to_use`** is not in the portable six-field spec, so using it makes a skill
unpackageable. It shares the same budget as `description`, so it buys organisation, not
room. Prefer putting everything in `description`.

**Portability is a hard error, not a soft ignore.** Only six fields survive packaging for
claude.ai, the Skills API, or Cowork/cloud sessions: `name`, `description`, `license`,
`compatibility`, `metadata`, `allowed-tools`. Anything else — including `argument-hint` —
fails the upload outright. This catches an unobvious path: enabling a personal skill for
cloud sessions uploads it to claude.ai, so the same six-field rule applies there.

**`version` is not a frontmatter field** in either authority. It belongs under `metadata`.

---

## 3. `allowed-tools`, and what it does not do

**It grants, it does not restrict.** The listed tools are pre-approved for the invoking
turn only; the grant clears on your next message. Every other tool remains callable under
your normal permission settings. It is a convenience, not a sandbox.

**Every entry must correspond to a command the skill actually instructs — and every
instructed command must have an entry.** Check both directions. An instructed-but-
unpermitted command produces a surprise prompt mid-run; a permitted-but-uninstructed one
is silent over-reach. `Bash(python3 *)` in a skill that runs no Python pre-approves
arbitrary code execution.

**Bash rules are not a security boundary.** The docs state this outright: a rule matches
the command text Claude usually writes, not the program. `Bash(git push *)` does not stop
`git -C . push`, `git -c push.default=current push`, or `git 'push'`. Nor does a
mid-pattern wildcard help — `Bash(git -C * commit *)` is *worse*, because the `*` covers
the subcommand slot and pre-approves `git -c core.pager=<command>`.

So: **when a skill has a safety-critical invariant, enforce it in the skill's own logic and
say so.** Never imply the permission layer is enforcing it. If it must hold against a
determined caller, that is a `PreToolUse` hook or sandboxing, not a glob.

Two syntax facts worth remembering: the `*` matches everything before it *literally*, so
put it after the subcommand; and `Tool(param:value)` works in deny/ask rules only.

---

## 4. Structure

Under 500 lines in SKILL.md — a recommendation, not a hard limit, but a real one: the body
stays in context across turns, so every line recurs. Bundled files cost nothing until read.

Use the spec's directories: `references/`, `scripts/`, `assets/`.

**Keep references one level deep from SKILL.md.** Claude may preview a nested file with
`head -100` rather than reading it, so a reference that points at another reference can be
read incompletely without any error. Give any reference over 100 lines a table of contents
for the same reason.

**SKILL.md is not re-read on later turns.** It enters the conversation once and stays.
Write standing instructions that hold for the whole task, not one-time steps. After
compaction only the first 5,000 tokens of each skill are re-attached, sharing a 25,000
token budget — so put what must survive near the top.

---

## 5. Skills that touch the user's files

Learned from `/remarkable-memory` and `/screenshots-memory`, both of which shipped bugs in
every one of these categories before review caught them.

**Name the action precisely at the consent point.** Not a euphemism ("retired"), not an
exaggeration ("deleted" when it moves to the Trash). Both are failures; the accurate word
is usually also the more reassuring one.

**Never escalate past what was approved.** If the plan said "moved to Trash" and no Trash
exists, stop — do not substitute `rm`. A fallback must never be more destructive than the
action the user agreed to.

**Verify the committed artifact, not the working-tree one.** Hashing a file on disk proves
nothing about what was committed: with git-lfs or any clean filter the commit may hold a
pointer while the working file looks correct. Read the bytes you are relying on
(`git rev-parse HEAD:<path>` then `cat-file blob`), and note that `git log -- <path>`
answers truthily for a path `HEAD` no longer contains.

**Order is verify → commit → destroy**, and only ever in that order. A failed verification
leaves that item alone and reports it, without aborting the rest of the batch.

**Long runs must checkpoint.** Work in batches that each complete and commit. An
all-or-nothing pass over hundreds of items loses everything to one interruption — and that
is exactly the first-run case.

**Every command that writes into a store commits before it returns.** Leaving a dirty tree
makes the next run's safety check fire falsely, which trains the user to wave through the
one check protecting them.

---

## 6. Constraints that fail at runtime, not review

- **`AskUserQuestion` takes 1–4 questions**, 2–4 options each, `header` max 12 characters.
  A five-question config flow fails live, not in review. Split into rounds.
- **It is unavailable in subagents**, so a `context: fork` skill cannot ask anything. Design
  forked skills to be autonomous.
- **A failed `` !`cmd` `` aborts the entire skill invocation** — Claude never sees the
  content. Any non-zero exit counts (except exit 1 from search tools), so append `|| true`.
  A command whose permission check would *ask* also aborts; pre-approve it.
- **Malformed frontmatter fails soft.** The body loads with empty metadata, so `/name` keeps
  working while automatic invocation silently stops. Nothing surfaces this — which is why
  `make check` exists.

---

## 7. Checks

```bash
make catalog   # regenerate the README table from frontmatter
make check     # fail if the table is stale or frontmatter won't parse (CI runs this)
```

The README catalog and `skills.json` are both **generated** from frontmatter. A second
hand-maintained copy always drifts: before this, 68% of the manifest's descriptions were
out of sync with their skills and it advertised a Linear-writing skill as having no side
effects — which the site consuming it was faithfully displaying.

`skills.json` is a **published API** — mostafa.xyz renders from it — so its field shape is
a contract. Don't change the keys without checking the consumer.

The two things a manifest needs that nothing else knows, `trigger` and `tags`, live in each
skill's own frontmatter `metadata:` map. Add them there when you add a skill; everything
else is derived.

Locally, `claude plugin validate ~/.claude/skills` reports skills whose frontmatter fails
to parse, and `/skill-doctor` shows per-skill context cost and flags skills never invoked.
