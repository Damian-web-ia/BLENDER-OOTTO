# EL MOTOR POR DENTRO (4 TIEMPOS) · primer vídeo con Maite · EKORUEDAS · 27-11-2026
# Sigue la skill "EKORUEDAS Automotive CGI 4K": estudio oscuro y limpio (azules fríos + reflejos cálidos), motor en corte
# con medidas reales, despiece suspendido que se vuelve a montar, funcionamiento por dentro (admisión, compresión,
# explosión, escape), cámara lenta en la chispa, rampa de velocidad, planos macro y foco de cine (lo pone el render).
# Maite explica (voz Renata); Clod no habla. Diseño a 30 fps: el render 4K lo pasa a 60 fps.
# Uso: blender -b --factory-startup --python motor_4t.py -- <carpeta EKORUEDAS_ESTUDIO_3D> <salida.blend>
import bpy, sys, os, math, json, random
from mathutils import Vector, Matrix, Euler, Quaternion
from bpy_extras.object_utils import world_to_camera_view
argv = sys.argv[sys.argv.index("--") + 1:]
R, SALIDA = argv[0], argv[1]
LIB = os.path.join(R, "biblioteca"); VID = os.path.join(R, "videos_3d", "motor_4t")
bpy.ops.wm.read_factory_settings(use_empty=True)
MP = {"__name__": "mp"}; exec(open(os.path.join(LIB, "materiales_pro.py"), encoding="utf-8").read(), MP)
BUJ = {"__name__": "buj"}; exec(open(os.path.join(LIB, "bujia_real.py"), encoding="utf-8").read(), BUJ)
G = {"__name__": "mot"}; exec(open(os.path.join(LIB, "motor_4t_real.py"), encoding="utf-8").read(), G)
sc = bpy.context.scene; sc.render.fps = 30
FIN = 1186; sc.frame_start, sc.frame_end = 1, FIN
VOZ = json.load(open(os.path.join(VID, "voces_motor.json"), encoding="utf-8"))
def F(t): return int(round(t * 30)) + 1
def FW(i, j, fin=False):
    l = VOZ["lineas"][i]; w = l["words"][j]; return F(l["at"] + (w[2] if fin else w[1]))
def lerp(a, b, u): return a + (b - a) * u
def suave(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)

col = bpy.data.collections.new("ESTUDIO"); sc.collection.children.link(col)
cm = bpy.data.collections.new("MOTOR"); sc.collection.children.link(cm)

# ================================================================ ESTUDIO
import bmesh
def malla(nombre, fn, mats, c=col):
    bm = bmesh.new(); fn(bm); me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me); c.objects.link(o)
    for m in mats: me.materials.append(m)
    return o
def mat(nombre, color, rugo=0.4, metal=0.0, emis=None, fuerza=0.0, coat=0.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rugo; b.inputs["Metallic"].default_value = metal
    if coat: b.inputs["Coat Weight"].default_value = coat
    if emis: b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = fuerza
    return m
M_CICLO = mat("EST_Ciclorama", (0.010, 0.011, 0.014), rugo=0.32, coat=0.2)
M_PEANA = mat("EST_Peana", (0.020, 0.021, 0.024), rugo=0.28, metal=0.6, coat=0.5)
M_FILO = mat("EST_FiloLuz", (0.3, 0.6, 1.0), emis=(0.30, 0.62, 1.0), fuerza=9.0)
M_LINEA = mat("EST_LineaFondo", (0.2, 0.4, 0.9), emis=(0.18, 0.42, 1.0), fuerza=1.6)
def ciclorama(bm):
    perfil = [(-6.0, 0.0), (1.2, 0.0)]
    for k in range(1, 17):
        a = math.pi / 2 * k / 16; perfil.append((1.2 + 1.0 * math.sin(a), 1.0 - 1.0 * math.cos(a)))
    perfil.append((2.2, 4.0))
    fila = []
    for x in (-6.0, 6.0):
        fila.append([bm.verts.new((x, y, z)) for y, z in perfil])
    for i in range(len(perfil) - 1):
        bm.faces.new([fila[0][i], fila[1][i], fila[1][i + 1], fila[0][i + 1]])
cic = malla("EST_Ciclorama", ciclorama, [M_CICLO])
for p in cic.data.polygons: p.use_smooth = True
def peana(bm):
    G["torno"](bm, [(0.0, 0.0), (0.30, 0.0), (0.30, 0.845), (0.296, 0.856), (0.285, 0.86), (0.0, 0.86)], seg=128)
pe = malla("EST_Peana", peana, [M_PEANA]); [setattr(p, "use_smooth", True) for p in pe.data.polygons]
def filo(bm): G["torno"](bm, [(0.300, 0.853), (0.3035, 0.853), (0.3035, 0.857), (0.300, 0.857)], seg=128)
malla("EST_FiloLuz", filo, [M_FILO])
for k, (x, z) in enumerate(((-1.6, 1.9), (-0.9, 2.4), (0.9, 2.4), (1.6, 1.9))):      # líneas de luz finas en el fondo
    malla(f"EST_Linea_{k}", lambda bm, x=x, z=z: G["caja"](bm, x - 0.006, x + 0.006, 2.18, 2.19, z - 0.9, z + 0.9), [M_LINEA])
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.005, 0.008, 1)
def luz(nombre, loc, energia, tam, color, mira=(0, 0, 1.08), forma='RECTANGLE', tam_y=None):
    d = bpy.data.lights.new(nombre, 'AREA'); d.energy = energia; d.color = color; d.shape = forma
    d.size = tam; d.size_y = tam_y if tam_y else tam
    o = bpy.data.objects.new(nombre, d); col.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
