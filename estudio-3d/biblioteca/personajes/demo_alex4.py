# DEMO 4 (con voz): Alex saluda y enseña sus expresiones, montado en 5 planos para vídeo vertical 9:16.
# Voz de Ootto (Carlos): "¡Eh, hola! Soy Alex. Mira esto: ya puedo sonreír, enfadarme... ¡y hasta sorprenderme! Bueno, ¿qué? ¿Empezamos?"
# Novedades frente a la demo 3:
#  - Los gestos caben en el encuadre vertical (manos cerca del cuerpo, nada se sale por los lados).
#  - 5 planos con cortes (general, medio 3/4, primer plano, general, medio con acercamiento).
#  - Comprobación automática: ninguna mano en gesto sale del encuadre (comprobar_encuadre()).
import bpy, math, bmesh
from mathutils import Vector
try: ANIM
except NameError: ANIM = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D\biblioteca\personajes\alex_anim.py"
exec(open(ANIM, encoding="utf-8").read())
sc = bpy.context.scene
D = 0.8   # la voz empieza en el segundo 0,8
VOZ = [{"at": D, "words": [["¡Eh", 0.057, 0.6], ["hola", 0.659, 1.09], ["Soy", 1.115, 1.38], ["Alex", 1.38, 1.8], ["Mira", 1.83, 2.07], ["esto", 2.07, 2.38], ["ya", 2.43, 2.59], ["puedo", 2.59, 2.75], ["sonreír", 2.75, 3.39], ["enfadarme", 3.552, 4.35], ["¡y", 4.458, 4.62], ["hasta", 4.62, 4.78], ["sorprenderme", 4.78, 5.42], ["Bueno", 5.52, 5.98], ["¿qué", 6.006, 6.22], ["¿Empezamos", 6.274, 6.89]]}]
def F(t): return int(round((D + t) * 30)) + 1
FIN = F(6.89) + 54
CORTES = [1, F(1.10), F(2.40), F(4.42), F(5.47), FIN + 1]     # inicio de cada plano

# ------------------------------------------------------------------ limpieza
ALEX.animation_data_clear()
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
sk = MALLA.data.shape_keys
if sk.animation_data and sk.animation_data.action: sk.animation_data.action = None
ALEX.location = (0, 0, 0); ALEX.rotation_euler = (0, 0, 0)
todo_reposo(1); sc.frame_set(1); calibrar_palma()
for l in ("R", "L"): brazo_caido(l, 1)

def manos(f, pos_r, pos_l, pose=None, codo_r=None, codo_l=None):
    mano_en("R", f, pos_r); mano_en("L", f, pos_l)
    if codo_r: codo_hacia("R", f, codo_r)
    if codo_l: codo_hacia("L", f, codo_l)
    if pose:
        mano_pose("R", f, pose); mano_pose("L", f, pose)

# ================================================================== PLANO 1 · general: "¡Eh, hola!"
cara(1, "concentrado", 0.6); cabeza(1, 4, 0, 35); columna(1, 0, 0, 10); cadera(1)
cabeza(F(-0.30), 4, 0, 33); cara(F(-0.25), "concentrado", 0.6); cadera(F(-0.30), (0.008, 0, 0))
# gira a cámara con anticipación (baja un poco la cabeza antes de girar)
cabeza(F(-0.08), 7, 0, 30)
cabeza(F(0.18), -4, -3, 0); columna(F(0.22), 0, 0, 0); cara(F(0.08), "sorpresa", 0.4); cara(F(0.55), "sonrisa")
cadera(F(0.20), (0, 0, -0.012))                    # pequeño rebote al girarse
cadera(F(0.45), (0, 0, 0))
# saludo con la mano derecha, a la altura de la cabeza y cerca del cuerpo
mano_en("R", F(0.02), (-0.31, -0.03, 0.89)); mano_pose("R", F(0.02), "relajada")
mano_en("R", F(0.42), (-0.33, -0.14, 1.60)); codo_hacia("R", F(0.42), (-0.80, 0.10, 1.12)); mano_pose("R", F(0.42), "abierta")
orientar_mano("R", F(0.42), palma_hacia=(0, -1, 0), dedos_hacia=(0, 0, 1))
for t, x in ((0.58, -0.22), (0.74, -0.36), (0.90, -0.23), (1.05, -0.34)):
    mano_en("R", F(t), (x, -0.14, 1.61))
