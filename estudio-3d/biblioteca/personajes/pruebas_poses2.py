# Banco de pruebas 2: posturas exigentes (una por fotograma) con posiciones absolutas.
import bpy
exec(open(ANIM, encoding="utf-8").read())
ALEX.animation_data_clear()
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
def pose(f, fn):
    todo_reposo(f)
    for l in ("R", "L"): brazo_caido(l, f)
    fn(f)
# 1 rodilla en el suelo (mirar una rueda)
def arrodillado(f):
    cadera(f, (0, 0.10, -0.45), (0, 0, 0)); columna(f, 15, 0, 0)
    pie_en("L", f, (0.20, -0.30, 0.12)); rodilla("L", f, (0, -0.5, 0))
    pie_en("R", f, (-0.20, 0.45, 0.10), (-70, 0, 0)); rodilla("R", f, (0, -0.4, -0.3))
    mano_en("R", f, (-0.15, -0.45, 0.55)); mano_en("L", f, (0.25, -0.35, 0.60)); cabeza(f, 15, 0, 0)
pose(1, arrodillado)
# 2 giro de tronco mirando atrás
def giro(f):
    columna(f, 0, 0, 35); cabeza(f, 0, 0, 30); cadera(f, (0, 0, 0), (0, 0, 10))
    mano_en("R", f, (-0.05, -0.30, 1.00)); mano_en("L", f, (0.40, 0.25, 0.95))
pose(2, giro)
# 3 inclinado a un lado apoyado
def lateral(f):
    columna(f, 0, 18, 0); cadera(f, (0.06, 0, 0), (0, -5, 0)); cabeza(f, 0, -8, 0)
    mano_en("L", f, (0.38, 0.0, 0.80)); mano_en("R", f, (-0.35, -0.10, 1.70))
pose(3, lateral)
# 4 empujando algo pesado
def empujar(f):
    cadera(f, (0, 0.10, -0.08)); columna(f, 22, 0, 0)
    pie_en("L", f, (0.20, -0.35, 0.12)); pie_en("R", f, (-0.20, 0.40, 0.12), (-25, 0, 0))
    for l in ("R", "L"): mano_en(l, f, (_sx(l) * 0.22, -0.62, 1.15)); mano_pose(l, f, "abierta")
pose(4, empujar)
# 5 sentado (en un taburete invisible)
def sentado(f):
    cadera(f, (0, 0.30, -0.42)); columna(f, -5, 0, 0)
    for l in ("R", "L"):
        pie_en(l, f, (_sx(l) * 0.22, -0.20, 0.12)); rodilla(l, f, (0, -0.6, 0.2))
        mano_en(l, f, (_sx(l) * 0.20, -0.18, 0.60))
pose(5, sentado)
# 6 salto (en el aire, brazos arriba)
def salto(f):
    cadera(f, (0, 0, 0.20))
    for l in ("R", "L"):
        pie_en(l, f, (_sx(l) * 0.22, 0.10, 0.30), (25, 0, 0)); rodilla(l, f, (0, -0.5, 0))
        mano_en(l, f, (_sx(l) * 0.45, -0.10, 2.05)); mano_pose(l, f, "abierta")
    cabeza(f, -12, 0, 0)
pose(6, salto)
for o in [ALEX] + [o for o in bpy.data.objects if o.name.startswith("CTRL_")]:
    ad = o.animation_data
    if ad and ad.action:
        try: cv = list(ad.action.fcurves)
        except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
        for fc in cv:
            for k in fc.keyframe_points: k.interpolation = 'CONSTANT'
bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, 6
result = {"ok": 6}
