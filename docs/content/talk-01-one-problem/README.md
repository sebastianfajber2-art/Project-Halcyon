# Talking Short 1: the one problem isn't the reactor

You talking to camera, with three short film cutaways, captions and text overlays, exported 1080 × 1920. The script and the clip descriptions are in `../hook-library/scripts/script-c-one-problem-short.md`.

## Steps

1. **Film** the script in one take, vertical, with sound (the shot list in the script says where each clip will cut in). Leave a second of silence before you start and a few seconds after.
2. **Get the three film clips** from your own copy and save them in `media/` as `film1_reactor.mp4`, `film2_hover.mp4` and `film3_flight.mp4`. Any length or format works; set `"in"` in `edit.json` to the second where the moment starts, and the editor uses 2.5 seconds from there.
3. **Run the editor:**

   ```bash
   python docs/content/edit_video.py talk-01-one-problem path/to/your-camera-video.mp4 --tighten
   ```

4. The finished video is `final/talk-01-one-problem_final.mp4`. Also written there: `captions_final.srt` (if you'd rather finish in CapCut), `captions_final.ass` and `edit_final.json` (the times it chose).

Before you have the clips, add `--placeholders` to preview the whole edit with test patterns in their place.

## Options

| Option | What it does |
| --- | --- |
| `--tighten` | Cuts pauses longer than half a second down to a short beat (jump cuts). Most talking Shorts want this. Leave it off if you want your natural pauses, for example the beat before "It's not." |
| `--crop-x 0.5` | If the camera video is wide (16:9), where to centre the vertical crop: 0 is the left edge, 1 the right. Use it to keep your face in frame. |
| `--denoise` | Reduces steady room noise in your voice. Try it if the recording has hiss. |
| `--music` | Adds a quiet synthesised music bed under your voice. Off by default; sound effects are always on. |
| `--out NAME` | Name of the output file. |
| `--keep-work` | Keeps the intermediate files. |

## What `edit.json` controls

Everything is placed on your words, not on fixed seconds, so it stays in time however fast you read.

| Field | Meaning |
| --- | --- |
| `lines` | The script cut into lines (`id` and `text`). A `|` in the text marks where one caption ends and the next begins. Keep the words exactly as you say them. |
| `cutaways` | Film clips: `line` and `word` (which word of that line it starts on, counting from 0), `lead` (seconds before that word), `duration`, `file`, `in` (start second inside the clip), `credit` (the on-screen source line). |
| `overlays` | Short words on screen: `line`, `word`, `duration`, `text`, and `"style": "accent"` for orange. They never overlap; a long one is shrunk to fit one line. |
| `sfx` | Sound effects on a word: `impact_low`, `whoosh_short`, `riser_end`, or your own file in `media/`; `gain_db` sets the level. A whoosh is added at every cutaway. |

To move a cutaway earlier or later, change its `word` or `lead`. To make it longer or shorter, change `duration`, but keep the film to 2 to 5 seconds a clip.

## What the editor tells you

When it runs it prints the time of each line, whether the start was found at a real pause or only estimated, and what share of the video is film. Check any "estimated" lines by eye, and heed the warning if film passes a fifth of the video: your commentary should lead.

## Limits

- **It doesn't transcribe.** Captions and overlay timing follow your script, so if you change words, skip a line or reorder lines, edit `lines` to match what you said.
- **It doesn't track your face.** For a wide take use `--crop-x` to centre the crop.
- **Film audio is never used.** Only your voice, the sound effects and the optional music are heard.

## Before you post

1. Upload to YouTube as **Private** first and read the copyright check in YouTube Studio.
2. If a clip is flagged, shorten or replace it and run the editor again.
3. Post to Shorts, then TikTok and Reels once the check is clean.

`media/` and `final/` are git-ignored, so clips and renders never reach the public repository. This is general guidance, not legal advice.
