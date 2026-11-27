# Montaje final del despiece del amortiguador: gancho, subtítulos palabra a palabra, rótulos de cada pieza con línea,
# GRÁFICO DEL REBOTE (sin / con amortiguador), avisos del consejo, NUEVO frente a GASTADO, dato del RACE y cierre "síguenos".
# Uso: python3 montaje_amortiguador.py <render.mp4> <anclas.json> <mezcla.ogg> <salida.mp4> <voces.json> [fotogramas sueltos para probar...]
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
B0, C0, D0, E0, F0, A2, INS, A3, CTA = 150, 214, 297, 357, 453, 533, 650, 719, 850
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
    else: fin = g[-1][2] + 0.6
    GRUPOS[k] = (g, g[0][1] - 0.04, fin)

# ---------------------------------------------------------------- subtítulos (abajo; en los planos del freno, más abajo para dejar sitio a los rótulos)
def y_sub(f):
    if f < B0: return 0.80
    if f < A2: return 0.895
    if f < CTA: return 0.82
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
    # cada línea entra con su propio rebote (como Clod en el capó)
    for k, (txt, col) in enumerate((("¿TU COCHE SIGUE", BLANCO), ("BOTANDO?", AMARILLO))):
        pk = ease_back((f - G0 - k * 5) / 7.0)
        if pk <= 0: continue
        szk = int(86 * (0.6 + 0.4 * pk)) if k == 0 else int(116 * (0.6 + 0.4 * pk))
        yk = 0.095 * H + (0 if k == 0 else 112) - 10 * math.sin(min(1.0, (f - G0) / 40.0) * math.pi * 3) * math.exp(-(f - G0) / 25.0)
        dd.text((W / 2, yk), txt, font=fnt(szk, "Black"), fill=col + (al,), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, al))
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
 ("muelle", FW(1, 1), C0 - 1, "MUELLE", "aguanta el peso del coche", (255, 120, 60)),
 ("amortiguador", FW(1, 8), D0 - 1, "AMORTIGUADOR", "frena el rebote", (110, 200, 255)),
 ("vastago", FW(1, 17), FW(1, 20) - 1, "VÁSTAGO", "entra en el cuerpo", (215, 222, 235)),
 ("piston", FW(1, 20), FW(1, 23) - 1, "PISTÓN", "empuja el aceite", (200, 210, 225)),
 ("aceite", FW(1, 23), E0 - 1, "ACEITE", "llena el tubo", (255, 190, 60)),
 ("valvulas", FW(1, 32) - 8, F0 - 1, "VÁLVULAS", "agujeros muy pequeños", (120, 230, 200)),
 ("calor", FW(1, 37), A2 - 1, "CALOR", "el bote se convierte en calor", (255, 120, 40)),
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

# ---------------------------------------------------------------- gráfico del rebote: sin amortiguador sigue botando, con amortiguador se para
G_F0, G_F1 = FW(1, 9) - 4, D0 - 1
def grafico(img, f):
    if not (G_F0 <= f <= G_F1): return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    a = min(1.0, (f - G_F0) / 6.0, max(0.0, (G_F1 - f) / 5.0)); al = int(255 * a)
    x0, y0, x1, y1 = 40, int(0.50 * H), 600, int(0.50 * H) + 380
    dd.rounded_rectangle((x0, y0, x1, y1), radius=26, fill=(12, 14, 18, int(215 * a)), outline=(255, 255, 255, int(70 * a)), width=2)
    dd.text((x0 + 26, y0 + 34), "BOTE DESPUÉS DE UN BACHE", font=fnt(30, "Black"), fill=(235, 235, 235, al), anchor="lm")
    gx0, gx1, gy = x0 + 28, x1 - 28, y0 + 180
    dd.line((gx0, gy, gx1, gy), fill=(255, 255, 255, int(60 * a)), width=2)
    prog = min(1.0, (f - G_F0) / 40.0)
    for k, (col, amort, txt) in enumerate((((255, 70, 60), 0.18, "SIN AMORTIGUADOR"), ((90, 220, 120), 1.35, "CON AMORTIGUADOR"))):
        pts = []
        n = int(140 * prog) + 2
        for i in range(n):
            t = i / 140.0 * 3.2
            y = math.exp(-amort * t) * math.cos(2 * math.pi * 1.6 * t)
            pts.append((gx0 + (gx1 - gx0) * i / 140.0, gy - 105 * y))
        if len(pts) > 1: dd.line(pts, fill=col + (al,), width=7, joint="curve")
        dd.line((x0 + 28, y1 - 66 + k * 32, x0 + 60, y1 - 66 + k * 32), fill=col + (al,), width=7)
        dd.text((x0 + 74, y1 - 66 + k * 32), txt, font=fnt(25, "Black"), fill=col + (al,), anchor="lm")
    img.alpha_composite(capa)

