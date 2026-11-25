# models.py - entornos, Jesko aproximado y caja LST ilustrativa (se ejecuta dentro de build.py)

# ================================================================= TALLER
W = {}
W["floor"] = prim("cube", "Taller_Suelo", "WORKSHOP", M["floorW"], loc=(0, 0, -0.05), scale=(40, 40, 0.1), smooth=False)
W["wall"] = prim("cube", "Taller_ParedFondo", "WORKSHOP", M["wallW"], loc=(0, 7, 3.5), scale=(30, 0.2, 7), smooth=False)
W["wallL"] = prim("cube", "Taller_ParedIzq", "WORKSHOP", M["wallW"], loc=(-8, 0, 3.5), scale=(0.2, 30, 7), smooth=False)
lp = bpy.data.meshes.new("Taller_Logo"); bm = bmesh.new()
bm.loops.layers.uv.new("UVMap"); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0, calc_uvs=True); bm.to_mesh(lp); bm.free()
logo = new_obj("Taller_Logo", lp, "WORKSHOP", M["logo"], loc=(0, 6.88, 4.2)); logo.rotation_euler = (math.radians(90), 0, 0); logo.scale = (1.3 * 1.15, 1.15, 1)
for i, x in enumerate((-5.5, -4.2, 4.2, 5.5)):
    prim("cube", f"Taller_Armario{i}", "WORKSHOP", M["red"], loc=(x, 6.5, 0.55), scale=(1.2, 0.6, 1.1), bevel=0.02)
for i, x in enumerate((-3.6, 3.6)):
    for j, y in enumerate((2.6, 5.0)):
        prim("cube", f"Taller_Elevador{i}{j}", "WORKSHOP", M["blue"], loc=(x, y, 1.6), scale=(0.25, 0.25, 3.2), bevel=0.02)
for i in range(6):
    x = -4.5 + i * 1.8
    prim("cyl", f"Taller_Lampara{i}", "WORKSHOP", M["warm"], loc=(x, 2.5, 5.2), scale=(1, 1, 1), r=0.35, d=0.06, seg=24)
for i in range(5):
    t = prim("torus", f"Taller_PilaRueda{i}", "WORKSHOP", M["rubber"], loc=(-6.6, 4.5, 0.12 + i * 0.24), R=0.32, rr=0.11)
stand = prim("cube", "Taller_Banco", "WORKSHOP", M["steel"], loc=(2.9, -1.2, 0.45), scale=(1.0, 0.7, 0.9), bevel=0.02)

def light(name, kind, loc, energy, color=(1, 0.85, 0.7), size=2.0, rot=(0, 0, 0), cname="WORKSHOP", spot=None):
    d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color
    if kind == "AREA":
        d.size = size
    if kind == "SPOT" and spot:
        d.spot_size = spot
    o = bpy.data.objects.new(name, d); COLL[cname].objects.link(o); o.location = loc; o.rotation_euler = rot
    return o

L_WS = [
    light("Taller_Clave", "AREA", (-3.5, -4.5, 5.0), 2500, (1, 0.82, 0.62), 5, (math.radians(50), 0, math.radians(-35))),
    light("Taller_Relleno", "AREA", (4.5, -3.0, 3.0), 800, (0.75, 0.85, 1.0), 4, (math.radians(65), 0, math.radians(55))),
    light("Taller_Techo", "AREA", (0, 2.0, 5.5), 1800, (1, 0.75, 0.5), 8, (0, 0, 0)),
    light("Taller_Contra", "AREA", (0, 5.0, 2.5), 1200, (1, 0.6, 0.3), 4, (math.radians(-70), 0, 0)),
]

# ================================================================= ESTUDIO / LABORATORIO (ciclorama)
bm = bmesh.new()
rows = []
for i in range(25):  # suelo -> curva -> pared (radio 6 m)
    a = math.radians(90) * i / 24
    rows.append((3.0 + 6 * math.sin(a), 6 - 6 * math.cos(a)))
vl = [[bm.verts.new((x, -14, 0)) for x in (-14, 14)]]
for y, z in rows:
    vl.append([bm.verts.new((x, y, z)) for x in (-14, 14)])
