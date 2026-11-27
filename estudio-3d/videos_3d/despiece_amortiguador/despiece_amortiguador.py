# DESPIECE 3D DEL AMORTIGUADOR (27-11-2026) · vertical 9:16, 30 fps, 30,5 s
# Alex = Diego (España). Clod NO habla: gestos. Taller, coche y personajes: los del despiece del neumático y de los frenos.
# Clod bota en el capó ("como Clod") -> rayos X a la rueda -> estalla -> sale el amortiguador -> muelle (aguanta el peso)
# -> se quita el muelle y el cuerpo se vuelve transparente (frena el rebote) -> vástago, pistón y aceite -> válvulas con
# el aceite pasando -> calor. Consejo (flota / cabecea / se balancea / pierde aceite) con amortiguador nuevo frente a gastado
# y el dato del RACE en el montaje. Mejoras frente a los frenos: rebote amortiguado de Clod, gráfico del rebote, temblor de
# cámara en la explosión, plano corto de Alex para el aviso final y cierre con "síguenos".
import bpy, math, json, os
import numpy as np
from mathutils import Vector, Matrix, Euler
BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
_SRC = open(BASE + r"\videos_3d\despiece_neumatico\despiece_neumatico_v2.py", encoding="utf-8").read()
exec(_SRC[:_SRC.index("# ---------------------------------------------------------------- RUEDA PROTAGONISTA")])
DD = BASE + r"\videos_3d\despiece_amortiguador"
FIN = 915

VOZ = json.load(open(DD + r"\voces_amortiguador.json", encoding="utf-8"))
def T(i, j, fin=False):
    l = VOZ["lineas"][i]; w = l["words"][j]; return l["at"] + (w[2] if fin else w[1])
def FW(i, j, fin=False): return F(T(i, j, fin))

# ---------------------------------------------------------------- rueda delantera izquierda (estalla) y amortiguador real
NR = {"__name__": "nr"}; exec(open(D_ + r"\neumatico_real.py", encoding="utf-8").read(), NR)
AMm = {"__name__": "am"}; exec(open(D_ + r"\amortiguador_real.py", encoding="utf-8").read(), AMm)
W0 = Vector(CAR.location) + Vector((X_DEL, -Y_RUEDA, Z_RUEDA))
WS0 = Vector(CAR.location) + Vector((X_DEL, -0.50, Z_RUEDA - 0.12))
ROT0 = (R(-8), 0, 0)
P = Vector((-1.30, -1.05, 0.70)); ROTP = (0, 0, R(-24))
PC = P + Vector((0, 0, 0.27))
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
O = AMm["construir_amortiguador"](CD, "AM")
AMO = O["raiz"]; AMO.rotation_mode = 'XYZ'
VAS = O["vastago"]; MUE = O["muelle"]; FUE = O["fuelle"]; COP = O["copela"]
L_MU = AMm["L_MUELLE"]; L_FU = AMm["Z_COPELA"] - 0.04 - AMm["Z_FUELLE0"]
# inserto: amortiguador nuevo y gastado (más pequeños) frente a una cámara aparte
Q = Vector((0.62, -1.95, 1.12))
DQ = Vector((-0.50, -0.26, 0.14)).normalized()
RQ = Vector((-DQ.y, DQ.x, 0)).normalized()               # derecha de la cámara del inserto
ANG = math.atan2(DQ.y, DQ.x) + math.pi / 2
INSERTO = {}
for pref, lado, gast in (("AN", -1, False), ("AG", 1, True)):
    o2 = AMm["construir_amortiguador"](CD, pref, interior=False, gastado=gast)
    r_ = o2["raiz"]; r_.scale = (0.55, 0.55, 0.55); r_.rotation_mode = 'XYZ'; r_.rotation_euler = (0, 0, ANG)
    r_.location = Q + RQ * (0.062 * lado) - Vector((0, 0, 0.14))
    INSERTO[pref] = (r_, r_.location + Vector((0, 0, 0.30 * 0.55)))
