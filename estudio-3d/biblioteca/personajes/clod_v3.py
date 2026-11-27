# CLOD v3 · robot de 32 cm, construido por código (27-11-2026).
# Damián, 27-11-2026 21:39: "quiero que hagas un modelo 3D mejor de Clod y que el Clod [de ahora] se elimine".
# Mismo personaje (naranja, pantalla negra con ojos y boca LED, cascos naranjas, símbolo blanco en el pecho, SIN antena)
# con acabado de producto: carcasas partidas con junta visible, núcleo oscuro, fuelles de goma en cuello y piernas,
# rótulas de grafito con ejes de acero, cascos con almohadillas de piel, aro LED verde azulado y tapa, manos con dedos,
# suela de goma, tornillería en las tapas, plástico con barniz y microtextura, pantalla de cristal y LED de puntos.
# Esqueleto, controles y nombres de la pantalla IGUALES que en Clod v2: clod_anim.py funciona sin cambios
# (ClodAnim("CLOD_v3") o ClodAnim(), que elige v3 si está).
# Uso:  blender -b --factory-startup --python clod_v3.py -- <salida.blend>
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix

K = 0.32                      # altura total en metros (diseño con altura 1 y se escala por K)
R = math.radians
NOMBRE = "CLOD_v3"


def V(x, y, z): return Vector((x * K, y * K, z * K))


# ------------------------------------------------------------------ materiales PBR (procedurales, sin texturas externas)
def _nodos(m):
    m.use_nodes = True; nt = m.node_tree
    return nt, nt.nodes.get("Principled BSDF")


def _micro(nt, b, escala=900.0, rug=(0.0, 0.0), relieve=0.0):
    """Microtextura: ruido que varía la rugosidad y un relieve muy fino (marcas de molde/pintura)."""
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = escala; nz.inputs["Detail"].default_value = 8.0; nz.inputs["Roughness"].default_value = 0.6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    if rug != (0.0, 0.0):
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rug[0]; mr.inputs["To Max"].default_value = rug[1]
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    if relieve:
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = relieve; bp.inputs["Distance"].default_value = 0.0004
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])


def material(nombre, color, rough=0.4, metal=0.0, coat=0.0, coat_rough=0.05, emision=0.0, em_color=None,
             aniso=0.0, micro=None, spec=None):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    nt, b = _nodos(m)
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = coat_rough
    if aniso and "Anisotropic" in b.inputs: b.inputs["Anisotropic"].default_value = aniso
    if spec is not None and "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = spec
    if emision > 0:
        b.inputs["Emission Color"].default_value = (*(em_color or color), 1)
        b.inputs["Emission Strength"].default_value = emision
    if micro: _micro(nt, b, *micro)
    return m


