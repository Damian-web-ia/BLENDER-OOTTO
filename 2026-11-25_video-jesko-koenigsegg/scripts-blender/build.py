# EKORUEDAS - "La caja de cambios imposible" (Koenigsegg Jesko / LST)
# Construye la escena completa en Blender 5.x. Ejecutar dentro de Blender.
# Geometría procedural y aproximada: NO es un modelo oficial del Jesko.
# El interior de la caja LST es ILUSTRATIVO (no la topología real de Koenigsegg).
import bpy, bmesh, math, json, os
from mathutils import Vector, Matrix

ROOT = r"C:\Users\EKORUEDAS\Desktop\CLAUDE VIDEOS\JESKO"
FPS = 30
END = 1800
VOICES = json.load(open(os.path.join(ROOT, "data", "voices.json"), encoding="utf-8"))
LOGO = os.path.join(ROOT, "assets", "logo_ekoruedas.png")

def fr(t):  # segundos -> fotograma
    return int(round(t * FPS)) + 1

# ----------------------------------------------------------------- limpieza
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
sc.render.resolution_x, sc.render.resolution_y = 2160, 3840
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "AgX"
try:
    sc.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass

COLL = {}
for n in ("WORKSHOP", "STUDIO", "LAB", "JESKO", "LST", "ALEX", "CLAUDE", "CAMERAS", "TEXTS"):
    c = bpy.data.collections.new(n); sc.collection.children.link(c); COLL[n] = c

def link(o, cname):
    for c in o.users_collection:
        c.objects.unlink(o)
    COLL[cname].objects.link(o)
    return o

# ----------------------------------------------------------------- materiales
def mat(name, color, rough=0.4, metal=0.0, coat=0.0, emit=None, es=0.0, alpha=1.0, trans=0.0, ior=1.45):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["IOR"].default_value = ior
    if trans:
        b.inputs["Transmission Weight"].default_value = trans
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

def carbon(name="Carbono"):
    m = mat(name, (0.02, 0.02, 0.022), 0.25, 0.1, coat=1.0)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (60, 60, 60)
    ck = nt.nodes.new("ShaderNodeTexChecker")
    ck.inputs["Color1"].default_value = (0.012, 0.012, 0.014, 1); ck.inputs["Color2"].default_value = (0.05, 0.05, 0.055, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], ck.inputs["Vector"])
    nt.links.new(ck.outputs["Color"], b.inputs["Base Color"])
    return m

