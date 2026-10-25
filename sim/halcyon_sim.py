"""Project Halcyon flight simulation v0.1.

Point-mass model of the jet wing suit in the vertical plane. It flies a whole
mission (takeoff or winch release, transition, climb, cruise, glide, stop mode,
vertical landing) and reports time and fuel per phase, so the endurance figures
in the design document can be checked.

Pure Python, no dependencies. Run:  python sim/halcyon_sim.py
"""

import argparse
import csv
import math
from dataclasses import dataclass

G = 9.81


@dataclass
class Suit:
    empty_mass: float = 177.0       # kg, pilot included (design doc 5.1)
    max_thrust: float = 2440.0      # N, 4 x 550 + 2 x 120
    tsfc: float = 0.157 / 3600      # kg/(N*s), JetCat P400-PRO datasheet
    idle_burn: float = 0.9 / 60     # kg/s, six turbines at idle
    wing_area: float = 1.75         # m^2, turn mode
    aspect_ratio: float = 4.2
    oswald: float = 0.8
    cd0: float = 0.08               # wing + body + turbines (assumption, to be measured)
    cl_max: float = 1.2


def air_density(h):
    """ISA troposphere density at altitude h (m)."""
    t = 288.15 - 0.0065 * h
    return 1.225 * (t / 288.15) ** 4.256


class Flight:
    def __init__(self, suit, fuel, dt=0.1):
        self.s = suit
        self.fuel = fuel
        self.fuel0 = fuel
        self.dt = dt
        self.t = 0.0
        self.x = 0.0
        self.h = 0.0
        self.vx = 0.0
        self.vz = 0.0
        self.log = []
        self.phases = []

    @property
    def mass(self):
        return self.s.empty_mass + self.fuel

    def aero(self, v):
        """Lift (capped at CL_max) and drag at speed v and the current height."""
        q = 0.5 * air_density(self.h) * v * v
        if q < 1e-6:
            return 0.0, 0.0
        cl = min(self.mass * G / (q * self.s.wing_area), self.s.cl_max)
        cd = self.s.cd0 + cl * cl / (math.pi * self.s.oswald * self.s.aspect_ratio)
        return q * self.s.wing_area * cl, q * self.s.wing_area * cd

    def step(self, phase, ax, az, idle=False):
        """Advance one step with the commanded accelerations; thrust is whatever that takes."""
        v = math.hypot(self.vx, self.vz)
        lift, drag = self.aero(v)
        if idle:
            tx, tz = 0.0, 0.0
            burn = self.s.idle_burn
            # steady glide: airspeed held, height traded for drag, sink = V / (L/D)
            ax, az = 0.0, 0.0
            self.vz = -v * drag / lift if lift > 0 else -v
        else:
            tx = self.mass * ax + drag
            tz = self.mass * az + self.mass * G - lift
            t = math.hypot(tx, tz)
            if t > self.s.max_thrust:
                scale = self.s.max_thrust / t
                tx, tz = tx * scale, tz * scale
                ax = (tx - drag) / self.mass
                az = (tz + lift - self.mass * G) / self.mass
            burn = max(self.s.tsfc * math.hypot(tx, tz), self.s.idle_burn)
        self.vx += ax * self.dt
        self.vz += az * self.dt
        self.x += self.vx * self.dt
        self.h = max(0.0, self.h + self.vz * self.dt)
        self.fuel -= burn * self.dt
        self.t += self.dt
        self.log.append((round(self.t, 1), phase, round(self.x), round(self.h, 1),
                         round(self.vx, 1), round(self.vz, 1), round(self.fuel, 2),
                         round(math.hypot(tx, tz))))

    def phase(self, name, done, control):
        t0, f0 = self.t, self.fuel
        while not done() and self.fuel > 0:
            self.step(name, *control())
        self.phases.append((name, self.t - t0, f0 - self.fuel))


def mission(launch, fuel, cruise_speed=55.0, cruise_alt=300.0, reserve_frac=0.10):
    s = Suit()
    f = Flight(s, fuel)
    v_stall = math.sqrt(2 * f.mass * G / (1.225 * s.wing_area * s.cl_max))
    landing_budget = 3.0  # kg kept for glide, stop mode and final hover (~1.9 kg used in v0.1 runs)
    reserve = reserve_frac * fuel

    if launch == "vertical":
        if f.mass * G * 1.2 > s.max_thrust:
            raise SystemExit(f"Too heavy for vertical takeoff: {f.mass:.0f} kg needs "
                             f"{f.mass * G * 1.2:.0f} N with 20% margin, suit has {s.max_thrust:.0f} N")
        f.phase("takeoff climb to 80 m", lambda: f.h >= 80, lambda: (0.0, 2.0 if f.vz < 10 else 0.0))
        f.phase("level off", lambda: abs(f.vz) < 0.2, lambda: (0.0, -2.0 if f.vz > 0 else 0.0))
        f.phase("transition to wing flight", lambda: f.vx >= 1.15 * v_stall, lambda: (3.0, -f.vz))
    else:
        # Winch release: glider-style tow leaves the suit at height and flying speed.
        f.h, f.vx = 300.0, 50.0
        f.phases.append(("winch tow (no fuel)", 40.0, 0.0))
        f.t = 40.0

    f.phase("climb to cruise altitude", lambda: f.h >= cruise_alt,
            lambda: ((cruise_speed - f.vx) * 0.2, 5.0 - f.vz))
    f.phase("cruise", lambda: f.fuel <= reserve + landing_budget,
            lambda: ((cruise_speed - f.vx) * 0.2, (cruise_alt - f.h) * 0.05 - f.vz * 0.5))
    f.phase("idle glide down to 30 m", lambda: f.h <= 30, lambda: (0.0, 0.0, True))
    f.phase("stop mode, decelerate", lambda: f.vx <= 2.0,
            lambda: (-1.5 * G, (30.0 - f.h) * 0.5 - f.vz))
    f.phase("vertical landing", lambda: f.h <= 0.0,
            lambda: (-f.vx, (-2.0 - f.vz) * 1.0))
    return f


def report(f, launch):
    print(f"\nHalcyon sim v0.1: {launch} launch, {f.fuel0:.0f} kg fuel")
    print(f"{'phase':32} {'time (s)':>9} {'fuel (kg)':>10}")
    for name, dt, df in f.phases:
        print(f"{name:32} {dt:9.0f} {df:10.2f}")
    print(f"{'total':32} {f.t:9.0f} {f.fuel0 - f.fuel:10.2f}")
    print(f"flight time {f.t / 60:.1f} min, range {f.x / 1000:.1f} km, fuel left {f.fuel:.1f} kg")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--launch", choices=["vertical", "winch"], default="vertical")
    ap.add_argument("--fuel", type=float, help="kg of fuel (default 30 vertical, 80 winch)")
    ap.add_argument("--speed", type=float, default=55.0, help="cruise airspeed, m/s")
    ap.add_argument("--csv", help="write the time history to this CSV file")
    args = ap.parse_args()
    fuel = args.fuel if args.fuel is not None else (30.0 if args.launch == "vertical" else 80.0)
    f = mission(args.launch, fuel, cruise_speed=args.speed)
    report(f, args.launch)
    if args.csv:
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["t_s", "phase", "x_m", "h_m", "vx_ms", "vz_ms", "fuel_kg", "thrust_N"])
            w.writerows(f.log)
        print(f"time history written to {args.csv}")


if __name__ == "__main__":
    main()
