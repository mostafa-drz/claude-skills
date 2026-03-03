---
name: respond-to-message
description: >-
  Crafts a response to a pasted message (LinkedIn, Slack, Gmail, Teams, etc.)
  in the user's configured tone and voice. Loads platform-specific context and
  formatting rules, generates a response matching the platform's conventions,
  and copies it to clipboard for immediate pasting. Use when you receive a
  message and need to reply quickly in your own voice.
argument-hint: <platform> [--refine] [--formal] [--casual]
disable-model-invocation: true
context: fork
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Glob
---

# Respond to Message

Craft responses to messages in your voice, matched to the platform. Copies to clipboard for pasting.

## Preferences

Before starting, use the `Read` tool to read `~/.claude/skills/respond-to-message/preferences.md`. If the file does not exist, treat as "no preferences set" and use defaults.

## Tone Profile

Use the `Read` tool to read `~/.claude/skills/respond-to-message/reference/tone-profile.md`. If it does not exist, fall back to preferences tone keywords. If neither exists, ask the user to describe their tone.

## Platform Context

Use `Glob` to check which platform files exist at `~/.claude/skills/respond-to-message/reference/platforms/*.md`. For the active platform, read its context file. If no file exists for the requested platform, use sensible defaults for that platform's conventions.

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/respond-to-message/preferences.md`, confirm, stop
- **`tone`** → open tone profile editing flow then stop
- **anything else** (including empty) → run the skill

### Help

```
Respond to Message — Craft replies in your voice, matched to the platform

Usage:
  /respond-to-message <platform>           Craft a response (then paste the message)
  /respond-to-message                      Auto-detect platform or ask
  /respond-to-message --refine             Re-draft the last response with feedback
  /respond-to-message --formal             Override tone to more formal
  /respond-to-message --casual             Override tone to more casual
  /respond-to-message config               Set up tone, platforms, and context
  /respond-to-message tone                 Edit your tone profile with examples
  /respond-to-message reset                Clear preferences
  /respond-to-message help                 This help

Platforms: linkedin, slack, gmail, teams, whatsapp, twitter, generic

Examples:
  /respond-to-message linkedin             Then paste the LinkedIn message in chat
  /respond-to-message slack                Then paste the Slack message + optional draft
  /respond-to-message gmail --formal       Reply to an email with formal tone override

Current preferences:
  (from preferences.md or defaults)
