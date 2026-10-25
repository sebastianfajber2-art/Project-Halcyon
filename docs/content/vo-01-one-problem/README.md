# Voiceover 1: the one problem isn't the reactor (faceless)

Your voice over photos, project visuals and three short film cutaways. Words follow Script C (`../hook-library/scripts/script-c-one-problem-short.md`).

1. Record `voiceover.txt` in one calm take (about 47 s; leave 1 s of silence at the start and 4 to 5 s at the end).
2. Optional: add your own film clips to `media/` as `film1_reactor.mp4`, `film2_hover.mp4`, `film3_flight.mp4` (2.5 s are used, muted). Set `"in"` in `build_timeline.py` to where each moment starts. Without them, stills stand in.
3. `python docs/content/vo-01-one-problem/build_scenes.py` then `python docs/content/vo-01-one-problem/build_timeline.py`
4. `python docs/content/render_short.py vo-01-one-problem your-voice.m4a`

Credits (put them in the description; the footage and photos live in the git-ignored `media/`, with a full list in `media/CREDITS.md`):

- Video, public domain: NASA / JHUAPL "After 60 Years, Nuclear Power for Spaceflight is Still Tried and True"; George Felton / US Customs and Border Protection, Black Hawk flyover of NRG Stadium; NASA Armstrong, "NASA's X-43A Accelerates Hypersonic Flight".
- Photos used only in earlier test versions (Wikimedia Commons): Jet suit flyer (ITookSomePhotos, CC BY-SA 4.0), Jetman turbine wind-tunnel test (Patrickhaas, CC BY-SA 3.0).

Order of work: render once, then `build_anim.py` (animated graphs, timed from the last render), then render again.
