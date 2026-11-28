# PELO DE MAITE CON HEBRAS (fase 4) · EKORUEDAS · 28-11-2026
# Encima de la masa de pelo de Tripo se "peinan" hebras reales (Hair Curves de Blender) tumbadas sobre la superficie:
# en la cabeza bajan desde la coronilla, en la trenza van a lo largo de la trenza. Las hebras se pegan a la malla con
# el nodo "Deform Curves on Surface", así siguen a la cabeza, a la trenza con su física y a cualquier deformación.
# Material: Principled Hair BSDF (melanina) con variación por hebra.
import bpy, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def _triangulos(me, mascara_pol):
    m = me.data; m.calc_loop_triangles()
    lt = m.loop_triangles
    n = len(lt)
    tv = np.empty(n * 3, np.int64); lt.foreach_get('vertices', tv); tv = tv.reshape(-1, 3)
    tl = np.empty(n * 3, np.int64); lt.foreach_get('loops', tl); tl = tl.reshape(-1, 3)
    tp = np.empty(n, np.int64); lt.foreach_get('polygon_index', tp)
    sel = mascara_pol[tp]
    return tv[sel], tl[sel], tp[sel]


def _segmentos_trenza(arm):
    return [(np.array(arm.matrix_world @ b.head_local), np.array(arm.matrix_world @ b.tail_local))
            for b in arm.data.bones if b.name.startswith("Trenza_")]


def _dist_segmentos(P, segs):
    d = np.full(len(P), 1e9)
    for a, b in segs:
        ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1); q = a + np.outer(t, ab)
        d = np.minimum(d, np.linalg.norm(P - q, axis=1))
    return d


def _zona_pelo(arm, me, ip):
    """Caras de 'pelo' que de verdad son pelo: cabeza y trenza. Lo demás (bordes oscuros de los tirantes, botones...)
    pasa al material de cuero."""
    m = me.data; nf = len(m.polygons)
    mi = np.empty(nf, np.int32); m.polygons.foreach_get('material_index', mi)
    cen = np.empty(nf * 3); m.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    cab = np.array(arm.matrix_world @ arm.data.bones["mixamorig:Head"].head_local)
    en_cabeza = (cen[:, 2] > cab[2] - 0.035) & (np.linalg.norm(cen - (cab + np.array([0, 0, 0.06])), axis=1) < 0.17)
    en_trenza = _dist_segmentos(cen, _segmentos_trenza(arm)) < 0.028
    es = (mi == ip) & (en_cabeza | en_trenza)
    otro = (mi == ip) & ~es
    i_cuero = next((i for i, mt in enumerate(m.materials) if mt and mt.name == "MAITE_funda"), None)
    if i_cuero is not None and otro.any():
        mi[otro] = i_cuero; m.polygons.foreach_set('material_index', mi); m.update()
    print("PELO_HEBRAS zona de pelo:", int(es.sum()), "caras; fuera de la cabeza y la trenza -> cuero:", int(otro.sum()), flush=True)
    return es


