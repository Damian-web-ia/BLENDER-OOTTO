# DESPIECE 3D DEL NEUMÁTICO · v2 REALISTA (26-11-2026) · vídeo vertical 9:16, 30 fps, ~28,4 s
# Cambios pedidos por Damián: piezas de verdad (hilos, cables, alambres, dibujo, marcado), sin cambios de color,
# estilo del vídeo de la caja de cambios (piezas con detalle, planos macro con desenfoque); Clod NO habla: hace gestos de fondo.
# Voces (Alex = "Carlos"): GANCHO 0,25 s · CAPAS 4,25 s · CONSEJO 20,15 s · SÍGUENOS 25,05 s
import bpy, math, bmesh, json
import numpy as np
from mathutils import Vector, Matrix, Euler, Quaternion
BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
D_ = BASE + r"\biblioteca"
TALLER = D_ + r"\taller_v2.py"; ANIM = D_ + r"\personajes\alex_anim.py"; ANIM_C = D_ + r"\personajes\clod_anim.py"
MODELO_C = D_ + r"\personajes\clod_v2.py"; CLOD_BLEND = D_ + r"\personajes\clod\clod_v2.blend"
sc = bpy.context.scene
R = math.radians
def F(t): return int(round(t * 30)) + 1
FIN = 851

# ---------------------------------------------------------------- taller, personajes y funciones
T_ = {"__name__": "taller"}; exec(open(TALLER, encoding="utf-8").read(), T_)
TT = T_["construir_taller"](); M = TT["M"]; COL = TT["col"]; T_["ajustes_render"](sc)
if "CLOD_v2" not in bpy.data.objects:
    with bpy.data.libraries.load(CLOD_BLEND, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c in ("CLOD_v2_personaje", "CLOD_v2_controles")]
    for c in dst.collections:
        if c.name not in sc.collection.children: sc.collection.children.link(c)
exec(open(ANIM, encoding="utf-8").read())
exec(open(ANIM_C, encoding="utf-8").read())
_m = {"__name__": "modelo"}; exec(open(MODELO_C, encoding="utf-8").read(), _m)
for n in ("Ciclorama",):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
caja, cilindro, mat, _obj = T_["caja"], T_["cilindro"], T_["mat"], T_["_obj"]
R_EXT, R_LL, ANCHO = T_["R_EXT"], T_["R_LLANTA"], T_["ANCHO"]

def col_nueva(n):
    c = bpy.data.collections.get(n)
    if c is None: c = bpy.data.collections.new(n); sc.collection.children.link(c)
    return c
CC = col_nueva("COCHE"); CD = col_nueva("DESPIECE")

# ---------------------------------------------------------------- rayos X: materiales que se vuelven transparentes con aristas azules
sc["xray"] = 0.0
def xray(m):
    if m.get("xray"): return m
    nt = m.node_tree; out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    src = out.inputs["Surface"].links[0].from_socket
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'VIEW_LAYER'; at.attribute_name = "xray"
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.25
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 1.6
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.12, 0.55, 1.0, 1); em.inputs["Strength"].default_value = 4.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    m1 = nt.nodes.new("ShaderNodeMixShader"); m2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], pw.inputs[0]); nt.links.new(pw.outputs[0], m1.inputs[0])
    nt.links.new(tr.outputs[0], m1.inputs[1]); nt.links.new(em.outputs[0], m1.inputs[2])
    nt.links.new(at.outputs["Fac"], m2.inputs[0]); nt.links.new(src, m2.inputs[1]); nt.links.new(m1.outputs[0], m2.inputs[2])
    nt.links.new(m2.outputs[0], out.inputs["Surface"])
    for a, v in (("surface_render_method", 'DITHERED'), ("use_transparent_shadow", True), ("blend_method", 'HASHED')):
        try: setattr(m, a, v)
        except Exception: pass
    m["xray"] = 1
    return m
def copia(m, nombre):
    c = bpy.data.materials.get(nombre)
    if c: return c
    c = m.copy(); c.name = nombre; return c

# ---------------------------------------------------------------- COCHE (compacto estilizado, morro hacia -X)
L_C, W_C = 4.05, 0.88
def interp(tab, u):
    xs = [p[0] for p in tab]; ys = [p[1] for p in tab]
    return float(np.interp(u, xs, ys))
BELT = [(-2.03, 0.58), (-1.85, 0.70), (-1.3, 0.80), (-0.70, 0.88), (0.0, 0.92), (1.5, 0.96), (1.95, 0.92), (2.03, 0.82)]
TOP = [(-2.03, 0.60), (-1.85, 0.72), (-1.3, 0.82), (-0.78, 0.905), (-0.10, 1.40), (0.30, 1.44), (1.15, 1.43), (1.70, 1.17), (1.93, 0.99), (2.03, 0.84)]
def z_bot(u): return 0.24 + 0.07 * max(0.0, (abs(u) - 1.6) / 0.43) ** 2
def ancho(u, W):
    t = min(1.0, abs(u) / (L_C / 2 + 0.005)); return max(0.035, W * (1 - t ** 4.5) ** (1 / 4.5))
def seccion(u):
    w = ancho(u, W_C); zb = z_bot(u); ze = interp(BELT, u); zt = max(interp(TOP, u), ze + 0.02)
    cab = min(1.0, max(0.0, (zt - ze - 0.03) / 0.30))
    wc = w * (0.90 + (0.74 - 0.90) * cab)
    H = [(0.0, zb), (0.55 * w, zb), (0.92 * w, zb + 0.02), (w, zb + 0.12), (w, zb + 0.30 * (ze - zb)),
         (w, zb + 0.70 * (ze - zb)), (0.985 * w, ze - 0.03), (0.95 * w, ze), (0.95 * w + (wc - 0.95 * w) * 0.15, ze + 0.03),
         (0.95 * w + (wc - 0.95 * w) * 0.55, ze + 0.5 * (zt - ze)), (wc, zt - 0.04), (0.72 * wc, zt), (0.0, zt + 0.01)]
    return H, ze, zt, cab
