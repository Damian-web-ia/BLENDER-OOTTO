# DESPIECE 3D DEL NEUMÁTICO (26-11-2026) · vídeo vertical 9:16, 30 fps, ~32,7 s
# Idea de Damián: "entras, hay un coche por fuera, poco a poco vas entrando y ves la pieza, la explicas,
# la divides en miles de cachitos y explicas para qué sirve y cómo funciona".
# Guion y voces (ya hechas, pista voces.ogg montada con estos desfases):
#   V1 Clod  0,30 s  "¿Una rueda es solo goma con aire? Vamos a verlo."
#   V2 Alex  3,35 s  "Ni de broma. Mira lo que lleva dentro."
#   V3 Alex  6,30 s  capas: alma interna, carcasa, talones, cinturones, banda de rodadura
#   V4 Clod 22,10 s  "¡Y yo que pensaba que era un donut gigante!"
#   V5 Alex 25,00 s  "Por eso, si ves un bulto o un corte en el lateral, no esperes: llévala a revisar."
#   V6 Clod 29,85 s  "¡Síguenos para más despieces!"
# Se ejecuta sobre alex_v2_rig.blend abierto (personajes v2). Construye taller v2 + coche + rueda despiezable.
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
FIN = 981

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
        cilindro(f"COCHE_Amort{s}", (X_DEL, s * 0.52, 0.62), 0.025, 0.34, ACERO, col=CC, padre=CAR)
        cu = bpy.data.curves.new(f"COCHE_Muelle{s}", "CURVE"); cu.dimensions = '3D'; cu.bevel_depth = 0.009; cu.bevel_resolution = 3
        sp = cu.splines.new('POLY'); N_ = 160; sp.points.add(N_ - 1)
        for j in range(N_):
            a = j / (N_ - 1) * 2 * math.pi * 6
            sp.points[j].co = (X_DEL + 0.065 * math.cos(a), s * 0.52 + 0.065 * math.sin(a), 0.47 + 0.26 * j / (N_ - 1), 1)
        o = bpy.data.objects.new(f"COCHE_Muelle{s}", cu); CC.objects.link(o); o.parent = CAR; cu.materials.append(ROJO)
# las otras tres ruedas
for (x, s, nm) in ((X_TRAS, -1, "RUEDA_TI"), (X_DEL, 1, "RUEDA_DD"), (X_TRAS, 1, "RUEDA_TD")):
    if nm not in bpy.data.objects:
        Mc = dict(M); Mc["goma"] = GOMA_C; Mc["llanta"] = LLANTA_C; Mc["llanta_osc"] = LLOSC_C
        T_["rueda"](nm, (x, s * Y_RUEDA, Z_RUEDA), (R(-90 * s), 0, 0), detalle="bajo", M=Mc, col=CC, padre=CAR)

# ---------------------------------------------------------------- RUEDA PROTAGONISTA y sus capas (raíz DESPIECE; eje del neumático = Z local)
W0 = Vector(CAR.location) + Vector((X_DEL, -Y_RUEDA, Z_RUEDA))           # rueda delantera izquierda (lado cámara)
P = Vector((-1.50, -0.90, 1.10))                                          # donde flota y se despieza
SUELO = Vector((-1.27, -0.80, ANCHO / 2))                                 # donde cae tumbada (como un donut)
GIRO_FIN = -60.0; BULTO_ANG = -90.0 - GIRO_FIN                            # el bulto acaba mirando a cámara (-Y)
DES = bpy.data.objects.get("DESPIECE")
if DES is None:
    DES = bpy.data.objects.new("DESPIECE", None); CD.objects.link(DES)
DES.empty_display_size = 0.4; DES.rotation_mode = 'XYZ'
def mat_capa(nombre, color, rough, metal, brillo_col, base=None):
    m = bpy.data.materials.get(nombre)
    if m: return m
    m = (base.copy() if base else mat(nombre, color, rough=rough, metal=metal)); m.name = nombre
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.45
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(lw.outputs["Facing"], mx.inputs[0]); mx.inputs[6].default_value = (*[c * 0.35 for c in brillo_col], 1); mx.inputs[7].default_value = (*brillo_col, 1)
    nt.links.new(mx.outputs[2], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 0.0
    return m
def textura_hilos(m, escala, giro_deg, c1, c2, radial=False):
    """Hilos de la carcasa (radiales) o de los cinturones (diagonales)."""
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    if radial:
        tc = nt.nodes.new("ShaderNodeTexCoord"); gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = 'RADIAL'
        mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = escala
        fr = nt.nodes.new("ShaderNodeMath"); fr.operation = 'FRACT'
        nt.links.new(tc.outputs["Object"], gr.inputs["Vector"]); nt.links.new(gr.outputs["Fac"], mu.inputs[0]); nt.links.new(mu.outputs[0], fr.inputs[0])
        fac = fr.outputs[0]
    else:
        tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, R(giro_deg))
        wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = escala; wv.inputs["Distortion"].default_value = 0
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"]); fac = wv.outputs["Fac"]
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.42; cr.color_ramp.elements[1].position = 0.58
    cr.color_ramp.elements[0].color = (*c1, 1); cr.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(fac, cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5; bp.inputs["Distance"].default_value = 0.0008
    nt.links.new(fac, bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])

