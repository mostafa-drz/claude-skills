#!/usr/bin/env python3
"""Validate runbook.json before it is rendered.

Usage:
  python3 scripts/validate_runbook.py runbook.json
  python3 scripts/validate_runbook.py runbook.json --previous runbook.prev.json
  python3 scripts/validate_runbook.py runbook.json --previous runbook.prev.json --reworded s4,s9

Standard library only. Exits 1 on any error, 0 otherwise; warnings never fail the run.
Every message names the item and the fix, so the agent can correct the data and re-run.

The checks that matter most are about step ids. A viewer's ticks are saved in their
browser as {id: true}, so an id is the only link between a saved tick and a step: a
reused or renumbered id silently shows the wrong step as done. --previous compares a
republish against the last delivered revision to catch exactly that.
"""
import json
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"^s([1-9][0-9]*)$")
KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ITEM_TYPES = ("step", "wait", "note")


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def text(value):
    return value.strip() if isinstance(value, str) else ""


def id_num(step_id):
    m = ID_RE.match(step_id) if isinstance(step_id, str) else None
    return int(m.group(1)) if m else None


def check_inline(r, where, value):
    if isinstance(value, str) and value.count("`") % 2:
        r.warn(where, "unmatched backtick: the rest of the line would render as code")


def steps_of(doc):
    """(id, position, where) for every step, in document order."""
    out, pos = [], 0
    for pi, phase in enumerate(doc.get("phases") or []):
        if not isinstance(phase, dict):
            continue
        for ii, item in enumerate(phase.get("items") or []):
            if isinstance(item, dict) and item.get("type") == "step":
                out.append((item.get("id"), pos, f"phases[{pi}].items[{ii}]"))
            pos += 1
    return out


