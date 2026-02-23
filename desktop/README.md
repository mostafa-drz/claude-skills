# Claude Desktop / claude.ai Skills

Skills for use in [Claude Desktop](https://claude.ai/download) and [claude.ai](https://claude.ai) web.

## How to Install

1. **Download** — Clone this repo or download the skill folder you want
2. **ZIP it** — Create a `.zip` file containing the skill folder (the folder with `SKILL.md` inside it)
3. **Upload** — Go to **Settings > Capabilities** in Claude Desktop or claude.ai
4. **Enable** — Toggle on "Code execution and file creation" if not already enabled
5. **Add skill** — Scroll to **Skills**, click **Upload skill**, select your `.zip` file

```bash
# Example: install research-assistant
cd desktop
zip -r research-assistant.zip research-assistant/
# Then upload research-assistant.zip via Settings > Capabilities > Skills
```

**Requirements:** Pro, Max, Team, or Enterprise plan.

## How Desktop Skills Differ from Code Skills

Desktop/claude.ai skills run in a **sandboxed VM** — they don't have access to your local filesystem, shell, or network the way Claude Code skills do.

| Feature | Desktop / claude.ai | Claude Code |
|---------|:-------------------:|:-----------:|
| Local filesystem access | - | ✅ |
| Shell / Bash execution | - | ✅ |
| Slash command invocation | - | ✅ |
| `$ARGUMENTS` / dynamic context | - | ✅ |
| Subagents | - | ✅ |
| MCP server integration | - | ✅ |
| Sandboxed Python/JS execution | ✅ | ✅ |
| Bundled scripts in ZIP | ✅ | N/A |

Desktop skills are best for **knowledge work** — research, writing, analysis, formatting — where you don't need to touch the local machine.

## Available Skills

| Skill | Description |
|-------|-------------|
| [`research-assistant`](research-assistant/SKILL.md) | Systematic topic research with structured briefing output |

## Further Reading

- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude) — Official help center
- [How to Create Custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) — Official guide
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — API documentation
