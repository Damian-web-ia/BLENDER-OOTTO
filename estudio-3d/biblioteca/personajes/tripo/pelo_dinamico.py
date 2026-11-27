# PELO CON MOVIMIENTO para personajes de Tripo (esqueleto Mixamo) · EKORUEDAS · 27-11-2026
# Damián (27-11): "personajes 3D que valgan la pena ... el pelo que tenga movimiento, que tenga todo movimiento".
# 1) preparar_pelo(arm, pelo): lo que cuelga por debajo de la cabeza (melena, coleta, mechones) se reparte en mechones
#    por zonas alrededor de la cabeza (izquierda, derecha, detrás...). Cada mechón lleva su cadena de huesos que nace de
#    mixamorig:Head; los pesos pasan suavemente de la cabeza a la cadena. Lo de arriba (el casco del pelo) sigue rígido.
# 2) hornear_pelo(arm, cadenas, f0, f1): cada cadena es un muelle amortiguado que sigue a la cabeza con retraso (inercia,
#    rebote y un poco de gravedad) y se guarda en fotogramas clave. Sin drivers ni manejadores: se renderiza igual en
#    segundo plano.
# Uso: exec(open(".../pelo_dinamico.py", encoding="utf-8").read())
#      cads = preparar_pelo(arm, bpy.data.objects["tripo_part_0"]) ; ...animar el cuerpo... ; hornear_pelo(arm, cads, 1, 150)
import bpy, math
from mathutils import Vector, Matrix, Quaternion


def _cabeza(arm):
    """Cabeza en espacio del esqueleto: base de mixamorig:Head y punta (HeadTop_End)."""
    h = arm.data.bones["mixamorig:Head"]; t = arm.data.bones.get("mixamorig:HeadTop_End")
    a = h.head_local.copy(); b = t.head_local.copy() if t else h.tail_local.copy()
    return a, b


def pieza_pelo(arm):
    """La malla que más vértices tiene alrededor y por encima de la cabeza (Tripo entrega el pelo como una pieza)."""
    a, b = _cabeza(arm); mw = arm.matrix_world
    c = mw @ ((a + b) / 2); alto = ((mw @ b) - (mw @ a)).length
    mejor, punt = None, -1e9
    for o in bpy.data.objects:
        if o.type != 'MESH' or not o.data.vertices: continue
        vs = [o.matrix_world @ v.co for v in o.data.vertices]
        cerca = sum(1 for v in vs if (v - c).length < alto * 1.6) / len(vs)
        arriba = sum(1 for v in vs if v.z > c.z) / len(vs)
        p = cerca * 2 + arriba + len(vs) / 20000
        if cerca > 0.6 and p > punt: mejor, punt = o, p
    return mejor


def _kmedias(pts, k, iters=25):
    cs = [pts[int(i * len(pts) / k)].copy() for i in range(k)]
    for _ in range(iters):
        grupos = [[] for _ in cs]
        for p in pts:
            j = min(range(len(cs)), key=lambda q: (p - cs[q]).length_squared); grupos[j].append(p)
        cs = [sum(g, Vector()) / len(g) if g else cs[j] for j, g in enumerate(grupos)]
    return cs


