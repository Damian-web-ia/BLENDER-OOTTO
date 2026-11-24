import bpy, math, os
from mathutils import Vector

OUT_DIR = r"C:\Users\EKORUEDAS\Desktop\CLAUDE VIDEOS"
FPS = 30
# word timings (s) from the Ootto voice (Diego)
WORDS = [("¡Hola",0.12,0.49),("Soy",0.608,0.77),("Claude",0.77,1.04),("el",1.165,1.18),("aprendiz",1.18,1.58),("de",1.66,1.66),("mecánico",1.66,2.11),("Hoy",2.11,2.26),("voy",2.34,2.42),("a",2.42,2.5),("cambiar",2.5,2.74),("una",2.82,2.9),("rueda",2.98,3.22),("yo",3.22,3.38),("solito",3.38,3.82),("¿Alguien",3.838,4.14),("sabe",4.22,4.3),("dónde",4.38,4.54),("se",4.54,4.62),("enchufa",4.62,5.1)]
LEAD = 0.6   # seconds of animation before the voice starts
TOTAL = LEAD + 5.22 + 1.0
f = lambda t: int(round((t) * FPS)) + 1

# ---------- clean scene ----------
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
    for d in list(coll):
        if d.users == 0:
            coll.remove(d)
sc.render.fps = FPS
sc.frame_start = 1
sc.frame_end = f(TOTAL)
sc.render.resolution_x = 1080
sc.render.resolution_y = 1920
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        sc.render.engine = eng
        break
    except Exception:
        pass
try:
    sc.eevee.taa_render_samples = 32
except Exception:
    pass

