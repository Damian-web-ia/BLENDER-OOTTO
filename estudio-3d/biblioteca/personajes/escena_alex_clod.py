# ESCENA CONJUNTA · Alex y Clod (con voces). Vídeo vertical 9:16, 5 planos.
# Diálogo (voz_dialogo.ogg, ya montado con sus silencios; empieza en el fotograma 1):
#   Clod (Diego): "¡Alex, mira! ¡Tengo pantalla nueva!"
#   Alex (Carlos): "¡Anda! Y yo ya puedo sonreír."
#   Clod: "¿Y enfadarte?"            Alex: "¡Grrr! ¿Así?"
#   Clod: "¡Ja, ja! ¡Perfecto! ¿Empezamos?"            Alex: "¡Empezamos!"
# Se ejecuta sobre alex_v2_rig.blend abierto. Añade a Clod desde clod_v2.blend (encima de un banco de trabajo).
import bpy, math, bmesh
from mathutils import Vector
D_ = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D\biblioteca\personajes"
ANIM = D_ + r"\alex_anim.py"; ANIM_C = D_ + r"\clod_anim.py"; MODELO_C = D_ + r"\clod_v2.py"
CLOD_BLEND = D_ + r"\clod\clod_v2.blend"
sc = bpy.context.scene

# ---------------------------------------------------------------- Clod en la escena (anexar una vez)
if "CLOD_v2" not in bpy.data.objects:
    with bpy.data.libraries.load(CLOD_BLEND, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c in ("CLOD_v2_personaje", "CLOD_v2_controles")]
    for c in dst.collections:
        if c.name not in sc.collection.children: sc.collection.children.link(c)
exec(open(ANIM, encoding="utf-8").read())
exec(open(ANIM_C, encoding="utf-8").read())
_m = {"__name__": "modelo"}; exec(open(MODELO_C, encoding="utf-8").read(), _m)

def F(t): return int(round(t * 30)) + 1
VOZ_ALEX = [{"at": 0, "words": [["¡Anda", 2.905, 3.37], ["Y", 3.39, 3.57], ["yo", 3.60, 3.68], ["ya", 3.68, 3.81], ["puedo", 3.81, 4.05], ["sonreír", 4.05, 4.61]]},
            {"at": 0, "words": [["¡Grrr", 6.041, 6.47], ["¿Así", 6.621, 7.10]]},
            {"at": 0, "words": [["¡Empezamos", 9.563, 10.21]]}]
VOZ_CLOD = [{"at": 0, "words": [["¡Alex", 0.62, 1.10], ["mira", 1.146, 1.47], ["¡Tengo", 1.54, 1.77], ["pantalla", 1.77, 2.17], ["nueva", 2.17, 2.57]]},
            {"at": 0, "words": [["¿Y", 4.97, 5.13], ["enfadarte", 5.13, 5.69]]},
            {"at": 0, "words": [["¡Ja", 7.519, 7.76], ["ja", 7.76, 8.00], ["¡Perfecto", 8.061, 8.59], ["¿Empezamos", 8.59, 9.27]]}]
FIN = F(10.21) + 45
CORTES = [1, F(2.75), F(4.85), F(5.90), F(7.35), FIN + 1]

# ---------------------------------------------------------------- limpieza y colocación
ALEX.animation_data_clear()
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
sk = MALLA.data.shape_keys
if sk.animation_data and sk.animation_data.action: sk.animation_data.action = None
ALEX.location = (0, 0, 0); ALEX.rotation_euler = (0, 0, math.radians(10))     # un poco girado hacia Clod
CL = ClodAnim()
for ob in [CL.arm] + list(CL.ctrl.values()) + CL.ojos + [CL.bocaob]:
    ob.animation_data_clear()
    if getattr(ob.data, "shape_keys", None) and ob.data.shape_keys.animation_data: ob.data.shape_keys.animation_data_clear()
POS_CLOD = (0.40, -0.55, 0.90); GIRO_CLOD = -50     # delante y a la derecha de Alex (más cerca de cámara)
CL.mover(1, POS_CLOD, GIRO_CLOD)
todo_reposo(1); sc.frame_set(1); calibrar_palma()
for l in ("R", "L"): brazo_caido(l, 1)
CL.reposo(1)
def SX(l): return -1 if l == "R" else 1

