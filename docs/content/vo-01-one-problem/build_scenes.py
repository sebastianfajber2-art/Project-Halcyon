"""Makes 1080x1920 scene frames from the photos in media/ (blurred fill, photo fitted, credit line,
optional big word). Run before build_timeline.py. Film scenes use your clip if media/film*.mp4
exists; otherwise build_timeline.py falls back to the still made here."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

HERE = Path(__file__).parent
W, H = 1080, 1920
FONT = "C:/Windows/Fonts/segoeuib.ttf"

# name: (source, credit, big word, accent?)
FRAMES = {
    "f01": ("media/curiosity_rtg.jpg", "NASA (public domain)", "", False),
    "f03": ("media/curiosity_rtg.jpg", "NASA (public domain)", "NOT THE REACTOR", True),
    "f04": ("media/jetman_turbine_windtunnel.jpg", "Photo: Patrickhaas, CC BY-SA 3.0", "HOVERING", True),
    "f10": ("media/jet_suit_flyer.jpg", "Photo: ITookSomePhotos, CC BY-SA 4.0", "~1 HOUR (SIMULATION)", True),
    "f11": ("../../brand/pfp.png", "", "@projectha1cyon", True),
}


def text_fit(d, text, max_w, size):
    while size > 30:
        f = ImageFont.truetype(FONT, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(FONT, 30)


def make(name, src, credit, big, accent):
    im = Image.open(HERE / src).convert("RGB")
    bg = im.copy()
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.6)
    fg_scale = min(W / im.width, 1180 / im.height)
    fg = im.resize((int(im.width * fg_scale), int(im.height * fg_scale)), Image.LANCZOS)
    y = (H - fg.height) // 2 - 60
    bg.paste(fg, ((W - fg.width) // 2, y))
    d = ImageDraw.Draw(bg)
    if credit:
        f = ImageFont.truetype(FONT, 28)
        d.text((W // 2, y + fg.height + 24), credit, font=f, fill="#dddddd", anchor="ma", stroke_width=3, stroke_fill="black")
    if big:
        f = text_fit(d, big, 900, 110)
        d.text((W // 2, 250), big, font=f, fill="#ff8a1f" if accent else "white", anchor="mm", stroke_width=8, stroke_fill="black")
    bg.save(HERE / f"{name}.png")


for n, (src, credit, big, acc) in FRAMES.items():
    make(n, src, credit, big, acc)

# ---- graphics drawn for this video (vertical, large text) ----
NAVY, BLUE, ORANGE, WHITE, GREY = "#0b1220", "#3b82f6", "#ff8a1f", "#ffffff", "#8aa0c0"


def font(size):
    return ImageFont.truetype(FONT, size)


def bars(name, show_wing, show_ratio):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 230), "FUEL BURNED PER MINUTE", font=font(70), fill=WHITE, anchor="mm")
    d.text((W // 2, 320), "Project Halcyon design numbers", font=font(38), fill=GREY, anchor="mm")
    base = 1300
    unit = 125  # px per kg
    # hover bar
    d.rounded_rectangle((170, base - 5 * unit, 470, base), radius=14, fill=ORANGE)
    d.text((320, base - 5 * unit - 60), "~5 kg", font=font(90), fill=ORANGE, anchor="mm")
    d.text((320, base + 70), "HOVER", font=font(60), fill=WHITE, anchor="mm")
    if show_wing:
        h = int(0.8 * unit)
        d.rounded_rectangle((610, base - h, 910, base), radius=14, fill=BLUE)
        d.text((760, base - h - 60), "under 1 kg", font=font(76), fill=BLUE, anchor="mm")
        d.text((760, base + 70), "WING", font=font(60), fill=WHITE, anchor="mm")
    d.line((120, base, 960, base), fill=GREY, width=4)
    if show_ratio:
        d.text((760, 820), "5x LESS", font=font(120), fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=NAVY)
    d.text((W // 2, 1730), "@projectha1cyon", font=font(44), fill=GREY, anchor="mm")
    im.save(HERE / f"{name}.png")


def wing_modes(name):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 200), "THREE WING MODES", font=font(70), fill=WHITE, anchor="mm")
    rows = [("SPEED", "swept back", 470), ("TURN", "open wide", 850), ("STOP", "tilted up", 1230)]
    for label, sub, cy in rows:
        d.text((90, cy - 25), label, font=font(96), fill=ORANGE, anchor="lm")
        d.text((90, cy + 55), sub, font=font(46), fill=GREY, anchor="lm")
        cx = 790
        d.rounded_rectangle((cx - 28, cy - 110, cx + 28, cy + 110), radius=24, fill=WHITE)  # body, top view
        if label == "SPEED":
            for sgn in (-1, 1):
                d.polygon([(cx + sgn * 24, cy - 40), (cx + sgn * 150, cy + 150), (cx + sgn * 120, cy + 160), (cx + sgn * 24, cy + 30)], fill=BLUE)
        elif label == "TURN":
            for sgn in (-1, 1):
                d.polygon([(cx + sgn * 24, cy - 50), (cx + sgn * 250, cy - 30), (cx + sgn * 250, cy + 20), (cx + sgn * 24, cy + 20)], fill=BLUE)
        else:
            for sgn in (-1, 1):
                d.polygon([(cx + sgn * 24, cy - 50), (cx + sgn * 230, cy - 60), (cx + sgn * 230, cy + 10), (cx + sgn * 24, cy + 20)], fill=BLUE)
            for k in range(3):  # brake lines
                d.line((cx - 60 + k * 60, cy + 150, cx - 60 + k * 60, cy + 205), fill=ORANGE, width=10)
    d.text((W // 2, 1730), "@projectha1cyon", font=font(44), fill=GREY, anchor="mm")
    im.save(HERE / f"{name}.png")


bars("g06", False, False)
bars("g07", True, False)
bars("g08", True, True)
wing_modes("g09")
print("made frames and graphics")


# ---- transparent overlays for the video-clip scenes (text pops in on top of footage) ----
def overlay_png(name, text, size, color, stroke=8, w=1000, h=None):
    h = h or int(size * 1.6)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = text_fit(d, text, w - 40, size)
    d.text((w // 2, h // 2), text, font=f, fill=color, anchor="mm", stroke_width=stroke, stroke_fill="black")
    im.save(HERE / f"{name}.png")


overlay_png("t_notreactor", "NOT THE REACTOR", 110, ORANGE)
overlay_png("t_hovering", "HOVERING", 120, ORANGE)
overlay_png("t_hour", "~1 HOUR (SIMULATION)", 100, ORANGE)
overlay_png("c_nasa", "NASA (public domain)", 34, "#dddddd", stroke=3, h=60)
overlay_png("c_usaf", "US Air National Guard (public domain)", 34, "#dddddd", stroke=3, h=60)
overlay_png("c_cbp", "US Customs and Border Protection (public domain)", 34, "#dddddd", stroke=3, h=60)
overlay_png("c_x43", "NASA Armstrong (public domain)", 34, "#dddddd", stroke=3, h=60)
print("made overlays")