# (27-11, 21:25) la primera prueba salió quemada y el fondo gris: luces a ~1/3 para un estudio oscuro de verdad
luz("Clave_calida", (-1.25, -1.55, 2.05), 105, 1.1, (1.0, 0.88, 0.76), tam_y=0.7)
luz("Contra_azul_izq", (-1.35, 1.10, 1.65), 190, 0.25, (0.45, 0.68, 1.0), tam_y=1.6)
luz("Contra_azul_der", (1.40, 1.05, 1.45), 190, 0.25, (0.45, 0.68, 1.0), tam_y=1.6)
luz("Cenital", (0.0, 0.1, 2.7), 45, 1.4, (0.92, 0.95, 1.0))
luz("Relleno_frio", (1.25, -1.75, 0.95), 22, 1.2, (0.75, 0.86, 1.0))
luz("Maite_clave", (-1.2, -1.6, 2.0), 55, 0.9, (1.0, 0.9, 0.8), mira=(-0.62, 0.1, 1.45))

# ================================================================ MOTOR
O = G["construir_motor"](cm, MP, BUJ)
RAIZ = O["raiz"]; RAIZ.location = (0, 0, 0.965)
ZC = G["CUBIERTA"] + 0.0016
def grupo(nombre, hijos):
    e = bpy.data.objects.new(nombre, None); cm.objects.link(e); e.parent = RAIZ; e.empty_display_size = 0.05
    for h in hijos:
        mw = h.matrix_local.copy(); h.parent = e; h.matrix_parent_inverse = Matrix.Identity(4); h.matrix_local = mw
    return e
cul_d = [o for o in O["detras"] if o.name.startswith(("MOT_Culata", "MOT_PortaLevas"))]
hijos_cul = cul_d + list(O["valv"].values()) + list(O["leva"].values()) + [m[0] for m in O["muelle"].values()]
if "bujia" in O: hijos_cul.append(O["bujia"]["raiz"])
EXP = {"cul": grupo("EXP_Culata", hijos_cul), "pis": grupo("EXP_Piston", [O["pis"]]), "bie": grupo("EXP_Biela", [O["bie"]]), "cig": grupo("EXP_Cigueñal", [O["cig"]])}
for k in ("ANC_CAMARA", "ANC_BUJIA"):
    a = bpy.data.objects[k]; mw = a.matrix_local.copy(); a.parent = EXP["cul"]; a.matrix_local = mw

# ---------------- ángulo del cigüeñal en cada fotograma
L1_BAJA, L1_ADM, L1_SUBE, L1_COMP = FW(1, 8), FW(1, 14, True), FW(1, 15), FW(1, 19, True)
L2_CHISPA, L2_EXPLOTA, L2_ABAJO, L2_SUBIR, L2_ESCAPE = FW(2, 2), FW(2, 8), FW(2, 14, True), FW(2, 16), FW(2, 22, True)
L3_BIELA, L3_CIG, L3_CUATRO, L3_VUELTAS = FW(3, 1), FW(3, 10), FW(3, 17), FW(3, 20, True)
L4_TRES, L4_SEG, L4_CLOD, L4_TOCA = FW(4, 1), FW(4, 10, True), FW(4, 11), FW(4, 15, True)
L5_TIRONES, L5_TIEMBLA, L5_QUE, L5_FIN = FW(5, 2), FW(5, 6), FW(5, 11), FW(5, 14, True)
F_ABRE = FW(0, 9) - 6
EXP0, EXP1, EXP2, EXP3 = L2_ESCAPE + 14, L2_ESCAPE + 44, L3_CUATRO - 24, L3_CUATRO - 2
RAMPA0 = L3_VUELTAS + 8
TRAMOS = [(1, -200.0, L1_BAJA - 2, -2.0, "lin"), (L1_BAJA - 2, -2.0, L1_BAJA, 0.0, "lin"),
          (L1_BAJA, 0.0, L1_ADM, 180.0, "suave"), (L1_ADM, 180.0, L1_SUBE, 180.0, "lin"), (L1_SUBE, 180.0, L1_COMP - 6, 360.0, "suave"),
          (L1_COMP - 6, 360.0, L2_EXPLOTA, 360.0, "lin"), (L2_EXPLOTA, 360.0, L2_ABAJO, 540.0, "salida"),
          (L2_ABAJO, 540.0, L2_SUBIR, 540.0, "lin"), (L2_SUBIR, 540.0, L2_ESCAPE, 720.0, "suave"),
          (L2_ESCAPE, 720.0, L3_CUATRO, 720.0, "lin"), (L3_CUATRO, 720.0, L3_VUELTAS, 1440.0, "suave")]
