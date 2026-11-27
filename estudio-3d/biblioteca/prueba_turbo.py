# Prueba del turbocompresor (27-11-2026): construye turbo_real.py en un estudio oscuro y saca 5 fotos verticales con Cycles:
#   cerrado.png (3/4, todo montado), corte.png (corte seccional), rueda.png (macro de la rueda del compresor),
#   al_rojo.png (corte con la carcasa de la turbina al rojo) y despiece.png (piezas separadas a lo largo del eje).
# Uso: blender -b --factory-startup --python prueba_turbo.py -- <EKORUEDAS_ESTUDIO_3D> <carpeta_salida> [muestras] [guardar.blend]
import bpy, os, sys, math
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = args[0], args[1]; MUESTRAS = int(args[2]) if len(args) > 2 else 96
GUARDA = args[3] if len(args) > 3 else None
os.makedirs(OUT, exist_ok=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
col = bpy.data.collections.new("TURBO"); sc.collection.children.link(col)
G = {"__name__": "turbo"}; exec(open(os.path.join(EST, "biblioteca", "turbo_real.py"), encoding="utf-8").read(), G)
O = G["construir_turbo"](col)
RAIZ = O["raiz"]; RAIZ.location = (0, 0, 0.20)
print("TURBO_OK", len(col.objects), "objetos")
if GUARDA: bpy.ops.wm.save_as_mainfile(filepath=GUARDA)

# ---------------- estudio oscuro
w = bpy.data.worlds.new("Mundo"); sc.world = w
try: w.use_nodes = True
except Exception: pass
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.0045, 0.006, 1)
def mat(n, c, r=0.4, m=0.0, e=0.0, ec=None):
    x = bpy.data.materials.new(n); x.use_nodes = True; b = x.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r; b.inputs["Metallic"].default_value = m
    if e: b.inputs["Emission Color"].default_value = (*(ec or c), 1); b.inputs["Emission Strength"].default_value = e
    return x
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0)); bpy.context.object.data.materials.append(mat("Suelo", (0.016, 0.017, 0.02), 0.26, 0.2))
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 1.4, 2.0), rotation=(math.radians(90), 0, 0)); bpy.context.object.data.materials.append(mat("Fondo", (0.010, 0.011, 0.014), 0.6))
for k, x in enumerate((-0.7, -0.25, 0.3, 0.8)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 1.35, 1.2)); t = bpy.context.object; t.scale = (0.006, 0.006, 1.2)
    t.data.materials.append(mat("Linea%d" % k, (0.2, 0.4, 0.9), 0.5, 0, 1.6, (0.18, 0.42, 1.0)))
def luz(n, pos, e, col_=(1, 1, 1), tam=0.5, mira=(0, 0, 0.2)):
    d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.color = col_; d.size = tam
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = pos
    o.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler(); return o
luz("Clave", (-0.55, -0.6, 0.75), 30, (1.0, 0.96, 0.92), 0.5)
luz("Relleno", (0.7, -0.5, 0.30), 6, (0.85, 0.9, 1.0), 0.7)
luz("ContraIzq", (-0.5, 0.6, 0.45), 40, (0.55, 0.72, 1.0), 0.3)
luz("ContraDer", (0.55, 0.55, 0.40), 36, (0.55, 0.72, 1.0), 0.3)
luz("Arriba", (0, 0.05, 1.0), 10, (1, 1, 1), 0.8)
luz("Calida", (0.45, -0.25, 0.05), 5, (1.0, 0.6, 0.3), 0.3)

r = sc.render; r.engine = 'CYCLES'; r.resolution_x = 1080; r.resolution_y = 1920; r.resolution_percentage = 100
cy = sc.cycles; cy.samples = MUESTRAS; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.01; cy.use_denoising = True
try: cy.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    for t in ("OPTIX", "CUDA"):
        try:
            pr.compute_device_type = t; pr.get_devices()
            for d in pr.devices: d.use = (d.type != 'CPU')
            cy.device = 'GPU'; break
        except Exception: continue
except Exception: pass
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.dof.use_dof = True
def foto(nombre, pos, mira, lente, fstop=5.6, foco=None):
    cam.location = pos; cam.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    cam_d.lens = lente; cam_d.dof.focus_distance = (Vector(foco or mira) - Vector(pos)).length; cam_d.dof.aperture_fstop = fstop
    r.filepath = os.path.join(OUT, nombre); bpy.ops.render.render(write_still=True); print("FOTO", nombre)
def ver(objs, v):
    for o in objs: o.hide_render = not v

C = Vector((0, 0, 0.20))
foto("cerrado.png", (-0.38, -0.62, 0.42), C + Vector((0.0, 0, 0.01)), 55, fstop=8)
ver(O["delante"], False)
foto("corte.png", (0.05, -0.60, 0.30), C + Vector((-0.005, 0, 0.0)), 55, fstop=8)
foto("rueda.png", (0.20, -0.20, 0.26), C + Vector((0.045, 0, 0.005)), 85, fstop=4, foco=C + Vector((0.050, -0.012, 0.004)))
G["calor"](O, 1, 1.0); sc.frame_set(1)
foto("al_rojo.png", (-0.20, -0.42, 0.28), C + Vector((-0.045, 0, 0.0)), 60, fstop=5.6)
G["calor"](O, 1, 0.0); sc.frame_set(1)
ver(O["delante"], True)
# despiece a lo largo del eje
def grupo(o):
    n = o.name
    if any(k in n for k in ("CarcasaCompresor", "CaracolaCompresor", "ContraplacaCompresor", "LabioEntrada")): return (0.125, 0, 0)
    if "TuercaRueda" in n: return (0.110, 0, 0)
    if "RuedaCompresor" in n: return (0.075, 0, 0)
    if "CollarAxial" in n: return (0.050, 0, 0)
    if "CojineteAxial" in n: return (0.040, 0, 0)
    if "Casquillo1" in n: return (0.020, 0, 0)
    if "Casquillo0" in n: return (-0.030, 0, 0)
    if n.startswith("TUR_Eje") or "RuedaTurbina" in n: return (-0.070, 0, 0)
    if "EscudoTermico" in n: return (-0.095, 0, 0)
    if any(k in n for k in ("CarcasaTurbina", "CaracolaTurbina", "BridaSalida", "BridaEntrada", "Esparrago", "TapaWastegate", "PalancaWastegate")): return (-0.150, 0, 0)
    if any(k in n for k in ("Actuador", "SoporteActuador", "Varilla", "ManguitoPresion")): return (0.04, 0, 0.07)
    return (0, 0, 0)
for o in col.objects:
    if o.type == 'MESH': o.location = o.location + Vector(grupo(o))
RAIZ.rotation_euler = (0, math.radians(-90), 0); RAIZ.location = (0, 0, 0.33)      # eje en vertical: compresor arriba, turbina abajo
foto("despiece.png", (0.0, -1.10, 0.36), (0, 0, 0.31), 50, fstop=11)
print("PRUEBA_OK")
