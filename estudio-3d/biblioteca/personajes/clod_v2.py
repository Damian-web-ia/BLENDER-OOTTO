# CLOD v2 · robot de 32 cm, construido por código (piezas rígidas = sin deformaciones raras).
# Naranja brillante, pantalla negra con ojos y boca LED (formas con shape keys), cascos naranjas,
# símbolo blanco en el pecho, sin antena. Esqueleto con IK en brazos y piernas.
# Uso:  blender -b --factory-startup --python clod_v2.py -- <salida.blend>
#   o dentro de Blender: exec(open(ruta).read()); construir_clod()
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix, Euler

K = 0.32                      # altura total en metros (todo se diseña con altura 1 y se escala por K)
R = math.radians


def V(x, y, z): return Vector((x * K, y * K, z * K))


# ------------------------------------------------------------------ materiales
def material(nombre, color, rough=0.4, metal=0.0, coat=0.0, coat_rough=0.05, emision=0.0, em_color=None):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = coat_rough
    if emision > 0:
        b.inputs["Emission Color"].default_value = (*(em_color or color), 1)
        b.inputs["Emission Strength"].default_value = emision
    return m


def materiales():
    return {
        "naranja": material("Clod_Naranja", (0.92, 0.27, 0.03), rough=0.32, coat=0.8, coat_rough=0.06),
        "oscuro": material("Clod_Gris", (0.035, 0.036, 0.04), rough=0.42, metal=0.35),
        "pantalla": material("Clod_Pantalla", (0.003, 0.003, 0.005), rough=0.06, coat=1.0, coat_rough=0.02),
        "led": material("Clod_LED", (0.80, 0.94, 1.0), rough=0.5, emision=7.0),
        "simbolo": material("Clod_Simbolo", (0.95, 0.95, 0.93), rough=0.3, emision=1.2, em_color=(1, 1, 1)),
        "mano": material("Clod_Manos", (0.86, 0.86, 0.84), rough=0.36, coat=0.4),
        "cojin": material("Clod_Cojin", (0.06, 0.06, 0.065), rough=0.8),
    }


# ------------------------------------------------------------------ primitivas
def _obj(nombre, bm, mat, col, liso=True):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = liso
    me.materials.append(mat)
    o = bpy.data.objects.new(nombre, me); col.objects.link(o)
    return o


def caja_redonda(nombre, centro, tam, radio, mat, col, seg=5, subdiv=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * tam[0] * K, v.co.y * tam[1] * K, v.co.z * tam[2] * K))
    o = _obj(nombre, bm, mat, col); o.location = V(*centro)
    m = o.modifiers.new("Bisel", "BEVEL"); m.width = radio * K; m.segments = seg; m.limit_method = 'NONE'
    if subdiv: s = o.modifiers.new("Suave", "SUBSURF"); s.levels = s.render_levels = subdiv
    return o


def placa_redonda(nombre, centro, w, h, r, prof, mat, col, seg=8, bisel=0.004):
    """Rectángulo de esquinas redondas en el plano XZ, con grosor 'prof' en Y (mirando a -Y)."""
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
    return o


def esfera(nombre, centro, radios, mat, col, u=48, v=24):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    for vt in bm.verts: vt.co = Vector((vt.co.x * radios[0] * K, vt.co.y * radios[1] * K, vt.co.z * radios[2] * K))
    o = _obj(nombre, bm, mat, col); o.location = V(*centro)
    return o


def capsula(nombre, a, b, r, mat, col, seg=32):
    """Cilindro con extremos redondeados entre los puntos a y b (unidades de diseño)."""
    A, B_ = V(*a), V(*b); d = B_ - A; L = d.length
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=16, radius=r * K)
    for vt in bm.verts:                       # estira el ecuador: media esfera arriba, media abajo
        if vt.co.z > 0: vt.co.z += L
    o = _obj(nombre, bm, mat, col)
    o.matrix_world = Matrix.Translation(A) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    return o


def cilindro(nombre, centro, r, prof, eje, mat, col, seg=48, bisel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r * K, radius2=r * K, depth=prof * K)
    o = _obj(nombre, bm, mat, col); o.location = V(*centro)
    o.rotation_euler = {"X": (0, R(90), 0), "Y": (R(90), 0, 0), "Z": (0, 0, 0)}[eje]
    if bisel:
        m = o.modifiers.new("Bisel", "BEVEL"); m.width = bisel * K; m.segments = 4; m.limit_method = 'ANGLE'
    return o


