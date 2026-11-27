# PRUEBA DE LA CARA DE MAITE: una foto por estado (parpadeos, mirada, expresiones) · EKORUEDAS · 27-11-2026
# Uso: blender -b --factory-startup --python prueba_cara.py -- <carpeta_estudio> <carpeta_salida> <plano: ojos|cara|boca> [muestras]
import bpy, os, sys, math, json
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT, PLANO = argv[0], argv[1], argv[2]; MUESTRAS = int(argv[3]) if len(argv) > 3 else 64
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(PM, "maite_v2.blend"))
sc = bpy.context.scene
ARM = bpy.data.objects["MAITE_rig"]; ME = bpy.data.objects["MAITE_cuerpo"]
ARM.scale = (1.73, 1.73, 1.73); bpy.context.view_layer.update()
KB = ME.data.shape_keys.key_blocks if ME.data.shape_keys else {}
# diagnóstico: MAITE_DIAG=arcilla (todo gris, para ver sólo la forma), sin_cornea, sin_globo
DIAG = os.environ.get("MAITE_DIAG", "")
if "arcilla" in DIAG:
    gris = bpy.data.materials.new("ARCILLA"); gris.use_nodes = True
    bs = gris.node_tree.nodes["Principled BSDF"]; bs.inputs["Base Color"].default_value = (0.55, 0.55, 0.55, 1); bs.inputs["Roughness"].default_value = 0.55
    for i in range(len(ME.data.materials)):
        if ME.data.materials[i] and not any(k in ME.data.materials[i].name for k in ("pestan", "delineado", "dientes")):
            ME.data.materials[i] = gris
for o in bpy.data.objects:
    if ("sin_cornea" in DIAG and "cornea" in o.name.lower()) or ("sin_globo" in DIAG and "globo" in o.name.lower()):
        o.hide_render = True
PB = ARM.pose.bones
# brazos abajo para que no estorben a la luz
for lado, sx in (("Left", 1), ("Right", -1)):
    b = PB[f"mixamorig:{lado}Arm"]; bpy.context.view_layer.update()
    M_ = b.matrix.copy(); y = M_.col[1].xyz.normalized(); q = y.rotation_difference(Vector((0.22 * sx, 0.04, -0.97)))
    b.matrix = Matrix.Translation(M_.translation) @ q.to_matrix().to_4x4() @ M_.to_3x3().to_4x4()
bpy.context.view_layer.update()
mir = PB.get("Mirada"); mir_rest = mir.bone.head_local.copy() if mir else None
def mirar(dx=0.0, dz=0.0):
    if not mir: return
    T = mir_rest + Vector((dx, 0, dz))
    mir.matrix = Matrix.Translation(T) @ mir.bone.matrix_local.to_3x3().to_4x4(); bpy.context.view_layer.update()
# ---- luz de retrato
def luz(n, loc, e, tam, col, mira=(0, 0, 1.5)):
    d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.size = tam; d.color = col; d.shape = 'DISK'
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
luz("Clave", (-0.9, -1.4, 2.0), 160, 1.0, (1.0, 0.90, 0.80))
luz("Relleno", (1.2, -1.2, 1.5), 60, 1.6, (0.70, 0.80, 1.0))
luz("Contra", (0.6, 1.2, 2.0), 140, 0.8, (1.0, 0.8, 0.6), mira=(0, 0, 1.55))
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.022, 0.028, 1)
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
PLANOS = {"ojos": ((0.10, -0.62, 1.535), (0.032, 0, 1.540), 110, (0.032, -0.10, 1.52)),
          "cara": ((0.16, -0.95, 1.50), (0.035, 0, 1.49), 85, (0.035, -0.12, 1.50)),
          "boca": ((0.06, -0.62, 1.45), (0.038, 0, 1.455), 110, (0.038, -0.12, 1.44)),
          "cara3q": ((-0.42, -0.85, 1.52), (0.03, 0, 1.49), 85, (0.0, -0.10, 1.50))}
loc, mira, lente, foco = PLANOS[PLANO]
cam.location = loc; cd.lens = lente; cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
cd.dof.use_dof = True; cd.dof.aperture_fstop = 8; cd.dof.focus_distance = (Vector(foco) - Vector(loc)).length
sc.render.engine = 'CYCLES'; sc.cycles.samples = MUESTRAS; sc.cycles.use_denoising = True
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = 'GPU'
except Exception as e: print("GPU", e)
sc.render.resolution_x, sc.render.resolution_y = 900, 640
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
ESTADOS = (json.loads(open(argv[4], encoding="utf-8").read() if argv[4].endswith(".json") else argv[4])) if len(argv) > 4 else [
    ["neutra", {}, [0, 0]],
    ["parpadeo_medio", {"eyeBlinkLeft": 0.5, "eyeBlinkRight": 0.5}, [0, 0]],
    ["ojos_cerrados", {"eyeBlinkLeft": 1, "eyeBlinkRight": 1}, [0, 0]],
    ["guino", {"eyeBlinkLeft": 1, "eyeSquintRight": 0.4}, [0, 0]],
    ["sorpresa", {"eyeWideLeft": 1, "eyeWideRight": 1}, [0, 0]],
    ["entrecerrados", {"eyeSquintLeft": 1, "eyeSquintRight": 1}, [0, 0]],
    ["mira_arriba", {"eyeLookUpLeft": 1, "eyeLookUpRight": 1}, [0, 0.12]],
    ["mira_abajo", {"eyeLookDownLeft": 1, "eyeLookDownRight": 1}, [0, -0.10]],
    ["mira_su_izquierda", {"eyeLookOutLeft": 1, "eyeLookInRight": 1}, [0.16, 0]],
]
# la mirada de reposo va a la cámara (retrato): con el objetivo a 45 cm los ojos convergen y desde un lado parecen bizcos
if mir and os.environ.get("MAITE_MIRADA", "camara") == "camara":
    bpy.context.view_layer.update()
    mir_rest = ARM.matrix_world.inverted() @ cam.matrix_world.translation
for nombre, claves, (dx, dz) in ESTADOS:
    for k in KB:
        if k.name != "Basis": k.value = 0.0
    for k, v in claves.items():
        if k in KB: KB[k].value = v
    mirar(dx, dz)
    sc.render.filepath = os.path.join(OUT, f"{nombre}.png"); bpy.ops.render.render(write_still=True)
    print("ESTADO", nombre, flush=True)
open(os.path.join(OUT, "HECHO.txt"), "w").write("ok"); print("PRUEBA_CARA_OK", flush=True)
