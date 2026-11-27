# PLANTILLA COMÚN DE LOS DESPIECES 3D (EKORUEDAS · 27-11-2026)
# Sale del despiece del amortiguador: taller, coche, Alex (voz Diego), Clod (solo gestos), rayos X al capó, la pieza sale
# volando con un destello y flota en un estudio oscuro; consejo de Alex, inserto nuevo / gastado, aviso final y "síguenos".
# Uso (en despiece_<pieza>.py):
#   BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"; NOMBRE = "bateria"; DD = BASE + r"\videos_3d\despiece_bateria"
#   _B = open(BASE + r"\plantillas\despiece_base.py", encoding="utf-8").read().split(<la línea que separa la PARTE 2>)
#   exec(_B[0])  -> escena, voz (FW, FL), materiales pro (MP), ayudantes (kl, ks, vis, kp, luz, ck, cl, partir, vuelo)
#   ... la pieza: modelo, su animación, sus planos (cl), PUNTOS para los rótulos, G (gestos), EV (eventos) ...
#   exec(_B[1])  -> luces, personajes, planos de Alex, cortes secos, render pro y anclas para el montaje
# Variables que pone la escena de la pieza antes de la PARTE 2:
#   RAIZ, E_POS, P, ROTP, ESC_P, ALTO, Q, INSERTO {"AN": (raiz, punto), "AG": (...)}, PUNTOS {clave: (obj, punto_local)},
#   XR0, EST, B0, A2, INS, A3, CTA, FIN, CORTES, EV, G {"pregunta", "clod", "mira", "sintomas": [...], "ojo", "manos"},
#   opcional: gag_clod(CL), gag_consejo(CL), EXTRA_CONST [objetos con cortes secos], MUESTRAS
# No usa drivers (en el render de fondo no se ejecutan): todo con fotogramas clave.
import bpy, bmesh, math, json, os, random
import numpy as np
from mathutils import Vector, Matrix, Euler
_SRC = open(BASE + r"\videos_3d\despiece_neumatico\despiece_neumatico_v2.py", encoding="utf-8").read()
exec(_SRC[:_SRC.index("# ---------------------------------------------------------------- RUEDA PROTAGONISTA")])
MP = {"__name__": "mp"}; exec(open(D_ + r"\materiales_pro.py", encoding="utf-8").read(), MP)
VOZ = json.load(open(DD + "\\voces_" + NOMBRE + ".json", encoding="utf-8"))
def T(i, j, fin=False):
    l = VOZ["lineas"][i]; w = l["words"][j]; return l["at"] + (w[2] if fin else w[1])
def FW(i, j, fin=False): return F(T(i, j, fin))
def FL(i): return FW(i, len(VOZ["lineas"][i]["words"]) - 1, True)
HOOD = Vector((-1.55, 0.62, 0.90))           # donde se sube Clod (capó)
ESC_P = 1.0; ALTO = 0.2; MUESTRAS = 48; EXTRA_CONST = []; INSERTO = {}; Q = Vector((0.62, -1.95, 1.12)); INS_DIST = 0.74
P = Vector((-1.30, -1.05, 0.70)); ROTP = (0, 0, math.radians(-24))

# ---------------------------------------------------------------- ayudantes de animación
def kl(o, f, loc=None, rot=None):
    if loc is not None: o.location = loc; o.keyframe_insert("location", frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=f)
def ks(o, f, s):
    if isinstance(s, (int, float)): s = (s, s, s)
    o.scale = s; o.keyframe_insert("scale", frame=f)
def vis(o, f, ver):
    for oo in [o] + list(o.children_recursive):
        oo.hide_render = not ver; oo.hide_viewport = not ver
        oo.keyframe_insert("hide_render", frame=f); oo.keyframe_insert("hide_viewport", frame=f)
def kp(prop, f, v): sc[prop] = v; sc.keyframe_insert(f'["{prop}"]', frame=f)
def ke(m, f, v, entrada="Emission Strength"):
    s = m.node_tree.nodes["Principled BSDF"].inputs[entrada]; s.default_value = v; s.keyframe_insert("default_value", frame=f)
def luz(n, tipo, loc, mira, color, size=1.0):
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, tipo)); CD.objects.link(o)
    o.location = loc; o.data.color = color
    if tipo == 'AREA': o.data.size = size
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if o.data.animation_data: o.data.animation_data_clear()
    return o