def validate(doc, r):
    if not isinstance(doc, dict):
        r.err("runbook", "top level must be a JSON object")
        return
    if doc.get("schema") != 1:
        r.err("schema", "must be 1")
    if not KEY_RE.match(text(doc.get("key"))):
        r.err("key", "must be a lowercase slug like 'acme-email-setup'; set once, never changed")
    if not text(doc.get("title")):
        r.err("title", "missing: give the runbook a 2-5 word name")
    elif len(text(doc["title"]).split()) > 8:
        r.warn("title", "reads like a sentence; use a short name and put the rest in subtitle")
    if not text(doc.get("subtitle")):
        r.warn("subtitle", "missing: one line on the route through the phases helps the reader")
    rev = doc.get("revision")
    if not isinstance(rev, int) or isinstance(rev, bool) or rev < 1:
        r.err("revision", "must be an integer >= 1")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", text(doc.get("generated_on"))):
        r.err("generated_on", "must be an ISO date, YYYY-MM-DD")
    retired = doc.get("retired_ids", [])
    if not isinstance(retired, list) or any(id_num(x) is None for x in retired):
        r.err("retired_ids", "must be a list of step ids like 's7'")
        retired = []
    footer = doc.get("footer", [])
    if not isinstance(footer, list) or not all(isinstance(x, str) for x in footer):
        r.err("footer", "must be a list of strings")

    phases = doc.get("phases")
    if not isinstance(phases, list) or not phases:
        r.err("phases", "must be a non-empty list")
        return
    if not 3 <= len(phases) <= 8:
        r.warn("phases", f"{len(phases)} phases; 3-8 reads best. Merge tiny phases or split a long one")

    for pi, phase in enumerate(phases):
        pw = f"phases[{pi}]"
        if not isinstance(phase, dict):
            r.err(pw, "must be an object")
            continue
        if not text(phase.get("title")):
            r.err(pw, "missing title")
        if not text(phase.get("where")):
            r.err(pw, "missing 'where': the site, app or place this phase happens in")
        items = phase.get("items")
        if not isinstance(items, list) or not items:
            r.err(pw, "items must be a non-empty list")
            continue
        n_steps = 0
        for ii, item in enumerate(items):
            iw = f"{pw}.items[{ii}]"
            kind = item.get("type") if isinstance(item, dict) else None
            if kind not in ITEM_TYPES:
                r.err(iw, f"type must be one of {', '.join(ITEM_TYPES)}")
                continue
            if kind == "step":
                n_steps += 1
                if not text(item.get("action")):
                    r.err(iw, "step has no action: what does the user do?")
                elif len(item["action"]) > 90:
                    r.warn(iw, "action over 90 characters; move the specifics into 'detail'")
                for field in ("action", "detail", "confirm"):
                    check_inline(r, f"{iw}.{field}", item.get(field))
                if "optional" in item and not isinstance(item["optional"], bool):
                    r.err(iw, "optional must be true or false")
                values = item.get("values", [])
                if not isinstance(values, list):
                    r.err(iw, "values must be a list of {label, text}")
                else:
                    for vi, v in enumerate(values):
                        if not isinstance(v, dict) or not text(v.get("text")):
                            r.err(f"{iw}.values[{vi}]", "needs a non-empty 'text' (the literal value)")
            elif kind == "wait":
                if not text(item.get("duration")):
                    r.err(iw, "wait needs a short 'duration' chip, e.g. '24–72 h'")
                if not text(item.get("text")):
                    r.err(iw, "wait needs 'text': what is being waited for")
                check_inline(r, f"{iw}.text", item.get("text"))
            else:
                if not text(item.get("text")):
                    r.err(iw, "note needs 'text'")
                check_inline(r, f"{iw}.text", item.get("text"))
        if n_steps > 12:
            r.warn(pw, f"{n_steps} steps; consider splitting the phase")

    steps = steps_of(doc)
    if not steps:
        r.err("phases", "no steps at all: a runbook needs at least one tickable step")
    seen = {}
    for sid, pos, where in steps:
        if id_num(sid) is None:
            r.err(where, f"id {sid!r} must look like 's1', 's2', ...")
            continue
        if sid in seen:
            r.err(where, f"duplicate id {sid}: every step needs its own id")
        seen[sid] = pos
        if sid in retired:
            r.err(where, f"{sid} is in retired_ids; retired ids are never reused. Give it a new number")

    if rev == 1 and not r.errors:
        expected = [f"s{i}" for i in range(1, len(steps) + 1)]
        if [s[0] for s in steps] != expected:
            r.warn("ids", "first revision should number steps s1..sN in document order")

    # Waits: 'blocks' must point at a step that comes after the wait.
    pos = 0
    for pi, phase in enumerate(phases):
        if not isinstance(phase, dict):
            continue
        for ii, item in enumerate(phase.get("items") or []):
            if isinstance(item, dict) and item.get("type") == "wait" and "blocks" in item:
                target = item["blocks"]
                if not isinstance(target, str) or target not in seen:
                    r.err(f"phases[{pi}].items[{ii}]", f"blocks {target!r}, which is not a step id")
                elif seen[target] < pos:
                    r.err(f"phases[{pi}].items[{ii}]",
                          f"blocks {target}, which comes before the wait; move the wait or fix the id")
            pos += 1


def step_map(doc):
    out = {}
    for phase in doc.get("phases") or []:
        if not isinstance(phase, dict):
            continue
        for item in phase.get("items") or []:
            if isinstance(item, dict) and item.get("type") == "step" and isinstance(item.get("id"), str):
                out[item["id"]] = item
    return out


def literal_values(step):
    values = step.get("values") if isinstance(step.get("values"), list) else []
    return [v.get("text") for v in values if isinstance(v, dict)]


