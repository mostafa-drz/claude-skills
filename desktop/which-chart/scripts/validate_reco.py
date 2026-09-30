#!/usr/bin/env python3
"""Validate reco.json before it is rendered.

Usage:  python3 scripts/validate_reco.py reco.json

Standard library only. Exits 1 on any error, 0 otherwise; warnings never fail the run.
Every message names the field and the fix, so the agent can correct the data and re-run.

What it guards, and why:
- One pick. A "top three" with no winner hands the decision back to the user.
- Every chart is a Vega-Lite spec that reads the user's rows (data {"name": "table"}), and
  every field a spec encodes exists in those rows or is created by a transform. A preview
  that silently plots nothing is worse than no preview.
- Illustrative data is labelled. If the rows were invented to show the shape, the page must
  say so, or a developer will read a made-up trend as a finding.
- No dual axes, no pies over time, no red-vs-green as the only encoding: the three mistakes
  this skill most often has to talk people out of must not appear in its own pick.
- Every reason cites a source from the list, so a claim can be checked.
"""
import json
import re
import sys
from pathlib import Path

KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_RE = re.compile(r"^#([0-9a-fA-F]{6})$")
RELATIONSHIPS = ("deviation", "correlation", "ranking", "distribution", "change-over-time",
                 "magnitude", "part-to-whole", "spatial", "flow")
FIELD_TYPES = ("temporal", "quantitative", "nominal", "ordinal")
SOURCES = ("csv", "json", "pasted", "screenshot", "description", "connector")
MAX_ROWS = 1500
TOP_LEVEL_VIEWS = ("mark", "layer", "facet", "hconcat", "vconcat", "concat", "repeat")
# Keys under which Vega-Lite creates a new field name.
CREATES = ("as", "groupby")


def text(value):
    return value.strip() if isinstance(value, str) else ""


def hue_of(hex6):
    r, g, b = (int(hex6[i:i + 2], 16) / 255 for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 0.12:
        return None  # a grey has no hue worth judging
    d = mx - mn
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60


def walk(node, visit, path="spec"):
    visit(node, path)
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, visit, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, visit, f"{path}[{i}]")


def created_fields(spec):
    """Names a spec's transforms (or aggregate/timeUnit shortcuts) bring into being."""
    names = set()

    def visit(node, _):
        if not isinstance(node, dict):
            return
        for key in CREATES:
            val = node.get(key)
            if isinstance(val, str):
                names.add(val)
            elif isinstance(val, list):
                names.update(v for v in val if isinstance(v, str))
        # {"fold": [...], "as": [...]} defaults to key/value
        if "fold" in node and "as" not in node:
            names.update(("key", "value"))
        if "pivot" in node:
            names.add(str(node.get("pivot")))
    walk(spec, visit)
    return names


def encoded_fields(spec):
    out = []

    def visit(node, path):
        if isinstance(node, dict) and ".encoding" in path and isinstance(node.get("field"), str):
            out.append((node["field"], path))
    walk(spec, visit)
    return out


DATE_ONLY = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")


def check_time(warnings, where, spec, date_only_fields):
    """Date-only strings ("2026-06-29") parse as UTC but display in local time, so without
    utc time units every label west of Greenwich shows the day (or month) before."""
    def visit(node, path):
        if not (isinstance(node, dict) and ".encoding" in path and node.get("field") in date_only_fields):
            return
        tu, scale = node.get("timeUnit"), node.get("scale")
        utc = (isinstance(tu, str) and tu.startswith("utc")) or \
            (isinstance(scale, dict) and scale.get("type") == "utc") or \
            (".tooltip" in path and node.get("formatType") == "utc")
        if (node.get("type") == "temporal" or tu) and not utc:
            warnings.append(f"{path}: '{node['field']}' holds date-only strings; use a utc timeUnit "
                            "(utcyearmonthdate) or \"scale\": {\"type\": \"utc\"}, and "
                            "\"formatType\": \"utc\" on formatted axes, or labels shift a day back")
    walk(spec, visit)


