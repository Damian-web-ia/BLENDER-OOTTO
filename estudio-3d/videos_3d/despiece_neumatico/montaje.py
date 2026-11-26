# Montaje final del despiece: textos (gancho, subtítulos palabra a palabra, rótulos de cada capa, aviso del bulto) + audio.
# Uso: python3 montaje.py <render.mp4> <anclas.json> <mezcla.ogg> <salida.mp4> [fotogramas sueltos para probar...]
import sys, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC, ANCLAS, AUDIO, OUT = sys.argv[1:5]
PRUEBA = [int(x) for x in sys.argv[5:]]
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
VOZ = [
 (0.30, [("¿Una", 0.12, 0.28), ("rueda", 0.28, 0.68), ("es", 0.73, 0.93), ("solo", 0.93, 1.25), ("goma", 1.25, 1.49), ("con", 1.49, 1.65), ("aire?", 1.65, 1.89), ("Vamos", 2.12, 2.29), ("a", 2.29, 2.37), ("verlo.", 2.37, 2.69)], [3, 2, 2, 3]),
 (3.35, [("Ni", 0.116, 0.36), ("de", 0.36, 0.44), ("broma.", 0.44, 0.85), ("Mira", 0.891, 1.19), ("lo", 1.19, 1.27), ("que", 1.27, 1.43), ("lleva", 1.43, 1.59), ("dentro.", 1.59, 2.07)], [3, 3, 2]),
 (6.30, [("Por", 0.04, 0.2), ("dentro,", 0.2, 0.68), ("una", 0.801, 0.92), ("capa", 0.92, 1.16), ("de", 1.16, 1.32), ("goma", 1.32, 1.56), ("que", 1.64, 1.64), ("no", 1.64, 1.72), ("deja", 1.72, 1.96), ("escapar", 1.96, 2.28), ("el", 2.28, 2.36), ("aire.", 2.36, 2.68),
         ("Encima,", 2.755, 3.32), ("la", 3.438, 3.56), ("carcasa:", 3.56, 4.1), ("lonas", 4.177, 4.5), ("de", 4.58, 4.58), ("hilo", 4.58, 4.82), ("que", 4.9, 4.9), ("aguantan", 4.9, 5.22), ("el", 5.22, 5.38), ("peso", 5.38, 5.78), ("y", 5.78, 5.86), ("los", 5.86, 6.02), ("golpes.", 6.02, 6.5),
         ("En", 6.55, 6.71), ("los", 6.71, 6.87), ("bordes,", 6.87, 7.35), ("los", 7.462, 7.71), ("talones,", 7.71, 8.27), ("con", 8.33, 8.5), ("aros", 8.5, 8.66), ("de", 8.66, 8.74), ("acero", 8.74, 9.06), ("que", 9.14, 9.14), ("la", 9.14, 9.22), ("sujetan", 9.22, 9.7), ("a", 9.7, 9.78), ("la", 9.78, 9.86), ("llanta.", 9.86, 10.18),
         ("Luego,", 10.2, 10.59), ("cinturones", 10.614, 11.17), ("de", 11.25, 11.25), ("acero", 11.25, 11.49), ("que", 11.57, 11.57), ("la", 11.57, 11.73), ("refuerzan.", 11.73, 12.27),
         ("Y", 12.31, 12.39), ("por", 12.39, 12.55), ("fuera,", 12.55, 12.95), ("la", 12.98, 13.14), ("banda", 13.14, 13.38), ("de", 13.38, 13.46), ("rodadura:", 13.46, 14.01), ("lo", 14.027, 14.25), ("único", 14.25, 14.49), ("que", 14.49, 14.57), ("toca", 14.57, 14.81), ("el", 14.89, 14.89), ("suelo.", 14.89, 15.21)],
  [2, 4, 3, 3, 1, 2, 3, 2, 5, 3, 2, 4, 3, 3, 1, 3, 3, 3, 4, 3, 3]),
 (22.10, [("¡Y", 0.12, 0.28), ("yo", 0.28, 0.52), ("que", 0.559, 0.68), ("pensaba", 0.68, 1.16), ("que", 1.16, 1.24), ("era", 1.24, 1.4), ("un", 1.4, 1.48), ("donut", 1.48, 1.88), ("gigante!", 1.88, 2.52)], [4, 3, 2]),
 (25.00, [("Por", 0.12, 0.28), ("eso,", 0.28, 0.68), ("si", 0.786, 1.0), ("ves", 1.0, 1.16), ("un", 1.16, 1.24), ("bulto", 1.24, 1.72), ("o", 1.72, 1.8), ("un", 1.8, 1.88), ("corte", 1.88, 2.12), ("en", 2.12, 2.2), ("el", 2.28, 2.28), ("lateral,", 2.28, 2.83), ("no", 2.88, 2.96), ("esperes:", 2.96, 3.59), ("llévala", 3.646, 4.0), ("a", 4.0, 4.08), ("revisar.", 4.08, 4.48)], [2, 4, 3, 3, 2, 3]),
 (29.85, [("¡Síguenos", 0.119, 0.6), ("para", 0.6, 0.76), ("más", 0.76, 0.92), ("despieces!", 0.92, 1.56)], [1, 3]),
]
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
    if f <= 189: return 0.80
    if f <= 650: return 0.895
    if f <= 745: return 0.15
    if f <= 895: return 0.80
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
    if f > 100: return
    p = ease_back((f - 6) / 7.0) if f >= 6 else 0.0
    if p <= 0: return
    a = 1.0 if f < 92 else max(0.0, (100 - f) / 8)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    sz = int(104 * (0.6 + 0.4 * p))
    dd.text((W / 2, 0.100 * H), "¿SOLO GOMA", font=fnt(sz, "Black"), fill=BLANCO + (int(255 * a),), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, int(255 * a)))
    dd.text((W / 2, 0.100 * H + sz * 1.05), "CON AIRE?", font=fnt(sz, "Black"), fill=AMARILLO + (int(255 * a),), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, int(255 * a)))
    img.alpha_composite(capa)