def malla_coche():
    me = bpy.data.meshes.get("COCHE_Carroceria")
    if me: return me
    n = 72; us = [-L_C / 2 * math.cos(math.pi * i / (n - 1)) for i in range(n)]
    V = []; info = []
    for u in us:
        H, ze, zt, cab = seccion(u)
        loop = H + [(-y, z) for (y, z) in reversed(H[1:-1])]
        for (y, z) in loop: V.append((u, y, z))
        info.append((ze, zt, cab))
    K = 24; Fc = []
    for i in range(n - 1):
        for k in range(K):
            k2 = (k + 1) % K
            Fc.append((i * K + k, i * K + k2, (i + 1) * K + k2, (i + 1) * K + k))
    Fc.append(tuple(reversed(range(K)))); Fc.append(tuple((n - 1) * K + k for k in range(K)))
    me = bpy.data.meshes.new("COCHE_Carroceria"); me.from_pydata(V, [], Fc); me.update()
    # materiales: 0 pintura, 1 cristal, 2 plástico negro
    for p in me.polygons:
        c = p.center; u = c.x; ze = interp(BELT, u); zt = max(interp(TOP, u), ze + 0.02)
        cab = (zt - ze) > 0.2; idx = 0
        if c.z < z_bot(u) + 0.075: idx = 2
        elif cab and ze + 0.04 < c.z < zt - 0.03 and abs(c.y) > 0.45:
            idx = 1
            if abs(u - 0.47) < 0.055 or u < -0.62 or u > 1.58: idx = 0       # pilares B, A y C
        elif cab and c.z > ze + 0.06 and (-0.70 < u < -0.16 or 1.22 < u < 1.85) and abs(c.y) < 0.62:
            idx = 1                                                         # parabrisas y luna trasera
        p.material_index = idx; p.use_smooth = True
    me.update()
    return me
PINTURA = mat("COCHE_Pintura", (0.015, 0.20, 0.27), rough=0.18, metal=0.55, coat=1.0)
CRISTAL = mat("COCHE_Cristal", (0.008, 0.010, 0.014), rough=0.04, coat=1.0, spec=0.6)
NEGRO_C = mat("COCHE_Plastico", (0.02, 0.02, 0.022), rough=0.55)
FARO = mat("COCHE_Faro", (0.9, 0.95, 1.0), rough=0.1, emis=4.0, ecol=(1.0, 0.97, 0.9))
PILOTO = mat("COCHE_Piloto", (0.5, 0.01, 0.01), rough=0.2, emis=3.0, ecol=(1.0, 0.05, 0.02))
GOMA_C = copia(M["goma"], "COCHE_Goma"); LLANTA_C = copia(M["llanta"], "COCHE_Llanta"); LLOSC_C = copia(M["llanta_osc"], "COCHE_LlantaOsc")
for m_ in (PINTURA, CRISTAL, NEGRO_C, FARO, PILOTO, GOMA_C, LLANTA_C, LLOSC_C): xray(m_)

CAR = bpy.data.objects.get("COCHE")
if CAR is None:
    CAR = bpy.data.objects.new("COCHE", None); CC.objects.link(CAR)
CAR.location = (0.0, 0.8, 0.0)
me_c = malla_coche()
for m_ in (PINTURA, CRISTAL, NEGRO_C):
    if m_.name not in [x.name for x in me_c.materials if x]: me_c.materials.append(m_)
car_body = bpy.data.objects.get("COCHE_Carroceria") or _obj("COCHE_Carroceria", me_c, None, CC, padre=CAR)
car_body.parent = CAR
if not car_body.modifiers:
    ss = car_body.modifiers.new("Liso", "SUBSURF"); ss.levels = 2; ss.render_levels = 2
X_DEL, X_TRAS, Y_RUEDA, Z_RUEDA = -1.27, 1.28, 0.76, R_EXT
for i, x in enumerate((X_DEL, X_TRAS)):
    nm = f"COCHE_Paso{i}"
    cy = bpy.data.objects.get(nm) or cilindro(nm, (x, 0, Z_RUEDA), 0.372, 2.4, NEGRO_C, seg=64, col=CC, padre=CAR, rot=(R(90), 0, 0))
    cy.hide_render = True; cy.display_type = 'WIRE'; cy.hide_set(True)
    if nm not in [md.name for md in car_body.modifiers]:
        b = car_body.modifiers.new(nm, "BOOLEAN"); b.object = cy; b.solver = 'EXACT'
    for s in (-1, 1):                                   # guardabarros interior (tubo negro)
        nt_ = f"COCHE_Aleta{i}{s}"
        if nt_ not in bpy.data.objects:
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=64, radius1=0.366, radius2=0.366, depth=0.40)
            me = bpy.data.meshes.new(nt_); bm.to_mesh(me); bm.free()
            o = _obj(nt_, me, NEGRO_C, CC, padre=CAR, loc=(x, s * (W_C - 0.21), Z_RUEDA)); o.rotation_euler = (R(90), 0, 0)
# faros, pilotos, calandra, retrovisores
def _lente(nombre, loc, esc, m):
    if nombre in bpy.data.objects: return
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * esc[0], v.co.y * esc[1], v.co.z * esc[2]))
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free(); _obj(nombre, me, m, CC, padre=CAR, loc=loc)
for s in (-1, 1):
    _lente(f"COCHE_Faro{s}", (-1.96, s * 0.58, 0.66), (0.07, 0.17, 0.065), FARO)
    _lente(f"COCHE_Piloto{s}", (1.985, s * 0.64, 0.86), (0.04, 0.15, 0.05), PILOTO)
    if f"COCHE_Espejo{s}" not in bpy.data.objects:
        caja(f"COCHE_Espejo{s}", (-0.62, s * 0.95, 1.00), (0.10, 0.14, 0.09), PINTURA, bisel=0.02, col=CC, padre=CAR)
if "COCHE_Calandra" not in bpy.data.objects:
    caja("COCHE_Calandra", (-2.005, 0, 0.47), (0.06, 0.82, 0.16), NEGRO_C, bisel=0.03, col=CC, padre=CAR)
# por dentro (solo se ve con rayos X): motor, caja, amortiguador con muelle, disco y pinza de freno
ACERO = M["acero"]; ROJO = M["rojo"]
if "COCHE_Motor" not in bpy.data.objects:
    caja("COCHE_Motor", (-1.30, 0.0, 0.57), (0.55, 0.62, 0.34), M["gris_maq"], bisel=0.03, col=CC, padre=CAR)
    for k in range(4):
        cilindro(f"COCHE_MotorTapa{k}", (-1.30, -0.21 + k * 0.14, 0.76), 0.05, 0.04, ACERO, col=CC, padre=CAR)
    caja("COCHE_Caja", (-0.85, 0.05, 0.50), (0.35, 0.40, 0.32), ACERO, bisel=0.03, col=CC, padre=CAR)
    for s in (-1, 1):
        dsc = cilindro(f"COCHE_Disco{s}", (X_DEL, s * 0.60, Z_RUEDA), 0.15, 0.024, ACERO, seg=64, col=CC, padre=CAR, rot=(R(90), 0, 0))
        for pp in dsc.data.polygons: pp.use_smooth = len(pp.vertices) == 4
        caja(f"COCHE_Pinza{s}", (X_DEL + 0.10, s * 0.585, Z_RUEDA + 0.11), (0.09, 0.07, 0.12), ROJO, bisel=0.012, col=CC, padre=CAR)
        cilindro(f"COCHE_Amort{s}", (X_DEL, s * 0.40, 0.62), 0.025, 0.34, ACERO, col=CC, padre=CAR)
        cu = bpy.data.curves.new(f"COCHE_Muelle{s}", "CURVE"); cu.dimensions = '3D'; cu.bevel_depth = 0.009; cu.bevel_resolution = 3
        sp = cu.splines.new('POLY'); N_ = 160; sp.points.add(N_ - 1)
        for j in range(N_):
            a = j / (N_ - 1) * 2 * math.pi * 6
            sp.points[j].co = (X_DEL + 0.055 * math.cos(a), s * 0.40 + 0.055 * math.sin(a), 0.47 + 0.26 * j / (N_ - 1), 1)
        o = bpy.data.objects.new(f"COCHE_Muelle{s}", cu); CC.objects.link(o); o.parent = CAR; cu.materials.append(ROJO)
