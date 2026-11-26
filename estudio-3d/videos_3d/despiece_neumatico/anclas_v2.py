# Posición en pantalla (0-1, y hacia arriba) de cada capa del despiece, fotograma a fotograma, sin mover la escena:
# se evalúan las curvas de animación de la cámara, de DESPIECE y de cada capa. Sirve para poner los rótulos en el montaje.
import bpy, json, math
from mathutils import Vector, Euler, Matrix
sc = bpy.context.scene; cam = sc.objects["CAM"]
def ev(idb, path, idx, f, por_defecto):
    ad = idb.animation_data
    if ad and ad.action:
        try: cv = list(ad.action.fcurves)
        except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
        for fc in cv:
            if fc.data_path == path and fc.array_index == idx: return fc.evaluate(f)
    return por_defecto
def trs(o, f):
    loc = Vector([ev(o, "location", i, f, o.location[i]) for i in range(3)])
    rot = Euler([ev(o, "rotation_euler", i, f, o.rotation_euler[i]) for i in range(3)], o.rotation_euler.order)
    return Matrix.Translation(loc) @ rot.to_matrix().to_4x4()
def proy(mc, lens, p):
    q = mc.inverted() @ p
    if q.z >= -1e-4: return None
    th = 12.0 / lens; tw = th * 9 / 16
    return [round(0.5 + (q.x / -q.z) / (2 * tw), 4), round(0.5 + (q.y / -q.z) / (2 * th), 4)]
DES = bpy.data.objects["DESPIECE"]
capas = {"alma": ["NR_G_alma"], "carcasa": ["NR_G_carc"], "talones": ["NR_G_tal"], "cinturones": ["NR_G_c1", "NR_G_c2"], "banda": ["NR_G_ext"]}
BORDE = {"alma": (0.0, 0.29), "carcasa": (0.0, 0.29), "talones": (0.0725, 0.2135), "cinturones": (0.0, 0.30), "banda": (0.0, 0.316)}
out = {}
for f in list(range(126, 608)) + list(range(636, 694)):
    mc = trs(cam, f); lens = ev(cam.data, "lens", 0, f, cam.data.lens)
    der = (mc.to_3x3() @ Vector((1, 0, 0))).normalized(); izq = -der
    md = trs(DES, f); d = {}
    for k, nombres in capas.items():
        zs = [ev(bpy.data.objects[n], "location", 2, f, 0.0) for n in nombres]
        c = md @ Vector((0, 0, sum(zs) / len(zs)))
        hz = Vector((mc.translation.x - c.x, mc.translation.y - c.y, 0))
        hz = hz.normalized() if hz.length > 1e-6 else Vector((0, -1, 0))
        dz, rb = BORDE[k]; fr = c + Vector((0, 0, dz)) + hz * rb
        d[k] = {"c": proy(mc, lens, c), "d": proy(mc, lens, c + der * 0.33), "i": proy(mc, lens, c + izq * 0.33), "f": proy(mc, lens, fr)}
    out[f] = d
# bulto
B = Vector(RESULT_BULTO)
for f in range(636, 694):
    mc = trs(cam, f); lens = ev(cam.data, "lens", 0, f, cam.data.lens); out[f]["bulto"] = proy(mc, lens, B)
json.dump(out, open(SALIDA, "w"))
