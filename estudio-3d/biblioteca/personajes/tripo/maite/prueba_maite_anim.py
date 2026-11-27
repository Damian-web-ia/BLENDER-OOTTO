# PRUEBA DE ANIMACIÓN DE MAITE v2 (6 s) · EKORUEDAS · 27-11-2026
# Uso: blender -b --factory-startup --python prueba_maite_anim.py -- <carpeta_estudio> <carpeta_fotogramas> [muestras] [porcentaje]
# Respira, gira hacia su izquierda explicando, se vuelve rápido a la derecha señalando (latigazo para la trenza),
# rebota presentando con las dos manos y se queda quieta para ver cómo se asienta la trenza.
import bpy, os, sys, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = argv[0], argv[1]
MUESTRAS = int(argv[2]) if len(argv) > 2 else 24
PCT = int(argv[3]) if len(argv) > 3 else 50
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(PM, "maite_v2.blend"))
sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = 1, 180
ARM = bpy.data.objects["MAITE_rig"]; ARM.scale = (1.73, 1.73, 1.73)
MA = {"__name__": "maite_anim"}; exec(open(os.path.join(PM, "maite_anim.py"), encoding="utf-8").read(), MA)
M = MA["MaiteAnim"](ARM)

# ---------------------------------------------------------------- animación
M.pose_reposo(1); M.cabeza(1); M.torso(1)
M.pose_reposo(14)
# 1) se gira a su izquierda y explica con la derecha
M.torso(34, giro=18, adelante=3); M.cabeza(34, giro=22, arriba=2)
M.brazo(34, "R", "explica"); M.mano(34, "R", "abierta", muneca=(0, -20, 0))
M.brazo(46, "R", "explica_alto"); M.mano(46, "R", "abierta", muneca=(0, -10, 8))
M.brazo(56, "R", "explica"); M.mano(56, "R", "relajada")
# 2) latigazo a su derecha señalando con la izquierda
M.brazo(60, "L", "reposo"); M.mano(60, "L", "relajada")
M.torso(62, giro=15); M.cabeza(62, giro=18)
M.torso(70, giro=-20, adelante=2); M.cabeza(70, giro=-32, arriba=4, ladeo=-4)
M.brazo(62, "R", "reposo"); M.mano(62, "R", "relajada")
M.brazo(70, "L", "senala"); M.mano(70, "L", "senala")
M.brazo(92, "L", "senala"); M.mano(92, "L", "senala")
# 3) rebote presentando con las dos manos
M.brazo(92, "R", "reposo"); M.mano(92, "R", "relajada")
M.caderas(92); M.caderas(100, baja=0.05); M.caderas(108, baja=-0.01); M.caderas(116)
M.torso(100, adelante=6); M.torso(112, giro=0, adelante=-2)
M.cabeza(100, giro=0, arriba=-4); M.cabeza(112, arriba=6, ladeo=6)
M.brazo(104, "L", "presenta"); M.brazo(104, "R", "presenta")
M.mano(104, "L", "abierta"); M.mano(104, "R", "abierta")
# 4) vuelve al reposo y se queda (para ver cómo se asienta la trenza)
M.pose_reposo(136); M.cabeza(136, ladeo=5, giro=-4); M.torso(136)
M.cabeza(180, ladeo=3, giro=-2)
M.respirar(1, 180); M.vida(1, 180, 0.8)
M.finalizar(1, 180)

# ---------------------------------------------------------------- estudio (como las fotos de referencia)
import bmesh
def mat(nombre, color, rugo):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = color; b.inputs["Roughness"].default_value = rugo
    return m
bm = bmesh.new(); filas = []
front = [bm.verts.new((x, -9, 0)) for x in (-9, 9)]; filas.append(front)
for i in range(25):
    a = math.radians(90 * i / 24); r = 1.6
    filas.append([bm.verts.new((x, 3.0 - r + math.sin(a) * r, r - math.cos(a) * r)) for x in (-9, 9)])
filas.append([bm.verts.new((x, 3.0, 9)) for x in (-9, 9)])
for a_, b_ in zip(filas[:-1], filas[1:]): bm.faces.new((a_[0], a_[1], b_[1], b_[0]))
md = bpy.data.meshes.new("Ciclorama"); bm.to_mesh(md); bm.free()
cic = bpy.data.objects.new("Ciclorama", md); sc.collection.objects.link(cic)
for pl in md.polygons: pl.use_smooth = True
cic.data.materials.append(mat("Fondo", (0.018, 0.021, 0.027, 1), 0.55))
def luz(n, loc, e, tam, col, mira=(0, 0, 1.2)):
    d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.size = tam; d.color = col; d.shape = 'DISK'
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
luz("Clave", (-1.6, -2.2, 2.6), 420, 1.6, (1.0, 0.90, 0.80))
luz("Relleno", (2.2, -1.8, 1.4), 120, 2.4, (0.70, 0.80, 1.0))
luz("Contra_izq", (-1.4, 1.6, 2.4), 360, 0.9, (0.55, 0.72, 1.0), mira=(0, 0, 1.4))
luz("Contra_der", (1.5, 1.4, 2.2), 260, 0.9, (1.0, 0.78, 0.55), mira=(0, 0, 1.3))
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.006, 0.008, 0.012, 1)
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (-0.95, -2.55, 1.38); cd.lens = 50
mira = Vector((0.04, 0, 1.18)); cam.rotation_euler = (mira - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.use_dof = True; cd.dof.aperture_fstop = 4.0; cd.dof.focus_distance = (mira - cam.location).length - 0.1

sc.render.engine = 'CYCLES'; sc.cycles.samples = MUESTRAS; sc.cycles.use_denoising = True
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = 'GPU'
except Exception as e: print("GPU", e)
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, PCT
sc.render.use_persistent_data = True
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PM, "prueba_maite_anim.blend"), compress=True)
sc.render.filepath = os.path.join(OUT, "f_")
sc.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(animation=True)
open(os.path.join(OUT, "DONE.txt"), "w").write("ok")
print("PRUEBA_OK", flush=True)