M_GOMA_H = mat_capa("D_Goma", None, 0, 0, (1.0, 0.55, 0.15), base=M["goma"])
M_ALMA = mat_capa("D_AlmaInterna", (0.07, 0.075, 0.085), 0.35, 0.0, (0.25, 0.65, 1.0))
M_CARC = mat_capa("D_Carcasa", (0.75, 0.62, 0.38), 0.6, 0.0, (1.0, 0.78, 0.30))
M_TAL = mat_capa("D_Talones", (0.80, 0.55, 0.30), 0.28, 1.0, (1.0, 0.55, 0.15))
M_CINT = mat_capa("D_Cinturones", (0.55, 0.57, 0.60), 0.25, 1.0, (0.70, 0.88, 1.0))
if not M_CARC.get("hilos"): textura_hilos(M_CARC, 420, 0, (0.55, 0.43, 0.24), (0.86, 0.75, 0.52), radial=True); M_CARC["hilos"] = 1
if not M_CINT.get("hilos"): textura_hilos(M_CINT, 260, 24, (0.30, 0.31, 0.33), (0.72, 0.74, 0.78)); M_CINT["hilos"] = 1
if not M_TAL.get("hilos"): textura_hilos(M_TAL, 900, 90, (0.55, 0.35, 0.16), (0.92, 0.70, 0.42)); M_TAL["hilos"] = 1

def revolver(nombre, pts, seg=180, cerrado=False):
    me = bpy.data.meshes.get(nombre)
    if me: return me
    n = len(pts); V = []; Fc = []
    for i in range(seg):
        th = 2 * math.pi * i / seg; c, s = math.cos(th), math.sin(th)
        for a, r in pts: V.append((r * c, r * s, a))
    for i in range(seg):
        i2 = (i + 1) % seg
        for k in range(n - 1 + (1 if cerrado else 0)):
            k2 = (k + 1) % n
            Fc.append((i * n + k, i2 * n + k, i2 * n + k2, i * n + k2))
    me = bpy.data.meshes.new(nombre); me.from_pydata(V, [], Fc); me.update()
    for p in me.polygons: p.use_smooth = True
    return me
def espejo_c(media):  # media: puntos de a<0 hasta a=0 -> camino completo talón a talón
    return media + [(-a, r) for (a, r) in reversed(media[:-1])]
cat = T_["_catmull"]
ALMA_P = espejo_c([tuple(p) for p in cat([(-0.074, 0.218), (-0.087, 0.238), (-0.093, 0.263), (-0.089, 0.285), (-0.075, 0.297), (-0.045, 0.300), (0.0, 0.301)], 5)])
CARC_P = espejo_c([tuple(p) for p in cat([(-0.068, 0.226), (-0.080, 0.212), (-0.090, 0.222), (-0.099, 0.244), (-0.103, 0.266), (-0.099, 0.289), (-0.084, 0.303), (-0.050, 0.307), (0.0, 0.3075)], 5)])
def capa(nombre, me, m, solid=0.0):
    o = bpy.data.objects.get(nombre)
    if o is None:
        if m.name not in [x.name for x in me.materials if x]: me.materials.append(m)
        o = bpy.data.objects.new(nombre, me); CD.objects.link(o)
    o.parent = DES
    if solid and not o.modifiers:
        sd = o.modifiers.new("Grosor", "SOLIDIFY"); sd.thickness = solid; sd.offset = 0
    return o
ALMA = capa("D_AlmaInterna", revolver("D_AlmaInterna", ALMA_P), M_ALMA, 0.003)
CARC = capa("D_Carcasa", revolver("D_Carcasa", CARC_P), M_CARC, 0.0025)
TAL = bpy.data.objects.get("D_Talones")
if TAL is None:
    circ = [(0.0085 * math.cos(2 * math.pi * k / 16), 0.0085 * math.sin(2 * math.pi * k / 16)) for k in range(16)]
    V = []; Fc = []; seg = 160
    for side in (-1, 1):
        base = len(V)
        for i in range(seg):
            th = 2 * math.pi * i / seg; c, s = math.cos(th), math.sin(th)
            for (da, dr) in circ:
                r = R_LL + 0.009 + dr; V.append((r * c, r * s, side * 0.074 + da))
        for i in range(seg):
            i2 = (i + 1) % seg
            for k in range(16):
                k2 = (k + 1) % 16; Fc.append((base + i * 16 + k, base + i2 * 16 + k, base + i2 * 16 + k2, base + i * 16 + k2))
    me = bpy.data.meshes.new("D_Talones"); me.from_pydata(V, [], Fc); me.update()
    for p in me.polygons: p.use_smooth = True
    TAL = capa("D_Talones", me, M_TAL)
