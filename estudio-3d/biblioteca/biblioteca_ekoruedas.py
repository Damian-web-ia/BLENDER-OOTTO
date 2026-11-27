# EKORUEDAS - BIBLIOTECA 3D (versión 3, 2026-11-27: Alex v3 con cara seria en personajes/alex_anim.py; versión 2, 26-11: capa viva; versión 1, 25-11)
# Personajes, coche, ruedas, taller, carretera cenital, luces y utilidades de cámara/texto/visemas.
# Uso desde el script de cada reel:  END = 1005; VOICES = [...]; exec(open(BIBLIOTECA).read())
# Luego el reel solo escribe cámaras, textos y acción. Mejorar aquí = mejorar todos los reels.
# Personajes: Alex (mecánico) y Clod (robot). Sin logo, sin nombre del taller en imagen.
import bpy, bmesh, math, json, os
from mathutils import Vector

# Antes de ejecutar esta biblioteca, el script del reel define END (último fotograma) y, si hay voces, VOICES.
FPS = 30
END = globals().get("END", 900)
VOICES = globals().get("VOICES", [])

def fr(t):
    return int(round(t * FPS)) + 1

# ----------------------------------------------------------------- limpieza y ajustes
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.curves, bpy.data.images, bpy.data.actions):
    for d in list(coll):
        if d.users == 0:
            coll.remove(d)
for m in list(sc.timeline_markers):
    sc.timeline_markers.remove(m)
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, END
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = 100
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "AgX"
try:
    sc.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass

COLL = {}
for n in ("TALLER", "COCHE", "INSERTO", "ALEX", "CLOD", "CAMARAS", "TEXTOS", "LUCES"):
    c = bpy.data.collections.new(n); sc.collection.children.link(c); COLL[n] = c

