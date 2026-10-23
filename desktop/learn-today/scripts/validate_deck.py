#!/usr/bin/env python3
"""Validate deck.json before it is rendered.

Usage:  python3 scripts/validate_deck.py deck.json

Standard library only. Exits 1 on any error, 0 otherwise; warnings never fail the run.
Every message names the field and the fix, so the agent can correct the data and re-run.

The limits are the skill. A deck of nine cards is a backlog, not a day's learning. A
link nobody opened this run may not exist, and a summary of a video nobody could read is
made up, so every card states how it was verified and what its summary came from. And a
reason can only cite a source that was actually read.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FORMATS = ("video", "article", "podcast", "course", "paper", "book", "tool")
VERIFIED = ("oembed", "opened")
SUMMARY_FROM = ("transcript", "page", "description")
STORAGE = ("artifact", "browser")
LABEL_KEYS = ("today", "top_pick", "stretch", "why", "you_get", "try", "open", "more",
              "less", "done", "feedback", "copy", "copied", "paste_hint", "adjusted",
              "read_from", "not_available", "min", "next", "prev", "start", "no_taps",
              "picks", "in_all", "of", "from_transcript", "from_page", "from_description")
YOUTUBE_HOSTS = ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be")
# BCP 47, simplified: language, then optional script, region and variants.
LANG_RE = re.compile(r"^[a-z]{2,3}(-[a-z]{4})?(-([a-z]{2}|\d{3}))?(-([a-z0-9]{5,8}|\d[a-z0-9]{3}))*$", re.I)
# Tracking parameters never change what a page is. Playback ones (t, si...) only matter on
# YouTube, where the video id alone identifies the piece; elsewhere ?t= can be a page id.
TRACKING = ("utm_",)


def link_key(parsed):
    """Identity of a link for duplicate checks: one YouTube video is one pick, whatever the URL form."""
    host = parsed.hostname or ""
    if host in YOUTUBE_HOSTS:
        vid = parsed.path.strip("/") if host == "youtu.be" else (parse_qs(parsed.query).get("v") or [""])[0]
        if vid:
            return ("youtube", vid)
    query = sorted((k, v) for k, vs in parse_qs(parsed.query).items() if not k.startswith(TRACKING) for v in vs)
    return (host.removeprefix("www."), parsed.path.rstrip("/"), tuple(query))


def text(value):
    return value.strip() if isinstance(value, str) else ""


def cap(errors, where, value, limit):
    if not value:
        errors.append(f"{where}: required and non-empty")
    elif len(value) > limit:
        errors.append(f"{where}: {len(value)} chars, cap is {limit}. Cut it")


def whole(n):
    return isinstance(n, int) and not isinstance(n, bool)


def main(path):
    errors, warnings = [], []
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {path}: {exc}")
        return 1
    if not isinstance(doc, dict):
        print("ERROR: deck.json must be a JSON object")
        return 1

    if not DATE_RE.match(text(doc.get("date"))):
        errors.append("date: required, as YYYY-MM-DD (today's date in the user's timezone)")
    if doc.get("intro") is not None:
        cap(errors, "intro", text(doc.get("intro")), 160)

    checked = doc.get("sources_checked")
    if not isinstance(checked, list) or not all(text(s) for s in checked):
        errors.append("sources_checked: required list of the sources actually read this run")
        checked = []
    checked = {text(s) for s in checked}

    def cites(where, items, lo, hi):
        if not isinstance(items, list) or not lo <= len(items) <= hi:
            errors.append(f"{where}: {lo}-{hi} items, each {{source, fact}}")
            return
        for i, e in enumerate(items):
            w = f"{where}[{i}]"
            if not isinstance(e, dict) or not text(e.get("source")) or not text(e.get("fact")):
                errors.append(f"{w}: needs a non-empty source and fact")
            elif text(e["source"]) not in checked and text(e["source"]) != "You":
                errors.append(f"{w}: source '{e['source']}' is not in sources_checked. Cite only "
                              "what you read (add Memory, Past chats, Project files there when read), "
                              "or 'You' for the user's words")
            elif len(text(e["fact"])) > 140:
                errors.append(f"{w}: fact over 140 chars")

    items = doc.get("items")
    if not isinstance(items, list) or not 3 <= len(items) <= 5:
        errors.append("items: 3-5 cards. Fewer than 3 verified? Give them as text instead of a deck")
        items = items if isinstance(items, list) else []

    seen, formats, areas, stretch, spans = set(), [], set(), 0, []
    budget = doc.get("daily_minutes", 30)
    if not whole(budget) or not 5 <= budget <= 240:
        errors.append("daily_minutes: optional whole number, 5-240 (default 30)")
        budget = 30

    for i, it in enumerate(items):
        w = f"items[{i}]"
        if not isinstance(it, dict):
            errors.append(f"{w}: must be an object")
            continue
        cap(errors, f"{w}.title", text(it.get("title")), 100)
        cap(errors, f"{w}.creator", text(it.get("creator")), 60)
        cap(errors, f"{w}.why", text(it.get("why")), 240)
        cap(errors, f"{w}.try", text(it.get("try")), 140)

        raw_url = it.get("url")
        url = raw_url if isinstance(raw_url, str) else ""
        try:
            parsed = urlparse(url)
            parsed.hostname  # raises on a malformed host such as "https://[bad"
        except ValueError:
            parsed = None
        if url != url.strip() or not parsed or parsed.scheme != "https" or not parsed.hostname:
            errors.append(f"{w}.url: an https link that you opened this run, with no spaces around it")
        else:
            key = link_key(parsed)
            if key in seen:
                errors.append(f"{w}.url: same piece as an earlier card (another link form or timestamp of it)")
            seen.add(key)
            if parsed.hostname in YOUTUBE_HOSTS and it.get("verified_by") != "oembed":
                warnings.append(f"{w}: YouTube link not checked with oEmbed; it may be private or removed")

        fmt = it.get("format")
        if fmt not in FORMATS:
            errors.append(f"{w}.format: one of {', '.join(FORMATS)}")
        else:
            formats.append(fmt)
        if it.get("verified_by") not in VERIFIED:
            errors.append(f"{w}.verified_by: one of {', '.join(VERIFIED)}. Open the link before it goes in")
        if it.get("summary_from") not in SUMMARY_FROM:
            errors.append(f"{w}.summary_from: one of {', '.join(SUMMARY_FROM)}. Say what the summary came from")

        minutes = it.get("minutes")
        if not whole(minutes) or not 1 <= minutes <= 240:
            errors.append(f"{w}.minutes: whole minutes, 1-240")
        else:
            spans.append(minutes)
        full = it.get("full_minutes")
        if full is not None and (not whole(full) or not whole(minutes) or full <= minutes or full > 600):
            errors.append(f"{w}.full_minutes: optional, the whole piece's length when minutes is only the "
                          "part the card points to (a whole number above minutes, at most 600)")

        area = text(it.get("area"))
        if not area or len(area) > 24:
            errors.append(f"{w}.area: 1-24 chars (work, business, life...)")
        areas.add(area.lower())
        if it.get("stretch") is True:
            stretch += 1
        elif "stretch" in it and not isinstance(it.get("stretch"), bool):
            errors.append(f"{w}.stretch: true or false, or omitted")

        summary = it.get("summary")
        if not isinstance(summary, list) or not 2 <= len(summary) <= 3 or not all(text(s) for s in summary):
            errors.append(f"{w}.summary: 2-3 non-empty lines of concrete takeaways")
        else:
            for j, s in enumerate(summary):
                if len(text(s)) > 160:
                    errors.append(f"{w}.summary[{j}]: over 160 chars")

        cites(f"{w}.because", it.get("because"), 1, 3)

    # The promise: the top pick plus any one other card fits the day. A long piece fits by
    # pointing to its best part (a timestamp), with minutes for that part and full_minutes for the whole.
    if len(spans) == len(items) and spans:
        if spans[0] > budget:
            errors.append(f"items[0]: the top pick is {spans[0]} min, over daily_minutes {budget}. "
                          "Pick a shorter one, or point to a part with a timestamp and set full_minutes")
        else:
            for i, m in enumerate(spans[1:], start=1):
                if spans[0] + m > budget:
                    errors.append(f"items[{i}]: top pick ({spans[0]}) + this card ({m}) is over daily_minutes "
                                  f"{budget}. Point to a part with a timestamp and set full_minutes, or swap it")
    if stretch > 1:
        errors.append("items: at most one stretch card")
    for f in set(formats):
        if f and formats.count(f) > 2 and not doc.get("format_preference"):
            warnings.append(f"items: {formats.count(f)} cards are {f}. Vary formats unless the user prefers one")
    mix = doc.get("mix", ["work", "business", "life"])
    if not isinstance(mix, list) or not mix or not all(text(m) for m in mix):
        errors.append("mix: optional list of areas, such as [\"work\", \"business\", \"life\"]")
    elif len(items) >= 3:
        missing = [m for m in mix if text(m).lower() not in areas]
        if missing and len(mix) <= len(items):
            warnings.append(f"items: no card for {', '.join(missing)} from the mix. Fine if the user asked for that")

    adjusted = doc.get("adjusted", [])
    if adjusted:
        cites_list = [{"source": a.get("source"), "fact": a.get("change")} if isinstance(a, dict) else a
                      for a in adjusted] if isinstance(adjusted, list) else adjusted
        cites("adjusted", cites_list, 1, 3)

    missing_src = doc.get("sources_missing", [])
    if not isinstance(missing_src, list) or not all(text(t) for t in missing_src):
        errors.append("sources_missing: optional list of non-empty lines")
    if doc.get("feedback_storage", "artifact") not in STORAGE:
        errors.append(f"feedback_storage: one of {', '.join(STORAGE)}")

    lang = doc.get("lang", "en")
    if not isinstance(lang, str) or not LANG_RE.match(lang):
        errors.append("lang: a language tag such as en, es, fa, pt-BR, with no spaces")
        lang = "en"
    labels = doc.get("labels", {})
    if not isinstance(labels, dict):
        errors.append("labels: optional object of label overrides")
    else:
        for k, v in labels.items():
            if k not in LABEL_KEYS:
                errors.append(f"labels.{k}: unknown key; allowed: {', '.join(LABEL_KEYS)}")
            elif not text(v):
                errors.append(f"labels.{k}: must be non-empty text")
        if text(lang) and not text(lang).startswith("en") and not labels:
            warnings.append("labels: page labels will be English while lang is not; add labels")

    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        print(f"{len(errors)} error(s). Fix deck.json and re-run.")
        return 1
    total = sum(it.get("minutes", 0) for it in items if isinstance(it, dict) and whole(it.get("minutes")))
    print(f"deck.json OK ({len(items)} cards, {total} min in all).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_deck.py deck.json")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