CINT1 = capa("D_Cinturon1", revolver("D_Cinturon1", [(a, 0.3095) for a in np.linspace(-0.082, 0.082, 8)], seg=200), M_CINT, 0.0018)
CINT2 = capa("D_Cinturon2", revolver("D_Cinturon2", [(a, 0.3125) for a in np.linspace(-0.074, 0.074, 8)], seg=200), M_CINT, 0.0018)
# neumático protagonista (malla propia para poder ponerle un bulto) y llanta
me_h = bpy.data.meshes.get("NEU_despiece")
if me_h is None:
    base_me = T_["malla_neumatico"]("NEU_alto", 800, 24, 110, 40)
    me_h = base_me.copy(); me_h.name = "NEU_despiece"
NEU = capa("D_Neumatico", me_h, M_GOMA_H)
if NEU.data.shape_keys is None: NEU.shape_key_add(name="Basis", from_mix=False)
if not NEU.data.materials or NEU.data.materials[0] != M_GOMA_H:
    NEU.data.materials.clear(); NEU.data.materials.append(M_GOMA_H)
if "bulto" not in NEU.data.shape_keys.key_blocks:
    kb = NEU.shape_key_add(name="bulto", from_mix=False)
    co = np.zeros(len(NEU.data.vertices) * 3, dtype=np.float32); NEU.data.shape_keys.key_blocks["Basis"].data.foreach_get("co", co)
    co = co.reshape(-1, 3); th_b = R(BULTO_ANG)
    r = np.hypot(co[:, 0], co[:, 1]); th = np.arctan2(co[:, 1], co[:, 0])
    dth = (th - th_b + np.pi) % (2 * np.pi) - np.pi
    rn = (r - R_LL) / (R_EXT - R_LL)
    g = np.exp(-((dth * r) ** 2) / (2 * 0.040 ** 2) - ((rn - 0.52) ** 2) / (2 * 0.20 ** 2))
    lado = (co[:, 2] > 0.02) & (rn > 0.12) & (rn < 0.92)
    co[:, 2] += np.where(lado, 0.024 * g, 0.0)
    kb.data.foreach_set("co", co.ravel()); kb.value = 0.0
for kb in NEU.data.shape_keys.key_blocks[1:]: kb.value = 0.0
LLR = bpy.data.objects.get("D_LlantaRaiz")
if LLR is None:
    LLR = bpy.data.objects.new("D_LlantaRaiz", None); CD.objects.link(LLR); LLR.parent = DES
    ml = T_["malla_llanta"]("LLANTA_5x2")
    _obj("D_Llanta", ml, M["llanta"], CD, padre=LLR)
    cilindro("D_LlantaFondo", (0, 0, -0.01), R_LL - 0.01, 0.01, M["llanta_osc"], seg=64, col=CD, padre=LLR)

# ---------------------------------------------------------------- MILES DE TROZOS (una malla, shape key "explota")
TROZOS = bpy.data.objects.get("D_Trozos")
if TROZOS is None:
    rng = np.random.default_rng(11)
    prof = T_["_perfil"](24, 40)[:-4]
    pa = [np.array([prof[0][0], prof[0][1]], dtype=float)]
    for (a, r, s) in prof[1:]:
        q = np.array([a, r], dtype=float)
        if np.linalg.norm(q - pa[-1]) > 1e-5: pa.append(q)
    pa = np.array(pa); seglen = np.linalg.norm(np.diff(pa, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seglen)]); Ltot = cum[-1]
    N_ANG, N_PROF = 120, 18
    V = []; V2 = []; Fc = []
    cara_ = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))
    for j in range(N_PROF):
        sj = (j + 0.5) / N_PROF * Ltot; k = min(len(seglen) - 1, int(np.searchsorted(cum, sj) - 1))
        tt = (sj - cum[k]) / seglen[k]; a0, r0 = pa[k] + tt * (pa[k + 1] - pa[k])
        d = (pa[k + 1] - pa[k]) / seglen[k]; nrm = np.array([d[1], -d[0]])
        if np.dot(nrm, np.array([a0, r0 - (R_LL + R_EXT) / 2])) < 0: nrm = -nrm
        hy = Ltot / N_PROF / 2 * 0.93
        for i in range(N_ANG):
            th = 2 * math.pi * (i + 0.5 * (j % 2)) / N_ANG
            er = np.array([math.cos(th), math.sin(th), 0.0]); ez = np.array([0, 0, 1.0]); et = np.array([-math.sin(th), math.cos(th), 0.0])
            N3 = nrm[0] * ez + nrm[1] * er; T3 = d[0] * ez + d[1] * er
            c = r0 * er + a0 * ez - N3 * 0.006
            hx = math.pi * r0 / N_ANG * 0.93 * rng.uniform(0.85, 1.1); hz = 0.0065
            loc = [c + sx * hx * et + sy * hy * rng.uniform(0.9, 1.0) * T3 + sz * hz * N3 for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
            dirv = N3 * 1.0 + er * 0.55 + rng.normal(0, 0.45, 3); dirv /= np.linalg.norm(dirv)
            dist = rng.uniform(0.6, 2.1)
            ax = rng.normal(0, 1, 3); ax /= np.linalg.norm(ax)
            Rm = np.array(Matrix.Rotation(rng.uniform(1.0, 5.0), 3, Vector(ax)))
            b0 = len(V)
            for p_ in loc:
                V.append(tuple(p_)); V2.append(tuple(c + dirv * dist + Rm @ (p_ - c)))
            for f_ in cara_: Fc.append(tuple(b0 + q for q in f_))
    me = bpy.data.meshes.new("D_Trozos"); me.from_pydata(V, [], Fc); me.update()
    me.materials.append(M_GOMA_H)
    TROZOS = bpy.data.objects.new("D_Trozos", me); CD.objects.link(TROZOS); TROZOS.parent = DES
    TROZOS.shape_key_add(name="Basis", from_mix=False); kb = TROZOS.shape_key_add(name="explota", from_mix=False)
    kb.data.foreach_set("co", np.array(V2, dtype=np.float32).ravel()); kb.value = 0.0

# ================================================================ ANIMACIÓN
for o in list(CD.all_objects) + [ALEX]:
    o.animation_data_clear()
for o in (NEU, TROZOS):
    if o.data.shape_keys.animation_data: o.data.shape_keys.animation_data_clear()
if sc.animation_data: sc.animation_data_clear()
def kl(o, f, loc=None, rot=None):
    if loc is not None: o.location = loc; o.keyframe_insert("location", frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=f)
def vis(o, f, ver):
    o.hide_render = not ver; o.hide_viewport = not ver
    o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)
