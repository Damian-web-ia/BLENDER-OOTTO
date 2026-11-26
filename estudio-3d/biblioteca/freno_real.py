# FRENO DE DISCO REALISTA (26-11-2026) · disco ventilado con aletas, pinza flotante de un pistón, pastillas con placa,
# soporte, guías con fuelles, buje con espárragos, latiguillo con líquido. Eje del disco = Z local; la pinza está en +X;
# lado interior (pistón) = -Z, lado de la rueda = +Z. Medidas en metros (disco de 300 mm).
import bpy, bmesh, math
import numpy as np
from mathutils import Vector, Matrix

R_IN, R_OUT = 0.090, 0.150          # anillos de fricción
T_ANILLO, HUECO = 0.009, 0.011      # grosor de cada anillo y canal entre ellos (disco de 29 mm)
Z_IN = -(HUECO / 2 + T_ANILLO)      # cara interior del disco
Z_OUT = HUECO / 2 + T_ANILLO        # cara exterior
FRIC = 0.011; PLACA = 0.005; SHIM = 0.0012
PAD_A = 26.0; PAD_R = (0.098, 0.147)

# ---------------------------------------------------------------- materiales
def _p(m): return m.node_tree.nodes.get("Principled BSDF")
def _nuevo(nombre, color, rough, metal=0.0, coat=0.0):
    m = bpy.data.materials.get(nombre)
    if m: return m, False
    m = bpy.data.materials.new(nombre); m.use_nodes = True; b = _p(m)
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if coat and "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = coat
    return m, True
