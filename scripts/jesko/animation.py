# animation.py - planos, cámaras, desmontaje/montaje, visemas, textos 3D y cambios de entorno

# ----------------------------------------------------------------- posiciones de personajes
WS_ALEX = ((-1.9, -1.7, 0), math.radians(-20))
WS_CLAUDE = ((1.35, -2.25, 0), math.radians(10))
ST_CLAUDE = ((1.15, -2.9, 0), math.radians(25))

def place(o, frame, pos, rz):
    o.location = pos; o.rotation_euler = (0, 0, rz)
    o.keyframe_insert("location", frame=frame); o.keyframe_insert("rotation_euler", frame=frame)

# Alex: en el taller (planos 1, 2 y 8); en estudio solo es voz en off
place(AL["root"], 1, *WS_ALEX)
key_hide(AL["root"], 1, False); key_hide(AL["root"], 331, True); key_hide(AL["root"], 1621, False)
# Claude: taller -> estudio -> taller
place(CL["root"], 1, *WS_CLAUDE); place(CL["root"], 246, (1.35, -2.25, 0), math.radians(10))
place(CL["root"], 247, (1.45, -2.45, 0), math.radians(-15))
place(CL["root"], 330, (1.45, -2.25, 0), math.radians(-35))   # se acerca a la rueda
place(CL["root"], 331, *ST_CLAUDE); place(CL["root"], 1620, *ST_CLAUDE)
place(CL["root"], 1621, (0.9, -2.4, 0), math.radians(-10)); place(CL["root"], 1800, (0.9, -2.4, 0), math.radians(-10))
for fc_owner in (CL["root"],):
    ad = fc_owner.animation_data
