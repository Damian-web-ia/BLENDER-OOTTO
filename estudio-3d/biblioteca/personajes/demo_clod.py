# DEMO CLOD v2 (con voz): Clod se presenta y enseña su pantalla LED nueva. 4 planos, vídeo vertical 9:16.
# Voz de Ootto (Diego): "¡Hola, hola! Soy Clod. ¡Mira mi pantalla nueva! Feliz, sorprendido, enfadado y triste. ¡Ja! ¿Vamos allá?"
# Se ejecuta sobre clod_v2.blend (abierto). Necesita: ANIM_C = ruta de clod_anim.py, MODELO_C = ruta de clod_v2.py
import bpy, math, bmesh
from mathutils import Vector
D_ = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D\biblioteca\personajes"
try: ANIM_C
except NameError: ANIM_C = D_ + r"\clod_anim.py"
try: MODELO_C
except NameError: MODELO_C = D_ + r"\clod_v2.py"
exec(open(ANIM_C, encoding="utf-8").read())
_m = {"__name__": "modelo"}; exec(open(MODELO_C, encoding="utf-8").read(), _m)
sc = bpy.context.scene
D = 0.6
VOZ = [{"at": D, "words": [["¡Hola", 0.119, 0.36], ["hola", 0.36, 0.68], ["Soy", 0.68, 0.84], ["Clod", 0.84, 1.24], ["¡Mira", 1.43, 1.66], ["mi", 1.66, 1.74], ["pantalla", 1.74, 2.14], ["nueva", 2.14, 2.46], ["Feliz", 2.47, 3.12], ["sorprendido", 3.13, 3.98], ["enfadado", 4.0, 4.64], ["y", 4.64, 4.72], ["triste", 4.72, 5.04], ["¡Ja", 5.40, 5.48], ["¿Vamos", 5.48, 5.72], ["allá", 5.72, 6.04]]}]
def F(t): return int(round((D + t) * 30)) + 1
FIN = F(6.04) + 62
CORTES = [1, F(1.36), F(3.99), F(5.30), FIN + 1]

CL = ClodAnim()
# ---------------------------------------------------------------- limpieza
for ob in [CL.arm] + list(CL.ctrl.values()) + CL.ojos + [CL.bocaob]:
    ob.animation_data_clear()
    if ob.data and getattr(ob.data, "shape_keys", None) and ob.data.shape_keys.animation_data: ob.data.shape_keys.animation_data_clear()
CL.reposo(1)
def S(l): return -1 if l == "R" else 1

# ================================================================ PLANO 1 · general: "¡Hola, hola! Soy Clod."
CL.cabeza(1, 0, 0, 32); CL.cuerpo(1, 0, 0, 12); CL.mirar(1, 0.03, 0.005); CL.cara(1, "neutra")
CL.cabeza(F(-0.25), 0, 0, 30); CL.mirar(F(-0.25), 0.03, 0.005)
CL.cabeza(F(-0.05), 4, 0, 28)                                     # anticipación
CL.cabeza(F(0.15), -6, -4, 0); CL.cuerpo(F(0.2), 0, 0, 0); CL.mirar(F(0.10), 0, 0)
CL.cara(F(0.05), "sorpresa", 0.6); CL.cara(F(0.30), "feliz")
CL.rebote(F(0.10), veces=2, alto=0.025, cada=7)
# saludo con la derecha
CL.mano_en("R", F(0.20), (-0.33, -0.06, 0.66)); CL.codo_hacia("R", F(0.20), (-0.80, 0.30, 0.45)); CL.pulgar("R", F(0.20), 0.7)
for t, x in ((0.36, -0.29), (0.52, -0.37), (0.68, -0.29), (0.84, -0.36)):
    CL.mano_en("R", F(t), (x, -0.06, 0.665))
