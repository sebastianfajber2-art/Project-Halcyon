# Script A (long video, about 4.5 minutes): grade the suit system by system

**Format from:** H1, "Why we can't build an iron man suit in real life" (reality check with a verdict per system).
**Title options:** "I graded Iron Man's suit with real numbers: 5 of 6 are possible" / "Can you really build an Iron Man suit? I checked every system"
**Thumbnail idea:** the six systems as a scoreboard with ticks and one red cross on the arc reactor.
**Changes from the source:** the hook and the question arrive in the first 15 seconds with the open loop ("the sixth is the one in his chest"); no subscribe plug before the first verdict; every verdict uses a number from the Halcyon design document, not a general analogy.

Read at about 2.4 words per second. `|` marks where a caption ends.

## Hook (0:00)

Everyone who watches Iron Man wonders | if you could actually build the suit. | I've spent weeks designing one | with real physics, real parts and real numbers. | Today I'll grade every system in it, one by one. | Five of the six can work. | The sixth is the one in his chest.

*Visual: the six systems appear as an empty scoreboard, then fill in during the video.*

## 1. JARVIS (about 0:20)

First, JARVIS. | A voice assistant that reads the suit's sensors and talks back | is possible today, | and I'm planning one in the helmet. | But there's a rule: the AI never flies the suit. | Flight control runs on three separate computers that vote, | and nothing can change their code in the air. | If JARVIS crashes, the suit keeps flying. | **Verdict: possible, but he's not the pilot.**

## 2. Flight (about 1:05)

Flight. | Six small jet turbines give 2,440 newtons of thrust. | The suit with me inside weighs 177 kilograms, | so it can lift off. | The problem is fuel. | Hovering burns about five kilograms a minute. | Flying forward on a wing burns less than one, | five times less. | So the real suit has wings: | they swing back for speed, open wide to turn, | and tilt up to brake. | On paper that's about twenty minutes from a standing start | and over an hour from a glider-style launch. | **Verdict: possible, but minutes of hovering, not hours.**

## 3. Repulsors (about 2:00)

Repulsors. | In the movie they're energy beams. | In real life a repulsor is just a thruster: | it pushes air one way and you move the other. | Mine are 120 newtons each, on the arms, for steering, not lifting. | **Verdict: real, but a lot less magical.**

## 4. Armor (about 2:35)

Armor. | My faceted carbon shell weighs eight kilograms. | It protects against scrapes, not bullets, | because stopping bullets means more weight, | and the engines have to lift every kilo. | **Verdict: a trade-off, not a superpower.**

## 5. Strength (about 3:05)

Strength. | Lifting heavy things needs a robot skeleton. | I've designed the knee: | a motor and a 35-to-1 gearbox that gives 164 newton-metres continuously, | with hard stops and a slip clutch | so it can never bend my leg the wrong way. | Each joint weighs about three and a half kilos. | **Verdict: possible on the ground, but too heavy to carry while flying.**

## 6. The arc reactor (about 3:50)

And now the one in his chest. | In the movie it makes three gigajoules every second. | No machine is perfectly efficient. | Even at ninety percent, the other ten percent becomes heat: | three hundred million watts, inside his chest. | Your body can get rid of about three hundred. | Fusion needs a machine the size of a room. | A nuclear battery gives tens of watts, | and flying needs hundreds of thousands. | **Verdict: impossible. Not yet, not like this.**

## Scoreboard and finish (about 4:25)

So here's the scoreboard. | JARVIS: possible. Flight: possible, for minutes. | Repulsors: real as thrusters. Armor: a trade-off. | Strength: possible on the ground. | The arc reactor: impossible. | That's why my suit runs on jet fuel instead. | Every calculation is open source, link below, | and nothing goes near me until it's tested. | Next video: the first real test.

## Facts to keep exact

| Claim | Source in the project |
| --- | --- |
| 2,440 N, 177 kg | Design doc 5.1 and 5.2 |
| Hover about 5 kg a minute, cruise under 1 kg a minute | Design doc 5.3 (305 kg/h and 57 kg/h) |
| About 20 min and over an hour | Design doc 2.3 and Section 12, simulation `sim/` |
| 3 GJ per second in the film, 300 MW of waste heat at 90% | Short 1 fact check |
| 164 N·m, about 3.5 kg a joint | Design doc 6.3 |
| Arm thrusters 120 N, shell 8 kg | Design doc 4 (bill of materials) |

## Chapters for the upload

0:00 Intro, 0:20 JARVIS, 1:05 Flight, 2:00 Repulsors, 2:35 Armor, 3:05 Strength, 3:50 Arc reactor, 4:25 Scoreboard
