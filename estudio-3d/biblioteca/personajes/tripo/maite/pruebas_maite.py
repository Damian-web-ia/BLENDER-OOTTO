# PRUEBAS OBLIGATORIAS DE MAITE (skill AAA, punto 19) · EKORUEDAS · 28-11-2026
# Uso: blender -b --factory-startup --python pruebas_maite.py -- <carpeta_estudio> <carpeta_salida> <prueba> [muestras] [ancho]
#   prueba: expresiones | pelo | ropa | objeto | giro | primer_plano
# Cada prueba anima con la biblioteca de Maite (maite_anim.py), hornea trenza y tela, y saca un MP4 (o una foto 4K).
import bpy, os, sys, math, random
from mathutils import Vector, Matrix, Quaternion
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT, PRUEBA = argv[0], argv[1], argv[2]
MUESTRAS = int(argv[3]) if len(argv) > 3 else 32; ANCHO = int(argv[4]) if len(argv) > 4 else 1080
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(PM, "maite_v2.blend"))
sc = bpy.context.scene; sc.render.fps = 24
ARM = bpy.data.objects["MAITE_rig"]; ME = bpy.data.objects["MAITE_cuerpo"]; P = "mixamorig:"
MA = {}; exec(compile(open(os.path.join(PM, "maite_anim.py"), encoding="utf-8").read(), "maite_anim", "exec"), MA)
A = MA["MaiteAnim"](ARM)
# ---------------------------------------------------------------- estudio: luz de tres puntos, fondo oscuro, suelo
def luz(n, loc, e, tam, col, mira=(0, 0, 0.75)):
    d = bpy.data.lights.new(n, 'AREA'); d.energy = e; d.size = tam; d.color = col
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
luz("Clave", (-1.4, -2.0, 2.2), 380, 1.4, (1.0, 0.92, 0.84)); luz("Relleno", (1.8, -1.6, 1.3), 140, 1.8, (0.75, 0.82, 1.0))
luz("Contra", (0.6, 1.8, 2.0), 300, 1.0, (1.0, 0.85, 0.7), mira=(0, 0, 0.9))
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.032, 0.035, 0.042, 1)
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=3, fill_type='NGON', location=(0, 0, 0)); suelo = bpy.context.active_object
ms = bpy.data.materials.new("Suelo"); ms.use_nodes = True
ms.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.09, 0.095, 0.105, 1)
ms.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6; suelo.data.materials.append(ms)
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
def camara(loc, mira, lente, f=None):
    cam.location = loc; cd.lens = lente; cam.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    if f is not None: cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = 'GPU'
except Exception as e: print("GPU", e)
sc.render.engine = 'CYCLES'; sc.cycles.samples = MUESTRAS; sc.cycles.use_denoising = True
sc.render.resolution_x = ANCHO; sc.render.resolution_y = int(ANCHO * 4 / 3) if PRUEBA != "giro" else int(ANCHO * 16 / 9)
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.35

def base(f0, f1):
    A.pose_reposo(f0); A.mano(f0, "L", "relajada"); A.mano(f0, "R", "relajada")
    A.respirar(f0, f1); A.vida(f0, f1)

def hornear_y_video(f0, f1, nombre):
    sc.frame_start, sc.frame_end = f0, f1
    A.finalizar(f0, f1)
    for ob in bpy.data.objects:
        for md in ob.modifiers:
            if md.type == 'CLOTH': md.point_cache.frame_start = f0; md.point_cache.frame_end = f1
    sc.frame_set(f0)
    with bpy.context.temp_override(scene=sc): bpy.ops.ptcache.bake_all(bake=True)
    ims = sc.render.image_settings
    if hasattr(ims, "media_type"): ims.media_type = 'VIDEO'          # Blender 5: el vídeo es un "tipo de medio" aparte
    ims.file_format = 'FFMPEG'; sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'
    sc.render.ffmpeg.constant_rate_factor = 'HIGH'; sc.render.ffmpeg.ffmpeg_preset = 'REALTIME'
    sc.render.filepath = os.path.join(OUT, nombre + ".mp4")
    bpy.ops.render.render(animation=True)
    print("VIDEO_OK", nombre, flush=True)

