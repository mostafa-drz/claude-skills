#!/usr/bin/env python3
"""Render a validated reco.json into the self-contained recommendation page.

Usage:
  python3 scripts/render_page.py reco.json reco.html   write the page
  python3 scripts/render_page.py reco.json --data      print only the escaped JSON, to paste
                                                       into the template's data block

Standard library only. The JSON goes into assets/page-template.html in one place, with "</"
escaped so no value (a label containing "</script>", say) can close the data block early.
The page sets every text with textContent and hands the rows to Vega-Lite as data, so
nothing in reco.json is ever parsed as HTML.
"""
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "page-template.html"
BLOCK = re.compile(r'(<script type="application/json" id="reco-data">)(.*?)(</script>)', re.S)


def payload(src):
    reco = json.loads(Path(src).read_text(encoding="utf-8"))
    return reco, json.dumps(reco, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main(argv):
    if len(argv) == 3 and argv[2] == "--data":
        print(payload(argv[1])[1])
        return 0
    if len(argv) != 3:
        print("Usage: python3 scripts/render_page.py reco.json reco.html | --data")
        return 2
    reco, data = payload(argv[1])
    html = TEMPLATE.read_text(encoding="utf-8")
    if not BLOCK.search(html):
        print(f"ERROR: data block not found in {TEMPLATE}; the template was edited incorrectly")
        return 1
    html = BLOCK.sub(lambda m: m.group(1) + data + m.group(3), html, count=1)
    title = str(reco.get("title") or "Which chart").replace("&", "&amp;").replace("<", "&lt;")
    html = html.replace("<title>Which chart</title>", f"<title>{title}</title>", 1)
    Path(argv[2]).write_text(html, encoding="utf-8")
    print(f"Wrote {argv[2]} ({len(html) // 1024} KB) from {argv[1]}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
