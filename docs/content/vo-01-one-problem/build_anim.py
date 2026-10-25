"""Animated graphics for scenes s06 to s09: bars that grow, a '5x LESS' pop, wings that move.
Timing follows the scene lengths from the last render (final/timeline_final.json), so run a
render first, then this, then render again. Writes media/anim06.mp4 ... anim09.mp4."""
import json, math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
W, H, FPS = 1080, 1920, 30
FONT = "C:/Windows/Fonts/segoeuib.ttf"
NAVY, BLUE, ORANGE, WHITE, GREY, DIM = "#0b1220", "#3b82f6", "#ff8a1f", "#ffffff", "#8aa0c0", "#3a4a66"
F = {}


def font(n):
    if n not in F:
        F[n] = ImageFont.truetype(FONT, n)
    return F[n]


def ease(x):  # ease-out
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def pop(x):  # overshoot scale 0 -> 1.15 -> 1
    x = min(max(x, 0.0), 1.0)
    return 0 if x == 0 else (1.15 * math.sin(x * math.pi / 0.9 * 0.5) if x < 0.6 else 1.15 - 0.15 * (x - 0.6) / 0.4)


def bars(t, hover_t, wing_t, ratio_t):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 230), "FUEL BURNED PER MINUTE", font=font(70), fill=WHITE, anchor="mm")
    d.text((W // 2, 320), "Project Halcyon design numbers", font=font(38), fill=GREY, anchor="mm")
    base, unit = 1300, 125
    d.line((120, base, 960, base), fill=GREY, width=4)
    d.text((320, base + 70), "HOVER", font=font(60), fill=WHITE, anchor="mm")
    d.text((760, base + 70), "WING", font=font(60), fill=WHITE if wing_t is not None else DIM, anchor="mm")
    k = ease((t - hover_t) / 0.7)
    if k > 0:
        h = int(5 * unit * k)
        d.rounded_rectangle((170, base - h, 470, base), radius=14, fill=ORANGE)
        d.text((320, base - h - 60), f"~{5 * k:.1f} kg" if k < 1 else "~5 kg", font=font(90), fill=ORANGE, anchor="mm")
    if wing_t is not None:
        k = ease((t - wing_t) / 0.5)
        if k > 0:
            h = max(int(0.8 * unit * k), 2)
            d.rounded_rectangle((610, base - h, 910, base), radius=14, fill=BLUE)
            if k > 0.9:
                d.text((760, base - h - 60), "under 1 kg", font=font(76), fill=BLUE, anchor="mm")
    if ratio_t is not None:
        s = pop((t - ratio_t) / 0.4)
        if s > 0.02:
            txt = Image.new("RGBA", (800, 260), (0, 0, 0, 0))
            ImageDraw.Draw(txt).text((400, 130), "5x LESS", font=font(120), fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=NAVY)
            txt = txt.resize((max(int(800 * s), 1), max(int(260 * s), 1)))
            im.paste(txt, (760 - txt.width // 2, 820 - txt.height // 2), txt)
    d.text((W // 2, 1730), "@projectha1cyon", font=font(44), fill=GREY, anchor="mm")
    return im


def wings(d, cx, cy, sweep_deg, length, chord):
    a = math.radians(sweep_deg)
    for sgn in (-1, 1):
        tip_x = cx + sgn * (24 + length * math.cos(a))
        tip_y = cy - 40 + length * math.sin(a)
        d.polygon([(cx + sgn * 24, cy - 40), (tip_x, tip_y), (tip_x - sgn * 0, tip_y + chord * 0.8), (cx + sgn * 24, cy - 40 + chord)], fill=BLUE)


def modes(t, T):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 200), "THREE WING MODES", font=font(70), fill=WHITE, anchor="mm")
    starts = [10 / 24 * T, 15 / 24 * T, 19 / 24 * T]  # "swing back", "open wide", "tilt up" in the script
    rows = [("SPEED", "swept back", 470), ("TURN", "open wide", 850), ("STOP", "tilted up", 1230)]
    for i, (label, sub, cy) in enumerate(rows):
        k = ease((t - starts[i]) / 0.7)
        on = t >= starts[i]
        d.text((90, cy - 25), label, font=font(96), fill=ORANGE if on else DIM, anchor="lm")
        d.text((90, cy + 55), sub, font=font(46), fill=GREY if on else DIM, anchor="lm")
        cx = 790
        d.rounded_rectangle((cx - 28, cy - 110, cx + 28, cy + 110), radius=24, fill=WHITE if on else DIM)
        if i == 0:
            wings(d, cx, cy, 0 + 58 * k, 150 + 0 * k, 70)             # sweeps back
        elif i == 1:
            wings(d, cx, cy, 0, 60 + 190 * k, 60)                     # opens wide
        else:
            wings(d, cx, cy, 0, 210, 30 + 70 * k)                     # chord grows: tilted up into the wind
            if k > 0.3:
                for j in range(3):
                    y0 = cy + 150
                    d.line((cx - 60 + j * 60, y0, cx - 60 + j * 60, y0 + 55 * ease((k - 0.3) / 0.7)), fill=ORANGE, width=10)
    d.text((W // 2, 1730), "@projectha1cyon", font=font(44), fill=GREY, anchor="mm")
    return im


def write(name, seconds, frame_fn):
    out = HERE / "media" / name
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(out)],
                         stdin=subprocess.PIPE)
    for n in range(int(seconds * FPS)):
        p.stdin.write(frame_fn(n / FPS).tobytes())
    p.stdin.close()
    p.wait()


tl = json.loads((HERE / "final" / "timeline_final.json").read_text(encoding="utf-8"))
dur = {s["id"]: s["end"] - s["start"] for s in tl["scenes"]}
pad = 1.5
write("anim06.mp4", dur["s06"] + pad, lambda t: bars(t, 0.25, None, None))
write("anim07.mp4", dur["s07"] + pad, lambda t: bars(t, -9, 0.55 * dur["s07"], None))
write("anim08.mp4", dur["s08"] + pad, lambda t: bars(t, -9, -9, 0.05))
write("anim09.mp4", dur["s09"] + pad, lambda t: modes(t, dur["s09"]))
print({k: round(v, 2) for k, v in dur.items() if k in ("s06", "s07", "s08", "s09")})
