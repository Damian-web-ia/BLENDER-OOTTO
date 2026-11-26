# Alex v2 - cara 2: retoques de las expresiones (se ejecuta una vez sobre alex_v2_rig.blend).
#  - La sonrisa ya no sube el parpado inferior (antes los ojos se cerraban al sonreir).
#  - "OjoAbierto" se nota de verdad (x2.5) para la sorpresa.
# Es idempotente: marca la malla con la propiedad "cara2".
import bpy
import numpy as np

OJO = {"R": np.array((-0.0475, 0, 1.604)), "L": np.array((0.025, 0, 1.609))}   # mundo, Alex en el origen


def _sm(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def retocar_cara(nombre="ALEX_v2_Malla", escala_ojo=2.5):
    ob = bpy.data.objects[nombre]; me = ob.data
    if me.get("cara2"):
        return {"hecho": "ya estaba"}
    n = len(me.vertices); kb = me.shape_keys.key_blocks
    mw = np.array(ob.matrix_world)
    B = np.zeros(n * 3); kb["Basis"].data.foreach_get("co", B); B = B.reshape(-1, 3)
    Wd = B @ mw[:3, :3].T + mw[:3, 3]
    delante = Wd[:, 1] < 0
    for L in ("R", "L"):
        o = OJO[L]
        d = np.sqrt(((Wd[:, 0] - o[0]) / 0.030) ** 2 + ((Wd[:, 2] - o[2]) / 0.016) ** 2)
        att = np.where(delante, _sm((d - 0.55) / 0.6), 1.0)
        for lado in ("R", "L"):
            k = kb["Sonrisa_" + lado]
            C = np.zeros(n * 3); k.data.foreach_get("co", C); D = C.reshape(-1, 3) - B
            D[:, 2] *= att
            k.data.foreach_set("co", (B + D).ravel())
    for L in ("R", "L"):
        k = kb["OjoAbierto_" + L]
        C = np.zeros(n * 3); k.data.foreach_get("co", C)
        k.data.foreach_set("co", (B + (C.reshape(-1, 3) - B) * escala_ojo).ravel())
    me["cara2"] = 1
    me.update()
    return {"hecho": "ok"}
