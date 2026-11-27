# CARA DE MAITE (fase 2 AAA) · ojos 3D, párpados y pestañas · EKORUEDAS · 27-11-2026
# Se ejecuta dentro de construir_maite_v2.py (después de subdividir), con ARM y ME ya cargados:
#   CM = {"__name__": "cara_maite"}; exec(open(".../cara_maite.py", encoding="utf-8").read(), CM)
#   CM["construir_ojos"](ARM, ME)
# Idea: el ojo pintado de Tripo se quita (agujero con el borde de la propia malla, que ya tiene anillos alrededor
# del ojo), se pone un globo ocular 3D detrás con iris, pupila y córnea brillante, el borde del párpado se cierra
# contra el globo, y unas pestañas 3D siguen a la piel. Los parpadeos son shape keys con nombres de ARKit.
# Coordenadas en el espacio de la malla de Tripo (Maite mide 0,98 aquí; en escena el esqueleto va a escala 1,73).
import bpy, bmesh, math, colorsys
import numpy as np
from mathutils import Vector, Matrix, Quaternion

# ---------------------------------------------------------------- puntos de referencia (medidos en la malla, 27-11)
# 'L' = izquierda de ELLA (x > 0.02), como en ARKit ("eyeBlinkLeft" = su ojo izquierdo).
# sup = línea donde termina el delineado pintado (esquina exterior, centro, esquina interior): por debajo, globo.
OJOS = {
    "R": dict(caja=(-0.034, 0.011, 0.860, 0.897), sup=((-0.0255, 0.8775), (-0.0100, 0.8805), (0.0055, 0.8762)),
              inf=((-0.0255, 0.8775), (-0.0095, 0.8664), (0.0055, 0.8765))),
    "L": dict(caja=(0.026, 0.071, 0.862, 0.900), sup=((0.0640, 0.8832), (0.0490, 0.8846), (0.0365, 0.8788)),
              inf=((0.0640, 0.8835), (0.0480, 0.8703), (0.0365, 0.8790))),
}
IRIS_RADIO = 0.0084          # radio del iris visto de frente (el de la pintura de Tripo es grande, de película)
IRIS_COLOR = (0.20, 0.135, 0.06)   # avellana oscuro (la pintura de Tripo es marrón verdoso oscuro)


def _parabola(p):
    (x0, z0), (x1, z1), (x2, z2) = p
    A = np.array([[x0 * x0, x0, 1], [x1 * x1, x1, 1], [x2 * x2, x2, 1]]); a, b, c = np.linalg.solve(A, [z0, z1, z2])
    return lambda x: a * x * x + b * x + c


def _color_caras(me):
    m = me.data
    img = max((n.image for mt in m.materials for n in mt.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image
               and n.image.colorspace_settings.name == 'sRGB'), key=lambda i: i.size[0] * i.size[1])
    w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    uvl = m.uv_layers.active.data
    luv = np.empty(len(uvl) * 2, np.float32); uvl.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    nf = len(m.polygons); lt = np.empty(nf, np.int32); m.polygons.foreach_get('loop_total', lt)
    lf = np.repeat(np.arange(nf), lt)
    fuv = np.zeros((nf, 2)); np.add.at(fuv, lf, luv); fuv /= lt[:, None]
    samp = np.r_[luv * 0.5 + fuv[lf] * 0.5, fuv]; sf = np.r_[lf, np.arange(nf)]
    cs = px[np.clip((samp[:, 1] * h).astype(int), 0, h - 1), np.clip((samp[:, 0] * w).astype(int), 0, w - 1), :3]
    fc = np.zeros((nf, 3)); cnt = np.zeros(nf); np.add.at(fc, sf, cs); np.add.at(cnt, sf, 1)
    return fc / cnt[:, None]


def _es_piel(c):
    h, s, v = colorsys.rgb_to_hsv(*c)
    return (h < 0.12 or h > 0.95) and s > 0.22 and v > 0.5


def _esfera(P, rmin=0.011):
    P = np.asarray(P, float); A = np.c_[2 * P, np.ones(len(P))]; f = (P ** 2).sum(1)
    sol, *_ = np.linalg.lstsq(A, f, rcond=None); c = sol[:3]; r = math.sqrt(max(1e-12, sol[3] + (c ** 2).sum()))
    return Vector(c), r


def _bucle(bordes):
    """Bucle cerrado más grande formado por las aristas de borde dadas (ignora agujeritos sueltos)."""
    vec = {}
    for e in bordes:
        a, b = e.verts; vec.setdefault(a, []).append(b); vec.setdefault(b, []).append(a)
    # componentes conexas
    vistos = set(); comps = []
    for v in vec:
        if v in vistos: continue
        pila = [v]; vistos.add(v); c = []
        while pila:
            x = pila.pop(); c.append(x)
            for o in vec[x]:
                if o not in vistos: vistos.add(o); pila.append(o)
        comps.append(c)
    comp = max(comps, key=len)
    ini = min(comp, key=lambda v: len(vec[v]) != 2)        # mejor empezar en un vértice normal
    bucle = [ini]; usados = {ini}; prev = None; cur = ini
    while True:
        cand = [o for o in vec[cur] if o not in usados]
        if not cand:
            break
        if prev is not None and len(cand) > 1:              # en un cruce, seguir lo más recto posible
            d0 = (cur.co - prev.co).normalized()
            cand.sort(key=lambda o: -(o.co - cur.co).normalized().dot(d0))
        prev, cur = cur, cand[0]; bucle.append(cur); usados.add(cur)
    return bucle


