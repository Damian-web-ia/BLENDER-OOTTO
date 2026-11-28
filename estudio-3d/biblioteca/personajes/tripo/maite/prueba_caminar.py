# PRUEBA RÁPIDA DEL PASEO DE MAITE (pies IK plantados) · EKORUEDAS · 28-11-2026
# Uso: blender -b --factory-startup --python prueba_caminar.py -- <carpeta_estudio> <carpeta_salida> [muestras]
# Saca fotogramas sueltos de lado y de frente (sin tela, para ir rápido) y deja una hoja de contactos.
import bpy, os, sys, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = argv[0], argv[1]; MUESTRAS = int(argv[2]) if len(argv) > 2 else 16
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(PM, "maite_v2.blend"))
sc = bpy.context.scene; sc.render.fps = 24
ARM = bpy.data.objects["MAITE_rig"]
MA = {}; exec(compile(open(os.path.join(PM, "maite_anim.py"), encoding="utf-8").read(), "maite_anim", "exec"), MA)
A = MA["MaiteAnim"](ARM)
A.pose_reposo(1); A.mano(1, "L", "relajada"); A.mano(1, "R", "relajada")
fin = A.caminar(1, pasos=6, zancada=0.30, frames_paso=14, inicio=(0.0, 0.9, 0.0))
A.pose_reposo(fin + 12)
A.respirar(1, fin + 12); A.finalizar(1, fin + 12, trenza=True)
for ob in bpy.data.objects:
    for md in ob.modifiers:
        if md.type == 'CLOTH': md.show_render = False; md.show_viewport = False
def luz(n, loc, e, tam):
    d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.size = tam
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, -0.9, 0.6)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
luz("Clave", (-1.6, -2.5, 2.4), 450, 2.0); luz("Relleno", (2.0, -1.0, 1.4), 160, 2.0)
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.055, 0.065, 1)
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, -1.0, 0)); suelo = bpy.context.active_object
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = 'GPU'
except Exception as e: print("GPU", e)
sc.render.engine = 'CYCLES'; sc.cycles.samples = MUESTRAS; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 640, 640
sc.view_settings.view_transform = 'AgX'
for nombre, loc, mira in (("lado", (2.6, -0.9, 0.55), (0, -0.9, 0.45)), ("frente", (0.4, -3.6, 0.7), (0, -0.9, 0.45))):
    cam.location = loc; cd.lens = 40
    cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    for f in range(1, fin + 13, 7 if nombre == "lado" else 14):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f"{nombre}_{f:03d}.png")
        bpy.ops.render.render(write_still=True)
print("CAMINAR_OK", fin, flush=True)
