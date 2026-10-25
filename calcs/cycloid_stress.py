"""EXO-01 cycloid stage stress hand calculations (design doc section 6.4).

Checks lobe contact stress, ring-pin bending and output-pin bending and contact
at the design torque, and sweeps the eccentricity. Pure Python. Run:
    python calcs/cycloid_stress.py
"""

import math

# Geometry (CAD Rev B)
N_PINS = 36          # ring pins; lobes = N_PINS - 1
R_PIN_CIRCLE = 52.0  # mm
R_PIN = 3.0          # mm
ECC = 1.2            # mm
DISC_T = 8.0         # mm
N_OUT = 8
R_OUT_CIRCLE = 34.0  # mm
D_OUT_PIN = 10.0     # mm
D_OUT_HOLE = 12.4    # mm

# Loads
T_PEAK = 476.0       # N*m at the output, motor peak through 35:1 at 85%
SAFETY = 1.5
DISC_SHARE = 0.6     # one disc takes 60% (manufacturing error between discs)
PIN_SHARING = 1.3    # uneven sharing between pins

E_STAR = 210e9 / (2 * (1 - 0.3 ** 2))  # steel on steel, Pa


def hertz_line(force, length_m, r_eq_m):
    return math.sqrt(force * E_STAR / (math.pi * length_m * r_eq_m))


def bending(moment, d_m):
    return 32 * moment / (math.pi * d_m ** 3)


def lobe_peak_contact(ecc, f_max, steps=36000):
    """Peak Hertz stress along the profile, with load ~ |sin| across each lobe."""
    n, r, rr = N_PINS, R_PIN_CIRCLE, R_PIN
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        psi = math.atan2(math.sin((1 - n) * t), (r / (ecc * n)) - math.cos((1 - n) * t))
        pts.append((r * math.cos(t) - rr * math.cos(t + psi) - ecc * math.cos(n * t),
                    -r * math.sin(t) + rr * math.sin(t + psi) + ecc * math.sin(n * t)))
    best, min_tip = 0.0, float("inf")
    for i in range(1, steps - 1):
        (ax, ay), (bx, by), (cx, cy) = pts[i - 1], pts[i], pts[i + 1]
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if abs(cross) < 1e-15:
            continue
        rho = math.sqrt(((bx - ax) ** 2 + (by - ay) ** 2) * ((cx - bx) ** 2 + (cy - by) ** 2)
                        * ((cx - ax) ** 2 + (cy - ay) ** 2)) / (2 * abs(cross))
        if cross < 0:  # convex lobe flank
            inv = 1 / rr + 1 / rho
            min_tip = min(min_tip, rho)
        else:          # concave pocket
            inv = 1 / rr - 1 / rho
        if inv <= 0:
            continue
        t = 2 * math.pi * i / steps
        load = f_max * abs(math.sin((n - 1) * t / 2))
        best = max(best, hertz_line(load, DISC_T / 1000, (1 / inv) / 1000))
    return best, min_tip


def pin_force(ecc_mm, t_disc):
    return PIN_SHARING * 4 * t_disc / (N_PINS * ecc_mm / 1000 * (N_PINS - 1))


def main():
    t_design = T_PEAK * SAFETY
    t_disc = t_design * DISC_SHARE
    f_pin = pin_force(ECC, t_disc)
    print(f"design torque {t_design:.0f} N*m, per disc {t_disc:.0f} N*m, max ring-pin force {f_pin:.0f} N")

    p_lobe, tip = lobe_peak_contact(ECC, f_pin)
    print(f"lobe contact (peak Hertz)        {p_lobe / 1e6:6.0f} MPa  (100Cr6 58-62 HRC static ~4000)")
    print(f"smallest lobe tip radius          {tip:6.2f} mm")

    m_ring = f_pin * 0.018 / 4
    print(f"ring pin bending, 18 mm span     {bending(m_ring, 2 * R_PIN / 1000) / 1e6:6.0f} MPa  (hardened dowel >=1500)")

    f_out = PIN_SHARING * 4 * t_disc / (N_OUT * R_OUT_CIRCLE / 1000)
    cantilever = bending(f_out * 0.018, D_OUT_PIN / 1000)
    span, a = 0.024, 0.007
    supported = bending(f_out * a * (span - a) / span, D_OUT_PIN / 1000)
    r_eq = 1 / (1 / (D_OUT_PIN / 2) - 1 / (D_OUT_HOLE / 2)) / 1000
    print(f"output pin force                  {f_out:6.0f} N")
    print(f"output pin bending, cantilever   {cantilever / 1e6:6.0f} MPa  (fails: no margin)")
    print(f"output pin bending, both ends    {supported / 1e6:6.0f} MPa")
    print(f"output pin in hole, contact      {hertz_line(f_out, DISC_T / 1000, r_eq) / 1e6:6.0f} MPa")

    print("\neccentricity sweep")
    for ecc in (1.2, 1.0, 0.9, 0.8):
        f = pin_force(ecc, t_disc)
        p, tip = lobe_peak_contact(ecc, f)
        print(f"  e={ecc:.1f} mm  pin force {f:5.0f} N  tip radius {tip:4.2f} mm  peak contact {p / 1e6:5.0f} MPa")


if __name__ == "__main__":
    main()
