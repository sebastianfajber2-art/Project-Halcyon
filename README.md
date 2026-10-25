# Project Halcyon

A physics-honest jet wing suit: kerosene micro-turbines, retractable swing wings with speed, turn and stop modes, a DIY leg exoskeleton, and a triple-redundant flight core. No arc reactor, because physics does not allow one; every number here comes from a calculation you can rerun.

> **Status: concept design.** Nothing in this repository is cleared to build, wear or fly. Everything that touches a person passes bench, dummy and unmanned tests first. See the safety notice below.

## Headline numbers

| Item | Value | Source |
| --- | --- | --- |
| Empty mass incl. pilot | 177 kg | Design doc 5.1 |
| Installed thrust | 2,440 N (4 × 550 N + 2 × 120 N turbines) | Design doc 5.2 |
| Flight time, vertical takeoff, 30 kg fuel | 17 min (doc, conservative) / 24 min (sim v0.1) | `sim/` |
| Flight time, winch launch, 80 kg fuel | 60–64 min (doc) / 68 min (sim v0.1) | `sim/` |
| Knee actuator | CubeMars RI115 + 35:1 cycloid, 164 N·m continuous | `cad/`, `calcs/` |
| Programme cost | ~€420,000 over ~5 years | Design doc 11.2 |

## Repository layout

| Path | What it is |
| --- | --- |
| `sim/halcyon_sim.py` | Flight simulation v0.1: point-mass mission from launch to landing, time and fuel per phase |
| `calcs/cycloid_stress.py` | EXO-01 gearbox stress hand calculations at 476 N·m × 1.5 |
| `cad/exo01_build.py` | Fusion API script that builds the EXO-01 knee actuator model (Rev B) |
| `docs/social-media-plan.md` | Build-in-public and funding plan |

The full system design document (requirements, part list, calculations, drawings, safety analysis, test plan, roadmap) lives as a shared doc; ask the project owner for access.

## Run it

Python 3.10 or newer, no extra packages.

```bash
python sim/halcyon_sim.py --launch vertical
python sim/halcyon_sim.py --launch winch --fuel 80 --csv winch.csv
python calcs/cycloid_stress.py
```

To build the CAD model, run `cad/exo01_build.py` in Autodesk Fusion (Utilities > Scripts and Add-Ins).

## What the simulation does and does not model

v0.1 is a point mass in the vertical plane with ISA air density, a parabolic drag polar (C_D0 = 0.08, assumed), lift capped at C_L,max = 1.2, and turbine fuel burn from the JetCat P400-PRO datasheet (0.157 kg/(N·h)). It does not model attitude dynamics, turbine spool lag, wind, wing-mode changes or pilot control. Treat its endurance as an optimistic bound until C_D0 is measured.

## Safety notice

Jet-powered human flight has killed experienced, professional pilots. This project follows a gated test plan: simulation, bench, dummy, scale model, unmanned full-scale, tethered, then free flight, with each gate passed before the next. Do not build or wear anything from this repository outside that process.

## License

| What | License |
| --- | --- |
| Software: `sim/`, `calcs/`, and the code in `cad/exo01_build.py` | [MIT](LICENSE) |
| Hardware designs: the EXO-01 geometry and any CAD, drawings or design files in `cad/` | [CERN-OHL-S-2.0](cad/LICENSE-CERN-OHL-S-2.0.txt) |
| Documentation in `docs/` and this README | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

MIT keeps the code easy for anyone to reuse. CERN-OHL-S means anyone who builds and distributes a product from these hardware designs must share their modified design under the same licence, so improvements come back to the project.