def kv(kb, f, v): kb.value = v; kb.keyframe_insert("value", frame=f)
def kxr(f, v): sc["xray"] = v; sc.keyframe_insert('["xray"]', frame=f)
def brillo(m, f, v):
    s = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]; s.default_value = v; s.keyframe_insert("default_value", frame=f)
def destello(m, f0, pico=7.0, resto=0.35):
    brillo(m, f0 - 1, 0.0); brillo(m, f0 + 5, pico); brillo(m, f0 + 22, resto)

# --- raíz: en el coche -> sale y sube -> se tumba (eje vertical) y gira -> cae al suelo
ROT0 = (R(90), 0, 0)
kl(DES, 1, W0, ROT0); kl(DES, 158, W0, ROT0)
kl(DES, 166, W0 + Vector((0, -0.30, 0.04)), (R(88), 0, R(-6)))
kl(DES, 178, W0.lerp(P, 0.65) + Vector((0, 0, 0.08)), (R(40), 0, R(-14)))
kl(DES, 189, P, (0, 0, R(-18)))
kl(DES, 590, P, (0, 0, R(GIRO_FIN + 8)))
kl(DES, 628, P + Vector((0, 0, -0.10)), (0, 0, R(GIRO_FIN + 2)))
kl(DES, 641, SUELO, (0, 0, R(GIRO_FIN)))
kl(DES, 645, SUELO + Vector((0, 0, 0.035)), None); kl(DES, 649, SUELO, None)
kl(DES, FIN, SUELO, (0, 0, R(GIRO_FIN)))
# --- llanta: cae al estallar
kl(LLR, 1, (0, 0, 0), (0, 0, 0)); kl(LLR, 190, (0, 0, 0), (0, 0, 0))
kl(LLR, 197, (0.05, 0, -0.35), (R(10), 0, 0)); kl(LLR, 204, (0.12, 0, -1.4), (R(25), R(8), 0))
vis(LLR, 1, True); vis(LLR, 205, False)
for c in LLR.children: vis(c, 1, True); vis(c, 205, False)
# --- neumático entero / trozos / capas
vis(NEU, 1, True); vis(NEU, 190, False); vis(NEU, 592, True)
kl(NEU, 1, (0, 0, 0)); kl(NEU, 590, (0, 0, 0)); kl(NEU, 591, (0, 0, 0.62)); kl(NEU, 600, (0, 0, 0.62)); kl(NEU, 630, (0, 0, 0))
vis(TROZOS, 1, False); vis(TROZOS, 190, True); vis(TROZOS, 231, False); vis(TROZOS, 556, True); vis(TROZOS, 592, False)
kl(TROZOS, 1, (0, 0, 0)); kl(TROZOS, 555, (0, 0, 0)); kl(TROZOS, 556, (0, 0, 0.62))
kbt = TROZOS.data.shape_keys.key_blocks["explota"]
for f_, v in ((189, 0.0), (190, 0.0), (192, 0.22), (196, 0.52), (204, 0.80), (218, 0.95), (230, 1.0), (556, 1.0), (566, 0.93), (578, 0.55), (586, 0.16), (591, 0.0)):
    kv(kbt, f_, v)
CAPAS = [ALMA, CARC, TAL, CINT1, CINT2]
for o in CAPAS: vis(o, 1, False); vis(o, 190, True); vis(o, 631, False)
def slot(o, f0, z, dur=20):
    kl(o, 1, (0, 0, 0)); kl(o, f0, (0, 0, 0)); kl(o, f0 + dur, (0, 0, z)); kl(o, 600, (0, 0, z)); kl(o, 630, (0, 0, 0))
