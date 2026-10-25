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
    "f01": ("media/jet_suit_flyer.jpg", "Photo: ITookSomePhotos, CC BY-SA 4.0", "", False),
    "f02": ("media/curiosity_rtg.jpg", "NASA (public domain)", "", False),
    "f03": ("media/curiosity_rtg.jpg", "NASA (public domain)", "NOT THE REACTOR", True),
    "f04": ("media/jetman_turbine_windtunnel.jpg", "Photo: Patrickhaas, CC BY-SA 3.0", "HOVERING", True),
    "f05": ("media/f22_twilight.jpg", "US Air Force (public domain)", "", False),
    "f06": ("../../brand/concept-sheet-a.png", "Project Halcyon concept sheet", "~5 KG A MINUTE", True),
    "f07": ("media/jetman_desert.jpg", "Photo: Jaguar MENA, CC BY 2.0", "UNDER 1 KG A MINUTE", True),
    "f08": ("media/f22_twilight.jpg", "US Air Force (public domain)", "5x LESS", True),
    "f09": ("../../brand/concept-sheet-a.png", "Project Halcyon concept sheet", "SPEED · TURN · STOP", True),
    "f10": ("media/jetman_desert.jpg", "Photo: Jaguar MENA, CC BY 2.0", "~1 HOUR (SIMULATION)", True),
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
print("made", len(FRAMES), "frames")
