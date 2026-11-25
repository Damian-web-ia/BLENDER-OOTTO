# PLANTILLA DE REEL DIARIO - copiar a la carpeta del reel como build_<tema>.py
# Carga la biblioteca (personajes, coche, taller, carretera, luces, utilidades) y solo define lo nuevo.
import json, os
ESTUDIO = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
ROOT = r"C:\Users\EKORUEDAS\Desktop\CLAUDE VIDEOS\AAAA-MM-DD_TITULO"
END = 900                                   # último fotograma (30 fps)
VOICES = json.load(open(os.path.join(ROOT, "data", "voces.json"), encoding="utf-8"))
exec(open(os.path.join(ESTUDIO, "biblioteca", "biblioteca_ekoruedas.py"), encoding="utf-8").read())

# 1) Cámaras: camera(nombre, lente) + cam_keys(nombre, [(fotograma, posición, objetivo), ...])
# 2) Cortes: sc.timeline_markers.new(nombre, frame=f).camera = CAMS[nombre][0]
# 3) Textos: cam_plate(...) y cam_text(cam, nombre, "TEXTO", M["white3d"] | M["orange3d"], y_frac, h_frac, f_in, f_out)
#    Regla: nunca encima de una cara ni de un objeto que se mueva por esa zona.
# 4) Acción: place(objeto, f, (x, y, z), giro_z_grados), key_rot, key_scale, key_emit
# 5) Bocas: hablar(VOICES); parpadeos: blink(AL["eyes"], f, (1, 1, 1), 2) / blink(CL["eyes"], f, (1.15, 1, 1), 1)

hablar(VOICES)
sc.frame_set(1)
os.makedirs(os.path.join(ROOT, "escena"), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "escena", "reel.blend"))
