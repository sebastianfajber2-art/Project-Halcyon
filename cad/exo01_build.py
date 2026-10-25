"""EXO-01 knee actuator, Rev B: Fusion API script that builds the concept model.

Run inside Autodesk Fusion (Utilities > Scripts and Add-Ins, or through the Fusion
MCP server). It opens a new design and builds all components in mm.
Purchased parts (motor, clutch, bearings) are envelopes at catalogue size;
the cycloid discs are true profiles.
"""

import adsk.core, adsk.fusion, math

CM = 0.1  # the Fusion API works in cm; every input below is in mm

N_PINS = 36          # ring pins -> 35 lobes -> 35:1
R_PIN_CIRCLE = 52.0
R_PIN = 3.0
ECC = 1.2
N_OUT = 8
R_OUT_CIRCLE = 34.0
R_OUT_PIN = 5.0
DISC_BORE_R = 24.0   # Rev B: 48 mm bore leaves 3.8 mm to the output-pin holes
MATERIAL = "100Cr6 (AISI 52100) 58-62 HRC"


def vi(mm):
    return adsk.core.ValueInput.createByReal(mm * CM)


def p3(x, y):
    return adsk.core.Point3D.create(x * CM, y * CM, 0)


def new_comp(root, name):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def plane_at(c, z):
    inp = c.constructionPlanes.createInput()
    inp.setByOffset(c.xYConstructionPlane, vi(z))
    return c.constructionPlanes.add(inp)


