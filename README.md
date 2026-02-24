# 🛠️ Claude Skills

Collection of [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for **Claude Code** and **Claude Desktop / claude.ai** — developer workflows, automation, and productivity.

Both platforms use the same SKILL.md format, but Claude Code skills have access to your local filesystem, shell, subagents, and MCP servers. Desktop skills run in a sandboxed VM — great for research, writing, and analysis.

## 📋 What's Inside

```
claude-skills/
├── code/                  # Claude Code skills (16 skills)
│   ├── SKILLS_GUIDE.md    # Design conventions for Code skills
│   ├── whats-next/
│   ├── create-pr/
│   └── ...
├── desktop/               # Claude Desktop / claude.ai skills
│   ├── README.md          # Install guide for Desktop
│   ├── research-assistant/
│   └── inbox-catchup/
```

---

## ⚡ Claude Code Skills

Full-access skills that integrate with your local dev environment — git, GitHub, Linear, shell, filesystem, MCP servers.

### Install

```bash
# Clone and copy all skills
git clone https://github.com/mostafa-drz/claude-skills.git
cp -r claude-skills/code/* ~/.claude/skills/

# Or copy a single skill
cp -r claude-skills/code/whats-next ~/.claude/skills/
```

Each skill supports `/skill-name help` for usage, `/skill-name config` for preferences, and learns from your corrections over time. See the [Design Guide](code/SKILLS_GUIDE.md) for conventions.

### Catalog

| Skill | Description | Side Effects |
|-------|-------------|:------------:|
| [`/address-pr-comments`](code/address-pr-comments/SKILL.md) | Fetches unresolved PR comments, categorizes and addresses them | Yes |
| [`/audit-skills`](code/audit-skills/SKILL.md) | Audits skills against manifest and upstream docs | Yes |
| [`/build-incremental`](code/build-incremental/SKILL.md) | Implements code in progressive, verified increments | Yes |
| [`/create-pr`](code/create-pr/SKILL.md) | Creates well-structured PRs with Linear linking | Yes |
| [`/git-cleanup`](code/git-cleanup/SKILL.md) | Removes stale branches, orphaned remotes, unused worktrees | Yes |
| [`/investigate-ci`](code/investigate-ci/SKILL.md) | Investigates GitHub Actions workflow failures | No |
| [`/organize-screenshots`](code/organize-screenshots/SKILL.md) | Scans and organizes screenshots with descriptive names | Yes |
| [`/post-pr-for-review`](code/post-pr-for-review/SKILL.md) | Generates contextual Slack message for PR review requests | Yes |
| [`/post-ticket-summary`](code/post-ticket-summary/SKILL.md) | Posts implementation summary to Linear issues | Yes |
| [`/publish-skills`](code/publish-skills/SKILL.md) | Publishes skills to a GitHub repo for sharing | Yes |
| [`/skill-creator`](code/skill-creator/SKILL.md) | Creates new skills interactively with guided questions | Yes |
| [`/slack-to-ticket`](code/slack-to-ticket/SKILL.md) | Creates Linear issues from Slack threads | Yes |
| [`/smoke-test`](code/smoke-test/SKILL.md) | Traces and verifies E2E in any environment | Yes |
| [`/sync-branch`](code/sync-branch/SKILL.md) | Merges branches with conflict handling | Yes |
| [`/thread-to-action`](code/thread-to-action/SKILL.md) | Parses threads and suggests developer actions | Yes |
| [`/whats-next`](code/whats-next/SKILL.md) | Suggests top 3 next actions from full context | No |

---

## 🖥️ Claude Desktop / claude.ai Skills

Sandboxed skills for knowledge work — no local filesystem or shell access needed. Works in the Claude Desktop app and claude.ai web.

### Install

1. Download the skill folder
2. ZIP it: `zip -r skill-name.zip skill-name/`
3. Go to **Settings > Capabilities** in Claude Desktop or claude.ai
4. Toggle on **Code execution and file creation**
5. Click **Upload skill** and select the `.zip`

Requires Pro, Max, Team, or Enterprise plan. See the [Desktop install guide](desktop/README.md) for details.

### Catalog

| Skill | Description |
|-------|-------------|
| [`research-assistant`](desktop/research-assistant/SKILL.md) | Systematic topic research with structured briefing output |
| [`inbox-catchup`](desktop/inbox-catchup/SKILL.md) | Scans connected comms (Gmail, Slack, Calendar), builds prioritized briefing, helps draft replies |

---

## 🔍 Code vs Desktop — When to Use What

| | Claude Code | Claude Desktop / claude.ai |
|---|:---:|:---:|
| **Best for** | Dev workflows, automation, CI/CD | Research, writing, analysis |
| Local filesystem | ✅ | - |
| Shell / Bash | ✅ | - |
| Slash commands (`/skill`) | ✅ | - |
| Dynamic context (`$ARGUMENTS`) | ✅ | - |
| Subagents | ✅ | - |
| MCP servers | ✅ | - |
| Sandboxed code execution | ✅ | ✅ |
| Bundled scripts | N/A | ✅ |

Both use the same `SKILL.md` format with YAML frontmatter + Markdown instructions. The [Agent Skills spec](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) covers the shared format.

---

## 📚 Further Reading

- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — Official spec
- [Extend Claude with Skills](https://code.claude.com/docs/en/skills) — Claude Code docs
- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude) — Desktop / claude.ai help
- [How to Create Custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) — Official guide
- [Anthropic Skills Repo](https://github.com/anthropics/skills) — Official examples

## 📄 License

[MIT](LICENSE)

---

*Built with Claude Code and too many terminal tabs.*
