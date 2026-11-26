# DESPIECE 3D DE LOS FRENOS (26-11-2026) · vertical 9:16, 30 fps, ~26,6 s
# Alex = Diego (España). Clod NO habla: gestos de fondo. Taller, coche y personajes: los mismos que el despiece del neumático.
# La rueda delantera estalla en trozos, el freno sale flotando y se explica: líquido -> pistón -> pinza -> pastillas -> disco
# -> calor -> canales de ventilación. Consejo (chirrido / vibración) con pastilla nueva frente a gastada. Síguenos.
import bpy, math, json, os
import numpy as np
from mathutils import Vector, Matrix, Euler
BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
_SRC = open(BASE + r"\videos_3d\despiece_neumatico\despiece_neumatico_v2.py", encoding="utf-8").read()
exec(_SRC[:_SRC.index("# ---------------------------------------------------------------- RUEDA PROTAGONISTA")])
DD = BASE + r"\videos_3d\despiece_frenos"
FIN = 800

# ---------------------------------------------------------------- voz de Alex (Diego): tiempos absolutos de cada palabra
VOZ = json.load(open(DD + r"\voces_frenos.json", encoding="utf-8"))
def T(i, j, fin=False):
    l = VOZ["lineas"][i]; w = l["words"][j]; return l["at"] + (w[2] if fin else w[1])
def FW(i, j, fin=False): return F(T(i, j, fin))

# ---------------------------------------------------------------- rueda delantera izquierda (estalla) y freno real
NR = {"__name__": "nr"}; exec(open(D_ + r"\neumatico_real.py", encoding="utf-8").read(), NR)
FR = {"__name__": "fr"}; exec(open(D_ + r"\freno_real.py", encoding="utf-8").read(), FR)
for n in ("COCHE_Disco-1", "COCHE_Pinza-1"):
    o = bpy.data.objects.get(n)
    if o: o.hide_render = True; o.hide_viewport = True
W0 = Vector(CAR.location) + Vector((X_DEL, -Y_RUEDA, Z_RUEDA))
WB0 = Vector(CAR.location) + Vector((X_DEL, -0.60, Z_RUEDA))
ROT0 = (R(90), R(-35), 0)
P = Vector((-1.30, -1.05, 1.00)); ROTP = (R(90), R(-35), R(-28))
RUEDA = bpy.data.objects.get("RUEDA_DI")
if RUEDA is None:
    Mc = dict(M); Mc["goma"] = GOMA_C; Mc["llanta"] = LLANTA_C; Mc["llanta_osc"] = LLOSC_C
    RUEDA = T_["rueda"]("RUEDA_DI", tuple(W0), (R(90), 0, 0), detalle="bajo", M=Mc, col=CD)
NEU = bpy.data.objects["RUEDA_DI_Neumatico"]; LLA = bpy.data.objects["RUEDA_DI_Llanta"]
MR = NR["materiales_reales"]()
TROZOS = bpy.data.objects.get("D_Trozos")
if TROZOS is None:
    TROZOS, V2 = NR["trozos_irregulares"](T_, "D_Trozos", MR["goma"])
    CD.objects.link(TROZOS); TROZOS.parent = RUEDA
    TROZOS.shape_key_add(name="Basis", from_mix=False); kb = TROZOS.shape_key_add(name="explota", from_mix=False)
    kb.data.foreach_set("co", np.array(V2, dtype=np.float32).ravel()); kb.value = 0.0
O = FR["construir_freno"](CD)
FRENO = O["raiz"]; FRENO.rotation_mode = 'XYZ'
for k in ("pinza", "pad_int", "pad_ext", "soporte", "disco_ext", "piston", "pinza_cuerpo"): O[k].rotation_mode = 'XYZ'
# pastillas sueltas para el consejo: nueva y gastada
Q = Vector((0.62, -1.95, 1.12))
M_PAD = Matrix(((0, 1, 0), (0, 0, -1), (-1, 0, 0)))
PADS = {}
for nombre, dz, gast in (("PAD_Nueva", 0.075, False), ("PAD_Gastada", -0.075, True)):
    e = bpy.data.objects.new(nombre + "_R", None); CD.objects.link(e)
    FR["pastilla"](nombre, CD, O["M"], e, 0.0, +1, gastada=gast)
    e.rotation_mode = 'XYZ'; e.rotation_euler = M_PAD.to_euler(); e.location = Q + Vector((0, 0, dz)) - M_PAD @ Vector((0.122, 0, 0))
    PADS[nombre] = (e, Q + Vector((0, 0, dz)))