FONT = None
for fp in (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"):
    if os.path.exists(fp):
        FONT = bpy.data.fonts.load(fp); break

# ----------------------------------------------------------------- materiales
def mat(name, color, rough=0.4, metal=0.0, coat=0.0, emit=None, es=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = es
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    return m

M = {
    "paint": mat("PinturaAzulPetroleo", (0.015, 0.16, 0.22), 0.22, 0.6, coat=1.0),
    "glassD": mat("CristalOscuro", (0.01, 0.012, 0.016), 0.05, 0.2, coat=1.0),
    "trim": mat("PlasticoNegro", (0.02, 0.02, 0.022), 0.6),
    "rubber": mat("CauchoNuevo", (0.012, 0.012, 0.014), 0.75),
    "worn": mat("CauchoGastado", (0.16, 0.16, 0.16), 0.95),
    "rim": mat("Llanta", (0.55, 0.56, 0.58), 0.25, 1.0),
    "rimW": mat("LlantaVieja", (0.3, 0.3, 0.3), 0.6, 0.6),
    "lightW": mat("Faro", (1, 1, 1), 0.2, emit=(0.9, 0.95, 1.0), es=6),
    "lightR": mat("Piloto", (0.5, 0, 0), 0.2, emit=(1, 0.04, 0.02), es=5),
    "orange": mat("NaranjaClod", (0.95, 0.22, 0.0), 0.35, coat=0.6),
    "dark": mat("NegroMate", (0.02, 0.02, 0.025), 0.5),
    "screen": mat("Pantalla", (0.004, 0.004, 0.006), 0.1, coat=1.0),
    "led": mat("LED", (1, 1, 1), 0.3, emit=(1, 1, 1), es=5),
    "skin": mat("Piel", (0.42, 0.24, 0.15), 0.5),
    "hair": mat("Pelo", (0.03, 0.022, 0.018), 0.6),
    "beard": mat("Barba", (0.06, 0.05, 0.045), 0.8),
    "uniform": mat("Uniforme", (0.025, 0.025, 0.03), 0.7),
    "piping": mat("Ribete", (0.95, 0.35, 0.02), 0.5),
    "eyeW": mat("OjoBlanco", (0.9, 0.9, 0.88), 0.2),
    "iris": mat("Iris", (0.06, 0.035, 0.02), 0.2, coat=1.0),
    "mouth": mat("Boca", (0.12, 0.03, 0.03), 0.6),
    "boot": mat("Bota", (0.05, 0.04, 0.035), 0.5),
    "floorW": mat("SueloTaller", (0.055, 0.056, 0.06), 0.45, coat=0.1),
    "wallW": mat("ParedTaller", (0.16, 0.165, 0.17), 0.85),
    "shelf": mat("Estanteria", (0.25, 0.26, 0.28), 0.5, 0.7),
    "red": mat("ArmarioRojo", (0.45, 0.02, 0.02), 0.3, 0.3, coat=0.5),
    "warm": mat("LamparaCalida", (1, 0.8, 0.5), 0.3, emit=(1, 0.72, 0.42), es=15),
    "asphalt": mat("AsfaltoMojado", (0.012, 0.013, 0.016), 0.08, 0.0, coat=1.0),
    "puddle": mat("Charco", (0.01, 0.012, 0.016), 0.02, 0.0, coat=1.0),
    "ground": mat("Arcen", (0.03, 0.042, 0.032), 0.8),
    "lineW": mat("LineaBlanca", (0.85, 0.85, 0.85), 0.4),
    "white3d": mat("TextoBlanco", (1, 1, 1), 0.3, emit=(1, 1, 1), es=2.5),
    "orange3d": mat("TextoNaranja", (1, 0.52, 0.0), 0.3, emit=(1, 0.52, 0.0), es=3.5),
    "hlF": mat("ResalteDelantero", (0.02, 0.02, 0.02), 0.5, emit=(1, 0.52, 0.0), es=0.0),
    "hlR": mat("ResalteTrasero", (0.02, 0.02, 0.02), 0.5, emit=(1, 0.52, 0.0), es=0.0),
    "glowNew": mat("BrilloNuevas", (0.012, 0.012, 0.014), 0.75, emit=(1, 0.52, 0.0), es=0.0),
}

# ----------------------------------------------------------------- utilidades
def new_obj(name, me, cname, m=None, parent=None, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, me); COLL[cname].objects.link(o)
    if m:
        me.materials.append(m)
    o.location = loc
    if parent:
        o.parent = parent
    return o

def empty(name, cname, parent=None, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, None); COLL[cname].objects.link(o)
    o.location = loc
    if parent:
        o.parent = parent
    return o

def prim(kind, name, cname, m=None, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), smooth=True, **kw):
    bm = bmesh.new()
    if kind == "cube":
        bmesh.ops.create_cube(bm, size=1.0)
    elif kind == "sphere":
        bmesh.ops.create_uvsphere(bm, u_segments=kw.get("u", 32), v_segments=kw.get("v", 16), radius=kw.get("r", 0.5))
    elif kind == "cyl":
        bmesh.ops.create_cone(bm, cap_ends=True, segments=kw.get("seg", 32), radius1=kw.get("r", 0.5), radius2=kw.get("r2", kw.get("r", 0.5)), depth=kw.get("d", 1.0))
    elif kind == "torus":
        R, rr, s1, s2 = kw.get("R", 0.5), kw.get("rr", 0.1), kw.get("s1", 48), kw.get("s2", 16)
        vs = []
        for i in range(s1):
            a = 2 * math.pi * i / s1
            row = []
            for j in range(s2):
                b_ = 2 * math.pi * j / s2
                row.append(bm.verts.new(((R + rr * math.cos(b_)) * math.cos(a), (R + rr * math.cos(b_)) * math.sin(a), rr * math.sin(b_) * kw.get("zs", 1.0))))
            vs.append(row)
        for i in range(s1):
            for j in range(s2):
                bm.faces.new((vs[i][j], vs[(i + 1) % s1][j], vs[(i + 1) % s1][(j + 1) % s2], vs[i][(j + 1) % s2]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o = new_obj(name, me, cname, m, parent, loc)
    o.rotation_euler = rot; o.scale = scale
    if kw.get("bevel"):
        md = o.modifiers.new("bev", "BEVEL"); md.width = kw["bevel"]; md.segments = kw.get("bseg", 3)
    return o

def key_loc(o, f, loc):
    o.location = loc; o.keyframe_insert("location", frame=f)

def key_rot(o, f, rot):
    o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=f)

def key_scale(o, f, s):
    o.scale = s; o.keyframe_insert("scale", frame=f)

def key_emit(m, f, strength):
    s = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    s.default_value = strength; s.keyframe_insert("default_value", frame=f)

def place(o, f, pos, rz_deg):
    o.location = pos; o.rotation_euler = (0, 0, math.radians(rz_deg))
    o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)

R = math.radians

# ----------------------------------------------------------------- ruedas
def wheel(name, cname, new=True, parent=None, loc=(0, 0, 0), standing=True, r=0.33, width=0.2):
    """Devuelve (exterior, giro). Con standing=True el eje queda a lo largo de -Y; el hijo 'giro' rota sobre su Z local."""
    outer = empty(name, cname, parent, loc)
    if standing:
        outer.rotation_euler = (R(90), 0, 0)
    spin = empty(name + "_Giro", cname, outer)
    rr = width * 0.5
    tm = M["rubber"] if new else M["worn"]
    prim("torus", name + "_Neumatico", cname, tm, spin, R=r - rr, rr=rr, s1=64, s2=20, zs=1.0)
    prim("cyl", name + "_Llanta", cname, M["rim"] if new else M["rimW"], spin, r=(r - rr) * 0.95, d=width * 0.75, seg=40)
    prim("cyl", name + "_Buje", cname, M["trim"], spin, r=0.05, d=width * 0.85, seg=20)
    for k in range(5):  # radios
        a = 2 * math.pi * k / 5
        prim("cube", f"{name}_Radio{k}", cname, M["trim"], spin, loc=(math.cos(a) * 0.1, math.sin(a) * 0.1, 0), rot=(0, 0, a), scale=(0.15, 0.03, width * 0.8), smooth=False)
    if new:  # taco del dibujo
        n = 44
        for k in range(n):
            a = 2 * math.pi * k / n
            prim("cube", f"{name}_Taco{k}", cname, M["rubber"], spin, loc=(math.cos(a) * (r - 0.004), math.sin(a) * (r - 0.004), 0), rot=(0, 0, a + R(12)), scale=(0.022, 0.035, width * 0.82), smooth=False)
    return outer, spin

# ----------------------------------------------------------------- taller
fl = prim("cube", "Taller_Suelo", "TALLER", M["floorW"], loc=(0, 0, -0.05), scale=(30, 30, 0.1), smooth=False)
prim("cube", "Taller_ParedFondo", "TALLER", M["wallW"], loc=(0, 4.0, 3), scale=(30, 0.2, 6), smooth=False)
prim("cube", "Taller_ParedIzq", "TALLER", M["wallW"], loc=(-7.0, 0, 3), scale=(0.2, 30, 6), smooth=False)
# franja naranja de seguridad en la pared (sin texto)
prim("cube", "Taller_Franja", "TALLER", M["piping"], loc=(0, 3.88, 1.1), scale=(30, 0.02, 0.06), smooth=False)
# estantería con neumáticos lisos
for i, x in enumerate((-4.6, -2.6)):
    prim("cube", f"Taller_EstPata{i}a", "TALLER", M["shelf"], loc=(x - 0.9, 3.6, 1.2), scale=(0.06, 0.5, 2.4), smooth=False)
    prim("cube", f"Taller_EstPata{i}b", "TALLER", M["shelf"], loc=(x + 0.9, 3.6, 1.2), scale=(0.06, 0.5, 2.4), smooth=False)
    for j, z in enumerate((0.15, 1.0, 1.85)):
        prim("cube", f"Taller_Balda{i}{j}", "TALLER", M["shelf"], loc=(x, 3.6, z), scale=(1.9, 0.55, 0.04), smooth=False)
        for k in range(3):
            prim("torus", f"Taller_Neum{i}{j}{k}", "TALLER", M["rubber"], loc=(x - 0.55 + k * 0.55, 3.6, z + 0.33), rot=(R(90), 0, 0), R=0.24, rr=0.085, s1=40, s2=12)
prim("cube", "Taller_Armario", "TALLER", M["red"], loc=(4.2, 3.4, 0.6), scale=(1.4, 0.6, 1.2), bevel=0.03)
prim("cube", "Taller_ArmarioTapa", "TALLER", M["shelf"], loc=(4.2, 3.4, 1.22), scale=(1.45, 0.65, 0.04), smooth=False)
prim("cyl", "Taller_Lampara", "TALLER", M["warm"], loc=(1.2, 1.0, 3.3), r=0.35, r2=0.12, d=0.25)
prim("cyl", "Taller_LamparaCable", "TALLER", M["trim"], loc=(1.2, 1.0, 4.4), r=0.01, d=2.0)

# ----------------------------------------------------------------- coche compacto (frente en +X)
CAR = empty("COCHE_Raiz", "COCHE")
prim("cube", "COCHE_Carroceria", "COCHE", M["paint"], CAR, loc=(0, 0, 0.78), scale=(4.2, 1.74, 0.62), bevel=0.16, bseg=5)
prim("cube", "COCHE_Habitaculo", "COCHE", M["glassD"], CAR, loc=(-0.3, 0, 1.33), scale=(2.3, 1.5, 0.58), bevel=0.2, bseg=5)
prim("cube", "COCHE_Techo", "COCHE", M["paint"], CAR, loc=(-0.38, 0, 1.6), scale=(1.95, 1.47, 0.1), bevel=0.05, bseg=3)
for s in (-1, 1):
    prim("cube", f"COCHE_Pilar{s}", "COCHE", M["paint"], CAR, loc=(-0.3, s * 0.745, 1.33), scale=(0.1, 0.03, 0.56), smooth=False)
    prim("cube", f"COCHE_Faro{s}", "COCHE", M["lightW"], CAR, loc=(2.08, s * 0.6, 0.9), scale=(0.08, 0.32, 0.1), bevel=0.02)
    prim("cube", f"COCHE_PilotoT{s}", "COCHE", M["lightR"], CAR, loc=(-2.08, s * 0.62, 0.95), scale=(0.08, 0.3, 0.1), bevel=0.02)
    for x in (1.35, -1.35):
        prim("torus", f"COCHE_Paso{s}{x}", "COCHE", M["trim"], CAR, loc=(x, s * 0.86, 0.36), rot=(R(90), 0, 0), R=0.4, rr=0.05, s1=40, s2=10)
prim("cube", "COCHE_ParagolpesD", "COCHE", M["trim"], CAR, loc=(2.1, 0, 0.55), scale=(0.12, 1.7, 0.2), bevel=0.04)
prim("cube", "COCHE_ParagolpesT", "COCHE", M["trim"], CAR, loc=(-2.1, 0, 0.55), scale=(0.12, 1.7, 0.2), bevel=0.04)
prim("cube", "COCHE_Rejilla", "COCHE", M["trim"], CAR, loc=(2.11, 0, 0.78), scale=(0.04, 0.7, 0.14), smooth=False)
WH = {}
for key, x, y, new in (("DI", 1.35, -0.8, False), ("DD", 1.35, 0.8, False), ("TI", -1.35, -0.8, True), ("TD", -1.35, 0.8, True)):
    WH[key] = wheel("COCHE_Rueda" + key, "COCHE", new, CAR, (x, y, 0.33))

# rueda nueva suelta (la que empuja Clod)
LOOSE, LOOSE_SPIN = wheel("RUEDA_Suelta", "COCHE", True, None, (-1.15, -1.55, 0.33))

# pilas de 4 neumáticos (plano 10): gastados y nuevos
STK_W = empty("PILA_Gastados", "COCHE", None, (3.35, -1.15, 0))
STK_N = empty("PILA_Nuevos", "COCHE", None, (3.35, -1.15, 0))
for k in range(4):
    prim("torus", f"PILA_G{k}", "COCHE", M["worn"], STK_W, loc=(0, 0, 0.1 + k * 0.2), R=0.23, rr=0.1, s1=48, s2=14)
    prim("torus", f"PILA_N{k}", "COCHE", M["glowNew"], STK_N, loc=(0, 0, 0.1 + k * 0.2), R=0.23, rr=0.1, s1=48, s2=14)

# ----------------------------------------------------------------- inserto: carretera mojada vista cenital (lejos del taller)
OX = 40.0
RAD, L0 = 9.0, 12.0

def centerline(s):
    if s <= L0:
        return Vector((0, -10 + s)), Vector((1, 0))
    th = (s - L0) / RAD
    return Vector((-RAD + RAD * math.cos(th), 2 + RAD * math.sin(th))), Vector((math.cos(th), math.sin(th)))

def strip(name, a, b, s0, s1, z, m, step=0.25):
    bm = bmesh.new(); prev = None
    n = max(2, int((s1 - s0) / step) + 1)
    for i in range(n):
        s = s0 + (s1 - s0) * i / (n - 1)
        p, nrm = centerline(s)
        va = bm.verts.new((OX + p.x + nrm.x * a, p.y + nrm.y * a, z)); vb = bm.verts.new((OX + p.x + nrm.x * b, p.y + nrm.y * b, z))
        if prev:
            bm.faces.new((prev[0], prev[1], vb, va))
        prev = (va, vb)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return new_obj(name, me, "INSERTO", m)

S_END = L0 + RAD * R(85)
prim("cube", "INS_Arcen", "INSERTO", M["ground"], loc=(OX, 2, -0.06), scale=(40, 40, 0.1), smooth=False)
strip("INS_Asfalto", -3.5, 3.5, 0, S_END, 0.0, M["asphalt"])
strip("INS_BordeD", 3.15, 3.3, 0, S_END, 0.006, M["lineW"])
strip("INS_BordeI", -3.3, -3.15, 0, S_END, 0.006, M["lineW"])
s = 0.5; k = 0
while s < S_END - 1:
    strip(f"INS_Discontinua{k}", -0.07, 0.07, s, s + 1.2, 0.006, M["lineW"], 0.3); s += 2.4; k += 1
for i, (px, py, rr) in enumerate(()):
    prim("cyl", f"INS_Charco{i}", "INSERTO", M["puddle"], loc=(OX + px, py, 0.008), scale=(1, 0.7, 1), r=rr, d=0.004, seg=32)

MINI = empty("MINI_Raiz", "INSERTO", None, (OX, -6, 0))  # frente en +Y
prim("cube", "MINI_Carroceria", "INSERTO", M["paint"], MINI, loc=(0, 0, 0.6), scale=(1.74, 4.2, 0.62), bevel=0.16, bseg=4)
prim("cube", "MINI_Habitaculo", "INSERTO", M["glassD"], MINI, loc=(0, -0.3, 1.15), scale=(1.5, 2.3, 0.56), bevel=0.2, bseg=4)
prim("cube", "MINI_Techo", "INSERTO", M["paint"], MINI, loc=(0, -0.38, 1.43), scale=(1.47, 1.9, 0.08), bevel=0.04)
for s_ in (-1, 1):
    prim("cube", f"MINI_Faro{s_}", "INSERTO", M["lightW"], MINI, loc=(s_ * 0.6, 2.08, 0.75), scale=(0.32, 0.08, 0.1))
    prim("cube", f"MINI_Piloto{s_}", "INSERTO", M["lightR"], MINI, loc=(s_ * 0.6, -2.08, 0.8), scale=(0.3, 0.08, 0.1))
    prim("cube", f"MINI_RuedaD{s_}", "INSERTO", M["hlF"], MINI, loc=(s_ * 0.88, 1.35, 0.33), scale=(0.24, 0.66, 0.66), bevel=0.08)
    prim("cube", f"MINI_RuedaT{s_}", "INSERTO", M["hlR"], MINI, loc=(s_ * 0.88, -1.35, 0.33), scale=(0.24, 0.66, 0.66), bevel=0.08)
prim("cube", "MINI_EjeD", "INSERTO", M["hlF"], MINI, loc=(0, 1.35, 0.02), scale=(2.7, 0.45, 0.02), smooth=False)
prim("cube", "MINI_EjeT", "INSERTO", M["hlR"], MINI, loc=(0, -1.35, 0.02), scale=(2.7, 0.45, 0.02), smooth=False)

# ----------------------------------------------------------------- personajes (Alex SIN logo en el pecho)
def build_clod():
    root = empty("CLOD_Raiz", "CLOD"); root.scale = (0.15, 0.15, 0.15)
    body = prim("sphere", "CLOD_Cuerpo", "CLOD", M["orange"], root, loc=(0, 0, 0.78), scale=(1, 0.85, 1.1), r=0.42, u=48, v=24)
    for i in range(6):
        prim("cube", f"CLOD_Simbolo{i}", "CLOD", M["led"], body, loc=(0, -0.425, 0.08), rot=(0, R(i * 30), 0), scale=(0.045, 0.02, 0.32), smooth=False)
    hp = empty("CLOD_Cabeza", "CLOD", root, (0, 0, 1.25))
    prim("cube", "CLOD_CabezaMalla", "CLOD", M["orange"], hp, loc=(0, 0, 0.42), scale=(1.15, 0.85, 0.85), bevel=0.18, bseg=6)
    prim("cube", "CLOD_Pantalla", "CLOD", M["screen"], hp, loc=(0, -0.37, 0.42), scale=(0.92, 0.12, 0.62), bevel=0.1, bseg=6)
    eyes = [prim("cyl", f"CLOD_Ojo{s}", "CLOD", M["led"], hp, loc=(s * 0.21, -0.44, 0.5), rot=(R(90), 0, 0), scale=(1.15, 1, 1), r=0.11, d=0.02, seg=32) for s in (-1, 1)]
    mouth = prim("torus", "CLOD_Boca", "CLOD", M["led"], hp, loc=(0, -0.44, 0.27), rot=(R(90), 0, 0), scale=(1, 0.45, 1), R=0.12, rr=0.02)
    for s in (-1, 1):
        prim("cyl", f"CLOD_Auricular{s}", "CLOD", M["orange"], hp, loc=(s * 0.62, 0, 0.42), rot=(0, R(90), 0), r=0.2, d=0.14)
        prim("torus", f"CLOD_AroAuricular{s}", "CLOD", M["dark"], hp, loc=(s * 0.69, 0, 0.42), rot=(0, R(90), 0), R=0.15, rr=0.035)
    arms, legs = {}, {}
    for s in (-1, 1):
        sh = empty(f"CLOD_Hombro{s}", "CLOD", root, (s * 0.5, 0, 1.02))
        prim("cyl", f"CLOD_Brazo{s}", "CLOD", M["orange"], sh, loc=(0, 0, -0.22), r=0.09, d=0.45)
        prim("sphere", f"CLOD_Mano{s}", "CLOD", M["dark"], sh, loc=(0, 0, -0.48), r=0.11)
        arms[s] = sh
        lg = empty(f"CLOD_Cadera{s}", "CLOD", root, (s * 0.2, 0, 0.45))
        prim("cyl", f"CLOD_Pierna{s}", "CLOD", M["dark"], lg, loc=(0, 0, -0.15), r=0.09, d=0.3)
        prim("cube", f"CLOD_Pie{s}", "CLOD", M["orange"], lg, loc=(0, -0.05, -0.37), scale=(0.22, 0.32, 0.14), bevel=0.05)
        legs[s] = lg
    return {"root": root, "head": hp, "eyes": eyes, "mouth": mouth, "arms": arms, "legs": legs}

def build_alex():
    root = empty("ALEX_Raiz", "ALEX")
    pelvis = empty("ALEX_Pelvis", "ALEX", root, (0, 0, 0.95))
    for s in (-1, 1):
        hip = empty(f"ALEX_Cadera{s}", "ALEX", pelvis, (s * 0.11, 0, 0))
        prim("cyl", f"ALEX_Pierna{s}", "ALEX", M["uniform"], hip, loc=(0, 0, -0.45), r=0.085, d=0.88)
        prim("cube", f"ALEX_Bota{s}", "ALEX", M["boot"], hip, loc=(0, -0.05, -0.9), scale=(0.13, 0.28, 0.1), bevel=0.03)
    spine = empty("ALEX_Columna", "ALEX", pelvis, (0, 0, 0.02))
    prim("cube", "ALEX_Torso", "ALEX", M["uniform"], spine, loc=(0, 0, 0.32), scale=(0.42, 0.24, 0.6), bevel=0.11, bseg=6)
    prim("cube", "ALEX_Cinturon", "ALEX", M["boot"], spine, loc=(0, 0, 0.04), scale=(0.425, 0.245, 0.06), bevel=0.05, bseg=3)
    prim("torus", "ALEX_Cuello_Ribete", "ALEX", M["piping"], spine, loc=(0, 0, 0.62), scale=(1.0, 0.85, 1.0), R=0.07, rr=0.016)
    for s in (-1, 1):
        prim("sphere", f"ALEX_Deltoide{s}", "ALEX", M["uniform"], spine, loc=(s * 0.205, 0, 0.55), r=0.07)
    neck = empty("ALEX_Cuello", "ALEX", spine, (0, 0, 0.585))
    prim("cyl", "ALEX_CuelloMalla", "ALEX", M["skin"], neck, loc=(0, 0, 0.05), r=0.058, d=0.12)
    head = empty("ALEX_Cabeza", "ALEX", neck, (0, 0, 0.1))
    prim("sphere", "ALEX_Craneo", "ALEX", M["skin"], head, loc=(0, 0, 0.13), scale=(0.92, 1.0, 1.15), r=0.115)
    prim("sphere", "ALEX_Pelo", "ALEX", M["hair"], head, loc=(0, 0.018, 0.2), scale=(0.97, 1.02, 0.72), r=0.122)
    prim("sphere", "ALEX_Barba", "ALEX", M["beard"], head, loc=(0, -0.012, 0.07), scale=(0.93, 0.96, 0.62), r=0.115)
    prim("sphere", "ALEX_Nariz", "ALEX", M["skin"], head, loc=(0, -0.118, 0.13), scale=(0.8, 1, 1.2), r=0.022)
    mouth = prim("sphere", "ALEX_Boca", "ALEX", M["mouth"], head, loc=(0, -0.113, 0.075), scale=(1.6, 0.5, 0.25), r=0.02)
    eyes = []
    for s in (-1, 1):
        e = empty(f"ALEX_Ojo{s}", "ALEX", head, (s * 0.042, -0.095, 0.16))
        prim("sphere", f"ALEX_OjoBlanco{s}", "ALEX", M["eyeW"], e, r=0.019)
        prim("sphere", f"ALEX_Iris{s}", "ALEX", M["iris"], e, loc=(0, -0.014, 0), r=0.0105)
        prim("cube", f"ALEX_Ceja{s}", "ALEX", M["hair"], head, loc=(s * 0.043, -0.108, 0.192), rot=(0, s * R(-8), 0), scale=(0.042, 0.012, 0.01), bevel=0.003)
        prim("sphere", f"ALEX_Oreja{s}", "ALEX", M["skin"], head, loc=(s * 0.108, 0.0, 0.14), scale=(0.35, 0.6, 1), r=0.03)
        eyes.append(e)
    arms = {}
    for s in (-1, 1):
        sh = empty(f"ALEX_Hombro{s}", "ALEX", spine, (s * 0.25, 0, 0.55))
        prim("cyl", f"ALEX_BrazoSup{s}", "ALEX", M["uniform"], sh, loc=(0, 0, -0.15), r=0.058, d=0.32)
        el = empty(f"ALEX_Codo{s}", "ALEX", sh, (0, 0, -0.3))
        prim("cyl", f"ALEX_Antebrazo{s}", "ALEX", M["uniform"], el, loc=(0, 0, -0.14), r=0.05, d=0.3)
        prim("sphere", f"ALEX_Mano{s}", "ALEX", M["skin"], el, loc=(0, 0, -0.32), scale=(0.8, 0.55, 1.1), r=0.05)
        sh.rotation_euler = (0, s * R(8), 0)
        arms[s] = (sh, el)
    return {"root": root, "spine": spine, "head": head, "eyes": eyes, "mouth": mouth, "arms": arms}

CL = build_clod()
AL = build_alex()

# ----------------------------------------------------------------- luces y mundo
def light(name, kind, loc, energy, size=1.0, color=(1, 1, 1), rot=(0, 0, 0)):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = color
    if kind == "AREA":
        ld.size = size
    o = bpy.data.objects.new(name, ld); COLL["LUCES"].objects.link(o); o.location = loc; o.rotation_euler = rot
    return o

def aim(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

k = light("Luz_Clave", "AREA", (4.5, -5.0, 4.5), 650, 4); aim(k, (0.5, -0.5, 0.8))
f_ = light("Luz_Relleno", "AREA", (-5.0, -4.5, 2.5), 180, 5, (0.8, 0.88, 1.0)); aim(f_, (0, 0, 0.8))
r_ = light("Luz_Contra", "AREA", (0.5, 3.0, 4.0), 600, 3); aim(r_, (0.5, -1.0, 0.8))
light("Luz_Lampara", "POINT", (1.2, 1.0, 3.1), 250, color=(1, 0.72, 0.42))
ins = light("Luz_Inserto", "AREA", (OX - 1, 3, 14), 2200, 22); aim(ins, (OX - 1, 3, 0))
ins2 = light("Luz_InsertoRim", "AREA", (OX + 6, 12, 6), 2500, 8, (0.7, 0.8, 1.0)); aim(ins2, (OX - 1, 2, 0))
w = sc.world or bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"].inputs
bg[0].default_value = (0.012, 0.013, 0.016, 1); bg[1].default_value = 0.5

# ----------------------------------------------------------------- cámaras y textos
CAMS = {}
def camera(name, lens):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_fit = "VERTICAL"; cd.sensor_height = 24
    cd.dof.use_dof = False; cd.clip_start = 0.02; cd.clip_end = 200
    co = bpy.data.objects.new(name, cd); COLL["CAMARAS"].objects.link(co)
    tg = empty(name + "_Objetivo", "CAMARAS")
    c = co.constraints.new("TRACK_TO"); c.target = tg; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    CAMS[name] = (co, tg, lens)
    return co

def cam_keys(name, keys):
    co, tg, _ = CAMS[name]
    for f, pos, tgt in keys:
        key_loc(co, f, pos); key_loc(tg, f, tgt)

TXT_D = 0.4
def cam_text(cam, name, body, m, y_frac, h_frac, f_in, f_out):
    """Texto ligado a la cámara, a 0,4 m (siempre delante de todo). y_frac: -1 abajo .. 1 arriba. h_frac: altura de letra / alto del cuadro."""
    co, _, lens = CAMS[cam]
    H = TXT_D * 12.0 / lens
    size = h_frac * 2 * H
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.extrude = size * 0.06
    cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.bevel_depth = size * 0.01
    if FONT:
        cu.font = FONT
    o = bpy.data.objects.new(name, cu); COLL["TEXTOS"].objects.link(o); cu.materials.append(m)
    o.parent = co; o.location = (0, y_frac * H, -TXT_D)
    key_scale(o, 1, (0, 0, 0)); key_scale(o, f_in - 1, (0, 0, 0)); key_scale(o, f_in + 5, (1.12, 1.12, 1.12)); key_scale(o, f_in + 8, (1, 1, 1))
    key_scale(o, f_out - 4, (1, 1, 1)); key_scale(o, f_out, (0, 0, 0))
    return o

M["plate"] = mat("PlacaTexto", (0, 0, 0), 0.9, alpha=0.6)
def cam_plate(cam, name, y_frac, h_frac, f_in, f_out):
    co, _, lens = CAMS[cam]
    H = TXT_D * 12.0 / lens
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5); bm.to_mesh(me); bm.free()
    o = new_obj(name, me, "TEXTOS", M["plate"], co, (0, y_frac * H, -TXT_D - 0.003))
    sx, sy = 2 * H * 9 / 16 * 0.94, h_frac * 2 * H
    key_scale(o, 1, (0, 0, 0)); key_scale(o, f_in - 1, (0, 0, 0)); key_scale(o, f_in + 4, (sx, sy, 1))
    key_scale(o, f_out - 4, (sx, sy, 1)); key_scale(o, f_out, (0, 0, 0))
    return o


# ----------------------------------------------------------------- visemas y parpadeos
def visemes(mouth, line, axis, closed, open_amt, idle):
    t0 = line["at"]
    for i, (a, b) in enumerate(line["w"]):
        a += t0; b += t0
        amt = open_amt * (0.75 + 0.25 * ((i * 37) % 5) / 4)
        fa, fb = fr(a), max(fr(b), fr(a) + 2)
        s_ = list(idle); s_[axis] = closed; key_scale(mouth, fa - 1, s_)
        s_ = list(idle); s_[axis] = amt; key_scale(mouth, (fa + fb) // 2, s_)
        s_ = list(idle); s_[axis] = closed; key_scale(mouth, fb + 1, s_)

def hablar(voices):
    """Mueve las bocas según los tiempos de cada palabra (voces.json)."""
    key_scale(CL["mouth"], 1, (1, 0.45, 1)); key_scale(AL["mouth"], 1, (1.6, 0.5, 0.25))
    for line in voices:
        if line["who"] == "Clod":
            visemes(CL["mouth"], line, 1, 0.45, 1.6, (1, 0.45, 1))
        else:
            visemes(AL["mouth"], line, 2, 0.25, 1.1, (1.6, 0.5, 0.25))

def blink(eyes, f, base, axis):
    for e in eyes:
        s1 = list(base); s1[axis] = 0.1
        key_scale(e, f, base); key_scale(e, f + 3, s1); key_scale(e, f + 6, base)

