#!/usr/bin/env python3
"""Validate compare.json before it is rendered.

Usage:  python3 scripts/validate_compare.py compare.json

Standard library only. Exits 1 on any error, 0 otherwise; warnings never fail the run.
Every message names the field and the fix, so the agent can correct the data and re-run.

The limits are the skill. Six products is a category page, not a decision; a value with
no source is a guess wearing a spec's clothes; a price with no date is stale the day it's
read; and a pick has to rest on rows that exist, for the reasons the user gave.
"""
import json
import re
import sys
from pathlib import Path

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
KINDS = ("maker", "review", "retailer", "user", "claude")
BETTER = ("higher", "lower")
LABEL_KEYS = ("pick", "why", "decided_by", "runner_up", "best_for", "priorities", "assumed",
              "side_by_side", "differences_only", "price", "pros", "cons", "ask", "ask_about",
              "copied", "copy_failed", "sources", "not_available", "unknown", "wins", "offline",
              "yes", "no", "from", "compared", "matters", "page", "ask_hint",
              "partly_unverified", "unverified")


def text(value):
    return value.strip() if isinstance(value, str) else ""


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def short_list(doc, field, cap, errors, item_cap=160):
    items = doc.get(field, [])
    if not isinstance(items, list) or len(items) > cap or not all(text(t) for t in items):
        errors.append(f"{field}: optional list of at most {cap} non-empty lines")
        return []
    for i, t in enumerate(items):
        if len(text(t)) > item_cap:
            errors.append(f"{field}[{i}]: over {item_cap} chars. One line each")
    return items


