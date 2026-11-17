#!/usr/bin/env python3
"""Fail on SKILL.md frontmatter that Claude Code would silently mis-load.

Claude Code fails soft here: malformed YAML loads the body with empty metadata,
so `/skill-name` keeps working while automatic invocation quietly stops. Nothing
surfaces the breakage, which is why it is checked here instead.

Rules enforced (sources in SKILLS_GUIDE.md):
  - frontmatter must open on line 1, or the whole file is treated as content
  - `description` must exist and be <= 1024 chars (hard cap: portable spec,
    Skills API and claude.ai uploads reject longer, they do not truncate)
  - `name`, when set, must match the directory and the spec's charset
  - a skill that can write must declare `disable-model-invocation: true`
  - every key is known: desktop/ skills may use only the six portable spec keys
    (claude.ai uploads and the Skills API reject anything else); code/ skills may
    also use Claude Code's keys. Claude Code ignores an unknown key without a word,
    so a typo like `disable-model-invokation` would otherwise ship unnoticed
  - `metadata` values are strings, as the Agent Skills spec requires
  - `compatibility`, when set, is <= 500 chars
  - no skill reaches a file it ships through `~/.claude/skills/<skill>/…`: a plugin
    install lives elsewhere, so that path only works for a manual copy. Bundled files
    resolve from `${CLAUDE_SKILL_DIR}`; `~/.claude/skills/` is for user data only
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit(
        "PyYAML is required: a regex parser cannot tell valid YAML from invalid,\n"
        "and invalid frontmatter is exactly what this check exists to catch.\n"
        "Install it with: pip install pyyaml"
    )

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^(?!-)(?!.*--)[a-z0-9-]{1,64}(?<!-)$")
WRITES = ("Write", "Edit", "NotebookEdit")
WRITE_BASH = re.compile(r"Bash\((rm|mv|cp|git|mkdir|tee|curl|npm|pip)\b")
# https://agentskills.io/specification — the only keys that survive packaging.
PORTABLE = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
# https://code.claude.com/docs/en/skills — the Claude Code superset.
CLAUDE_CODE = PORTABLE | {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
    "background", "hooks", "paths", "shell",
}
ALLOWED = {"code": CLAUDE_CODE, "desktop": PORTABLE}
# Files a skill writes for the user. These belong under ~/.claude/skills/, where a
# plugin update can't overwrite them, even when the repo ships an empty starter copy.
USER_DATA = {"preferences.md", "learnings.md", "feedback-journal.md", "tone-profile.md"}
# Folders whose files are user settings seeded from a shipped starter copy.
USER_DATA_DIRS = ("reference/platforms/",)
HOME_SKILL_PATH = re.compile(r"~/\.claude/skills/([a-z0-9-]+)/([A-Za-z0-9_./-]+)")


def shipped_via_home(platform: str, text: str) -> list:
    """Paths written as ~/.claude/skills/<skill>/<file> where that file ships in the repo."""
    hits = []
    for skill, rest in HOME_SKILL_PATH.findall(text):
        rest = rest.rstrip(".")
        if (rest and Path(rest).name not in USER_DATA and not rest.startswith(USER_DATA_DIRS)
                and (ROOT / platform / skill / rest).exists()):
            hits.append(f"~/.claude/skills/{skill}/{rest}")
    return hits

def main() -> int:
    problems = []
    for platform in ("code", "desktop"):
        for md in sorted((ROOT / platform).glob("*/SKILL.md")):
            rel, d = md.relative_to(ROOT), md.parent.name
            raw = md.read_text()
            if not raw.startswith("---\n"):
                problems.append(f"{rel}: frontmatter must start on line 1")
                continue
            try:
                parsed = yaml.safe_load(raw.split("---\n", 2)[1])
            except yaml.YAMLError as exc:
                # Claude Code fails soft here: the body loads with empty metadata, so
                # the skill answers /name while never auto-matching again.
                first = str(exc).split("\n")[0]
                problems.append(f"{rel}: frontmatter is not valid YAML — {first}")
                continue
            if not isinstance(parsed, dict):
                problems.append(f"{rel}: frontmatter is not a YAML mapping")
                continue
            fm = {k: ("" if v is None else v) for k, v in parsed.items()}
            desc = str(fm.get("description", "")).strip()
            if not desc:
                problems.append(f"{rel}: no description — Claude cannot match this skill")
            elif len(desc) > 1024:
                problems.append(f"{rel}: description {len(desc)} chars, hard cap is 1024")
            name = str(fm.get("name", "")).strip()
            if name and name != d:
                problems.append(f"{rel}: name '{name}' != directory '{d}'")
            if name and not NAME_RE.match(name):
                problems.append(f"{rel}: name '{name}' breaks the spec charset")
            tools = str(fm.get("allowed-tools", ""))
            body_writes = any(t in tools for t in WRITES) or WRITE_BASH.search(tools)
            if body_writes and str(fm.get("disable-model-invocation", "")).lower() not in ("true", "yes", "on", "1"):
                problems.append(f"{rel}: can write but no disable-model-invocation: true")
            unknown = sorted(set(fm) - ALLOWED[platform])
            if unknown:
                why = ("not portable — claude.ai and the Skills API reject it"
                       if platform == "desktop" else "not a Claude Code skill field")
                problems.append(f"{rel}: unknown key(s) {', '.join(unknown)} — {why}")
            compat = str(fm.get("compatibility", ""))
            if len(compat) > 500:
                problems.append(f"{rel}: compatibility {len(compat)} chars, cap is 500")
            meta = fm.get("metadata") or {}
            if not isinstance(meta, dict):
                problems.append(f"{rel}: metadata must be a mapping")
                meta = {}
            for k, v in meta.items():
                if not isinstance(v, str):
                    problems.append(
                        f"{rel}: metadata.{k} is {type(v).__name__}, the spec requires a "
                        f'string — quote it, e.g. {k}: "{str(v).lower()}"'
                    )
            for hit in shipped_via_home(platform, raw):
                problems.append(
                    f"{rel}: {hit} is a bundled file — use ${{CLAUDE_SKILL_DIR}}/… "
                    "(plugin installs don't live in ~/.claude/skills)"
                )
            if platform == "desktop" and "side_effects" not in meta:
                problems.append(
                    f"{rel}: desktop skills must declare metadata.side_effects — "
                    "disable-model-invocation is Code-only, so it cannot be derived"
                )
    if problems:
        print(f"{len(problems)} frontmatter problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("frontmatter OK across all skills")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