def repintar_piel(me, caras, color=None, margen_px=3, ruido=0.006, semilla=3, colores=None):
    """Pinta en la textura 4K las caras dadas con color de piel (quita el ojo/delineado pintados de Tripo).
    Si no se da color, se toma la media de la piel de alrededor."""
    m = me.data
    img = max((n.image for mt in m.materials for n in mt.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image
               and n.image.colorspace_settings.name == 'sRGB'), key=lambda i: i.size[0] * i.size[1])
    w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    uvl = m.uv_layers.active.data; rng = np.random.default_rng(semilla)
    if color is None: color = (0.93, 0.56, 0.42)
    col = np.array(color, np.float32)
    pintados = 0
    for fi in caras:
        p = m.polygons[fi]
        uv = np.array([uvl[li].uv[:] for li in p.loop_indices], np.float64) * [w, h]
        c = uv.mean(0); uv = c + (uv - c) * (1 + margen_px / max(1.0, np.linalg.norm(uv - c, axis=1).mean()))
        x0, y0 = np.floor(uv.min(0)).astype(int); x1, y1 = np.ceil(uv.max(0)).astype(int)
        x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(w - 1, x1), min(h - 1, y1)
        if x1 < x0 or y1 < y0: continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        dentro = np.zeros(gx.shape, bool)
        for k in range(1, len(uv) - 1):                          # abanico de triángulos
            a, b, cc = uv[0], uv[k], uv[k + 1]
            d1 = (gx - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (gy - b[1])
            d2 = (gx - cc[0]) * (b[1] - cc[1]) - (b[0] - cc[0]) * (gy - cc[1])
            d3 = (gx - a[0]) * (cc[1] - a[1]) - (cc[0] - a[0]) * (gy - a[1])
            neg = (d1 < 0) | (d2 < 0) | (d3 < 0); pos = (d1 > 0) | (d2 > 0) | (d3 > 0)
            dentro |= ~(neg & pos)
        if not dentro.any(): continue
        blk = px[y0:y1 + 1, x0:x1 + 1, :3]
        cc_ = np.array(colores[fi], np.float32) if colores is not None and fi in colores else col
        blk[dentro] = cc_ + rng.normal(0, ruido, (int(dentro.sum()), 3)).astype(np.float32)
        pintados += int(dentro.sum())
    img.pixels.foreach_set(px.ravel()); img.update()
    try: img.pack()
    except Exception as e: print("PACK", e)
    print("REPINTADO", len(caras), "caras,", pintados, "píxeles", flush=True)


def colores_locales(cen, fc, caras, k=10, excluir=()):
    """Para cada cara a repintar, la media del color de las k caras de piel más cercanas (así no se nota el parche)."""
    ex = set(excluir) | set(caras)
    piel = np.array([i for i in range(len(cen)) if i not in ex and _es_piel(fc[i])])
    S = cen[piel]; out = {}
    for fi in caras:
        d = np.linalg.norm(S - cen[fi], axis=1); j = np.argsort(d)[:k]
        out[fi] = tuple(float(x) for x in np.average(fc[piel[j]], axis=0, weights=1 / (d[j] + 1e-4)))
    return out


def material_ojo(nombre, iris_rgb, theta_iris, theta_pupila):
    mt = bpy.data.materials.new(nombre); mt.use_nodes = True; nt = mt.node_tree; N = nt.nodes; L = nt.links
    bs = N["Principled BSDF"]; bs.location = (700, 0)
    tc = N.new("ShaderNodeTexCoord"); tc.location = (-1400, 0)
    sep = N.new("ShaderNodeSeparateXYZ"); sep.location = (-1200, 0); L.new(tc.outputs["Object"], sep.inputs[0])
    nrm = N.new("ShaderNodeVectorMath"); nrm.operation = 'NORMALIZE'; nrm.location = (-1200, -200); L.new(tc.outputs["Object"], nrm.inputs[0])
    sz = N.new("ShaderNodeSeparateXYZ"); sz.location = (-1000, -200); L.new(nrm.outputs["Vector"], sz.inputs[0])
    ang = N.new("ShaderNodeMath"); ang.operation = 'ARCCOSINE'; ang.location = (-800, -200); L.new(sz.outputs["Z"], ang.inputs[0])
    # ángulo alrededor del eje (para las fibras del iris)
    at = N.new("ShaderNodeMath"); at.operation = 'ARCTAN2'; at.location = (-800, 100)
    L.new(sep.outputs["Y"], at.inputs[0]); L.new(sep.outputs["X"], at.inputs[1])
    fib = N.new("ShaderNodeTexNoise"); fib.location = (-600, 200); fib.noise_dimensions = '2D'
    fib.inputs["Scale"].default_value = 3.0; fib.inputs["Detail"].default_value = 8.0
    cmb = N.new("ShaderNodeCombineXYZ"); cmb.location = (-700, 300)
    mul = N.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 14.0; L.new(at.outputs[0], mul.inputs[0])
    mul2 = N.new("ShaderNodeMath"); mul2.operation = 'MULTIPLY'; mul2.inputs[1].default_value = 1.5 / max(1e-4, theta_iris); L.new(ang.outputs[0], mul2.inputs[0])
    L.new(mul.outputs[0], cmb.inputs["X"]); L.new(mul2.outputs[0], cmb.inputs["Y"]); L.new(cmb.outputs[0], fib.inputs["Vector"])
    # colores del iris: base muestreada, fibras claras, anillo oscuro exterior
    rmp = N.new("ShaderNodeValToRGB"); rmp.location = (-350, 200)
    base = Vector(iris_rgb)
    rmp.color_ramp.elements[0].color = (*(base * 0.30), 1); rmp.color_ramp.elements[1].color = (*(base * 1.25), 1)
    rmp.color_ramp.elements[1].position = 0.8
    e = rmp.color_ramp.elements.new(0.55); e.color = (*(Vector((0.10, 0.12, 0.05)) * 0.9), 1)    # motas verdosas
    # u = ángulo / ángulo del iris (0 centro, 1 borde del iris)
    u = N.new("ShaderNodeMath"); u.operation = 'DIVIDE'; u.inputs[1].default_value = theta_iris; L.new(ang.outputs[0], u.inputs[0]); u.location = (-600, -200)
    up = N.new("ShaderNodeValue"); up.name = "Pupila"; up.label = "Pupila (0.25-0.6)"; up.outputs[0].default_value = theta_pupila / theta_iris; up.location = (-600, -400)
    # fibras -> rampa
    L.new(fib.outputs["Fac"], rmp.inputs["Fac"])
    # anillo límbico: oscurece al acercarse al borde del iris
    lim = N.new("ShaderNodeMapRange"); lim.location = (-350, -100)
    lim.inputs["From Min"].default_value = 0.72; lim.inputs["From Max"].default_value = 1.0
    lim.inputs["To Min"].default_value = 1.0; lim.inputs["To Max"].default_value = 0.35; L.new(u.outputs[0], lim.inputs["Value"])
    iris = N.new("ShaderNodeMix"); iris.data_type = 'RGBA'; iris.blend_type = 'MULTIPLY'; iris.location = (-150, 150)
    iris.inputs["Factor"].default_value = 1.0; L.new(rmp.outputs["Color"], iris.inputs[6]); L.new(lim.outputs["Result"], iris.inputs[7])
    # pupila
    pu = N.new("ShaderNodeMath"); pu.operation = 'LESS_THAN'; pu.location = (-350, -300); L.new(u.outputs[0], pu.inputs[0]); L.new(up.outputs[0], pu.inputs[1])
    conp = N.new("ShaderNodeMix"); conp.data_type = 'RGBA'; conp.location = (50, 100)
    L.new(pu.outputs[0], conp.inputs["Factor"]); L.new(iris.outputs[2], conp.inputs[6]); conp.inputs[7].default_value = (0.008, 0.007, 0.007, 1)
    # esclera (blanco roto, algo rosado hacia los lados) y borde suave iris-esclera
    scl = N.new("ShaderNodeMapRange"); scl.location = (-350, -500)
    scl.inputs["From Min"].default_value = 1.0; scl.inputs["From Max"].default_value = 3.2
    L.new(u.outputs[0], scl.inputs["Value"])
    esc = N.new("ShaderNodeMix"); esc.data_type = 'RGBA'; esc.location = (-150, -400)
    L.new(scl.outputs["Result"], esc.inputs["Factor"]); esc.inputs[6].default_value = (0.80, 0.77, 0.73, 1); esc.inputs[7].default_value = (0.70, 0.56, 0.52, 1)
    borde = N.new("ShaderNodeMapRange"); borde.location = (-150, -150)
    borde.inputs["From Min"].default_value = 0.97; borde.inputs["From Max"].default_value = 1.06; L.new(u.outputs[0], borde.inputs["Value"])
    fin = N.new("ShaderNodeMix"); fin.data_type = 'RGBA'; fin.location = (300, 0)
    L.new(borde.outputs["Result"], fin.inputs["Factor"]); L.new(conp.outputs[2], fin.inputs[6]); L.new(esc.outputs[2], fin.inputs[7])
    L.new(fin.outputs[2], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.35; bs.inputs["Subsurface Weight"].default_value = 0.12
    bs.inputs["Subsurface Radius"].default_value = (1.0, 0.5, 0.4); bs.inputs["Subsurface Scale"].default_value = 0.002
    # el iris está algo hundido: relieve
    bu = N.new("ShaderNodeBump"); bu.location = (450, -300); bu.inputs["Strength"].default_value = 0.25; bu.inputs["Distance"].default_value = 0.0006
    L.new(fib.outputs["Fac"], bu.inputs["Height"]); L.new(bu.outputs["Normal"], bs.inputs["Normal"])
    return mt


def material_cornea():
    mt = bpy.data.materials.get("MAITE_cornea") or bpy.data.materials.new("MAITE_cornea"); mt.use_nodes = True
    bs = mt.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (1, 1, 1, 1); bs.inputs["Roughness"].default_value = 0.0
    bs.inputs["Transmission Weight"].default_value = 1.0; bs.inputs["IOR"].default_value = 1.336
    bs.inputs["Specular IOR Level"].default_value = 0.8
    return mt


def material_simple(nombre, color, rug=0.5, sss=0.0, coat=0.0):
    mt = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre); mt.use_nodes = True
    bs = mt.node_tree.nodes["Principled BSDF"]; bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = rug
    if sss: bs.inputs["Subsurface Weight"].default_value = sss; bs.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.3); bs.inputs["Subsurface Scale"].default_value = 0.003
    if coat: bs.inputs["Coat Weight"].default_value = coat; bs.inputs["Coat Roughness"].default_value = 0.1
    return mt


