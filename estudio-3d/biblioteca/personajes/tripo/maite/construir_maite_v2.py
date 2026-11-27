# MAITE v2 · se construye a partir del modelo de Tripo (maite_tripo.blend) · EKORUEDAS · 27-11-2026
# Damián (27-11): "animala bien porfavor" · "que quede el modelo 100% acabado, y que el pelo sea fluido,
# que la ropa se mueva mientras ella mueve sus manos, que tenga sombras".
# Uso: blender -b --factory-startup --python construir_maite_v2.py -- <carpeta_estudio> [salida.blend]
# Fase 1 (AAA): malla limpia (soldar, tapar agujeros), un MATERIAL POR TEJIDO (piel, pelo, camiseta, mono, puños,
#   guantes, botas, funda, ojos/dientes) reconocido por el color de la textura y la zona del cuerpo, y una subdivisión
#   Catmull-Clark aplicada (malla 4 veces más densa para deformar bien; la textura no se toca).
# Trenza: cadena de huesos propia (Trenza_0..4) y sus pesos (se reconoce por el color castaño bajo la oreja izquierda).
# Los pasos siguientes (ojos 3D, párpados, boca, shape keys ARKit) se añaden aquí mismo cuando estén probados.
import bpy, os, sys, math
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
EST = argv[0] if argv else r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite")
SALIDA = argv[1] if len(argv) > 1 else os.path.join(PM, "maite_v2.blend")

bpy.ops.wm.open_mainfile(filepath=os.path.join(PM, "maite_tripo.blend"))
ARM = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
ME = [o for o in bpy.data.objects if o.type == 'MESH'][0]
ARM.name = "MAITE_rig"; ME.name = "MAITE_cuerpo"
for img in bpy.data.images:                       # texturas dentro del .blend (así se mueve sin perderlas)
    if img.source == 'FILE' and not img.packed_file:
        n = os.path.basename(bpy.path.abspath(img.filepath))
        for r_, _d, fs in os.walk(PM):
            if n in fs:
                img.filepath = os.path.join(r_, n); break
        try: img.reload(); img.pack()
        except Exception as e: print("IMG", img.name, e)


def colores_vertice(me):
    """Color medio de la textura base en cada vértice (media de sus esquinas UV)."""
    m = me.data
    img = max((n.image for mt in m.materials for n in mt.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image
               and n.image.colorspace_settings.name == 'sRGB'), key=lambda i: i.size[0] * i.size[1])
    w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    uvl = m.uv_layers.active.data
    luv = np.empty(len(uvl) * 2, np.float32); uvl.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    lv = np.empty(len(m.loops), np.int32); m.loops.foreach_get('vertex_index', lv)
    nv = len(m.vertices)
    cl = px[np.clip((luv[:, 1] * h).astype(int), 0, h - 1), np.clip((luv[:, 0] * w).astype(int), 0, w - 1), :3]
    acc = np.zeros((nv, 3)); cnt = np.zeros(nv); np.add.at(acc, lv, cl); np.add.at(cnt, lv, 1)
    return acc / np.maximum(cnt, 1)[:, None]


def coords(me):
    m = me.data; co = np.empty(len(m.vertices) * 3, np.float32); m.vertices.foreach_get('co', co)
    return co.reshape(-1, 3)


def aristas(me):
    m = me.data; e = np.empty(len(m.edges) * 2, np.int32); m.edges.foreach_get('vertices', e); return e.reshape(-1, 2)


