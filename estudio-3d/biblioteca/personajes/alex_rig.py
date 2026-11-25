# ALEX v2 · CONSTRUCCIÓN DEL RIG DE ANIMACIÓN (se ejecuta UNA vez sobre alex_v2.blend)
# Esqueleto Mixamo de Tripo + controles IK de brazos y piernas, polos calibrados,
# deformación mejorada y colección lista para importar en cualquier reel.
import bpy, math
from mathutils import Vector, Matrix

R = math.radians
arm = bpy.data.objects["ALEX_v2"]
me = bpy.data.objects["ALEX_v2_Malla"]
pb = arm.pose.bones
def B(n): return pb["mixamorig:" + n]

# ---------------------------------------------------------------- pose de reposo limpia
if arm.animation_data: arm.animation_data_clear()
for p in pb:
    for c in list(p.constraints): p.constraints.remove(c)
    p.rotation_mode = 'XYZ'; p.rotation_euler = (0, 0, 0); p.location = (0, 0, 0); p.scale = (1, 1, 1)
bpy.context.view_layer.update()

# ---------------------------------------------------------------- deformación
am = [m for m in me.modifiers if m.type == 'ARMATURE'][0]
am.use_deform_preserve_volume = True          # codos, muñecas y rodillas sin perder volumen
cs = me.modifiers.get("Suavizado_correctivo") or me.modifiers.new("Suavizado_correctivo", 'CORRECTIVE_SMOOTH')
cs.rest_source = 'ORCO'; cs.smooth_type = 'LENGTH_WEIGHTED'; cs.iterations = 6; cs.factor = 0.5
cs.use_pin_boundary = True; cs.scale = 1.0
# pesos: normalizar y como mucho 4 huesos por vértice
bpy.context.view_layer.objects.active = me
for o in bpy.context.selected_objects: o.select_set(False)
me.select_set(True)
try:
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
except Exception as e:
    print("pesos:", e)

# ---------------------------------------------------------------- controles
col = bpy.data.collections.get("ALEX_v2_controles")
if not col:
    col = bpy.data.collections.new("ALEX_v2_controles"); bpy.context.scene.collection.children.link(col)
for o in list(col.objects): bpy.data.objects.remove(o)

def W(n, tail=False):
    b = B(n); return arm.matrix_world @ (b.tail if tail else b.head)

def ctrl(name, world_mat, size=0.06, shape='CUBE'):
    o = bpy.data.objects.new(name, None); col.objects.link(o)
    o.empty_display_type = shape; o.empty_display_size = size
    o.parent = arm; o.matrix_world = world_mat
    o.rotation_mode = 'XYZ'
    return o

def bone_world(n):
    return arm.matrix_world @ B(n).matrix

CT = {}
for lado, L in (("R", "Right"), ("L", "Left")):
    s = -1 if lado == "R" else 1
    # mano: en la muñeca, orientada como la mano (por si se quiere usar su giro)
    CT["mano_" + lado] = ctrl("CTRL_mano_" + lado, Matrix.Translation(W(L + "Hand")), 0.05, 'CUBE')
    # codo: detrás y un poco fuera del codo
    e = W(L + "ForeArm")
    CT["codo_" + lado] = ctrl("CTRL_codo_" + lado, Matrix.Translation(e + Vector((s * 0.25, 0.45, 0))), 0.04, 'SPHERE')
    # pie: en el tobillo, con la orientación del pie
    fm = bone_world(L + "Foot").normalized()
    CT["pie_" + lado] = ctrl("CTRL_pie_" + lado, fm, 0.08, 'CUBE')
    # rodilla: delante
    k = W(L + "Leg")
    CT["rodilla_" + lado] = ctrl("CTRL_rodilla_" + lado, Matrix.Translation(k + Vector((s * 0.05, -0.6, 0))), 0.04, 'SPHERE')

def ik(bone, target, pole):
    c = B(bone).constraints.new('IK'); c.name = "IK"
    c.target = target; c.pole_target = pole; c.chain_count = 2; c.use_tail = True; c.use_stretch = False
    return c

IKS = {}
for lado, L in (("R", "Right"), ("L", "Left")):
    IKS["brazo_" + lado] = ik(L + "ForeArm", CT["mano_" + lado], CT["codo_" + lado])
    IKS["pierna_" + lado] = ik(L + "Leg", CT["pie_" + lado], CT["rodilla_" + lado])
    cr = B(L + "Foot").constraints.new('COPY_ROTATION'); cr.name = "Rot_pie"
    cr.target = CT["pie_" + lado]; cr.target_space = 'WORLD'; cr.owner_space = 'WORLD'

# ---------------------------------------------------------------- calibrar polos (reposo intacto con IK activo)
bpy.context.view_layer.update()
REST = {}
for p in pb: REST[p.name] = (arm.matrix_world @ p.head).copy()
CAL = {}
def calib(key, mid_bone):
    c = IKS[key]; best = None
    for a in range(-180, 180, 2):
        c.pole_angle = R(a); bpy.context.view_layer.update()
        d = ((arm.matrix_world @ B(mid_bone).head) - REST["mixamorig:" + mid_bone]).length
        if best is None or d < best[0]: best = (d, a)
    for a10 in range(best[1] * 10 - 20, best[1] * 10 + 21):
        c.pole_angle = R(a10 / 10); bpy.context.view_layer.update()
        d = ((arm.matrix_world @ B(mid_bone).head) - REST["mixamorig:" + mid_bone]).length
        if d < best[0]: best = (d, a10 / 10)
    c.pole_angle = R(best[1]); CAL[key] = (round(best[1], 1), round(best[0] * 1000, 2))
for lado, L in (("R", "Right"), ("L", "Left")):
    calib("brazo_" + lado, L + "ForeArm"); calib("pierna_" + lado, L + "Leg")
bpy.context.view_layer.update()
err = max(((arm.matrix_world @ p.head) - REST[p.name]).length for p in pb)
arm["polos_calibrados"] = str(CAL)

# ---------------------------------------------------------------- colección del personaje
pc = bpy.data.collections.get("ALEX_v2_personaje")
if not pc:
    pc = bpy.data.collections.new("ALEX_v2_personaje"); bpy.context.scene.collection.children.link(pc)
for o in (arm, me):
    for c in list(o.users_collection): c.objects.unlink(o)
    pc.objects.link(o)
if col.name not in [c.name for c in pc.children]:
    bpy.context.scene.collection.children.unlink(col); pc.children.link(col)

result = {"polos": CAL, "error_reposo_mm": round(err * 1000, 2), "controles": sorted(o.name for o in col.objects)}
