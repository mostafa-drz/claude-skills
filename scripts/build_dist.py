#!/usr/bin/env python3
"""Build one uploadable .zip per portable skill, for claude.ai and Claude Desktop.

claude.ai's "Upload skill" wants a zip holding `<name>/SKILL.md`, and rejects any
frontmatter key outside the six-key Agent Skills spec. So only skills whose frontmatter
is portable are zipped — which `check_frontmatter.py` guarantees for every desktop/ skill.
Code skills use Claude Code keys and ship through the plugin marketplace instead.

    python3 scripts/build_dist.py          # write dist/<name>.zip
    python3 scripts/build_dist.py --list   # print what would be zipped

The zips are byte-for-byte reproducible (fixed timestamps, sorted entries), so a
release built twice from one commit produces identical assets.
"""
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_catalog import frontmatter  # noqa: E402  same parser as the catalog
from check_frontmatter import PORTABLE  # noqa: E402  same rule as the check

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
# Per-user runtime state, never part of an installed skill. `evals/` ships: several
# skills point at their worked example there (e.g. evals/example-reco.json) at runtime.
SKIP_DIRS = {"__pycache__", "reports", "sessions"}
SKIP_FILES = {".DS_Store", "Thumbs.db", "preferences.md", "learnings.md",
              "feedback-journal.md", "last-audit.md", "resume-state.md"}
EPOCH = (1980, 1, 1, 0, 0, 0)


def portable_skills():
    for skill_md in sorted(ROOT.glob("*/*/SKILL.md")):
        fm = frontmatter(skill_md)
        if fm and set(fm) <= PORTABLE:
            yield skill_md.parent


def files(skill: Path):
    for f in sorted(skill.rglob("*")):
        rel = f.relative_to(skill)
        if f.is_file() and f.name not in SKIP_FILES and not SKIP_DIRS & set(rel.parts[:-1]):
            yield f, rel


def build(skill: Path) -> Path:
    out = DIST / f"{skill.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f, rel in files(skill):
            info = zipfile.ZipInfo(f"{skill.name}/{rel.as_posix()}", EPOCH)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, f.read_bytes())
    return out


def main():
    skills = list(portable_skills())
    names = [s.name for s in skills]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        sys.exit(f"two portable skills share a name, their zips would collide: {dupes}")
    if "--list" in sys.argv:
        print("\n".join(str(s.relative_to(ROOT)) for s in skills))
        return
    DIST.mkdir(exist_ok=True)
    for old in DIST.glob("*.zip"):
        old.unlink()
    for s in skills:
        out = build(s)
        print(f"{out.relative_to(ROOT)}  ({out.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()