def toro(nombre, centro, R_, r, eje, mat, col, arco=360, giro=0):
    bm = bmesh.new(); n, m = 64, 16
    rows = []
    for i in range(n + (0 if arco == 360 else 1)):
        a = R(giro) + R(arco) * i / n
        row = []
        for j in range(m):
            b = 2 * math.pi * j / m
            x = (R_ + r * math.cos(b)) * math.cos(a); y = (R_ + r * math.cos(b)) * math.sin(a); z = r * math.sin(b)
            row.append(bm.verts.new((x * K, y * K, z * K)))
        rows.append(row)
    pares = list(zip(rows, rows[1:] + ([rows[0]] if arco == 360 else [])))
    for ra, rb in pares:
        for j in range(m): bm.faces.new((ra[j], ra[(j + 1) % m], rb[(j + 1) % m], rb[j]))
    o = _obj(nombre, bm, mat, col); o.location = V(*centro)
    o.rotation_euler = {"X": (0, R(90), 0), "Y": (R(90), 0, 0), "Z": (0, 0, 0)}[eje]
    return o


# ------------------------------------------------------------------ formas LED (tira de N columnas, arriba/abajo)
N_LED = 32
def _cols(w):
    return [w / 2 * -math.cos(math.pi * i / (N_LED - 1)) for i in range(N_LED)]


def _forma(nombre_forma, w, h, lado=1):
    """Devuelve [(x, z_arriba, z_abajo)] en metros de diseño (antes de K)."""
    out = []
    for i, x in enumerate(_cols(w)):
        t = 2 * x / w if w else 0                       # -1..1
        tt = max(0.0, 1 - abs(t) ** 2.6) ** (1 / 2.6)    # superelipse
        if nombre_forma == "ojo":
            out.append((x, h / 2 * tt, -h / 2 * tt))
        elif nombre_forma == "ojo_grande":
            out.append((x * 1.12, h / 2 * 1.18 * tt, -h / 2 * 1.18 * tt))
        elif nombre_forma == "feliz":                    # arco ∩
            c = h * 0.28 * (1 - t * t) - h * 0.02
            g = h * 0.13 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6)
            out.append((x * 1.05, c + g, c - g))
        elif nombre_forma == "cerrado":
            g = h * 0.06 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6)
            out.append((x * 1.08, g - h * 0.05, -g - h * 0.05))
        elif nombre_forma in ("enfado", "triste"):
            s = (1 if nombre_forma == "enfado" else -1) * lado     # lado: +1 si el interior del ojo está hacia +x
            top = min(h / 2 * tt, h * 0.12 - s * 0.55 * h * t)
            bot = -h / 2 * tt
            out.append((x, max(top, bot + 0.002), bot))
        elif nombre_forma == "sonrisa":                  # boca ∪
            c = -h * 0.55 * (1 - t * t) + h * 0.2
            g = h * 0.16 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6)
            out.append((x, c + g, c - g))
        elif nombre_forma == "abierta":                  # boca "D" (habla)
            out.append((x * 0.85, h * 0.18 * tt, -h * 0.95 * tt))
        elif nombre_forma == "O":
            out.append((x * 0.42, h * 0.55 * tt, -h * 0.55 * tt))
        elif nombre_forma == "plana":
            g = h * 0.11 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6)
            out.append((x * 0.8, g, -g))
        elif nombre_forma == "triste_boca":              # boca ∩
            c = h * 0.45 * (1 - t * t) - h * 0.25
            g = h * 0.15 * max(0.0, 1 - abs(t) ** 6) ** (1 / 6)
            out.append((x * 0.9, c + g, c - g))
        elif nombre_forma == "grande":                   # sonrisa enorme abierta
            out.append((x * 1.15, h * 0.12 * tt + h * 0.1, -h * 1.15 * tt + h * 0.1))
    return out


