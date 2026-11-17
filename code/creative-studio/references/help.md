**/creative-studio**: one brief in, finished on-brand assets out.

Examples:
- `/creative-studio reel: how to start an email you've avoided, 25 seconds`
- `/creative-studio instagram carousel: 5 slides on the 2-minute first step`
- `/creative-studio blog hero for "Why the first step is the hardest"`
- `/creative-studio voiceover for this script: ...`
- `/creative-studio deck: 6 slides introducing the kit`

What it does: loads your brand file (`brand/brand.json`), plans the assets with a cost
estimate, drafts cheaply, finishes with your chosen voice and images, checks everything
against the brand, and saves files plus a recipe to `creative/out/`.

It never posts, publishes or emails anything without your yes. Spends over your cap
(default $1) or any AI
video wait for your yes too.

Subcommands: `help`, `config` (brand path, output folder, spend cap), `reset` (clears
preferences only; brands and assets are untouched).

Needs, by asset:
- All: the fal connector (or a `FAL_KEY`), Python 3 with Pillow.
- Video: `ffmpeg` and `ffprobe` with libass.
- Carousels, social and OG cards: Python `playwright` plus its Chromium browser
  (`pip install playwright && playwright install chromium`).
- Decks without a deck tool: `python-pptx`.

The skill checks these before spending anything.