CL.cabeza(F(0.6), -3, 6, 0)
# "Soy Clod": mano al pecho, se inclina un poco
CL.mano_en("R", F(1.02), (-0.12, -0.21, 0.45)); CL.codo_hacia("R", F(1.02), (-0.60, 0.20, 0.35)); CL.pulgar("R", F(1.02), 0.2)
CL.cabeza(F(1.05), 6, -5, 0); CL.cuerpo(F(1.05), 5, 0, 0); CL.cara(F(1.0), "contento")
CL.mano_en("R", F(1.30), (-0.12, -0.215, 0.46))
# ================================================================ PLANO 2 · medio: "¡Mira mi pantalla nueva! Feliz... ¡sorprendido!"
for l in ("R", "L"):
    CL.mano_en(l, F(1.50), (S(l) * 0.26, -0.13, 0.62)); CL.codo_hacia(l, F(1.50), (S(l) * 0.70, 0.20, 0.45)); CL.pulgar(l, F(1.50), 1.0)
    CL.mano_en(l, F(2.30), (S(l) * 0.26, -0.135, 0.63))
CL.cuerpo(F(1.5), 0, 0, 0); CL.cabeza(F(1.55), -4, 0, 0); CL.cara(F(1.5), "contento"); CL.mirar(F(1.5), 0, 0.012)
CL.mirar(F(1.85), -0.022, 0.012); CL.mirar(F(2.15), 0.022, 0.012); CL.mirar(F(2.40), 0, 0)
# Feliz: ojos de alegría y saltitos
for l in ("R", "L"):
    CL.brazo_caido(l, F(2.52)); CL.mano_en(l, F(2.70), (S(l) * 0.30, -0.08, 0.50)); CL.codo_hacia(l, F(2.70), (S(l) * 0.70, 0.25, 0.40))
CL.cara(F(2.47), "feliz"); CL.cabeza(F(2.6), -5, 7, 0)
CL.rebote(F(2.55), veces=2, alto=0.03, cada=8)
CL.cabeza(F(3.0), -5, -6, 0)
# ¡sorprendido!: se echa atrás, se estira y levanta las manos
CL.cara(F(3.12), "sorpresa"); CL.cabeza(F(3.18), -10, 0, 0); CL.cuerpo(F(3.18), -6, 0, 0)
CL.aplastar(F(3.10), 1.0); CL.aplastar(F(3.20), 1.14); CL.aplastar(F(3.34), 0.96); CL.aplastar(F(3.48), 1.03); CL.aplastar(F(3.70), 1.0)
for l in ("R", "L"):
    CL.mano_en(l, F(3.20), (S(l) * 0.27, -0.10, 0.62)); CL.codo_hacia(l, F(3.20), (S(l) * 0.75, 0.15, 0.45)); CL.pulgar(l, F(3.20), 1.0)
    CL.mano_en(l, F(3.90), (S(l) * 0.27, -0.10, 0.61))
CL.mirar(F(3.2), 0, 0.01); CL.cara(F(3.85), "sorpresa", 0.9)
# ================================================================ PLANO 3 · medio 3/4: "enfadado... y triste."
CL.cara(F(4.02), "enfado"); CL.cabeza(F(4.06), 8, 0, 0); CL.cuerpo(F(4.06), 6, 0, 0); CL.mirar(F(4.02), 0, -0.004)
for l in ("R", "L"):
    CL.mano_en(l, F(4.10), (S(l) * 0.225, -0.01, 0.33)); CL.codo_hacia(l, F(4.10), (S(l) * 0.70, 0.10, 0.45)); CL.pulgar(l, F(4.10), 0.0)
CL.cadera(F(4.10), (0, 0, 0)); CL.cadera(F(4.25), (0, 0, -0.012)); CL.cadera(F(4.45), (0, 0, 0))
CL.cabeza(F(4.30), 8, 4, 0); CL.cabeza(F(4.50), 8, -4, 0); CL.cara(F(4.55), "enfado")
# triste: hombros caídos, cabeza abajo
CL.cara(F(4.70), "triste"); CL.cabeza(F(4.78), 16, 6, 0); CL.cuerpo(F(4.78), 9, 0, 0); CL.mirar(F(4.72), 0, -0.012)
for l in ("R", "L"):
    CL.mano_en(l, F(4.80), (S(l) * 0.235, -0.04, 0.275)); CL.codo_hacia(l, F(4.80), (S(l) * 0.40, 0.45, 0.38))
