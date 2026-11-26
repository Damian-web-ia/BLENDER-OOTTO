# Montaje final del despiece de los frenos: gancho, subtítulos palabra a palabra, rótulos de cada pieza,
# avisos del consejo (chirría / vibra / no lo dejes) y pastilla NUEVA frente a GASTADA. Audio: mezcla de Diego + música + efectos.
# Uso: python3 montaje_frenos.py <render.mp4> <anclas_frenos.json> <mezcla.ogg> <salida.mp4> <voces_frenos.json> [fotogramas sueltos para probar...]
import sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont
SRC, ANCLAS, AUDIO, OUT, VOZJ = sys.argv[1:6]
PRUEBA = [int(x) for x in sys.argv[6:]]
W, H = 1080, 1920
FONT = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
_cache = {}
def fnt(sz, peso="ExtraBold"):
    k = (sz, peso)
    if k not in _cache:
        f = ImageFont.truetype(FONT, sz)
        try: f.set_variation_by_name(peso)
        except Exception: pass
        _cache[k] = f
    return _cache[k]
AMARILLO = (255, 212, 0); BLANCO = (255, 255, 255); NEGRO = (0, 0, 0)
_a = json.load(open(ANCLAS)); anclas = _a["anclas"]
B0, C0, D0, E0, A2, INS, CTA = 139, 226, 331, 417, 525, 618, 694
def T(f): return (f - 1) / 30.0
def F(t): return int(round(t * 30)) + 1
def ease_back(x):
    x = max(0.0, min(1.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------------------------------------------------------------- voz: tiempos de cada palabra
_vz = json.load(open(VOZJ, encoding="utf-8"))
def FW(i, j, fin=False):
    l = _vz["lineas"][i]; w = l["words"][j]; return F(l["at"] + (w[2] if fin else w[1]))
GRUPOS = []
for l in _vz["lineas"]:
    ws = [(m, l["at"] + w[1], l["at"] + w[2]) for m, w in zip(l["mostrar"], l["words"])]
    assert sum(l["grupos"]) == len(ws)
    i = 0
    for n in l["grupos"]:
        GRUPOS.append(ws[i:i + n]); i += n
for k, g in enumerate(GRUPOS):
    fin = g[-1][2] + 0.35
    if k + 1 < len(GRUPOS):
        if GRUPOS[k + 1][0][1] - g[-1][2] < 0.6: fin = min(fin, GRUPOS[k + 1][0][1])
    else: fin = 99.0
    GRUPOS[k] = (g, g[0][1] - 0.04, fin)

# ---------------------------------------------------------------- subtítulos (abajo; en los planos del freno, más abajo para dejar sitio a los rótulos)
def y_sub(f):
    if f < B0: return 0.80
    if f < A2: return 0.895
    if f < CTA: return 0.80
    return 0.86
def subtitulo(d, f):
    t = T(f)
    for g, t0, t1 in GRUPOS:
        if t0 <= t < t1:
            fz = fnt(66); esp = fz.getlength(" ")
            anchos = [fz.getlength(w) for (w, _, _) in g]; tot = sum(anchos) + esp * (len(g) - 1)
            lineas = [list(range(len(g)))]
            if tot > W * 0.86:
                m = len(g) // 2; lineas = [list(range(m)), list(range(m, len(g)))]
            yc = y_sub(f) * H; lh = 82; y0 = yc - lh * (len(lineas) - 1) / 2
            pop = ease_back((t - t0) / 0.12); s = 0.85 + 0.15 * pop
            for li, idx in enumerate(lineas):
                tw = sum(anchos[i] for i in idx) + esp * (len(idx) - 1); x = W / 2 - tw / 2; y = y0 + li * lh
                for i in idx:
                    w, a, b = g[i]; col = AMARILLO if a - 0.02 <= t < b + 0.06 else BLANCO
                    d.text((x + anchos[i] / 2, y), w, font=fnt(int(66 * s)), fill=col, anchor="mm", stroke_width=9, stroke_fill=NEGRO)
                    x += anchos[i] + esp
            return

# ---------------------------------------------------------------- gancho
def gancho(img, f):
    G0, G1 = 4, 100
    if not (G0 <= f <= G1): return
    p = ease_back((f - G0) / 7.0); a = 1.0 if f < G1 - 10 else max(0.0, (G1 - f) / 10)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    sz = int(104 * (0.6 + 0.4 * p)); al = int(255 * a)
    dd.text((W / 2, 0.100 * H), "¿QUÉ PASA", font=fnt(sz, "Black"), fill=BLANCO + (al,), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, al))
    dd.text((W / 2, 0.100 * H + sz * 1.05), "AL FRENAR?", font=fnt(sz, "Black"), fill=AMARILLO + (al,), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, al))
    img.alpha_composite(capa)

# ---------------------------------------------------------------- caja de rótulo
def caja(dd, cx, cy, texto, sub, color, escala=1.0, alfa=255):
    ft = fnt(int(60 * escala), "Black"); fs = fnt(int(37 * escala), "SemiBold")
    tw = ft.getlength(texto); sw = fs.getlength(sub) if sub else 0; bw = max(tw, sw) + 56 * escala
    bh = (74 + (50 if sub else 0)) * escala
    x0 = cx - bw / 2; x0 = max(24, min(W - 24 - bw, x0)); y0 = cy - bh / 2
    dd.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=int(20 * escala), fill=(12, 14, 18, int(alfa * 0.86)), outline=color + (alfa,), width=max(2, int(4 * escala)))
    dd.rectangle((x0 + 3, y0 + 14 * escala, x0 + 11 * escala, y0 + bh - 14 * escala), fill=color + (alfa,))
    dd.text((x0 + bw / 2 + 4 * escala, y0 + 42 * escala), texto, font=ft, fill=color + (alfa,), anchor="mm")
    if sub: dd.text((x0 + bw / 2 + 4 * escala, y0 + 99 * escala), sub, font=fs, fill=(235, 235, 235, alfa), anchor="mm")
    return (x0, y0, x0 + bw, y0 + bh)