# ================================================================ ALEX
cara(1, "sonrisa", 0.3); cabeza(1, 25, 0, 26); columna(1, 4, 0, 6)
cara(F(0.70), "sorpresa", 0.4); cabeza(F(0.78), 26, 3, 28)
cara(F(1.60), "sonrisa", 0.8); columna(F(2.0), 6, 0, 8); cabeza(F(2.3), 26, 6, 26)
# "¡Anda! Y yo ya puedo sonreír."
cara(F(2.85), "sorpresa", 0.8); cabeza(F(2.98), -3, 0, -22); columna(F(2.98), -2, 0, -6)
mano_en("R", F(3.05), (-0.31, -0.03, 0.89))
mano_en("R", F(3.35), (-0.07, -0.24, 1.22)); codo_hacia("R", F(3.35), (-0.70, 0.00, 0.90)); mano_pose("R", F(3.35), "abierta")
orientar_mano("R", F(3.35), palma_hacia=(0, 1, 0), dedos_hacia=(1, 0, 0.3))
mano_en("R", F(3.80), (-0.06, -0.25, 1.23)); cara(F(3.40), "sonrisa", 0.8); cabeza(F(3.45), 5, -4, -22)
cara(F(4.02), "risa"); cabeza(F(4.12), -6, 5, -20)
# abre la mano derecha hacia fuera, palma arriba (la izquierda sigue relajada)
mano_en("R", F(4.15), (-0.31, -0.24, 1.16)); codo_hacia("R", F(4.15), (-0.8, 0.3, 0.9)); mano_pose("R", F(4.15), "abierta")
orientar_mano("R", F(4.15), palma_hacia=(0, 0, 1), dedos_hacia=(-0.6, -1, 0.2))
mano_en("R", F(4.62), (-0.32, -0.24, 1.18)); mano_pose("R", F(4.62), "abierta")
orientar_mano("R", F(4.62), palma_hacia=(0, 0, 1), dedos_hacia=(-0.6, -1, 0.2))
brazo_caido("L", F(4.15)); mano_pose("L", F(4.15), "relajada")
# escucha a Clod: "¿Y enfadarte?"
for l in ("R", "L"): brazo_caido(l, F(5.00)); mano_pose(l, F(5.00), "relajada"); mano_giro(l, F(5.00))
cara(F(5.05), "sonrisa", 0.6); cabeza(F(5.10), 25, 0, 26); columna(F(5.1), 4, 0, 6)
cara(F(5.60), "duda", 0.6); cabeza(F(5.70), 24, -5, 24)
# "¡Grrr! ¿Así?"
cara(F(5.98), "enfado"); cabeza(F(6.05), 8, 0, -6); columna(F(6.05), 7, 0, 0)
for l in ("R", "L"):
    mano_en(l, F(6.10), (SX(l) * 0.12, -0.27, 1.23)); codo_hacia(l, F(6.10), (SX(l) * 0.70, 0.35, 1.00)); mano_pose(l, F(6.10), "puño")
for t, dz in ((6.20, 0.025), (6.30, -0.005), (6.40, 0.02), (6.50, 0.0)):
    for l in ("R", "L"): mano_en(l, F(t), (SX(l) * 0.12, -0.27, 1.23 + dz))
