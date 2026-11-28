# PRUEBA DEL RIG DE MAITE: poses de estrés (sentadilla con IK, paso con roll de pie, brazos arriba, puño y giro de
# muñeca, mano con IK delante del pecho) en cuerpo entero y primeros planos de articulaciones · EKORUEDAS · 28-11-2026
# Uso: blender -b --factory-startup --python prueba_rig.py -- <carpeta_estudio> <carpeta_salida> [muestras]
import bpy, os, sys, math
from mathutils import Vector, Matrix, Euler
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = argv[0], argv[1]; MUESTRAS = int(argv[2]) if len(argv) > 2 else 48
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(PM, "maite_v2.blend"))
sc = bpy.context.scene
ARM = bpy.data.objects["MAITE_rig"]; ME = bpy.data.objects["MAITE_cuerpo"]
PB = ARM.pose.bones; P = "mixamorig:"
# ---- luz y cámara
def luz(n, loc, e, tam, col, mira=(0, 0, 0.6)):
    d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.size = tam; d.color = col
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
luz("Clave", (-1.6, -2.2, 2.4), 420, 1.6, (1.0, 0.92, 0.84))
luz("Relleno", (2.0, -1.8, 1.4), 160, 2.0, (0.75, 0.82, 1.0))
luz("Contra", (0.8, 2.0, 2.2), 300, 1.2, (1.0, 0.85, 0.7), mira=(0, 0, 0.9))
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.035, 0.038, 0.045, 1)
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0)); suelo = bpy.context.active_object
ms = bpy.data.materials.new("Suelo"); ms.use_nodes = True; ms.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.20, 0.21, 0.23, 1)
suelo.data.materials.append(ms)
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
def camara(loc, mira, lente):
    cam.location = loc; cd.lens = lente; cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = 'GPU'
except Exception as e: print("GPU", e)
sc.render.engine = 'CYCLES'; sc.cycles.samples = MUESTRAS; sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
# ---- utilidades de pose
def limpiar():
    for b in PB:
        b.location = (0, 0, 0); b.rotation_quaternion = (1, 0, 0, 0); b.rotation_euler = (0, 0, 0); b.scale = (1, 1, 1)
    for l in ("L", "R"):
        ARM.pose.bones["CTRL_raiz"][f"ik_brazo_{l}"] = 0.0; ARM.pose.bones["CTRL_raiz"][f"ik_pierna_{l}"] = 1.0
        PB[f"IK_pie_{l}"]["roll"] = 0.0
    bpy.context.view_layer.update()
def dirigir(nombre, d):
    b = PB[nombre]; bpy.context.view_layer.update()
    M_ = b.matrix.copy(); y = M_.col[1].xyz.normalized(); q = y.rotation_difference(Vector(d).normalized())
    b.matrix = Matrix.Translation(M_.translation) @ q.to_matrix().to_4x4() @ M_.to_3x3().to_4x4(); bpy.context.view_layer.update()
def brazos_abajo():
    for lado, sx in (("Left", 1), ("Right", -1)):
        dirigir(P + lado + "Arm", (0.22 * sx, 0.04, -0.97)); dirigir(P + lado + "ForeArm", (0.12 * sx, -0.22, -0.97))
def mover_mundo(nombre, d):
    b = PB[nombre]; bpy.context.view_layer.update()
    b.matrix = Matrix.Translation(Vector(d)) @ b.matrix; bpy.context.view_layer.update()
def girar_local(nombre, eje, grados):
    b = PB[nombre]; b.rotation_mode = 'QUATERNION'
    from mathutils import Quaternion
    b.rotation_quaternion = Quaternion(eje, math.radians(grados)) @ b.rotation_quaternion
    bpy.context.view_layer.update()
CUERPO = ((0.72, -1.80, 0.66), (0.0, 0.0, 0.50), 50)
POSES = []
def pose(nombre, cam_=CUERPO):
    def deco(fn): POSES.append((nombre, fn, cam_)); return fn
    return deco
@pose("01_reposo")
def _(): brazos_abajo()
@pose("02_sentadilla")
def _():
    brazos_abajo(); mover_mundo(P + "Hips", (0, 0.05, -0.13))          # baja 13 cm y la cadera va atrás
    girar_local(P + "Spine", (1, 0, 0), 14); girar_local(P + "Spine1", (1, 0, 0), 10)
    for lado, sx in (("Left", 1), ("Right", -1)):
        dirigir(P + lado + "Arm", (0.20 * sx, -0.85, -0.45)); dirigir(P + lado + "ForeArm", (0.10 * sx, -0.99, 0.0))
@pose("03_paso")
def _():
    brazos_abajo(); PB["IK_pie_L"].location = (0, 0.13, 0); PB["IK_pie_R"].location = (0, -0.07, 0)
    PB["IK_pie_R"]["roll"] = 0.65; mover_mundo(P + "Hips", (0, -0.03, -0.02))
@pose("04_brazos_arriba")
def _():
    for lado, sx in (("Left", 1), ("Right", -1)):
        dirigir(P + lado + "Arm", (0.30 * sx, 0.05, 0.95)); dirigir(P + lado + "ForeArm", (0.15 * sx, -0.05, 0.99))
@pose("05_puno_giro", ((0.05, -0.85, 0.72), (0.0, -0.15, 0.62), 55))
def _():
    brazos_abajo()
    dirigir(P + "LeftArm", (0.45, -0.60, -0.66)); dirigir(P + "LeftForeArm", (0.10, -0.99, 0.10))
    dirigir(P + "RightArm", (-0.45, -0.60, -0.66)); dirigir(P + "RightForeArm", (-0.10, -0.99, 0.10))
    PB["MANO_dedos_R"].rotation_euler = (math.radians(70), 0, 0)
    PB["MANO_dedos_L"].rotation_euler = (math.radians(70), 0, 0)
    girar_local(P + "LeftHand", (0, 1, 0), 80)
@pose("06_mano_ik", ((-0.55, -1.25, 0.80), (-0.05, 0.0, 0.62), 55))
def _():
    brazos_abajo(); ARM.pose.bones["CTRL_raiz"]["ik_brazo_R"] = 1.0
    PB["IK_mano_R"].location = (0, 0, 0)
    bpy.context.view_layer.update()
    # llevar el objetivo delante del pecho (en coordenadas del mundo)
    b = PB["IK_mano_R"]; destino = Vector((-0.06, -0.20, 0.66))
    M_ = b.matrix.copy(); b.matrix = Matrix.Translation(destino) @ M_.to_3x3().to_4x4()
    PB["MANO_dedos_R"].rotation_euler = (math.radians(55), 0, 0)
for nombre, fn, (loc, mira, lente) in POSES:
    limpiar(); fn(); bpy.context.view_layer.update()
    sc.render.resolution_x, sc.render.resolution_y = (1080, 1440) if lente == 50 else (1200, 900)
    camara(loc, mira, lente)
    sc.render.filepath = os.path.join(OUT, f"{nombre}.png"); bpy.ops.render.render(write_still=True)
    print("POSE", nombre, flush=True)
open(os.path.join(OUT, "HECHO.txt"), "w").write("ok"); print("PRUEBA_RIG_OK", flush=True)
