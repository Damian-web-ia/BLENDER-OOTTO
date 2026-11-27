# FILTRO DE ACEITE (cartucho roscado) por código · EKORUEDAS · 27-11-2026
# Medidas reales aproximadas: lata de 76 mm de diámetro y 90 mm de alto. Origen en el centro de la placa base; Z hacia la cúpula.
# Por dentro: placa base con 6 agujeros de entrada alrededor y la rosca central de salida, junta tórica, válvula antirretorno
# de goma (tapa los agujeros cuando el motor se para), papel filtrante plisado entre dos tapas de chapa, tubo central
# perforado, válvula de derivación (bypass) arriba con su muelle, y el aceite: sucio fuera del papel, limpio en el centro.
# Uso: FA = {"__name__": "fa"}; exec(open(".../filtro_aceite_real.py", encoding="utf-8").read(), FA)
#      O = FA["construir_filtro"](coleccion, MP, "FIL", interior=True)
import bpy, bmesh, math, random
from mathutils import Vector

R_LATA, H_LATA = 0.038, 0.090
R_AGU, N_AGU, RA = 0.022, 6, 0.0042          # agujeros de entrada
R_PAP0, R_PAP1, Z_PAP0, Z_PAP1, N_PLI = 0.0185, 0.0312, 0.0125, 0.0735, 60
R_TUBO = 0.0172
Z_TAPA_SUP = 0.0755
Z_ACEITE1 = 0.084

def _obj(nombre, bm, mats, col, padre, liso=True, angulo=35):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = liso
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(nombre, me); col.objects.link(o); o.parent = padre
    if liso:
        md = o.modifiers.new("aristas", 'EDGE_SPLIT'); md.split_angle = math.radians(angulo)
    return o

def torno(bm, perfil, seg=72, cerrar=True):
    """Gira un perfil cerrado (r, z) alrededor de Z."""
    vs = [bm.verts.new((r, 0, z)) for r, z in perfil]
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs) if cerrar else len(vs) - 1)]
    res = bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.tau, steps=seg, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

def _cil(bm, c, r, z0, z1, seg=24):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
    for v in res["verts"]: v.co += Vector((c[0], c[1], (z0 + z1) / 2))

def _salida(nt): return [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]

def papel(nombre, sucio=None):
    """Papel filtrante de celulosa (crema, fibra fina). 'sucio' None = sigue la propiedad de escena 'sucio'; si no, valor fijo."""
    m = bpy.data.materials.new(nombre); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.88; b.inputs["Subsurface Weight"].default_value = 0.15
    b.inputs["Subsurface Radius"].default_value = (0.004, 0.003, 0.002)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1400.0; nz.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.0002
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 260.0; nz2.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    if sucio is None:
        at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'VIEW_LAYER'; at.attribute_name = "sucio"; fac = at.outputs["Fac"]
    else:
        v = nt.nodes.new("ShaderNodeValue"); v.outputs[0].default_value = sucio; fac = v.outputs[0]
    # el atasco aparece a manchas que crecen (umbral del ruido que baja con 'sucio')
    rg = nt.nodes.new("ShaderNodeMapRange"); rg.clamp = True
    nt.links.new(nz2.outputs["Fac"], rg.inputs["Value"]); rg.inputs["From Min"].default_value = 0.25; rg.inputs["From Max"].default_value = 0.55
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 1.8; mul.use_clamp = True
    nt.links.new(fac, mul.inputs[0])
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'MULTIPLY'; ad.use_clamp = True
    nt.links.new(rg.outputs["Result"], ad.inputs[0]); nt.links.new(mul.outputs[0], ad.inputs[1])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(ad.outputs[0], mx.inputs[0]); mx.inputs[6].default_value = (0.80, 0.66, 0.40, 1); mx.inputs[7].default_value = (0.045, 0.032, 0.02, 1)
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    return m