def theta_de(f):
    for a, ta, b, tb, tipo in TRAMOS:
        if a <= f <= b:
            u = (f - a) / max(1, b - a)
            u = suave(u) if tipo == "suave" else (1 - (1 - u) ** 2.2 if tipo == "salida" else u)
            return lerp(ta, tb, u)
    # rampa de velocidad y ralentí
    th = 1440.0
    for g in range(L3_VUELTAS + 1, f + 1):
        if g < RAMPA0: v = 6.0
        elif g < L4_SEG: v = lerp(10.0, 62.0, suave((g - RAMPA0) / max(1, L4_SEG - 12 - RAMPA0)))
        elif g < L4_TOCA + 12: v = lerp(62.0, 7.0, suave((g - L4_SEG) / max(1, L4_TOCA + 12 - L4_SEG)))
        else: v = 4.0
        th += v
    return th
THETA = {}
acum = None
for f in range(1, FIN + 1):
    if f <= L3_VUELTAS: THETA[f] = theta_de(f)
    else:
        if acum is None: acum = 1440.0
        g = f
        if g < RAMPA0: v = 6.0
        elif g < L4_SEG: v = lerp(10.0, 62.0, suave((g - RAMPA0) / max(1, L4_SEG - 12 - RAMPA0)))
        elif g < L4_TOCA + 12: v = lerp(62.0, 7.0, suave((g - L4_SEG) / max(1, L4_TOCA + 12 - L4_SEG)))
        else: v = 4.0
        acum += v; THETA[f] = acum
for f in range(1, FIN + 1): G["poner_angulo"](O, THETA[f], f)
for o in [O["cig"], O["bie"], O["pis"], O["gas"]] + list(O["valv"].values()) + list(O["leva"].values()) + [m[0] for m in O["muelle"].values()]:
    ad = o.animation_data
    if ad and ad.action:
        try: fcs = list(ad.action.fcurves)
        except Exception: fcs = [fc for l in ad.action.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
        for fc in fcs:
            for k in fc.keyframe_points: k.interpolation = 'LINEAR'

# ---------------- gas de la cámara (color y brillo de cada tiempo)
MIX, EM = O["M"]["_mezcla_nodos"]
AZUL, AZUL2, NARANJA, HUMO = (0.15, 0.50, 1.0), (0.30, 0.62, 1.0), (1.0, 0.36, 0.04), (0.45, 0.38, 0.32)
def gas(f):
    th = THETA[f]; ph = th % 720.0
    if f < F_ABRE + 20 or EXP0 - 4 <= f <= EXP3 + 2: return 0.0, AZUL, 0.0
    debil = 0.45 if f > L3_VUELTAS else 1.0
    if L2_CHISPA - 4 <= f < L2_EXPLOTA:
        u = suave((f - L2_CHISPA) / max(1, L2_EXPLOTA - L2_CHISPA)); return 0.7, tuple(lerp(a, b, u * 0.6) for a, b in zip(AZUL2, NARANJA)), lerp(1.3, 2.2, u)
    if L2_EXPLOTA <= f <= L2_ABAJO + 4:
        u = (f - L2_EXPLOTA) / max(1, L2_ABAJO + 4 - L2_EXPLOTA); return lerp(0.9, 0.6, u), NARANJA, lerp(3.2, 0.7, u ** 0.6)
    if ph < 180: return lerp(0.12, 0.42, ph / 180) * debil, AZUL, 1.3 * debil
    if ph < 360: return lerp(0.42, 0.65, (ph - 180) / 180) * debil, AZUL2, lerp(1.1, 1.4, (ph - 180) / 180) * debil
    if ph < 540: return lerp(0.85, 0.5, (ph - 360) / 180) * debil, NARANJA, lerp(3.5, 0.7, (ph - 360) / 180) * debil
    return lerp(0.45, 0.1, (ph - 540) / 180) * debil, HUMO, 0.6 * debil
for f in range(1, FIN + 1):
    m_, c_, s_ = gas(f)
    MIX.inputs[0].default_value = m_; MIX.inputs[0].keyframe_insert("default_value", frame=f)
    EM.inputs["Color"].default_value = (*c_, 1); EM.inputs["Color"].keyframe_insert("default_value", frame=f)
    EM.inputs["Strength"].default_value = s_; EM.inputs["Strength"].keyframe_insert("default_value", frame=f)

# ---------------- luz de la explosión, chispa y bola de fuego
def vis(o, f, v):
    o.hide_render = not v; o.hide_viewport = not v; o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)