def check_spec(errors, warnings, where, spec, field_names, allow_repeat):
    if not isinstance(spec, dict):
        errors.append(f"{where}.spec: must be a Vega-Lite object")
        return
    if not any(k in spec for k in TOP_LEVEL_VIEWS):
        errors.append(f"{where}.spec: no mark, layer, facet, concat or repeat; it would draw nothing")
    data = spec.get("data")
    if data != {"name": "table"}:
        errors.append(f'{where}.spec.data: must be {{"name": "table"}}, so the chart reads the '
                      f"rows in data.rows (the page supplies them); don't inline values")
    if "datasets" in spec:
        errors.append(f"{where}.spec.datasets: remove it; the page adds the rows")
    if "$schema" not in spec:
        warnings.append(f"{where}.spec: add \"$schema\": \"https://vega.github.io/schema/vega-lite/v6.json\" "
                        "so the copied spec validates in editors")
    known = set(field_names) | created_fields(spec)
    for name, path in encoded_fields(spec):
        base = name.split(".")[0]
        if name not in known and base not in known and not (allow_repeat and name.startswith("repeat")):
            errors.append(f"{path}: field '{name}' is not in data.fields and no transform creates "
                          f"it; fix the name or add the transform")

    # Dual axes: a layer whose y scales are resolved independently.
    def visit(node, path):
        if isinstance(node, dict):
            res = node.get("resolve", {})
            if isinstance(res, dict) and isinstance(res.get("scale"), dict) and \
                    res["scale"].get("y") == "independent" and "layer" in node:
                errors.append(f"{path}.resolve: independent y scales on a layer is a dual-axis "
                              "chart; use two charts, small multiples, or index to a common base")
            if node.get("mark") in ("arc", {"type": "arc"}) or \
                    (isinstance(node.get("mark"), dict) and node["mark"].get("type") == "arc"):
                enc = node.get("encoding", {})
                for ch in ("facet", "row", "column", "x"):
                    f = enc.get(ch, {}) if isinstance(enc, dict) else {}
                    if isinstance(f, dict) and f.get("type") == "temporal":
                        errors.append(f"{path}: pie/donut per time period; change over time needs a "
                                      "common baseline (lines, stacked bars)")
            scale = node.get("scale")
            if isinstance(scale, dict) and isinstance(scale.get("range"), list):
                hues = [hue_of(m.group(1)) for c in scale["range"] if isinstance(c, str)
                        for m in [HEX_RE.match(c)] if m]
                red = any(h is not None and (h < 20 or h > 340) for h in hues)
                green = any(h is not None and 90 <= h <= 150 for h in hues)
                if red and green:
                    warnings.append(f"{path}.scale.range: red and green together can't be told "
                                    "apart by ~1 in 12 men; use the blue/red pair in "
                                    "references/choosing.md, or add labels as a second encoding")
    walk(spec, visit)


