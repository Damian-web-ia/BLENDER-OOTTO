# EKORUEDAS · TALLER v2 (26-11-2026): taller grande y ordenado + neumáticos con dibujo real.
# Todo por código (sin descargas). Unidades: metros. Alex en el origen mirando a -Y (la cámara suele estar en -Y).
# Uso:  exec(open(ruta_taller_v2).read());  T = construir_taller();  rueda("RUEDA_Heroe", (x, y, z), rot)
# Neumático 205/55 R16 a escala real: dibujo direccional en V, 4 ranuras principales con TESTIGOS DE DESGASTE (TWI)
# a 1,6 mm, laminillas, flanco con nervios y forma "gastado" (shape key) en la que el dibujo baja hasta el testigo.
import bpy, bmesh, math
import numpy as np
from mathutils import Vector, Matrix

R = math.radians
COL_T = "TALLER_v2"

# ------------------------------------------------------------------ colección y materiales
def _col(nombre=COL_T):
    c = bpy.data.collections.get(nombre)
    if c is None:
        c = bpy.data.collections.new(nombre); bpy.context.scene.collection.children.link(c)
    return c

def mat(nombre, color, rough=0.5, metal=0.0, coat=0.0, emis=0.0, ecol=None, bump=0.0, escala_bump=60.0, spec=None):
    m = bpy.data.materials.get(nombre)
    if m: return m
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if spec is not None and "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = spec
    if coat and "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = coat
    if emis:
        b.inputs["Emission Color"].default_value = (*(ecol or color), 1); b.inputs["Emission Strength"].default_value = emis
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); bp = nt.nodes.new("ShaderNodeBump")
        nz.inputs["Scale"].default_value = escala_bump; nz.inputs["Detail"].default_value = 8
        bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.002
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def materiales():
    return {
        "goma": mat("T2_Goma", (0.018, 0.018, 0.02), rough=0.78, bump=0.25, escala_bump=900, spec=0.35),
        "llanta": mat("T2_Llanta", (0.80, 0.81, 0.83), rough=0.22, metal=1.0),
        "llanta_osc": mat("T2_LlantaOscura", (0.10, 0.10, 0.11), rough=0.35, metal=1.0),
        "tuerca": mat("T2_Tuerca", (0.55, 0.56, 0.58), rough=0.25, metal=1.0),
        "suelo": mat("T2_Suelo", (0.16, 0.17, 0.18), rough=0.32, bump=0.08, escala_bump=6),
        "linea": mat("T2_LineaAmarilla", (0.95, 0.70, 0.02), rough=0.45),
        "pared": mat("T2_Pared", (0.70, 0.71, 0.72), rough=0.85),
        "zocalo": mat("T2_Zocalo", (0.22, 0.24, 0.27), rough=0.6),
        "franja": mat("T2_Franja", (0.95, 0.35, 0.03), rough=0.5),
        "techo": mat("T2_Techo", (0.30, 0.31, 0.33), rough=0.9),
        "led": mat("T2_PanelLED", (1, 1, 1), rough=0.4, emis=6.0, ecol=(1.0, 0.97, 0.92)),
        "rack_azul": mat("T2_RackAzul", (0.03, 0.15, 0.42), rough=0.45, metal=0.3),
        "rack_naranja": mat("T2_RackNaranja", (0.95, 0.32, 0.02), rough=0.45, metal=0.2),
        "madera": mat("T2_Madera", (0.42, 0.25, 0.12), rough=0.6, bump=0.05, escala_bump=40),
        "acero": mat("T2_Acero", (0.45, 0.46, 0.48), rough=0.35, metal=0.9),
        "negro": mat("T2_NegroMate", (0.03, 0.03, 0.035), rough=0.6),
        "rojo": mat("T2_RojoMaquina", (0.55, 0.03, 0.02), rough=0.35, coat=0.4),
        "gris_maq": mat("T2_GrisMaquina", (0.25, 0.27, 0.30), rough=0.4, metal=0.4),
        "panel": mat("T2_Perforado", (0.35, 0.37, 0.40), rough=0.6),
        "pantalla": mat("T2_PantallaVerde", (0.05, 0.6, 0.2), rough=0.3, emis=2.5),
        "mango_rojo": mat("T2_MangoRojo", (0.7, 0.05, 0.03), rough=0.4),
        "mango_amar": mat("T2_MangoAmarillo", (0.95, 0.75, 0.05), rough=0.4),
    }

