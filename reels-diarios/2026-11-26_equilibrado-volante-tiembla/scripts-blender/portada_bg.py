# PORTADA 26-11-2026 · blender -b escena\equilibrado.blend --python portada_bg.py -- <salida.png>
# Fotograma 645 (Alex hace "¡para!" con la mano y Clod pone cara de susto). Para la portada, Clod se quita su
# movimiento de objeto y se sube encima de la rueda de la equilibradora (como si quisiera hacer de contrapeso).
# El texto "¿TE TIEMBLA EL VOLANTE?" (TIEMBLA en #FF8400, placa oscura arriba) se pone después con PIL (Ootto).
import bpy, sys, math
from mathutils import Vector
OUT = sys.argv[sys.argv.index("--") + 1]
sc = bpy.context.scene
C = bpy.data.objects["CLOD_v2"]; ad = C.animation_data
def quitar(idb, rutas):
    ad = idb.animation_data
    try: pares = [(fc, ad.action.fcurves) for fc in ad.action.fcurves]
    except Exception: pares = [(fc, cb.fcurves) for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
    for fc, col in pares:
        if fc.data_path in rutas: col.remove(fc)
quitar(C, ("location", "rotation_euler"))
W = Vector((0.784, -0.151, 0.82)); R_EXT = 0.316
C.location = (W.x + 0.02, W.y - 0.02, W.z + R_EXT - 0.012); C.rotation_euler = (0, 0, math.radians(-25))
cam = bpy.data.objects.new("CAM_PORTADA", bpy.data.cameras.new("CAM_PORTADA")); sc.collection.objects.link(cam)
loc = Vector((0.42, -2.62, 1.30)); t = Vector((0.40, -0.35, 1.33))
cam.location = loc; cam.rotation_euler = (t - loc).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 26; cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24
sc.camera = cam; sc.frame_set(645)
from bpy_extras.object_utils import world_to_camera_view as w2c
A = bpy.data.objects["ALEX_v2"]
for n, p in (("Alex", A.matrix_world @ A.pose.bones["mixamorig:Head"].tail), ("Clod", bpy.data.objects["CLOD_Diadema"].matrix_world.translation)):
    c = w2c(sc, cam, p); assert 0.02 < c.x < 0.98 and 0.02 < c.y < 0.98, (n, c)
r = sc.render; r.resolution_percentage = 100; sc.eevee.taa_render_samples = 64; r.use_motion_blur = False
r.image_settings.media_type = 'IMAGE'; r.image_settings.file_format = 'PNG'; r.filepath = OUT
bpy.ops.render.render(write_still=True)
