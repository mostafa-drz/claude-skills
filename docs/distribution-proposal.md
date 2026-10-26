# Proposal: make claude-skills a standard, installable skills package

Status: **accepted, implemented** · Date: 2026-10-26

## 1. What "standard" means in October 2026

| Layer | Standard | What it requires | Who uses it |
|---|---|---|---|
| Skill format | [Agent Skills spec](https://agentskills.io/specification) | `SKILL.md` with `name` (= dir, kebab, ≤64) + `description` (≤1024). Optional `license`, `compatibility` (≤500), `metadata` (string→string), `allowed-tools`. Dirs: `scripts/`, `references/`, `assets/`. Body < 500 lines. Validator: `skills-ref validate` rejects any other top-level key. | Claude (all surfaces), Codex, Cursor, Gemini CLI, Copilot, Windsurf, ~70 agents |
| Claude Code extras | [Claude Code skills](https://code.claude.com/docs/en/skills) | Superset: `argument-hint`, `disable-model-invocation`, `context`, `agent`, … plus `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_DATA}`. claude.ai uploads and the Skills API **reject** these extra keys. | Claude Code only |
| Install by name | [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugins/marketplace-reference.md) | `.claude-plugin/marketplace.json` at repo root: `name`, `owner`, `plugins[]`. An entry with `"source": "./"`, `"strict": false`, `"skills": [...]` turns existing folders into a plugin with **no file moves** — exactly how `anthropics/skills` ships. Validate with `claude plugin validate .` | `/plugin marketplace add owner/repo` → `/plugin install x@market` |
| Cross-agent installer | [`npx skills`](https://vercel.com/blog/introducing-skills) / skills.sh | Scans `skills/`, `.claude/skills/`, … **and reads paths declared in `.claude-plugin/marketplace.json`**. | `npx skills add owner/repo -s name` |
| claude.ai / Desktop | Upload a `.zip` of the skill folder | Only spec keys in frontmatter. | Settings → Capabilities → Upload skill |
| Official directory | [Anthropic directory](https://claude.com/docs/plugins/pre-submission-checklist) (claude.ai/directory/manage) | One plugin per submission; folder with `.claude-plugin/plugin.json`, README ≥ 40 words, LICENSE, `description`/`author`/`version`, no files outside the plugin folder, no `.DS_Store`, files < 256 KiB, distinctive name. Reaches claude.ai, Cowork and Claude Code (synced). | Paid plan to submit |
| Community indexes | SkillsMP, claudemarketplaces.com, skills.sh, awesome-lists (ComposioHQ/awesome-claude-skills, VoltAgent/awesome-agent-skills, hesreallyhim/awesome-claude-code) | Mostly crawl GitHub for `SKILL.md` + `marketplace.json` ("Marketplace Ready" badge); awesome-lists take PRs. | Discovery |

## 2. Where the repo stands

Already good: every skill has a valid `name` matching its folder, descriptions ≤ 1024, frontmatter
validated in CI, a generated catalog, MIT license.

Gaps:

1. **No `marketplace.json`** — nobody can `/plugin install` or `npx skills add` by name; install is `git clone && cp -r`.
2. **Desktop skills aren't strictly spec-valid**: `metadata.side_effects` is a YAML boolean; the spec says metadata values are strings (risk on claude.ai upload / `skills-ref`).
3. **No `license` / `author` / `version`** in skill frontmatter or package metadata — directory and indexes show these.
4. **Zips are hand-made** for claude.ai; no release artifacts.
5. **Name clash**: `remarkable-memory` exists in both `code/` and `desktop/` — fine across two plugins, impossible inside one.
6. **Install-path assumptions**: 48 skills read/write `~/.claude/skills/<name>/preferences.md`; `audit-skills` reads `~/.claude/skills/SKILLS_GUIDE.md`. Still works after a plugin install (it's just a user-data path), but it's not where a plugin lives. Long-term fix is `${CLAUDE_PLUGIN_DATA}` with fallback — **out of scope for this PR** (behavior change for existing users).
7. **CI doesn't validate packaging** (no `claude plugin validate`, no spec check).

## 3. Proposal (one PR, no skill moved or renamed)

Keeps `code/` and `desktop/` exactly where they are, so `skills.json`, mostafa.xyz, links and hooks keep working.

1. **`.claude-plugin/marketplace.json`, generated** by `scripts/build_catalog.py` from frontmatter (same single-source rule as the README and `skills.json`; `make check` fails if stale). Plugins grouped as bundles (see decision A), each `source: "./"`, `strict: false`, `skills: [...]`, with `description`, `author`, `license`, `homepage`, `keywords`, `category`.
2. **Frontmatter normalization** (mechanical): add `license: MIT` to every skill; make all `metadata` values strings (`side_effects: "true"`), add `metadata.author`. Update `build_catalog.py` / `check_frontmatter.py` accordingly.
3. **Two validation profiles in `check_frontmatter.py`**:
   - `desktop/` = **portable**: only spec keys, string metadata, `compatibility` ≤ 500 → guaranteed to upload to claude.ai and pass `skills-ref`.
   - `code/` = **Claude Code**: spec core + known Claude Code keys only (catches typos, which Claude Code silently ignores).
4. **`make dist`** builds `dist/<name>.zip` per skill (correct `name/SKILL.md` layout, excludes `.DS_Store`, `evals/`, `preferences.md`). A **release workflow** on tag `v*` attaches the zips to the GitHub Release — one-click claude.ai install.
5. **CI**: add `claude plugin validate .` (pinned `@anthropic-ai/claude-code` version) next to `make check`.
6. **README install section** rewritten with the four routes:
   ```
   # Claude Code
   /plugin marketplace add mostafa-drz/claude-skills
   /plugin install dev-workflow@mostafa-skills
   # Any agent (Codex, Cursor, Gemini CLI, …)
   npx skills add mostafa-drz/claude-skills -s whats-next
   # claude.ai / Desktop: download <name>.zip from Releases → Settings → Capabilities → Upload
   # Manual: cp -r code/whats-next ~/.claude/skills/
   ```
7. **Version**: `metadata.version` on the marketplace; plugin entries omit `version` so Claude Code tracks the commit SHA (every push is an update, no bump discipline needed).

### Follow-ups (not in this PR)

- **Anthropic directory**: needs a real `plugins/<name>/.claude-plugin/plugin.json` folder per submission and a paid account — do it for 1–2 flagship bundles once the marketplace is proven.
- PRs to the awesome-lists + skills.sh badge in README.
- Move preference storage to `${CLAUDE_PLUGIN_DATA}` with a fallback to the current path.

## 4. Decisions

- **A. Plugin grouping:** 7 themed bundles: `git-and-prs`, `dev-workflow`, `qa-and-audits`,
  `comms-and-tickets`, `personal-and-research`, `skill-authoring`, `everyday-assistant`
  (the desktop skills). Each skill names its bundle in `metadata.bundle`.
- **B. Marketplace name:** `mostafa-skills`. This is permanent.

## 5. Verified while implementing

- `claude plugin validate .` passes (CLI 2.1.296 and 2.1.310).
- In an isolated `$HOME`: `claude plugin marketplace add` + `install` for three bundles; `claude plugin details everyday-assistant` lists all 11 skills.
- `npx skills@1.5.22 add . --list` finds 59 skills grouped by bundle. The two `remarkable-memory` skills share a name, so it lists one.
- `skills-ref validate` passes for all 11 desktop skills. On `main`, `day-timeline` failed it (`argument-hint`), which means its claude.ai upload would have been rejected. Fixed.
- `make dist` builds byte-identical zips on repeated runs.