# las otras tres ruedas
for (x, s, nm) in ((X_TRAS, -1, "RUEDA_TI"), (X_DEL, 1, "RUEDA_DD"), (X_TRAS, 1, "RUEDA_TD")):
    if nm not in bpy.data.objects:
        Mc = dict(M); Mc["goma"] = GOMA_C; Mc["llanta"] = LLANTA_C; Mc["llanta_osc"] = LLOSC_C
        T_["rueda"](nm, (x, s * Y_RUEDA, Z_RUEDA), (R(-90 * s), 0, 0), detalle="bajo", M=Mc, col=CC, padre=CAR)


# ---------------------------------------------------------------- RUEDA PROTAGONISTA REALISTA (raíz DESPIECE; eje del neumático = Z local)
NR = {"__name__": "nr"}; exec(open(D_ + r"\neumatico_real.py", encoding="utf-8").read(), NR)
W0 = Vector(CAR.location) + Vector((X_DEL, -Y_RUEDA, Z_RUEDA))           # rueda delantera izquierda (lado cámara)
P = Vector((-1.50, -0.90, 1.10))                                          # donde flota y se despieza
SUELO = Vector((-1.27, -0.80, ANCHO / 2))                                 # donde cae tumbada
GIRO_FIN = -60.0; BULTO_ANG = -90.0 - GIRO_FIN                            # el bulto acaba mirando a cámara (-Y)
DES = bpy.data.objects.get("DESPIECE")
if DES is None:
    DES = bpy.data.objects.new("DESPIECE", None); CD.objects.link(DES)
DES.empty_display_size = 0.4; DES.rotation_mode = 'XYZ'
def grupo(n):
    g = bpy.data.objects.get(n)
    if g is None: g = bpy.data.objects.new(n, None); CD.objects.link(g)
    g.parent = DES; g.empty_display_size = 0.1; return g
G = {k: grupo("NR_G_" + k) for k in ("alma", "carc", "tal", "c1", "c2", "ext")}
O, MR = NR["construir"](T_, CD, padre=DES)
REPARTO = {"AlmaInterna": "alma", "CarcasaGoma": "carc", "CarcasaHilos": "carc", "TalonAlambres": "tal", "TalonRelleno": "tal",
           "Cinturon1Cables": "c1", "Cinturon1Goma": "c1", "Cinturon2Cables": "c2", "Cinturon2Goma": "c2",
           "Banda": "ext", "Flancos": "ext", "Marcado": "ext"}
for k, o in O.items(): o.parent = G[REPARTO[k]]; o.location = (0, 0, 0)
FLANCOS = O["Flancos"]
if FLANCOS.data.shape_keys is None: FLANCOS.shape_key_add(name="Basis", from_mix=False)
if "bulto" not in FLANCOS.data.shape_keys.key_blocks:
    kb = FLANCOS.shape_key_add(name="bulto", from_mix=False)
    co = np.zeros(len(FLANCOS.data.vertices) * 3, dtype=np.float32); FLANCOS.data.shape_keys.key_blocks["Basis"].data.foreach_get("co", co)
    co = co.reshape(-1, 3); th_b = R(BULTO_ANG)
    r = np.hypot(co[:, 0], co[:, 1]); th = np.arctan2(co[:, 1], co[:, 0])
    dth = (th - th_b + np.pi) % (2 * np.pi) - np.pi; rn = (r - R_LL) / (R_EXT - R_LL)
    g = np.exp(-((dth * r) ** 2) / (2 * 0.032 ** 2) - ((rn - 0.52) ** 2) / (2 * 0.15 ** 2))
    co[:, 2] += np.where(co[:, 2] > 0.02, 0.034 * g, 0.0)
    kb.data.foreach_set("co", co.ravel()); kb.value = 0.0
LLR = bpy.data.objects.get("D_LlantaRaiz")
if LLR is None:
    LLR = bpy.data.objects.new("D_LlantaRaiz", None); CD.objects.link(LLR); LLR.parent = DES
    ml = T_["malla_llanta"]("LLANTA_5x2")
    _obj("D_Llanta", ml, M["llanta"], CD, padre=LLR)
    cilindro("D_LlantaFondo", (0, 0, -0.01), R_LL - 0.01, 0.01, M["llanta_osc"], seg=64, col=CD, padre=LLR)
TROZOS = bpy.data.objects.get("D_Trozos")
if TROZOS is None:
    TROZOS, V2 = NR["trozos_irregulares"](T_, "D_Trozos", MR["goma"])
    CD.objects.link(TROZOS); TROZOS.parent = DES
    TROZOS.shape_key_add(name="Basis", from_mix=False); kb = TROZOS.shape_key_add(name="explota", from_mix=False)
    kb.data.foreach_set("co", np.array(V2, dtype=np.float32).ravel()); kb.value = 0.0

# ================================================================ ANIMACIÓN
for o in list(CD.all_objects) + [ALEX]: o.animation_data_clear()
for o in (FLANCOS, TROZOS):
    if o.data.shape_keys.animation_data: o.data.shape_keys.animation_data_clear()
if sc.animation_data: sc.animation_data_clear()
def kl(o, f, loc=None, rot=None):
    if loc is not None: o.location = loc; o.keyframe_insert("location", frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=f)
def vis(o, f, ver):
    for oo in [o] + list(o.children_recursive):
        oo.hide_render = not ver; oo.hide_viewport = not ver
        oo.keyframe_insert("hide_render", frame=f); oo.keyframe_insert("hide_viewport", frame=f)