dl = bpy.data.lights.new("MOT_LuzCamara", 'POINT'); dl.shadow_soft_size = 0.01; dl.color = (1.0, 0.55, 0.18)
lc = bpy.data.objects.new("MOT_LuzCamara", dl); cm.objects.link(lc); lc.parent = EXP["cul"]; lc.location = (0, -0.01, ZC + 0.004)
def kluz(f, e): dl.energy = e; dl.keyframe_insert("energy", frame=f)
kluz(1, 0); kluz(L2_EXPLOTA - 8, 0.15); kluz(L2_EXPLOTA, 6); kluz(L2_EXPLOTA + 8, 2.5); kluz(L2_ABAJO + 4, 0.1); kluz(L2_ABAJO + 10, 0)
f_ = RAMPA0
while f_ < L4_TOCA + 12:                                   # destellos durante la rampa (cada explosión)
    if THETA[f_] % 720 < 30 or (f_ > 1 and (THETA[f_] // 720) != (THETA[f_ - 1] // 720)): kluz(f_, 1.5); kluz(f_ + 1, 0.1)
    f_ += 1
kluz(L4_TOCA + 14, 0)
punta = O["electrodo_punta"] + Vector((0, 0, -0.0012))
M_CH = O["M"]["chispa"]
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.0011)
me = bpy.data.meshes.new("MOT_Chispa"); bm.to_mesh(me); bm.free(); me.materials.append(M_CH)
ch = bpy.data.objects.new("MOT_Chispa", me); cm.objects.link(ch); ch.parent = EXP["cul"]; ch.location = punta
vis(ch, 1, False)
for a, b in ((L2_CHISPA, L2_CHISPA + 3), (L2_CHISPA + 6, L2_CHISPA + 8), (L2_EXPLOTA - 6, L2_EXPLOTA - 2)): vis(ch, a, True); vis(ch, b, False)
ds = bpy.data.lights.new("MOT_LuzChispa", 'POINT'); ds.color = (0.6, 0.8, 1.0); ds.shadow_soft_size = 0.002
ls = bpy.data.objects.new("MOT_LuzChispa", ds); cm.objects.link(ls); ls.parent = EXP["cul"]; ls.location = punta
for f, e in ((1, 0), (L2_CHISPA - 1, 0), (L2_CHISPA, 1.2), (L2_CHISPA + 3, 0), (L2_CHISPA + 6, 0.9), (L2_CHISPA + 8, 0), (L2_EXPLOTA - 6, 1.0), (L2_EXPLOTA - 2, 0)):
    ds.energy = e; ds.keyframe_insert("energy", frame=f)
mf = bpy.data.materials.new("MOT_Fuego"); mf.use_nodes = True; nt = mf.node_tree; nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial"); mx = nt.nodes.new("ShaderNodeMixShader"); tr = nt.nodes.new("ShaderNodeBsdfTransparent")
em = nt.nodes.new("ShaderNodeEmission"); nz = nt.nodes.new("ShaderNodeTexNoise"); rp = nt.nodes.new("ShaderNodeValToRGB"); tc = nt.nodes.new("ShaderNodeTexCoord")
nz.inputs["Scale"].default_value = 180.0; nz.inputs["Detail"].default_value = 6.0
nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], rp.inputs["Fac"])
rp.color_ramp.elements[0].color = (1.0, 0.25, 0.03, 1); rp.color_ramp.elements[1].color = (1.0, 0.85, 0.45, 1)
nt.links.new(rp.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = 8.0
nt.links.new(nz.outputs["Fac"], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
nt.links.new(mx.outputs[0], out.inputs["Surface"])
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
me = bpy.data.meshes.new("MOT_Fuego"); bm.to_mesh(me); bm.free(); me.materials.append(mf)
fu = bpy.data.objects.new("MOT_Fuego", me); cm.objects.link(fu); fu.parent = EXP["cul"]; fu.location = punta
dsp = fu.modifiers.new("Llama", 'DISPLACE'); tx = bpy.data.textures.new("Llama", 'CLOUDS'); tx.noise_scale = 0.4; dsp.texture = tx; dsp.strength = 0.35
vis(fu, 1, False); vis(fu, L2_EXPLOTA - 14, True); vis(fu, L2_EXPLOTA + 16, False)
for f, s_ in ((L2_EXPLOTA - 14, 0.001), (L2_EXPLOTA - 2, 0.016), (L2_EXPLOTA + 2, 0.034), (L2_EXPLOTA + 10, 0.040), (L2_EXPLOTA + 16, 0.030)):
    fu.scale = (s_, s_ * 0.9, s_ * 0.55); fu.keyframe_insert("scale", frame=f)
for f, s_ in ((L2_EXPLOTA - 14, 2.5), (L2_EXPLOTA, 5.5), (L2_EXPLOTA + 10, 2.5), (L2_EXPLOTA + 16, 0.0)):
    em.inputs["Strength"].default_value = s_; em.inputs["Strength"].keyframe_insert("default_value", frame=f)

# ---------------- mezcla que entra (admisión) y gases que salen (escape)
rnd = random.Random(7)
def bolita(nombre, mat_, r):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=r)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free(); me.materials.append(mat_)
    o = bpy.data.objects.new(nombre, me); cm.objects.link(o); o.parent = RAIZ; return o
A_ADM, A_ESC = O["asiento"]["adm"], O["asiento"]["esc"]
for i in range(34):
    o = bolita(f"MOT_Mezcla_{i}", O["M"]["gas_adm"], rnd.uniform(0.0016, 0.0026))
    t0 = L1_BAJA - 6 + int(i * (L1_ADM - L1_BAJA - 10) / 34)
    p0 = Vector((-0.112, rnd.uniform(-0.008, 0.008), ZC + 0.028 + rnd.uniform(-0.007, 0.007)))
    p1 = Vector((-0.060, rnd.uniform(-0.007, 0.007), ZC + 0.030 + rnd.uniform(-0.005, 0.005)))
    p2 = A_ADM + Vector((rnd.uniform(-0.010, 0.008), rnd.uniform(-0.010, 0.010), -0.004))
    vis(o, 1, False); vis(o, t0, True)
    for f, p in ((t0, p0), (t0 + 8, p1), (t0 + 15, p2)): o.location = p; o.keyframe_insert("location", frame=f)
    for f in range(t0 + 18, L1_COMP + 1, 6):
        zp = G["piston_z"](THETA[f]) + G["COMP_H"]
        o.location = Vector((rnd.uniform(-0.034, 0.034), rnd.uniform(-0.034, 0.034), lerp(zp + 0.003, ZC + 0.006, rnd.random()))); o.keyframe_insert("location", frame=f)
    vis(o, L1_COMP - 4, False)
for i in range(30):
    o = bolita(f"MOT_Humo_{i}", O["M"]["gas_esc"], rnd.uniform(0.0018, 0.0030))
    t0 = L2_SUBIR + int(i * (L2_ESCAPE - L2_SUBIR - 8) / 30)
    zp = G["piston_z"](THETA[t0]) + G["COMP_H"]
    p0 = Vector((rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03), lerp(zp + 0.004, ZC + 0.004, rnd.random())))
    p1 = A_ESC + Vector((rnd.uniform(-0.006, 0.010), rnd.uniform(-0.010, 0.010), -0.003))
    p2 = Vector((0.065, rnd.uniform(-0.007, 0.007), ZC + 0.031 + rnd.uniform(-0.005, 0.005)))
    p3 = Vector((0.135, rnd.uniform(-0.010, 0.010), ZC + 0.028 + rnd.uniform(-0.008, 0.008)))
    vis(o, 1, False); vis(o, t0, True)
    for f, p in ((t0, p0), (t0 + 7, p1), (t0 + 14, p2), (t0 + 22, p3)): o.location = p; o.keyframe_insert("location", frame=f)
    vis(o, t0 + 22, False)