for p_ in ("xray", "xray_amo", "calor"): sc[p_] = 0.0
def xray_prop(m, prop):
    if m.get("xr_" + prop): return
    nt = m.node_tree; out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    src = out.inputs["Surface"].links[0].from_socket
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'VIEW_LAYER'; at.attribute_name = prop
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.3
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.35, 0.75, 1.0, 1); em.inputs["Strength"].default_value = 2.2
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    m1 = nt.nodes.new("ShaderNodeMixShader"); m2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], m1.inputs[0]); nt.links.new(tr.outputs[0], m1.inputs[1]); nt.links.new(em.outputs[0], m1.inputs[2])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 0.9
    nt.links.new(at.outputs["Fac"], mul.inputs[0]); nt.links.new(mul.outputs[0], m2.inputs[0])
    nt.links.new(src, m2.inputs[1]); nt.links.new(m1.outputs[0], m2.inputs[2]); nt.links.new(m2.outputs[0], out.inputs["Surface"])
    for a, v in (("surface_render_method", 'DITHERED'), ("use_transparent_shadow", True)):
        try: setattr(m, a, v)
        except Exception: pass
    m["xr_" + prop] = 1
for k in ("pintura", "tubo"): xray_prop(O["M"][k], "xray_amo")

# ================================================================ ANIMACIÓN
for o in list(CD.all_objects): o.animation_data_clear()
if TROZOS.data.shape_keys.animation_data: TROZOS.data.shape_keys.animation_data_clear()
if sc.animation_data: sc.animation_data_clear()
def kl(o, f, loc=None, rot=None):
    if loc is not None: o.location = loc; o.keyframe_insert("location", frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=f)
def ks(o, f, s): o.scale = s; o.keyframe_insert("scale", frame=f)
def vis(o, f, ver):
    for oo in [o] + list(o.children_recursive):
        oo.hide_render = not ver; oo.hide_viewport = not ver
        oo.keyframe_insert("hide_render", frame=f); oo.keyframe_insert("hide_viewport", frame=f)
def kp(prop, f, v): sc[prop] = v; sc.keyframe_insert(f'["{prop}"]', frame=f)

EST = 120
B0, C0, D0, E0, F0, A2, INS, A3, CTA = 150, 214, 264, 357, 453, 533, 650, 719, 850
CORTES = [1, B0, C0, D0, E0, F0, A2, INS, A3, CTA, FIN + 1]
Z0 = Vector((0, 0, 0))
# --- la rueda: rayos X, estalla en trozos, la llanta cae; vuelve entera en el consejo
kp("xray", 1, 0.0); kp("xray", 88, 0.0); kp("xray", 100, 1.0); kp("xray", EST + 16, 1.0); kp("xray", EST + 26, 0.0)
vis(NEU, 1, True); vis(NEU, EST, False); vis(NEU, A2, True)
vis(TROZOS, 1, False); vis(TROZOS, EST, True); vis(TROZOS, EST + 42, False)
kbt = TROZOS.data.shape_keys.key_blocks["explota"]
for f_, v in ((EST - 1, 0.0), (EST, 0.0), (EST + 2, 0.22), (EST + 6, 0.52), (EST + 14, 0.80), (EST + 28, 0.95), (EST + 40, 1.0)):
    kbt.value = v; kbt.keyframe_insert("value", frame=f_)