if PRUEBA == "expresiones":
    # 1 — Expresiones con transiciones, parpadeo, mirada viva y cabeza viva (10 s)
    f0, f1 = 1, 240; base(f0, f1)
    secuencia = [(1, "neutra"), (24, "alegria"), (54, "sorpresa"), (84, "enfado"), (114, "tristeza"), (144, "pensamiento"),
                 (174, "risa"), (204, "guino"), (228, "neutra")]
    for f, e in secuencia:
        A.expresion(f, e); A.expresion(f + 16, e)
    A.cabeza(60, arriba=4); A.cabeza(90, arriba=-3, ladeo=-3); A.cabeza(120, arriba=-6, ladeo=4); A.cabeza(150, giro=-8, arriba=5)
    A.cabeza(180, arriba=2, ladeo=5); A.cabeza(210, giro=6); A.cabeza(236)
    A.parpadeos_auto(f0, f1, evitar=[(200, 222)]); A.mirada_viva(f0, f1)
    A.mirar(140, 0.10, 0.12); A.mirar(165, 0.10, 0.12); A.mirar(172, 0, 0)
    camara((0.10, -0.62, 0.90), (0.02, 0.0, 0.86), 85)
    hornear_y_video(f0, f1, "prueba1_expresiones")
elif PRUEBA == "pelo":
    # 3 — Giros de cabeza rápidos, cambios de dirección: la trenza reacciona con retraso (6 s)
    f0, f1 = 1, 144; base(f0, f1)
    for f, g, a_, t in ((1, 0, 0, 0), (14, 0, 0, 0), (22, 38, 0, 15), (34, 38, 4, 15), (42, -40, 0, -18), (56, -40, -5, -18),
                        (64, 0, 12, 0), (76, 0, -14, 0), (88, 30, 0, 20), (94, -30, 0, -20), (100, 30, 0, 20), (110, 0, 0, 0), (144, 0, 0, 0)):
        A.cabeza(f, arriba=a_, giro=g); A.torso(f, giro=t * 0.6)
    A.expresion(1, "sonrisa_natural"); A.parpadeos_auto(f0, f1); A.mirada_viva(f0, f1)
    camara((0.60, -1.05, 0.95), (0.02, 0.0, 0.78), 55)
    hornear_y_video(f0, f1, "prueba3_pelo")
elif PRUEBA == "ropa":
    # 4 — Llega andando (pies plantados), brazos arriba, se agacha, gira y saluda: mangas con tela (10,5 s)
    S = 60; f0, f1 = 1, 192 + S; base(f0, f1)
    fw = A.caminar(1, pasos=4, zancada=0.27, frames_paso=14, inicio=(0.0, 0.81, 0.0))
    A.brazo(fw + 2, "L", "reposo"); A.brazo(fw + 2, "R", "reposo")
    arriba_b, arriba_a = (-0.35, 0.0, 0.94), (-0.10, -0.05, 0.99)
    A.brazo(20 + S, "L", "reposo"); A.brazo(20 + S, "R", "reposo")
    for f in (40 + S, 56 + S):
        A.brazo(f, "L", "reposo", d_brazo=arriba_b, d_ante=arriba_a); A.brazo(f, "R", "reposo", d_brazo=arriba_b, d_ante=arriba_a)
    A.brazo(76 + S, "L", "explica"); A.brazo(76 + S, "R", "explica")
    A.caderas(76 + S); A.caderas(96 + S, baja=0.10); A.torso(96 + S, adelante=18); A.caderas(116 + S, baja=0.10); A.torso(116 + S, adelante=18)
    A.caderas(136 + S); A.torso(136 + S); A.torso(150 + S, giro=25); A.brazo(150 + S, "R", "saluda"); A.brazo(150 + S, "L", "jarras")
    A.brazo(164 + S, "R", "saluda", d_ante=(-0.55, 0.0, 0.83)); A.brazo(176 + S, "R", "saluda"); A.torso(176 + S, giro=25)
    A.brazo(192 + S, "R", "saluda", d_ante=(-0.55, 0.0, 0.83))
    A.expresion(1, "sonrisa_natural"); A.expresion(150 + S, "alegria"); A.parpadeos_auto(f0, f1); A.mirada_viva(f0, f1)
    camara((1.05, -2.35, 0.80), (0.0, 0.25, 0.55), 42)
    hornear_y_video(f0, f1, "prueba4_ropa")