def _uv_pelo(me, caras):
    """UV propio para pegar las hebras (el atlas de Tripo se solapa: el 40 % de las hebras no encontraba su sitio).
    Cada cara de pelo recibe su propia casilla en una rejilla (sin operadores, sin solapes); el resto de caras va a
    (5, 5). El nodo sólo necesita que cada punto UV caiga en una única cara. El render sigue con el UV de Tripo."""
    m = me.data
    render = next(l for l in m.uv_layers if l.active_render)
    uvp = m.uv_layers.get("uv_pelo") or m.uv_layers.new(name="uv_pelo")
    for l in m.uv_layers: l.active_render = (l.name == render.name)
    nf = len(m.polygons)
    lt = np.empty(nf, np.int32); m.polygons.foreach_get('loop_total', lt)
    ls = np.empty(nf, np.int32); m.polygons.foreach_get('loop_start', ls)
    uv = np.full((len(m.loops), 2), 5.0, np.float32)
    caras = np.asarray(caras)
    G = int(math.ceil(math.sqrt(len(caras)))); celda = 1.0 / G; mg = celda * 0.12
    for k, f in enumerate(caras):
        cx, cy = (k % G) * celda, (k // G) * celda
        n = lt[f]
        if n == 4:
            esq = [(0, 0), (1, 0), (1, 1), (0, 1)]
        elif n == 3:
            esq = [(0, 0), (1, 0), (0.5, 1)]
        else:
            esq = [(0.5 + 0.5 * math.cos(2 * math.pi * q / n), 0.5 + 0.5 * math.sin(2 * math.pi * q / n)) for q in range(n)]
        for q, (a, b) in enumerate(esq):
            uv[ls[f] + q] = (cx + mg + a * (celda - 2 * mg), cy + mg + b * (celda - 2 * mg))
    uvp.data.foreach_set('uv', uv.ravel())
    m.uv_layers.active = render
    print("PELO_HEBRAS uv propio:", len(caras), "caras de pelo en una rejilla de", G, "x", G, flush=True)
    return uvp


def pelo_curvas(arm, me, densidad=1.6e6, puntos=6, semilla=21, largo=(0.014, 0.034), ojos=None):
    m = me.data; rng = np.random.default_rng(semilla)
    ip = next(i for i, mt in enumerate(m.materials) if mt and mt.name == "MAITE_pelo")
    co = np.empty(len(m.vertices) * 3); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    zona = _zona_pelo(arm, me, ip)
    cejas = _caras_cejas(me, ojos) if ojos else np.zeros(len(m.polygons), bool)
    uvl = _uv_pelo(me, np.where(zona | cejas)[0]); uv_nombre = uvl.name
    luv = np.empty(len(uvl.data) * 2); uvl.data.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    if cejas.any(): _cejas_curvas(me, cejas, ojos, luv, uv_nombre)
    tv, tl, tp = _triangulos(me, zona)
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
    ob = _objeto_hebras("MAITE_pelo_hebras", "MAITE_hebras", me, pos, rad, uv, uv_nombre, 0.80, 0.50, 0.32)
    print("PELO_HEBRAS", n, "hebras de", puntos, "puntos; área", round(float(area.sum()), 4), "m²; coronilla", np.round(coronilla, 3).tolist(), flush=True)
    return ob


def _objeto_hebras(nombre_obj, nombre_mat, me, pos, rad, uv, uv_nombre, melanina, rojizo, rugosidad):
    n, puntos = pos.shape[0], pos.shape[1]
    c = bpy.data.hair_curves.get(nombre_obj)
    if c: bpy.data.hair_curves.remove(c)
    c = bpy.data.hair_curves.new(nombre_obj)
    c.add_curves([puntos] * n)
    c.position_data.foreach_set('vector', pos.reshape(-1).astype(np.float32))
    ar = c.attributes.get("radius") or c.attributes.new("radius", 'FLOAT', 'POINT')
    ar.data.foreach_set('value', rad.reshape(-1).astype(np.float32))
    au = c.attributes.get("surface_uv_coordinate") or c.attributes.new("surface_uv_coordinate", 'FLOAT2', 'CURVE')
    au.data.foreach_set('vector', uv.reshape(-1).astype(np.float32))
    c.surface = me; c.surface_uv_map = uv_nombre
    me.add_rest_position_attribute = True            # el nodo de pegar necesita "rest_position" en la superficie
    ob = bpy.data.objects.get(nombre_obj)
    if ob: bpy.data.objects.remove(ob)
    ob = bpy.data.objects.new(nombre_obj, c)
    me.users_collection[0].objects.link(ob)
    ob.parent = me; ob.matrix_parent_inverse.identity(); ob.matrix_world = me.matrix_world.copy()
    # pegadas a la superficie (siguen a la cabeza, a la trenza y a las formas de la cara)
    ng = bpy.data.node_groups.get("MAITE_pegar_hebras")
    if ng is None:
        ng = bpy.data.node_groups.new("MAITE_pegar_hebras", 'GeometryNodeTree')
        ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
        gi = ng.nodes.new('NodeGroupInput'); go = ng.nodes.new('NodeGroupOutput')
        de = ng.nodes.new('GeometryNodeDeformCurvesOnSurface')
        ng.links.new(gi.outputs[0], de.inputs[0]); ng.links.new(de.outputs[0], go.inputs[0])
    md = ob.modifiers.new("Pegar a la piel", 'NODES'); md.node_group = ng
    mt = bpy.data.materials.get(nombre_mat) or bpy.data.materials.new(nombre_mat); mt.use_nodes = True
    N = mt.node_tree.nodes; Lk = mt.node_tree.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); hb = N.new("ShaderNodeBsdfHairPrincipled")
    hb.parametrization = 'MELANIN'
    hb.inputs["Melanin"].default_value = melanina; hb.inputs["Melanin Redness"].default_value = rojizo
    hb.inputs["Roughness"].default_value = rugosidad; hb.inputs["Radial Roughness"].default_value = 0.45
    hb.inputs["Random Color"].default_value = 0.12; hb.inputs["Random Roughness"].default_value = 0.15
    Lk.new(hb.outputs[0], out.inputs["Surface"])
    c.materials.append(mt)
    return ob


