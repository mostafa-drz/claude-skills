---
name: clean-copy
description: >-
  Cleans terminal-formatted text and copies it to the macOS clipboard via
  pbcopy, formatted for the target platform (Gmail, Slack, LinkedIn, plain,
  markdown). Strips uniform leading indentation, trailing whitespace, and
  soft-wrapped paragraphs that come from copying out of a terminal, then
  applies platform conventions (Slack `*bold*` vs Gmail plain prose, etc.).
  Use when the user wants to paste a draft from the chat into Gmail, Slack,
  LinkedIn, or any other tool without nightmare terminal formatting (extra
  whitespace, hard wraps, indented blocks) coming along.
argument-hint: <platform> [--source last|paste|file:<path>] [--no-reflow] [--preview]
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
---

# Clean Copy

Clean a draft from the conversation (or a pasted/file source) and copy it to
the clipboard, formatted for a specific platform. The goal: a paste that looks
right in Gmail / Slack / LinkedIn on the first try, with zero manual cleanup.

## Preferences

Before starting, use the `Read` tool to read
`~/.claude/skills/clean-copy/preferences.md`. If the file does not exist, treat
as "no preferences set" and use defaults below.

**Defaults:**
- default-platform: `gmail`
- default-source: `last` (most recent assistant draft in the conversation)
- reflow-paragraphs: `true` (rewrap soft-wrapped paragraphs into single lines)
- bullet-style: `-` (preserve as-is)
- preview-after-copy: `true` (show first 12 lines + char count)

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help, stop
- **`config`** → interactive setup, stop
- **`reset`** → delete `~/.claude/skills/clean-copy/preferences.md`, confirm, stop
- **anything else** (including empty) → run the skill

### Help

```
Clean Copy — Clean terminal-formatted text and copy to clipboard for a target platform

Usage:
  /clean-copy <platform>            Clean latest draft, format, pbcopy
  /clean-copy                       Use default platform from preferences
  /clean-copy config                Set defaults (default platform, reflow, etc.)
  /clean-copy reset                 Clear preferences
  /clean-copy help                  This help

Platforms:
  gmail        Plain prose, bullets as "- ", no markdown rendering
  slack        Slack mrkdwn: *bold*, _italic_, `code`, > quotes
  linkedin     Plain prose, no markdown (LinkedIn strips it), short paragraphs
  plain        Strip all markdown, just clean prose
  markdown     Preserve markdown, only clean terminal whitespace

Options:
  --source last         Latest assistant draft in conversation (default)
  --source paste        Prompt the user to paste the source text
  --source file:<path>  Read source from a file
  --no-reflow           Keep hard line breaks as-is (don't unwrap paragraphs)
  --preview             Show full cleaned text before copying

Examples:
  /clean-copy gmail                    Clean my last draft for Gmail compose
  /clean-copy slack                    Format for Slack mrkdwn
  /clean-copy linkedin --no-reflow     Keep my line breaks (poetry / structured posts)
  /clean-copy plain --source paste     I'll paste the messy text after invocation
  /clean-copy markdown --source file:/tmp/draft.md

Current preferences:
  (loaded from preferences.md, or defaults shown above)
```

### Config

Use `AskUserQuestion` to collect:

- **Q1: Default platform** — `gmail`, `slack`, `linkedin`, `plain`, or `markdown`. The platform used when `/clean-copy` is invoked with no platform arg.
- **Q2: Reflow paragraphs by default?** — `Yes` (recommended for prose) or `No` (preserve hard line breaks). Reflow joins soft-wrapped lines into single paragraphs separated by blank lines.
- **Q3: Bullet style** — `-` (keep as written), `•` (convert to bullet glyph), or `*` (asterisk). Affects how list items render after cleaning.
- **Q4: Preview after copy?** — `Yes` (show first 12 lines + char count) or `No` (silent except for "Copied").

Save to `~/.claude/skills/clean-copy/preferences.md` in this format:

```markdown
# /clean-copy preferences
Updated: <date>

## Defaults
- default-platform: gmail
- reflow-paragraphs: true
- bullet-style: -
- preview-after-copy: true

## Learned
- (patterns observed silently, e.g., "user always picks slack on weekdays mornings")
```

