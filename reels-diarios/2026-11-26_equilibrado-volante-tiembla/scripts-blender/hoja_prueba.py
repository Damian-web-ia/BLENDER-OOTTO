# Hoja de prueba: renderiza los fotogramas FRAMES (al PCT % con MUESTRAS) y los junta en una hoja PNG (SALIDA).
# Variables que pone quien ejecuta: FRAMES, SALIDA, PCT=40, MUESTRAS=16, COLS=5, CAM=None (otra cámara)
import bpy, os, numpy as np, tempfile
sc = bpy.context.scene; r = sc.render
FR = globals()["FRAMES"]; OUT = globals()["SALIDA"]; PCT = globals().get("PCT", 40); SMP = globals().get("MUESTRAS", 16)
COLS = globals().get("COLS", 5); CAMX = globals().get("CAM")
old = (r.resolution_percentage, sc.eevee.taa_render_samples, r.filepath, sc.camera, sc.frame_current, r.use_motion_blur)
r.resolution_percentage = PCT; sc.eevee.taa_render_samples = SMP
r.image_settings.media_type = 'IMAGE'; r.image_settings.file_format = 'PNG'
if CAMX: sc.camera = bpy.data.objects[CAMX]
tmp = tempfile.mkdtemp(); tiles = []
for f in FR:
    sc.frame_set(f); p = os.path.join(tmp, f"t_{f:04d}.png"); r.filepath = p
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(p); w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4); tiles.append(a); bpy.data.images.remove(im)
h, w = tiles[0].shape[:2]; rows = (len(tiles) + COLS - 1) // COLS; g = 6
sheet = np.ones(((h + g) * rows, (w + g) * min(COLS, len(tiles)), 4), dtype=np.float32)
for i, a in enumerate(tiles):
    rr, cc = divmod(i, COLS); y0 = (rows - 1 - rr) * (h + g); x0 = cc * (w + g)
    sheet[y0:y0 + h, x0:x0 + w] = a
img = bpy.data.images.new("hoja", sheet.shape[1], sheet.shape[0], alpha=True)
img.pixels = sheet.ravel().tolist(); img.filepath_raw = OUT; img.file_format = 'PNG'; img.save(); bpy.data.images.remove(img)
r.resolution_percentage, sc.eevee.taa_render_samples, r.filepath, cam0, f0, _ = old; sc.camera = cam0; sc.frame_set(f0)
result = {"hoja": OUT, "tam": [int(sheet.shape[1]), int(sheet.shape[0])]}
