"""Template for a video that mixes your own clips and photos with the project's graphics.

Copy this folder (clip-template -> short-03), put your files in media/, change the scenes below,
then run:   python docs/content/short-03/build_timeline.py

Scene types
  image scene  {"image": "../short-01/scene-02.png", "motion": {"type": "zoom_in", "from": 1.0, "to": 1.05}}
  clip scene   {"clip": {"file": "media/clip1.mp4", "in": 12.0, "speed": 1.0}}
               "in" is where in the source clip to start (seconds). Clip audio is never used.
               Landscape clips are centred on a blurred copy of themselves to fill the vertical frame.
  photo overlay (on any scene)
               {"file": "media/tony.jpg", "x": 60, "y": 520, "w": 360, "start": 0.5, "end": 4.0,
                "credit": "Marvel Studios (still)"}   start/end are seconds from the scene start

In "vo", a | marks where one caption ends and the next begins.
Sound effects: a built-in name (impact_low, whoosh_short, riser_end) or your own file, e.g. "media/pop.wav".

media/ is git-ignored so copyrighted material never reaches the public repository.
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "short-01"))
import make_timeline as mt  # noqa: E402

mt.OUT = HERE
mt.TITLE = "Clip template: Is Iron Man's flight realistic?"

mt.SCENES = [
    {"id": "s01", "start": 0.0, "end": 4.5,
     "clip": {"file": "media/clip_test.mp4", "in": 1.0, "speed": 1.0},
     "vo": "Iron Man flies faster than sound. | But is that realistic?"},
    {"id": "s02", "start": 4.5, "end": 10.5, "image": "../short-01/scene-02.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.05},
     "overlays": [{"file": "media/photo_test.png", "x": 60, "y": 1010, "w": 330, "start": 0.4, "end": 5.0,
                   "credit": "Test photo (stand-in)"}],
     "vo": "Here's the problem. | Tony Stark's suit would need | a power source that doesn't exist."},
    {"id": "s03", "start": 10.5, "end": 15.0, "image": "../short-01/scene-07.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.03},
     "vo": "So I'm building the real thing. | Follow along."},
]

mt.SFX = [
    {"at": 0.0, "file": "whoosh_short", "gain_db": -12, "why": "opening"},
    {"at": 4.5, "file": "media/pop_test.wav", "gain_db": -10, "why": "your own sound file"},
    {"at": 10.5, "file": "impact_low", "gain_db": -8, "why": "the turn to the project"},
]

mt.MUSIC = [
    {"start": 0.0, "end": 15.0, "file": "dark_drone", "gain_db": -22, "fade_out": 1.0},
]

if __name__ == "__main__":
    mt.main()