vl.append([bm.verts.new((x, 9.0 + 0.01, 14)) for x in (-14, 14)])
for a, b in zip(vl[:-1], vl[1:]):
    bm.faces.new((a[0], a[1], b[1], b[0]))
me = bpy.data.meshes.new("Estudio_Ciclorama"); bm.to_mesh(me); bm.free()
for p in me.polygons:
    p.use_smooth = True
CYC = new_obj("Estudio_Ciclorama", me, "STUDIO", M["cyc"])
L_ST = [
    light("Estudio_SoftboxIzq", "AREA", (-4.5, -2.5, 4.0), 3500, (1, 1, 1), 4, (math.radians(55), 0, math.radians(-55))),
    light("Estudio_SoftboxDer", "AREA", (4.5, -1.5, 4.0), 2500, (1, 1, 1), 4, (math.radians(55), 0, math.radians(60))),
    light("Estudio_Cenital", "AREA", (0, 0.5, 7.0), 3000, (1, 1, 1), 6, (0, 0, 0)),
    light("Estudio_Contra", "AREA", (0, 6.0, 3.0), 2000, (0.7, 0.85, 1.0), 6, (math.radians(-65), 0, 0)),
]
for o in L_ST:
    link(o, "STUDIO")
# paneles visibles de softbox (reflejos en la pintura)
for i, (x, y, z, rz) in enumerate(((-4.6, -2.6, 4.1, -55), (4.6, -1.6, 4.1, 60))):
    p = prim("cube", f"Estudio_PanelSoftbox{i}", "STUDIO", mat(f"Softbox{i}", (1, 1, 1), emit=(1, 1, 1), es=6), loc=(x, y, z), rot=(math.radians(55), 0, math.radians(rz)), scale=(4, 2.2, 0.02), smooth=False)
L_LAB = [
    light("Lab_Clave", "AREA", (-2.5, -2.0, 5.0), 1500, (0.9, 0.95, 1.0), 3, (math.radians(40), 0, math.radians(-40))),
    light("Lab_Relleno", "AREA", (2.5, -1.0, 4.5), 900, (1, 1, 1), 3, (math.radians(45), 0, math.radians(45))),
    light("Lab_Recorte", "SPOT", (0, 3.0, 5.0), 3000, (1, 0.7, 0.4), 1, (math.radians(-35), 0, 0), spot=math.radians(40)),
]
for o in L_LAB:
    link(o, "LAB")

# ================================================================= JESKO (aproximado)
JR = empty("JESKO_Raiz", "JESKO")
PARTS = {}  # nombre -> (objeto, vector de desmontaje, retraso)

