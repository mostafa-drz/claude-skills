#!/usr/bin/env python3
"""Validate timeline.json before it is rendered.

Usage:  python3 scripts/validate_timeline.py timeline.json [--repo PATH]

Standard library only. Exits 1 on any error, 0 otherwise; warnings never fail the run.
Every message names the item and the fix, so the agent can correct the data and re-run.

What it guards, and why:
- Every change carries evidence. An item with no commit is a claim nobody can check, so it
  is rejected. With --repo, every SHA must resolve to a real commit in that repository, and
  a subject that disagrees with the commit is reported: a hallucinated or mistyped SHA is
  the one error this skill must never ship.
- A "why" is either backed or labelled. If no PR, commit body or review states the reason,
  the item must say why_inferred: true, and the page shows it as Claude's reading.
- Links are https only, and the commit link template contains {sha}, so nothing in the
  page can point at a javascript: or data: URL.
- References resolve: an item's area and chapter must exist, so lanes and chapters never
  silently drop a change.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TYPES = ("feat", "fix", "refactor", "perf", "security", "docs", "test", "chore", "revert")
VIEWS = ("timeline", "lanes", "chapters", "walkthrough")
EVIDENCE = ("pr-body", "commit-message", "review", "issue", "diff", "changelog", "discussion")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
URL_RE = re.compile(r"^https://[^\s\"'<>]+$")


def s(v):
    return v.strip() if isinstance(v, str) else ""


def main(argv):
    if not argv or argv[0].startswith("-"):
        print("Usage: python3 scripts/validate_timeline.py timeline.json [--repo PATH]")
        return 2
    repo = argv[argv.index("--repo") + 1] if "--repo" in argv else None
    try:
        d = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read {argv[0]}: {e}")
        return 1
    errs, warns = [], []
    E, W = errs.append, warns.append

    if not s(d.get("title")):
        E("title: missing. One line naming what the range is about, not 'Timeline'.")
    if d.get("view", "timeline") not in VIEWS:
        E(f"view: '{d.get('view')}' is not one of {', '.join(VIEWS)}")
    if d.get("order", "newest") not in ("newest", "oldest"):
        E("order: use 'newest' or 'oldest'")
    th = d.get("theme") or {}
    if th.get("mode", "dark") not in ("dark", "light", "system"):
        E("theme.mode: use dark, light or system")
    if th.get("density", "compact") not in ("compact", "comfortable"):
        E("theme.density: use compact or comfortable")
    if "accent" in th and not HEX_RE.match(str(th["accent"])):
        E("theme.accent: must be a 6-digit hex like #ff6b3d")

    rp = d.get("repo") or {}
    cu = rp.get("commit_url")
    if cu is not None and (not URL_RE.match(str(cu)) or "{sha}" not in str(cu)):
        E("repo.commit_url: must be an https URL containing {sha}, e.g. https://github.com/o/r/commit/{sha}")
    if rp.get("url") is not None and not URL_RE.match(str(rp["url"])):
        E("repo.url: must be https")
    if not cu:
        W("repo.commit_url: missing, so SHAs render as plain text instead of links")

    areas = {a.get("key") for a in d.get("areas") or [] if isinstance(a, dict)}
    for a in d.get("areas") or []:
        if not s(a.get("key")) or not s(a.get("label")):
            E(f"areas: every area needs key and label (got {a!r})")
    chapters = {c.get("key") for c in d.get("chapters") or [] if isinstance(c, dict)}
    for c in d.get("chapters") or []:
        if not s(c.get("key")) or not s(c.get("title")):
            E(f"chapters: every chapter needs key and title (got {c!r})")
        if c.get("date") and not DATE_RE.match(str(c["date"])):
            E(f"chapters[{c.get('key')}].date: use YYYY-MM-DD")

    items = d.get("items")
    if not isinstance(items, list) or not items:
        E("items: empty. A timeline needs at least one change.")
        items = []
    seen, sha_owner, shas = set(), {}, []
    for i, it in enumerate(items):
        at = f"items[{i}]" + (f" ({it.get('id')})" if isinstance(it, dict) and it.get("id") else "")
        if not isinstance(it, dict):
            E(f"{at}: must be an object")
            continue
        iid = s(it.get("id"))
        if not ID_RE.match(iid):
            E(f"{at}.id: kebab-case required, e.g. 'session-cookies'")
        elif iid in seen:
            E(f"{at}.id: duplicate '{iid}'")
        seen.add(iid)
        title = s(it.get("title"))
        if not title:
            E(f"{at}.title: missing")
        elif len(title) > 90:
            W(f"{at}.title: {len(title)} chars; keep it under 90 so it reads as a headline")
        if it.get("type") not in TYPES:
            E(f"{at}.type: '{it.get('type')}' is not one of {', '.join(TYPES)}")
        if not DATE_RE.match(str(it.get("date", ""))):
            E(f"{at}.date: use YYYY-MM-DD (the date the change landed)")
        if not s(it.get("what")):
            E(f"{at}.what: missing. One or two sentences on what changed, in plain words.")
        if it.get("area") and areas and it["area"] not in areas:
            E(f"{at}.area: '{it['area']}' is not in areas; add it or fix the key")
        if it.get("chapter") and it["chapter"] not in chapters:
            E(f"{at}.chapter: '{it['chapter']}' is not in chapters")
        if it.get("impact") not in (None, "breaking", "notable", "minor"):
            E(f"{at}.impact: use breaking, notable or minor")

        commits = it.get("commits") or []
        if not commits:
            E(f"{at}.commits: empty. Every change must cite at least one commit SHA.")
        for c in commits:
            sha = s(c.get("sha") if isinstance(c, dict) else "").lower()
            if not SHA_RE.match(sha):
                E(f"{at}.commits: '{sha}' is not a hex SHA (7-40 chars)")
                continue
            if len(sha) < 40:
                W(f"{at}.commits: {sha} is abbreviated; prefer the full 40-char SHA so links never go ambiguous")
            if sha in sha_owner and sha_owner[sha] != iid:
                W(f"{at}.commits: {sha[:7]} is also cited by '{sha_owner[sha]}'; one commit usually belongs to one change")
            sha_owner[sha] = iid
            shas.append((at, sha, s(c.get("subject"))))
        for p in it.get("prs") or []:
            if not isinstance(p, dict) or not isinstance(p.get("number"), int):
                E(f"{at}.prs: each PR needs an integer number")
                continue
            if p.get("url") is not None and not URL_RE.match(str(p["url"])):
                E(f"{at}.prs #{p['number']}.url: must be https")
            if not p.get("url"):
                W(f"{at}.prs #{p['number']}: no url, so it renders without a link")

        ev = it.get("evidence") or []
        for e in ev:
            if not isinstance(e, dict) or not s(e.get("text")) or not s(e.get("source")):
                E(f"{at}.evidence: each entry needs text (a short quote) and source (e.g. 'PR #142')")
                continue
            if e.get("kind") not in EVIDENCE:
                E(f"{at}.evidence: kind '{e.get('kind')}' is not one of {', '.join(EVIDENCE)}")
            if e.get("url") is not None and not URL_RE.match(str(e["url"])):
                E(f"{at}.evidence.url: must be https")
            if len(s(e.get("text"))) > 400:
                W(f"{at}.evidence: a quote over 400 chars; trim to the sentence that proves the point")
        if s(it.get("why")) and not it.get("why_inferred") and not ev:
            E(f"{at}.why: no evidence states this reason. Add an evidence quote, or set why_inferred: true.")
        if "why" not in it:
            W(f"{at}.why: missing. Quote the stated reason, infer one with why_inferred: true, "
              "or set why: null so the page says no source states it.")
        rv = it.get("review")
        if rv is not None:
            if not isinstance(rv, dict) or not isinstance(rv.get("check", []), list):
                E(f"{at}.review: must be {{risk?: str, check?: [str]}}")
        elif d.get("view") == "walkthrough":
            W(f"{at}.review: the walkthrough is a review; give each step a risk or something to check")
        if it.get("step") is not None and not isinstance(it.get("step"), int):
            E(f"{at}.step: must be an integer")

    if repo and shas:
        for at, sha, subject in shas:
            p = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%s", f"{sha}^{{commit}}", "--"],
                               capture_output=True, text=True)
            if p.returncode != 0:
                E(f"{at}: {sha[:12]} does not exist in {repo}. Never cite a SHA you did not read from git.")
            elif subject and p.stdout.strip() != subject:
                W(f"{at}: {sha[:7]} subject is '{p.stdout.strip()}', not '{subject}'")
    elif not repo:
        W("SHAs not verified against a repository; run with --repo PATH")

    for w in warns:
        print("warning:", w)
    for e in errs:
        print("ERROR:", e)
    n = len(items)
    print(f"{'FAILED' if errs else 'OK'}: {n} changes, {len(shas)} commit citations, "
          f"{len(errs)} errors, {len(warns)} warnings")
    return 1 if errs else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