def _caras_cejas(me, ojos):
    """Caras de piel con la ceja pintada (oscuras, encima de cada ojo)."""
    m = me.data; nf = len(m.polygons)
    ipiel = next(i for i, mt in enumerate(m.materials) if mt and mt.name == "MAITE_piel")
    img = next(n.image for n in m.materials[ipiel].node_tree.nodes if n.type == 'TEX_IMAGE' and n.image and n.image.colorspace_settings.name == 'sRGB')
    w, h = img.size; px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    lum = px[:, :, :3] @ np.array([0.3, 0.55, 0.15], np.float32)
    uvl = next(l for l in m.uv_layers if l.active_render)
    luv = np.empty(len(uvl.data) * 2, np.float32); uvl.data.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    lt = np.empty(nf, np.int32); m.polygons.foreach_get('loop_total', lt); lf = np.repeat(np.arange(nf), lt)
    fuv = np.zeros((nf, 2)); np.add.at(fuv, lf, luv); fuv /= lt[:, None]
    oscuro = np.full(nf, 9.0)
    for t in (0.0, 0.4, 0.8):
        s_ = fuv[lf] * (1 - t) + luv * t
        v = lum[np.clip((s_[:, 1] * h).astype(int), 0, h - 1), np.clip((s_[:, 0] * w).astype(int), 0, w - 1)]
        np.minimum.at(oscuro, lf, v)
    mi = np.empty(nf, np.int32); m.polygons.foreach_get('material_index', mi)
    cen = np.empty(nf * 3); m.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    es = np.zeros(nf, bool)
    for C in ojos:
        d = cen - np.array(C)
        es |= (mi == ipiel) & (oscuro < 0.36) & (d[:, 2] > 0.014) & (d[:, 2] < 0.038) & (np.abs(d[:, 0]) < 0.034) & (d[:, 1] < 0.006)
    # sólo las manchas grandes (la ceja); un punto oscuro suelto de la textura daría un pelo perdido en la frente
    ids = np.where(es)[0]; padre = {}
    def raiz(a):
        while padre.setdefault(a, a) != a:
            padre[a] = padre[padre[a]]; a = padre[a]
        return a
    for fi in ids:
        vs = list(m.polygons[fi].vertices)
        for v in vs[1:]: padre[raiz(vs[0])] = raiz(v)
    comp = np.array([raiz(m.polygons[fi].vertices[0]) for fi in ids])
    tam = {c: int((comp == c).sum()) for c in set(comp.tolist())}
    grande = max(tam.values()) if tam else 0
    for fi, c in zip(ids, comp):
        if tam[c] < max(6, 0.12 * grande): es[fi] = False
    print("CEJAS caras con ceja pintada:", int(es.sum()), "(manchas:", sorted(tam.values(), reverse=True)[:6], ")", flush=True)
    return es