slot(ALMA, 195, -0.52); slot(CARC, 274, -0.22); slot(TAL, 388, 0.05); slot(CINT1, 497, 0.30); slot(CINT2, 499, 0.34)
# --- brillos al nombrar cada capa
for m_ in (M_ALMA, M_CARC, M_TAL, M_CINT, M_GOMA_H): brillo(m_, 1, 0.0)
destello(M_ALMA, 192); destello(M_CARC, 292); destello(M_TAL, 420); destello(M_CINT, 507); destello(M_GOMA_H, 585, 5.0, 0.0)
brillo(M_GOMA_H, 610, 0.0)
for m_ in (M_ALMA, M_CARC, M_TAL, M_CINT): brillo(m_, 600, 0.35); brillo(m_, 625, 0.0)
# --- bulto en el lateral (plano de detalle)
kbb = NEU.data.shape_keys.key_blocks["bulto"]; kv(kbb, 1, 0.0); kv(kbb, 815, 0.0); kv(kbb, 816, 1.0)

# --- rayos X y luces
kxr(1, 0.0); kxr(140, 0.0); kxr(170, 1.0); kxr(650, 1.0); kxr(651, 0.0)
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
    for f_, k in ((1, 1.0), (140, 1.0), (174, 0.06), (649, 0.06), (651, 1.0)):
        o.data.energy = e0 * k; o.data.keyframe_insert("energy", frame=f_)
    o.data.energy = e0
