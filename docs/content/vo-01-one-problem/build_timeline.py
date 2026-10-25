"""Voiceover video 1: the one problem isn't the reactor (faceless). Words follow Script C.
Run build_scenes.py first, then this. Film scenes (2.5 s, muted) use media/film1_reactor.mp4,
film2_hover.mp4, film3_flight.mp4 if you put them there; otherwise a still stands in."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "short-01"))
import make_timeline as mt  # noqa: E402

mt.OUT = HERE
mt.TITLE = "Voiceover 1: the one problem isn't the reactor"

CREDIT_FILM = "Iron Man (2008), Marvel Studios"


def film(file, still, in_s=0.0):
    if (HERE / "media" / file).exists():
        return {"clip": {"file": f"media/{file}", "in": in_s, "speed": 1.0}}
    return {"image": still, "motion": {"type": "zoom_in", "from": 1.0, "to": 1.04}}


def still(img):
    return {"image": img, "motion": {"type": "zoom_in", "from": 1.0, "to": 1.05}}


mt.SCENES = [
    {"id": "s01", "start": 0.0, "end": 3.3, **still("f01.png"),
     "vo": "Everyone says the one problem | stopping a real"},
    {"id": "s02", "start": 3.3, "end": 6.2, **film("film1_reactor.mp4", "f02.png"),
     "vo": "Iron Man suit | is the arc reactor."},
    {"id": "s03", "start": 6.2, "end": 8.8, **still("f03.png"),
     "vo": "I ran the numbers. | It's not."},
    {"id": "s04", "start": 8.8, "end": 12.1, **still("f04.png"),
     "vo": "The real problem is hovering. | Hovering means pushing"},
    {"id": "s05", "start": 12.1, "end": 15.8, **film("film2_hover.mp4", "f05.png"),
     "vo": "your whole weight down | through the air, every second."},
    {"id": "s06", "start": 15.8, "end": 20.8, **still("f06.png"),
     "vo": "My suit burns about five kilograms | of fuel a minute doing that."},
    {"id": "s07", "start": 20.8, "end": 24.6, **film("film3_flight.mp4", "f07.png"),
     "vo": "Flying forward on a wing | burns less than one."},
    {"id": "s08", "start": 24.6, "end": 26.3, **still("f08.png"),
     "vo": "That's five times less."},
    {"id": "s09", "start": 26.3, "end": 36.2, **still("f09.png"),
     "vo": "So the fix isn't | a better power source. | It's wings. | They swing back for speed, | open wide to turn, | and tilt up to brake."},
    {"id": "s10", "start": 36.2, "end": 44.2, **still("f10.png"),
     "vo": "With wings, the same suit flies | for about an hour | when launched like a glider. | The reactor can wait."},
    {"id": "s11", "start": 44.2, "end": 47.1, **still("f11.png"),
     "vo": "Follow, | and I'll show you the test."},
]

mt.SFX = [
    {"at": 3.3, "file": "whoosh_short", "gain_db": -12, "why": "film 1"},
    {"at": 6.2, "file": "impact_low", "gain_db": -8, "why": "It's not"},
    {"at": 12.1, "file": "whoosh_short", "gain_db": -12, "why": "film 2"},
    {"at": 20.8, "file": "whoosh_short", "gain_db": -12, "why": "film 3"},
    {"at": 26.3, "file": "riser_end", "gain_db": -12, "why": "the fix"},
]

mt.MUSIC = [{"start": 0.0, "end": 47.1, "file": "dark_drone", "gain_db": -24, "fade_out": 1.0}]

if __name__ == "__main__":
    mt.main()
