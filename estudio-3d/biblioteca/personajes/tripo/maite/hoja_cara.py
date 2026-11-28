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
A = MA["MaiteAnim"](ARM); sc.frame_set(1); A.pose_reposo(1); sc.frame_set(1)
bpy.context.view_layer.update()
# centro y tamaño de la cabeza (vértices con peso de la cabeza, con la postura aplicada), para encuadrar las vistas
dg = bpy.context.evaluated_depsgraph_get(); ev = ME.evaluated_get(dg); mev = ev.to_mesh()
gi = ME.vertex_groups["mixamorig:Head"].index
pts = [ME.matrix_world @ mev.vertices[v.index].co for v in ME.data.vertices
       if any(g.group == gi and g.weight > 0.6 for g in v.groups)]
ev.to_mesh_clear()
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
H = (mn + mx) / 2; ALTO = mx.z - mn.z
C = Vector((H.x, mn.y, H.z - ALTO * 0.08))  # centro de la cara (por delante)
OJ = [ARM.matrix_world @ ARM.pose.bones[n].head for n in ("Ojo_L", "Ojo_R") if n in ARM.pose.bones]
E = sum(OJ, Vector()) / len(OJ) if OJ else Vector((H.x, mn.y + 0.03, H.z))
H.x = E.x                                        # la trenza cae a un lado: el centro de la caja no es el de la cara
if "boca" in ARM:                                # centro de la boca en reposo -> con la postura de la cabeza
    pbh_ = ARM.pose.bones["mixamorig:Head"]
    Mh_ = ARM.matrix_world @ pbh_.matrix @ pbh_.bone.matrix_local.inverted() @ ARM.matrix_world.inverted()
    B = Mh_ @ (ME.matrix_world @ Vector(eval(ARM["boca"])))
else: B = Vector((E.x, E.y, E.z - 0.040))
print("OJOS", tuple(round(v, 4) for v in E), "BOCA", tuple(round(v, 4) for v in B), flush=True)
print("CABEZA", tuple(round(v, 4) for v in H), "alto", round(ALTO, 4), "frente_y", round(mn.y, 4), flush=True)
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
def foto(nombre, loc, lente, mira=None):
    ruta = os.path.join(OUT, nombre + ".png")
    if os.path.exists(ruta) and os.environ.get("HOJA_REPETIR") != "1": print("YA", nombre); return
    mira = C if mira is None else mira
    cam.location = loc; cd.lens = lente
    cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, nombre + ".png"); bpy.ops.render.render(write_still=True)
    print("FOTO", nombre, flush=True)
import math as _m
d = 1.55 * ALTO * 85 / 36                       # distancia para que la cabeza ocupe ~2/3 del cuadro con 85 mm
def orbita(az, el, dist=None):
    """az: 0 = de frente, 90 = su izquierda; el: elevación en grados."""
    r = dist or d; a, e = _m.radians(az), _m.radians(el)
    return (H.x + r * _m.cos(e) * _m.sin(a), H.y - r * _m.cos(e) * _m.cos(a), H.z + r * _m.sin(e))
sonrisa = MA["EXPRESIONES"]["sonrisa_natural"]
claves({k: v * 0.6 for k, v in sonrisa.items()}); mirar_camara()
VISTAS = [("01_frente", 0, 0), ("02_perfil_izquierdo", 90, 0), ("03_perfil_derecho", -90, 0),
          ("04_tres_cuartos_izquierda", 42, 4), ("05_tres_cuartos_derecha", -42, 4),
          ("06_arriba", 0, 42), ("07_abajo", 0, -28)]
for nombre, az, el in VISTAS: foto(nombre, orbita(az, el), 85, H)
claves({}); foto("08_neutra", orbita(0, 0), 85, H)
# --- primeros planos
claves({k: v * 0.6 for k, v in sonrisa.items()})
foto("09_ojos", (E.x, E.y - 0.30, E.z), 135, E)
foto("10_labios", (B.x, B.y - 0.17, B.z), 135, B)
foto("11_piel_mejilla", (E.x + 0.14, E.y - 0.21, E.z - 0.016), 135, (E.x + 0.030, E.y, E.z - 0.020))
foto("12_pelo", orbita(160, 18), 85, H)
# --- expresiones
EXP = ["neutra", "sonrisa_profesional", "sonrisa_espontanea", "risa_suave", "carcajada", "entusiasmo", "curiosidad", "concentracion",
       "seguridad", "determinacion", "orgullo", "complicidad", "sarcasmo", "ironia", "incredulidad", "confusion", "sorpresa_leve",
       "sorpresa_intensa", "preocupacion", "nerviosismo", "frustracion", "enfado", "impaciencia", "aburrimiento", "cansancio",
       "tristeza", "decepcion", "pensamiento_profundo", "comica", "ceja_izquierda", "guino", "desaprobacion", "sospecha", "explicando"]
for i, e in enumerate(EXP):
    claves(MA["EXPRESIONES"].get(e, {})); foto(f"exp_{i:02d}_{e}", orbita(0, 0, d * 0.92), 85, H)
# --- visemas
for i, (v, dv) in enumerate(MA["VISEMAS"].items()):
    claves(dv); foto(f"vis_{i:02d}_{v}", (B.x, B.y - 0.50, B.z), 110, B)
json.dump({"expresiones": EXP, "visemas": list(MA["VISEMAS"])}, open(os.path.join(OUT, "indice.json"), "w"))
print("HOJA_CARA_OK", flush=True)
