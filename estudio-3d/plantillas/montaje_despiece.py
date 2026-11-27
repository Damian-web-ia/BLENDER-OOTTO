# MONTAJE COMÚN DE LOS DESPIECES 3D (EKORUEDAS · 27-11-2026). Sale de montaje_amortiguador.py.
# Gancho que rebota, subtítulos palabra a palabra (la palabra que suena en amarillo), rótulos de cada pieza con línea a su
# ancla, números que salen sobre las anclas (celdas, válvulas...), gráfico (barras o contador), avisos, inserto nuevo / gastado,
# tarjeta del dato y cierre "síguenos". Todo lo que cambia de un vídeo a otro va en montaje_<pieza>.json.
# Uso: python3 montaje_despiece.py <render.mp4> <anclas.json> <mezcla.ogg> <salida.mp4> <voces.json> <montaje.json> [fotogramas de prueba...]
import sys, json, math, subprocess, re
from PIL import Image, ImageDraw, ImageFont
SRC, ANCLAS, AUDIO, OUT, VOZJ, CFGJ = sys.argv[1:7]
PRUEBA = [int(x) for x in sys.argv[7:]]
W, H = 1080, 1920
FONT = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
_cache = {}
def fnt(sz, peso="ExtraBold"):
    k = (sz, peso)
    if k not in _cache:
        f = ImageFont.truetype(FONT, max(8, sz))
        try: f.set_variation_by_name(peso)
        except Exception: pass
        _cache[k] = f
    return _cache[k]
AMARILLO = (255, 212, 0); BLANCO = (255, 255, 255); NEGRO = (0, 0, 0)
COLORES = {"amarillo": AMARILLO, "blanco": BLANCO, "rojo": (255, 70, 60), "verde": (90, 220, 120), "azul": (110, 200, 255), "naranja": (255, 140, 40)}
def col(c): return tuple(c) if isinstance(c, (list, tuple)) else COLORES[c]
_a = json.load(open(ANCLAS)); anclas = _a["anclas"]; EV = _a["eventos"]; FIN = _a["fin"]
CFG = json.load(open(CFGJ, encoding="utf-8"))
def T(f): return (f - 1) / 30.0
def F(t): return int(round(t * 30)) + 1
def ease_back(x):
    x = max(0.0, min(1.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
_vz = json.load(open(VOZJ, encoding="utf-8"))
def FW(i, j, fin=False):
    l = _vz["lineas"][i]; w = l["words"][j]; return F(l["at"] + (w[2] if fin else w[1]))
def RF(x):
    """Fotograma: número, "EVENTO+n", [línea, palabra(, "fin")(, desplazamiento)]."""
    if isinstance(x, (int, float)): return int(x)
    if isinstance(x, list):
        fin = "fin" in x; off = sum(v for v in x[2:] if isinstance(v, int))
        return FW(x[0], x[1], fin) + off
    m = re.match(r"^([A-Z_0-9]+)\s*([+-]\s*\d+)?$", x.strip())
    return int(EV[m.group(1)]) + (int(m.group(2).replace(" ", "")) if m.group(2) else 0)
B0, A2, INS, A3, CTA = (int(EV[k]) for k in ("B0", "A2", "INS", "A3", "CTA"))

# ---------------------------------------------------------------- subtítulos
GRUPOS = []
for l in _vz["lineas"]:
    ws = [(m, l["at"] + w[1], l["at"] + w[2]) for m, w in zip(l["mostrar"], l["words"])]
    i = 0
    for n in l["grupos"]:
        GRUPOS.append(ws[i:i + n]); i += n
for k, g in enumerate(GRUPOS):
    fin = g[-1][2] + 0.35
    if k + 1 < len(GRUPOS):
        if GRUPOS[k + 1][0][1] - g[-1][2] < 0.6: fin = min(fin, GRUPOS[k + 1][0][1])
    else: fin = g[-1][2] + 0.6
    GRUPOS[k] = (g, g[0][1] - 0.04, fin)
Y_SUB = CFG.get("y_sub", {"intro": 0.80, "pieza": 0.895, "alex": 0.82, "cierre": 0.86})
def y_sub(f):
    if f < B0: return Y_SUB["intro"]
    if f < A2: return Y_SUB["pieza"]
    if INS <= f < A3: return Y_SUB.get("inserto", 0.86)
    if f < CTA: return Y_SUB["alex"]
    return Y_SUB["cierre"]
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
                    w, a, b = g[i]; c = AMARILLO if a - 0.02 <= t < b + 0.06 else BLANCO
                    d.text((x + anchos[i] / 2, y), w, font=fnt(int(66 * s)), fill=c, anchor="mm", stroke_width=9, stroke_fill=NEGRO)
                    x += anchos[i] + esp
            return

# ---------------------------------------------------------------- gancho
GH = RF(CFG.get("gancho_hasta", 100))
def gancho(img, f):
    G0 = 4
    if not (G0 <= f <= GH): return
    a = 1.0 if f < GH - 10 else max(0.0, (GH - f) / 10)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa); al = int(255 * a)
    y = 0.085 * H
    for k, (txt, c) in enumerate(CFG["gancho"]):
        pk = ease_back((f - G0 - k * 5) / 7.0)
        if pk <= 0: continue
        base = 86 if k < len(CFG["gancho"]) - 1 else 112
        while fnt(base, "Black").getlength(txt) > W - 80 and base > 40: base -= 2
        szk = int(base * (0.6 + 0.4 * pk))
        yk = y - 10 * math.sin(min(1.0, (f - G0) / 40.0) * math.pi * 3) * math.exp(-(f - G0) / 25.0)
        dd.text((W / 2, yk), txt, font=fnt(szk, "Black"), fill=col(c) + (al,), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, al))
        y += base + 18
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