# propiedades de la escena que mueven los materiales
for p_ in ("xray", "xray_pinza", "calor", "flujo_luz", "aire"): sc[p_] = 0.0
# la pinza también se ve con rayos X (rojo transparente con aristas): copia de la función de la rueda con otra propiedad
def xray_prop(m, prop):
    if m.get("xr_" + prop): return
    nt = m.node_tree; out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    src = out.inputs["Surface"].links[0].from_socket
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'VIEW_LAYER'; at.attribute_name = prop
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.3
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1.0, 0.18, 0.12, 1); em.inputs["Strength"].default_value = 3.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    m1 = nt.nodes.new("ShaderNodeMixShader"); m2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], m1.inputs[0]); nt.links.new(tr.outputs[0], m1.inputs[1]); nt.links.new(em.outputs[0], m1.inputs[2])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 0.85
    nt.links.new(at.outputs["Fac"], mul.inputs[0]); nt.links.new(mul.outputs[0], m2.inputs[0])
    nt.links.new(src, m2.inputs[1]); nt.links.new(m1.outputs[0], m2.inputs[2]); nt.links.new(m2.outputs[0], out.inputs["Surface"])
    for a, v in (("surface_render_method", 'DITHERED'), ("use_transparent_shadow", True)):
        try: setattr(m, a, v)
        except Exception: pass
    m["xr_" + prop] = 1
xray_prop(O["M"]["pinza"], "xray_pinza"); xray_prop(O["M"]["goma"], "xray_pinza")

# ================================================================ ANIMACIÓN
for o in list(CD.all_objects): o.animation_data_clear()
if TROZOS.data.shape_keys.animation_data: TROZOS.data.shape_keys.animation_data_clear()
if sc.animation_data: sc.animation_data_clear()
def kl(o, f, loc=None, rot=None):
    if loc is not None: o.location = loc; o.keyframe_insert("location", frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=f)
def vis(o, f, ver):
    for oo in [o] + list(o.children_recursive):
        if oo.name.startswith("FR_Cort"): continue
        oo.hide_render = not ver; oo.hide_viewport = not ver
        oo.keyframe_insert("hide_render", frame=f); oo.keyframe_insert("hide_viewport", frame=f)
def kp(prop, f, v): sc[prop] = v; sc.keyframe_insert(f'["{prop}"]', frame=f)

EST = 111                       # estalla la rueda (justo después de "rueda")
B0, C0, D0, E0, A2, INS, CTA = 139, 226, 331, 417, 525, 618, 694
CORTES = [1, B0, C0, D0, E0, A2, INS, CTA, FIN + 1]
Z0 = Vector((0, 0, 0))
# --- la rueda: rayos X, estalla en trozos, la llanta cae; vuelve entera en el consejo
kp("xray", 1, 0.0); kp("xray", 90, 0.0); kp("xray", 102, 1.0); kp("xray", EST + 16, 1.0); kp("xray", EST + 26, 0.0)
vis(NEU, 1, True); vis(NEU, EST, False); vis(NEU, A2, True)
vis(TROZOS, 1, False); vis(TROZOS, EST, True); vis(TROZOS, EST + 42, False)
kbt = TROZOS.data.shape_keys.key_blocks["explota"]
for f_, v in ((EST - 1, 0.0), (EST, 0.0), (EST + 2, 0.22), (EST + 6, 0.52), (EST + 14, 0.80), (EST + 28, 0.95), (EST + 40, 1.0)):
    kbt.value = v; kbt.keyframe_insert("value", frame=f_)
kl(LLA, 1, Z0, (0, 0, 0)); kl(LLA, EST, Z0, (0, 0, 0)); kl(LLA, EST + 7, (0.05, -0.30, 0.10), (R(10), 0, 0)); kl(LLA, EST + 16, (0.12, -1.3, 0.25), (R(25), R(8), 0))
kl(LLA, A2 - 1, (0.12, -1.3, 0.25), None); kl(LLA, A2, Z0, (0, 0, 0))
vis(LLA, 1, True); vis(LLA, EST + 17, False); vis(LLA, A2, True)
# --- el freno: dentro de la rueda -> sale flotando -> se queda delante (P) -> vuelve a su sitio en el consejo
kl(FRENO, 1, WB0, ROT0); kl(FRENO, EST + 2, WB0, ROT0)
kl(FRENO, EST + 12, WB0 + Vector((0.02, -0.45, 0.16)), (R(90), R(-35), R(-10)))
kl(FRENO, B0 - 2, P, ROTP); kl(FRENO, A2 - 1, P, ROTP); kl(FRENO, A2, WB0, ROT0); kl(FRENO, FIN, WB0, ROT0)
vis(FRENO, 1, True); vis(FRENO, A2, False); vis(FRENO, FIN, False)
# --- el disco gira con la rueda y frena hasta pararse
g = O["giro"]
kl(g, 1, None, (0, 0, 0)); kl(g, EST, None, (0, 0, 0)); kl(g, D0, None, (0, 0, R(10 * (D0 - EST)))); kl(g, D0 + 45, None, (0, 0, R(10 * (D0 - EST) + 230)))
# --- líquido y pistón (plano B)
mp = O["M"]["liquido"].node_tree.nodes[O["M"]["liquido"]["mapping"]]
for f_, v in ((1, 0.0), (B0 + 15, 0.0), (FW(1, 3) + 40, 2.6), (C0, 3.2)):
    mp.inputs["Location"].default_value[0] = v; mp.inputs["Location"].keyframe_insert("default_value", index=0, frame=f_)
