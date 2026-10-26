#!/usr/bin/env python3
"""Collect the raw evidence for a change timeline from git: commits, diff stats, PR numbers, tags.

Usage:
  python3 scripts/collect.py [--repo PATH] [--range BASE..HEAD | --since WHEN [--until WHEN]]
                             [--branch REF] [--path DIR ...] [--max N] > raw.json

Standard library only, read-only: it runs `git log`, `git rev-list`, `git tag` and `git remote`,
nothing that writes. PR *details* (bodies, reviews, linked issues) are not fetched here; the
skill reads them with `gh` or the GitHub connector, because those need auth this script
should not hold.

What it gives the agent, and why:
- Every commit with its full SHA, author date, subject, body and per-file numstat, so each
  timeline item can cite exactly the commits it is built from.
- PR numbers found three ways: squash subjects "(#123)", merge subjects "Merge pull request
  #123", and, for merge commits, every commit the merge brought in (M^1..M^2). A commit that
  belongs to a PR is attributed to it even when its own subject does not say so.
- Tags inside the range with their dates, which become release chapters.
- A suggested set of areas from the paths touched, which become swimlanes. A suggestion
  only: the agent renames or merges them.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date

RS, US = "\x1e", "\x1f"
PR_SQUASH = re.compile(r"\(#(\d+)\)\s*$")
PR_MERGE = re.compile(r"^Merge pull request #(\d+)\b")
PR_ANY = re.compile(r"(?:^|[\s(])#(\d+)\b")
# Directories that hold code rather than name an area; the area is the segment below them.
CONTAINERS = {"src", "lib", "app", "apps", "packages", "pkg", "services", "libs", "modules",
              "internal", "cmd", "code", "desktop", "components", "crates"}


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def remote(repo):
    url = git(repo, "remote", "get-url", "origin", check=False).strip()
    m = re.match(r"^(?:git@|ssh://git@|https://)([^/:]+)[/:]([^/]+)/(.+?)(?:\.git)?/?$", url)
    if not m:
        return {"name": None, "url": None, "commit_url": None}
    host, owner, name = m.groups()
    web = f"https://{host}/{owner}/{name}"
    if "gitlab" in host:
        commit = web + "/-/commit/{sha}"
    elif "bitbucket" in host:
        commit = web + "/commits/{sha}"
    else:
        commit = web + "/commit/{sha}"
    return {"name": f"{owner}/{name}", "url": web, "host": host, "commit_url": commit}


def area_of(path):
    parts = path.split("/")
    if len(parts) == 1:
        return "root"
    if parts[0] in CONTAINERS and len(parts) > 2:
        return f"{parts[0]}/{parts[1]}"
    return parts[0]


def log(repo, rev_args, paths, merges):
    fmt = RS + US.join(["%H", "%P", "%aI", "%an", "%s", "%b"]) + US
    args = ["log", f"--format={fmt}", "--numstat", "--no-renames"]
    args += ["--merges"] if merges else ["--no-merges"]
    out = git(repo, *args, *rev_args, "--", *paths)
    commits = []
    for chunk in out.split(RS)[1:]:
        fields = chunk.split(US)
        if len(fields) < 7:
            continue
        sha, parents, when, author, subject, body, rest = fields[:7]
        files = []
        for line in rest.strip().splitlines():
            bits = line.split("\t")
            if len(bits) == 3:
                a, d, p = bits
                files.append({"path": p, "additions": int(a) if a.isdigit() else 0,
                              "deletions": int(d) if d.isdigit() else 0, "binary": a == "-"})
        commits.append({"sha": sha, "parents": parents.split(), "date": when, "author": author,
                        "subject": subject, "body": body.strip(), "files": files,
                        "additions": sum(f["additions"] for f in files),
                        "deletions": sum(f["deletions"] for f in files)})
    return commits


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--range", help="BASE..HEAD, e.g. main..feature or v1.2.0..v1.3.0")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--branch", default="HEAD")
    ap.add_argument("--path", action="append", default=[], help="limit to a path; repeatable")
    ap.add_argument("--max", type=int, default=400)
    a = ap.parse_args(argv)

    repo = git(a.repo, "rev-parse", "--show-toplevel").strip()
    if a.range:
        if ".." not in a.range:
            sys.exit("--range must look like BASE..HEAD")
        base, head = a.range.split("..", 1)
        rev = [a.range.replace("...", "..")]
    else:
        base, head = None, a.branch
        rev = [a.branch]
    if a.since:
        rev.append(f"--since={a.since}")
    if a.until:
        rev.append(f"--until={a.until}")
    rev.append(f"--max-count={a.max}")

    commits = log(repo, rev, a.path, merges=False)
    merges = log(repo, rev, a.path, merges=True)
    by_sha = {c["sha"]: c for c in commits}

    # PR attribution: squash "(#N)", merge "Merge pull request #N", then merge ancestry.
    for c in commits:
        prs = []
        m = PR_SQUASH.search(c["subject"]) or PR_MERGE.match(c["subject"])
        if m:
            prs.append(int(m.group(1)))
        c["prs"] = prs
        c["mentions"] = sorted({int(n) for n in PR_ANY.findall(c["subject"] + " " + c["body"])} - set(prs))
    pr_merges = []
    for mc in merges:
        m = PR_MERGE.match(mc["subject"])
        if not m or len(mc["parents"]) < 2:
            continue
        n = int(m.group(1))
        inner = git(repo, "rev-list", f"{mc['parents'][0]}..{mc['parents'][1]}", check=False).split()
        for sha in inner:
            if sha in by_sha and n not in by_sha[sha]["prs"]:
                by_sha[sha]["prs"].append(n)
        pr_merges.append({"number": n, "merge_sha": mc["sha"], "date": mc["date"],
                          "branch": mc["subject"].split(" from ", 1)[-1] if " from " in mc["subject"] else None,
                          "title": mc["body"].splitlines()[0] if mc["body"] else None,
                          "commits": [s for s in inner if s in by_sha]})

    tags = []
    if commits:
        oldest = commits[-1]["sha"]
        out = git(repo, "tag", "--contains", oldest, "--sort=creatordate",
                  "--format=%(refname:short)\t%(creatordate:short)\t%(objectname)", check=False)
        for line in out.splitlines():
            name, when, obj = (line.split("\t") + ["", "", ""])[:3]
            sha = git(repo, "rev-list", "-n", "1", name, check=False).strip()
            tags.append({"name": name, "date": when, "sha": sha})

    areas = Counter()
    for c in commits:
        for f in c["files"]:
            areas[area_of(f["path"])] += f["additions"] + f["deletions"]
    prs = sorted({n for c in commits for n in c["prs"]})

    out = {
        "collected": date.today().isoformat(),
        "repo": remote(repo),
        "range": {"base": base, "head": head, "since": a.since, "until": a.until,
                  "paths": a.path, "truncated": len(commits) >= a.max},
        "stats": {"commits": len(commits), "prs": len(prs),
                  "authors": len({c["author"] for c in commits}),
                  "additions": sum(c["additions"] for c in commits),
                  "deletions": sum(c["deletions"] for c in commits)},
        "prs": prs,
        "pr_merges": pr_merges,
        "tags": tags,
        "suggested_areas": [{"key": k, "churn": v} for k, v in areas.most_common(12)],
        "commits": commits,
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    print()
    if out["range"]["truncated"]:
        print(f"warning: stopped at --max {a.max}; narrow the range or raise --max", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
