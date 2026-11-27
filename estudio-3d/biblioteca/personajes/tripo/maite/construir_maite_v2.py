# MAITE v2 · se construye a partir del modelo de Tripo (maite_tripo.blend) · EKORUEDAS · 27-11-2026
# Damián (27-11): "animala bien porfavor" · "que quede el modelo 100% acabado, y que el pelo sea fluido,
# que la ropa se mueva mientras ella mueve sus manos, que tenga sombras".
# Uso: blender -b --factory-startup --python construir_maite_v2.py -- <carpeta_estudio> [salida.blend]
# Paso 1 (este archivo): TRENZA con cadena de huesos propia (Trenza_0..4) y sus pesos; texturas empaquetadas.
#   La trenza se reconoce por el color de la textura (pelo castaño) y por estar por debajo de la oreja izquierda.
# Los pasos siguientes (ojos 3D, párpados, cejas, boca) se añaden aquí mismo cuando estén probados.
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


trenza = preparar_trenza(ARM, ME)
ARM["trenza"] = ",".join(trenza)
ARM["maite_version"] = "v2-trenza"
bpy.ops.wm.save_as_mainfile(filepath=SALIDA, compress=True)
print("MAITE_V2_OK", SALIDA, flush=True)
