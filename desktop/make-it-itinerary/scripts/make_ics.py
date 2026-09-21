#!/usr/bin/env python3
"""Export a validated itinerary.json as an iCalendar (.ics) file.

Usage:  python3 scripts/make_ics.py itinerary.json trip.ics

Standard library only. Run validate_itinerary.py first; this script assumes the file is
valid and only reports what it has to skip.

One event per timed item. Travel and free-time blocks are included because they're the
parts people forget, and meals too. Stays become all-day events, because a check-in time
is a window rather than an appointment. Times are converted to UTC through the trip's
IANA timezone, so a phone still set to its home timezone before the trip shows each item
at the right local hour. Without a timezone the events are "floating" local times, and the
script says so.

Format rules from RFC 5545: CRLF line endings, lines folded at 75 octets, and text values
escaped (backslash, semicolon, comma, newline).

Each event's UID comes from the plan's `id` and the item's `id`, both set once and never
changed, so an item keeps its UID when it moves to another day or time. SEQUENCE is the
plan's `revision`, which goes up on every edit, so a client that matches events by UID
can tell the re-imported version is newer. Some calendar apps import a file only once,
whatever the UIDs say. Their users replace the old trip events instead, which is why the
skill suggests importing into a separate calendar.
"""
import json
import sys
from datetime import date, datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # Python < 3.9
    ZoneInfo = None
    ZoneInfoNotFoundError = Exception

# An item with a start and no end still needs a duration in a calendar. An hour is a
# visible placeholder. The description says the end wasn't set.
DEFAULT_DURATION_MIN = 60


def esc(text):
    return (str(text).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\r\n", "\\n").replace("\n", "\\n"))


def fold(line):
    """Fold at 75 octets without splitting a multi-byte character."""
    out, cur = [], b""
    for ch in line:
        enc = ch.encode("utf-8")
        if len(cur) + len(enc) > (75 if not out else 74):
            out.append(cur)
            cur = b""
        cur += enc
    out.append(cur)
    return "\r\n ".join(part.decode("utf-8") for part in out)


def uid(plan_id, item_id):
    return f"{item_id}.{plan_id}@make-it-itinerary"


def main(src, dst):
    with open(src, encoding="utf-8") as fh:
        plan = json.load(fh)
    trip = plan["trip"]
    tzname = trip.get("timezone")
    tz, note = None, None
    if tzname and ZoneInfo:
        try:
            tz = ZoneInfo(tzname)
        except (ZoneInfoNotFoundError, ValueError):
            note = f"timezone {tzname!r} not found in this sandbox; using floating local times"
    elif tzname:
        note = "zoneinfo unavailable (Python < 3.9); using floating local times"
    else:
        note = "no trip.timezone; using floating local times (shown at the phone's local clock)"

    def stamp(day, hhmm):
        h, m = map(int, hhmm.split(":"))
        local = datetime.combine(day, datetime.min.time()).replace(hour=h, minute=m)
        if tz:
            return local.replace(tzinfo=tz).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return local.strftime("%Y%m%dT%H%M%S")

    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             "PRODID:-//make-it-itinerary//EN", "CALSCALE:GREGORIAN",
             f"X-WR-CALNAME:{esc(plan['title'])}"]
    count, skipped = 0, 0
    plan_id, seq = plan["id"], int(plan.get("revision", 0))

    for d in plan["days"]:
        day = date.fromisoformat(d["date"])
        for it in d.get("items") or []:
            if not it.get("start"):
                skipped += 1
                continue
            start = it["start"]
            end = it.get("end")
            desc = []
            if not end:
                h, m = map(int, start.split(":"))
                e = datetime(2000, 1, 1, h, m) + timedelta(minutes=DEFAULT_DURATION_MIN)
                if e.day != 1:  # would run past midnight; clamp to 23:59
                    e = datetime(2000, 1, 1, 23, 59)
                end = e.strftime("%H:%M")
                desc.append("End time not set; shown as one hour.")
            if it.get("notes"):
                desc.append(it["notes"])
            if it.get("booking") in ("required", "recommended"):
                desc.append(f"Booking {it['booking']}.")
            if it.get("cost"):
                desc.append(f"Cost: {it['cost']}")
            chk = it.get("check") or {}
            if chk.get("status") == "verified":
                desc.append(f"Checked {chk.get('checked_on')}: {chk.get('claim')} ({chk.get('source')})")
            elif chk.get("status") == "conflict":
                desc.append(f"Sources disagree: {chk.get('claim')}")
            elif chk.get("status") == "unverified":
                desc.append("Not verified online. Confirm before you go.")
            lines += ["BEGIN:VEVENT",
                      f"UID:{uid(plan_id, it['id'])}",
                      f"SEQUENCE:{seq}",
                      f"DTSTAMP:{now}",
                      f"DTSTART:{stamp(day, start)}",
                      f"DTEND:{stamp(day, end)}",
                      f"SUMMARY:{esc(it['title'])}"]
            if it.get("place"):
                lines.append(f"LOCATION:{esc(it['place'])}")
            lines += [f"DESCRIPTION:{esc(chr(10).join(desc))}",
                      "TRANSP:TRANSPARENT" if it.get("kind") in ("free", "travel") else "TRANSP:OPAQUE",
                      "END:VEVENT"]
            count += 1

    for s in plan.get("stays") or []:
        try:
            nights = sorted(date.fromisoformat(n) for n in s.get("nights") or [])
        except (TypeError, ValueError):
            nights = []
        if not nights:
            print(f"SKIPPED stay {s.get('name')!r}: no valid nights (run validate_itinerary.py)")
            skipped += 1
            continue
        first, last = nights[0], nights[-1] + timedelta(days=1)  # DTEND is exclusive
        lines += ["BEGIN:VEVENT",
                  f"UID:{uid(plan_id, s['id'])}",
                  f"SEQUENCE:{seq}",
                  f"DTSTAMP:{now}",
                  f"DTSTART;VALUE=DATE:{first.strftime('%Y%m%d')}",
                  f"DTEND;VALUE=DATE:{last.strftime('%Y%m%d')}",
                  f"SUMMARY:{esc('Stay: ' + str(s.get('name')))}",
                  "TRANSP:TRANSPARENT", "END:VEVENT"]
        count += 1

    lines.append("END:VCALENDAR")
    with open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write("\r\n".join(fold(line) for line in lines) + "\r\n")

    print(f"Wrote {dst}: {count} event(s)" + (f", skipped {skipped} (see above or: no start time)" if skipped else "") + ".")
    if note:
        print("NOTE:", note)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/make_ics.py itinerary.json trip.ics")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