kl(LLA, 1, Z0, (0, 0, 0)); kl(LLA, EST, Z0, (0, 0, 0)); kl(LLA, EST + 7, (0.05, -0.30, 0.10), (R(10), 0, 0)); kl(LLA, EST + 16, (0.12, -1.3, 0.25), (R(25), R(8), 0))
kl(LLA, A2 - 1, (0.12, -1.3, 0.25), None); kl(LLA, A2, Z0, (0, 0, 0))
vis(LLA, 1, True); vis(LLA, EST + 17, False); vis(LLA, A2, True)
# --- el amortiguador: dentro del paso de rueda -> sale -> se queda flotando en P -> desaparece en el consejo
kl(AMO, 1, WS0, ROT0); kl(AMO, EST + 2, WS0, ROT0)
kl(AMO, EST + 12, WS0 + Vector((0.02, -0.52, 0.14)), (R(-4), 0, R(-10)))
kl(AMO, B0 - 2, P, ROTP); kl(AMO, A2 - 1, P, ROTP)
vis(AMO, 1, True); vis(AMO, A2, False)
# --- recorrido del vástago (d > 0 = entra): copela, muelle y fuelle le siguen
def rec(f, d):
    kl(VAS, f, (0, 0, -d)); ks(MUE, f, (1, 1, (L_MU - d) / L_MU)); ks(FUE, f, (1, 1, (L_FU - d) / L_FU))
rec(1, 0.0); rec(B0 + 6, 0.0)
for f_, d in ((B0 + 20, 0.065), (B0 + 33, -0.022), (B0 + 44, 0.03), (B0 + 54, -0.008), (B0 + 62, 0.0)): rec(f_, d)
rec(C0, 0.0)
# muelle, fuelle y copela se van hacia arriba (despiece) al empezar el plano del amortiguador
for o, z0 in ((MUE, AMm["Z_MUELLE0"]), (FUE, AMm["Z_FUELLE0"]), (COP, 0.0)):
    kl(o, C0 + 2, Vector((0, 0, z0))); kl(o, C0 + 24, Vector((0.0, 0.0, z0 + 0.42)))
for o in (MUE, FUE, COP): vis(o, 1, True); vis(o, C0 + 25, False)
kp("xray_amo", 1, 0.0); kp("xray_amo", C0 + 4, 0.0); kp("xray_amo", C0 + 16, 1.0); kp("xray_amo", A2 - 1, 1.0); kp("xray_amo", A2, 0.0)
# "cuando la rueda sube, el vástago mete el pistón en el aceite"
kl(VAS, D0 + 8, (0, 0, 0.0)); kl(VAS, FW(1, 15), (0, 0, -0.012)); kl(VAS, FW(1, 23, True) + 4, (0, 0, -0.075))
# válvulas: sigue bajando despacio y el aceite pasa por los agujeros del pistón
kl(VAS, F0 - 2, (0, 0, -0.105))
# calor: va y viene (bache tras bache) y el aceite se calienta
for k in range(5):
    kl(VAS, F0 + 8 + k * 14, (0, 0, -0.105 + (0.016 if k % 2 == 0 else -0.004)))
kl(VAS, A2 - 1, (0, 0, -0.10))
kp("calor", 1, 0.0); kp("calor", F0 + 6, 0.0); kp("calor", FW(1, 39), 1.0); kp("calor", A2 - 1, 1.0); kp("calor", A2, 0.0)
# chispas de aceite que suben por las válvulas (ciclos de 16 fotogramas)
for s in O["flujo"]:
    vis(s, 1, False); vis(s, E0, True); vis(s, F0, False)
    x, y = s.location.x, s.location.y
    f_ = E0 - 16 + int(s["fase"]) % 16
    while f_ < F0 + 16:
        kl(s, f_, (x, y, -0.030)); kl(s, f_ + 15, (x, y, 0.034)); f_ += 16
# inserto: solo en su plano
for pref, (r_, c_) in INSERTO.items():
    vis(r_, 1, False); vis(r_, INS, True); vis(r_, A3, False)
    a0 = r_.rotation_euler.copy(); kl(r_, INS, None, a0); a1 = a0.copy(); a1[2] += R(10); kl(r_, A3 - 1, None, a1)

