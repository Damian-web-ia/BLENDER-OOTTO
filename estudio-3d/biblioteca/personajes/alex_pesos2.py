# Alex v2 - pesos 2: hombros y trapecio sin pliegues.
# El auto-rig de Tripo deja cortes bruscos de peso entre Shoulder / Arm / Neck
# y algo de peso de la cabeza sobre los hombros. Al subir el brazo o girar la
# cabeza aparece un pico en la parte alta del hombro. Esto lo arregla:
#   1) quita el peso de Head por debajo del cuello y fuera del eje (pasa a Neck)
#   2) suaviza (laplaciano) los pesos de tronco-hombro-brazo en una zona acotada
#   3) mantiene la suma de pesos de cada vertice
# Uso dentro de Blender: exec(open(ruta).read()); arreglar_hombros()
import bpy
import numpy as np

GRUPOS = ["Spine1", "Spine2", "Neck", "Head", "RightShoulder", "LeftShoulder",
          "RightArm", "LeftArm"]


def _zona(co):
    """Peso 0..1 de la zona a suavizar (coordenadas locales de la malla, alto 0.979)."""
    x = np.abs(co[:, 0]); z = co[:, 2]
    fz = np.clip((z - 0.66) / 0.05, 0, 1) * np.clip((0.865 - z) / 0.03, 0, 1)
    fx = np.clip((x - 0.025) / 0.02, 0, 1) * np.clip((0.215 - x) / 0.03, 0, 1)
    return fz * fx


def arreglar_hombros(nombre="ALEX_v2_Malla", iteraciones=10, fuerza=0.5):
    ob = bpy.data.objects[nombre]
    me = ob.data
    n = len(me.vertices)
    co = np.zeros(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    E = np.zeros(len(me.edges) * 2, dtype=np.int64); me.edges.foreach_get("vertices", E)
    E = E.reshape(-1, 2)
    idx = {}
    for g in GRUPOS:
        vg = ob.vertex_groups.get("mixamorig:" + g)
        if vg: idx[g] = vg.index
    cols = list(idx.keys())
    W = np.zeros((n, len(cols)))
    gi = {idx[g]: k for k, g in enumerate(cols)}
    for v in me.vertices:
        for g in v.groups:
            k = gi.get(g.group)
            if k is not None: W[v.index, k] = g.weight
    total0 = W.sum(1)
    # 1) Head fuera del cuello -> Neck
    h, nk = cols.index("Head"), cols.index("Neck")
    fuera = (co[:, 2] < 0.83) & (np.abs(co[:, 0]) > 0.07)
    W[fuera, nk] += W[fuera, h]; W[fuera, h] = 0
    # 2) suavizado laplaciano con caida suave
    a = _zona(co) * fuerza
    act = a > 0
    deg = np.bincount(E.ravel(), minlength=n).astype(float)
    for _ in range(iteraciones):
        S = np.zeros_like(W)
        np.add.at(S, E[:, 0], W[E[:, 1]]); np.add.at(S, E[:, 1], W[E[:, 0]])
        M = S / np.maximum(deg, 1)[:, None]
        W = W + (M - W) * a[:, None]
    # 3) misma suma por vertice que antes
    s = W.sum(1)
    W = W * np.where(s > 1e-6, total0 / np.maximum(s, 1e-6), 0)[:, None]
    cambiados = 0
    for k, g in enumerate(cols):
        vg = ob.vertex_groups[idx[g]]
        for i in np.where(act | fuera)[0]:
            w = float(W[i, k])
            if w > 0.002:
                vg.add([int(i)], w, 'REPLACE')
            else:
                vg.remove([int(i)])
        cambiados += 1
    me.update()
    return {"vertices_zona": int(act.sum()), "head_quitado": int(fuera.sum()), "grupos": cambiados}


def quitar_picos(nombre="ALEX_v2_Malla", umbral=3.0, iteraciones=8):
    """Alisa los 'dientes' de la malla de Tripo en el trapecio (junto al cuello).
    Mueve la Basis y suma el mismo desplazamiento a todas las shape keys."""
    ob = bpy.data.objects[nombre]; me = ob.data; n = len(me.vertices)
    E = np.zeros(len(me.edges) * 2, dtype=np.int64); me.edges.foreach_get("vertices", E); E = E.reshape(-1, 2)
    deg = np.bincount(E.ravel(), minlength=n)[:, None].astype(float)
    def media(X):
        S = np.zeros_like(X); np.add.at(S, E[:, 0], X[E[:, 1]]); np.add.at(S, E[:, 1], X[E[:, 0]])
        return S / np.maximum(deg, 1)
    kbs = me.shape_keys.key_blocks if me.shape_keys else None
    B = np.zeros(n * 3)
    (kbs["Basis"].data if kbs else me.vertices).foreach_get("co", B); B = B.reshape(-1, 3)
    L = np.linalg.norm(B - media(B), axis=1)
    zona = (B[:, 2] > 0.75) & (B[:, 2] < 0.835) & (np.abs(B[:, 0]) > 0.05) & (np.abs(B[:, 0]) < 0.20)
    pico = zona & (L > umbral * np.median(L[zona]))
    vecino = media(pico.astype(float)[:, None])[:, 0] > 0
    w = np.where(pico, 0.6, np.where(vecino & zona, 0.25, 0.0))
    X = B.copy()
    for _ in range(iteraciones):
        X = X + (media(X) - X) * w[:, None]
    D = X - B
    if kbs:
        for kb in kbs:
            C = np.zeros(n * 3); kb.data.foreach_get("co", C)
            kb.data.foreach_set("co", (C.reshape(-1, 3) + D).ravel())
    V = np.zeros(n * 3); me.vertices.foreach_get("co", V)
    me.vertices.foreach_set("co", (V.reshape(-1, 3) + D).ravel())
    me.update()
    return {"picos": int(pico.sum()), "movidos": int((w > 0).sum()),
            "max_mm": round(float(np.linalg.norm(D, axis=1).max()) * ob.matrix_world.to_scale()[0] * 1000, 1)}