mano_pose("R", F(1.05), "abierta")
# ================================================================== PLANO 2 · medio 3/4: "Soy Alex. Mira esto:"
mano_en("R", F(1.32), (-0.07, -0.24, 1.22)); codo_hacia("R", F(1.32), (-0.70, 0.00, 0.90)); mano_pose("R", F(1.32), "abierta")
orientar_mano("R", F(1.32), palma_hacia=(0, 1, 0), dedos_hacia=(1, 0, 0.3))
mano_pose("L", F(1.32), "relajada")
cabeza(F(1.35), 5, -4, 0); cara(F(1.35), "sonrisa", 0.8)
mano_en("R", F(1.70), (-0.06, -0.25, 1.23))
# "Mira esto": los dos índices señalan su cara desde los lados
for l in ("R", "L"):
    s = _sx(l)
    mano_en(l, F(2.00), (s * 0.20, -0.22, 1.47)); codo_hacia(l, F(2.00), (s * 0.60, 0.05, 1.05)); mano_pose(l, F(2.00), "señalar")
    orientar_mano(l, F(2.00), dedos_hacia=(-s * 1, -0.2, 0.25), pulgar_hacia=(0, 0, 1))
    mano_en(l, F(2.30), (s * 0.19, -0.22, 1.48))
cabeza(F(2.00), -3, 3, 0); cara(F(2.00), "picaro", 0.7)
# ================================================================== PLANO 3 · primer plano: "ya puedo sonreír, enfadarme..."
for l in ("R", "L"):
    brazo_caido(l, F(2.62)); mano_pose(l, F(2.62), "relajada"); mano_giro(l, F(2.62))
cara(F(2.70), "risa", 1.0); cabeza(F(2.80), -6, 5, 0)
cadera(F(2.80), (0, 0, 0.008)); cadera(F(3.00), (0, 0, -0.006)); cadera(F(3.20), (0, 0, 0.004)); cadera(F(3.40), (0, 0, 0))
cabeza(F(3.30), -4, 4, 0); cara(F(3.36), "risa", 0.9)
# enfadarme: cejas abajo, puños delante del pecho, se inclina
cara(F(3.52), "enfado"); cabeza(F(3.58), 8, 0, 0); columna(F(3.62), 7, 0, 0)
for l in ("R", "L"):
    s = _sx(l)
    mano_en(l, F(3.68), (s * 0.13, -0.27, 1.20)); codo_hacia(l, F(3.68), (s * 0.70, 0.35, 1.00)); mano_pose(l, F(3.68), "puño")
for t, dz in ((3.82, 0.025), (3.96, -0.005), (4.10, 0.02), (4.24, 0.0)):
    for l in ("R", "L"):
        s = _sx(l); mano_en(l, F(t), (s * 0.13, -0.27, 1.20 + dz))
cara(F(4.30), "enfado", 0.95); cabeza(F(4.30), 9, 0, 0)
# ================================================================== PLANO 4 · general: "¡y hasta sorprenderme!"
cara(F(4.46), "enfado", 0.9)
cara(F(4.58), "sorpresa", 1.0); cabeza(F(4.60), -10, 0, 0); columna(F(4.60), -7, 0, 0); cadera(F(4.60), (0, 0.05, 0.005))
for l in ("R", "L"):
    s = _sx(l)
    mano_en(l, F(4.60), (s * 0.34, -0.20, 1.50)); codo_hacia(l, F(4.60), (s * 0.85, 0.15, 1.05)); mano_pose(l, F(4.60), "abierta")
    orientar_mano(l, F(4.60), palma_hacia=(0, -1, 0), dedos_hacia=(s * 0.3, 0, 1))
    mano_en(l, F(4.78), (s * 0.35, -0.20, 1.53))                  # pequeño rebote
    mano_en(l, F(5.30), (s * 0.34, -0.20, 1.51))