cara(F(6.60), "duda"); cabeza(F(6.72), 22, -8, 24); columna(F(6.72), 4, 0, 6)
for l in ("R", "L"): brazo_caido(l, F(6.95)); mano_pose(l, F(6.95), "relajada")
# Clod se ríe
cara(F(7.60), "risa"); cabeza(F(7.70), 18, 4, 24)
cadera(F(7.6), (0, 0, 0)); cadera(F(7.75), (0, 0, -0.008)); cadera(F(7.9), (0, 0, 0.004)); cadera(F(8.05), (0, 0, 0))
cara(F(8.7), "sonrisa"); cabeza(F(9.15), 2, -4, -6); columna(F(9.15), 0, 0, 0)
# "¡Empezamos!": pulgar arriba a cámara, mano izquierda en la cadera y guiño
mano_en("L", F(9.45), (0.27, -0.02, 1.00)); codo_hacia("L", F(9.45), (0.55, 0.10, 1.10)); mano_pose("L", F(9.45), "relajada")
mano_en("R", F(9.40), (-0.14, -0.32, 1.22)); codo_hacia("R", F(9.40), (-0.70, 0.10, 0.80)); mano_pose("R", F(9.40), "pulgar")
orientar_mano("R", F(9.40), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", F(9.55), (-0.14, -0.33, 1.27)); orientar_mano("R", F(9.55), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", F(9.70), (-0.14, -0.32, 1.24))
cara(F(9.50), "sonrisa"); cabeza(F(9.55), 3, -6, -6)
parpadeo(F(10.45), 1.0, lado="L")
mano_en("R", FIN - 8, (-0.14, -0.32, 1.25)); orientar_mano("R", FIN - 8, pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
cara(FIN, "sonrisa", 0.85); cabeza(FIN, 2, -4, -6); mano_en("L", FIN, (0.27, -0.02, 1.00))

# ================================================================ CLOD
CL.cara(1, "contento"); CL.cabeza(1, -20, 0, -40); CL.cuerpo(1, 0, 0, -20); CL.mirar(1, -0.025, 0.012)
# "¡Alex, mira!": saluda a Alex
CL.cabeza(F(0.45), -14, 0, -36); CL.cara(F(0.58), "feliz"); CL.cabeza(F(0.66), -22, 4, -42)
fs = CL.saludo("R", F(0.50), ciclos=2, vel=5)
# "¡Tengo pantalla nueva!": se señala la pantalla y mira a cámara
for l in ("R", "L"):
    CL.mano_en(l, F(1.62), (SX(l) * 0.26, -0.13, 0.62)); CL.codo_hacia(l, F(1.62), (SX(l) * 0.70, 0.20, 0.45)); CL.pulgar(l, F(1.62), 1.0)
    CL.mano_en(l, F(2.55), (SX(l) * 0.26, -0.135, 0.63))
CL.cabeza(F(1.62), -6, 0, 28); CL.cuerpo(F(1.62), 0, 0, 10); CL.mirar(F(1.62), 0.02, 0.012); CL.cara(F(1.60), "feliz")
CL.mirar(F(2.05), -0.015, 0.012); CL.mirar(F(2.40), 0.02, 0.012)
# escucha a Alex
for l in ("R", "L"): CL.brazo_caido(l, F(2.85))
CL.cabeza(F(3.00), -20, 6, -42); CL.cuerpo(F(3.0), 0, 0, -20); CL.mirar(F(3.00), -0.02, 0.012); CL.cara(F(2.95), "sorpresa", 0.5)
CL.cara(F(4.08), "feliz"); CL.rebote(F(4.15), veces=2, alto=0.025, cada=7)
# "¿Y enfadarte?": pícaro, mano a la "barbilla"
CL.mover(F(4.75), POS_CLOD, GIRO_CLOD); CL.mover(F(4.92), POS_CLOD, GIRO_CLOD - 22); CL.mover(F(5.88), POS_CLOD, GIRO_CLOD - 22)
CL.mover(F(6.02), POS_CLOD, GIRO_CLOD)                               # se gira hacia Alex (plano 3 = lo que ve Alex)
CL.cara(F(4.95), "contento"); CL.cabeza(F(5.02), -26, -10, -50); CL.cuerpo(F(5.02), 0, 0, -30); CL.mirar(F(5.0), 0.0, 0.012)
CL.cuerpo(F(5.88), 0, 0, -30); CL.cuerpo(F(6.02), 0, 0, -20)
CL.mano_en("R", F(5.05), (-0.12, -0.20, 0.50)); CL.codo_hacia("R", F(5.05), (-0.60, 0.20, 0.35)); CL.pulgar("R", F(5.05), 0.3)
CL.mano_en("R", F(5.70), (-0.12, -0.205, 0.51))
# "¡Grrr!": susto
CL.cara(F(6.08), "susto"); CL.cuerpo(F(6.15), -6, 0, -20)
CL.aplastar(F(6.06), 1.0); CL.aplastar(F(6.14), 1.13); CL.aplastar(F(6.28), 0.95); CL.aplastar(F(6.42), 1.0)
for l in ("R", "L"):
    CL.mano_en(l, F(6.15), (SX(l) * 0.27, -0.10, 0.62)); CL.codo_hacia(l, F(6.15), (SX(l) * 0.75, 0.15, 0.45)); CL.pulgar(l, F(6.15), 1.0)
    CL.mano_en(l, F(6.55), (SX(l) * 0.27, -0.10, 0.61))
CL.cara(F(6.80), "contento"); CL.cuerpo(F(6.85), 0, 0, -20)
for l in ("R", "L"): CL.brazo_caido(l, F(6.95))
# "¡Ja, ja! ¡Perfecto! ¿Empezamos?"
CL.cara(F(7.45), "risa"); CL.cabeza(F(7.55), -16, 8, -36); CL.rebote(F(7.50), veces=2, alto=0.03, cada=7)
CL.cara(F(8.06), "feliz"); CL.cabeza(F(8.10), -6, 0, 26); CL.cuerpo(F(8.1), 0, 0, 10); CL.mirar(F(8.1), 0.02, 0.01)
fp = CL.pulgar_arriba("L", F(8.00), dur=18)
for l in ("R", "L"):
    CL.mano_en(l, F(8.85), (SX(l) * 0.30, -0.08, 0.52)); CL.codo_hacia(l, F(8.85), (SX(l) * 0.70, 0.25, 0.40)); CL.pulgar(l, F(8.85), 0.6)
    CL.mano_giro(l, F(8.85))
CL.cabeza(F(8.75), -8, 0, 24)
# "¡Empezamos!" (Alex): Clod salta de alegría
for l in ("R", "L"): CL.mano_en(l, F(9.55), (SX(l) * 0.30, -0.08, 0.53))
CL.cara(F(9.62), "feliz")
fj = CL.salto(F(9.70), alto=0.22, aire=12)
CL.cara(FIN, "feliz"); CL.cabeza(FIN, -6, 0, 22)

# ---------------------------------------------------------------- voz, parpadeos, respiración, suavizado
hablar(VOZ_ALEX)
CL.hablar(VOZ_CLOD)
parpadeos(1, FIN, evitar=(F(10.45), F(6.05), F(4.1)))
CL.parpadeos(1, FIN, cada=(55, 85), evitar=[(F(0.58), F(2.6)), (F(4.08), F(4.6)), (F(7.45), F(10.6))])
respirar(1, FIN, periodo=64, amplitud=1.5)
suavizar(); CL.suavizar()
ad = sk.animation_data
if ad and ad.action:
    try: cv = list(ad.action.fcurves)
    except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
    for fc in cv:
        for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
        fc.update()

# ---------------------------------------------------------------- decorado: estudio y banco de trabajo
def caja(nombre, centro, tam, mat):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * tam[0], v.co.y * tam[1], v.co.z * tam[2]))
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.get(nombre)
    if o: bpy.data.objects.remove(o, do_unlink=True)
    o = bpy.data.objects.new(nombre, me); sc.collection.objects.link(o); o.location = centro
    m = o.modifiers.new("Bisel", "BEVEL"); m.width = 0.008; m.segments = 3; m.limit_method = 'ANGLE'
    return o