kp("flujo_luz", 1, 0.0); kp("flujo_luz", FW(1, 3) - 4, 0.0); kp("flujo_luz", FW(1, 3) + 4, 1.0); kp("flujo_luz", C0 + 20, 1.0); kp("flujo_luz", C0 + 40, 0.0)
kp("xray_pinza", 1, 0.0); kp("xray_pinza", B0 + 6, 0.0); kp("xray_pinza", B0 + 20, 1.0); kp("xray_pinza", C0 - 1, 1.0); kp("xray_pinza", C0, 0.0)
GAP = 0.015
for o, z_ini in ((O["piston"], -GAP), (O["pad_int"], -GAP)):
    kl(o, 1, (0, 0, z_ini)); kl(o, FW(1, 6), (0, 0, z_ini)); kl(o, FW(1, 8) + 6, (0, 0, 0))
# --- la pinza aprieta: el cuerpo desliza y trae la pastilla exterior (plano C)
for o in (O["pinza_cuerpo"], O["pad_ext"]):
    kl(o, 1, (0, 0, GAP)); kl(o, FW(1, 14), (0, 0, GAP)); kl(o, FW(1, 14) + 12, (0, 0, 0))
# --- calor (plano D) y enfriado (plano E)
kp("calor", 1, 0.0); kp("calor", D0 + 4, 0.0); kp("calor", FW(1, 35), 1.0); kp("calor", FW(1, 41), 1.0); kp("calor", FW(1, 43), 0.3); kp("calor", FW(1, 45, True), 0.0)
# --- se abre: la pinza y el soporte se apartan, las pastillas se separan y el disco enseña sus canales (plano E)
kl(O["pinza"], 1, Z0); kl(O["pinza"], E0 + 1, Z0); kl(O["pinza"], E0 + 16, (0.42, 0.06, -0.06))
kl(O["soporte"], 1, Z0); kl(O["soporte"], E0 + 3, Z0); kl(O["soporte"], E0 + 18, (0.36, 0.04, -0.12))
kl(O["pad_int"], E0 + 2, Z0); kl(O["pad_int"], E0 + 18, (0.30, 0.02, -0.10))
kl(O["pad_ext"], E0 + 2, Z0); kl(O["pad_ext"], E0 + 18, (0.30, 0.02, 0.14))
kl(O["disco_ext"], 1, Z0); kl(O["disco_ext"], E0 + 10, Z0); kl(O["disco_ext"], E0 + 28, (0, 0, 0.048))
ai = O["aire"]
kp("aire", 1, 0.0)
for k in range(3):
    f0 = FW(1, 41) - 4 + k * 22
    kl(ai, f0, None, None); ai.scale = (0.78, 0.78, 1); ai.keyframe_insert("scale", frame=f0)
    ai.scale = (1.30, 1.30, 1); ai.keyframe_insert("scale", frame=f0 + 21)
    kp("aire", f0, 0.0); kp("aire", f0 + 5, 1.0); kp("aire", f0 + 15, 1.0); kp("aire", f0 + 21, 0.0)
# --- pastillas del consejo: solo en el inserto
for nombre, (e, c) in PADS.items():
    vis(e, 1, False); vis(e, INS, True); vis(e, CTA, False)
    kl(e, INS, None, e.rotation_euler.copy()); r2 = e.rotation_euler.copy(); r2[2] += R(8); kl(e, CTA - 1, None, r2)

# --- luces: el taller se oscurece cuando el freno flota; luces de estudio en P y en el inserto
LUZ_PERS = {"Key_Pers": ((1.0, -3.2, 2.7), 360, 1.8), "Rim_Pers": ((-2.2, 2.0, 2.8), 420, 1.5), "Fill_Pers": ((-3.4, -2.6, 1.7), 120, 2.0)}
for n, (loc, e_, size) in LUZ_PERS.items():
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, "AREA")); CD.objects.link(o)
    o.data.energy = e_; o.data.size = size; o.location = loc
    o.rotation_euler = (Vector((-0.9, -0.2, 0.9)) - o.location).to_track_quat("-Z", "Y").to_euler()