# ---------------- se abre el motor (las mitades de delante salen volando) y despiece suspendido
for k, o in enumerate(O["delante"]):
    f0 = F_ABRE + k * 2; o.keyframe_insert("location", frame=f0); o.keyframe_insert("rotation_euler", frame=f0)
    o.location = (rnd.uniform(-0.15, 0.15), -0.75, rnd.uniform(-0.05, 0.12)); o.rotation_euler = (rnd.uniform(-0.6, 0.6), 0, rnd.uniform(-0.8, 0.8))
    o.keyframe_insert("location", frame=f0 + 16); o.keyframe_insert("rotation_euler", frame=f0 + 16)
    vis(o, 1, True); vis(o, f0 + 15, False)
DESP = {"cul": ((0, -0.02, 0.17), (0, 0, 0.12)), "pis": ((0, -0.15, 0.10), (0, 0, 0.0)), "bie": ((0, -0.17, -0.02), (0, 0, 0.0)), "cig": ((0, -0.13, -0.16), (0, 0, 0.0))}
for k, (nm, (off, rot)) in enumerate(DESP.items()):
    e = EXP[nm]; a = EXP0 + k * 4
    for f in (1, a): e.location = (0, 0, 0); e.rotation_euler = (0, 0, 0); e.keyframe_insert("location", frame=f); e.keyframe_insert("rotation_euler", frame=f)
    e.location = off; e.rotation_euler = rot; e.keyframe_insert("location", frame=a + 22); e.keyframe_insert("rotation_euler", frame=a + 22)
    e.location = Vector(off) + Vector((0, 0, 0.012)); e.rotation_euler = (rot[0], rot[1], rot[2] - 0.25); e.keyframe_insert("location", frame=EXP2); e.keyframe_insert("rotation_euler", frame=EXP2)
    e.location = (0, 0, 0); e.rotation_euler = (0, 0, 0); e.keyframe_insert("location", frame=EXP3 - (3 - k) * 2); e.keyframe_insert("rotation_euler", frame=EXP3 - (3 - k) * 2)
vis(O["gas"], 1, True); vis(O["gas"], EXP0 - 4, False); vis(O["gas"], EXP3 + 2, True)
# el motor entero gira despacio sobre la peana en el gancho (presentación 360)
RAIZ.rotation_euler = (0, 0, math.radians(-35)); RAIZ.keyframe_insert("rotation_euler", frame=1)
RAIZ.rotation_euler = (0, 0, 0); RAIZ.keyframe_insert("rotation_euler", frame=F_ABRE - 4)

# ================================================================ PERSONAJES
def anexar(ruta, objetos=None, colecciones=None):
    with bpy.data.libraries.load(ruta, link=False) as (src, dst):
        if objetos: dst.objects = [n for n in src.objects if n in objetos or objetos == "*"]
        if colecciones: dst.collections = [n for n in src.collections if n in colecciones]
    return dst
# ---- Maite (Tripo, esqueleto Mixamo)
PM = os.path.join(LIB, "personajes", "tripo", "maite")
dst = anexar(os.path.join(PM, "maite_tripo.blend"), objetos="*")
cmai = bpy.data.collections.new("MAITE"); sc.collection.children.link(cmai)
for o in dst.objects:
    if o is not None and o.type in ("ARMATURE", "MESH"): cmai.objects.link(o)
for img in bpy.data.images:
    if img.source == 'FILE' and not img.packed_file:
        cand = os.path.join(PM, os.path.basename(bpy.path.abspath(img.filepath)))
        for raiz_, _d, fs in os.walk(PM):
            if os.path.basename(img.filepath) in fs: cand = os.path.join(raiz_, os.path.basename(img.filepath))
        try: img.filepath = cand; img.reload(); img.pack()
        except Exception as e: print("IMG", img.name, e)
