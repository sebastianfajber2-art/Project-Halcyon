"""Render a finished Short (mp4) from its timeline.json and a voiceover recording.

    python docs/content/render_short.py short-01 path/to/voice.m4a
    options:  --no-music   leave out the synthesised music and effects
              --out NAME   output name (default: <short>_final)
              --keep-work  keep the temporary audio and subtitle files

How it works
  1. The recording is analysed to find where you really speak and pause.
  2. Scene cuts, captions, sound cues and music are re-timed to your voice.
  3. ffmpeg renders 1080x1920 at 30 fps: a slow zoom on each frame, burned-in captions,
     your voice (levelled), music and effects, final loudness -14 LUFS.

The music and effects are synthesised placeholders, so there is nothing to license; swap in a
platform-library track in an editor if you prefer. Needs ffmpeg on the PATH and numpy.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
FPS = 30
FFMPEG = shutil.which("ffmpeg")

# Captions are burned in from an .ass file on a true 1080x1920 canvas, so every number below is in pixels.
# (An .srt file would be laid out on libass's default 384x288 canvas and its sizes would come out wrong.)
ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Arial,72,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,2,140,140,300,1
Style: Credit,Arial,30,&H00D8D8D8,&H000000FF,&H00000000,&H00000000,0,1,0,0,100,100,0,0,1,3,0,1,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Synthesised placeholder sounds (ffmpeg expressions), keyed by the names used in timeline.json.
MUSIC_EXPR = {
    "dark_drone": ("0.5*sin(2*PI*55*t)+0.3*sin(2*PI*82.41*t)+0.2*sin(2*PI*110.4*t)"
                   "+0.12*sin(2*PI*164.8*t)*(0.5+0.5*sin(2*PI*0.2*t))"),
    "uplifting_pulse": ("(0.3*sin(2*PI*110*t)+0.25*sin(2*PI*164.81*t)+0.25*sin(2*PI*220*t)"
                        "+0.2*sin(2*PI*261.63*t)+0.15*sin(2*PI*329.63*t))*(0.7+0.3*sin(2*PI*0.15*t))"
                        "+0.18*sin(2*PI*55*t)*pow(max(0,sin(2*PI*2*t)),3)"),
}
# name -> (lavfi source, filters applied after it, seconds before the cue time that the sound starts)
SFX_SRC = {
    "impact_low": ("aevalsrc='sin(2*PI*(45+40*exp(-12*t))*t)*exp(-4.5*t)':s=48000:d=1.4", "", 0.0),
    "whoosh_short": ("anoisesrc=d=0.8:c=pink:a=0.6:r=48000",
                     "highpass=f=300,lowpass=f=5000,afade=t=in:d=0.4,afade=t=out:st=0.4:d=0.4,", 0.35),
    "riser_end": ("anoisesrc=d=1.4:c=white:a=0.5:r=48000",
                  "highpass=f=1500,afade=t=in:d=1.3,afade=t=out:st=1.3:d=0.1,", 1.3),
}


def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, cwd=cwd)
    if r.returncode != 0:
        sys.exit("ffmpeg failed:\n" + r.stderr.decode(errors="replace")[-3500:])
    return r


# ---------------------------------------------------------------- analysing the voice

def decode_mono(path, sr=16000):
    r = run([FFMPEG, "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"])
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def runs(mask):
    out, s = [], 0
    for i in range(1, len(mask) + 1):
        if i == len(mask) or mask[i] != mask[s]:
            out.append((s, i, bool(mask[s])))
            s = i
    return out


def clean(mask, fill, drop):
    """Bridge pauses shorter than `fill` frames, then drop speech blips shorter than `drop` frames."""
    mask = mask.copy()
    for a, b, v in runs(mask):
        if not v and a > 0 and b < len(mask) and b - a < fill:
            mask[a:b] = True
    for a, b, v in runs(mask):
        if v and b - a < drop:
            mask[a:b] = False
    return mask


def find_speech(voice, step=0.01):
    x = decode_mono(voice)
    n = int(16000 * step)
    m = len(x) // n
    rms = np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(axis=1) + 1e-12)
    db = np.convolve(20 * np.log10(rms), np.ones(5) / 5, mode="same")
    hi, lo = np.percentile(db, 90), np.percentile(db, 10)
    thr = max(lo + 0.4 * (hi - lo), hi - 30)
    mask = clean(db > thr, fill=12, drop=6)
    segs = [(a * step, b * step) for a, b, v in runs(mask) if v]
    if not segs:
        sys.exit("no speech found in the recording")
    return segs, (thr, hi, lo)


def time_at_speech(segs, s):
    acc = 0.0
    for a, b in segs:
        if acc + (b - a) >= s:
            return a + (s - acc)
        acc += b - a
    return segs[-1][1]


def pick_cuts(segs, gaps, fractions):
    """Choose each scene cut: the pause nearest to where the script says the scene should end."""
    total = sum(b - a for a, b in segs)
    cuts, last = [], segs[0][0]
    for f in fractions:
        expected = time_at_speech(segs, f * total)
        best = None
        for ga, gb in gaps:
            c = (ga + gb) / 2
            if c <= last + 1.2 or abs(c - expected) > 1.5:
                continue
            score = abs(c - expected) - 1.5 * min(gb - ga, 0.6)
            if best is None or score < best[0]:
                best = (score, ga, gb)
        if best:
            cut, how = max(best[1] + 0.05, best[2] - 0.12), "pause"
        else:
            cut, how = expected, "estimated"
        if cut < last + 1.2:
            cut, how = last + 1.2, "estimated"
        cuts.append((cut, how))
        last = cut
    return cuts


# ---------------------------------------------------------------- building the files

def srt_time(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def ass_time(t):
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def build_audio(out_dir, short_dir, voice_wav, total, music, sfx, no_music):
    inputs = ["-i", str(voice_wav)]
    chains, mix = [], []
    use_music = bool(music) and not no_music
    if use_music:
        chains.append("[0:a]asplit=2[vo][vsc]")
    else:
        chains.append("[0:a]anull[vo]")
    mix.append("[vo]")
    idx = 1
    if use_music:
        mlabels = []
        for seg in music:
            if seg["file"] not in MUSIC_EXPR:
                print("  warning: unknown music", seg["file"], "- using dark_drone")
            expr = MUSIC_EXPR.get(seg["file"], MUSIC_EXPR["dark_drone"])
            dur = seg["end"] - seg["start"]
            fade = min(seg.get("fade_out", 0.5), dur / 2)
            ms = int(seg["start"] * 1000)
            inputs += ["-f", "lavfi", "-i", f"aevalsrc='{expr}':s=48000:d={dur:.3f}"]
            chains.append(f"[{idx}:a]lowpass=f=600,volume={seg['gain_db']}dB,afade=t=in:d=0.6,"
                          f"afade=t=out:st={dur - fade:.3f}:d={fade:.3f},adelay={ms}|{ms}[m{idx}]")
            mlabels.append(f"[m{idx}]")
            idx += 1
        if len(mlabels) > 1:
            chains.append("".join(mlabels) + f"amix=inputs={len(mlabels)}:normalize=0[music]")
        else:
            chains.append(f"{mlabels[0]}anull[music]")
        chains.append("[music][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[duck]")
        mix.append("[duck]")
    for cue in ([] if no_music else sfx):
        if cue["file"] in SFX_SRC:                       # a built-in synthesised effect
            src, post, lead = SFX_SRC[cue["file"]]
            ms = int(max(0.0, cue["at"] - lead) * 1000)
            inputs += ["-f", "lavfi", "-i", src]
            chains.append(f"[{idx}:a]{post}volume={cue['gain_db']}dB,adelay={ms}|{ms}[s{idx}]")
        elif (short_dir / cue["file"]).exists():         # your own sound file (wav, mp3, ...)
            ms = int(max(0.0, cue["at"]) * 1000)
            inputs += ["-i", str(short_dir / cue["file"])]
            chains.append(f"[{idx}:a]aformat=channel_layouts=mono,volume={cue['gain_db']}dB,"
                          f"adelay={ms}|{ms}[s{idx}]")
        else:
            print("  warning: sound effect not found:", cue["file"], "- skipped")
            continue
        mix.append(f"[s{idx}]")
        idx += 1
    chains.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,"
                  f"loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.9,atrim=end={total:.3f},asetpts=N/SR/TB[a]")
    out = out_dir / "audio.wav"
    run([FFMPEG, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chains), "-map", "[a]",
         "-ac", "2", "-ar", "48000", str(out)])
    return out


def build_video(out_dir, short_dir, scenes, frames):
    """One video stream per scene (a still with slow zoom, or a clip on a blurred fill), photo overlays on
    top, then all scenes joined. Clip audio is never used."""
    inputs, parts, labels, n_in = [], [], [], 0
    for i, (sc, n) in enumerate(zip(scenes, frames)):
        dur = n / FPS
        if sc.get("type") == "clip":
            c = sc["clip"]
            speed = c.get("speed", 1.0)
            path = short_dir / c["file"]
            if not path.exists():
                sys.exit(f"clip not found: {path}")
            inputs += ["-ss", f"{c.get('in', 0):.3f}", "-t", f"{dur * speed + 1:.3f}", "-i", str(path)]
            parts.append(
                f"[{n_in}:v]setpts=(PTS-STARTPTS)/{speed},fps={FPS},split=2[bg{i}][fg{i}];"
                f"[bg{i}]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"boxblur=40:6,eq=brightness=-0.12[bb{i}];"
                f"[fg{i}]scale=1080:-2[ff{i}];"
                f"[bb{i}][ff{i}]overlay=(W-w)/2:(H-h)/2,tpad=stop_mode=clone:stop_duration=3,"
                f"trim=end_frame={n},setpts=PTS-STARTPTS,setsar=1[b{i}]")
        else:
            m = sc.get("motion", {"from": 1.0, "to": 1.0})
            a, b = m["from"], m["to"]
            inputs += ["-i", str(short_dir / sc["src"])]
            parts.append(f"[{n_in}:v]scale=2160:3840:flags=lanczos,"
                         f"zoompan=z='{a}+({b}-{a})*on/{max(n - 1, 1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                         f":d={n}:s=1080x1920:fps={FPS},setsar=1[b{i}]")
        n_in += 1
        cur = f"[b{i}]"
        for k, ov in enumerate(sc.get("overlays", [])):
            path = short_dir / ov["file"]
            if not path.exists():
                sys.exit(f"photo not found: {path}")
            inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(path)]
            parts.append(f"[{n_in}:v]scale={int(ov['w'])}:-2,format=rgba[o{i}_{k}]")
            parts.append(f"{cur}[o{i}_{k}]overlay=x={int(ov['x'])}:y={int(ov['y'])}:"
                         f"enable='between(t,{ov['start']},{ov['end']})'[b{i}_{k}]")
            cur = f"[b{i}_{k}]"
            n_in += 1
        labels.append(cur)
    parts.append("".join(labels) + f"concat=n={len(scenes)}:v=1:a=0,format=yuv420p[vc]")
    parts.append("[vc]subtitles=captions_final.ass[vout]")
    out = out_dir / "video_silent.mp4"
    run([FFMPEG, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[vout]",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", str(FPS), str(out)], cwd=out_dir)
    return out


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("short", help="folder name under docs/content, e.g. short-01")
    ap.add_argument("voice", help="the voiceover recording (wav, m4a, mp3, mp4, mkv ...)")
    ap.add_argument("--out", help="output name without extension")
    ap.add_argument("--no-music", action="store_true")
    ap.add_argument("--keep-work", action="store_true")
    args = ap.parse_args()
    if not FFMPEG:
        sys.exit("ffmpeg not found on the PATH")

    short_dir = HERE / args.short
    tl = json.loads((short_dir / "timeline.json").read_text(encoding="utf-8"))
    scenes = tl["tracks"]["video"]
    vo_scenes = tl["tracks"]["voiceover"]["segments"]
    out_dir = short_dir / "final"
    out_dir.mkdir(exist_ok=True)
    name = args.out or f"{args.short}_final"

    # 1. where does the voice really fall?
    segs, (thr, hi, lo) = find_speech(args.voice)
    gaps = [(segs[i][1], segs[i + 1][0]) for i in range(len(segs) - 1)]
    words = [len(s["text"].split()) for s in vo_scenes]
    fractions = [sum(words[:i + 1]) / sum(words) for i in range(len(words) - 1)]
    cuts = pick_cuts(segs, gaps, fractions)

    t_start = max(0.0, segs[0][0] - 0.2)
    t_end = segs[-1][1] + 0.8
    old = [scenes[0]["start"]] + [s["start"] for s in scenes[1:]] + [scenes[-1]["end"]]
    new_s = [0.0] + [c - t_start for c, _ in cuts] + [t_end - t_start]
    knots = [round(t * FPS) for t in new_s]
    frames = [b - a for a, b in zip(knots, knots[1:])]
    if min(frames) < 15:
        sys.exit("a scene came out shorter than half a second; check the recording against the script")
    total = knots[-1] / FPS
    new = [k / FPS for k in knots]
    tmap = lambda t: float(np.interp(t, old, new))  # noqa: E731

    print(f"voice: speech {segs[0][0]:.2f}-{segs[-1][1]:.2f} s, {len(gaps)} pauses found "
          f"(level {hi:.0f} dB, threshold {thr:.0f} dB)")
    for s, (c, how) in zip(scenes[1:], cuts):
        print(f"  cut to {s['id']} at {c - t_start:6.2f} s  ({how})")
    print(f"video: {total:.1f} s, {sum(frames)} frames")
    if total > 55:
        print("  warning: longer than 55 s; consider a faster read")
    if any(how == "estimated" for _, how in cuts):
        print("  note: some cuts are estimated because no clear pause was found; check them by eye")

    # 2. re-time captions, then snap caption joins to real pauses
    caps = []
    for c in tl["tracks"]["captions"]["lines"]:
        caps.append({"scene": c["scene"], "start": tmap(c["start"]), "end": tmap(c["end"]), "text": c["text"]})
    centers = [((a + b) / 2) - t_start for a, b in gaps]
    for k in range(len(caps) - 1):
        a, b = caps[k], caps[k + 1]
        if a["scene"] != b["scene"]:
            continue
        join = (a["end"] + b["start"]) / 2
        near = [c for c in centers if abs(c - join) <= 0.3]
        if near:
            join = min(near, key=lambda c: abs(c - join))
        a["end"] = b["start"] = join
    for c in caps:
        c["end"] = max(c["end"], c["start"] + 0.5)
    for k in range(len(caps) - 1):
        caps[k]["end"] = min(caps[k]["end"], caps[k + 1]["start"])
    (out_dir / "captions_final.srt").write_text("".join(
        f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n\n"
        for i, c in enumerate(caps, 1)), encoding="utf-8")
    # small source credit above each photo overlay that has one (e.g. "Marvel Studios (still)")
    credits = ""
    for i, sc in enumerate(scenes):
        for ov in sc.get("overlays", []):
            if ov.get("credit"):
                a, b = new[i] + ov["start"], min(new[i] + ov["end"], new[i + 1])
                credits += (f"Dialogue: 1,{ass_time(a)},{ass_time(b)},Credit,,0,0,0,,"
                            f"{{\\an1\\pos({int(ov['x'])},{int(ov['y']) - 8})}}{ov['credit']}\n")
    (out_dir / "captions_final.ass").write_text(ASS_HEADER + "".join(
        f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},Cap,,0,0,0,,{c['text']}\n" for c in caps)
        + credits, encoding="utf-8")

    sfx =[{**c, "at": tmap(c["at"])} for c in tl["tracks"]["sfx"]]
    music = [{**m, "start": tmap(m["start"]), "end": min(tmap(m["end"]), total)} for m in tl["tracks"]["music"]]

    # 3. levelled voice, trimmed to the video
    voice_wav = out_dir / "voice_prepped.wav"
    run([FFMPEG, "-y", "-v", "error", "-ss", f"{t_start:.3f}", "-i", str(args.voice), "-t", f"{total:.3f}",
         "-af", "highpass=f=80,acompressor=threshold=0.1:ratio=3:attack=15:release=250:makeup=2,"
                f"loudnorm=I=-16:TP=-2:LRA=9,apad=whole_dur={total:.3f}",
         "-ac", "1", "-ar", "48000", str(voice_wav)])

    # 4. render
    audio = build_audio(out_dir, short_dir, voice_wav, total, music, sfx, args.no_music)
    video = build_video(out_dir, short_dir, scenes, frames)
    final = out_dir / f"{name}.mp4"
    run([FFMPEG, "-y", "-v", "error", "-i", str(video), "-i", str(audio), "-c:v", "copy", "-c:a", "aac",
         "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(final)])

    final_tl = {"format": {"width": 1080, "height": 1920, "fps": FPS, "duration": total},
                "voice": {"source": str(args.voice), "trim_start": t_start, "duration": total},
                "scenes": [{"id": s["id"], "src": s["src"], "start": new[i], "end": new[i + 1], "frames": frames[i],
                            "motion": s["motion"]} for i, s in enumerate(scenes)],
                "captions": caps, "sfx": sfx, "music": music}
    (out_dir / "timeline_final.json").write_text(json.dumps(final_tl, indent=2, ensure_ascii=False), encoding="utf-8")
    if not args.keep_work:
        for f in (video, audio, voice_wav):
            f.unlink(missing_ok=True)
    print("done:", final, f"({final.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
