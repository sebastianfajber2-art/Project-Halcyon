"""Build the edit timeline for Short 1 from one list of scenes.

Writes three files next to this script:
  timeline.json   every cut, motion, caption style and sound cue (for an editor or an editing MCP)
  captions.srt    caption lines, timed from the scene windows
  voiceover.txt   the read-aloud script with scene markers

Edit the SCENES / SFX / MUSIC lists below, then run:
    python docs/content/short-01/make_timeline.py
In "vo", a | marks where one caption ends and the next begins. Caption times are
estimated from word counts; re-time them against the recorded voiceover.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent
TITLE = "Short 1: Iron Man's arc reactor would cook him alive"
FPS, W, H = 30, 1080, 1920


def snap(t):
    """Round to a whole frame at 30 fps."""
    return round(t * FPS) / FPS


SCENES = [
    {"id": "s01", "start": 0.0, "end": 3.0, "image": "scene-01.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.12},
     "vo": "Iron Man's arc reactor | would cook him alive."},
    {"id": "s02", "start": 3.0, "end": 9.0, "image": "scene-02.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.05},
     "vo": "In the movie it makes | three gigajoules every second. | From his chest."},
    {"id": "s03", "start": 9.0, "end": 15.0, "image": "scene-03.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.05},
     "vo": "But no machine | is a hundred percent efficient. | Even at ninety percent..."},
    {"id": "s04", "start": 15.0, "end": 21.0, "image": "scene-04.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.08},
     "vo": "...that's three hundred million | watts of waste heat. | A small power plant, | on his ribs."},
    {"id": "s05", "start": 21.0, "end": 25.5, "image": "scene-05.png",
     "motion": {"type": "zoom_out", "from": 1.10, "to": 1.00},
     "vo": "Your body can get rid of | about three hundred watts."},
    {"id": "s06", "start": 25.5, "end": 34.0, "image": "scene-06.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.06},
     "vo": "So I'm building | a real flying suit. | Rule one: physics wins. | "
           "Jet turbines instead of a reactor. | Wings instead of hovering."},
    {"id": "s07", "start": 34.0, "end": 40.0, "image": "scene-07.png",
     "motion": {"type": "zoom_in", "from": 1.00, "to": 1.03},
     "vo": "Every number is checked. | Follow to see if it flies."},
]

SFX = [
    {"at": 1.6, "file": "impact_low", "gain_db": -6, "why": "hit on 'cook him alive'"},
    {"at": 3.0, "file": "whoosh_short", "gain_db": -12, "why": "cut to the big number"},
    {"at": 16.2, "file": "impact_low", "gain_db": -6, "why": "hit on 'three hundred million'"},
    {"at": 25.5, "file": "riser_end", "gain_db": -8, "why": "music lifts into the suit"},
]

MUSIC = [
    {"start": 0.0, "end": 25.5, "file": "dark_drone", "gain_db": -22, "fade_out": 0.4},
    {"start": 25.5, "end": 40.0, "file": "uplifting_pulse", "gain_db": -18, "fade_out": 1.0},
]

CAPTION_STYLE = {"font": "Segoe UI Bold", "size": 64, "fill": "#ffffff", "outline": "#000000",
                 "outline_px": 6, "x": 540, "y": 1560, "max_width": 760, "max_lines": 2}


def video_entry(s):
    """A scene is a still image (default) or a video clip, optionally with photo overlays.

    image scene:  {"image": "scene-01.png", "motion": {...}}
    clip scene:   {"clip": {"file": "media/x.mp4", "in": 12.0, "speed": 1.0}}   (clip audio is never used)
    overlays:     [{"file": "media/photo.jpg", "x": 60, "y": 520, "w": 360, "start": 0.5, "end": 4.0,
                    "credit": "Marvel Studios (still)"}]   (start/end are seconds from the scene start)
    """
    entry = {"id": s["id"], "src": s.get("image") or s["clip"]["file"],
             "type": "clip" if "clip" in s else "image",
             "start": snap(s["start"]), "end": snap(s["end"]),
             "motion": s.get("motion", {"type": "none", "from": 1.0, "to": 1.0}),
             "transition_in": "cut"}
    if "clip" in s:
        entry["clip"] = s["clip"]
    if s.get("overlays"):
        entry["overlays"] = s["overlays"]
    return entry


def phrases(s):
    return [p.strip().replace("...", "…") for p in s["vo"].split("|")]


def plain(s):
    """The spoken text without caption markers."""
    return " ".join(p.strip() for p in s["vo"].split("|"))


def n_words(text):
    return len(text.split())


def caption_lines():
    """One caption per phrase, spread over the scene's speaking window by word count."""
    out = []
    for s in SCENES:
        lead, tail = (0.1, 0.2) if s["end"] - s["start"] > 3.5 else (0.05, 0.1)
        t0, t1 = s["start"] + lead, s["end"] - tail
        ps = phrases(s)
        per = (t1 - t0) / sum(n_words(p) for p in ps)
        t = t0
        for p in ps:
            end = t + per * n_words(p)
            out.append({"scene": s["id"], "start": snap(t), "end": snap(end), "text": p})
            t = end
    return out