def kv(kb, f, v): kb.value = v; kb.keyframe_insert("value", frame=f)
def kxr(f, v): sc["xray"] = v; sc.keyframe_insert('["xray"]', frame=f)
B_ = 129   # el neumático ya está tumbado en P
EST = 130  # "Por dentro": estalla
# --- raíz: en el coche -> sale y sube -> se tumba -> gira despacio -> se monta -> cae al suelo
ROT0 = (R(90), 0, 0)
kl(DES, 1, W0, ROT0); kl(DES, 96, W0, ROT0)
kl(DES, 104, W0 + Vector((0, -0.30, 0.04)), (R(88), 0, R(-6)))
kl(DES, 116, W0.lerp(P, 0.65) + Vector((0, 0, 0.08)), (R(40), 0, R(-14)))
kl(DES, B_, P, (0, 0, R(-18)))
kl(DES, 555, P, (0, 0, R(GIRO_FIN + 6)))
kl(DES, 572, P + Vector((0, 0, -0.10)), (0, 0, R(GIRO_FIN + 2)))
kl(DES, 586, SUELO, (0, 0, R(GIRO_FIN)))
kl(DES, 590, SUELO + Vector((0, 0, 0.035)), None); kl(DES, 594, SUELO, None)
kl(DES, FIN, SUELO, (0, 0, R(GIRO_FIN)))
# --- llanta: cae al estallar
kl(LLR, 1, (0, 0, 0), (0, 0, 0)); kl(LLR, EST, (0, 0, 0), (0, 0, 0))
kl(LLR, EST + 7, (0.05, 0, -0.35), (R(10), 0, 0)); kl(LLR, EST + 14, (0.12, 0, -1.4), (R(25), R(8), 0))
vis(LLR, 1, True); vis(LLR, EST + 15, False)
# --- goma exterior / trozos / capas
vis(G["ext"], 1, True); vis(G["ext"], EST, False); vis(G["ext"], 523, True)
kl(G["ext"], 1, (0, 0, 0)); kl(G["ext"], 521, (0, 0, 0)); kl(G["ext"], 522, (0, 0, 0.62)); kl(G["ext"], 555, (0, 0, 0.62)); kl(G["ext"], 572, (0, 0, 0))
vis(TROZOS, 1, False); vis(TROZOS, EST, True); vis(TROZOS, EST + 41, False); vis(TROZOS, 498, True); vis(TROZOS, 523, False)
kl(TROZOS, 1, (0, 0, 0)); kl(TROZOS, 496, (0, 0, 0)); kl(TROZOS, 497, (0, 0, 0.62))
kbt = TROZOS.data.shape_keys.key_blocks["explota"]
for f_, v in ((EST - 1, 0.0), (EST, 0.0), (EST + 2, 0.22), (EST + 6, 0.52), (EST + 14, 0.80), (EST + 28, 0.95), (EST + 40, 1.0),
              (498, 1.0), (505, 0.90), (513, 0.52), (519, 0.15), (522, 0.0)):
    kv(kbt, f_, v)
INTERNAS = [G[k] for k in ("alma", "carc", "tal", "c1", "c2")]
for g in INTERNAS: vis(g, 1, False); vis(g, EST, True); vis(g, 574, False)
def slot(g, f0, z, dur=20):
    kl(g, 1, (0, 0, 0)); kl(g, f0, (0, 0, 0)); kl(g, f0 + dur, (0, 0, z)); kl(g, 555, (0, 0, z)); kl(g, 572, (0, 0, 0))
slot(G["alma"], 150, -0.52); slot(G["carc"], 213, -0.22); slot(G["tal"], 327, 0.06); slot(G["c1"], 437, 0.30); slot(G["c2"], 439, 0.34)
# --- bulto en el flanco (plano de detalle)
kbb = FLANCOS.data.shape_keys.key_blocks["bulto"]; kv(kbb, 1, 0.0); kv(kbb, 639, 0.0); kv(kbb, 640, 1.0)

# --- rayos X y luces
kxr(1, 0.0); kxr(80, 0.0); kxr(110, 1.0); kxr(605, 1.0); kxr(606, 0.0)
LUZ_PERS = {"Key_Pers": ((1.0, -3.2, 2.7), 360, 1.8), "Rim_Pers": ((-2.2, 2.0, 2.8), 420, 1.5), "Fill_Pers": ((-3.4, -2.6, 1.7), 120, 2.0)}
for n, (loc, e, size) in LUZ_PERS.items():
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, "AREA")); CD.objects.link(o)
    o.data.energy = e; o.data.size = size; o.location = loc
    o.rotation_euler = (Vector((-0.9, -0.2, 0.9)) - o.location).to_track_quat("-Z", "Y").to_euler()
for o in [x for x in bpy.data.objects if x.type == 'LIGHT' and not x.name.startswith("D_Luz")]:
    if o.data.animation_data: o.data.animation_data_clear()
    e0 = o.data.energy
    for f_, k in ((1, 1.0), (80, 1.0), (114, 0.06), (604, 0.06), (606, 1.0)):
        o.data.energy = e0 * k; o.data.keyframe_insert("energy", frame=f_)
    o.data.energy = e0
LED = M["led"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for f_, v in ((1, 6.0), (80, 6.0), (114, 0.25), (604, 0.25), (606, 6.0)):
    LED.default_value = v; LED.keyframe_insert("default_value", frame=f_)
def luz(n, tipo, loc, mira, color, size=1.0):
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, tipo)); CD.objects.link(o)
    o.location = loc; o.data.color = color
    if tipo == 'AREA': o.data.size = size
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if o.data.animation_data: o.data.animation_data_clear()
    return o
L1 = luz("D_LuzClave", 'SPOT', P + Vector((1.2, -1.5, 1.7)), P, (1.0, 0.95, 0.88)); L1.data.spot_size = R(40); L1.data.spot_blend = 0.4
L2 = luz("D_LuzContra", 'AREA', P + Vector((-0.6, 1.4, 0.9)), P, (0.55, 0.72, 1.0), 1.2)
L3 = luz("D_LuzBajo", 'AREA', P + Vector((0.3, -0.8, -1.0)), P, (1.0, 0.7, 0.45), 1.0)
L5 = luz("D_LuzArriba", 'AREA', P + Vector((0.0, -0.2, 1.6)), P, (1.0, 1.0, 1.0), 1.6)
L4 = luz("D_LuzFlash", 'POINT', P + Vector((0, -0.25, 0.15)), P, (1.0, 0.85, 0.6))
for o, e in ((L1, 650), (L2, 220), (L3, 25), (L5, 120)):
    for f_, v in ((1, 0), (90, 0), (120, e), (590, e), (604, 0)):
        o.data.energy = v; o.data.keyframe_insert("energy", frame=f_)
