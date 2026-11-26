# NEUMÁTICO REALISTA POR DENTRO (26-11-2026) · 205/55 R16, eje = Z local, a = axial, r = radial (metros)
# Piezas con su estructura de verdad (nada de anillos lisos que cambian de color):
#   alma interna (butilo, 2 mm) · carcasa (900 hilos de poliéster radiales que abrazan el talón + goma de unión)
#   talones (haz de 4x4 alambres de acero con baño de latón + relleno de goma dura) · 2 cinturones de acero
#   (~460 cables trenzados a ±24°, cruzados) · goma exterior (banda de rodadura con su dibujo + 2 flancos con nervios
#   y marcado 205/55 R16 91V en relieve).
# Necesita el módulo taller_v2 ya ejecutado en el diccionario T (perfil, dibujo, catmull).
import bpy, bmesh, math
import numpy as np
from mathutils import Vector, Matrix

def _catm(T, pts, n):
    return [tuple(map(float, p)) for p in T["_catmull"]([tuple(p) for p in pts], n)]
def espejo(media):
    return media + [(-a, r) for (a, r) in reversed(media[:-1])]
def _remuestrear(pts, n):
    p = np.array(pts, float); d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    t = np.linspace(0, d[-1], n); return np.c_[np.interp(t, d, p[:, 0]), np.interp(t, d, p[:, 1])]