def mat(nombre, color, rough, metal=0.0):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    return m
madera = mat("Banco_Madera", (0.30, 0.17, 0.08), 0.55); metal_ = mat("Banco_Metal", (0.05, 0.05, 0.055), 0.4, 0.6)
mx, my = 0.42, -0.55
caja("Banco_Tablero", (mx, my, 0.875), (0.55, 0.40, 0.05), madera)
for i, (dx, dy) in enumerate(((-0.235, -0.16), (0.235, -0.16), (-0.235, 0.16), (0.235, 0.16))):
    caja(f"Banco_Pata{i}", (mx + dx, my + dy, 0.425), (0.04, 0.04, 0.85), metal_)
caja("Banco_Balda", (mx, my, 0.18), (0.51, 0.36, 0.025), metal_)
if "Ciclorama" not in bpy.data.objects:
    m_ = mat("Estudio", (0.20, 0.045, 0.06), 0.9)
    mesh = bpy.data.meshes.new("Ciclorama"); bm = bmesh.new(); prof = [(-8, 0)]
    for i in range(25):
        a = (i / 24) * math.pi / 2; r = 2.5; prof.append((3 + r * math.sin(a), r - r * math.cos(a)))
    prof.append((5.5, 10))
    rows = [[bm.verts.new((x, y, z)) for x in (-8, 8)] for (y, z) in prof]
    for a_, c_ in zip(rows[:-1], rows[1:]): bm.faces.new((a_[0], a_[1], c_[1], c_[0]))
    bm.to_mesh(mesh); bm.free(); mesh.materials.append(m_)
    for p in mesh.polygons: p.use_smooth = True
    o = bpy.data.objects.new("Ciclorama", mesh); sc.collection.objects.link(o)
if not sc.world: sc.world = bpy.data.worlds.new("Mundo")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.2, 0.05, 0.06, 1)
LUZ = {"Clave": ((1.9, -2.2, 2.6), 430, (1, 0.93, 0.85)), "Relleno": ((-2.4, -1.8, 1.7), 190, (0.85, 0.9, 1)),
       "Contra": ((-1.0, 2.5, 2.6), 800, (1, 0.75, 0.55))}