for f_, v in ((1, 0), (EST - 1, 0), (EST, 500), (EST + 4, 250), (EST + 15, 0)):
    L4.data.energy = v; L4.data.keyframe_insert("energy", frame=f_)

# ================================================================ PERSONAJES
ALEX_POS = Vector((-0.62, -0.60, 0)); ALEX_GIRO = -12
sk = MALLA.data.shape_keys
if sk.animation_data and sk.animation_data.action: sk.animation_data.action = None
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
ALEX.location = ALEX_POS; ALEX.rotation_euler = (0, 0, R(ALEX_GIRO))
CL = ClodAnim()
for ob in [CL.arm] + list(CL.ctrl.values()) + CL.ojos + [CL.bocaob]:
    ob.animation_data_clear()
    if getattr(ob.data, "shape_keys", None) and ob.data.shape_keys.animation_data: ob.data.shape_keys.animation_data_clear()
def SX(l): return -1 if l == "R" else 1
ALEX.keyframe_insert("location", frame=1); ALEX.keyframe_insert("rotation_euler", frame=1)
todo_reposo(1); sc.frame_set(1); calibrar_palma()
for l in ("R", "L"): brazo_caido(l, 1)
cara(1, "sonrisa", 0.4)
# Clod sobre el capó, cerca del parabrisas (altura medida con un rayo sobre la carrocería)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
XC, YC = -1.55, 0.62
hit, loc_h, *_ = sc.ray_cast(dg, Vector((XC, YC, 3.0)), Vector((0, 0, -1)))
CLOD_CAPO = (XC, YC, (loc_h.z if hit else 0.90) - 0.004)
CLOD_GIRO = 10

# ---- Clod: SOLO gestos de fondo (no habla)
CL.reposo(1); CL.mover(1, CLOD_CAPO, CLOD_GIRO); CL.cara(1, "contento"); CL.cabeza(1, -6, 0, 10); CL.mirar(1, 0.01, 0.0)
for l in ("R", "L"): CL.brazo_caido(l, 1)
# "¿solo goma con aire?": se encoge de hombros
CL.cara(F(0.6), "duda")
for l in ("R", "L"):
    CL.mano_en(l, F(0.7), (SX(l) * 0.30, -0.12, 0.50)); CL.codo_hacia(l, F(0.7), (SX(l) * 0.75, 0.10, 0.40)); CL.pulgar(l, F(0.7), 1.0)
    CL.mano_giro(l, F(0.7), gira=SX(l) * 40); CL.mano_en(l, F(1.5), (SX(l) * 0.31, -0.12, 0.53))
CL.cabeza(F(0.8), -4, 12, 6); CL.cabeza(F(1.4), -4, -10, 6)
# "Ni de broma": susto con aplastamiento
CL.cara(F(1.85), "sorpresa"); CL.aplastar(F(1.85), 1.0); CL.aplastar(F(1.98), 1.14); CL.aplastar(F(2.15), 0.95); CL.aplastar(F(2.3), 1.0)
for l in ("R", "L"): CL.brazo_caido(l, F(2.0))
# "Mira lo que lleva dentro": señala la rueda (abajo, delante)
CL.cara(F(2.6), "feliz")
CL.mano_en("R", F(2.7), (-0.30, -0.26, 0.30)); CL.codo_hacia("R", F(2.7), (-0.62, 0.15, 0.45)); CL.pulgar("R", F(2.7), 0.2)
CL.cabeza(F(2.7), 22, 0, -14); CL.mirar(F(2.7), -0.012, -0.012)
# la rueda sale volando: manos a la cabeza
CL.cara(104, "susto")
for l in ("R", "L"):
    CL.mano_en(l, 108, (SX(l) * 0.22, -0.06, 0.86)); CL.codo_hacia(l, 108, (SX(l) * 0.70, 0.10, 0.75)); CL.pulgar(l, 108, 0.6)
CL.cabeza(108, 6, 0, -20)
# estalla: se tapa la cara... y se asoma
for l in ("R", "L"):
    CL.mano_en(l, EST + 1, (SX(l) * 0.08, -0.26, 0.74)); CL.codo_hacia(l, EST + 1, (SX(l) * 0.55, 0.05, 0.55))
CL.aplastar(EST, 1.0); CL.aplastar(EST + 4, 0.88); CL.aplastar(EST + 12, 1.0)
CL.cara(EST + 2, "susto")
CL.mano_en("L", EST + 30, (0.24, -0.12, 0.60)); CL.codo_hacia("L", EST + 30, (0.70, 0.10, 0.45)); CL.cara(EST + 30, "sorpresa")
CL.mano_en("R", EST + 30, (-0.08, -0.26, 0.74))
for l in ("R", "L"): CL.brazo_caido(l, EST + 55)
CL.cara(EST + 55, "feliz"); CL.cabeza(EST + 55, 8, 6, -24); CL.mirar(EST + 55, -0.015, 0.0)
# mientras Alex explica: asiente y aplaude a ratos
for f0 in (250, 380, 470):
    CL.cara(f0, "feliz"); CL.rebote(f0, veces=2, alto=0.02, cada=7, manos=False)
CL.cara(560, "sorpresa")
# cae el neumático al suelo: salta de alegría
fj = CL.salto(592, alto=0.18, aire=11); CL.cara(590, "feliz")
# consejo: "un bulto o un corte": susto; "no esperes": dice que no con el dedo, como Alex
CL.cara(F(21.3), "sorpresa"); CL.cabeza(F(21.3), 0, 0, -6)
CL.cara(F(23.0), "serio")
CL.mano_en("R", F(23.05), (-0.12, -0.22, 0.70)); CL.codo_hacia("R", F(23.05), (-0.55, 0.10, 0.45)); CL.pulgar("R", F(23.05), 0.0)
for k, dx in enumerate((-0.05, 0.05, -0.05, 0.05, 0.0)): CL.mano_en("R", F(23.15) + k * 4, (-0.12 + dx, -0.22, 0.72))
for k, g in enumerate((-12, 12, -12, 12, 0)): CL.cabeza(F(23.15) + k * 4, 0, 0, g)
CL.brazo_caido("R", F(24.4)); CL.cara(F(24.4), "contento")
# síguenos: salta y pulgar arriba
CL.cara(F(25.0), "feliz")
fj2 = CL.salto(F(25.15), alto=0.20, aire=12)
fp = CL.pulgar_arriba("L", F(25.8), dur=40)

