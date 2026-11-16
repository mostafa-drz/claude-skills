---
name: creative-studio
description: >-
  Makes brand-consistent creative assets end to end from a one-line brief: images, voiceovers,
  short vertical videos with burned-in captions (Reels, TikTok, Shorts), Instagram carousels,
  social cards, blog heroes and slide decks. Reads the project's brand file, generates with
  fal.ai models (images, voice, optional AI video), assembles video with ffmpeg, checks every
  asset against the brand, shows a cost estimate before spending and saves everything with
  its recipe. Never posts or publishes without an explicit yes. Use for "make a reel",
  "Instagram post", "TikTok", "carousel", "voiceover", "explainer video", "blog image",
  "social card", "ad creative", "deck" or "creative assets".
disable-model-invocation: true
allowed-tools:
  - Read
  - Glob
  - Write
  - Edit
  - Bash(ffmpeg *)
  - Bash(ffprobe *)
  - Bash(python3 *)
  - Bash(mkdir *)
  - Bash(curl -sS -o *)
  - mcp__Fal_AI__recommend_model
  - mcp__Fal_AI__get_model_schema
  - mcp__Fal_AI__estimate_cost
  - mcp__Fal_AI__submit_job
  - mcp__Fal_AI__submit_jobs
  - mcp__Fal_AI__wait_for_jobs
  - mcp__Fal_AI__show_media
  - AskUserQuestion
metadata:
  trigger: "Making images, voiceovers, short videos, carousels, social cards or decks for a brand."
  version: "0.1.0"
---

# Creative Studio

One brief in, finished on-brand assets out. The user picks; nothing ships without their yes.

## Standing rules (hold for the whole task)

1. **Brand first.** Every asset follows the brand file. If an asset breaks it, fix or redo it.
2. **Cost gate.** Before any paid call, show the plan with an estimated cost. Batches under
   $1 the user asked for can run; anything over $1, any AI video, and any retry loop wait
   for an explicit yes. Report actual spend at the end.
3. **Draft cheap, finish good.** Drafts use the brand's draft voice and 2–3 image options;
   the final uses the default voice and the chosen image.
4. **Never invent text in images.** Image prompts say "no text, no logos". Look at every
   generated image; regenerate any with invented words or logos. Put real text in the layout.
5. **No fake people, testimonials, numbers or medical claims.** Use real product output.
6. **Never post, publish, email or upload to a live site without an explicit yes** for that
   specific action. Saving files locally is fine.
7. **One submit per job.** Keep fal job handles; read results with `wait_for_jobs`. Never
   resubmit to check a job.

## Subcommands

- `help`: read `references/help.md` and print it.
- `config`: set defaults (brand path, output folder, spend cap) in the preferences file.
- `reset`: delete the preferences file only. Say plainly: "This clears your Creative Studio
  preferences. Your brands and generated assets are not touched."

Preferences: `~/.claude/skills/creative-studio/preferences.md` (format in SKILLS_GUIDE).
Write it after the first successful run.

## 1. Load the brand

Look in order and use the first found:

1. `brand/brand.json` (plus `brand/BRAND.md`) in the current project.
2. `brand_path` from preferences.
3. `~/.claude/skills/creative-studio/brands/<name>.json`.

None found: ask at most 3 questions (name and one line; one accent color plus background;
voice tone) and write a starter `brand.json` from `references/brand-template.json`. Offer to
save it to the project's `brand/` or the personal brands folder.

Say which brand you loaded in one line.

## 2. Plan from the brief

Turn the brief into one short table: asset, format and size (from `brand.formats`), models,
estimated cost. Ask at most one question, and only if the channel is unknown. Example:

| Asset | Format | Models | Est. |
| --- | --- | --- | --- |
| Reel, 25 s | 1080×1920 | 3 images + Sarah voice | ~$0.15 |

Get prices from `estimate_cost` when unsure. Then follow the cost gate.

## 3. Make it

Recipes with exact commands are in `references/recipes.md`. Read the section you need.

- **Image:** `brand.image.endpoint` with `brand.image.style`, `palette_rgb` and the scene +
  `brand.image.prompt_suffix`. Size from the format.
- **Voiceover:** write the script first (spoken length ≈ words ÷ `words_per_minute`), show it,
  then generate with `brand.voiceover.draft`, and `default` for the final. Ask for word
  timestamps when the endpoint supports them; they drive captions.
- **Vertical video:** script → voice → 3–6 scenes (images) → `scripts/assemble.py` builds the
  1080×1920 MP4 with gentle crossfades, slow push-in and burned captions. Hook in the first 2
  seconds. AI video clips (Veo, Kling) only when asked, as short b-roll, after a yes.
- **Carousel / social card / OG card:** an illustration from fal plus real text laid out in
  HTML with the brand fonts and colors, rendered to PNG at the exact size
  (`references/recipes.md#layouts`). One idea per slide; the last slide is the CTA.
- **Deck:** use a deck tool or skill if available (Slides artifact, pptx skill); otherwise
  python-pptx with brand colors and fonts. One message per slide, big type.

Save everything to `creative/out/<YYYY-MM-DD>-<slug>/` (or the configured folder), with
`manifest.json`: brief, brand used, each file, its fal endpoint, inputs, request ID and cost.

## 4. Check before showing

Run the checklist in `references/recipes.md#qa`: brand colors and fonts, no invented text
or logos, captions present and readable, length within the format, claims and copy rules,
file sizes. Fix failures before showing.

## 5. Show and hand off

Show the assets (fal `show_media` for media, or send the files) with a one-line summary and
the actual cost. Offer the next step: variations, another channel, or publishing. Publishing
(site, storage, social) happens only after an explicit yes, using the project's own process.
