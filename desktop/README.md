# Claude Desktop / claude.ai Skills

Skills for use in [Claude Desktop](https://claude.ai/download) and [claude.ai](https://claude.ai) web. These extend Claude with specialized behaviors — structured workflows, domain expertise, and repeatable processes — without needing any coding environment.

## How Skills Work

A skill is a `SKILL.md` file — plain Markdown with a YAML header — that tells Claude **how** to handle a specific type of request. When you upload a skill, Claude reads its description and automatically activates it when your request matches.

For example, if you have the `research-assistant` skill installed and ask _"Research the current state of WebAssembly"_, Claude recognizes the match and follows the skill's structured research process instead of giving a generic answer.

**Skills are not plugins or code.** They're instruction sets. Think of them as expert playbooks that Claude follows.

## Install a Skill

### Step 1: Get the skill files

```bash
# Clone the repo
git clone https://github.com/mostafa-drz/claude-skills.git

# Or download just the skill folder you want from GitHub
```

### Step 2: Create a ZIP

The ZIP must contain the skill folder (with `SKILL.md` inside). The folder name should match the skill name.

```bash
cd claude-skills/desktop

# ZIP a single skill
zip -r inbox-catchup.zip inbox-catchup/
```

**ZIP structure should look like:**
```
inbox-catchup.zip
└── inbox-catchup/
    └── SKILL.md
```

### Step 3: Upload to Claude

1. Open [claude.ai](https://claude.ai) or the Claude Desktop app
2. Go to **Settings** (gear icon) > **Capabilities**
3. Make sure **"Code execution and file creation"** is toggled ON
4. Scroll to the **Skills** section
5. Click **"Upload skill"**
6. Select your `.zip` file

The skill appears in your Skills list. You can toggle it on/off per conversation.

**Plan required:** Pro, Max, Team, or Enterprise.

### Step 4: Use it

Just start a conversation. Claude activates matching skills automatically based on your message. You can also mention the skill by name:

> _"Use inbox-catchup to check my messages"_
>
> _"Research the pros and cons of server-side rendering"_

## Configuring Skills

Some Desktop skills have a **Configuration** section inside their `SKILL.md` with editable defaults. To customize:

1. Open the `SKILL.md` in any text editor
2. Find the `## Configuration` section
3. Edit the values (time window, tone, sources, etc.)
4. Re-ZIP and re-upload

Since Desktop skills run in a sandboxed environment, they can't persist preferences to disk the way Claude Code skills do. Configuration is either baked into the SKILL.md or asked at the start of each conversation.

## Connecting Integrations

Desktop skills can use whatever integrations are connected to your Claude account:

**Google Workspace** (built-in on Pro/Max/Team/Enterprise):
- Settings > Connected apps > Connect Google account
- Gives skills access to Gmail, Google Calendar, Google Drive

**MCP Servers** (Claude Desktop app only):
- Configure in Claude Desktop's settings file (`claude_desktop_config.json`)
- Skills can use any MCP server you've set up (Slack, databases, APIs, etc.)
- [MCP setup guide](https://modelcontextprotocol.io/quickstart/user)

**What if nothing is connected?** Skills that need integrations will detect what's available and tell you what to connect. They won't fabricate data or pretend a source exists.

## How Desktop Skills Differ from Code Skills

Desktop/claude.ai skills run in a **sandboxed VM**. They're great for knowledge work but can't touch your local machine.

| Feature | Desktop / claude.ai | Claude Code |
|---------|:-------------------:|:-----------:|
| Local filesystem access | - | ✅ |
| Shell / Bash execution | - | ✅ |
| Slash command invocation (`/skill`) | - | ✅ |
| Arguments (`$ARGUMENTS`) | - | ✅ |
| Subagents | - | ✅ |
| MCP server integration | Via Desktop app | ✅ |
| Google Workspace integration | ✅ | - |
| Sandboxed Python/JS execution | ✅ | ✅ |
| Bundled scripts in ZIP | ✅ | N/A |
| Persistent preferences | - | ✅ |

**Best for:** research, writing, analysis, communication triage, document generation — anything that doesn't need local file access.

## Available Skills

### inbox-catchup

Scans all connected communication channels — Gmail, Slack, Calendar, and any available integrations — then produces a prioritized catchup briefing. Helps triage messages and draft replies.

**When to use:** Starting the day, returning from a break, or needing to quickly catch up on communications.

**Requires:** At least one communication integration (Google Workspace for Gmail/Calendar, or MCP servers for Slack/Teams).

**Configurable:** Sources to scan, time window, priority contacts, reply tone, auto-draft behavior.

[View full skill](inbox-catchup/SKILL.md)

---

### research-assistant

Researches a topic systematically and produces a structured briefing with key facts, perspectives, timeline, and open questions.

**When to use:** Researching a topic, preparing a briefing, or compiling background before a meeting or decision.

**Requires:** No integrations needed — works with Claude's built-in knowledge and web search.

**Output:** Structured briefing document with Overview, Key Facts, Perspectives, Timeline, and Open Questions sections.

[View full skill](research-assistant/SKILL.md)

---

## Creating Your Own Desktop Skill

Desktop skills use the same `SKILL.md` format as Claude Code skills, minus the Code-specific features:

```yaml
---
name: my-skill-name
description: >-
  Does X when the user asks for Y. Use when [trigger scenario].
---

# My Skill Name

## Process

1. First step
2. Second step
3. ...

## Guidelines

- Principle one
- Principle two
```

**Rules:**
- `name`: lowercase, hyphens only, max 64 chars
- `description`: third-person, include trigger keywords and "Use when..." — this is how Claude decides when to activate
- Keep instructions under 500 lines
- Don't include `allowed-tools`, `disable-model-invocation`, or `$ARGUMENTS` — those are Code-only features

**Test before sharing:** Upload your skill and try it in a few conversations to make sure Claude triggers it correctly and follows the instructions.

## Troubleshooting

**Skill not activating?**
- Check that "Code execution and file creation" is ON in Settings > Capabilities
- Make sure the skill is toggled ON in your Skills list
- Try mentioning the skill by name in your message
- Check that the `description` field has clear trigger keywords

**ZIP upload failing?**
- Make sure the ZIP contains a folder (not loose files) with `SKILL.md` inside
- Folder name must match the `name` in YAML frontmatter
- No special characters in the folder name

**Integrations not working?**
- Google Workspace: check Settings > Connected apps
- MCP servers: only available in the Claude Desktop native app, not claude.ai web
- Some integrations require specific plan tiers

## Further Reading

- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude) — Official help center
- [How to Create Custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) — Official guide
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — API documentation
- [Anthropic Skills Repo](https://github.com/anthropics/skills) — Official example skills
