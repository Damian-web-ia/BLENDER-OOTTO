# EL TURBO POR DENTRO · Maite + Clod v3 · EKORUEDAS · 27-11-2026
# Skill "EKORUEDAS Automotive CGI 4K": estudio oscuro (azules fríos + reflejos cálidos), turbo real en corte seccional
# (biblioteca/turbo_real.py), funcionamiento por dentro (gases de escape que mueven la turbina y la ponen al rojo, aire
# que aspira el compresor y sale apretado), despiece vertical suspendido que gira y se vuelve a montar, macro de las
# ruedas, rampa de velocidad y foco de cine (lo pone el render). Maite explica (voz Renata); Clod v3 no habla.
# Diseño a 30 fps: el render 4K lo pasa a 60 fps.
# Uso: blender -b --factory-startup --python turbo.py -- <carpeta EKORUEDAS_ESTUDIO_3D> <salida.blend>
import bpy, bmesh, sys, os, math, json, random
from mathutils import Vector, Matrix, Euler, Quaternion
from bpy_extras.object_utils import world_to_camera_view
argv = sys.argv[sys.argv.index("--") + 1:]
R, SALIDA = argv[0], argv[1]
LIB = os.path.join(R, "biblioteca"); VID = os.path.join(R, "videos_3d", "turbo")
bpy.ops.wm.read_factory_settings(use_empty=True)
G = {"__name__": "tur"}; exec(open(os.path.join(LIB, "turbo_real.py"), encoding="utf-8").read(), G)
sc = bpy.context.scene; sc.render.fps = 30
FIN = 1189; sc.frame_start, sc.frame_end = 1, FIN
VOZ = json.load(open(os.path.join(VID, "voces_turbo.json"), encoding="utf-8"))
def F(t): return int(round(t * 30)) + 1
def FW(i, j, fin=False):
    l = VOZ["lineas"][i]; w = l["words"][j]; return F(l["at"] + (w[2] if fin else w[1]))
def lerp(a, b, u): return a + (b - a) * u
def suave(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
TAU = 2 * math.pi

col = bpy.data.collections.new("ESTUDIO"); sc.collection.children.link(col)
ct = bpy.data.collections.new("TURBO"); sc.collection.children.link(ct)

# ================================================================ ESTUDIO (el mismo del motor)
def malla(nombre, fn, mats, c=col):
    bm = bmesh.new(); fn(bm); me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me); c.objects.link(o)
    for m in mats: me.materials.append(m)
    return o
def mat(nombre, color, rugo=0.4, metal=0.0, emis=None, fuerza=0.0, coat=0.0, alfa=1.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rugo; b.inputs["Metallic"].default_value = metal
    if coat: b.inputs["Coat Weight"].default_value = coat
    if emis: b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = fuerza
    if alfa < 1.0: b.inputs["Alpha"].default_value = alfa
    return m
M_CICLO = mat("EST_Ciclorama", (0.010, 0.011, 0.014), rugo=0.32, coat=0.2)
M_PEANA = mat("EST_Peana", (0.020, 0.021, 0.024), rugo=0.28, metal=0.6, coat=0.5)
M_FILO = mat("EST_FiloLuz", (0.3, 0.6, 1.0), emis=(0.30, 0.62, 1.0), fuerza=9.0)
M_LINEA = mat("EST_LineaFondo", (0.2, 0.4, 0.9), emis=(0.18, 0.42, 1.0), fuerza=1.6)
M_SOPORTE = mat("EST_Soporte", (0.05, 0.05, 0.055), rugo=0.3, metal=1.0)
def ciclorama(bm):
    perfil = [(-6.0, 0.0), (1.2, 0.0)]
    for k in range(1, 17):
        a = math.pi / 2 * k / 16; perfil.append((1.2 + 1.0 * math.sin(a), 1.0 - 1.0 * math.cos(a)))
    perfil.append((2.2, 4.0))
    fila = [[bm.verts.new((x, y, z)) for y, z in perfil] for x in (-6.0, 6.0)]
    for i in range(len(perfil) - 1): bm.faces.new([fila[0][i], fila[1][i], fila[1][i + 1], fila[0][i + 1]])
cic = malla("EST_Ciclorama", ciclorama, [M_CICLO]); [setattr(p, "use_smooth", True) for p in cic.data.polygons]
def torno_z(bm, prof, seg=128):
    angs = [TAU * i / seg for i in range(seg)]; an = []
    for r_, z in prof: an.append([bm.verts.new((r_ * math.cos(a), r_ * math.sin(a), z)) for a in angs] if r_ > 1e-7 else [bm.verts.new((0, 0, z))])
    for ra, rb in zip(an, an[1:]):
        if len(ra) == 1:
            for j in range(seg): bm.faces.new((ra[0], rb[(j + 1) % seg], rb[j]))
        elif len(rb) == 1:
            for j in range(seg): bm.faces.new((ra[j], ra[(j + 1) % seg], rb[0]))
        else:
            for j in range(seg): bm.faces.new((ra[j], ra[(j + 1) % seg], rb[(j + 1) % seg], rb[j]))
pe = malla("EST_Peana", lambda bm: torno_z(bm, [(0.0, 0.0), (0.30, 0.0), (0.30, 0.845), (0.296, 0.856), (0.285, 0.86), (0.0, 0.86)]), [M_PEANA]); [setattr(p, "use_smooth", True) for p in pe.data.polygons]
malla("EST_FiloLuz", lambda bm: torno_z(bm, [(0.300, 0.853), (0.3035, 0.853), (0.3035, 0.857), (0.300, 0.857)], seg=128), [M_FILO])
for k, (x, z) in enumerate(((-1.6, 1.9), (-0.9, 2.4), (0.9, 2.4), (1.6, 1.9))):
    malla(f"EST_Linea_{k}", lambda bm, x=x, z=z: G["caja"](bm, x - 0.006, x + 0.006, 2.18, 2.19, z - 0.9, z + 0.9), [M_LINEA])
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.005, 0.008, 1)
def luz(nombre, loc, energia, tam, color, mira=(0, 0, 1.0), forma='RECTANGLE', tam_y=None, tipo='AREA'):
    d = bpy.data.lights.new(nombre, tipo); d.energy = energia; d.color = color
    if tipo == 'AREA': d.shape = forma; d.size = tam; d.size_y = tam_y if tam_y else tam
    o = bpy.data.objects.new(nombre, d); col.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