for o in [x for x in bpy.data.objects if x.type == 'LIGHT' and not x.name.startswith("D_Luz")]:
    if o.data.animation_data: o.data.animation_data_clear()
    e0 = o.data.energy
    for f_, k in ((1, 1.0), (96, 1.0), (118, 0.07), (A2 - 1, 0.07), (A2, 1.0)):
        o.data.energy = e0 * k; o.data.keyframe_insert("energy", frame=f_)
    o.data.energy = e0
LED = M["led"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
if LED.is_linked is False:
    for f_, v in ((1, 6.0), (96, 6.0), (118, 0.25), (A2 - 1, 0.25), (A2, 6.0)):
        LED.default_value = v; LED.keyframe_insert("default_value", frame=f_)
def luz(n, tipo, loc, mira, color, size=1.0):
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, tipo)); CD.objects.link(o)
    o.location = loc; o.data.color = color
    if tipo == 'AREA': o.data.size = size
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if o.data.animation_data: o.data.animation_data_clear()
    return o
L1 = luz("D_LuzClave", 'SPOT', P + Vector((0.9, -1.2, 1.2)), P, (1.0, 0.95, 0.88)); L1.data.spot_size = R(35); L1.data.spot_blend = 0.45
L2 = luz("D_LuzContra", 'AREA', P + Vector((-0.5, 1.0, 0.7)), P, (0.55, 0.72, 1.0), 0.9)
L3 = luz("D_LuzBajo", 'AREA', P + Vector((0.3, -0.7, -0.8)), P, (1.0, 0.75, 0.5), 0.8)
L5 = luz("D_LuzArriba", 'AREA', P + Vector((0.0, -0.2, 1.1)), P, (1.0, 1.0, 1.0), 1.0)
LC = luz("D_LuzCalor", 'POINT', P + Vector((0.0, -0.12, 0.05)), P, (1.0, 0.45, 0.12))
L4 = luz("D_LuzFlash", 'POINT', W0 + Vector((0, -0.25, 0.05)), W0, (1.0, 0.85, 0.6))
for o, e_ in ((L1, 330), (L2, 110), (L3, 14), (L5, 60)):
    for f_, v in ((1, 0), (100, 0), (124, e_), (A2 - 1, e_), (A2, 0)):
        o.data.energy = v; o.data.keyframe_insert("energy", frame=f_)
for f_, v in ((1, 0), (D0 + 4, 0), (FW(1, 35), 18), (FW(1, 41), 18), (FW(1, 43), 4), (FW(1, 45, True), 0), (A2, 0)):
    LC.data.energy = v; LC.data.keyframe_insert("energy", frame=f_)
for f_, v in ((1, 0), (EST - 1, 0), (EST, 140), (EST + 4, 70), (EST + 12, 0)):
    L4.data.energy = v; L4.data.keyframe_insert("energy", frame=f_)
LI = luz("D_LuzInserto", 'SPOT', Q + Vector((-0.30, -0.50, 0.45)), Q, (1.0, 0.96, 0.9)); LI.data.spot_size = R(40); LI.data.spot_blend = 0.5
LI2 = luz("D_LuzInsertoContra", 'AREA', Q + Vector((0.35, 0.35, 0.3)), Q, (0.6, 0.75, 1.0), 0.6)
for o, e_ in ((LI, 45), (LI2, 14)):
    for f_, v in ((1, 0), (INS - 1, 0), (INS, e_), (CTA - 1, e_), (CTA, 0)):
        o.data.energy = v; o.data.keyframe_insert("energy", frame=f_)

# ================================================================ PERSONAJES
ALEX_POS = Vector((-0.62, -0.60, 0)); ALEX_GIRO = -12
sk = MALLA.data.shape_keys
if sk.animation_data and sk.animation_data.action: sk.animation_data.action = None
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
ALEX.animation_data_clear()
ALEX.location = ALEX_POS; ALEX.rotation_euler = (0, 0, R(ALEX_GIRO))
CL = ClodAnim()
for ob in [CL.arm] + list(CL.ctrl.values()) + CL.ojos + [CL.bocaob]:
    ob.animation_data_clear()
    if getattr(ob.data, "shape_keys", None) and ob.data.shape_keys.animation_data: ob.data.shape_keys.animation_data_clear()
def SX(l): return -1 if l == "R" else 1
ALEX.keyframe_insert("location", frame=1); ALEX.keyframe_insert("rotation_euler", frame=1)
todo_reposo(1); sc.frame_set(1); calibrar_palma()
for l in ("R", "L"): brazo_caido(l, 1)
cara(1, "sonrisa", 0.4)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
XC, YC = -1.55, 0.62
hit, loc_h, *_ = sc.ray_cast(dg, Vector((XC, YC, 3.0)), Vector((0, 0, -1)))
CLOD_CAPO = (XC, YC, (loc_h.z if hit else 0.90) - 0.004)
CLOD_GIRO = 10

