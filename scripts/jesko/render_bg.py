# Uso: blender -b episode.blend --python render_bg.py -- <pct> <samples> <carpeta_frames>
import bpy, sys, os
argv = sys.argv[sys.argv.index("--") + 1:]
pct, samples, outdir = int(argv[0]), int(argv[1]), argv[2]
sc = bpy.context.scene; r = sc.render
r.resolution_percentage = pct
sc.eevee.taa_render_samples = samples
r.image_settings.media_type = 'IMAGE'; r.image_settings.file_format = 'PNG'; r.image_settings.color_depth = '8'
r.use_overwrite = False; r.use_placeholder = True
os.makedirs(outdir, exist_ok=True)
r.filepath = os.path.join(outdir, "f_")
bpy.ops.render.render(animation=True)
open(os.path.join(outdir, "DONE.txt"), "w").write("ok")