luz("Clave_calida", (-1.25, -1.55, 2.05), 100, 1.1, (1.0, 0.88, 0.76), tam_y=0.7)
luz("Contra_azul_izq", (-1.35, 1.10, 1.65), 190, 0.25, (0.45, 0.68, 1.0), tam_y=1.6)
luz("Contra_azul_der", (1.40, 1.05, 1.45), 190, 0.25, (0.45, 0.68, 1.0), tam_y=1.6)
luz("Cenital", (0.0, 0.1, 2.7), 45, 1.4, (0.92, 0.95, 1.0))
luz("Relleno_frio", (1.25, -1.75, 0.95), 22, 1.2, (0.75, 0.86, 1.0))
luz("Maite_clave", (-1.2, -1.6, 2.0), 55, 0.9, (1.0, 0.9, 0.8), mira=(-0.62, 0.1, 1.45))
luz("Turbo_clave", (0.55, -0.85, 1.45), 26, 0.5, (1.0, 0.95, 0.9), mira=(0, 0, 0.97))      # luz de producto para el metal
# soporte de exposición (columna fina bajo el retorno de aceite)
malla("EST_Columna", lambda bm: torno_z(bm, [(0.0, 0.860), (0.045, 0.860), (0.045, 0.866), (0.007, 0.870), (0.007, 0.917), (0.0, 0.917)], seg=64), [M_SOPORTE])

# ================================================================ TURBO
O = G["construir_turbo"](ct)
RAIZ = O["raiz"]; RAIZ.location = (0, 0, 0.96); RAIZ.rotation_mode = 'XYZ'
ROTOR = O["rotor"]
bpy.context.view_layer.update()
def grupo(nombre, hijos, padre=None):
    e = bpy.data.objects.new(nombre, None); ct.objects.link(e); e.parent = padre or RAIZ; e.empty_display_size = 0.03
    for h in hijos:
        mw = h.matrix_local.copy(); h.parent = e; h.matrix_parent_inverse = Matrix.Identity(4); h.matrix_local = mw
    return e
def ob(n): return bpy.data.objects[n]
det = {o.name: o for o in O["detras"]}
def por_nombre(claves, fuente):
    return [o for o in fuente if any(k in o.name for k in claves)]
