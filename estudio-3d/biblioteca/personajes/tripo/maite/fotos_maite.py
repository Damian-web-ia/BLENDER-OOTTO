# FOTOS DE REFERENCIA DE MAITE (Cycles) · EKORUEDAS · 27-11-2026
# Uso: blender -b --factory-startup --python fotos_maite.py -- <carpeta_estudio> <carpeta_salida> [muestras]
# Abre maite_tripo.blend, la pone en pose natural (brazos abajo, dedos relajados), estudio oscuro con luz
# clave cálida, relleno frío y contraluz, y saca 6 fotos verticales 1080x1920.
import bpy, os, sys, math
from mathutils import Vector, Matrix, Quaternion
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = argv[0], argv[1]; MUESTRAS = int(argv[2]) if len(argv) > 2 else 128
BLEND = argv[3] if len(argv) > 3 else "maite_tripo.blend"
SOLO = set(argv[4].split(",")) if len(argv) > 4 and argv[4] else None
os.makedirs(OUT, exist_ok=True)
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite")
bpy.ops.wm.open_mainfile(filepath=os.path.join(PM, BLEND))
sc = bpy.context.scene
ARM = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
CUERPO = [o for o in bpy.data.objects if o.type == 'MESH'][0]
for img in bpy.data.images:
    if img.source == 'FILE' and not img.packed_file:
        n = os.path.basename(bpy.path.abspath(img.filepath))
        for r_, _d, fs in os.walk(PM):
            if n in fs:
                img.filepath = os.path.join(r_, n); img.reload(); break
ARM.scale = (1.73, 1.73, 1.73)
PB = ARM.pose.bones
for pb in PB: pb.rotation_mode = 'QUATERNION'
def dirigir(nombre, d):
    b = PB.get(nombre)
    if not b: return
    bpy.context.view_layer.update()
    M = b.matrix.copy(); y = M.col[1].xyz.normalized()
    q = y.rotation_difference(Vector(d).normalized())
    b.matrix = Matrix.Translation(M.translation) @ q.to_matrix().to_4x4() @ M.to_3x3().to_4x4()
    bpy.context.view_layer.update()
def dedos(lado, curva):
    for dedo in ("Index", "Middle", "Ring", "Pinky"):
        for k in (1, 2, 3):
            b = PB.get(f"mixamorig:{lado}Hand{dedo}{k}")
            if b: b.rotation_quaternion = Quaternion((1, 0, 0), math.radians(curva * (0.8 + 0.25 * k)))
    for k in (1, 2):
        b = PB.get(f"mixamorig:{lado}HandThumb{k}")
        if b: b.rotation_quaternion = Quaternion((0, 0, 1), math.radians(curva * 0.4 * (1 if lado == 'Left' else -1)))
# pose natural: brazos caídos un poco separados, codos algo doblados, peso en una pierna
dirigir("mixamorig:LeftArm", (0.22, 0.04, -0.97)); dirigir("mixamorig:RightArm", (-0.22, 0.04, -0.97))
dirigir("mixamorig:LeftForeArm", (0.14, -0.20, -0.97)); dirigir("mixamorig:RightForeArm", (-0.14, -0.20, -0.97))
dedos("Left", 18); dedos("Right", 18)
PB["mixamorig:Spine2"].rotation_quaternion = Quaternion((1, 0, 0), math.radians(-2))
PB["mixamorig:Head"].rotation_quaternion = Quaternion((0, 0, 1), math.radians(3)) @ Quaternion((1, 0, 0), math.radians(-3))
PB["mixamorig:Hips"].rotation_quaternion = Quaternion((0, 0, 1), math.radians(2))
bpy.context.view_layer.update()
# ---- estudio
def mat_fondo():
    m = bpy.data.materials.new("Fondo"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.018, 0.021, 0.027, 1)
    b.inputs["Roughness"].default_value = 0.55; return m
bpy.ops.mesh.primitive_plane_add(size=1); suelo = bpy.context.object
mat_fondo()
# fondo: pared detrás con curva suave hacia el suelo (ciclorama abierto, la cámara queda fuera)
import bmesh
bm = bmesh.new(); prev = None; filas = []
for i in range(25):
    a = math.radians(90 * i / 24); r = 1.6
    y = 3.0 + (math.sin(a) * r if i else 0) - r; z = r - math.cos(a) * r
    filas.append([bm.verts.new((x, 3.0 - r + math.sin(a) * r, z)) for x in (-9, 9)])
top = [bm.verts.new((x, 3.0, 9)) for x in (-9, 9)]; filas.append(top)
front = [bm.verts.new((x, -9, 0)) for x in (-9, 9)]; filas.insert(0, front)
for a_, b_ in zip(filas[:-1], filas[1:]): bm.faces.new((a_[0], a_[1], b_[1], b_[0]))
md = bpy.data.meshes.new("Ciclorama"); bm.to_mesh(md); bm.free()
cic = bpy.data.objects.new("Ciclorama", md); sc.collection.objects.link(cic)
for pl in md.polygons: pl.use_smooth = True
cic.data.materials.append(bpy.data.materials["Fondo"])
bpy.data.objects.remove(suelo)
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
# ---- cámara y render
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.dof.use_dof = True; cd.dof.aperture_fstop = 2.8; cd.sensor_width = 36
sc.render.engine = 'CYCLES'; sc.cycles.samples = MUESTRAS; sc.cycles.use_denoising = True
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = 'GPU'
except Exception as e: print("GPU", e)
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.film_transparent = False
def foto(nombre, loc, mira, lente, foco=None):
    if SOLO and nombre[:2] not in SOLO: return
    cam.location = loc; cd.lens = lente
    cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cd.dof.focus_distance = ((Vector(foco or mira) - Vector(loc)).length)
    sc.render.filepath = os.path.join(OUT, nombre + ".png"); bpy.ops.render.render(write_still=True)
    print("FOTO", nombre, flush=True)
foto("01_cuerpo_frente", (0, -4.4, 1.0), (0, 0, 0.88), 50, foco=(0, -0.1, 1.45))
foto("02_cuerpo_tres_cuartos", (-2.9, -3.3, 1.15), (0, 0, 0.90), 50, foco=(0, -0.1, 1.45))
ARM.rotation_euler = (0, 0, math.radians(180)); bpy.context.view_layer.update()   # espalda: se gira ella, no la cámara
foto("03_espalda", (-1.2, -4.2, 1.2), (0, 0, 0.92), 50, foco=(0, -0.05, 1.4))
ARM.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
foto("04_cara", (0.22, -0.95, 1.53), (0.035, 0, 1.50), 85, foco=(0.035, -0.13, 1.51))
foto("05_perfil", (-1.05, -0.06, 1.52), (0, -0.02, 1.50), 85, foco=(-0.10, -0.04, 1.50))
foto("06_trenza_y_manos", (1.4, -1.6, 1.25), (0.10, 0, 1.15), 70, foco=(0.12, -0.05, 1.25))
open(os.path.join(OUT, "HECHO.txt"), "w").write("ok")
print("FOTOS_OK", flush=True)