def lerp_tab(tab, y):
    for (y0, v0), (y1, v1) in zip(tab[:-1], tab[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0); t = t * t * (3 - 2 * t)
            return v0 + (v1 - v0) * t
    return tab[0][1] if y < tab[0][0] else tab[-1][1]

TOP = [(-2.3, 0.50), (-2.05, 0.64), (-1.6, 0.74), (-1.0, 0.80), (-0.6, 0.86), (0.2, 0.88), (1.0, 0.95), (1.7, 0.99), (2.3, 0.93)]
HW = [(-2.3, 0.74), (-2.05, 0.92), (-1.35, 1.0), (-0.7, 0.95), (0.2, 0.96), (1.35, 1.02), (2.0, 1.0), (2.3, 0.92)]
BOT = [(-2.3, 0.18), (-1.9, 0.13), (2.3, 0.14)]

def body_sec(y, seg=44, scale=1.0):
    top, bot, hw = lerp_tab(TOP, y), lerp_tab(BOT, y), lerp_tab(HW, y) * scale
    return superellipse(0, y, (top + bot) / 2, hw, (top - bot) / 2 * scale, n=3.4, seg=seg)

def body_range(name, y0, y1, m, n=12):
    ys = [y0 + (y1 - y0) * i / n for i in range(n + 1)]
    return loft(name, "JESKO", [body_sec(y) for y in ys], m, parent=JR)

def side_skin(name, y0, y1, side, m, n=10):
    secs = []
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        top, bot, hw = lerp_tab(TOP, y) - 0.04, lerp_tab(BOT, y) + 0.05, lerp_tab(HW, y) * 1.012
        cz, hh = (top + bot) / 2, (top - bot) / 2 * 1.012
        pts = []
        for k in range(13):
            t = math.radians(-62 + 124 * k / 12)
            c, s = math.cos(t), math.sin(t)
            x = hw * abs(c) ** (2 / 3.4)
            z = cz + hh * math.copysign(abs(s) ** (2 / 3.4), s)
            pts.append((side * x, y, z))
        secs.append(pts)
    bm = bmesh.new()
    rings = [[bm.verts.new(p) for p in s] for s in secs]
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(len(a) - 1):
            f = bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]) if side > 0 else (a[i + 1], a[i], b[i], b[i + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = new_obj(name, me, "JESKO", m, JR)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.02
    return o

tub = body_range("JESKO_Monocasco", -0.85, 0.75, M["carbon"])
front = body_range("JESKO_CapoDelantero", -2.3, -0.85, M["pearl"])
rear = body_range("JESKO_CapoTrasero", 0.75, 2.3, M["pearl"])
doorL = side_skin("JESKO_PuertaIzq", -0.8, 0.7, -1, M["pearl"])
doorR = side_skin("JESKO_PuertaDer", -0.8, 0.7, 1, M["pearl"])

# cabina (techo) y parabrisas
def canopy_sec(y, s=1.0):
    base = lerp_tab(TOP, y) - 0.06
    top = lerp_tab([(-0.8, 0.86), (-0.3, 1.1), (0.25, 1.21), (0.9, 1.12), (1.6, 0.99)], y)
    hw = lerp_tab([(-0.8, 0.5), (-0.2, 0.64), (0.6, 0.66), (1.6, 0.42)], y) * s
    return superellipse(0, y, base, hw, (top - base) * s, n=2.6, seg=40, zmin=base)
canopy = loft("JESKO_Cabina", "JESKO", [canopy_sec(-0.8 + 2.4 * i / 14) for i in range(15)], M["pearl"], parent=JR)
wind = loft("JESKO_Parabrisas", "JESKO", [canopy_sec(-0.82 + 0.85 * i / 6, 1.015) for i in range(7)], M["glass"], parent=JR)
for side in (-1, 1):
    win = prim("cube", f"JESKO_VentanaLat{'Izq' if side < 0 else 'Der'}", "JESKO", M["glass"], JR, loc=(side * 0.6, 0.15, 1.0), rot=(0, side * math.radians(-24), 0), scale=(0.02, 0.75, 0.17), bevel=0.01)
    win.parent = canopy
# faros y pilotos
for side in (-1, 1):
    hl = prim("cube", f"JESKO_Faro{side}", "JESKO", M["lightW"], front, loc=(side * 0.62, -2.13, 0.56), rot=(0, 0, side * math.radians(18)), scale=(0.34, 0.08, 0.035), bevel=0.01)
tail = prim("cube", "JESKO_PilotoTrasero", "JESKO", M["lightR"], rear, loc=(0, 2.31, 0.78), scale=(1.5, 0.02, 0.03), bevel=0.005)
# alerón trasero (perfil alar) y cuellos de cisne
wing_secs = []
for i in range(9):
    x = -1.0 + 2.0 * i / 8
    pts = []
    for k in range(24):
        t = 2 * math.pi * k / 24
        yy = 0.2 * math.cos(t)
        zz = 0.035 * math.sin(t) * (1.3 if math.sin(t) > 0 else 0.6) + 0.02 * math.cos(t)
        pts.append((x, 2.25 + yy, 1.42 + zz - 0.04 * math.cos(t)))
    wing_secs.append(pts)
wing = loft("JESKO_Aleron", "JESKO", wing_secs, M["carbon"], parent=JR)
for side in (-1, 1):
    prim("cube", f"JESKO_Endplate{side}", "JESKO", M["carbon"], wing, loc=(side * 1.0, 2.25, 1.38), scale=(0.015, 0.5, 0.22), bevel=0.01)
    neck = prim("cube", f"JESKO_CuelloCisne{side}", "JESKO", M["carbon"], wing, loc=(side * 0.35, 2.08, 1.18), rot=(math.radians(-18), 0, 0), scale=(0.03, 0.08, 0.42), bevel=0.01)
# difusor, splitter, faldones
diff = prim("cube", "JESKO_Difusor", "JESKO", M["carbon"], JR, loc=(0, 2.1, 0.17), rot=(math.radians(-12), 0, 0), scale=(1.7, 0.6, 0.03), bevel=0.01)
for i in range(6):
    prim("cube", f"JESKO_AletaDifusor{i}", "JESKO", M["carbon"], diff, loc=((-0.6 + 0.24 * i) / 1.7, 0, 3.0), scale=(0.008 / 1.7, 1.0, 6.0), smooth=False)
split = prim("cube", "JESKO_Splitter", "JESKO", M["carbon"], JR, loc=(0, -2.2, 0.13), scale=(1.6, 0.4, 0.02), bevel=0.01)
skirtL = prim("cube", "JESKO_FaldonIzq", "JESKO", M["carbon"], JR, loc=(-0.98, 0, 0.17), scale=(0.06, 1.7, 0.08), bevel=0.01)
skirtR = prim("cube", "JESKO_FaldonDer", "JESKO", M["carbon"], JR, loc=(0.98, 0, 0.17), scale=(0.06, 1.7, 0.08), bevel=0.01)

# ruedas
def wheel(name, x, y, width):
    root = empty(name, "JESKO", JR, (x, y, 0.36))
    side = 1 if x > 0 else -1
    tyre = ring(name + "_Neumatico", 0.36, 0.25, width, "JESKO", M["rubber"], root)
    tyre.rotation_euler = (0, 0, math.radians(90))
    md = tyre.modifiers.new("bev", "BEVEL"); md.width = 0.03; md.segments = 3
    rim = prim("cyl", name + "_Llanta", "JESKO", M["rim"], root, loc=(side * 0.06, 0, 0), rot=(0, math.radians(90), 0), r=0.25, d=0.03, seg=48)
    for k in range(10):
        a = 2 * math.pi * k / 10
        sp = prim("cube", f"{name}_Radio{k}", "JESKO", M["alu"], rim, loc=(0.11 * math.cos(a), 0.11 * math.sin(a), -side * 0.02), rot=(0, 0, a), scale=(0.2, 0.025, 0.02), smooth=False)
    disc = prim("cyl", name + "_Disco", "JESKO", M["steel"], root, loc=(-side * 0.02, 0, 0), rot=(0, math.radians(90), 0), r=0.2, d=0.03, seg=48)
    cal = prim("cube", name + "_Pinza", "JESKO", M["caliper"], root, loc=(side * 0.0, 0.0, 0.17), scale=(0.07, 0.16, 0.06), bevel=0.01)
    return root
WH = {
    "FL": wheel("JESKO_RuedaDelIzq", -0.86, -1.35, 0.27),
    "FR": wheel("JESKO_RuedaDelDer", 0.86, -1.35, 0.27),
    "RL": wheel("JESKO_RuedaTrasIzq", -0.88, 1.35, 0.33),
    "RR": wheel("JESKO_RuedaTrasDer", 0.88, 1.35, 0.33),
}
# motor V8 aproximado
ENG = empty("JESKO_Motor", "JESKO", JR, (0, 1.0, 0.45))
prim("cube", "Motor_Bloque", "JESKO", M["engine"], ENG, scale=(0.42, 0.62, 0.32), bevel=0.02)
for side in (-1, 1):
    bank = prim("cube", f"Motor_Bancada{side}", "JESKO", M["alu"], ENG, loc=(side * 0.2, 0, 0.2), rot=(0, side * math.radians(30), 0), scale=(0.18, 0.6, 0.16), bevel=0.02)
    tb = prim("torus", f"Motor_Turbo{side}", "JESKO", M["steel"], ENG, loc=(side * 0.42, 0.25, 0.05), rot=(0, math.radians(90), 0), R=0.08, rr=0.04)
prim("cube", "Motor_Admision", "JESKO", M["carbon"], ENG, loc=(0, 0, 0.33), scale=(0.2, 0.55, 0.1), bevel=0.03)

# ================================================================= CAJA LST (ILUSTRATIVA)
PAIRS = [(14, 46), (17, 43), (20, 40), (23, 37), (26, 34), (29, 31), (32, 28), (35, 25), (38, 22)]  # marchas 1..9 (ilustrativo)
W_IN = 0.18  # rad/fotograma eje primario

def add_spin_driver(obj, idx, expr):
    fc = obj.driver_add("rotation_euler", idx)
    fc.driver.type = "SCRIPTED"; fc.driver.expression = expr

def build_lst(prefix, parent, loc, scale=1.0):
    root = empty(prefix + "_Raiz", "LST", parent, loc); root.scale = (scale, scale, scale)
    info = {"root": root, "gears": [], "packs": [], "labels": []}
    # carcasa en dos mitades (la delantera se oculta para la vista seccionada)
    back = prim("cube", prefix + "_CarcasaTrasera", "LST", M["alu"], root, loc=(0, 0, 0.06), scale=(0.5, 0.6, 0.42), bevel=0.04)
    back.scale = (0.5, 0.6, 0.42)
    cover = prim("cube", prefix + "_CarcasaDelantera", "LST", M["alu"], root, loc=(0, -0.002, 0.06), scale=(0.52, 0.62, 0.44), bevel=0.05)
    info["cover"] = cover; info["back"] = back
    for name, x, z in (("Primario", -0.1, 0.0), ("Secundario", 0.1, 0.0), ("Embragues", 0.0, 0.17)):
        prim("cyl", f"{prefix}_Eje{name}", "LST", M["steel"], root, loc=(x, 0, z), rot=(math.radians(90), 0, 0), r=0.012, d=0.62, seg=24)
    for g, (ti, to) in enumerate(PAIRS):
        y = -0.24 + g * 0.06
        ri = 0.2 * ti / (ti + to); ro = 0.2 * to / (ti + to)
        gm = mat(f"{prefix}_MatMarcha{g+1}", (0.62, 0.63, 0.65), 0.22, 1.0, emit=(1, 0.4, 0.0), es=0.0)
        gi = gear_mesh(f"{prefix}_Marcha{g+1}_Conductor", ti, ri, 0.028, "LST", gm, root, (-0.1, y, 0.0))
        go = gear_mesh(f"{prefix}_Marcha{g+1}_Conducido", to, ro, 0.028, "LST", gm, root, (0.1, y, 0.0))
        add_spin_driver(gi, 1, f"frame*{W_IN:.4f}")
        add_spin_driver(go, 1, f"-frame*{W_IN * ti / to:.5f}")  # velocidad inversamente proporcional a los dientes
        info["gears"].append((gi, go, gm))
    for p in range(7):  # siete paquetes multidisco ilustrativos
        y = -0.24 + p * 0.08
        pm = mat(f"{prefix}_MatEmbrague{p+1}", (0.35, 0.16, 0.06), 0.7, 0.0, emit=(1, 0.45, 0.05), es=0.0)
        pk = empty(f"{prefix}_Embrague{p+1}", "LST", root, (0, y, 0.17))
        ring(f"{prefix}_Embrague{p+1}_Campana", 0.07, 0.064, 0.06, "LST", M["alu"], pk)
        for d in range(9):
            dy = -0.024 + d * 0.006
            ring(f"{prefix}_Embrague{p+1}_Disco{d}", 0.058 if d % 2 else 0.062, 0.02, 0.0035, "LST", pm if d % 2 else M["steel"], pk, (0, dy, 0))
        add_spin_driver(pk, 1, f"frame*{W_IN * 0.6:.4f}")
        info["packs"].append((pk, pm))
    # placa electrónica (ECU) ilustrativa
    pcb = prim("cube", prefix + "_ECU", "LST", M["pcb"], root, loc=(0, 0.05, 0.3), scale=(0.34, 0.24, 0.008), smooth=False)
    for k in range(8):
        prim("cube", f"{prefix}_ECU_Chip{k}", "LST", M["chip"], pcb, loc=(-0.3 + 0.2 * (k % 4), -0.25 + 0.5 * (k // 4), 1.0), scale=(0.12, 0.18, 1.5), smooth=False)
    info["pcb"] = pcb
    return info

LSTD = build_lst("LSTExpo", None, (2.9, -1.2, 1.15), scale=1.4)  # unidad expuesta en el banco del taller (plano 1)
LSTD["cover"].hide_render = True; LSTD["cover"].hide_viewport = True
LSTC = build_lst("LST", JR, (0, 1.85, 0.45), scale=1.0)            # unidad montada en el coche