# ---- Clod (solo gestos)
CL.reposo(1); CL.mover(1, CLOD_CAPO, CLOD_GIRO); CL.cara(1, "contento"); CL.cabeza(1, -6, 0, 10); CL.mirar(1, 0.01, 0.0)
for l in ("R", "L"): CL.brazo_caido(l, 1)
# "Pisas el freno": se agacha como si pisara
CL.aplastar(FW(0, 0), 1.0); CL.aplastar(FW(0, 2) - 6, 0.84); CL.aplastar(FW(0, 2) + 4, 1.0)
# "y el coche se para": el frenazo lo lanza hacia delante
CL.cara(FW(0, 5), "sorpresa"); CL.cuerpo(FW(0, 5), 0, 0, 0); CL.cuerpo(FW(0, 7) - 4, 28, 0, 0); CL.cuerpo(FW(0, 7) + 6, -6, 0, 0); CL.cuerpo(FW(0, 7) + 12, 0, 0, 0)
CL.cabeza(FW(0, 7) - 4, 22, 0, 10); CL.cabeza(FW(0, 7) + 8, -6, 0, 10)
for l in ("R", "L"):
    CL.mano_en(l, FW(0, 7) - 4, (SX(l) * 0.32, -0.30, 0.55)); CL.codo_hacia(l, FW(0, 7) - 4, (SX(l) * 0.70, 0.0, 0.45))
    CL.brazo_caido(l, FW(0, 7) + 12)
# "¿Pero qué pasa dentro de la rueda?": se encoge de hombros y señala la rueda
CL.cara(FW(0, 8), "duda")
for l in ("R", "L"):
    CL.mano_en(l, FW(0, 8) + 2, (SX(l) * 0.30, -0.12, 0.50)); CL.codo_hacia(l, FW(0, 8) + 2, (SX(l) * 0.75, 0.10, 0.40)); CL.pulgar(l, FW(0, 8) + 2, 1.0)
    CL.mano_giro(l, FW(0, 8) + 2, gira=SX(l) * 40)
CL.cara(FW(0, 12), "feliz")
CL.mano_en("R", FW(0, 12) + 2, (-0.30, -0.26, 0.30)); CL.codo_hacia("R", FW(0, 12) + 2, (-0.62, 0.15, 0.45)); CL.pulgar("R", FW(0, 12) + 2, 0.2)
CL.brazo_caido("L", FW(0, 12) + 2)
CL.cabeza(FW(0, 12) + 2, 22, 0, -14); CL.mirar(FW(0, 12) + 2, -0.012, -0.012)
# estalla: se tapa la cara y se asoma
for l in ("R", "L"):
    CL.mano_en(l, EST + 1, (SX(l) * 0.08, -0.26, 0.74)); CL.codo_hacia(l, EST + 1, (SX(l) * 0.55, 0.05, 0.55))
CL.aplastar(EST, 1.0); CL.aplastar(EST + 4, 0.88); CL.aplastar(EST + 12, 1.0); CL.cara(EST + 2, "susto")
CL.mano_en("L", EST + 26, (0.24, -0.12, 0.60)); CL.codo_hacia("L", EST + 26, (0.70, 0.10, 0.45)); CL.cara(EST + 26, "sorpresa")
for l in ("R", "L"): CL.brazo_caido(l, B0 + 10)
CL.cara(B0 + 10, "feliz"); CL.cabeza(B0 + 10, 0, 0, 10)
# consejo: "chirría" -> se tapa los oídos; "vibra el volante" -> tiembla; "no lo dejes" -> dedo que dice no
CL.cara(A2, "contento"); CL.cabeza(A2, -4, 0, 8)
fch = FW(2, 3)
CL.cara(fch - 2, "enfado")
for l in ("R", "L"):
    CL.mano_en(l, fch, (SX(l) * 0.36, -0.02, 0.80)); CL.codo_hacia(l, fch, (SX(l) * 0.80, 0.05, 0.62)); CL.pulgar(l, fch, 0.3)
    CL.mano_en(l, FW(2, 4) - 2, (SX(l) * 0.36, -0.02, 0.81))
fv = FW(2, 6)
for k in range(12):
    CL.cabeza(fv + 2 * k, 0, (3 if k % 2 else -3), 8); CL.aplastar(fv + 2 * k, 1.0 + (0.03 if k % 2 else -0.03))
