#!/usr/bin/env python3
"""Assemble a calm vertical video: still scenes + voiceover + burned-in captions.

python3 assemble.py --scenes s1.png s2.png s3.png --voice voice.mp3 \
    --captions captions.json --out reel.mp4 [--fonts-dir DIR --font "Instrument Sans"]
    [--size 1080x1920] [--fade 0.5]

captions.json: [{"start": 0.0, "end": 1.8, "text": "Can't start the email?"}, ...]
Without --captions, no captions are burned (the skill should always pass them).
Needs ffmpeg and ffprobe with libass.
"""
import argparse, json, os, subprocess, sys, tempfile


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def ass_time(t):
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def write_ass(captions, path, w, h, font):
    size = round(w * 0.058)
    margin_v = round(h * 0.2)
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV",
        # White text in an opaque-ish dark box (BorderStyle 3), centred in the lower third.
        f"Style: Cap,{font},{size},&H00FFFFFF,&H9918181D,&H9918181D,1,3,18,0,2,90,90,{margin_v}",
        "", "[Events]", "Format: Layer, Start, End, Style, Text",
    ]
    for c in captions:
        text = str(c["text"]).replace("\n", " ").replace("{", "(").replace("}", ")")
        lines.append(f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},Cap,{text}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenes", nargs="+", required=True)
    p.add_argument("--voice", required=True)
    p.add_argument("--captions")
    p.add_argument("--out", required=True)
    p.add_argument("--size", default="1080x1920")
    p.add_argument("--fade", type=float, default=0.5)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--fonts-dir")
    p.add_argument("--font", default="Instrument Sans")
    a = p.parse_args()

    w, h = (int(x) for x in a.size.split("x"))
    total = duration(a.voice) + 0.6  # small tail after the last word
    n = len(a.scenes)
    seg = (total + a.fade * (n - 1)) / n  # each scene's length, overlaps included
    frames = int(seg * a.fps)

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for s in a.scenes:
        cmd += ["-loop", "1", "-t", f"{seg:.3f}", "-i", s]
    cmd += ["-i", a.voice]

    parts = []
    for i in range(n):
        # Cover-crop to the frame, then a slow 4% push-in.
        parts.append(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
            f"scale={w * 2}:{h * 2},zoompan=z='min(1+0.04*on/{frames},1.04)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={a.fps},"
            f"setsar=1,format=yuv420p[v{i}]"
        )
    last = "v0"
    for i in range(1, n):
        offset = i * (seg - a.fade)
        parts.append(f"[{last}][v{i}]xfade=transition=fade:duration={a.fade}:offset={offset:.3f}[x{i}]")
        last = f"x{i}"

    tmp = None
    if a.captions:
        with open(a.captions) as f:
            caps = json.load(f)
        tmp = tempfile.NamedTemporaryFile(suffix=".ass", delete=False)
        tmp.close()
        write_ass(caps, tmp.name, w, h, a.font)
        sub = f"subtitles='{tmp.name}'"
        if a.fonts_dir:
            sub += f":fontsdir='{a.fonts_dir}'"
        parts.append(f"[{last}]{sub}[vout]")
        last = "vout"

    cmd += [
        "-filter_complex", ";".join(parts),
        "-map", f"[{last}]", "-map", f"{n}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", a.out,
    ]
    try:
        subprocess.run(cmd, check=True)
    finally:
        if tmp:
            os.unlink(tmp.name)
    print(json.dumps({"out": a.out, "seconds": round(duration(a.out), 2), "scenes": n}))


if __name__ == "__main__":
    sys.exit(main())
