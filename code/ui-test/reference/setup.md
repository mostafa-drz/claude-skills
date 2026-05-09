# Claude-in-Chrome setup walkthrough

Used by `/ui-test setup`. Load via Read when the user asks for setup help, or when Step 1 preflight fails and they reply "help".

Reference: official docs at `https://code.claude.com/docs/en/chrome` — fetch via WebFetch if a detail in this file is stale.

## Prerequisites checklist (print verbatim)

```
Before we go:

  1. Browser        Google Chrome or Microsoft Edge
                    (Brave, Arc, other Chromium browsers: not yet supported)
                    Windows WSL: not supported

  2. Plan           A direct Anthropic plan — Pro, Max, Team, or Enterprise
                    (Free tier and third-party providers don't have Chrome)

  3. Claude Code    Version 2.0.73 or higher  →  claude --version

  4. Extension      "Claude" by Anthropic, version 1.0.36 or higher
                    https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn
                    Pin via the puzzle-piece icon after install.
```

Run `claude --version` via Bash and surface the result.

## Enable Chrome in Claude Code

The user must run these themselves (slash commands can't be triggered for them):

```
A.  Inside Claude Code:   /chrome     → "Enable" (or "Enabled by default")
B.  Verify:               /mcp        → look for "claude-in-chrome"
C.  Site permissions are managed inside the Chrome extension
    (click the extension icon → settings). Allow whichever sites
    you actually test on (localhost, staging, prod).
```

## Quick troubleshooting

| Symptom | Fix |
|---|---|
| "Extension not detected" | `chrome://extensions` — confirm installed + enabled. Update if < 1.0.36. |
| "Browser extension is not connected" | Restart Chrome and Claude Code, then `/chrome` → "Reconnect". |
| Works once then dies | Service worker idled. `/chrome` → "Reconnect extension". |
| "Receiving end does not exist" | Same — reconnect. |
| First-time connection fails | Restart Chrome (native messaging host config picked up on startup). |
| `tabs_context_mcp` returns empty array | Open at least one tab in the controlled Chrome window. |

## Confirm

After the user says they're set up, run preflight (`tabs_context_mcp`). On pass:

> Connection good. Paste a test description: `/ui-test "<description>"`.