CL.cabeza(fv + 26, 0, 0, 8); CL.aplastar(fv + 26, 1.0)
for l in ("R", "L"): CL.brazo_caido(l, fv + 4)
fn = FW(2, 9)
CL.cara(fn, "serio")
CL.mano_en("R", fn + 2, (-0.12, -0.22, 0.70)); CL.codo_hacia("R", fn + 2, (-0.55, 0.10, 0.45)); CL.pulgar("R", fn + 2, 0.0)
for k, dx in enumerate((-0.05, 0.05, -0.05, 0.05, 0.0)): CL.mano_en("R", fn + 4 + k * 4, (-0.12 + dx, -0.22, 0.72))
CL.brazo_caido("R", fn + 30); CL.cara(fn + 30, "contento")
# síguenos: salta y pulgar arriba
CL.cara(CTA + 4, "feliz")
CL.salto(CTA + 8, alto=0.20, aire=12)
CL.pulgar_arriba("L", CTA + 30, dur=40)

# ---- Alex
cabeza(1, 0, 0, -6); columna(1, 0, 0, 0)
# "Pisas el freno": la mano baja como un pie en el pedal
f_ = FW(0, 0)
cara(f_, "picaro", 0.6)
mano_en("R", f_, (-0.30, -0.30, 1.06)); codo_hacia("R", f_, (-0.62, 0.05, 1.0)); mano_pose("R", f_, "abierta")
orientar_mano("R", f_, palma_hacia=(0, 0, -1), dedos_hacia=(0, -1, 0))
mano_en("R", FW(0, 2), (-0.30, -0.30, 0.94)); orientar_mano("R", FW(0, 2), palma_hacia=(0, 0, -1), dedos_hacia=(0, -1, 0))
# "y el coche se para": las dos manos dicen ¡alto!
fp = FW(0, 5)
for l in ("R", "L"):
    mano_en(l, fp, (SX(l) * 0.24, -0.40, 1.16)); codo_hacia(l, fp, (SX(l) * 0.55, 0.05, 1.0)); mano_pose(l, fp, "abierta")
    orientar_mano(l, fp, palma_hacia=(0, -1, 0), dedos_hacia=(0, 0, 1))
cabeza(fp, -4, 0, 0); cara(fp, "sorpresa", 0.6)
# "¿Pero qué pasa dentro de la rueda?": señala la rueda
fq = FW(0, 9)
for l in ("L",): brazo_caido(l, fq); mano_pose(l, fq, "relajada")
mano_en("R", fq, (-0.42, -0.14, 1.04)); codo_hacia("R", fq, (-0.75, 0.15, 1.05)); mano_pose("R", fq, "señalar")
orientar_mano("R", fq, dedos_hacia=(-1, 0.45, -0.5), pulgar_hacia=(0, 0, 1))
mano_en("R", FW(0, 14, True) + 6, (-0.44, -0.14, 1.02)); orientar_mano("R", FW(0, 14, True) + 6, dedos_hacia=(-1, 0.45, -0.5), pulgar_hacia=(0, 0, 1))
cabeza(fq, 14, 0, -24); cara(fq, "duda", 0.8); columna(fq, 4, 0, -6)
for l in ("R", "L"): brazo_caido(l, B0 + 30); mano_pose(l, B0 + 30, "relajada")
cabeza(B0 + 30, 0, 0, 0); columna(B0 + 30, 0, 0, 0); cara(B0 + 30, "neutra")
# consejo
kl(ALEX, A2 - 1, ALEX_POS, (0, 0, R(ALEX_GIRO))); kl(ALEX, A2, ALEX_POS, (0, 0, R(-4)))
todo_reposo(A2)
for l in ("R", "L"): brazo_caido(l, A2); mano_pose(l, A2, "relajada")
cara(A2, "duda", 0.5); cabeza(A2, 2, 0, 0); columna(A2, 2, 0, 0)
# "chirría": mano a la oreja
fo = FW(2, 3)
mano_en("R", fo, (-0.16, -0.06, 1.60)); codo_hacia("R", fo, (-0.55, 0.05, 1.30)); mano_pose("R", fo, "abierta")
orientar_mano("R", fo, palma_hacia=(1, 0, 0), dedos_hacia=(0, 0, 1)); cara(fo, "enfado", 0.4); cabeza(fo, 0, -8, 6)
# "o te vibra el volante": agarra un volante que tiembla
fw = FW(2, 6)
for l in ("R", "L"):
    mano_en(l, fw, (SX(l) * 0.19, -0.40, 1.16)); codo_hacia(l, fw, (SX(l) * 0.50, 0.0, 1.0)); mano_pose(l, fw, "puño")
    orientar_mano(l, fw, palma_hacia=(-SX(l), 0, 0), dedos_hacia=(0, 0, 1))
    for k in range(10): mano_en(l, fw + 2 + 2 * k, (SX(l) * 0.19 + (0.012 if k % 2 else -0.012), -0.40, 1.16 + (0.008 if k % 2 else -0.008)))