# ---------------------------------------------------------------- rótulos de las piezas (uno activo, con línea a su pieza)
PIEZAS = [(p["ancla"], RF(p["desde"]), RF(p["hasta"]), p["titulo"], p.get("sub", ""), col(p["color"])) for p in CFG.get("piezas", [])]
def rotulos(img, f):
    A = anclas.get(str(f)) or {}
    act = [p for p in PIEZAS if p[1] <= f <= p[2]]
    if not act: return
    cl, f0, f1, tit, sub, c = act[-1]
    pt = A.get(cl)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    p = ease_back((f - f0) / 8.0); alfa = 255 if f < f1 - 5 else int(255 * max(0.0, (f1 - f) / 5))
    cj = caja(dd, W / 2, 0.095 * H, tit, sub, c, escala=0.75 + 0.25 * p, alfa=alfa)
    if pt is not None and 0.03 < pt[0] < 0.97 and 0.06 < pt[1] < 0.95:
        px, py = pt[0] * W, (1 - pt[1]) * H
        bx = min(max(px, cj[0] + 40), cj[2] - 40)
        prog = min(1.0, (f - f0) / 6.0); ex, ey = bx + (px - bx) * prog, cj[3] + (py - cj[3]) * prog
        dd.line((bx, cj[3], ex, ey), fill=c + (alfa,), width=4)
        if prog >= 1:
            r = 10 + 3 * math.sin(f * 0.35)
            dd.ellipse((px - r, py - r, px + r, py + r), fill=c + (alfa,), outline=(255, 255, 255, alfa), width=3)
    img.alpha_composite(capa)

# ---------------------------------------------------------------- números sobre anclas (1, 2, 3... uno detrás de otro)
def numeros(img, f):
    N = CFG.get("numeros")
    if not N: return
    f0, f1 = RF(N["desde"]), RF(N["hasta"])
    if not (f0 <= f <= f1): return
    A = anclas.get(str(f)) or {}
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    alfa = 255 if f < f1 - 5 else int(255 * max(0.0, (f1 - f) / 5)); c = col(N.get("color", "amarillo"))
    for k, cl in enumerate(N["anclas"]):
        fk = f0 + k * N.get("cada", 4)
        pt = A.get(cl)
        if f < fk or pt is None: continue
        p = ease_back((f - fk) / 6.0); r = 38 * (0.5 + 0.5 * p)
        x, y = pt[0] * W, (1 - pt[1]) * H
        dd.ellipse((x - r, y - r, x + r, y + r), fill=(12, 14, 18, int(alfa * 0.85)), outline=c + (alfa,), width=5)
        dd.text((x, y + 2), str(k + 1), font=fnt(int(44 * (0.5 + 0.5 * p)), "Black"), fill=c + (alfa,), anchor="mm")
    img.alpha_composite(capa)