elif PRUEBA == "objeto":
    # 5 — Interacción con una pieza mecánica: coge la llave de cruz, la mira, la gira y la enseña a cámara (7 s)
    UT = {}; exec(compile(open(os.path.join(PM, "utileria_maite.py"), encoding="utf-8").read(), "utileria", "exec"), UT)
    f0, f1 = 1, 168; base(f0, f1)
    A.brazo(1, "R", "agarra"); A.mano(1, "R", "empuna"); sc.frame_set(1)
    llave = UT["llave_cruz"](); UT["agarrar"](ARM, llave, "R")
    A.mano(1, "R", "empuna")            # empieza ya con la llave delante (con el brazo abajo la cruz atravesaba el cuerpo)
    A.brazo(24, "R", "agarra"); A.mano(24, "R", "empuna"); A.cabeza(24, arriba=-12, giro=-10)
    A.mirar(24, -0.05, -0.12); A.expresion(24, "curiosidad")
    A.mano(48, "R", "empuna", muneca=(0, 45, 0)); A.cabeza(48, arriba=-10, giro=-14, ladeo=4); A.expresion(48, "concentracion")
    A.mano(72, "R", "empuna", muneca=(0, -35, 10)); A.cabeza(72, arriba=-8, giro=-8)
    A.brazo(100, "R", "presenta"); A.mano(100, "R", "empuna", muneca=(0, 0, -10)); A.cabeza(100); A.mirar(100, 0, 0)
    A.expresion(100, "alegria"); A.brazo(140, "R", "presenta"); A.brazo(150, "L", "jarras")
    A.parpadeos_auto(f0, f1, evitar=[(20, 30)]); A.mirada_viva(100, f1)
    camara((0.55, -1.35, 0.86), (0.0, 0.0, 0.70), 50)
    hornear_y_video(f0, f1, "prueba5_objeto")
elif PRUEBA == "giro":
    # 8 — Turntable: la cámara da una vuelta completa alrededor de Maite en reposo (8 s)
    f0, f1 = 1, 192; base(f0, f1); A.expresion(1, "sonrisa_natural"); A.parpadeos_auto(f0, f1)
    sc.render.use_motion_blur = False
    eje = bpy.data.objects.new("Eje_giro", None); sc.collection.objects.link(eje); eje.location = (0.01, 0.0, 0.0)
    camara((0.01, -2.3, 0.85), (0.01, 0.0, 0.52), 50); cam.parent = eje; cam.location = (0.0, -2.3, 0.85)
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    eje.rotation_euler = (0, 0, 0); eje.keyframe_insert("rotation_euler", frame=f0)
    eje.rotation_euler = (0, 0, 2 * math.pi); eje.keyframe_insert("rotation_euler", frame=f1 + 1)
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'BEZIER'
    hornear_y_video(f0, f1, "prueba8_giro")
elif PRUEBA == "primer_plano":
    # 6 — Primer plano 4K vertical del rostro (foto)
    base(1, 2); A.expresion(1, "sonrisa_natural"); A.finalizar(1, 2, trenza=False)
    sc.render.resolution_x, sc.render.resolution_y = 2160, 3840
    camara((0.16, -0.70, 0.90), (0.02, 0.0, 0.84), 105); sc.frame_set(1)
    sc.render.filepath = os.path.join(OUT, "prueba6_primer_plano_4k.png"); bpy.ops.render.render(write_still=True)
    print("FOTO_OK prueba6", flush=True)
open(os.path.join(OUT, f"HECHO_{PRUEBA}.txt"), "w").write("ok"); print("PRUEBA_OK", PRUEBA, flush=True)