def _bump(m, tipo, escala, fuerza, dist=0.0002):
    nt = m.node_tree; b = _p(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if tipo == "anillos":
        tx = nt.nodes.new("ShaderNodeTexWave"); tx.wave_type = 'RINGS'
        try: tx.rings_direction = 'Z'
        except Exception: pass
        tx.inputs["Scale"].default_value = escala; tx.inputs["Distortion"].default_value = 0.6
        nt.links.new(tc.outputs["Object"], tx.inputs["Vector"]); src = tx.outputs["Fac"]
    else:
        tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = escala; tx.inputs["Detail"].default_value = 8
        nt.links.new(tc.outputs["Object"], tx.inputs["Vector"]); src = tx.outputs["Fac"]
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = fuerza; bp.inputs["Distance"].default_value = dist
    nt.links.new(src, bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
def _prop(nt, nombre):
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'VIEW_LAYER'; at.attribute_name = nombre; return at.outputs["Fac"]

def materiales_freno():
    M = {}
    # disco: fundición mecanizada (anillos finos) + calor (incandescente en la pista de las pastillas, propiedad "calor")
    m, n = _nuevo("F_Disco", (0.20, 0.20, 0.205), 0.38, 0.9)
    if n:
        _bump(m, "anillos", 900, 0.18)
        nt = m.node_tree; b = _p(m)
        tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
        sq = nt.nodes.new("ShaderNodeVectorMath"); sq.operation = 'LENGTH'
        cxy = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(sep.outputs[0], cxy.inputs[0]); nt.links.new(sep.outputs[1], cxy.inputs[1])
        nt.links.new(cxy.outputs[0], sq.inputs[0])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.interpolation_type = 'SMOOTHERSTEP'
        mr.inputs["From Min"].default_value = 0.092; mr.inputs["From Max"].default_value = 0.122; mr.inputs["To Min"].default_value = 0; mr.inputs["To Max"].default_value = 1
        nt.links.new(sq.outputs["Value"], mr.inputs["Value"])
        mr2 = nt.nodes.new("ShaderNodeMapRange"); mr2.interpolation_type = 'SMOOTHERSTEP'
        mr2.inputs["From Min"].default_value = 0.151; mr2.inputs["From Max"].default_value = 0.138; mr2.inputs["To Min"].default_value = 0; mr2.inputs["To Max"].default_value = 1
        nt.links.new(sq.outputs["Value"], mr2.inputs["Value"])
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; nt.links.new(mr.outputs["Result"], mul.inputs[0]); nt.links.new(mr2.outputs["Result"], mul.inputs[1])
        mul2 = nt.nodes.new("ShaderNodeMath"); mul2.operation = 'MULTIPLY'; nt.links.new(mul.outputs[0], mul2.inputs[0]); nt.links.new(_prop(nt, "calor"), mul2.inputs[1])
        bb = nt.nodes.new("ShaderNodeBlackbody"); bb.inputs["Temperature"].default_value = 980
        nt.links.new(bb.outputs[0], b.inputs["Emission Color"])
        st = nt.nodes.new("ShaderNodeMath"); st.operation = 'MULTIPLY'; st.inputs[1].default_value = 3.2
        nt.links.new(mul2.outputs[0], st.inputs[0]); nt.links.new(st.outputs[0], b.inputs["Emission Strength"])
    M["disco"] = m
    m, n = _nuevo("F_Campana", (0.10, 0.10, 0.105), 0.55, 0.55)
    if n: _bump(m, "ruido", 600, 0.25)
    M["campana"] = m
    m, n = _nuevo("F_Fundicion", (0.16, 0.16, 0.165), 0.62, 0.65)
    if n: _bump(m, "ruido", 380, 0.45)
    M["fundicion"] = m
    m, n = _nuevo("F_PinzaRoja", (0.62, 0.025, 0.02), 0.28, 0.0, coat=0.7)
    if n: _bump(m, "ruido", 260, 0.12)
    M["pinza"] = m
    m, n = _nuevo("F_Cromo", (0.85, 0.86, 0.88), 0.07, 1.0); M["cromo"] = m
    m, n = _nuevo("F_Acero", (0.72, 0.72, 0.74), 0.32, 1.0); M["acero"] = m
    m, n = _nuevo("F_Laton", (0.75, 0.55, 0.25), 0.3, 1.0); M["laton"] = m
    m, n = _nuevo("F_Goma", (0.018, 0.018, 0.02), 0.62)
    if n: _bump(m, "ruido", 900, 0.15)
    M["goma"] = m
    m, n = _nuevo("F_Friccion", (0.065, 0.058, 0.052), 0.88)
    if n: _bump(m, "ruido", 1600, 0.6)
    M["friccion"] = m
    m, n = _nuevo("F_PlacaNegra", (0.02, 0.02, 0.022), 0.45, 0.2, coat=0.2); M["placa"] = m
    m, n = _nuevo("F_Liquido", (0.05, 0.35, 0.9), 0.2)
    if n:
        nt = m.node_tree; b = _p(m)
        tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
        nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
        wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'; wv.inputs["Scale"].default_value = 6.0
        nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
        cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.55; cr.color_ramp.elements[1].position = 0.9
        nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"])
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 14.0
        nt.links.new(cr.outputs["Color"], mul.inputs[0])
        mul2 = nt.nodes.new("ShaderNodeMath"); mul2.operation = 'MULTIPLY'; nt.links.new(mul.outputs[0], mul2.inputs[0]); nt.links.new(_prop(nt, "flujo_luz"), mul2.inputs[1])
        b.inputs["Emission Color"].default_value = (0.12, 0.55, 1.0, 1); nt.links.new(mul2.outputs[0], b.inputs["Emission Strength"])
        m["mapping"] = mp.name
    M["liquido"] = m
    m, n = _nuevo("F_Aire", (0.6, 0.85, 1.0), 0.3)
    if n:
        nt = m.node_tree; b = _p(m); b.inputs["Emission Color"].default_value = (0.45, 0.8, 1.0, 1); b.inputs["Emission Strength"].default_value = 6.0
        out = [x for x in nt.nodes if x.type == 'OUTPUT_MATERIAL'][0]
        tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
        inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        nt.links.new(_prop(nt, "aire"), inv.inputs[1]); nt.links.new(inv.outputs[0], mx.inputs[0])
        nt.links.new(b.outputs[0], mx.inputs[2]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(mx.outputs[0], out.inputs["Surface"])
        for a, v in (("surface_render_method", 'BLENDED'), ("blend_method", 'BLEND')):
            try: setattr(m, a, v)
            except Exception: pass
    M["aire"] = m
    return M

# ---------------------------------------------------------------- utilidades de malla
def _malla(nombre, V, F, m, liso=True, col=None, padre=None, loc=(0, 0, 0), recalc=True):
    me = bpy.data.meshes.new(nombre); me.from_pydata([tuple(v) for v in V], [], [tuple(f) for f in F]); me.update(calc_edges=True)
    if recalc:
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    if m: me.materials.append(m)
    o = bpy.data.objects.new(nombre, me); (col or bpy.context.scene.collection).objects.link(o); o.location = loc
    if padre: o.parent = padre
    if liso: me.shade_smooth()
    return o
def _bisel(o, w, seg=3):
    md = o.modifiers.new("Bisel", "BEVEL"); md.width = w; md.segments = seg; md.limit_method = 'ANGLE'
    try: md.harden_normals = True
    except Exception: pass
    return md
def extruir(nombre, poly, z0, z1, m, col=None, padre=None, bisel=0.0, liso=False):
    """Prisma de un polígono 2D (lista (x, y), sentido antihorario) entre z0 y z1."""
    n = len(poly); V = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    F = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    o = _malla(nombre, V, F, m, liso=liso, col=col, padre=padre)
    if bisel: _bisel(o, bisel)
    return o
def sector(r0, r1, a0, a1, n=24):
    """Contorno de un sector de corona (ángulos en grados)."""
    A = np.radians(np.linspace(a0, a1, n)); out = [(r1 * math.cos(a), r1 * math.sin(a)) for a in A]
    out += [(r0 * math.cos(a), r0 * math.sin(a)) for a in A[::-1]]
    return out
def corona(nombre, r0, r1, z0, z1, m, seg=128, col=None, padre=None):
    lazo = [(z0, r0), (z0, r1), (z1, r1), (z1, r0)]
    return revolucion(nombre, lazo, m, seg, col, padre)
def revolucion(nombre, lazo, m, seg=96, col=None, padre=None):
    lazo = np.asarray(lazo, float); K = len(lazo); th = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    V = np.stack([lazo[None, :, 1] * np.cos(th)[:, None], lazo[None, :, 1] * np.sin(th)[:, None], np.broadcast_to(lazo[None, :, 0], (seg, K))], -1).reshape(-1, 3)
    i = np.arange(seg)[:, None]; k = np.arange(K)[None, :]; i2 = (i + 1) % seg; k2 = (k + 1) % K
    F = np.stack([i * K + k, i * K + k2, i2 * K + k2, i2 * K + k], -1).reshape(-1, 4)
    o = _malla(nombre, V.tolist(), F.tolist(), m, liso=True, col=col, padre=padre)
    return o
def cil(nombre, c, r, h, m, eje='Z', seg=32, col=None, padre=None, bisel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me); (col or bpy.context.scene.collection).objects.link(o)
    o.location = c; o.rotation_euler = {'Z': (0, 0, 0), 'X': (0, math.radians(90), 0), 'Y': (math.radians(90), 0, 0)}[eje]
    if padre: o.parent = padre
    me.materials.append(m)
    for p in me.polygons: p.use_smooth = len(p.vertices) == 4
    if bisel: _bisel(o, bisel, 2)
    return o
def caja(nombre, x0, x1, y0, y1, z0, z1, m, bisel=0.004, col=None, padre=None):
    return extruir(nombre, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, m, col, padre, bisel)
def tubo(nombre, puntos, r, m, lados=16, col=None, padre=None, uv=True):
    P = [Vector(p) for p in puntos]; n_ = len(P)
    T = [(P[min(i + 1, n_ - 1)] - P[max(i - 1, 0)]).normalized() for i in range(n_)]
    up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0)); nn = (up - T[0] * up.dot(T[0])).normalized()
    V = []; F = []; L = [0.0]
    for i in range(1, n_): L.append(L[-1] + (P[i] - P[i - 1]).length)
    for i in range(n_):
        nn = (nn - T[i] * nn.dot(T[i])).normalized(); bb = T[i].cross(nn)
        for k in range(lados):
            a = 2 * math.pi * k / lados; V.append(P[i] + (nn * math.cos(a) + bb * math.sin(a)) * r)
    for i in range(n_ - 1):
        for k in range(lados):
            k2 = (k + 1) % lados; F.append((i * lados + k, i * lados + k2, (i + 1) * lados + k2, (i + 1) * lados + k))
    o = _malla(nombre, V, F, m, True, col, padre)
    if uv:
        me = o.data; ul = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for li in poly.loop_indices:
                vi = me.loops[li].vertex_index; i = vi // lados; k = vi % lados
                ul.data[li].uv = (L[i] / max(L[-1], 1e-6), k / lados)
    return o
def fuelle(nombre, c, r0, r1, z0, z1, m, pliegues=4, eje_dir=1, col=None, padre=None):
    """Fuelle de goma (acordeón) alrededor del eje Z local, centrado en c (x, y)."""
    K = pliegues * 8; lazo_ext = []
    for i in range(K + 1):
        t = i / K; z = z0 + (z1 - z0) * t; r = r0 + (r1 - r0) * t + 0.0025 * (0.5 + 0.5 * math.cos(2 * math.pi * pliegues * t))
        lazo_ext.append((z, r))
    lazo = lazo_ext + [(z, r - 0.0012) for z, r in lazo_ext[::-1]]
    o = revolucion(nombre, lazo, m, 48, col, padre); o.location = (c[0], c[1], 0); return o

# ---------------------------------------------------------------- piezas
def disco(col, M, padre):
    raiz = bpy.data.objects.new("FR_Disco", None); col.objects.link(raiz); raiz.parent = padre; raiz.empty_display_size = 0.17
    corona("FR_AnilloInt", R_IN, R_OUT, Z_IN, Z_IN + T_ANILLO, M["disco"], 160, col, raiz)
    ext = bpy.data.objects.new("FR_DiscoExt", None); col.objects.link(ext); ext.parent = raiz; ext.empty_display_size = 0.12
    corona("FR_AnilloExt", R_IN, R_OUT, Z_OUT - T_ANILLO, Z_OUT, M["disco"], 160, col, ext)
    # aletas curvas entre los dos anillos (36)
    V = []; F = []; n = 36; z0, z1 = -HUECO / 2 - 0.0002, HUECO / 2 + 0.0002
    for k in range(n):
        a0 = 2 * math.pi * k / n
        ruta = []
        for j in range(9):
            t = j / 8; r = R_IN + 0.003 + (R_OUT - R_IN - 0.005) * t; a = a0 + math.radians(28) * t
            ruta.append((r, a))
        base = len(V); w = 0.0024
        for (r, a) in ruta:
            for s in (-1, 1):
                ang = a + s * w / r
                for z in (z0, z1): V.append((r * math.cos(ang), r * math.sin(ang), z))
        for j in range(8):
            b = base + j * 4; c_ = b + 4
            F += [(b, c_, c_ + 1, b + 1), (b + 2, b + 3, c_ + 3, c_ + 2), (b, b + 2, c_ + 2, c_), (b + 1, c_ + 1, c_ + 3, b + 3)]
        F += [(base, base + 1, base + 3, base + 2)]; e = base + 32; F += [(e, e + 2, e + 3, e + 1)]
    _malla("FR_Aletas", V, F, M["disco"], False, col, raiz)
    # campana con 5 agujeros (booleana con cortadores ocultos)
    lazo = [(Z_OUT - 0.004, 0.088), (Z_OUT + 0.003, 0.0855), (0.040, 0.0855), (0.045, 0.081), (0.045, 0.034), (0.039, 0.034), (0.039, 0.0795), (Z_OUT + 0.002, 0.0795), (Z_OUT - 0.004, 0.0835)]
    cam = revolucion("FR_Campana", lazo, M["campana"], 96, col, ext)
    for k in range(5):
        a = 2 * math.pi * k / 5 + math.pi / 2
        cu = cil(f"FR_Cort{k}", (0.054 * math.cos(a), 0.054 * math.sin(a), 0.042), 0.0078, 0.03, M["acero"], 'Z', 24, col, ext)
        cu.hide_render = True; cu.hide_set(True); cu.display_type = 'WIRE'
        b = cam.modifiers.new(f"Agujero{k}", "BOOLEAN"); b.object = cu; b.solver = 'EXACT'
    return raiz, ext

def buje(col, M, padre):
    raiz = bpy.data.objects.new("FR_Buje", None); col.objects.link(raiz); raiz.parent = padre
    revolucion("FR_BujeCuerpo", [(-0.075, 0.0), (-0.075, 0.045), (-0.02, 0.05), (0.036, 0.062), (0.0385, 0.062), (0.0385, 0.03), (0.06, 0.028), (0.062, 0.0)], M["fundicion"], 64, col, raiz)
    for k in range(5):
        a = 2 * math.pi * k / 5 + math.pi / 2; x, y = 0.054 * math.cos(a), 0.054 * math.sin(a)
        cil(f"FR_Esparrago{k}", (x, y, 0.064), 0.0062, 0.05, M["acero"], 'Z', 20, col, raiz)
        cil(f"FR_EsparragoCabeza{k}", (x, y, 0.0365), 0.009, 0.004, M["acero"], 'Z', 6, col, raiz)
    return raiz

def pastilla(nombre, col, M, padre, z_cara, hacia, gastada=False):
    """hacia = +1: la fricción mira a +Z (pastilla interior); -1: mira a -Z (exterior). z_cara = cara de fricción."""
    raiz = bpy.data.objects.new(nombre, None); col.objects.link(raiz); raiz.parent = padre; raiz.empty_display_size = 0.05
    fr = 0.003 if gastada else FRIC
    zf0, zf1 = sorted((z_cara, z_cara - hacia * fr))
    zp = z_cara - hacia * fr
    zb0, zb1 = sorted((zp, zp - hacia * PLACA))
    zs = zp - hacia * PLACA
    zs0, zs1 = sorted((zs, zs - hacia * SHIM))
    # material de fricción en dos mitades (ranura central) con bordes biselados
    for i, (a0, a1) in enumerate(((-PAD_A, -0.9), (0.9, PAD_A))):
        extruir(f"{nombre}_Friccion{i}", sector(PAD_R[0], PAD_R[1], a0, a1, 18), zf0, zf1, M["friccion"], col, raiz, bisel=0.0015)
    # placa de acero con orejetas
    pl = sector(PAD_R[0] - 0.004, PAD_R[1] + 0.003, -PAD_A - 3, PAD_A + 3, 26)
    extruir(f"{nombre}_Placa", pl, zb0, zb1, M["placa"], col, raiz, bisel=0.0012)
    for s in (-1, 1):
        a = math.radians(s * (PAD_A + 7)); r = 0.125
        caja(f"{nombre}_Oreja{s}", r * math.cos(a) - 0.010, r * math.cos(a) + 0.010, r * math.sin(a) - 0.009, r * math.sin(a) + 0.009, zb0, zb1, M["placa"], 0.0012, col, raiz)
    extruir(f"{nombre}_Shim", sector(PAD_R[0] + 0.004, PAD_R[1] - 0.004, -PAD_A + 2, PAD_A - 2, 20), zs0, zs1, M["acero"], col, raiz, bisel=0.0005)
    return raiz

def pinza(col, M, padre):
    """Cuerpo de la pinza (rojo), pistón cromado con fuelle, purgador y racor del latiguillo."""
    raiz = bpy.data.objects.new("FR_Pinza", None); col.objects.link(raiz); raiz.parent = padre; raiz.empty_display_size = 0.08
    cuerpo = bpy.data.objects.new("FR_PinzaCuerpo", None); col.objects.link(cuerpo); cuerpo.parent = raiz
    zpi = Z_IN - FRIC - PLACA - SHIM             # cara del pistón
    caja("FR_PinzaAlojamiento", 0.080, 0.178, -0.050, 0.050, zpi - 0.050, zpi - 0.004, M["pinza"], 0.008, col, cuerpo)
    cil("FR_PinzaBoss", (0.122, 0, zpi - 0.058), 0.034, 0.018, M["pinza"], 'Z', 48, col, cuerpo, 0.004)
    caja("FR_PinzaPuente", 0.153, 0.182, -0.046, 0.046, zpi - 0.050, Z_OUT + FRIC + PLACA + 0.020, M["pinza"], 0.007, col, cuerpo)
    zo = Z_OUT + FRIC + PLACA
    for s in (-1, 1):
        caja(f"FR_PinzaDedo{s}", 0.100, 0.170, s * 0.006 if s > 0 else -0.042, 0.042 if s > 0 else -0.006, zo, zo + 0.018, M["pinza"], 0.006, col, cuerpo)
        caja(f"FR_PinzaOreja{s}", 0.092, 0.128, s * 0.050 if s > 0 else -0.074, 0.074 if s > 0 else -0.050, zpi - 0.040, zpi - 0.014, M["pinza"], 0.006, col, cuerpo)
        cil(f"FR_TornilloGuia{s}", (0.110, s * 0.062, zpi - 0.046), 0.0085, 0.010, M["acero"], 'Z', 6, col, cuerpo)
    # purgador (latón) arriba y racor del latiguillo
    cil("FR_Purgador", (0.186, 0.022, zpi - 0.030), 0.0045, 0.020, M["acero"], 'X', 6, col, cuerpo)
    cil("FR_PurgadorCapuchon", (0.198, 0.022, zpi - 0.030), 0.006, 0.008, M["goma"], 'X', 16, col, cuerpo)
    cil("FR_Racor", (0.186, -0.024, zpi - 0.034), 0.0075, 0.016, M["laton"], 'X', 6, col, cuerpo)
    # cámara de líquido detrás del pistón (solo se ve con rayos X)
    camara = cil("FR_CamaraLiquido", (0.122, 0, zpi - 0.044), 0.0255, 0.010, M["liquido"], 'Z', 40, col, raiz)
    # pistón y fuelle
    pis = bpy.data.objects.new("FR_PistonRaiz", None); col.objects.link(pis); pis.parent = raiz
    revolucion("FR_Piston", [(zpi - 0.038, 0.0), (zpi - 0.038, 0.0245), (zpi - 0.002, 0.0255), (zpi, 0.0235), (zpi, 0.012), (zpi - 0.006, 0.010), (zpi - 0.006, 0.0)], M["cromo"], 64, col, pis).location = (0.122, 0, 0)
    fuelle("FR_FuellePiston", (0.122, 0.0), 0.0262, 0.0275, zpi - 0.006, zpi + 0.0005, M["goma"], 3, col=col, padre=pis)
    return raiz, cuerpo, pis, camara

def soporte(col, M, padre):
    raiz = bpy.data.objects.new("FR_Soporte", None); col.objects.link(raiz); raiz.parent = padre
    zpi = Z_IN - FRIC - PLACA - SHIM
    for s in (-1, 1):
        a = math.radians(s * (PAD_A + 9)); cx, cy = 0.122 * math.cos(a), 0.122 * math.sin(a)
        caja(f"FR_SoporteBrazo{s}", cx - 0.040, cx + 0.034, cy - 0.011, cy + 0.011, zpi - 0.012, Z_IN - 0.002, M["fundicion"], 0.004, col, raiz)
        caja(f"FR_SoportePuente{s}", 0.152, 0.166, cy - 0.011, cy + 0.011, Z_IN - 0.004, Z_OUT + FRIC + 0.004, M["fundicion"], 0.003, col, raiz)
        caja(f"FR_SoporteTope{s}", cx - 0.010, cx + 0.028, cy - 0.011, cy + 0.011, Z_OUT + 0.002, Z_OUT + FRIC + 0.004, M["fundicion"], 0.003, col, raiz)
        # guía con fuelle
        cil(f"FR_Guia{s}", (0.110, s * 0.062, zpi - 0.006), 0.0068, 0.040, M["acero"], 'Z', 24, col, raiz)
        fuelle(f"FR_FuelleGuia{s}", (0.110, s * 0.062), 0.0085, 0.0095, zpi - 0.014, zpi + 0.004, M["goma"], 3, col=col, padre=raiz)
    caja("FR_SoporteAnclaje", 0.030, 0.095, -0.095, 0.095, zpi - 0.030, zpi - 0.014, M["fundicion"], 0.005, col, raiz)
    for s in (-1, 1):
        cil(f"FR_TornilloAnclaje{s}", (0.062, s * 0.075, zpi - 0.034), 0.010, 0.010, M["acero"], 'Z', 6, col, raiz)
    return raiz

def latiguillo(col, M, padre):
    zpi = Z_IN - FRIC - PLACA - SHIM
    pts = []
    p0 = Vector((0.194, -0.024, zpi - 0.034)); p1 = Vector((0.26, -0.03, zpi - 0.05)); p2 = Vector((0.31, 0.02, zpi - 0.13)); p3 = Vector((0.33, 0.09, zpi - 0.26))
    for i in range(41):
        t = i / 40; pts.append(p0 * (1 - t) ** 3 + p1 * 3 * (1 - t) ** 2 * t + p2 * 3 * (1 - t) * t * t + p3 * t ** 3)
    h = tubo("FR_Latiguillo", pts, 0.0062, M["goma"], 16, col, padre)
    core = tubo("FR_LiquidoLatiguillo", pts, 0.0034, M["liquido"], 12, col, padre)
    cil("FR_LatiguilloFinal", tuple(p3), 0.0085, 0.02, M["acero"], 'Z', 6, col, padre)
    return h, core

def aire(col, M, padre, n=36):
    """Rayas de aire que salen por los canales (se mueven escalando su raíz en XY)."""
    raiz = bpy.data.objects.new("FR_AireRaiz", None); col.objects.link(raiz); raiz.parent = padre
    V = []; F = []
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n + math.radians(14)
        for (r0, r1) in ((0.095, 0.120), (0.125, 0.150)):
            b = len(V); w = 0.0016
            for r in (r0, r1):
                for s in (-1, 1):
                    ang = a + s * w / r
                    V.append((r * math.cos(ang), r * math.sin(ang), 0.0))
            F.append((b, b + 1, b + 3, b + 2))
    _malla("FR_Aire", V, F, M["aire"], False, col, raiz)
    return raiz

def construir_freno(col, padre=None):
    """Devuelve dict con raíces de cada pieza y los materiales."""
    M = materiales_freno()
    raiz = bpy.data.objects.new("FRENO", None); col.objects.link(raiz); raiz.empty_display_size = 0.2
    if padre: raiz.parent = padre
    giro = bpy.data.objects.new("FR_Giro", None); col.objects.link(giro); giro.parent = raiz; giro.rotation_mode = 'XYZ'
    dsc, dsc_ext = disco(col, M, giro)
    bj = buje(col, M, giro)
    pi = pastilla("FR_PastillaInt", col, M, raiz, Z_IN, +1)
    pe = pastilla("FR_PastillaExt", col, M, raiz, Z_OUT, -1)
    pz, cuerpo, pis, camara = pinza(col, M, raiz)
    so = soporte(col, M, raiz)
    lat, core = latiguillo(col, M, pz)
    ai = aire(col, M, dsc)
    return {"raiz": raiz, "giro": giro, "disco": dsc, "disco_ext": dsc_ext, "buje": bj, "pad_int": pi, "pad_ext": pe,
            "pinza": pz, "pinza_cuerpo": cuerpo, "piston": pis, "camara": camara, "soporte": so, "latiguillo": lat,
            "liquido": core, "aire": ai, "M": M}