def compare(doc, prev, r, reworded=()):
    """A republish must keep every delivered id meaning the same step.

    Ids alone can't prove that: an id kept on a step whose meaning changed would carry
    the old tick onto new work. So a kept id must keep its literal values exactly, and its
    action unless the caller vouches, with --reworded, that only the wording changed.
    """
    if not isinstance(prev, dict) or not isinstance(doc, dict):
        if not isinstance(prev, dict):
            r.err("--previous", "previous runbook is not a JSON object")
        return
    if text(doc.get("key")) != text(prev.get("key")):
        r.err("key", f"changed from {prev.get('key')!r}; the key never changes, or every saved tick is lost")
    prev_rev, rev = prev.get("revision"), doc.get("revision")
    if isinstance(prev_rev, int) and isinstance(rev, int) and rev <= prev_rev:
        r.err("revision", f"is {rev}, previous was {prev_rev}; add 1 on every republish")
    def ids(items):
        return {x for x in items if isinstance(x, str)} if isinstance(items, list) else set()

    now = ids([s[0] for s in steps_of(doc)])
    retired = ids(doc.get("retired_ids"))
    before = ids([s[0] for s in steps_of(prev)])
    prev_retired = ids(prev.get("retired_ids"))
    ever = before | prev_retired
    for sid in sorted(before - now - retired, key=lambda s: id_num(s) or 0):
        r.err("retired_ids", f"{sid} was in the previous revision and is gone; add it to retired_ids")
    for sid in sorted(prev_retired - retired, key=lambda s: id_num(s) or 0):
        r.err("retired_ids", f"{sid} was retired before; keep it retired so it is never reused")
    old_steps, new_steps = step_map(prev), step_map(doc)
    for sid in sorted(now & before, key=lambda s: id_num(s) or 0):
        old, new = old_steps.get(sid, {}), new_steps.get(sid, {})
        if literal_values(old) != literal_values(new):
            r.err(sid, "kept its id but its values changed, so a tick on the old value would show the "
                       "new one as done. Retire the id and add the step under a new one")
        elif text(old.get("action")) != text(new.get("action")) and sid not in reworded:
            r.err(sid, f"action changed from {text(old.get('action'))!r}. If it's the same step reworded, "
                       f"re-run with --reworded {sid}; if its meaning changed, retire the id and add a new one")
    for sid in sorted(set(reworded) - (now & before), key=lambda s: id_num(s) or 0):
        r.warn("--reworded", f"{sid} is not a step kept from the previous revision; ignored")
    high = max((id_num(s) or 0 for s in ever), default=0)
    for sid in sorted(now - ever, key=lambda s: id_num(s) or 0):
        if (id_num(sid) or 0) <= high:
            r.err("ids", f"new step {sid} must be numbered above s{high}, the highest id ever used")


def main(argv):
    args = argv[1:]
    prev_path, reworded = None, ()
    if "--reworded" in args:
        i = args.index("--reworded")
        if i + 1 >= len(args):
            print("ERROR: --reworded needs step ids, e.g. --reworded s4,s9")
            return 2
        reworded = tuple(x.strip() for x in args[i + 1].split(",") if x.strip())
        del args[i:i + 2]
    if "--previous" in args:
        i = args.index("--previous")
        if i + 1 >= len(args):
            print("ERROR: --previous needs a file path")
            return 2
        prev_path = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print("Usage: python3 scripts/validate_runbook.py runbook.json [--previous runbook.prev.json [--reworded s4,s9]]")
        return 2

    r = Report()
    try:
        doc = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {args[0]}: {exc}")
        return 1
    validate(doc, r)
    if prev_path:
        try:
            prev = json.loads(Path(prev_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: cannot read {prev_path}: {exc}")
            return 1
        compare(doc, prev, r, reworded)
    elif reworded:
        r.warn("--reworded", "only means something with --previous; ignored")

    for e in r.errors:
        print(f"ERROR {e}")
    for w in r.warnings:
        print(f"WARN  {w}")
    n = len(steps_of(doc)) if isinstance(doc, dict) else 0
    if r.errors:
        print(f"{len(r.errors)} error(s), {len(r.warnings)} warning(s). Fix the errors and re-run.")
        return 1
    print(f"OK: {n} steps, {len(r.warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