for n, (loc, e, col) in LUZ.items():
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, "AREA")); sc.collection.objects.link(o); o.data.size = 1.5
    o.location = loc; o.data.energy = e; o.data.color = col
    o.rotation_euler = (Vector((0.2, -0.25, 1.2)) - o.location).to_track_quat("-Z", "Y").to_euler()
_m["brillo_led"](sc, umbral=6.0)

# ---------------------------------------------------------------- cámara: 5 planos
cam = bpy.data.objects.get("CAM")
if cam is None:
    cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam)
cam.animation_data_clear(); cam.data.animation_data_clear()
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.03
def ck(f, loc, t, lens):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
PLANOS = [
    [(CORTES[0], (0.12, -2.40, 1.30), (0.16, -0.25, 1.20), 30), (CORTES[1] - 1, (0.12, -2.28, 1.31), (0.16, -0.25, 1.21), 30)],   # 1 los dos
    [(CORTES[1], (-0.45, -1.75, 1.50), (0.0, 0, 1.38), 30), (CORTES[2] - 1, (-0.42, -1.66, 1.51), (0.0, 0, 1.39), 30)],           # 2 Alex medio
    [(CORTES[2], (0.18, -0.12, 1.52), (0.40, -0.55, 1.10), 40), (CORTES[3] - 1, (0.20, -0.17, 1.49), (0.40, -0.55, 1.10), 40)],    # 3 Clod visto por Alex
    [(CORTES[3], (0.05, -1.32, 1.56), (0.01, 0, 1.49), 40), (CORTES[4] - 1, (0.05, -1.25, 1.56), (0.01, 0, 1.49), 40)],           # 4 Alex cerca
    [(CORTES[4], (0.20, -2.45, 1.30), (0.17, -0.25, 1.20), 30), (CORTES[5] - 1, (0.16, -2.00, 1.34), (0.17, -0.25, 1.26), 30)],   # 5 los dos, acercándose
]
for claves in PLANOS:
    for (f_, p, t, lens) in claves: ck(f_, p, t, lens)
def _curvas(idb):
    ad_ = idb.animation_data
    if not ad_ or not ad_.action: return []
    try: return list(ad_.action.fcurves)
    except Exception: return [fc for l in ad_.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
fin_plano = {c - 1 for c in CORTES[1:]}
for fc in _curvas(cam) + _curvas(cam.data):
    for k in fc.keyframe_points:
        k.interpolation = 'CONSTANT' if int(round(k.co[0])) in fin_plano else 'BEZIER'
        k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
    fc.update()
sc.camera = cam; sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 67
sc.eevee.taa_render_samples = 48; sc.render.fps = 30
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.view_settings.exposure = -0.15
sc.frame_start, sc.frame_end = 1, FIN

# ---------------------------------------------------------------- comprobación del encuadre por plano
def comprobar_encuadre(margen=0.012):
    from bpy_extras.object_utils import world_to_camera_view as w2c
    alex_pts = ["RightHandMiddle3", "LeftHandMiddle3", "RightHandThumb3", "LeftHandThumb3"]
    clod_ob = [bpy.data.objects[n] for n in ("CLOD_Mano_R", "CLOD_Mano_L", "CLOD_Casco_R", "CLOD_Casco_L", "CLOD_Diadema")]
    quien = {0: ("A", "C"), 1: ("A",), 2: ("C",), 3: ("A",), 4: ("A", "C")}
    malos = []
    for f_ in range(sc.frame_start, sc.frame_end + 1):
        plano = max(i for i, c in enumerate(CORTES[:-1]) if f_ >= c)
        sc.frame_set(f_); pts = []
        if "A" in quien[plano]:
            mw = ALEX.matrix_world
            for b in alex_pts:
                w = mw @ PB["mixamorig:" + b].tail
                if w.z > 1.02: pts.append(("A_" + b, w))
            pts.append(("A_cabeza", mw @ (PB["mixamorig:Head"].tail + Vector((0, 0, 0.02)))))
        if "C" in quien[plano]:
            pts += [("C_" + o.name, o.matrix_world.translation) for o in clod_ob]
        for n, w in pts:
            c = w2c(sc, cam, w)
            if c.x < margen or c.x > 1 - margen or c.y > 1 - margen: malos.append((f_, n, round(c.x, 3), round(c.y, 3)))
    return malos
malos = comprobar_encuadre()
result = {"fin": FIN, "cortes": CORTES, "fuera_de_plano": len(malos), "ejemplos": malos[:25]}
