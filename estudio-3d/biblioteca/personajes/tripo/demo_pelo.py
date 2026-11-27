# DEMO DE PELO CON MOVIMIENTO · personaje de Tripo · EKORUEDAS · 27-11-2026
# Uso: blender -b <personaje>_tripo.blend --python demo_pelo.py -- <pelo_dinamico.py> <salida.mp4> <salida.blend> [pieza_pelo]
# Gira la cadera a un lado y a otro, da un saltito y niega con la cabeza: el pelo sigue con inercia y rebota.
import bpy, sys, math, os
from mathutils import Vector, Matrix, Quaternion
argv = sys.argv[sys.argv.index("--") + 1:]
LIB, MP4, BLEND = argv[0], argv[1], argv[2]
PIEZA = argv[3] if len(argv) > 3 else None
exec(open(LIB, encoding="utf-8").read())
sc = bpy.context.scene
arm = [o for o in sc.objects if o.type == 'ARMATURE'][0]
F0, F1 = 1, 150
sc.frame_start, sc.frame_end = F0, F1
sc.render.fps = 30

# ---- pose de partida: brazos abajo (Tripo los entrega en T)
for o in sc.objects: o.select_set(False)
bpy.context.view_layer.objects.active = arm
pb = arm.pose.bones
for nm in pb.keys(): pb[nm].rotation_mode = 'XYZ'
sc.frame_set(F0); bpy.context.view_layer.update()
for lado, sg in (("Left", 1), ("Right", -1)):
    b = pb.get(f"mixamorig:{lado}Arm")
    if not b: continue
    M = b.matrix.copy(); y = M.col[1].xyz.normalized()
    sgx = 1 if y.x >= 0 else -1
    obj = Vector((sgx * 0.33, 0.06, -0.94)).normalized()
    q = y.rotation_difference(obj)
    b.matrix = Matrix.Translation(M.translation) @ q.to_matrix().to_4x4() @ M.to_3x3().to_4x4()
    bpy.context.view_layer.update()
    for f in (F0, F1): b.keyframe_insert("rotation_euler", frame=f)
    fa = pb.get(f"mixamorig:{lado}ForeArm")
    if fa:
        fa.rotation_euler = (0, 0, 0)
        for f in (F0, F1): fa.keyframe_insert("rotation_euler", frame=f)

def claves(b, prop, idx, pares):
    for f, v in pares:
        getattr(b, prop)[idx] = v; b.keyframe_insert(prop, index=idx, frame=f)

H, CAB, SP = pb["mixamorig:Hips"], pb["mixamorig:Head"], pb.get("mixamorig:Spine1")
r = math.radians
claves(H, "rotation_euler", 1, [(1, 0), (22, r(32)), (46, r(-32)), (68, r(22)), (88, 0), (150, 0)])
if SP: claves(SP, "rotation_euler", 1, [(1, 0), (24, r(10)), (48, r(-10)), (70, r(6)), (90, 0), (150, 0)])
claves(H, "location", 1, [(1, 0), (96, 0), (103, -0.035), (111, 0.075), (118, 0), (122, -0.018), (127, 0), (150, 0)])
claves(CAB, "rotation_euler", 1, [(1, 0), (120, 0), (126, r(24)), (132, r(-24)), (138, r(16)), (144, r(-6)), (150, 0)])
claves(CAB, "rotation_euler", 0, [(1, 0), (100, 0), (108, r(-10)), (116, r(8)), (124, 0), (150, 0)])
for fc in (arm.animation_data.action.fcurves if hasattr(arm.animation_data.action, "fcurves") else []):
    for k in fc.keyframe_points: k.interpolation = 'BEZIER'

# ---- pelo
pelo = bpy.data.objects.get(PIEZA) if PIEZA else None
cads = preparar_pelo(arm, pelo, n=3, mechones=3)
print("CADENAS", cads)
if cads: hornear_pelo(arm, cads, F0, F1)

# ---- estudio: suelo, luces, cámara
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0)); suelo = bpy.context.object
ms = bpy.data.materials.new("Suelo"); ms.use_nodes = True; bs = ms.node_tree.nodes["Principled BSDF"]
bs.inputs["Base Color"].default_value = (0.05, 0.055, 0.06, 1); bs.inputs["Roughness"].default_value = 0.35
suelo.data.materials.append(ms)
w = sc.world or bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.035, 0.04, 0.05, 1)
def luz(nombre, loc, energia, tam, color=(1, 1, 1)):
    d = bpy.data.lights.new(nombre, 'AREA'); d.energy = energia; d.size = tam; d.color = color
    o = bpy.data.objects.new(nombre, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0.55)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
luz("Clave", (-1.6, -1.8, 2.2), 260, 1.6, (1.0, 0.96, 0.9))
luz("Relleno", (1.8, -1.4, 1.2), 70, 2.0, (0.85, 0.92, 1.0))
luz("Contra", (0.4, 2.0, 1.8), 320, 1.0, (0.7, 0.85, 1.0))
cd = bpy.data.cameras.new("Cam"); cd.lens = 50; cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
for f, ang in ((F0, -18), (F1, 14)):
    a = math.radians(ang); cam.location = (2.05 * math.sin(a), -2.05 * math.cos(a), 0.62)
    cam.rotation_euler = (Vector((0, 0, 0.50)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)

r_ = sc.render
r_.engine = 'BLENDER_EEVEE'
try: sc.eevee.taa_render_samples = 32
except Exception: pass
r_.resolution_x, r_.resolution_y, r_.resolution_percentage = 720, 1280, 100
try: sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
r_.image_settings.media_type = 'VIDEO'; r_.image_settings.file_format = 'FFMPEG'
r_.ffmpeg.format = 'MPEG4'; r_.ffmpeg.codec = 'H264'; r_.ffmpeg.constant_rate_factor = 'HIGH'; r_.ffmpeg.audio_codec = 'NONE'
r_.filepath = MP4
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.render.render(animation=True)
open(MP4 + ".done", "w").write("ok")
print("DEMO_OK")