### Reset

Delete `~/.claude/skills/clean-copy/preferences.md` and confirm:
"Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:

> First time using /clean-copy? Run `/clean-copy config` to set defaults, or
> just continue — defaults are gmail / reflow on / dash bullets.

Then proceed.

## Workflow

### Step 1 — Resolve platform

Parse `$ARGUMENTS`:
- If a platform keyword (`gmail`, `slack`, `linkedin`, `plain`, `markdown`) is present, use it.
- Otherwise, fall back to `default-platform` from preferences (or `gmail`).
- If still unclear AND the source text strongly hints (e.g., starts with "Hi all," → email; starts with "@channel" → slack), pick that and mention it: "Detected gmail-style draft, formatting for Gmail."

### Step 2 — Resolve source

Check for `--source` flag in `$ARGUMENTS`:

- **`last`** (default) — pick the most recent **assistant** message in the conversation that looks like a finished draft (prose body of >40 words, not a meta reply about the skill itself). Do NOT pick a user message; the user's invocation message is not the source. If no clear draft is found, fall back to `paste` mode.
- **`paste`** — ask the user via AskUserQuestion or plain prompt: "Paste the text you want cleaned and copied. Send it as your next message."
- **`file:<path>`** — read the file at `<path>` with the Read tool. If it doesn't exist, abort with a clear error.

If multiple plausible drafts are in the conversation, pick the most recent one and say "Using your most recent draft (~N words). Run `/clean-copy <platform> --source paste` to override."

### Step 3 — Clean (platform-agnostic)

Apply these passes in order. Each pass is non-destructive of meaning — only whitespace and terminal artifacts.

1. **Normalize line endings** — convert `\r\n` and `\r` to `\n`.
2. **Strip box-drawing artifacts** — terminal renderers sometimes inject `│`, `─`, `┃`, or trailing block characters at the right edge. Drop them.
3. **Detect and strip uniform leading indent** (the "terminal padding" pass):
   - Look at substantive lines only — non-blank lines longer than 20 characters that aren't inside a fenced code block. (This excludes short greetings like "Hi all," which often have 0 indent even when the body is indented.)
   - Find the **mode** (most common count) of leading spaces across those substantive lines. If the mode is >0, that's the terminal-injected padding.
   - Strip up to that many leading spaces from every line (lines with fewer leading spaces just lose what they have — never go negative).
   - Inside fenced code blocks, do not touch indentation — code's leading whitespace is meaningful.
4. **Strip trailing whitespace** on every line.
5. **Collapse runs of blank lines** — 3+ blank lines → 2 blank lines (one paragraph break).
6. **Drop terminal padding artifacts** — lines that contain only whitespace + terminal-injected glyphs become empty.

### Step 4 — Reflow (optional, default on)

If `--no-reflow` is set OR the source contains fenced code blocks where line
breaks matter, **skip this step for those sections**.

For prose paragraphs, **rejoin soft-wrapped lines**:

- A soft wrap is detected when a line ends without sentence-ending punctuation (`.`, `!`, `?`, `:`, `;`, `…`) AND the next line exists, is non-empty, is not a list item (`-`, `*`, `1.`), is not a heading (`#`), and is not blockquote (`>`).
- Join soft-wrapped lines with a single space.
- Preserve paragraph breaks (a blank line) verbatim.
- Preserve list item structure — each list item stays on its own line; if a list item itself has a soft-wrapped continuation, join those into the same item.

This is the most important pass for terminal output: a paragraph wrapped at 80
columns becomes one long line, which Gmail / Slack / LinkedIn will then
re-wrap correctly for their own width.

### Step 5 — Format for platform

Apply platform-specific transforms after cleaning:

**`gmail`** (rich compose, but markdown is NOT rendered):
- Strip markdown emphasis: `**bold**` → `bold`, `*italic*` → `italic`, `__bold__` → `bold`, `_italic_` → `italic`.
- Headings: `# H1` / `## H2` → drop the `#`s and surrounding hashes; keep the text on its own line. Do NOT bold (Gmail won't render).
- Bullets: keep as `- item` (Gmail compose recognizes and renders these as proper bullets when you press Enter inside the editor on the next line; pasting `- ` lines is fine).
- Code blocks: drop the fence markers ` ``` `, keep content as-is (monospace is lost, that's expected).
- Inline code: `` `code` `` → `code` (drop backticks).
- Links: `[text](url)` → `text (url)` so the URL is visible.

**`slack`** (mrkdwn — different from CommonMark):
- `**bold**` → `*bold*` (single asterisk).
- `*italic*` or `_italic_` → `_italic_`.
- `~~strike~~` → `~strike~`.
- Headings `# H1` → `*H1*` on its own line (slack has no real headings; bold is the convention).
- Bullets: keep as `- item` or convert to `• item` per `bullet-style` preference. Slack renders both.
- `> quote` lines kept as-is (slack renders them).
- Inline code and code blocks (` ``` `) kept as-is — Slack supports them.
- Links: `[text](url)` → `<url|text>` (slack format).

**`linkedin`** (no markdown rendering, anywhere):
- Strip all markdown: emphasis, headings, code fences, inline code backticks.
- Bullets: keep as `- item` lines (LinkedIn doesn't auto-format but plain dashes are conventional).
- Links: `[text](url)` → `text: url` (or just `url` on its own line if `text` is the same).
- Keep paragraphs short — if reflow joined a paragraph into >400 chars, split at the nearest sentence boundary near 250 chars. (LinkedIn has its own truncation.)

**`plain`**:
- Strip ALL markdown completely (emphasis, headings, code fences/inline backticks, links → just `text`).
- Bullets: keep as `- item`.
- Output is pure text — pastes the same way into anything.

**`markdown`**:
- No platform transforms. Markdown is preserved exactly. Only the cleaning passes (Step 3) and optional reflow (Step 4) are applied.

### Step 6 — Write and copy

1. Write the cleaned, formatted text to `/tmp/clean-copy-output.txt` using the `Write` tool. Use the `Write` tool, not `echo`, to avoid quoting issues with special characters in the draft.
2. Pipe through pbcopy via Bash: `pbcopy < /tmp/clean-copy-output.txt`
3. Verify by running `pbpaste | wc -c` and confirm the byte count is non-zero and roughly matches the source.

### Step 7 — Report

If `preview-after-copy` is true (default) OR `--preview` flag is set:

> ✓ Copied to clipboard — formatted for **{platform}** ({char_count} chars, {line_count} lines)
>
> ```
> {first 12 lines of cleaned output}
> ...
> ```
>
> Source: {last assistant draft / pasted / file:path}
> Cleaning: stripped {N}-space indent, reflowed {M} soft wraps, dropped {K} trailing-whitespace lines

If preview is off, just:

> ✓ Copied for {platform} ({char_count} chars).

### Step 8 — Learn

Watch for silent corrections:

- User invokes `/clean-copy` (no platform), then immediately reruns with a specific platform → save that as the new `default-platform`.
- User adds `--no-reflow` two times in a row → flip `reflow-paragraphs` to `false`.
- User runs `/clean-copy plain` repeatedly when their default is `gmail` → consider suggesting a default change after 3 occurrences.

When something is learned, mention it once: "Noted: you've picked slack three times in a row — want me to make that the default? (`/clean-copy config` to change.)"

## Principles

- **Clipboard-first** — the whole point is `pbcopy`. Always end with a fresh clipboard the user can paste immediately. Never just print.
- **Don't change meaning, only formatting** — never rephrase, summarize, or "improve" the draft. Cleaning is whitespace + platform syntax conversion only.
- **Reflow is the killer feature** — terminal output's biggest sin is hard wraps at 80 columns. Reflowing soft-wrapped paragraphs into single lines is what makes Gmail and Slack render the draft correctly.
- **Preserve code and lists faithfully** — fenced code blocks and list structure must survive untouched. Reflow stops at code fences and list items.
- **One clean source of truth** — write cleaned text to `/tmp/clean-copy-output.txt` first, then pbcopy from the file. Avoids quoting hell from inline shell strings with quotes / backticks / unicode.
- **No surprises** — if the source is ambiguous (multiple drafts in conversation, or "is this a draft?") say which one you picked and how to override. Never silently pick wrong.
