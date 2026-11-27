# Portada de los despieces (EKORUEDAS · 27-11-2026): un fotograma fuerte del render + texto grande (máx. 5 palabras)
# con borde negro, viñeta suave y versión cuadrada. Sin logo, nombre del taller ni teléfono.
# Uso: python3 portada_despiece.py <fotograma.png> <salida_vertical.jpg> <salida_cuadrada.jpg> "LÍNEA 1|blanco" "LÍNEA 2|amarillo" [y_texto=0.10]
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
FONT = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
COL = {"blanco": (255, 255, 255), "amarillo": (255, 212, 0), "naranja": (255, 140, 40), "azul": (110, 200, 255), "rojo": (255, 70, 60)}
src, out_v, out_c = sys.argv[1:4]
lineas = [a.split("|") for a in sys.argv[4:] if "|" in a]
y0 = float([a for a in sys.argv[4:] if a.startswith("y=")][0][2:]) if any(a.startswith("y=") for a in sys.argv[4:]) else 0.10
W, H = 1080, 1920
img = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
img = ImageEnhance.Contrast(img).enhance(1.08); img = ImageEnhance.Color(img).enhance(1.12)
# viñeta y degradado oscuro arriba para que el texto se lea
v = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(v)
for i in range(60):
    a = int(255 * (i / 60) ** 2 * 0.55); dv.rectangle((i * 6, i * 10, W - i * 6, H - i * 10), outline=255 - a)
osc = Image.new("RGB", (W, H), (0, 0, 0)); img = Image.composite(img, osc, v.filter(ImageFilter.GaussianBlur(60)))
grad = Image.new("L", (W, H), 0); dg = ImageDraw.Draw(grad)
for y in range(int(H * 0.42)): dg.line((0, y, W, y), fill=int(170 * (1 - y / (H * 0.42)) ** 1.6))
img = Image.composite(osc, img, grad)
d = ImageDraw.Draw(img)
def fnt(sz):
    f = ImageFont.truetype(FONT, sz)
    try: f.set_variation_by_name("Black")
    except Exception: pass
    return f
y = y0 * H
for k, (txt, c) in enumerate(lineas):
    base = 150 if k == len(lineas) - 1 else 112
    while fnt(base).getlength(txt) > W - 70 and base > 50: base -= 2
    d.text((W / 2, y + base / 2), txt, font=fnt(base), fill=COL.get(c, (255, 255, 255)), anchor="mm", stroke_width=max(8, base // 9), stroke_fill=(0, 0, 0))
    y += base + 14
img.save(out_v, quality=92)
# cuadrada: recorte centrado que conserva el texto (desde arriba)
top = max(0, int(y0 * H) - 60); sq = img.crop((0, top, W, top + W)); sq.save(out_c, quality=92)
print("ok", out_v, out_c)