# ---- Alex
cabeza(1, 0, 0, -6); columna(1, 0, 0, 0)
# "¿Una rueda es solo goma con aire?": manos abiertas, cejas arriba
cara(F(0.3), "duda", 0.8); cabeza(F(0.35), 2, 6, -4)
for l in ("R", "L"):
    mano_en(l, F(0.55), (SX(l) * 0.30, -0.28, 1.08)); codo_hacia(l, F(0.55), (SX(l) * 0.65, 0.05, 1.0)); mano_pose(l, F(0.55), "abierta")
    orientar_mano(l, F(0.55), palma_hacia=(0, -0.2, 1), dedos_hacia=(SX(l) * 0.8, -0.6, 0))
    mano_en(l, F(1.5), (SX(l) * 0.31, -0.28, 1.09))
# "Ni de broma": niega con la cabeza y sonríe
cara(F(1.75), "sonrisa", 0.9)
for k, g in enumerate((-12, 10, -8, 0)): cabeza(F(1.8) + k * 4, 2, 0, g)
for l in ("R", "L"): brazo_caido(l, F(2.1)); mano_pose(l, F(2.1), "relajada")
# "Mira lo que lleva dentro": señala la rueda
mano_en("R", F(2.65), (-0.42, -0.14, 1.04)); codo_hacia("R", F(2.65), (-0.75, 0.15, 1.05)); mano_pose("R", F(2.65), "señalar")
orientar_mano("R", F(2.65), dedos_hacia=(-1, 0.45, -0.5), pulgar_hacia=(0, 0, 1))
mano_en("R", F(3.7), (-0.44, -0.14, 1.02)); orientar_mano("R", F(3.7), dedos_hacia=(-1, 0.45, -0.5), pulgar_hacia=(0, 0, 1))
cabeza(F(2.7), 14, 0, -24); cara(F(2.7), "picaro"); columna(F(2.7), 4, 0, -6)
for l in ("R", "L"): brazo_caido(l, 170); mano_pose(l, 170, "relajada")
cabeza(170, 0, 0, 0); columna(170, 0, 0, 0); cara(170, "neutra")
# consejo (606-752)
kl(ALEX, 605, ALEX_POS, (0, 0, R(ALEX_GIRO))); kl(ALEX, 606, ALEX_POS, (0, 0, R(-4)))
todo_reposo(606)
for l in ("R", "L"): brazo_caido(l, 606); mano_pose(l, 606, "relajada")
cara(606, "duda", 0.5); cabeza(606, 2, 0, 0); columna(606, 2, 0, 0)
mano_en("R", F(20.85), (-0.34, -0.28, 1.04)); codo_hacia("R", F(20.85), (-0.70, 0.05, 1.00)); mano_pose("R", F(20.85), "abierta")
orientar_mano("R", F(20.85), palma_hacia=(0, -0.3, 1), dedos_hacia=(-1, -0.4, -0.3))
cabeza(F(20.9), 8, 0, -18); cara(F(20.9), "duda", 0.8)
mano_en("R", F(22.8), (-0.35, -0.29, 1.03))
cara(F(23.0), "enfado", 0.35); cabeza(F(23.05), 0, 4, 0)
mano_en("R", F(23.1), (-0.16, -0.30, 1.36)); codo_hacia("R", F(23.1), (-0.55, 0.05, 1.05)); mano_pose("R", F(23.1), "señalar")
orientar_mano("R", F(23.1), dedos_hacia=(0, 0, 1), pulgar_hacia=(1, 0, 0))
for t, dz in ((23.3, 0.02), (23.5, -0.005), (23.7, 0.015)): mano_en("R", F(t), (-0.16, -0.30, 1.36 + dz))
cara(F(23.9), "sonrisa", 0.6)
for k, a in enumerate((8, -2, 6, 0)): cabeza(F(24.0) + k * 5, a, 0, 0)
brazo_caido("R", F(24.8)); mano_pose("R", F(24.8), "relajada")
# síguenos (753-851): pulgar arriba
cara(F(25.05), "sonrisa"); cabeza(F(25.05), 2, -4, -10)
mano_en("R", F(25.35), (-0.14, -0.32, 1.22)); codo_hacia("R", F(25.35), (-0.70, 0.10, 0.80)); mano_pose("R", F(25.35), "pulgar")
orientar_mano("R", F(25.35), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", F(25.55), (-0.14, -0.33, 1.27)); orientar_mano("R", F(25.55), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", F(25.75), (-0.14, -0.32, 1.24)); mano_en("R", FIN, (-0.14, -0.32, 1.25))
orientar_mano("R", FIN, pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
parpadeo(F(27.6), 1.0, lado="L")
VOZ_ALEX = [{"at": 0.25, "words": [["¿Una", 0.103, 0.28], ["rueda", 0.28, 0.52], ["es", 0.52, 0.60], ["solo", 0.60, 0.84], ["goma", 0.84, 1.08], ["con", 1.08, 1.16], ["aire", 1.16, 1.48],
                                   ["Ni", 1.551, 1.83], ["de", 1.83, 1.91], ["broma", 1.91, 2.31], ["Mira", 2.373, 2.61], ["lo", 2.61, 2.69], ["que", 2.69, 2.85], ["lleva", 2.85, 3.01], ["dentro", 3.01, 3.41]]},
            {"at": 20.15, "words": [["Por", 0.12, 0.28], ["eso", 0.28, 0.68], ["si", 0.786, 1.0], ["ves", 1.0, 1.16], ["un", 1.16, 1.24], ["bulto", 1.24, 1.72], ["o", 1.72, 1.80], ["un", 1.80, 1.88], ["corte", 1.88, 2.12], ["en", 2.12, 2.20], ["el", 2.28, 2.28], ["lateral", 2.28, 2.83], ["no", 2.88, 2.96], ["esperes", 2.96, 3.59], ["llévala", 3.646, 4.0], ["a", 4.0, 4.08], ["revisar", 4.08, 4.48]]},
            {"at": 25.05, "words": [["Síguenos", 0.119, 0.60], ["para", 0.60, 0.84], ["ver", 0.84, 1.0], ["más", 1.0, 1.24], ["despieces", 1.24, 1.72], ["como", 1.72, 1.96], ["este", 1.96, 2.28]]}]
V3_PALABRAS = [("Por", 0.04, 0.2), ("dentro", 0.2, 0.68), ("una", 0.801, 0.92), ("capa", 0.92, 1.16), ("de", 1.16, 1.32), ("goma", 1.32, 1.56), ("que", 1.64, 1.64), ("no", 1.64, 1.72), ("deja", 1.72, 1.96), ("escapar", 1.96, 2.28), ("el", 2.28, 2.36), ("aire", 2.36, 2.68),
 ("Encima", 2.755, 3.32), ("la", 3.438, 3.56), ("carcasa", 3.56, 4.1), ("lonas", 4.177, 4.5), ("de", 4.58, 4.58), ("hilo", 4.58, 4.82), ("que", 4.9, 4.9), ("aguantan", 4.9, 5.22), ("el", 5.22, 5.38), ("peso", 5.38, 5.78), ("y", 5.78, 5.86), ("los", 5.86, 6.02), ("golpes", 6.02, 6.5),
 ("En", 6.55, 6.71), ("los", 6.71, 6.87), ("bordes", 6.87, 7.35), ("los", 7.462, 7.71), ("talones", 7.71, 8.27), ("con", 8.33, 8.5), ("aros", 8.5, 8.66), ("de", 8.66, 8.74), ("acero", 8.74, 9.06), ("que", 9.14, 9.14), ("la", 9.14, 9.22), ("sujetan", 9.22, 9.7), ("a", 9.7, 9.78), ("la", 9.78, 9.86), ("llanta", 9.86, 10.18),
 ("Luego", 10.2, 10.59), ("cinturones", 10.614, 11.17), ("de", 11.25, 11.25), ("acero", 11.25, 11.49), ("que", 11.57, 11.57), ("la", 11.57, 11.73), ("refuerzan", 11.73, 12.27),
 ("Y", 12.31, 12.39), ("por", 12.39, 12.55), ("fuera", 12.55, 12.95), ("la", 12.98, 13.14), ("banda", 13.14, 13.38), ("de", 13.38, 13.46), ("rodadura", 13.46, 14.01), ("lo", 14.027, 14.25), ("único", 14.25, 14.49), ("que", 14.49, 14.57), ("toca", 14.57, 14.81), ("el", 14.89, 14.89), ("suelo", 14.89, 15.21)]
def abs_t(lineas):
    return [{"at": 0, "words": [[w, l["at"] + a, l["at"] + b] for (w, a, b) in l["words"]]} for l in lineas]
parpadeos(1, FIN, evitar=(F(27.6),))
CL.parpadeos(1, FIN, cada=(55, 85), evitar=[(EST - 30, EST + 60), (F(24.9), F(26.3))])
respirar(1, FIN, periodo=64, amplitud=1.5)
suavizar(); CL.suavizar()
ad = sk.animation_data
if ad and ad.action:
    try: cv = list(ad.action.fcurves)
    except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
    for fc in cv:
        for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
        fc.update()
_m["brillo_led"](sc, umbral=6.0)

# ================================================================ CÁMARA
cam = bpy.data.objects.get("CAM")
if cam is None:
    cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam)
