# Command surface

Loaded on demand when `/screenshots-memory help` or `config` runs. These are literal
output templates — the behaviour they describe lives in SKILL.md.

## Help

Print this, filling in the user's actual preferences:

```
screenshots-memory — Screenshots → a queryable, private memory

  sync [path|glob] [--since Nd] [--kind k] [--yes]   Pull new captures, extract, cluster
  <question>                        Ask the memory in plain language
  review [--min-confidence 0-1]     Correct low-confidence reads (teaches the extractor)
  review --apply <json block>       Apply reviews collected in the HTML page
  clusters | browse                 Re-render + open the HTML browser
  feedback · config · setup · reset · help

Examples:
  /screenshots-memory sync                       Sweep the inbox (~/Desktop)
  /screenshots-memory sync ~/Downloads --since 7d
  /screenshots-memory what did Slack ask me to do last week

Store: {memory-root} — a local git repo, no remote. {N} captures, {C} clusters,
{F} flagged for review. Full guide: README.md · layout: reference/memory-schema.md

Current preferences:
  (list them)
```

## Config

Fire ONE `AskUserQuestion` (multi-question) to collect:

1. **Memory root** — where the memory store lives (default `~/screenshots-memory/`)
2. **Inbox** — the folder that gets swept when no path is given (default `~/Desktop`)
3. **Originals** — `move` (once the store's copy is committed and hash-verified, the
   inbox original is **deleted**; the store becomes the only copy) or `copy` (leaves the
   inbox untouched). Say "deleted" when asking — this is the skill's only irreversible act.
4. **Confidence threshold** — how sure the reader must be before a note is trusted (default `0.75`)
5. **Tone** — `friendly-cli` / `detailed` / `minimal`

Save to `~/.claude/skills/screenshots-memory/preferences.md`:

```markdown
# /screenshots-memory preferences
Updated: {date}

## Defaults
- memory-root: {path}
- inbox: {path}
- originals: {move|copy}
- confidence-threshold: {0-1}
- cluster-style: topic
- sensitive-policy: ask-batched
- open-html: {true|false}
- tone: {friendly-cli|detailed|minimal}

## Learned
<!-- patterns observed from the user's choices; edit freely -->
```

The kind registry lives in `{memory-root}/kinds.md`, not here. Confirm warmly: "Saved. I'll use this as the baseline and keep sharpening as you correct
extractions."