def material_led(nombre, color=(0.80, 0.94, 1.0), fuerza=7.0, paso=0.0011):
    """LED de puntos: emisión con una rejilla de puntos (se ve de cerca) que de lejos se lee como trazo continuo."""
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    def onda(eje):
        mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = 2 * math.pi / paso
        nt.links.new(sep.outputs[eje], mu.inputs[0])
        si = nt.nodes.new("ShaderNodeMath"); si.operation = 'SINE'; nt.links.new(mu.outputs[0], si.inputs[0])
        ab = nt.nodes.new("ShaderNodeMath"); ab.operation = 'ABSOLUTE'; nt.links.new(si.outputs[0], ab.inputs[0])
        return ab
    a, c = onda("X"), onda("Z")
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = 'MULTIPLY'; nt.links.new(a.outputs[0], mx.inputs[0]); nt.links.new(c.outputs[0], mx.inputs[1])
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 0.6; nt.links.new(mx.outputs[0], pw.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = fuerza * 0.10; mr.inputs["To Max"].default_value = fuerza * 1.6
    nt.links.new(pw.outputs[0], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], em.inputs["Strength"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def materiales():
    return {
        # plástico ABS pintado en naranja con barniz: rugosidad y relieve finísimos
        "naranja": material("ClodV3_Naranja", (0.90, 0.15, 0.006), rough=0.30, coat=0.65, coat_rough=0.07, micro=(1400.0, (0.24, 0.36), 0.05)),
        # aluminio anodizado grafito, cepillado
        "grafito": material("ClodV3_Grafito", (0.030, 0.032, 0.036), rough=0.34, metal=0.85, aniso=0.45, micro=(2200.0, (0.28, 0.40), 0.02)),
        "nucleo": material("ClodV3_Nucleo", (0.012, 0.012, 0.014), rough=0.6, metal=0.3),
        "goma": material("ClodV3_Goma", (0.018, 0.018, 0.020), rough=0.78, micro=(1800.0, (0.70, 0.86), 0.10)),
        "acero": material("ClodV3_Acero", (0.78, 0.79, 0.80), rough=0.16, metal=1.0, aniso=0.3, micro=(3000.0, (0.12, 0.22), 0.0)),
        "pantalla": material("ClodV3_Pantalla", (0.0015, 0.0015, 0.002), rough=0.06, coat=1.0, coat_rough=0.02, spec=0.6),
        "led": material_led("ClodV3_LED"),
        "simbolo": material("ClodV3_Simbolo", (0.93, 0.93, 0.91), rough=0.22, coat=0.8, coat_rough=0.05, emision=0.8, em_color=(1, 1, 1)),
        "mano": material("ClodV3_Manos", (0.84, 0.84, 0.82), rough=0.42, coat=0.35, micro=(1600.0, (0.38, 0.50), 0.04)),
        "piel": material("ClodV3_Almohadilla", (0.030, 0.027, 0.026), rough=0.52, micro=(700.0, (0.45, 0.62), 0.25)),
        "acento": material("ClodV3_LuzCasco", (0.0, 0.51, 0.49), rough=0.3, emision=6.0, em_color=(0.0, 0.85, 0.78)),
    }


# ------------------------------------------------------------------ primitivas (unidades de diseño)
def _obj(nombre, bm, mat, col, liso=True):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = liso
    me.materials.append(mat)
    o = bpy.data.objects.new(nombre, me); col.objects.link(o)
    return o


def caja_redonda(nombre, centro, tam, radio, mat, col, seg=6, subdiv=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * tam[0] * K, v.co.y * tam[1] * K, v.co.z * tam[2] * K))
    o = _obj(nombre, bm, mat, col); o.location = V(*centro)
    m = o.modifiers.new("Bisel", "BEVEL"); m.width = radio * K; m.segments = seg; m.limit_method = 'NONE'
    if subdiv: s = o.modifiers.new("Suave", "SUBSURF"); s.levels = 1; s.render_levels = subdiv
    return o


def placa_redonda(nombre, centro, w, h, r, prof, mat, col, seg=10, bisel=0.004, cara=-1):
    """Rectángulo de esquinas redondas en el plano XZ con grosor 'prof' en Y."""
    bm = bmesh.new(); pts = []
    for cx, cz, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(seg + 1):
            a = R(a0 + 90 * i / seg); pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    fr = [bm.verts.new((x * K, -prof / 2 * K, z * K)) for x, z in pts]
    bk = [bm.verts.new((x * K, prof / 2 * K, z * K)) for x, z in pts]
    bm.faces.new(list(reversed(fr))); bm.faces.new(bk)
    n = len(pts)
    for i in range(n): bm.faces.new((fr[i], fr[(i + 1) % n], bk[(i + 1) % n], bk[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _obj(nombre, bm, mat, col, liso=False); o.location = V(*centro)
    if bisel:
        m = o.modifiers.new("Bisel", "BEVEL"); m.width = bisel * K; m.segments = 3; m.limit_method = 'ANGLE'
        o.data.polygons.foreach_set("use_smooth", [True] * len(o.data.polygons))
        try: o.modifiers.new("Normales", "WEIGHTED_NORMAL")
        except Exception: pass
    return o


def esfera(nombre, centro, radios, mat, col, u=64, v=32, super_=2.0):
    """Elipsoide; super_>2 la hace más 'cuadrada' (superelipsoide, aspecto de producto diseñado)."""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    for vt in bm.verts:
        x, y, z = vt.co
        if super_ != 2.0:
            n = (abs(x) ** super_ + abs(y) ** super_ + abs(z) ** super_) ** (1 / super_)
            if n > 1e-9: x, y, z = x / n, y / n, z / n
        vt.co = Vector((x * radios[0] * K, y * radios[1] * K, z * radios[2] * K))
    o = _obj(nombre, bm, mat, col); o.location = V(*centro)
    return o


def capsula(nombre, a, b, r, mat, col, seg=40):
    A, B_ = V(*a), V(*b); d = B_ - A; L = d.length
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=20, radius=r * K)
    for vt in bm.verts:
        if vt.co.z > 0: vt.co.z += L
    o = _obj(nombre, bm, mat, col)
    o.matrix_world = Matrix.Translation(A) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    return o


def cilindro(nombre, centro, r, prof, eje, mat, col, seg=64, bisel=0.0, bseg=4):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r * K, radius2=r * K, depth=prof * K)
    o = _obj(nombre, bm, mat, col); o.location = V(*centro)
    o.rotation_euler = {"X": (0, R(90), 0), "Y": (R(90), 0, 0), "Z": (0, 0, 0)}[eje]
    if bisel:
        m = o.modifiers.new("Bisel", "BEVEL"); m.width = bisel * K; m.segments = bseg; m.limit_method = 'ANGLE'
        o.data.polygons.foreach_set("use_smooth", [True] * len(o.data.polygons))
        try: o.modifiers.new("Normales", "WEIGHTED_NORMAL")
        except Exception: pass
    return o


def toro(nombre, centro, R_, r, eje, mat, col, arco=360, giro=0, n=72, m=18):
    bm = bmesh.new(); rows = []
    for i in range(n + (0 if arco == 360 else 1)):
        a = R(giro) + R(arco) * i / n; row = []
        for j in range(m):
            b = 2 * math.pi * j / m
            row.append(bm.verts.new((((R_ + r * math.cos(b)) * math.cos(a)) * K, ((R_ + r * math.cos(b)) * math.sin(a)) * K, (r * math.sin(b)) * K)))
        rows.append(row)
    pares = list(zip(rows, rows[1:] + ([rows[0]] if arco == 360 else [])))
    for ra, rb in pares:
        for j in range(m): bm.faces.new((ra[j], ra[(j + 1) % m], rb[(j + 1) % m], rb[j]))
    if arco != 360:                                  # tapas redondas en los extremos
        for row in (rows[0], rows[-1]):
            c = bm.verts.new(sum((v.co for v in row), Vector()) / len(row))
            for j in range(m): bm.faces.new((row[j], row[(j + 1) % m], c))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _obj(nombre, bm, mat, col); o.location = V(*centro)
    o.rotation_euler = {"X": (0, R(90), 0), "Y": (R(90), 0, 0), "Z": (0, 0, 0)}[eje]
    return o


def cilindro_eje(nombre, a, b, t, r, ancho, mat, col, seg=64):
    """Aro/manguito de radio r y anchura 'ancho' alineado con el segmento a-b, en la fracción t del recorrido."""
    A, B_ = V(*a), V(*b); d = B_ - A; c = A + d * t
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r * K, radius2=r * K, depth=ancho * K)
    o = _obj(nombre, bm, mat, col)
    o.matrix_world = Matrix.Translation(c) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    m = o.modifiers.new("Bisel", "BEVEL"); m.width = 0.004 * K; m.segments = 4; m.limit_method = 'ANGLE'
    o.data.polygons.foreach_set("use_smooth", [True] * len(o.data.polygons))
    try: o.modifiers.new("Normales", "WEIGHTED_NORMAL")
    except Exception: pass
    return o


def tornillo(nombre, centro, normal, mat, col, r=0.0065):
    """Cabeza de tornillo Allen: cúpula baja con hexágono hundido, orientada según 'normal' (unidades de diseño)."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=r * K, radius2=r * 0.86 * K, depth=r * 0.55 * K)
    for v in bm.verts: v.co.z += r * 0.27 * K
    o = _obj(nombre, bm, mat, col)
    hx = bmesh.new(); bmesh.ops.create_cone(hx, cap_ends=True, segments=6, radius1=r * 0.42 * K, radius2=r * 0.42 * K, depth=r * 0.6 * K)
    for v in hx.verts: v.co.z += r * 0.55 * K
    meh = bpy.data.meshes.new(nombre + "_hex"); hx.to_mesh(meh); hx.free()
    oh = bpy.data.objects.new(nombre + "_hex", meh); bpy.context.scene.collection.objects.link(oh); oh.hide_render = True; oh.hide_viewport = True
    bo = o.modifiers.new("Hexagono", "BOOLEAN"); bo.operation = 'DIFFERENCE'; bo.object = oh; bo.solver = 'EXACT'
    o.matrix_world = Matrix.Translation(V(*centro)) @ Vector(normal).normalized().to_track_quat('Z', 'Y').to_matrix().to_4x4()
    oh.matrix_world = o.matrix_world.copy(); oh.parent = o; oh.matrix_parent_inverse = o.matrix_world.inverted()
    try: bpy.context.scene.collection.objects.unlink(oh); col.objects.link(oh)
    except Exception: pass
    return o


def partir(o, col, y_corte, hueco=0.008, nombre="Corte"):
    """Parte una carcasa en dos con una junta de 'hueco' (unidades de diseño) en el plano y = y_corte (local del diseño)."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * 2.0 * K, v.co.y * hueco * K, v.co.z * 2.0 * K))
    me = bpy.data.meshes.new(o.name + "_" + nombre); bm.to_mesh(me); bm.free()
    c = bpy.data.objects.new(o.name + "_" + nombre, me); col.objects.link(c)
    c.location = Vector((o.location.x, y_corte * K, o.location.z)); c.display_type = 'WIRE'; c.hide_render = True
    bo = o.modifiers.new(nombre, "BOOLEAN"); bo.operation = 'DIFFERENCE'; bo.object = c; bo.solver = 'EXACT'
    return c


# ------------------------------------------------------------------ pantalla LED (idéntica a Clod v2: mismas formas y nombres)
N_LED = 32
def _cols(w): return [w / 2 * -math.cos(math.pi * i / (N_LED - 1)) for i in range(N_LED)]


def _forma(nombre_forma, w, h, lado=1):
    out = []
    for i, x in enumerate(_cols(w)):
        t = 2 * x / w if w else 0
        tt = max(0.0, 1 - abs(t) ** 2.6) ** (1 / 2.6)
        if nombre_forma == "ojo": out.append((x, h / 2 * tt, -h / 2 * tt))
        elif nombre_forma == "ojo_grande": out.append((x * 1.12, h / 2 * 1.18 * tt, -h / 2 * 1.18 * tt))
        elif nombre_forma == "feliz":
            c = h * 0.28 * (1 - t * t) - h * 0.02; g = h * 0.13 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6)
            out.append((x * 1.05, c + g, c - g))
        elif nombre_forma == "cerrado":
            g = h * 0.06 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6); out.append((x * 1.08, g - h * 0.05, -g - h * 0.05))
        elif nombre_forma in ("enfado", "triste"):
            s = (1 if nombre_forma == "enfado" else -1) * lado
            top = min(h / 2 * tt, h * 0.12 - s * 0.55 * h * t); bot = -h / 2 * tt
            out.append((x, max(top, bot + 0.002), bot))
        elif nombre_forma == "sonrisa":
            c = -h * 0.55 * (1 - t * t) + h * 0.2; g = h * 0.16 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6)
            out.append((x, c + g, c - g))
        elif nombre_forma == "abierta": out.append((x * 0.85, h * 0.18 * tt, -h * 0.95 * tt))
        elif nombre_forma == "O": out.append((x * 0.42, h * 0.55 * tt, -h * 0.55 * tt))
        elif nombre_forma == "plana":
            g = h * 0.11 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6); out.append((x * 0.8, g, -g))
        elif nombre_forma == "triste_boca":
            c = h * 0.45 * (1 - t * t) - h * 0.25; g = h * 0.15 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6)
            out.append((x * 0.9, c + g, c - g))
        elif nombre_forma == "grande": out.append((x * 1.15, h * 0.12 * tt + h * 0.1, -h * 1.15 * tt + h * 0.1))
    return out


