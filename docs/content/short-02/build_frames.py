"""Frames for Short 2: "Can you build a real Iron Man suit?" (1080 x 1920 SVGs).

Reuses the look and helpers of Short 1. Run:
    python docs/content/short-02/build_frames.py
Then render each scene-NN.svg to PNG at 1080 x 1920 (headless Edge or any browser).
Text stays between y = 300 and y = 1400 and clear of the button column (x > 940, y 950-1650).
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "short-01"))
import make_frames as base  # noqa: E402  (Short 1 helpers and flight-view drawing)

frame, text = base.frame, base.text
INK, QUIET, BLUE, ORANGE, RED = base.INK, base.QUIET, base.BLUE, base.ORANGE, base.RED

scenes = {}

# 1  the question and the twist
scenes["scene-01"] = frame(
    text(540, 620, "CAN YOU BUILD", 84, INK, 700, spacing=3)
    + text(540, 720, "A REAL", 84, INK, 700, spacing=3)
    + text(540, 835, "IRON MAN SUIT?", 96, ORANGE, 800, spacing=2)
    + text(540, 1080, "YES.", 170, BLUE, 800)
    + text(540, 1200, "BUT NOT LIKE THE MOVIE.", 52, QUIET, 600, spacing=2)
)

# 2  no arc reactor
crossed_ring = (
    '  <circle cx="540" cy="820" r="240" fill="none" stroke="#5b6f88" stroke-width="26"/>\n'
    '  <polygon points="540,690 650,885 430,885" fill="none" stroke="#5b6f88" stroke-width="14"/>\n'
    '  <circle cx="540" cy="820" r="60" fill="#5b6f88"/>\n'
    f'  <line x1="330" y1="610" x2="750" y2="1030" stroke="{RED}" stroke-width="30" stroke-linecap="round"/>\n'
    f'  <line x1="750" y1="610" x2="330" y2="1030" stroke="{RED}" stroke-width="30" stroke-linecap="round"/>\n'
)
scenes["scene-02"] = frame(
    crossed_ring
    + text(540, 1260, "NO ARC REACTOR", 84, INK, 700, spacing=3)
    + text(540, 1360, "THE REAL SUIT RUNS ON JET FUEL", 40, ORANGE, 700, spacing=1)
)

# 3  six turbines
scenes["scene-03"] = frame(
    text(540, 470, "SIX SMALL JET TURBINES", 56, INK, 700, spacing=2)
    + text(540, 550, "2,440 N OF THRUST", 62, ORANGE, 800, spacing=2)
    + base.FLIGHT_VIEW
    + text(540, 1390, "ENOUGH TO LIFT A PERSON", 44, BLUE, 700, spacing=2)
)


# 4  three wing modes
def wing_icon(cx, cy, span, sweep, chord, flaps=False):
    """Top view of the suit with its wings; sweep > 0 swings the tips back, < 0 forward."""
    root = 22
    right = [(cx + root, cy - 50), (cx + root + span, cy - 50 + sweep),
             (cx + root + span, cy - 50 + sweep + chord), (cx + root, cy + 10)]
    left = [(2 * cx - x, y) for x, y in right]
    pts = lambda p: " ".join(f"{x},{y}" for x, y in p)  # noqa: E731
    out = "".join(f'  <polygon points="{pts(w)}" fill="#3d8bff" fill-opacity="0.9" stroke="#9cc4ff" stroke-width="3"/>\n'
                  for w in (right, left))
    if flaps:
        for w in (right, left):
            (x1, y1), (x2, y2) = w[3], w[2]
            out += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ORANGE}" stroke-width="10" stroke-linecap="round"/>\n'
    out += (f'  <polygon points="{cx - 24},{cy - 64} {cx + 24},{cy - 64} {cx + 30},{cy + 10} {cx + 16},{cy + 90} '
            f'{cx - 16},{cy + 90} {cx - 30},{cy + 10}" fill="#1d2a3d" stroke="#cfe0f5" stroke-width="3"/>\n')
    out += (f'  <polygon points="{cx},{cy - 120} {cx + 22},{cy - 92} {cx + 14},{cy - 66} {cx - 14},{cy - 66} '
            f'{cx - 22},{cy - 92}" fill="#1d2a3d" stroke="#cfe0f5" stroke-width="3"/>\n')
    return out


scenes["scene-04"] = frame(
    text(540, 420, "THREE WING MODES", 66, INK, 800, spacing=3)
    + wing_icon(200, 740, 70, 95, 34)
    + wing_icon(535, 740, 120, 14, 40)
    + wing_icon(870, 740, 120, -16, 40, flaps=True)
    + text(200, 910, "SPEED", 52, BLUE, 800, spacing=2) + text(200, 955, "swept back", 32, QUIET)
    + text(535, 910, "TURN", 52, BLUE, 800, spacing=2) + text(535, 955, "full span", 32, QUIET)
    + text(870, 910, "STOP", 52, ORANGE, 800, spacing=2) + text(870, 955, "airbrake", 32, QUIET)
    + text(540, 1130, "YOU PICK THE MODE,", 40, INK, 700, spacing=1)
    + text(540, 1190, "THE COMPUTER MOVES THE WINGS", 40, INK, 700, spacing=1)
)

# 5  endurance, honestly labelled
scenes["scene-05"] = frame(
    text(540, 560, "ON PAPER", 52, QUIET, 600, spacing=6)
    + text(540, 790, "~20 MIN", 140, BLUE, 800)
    + text(540, 860, "from a standing start", 44, QUIET)
    + text(540, 1090, "60+ MIN", 140, ORANGE, 800)
    + text(540, 1160, "from a glider-style launch", 44, QUIET)
    + text(540, 1330, "simulation numbers, not flown yet", 38, QUIET, 600, spacing=1)
)

# 6  the knee actuator, as a cycloid drive picture
ring_pins = "".join(
    f'  <circle cx="{540 + 215 * math.cos(2 * math.pi * i / 36):.1f}" cy="{980 + 215 * math.sin(2 * math.pi * i / 36):.1f}" '
    'r="11" fill="#9cc4ff"/>\n' for i in range(36))
out_holes = "".join(
    f'  <circle cx="{540 + 140 * math.cos(2 * math.pi * i / 8):.1f}" cy="{980 + 140 * math.sin(2 * math.pi * i / 8):.1f}" '
    f'r="16" fill="#0d1420" stroke="{ORANGE}" stroke-width="5"/>\n' for i in range(8))
knee = (ring_pins
        + '  <circle cx="540" cy="980" r="185" fill="#1d2a3d" stroke="#4f97ff" stroke-width="6"/>\n'
        + out_holes
        + '  <circle cx="540" cy="980" r="75" fill="#0d1420" stroke="#cfe0f5" stroke-width="4"/>\n'
        + '  <circle cx="540" cy="980" r="24" fill="#ff7a1a"/>\n')
scenes["scene-06"] = frame(
    text(540, 480, "THE LEGS GET A ROBOT", 58, INK, 700, spacing=2)
    + text(540, 570, "EXOSKELETON", 80, ORANGE, 800, spacing=3)
    + knee
    + text(540, 1330, "KNEE ACTUATOR: DESIGNED", 46, BLUE, 700, spacing=2)
    + text(540, 1395, "CODE IS OPEN SOURCE", 46, INK, 700, spacing=2)
)

# 7  safety and follow
scenes["scene-07"] = frame(
    '  <image href="../../brand/pfp.png" x="300" y="340" width="480" height="480"/>\n'
    + text(540, 960, "NOTHING GOES ON ME", 64, INK, 800, spacing=2)
    + text(540, 1040, "UNTIL IT'S TESTED", 64, ORANGE, 800, spacing=2)
    + text(540, 1190, "FOLLOW TO WATCH IT HAPPEN", 42, INK, 800, spacing=1)
    + text(540, 1280, "@projectha1cyon", 56, BLUE, 700)
)

if __name__ == "__main__":
    for name, svg in scenes.items():
        (HERE / f"{name}.svg").write_text(svg, encoding="utf-8")
        print("wrote", name + ".svg")