# --- luces: el taller se oscurece cuando el amortiguador flota; luces de estudio en P y en el inserto
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
L1 = luz("D_LuzClave", 'SPOT', PC + Vector((0.9, -1.2, 1.0)), PC, (1.0, 0.95, 0.88)); L1.data.spot_size = R(38); L1.data.spot_blend = 0.45
L2 = luz("D_LuzContra", 'AREA', PC + Vector((-0.5, 1.0, 0.7)), PC, (0.55, 0.72, 1.0), 0.9)
L3 = luz("D_LuzBajo", 'AREA', PC + Vector((0.3, -0.7, -0.8)), PC, (1.0, 0.75, 0.5), 0.8)
L5 = luz("D_LuzArriba", 'AREA', PC + Vector((0.0, -0.2, 1.1)), PC, (1.0, 1.0, 1.0), 1.0)
LC = luz("D_LuzCalor", 'POINT', P + Vector((0.0, -0.10, 0.12)), P, (1.0, 0.45, 0.12))
L4 = luz("D_LuzFlash", 'POINT', W0 + Vector((0, -0.25, 0.05)), W0, (1.0, 0.85, 0.6))
for o, e_ in ((L1, 330), (L2, 110), (L3, 14), (L5, 60)):
    for f_, v in ((1, 0), (100, 0), (124, e_), (A2 - 1, e_), (A2, 0)):
        o.data.energy = v; o.data.keyframe_insert("energy", frame=f_)
for f_, v in ((1, 0), (F0 + 6, 0), (FW(1, 39), 16), (A2 - 1, 16), (A2, 0)):
    LC.data.energy = v; LC.data.keyframe_insert("energy", frame=f_)
for f_, v in ((1, 0), (EST - 1, 0), (EST, 140), (EST + 4, 70), (EST + 12, 0)):
    L4.data.energy = v; L4.data.keyframe_insert("energy", frame=f_)
LI = luz("D_LuzInserto", 'SPOT', Q + Vector((-0.40, -0.60, 0.55)), Q, (1.0, 0.96, 0.9)); LI.data.spot_size = R(45); LI.data.spot_blend = 0.5
LI2 = luz("D_LuzInsertoContra", 'AREA', Q + Vector((0.40, 0.40, 0.35)), Q, (0.6, 0.75, 1.0), 0.6)
for o, e_ in ((LI, 60), (LI2, 18)):
    for f_, v in ((1, 0), (INS - 1, 0), (INS, e_), (A3 - 1, e_), (A3, 0)):
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
CL.reposo(1); CL.mover(1, CLOD_CAPO, CLOD_GIRO); CL.cara(1, "feliz"); CL.cabeza(1, -6, 0, 10); CL.mirar(1, 0.01, 0.0)
for l in ("R", "L"): CL.brazo_caido(l, 1)
# "¿Tu coche sigue botando después de un bache?": Clod bota en el capó, cada vez menos (rebote amortiguado)
fb = FW(0, 2) - 6
for k, (alto, aire) in enumerate(((0.17, 12), (0.10, 10), (0.05, 8))):
    CL.salto(fb + k * 15, alto=alto, aire=aire)
for l in ("R", "L"):
    CL.mano_en(l, fb + 2, (SX(l) * 0.34, -0.06, 0.62)); CL.codo_hacia(l, fb + 2, (SX(l) * 0.75, 0.05, 0.50))
CL.cara(fb, "feliz")
# "como Clod": se da cuenta de que hablan de él y mira a cámara, cortado
fc = FW(0, 8)
for l in ("R", "L"): CL.brazo_caido(l, fc)
CL.cara(fc, "sorpresa"); CL.cabeza(fc, -4, 6, -18); CL.mirar(fc, -0.012, 0.004)
CL.cara(FW(0, 9, True), "duda"); CL.mano_en("R", FW(0, 9, True), (-0.18, -0.22, 0.70)); CL.codo_hacia("R", FW(0, 9, True), (-0.55, 0.05, 0.50))
# "Mira lo que hay aquí dentro": señala la rueda
fm = FW(0, 10)
CL.cara(fm, "feliz"); CL.brazo_caido("R", fm - 2)
CL.mano_en("R", fm + 2, (-0.30, -0.26, 0.30)); CL.codo_hacia("R", fm + 2, (-0.62, 0.15, 0.45)); CL.pulgar("R", fm + 2, 0.2)
CL.cabeza(fm + 2, 22, 0, -14); CL.mirar(fm + 2, -0.012, -0.012)
# estalla: se tapa la cara y se asoma
for l in ("R", "L"):
    CL.mano_en(l, EST + 1, (SX(l) * 0.08, -0.26, 0.74)); CL.codo_hacia(l, EST + 1, (SX(l) * 0.55, 0.05, 0.55))