def main(path):
    errors, warnings = [], []
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {path}: {exc}")
        return 1
    if not isinstance(doc, dict):
        print("ERROR: compare.json must be a JSON object")
        return 1

    if not DATE_RE.match(text(doc.get("date"))):
        errors.append("date: required, as YYYY-MM-DD (today, in the user's timezone)")
    title = text(doc.get("title"))
    if not title or len(title) > 60:
        errors.append("title: required, 1-60 chars, what's being bought ('Noise-cancelling headphones')")

    # Sources first: everything else cites them.
    sources = doc.get("sources")
    source_ids = set()
    if not isinstance(sources, list) or not sources:
        errors.append("sources: required list of {id, title, kind, url?}. Every value cites one")
        sources = []
    for i, s in enumerate(sources):
        where = f"sources[{i}]"
        if not isinstance(s, dict):
            errors.append(f"{where}: must be an object")
            continue
        sid = text(s.get("id"))
        if not ID_RE.match(sid):
            errors.append(f"{where}.id: lowercase letters, digits and hyphens, e.g. 'sony-specs'")
        elif sid in source_ids:
            errors.append(f"{where}.id: '{sid}' is used twice")
        source_ids.add(sid)
        if not text(s.get("title")):
            errors.append(f"{where}.title: required ('Sony spec page', 'RTINGS review')")
        if s.get("kind") not in KINDS:
            errors.append(f"{where}.kind: one of {', '.join(KINDS)}")
        url = s.get("url")
        if url is not None and not re.match(r"^https?://", text(url)):
            errors.append(f"{where}.url: must start with http:// or https://, or be omitted")
        if s.get("kind") in ("maker", "review", "retailer") and not text(url):
            warnings.append(f"{where}: a {s.get('kind')} source with no url can't be checked. Add the page you read")

    offline = doc.get("offline", False)
    if not isinstance(offline, bool):
        errors.append("offline: true or false (true when there was no web access this run)")
    claude_ids = [text(s.get("id")) for s in sources if isinstance(s, dict) and s.get("kind") == "claude"]
    if offline is False and sources and len(claude_ids) == len(sources):
        errors.append("offline: every source is 'claude' but offline is false. Set offline: true so the page says so")
    elif offline is False and claude_ids:
        warnings.append(f"sources: {', '.join(claude_ids)} are Claude's knowledge; the page will mark those values unverified. Replace them with pages you read where you can")

    def cite(where, sid):
        if text(sid) not in source_ids:
            errors.append(f"{where}: source '{sid}' is not in sources. Cite only what you read, by its id")

    # Products.
    products = doc.get("products")
    pids = []
    if not isinstance(products, list) or not 2 <= len(products) <= 5:
        errors.append("products: 2-5. One isn't a comparison; six is a category page. Narrow it")
        products = []
    for i, p in enumerate(products):
        where = f"products[{i}]"
        if not isinstance(p, dict):
            errors.append(f"{where}: must be an object")
            continue
        pid = text(p.get("id"))
        if not ID_RE.match(pid):
            errors.append(f"{where}.id: lowercase letters, digits and hyphens, e.g. 'xm6'")
        elif pid in pids:
            errors.append(f"{where}.id: '{pid}' is used twice")
        pids.append(pid)
        name = text(p.get("name"))
        if not name or len(name) > 40:
            errors.append(f"{where}.name: required, 1-40 chars")
        if len(text(p.get("tagline"))) > 80:
            errors.append(f"{where}.tagline: over 80 chars. One short line")
        if p.get("url") is not None and not re.match(r"^https?://", text(p.get("url"))):
            errors.append(f"{where}.url: must start with http:// or https://, or be omitted")
        for field in ("pros", "cons"):
            items = p.get(field, [])
            if not isinstance(items, list) or len(items) > 3 or not all(text(t) and len(text(t)) <= 90 for t in items):
                errors.append(f"{where}.{field}: at most 3 lines of 90 chars or less")
        price = p.get("price")
        if price is None:
            if not text(p.get("price_note")):
                errors.append(f"{where}.price: required. If you couldn't find one, set null and say why in price_note")
        elif not isinstance(price, dict):
            errors.append(f"{where}.price: an object {{amount, currency, where, as_of, source}} or null")
        else:
            if not is_num(price.get("amount")) or price["amount"] <= 0:
                errors.append(f"{where}.price.amount: a positive number")
            if not CURRENCY_RE.match(text(price.get("currency"))):
                errors.append(f"{where}.price.currency: a 3-letter code such as USD, CAD, EUR")
            if not text(price.get("where")):
                errors.append(f"{where}.price.where: the store it was read at ('Best Buy', 'maker')")
            if not DATE_RE.match(text(price.get("as_of"))):
                errors.append(f"{where}.price.as_of: the date the price was read, YYYY-MM-DD. Prices move")
            if "from" in price and not isinstance(price["from"], bool):
                errors.append(f"{where}.price.from: true when it varies by configuration, else omit")
            if len(text(price.get("note"))) > 60:
                errors.append(f"{where}.price.note: over 60 chars ('Sale, list $449')")
            cite(f"{where}.price.source", price.get("source"))
    currencies = {text(p["price"].get("currency")) for p in products
                  if isinstance(p, dict) and isinstance(p.get("price"), dict)}
    if len(currencies) > 1:
        warnings.append(f"prices use {len(currencies)} currencies ({', '.join(sorted(currencies))}); the price row can't compare them. Convert, or say so in assumptions")

    # Rows.
    rows = doc.get("rows")
    keys = {}
    if not isinstance(rows, list) or not 3 <= len(rows) <= 20:
        errors.append("rows: 3-20. Keep what differs and what matters; drop what every product shares")
        rows = []
    same = 0
    for i, r in enumerate(rows):
        where = f"rows[{i}]"
        if not isinstance(r, dict):
            errors.append(f"{where}: must be an object")
            continue
        key = text(r.get("key"))
        if not ID_RE.match(key) or key == "price":
            errors.append(f"{where}.key: lowercase id such as 'battery'. 'price' is reserved (the page adds it)")
        elif key in keys:
            errors.append(f"{where}.key: '{key}' is used twice")
        if not text(r.get("label")) or len(text(r.get("label"))) > 40:
            errors.append(f"{where}.label: required, 1-40 chars")
        if not text(r.get("group")):
            errors.append(f"{where}.group: required ('Sound', 'Battery', 'Size & weight')")
        better = r.get("better")
        if better is not None and better not in BETTER:
            errors.append(f"{where}.better: 'higher', 'lower', or omitted")
        values = r.get("values")
        if not isinstance(values, dict):
            errors.append(f"{where}.values: an object keyed by product id")
            keys[key] = r
            continue
        for pid in pids:
            if pid not in values:
                errors.append(f"{where}.values: missing '{pid}'. Use {{\"v\": null, \"note\": \"not published\"}} when unknown")
        for pid, cell in values.items():
            cw = f"{where}.values.{pid}"
            if pid not in pids:
                errors.append(f"{cw}: no product has this id")
                continue
            if not isinstance(cell, dict) or "v" not in cell:
                errors.append(f"{cw}: an object {{v, source, note?}}")
                continue
            v = cell["v"]
            if v is None:
                if not text(cell.get("note")):
                    errors.append(f"{cw}: unknown values need a note saying why ('not published')")
                continue
            if not (is_num(v) or isinstance(v, bool) or text(v)):
                errors.append(f"{cw}.v: a number, true/false, non-empty text, or null")
            if better and not is_num(v):
                errors.append(f"{cw}.v: row has better={better}, so values must be numbers (or null)")
            if isinstance(v, str) and len(v) > 60:
                errors.append(f"{cw}.v: over 60 chars. Put detail in note")
            if len(text(cell.get("note"))) > 120:
                errors.append(f"{cw}.note: over 120 chars")
            cite(f"{cw}.source", cell.get("source"))
        known = [json.dumps(c.get("v")) for c in values.values() if isinstance(c, dict) and c.get("v") is not None]
        if len(known) == len(pids) and len(set(known)) == 1:
            same += 1
        keys[key] = r
    if same > 3:
        warnings.append(f"{same} rows are identical across every product. Drop the ones nobody asked about")

    def winners(key):
        if key == "price":
            prices = {p["id"]: p["price"]["amount"] for p in products
                      if isinstance(p, dict) and isinstance(p.get("price"), dict) and is_num(p["price"].get("amount"))}
            if len(prices) < 2 or len(prices) < len(pids) or len(currencies) != 1:
                return None
            low = min(prices.values())
            return {pid for pid, a in prices.items() if a == low}
        # Mirrors winners() in the page template: numeric rows with `better`, and yes/no rows
        # where some products are yes. An unknown value might be the best, so nobody wins.
        r = keys.get(key)
        if not r or not isinstance(r.get("values"), dict):
            return None
        vals = {pid: c.get("v") for pid, c in r["values"].items() if isinstance(c, dict) and c.get("v") is not None}
        if len(vals) < 2 or len(vals) < len(pids):
            return None
        if r.get("better") in BETTER and all(is_num(v) for v in vals.values()):
            best = (max if r["better"] == "higher" else min)(vals.values())
            won = {pid for pid, v in vals.items() if v == best}
        elif all(isinstance(v, bool) for v in vals.values()):
            won = {pid for pid, v in vals.items() if v}
        else:
            return None
        return won if 0 < len(won) < len(vals) else None

    # Priorities.
    priorities = doc.get("priorities", [])
    if not isinstance(priorities, list) or len(priorities) > 4:
        errors.append("priorities: optional, at most 4 {label, row}")
        priorities = []
    for i, pr in enumerate(priorities):
        where = f"priorities[{i}]"
        if not isinstance(pr, dict) or not text(pr.get("label")):
            errors.append(f"{where}: needs a label in the user's words")
            continue
        if text(pr.get("row")) not in keys and text(pr.get("row")) != "price":
            errors.append(f"{where}.row: '{pr.get('row')}' is not a row key. Every priority needs a row that shows it")
    short_list(doc, "assumptions", 3, errors)
    short_list(doc, "sources_missing", 8, errors)
    short_list(doc, "ask", 4, errors, item_cap=120)

    # Verdict.
    v = doc.get("verdict")
    if not isinstance(v, dict):
        errors.append("verdict: required {pick, headline, why, because, runner_up?, best_for?}")
        v = {}
    pick = text(v.get("pick"))
    if pick not in pids:
        errors.append(f"verdict.pick: '{pick}' is not a product id")
    if not text(v.get("headline")) or len(text(v.get("headline"))) > 90:
        errors.append("verdict.headline: required, 90 chars or less")
    if not text(v.get("why")) or len(text(v.get("why"))) > 360:
        errors.append("verdict.why: required, 360 chars or less. Two or three plain sentences")
    because = v.get("because")
    if not isinstance(because, list) or not 1 <= len(because) <= 4:
        errors.append("verdict.because: 1-4 row keys that decide the pick")
        because = []
    for k in because:
        if text(k) not in keys and text(k) != "price":
            errors.append(f"verdict.because: '{k}' is not a row key")
            continue
        w = winners(text(k))
        if w is not None and pick in pids and pick not in w:
            warnings.append(f"verdict.because: the pick loses on '{k}'. Is that really a reason for it?")
    ru = v.get("runner_up")
    if ru is not None:
        if not isinstance(ru, dict) or text(ru.get("id")) not in pids or text(ru.get("id")) == pick:
            errors.append("verdict.runner_up: {id, when}, a different product than the pick")
        elif not text(ru.get("when")) or len(text(ru.get("when"))) > 120:
            errors.append("verdict.runner_up.when: the condition that flips it, 120 chars or less")
    best_for = v.get("best_for", [])
    if not isinstance(best_for, list) or len(best_for) > 3:
        errors.append("verdict.best_for: optional, at most 3 {label, id, row}")
        best_for = []
    seen = set()
    for i, b in enumerate(best_for):
        where = f"verdict.best_for[{i}]"
        if not isinstance(b, dict) or not text(b.get("label")) or len(text(b.get("label"))) > 24:
            errors.append(f"{where}: needs a label of 24 chars or less ('Best value', 'Lightest')")
            continue
        if text(b["label"]).lower() in seen:
            errors.append(f"{where}: label '{b['label']}' is used twice")
        seen.add(text(b["label"]).lower())
        if text(b.get("id")) not in pids:
            errors.append(f"{where}.id: not a product id")
        row = text(b.get("row"))
        if row not in keys and row != "price":
            errors.append(f"{where}.row: required, the row key that earns the label ('price', 'weight')")
        else:
            w = winners(row)
            if w is None:
                errors.append(f"{where}: row '{row}' has no winner (no 'better', a tie, or an unknown value). Pick a row the product wins outright")
            elif text(b.get("id")) not in w:
                errors.append(f"{where}: '{b.get('id')}' doesn't win row '{row}'. The label has to be earned")

    lang = doc.get("lang", "en")
    if not re.match(r"^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$", text(lang)):
        errors.append("lang: a language tag such as en, es, fa, pt-BR")
    labels = doc.get("labels", {})
    if not isinstance(labels, dict):
        errors.append("labels: optional object of heading overrides")
    else:
        for k, val in labels.items():
            if k not in LABEL_KEYS:
                errors.append(f"labels.{k}: unknown key; allowed: {', '.join(LABEL_KEYS)}")
            elif not text(val):
                errors.append(f"labels.{k}: must be non-empty text")
        if text(lang) and not text(lang).startswith("en") and not labels:
            warnings.append("labels: page headings will be English while lang is not; add labels")

    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        print(f"{len(errors)} error(s). Fix compare.json and re-run.")
        return 1
    print(f"compare.json OK ({len(pids)} products, {len(keys)} rows, {len(source_ids)} sources).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_compare.py compare.json")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