todos = list(ct.objects)
EXP = {
    "comp_carc": grupo("EXP_CarcasaCompresor", por_nombre(("CarcasaCompresor", "CaracolaCompresor", "ContraplacaCompresor", "LabioEntrada"), O["detras"])),
    "rueda_comp": grupo("EXP_RuedaCompresor", list(O["rueda_comp"]), ROTOR),
    "tuerca": grupo("EXP_Tuerca", [ob("TUR_TuercaRueda")], ROTOR),
    "collar": grupo("EXP_Collar", [ob("TUR_CollarAxial")], ROTOR),
    "eje_turb": grupo("EXP_EjeTurbina", [O["eje"]] + list(O["rueda_turb"]), ROTOR),
    "axial": grupo("EXP_CojineteAxial", [ob("TUR_CojineteAxial")]),
    "casq1": grupo("EXP_Casquillo1", [ob("TUR_Casquillo1")]),
    "casq0": grupo("EXP_Casquillo0", [ob("TUR_Casquillo0")]),
    "escudo": grupo("EXP_Escudo", por_nombre(("EscudoTermico",), O["detras"])),
    "turb_carc": grupo("EXP_CarcasaTurbina", por_nombre(("CarcasaTurbina", "CaracolaTurbina", "BridaSalida", "BridaEntrada"), O["detras"]) +
                       [o for o in todos if o.name.startswith(("TUR_Esparrago", "TUR_TapaWastegate", "TUR_PalancaWastegate"))]),
    "actuador": grupo("EXP_Actuador", [o for o in todos if o.name.startswith(("TUR_Actuador", "TUR_SoporteActuador", "TUR_Varilla", "TUR_ManguitoPresion"))]),
}
for an, g in (("RUEDA_COMPRESOR", "rueda_comp"), ("RUEDA_TURBINA", "eje_turb"), ("EJE", "eje_turb"), ("COJINETES", "casq1"), ("CARCASA_COMPRESOR", "comp_carc"),
              ("CARCASA_TURBINA", "turb_carc"), ("WASTEGATE", "turb_carc"), ("ACTUADOR", "actuador")):
    a = ob("ANC_" + an); mw = a.matrix_local.copy(); a.parent = EXP[g]; a.matrix_local = mw

# ---------------- momentos (sincronizados con la voz de Maite)
E_ABRE = FW(0, 15) - 4                                   # "abrirla"
SOPLA0, SOPLA1 = FW(1, 12, True) + 2, FW(2, 4)         # Clod sopla en la boca del compresor (después de "eje")
L2_ESC = FW(2, 6)                                        # "mueven": entran los gases de escape
L2_ROJO = FW(2, 15, True)                                # "ardiendo": turbina al rojo
L3_COMP, L3_AIRE, L3_MAS = FW(3, 4), FW(3, 6), FW(3, 14)
L3_POT = FW(3, 17, True)
EXP0 = FW(4, 0) - 26                                      # empieza el despiece
L4_ACEITE = FW(4, 8)
EXP2 = FW(4, 8, True) + 18; EXP3 = EXP2 + 26             # vuelve a montarse
L5 = FW(5, 0); L5_ACEITE, L5_RALENTI, L5_QUE, L5_FIN = FW(5, 2), FW(5, 14), FW(5, 18), FW(5, 21, True)
print("MOMENTOS", E_ABRE, SOPLA0, SOPLA1, L2_ESC, L2_ROJO, L3_COMP, L3_MAS, EXP0, EXP2, EXP3, L5)

# ---------------- giro del rotor: velocidad (grados por fotograma de diseño) en cada momento
def omega(f):
    if f < SOPLA0 + 10: return 0.0
    if f < SOPLA0 + 40: return 2.2 * (1 - (f - SOPLA0 - 10) / 30.0)                # el soplido de Clod apenas lo mueve
    if f < L2_ESC: return 0.0
    if f < L2_ROJO: return 70.0 * suave((f - L2_ESC) / max(1, L2_ROJO - L2_ESC))
    if f < L3_MAS: return 70.0
    if f < L3_POT + 6: return lerp(70.0, 88.0, suave((f - L3_MAS) / max(1, L3_POT + 6 - L3_MAS)))
    if f < EXP0 - 4: return lerp(88.0, 0.0, suave((f - L3_POT - 6) / max(1, EXP0 - 4 - L3_POT - 6)))
    if f < EXP3 + 12: return 0.0
    return 9.0 * suave((f - EXP3 - 12) / 40.0)