MAITE = [o for o in cmai.objects if o.type == 'ARMATURE'][0]
MAITE.scale = (1.73, 1.73, 1.73); MAITE.location = (-0.64, 0.12, 0.0); MAITE.rotation_euler = (0, 0, math.radians(14))
sc.frame_set(1); bpy.context.view_layer.update()
PBm = MAITE.pose.bones
for pb in PBm: pb.rotation_mode = 'QUATERNION'
def dirigir(nombre, d_arm, f):
    """Gira el hueso para que apunte a la dirección d (espacio del esqueleto) y pone clave."""
    b = PBm.get(nombre)
    if not b: return
    bpy.context.view_layer.update()
    M_ = b.matrix.copy(); y = M_.col[1].xyz.normalized()
    q = y.rotation_difference(Vector(d_arm).normalized())
    b.matrix = Matrix.Translation(M_.translation) @ q.to_matrix().to_4x4() @ M_.to_3x3().to_4x4()
    bpy.context.view_layer.update(); b.keyframe_insert("rotation_quaternion", frame=f)
def girar(nombre, f, eje, grados):
    b = PBm.get(nombre)
    if not b: return
    b.rotation_quaternion = Quaternion(Vector(eje), math.radians(grados)); b.keyframe_insert("rotation_quaternion", frame=f)
def pose_base(f):
    for nm in ("mixamorig:Spine", "mixamorig:Spine1", "mixamorig:Spine2", "mixamorig:Neck", "mixamorig:Head", "mixamorig:LeftArm", "mixamorig:RightArm", "mixamorig:LeftForeArm", "mixamorig:RightForeArm", "mixamorig:LeftHand", "mixamorig:RightHand"):
        if nm in PBm: PBm[nm].rotation_quaternion = Quaternion(); PBm[nm].keyframe_insert("rotation_quaternion", frame=f)
    sc.frame_set(f); bpy.context.view_layer.update()
    dirigir("mixamorig:LeftArm", (0.30, 0.05, -0.95), f); dirigir("mixamorig:RightArm", (-0.30, 0.05, -0.95), f)
    dirigir("mixamorig:LeftForeArm", (0.20, -0.22, -0.95), f); dirigir("mixamorig:RightForeArm", (-0.20, -0.22, -0.95), f)
def gesto_explica(f, lado="Right", abre=1.0):
    s = 1 if lado == "Left" else -1
    sc.frame_set(f); bpy.context.view_layer.update()
    dirigir(f"mixamorig:{lado}Arm", (s * 0.38, -0.20, -0.90), f)
    dirigir(f"mixamorig:{lado}ForeArm", (s * 0.30, -0.80 * abre, 0.25 * abre - 0.4 * (1 - abre)), f)
def senala_motor(f):
    sc.frame_set(f); bpy.context.view_layer.update()
    dirigir("mixamorig:LeftArm", (0.92, -0.22, -0.22), f); dirigir("mixamorig:LeftForeArm", (0.96, -0.18, -0.10), f)