CL.aplastar(EST, 1.0); CL.aplastar(EST + 4, 0.88); CL.aplastar(EST + 12, 1.0); CL.cara(EST + 2, "susto")
CL.mano_en("L", EST + 26, (0.24, -0.12, 0.60)); CL.codo_hacia("L", EST + 26, (0.70, 0.10, 0.45)); CL.cara(EST + 26, "sorpresa")
for l in ("R", "L"): CL.brazo_caido(l, B0 + 10)
CL.cara(B0 + 10, "feliz"); CL.cabeza(B0 + 10, 0, 0, 10)
# consejo: "flota" -> sube y baja con los brazos abiertos; "cabecea al frenar" -> se va hacia delante;
# "se balancea en las curvas" -> se mece de lado a lado; "aceite por fuera" -> asco
CL.cara(A2, "contento"); CL.cabeza(A2, -4, 0, 8)
ff = FW(2, 3)
CL.cara(ff, "feliz")
for l in ("R", "L"):
    CL.mano_en(l, ff, (SX(l) * 0.40, -0.04, 0.55)); CL.codo_hacia(l, ff, (SX(l) * 0.80, 0.05, 0.50))
for k in range(4): CL.aplastar(ff + 2 + k * 5, 1.06 if k % 2 == 0 else 0.95)
CL.aplastar(ff + 22, 1.0)
fk = FW(2, 4)
CL.cara(fk, "sorpresa"); CL.cuerpo(fk, 0, 0, 0); CL.cuerpo(fk + 6, 26, 0, 0); CL.cuerpo(fk + 13, -7, 0, 0); CL.cuerpo(fk + 19, 0, 0, 0)
CL.cabeza(fk + 6, 18, 0, 8); CL.cabeza(fk + 16, -4, 0, 8)
for l in ("R", "L"): CL.brazo_caido(l, fk + 2)
fl_ = FW(2, 7)
CL.cara(fl_, "duda")
for k in range(5): CL.cuerpo(fl_ + 2 + k * 7, 0, (11 if k % 2 == 0 else -11), 0); CL.cabeza(fl_ + 2 + k * 7, 0, (-6 if k % 2 == 0 else 6), 8)
CL.cuerpo(fl_ + 38, 0, 0, 0); CL.cabeza(fl_ + 38, 0, 0, 8)
CL.cara(FW(2, 14), "enfado")
# síguenos: salta y pulgar arriba
CL.cara(CTA + 4, "feliz")
CL.salto(CTA + 8, alto=0.20, aire=12)
CL.pulgar_arriba("L", CTA + 30, dur=34)

# ---- Alex
cabeza(1, 0, 0, -6); columna(1, 0, 0, 0)
# "¿Tu coche sigue botando...?": la mano bota como un coche con los amortiguadores gastados
f_ = FW(0, 1)
cara(f_, "picaro", 0.6)
mano_en("R", f_, (-0.28, -0.32, 1.10)); codo_hacia("R", f_, (-0.62, 0.05, 1.0)); mano_pose("R", f_, "abierta")
orientar_mano("R", f_, palma_hacia=(0, 0, -1), dedos_hacia=(0, -1, 0))
for k, dz in enumerate((0.10, 0.0, 0.065, 0.0, 0.03, 0.0)):
    mano_en("R", f_ + 4 + k * 5, (-0.28, -0.32, 1.10 + dz)); orientar_mano("R", f_ + 4 + k * 5, palma_hacia=(0, 0, -1), dedos_hacia=(0, -1, 0))