LED = M["led"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for f_, v in ((1, 6.0), (140, 6.0), (174, 0.25), (649, 0.25), (651, 6.0)):
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
L1 = luz("D_LuzClave", 'AREA', P + Vector((0.9, -1.6, 1.4)), P, (1.0, 0.95, 0.88), 1.3)
L2 = luz("D_LuzContra", 'AREA', P + Vector((-0.6, 1.4, 0.9)), P, (0.35, 0.62, 1.0), 1.2)
L3 = luz("D_LuzBajo", 'AREA', P + Vector((0.3, -0.8, -1.0)), P, (1.0, 0.6, 0.3), 1.0)
L4 = luz("D_LuzFlash", 'POINT', P + Vector((0, -0.25, 0.15)), P, (1.0, 0.85, 0.6))
for o, e in ((L1, 150), (L2, 320), (L3, 45)):
    for f_, v in ((1, 0), (150, 0), (180, e), (640, e), (650, 0)):
        o.data.energy = v; o.data.keyframe_insert("energy", frame=f_)
for f_, v in ((1, 0), (189, 0), (190, 600), (194, 300), (205, 0), (556, 0), (590, 0), (592, 500), (600, 0)):
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
# capó: altura en el centro a la x de Clod
X_CLOD = -1.42
H_, ze_, zt_, cab_ = seccion(X_CLOD)
CLOD_CAPO = (CAR.location.x + X_CLOD, CAR.location.y - 0.05, zt_ + 0.01 - 0.012)
CLOD_SUELO = (-1.01, -0.86, ANCHO + 0.002)          # de pie encima del neumático tumbado

# ---- PLANO 1 (1-100): Clod sobre el capó: "¿Una rueda es solo goma con aire? Vamos a verlo."
CL.reposo(1); CL.mover(1, CLOD_CAPO, -6); CL.cara(1, "duda"); CL.cabeza(1, 0, 6, 0)
for l in ("R", "L"):
    CL.mano_en(l, F(0.45), (SX(l) * 0.30, -0.12, 0.50)); CL.codo_hacia(l, F(0.45), (SX(l) * 0.75, 0.10, 0.40)); CL.pulgar(l, F(0.45), 1.0)
    CL.mano_giro(l, F(0.45), gira=SX(l) * 40)
    CL.mano_en(l, F(1.9), (SX(l) * 0.31, -0.12, 0.52))
CL.cabeza(F(0.6), -6, 10, 4); CL.cuerpo(F(0.6), 0, 4, 0); CL.mirar(F(0.6), 0.0, 0.01)
CL.cabeza(F(1.6), -6, -8, -4); CL.cuerpo(F(1.6), 0, -3, 0)
# "Vamos a verlo": señala hacia abajo, a la rueda, y salta un poco
CL.cara(F(2.1), "feliz")
CL.mano_en("R", F(2.25), (-0.34, -0.22, 0.30)); CL.codo_hacia("R", F(2.25), (-0.65, 0.20, 0.45)); CL.pulgar("R", F(2.25), 0.2)
CL.brazo_caido("L", F(2.25)); CL.cabeza(F(2.25), 22, 0, -10); CL.mirar(F(2.25), -0.015, -0.012)
CL.rebote(F(2.55), veces=1, alto=0.03, cada=7)
CL.mano_en("R", F(3.4), (-0.34, -0.22, 0.31))
# después mira la rueda (planos 2-3) hasta que se apagan las luces
for l in ("R", "L"): CL.brazo_caido(l, 115)
CL.cara(115, "contento"); CL.cabeza(115, 24, 0, -8); CL.mirar(115, -0.01, -0.012)
CL.cara(150, "sorpresa"); CL.cabeza(165, 8, 0, -12)
CL.mover(650, CLOD_CAPO, -6)

# ---- Alex en los planos 1-2: mira a Clod y luego: "Ni de broma. Mira lo que lleva dentro."
cabeza(1, -12, 0, -30); columna(1, 0, 0, -8)
for l in ("R", "L"):
    mano_en(l, 20, (SX(l) * 0.13, -0.20, 1.04)); codo_hacia(l, 20, (SX(l) * 0.55, 0.05, 1.05)); mano_pose(l, 20, "relajada")
mano_en("R", 20, (-0.12, -0.21, 1.10)); mano_en("L", 20, (0.12, -0.21, 1.06))
cara(F(1.2), "picaro"); cabeza(F(1.3), -10, 6, -32)
# "Ni de broma": niega con la cabeza
cara(F(3.3), "sonrisa", 0.8); cabeza(F(3.35), 0, 0, -4); columna(F(3.35), 0, 0, 0)
for k, g in enumerate((-12, 10, -8, 0)): cabeza(F(3.45) + k * 4, 2, 0, g)
for l in ("R", "L"): brazo_caido(l, F(3.5)); mano_pose(l, F(3.5), "relajada")
# "Mira lo que lleva dentro": señala la rueda con la derecha
mano_en("R", F(4.3), (-0.42, -0.14, 1.04)); codo_hacia("R", F(4.3), (-0.75, 0.15, 1.05)); mano_pose("R", F(4.3), "señalar")
orientar_mano("R", F(4.3), dedos_hacia=(-1, 0.45, -0.5), pulgar_hacia=(0, 0, 1))
mano_en("R", F(5.5), (-0.44, -0.14, 1.02)); orientar_mano("R", F(5.5), dedos_hacia=(-1, 0.45, -0.5), pulgar_hacia=(0, 0, 1))
cabeza(F(4.4), 14, 0, -24); cara(F(4.4), "picaro"); columna(F(4.4), 4, 0, -6)
for l in ("R", "L"): brazo_caido(l, 230); mano_pose(l, 230, "relajada")
cabeza(230, 0, 0, 0); columna(230, 0, 0, 0); cara(230, "neutra")

# ---- PLANO 4 (651-745): Clod junto al neumático tumbado: "¡Y yo que pensaba que era un donut gigante!"
CL.mover(651, CLOD_SUELO, -6); CL.reposo(651); CL.cara(651, "contento"); CL.cabeza(651, 10, 0, -28); CL.mirar(651, -0.02, -0.01)
for l in ("R", "L"): CL.brazo_caido(l, 651)
CL.cara(F(22.05), "sorpresa"); CL.cabeza(F(22.15), -4, 0, -6); CL.mirar(F(22.15), 0.0, 0.01)
CL.aplastar(F(22.05), 1.0); CL.aplastar(F(22.18), 1.12); CL.aplastar(F(22.35), 0.96); CL.aplastar(F(22.5), 1.0)
for l in ("R", "L"):   # manos a la "cabeza"
    CL.mano_en(l, F(22.2), (SX(l) * 0.22, -0.06, 0.86)); CL.codo_hacia(l, F(22.2), (SX(l) * 0.70, 0.10, 0.75)); CL.pulgar(l, F(22.2), 0.6)
    CL.mano_en(l, F(23.2), (SX(l) * 0.23, -0.07, 0.87))
CL.cabeza(F(23.0), -2, 8, 4)
# "donut gigante": señala el neumático y se ríe
CL.cara(F(23.6), "risa")
CL.mano_en("R", F(23.6), (-0.36, -0.22, 0.34)); CL.codo_hacia("R", F(23.6), (-0.62, 0.15, 0.45)); CL.pulgar("R", F(23.6), 0.2)
CL.mano_en("L", F(23.6), (0.26, -0.12, 0.40)); CL.codo_hacia("L", F(23.6), (0.70, 0.10, 0.40))
CL.cabeza(F(23.7), 12, -6, -22); CL.rebote(F(23.9), veces=2, alto=0.025, cada=7)
CL.mano_en("R", F(24.7), (-0.36, -0.22, 0.35))
for l in ("R", "L"): CL.brazo_caido(l, F(25.1))
CL.cara(F(25.1), "contento")

# ---- PLANO 5 (746-895): Alex serio: "Por eso, si ves un bulto o un corte en el lateral, no esperes: llévala a revisar."
kl(ALEX, 745, ALEX_POS, (0, 0, R(ALEX_GIRO))); kl(ALEX, 746, ALEX_POS, (0, 0, R(-4)))
todo_reposo(746)
for l in ("R", "L"): brazo_caido(l, 746); mano_pose(l, 746, "relajada")
cara(746, "concentrado", 0.7); cabeza(746, 2, 0, 0); columna(746, 2, 0, 0)
# "si ves un bulto o un corte en el lateral": mano abierta hacia el neumático (a su derecha, abajo)
mano_en("R", F(25.75), (-0.34, -0.28, 1.04)); codo_hacia("R", F(25.75), (-0.70, 0.05, 1.00)); mano_pose("R", F(25.75), "abierta")
orientar_mano("R", F(25.75), palma_hacia=(0, -0.3, 1), dedos_hacia=(-1, -0.4, -0.3))
cabeza(F(25.8), 8, 0, -18); cara(F(25.8), "concentrado", 0.9)
mano_en("R", F(27.6), (-0.35, -0.29, 1.03))
# "no esperes": índice arriba, mirando a cámara
cara(F(27.8), "enfado", 0.35); cabeza(F(27.85), 0, 4, 0)
mano_en("R", F(27.9), (-0.16, -0.30, 1.36)); codo_hacia("R", F(27.9), (-0.55, 0.05, 1.05)); mano_pose("R", F(27.9), "señalar")
orientar_mano("R", F(27.9), dedos_hacia=(0, 0, 1), pulgar_hacia=(1, 0, 0))
for t, dz in ((28.1, 0.02), (28.3, -0.005), (28.5, 0.015)): mano_en("R", F(t), (-0.16, -0.30, 1.36 + dz))
# "llévala a revisar": asiente con una media sonrisa
cara(F(28.7), "sonrisa", 0.6)
for k, a in enumerate((8, -2, 6, 0)): cabeza(F(28.8) + k * 5, a, 0, 0)
brazo_caido("R", F(29.6)); mano_pose("R", F(29.6), "relajada")

# ---- PLANO 6 (896-981): "¡Síguenos para más despieces!" Clod salta y los dos levantan el pulgar
CL.mover(895, CLOD_SUELO, -6); CL.mover(896, CLOD_SUELO, -6)
CL.cara(896, "feliz"); CL.cabeza(896, -4, 0, 0)
fj = CL.salto(F(29.95), alto=0.22, aire=12)
fp = CL.pulgar_arriba("L", F(30.5), dur=40)
cara(F(29.9), "sonrisa"); cabeza(F(29.9), 2, -4, -10)
mano_en("R", F(30.2), (-0.14, -0.32, 1.22)); codo_hacia("R", F(30.2), (-0.70, 0.10, 0.80)); mano_pose("R", F(30.2), "pulgar")
orientar_mano("R", F(30.2), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", F(30.4), (-0.14, -0.33, 1.27)); orientar_mano("R", F(30.4), pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
mano_en("R", F(30.6), (-0.14, -0.32, 1.24)); mano_en("R", FIN, (-0.14, -0.32, 1.25))
orientar_mano("R", FIN, pulgar_hacia=(0, 0, 1), dedos_hacia=(0.6, -0.4, 0))
parpadeo(F(31.6), 1.0, lado="L")

# ---- voces (labios), parpadeos, respiración
VOZ_CLOD = [{"at": 0.30, "words": [["¿Una", 0.12, 0.28], ["rueda", 0.28, 0.68], ["es", 0.73, 0.93], ["solo", 0.93, 1.25], ["goma", 1.25, 1.49], ["con", 1.49, 1.65], ["aire", 1.65, 1.89], ["Vamos", 2.12, 2.29], ["a", 2.29, 2.37], ["verlo", 2.37, 2.69]]},
            {"at": 22.10, "words": [["¡Y", 0.12, 0.28], ["yo", 0.28, 0.52], ["que", 0.559, 0.68], ["pensaba", 0.68, 1.16], ["que", 1.16, 1.24], ["era", 1.24, 1.40], ["un", 1.40, 1.48], ["donut", 1.48, 1.88], ["gigante", 1.88, 2.52]]},
            {"at": 29.85, "words": [["¡Síguenos", 0.119, 0.60], ["para", 0.60, 0.76], ["más", 0.76, 0.92], ["despieces", 0.92, 1.56]]}]
VOZ_ALEX = [{"at": 3.35, "words": [["Ni", 0.116, 0.36], ["de", 0.36, 0.44], ["broma", 0.44, 0.85], ["Mira", 0.891, 1.19], ["lo", 1.19, 1.27], ["que", 1.27, 1.43], ["lleva", 1.43, 1.59], ["dentro", 1.59, 2.07]]},
            {"at": 25.00, "words": [["Por", 0.12, 0.28], ["eso", 0.28, 0.68], ["si", 0.786, 1.0], ["ves", 1.0, 1.16], ["un", 1.16, 1.24], ["bulto", 1.24, 1.72], ["o", 1.72, 1.80], ["un", 1.80, 1.88], ["corte", 1.88, 2.12], ["en", 2.12, 2.20], ["el", 2.28, 2.28], ["lateral", 2.28, 2.83], ["no", 2.88, 2.96], ["esperes", 2.96, 3.59], ["llévala", 3.646, 4.0], ["a", 4.0, 4.08], ["revisar", 4.08, 4.48]]}]
def abs_t(lineas):
    return [{"at": 0, "words": [[w, l["at"] + a, l["at"] + b] for (w, a, b) in l["words"]]} for l in lineas]
hablar(abs_t(VOZ_ALEX)); CL.hablar(abs_t(VOZ_CLOD))
parpadeos(1, FIN, evitar=(F(31.6),))
CL.parpadeos(1, FIN, cada=(55, 85), evitar=[(F(22.0), F(23.4)), (F(29.8), F(31.0))])
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
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.02
def ck(f, loc, t, lens, dof=None, fstop=2.8):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens; cam.data.dof.use_dof = dof is not None
    cam.data.dof.focus_distance = (Vector(dof) - Vector(loc)).length if dof else 10.0; cam.data.dof.aperture_fstop = fstop
    for p in ("location", "rotation_euler"): cam.keyframe_insert(p, frame=f)
    cam.data.keyframe_insert("lens", frame=f)
    for p in ("use_dof", "focus_distance", "aperture_fstop"): cam.data.dof.keyframe_insert(p, frame=f)
CORTES = [1, 101, 651, 746, 816, 896, FIN + 1]
W0t = tuple(W0)
# plano 1: coche con Clod en el capó, acercándose
ck(1, (-1.30, -2.10, 0.80), (-1.33, 0.30, 0.66), 38)
ck(100, (-1.30, -1.88, 0.80), (-1.33, 0.30, 0.67), 38)
# planos 2-3 (continuo): Alex y la rueda -> entramos -> despiece en el aire -> cae
ck(101, (-0.85, -3.30, 1.45), (-0.86, -0.20, 0.95), 27)
ck(128, (-0.90, -2.85, 1.38), (-1.00, -0.12, 0.84), 28)
ck(150, (-1.04, -1.62, 0.92), (-1.24, 0.02, 0.48), 32)
ck(166, (-1.06, -1.30, 0.78), (-1.27, 0.0, 0.36), 34)
ck(180, (-0.95, -2.10, 1.40), tuple(P + Vector((0, 0, -0.10))), 35)
def orbita(f, ang, dist=2.30, alt=1.55, mira_z=0.02, lens=36):
    a = R(ang); off = Vector((math.sin(a) * dist, -math.cos(a) * dist, alt))
    ck(f, tuple(P + off), tuple(P + Vector((0, 0, mira_z))), lens)
orbita(194, -14); orbita(272, -19); orbita(386, -24); orbita(495, -28); orbita(556, -31, mira_z=0.10); orbita(600, -32, mira_z=0.08)
ck(628, (-0.62, -2.55, 1.30), tuple(P + Vector((0, 0, -0.45))), 33)
ck(650, (-0.70, -2.35, 0.95), tuple(SUELO + Vector((0, 0, 0.10))), 32)
# plano 4: Clod y el "donut"
ck(651, (-1.12, -2.70, 0.80), (-1.12, -0.85, 0.28), 30)
ck(745, (-1.12, -2.52, 0.78), (-1.12, -0.85, 0.29), 30)
# plano 5: Alex serio, luego detalle del bulto
ck(746, (-0.74, -2.15, 1.52), (-0.62, -0.60, 1.40), 40)
ck(815, (-0.72, -2.00, 1.52), (-0.62, -0.60, 1.40), 40)
th_w = R(BULTO_ANG + GIRO_FIN); rb = R_LL + 0.52 * (R_EXT - R_LL)
B = SUELO + Vector((rb * math.cos(th_w), rb * math.sin(th_w), ANCHO / 2 + 0.012))
ck(816, tuple(B + Vector((0.20, -0.46, 0.36))), tuple(B), 50, dof=tuple(B), fstop=3.5)
ck(895, tuple(B + Vector((0.16, -0.38, 0.30))), tuple(B), 50, dof=tuple(B), fstop=3.5)
# plano 6: los dos
ck(896, (-0.95, -3.85, 1.15), (-0.95, -0.70, 0.92), 30)
ck(FIN, (-0.95, -3.62, 1.13), (-0.95, -0.70, 0.93), 30)
def _curvas(idb):
    ad_ = getattr(idb, "animation_data", None)
    if not ad_ or not ad_.action: return []
    try: return list(ad_.action.fcurves)
    except Exception: return [fc for l in ad_.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
fin_plano = {c - 1 for c in CORTES[1:]}
for idb in (cam, cam.data, cam.data.dof, DES, ALEX, CL.arm):
    for fc in _curvas(idb):
        for k in fc.keyframe_points:
            if int(round(k.co[0])) in fin_plano: k.interpolation = 'CONSTANT'
        fc.update()
for fc in _curvas(sc):
    for k in fc.keyframe_points: k.interpolation = 'LINEAR'
# cortes de Clod (salto de sitio entre planos)
for o in [CL.arm] + list(CL.ctrl.values()):
    for fc in _curvas(o):
        for k in fc.keyframe_points:
            if int(round(k.co[0])) in (650, 895): k.interpolation = 'CONSTANT'
        fc.update()

sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 67
sc.eevee.taa_render_samples = 40; sc.render.fps = 30; sc.frame_start, sc.frame_end = 1, FIN
try: sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45
except Exception: pass
sc.view_settings.exposure = -0.1
result = {"ok": True, "fin": FIN, "P": list(P), "suelo": list(SUELO), "bulto": list(B), "verts_trozos": len(TROZOS.data.vertices)}