# ---------------------------------------------------------------- rótulos de las capas
CAPAS = [  # clave, desde, título, explicación, lado del ancla, color
 ("alma", 192, "ALMA INTERNA", "no deja escapar el aire", "i", (90, 170, 255)),
 ("carcasa", 290, "CARCASA", "lonas de hilo: peso y golpes", "d", (255, 196, 80)),
 ("talones", 420, "TALONES", "aros de acero que la sujetan", "i", (255, 140, 50)),
 ("cinturones", 505, "CINTURONES", "de acero: la refuerzan", "d", (190, 220, 255)),
 ("banda", 583, "BANDA DE RODADURA", "lo único que toca el suelo", "i", (255, 212, 0)),
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
    if not (192 <= f <= 615) or str(f) not in anclas: return
    A = anclas[str(f)]; capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    activo = max([k for k, c in enumerate(CAPAS) if f >= c[1]], default=-1)
    salida = 1.0 if f < 600 else max(0.0, (615 - f) / 15)
    for k, (cl, f0, tit, sub, lado, col) in enumerate(CAPAS):
        if f < f0: continue
        pt = A[cl][lado]; c = A[cl]["c"]
        if pt is None: continue
        px, py = pt[0] * W, (1 - pt[1]) * H
        p = ease_back((f - f0) / 8.0); alfa = int(255 * salida)
        if k == activo:
            # cuadro grande arriba con línea al borde de la capa
            by = 0.090 * H if f < 583 else 0.062 * H
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
    if not (817 <= f <= 895) or "bulto" not in anclas.get(str(f), {}): return
    b = anclas[str(f)]["bulto"]
    if b is None: return
    cx, cy = b[0] * W, (1 - b[1]) * H - 0.075 * H; capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    prog = min(1.0, (f - 817) / 10.0); r = 190 + 10 * math.sin((f - 817) * 0.4)
    dd.arc((cx - r, cy - r * 0.75, cx + r, cy + r * 0.75), start=-90, end=-90 + 360 * prog, fill=(255, 40, 40, 255), width=14)
    if f >= 822:
        p = ease_back((f - 822) / 8.0)
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