TH = [0.0] * (FIN + 2)
for f in range(2, FIN + 2): TH[f] = TH[f - 1] + omega(f)
for f in range(1, FIN + 1): G["girar_rotor"](O, f, TH[f])
fcs = []
a_ = ROTOR.animation_data.action
try: fcs = list(a_.fcurves)
except Exception: fcs = [fc for l in a_.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
for fc in fcs:
    for k in fc.keyframe_points: k.interpolation = 'LINEAR'

# ---------------- calor de la turbina (al rojo con los gases) y su luz
for f, v in ((1, 0.0), (L2_ESC, 0.0), (L2_ROJO, 1.0), (EXP0 - 8, 1.0), (EXP0 + 18, 0.0)): G["calor"](O, f, v)
dl = bpy.data.lights.new("TUR_LuzCalor", 'POINT'); dl.color = (1.0, 0.42, 0.12); dl.shadow_soft_size = 0.03
lc = bpy.data.objects.new("TUR_LuzCalor", dl); ct.objects.link(lc); lc.parent = EXP["turb_carc"]; lc.location = (-0.055, 0.035, 0.0)
for f, e in ((1, 0.0), (L2_ESC, 0.0), (L2_ROJO, 3.5), (EXP0 - 8, 3.5), (EXP0 + 18, 0.0)): dl.energy = e; dl.keyframe_insert("energy", frame=f)
# aceite que brilla cuando Maite lo nombra
em_ace = O["M"]["aceite"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for f, v in ((1, 0.6), (L4_ACEITE - 12, 0.6), (L4_ACEITE, 4.0), (L4_ACEITE + 40, 4.0), (EXP2 + 10, 0.6)): em_ace.default_value = v; em_ace.keyframe_insert("default_value", frame=f)

# ---------------- flujo: aire que entra por el compresor y gases que atraviesan la turbina (bolitas brillantes)
rnd = random.Random(11)
def vis(o, f, v):
    o.hide_render = not v; o.hide_viewport = not v; o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)
def bolita(nombre, mat_, r):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=r)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free(); me.materials.append(mat_)
    o = bpy.data.objects.new(nombre, me); ct.objects.link(o); o.parent = RAIZ
    try: o.visible_shadow = False
    except Exception: pass
    return o
EJ_C = G["caracola"](bmesh.new(), 0.0345, 0.0330, 0.0045, 0.0165, math.radians(95), 0.93, 0.050, 1)
EJ_T = G["caracola"](bmesh.new(), -0.0540, 0.0310, 0.0050, 0.0165, math.radians(-85), 0.93, 0.040, -1)
NC = 120
def en_tubo(e, frac=0.6):
    c, rd, rt = e; a = rnd.uniform(0, TAU); rr = rt * frac * math.sqrt(rnd.random())
    return c + rr * (math.cos(a) * rd + math.sin(a) * Vector((1, 0, 0)))
def polar(x, r, a): return Vector((x, r * math.cos(a), r * math.sin(a)))
def camino(o, f0, puntos, paso):
    for k, p in enumerate(puntos):
        o.location = p; o.keyframe_insert("location", frame=f0 + int(round(k * paso)))
    return f0 + int(round((len(puntos) - 1) * paso))
# aire (azul): entra axial, la rueda lo lanza hacia fuera y la caracola lo lleva hasta la salida
for i in range(64):
    o = bolita(f"TUR_Aire_{i}", O["M"]["aire"], rnd.uniform(0.0022, 0.0032))
    f0 = L3_COMP - 16 + int(i * (EXP0 - 30 - (L3_COMP - 16)) / 64)
    u0 = rnd.uniform(0.04, 0.55); i0 = int(u0 * NC); phi = math.radians(95) + TAU * 0.93 * u0
    pts = [polar(0.17, rnd.uniform(0.0, 0.017), rnd.uniform(0, TAU)), polar(0.088, rnd.uniform(0.004, 0.017), phi - 1.6),
           polar(0.058, rnd.uniform(0.008, 0.016), phi - 1.1), polar(0.0345, 0.027, phi - 0.4)]
    for u in (u0 + (1 - u0) * k / 3 for k in range(4)):
        pts.append(en_tubo(EJ_C[min(NC, int(u * NC))], 0.55))
    pts += [en_tubo(EJ_C[-1], 0.5), EJ_C[-1][0] + (EJ_C[-1][0] - EJ_C[NC][0]).normalized() * 0.07]
    vis(o, 1, False); vis(o, f0, True); fin_ = camino(o, f0, pts, 3.2); vis(o, fin_, False)
