# PRUEBAS OBLIGATORIAS DE MAITE (skill AAA, punto 19) · EKORUEDAS · 28-11-2026
# Uso: blender -b --factory-startup --python pruebas_maite.py -- <carpeta_estudio> <carpeta_salida> <prueba> [muestras] [ancho]
#   prueba: expresiones | dialogo <carpeta_voz> | pelo | ropa | objeto | cine [carpeta_voz] | giro | primer_plano | demo_cara [carpeta_voz]
#   MAITE_FPS=60 cambia los fotogramas por segundo (demo_cara); MAITE_FOTOS="2,6.5,…" (segundos) saca fotos de control en vez del vídeo.
# Cada prueba anima con la biblioteca de Maite (maite_anim.py), hornea trenza y tela, y saca un MP4 (o una foto 4K).
import bpy, os, sys, math, random
from mathutils import Vector, Matrix, Quaternion
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT, PRUEBA = argv[0], argv[1], argv[2]
MUESTRAS = int(argv[3]) if len(argv) > 3 else 32; ANCHO = int(argv[4]) if len(argv) > 4 else 1080
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.environ.get("MAITE_BLEND") or os.path.join(PM, "maite_v2.blend"))
sc = bpy.context.scene; sc.render.fps = int(os.environ.get("MAITE_FPS", "24"))
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
sc.render.resolution_x = ANCHO; sc.render.resolution_y = int(ANCHO * 4 / 3) if PRUEBA not in ("giro", "demo_cara") else int(ANCHO * 16 / 9)
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.35

def base(f0, f1):
    A.pose_reposo(f0); A.mano(f0, "L", "relajada"); A.mano(f0, "R", "relajada")
    A.respirar(f0, f1); A.vida(f0, f1)

def sonido(ruta, f_inicio=1):
    """Pone el audio en la escena (sale dentro del MP4, en AAC)."""
    ed = sc.sequence_editor or sc.sequence_editor_create()
    tiras = getattr(ed, "strips", None) or getattr(ed, "sequences")
    tiras.new_sound("voz", ruta, 1, f_inicio)
    sc.render.ffmpeg.audio_codec = 'AAC'; sc.render.ffmpeg.audio_bitrate = 192; sc.render.ffmpeg.audio_channels = 'STEREO'

def ciclorama():
    """Ciclorama oscuro (suelo que sube en curva hacia el fondo)."""
    import bmesh
    bm = bmesh.new(); R_, ancho_, n_ = 1.2, 6.0, 16
    perfil = [(-4.0, 0.0), (1.0, 0.0)] + [(1.0 + R_ * math.sin(a), R_ - R_ * math.cos(a)) for a in [math.pi / 2 * (i + 1) / n_ for i in range(n_)]] + [(1.0 + R_, 4.0)]
    filas = []
    for x_ in (-ancho_ / 2, ancho_ / 2):
        filas.append([bm.verts.new((x_, y_, z_)) for y_, z_ in perfil])
    for i in range(len(perfil) - 1):
        bm.faces.new((filas[0][i], filas[1][i], filas[1][i + 1], filas[0][i + 1]))
    mc = bpy.data.meshes.new("Ciclorama"); bm.to_mesh(mc); bm.free()
    for p_ in mc.polygons: p_.use_smooth = True
    cic = bpy.data.objects.new("Ciclorama", mc); sc.collection.objects.link(cic); cic.location = (0, 0.6, 0)
    mcm = bpy.data.materials.new("Ciclorama"); mcm.use_nodes = True
    mcm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.045, 0.05, 0.06, 1)
    mcm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.55; mc.materials.append(mcm)
    suelo.hide_render = True