def perforado(nombre, MP):
    """Chapa perforada (tubo central): agujeros redondos con transparencia."""
    m = MP["acero"](nombre, color=(0.62, 0.63, 0.65), rugo=(0.2, 0.35), anillos=False)
    nt = m.node_tree; out = _salida(nt); src = out.inputs["Surface"].links[0].from_socket
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    at2 = nt.nodes.new("ShaderNodeMath"); at2.operation = 'ARCTAN2'
    nt.links.new(sp.outputs["Y"], at2.inputs[0]); nt.links.new(sp.outputs["X"], at2.inputs[1])
    cb = nt.nodes.new("ShaderNodeCombineXYZ")
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = 0.0172 * 1.0
    nt.links.new(at2.outputs[0], mu.inputs[0]); nt.links.new(mu.outputs[0], cb.inputs["X"]); nt.links.new(sp.outputs["Z"], cb.inputs["Y"])
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 160.0; vo.inputs["Randomness"].default_value = 0.0
    nt.links.new(cb.outputs[0], vo.inputs["Vector"])
    lt = nt.nodes.new("ShaderNodeMath"); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.30
    nt.links.new(vo.outputs["Distance"], lt.inputs[0])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lt.outputs[0], mx.inputs[0]); nt.links.new(src, mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    return m

def materiales(MP, pref="FIL"):
    M = {}
    M["lata"] = MP["pintura"](pref + "_Lata", color=(0.012, 0.05, 0.20), rugo=0.3, barniz=0.8, piel_naranja=0.02, metal=0.35)
    M["placa"] = MP["acero"](pref + "_Placa", color=(0.55, 0.56, 0.58), rugo=(0.18, 0.34), anillos=True)
    M["chapa"] = MP["acero"](pref + "_Chapa", color=(0.66, 0.67, 0.69), rugo=(0.22, 0.36), anillos=False)
    M["perforado"] = perforado(pref + "_Perforado", MP)
    M["goma"] = MP["goma"](pref + "_Goma")
    M["papel"] = papel(pref + "_Papel")
    M["sucio"] = MP["aceite"](pref + "_AceiteSucio", color=(0.20, 0.11, 0.035), calor=False)
    M["limpio"] = MP["aceite"](pref + "_AceiteLimpio", color=(0.98, 0.72, 0.24), calor=False)
    m = bpy.data.materials.new(pref + "_Mugre"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.03, 0.022, 0.015, 1); b.inputs["Roughness"].default_value = 0.6
    M["mugre"] = m
    m = bpy.data.materials.new(pref + "_Brillo"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (1.0, 0.75, 0.3, 1); b.inputs["Emission Color"].default_value = (1.0, 0.72, 0.25, 1)
    b.inputs["Emission Strength"].default_value = 18.0
    M["brillo"] = m
    m = bpy.data.materials.new(pref + "_Alarma"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.05, 0.02, 0.01, 1); b.inputs["Emission Color"].default_value = (1.0, 0.12, 0.05, 1)
    b.inputs["Emission Strength"].default_value = 6.0
    M["alarma"] = m
    return M

def plisado(bm, r0, r1, z0, z1, n, grosor=0.00045):
    """Papel plisado: zigzag entre r0 y r1 (n pliegues) con grosor real."""
    pts = []
    for i in range(2 * n):
        a = math.tau * i / (2 * n); r = r1 if i % 2 == 0 else r0
        pts.append((r * math.cos(a), r * math.sin(a)))
    abajo = [bm.verts.new((x, y, z0)) for x, y in pts]; arriba = [bm.verts.new((x, y, z1)) for x, y in pts]
    caras = []
    for i in range(len(pts)):
        j = (i + 1) % len(pts); caras.append(bm.faces.new((abajo[i], abajo[j], arriba[j], arriba[i])))
    bmesh.ops.recalc_face_normals(bm, faces=caras)
    bmesh.ops.solidify(bm, geom=caras, thickness=grosor)

def construir_filtro(col, MP, pref="FIL", interior=True, solo_elemento=False, papel_sucio=None):
    M = materiales(MP, pref)
    if papel_sucio is not None: M["papel"] = papel(pref + "_PapelFijo", sucio=papel_sucio)
    raiz = bpy.data.objects.new(pref, None); col.objects.link(raiz); raiz.empty_display_size = 0.05
    O = {"raiz": raiz, "M": M}
    # ---- elemento: papel plisado + tapas de chapa (sirve también solo, para el inserto)
    bm = bmesh.new(); plisado(bm, R_PAP0, R_PAP1, Z_PAP0, Z_PAP1, N_PLI)
    O["papel"] = _obj(pref + "_Papel", bm, [M["papel"]], col, raiz, liso=False)
    bm = bmesh.new()
    for z0, z1 in ((Z_PAP0 - 0.0012, Z_PAP0), (Z_PAP1, Z_PAP1 + 0.0012)):
        torno(bm, [(R_TUBO, z0), (R_PAP1 + 0.0012, z0), (R_PAP1 + 0.0012, z1), (R_TUBO, z1)])
    O["tapas"] = _obj(pref + "_Tapas", bm, [M["chapa"]], col, raiz)
    bm = bmesh.new(); torno(bm, [(R_TUBO - 0.0005, Z_PAP0 - 0.0012), (R_TUBO, Z_PAP0 - 0.0012), (R_TUBO, Z_PAP1 + 0.0012), (R_TUBO - 0.0005, Z_PAP1 + 0.0012)], seg=64)
    O["tubo"] = _obj(pref + "_Tubo", bm, [M["perforado"]], col, raiz)
    if solo_elemento: return O
    # ---- placa base con agujeros (de chapa gruesa) y cuello roscado
    bm = bmesh.new()
    torno(bm, [(0.0102, -0.0005), (0.036, -0.0005), (0.036, 0.0045), (0.0102, 0.0045)], seg=96)
    O["placa"] = _obj(pref + "_Placa", bm, [M["placa"]], col, raiz)
    bm = bmesh.new()
    for k in range(N_AGU):
        a = math.tau * (k + 0.5) / N_AGU; _cil(bm, (R_AGU * math.cos(a), R_AGU * math.sin(a)), RA, -0.0006, 0.0046, seg=24)
    O["agujeros"] = _obj(pref + "_Agujeros", bm, [M["mugre"]], col, raiz)
    O["angulos_agujeros"] = [math.tau * (k + 0.5) / N_AGU for k in range(N_AGU)]
    perfil = [(0.0095, -0.010)]
    for i in range(7):                  # rosca (anillos) del cuello central
        z = -0.010 + i * 0.0018; perfil += [(0.0118, z + 0.0004), (0.0118, z + 0.0009), (0.0110, z + 0.0014)]
    perfil += [(0.0110, 0.006), (0.0095, 0.006)]
    bm = bmesh.new(); torno(bm, perfil, seg=72); O["cuello"] = _obj(pref + "_Cuello", bm, [M["placa"]], col, raiz)
    bm = bmesh.new(); torno(bm, [(0.0285 + 0.0028 * math.cos(t), -0.0018 + 0.0022 * math.sin(t)) for t in [i * math.tau / 16 for i in range(16)]], seg=96)
    O["junta"] = _obj(pref + "_Junta", bm, [M["goma"]], col, raiz)
    # ---- lata: pared fina con cúpula y reborde engatillado abajo
    pf = [(0.0372, 0.0045), (R_LATA, 0.0045), (R_LATA, 0.080)]
    for i in range(1, 10):
        t = i / 10 * math.pi / 2; pf.append((R_LATA * math.cos(t) * 0.98 + 0.0008, 0.080 + 0.010 * math.sin(t)))
    pf += [(0.0, H_LATA), (0.0, H_LATA - 0.0008)]
    for i in range(9, 0, -1):
        t = i / 10 * math.pi / 2; pf.append(((R_LATA - 0.0008) * math.cos(t) * 0.98 + 0.0008, 0.080 + 0.0092 * math.sin(t)))
    pf += [(0.0372, 0.080)]
    bm = bmesh.new(); torno(bm, pf, seg=96); O["lata"] = _obj(pref + "_Lata", bm, [M["lata"]], col, raiz, angulo=50)
    bm = bmesh.new(); torno(bm, [(0.0372 + 0.0026 * math.cos(t), 0.0055 + 0.0030 * math.sin(t)) for t in [i * math.tau / 16 for i in range(16)]], seg=96)
    O["reborde"] = _obj(pref + "_Reborde", bm, [M["lata"]], col, raiz)
    if not interior: return O
    # ---- válvula antirretorno (goma): anillo que tapa los agujeros por dentro; forma "abierta" = el borde se levanta
    bm = bmesh.new(); torno(bm, [(0.0125, 0.0046), (0.0300, 0.0046), (0.0300, 0.0062), (0.0125, 0.0062)], seg=96)
    O["antirretorno"] = o = _obj(pref + "_Antirretorno", bm, [M["goma"]], col, raiz)
    o.shape_key_add(name="Basis", from_mix=False); kb = o.shape_key_add(name="abierta", from_mix=False)
    for i, v in enumerate(o.data.vertices):
        r = math.hypot(v.co.x, v.co.y)
        if r > 0.0165: kb.data[i].co.z = v.co.z + (r - 0.0165) / (0.0300 - 0.0165) * 0.0055
    # ---- válvula de derivación: disco en la tapa de arriba con su muelle (abre hacia abajo)
    bm = bmesh.new(); torno(bm, [(0.0, Z_TAPA_SUP), (0.0085, Z_TAPA_SUP), (0.0085, Z_TAPA_SUP + 0.0016), (0.0, Z_TAPA_SUP + 0.0016)], seg=48)
    O["bypass"] = _obj(pref + "_Bypass", bm, [M["chapa"]], col, raiz)
    bm = bmesh.new(); torno(bm, [(0.0, Z_TAPA_SUP + 0.0016), (0.0035, Z_TAPA_SUP + 0.0016), (0.0035, Z_TAPA_SUP + 0.0034), (0.0, Z_TAPA_SUP + 0.0034)], seg=32)
    _obj(pref + "_BypassBoton", bm, [M["goma"]], col, O["bypass"])
    cu = bpy.data.curves.new(pref + "_MuelleC", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.00065; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); N_ = 120; sp.points.add(N_ - 1)
    for j in range(N_):
        a = j / (N_ - 1) * math.tau * 3.5; z = Z_TAPA_SUP + 0.0034 + 0.0085 * j / (N_ - 1)
        sp.points[j].co = (0.0125 * math.cos(a), 0.0125 * math.sin(a), z, 1)
    mu = bpy.data.objects.new(pref + "_Muelle", cu); col.objects.link(mu); mu.parent = raiz; cu.materials.append(M["chapa"])
    O["muelle"] = mu
    # ---- aceite: sucio alrededor del papel y arriba; limpio dentro del tubo
    bm = bmesh.new(); torno(bm, [(R_PAP1 + 0.0004, 0.0063), (R_LATA - 0.0009, 0.0063), (R_LATA - 0.0009, Z_ACEITE1), (0.0, Z_ACEITE1),
                                 (0.0, Z_PAP1 + 0.0014), (R_PAP1 + 0.0004, Z_PAP1 + 0.0014)], seg=96)
    O["aceite_sucio"] = _obj(pref + "_AceiteSucio", bm, [M["sucio"]], col, raiz)
    bm = bmesh.new(); torno(bm, [(0.0, 0.0045), (R_TUBO - 0.0006, 0.0045), (R_TUBO - 0.0006, Z_PAP1), (0.0, Z_PAP1)], seg=64)
    O["aceite_limpio"] = _obj(pref + "_AceiteLimpio", bm, [M["limpio"]], col, raiz)
    return O

def _keys_vis(o, f0, f1):
    for ff, v in ((1, False), (f0, True), (f1, False)):
        o.hide_render = o.hide_viewport = not v; o.keyframe_insert("hide_render", frame=ff); o.keyframe_insert("hide_viewport", frame=ff)

def granos_sucios(col, padre, M, angulos, f0, f1, n=70, semilla=4, pref="FIL"):
    """Granos de suciedad: entran por los agujeros, suben por fuera del papel y se quedan pegados en él (mitad de atrás)."""
    rnd = random.Random(semilla); obs = []
    for i in range(n):
        bm = bmesh.new(); r = rnd.uniform(0.0005, 0.0011); res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in res["verts"]: v.co = Vector((v.co.x * rnd.uniform(0.7, 1.3), v.co.y * rnd.uniform(0.7, 1.3), v.co.z * rnd.uniform(0.7, 1.3)))
        o = _obj(f"{pref}_Grano{i}", bm, [M["mugre"]], col, padre, liso=False)
        a0 = [a for a in angulos if 0.15 < (a % math.tau) < math.pi - 0.15]
        a = rnd.choice(a0) if a0 else rnd.uniform(0.3, 2.8)
        a_fin = rnd.uniform(0.25, math.pi - 0.25)
        zf = rnd.uniform(Z_PAP0 + 0.004, Z_PAP1 - 0.004)
        fs = f0 + int(i * (f1 - f0 - 40) / n)
        def P(rr, aa, zz): return (rr * math.cos(aa), rr * math.sin(aa), zz)
        pasos = [(fs, P(R_AGU, a, -0.004)), (fs + 6, P(R_AGU, a, 0.007)), (fs + 14, P(0.0345, (a + a_fin) / 2, zf * 0.6)),
                 (fs + 22, P(0.0335, a_fin, zf)), (fs + 30, P(R_PAP1 + 0.0009, a_fin, zf))]
        for ff, p_ in pasos: o.location = p_; o.keyframe_insert("location", frame=ff)
        _keys_vis(o, fs, 100000)
        obs.append(o)
    return obs

def chispas_limpias(col, padre, M, f0, f1, n=26, semilla=6, pref="FIL", periodo=40):
    """Aceite limpio: puntitos dorados que salen del papel hacia el centro, bajan por el tubo y salen por la rosca."""
    rnd = random.Random(semilla); obs = []
    for i in range(n):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.0007)
        o = _obj(f"{pref}_Limpio{i}", bm, [M["brillo"]], col, padre)
        a = rnd.uniform(0.3, math.pi - 0.3); z0 = rnd.uniform(Z_PAP0 + 0.005, Z_PAP1 - 0.005); fase = rnd.randrange(periodo)
        f = f0 - periodo + fase
        while f < f1:
            pts = [(0, (R_PAP0 * math.cos(a), R_PAP0 * math.sin(a), z0)), (10, (0.006 * math.cos(a), 0.006 * math.sin(a), z0 - 0.004)),
                   (periodo - 1, (0.0015 * math.cos(a), 0.0015 * math.sin(a), -0.016))]
            for df, p_ in pts:
                if f + df >= 1: o.location = p_; o.keyframe_insert("location", frame=f + df)
            f += periodo
        _keys_vis(o, f0, f1)
        obs.append(o)
    return obs

def chorro_bypass(col, padre, M, f0, f1, n=40, semilla=8, pref="FIL", periodo=26):
    """Sin filtrar: granos de suciedad que bajan por la válvula de derivación y salen directos por la rosca."""
    rnd = random.Random(semilla); obs = []
    for i in range(n):
        bm = bmesh.new(); r = rnd.uniform(0.0005, 0.001); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        o = _obj(f"{pref}_SinFiltrar{i}", bm, [M["mugre"]], col, padre, liso=False)
        a = rnd.uniform(0.2, math.pi - 0.2); rr = rnd.uniform(0.012, 0.030); fase = rnd.randrange(periodo)
        f = f0 - periodo + fase
        while f < f1:
            pts = [(0, (rr * math.cos(a), rr * math.sin(a), Z_ACEITE1 - 0.002)), (8, (0.003 * math.cos(a), 0.003 * math.sin(a), Z_TAPA_SUP + 0.001)),
                   (periodo - 1, (0.002 * math.cos(a), 0.002 * math.sin(a), -0.018))]
            for df, p_ in pts:
                if f + df >= 1: o.location = p_; o.keyframe_insert("location", frame=f + df)
            f += periodo
        _keys_vis(o, f0, f1)
        obs.append(o)
    return obs