cam.animation_data_clear(); cam.data.animation_data_clear()
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.01
def ck(f, loc, t, lens, dof=None, fstop=2.8):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens; cam.data.dof.use_dof = dof is not None
    cam.data.dof.focus_distance = (Vector(dof) - Vector(loc)).length if dof else 10.0; cam.data.dof.aperture_fstop = fstop
    for p in ("location", "rotation_euler"): cam.keyframe_insert(p, frame=f)
    cam.data.keyframe_insert("lens", frame=f)
    for p in ("use_dof", "focus_distance", "aperture_fstop"): cam.data.dof.keyframe_insert(p, frame=f)
def macro(f, ang, z, borde, dist, elev, lens, fstop=2.8, dof=True):
    """Cámara mirando un punto del borde de una capa (z local en la pila, radio 'borde'), desde el acimut 'ang'."""
    a = R(ang); d = Vector((math.sin(a), -math.cos(a), 0)); tg = P + Vector((0, 0, z)) + d * borde
    pos = tg + d * math.cos(R(elev)) * dist + Vector((0, 0, math.sin(R(elev)) * dist))
    ck(f, tuple(pos), tuple(tg), lens, dof=tuple(tg) if dof else None, fstop=fstop)
CORTES = [1, 606, 640, 692, 753, FIN + 1]
# plano 1 (continuo hasta la caída): Alex, la rueda y Clod de fondo -> entramos -> la rueda sale -> despiece
ck(1, (-0.85, -3.30, 1.45), (-0.88, -0.10, 0.98), 27)
ck(70, (-0.88, -2.95, 1.40), (-0.95, -0.10, 0.90), 28)
ck(90, (-1.02, -2.00, 1.05), (-1.20, 0.0, 0.52), 31)
ck(104, (-1.06, -1.35, 0.80), (-1.27, 0.0, 0.38), 34)
ck(118, (-1.05, -2.25, 1.75), tuple(P + Vector((0, 0, -0.10))), 35)
macro(EST, 18, 0.0, 0.0, 2.30, 34, 36, dof=False)                       # estalla: plano general
macro(148, 22, -0.30, 0.10, 1.80, 30, 38, dof=False)
macro(176, 24, -0.52, 0.29, 0.72, 26, 50, 2.8)                          # alma interna (macro)
macro(205, 32, -0.52, 0.29, 0.66, 24, 50, 2.8)
macro(222, 30, -0.36, 0.18, 1.30, 28, 40, dof=False)
macro(246, 34, -0.22, 0.285, 0.60, 18, 55, 2.8)                         # carcasa: hilos de poliéster
macro(312, 46, -0.22, 0.285, 0.55, 22, 55, 2.8)
macro(330, 44, -0.06, 0.16, 1.25, 30, 40, dof=False)
macro(362, 52, 0.06 + 0.0725, 0.2135, 0.30, 22, 70, 7.0)                 # talón: haz de alambres y relleno
macro(425, 60, 0.06 + 0.0725, 0.2135, 0.28, 24, 70, 7.0)
macro(440, 58, 0.20, 0.16, 1.25, 34, 40, dof=False)
macro(466, 62, 0.32, 0.299, 0.52, 48, 55, 2.8)                          # cinturones: cables de acero cruzados
macro(494, 70, 0.32, 0.299, 0.48, 52, 55, 2.8)
macro(508, 40, 0.10, 0.0, 2.40, 32, 36, dof=False)                       # vuelve la goma exterior
macro(552, 46, 0.10, 0.0, 2.30, 32, 36, dof=False)
ck(574, (-0.70, -2.60, 1.35), tuple(P + Vector((0, 0, -0.45))), 33)
ck(600, (-0.75, -2.40, 0.95), tuple(SUELO + Vector((0, 0, 0.10))), 32)
ck(605, (-0.76, -2.36, 0.94), tuple(SUELO + Vector((0, 0, 0.10))), 32)
# consejo: Alex con Clod de fondo, detalle del bulto, Alex otra vez
ck(606, (-0.30, -2.35, 1.45), (-0.95, -0.05, 1.15), 28)
ck(639, (-0.31, -2.25, 1.45), (-0.95, -0.05, 1.15), 28)
th_w = R(BULTO_ANG + GIRO_FIN); rb = R_LL + 0.52 * (R_EXT - R_LL)
B = SUELO + Vector((rb * math.cos(th_w), rb * math.sin(th_w), ANCHO / 2 + 0.012))
ck(640, tuple(B + Vector((0.34, -0.30, 0.10))), tuple(B + Vector((0, 0, -0.01))), 45, dof=tuple(B), fstop=4.0)
ck(691, tuple(B + Vector((0.29, -0.26, 0.09))), tuple(B + Vector((0, 0, -0.01))), 45, dof=tuple(B), fstop=4.0)
LB = luz("D_LuzBulto", 'SPOT', B + Vector((-0.55, 0.05, 0.14)), B, (1.0, 0.96, 0.9)); LB.data.spot_size = R(40); LB.data.spot_blend = 0.4
for f_, v in ((1, 0), (639, 0), (640, 160), (691, 160), (692, 0)):
    LB.data.energy = v; LB.data.keyframe_insert("energy", frame=f_)