F1 = 1
pose_base(1)
for f in range(1, FIN + 1, 45):                         # respiración
    girar("mixamorig:Spine2", f, (1, 0, 0), 1.6 if (f // 45) % 2 else -0.4)
girar("mixamorig:Head", 1, (0, 1, 0), -4); girar("mixamorig:Head", FW(0, 3), (0, 1, 0), -8)
gesto_explica(FW(0, 0) + 4, "Right", 0.6); gesto_explica(FW(0, 3), "Right", 1.0); gesto_explica(FW(0, 8), "Right", 0.4)
senala_motor(F_ABRE - 12); girar("mixamorig:Head", F_ABRE - 10, (0, 1, 0), 22)
senala_motor(F_ABRE + 10); pose_base(F_ABRE + 40); girar("mixamorig:Head", F_ABRE + 40, (0, 1, 0), 16)
# cierre: a cámara, explica con las dos manos
pose_base(L4_TOCA + 10); girar("mixamorig:Head", L4_TOCA + 10, (0, 1, 0), -6)
gesto_explica(L5_TIRONES - 2, "Right", 0.8); gesto_explica(L5_TIEMBLA, "Right", 0.5); gesto_explica(L5_TIEMBLA, "Left", 0.4)
pose_base(L5_QUE - 6); gesto_explica(L5_QUE + 2, "Left", 1.0); gesto_explica(L5_QUE + 2, "Right", 1.0); pose_base(L5_FIN + 30)
for pb in PBm:
    ad = MAITE.animation_data
if MAITE.animation_data and MAITE.animation_data.action:
    a_ = MAITE.animation_data.action
    try: fcs = list(a_.fcurves)
    except Exception: fcs = [fc for l in a_.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
    for fc in fcs:
        for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'

# ---- Clod (no habla: gestos y cara)
PC = os.path.join(LIB, "personajes")
dst = anexar(os.path.join(PC, "clod", "clod_v2.blend"), colecciones=["CLOD_v2_personaje", "CLOD_v2_controles"])
for c_ in dst.collections:
    if c_ is not None: sc.collection.children.link(c_)
CA = {"__name__": "clod"}; exec(open(os.path.join(PC, "clod_anim.py"), encoding="utf-8").read(), CA)
CL = CA["ClodAnim"]()
CLOD_POS = Vector((0.27, 0.08, 0.860)); CLOD_GIRO = -35
CLOD_CERCA = Vector((0.15, -0.075, 0.860))
CL.reposo(1); CL.mover(1, tuple(CLOD_POS), CLOD_GIRO); CL.cara(1, "feliz"); CL.mirar(1, 0.0, 0.0)
def local_clod(p_mundo):
    return (CL.arm.matrix_world.inverted() @ Vector(p_mundo)) / CL.K
sc.frame_set(1); bpy.context.view_layer.update()
CL.cara(F_ABRE - 2, "contento"); CL.cara(F_ABRE + 4, "sorpresa"); CL.cuerpo(F_ABRE + 4, adelante=-8); CL.cuerpo(F_ABRE + 18, adelante=0); CL.cara(F_ABRE + 30, "feliz")
CL.cara(L2_EXPLOTA - 2, "contento"); CL.cara(L2_EXPLOTA + 2, "susto"); CL.aplastar(L2_EXPLOTA + 2, 0.92); CL.aplastar(L2_EXPLOTA + 10, 1.0); CL.cara(L2_EXPLOTA + 40, "contento")
# el gag: Clod mira la polea que gira cada vez más rápido y va a tocarla
POLEA = RAIZ.matrix_world @ Vector((0.034, -0.100, 0.020))
CL.mover(RAMPA0 + 6, tuple(CLOD_POS), CLOD_GIRO); CL.mover(RAMPA0 + 34, tuple(CLOD_CERCA), CLOD_GIRO - 15)
f_ = CL.rebote(RAMPA0 + 8, veces=3)
CL.mover(L5_TIRONES - 10, tuple(CLOD_CERCA), CLOD_GIRO - 15); CL.mover(L5_TIRONES + 20, tuple(CLOD_POS), CLOD_GIRO)
sc.frame_set(L4_CLOD - 40); bpy.context.view_layer.update()
CL.cara(RAMPA0, "contento"); CL.cara(RAMPA0 + 30, "sorpresa"); CL.mirar(RAMPA0 + 30, -0.35, -0.2)
CL.cabeza(RAMPA0 + 30, asiente=8, gira=12)
CL.brazo_caido("R", L4_CLOD - 40)
mano0 = local_clod(POLEA + Vector((0.07, -0.02, 0.02))); mano1 = local_clod(POLEA + Vector((0.012, -0.004, 0.004)))
CL.mano_en("R", L4_CLOD - 22, tuple(mano0)); CL.cara(L4_CLOD - 22, "duda")
CL.mano_en("R", L4_CLOD - 1, tuple(mano1)); CL.cuerpo(L4_CLOD - 1, adelante=12)
CL.brazo_caido("R", L4_CLOD + 5); CL.cuerpo(L4_CLOD + 5, adelante=-10); CL.cara(L4_CLOD + 2, "susto"); CL.aplastar(L4_CLOD + 3, 0.88); CL.aplastar(L4_CLOD + 10, 1.0)
CL.mirar(L4_CLOD + 4, 0.25, 0.1); CL.cabeza(L4_CLOD + 6, asiente=-4, gira=-18)
CL.cara(L4_CLOD + 18, "triste"); CL.cuerpo(L4_CLOD + 22, adelante=0); CL.cabeza(L4_TOCA + 4, asiente=6, gira=-10)
CL.cara(L5_TIRONES, "contento"); CL.mirar(L5_TIRONES, 0.0, 0.0); CL.cabeza(L5_TIRONES, 0, 0, 20)
f_ = CL.saludo("L", L5_QUE, ciclos=2); CL.cara(L5_QUE, "feliz")
CL.parpadeos(1, FIN, evitar=((L4_CLOD - 2, L4_CLOD + 20),)); CL.suavizar()

# ================================================================ CÁMARAS
cd = bpy.data.cameras.new("CAM"); cam = bpy.data.objects.new("CAM", cd); col.objects.link(cam); sc.camera = cam
cd.sensor_fit = 'AUTO'; cd.sensor_width = 36; cd.clip_start = 0.01
E = Vector((0, 0, 1.10))
PLANOS = [  # (desde, hasta, cam_ini, cam_fin, mira_ini, mira_fin, lente)
    (1, 62, (0.35, -2.55, 1.30), (0.30, -2.30, 1.27), (-0.18, 0, 1.10), (-0.15, 0, 1.10), 38),
    (63, 121, None, None, E, E, 50),
    (122, L1_BAJA - 1, (0.0, -0.92, 1.12), (0.0, -0.80, 1.12), (0, 0, 1.09), (0, 0, 1.09), 50),
    (L1_BAJA, L1_SUBE - 1, (-0.12, -0.46, 1.22), (-0.09, -0.40, 1.20), (-0.012, 0, 1.165), (-0.01, 0, 1.15), 50),
    (L1_SUBE, L1_COMP, (0.06, -0.48, 1.17), (0.04, -0.42, 1.19), (0, 0, 1.16), (0, 0, 1.175), 50),
    (L1_COMP + 1, L2_EXPLOTA - 1, (0.016, -0.33, 1.205), (0.008, -0.28, 1.198), (0, 0, 1.192), (0, 0, 1.192), 58),     # cámara de combustión entera: válvulas, bujía y pistón arriba
    (L2_EXPLOTA, L2_SUBIR - 1, (0.0, -0.66, 1.10), (0.0, -0.60, 1.10), (0, 0, 1.12), (0, 0, 1.12), 45),
    (L2_SUBIR, EXP0 - 1, (0.16, -0.52, 1.24), (0.13, -0.47, 1.22), (0.035, 0, 1.17), (0.035, 0, 1.17), 50),
    (EXP0, L3_CUATRO - 1, (-0.45, -0.80, 1.30), (-0.25, -0.88, 1.26), (0, -0.08, 1.10), (0, -0.08, 1.10), 40),
    (L3_CUATRO, RAMPA0 - 1, (0.0, -0.88, 1.10), (0.0, -0.80, 1.10), (0, 0, 1.07), (0, 0, 1.07), 50),
    (RAMPA0, L4_CLOD - 1, (-0.46, -0.82, 1.06), (-0.38, -0.74, 1.05), (0.04, -0.05, 1.04), (0.04, -0.05, 1.04), 35),
    (L4_CLOD, L4_TOCA + 18, (0.04, -0.62, 1.07), (0.05, -0.58, 1.06), (0.10, -0.07, 1.01), (0.10, -0.07, 1.01), 32),
    (L4_TOCA + 19, FIN, (-0.05, -2.05, 1.40), (-0.10, -1.85, 1.38), (-0.30, 0, 1.22), (-0.30, 0, 1.22), 42)]
CORTES = []
def ck(f, loc, mira, lente):
    cam.location = loc; cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cd.lens = lente; cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cd.keyframe_insert("lens", frame=f)
for a, b, c0, c1, m0, m1, le in PLANOS:
    CORTES.append(a)
    if c0 is None:                                      # órbita alrededor del motor
        for k in range(0, 5):
            f = int(lerp(a, b, k / 4)); u = k / 4
            ang = math.radians(lerp(-38, -8, suave(u))); rr = lerp(0.95, 0.80, u); h = lerp(1.30, 1.18, u)
            ck(f, (E.x + rr * math.sin(ang), E.y - rr * math.cos(ang), h), E, le)
    else:
        ck(a, c0, m0, le); ck(b, c1, m1, le)
CORTES.append(FIN + 1)
ad = cam.animation_data
fcs_cam = []
for ob in (cam, cd):
    a_ = ob.animation_data.action
    try: fcs_cam += list(a_.fcurves)
    except Exception: fcs_cam += [fc for l in a_.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
fin_plano = {c - 1 for c in CORTES[1:]}
for fc in fcs_cam:
    for k in fc.keyframe_points:
        k.interpolation = 'CONSTANT' if int(round(k.co[0])) in fin_plano else 'BEZIER'
        k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'

# ================================================================ RENDER (base; el 4K lo pone render_cycles_bg.py)
r = sc.render; r.engine = 'CYCLES'; sc.cycles.device = 'GPU'
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 1920, 100
r.use_motion_blur = True; r.motion_blur_shutter = 0.5
try: sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass

# ================================================================ ANCLAS PARA EL MONTAJE
NOMBRES = ["PISTON", "BIELA", "CIGUENAL", "VALV_ADM", "VALV_ESC", "LEVAS", "CAMARA", "BUJIA", "POLEA"]
anclas = {}
for f in range(1, FIN + 1):
    sc.frame_set(f); A = {}
    for nm in NOMBRES:
        o = bpy.data.objects.get("ANC_" + nm)
        if not o: continue
        p = world_to_camera_view(sc, cam, o.matrix_world.translation)
        if p.z > 0: A[nm] = [round(p.x, 4), round(p.y, 4)]
    cab = PBm.get("mixamorig:Head")
    if cab:
        p = world_to_camera_view(sc, cam, MAITE.matrix_world @ cab.head)
        if p.z > 0: A["MAITE"] = [round(p.x, 4), round(p.y, 4)]
    anclas[str(f)] = A
EV = {"B0": 122, "A2": L4_TOCA + 19, "INS": L4_TOCA + 19, "A3": L4_TOCA + 19, "CTA": L5_FIN + 4, "FIN": FIN, "F_ABRE": F_ABRE,
      "L1_BAJA": L1_BAJA, "L1_ADM": L1_ADM, "L1_SUBE": L1_SUBE, "L1_COMP": L1_COMP, "L2_CHISPA": L2_CHISPA, "L2_EXPLOTA": L2_EXPLOTA,
      "L2_ABAJO": L2_ABAJO, "L2_SUBIR": L2_SUBIR, "L2_ESCAPE": L2_ESCAPE, "EXP0": EXP0, "EXP3": EXP3, "L3_CUATRO": L3_CUATRO,
      "L3_VUELTAS": L3_VUELTAS, "RAMPA0": RAMPA0, "L4_SEG": L4_SEG, "L4_CLOD": L4_CLOD, "L4_TOCA": L4_TOCA, "L5_QUE": L5_QUE}
json.dump({"anclas": anclas, "cortes": CORTES, "fin": FIN, "eventos": EV}, open(os.path.join(os.path.dirname(SALIDA), "anclas_motor.json"), "w"))
bpy.ops.wm.save_as_mainfile(filepath=SALIDA)
print("ESCENA_OK", FIN, CORTES, EV)
