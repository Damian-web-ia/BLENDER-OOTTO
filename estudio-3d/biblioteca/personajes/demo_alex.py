# DEMO: Alex v2 respira, saluda, camina hacia cámara, señala, pulgar arriba y se encoge de hombros (~14 s).
import bpy, math
from mathutils import Vector
exec(open(ANIM, encoding="utf-8").read())
sc = bpy.context.scene
ALEX.animation_data_clear()
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
ALEX.location = (0, 1.6, 0); ALEX.rotation_euler = (0, 0, 0)
todo_reposo(1)
f = 12
f = saludo("R", f, ciclos=3, vel=7)
f += 4
f = andar(f, pasos=4, zancada=0.5, fp=16)
f += 6
f = senalar("R", f, dur=30, objetivo=(0.0, -3.0, 1.2))
f += 4
f = pulgar_arriba("L", f, dur=26)
f += 4
f = encogerse(f, dur=22)
fin = f + 20
todo_reposo(fin)
respirar(1, fin, periodo=64, amplitud=1.5)
# cabeza viva: mira a cámara con pequeñas variaciones
for k, (fk, a, i, g) in enumerate(((1, 0, 0, 0), (60, -3, -4, -4), (120, 2, 3, 0), (200, 0, 0, 3), (280, -2, -5, -5), (360, 3, 5, 2), (fin, 0, 0, 0))):
    if fk <= fin: cabeza(fk, a, i, g)
suavizar()
sc.frame_start, sc.frame_end = 1, fin
result = {"fin": fin}
