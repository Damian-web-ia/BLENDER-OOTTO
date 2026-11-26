# Montaje final del despiece: textos (gancho, subtítulos palabra a palabra, rótulos de cada capa, aviso del bulto) + audio.
# Uso: python3 montaje.py <render.mp4> <anclas.json> <mezcla.ogg> <salida.mp4> [fotogramas sueltos para probar...]
import sys, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC, ANCLAS, AUDIO, OUT, WARPJ, VOZJ = sys.argv[1:7]
PRUEBA = [int(x) for x in sys.argv[7:]]
_wp = json.load(open(WARPJ))["warp"] if WARPJ != "none" else [(1, 1)]
def W(x):
    xs = [a for a, b in _wp]; ys = [b for a, b in _wp]
    if x <= xs[0]: return x
    if x >= xs[-1]: return ys[-1] + (x - xs[-1])
    return float(np.interp(x, xs, ys))
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
anclas = json.load(open(ANCLAS))
def T(f): return (f - 1) / 30.0
def ease_back(x):
    x = max(0.0, min(1.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------------------------------------------------------------- subtítulos
_vz = json.load(open(VOZJ, encoding="utf-8"))
VOZ = [(l["at"], [(m, w[1], w[2]) for m, w in zip(l["mostrar"], l["words"])], l["grupos"]) for l in _vz["lineas"]]
GRUPOS = []
for at, ws, tam in VOZ:
    assert sum(tam) == len(ws), (at, sum(tam), len(ws))
    i = 0
    for n in tam:
        g = [(w, at + a, at + b) for (w, a, b) in ws[i:i + n]]; GRUPOS.append(g); i += n
for k, g in enumerate(GRUPOS):
    fin = g[-1][2] + 0.35
    if k + 1 < len(GRUPOS): fin = min(fin, GRUPOS[k + 1][0][1]) if GRUPOS[k + 1][0][1] - g[-1][2] < 0.6 else fin
    else: fin = 99.0                      # el último (la llamada a seguir) se queda hasta el final
    GRUPOS[k] = (g, g[0][1] - 0.04, fin)
def y_sub(f):
    if f <= W(129): return 0.80
    if f <= W(605): return 0.895
    if f <= W(752): return 0.80
    return 0.14
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
                    fs = fnt(int(66 * s)); d.text((x + anchos[i] / 2, y), w, font=fs, fill=col, anchor="mm", stroke_width=9, stroke_fill=NEGRO)
                    x += anchos[i] + esp
            return

# ---------------------------------------------------------------- gancho
def gancho(img, d, f):
    if f > W(76): return
    p = ease_back((f - 4) / 7.0) if f >= 4 else 0.0
    if p <= 0: return
    a = 1.0 if f < W(66) else max(0.0, (W(76) - f) / 10)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    sz = int(104 * (0.6 + 0.4 * p))
    dd.text((W / 2, 0.100 * H), "¿SOLO GOMA", font=fnt(sz, "Black"), fill=BLANCO + (int(255 * a),), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, int(255 * a)))
    dd.text((W / 2, 0.100 * H + sz * 1.05), "CON AIRE?", font=fnt(sz, "Black"), fill=AMARILLO + (int(255 * a),), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, int(255 * a)))
    img.alpha_composite(capa)

# ---------------------------------------------------------------- rótulos de las capas
CAPAS = [  # clave, desde, título, explicación, lado del ancla, color
 ("alma", W(153), "ALMA INTERNA", "goma que retiene el aire", "i", (90, 170, 255)),
 ("carcasa", W(235), "CARCASA", "hilos de poliéster: peso y golpes", "d", (255, 196, 80)),
 ("talones", W(360), "TALONES", "haz de alambres de acero", "i", (255, 140, 50)),
 ("cinturones", W(447), "CINTURONES", "cables de acero cruzados", "d", (190, 220, 255)),
 ("banda", W(523), "BANDA DE RODADURA", "lo único que toca el suelo", "i", (255, 212, 0)),
]
def pastilla(dd, cx, cy, texto, sub, color, escala=1.0, alfa=255, ancla_x=None):
    ft = fnt(int(60 * escala), "Black"); fs = fnt(int(37 * escala), "SemiBold")
    tw = ft.getlength(texto); sw = fs.getlength(sub) if sub else 0; bw = max(tw, sw) + 56 * escala
    bh = (74 + (50 if sub else 0)) * escala
    x0 = cx - bw / 2; x0 = max(24, min(W - 24 - bw, x0)); y0 = cy - bh / 2
    dd.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=int(20 * escala), fill=(12, 14, 18, int(alfa * 0.86)), outline=color + (alfa,), width=max(2, int(4 * escala)))
    dd.rectangle((x0 + 3, y0 + 14 * escala, x0 + 11 * escala, y0 + bh - 14 * escala), fill=color + (alfa,))
    dd.text((x0 + bw / 2 + 4 * escala, y0 + 42 * escala), texto, font=ft, fill=color + (alfa,), anchor="mm")
    if sub: dd.text((x0 + bw / 2 + 4 * escala, y0 + 99 * escala), sub, font=fs, fill=(235, 235, 235, alfa), anchor="mm")
    return (x0, y0, x0 + bw, y0 + bh)