def _obj(nombre, me, m, col=None, liso=True, padre=None, loc=(0, 0, 0)):
    if liso:
        for p in me.polygons: p.use_smooth = True
    if m is not None and not me.materials: me.materials.append(m)
    o = bpy.data.objects.new(nombre, me); (col or _col()).objects.link(o)
    o.location = loc
    if padre: o.parent = padre
    return o

def caja(nombre, centro, tam, m, bisel=0.0, col=None, padre=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * tam[0], v.co.y * tam[1], v.co.z * tam[2]))
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = _obj(nombre, me, m, col, liso=False, padre=padre, loc=centro); o.rotation_euler = rot
    if bisel:
        md = o.modifiers.new("Bisel", "BEVEL"); md.width = bisel; md.segments = 3; md.limit_method = 'ANGLE'
    return o

def cilindro(nombre, centro, r, h, m, seg=32, col=None, padre=None, rot=(0, 0, 0), r2=None, bisel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = _obj(nombre, me, m, col, liso=True, padre=padre, loc=centro); o.rotation_euler = rot
    if bisel:
        md = o.modifiers.new("Bisel", "BEVEL"); md.width = bisel; md.segments = 2; md.limit_method = 'ANGLE'
    return o

# ------------------------------------------------------------------ NEUMÁTICO 205/55 R16 (eje = Z local)
ANCHO = 0.205; R_LLANTA = 0.2032; ALTO = 0.55 * ANCHO; R_EXT = R_LLANTA + ALTO    # 0,316 m
PROF = 0.008; TWI = 0.0016                                                     # dibujo nuevo 8 mm, testigo 1,6 mm

def _catmull(pts, n):
    P = [pts[0]] + pts + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (np.array(P[j]) for j in (i - 1, i, i + 1, i + 2))
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(np.array(pts[-1])); return out

def _perfil(n_flanco, n_banda):
    """Sección (a = axial, r = radial, s = posición en la banda -1..1 o None en flanco). Lazo cerrado."""
    W = ANCHO
    lado = [(0.40 * W, R_LLANTA + 0.004), (0.47 * W, R_LLANTA + 0.022), (0.505 * W, R_LLANTA + 0.5 * ALTO),
            (0.49 * W, R_EXT - 0.022), (0.455 * W, R_EXT - 0.006), (0.43 * W, R_EXT - 0.0008)]
    der = _catmull(lado, max(2, n_flanco // 5))
    banda = [(0.43 * W * s, R_EXT - 0.003 * s * s, s) for s in np.linspace(1, -1, n_banda)][1:-1]
    izq = [(-a, r) for a, r in reversed(der)]
    prof = [(a, r, None) for a, r in der] + banda + [(a, r, None) for a, r in izq]
    interior = [(0.36 * W * s, R_LLANTA + 0.002, None) for s in np.linspace(-1, 1, 6)[1:-1]]
    return prof + interior

def _dibujo(theta, s, n_pasos=40):
    """Profundidad del dibujo (m) en el ángulo theta y la posición s (-1..1) de la banda. Devuelve (prof, es_ranura_ppal)."""
    a = abs(s); fase = theta * n_pasos / (2 * math.pi) + 1.25 * a
    fr = fase - math.floor(fase)
    for c in (0.24, 0.62):                                     # 4 ranuras principales (circunferenciales)
        if abs(a - c) < 0.05:
            ft = theta * 6 / (2 * math.pi); ft -= math.floor(ft)
            return (PROF - TWI if ft < 0.025 else PROF), True   # testigo TWI: 6 por vuelta
    if a < 0.19:                                               # nervio central con laminillas finas
        f2 = (theta * n_pasos / (2 * math.pi) + 0.5) % 1.0
        return (0.0025 if f2 < 0.035 else 0.0), False
    if fr < 0.17:                                              # ranuras laterales en V (direccional)
        return (0.0065 if a < 0.94 else 0.0065 * (1 - (a - 0.94) / 0.06)), False
    if a > 0.68 and abs(fr - 0.56) < 0.02:                     # laminilla del hombro
        return 0.002, False
    return 0.0, False

def malla_neumatico(nombre, n_u=800, n_flanco=24, n_banda=110, n_pasos=40, nervios=True):
    """Crea (o devuelve) la malla del neumático, con shape key 'gastado' (dibujo hasta el testigo de 1,6 mm)."""
    me = bpy.data.meshes.get(nombre)
    if me: return me
    prof = _perfil(n_flanco, n_banda); K = len(prof)
    V = []; Vg = []
    for i in range(n_u):
        th = 2 * math.pi * i / n_u; c, s_ = math.cos(th), math.sin(th)
        for (a, r, sb) in prof:
            rr = r; rg = r
            if sb is not None:
                d, _ = _dibujo(th, sb, n_pasos)
                rr = r - d; rg = min(rr, r - (PROF - TWI))     # gastado: la banda baja hasta el testigo
            elif nervios and r > R_LLANTA + 0.03 and r < R_EXT - 0.03:
                rn = (r - R_LLANTA) / ALTO                      # nervios concéntricos del flanco
                bump = 0.0012 if (abs(rn - 0.38) < 0.012 or abs(rn - 0.80) < 0.01) else 0.0
                a = a + math.copysign(bump, a)
            V.append((rr * c, rr * s_, a)); Vg.append((rg * c, rg * s_, a))
    F = []
    for i in range(n_u):
        i2 = (i + 1) % n_u
        for k in range(K):
            k2 = (k + 1) % K
            F.append((i * K + k, i2 * K + k, i2 * K + k2, i * K + k2))
    me = bpy.data.meshes.new(nombre); me.from_pydata(V, [], F); me.update()
    for p in me.polygons: p.use_smooth = True
    tmp = bpy.data.objects.new("_tmp_" + nombre, me); bpy.context.scene.collection.objects.link(tmp)
    tmp.shape_key_add(name="Basis", from_mix=False)
    kb = tmp.shape_key_add(name="gastado", from_mix=False)
    kb.data.foreach_set("co", np.array(Vg, dtype=np.float32).ravel()); kb.value = 0.0   # nuevo por defecto
    bpy.data.objects.remove(tmp, do_unlink=True)
    me["dot"] = 0
    return me

def malla_llanta(nombre, seg=96):
    """Llanta de aleación de 5 radios dobles (eje Z; cara exterior hacia +Z)."""
    me = bpy.data.meshes.get(nombre)
    if me: return me
    bm = bmesh.new()
    def anillo(r1, r2, z1, z2, n=seg):
        g = bmesh.ops.create_cone(bm, cap_ends=False, segments=n, radius1=r1, radius2=r2, depth=abs(z2 - z1))
        bmesh.ops.translate(bm, verts=g["verts"], vec=(0, 0, (z1 + z2) / 2))
    anillo(R_LLANTA - 0.006, R_LLANTA - 0.006, -0.085, 0.085)          # barril
    for z in (-0.085, 0.085):                                           # pestañas
        g = bmesh.ops.create_circle(bm, cap_ends=False, segments=seg, radius=R_LLANTA + 0.004)
        bmesh.ops.translate(bm, verts=g["verts"], vec=(0, 0, z))
    # radios dobles
    for k in range(5):
        for d in (-7.5, 7.5):
            ang = R(k * 72 + d)
            r0, r1 = 0.058, R_LLANTA - 0.008
            w0, w1, t = 0.016, 0.011, 0.022
            ca, sa = math.cos(ang), math.sin(ang); px, py = -sa, ca
            zz0, zz1 = 0.062, 0.045                                       # radio con caída (dish)
            pts = []
            for (r, w, z) in ((r0, w0, zz0), (r1, w1, zz1)):
                for sgn in (-1, 1):
                    for dz in (0, -t):
                        pts.append(bm.verts.new((ca * r + px * w * sgn, sa * r + py * w * sgn, z + dz)))
            v = pts  # 0:r0,-w,top 1:r0,-w,bot 2:r0,+w,top 3:r0,+w,bot 4..7 idem en r1
            for f in ((0, 2, 6, 4), (1, 5, 7, 3), (0, 4, 5, 1), (2, 3, 7, 6), (0, 1, 3, 2), (4, 6, 7, 5)):
                bm.faces.new([v[i] for i in f])
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.064, radius2=0.058, depth=0.03)  # buje
    bmesh.ops.translate(bm, verts=g["verts"], vec=(0, 0, 0.052))
    g = bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=12, radius=0.03)                          # tapacubos
    for vv in g["verts"]: vv.co.z = 0.068 + max(0.0, vv.co.z) * 0.35
    for k in range(5):                                                                                   # tuercas
        a = R(k * 72 + 36)
        g = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.0095, radius2=0.0095, depth=0.014)
        bmesh.ops.translate(bm, verts=g["verts"], vec=(math.cos(a) * 0.044, math.sin(a) * 0.044, 0.072))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me