def componentes(mask, E):
    par = np.arange(len(mask))
    def raiz(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for a, b in E[mask[E[:, 0]] & mask[E[:, 1]]]:
        ra, rb = raiz(a), raiz(b)
        if ra != rb: par[ra] = rb
    idx = np.where(mask)[0]; rs = np.array([raiz(i) for i in idx])
    return idx, rs


# ------------------------------------------------------------------ FASE 1 · LIMPIEZA
import bmesh, colorsys
from collections import Counter
def limpiar(me):
    bm = bmesh.new(); bm.from_mesh(me.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bordes = [e for e in bm.edges if e.is_boundary]
    if bordes: bmesh.ops.holes_fill(bm, edges=bordes, sides=16)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    bm.normal_update(); bm.to_mesh(me.data); bm.free(); me.data.update()
    bm = bmesh.new(); bm.from_mesh(me.data)
    info = (sum(1 for e in bm.edges if e.is_boundary), sum(1 for e in bm.edges if not e.is_manifold)); bm.free()
    print("LIMPIEZA bordes/no-manifold:", info, flush=True)

# ------------------------------------------------------------------ FASE 1 · TEJIDOS
def clasificar(me):
    m = me.data
    img = max((n.image for mt in m.materials for n in mt.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image
               and n.image.colorspace_settings.name == 'sRGB'), key=lambda i: i.size[0] * i.size[1])
    w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    uvl = m.uv_layers.active.data
    luv = np.empty(len(uvl) * 2, np.float32); uvl.foreach_get('uv', luv); luv = luv.reshape(-1, 2)
    nf = len(m.polygons)
    lt = np.empty(nf, np.int32); m.polygons.foreach_get('loop_total', lt)
    lf = np.repeat(np.arange(nf), lt)
    fuv = np.zeros((nf, 2)); np.add.at(fuv, lf, luv); fuv /= lt[:, None]
    samp = np.r_[luv * 0.5 + fuv[lf] * 0.5, fuv]; sf = np.r_[lf, np.arange(nf)]
    cs = px[np.clip((samp[:, 1] * h).astype(int), 0, h - 1), np.clip((samp[:, 0] * w).astype(int), 0, w - 1), :3]
    fc = np.zeros((nf, 3)); cnt = np.zeros(nf); np.add.at(fc, sf, cs); np.add.at(cnt, sf, 1); fc /= cnt[:, None]
    cen = np.empty(nf * 3, np.float32); m.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    hsv = np.array([colorsys.rgb_to_hsv(*c) for c in fc]); H, S, V = hsv.T; r, g, b = fc.T
    x, y, z = cen.T
    cls = np.full(nf, 'otro', dtype=object)
    azul = (b > r + 0.05) & (b > g) & (S > 0.25)
    claro = (V > 0.48) & (S < 0.24)
    piel = (H < 0.12) & (S > 0.25) & (V > 0.55)
    oscuro = (V < 0.55) & ~azul & ~claro
    cls[azul] = 'mono'
    cls[claro & (z > 0.55)] = 'camiseta'
    cls[(z < 0.17) & (V > 0.3) & (S < 0.3) & (b >= r - 0.02)] = 'punos'
    cls[piel] = 'piel'
    cara = (z > 0.80) & (y < -0.02)
    cls[cara & claro] = 'ojos_dientes'
    cls[oscuro & (z > 0.6) & (np.abs(x) < 0.2)] = 'pelo'
    cls[oscuro & (np.abs(x) > 0.22)] = 'guantes'
    cls[oscuro & (z < 0.13)] = 'botas'
    cls[oscuro & (x < -0.09) & (z > 0.38) & (z < 0.6)] = 'funda'
    frente = (y < -0.035) & (z > 0.855) & (z < 0.915) & (np.abs(x - 0.02) < 0.075)   # cejas, pestañas y pupilas pintadas
    cls[frente & (cls == 'pelo')] = 'piel'
    ek = {}
    for p in m.polygons:
        for k in p.edge_keys: ek.setdefault(k, []).append(p.index)
    vec = [[] for _ in range(nf)]
    for fs in ek.values():
        for a_ in fs:
            for c_ in fs:
                if a_ != c_: vec[a_].append(c_)
    for _ in range(6):
        nuevo = cls.copy()
        for i in range(nf):
            if not vec[i]: continue
            cc = Counter(cls[j] for j in vec[i] if cls[j] != 'otro')
            if not cc: continue
            top, nt = cc.most_common(1)[0]
            if cls[i] == 'otro' or (nt >= len(vec[i]) - 1 and top != cls[i] and nt >= 3 and cls[i] != 'ojos_dientes'):
                nuevo[i] = top
        cls = nuevo
    print("TEJIDOS", dict(Counter(cls.tolist())), flush=True)
    return cls

TEJIDOS = {   # rugosidad (mín, máx), subsurface, sheen, coat, relieve fino (fuerza, escala, tipo), retoque de color (tono, sat, valor)
    "piel":        dict(rug=(0.42, 0.58), sss=0.22, sheen=0.15, coat=0.04, rel=(0.08, 900, "poros"), hsv=(0.5, 1.03, 1.0)),
    "pelo":        dict(rug=(0.48, 0.66), sss=0.0, sheen=0.10, coat=0.05, rel=(0.05, 260, "mechas"), hsv=(0.5, 1.03, 1.0)),
    "camiseta":    dict(rug=(0.86, 0.95), sss=0.06, sheen=0.25, coat=0.0, rel=(0.12, 1400, "algodon"), hsv=(0.5, 1.0, 1.0)),
    "mono":        dict(rug=(0.80, 0.92), sss=0.0, sheen=0.08, coat=0.0, rel=(0.10, 700, "sarga"), hsv=(0.5, 1.0, 1.0)),
    "punos":       dict(rug=(0.80, 0.92), sss=0.0, sheen=0.08, coat=0.0, rel=(0.10, 700, "sarga"), hsv=(0.5, 1.0, 1.0)),
    "guantes":     dict(rug=(0.55, 0.70), sss=0.0, sheen=0.10, coat=0.08, rel=(0.20, 600, "cuero"), hsv=(0.5, 1.0, 1.0)),
    "botas":       dict(rug=(0.42, 0.62), sss=0.0, sheen=0.0, coat=0.22, rel=(0.25, 500, "cuero"), hsv=(0.5, 1.0, 1.0)),
    "funda":       dict(rug=(0.45, 0.62), sss=0.0, sheen=0.0, coat=0.18, rel=(0.22, 500, "cuero"), hsv=(0.5, 1.0, 1.0)),
    "ojos_dientes": dict(rug=(0.12, 0.25), sss=0.05, sheen=0.0, coat=0.6, rel=(0.0, 100, "poros"), hsv=(0.5, 1.0, 1.0)),
}
def materiales(me, cls, dims):
    m = me.data
    viejo = m.materials[0]
    imgs = {n.image.name: n.image for n in viejo.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image}
    def img(sub):
        for k, v in imgs.items():
            if sub in k.lower(): return v
    i_col = max((v for v in imgs.values() if v.colorspace_settings.name == 'sRGB'), key=lambda i: i.size[0])
    i_nor = [v for v in imgs.values() if v is not i_col and 'rough' not in v.name.lower() and 'metal' not in v.name.lower()][0]
    i_rug = img('rough'); i_met = img('metal')
    m.materials.clear(); idx = {}
    for nombre, P in TEJIDOS.items():
        mt = bpy.data.materials.new("MAITE_" + nombre); mt.use_nodes = True
        nt = mt.node_tree; N = nt.nodes; Lk = nt.links
        bs = N["Principled BSDF"]; bs.location = (300, 0)
        uv = N.new("ShaderNodeUVMap"); uv.uv_map = m.uv_layers.active.name; uv.location = (-1200, 0)
        def tex(im, y, col='sRGB'):
            t = N.new("ShaderNodeTexImage"); t.image = im; t.location = (-900, y); t.interpolation = 'Linear'
            Lk.new(uv.outputs["UV"], t.inputs["Vector"]); return t
        tc = tex(i_col, 300)
        hs = N.new("ShaderNodeHueSaturation"); hs.location = (-500, 300)
        hs.inputs["Hue"].default_value, hs.inputs["Saturation"].default_value, hs.inputs["Value"].default_value = P["hsv"]
        Lk.new(tc.outputs["Color"], hs.inputs["Color"]); Lk.new(hs.outputs["Color"], bs.inputs["Base Color"])
        if i_rug:
            tr = tex(i_rug, 0); mr = N.new("ShaderNodeMapRange"); mr.location = (-500, 0)
            mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = P["rug"]
            Lk.new(tr.outputs["Color"], mr.inputs["Value"]); Lk.new(mr.outputs["Result"], bs.inputs["Roughness"])
        else:
            bs.inputs["Roughness"].default_value = sum(P["rug"]) / 2
        bs.inputs["Metallic"].default_value = 0.0
        tn = tex(i_nor, -300); nm = N.new("ShaderNodeNormalMap"); nm.location = (-500, -300); nm.uv_map = uv.uv_map
        nm.inputs["Strength"].default_value = 1.0
        Lk.new(tn.outputs["Color"], nm.inputs["Color"])
        # relieve fino procedural sobre coordenadas de reposo (no "nada" al animar)
        fu, esc, tipo = P["rel"]
        if fu > 0:
            co = N.new("ShaderNodeTexCoord"); co.location = (-1400, -600)
            vm = N.new("ShaderNodeVectorMath"); vm.operation = 'MULTIPLY'; vm.location = (-1200, -600)
            vm.inputs[1].default_value = dims; Lk.new(co.outputs["Generated"], vm.inputs[0])
            if tipo == "sarga":          # tela vaquera: diagonales finas
                t3 = N.new("ShaderNodeTexWave"); t3.wave_type = 'BANDS'; t3.bands_direction = 'DIAGONAL'
                t3.inputs["Scale"].default_value = esc; t3.inputs["Distortion"].default_value = 2.0
                t3.inputs["Detail"].default_value = 3.0; out = t3.outputs["Fac"]
            elif tipo == "mechas":       # pelo: vetas a lo largo del mechón
                t3 = N.new("ShaderNodeTexWave"); t3.wave_type = 'BANDS'; t3.bands_direction = 'Z'
                t3.inputs["Scale"].default_value = esc; t3.inputs["Distortion"].default_value = 6.0
                t3.inputs["Detail"].default_value = 4.0; out = t3.outputs["Fac"]
            else:                        # poros, algodón, cuero: ruido fino
                t3 = N.new("ShaderNodeTexNoise"); t3.inputs["Scale"].default_value = esc
                t3.inputs["Detail"].default_value = 6.0; t3.inputs["Roughness"].default_value = 0.6; out = t3.outputs["Fac"]
            t3.location = (-900, -650); Lk.new(vm.outputs["Vector"], t3.inputs["Vector"])
            bu = N.new("ShaderNodeBump"); bu.location = (-300, -450)
            bu.inputs["Strength"].default_value = fu; bu.inputs["Distance"].default_value = 0.0004
            Lk.new(out, bu.inputs["Height"]); Lk.new(nm.outputs["Normal"], bu.inputs["Normal"])
            Lk.new(bu.outputs["Normal"], bs.inputs["Normal"])
        else:
            Lk.new(nm.outputs["Normal"], bs.inputs["Normal"])
        if P["sss"] > 0:
            bs.inputs["Subsurface Weight"].default_value = P["sss"]
            bs.inputs["Subsurface Radius"].default_value = (1.0, 0.42, 0.25)
            bs.inputs["Subsurface Scale"].default_value = 0.004
        bs.inputs["Sheen Weight"].default_value = P["sheen"]
        bs.inputs["Coat Weight"].default_value = P["coat"]; bs.inputs["Coat Roughness"].default_value = 0.25
        m.materials.append(mt); idx[nombre] = len(m.materials) - 1
    mi = np.array([idx.get(c, idx["piel"]) for c in cls], np.int32); m.polygons.foreach_set('material_index', mi)
    print("MATERIALES", list(idx), flush=True)

def subdividir(me, niveles=1):
    bpy.context.view_layer.objects.active = me; me.select_set(True)
    md = me.modifiers.new("Sub_base", 'SUBSURF'); md.levels = niveles; md.render_levels = niveles
    md.uv_smooth = 'PRESERVE_BOUNDARIES'; md.boundary_smooth = 'ALL'; md.quality = 3
    while me.modifiers[0] != md: bpy.ops.object.modifier_move_up(modifier=md.name)
    bpy.ops.object.modifier_apply(modifier=md.name)
    r = me.modifiers.new("Sub_render", 'SUBSURF'); r.levels = 0; r.render_levels = 1; r.uv_smooth = 'PRESERVE_BOUNDARIES'
    print("SUBDIVIDIDA", len(me.data.vertices), "vértices", flush=True)

# ------------------------------------------------------------------ TRENZA
N_TRENZA = 5
def preparar_trenza(arm, me, n=N_TRENZA):
    co = coords(me); col = colores_vertice(me); E = aristas(me)
    r, g, b = col.T
    pelo = (r > 0.06) & (r < 0.42) & (r > b * 1.05) & (g < 0.30) & (b < 0.30)
    head = arm.data.bones["mixamorig:Head"].head_local
    z_oreja = head.z - 0.005
    zona = (co[:, 2] < z_oreja) & (co[:, 2] > head.z - 0.25) & (co[:, 0] > 0.03) & (np.abs(co[:, 1]) < 0.12)
    idx, rs = componentes(pelo & zona, E)
    u, c = np.unique(rs, return_counts=True)
    trenza = np.zeros(len(co), bool); trenza[idx[rs == u[np.argmax(c)]]] = True
    # un anillo más de vértices de borde (mezcla de color) que no sean piel, camiseta ni peto
    piel = (r > 0.6) & (g > 0.3); claro = (r > 0.6) & (g > 0.6); azul = (b > r)
    for _ in range(2):
        vec = np.zeros(len(co), bool)
        m_ = trenza[E[:, 0]] & ~trenza[E[:, 1]]; vec[E[m_, 1]] = True
        m_ = trenza[E[:, 1]] & ~trenza[E[:, 0]]; vec[E[m_, 0]] = True
        trenza |= vec & zona & ~piel & ~claro & ~azul
    P = co[trenza]; ids = np.where(trenza)[0]
    z0, z1 = P[:, 2].max(), P[:, 2].min()
    # línea central por rodajas de altura
    cen = []
    for s in range(n + 1):
        z = z0 - (z0 - z1) * s / n; tol = (z0 - z1) / (2 * n) + 1e-4
        ban = P[np.abs(P[:, 2] - z) <= tol]
        if len(ban) < 6: ban = P[np.argsort(np.abs(P[:, 2] - z))[:12]]
        c_ = ban.mean(0); cen.append(Vector((float(c_[0]), float(c_[1]), float(z))))
    bpy.context.view_layer.objects.active = arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); eb = arm.data.edit_bones
    padre = eb["mixamorig:Head"]; nombres = []
    for s in range(n):
        nb = eb.new(f"Trenza_{s}"); nb.head = cen[s]; nb.tail = cen[s + 1]; nb.parent = padre
        nb.use_connect = s > 0; nb.roll = 0; nb.use_deform = True; padre = nb; nombres.append(nb.name)
    bpy.ops.object.mode_set(mode='OBJECT')
    # pesos: la trenza deja de seguir al hombro y pasa a su cadena; arriba se funde con la cabeza
    for nm in nombres + ["mixamorig:Head"]:
        if nm not in me.vertex_groups: me.vertex_groups.new(name=nm)
    grupos = {g.index: g for g in me.vertex_groups}
    mv = me.data.vertices
    for i in ids:
        for ge in list(mv[i].groups):
            grupos[ge.group].remove([int(i)])
    tr = 0.18                                        # tramo de fusión con la cabeza (fracción de la trenza)
    for i in ids:
        t = float((z0 - co[i, 2]) / max(1e-6, z0 - z1)); x = min(0.999, t) * n; s = int(x); fr = x - s
        mez = min(1.0, t / tr); mez = mez * mez * (3 - 2 * mez)
        w = {nombres[s]: (1 - fr) * mez, "mixamorig:Head": 1 - mez}
        if s + 1 < n: w[nombres[s + 1]] = fr * mez
        else: w[nombres[s]] = mez
        for nm, val in w.items():
            if val > 1e-3: me.vertex_groups[nm].add([int(i)], float(val), 'REPLACE')
    for nm in nombres:
        arm.pose.bones[nm].rotation_mode = 'QUATERNION'
    print("TRENZA", len(ids), "vértices", [tuple(round(v, 3) for v in c_) for c_ in cen], flush=True)
    return nombres


limpiar(ME)
DIMS = tuple(ME.dimensions)
CLS = clasificar(ME)
materiales(ME, CLS, DIMS)
subdividir(ME, 1)
trenza = preparar_trenza(ARM, ME)
ARM["trenza"] = ",".join(trenza)
ARM["maite_version"] = "v2-fase1"
bpy.ops.wm.save_as_mainfile(filepath=SALIDA, compress=True)
print("MAITE_V2_OK", SALIDA, flush=True)
