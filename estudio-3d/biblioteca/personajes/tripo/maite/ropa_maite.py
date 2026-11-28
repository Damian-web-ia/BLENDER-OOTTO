# ROPA CON TELA DE VERDAD (fase 5) · EKORUEDAS · 28-11-2026
# El modelo de Tripo es una sola malla: la ropa está "pintada" encima del cuerpo y no hay brazo debajo de la manga.
# Para que la tela se mueva sin romper nada:
#   1. Las mangas de la camiseta se copian a un objeto propio (MAITE_manga_L/R), 1,2 mm por fuera, con los mismos
#      pesos del esqueleto (sigue al brazo) y encima una simulación de tela de algodón con pines: cosida al hombro,
#      libre (con peso) en el bajo de la manga.
#   2. La manga original del cuerpo se encoge 3 mm hacia el hueso y pasa a piel: es el brazo que se ve si la manga
#      se levanta.
#   3. El cuerpo es objeto de colisión para la tela.
import bpy, bmesh, math
import numpy as np
from mathutils import Vector

P = "mixamorig:"


def _pesos(me, gi):
    """Peso de cada vértice en el grupo gi (np.array)."""
    m = me.data; w = np.zeros(len(m.vertices))
    for v in m.vertices:
        for g in v.groups:
            if g.group == gi: w[v.index] = g.weight; break
    return w