def rueda(nombre, pos, rot=(0, 0, 0), detalle="alto", con_llanta=True, M=None, col=None, padre=None):
    """Rueda montada (o neumático suelto si con_llanta=False). Eje del neumático = Z local del objeto raíz."""
    M = M or materiales()
    raiz = bpy.data.objects.new(nombre, None); (col or _col()).objects.link(raiz)
    raiz.empty_display_size = 0.35; raiz.location = pos; raiz.rotation_euler = rot
    if padre: raiz.parent = padre
    mn = malla_neumatico("NEU_alto" if detalle == "alto" else "NEU_bajo",
                         *((800, 24, 110, 40) if detalle == "alto" else (252, 12, 30, 36)))
    t = _obj(nombre + "_Neumatico", mn, M["goma"], col, padre=raiz)
    if con_llanta:
        ml = malla_llanta("LLANTA_5x2")
        if not ml.materials: ml.materials.append(M["llanta"])
        _obj(nombre + "_Llanta", ml, M["llanta"], col, padre=raiz)
        disco = cilindro(nombre + "_Fondo", (0, 0, -0.01), R_LLANTA - 0.01, 0.01, M["llanta_osc"], seg=64, col=col, padre=raiz)
    return raiz

def pila_neumaticos(nombre, pos, n=4, M=None, col=None, giro=0.0):
    M = M or materiales(); raiz = bpy.data.objects.new(nombre, None); (col or _col()).objects.link(raiz)
    raiz.location = pos; raiz.rotation_euler = (0, 0, giro)
    mn = malla_neumatico("NEU_bajo", 252, 12, 30, 36)
    for k in range(n):
        o = _obj(f"{nombre}_{k}", mn, M["goma"], col, padre=raiz, loc=(0.004 * ((k * 7) % 3 - 1), 0.004 * ((k * 5) % 3 - 1), ANCHO * 0.5 + k * ANCHO * 1.01))
        o.rotation_euler = (0, 0, R(k * 37))
    return raiz

