# Cola 4K60 del turbo (Maite + Clod v3, 27-11-2026): espera a que no quede NINGÚN otro render 4K en marcha
# (motor, embrague...), renderiza con reintentos y codifica. Nunca para otros renders.
# Uso: blender -b --factory-startup --python cola_turbo.py
import bpy, subprocess, os, time, glob, json
R = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
B = bpy.app.binary_path
REN = os.path.join(R, "scripts", "render_cycles_bg.py"); ENC = os.path.join(R, "scripts", "encode_bg.py")
EST = os.path.join(R, "videos_3d", "cola_4k_estado.txt")
def estado(t): open(EST, "a", encoding="utf-8").write(time.strftime("%d-%m %H:%M:%S ") + t + "\n")
def otros():
    out = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process -Filter \"name='blender.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],
                         capture_output=True, text=True, creationflags=0x08000000).stdout
    try: ps = json.loads(out); ps = ps if isinstance(ps, list) else [ps]
    except Exception: return False
    return any("render_cycles_bg.py" in (p.get("CommandLine") or "") and "\\turbo\\" not in (p.get("CommandLine") or "") for p in ps)
nm = "turbo"; d = os.path.join(R, "videos_3d", nm); out = os.path.join(d, "render4k"); os.makedirs(out, exist_ok=True)
blend = os.path.join(d, nm + ".blend"); done = os.path.join(out, "DONE.txt")
avisado = False
while otros():
    if not avisado: estado(nm + " en cola: espera a que terminen los otros renders 4K"); avisado = True
    time.sleep(300)
for intento in range(40):
    if os.path.exists(done): break
    while otros(): time.sleep(300)
    for f in glob.glob(os.path.join(out, "*.png")):
        if os.path.getsize(f) == 0: os.remove(f)
    estado("%s render intento %d (%d png)" % (nm, intento + 1, len(glob.glob(os.path.join(out, "*.png")))))
    with open(os.path.join(d, "render4k.log"), "a") as lg:
        subprocess.run([B, "-b", blend, "--python", REN, "--", out, "64"], stdout=lg, stderr=subprocess.STDOUT, creationflags=0x08000000)   # sin ventana de consola
    if not os.path.exists(done): time.sleep(60)
if os.path.exists(done):
    mp4 = os.path.join(d, nm + "_4k60.mp4")
    estado(nm + " codificando")
    with open(os.path.join(d, "encode4k.log"), "a") as lg:
        subprocess.run([B, "-b", "--factory-startup", "--python", ENC, "--", out, mp4, "2160", "3840", "60", "PERC_LOSSLESS"], stdout=lg, stderr=subprocess.STDOUT, creationflags=0x08000000)
    estado("%s LISTO %s" % (nm, os.path.exists(mp4 + ".done")))
else:
    estado(nm + " SIN TERMINAR tras 40 intentos")