# ---------------------------------------------------------------- consejo: avisos que se apilan arriba
AVISOS = [(FW(2, 3), "¿FLOTA?", (255, 212, 0)), (FW(2, 4), "¿CABECEA AL FRENAR?", (255, 160, 60)), (FW(2, 7), "¿SE BALANCEA EN CURVAS?", (255, 90, 60))]
def avisos(img, f):
    if not (A2 <= f < INS): return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    alfa = 255 if f < INS - 4 else int(255 * (INS - f) / 4)
    act = [(k, a) for k, a in enumerate(AVISOS) if a[0] <= f]
    if act:
        k, (f0, txt, col) = act[-1]
        base = 80
        while fnt(base, "Black").getlength(txt) > W - 90 and base > 40: base -= 2
        p = ease_back((f - f0) / 7.0); sz = int(base * (0.6 + 0.4 * p))
        dd.text((W / 2, 0.075 * H), txt, font=fnt(sz, "Black"), fill=col + (alfa,), anchor="mm", stroke_width=11, stroke_fill=(0, 0, 0, alfa))
        dd.text((W / 2, 0.075 * H + 70), f"SÍNTOMA {k + 1} DE 4", font=fnt(30, "Black"), fill=(235, 235, 235, alfa), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, alfa))
    img.alpha_composite(capa)

# ---------------------------------------------------------------- inserto: amortiguador nuevo frente a gastado
def inserto(img, f):
    if not (INS <= f < A3): return
    A = anclas.get(str(f)) or {}
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    alfa = 255 if f < A3 - 4 else int(255 * (A3 - f) / 4)
    p0 = ease_back((f - INS) / 7.0)
    dd.text((W / 2, 0.075 * H + 70), "SÍNTOMA 4 DE 4", font=fnt(30, "Black"), fill=(235, 235, 235, alfa), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, alfa))
    dd.text((W / 2, 0.075 * H), "¿PIERDE ACEITE?", font=fnt(int(84 * (0.6 + 0.4 * p0)), "Black"), fill=(255, 212, 0, alfa), anchor="mm", stroke_width=11, stroke_fill=(0, 0, 0, alfa))
    for k, (cl, tit, sub, col) in enumerate((("AN", "NUEVO", "seco y limpio", (90, 220, 120)), ("AG", "GASTADO", "pierde aceite", (255, 70, 60)))):
        f0 = INS + 6 + k * 12
        if f < f0: continue
        pt = A.get(cl)
        if pt is None: continue
        p = ease_back((f - f0) / 8.0)
        caja(dd, pt[0] * W, 0.725 * H, tit, sub, col, escala=0.70 + 0.12 * p, alfa=alfa)
    img.alpha_composite(capa)

# ---------------------------------------------------------------- dato del RACE durante el aviso final
DATO_F0 = FW(3, 6) - 2
def dato(img, f):
    if not (DATO_F0 <= f < CTA): return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    p = ease_back((f - DATO_F0) / 8.0); al = 255 if f < CTA - 4 else int(255 * (CTA - f) / 4)
    cx, cy = W / 2, 0.645 * H
    bw, bh = 820 * (0.85 + 0.15 * p), 300 * (0.85 + 0.15 * p)
    dd.rounded_rectangle((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), radius=30, fill=(12, 14, 18, int(225 * al / 255)), outline=(255, 70, 60, al), width=5)
    n = min(35, int(35 * min(1.0, (f - DATO_F0) / 18.0)))
    dd.text((cx, cy - 62), f"HASTA UN {n} %", font=fnt(int(104 * (0.85 + 0.15 * p)), "Black"), fill=(255, 70, 60, al), anchor="mm")
    dd.text((cx, cy + 32), "MÁS DISTANCIA DE FRENADA", font=fnt(int(44 * (0.85 + 0.15 * p)), "Black"), fill=(245, 245, 245, al), anchor="mm")
    dd.text((cx, cy + 98), "con amortiguadores en mal estado · Fuente: RACE", font=fnt(int(27 * (0.85 + 0.15 * p)), "SemiBold"), fill=(200, 200, 200, al), anchor="mm")
    img.alpha_composite(capa)

# ---------------------------------------------------------------- cierre
def cierre(img, f):
    if f < CTA + 4: return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    p = ease_back((f - CTA - 4) / 8.0)
    dd.text((W / 2, 0.095 * H), "SÍGUENOS", font=fnt(int(104 * (0.6 + 0.4 * p)), "Black"), fill=AMARILLO + (255,), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, 255))
    if f >= CTA + 12:
        p2 = ease_back((f - CTA - 12) / 8.0)
        dd.text((W / 2, 0.095 * H + 100), "¿QUÉ PIEZA DESMONTAMOS MAÑANA?", font=fnt(int(44 * (0.6 + 0.4 * p2)), "Black"), fill=BLANCO + (255,), anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0, 255))
    img.alpha_composite(capa)

def componer(fr, f):
    img = fr.convert("RGBA")
    gancho(img, f); rotulos(img, f); grafico(img, f); avisos(img, f); inserto(img, f); dato(img, f); cierre(img, f)
    subtitulo(ImageDraw.Draw(img), f)
    return img.convert("RGB")

if PRUEBA:
    for f in PRUEBA:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf", f"select=eq(n\\,{f - 1}),scale={W}:{H}:flags=lanczos", "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        componer(Image.frombytes("RGB", (W, H), raw), f).save(f"/tmp/prueba_am_{f:04d}.png")
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