# ------------------------------------------------------------------ MÁQUINAS Y MOBILIARIO
def estanteria_neumaticos(x0, y, M, col, bahias=3, niveles=(0.10, 1.02, 1.94), ancho=2.5):
    mn = malla_neumatico("NEU_bajo", 252, 12, 30, 36)
    for b in range(bahias):
        xc = x0 + b * ancho
        for sx in (-1, 1):
            for sy in (-1, 1):
                caja(f"Rack_Pie_{b}_{sx}_{sy}", (xc + sx * ancho / 2, y + sy * 0.32, 1.5), (0.08, 0.06, 3.0), M["rack_azul"], col=col)
        for j, z in enumerate(niveles):
            for sy in (-1, 1):
                caja(f"Rack_Larguero_{b}_{j}_{sy}", (xc, y + sy * 0.32, z), (ancho - 0.08, 0.05, 0.1), M["rack_naranja"], col=col)
            n = 10
            for k in range(n):
                o = _obj(f"Rack_Neu_{b}_{j}_{k}", mn, M["goma"], col, loc=(xc - ancho / 2 + 0.17 + k * (ancho - 0.34) / (n - 1), y, z + 0.05 + R_EXT))
                o.rotation_mode = 'ZYX'; o.rotation_euler = (0, R(90), R(((b * 31 + j * 17 + k * 7) % 11) * 6))
        caja(f"Rack_Arriostre_{b}", (xc, y + 0.32, 2.55), (0.04, 0.03, 1.1), M["rack_azul"], col=col, rot=(0, R(35), 0))

