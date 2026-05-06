---
name: capture-screens
description: >-
  Automatically navigates a web app using Playwright MCP and captures
  context-aware named screenshots at each product feature state. Names each
  file semantically based on context (e.g., checkout-payment-form-filled.png).
  Outputs a manifest.json mapping filenames to descriptions and a summary
  report. Use when documenting product features, generating demo screenshots,
  building user guides, or creating visual test assets for any web application.
  Composable primitive — other skills (user-guide, demo-docs) consume its
  manifest.json output.
argument-hint: "[context-description] [--url <url>] [--features <list>] [--output <dir>] [--no-highlight] [--viewport <WxH>] [--auth <instructions>] [--inject-js <file>]"
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Bash(mkdir *)
  - mcp__playwright__browser_navigate
  - mcp__playwright__browser_snapshot
  - mcp__playwright__browser_evaluate
  - mcp__playwright__browser_take_screenshot
  - mcp__playwright__browser_wait_for
  - mcp__playwright__browser_click
  - mcp__playwright__browser_type
  - mcp__playwright__browser_resize
  - mcp__playwright__browser_console_messages
---

## Preferences

_On startup, use Read to load `~/.claude/skills/capture-screens/preferences.md`. If missing, use defaults below._

Defaults:
- `url`: `http://localhost:3000`
- `output`: `screenshots`
- `viewport`: `1440x900`
- `highlight`: true
- `highlight-color`: `#FF4B4B`
- `wait-ms`: `800`

## Context

_On startup, use Bash to detect the current working directory. Use this for default output path resolution._

## Command routing

Check `$ARGUMENTS`:
- `help` → show help, stop
- `config` → run config flow, stop
- `reset` → delete preferences file, confirm, stop
- anything else → run the skill

## Help

```
capture-screens — Automated contextual screenshot capture via Playwright

Usage:
  /capture-screens [context]                          Interactive — prompts for missing inputs
  /capture-screens [context] --url <url>              App URL to capture
  /capture-screens [context] --features <f1,f2,...>   Comma-separated routes or feature names
  /capture-screens [context] --output <dir>           Output directory (default: screenshots/)
  /capture-screens [context] --no-highlight           Skip CSS highlight injection
  /capture-screens [context] --viewport <WxH>         Viewport size (default: 1440x900)
  /capture-screens [context] --auth <instructions>    How to authenticate, e.g. "login as admin@example.com / pass123"
  /capture-screens [context] --inject-js <file>       Path to a JS file to evaluate before capturing (e.g. to seed state)
  /capture-screens config                             Set persistent preferences
  /capture-screens reset                              Clear preferences
  /capture-screens help                               This help

Context argument:
  Free-text description of what you're capturing. Used to generate semantic
  filenames and manifest descriptions. Example:
  "Checkout flow — cart summary, shipping form, payment step, confirmation"

Examples:
  /capture-screens "Settings page — profile tab, notifications, billing"
  /capture-screens "Onboarding flow" --url https://staging.myapp.com --auth "skip login, go to /onboarding"
  /capture-screens "Admin dashboard" --url http://localhost:3000 --no-highlight --output docs/screenshots
  /capture-screens "Product tour" --inject-js seed-demo-state.js

Output:
  {output}/                    ← semantically-named PNGs
  {output}/manifest.json       ← filename → description map (for downstream skills)
  {output}/capture-report.md   ← human-readable summary with descriptions

Current preferences:
  (shown from preferences.md)
```

## Config

Use AskUserQuestion to collect:

1. **Default URL** — what URL does your app run on? (default: `http://localhost:3000`)
2. **Default output directory** — where to save screenshots? (default: `screenshots`)
3. **Viewport size** — browser viewport? (default: `1440x900`)
4. **Highlight color** — CSS color for element highlights? (default: `#FF4B4B`)
5. **Default wait** — ms to wait after navigation before screenshot? (default: `800`)

Save to `~/.claude/skills/capture-screens/preferences.md`.

## Reset

Delete `~/.claude/skills/capture-screens/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists, show:
> First time using /capture-screens? Run `/capture-screens config` to set your defaults, or continue — sensible defaults will be used.

Then proceed.

## Workflow

### Step 1 — Gather inputs

Parse `$ARGUMENTS` for:
- **Context description** — free text before any `--flag`
- `--url <url>` — app URL (fallback: preferences → `http://localhost:3000`)
- `--features <list>` — comma-separated routes or feature names
- `--output <dir>` — output directory (fallback: preferences → `screenshots`)
- `--no-highlight` — skip CSS highlight injection
- `--viewport <WxH>` — e.g., `1440x900`
- `--auth <instructions>` — how to authenticate (e.g., `"login as user@example.com / password"`)
- `--inject-js <file>` — path to a JS file to evaluate before capturing (for any custom state setup: localStorage, cookies, mocked APIs, etc.)

If **context description** is missing, ask:
> What are you capturing? Describe the product area and key states to document.
> Example: "Checkout flow — cart, shipping, payment, confirmation page"

If **features** are missing, derive a capture plan from the context description. Ask to confirm:
> Based on your description, I'll capture: [list of routes/states]. Anything to add or remove?

### Step 2 — Prepare output directory

Create the output directory:
```
mkdir -p {output}
```

### Step 3 — Open browser and set viewport