# "como Clod": le señala con la cabeza y una sonrisa
cabeza(FW(0, 8), 4, 6, 18); cara(FW(0, 8), "sonrisa", 0.7)
# "Mira lo que hay aquí dentro": señala la rueda
fq = FW(0, 10)
brazo_caido("L", fq); mano_pose("L", fq, "relajada")
mano_en("R", fq, (-0.42, -0.14, 1.04)); codo_hacia("R", fq, (-0.75, 0.15, 1.05)); mano_pose("R", fq, "señalar")
orientar_mano("R", fq, dedos_hacia=(-1, 0.45, -0.5), pulgar_hacia=(0, 0, 1))
mano_en("R", FW(0, 15, True) + 6, (-0.44, -0.14, 1.02)); orientar_mano("R", FW(0, 15, True) + 6, dedos_hacia=(-1, 0.45, -0.5), pulgar_hacia=(0, 0, 1))
cabeza(fq, 14, 0, -24); cara(fq, "duda", 0.8); columna(fq, 4, 0, -6)
for l in ("R", "L"): brazo_caido(l, B0 + 30); mano_pose(l, B0 + 30, "relajada")
cabeza(B0 + 30, 0, 0, 0); columna(B0 + 30, 0, 0, 0); cara(B0 + 30, "neutra")
# consejo
kl(ALEX, A2 - 1, ALEX_POS, (0, 0, R(ALEX_GIRO))); kl(ALEX, A2, ALEX_POS, (0, 0, R(-4)))
todo_reposo(A2)
for l in ("R", "L"): brazo_caido(l, A2); mano_pose(l, A2, "relajada")
cara(A2, "duda", 0.5); cabeza(A2, 2, 0, 0); columna(A2, 2, 0, 0)
# "flota": la mano plana sube y baja despacio
ff2 = FW(2, 3) - 2
mano_pose("R", ff2, "abierta")
for k, dz in enumerate((0.0, 0.06, -0.01, 0.05, 0.0)):
    mano_en("R", ff2 + k * 5, (-0.22, -0.36, 1.12 + dz)); orientar_mano("R", ff2 + k * 5, palma_hacia=(0, 0, -1), dedos_hacia=(0, -1, 0))
codo_hacia("R", ff2, (-0.58, 0.05, 1.0))
# "cabecea al frenar": la mano se inclina hacia delante
fk2 = FW(2, 4)
mano_en("R", fk2 + 4, (-0.22, -0.40, 1.08)); orientar_mano("R", fk2 + 4, palma_hacia=(0, -0.6, -0.8), dedos_hacia=(0, -0.8, 0.6))
mano_en("R", fk2 + 12, (-0.22, -0.38, 1.10)); orientar_mano("R", fk2 + 12, palma_hacia=(0, 0, -1), dedos_hacia=(0, -1, 0))
cara(fk2, "sorpresa", 0.5)
# "se balancea en las curvas": la mano se mece de lado a lado
fb2 = FW(2, 7)
for k in range(5):
    s_ = 1 if k % 2 == 0 else -1
    orientar_mano("R", fb2 + 2 + k * 7, palma_hacia=(s_ * 0.45, 0, -0.9), dedos_hacia=(0, -1, 0))
    mano_en("R", fb2 + 2 + k * 7, (-0.22 + 0.03 * s_, -0.38, 1.10))