cadera(F(4.78), (0, 0.055, 0.0)); cabeza(F(4.80), -9, 0, 0)
cara(F(5.30), "sorpresa", 0.9); cadera(F(5.30), (0, 0.05, 0.0))
# ================================================================== PLANO 5 · medio + acercamiento: "Bueno, ¿qué? ¿Empezamos?"
cara(F(5.58), "picaro"); cabeza(F(5.68), 0, 7, 0); columna(F(5.68), 0, 0, 0); cadera(F(5.68), (0, 0, 0))
for l in ("R", "L"):
    s = _sx(l)
    mano_en(l, F(5.75), (s * 0.33, -0.25, 1.02)); codo_hacia(l, F(5.75), (s * 0.70, 0.30, 0.85)); mano_pose(l, F(5.75), "abierta")
    orientar_mano(l, F(5.75), palma_hacia=(0, 0, 1), dedos_hacia=(s * 0.5, -1, 0))
    hombro(l, F(6.02), 13)
    mano_en(l, F(6.02), (s * 0.34, -0.25, 1.05))
cabeza(F(6.02), 0, 9, 0)
for l in ("R", "L"): hombro(l, F(6.20), 0)
# "¿Empezamos?": mano izquierda a la cadera, pulgar arriba con la derecha y guiño
mano_en("L", F(6.42), (0.27, -0.02, 1.00)); codo_hacia("L", F(6.42), (0.55, 0.10, 1.10)); mano_pose("L", F(6.42), "relajada")
mano_en("R", F(6.38), (-0.14, -0.32, 1.22)); codo_hacia("R", F(6.38), (-0.70, 0.10, 0.80)); mano_pose("R", F(6.38), "pulgar")
orientar_mano("R", F(6.38), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", F(6.52), (-0.14, -0.33, 1.27)); orientar_mano("R", F(6.52), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", F(6.64), (-0.14, -0.32, 1.24))
cara(F(6.36), "sonrisa"); cabeza(F(6.42), 3, -6, 0)
parpadeo(F(6.95), 1.0, lado="L")      # guiño
mano_en("R", FIN - 10, (-0.14, -0.32, 1.25)); orientar_mano("R", FIN - 10, pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
cara(FIN, "sonrisa", 0.85); cabeza(FIN, 2, -4, 0); mano_en("L", FIN, (0.27, -0.02, 1.00))

hablar(VOZ)
parpadeos(1, FIN, evitar=(F(6.95), F(4.6), F(2.8)))
respirar(1, FIN, periodo=64, amplitud=1.5)
suavizar()
ad = sk.animation_data
if ad and ad.action:
    try: cv = list(ad.action.fcurves)
    except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
    for fc in cv:
        for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
        fc.update()

# ------------------------------------------------------------------ estudio y luces
if "Ciclorama" not in bpy.data.objects:
    mat = bpy.data.materials.get("Estudio") or bpy.data.materials.new("Estudio"); mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.20, 0.045, 0.06, 1); b.inputs["Roughness"].default_value = 0.9
    mesh = bpy.data.meshes.new("Ciclorama"); bm = bmesh.new(); prof = [(-8, 0)]
    for i in range(25):
        a = (i / 24) * math.pi / 2; r = 2.5; prof.append((3 + r * math.sin(a), r - r * math.cos(a)))
    prof.append((5.5, 10))
    rows = [[bm.verts.new((x, y, z)) for x in (-8, 8)] for (y, z) in prof]
    for a_, c_ in zip(rows[:-1], rows[1:]): bm.faces.new((a_[0], a_[1], c_[1], c_[0]))
    bm.to_mesh(mesh); bm.free(); mesh.materials.append(mat)
    for p in mesh.polygons: p.use_smooth = True
    o = bpy.data.objects.new("Ciclorama", mesh); sc.collection.objects.link(o)
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.2, 0.05, 0.06, 1)
LUZ = {"Clave": ((1.8, -2.2, 2.6), 430, (1, 0.93, 0.85)), "Relleno": ((-2.4, -1.8, 1.7), 190, (0.85, 0.9, 1)),
       "Contra": ((-1.0, 2.5, 2.6), 800, (1, 0.75, 0.55))}
