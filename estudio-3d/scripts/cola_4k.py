# Cola 4K60 Cycles (27-11-2026): batería -> filtro -> bujía. Reintenta si un render se cae (p. ej. memoria de la gráfica
# compartida con la tarea de las 19:30) y al terminar cada uno lo codifica a MP4 4K60 casi sin pérdida.
# Uso: blender -b --factory-startup --python cola_4k.py
import bpy, subprocess, os, time, glob
R = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
B = bpy.app.binary_path
REN = os.path.join(R, "scripts", "render_cycles_bg.py"); ENC = os.path.join(R, "scripts", "encode_bg.py")
EST = os.path.join(R, "videos_3d", "cola_4k_estado.txt")
def estado(t):
    open(EST, "a", encoding="utf-8").write(time.strftime("%d-%m %H:%M:%S ") + t + "\n")
for nm in ("despiece_bateria", "despiece_filtro_aceite", "despiece_bujia"):
    d = os.path.join(R, "videos_3d", nm); out = os.path.join(d, "render4k"); os.makedirs(out, exist_ok=True)
    blend = os.path.join(d, nm + ".blend"); done = os.path.join(out, "DONE.txt")
    for intento in range(40):
        if os.path.exists(done): break
        for f in glob.glob(os.path.join(out, "*.png")):
            if os.path.getsize(f) == 0: os.remove(f)
        estado("%s render intento %d (%d png)" % (nm, intento + 1, len(glob.glob(os.path.join(out, "*.png")))))
        with open(os.path.join(d, "render4k.log"), "a") as lg:
            subprocess.run([B, "-b", blend, "--python", REN, "--", out, "64"], stdout=lg, stderr=subprocess.STDOUT)
        if not os.path.exists(done): time.sleep(60)
    if not os.path.exists(done):
        estado("%s SIN TERMINAR tras 40 intentos" % nm); continue
    mp4 = os.path.join(d, nm + "_4k60.mp4")
    if not os.path.exists(mp4 + ".done"):
        estado("%s codificando" % nm)
        with open(os.path.join(d, "encode4k.log"), "a") as lg:
            subprocess.run([B, "-b", "--factory-startup", "--python", ENC, "--", out, mp4, "2160", "3840", "60", "PERC_LOSSLESS"], stdout=lg, stderr=subprocess.STDOUT)
    estado("%s LISTO %s" % (nm, os.path.exists(mp4 + ".done")))
estado("COLA TERMINADA")
