#!/usr/bin/env python3
"""Mirror SKILLS_GUIDE.md into code/ so `cp -r code/* ~/.claude/skills/` ships it.

`audit-skills` reads `~/.claude/skills/SKILLS_GUIDE.md` at runtime, so the copy has to
exist there — but a second hand-maintained copy drifts, and this one already had.
It is generated now, and `--check` fails if the two diverge.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "SKILLS_GUIDE.md", ROOT / "code" / "SKILLS_GUIDE.md"
BANNER = "<!-- Generated copy of ../SKILLS_GUIDE.md — edit that one, then run `make catalog`. -->\n\n"

want = BANNER + SRC.read_text()
if "--check" in sys.argv:
    have = DST.read_text() if DST.exists() else ""
    if have != want:
        sys.exit("code/SKILLS_GUIDE.md is out of sync — run `make catalog`.")
    print("guide copy in sync")
else:
    DST.write_text(want)
    print("guide copy synced to code/")
