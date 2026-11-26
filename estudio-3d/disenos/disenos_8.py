# 8 DISEÑOS DE VÍDEO (26-11-2026) · tema común: el testigo de desgaste (1,6 mm)
# Cada fotograma (1..9) es un fotograma clave de un diseño distinto, en el taller v2 con Alex v2 y Clod v2.
# Se ejecuta sobre alex_v2_rig.blend abierto. Después: render_bg.py (fotogramas 1-9) y composición de textos aparte.
#   1 Revelación 3D en macro      2 Sketch de Alex y Clod       3 Reto "¿cuál pasa la ITV?"
#   4 POV: eres una rueda lisa    5 Antes/después (nuevo)       6 Clod presentador de noticias
#   7 Top 3 con número grande     8 Cinemático sin palabras     9 Antes/después (gastado, para el 5)
import bpy, math, bmesh
from mathutils import Vector
D_ = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D\biblioteca"
TALLER = D_ + r"\taller_v2.py"; ANIM = D_ + r"\personajes\alex_anim.py"; ANIM_C = D_ + r"\personajes\clod_anim.py"
MODELO_C = D_ + r"\personajes\clod_v2.py"; CLOD_BLEND = D_ + r"\personajes\clod\clod_v2.blend"
sc = bpy.context.scene
RR = math.radians

# ---------------------------------------------------------------- taller, Clod y funciones
T_ = {"__name__": "taller"}; exec(open(TALLER, encoding="utf-8").read(), T_)
TT = T_["construir_taller"](); M = TT["M"]; T_["ajustes_render"](sc)
if "CLOD_v2" not in bpy.data.objects:
    with bpy.data.libraries.load(CLOD_BLEND, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c in ("CLOD_v2_personaje", "CLOD_v2_controles")]
    for c in dst.collections:
        if c.name not in sc.collection.children: sc.collection.children.link(c)
exec(open(ANIM, encoding="utf-8").read())
exec(open(ANIM_C, encoding="utf-8").read())
_m = {"__name__": "modelo"}; exec(open(MODELO_C, encoding="utf-8").read(), _m)
for n in ("Ciclorama",):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)

# ---------------------------------------------------------------- utilería: dos ruedas en soportes, pila para Clod
def soporte(nombre, pos):
    raiz = bpy.data.objects.new(nombre, None); TT["col"].objects.link(raiz); raiz.location = pos
    T_["caja"](nombre + "_Base", (0, 0, 0.025), (0.46, 0.34, 0.05), M["negro"], padre=raiz)
    for sx in (-1, 1):
        T_["caja"](nombre + f"_Poste{sx}", (sx * 0.16, 0, 0.29), (0.035, 0.05, 0.5), M["acero"], padre=raiz)
    T_["cilindro"](nombre + "_Eje", (0, 0, 0.55), 0.018, 0.36, M["acero"], padre=raiz, rot=(0, RR(90), 0))
    return raiz
SOP_A = soporte("Soporte_A", (-0.80, -0.48, 0)); SOP_B = soporte("Soporte_B", (0.95, -0.50, 0))
RN = T_["rueda"]("RUEDA_Nueva", (0, 0, 0.55), (0, RR(90), 0), detalle="alto", M=M, padre=SOP_A)
RG = T_["rueda"]("RUEDA_Gastada", (0, 0, 0.55), (0, RR(90), 0), detalle="alto", M=M, padre=SOP_B)
neu_g = bpy.data.objects["RUEDA_Gastada_Neumatico"]
if neu_g.data.name == "NEU_alto":                       # malla propia para poder gastarla sin gastar la nueva
    me2 = neu_g.data.copy(); me2.name = "NEU_alto_gastado"; neu_g.data = me2
neu_g.data.shape_keys.key_blocks["gastado"].value = 1.0
PILA = T_["pila_neumaticos"]("Pila_Clod", (0.72, -0.30, 0), 4, M)
TOP_PILA = 4 * T_["ANCHO"] * 1.01

FUERA = (0, 0, -20)
def k_loc(o, f, pos):
    o.location = pos; o.keyframe_insert("location", frame=f)

# ---------------------------------------------------------------- luces de personaje
for n, loc, e, size in (("Key_Pers", (1.7, -2.4, 2.6), 320, 1.6), ("Rim_Pers", (-1.2, 2.0, 2.7), 420, 1.4), ("Fill_Pers", (-2.4, -1.6, 1.6), 110, 2.0)):
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, "AREA")); TT["col"].objects.link(o)
    o.data.energy = e; o.data.size = size; o.location = loc
    o.rotation_euler = (Vector((0, -0.2, 1.2)) - o.location).to_track_quat("-Z", "Y").to_euler()

# ---------------------------------------------------------------- cámara
cam = bpy.data.objects.get("CAM")
if cam is None:
    cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam)