CL.aplastar(F(4.75), 1.0); CL.aplastar(F(4.95), 0.95)
CL.cabeza(F(5.22), 17, 7, 0); CL.cara(F(5.22), "triste")
# ================================================================ PLANO 4 · general: "¡Ja! ¿Vamos allá?"
CL.cara(F(5.34), "risa"); CL.cabeza(F(5.40), -8, -4, 0); CL.cuerpo(F(5.40), -3, 0, 0); CL.mirar(F(5.34), 0, 0); CL.aplastar(F(5.38), 1.08)
CL.aplastar(F(5.50), 1.0)
for l in ("R", "L"): CL.brazo_caido(l, F(5.40))
CL.mano_en("L", F(5.40), (0.225, -0.01, 0.33)); CL.codo_hacia("L", F(5.40), (0.70, 0.10, 0.45))   # mano en la cadera
f_pulgar = F(5.50)
CL.pulgar_arriba("R", f_pulgar, dur=26)
CL.cara(F(5.75), "feliz"); CL.cabeza(F(5.75), -2, -7, 0)
CL.parpadeo(F(6.20), lado="L")                                      # guiño
f = CL.salto(F(6.55), alto=0.20, aire=12)
CL.cara(f, "feliz"); CL.cabeza(f, -3, -4, 0)
CL.mano_en("R", f + 4, (-0.17, -0.19, 0.44)); CL.pulgar("R", f + 4, 1.0)

CL.hablar(VOZ)
CL.parpadeos(1, FIN, cada=(50, 80), evitar=[(F(6.20), F(6.20)), (F(2.47), F(3.12))])
CL.suavizar()

# ---------------------------------------------------------------- estudio
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
    o = bpy.data.objects.new("Ciclorama", mesh); sc.collection.objects.link(o); o.scale = (0.3, 0.3, 0.3)
for n in ("Suelo",):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
if not sc.world: sc.world = bpy.data.worlds.new("Mundo")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.2, 0.05, 0.06, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
LUZ = {"Clave": ((0.55, -0.75, 0.80), 55, (1, 0.93, 0.85)), "Relleno": ((-0.75, -0.55, 0.45), 20, (0.85, 0.9, 1)),
       "Contra": ((-0.30, 0.75, 0.85), 70, (1, 0.75, 0.55))}
for n, (loc, e, col) in LUZ.items():
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, "AREA")); sc.collection.objects.link(o)
    o.data.size = 1.4 if n != "Relleno" else 0.8; o.location = loc; o.data.energy = e; o.data.color = col
    o.rotation_euler = (Vector((0, 0, 0.18)) - o.location).to_track_quat("-Z", "Y").to_euler()
_m["brillo_led"](sc, umbral=6.0)

# ---------------------------------------------------------------- cámara: 4 planos
cam = bpy.data.objects.get("CAM")
if cam is None:
    cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam)
cam.animation_data_clear(); cam.data.animation_data_clear()
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.01
def ck(f, loc, t, lens):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
PLANOS = [
    [(CORTES[0], (0.10, -1.10, 0.20), (0, 0, 0.165), 50), (CORTES[1] - 1, (0.08, -1.00, 0.20), (0, 0, 0.165), 50)],
    [(CORTES[1], (0.04, -0.84, 0.27), (0, 0, 0.215), 50), (CORTES[2] - 1, (0.03, -0.77, 0.27), (0, 0, 0.215), 50)],
    [(CORTES[2], (0.42, -0.86, 0.25), (0, 0, 0.20), 50), (CORTES[3] - 1, (0.38, -0.80, 0.245), (0, 0, 0.20), 50)],
    [(CORTES[3], (-0.08, -1.05, 0.21), (0, 0, 0.18), 50), (CORTES[4] - 1, (-0.06, -0.92, 0.22), (0, 0, 0.20), 50)],
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
sc.frame_start, sc.frame_end = 1, FIN

# ---------------------------------------------------------------- comprobación del encuadre
def comprobar_encuadre(margen=0.01):
    from bpy_extras.object_utils import world_to_camera_view as w2c
    malos = []
    piezas = [bpy.data.objects[n] for n in ("CLOD_Mano_R", "CLOD_Mano_L", "CLOD_Cabeza", "CLOD_Casco_R", "CLOD_Casco_L")]
    for f_ in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f_)
        for o in piezas:
            c = w2c(sc, cam, o.matrix_world.translation)
            if c.x < margen or c.x > 1 - margen or c.y > 1 - margen: malos.append((f_, o.name, round(c.x, 3), round(c.y, 3)))
    return malos
malos = comprobar_encuadre()
result = {"fin": FIN, "cortes": CORTES, "fuera_de_plano": len(malos), "ejemplos": malos[:20]}