M = {
    "pearl": mat("PinturaPerlada", (0.86, 0.87, 0.9), 0.18, 0.35, coat=1.0),
    "carbon": carbon(),
    "glass": mat("Cristal", (0.02, 0.03, 0.04), 0.02, 0.0, alpha=0.35, ior=1.5),
    "rubber": mat("Caucho", (0.018, 0.018, 0.02), 0.85),
    "rim": mat("Llanta", (0.06, 0.06, 0.065), 0.25, 1.0, coat=0.5),
    "steel": mat("AceroMecanizado", (0.62, 0.63, 0.65), 0.22, 1.0),
    "alu": mat("Aluminio", (0.8, 0.81, 0.83), 0.3, 1.0),
    "brass": mat("Bronce", (0.75, 0.55, 0.25), 0.3, 1.0),
    "friction": mat("Friccion", (0.35, 0.16, 0.06), 0.8, 0.0),
    "caliper": mat("Pinza", (0.95, 0.35, 0.02), 0.3, 0.0, coat=1.0),
    "lightW": mat("FaroLED", (1, 1, 1), 0.2, emit=(0.85, 0.92, 1.0), es=8),
    "lightR": mat("PilotoRojo", (0.5, 0, 0), 0.2, emit=(1, 0.03, 0.02), es=6),
    "engine": mat("Motor", (0.12, 0.12, 0.13), 0.35, 0.8),
    "pcb": mat("PlacaECU", (0.02, 0.18, 0.08), 0.4, 0.0, emit=(0.1, 1, 0.4), es=0.0),
    "chip": mat("Chip", (0.02, 0.02, 0.02), 0.3),
    "route": mat("RutaEnergia", (1, 0.45, 0.0), 0.3, emit=(1, 0.45, 0.02), es=0.0),
    # personajes
    "orange": mat("NaranjaClaude", (0.95, 0.22, 0.0), 0.35, coat=0.6),
    "dark": mat("NegroMate", (0.02, 0.02, 0.025), 0.5),
    "screen": mat("Pantalla", (0.004, 0.004, 0.006), 0.1, coat=1.0),
    "led": mat("LED", (1, 1, 1), 0.3, emit=(1, 1, 1), es=5),
    "ledR": mat("LEDRojo", (1, 0.1, 0.05), 0.3, emit=(1, 0.08, 0.03), es=5),
    "skin": mat("Piel", (0.42, 0.24, 0.15), 0.5),
    "hair": mat("Pelo", (0.03, 0.022, 0.018), 0.6),
    "beard": mat("Barba", (0.06, 0.05, 0.045), 0.8),
    "uniform": mat("Uniforme", (0.025, 0.025, 0.03), 0.7),
    "piping": mat("Ribete", (0.95, 0.35, 0.02), 0.5),
    "eyeW": mat("OjoBlanco", (0.9, 0.9, 0.88), 0.2),
    "iris": mat("Iris", (0.06, 0.035, 0.02), 0.2, coat=1.0),
    "mouth": mat("Boca", (0.12, 0.03, 0.03), 0.6),
    "boot": mat("Bota", (0.05, 0.04, 0.035), 0.5),
    # entornos
    "floorW": mat("SueloTaller", (0.09, 0.09, 0.095), 0.3, coat=0.3),
    "wallW": mat("ParedTaller", (0.12, 0.125, 0.13), 0.8),
    "red": mat("RojoArmario", (0.45, 0.02, 0.02), 0.3, 0.3, coat=0.5),
    "blue": mat("AzulElevador", (0.02, 0.12, 0.35), 0.35, 0.5),
    "warm": mat("LamparaCalida", (1, 0.8, 0.5), 0.3, emit=(1, 0.72, 0.42), es=15),
    "cyc": mat("Ciclorama", (0.03, 0.032, 0.036), 0.5),
    "white3d": mat("Texto3DBlanco", (1, 1, 1), 0.3, emit=(1, 1, 1), es=2.5),
    "orange3d": mat("Texto3DNaranja", (1, 0.4, 0.0), 0.3, emit=(1, 0.38, 0.0), es=3.5),
    "grey3d": mat("Texto3DGris", (0.3, 0.3, 0.3), 0.5, emit=(0.3, 0.3, 0.3), es=0.4),
}

def logo_mat():
    m = bpy.data.materials.new("LogoEkoruedas"); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(LOGO)
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.6
    try:
        m.surface_render_method = "DITHERED"
    except Exception:
        pass
    return m
M["logo"] = logo_mat()

