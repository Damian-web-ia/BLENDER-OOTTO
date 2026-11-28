# PELO DE MAITE CON HEBRAS (fase 4) · EKORUEDAS · 28-11-2026
# Encima de la masa de pelo de Tripo se "peinan" hebras reales (Hair Curves de Blender) tumbadas sobre la superficie:
# en la cabeza bajan desde la coronilla, en la trenza van a lo largo de la trenza. Las hebras se pegan a la malla con
# el nodo "Deform Curves on Surface", así siguen a la cabeza, a la trenza con su física y a cualquier deformación.
# Material: Principled Hair BSDF (melanina) con variación por hebra.
import bpy, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def _triangulos(me, mat_index):
    m = me.data; m.calc_loop_triangles()
    lt = m.loop_triangles
    n = len(lt)
    tv = np.empty(n * 3, np.int64); lt.foreach_get('vertices', tv); tv = tv.reshape(-1, 3)
    tl = np.empty(n * 3, np.int64); lt.foreach_get('loops', tl); tl = tl.reshape(-1, 3)
    tp = np.empty(n, np.int64); lt.foreach_get('polygon_index', tp)
    mi = np.empty(len(m.polygons), np.int32); m.polygons.foreach_get('material_index', mi)
    sel = mi[tp] == mat_index
    return tv[sel], tl[sel], tp[sel]


def _uv_pelo(me, ip):
    """UV propio para pegar las hebras: el atlas de Tripo se solapa (40 % de hebras sin sitio). Proyección inteligente
    sólo del pelo; el resto de caras se manda fuera (5, 5) para que no haya ambigüedad. El render sigue usando el de Tripo."""
    m = me.data
    render = next(l for l in m.uv_layers if l.active_render)
    uvp = m.uv_layers.get("uv_pelo") or m.uv_layers.new(name="uv_pelo")
    for l in m.uv_layers: l.active_render = (l.name == render.name)
    m.uv_layers.active = uvp
    for p in m.polygons: p.select = (p.material_index == ip)
    bpy.context.view_layer.objects.active = me
    for o in bpy.context.view_layer.objects: o.select_set(False)
    me.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.002, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    mi = np.empty(len(m.polygons), np.int32); m.polygons.foreach_get('material_index', mi)
    lt = np.empty(len(m.polygons), np.int32); m.polygons.foreach_get('loop_total', lt)
    lf = np.repeat(np.arange(len(m.polygons)), lt)
    uv = np.empty(len(m.loops) * 2, np.float32); uvp.data.foreach_get('uv', uv); uv = uv.reshape(-1, 2)
    uv[mi[lf] != ip] = (5.0, 5.0)
    uvp.data.foreach_set('uv', uv.ravel())
    m.uv_layers.active = render
    print("PELO_HEBRAS uv propio del pelo listo; render con", render.name, flush=True)
    return uvp


