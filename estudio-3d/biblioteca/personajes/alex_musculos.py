# ALEX v2 · MÚSCULOS QUE ACOMPAÑAN AL MOVIMIENTO (shape keys correctivas con drivers). Una vez sobre alex_v2_rig.blend.
# - Bíceps: se hincha al doblar el codo.            - Tríceps: se tensa al estirar el brazo hacia delante/arriba.
# - Deltoides: se redondea al levantar el brazo.     - Pectoral: se comprime al cruzar el brazo por delante.
# - Antebrazo: se ensancha un poco al cerrar el puño (se usa con el codo doblado).
import bpy, math
from mathutils import Vector
from mathutils.geometry import intersect_point_line

arm = bpy.data.objects["ALEX_v2"]; me = bpy.data.objects["ALEX_v2_Malla"]; mesh = me.data
mw = me.matrix_world; aw = arm.matrix_world; inv3 = mw.inverted().to_3x3()
if not mesh.shape_keys: me.shape_key_add(name="Basis", from_mix=False)
KB = mesh.shape_keys.key_blocks

# normales y posiciones de reposo en mundo
W = [mw @ v.co for v in mesh.vertices]
N = [(mw.to_3x3() @ v.normal).normalized() for v in mesh.vertices]
VG = {g.index: g.name for g in me.vertex_groups}
def peso_grupo(i, nombres):
    return sum(g.weight for g in mesh.vertices[i].groups if VG.get(g.group) in nombres)

def sm(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def campana(t, a, b):                     # 0 fuera de [a,b], 1 en el centro, suave
    if t <= a or t >= b: return 0.0
    m = (a + b) / 2; h = (b - a) / 2
    return sm(1 - abs(t - m) / h)

def hueso(n):
    b = arm.data.bones["mixamorig:" + n]; return aw @ b.head_local, aw @ b.tail_local

def key(nombre, fn):
    kb = KB.get(nombre)
    if kb: me.shape_key_remove(kb)
    kb = me.shape_key_add(name=nombre, from_mix=False); kb.slider_max = 1.5
    basis = KB["Basis"]; n = 0
    for i in range(len(W)):
        d = fn(i)
        if d is None or d.length < 1e-6: continue
        kb.data[i].co = basis.data[i].co + inv3 @ d; n += 1
    return kb, n

def driver(kb, expr, vars_):
    """vars_: (nombre, hueso1, hueso2) → distancia entre las cabezas de los dos huesos (LOC_DIFF)."""
    kb.driver_remove("value")
    fc = kb.driver_add("value"); dr = fc.driver; dr.type = 'SCRIPTED'
    for nombre, b1, b2 in vars_:
        v = dr.variables.new(); v.name = nombre; v.type = 'LOC_DIFF'
        v.targets[0].id = arm; v.targets[0].bone_target = "mixamorig:" + b1
        v.targets[1].id = arm; v.targets[1].bone_target = "mixamorig:" + b2
    dr.expression = expr
    for m in fc.modifiers: fc.modifiers.remove(m)

def dist(b1, b2):
    bpy.context.view_layer.update()
    return ((aw @ arm.pose.bones["mixamorig:" + b1].head) - (aw @ arm.pose.bones["mixamorig:" + b2].head)).length

stats = {}
for L, s in (("Right", -1), ("Left", 1)):
    lado = "R" if L == "Right" else "L"
    h, t = hueso(L + "Arm"); eh, et = hueso(L + "ForeArm")
    largo = (t - h).length
    frente = Vector((0, -1, 0)); fuera = Vector((s, 0, 0))
    def info(i, h=h, t=t):
        p = W[i]; q, fac = intersect_point_line(p, h, t)
        rad = (p - q); r = rad.length
        return p, fac, (rad / r if r > 1e-6 else rad), r

    def biceps(i, info=info):
        if peso_grupo(i, ("mixamorig:" + L + "Arm",)) < 0.2: return None
        p, fac, rd, r = info(i)
        w = campana(fac, 0.25, 0.95) * sm((rd.dot(frente) + 0.1) / 0.8)
        if w <= 0: return None
        return N[i] * 0.020 * w + (eh - p).normalized() * 0.004 * w
    kb, n = key("Biceps_" + lado, biceps); stats[kb.name] = n
    D0 = dist(L + "Arm", L + "Hand")          # brazo estirado: hombro-muñeca
    FLEX = f"max(0, min(1.3, ({D0:.4f} - mh) / {D0 - 0.17:.4f}))"
    driver(kb, FLEX, [("mh", L + "Arm", L + "Hand")])

    def triceps(i, info=info):
        if peso_grupo(i, ("mixamorig:" + L + "Arm",)) < 0.2: return None
        p, fac, rd, r = info(i)
        w = campana(fac, 0.15, 0.85) * sm((-rd.dot(frente) + 0.0) / 0.8)
        if w <= 0: return None
        return N[i] * 0.010 * w
    kb, n = key("Triceps_" + lado, triceps); stats[kb.name] = n
    E0 = dist(L + "ForeArm", L + "UpLeg")     # codo-cadera en reposo
    ALZA = f"max(0, min(1.2, (ec - {E0:.4f}) / 0.45))"
    driver(kb, ALZA + f" * max(0, 1 - max(0, ({D0:.4f} - mh) / 0.12))", [("ec", L + "ForeArm", L + "UpLeg"), ("mh", L + "Arm", L + "Hand")])

    def deltoide(i, info=info):
        p, fac, rd, r = info(i)
        if fac > 0.45 or peso_grupo(i, ("mixamorig:" + L + "Arm", "mixamorig:" + L + "Shoulder")) < 0.15: return None
        w = sm((fac + 0.15) / 0.2) * (1 - sm((fac - 0.15) / 0.3)) * sm((rd.dot(fuera) + rd.z * 0.6 + 0.2) / 0.9)
        if w <= 0: return None
        return N[i] * 0.012 * w + Vector((0, 0, 0.004)) * w
    kb, n = key("Deltoide_" + lado, deltoide); stats[kb.name] = n
    driver(kb, ALZA, [("ec", L + "ForeArm", L + "UpLeg")])

    def pectoral(i, L=L, s=s):
        p = W[i]
        if peso_grupo(i, ("mixamorig:Spine2",)) < 0.3 or p.y > -0.05: return None
        c = Vector((s * 0.10, -0.15, 1.27))
        d = math.sqrt(((p.x - c.x) / 0.10) ** 2 + ((p.z - c.z) / 0.08) ** 2)
        w = 1 - sm((d - 0.3) / 0.7)
        if w <= 0: return None
        return N[i] * 0.008 * w + Vector((-s * 0.006, 0, 0)) * w
    kb, n = key("Pectoral_" + lado, pectoral); stats[kb.name] = n
    OTRO = ("Left" if L == "Right" else "Right") + "Arm"
    C0 = dist(L + "ForeArm", OTRO)
    driver(kb, f"max(0, min(1, ({C0:.4f} - cx) / 0.22))", [("cx", L + "ForeArm", OTRO)])

    def antebrazo(i, eh=eh, et=et):
        if peso_grupo(i, ("mixamorig:" + L + "ForeArm",)) < 0.3: return None
        p = W[i]; q, fac = intersect_point_line(p, eh, et)
        w = campana(fac, 0.0, 0.6)
        if w <= 0: return None
        return N[i] * 0.006 * w
    kb, n = key("Antebrazo_" + lado, antebrazo); stats[kb.name] = n
    driver(kb, FLEX + " * 0.8", [("mh", L + "Arm", L + "Hand")])

result = stats