def srt_time(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def check():
    problems = []
    for a, b in zip(SCENES, SCENES[1:]):
        if abs(a["end"] - b["start"]) > 1e-9:
            problems.append(f"gap or overlap between {a['id']} and {b['id']}")
    print(f"{'scene':6} {'time':>12} {'words':>6} {'w/s':>5}")
    for s in SCENES:
        n, d = n_words(plain(s)), s["end"] - s["start"]
        flag = "  too fast" if n / d > 3.0 else ""
        print(f"{s['id']:6} {s['start']:5.1f}-{s['end']:5.1f}s {n:6d} {n / d:5.2f}{flag}")
        if n / d > 3.0:
            problems.append(f"{s['id']} is read at {n / d:.1f} words per second")
        for p in phrases(s):
            if n_words(p) > 6:
                problems.append(f"caption too long in {s['id']}: {p!r}")
    total = sum(n_words(plain(s)) for s in SCENES)
    print(f"total {total} words in {SCENES[-1]['end']:.1f} s = {total / SCENES[-1]['end']:.2f} w/s")
    return problems


def main():
    problems = check()
    if problems:
        raise SystemExit("timeline problems: " + "; ".join(problems))
    caps = caption_lines()
    timeline = {
        "project": f"Project Halcyon, {TITLE}",
        "format": {"width": W, "height": H, "fps": FPS, "duration": SCENES[-1]["end"]},
        "tracks": {
            "video": [video_entry(s) for s in SCENES],
            "voiceover": {"src": "voiceover.wav", "status": "to record",
                          "segments": [{"scene": s["id"], "start": s["start"], "end": s["end"],
                                        "text": plain(s)} for s in SCENES]},
            "captions": {"src": "captions.srt", "style": CAPTION_STYLE, "lines": caps},
            "music": MUSIC,
            "sfx": SFX,
        },
        "notes": [
            "Scene images already contain the on-screen text, so no separate text overlays are needed.",
            "Keep all added graphics inside y = 300..1400 and clear of x > 940 between y = 950 and y = 1650.",
            "Captions sit at y = 1560 (below the scene text, left of the button column).",
            "After recording, trim silences in the voiceover and re-time scene cuts and captions to match.",
            "Music and sfx names are placeholders: use royalty-free or platform-library sounds.",
        ],
    }
    (OUT / "timeline.json").write_text(json.dumps(timeline, indent=2, ensure_ascii=False), encoding="utf-8")

    srt = "".join(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n\n"
                  for i, c in enumerate(caps, 1))
    (OUT / "captions.srt").write_text(srt, encoding="utf-8")

    lines = [f"{TITLE.split(':')[0].upper()}: VOICEOVER SCRIPT",
             f"Read in one take, calm and clear, about 2 to 2.7 words per second (about {SCENES[-1]['end']:.0f} seconds in total).",
             "Take a short breath where there are three dots. Do not read the scene labels or times.", ""]
    for s in SCENES:
        lines += [f"[{s['id']}  {s['start']:.1f}-{s['end']:.1f} s]", plain(s), ""]
    (OUT / "voiceover.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote timeline.json, captions.srt ({len(caps)} lines), voiceover.txt")


if __name__ == "__main__":
    main()
