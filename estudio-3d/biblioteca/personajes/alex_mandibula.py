# ALEX v2 · MANDÍBULA PARA HABLAR (se ejecuta una vez sobre alex_v2_rig.blend)
# Añade el hueso "Mandibula" (hijo de la cabeza) y le asigna la barbilla y el labio inferior con caída suave.
import bpy, math
from mathutils import Vector

arm = bpy.data.objects["ALEX_v2"]; me = bpy.data.objects["ALEX_v2_Malla"]
inv = arm.matrix_world.inverted()
PIVOTE = Vector((0.0, 0.015, 1.535))     # bisagra (delante de la oreja, a la altura del lóbulo)
BARBILLA = Vector((0.0, -0.10, 1.485))
Z_BOCA = 1.507                           # línea entre los labios (medida en el perfil de la cara)

# --- hueso
bpy.context.view_layer.objects.active = arm
for o in bpy.context.selected_objects: o.select_set(False)
arm.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones
if "Mandibula" in eb: eb.remove(eb["Mandibula"])
b = eb.new("Mandibula"); b.head = inv @ PIVOTE; b.tail = inv @ BARBILLA
b.parent = eb["mixamorig:Head"]; b.use_deform = True
b.align_roll(inv.to_3x3() @ Vector((0, 0, 1)))
bpy.ops.object.mode_set(mode='OBJECT')

# --- pesos
mw = me.matrix_world
vg = me.vertex_groups.get("Mandibula") or me.vertex_groups.new(name="Mandibula")
head_g = me.vertex_groups["mixamorig:Head"]; neck_g = me.vertex_groups.get("mixamorig:Neck")
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
n = 0
for v in me.data.vertices:
    p = mw @ v.co
    if not (1.42 < p.z < Z_BOCA + 0.012 and abs(p.x) < 0.12 and p.y < 0.03): continue
    w = smooth((Z_BOCA + 0.010 - p.z) / 0.016)          # por debajo de los labios → 1
    w *= smooth((0.115 - abs(p.x)) / 0.04)               # se apaga hacia las orejas
    w *= smooth((0.025 - p.y) / 0.05)                    # se apaga hacia atrás (cuello/nuca)
    w *= smooth((p.z - 1.435) / 0.03)                    # se apaga hacia el cuello
    if w < 0.01: continue
    vg.add([v.index], w, 'REPLACE')
    for gr in v.groups:
        if gr.group in (head_g.index, neck_g.index if neck_g else -1):
            me.vertex_groups[gr.group].add([v.index], gr.weight * (1 - w), 'REPLACE')
    n += 1
bpy.context.view_layer.objects.active = me
for o in bpy.context.selected_objects: o.select_set(False)
me.select_set(True)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
result = {"vertices_mandibula": n}