def elevador(x, y, M, col):
    for sx in (-1, 1):
        caja(f"Elev_Columna{sx}", (x + sx * 1.45, y, 1.65), (0.32, 0.36, 3.3), M["gris_maq"], bisel=0.01, col=col)
        caja(f"Elev_Base{sx}", (x + sx * 1.45, y, 0.015), (0.6, 0.6, 0.03), M["linea"], col=col)
        caja(f"Elev_Carro{sx}", (x + sx * 1.30, y, 0.30), (0.12, 0.30, 0.42), M["rojo"], col=col)
        for sy in (-1, 1):
            brazo = caja(f"Elev_Brazo{sx}{sy}", (x + sx * 1.0, y + sy * 0.45, 0.17), (0.62, 0.09, 0.07), M["gris_maq"], col=col, rot=(0, 0, R(sx * sy * 28)))
            cilindro(f"Elev_Taco{sx}{sy}", (x + sx * 0.75, y + sy * 0.62, 0.23), 0.06, 0.05, M["negro"], col=col)
    caja("Elev_Travesano", (x, y, 3.25), (3.2, 0.2, 0.16), M["gris_maq"], col=col)
    for sx in (-1, 1):
        caja(f"Elev_Bandas{sx}", (x + sx * 1.45, y - 0.185, 1.0), (0.3, 0.005, 0.12), M["linea"], col=col)

def desmontadora(x, y, M, col, giro=0.0):
    raiz = bpy.data.objects.new("Desmontadora", None); col.objects.link(raiz); raiz.location = (x, y, 0); raiz.rotation_euler = (0, 0, giro)
    caja("Desm_Cuerpo", (0, 0, 0.42), (0.75, 0.95, 0.84), M["rojo"], bisel=0.02, col=col, padre=raiz)
    cilindro("Desm_Plato", (0, -0.12, 0.88), 0.30, 0.05, M["acero"], seg=48, col=col, padre=raiz)
    for k in range(4):
        a = R(45 + k * 90)
        caja(f"Desm_Garra{k}", (math.cos(a) * 0.24, -0.12 + math.sin(a) * 0.24, 0.92), (0.08, 0.04, 0.05), M["negro"], col=col, padre=raiz, rot=(0, 0, a))
    caja("Desm_Columna", (0, 0.40, 1.15), (0.16, 0.16, 1.5), M["rojo"], bisel=0.01, col=col, padre=raiz)
    caja("Desm_Brazo", (0, 0.12, 1.78), (0.10, 0.62, 0.10), M["gris_maq"], col=col, padre=raiz)
    caja("Desm_Cabezal", (0, -0.15, 1.40), (0.07, 0.07, 0.72), M["acero"], col=col, padre=raiz)
    caja("Desm_Destalonador", (0.48, 0.10, 0.55), (0.10, 0.6, 0.09), M["gris_maq"], col=col, padre=raiz, rot=(R(12), 0, 0))
    for k in range(3):
        caja(f"Desm_Pedal{k}", (-0.2 + k * 0.2, -0.52, 0.04), (0.12, 0.18, 0.03), M["negro"], col=col, padre=raiz)
    return raiz

