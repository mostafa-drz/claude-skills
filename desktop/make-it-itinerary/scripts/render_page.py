#!/usr/bin/env python3
"""Render a validated itinerary.json into the self-contained HTML page.

Usage:  python3 scripts/render_page.py itinerary.json itinerary.html

Standard library only. Injects the JSON into assets/itinerary-template.html, the one
place the data goes, and escapes "</" so no value (a restaurant called
"</script>", say) can close the data block early and break the page or inject markup.
Every value is later rendered with textContent, so the escaping here is the only
HTML-level concern.
"""
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "itinerary-template.html"
BLOCK = re.compile(r'(<script type="application/json" id="itinerary-data">)(.*?)(</script>)', re.S)


def main(src, dst):
    plan = json.loads(Path(src).read_text(encoding="utf-8"))
    payload = json.dumps(plan, ensure_ascii=False, indent=1).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    if not BLOCK.search(html):
        print(f"ERROR: data block not found in {TEMPLATE}; the template was edited incorrectly")
        return 1
    html = BLOCK.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(3), html, count=1)
    title = str(plan.get("title") or "Trip itinerary").replace("&", "&amp;").replace("<", "&lt;")
    html = html.replace("<title>Trip itinerary</title>", f"<title>{title}</title>", 1)
    Path(dst).write_text(html, encoding="utf-8")
    print(f"Wrote {dst} ({len(html) // 1024} KB) from {src}.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/render_page.py itinerary.json itinerary.html")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
