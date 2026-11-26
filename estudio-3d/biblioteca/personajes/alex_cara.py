# ALEX v2 · EXPRESIONES FACIALES (shape keys). Se ejecuta una vez sobre alex_v2_rig.blend.
# Puntos de referencia medidos en una vista ortográfica frontal (metros, mundo; Alex en el origen, 1,75 m):
import bpy, math
from mathutils import Vector

XC = -0.0125                                   # eje de la cara
OJO = {"R": Vector((-0.0475, 0, 1.604)), "L": Vector((0.025, 0, 1.609))}
CEJA = {"R": Vector((-0.050, 0, 1.620)), "L": Vector((0.022, 0, 1.626))}
CEJA_INT = {"R": Vector((-0.027, 0, 1.617)), "L": Vector((-0.002, 0, 1.623))}
COMISURA = {"R": Vector((-0.055, 0, 1.539)), "L": Vector((0.030, 0, 1.540))}
MEJILLA = {"R": Vector((-0.068, 0, 1.572)), "L": Vector((0.048, 0, 1.575))}
ZL = 1.5375                                    # línea de los labios

me = bpy.data.objects["ALEX_v2_Malla"]; mesh = me.data; mw = me.matrix_world
inv3 = mw.inverted().to_3x3()
W = [mw @ v.co for v in mesh.vertices]

def sm(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def peso_elipse(p, c, rx, rz, plano=0.35):
    """1 dentro del núcleo, cae suave hasta 0 en el borde. Solo la cara delantera."""
    if p.y > 0.0: return 0.0
    d = math.sqrt(((p.x - c.x) / rx) ** 2 + ((p.z - c.z) / rz) ** 2)
    return 1 - sm((d - plano) / (1 - plano))

if not mesh.shape_keys: me.shape_key_add(name="Basis", from_mix=False)
def key(nombre, fn):
    kb = mesh.shape_keys.key_blocks.get(nombre)
    if kb: me.shape_key_remove(kb)
    kb = me.shape_key_add(name=nombre, from_mix=False); kb.slider_min = -1.0; kb.slider_max = 1.0
    basis = mesh.shape_keys.key_blocks["Basis"]
    n = 0
    for i, p in enumerate(W):
        d = fn(p)
        if d is None or d.length < 1e-7: continue
        kb.data[i].co = basis.data[i].co + inv3 @ d; n += 1
    return n

stats = {}
for L in ("R", "L"):
    o = OJO[L]; c = CEJA[L]; ci = CEJA_INT[L]; s = -1 if L == "R" else 1
    # --- cejas
    def ceja_arriba(p, c=c, o=o):
        w = peso_elipse(p, c, 0.034, 0.020)
        wf = peso_elipse(p, c + Vector((0, 0, 0.022)), 0.040, 0.025) * 0.45      # frente acompaña
        wp = peso_elipse(p, o + Vector((0, 0, 0.004)), 0.020, 0.008) * 0.35      # párpado superior se abre
        return Vector((0, 0, 0.0065 * max(w, wf) + 0.002 * wp))
    stats["CejaArriba_" + L] = key("CejaArriba_" + L, ceja_arriba)
    def ceja_enfado(p, ci=ci, c=c, s=s):
        wi = peso_elipse(p, ci, 0.022, 0.016)
        wo = peso_elipse(p, c + Vector((s * 0.018, 0, 0)), 0.018, 0.014)
        return Vector((-s * 0.0035 * wi, 0.0015 * wi, -0.0060 * wi + 0.0015 * wo))
    stats["CejaEnfado_" + L] = key("CejaEnfado_" + L, ceja_enfado)
    def ceja_triste(p, ci=ci, c=c, s=s):
        wi = peso_elipse(p, ci, 0.022, 0.016)
        wo = peso_elipse(p, c + Vector((s * 0.018, 0, 0)), 0.018, 0.014)
        return Vector((-s * 0.001 * wi, 0, 0.0060 * wi - 0.0025 * wo))
    stats["CejaTriste_" + L] = key("CejaTriste_" + L, ceja_triste)
    # --- párpados
    def parpado(p, o=o):
        w = peso_elipse(p, o, 0.024, 0.016, plano=0.45)
        if w <= 0: return None
        zc = o.z - 0.0015
        f = 1.0 if p.z > zc else 0.30            # el superior baja casi todo; el inferior sube un poco
        return Vector((0, -0.0012 * w, (zc - p.z) * w * f * 0.97))
    stats["Parpado_" + L] = key("Parpado_" + L, parpado)
    def ojo_abierto(p, o=o):
        w = peso_elipse(p, o, 0.026, 0.020, plano=0.4)
        if w <= 0: return None
        return Vector((0, 0, (0.0035 if p.z > o.z else -0.0020) * w))
    stats["OjoAbierto_" + L] = key("OjoAbierto_" + L, ojo_abierto)
    # --- boca
    m = COMISURA[L]; mj = MEJILLA[L]
    def sonrisa(p, m=m, mj=mj, o=o, s=s):
        wc = peso_elipse(p, m, 0.028, 0.022)
        wm = peso_elipse(p, mj, 0.030, 0.026) * 0.7
        wo = peso_elipse(p, o + Vector((0, 0, -0.008)), 0.022, 0.008) * 0.5   # el párpado inferior sube
        return Vector((s * 0.0045 * wc, 0.0030 * wc - 0.0015 * wm, 0.0065 * wc + 0.0040 * wm + 0.0020 * wo))
    stats["Sonrisa_" + L] = key("Sonrisa_" + L, sonrisa)
    def triste(p, m=m, s=s):
        wc = peso_elipse(p, m, 0.026, 0.020)
        return Vector((-s * 0.0015 * wc, 0.0010 * wc, -0.0060 * wc))
    stats["BocaTriste_" + L] = key("BocaTriste_" + L, triste)

def boca_o(p):
    w = peso_elipse(p, Vector((XC, 0, ZL)), 0.060, 0.030, plano=0.25)
    return Vector((-(p.x - XC) * 0.38 * w, -0.0045 * w, -(p.z - ZL) * 0.10 * w))
stats["Boca_O"] = key("Boca_O", boca_o)
def boca_ancha(p):
    w = peso_elipse(p, Vector((XC, 0, ZL)), 0.060, 0.026, plano=0.3)
    return Vector(((p.x - XC) * 0.16 * w, 0.0020 * w, 0))
stats["Boca_Ancha"] = key("Boca_Ancha", boca_ancha)
def nariz(p):
    w = peso_elipse(p, Vector((XC + 0.004, 0, 1.567)), 0.030, 0.016)
    return Vector((0, 0.0005 * w, 0.0030 * w))
stats["Nariz_Arruga"] = key("Nariz_Arruga", nariz)

# el suavizado correctivo no debe tocar la cara (borraría las expresiones)
vg = me.vertex_groups.get("CS_cuerpo") or me.vertex_groups.new(name="CS_cuerpo")
vg.add(list(range(len(mesh.vertices))), 1.0, 'REPLACE')
for i, p in enumerate(W):
    w = 1 - sm((p.z - 1.43) / 0.04)
    vg.add([i], w, 'REPLACE')
cs = me.modifiers.get("Suavizado_correctivo")
if cs: cs.vertex_group = "CS_cuerpo"
result = stats