cara(fb2, "duda", 0.8); cabeza(fb2, 0, 5, 0)
brazo_caido("R", INS - 4); mano_pose("R", INS - 4, "relajada")
# aviso final (plano corto): "Y ojo" -> dedo bajo el ojo; "más metros para frenar" -> separa las manos
kl(ALEX, A3 - 1, ALEX_POS, (0, 0, R(-4))); kl(ALEX, A3, ALEX_POS, (0, 0, R(-8)))
fo = FW(3, 1)
cara(fo - 2, "enfado", 0.3); cabeza(fo, 2, 0, 0)
mano_en("R", fo, (-0.07, -0.16, 1.62)); codo_hacia("R", fo, (-0.50, 0.05, 1.30)); mano_pose("R", fo, "señalar")
orientar_mano("R", fo, dedos_hacia=(0, 0, 1), pulgar_hacia=(1, 0, 0))
brazo_caido("R", FW(3, 5)); mano_pose("R", FW(3, 5), "relajada")
fm2 = FW(3, 9)
for l in ("R", "L"):
    mano_en(l, fm2 - 2, (SX(l) * 0.10, -0.36, 1.20)); codo_hacia(l, fm2 - 2, (SX(l) * 0.50, 0.0, 1.0)); mano_pose(l, fm2 - 2, "abierta")
    orientar_mano(l, fm2 - 2, palma_hacia=(-SX(l), 0, 0), dedos_hacia=(0, 0, 1))
    mano_en(l, fm2 + 14, (SX(l) * 0.32, -0.36, 1.20)); orientar_mano(l, fm2 + 14, palma_hacia=(-SX(l), 0, 0), dedos_hacia=(0, 0, 1))
cara(fm2, "duda", 0.9)
for l in ("R", "L"): brazo_caido(l, CTA - 6); mano_pose(l, CTA - 6, "relajada")
# síguenos: pulgar arriba
kl(ALEX, CTA - 1, ALEX_POS, (0, 0, R(-8))); kl(ALEX, CTA, ALEX_POS, (0, 0, R(ALEX_GIRO)))
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
    a = MP @ Vector(pos); b = MP @ Vector(mira)
    ck(f, tuple(a), tuple(b), lens, dof=tuple(b) if fstop else None, fstop=fstop or 2.8)
# plano A: Alex, el coche y Clod botando -> entramos en la rueda -> estalla (temblor) -> sale el amortiguador
ck(1, (-0.85, -3.30, 1.45), (-0.95, -0.10, 0.98), 27)
ck(76, (-0.88, -3.05, 1.42), (-1.00, -0.10, 0.92), 28)
ck(92, (-1.05, -2.05, 0.95), (-1.22, 0.0, 0.45), 31)
ck(114, (-1.10, -1.30, 0.62), tuple(W0 + Vector((0, 0, 0.02))), 34)
for k, (dx, dz) in enumerate(((0.012, -0.008), (-0.010, 0.010), (0.007, -0.005), (-0.004, 0.003))):
    ck(EST + 1 + k * 2, (-1.10 + dx, -1.32, 0.63 + dz), tuple(W0 + Vector((0, -0.05, 0.05))), 33)
ck(EST + 12, (-1.08, -1.75, 0.82), tuple(W0 + Vector((0, -0.25, 0.18))), 33)
ck(B0 - 1, tuple(MP @ Vector((0.28, -0.95, 0.42))), tuple(PC), 34)
# plano B: el muelle aguanta el peso (bota)
cl(B0, (0.30, -0.95, 0.40), (0.02, 0.0, 0.30), 34); cl(C0 - 1, (0.26, -0.88, 0.38), (0.02, 0.0, 0.30), 35)
# plano C: sin muelle, rayos X; el amortiguador a la derecha para dejar sitio al gráfico del rebote
cl(C0, (0.20, -0.80, 0.27), (-0.095, -0.024, 0.20), 36); cl(D0 - 1, (0.18, -0.76, 0.26), (-0.09, -0.022, 0.20), 37)
# plano D: vástago, pistón y aceite
cl(D0, (0.12, -0.50, 0.24), (0.0, 0.0, 0.17), 38); cl(E0 - 1, (0.10, -0.46, 0.20), (0.0, 0.0, 0.14), 40)
# plano E: las válvulas del pistón, muy cerca
cl(E0, (0.035, -0.15, 0.150), (0.0, 0.0, 0.113), 44, 4.0); cl(F0 - 1, (0.030, -0.14, 0.120), (0.0, 0.0, 0.086), 46, 4.0)
# plano F: el aceite se calienta
cl(F0, (0.16, -0.55, 0.22), (0.0, 0.0, 0.15), 38); cl(A2 - 1, (0.14, -0.50, 0.20), (0.0, 0.0, 0.15), 40)
# consejo: Alex con Clod de fondo
ck(A2, (-0.30, -2.35, 1.45), (-0.95, -0.05, 1.15), 28); ck(INS - 1, (-0.31, -2.25, 1.45), (-0.95, -0.05, 1.15), 28)
# inserto: nuevo frente a gastado
ck(INS, tuple(Q + DQ * 0.74), tuple(Q), 40, dof=tuple(Q), fstop=5.6)
ck(A3 - 1, tuple(Q + DQ * 0.68), tuple(Q), 41, dof=tuple(Q), fstop=5.6)
# aviso final: plano corto de Alex
ck(A3, (-0.42, -1.70, 1.52), (-0.66, -0.58, 1.42), 40); ck(CTA - 1, (-0.44, -1.58, 1.52), (-0.66, -0.58, 1.42), 42)
# síguenos
ck(CTA, (-0.85, -3.75, 1.30), (-0.88, -0.25, 0.92), 28); ck(FIN, (-0.86, -3.50, 1.28), (-0.88, -0.25, 0.94), 28)