def construir_ojos(arm, me, col_ojo=None):
    m = me.data
    fc = _color_caras(me)
    cen = np.empty(len(m.polygons) * 3, np.float32); m.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    datos = {}
    bm = bmesh.new(); bm.from_mesh(m); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
    mat_borde = material_simple("MAITE_parpado_borde", (0.70, 0.36, 0.30), rug=0.5, sss=0.25, coat=0.05)
    m.materials.append(mat_borde); i_borde = len(m.materials) - 1
    mat_cuenca = material_simple("MAITE_cuenca", (0.16, 0.06, 0.05), rug=0.4, coat=0.5)
    m.materials.append(mat_cuenca); i_cuenca = len(m.materials) - 1
    mat_lin = material_simple("MAITE_delineado", (0.030, 0.018, 0.016), rug=0.45)
    m.materials.append(mat_lin); i_lin = len(m.materials) - 1
    for lado, O in OJOS.items():
        x0, x1, z0, z1 = O["caja"]; top = _parabola(O["sup"]); bot = _parabola(O["inf"])
        xs = sorted(p[0] for p in (O["sup"][0], O["sup"][2]))
        sel = set(); lin = set()
        for i, c in enumerate(cen):
            if not (x0 < c[0] < x1 and z0 < c[2] < z1 and c[1] < -0.02): continue
            if xs[0] < c[0] < xs[1] and bot(c[0]) < c[2] < top(c[0]):
                sel.add(i)                                  # dentro de la abertura del ojo: fuera (globo detrás)
            elif not _es_piel(fc[i]) and xs[0] - 0.007 < c[0] < xs[1] + 0.005 and bot(c[0]) - 0.007 < c[2] < top(c[0]) + 0.0105:
                lin.add(i)                                  # delineado, pestañas y restos de blanco pintados: a piel
        datos_lin = datos.setdefault("_repintar", set()); datos_lin |= lin
        # mayor componente conexa
        caras = [bm.faces[i] for i in sel]; vis = set(); grupos = []
        for f in caras:
            if f.index in vis: continue
            pila = [f]; vis.add(f.index); g = []
            while pila:
                x = pila.pop(); g.append(x)
                for e in x.edges:
                    for o in e.link_faces:
                        if o.index in sel and o.index not in vis: vis.add(o.index); pila.append(o)
            grupos.append(g)
        g = max(grupos, key=len)
        # superficie pintada del ojo -> esfera del globo
        P = [tuple(v.co) for f in g for v in f.verts]
        iris_cols = [fc[f.index] for f in g if 0.12 < max(fc[f.index]) and min(fc[f.index]) < 0.6]
        datos[lado] = dict(P=P, caras=[f.index for f in g], iris=np.mean(iris_cols, axis=0) if iris_cols else (0.2, 0.22, 0.14))
        # color de piel de alrededor del ojo
        alrededor = [i for i, c in enumerate(cen) if x0 < c[0] < x1 and z0 - 0.01 < c[2] < z1 and c[1] < -0.02 and _es_piel(fc[i])]
        datos[lado]["piel"] = np.median(fc[alrededor], axis=0) if alrededor else np.array((0.93, 0.56, 0.42))
        print("OJO", lado, len(g), "caras", flush=True)
    rep = datos.pop("_repintar", set())
    piel_media = np.mean([d["piel"] for d in datos.values()], axis=0)
    hueco = [i for d in datos.values() for i in d["caras"]]
    repintar_piel(me, sorted(rep), tuple(float(x) for x in piel_media), colores=colores_locales(cen, fc, sorted(rep), excluir=hueco))
    # borrar las caras de los dos ojos a la vez
    borrar = [bm.faces[i] for d in datos.values() for i in d["caras"]]
    bmesh.ops.delete(bm, geom=borrar, context='FACES')
    # tapar los agujeritos que Tripo dejó junto a los ojos (el agujero grande del ojo no se toca)
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=10)
    bm.verts.ensure_lookup_table()
    for lado, d in datos.items():
        O = OJOS[lado]; top = _parabola(O["sup"])
        # bucle del agujero de este ojo
        cx = np.mean([p[0] for p in d["P"]]); cz = np.mean([p[2] for p in d["P"]])
        bordes = [e for e in bm.edges if e.is_boundary and all(abs(v.co.x - cx) < 0.03 and abs(v.co.z - cz) < 0.02 and v.co.y < -0.02 for v in e.verts)]
        bucle = _bucle(bordes)
        print("AGUJERO", lado, len(bordes), "aristas de borde,", len(bucle), "en el bucle", flush=True)
        # el borde se ajusta a las dos curvas del diseño (arriba el delineado, abajo el párpado inferior)
        bot = _parabola(O["inf"])
        for v in bucle:
            zt, zb = top(v.co.x), bot(v.co.x)
            v.co.z = zt if abs(v.co.z - zt) < abs(v.co.z - zb) else zb
        for _ in range(3):
            n = len(bucle); nuevos = []
            for k, v in enumerate(bucle):
                a, b = bucle[k - 1].co, bucle[(k + 1) % n].co; nuevos.append(v.co * 0.5 + (a + b) * 0.25)
            for v, p in zip(bucle, nuevos): v.co.x, v.co.y, v.co.z = p.x, p.y, p.z
        # esfera del globo: su frente queda donde estaba el ojo pintado; radio entre 9 y 18 mm (unidades de malla)
        Cf, Rf = _esfera(d["P"])
        Pm = Vector(np.mean(np.asarray(d["P"]), axis=0)); nrm = (Pm - Cf).normalized()
        if nrm.y > -0.3: nrm = Vector((0, -1, 0))          # por si el ajuste sale raro: hacia delante
        Pc = Cf + nrm * Rf if Rf < 0.05 else Pm
        R = min(max(Rf, 0.0115), 0.018)
        # ningún punto del borde puede quedar dentro del globo
        for v in bucle:
            dv = v.co - Pc; dl = -dv.dot(nrm); a2 = (dv + nrm * dl).length_squared
            if dl > 1e-5: R = min(R, (a2 + dl * dl) / (2 * dl) - 0.0005)
        # ni la piel de alrededor: el globo no puede asomar por fuera del agujero
        sbv = set(bucle)
        for v in bm.verts:
            if v in sbv or (v.co - Pc).length > 0.024 or v.co.y > Pc.y + 0.02: continue
            dv = v.co - Pc; dl = -dv.dot(nrm); a2 = (dv + nrm * dl).length_squared
            if dl > 2e-4 and a2 > 1e-8: R = min(R, (a2 + dl * dl) / (2 * dl) - 0.0003)
        R = max(R, 0.009)
        Pc = Pc - nrm * 0.0003                               # un pelo por detrás de donde estaba la pintura
        C = Pc - nrm * R
        # párpado con grosor: 1) un milímetro de piel hacia dentro  2) pliegue oscuro hasta tocar el globo
        sb = set(bucle)
        ext = bmesh.ops.extrude_edge_only(bm, edges=[e for e in bm.edges if e.is_boundary and e.verts[0] in sb and e.verts[1] in sb])
        nv1 = [x for x in ext["geom"] if isinstance(x, bmesh.types.BMVert)]
        for v in nv1:
            dv = v.co - C; dist = dv.length
            v.co = C + dv.normalized() * max(R + 0.0004, dist - 0.0009)
        for f in [x for x in ext["geom"] if isinstance(x, bmesh.types.BMFace)]:
            f.material_index = i_borde; f.smooth = True
        sb1 = set(nv1)
        ext2 = bmesh.ops.extrude_edge_only(bm, edges=[e for e in bm.edges if e.is_boundary and e.verts[0] in sb1 and e.verts[1] in sb1])
        nv = [x for x in ext2["geom"] if isinstance(x, bmesh.types.BMVert)]
        for v in nv:
            dv = v.co - C; v.co = C + dv.normalized() * (R + 0.0002)
        for f in [x for x in ext2["geom"] if isinstance(x, bmesh.types.BMFace)]:
            f.material_index = i_cuenca; f.smooth = True
        nv = nv1 + nv
        d.update(C=C, R=R, nrm=nrm, bucle_v=bucle, borde_v=nv)
        print("GLOBO", lado, tuple(round(x, 4) for x in C), round(R, 4), flush=True)
    bm.verts.index_update()
    for d in datos.values():
        d["bucle"] = [v.index for v in d.pop("bucle_v")]; d["borde_int"] = [v.index for v in d.pop("borde_v")]
    bm.normal_update(); bm.to_mesh(m); bm.free(); m.update()
    # ---------------------------------------------------------------- dirección de la cara
    lat = (datos["L"]["C"] - datos["R"]["C"]); lat.z = 0; lat.normalize()
    adelante = lat.cross(Vector((0, 0, 1))).normalized()
    # ---------------------------------------------------------------- huesos de los ojos y de la mirada
    bpy.context.view_layer.objects.active = arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); eb = arm.data.edit_bones; cab = eb["mixamorig:Head"]
    for lado, d in datos.items():
        b = eb.new(f"Ojo_{lado}"); b.head = d["C"]; b.tail = d["C"] + adelante * 0.012; b.parent = cab; b.use_deform = False
    mid = (datos["L"]["C"] + datos["R"]["C"]) / 2
    t = eb.new("Mirada"); t.head = mid + adelante * 0.45; t.tail = t.head + Vector((0, 0, 0.02)); t.parent = cab; t.use_deform = False
    bpy.ops.object.mode_set(mode='OBJECT')
    for lado in datos:
        pb = arm.pose.bones[f"Ojo_{lado}"]; pb.rotation_mode = 'QUATERNION'
        c = pb.constraints.new('DAMPED_TRACK'); c.target = arm; c.subtarget = "Mirada"; c.track_axis = 'TRACK_Y'
    # ---------------------------------------------------------------- globos y córneas
    col = bpy.data.collections.get("MAITE_ojos") or bpy.data.collections.new("MAITE_ojos")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for lado, d in datos.items():
        C, R = d["C"], d["R"]
        th_i = math.asin(min(0.95, IRIS_RADIO / R)); th_p = th_i * 0.40
        iris_rgb = tuple(float(x) for x in (col_ojo or IRIS_COLOR))
        mt = material_ojo(f"MAITE_ojo_{lado}", iris_rgb, th_i, th_p)
        for nombre, radio, mat_ in ((f"MAITE_globo_{lado}", R, mt), (f"MAITE_cornea_{lado}", R + 0.00018, material_cornea())):
            bmg = bmesh.new(); bmesh.ops.create_uvsphere(bmg, u_segments=64, v_segments=40, radius=radio)
            md = bpy.data.meshes.new(nombre); bmg.to_mesh(md); bmg.free()
            for p in md.polygons: p.use_smooth = True
            o = bpy.data.objects.new(nombre, md); col.objects.link(o); md.materials.append(mat_)
            # +Z local del globo = hacia delante (el iris está en el polo +Z)
            q = Vector((0, 0, 1)).rotation_difference(adelante)
            o.matrix_world = Matrix.Translation(C) @ q.to_matrix().to_4x4()
            mw = o.matrix_world.copy(); bpy.context.view_layer.update()
            o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = f"Ojo_{lado}"
            o.matrix_world = mw
            if "cornea" in nombre:
                o.visible_shadow = False
        print("OJO_3D", lado, "iris", tuple(round(x, 3) for x in iris_rgb), flush=True)
    arm["ojos"] = str({k: (tuple(round(x, 5) for x in d["C"]), round(d["R"], 5)) for k, d in datos.items()})
    return datos, adelante