def pelo_curvas(arm, me, densidad=1.6e6, puntos=6, semilla=21, largo=(0.014, 0.034)):
    m = me.data; rng = np.random.default_rng(semilla)
    ip = next(i for i, mt in enumerate(m.materials) if mt and mt.name == "MAITE_pelo")
    co = np.empty(len(m.vertices) * 3); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    uvl = _uv_pelo(me, ip); uv_nombre = uvl.name
    luv = np.empty(len(uvl.data) * 2); uvl.data.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    tv, tl, tp = _triangulos(me, ip)
    A, B, C = co[tv[:, 0]], co[tv[:, 1]], co[tv[:, 2]]
    area = np.linalg.norm(np.cross(B - A, C - A), axis=1) / 2
    n = int(area.sum() * densidad)
    elegidos = rng.choice(len(area), size=n, p=area / area.sum())
    r1 = np.sqrt(rng.random(n)); r2 = rng.random(n)
    wa, wb, wc = 1 - r1, r1 * (1 - r2), r1 * r2
    raiz = A[elegidos] * wa[:, None] + B[elegidos] * wb[:, None] + C[elegidos] * wc[:, None]
    U0, U1, U2 = luv[tl[elegidos, 0]], luv[tl[elegidos, 1]], luv[tl[elegidos, 2]]
    uv = U0 * wa[:, None] + U1 * wb[:, None] + U2 * wc[:, None]
    # BVH sólo del pelo (para tumbar las hebras sobre su superficie)
    vp = np.unique(tv)
    mapa = np.full(len(co), -1); mapa[vp] = np.arange(len(vp))
    bvh = BVHTree.FromPolygons([Vector(p) for p in co[vp]], [list(mapa[t]) for t in tv])
    # dirección de peinado: trenza a lo largo de sus huesos; cabeza desde la coronilla hacia abajo
    trenza = [b for b in arm.data.bones if b.name.startswith("Trenza_")]
    segs = [(np.array(arm.matrix_world @ b.head_local), np.array(arm.matrix_world @ b.tail_local)) for b in trenza]
    head = arm.data.bones["mixamorig:Head"]
    coronilla = np.array(arm.matrix_world @ head.head_local) * 0 + np.array([0, 0, 0.0])
    Pz = co[vp]; arriba = Pz[Pz[:, 2] > np.percentile(Pz[:, 2], 85)]
    coronilla = np.array([np.median(arriba[:, 0]), np.median(arriba[:, 1]) + 0.025, arriba[:, 2].max()])
    def dir_trenza(p):
        mejor, d = 1e9, None
        for a, b in segs:
            ab = b - a; t = np.clip((p - a) @ ab / (ab @ ab), 0, 1); q = a + ab * t
            dd = np.linalg.norm(p - q)
            if dd < mejor: mejor, d = dd, ab / np.linalg.norm(ab)
        return mejor, d
    pos = np.empty((n, puntos, 3)); rad = np.empty((n, puntos))
    L = rng.uniform(largo[0], largo[1], n)
    for i in range(n):
        p = Vector(raiz[i]); loc, nor, _f, _d = bvh.find_nearest(p)
        nor = Vector(nor) if nor is not None else Vector((0, 0, 1))
        dt, dbr = dir_trenza(np.array(p))
        if dt < 0.03 and p.z < 0.80:
            d = Vector(dbr); torsion = 0.45 if (np.cross(dbr, np.array(nor)) @ np.array([0, 0, 1])) > 0 else -0.45
            d = (d + nor.cross(d) * torsion).normalized()
        else:
            d = Vector(np.array(p) - coronilla); d = d - nor * d.dot(nor)
            if d.length < 1e-6: d = Vector((0, 0, -1))
            d.normalize(); d = (d + Vector((0, 0, -0.35))).normalized()
        d = (d + Vector(rng.normal(0, 0.05, 3))).normalized()
        paso = L[i] / (puntos - 1)
        for k in range(puntos):
            t = k / (puntos - 1)
            loc, nor, _f, _d = bvh.find_nearest(p)
            if loc is None: loc, nor = p, Vector((0, 0, 1))
            nor = Vector(nor)
            q = Vector(loc) + nor * (0.00025 + 0.0010 * t * t)
            pos[i, k] = q; rad[i, k] = 0.00011 * (1 - 0.75 * t)
            d = d - nor * d.dot(nor)
            if d.length < 1e-6: d = Vector((0, 0, -1))
            d.normalize()
            p = q + d * paso
    c = bpy.data.hair_curves.get("MAITE_hebras")
    if c: bpy.data.hair_curves.remove(c)
    c = bpy.data.hair_curves.new("MAITE_hebras")
    c.add_curves([puntos] * n)
    c.position_data.foreach_set('vector', pos.reshape(-1).astype(np.float32))
    ar = c.attributes.get("radius") or c.attributes.new("radius", 'FLOAT', 'POINT')
    ar.data.foreach_set('value', rad.reshape(-1).astype(np.float32))
    au = c.attributes.get("surface_uv_coordinate") or c.attributes.new("surface_uv_coordinate", 'FLOAT2', 'CURVE')
    au.data.foreach_set('vector', uv.reshape(-1).astype(np.float32))
    c.surface = me; c.surface_uv_map = uv_nombre
    me.add_rest_position_attribute = True            # el nodo de pegar necesita "rest_position" en la superficie
    ob = bpy.data.objects.get("MAITE_pelo_hebras")
    if ob: bpy.data.objects.remove(ob)
    ob = bpy.data.objects.new("MAITE_pelo_hebras", c)
    me.users_collection[0].objects.link(ob)
    ob.parent = me; ob.matrix_parent_inverse.identity(); ob.matrix_world = me.matrix_world.copy()
    # deformar sobre la superficie (sigue a la cabeza, a la trenza y a las formas de la cara)
    ng = bpy.data.node_groups.get("MAITE_pegar_hebras") or bpy.data.node_groups.new("MAITE_pegar_hebras", 'GeometryNodeTree')
    ng.nodes.clear()
    if not ng.interface.items_tree:
        ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi = ng.nodes.new('NodeGroupInput'); go = ng.nodes.new('NodeGroupOutput')
    de = ng.nodes.new('GeometryNodeDeformCurvesOnSurface')
    ng.links.new(gi.outputs[0], de.inputs[0]); ng.links.new(de.outputs[0], go.inputs[0])
    md = ob.modifiers.new("Pegar a la piel", 'NODES'); md.node_group = ng
    # material de pelo
    mt = bpy.data.materials.get("MAITE_hebras") or bpy.data.materials.new("MAITE_hebras"); mt.use_nodes = True
    N = mt.node_tree.nodes; Lk = mt.node_tree.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); hb = N.new("ShaderNodeBsdfHairPrincipled")
    hb.parametrization = 'MELANIN'
    hb.inputs["Melanin"].default_value = 0.80; hb.inputs["Melanin Redness"].default_value = 0.50
    hb.inputs["Roughness"].default_value = 0.32; hb.inputs["Radial Roughness"].default_value = 0.45
    hb.inputs["Random Color"].default_value = 0.12; hb.inputs["Random Roughness"].default_value = 0.15
    Lk.new(hb.outputs[0], out.inputs["Surface"])
    c.materials.append(mt)
    print("PELO_HEBRAS", n, "hebras de", puntos, "puntos; área", round(float(area.sum()), 4), "m²; coronilla", np.round(coronilla, 3).tolist(), flush=True)
    return ob