1. Navigate to `--url` via `browser_navigate`
2. Resize via `browser_resize` to `{viewport}`
3. Take a baseline `browser_snapshot` to verify the page loaded

**Authentication** — if the page requires login:
- If `--auth` was provided, follow those instructions using `browser_type` and `browser_click`
- Otherwise ask: "The page requires login. How should I authenticate? (provide credentials or 'skip' to continue unauthenticated)"
- Wait for the authenticated state before continuing

### Step 4 — Inject custom JS (if --inject-js provided)

If `--inject-js <file>` was provided:
1. Read the file contents with Read
2. Evaluate via `browser_evaluate`
3. Reload the page via `browser_navigate` to let the app pick up any injected state
4. Wait for the page to stabilize

This is the escape hatch for any app-specific state seeding — localStorage, sessionStorage, cookies, API mocking, feature flags, etc. The skill itself has no opinion about what the JS does.

### Step 5 — Inject highlight utility (skip if --no-highlight)

Inject once into the page via `browser_evaluate`:

```javascript
const style = document.createElement('style');
style.id = '__capture-highlight-style';
style.textContent = `
  [data-capture-highlight] {
    outline: 3px solid {highlight-color} !important;
    outline-offset: 3px !important;
    border-radius: 4px !important;
    box-shadow: 0 0 0 6px {highlight-color}22 !important;
  }
`;
document.head.appendChild(style);

window.__captureHighlight = (selector) => {
  document.querySelectorAll('[data-capture-highlight]')
    .forEach(el => el.removeAttribute('data-capture-highlight'));
  const el = selector ? document.querySelector(selector) : null;
  if (el) {
    el.setAttribute('data-capture-highlight', '');
    el.scrollIntoView({ block: 'center', behavior: 'instant' });
  }
};

window.__captureClearHighlight = () => {
  document.querySelectorAll('[data-capture-highlight]')
    .forEach(el => el.removeAttribute('data-capture-highlight'));
};
```

### Step 6 — Capture each feature/state

For each item in the capture plan:

1. **Navigate** to the route via `browser_navigate` (or `browser_click` for tabs/buttons within the same page)
2. **Wait** for content via `browser_wait_for` — target a meaningful selector (main content area, data table, heading) or fall back to `{wait-ms}` ms
3. **Snapshot** via `browser_snapshot` to understand the current page structure
4. **Identify key element** to highlight — the most visually significant element for this state (active tab, primary action, key data component). Skip if nothing meaningful to highlight.
5. **Highlight** via `browser_evaluate`: `window.__captureHighlight('{selector}')`
6. **Screenshot** via `browser_take_screenshot`
7. **Generate semantic filename** from context (see Filename rules below)
8. **Save** to `{output}/{filename}.png`
9. **Record** in manifest: `{ filename, description, route, timestamp }`
10. **Clear highlight** via `browser_evaluate`: `window.__captureClearHighlight()`

**Within-page states** (tabs, modals, dropdowns, hover states):
- Use `browser_click` to open the state, screenshot, then restore to neutral state before moving on

**On failure**: log the error and skip — never abort the full session for one bad step.

### Step 7 — Write outputs

**`{output}/manifest.json`:**
```json
{
  "capturedAt": "{ISO timestamp}",
  "url": "{app url}",
  "viewport": "{WxH}",
  "context": "{context description}",
  "screenshots": [
    {
      "filename": "settings-profile-tab-overview.png",
      "description": "Settings page — Profile tab showing name, avatar, and account details",
      "route": "/settings/profile",
      "selector": ".profile-form"
    }
  ]
}
```

**`{output}/capture-report.md`:**
```markdown
# Screenshot Capture Report
**Context:** {context description}
**URL:** {url}
**Captured:** {timestamp}
**Count:** {N} screenshots → `{output}/`

## Screenshots

### {Feature Area}
**File:** `{filename}.png`
**Route:** `{route}`
**Description:** {description}

---
```

### Step 8 — Report

```
Captured {N} screenshots → {output}/
  ✓ {filename1}.png — {description}
  ✓ {filename2}.png — ...

Manifest: {output}/manifest.json
Report:   {output}/capture-report.md
```

List any skipped steps and their errors at the end.

## Filename generation rules

- **Format:** `{feature}-{sub-feature}-{state}.png` (2-3 levels, kebab-case)
- **Specific:** `checkout-payment-form-filled.png` not `checkout-3.png`
- **State-aware:** append `-open`, `-empty`, `-active`, `-selected`, `-error` when the UI state matters
- **Unique:** if two shots of the same feature, differentiate by state — never append `-2`
- **Max 60 chars** excluding `.png`
- Derive names from: context description + current route + page title visible in snapshot + key elements visible

## Principles

1. **App-agnostic by default** — no assumptions about framework, auth method, or state management; ask or accept instructions rather than guessing
2. **Snapshot before screenshot** — always `browser_snapshot` first to understand page structure before deciding what to highlight and capture
3. **Name from what you see, not sequence** — derive filenames from the actual content visible in the snapshot, not from a counter
4. **`--inject-js` is the escape hatch** — any app-specific state setup (localStorage, cookies, API mocks) belongs in an external JS file the user provides; the skill doesn't know or care what it does
5. **Graceful continuation** — a failed step is logged and skipped; the session completes as much as possible