ck(692, (-0.32, -2.20, 1.45), (-0.95, -0.05, 1.15), 28)
ck(752, (-0.33, -2.10, 1.45), (-0.95, -0.05, 1.15), 28)
# síguenos: los dos y el neumático
ck(753, (-0.85, -3.75, 1.30), (-0.88, -0.25, 0.92), 28)
ck(FIN, (-0.86, -3.50, 1.28), (-0.88, -0.25, 0.94), 28)
def _curvas(idb):
    ad_ = getattr(idb, "animation_data", None)
    if not ad_ or not ad_.action: return []
    try: return list(ad_.action.fcurves)
    except Exception: return [fc for l in ad_.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
fin_plano = {c - 1 for c in CORTES[1:]}
for idb in (cam, cam.data, DES, ALEX):
    for fc in _curvas(idb):
        for k in fc.keyframe_points:
            if int(round(k.co[0])) in fin_plano: k.interpolation = 'CONSTANT'
        fc.update()
for fc in _curvas(sc):
    for k in fc.keyframe_points: k.interpolation = 'LINEAR'

sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 67
sc.eevee.taa_render_samples = 48; sc.render.fps = 30; sc.frame_start, sc.frame_end = 1, FIN
try: sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45; sc.render.motion_blur_position = 'START'
except Exception: pass
sc.view_settings.exposure = -0.1

# ================================================================ VOZ NUEVA DE ALEX: reajuste de todos los tiempos
# Todo se diseñó con la voz "Carlos" (VOZ_ALEX). Si existe voces_alex.json (otra voz), se calcula una correspondencia
# de tiempos por palabras clave y se mueven TODAS las claves de animación; luego se ponen los labios con la voz nueva.
import os
VOZ_JSON = BASE + r"\videos_3d\despiece_neumatico\voces_alex.json"
def _todas_curvas():
    out = []
    for act in bpy.data.actions:
        try: cv = list(act.fcurves)
        except Exception: cv = []
        if not cv:
            try: cv = [fc for l in act.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
            except Exception: cv = []
        out += cv
    return out
def _abs(lineas): return [(l["at"] + a, l["at"] + b) for l in lineas for (w, a, b) in l["words"]]
WARP = [(1.0, 1.0)]
VOZ_USAR = VOZ_ALEX
if os.path.exists(VOZ_JSON):
    nueva = json.load(open(VOZ_JSON, encoding="utf-8"))
    VOZ_USAR = [{"at": l["at"], "words": [[w[0], w[1], w[2]] for w in l["words"]]} for l in nueva["lineas"]]
    viejo = [{"at": 0.25, "words": VOZ_ALEX[0]["words"]}, {"at": 4.25, "words": [[w, a, b] for (w, a, b) in V3_PALABRAS]},
             {"at": 20.15, "words": VOZ_ALEX[1]["words"]}, {"at": 25.05, "words": VOZ_ALEX[2]["words"]}]
    def T(lineas, i, j, fin=False):
        l = lineas[i]; w = l["words"][j]; return l["at"] + (w[2] if fin else w[1])
    nuevo = [{"at": l["at"], "words": l["words"]} for l in nueva["lineas"]]
    # (línea, palabra, ¿final?) de los momentos que mandan en la animación
    CLAVES = [(0, 6, True), (0, 7, False), (0, 9, True), (0, 10, False), (0, 14, True),
              (1, 0, False), (1, 2, False), (1, 12, False), (1, 14, False), (1, 25, False), (1, 29, False), (1, 40, False), (1, 41, False),
              (1, 47, False), (1, 51, False), (1, 59, True),
              (2, 0, False), (2, 4, False), (2, 11, True), (2, 12, False), (2, 16, True),
              (3, 0, False), (3, 6, True)]
    for (i, j, fz) in CLAVES:
        WARP.append((T(viejo, i, j, fz) * 30 + 1, T(nuevo, i, j, fz) * 30 + 1))
    # cortes de plano: que caigan en fotogramas enteros
    for c_old, (i, j) in ((606, (2, 0)), (640, (2, 4)), (692, (2, 12)), (753, (3, 0))):
        c_new = round(WARP[[k for k, (i2, j2, f2) in enumerate(CLAVES) if (i2, j2) == (i, j)][0] + 1][1]) - (round(T(viejo, i, j) * 30 + 1) - c_old)
        WARP += [(c_old - 1, c_new - 1), (c_old, c_new)]
    WARP.append((FIN, T(nuevo, 3, 6, True) * 30 + 1 + 27))
    WARP = sorted(set(WARP))
    def W(x):
        xs = [a for a, b in WARP]; ys = [b for a, b in WARP]
        if x <= xs[0]: return x
        if x >= xs[-1]: return ys[-1] + (x - xs[-1])
        return float(np.interp(x, xs, ys))
    # 2) mover todas las claves
    for fc in _todas_curvas():
        for k in fc.keyframe_points:
            x = k.co[0]; nx = W(x); d = nx - x
            k.co[0] = nx; k.handle_left[0] += d; k.handle_right[0] += d
        fc.update()
    FIN = int(round(W(FIN)))
    CORTES = [int(round(W(c))) for c in CORTES]
    sc.frame_end = FIN
    json.dump({"warp": WARP, "fin": FIN, "cortes": CORTES}, open(BASE + r"\videos_3d\despiece_neumatico\warp.json", "w"))
# 3) labios con la voz que se usa
hablar(abs_t(VOZ_USAR))
suavizar()
ad = sk.animation_data
if ad and ad.action:
    try: cv = list(ad.action.fcurves)
    except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
    for fc in cv:
        for k in fc.keyframe_points:
            if k.interpolation != 'CONSTANT': k.interpolation = 'BEZIER'
        fc.update()
result = {"ok": True, "fin": FIN, "P": list(P), "suelo": list(SUELO), "bulto": list(B), "clod": list(CLOD_CAPO), "hit": bool(hit)}
