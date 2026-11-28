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


def _pliegue(bm, verts_bucle, valor=0.8):
    """Marca con 'crease' las aristas que unen vértices consecutivos de un bucle (borde de párpado o labio)."""
    cr = bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
    sv = set(verts_bucle)
    for v in verts_bucle:
        for e in v.link_edges:
            if e.other_vert(v) in sv: e[cr] = max(e[cr], valor)


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


def _imagenes(me):
    """Imágenes de la textura de Tripo: color (sRGB, la más grande), normal, rugosidad y metal."""
    m = me.data; ims = []
    for mt in m.materials:
        if not mt or not mt.node_tree: continue
        for n in mt.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image and n.image not in ims: ims.append(n.image)
    col = max((i for i in ims if i.colorspace_settings.name == 'sRGB'), key=lambda i: i.size[0] * i.size[1])
    rug = next((i for i in ims if 'rough' in i.name.lower()), None)
    met = next((i for i in ims if 'metal' in i.name.lower()), None)
    nor = next((i for i in ims if i not in (col, rug, met) and i.colorspace_settings.name != 'sRGB'), None)
    return dict(color=col, normal=nor, rugosidad=rug, metal=met)


def _muestrear(me, img):
    """Valor medio de una imagen en cada cara (RGB)."""
    m = me.data; w, h = img.size
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