# gases de escape (naranja): entran por la brida, recorren la caracola hacia dentro, empujan la rueda y salen por el eje
c_in, rd_in, _ = EJ_T[-1]; tg_in = (EJ_T[-1][0] - EJ_T[NC][0]).normalized()
for i in range(64):
    o = bolita(f"TUR_Escape_{i}", O["M"]["escape"], rnd.uniform(0.0024, 0.0034))
    f0 = L2_ESC - 8 + int(i * (EXP0 - 26 - (L2_ESC - 8)) / 64)
    u1 = rnd.uniform(0.08, 0.75); phi = math.radians(-85) - TAU * 0.93 * u1
    pts = [c_in + tg_in * 0.09 + Vector((rnd.uniform(-0.004, 0.004), 0, 0)), en_tubo(EJ_T[-1], 0.5)]
    for u in (1 - (1 - u1) * k / 3 for k in range(1, 4)):
        pts.append(en_tubo(EJ_T[min(NC, int(u * NC))], 0.55))
    pts += [polar(-0.049, 0.021, phi + 0.5), polar(-0.062, 0.013, phi + 1.4), polar(-0.085, rnd.uniform(0.006, 0.016), phi + 1.9),
            polar(-0.16, rnd.uniform(0.006, 0.02), phi + 2.1)]
    vis(o, 1, False); vis(o, f0, True); fin_ = camino(o, f0, pts, 2.6); vis(o, fin_, False)

# ---------------- se abre el turbo (las mitades de delante salen volando)
for k, o in enumerate(O["delante"]):
    f0 = E_ABRE + k % 6 * 2; o.keyframe_insert("location", frame=f0); o.keyframe_insert("rotation_euler", frame=f0)
    o.location = Vector(o.location) + Vector((rnd.uniform(-0.12, 0.12), -0.65, rnd.uniform(-0.04, 0.10))); o.rotation_euler = (rnd.uniform(-0.6, 0.6), 0, rnd.uniform(-0.8, 0.8))
    o.keyframe_insert("location", frame=f0 + 16); o.keyframe_insert("rotation_euler", frame=f0 + 16)
    vis(o, 1, True); vis(o, f0 + 15, False)
# presentación: el turbo gira despacio en el gancho
RAIZ.rotation_euler = (0, 0, math.radians(-38)); RAIZ.keyframe_insert("rotation_euler", frame=1); RAIZ.keyframe_insert("location", frame=1)
RAIZ.rotation_euler = (0, 0, 0); RAIZ.keyframe_insert("rotation_euler", frame=E_ABRE - 4)
# ---------------- despiece vertical: se levanta, se pone de pie, se separa, gira suspendido y se vuelve a montar
RAIZ.keyframe_insert("rotation_euler", frame=EXP0); RAIZ.location = (0, 0, 0.96); RAIZ.keyframe_insert("location", frame=EXP0)
RAIZ.rotation_euler = (0, math.radians(-90), 0); RAIZ.location = (0, 0, 1.20)
RAIZ.keyframe_insert("rotation_euler", frame=EXP0 + 22); RAIZ.keyframe_insert("location", frame=EXP0 + 22)
RAIZ.rotation_euler = (0, math.radians(-90), math.radians(40)); RAIZ.keyframe_insert("rotation_euler", frame=EXP2)
RAIZ.rotation_euler = (0, math.radians(-90), math.radians(50)); RAIZ.keyframe_insert("rotation_euler", frame=EXP3)
RAIZ.rotation_euler = (0, 0, 0); RAIZ.location = (0, 0, 0.96); RAIZ.keyframe_insert("rotation_euler", frame=EXP3 + 22); RAIZ.keyframe_insert("location", frame=EXP3 + 22)
DESP = [("comp_carc", (0.125, 0, 0)), ("tuerca", (0.108, 0, 0)), ("rueda_comp", (0.072, 0, 0)), ("collar", (0.050, 0, 0)), ("axial", (0.040, 0, 0)),
        ("casq1", (0.021, 0, 0)), ("casq0", (-0.030, 0, 0)), ("eje_turb", (-0.068, 0, 0)), ("escudo", (-0.094, 0, 0)), ("turb_carc", (-0.150, 0, 0)),
        ("actuador", (0.030, 0.0, 0.075))]
for k, (nm, off) in enumerate(DESP):
    e = EXP[nm]; a = EXP0 + 16 + k * 2
    for f in (1, a): e.location = (0, 0, 0); e.keyframe_insert("location", frame=f)
    e.location = off; e.keyframe_insert("location", frame=a + 20)
    e.location = Vector(off) * 1.04; e.keyframe_insert("location", frame=EXP2)
    e.location = (0, 0, 0); e.keyframe_insert("location", frame=EXP3 - (len(DESP) - 1 - k))
for nm in ("comp_carc", "turb_carc", "escudo", "actuador"):      # las carcasas giran un poco sobre sí mismas mientras están suspendidas
    e = EXP[nm]
    for f, r_ in ((EXP0 + 30, 0), (EXP2, 0.35 if nm != "actuador" else 0.0), (EXP3 - 4, 0)):
        e.rotation_euler = (r_, 0, 0); e.keyframe_insert("rotation_euler", frame=f)

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
def senala(f):
    sc.frame_set(f); bpy.context.view_layer.update()
    dirigir("mixamorig:LeftArm", (0.92, -0.22, -0.22), f); dirigir("mixamorig:LeftForeArm", (0.96, -0.18, -0.10), f)