# ================================================================ PÁRPADOS (shape keys ARKit) Y PESTAÑAS 3D
def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0); return t * t * (3 - 2 * t)


def _rot_puntos(P, C, eje, ang):
    """Gira los puntos P (N,3) alrededor del eje que pasa por C; ang puede ser un array (N,)."""
    k = np.asarray(eje, float); k = k / np.linalg.norm(k)
    v = P - np.asarray(C); a = np.asarray(ang, float)[:, None] if np.ndim(ang) else ang
    c, s_ = np.cos(a), np.sin(a)
    return np.asarray(C) + v * c + np.cross(k, v) * s_ + k * (v @ k)[:, None] * (1 - c)


def preparar_parpados(arm, me, datos, adelante, semilla=7):
    m = me.data; rng = np.random.default_rng(semilla)
    lat = (datos["L"]["C"] - datos["R"]["C"]); lat.z = 0; lat.normalize(); up = Vector((0, 0, 1))
    co0 = np.empty(len(m.vertices) * 3, np.float64); m.vertices.foreach_get('co', co0); co0 = co0.reshape(-1, 3)
    info = {}
    for lado, d in datos.items():
        C = np.array(d["C"]); bucle = d["bucle"]; P = co0[bucle]
        # esquinas: extremos del bucle a lo largo del eje lateral
        t = (P - C) @ np.array(lat); i0, i1 = int(np.argmin(t)), int(np.argmax(t))
        A, B = P[i0], P[i1]
        def encima(Q):
            # altura sobre la recta de las esquinas (en el plano de la cara)
            u = (Q - A); ab = (B - A); ab /= np.linalg.norm(ab)
            perp = u - np.outer(u @ ab, ab)
            return perp @ np.array(up)
        h = encima(P)
        sup = [bucle[k] for k in range(len(bucle)) if h[k] > 0.0003]
        inf = [bucle[k] for k in range(len(bucle)) if h[k] < -0.0003]
        print("BUCLE", lado, len(bucle), "h", round(float(h.min()), 4), round(float(h.max()), 4), "esquinas", np.round(A, 4), np.round(B, 4), flush=True)
        if len(sup) < 3 or len(inf) < 3:                  # por si el bucle sale raro: arriba/abajo del centro
            sup = [bucle[k] for k in range(len(bucle)) if P[k][2] > C[2] + 0.0005]
            inf = [bucle[k] for k in range(len(bucle)) if P[k][2] < C[2] - 0.0005]
        Ps, Pi = co0[sup], co0[inf]
        # ángulo de apertura (en el plano perpendicular al eje lateral)
        ptop = Ps[np.argmax(Ps[:, 2])]; pbot = Pi[np.argmin(Pi[:, 2])]
        def ang2(Q):
            v = Q - C; v = v - (v @ np.array(lat)) * np.array(lat); return math.atan2(v @ np.array(up), v @ np.array(adelante))
        th = ang2(ptop) - ang2(pbot)
        # pesos de la zona del párpado superior e inferior
        caja = (np.abs(co0[:, 0] - C[0]) < 0.03) & (np.abs(co0[:, 2] - C[2]) < 0.025) & (co0[:, 1] < C[1] + 0.012)
        idx = np.where(caja)[0]; Q = co0[idx]
        dsup = np.min(np.linalg.norm(Q[:, None, :] - Ps[None, :, :], axis=2), axis=1)
        dinf = np.min(np.linalg.norm(Q[:, None, :] - Pi[None, :, :], axis=2), axis=1)
        hq = encima(Q)
        semi = np.linalg.norm(B - A) / 2
        dcor = np.minimum(np.linalg.norm(Q - A, axis=1), np.linalg.norm(Q - B, axis=1))
        fcor = _ss(0.0, 0.45 * semi, dcor)
        wsup = (1 - _ss(0.0006, 0.0068, dsup)) * _ss(-0.0004, 0.0012, hq) * fcor
        winf = (1 - _ss(0.0004, 0.0042, dinf)) * _ss(-0.0004, 0.0012, -hq) * fcor
        # el borde interior (extruido) va con su vértice del borde
        for k in d["borde_int"]:
            j = np.where(idx == k)[0]
            if len(j):
                q = co0[k]; js = np.argmin(np.linalg.norm(Ps - q, axis=1)); ji = np.argmin(np.linalg.norm(Pi - q, axis=1))
                if np.linalg.norm(Ps[js] - q) < np.linalg.norm(Pi[ji] - q):
                    wsup[j] = max(wsup[j][0], 1.0 * fcor[j][0]); winf[j] = 0
                else:
                    winf[j] = max(winf[j][0], 1.0 * fcor[j][0]); wsup[j] = 0
        info[lado] = dict(C=C, idx=idx, wsup=wsup, winf=winf, th=th, sup=sup, inf=inf, A=A, B=B)
        print("PARPADOS", lado, "apertura", round(math.degrees(th), 1), "grados", len(sup), len(inf), flush=True)
    # ------------------------------------------------------------ pestañas 3D (parte de la malla, siguen a la piel)
    bm = bmesh.new(); bm.from_mesh(m)
    mat_p = material_simple("MAITE_pestanas", (0.020, 0.013, 0.011), rug=0.5)
    m.materials.append(mat_p); i_p = len(m.materials) - 1
    i_lin = next((k for k, mt in enumerate(m.materials) if mt and mt.name.startswith("MAITE_delineado")), None)
    if i_lin is None:
        m.materials.append(material_simple("MAITE_delineado", (0.030, 0.018, 0.016), rug=0.45)); i_lin = len(m.materials) - 1
    bm.verts.ensure_lookup_table()
    origen = []                                  # (índice del vértice nuevo, vértice del borde del que nace)
    for lado, I in info.items():
        C = Vector(I["C"]); A, B = Vector(I["A"]), Vector(I["B"])
        # delineado: banda oscura lisa sobre el borde superior, más ancha hacia fuera y con un rabito final
        pts_s = sorted(I["sup"], key=lambda k: (Vector(co0[k]) - A).dot(B - A))
        cs_ = [Vector(co0[k]) for k in pts_s]
        exterior_es_B = (B - A).dot(lat) * (1 if lado == "L" else -1) > 0
        prev = None; nseg = 40
        largo = [0.0]
        for a_, b_ in zip(cs_[:-1], cs_[1:]): largo.append(largo[-1] + (b_ - a_).length)
        for j in range(nseg + 5):
            if j <= nseg:
                s_ = j / nseg * largo[-1]; k = max(1, min(len(cs_) - 1, int(np.searchsorted(largo, s_))))
                f_ = (s_ - largo[k - 1]) / max(1e-9, largo[k] - largo[k - 1]); base = cs_[k - 1].lerp(cs_[k], f_)
                pref = pts_s[k - 1] if f_ < 0.5 else pts_s[k]
                tt = j / nseg; tout = tt if exterior_es_B else 1 - tt
            else:                                            # rabito hacia la sien
                ext = (j - nseg) / 4.0
                fin = cs_[-1] if exterior_es_B else cs_[0]; ant = cs_[-2] if exterior_es_B else cs_[1]
                dirx = (fin - ant).normalized()
                base = fin + dirx * 0.0011 * ext + up * 0.0007 * ext * ext
                pref = pts_s[-1] if exterior_es_B else pts_s[0]; tout = 1.0
                if not exterior_es_B: continue
            radial = (base - C); radial = radial - lat * radial.dot(lat); radial.normalize()
            nsup = (base - C).normalized()
            grosor = (0.00045 + 0.00095 * tout ** 1.3) if j <= nseg else 0.0013 * (1 - (j - nseg) / 4.5)
            va = bm.verts.new(base + nsup * 0.00012 - radial * 0.00005); vb = bm.verts.new(base + nsup * 0.00012 + radial * grosor)
            origen += [(va, pref), (vb, pref)]
            if prev:
                f2 = bm.faces.new((prev[0], prev[1], vb, va)); f2.material_index = i_lin; f2.smooth = True
            prev = (va, vb)
        if not exterior_es_B:                                 # rabito del lado A (cuando la sien está en A)
            fin = cs_[0]; ant = cs_[1]; dirx = (fin - ant).normalized()
            prev = None
            for e_ in range(5):
                ext = e_ / 4.0; base = fin + dirx * 0.0011 * ext + up * 0.0007 * ext * ext
                radial = (base - C); radial = radial - lat * radial.dot(lat); radial.normalize(); nsup = (base - C).normalized()
                grosor = 0.0014 * (1 - ext * 0.9)
                va = bm.verts.new(base + nsup * 0.00012 - radial * 0.00005); vb = bm.verts.new(base + nsup * 0.00012 + radial * grosor)
                origen += [(va, pts_s[0]), (vb, pts_s[0])]
                if prev:
                    f2 = bm.faces.new((prev[0], prev[1], vb, va)); f2.material_index = i_lin; f2.smooth = True
                prev = (va, vb)
        for fila, (lista, n, Lmin, Lmax, haciaarriba) in enumerate(((I["sup"], 64, 0.0024, 0.0050, 1), (I["sup"], 40, 0.0018, 0.0034, 1), (I["inf"], 22, 0.0007, 0.0014, -1))):
            pts = sorted(lista, key=lambda k: (Vector(co0[k]) - A).dot(B - A))
            cur = [Vector(co0[k]) for k in pts]
            if len(cur) < 3: continue
            largo = [0.0]
            for a_, b_ in zip(cur[:-1], cur[1:]): largo.append(largo[-1] + (b_ - a_).length)
            for j in range(n):
                s_ = (j + 0.5 + rng.uniform(-0.3, 0.3)) / n * largo[-1]
                k = max(1, min(len(cur) - 1, int(np.searchsorted(largo, s_))))
                f_ = (s_ - largo[k - 1]) / max(1e-9, largo[k] - largo[k - 1]); base = cur[k - 1].lerp(cur[k], f_)
                pref = pts[k - 1] if f_ < 0.5 else pts[k]
                exterior = (base - A).length / max(1e-6, (B - A).length)        # 0 esquina A, 1 esquina B
                hacia_fuera = exterior if (B - A).dot(lat) * (1 if lado == "L" else -1) > 0 else 1 - exterior
                L = (Lmin + (Lmax - Lmin) * (hacia_fuera ** 1.4)) * rng.uniform(0.85, 1.15)
                radial = (base - C); radial = radial - lat * radial.dot(lat); radial.normalize()
                d0 = (radial * 0.55 + adelante * 0.65).normalized()
                curva = up * haciaarriba
                lado_v = (d0.cross(curva)).normalized()
                lado_v = lado_v * 1.0
                ancho0 = 0.00024 if fila == 0 else 0.00018
                base = base - radial * 0.00025 + adelante * 0.0001 * fila
                prev = None
                for sgm in range(5):
                    tt = sgm / 4
                    p = base + d0 * (L * tt) + curva * (L * 0.55 * tt * tt) + lado_v * (rng.uniform(-0.2, 0.2) * L * tt)
                    w = ancho0 * (1 - tt * 0.88)
                    va = bm.verts.new(p - lado_v * w / 2); vb = bm.verts.new(p + lado_v * w / 2)
                    origen += [(va, pref), (vb, pref)]
                    if prev:
                        fc_ = bm.faces.new((prev[0], prev[1], vb, va)); fc_.material_index = i_p; fc_.smooth = True
                    prev = (va, vb)
    bm.verts.index_update()
    pares = [(v.index, k) for v, k in origen]
    bm.normal_update(); bm.to_mesh(m); bm.free(); m.update()
    # pesos del esqueleto: los de su vértice del borde
    grupos = {g.index: g for g in me.vertex_groups}
    for nuevo, ref in pares:
        for ge in m.vertices[ref].groups:
            grupos[ge.group].add([nuevo], ge.weight, 'REPLACE')
    print("PESTANAS", len(pares) // 10, "pelos", flush=True)
    # ------------------------------------------------------------ shape keys
    co = np.empty(len(m.vertices) * 3, np.float64); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    for lado, I in info.items():                 # añadir las pestañas a las zonas de peso
        nuevos = [(a, b) for a, b in pares if b in set(I["sup"]) | set(I["inf"])]
        if nuevos:
            pos = {k: j for j, k in enumerate(I["idx"])}
            extra_idx = np.array([a for a, b in nuevos])
            ws = np.array([I["wsup"][pos[b]] if b in pos else (1.0 if b in set(I["sup"]) else 0.0) for a, b in nuevos])
            wi = np.array([I["winf"][pos[b]] if b in pos else (1.0 if b in set(I["inf"]) else 0.0) for a, b in nuevos])
            I["idx"] = np.r_[I["idx"], extra_idx]; I["wsup"] = np.r_[I["wsup"], ws]; I["winf"] = np.r_[I["winf"], wi]
    return info



# ================================================================ BOCA: abertura, labios con grosor, dientes, encías, lengua
BOCA = dict(esq_d=(-0.0032, 0.8325), esq_i=(0.0436, 0.8325), sup_c=(0.0205, 0.8350), inf_c=(0.0210, 0.8297))


def _reindexar(me, puntos):
    from mathutils import kdtree
    m = me.data; kd = kdtree.KDTree(len(m.vertices))
    for v in m.vertices: kd.insert(v.co, v.index)
    kd.balance()
    return [kd.find(Vector(p))[1] for p in puntos]


def _caja_redonda(bm, centro, X, Y, Z, sx, sy, sz, mat_i, segs=2):
    """Caja de esquinas redondeadas (para dientes): cubo subdividido y 'inflado' hacia una superelipse.
    Devuelve (desde, hasta): el tramo de índices de sus vértices (se añaden al final de la malla)."""
    bm.verts.ensure_lookup_table(); n0 = len(bm.verts)
    r = bmesh.ops.create_cube(bm, size=2.0)
    aristas = list({e for v in r["verts"] for e in v.link_edges})
    bmesh.ops.subdivide_edges(bm, edges=aristas, cuts=segs, use_grid_fill=True)
    bm.verts.ensure_lookup_table(); n1 = len(bm.verts)
    vs = [bm.verts[i] for i in range(n0, n1)]
    for v in vs:
        p = v.co.copy()
        k = (abs(p.x) ** 3 + abs(p.y) ** 3 + abs(p.z) ** 3) ** (1 / 3)
        p = p / max(k, 1e-6)
        v.co = centro + X * (p.x * sx) + Y * (p.y * sy) + Z * (p.z * sz)
    for f in {f for v in vs for f in v.link_faces}:
        f.material_index = mat_i; f.smooth = True
    return n0, n1


def _elipsoide(bm, centro, X, Y, Z, rx, ry, rz, mat_i, u=24, v=14):
    bm.verts.ensure_lookup_table(); n0 = len(bm.verts)
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    bm.verts.ensure_lookup_table(); n1 = len(bm.verts)
    vs = [bm.verts[i] for i in range(n0, n1)]
    for q in vs:
        p = q.co.copy(); q.co = centro + X * (p.x * rx) + Y * (p.y * ry) + Z * (p.z * rz)
    for f in {f for q in vs for f in q.link_faces}:
        f.material_index = mat_i; f.smooth = True
    return n0, n1


def construir_boca(arm, me, adelante, lat, datos_ojos):
    m = me.data; up = Vector((0, 0, 1)); F = adelante.copy(); X = lat.copy()
    B = BOCA; sup = _parabola((B["esq_d"], B["sup_c"], B["esq_i"])); inf = _parabola((B["esq_d"], B["inf_c"], B["esq_i"]))
    x0, x1 = B["esq_d"][0], B["esq_i"][0]
    # posiciones de los bucles de los ojos (los índices cambian al borrar la boca)
    for d in datos_ojos.values():
        d["bucle_co"] = [tuple(m.vertices[i].co) for i in d["bucle"]]; d["borde_co"] = [tuple(m.vertices[i].co) for i in d["borde_int"]]
    cen = np.empty(len(m.polygons) * 3, np.float32); m.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    sel = [i for i, c in enumerate(cen) if x0 + 0.0008 < c[0] < x1 - 0.0008 and inf(c[0]) < c[2] < sup(c[0]) and c[1] < -0.04]
    bm = bmesh.new(); bm.from_mesh(m); bm.faces.ensure_lookup_table()
    mats = {}
    for nombre, col, rug, sss, coat in (("MAITE_labio_int", (0.62, 0.24, 0.24), 0.3, 0.3, 0.5), ("MAITE_boca_int", (0.16, 0.035, 0.04), 0.5, 0.0, 0.3),
                                         ("MAITE_dientes", (0.86, 0.84, 0.78), 0.28, 0.15, 0.35), ("MAITE_encias", (0.70, 0.27, 0.29), 0.35, 0.3, 0.4),
                                         ("MAITE_lengua", (0.66, 0.26, 0.27), 0.45, 0.35, 0.25)):
        m.materials.append(material_simple(nombre, col, rug=rug, sss=sss, coat=coat)); mats[nombre] = len(m.materials) - 1
    fc = _color_caras(me)
    restos = [i for i, c in enumerate(cen) if i not in set(sel) and x0 - 0.006 < c[0] < x1 + 0.006 and inf(c[0]) - 0.005 < c[2] < sup(c[0]) + 0.004
              and c[1] < -0.04 and not _es_piel(fc[i])]
    if restos: repintar_piel(me, restos, colores=colores_locales(cen, fc, restos, excluir=sel))
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in sel], context='FACES')
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=10)
    cx = (x0 + x1) / 2; cz = (B["sup_c"][1] + B["inf_c"][1]) / 2
    bordes = [e for e in bm.edges if e.is_boundary and all(abs(v.co.x - cx) < 0.032 and abs(v.co.z - cz) < 0.012 and v.co.y < -0.03 for v in e.verts)]
    bucle = _bucle(bordes)
    print("BOCA agujero", len(sel), "caras,", len(bordes), "aristas,", len(bucle), "en el bucle", flush=True)
    for v in bucle:
        zt, zb = sup(v.co.x), inf(v.co.x)
        v.co.z = zt if abs(v.co.z - zt) < abs(v.co.z - zb) else zb
    for _ in range(3):
        n = len(bucle); nuevos = []
        for k, v in enumerate(bucle):
            a, b = bucle[k - 1].co, bucle[(k + 1) % n].co; nuevos.append(v.co * 0.5 + (a + b) * 0.25)
        for v, p in zip(bucle, nuevos): v.co.x, v.co.y, v.co.z = p.x, p.y, p.z
    O = sum((v.co for v in bucle), Vector()) / len(bucle)
    O.y = min(v.co.y for v in bucle) * 0.5 + O.y * 0.5
    # labios con grosor: 1) cara interna del labio (rosa húmedo)  2) hacia dentro, oscuro
    sb = set(bucle)
    e1 = bmesh.ops.extrude_edge_only(bm, edges=[e for e in bm.edges if e.is_boundary and e.verts[0] in sb and e.verts[1] in sb])
    v1 = [x for x in e1["geom"] if isinstance(x, bmesh.types.BMVert)]
    for v in v1:
        dz = v.co.z - O.z
        v.co = v.co - F * 0.0022 - up * (0.0004 if dz > 0 else -0.0004)
    for f in [x for x in e1["geom"] if isinstance(x, bmesh.types.BMFace)]: f.material_index = mats["MAITE_labio_int"]; f.smooth = True
    sb1 = set(v1)
    e2 = bmesh.ops.extrude_edge_only(bm, edges=[e for e in bm.edges if e.is_boundary and e.verts[0] in sb1 and e.verts[1] in sb1])
    v2 = [x for x in e2["geom"] if isinstance(x, bmesh.types.BMVert)]
    for v in v2:
        dz = v.co.z - O.z
        v.co = v.co - F * 0.0055 + up * (0.0014 if dz > 0 else -0.0014)
    for f in [x for x in e2["geom"] if isinstance(x, bmesh.types.BMFace)]: f.material_index = mats["MAITE_boca_int"]; f.smooth = True
    # ---- piezas de dentro (en el marco de la boca: X lateral, F hacia delante, up)
    bm.verts.index_update(); bm.verts.ensure_lookup_table()
    idx_bucle = [v.index for v in bucle]; idx_v1 = [v.index for v in v1]; idx_v2 = [v.index for v in v2]
    from mathutils.bvhtree import BVHTree
    bvh_piel = BVHTree.FromBMesh(bm)
    abertura = [((v.co - O).dot(X), (v.co - O).dot(up)) for v in bucle]
    partes = {"dientes_sup": [], "dientes_inf": [], "encia_sup": [], "encia_inf": [], "lengua": [], "saco": []}   # tramos de índices
    anchos = [0.0043, 0.0037, 0.0035, 0.0032, 0.0031, 0.0030]
    altos_s = [0.0050, 0.0044, 0.0047, 0.0041, 0.0038, 0.0035]
    z_borde_sup = O.z - 0.0007                     # filo de los dientes de arriba
    for fila, (r_arco, prof, esc, signo) in enumerate(((0.0185, 0.0026, 1.0, 1), (0.0165, 0.0040, 0.88, -1))):
        s_acum = 0.0
        for k, (w_, h_) in enumerate(zip(anchos, altos_s)):
            w_ *= esc; h_ *= esc * (0.85 if signo < 0 else 1.0)
            for lado_s in (-1, 1):
                s_ = (s_acum + w_ / 2) * lado_s; phi = s_ / r_arco
                pos = O + X * (r_arco * math.sin(phi)) - F * (prof + r_arco * (1 - math.cos(phi)))
                tang = (X * math.cos(phi) - F * math.sin(phi)).normalized()
                nrm_ = tang.cross(up).normalized()
                if signo > 0:
                    c_ = pos + up * (z_borde_sup - O.z + h_ / 2)
                else:
                    c_ = pos + up * (z_borde_sup - O.z - 0.0004 - h_ / 2)
                partes["dientes_sup" if signo > 0 else "dientes_inf"].append(
                    _caja_redonda(bm, c_, tang, nrm_, up, w_ * 0.47, 0.0012, h_ / 2, mats["MAITE_dientes"]))
            s_acum += w_
    # encías: anillos aplastados que siguen el arco de los dientes
    for signo, clave_, r_a, prof in ((1, "encia_sup", 0.0190, 0.0026), (-1, "encia_inf", 0.0170, 0.0040)):
        cprof = prof + r_a - 0.0006
        c_ = O - F * cprof + up * (signo * 0.0056 + (z_borde_sup - O.z) - (0.0004 if signo < 0 else 0))
        partes[clave_].append(_elipsoide(bm, c_, X, F, up, r_a, r_a * 0.92, 0.0026, mats["MAITE_encias"], 40, 12))
    partes["lengua"].append(_elipsoide(bm, O - F * 0.0185 + up * (z_borde_sup - O.z - 0.0050), X, F, up, 0.0105, 0.0120, 0.0034, mats["MAITE_lengua"], 28, 14))
    partes["saco"].append(_elipsoide(bm, O - F * 0.0235 + up * (-0.0012), X, F, up, 0.026, 0.0180, 0.0125, mats["MAITE_boca_int"], 36, 20))
    bm.verts.index_update(); bm.verts.ensure_lookup_table()
    info = {k: [i for (a_, b_) in tramos for i in range(a_, b_)] for k, tramos in partes.items()}
    # nada de dentro puede asomar por la piel: si un vértice está delante de la piel (y no detrás de la abertura), se mete
    def en_abertura(px_, pz_):
        dentro = False; n = len(abertura)
        for k in range(n):
            (ax, az), (bx, bz) = abertura[k - 1], abertura[k]
            if (az > pz_) != (bz > pz_) and px_ < (bx - ax) * (pz_ - az) / (bz - az + 1e-12) + ax: dentro = not dentro
        return dentro
    metidos = 0
    for k in ("saco", "lengua", "encia_sup", "encia_inf", "dientes_sup", "dientes_inf"):
        for i in info[k]:
            v = bm.verts[i]; p = v.co
            if en_abertura((p - O).dot(X) * 0.92, (p - O).dot(up) * 0.92): continue
            hit_f = bvh_piel.ray_cast(p, F, 0.08)[0]
            if hit_f is not None: continue                    # hay piel delante: está dentro de la cabeza
            hit_b, _n, _i, dist = bvh_piel.ray_cast(p, -F, 0.05)
            if hit_b is not None:
                v.co = p - F * (dist + 0.0015); metidos += 1
    print("BOCA vértices metidos dentro de la cara:", metidos, flush=True)
    info["bucle"] = idx_bucle; info["labio_int"] = idx_v1; info["boca_int"] = idx_v2
    info.update(O=tuple(O), F=tuple(F), X=tuple(X))
    bm.normal_update(); bm.to_mesh(m); bm.free(); m.update()
    # pesos del esqueleto de las piezas nuevas: todo a la cabeza
    g = me.vertex_groups.get("mixamorig:Head") or me.vertex_groups.new(name="mixamorig:Head")
    nuevas = [i for k in ("dientes_sup", "dientes_inf", "encia_sup", "encia_inf", "lengua", "saco") for i in info[k]]
    g.add(nuevas, 1.0, 'REPLACE')
    # reindexar los ojos
    for d in datos_ojos.values():
        d["bucle"] = _reindexar(me, d["bucle_co"]); d["borde_int"] = _reindexar(me, d["borde_co"])
    print("BOCA lista: dientes", len(info["dientes_sup"]) // 8, "piezas, centro", tuple(round(x, 4) for x in O), flush=True)
    return info


# ================================================================ LAS 52 SHAPE KEYS DE ARKIT (+ todo en la misma malla)
def _dist_a(P, Q):
    """Distancia de cada punto de P al punto más cercano de Q (por bloques para no gastar memoria)."""
    out = np.empty(len(P))
    for i in range(0, len(P), 4000):
        out[i:i + 4000] = np.min(np.linalg.norm(P[i:i + 4000, None, :] - Q[None, :, :], axis=2), axis=1)
    return out


def crear_claves(arm, me, info_ojos, info_boca, adelante):
    m = me.data; N = len(m.vertices)
    co = np.empty(N * 3, np.float64); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    nor = np.empty(N * 3, np.float64); m.vertices.foreach_get('normal', nor); nor = nor.reshape(-1, 3)
    up = np.array([0.0, 0.0, 1.0])
    O = np.array(info_boca["O"]); F = np.array(info_boca["F"]); X = np.array(info_boca["X"])
    lat = X.copy()
    B = BOCA; sup = _parabola((B["esq_d"], B["sup_c"], B["esq_i"])); inf = _parabola((B["esq_d"], B["inf_c"], B["esq_i"]))
    mid = lambda x: (sup(x) + inf(x)) / 2
    d = co - O; dx = d @ X; dz = d @ up; dep = -(d @ F)
    x, z = co[:, 0], co[:, 2]
    # conjuntos
    def mask(lista):
        mk = np.zeros(N, bool); mk[np.asarray(lista, int)] = True; return mk
    t_sup, t_inf = mask(info_boca["dientes_sup"]), mask(info_boca["dientes_inf"])
    g_sup, g_inf = mask(info_boca["encia_sup"]), mask(info_boca["encia_inf"])
    leng, saco = mask(info_boca["lengua"]), mask(info_boca["saco"])
    rim = mask(info_boca["labio_int"]) | mask(info_boca["boca_int"])
    interior = t_sup | t_inf | g_sup | g_inf | leng | saco
    piel = ~interior
    lm = mid(x)
    abajo = z < lm
    # ---- peso de la mandíbula
    wj = (1 - _ss(-0.0022, 0.0004, z - lm)) * (1 - _ss(0.028, 0.052, np.abs(dx))) * (1 - _ss(0.022, 0.050, dep)) * _ss(0.783, 0.801, z)
    wj = np.where(piel, wj, 0.0)
    wj = np.where(rim, np.where(abajo, 1.0, 0.0) * (1 - _ss(0.028, 0.04, np.abs(dx))), wj)
    wj = np.where(t_inf | g_inf | leng, 1.0, wj)
    wj = np.where(saco, 1 - _ss(-0.006, 0.003, dz), wj)
    piv = O - F * 0.068 + up * 0.019
    # ---- zonas de los labios
    cerca_linea = 1 - _ss(0.0006, 0.0075, np.abs(z - lm))
    ancho_boca = 1 - _ss(0.020, 0.034, np.abs(dx))
    frente = 1 - _ss(0.012, 0.026, dep)
    w_lab = np.where(piel, cerca_linea * ancho_boca * frente, 0.0)
    w_lab_sup = w_lab * (~abajo); w_lab_inf = w_lab * abajo
    zona_boca = np.where(piel, (1 - _ss(0.0, 0.016, np.abs(z - lm))) * (1 - _ss(0.022, 0.042, np.abs(dx))) * frente, 0.0)
    # esquinas (extremos del bucle de la boca a lo largo del eje lateral)
    bl = co[info_boca["bucle"]]; tb = (bl - O) @ X
    K = {"Right": bl[np.argmin(tb)], "Left": bl[np.argmax(tb)]}
    def w_punto(P, radio, solo_piel=True):
        w = 1 - _ss(0.0, radio, np.linalg.norm(co - P, axis=1))
        return np.where(piel, w, 0.0) if solo_piel else w
    lado_x = {"Left": _ss(-0.004, 0.010, dx), "Right": _ss(-0.004, 0.010, -dx)}
    sgn = {"Left": 1.0, "Right": -1.0}
    # ---- cejas: lo oscuro por encima de cada ojo
    fc = _color_caras(me)
    vcol = np.zeros((N, 3)); cnt = np.zeros(N)
    for p in m.polygons:
        for vi in p.vertices: vcol[vi] += fc[p.index]; cnt[vi] += 1
    vcol /= np.maximum(cnt, 1)[:, None]
    lum = vcol @ np.array([0.3, 0.55, 0.15])
    cejas = {}
    for lado, lado_arkit in (("L", "Left"), ("R", "Right")):
        Ce = info_ojos[lado]["C"]
        cand = piel & (lum < 0.33) & (z > Ce[2] + 0.013) & (z < Ce[2] + 0.032) & (np.abs(co[:, 0] - Ce[0]) < 0.024) & (co[:, 1] < Ce[1] - 0.004)
        idx = np.where(cand)[0]
        if len(idx) < 5:
            print("CEJA", lado, "sin vértices oscuros", flush=True); continue
        P = co[idx]; t = (P - Ce) @ X * sgn[lado_arkit]                 # + hacia fuera (sien)
        tn = (t - t.min()) / max(1e-6, t.max() - t.min())
        dist = _dist_a(co, P)
        w = np.where(piel, 1 - _ss(0.0008, 0.0065, dist), 0.0)
        # parámetro dentro-fuera para cada vértice (del más cercano de la ceja)
        tv = (co - Ce) @ X * sgn[lado_arkit]; tvn = np.clip((tv - t.min()) / max(1e-6, t.max() - t.min()), 0, 1)
        cejas[lado_arkit] = dict(w=w, t=tvn, interior_dir=-X * sgn[lado_arkit])
        print("CEJA", lado, len(idx), "vértices", flush=True)
    claves = {}
    def rotar(P, C, eje, ang):
        return _rot_puntos(P, C, eje, ang)
    def k_add(nombre, Xn):
        claves[nombre] = Xn
    # ---------------- mandíbula
    k_add("jawOpen", rotar(co, piv, lat, math.radians(14) * wj))
    k_add("jawForward", co + np.outer(wj, F) * 0.0026)
    for s_, nombre in ((1, "jawLeft"), (-1, "jawRight")):
        k_add(nombre, rotar(co, piv, up, math.radians(5) * s_ * wj) + np.outer(wj, X) * 0.0012 * s_)
    # ---------------- boca
    Xc = rotar(co, piv, lat, -math.radians(12) * wj * cerca_linea * ancho_boca * abajo)
    Xc = Xc - np.outer(w_lab_sup, up) * 0.0010
    k_add("mouthClose", Xc)
    Xf = co + np.outer(w_lab, F) * 0.0022 - np.outer(w_lab * dx * 0.28, X) + np.outer(w_lab_sup, up) * 0.0009 - np.outer(w_lab_inf, up) * 0.0012
    k_add("mouthFunnel", Xf)
    Xp = co + np.outer(w_lab, F) * 0.0030 - np.outer(w_lab * dx * 0.48, X) - np.outer(w_lab * (z - lm) * 0.40, up)
    k_add("mouthPucker", Xp)
    for s_, nombre in ((1, "mouthLeft"), (-1, "mouthRight")):
        k_add(nombre, co + np.outer(zona_boca, X) * 0.0040 * s_)
    for lado in ("Left", "Right"):
        Kp = K[lado]; s_ = sgn[lado]
        wc = w_punto(Kp, 0.016) * frente
        wc2 = w_punto(Kp, 0.010) * frente
        mejilla = w_punto(Kp + X * 0.010 * s_ + up * 0.010 - F * 0.004, 0.016)
        k_add(f"mouthSmile{lado}", co + np.outer(wc, up) * 0.0027 + np.outer(wc, X) * 0.0017 * s_ - np.outer(wc, F) * 0.0010 + np.outer(mejilla, up) * 0.0010)
        k_add(f"mouthFrown{lado}", co - np.outer(wc, up) * 0.0024 + np.outer(wc2, X) * 0.0004 * s_)
        k_add(f"mouthDimple{lado}", co - np.outer(wc2, F) * 0.0016 + np.outer(wc2, X) * 0.0008 * s_)
        k_add(f"mouthStretch{lado}", co + np.outer(wc, X) * 0.0032 * s_ - np.outer(wc, up) * 0.0008)
        wl = lado_x[lado]
        k_add(f"mouthPress{lado}", co - np.outer(w_lab * wl * (z - lm) * 0.55, up))
        k_add(f"mouthLowerDown{lado}", co - np.outer(w_lab_inf * wl, up) * 0.0026)
        k_add(f"mouthUpperUp{lado}", co + np.outer(w_lab_sup * wl, up) * 0.0024)
    k_add("mouthRollLower", co - np.outer(w_lab_inf * cerca_linea, F) * 0.0018 + np.outer(w_lab_inf * cerca_linea, up) * 0.0010)
    k_add("mouthRollUpper", co - np.outer(w_lab_sup * cerca_linea, F) * 0.0016 - np.outer(w_lab_sup * cerca_linea, up) * 0.0008)
    barbilla = np.where(piel & abajo, (1 - _ss(0.0, 0.020, lm - z)) * (1 - _ss(0.018, 0.032, np.abs(dx))) * frente, 0.0)
    k_add("mouthShrugLower", co + np.outer(barbilla, up) * 0.0016 + np.outer(barbilla, F) * 0.0006)
    k_add("mouthShrugUpper", co + np.outer(w_lab_sup, up) * 0.0012)
    # ---------------- mejillas y nariz
    ojos = {"Left": np.array(info_ojos["L"]["C"]), "Right": np.array(info_ojos["R"]["C"])}
    pc = np.zeros(N)
    for lado in ("Left", "Right"):
        s_ = sgn[lado]
        cp = K[lado] + X * 0.014 * s_ + up * 0.008 - F * 0.006
        pc = np.maximum(pc, w_punto(cp, 0.022))
        cs_ = ojos[lado] - up * 0.016 + X * 0.004 * s_ + F * 0.004
        ws = w_punto(cs_, 0.016)
        k_add(f"cheekSquint{lado}", co + np.outer(ws, up) * 0.0018 + np.outer(ws, F) * 0.0004)
        ala = O + X * (0.0175 * s_) + up * 0.0165
        wn = w_punto(ala, 0.009)
        k_add(f"noseSneer{lado}", co + np.outer(wn, up) * 0.0016 + np.outer(wn, F) * 0.0003)
    k_add("cheekPuff", co + nor * (pc * 0.0030)[:, None])
    # ---------------- cejas
    ci = np.zeros(N); 
    for lado in ("Left", "Right"):
        if lado not in cejas: continue
        c = cejas[lado]; w, t = c["w"], c["t"]
        k_add(f"browDown{lado}", co - np.outer(w * (1.0 - 0.4 * t), up) * 0.0022 + np.outer(w * (1 - t), c["interior_dir"]) * 0.0009)
        k_add(f"browOuterUp{lado}", co + np.outer(w * _ss(0.3, 1.0, t), up) * 0.0026)
        ci = np.maximum(ci, w * (1 - _ss(0.0, 0.7, t)))
    k_add("browInnerUp", co + np.outer(ci, up) * 0.0028)
    # ---------------- lengua
    k_add("tongueOut", rotar(co, piv, lat, math.radians(14) * np.where(leng, 1.0, 0.0)) + np.outer(np.where(leng, 1.0, 0.0), F) * 0.010 - np.outer(np.where(leng, 1.0, 0.0), up) * 0.001)
    # ---------------- ojos (párpados)
    for lado, sufijo in (("L", "Left"), ("R", "Right")):
        I = info_ojos[lado]; th = I["th"]; fuera = 1 if lado == "L" else -1
        def kp(nombre, ang_sup, ang_inf, giro):
            Xn = co.copy(); idx = I["idx"]; Q = Xn[idx]; C = I["C"]
            if ang_sup: Q = _rot_puntos(Q, C, lat, ang_sup * I["wsup"])
            if ang_inf: Q = _rot_puntos(Q, C, lat, ang_inf * I["winf"])
            if giro: Q = _rot_puntos(Q, C, up, giro * np.maximum(I["wsup"], I["winf"]))
            Xn[idx] = Q; k_add(nombre, Xn)
        kp(f"eyeBlink{sufijo}", 0.80 * th + 0.03, -0.20 * th - 0.01, 0)
        kp(f"eyeWide{sufijo}", -0.20 * th, 0.06 * th, 0)
        kp(f"eyeSquint{sufijo}", 0.12 * th, -0.38 * th, 0)
        kp(f"eyeLookUp{sufijo}", -0.16 * th, -0.07 * th, 0)
        kp(f"eyeLookDown{sufijo}", 0.32 * th, 0.08 * th, 0)
        kp(f"eyeLookOut{sufijo}", 0, 0, 0.06 * fuera)
        kp(f"eyeLookIn{sufijo}", 0, 0, -0.06 * fuera)
    # ---------------- escribir las shape keys en el orden de ARKit
    ORDEN = ["eyeBlinkLeft", "eyeLookDownLeft", "eyeLookInLeft", "eyeLookOutLeft", "eyeLookUpLeft", "eyeSquintLeft", "eyeWideLeft",
             "eyeBlinkRight", "eyeLookDownRight", "eyeLookInRight", "eyeLookOutRight", "eyeLookUpRight", "eyeSquintRight", "eyeWideRight",
             "jawForward", "jawLeft", "jawRight", "jawOpen", "mouthClose", "mouthFunnel", "mouthPucker", "mouthLeft", "mouthRight",
             "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight", "mouthDimpleLeft", "mouthDimpleRight",
             "mouthStretchLeft", "mouthStretchRight", "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper",
             "mouthPressLeft", "mouthPressRight", "mouthLowerDownLeft", "mouthLowerDownRight", "mouthUpperUpLeft", "mouthUpperUpRight",
             "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight", "cheekPuff", "cheekSquintLeft",
             "cheekSquintRight", "noseSneerLeft", "noseSneerRight", "tongueOut"]
    if not m.shape_keys: me.shape_key_add(name="Basis", from_mix=False)
    hechas = []
    for nombre in ORDEN:
        if nombre not in claves: continue
        k = me.shape_key_add(name=nombre, from_mix=False); k.data.foreach_set('co', claves[nombre].ravel().astype(np.float32))
        k.value = 0.0; k.slider_min = 0.0; k.slider_max = 1.0; hechas.append(nombre)
    faltan = [n for n in ORDEN if n not in hechas]
    print("ARKIT", len(hechas), "de 52", ("faltan " + ",".join(faltan)) if faltan else "", flush=True)
    return hechas
