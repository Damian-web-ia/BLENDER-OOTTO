# BATERÍA DE COCHE 12 V (plomo-ácido) por código · EKORUEDAS · 27-11-2026
# Medidas reales aproximadas (tipo L2, 60 Ah): 242 x 175 x 190 mm. Origen en el centro de la base; X = largo, Y = ancho, Z = alto.
# Por dentro: 6 celdas en fila (2,1 V cada una), en cada celda placas positivas (dióxido de plomo, marrón) y negativas
# (plomo esponjoso, gris) con separadores, bañadas en electrolito (ácido sulfúrico y agua). Puentes de plomo entre celdas
# y los dos bornes saliendo de las celdas de los extremos. La tapa y la pared de delante se pueden quitar (despiece).
# Uso: BT = {"__name__": "bt"}; exec(open(".../bateria_real.py", encoding="utf-8").read(), BT)
#      O = BT["construir_bateria"](coleccion, MP, "BAT", interior=True, gastada=False)
import bpy, bmesh, math, random
from mathutils import Vector

LX, LY, HC = 0.242, 0.175, 0.172          # caja (sin tapa)
TW = 0.004                                # grosor de pared
Z_TAPA0, Z_TAPA1 = 0.172, 0.186
N_CELDAS = 6; TP = 0.003                  # tabiques
X_IN0 = -LX / 2 + TW; X_IN1 = LX / 2 - TW
CW = (X_IN1 - X_IN0 - TP * (N_CELDAS - 1)) / N_CELDAS
Y_IN = LY / 2 - TW
PL_Y, PL_Z0, PL_Z1 = 0.071, 0.012, 0.132  # placas
N_PL = 10; PL_T = 0.0016
Z_PUENTE0, Z_PUENTE1 = 0.140, 0.149
Y_PUENTE = 0.045
Z_LIQ = 0.150
R_BORNE = 0.0088; Z_BORNE1 = 0.206

def celda_x(k):
    x0 = X_IN0 + k * (CW + TP); return x0, x0 + CW

def _caja(bm, c, s, bisel=0.0):
    r = bmesh.ops.create_cube(bm, size=1.0); vs = r["verts"]
    for v in vs: v.co = Vector((c[0] + v.co.x * s[0], c[1] + v.co.y * s[1], c[2] + v.co.z * s[2]))
    if bisel > 0:
        es = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=es, offset=bisel, segments=2, affect='EDGES', profile=0.5)
    return vs

def _cil(bm, c, r, z0, z1, seg=24, r1=None):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r1 is None else r1, depth=z1 - z0)
    for v in res["verts"]: v.co += Vector((c[0], c[1], (z0 + z1) / 2))
    return res["verts"]

def _obj(nombre, bm, mats, col, padre, liso=False, angulo=40):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = liso
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(nombre, me); col.objects.link(o); o.parent = padre
    if liso:
        md = o.modifiers.new("aristas", 'EDGE_SPLIT'); md.split_angle = math.radians(angulo)
    return o

def _salida(nt): return [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]

