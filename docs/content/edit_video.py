"""Edit a talking-to-camera video: film cutaways, captions, overlays and loudness, exported 9:16.

    python docs/content/edit_video.py <project-folder> <camera-video>
    options:  --out NAME        output name (default <project>_final)
              --tighten         cut long pauses down to a short beat (jump cuts)
              --crop-x 0.5      for wide camera video, where to centre the 9:16 crop (0 left, 1 right)
              --denoise         reduce steady room noise in the voice
              --music           add a quiet synthesised music bed under the voice
              --placeholders    use test patterns for film clips that are missing, to preview the edit
              --keep-work       keep the intermediate files

The project folder holds edit.json (the script split into lines, with cutaways, overlays and sound cues
anchored to words) and a media/ folder for the film clips (git-ignored).

How it works
  1. Your camera video becomes the base: trimmed to the speech, optionally jump-cut, cropped to 1080 x 1920.
  2. Your voice is analysed to find where each script line really starts, then the words inside each line.
  3. Cutaways, overlays, captions and sound cues are placed on those real times.
  4. ffmpeg renders the picture (cutaways on a blurred fill, captions and text burned in) and the sound
     (your voice levelled, sound effects, optional music, loudness about -14 LUFS).

The film clips' own sound is never used. Needs ffmpeg and ffprobe on the PATH, plus numpy.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from render_short import (FFMPEG, FPS, build_audio, find_speech, pick_cuts, run, srt_time,  # noqa: E402
                          ass_time)

FFPROBE = shutil.which("ffprobe")
ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Arial,72,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,2,140,140,300,1
Style: Big,Arial,92,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,7,0,2,100,100,520,1
Style: Accent,Arial,92,&H001A7AFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,7,0,2,100,100,520,1
Style: Credit,Arial,30,&H00D8D8D8,&H000000FF,&H00000000,&H00000000,0,1,0,0,100,100,0,0,1,3,0,1,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def probe(path):
    r = run([FFPROBE, "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
             "-of", "json", str(path)])
    d = json.loads(r.stdout)
    video = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    has_audio = any(s["codec_type"] == "audio" for s in d["streams"])
    return video, has_audio, float(d["format"]["duration"])


def make_chunks(segs, duration, tighten):
    """Source-time intervals to keep: the speech with a little room, optionally with long pauses shortened."""
    lead, tail = 0.25, 0.6
    first = max(0.0, segs[0][0] - lead)
    if not tighten:
        return [(first, min(duration, segs[-1][1] + tail))]
    max_gap, beat = 0.55, 0.28
    chunks, a, prev_end = [], first, segs[0][1]
    for s0, s1 in segs[1:]:
        if s0 - prev_end > max_gap:
            chunks.append((a, prev_end + beat * 0.55))
            a = s0 - beat * 0.45
        prev_end = s1
    chunks.append((a, min(duration, prev_end + tail)))
    return chunks


def make_base(cam, out_dir, chunks, crop_x):
    inputs = ["-i", str(cam)]
    parts = []
    for i, (a, b) in enumerate(chunks):
        parts.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}]")
    parts.append("".join(f"[v{i}][a{i}]" for i in range(len(chunks))) + f"concat=n={len(chunks)}:v=1:a=1[cv][ca]")
    parts.append(f"[cv]scale=1080:1920:force_original_aspect_ratio=increase,"
                 f"crop=w=1080:h=1920:x='(in_w-out_w)*{crop_x}':y='(in_h-out_h)/2',fps={FPS},format=yuv420p[v]")
    parts.append("[ca]aresample=48000[a]")
    out = out_dir / "base.mp4"
    run([FFMPEG, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-c:a", "aac", "-b:a", "256k", str(out)])
    return out


class Line:
    def __init__(self, spec):
        self.id = spec["id"]
        self.phrases = [p.strip() for p in spec["text"].split("|")]
        self.n = sum(len(p.split()) for p in self.phrases)
        self.t0 = self.t1 = 0.0
        self.how = "pause"

    def word_time(self, segs, k):
        """Time at which word k of this line is spoken, interpolating over the speech (not the pauses) in its span."""
        k = max(0, min(k, self.n))
        inside = [(max(a, self.t0), min(b, self.t1)) for a, b in segs if b > self.t0 and a < self.t1]
        inside = [(a, b) for a, b in inside if b > a]
        total = sum(b - a for a, b in inside)
        if total <= 0:
            return self.t0 + (self.t1 - self.t0) * k / max(self.n, 1)
        target = total * k / max(self.n, 1)
        acc = 0.0
        for a, b in inside:
            if acc + (b - a) >= target:
                return a + (target - acc)
            acc += b - a
        return inside[-1][1]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", help="folder under docs/content containing edit.json")
    ap.add_argument("camera", help="your talking video (mp4, mov, mkv ...)")
    ap.add_argument("--out")
    ap.add_argument("--tighten", action="store_true")
    ap.add_argument("--crop-x", type=float, default=0.5)
    ap.add_argument("--denoise", action="store_true")
    ap.add_argument("--music", action="store_true")
    ap.add_argument("--placeholders", action="store_true")
    ap.add_argument("--keep-work", action="store_true")
    args = ap.parse_args()
    if not FFMPEG or not FFPROBE:
        sys.exit("ffmpeg and ffprobe must be on the PATH")

    proj = Path(args.project)
    if not proj.exists():
        proj = Path(__file__).parent / args.project
    spec = json.loads((proj / "edit.json").read_text(encoding="utf-8"))
    out_dir = proj / "final"
    out_dir.mkdir(exist_ok=True)
    name = args.out or f"{proj.name}_final"
    cam = Path(args.camera)
    if not cam.exists():
        sys.exit(f"camera video not found: {cam}")
    video, has_audio, duration = probe(cam)
    if not video or not has_audio:
        sys.exit("the camera file needs both a picture and sound")

    # 1. base video
    segs0, _ = find_speech(cam)
    chunks = make_chunks(segs0, duration, args.tighten)
    base = make_base(cam, out_dir, chunks, args.crop_x)
    _, _, total = probe(base)
    segs, (thr, hi, lo) = find_speech(base)
    print(f"camera: {video['width']}x{video['height']}, {duration:.1f} s; base {total:.1f} s "
          f"({len(chunks)} piece{'s' if len(chunks) > 1 else ''}{', jump-cut' if args.tighten else ''})")

    # 2. line times from the voice
    lines = [Line(s) for s in spec["lines"]]
    by_id = {l.id: l for l in lines}
    gaps = [(segs[i][1], segs[i + 1][0]) for i in range(len(segs) - 1)]
    words = [l.n for l in lines]
    fractions = [sum(words[:i + 1]) / sum(words) for i in range(len(words) - 1)]
    cuts = pick_cuts(segs, gaps, fractions)
    starts = [segs[0][0]] + [c for c, _ in cuts]
    for i, l in enumerate(lines):
        l.t0 = starts[i]
        l.t1 = starts[i + 1] if i + 1 < len(lines) else segs[-1][1]
        l.how = "start" if i == 0 else cuts[i - 1][1]
        print(f"  {l.id}: {l.t0:6.2f} to {l.t1:6.2f} s  ({l.how})")
    if any(l.how == "estimated" for l in lines):
        print("  note: some line starts are estimated because no clear pause was found; check them by eye")

    def when(ev, lead_default=0.0):
        l = by_id.get(ev["line"])
        if l is None:
            sys.exit(f"edit.json refers to an unknown line: {ev['line']}")
        return max(0.0, l.word_time(segs, ev.get("word", 0)) - ev.get("lead", lead_default))

    # 3. events on real times
    cutaways, overlays, sfx, ass_lines = [], [], [], []
    last_end = 0.0
    for ev in spec.get("cutaways", []):
        t = when(ev)
        d = float(ev.get("duration", 2.5))
        t = max(t, last_end + 0.1)
        d = min(d, total - t - 0.1)
        path = proj / ev["file"]
        status = "found"
        if not path.exists():
            if not args.placeholders:
                sys.exit(f"film clip not found: {path}\n(put your clip there, or use --placeholders to preview the edit)")
            status = "PLACEHOLDER"
        cutaways.append({**ev, "start": t, "duration": d, "status": status})
        last_end = t + d
        if ev.get("whoosh", True):
            sfx.append({"at": t, "file": "whoosh_short", "gain_db": -14})
        if ev.get("credit"):
            label = ev["credit"] + (f"  [placeholder: {ev['file']}]" if status == "PLACEHOLDER" else "")
            ass_lines.append(f"Dialogue: 1,{ass_time(t)},{ass_time(t + d)},Credit,,0,0,0,,"
                             f"{{\\an1\\pos(60,1470)}}{label}")
    film = sum(c["duration"] for c in cutaways)
    print(f"cutaways: {len(cutaways)}, {film:.1f} s of {total:.1f} s = {100 * film / total:.0f}% of the video")
    if film / total > 0.2:
        print("  warning: more than a fifth of the video is film; keep your commentary leading")
    for c in cutaways:
        if c["duration"] > 5:
            print(f"  warning: the clip at {c['start']:.1f} s is over 5 s; shorter is safer")

    for ev in spec.get("overlays", []):
        overlays.append({**ev, "start": when(ev), "duration": float(ev.get("duration", 2.0))})
    overlays.sort(key=lambda o: o["start"])
    for a, b in zip(overlays, overlays[1:]):             # one overlay on screen at a time
        if a["start"] + a["duration"] > b["start"] - 0.05:
            a["duration"] = max(0.3, b["start"] - 0.05 - a["start"])
    for o in overlays:
        style = "Accent" if o.get("style") == "accent" else "Big"
        size = min(92, int(840 / (0.62 * max(len(o["text"]), 1))))     # long text shrinks to stay on one line
        pop = f"{{\\fad(90,90)\\fs{size}\\t(0,140,\\fscx112\\fscy112)\\t(140,260,\\fscx100\\fscy100)}}"
        ass_lines.append(f"Dialogue: 2,{ass_time(o['start'])},{ass_time(o['start'] + o['duration'])},{style},,0,0,0,,"
                         f"{pop}{o['text']}")

    for ev in spec.get("sfx", []):
        sfx.append({"at": when(ev) + ev.get("offset", 0.0), "file": ev["file"], "gain_db": ev.get("gain_db", -10)})

    # captions: one per phrase, timed from the word positions
    caps = []
    for l in lines:
        k = 0
        spans = []
        for p in l.phrases:
            spans.append((k, k + len(p.split())))
            k += len(p.split())
        for (a, b), p in zip(spans, l.phrases):
            s = l.word_time(segs, a) - 0.04
            e = l.word_time(segs, b) + (0.0 if b < l.n else 0.2)
            caps.append({"line": l.id, "start": max(0.0, s), "end": e, "text": p})
    for i in range(len(caps) - 1):
        caps[i]["end"] = min(max(caps[i]["end"], caps[i]["start"] + 0.5), caps[i + 1]["start"])
    for c in caps:
        ass_lines.append(f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},Cap,,0,0,0,,{c['text']}")
    (out_dir / "captions_final.ass").write_text(ASS_HEADER + "\n".join(ass_lines) + "\n", encoding="utf-8")
    (out_dir / "captions_final.srt").write_text("".join(
        f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n\n" for i, c in enumerate(caps, 1)),
        encoding="utf-8")

    # 4. picture
    inputs = ["-i", str(base)]
    parts, cur = [], "[0:v]"
    for i, c in enumerate(cutaways):
        d, T = c["duration"], c["start"]
        speed = c.get("speed", 1.0)
        n = i + 1
        if c["status"] == "PLACEHOLDER":
            inputs += ["-f", "lavfi", "-i", f"testsrc2=size=1920x1080:rate={FPS}:duration={d + 1:.2f}"]
        else:
            inputs += ["-ss", f"{c.get('in', 0):.3f}", "-t", f"{d * speed + 1:.3f}", "-i", str(proj / c["file"])]
        parts.append(
            f"[{n}:v]setpts=(PTS-STARTPTS)/{speed},fps={FPS},split=2[cb{i}][cf{i}];"
            f"[cb{i}]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"boxblur=40:6,eq=brightness=-0.12[cbb{i}];[cf{i}]scale=1080:-2[cff{i}];"
            f"[cbb{i}][cff{i}]overlay=(W-w)/2:(H-h)/2,tpad=stop_mode=clone:stop_duration=3,"
            f"trim=duration={d:.3f},setpts=PTS-STARTPTS+{T:.3f}/TB[c{i}]")
        parts.append(f"{cur}[c{i}]overlay=eof_action=pass:enable='between(t,{T:.3f},{T + d:.3f})'[o{i}]")
        cur = f"[o{i}]"
    parts.append(f"{cur}subtitles=captions_final.ass[vout]")
    video_only = out_dir / "video_silent.mp4"
    run([FFMPEG, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[vout]",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", str(FPS), "-pix_fmt", "yuv420p",
         str(video_only)], cwd=out_dir)

    # 5. sound
    voice = out_dir / "voice_prepped.wav"
    chain = "highpass=f=80," + ("afftdn=nr=12:nf=-30," if args.denoise else "") + \
            "acompressor=threshold=0.1:ratio=3:attack=15:release=250:makeup=2,loudnorm=I=-16:TP=-2:LRA=9"
    run([FFMPEG, "-y", "-v", "error", "-i", str(base), "-vn", "-af", chain, "-ac", "1", "-ar", "48000", str(voice)])
    music = [{"start": 0.0, "end": total, "file": "dark_drone", "gain_db": -26, "fade_out": 1.0}] if args.music else []
    audio = build_audio(out_dir, proj, voice, total, music, sfx, False)

    final = out_dir / f"{name}.mp4"
    run([FFMPEG, "-y", "-v", "error", "-i", str(video_only), "-i", str(audio), "-c:v", "copy", "-c:a", "aac",
         "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(final)])
    (out_dir / "edit_final.json").write_text(json.dumps(
        {"duration": total, "lines": [{"id": l.id, "start": l.t0, "end": l.t1, "how": l.how} for l in lines],
         "cutaways": cutaways, "overlays": overlays, "sfx": sfx, "captions": caps},
        indent=2, ensure_ascii=False), encoding="utf-8")
    if not args.keep_work:
        for f in (base, video_only, audio, voice):
            f.unlink(missing_ok=True)
    print("done:", final, f"({final.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
