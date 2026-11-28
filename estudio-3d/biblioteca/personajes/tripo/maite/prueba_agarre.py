# PRUEBA RÁPIDA DEL AGARRE (llave de cruz en la mano derecha) · EKORUEDAS · 28-11-2026
# Uso: blender -b --factory-startup --python prueba_agarre.py -- <carpeta_estudio> <carpeta_salida> [archivo.blend]
import bpy, os, sys
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = argv[0], argv[1]; PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite")
BLEND = argv[2] if len(argv) > 2 else os.path.join(PM, "maite_v2.blend"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene; ARM = bpy.data.objects["MAITE_rig"]
MA = {}; exec(compile(open(os.path.join(PM, "maite_anim.py"), encoding="utf-8").read(), "maite_anim", "exec"), MA)
UT = {}; exec(compile(open(os.path.join(PM, "utileria_maite.py"), encoding="utf-8").read(), "utileria", "exec"), UT)
A = MA["MaiteAnim"](ARM)
A.pose_reposo(1); A.brazo(1, "R", "agarra"); A.mano(1, "R", "empuna"); sc.frame_set(1)
llave = UT["llave_cruz"](); UT["agarrar"](ARM, llave, "R")
A.mano(20, "R", "empuna", muneca=(0, 45, 0)); A.brazo(40, "R", "presenta"); A.mano(40, "R", "empuna")
for ob in bpy.data.objects:
    for md in ob.modifiers:
        if md.type == 'CLOTH': md.show_render = False
d = bpy.data.lights.new("Clave", 'AREA'); d.energy = 300; d.size = 1.5
o = bpy.data.objects.new("Clave", d); sc.collection.objects.link(o); o.location = (-1.2, -1.8, 1.8)
o.rotation_euler = (Vector((0.1, 0, 0.7)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.12, 0.13, 0.15, 1)
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = 'GPU'
except Exception as e: print("GPU", e)
sc.render.engine = 'CYCLES'; sc.cycles.samples = 24; sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = 720; sc.view_settings.view_transform = 'AgX'
for nombre, loc, mira, lente in (("frente", (0.30, -1.10, 0.80), (-0.10, -0.05, 0.62), 55), ("cerca", (-0.05, -0.62, 0.70), (-0.14, -0.12, 0.60), 70)):
    cam.location = loc; cd.lens = lente; cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    for f in (1, 20, 40):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f"{nombre}_{f:02d}.png"); bpy.ops.render.render(write_still=True)
print("AGARRE_OK", flush=True)