def rotulos(img, f):
    if not (W(153) <= f <= W(560)) or str(f) not in anclas: return
    A = anclas[str(f)]; capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    activo = max([k for k, c in enumerate(CAPAS) if f >= c[1]], default=-1)
    salida = 1.0 if f < W(548) else max(0.0, (W(560) - f) / 12)
    for k, (cl, f0, tit, sub, lado, col) in enumerate(CAPAS):
        if f < f0: continue
        pt = A[cl]["f"] if k == activo else A[cl][lado]
        if pt is None or not (0.02 < pt[0] < 0.98 and 0.03 < pt[1] < 0.97): continue
        px, py = pt[0] * W, (1 - pt[1]) * H
        p = ease_back((f - f0) / 8.0); alfa = int(255 * salida)
        if k == activo:
            # cuadro grande arriba con línea al borde de la capa
            by = 0.090 * H if f < W(523) else 0.062 * H
            caja = pastilla(dd, W / 2, by, tit, sub, col, escala=0.75 + 0.25 * p, alfa=alfa)
            bx = (caja[0] + caja[2]) / 2 if False else (caja[0] + 40 if lado == "i" else caja[2] - 40)
            dd.line((bx, caja[3], px, py), fill=col + (alfa,), width=4)
            r = 9 + 3 * math.sin(f * 0.35)
            dd.ellipse((px - r, py - r, px + r, py + r), fill=col + (alfa,), outline=(255, 255, 255, alfa), width=3)
        else:
            # etiqueta pequeña al lado de su capa
            ft = fnt(30, "Black"); tw = ft.getlength(tit)
            x = px - tw - 34 if lado == "i" else px + 14
            x = max(16, min(W - tw - 36, x))
            dd.rounded_rectangle((x, py - 24, x + tw + 22, py + 24), radius=12, fill=(12, 14, 18, int(alfa * 0.8)), outline=col + (int(alfa * 0.9),), width=2)
            dd.text((x + 11 + tw / 2, py), tit, font=ft, fill=col + (alfa,), anchor="mm")
    img.alpha_composite(capa)

# ---------------------------------------------------------------- aviso del bulto
def bulto(img, f):
    if not (W(641) <= f <= W(691)) or "bulto" not in anclas.get(str(f), {}): return
    b = anclas[str(f)]["bulto"]
    if b is None: return
    cx, cy = b[0] * W, (1 - b[1]) * H - 0.075 * H; capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    f0b = W(641); prog = min(1.0, (f - f0b) / 10.0); r = 190 + 10 * math.sin((f - f0b) * 0.4)
    dd.arc((cx - r, cy - r * 0.75, cx + r, cy + r * 0.75), start=-90, end=-90 + 360 * prog, fill=(255, 40, 40, 255), width=14)
    if f >= W(646):
        p = ease_back((f - W(646)) / 8.0)
        pastilla(dd, W / 2, cy - r * 0.75 - 110, "BULTO = PELIGRO", "la carcasa está rota por dentro", (255, 60, 60), escala=0.8 + 0.2 * p)
    img.alpha_composite(capa)

def componer(fr, f):
    img = fr.convert("RGBA"); d = ImageDraw.Draw(img)
    gancho(img, d, f); rotulos(img, f); bulto(img, f)
    d = ImageDraw.Draw(img); subtitulo(d, f)
    return img.convert("RGB")

if PRUEBA:
    for f in PRUEBA:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf", f"select=eq(n\\,{f - 1}),scale={W}:{H}:flags=lanczos", "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        fr = Image.frombytes("RGB", (W, H), raw); componer(fr, f).save(f"/tmp/prueba_{f:04d}.png")
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
