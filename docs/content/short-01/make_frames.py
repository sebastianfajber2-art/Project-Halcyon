"""Generate the 1080x1920 scene frames for Short 1 as SVG files.

Run:  python docs/content/short-01/make_frames.py
Then render each scene-NN.svg to PNG (any browser screenshot at 1080x1920 works;
the repo uses headless Edge). Text stays between y=300 and y=1400 so the
TikTok / Reels buttons never cover it.
"""

from pathlib import Path

OUT = Path(__file__).parent
W, H = 1080, 1920
FONT = "Segoe UI, Arial, sans-serif"
BLUE, ORANGE, RED, INK, QUIET = "#4f97ff", "#ff7a1a", "#ff4a36", "#e9eff7", "#8fa3bd"


def frame(body, defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">
  <defs>
    <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M60 0H0V60" fill="none" stroke="#132033" stroke-width="1"/></pattern>
    {defs}
  </defs>
  <rect width="{W}" height="{H}" fill="#0d1420"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <text x="540" y="250" text-anchor="middle" fill="{QUIET}" font-size="34" letter-spacing="4">PROJECT HALCYON</text>
{body}
</svg>
"""


def text(x, y, s, size, fill=INK, weight=400, anchor="middle", spacing=0):
    return (f'  <text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{spacing}">{s}</text>\n')


scenes = {}

scenes["scene-01"] = frame(
    '  <circle cx="540" cy="800" r="430" fill="url(#heat)"/>\n'
    '  <circle cx="540" cy="800" r="250" fill="none" stroke="#9cc4ff" stroke-width="34" filter="url(#glow)"/>\n'
    '  <circle cx="540" cy="800" r="250" fill="none" stroke="#dff0ff" stroke-width="10"/>\n'
    '  <polygon points="540,640 680,885 400,885" fill="none" stroke="#dff0ff" stroke-width="16" filter="url(#glow)"/>\n'
    '  <circle cx="540" cy="800" r="70" fill="#dff0ff" filter="url(#glow)"/>\n'
    + text(540, 1290, "IT WOULD", 92, INK, 700, spacing=4)
    + text(540, 1400, "COOK HIM ALIVE", 88, ORANGE, 800, spacing=2),
    '<radialGradient id="heat"><stop offset="0" stop-color="#ff4a36" stop-opacity="0.75"/>'
    '<stop offset="1" stop-color="#ff4a36" stop-opacity="0"/></radialGradient>'
    '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>',
)

scenes["scene-02"] = frame(
    text(540, 640, "IN THE MOVIE", 52, QUIET, 600, spacing=6)
    + text(540, 860, "3,000,000,000", 148, INK, 800)
    + text(540, 975, "WATTS", 84, BLUE, 700, spacing=8)
    + text(540, 1110, "every second · from his chest", 50, QUIET),
)

scenes["scene-03"] = frame(
    text(540, 600, "NO MACHINE IS", 66, INK, 700, spacing=3)
    + text(540, 690, "100% EFFICIENT", 66, INK, 700, spacing=3)
    + '  <rect x="180" y="840" width="648" height="140" rx="10" fill="#3d8bff"/>\n'
    + '  <rect x="828" y="840" width="72" height="140" rx="10" fill="#ff7a1a"/>\n'
    + text(180, 1060, "90% useful", 52, BLUE, 700, anchor="start")
    + text(900, 1060, "10% HEAT", 52, ORANGE, 800, anchor="end")
    + text(540, 1230, "even if Tony built the best", 46, QUIET)
    + text(540, 1295, "machine ever made", 46, QUIET),
)

waves = "".join(
    f'  <path d="M{x} 700 q 22 -40 0 -80 q -22 -40 0 -80" fill="none" stroke="{RED}" stroke-width="10" stroke-linecap="round" opacity="0.8"/>\n'
    for x in (380, 470, 560, 650, 740)
)
scenes["scene-04"] = frame(
    waves
    + text(540, 880, "300,000,000 W", 128, RED, 800)
    + text(540, 990, "OF WASTE HEAT", 80, INK, 700, spacing=6)
    + text(540, 1120, "≈ a small power plant,", 52, QUIET)
    + text(540, 1190, "sitting on his ribs", 52, QUIET),
)

scenes["scene-05"] = frame(
    '  <circle cx="540" cy="760" r="300" fill="#ff4a36" fill-opacity="0.85"/>\n'
    + text(540, 780, "300,000,000 W", 70, "#0d1420", 800)
    + '  <circle cx="820" cy="1110" r="4" fill="#9cc4ff"/>\n'
    + '  <path d="M810 1102 L720 1150" stroke="#9cc4ff" stroke-width="3"/>\n'
    + text(700, 1175, "YOUR BODY: 300 W", 50, BLUE, 700, anchor="end")
    + text(540, 1300, "1,000,000× TOO MUCH", 66, ORANGE, 800)
    + text(540, 1370, "to scale, your dot is basically invisible", 40, QUIET),
)

# Top view in flight, same geometry as concept sheet A, without the part balloons.
FLIGHT_VIEW = """
  <g transform="translate(540 1000) scale(1.05) translate(-1925 -740)" stroke-linejoin="miter">
    <polygon points="1981,570 2303,590 2303,716 1981,808" fill="#3d8bff" fill-opacity="0.85" stroke="#9cc4ff" stroke-width="2"/>
    <polygon points="1869,570 1547,590 1547,716 1869,808" fill="#3d8bff" fill-opacity="0.85" stroke="#9cc4ff" stroke-width="2"/>
    <polygon points="1857,590 1837,602 1825,790 1841,814 1853,642" fill="#1d2a3d" stroke="#cfe0f5" stroke-width="2"/>
    <polygon points="1993,590 2013,602 2025,790 2009,814 1997,642" fill="#1d2a3d" stroke="#cfe0f5" stroke-width="2"/>
    <polygon points="1901,830 1921,830 1917,990 1905,1014 1889,990" fill="#1d2a3d" stroke="#cfe0f5" stroke-width="2"/>
    <polygon points="1929,830 1949,830 1961,990 1945,1014 1933,990" fill="#1d2a3d" stroke="#cfe0f5" stroke-width="2"/>
    <polygon points="1869,558 1981,558 1993,630 1973,790 1949,826 1901,826 1877,790 1857,630" fill="#1d2a3d" stroke="#cfe0f5" stroke-width="2"/>
    <polygon points="1925,466 1957,498 1949,542 1901,542 1893,498" fill="#1d2a3d" stroke="#cfe0f5" stroke-width="2"/>
    <rect x="1901" y="634" width="48" height="124" rx="10" fill="#2b3e58" stroke="#ff7a1a" stroke-width="2"/>
    <rect x="1869" y="642" width="24" height="104" rx="6" fill="#5b6f88" stroke="#cfe0f5" stroke-width="2"/>
    <rect x="1957" y="642" width="24" height="104" rx="6" fill="#5b6f88" stroke="#cfe0f5" stroke-width="2"/>
    <rect x="1861" y="882" width="20" height="80" rx="5" fill="#5b6f88" stroke="#cfe0f5" stroke-width="2"/>
    <rect x="1969" y="882" width="20" height="80" rx="5" fill="#5b6f88" stroke="#cfe0f5" stroke-width="2"/>
    <circle cx="1981" cy="582" r="10" fill="#ff7a1a"/><circle cx="1869" cy="582" r="10" fill="#ff7a1a"/>
    <path d="M1881 750 L1881 810 M1969 750 L1969 810 M1871 966 L1871 1020 M1979 966 L1979 1020" stroke="#ff9d57" stroke-width="3" stroke-dasharray="6 8" fill="none"/>
  </g>
"""

scenes["scene-06"] = frame(
    text(540, 470, "SO I'M BUILDING", 62, INK, 700, spacing=3)
    + text(540, 550, "A REAL ONE", 62, ORANGE, 800, spacing=3)
    + FLIGHT_VIEW
    + text(540, 1390, "JET TURBINES · SWING WINGS", 44, BLUE, 700, spacing=2),
)

scenes["scene-07"] = frame(
    '  <image href="../../brand/pfp.png" x="240" y="420" width="600" height="600"/>\n'
    + text(540, 1180, "EVERY NUMBER CHECKED", 58, QUIET, 600, spacing=4)
    + text(540, 1280, "FOLLOW TO SEE IF IT FLIES", 56, INK, 800, spacing=1)
    + text(540, 1370, "@projectha1cyon", 60, BLUE, 700),
)

if __name__ == "__main__":
    for name, svg in scenes.items():
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print("wrote", name + ".svg")
