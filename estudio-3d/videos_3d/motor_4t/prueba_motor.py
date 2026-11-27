# Prueba rápida del modelo del motor (sin personajes): construye, pone el cigüeñal a varios ángulos y renderiza.
# Uso: blender -b --factory-startup --python prueba_motor.py -- <carpeta_biblioteca> <carpeta_salida> [angulos]
import bpy, sys, os, math, time
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
LIB, OUT = argv[0], argv[1]
ANG = [float(a) for a in argv[2].split(",")] if len(argv) > 2 else [90.0]
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
MP = {"__name__": "mp"}; exec(open(os.path.join(LIB, "materiales_pro.py"), encoding="utf-8").read(), MP)
BUJ = {"__name__": "buj"}; exec(open(os.path.join(LIB, "bujia_real.py"), encoding="utf-8").read(), BUJ)
G = {"__name__": "mot"}; exec(open(os.path.join(LIB, "motor_4t_real.py"), encoding="utf-8").read(), G)
sc = bpy.context.scene
for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
col = bpy.data.collections.new("MOTOR"); sc.collection.children.link(col)
O = G["construir_motor"](col, MP, BUJ)
print("CONSTRUIDO", round(time.time() - t0, 1), "s", len(col.objects), "objetos")
for d in O["delante"]: d.hide_render = True
# estudio mínimo
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.025, 0.035, 1)
def luz(n, loc, e, s, c):
    d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.size = s; d.color = c
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0.12)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
luz("K", (-0.6, -0.9, 0.8), 120, 0.6, (1, 0.93, 0.85)); luz("R", (0.7, 0.6, 0.5), 160, 0.5, (0.6, 0.8, 1.0)); luz("F", (0.8, -0.8, 0.2), 40, 0.8, (0.8, 0.9, 1))
cd = bpy.data.cameras.new("C"); cd.lens = 50; cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
r = sc.render; r.engine = 'CYCLES'; sc.cycles.device = 'GPU'; sc.cycles.samples = 24; sc.cycles.use_denoising = True
cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
for dv in cp.devices: dv.use = dv.type == "OPTIX"
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 1920, 50
try: sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
vistas = {"frente": ((0.0, -0.95, 0.13), (0, 0, 0.12)), "tres_cuartos": ((-0.55, -0.70, 0.40), (0, 0, 0.12)), "camara": ((0.0, -0.30, 0.22), (0, 0, 0.21))}
for a in ANG:
    G["poner_angulo"](O, a, 1, clave=False)
    for nm, (loc, mira) in vistas.items():
        cam.location = loc; cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        r.filepath = os.path.join(OUT, f"motor_{nm}_{int(a):03d}.png"); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "prueba_motor.blend"))
print("PRUEBA_MOTOR_OK", round(time.time() - t0, 1))
