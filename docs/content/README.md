# Making a Short

Each short lives in its own folder (`short-01`, `short-02`, ...) with its script, scene frames and `timeline.json`. One command turns a voiceover recording into the finished video.

## 1. Record the voice

- Read the short's `voiceover.txt` in one calm take, about 2 to 2.7 words per second. Take a short breath where there are three dots.
- Leave about 1 second of silence at the start and 4 to 5 seconds at the end.
- Any format works: wav, m4a, mp3, or a video file (for example an OBS recording; the audio is used).
- Do 2 or 3 takes and keep the best. If you cleaned it (Adobe Podcast Enhance Speech, CapCut noise reduction), use the cleaned file.

## 2. Render

```bash
python docs/content/render_short.py short-01 path/to/your-voice.m4a
```

Result: `docs/content/short-01/final/short-01_final.mp4` (1080 × 1920, 30 fps). Also written there: `timeline_final.json` and `captions_final.srt` (the re-timed cuts and captions, if you would rather finish the edit in CapCut).

Options: `--no-music` (voice only), `--out NAME` (file name), `--keep-work` (keep the temporary audio files).

What the renderer does:

1. Finds where you speak and where you pause.
2. Puts each scene cut on the pause nearest to where that scene's sentences end, so the pictures follow your voice.
3. Re-times captions, music and sound effects to match.
4. Renders a slow zoom on every frame, burned-in captions (white with a black outline, inside the safe area), your voice levelled, quiet music that ducks under the voice, and a final loudness of about -14 LUFS.

It tells you when a cut is only estimated because no clear pause was found; check those by eye.

## 3. Check before posting

- Watch the whole video with sound on, once on your phone.
- Read the captions against what you actually said; the captions follow the script, so change `vo` in the short's timeline script if you ad-libbed.
- The music and sound effects are synthesised placeholders (nothing to license). If you prefer a platform-library track, render with `--no-music` and add it in the app.
- Post to TikTok, YouTube Shorts and Instagram Reels from the phone app for the best reach.

## Talking to camera, with film cutaways

For videos where you talk to the camera and short film clips cut in, use `edit_video.py` (not `render_short.py`). Your camera video is the base; it adds the cutaways, captions, text overlays and loudness, all timed to what you actually say. The worked example is `talk-01-one-problem/`: read its README, then run

```bash
python docs/content/edit_video.py talk-01-one-problem path/to/camera-video.mp4 --tighten
```

## Videos with your own clips and photos (voiceover over pictures)

`clip-template/` shows how to mix your own video clips, photos and sound files with the project graphics, still with one command to render. Read its README first, especially the rules on using other people's footage.

## Needs

Python 3, `numpy`, and `ffmpeg` on the PATH. Videos and voice recordings are git-ignored and stay on your PC.
