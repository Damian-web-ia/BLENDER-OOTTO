# DEMO 2: llega andando, saluda, señala, se agacha a mirar el suelo, pulgar arriba y se encoge de hombros.
import bpy
exec(open(ANIM, encoding="utf-8").read())
sc = bpy.context.scene
ALEX.animation_data_clear()
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
ALEX.location = (0, 2.0, 0); ALEX.rotation_euler = (0, 0, 0)
todo_reposo(1); sc.frame_set(1); calibrar_palma()
cabeza(1, 0, 0, -8); cabeza(14, 0, 0, 6); cabeza(26, 0, 0, 0)
f = andar(28, pasos=4, zancada=0.6, fp=15)
f += 2
f = saludo("R", f, ciclos=3, vel=7)
f += 2
f = senalar("L", f, dur=24, objetivo=(1.5, -2.0, 0.6))
f = agacharse(f, dur=36, mano_lado="R")
f += 2
f = pulgar_arriba("R", f, dur=24)
f += 2
f = encogerse(f, dur=20)
fin = f + 24
todo_reposo(fin)
respirar(1, fin, periodo=64, amplitud=1.5)
suavizar()
sc.frame_start, sc.frame_end = 1, fin
result = {"fin": fin}