def equilibradora(x, y, M, col, giro=0.0):
    raiz = bpy.data.objects.new("Equilibradora", None); col.objects.link(raiz); raiz.location = (x, y, 0); raiz.rotation_euler = (0, 0, giro)
    caja("Equi_Cuerpo", (0, 0, 0.55), (0.55, 0.80, 1.10), M["gris_maq"], bisel=0.02, col=col, padre=raiz)
    caja("Equi_Panel", (0, -0.30, 1.16), (0.50, 0.28, 0.12), M["negro"], bisel=0.01, col=col, padre=raiz, rot=(R(-25), 0, 0))
    caja("Equi_Pantalla", (0, -0.33, 1.20), (0.38, 0.16, 0.01), M["pantalla"], col=col, padre=raiz, rot=(R(-25), 0, 0))
    cilindro("Equi_Eje", (0.42, 0, 0.82), 0.02, 0.36, M["acero"], col=col, padre=raiz, rot=(0, R(90), 0))
    cilindro("Equi_Brida", (0.30, 0, 0.82), 0.07, 0.05, M["acero"], col=col, padre=raiz, rot=(0, R(90), 0))
    # rueda montada en el eje
    w = rueda("Equi_Rueda", (0.48, 0, 0.82), (0, R(90), 0), detalle="bajo", M=M, col=col, padre=raiz)
    # capota (semicírculo)
    bm = bmesh.new(); seg = 24; pts = []
    for i in range(seg + 1):
        a = math.pi * i / seg
        for x_ in (0.30, 0.68):
            pts.append(bm.verts.new((x_, math.cos(a) * 0.40, 0.82 + math.sin(a) * 0.40)))
    for i in range(seg): bm.faces.new((pts[2 * i], pts[2 * i + 2], pts[2 * i + 3], pts[2 * i + 1]))
    me = bpy.data.meshes.new("Equi_Capota"); bm.to_mesh(me); bm.free()
    o = _obj("Equi_Capota", me, M["rojo"], col, padre=raiz); o.modifiers.new("Grosor", "SOLIDIFY").thickness = 0.01
    o.rotation_euler = (0, 0, 0)
    return raiz