def _curvas(idb):
    ad_ = getattr(idb, "animation_data", None)
    if not ad_ or not ad_.action: return []
    try: return list(ad_.action.fcurves)
    except Exception: return [fc for l in ad_.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
fin_plano = {c - 1 for c in CORTES[1:]}
for idb in (cam, cam.data, AMO, ALEX, LLA):
    for fc in _curvas(idb):
        for k in fc.keyframe_points:
            if int(round(k.co[0])) in fin_plano: k.interpolation = 'CONSTANT'
        fc.update()
for s in O["flujo"]:
    for fc in _curvas(s):
        for k in fc.keyframe_points:
            k.interpolation = 'CONSTANT' if abs(k.co[1] - 0.034) < 1e-4 else 'LINEAR'
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
PIS = O["piston"]
CU = O["cuerpo"]
PUNTOS = {"muelle": (MUE, Vector((AMm["R_MUELLE"] * 0.7, -AMm["R_MUELLE"] * 0.7, L_MU * 0.55))),
          "amortiguador": (CU, Vector((0.0, -AMm["R_CUERPO"], 0.10))),
          "vastago": (VAS, Vector((0.0, -AMm["R_VAS"], 0.27))),
          "piston": (PIS, Vector((0.0, -AMm["R_PIS"], 0.0))),
          "aceite": (CU, Vector((0.0, -0.012, 0.06))),
          "valvulas": (PIS, Vector((0.0, -AMm["RH"], AMm["H_PIS"] / 2))),
          "calor": (CU, Vector((0.0, -AMm["R_CUERPO"], 0.12)))}
def proy(f):
    mc = cam.matrix_world; lens = cam.data.lens; th = 12.0 / lens; tw = th * 9 / 16
    def pp(p):
        q = mc.inverted() @ p
        if q.z >= -1e-4: return None
        return [round(0.5 + (q.x / -q.z) / (2 * tw), 4), round(0.5 + (q.y / -q.z) / (2 * th), 4)]
    return pp
ANCLAS = {}
for f in list(range(B0, A2)) + list(range(INS, A3)):
    sc.frame_set(f); pp = proy(f); d = {}
    if f < A2:
        for k, (ob, lp) in PUNTOS.items(): d[k] = pp(ob.matrix_world @ lp)
    else:
        for pref, (r_, c_) in INSERTO.items(): d[pref] = pp(c_)
    ANCLAS[f] = d
json.dump({"anclas": ANCLAS, "cortes": CORTES, "fin": FIN}, open(DD + r"\anclas_amortiguador.json", "w"))
sc.frame_set(1)
result = {"ok": True, "fin": FIN, "P": list(P), "clod": list(CLOD_CAPO), "hit": bool(hit), "cortes": CORTES}