# cortes secos en los cambios de plano
def make_constant_at(o, frames):
    ad = o.animation_data
    if not ad or not ad.action:
        return
    try:
        curves = ad.action.fcurves
    except Exception:
        curves = [fc for layer in ad.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
    for fc in curves:
        for k in fc.keyframe_points:
            if int(k.co.x) in frames:
                k.interpolation = "CONSTANT"
make_constant_at(CL["root"], {246, 330, 1620})

# ----------------------------------------------------------------- entornos
WS_OBJS = [o for o in COLL["WORKSHOP"].objects]
ST_OBJS = [o for o in COLL["STUDIO"].objects]
LAB_OBJS = [o for o in COLL["LAB"].objects]
for o in WS_OBJS:
    key_hide(o, 1, False); key_hide(o, 331, True); key_hide(o, 1621, False)
for o in LSTD["root"].children_recursive + [LSTD["root"]]:
    key_hide(o, 1, False); key_hide(o, 331, True); key_hide(o, 1621, False)
for hz in (LSTD["cover"], LSTD["back"]):
    hz.animation_data_clear(); hz.hide_render = True; hz.hide_viewport = True
for o in ST_OBJS:
    key_hide(o, 1, True); key_hide(o, 331, False); key_hide(o, 1621, True)
for o in LAB_OBJS:
    key_hide(o, 1, True); key_hide(o, 571, False); key_hide(o, 1381, True)
for pn in ("Estudio_PanelSoftbox0", "Estudio_PanelSoftbox1"):
    if pn in bpy.data.objects:
        bpy.data.objects[pn].visible_camera = False
w = sc.world or bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"].inputs
bg[0].default_value = (0.01, 0.01, 0.012, 1); bg[1].default_value = 0.4

# ----------------------------------------------------------------- desmontaje (plano 3) y montaje inverso (plano 7)
def explode(o, offset, s0, s1, r0, r1, extra_rot=(0, 0, 0), spin=False):
    """s0-s1: salida (desmontaje); r0-r1: regreso (montaje inverso). Guarda la posición original."""
    base = o.location.copy(); brot = o.rotation_euler.copy()
    o["pos_original"] = list(base)
    tgt = base + Vector(offset)
    key_loc(o, s0, base); key_loc(o, s1, tgt); key_loc(o, r0, tgt); key_loc(o, r1, base)
    if any(extra_rot):
        key_rot(o, s0, brot); key_rot(o, s1, Vector(brot) + Vector(extra_rot)); key_rot(o, r0, Vector(brot) + Vector(extra_rot)); key_rot(o, r1, brot)

EXPLODE = [
    (doorL, (-1.5, 0, 0.5), 340, 390, 1570, 1612, (0, math.radians(-25), 0)),
    (doorR, (1.5, 0, 0.5), 345, 395, 1570, 1612, (0, math.radians(25), 0)),
    (front, (0, -0.9, 1.6), 360, 415, 1550, 1600, (math.radians(-12), 0, 0)),
    (canopy, (0, -0.2, 2.5), 380, 435, 1540, 1592, (0, 0, 0)),
    (wind, (0, -0.2, 2.5), 380, 435, 1540, 1592, (0, 0, 0)),
    (rear, (0, 0.8, 1.9), 395, 450, 1530, 1585, (math.radians(10), 0, 0)),
    (wing, (0, 1.2, 2.7), 400, 455, 1525, 1580, (0, 0, 0)),
    (WH["FL"], (-1.4, 0, 0.1), 420, 470, 1500, 1560, (0, 0, 0)),
    (WH["FR"], (1.4, 0, 0.1), 422, 472, 1500, 1560, (0, 0, 0)),
    (WH["RL"], (-1.5, 0, 0.1), 424, 474, 1500, 1560, (0, 0, 0)),
    (WH["RR"], (1.5, 0, 0.1), 426, 476, 1500, 1560, (0, 0, 0)),
    (split, (0, -1.2, -0.0), 430, 480, 1490, 1540, (0, 0, 0)),
    (diff, (0, 1.4, 0.0), 432, 482, 1490, 1540, (0, 0, 0)),
    (skirtL, (-1.2, 0, 0), 434, 484, 1490, 1540, (0, 0, 0)),
    (skirtR, (1.2, 0, 0), 434, 484, 1490, 1540, (0, 0, 0)),
    (ENG, (0, -0.3, 1.1), 455, 515, 1450, 1510, (0, 0, 0)),
]
for o, off, s0, s1, r0, r1, er in EXPLODE:
    explode(o, off, s0, s1, r0, r1, er)

# Caja LST: sale del coche, sube al "laboratorio", se gira con los ejes en vertical y se escala para los macros
LR = LSTC["root"]; base = LR.location.copy()
LAB_POS = Vector((0, -1.0, 1.35))
key_loc(LR, 470, base); key_loc(LR, 520, base + Vector((0, 0, 2.2))); key_loc(LR, 565, LAB_POS)
key_rot(LR, 470, (0, 0, 0)); key_rot(LR, 565, (math.radians(-90), 0, 0))
key_scale(LR, 470, (1, 1, 1)); key_scale(LR, 565, (2, 2, 2))
key_loc(LR, 1381, LAB_POS); key_rot(LR, 1381, (math.radians(-90), 0, 0)); key_scale(LR, 1381, (2, 2, 2))
key_loc(LR, 1420, base + Vector((0, 0, 2.2))); key_loc(LR, 1460, base)
key_rot(LR, 1460, (0, 0, 0)); key_scale(LR, 1460, (1, 1, 1))
# vista seccionada: se oculta la carcasa delantera mientras está en el laboratorio
for hz in (LSTC["cover"], LSTC["back"]):
    key_hide(hz, 1, False); key_hide(hz, 560, True); key_hide(hz, 1390, False)
# giro lento tipo plataforma durante el plano 4
key_rot(LR, 600, (math.radians(-90), 0, 0)); key_rot(LR, 720, (math.radians(-90), 0, math.radians(25)))
key_rot(LR, 840, (math.radians(-90), 0, 0))

# en el laboratorio solo se ve la caja: el resto del coche desmontado se oculta
lst_set = set(LR.children_recursive) | {LR}
for o in [JR] + list(JR.children_recursive):
    if o in lst_set or o.type not in ("MESH", "CURVE", "FONT"):
        continue
    key_hide(o, 1, False); key_hide(o, 566, True); key_hide(o, 1381, False)

# ----------------------------------------------------------------- iluminación de embragues, rutas y marchas
def pulse(m, f0, f1, peak):
    key_emit(m, f0 - 3, 0.0); key_emit(m, f0, peak); key_emit(m, f1, peak); key_emit(m, f1 + 4, 0.0)

# plano 4: los 7 embragues se activan coordinadamente (abriendo y cerrando rutas)
for p, (pk, pm) in enumerate(LSTC["packs"]):
    key_emit(pm, 1, 0.0)
    t0 = 19.4 + p * 0.55
    pulse(pm, fr(t0), fr(t0 + 0.9), 6.0)
    pulse(pm, fr(22.8 + (p % 3) * 0.2), fr(23.6), 4.0)
    # compresión del paquete (discos que se aprietan)
    key_scale(pk, fr(t0) - 3, (1, 1, 1)); key_scale(pk, fr(t0), (1, 0.82, 1)); key_scale(pk, fr(t0 + 0.9), (1, 0.82, 1)); key_scale(pk, fr(t0 + 0.9) + 4, (1, 1, 1))
# plano 5: de séptima a cuarta directamente (UPOD)
for g, (gi, go, gm) in enumerate(LSTC["gears"]):
    key_emit(gm, 1, 0.0)
G7, G6, G5, G4 = (LSTC["gears"][i][2] for i in (6, 5, 4, 3))
key_emit(G7, fr(28.2), 0.0); key_emit(G7, fr(28.5), 5.0); key_emit(G7, fr(33.0), 5.0); key_emit(G7, fr(33.15), 0.0)
key_emit(G4, fr(33.0), 0.0); key_emit(G4, fr(33.15), 7.0); key_emit(G4, fr(37.8), 7.0); key_emit(G4, fr(38.0), 0.0)
# plano 6: electrónica y embragues coordinados
key_emit(M["pcb"], 1, 0.0); key_emit(M["pcb"], fr(39.6), 0.0); key_emit(M["pcb"], fr(39.9), 3.0); key_emit(M["pcb"], fr(45.8), 3.0); key_emit(M["pcb"], fr(46.0), 0.0)
for p, (pk, pm) in enumerate(LSTC["packs"]):
    pulse(pm, fr(40.9 + p * 0.12), fr(42.0 + p * 0.12), 5.0)

# ----------------------------------------------------------------- textos 3D (blancos/naranjas, ligados a cámara)
CAMS = {}
def camera(name, lens):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_fit = "VERTICAL"; cd.sensor_height = 24
    cd.dof.use_dof = True; cd.dof.aperture_fstop = 4.0
    co = bpy.data.objects.new(name, cd); COLL["CAMERAS"].objects.link(co)
    tg = empty(name + "_Objetivo", "CAMERAS")
    c = co.constraints.new("TRACK_TO"); c.target = tg; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    cd.dof.focus_object = tg
    CAMS[name] = (co, tg)
    return co, tg

def cam_keys(name, keys):
    co, tg = CAMS[name]
    for f, pos, tgt, lens in keys:
        key_loc(co, f, pos); key_loc(tg, f, tgt)
        co.data.lens = lens; co.data.keyframe_insert("lens", frame=f)

def popup_text(name, body, m, cam, local, size, f_in, f_out):
    t = text3d(name, body, m, size=size, parent=cam, loc=local, rot=(0, 0, 0))
    key_scale(t, 1, (0, 0, 0)); key_scale(t, f_in - 1, (0, 0, 0)); key_scale(t, f_in + 5, (1.12, 1.12, 1.12)); key_scale(t, f_in + 8, (1, 1, 1))
    key_scale(t, f_out, (1, 1, 1)); key_scale(t, f_out + 5, (0, 0, 0))
    return t

# ----------------------------------------------------------------- planos y cámaras
LX = Vector(LAB_POS)
camera("CAM_P1_Macro", 100)
cam_keys("CAM_P1_Macro", [
    (1, (2.78, -2.05, 1.24), (2.86, -1.2, 1.2), 100),
    (45, (2.7, -2.15, 1.3), (2.86, -1.2, 1.2), 85),
    (80, (2.45, -2.6, 1.45), (2.86, -1.2, 1.2), 60),
    (150, (0.6, -7.6, 1.75), (-0.2, -0.6, 0.8), 26),
])
camera("CAM_P2_Orbita", 28)
piv = empty("CAM_P2_Pivote", "CAMERAS", None, (0, 0, 0))
co2, tg2 = CAMS["CAM_P2_Orbita"]; co2.parent = piv; co2.location = (0, -7.2, 1.5); tg2.location = (0, -0.2, 0.7)
key_rot(piv, 151, (0, 0, math.radians(-35))); key_rot(piv, 246, (0, 0, math.radians(30)))
camera("CAM_P2_Claude", 45)
cam_keys("CAM_P2_Claude", [(247, (1.05, -3.35, 0.32), (1.45, -2.45, 0.24), 45), (330, (1.0, -3.2, 0.3), (1.45, -2.3, 0.24), 50)])
camera("CAM_P3_Grua", 24)
cam_keys("CAM_P3_Grua", [(331, (5.0, -7.0, 2.2), (0, 0, 0.8), 24), (570, (6.0, -6.0, 5.2), (0, 0.2, 1.6), 24)])
camera("CAM_P4_MacroLST", 70)
cam_keys("CAM_P4_MacroLST", [(571, (-1.3, -3.8, 0.95), LX + Vector((0, 0, 0.0)), 45), (726, (1.0, -3.6, 1.85), LX + Vector((0, 0, 0.2)), 50)])
camera("CAM_ClaudeEstudio", 50)
cpos = Vector(ST_CLAUDE[0])
cam_keys("CAM_ClaudeEstudio", [(727, cpos + Vector((-0.35, -1.0, 0.18)), cpos + Vector((0, 0, 0.24)), 50), (840, cpos + Vector((-0.3, -0.92, 0.2)), cpos + Vector((0, 0, 0.24)), 55)])
camera("CAM_P5_Esquema", 50)
cam_keys("CAM_P5_Esquema", [(841, (0.25, -5.2, 1.4), LX, 50), (1068, (0.15, -4.9, 1.4), LX, 50)])
camera("CAM_P6_Macro", 100)
cam_keys("CAM_P6_Macro", [(1141, LX + Vector((0.7, -1.9, -0.45)), LX + Vector((0.15, 0, -0.3)), 42), (1290, LX + Vector((-0.6, -1.8, 0.55)), LX + Vector((0, 0, 0.35)), 42)])
camera("CAM_P7_Montaje", 26)
cam_keys("CAM_P7_Montaje", [(1381, (6.4, -5.6, 4.3), (0, 0.2, 1.4), 26), (1620, (4.6, -7.0, 1.9), (0, 0, 0.7), 28)])
camera("CAM_P8_Alex", 50)
ap = Vector(WS_ALEX[0])
cam_keys("CAM_P8_Alex", [(1621, ap + Vector((0.4, -2.6, 1.72)), ap + Vector((0, 0, 1.62)), 42), (1716, ap + Vector((0.3, -2.2, 1.74)), ap + Vector((0, 0, 1.66)), 48)])
camera("CAM_P8_Claude", 45)
cw = Vector((0.9, -2.4, 0))
cam_keys("CAM_P8_Claude", [(1717, cw + Vector((-0.25, -0.95, 0.2)), cw + Vector((0, 0, 0.24)), 45), (1800, cw + Vector((-0.2, -0.8, 0.22)), cw + Vector((0, 0, 0.25)), 50)])
for n in ("CAM_P4_MacroLST", "CAM_P6_Macro"):
    CAMS[n][0].data.dof.aperture_fstop = 5.6
CAMS["CAM_P5_Esquema"][0].data.dof.use_dof = False

SHOTS = [(1, "CAM_P1_Macro"), (151, "CAM_P2_Orbita"), (247, "CAM_P2_Claude"), (331, "CAM_P3_Grua"), (571, "CAM_P4_MacroLST"),
         (727, "CAM_ClaudeEstudio"), (841, "CAM_P5_Esquema"), (1069, "CAM_ClaudeEstudio"), (1141, "CAM_P6_Macro"),
         (1291, "CAM_ClaudeEstudio"), (1381, "CAM_P7_Montaje"), (1621, "CAM_P8_Alex"), (1717, "CAM_P8_Claude")]
for f, n in SHOTS:
    mk = sc.timeline_markers.new(n, frame=f); mk.camera = CAMS[n][0]
sc.camera = CAMS["CAM_P1_Macro"][0]
# la cámara de Claude en estudio se reutiliza en 3 momentos: reencuadres
cam_keys("CAM_ClaudeEstudio", [(1069, cpos + Vector((0.3, -1.0, 0.2)), cpos + Vector((0, 0, 0.24)), 50), (1140, cpos + Vector((0.25, -0.9, 0.2)), cpos + Vector((0, 0, 0.24)), 55),
                                (1291, cpos + Vector((-0.1, -1.05, 0.12)), cpos + Vector((0, 0, 0.26)), 48), (1380, cpos + Vector((-0.1, -0.9, 0.14)), cpos + Vector((0, 0, 0.26)), 52)])

# textos del plano 3 (cifras verificadas en koenigsegg.com)
c3 = CAMS["CAM_P3_Grua"][0]
popup_text("TXT_9marchas", "9 MARCHAS", M["white3d"], c3, (0, 1.2, -3.2), 0.22, fr(11.95), 568)
popup_text("TXT_7embragues", "7 EMBRAGUES", M["orange3d"], c3, (0, 0.92, -3.2), 0.22, fr(12.85), 568)
popup_text("TXT_90kg", "90 KG", M["orange3d"], c3, (0, 0.62, -3.2), 0.24, fr(15.0), 568)
# plano 5: UPOD 7 -> 4 y aviso de esquema ilustrativo
c5 = CAMS["CAM_P5_Esquema"][0]
popup_text("TXT_UPOD", "UPOD", M["orange3d"], c5, (0, 0.45, -2.5), 0.094, fr(28.9), 1066)
popup_text("TXT_7a4", "7  >  4", M["orange3d"], c5, (0, -0.37, -2.5), 0.1, fr(32.65), 1066)
popup_text("TXT_Ilustrativo", "ESQUEMA ILUSTRATIVO", M["grey3d"], c5, (0, -0.51, -2.5), 0.031, 845, 1066)
# números de marcha junto a cada par (miran siempre a la cámara)
for g in range(9):
    t = text3d(f"TXT_Marcha{g+1}", str(g + 1), M["orange3d"] if g in (3, 6) else M["white3d"], size=0.035, parent=LR, loc=(0.2, -0.24 + g * 0.06, 0.0))
    cr = t.constraints.new("COPY_ROTATION"); cr.target = c5
    key_hide(t, 1, True); key_hide(t, 841, False); key_hide(t, 1069, True)

# ----------------------------------------------------------------- visemas, parpadeo y gestos
def visemes(mouth, line, axis, closed, open_amt, idle_scale):
    t0 = line["at"]
    for i, (a, b) in enumerate(line["w"]):
        a += t0; b += t0
        amt = open_amt * (0.75 + 0.25 * ((i * 37) % 5) / 4)
        fa, fb = fr(a), max(fr(b), fr(a) + 2)
        s = list(idle_scale); s[axis] = closed; key_scale(mouth, fa - 1, s)
        s = list(idle_scale); s[axis] = amt; key_scale(mouth, (fa + fb) // 2, s)
        s = list(idle_scale); s[axis] = closed; key_scale(mouth, fb + 1, s)

key_scale(CL["mouth"], 1, (1, 0.45, 1)); key_scale(AL["mouth"], 1, (1.6, 0.5, 0.25))
for line in VOICES:
    if line["who"] == "Claude":
        visemes(CL["mouth"], line, 1, 0.45, 1.6, (1, 0.45, 1))
    else:
        visemes(AL["mouth"], line, 2, 0.25, 1.1, (1.6, 0.5, 0.25))

def blink(eyes, f, axis_scale):
    for e in eyes:
        s0 = list(axis_scale)
        key_scale(e, f, s0); s1 = list(s0); s1[2 if e.name.startswith("ALEX") else 1] = 0.1
        key_scale(e, f + 3, s1); key_scale(e, f + 6, s0)
for f in range(40, END, 97):
    blink(AL["eyes"], f, (1, 1, 1))
for f in range(25, END, 83):
    blink(CL["eyes"], f, (1.15, 1, 1))
# Claude: ojos muy abiertos en las sorpresas
for t in (24.3, 51.0):
    for e in CL["eyes"]:
        key_scale(e, fr(t) - 2, (1.15, 1, 1)); key_scale(e, fr(t) + 3, (1.4, 1.35, 1.35)); key_scale(e, fr(t + 2.6), (1.4, 1.35, 1.35)); key_scale(e, fr(t + 3.0), (1.15, 1, 1))

# respiración de Alex
sp = AL["spine"]
for f in range(1, END + 1, 60):
    key_scale(sp, f, (1, 1, 1)); key_scale(sp, f + 30, (1.015, 1.02, 1.01))
# gestos de Alex (brazo derecho = s=1 mira a -Y, explica) en sus líneas visibles
shR, elR = AL["arms"][1]; shL, elL = AL["arms"][-1]
key_rot(elR, 1, (0, 0, 0)); key_rot(shR, 1, (0, math.radians(8), 0))
for a, b in ((0.3, 2.8), (5.2, 8.1), (54.2, 56.6)):
    key_rot(elR, fr(a), (0, 0, 0)); key_rot(elR, fr(a) + 8, (math.radians(-75), 0, math.radians(-20)))
    key_rot(elR, fr((a + b) / 2), (math.radians(-60), 0, math.radians(-35))); key_rot(elR, fr(b) - 6, (math.radians(-80), 0, math.radians(-15))); key_rot(elR, fr(b) + 6, (0, 0, 0))
# en el plano 8 Alex se gira y mira a cámara
key_rot(AL["root"], 1620, (0, 0, WS_ALEX[1])); key_rot(AL["root"], 1621, (0, 0, math.radians(-12))); key_rot(AL["root"], 1800, (0, 0, math.radians(-12)))
hd = AL["head"]
key_rot(hd, 1, (0, 0, 0))
for a in (0.5, 5.4, 54.3):
    key_rot(hd, fr(a), (0, 0, 0)); key_rot(hd, fr(a) + 6, (math.radians(-6), 0, 0)); key_rot(hd, fr(a) + 14, (0, 0, 0))
# Claude: gestos
hpC = CL["head"]; aR = CL["arms"][1]; aL = CL["arms"][-1]
key_rot(hpC, 1, (0, 0, 0)); key_rot(aR, 1, (0, 0, 0)); key_rot(aL, 1, (0, 0, 0))
for t, tilt in ((9.0, 12), (24.3, -10), (35.8, 14), (43.1, -12), (51.0, 10), (57.2, 8)):
    key_rot(hpC, fr(t) - 3, (0, 0, 0)); key_rot(hpC, fr(t) + 6, (0, math.radians(tilt), 0)); key_rot(hpC, fr(t + 1.6), (0, math.radians(tilt), 0)); key_rot(hpC, fr(t + 2.2), (0, 0, 0))
# brazos arriba en "¿Siete embragues?" y súplica al final
for t in (24.3,):
    for s, arm in ((1, aR), (-1, aL)):
        key_rot(arm, fr(t) - 2, (0, 0, 0)); key_rot(arm, fr(t) + 5, (0, s * math.radians(150), 0)); key_rot(arm, fr(t + 1.2), (0, s * math.radians(140), 0)); key_rot(arm, fr(t + 1.6), (0, 0, 0))
for s, arm in ((1, aR), (-1, aL)):
    key_rot(arm, fr(57.1), (0, 0, 0)); key_rot(arm, fr(57.5), (math.radians(-70), s * math.radians(-30), 0)); key_rot(arm, 1800, (math.radians(-70), s * math.radians(-30), 0))
# saltito de Claude al hablar
cr = CL["root"]
for line in VOICES:
    if line["who"] == "Claude":
        f0 = fr(line["at"])
        z0 = 0.0
        for k in range(3):
            pass
