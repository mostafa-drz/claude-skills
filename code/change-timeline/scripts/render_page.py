#!/usr/bin/env python3
"""Render a validated timeline.json into the self-contained timeline page.

Usage:
  python3 scripts/render_page.py timeline.json timeline.html   write the page
  python3 scripts/render_page.py timeline.json --data          print only the escaped JSON, to
                                                               paste into the template's data block

Standard library only. The JSON goes into assets/timeline-template.html in one place, with
"</" escaped so no value (a commit subject containing "</script>", say) can close the data
block early. The page sets every text with textContent, so nothing in the JSON is parsed as HTML.
"""
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "timeline-template.html"
BLOCK = re.compile(r'(<script type="application/json" id="tl-data">)(.*?)(</script>)', re.S)


def payload(src):
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    return data, json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main(argv):
    if len(argv) == 3 and argv[2] == "--data":
        print(payload(argv[1])[1])
        return 0
    if len(argv) != 3:
        print("Usage: python3 scripts/render_page.py timeline.json timeline.html | --data")
        return 2
    data, blob = payload(argv[1])
    html = TEMPLATE.read_text(encoding="utf-8")
    if not BLOCK.search(html):
        print(f"ERROR: data block not found in {TEMPLATE}; the template was edited incorrectly")
        return 1
    html = BLOCK.sub(lambda m: m.group(1) + blob + m.group(3), html, count=1)
    title = str(data.get("title") or "Change timeline").replace("&", "&amp;").replace("<", "&lt;")
    html = html.replace("<title>Change timeline</title>", f"<title>{title}</title>", 1)
    Path(argv[2]).write_text(html, encoding="utf-8")
    print(f"Wrote {argv[2]} ({len(html) // 1024} KB) from {argv[1]}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