def led(nombre, centro, w, h, base, claves, mat, col, lado=1):
    bm = bmesh.new(); pts = _forma(base, w, h, lado)
    top = [bm.verts.new((x * K, 0, zt * K)) for (x, zt, zb) in pts]
    bot = [bm.verts.new((x * K, 0, zb * K)) for (x, zt, zb) in pts]
    for i in range(N_LED - 1): bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
    o = _obj(nombre, bm, mat, col, liso=False); o.location = V(*centro)
    o.shape_key_add(name="Basis", from_mix=False)
    for nk in claves:
        kb = o.shape_key_add(name=nk, from_mix=False); kb.value = 0.0
        for i, (x, zt, zb) in enumerate(_forma(nk, w, h, lado)):
            kb.data[i].co = Vector((x * K, 0, zt * K)); kb.data[N_LED + i].co = Vector((x * K, 0, zb * K))
    try: o.visible_shadow = False
    except Exception: pass
    return o


# ------------------------------------------------------------------ construcción
def construir_clod(origen=(0, 0, 0)):
    M = materiales()
    col = bpy.data.collections.get(NOMBRE + "_personaje") or bpy.data.collections.new(NOMBRE + "_personaje")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    piezas = {}
    def P(o, hueso): piezas[o.name] = (o, hueso); return o

    # ---------------- pies: botín naranja, suela de goma, tobillera de grafito con aro de acero y dos tornillos
    for s, L in ((-1, "R"), (1, "L")):
        P(caja_redonda(f"CLOD_Pie_{L}", (s * 0.115, -0.03, 0.054), (0.148, 0.232, 0.074), 0.034, M["naranja"], col, seg=6), f"pie.{L}")
        P(caja_redonda(f"CLOD_Suela_{L}", (s * 0.115, -0.03, 0.017), (0.156, 0.244, 0.022), 0.010, M["goma"], col, seg=4), f"pie.{L}")
        for k in range(4):                               # dibujo de la suela (asoma por el lateral y la punta)
            P(caja_redonda(f"CLOD_Taco_{L}{k}", (s * 0.115, -0.125 + k * 0.06, 0.0045), (0.146, 0.018, 0.009), 0.0035, M["goma"], col, seg=2, subdiv=0), f"pie.{L}")
        P(cilindro(f"CLOD_Tobillo_{L}", (s * 0.115, -0.004, 0.094), 0.046, 0.030, "Z", M["grafito"], col, bisel=0.006), f"pie.{L}")
        P(toro(f"CLOD_AroTobillo_{L}", (s * 0.115, -0.004, 0.081), 0.046, 0.0045, "Z", M["acero"], col), f"pie.{L}")
        for k, yy in enumerate((-0.07, 0.02)):
            P(tornillo(f"CLOD_TornPie_{L}{k}", (s * 0.189, yy - 0.03, 0.058), (s, 0, 0), M["acero"], col, r=0.0075), f"pie.{L}")

    # ---------------- piernas: fuelle de goma, rótula de grafito con eje de acero, muslo naranja con junta
    for s, L in ((-1, "R"), (1, "L")):
        P(capsula(f"CLOD_Espinilla_{L}", (s * 0.115, -0.006, 0.098), (s * 0.115, -0.012, 0.182), 0.034, M["goma"], col), f"pierna.{L}")
        for k in range(5):
            z = 0.106 + k * 0.018
            P(toro(f"CLOD_Fuelle_{L}{k}", (s * 0.115, -0.006 - 0.006 * (z - 0.098) / 0.084, z), 0.036, 0.0085, "Z", M["goma"], col), f"pierna.{L}")
        P(esfera(f"CLOD_Rodilla_{L}", (s * 0.115, -0.012, 0.19), (0.05, 0.05, 0.05), M["grafito"], col), f"pierna.{L}")
        P(cilindro(f"CLOD_EjeRodilla_{L}", (s * 0.115, -0.012, 0.19), 0.022, 0.112, "X", M["acero"], col, bisel=0.004), f"pierna.{L}")
        P(capsula(f"CLOD_Muslo_{L}", (s * 0.115, -0.012, 0.205), (s * 0.11, 0.0, 0.295), 0.046, M["naranja"], col), f"muslo.{L}")
        P(esfera(f"CLOD_Cadera_{L}", (s * 0.11, 0.0, 0.30), (0.046, 0.046, 0.046), M["grafito"], col), "cadera")

    # ---------------- cadera y cuerpo: carcasa partida en dos (junta lateral) con núcleo oscuro
    P(esfera("CLOD_Faja", (0, 0, 0.278), (0.152, 0.122, 0.048), M["grafito"], col, 64, 20, super_=2.4), "cadera")
    P(toro("CLOD_AroFaja", (0, 0, 0.300), 0.128, 0.0055, "Z", M["acero"], col), "cadera")
    cuerpo = P(esfera("CLOD_Cuerpo", (0, 0, 0.42), (0.205, 0.165, 0.175), M["naranja"], col, 96, 48, super_=2.35), "cuerpo")
    P(partir(cuerpo, col, -0.075, 0.009, "Junta"), "cuerpo")      # junta de la tapa frontal (se ve en los 3/4)
    P(esfera("CLOD_NucleoCuerpo", (0, 0, 0.42), (0.192, 0.152, 0.162), M["nucleo"], col, 64, 32, super_=2.35), "cuerpo")
    # símbolo del pecho: 6 barras redondeadas que se cruzan, pegadas a la carcasa
    for i in range(6):
        b = caja_redonda(f"CLOD_Simbolo{i}", (0, -0.17, 0.445), (0.017, 0.01, 0.13), 0.0065, M["simbolo"], col, seg=3, subdiv=0)
        b.rotation_euler = (0, R(i * 30), 0)
        sw = b.modifiers.new("Pegar", "SHRINKWRAP"); sw.target = cuerpo
        sw.wrap_method = 'PROJECT'; sw.use_negative_direction = True; sw.use_positive_direction = True
        sw.use_project_y = True; sw.offset = 0.0028 * K / 0.32
        P(b, "cuerpo")
    # espalda: tres rejillas de ventilación y tapa con cuatro tornillos
    for k, z in enumerate((0.47, 0.44, 0.41)):
        b = caja_redonda(f"CLOD_Rejilla{k}", (0, 0.17, z), (0.12, 0.01, 0.012), 0.005, M["nucleo"], col, seg=3, subdiv=0)
        sw = b.modifiers.new("Pegar", "SHRINKWRAP"); sw.target = cuerpo; sw.wrap_method = 'PROJECT'
        sw.use_negative_direction = True; sw.use_positive_direction = True; sw.use_project_y = True; sw.offset = 0.0012 * K / 0.32
        P(b, "cuerpo")
    for k, (x, z) in enumerate(((-0.075, 0.50), (0.075, 0.50), (-0.075, 0.37), (0.075, 0.37))):
        y = 0.165 * (1 - (abs(x) / 0.205) ** 2.35 - (abs(z - 0.42) / 0.175) ** 2.35) ** (1 / 2.35) + 0.001
        P(tornillo(f"CLOD_TornEspalda{k}", (x, y, z), (x / 0.205 * 0.4, 1, (z - 0.42) / 0.175 * 0.5), M["acero"], col), "cuerpo")

    # ---------------- cuello con fuelle
    P(cilindro("CLOD_Cuello", (0, 0, 0.60), 0.040, 0.095, "Z", M["grafito"], col), "cuello")
    for k, z in enumerate((0.572, 0.594, 0.616, 0.638)):
        P(toro(f"CLOD_FuelleCuello{k}", (0, 0, z), 0.045, 0.0085, "Z", M["goma"], col), "cuello")

    # ---------------- cabeza: carcasa partida (frontal + trasera) con núcleo, marco y pantalla de cristal
    cab = P(caja_redonda("CLOD_Cabeza", (0, 0, 0.80), (0.47, 0.34, 0.35), 0.078, M["naranja"], col, seg=8), "cabeza")
    P(partir(cab, col, 0.118, 0.009, "Junta"), "cabeza")         # junta de la tapa trasera, detrás de los cascos
    P(caja_redonda("CLOD_NucleoCabeza", (0, 0, 0.80), (0.452, 0.322, 0.332), 0.07, M["nucleo"], col, seg=4), "cabeza")
    P(placa_redonda("CLOD_Marco", (0, -0.168, 0.80), 0.375, 0.27, 0.06, 0.02, M["grafito"], col), "cabeza")
    P(placa_redonda("CLOD_Pantalla", (0, -0.176, 0.80), 0.345, 0.24, 0.048, 0.012, M["pantalla"], col, bisel=0.003), "cabeza")
    for k, (x, z) in enumerate(((-0.164, 0.912), (0.164, 0.912), (-0.164, 0.688), (0.164, 0.688))):
        P(tornillo(f"CLOD_TornMarco{k}", (x, -0.1785, z), (0, -1, 0), M["acero"], col, r=0.0055), "cabeza")
    yled = -0.1835
    P(led("CLOD_Ojo_R", (-0.085, yled, 0.825), 0.068, 0.088, "ojo", ["ojo_grande", "feliz", "cerrado", "enfado", "triste"], M["led"], col, lado=1), "cabeza")
    P(led("CLOD_Ojo_L", (0.085, yled, 0.825), 0.068, 0.088, "ojo", ["ojo_grande", "feliz", "cerrado", "enfado", "triste"], M["led"], col, lado=-1), "cabeza")
    P(led("CLOD_Boca", (0, yled, 0.735), 0.10, 0.05, "sonrisa", ["abierta", "O", "plana", "triste_boca", "grande"], M["led"], col), "cabeza")
    # nuca: tapa de grafito con rejilla y cuatro tornillos
    tapa = placa_redonda("CLOD_TapaNuca", (0, 0.172, 0.80), 0.20, 0.14, 0.03, 0.012, M["grafito"], col)
    P(tapa, "cabeza")
    for k, z in enumerate((0.835, 0.812, 0.789, 0.766)):
        P(placa_redonda(f"CLOD_RejillaNuca{k}", (0, 0.1785, z), 0.14, 0.009, 0.0045, 0.004, M["nucleo"], col, seg=4, bisel=0.0), "cabeza")
    for k, (x, z) in enumerate(((-0.085, 0.855), (0.085, 0.855), (-0.085, 0.745), (0.085, 0.745))):
        P(tornillo(f"CLOD_TornNuca{k}", (x, 0.178, z), (0, 1, 0), M["acero"], col, r=0.006), "cabeza")

    # ---------------- cascos: copa naranja, almohadilla de piel, tapa de grafito con aro de luz y botón de acero; diadema acolchada
    for s, L in ((-1, "R"), (1, "L")):
        P(cilindro(f"CLOD_Casco_{L}", (s * 0.262, 0, 0.80), 0.105, 0.065, "X", M["naranja"], col, seg=96, bisel=0.016, bseg=6), "cabeza")
        P(toro(f"CLOD_CojinCasco_{L}", (s * 0.232, 0, 0.80), 0.083, 0.024, "X", M["piel"], col, n=96, m=24), "cabeza")
        P(cilindro(f"CLOD_TapaCasco_{L}", (s * 0.298, 0, 0.80), 0.074, 0.014, "X", M["grafito"], col, seg=96, bisel=0.005), "cabeza")
        P(toro(f"CLOD_LuzCasco_{L}", (s * 0.3055, 0, 0.80), 0.060, 0.0042, "X", M["acento"], col, n=96, m=12), "cabeza")
        for k, rr in enumerate((0.044, 0.034)):
            P(toro(f"CLOD_RanuraCasco_{L}{k}", (s * 0.3055, 0, 0.80), rr, 0.0022, "X", M["nucleo"], col, n=72, m=8), "cabeza")
        P(cilindro(f"CLOD_BotonCasco_{L}", (s * 0.308, 0, 0.80), 0.022, 0.008, "X", M["acero"], col, seg=64, bisel=0.003), "cabeza")
        P(caja_redonda(f"CLOD_Deslizador_{L}", (s * 0.272, 0, 0.905), (0.020, 0.034, 0.05), 0.008, M["acero"], col, seg=3), "cabeza")
    P(toro("CLOD_Diadema", (0, 0, 0.80), 0.285, 0.020, "Y", M["grafito"], col, arco=180, giro=0, n=120), "cabeza")
    P(toro("CLOD_AlmohadillaDiadema", (0, 0, 0.80), 0.290, 0.030, "Y", M["piel"], col, arco=64, giro=58, n=64, m=20), "cabeza")

    # ---------------- brazos: hombro y codo de grafito con tapa de acero, brazos naranjas con junta, muñequera, mano con dedos
    for s, L in ((-1, "R"), (1, "L")):
        P(esfera(f"CLOD_Hombro_{L}", (s * 0.205, 0.0, 0.50), (0.05, 0.05, 0.05), M["grafito"], col), f"brazo.{L}")
        P(cilindro(f"CLOD_TapaHombro_{L}", (s * 0.252, 0.0, 0.50), 0.026, 0.010, "X", M["acero"], col, bisel=0.003), f"brazo.{L}")
        P(capsula(f"CLOD_Brazo_{L}", (s * 0.21, 0.0, 0.485), (s * 0.231, 0.011, 0.392), 0.038, M["naranja"], col), f"brazo.{L}")
        P(esfera(f"CLOD_Codo_{L}", (s * 0.233, 0.012, 0.38), (0.038, 0.038, 0.038), M["grafito"], col), f"antebrazo.{L}")
        P(cilindro(f"CLOD_EjeCodo_{L}", (s * 0.233, 0.012, 0.38), 0.016, 0.086, "X", M["acero"], col, bisel=0.003), f"antebrazo.{L}")
        P(capsula(f"CLOD_Antebrazo_{L}", (s * 0.234, 0.011, 0.368), (s * 0.249, -0.013, 0.292), 0.036, M["naranja"], col), f"antebrazo.{L}")
        P(cilindro_eje(f"CLOD_Muneca_{L}", (s * 0.234, 0.011, 0.368), (s * 0.249, -0.013, 0.292), 0.93, 0.0405, 0.020, M["grafito"], col), f"antebrazo.{L}")
        # mano: palma blanca + tres dedos algo curvados + pulgar (hueso propio)
        P(caja_redonda(f"CLOD_Mano_{L}", (s * 0.255, -0.020, 0.243), (0.058, 0.080, 0.066), 0.026, M["mano"], col, seg=5), f"mano.{L}")
        for k, dy in enumerate((-0.023, 0.0, 0.023)):
            y0 = -0.018 + dy
            P(capsula(f"CLOD_Dedo_{L}{k}", (s * 0.256, y0, 0.220), (s * (0.256 - 0.008), y0 - 0.003, 0.200), 0.0150, M["mano"], col, seg=24), f"mano.{L}")
        P(capsula(f"CLOD_Pulgar_{L}", (s * 0.238, -0.054, 0.258), (s * 0.229, -0.074, 0.282), 0.0175, M["mano"], col, seg=24), f"pulgar.{L}")

    # ----------------------------------------------------- esqueleto (igual que v2)
    arm_d = bpy.data.armatures.new(NOMBRE + "_Arm"); arm = bpy.data.objects.new(NOMBRE, arm_d); col.objects.link(arm)
    arm_d.display_type = 'STICK'; arm.show_in_front = True
    bpy.context.view_layer.objects.active = arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_d.edit_bones
    def hueso(n, h, t, padre=None, conectado=False):
        b = eb.new(n); b.head = V(*h); b.tail = V(*t); b.use_deform = False
        if padre: b.parent = eb[padre]; b.use_connect = conectado
        return b
    hueso("raiz", (0, 0, 0), (0, 0.15, 0))
    hueso("cadera", (0, 0, 0.30), (0, 0, 0.40), "raiz")
    hueso("cuerpo", (0, 0, 0.40), (0, 0, 0.56), "cadera", True)
    hueso("cuello", (0, 0, 0.56), (0, 0, 0.64), "cuerpo", True)
    hueso("cabeza", (0, 0, 0.64), (0, 0, 0.97), "cuello", True)
    for s, L in ((-1, "R"), (1, "L")):
        hueso(f"brazo.{L}", (s * 0.205, 0.0, 0.50), (s * 0.233, 0.012, 0.38), "cuerpo")
        hueso(f"antebrazo.{L}", (s * 0.233, 0.012, 0.38), (s * 0.252, -0.016, 0.27), f"brazo.{L}", True)
        hueso(f"mano.{L}", (s * 0.252, -0.016, 0.27), (s * 0.258, -0.025, 0.20), f"antebrazo.{L}", True)
        hueso(f"pulgar.{L}", (s * 0.238, -0.05, 0.258), (s * 0.228, -0.078, 0.29), f"mano.{L}")
        hueso(f"muslo.{L}", (s * 0.11, 0.0, 0.30), (s * 0.115, -0.014, 0.19), "cadera")
        hueso(f"pierna.{L}", (s * 0.115, -0.014, 0.19), (s * 0.115, 0.0, 0.07), f"muslo.{L}", True)
        hueso(f"pie.{L}", (s * 0.115, 0.0, 0.07), (s * 0.115, -0.12, 0.05), f"pierna.{L}", True)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()

    # piezas rígidas pegadas a su hueso (sin pesos: nada se deforma)
    for nombre, (o, hn) in piezas.items():
        mw = o.matrix_world.copy()
        o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = hn
        pb = arm.pose.bones[hn]
        pm = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
        o.matrix_parent_inverse = pm.inverted()
        o.matrix_world = mw
    bpy.context.view_layer.update()

    # ----------------------------------------------------- controles IK (mismos nombres que v2)
    colc = bpy.data.collections.get(NOMBRE + "_controles") or bpy.data.collections.new(NOMBRE + "_controles")
    if colc.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(colc)
    def ctrl(n, pos, forma='SPHERE', t=0.02):
        e = bpy.data.objects.new(n, None); colc.objects.link(e); e.empty_display_type = forma; e.empty_display_size = t * K / 0.32
        e.parent = arm; e.location = pos; return e
    for s, L in ((-1, "R"), (1, "L")):
        cm = ctrl(f"CTRLC_mano_{L}", V(s * 0.252, -0.016, 0.27), 'CUBE')
        cc = ctrl(f"CTRLC_codo_{L}", V(s * 0.30, 0.45, 0.38))
        cp = ctrl(f"CTRLC_pie_{L}", V(s * 0.115, 0.0, 0.07), 'CUBE', 0.03)
        cr = ctrl(f"CTRLC_rodilla_{L}", V(s * 0.115, -0.45, 0.19))
        ik = arm.pose.bones[f"antebrazo.{L}"].constraints.new("IK"); ik.name = "IK"
        ik.target = cm; ik.pole_target = cc; ik.chain_count = 2; ik.use_tail = True; ik.use_stretch = False
        ik2 = arm.pose.bones[f"pierna.{L}"].constraints.new("IK"); ik2.name = "IK"
        ik2.target = cp; ik2.pole_target = cr; ik2.chain_count = 2; ik2.use_tail = True; ik2.use_stretch = False
        cr_ = arm.pose.bones[f"pie.{L}"].constraints.new("COPY_ROTATION"); cr_.target = cp; cr_.mix_mode = 'BEFORE'
        cr_.target_space = 'LOCAL'; cr_.owner_space = 'LOCAL'
    calibrar_polos(arm)
    arm.location = origen
    for pb in arm.pose.bones: pb.rotation_mode = 'XYZ'
    arm["version"] = "v3 (27-11-2026)"
    return arm