def escarcha(m, prop="frio"):
    """Mezcla el material con escarcha blanca (ruido) según la propiedad de escena 'frio' (0-1)."""
    if m.get("escarcha"): return m
    nt = m.node_tree; out = _salida(nt); src = out.inputs["Surface"].links[0].from_socket
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'VIEW_LAYER'; at.attribute_name = prop
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 170.0; nz.inputs["Detail"].default_value = 12.0
    nz.inputs["Roughness"].default_value = 0.68
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    # el frío "crece": umbral que baja con la propiedad
    rg = nt.nodes.new("ShaderNodeMapRange"); rg.clamp = True
    nt.links.new(nz.outputs["Fac"], rg.inputs["Value"]); rg.inputs["From Min"].default_value = 0.42; rg.inputs["From Max"].default_value = 0.58
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.use_clamp = True
    nt.links.new(rg.outputs["Result"], mul.inputs[0])
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 1.6
    nt.links.new(at.outputs["Fac"], m2.inputs[0]); nt.links.new(m2.outputs[0], mul.inputs[1])
    fr = nt.nodes.new("ShaderNodeBsdfPrincipled")
    fr.inputs["Base Color"].default_value = (0.86, 0.93, 1.0, 1); fr.inputs["Roughness"].default_value = 0.5
    fr.inputs["Subsurface Weight"].default_value = 0.35; fr.inputs["Specular IOR Level"].default_value = 0.8
    fr.inputs["Coat Weight"].default_value = 0.4; fr.inputs["Coat Roughness"].default_value = 0.15
    nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 420.0; nz2.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.0006
    nt.links.new(nz2.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], fr.inputs["Normal"])
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mul.outputs[0], mx.inputs[0]); nt.links.new(src, mx.inputs[1]); nt.links.new(fr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    m["escarcha"] = 1
    return m

def _placa_mat(nombre, color, rugo):
    """Rejilla de plomo con la pasta activa: textura de ladrillo (rejilla) en el plano YZ y grano fino."""
    m = bpy.data.materials.new(nombre); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rugo
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); cb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(tc.outputs["Object"], sp.inputs[0])
    nt.links.new(sp.outputs["Y"], cb.inputs["X"]); nt.links.new(sp.outputs["Z"], cb.inputs["Y"]); nt.links.new(sp.outputs["X"], cb.inputs["Z"])
    br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 60.0; br.inputs["Mortar Size"].default_value = 0.035
    br.offset = 0.0; br.squash = 1.0
    nt.links.new(cb.outputs[0], br.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0; nz.inputs["Detail"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'MULTIPLY_ADD'
    nt.links.new(nz.outputs["Fac"], ad.inputs[0]); ad.inputs[1].default_value = 0.35; nt.links.new(br.outputs["Fac"], ad.inputs[2])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.7; bp.inputs["Distance"].default_value = 0.0004
    nt.links.new(ad.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    # la rejilla (mortero) es metal más claro
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(br.outputs["Fac"], mx.inputs[0]); mx.inputs[6].default_value = (*color, 1); mx.inputs[7].default_value = (0.42, 0.42, 0.44, 1)
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    return m

def _plastico(nombre, color, rugo=0.5, transm=0.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rugo
    if transm: b.inputs["Transmission Weight"].default_value = transm
    return m

def materiales(MP, pref="BAT"):
    M = {}
    M["caja"] = escarcha(MP["pintura"](pref + "_Plastico", color=(0.03, 0.03, 0.034), rugo=0.42, barniz=0.25, piel_naranja=0.02))
    M["tapa"] = escarcha(MP["pintura"](pref + "_Tapa", color=(0.045, 0.046, 0.05), rugo=0.40, barniz=0.3, piel_naranja=0.015))
    M["plomo"] = MP["acero"](pref + "_Plomo", color=(0.40, 0.41, 0.43), rugo=(0.30, 0.48), anillos=False)
    M["pos"] = _placa_mat(pref + "_PlacaPos", (0.20, 0.085, 0.05), 0.85)
    M["neg"] = _placa_mat(pref + "_PlacaNeg", (0.30, 0.31, 0.33), 0.72)
    M["sep"] = _plastico(pref + "_Separador", (0.86, 0.87, 0.84), 0.6, 0.12)
    M["liq"] = MP["aceite"](pref + "_Electrolito", color=(0.80, 0.90, 0.96), calor=False)
    M["rojo"] = _plastico(pref + "_Rojo", (0.55, 0.02, 0.02), 0.35)
    M["negro"] = _plastico(pref + "_Negro", (0.012, 0.012, 0.014), 0.35)
    M["blanco"] = _plastico(pref + "_Marca", (0.85, 0.85, 0.82), 0.4)
    m = bpy.data.materials.new(pref + "_Sulfato"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.80, 0.87, 0.76, 1); b.inputs["Roughness"].default_value = 0.95
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 300.0; nz.inputs["Detail"].default_value = 6.0
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 1.0; bp.inputs["Distance"].default_value = 0.0008
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    M["sulfato"] = m
    m = bpy.data.materials.new(pref + "_Chispa"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.6, 0.9, 1.0, 1); b.inputs["Emission Color"].default_value = (0.55, 0.85, 1.0, 1)
    b.inputs["Emission Strength"].default_value = 45.0
    M["chispa"] = m
    M["burbuja"] = MP["burbuja"](pref + "_Burbuja")
    return M

def construir_bateria(col, MP, pref="BAT", interior=True, gastada=False):
    M = materiales(MP, pref)
    raiz = bpy.data.objects.new(pref, None); col.objects.link(raiz); raiz.empty_display_size = 0.12
    O = {"raiz": raiz, "M": M}
    # ---- caja: base y 4 paredes (la de delante, y < 0, se quita en el despiece)
    def pared(n, c, s):
        bm = bmesh.new(); _caja(bm, c, s, 0.0012)
        # reborde abajo (por fuera) en las paredes largas
        if n in ("Frente", "Atras"):
            sg = -1 if n == "Frente" else 1
            _caja(bm, (0, c[1] + sg * 0.004, 0.006), (LX - 0.004, 0.006, 0.012), 0.001)
        return _obj(f"{pref}_{n}", bm, [M["caja"]], col, raiz)
    O["base"] = pared("Base", (0, 0, TW / 2), (LX, LY, TW))
    O["frente"] = pared("Frente", (0, -LY / 2 + TW / 2, HC / 2), (LX, TW, HC))
    O["atras"] = pared("Atras", (0, LY / 2 - TW / 2, HC / 2), (LX, TW, HC))
    O["izq"] = pared("Izq", (-LX / 2 + TW / 2, 0, HC / 2), (TW, LY - 2 * TW, HC))
    O["der"] = pared("Der", (LX / 2 - TW / 2, 0, HC / 2), (TW, LY - 2 * TW, HC))
    # ---- tapa con tapones de las celdas y marcas + / −
    tapa = bpy.data.objects.new(pref + "_TapaGrupo", None); col.objects.link(tapa); tapa.parent = raiz
    bm = bmesh.new(); _caja(bm, (0, 0, (Z_TAPA0 + Z_TAPA1) / 2), (LX + 0.002, LY + 0.002, Z_TAPA1 - Z_TAPA0), 0.002)
    _caja(bm, (0, 0.028, Z_TAPA1 + 0.002), (LX - 0.04, 0.05, 0.004), 0.0015)          # franja central en relieve
    O["tapa"] = _obj(pref + "_Tapa", bm, [M["tapa"]], col, tapa)
    bm = bmesh.new()
    for k in range(N_CELDAS):
        x0, x1 = celda_x(k); _cil(bm, ((x0 + x1) / 2, 0.028, 0), 0.0085, Z_TAPA1 + 0.004, Z_TAPA1 + 0.009, seg=20)
    _obj(pref + "_Tapones", bm, [M["tapa"]], col, tapa, liso=True)
    xb_n, xb_p = celda_x(0), celda_x(N_CELDAS - 1)
    XBN = (xb_n[0] + xb_n[1]) / 2; XBP = (xb_p[0] + xb_p[1]) / 2; YB = -Y_PUENTE
    O["XB"] = (XBN, XBP, YB)
    for x, mat, nom in ((XBP, M["rojo"], "AnilloPos"), (XBN, M["negro"], "AnilloNeg")):
        bm = bmesh.new(); _cil(bm, (x, YB, 0), 0.0165, Z_TAPA1, Z_TAPA1 + 0.003, seg=32)
        _obj(f"{pref}_{nom}", bm, [mat], col, tapa, liso=True)
    bm = bmesh.new()                                                                  # + y − en relieve
    _caja(bm, (XBP, YB + 0.032, Z_TAPA1 + 0.0015), (0.016, 0.004, 0.003)); _caja(bm, (XBP, YB + 0.032, Z_TAPA1 + 0.0015), (0.004, 0.016, 0.003))
    _caja(bm, (XBN, YB + 0.032, Z_TAPA1 + 0.0015), (0.016, 0.004, 0.003))
    _obj(pref + "_Marcas", bm, [M["blanco"]], col, tapa)
    O["tapa_grupo"] = tapa
    # ---- bornes (salen de las celdas de los extremos y atraviesan la tapa)
    bornes = {}
    for x, nom in ((XBP, "+"), (XBN, "-")):
        bm = bmesh.new()
        z0 = Z_PUENTE0 if interior else Z_TAPA1
        _cil(bm, (x, YB, 0), R_BORNE * 1.05, z0, Z_TAPA1 + 0.003, seg=32)
        _cil(bm, (x, YB, 0), R_BORNE * 1.08, Z_TAPA1 + 0.003, Z_BORNE1, seg=32, r1=R_BORNE * 0.92)
        bornes[nom] = _obj(f"{pref}_Borne{'Pos' if nom == '+' else 'Neg'}", bm, [M["plomo"]], col, raiz, liso=True)
    O["bornes"] = bornes
    if gastada:                                       # sulfato blanco-verdoso alrededor de los bornes
        rnd = random.Random(7); bm = bmesh.new()
        for x in (XBP, XBN):
            for i in range(26 if x == XBP else 18):
                a = rnd.uniform(0, math.tau); rr = rnd.uniform(0.010, 0.019); s = rnd.uniform(0.0025, 0.0055)
                r = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=s)
                for v in r["verts"]:
                    v.co = Vector((v.co.x * rnd.uniform(0.8, 1.3), v.co.y * rnd.uniform(0.8, 1.3), v.co.z * 0.6)) + \
                        Vector((x + rr * math.cos(a), YB + rr * math.sin(a), Z_TAPA1 + 0.004 + rnd.uniform(0, 0.007)))
        O["sulfato"] = _obj(pref + "_Sulfato", bm, [M["sulfato"]], col, raiz, liso=True)
    if not interior:
        bm = bmesh.new(); _caja(bm, (0, 0, HC * 0.5), (LX - 2 * TW, LY - 2 * TW, HC - 0.01))     # relleno (no se ve)
        _obj(pref + "_Relleno", bm, [M["negro"]], col, raiz)
        return O
    # ---- tabiques entre celdas
    bm = bmesh.new()
    for k in range(1, N_CELDAS):
        x = celda_x(k)[0] - TP / 2; _caja(bm, (x, 0, (TW + 0.165) / 2), (TP, 2 * Y_IN, 0.165 - TW))
    O["tabiques"] = _obj(pref + "_Tabiques", bm, [M["caja"]], col, raiz)
    # ---- placas, separadores, puentes y conectores. La celda 0 (la del borne negativo) va aparte: es el "elemento" que sale.
    elem = bpy.data.objects.new(pref + "_Elemento1", None); col.objects.link(elem); elem.parent = raiz
    O["elemento"] = elem; O["placas_e1"] = []
    bm_p, bm_n, bm_s, bm_pu = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
    for k in range(N_CELDAS):
        x0, x1 = celda_x(k); paso = (CW - 0.004) / N_PL
        s_pos = 1 if k % 2 == 0 else -1                 # lado (y) del puente positivo en esta celda
        for i in range(N_PL):
            x = x0 + 0.002 + paso * (i + 0.5); pos = (i % 2 == 0)
            lug_y = s_pos * Y_PUENTE if pos else -s_pos * Y_PUENTE
            if k == 0:
                b_ = bmesh.new(); _caja(b_, (x, 0, (PL_Z0 + PL_Z1) / 2), (PL_T, 2 * PL_Y, PL_Z1 - PL_Z0))
                _caja(b_, (x, lug_y, (PL_Z1 + Z_PUENTE0) / 2), (PL_T, 0.010, Z_PUENTE0 - PL_Z1 + 0.001))
                o = _obj(f"{pref}_E1_Placa{i}", b_, [M["pos"] if pos else M["neg"]], col, elem); O["placas_e1"].append(o)
            else:
                b_ = bm_p if pos else bm_n
                _caja(b_, (x, 0, (PL_Z0 + PL_Z1) / 2), (PL_T, 2 * PL_Y, PL_Z1 - PL_Z0))
                _caja(b_, (x, lug_y, (PL_Z1 + Z_PUENTE0) / 2), (PL_T, 0.010, Z_PUENTE0 - PL_Z1 + 0.001))
            if i < N_PL - 1 and k > 0:
                _caja(bm_s, (x + paso / 2, 0, (PL_Z0 + PL_Z1) / 2 + 0.002), (0.0006, 2 * PL_Y + 0.004, PL_Z1 - PL_Z0 + 0.008))
        # puentes (+ y −) de la celda
        for sg in (1, -1):
            b_ = bm_pu if k > 0 else bmesh.new()
            _caja(b_, ((x0 + x1) / 2, sg * Y_PUENTE, (Z_PUENTE0 + Z_PUENTE1) / 2), (CW - 0.003, 0.012, Z_PUENTE1 - Z_PUENTE0), 0.001)
            if k == 0: _obj(f"{pref}_E1_Puente{'P' if sg > 0 else 'N'}", b_, [M["plomo"]], col, elem)
        # conector con la celda siguiente (atraviesa el tabique por arriba)
        if k < N_CELDAS - 1:
            xs = x1 + TP / 2; _caja(bm_pu, (xs, s_pos * Y_PUENTE, (Z_PUENTE0 + Z_PUENTE1) / 2 + 0.002), (0.012, 0.012, 0.014), 0.001)
    O["placas_pos"] = _obj(pref + "_PlacasPos", bm_p, [M["pos"]], col, raiz)
    O["placas_neg"] = _obj(pref + "_PlacasNeg", bm_n, [M["neg"]], col, raiz)
    O["separadores"] = _obj(pref + "_Separadores", bm_s, [M["sep"]], col, raiz)
    O["puentes"] = _obj(pref + "_Puentes", bm_pu, [M["plomo"]], col, raiz)
    # ---- electrolito (cada celda llena hasta Z_LIQ)
    bm = bmesh.new()
    for k in range(N_CELDAS):
        x0, x1 = celda_x(k); _caja(bm, ((x0 + x1) / 2, 0, (TW + Z_LIQ) / 2), (CW - 0.0006, 2 * Y_IN - 0.0006, Z_LIQ - TW))
    O["electrolito"] = _obj(pref + "_Electrolito", bm, [M["liq"]], col, raiz)
    O["celdas"] = [Vector(((celda_x(k)[0] + celda_x(k)[1]) / 2, 0, Z_LIQ)) for k in range(N_CELDAS)]
    return O

def _tiempo(f, f_frio, lento):
    """Tiempo 'interno' de la reacción: con frío pasa más despacio."""
    return f if f <= f_frio else f_frio + (f - f_frio) * lento

def burbujas(col, padre, M, f0, f1, f_frio, lento=0.3, n=60, semilla=5, pref="BAT"):
    """Burbujitas que suben entre las placas hasta la superficie del electrolito y vuelven a salir abajo."""
    rnd = random.Random(semilla); obs = []
    mat = M["burbuja"]
    for i in range(n):
        k = rnd.randrange(1, N_CELDAS); x0, x1 = celda_x(k)
        r = rnd.uniform(0.0007, 0.0016)
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=r)
        o = _obj(f"{pref}_Burbuja{i}", bm, [mat], col, padre, liso=True)
        x = rnd.uniform(x0 + 0.003, x1 - 0.003); y = rnd.uniform(-PL_Y, -0.004)     # mitad de delante (la que se ve)
        za, zb = rnd.uniform(0.02, 0.10), Z_LIQ - r
        per = rnd.uniform(34, 60); fase = rnd.uniform(0, per)
        f = f0
        while f <= f1 + 2:
            t = (_tiempo(f, f_frio, lento) + fase) % per / per
            o.location = (x + 0.0005 * math.sin(f * 0.4 + i), y, za + (zb - za) * t); o.keyframe_insert("location", frame=f)
            f += 2
        o.hide_render = o.hide_viewport = True
        for ff, v in ((1, False), (f0, True), (f1, False)):
            o.hide_render = o.hide_viewport = not v; o.keyframe_insert("hide_render", frame=ff); o.keyframe_insert("hide_viewport", frame=ff)
        obs.append(o)
    return obs

def camino_corriente(O):
    """Recorrido de la corriente: del borne − baja al puente de la celda 1, pasa por las 6 celdas y sube por el borne +."""
    XBN, XBP, YB = O["XB"]; zc = (Z_PUENTE0 + Z_PUENTE1) / 2 + 0.006
    pts = [Vector((XBN, YB, Z_BORNE1 + 0.03)), Vector((XBN, YB, zc))]
    for k in range(N_CELDAS):
        x0, x1 = celda_x(k); s_pos = 1 if k % 2 == 0 else -1
        pts.append(Vector(((x0 + x1) / 2, -s_pos * Y_PUENTE, zc)))
        pts.append(Vector(((x0 + x1) / 2, s_pos * Y_PUENTE, zc)))
        if k < N_CELDAS - 1: pts.append(Vector((x1 + TP / 2, s_pos * Y_PUENTE, zc)))
    pts += [Vector((XBP, YB, zc)), Vector((XBP, YB, Z_BORNE1 + 0.06))]
    return pts

def corriente(col, padre, M, pts, f0, f1, f_frio, lento=0.3, n=22, vueltas=34, pref="BAT"):
    """Chispitas de luz que recorren el camino de la corriente; con frío van más despacio."""
    largos = [0.0]
    for a, b in zip(pts, pts[1:]): largos.append(largos[-1] + (b - a).length)
    L = largos[-1]
    def punto(s):
        s = s % L
        for i in range(len(pts) - 1):
            if largos[i + 1] >= s:
                t = (s - largos[i]) / max(1e-9, largos[i + 1] - largos[i]); return pts[i].lerp(pts[i + 1], t)
        return pts[-1]
    obs = []
    for i in range(n):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.0027)
        o = _obj(f"{pref}_Corriente{i}", bm, [M["chispa"]], col, padre, liso=True)
        f = f0
        while f <= f1 + 2:
            s = (_tiempo(f, f_frio, lento) - f0) / vueltas * L + i * L / n
            o.location = punto(s); o.keyframe_insert("location", frame=f); f += 1
        for ff, v in ((1, False), (f0, True), (f1, False)):
            o.hide_render = o.hide_viewport = not v; o.keyframe_insert("hide_render", frame=ff); o.keyframe_insert("hide_viewport", frame=ff)
        obs.append(o)
    return obs