def _rasterizar(me, img, caras, valores, margen_px=3, ruido=0.0, semilla=3):
    m = me.data; w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    uvl = m.uv_layers.active.data; rng = np.random.default_rng(semilla); pintados = 0
    for fi in caras:
        p = m.polygons[fi]
        uv = np.array([uvl[li].uv[:] for li in p.loop_indices], np.float64) * [w, h]
        c = uv.mean(0); r_ = max(1.0, np.linalg.norm(uv - c, axis=1).mean()); uv = c + (uv - c) * (1 + margen_px / r_)
        x0, y0 = np.floor(uv.min(0)).astype(int); x1, y1 = np.ceil(uv.max(0)).astype(int)
        x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(w - 1, x1), min(h - 1, y1)
        if x1 < x0 or y1 < y0: continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        dentro = np.zeros(gx.shape, bool)
        for k in range(1, len(uv) - 1):
            a, b, cc = uv[0], uv[k], uv[k + 1]
            d1 = (gx - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (gy - b[1])
            d2 = (gx - cc[0]) * (b[1] - cc[1]) - (b[0] - cc[0]) * (gy - cc[1])
            d3 = (gx - a[0]) * (cc[1] - a[1]) - (cc[0] - a[0]) * (gy - a[1])
            neg = (d1 < 0) | (d2 < 0) | (d3 < 0); pos = (d1 > 0) | (d2 > 0) | (d3 > 0)
            dentro |= ~(neg & pos)
        if not dentro.any(): continue
        n_ = int(dentro.sum()); val = np.array(valores[fi], np.float32)
        px[y0:y1 + 1, x0:x1 + 1, :3][dentro] = val + (rng.normal(0, ruido, (n_, 3)).astype(np.float32) if ruido else 0)
        pintados += n_
    img.pixels.foreach_set(px.ravel()); img.update()
    try: img.pack()
    except Exception as e: print("PACK", e)
    return pintados


def repintar_piel(me, caras, color=None, colores=None, cen=None, excluir=(), caras_mapas=()):
    """Quita de la textura lo pintado por Tripo en esas caras: color de piel de alrededor, normal plana,
    rugosidad y metal de la piel de alrededor (si no, la zona brilla como plástico y se ve el relieve viejo)."""
    if not caras: return
    caras = sorted(caras); I = _imagenes(me)
    if cen is None:
        m = me.data; cen = np.empty(len(m.polygons) * 3, np.float32); m.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    fc = _muestrear(me, I["color"])
    ex = set(excluir) | set(caras)
    piel = np.array([i for i in range(len(cen)) if i not in ex and _es_piel(fc[i])])
    S = cen[piel]; vecinos = {}
    for fi in caras:
        d = np.linalg.norm(S - cen[fi], axis=1); j = np.argsort(d)[:10]; vecinos[fi] = (piel[j], 1 / (d[j] + 1e-4))
    def locales(vals):
        return {fi: tuple(float(x) for x in np.average(vals[j], axis=0, weights=wt)) for fi, (j, wt) in vecinos.items()}
    tot = _rasterizar(me, I["color"], caras, colores or locales(fc), ruido=0.005)
    todas = sorted(set(caras) | set(caras_mapas))
    for fi in todas:
        if fi not in vecinos:
            d = np.linalg.norm(S - cen[fi], axis=1); j = np.argsort(d)[:10]; vecinos[fi] = (piel[j], 1 / (d[j] + 1e-4))
    if I["normal"] is not None:
        _rasterizar(me, I["normal"], todas, {fi: (0.5, 0.5, 1.0) for fi in todas}, margen_px=2)
    for clave in ("rugosidad", "metal"):
        if I[clave] is not None:
            vals = _muestrear(me, I[clave])
            lejos = {fi: tuple(float(x) for x in np.median(vals[piel[np.argsort(np.linalg.norm(S - cen[fi], axis=1))[10:40]]], axis=0)) for fi in todas}
            _rasterizar(me, I[clave], todas, lejos, margen_px=2)
    print("REPINTADO", len(caras), "caras,", tot, "píxeles (color, normal, rugosidad, metal)", flush=True)


def colores_locales(cen, fc, caras, k=10, excluir=()):
    """Para cada cara a repintar, la media del color de las k caras de piel más cercanas (así no se nota el parche)."""
    ex = set(excluir) | set(caras)
    piel = np.array([i for i in range(len(cen)) if i not in ex and _es_piel(fc[i])])
    S = cen[piel]; out = {}
    for fi in caras:
        d = np.linalg.norm(S - cen[fi], axis=1); j = np.argsort(d)[:k]
        out[fi] = tuple(float(x) for x in np.average(fc[piel[j]], axis=0, weights=1 / (d[j] + 1e-4)))
    return out


def _sk(sockets, ident):
    return next(x for x in sockets if x.identifier == ident)


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
    bs.inputs["Roughness"].default_value = 0.4
    bs.inputs["Specular IOR Level"].default_value = 0.0          # el brillo lo pone la córnea (si no, pupila gris lechosa)
    # el iris está algo hundido: relieve
    bu = N.new("ShaderNodeBump"); bu.location = (450, -300); bu.inputs["Strength"].default_value = 0.25; bu.inputs["Distance"].default_value = 0.0006
    L.new(fib.outputs["Fac"], bu.inputs["Height"]); L.new(bu.outputs["Normal"], bs.inputs["Normal"])
    return mt


def material_cornea():
    mt = bpy.data.materials.get("MAITE_cornea") or bpy.data.materials.new("MAITE_cornea"); mt.use_nodes = True
    bs = mt.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (1, 1, 1, 1); bs.inputs["Roughness"].default_value = 0.0
    bs.inputs["Transmission Weight"].default_value = 1.0; bs.inputs["IOR"].default_value = 1.376
    bs.inputs["Specular IOR Level"].default_value = 0.5
    return mt


def material_cuenca():
    """Fondo entre el párpado y el globo: sigue siendo 'blanco del ojo' (algo rosado) y se oscurece donde se mete
    (oclusión ambiental), así las comisuras de un ojo almendrado se leen como esclera y no como un pliegue marrón."""
    mt = bpy.data.materials.get("MAITE_cuenca") or bpy.data.materials.new("MAITE_cuenca"); mt.use_nodes = True
    N = mt.node_tree.nodes; L = mt.node_tree.links; bs = N["Principled BSDF"]
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.006; ao.samples = 8; ao.location = (-700, 0)
    pw = N.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.2; L.new(ao.outputs["AO"], pw.inputs[0]); pw.location = (-500, 0)
    mx = N.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.location = (-300, 0)
    L.new(pw.outputs[0], _sk(mx.inputs, "Factor_Float"))
    _sk(mx.inputs, "A_Color").default_value = (0.08, 0.035, 0.035, 1); _sk(mx.inputs, "B_Color").default_value = (0.34, 0.24, 0.23, 1)
    L.new(_sk(mx.outputs, "Result_Color"), bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.5; bs.inputs["Specular IOR Level"].default_value = 0.25   # sin barniz: miraba a la luz y salía gris claro
    return mt


def _oscurecer_por_oclusion(mt, distancia, potencia):
    """Multiplica el color base por la oclusión ambiental (lo de dentro de la boca se oscurece al meterse)."""
    N = mt.node_tree.nodes; L = mt.node_tree.links; bs = N["Principled BSDF"]
    if N.get("OCL_ao"): return
    col = tuple(bs.inputs["Base Color"].default_value)
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.name = "OCL_ao"; ao.inputs["Distance"].default_value = distancia; ao.samples = 8
    pw = N.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = potencia; L.new(ao.outputs["AO"], pw.inputs[0])
    mx = N.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
    _sk(mx.inputs, "Factor_Float").default_value = 1.0; _sk(mx.inputs, "A_Color").default_value = col
    cc = N.new("ShaderNodeCombineColor")
    for k_ in ("Red", "Green", "Blue"): L.new(pw.outputs[0], cc.inputs[k_])
    L.new(cc.outputs["Color"], _sk(mx.inputs, "B_Color")); L.new(_sk(mx.outputs, "Result_Color"), bs.inputs["Base Color"])


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
    mat_borde = material_simple("MAITE_parpado_borde", (0.60, 0.38, 0.34), rug=0.45, sss=0.25, coat=0.05)
    m.materials.append(mat_borde); i_borde = len(m.materials) - 1
    mat_cuenca = material_cuenca()
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
    alrededor = []
    lumf = fc @ np.array([0.3, 0.55, 0.15])
    for lado, O in OJOS.items():
        top = _parabola(O["sup"]); bot = _parabola(O["inf"]); xs = sorted(p[0] for p in (O["sup"][0], O["sup"][2]))
        for i, c in enumerate(cen):
            if xs[0] - 0.008 < c[0] < xs[1] + 0.006 and bot(c[0]) - 0.008 < c[2] < top(c[0]) + 0.0095 and c[1] < -0.02 and lumf[i] > 0.33:
                alrededor.append(i)
    repintar_piel(me, sorted(rep), cen=cen, excluir=hueco, caras_mapas=[i for i in alrededor if i not in set(hueco)])
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
            v.co = C + dv.normalized() * max(R + 0.0004, dist - 0.0006)
        for f in [x for x in ext["geom"] if isinstance(x, bmesh.types.BMFace)]:
            f.material_index = i_borde; f.smooth = True
        sb1 = set(nv1)
        ext2 = bmesh.ops.extrude_edge_only(bm, edges=[e for e in bm.edges if e.is_boundary and e.verts[0] in sb1 and e.verts[1] in sb1])
        nv = [x for x in ext2["geom"] if isinstance(x, bmesh.types.BMVert)]
        for v in nv:
            dv = v.co - C; v.co = C + dv.normalized() * (R + 0.0002)
        for f in [x for x in ext2["geom"] if isinstance(x, bmesh.types.BMFace)]:
            f.material_index = i_cuenca; f.smooth = True
        _pliegue(bm, bucle, 0.6); _pliegue(bm, nv1, 0.8); _pliegue(bm, nv, 1.0)
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
    t = eb.new("Mirada"); t.head = mid + adelante * 1.0;   # a 1 m: los ojos apenas convergen (a 45 cm parecían bizcos)
    t.tail = t.head + Vector((0, 0, 0.02)); t.parent = cab; t.use_deform = False
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
        for nombre, radio, mat_ in ((f"MAITE_globo_{lado}", R, mt), (f"MAITE_cornea_{lado}", R + 0.0001, material_cornea())):
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
        fcor = _ss(0.0, 0.55 * semi, dcor)
        wsup = (1 - _ss(0.0006, 0.0090, dsup)) * _ss(-0.0004, 0.0012, hq) * fcor
        winf = (1 - _ss(0.0004, 0.0050, dinf)) * _ss(-0.0004, 0.0012, -hq) * fcor
        # suavizado por aristas: el giro pasa de 1 a 0 sin escalón (si no, al cerrar sale un pliegue en las esquinas)
        loc = np.full(len(co0), -1); loc[idx] = np.arange(len(idx))
        evp = np.empty(len(m.edges) * 2, np.int64); m.edges.foreach_get('vertices', evp); evp = evp.reshape(-1, 2)
        ea, eb_ = loc[evp[:, 0]], loc[evp[:, 1]]; ok_ = (ea >= 0) & (eb_ >= 0); ea, eb_ = ea[ok_], eb_[ok_]
        fijo_s = np.isin(idx, sup); fijo_i = np.isin(idx, inf)
        deg = np.zeros(len(idx)); np.add.at(deg, ea, 1); np.add.at(deg, eb_, 1)
        for w_, fijo in ((wsup, fijo_s), (winf, fijo_i)):
            for _ in range(6):
                acc = np.zeros(len(idx)); np.add.at(acc, ea, w_[eb_]); np.add.at(acc, eb_, w_[ea])
                nuevo = np.where(deg > 0, 0.5 * w_ + 0.5 * acc / np.maximum(deg, 1), w_)
                w_[:] = np.where(fijo, w_, nuevo)
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
        for j in range(nseg + 1):                         # (sin rabito: en las pruebas salía como un pelo tieso)
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
            grosor = (0.00045 + 0.00080 * tout ** 1.3) * (1 - 0.85 * _ss(0.86, 1.0, tout)) if j <= nseg else 0.0013 * (1 - (j - nseg) / 4.5)
            va = bm.verts.new(base + nsup * 0.00012 - radial * 0.00005); vb = bm.verts.new(base + nsup * 0.00012 + radial * grosor)
            origen += [(va, pref), (vb, pref)]
            if prev:
                f2 = bm.faces.new((prev[0], prev[1], vb, va)); f2.material_index = i_lin; f2.smooth = True
            prev = (va, vb)
        if False:                                             # rabito del lado A: desactivado
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
        for fila, (lista, n, Lmin, Lmax, haciaarriba) in enumerate(((I["sup"], 64, 0.0024, 0.0050, 1), (I["sup"], 40, 0.0018, 0.0034, 1), (I["inf"], 24, 0.0008, 0.0019, -1))):
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
                if exterior < 0.035 or exterior > 0.965: continue          # en las esquinas mismas no (se clavan en la piel)
                if fila == 2 and hacia_fuera < 0.40: continue               # abajo sólo en la mitad de fuera (si no, parecen puntos de costura)
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


def _caja_redonda(bm, capa, parte, centro, X, Y, Z, sx, sy, sz, mat_i, segs=2):
    """Caja de esquinas redondeadas (para dientes): cubo subdividido y 'inflado' hacia una superelipse.
    Sus vértices quedan marcados con 'parte' en la capa entera 'capa'. (Las referencias a BMVert NO sobreviven a
    subdivide_edges ni a crear capas, y create_uvsphere reutiliza huecos: por eso todo se marca en una capa.)"""
    tmp = -7
    r = bmesh.ops.create_cube(bm, size=2.0)
    for v in r["verts"]: v[capa] = tmp
    aristas = list({e for v in r["verts"] for e in v.link_edges})
    bmesh.ops.subdivide_edges(bm, edges=aristas, cuts=segs, use_grid_fill=True)
    vs = [v for v in bm.verts if v[capa] == tmp]
    for v in vs:
        p = v.co.copy()
        k = (abs(p.x) ** 3 + abs(p.y) ** 3 + abs(p.z) ** 3) ** (1 / 3)
        p = p / max(k, 1e-6)
        v.co = centro + X * (p.x * sx) + Y * (p.y * sy) + Z * (p.z * sz)
        v[capa] = parte
    for f in {f for v in vs for f in v.link_faces}:
        f.material_index = mat_i; f.smooth = True


def _elipsoide(bm, capa, parte, centro, X, Y, Z, rx, ry, rz, mat_i, u=24, v=14):
    r = bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    vs = list(r["verts"])
    for q in vs:
        p = q.co.copy(); q.co = centro + X * (p.x * rx) + Y * (p.y * ry) + Z * (p.z * rz); q[capa] = parte
    for f in {f for q in vs for f in q.link_faces}:
        f.material_index = mat_i; f.smooth = True


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
    for nombre, col, rug, sss, coat in (("MAITE_labio_int", (0.62, 0.24, 0.24), 0.3, 0.3, 0.5), ("MAITE_boca_int", (0.075, 0.016, 0.018), 0.6, 0.0, 0.0),
                                         ("MAITE_dientes", (0.86, 0.84, 0.78), 0.28, 0.15, 0.35), ("MAITE_encias", (0.70, 0.27, 0.29), 0.35, 0.3, 0.4),
                                         ("MAITE_lengua", (0.66, 0.26, 0.27), 0.45, 0.35, 0.25)):
        mt_ = material_simple(nombre, col, rug=rug, sss=sss, coat=coat)
        if nombre in ("MAITE_boca_int", "MAITE_lengua", "MAITE_encias"): _oscurecer_por_oclusion(mt_, 0.010, 2.5 if nombre == "MAITE_boca_int" else 1.4)
        m.materials.append(mt_); mats[nombre] = len(m.materials) - 1
    fc = _color_caras(me)
    ssel = set(sel)
    restos = [i for i, c in enumerate(cen) if i not in ssel and x0 - 0.008 < c[0] < x1 + 0.008 and inf(c[0]) - 0.009 < c[2] < sup(c[0]) + 0.007
              and c[1] < -0.04 and not _es_piel(fc[i])]
    if restos: repintar_piel(me, restos, cen=cen, excluir=sel)
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
    tb_ = [(v.co - O).dot(X) for v in bucle]
    O = O + X * ((max(tb_) + min(tb_)) / 2)                 # centrado entre las comisuras
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
    _pliegue(bm, bucle, 0.5); _pliegue(bm, v1, 0.9); _pliegue(bm, v2, 1.0)
    # ---- piezas de dentro (en el marco de la boca: X lateral, F hacia delante, up)
    bm.verts.index_update(); bm.verts.ensure_lookup_table()
    idx_bucle = [v.index for v in bucle]; idx_v1 = [v.index for v in v1]; idx_v2 = [v.index for v in v2]
    from mathutils.bvhtree import BVHTree
    i_piel = next((i for i, mt in enumerate(m.materials) if mt and mt.name.startswith("MAITE_piel")), 0)
    caras_piel = [f for f in bm.faces if f.material_index == i_piel and (f.calc_center_median() - O).length < 0.06]
    vp = {v: k for k, v in enumerate({v for f in caras_piel for v in f.verts})}
    bvh_piel = BVHTree.FromPolygons([v.co.copy() for v in vp], [[vp[v] for v in f.verts] for f in caras_piel])
    abertura = [((v.co - O).dot(X), (v.co - O).dot(up)) for v in bucle]
    PARTES = {"dientes_sup": 1, "dientes_inf": 2, "encia_sup": 3, "encia_inf": 4, "lengua": 5, "saco": 6, "bucle": 101, "labio_int": 102, "boca_int": 103}
    capa = bm.verts.layers.int.get("parte_boca") or bm.verts.layers.int.new("parte_boca")      # (invalida las referencias viejas)
    bm.verts.ensure_lookup_table()
    for v in bm.verts: v[capa] = 0
    for clave_, lista_ in (("bucle", idx_bucle), ("labio_int", idx_v1), ("boca_int", idx_v2)):
        for i_ in lista_: bm.verts[i_][capa] = PARTES[clave_]
    anchos = [0.0043, 0.0037, 0.0035, 0.0032, 0.0031, 0.0030]
    altos_s = [0.0050, 0.0044, 0.0047, 0.0041, 0.0038, 0.0035]
    z_borde_sup = O.z - 0.0007                     # filo de los dientes de arriba
    for fila, (r_arco, prof, esc, signo) in enumerate(((0.0205, 0.0026, 1.0, 1), (0.0184, 0.0040, 0.88, -1))):
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
                _caja_redonda(bm, capa, PARTES["dientes_sup" if signo > 0 else "dientes_inf"],
                              c_, tang, nrm_, up, w_ * 0.505, 0.0012, h_ / 2, mats["MAITE_dientes"])
            s_acum += w_
    # encías: anillos aplastados que siguen el arco de los dientes
    for signo, clave_, r_a, prof in ((1, "encia_sup", 0.0210, 0.0026), (-1, "encia_inf", 0.0189, 0.0040)):
        cprof = prof + r_a - 0.0006
        c_ = O - F * cprof + up * (signo * 0.0056 + (z_borde_sup - O.z) - (0.0004 if signo < 0 else 0))
        _elipsoide(bm, capa, PARTES[clave_], c_, X, F, up, r_a, r_a * 0.92, 0.0026, mats["MAITE_encias"], 40, 12)
    _elipsoide(bm, capa, PARTES["lengua"], O - F * 0.0215 + up * (z_borde_sup - O.z - 0.0088), X, F, up, 0.0090, 0.0112, 0.0026, mats["MAITE_lengua"], 28, 14)
    _elipsoide(bm, capa, PARTES["saco"], O - F * 0.0235 + up * 0.0004, X, F, up, 0.0245, 0.0175, 0.0102, mats["MAITE_boca_int"], 36, 20)
    bm.verts.index_update(); bm.verts.ensure_lookup_table()
    info = {k: [] for k in PARTES}
    inv = {v_: k for k, v_ in PARTES.items()}
    for v in bm.verts:
        k = inv.get(v[capa])
        if k: info[k].append(v.index)
    idx_bucle, idx_v1, idx_v2 = info.pop("bucle"), info.pop("labio_int"), info.pop("boca_int")
    # nada de dentro puede asomar por la piel: si un vértice está delante de la piel (y no detrás de la abertura), se mete
    def en_abertura(px_, pz_):
        dentro = False; n = len(abertura)
        for k in range(n):
            (ax, az), (bx, bz) = abertura[k - 1], abertura[k]
            if (az > pz_) != (bz > pz_) and px_ < (bx - ax) * (pz_ - az) / (bz - az + 1e-12) + ax: dentro = not dentro
        return dentro
    metidos = 0
    for k in ("saco",):
        for i in info[k]:
            v = bm.verts[i]; p = v.co
            if en_abertura((p - O).dot(X) * 0.92, (p - O).dot(up) * 0.92): continue
            loc, nrm_p, _i, dist = bvh_piel.find_nearest(p, 0.012)
            if loc is None: continue
            fuera = (p - loc).dot(nrm_p) > -0.0003                 # delante de la piel (o rozándola)
            if fuera:
                v.co = loc - nrm_p * 0.0012; metidos += 1
    print("BOCA vértices metidos dentro de la cara:", metidos, flush=True)
    info["bucle"] = idx_bucle; info["labio_int"] = idx_v1; info["boca_int"] = idx_v2
    bm.verts.layers.int.remove(capa)
    info.update(O=tuple(O), F=tuple(F), X=tuple(X))
    bm.normal_update(); bm.to_mesh(m); bm.free(); m.update()
    # pesos del esqueleto de las piezas nuevas: todo a la cabeza
    g = me.vertex_groups.get("mixamorig:Head") or me.vertex_groups.new(name="mixamorig:Head")
    nuevas = [i for k in ("dientes_sup", "dientes_inf", "encia_sup", "encia_inf", "lengua", "saco") for i in info[k]]
    g.add(nuevas, 1.0, 'REPLACE')
    # reindexar los ojos
    for d in datos_ojos.values():
        d["bucle"] = _reindexar(me, d["bucle_co"]); d["borde_int"] = _reindexar(me, d["borde_co"])
    lejos = sum(1 for k in ("dientes_sup", "dientes_inf", "encia_sup", "encia_inf", "lengua", "saco") for i in info[k]
                if (m.vertices[i].co - O).length > 0.06)
    print("BOCA lista: dientes", len(info["dientes_sup"]), "vértices arriba, centro", tuple(round(x, 4) for x in O),
          "| piezas fuera de sitio:", lejos, flush=True)
    if lejos: raise RuntimeError(f"BOCA: {lejos} vértices de dientes/encías/lengua/saco a más de 6 cm de la boca")
    return info


def _pliegues(me, C, radio=0.022):
    """Aristas de piel cuyas dos caras están casi del revés (pliegue) cerca de C."""
    bm = bmesh.new(); bm.from_mesh(me.data); bm.normal_update()
    ip = {i for i, mt in enumerate(me.data.materials) if mt and mt.name in ("MAITE_piel", "MAITE_ojos_dientes", "MAITE_pelo")}
    Cv = Vector(tuple(C)); n = 0
    for e in bm.edges:
        if len(e.link_faces) != 2: continue
        f1, f2 = e.link_faces
        if f1.material_index in ip and f2.material_index in ip and ((e.verts[0].co + e.verts[1].co) / 2 - Cv).length < radio:
            if f1.normal.dot(f2.normal) < -0.3: n += 1
    bm.free(); return n


def alisar_parpados(me, datos, adelante, iteraciones=160, grosor=0.0014):
    """El modelo de Tripo trae el párpado de arriba esculpido con un pliegue que se dobla hacia dentro (caras del revés
    a 10-14 mm sobre el ojo: en el render es una 'aleta'). Se relaja la piel alrededor del agujero del ojo como una
    membrana (bucle del agujero y piel de fuera fijos) sin dejar que se meta en el globo."""
    m = me.data; N = len(m.vertices)
    co = np.empty(N * 3, np.float64); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    F = np.array(adelante, np.float64)
    fam = [i for i, mt in enumerate(m.materials) if mt and mt.name in ("MAITE_piel", "MAITE_ojos_dientes", "MAITE_pelo")]
    mi = np.empty(len(m.polygons), np.int32); m.polygons.foreach_get('material_index', mi)
    lt = np.empty(len(m.polygons), np.int32); m.polygons.foreach_get('loop_total', lt)
    lv = np.empty(len(m.loops), np.int64); m.loops.foreach_get('vertex_index', lv)
    lf = np.repeat(np.arange(len(m.polygons)), lt)
    en_fam = np.isin(mi, fam)
    otro = np.zeros(N, bool); otro[lv[~en_fam[lf]]] = True       # vértices que tocan caras que no son piel: fijos
    solo_fam = ~otro
    ev = np.empty(len(m.edges) * 2, np.int64); m.edges.foreach_get('vertices', ev); ev = ev.reshape(-1, 2)
    a = np.r_[ev[:, 0], ev[:, 1]]; b = np.r_[ev[:, 1], ev[:, 0]]
    total = 0
    for lado, d in datos.items():
        C = np.array(d["C"], np.float64); R = float(d["R"])
        # el borde del párpado descansa sobre el globo: bucle a R+1,0 mm, labio interno a R+0,5 mm, fondo a R+0,2 mm
        ib = np.array(d["bucle"]); r_ = co[ib] - C; nr = np.linalg.norm(r_, axis=1)
        nuevo = np.minimum(nr, R + 0.0010)
        co[ib] = C + r_ / nr[:, None] * nuevo[:, None]
        bi = np.array(d["borde_int"]); r_ = co[bi] - C; nr = np.linalg.norm(r_, axis=1)
        nuevo = np.where(nr > R + 0.0003, np.minimum(nr, R + 0.0005), nr)
        co[bi] = C + r_ / nr[:, None] * nuevo[:, None]
        bucle = co[d["bucle"]]
        rel = co - C
        cerca = np.linalg.norm(rel, axis=1) < 0.032
        dl = np.full(N, 1e9); dl[cerca] = _dist_a(co[cerca], bucle)
        zona = solo_fam & cerca & (dl > 1e-5) & (dl < 0.015) & (rel[:, 2] > -0.013) & (rel[:, 2] < 0.0185) & (rel @ F > -0.008)
        zona[d["bucle"]] = False
        lam = 0.6 * (1 - _ss(0.0110, 0.0150, dl)) * (1 - _ss(0.0160, 0.0185, rel[:, 2]))
        sel = zona[a]; aa, bb = a[sel], b[sel]
        deg = np.zeros(N); np.add.at(deg, aa, 1)
        zi = np.where(zona & (deg > 0))[0]
        x = co.copy()
        # Relajación "plana" (tipo Tutte): primero la posición en el plano de la cara (u, v) como media de los
        # vecinos hasta converger -> sin pliegues; luego la profundidad, también suave, y nunca dentro del globo.
        Xd = np.array(adelante, np.float64); Xd = np.cross(Xd, [0, 0, 1.0]); Xd /= np.linalg.norm(Xd)   # lateral
        U = np.array([0, 0, 1.0])
        rel_ = co - C
        uvw = np.c_[rel_ @ Xd, rel_ @ U, rel_ @ F]
        x2 = uvw.copy()
        lam_v = lam[zi][:, None]
        for it in range(iteraciones * 12):
            acc = np.zeros((N, 3)); np.add.at(acc, aa, x2[bb])
            media = acc[zi] / deg[zi][:, None]
            if it < iteraciones * 10:                      # 1) plano: (u, v) del todo; profundidad poco a poco
                x2[zi, :2] = x2[zi, :2] + (media[:, :2] - x2[zi, :2]) * np.minimum(1.0, lam_v * 1.6)
                x2[zi, 2] = x2[zi, 2] + (media[:, 2] - x2[zi, 2]) * lam[zi] * 0.5
            else:                                          # 2) profundidad suave
                x2[zi, 2] = x2[zi, 2] + (media[:, 2] - x2[zi, 2]) * lam[zi]
            r2 = x2[zi, 0] ** 2 + x2[zi, 1] ** 2
            frente = np.sqrt(np.maximum((R + grosor) ** 2 - r2, 0.0))
            sobre = r2 < (R + grosor) ** 2
            x2[zi, 2] = np.where(sobre, np.maximum(x2[zi, 2], frente), x2[zi, 2])
        x = co.copy()
        x[zi] = C + np.outer(x2[zi, 0], Xd) + np.outer(x2[zi, 1], U) + np.outer(x2[zi, 2], F)
        mov = np.linalg.norm(x[zi] - co[zi], axis=1)
        co[zi] = x[zi]; total += len(zi)
        print("PARPADO_ALISADO", lado, len(zi), "vértices, movimiento máx", round(float(mov.max()) if len(mov) else 0, 4),
              "medio", round(float(mov.mean()) if len(mov) else 0, 4), flush=True)
    antes = {lado: _pliegues(me, d["C"]) for lado, d in datos.items()}
    m.vertices.foreach_set('co', co.ravel()); m.update()
    print("PARPADO_PLIEGUES antes", antes, "después", {lado: _pliegues(me, d["C"]) for lado, d in datos.items()}, flush=True)
    return total


# ================================================================ LAS 52 SHAPE KEYS DE ARKIT (+ todo en la misma malla)
def _dist_a(P, Q):
    """Distancia de cada punto de P al punto más cercano de Q."""
    Q = np.asarray(Q, np.float64)
    if len(Q) == 0: return np.full(len(P), 1e9)
    from mathutils.kdtree import KDTree
    kd = KDTree(len(Q))
    for i, q in enumerate(Q): kd.insert(q, i)
    kd.balance()
    return np.array([kd.find(p)[2] for p in np.asarray(P, np.float64)])


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
        cand = piel & (lum < 0.33) & (z > Ce[2] + 0.0165) & (z < Ce[2] + 0.036) & (np.abs(co[:, 0] - Ce[0]) < 0.031) & (co[:, 1] < Ce[1] + 0.006)
        idx = np.where(cand)[0]
        if len(idx) < 5:
            print("CEJA", lado, "sin vértices oscuros", flush=True); continue
        P = co[idx]; t = (P - Ce) @ X * sgn[lado_arkit]                 # + hacia fuera (sien)
        tn = (t - t.min()) / max(1e-6, t.max() - t.min())
        dist = _dist_a(co, P)
        w = np.where(piel, 1 - _ss(0.0015, 0.0110, dist), 0.0) * _ss(Ce[2] + 0.006, Ce[2] + 0.013, z)
        Il = info_ojos[lado]; wl = np.zeros(N); wl[Il["idx"]] = Il["wsup"]; w = w * (1 - _ss(0.2, 0.6, wl))   # el borde del párpado y las pestañas, quietos
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
    # cierre de labios: la boca de Maite está abierta en reposo (sonrisa con dientes); cada labio baja/sube la mitad del hueco
    hueco = np.maximum(sup(x) - inf(x), 0.0) / 2
    w_rim = np.where(mask(info_boca["labio_int"]), 1.0, 0.0) + np.where(mask(info_boca["boca_int"]), 0.35, 0.0)
    w_cierre = np.where(rim, w_rim, np.where(piel, 1 - _ss(0.0008, 0.0070, np.abs(z - lm)), 0.0)) \
        * (1 - _ss(0.018, 0.031, np.abs(dx))) * (1 - _ss(0.014, 0.030, dep))
    cierre = np.outer(w_cierre * hueco * np.where(abajo, 1.0, -1.0) * 1.04, up)
    k_add("mouthClose", co + cierre - np.outer(w_lab, F) * 0.0003)
    Xf = co + np.outer(w_lab, F) * 0.0022 - np.outer(w_lab * dx * 0.28, X) + np.outer(w_lab_sup, up) * 0.0009 - np.outer(w_lab_inf, up) * 0.0012
    k_add("mouthFunnel", Xf + cierre * 0.25)
    # el morro: labios hacia delante y hacia el centro, y casi juntos (la boca de reposo está abierta)
    w_mor = np.maximum(w_lab, np.where(rim, w_rim * (1 - _ss(0.018, 0.031, np.abs(dx))), 0.0))
    Xp = co + np.outer(w_mor, F) * 0.0036 - np.outer(w_mor * dx * 0.26, X) - np.outer(w_lab * (z - lm) * 0.40, up) + cierre * 0.80
    k_add("mouthPucker", Xp)
    for s_, nombre in ((1, "mouthLeft"), (-1, "mouthRight")):
        k_add(nombre, co + np.outer(zona_boca, X) * 0.0040 * s_)
    for lado in ("Left", "Right"):
        Kp = K[lado]; s_ = sgn[lado]
        wc = w_punto(Kp, 0.016) * frente
        wc2 = w_punto(Kp, 0.010) * frente
        mejilla = w_punto(Kp + X * 0.010 * s_ + up * 0.010 - F * 0.004, 0.016)
        k_add(f"mouthSmile{lado}", co + np.outer(wc, up) * 0.0042 + np.outer(wc, X) * 0.0026 * s_ - np.outer(wc, F) * 0.0014 + np.outer(mejilla, up) * 0.0018 + np.outer(mejilla, F) * 0.0006)
        k_add(f"mouthFrown{lado}", co - np.outer(wc, up) * 0.0024 + np.outer(wc2, X) * 0.0004 * s_)
        k_add(f"mouthDimple{lado}", co - np.outer(wc2, F) * 0.0016 + np.outer(wc2, X) * 0.0008 * s_)
        k_add(f"mouthStretch{lado}", co + np.outer(wc, X) * 0.0032 * s_ - np.outer(wc, up) * 0.0008)
        wl = lado_x[lado]
        k_add(f"mouthPress{lado}", co + cierre * wl[:, None] - np.outer(w_lab * wl * (z - lm) * 0.20, up) + np.outer(w_lab * wl, F) * 0.0004)
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
        k_add(f"cheekSquint{lado}", co + np.outer(ws, up) * 0.0030 + np.outer(ws, F) * 0.0007)
        ala = O + X * (0.0175 * s_) + up * 0.0165
        wn = w_punto(ala, 0.009)
        k_add(f"noseSneer{lado}", co + np.outer(wn, up) * 0.0016 + np.outer(wn, F) * 0.0003)
    k_add("cheekPuff", co + nor * (pc * 0.0030)[:, None])
    # ---------------- cejas
    ci = np.zeros(N); 
    for lado in ("Left", "Right"):
        if lado not in cejas: continue
        c = cejas[lado]; w, t = c["w"], c["t"]
        k_add(f"browDown{lado}", co - np.outer(w * (1.0 - 0.4 * t), up) * 0.0046 + np.outer(w * (1 - t), c["interior_dir"]) * 0.0018 - np.outer(w * (1 - t), F) * 0.0006)
        k_add(f"browOuterUp{lado}", co + np.outer(w * _ss(0.3, 1.0, t), up) * 0.0056)
        ci = np.maximum(ci, w * (1 - _ss(0.0, 0.7, t)))
    k_add("browInnerUp", co + np.outer(ci, up) * 0.0060)
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



def ajustar_globos(me, datos, margen=0.00025):
    """La subdivisión del render encoge un poco la piel: se evalúa la malla subdividida y, si el globo o la córnea
    asomarían por la piel, se encogen (con el centro fijo)."""
    sub = me.modifiers.get("Sub_render"); arm_mods = [md for md in me.modifiers if md.type == 'ARMATURE']
    lv = sub.levels if sub else 0
    if sub: sub.levels = max(1, sub.render_levels)
    for md in arm_mods: md.show_viewport = False
    dg = bpy.context.evaluated_depsgraph_get(); ev = me.evaluated_get(dg); mm = ev.to_mesh()
    P = np.empty(len(mm.vertices) * 3, np.float64); mm.vertices.foreach_get('co', P); P = P.reshape(-1, 3)
    ev.to_mesh_clear()
    if sub: sub.levels = lv
    for md in arm_mods: md.show_viewport = True
    m = me.data
    for lado, d in datos.items():
        C = np.array(d["C"]); R = d["R"]
        bucle = np.array([tuple(m.vertices[i].co) for i in d["bucle"]])
        cerca = np.linalg.norm(P - C, axis=1) < R + 0.006
        Q = P[cerca]
        lejos_borde = _dist_a(Q, bucle) > 0.0012
        Q = Q[lejos_borde]
        if not len(Q): continue
        dmin = float(np.min(np.linalg.norm(Q - C, axis=1)))
        Rn = min(R, dmin - margen)
        if Rn < R:
            f = Rn / R
            for nombre in (f"MAITE_globo_{lado}", f"MAITE_cornea_{lado}"):
                o = bpy.data.objects.get(nombre)
                if o: o.scale = (o.scale[0] * f, o.scale[1] * f, o.scale[2] * f)
        print("GLOBO_AJUSTE", lado, "R", round(R, 5), "->", round(Rn, 5), flush=True)


# ======================================================================================
# PIEL LISA alrededor de ojos y boca: en vez de repintar la textura por caras (se ve a bloques, la malla de Tripo
# tiene caras de ~4 mm), se guarda en cada vértice un color de piel "limpio" (relleno armónico desde la piel sana
# de alrededor) y una máscara suave; el material de la piel mezcla textura -> color limpio con esa máscara y apaga
# ahí el mapa de normales y la rugosidad pintada. Sin costuras de UV, sin bloques y se mueve con la cara.
def _srgb_a_lineal(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _color_vertices(me, img):
    """Color medio de la textura en cada vértice (muestreado un poco hacia dentro de cada cara, lejos de las costuras)."""
    m = me.data; w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    uvl = m.uv_layers.active.data
    luv = np.empty(len(uvl) * 2, np.float32); uvl.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    nf = len(m.polygons); lt = np.empty(nf, np.int32); m.polygons.foreach_get('loop_total', lt)
    lf = np.repeat(np.arange(nf), lt)
    fuv = np.zeros((nf, 2)); np.add.at(fuv, lf, luv); fuv /= lt[:, None]
    lv = np.empty(len(m.loops), np.int64); m.loops.foreach_get('vertex_index', lv)
    N = len(m.vertices); acc = np.zeros((N, 3)); cnt = np.zeros(N)
    for t in (0.2, 0.35):
        s_ = luv * (1 - t) + fuv[lf] * t
        c = px[np.clip((s_[:, 1] * h).astype(int), 0, h - 1), np.clip((s_[:, 0] * w).astype(int), 0, w - 1), :3]
        np.add.at(acc, lv, c); np.add.at(cnt, lv, 1)
    return acc / np.maximum(cnt, 1)[:, None]


def _lum_min_caras(me, img):
    """Luminancia mínima de la textura dentro de cada cara (muestreo denso): encuentra manchas pequeñas."""
    m = me.data; w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    lum_img = px[:, :, :3] @ np.array([0.3, 0.55, 0.15], np.float32)
    uvl = m.uv_layers.active.data
    luv = np.empty(len(uvl) * 2, np.float32); uvl.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    nf = len(m.polygons); lt = np.empty(nf, np.int32); m.polygons.foreach_get('loop_total', lt)
    ls = np.empty(nf, np.int32); m.polygons.foreach_get('loop_start', ls)
    lf = np.repeat(np.arange(nf), lt)
    fuv = np.zeros((nf, 2)); np.add.at(fuv, lf, luv); fuv /= lt[:, None]
    sig = np.r_[1:len(luv)]; sig = np.append(sig, 0)
    fin = ls + lt - 1; nxt = np.arange(len(luv)) + 1; nxt[fin] = ls        # siguiente loop de la misma cara
    out = np.full(nf, 9.0); blanco = np.zeros(nf)
    min_img = px[:, :, :3].min(axis=2)
    for t in (0.15, 0.45, 0.75, 0.95):
        for q in (0.0, 0.5):
            a_ = luv * (1 - q) + luv[nxt] * q
            s_ = fuv[lf] * (1 - t) + a_ * t
            yy = np.clip((s_[:, 1] * h).astype(int), 0, h - 1); xx = np.clip((s_[:, 0] * w).astype(int), 0, w - 1)
            np.minimum.at(out, lf, lum_img[yy, xx]); np.maximum.at(blanco, lf, min_img[yy, xx])
    return out, blanco


def piel_lisa(me, datos_ojos, info_boca, r_ojo=(0.0060, 0.0115), r_boca=(0.0010, 0.0034)):
    m = me.data; N = len(m.vertices)
    co = np.empty(N * 3, np.float64); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    # caras que la clasificación por color dejó como "ojos_dientes" o "pelo" junto a los ojos y la boca: son piel
    idx_m = {mt.name: i for i, mt in enumerate(m.materials) if mt}
    ip = idx_m.get("MAITE_piel", 0); restos = {idx_m.get("MAITE_ojos_dientes", -1), idx_m.get("MAITE_pelo", -1)}
    Cs = [np.array(d["C"]) for d in datos_ojos.values()]; Ob = np.array(info_boca["O"])
    cambiadas = 0
    for p in m.polygons:
        if p.material_index in restos:
            c = np.array(p.center)
            if min(np.linalg.norm(c - C) for C in Cs) < 0.022 or (np.linalg.norm(c - Ob) < 0.030 and p.material_index == idx_m.get("MAITE_ojos_dientes")):
                p.material_index = ip; cambiadas += 1
    print("PIEL_LISA caras pasadas a piel:", cambiadas, flush=True)
    I = _imagenes(me)
    vc = _color_vertices(me, I["color"])
    lum = vc @ np.array([0.3, 0.55, 0.15])
    # vértices de caras de piel (los únicos que entran en el relleno)
    i_piel = next((i for i, mt in enumerate(m.materials) if mt and mt.name.startswith("MAITE_piel")), 0)
    mi = np.empty(len(m.polygons), np.int32); m.polygons.foreach_get('material_index', mi)
    es_piel_v = np.zeros(N, bool)
    for p in m.polygons:
        if mi[p.index] == i_piel: es_piel_v[list(p.vertices)] = True
    mask = np.zeros(N)
    cejas = np.zeros(N, bool)
    lmc, blc = _lum_min_caras(me, I["color"]); lum_min_v = np.full(N, 9.0); blanco_v = np.zeros(N)
    lt_ = np.empty(len(m.polygons), np.int32); m.polygons.foreach_get('loop_total', lt_)
    lv_ = np.empty(len(m.loops), np.int64); m.loops.foreach_get('vertex_index', lv_)
    np.minimum.at(lum_min_v, lv_, np.repeat(lmc, lt_)); np.maximum.at(blanco_v, lv_, np.repeat(blc, lt_))
    for lado, d in datos_ojos.items():
        C = np.array(d["C"]); bucle = co[d["bucle"]]
        dist = _dist_a(co, bucle)
        cerca = np.linalg.norm(co - C, axis=1) < 0.045
        w = np.where(cerca, 1 - _ss(r_ojo[0], r_ojo[1], dist), 0.0)
        # las cejas no se tocan
        ce = es_piel_v & cerca & (lum < 0.30) & (co[:, 2] > C[2] + 0.0165)
        cejas |= ce
        if ce.any():
            w *= _ss(0.0012, 0.0042, _dist_a(co, co[ce]))
        # manchas oscuras sueltas (pestañas pintadas de Tripo) entre el ojo y la ceja
        dlb = _dist_a(co, bucle)
        manchas = es_piel_v & cerca & ~ce & (lum_min_v < 0.45) & (dlb < 0.017) & (co[:, 2] > C[2] - 0.014)
        if ce.any(): manchas &= _dist_a(co, co[ce]) > 0.0015
        if manchas.any():
            w = np.maximum(w, 1 - _ss(0.0012, 0.0034, _dist_a(co, co[manchas])))
        mask = np.maximum(mask, w)
    bl = co[info_boca["bucle"]]
    dbo = _dist_a(co, bl)
    mask = np.maximum(mask, 1 - _ss(r_boca[0], r_boca[1], dbo))
    blancas = es_piel_v & (dbo < 0.010) & (blanco_v > 0.62)          # restos de dientes pintados junto a los labios
    if blancas.any():
        mask = np.maximum(mask, 1 - _ss(0.0012, 0.0032, _dist_a(co, co[blancas])))
    print("PIEL_LISA manchas blancas junto a la boca:", int(blancas.sum()), flush=True)
    mask = np.where(es_piel_v, mask, 0.0)
    # relleno armónico: incógnitas = mask > 0.02; fijos = vecinos sanos (piel clara, no ceja)
    U = mask > 0.02
    sano = es_piel_v & ~U & ~cejas & (lum > 0.45) & (vc[:, 0] > vc[:, 2] + 0.15)
    ev = np.empty(len(m.edges) * 2, np.int64); m.edges.foreach_get('vertices', ev); ev = ev.reshape(-1, 2)
    a = np.r_[ev[:, 0], ev[:, 1]]; b = np.r_[ev[:, 1], ev[:, 0]]
    util = U[a] & (U[b] | sano[b])
    a, b = a[util], b[util]
    x = vc.copy()
    ref = np.median(vc[sano & (_dist_a(co, co[U]) < 0.008)], axis=0) if U.any() else np.median(vc[sano], axis=0)
    x[U] = ref
    deg = np.zeros(N); np.add.at(deg, a, 1)
    libres = U & (deg > 0)
    for _ in range(600):
        acc = np.zeros((N, 3)); np.add.at(acc, a, x[b])
        x[libres] = acc[libres] / deg[libres][:, None]
    x[U & ~libres] = ref
    lin = _srgb_a_lineal(np.where(U[:, None], x, vc))
    # atributos
    for nombre in ("piel_lisa", "mascara_piel"):
        if nombre in m.attributes: m.attributes.remove(m.attributes[nombre])
    at = m.attributes.new("piel_lisa", 'FLOAT_COLOR', 'POINT')
    at.data.foreach_set('color', np.c_[lin, np.ones(N)].astype(np.float32).ravel())
    am = m.attributes.new("mascara_piel", 'FLOAT', 'POINT')
    am.data.foreach_set('value', mask.astype(np.float32))
    if "sin_relieve" in m.attributes: m.attributes.remove(m.attributes["sin_relieve"])
    # sólo donde la textura es piel (o junto a las cejas): hay caras de "piel" en el nacimiento del pelo pintadas de pelo,
    # que necesitan su relieve para no verse como un parche liso
    pareceme_piel = (vc[:, 0] - vc[:, 2] > 0.25) & (lum > 0.42)
    junto_ceja = (_dist_a(co, co[cejas]) < 0.005) if cejas.any() else np.zeros(N, bool)
    cara = np.where(es_piel_v & (pareceme_piel | junto_ceja), _ss(0.786, 0.800, co[:, 2]), 0.0)
    for _ in range(2):                                              # suavizado por aristas (sin escalones)
        acc = np.zeros(N); cnt_ = np.zeros(N); np.add.at(acc, ev[:, 0], cara[ev[:, 1]]); np.add.at(acc, ev[:, 1], cara[ev[:, 0]])
        np.add.at(cnt_, ev[:, 0], 1); np.add.at(cnt_, ev[:, 1], 1)
        cara = np.where(es_piel_v, np.maximum(cara * 0.5, 0.5 * cara + 0.5 * acc / np.maximum(cnt_, 1)), 0.0)
    ar = m.attributes.new("sin_relieve", 'FLOAT', 'POINT'); ar.data.foreach_set('value', np.maximum(mask, cara).astype(np.float32))
    # rugosidad de piel sana (ya pasada por el Map Range del material)
    mt = m.materials[i_piel]; Nn = mt.node_tree.nodes; Lk = mt.node_tree.links
    rug_lisa = 0.5
    mr = next((n for n in Nn if n.type == 'MAP_RANGE'), None)
    if I["rugosidad"] is not None and mr is not None:
        rv = _color_vertices(me, I["rugosidad"])[:, 0]
        fmin, fmax, tmin, tmax = (mr.inputs[k].default_value for k in ("From Min", "From Max", "To Min", "To Max"))
        rmap = tmin + np.clip((rv - fmin) / max(1e-6, fmax - fmin), 0, 1) * (tmax - tmin)
        rug_lisa = float(np.median(rmap[sano & (_dist_a(co, co[U]) < 0.010)]))
    _material_piel_lisa(mt, rug_lisa)
    print("PIEL_LISA", int(U.sum()), "vértices rellenos,", int(libres.sum()), "libres, rugosidad", round(rug_lisa, 3), flush=True)



def _material_piel_lisa(mt, rug_lisa):
    T = mt.node_tree; Nn = T.nodes; Lk = T.links
    for n in [n for n in Nn if n.name.startswith("LISA_")]: Nn.remove(n)
    ac = Nn.new("ShaderNodeAttribute"); ac.name = "LISA_color"; ac.attribute_type = 'GEOMETRY'; ac.attribute_name = "piel_lisa"; ac.location = (-900, 520)
    am = Nn.new("ShaderNodeAttribute"); am.name = "LISA_mascara"; am.attribute_type = 'GEOMETRY'; am.attribute_name = "mascara_piel"; am.location = (-900, 700)
    # color: textura -> mezcla -> (HSV)
    hs = next((n for n in Nn if n.type == 'HUE_SAT'), None)
    tex = next((n for n in Nn if n.type == 'TEX_IMAGE' and n.image and n.image.colorspace_settings.name == 'sRGB'), None)
    mx = Nn.new("ShaderNodeMix"); mx.name = "LISA_mezcla"; mx.data_type = 'RGBA'; mx.location = (-650, 450)
    Lk.new(am.outputs["Fac"], _sk(mx.inputs, "Factor_Float")); Lk.new(tex.outputs["Color"], _sk(mx.inputs, "A_Color")); Lk.new(ac.outputs["Color"], _sk(mx.inputs, "B_Color"))
    destino = hs.inputs["Color"] if hs else next(n for n in Nn if n.type == 'BSDF_PRINCIPLED').inputs["Base Color"]
    for l in list(destino.links): Lk.remove(l)
    Lk.new(_sk(mx.outputs, "Result_Color"), destino)
    # rugosidad
    mr = next((n for n in Nn if n.type == 'MAP_RANGE'), None)
    if mr is not None:
        dests = [l.to_socket for l in mr.outputs["Result"].links]
        mf = Nn.new("ShaderNodeMix"); mf.name = "LISA_rug"; mf.data_type = 'FLOAT'; mf.location = (-300, 80)
        Lk.new(am.outputs["Fac"], _sk(mf.inputs, "Factor_Float")); Lk.new(mr.outputs["Result"], _sk(mf.inputs, "A_Float")); _sk(mf.inputs, "B_Float").default_value = rug_lisa
        for d_ in dests:
            for l in list(d_.links): Lk.remove(l)
            Lk.new(_sk(mf.outputs, "Result_Float"), d_)
    # normal: intensidad = 1 - máscara
    nm = next((n for n in Nn if n.type == 'NORMAL_MAP'), None)
    if nm is not None:
        k = nm.inputs["Strength"].default_value
        ar = Nn.new("ShaderNodeAttribute"); ar.name = "LISA_sin_relieve"; ar.attribute_type = 'GEOMETRY'; ar.attribute_name = "sin_relieve"; ar.location = (-900, -420)
        ms = Nn.new("ShaderNodeMath"); ms.name = "LISA_normal"; ms.operation = 'MULTIPLY_ADD'; ms.location = (-700, -420)
        Lk.new(ar.outputs["Fac"], ms.inputs[0]); ms.inputs[1].default_value = -k; ms.inputs[2].default_value = k
        Lk.new(ms.outputs[0], nm.inputs["Strength"])


# ======================================================================================
# MAQUILLAJE: labios algo más rosados y un rubor suave en las mejillas, pintados en una imagen propia (2K, mismas UV)
# calculando para cada píxel su posición 3D (así la forma del labio sale nítida aunque la malla tenga caras de 4 mm).
def _pixeles_3d(me, caras, w, h):
    """Para las caras dadas: índices de píxel (y, x) de la imagen w×h que caen dentro de cada triángulo en UV y su
    posición 3D interpolada."""
    m = me.data; uvl = m.uv_layers.active.data
    ys, xs, P = [], [], []
    for fi in caras:
        p = m.polygons[fi]
        uv = np.array([uvl[li].uv[:] for li in p.loop_indices], np.float64) * [w, h]
        V = np.array([m.vertices[vi].co[:] for vi in p.vertices], np.float64)
        for k in range(1, len(uv) - 1):
            a, b, c = uv[0], uv[k], uv[k + 1]
            x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int) - 1
            x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int) + 1
            x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(w - 1, x1), min(h - 1, y1)
            if x1 < x0 or y1 < y0: continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-12: continue
            l1 = ((b[1] - c[1]) * (gx - c[0]) + (c[0] - b[0]) * (gy - c[1])) / den
            l2 = ((c[1] - a[1]) * (gx - c[0]) + (a[0] - c[0]) * (gy - c[1])) / den
            l3 = 1 - l1 - l2
            tol = -0.02
            dentro = (l1 >= tol) & (l2 >= tol) & (l3 >= tol)
            if not dentro.any(): continue
            ys.append((gy[dentro] - 0.5).astype(int)); xs.append((gx[dentro] - 0.5).astype(int))
            P.append(l1[dentro][:, None] * V[0] + l2[dentro][:, None] * V[k] + l3[dentro][:, None] * V[k + 1])
    if not ys: return np.zeros(0, int), np.zeros(0, int), np.zeros((0, 3))
    return np.concatenate(ys), np.concatenate(xs), np.concatenate(P)


def _sangrado(px, ys, xs, pasos=8):
    """Extiende cada isla de UV unos píxeles hacia fuera (el filtrado de la textura en el borde de una isla mezcla
    con los píxeles vecinos: si están vacíos, la costura se ve como una línea)."""
    h, w = px.shape[:2]
    lleno = np.zeros((h, w), bool); lleno[ys, xs] = True
    for _ in range(pasos):
        suma = np.zeros((h, w, 3), np.float32); cuenta = np.zeros((h, w), np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            ll = np.roll(np.roll(lleno, dy, 0), dx, 1); vv = np.roll(np.roll(px[:, :, :3], dy, 0), dx, 1)
            suma += vv * ll[:, :, None]; cuenta += ll
        nuevo = (~lleno) & (cuenta > 0)
        px[nuevo, :3] = suma[nuevo] / cuenta[nuevo][:, None]
        lleno |= nuevo


def maquillaje(me, datos_ojos, info_boca, tam=2048):
    m = me.data
    O = np.array(info_boca["O"]); F = np.array(info_boca["F"]); X = np.array(info_boca["X"])
    B = BOCA; sup = _parabola((B["esq_d"], B["sup_c"], B["esq_i"])); inf = _parabola((B["esq_d"], B["inf_c"], B["esq_i"]))
    cx = (B["esq_d"][0] + B["esq_i"][0]) / 2; hw = (B["esq_i"][0] - B["esq_d"][0]) / 2
    ip = next((i for i, mt in enumerate(m.materials) if mt and mt.name == "MAITE_piel"), 0)
    Cs = [np.array(d["C"]) for d in datos_ojos.values()]
    caras = [p.index for p in m.polygons if p.material_index == ip and
             (np.linalg.norm(np.array(p.center) - O) < 0.050 or min(np.linalg.norm(np.array(p.center) - C) for C in Cs) < 0.045)]
    ys, xs, P = _pixeles_3d(me, caras, tam, tam)
    x, z = P[:, 0], P[:, 2]
    t = np.clip((x - cx) / hw, -1.0, 1.0); fuera_x = np.abs((x - cx) / hw) > 1.0
    alto_s = 0.0036 * np.sqrt(np.clip(1 - t * t, 0, 1)) ** 0.8
    alto_i = 0.0048 * np.sqrt(np.clip(1 - t * t, 0, 1)) ** 0.6
    zs, zi = sup(x), inf(x)
    borde = 0.0007
    w_sup = _ss(zs - borde, zs + borde * 0.3, z) * (1 - _ss(zs + alto_s - borde, zs + alto_s + borde, z))
    w_inf = (1 - _ss(zi - borde * 0.3, zi + borde, z)) * _ss(zi - alto_i - borde, zi - alto_i + borde, z)
    delante = np.abs((P - O) @ F) < 0.012
    labios = np.where(delante & ~fuera_x, np.maximum(w_sup, w_inf), 0.0) * (1 - _ss(0.86, 1.0, np.abs(t)))
    rubor = np.zeros(len(P))
    for lado, d in datos_ojos.items():
        C = np.array(d["C"]); fuera = X * (1 if lado == "L" else -1)
        Cb = C - np.array([0, 0, 1.0]) * 0.024 + fuera * 0.005 + F * 0.012
        r = np.linalg.norm(P - Cb, axis=1)
        rubor = np.maximum(rubor, 1 - _ss(0.004, 0.016, r))
    # orificios de la nariz: sombra suave en la cara de abajo (el modelo no los tiene; los pintaba el mapa de normales)
    co_ = np.empty(len(m.vertices) * 3, np.float64); m.vertices.foreach_get('co', co_); co_ = co_.reshape(-1, 3)
    rel = co_ - O; fxv, fzv, ffv = rel @ X, rel[:, 2], rel @ F
    zona_n = np.where((np.abs(fxv) < 0.016) & (fzv > 0.004) & (fzv < 0.045) & (ffv > -0.02))[0]
    punta = zona_n[np.argmax(ffv[zona_n])] if len(zona_n) else None
    nariz = np.zeros(len(P))
    if punta is not None:
        for sgn_ in (-1, 1):
            Nc = O + X * (fxv[punta] + sgn_ * 0.0046) + np.array([0, 0, 1.0]) * (fzv[punta] - 0.0070) + F * (ffv[punta] - 0.0058)
            q = P - Nc
            e = np.sqrt(((q @ X) / 0.0030) ** 2 + (q[:, 2] / 0.0013) ** 2 + ((q @ F) / 0.0030) ** 2)
            nariz = np.maximum(nariz, (1 - _ss(0.35, 1.0, e)) * 0.9)
    img = bpy.data.images.get("MAITE_maquillaje")
    if img: bpy.data.images.remove(img)
    img = bpy.data.images.new("MAITE_maquillaje", tam, tam, alpha=False)
    img.colorspace_settings.name = 'Non-Color'
    px = np.zeros((tam, tam, 4), np.float32); px[:, :, 3] = 1
    np.maximum.at(px[:, :, 0], (ys, xs), labios.astype(np.float32))
    np.maximum.at(px[:, :, 1], (ys, xs), rubor.astype(np.float32))
    np.maximum.at(px[:, :, 2], (ys, xs), nariz.astype(np.float32))
    _sangrado(px, ys, xs, pasos=8)                      # sin esto, las costuras de UV salen como grietas claras en los labios
    img.pixels.foreach_set(px.ravel()); img.update(); img.pack()
    _material_maquillaje(m.materials[ip], img)
    print("MAQUILLAJE", len(caras), "caras,", len(P), "píxeles; labios", int((labios > 0.5).sum()), "rubor", int((rubor > 0.5).sum()),
          "nariz", int((nariz > 0.5).sum()), flush=True)


def _material_maquillaje(mt, img, tinte_labios=(0.82, 0.44, 0.47), tinte_rubor=(0.98, 0.74, 0.72), k_labios=0.75, k_rubor=0.30):
    T = mt.node_tree; Nn = T.nodes; Lk = T.links
    for n in [n for n in Nn if n.name.startswith("MAQ_")]: Nn.remove(n)
    uvn = next(n for n in Nn if n.type == 'UVMAP')
    tx = Nn.new("ShaderNodeTexImage"); tx.name = "MAQ_tex"; tx.image = img; tx.interpolation = 'Linear'; tx.location = (-900, 900)
    Lk.new(uvn.outputs["UV"], tx.inputs["Vector"])
    sp = Nn.new("ShaderNodeSeparateColor"); sp.name = "MAQ_sep"; sp.location = (-650, 900); Lk.new(tx.outputs["Color"], sp.inputs["Color"])
    mx = Nn.get("LISA_mezcla"); destino = [l.to_socket for l in _sk(mx.outputs, "Result_Color").links]
    prev = _sk(mx.outputs, "Result_Color")
    for nombre, canal, tinte, k, x_ in (("MAQ_labios", "Red", tinte_labios, k_labios, -450), ("MAQ_rubor", "Green", tinte_rubor, k_rubor, -300),
                                        ("MAQ_nariz", "Blue", (0.55, 0.33, 0.31), 0.60, -150)):
        mu = Nn.new("ShaderNodeMath"); mu.name = nombre + "_k"; mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = k; mu.location = (x_, 1000)
        Lk.new(sp.outputs[canal], mu.inputs[0])
        mm = Nn.new("ShaderNodeMix"); mm.name = nombre; mm.data_type = 'RGBA'; mm.blend_type = 'MULTIPLY'; mm.location = (x_, 800)
        Lk.new(mu.outputs[0], _sk(mm.inputs, "Factor_Float")); Lk.new(prev, _sk(mm.inputs, "A_Color"))
        _sk(mm.inputs, "B_Color").default_value = (*tinte, 1)
        prev = _sk(mm.outputs, "Result_Color")
    for d_ in destino:
        for l in list(d_.links): Lk.remove(l)
        Lk.new(prev, d_)


def bordes_ojos(me, datos_ojos, d_min=0.0006, d_max=0.0034, sombra_sup=0.38, sombra_inf=0.78):
    """Lo que en 4K hace que el ojo 'esté dentro' de la cara y no pegado encima:
    - el borde del párpado de arriba es la línea de las pestañas (oscura) y el de abajo, la línea de agua (rosada y húmeda);
      se distinguen con el atributo 'borde_sup', calculado en reposo, así acompaña al parpadeo;
    - el fondo de la cuenca, del color del blanco del ojo en sombra (antes salía un aro gris lila alrededor);
    - sombra de contacto en el globo: se oscurece cerca del párpado (más debajo del de arriba). La distancia al
      párpado se mide en cada fotograma con nodos de geometría, así la sombra sigue a los parpadeos y gestos."""
    m = me.data
    co = np.empty(len(m.vertices) * 3); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    Cs = np.array([d["C"] for d in datos_ojos.values()])
    cerca = np.argmin(np.linalg.norm(co[:, None, :] - Cs[None], axis=2), axis=1)
    sup = _ss(-0.0012, 0.0022, co[:, 2] - Cs[cerca, 2]).astype(np.float32)
    at = m.attributes.get("borde_sup") or m.attributes.new("borde_sup", 'FLOAT', 'POINT')
    at.data.foreach_set('value', sup)

    def atributo(N, x, y):
        a = N.new("ShaderNodeAttribute"); a.attribute_type = 'GEOMETRY'; a.attribute_name = "borde_sup"; a.location = (x, y); return a

    # borde del párpado
    mt = bpy.data.materials["MAITE_parpado_borde"]; N = mt.node_tree.nodes; L = mt.node_tree.links; bs = N["Principled BSDF"]
    a = atributo(N, -700, 200)
    mx = N.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.location = (-400, 200)
    _sk(mx.inputs, "A_Color").default_value = (0.76, 0.46, 0.42, 1); _sk(mx.inputs, "B_Color").default_value = (0.085, 0.045, 0.040, 1)
    L.new(a.outputs["Fac"], _sk(mx.inputs, "Factor_Float")); L.new(_sk(mx.outputs, "Result_Color"), bs.inputs["Base Color"])
    rg = N.new("ShaderNodeMapRange"); rg.location = (-400, -100); rg.inputs["To Min"].default_value = 0.30; rg.inputs["To Max"].default_value = 0.55
    L.new(a.outputs["Fac"], rg.inputs["Value"]); L.new(rg.outputs["Result"], bs.inputs["Roughness"])
    cw = N.new("ShaderNodeMapRange"); cw.location = (-400, -350); cw.inputs["To Min"].default_value = 0.35; cw.inputs["To Max"].default_value = 0.0
    L.new(a.outputs["Fac"], cw.inputs["Value"]); L.new(cw.outputs["Result"], bs.inputs["Coat Weight"])
    bs.inputs["Coat Roughness"].default_value = 0.08

    # fondo de la cuenca: blanco del ojo en sombra; arriba, más oscuro (debajo de las pestañas)
    mt = bpy.data.materials["MAITE_cuenca"]; N = mt.node_tree.nodes; L = mt.node_tree.links; bs = N["Principled BSDF"]
    mx0 = next(n for n in N if n.type == 'MIX' and n.data_type == 'RGBA')
    _sk(mx0.inputs, "A_Color").default_value = (0.10, 0.045, 0.042, 1); _sk(mx0.inputs, "B_Color").default_value = (0.60, 0.50, 0.47, 1)
    a = atributo(N, -500, 300)
    k = N.new("ShaderNodeMapRange"); k.location = (-300, 300); k.inputs["To Min"].default_value = 1.0; k.inputs["To Max"].default_value = 0.30
    L.new(a.outputs["Fac"], k.inputs["Value"])
    cc = N.new("ShaderNodeCombineColor"); cc.location = (-100, 300)
    for c_ in ("Red", "Green", "Blue"): L.new(k.outputs["Result"], cc.inputs[c_])
    mu = N.new("ShaderNodeMix"); mu.data_type = 'RGBA'; mu.blend_type = 'MULTIPLY'; mu.location = (100, 100)
    _sk(mu.inputs, "Factor_Float").default_value = 1.0
    L.new(_sk(mx0.outputs, "Result_Color"), _sk(mu.inputs, "A_Color")); L.new(cc.outputs["Color"], _sk(mu.inputs, "B_Color"))
    L.new(_sk(mu.outputs, "Result_Color"), bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.38

    # sombra de contacto en cada globo
    for lado in datos_ojos:
        g = bpy.data.objects.get(f"MAITE_globo_{lado}")
        if g is None: continue
        nombre = f"MAITE_sombra_parpado_{lado}"
        ng = bpy.data.node_groups.get(nombre)
        if ng: bpy.data.node_groups.remove(ng)
        ng = bpy.data.node_groups.new(nombre, 'GeometryNodeTree')
        ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
        G = ng.nodes; GL = ng.links
        gi = G.new("NodeGroupInput"); go = G.new("NodeGroupOutput")
        oi = G.new("GeometryNodeObjectInfo"); oi.transform_space = 'RELATIVE'; oi.inputs["Object"].default_value = me
        px = G.new("GeometryNodeProximity"); px.target_element = 'FACES'
        GL.new(oi.outputs["Geometry"], next(s for s in px.inputs if s.type == 'GEOMETRY'))
        ps = G.new("GeometryNodeInputPosition"); GL.new(ps.outputs[0], px.inputs["Source Position"])
        mr = G.new("ShaderNodeMapRange"); mr.interpolation_type = 'SMOOTHSTEP'
        mr.inputs["From Min"].default_value = d_min; mr.inputs["From Max"].default_value = d_max
        GL.new(px.outputs["Distance"], mr.inputs["Value"])
        st = G.new("GeometryNodeStoreNamedAttribute"); st.data_type = 'FLOAT'; st.domain = 'POINT'
        st.inputs["Name"].default_value = "lejos_parpado"
        GL.new(gi.outputs[0], st.inputs["Geometry"]); GL.new(mr.outputs["Result"], st.inputs["Value"]); GL.new(st.outputs["Geometry"], go.inputs[0])
        for md in [md for md in g.modifiers if md.name == "SombraParpado"]: g.modifiers.remove(md)
        md = g.modifiers.new("SombraParpado", 'NODES'); md.node_group = ng
        mt = g.active_material; N = mt.node_tree.nodes; L = mt.node_tree.links; bs = N["Principled BSDF"]
        if N.get("SOMBRA_mult"): continue
        prev = bs.inputs["Base Color"].links[0].from_socket if bs.inputs["Base Color"].is_linked else None
        at_ = N.new("ShaderNodeAttribute"); at_.attribute_type = 'GEOMETRY'; at_.attribute_name = "lejos_parpado"; at_.location = (100, 500)
        geo = N.new("ShaderNodeNewGeometry"); geo.location = (100, 700)
        sz = N.new("ShaderNodeSeparateXYZ"); sz.location = (300, 700); L.new(geo.outputs["Normal"], sz.inputs[0])
        arriba = N.new("ShaderNodeMapRange"); arriba.interpolation_type = 'SMOOTHSTEP'; arriba.location = (450, 700)
        arriba.inputs["From Min"].default_value = -0.35; arriba.inputs["From Max"].default_value = 0.35
        arriba.inputs["To Min"].default_value = sombra_inf; arriba.inputs["To Max"].default_value = sombra_sup
        L.new(sz.outputs["Z"], arriba.inputs["Value"])
        f = N.new("ShaderNodeMix"); f.data_type = 'FLOAT'; f.location = (600, 550)          # lejos -> 1, cerca -> sombra
        L.new(at_.outputs["Fac"], _sk(f.inputs, "Factor_Float")); L.new(arriba.outputs["Result"], _sk(f.inputs, "A_Float"))
        _sk(f.inputs, "B_Float").default_value = 1.0
        cc = N.new("ShaderNodeCombineColor"); cc.location = (750, 550)
        for c_ in ("Red", "Green", "Blue"): L.new(_sk(f.outputs, "Result_Float"), cc.inputs[c_])
        mu = N.new("ShaderNodeMix"); mu.name = "SOMBRA_mult"; mu.data_type = 'RGBA'; mu.blend_type = 'MULTIPLY'; mu.location = (900, 400)
        _sk(mu.inputs, "Factor_Float").default_value = 1.0
        if prev is not None: L.new(prev, _sk(mu.inputs, "A_Color"))
        else: _sk(mu.inputs, "A_Color").default_value = bs.inputs["Base Color"].default_value
        L.new(cc.outputs["Color"], _sk(mu.inputs, "B_Color")); L.new(_sk(mu.outputs, "Result_Color"), bs.inputs["Base Color"])
    print("BORDES_OJOS borde_sup:", int((sup > 0.5).sum()), "vértices arriba", flush=True)