def kluz(o, claves):
    for f_, v in claves: o.data.energy = v; o.data.keyframe_insert("energy", frame=f_)
def col_pieza(n):
    c = bpy.data.collections.get(n)
    if c is None: c = bpy.data.collections.new(n); CD.children.link(c)
    return c

# ---------------------------------------------------------------- cámara
cam = bpy.data.objects.get("CAM")
if cam is None:
    cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam)
cam.animation_data_clear(); cam.data.animation_data_clear()
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.004
def ck(f, loc, t, lens, dof=None, fstop=2.8):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens; cam.data.dof.use_dof = dof is not None
    cam.data.dof.focus_distance = (Vector(dof) - Vector(loc)).length if dof else 10.0; cam.data.dof.aperture_fstop = fstop
    for p_ in ("location", "rotation_euler"): cam.keyframe_insert(p_, frame=f)
    cam.data.keyframe_insert("lens", frame=f)
    for p_ in ("use_dof", "focus_distance", "aperture_fstop"): cam.data.dof.keyframe_insert(p_, frame=f)
def MPm(): return Matrix.Translation(P) @ Euler(ROTP).to_matrix().to_4x4() @ Matrix.Scale(ESC_P, 4)
def cl(f, pos, mira, lens, fstop=None):
    M_ = MPm(); a = M_ @ Vector(pos); b = M_ @ Vector(mira)
    ck(f, tuple(a), tuple(b), lens, dof=tuple(b) if fstop else None, fstop=fstop or 2.8)

# ---------------------------------------------------------------- corte por la mitad (plano y = 0 del objeto)
MC = MP["corte"]("MP_Corte_" + NOMBRE)
def cortar(me_src, nombre, quitar_frente, tapar=True, tapa_corte=True):
    bm = bmesh.new(); bm.from_mesh(me_src)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    if quitar_frente: bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_inner=True)
    else: bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_outer=True)
    if tapar:
        bordes = [e for e in bm.edges if e.is_boundary]
        if bordes:
            r_ = bmesh.ops.holes_fill(bm, edges=bordes, sides=0)
            for fc in r_["faces"]:
                fc.smooth = False
                if tapa_corte: fc.material_index = len(me_src.materials)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for m in me_src.materials: me.materials.append(m)
    if tapa_corte: me.materials.append(MC)
    return me
def _copia_obj(nombre, me, padre, ref):
    o = bpy.data.objects.new(nombre, me); ref.users_collection[0].objects.link(o); o.parent = padre
    o.matrix_parent_inverse = ref.matrix_parent_inverse.copy(); o.location = ref.location; o.rotation_euler = ref.rotation_euler; o.scale = ref.scale
    for md in ref.modifiers:
        if md.type == 'EDGE_SPLIT': n_ = o.modifiers.new("aristas", 'EDGE_SPLIT'); n_.split_angle = md.split_angle
    return o
def partir(objs, frente, solo_fondo=(), sin_tapa=()):
    """Cada objeto se parte en y = 0: la mitad de atrás se queda, la de delante va con 'frente' (y sale volando)."""
    for o in list(objs):
        me0 = o.data; tapa = o.name not in sin_tapa
        _copia_obj(o.name + "_Fondo", cortar(me0, o.name + "_Fondo", True, True, tapa), o.parent, o)
        if o.name not in solo_fondo:
            _copia_obj(o.name + "_Frente", cortar(me0, o.name + "_Frente", False, True, tapa), frente, o)
        bpy.data.objects.remove(o)

# ---------------------------------------------------------------- vuelo: del capó (rayos X) al estudio
def vuelo(raiz, f_sale, f_llega, esc_coche=1.0, rot_coche=(0, 0, 0), alto_salida=0.45):
    kl(raiz, 1, E_POS, rot_coche); kl(raiz, f_sale, E_POS, rot_coche)
    kl(raiz, f_sale + 10, E_POS + Vector((0.02, -0.06, alto_salida)), (rot_coche[0] + 0.15, rot_coche[1], rot_coche[2] - 0.35))
    kl(raiz, f_llega, P, ROTP)
    ks(raiz, 1, esc_coche); ks(raiz, f_sale + 2, esc_coche); ks(raiz, f_llega, ESC_P)