def mangas_tela(arm, me, separacion=0.0012, encoger=0.003):
    m = me.data; nf = len(m.polygons); N = len(m.vertices)
    names = [mt.name if mt else "" for mt in m.materials]
    ic = names.index("MAITE_camiseta"); ip = names.index("MAITE_piel")
    mi = np.empty(nf, np.int32); m.polygons.foreach_get('material_index', mi)
    lt = np.empty(nf, np.int32); m.polygons.foreach_get('loop_total', lt)
    lv = np.empty(len(m.loops), np.int64); m.loops.foreach_get('vertex_index', lv)
    lf = np.repeat(np.arange(nf), lt)
    co = np.empty(N * 3); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    nor = np.empty(N * 3); m.vertices.foreach_get('normal', nor); nor = nor.reshape(-1, 3)
    # colisión del cuerpo (una vez)
    if not any(md.type == 'COLLISION' for md in me.modifiers):
        col = me.modifiers.new("Colision", 'COLLISION')
        idx_sub = next(i for i, x in enumerate(me.modifiers) if x.type == 'SUBSURF')
        me.modifiers.move(list(me.modifiers).index(col), idx_sub)
    me.collision.thickness_outer = 0.001; me.collision.thickness_inner = 0.002; me.collision.cloth_friction = 6.0
    me.collision.damping = 0.4
    creados = []
    for lado, l in (("Left", "L"), ("Right", "R")):
        g = me.vertex_groups[P + lado + "Arm"]
        w = _pesos(me, g.index)
        wf = np.zeros(nf); np.add.at(wf, lf, w[lv]); wf /= lt
        caras = np.where((mi == ic) & (wf > 0.40))[0]
        if not len(caras): continue
        vset = np.unique(np.concatenate([np.array(m.polygons[f].vertices) for f in caras]))
        # vértices del borde de costura: los que también tocan caras de camiseta que no son de la manga (hombro/axila)
        en_manga = np.zeros(nf, bool); en_manga[caras] = True
        toca_torso = np.zeros(N, bool); toca_torso[lv[(mi[lf] == ic) & ~en_manga[lf]]] = True
        toca_piel = np.zeros(N, bool); toca_piel[lv[(mi[lf] != ic)]] = True          # bajo de la manga (junto al brazo)
        # --- objeto de la manga
        mapa = {int(v): k for k, v in enumerate(vset)}
        verts = [tuple(co[v] + nor[v] * separacion) for v in vset]
        faces = [[mapa[int(v)] for v in m.polygons[f].vertices] for f in caras]
        nm = f"MAITE_manga_{l}"
        viejo = bpy.data.objects.get(nm)
        if viejo: bpy.data.objects.remove(viejo)
        md_ = bpy.data.meshes.new(nm); md_.from_pydata(verts, [], faces); md_.update()
        md_.materials.append(m.materials[ic])
        uvr = next(u for u in m.uv_layers if u.active_render)
        un = md_.uv_layers.new(name=uvr.name)
        k = 0
        for fi, f in enumerate(caras):
            p = m.polygons[f]
            for li in p.loop_indices:
                un.data[k].uv = uvr.data[li].uv; k += 1
        for p in md_.polygons: p.use_smooth = True
        for na in ("tela_vaquero", "tela_lum"):              # la tela de la manga se pinta igual que en el cuerpo
            if na in m.attributes and m.attributes[na].domain == 'POINT':
                src = np.empty(N, np.float32); m.attributes[na].data.foreach_get('value', src)
                at_ = md_.attributes.new(na, 'FLOAT', 'POINT'); at_.data.foreach_set('value', src[np.array(vset, np.int64)])
        ob = bpy.data.objects.new(nm, md_)
        me.users_collection[0].objects.link(ob)
        ob.parent = me.parent; ob.matrix_parent_inverse = me.matrix_parent_inverse.copy(); ob.matrix_world = me.matrix_world.copy()
        # pesos del esqueleto copiados
        por_grupo = {}
        for i_, v in enumerate(vset):
            for g_ in m.vertices[int(v)].groups:
                if g_.weight > 0.001: por_grupo.setdefault(g_.group, []).append((i_, g_.weight))
        for gidx, lista in por_grupo.items():
            nombre_g = me.vertex_groups[gidx].name
            if nombre_g.startswith("Trenza") or nombre_g == "suave_articulaciones": continue   # la manga no sigue a la trenza
            ng = ob.vertex_groups.new(name=nombre_g)
            for i_, wi in lista: ng.add([i_], float(wi), 'REPLACE')
        # pines: cosida al hombro (1), libre con peso hacia el bajo (0,35)
        b = arm.data.bones[P + lado + "Arm"]
        A = np.array(arm.matrix_world @ b.head_local); B = np.array(arm.matrix_world @ b.tail_local); ab = B - A
        t = np.clip(((co[vset] - A) @ ab) / (ab @ ab), 0, 1)
        t0, t1 = np.percentile(t, 5), np.percentile(t, 95)
        tn = np.clip((t - t0) / max(1e-6, t1 - t0), 0, 1)
        pin = 1.0 - 0.42 * tn ** 1.5
        pin = np.where(toca_torso[vset], 1.0, pin)
        gp = ob.vertex_groups.new(name="pin")
        for i_, wi in enumerate(pin): gp.add([i_], float(wi), 'REPLACE')
        am = ob.modifiers.new("Armature", 'ARMATURE'); am.object = arm
        cl = ob.modifiers.new("Tela", 'CLOTH')
        s = cl.settings
        # algodón a escala del modelo (1 m): masa por vértice pequeña (con 0,12 kg la manga pesaba 55 kg y se caía)
        s.quality = 10; s.mass = 0.0025; s.air_damping = 1.0; s.gravity = (0, 0, -9.81)
        s.tension_stiffness = 15; s.compression_stiffness = 15; s.shear_stiffness = 5; s.bending_stiffness = 0.05
        s.tension_damping = 5; s.compression_damping = 5; s.shear_damping = 5; s.bending_damping = 0.5
        s.vertex_group_mass = "pin"; s.pin_stiffness = 30.0
        s.shrink_min = 0.0
        cl.collision_settings.use_collision = True; cl.collision_settings.distance_min = 0.0012
        cl.collision_settings.collision_quality = 3; cl.collision_settings.use_self_collision = False
        cl.point_cache.frame_start = 1; cl.point_cache.frame_end = 250
        sd = ob.modifiers.new("Sub_render", 'SUBSURF'); sd.levels = 0; sd.render_levels = 1
        # la manga original se encoge hacia el hueso y pasa a piel (el brazo que se ve si la manga se levanta)
        solo_manga = ~toca_torso[vset]
        P_ = co[vset]; q = A + np.outer(t, ab); radial = P_ - q; rl = np.linalg.norm(radial, axis=1)
        nuevo = q + radial / np.maximum(rl, 1e-6)[:, None] * np.maximum(rl - encoger, rl * 0.6)[:, None]
        mover = vset[solo_manga]
        co[mover] = nuevo[solo_manga]
        for f in caras: m.polygons[f].material_index = ip
        # color de piel liso en ese "brazo" (la textura ahí es la de la camiseta, blanca)
        if "mascara_piel" in m.attributes and "piel_lisa" in m.attributes:
            am = m.attributes["mascara_piel"]; ac = m.attributes["piel_lisa"]
            mk = np.empty(N, np.float32); am.data.foreach_get('value', mk)
            cl_ = np.empty(N * 4, np.float32); ac.data.foreach_get('color', cl_); cl_ = cl_.reshape(-1, 4)
            piel_v = np.zeros(N, bool); piel_v[lv[mi[lf] == ip]] = True
            brazo = np.where(piel_v & (w > 0.3) & ~np.isin(np.arange(N), vset))[0]      # piel del brazo junto a la manga
            ref = np.median(cl_[brazo], axis=0) if len(brazo) else np.array([0.80, 0.42, 0.33, 1.0])
            mk[vset[solo_manga]] = 1.0; cl_[vset[solo_manga]] = ref
            am.data.foreach_set('value', mk); ac.data.foreach_set('color', cl_.ravel())
        creados.append(ob)
        print("ROPA manga", l, len(caras), "caras,", len(vset), "vértices; costura", int(toca_torso[vset].sum()), flush=True)
    m.vertices.foreach_set('co', co.ravel())
    # las formas de la cara (shape keys) guardan posiciones absolutas: la base debe seguir igual que la malla
    if m.shape_keys:
        kb = m.shape_keys.key_blocks
        base = np.empty(N * 3); kb[0].data.foreach_get('co', base); base = base.reshape(-1, 3)
        delta = co - base
        for k_ in kb:
            arr = np.empty(N * 3); k_.data.foreach_get('co', arr); arr = arr.reshape(-1, 3) + delta
            k_.data.foreach_set('co', arr.ravel())
    m.update()
    return creados
