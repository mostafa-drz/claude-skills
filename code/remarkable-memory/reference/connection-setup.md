# Connecting a reMarkable

Load this when running `/remarkable-memory setup` or when a sync preflight fails.
Three connection paths; pick one and save it as `connection` in preferences.

Reality checks to set expectations honestly:

- **Wireless/cloud sync needs reMarkable Connect** (~$3.99/mo). **USB and SSH are
  free.** On-device handwriting→text is free too, but the useful stuff (cross-
  notebook access, cloud pull) is what the connection provides.
- **The cloud API is community-reverse-engineered**, not an official reMarkable
  product. It can and does change. When a sync suddenly breaks, this is almost
  always why — not the user's notes. Say so.
- **Claude vision reads the handwriting** — no MyScript/OCR key required. MyScript
  (reMarkable's own engine) is only an alternative if the user prefers it.

---

## Option 1 — reMarkable MCP server (recommended)

Free, open-source (MIT). Exposes the tablet to Claude as MCP tools, so pages come
straight into the session. Supports three modes internally: USB web interface (no
subscription), SSH (developer mode), and cloud (Connect). Hand pages to Claude as
**page-image renders** and let Claude read them — that's the keyless path.

- Repo: `https://github.com/SamMorrowDrums/remarkable-mcp`
- Also seen as `wavyrai/rm-mcp` and other forks — any that expose read + page-image
  tools work.

> **Note on "no OCR key."** The server's own OCR-text backend uses Google Vision
> (needs an API key) or Tesseract (poor on handwriting); its keyless OCR relies on
> **MCP sampling**, which **Claude Code does not support**. So on Claude Code, don't
> use the OCR-text tool — use the **page-image** tool and let Claude read the image
> directly. Claude Desktop does support sampling, but the image path works there too
> and is what the Desktop companion uses.

### USB happy-path (free, no subscription, most reliable)

The fiddly bit is on the tablet, not the software — do this first:

1. On the reMarkable: **Settings → Storage → enable "USB web interface."**
2. Plug the tablet into the computer with the USB cable.
3. In a browser, open **`http://10.11.99.1`** — you should see your documents. If
   that page loads, the device side is working.
4. Install the MCP server per its README (Python) and point it at USB mode.
5. Add it to the host client's MCP config:
   - **Claude Code**: `claude mcp add …`, or edit `.mcp.json` / user MCP config.
   - **Claude Desktop**: add to the Desktop MCP settings JSON.
6. **Restart the client.** New MCP tools load only at session start — a
   same-session preflight will fail until you restart.
7. Re-run `/remarkable-memory setup`. Preflight looks for a `mcp__*remarkable*` tool.

### SSH / cloud modes

- **SSH** gives full filesystem access and is the most powerful, but requires
  putting the tablet into **developer mode — which factory-resets the device.** Only
  go here if you know you want it and have backed up.
- **Cloud** is wireless but needs a reMarkable **Connect** subscription (~$3.99/mo).

Preflight (any mode): a reMarkable MCP read/list tool responds without error.

---

## Option 2 — rmapi (CLI)

Free Go CLI for the reMarkable cloud API. Good for terminal-native users.

- Repos: `https://github.com/ddvk/rmapi` (maintained fork) ·
  `https://github.com/juruen/rmapi` (original, effectively unmaintained)

Setup:
1. Install the binary (`go install` or a release).
2. First run prompts for a **one-time pairing code** from
   `https://my.remarkable.com/device/desktop/connect` — this registers a device
   token stored locally.
3. Verify: `rmapi ls` lists your cloud documents.

Preflight: `rmapi account` (or `rmapi ls`) exits 0. Requires cloud (Connect).

Sync via rmapi: `rmapi get <path>` pulls a document, but it arrives in reMarkable's
proprietary **`.rm` lines format** plus metadata — not an image. rmapi alone is fine
for **typed (Type Folio) text and metadata**, but the **handwriting-image path needs
a `.rm`→PNG/SVG renderer** (e.g. `rmc`/`rmrl`), which this skill does not bundle or
install. So for handwritten pages, prefer **Option 1 (the MCP server)**, which
renders pages for you. Use rmapi standalone only if your notebooks are typed text or
you already have a renderer wired up.

---

## Option 3 — remarkdown (hosted, zero-install)

A hosted MCP server. Nothing runs locally; pair once with a code and the token stays
on their side, encrypted. Easiest onboarding, but it's a paid third party holding a
token.

- Site: `https://remarkdown.org`
- Pricing (as surveyed): pairing + pushing notes is free; **reading, full-text
  search, and handwriting transcription are "Pro" at ~$9/mo.**

Setup:
1. Pair the tablet at remarkdown.org with a one-time code.
2. Add their hosted MCP endpoint to the host client's MCP config.
3. Re-run setup; preflight checks their tool responds.

Trade-off to state plainly: zero maintenance and no local process, but a monthly fee
and a third party in the trust path. For a personal/portfolio build, Option 1 keeps
everything local and free.

---

## Quick troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Preflight finds no reMarkable tool | MCP server not added to this client's config, or not running. Re-add and restart the client. |
| `rmapi` says unauthorized | Token expired/revoked. Re-pair with a fresh code from my.remarkable.com. |
| Sync worked yesterday, fails today with API errors | The community cloud API likely changed. Check the MCP/rmapi repo issues for a fix; not a problem with the notes. |
| Cloud mode says "not subscribed" | Cloud needs reMarkable Connect. Switch to USB/SSH mode, or subscribe. |
| Pages come back blank/garbled | Wrong mode for the device state, or a page still syncing on the tablet. Re-open it on the device, let it sync, retry. |
