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
    "R": dict(caja=(-0.034, 0.011, 0.860, 0.897), sup=((-0.0255, 0.8775), (-0.0100, 0.8822), (0.0055, 0.8765)),
              inf=((-0.0255, 0.8775), (-0.0095, 0.8664), (0.0055, 0.8765))),
    "L": dict(caja=(0.026, 0.071, 0.862, 0.900), sup=((0.0640, 0.8835), (0.0490, 0.8862), (0.0365, 0.8790)),
              inf=((0.0640, 0.8835), (0.0480, 0.8703), (0.0365, 0.8790))),
}
IRIS_RADIO = 0.0076          # radio del iris visto de frente (el de la pintura de Tripo es grande, de película)
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
    """Ordena las aristas de borde en un bucle cerrado de vértices."""
    vec = {}
    for e in bordes:
        a, b = e.verts; vec.setdefault(a, []).append(b); vec.setdefault(b, []).append(a)
    ini = next(iter(vec)); bucle = [ini]; prev = None; cur = ini
    while True:
        sig = [v for v in vec[cur] if v is not prev]
        if not sig: break
        prev, cur = cur, sig[0]
        if cur is ini: break
        bucle.append(cur)
        if len(bucle) > len(vec) + 2: break
    return bucle


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
    rmp.color_ramp.elements[0].color = (*(base * 0.45), 1); rmp.color_ramp.elements[1].color = (*(base * 2.2), 1)
    rmp.color_ramp.elements[1].position = 0.8
    e = rmp.color_ramp.elements.new(0.55); e.color = (*(Vector((0.10, 0.12, 0.05)) * 1.4), 1)    # motas verdosas
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
    mat_borde = material_simple("MAITE_parpado_borde", (0.62, 0.32, 0.27), rug=0.35, sss=0.25, coat=0.25)
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
            elif not _es_piel(fc[i]) and c[2] >= top(c[0]) - 0.0005 and c[2] < top(c[0]) + 0.009 \
                    and xs[0] - 0.004 < c[0] < xs[1] + 0.002:
                lin.add(i)                                  # delineado y pestañas pintadas: color oscuro limpio
        for i in lin: bm.faces[i].material_index = i_lin
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
        print("OJO", lado, len(g), "caras", flush=True)
    # borrar las caras de los dos ojos a la vez
    borrar = [bm.faces[i] for d in datos.values() for i in d["caras"]]
    bmesh.ops.delete(bm, geom=borrar, context='FACES')
    bm.verts.ensure_lookup_table()
    for lado, d in datos.items():
        O = OJOS[lado]; top = _parabola(O["sup"])
        # bucle del agujero de este ojo
        cx = np.mean([p[0] for p in d["P"]]); cz = np.mean([p[2] for p in d["P"]])
        bordes = [e for e in bm.edges if e.is_boundary and all(abs(v.co.x - cx) < 0.03 and abs(v.co.z - cz) < 0.02 and v.co.y < -0.02 for v in e.verts)]
        bucle = _bucle(bordes)
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
        R = max(R, 0.009)
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