# ---------------------------------------------------------------- gráfico: barras o contador
def grafico(img, f):
    G = CFG.get("grafico")
    if not G: return
    f0, f1 = RF(G["desde"]), RF(G["hasta"])
    if not (f0 <= f <= f1): return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    a = min(1.0, (f - f0) / 6.0, max(0.0, (f1 - f) / 5.0)); al = int(255 * a)
    y0 = int(G.get("y", 0.60) * H)
    if G["tipo"] == "barras":
        x0, x1 = 60, W - 60; y1 = y0 + 120 + 92 * len(G["barras"]) + (46 if G.get("nota") else 0)
        dd.rounded_rectangle((x0, y0, x1, y1), radius=26, fill=(12, 14, 18, int(215 * a)), outline=(255, 255, 255, int(70 * a)), width=2)
        dd.text((x0 + 30, y0 + 46), G["titulo"], font=fnt(38, "Black"), fill=(235, 235, 235, al), anchor="lm")
        prog = min(1.0, (f - f0 - 6) / 24.0)
        for k, b_ in enumerate(G["barras"]):
            txt, v, c = b_[:3]; c = col(c); yb = y0 + 110 + k * 92
            dd.text((x0 + 30, yb + 30), txt, font=fnt(34, "Black"), fill=c + (al,), anchor="lm")
            bx0, bx1 = x0 + 250, x1 - 40
            dd.rounded_rectangle((bx0, yb + 8, bx1, yb + 52), radius=12, fill=(255, 255, 255, int(30 * a)))
            vv = max(0.0, prog) * v
            if vv > 0.01: dd.rounded_rectangle((bx0, yb + 8, bx0 + (bx1 - bx0) * vv, yb + 52), radius=12, fill=c + (al,))
            et = b_[3] if len(b_) > 3 and prog >= 1 else f"{int(round(vv * 100))} %"
            dd.text((bx1 - 14, yb + 30), et, font=fnt(30, "Black"), fill=(255, 255, 255, al), anchor="rm", stroke_width=4, stroke_fill=(0, 0, 0, al))
        if G.get("nota"): dd.text(((x0 + x1) / 2, y1 - 34), G["nota"], font=fnt(27, "SemiBold"), fill=(210, 210, 210, al), anchor="mm")
    elif G["tipo"] == "contador":
        x0, x1 = 90, W - 90; y1 = y0 + 250
        dd.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=(12, 14, 18, int(215 * a)), outline=col(G.get("color", "azul")) + (al,), width=4)
        dd.text((W / 2, y0 + 48), G["titulo"], font=fnt(36, "Black"), fill=(235, 235, 235, al), anchor="mm")
        fa = RF(G.get("sube_desde", G["desde"])); fb = RF(G.get("sube_hasta", G["hasta"]))
        u = max(0.0, min(1.0, (f - fa) / max(1, fb - fa))); u = 1 - (1 - u) ** 3
        n = G["de"] + (G["a"] - G["de"]) * u
        txt = f"{int(round(n)):,}".replace(",", ".") + G.get("sufijo", "")
        p = ease_back((f - f0) / 8.0)
        dd.text((W / 2, y0 + 150), txt, font=fnt(int(120 * (0.8 + 0.2 * p)), "Black"), fill=col(G.get("color", "azul")) + (al,), anchor="mm")
        if G.get("nota"): dd.text((W / 2, y1 - 26), G["nota"], font=fnt(26, "SemiBold"), fill=(200, 200, 200, al), anchor="mm")
    img.alpha_composite(capa)

# ---------------------------------------------------------------- avisos (uno a la vez, arriba)
AVISOS = [(RF(a["desde"]), RF(a["hasta"]), a["texto"], col(a.get("color", "amarillo")), a.get("sub", "")) for a in CFG.get("avisos", [])]
def avisos(img, f):
    act = [a for a in AVISOS if a[0] <= f <= a[1]]
    if not act: return
    f0, f1, txt, c, sub = act[-1]
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    alfa = 255 if f < f1 - 4 else int(255 * max(0.0, (f1 - f) / 4))
    base = 80
    while fnt(base, "Black").getlength(txt) > W - 90 and base > 40: base -= 2
    p = ease_back((f - f0) / 7.0); sz = int(base * (0.6 + 0.4 * p))
    yy = CFG.get("y_avisos", 0.075) * H
    dd.text((W / 2, yy), txt, font=fnt(sz, "Black"), fill=c + (alfa,), anchor="mm", stroke_width=11, stroke_fill=(0, 0, 0, alfa))
    if sub: dd.text((W / 2, yy + 70), sub, font=fnt(30, "Black"), fill=(235, 235, 235, alfa), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, alfa))
    img.alpha_composite(capa)