def mat(name, color, rough=0.4, metal=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        for k in ("Emission Color", "Emission"):
            if k in b.inputs:
                b.inputs[k].default_value = (*emit, 1)
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = emit_strength
    return m

ORANGE = mat("Naranja", (1.0, 0.33, 0.02), 0.35)
DARK = mat("NegroMate", (0.02, 0.02, 0.025), 0.5)
SCREEN = mat("Pantalla", (0.005, 0.005, 0.008), 0.15)
LED = mat("LED", (1, 1, 1), 0.3, emit=(1, 1, 1), emit_strength=6)
GREY = mat("Gris", (0.12, 0.12, 0.13), 0.6, 0.3)
FLOOR = mat("Suelo", (0.22, 0.22, 0.23), 0.35)
WALL = mat("Pared", (0.09, 0.095, 0.1), 0.8)
RUBBER = mat("Goma", (0.03, 0.03, 0.03), 0.8)
RIM = mat("Llanta", (0.7, 0.7, 0.72), 0.25, 0.9)

def add(obj_op, name, mat_=None, parent=None, **kw):
    obj_op(**kw)
    o = bpy.context.active_object
    o.name = name
    if mat_:
        o.data.materials.append(mat_)
    if parent:
        o.parent = parent
    return o

def bevel(o, w=0.08, seg=4):
    m = o.modifiers.new("bev", "BEVEL"); m.width = w; m.segments = seg
    bpy.ops.object.shade_smooth()
    return o

# ---------- robot Claude ----------
root = bpy.data.objects.new("Claude", None); sc.collection.objects.link(root)
body = add(bpy.ops.mesh.primitive_uv_sphere_add, "Cuerpo", ORANGE, root, radius=0.42, location=(0, 0, 0.78), segments=48, ring_count=24)
body.scale = (1, 0.85, 1.1); bpy.ops.object.shade_smooth()
# chest symbol: 6 thin white bars (asterisk)
for i in range(6):
    b = add(bpy.ops.mesh.primitive_cube_add, f"Simbolo{i}", LED, body, size=1, location=(0, -0.41, 0.0))
    b.scale = (0.025, 0.01, 0.12); b.rotation_euler = (0, math.radians(i * 30), 0)
    b.location = (0, -0.41 / 0.85, 0.05)
head_pivot = bpy.data.objects.new("CabezaPivote", None); sc.collection.objects.link(head_pivot)
head_pivot.parent = root; head_pivot.location = (0, 0, 1.25)
head = add(bpy.ops.mesh.primitive_cube_add, "Cabeza", ORANGE, head_pivot, size=1, location=(0, 0, 0.42))
head.scale = (1.15, 0.85, 0.85); bevel(head, 0.18, 6)
screen = add(bpy.ops.mesh.primitive_cube_add, "Pantalla", SCREEN, head_pivot, size=1, location=(0, -0.37, 0.42))
screen.scale = (0.92, 0.12, 0.62); bevel(screen, 0.1, 6)
eyeL = add(bpy.ops.mesh.primitive_cylinder_add, "OjoI", LED, head_pivot, radius=0.11, depth=0.02, location=(-0.2, -0.44, 0.5), rotation=(math.radians(90), 0, 0))
eyeR = add(bpy.ops.mesh.primitive_cylinder_add, "OjoD", LED, head_pivot, radius=0.11, depth=0.02, location=(0.2, -0.44, 0.5), rotation=(math.radians(90), 0, 0))
mouth = add(bpy.ops.mesh.primitive_torus_add, "Boca", LED, head_pivot, major_radius=0.12, minor_radius=0.018, location=(0, -0.44, 0.27), rotation=(math.radians(90), 0, 0))
mouth.scale = (1, 0.45, 1)
for s, x in (("I", -0.62), ("D", 0.62)):
    ph = add(bpy.ops.mesh.primitive_cylinder_add, f"Auricular{s}", ORANGE, head_pivot, radius=0.2, depth=0.14, location=(x, 0, 0.42), rotation=(0, math.radians(90), 0))
    bpy.ops.object.shade_smooth()
    ring = add(bpy.ops.mesh.primitive_torus_add, f"AroAuricular{s}", DARK, head_pivot, major_radius=0.15, minor_radius=0.035, location=(x * 1.08, 0, 0.42), rotation=(0, math.radians(90), 0))
arms = {}
for s, x in (("I", -0.5), ("D", 0.5)):
    sh = bpy.data.objects.new(f"Hombro{s}", None); sc.collection.objects.link(sh)
    sh.parent = root; sh.location = (x, 0, 1.02)
    arm = add(bpy.ops.mesh.primitive_cylinder_add, f"Brazo{s}", ORANGE, sh, radius=0.09, depth=0.45, location=(0, 0, -0.22))
    bpy.ops.object.shade_smooth()
    hand = add(bpy.ops.mesh.primitive_uv_sphere_add, f"Mano{s}", DARK, sh, radius=0.11, location=(0, 0, -0.48))
    bpy.ops.object.shade_smooth()
    arms[s] = sh
for s, x in (("I", -0.2), ("D", 0.2)):
    leg = add(bpy.ops.mesh.primitive_cylinder_add, f"Pierna{s}", DARK, root, radius=0.09, depth=0.3, location=(x, 0, 0.3)); bpy.ops.object.shade_smooth()
    foot = add(bpy.ops.mesh.primitive_cube_add, f"Pie{s}", ORANGE, root, size=1, location=(x, -0.05, 0.08)); foot.scale = (0.22, 0.32, 0.14); bevel(foot, 0.05, 3)

# ---------- workshop ----------
fl = add(bpy.ops.mesh.primitive_plane_add, "Suelo", FLOOR, size=30)
wall = add(bpy.ops.mesh.primitive_plane_add, "Pared", WALL, size=30, location=(0, 4, 0), rotation=(math.radians(90), 0, 0))
bench = add(bpy.ops.mesh.primitive_cube_add, "Banco", GREY, size=1, location=(2.2, 2.6, 0.5)); bench.scale = (2.2, 0.8, 1.0); bevel(bench, 0.03, 2)
tyre = add(bpy.ops.mesh.primitive_torus_add, "Rueda", RUBBER, major_radius=0.42, minor_radius=0.18, location=(1.25, 0.2, 0.6), rotation=(math.radians(90), 0, math.radians(-25)))
bpy.ops.object.shade_smooth()
rim = add(bpy.ops.mesh.primitive_cylinder_add, "Llanta", RIM, radius=0.3, depth=0.2, location=(1.25, 0.2, 0.6), rotation=(math.radians(90), 0, math.radians(-25)))
bpy.ops.object.shade_smooth()
for i, x in enumerate((-2.5, -1.2, 0.1, 1.4, 2.7)):
    lamp = add(bpy.ops.mesh.primitive_cylinder_add, f"Lampara{i}", LED, radius=0.12, depth=0.05, location=(x, 3.2, 3.6))

# lights
def light(name, kind, loc, energy, color=(1, 0.85, 0.7), size=2.0, rot=(0, 0, 0)):
    d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color
    if kind == "AREA": d.size = size
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = rot
    return o
light("Clave", "AREA", (-2.2, -2.5, 3.2), 900, size=3, rot=(math.radians(55), 0, math.radians(-40)))
light("Relleno", "AREA", (2.5, -2.0, 1.8), 300, color=(0.8, 0.9, 1.0), size=3, rot=(math.radians(70), 0, math.radians(50)))
light("Contra", "AREA", (0, 2.5, 3.0), 600, color=(1, 0.6, 0.3), size=2, rot=(math.radians(-50), 0, 0))
w = sc.world or bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.025, 1)

