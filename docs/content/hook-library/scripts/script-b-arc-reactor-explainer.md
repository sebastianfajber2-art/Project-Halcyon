# Script B (about 2.5 minutes): how the arc reactor would work, and why it can't

**Format from:** H2, "How the Arc Reactor Works" (spectacle, then what's inside, then "why we can't build one (yet)", then behind the scenes).
**Title options:** "How Iron Man's arc reactor would work (and why it can't)" / "The arc reactor problem nobody talks about"
**Hook pattern:** size versus power: a palm-sized object against a power-station number.
**Changes from the source:** the physics is your own (heat, not output, is the real wall), and the "behind the scenes" chapter shows the open-source check you actually ran.

Read at about 2.4 words per second. `|` marks where a caption ends.

## The reactor in action (0:00)

A glowing ring in his chest | that powers a flying suit. | In the movie it makes three gigajoules every second. | That's three billion watts, | from something you could hold in your hand.

*Visual: the reactor ring from Short 1, with the number counting up.*

## What would be inside (0:25)

So what would it take? | There are only a few real options. | Fusion: | real fusion machines are being built right now, | and the smallest serious designs are metres across, | because a small plasma loses heat faster than it makes it. | And the cleanest fuel needs more than a billion degrees. | A nuclear battery: | NASA runs probes on plutonium batteries | that make about half a watt of heat per gram. | A chest-sized one gives tens of watts of electricity. | A palm-sized ring making billions of watts | isn't on that list.

## Why we can't build one, yet (1:20)

But output isn't even the real problem. Heat is. | No machine is perfectly efficient. | Say this one is ninety percent efficient. | The other ten percent of three billion watts | is three hundred million watts of heat, | inside your chest. | Your body can get rid of about three hundred watts. | That's a million times too much. | So the reactor wouldn't power the suit. | It would cook the pilot.

## How I checked (2:00)

I didn't trust my head, | so I put the numbers into a design document and a simulation | and put the code online. | The result: instead of a reactor, | the suit I'm building runs on jet fuel, | with wings so it doesn't have to hover. | The link's below. | Next: the first real test.

## Facts to keep exact

| Claim | Source |
| --- | --- |
| "Three gigajoules per second" | Spoken in the 2008 film |
| 300 MW of heat at 90% efficiency | 10% of 3 GW; Short 1 fact check |
| About 300 W the body can shed | Short 1 fact check (a resting person produces about 100 W; hard work can reach about 1 kW) |
| Plutonium-238 about half a watt of heat per gram (0.57 W/g) | Verified 25 Oct 2026: [Wikipedia, Plutonium-238](https://en.wikipedia.org/wiki/Plutonium-238) and a [US Department of Energy briefing](https://www.energy.gov/sites/default/files/NEGTN0NEAC_PU-238_042108.pdf). One National Academies table lists 0.40 W/g, probably for a different fuel form. |
| Proton-boron needs more than a billion degrees | Verified: published studies work at ion temperatures of about 75 to 500 keV (1 keV is about 11.6 million kelvin), for example [Ochs et al., Physics of Plasmas, 2026](https://w3.pppl.gov/~fisch/fischpapers/2026/Ochs.Bremsstrahlung.POP2026.pdf) |
| Fusion machines "metres across" and "a small plasma loses heat faster" | **Not yet verified in this project.** Check a source (company machine sizes, plasma confinement basics) before filming, or soften to "room-sized". |
| Chest-sized plutonium battery gives "tens of watts" | My own estimate: about 450 g × 0.57 W/g ≈ 250 W of heat, times about 25% conversion ≈ 60 W. Say "tens of watts" and show the sum. |
| Chapters | 0:00 In action, 0:25 What's inside, 1:20 Why we can't (yet), 2:00 How I checked |
