"""Edit timeline for Short 2: "Can you build a real Iron Man suit?"

Reuses the Short 1 engine (make_timeline.py) with this video's scenes. Run:
    python docs/content/short-02/build_timeline.py
In "vo", a | marks where one caption ends and the next begins.
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "short-01"))
import make_timeline as mt  # noqa: E402

mt.OUT = HERE
mt.TITLE = "Short 2: Can you build a real Iron Man suit?"

mt.SCENES = [
    {"id": "s01", "start": 0.0, "end": 6.5, "image": "scene-01.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.08},
     "vo": "Can you build | a real Iron Man suit? | Yes. But not the way | the movie does it."},
    {"id": "s02", "start": 6.5, "end": 13.0, "image": "scene-02.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.05},
     "vo": "No arc reactor. | It would cook you alive. | So the real suit | runs on jet fuel."},
    {"id": "s03", "start": 13.0, "end": 20.0, "image": "scene-03.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.05},
     "vo": "Six small jet turbines | push out about | two and a half thousand newtons. | Enough to lift a person."},
    {"id": "s04", "start": 20.0, "end": 29.0, "image": "scene-04.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.04},
     "vo": "But hovering burns fuel fast, | so the suit has wings. | They swing back for speed, | "
           "open wide to turn, | and tilt up to brake."},
    {"id": "s05", "start": 29.0, "end": 37.0, "image": "scene-05.png",
     "motion": {"type": "zoom_out", "from": 1.08, "to": 1.00},
     "vo": "On paper, that's about twenty minutes | from a standing start, | and over an hour | "
           "from a glider-style launch."},
    {"id": "s06", "start": 37.0, "end": 46.0, "image": "scene-06.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.05},
     "vo": "The legs get a robot exoskeleton | so you can | stand up in it. | I've already designed the knee, | "
           "and the code is open source."},
    {"id": "s07", "start": 46.0, "end": 52.5, "image": "scene-07.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.03},
     "vo": "It's dangerous, so nothing | goes on me until it's tested, | step by step. | Follow to watch it happen."},
]

mt.SFX = [
    {"at": 6.5, "file": "impact_low", "gain_db": -6, "why": "hit on 'No arc reactor'"},
    {"at": 13.0, "file": "whoosh_short", "gain_db": -12, "why": "cut to the suit"},
    {"at": 20.0, "file": "whoosh_short", "gain_db": -12, "why": "cut to the wing modes"},
    {"at": 29.0, "file": "impact_low", "gain_db": -8, "why": "the numbers land"},
    {"at": 37.0, "file": "whoosh_short", "gain_db": -12, "why": "cut to the knee"},
]

mt.MUSIC = [
    {"start": 0.0, "end": 13.0, "file": "dark_drone", "gain_db": -22, "fade_out": 0.4},
    {"start": 13.0, "end": 52.5, "file": "uplifting_pulse", "gain_db": -19, "fade_out": 1.0},
]

if __name__ == "__main__":
    mt.main()
