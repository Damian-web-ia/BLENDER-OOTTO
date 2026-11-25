# Portada: Alex señala la rueda trasera y Clod abraza una rueda nueva. Texto «¿DELANTE O DETRÁS?».
# Uso: blender -b ruedas_2026-11-25.blend --python portada_bg.py -- <salida.png>
import bpy, sys, math, bmesh
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1]
R = math.radians
sc = bpy.context.scene
sc.frame_set(1000)
O = bpy.data.objects
def free(n):
    o = O[n]; o.animation_data_clear(); return o
# ocultar textos y placas de los planos
for o in O:
    if o.name.startswith(("TXT_", "PL_")):
        o.animation_data_clear(); o.hide_render = True
# Alex
a = free("ALEX_Raiz"); a.location = (-0.85, -1.75, 0); a.rotation_euler = (0, 0, R(-20))
sh = free("ALEX_Hombro-1"); sh.rotation_euler = (0, R(78), 0)
el = free("ALEX_Codo-1"); el.rotation_euler = (0, R(8), 0)
shr = free("ALEX_Hombro1"); shr.rotation_euler = (0, R(8), 0)
elr = free("ALEX_Codo1"); elr.rotation_euler = (R(-70), 0, R(-25))
h = free("ALEX_Cabeza"); h.rotation_euler = (0, 0, R(18))
free("ALEX_Boca").scale = (1.6, 0.5, 0.7)
# Clod abrazando una rueda nueva
w = free("RUEDA_Suelta"); w.location = (-1.45, -3.05, 0.33); w.rotation_euler = (R(90), 0, R(-25))
free("RUEDA_Suelta_Giro").rotation_euler = (0, 0, 0)
c = free("CLOD_Raiz"); c.location = (-1.9, -3.08, 0.0); c.rotation_euler = (0, 0, R(80))
for s in (-1, 1):
    free(f"CLOD_Hombro{s}").rotation_euler = (R(-95), 0, s * R(-25))
    free(f"CLOD_Cadera{s}").rotation_euler = (0, 0, 0)
    e = free(f"CLOD_Ojo{s}"); e.scale = (1.3, 0.35, 1)  # ojos felices entornados
free("CLOD_Cabeza").rotation_euler = (0, R(-12), 0)
free("CLOD_Boca").scale = (1.2, 0.9, 1)
for n in ("PILA_Gastados", "PILA_Nuevos"):
    free(n).hide_render = True
# cámara de portada
cd = bpy.data.cameras.new("CAM_Portada"); cd.lens = 26; cd.sensor_fit = "VERTICAL"; cd.sensor_height = 24; cd.clip_start = 0.02
cam = bpy.data.objects.new("CAM_Portada", cd); sc.collection.objects.link(cam)
cam.location = (-1.55, -5.7, 0.85)
tgt = Vector((-1.5, -1.5, 0.95))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
for mk in list(sc.timeline_markers):
    sc.timeline_markers.remove(mk)
# texto
D = 0.4; H = D * 12 / 26
fnt = None
for f in bpy.data.fonts:
    if "arial" in f.filepath.lower() or "segoe" in f.filepath.lower():
        fnt = f
def txt(body, matname, y, hf):
    cu = bpy.data.curves.new(body, "FONT"); cu.body = body; cu.size = hf * 2 * H; cu.extrude = cu.size * 0.06
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    if fnt:
        cu.font = fnt
    o = bpy.data.objects.new(body, cu); sc.collection.objects.link(o); cu.materials.append(bpy.data.materials[matname])
    o.parent = cam; o.location = (0, y * H, -D)
txt("¿DELANTE", "TextoBlanco", 0.73, 0.075)
txt("O DETRÁS?", "TextoNaranja", 0.555, 0.085)
me = bpy.data.meshes.new("PL"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5); bm.to_mesh(me); bm.free()
pl = bpy.data.objects.new("PL_Portada", me); sc.collection.objects.link(pl); me.materials.append(bpy.data.materials["PlacaTexto"])
pl.parent = cam; pl.location = (0, 0.64 * H, -D - 0.003); pl.scale = (2 * H * 9 / 16 * 0.94, 0.19 * 2 * H, 1)
r = sc.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 1920, 100
sc.eevee.taa_render_samples = 64
r.image_settings.media_type = "IMAGE"; r.image_settings.file_format = "PNG"
r.filepath = out
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update()
for n in ("CLOD_Raiz", "RUEDA_Suelta", "ALEX_Raiz", "CLOD_Cabeza"):
    print("POS", n, tuple(round(v, 3) for v in world_to_camera_view(sc, cam, O[n].matrix_world.translation)), O[n].hide_render)
bpy.ops.render.render(write_still=True)
open(out + ".done", "w").write("ok")
