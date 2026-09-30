#!/usr/bin/env python3
"""Render a validated compare.json into the self-contained HTML page.

Usage:
  python3 scripts/render_page.py compare.json --data           print the data block only
  python3 scripts/render_page.py compare.json compare.html     write the full page

With artifacts available, the agent writes the artifact itself, as the template plus the
printed data block, so the page is generated once. The full-page mode is for surfaces
without artifacts, where the file is shared instead.

Standard library only. Injects the JSON into assets/compare-template.html, the one place
the data goes, and escapes "</" so no value can close the data block early and inject
markup. Every value is later rendered with textContent, so this is the only HTML-level
concern.
"""
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "compare-template.html"
BLOCK = re.compile(r'(<script type="application/json" id="compare-data">)(.*?)(</script>)', re.S)


def payload_of(src):
    doc = json.loads(Path(src).read_text(encoding="utf-8"))
    return json.dumps(doc, ensure_ascii=False, indent=1).replace("</", "<\\/")


def main(src, dst):
    payload = payload_of(src)
    if dst == "--data":
        print(payload)
        return 0
    html = TEMPLATE.read_text(encoding="utf-8")
    if not BLOCK.search(html):
        print(f"ERROR: data block not found in {TEMPLATE}; the template was edited incorrectly")
        return 1
    html = BLOCK.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(3), html, count=1)
    Path(dst).write_text(html, encoding="utf-8")
    print(f"Wrote {dst} ({len(html) // 1024} KB) from {src}.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/render_page.py compare.json (--data | compare.html)")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
