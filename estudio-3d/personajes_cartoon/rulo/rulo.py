# Rulo: personaje original de dibujos en 3D (estilo serie de animación), con rig flexible
# (brazos y piernas de goma con huesos B-Bone), pelo con físicas (Wiggle Bones) y una animación de prueba de 8 s.
# Se ejecuta dentro de Blender 5.x (MCP o blender -b --python). Variables opcionales: SALIDA_BLEND.
import bpy, bmesh, math
from mathutils import Vector, Matrix, Quaternion

FPS, FIN = 30, 240
SALIDA_BLEND = globals().get("SALIDA_BLEND")

def lin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)

# ------------------------------------------------------------------ escena vacía
bpy.ops.wm.read_homefile(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = FIN
for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try: sc.render.engine = eng; break
    except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.view_settings.view_transform = 'Standard'
try: sc.view_settings.look = 'None'
except Exception: pass
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
try: sc.eevee.taa_render_samples = 32
except Exception: pass
try: sc.eevee.use_raytracing = False
except Exception: pass
COL = sc.collection

# ------------------------------------------------------------------ materiales
MATS = {}
def mat_toon(nombre, hexc, sombra=(0.55, 0.55, 0.72), umbral=0.22):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    o = N.new('ShaderNodeOutputMaterial'); d = N.new('ShaderNodeBsdfDiffuse'); d.inputs['Color'].default_value = (1, 1, 1, 1)
    s = N.new('ShaderNodeShaderToRGB'); r = N.new('ShaderNodeValToRGB'); cr = r.color_ramp; cr.interpolation = 'CONSTANT'
    cr.elements[0].position = 0.0; cr.elements[0].color = tuple(sombra) + (1,)
    cr.elements[1].position = umbral; cr.elements[1].color = (1, 1, 1, 1)
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
    mx.inputs[6].default_value = lin(hexc)
    e = N.new('ShaderNodeEmission')
    L.new(d.outputs[0], s.inputs[0]); L.new(s.outputs['Color'], r.inputs['Fac'])
    L.new(r.outputs['Color'], mx.inputs[7]); L.new(mx.outputs[2], e.inputs['Color']); L.new(e.outputs[0], o.inputs['Surface'])
    MATS[nombre] = m; return m

def mat_plano(nombre, hexc, fuerza=1.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; N = m.node_tree.nodes; N.clear()
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = lin(hexc)
    e.inputs['Strength'].default_value = fuerza; m.node_tree.links.new(e.outputs[0], o.inputs['Surface'])
    MATS[nombre] = m; return m

M_PIEL = mat_toon("Piel", "#FFC39A")
M_PELO = mat_toon("Pelo", "#FF6F10", sombra=(0.62, 0.42, 0.45))
M_CAMISETA = mat_toon("Camiseta", "#E8332E")
M_PANTALON = mat_toon("Pantalon", "#23367A")
M_BLANCO = mat_toon("Blanco", "#F7F7F2", sombra=(0.70, 0.72, 0.85))
M_ZAPA = mat_toon("Zapatilla", "#1E5BFF")
M_SUELA = mat_toon("Suela", "#F2F2F2", sombra=(0.70, 0.72, 0.85))
M_NARIZ = mat_toon("Nariz", "#FF9472")
M_BOCA = mat_plano("Boca", "#5A0E1E")
M_LENGUA = mat_plano("Lengua", "#FF5F7A")
M_NEGRO = mat_plano("Negro", "#14101C")
M_BRILLO = mat_plano("Brillo", "#FFFFFF", 1.2)
M_ESTRELLA = mat_toon("Estrella", "#FFD23F")
M_GOMA = mat_toon("Goma", "#FFD23F")

M_CONT = bpy.data.materials.new("Contorno"); M_CONT.use_nodes = True
_N = M_CONT.node_tree.nodes; _N.clear(); _o = _N.new('ShaderNodeOutputMaterial'); _e = _N.new('ShaderNodeEmission')
_e.inputs['Color'].default_value = lin("#1A1224"); M_CONT.node_tree.links.new(_e.outputs[0], _o.inputs['Surface'])
M_CONT.use_backface_culling = True
try: M_CONT.use_backface_culling_shadow = True
except Exception: pass

# fondo: degradado (más claro detrás del personaje) con sombras de dibujo
def mat_fondo():
    m = bpy.data.materials.new("Fondo"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    o = N.new('ShaderNodeOutputMaterial'); d = N.new('ShaderNodeBsdfDiffuse'); s = N.new('ShaderNodeShaderToRGB')
    r = N.new('ShaderNodeValToRGB'); r.color_ramp.interpolation = 'CONSTANT'
    r.color_ramp.elements[0].color = (0.72, 0.72, 0.86, 1); r.color_ramp.elements[1].position = 0.18; r.color_ramp.elements[1].color = (1, 1, 1, 1)
    tc = N.new('ShaderNodeTexCoord'); vm = N.new('ShaderNodeVectorMath'); vm.operation = 'DISTANCE'; vm.inputs[1].default_value = (0, 2.0, 1.25)
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.4; mr.inputs['From Max'].default_value = 3.6
    mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
    c = N.new('ShaderNodeMix'); c.data_type = 'RGBA'; c.inputs[6].default_value = lin("#1FA7D6"); c.inputs[7].default_value = lin("#8FE6FF")
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
    e = N.new('ShaderNodeEmission')
    L.new(tc.outputs['Object'], vm.inputs[0]); L.new(vm.outputs['Value'], mr.inputs['Value']); L.new(mr.outputs['Result'], c.inputs[0])
    L.new(d.outputs[0], s.inputs[0]); L.new(s.outputs['Color'], r.inputs['Fac'])
    L.new(c.outputs[2], mx.inputs[6]); L.new(r.outputs['Color'], mx.inputs[7]); L.new(mx.outputs[2], e.inputs['Color'])
    L.new(e.outputs[0], o.inputs['Surface']); return m
M_FONDO = mat_fondo()

# ------------------------------------------------------------------ mallas
def nueva(nombre, verts, caras, mat, suave=True, origen=(0, 0, 0)):
    me = bpy.data.meshes.new(nombre)
    me.from_pydata([tuple(Vector(v) - Vector(origen)) for v in verts], [], caras); me.update(calc_edges=True)
    ob = bpy.data.objects.new(nombre, me); COL.objects.link(ob); ob.location = origen
    me.materials.append(mat)
    if suave: me.shade_smooth()
    return ob

def elipsoide(nombre, centro, radios, mat, u=40, v=24, rot=None):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    for vt in bm.verts: vt.co = Vector((vt.co.x * radios[0], vt.co.y * radios[1], vt.co.z * radios[2]))
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(nombre, me); COL.objects.link(ob); ob.location = centro
    if rot is not None: ob.rotation_mode = 'QUATERNION'; ob.rotation_quaternion = rot
    me.materials.append(mat); me.shade_smooth(); return ob

def toro(nombre, centro, R, r, mat, eje=(0, 0, 1), n=32, m=12):
    eje = Vector(eje).normalized(); q = Vector((0, 0, 1)).rotation_difference(eje)
    vs = []; fs = []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            p = Vector(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
            vs.append(Vector(centro) + q @ p)
    for i in range(n):
        for j in range(m):
            i2 = (i + 1) % n; j2 = (j + 1) % m
            fs.append((i * m + j, i * m + j2, i2 * m + j2, i2 * m + j))
    return nueva(nombre, vs, fs, mat, origen=centro)

def tubo(nombre, puntos, radios, mat, lados=12, aplanar=1.0):
    P = [Vector(p) for p in puntos]; Nn = len(P)
    T = [(P[min(i + 1, Nn - 1)] - P[max(i - 1, 0)]).normalized() for i in range(Nn)]
    up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    n = (up - T[0] * up.dot(T[0])).normalized(); fr = []
    for i in range(Nn):
        n = (n - T[i] * n.dot(T[i])).normalized(); fr.append((n.copy(), T[i].cross(n)))
    vs = []
    for i in range(Nn):
        a_, b_ = fr[i]
        for k in range(lados):
            a = 2 * math.pi * k / lados
            vs.append(P[i] + (a_ * math.cos(a) * aplanar + b_ * math.sin(a)) * radios[i])
    fs = []
    for i in range(Nn - 1):
        for k in range(lados):
            k2 = (k + 1) % lados
            fs.append((i * lados + k, i * lados + k2, (i + 1) * lados + k2, (i + 1) * lados + k))
    vs.append(P[0]); c0 = len(vs) - 1
    for k in range(lados): fs.append((c0, (k + 1) % lados, k))
    vs.append(P[-1]); c1 = len(vs) - 1
    for k in range(lados): fs.append(((Nn - 1) * lados + k, (Nn - 1) * lados + (k + 1) % lados, c1))
    return nueva(nombre, vs, fs, mat)

def torno(nombre, perfil, mat, seg=40, fy=0.86):
    vs = []; fs = []
    for z, r in perfil:
        for j in range(seg):
            a = 2 * math.pi * j / seg
            vs.append((r * math.cos(a), r * math.sin(a) * fy, z))
    for i in range(len(perfil) - 1):
        for j in range(seg):
            j2 = (j + 1) % seg
            fs.append((i * seg + j, i * seg + j2, (i + 1) * seg + j2, (i + 1) * seg + j))
    return nueva(nombre, vs, fs, mat)

def contorno(ob, grosor=0.007, grupo=None):
    ob.data.materials.append(M_CONT)
    md = ob.modifiers.new("Contorno", 'SOLIDIFY'); md.thickness = grosor; md.offset = 1.0
    md.use_flip_normals = True; md.use_rim = False; md.material_offset = len(ob.data.materials) - 1
    try: md.use_quality_normals = True
    except Exception: pass
    if grupo: md.vertex_group = grupo; md.thickness_vertex_group = 0.25
    return md

def bez(p, t):
    if len(p) == 3: return p[0] * (1 - t) ** 2 + p[1] * 2 * (1 - t) * t + p[2] * t * t
    return p[0] * (1 - t) ** 3 + p[1] * 3 * (1 - t) ** 2 * t + p[2] * 3 * (1 - t) * t * t + p[3] * t ** 3

# ------------------------------------------------------------------ cabeza (centro y radios)
C = Vector((0, 0, 1.30)); RA, RB, RC = 0.34, 0.32, 0.36
def en_cabeza(d, fuera=0.0):
    d = Vector(d).normalized()
    t = 1.0 / math.sqrt((d.x / RA) ** 2 + (d.y / RB) ** 2 + (d.z / RC) ** 2)
    p = C + d * t
    n = Vector(((p.x - C.x) / RA ** 2, (p.y - C.y) / RB ** 2, (p.z - C.z) / RC ** 2)).normalized()
    return p + n * fuera, n

RIGIDOS = []   # (objeto, hueso)
cabeza = elipsoide("Cabeza", C, (RA, RB, RC), M_PIEL, 56, 36); contorno(cabeza, 0.008); RIGIDOS.append((cabeza, "cabeza"))
for s in (1, -1):
    p, n = en_cabeza((s, 0.05, -0.08), -0.02)
    o = elipsoide(f"Oreja.{'L' if s > 0 else 'R'}", p, (0.045, 0.06, 0.075), M_PIEL, 24, 16); contorno(o, 0.006); RIGIDOS.append((o, "cabeza"))

# casquete de pelo con borde en zigzag
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=40, radius=1.0)
quitar = []
for vt in bm.verts:
    ux, uy, uz = vt.co
    ang = math.atan2(ux, -uy)
    umbral = 0.10 - 0.45 * uy + (0.05 * (abs(((ang * 7 / math.pi) % 2) - 1) - 0.5) if uy < 0.2 else 0.0)
    if uz < umbral: quitar.append(vt)
bmesh.ops.delete(bm, geom=quitar, context='VERTS')
for vt in bm.verts: vt.co = Vector((vt.co.x * RA * 1.05, vt.co.y * RB * 1.05, vt.co.z * RC * 1.05))
me = bpy.data.meshes.new("PeloCasquete"); bm.to_mesh(me); bm.free()
casq = bpy.data.objects.new("PeloCasquete", me); COL.objects.link(casq); casq.location = C
me.materials.append(M_PELO); me.shade_smooth(); contorno(casq, 0.007); RIGIDOS.append((casq, "cabeza"))

# ojos (blanco + pupila + brillo); el parpadeo escala el blanco (y lo que cuelga de él)
OJOS = {}
for s in (1, -1):
    lado = 'L' if s > 0 else 'R'
    p, n = en_cabeza((0.30 * s, -1, 0.17), -0.03)
    q = Vector((0, -1, 0)).rotation_difference(n)
    ojo = elipsoide(f"Ojo.{lado}", p, (0.088, 0.06, 0.122), M_BLANCO, 32, 20, rot=q); contorno(ojo, 0.006)
    pup = elipsoide(f"Pupila.{lado}", (0, 0, 0), (0.04, 0.022, 0.052), M_NEGRO, 24, 16); pup.parent = ojo; pup.location = (-0.012 * s, -0.047, -0.004)
    bri = elipsoide(f"Brillo.{lado}", (0, 0, 0), (0.013, 0.008, 0.016), M_BRILLO, 12, 8); bri.parent = pup; bri.location = (0.012, -0.018, 0.022)
    OJOS[lado] = (ojo, pup); RIGIDOS.append((ojo, "cabeza"))
    # ceja
    pts = []
    for t in (0.0, 0.5, 1.0):
        pc, nc = en_cabeza((0.30 * s + (t - 0.5) * 0.30, -1, 0.62 - 0.12 * abs(t - 0.5)), 0.012)
        pts.append(pc)
    ceja = tubo(f"Ceja.{lado}", [bez(pts, i / 10) for i in range(11)], [0.016 * (0.6 + 0.4 * math.sin(math.pi * i / 10)) for i in range(11)], M_NEGRO, 8)
    RIGIDOS.append((ceja, "cabeza")); OJOS[lado] = OJOS[lado] + (ceja,)

# nariz
p, n = en_cabeza((0, -1, -0.02), 0.012)
nariz = elipsoide("Nariz", p, (0.05, 0.045, 0.042), M_NARIZ, 24, 16); contorno(nariz, 0.006); RIGIDOS.append((nariz, "cabeza"))

# boca: sonrisa abierta en forma de D, pegada a la cara, con dientes y lengua
pm, nm = en_cabeza((0, -1, -0.40), 0.0)
U = Vector((1, 0, 0)); Vv = nm.cross(U).normalized()
if Vv.z < 0: Vv = -Vv
def proyecta(u, v, fuera):
    q = pm + U * u + Vv * v
    p2, n2 = en_cabeza(q - C, fuera); return p2
def forma(nombre, contorno2d, mat, fuera):
    vs = [proyecta(u, v, fuera) for u, v in contorno2d]
    cx = sum(u for u, v in contorno2d) / len(contorno2d); cy = sum(v for u, v in contorno2d) / len(contorno2d)
    vs.append(proyecta(cx, cy, fuera)); c = len(vs) - 1
    fs = [(c, i, (i + 1) % (len(vs) - 1)) for i in range(len(vs) - 1)]
    ob = nueva(nombre, vs, fs, mat, suave=True, origen=pm)
    if ob.data.polygons[0].normal.dot(nm) < 0:
        for pl in ob.data.polygons: pl.flip()
    return ob
W2, H2 = 0.115, 0.10
boca2d = [(W2 * (2 * i / 20 - 1), 0.018 * (2 * i / 20 - 1) ** 2) for i in range(21)] + \
         [(W2 * math.cos(math.pi * i / 20), -H2 * math.sin(math.pi * i / 20)) for i in range(1, 20)]
boca = forma("Boca", boca2d, M_BOCA, 0.003)
dientes = forma("Dientes", [(W2 * 0.86 * (2 * i / 12 - 1), 0.012 * (2 * i / 12 - 1) ** 2 - 0.004) for i in range(13)] +
                [(W2 * 0.80 * (1 - 2 * i / 12), -0.030) for i in range(13)], M_BLANCO, 0.005)
lengua = forma("Lengua", [(0.05 * math.cos(2 * math.pi * i / 24), -0.072 + 0.022 * math.sin(2 * math.pi * i / 24)) for i in range(24)], M_LENGUA, 0.0055)
for o in (dientes, lengua): o.parent = boca; o.matrix_parent_inverse = Matrix.Identity(4); o.location = (0, 0, 0)
RIGIDOS.append((boca, "cabeza"))

# mechones de pelo: (raíz, control1, control2, punta, radio)
MECHONES = [
    ((0, -0.13, 1.60), (0, -0.30, 1.86), (0, -0.50, 1.86), (0, -0.46, 1.70), 0.085),      # tupé que se riza hacia delante
    ((-0.12, -0.06, 1.62), (-0.20, -0.20, 1.88), (-0.32, -0.26, 1.90), (-0.40, -0.22, 1.80), 0.072),
    ((0.12, -0.06, 1.62), (0.20, -0.20, 1.88), (0.32, -0.26, 1.90), (0.40, -0.22, 1.80), 0.072),
    ((0, 0.10, 1.63), (0, 0.12, 1.86), (0, 0.24, 1.98), (0, 0.36, 1.96), 0.08),
    ((-0.16, 0.10, 1.57), (-0.28, 0.12, 1.76), (-0.40, 0.18, 1.84), (-0.48, 0.26, 1.80), 0.068),
    ((0.16, 0.10, 1.57), (0.28, 0.12, 1.76), (0.40, 0.18, 1.84), (0.48, 0.26, 1.80), 0.068),
    ((-0.28, 0.02, 1.47), (-0.40, 0.00, 1.55), (-0.50, 0.02, 1.52), (-0.55, 0.06, 1.42), 0.058),
    ((0.28, 0.02, 1.47), (0.40, 0.00, 1.55), (0.50, 0.02, 1.52), (0.55, 0.06, 1.42), 0.058),
    ((0, 0.30, 1.47), (0, 0.48, 1.52), (0, 0.62, 1.40), (0, 0.66, 1.18), 0.072),           # coleta
    ((-0.18, 0.25, 1.40), (-0.26, 0.40, 1.40), (-0.32, 0.46, 1.30), (-0.32, 0.50, 1.16), 0.055),
    ((0.18, 0.25, 1.40), (0.26, 0.40, 1.40), (0.32, 0.46, 1.30), (0.32, 0.50, 1.16), 0.055),
]
NANILLOS = 22
def radio_mechon(r0, t): return max(0.003, r0 * (0.6 + 2 * t) * (1 - t) / 0.85)

# ------------------------------------------------------------------ cuerpo
torso = torno("Torso", [(0.46, 0.0), (0.465, 0.15), (0.50, 0.20), (0.62, 0.205), (0.75, 0.19), (0.88, 0.165), (0.96, 0.12), (0.995, 0.0)], M_CAMISETA)
contorno(torso, 0.007)
pantalon = torno("Pantalon", [(0.38, 0.0), (0.385, 0.17), (0.41, 0.212), (0.55, 0.215), (0.60, 0.208), (0.605, 0.0)], M_PANTALON)
contorno(pantalon, 0.007)
# estrella en el pecho
st = []
for i in range(10):
    a = math.pi / 2 + i * math.pi / 5; r = 0.07 if i % 2 == 0 else 0.03
    st.append((r * math.cos(a), r * math.sin(a)))
z0 = 0.80; vs = [];
for u, v in st:
    z = z0 + v; rr = 0.18 - 0.01 * (z - 0.75) / 0.2
    ang = u / rr; vs.append((rr * math.sin(ang), -rr * math.cos(ang) * 0.86 - 0.004, z))
vs.append((0, -0.178 * 0.86 - 0.004, z0)); c = len(vs) - 1
estrella = nueva("Estrella", vs, [(c, i, (i + 1) % 10) for i in range(10)], M_ESTRELLA)
if estrella.data.polygons[0].normal.y > 0:
    for pl in estrella.data.polygons: pl.flip()

# ------------------------------------------------------------------ esqueleto
arm_d = bpy.data.armatures.new("Rig_Rulo"); RIG = bpy.data.objects.new("Rig_Rulo", arm_d); COL.objects.link(RIG)
arm_d.display_type = 'BBONE'
bpy.context.view_layer.objects.active = RIG; RIG.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
EB = arm_d.edit_bones
def hueso(n, h, t, padre=None, con=False, segs=1):
    b = EB.new(n); b.head = h; b.tail = t
    if padre: b.parent = EB[padre]; b.use_connect = con
    b.bbone_segments = segs
    if segs > 1:
        try: b.bbone_handle_type_start = 'AUTO'; b.bbone_handle_type_end = 'AUTO'
        except Exception: pass
    return b
hueso("raiz", (0, 0, 0), (0, 0, 0.25))
hueso("cadera", (0, 0, 0.50), (0, 0, 0.62), "raiz")
hueso("columna", (0, 0, 0.62), (0, 0, 0.78), "cadera", True, 4)
hueso("pecho", (0, 0, 0.78), (0, 0, 0.96), "columna", True, 4)
hueso("cuello", (0, 0, 0.96), (0, 0, 1.04), "pecho", True)
hueso("cabeza", (0, 0, 1.04), (0, 0, 1.62), "cuello", True)
for s, L in ((1, "L"), (-1, "R")):
    hueso(f"brazo_sup.{L}", (0.19 * s, 0, 0.90), (0.27 * s, 0.005, 0.69), "pecho", False, 8)
    hueso(f"brazo_inf.{L}", (0.27 * s, 0.005, 0.69), (0.31 * s, -0.005, 0.48), f"brazo_sup.{L}", True, 8)
    hueso(f"mano.{L}", (0.31 * s, -0.005, 0.48), (0.32 * s, -0.01, 0.38), f"brazo_inf.{L}", True)
    hueso(f"muslo.{L}", (0.10 * s, 0, 0.52), (0.11 * s, -0.01, 0.32), "cadera", False, 8)
    hueso(f"pierna.{L}", (0.11 * s, -0.01, 0.32), (0.12 * s, 0, 0.12), f"muslo.{L}", True, 8)
    hueso(f"pie.{L}", (0.12 * s, 0, 0.12), (0.12 * s, -0.14, 0.06), f"pierna.{L}", True)
MECH_HUESOS = []
for i, (a, b1, b2, cc, r0) in enumerate(MECHONES):
    pts = [Vector(a), Vector(b1), Vector(b2), Vector(cc)]
    ks = [bez(pts, t) for t in (0, 1 / 3, 2 / 3, 1)]
    nombres = []
    for j in range(3):
        n = f"pelo{i:02d}_{j}"
        hueso(n, ks[j], ks[j + 1], "cabeza" if j == 0 else f"pelo{i:02d}_{j - 1}", j > 0)
        nombres.append(n)
    MECH_HUESOS.append(nombres)
bpy.ops.object.mode_set(mode='OBJECT')

# ------------------------------------------------------------------ pieles (deformación)
def deformado(ob, grupos):
    ob.parent = RIG; ob.matrix_parent_inverse = Matrix.Identity(4)
    for g, pesos in grupos.items():
        vg = ob.vertex_groups.new(name=g)
        for idx, w in pesos:
            if w > 0.001: vg.add([idx], w, 'REPLACE')
    md = ob.modifiers.new("Armature", 'ARMATURE'); md.object = RIG
    # el contorno va DESPUÉS de la deformación
    for m in list(ob.modifiers):
        if m.type == 'SOLIDIFY':
            ob.modifiers.remove(m); contorno_tmp = True
            break
    else:
        contorno_tmp = False
    return contorno_tmp

def suave(x, a, b):
    t = min(1.0, max(0.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

def pesar_altura(ob, tramos):
    vs = [ob.matrix_world @ v.co for v in ob.data.vertices]; G = {}
    for i, p in enumerate(vs):
        ws = tramos(p.z)
        for g, w in ws.items(): G.setdefault(g, []).append((i, w))
    return G

def tramo_cuerpo(z):
    a = 1 - suave(z, 0.58, 0.66); c = suave(z, 0.74, 0.82); b = max(0.0, 1 - a - c)
    return {"cadera": a, "columna": b, "pecho": c}
for ob, gr in ((torso, 0.007), (pantalon, 0.007)):
    tenia = deformado(ob, pesar_altura(ob, tramo_cuerpo if ob is torso else (lambda z: {"cadera": 1.0})))
    if tenia: contorno(ob, gr)
deformado(estrella, {"pecho": [(i, 1.0) for i in range(len(estrella.data.vertices))]})

def extremidad(nombre, a, b, c, radio, mat, h1, h2, puntas=None):
    pts = [Vector(a), Vector(b), Vector(c)]; n = 24
    P = [];  T = []
    for i in range(n + 1):
        t = i / n
        P.append(pts[0] + (pts[1] - pts[0]) * (t * 2) if t <= 0.5 else pts[1] + (pts[2] - pts[1]) * ((t - 0.5) * 2)); T.append(t)
    rs = [radio * (1.0 - 0.12 * t) for t in T]
    ob = tubo(nombre, P, rs, mat, 12)
    lados = 12; G = {h1: [], h2: []}
    for i, t in enumerate(T):
        w2 = suave(t, 0.42, 0.58)
        for k in range(lados):
            G[h1].append((i * lados + k, 1 - w2)); G[h2].append((i * lados + k, w2))
    G[h1].append((len(P) * lados, 1.0)); G[h2].append((len(P) * lados + 1, 1.0))
    deformado(ob, G); contorno(ob, 0.006); return ob

for s, L in ((1, "L"), (-1, "R")):
    extremidad(f"Brazo.{L}", (0.17 * s, 0, 0.90), (0.27 * s, 0.005, 0.69), (0.31 * s, -0.005, 0.48), 0.034, M_PIEL, f"brazo_sup.{L}", f"brazo_inf.{L}")
    manga = tubo(f"Manga.{L}", [Vector((0.15 * s, 0, 0.92)) + (Vector((0.27 * s, 0.005, 0.69)) - Vector((0.19 * s, 0, 0.90))) * (i / 6) * 0.55 for i in range(7)],
                 [0.068 - 0.006 * i / 6 for i in range(7)], M_CAMISETA, 16)
    deformado(manga, {f"brazo_sup.{L}": [(i, 1.0) for i in range(len(manga.data.vertices))]}); contorno(manga, 0.006)
    extremidad(f"Pierna.{L}", (0.10 * s, 0, 0.50), (0.11 * s, -0.01, 0.32), (0.12 * s, 0, 0.12), 0.04, M_PIEL, f"muslo.{L}", f"pierna.{L}")
    calcetin = tubo(f"Calcetin.{L}", [Vector((0.12 * s, 0, 0.11)) + Vector((-0.01 * s, -0.01, 0.20)) * (i / 5) * 0.55 for i in range(6)], [0.047] * 6, M_BLANCO, 14)
    deformado(calcetin, {f"pierna.{L}": [(i, 1.0) for i in range(len(calcetin.data.vertices))]}); contorno(calcetin, 0.006)
    # guante y zapatilla (rígidos)
    mu = Vector((0.31 * s, -0.005, 0.48))
    puno = toro(f"Puno.{L}", mu + Vector((0, 0, -0.005)), 0.042, 0.018, M_BLANCO, eje=(0.04 * s, -0.01, -0.21)); contorno(puno, 0.005)
    palma = elipsoide(f"Mano.{L}", mu + Vector((0.006 * s, -0.005, -0.075)), (0.036, 0.058, 0.07), M_BLANCO, 28, 18); contorno(palma, 0.006)
    pulgar = elipsoide(f"Pulgar.{L}", mu + Vector((0.0, -0.058, -0.05)), (0.02, 0.022, 0.04), M_BLANCO, 16, 12,
                       rot=Quaternion((1, 0, 0), math.radians(-35))); contorno(pulgar, 0.005)
    for o in (puno, palma, pulgar): RIGIDOS.append((o, f"mano.{L}"))
    zap = elipsoide(f"Zapatilla.{L}", (0.125 * s, -0.06, 0.082), (0.088, 0.155, 0.072), M_ZAPA, 32, 20); contorno(zap, 0.007)
    suela = elipsoide(f"Suela.{L}", (0.125 * s, -0.06, 0.032), (0.095, 0.165, 0.034), M_SUELA, 32, 14); contorno(suela, 0.006)
    for o in (zap, suela): RIGIDOS.append((o, f"pie.{L}"))

# mechones (con pesos a sus 3 huesos) + goma de la coleta
for i, (a, b1, b2, cc, r0) in enumerate(MECHONES):
    pts = [Vector(a), Vector(b1), Vector(b2), Vector(cc)]
    T = [k / (NANILLOS - 1) for k in range(NANILLOS)]
    ob = tubo(f"Mechon{i:02d}", [bez(pts, t) for t in T], [radio_mechon(r0, t) for t in T], M_PELO, 10, aplanar=0.8)
    lados = 10; G = {h: [] for h in MECH_HUESOS[i]}; G["grosor"] = []
    for k, t in enumerate(T):
        cs = [(j + 0.5) / 3 for j in range(3)]
        ws = [max(0.0, 1 - abs(t - c_) * 3) for c_ in cs]
        if t <= cs[0]: ws = [1, 0, 0]
        if t >= cs[2]: ws = [0, 0, 1]
        sw = sum(ws); ws = [w / sw for w in ws]
        for kk in range(lados):
            for j in range(3): G[MECH_HUESOS[i][j]].append((k * lados + kk, ws[j]))
            G["grosor"].append((k * lados + kk, 0.25 + 0.75 * (1 - t)))
    nv = len(ob.data.vertices)
    G[MECH_HUESOS[i][0]].append((nv - 2, 1.0)); G[MECH_HUESOS[i][2]].append((nv - 1, 1.0))
    G["grosor"] += [(nv - 2, 1.0), (nv - 1, 0.25)]
    deformado(ob, G); contorno(ob, 0.007, "grosor")
goma = toro("GomaColeta", (0, 0.33, 1.475), 0.05, 0.02, M_GOMA, eje=(0, 1, 0.25)); contorno(goma, 0.005); RIGIDOS.append((goma, "cabeza"))

# ------------------------------------------------------------------ piezas rígidas a sus huesos
bpy.context.view_layer.update()
for ob, hb in RIGIDOS:
    mw = ob.matrix_world.copy(); b = arm_d.bones[hb]
    Mb = RIG.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    ob.parent = RIG; ob.parent_type = 'BONE'; ob.parent_bone = hb
    ob.matrix_parent_inverse = Mb.inverted()

# ------------------------------------------------------------------ decorado, luz y cámara
vs = []; fs = []
perfil = [(-6.0, 0.0), (1.0, 0.0)] + [(1.0 + math.sin(math.radians(a)), 1.0 - math.cos(math.radians(a))) for a in range(10, 91, 10)] + [(2.0, 6.0)]
xs = [-6, -2, 0, 2, 6]
for (y, z) in perfil:
    for x in xs: vs.append((x, y, z))
for i in range(len(perfil) - 1):
    for j in range(len(xs) - 1):
        a = i * len(xs) + j; fs.append((a, a + 1, a + 1 + len(xs), a + len(xs)))
fondo = nueva("Fondo", vs, fs, M_FONDO)
for j, (x, z, r, rot) in enumerate([(-0.95, 2.05, 0.22, 10), (0.9, 2.3, 0.16, -15), (1.15, 1.25, 0.12, 25), (-1.2, 1.0, 0.14, -5), (0.55, 2.75, 0.1, 30), (-0.55, 2.7, 0.12, -20)]):
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5 + math.radians(rot); rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), 1.98, z + rr * math.sin(a)))
    pts.append((x, 1.98, z)); cc = len(pts) - 1
    e = nueva(f"EstrellaFondo{j}", pts, [(cc, (i + 1) % 10, i) for i in range(10)], mat_plano(f"EstrellaFondo{j}", "#C9F4FF", 1.0), suave=False, origen=(x, 1.98, z))
    e.rotation_mode = 'XYZ'
    for f, ang in ((1, 0), (FIN, 40 if j % 2 else -40)):
        e.rotation_euler = (0, math.radians(ang), 0); e.keyframe_insert("rotation_euler", index=1, frame=f)
# sombra de contacto (mancha) bajo los pies
mb = bpy.data.materials.new("SombraSuelo"); mb.use_nodes = True; N = mb.node_tree.nodes; N.clear()
o = N.new('ShaderNodeOutputMaterial'); tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = lin("#0E5C7A")
mx = N.new('ShaderNodeMixShader'); mx.inputs[0].default_value = 0.55
mb.node_tree.links.new(tr.outputs[0], mx.inputs[1]); mb.node_tree.links.new(em.outputs[0], mx.inputs[2]); mb.node_tree.links.new(mx.outputs[0], o.inputs['Surface'])
try: mb.surface_render_method = 'BLENDED'
except Exception: pass
vs = [(0, 0, 0.004)] + [(0.36 * math.cos(2 * math.pi * i / 48), 0.22 * math.sin(2 * math.pi * i / 48) - 0.03, 0.004) for i in range(48)]
mancha = nueva("SombraContacto", vs, [(0, i + 1, (i + 1) % 48 + 1) for i in range(48)], mb, suave=False)

sol = bpy.data.lights.new("Sol", 'SUN'); sol.energy = 3.2; sol.angle = math.radians(0.8)
so = bpy.data.objects.new("Sol", sol); COL.objects.link(so)
so.rotation_euler = Vector((0.0, 0.0, -1.0)).rotation_difference(Vector((0.28, 0.62, -0.73)).normalized()).to_euler()
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes.get("Background")
if bg: bg.inputs['Color'].default_value = lin("#7FA8C9"); bg.inputs['Strength'].default_value = 0.06

cam_d = bpy.data.cameras.new("Camara"); cam_d.lens = 40; cam = bpy.data.objects.new("Camara", cam_d); COL.objects.link(cam); sc.camera = cam
mira = bpy.data.objects.new("Mira", None); COL.objects.link(mira)
tc = cam.constraints.new('TRACK_TO'); tc.target = mira; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'

# ------------------------------------------------------------------ animación
P = RIG.pose.bones
def q_eje(pb, eje, g):
    R = pb.bone.matrix_local.to_3x3()
    return Quaternion((R.inverted() @ Vector(eje)).normalized(), math.radians(g))
def esc_local(pb, s):
    R = pb.bone.matrix_local.to_3x3(); out = []
    for i in range(3):
        col = Vector((R[0][i], R[1][i], R[2][i])); j = max(range(3), key=lambda k: abs(col[k])); out.append(s[j])
    return out
def K(nombre, f, r=(), l=None, s=None):
    pb = P[nombre]; pb.rotation_mode = 'QUATERNION'; q = Quaternion()
    for eje, g in r: q = q @ q_eje(pb, eje, g)
    pb.rotation_quaternion = q; pb.keyframe_insert("rotation_quaternion", frame=f)
    if l is not None:
        pb.location = pb.bone.matrix_local.to_3x3().inverted() @ Vector(l); pb.keyframe_insert("location", frame=f)
    if s is not None:
        pb.scale = esc_local(pb, s); pb.keyframe_insert("scale", frame=f)
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)

# raíz: salto con giro, aplastar y estirar, baile
def KR(f, l=(0, 0, 0), s=(1, 1, 1), giro=0.0, lado=0.0):
    pb = P["raiz"]; pb.rotation_mode = 'XYZ'
    R = pb.bone.matrix_local.to_3x3().inverted()
    e = R @ Vector((0, math.radians(lado), math.radians(giro)))
    pb.rotation_euler = e; pb.keyframe_insert("rotation_euler", frame=f)
    pb.location = R @ Vector(l); pb.keyframe_insert("location", frame=f)
    pb.scale = esc_local(pb, s); pb.keyframe_insert("scale", frame=f)
KR(1); KR(36); KR(46, s=(1.14, 1.14, 0.80)); KR(53, l=(0, 0, 0.12), s=(0.9, 0.9, 1.2)); KR(56, l=(0, 0, 0.26), s=(0.95, 0.95, 1.1))
KR(62, l=(0, 0, 0.46), s=(1, 1, 1.03), giro=90); KR(72, l=(0, 0, 0.58), giro=200); KR(82, l=(0, 0, 0.42), giro=320)
KR(87, l=(0, 0, 0.06), s=(0.93, 0.93, 1.1), giro=360); KR(90, l=(0, 0, 0), s=(1.2, 1.2, 0.76), giro=360)
KR(96, s=(0.95, 0.95, 1.07), giro=360); KR(102, s=(1.02, 1.02, 0.98), giro=360); KR(108, giro=360); KR(168, giro=360)
for k, f in enumerate(range(175, 212, 10)):
    sx = 0.05 if k % 2 == 0 else -0.05
    KR(f, l=(sx, 0, 0), s=(1.03, 1.03, 0.95), giro=360, lado=7 if k % 2 == 0 else -7)
    KR(f + 5, l=(sx * 0.4, 0, 0.02), giro=360, lado=0)
KR(216, giro=360); KR(FIN, giro=360)

# tronco
for f, r in ((1, []), (36, []), (46, [(X, 16)]), (53, [(X, -10)]), (72, []), (90, [(X, 14)]), (100, [(X, -3)]), (108, []), (168, [])):
    K("columna", f, r)
for k, f in enumerate(range(175, 212, 10)):
    K("columna", f, [(Y, -8 if k % 2 == 0 else 8)]); K("columna", f + 5, [])
K("columna", 216, []); K("columna", FIN, [(X, -4)])
for f in (1, 240): K("pecho", f, [])
K("pecho", 18, [(Y, 3)]); K("pecho", 30, [(Y, -2)])

# cabeza: saludo ladeado, mira arriba, cae, "no, no, no" muy rápido (latigazo del pelo), baile, guiño final
cab = [(1, [(Y, 7)], None), (20, [(Y, -5)], None), (36, [], None), (46, [(X, -14)], None), (60, [(X, -8)], None), (72, [], None),
       (90, [(X, 12)], (1.08, 1.08, 0.9)), (96, [(X, -5)], (0.96, 0.96, 1.05)), (104, [(Y, 9)], (1, 1, 1)), (116, [], None)]
for f, r, s in cab: K("cabeza", f, r, s=s if s else (1, 1, 1))
for k, f in enumerate((121, 127, 133, 139, 145, 151, 157)):
    K("cabeza", f, [(Z, 32 if k % 2 == 0 else -32), (X, 4)])
K("cabeza", 164, [])
for k, f in enumerate(range(175, 212, 10)):
    K("cabeza", f, [(Y, 10 if k % 2 == 0 else -10)]); K("cabeza", f + 5, [(X, 6)])
K("cabeza", 216, []); K("cabeza", 224, [(Y, -10), (Z, 6)]); K("cabeza", FIN, [(Y, -12), (Z, 6)])
K("cuello", 1, []); K("cuello", FIN, [])

# brazos (de goma): saludo, impulso, brazos abiertos en el aire, caída, brazos en jarra, baile, "¡ey!" final
def brazo(L, f, sup, inf, mano=()):
    sgn = 1 if L == "L" else -1
    K(f"brazo_sup.{L}", f, [(e, g * (sgn if e == Y or e == Z else 1)) for e, g in sup])
    K(f"brazo_inf.{L}", f, [(e, g * (sgn if e == Y or e == Z else 1)) for e, g in inf])
    K(f"mano.{L}", f, [(e, g * (sgn if e == Y or e == Z else 1)) for e, g in mano])
# convención: en Y, negativo = el brazo sube hacia fuera (para los dos lados, ya corregido por sgn)
for L in ("L", "R"):
    brazo(L, 1, [(Y, -8)], []) if L == "L" else None
brazo("R", 1, [(Y, -145), (X, -10)], [(Y, -20)])
for k, f in enumerate((6, 12, 18, 24, 30)):
    brazo("R", f, [(Y, -145), (X, -10)], [(Y, 25 if k % 2 == 0 else -25)], [(Y, 15 if k % 2 == 0 else -15)])
brazo("L", 30, [(Y, -10)], [(Y, -8)]); brazo("R", 38, [(Y, -10)], [(Y, -8)])
for L in ("L", "R"):
    brazo(L, 46, [(X, 45), (Y, -10)], [(X, 25)])
    brazo(L, 54, [(Y, -165)], [(Y, -10)])
    brazo(L, 64, [(Y, -95)], [(Y, -15)], [(Y, -10)])
    brazo(L, 80, [(Y, -100)], [(Y, 20)], [(Y, 10)])
    brazo(L, 87, [(Y, -135)], [(Y, -15)])
    brazo(L, 91, [(Y, -50)], [(Y, -40)])
    brazo(L, 100, [(Y, -12)], [(Y, -8)])
    brazo(L, 112, [(Y, -38), (X, 8)], [(Y, 95)], [(Y, 20)])   # en jarra
    brazo(L, 164, [(Y, -38), (X, 8)], [(Y, 95)], [(Y, 20)])
for k, f in enumerate(range(172, 212, 5)):
    a = k % 2 == 0
    brazo("L", f, [(Y, -150 if a else -125)], [(Y, 35 if a else -30)], [(Y, 20 if a else -20)])
    brazo("R", f, [(Y, -125 if a else -150)], [(Y, -30 if a else 35)], [(Y, -20 if a else 20)])
brazo("L", 216, [(Y, -38), (X, 8)], [(Y, 95)], [(Y, 20)]); brazo("L", FIN, [(Y, -38), (X, 8)], [(Y, 95)], [(Y, 20)])
brazo("R", 216, [(X, -60), (Y, -30)], [(X, -35)], [(X, -10)]); brazo("R", 226, [(X, -75), (Y, -38)], [(X, -20)], [(X, -20)])
brazo("R", FIN, [(X, -72), (Y, -36)], [(X, -22)], [(X, -18)])

# piernas: recogidas en el aire, pasitos en el baile
def pierna(L, f, m, p, pie=()):
    K(f"muslo.{L}", f, m); K(f"pierna.{L}", f, p); K(f"pie.{L}", f, pie)
for L in ("L", "R"):
    for f in (1, 46, 54): pierna(L, f, [], [])
    pierna(L, 62, [(X, -55)], [(X, 75)], [(X, 10)]); pierna(L, 80, [(X, -60)], [(X, 80)], [(X, 10)])
    pierna(L, 87, [(X, -8)], [(X, 10)]); pierna(L, 90, [], []); pierna(L, 168, [], [])
for k, f in enumerate(range(175, 212, 10)):
    L = "L" if k % 2 == 0 else "R"; O = "R" if L == "L" else "L"
    pierna(L, f, [(X, -28)], [(X, 45)], [(X, 10)]); pierna(O, f, [], [])
    pierna(L, f + 5, [], []); pierna(O, f + 5, [], [])
for L in ("L", "R"): pierna(L, 216, [], []); pierna(L, FIN, [], [])

# cara: parpadeos, guiño, cejas y boca
def ko(ob, f, attr, val, idx=None):
    setattr(ob, attr, val) if idx is None else getattr(ob, attr).__setitem__(idx, val)
    ob.keyframe_insert(attr, frame=f) if idx is None else ob.keyframe_insert(attr, index=idx, frame=f)
for lado in ("L", "R"):
    ojo, pup, ceja = OJOS[lado]
    for f, v in ((1, 1), (32, 1), (34, 0.08), (37, 1), (110, 1), (112, 0.08), (115, 1), (166, 1), (168, 0.08), (171, 1), (FIN, 1)):
        ko(ojo, f, "scale", v, 2)
    zc = ceja.location.z
    for f, dz in ((1, 0), (40, 0), (46, 0.035), (88, 0.03), (96, 0), (118, 0), (121, -0.018), (160, -0.018), (166, 0), (FIN, 0)):
        ko(ceja, f, "location", zc + dz, 2)
    pz = pup.location.z
    for f, dz in ((1, 0), (40, 0), (46, 0.022), (64, 0.022), (90, -0.01), (100, 0), (FIN, 0)):
        ko(pup, f, "location", pz + dz, 2)
ojoL = OJOS["L"][0]
for f, v in ((216, 1), (220, 0.1), (236, 0.1), (FIN, 1)):
    ko(ojoL, f, "scale", v, 2)
for f, v in ((1, 1.0), (44, 0.8), (54, 1.45), (86, 1.4), (92, 0.7), (100, 1.0), (118, 1.0), (122, 0.55), (160, 0.55), (168, 1.15), (212, 1.15), (220, 1.25), (FIN, 1.25)):
    ko(boca, f, "scale", v, 2)

# sombra de contacto: se encoge y aclara al saltar
for f, s in ((1, 1), (53, 0.95), (62, 0.62), (72, 0.5), (82, 0.62), (87, 0.95), (90, 1.15), (100, 1), (FIN, 1)):
    mancha.scale = (s, s, 1); mancha.keyframe_insert("scale", frame=f)

# cámara (vertical 9:16): general, sigue el salto, primer plano en el "no, no, no", general en el baile
for f, cp, mp in ((1, (0, -3.35, 1.05), (0, 0, 0.98)), (50, (0, -3.35, 1.05), (0, 0, 0.98)), (72, (0, -3.55, 1.38), (0, 0, 1.32)),
                  (96, (0, -3.35, 1.05), (0, 0, 0.98)), (112, (0, -3.3, 1.08), (0, 0, 1.0)), (124, (0.28, -2.05, 1.42), (0, 0, 1.36)),
                  (160, (0.2, -2.0, 1.42), (0, 0, 1.36)), (172, (0, -3.4, 1.05), (0, 0, 0.98)), (212, (0, -3.35, 1.05), (0, 0, 0.98)),
                  (FIN, (0.15, -2.75, 1.12), (0, 0, 1.08))):
    cam.location = cp; cam.keyframe_insert("location", frame=f); mira.location = mp; mira.keyframe_insert("location", frame=f)

# interpolación suave (Bézier con tiradores automáticos)
def todas_curvas(ad):
    act = ad.action if ad else None
    if not act: return []
    try:
        return list(act.fcurves)
    except Exception:
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags: out += list(cb.fcurves)
        return out
for ob in bpy.data.objects:
    for fc in todas_curvas(ob.animation_data):
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
        fc.update()

# ------------------------------------------------------------------ pelo con físicas: Wiggle Bones
resultado_pelo = {"wiggle": False}
if hasattr(sc, "wiggle"):
    for cad in MECH_HUESOS:
        for j, n in enumerate(cad):
            w_ = P[n].wiggle
            w_.tail = True; w_.mass = 1.0; w_.stiff = (520, 380, 260)[j]; w_.damp = (1.2, 0.9, 0.7)[j]; w_.gravity = 0.35; w_.chain = True
    sc.wiggle.iterations = 4; sc.wiggle.loop = False; sc.wiggle.enable = True
    RIG.wiggle.enable = True
    # simular desde un poco antes del principio (para que el pelo ya esté asentado) y guardar cada fotograma
    todos = [n for cad in MECH_HUESOS for n in cad]
    sc.wiggle.is_preroll = True
    for f in range(-24, 2): sc.frame_set(f)
    datos = {n: {} for n in todos}
    for f in range(1, FIN + 1):
        sc.frame_set(f)
        if f == 1: sc.wiggle.is_preroll = False
        for n in todos: datos[n][f] = P[n].matrix_basis.copy()
    sc.wiggle.enable = False; RIG.wiggle.freeze = True
    for n in todos:
        pb = P[n]; pb.rotation_mode = 'QUATERNION'
        for f in range(1, FIN + 1):
            pb.matrix_basis = datos[n][f]
            pb.keyframe_insert("rotation_quaternion", frame=f, group=n)
            pb.keyframe_insert("location", frame=f, group=n)
    resultado_pelo = {"wiggle": True, "huesos": len(todos)}

sc.frame_set(1)
if SALIDA_BLEND:
    bpy.ops.wm.save_as_mainfile(filepath=SALIDA_BLEND)
result = {"objetos": len(bpy.data.objects), "huesos": len(arm_d.bones), "pelo": resultado_pelo, "fin": FIN}