def preparar_pelo(arm, pelo=None, n=3, mechones=3, z_corte=None, transicion=None, minimo=40):
    """Devuelve la lista de cadenas (listas de nombres de hueso). None si no cuelga nada."""
    pelo = pelo or pieza_pelo(arm)
    a, b = _cabeza(arm); alto = (b - a).length; centro = a + (b - a) * 0.45
    z0 = z_corte if z_corte is not None else centro.z - alto * 0.15        # por encima: rígido con la cabeza
    zt = transicion or alto * 0.30                                       # tramo en el que pasa de cabeza a mechón
    mw = pelo.matrix_world; ai = arm.matrix_world.inverted()
    pts = [(i, ai @ (mw @ v.co)) for i, v in enumerate(pelo.data.vertices)]
    cuelga = [(i, p) for i, p in pts if p.z < z0]
    if len(cuelga) < minimo: return None
    # mechones: agrupar lo que cuelga por su posición alrededor de la cabeza (planta XY)
    plano = [Vector((p.x, p.y, 0)) for _, p in cuelga]
    cs = _kmedias(plano, min(mechones, max(1, len(cuelga) // minimo)))
    grupo = [min(range(len(cs)), key=lambda q: (Vector((p.x, p.y, 0)) - cs[q]).length_squared) for _, p in cuelga]
    cuentas = [grupo.count(j) for j in range(len(cs))]
    validos = [j for j in range(len(cs)) if cuentas[j] >= minimo]
    if not validos: return None
    for k in range(len(grupo)):                                          # los grupos pequeños se unen al más cercano válido
        if grupo[k] not in validos:
            p = cuelga[k][1]; grupo[k] = min(validos, key=lambda q: (Vector((p.x, p.y, 0)) - cs[q]).length_squared)
    bpy.context.view_layer.objects.active = arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones; cadenas = []; info = []
    for m, j in enumerate(validos):
        mios = [cuelga[k] for k in range(len(cuelga)) if grupo[k] == j]
        zb = min(p.z for _, p in mios)
        cen = []
        for s in range(n + 1):
            z = z0 - (z0 - zb) * s / n; tol = (z0 - zb) / (2 * n) + 1e-4
            ban = [p for _, p in mios if abs(p.z - z) <= tol] or sorted((p for _, p in mios), key=lambda q: abs(q.z - z))[:8]
            c = sum(ban, Vector()) / len(ban); cen.append(Vector((c.x, c.y, z)))
        padre = eb["mixamorig:Head"]; nombres = []
        for s in range(n):
            nb = eb.new(f"Pelo_{m}_{s}"); nb.head = cen[s]; nb.tail = cen[s + 1]; nb.parent = padre
            nb.use_connect = s > 0; nb.roll = 0; padre = nb; nombres.append(nb.name)
        cadenas.append(nombres); info.append((mios, z0, zb))
    bpy.ops.object.mode_set(mode='OBJECT')
    for nm in [x for c in cadenas for x in c] + ["mixamorig:Head"]:
        if nm not in pelo.vertex_groups: pelo.vertex_groups.new(name=nm)
    otros = [g for g in pelo.vertex_groups if g.name.startswith("mixamorig:") and g.name != "mixamorig:Head"]
    for nombres, (mios, z0_, zb) in zip(cadenas, info):
        for i, p in mios:
            t = max(0.0, min(0.999, (z0_ - p.z) / max(1e-6, z0_ - zb))) * n; s = int(t); f = t - s
            mez = max(0.0, min(1.0, (z0_ - p.z) / zt)); mez = mez * mez * (3 - 2 * mez)
            w = {nombres[s]: (1 - f) * mez, "mixamorig:Head": 1 - mez}
            if s + 1 < n: w[nombres[s + 1]] = f * mez
            else: w[nombres[s]] = mez
            for g in otros:
                try: g.remove([i])
                except Exception: pass
            for nm, val in w.items():
                if val > 1e-3: pelo.vertex_groups[nm].add([i], val, 'REPLACE')
                else:
                    try: pelo.vertex_groups[nm].remove([i])
                    except Exception: pass
    if not any(md.type == 'ARMATURE' for md in pelo.modifiers):
        md = pelo.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    for c in cadenas:
        for nm in c: arm.pose.bones[nm].rotation_mode = 'QUATERNION'
    return cadenas


def hornear_pelo(arm, cadenas, f0, f1, rigidez=0.11, amort=0.86, gravedad=0.0004, previo=20):
    """Muelle amortiguado (Verlet). 'gravedad' en metros por fotograma² del mundo. 'previo': fotogramas de asentado."""
    sc = bpy.context.scene
    if isinstance(cadenas[0], str): cadenas = [cadenas]
    g = arm.matrix_world.inverted().to_3x3() @ Vector((0, 0, -gravedad))
    C = []
    for cad in cadenas:
        pbs = [arm.pose.bones[nm] for nm in cad]
        for pb in pbs: pb.rotation_quaternion = Quaternion()
        C.append({"pbs": pbs})
    sc.frame_set(f0); bpy.context.view_layer.update()
    Hinv = arm.pose.bones["mixamorig:Head"].matrix.inverted()
    for c in C:
        pbs = c["pbs"]; j = [pbs[0].head.copy()] + [pb.tail.copy() for pb in pbs]
        c["off"] = [Hinv @ x for x in j]; c["L"] = [(j[k + 1] - j[k]).length for k in range(len(pbs))]
        c["pos"] = [x.copy() for x in j]; c["ant"] = [x.copy() for x in j]

    def paso(f, guardar):
        sc.frame_set(f)
        for c in C:
            for pb in c["pbs"]: pb.rotation_quaternion = Quaternion()
        bpy.context.view_layer.update()
        Mh = arm.pose.bones["mixamorig:Head"].matrix
        for c in C:
            reposo = [Mh @ o for o in c["off"]]; pos, ant = c["pos"], c["ant"]
            pos[0] = reposo[0].copy()
            for k in range(1, len(pos)):
                v = (pos[k] - ant[k]) * amort; ant[k] = pos[k].copy()
                r = rigidez * (1.0 - 0.45 * k / len(pos))
                pos[k] = pos[k] + v + (reposo[k] - pos[k]) * r + g
            for k in range(1, len(pos)):
                d = pos[k] - pos[k - 1]
                if d.length > 1e-9: pos[k] = pos[k - 1] + d.normalized() * c["L"][k - 1]
        if not guardar: return
        for c in C:
            for k, pb in enumerate(c["pbs"]):
                M = pb.matrix.copy(); cab = M.translation.copy(); y = M.col[1].xyz.normalized()
                q = y.rotation_difference((c["pos"][k + 1] - cab).normalized())
                pb.matrix = Matrix.Translation(cab) @ q.to_matrix().to_4x4() @ M.to_3x3().to_4x4()
                bpy.context.view_layer.update()
                pb.keyframe_insert("rotation_quaternion", frame=f)

    for _ in range(previo): paso(f0, False)          # se asienta antes de empezar
    for f in range(f0, f1 + 1): paso(f, True)
    return True