cara(fw, "duda", 0.9); cabeza(fw, 4, 0, 0)
# "no lo dejes": dedo arriba que dice no
fn2 = FW(2, 9)
brazo_caido("L", fn2); mano_pose("L", fn2, "relajada")
cara(fn2, "enfado", 0.35); cabeza(fn2, 0, 4, 0)
mano_en("R", fn2, (-0.16, -0.30, 1.36)); codo_hacia("R", fn2, (-0.55, 0.05, 1.05)); mano_pose("R", fn2, "señalar")
orientar_mano("R", fn2, dedos_hacia=(0, 0, 1), pulgar_hacia=(1, 0, 0))
for t_, dz in ((0.2, 0.02), (0.4, -0.005), (0.6, 0.015)): mano_en("R", fn2 + int(t_ * 30), (-0.16, -0.30, 1.36 + dz))
brazo_caido("R", CTA - 6); mano_pose("R", CTA - 6, "relajada")
# síguenos: pulgar arriba
kl(ALEX, CTA - 1, ALEX_POS, (0, 0, R(-4))); kl(ALEX, CTA, ALEX_POS, (0, 0, R(ALEX_GIRO)))
cara(CTA, "sonrisa"); cabeza(CTA, 2, -4, -10)
mano_en("R", CTA + 8, (-0.14, -0.32, 1.22)); codo_hacia("R", CTA + 8, (-0.70, 0.10, 0.80)); mano_pose("R", CTA + 8, "pulgar")
orientar_mano("R", CTA + 8, pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", CTA + 14, (-0.14, -0.33, 1.27)); orientar_mano("R", CTA + 14, pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", FIN, (-0.14, -0.32, 1.25)); orientar_mano("R", FIN, pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
parpadeo(FIN - 25, 1.0, lado="L")
parpadeos(1, FIN, evitar=(FIN - 25,))
CL.parpadeos(1, FIN, cada=(55, 85), evitar=[(EST - 30, EST + 60), (CTA, CTA + 50)])
respirar(1, FIN, periodo=64, amplitud=1.5)
LINEAS = [{"at": 0, "words": [[w[0], l["at"] + w[1], l["at"] + w[2]] for w in l["words"]]} for l in VOZ["lineas"]]
hablar(LINEAS)
suavizar(); CL.suavizar()
ad = sk.animation_data
if ad and ad.action:
    try: cv = list(ad.action.fcurves)
    except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
    for fc in cv:
        for k in fc.keyframe_points:
            if k.interpolation != 'CONSTANT': k.interpolation = 'BEZIER'
        fc.update()
_m["brillo_led"](sc, umbral=6.0)

# ================================================================ CÁMARA
cam = bpy.data.objects.get("CAM")
if cam is None:
    cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam)
cam.animation_data_clear(); cam.data.animation_data_clear()
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.005
def ck(f, loc, t, lens, dof=None, fstop=2.8):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens; cam.data.dof.use_dof = dof is not None
    cam.data.dof.focus_distance = (Vector(dof) - Vector(loc)).length if dof else 10.0; cam.data.dof.aperture_fstop = fstop
    for p_ in ("location", "rotation_euler"): cam.keyframe_insert(p_, frame=f)
    cam.data.keyframe_insert("lens", frame=f)
    for p_ in ("use_dof", "focus_distance", "aperture_fstop"): cam.data.dof.keyframe_insert(p_, frame=f)
MP = Matrix.Translation(P) @ Euler(ROTP).to_matrix().to_4x4()
def cl(f, pos, mira, lens, fstop=None):
    """Cámara en coordenadas del freno (cuando está quieto en P)."""
    a = MP @ Vector(pos); b = MP @ Vector(mira)
    ck(f, tuple(a), tuple(b), lens, dof=tuple(b) if fstop else None, fstop=fstop or 2.8)
