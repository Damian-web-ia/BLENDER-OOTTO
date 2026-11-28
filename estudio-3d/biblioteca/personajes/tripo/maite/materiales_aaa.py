# MATERIALES AAA DE MAITE (fase 6) · EKORUEDAS · 28-11-2026
# Se ejecuta desde construir_maite_v2.py después de la cara. Funciones:
#   pelo_aaa(me): el pelo de Tripo es una masa con mechas y brillos PINTADOS en la textura (parece plastilina).
#                 Se baja el contraste de la pintura, se añaden vetas finas que bajan desde la coronilla (en coordenadas
#                 de reposo: no "nadan" al animar) y un brillo anisótropo a lo largo del pelo.
import bpy
import numpy as np


def _sk(sockets, ident):
    return next(x for x in sockets if x.identifier == ident)


def _srgb_a_lineal(c):
    c = np.clip(np.asarray(c, np.float64), 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _color_medio(me, mat_index, img):
    m = me.data; w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    uvl = m.uv_layers.active.data
    luv = np.empty(len(uvl) * 2, np.float32); uvl.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    nf = len(m.polygons); lt = np.empty(nf, np.int32); m.polygons.foreach_get('loop_total', lt)
    mi = np.empty(nf, np.int32); m.polygons.foreach_get('material_index', mi)
    lf = np.repeat(np.arange(nf), lt)
    sel = mi[lf] == mat_index
    s_ = luv[sel]
    c = px[np.clip((s_[:, 1] * h).astype(int), 0, h - 1), np.clip((s_[:, 0] * w).astype(int), 0, w - 1), :3]
    return np.median(c, axis=0), np.percentile(c @ np.array([0.3, 0.55, 0.15]), [10, 50, 90])


def _caras_pelo_en_piel(me, ip_pelo, ojos):
    """Caras con material de piel pero pintadas de pelo (nacimiento del pelo, patillas): pasan a pelo.
    Las cejas no (están junto a los ojos)."""
    m = me.data
    ip_piel = next(i for i, mt in enumerate(m.materials) if mt and mt.name == "MAITE_piel")
    tex = next(n for n in m.materials[ip_piel].node_tree.nodes if n.type == 'TEX_IMAGE' and n.image and n.image.colorspace_settings.name == 'sRGB').image
    w, h = tex.size; px = np.empty(w * h * 4, np.float32); tex.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    uvl = m.uv_layers.active.data
    luv = np.empty(len(uvl) * 2, np.float32); uvl.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    nf = len(m.polygons); lt = np.empty(nf, np.int32); m.polygons.foreach_get('loop_total', lt)
    lf = np.repeat(np.arange(nf), lt)
    fuv = np.zeros((nf, 2)); np.add.at(fuv, lf, luv); fuv /= lt[:, None]
    c = px[np.clip((fuv[:, 1] * h).astype(int), 0, h - 1), np.clip((fuv[:, 0] * w).astype(int), 0, w - 1), :3]
    lum = c @ np.array([0.3, 0.55, 0.15]); rojo = c[:, 0] - c[:, 2]
    mi = np.empty(nf, np.int32); m.polygons.foreach_get('material_index', mi)
    cen = np.empty(nf * 3, np.float64); m.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    cerca_ojo = np.zeros(nf, bool)
    for C in ojos:
        d = cen - np.array(C); cerca_ojo |= (np.abs(d[:, 0]) < 0.034) & (d[:, 2] > -0.02) & (d[:, 2] < 0.040) & (np.linalg.norm(d, axis=1) < 0.05)
    cand = (mi == ip_piel) & (lum < 0.40) & (rojo < 0.22) & ~cerca_ojo & (cen[:, 2] > 0.80)
    # sólo las que tocan pelo (o tocan otras candidatas que tocan pelo): crecer desde el pelo
    vpelo = np.zeros(len(m.vertices), bool)
    lv = np.empty(len(m.loops), np.int64); m.loops.foreach_get('vertex_index', lv)
    vpelo[lv[mi[lf] == ip_pelo]] = True
    cambia = np.zeros(nf, bool)
    for _ in range(6):
        toca = np.zeros(nf, bool); np.logical_or.at(toca, lf, vpelo[lv])
        nuevas = cand & toca & ~cambia
        if not nuevas.any(): break
        cambia |= nuevas; vpelo[lv[cambia[lf]]] = True
    mi[cambia] = ip_pelo; m.polygons.foreach_set('material_index', mi); m.update()
    print("PELO_AAA caras de piel pintadas de pelo -> pelo:", int(cambia.sum()), flush=True)


def pelo_aaa(me, fuerza_pintura=0.30, vetas=170.0, ojos=()):
    m = me.data
    ip = next(i for i, mt in enumerate(m.materials) if mt and mt.name == "MAITE_pelo")
    if ojos: _caras_pelo_en_piel(me, ip, ojos)
    mt = m.materials[ip]; T = mt.node_tree; N = T.nodes; L = T.links
    for n in [n for n in N if n.name.startswith("PELO_")]: N.remove(n)
    bs = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    tex = next(n for n in N if n.type == 'TEX_IMAGE' and n.image and n.image.colorspace_settings.name == 'sRGB')
    hs = next((n for n in N if n.type == 'HUE_SAT'), None)
    med, pct = _color_medio(me, ip, tex.image)
    base_lin = _srgb_a_lineal(med)
    # centro de la cabeza en coordenadas de reposo (Generated × dimensiones, origen en la esquina de la caja)
    co = np.empty(len(m.vertices) * 3, np.float64); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    mi = np.empty(len(m.polygons), np.int32); m.polygons.foreach_get('material_index', mi)
    vs = np.unique(np.concatenate([np.array(p.vertices) for p in m.polygons if p.material_index == ip]))
    P = co[vs]; arriba = P[P[:, 2] > np.percentile(P[:, 2], 40)]
    cabeza = np.array([np.median(arriba[:, 0]), np.median(arriba[:, 1]), arriba[:, 2].max()])
    mn = co.min(0); dims = co.max(0) - mn
    cen = cabeza - mn
    # --- coordenadas: P (reposo, metros) -> ángulo alrededor de la coronilla y altura
    tc = N.new("ShaderNodeTexCoord"); tc.name = "PELO_coord"; tc.location = (-2200, -900)
    vm = N.new("ShaderNodeVectorMath"); vm.name = "PELO_dims"; vm.operation = 'MULTIPLY'; vm.location = (-2000, -900)
    vm.inputs[1].default_value = tuple(dims); L.new(tc.outputs["Generated"], vm.inputs[0])
    vr = N.new("ShaderNodeVectorMath"); vr.name = "PELO_rel"; vr.operation = 'SUBTRACT'; vr.location = (-1800, -900)
    vr.inputs[1].default_value = tuple(cen); L.new(vm.outputs[0], vr.inputs[0])
    sp = N.new("ShaderNodeSeparateXYZ"); sp.name = "PELO_sep"; sp.location = (-1600, -900); L.new(vr.outputs[0], sp.inputs[0])
    at = N.new("ShaderNodeMath"); at.name = "PELO_ang"; at.operation = 'ARCTAN2'; at.location = (-1400, -850)
    L.new(sp.outputs["X"], at.inputs[0]); L.new(sp.outputs["Y"], at.inputs[1])
    ka = N.new("ShaderNodeMath"); ka.name = "PELO_k"; ka.operation = 'MULTIPLY'; ka.inputs[1].default_value = vetas / 6.2832; ka.location = (-1250, -850)
    L.new(at.outputs[0], ka.inputs[0])
    kz = N.new("ShaderNodeMath"); kz.name = "PELO_kz"; kz.operation = 'MULTIPLY'; kz.inputs[1].default_value = 6.0; kz.location = (-1250, -1000)
    L.new(sp.outputs["Z"], kz.inputs[0])
    cb = N.new("ShaderNodeCombineXYZ"); cb.name = "PELO_uv"; cb.location = (-1100, -900)
    L.new(ka.outputs[0], cb.inputs["X"]); L.new(kz.outputs[0], cb.inputs["Y"])
    # vetas: ruido estirado a lo largo del pelo (fino) + mechones (grueso)
    nf_ = N.new("ShaderNodeTexNoise"); nf_.name = "PELO_vetas"; nf_.location = (-900, -850); nf_.noise_dimensions = '2D'
    nf_.inputs["Scale"].default_value = 1.0; nf_.inputs["Detail"].default_value = 3.0; nf_.inputs["Roughness"].default_value = 0.55
    L.new(cb.outputs[0], nf_.inputs["Vector"])
    mg = N.new("ShaderNodeVectorMath"); mg.name = "PELO_grueso_esc"; mg.operation = 'MULTIPLY'; mg.location = (-1000, -1100)
    mg.inputs[1].default_value = (0.18, 0.5, 1.0); L.new(cb.outputs[0], mg.inputs[0])
    ng = N.new("ShaderNodeTexNoise"); ng.name = "PELO_mechones"; ng.location = (-900, -1100); ng.noise_dimensions = '2D'
    ng.inputs["Scale"].default_value = 1.0; ng.inputs["Detail"].default_value = 2.0
    L.new(mg.outputs[0], ng.inputs["Vector"])
    mz = N.new("ShaderNodeMix"); mz.name = "PELO_mezcla_vetas"; mz.data_type = 'FLOAT'; mz.location = (-700, -950)
    _sk(mz.inputs, "Factor_Float").default_value = 0.35
    L.new(nf_.outputs["Fac"], _sk(mz.inputs, "A_Float")); L.new(ng.outputs["Fac"], _sk(mz.inputs, "B_Float"))
    vet = _sk(mz.outputs, "Result_Float")
    # color: menos pintura (mezcla hacia el color medio) y variación por vetas
    mx = N.new("ShaderNodeMix"); mx.name = "PELO_menos_pintura"; mx.data_type = 'RGBA'; mx.location = (-650, 450)
    _sk(mx.inputs, "Factor_Float").default_value = fuerza_pintura
    _sk(mx.inputs, "A_Color").default_value = (*base_lin, 1); L.new(tex.outputs["Color"], _sk(mx.inputs, "B_Color"))
    rm = N.new("ShaderNodeMapRange"); rm.name = "PELO_luz_vetas"; rm.location = (-500, -700)
    rm.inputs["From Min"].default_value = 0.30; rm.inputs["From Max"].default_value = 0.70
    rm.inputs["To Min"].default_value = 0.72; rm.inputs["To Max"].default_value = 1.12; L.new(vet, rm.inputs["Value"])
    mu = N.new("ShaderNodeMix"); mu.name = "PELO_vetas_color"; mu.data_type = 'RGBA'; mu.blend_type = 'MULTIPLY'; mu.location = (-450, 450)
    _sk(mu.inputs, "Factor_Float").default_value = 1.0
    L.new(_sk(mx.outputs, "Result_Color"), _sk(mu.inputs, "A_Color"))
    cr = N.new("ShaderNodeCombineColor"); cr.name = "PELO_gris"; cr.location = (-350, -700)
    for k_ in ("Red", "Green", "Blue"): L.new(rm.outputs["Result"], cr.inputs[k_])
    L.new(cr.outputs["Color"], _sk(mu.inputs, "B_Color"))
    destino = hs.inputs["Color"] if hs else bs.inputs["Base Color"]
    for l in list(destino.links): L.remove(l)
    L.new(_sk(mu.outputs, "Result_Color"), destino)
    # relieve de las vetas encima del mapa de normales de Tripo
    nm = next((n for n in N if n.type == 'NORMAL_MAP'), None)
    if nm: nm.inputs["Strength"].default_value = 0.6
    bu = next((n for n in N if n.type == 'BUMP'), None)
    if bu is None:
        bu = N.new("ShaderNodeBump"); bu.location = (-200, -450)
        if nm: L.new(nm.outputs["Normal"], bu.inputs["Normal"])
        L.new(bu.outputs["Normal"], bs.inputs["Normal"])
    for l in list(bu.inputs["Height"].links): L.remove(l)
    L.new(vet, bu.inputs["Height"]); bu.inputs["Strength"].default_value = 0.22; bu.inputs["Distance"].default_value = 0.0004
    # brillo anisótropo a lo largo del pelo (tangente horizontal alrededor de Z, girada 90°)
    tg = N.new("ShaderNodeTangent"); tg.name = "PELO_tangente"; tg.direction_type = 'RADIAL'; tg.axis = 'Z'; tg.location = (-200, -150)
    L.new(tg.outputs["Tangent"], bs.inputs["Tangent"])
    bs.inputs["Anisotropic"].default_value = 0.75; bs.inputs["Anisotropic Rotation"].default_value = 0.25
    bs.inputs["Specular IOR Level"].default_value = 0.45
    for l in list(bs.inputs["Roughness"].links): L.remove(l)
    rr = N.new("ShaderNodeMapRange"); rr.name = "PELO_rug"; rr.location = (-200, 100)
    rr.inputs["To Min"].default_value = 0.40; rr.inputs["To Max"].default_value = 0.58; L.new(vet, rr.inputs["Value"])
    L.new(rr.outputs["Result"], bs.inputs["Roughness"])
    bs.inputs["Sheen Weight"].default_value = 0.18; bs.inputs["Sheen Roughness"].default_value = 0.4
    bs.inputs["Coat Weight"].default_value = 0.0
    print("PELO_AAA color medio", np.round(med, 3).tolist(), "luminancia p10/50/90", np.round(pct, 3).tolist(),
          "coronilla", np.round(cabeza, 3).tolist(), flush=True)


def piel_aaa(me, poro=0.00055, fuerza_poro=0.16, rug_labios=0.30):
    """Piel para primer plano (va después del maquillaje). Sin esto, en 4K la cara parece de cera:
    - poro fino pegado a la piel (coordenadas de reposo: no 'nada' cuando se mueve), menos en los labios;
    - rugosidad con variación suave y labios algo más brillantes;
    - un moteado de color muy leve, como la piel de verdad."""
    m = me.data
    mt = next(mt for mt in m.materials if mt and mt.name == "MAITE_piel")
    T = mt.node_tree; Nn = T.nodes; Lk = T.links
    for n in [n for n in Nn if n.name.startswith("PIEL_")]: Nn.remove(n)
    bs = next(n for n in Nn if n.type == 'BSDF_PRINCIPLED')
    bump = next(n for n in Nn if n.type == 'BUMP')
    ruido = next(n for n in Nn if n.type == 'TEX_NOISE')
    vm = next(n for n in Nn if n.type == 'VECT_MATH' and n.operation == 'MULTIPLY')      # Generated × medidas = metros
    pos = vm.outputs["Vector"]
    labios = Nn["MAQ_sep"].outputs["Red"] if "MAQ_sep" in Nn else None

    def nodo(tipo, nombre, x, y, **kw):
        n = Nn.new(tipo); n.name = "PIEL_" + nombre; n.label = n.name; n.location = (x, y)
        for k, v in kw.items(): setattr(n, k, v)
        return n

    def mate(nombre, op, a, b, x, y, c=None):
        n = nodo("ShaderNodeMath", nombre, x, y, operation=op)
        for i, v in enumerate((a, b, c)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: Lk.new(v, n.inputs[i])
        return n.outputs[0]

    # --- poro: celdas de Voronoi de medio milímetro; el fondo de cada celda es un hoyito
    vo = nodo("ShaderNodeTexVoronoi", "poro", -1500, -700, feature='F1', distance='EUCLIDEAN')
    vo.inputs["Scale"].default_value = 1.0 / poro; vo.inputs["Randomness"].default_value = 1.0
    Lk.new(pos, vo.inputs["Vector"])
    mr = nodo("ShaderNodeMapRange", "poro_forma", -1300, -700, interpolation_type='SMOOTHSTEP')
    mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = 0.32
    Lk.new(vo.outputs["Distance"], mr.inputs["Value"])
    alto = mate("alto", 'MULTIPLY_ADD', mr.outputs["Result"], 0.65, -1100, -700, c=None)
    # alto = poro*0.65 + ruido*0.35
    ru = mate("ruido_k", 'MULTIPLY', ruido.outputs["Fac"], 0.35, -1100, -850)
    Lk.new(ru, Nn["PIEL_alto"].inputs[2])
    for l in list(bump.inputs["Height"].links): Lk.remove(l)
    Lk.new(alto, bump.inputs["Height"])
    bump.inputs["Distance"].default_value = 0.00018
    # fuerza: menos en los labios (son lisos)
    if labios is not None:
        menos = mate("fuerza", 'MULTIPLY_ADD', labios, -0.85 * fuerza_poro, -900, -560, c=fuerza_poro)
        Lk.new(menos, bump.inputs["Strength"])
    else:
        bump.inputs["Strength"].default_value = fuerza_poro

    # --- rugosidad: variación lenta (zonas algo más grasas y más secas) y labios más brillantes
    rs = bs.inputs["Roughness"]; ant = rs.links[0].from_socket if rs.is_linked else None
    lento = nodo("ShaderNodeTexNoise", "lento", -1500, -250); lento.inputs["Scale"].default_value = 1.0 / 0.018
    lento.inputs["Detail"].default_value = 3.0; Lk.new(pos, lento.inputs["Vector"])
    var = mate("var", 'MULTIPLY_ADD', lento.outputs["Fac"], 0.30, -1300, -250, c=0.85)          # 0,85 .. 1,15
    r1 = mate("rug_var", 'MULTIPLY', ant if ant is not None else rs.default_value, var, -1100, -250)
    if labios is not None:
        mezcla = nodo("ShaderNodeMix", "rug_labios", -900, -250, data_type='FLOAT')
        fl = mate("labios_k", 'MULTIPLY', labios, 0.85, -1100, -120)
        Lk.new(fl, _sk(mezcla.inputs, "Factor_Float")); Lk.new(r1, _sk(mezcla.inputs, "A_Float"))
        _sk(mezcla.inputs, "B_Float").default_value = rug_labios
        r1 = _sk(mezcla.outputs, "Result_Float")
    for l in list(rs.links): Lk.remove(l)
    Lk.new(r1, rs)

    # --- moteado de color muy leve (sólo oscurece un 0-3 %)
    bc = bs.inputs["Base Color"]
    if bc.is_linked:
        prev = bc.links[0].from_socket
        mo = nodo("ShaderNodeTexNoise", "moteado", -1500, 200); mo.inputs["Scale"].default_value = 1.0 / 0.009
        mo.inputs["Detail"].default_value = 4.0; Lk.new(pos, mo.inputs["Vector"])
        cr = nodo("ShaderNodeValToRGB", "moteado_rampa", -1300, 200)
        cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = (0.955, 0.925, 0.925, 1)
        cr.color_ramp.elements[1].position = 0.65; cr.color_ramp.elements[1].color = (1, 1, 1, 1)
        Lk.new(mo.outputs["Fac"], cr.inputs["Fac"])
        mx = nodo("ShaderNodeMix", "moteado_mezcla", -300, 300, data_type='RGBA', blend_type='MULTIPLY')
        _sk(mx.inputs, "Factor_Float").default_value = 0.8
        Lk.new(prev, _sk(mx.inputs, "A_Color")); Lk.new(cr.outputs["Color"], _sk(mx.inputs, "B_Color"))
        for l in list(bc.links): Lk.remove(l)
        Lk.new(_sk(mx.outputs, "Result_Color"), bc)
    print("PIEL_AAA poro", poro, "fuerza", fuerza_poro, flush=True)
