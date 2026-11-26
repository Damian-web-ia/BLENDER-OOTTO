# DEMO 3 (con voz): Alex saluda a cámara y enseña sus expresiones.
# Voz de Ootto (Carlos): "¡Eh, hola! Soy Alex. Mira esto: ya puedo sonreír, enfadarme... ¡y hasta sorprenderme! Bueno, ¿qué? ¿Empezamos?"
import bpy, math, bmesh
from mathutils import Vector
exec(open(ANIM, encoding="utf-8").read())
sc = bpy.context.scene
D = 0.8   # la voz empieza en el segundo 0,8
VOZ = [{"at": D, "words": [["¡Eh", 0.057, 0.6], ["hola", 0.659, 1.09], ["Soy", 1.115, 1.38], ["Alex", 1.38, 1.8], ["Mira", 1.83, 2.07], ["esto", 2.07, 2.38], ["ya", 2.43, 2.59], ["puedo", 2.59, 2.75], ["sonreír", 2.75, 3.39], ["enfadarme", 3.552, 4.35], ["¡y", 4.458, 4.62], ["hasta", 4.62, 4.78], ["sorprenderme", 4.78, 5.42], ["Bueno", 5.52, 5.98], ["¿qué", 6.006, 6.22], ["¿Empezamos", 6.274, 6.89]]}]
def F(t): return int(round((D + t) * 30)) + 1
FIN = F(6.89) + 54
ALEX.animation_data_clear()
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
sk = MALLA.data.shape_keys
if sk.animation_data and sk.animation_data.action: sk.animation_data.action = None
ALEX.location = (0, 0, 0); ALEX.rotation_euler = (0, 0, 0)
todo_reposo(1); sc.frame_set(1); calibrar_palma()
for l in ("R", "L"): brazo_caido(l, 1)

# --- 0. espera mirando a un lado
cara(1, "concentrado", 0.6); cabeza(1, 4, 0, 35); columna(1, 0, 0, 10)
cabeza(F(-0.35), 4, 0, 35); cara(F(-0.3), "concentrado", 0.6)
# --- 1. "¡Eh, hola!": gira a cámara, cejas arriba, sonrisa y saludo
cabeza(F(0.15), -4, -3, 0); columna(F(0.2), 0, 0, 0); cara(F(0.1), "sorpresa", 0.35); cara(F(0.5), "sonrisa")
f = F(0.0); s = -1
mano_en("R", f, (-0.31, -0.03, 0.89)); mano_pose("R", f, "relajada")
mano_en("R", F(0.15), (-0.30, -0.02, 0.85))
mano_en("R", F(0.45), (-0.44, -0.10, 1.57)); codo_hacia("R", F(0.45), (-0.95, 0.15, 1.05)); mano_pose("R", F(0.45), "abierta")
mano_en("R", F(0.62), (-0.36, -0.10, 1.54)); mano_en("R", F(0.80), (-0.52, -0.10, 1.54)); mano_en("R", F(0.98), (-0.40, -0.10, 1.55))
# --- 2. "Soy Alex": se toca el pecho
mano_en("R", F(1.25), (-0.06, -0.24, 1.22)); codo_hacia("R", F(1.25), (-0.7, 0.0, 0.9)); mano_pose("R", F(1.25), "abierta")
orientar_mano("R", F(1.25), palma_hacia=(0, 1, 0), dedos_hacia=(1, 0, 0.3))
mano_pose("L", F(1.25), "relajada")
cabeza(F(1.3), 4, -4, 0); cara(F(1.3), "sonrisa", 0.8)
# --- 3. "Mira esto:": abre las manos
for l in ("R", "L"):
    sx = -1 if l == "R" else 1
    mano_en(l, F(1.95), (sx * 0.40, -0.30, 1.05)); codo_hacia(l, F(1.95), (sx * 0.8, 0.3, 0.9)); mano_pose(l, F(1.95), "abierta")
cabeza(F(2.0), 0, 0, 0); cara(F(2.0), "picaro", 0.6)
# --- 4. "ya puedo sonreír": sonrisa enorme, manos abiertas a los lados
cara(F(2.7), "risa"); cabeza(F(2.8), -6, 4, 0)
for l in ("R", "L"):
    sx = -1 if l == "R" else 1
    mano_en(l, F(2.8), (sx * 0.46, -0.20, 1.15)); mano_pose(l, F(2.8), "abierta"); mano_pose(l, F(3.35), "abierta")
# --- 5. "enfadarme...": cejas abajo, puños, se inclina hacia delante
cara(F(3.45), "enfado"); cabeza(F(3.55), 8, 0, 0); columna(F(3.6), 6, 0, 0)
for l in ("R", "L"):
    sx = -1 if l == "R" else 1
    mano_en(l, F(3.6), (sx * 0.30, -0.18, 0.98)); codo_hacia(l, F(3.6), (sx * 0.8, 0.4, 1.0)); mano_pose(l, F(3.6), "puño")