# ---------------------------------------------------------------- materiales realistas
def _nodos_trenza(m, escala=(380.0, 1.0), giro=0.6, fuerza=0.6, color_rampa=None):
    """Relieve de hilo trenzado a lo largo del cable (usa el UV: u = largo, v = vuelta)."""
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    uv = nt.nodes.new("ShaderNodeUVMap"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (escala[0], escala[1], 1); mp.inputs["Rotation"].default_value = (0, 0, giro)
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 1.0; wv.inputs["Distortion"].default_value = 0.0
    wv.inputs["Detail"].default_value = 0.0
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = fuerza; bp.inputs["Distance"].default_value = 0.0004
    nt.links.new(uv.outputs["UV"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    if color_rampa:
        cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (*color_rampa[0], 1); cr.color_ramp.elements[1].color = (*color_rampa[1], 1)
        nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
def _mat(nombre, color, rough, metal=0.0, coat=0.0, spec=None):
    m = bpy.data.materials.get(nombre)
    if m: return m, False
    m = bpy.data.materials.new(nombre); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if coat and "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = coat
    if spec is not None and "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = spec
    return m, True
def _ruido(m, escala, fuerza, dist=0.0003, rough_var=None):
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = escala; nz.inputs["Detail"].default_value = 10; nz.inputs["Roughness"].default_value = 0.65
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = fuerza; bp.inputs["Distance"].default_value = dist
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    if not b.inputs["Normal"].is_linked: nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    if rough_var:
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rough_var[0]; mr.inputs["To Max"].default_value = rough_var[1]
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
def materiales_reales():
    M = {}
    m, n = _mat("R_Goma", (0.016, 0.016, 0.018), 0.72, spec=0.4)
    if n: _ruido(m, 2200, 0.25, rough_var=(0.62, 0.85))
    M["goma"] = m
    m, n = _mat("R_Butilo", (0.020, 0.021, 0.024), 0.55, spec=0.35)
    if n: _ruido(m, 900, 0.12, rough_var=(0.48, 0.62))
    M["butilo"] = m
    m, n = _mat("R_GomaUnion", (0.022, 0.022, 0.024), 0.55, spec=0.45)
    if n: _ruido(m, 1500, 0.15)
    M["union"] = m
    m, n = _mat("R_Poliester", (0.80, 0.72, 0.52), 0.55, spec=0.3)
    if n: _nodos_trenza(m, escala=(260.0, 1.0), giro=0.9, fuerza=0.5, color_rampa=((0.62, 0.53, 0.35), (0.88, 0.81, 0.62)))
    M["poliester"] = m
    m, n = _mat("R_CableAcero", (0.60, 0.61, 0.63), 0.34, metal=1.0)
    if n: _nodos_trenza(m, escala=(520.0, 1.0), giro=0.75, fuerza=0.8, color_rampa=((0.42, 0.43, 0.45), (0.74, 0.75, 0.77)))
    M["acero"] = m
    m, n = _mat("R_AlambreLaton", (0.78, 0.55, 0.32), 0.30, metal=1.0)
    if n: _ruido(m, 4000, 0.2)
    M["laton"] = m
    m, n = _mat("R_Relleno", (0.045, 0.045, 0.05), 0.38, spec=0.55)
    if n: _ruido(m, 1200, 0.1)
    M["relleno"] = m
    return M

# ---------------------------------------------------------------- tubos (cables e hilos) con UV, todo con numpy
def malla_tubos(nombre, rutas, normales, radio, lados=6, largo_uv=1.0):
    """rutas: (N, P, 3) puntos; normales: (N, P, 3) un vector perpendicular a cada ruta. Devuelve malla con UV."""
    rutas = np.asarray(rutas, float); normales = np.asarray(normales, float)
    N, P, _ = rutas.shape
    T = np.gradient(rutas, axis=1); T /= np.linalg.norm(T, axis=2, keepdims=True)
    Nn = normales - (normales * T).sum(2, keepdims=True) * T; Nn /= np.linalg.norm(Nn, axis=2, keepdims=True)
    B = np.cross(T, Nn)
    ang = np.linspace(0, 2 * np.pi, lados, endpoint=False)
    V = rutas[:, :, None, :] + radio * (np.cos(ang)[None, None, :, None] * Nn[:, :, None, :] + np.sin(ang)[None, None, :, None] * B[:, :, None, :])
    V = V.reshape(-1, 3)
    c = np.arange(N)[:, None, None]; k = np.arange(P - 1)[None, :, None]; j = np.arange(lados)[None, None, :]
    base = c * P * lados
    v0 = base + k * lados + j; v1 = base + (k + 1) * lados + j; v2 = base + (k + 1) * lados + (j + 1) % lados; v3 = base + k * lados + (j + 1) % lados
    F = np.stack([v0, v1, v2, v3], axis=-1).reshape(-1, 4)
    me = bpy.data.meshes.new(nombre)
    me.vertices.add(len(V)); me.vertices.foreach_set("co", V.astype(np.float32).ravel())
    me.loops.add(len(F) * 4); me.loops.foreach_set("vertex_index", F.astype(np.int32).ravel())
    me.polygons.add(len(F)); me.polygons.foreach_set("loop_start", (np.arange(len(F)) * 4).astype(np.int32))
    me.polygons.foreach_set("loop_total", np.full(len(F), 4, np.int32))
    # UV: u a lo largo (metros * largo_uv), v alrededor
    seg = np.linalg.norm(np.diff(rutas, axis=1), axis=2); dist = np.concatenate([np.zeros((N, 1)), np.cumsum(seg, axis=1)], axis=1)
    kk = np.broadcast_to(k, (N, P - 1, lados)); jj = np.broadcast_to(j, (N, P - 1, lados)); cc = np.broadcast_to(c, (N, P - 1, lados))
    u0 = dist[cc, kk] * largo_uv; u1 = dist[cc, kk + 1] * largo_uv; w0 = jj / lados; w1 = (jj + 1) / lados
    UV = np.stack([np.stack([u0, w0], -1), np.stack([u1, w0], -1), np.stack([u1, w1], -1), np.stack([u0, w1], -1)], axis=3).reshape(-1, 2)
    me.update(calc_edges=True)
    uvl = me.uv_layers.new(name="UVMap"); uvl.data.foreach_set("uv", UV.astype(np.float32).ravel())
    try: me.shade_smooth()
    except Exception:
        for p in me.polygons: p.use_smooth = True
    me.update()
    return me

def malla_revolucion(nombre, lazo, seg=360, cerrado=True):
    """Revoluciona un lazo (a, r) alrededor de Z."""
    lazo = np.asarray(lazo, float); K = len(lazo)
    th = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    V = np.stack([lazo[None, :, 1] * np.cos(th)[:, None], lazo[None, :, 1] * np.sin(th)[:, None], np.broadcast_to(lazo[None, :, 0], (seg, K))], -1).reshape(-1, 3)
    i = np.arange(seg)[:, None]; k = np.arange(K if cerrado else K - 1)[None, :]
    i2 = (i + 1) % seg; k2 = (k + 1) % K
    F = np.stack([i * K + k, i2 * K + k, i2 * K + k2, i * K + k2], -1).reshape(-1, 4)
    me = bpy.data.meshes.new(nombre); me.from_pydata(V.tolist(), [], F.tolist()); me.update()
    for p in me.polygons: p.use_smooth = True
    return me

def lazo_con_grosor(camino, grosor, hacia):
    """Convierte un camino (a, r) en un lazo cerrado con grosor; 'hacia' = +1 desplaza a la derecha del avance."""
    p = np.asarray(camino, float); t = np.gradient(p, axis=0); t /= np.linalg.norm(t, axis=1, keepdims=True)
    n = np.c_[t[:, 1], -t[:, 0]] * hacia
    q = p + n * grosor
    return np.vstack([p, q[::-1]])

# ---------------------------------------------------------------- geometría de las capas
CARC_H = [(-0.084, 0.238), (-0.083, 0.222), (-0.080, 0.2095), (-0.072, 0.2062), (-0.063, 0.2085), (-0.0615, 0.218), (-0.068, 0.232),
          (-0.084, 0.246), (-0.093, 0.262), (-0.091, 0.280), (-0.079, 0.2915), (-0.050, 0.2950), (0.0, 0.2955)]
ALMA_H = [(-0.0595, 0.2125), (-0.0592, 0.2200), (-0.0655, 0.2335), (-0.0815, 0.2475), (-0.0905, 0.2625), (-0.0885, 0.2790),
          (-0.0770, 0.2890), (-0.0490, 0.2928), (0.0, 0.2933)]
TALON_C = (0.0725, 0.2135)
APEX = [(-0.0775, 0.2195), (-0.0670, 0.2195), (-0.0810, 0.2390)]

def construir(T, col, M=None, padre=None, n_hilos=900, n_cables=300, prefijo="NR_"):
    """Crea todas las piezas como objetos hijos de 'padre'. Devuelve dict nombre->objeto."""
    M = M or materiales_reales(); O = {}
    def obj(nombre, me, mats):
        o = bpy.data.objects.get(prefijo + nombre)
        if o is None:
            for m in mats: me.materials.append(m)
            o = bpy.data.objects.new(prefijo + nombre, me); col.objects.link(o)
        o.parent = padre; O[nombre] = o; return o
    def existe(n): return bpy.data.objects.get(prefijo + n)
    # --- alma interna (2,2 mm hacia la cámara de aire)
    if not existe("AlmaInterna"):
        c = _remuestrear(espejo(_catm(T, ALMA_H, 4)), 120)
        obj("AlmaInterna", malla_revolucion(prefijo + "AlmaInterna", lazo_con_grosor(c, 0.0022, +1), seg=360), [M["butilo"]])
    else: O["AlmaInterna"] = existe("AlmaInterna")
    # --- carcasa: goma de unión + 900 hilos radiales
    camino = _remuestrear(espejo(_catm(T, CARC_H, 4)), 70)
    if not existe("CarcasaGoma"):
        obj("CarcasaGoma", malla_revolucion(prefijo + "CarcasaGoma", lazo_con_grosor(camino, 0.0009, +1), seg=360), [M["union"]])
    else: O["CarcasaGoma"] = existe("CarcasaGoma")
    if not existe("CarcasaHilos"):
        th = np.linspace(0, 2 * np.pi, n_hilos, endpoint=False)
        tg = np.gradient(camino, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True)
        n_out = -np.c_[tg[:, 1], -tg[:, 0]]                      # normal hacia fuera (lado contrario a la cámara de aire)
        cam_h = camino + n_out * 0.0005
        a = cam_h[:, 0]; r = cam_h[:, 1]
        rutas = np.stack([r[None, :] * np.cos(th)[:, None], r[None, :] * np.sin(th)[:, None], np.broadcast_to(a, (n_hilos, len(a)))], -1)
        norm = np.stack([-np.sin(th)[:, None] * np.ones_like(r)[None, :], np.cos(th)[:, None] * np.ones_like(r)[None, :], np.zeros((n_hilos, len(a)))], -1)
        obj("CarcasaHilos", malla_tubos(prefijo + "CarcasaHilos", rutas, norm, 0.00042, lados=5), [M["poliester"]])
    else: O["CarcasaHilos"] = existe("CarcasaHilos")
    # --- talones: 2 haces de 4x4 alambres + relleno
    if not existe("TalonAlambres"):
        bm_ruta = []; bm_norm = []; seg = 260; th = np.linspace(0, 2 * np.pi, seg + 1)
        for lado in (-1, 1):
            for i in range(4):
                for j in range(4):
                    aa = lado * TALON_C[0] + (i - 1.5) * 0.0021; rr = TALON_C[1] + (j - 1.5) * 0.0021
                    bm_ruta.append(np.stack([rr * np.cos(th), rr * np.sin(th), np.full_like(th, aa)], -1))
                    bm_norm.append(np.stack([np.cos(th), np.sin(th), np.zeros_like(th)], -1))
        obj("TalonAlambres", malla_tubos(prefijo + "TalonAlambres", np.array(bm_ruta), np.array(bm_norm), 0.00098, lados=8, largo_uv=1.0), [M["laton"]])
    else: O["TalonAlambres"] = existe("TalonAlambres")
    if not existe("TalonRelleno"):
        tri = _remuestrear(APEX + [APEX[0]], 24)
        me1 = malla_revolucion("tmp_apex1", tri, seg=360); me2 = malla_revolucion("tmp_apex2", np.c_[-tri[:, 0], tri[:, 1]], seg=360)
        bm = bmesh.new(); bm.from_mesh(me1); bm.from_mesh(me2); me = bpy.data.meshes.new(prefijo + "TalonRelleno"); bm.to_mesh(me); bm.free()
        bpy.data.meshes.remove(me1); bpy.data.meshes.remove(me2)
        for p in me.polygons: p.use_smooth = True
        obj("TalonRelleno", me, [M["relleno"]])
    else: O["TalonRelleno"] = existe("TalonRelleno")
    # --- cinturones: cables trenzados en diagonal (+24° y -24°) sobre una lámina de goma
    for k, (r0, media, ang) in enumerate(((0.2985, 0.077, 24.0), (0.3005, 0.071, -24.0))):
        nm = f"Cinturon{k + 1}"
        if not existe(nm + "Cables"):
            P = 12; aa = np.linspace(-media, media, P); tana = math.tan(math.radians(abs(ang))) * (1 if ang > 0 else -1)
            th0 = np.linspace(0, 2 * np.pi, n_cables, endpoint=False)
            dth = aa / tana / r0
            TH = th0[:, None] + dth[None, :]; rr = r0 + 0.0008
            rutas = np.stack([rr * np.cos(TH), rr * np.sin(TH), np.broadcast_to(aa, TH.shape)], -1)
            norm = np.stack([np.cos(TH), np.sin(TH), np.zeros_like(TH)], -1)
            obj(nm + "Cables", malla_tubos(prefijo + nm + "Cables", rutas, norm, 0.00072, lados=6, largo_uv=1.0), [M["acero"]])
        else: O[nm + "Cables"] = existe(nm + "Cables")
        if not existe(nm + "Goma"):
            lam = [(-media - 0.001, r0 - 0.0004), (media + 0.001, r0 - 0.0004), (media + 0.001, r0 - 0.0010), (-media - 0.001, r0 - 0.0010)]
            obj(nm + "Goma", malla_revolucion(prefijo + nm + "Goma", lam, seg=360), [M["union"]])
        else: O[nm + "Goma"] = existe(nm + "Goma")
    # --- goma exterior: banda de rodadura con dibujo + flancos
    if not existe("Banda"):
        obj("Banda", malla_banda(T, prefijo + "Banda"), [M["goma"]])
    else: O["Banda"] = existe("Banda")
    if not existe("Flancos"):
        obj("Flancos", malla_flancos(T, prefijo + "Flancos"), [M["goma"]])
    else: O["Flancos"] = existe("Flancos")
    if not existe("Marcado"):
        me = malla_marcado(T, prefijo + "Marcado")
        if me: obj("Marcado", me, [M["goma"]])
    else: O["Marcado"] = existe("Marcado")
    return O, M

def malla_banda(T, nombre, n_u=720, n_banda=96):
    W = T["ANCHO"]; R_EXT = T["R_EXT"]; dib = T["_dibujo"]
    ss = np.linspace(1, -1, n_banda)
    arriba = [(0.43 * W * s, R_EXT - 0.003 * s * s, s) for s in ss]
    resto = [(-0.0933, 0.310, None), (-0.0975, 0.3025, None), (-0.06, 0.3025, None), (0.0, 0.3025, None), (0.06, 0.3025, None), (0.0975, 0.3025, None), (0.0933, 0.310, None)]
    lazo = arriba + resto; K = len(lazo)
    th = np.linspace(0, 2 * np.pi, n_u, endpoint=False); V = []
    for t in th:
        c, s_ = math.cos(t), math.sin(t)
        for (a, r, sb) in lazo:
            rr = r - (dib(t, sb, 40)[0] if sb is not None else 0.0)
            V.append((rr * c, rr * s_, a))
    i = np.arange(n_u)[:, None]; k = np.arange(K)[None, :]
    F = np.stack([i * K + k, ((i + 1) % n_u) * K + k, ((i + 1) % n_u) * K + (k + 1) % K, i * K + (k + 1) % K], -1).reshape(-1, 4)
    me = bpy.data.meshes.new(nombre); me.from_pydata(V, [], F.tolist()); me.update()
    for p in me.polygons: p.use_smooth = True
    return me

FLANCO_EXT = [(0.0820, 0.2072), (0.0890, 0.2140), (0.0964, 0.2252), (0.1015, 0.2420), (0.1035, 0.2596), (0.1025, 0.2780), (0.1005, 0.2940), (0.0975, 0.3025)]
def malla_flancos(T, nombre, n_u=480):
    ext = _remuestrear(_catm(T, FLANCO_EXT, 5), 40)
    rn = (ext[:, 1] - 0.2032) / (0.316 - 0.2032)
    nerv = np.where((np.abs(rn - 0.38) < 0.014) | (np.abs(rn - 0.80) < 0.012), 0.0011, 0.0)
    ext2 = ext.copy(); ext2[:, 0] += nerv
    inte = ext.copy(); inte[:, 0] -= np.interp(ext[:, 1], [0.207, 0.225, 0.26, 0.29, 0.3025], [0.010, 0.011, 0.008, 0.012, 0.004])
    lazo = np.vstack([ext2, inte[::-1]])
    m1 = malla_revolucion("tmp_f1", lazo, seg=n_u); m2 = malla_revolucion("tmp_f2", np.c_[-lazo[::-1, 0], lazo[::-1, 1]], seg=n_u)
    bm = bmesh.new(); bm.from_mesh(m1); bm.from_mesh(m2); me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    bpy.data.meshes.remove(m1); bpy.data.meshes.remove(m2)
    for p in me.polygons: p.use_smooth = True
    return me

def malla_marcado(T, nombre):
    """Letras en relieve sobre el flanco exterior (+Z): medida y tipo, sin marcas comerciales."""
    textos = [("205/55 R16 91V", 0.270, 90.0, 0.0135), ("TUBELESS", 0.270, -90.0, 0.0115), ("RADIAL", 0.240, -90.0, 0.0085)]
    ext = _remuestrear(_catm(T, FLANCO_EXT, 5), 60)
    bm_tot = bmesh.new()
    for (txt, r0, ang0, alto) in textos:
        cu = bpy.data.curves.new("tmp_txt", "FONT"); cu.body = txt; cu.size = alto; cu.extrude = 0.0008; cu.align_x = 'CENTER'
        try: cu.font = bpy.data.fonts.load(r"C:\Windows\Fonts\arialbd.ttf", check_existing=True)
        except Exception: pass
        ob = bpy.data.objects.new("tmp_txt", cu); bpy.context.scene.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
        co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        x, y, z = co[:, 0], co[:, 1], co[:, 2]
        # x -> a lo largo del arco (de derecha a izquierda para leerse desde fuera), y -> radio
        th = math.radians(ang0) - x / r0
        rr = r0 + y
        asup = np.interp(rr, ext[:, 1], ext[:, 0])
        co2 = np.c_[rr * np.cos(th), rr * np.sin(th), asup + z + 0.0011]
        me.vertices.foreach_set("co", co2.astype(np.float32).ravel()); me.update()
        bm_tot.from_mesh(me); bpy.data.meshes.remove(me)
    out = bpy.data.meshes.new(nombre); bm_tot.to_mesh(out); bm_tot.free()
    for p in out.polygons: p.use_smooth = False
    return out

def trozos_irregulares(T, nombre, mat, n_ang=120, n_prof=18, seed=11):
    """Miles de trozos de goma (formas irregulares) sobre la superficie exterior + shape key 'explota'."""
    rng = np.random.default_rng(seed); R_LL, R_EXT = T["R_LLANTA"], T["R_EXT"]
    prof = T["_perfil"](24, 40)[:-4]
    pa = [np.array([prof[0][0], prof[0][1]], float)]
    for (a, r, s) in prof[1:]:
        q = np.array([a, r], float)
        if np.linalg.norm(q - pa[-1]) > 1e-5: pa.append(q)
    pa = np.array(pa); seglen = np.linalg.norm(np.diff(pa, axis=0), axis=1); cum = np.r_[0, np.cumsum(seglen)]; L = cum[-1]
    V = []; V2 = []; Fc = []
    caras = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))
    for j in range(n_prof):
        sj = (j + 0.5) / n_prof * L; k = min(len(seglen) - 1, int(np.searchsorted(cum, sj) - 1))
        tt = (sj - cum[k]) / seglen[k]; a0, r0 = pa[k] + tt * (pa[k + 1] - pa[k])
        d = (pa[k + 1] - pa[k]) / seglen[k]; nrm = np.array([d[1], -d[0]])
        if np.dot(nrm, np.array([a0, r0 - (R_LL + R_EXT) / 2])) < 0: nrm = -nrm
        hy = L / n_prof / 2
        for i in range(n_ang):
            th = 2 * math.pi * (i + 0.5 * (j % 2) + rng.uniform(-0.2, 0.2)) / n_ang
            er = np.array([math.cos(th), math.sin(th), 0.0]); ez = np.array([0, 0, 1.0]); et = np.array([-math.sin(th), math.cos(th), 0.0])
            N3 = nrm[0] * ez + nrm[1] * er; T3 = d[0] * ez + d[1] * er
            hx = math.pi * r0 / n_ang * rng.uniform(0.75, 1.15); hz = rng.uniform(0.004, 0.009)
            c = r0 * er + a0 * ez - N3 * hz
            loc = []
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        f = rng.uniform(0.55, 1.15)
                        loc.append(c + sx * hx * f * et + sy * hy * rng.uniform(0.6, 1.1) * T3 + sz * hz * rng.uniform(0.6, 1.2) * N3)
            dirv = N3 * 1.0 + er * 0.55 + rng.normal(0, 0.45, 3); dirv /= np.linalg.norm(dirv)
            dist = rng.uniform(0.6, 2.1); ax = rng.normal(0, 1, 3); ax /= np.linalg.norm(ax)
            Rm = np.array(Matrix.Rotation(rng.uniform(1.0, 5.0), 3, Vector(ax)))
            b0 = len(V)
            for p_ in loc: V.append(tuple(p_)); V2.append(tuple(c + dirv * dist + Rm @ (p_ - c)))
            for f_ in caras: Fc.append(tuple(b0 + q for q in f_))
    me = bpy.data.meshes.new(nombre); me.from_pydata(V, [], Fc); me.update(); me.materials.append(mat)
    o = bpy.data.objects.new(nombre, me)
    return o, V2
