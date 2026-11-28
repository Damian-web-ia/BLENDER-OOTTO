# HOJA DE REFERENCIA FACIAL DE MAITANE (prompt de la cara, punto 11) · EKORUEDAS · 28-11-2026
# Uso: blender -b --factory-startup --python hoja_cara.py -- <carpeta_estudio> <carpeta_salida> [muestras] [lado_px]
# Saca una imagen por vista (frente, perfiles, tres cuartos, arriba, abajo), primeros planos (ojos, labios, piel, pelo),
# una por expresión de la biblioteca y una por visema. Objetivos de 85-135 mm, AgX, luz de estudio de tres puntos.
import bpy, os, sys, math, json
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = argv[0], argv[1]; MUESTRAS = int(argv[2]) if len(argv) > 2 else 64; LADO = int(argv[3]) if len(argv) > 3 else 900
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.environ.get("MAITE_BLEND") or os.path.join(PM, "maite_v2.blend"))
sc = bpy.context.scene
ARM = bpy.data.objects["MAITE_rig"]; ME = bpy.data.objects["MAITE_cuerpo"]
MA = {}; exec(compile(open(os.path.join(PM, "maite_anim.py"), encoding="utf-8").read(), "maite_anim", "exec"), MA)
KB = ME.data.shape_keys.key_blocks
for ob in bpy.data.objects:
    for md in ob.modifiers:
        if md.type == 'CLOTH': md.show_render = False
bpy.context.view_layer.update()
cab = ARM.matrix_world @ ARM.pose.bones["mixamorig:Head"].head
C = Vector((0.019, -0.040, 0.865))          # centro de la cara (entre ojos y boca), escala del modelo
def luz(n, loc, e, tam, col):
    d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.size = tam; d.color = col
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (C - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
luz("Clave", (-0.9, -1.3, 1.6), 140, 0.9, (1.0, 0.93, 0.86)); luz("Relleno", (1.1, -1.0, 1.0), 55, 1.2, (0.80, 0.86, 1.0))
luz("Contra", (0.5, 1.1, 1.5), 120, 0.8, (1.0, 0.88, 0.75))
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.035, 0.038, 0.045, 1)
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = 'GPU'
except Exception as e: print("GPU", e)
sc.render.engine = 'CYCLES'; sc.cycles.samples = MUESTRAS; sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = LADO; sc.view_settings.view_transform = 'AgX'
def mirar_camara(dx=0.0, dz=0.0):
    b = ARM.pose.bones.get("Mirada")
    if b: b.location = Vector((dx, dz, 0.0))
def claves(d):
    for k in KB[1:]: k.value = 0.0
    for k, v in d.items():
        if k in KB: KB[k].value = v
def foto(nombre, loc, mira, lente):
    cam.location = loc; cd.lens = lente
    cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, nombre + ".png"); bpy.ops.render.render(write_still=True)
    print("FOTO", nombre, flush=True)
d = 0.62
sonrisa = MA["EXPRESIONES"]["sonrisa_natural"]
# --- vistas
claves({k: v * 0.6 for k, v in sonrisa.items()}); mirar_camara()
VISTAS = [("01_frente", (0.019, -0.040 - d, 0.865), 85), ("02_perfil_izquierdo", (0.019 + d, -0.040, 0.865), 85),
          ("03_perfil_derecho", (0.019 - d, -0.040, 0.865), 85), ("04_tres_cuartos_izquierda", (0.019 + d * 0.68, -0.040 - d * 0.73, 0.875), 85),
          ("05_tres_cuartos_derecha", (0.019 - d * 0.68, -0.040 - d * 0.73, 0.875), 85), ("06_arriba", (0.019, -0.040 - d * 0.45, 0.865 + d * 0.88), 85),
          ("07_abajo", (0.019, -0.040 - d * 0.62, 0.865 - d * 0.70), 85)]
for nombre, loc, lente in VISTAS: foto(nombre, loc, C, lente)
claves({}); foto("08_neutra", (0.019, -0.040 - d, 0.865), 85)
# --- primeros planos
claves({k: v * 0.6 for k, v in sonrisa.items()})
foto("09_ojos", (0.021, -0.040 - 0.55, 0.884), 135)
foto("10_labios", (0.021, -0.050 - 0.45, 0.835), 135)
foto("11_piel_mejilla", (0.055 + 0.20, -0.060 - 0.34, 0.86), 135)
foto("12_pelo", (0.15, 0.42, 0.95), 85)
# --- expresiones
EXP = ["neutra", "sonrisa_profesional", "sonrisa_espontanea", "risa_suave", "carcajada", "entusiasmo", "curiosidad", "concentracion",
       "seguridad", "determinacion", "orgullo", "complicidad", "sarcasmo", "ironia", "incredulidad", "confusion", "sorpresa_leve",
       "sorpresa_intensa", "preocupacion", "nerviosismo", "frustracion", "enfado", "impaciencia", "aburrimiento", "cansancio",
       "tristeza", "decepcion", "pensamiento_profundo", "comica", "ceja_izquierda", "guino", "desaprobacion", "sospecha", "explicando"]
for i, e in enumerate(EXP):
    claves(MA["EXPRESIONES"].get(e, {})); foto(f"exp_{i:02d}_{e}", (0.019, -0.040 - d * 0.9, 0.865), 85)
# --- visemas
for i, (v, dv) in enumerate(MA["VISEMAS"].items()):
    claves(dv); foto(f"vis_{i:02d}_{v}", (0.021, -0.050 - 0.50, 0.845), 110)
json.dump({"expresiones": EXP, "visemas": list(MA["VISEMAS"])}, open(os.path.join(OUT, "indice.json"), "w"))
print("HOJA_CARA_OK", flush=True)
