# BUJÍA (rosca M14) por código · EKORUEDAS · 27-11-2026
# Medidas reales aproximadas: 90 mm de largo, hexágono de 16 mm, rosca de 14 mm (paso 1,25) y 19 mm de largo, separación de
# electrodos de 0,9 mm. Origen en la punta del electrodo central; Z hacia el terminal.
# Partes: terminal y espiga, aislante de cerámica (óxido de aluminio) con sus nervios, sello conductor, electrodo central con
# alma de cobre, cuerpo metálico (hexágono, asiento, rosca de verdad en hélice), arandela de cobre y electrodo de masa en "J".
# Extras animables: chispas (arcos que parpadean), bola de fuego, corriente que baja por el centro, desgaste (forma "gastado")
# y hollín en la punta de la cerámica (propiedad de escena "hollin").
# Uso: BJ = {"__name__": "bj"}; exec(open(".../bujia_real.py", encoding="utf-8").read(), BJ)
#      O = BJ["construir_bujia"](coleccion, MP, "BUJ", gastada=False)
import bpy, bmesh, math, random
from mathutils import Vector

GAP = 0.0009
Z_CASCO0, Z_ROSCA1, Z_HEX0, Z_HEX1, Z_CASCO1 = 0.0035, 0.0225, 0.0262, 0.0342, 0.0382
Z_TERM = 0.0905

def _obj(nombre, bm, mats, col, padre, liso=True, angulo=35):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = liso
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(nombre, me); col.objects.link(o); o.parent = padre
    if liso:
        md = o.modifiers.new("aristas", 'EDGE_SPLIT'); md.split_angle = math.radians(angulo)
    return o

def torno(bm, perfil, seg=64):
    vs = [bm.verts.new((r, 0, z)) for r, z in perfil]
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.tau, steps=seg, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

def _caja(bm, c, s):
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]: v.co = Vector((c[0] + v.co.x * s[0], c[1] + v.co.y * s[1], c[2] + v.co.z * s[2]))
    return r["verts"]

def _mat(nombre, color, metal=0.0, rugo=0.4, emis=None, fuerza=0.0, coat=0.0, ss=0.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rugo
    if coat: b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = 0.05
    if ss: b.inputs["Subsurface Weight"].default_value = ss; b.inputs["Subsurface Radius"].default_value = (0.002, 0.002, 0.0018)
    if emis: b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = fuerza
    return m

def porcelana(nombre):
    """Cerámica blanca brillante; con 'hollin' (0-1) la punta se ennegrece de abajo arriba."""
    m = _mat(nombre, (0.92, 0.92, 0.89), rugo=0.14, coat=0.6, ss=0.12); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    rg = nt.nodes.new("ShaderNodeMapRange"); rg.clamp = True; rg.inputs["From Min"].default_value = 0.002; rg.inputs["From Max"].default_value = 0.013
    rg.inputs["To Min"].default_value = 1.0; rg.inputs["To Max"].default_value = 0.0
    nt.links.new(sp.outputs["Z"], rg.inputs["Value"])
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'VIEW_LAYER'; at.attribute_name = "hollin"
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0; nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = 'MULTIPLY'; nt.links.new(rg.outputs["Result"], m1.inputs[0]); nt.links.new(at.outputs["Fac"], m1.inputs[1])
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = 'MULTIPLY'; m2.use_clamp = True; nt.links.new(m1.outputs[0], m2.inputs[0])
    m3 = nt.nodes.new("ShaderNodeMath"); m3.operation = 'MULTIPLY_ADD'; m3.inputs[1].default_value = 0.8; m3.inputs[2].default_value = 0.6
    nt.links.new(nz.outputs["Fac"], m3.inputs[0]); nt.links.new(m3.outputs[0], m2.inputs[1])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; nt.links.new(m2.outputs[0], mx.inputs[0])
    mx.inputs[6].default_value = (0.92, 0.92, 0.89, 1); mx.inputs[7].default_value = (0.02, 0.018, 0.016, 1)
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    mr = nt.nodes.new("ShaderNodeMapRange"); nt.links.new(m2.outputs[0], mr.inputs["Value"]); mr.inputs["To Min"].default_value = 0.14; mr.inputs["To Max"].default_value = 0.8
    nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    return m

def materiales(MP, pref="BUJ"):
    M = {}
    M["casco"] = MP["acero"](pref + "_Casco", color=(0.74, 0.75, 0.77), rugo=(0.10, 0.22), anillos=True)
    M["hex"] = MP["acero"](pref + "_Hex", color=(0.70, 0.71, 0.73), rugo=(0.12, 0.26), anillos=False)
    M["porcelana"] = porcelana(pref + "_Porcelana")
    M["niquel"] = _mat(pref + "_Niquel", (0.62, 0.62, 0.63), metal=1.0, rugo=0.28)
    M["cobre"] = _mat(pref + "_Cobre", (0.95, 0.52, 0.32), metal=1.0, rugo=0.22)
    M["sello"] = _mat(pref + "_Sello", (0.08, 0.08, 0.09), metal=0.3, rugo=0.5)
    M["terminal"] = MP["acero"](pref + "_Terminal", color=(0.68, 0.69, 0.70), rugo=(0.14, 0.28), anillos=False)
    M["arco"] = _mat(pref + "_Arco", (0.6, 0.8, 1.0), emis=(0.55, 0.78, 1.0), fuerza=90.0)
    M["arco_debil"] = _mat(pref + "_ArcoDebil", (1.0, 0.5, 0.2), emis=(1.0, 0.45, 0.15), fuerza=25.0)
    M["voltaje"] = _mat(pref + "_Voltaje", (0.6, 0.85, 1.0), emis=(0.5, 0.8, 1.0), fuerza=40.0)
    m = bpy.data.materials.new(pref + "_Fuego"); m.use_nodes = True; nt = m.node_tree
    out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]; nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission"); tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 4.0; nz.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (1.0, 0.25, 0.02, 1); cr.color_ramp.elements[1].color = (1.0, 0.85, 0.35, 1)
    nt.links.new(nz.outputs["Fac"], cr.inputs[0]); nt.links.new(cr.outputs[0], em.inputs["Color"]); em.inputs["Strength"].default_value = 30.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader"); mx.name = "Fundido"
    mx.inputs[0].default_value = 0.0
    nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs["Surface"])
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    M["fuego"] = m
    return M

