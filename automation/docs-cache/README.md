# Docs Cache

Dated snapshots of the upstream Claude Skills docs the routine fetches each morning. Format: `YYYY-MM-DD.md`. See [`../daily-skill-routine.md` §3](../daily-skill-routine.md#3-source-of-truth-docs) for the source URLs and refresh logic.

Each snapshot includes: fetch timestamp, source URL, the key sections relevant to skill authoring, and a diff vs the previous cache file. Use these to see what was true on day N — useful when a routine-built skill later looks wrong and you need to know what the spec was at the time.