# ==== PARTE 2 ====
# ================================================================ LUCES
if "F_OSCURO" not in globals(): F_OSCURO = EST - 2        # el taller se oscurece cuando la pieza va al estudio
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
    kluz(o, [(1, e0), (F_OSCURO - 22, e0), (F_OSCURO, e0 * 0.07), (A2 - 1, e0 * 0.07), (A2, e0)])
    o.data.energy = e0
LED = M["led"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
if LED.is_linked is False:
    for f_, v in ((1, 6.0), (F_OSCURO - 22, 6.0), (F_OSCURO, 0.25), (A2 - 1, 0.25), (A2, 6.0)):
        LED.default_value = v; LED.keyframe_insert("default_value", frame=f_)
PC = P + Vector((0, 0, ALTO * ESC_P * 0.5))
L1 = luz("D_LuzClave", 'SPOT', PC + Vector((0.9, -1.2, 1.0)), PC, (1.0, 0.95, 0.88)); L1.data.spot_size = math.radians(38); L1.data.spot_blend = 0.45
L2 = luz("D_LuzContra", 'AREA', PC + Vector((-0.5, 1.0, 0.7)), PC, (0.55, 0.72, 1.0), 0.9)
L3 = luz("D_LuzBajo", 'AREA', PC + Vector((0.3, -0.7, -0.8)), PC, (1.0, 0.75, 0.5), 0.8)
L5 = luz("D_LuzArriba", 'AREA', PC + Vector((0.0, -0.2, 1.1)), PC, (1.0, 1.0, 1.0), 1.0)
L4 = luz("D_LuzFlash", 'POINT', E_POS + Vector((0, -0.25, 0.30)), E_POS, (1.0, 0.85, 0.6))
for o, e_ in ((L1, 330), (L2, 110), (L3, 14), (L5, 60)):
    kluz(o, [(1, 0), (EST - 20, 0), (EST + 4, e_), (A2 - 1, e_), (A2, 0)])
kluz(L4, [(1, 0), (EST - 1, 0), (EST, 140), (EST + 4, 70), (EST + 12, 0)])
if INS < A3:
    LI = luz("D_LuzInserto", 'SPOT', Q + Vector((-0.40, -0.60, 0.55)), Q, (1.0, 0.96, 0.9)); LI.data.spot_size = math.radians(45); LI.data.spot_blend = 0.5
    LI2 = luz("D_LuzInsertoContra", 'AREA', Q + Vector((0.40, 0.40, 0.35)), Q, (0.6, 0.75, 1.0), 0.6)
    for o, e_ in ((LI, 60), (LI2, 18)): kluz(o, [(1, 0), (INS - 1, 0), (INS, e_), (A3 - 1, e_), (A3, 0)])
# rayos X al capó
kp("xray", 1, 0.0); kp("xray", XR0, 0.0); kp("xray", XR0 + 12, 1.0); kp("xray", EST + 16, 1.0); kp("xray", EST + 26, 0.0)
def _curvas(idb):
    ad_ = getattr(idb, "animation_data", None)
    if not ad_ or not ad_.action: return []
    try: return list(ad_.action.fcurves)
    except Exception: return [fc for l in ad_.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
for oo in [RAIZ] + list(RAIZ.children_recursive):        # la pieza desaparece en el consejo (sin pisar las claves que ya tenga)
    if not any(fc.data_path == "hide_render" for fc in _curvas(oo)):
        oo.hide_render = oo.hide_viewport = False; oo.keyframe_insert("hide_render", frame=1); oo.keyframe_insert("hide_viewport", frame=1)
    oo.hide_render = oo.hide_viewport = True; oo.keyframe_insert("hide_render", frame=A2); oo.keyframe_insert("hide_viewport", frame=A2)
for pref, (r_, c_) in INSERTO.items():
    vis(r_, 1, False); vis(r_, INS, True); vis(r_, A3, False)
    a0 = r_.rotation_euler.copy(); kl(r_, INS, None, a0); a1 = a0.copy(); a1[2] += math.radians(10); kl(r_, A3 - 1, None, a1)

# ================================================================ PERSONAJES
ALEX_POS = Vector((-0.62, -0.60, 0)); ALEX_GIRO = -12
sk = MALLA.data.shape_keys
if sk.animation_data and sk.animation_data.action: sk.animation_data.action = None
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
ALEX.animation_data_clear()
ALEX.location = ALEX_POS; ALEX.rotation_euler = (0, 0, math.radians(ALEX_GIRO))
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
XC, YC = HOOD.x, HOOD.y
hit, loc_h, *_ = sc.ray_cast(dg, Vector((XC, YC, 3.0)), Vector((0, 0, -1)))
CLOD_CAPO = (XC, YC, (loc_h.z if hit else 0.90) - 0.004)
CLOD_GIRO = 10
CL.reposo(1); CL.mover(1, CLOD_CAPO, CLOD_GIRO); CL.cara(1, "feliz"); CL.cabeza(1, -6, 0, 10); CL.mirar(1, 0.01, 0.0)
for l in ("R", "L"): CL.brazo_caido(l, 1)
if "gag_clod" in globals(): gag_clod(CL)
# la pieza sale disparada: Clod se encoge y se tapa la cara, luego se asoma
for l in ("R", "L"):
    CL.mano_en(l, EST + 1, (SX(l) * 0.08, -0.26, 0.74)); CL.codo_hacia(l, EST + 1, (SX(l) * 0.55, 0.05, 0.55))
CL.aplastar(EST, 1.0); CL.aplastar(EST + 4, 0.88); CL.aplastar(EST + 12, 1.0); CL.cara(EST + 2, "susto")
CL.mano_en("L", EST + 26, (0.24, -0.12, 0.60)); CL.codo_hacia("L", EST + 26, (0.70, 0.10, 0.45)); CL.cara(EST + 26, "sorpresa")
for l in ("R", "L"): CL.brazo_caido(l, B0 + 10)
CL.cara(B0 + 10, "feliz"); CL.cabeza(B0 + 10, 0, 0, 10)
# consejo: Clod reacciona a cada síntoma
CL.cara(A2, "contento"); CL.cabeza(A2, -4, 0, 8)
for k, fs in enumerate(G.get("sintomas", [])):
    ex = ("duda", "sorpresa", "triste", "enfado")[k % 4]
    CL.cara(fs, ex); CL.cabeza(fs, (6, -4, 10, 0)[k % 4], (8, -8, 0, 6)[k % 4], 8)
    CL.aplastar(fs, 1.0); CL.aplastar(fs + 4, 0.94); CL.aplastar(fs + 10, 1.0)
if "gag_consejo" in globals(): gag_consejo(CL)
# síguenos: salta y pulgar arriba
CL.cara(CTA + 4, "feliz")
CL.salto(CTA + 8, alto=0.20, aire=12)
CL.pulgar_arriba("L", CTA + 30, dur=34)

# ---- Alex
cabeza(1, 0, 0, -6); columna(1, 0, 0, 0)
fp = G["pregunta"]                              # la pregunta del gancho: palma arriba, cara de pícaro
cara(fp, "picaro", 0.6)
mano_en("R", fp, (-0.26, -0.30, 1.12)); codo_hacia("R", fp, (-0.62, 0.05, 1.0)); mano_pose("R", fp, "abierta")
orientar_mano("R", fp, palma_hacia=(0, 0, 1), dedos_hacia=(0, -1, 0))
mano_en("R", fp + 10, (-0.24, -0.32, 1.15)); orientar_mano("R", fp + 10, palma_hacia=(0, 0, 1), dedos_hacia=(0, -1, 0))
cabeza(fp + 6, 4, -5, 0)
cabeza(G["clod"], 4, 6, 18); cara(G["clod"], "sonrisa", 0.7)    # mira a Clod
fq = G["mira"]                                  # señala el capó
brazo_caido("L", fq); mano_pose("L", fq, "relajada")
mano_en("R", fq, (-0.42, -0.10, 1.08)); codo_hacia("R", fq, (-0.75, 0.15, 1.05)); mano_pose("R", fq, "señalar")
orientar_mano("R", fq, dedos_hacia=(-1, 0.6, -0.2), pulgar_hacia=(0, 0, 1))
mano_en("R", fq + 12, (-0.44, -0.10, 1.07)); orientar_mano("R", fq + 12, dedos_hacia=(-1, 0.6, -0.2), pulgar_hacia=(0, 0, 1))
cabeza(fq, 10, 0, -26); cara(fq, "duda", 0.8); columna(fq, 4, 0, -6)
for l in ("R", "L"): brazo_caido(l, B0 + 30); mano_pose(l, B0 + 30, "relajada")
cabeza(B0 + 30, 0, 0, 0); columna(B0 + 30, 0, 0, 0); cara(B0 + 30, "neutra")
# consejo: cuenta los síntomas con una mano y otra
kl(ALEX, A2 - 1, ALEX_POS, (0, 0, math.radians(ALEX_GIRO))); kl(ALEX, A2, ALEX_POS, (0, 0, math.radians(-4)))
todo_reposo(A2)
for l in ("R", "L"): brazo_caido(l, A2); mano_pose(l, A2, "relajada")
cara(A2, "duda", 0.5); cabeza(A2, 2, 0, 0); columna(A2, 2, 0, 0)
for k, fs in enumerate(G.get("sintomas", [])):
    l = "R" if k % 2 == 0 else "L"; o_ = "L" if l == "R" else "R"
    mano_en(l, fs - 3, (SX(l) * 0.19, -0.36, 1.17)); codo_hacia(l, fs - 3, (SX(l) * 0.55, 0.05, 1.0)); mano_pose(l, fs - 3, "abierta")
    orientar_mano(l, fs - 3, palma_hacia=(0, -1, 0), dedos_hacia=(0, 0, 1))
    mano_en(l, fs + 8, (SX(l) * 0.20, -0.37, 1.20)); orientar_mano(l, fs + 8, palma_hacia=(0, -1, 0), dedos_hacia=(0, 0, 1))
    brazo_caido(o_, fs - 3); mano_pose(o_, fs - 3, "relajada")
    cara(fs, ("duda", "sorpresa", "enfado", "duda")[k % 4], 0.7); cabeza(fs, 3, (5 if l == "R" else -5), 0)
fin_s = (INS if INS < A3 else A3) - 4
for l in ("R", "L"): brazo_caido(l, fin_s); mano_pose(l, fin_s, "relajada")
# aviso final (plano corto): "ojo" -> dedo bajo el ojo; después separa las manos
kl(ALEX, A3 - 1, ALEX_POS, (0, 0, math.radians(-4))); kl(ALEX, A3, ALEX_POS, (0, 0, math.radians(-8)))
fo = G["ojo"]
cara(fo - 2, "enfado", 0.3); cabeza(fo, 2, 0, 0)
mano_en("R", fo, (-0.07, -0.16, 1.62)); codo_hacia("R", fo, (-0.50, 0.05, 1.30)); mano_pose("R", fo, "señalar")
orientar_mano("R", fo, dedos_hacia=(0, 0, 1), pulgar_hacia=(1, 0, 0))
brazo_caido("R", fo + 26); mano_pose("R", fo + 26, "relajada")
fm2 = G.get("manos")
if fm2:
    for l in ("R", "L"):
        mano_en(l, fm2 - 2, (SX(l) * 0.10, -0.36, 1.20)); codo_hacia(l, fm2 - 2, (SX(l) * 0.50, 0.0, 1.0)); mano_pose(l, fm2 - 2, "abierta")
        orientar_mano(l, fm2 - 2, palma_hacia=(-SX(l), 0, 0), dedos_hacia=(0, 0, 1))
        mano_en(l, fm2 + 14, (SX(l) * 0.30, -0.36, 1.20)); orientar_mano(l, fm2 + 14, palma_hacia=(-SX(l), 0, 0), dedos_hacia=(0, 0, 1))
    cara(fm2, "duda", 0.9)
for l in ("R", "L"): brazo_caido(l, CTA - 6); mano_pose(l, CTA - 6, "relajada")
# síguenos: pulgar arriba
kl(ALEX, CTA - 1, ALEX_POS, (0, 0, math.radians(-8))); kl(ALEX, CTA, ALEX_POS, (0, 0, math.radians(ALEX_GIRO)))
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
vis(ALEX, 1, True); vis(ALEX, B0, False); vis(ALEX, A2, True)

# ================================================================ CÁMARAS DE ALEX (los planos de la pieza los pone su escena)
EP = Vector(E_POS) + Vector((0, 0, 0.10))
# gancho: Alex y Clod a la vez (Alex a la derecha, Clod en el capó a la izquierda)
ck(1, (-0.25, -2.80, 1.40), (-1.05, 0.0, 1.05), 30)
ck(max(2, XR0 - 16), (-0.33, -2.58, 1.37), (-1.10, 0.05, 1.02), 31)
if "CAMS_INTRO" in globals():
    for a_ in CAMS_INTRO: ck(*a_)
else:
    ck(XR0 + 8, (-1.30, -1.42, 1.16), tuple(EP), 40)
    ck(EST - 1, (-1.29, -1.30, 1.12), tuple(EP), 42)
    for k, (dx, dz) in enumerate(((0.012, -0.008), (-0.010, 0.010), (0.007, -0.005), (-0.004, 0.003))):
        ck(EST + 1 + k * 2, (-1.29 + dx, -1.32, 1.13 + dz), tuple(EP + Vector((0, 0, 0.12))), 40)
    ck(EST + 14, (-1.25, -1.70, 1.25), tuple(EP + Vector((0, -0.1, 0.40))), 34)
    ck(B0 - 1, tuple(MPm() @ Vector((0.0, -ALTO * 4.2, ALTO * 1.6))), tuple(PC), 34)
if A2 < INS:
    ck(A2, (-0.30, -2.35, 1.45), (-0.95, -0.05, 1.15), 28); ck(INS - 1, (-0.31, -2.25, 1.45), (-0.95, -0.05, 1.15), 28)
if INS < A3:
    DQ = Vector((-0.50, -0.26, 0.14)).normalized()
    ck(INS, tuple(Q + DQ * INS_DIST), tuple(Q), 40, dof=tuple(Q), fstop=5.6)
    ck(A3 - 1, tuple(Q + DQ * INS_DIST * 0.92), tuple(Q), 41, dof=tuple(Q), fstop=5.6)
ck(A3, (-0.40, -2.05, 1.55), (-0.66, -0.58, 1.50), 35); ck(CTA - 1, (-0.42, -1.92, 1.55), (-0.66, -0.58, 1.50), 37)
ck(CTA, (-0.85, -3.75, 1.30), (-0.88, -0.25, 0.92), 28); ck(FIN, (-0.86, -3.50, 1.28), (-0.88, -0.25, 0.94), 28)

fin_plano = {c - 1 for c in CORTES[1:]}
for idb in [cam, cam.data, RAIZ, ALEX] + list(EXTRA_CONST):
    for fc in _curvas(idb):
        for k in fc.keyframe_points:
            if int(round(k.co[0])) in fin_plano: k.interpolation = 'CONSTANT'
        fc.update()
for fc in _curvas(sc):
    for k in fc.keyframe_points: k.interpolation = 'LINEAR'

sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.fps = 30; sc.frame_start, sc.frame_end = 1, FIN
MP["render_pro"](sc, 100, MUESTRAS)
try: sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45; sc.render.motion_blur_position = 'START'
except Exception: pass
sc.view_settings.exposure = -0.1

# ================================================================ ANCLAS para los rótulos del montaje (pantalla 0-1, y hacia arriba)
def proy():
    mc = cam.matrix_world; lens = cam.data.lens; th = 12.0 / lens; tw = th * 9 / 16
    def pp(p):
        q = mc.inverted() @ p
        if q.z >= -1e-4: return None
        return [round(0.5 + (q.x / -q.z) / (2 * tw), 4), round(0.5 + (q.y / -q.z) / (2 * th), 4)]
    return pp
ANCLAS = {}
for f in list(range(B0, A2)) + list(range(INS, A3)):
    sc.frame_set(f); pp = proy(); d = {}
    if f < A2:
        for k, (ob, lp) in PUNTOS.items(): d[k] = pp(ob.matrix_world @ Vector(lp))
    else:
        for pref, (r_, c_) in INSERTO.items(): d[pref] = pp(r_.matrix_world @ Vector(c_))
    ANCLAS[f] = d
EV.update({"EST": EST, "B0": B0, "A2": A2, "INS": INS, "A3": A3, "CTA": CTA, "FIN": FIN})
json.dump({"anclas": ANCLAS, "cortes": CORTES, "fin": FIN, "eventos": EV}, open(DD + "\\anclas_" + NOMBRE + ".json", "w"))
sc.frame_set(1)
result = {"ok": True, "fin": FIN, "cortes": CORTES, "clod": list(CLOD_CAPO), "hit": bool(hit)}