# ----------------------------------------------------------------- utilidades de modelado
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
        verts = []
        for i in range(s1):
            a = 2 * math.pi * i / s1
            row = []
            for j in range(s2):
                b_ = 2 * math.pi * j / s2
                row.append(bm.verts.new(((R + rr * math.cos(b_)) * math.cos(a), (R + rr * math.cos(b_)) * math.sin(a), rr * math.sin(b_))))
            verts.append(row)
        for i in range(s1):
            for j in range(s2):
                bm.faces.new((verts[i][j], verts[(i + 1) % s1][j], verts[(i + 1) % s1][(j + 1) % s2], verts[i][(j + 1) % s2]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o = new_obj(name, me, cname, m, parent, loc)
    o.rotation_euler = rot; o.scale = scale
    if kw.get("bevel"):
        md = o.modifiers.new("bev", "BEVEL"); md.width = kw["bevel"]; md.segments = kw.get("bseg", 3)
    return o

def loft(name, cname, sections, m, parent=None, closed_ends=True, smooth=True):
    """sections: lista de listas de puntos (x,y,z) con el mismo número de puntos (anillos)."""
    bm = bmesh.new()
    rings = [[bm.verts.new(p) for p in s] for s in sections]
    n = len(sections[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    if closed_ends:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return new_obj(name, me, cname, m, parent)

def superellipse(cx, y, cz, hw, hh, n=3.2, seg=40, zmin=None):
    pts = []
    for i in range(seg):
        t = 2 * math.pi * i / seg
        c, s = math.cos(t), math.sin(t)
        x = cx + hw * math.copysign(abs(c) ** (2 / n), c)
        z = cz + hh * math.copysign(abs(s) ** (2 / n), s)
        if zmin is not None:
            z = max(z, zmin)
        pts.append((x, y, z))
    return pts

def text3d(name, body, m, size=0.3, depth=0.03, align="CENTER", parent=None, loc=(0, 0, 0), rot=(math.radians(90), 0, 0)):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.extrude = depth
    cu.align_x = align; cu.align_y = "CENTER"; cu.bevel_depth = depth * 0.15
    o = bpy.data.objects.new(name, cu); COLL["TEXTS"].objects.link(o); cu.materials.append(m)
    o.location = loc; o.rotation_euler = rot
    if parent:
        o.parent = parent
    return o

def gear_mesh(name, teeth, r, width, cname, m, parent=None, loc=(0, 0, 0), bore=0.25):
    """Engranaje recto: perfil con dientes trapezoidales extruido a lo largo de Y local."""
    bm = bmesh.new()
    tooth_h = max(0.012, r * 0.09)
    prof = []
    for i in range(teeth):
        a0 = 2 * math.pi * i / teeth
        da = 2 * math.pi / teeth
        for frac, rad in ((0.0, r - tooth_h), (0.18, r - tooth_h), (0.3, r + tooth_h * 0.4), (0.62, r + tooth_h * 0.4), (0.74, r - tooth_h)):
            a = a0 + frac * da
            prof.append((rad * math.cos(a), rad * math.sin(a)))
    inner = [(bore * r * math.cos(2 * math.pi * i / len(prof)), bore * r * math.sin(2 * math.pi * i / len(prof))) for i in range(len(prof))]
    y0, y1 = -width / 2, width / 2
    O0 = [bm.verts.new((x, y0, z)) for x, z in prof]; O1 = [bm.verts.new((x, y1, z)) for x, z in prof]
    I0 = [bm.verts.new((x, y0, z)) for x, z in inner]; I1 = [bm.verts.new((x, y1, z)) for x, z in inner]
    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((O0[i], O0[j], O1[j], O1[i]))
        bm.faces.new((I0[j], I0[i], I1[i], I1[j]))
        bm.faces.new((O0[j], O0[i], I0[i], I0[j]))
        bm.faces.new((O1[i], O1[j], I1[j], I1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return new_obj(name, me, cname, m, parent, loc)

def ring(name, r_out, r_in, width, cname, m, parent=None, loc=(0, 0, 0), seg=48):
    bm = bmesh.new()
    O0 = [bm.verts.new((r_out * math.cos(2 * math.pi * i / seg), -width / 2, r_out * math.sin(2 * math.pi * i / seg))) for i in range(seg)]
    O1 = [bm.verts.new((v.co.x, width / 2, v.co.z)) for v in O0]
    I0 = [bm.verts.new((r_in * math.cos(2 * math.pi * i / seg), -width / 2, r_in * math.sin(2 * math.pi * i / seg))) for i in range(seg)]
    I1 = [bm.verts.new((v.co.x, width / 2, v.co.z)) for v in I0]
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((O0[i], O0[j], O1[j], O1[i])); bm.faces.new((I0[j], I0[i], I1[i], I1[j]))
        bm.faces.new((O0[j], O0[i], I0[i], I0[j])); bm.faces.new((O1[i], O1[j], I1[j], I1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return new_obj(name, me, cname, m, parent, loc)

def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def key_loc(o, frame, loc):
    o.location = loc; o.keyframe_insert("location", frame=frame)

def key_rot(o, frame, rot):
    o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=frame)

def key_scale(o, frame, s):
    o.scale = s; o.keyframe_insert("scale", frame=frame)

def key_hide(o, frame, hidden):
    o.hide_render = hidden; o.hide_viewport = hidden
    o.keyframe_insert("hide_render", frame=frame); o.keyframe_insert("hide_viewport", frame=frame)
    for c in o.children_recursive:
        c.hide_render = hidden; c.keyframe_insert("hide_render", frame=frame)

def key_emit(m, frame, strength):
    s = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    s.default_value = strength; s.keyframe_insert("default_value", frame=frame)

def set_constant(o):
    ad = o.animation_data
    if ad and ad.action:
        try:
            for fc in ad.action.fcurves:
                for k in fc.keyframe_points:
                    k.interpolation = "CONSTANT"
        except Exception:
            pass

exec(open(os.path.join(ROOT, "scripts", "models.py"), encoding="utf-8").read())
exec(open(os.path.join(ROOT, "scripts", "characters.py"), encoding="utf-8").read())
exec(open(os.path.join(ROOT, "scripts", "animation.py"), encoding="utf-8").read())

os.makedirs(os.path.join(ROOT, "scenes"), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "scenes", "episode.blend"))
result = {"objects": len(bpy.data.objects), "frames": [sc.frame_start, sc.frame_end], "markers": len(sc.timeline_markers)}