def calibrar_polos(arm):
    res = {}
    for hn in ("antebrazo.R", "antebrazo.L", "pierna.R", "pierna.L"):
        pb = arm.pose.bones[hn]; ik = pb.constraints["IK"]; padre = pb.parent
        def err():
            bpy.context.view_layer.update(); e = 0.0
            for b in (padre, pb):
                rest = arm.matrix_world @ b.bone.matrix_local; cur = arm.matrix_world @ b.matrix
                e += (rest.to_3x3().col[0] - cur.to_3x3().col[0]).length + (rest.to_3x3().col[2] - cur.to_3x3().col[2]).length
            return e
        mejor = (1e9, 0)
        for a in range(-180, 181, 5):
            ik.pole_angle = R(a); v = err()
            if v < mejor[0]: mejor = (v, a)
        for a in [mejor[1] + d for d in range(-5, 6)]:
            ik.pole_angle = R(a); v = err()
            if v < mejor[0]: mejor = (v, a)
        ik.pole_angle = R(mejor[1]); res[hn] = (mejor[1], round(mejor[0], 4))
    arm["polos"] = str(res)
    return res


if __name__ == "__main__" and "--" in sys.argv:
    salida = sys.argv[sys.argv.index("--") + 1]
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    construir_clod()
    n = sum(1 for o in bpy.data.objects if o.type == 'MESH')
    bpy.ops.wm.save_as_mainfile(filepath=salida)
    print("CLOD_V3_OK", n, "piezas")