# plano A: Alex, el coche y Clod -> entramos en la rueda -> estalla -> el freno sale flotando
ck(1, (-0.85, -3.30, 1.45), (-0.88, -0.10, 0.98), 27)
ck(60, (-0.88, -3.00, 1.40), (-0.95, -0.10, 0.90), 28)
ck(80, (-1.05, -2.05, 0.95), (-1.22, 0.0, 0.45), 31)
ck(100, (-1.10, -1.30, 0.62), tuple(W0 + Vector((0, 0, 0.02))), 34)
ck(EST + 10, (-1.08, -1.75, 0.78), tuple(W0 + Vector((0, -0.2, 0.1))), 33)
ck(B0 - 1, tuple(MP @ Vector((0.25, -0.30, 0.85))), tuple(P), 36)
# plano B: líquido y pistón (pinza con rayos X)
cl(B0, (0.52, -0.15, -0.42), (0.13, 0.0, -0.05), 40, 5.6); cl(C0 - 1, (0.47, -0.18, -0.37), (0.13, 0.0, -0.05), 42, 5.6)
# plano C: la pinza aprieta las pastillas contra el disco, que gira
cl(C0, (0.50, -0.42, 0.50), (0.07, 0.0, 0.0), 36, 6.0); cl(D0 - 1, (0.45, -0.40, 0.46), (0.07, 0.0, 0.0), 38, 6.0)
# plano D: roce = calor
cl(D0, (0.12, -0.48, 0.62), (0.04, 0.0, 0.0), 34); cl(E0 - 1, (0.14, -0.42, 0.56), (0.04, 0.0, 0.0), 36)
# plano E: se abre y se ven los canales por dentro
cl(E0, (0.62, -0.40, 0.42), (0.08, 0.0, 0.02), 34); cl(E0 + 30, (0.58, -0.30, 0.16), (0.10, 0.0, 0.025), 40, 6.0)
cl(A2 - 1, (0.54, -0.28, 0.14), (0.10, 0.0, 0.025), 42, 6.0)
# consejo: Alex con Clod de fondo -> inserto pastilla nueva / gastada -> Alex
ck(A2, (-0.30, -2.35, 1.45), (-0.95, -0.05, 1.15), 28); ck(INS - 1, (-0.31, -2.25, 1.45), (-0.95, -0.05, 1.15), 28)
ck(INS, tuple(Q + Vector((-0.50, -0.26, 0.14))), tuple(Q), 48, dof=tuple(Q), fstop=5.6)
ck(CTA - 1, tuple(Q + Vector((-0.46, -0.24, 0.13))), tuple(Q), 50, dof=tuple(Q), fstop=5.6)
# síguenos
ck(CTA, (-0.85, -3.75, 1.30), (-0.88, -0.25, 0.92), 28); ck(FIN, (-0.86, -3.50, 1.28), (-0.88, -0.25, 0.94), 28)

def _curvas(idb):
    ad_ = getattr(idb, "animation_data", None)
    if not ad_ or not ad_.action: return []
    try: return list(ad_.action.fcurves)
    except Exception: return [fc for l in ad_.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
fin_plano = {c - 1 for c in CORTES[1:]}
for idb in (cam, cam.data, FRENO, ALEX, LLA):
    for fc in _curvas(idb):
        for k in fc.keyframe_points:
            if int(round(k.co[0])) in fin_plano: k.interpolation = 'CONSTANT'
        fc.update()
for fc in _curvas(g):
    for k in fc.keyframe_points:
        if k.co[0] < D0 - 0.5: k.interpolation = 'LINEAR'
    fc.update()
for fc in _curvas(sc):
    for k in fc.keyframe_points: k.interpolation = 'LINEAR'

sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 67
sc.eevee.taa_render_samples = 48; sc.render.fps = 30; sc.frame_start, sc.frame_end = 1, FIN
try: sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45; sc.render.motion_blur_position = 'START'
except Exception: pass
sc.view_settings.exposure = -0.1

# ================================================================ ANCLAS para los rótulos del montaje (pantalla 0-1, y hacia arriba)
ZPI = FR["Z_IN"] - FR["FRIC"] - FR["PLACA"] - FR["SHIM"]
PUNTOS = {"liquido": (O["latiguillo"], Vector((0.265, -0.02, ZPI - 0.065))), "piston": (O["piston"], Vector((0.122, 0.0, ZPI - 0.005))),
          "pinza": (O["pinza_cuerpo"], Vector((0.17, 0.0, -0.01))), "pastillas": (O["pad_ext"], Vector((0.146, 0.02, FR["Z_OUT"] + 0.008))),
          "disco": (FRENO, Vector((0.03, -0.149, 0.0))), "calor": (FRENO, Vector((0.06, -0.10, FR["Z_OUT"]))),
          "canales": (FRENO, Vector((0.148, -0.01, 0.0)))}
def proy(f):
    mc = cam.matrix_world; lens = cam.data.lens; th = 12.0 / lens; tw = th * 9 / 16
    def pp(p):
        q = mc.inverted() @ p
        if q.z >= -1e-4: return None
        return [round(0.5 + (q.x / -q.z) / (2 * tw), 4), round(0.5 + (q.y / -q.z) / (2 * th), 4)]
    return pp
ANCLAS = {}
for f in list(range(B0, A2)) + list(range(INS, CTA)):
    sc.frame_set(f); pp = proy(f); d = {}
    if f < A2:
        for k, (ob, lp) in PUNTOS.items(): d[k] = pp(ob.matrix_world @ lp)
    else:
        for nombre, (e, c) in PADS.items(): d[nombre] = pp(c)
    ANCLAS[f] = d
json.dump({"anclas": ANCLAS, "cortes": CORTES, "fin": FIN}, open(DD + r"\anclas_frenos.json", "w"))
sc.frame_set(1)
result = {"ok": True, "fin": FIN, "P": list(P), "clod": list(CLOD_CAPO), "hit": bool(hit), "cortes": CORTES}
