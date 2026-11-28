# PRUEBA DE TELA: Maite sube los brazos, los baja hacia delante y saluda; se hornea la tela de las mangas y se
# renderizan fotogramas clave (y, si se pide, un vídeo corto) · EKORUEDAS · 28-11-2026
# Uso: blender -b --factory-startup --python prueba_tela.py -- <carpeta_estudio> <carpeta_salida> [muestras] [video 0/1]
import bpy, os, sys, math
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = argv[0], argv[1]; MUESTRAS = int(argv[2]) if len(argv) > 2 else 32; VIDEO = len(argv) > 3 and argv[3] == "1"
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(PM, "maite_v2.blend"))
sc = bpy.context.scene; sc.render.fps = 24; sc.frame_start = 1; sc.frame_end = 72
ARM = bpy.data.objects["MAITE_rig"]; PB = ARM.pose.bones; P = "mixamorig:"
def luz(n, loc, e, tam, col, mira=(0, 0, 0.7)):
    d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.size = tam; d.color = col
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
luz("Clave", (-1.4, -2.0, 2.2), 380, 1.4, (1.0, 0.92, 0.84)); luz("Relleno", (1.8, -1.6, 1.3), 140, 1.8, (0.75, 0.82, 1.0))
luz("Contra", (0.6, 1.8, 2.0), 260, 1.0, (1.0, 0.85, 0.7), mira=(0, 0, 0.9))
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.035, 0.038, 0.045, 1)
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0.55, -1.30, 0.95); cd.lens = 50
cam.rotation_euler = (Vector((0.0, 0.0, 0.76)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = 'GPU'
except Exception as e: print("GPU", e)
sc.render.engine = 'CYCLES'; sc.cycles.samples = MUESTRAS; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1350
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
for b in PB:
    if b.name.startswith(P): b.rotation_mode = 'QUATERNION'
def dirigir(nombre, d):
    b = PB[nombre]; bpy.context.view_layer.update()
    M_ = b.matrix.copy(); y = M_.col[1].xyz.normalized(); q = y.rotation_difference(Vector(d).normalized())
    b.matrix = Matrix.Translation(M_.translation) @ q.to_matrix().to_4x4() @ M_.to_3x3().to_4x4(); bpy.context.view_layer.update()
def clave(f, poses):
    sc.frame_set(f)
    for b in PB:
        if b.name.startswith(P): b.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.view_layer.update()
    for nombre, d in poses: dirigir(nombre, d)
    for nombre, _ in poses: PB[nombre].keyframe_insert("rotation_quaternion", frame=f)
abajo = [(P + "LeftArm", (0.22, 0.04, -0.97)), (P + "LeftForeArm", (0.12, -0.22, -0.97)),
         (P + "RightArm", (-0.22, 0.04, -0.97)), (P + "RightForeArm", (-0.12, -0.22, -0.97))]
arriba = [(P + "LeftArm", (0.35, 0.0, 0.94)), (P + "LeftForeArm", (0.10, -0.05, 0.99)),
          (P + "RightArm", (-0.35, 0.0, 0.94)), (P + "RightForeArm", (-0.10, -0.05, 0.99))]
delante = [(P + "LeftArm", (0.40, -0.70, -0.59)), (P + "LeftForeArm", (0.15, -0.95, 0.25)),
           (P + "RightArm", (-0.85, 0.05, 0.25)), (P + "RightForeArm", (-0.15, 0.05, 0.99))]
saludo = [(P + "LeftArm", (0.40, -0.70, -0.59)), (P + "LeftForeArm", (0.15, -0.95, 0.25)),
          (P + "RightArm", (-0.85, 0.05, 0.25)), (P + "RightForeArm", (-0.55, 0.0, 0.83))]
clave(1, abajo); clave(8, abajo); clave(22, arriba); clave(32, arriba); clave(46, delante); clave(54, saludo); clave(62, delante); clave(72, saludo)
# hornear la tela
sc.frame_set(1)
for ob in bpy.data.objects:
    for md in ob.modifiers:
        if md.type == 'CLOTH': md.point_cache.frame_start = 1; md.point_cache.frame_end = 72
with bpy.context.temp_override(scene=sc):
    bpy.ops.ptcache.bake_all(bake=True)
print("TELA_HORNEADA", flush=True)
if VIDEO:
    if hasattr(sc.render.image_settings, 'media_type'): sc.render.image_settings.media_type = 'VIDEO'
    sc.render.image_settings.file_format = 'FFMPEG'; sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'
    sc.render.ffmpeg.constant_rate_factor = 'HIGH'; sc.render.ffmpeg.ffmpeg_preset = 'REALTIME'
    sc.render.resolution_x, sc.render.resolution_y = 720, 900
    sc.render.filepath = os.path.join(OUT, "tela.mp4"); bpy.ops.render.render(animation=True)
else:
    for f in (8, 22, 32, 46, 54, 72):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f"f{f:03d}.png"); bpy.ops.render.render(write_still=True)
        print("FOTOGRAMA", f, flush=True)
open(os.path.join(OUT, "HECHO.txt"), "w").write("ok"); print("PRUEBA_TELA_OK", flush=True)