def hornear_y_video(f0, f1, nombre):
    sc.frame_start, sc.frame_end = f0, f1
    A.finalizar(f0, f1)
    for ob in bpy.data.objects:
        for md in ob.modifiers:
            if md.type == 'CLOTH': md.point_cache.frame_start = f0; md.point_cache.frame_end = f1
    fotos = os.environ.get("MAITE_FOTOS")
    if fotos:                                    # fotos de control (sin tela) en los segundos pedidos, en vez del vídeo
        for ob in bpy.data.objects:
            for md in ob.modifiers:
                if md.type == 'CLOTH': md.show_render = False
        for t in fotos.split(","):
            f = f0 + int(round(float(t) * sc.render.fps)); sc.frame_set(f)
            sc.render.filepath = os.path.join(OUT, f"{nombre}_t{float(t):05.1f}.png"); bpy.ops.render.render(write_still=True)
            print("FOTO", nombre, t, flush=True)
        return
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
elif PRUEBA == "dialogo":
    # 2 — Diálogo en español con labios sincronizados a la voz (tiempos de cada palabra de la voz generada)
    # argv[5] = carpeta con voz.wav (o .mp3) y palabras.json ([{"text","start","end"}] en segundos)
    import json, glob
    CARP = argv[5]; pal = json.load(open(os.path.join(CARP, "palabras.json"), encoding="utf-8"))
    voz = (glob.glob(os.path.join(CARP, "voz.*")) or [None])[0]
    dur = max(w["end"] for w in pal); f0 = 1; f_hab = 13; f1 = f_hab + int(dur * 24) + 24
    base(f0, f1); A.expresion(1, "sonrisa_natural")
    A.hablar(pal, f_inicio=f_hab, intensidad=1.0)
    # gestos al hablar: cabeza que acompaña las frases, cejas en las palabras con acento, manos que explican
    for i, w in enumerate(pal):
        f = f_hab + int(w["start"] * 24)
        if i % 5 == 0: A.cabeza(f, arriba=2 if i % 10 == 0 else -2, giro=4 if i % 10 == 0 else -3, ladeo=2)
    A.brazo(f_hab + 20, "R", "explica"); A.brazo(f_hab + int(dur * 12), "R", "presenta"); A.brazo(f1 - 12, "R", "reposo")
    A.parpadeos_auto(f0, f1); A.mirada_viva(f0, f1)
    if voz: sonido(voz, f_hab)
    camara((0.12, -0.80, 0.88), (0.02, 0.0, 0.80), 70)
    hornear_y_video(f0, f1, "prueba2_dialogo")
