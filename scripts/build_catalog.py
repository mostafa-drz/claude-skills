#!/usr/bin/env python3
"""Generate the README catalog and skills.json from each SKILL.md frontmatter.

`skills.json` is a PUBLISHED API: mostafa.xyz/lab/claude-skills renders from it.
It is generated, not hand-maintained — before that, 68% of its descriptions had
drifted from their frontmatter and it advertised a Linear-writing skill as having
no side effects, both of which the site was showing.

The frontmatter is the only thing Claude actually reads, so it is the only
source of truth. Every other copy of a skill's description drifted: before this
script existed, 68% of the entries in the old hand-maintained skills.json no
longer matched their frontmatter, and one advertised a Linear-writing skill as
having no side effects.

    python3 scripts/build_catalog.py          # rewrite README table + skills.json
    python3 scripts/build_catalog.py --check  # fail if either would change (CI)
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = "<!-- BEGIN GENERATED CATALOG -->"
END = "<!-- END GENERATED CATALOG -->"


def frontmatter(path: Path) -> dict:
    """Parse just enough YAML for our fields. Avoids a PyYAML dependency so the
    check runs anywhere, and tolerates the block scalars (`>-`) used throughout."""
    text = path.read_text()
    if not text.startswith("---\n"):
        return {}
    body = text.split("---\n", 2)[1]
    out, key, buf = {}, None, []

    def flush():
        if key:
            out[key] = " ".join(w.strip() for w in buf).strip()

    for line in body.split("\n"):
        m = re.match(r"^([a-zA-Z][\w-]*):\s*(.*)$", line)
        if m:
            flush()
            key, rest = m.group(1), m.group(2).strip()
            buf = [] if rest in (">-", "|", ">", "|-", "") else [rest]
        elif key and (line.startswith("  ") or line.startswith("\t")):
            buf.append(line)
        elif line.strip() == "":
            continue
        else:
            flush()
            key, buf = None, []
    flush()
    return {k: v.strip().strip('"').strip("'") for k, v in out.items()}


def skills():
    for platform in ("code", "desktop"):
        for skill_md in sorted((ROOT / platform).glob("*/SKILL.md")):
            d = skill_md.parent
            fm = frontmatter(skill_md)
            desc = re.sub(r"\s+", " ", fm.get("description", "")).strip()
            # The catalog is an index, not a spec — one sentence is the right size.
            first = re.split(r"(?<=[.!?])\s+", desc)[0] if desc else "_(no description)_"
            meta = fm_block_metadata(skill_md)
            yield {
                "name": d.name,
                "platform": platform,
                "path": f"{platform}/{d.name}/SKILL.md",
                "summary": first,
                "icon": (d / "icon.svg").exists(),
                # Derived, never hand-set: the frontmatter already states it.
                "side_effects": side_effects(platform, fm, meta),
                "description": desc,
                "trigger": meta.get("trigger", ""),
                "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
            }


TRUE = ("true", "yes", "on", "1")


def side_effects(platform: str, fm: dict, meta: dict) -> bool:
    """`disable-model-invocation` is a Claude Code field; Desktop skills don't have it,
    and declare no allowed-tools either, so nothing about them is derivable. Publishing
    a Desktop skill that writes files as read-only is the failure this guards."""
    if platform == "desktop":
        return str(meta.get("side_effects", "")).lower() in TRUE
    return str(fm.get("disable-model-invocation", "")).lower() in TRUE


def fm_block_metadata(path: Path) -> dict:
    """Read the nested `metadata:` map. Curated per-skill data that cannot be derived
    lives here — the two fields the published manifest needs and nothing else knows."""
    text = path.read_text()
    if not text.startswith("---\n"):
        return {}
    fm = text.split("---\n", 2)[1]
    m = re.search(r"^metadata:\n((?:[ \t]+.*\n?)*)", fm, re.M)
    if not m:
        return {}
    out = {}
    for line in m.group(1).split("\n"):
        kv = re.match(r"^\s+([\w-]+):\s*(.*)$", line)
        if kv:
            v = kv.group(2).strip()
            if v.startswith('"') and v.endswith('"'):
                v = json.loads(v)
            out[kv.group(1)] = v
    return out


REPO = "https://github.com/mostafa-drz/claude-skills"


def manifest(rows):
    """The published catalog consumed by mostafa.xyz. Field shape is deliberately
    unchanged from the hand-maintained version so the site keeps rendering."""
    out = []
    for s in rows:
        e = {
            "name": s["name"],
            "platform": s["platform"],
            "description": s["description"],
            "trigger": s["trigger"],
            "tags": s["tags"],
        }
        if s["icon"]:
            e["icon"] = (
                "https://raw.githubusercontent.com/mostafa-drz/claude-skills/main/"
                f'{s["platform"]}/{s["name"]}/icon.svg'
            )
        e["url"] = f'{REPO}/blob/main/{s["path"]}'
        e["sideEffects"] = s["side_effects"]
        out.append(e)
    return {"updated": date.today().isoformat(), "repo": REPO, "skills": out}


def table(rows):
    out = ["| Skill | What it does | Side effects |", "|---|---|---|"]
    for s in rows:
        icon = (
            f'<img src="{s["platform"]}/{s["name"]}/icon.svg" width="20" height="20" '
            f'alt="" valign="middle"> &nbsp; '
            if s["icon"] else ""
        )
        out.append(
            f'| {icon}[`/{s["name"]}`]({s["path"]}) | {s["summary"]} | '
            f'{"Yes" if s["side_effects"] else "No"} |'
        )
    return "\n".join(out)


def render():
    rows = list(skills())
    code = [s for s in rows if s["platform"] == "code"]
    desktop = [s for s in rows if s["platform"] == "desktop"]
    parts = [
        START,
        "<!-- Generated by scripts/build_catalog.py from each SKILL.md frontmatter.",
        "     Do not edit by hand: run `make catalog`. -->",
        "",
        f"### Claude Code ({len(code)})",
        "",
        table(code),
        "",
        f"### Claude Desktop ({len(desktop)})",
        "",
        table(desktop),
        "",
        END,
    ]
    return "\n".join(parts)


def main():
    check = "--check" in sys.argv
    rows = list(skills())

    mf = ROOT / "skills.json"
    built = manifest(rows)
    have_raw = mf.read_text() if mf.exists() else ""
    # Regenerating on a later day must not produce a date-only diff, or every run
    # creates churn that means nothing and `--check` has to ignore the field to cope.
    try:
        prev = json.loads(have_raw)
        if prev.get("skills") == built["skills"] and prev.get("repo") == built["repo"]:
            built["updated"] = prev.get("updated", built["updated"])
    except (ValueError, AttributeError):
        pass
    want = json.dumps(built, indent=2, ensure_ascii=False) + "\n"
    if check:
        if have_raw != want:
            sys.exit("skills.json is out of date — run `make catalog`.")
    else:
        mf.write_text(want)

    readme = ROOT / "README.md"
    text = readme.read_text()
    if START not in text or END not in text:
        sys.exit(f"README.md is missing the {START} / {END} markers.")
    new = text[: text.index(START)] + render() + text[text.index(END) + len(END):]
    if check:
        if new != text:
            sys.exit("README catalog is out of date — run `make catalog`.")
        print(f"catalog + manifest up to date ({len(rows)} skills)")
        return
    readme.write_text(new)
    print(f"catalog + manifest written ({len(rows)} skills)")


if __name__ == "__main__":
    main()