def banco_y_panel(x, y, M, col, giro=0.0):
    raiz = bpy.data.objects.new("Banco", None); col.objects.link(raiz); raiz.location = (x, y, 0); raiz.rotation_euler = (0, 0, giro)
    caja("Banco_Tablero", (0, 0, 0.90), (2.2, 0.72, 0.05), M["madera"], bisel=0.005, col=col, padre=raiz)
    for sx in (-1, 1):
        for sy in (-1, 1):
            caja(f"Banco_Pata{sx}{sy}", (sx * 1.04, sy * 0.32, 0.44), (0.05, 0.05, 0.88), M["acero"], col=col, padre=raiz)
    caja("Banco_Balda", (0, 0, 0.18), (2.1, 0.66, 0.03), M["acero"], col=col, padre=raiz)
    caja("Banco_Tornillo", (-0.85, -0.25, 0.99), (0.16, 0.22, 0.13), M["gris_maq"], bisel=0.01, col=col, padre=raiz)
    caja("Banco_Caja", (0.6, 0.05, 1.0), (0.48, 0.24, 0.18), M["rojo"], bisel=0.01, col=col, padre=raiz)
    # panel perforado con herramientas
    caja("Panel_Fondo", (0, 0.37, 1.65), (2.2, 0.02, 1.2), M["panel"], col=col, padre=raiz)
    for i in range(5):                                         # llaves de mayor a menor
        L = 0.30 - i * 0.035
        caja(f"Panel_Llave{i}", (-0.9 + i * 0.12, 0.34, 1.80 - L / 2), (0.022, 0.012, L), M["acero"], col=col, padre=raiz)
        cilindro(f"Panel_LlaveOjo{i}", (-0.9 + i * 0.12, 0.34, 1.80 - L), 0.024, 0.012, M["acero"], col=col, padre=raiz, rot=(R(90), 0, 0))
    for i, m_ in enumerate((M["mango_rojo"], M["mango_amar"], M["mango_rojo"], M["mango_amar"])):
        cilindro(f"Panel_Destorn{i}", (0.05 + i * 0.09, 0.34, 1.86), 0.014, 0.12, m_, col=col, padre=raiz)
        cilindro(f"Panel_DestornV{i}", (0.05 + i * 0.09, 0.34, 1.73), 0.004, 0.16, M["acero"], col=col, padre=raiz)
    caja("Panel_Martillo", (0.62, 0.34, 1.70), (0.03, 0.025, 0.32), M["madera"], col=col, padre=raiz)
    caja("Panel_MartilloCab", (0.62, 0.34, 1.86), (0.13, 0.03, 0.04), M["acero"], col=col, padre=raiz)
    caja("Panel_Pistola", (0.88, 0.33, 1.68), (0.18, 0.06, 0.12), M["negro"], bisel=0.01, col=col, padre=raiz)
    caja("Panel_PistolaMango", (0.84, 0.33, 1.58), (0.05, 0.05, 0.14), M["negro"], col=col, padre=raiz, rot=(0, R(-12), 0))
    # armario de cajones
    caja("Armario_Cuerpo", (1.55, -0.05, 0.52), (0.72, 0.5, 1.0), M["rojo"], bisel=0.01, col=col, padre=raiz)
    for k in range(6):
        z = 0.12 + k * 0.155
        caja(f"Armario_Tirador{k}", (1.55, -0.305, z + 0.06), (0.5, 0.015, 0.018), M["acero"], col=col, padre=raiz)
        caja(f"Armario_Junta{k}", (1.55, -0.302, z), (0.70, 0.004, 0.006), M["negro"], col=col, padre=raiz)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cilindro(f"Armario_Rueda{sx}{sy}", (1.55 + sx * 0.3, -0.05 + sy * 0.2, 0.035), 0.035, 0.03, M["negro"], col=col, padre=raiz, rot=(R(90), 0, 0))
    return raiz

def compresor(x, y, M, col):
    cilindro("Compresor_Calderin", (x, y, 0.38), 0.24, 1.0, M["rojo"], seg=40, col=col, rot=(0, R(90), 0))
    caja("Compresor_Motor", (x - 0.1, y, 0.72), (0.40, 0.32, 0.28), M["gris_maq"], bisel=0.02, col=col)
    for sx in (-1, 1): caja(f"Compresor_Pata{sx}", (x + sx * 0.35, y, 0.08), (0.08, 0.36, 0.16), M["negro"], col=col)