cam.animation_data_clear(); cam.data.animation_data_clear()
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.02
def ck(f, loc, t, lens, dof=None, fstop=2.8):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens; cam.data.dof.use_dof = dof is not None
    cam.data.dof.focus_distance = (Vector(dof) - Vector(loc)).length if dof else 10.0; cam.data.dof.aperture_fstop = fstop
    for p in ("location", "rotation_euler"): cam.keyframe_insert(p, frame=f)
    cam.data.keyframe_insert("lens", frame=f)
    for p in ("use_dof", "focus_distance", "aperture_fstop"): cam.data.dof.keyframe_insert(p, frame=f)

# ---------------------------------------------------------------- personajes: limpieza
ALEX.animation_data_clear()
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
sk = MALLA.data.shape_keys
if sk.animation_data and sk.animation_data.action: sk.animation_data.action = None
ALEX.location = (0, 0, 0); ALEX.rotation_euler = (0, 0, 0)
CL = ClodAnim()
for ob in [CL.arm] + list(CL.ctrl.values()) + CL.ojos + [CL.bocaob]:
    ob.animation_data_clear()
    if getattr(ob.data, "shape_keys", None) and ob.data.shape_keys.animation_data: ob.data.shape_keys.animation_data_clear()
sc.frame_set(1); calibrar_palma()
def SX(l): return -1 if l == "R" else 1
def alex_base(f, expr="neutra", inten=1.0, pos=(0, 0, 0), giro=0):
    ALEX.location = pos; ALEX.rotation_euler = (0, 0, RR(giro))
    ALEX.keyframe_insert("location", frame=f); ALEX.keyframe_insert("rotation_euler", frame=f)
    todo_reposo(f)
    for l in ("R", "L"): brazo_caido(l, f)
    cara(f, expr, inten); boca(f, 0)
    for L_ in ("R", "L"):
        kb = MALLA.data.shape_keys.key_blocks["Parpado_" + L_]; kb.value = 0; kb.keyframe_insert("value", frame=f)
def clod_base(f, pos, giro=-35, expr="contento"):
    CL.reposo(f); CL.mover(f, pos, giro); CL.cara(f, expr)
    for kb in CL.ojos[0].data.shape_keys.key_blocks[1:]: pass
def escena(f, pila=True, b=False, clod_pos=None, clod_giro=-35):
    k_loc(PILA, f, (0.72, -0.30, 0) if pila else FUERA)
    k_loc(SOP_B, f, (0.95, -0.50, 0) if b else FUERA)
    k_loc(SOP_A, f, (-0.80, -0.48, 0))
    clod_base(f, clod_pos if clod_pos else ((0.72, -0.30, TOP_PILA) if pila else FUERA), clod_giro)

A_TOP = Vector((-0.80, -0.48, 0.55 + T_["R_EXT"]))          # punto más alto de la rueda nueva
A_FRENTE = Vector((-0.80, -0.48 - T_["R_EXT"], 0.55))       # banda de rodadura de cara a la cámara

# ============================ 1 · REVELACIÓN 3D EN MACRO (banda de rodadura con el testigo)
f = 1; escena(f); alex_base(f)
p_tw = A_FRENTE + Vector((0.0, 0, 0.0))
ck(f, tuple(p_tw + Vector((0.11, -0.19, 0.06))), tuple(p_tw + Vector((0.0, 0, -0.01))), 60, dof=tuple(p_tw), fstop=4.0)

# ============================ 2 · SKETCH ALEX + CLOD (plano a dos, risas)
f = 2; escena(f); alex_base(f, "risa", pos=(0, 0, 0), giro=12)
mano_en("L", f, (0.33, -0.30, 1.22)); codo_hacia("L", f, (0.75, 0.15, 0.95)); mano_pose("L", f, "señalar")
orientar_mano("L", f, dedos_hacia=(1, -0.4, -0.2), pulgar_hacia=(0, 0, 1))
mano_en("R", f, (-0.16, -0.22, 1.10)); mano_pose("R", f, "abierta")
cabeza(f, -6, 6, 18); columna(f, -3, 0, 4)
CL.cara(f, "risa"); CL.cabeza(f, -14, 8, -34)
for l in ("R", "L"): CL.mano_en(l, f, (SX(l) * 0.27, -0.10, 0.62)); CL.codo_hacia(l, f, (SX(l) * 0.75, 0.15, 0.45)); CL.pulgar(l, f, 1.0)
ck(f, (0.30, -2.45, 1.30), (0.30, -0.15, 1.08), 30)

# ============================ 3 · RETO: ¿CUÁL PASA LA ITV? (dos ruedas, Alex en medio)
f = 3; escena(f, pila=False, b=True); alex_base(f, "duda", pos=(0.08, 0.05, 0))
for l, tgt in (("R", (-0.52, -0.40, 1.02)), ("L", (0.62, -0.40, 1.02))):
    mano_en(l, f, tgt); codo_hacia(l, f, (SX(l) * 0.9, 0.2, 0.9)); mano_pose(l, f, "abierta")
    orientar_mano(l, f, palma_hacia=(0, 0, 1), dedos_hacia=(SX(l) * 1, -0.5, 0))
