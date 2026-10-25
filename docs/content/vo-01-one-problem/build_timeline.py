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
import json
try:
    _tl = json.loads((HERE / "final" / "timeline_final.json").read_text(encoding="utf-8"))
    DUR = {s["id"]: s["end"] - s["start"] for s in _tl["scenes"]}
except Exception:
    DUR = {}


def footage(file, in_s, fallback, text=None, credit=None):
    """A real video clip scene (muted) with a text pop-up and a credit line; the still if the clip is missing."""
    if not (HERE / "media" / file).exists():
        return fallback
    ov = []
    if text:
        ov.append({"file": text, "x": 40, "y": 190, "w": 1000, "start": 0.0, "end": 9.0, "credit": ""})
    if credit:
        ov.append({"file": credit, "x": 40, "y": 1290, "w": 1000, "start": 0.0, "end": 9.0, "credit": ""})
    return {"clip": {"file": f"media/{file}", "in": in_s, "speed": 1.0}, "overlays": ov}



def film(file, still, in_s=0.0, fallback=None):
    if (HERE / "media" / file).exists():
        return {"clip": {"file": f"media/{file}", "in": in_s, "speed": 1.0}}
    if fallback:
        return fallback
    return {"image": still, "motion": {"type": "none", "from": 1.0, "to": 1.0}}


def anim(file, img):
    if (HERE / "media" / file).exists():
        return {"clip": {"file": f"media/{file}", "in": 0.0, "speed": 1.0}}
    return still(img)


def still(img):
    return {"image": img, "motion": {"type": "none", "from": 1.0, "to": 1.0}}


mt.SCENES = [
    {"id": "s01", "start": 0.0, "end": 3.3, **footage("rtg_nasa.webm", 30.0, still("f01.png"), None, "c_nasa.png"),
     "vo": "Everyone says the one problem | stopping a real"},
    {"id": "s02", "start": 3.3, "end": 6.2, **film("film1_reactor.mp4", "f01.png", fallback=footage("rtg_nasa.webm", 30.0 + DUR.get("s01", 2.1), still("f01.png"), None, "c_nasa.png")),
     "vo": "Iron Man suit | is the arc reactor."},
    {"id": "s03", "start": 6.2, "end": 8.8, **footage("rtg_nasa.webm", 30.0 + DUR.get("s01", 2.1) + DUR.get("s02", 2.1), still("f03.png"), "t_notreactor.png", "c_nasa.png"),
     "vo": "I ran the numbers. | It's not."},
    {"id": "s04", "start": 8.8, "end": 12.1, **footage("blackhawk.webm", 11.0, still("f04.png"), "t_hovering.png", "c_cbp.png"),
     "vo": "The real problem is hovering. | Hovering means pushing"},
    {"id": "s05", "start": 12.1, "end": 15.8, **film("film2_hover.mp4", "f04.png", fallback=footage("blackhawk.webm", 11.0 + DUR.get("s04", 1.7), still("f04.png"), "t_hovering.png", "c_cbp.png")),
     "vo": "your whole weight down | through the air, every second."},
    {"id": "s06", "start": 15.8, "end": 20.8, **anim("anim06.mp4", "g06.png"),
     "vo": "My suit burns about five kilograms | of fuel a minute doing that."},
    {"id": "s07", "start": 20.8, "end": 24.6, **film("film3_flight.mp4", "g07.png", fallback=anim("anim07.mp4", "g07.png")),
     "vo": "Flying forward on a wing | burns less than one."},
    {"id": "s08", "start": 24.6, "end": 26.3, **anim("anim08.mp4", "g08.png"),
     "vo": "That's five times less."},
    {"id": "s09", "start": 26.3, "end": 36.2, **anim("anim09.mp4", "g09.png"),
     "vo": "So the fix isn't | a better power source. | It's wings. | They swing back for speed, | open wide to turn, | and tilt up to brake."},
    {"id": "s10", "start": 36.2, "end": 44.2, **footage("x43a_nasa.webm", 70.0, still("f10.png"), "t_hour.png", "c_x43.png"),
     "vo": "With wings, the same suit flies | for about an hour | when launched like a glider. | The reactor can wait."},
    {"id": "s11", "start": 44.2, "end": 47.1, **still("f11.png"),
     "vo": "Follow, | and I'll show you the test."},
]

mt.SFX = [
    {"at": 0.0, "file": "whoosh_short", "gain_db": -14, "why": "opening"},
    {"at": 6.2, "file": "impact_low", "gain_db": -8, "why": "It's not"},
    {"at": 6.2, "file": "media/pop.wav", "gain_db": -6, "why": "NOT THE REACTOR pops up"},
    {"at": 8.8, "file": "whoosh_short", "gain_db": -14, "why": "cut to the turbine"},
    {"at": 8.8, "file": "media/pop.wav", "gain_db": -6, "why": "HOVERING"},
    {"at": 15.8, "file": "whoosh_short", "gain_db": -14, "why": "cut to the numbers"},
    {"at": 15.8, "file": "media/pop.wav", "gain_db": -6, "why": "hover bar"},
    {"at": 20.8, "file": "media/pop.wav", "gain_db": -6, "why": "wing bar"},
    {"at": 24.6, "file": "impact_low", "gain_db": -9, "why": "5x less"},
    {"at": 24.6, "file": "media/pop.wav", "gain_db": -6, "why": "5x LESS"},
    {"at": 26.3, "file": "whoosh_short", "gain_db": -14, "why": "cut to the wing modes"},
    {"at": 26.3, "file": "riser_end", "gain_db": -12, "why": "the fix"},
    {"at": 36.2, "file": "whoosh_short", "gain_db": -14, "why": "cut to the flyer"},
    {"at": 36.2, "file": "media/pop.wav", "gain_db": -6, "why": "1 HOUR"},
    {"at": 44.2, "file": "media/pop.wav", "gain_db": -6, "why": "follow"},
]

mt.MUSIC = [{"start": 0.0, "end": 47.1, "file": "dark_drone", "gain_db": -24, "fade_out": 1.0}]

if __name__ == "__main__":
    mt.main()