elif PRUEBA == "cine":
    # 7 — Secuencia cinematográfica vertical 9:16: llega andando con la llave de cruz, se para, sonríe a cámara, enseña
    #     la llave, la mira, (habla si se da la carpeta de la voz) y guiña; cámara que la acompaña y se acerca, con
    #     desenfoque de fondo enfocado a la cara. Estudio: ciclorama oscuro, clave cálida, contra fría (estética EKORUEDAS).
    import json, glob
    UT = {}; exec(compile(open(os.path.join(PM, "utileria_maite.py"), encoding="utf-8").read(), "utileria", "exec"), UT)
    CARP = argv[5] if len(argv) > 5 else None
    pal = json.load(open(os.path.join(CARP, "palabras.json"), encoding="utf-8")) if CARP else []
    voz = (glob.glob(os.path.join(CARP, "voz.*")) or [None])[0] if CARP else None
    sc.render.resolution_x = ANCHO; sc.render.resolution_y = int(ANCHO * 16 / 9)
    ciclorama()
    suelo.hide_render = True
    luz("Contra_fria", (-1.2, 1.6, 1.9), 420, 1.2, (0.62, 0.78, 1.0), mira=(0, 0, 0.8))
    # la llave, en la mano derecha desde el principio
    A.brazo(1, "R", "agarra"); A.mano(1, "R", "empuna"); sc.frame_set(1)
    llave = UT["llave_cruz"](); UT["agarrar"](ARM, llave, "R")
    f0 = 1
    fw = A.caminar(1, pasos=5, zancada=0.27, frames_paso=14, inicio=(0.0, 1.08, 0.0), brazos=("L",))
    for f in (1, fw): A.brazo(f, "R", "agarra"); A.mano(f, "R", "empuna")
    A.expresion(1, "sonrisa_natural"); A.expresion(fw + 6, "alegria"); A.cabeza(fw + 6, arriba=2, ladeo=-3)
    A.brazo(fw + 24, "R", "presenta"); A.mano(fw + 24, "R", "empuna", muneca=(0, 0, -10)); A.expresion(fw + 28, "entusiasmo")
    A.brazo(fw + 56, "R", "agarra"); A.cabeza(fw + 56, arriba=-10, giro=-12); A.mirar(fw + 56, -0.05, -0.10)
    A.expresion(fw + 56, "curiosidad"); A.mano(fw + 76, "R", "empuna", muneca=(0, 40, 0))
    A.cabeza(fw + 96); A.mirar(fw + 96, 0, 0); A.mano(fw + 96, "R", "empuna")
    f_hab = fw + 100
    if pal:
        dur = max(w["end"] for w in pal); A.expresion(f_hab - 4, "sonrisa_natural")
        A.hablar(pal, f_inicio=f_hab)
        for i, w in enumerate(pal):
            if i % 5 == 0: A.cabeza(f_hab + int(w["start"] * 24), arriba=2 if i % 10 == 0 else -2, giro=3 if i % 10 == 0 else -3, ladeo=2)
        f_fin = f_hab + int(dur * 24) + 6
        if voz: sonido(voz, f_hab)
    else:
        A.expresion(f_hab, "sonrisa_natural"); f_fin = f_hab + 24
    A.expresion(f_fin, "guino"); A.expresion(f_fin + 18, "sonrisa_natural"); f1 = f_fin + 36
    A.parpadeos_auto(f0, f1, evitar=[(f_fin - 4, f_fin + 20)]); A.mirada_viva(fw, f1, amplitud=0.018)
    # cámara: acompaña la llegada y se acerca; enfoque a la cara
    foco = bpy.data.objects.new("Foco", None); sc.collection.objects.link(foco)
    cl_ = foco.constraints.new('COPY_LOCATION'); cl_.target = ARM; cl_.subtarget = "mixamorig:Head"
    cd.dof.use_dof = True; cd.dof.focus_object = foco; cd.dof.aperture_fstop = 2.8
    for f, loc, mira, lente in ((1, (0.30, -2.9, 0.50), (0.0, 0.9, 0.55), 38), (fw - 10, (0.18, -2.05, 0.68), (0.0, 0.15, 0.62), 48),
                               (fw + 40, (0.12, -1.55, 0.80), (0.0, 0.0, 0.72), 58), (f_hab, (0.08, -1.18, 0.86), (0.0, 0.0, 0.80), 66),
                               (f1, (0.05, -1.02, 0.88), (0.0, 0.0, 0.83), 72)):
        camara(loc, mira, lente, f)
        cd.keyframe_insert("lens", frame=f)
    hornear_y_video(f0, f1, "prueba7_cine")
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
elif PRUEBA == "demo_cara":
    # 13 — Demostración facial (prompt de la cara, punto 13), vertical 9:16, unos 42 s:
    #  1 neutra con respiración y parpadeos · 2 sonrisa progresiva · 3 cejas por separado · 4 miradas · 5 sorpresa
    #  6 sarcasmo · 7 risa · 8 concentración · 9 diálogo en español · 10 giros de cabeza con la trenza · 11 transiciones
    #  12 primer plano cinematográfico (se acerca a 100 mm durante el diálogo) · 13 vuelta completa alrededor de la cabeza.
    import json, glob
    CARP = argv[5] if len(argv) > 5 else None
    FPS = sc.render.fps
    def F(t): return 1 + int(round(t * FPS))
    E_ = MA["EXPRESIONES"]
    E_["demo_cejas_arriba"] = {"browInnerUp": 0.9, "browOuterUpLeft": 0.7, "browOuterUpRight": 0.7, "eyeWideLeft": 0.25, "eyeWideRight": 0.25}
    ciclorama(); luz("Contra_fria", (-1.2, 1.6, 1.9), 420, 1.2, (0.62, 0.78, 1.0), mira=(0, 0, 0.8))
    for ob in bpy.data.objects:                      # demo de la cara: los brazos casi no se mueven, sin tela
        for md in ob.modifiers:
            if md.type == 'CLOTH': md.show_render = False
    # medidas de la cabeza en reposo
    A.pose_reposo(1); sc.frame_set(1); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); ev = ME.evaluated_get(dg); mev = ev.to_mesh()
    gi = ME.vertex_groups["mixamorig:Head"].index
    pts = [ME.matrix_world @ mev.vertices[v.index].co for v in ME.data.vertices if any(g.group == gi and g.weight > 0.6 for g in v.groups)]
    ev.to_mesh_clear()
    mn = Vector((min(q.x for q in pts), min(q.y for q in pts), min(q.z for q in pts))); mx = Vector((max(q.x for q in pts), max(q.y for q in pts), max(q.z for q in pts)))
    H = (mn + mx) / 2; ALTO = mx.z - mn.z
    OJ = [ARM.matrix_world @ ARM.pose.bones[n].head for n in ("Ojo_L", "Ojo_R") if n in ARM.pose.bones]
    EO = sum(OJ, Vector()) / len(OJ) if OJ else Vector((H.x, mn.y + 0.03, H.z))
    H.x = EO.x                                   # la trenza cae a un lado: centrar en la cara
    print("CABEZA", tuple(round(v, 4) for v in H), "alto", round(ALTO, 4), "ojos", tuple(round(v, 4) for v in EO), flush=True)
    # foco en los ojos, pegado a la cabeza
    pbh = ARM.pose.bones["mixamorig:Head"]
    foco = bpy.data.objects.new("Foco_ojos", None); sc.collection.objects.link(foco); foco.location = EO
    co_ = foco.constraints.new('CHILD_OF'); co_.target = ARM; co_.subtarget = "mixamorig:Head"
    co_.inverse_matrix = (ARM.matrix_world @ pbh.matrix).inverted()
    mira = bpy.data.objects.new("Mira_cam", None); sc.collection.objects.link(mira)
    tt = cam.constraints.new('TRACK_TO'); tt.target = mira; tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
    cd.dof.use_dof = True; cd.dof.focus_object = foco; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36.0   # 85 mm de cámara de cine completa puesta en vertical
    def plano(t, alto_cuadro, lente, az=0.0, el=2.0, fstop=2.8, centro=None):
        """Cámara a la distancia justa para que 'alto_cuadro' (m) llene el alto del cuadro con esa lente."""
        c = Vector(centro) if centro is not None else H
        d = alto_cuadro * lente / cd.sensor_height
        a, e = math.radians(az), math.radians(el)
        cam.location = (c.x + d * math.cos(e) * math.sin(a), c.y - d * math.cos(e) * math.cos(a), c.z + d * math.sin(e))
        mira.location = c; cd.lens = lente; cd.dof.aperture_fstop = fstop
        f = F(t); cam.keyframe_insert("location", frame=f); mira.keyframe_insert("location", frame=f)
        cd.keyframe_insert("lens", frame=f); cd.keyframe_insert("dof.aperture_fstop", frame=f)
    BUSTO = ALTO * 2.05; CARA = ALTO * 1.25; MUY_CERCA = ALTO * 0.95
    CB = Vector((H.x, H.y, H.z - ALTO * 0.22)); CC = Vector((H.x, H.y, EO.z - ALTO * 0.10))
    # palabras del diálogo: las de la voz si hay carpeta; si no, tiempos estimados del texto (sin sonido)
    FRASE = "¡Hola! Soy Maitane, de EKORUEDAS. Hoy os enseño a mirar el desgaste de los neumáticos."
    if CARP and os.path.exists(os.path.join(CARP, "palabras.json")):
        pal = json.load(open(os.path.join(CARP, "palabras.json"), encoding="utf-8"))
        voz = (glob.glob(os.path.join(CARP, "voz.*")) or [None])[0]
    else:
        pal, t_ = [], 0.0; voz = None
        for w in FRASE.split():
            n_ = max(1, sum(1 for c in w.lower() if c in "aeiouáéíóú")); dur = 0.17 * n_ + 0.06
            pal.append({"text": w, "start": round(t_, 3), "end": round(t_ + dur, 3)}); t_ += dur + (0.28 if w[-1] in ".,!?" else 0.03)
    T_HAB = 24.8; DUR_HAB = max(w["end"] for w in pal)
    print("DEMO tiempos: diálogo", round(DUR_HAB, 2), "s", flush=True)
    T_GIROS = T_HAB + DUR_HAB + 0.8; T_VUELTA = T_GIROS + 3.2; T_FIN = T_VUELTA + 7.0
    f0, f1 = 1, F(T_FIN)
    base(f0, f1)
    def ex(t, nombre, k=1.0): A.expresion(F(t), nombre, k)
    # 1 — neutra, respira, parpadea
    ex(0, "neutra"); ex(3.6, "neutra")
    # 2 — sonrisa progresiva
    ex(4.4, "sonrisa_profesional", 0.6); ex(5.2, "sonrisa_profesional"); ex(6.0, "sonrisa_espontanea"); ex(6.9, "felicidad"); ex(7.5, "felicidad")
    # 3 — cejas por separado
    ex(8.0, "ceja_izquierda"); ex(8.7, "ceja_izquierda"); ex(9.1, "ceja_derecha"); ex(9.8, "ceja_derecha")
    ex(10.2, "demo_cejas_arriba"); ex(10.8, "demo_cejas_arriba"); ex(11.2, "sonrisa_natural", 0.6)
    # 4 — miradas (la cabeza acompaña un poco)
    for t, x, z, g, ar in ((11.4, 0, 0, 0, 0), (11.8, 0.30, 0.02, 7, 0), (12.5, 0.30, 0.02, 7, 0), (12.9, -0.30, 0.0, -7, 0), (13.6, -0.30, 0.0, -7, 0),
                           (14.0, 0.0, 0.20, 0, 4), (14.5, 0.0, 0.20, 0, 4), (14.9, 0.02, -0.16, 0, -4), (15.4, 0.02, -0.16, 0, -4), (15.8, 0, 0, 0, 0)):
        A.mirar(F(t), x, z); A.cabeza(F(t), arriba=ar, giro=g)
    # 5 — sorpresa (pupilas que se abren)
    ex(15.9, "sonrisa_natural", 0.4); ex(16.3, "sorpresa_intensa"); ex(17.4, "sorpresa_intensa")
    A.pupila(F(15.9), 1.0); A.pupila(F(16.4), 1.35); A.pupila(F(17.6), 1.0); A.cabeza(F(16.3), arriba=3); A.cabeza(F(17.6))
    # 6 — sarcasmo
    ex(18.0, "sarcasmo"); ex(19.6, "sarcasmo"); A.cabeza(F(18.0), ladeo=6, giro=-4); A.mirar(F(18.0), -0.10, 0.04); A.mirar(F(19.6), 0, 0)
    # 7 — risa natural
    ex(20.1, "risa_suave"); ex(20.8, "carcajada"); ex(21.9, "carcajada"); ex(22.6, "sonrisa_espontanea")
    A.cabeza(F(19.6), ladeo=2); A.cabeza(F(20.8), arriba=7, ladeo=-3); A.cabeza(F(21.3), arriba=4, ladeo=3); A.cabeza(F(21.9), arriba=7); A.cabeza(F(22.6))
    A.torso(F(20.8), adelante=-3); A.torso(F(22.6))
    # 8 — concentración (mira abajo, pupilas algo cerradas)
    ex(23.0, "concentracion"); ex(24.4, "concentracion"); A.mirar(F(23.0), -0.04, -0.12); A.cabeza(F(23.0), arriba=-6, giro=-5)
    A.pupila(F(23.0), 0.85); A.pupila(F(24.4), 1.0)
    # 9 — diálogo (labios por visemas), gestos de cabeza y cejas
    A.mirar(F(24.5), 0, 0); A.cabeza(F(24.6)); ex(24.6, "sonrisa_natural", 0.7)
    A.hablar(pal, f_inicio=F(T_HAB))
    for i, w in enumerate(pal):
        f = F(T_HAB + w["start"])
        if i % 4 == 0: A.cabeza(f, arriba=2 if i % 8 == 0 else -1.5, giro=3 if i % 8 == 0 else -2.5, ladeo=1.5)
    if voz: sonido(voz, F(T_HAB))
    ex(T_HAB + DUR_HAB + 0.2, "sonrisa_natural")
    # 10 — giros de cabeza: la trenza reacciona
    for dt, g, ar, tz in ((0.0, 0, 0, 0), (0.5, 36, 2, 12), (1.0, 36, 0, 12), (1.5, -38, -2, -14), (2.1, -38, 0, -14), (2.6, 0, 3, 0), (3.2, 0, 0, 0)):
        A.cabeza(F(T_GIROS + dt), arriba=ar, giro=g); A.torso(F(T_GIROS + dt), giro=tz * 0.6)
    # 13 — vuelta completa de la cámara alrededor de la cabeza; acaba de frente con un guiño
    ex(T_VUELTA, "sonrisa_natural"); ex(T_FIN - 1.0, "guino"); ex(T_FIN - 0.4, "sonrisa_natural")
    A.parpadeos_auto(f0, f1, evitar=[(F(16.0), F(17.8)), (F(20.4), F(22.2)), (F(T_FIN - 1.2), F(T_FIN))])
    A.mirada_viva(f0, F(11.2), amplitud=0.016); A.mirada_viva(F(T_HAB), F(T_GIROS), amplitud=0.012)
    # cámara: busto 85 mm → cara 85 mm → primer plano 100 mm durante el diálogo → vuelta completa
    plano(0, BUSTO, 85, az=6, centro=CB); plano(3.6, BUSTO * 0.94, 85, az=4, centro=CB)
    plano(7.5, CARA, 85, az=0, centro=CC); plano(15.8, CARA, 85, az=-3, centro=CC); plano(22.6, CARA * 1.04, 85, az=4, centro=CC)
    plano(T_HAB, CARA, 90, az=2, centro=CC, fstop=3.2); plano(T_HAB + DUR_HAB, MUY_CERCA, 100, az=0, el=1, centro=CC, fstop=4.0)
    plano(T_GIROS, BUSTO * 0.9, 85, az=0, centro=CB); plano(T_VUELTA, CARA * 1.15, 85, az=0, centro=CC)
    n_v = int((T_FIN - 0.6 - T_VUELTA) * FPS)
    for i in range(n_v + 1):
        u = i / n_v; u_s = u * u * (3 - 2 * u)                     # arranca y frena suave
        plano(T_VUELTA + i / FPS, CARA * 1.15, 85, az=360.0 * u_s, el=4 + 6 * math.sin(math.pi * u), centro=CC)
    plano(T_FIN, CARA * 1.1, 85, az=0, centro=CC)
    hornear_y_video(f0, f1, "demo_cara")
elif PRUEBA == "primer_plano":
    # 6 — Primer plano 4K vertical del rostro (foto)
    base(1, 2); A.expresion(1, "sonrisa_natural"); A.finalizar(1, 2, trenza=False)
    sc.render.resolution_x, sc.render.resolution_y = 2160, 3840
    camara((0.16, -0.70, 0.90), (0.02, 0.0, 0.84), 105); sc.frame_set(1)
    sc.render.filepath = os.path.join(OUT, "prueba6_primer_plano_4k.png"); bpy.ops.render.render(write_still=True)
    print("FOTO_OK prueba6", flush=True)
open(os.path.join(OUT, f"HECHO_{PRUEBA}.txt"), "w").write("ok"); print("PRUEBA_OK", PRUEBA, flush=True)