def led(nombre, centro, w, h, base, claves, mat, col, lado=1, prof=0.0):
    """Malla LED plana mirando a -Y en 'centro'. base y claves = nombres de forma."""
    bm = bmesh.new()
    pts = _forma(base, w, h, lado)
    top = [bm.verts.new((x * K, 0, zt * K)) for (x, zt, zb) in pts]
    bot = [bm.verts.new((x * K, 0, zb * K)) for (x, zt, zb) in pts]
    for i in range(N_LED - 1): bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
    o = _obj(nombre, bm, mat, col, liso=False); o.location = V(*centro)
    o.shape_key_add(name="Basis", from_mix=False)
    for nk in claves:
        kb = o.shape_key_add(name=nk, from_mix=False); kb.value = 0.0
        pts = _forma(nk, w, h, lado)
        for i, (x, zt, zb) in enumerate(pts):
            kb.data[i].co = Vector((x * K, 0, zt * K)); kb.data[N_LED + i].co = Vector((x * K, 0, zb * K))
    return o


# ------------------------------------------------------------------ construcción
def construir_clod(origen=(0, 0, 0)):
    M = materiales()
    col = bpy.data.collections.get("CLOD_v2_personaje") or bpy.data.collections.new("CLOD_v2_personaje")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    piezas = {}
    def P(o, hueso): piezas[o.name] = (o, hueso); return o

    # pies y piernas
    for s, L in ((-1, "R"), (1, "L")):
        P(caja_redonda(f"CLOD_Pie_{L}", (s * 0.115, -0.03, 0.045), (0.15, 0.24, 0.09), 0.04, M["naranja"], col), f"pie.{L}")
        P(capsula(f"CLOD_Espinilla_{L}", (s * 0.115, -0.005, 0.085), (s * 0.115, -0.012, 0.185), 0.04, M["oscuro"], col), f"pierna.{L}")
        P(esfera(f"CLOD_Rodilla_{L}", (s * 0.115, -0.012, 0.19), (0.05, 0.05, 0.05), M["oscuro"], col), f"pierna.{L}")
        P(capsula(f"CLOD_Muslo_{L}", (s * 0.115, -0.012, 0.195), (s * 0.11, 0.0, 0.30), 0.045, M["naranja"], col), f"muslo.{L}")
    # cuerpo
    P(esfera("CLOD_Cuerpo", (0, 0, 0.42), (0.205, 0.165, 0.175), M["naranja"], col, 64, 32), "cuerpo")
    P(esfera("CLOD_Faja", (0, 0, 0.275), (0.15, 0.12, 0.045), M["oscuro"], col, 48, 16), "cadera")
    # símbolo del pecho: 6 barras redondeadas que se cruzan (proyectadas sobre el cuerpo)
    for i in range(6):
        b = caja_redonda(f"CLOD_Simbolo{i}", (0, -0.168, 0.445), (0.016, 0.01, 0.13), 0.006, M["simbolo"], col, seg=3, subdiv=0)
        b.rotation_euler = (0, R(i * 30), 0)
        sw = b.modifiers.new("Pegar", "SHRINKWRAP"); sw.target = bpy.data.objects["CLOD_Cuerpo"]
        sw.wrap_method = 'PROJECT'; sw.use_negative_direction = True; sw.use_positive_direction = True
        sw.use_project_y = True; sw.offset = 0.0025 * K / 0.32
        P(b, "cuerpo")
    # cuello y cabeza
    P(capsula("CLOD_Cuello", (0, 0, 0.56), (0, 0, 0.63), 0.05, M["oscuro"], col), "cuello")
    P(caja_redonda("CLOD_Cabeza", (0, 0, 0.80), (0.47, 0.34, 0.35), 0.075, M["naranja"], col, seg=6), "cabeza")
    P(placa_redonda("CLOD_Marco", (0, -0.168, 0.80), 0.375, 0.27, 0.06, 0.02, M["oscuro"], col), "cabeza")
    P(placa_redonda("CLOD_Pantalla", (0, -0.176, 0.80), 0.345, 0.24, 0.048, 0.012, M["pantalla"], col), "cabeza")
    yled = -0.1835
    P(led("CLOD_Ojo_R", (-0.085, yled, 0.825), 0.068, 0.088, "ojo", ["ojo_grande", "feliz", "cerrado", "enfado", "triste"], M["led"], col, lado=1), "cabeza")
    P(led("CLOD_Ojo_L", (0.085, yled, 0.825), 0.068, 0.088, "ojo", ["ojo_grande", "feliz", "cerrado", "enfado", "triste"], M["led"], col, lado=-1), "cabeza")
    P(led("CLOD_Boca", (0, yled, 0.735), 0.10, 0.05, "sonrisa", ["abierta", "O", "plana", "triste_boca", "grande"], M["led"], col), "cabeza")
    # cascos
    for s, L in ((-1, "R"), (1, "L")):
        P(cilindro(f"CLOD_Casco_{L}", (s * 0.262, 0, 0.80), 0.105, 0.065, "X", M["naranja"], col, bisel=0.012), "cabeza")
        P(toro(f"CLOD_CojinCasco_{L}", (s * 0.235, 0, 0.80), 0.085, 0.022, "X", M["cojin"], col), "cabeza")
        P(cilindro(f"CLOD_TapaCasco_{L}", (s * 0.298, 0, 0.80), 0.07, 0.012, "X", M["oscuro"], col, bisel=0.004), "cabeza")
    diadema = toro("CLOD_Diadema", (0, 0, 0.80), 0.285, 0.022, "Y", M["oscuro"], col, arco=180, giro=0)
    P(diadema, "cabeza")
    # brazos
    for s, L in ((-1, "R"), (1, "L")):
        P(esfera(f"CLOD_Hombro_{L}", (s * 0.205, 0.0, 0.50), (0.048, 0.048, 0.048), M["oscuro"], col), f"brazo.{L}")
        P(capsula(f"CLOD_Brazo_{L}", (s * 0.21, 0.0, 0.49), (s * 0.232, 0.012, 0.385), 0.038, M["naranja"], col), f"brazo.{L}")
        P(esfera(f"CLOD_Codo_{L}", (s * 0.233, 0.012, 0.38), (0.036, 0.036, 0.036), M["oscuro"], col), f"antebrazo.{L}")
        P(capsula(f"CLOD_Antebrazo_{L}", (s * 0.234, 0.012, 0.375), (s * 0.25, -0.015, 0.285), 0.036, M["naranja"], col), f"antebrazo.{L}")
        P(esfera(f"CLOD_Mano_{L}", (s * 0.255, -0.022, 0.245), (0.05, 0.045, 0.058), M["mano"], col), f"mano.{L}")
        P(capsula(f"CLOD_Pulgar_{L}", (s * 0.235, -0.055, 0.262), (s * 0.228, -0.075, 0.285), 0.017, M["mano"], col), f"pulgar.{L}")

    # ----------------------------------------------------- esqueleto
    arm_d = bpy.data.armatures.new("CLOD_v2_Arm"); arm = bpy.data.objects.new("CLOD_v2", arm_d); col.objects.link(arm)
    arm_d.display_type = 'STICK'; arm.show_in_front = True
    bpy.context.view_layer.objects.active = arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_d.edit_bones
    def hueso(n, h, t, padre=None, conectado=False, deform=False):
        b = eb.new(n); b.head = V(*h); b.tail = V(*t); b.use_deform = deform
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

    # piezas rígidas pegadas a su hueso (sin pesos)
    for nombre, (o, hn) in piezas.items():
        mw = o.matrix_world.copy()
        o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = hn
        pb = arm.pose.bones[hn]
        pm = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
        o.matrix_parent_inverse = pm.inverted()
        o.matrix_world = mw
    bpy.context.view_layer.update()

    # ----------------------------------------------------- controles IK
    colc = bpy.data.collections.get("CLOD_v2_controles") or bpy.data.collections.new("CLOD_v2_controles")
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
    return arm


def calibrar_polos(arm):
    """Busca el ángulo de polo que deja cada cadena IK igual que en reposo."""
    import itertools
    res = {}
    for hn in ("antebrazo.R", "antebrazo.L", "pierna.R", "pierna.L"):
        pb = arm.pose.bones[hn]; ik = pb.constraints["IK"]; padre = pb.parent
        def err():
            bpy.context.view_layer.update()
            e = 0.0
            for b in (padre, pb):
                rest = arm.matrix_world @ b.bone.matrix_local
                cur = arm.matrix_world @ b.matrix
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
    bpy.ops.wm.save_as_mainfile(filepath=salida)