def main(path):
    errors, warnings = [], []
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {path}: {exc}")
        return 1
    if not isinstance(doc, dict):
        print("ERROR: reco.json must be a JSON object")
        return 1

    if not KEY_RE.match(text(doc.get("key"))):
        errors.append("key: a lowercase-hyphen slug such as 'brand-sentiment-over-time'")
    title = text(doc.get("title"))
    if not title or len(title) > 60:
        errors.append("title: a name of 60 characters or less, not a sentence")

    brief = doc.get("brief") if isinstance(doc.get("brief"), dict) else {}
    for f in ("use_case", "question", "audience", "surface"):
        if not text(brief.get(f)):
            errors.append(f"brief.{f}: required (a default is fine; say it was assumed in brief.assumed)")
    if len(text(brief.get("question"))) > 140:
        errors.append("brief.question: one question, 140 characters or less")
    if brief.get("assumed") is not None and not isinstance(brief.get("assumed"), list):
        errors.append("brief.assumed: a list of the brief fields that were defaults, not answers")

    # Data
    data = doc.get("data") if isinstance(doc.get("data"), dict) else {}
    if data.get("source") not in SOURCES:
        errors.append(f"data.source: one of {', '.join(SOURCES)}")
    if not isinstance(data.get("illustrative"), bool):
        errors.append("data.illustrative: true when rows were made up to show the shape, false when "
                      "they are the user's")
    if data.get("source") == "description" and data.get("illustrative") is False:
        errors.append("data.illustrative: rows built from a description are illustrative; set true")
    rows = data.get("rows")
    if not isinstance(rows, list) or not rows or not all(isinstance(r, dict) for r in rows):
        errors.append("data.rows: a non-empty list of objects, one per row")
        rows = []
    elif len(rows) > MAX_ROWS:
        errors.append(f"data.rows: {len(rows)} rows; aggregate to {MAX_ROWS} or fewer (the grain the "
                      "chart shows), and say so in data.notes")
    fields = data.get("fields")
    field_names = []
    if not isinstance(fields, list) or not fields:
        errors.append("data.fields: list each column with name, type and role")
    else:
        for i, f in enumerate(fields):
            if not isinstance(f, dict) or not text(f.get("name")):
                errors.append(f"data.fields[{i}]: needs a name")
                continue
            field_names.append(f["name"])
            if f.get("type") not in FIELD_TYPES:
                errors.append(f"data.fields[{i}].type: one of {', '.join(FIELD_TYPES)}")
            if rows and not any(f["name"] in r for r in rows[:50]):
                errors.append(f"data.fields[{i}]: '{f['name']}' appears in none of the first rows")
    if rows:
        extra = set().union(*(r.keys() for r in rows[:50])) - set(field_names)
        if extra:
            warnings.append(f"data.rows: columns not described in data.fields: {', '.join(sorted(extra))}")

    date_only = {f for f in field_names
                 if rows and all(DATE_ONLY.match(str(r.get(f, ""))) for r in rows[:50] if f in r)}

    rel = doc.get("relationships")
    if not isinstance(rel, list) or not rel or any(r not in RELATIONSHIPS for r in rel):
        errors.append(f"relationships: 1–2 of {', '.join(RELATIONSHIPS)}")
    elif len(rel) > 2:
        warnings.append("relationships: more than two usually means the question isn't settled yet")

    sources = doc.get("sources")
    n_sources = len(sources) if isinstance(sources, list) else 0
    if not n_sources:
        errors.append("sources: at least one {label, url} that the reasons cite")
    else:
        for i, s in enumerate(sources):
            if not isinstance(s, dict) or not text(s.get("label")) or \
                    not text(s.get("url")).startswith(("https://", "http://")):
                errors.append(f"sources[{i}]: needs a label and an http(s) url")

    def check_cites(where, cites):
        if not isinstance(cites, list) or not cites:
            errors.append(f"{where}.cites: list the source numbers (1-based) behind this reason, "
                          "or mark a why line \"judgement\": true")
            return
        for c in cites:
            if not isinstance(c, int) or not 1 <= c <= n_sources:
                errors.append(f"{where}.cites: {c!r} is not a source number 1..{n_sources}")

    # Options
    options = doc.get("options")
    if not isinstance(options, list) or not options:
        errors.append("options: one pick plus 1–3 alternatives")
        options = []
    picks = [o for o in options if isinstance(o, dict) and o.get("rank") == "pick"]
    alts = [o for o in options if isinstance(o, dict) and o.get("rank") == "alternative"]
    if len(picks) != 1:
        errors.append(f"options: exactly one rank 'pick' (found {len(picks)}); choose, don't hand back a list")
    if not 1 <= len(alts) <= 3:
        errors.append(f"options: 1–3 rank 'alternative' (found {len(alts)})")
    if options and options[0] is not (picks[0] if picks else None):
        errors.append("options[0]: put the pick first")
    ids = set()
    for i, o in enumerate(options):
        where = f"options[{i}]"
        if not isinstance(o, dict):
            errors.append(f"{where}: must be an object")
            continue
        oid = text(o.get("id"))
        if not KEY_RE.match(oid) or oid in ids:
            errors.append(f"{where}.id: a unique slug")
        ids.add(oid)
        if o.get("rank") not in ("pick", "alternative"):
            errors.append(f"{where}.rank: 'pick' or 'alternative'")
        if not text(o.get("name")) or len(text(o.get("name"))) > 60:
            errors.append(f"{where}.name: the chart's name, 60 characters or less")
        if not text(o.get("answers")):
            errors.append(f"{where}.answers: the question this chart answers best, in the user's words")
        why = o.get("why")
        if not isinstance(why, list) or not 1 <= len(why) <= 3:
            errors.append(f"{where}.why: 1–3 reasons")
        else:
            for j, w in enumerate(why):
                if not isinstance(w, dict) or not text(w.get("text")):
                    errors.append(f"{where}.why[{j}]: {{text, cites}}")
                    continue
                if len(w["text"]) > 220:
                    errors.append(f"{where}.why[{j}].text: 220 characters or less")
                if w.get("judgement") is True:
                    if w.get("cites"):
                        errors.append(f"{where}.why[{j}]: judgement or cites, not both")
                else:
                    check_cites(f"{where}.why[{j}]", w.get("cites"))
        costs = o.get("costs")
        if not isinstance(costs, list) or not 1 <= len(costs) <= 3 or not all(text(c) for c in costs):
            errors.append(f"{where}.costs: 1–3 honest costs; every chart has one")
        if o.get("rank") == "alternative" and not text(o.get("choose_if")):
            errors.append(f"{where}.choose_if: when this beats the pick")
        check_spec(errors, warnings, where, o.get("spec"), field_names, True)
        check_time(warnings, where, o.get("spec"), date_only)

    avoid = doc.get("avoid", [])
    if not isinstance(avoid, list) or len(avoid) > 3:
        errors.append("avoid: at most 3")
    else:
        for i, a in enumerate(avoid):
            if not isinstance(a, dict) or not text(a.get("name")) or not text(a.get("why")):
                errors.append(f"avoid[{i}]: {{name, why, cites}}")
            else:
                check_cites(f"avoid[{i}]", a.get("cites"))

    shots = doc.get("screenshots", [])
    if not isinstance(shots, list):
        errors.append("screenshots: a list")
    else:
        for i, s in enumerate(shots):
            if not isinstance(s, dict) or not all(text(s.get(k)) for k in ("label", "seen", "verdict")):
                errors.append(f"screenshots[{i}]: {{label, seen, verdict}}")
    if data.get("source") == "screenshot" and not shots:
        warnings.append("screenshots: the data came from a screenshot; say what you read from it")

    notes = doc.get("build_notes", [])
    if not isinstance(notes, list) or len(notes) > 6 or not all(text(n) for n in notes):
        errors.append("build_notes: up to 6 short lines")

    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    if errors:
        print(f"\n{len(errors)} error(s). Fix them and re-run.")
        return 1
    print(f"OK: {len(options)} options, {len(rows)} rows, {n_sources} sources"
          + (f", {len(warnings)} warning(s)" if warnings else ""))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_reco.py reco.json")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