def construir_bujia(col, MP, pref="BUJ", gastada=False):
    M = materiales(MP, pref)
    raiz = bpy.data.objects.new(pref, None); col.objects.link(raiz); raiz.empty_display_size = 0.03
    O = {"raiz": raiz, "M": M}
    # ---- aislante (con su taladro) y nervios
    pf = [(0.0013, 0.0013), (0.0021, 0.0013), (0.0043, 0.010), (0.0048, 0.011), (0.0048, 0.030), (0.0061, 0.031), (0.0061, 0.035), (0.0052, 0.036)]
    for k in range(5):
        z = 0.048 + k * 0.0055; pf += [(0.0052, z), (0.0058, z + 0.0012), (0.0058, z + 0.0028), (0.0052, z + 0.0040)]
    pf += [(0.0052, 0.0785), (0.0046, 0.0805), (0.0046, 0.0828), (0.0019, 0.0828), (0.0019, 0.0200), (0.0013, 0.0200)]
    bm = bmesh.new(); torno(bm, pf, seg=72); O["aislante"] = _obj(pref + "_Aislante", bm, [M["porcelana"]], col, raiz)
    # ---- electrodo central (níquel) con alma de cobre, sello conductor, espiga y terminal
    bm = bmesh.new(); torno(bm, [(0.0, 0.0), (0.00118, 0.0), (0.00125, 0.0003), (0.00125, 0.0200), (0.0, 0.0200)], seg=40)
    O["electrodo"] = o = _obj(pref + "_Electrodo", bm, [M["niquel"]], col, raiz)
    o.shape_key_add(name="Basis", from_mix=False); kb = o.shape_key_add(name="gastado", from_mix=False)
    for i, v in enumerate(o.data.vertices):                 # la punta se redondea y se acorta
        if v.co.z < 0.0012:
            r = math.hypot(v.co.x, v.co.y); s = max(0.55, 1 - (0.0012 - v.co.z) / 0.0012 * 0.45)
            kb.data[i].co = Vector((v.co.x * s, v.co.y * s, v.co.z + 0.00055 + (0.00125 - r) * 0.05))
    bm = bmesh.new(); torno(bm, [(0.0, 0.0016), (0.00072, 0.0016), (0.00072, 0.0195), (0.0, 0.0195)], seg=32)
    O["cobre"] = _obj(pref + "_AlmaCobre", bm, [M["cobre"]], col, raiz)
    bm = bmesh.new(); torno(bm, [(0.0, 0.0200), (0.00185, 0.0200), (0.00185, 0.0400), (0.0, 0.0400)], seg=32)
    O["sello"] = _obj(pref + "_Sello", bm, [M["sello"]], col, raiz)
    pt = [(0.0, 0.0400), (0.0018, 0.0400), (0.0018, 0.0830), (0.0026, 0.0832), (0.0040, 0.0838), (0.0040, 0.0858), (0.0031, 0.0866),
          (0.0031, 0.0876), (0.0040, 0.0884), (0.0040, Z_TERM - 0.0006), (0.0034, Z_TERM), (0.0, Z_TERM)]
    bm = bmesh.new(); torno(bm, pt, seg=48); O["terminal"] = _obj(pref + "_Terminal", bm, [M["terminal"]], col, raiz)
    # ---- cuerpo metálico: tubo con asiento y engatillado; hexágono aparte; rosca en hélice de verdad
    pc = [(0.0050, Z_CASCO0), (0.0062, Z_CASCO0), (0.0063, Z_ROSCA1), (0.0084, Z_ROSCA1 + 0.0004), (0.0084, Z_HEX0 - 0.0003),
          (0.0078, Z_HEX0), (0.0078, Z_HEX1), (0.0072, Z_HEX1 + 0.0004), (0.0062, Z_CASCO1), (0.0054, Z_CASCO1), (0.0050, Z_HEX1)]
    bm = bmesh.new(); torno(bm, pc, seg=72); O["casco"] = _obj(pref + "_Casco", bm, [M["casco"]], col, raiz)
    bm = bmesh.new()
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.0092, radius2=0.0092, depth=Z_HEX1 - Z_HEX0)
    for v in res["verts"]: v.co.z += (Z_HEX0 + Z_HEX1) / 2
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.0004, segments=2, affect='EDGES')
    O["hex"] = _obj(pref + "_Hexagono", bm, [M["hex"]], col, raiz, angulo=40)
    paso = 0.00125; vueltas = (Z_ROSCA1 - Z_CASCO0 - 0.0015) / paso; pasos = int(vueltas * 48)
    bm = bmesh.new()
    tri = [bm.verts.new((0.0061, 0, Z_CASCO0 + 0.0006)), bm.verts.new((0.0070, 0, Z_CASCO0 + 0.0006 + paso * 0.42)),
           bm.verts.new((0.0070, 0, Z_CASCO0 + 0.0006 + paso * 0.58)), bm.verts.new((0.0061, 0, Z_CASCO0 + 0.0006 + paso))]
    cara = bm.faces.new(tri)
    bmesh.ops.spin(bm, geom=[cara] + tri + list(cara.edges), cent=(0, 0, 0), axis=(0, 0, 1), dvec=(0, 0, paso / 48),
                   angle=math.tau * vueltas, steps=pasos, use_merge=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    O["rosca"] = _obj(pref + "_Rosca", bm, [M["casco"]], col, raiz, angulo=60)
    bm = bmesh.new(); torno(bm, [(0.0066, Z_ROSCA1 - 0.0013), (0.0091, Z_ROSCA1 - 0.0013), (0.0091, Z_ROSCA1), (0.0066, Z_ROSCA1)], seg=72)
    O["arandela"] = _obj(pref + "_Arandela", bm, [M["cobre"]], col, raiz)
    # ---- electrodo de masa en "J" (soldado abajo al cuerpo, pasa por debajo del central)
    bm = bmesh.new()
    _caja(bm, (0.0058, 0, (-GAP - 0.0013 + Z_CASCO0 + 0.0008) / 2), (0.0013, 0.0025, Z_CASCO0 + 0.0008 + GAP + 0.0013))
    _caja(bm, (0.0024, 0, -GAP - 0.00065), (0.0072, 0.0025, 0.0013))
    O["masa"] = _obj(pref + "_Masa", bm, [M["niquel"]], col, raiz, liso=False)
    if gastada:
        O["electrodo"].data.shape_keys.key_blocks["gastado"].value = 1.0
        O["masa"].location.z = -0.0005
        M["porcelana"] = porcelana(pref + "_PorcelanaSucia")
    return O

def _keys_vis(o, claves):
    for ff, v in claves:
        o.hide_render = o.hide_viewport = not v; o.keyframe_insert("hide_render", frame=ff); o.keyframe_insert("hide_viewport", frame=ff)

def arco(col, padre, mat, a, b, nombre, semilla=1, quiebros=7, amp=0.00028, grosor=0.00011):
    """Un rayo quebrado entre a y b (curva con grosor y emisión)."""
    rnd = random.Random(semilla); a, b = Vector(a), Vector(b); d = b - a
    lado = d.orthogonal().normalized(); lado2 = d.cross(lado).normalized()
    cu = bpy.data.curves.new(nombre, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = grosor; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); sp.points.add(quiebros)
    for i in range(quiebros + 1):
        t = i / quiebros; p = a + d * t
        if 0 < i < quiebros: p += lado * rnd.uniform(-amp, amp) + lado2 * rnd.uniform(-amp, amp)
        sp.points[i].co = (*p, 1)
    o = bpy.data.objects.new(nombre, cu); col.objects.link(o); o.parent = padre; cu.materials.append(mat)
    return o

def chispas(col, padre, mat, a, b, fotos, pref="BUJ_Chispa", n=3, amp=0.00028, grosor=0.00011, luz=None, energia=8.0):
    """Arcos que parpadean: en cada fotograma de 'fotos' se enciende uno distinto durante 2 fotogramas."""
    arcos = [arco(col, padre, mat, a, b, f"{pref}{i}", semilla=i * 7 + 3, amp=amp, grosor=grosor) for i in range(n)]
    for i, o in enumerate(arcos):
        cl = [(1, False)]
        for k, f in enumerate(fotos):
            if k % n == i: cl += [(f, True), (f + 2, False)]
        _keys_vis(o, sorted(cl))
    if luz is not None:
        luz.data.energy = 0; luz.data.keyframe_insert("energy", frame=1)
        for f in fotos:
            for ff, v in ((f - 1, 0), (f, energia), (f + 2, 0)): luz.data.energy = v; luz.data.keyframe_insert("energy", frame=ff)
    return arcos

def bola_fuego(col, padre, mat, centro, fotos, nombre="BUJ_Fuego", r_max=0.011):
    """Bola de fuego que crece y se apaga tras cada chispa."""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(nombre, me); col.objects.link(o); o.parent = padre; me.materials.append(mat); o.location = centro
    fnd = mat.node_tree.nodes["Fundido"].inputs[0]
    o.scale = (0.0001,) * 3; o.keyframe_insert("scale", frame=1); fnd.default_value = 0.0; fnd.keyframe_insert("default_value", frame=1)
    cl = [(1, False)]
    for f in fotos:
        for ff, s, fd in ((f, 0.08, 0.0), (f + 4, 0.75, 0.0), (f + 10, 1.0, 0.55), (f + 16, 1.12, 1.0)):
            o.scale = (r_max * s, r_max * s, r_max * s * 0.85); o.keyframe_insert("scale", frame=ff)
            fnd.default_value = fd; fnd.keyframe_insert("default_value", frame=ff)
        cl += [(f, True), (f + 17, False)]
    _keys_vis(o, sorted(cl))
    return o

def voltaje(col, padre, mat, f0, f1, n=14, periodo=18, pref="BUJ_Volt"):
    """Puntitos de luz que bajan por el centro (espiga, sello y electrodo) hasta la punta."""
    rnd = random.Random(2); obs = []
    for i in range(n):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.00055)
        me = bpy.data.meshes.new(f"{pref}{i}"); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(f"{pref}{i}", me); col.objects.link(o); o.parent = padre; me.materials.append(mat)
        fase = int(i * periodo / n); f = f0 - periodo + fase; ang = rnd.uniform(0, math.tau)
        while f < f1 + periodo:
            for df, z in ((0, Z_TERM + 0.002), (periodo - 1, 0.0002)):
                if f + df >= 1:
                    o.location = (0.0009 * math.cos(ang), -0.0009 * abs(math.sin(ang)) - 0.0004, z); o.keyframe_insert("location", frame=f + df)
            f += periodo
        _keys_vis(o, [(1, False), (f0, True), (f1, False)])
        obs.append(o)
    return obs
