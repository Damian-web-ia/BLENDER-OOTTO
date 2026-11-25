# Banco de pruebas: una pose distinta en cada fotograma (1..12) para revisar deformaciones.
import bpy
exec(open(ANIM, encoding="utf-8").read())
ad = ALEX.animation_data
if ad: ALEX.animation_data_clear()
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
P = {}
def pose(f, fn):
    todo_reposo(f); fn(f)
# 1 reposo natural
pose(1, lambda f: None)
# 2 saludo
def saludo(f):
    mano("R", f, (-0.05, -0.15, 0.62)); codo("R", f, (-0.5, 0.2, -0.3)); mano_pose("R", f, "abierta"); cabeza(f, 0, -5, -5)
pose(2, saludo)
# 3 señalar adelante
def senalar(f):
    mano("R", f, (0.20, -0.45, 0.42)); codo("R", f, (-0.2, 0.0, -0.4)); mano_pose("R", f, "señalar"); columna(f, 0, 0, 8)
pose(3, senalar)
# 4 pulgar arriba delante del pecho
def pulgar(f):
    mano("R", f, (0.20, -0.30, 0.25)); codo("R", f, (-0.3, 0.0, -0.5)); mano_pose("R", f, "pulgar"); mano_giro("R", f, 0, 0, -60)
pose(4, pulgar)
# 5 manos en la cintura (en jarra)
def jarra(f):
    for l, s in (("R", 1), ("L", -1)):
        mano(l, f, (s * 0.16, 0.04, 0.06)); codo(l, f, (-s * 0.5, 0.2, 0.0)); mano_pose(l, f, "puño")
pose(5, jarra)
# 6 brazos cruzados
def cruzados(f):
    mano("R", f, (0.52, -0.14, 0.20)); codo("R", f, (-0.3, -0.3, -0.3))
    mano("L", f, (-0.52, -0.18, 0.22)); codo("L", f, (0.3, -0.3, -0.3))
    mano_pose("R", f, "relajada"); mano_pose("L", f, "relajada")
pose(6, cruzados)
# 7 sentadilla (pies quietos)
def sentadilla(f):
    cadera(f, (0, 0.10, -0.38)); columna(f, 25, 0, 0)
    for l, s in (("R", 1), ("L", -1)):
        rodilla(l, f, (-s * 0.1, -0.3, 0)); mano(l, f, (s * 0.05, -0.35, -0.05)); codo(l, f, (0, 0.2, -0.3))
pose(7, sentadilla)
# 8 pensativo (mano a la barbilla)
def pensativo(f):
    mano("R", f, (0.30, -0.22, 0.58)); codo("R", f, (-0.1, -0.3, -0.6)); mano_pose("R", f, "relajada"); cabeza(f, 5, 8, 0)
    mano("L", f, (-0.30, -0.12, 0.25)); codo("L", f, (0.1, 0.1, -0.4))
pose(8, pensativo)
# 9 encogerse de hombros
def encoge(f):
    for l, s in (("R", 1), ("L", -1)):
        mano(l, f, (-s * 0.12, -0.25, 0.15)); codo(l, f, (-s * 0.2, 0.3, -0.3)); mano_pose(l, f, "abierta"); mano_giro(l, f, 0, 0, 70 if l == "R" else -70); hombro(l, f, 15)
    cabeza(f, 0, 10, 0)
pose(9, encoge)
# 10 paso largo (zancada)
def zancada(f):
    pie("L", f, (0, -0.35, 0)); pie("R", f, (0, 0.30, 0.05), (20, 0, 0)); cadera(f, (0, -0.02, -0.08))
    mano("R", f, (0.05, -0.25, 0.08)); mano("L", f, (-0.05, 0.25, 0.05))
pose(10, zancada)
# 11 brazos arriba (celebración)
def arriba(f):
    for l, s in (("R", 1), ("L", -1)):
        mano(l, f, (-s * 0.15, -0.05, 0.95)); codo(l, f, (-s * 0.5, 0.2, 0.2)); mano_pose(l, f, "puño")
    cabeza(f, -10, 0, 0)
pose(11, arriba)
# 12 agacharse a coger algo del suelo
def coger(f):
    cadera(f, (0, 0.15, -0.30)); columna(f, 45, 0, 0)
    mano("R", f, (0.05, -0.45, -0.70)); codo("R", f, (-0.3, 0, 0)); mano("L", f, (-0.05, -0.30, -0.50))
    for l, s in (("R", 1), ("L", -1)): rodilla(l, f, (-s * 0.1, -0.3, 0))
pose(12, coger)
for o in [ALEX] + [o for o in bpy.data.objects if o.name.startswith("CTRL_")]:
    ad = o.animation_data
    if ad and ad.action:
        try: cv = list(ad.action.fcurves)
        except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
        for fc in cv:
            for k in fc.keyframe_points: k.interpolation = 'CONSTANT'
bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, 12
result = {"ok": 12}