def _cejas_curvas(me, cejas, ojos, luv, uv_nombre, densidad=0.75e7, puntos=4, semilla=5):
    """Pelos de las cejas: cortos, tumbados, del lado de la nariz hacia fuera; los del principio, de pie."""
    m = me.data; rng = np.random.default_rng(semilla)
    co = np.empty(len(m.vertices) * 3); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    tv, tl, tp = _triangulos(me, cejas)
    A, B, C = co[tv[:, 0]], co[tv[:, 1]], co[tv[:, 2]]
    area = np.linalg.norm(np.cross(B - A, C - A), axis=1) / 2
    n = int(area.sum() * densidad)
    el = rng.choice(len(area), size=n, p=area / area.sum())
    r1 = np.sqrt(rng.random(n)); r2 = rng.random(n); wa, wb, wc = 1 - r1, r1 * (1 - r2), r1 * r2
    raiz = A[el] * wa[:, None] + B[el] * wb[:, None] + C[el] * wc[:, None]
    uv = luv[tl[el, 0]] * wa[:, None] + luv[tl[el, 1]] * wb[:, None] + luv[tl[el, 2]] * wc[:, None]
    # sólo donde la pintura de la ceja es oscura de verdad (la forma de la ceja la da la textura)
    ipiel = next(i for i, mt in enumerate(m.materials) if mt and mt.name == "MAITE_piel")
    img = next(x.image for x in m.materials[ipiel].node_tree.nodes if x.type == 'TEX_IMAGE' and x.image and x.image.colorspace_settings.name == 'sRGB')
    w, h = img.size; px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    uvr = next(l for l in m.uv_layers if l.active_render)
    lr = np.empty(len(uvr.data) * 2, np.float32); uvr.data.foreach_get('uv', lr); lr = lr.reshape(-1, 2)
    uvt = lr[tl[el, 0]] * wa[:, None] + lr[tl[el, 1]] * wb[:, None] + lr[tl[el, 2]] * wc[:, None]
    col = px[np.clip((uvt[:, 1] * h).astype(int), 0, h - 1), np.clip((uvt[:, 0] * w).astype(int), 0, w - 1), :3]
    ok = (col @ np.array([0.3, 0.55, 0.15])) < 0.40
    raiz, uv = raiz[ok], uv[ok]; n = len(raiz)
    vp = np.unique(tv); mapa = np.full(len(co), -1); mapa[vp] = np.arange(len(vp))
    # superficie de la cara alrededor (piel cercana a las cejas) para tumbar los pelos
    cen = np.empty(len(m.polygons) * 3); m.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    cerca = np.where(np.min([np.linalg.norm(cen - np.array(Cj), axis=1) for Cj in ojos], axis=0) < 0.06)[0]
    vs = np.unique(np.concatenate([np.array(m.polygons[i].vertices) for i in cerca]))
    mp = np.full(len(co), -1); mp[vs] = np.arange(len(vs))
    bvh = BVHTree.FromPolygons([Vector(p) for p in co[vs]], [list(mp[list(m.polygons[i].vertices)]) for i in cerca])
    pos = np.empty((n, puntos, 3)); rad = np.empty((n, puntos))
    ejes = {}
    for k, Cj in enumerate(ojos):
        Cj = np.array(Cj); sel = np.linalg.norm(raiz - Cj, axis=1) < 0.05
        if sel.sum() < 3: continue
        Q = raiz[sel]; cq = Q.mean(0); _, _, vt = np.linalg.svd(Q - cq); a = vt[0]
        cara_x = (np.array(ojos[0]) + np.array(ojos[1])) / 2 if len(ojos) > 1 else Cj
        if (a @ (cq - cara_x)) < 0: a = -a                     # hacia fuera (la sien)
        tq = (Q - cq) @ a
        ejes[k] = (Cj, cq, a, tq.min(), tq.max())
    L = rng.uniform(0.0025, 0.0046, n)
    for i in range(n):
        p0 = raiz[i]; kk = min(ejes, key=lambda k_: np.linalg.norm(p0 - ejes[k_][0]))
        Cj, cq, a, t0, t1 = ejes[kk]
        t = np.clip(((p0 - cq) @ a - t0) / max(1e-6, t1 - t0), 0, 1)
        d = Vector(a * (0.35 + 0.75 * t) + np.array([0, 0, 1.0]) * (0.95 - 1.05 * t) + rng.normal(0, 0.12, 3)).normalized()
        p = Vector(p0); paso = L[i] / (puntos - 1)
        for k in range(puntos):
            tt = k / (puntos - 1)
            loc, nor, _f, _d = bvh.find_nearest(p)
            if loc is None: loc, nor = p, Vector((0, -1, 0))
            nor = Vector(nor)
            q = Vector(loc) + nor * (0.00012 + 0.00035 * tt)
            pos[i, k] = q; rad[i, k] = 0.000045 * (1 - 0.7 * tt)
            d = d - nor * d.dot(nor)
            if d.length < 1e-6: d = Vector((0, 0, 1))
            d.normalize(); p = q + d * paso
    _objeto_hebras("MAITE_cejas_hebras", "MAITE_cejas", me, pos, rad, uv, uv_nombre, 0.74, 0.50, 0.36)
    print("CEJAS", n, "pelos", flush=True)
