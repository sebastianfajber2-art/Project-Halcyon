# Clip template: videos with your own clips and photos

Copy this folder to a new name (for example `short-03`), put your files in `media/`, change the scenes in `build_timeline.py`, then:

```bash
python docs/content/short-03/build_timeline.py          # writes timeline.json, captions.srt, voiceover.txt
# record voiceover.txt, then:
python docs/content/render_short.py short-03 your-voice.m4a
```

## What a scene can be

| Scene | How | Notes |
| --- | --- | --- |
| Project graphic | `"image": "../short-01/scene-02.png"` plus a slow zoom | The frames made for the other shorts, or new ones |
| Video clip | `"clip": {"file": "media/clip1.mp4", "in": 12.0}` | `in` is where to start in the source clip, in seconds. Landscape clips are centred on a blurred copy of themselves to fill the vertical frame. The clip's own audio is never used. |
| Photo on top | `"overlays": [{"file": "media/photo.jpg", "x": 60, "y": 1010, "w": 330, "start": 0.4, "end": 5.0, "credit": "Source name"}]` | Seconds are counted from the start of that scene. The credit appears as small text above the photo. |
| Sound effect | in `mt.SFX`: a built-in name (`impact_low`, `whoosh_short`, `riser_end`) or your own file, `"media/pop.wav"` | |

Keep photos in empty parts of a graphic (the template puts one low on the left), clear of the text and of the right-hand button column (x > 940, y 950 to 1650).

## Rules that keep an account safe

- `media/` is git-ignored on purpose: never put copyrighted clips in the public repository.
- Use 2 to 5 seconds of a clip, and only while you are talking about that exact moment.
- The clip's audio is dropped, so the movie's music and dialogue never reach the video; your voice and your own sound effects carry it.
- Your commentary is the video; clips and photos illustrate it. Keep them well under a fifth of the running time.
- Credit the source on screen. It does not grant permission, but it shows the use is commentary.
- Do not add the studio's logos to your branding, and do not suggest they endorse the channel.
- Before posting on YouTube, upload as **Private** and read the copyright check in YouTube Studio first.
- Do not try to disguise clips (flipping, speed tricks, filters) to get past detection. It breaks platform rules and does not help legally.

This is general guidance, not legal advice.

## The stand-in media

The template points at `media/clip_test.mp4`, `media/photo_test.png` and `media/pop_test.wav`: generated test patterns used to prove the pipeline. Replace them with your own files.
