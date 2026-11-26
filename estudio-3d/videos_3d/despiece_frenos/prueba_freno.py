# Prueba del modelo del freno: escena vacía, estudio oscuro, 3 fotos (general, pinza con rayos X, canales abiertos).
import bpy, math
from mathutils import Vector, Euler
BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
bpy.ops.wm.read_homefile(use_empty=True)
sc = bpy.context.scene
for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try: sc.render.engine = eng; break
    except Exception: pass
try: sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
FR = {"__name__": "fr"}; exec(open(BASE + r"\biblioteca\freno_real.py", encoding="utf-8").read(), FR)
O = FR["construir_freno"](sc.collection)
O["raiz"].rotation_euler = (math.radians(90), math.radians(-35), math.radians(-25)); O["raiz"].location = (0, 0, 0.3)
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.022, 0.026, 1)
def luz(n, tipo, loc, e, size=0.6, color=(1, 1, 1)):
    o = bpy.data.objects.new(n, bpy.data.lights.new(n, tipo)); sc.collection.objects.link(o); o.location = loc; o.data.energy = e; o.data.color = color
    if tipo == 'AREA': o.data.size = size
    o.rotation_euler = (Vector((0, 0, 0.3)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o
luz("K", 'AREA', (0.6, -0.9, 1.0), 90, 0.8); luz("R", 'AREA', (-0.7, 0.6, 0.7), 60, 0.8, (0.6, 0.75, 1)); luz("F", 'AREA', (-0.6, -0.8, 0.2), 15, 0.8)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 40
try: sc.eevee.taa_render_samples = 24
except Exception: pass
M = O["raiz"].matrix_world
def foto(nombre, pos, mira, lens, ajustes):
    for k, v in ajustes.items(): sc[k] = v
    sc.view_layers[0].update()
    p = Vector(pos); t = Vector(mira)
    cam.location = p; cam.rotation_euler = (t - p).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
    sc.render.filepath = OUT + "\\" + nombre + ".png"; bpy.ops.render.render(write_still=True)
bpy.context.view_layer.update(); M = O["raiz"].matrix_world
sc["xray_pinza"] = 0.0; sc["calor"] = 0.0; sc["flujo_luz"] = 0.0; sc["aire"] = 0.0
foto("a_general", M @ Vector((0.20, -0.75, 0.55)), M @ Vector((0.05, 0, 0)), 40, {})
foto("b_pinza", M @ Vector((0.40, -0.10, -0.30)), M @ Vector((0.13, 0, -0.05)), 45, {"flujo_luz": 1.0})
foto("c_calor", M @ Vector((0.12, -0.30, 0.50)), M @ Vector((0.05, 0, 0)), 40, {"calor": 1.0, "flujo_luz": 0.0})
O["disco_ext"].location = (0, 0, 0.05); O["pinza"].location = (0.12, 0, 0); O["pad_int"].location = (0, 0, -0.05); O["pad_ext"].location = (0, 0, 0.10)
foto("d_canales", M @ Vector((0.33, -0.25, 0.05)), M @ Vector((0.13, 0, 0.0)), 55, {"calor": 0.4, "aire": 1.0})
result = {"ok": True}