# camera
cam_d = bpy.data.cameras.new("Camara"); cam_d.lens = 40
cam = bpy.data.objects.new("Camara", cam_d); sc.collection.objects.link(cam); sc.camera = cam
target = bpy.data.objects.new("Objetivo", None); sc.collection.objects.link(target); target.location = (0.15, 0, 1.25)
tc = cam.constraints.new("TRACK_TO"); tc.target = target; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
try:
    cam_d.dof.use_dof = True; cam_d.dof.focus_object = target; cam_d.dof.aperture_fstop = 2.8
except Exception:
    pass
cam.location = (0.4, -5.2, 1.6); cam.keyframe_insert("location", frame=1)
cam.location = (0.25, -3.9, 1.45); cam.keyframe_insert("location", frame=f(TOTAL))

# ---------- animation ----------
def key(o, path, frame, value, idx=None):
    if idx is None:
        setattr(o, path, value); o.keyframe_insert(path, frame=frame)
    else:
        getattr(o, path)[idx] = value; o.keyframe_insert(path, index=idx, frame=frame)

# hop in from the left
for t, x, z in ((0.0, -2.4, 0.0), (0.15, -1.8, 0.35), (0.3, -1.2, 0.0), (0.45, -0.6, 0.3), (0.6, 0.0, 0.0)):
    key(root, "location", f(t), x, 0); key(root, "location", f(t), z, 2)
# idle bob while talking
t = LEAD
while t < TOTAL:
    key(root, "location", f(t), 0.0, 2); key(root, "location", f(t + 0.4), 0.04, 2); t += 0.8

# mouth: open on every word
key(mouth, "scale", 1, 0.45, 1)
for w_, a, b in WORDS:
    a += LEAD; b += LEAD
    key(mouth, "scale", f(a) - 1, 0.45, 1)
    key(mouth, "scale", f((a + b) / 2), 1.6, 1)
    key(mouth, "scale", f(b) + 1, 0.45, 1)

# eyes: blinks, happy squint on "Hola", wide on the question
def eyes(frame, sy):
    for e in (eyeL, eyeR):
        key(e, "scale", frame, sy, 1)
eyes(1, 1.0)
eyes(f(LEAD + 0.1), 1.0); eyes(f(LEAD + 0.2), 0.35); eyes(f(LEAD + 0.6), 0.35); eyes(f(LEAD + 0.7), 1.0)
for bt in (2.2, 3.6):
    eyes(f(LEAD + bt), 1.0); eyes(f(LEAD + bt + 0.05), 0.1); eyes(f(LEAD + bt + 0.12), 1.0)
eyes(f(LEAD + 3.85), 1.0); eyes(f(LEAD + 4.0), 1.35); eyes(f(TOTAL), 1.35)

# wave on "Hola"
R = arms["D"]
key(R, "rotation_euler", 1, 0.0, 1)
key(R, "rotation_euler", f(LEAD), 0.0, 1)
for i, ang in enumerate((150, 120, 150, 120, 150)):
    key(R, "rotation_euler", f(LEAD + 0.1 + i * 0.18), math.radians(ang), 1)
key(R, "rotation_euler", f(LEAD + 1.3), 0.0, 1)
# head tilt on the question
key(head_pivot, "rotation_euler", f(LEAD + 3.7), 0.0, 1)
key(head_pivot, "rotation_euler", f(LEAD + 4.1), math.radians(14), 1)
key(head_pivot, "rotation_euler", f(TOTAL), math.radians(14), 1)
# point at the tyre on "rueda"
L = arms["I"]
key(L, "rotation_euler", f(LEAD + 2.6), 0.0, 1)
key(L, "rotation_euler", f(LEAD + 3.0), math.radians(-80), 1)
key(L, "rotation_euler", f(LEAD + 3.7), math.radians(-80), 1)
key(L, "rotation_euler", f(LEAD + 4.0), 0.0, 1)

# ---------- output ----------
os.makedirs(OUT_DIR, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "prueba_claude_3d.blend"))
result = {"frames": sc.frame_end, "engine": sc.render.engine, "version": bpy.app.version_string}