for n, (loc, e, col) in LUZ.items():
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, "AREA")); sc.collection.objects.link(o); o.data.size = 1.5
    o.location = loc; o.data.energy = e; o.data.color = col
    o.rotation_euler = (Vector((0, 0, 1.35)) - o.location).to_track_quat("-Z", "Y").to_euler()

# ------------------------------------------------------------------ cámara: 5 planos con cortes secos
cam = bpy.data.objects.get("CAM")
if cam is None:
    cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam)
cam.animation_data_clear(); cam.data.animation_data_clear()
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.05
def ck(f, loc, t, lens):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
    cam.data.keyframe_insert("lens", frame=f)
PLANOS = [  # (posición inicial, mira inicial, posición final, mira final, focal)
    ((0.10, -3.05, 1.10), (0, 0, 1.04), (0.08, -2.80, 1.12), (0, 0, 1.06), 35),      # 1 general
    ((0.80, -2.05, 1.48), (0, 0, 1.34), (0.74, -1.95, 1.48), (0, 0, 1.35), 35),      # 2 medio 3/4 (su izquierda)
    ((0.05, -1.42, 1.56), (0, 0, 1.45), (0.03, -1.30, 1.57), (0, 0, 1.46), 35),      # 3 primer plano
    ((-0.55, -2.70, 1.28), (0, 0, 1.24), (-0.50, -2.60, 1.29), (0, 0, 1.25), 35),    # 4 general (su derecha)
    ((0.12, -2.55, 1.30), (0, 0, 1.24), (0.06, -1.80, 1.45), (0, 0, 1.37), 35),      # 5 medio -> medio corto
]
for i, (p0, t0, p1, t1, lens) in enumerate(PLANOS):
    f0, f1 = CORTES[i], CORTES[i + 1] - 1
    ck(f0, p0, t0, lens); ck(f1, p1, t1, lens)
def _curvas(idb):
    ad_ = idb.animation_data
    if not ad_ or not ad_.action: return []
    try: return list(ad_.action.fcurves)
    except Exception: return [fc for l in ad_.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
fin_plano = {c - 1 for c in CORTES[1:]}
for fc in _curvas(cam) + _curvas(cam.data):
    for k in fc.keyframe_points:
        f = int(round(k.co[0]))
        k.interpolation = 'CONSTANT' if f in fin_plano else 'BEZIER'
        k.easing = 'AUTO'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
    fc.update()

sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 67
sc.eevee.taa_render_samples = 48; sc.render.fps = 30
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.view_settings.exposure = -0.15
sc.frame_start, sc.frame_end = 1, FIN

# ------------------------------------------------------------------ comprobación del encuadre
def comprobar_encuadre(margen=0.015):
    """Devuelve los fotogramas en que una mano en gesto (por encima de 1,02 m) o la cabeza se salen por
    arriba o por los lados. Salir por abajo se permite (la mano entra o sale del plano)."""
    from bpy_extras.object_utils import world_to_camera_view as w2c
    pts = {"R": ["RightHand", "RightHandIndex3", "RightHandMiddle3", "RightHandPinky3", "RightHandThumb3"],
           "L": ["LeftHand", "LeftHandIndex3", "LeftHandMiddle3", "LeftHandPinky3", "LeftHandThumb3"]}
    malos = []
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f); mw = ALEX.matrix_world
        for lado, bones in pts.items():
            ws = [mw @ PB["mixamorig:" + b].tail for b in bones]
            if max(w.z for w in ws) < 1.02: continue
            for w in ws:
                c = w2c(sc, cam, w)
                if c.x < margen or c.x > 1 - margen or c.y > 1 - margen:
                    malos.append((f, lado, round(c.x, 3), round(c.y, 3))); break
        top = mw @ (PB["mixamorig:Head"].tail + Vector((0, 0, 0.02)))
        c = w2c(sc, cam, top)
        if c.y > 1 - margen or c.x < margen or c.x > 1 - margen: malos.append((f, "cabeza", round(c.x, 3), round(c.y, 3)))
    return malos
malos = comprobar_encuadre()
result = {"fin": FIN, "cortes": CORTES, "fuera_de_plano": len(malos), "ejemplos": malos[:25]}