```

### Config

Use `AskUserQuestion` to collect:

**Q1: Tone keywords** — How would you describe your communication style? (e.g., "direct, warm, professional but not stiff, uses analogies")

**Q2: Your role/title** — Used for professional context in responses (e.g., "VP of Engineering at Acme Corp")

**Q3: Active platforms** — Which platforms do you want configured? (multiSelect: LinkedIn, Slack, Gmail, Teams, WhatsApp, Twitter/X)

**Q4: Sample messages** — "Would you like to paste 2-3 example messages you've written so I can learn your tone? (recommended)" (Yes/No)

If Q4 is Yes, use `AskUserQuestion` to collect sample messages, then analyze them for:
- Sentence length patterns
- Greeting/closing conventions
- Level of formality
- Use of humor, emojis, or directness
- Vocabulary tendencies

Save tone analysis + samples to `reference/tone-profile.md`.

For each platform selected in Q3, ask:

**Platform-specific Q** — "Any specific context for {platform}? (e.g., your LinkedIn headline, Slack workspace role, email signature)" — save to `reference/platforms/{platform}.md`.

Save overall preferences to `~/.claude/skills/respond-to-message/preferences.md`.

### Tone

Interactive flow to update the tone profile:

1. Read current `reference/tone-profile.md` (if exists, show summary)
2. Ask: "Paste 2-3 messages you've recently sent that represent your voice."
3. Analyze patterns and update `reference/tone-profile.md`
4. Confirm: "Tone profile updated. Key traits: {traits}."

### Reset

Delete `~/.claude/skills/respond-to-message/preferences.md` and confirm: "Preferences cleared. Using defaults. (Tone profile and platform contexts are preserved — delete them manually if needed.)"

## First-time detection

If no preferences file AND no tone profile exist, show:

> First time using /respond-to-message? Run `/respond-to-message config` to set up your tone and platforms, or just continue — I'll ask what I need as we go.

Then proceed normally.

## Workflow

### Step 1: Detect platform

If `$ARGUMENTS` contains a platform name (linkedin, slack, gmail, teams, whatsapp, twitter, generic), use it.

If no platform specified, check the pasted message for cues:
- "via LinkedIn" / LinkedIn formatting → linkedin
- Slack-style formatting (channel names, @mentions, threads) → slack
- Email headers (From:, Subject:, etc.) → gmail
- Teams-style formatting → teams

If still ambiguous, ask:

> What platform is this message from?

Options: LinkedIn, Slack, Gmail, Teams, WhatsApp, Twitter/X, Other

### Step 2: Parse the input

From the conversation context, extract:
- **Incoming message** — the message the user received and needs to respond to
- **Draft response** (optional) — the user's initial attempt, to be refined
- **Sender context** — who sent it (name, title, relationship if apparent)
- **Thread context** — is this a reply in an ongoing conversation?
- **Specific instructions** — any guidance like "decline politely" or "express interest but ask about timeline"

If the incoming message isn't clear, ask:

> Paste the message you want to respond to. You can also include a draft response if you have one.

### Step 3: Load tone and context

1. **Tone profile** — read from `reference/tone-profile.md`
2. **Platform context** — read from `reference/platforms/{platform}.md`
3. **Preferences** — read from `preferences.md`

Merge into a response framework:
- **Voice**: tone keywords + sample patterns
- **Format**: platform-specific conventions (see Step 5)
- **Context**: role, company, expertise areas

### Step 4: Analyze and strategize

Before drafting, consider:
- **Intent**: What does the sender want? What should the response achieve?
- **Relationship**: Professional contact, colleague, recruiter, client, friend?
- **Stakes**: Casual conversation, business opportunity, sensitive topic?
- **Action needed**: Accept, decline, defer, negotiate, inform, ask?

If the user provided a draft, identify what to keep and what to improve.

If the intent is unclear, ask one clarifying question:

> This looks like [interpretation]. Do you want to [suggested action], or something else?

### Step 5: Craft the response

Write the response following platform conventions:

**LinkedIn:**
- Professional but personable
- Keep under 300 words for DMs
- No markdown (LinkedIn strips it) — use line breaks for structure
- Opening: acknowledge their message specifically
- Close: clear next step or warm sign-off

**Slack:**
- Concise, conversational
- Use emoji sparingly (match workspace culture)
- Bold for emphasis, code blocks for technical content
- Thread-aware — reference what was said above
- No formal sign-offs

**Gmail:**
- Proper email structure (greeting, body, sign-off)
- Match formality to the sender's style
- Keep paragraphs short (2-3 sentences)
- Clear subject line suggestion if starting a new thread
- Include email signature if configured

**Teams:**
- Similar to Slack but slightly more formal
- Support for mentions (@Name)
- Keep it scannable

**WhatsApp:**
- Short, casual
- Emoji-friendly
- Break into multiple short messages if content is long

**Twitter/X:**
- Under 280 characters (or note if a thread is needed)
- Punchy, direct
- Hashtags only if relevant

**Generic:**
- Match the sender's format and length
- Default to professional-casual

Apply tone profile throughout. The response should sound like the user, not like AI.

### Step 6: Copy to clipboard

1. Write the response to `/tmp/respond-to-message-output.md` using the `Write` tool
2. Run `pbcopy < /tmp/respond-to-message-output.md` via `Bash`
3. Report:

> **Copied to clipboard.** Ready to paste.
>
> ---
> {the response, displayed for review}
> ---
>
> `/respond-to-message --refine` to adjust, or just paste it.

### Step 7: Handle refinement

If `--refine` flag is set or the user asks to adjust:

1. Ask what to change (shorter, more formal, different angle, etc.)
2. Re-draft
3. Copy new version to clipboard
4. Show diff summary: "Made it [shorter/more formal/etc.]"

## Principles

- **Sound like the user, not like AI** — the response must match the user's actual voice. Generic, overly polished AI-speak is a failure. Use the tone profile religiously.
- **Platform-native formatting** — a LinkedIn DM should look like a LinkedIn DM, not a formatted email. Match conventions exactly.
- **Clipboard-first** — always `pbcopy`. The user should be able to Cmd+V immediately after the skill runs.
- **Clarify when unsure** — if the intent or desired action isn't clear, ask ONE focused question rather than guessing wrong.
- **Minimal not maximal** — shorter responses are usually better. Don't pad with pleasantries or filler unless that's the user's actual style.
