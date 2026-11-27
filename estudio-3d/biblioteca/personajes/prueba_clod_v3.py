# Prueba de Clod v3 (27-11-2026): construye Clod v3 y, al lado, el Clod v2 para comparar (antes / después),
# en un estudio oscuro como el de los vídeos 4K, y saca 4 fotos con Cycles:
#   comparacion.png (v2 | v3), cara.png (primer plano de la pantalla), espalda.png (3/4 trasero), saludo.png (v3 saludando).
# Uso: blender -b --factory-startup --python prueba_clod_v3.py -- <EKORUEDAS_ESTUDIO_3D> <carpeta_salida> [muestras]
import bpy, os, sys, math
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = args[0], args[1]; MUESTRAS = int(args[2]) if len(args) > 2 else 96
PER = os.path.join(EST, "biblioteca", "personajes"); os.makedirs(OUT, exist_ok=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene

# ---------------- Clod v3 (construido aquí mismo)
G = {"__name__": "clod_v3"}; exec(open(os.path.join(PER, "clod_v3.py"), encoding="utf-8").read(), G)
arm3 = G["construir_clod"]((0.13, 0, 0))
CA = {"__name__": "clod_anim"}; exec(open(os.path.join(PER, "clod_anim.py"), encoding="utf-8").read(), CA)
CL = CA["ClodAnim"]("CLOD_v3")
CL.reposo(1); CL.mover(1, (0.13, 0, 0), 0); CL.cara(1, "feliz")
F_SAL = CL.saludo("R", 2)
CL.parpadeos(1, F_SAL + 20) if hasattr(CL, "parpadeos") else None

# ---------------- Clod v2 al lado (solo para comparar)
v2 = os.path.join(PER, "clod", "clod_v2.blend")
if os.path.exists(v2):
    with bpy.data.libraries.load(v2, link=False) as (src, dst):
        dst.collections = [n for n in src.collections if n in ("CLOD_v2_personaje", "CLOD_v2_controles")]
    for c in dst.collections:
        if c is not None: sc.collection.children.link(c)
    a2 = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o.name.startswith("CLOD_v2")][0]
    a2.location = (-0.13, 0, 0)

# ---------------- estudio oscuro
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.0045, 0.006, 1)
def mat(n, c, r=0.4, m=0.0, e=0.0, ec=None):
    x = bpy.data.materials.new(n); x.use_nodes = True; b = x.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r; b.inputs["Metallic"].default_value = m
    if e: b.inputs["Emission Color"].default_value = (*(ec or c), 1); b.inputs["Emission Strength"].default_value = e
    return x
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0)); suelo = bpy.context.object; suelo.data.materials.append(mat("Suelo", (0.018, 0.019, 0.022), 0.28, 0.2))
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 1.6, 2.0), rotation=(math.radians(90), 0, 0)); fondo = bpy.context.object
fondo.data.materials.append(mat("Fondo", (0.012, 0.013, 0.016), 0.6))
for k, x in enumerate((-0.9, -0.3, 0.45, 1.1)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 1.55, 1.2)); t = bpy.context.object; t.scale = (0.008, 0.008, 1.2)
    t.data.materials.append(mat("Linea%d" % k, (0.2, 0.4, 0.9), 0.5, 0, 1.6, (0.18, 0.42, 1.0)))
def luz(n, tipo, pos, e, col=(1, 1, 1), tam=0.5, mira=(0, 0, 0.16)):
    d = bpy.data.lights.new(n, tipo); d.energy = e; d.color = col
    if tipo == 'AREA': d.size = tam
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = pos
    o.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler(); return o
luz("Clave", 'AREA', (-0.7, -0.75, 0.75), 38, (1.0, 0.96, 0.92), 0.6)
luz("Relleno", 'AREA', (0.8, -0.6, 0.35), 7, (0.85, 0.9, 1.0), 0.8)
luz("ContraIzq", 'AREA', (-0.6, 0.7, 0.5), 45, (0.55, 0.72, 1.0), 0.35)
luz("ContraDer", 'AREA', (0.65, 0.65, 0.45), 40, (0.55, 0.72, 1.0), 0.35)
luz("Arriba", 'AREA', (0, 0, 1.3), 12, (1, 1, 1), 1.0)
luz("Calida", 'AREA', (0.5, -0.2, 0.08), 4, (1.0, 0.6, 0.3), 0.3)

# ---------------- render
r = sc.render; r.engine = 'CYCLES'; r.resolution_x = 1080; r.resolution_y = 1350; r.resolution_percentage = 100
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
def foto(nombre, pos, mira, lente, f=1, fstop=2.8, foco=None):
    sc.frame_set(f)
    cam.location = pos; cam.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    cam_d.lens = lente; cam_d.dof.focus_distance = (Vector(foco or mira) - Vector(pos)).length; cam_d.dof.aperture_fstop = fstop
    r.filepath = os.path.join(OUT, nombre); bpy.ops.render.render(write_still=True); print("FOTO", nombre)
foto("comparacion.png", (0.0, -1.05, 0.22), (0.0, 0, 0.165), 58, fstop=8)
foto("cara.png", (0.165, -0.33, 0.27), (0.13, 0, 0.256), 90, fstop=4, foco=(0.13, -0.06, 0.256))
foto("espalda.png", (0.55, 0.62, 0.30), (0.13, 0, 0.17), 60, fstop=5.6)
foto("saludo.png", (-0.22, -0.78, 0.20), (0.13, 0, 0.17), 60, f=(2 + F_SAL) // 2 + 4, fstop=4)
print("PRUEBA_OK")