cabeza(f, 0, 8, 0); hombro("R", f, 8); hombro("L", f, 8)
ck(f, (0.08, -3.0, 1.25), (0.08, -0.3, 0.92), 30)

# ============================ 4 · POV: ERES UNA RUEDA LISA (cámara a ras de rueda, Alex se asoma)
f = 4; escena(f); alex_base(f, "sorpresa", pos=(0, 0, 0), giro=0)
columna(f, 24, 0, 0); cabeza(f, 22, -6, 0)
mano_en("R", f, (-0.20, -0.36, 0.95)); codo_hacia("R", f, (-0.8, 0.0, 0.8)); mano_pose("R", f, "abierta")
mano_en("L", f, (0.24, -0.30, 1.00)); mano_pose("L", f, "relajada")
cadera(f, (0, 0.05, -0.04))
CL.cara(f, "susto"); CL.cabeza(f, -12, 0, -30)
ck(f, (0.10, -0.95, 0.42), (0.0, -0.20, 1.45), 24)

# ============================ 5 · ANTES / DESPUÉS: NUEVO (arriba de la pantalla partida)
f = 5; escena(f); alex_base(f)
cam5 = (A_FRENTE + Vector((0.0, -0.30, 0.10)), A_FRENTE + Vector((0, 0, 0.02)))
ck(f, tuple(cam5[0]), tuple(cam5[1]), 55, dof=tuple(A_FRENTE), fstop=5.6)

# ============================ 6 · CLOD PRESENTADOR DE NOTICIAS
f = 6; escena(f, clod_giro=-10); alex_base(f, "concentrado", 0.5, pos=(-0.35, 0.9, 0), giro=-20)
CL.cara(f, "contento"); CL.cabeza(f, -4, 0, 0)
CL.mano_en("R", f, (-0.12, -0.20, 0.50)); CL.codo_hacia("R", f, (-0.60, 0.20, 0.35)); CL.pulgar("R", f, 0.3)
CL.mano_en("L", f, (0.12, -0.20, 0.50)); CL.codo_hacia("L", f, (0.60, 0.20, 0.35)); CL.pulgar("L", f, 0.3)
pc = Vector((0.72, -0.30, TOP_PILA + 0.20))
ck(f, tuple(pc + Vector((-0.05, -0.80, 0.06))), tuple(pc + Vector((0, 0, 0.02))), 50, dof=tuple(pc), fstop=2.8)

# ============================ 7 · TOP 3 CON NÚMERO GRANDE
f = 7; escena(f); alex_base(f, "sonrisa", 0.8)
mano_en("R", f, (-0.26, -0.24, 1.55)); codo_hacia("R", f, (-0.8, 0.1, 1.10)); mano_pose("R", f, "señalar")
orientar_mano("R", f, dedos_hacia=(0, 0, 1), pulgar_hacia=(1, 0, 0))
cabeza(f, -2, -4, 0)
CL.cara(f, "feliz"); CL.cabeza(f, -10, 0, -25)
ck(f, (-0.10, -2.20, 1.32), (0.15, 0, 1.18), 32)

# ============================ 8 · CINEMÁTICO SIN PALABRAS (contraluz, rueda en primer plano)
f = 8; escena(f); alex_base(f, "concentrado", 0.6, pos=(0.35, 1.0, 0), giro=-25)
mano_en("R", f, (-0.31, -0.03, 0.89))
CL.cara(f, "contento")
ck(f, (-1.35, -1.55, 0.30), (-0.55, -0.10, 0.62), 35, dof=tuple(Vector((-0.80, -0.48, 0.55))), fstop=2.0)

# ============================ 9 · ANTES / DESPUÉS: GASTADO (misma cámara que el 5, sobre la rueda gastada)
f = 9; escena(f, b=True, pila=False); alex_base(f, pos=(0, 2.0, 0))
SOP_B.location = SOP_A.location.copy(); SOP_B.keyframe_insert("location", frame=f)
k_loc(SOP_A, f, FUERA)
ck(f, tuple(cam5[0]), tuple(cam5[1]), 55, dof=tuple(A_FRENTE), fstop=5.6)

# ---------------------------------------------------------------- todo constante (cada fotograma es una foto distinta)
def _curvas(idb):
    ad = getattr(idb, "animation_data", None)
    if not ad or not ad.action: return []
    try: return list(ad.action.fcurves)
    except Exception: return [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
for ob in bpy.data.objects:
    for idb in (ob, ob.data, getattr(ob.data, "shape_keys", None) if ob.data else None, getattr(ob.data, "dof", None) if ob.type == 'CAMERA' else None):
        if idb is None: continue
        for fc in _curvas(idb):
            for k in fc.keyframe_points: k.interpolation = 'CONSTANT'
for fc in _curvas(cam.data):
    for k in fc.keyframe_points: k.interpolation = 'CONSTANT'
_m["brillo_led"](sc, umbral=6.0)
sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 50
sc.eevee.taa_render_samples = 40; sc.render.fps = 30; sc.frame_start, sc.frame_end = 1, 9
sc.view_settings.exposure = -0.1
result = {"ok": True}