# ------------------------------------------------------------------ TALLER COMPLETO
def construir_taller(ancho=12.0, fondo_y=4.8, frente_y=-7.0, alto=4.4):
    col = _col(); M = materiales()
    W2 = ancho / 2; L = fondo_y - frente_y; yc = (fondo_y + frente_y) / 2
    caja("T2_Suelo", (0, yc, -0.05), (ancho + 2, L + 2, 0.1), M["suelo"], col=col)
    caja("T2_ParedFondo", (0, fondo_y + 0.1, alto / 2), (ancho + 2, 0.2, alto), M["pared"], col=col)
    caja("T2_ZocaloFondo", (0, fondo_y - 0.005, 0.6), (ancho + 2, 0.02, 1.2), M["zocalo"], col=col)
    caja("T2_FranjaFondo", (0, fondo_y - 0.012, 1.22), (ancho + 2, 0.01, 0.06), M["franja"], col=col)
    for sx in (-1, 1):
        caja(f"T2_Pared{sx}", (sx * (W2 + 0.1), yc, alto / 2), (0.2, L + 2, alto), M["pared"], col=col)
        caja(f"T2_Zocalo{sx}", (sx * (W2 - 0.005), yc, 0.6), (0.02, L + 2, 1.2), M["zocalo"], col=col)
        caja(f"T2_Franja{sx}", (sx * (W2 - 0.012), yc, 1.22), (0.01, L + 2, 0.06), M["franja"], col=col)
    caja("T2_Techo", (0, yc, alto + 0.05), (ancho + 2, L + 2, 0.1), M["techo"], col=col)
    # paneles LED del techo (emisivos) + luces de área que iluminan de verdad
    k = 0
    for x in (-3.0, 0.0, 3.0):
        for y in (-3.5, -0.5, 2.5):
            caja(f"T2_LED{k}", (x, y, alto - 0.02), (1.2, 0.3, 0.03), M["led"], col=col); k += 1
    for i, (x, y) in enumerate(((-3, -1.5), (3, -1.5), (0, 2.5), (0, -4.0))):
        ld = bpy.data.lights.new(f"T2_LuzTecho{i}", "AREA"); ld.shape = 'RECTANGLE'; ld.size = 2.4; ld.size_y = 1.2
        ld.energy = 260; ld.color = (1.0, 0.96, 0.90)
        o = bpy.data.objects.new(f"T2_LuzTecho{i}", ld); col.objects.link(o); o.location = (x, y, alto - 0.1)
    # líneas amarillas del suelo (pasillo y zona del elevador)
    for y in (3.55, -1.6):
        caja(f"T2_Linea_{y}", (0, y, 0.002), (ancho - 0.4, 0.08, 0.004), M["linea"], col=col)
    for (cx, cy, w, h) in ((4.3, 1.3, 3.6, 3.6),):
        for s in (-1, 1):
            caja(f"T2_LineaElevX{s}", (cx, cy + s * h / 2, 0.003), (w, 0.07, 0.004), M["linea"], col=col)
            caja(f"T2_LineaElevY{s}", (cx + s * w / 2, cy, 0.003), (0.07, h, 0.004), M["linea"], col=col)
    # mobiliario
    estanteria_neumaticos(-2.5, fondo_y - 0.45, M, col)
    elevador(4.3, 1.3, M, col)
    desmontadora(-1.8, 2.2, M, col, giro=R(-15))
    equilibradora(1.9, 2.3, M, col, giro=R(20))
    banco_y_panel(-W2 + 0.4, 0.6, M, col, giro=R(-90))
    compresor(-W2 + 0.5, 3.6, M, col)
    pila_neumaticos("Pila_A", (-4.6, -0.8, 0), 4, M, col)
    pila_neumaticos("Pila_B", (-4.0, -0.4, 0), 3, M, col)
    return {"M": M, "col": col}

def ajustes_render(sc=None):
    sc = sc or bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    try: sc.eevee.use_raytracing = True
    except Exception: pass
    try: sc.eevee.use_shadows = True
    except Exception: pass
    sc.view_settings.view_transform = "AgX"
    try: sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception: pass
    if not sc.world: sc.world = bpy.data.worlds.new("Mundo")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    if bg: bg.inputs[0].default_value = (0.05, 0.05, 0.055, 1); bg.inputs[1].default_value = 0.5