# ---------------------------------------------------------------- rótulos de las piezas (uno activo a la vez, con línea a su pieza)
PIEZAS = [  # clave del ancla, desde, hasta, título, explicación, color
 ("liquido", FW(1, 3), C0 - 1, "LÍQUIDO DE FRENOS", "empuja el pistón", (90, 170, 255)),
 ("piston", FW(1, 8), C0 - 1, "PISTÓN", "aprieta la pastilla", (200, 210, 225)),
 ("pinza", FW(1, 13), FW(1, 16) - 1, "PINZA", "abraza el disco", (255, 90, 70)),
 ("pastillas", FW(1, 16), FW(1, 19) - 1, "PASTILLAS", "rozan el disco", (255, 196, 80)),
 ("disco", FW(1, 19), D0 - 1, "DISCO", "gira con la rueda", (190, 220, 255)),
 ("calor", FW(1, 31), E0 - 1, "CALOR", "el roce frena el coche", (255, 120, 40)),
 ("canales", FW(1, 41), A2 - 1, "CANALES", "por aquí sale el calor", (120, 230, 200)),
]
def rotulos(img, f):
    A = anclas.get(str(f))
    if not A: return
    act = [p for p in PIEZAS if p[1] <= f <= p[2]]
    if not act: return
    cl, f0, f1, tit, sub, col = act[-1]
    pt = A.get(cl)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    p = ease_back((f - f0) / 8.0); alfa = 255 if f < f1 - 5 else int(255 * max(0.0, (f1 - f) / 5))
    c = caja(dd, W / 2, 0.095 * H, tit, sub, col, escala=0.75 + 0.25 * p, alfa=alfa)
    if pt is not None and 0.03 < pt[0] < 0.97 and 0.06 < pt[1] < 0.95:
        px, py = pt[0] * W, (1 - pt[1]) * H
        bx = min(max(px, c[0] + 40), c[2] - 40)
        prog = min(1.0, (f - f0) / 6.0); ex, ey = bx + (px - bx) * prog, c[3] + (py - c[3]) * prog
        dd.line((bx, c[3], ex, ey), fill=col + (alfa,), width=4)
        if prog >= 1:
            r = 10 + 3 * math.sin(f * 0.35)
            dd.ellipse((px - r, py - r, px + r, py + r), fill=col + (alfa,), outline=(255, 255, 255, alfa), width=3)
    img.alpha_composite(capa)

# ---------------------------------------------------------------- consejo: avisos que se apilan arriba
AVISOS = [(FW(2, 3), "¿CHIRRÍA?", (255, 212, 0)), (FW(2, 6), "¿VIBRA EL VOLANTE?", (255, 160, 60)), (FW(2, 9), "¡NO LO DEJES!", (255, 70, 60))]
def avisos(img, f):
    if not (A2 <= f < INS): return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    alfa = 255 if f < INS - 4 else int(255 * (INS - f) / 4)
    for k, (f0, txt, col) in enumerate(AVISOS):
        if f < f0: continue
        p = ease_back((f - f0) / 7.0); sz = int(78 * (0.6 + 0.4 * p))
        y = 0.070 * H + k * 100
        dd.text((W / 2, y), txt, font=fnt(sz, "Black"), fill=col + (alfa,), anchor="mm", stroke_width=11, stroke_fill=(0, 0, 0, alfa))
    img.alpha_composite(capa)

# ---------------------------------------------------------------- inserto: pastilla nueva frente a gastada
def inserto(img, f):
    if not (INS <= f < CTA): return
    A = anclas.get(str(f)) or {}
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    alfa = 255 if f < CTA - 4 else int(255 * (CTA - f) / 4)
    for k, (cl, tit, sub, col) in enumerate((("PAD_Nueva", "NUEVA", "material grueso", (90, 220, 120)), ("PAD_Gastada", "GASTADA", "casi sin material", (255, 70, 60)))):
        f0 = INS + 4 + k * 14
        if f < f0: continue
        pt = A.get(cl)
        if pt is None: continue
        p = ease_back((f - f0) / 8.0)
        cy = (1 - pt[1]) * H + (-0.13 * H if k == 0 else 0.13 * H)
        caja(dd, W / 2, cy, tit, sub, col, escala=0.8 + 0.2 * p, alfa=alfa)
    img.alpha_composite(capa)

def componer(fr, f):
    img = fr.convert("RGBA")
    gancho(img, f); rotulos(img, f); avisos(img, f); inserto(img, f)
    subtitulo(ImageDraw.Draw(img), f)
    return img.convert("RGB")

if PRUEBA:
    for f in PRUEBA:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf", f"select=eq(n\\,{f - 1}),scale={W}:{H}:flags=lanczos", "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        componer(Image.frombytes("RGB", (W, H), raw), f).save(f"/tmp/prueba_fr_{f:04d}.png")
    sys.exit(0)
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf", f"scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-i", AUDIO,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
f = 0; n = W * H * 3
while True:
    buf = dec.stdout.read(n)
    if len(buf) < n: break
    f += 1; enc.stdin.write(componer(Image.frombytes("RGB", (W, H), buf), f).tobytes())
enc.stdin.close(); enc.wait(); print("fotogramas", f)
