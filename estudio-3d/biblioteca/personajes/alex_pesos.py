# ALEX v2 · CORRECCIÓN DE PESOS EN LAS AXILAS (se ejecuta una vez sobre alex_v2_rig.blend)
# El auto-rig de Tripo asigna parte del costado del torso al brazo: al levantar los brazos el torso se deforma.
# Aquí se pasa ese peso del brazo al pecho (Spine2) según lo lejos que esté el vértice del eje del brazo hacia dentro.
import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line

arm = bpy.data.objects["ALEX_v2"]; me = bpy.data.objects["ALEX_v2_Malla"]
mw = me.matrix_world; aw = arm.matrix_world
VG = {g.name: g for g in me.vertex_groups}
spine = VG["mixamorig:Spine2"]
cambios = {}
for L in ("Right", "Left"):
    g_arm = VG["mixamorig:" + L + "Arm"]; g_sh = VG["mixamorig:" + L + "Shoulder"]
    b = arm.data.bones["mixamorig:" + L + "Arm"]
    h = aw @ b.head_local; t = aw @ b.tail_local
    n = 0
    for v in me.data.vertices:
        p = mw @ v.co
        if not (0.95 < p.z < 1.33): continue
        wa = 0.0
        for gr in v.groups:
            if gr.group == g_arm.index: wa = gr.weight
        if wa < 0.02: continue
        q, fac = intersect_point_line(p, h, t)
        fac = max(0.0, min(1.0, fac)); q = h + (t - h) * fac
        d_in = abs(q.x) - abs(p.x)            # cuánto está el vértice hacia dentro (hacia el torso) del eje del brazo
        if d_in <= 0.035: continue
        k = min(1.0, (d_in - 0.035) / 0.05)    # 0 → se queda en el brazo; 1 → pasa entero al pecho
        k *= min(1.0, (1.33 - p.z) / 0.08)     # suave cerca del hombro
        mover = wa * k
        g_arm.add([v.index], wa - mover, 'REPLACE')
        spine.add([v.index], mover, 'ADD')
        n += 1
    cambios[L] = n
# normalizar
bpy.context.view_layer.objects.active = me
for o in bpy.context.selected_objects: o.select_set(False)
me.select_set(True)
try:
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
except Exception as e:
    print("normalizar:", e)
arm["pesos_axila"] = str(cambios)
result = {"vertices_corregidos": cambios}
