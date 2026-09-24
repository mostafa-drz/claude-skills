#!/usr/bin/env python3
"""Validate focus.json before it is rendered.

Usage:  python3 scripts/validate_focus.py focus.json

Standard library only. Exits 1 on any error, 0 otherwise; warnings never fail the run.
Every message names the field and the fix, so the agent can correct the data and re-run.

The limits are the skill. A focus that needs two sentences is two things; a "how" with
seven steps is a project plan; a first step longer than 25 minutes is the procrastination
the skill exists to break. And a reason can only cite a source that was actually read,
so an evidence line can never be invented to make the pick sound better.
"""
import json
import re
import sys
from pathlib import Path

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
OUTCOMES = ("done", "partial", "not_done", "unknown")
LIMITS = {"focus": 90, "why": 320, "done_when": 160, "good_enough": 160}


def text(value):
    return value.strip() if isinstance(value, str) else ""


def main(path):
    errors, warnings = [], []
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {path}: {exc}")
        return 1
    if not isinstance(doc, dict):
        print("ERROR: focus.json must be a JSON object")
        return 1

    if not DATE_RE.match(text(doc.get("date"))):
        errors.append("date: required, as YYYY-MM-DD (today's date in the user's timezone)")

    for field, cap in LIMITS.items():
        value = text(doc.get(field))
        if not value:
            errors.append(f"{field}: required and non-empty")
        elif len(value) > cap:
            errors.append(f"{field}: {len(value)} chars, cap is {cap}. Cut it; if it won't fit, it's more than one thing")

    focus = text(doc.get("focus"))
    if focus and re.search(r"\band then\b|;", focus):
        warnings.append("focus: reads like two things joined together. Pick one")

    checked = doc.get("sources_checked")
    if not isinstance(checked, list) or not all(text(s) for s in checked):
        errors.append("sources_checked: required list of the sources actually read this run (may be empty only if none exist)")
        checked = []
    checked = {text(s) for s in checked}

    evidence = doc.get("evidence")
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 4:
        errors.append("evidence: 1-4 items, each {source, fact}. The why must rest on something you read")
        evidence = []
    for i, e in enumerate(evidence):
        where = f"evidence[{i}]"
        if not isinstance(e, dict) or not text(e.get("source")) or not text(e.get("fact")):
            errors.append(f"{where}: needs a non-empty source and fact")
            continue
        if text(e["source"]) not in checked and text(e["source"]) not in ("You", "Memory", "Past chats"):
            errors.append(
                f"{where}: source '{e['source']}' is not in sources_checked. Cite only what you read; "
                "use 'You' for something the user said in this chat"
            )

    how = doc.get("how")
    if not isinstance(how, list) or not 1 <= len(how) <= 3:
        errors.append("how: 1-3 steps. More than three is a plan, not a focus")
        how = []
    for i, s in enumerate(how):
        where = f"how[{i}]"
        if not isinstance(s, dict) or not text(s.get("step")):
            errors.append(f"{where}: needs a non-empty step")
            continue
        if len(text(s["step"])) > 140:
            errors.append(f"{where}: step over 140 chars. One concrete action, not a paragraph")
        minutes = s.get("minutes")
        if minutes is not None and (not isinstance(minutes, int) or minutes <= 0):
            errors.append(f"{where}: minutes must be a positive whole number, or omitted")
        if i == 0:
            if minutes is None:
                errors.append("how[0]: the first step needs minutes. Starting is the point, so size it")
            elif isinstance(minutes, int) and minutes > 25:
                errors.append(f"how[0]: first step is {minutes} min, cap is 25. Make the start smaller")

    not_today = doc.get("not_today", [])
    if not isinstance(not_today, list) or len(not_today) > 3 or not all(text(t) for t in not_today):
        errors.append("not_today: optional list of at most 3 non-empty lines")

    missing = doc.get("sources_missing", [])
    if not isinstance(missing, list) or not all(text(t) for t in missing):
        errors.append("sources_missing: optional list of non-empty lines")

    y = doc.get("yesterday")
    if y is not None:
        if not isinstance(y, dict) or not text(y.get("focus")):
            errors.append("yesterday: when present, needs a focus")
        elif y.get("outcome") not in OUTCOMES:
            errors.append(f"yesterday.outcome: one of {', '.join(OUTCOMES)}. Use unknown unless the user said")

    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        print(f"{len(errors)} error(s). Fix focus.json and re-run.")
        return 1
    print(f"focus.json OK ({len(how)} step(s), {len(evidence)} evidence line(s)).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_focus.py focus.json")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
