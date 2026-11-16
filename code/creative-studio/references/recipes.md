# Creative Studio recipes

Contents: [Images](#images) · [Voiceover](#voiceover) · [Vertical video](#vertical-video) ·
[Layouts](#layouts) · [Deck](#deck) · [QA](#qa) · [Costs](#costs)

## Images

`submit_jobs` with one item per option, same endpoint, different scene wording:

```json
{
  "endpoint_id": "<brand.image.endpoint>",
  "input": {
    "prompt": "<one small scene>. <brand.image.prompt_suffix>",
    "style": "<brand.image.style>",
    "colors": "<brand.image.palette_rgb>",
    "image_size": { "width": 1080, "height": 1920 }
  }
}
```

Recraft accepts `image_size` as `{width, height}` or a preset (`square_hd`,
`portrait_16_9`, `landscape_16_9`). Download each result with `curl -sS -o <file> <url>`,
then Read the image to check it (no invented text or logos).

## Voiceover

1. Script: one idea, hook first, about `seconds × words_per_minute ÷ 60` words.
2. Draft: `brand.voiceover.draft` (Kokoro: `{"prompt": script, "voice": "af_heart"}`).
3. Final: `brand.voiceover.default` (ElevenLabs v3:
   `{"text": script, "voice": "Sarah", "stability": 0.5, "timestamps": true}`).
4. Save `voice.mp3` and, when returned, `timestamps.json` (word start/end in seconds).

## Vertical video

`scripts/assemble.py` builds a 1080×1920 MP4 from scenes, a voice track and captions:

```bash
python3 scripts/assemble.py --scenes s1.png s2.png s3.png --voice voice.mp3 \
  --captions captions.json --out reel.mp4 [--fonts-dir /path/to/fonts --font "Instrument Sans"]
```

- `captions.json`: `[{"start": 0.0, "end": 1.8, "text": "Can't start the email?"}, ...]`.
  Build it from word timestamps, 2–5 words per caption, breaking at punctuation. Without
  timestamps, split the script evenly over the voice duration.
- Scenes share the voice duration evenly, with 0.5 s crossfades and a slow 4% push-in.
- Captions are burned in, centred in the lower third, white text on a dark translucent box.
- `--font` is a font family name; `--fonts-dir` is the folder holding its .ttf/.otf.
- Check: `ffprobe -v error -show_entries format=duration -of csv=p=0 reel.mp4`.

## Layouts

Carousels, social cards and OG cards are HTML rendered to PNG at the exact size, so the text
is real, sharp and on-brand:

```python
# render.py: python3 render.py slide.html slide.png 1080 1350
import sys
from playwright.sync_api import sync_playwright
src, out, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    pg.goto(f"file://{__import__('os').path.abspath(src)}")
    pg.wait_for_timeout(500)
    pg.screenshot(path=out)
    b.close()
```

Slide HTML: brand `paper` background, Google Fonts link for the brand fonts, headline in
the display font (56–72px), one supporting line in the text font (28–34px), the
illustration in a rounded white card, a small wordmark at the bottom, generous margins
(≥72px). Last slide: one CTA line and the URL.

## Deck

Prefer an available deck tool (Slides artifact or a pptx skill). Otherwise python-pptx:
16:9, brand `paper` background, display font for titles (40–54pt), text font for body
(20–24pt), accent color only for one key mark per slide, one message per slide.

## QA

- [ ] Brand colors and fonts only; one accent.
- [ ] No invented text, logos or faces in generated images (look at each one).
- [ ] Captions on every video, readable at phone size, in the safe area (top/bottom 250px
      clear of UI).
- [ ] Length within the format; hook in the first 2 seconds.
- [ ] Copy follows `brand.voice` rules; no banned words; no medical or fake claims.
- [ ] Files: MP4 H.264 + AAC, PNG/WebP under 1 MB for web where possible.
- [ ] `manifest.json` lists every file with endpoint, inputs, request ID and cost.

## Costs

Check with `estimate_cost`; at the time of writing (fal): Recraft V3 $0.04 per image
($0.08 vector), ElevenLabs v3 and MiniMax HD $0.10 per 1,000 characters, Kokoro much
cheaper, AI video roughly $0.05–0.50 per second depending on model and resolution.