def extrude(c, profiles, h, name):
    coll = adsk.core.ObjectCollection.create()
    for p in profiles:
        coll.add(p)
    ext = c.features.extrudeFeatures.addSimple(coll, vi(h), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    for i in range(ext.bodies.count):
        ext.bodies.item(i).name = name if ext.bodies.count == 1 else f"{name} {i + 1}"


def ring(c, name, r_out, r_in, z0, h, cx=0.0):
    sk = c.sketches.add(plane_at(c, z0))
    sk.name = name
    sk.sketchCurves.sketchCircles.addByCenterRadius(p3(cx, 0), r_out * CM)
    if r_in > 0:
        sk.sketchCurves.sketchCircles.addByCenterRadius(p3(cx, 0), r_in * CM)
        extrude(c, [p for p in sk.profiles if p.profileLoops.count == 2], h, name)
    else:
        extrude(c, [sk.profiles.item(0)], h, name)


def box(c, name, cx, cy, w, d, z0, h):
    sk = c.sketches.add(plane_at(c, z0))
    sk.name = name
    sk.sketchCurves.sketchLines.addTwoPointRectangle(p3(cx - w / 2, cy - d / 2), p3(cx + w / 2, cy + d / 2))
    extrude(c, [sk.profiles.item(0)], h, name)


def pins(c, name, n, r_circle, r_pin, z0, h, cx=0.0):
    sk = c.sketches.add(plane_at(c, z0))
    sk.name = name
    for i in range(n):
        a = 2 * math.pi * i / n
        sk.sketchCurves.sketchCircles.addByCenterRadius(p3(cx + r_circle * math.cos(a), r_circle * math.sin(a)), r_pin * CM)
    extrude(c, list(sk.profiles), h, name)


def needle_bearing(c, name, cx, z0, h):
    ring(c, name + " inner race", 19.5, 17.5, z0, h, cx)
    pins(c, name + " needle", 36, 21.0, 1.45, z0, h, cx)
    ring(c, name + " outer race", 24.0, 22.5, z0, h, cx)


def cycloid_disc(c, name, z0, h, phase):
    n, r, rr, e = N_PINS, R_PIN_CIRCLE, R_PIN, ECC
    sk = c.sketches.add(plane_at(c, z0))
    sk.name = name
    pts = adsk.core.ObjectCollection.create()
    ox, oy = e * math.cos(phase), e * math.sin(phase)
    steps = 540
    for i in range(steps):
        t = 2 * math.pi * i / steps
        psi = math.atan2(math.sin((1 - n) * t), (r / (e * n)) - math.cos((1 - n) * t))
        x = r * math.cos(t) - rr * math.cos(t + psi) - e * math.cos(n * t)
        y = -r * math.sin(t) + rr * math.sin(t + psi) + e * math.sin(n * t)
        pts.add(p3(x * math.cos(phase) - y * math.sin(phase) + ox, x * math.sin(phase) + y * math.cos(phase) + oy))
    sk.sketchCurves.sketchFittedSplines.add(pts).isClosed = True
    circ = sk.sketchCurves.sketchCircles
    circ.addByCenterRadius(p3(ox, oy), DISC_BORE_R * CM)
    for i in range(N_OUT):
        a = 2 * math.pi * i / N_OUT
        circ.addByCenterRadius(p3(ox + R_OUT_CIRCLE * math.cos(a), oy + R_OUT_CIRCLE * math.sin(a)), (R_OUT_PIN + ECC) * CM)
    extrude(c, [max(sk.profiles, key=lambda p: p.profileLoops.count)], h, name)


def steel_material(app, design):
    mat = design.materials.itemByName(MATERIAL)
    if mat:
        return mat
    for li in range(app.materialLibraries.count):
        base = app.materialLibraries.item(li).materials.itemByName("Steel, Alloy")
        if base:
            return design.materials.addByCopy(base, MATERIAL)
    raise RuntimeError("Steel, Alloy not found in the material libraries")


def run(_context: str):
    app = adsk.core.Application.get()
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    root = design.rootComponent

    housing = new_comp(root, "Housing (7075)")
    ring(housing, "Back cover", 62.5, 15.0, -4.0, 4.0)
    ring(housing, "Housing tube", 62.5, 58.5, 0.0, 62.0)
    ring(housing, "Ring pin carrier", 62.5, 54.0, 40.0, 22.0)
    ring(housing, "Output housing", 64.0, 60.0, 62.0, 59.0)
    box(housing, "Hard stop 0 deg", -16.0, 69.0, 12.0, 12.0, 106.0, 15.0)
    a = math.radians(219.0)
    box(housing, "Hard stop 120 deg", 70.0 * math.cos(a), 70.0 * math.sin(a), 12.0, 12.0, 106.0, 15.0)

    motor = new_comp(root, "Motor CubeMars RI115-PH")
    ring(motor, "RI115 stator + rotor", 57.5, 37.0, 0.0, 38.1)

    shaft = new_comp(root, "Eccentric input shaft")
    ring(shaft, "Input shaft", 17.5, 12.0, 0.0, 62.0)
    needle_bearing(shaft, "Needle bearing A (C0 >= 25 kN)", ECC, 42.0, 8.0)
    needle_bearing(shaft, "Needle bearing B (C0 >= 25 kN)", -ECC, 51.0, 8.0)

    cyc = new_comp(root, "Cycloid stage 35-1")
    pins(cyc, "Ring pin", N_PINS, R_PIN_CIRCLE, R_PIN, 40.0, 22.0)
    cycloid_disc(cyc, "Cycloid disc A", 42.0, 8.0, 0.0)
    cycloid_disc(cyc, "Cycloid disc B", 51.0, 8.0, math.pi)
    pins(cyc, "Output pin", N_OUT, R_OUT_CIRCLE, R_OUT_PIN, 42.0, 22.0)
    ring(cyc, "Output pin support ring", 44.0, 24.0, 38.4, 3.6)
    pins(cyc, "Output pin extension", N_OUT, R_OUT_CIRCLE, R_OUT_PIN, 38.4, 3.6)
    mat = steel_material(app, design)
    for i in range(cyc.bRepBodies.count):
        cyc.bRepBodies.item(i).material = mat

    clutch = new_comp(root, "Slip clutch R+W SK1 (280 Nm)")
    ring(clutch, "SK1 torque limiter", 45.0, 15.0, 64.0, 40.0)

    bearing = new_comp(root, "Output bearing GSRU85")
    ring(bearing, "Crossed-roller bearing 55x120x15", 60.0, 27.5, 106.0, 15.0)

    out = new_comp(root, "Output flange + shin link")
    ring(out, "Output flange", 57.0, 15.0, 121.0, 10.0)
    box(out, "Shin link", 0.0, -195.0, 40.0, 310.0, 121.0, 10.0)
    box(out, "Hard stop dog", 0.0, 66.0, 12.0, 20.0, 121.0, 10.0)
    box(out, "Hard stop dog tab", 0.0, 70.0, 12.0, 12.0, 109.0, 12.0)

    sense = new_comp(root, "Output angle sensing")
    ring(sense, "Sense shaft", 6.0, 0.0, -8.0, 139.0)
    ring(sense, "AS5047P encoder board", 20.0, 0.0, -14.0, 4.0)

    thigh = new_comp(root, "Thigh link")
    box(thigh, "Thigh link", 0.0, 195.0, 40.0, 310.0, -14.0, 10.0)

    app.activeViewport.fit()
    print("EXO-01 Rev B built:", root.occurrences.count, "components")
