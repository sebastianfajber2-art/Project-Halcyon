# Voiceover 1: the one problem isn't the reactor (faceless)

Your voice over photos, project visuals and three short film cutaways. Words follow Script C (`../hook-library/scripts/script-c-one-problem-short.md`).

1. Record `voiceover.txt` in one calm take (about 47 s; leave 1 s of silence at the start and 4 to 5 s at the end).
2. Optional: add your own film clips to `media/` as `film1_reactor.mp4`, `film2_hover.mp4`, `film3_flight.mp4` (2.5 s are used, muted). Set `"in"` in `build_timeline.py` to where each moment starts. Without them, stills stand in.
3. `python docs/content/vo-01-one-problem/build_scenes.py` then `python docs/content/vo-01-one-problem/build_timeline.py`
4. `python docs/content/render_short.py vo-01-one-problem your-voice.m4a`

Photo credits (put them in the description): see the list in `build_scenes.py` frames, all from Wikimedia Commons: Jet suit flyer (ITookSomePhotos, CC BY-SA 4.0), Jetman turbine wind-tunnel test (Patrickhaas, CC BY-SA 3.0), Jetman desert race (Jaguar MENA, CC BY 2.0), Curiosity RTG (NASA / Kim Shiflett, public domain), F-22 Raptor at twilight (US Air Force, public domain).
