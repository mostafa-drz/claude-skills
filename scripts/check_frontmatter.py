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
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_catalog import frontmatter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^(?!-)(?!.*--)[a-z0-9-]{1,64}(?<!-)$")
WRITES = ("Write", "Edit", "NotebookEdit")
WRITE_BASH = re.compile(r"Bash\((rm|mv|cp|git|mkdir|tee|curl|npm|pip)\b")

def main() -> int:
    problems = []
    for platform in ("code", "desktop"):
        for md in sorted((ROOT / platform).glob("*/SKILL.md")):
            rel, d = md.relative_to(ROOT), md.parent.name
            raw = md.read_text()
            if not raw.startswith("---\n"):
                problems.append(f"{rel}: frontmatter must start on line 1")
                continue
            fm = frontmatter(md)
            desc = fm.get("description", "").strip()
            if not desc:
                problems.append(f"{rel}: no description — Claude cannot match this skill")
            elif len(desc) > 1024:
                problems.append(f"{rel}: description {len(desc)} chars, hard cap is 1024")
            name = fm.get("name", "").strip()
            if name and name != d:
                problems.append(f"{rel}: name '{name}' != directory '{d}'")
            if name and not NAME_RE.match(name):
                problems.append(f"{rel}: name '{name}' breaks the spec charset")
            tools = fm.get("allowed-tools", "")
            body_writes = any(t in tools for t in WRITES) or WRITE_BASH.search(tools)
            if body_writes and fm.get("disable-model-invocation", "").lower() not in ("true", "yes", "on", "1"):
                problems.append(f"{rel}: can write but no disable-model-invocation: true")
    if problems:
        print(f"{len(problems)} frontmatter problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("frontmatter OK across all skills")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
