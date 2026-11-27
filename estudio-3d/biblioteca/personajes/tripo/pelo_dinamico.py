# PELO CON MOVIMIENTO para personajes de Tripo (esqueleto Mixamo) · EKORUEDAS · 27-11-2026
# Damián (27-11): "personajes 3D que valgan la pena ... el pelo que tenga movimiento, que tenga todo movimiento".
# 1) preparar_pelo(): busca la pieza del pelo (Tripo la entrega por partes), separa lo que cuelga lejos de la cabeza
#    (coleta, melena, rizos), le pone una cadena de huesos que sale de mixamorig:Head y reparte los pesos con suavidad.
# 2) hornear_pelo(f0, f1): simula la cadena como un muelle amortiguado que sigue a la cabeza (inercia, rebote, gravedad)
#    y lo guarda en fotogramas clave. Sin drivers ni manejadores: se renderiza igual en segundo plano.
# Uso: exec(open(".../pelo_dinamico.py", encoding="utf-8").read()); cad = preparar_pelo(arm, n=5); ... animar ...; hornear_pelo(arm, cad, 1, 240)
import bpy, bmesh, math
from mathutils import Vector, Matrix, Quaternion

def _cabeza(arm):
    h = arm.data.bones["mixamorig:Head"]; t = arm.data.bones.get("mixamorig:HeadTop_End")
    a = h.head_local; b = t.head_local if t else h.tail_local
    return a, b

def pieza_pelo(arm):
    """La malla cuyo volumen está más por encima y por detrás de la cabeza (el pelo)."""
    a, b = _cabeza(arm); centro = (a + b) / 2; alto = (b - a).length
    mejor, punt = None, -1e9
    for o in bpy.data.objects:
        if o.type != 'MESH': continue
        vs = [o.matrix_world @ v.co for v in o.data.vertices]
        if not vs: continue
        arriba = sum(1 for v in vs if v.z > centro.z + alto * 0.25) / len(vs)
        cerca = sum(1 for v in vs if (v - centro).length < alto * 2.2) / len(vs)
        detras = sum(1 for v in vs if v.y > centro.y + alto * 0.2) / len(vs)
        p = arriba * 2 + cerca + detras
        if cerca > 0.5 and p > punt: mejor, punt = o, p
    return mejor

def preparar_pelo(arm, n=5, radio=None, pelo=None):
    sc = bpy.context.scene
    pelo = pelo or pieza_pelo(arm)
    a, b = _cabeza(arm); alto = (b - a).length; centro = a + (b - a) * 0.45
    radio = radio or alto * 0.62
    mw = pelo.matrix_world; ai = arm.matrix_world.inverted()
    pts = [(i, ai @ (mw @ v.co)) for i, v in enumerate(pelo.data.vertices)]
    lejos = [(i, p) for i, p in pts if (p - centro).length > radio and p.z < b.z]
    if len(lejos) < 30: return None
    zs = sorted(p.z for _, p in lejos); z_top, z_bot = zs[-1], zs[0]
    # línea central por rodajas de altura
    centros = []
    for k in range(n + 1):
        z = z_top + (z_bot - z_top) * k / n; ban = [p for _, p in lejos if abs(p.z - z) < (z_top - z_bot) / (2 * n) + 1e-4]
        if not ban: ban = sorted((p for _, p in lejos), key=lambda q: abs(q.z - z))[:10]
        c = sum(ban, Vector()) / len(ban); centros.append(Vector((c.x, c.y, z)))
    # la raíz se acerca a la cabeza (donde nace la coleta o la melena)
    centros[0] = centro + (centros[0] - centro).normalized() * radio * 0.92
    bpy.context.view_layer.objects.active = arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones; padre = eb["mixamorig:Head"]; nombres = []
    for k in range(n):
        nb = eb.new(f"Pelo_{k}"); nb.head = centros[k]; nb.tail = centros[k + 1]; nb.parent = padre
        nb.use_connect = k > 0; nb.roll = 0; padre = nb; nombres.append(nb.name)
    bpy.ops.object.mode_set(mode='OBJECT')
    # pesos: a lo largo de la cadena; cerca del cuero cabelludo se mezcla con la cabeza
    for nm in nombres + ["mixamorig:Head"]:
        if nm not in pelo.vertex_groups: pelo.vertex_groups.new(name=nm)
    largo = [(centros[k + 1] - centros[k]).length for k in range(n)]; tot = sum(largo)
    for i, p in lejos:
        # posición a lo largo de la cadena (por altura)
        t = max(0.0, min(0.999, (z_top - p.z) / max(1e-6, z_top - z_bot))) * n
        k = int(t); f = t - k
        mezcla = max(0.0, min(1.0, ((p - centro).length - radio) / (alto * 0.25)))
        w = {nombres[k]: (1 - f) * mezcla}
        if k + 1 < n: w[nombres[k + 1]] = f * mezcla
        w["mixamorig:Head"] = 1 - mezcla
        for g in pelo.vertex_groups:
            if g.name.startswith("mixamorig:") and g.name != "mixamorig:Head":
                try: g.remove([i])
                except Exception: pass
        for nm, val in w.items():
            if val > 1e-3: pelo.vertex_groups[nm].add([i], val, 'REPLACE')
    if not any(m.type == 'ARMATURE' for m in pelo.modifiers):
        md = pelo.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    for nm in nombres: arm.pose.bones[nm].rotation_mode = 'QUATERNION'
    return nombres

def hornear_pelo(arm, cadena, f0, f1, rigidez=0.10, amort=0.86, gravedad=0.0012):
    """Muelle amortiguado: cada articulación sigue a su sitio de reposo (pegado a la cabeza) con retraso y rebote."""
    sc = bpy.context.scene; pbs = [arm.pose.bones[n] for n in cadena]
    for pb in pbs: pb.rotation_quaternion = Quaternion();
    sc.frame_set(f0); bpy.context.view_layer.update()
    H = arm.pose.bones["mixamorig:Head"]
    Hinv = H.matrix.inverted()
    juntas = [pbs[0].head.copy()] + [pb.tail.copy() for pb in pbs]
    off = [Hinv @ j for j in juntas]                       # sitio de reposo en el espacio de la cabeza
    L = [(juntas[k + 1] - juntas[k]).length for k in range(len(pbs))]
    pos = [j.copy() for j in juntas]; ant = [j.copy() for j in juntas]
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        for pb in pbs: pb.rotation_quaternion = Quaternion()
        bpy.context.view_layer.update()
        Mh = arm.pose.bones["mixamorig:Head"].matrix
        reposo = [Mh @ o for o in off]
        pos[0] = reposo[0].copy()
        for k in range(1, len(pos)):
            v = (pos[k] - ant[k]) * amort
            ant[k] = pos[k].copy()
            r = rigidez * (1.0 - 0.45 * k / len(pos))
            pos[k] = pos[k] + v + (reposo[k] - pos[k]) * r + Vector((0, 0, -gravedad))
        for k in range(1, len(pos)):                       # largo fijo de cada hueso
            d = pos[k] - pos[k - 1]
            if d.length > 1e-9: pos[k] = pos[k - 1] + d.normalized() * L[k - 1]
        for k, pb in enumerate(pbs):
            M = pb.matrix.copy(); cab = M.translation.copy(); y = M.col[1].xyz.normalized()
            q = y.rotation_difference((pos[k + 1] - cab).normalized())
            pb.matrix = Matrix.Translation(cab) @ q.to_matrix().to_4x4() @ M.to_3x3().to_4x4()
            bpy.context.view_layer.update()
            pb.keyframe_insert("rotation_quaternion", frame=f)
    return True