pose_base(1)
for f in range(1, FIN + 1, 45):
    girar("mixamorig:Spine2", f, (1, 0, 0), 1.6 if (f // 45) % 2 else -0.4)
girar("mixamorig:Head", 1, (0, 1, 0), -4); girar("mixamorig:Head", FW(0, 5), (0, 1, 0), -8)
gesto_explica(FW(0, 0) + 4, "Right", 0.6); gesto_explica(FW(0, 8), "Right", 1.0); gesto_explica(FW(0, 12), "Right", 0.4)
senala(E_ABRE - 10); girar("mixamorig:Head", E_ABRE - 8, (0, 1, 0), 22)
senala(E_ABRE + 12); pose_base(E_ABRE + 40); girar("mixamorig:Head", E_ABRE + 40, (0, 1, 0), 16)
gesto_explica(FW(1, 4), "Left", 0.8); gesto_explica(FW(1, 7), "Left", 0.5); pose_base(FW(1, 12, True) + 6)
girar("mixamorig:Head", SOPLA1 - 14, (0, 1, 0), 30); gesto_explica(SOPLA1 - 6, "Left", 0.7)            # mira a Clod: "con soplar no basta"
girar("mixamorig:Head", L2_ESC + 4, (0, 1, 0), 18); senala(L2_ESC + 6); pose_base(L2_ROJO + 20)
gesto_explica(L3_COMP, "Right", 0.8); gesto_explica(L3_MAS, "Right", 1.0); gesto_explica(L3_MAS, "Left", 0.6); pose_base(L3_POT + 16)
girar("mixamorig:Head", EXP0, (0, 1, 0), 20); gesto_explica(L4_ACEITE - 6, "Left", 0.9); pose_base(EXP3)
girar("mixamorig:Head", L5 - 6, (0, 1, 0), -6)
gesto_explica(L5_ACEITE - 2, "Right", 0.8); gesto_explica(L5_RALENTI - 4, "Right", 0.5); gesto_explica(L5_RALENTI - 4, "Left", 0.4)
pose_base(L5_QUE - 6); gesto_explica(L5_QUE + 2, "Left", 1.0); gesto_explica(L5_QUE + 2, "Right", 1.0); pose_base(L5_FIN + 30)
if MAITE.animation_data and MAITE.animation_data.action:
    a_ = MAITE.animation_data.action
    try: fcs = list(a_.fcurves)
    except Exception: fcs = [fc for l in a_.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
    for fc in fcs:
        for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'

# ---- Clod v3 (no habla: gestos, cara y un soplido)
PC = os.path.join(LIB, "personajes")
dst = anexar(os.path.join(PC, "clod", "clod_v3.blend"), colecciones=["CLOD_v3_personaje", "CLOD_v3_controles"])
for c_ in dst.collections:
    if c_ is not None: sc.collection.children.link(c_)
CA = {"__name__": "clod"}; exec(open(os.path.join(PC, "clod_anim.py"), encoding="utf-8").read(), CA)
CL = CA["ClodAnim"]("CLOD_v3")
CLOD_POS = Vector((0.27, 0.08, 0.860)); CLOD_GIRO = -35
CLOD_SOPLA = Vector((0.185, -0.005, 0.860)); GIRO_SOPLA = -90
CL.reposo(1); CL.mover(1, tuple(CLOD_POS), CLOD_GIRO); CL.cara(1, "feliz"); CL.mirar(1, 0.0, 0.0)
sc.frame_set(1); bpy.context.view_layer.update()
CL.cara(E_ABRE - 2, "contento"); CL.cara(E_ABRE + 4, "sorpresa"); CL.cuerpo(E_ABRE + 4, adelante=-8); CL.cuerpo(E_ABRE + 18, adelante=0); CL.cara(E_ABRE + 30, "feliz")
# el gag: se acerca a la boca del compresor y sopla para hacerlo girar
CL.mover(FW(1, 0), tuple(CLOD_POS), CLOD_GIRO); CL.mover(FW(1, 0) + 6, tuple(CLOD_POS), 45)          # se gira hacia el turbo
f_ = CL.andar(FW(1, 0) + 6, pasos=3, zancada=0.125, fp=8, giro_z=45, desde=tuple(CLOD_POS))            # tres pasitos hasta la boca del compresor
CL.mover(f_ + 4, tuple(CLOD_SOPLA), 45); CL.mover(SOPLA0 - 4, tuple(CLOD_SOPLA), GIRO_SOPLA)
CL.cara(SOPLA0 - 4, "duda"); CL.cuerpo(SOPLA0, adelante=10); CL.cabeza(SOPLA0, asiente=8)
CL.aplastar(SOPLA0 + 2, 1.07); CL.cara(SOPLA0 + 4, "sorpresa")                   # coge aire (se hincha) y sopla con la boca en O
CL.aplastar(SOPLA0 + 16, 0.95); CL.aplastar(SOPLA0 + 26, 1.0)
CL.cara(SOPLA0 + 30, "contento"); CL.mirar(SOPLA0 + 30, -0.3, -0.2)
CL.cara(SOPLA1, "triste"); CL.cabeza(SOPLA1, asiente=14); CL.cuerpo(SOPLA1, adelante=0)
CL.mover(L2_ESC + 6, tuple(CLOD_SOPLA), GIRO_SOPLA)
CL.cara(L2_ESC + 8, "susto"); CL.aplastar(L2_ESC + 9, 0.9); CL.aplastar(L2_ESC + 14, 1.0); CL.cabeza(L2_ESC + 10, asiente=-4)
CL.mover(L2_ESC + 14, tuple(CLOD_SOPLA), -135)                                                          # se da la vuelta y vuelve a su sitio
f_ = CL.andar(L2_ESC + 14, pasos=3, zancada=0.125, fp=7, giro_z=-135, desde=tuple(CLOD_SOPLA))
CL.mover(f_ + 8, tuple(CLOD_POS), CLOD_GIRO)
CL.cara(L2_ROJO + 10, "sorpresa"); CL.mirar(L2_ROJO + 10, -0.4, 0.0)
CL.cara(L3_MAS, "feliz"); f_ = CL.rebote(L3_MAS, veces=2)
CL.cara(EXP0 + 10, "sorpresa"); CL.cabeza(EXP0 + 10, asiente=-10, gira=-8); CL.mirar(EXP0 + 10, -0.3, 0.4)
CL.cara(EXP3, "contento"); CL.cabeza(EXP3 + 6, 0, 0, 0); CL.mirar(EXP3 + 6, 0.0, 0.0)
f_ = CL.pulgar_arriba("R", L5_ACEITE) if hasattr(CL, "pulgar_arriba") else None
CL.cara(L5_ACEITE, "feliz")
f_ = CL.saludo("L", L5_QUE, ciclos=2); CL.cara(L5_QUE, "feliz")
CL.parpadeos(1, FIN, evitar=((SOPLA0, SOPLA0 + 26),)); CL.suavizar()
# soplido: bolitas translúcidas de la "boca" de Clod a la boca del compresor
M_SOP = mat("TUR_Soplido", (0.85, 0.92, 1.0), rugo=0.2, emis=(0.75, 0.88, 1.0), fuerza=1.2, alfa=0.35)
sc.frame_set(SOPLA0 + 6); bpy.context.view_layer.update()
boca = CL.arm.matrix_world @ (Vector((0.0, -0.19, 0.735)) * CL.K)
entrada = RAIZ.matrix_world @ Vector((0.088, 0, 0))
for i in range(10):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=rnd.uniform(0.003, 0.006))
    me = bpy.data.meshes.new(f"TUR_Soplido_{i}"); bm.to_mesh(me); bm.free(); me.materials.append(M_SOP)
    o = bpy.data.objects.new(f"TUR_Soplido_{i}", me); ct.objects.link(o)
    f0 = SOPLA0 + 5 + i * 2
    vis(o, 1, False); vis(o, f0, True)
    o.location = boca + Vector((rnd.uniform(-0.004, 0.004), rnd.uniform(-0.004, 0.004), rnd.uniform(-0.004, 0.004))); o.keyframe_insert("location", frame=f0)
    o.location = entrada + Vector((0.005, rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01))); o.keyframe_insert("location", frame=f0 + 12)
    vis(o, f0 + 12, False)

# ================================================================ CÁMARAS
cd = bpy.data.cameras.new("CAM"); cam = bpy.data.objects.new("CAM", cd); col.objects.link(cam); sc.camera = cam
cd.sensor_fit = 'AUTO'; cd.sensor_width = 36; cd.clip_start = 0.01
E = Vector((0, 0, 0.975))
P1 = F(2.3)
PLANOS = [  # (desde, hasta, cam_ini, cam_fin, mira_ini, mira_fin, lente)
    (1, P1, None, None, E, E, 50),                                                                         # órbita del turbo cerrado
    (P1 + 1, E_ABRE + 22, (0.30, -2.30, 1.26), (0.26, -2.10, 1.24), (-0.16, 0, 1.08), (-0.14, 0, 1.06), 40),   # Maite: "vamos a abrirla"
    (E_ABRE + 23, SOPLA0 - 1, (0.0, -0.60, 1.00), (0.0, -0.54, 0.995), E, E, 50),                          # corte: turbina, compresor, eje
    (SOPLA0, L2_ESC - 1, (-0.10, -0.31, 1.12), (-0.08, -0.28, 1.11), (0.13, 0.0, 1.03), (0.13, 0.0, 1.03), 32),  # Clod sopla (se le ve la cara)
    (L2_ESC, L2_ROJO + 24, (-0.23, -0.32, 1.02), (-0.19, -0.28, 1.00), (-0.05, 0, 0.97), (-0.05, 0, 0.97), 52),  # turbina al rojo
    (L2_ROJO + 25, L3_COMP - 1, (0.0, -0.66, 1.03), (0.0, -0.60, 1.01), E, E, 45),                         # todo girando
    (L3_COMP, L3_MAS - 1, (0.21, -0.23, 1.00), (0.18, -0.20, 0.99), (0.046, 0, 0.976), (0.046, 0, 0.976), 60),  # macro del compresor
    (L3_MAS, EXP0 - 1, (-0.12, -0.50, 0.93), (0.06, -0.45, 0.95), (0, 0, 0.985), (0, 0, 0.985), 34),      # rampa: más aire, más potencia
    (EXP0, EXP3, (0.0, -0.78, 1.21), (0.0, -0.72, 1.20), (0, 0, 1.20), (0, 0, 1.19), 45),                  # despiece vertical
    (EXP3 + 1, L5 - 1, (0.10, -0.70, 1.04), (0.06, -0.64, 1.02), E, E, 45),                                # vuelve a montarse
    (L5, FIN, (0.0, -2.45, 1.30), (-0.04, -2.30, 1.28), (-0.19, 0, 1.10), (-0.19, 0, 1.10), 38)]           # cierre con Maite y Clod
CORTES = []
def ck(f, loc, mira, lente):
    cam.location = loc; cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cd.lens = lente; cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cd.keyframe_insert("lens", frame=f)
for a, b, c0, c1, m0, m1, le in PLANOS:
    CORTES.append(a)
    if c0 is None:
        for k in range(0, 5):
            f = int(lerp(a, b, k / 4)); u = k / 4
            ang = math.radians(lerp(-48, -20, suave(u))); rr = lerp(0.62, 0.54, u); h = lerp(1.10, 1.03, u)
            ck(f, (E.x + rr * math.sin(ang), E.y - rr * math.cos(ang), h), E, le)
    else:
        ck(a, c0, m0, le); ck(b, c1, m1, le)
CORTES.append(FIN + 1)
fcs_cam = []
for ob_ in (cam, cd):
    a_ = ob_.animation_data.action
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
NOMBRES = ["RUEDA_COMPRESOR", "RUEDA_TURBINA", "EJE", "COJINETES", "ACEITE", "CARCASA_CENTRAL", "CARCASA_COMPRESOR", "CARCASA_TURBINA",
           "WASTEGATE", "ACTUADOR", "ENTRADA_AIRE", "SALIDA_AIRE", "ENTRADA_ESCAPE", "SALIDA_ESCAPE"]
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
EV = {"B0": E_ABRE + 23, "A2": L5, "INS": L5, "A3": L5, "E_ABRE": E_ABRE, "SOPLA0": SOPLA0, "SOPLA1": SOPLA1, "L2_ESC": L2_ESC, "L2_ROJO": L2_ROJO, "L3_COMP": L3_COMP, "L3_AIRE": L3_AIRE,
      "L3_MAS": L3_MAS, "L3_POT": L3_POT, "EXP0": EXP0, "L4_ACEITE": L4_ACEITE, "EXP2": EXP2, "EXP3": EXP3, "L5": L5, "L5_QUE": L5_QUE,
      "CTA": L5_FIN + 4, "FIN": FIN, "P1": P1}
json.dump({"anclas": anclas, "cortes": CORTES, "fin": FIN, "eventos": EV}, open(os.path.join(os.path.dirname(SALIDA), "anclas_turbo.json"), "w"))
bpy.ops.wm.save_as_mainfile(filepath=SALIDA)
print("ESCENA_OK", FIN, CORTES, EV)