mano_en("R", F(4.0), (-0.30, -0.18, 1.00)); mano_en("L", F(4.0), (0.30, -0.18, 1.00))
cara(F(4.3), "enfado")
# --- 6. "¡y hasta sorprenderme!": se echa atrás, ojos y cejas arriba, manos arriba
cara(F(4.55), "sorpresa"); cabeza(F(4.6), -10, 0, 0); columna(F(4.6), -6, 0, 0)
for l in ("R", "L"):
    sx = -1 if l == "R" else 1
    mano_en(l, F(4.62), (sx * 0.45, -0.22, 1.45)); codo_hacia(l, F(4.62), (sx * 0.9, 0.2, 1.0)); mano_pose(l, F(4.62), "abierta")
mano_en("R", F(5.3), (-0.46, -0.22, 1.47)); mano_en("L", F(5.3), (0.46, -0.22, 1.47)); cara(F(5.35), "sorpresa", 0.9)
# --- 7. "Bueno, ¿qué?": se relaja, sonrisa pícara, se encoge un poco
cara(F(5.6), "picaro"); cabeza(F(5.7), 0, 6, 0); columna(F(5.7), 0, 0, 0)
for l in ("R", "L"):
    sx = -1 if l == "R" else 1
    mano_en(l, F(5.75), (sx * 0.42, -0.24, 1.02)); mano_pose(l, F(5.75), "abierta"); hombro(l, F(5.75), 10)
    hombro(l, F(6.15), 0)
for l in ("R", "L"): orientar_mano(l, F(5.75), palma_hacia=(0, 0, 1), dedos_hacia=((-1 if l == "R" else 1) * 0.5, -1, 0))
# --- 8. "¿Empezamos?": pulgar arriba y guiño
brazo_caido("L", F(6.3)); mano_pose("L", F(6.3), "relajada"); mano_giro("L", F(6.3))
mano_en("R", F(6.35), (-0.24, -0.30, 1.18)); codo_hacia("R", F(6.35), (-0.8, 0.1, 0.75)); mano_pose("R", F(6.35), "pulgar")
orientar_mano("R", F(6.35), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", F(6.5), (-0.24, -0.31, 1.22)); orientar_mano("R", F(6.5), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
cara(F(6.35), "sonrisa"); cabeza(F(6.4), 3, -6, 0)
parpadeo(F(6.95), 1.0, lado="L")      # guiño
mano_en("R", F(7.6), (-0.24, -0.30, 1.19)); orientar_mano("R", F(7.6), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
cara(FIN, "sonrisa", 0.8); cabeza(FIN, 2, -4, 0)
mano_en("R", FIN, (-0.25, -0.29, 1.17))

hablar(VOZ)
parpadeos(1, FIN, evitar=(F(6.95), F(4.6)))
respirar(1, FIN, periodo=64, amplitud=1.5)
suavizar()
# las curvas de la cara también suaves
ad = sk.animation_data
if ad and ad.action:
    try: cv = list(ad.action.fcurves)
    except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
    for fc in cv:
        for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
        fc.update()

# --- estudio
if "Ciclorama" not in bpy.data.objects:
    mat = bpy.data.materials.get("Estudio") or bpy.data.materials.new("Estudio"); mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.20, 0.045, 0.06, 1); b.inputs["Roughness"].default_value = 0.9
    mesh = bpy.data.meshes.new("Ciclorama"); bm = bmesh.new(); prof = [(-8, 0)]
    for i in range(25):
        a = (i / 24) * math.pi / 2; r = 2.5; prof.append((3 + r * math.sin(a), r - r * math.cos(a)))
    prof.append((5.5, 10))
    rows = [[bm.verts.new((x, y, z)) for x in (-8, 8)] for (y, z) in prof]
    for a_, c_ in zip(rows[:-1], rows[1:]): bm.faces.new((a_[0], a_[1], c_[1], c_[0]))
    bm.to_mesh(mesh); bm.free(); mesh.materials.append(mat)
    for p in mesh.polygons: p.use_smooth = True
    o = bpy.data.objects.new("Ciclorama", mesh); sc.collection.objects.link(o)
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.2, 0.05, 0.06, 1)
L = bpy.data.objects
for n, loc, e, col in (("Clave", (1.8, -2.2, 2.6), 520, (1, 0.93, 0.85)), ("Relleno", (-2.4, -1.8, 1.7), 200, (0.85, 0.9, 1)), ("Contra", (-1.0, 2.5, 2.6), 800, (1, 0.75, 0.55))):
    o = L[n]; o.location = loc; o.data.energy = e; o.data.color = col
    o.rotation_euler = (Vector((0, 0, 1.35)) - o.location).to_track_quat("-Z", "Y").to_euler()
cam = L["CAM"]; cam.animation_data_clear(); cam.data.lens = 40; cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24
def ck(f, loc, t):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
ck(1, (0.25, -2.15, 1.47), (0, 0, 1.30)); ck(FIN, (0.14, -1.80, 1.49), (0, 0, 1.33))
sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 67
sc.eevee.taa_render_samples = 48; sc.render.fps = 30
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.frame_start, sc.frame_end = 1, FIN
result = {"fin": FIN}