# ---------------------------------------------------------------- inserto: nuevo frente a gastado
def inserto(img, f):
    I = CFG.get("inserto")
    if not I or not (INS <= f < A3): return
    A = anclas.get(str(f)) or {}
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    alfa = 255 if f < A3 - 4 else int(255 * (A3 - f) / 4)
    p0 = ease_back((f - INS) / 7.0)
    if I.get("sub"): dd.text((W / 2, 0.075 * H + 70), I["sub"], font=fnt(30, "Black"), fill=(235, 235, 235, alfa), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, alfa))
    base = 84
    while fnt(base, "Black").getlength(I["titulo"]) > W - 90 and base > 40: base -= 2
    dd.text((W / 2, 0.075 * H), I["titulo"], font=fnt(int(base * (0.6 + 0.4 * p0)), "Black"), fill=col(I.get("color", "amarillo")) + (alfa,), anchor="mm", stroke_width=11, stroke_fill=(0, 0, 0, alfa))
    for k, cl in enumerate(("AN", "AG")):
        tit, sub, c = I[cl]; f0 = INS + 6 + k * 12
        if f < f0: continue
        pt = A.get(cl)
        if pt is None: continue
        p = ease_back((f - f0) / 8.0)
        caja(dd, pt[0] * W, I.get("y", 0.725) * H, tit, sub, col(c), escala=0.70 + 0.12 * p, alfa=alfa)
    img.alpha_composite(capa)

# ---------------------------------------------------------------- tarjeta del dato
def dato(img, f):
    D = CFG.get("dato")
    if not D: return
    f0, f1 = RF(D["desde"]), RF(D.get("hasta", "CTA"))
    if not (f0 <= f < f1): return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    p = ease_back((f - f0) / 8.0); al = 255 if f < f1 - 4 else int(255 * (f1 - f) / 4); e = 0.85 + 0.15 * p
    c = col(D.get("color", "rojo"))
    cx, cy = W / 2, D.get("y", 0.645) * H
    bw, bh = 860 * e, 300 * e
    dd.rounded_rectangle((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), radius=30, fill=(12, 14, 18, int(225 * al / 255)), outline=c + (al,), width=5)
    base = 104
    while fnt(base, "Black").getlength(D["grande"]) > 800 and base > 50: base -= 2
    dd.text((cx, cy - 62 * e), D["grande"], font=fnt(int(base * e), "Black"), fill=c + (al,), anchor="mm")
    dd.text((cx, cy + 32 * e), D["medio"], font=fnt(int(44 * e), "Black"), fill=(245, 245, 245, al), anchor="mm")
    if D.get("fuente"): dd.text((cx, cy + 98 * e), D["fuente"], font=fnt(int(27 * e), "SemiBold"), fill=(200, 200, 200, al), anchor="mm")
    img.alpha_composite(capa)

# ---------------------------------------------------------------- cierre
def cierre(img, f):
    if f < CTA + 4: return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(capa)
    p = ease_back((f - CTA - 4) / 8.0)
    dd.text((W / 2, 0.095 * H), "SÍGUENOS", font=fnt(int(104 * (0.6 + 0.4 * p)), "Black"), fill=AMARILLO + (255,), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, 255))
    if f >= CTA + 12:
        p2 = ease_back((f - CTA - 12) / 8.0)
        dd.text((W / 2, 0.095 * H + 100), CFG.get("pregunta_final", "¿QUÉ PIEZA DESMONTAMOS MAÑANA?"), font=fnt(int(44 * (0.6 + 0.4 * p2)), "Black"), fill=BLANCO + (255,), anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0, 255))
    img.alpha_composite(capa)

def componer(fr, f):
    img = fr.convert("RGBA")
    gancho(img, f); rotulos(img, f); numeros(img, f); grafico(img, f); avisos(img, f); inserto(img, f); dato(img, f); cierre(img, f)
    subtitulo(ImageDraw.Draw(img), f)
    return img.convert("RGB")

if PRUEBA:
    for f in PRUEBA:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf", f"select=eq(n\\,{f - 1}),scale={W}:{H}:flags=lanczos", "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        componer(Image.frombytes("RGB", (W, H), raw), f).save(f"/tmp/prueba_{f:04d}.png")
    sys.exit(0)
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf", f"scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-i", AUDIO,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-af", "volume=-0.8dB,alimiter=limit=0.89:level=false", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
f = 0; n = W * H * 3
while True:
    buf = dec.stdout.read(n)
    if len(buf) < n: break
    f += 1; enc.stdin.write(componer(Image.frombytes("RGB", (W, H), buf), f).tobytes())
enc.stdin.close(); enc.wait(); print("fotogramas", f)
