#!/usr/bin/env python3
"""Validate an itinerary.json before anything is rendered from it.

Usage:  python3 scripts/validate_itinerary.py itinerary.json

Standard library only, so it runs in any code-execution sandbox without installing
anything. Exit 0 means renderable: warnings may still be printed and are worth reading.
Exit 1 means at least one error, and every error names the day, the item and the fix.

The rules come from references/itinerary-schema.md. Errors are things that make a plan
wrong on the day: overlapping times, missing days, a "verified" badge with no source.
Warnings are things that make it worse: no travel time between two places, more
activities than the chosen pace allows.
"""
import json
import re
import sys
from datetime import date, timedelta

KINDS = {"activity", "meal", "travel", "stay", "free"}
BOOKING = {"required", "recommended", "walk-in", "unknown"}
STATUS = {"verified", "unverified", "conflict", "none"}
ORIGINS = {"said", "inferred", "asked", "assumed"}
PACES = {"relaxed", "balanced", "packed"}
BUDGETS = {"budget", "mid", "premium", None}
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

# Activities per day before a pace reads as overloaded. Meals, travel, stays and free
# time don't count. Three is a full relaxed day with children: a morning thing, an
# afternoon thing, and one short stop.
PACE_LIMIT = {"relaxed": 3, "balanced": 4, "packed": 6}

# Consecutive items at different places closer together than this, with no travel item
# between them, usually mean the transfer was forgotten. 15 minutes covers a short walk.
MIN_TRANSFER_MIN = 15


def minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def main(path):
    errors, warnings = [], []
    err, warn = errors.append, warnings.append

    try:
        with open(path, encoding="utf-8") as fh:
            plan = json.load(fh)
    except FileNotFoundError:
        print(f"ERROR: {path} not found. Write the itinerary JSON first.")
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: {path} is not valid JSON (line {exc.lineno}, col {exc.colno}): {exc.msg}")
        return 1

    if plan.get("schema") != 1:
        err(f"schema is {plan.get('schema')!r}; this validator understands schema 1")
    if not str(plan.get("title", "")).strip():
        err("title is empty; the page header needs one")
    # Calendar UIDs are built from these ids, so they must survive every edit: an id
    # derived from a title or a time would change when the item moves, and a re-imported
    # calendar would then duplicate the event instead of updating it.
    if not ID.match(str(plan.get("id", ""))):
        err("id must be a short slug (a-z, 0-9, -) set once when the plan is created, never changed")
    rev = plan.get("revision", 0)
    if not isinstance(rev, int) or rev < 0:
        err("revision must be a whole number: 0 on creation, +1 on every edit")
    seen_ids = {}

    def check_id(where, value):
        value = str(value or "")
        if not ID.match(value):
            err(f"{where}: id {value!r} must be a short slug (a-z, 0-9, -), kept unchanged when the item moves")
        elif value in seen_ids:
            err(f"{where}: id {value!r} is already used by {seen_ids[value]}. Ids are unique across the plan")
        else:
            seen_ids[value] = where

    generated = parse_date(plan.get("generated_on"))
    if generated is None:
        err("generated_on must be an ISO date (YYYY-MM-DD): the date the plan was checked")

    trip = plan.get("trip") or {}
    start, end = parse_date(trip.get("start")), parse_date(trip.get("end"))
    if start is None or end is None:
        err("trip.start and trip.end must both be ISO dates (YYYY-MM-DD)")
    elif end < start:
        err(f"trip.end {end} is before trip.start {start}")
    if not str(trip.get("destination", "")).strip():
        err("trip.destination is empty")
    if trip.get("pace") not in PACES:
        err(f"trip.pace is {trip.get('pace')!r}; use one of {sorted(PACES)}")
    if trip.get("budget", None) not in BUDGETS:
        err(f"trip.budget is {trip.get('budget')!r}; use budget, mid, premium or null")
    if not trip.get("timezone"):
        warn("trip.timezone is not set; a calendar export will use floating local times")

    party = trip.get("party") or {}
    if not isinstance(party.get("adults"), int) or party.get("adults", 0) < 1:
        err("trip.party.adults must be a whole number, at least 1")
    kids = party.get("children", [])
    if not isinstance(kids, list):
        err("trip.party.children must be a list of ages ([] if none)")
    elif any(k is not None and not isinstance(k, (int, float)) for k in kids):
        err("trip.party.children holds ages as numbers, or null for an unknown age, never text")

    for i, b in enumerate(plan.get("brief") or []):
        if b.get("origin") not in ORIGINS:
            err(f"brief[{i}] ({b.get('field')}): origin {b.get('origin')!r} must be one of {sorted(ORIGINS)}")
        if b.get("origin") == "assumed" and not str(b.get("why", "")).strip():
            err(f"brief[{i}] ({b.get('field')}): an assumed value needs a 'why' the user can overrule")

    days = plan.get("days") or []
    if not days:
        err("days is empty")
    if start and end and end >= start:
        expected = [start + timedelta(d) for d in range((end - start).days + 1)]
        got = [parse_date(d.get("date")) for d in days]
        missing = [str(d) for d in expected if d not in got]
        extra = [str(d) for d in got if d and d not in expected]
        if missing:
            err(f"no day entry for {', '.join(missing)}; every date in the trip needs one, even a travel day")
        if extra:
            err(f"day entries outside the trip dates: {', '.join(extra)}")
        if [g for g in got if g] != sorted(g for g in got if g):
            err("days are not in date order")
        if len(set(got)) != len(got):
            err("two day entries share a date")

    verified = unverified = conflicts = 0
    pace_limit = PACE_LIMIT.get(trip.get("pace"))

    nothing_to_check = 0

    def check_block(where, chk, item=None):
        nonlocal verified, unverified, conflicts, nothing_to_check
        # Verification status is never implied by a missing field: a named restaurant
        # with no check would otherwise pass silently and drop out of the page's meter.
        # Only free time may leave it out.
        if chk is None:
            if not item or item.get("kind") != "free":
                err(f"{where}: no check block. Use {{\"status\": \"unverified\"}} if it should be "
                    f"checked but wasn't, or {{\"status\": \"none\"}} if there is genuinely nothing to verify")
            return
        if not isinstance(chk, dict):
            err(f"{where}: check must be an object")
            return
        status = chk.get("status")
        if status not in STATUS:
            err(f"{where}: check.status {status!r} must be one of {sorted(STATUS)}")
            return
        src = str(chk.get("source") or "")
        if status == "verified":
            verified += 1
            if not src.startswith(("http://", "https://")):
                err(f"{where}: marked verified but has no source URL. Add the page you read, or mark it unverified")
            if not str(chk.get("claim", "")).strip():
                err(f"{where}: marked verified but no claim says what the source confirmed")
            checked = parse_date(chk.get("checked_on"))
            if checked is None:
                err(f"{where}: verified items need checked_on (YYYY-MM-DD)")
            elif generated and checked > generated:
                err(f"{where}: checked_on {checked} is after generated_on {generated}")
        elif status == "conflict":
            conflicts += 1
            if not str(chk.get("claim", "")).strip():
                err(f"{where}: a conflict needs a claim describing what the sources disagree on")
            if not src.startswith(("http://", "https://")):
                err(f"{where}: a conflict needs a source for at least one side")
        elif status == "none":
            nothing_to_check += 1
            if item and item.get("booking") in ("required", "recommended"):
                err(f"{where}: needs booking, so it can't be 'nothing to verify'. Check it, or mark it unverified")
            elif item and item.get("kind") in ("meal", "stay") and item.get("place"):
                warn(f"{where}: a named place marked 'nothing to verify'. Is it open that day?")
        else:
            unverified += 1

    for d in days:
        label = f"day {d.get('date')}"
        if not str(d.get("title", "")).strip():
            warn(f"{label}: no title; the page will show only the date")
        items = d.get("items") or []
        prev = None
        activities = 0
        for j, it in enumerate(items):
            where = f"{label} item {j + 1} ({it.get('title') or 'untitled'})"
            if not str(it.get("title", "")).strip():
                err(f"{where}: title is empty")
            check_id(where, it.get("id"))
            if it.get("kind") not in KINDS:
                err(f"{where}: kind {it.get('kind')!r} must be one of {sorted(KINDS)}")
            if it.get("booking", "unknown") not in BOOKING:
                err(f"{where}: booking {it.get('booking')!r} must be one of {sorted(BOOKING)}")
            s, e = it.get("start"), it.get("end")
            if not (isinstance(s, str) and HHMM.match(s)):
                err(f"{where}: start {s!r} must be HH:MM (24-hour)")
                s = None
            if e is not None and not (isinstance(e, str) and HHMM.match(e)):
                err(f"{where}: end {e!r} must be HH:MM (24-hour)")
                e = None
            if s and e and minutes(e) <= minutes(s):
                err(f"{where}: ends at {e}, not after it starts at {s}. Split an overnight item across two days")
            if it.get("kind") == "activity":
                activities += 1
            check_block(where, it.get("check"), it)

            if prev and s:
                p_end = prev.get("end") or prev.get("start")
                if p_end and HHMM.match(p_end):
                    if minutes(s) < minutes(p_end):
                        err(f"{where}: starts at {s}, before the previous item ends at {p_end}")
                    gap = minutes(s) - minutes(p_end)
                    moved = (prev.get("place") and it.get("place")
                             and prev["place"].strip().lower() != it["place"].strip().lower())
                    if (moved and 0 <= gap < MIN_TRANSFER_MIN
                            and "travel" not in (prev.get("kind"), it.get("kind"))):
                        warn(f"{where}: {gap} min after '{prev.get('title')}' at a different place, "
                             f"with no travel item. Add the transfer, or confirm it's walkable")
                if prev.get("start") and HHMM.match(str(prev["start"])) and minutes(s) < minutes(prev["start"]):
                    err(f"{where}: items are not in time order")
            prev = it if s else prev

        if pace_limit and activities > pace_limit:
            warn(f"{label}: {activities} activities on a '{trip.get('pace')}' day (guide: {pace_limit}). "
                 f"Cut one, or tell the user it's a full day")

    for k, s in enumerate(plan.get("stays") or []):
        where = f"stay {k + 1} ({s.get('name') or 'unnamed'})"
        if not str(s.get("name", "")).strip():
            err(f"{where}: name is empty")
        check_id(where, s.get("id"))
        nights = s.get("nights")
        if not isinstance(nights, list) or not nights:
            err(f"{where}: nights must be a list of ISO dates, one per night slept there")
        else:
            parsed = [parse_date(n) for n in nights]
            bad = [str(n) for n, p in zip(nights, parsed) if p is None]
            if bad:
                err(f"{where}: nights {', '.join(bad)} are not ISO dates (YYYY-MM-DD)")
            else:
                parsed.sort()
                if len(set(parsed)) != len(parsed):
                    err(f"{where}: a night is listed twice")
                if start and end and (parsed[0] < start or parsed[-1] > end):
                    err(f"{where}: nights {parsed[0]}..{parsed[-1]} fall outside the trip {start}..{end}")
                gaps = [str(b) for a, b in zip(parsed, parsed[1:]) if (b - a).days > 1]
                if gaps:
                    # The calendar shows a stay as one continuous block, so a gap would
                    # claim nights that were spent elsewhere.
                    err(f"{where}: nights are not consecutive (break before {', '.join(gaps)}). "
                        f"Split it into one stay per consecutive run")
        check_block(where, s.get("check"), {"kind": "stay", "place": s.get("name"),
                                            "booking": s.get("booking")})

    for w in warnings:
        print("WARN: ", w)
    for e in errors:
        print("ERROR:", e)
    total = verified + unverified + conflicts + nothing_to_check
    print(f"\n{len(days)} day(s), {total} checked item(s): "
          f"{verified} verified, {unverified} unverified, {conflicts} conflict(s)"
          + (f", {nothing_to_check} with nothing to verify." if nothing_to_check else "."))
    print("Result:", "NOT renderable. Fix the errors above." if errors
          else "renderable" + (f", with {len(warnings)} warning(s)." if warnings else "."))
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[2])
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
