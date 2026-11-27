# Uso: blender -b --factory-startup --python encode_bg.py -- <carpeta_frames> <salida.mp4> <ancho> <alto> [fps=30] [calidad=HIGH]
import bpy, sys, os
argv = sys.argv[sys.argv.index("--") + 1:]
src, dst, w, h = argv[0], argv[1], int(argv[2]), int(argv[3])
fps = int(argv[4]) if len(argv) > 4 else 30
calidad = argv[5] if len(argv) > 5 else 'HIGH' 
sc = bpy.context.scene
sc.render.fps = fps; sc.render.resolution_x = w; sc.render.resolution_y = h; sc.render.resolution_percentage = 100
files = sorted(f for f in os.listdir(src) if f.endswith(".png"))
sc.sequence_editor_create()
strip = sc.sequence_editor.strips.new_image("frames", os.path.join(src, files[0]), 1, 1) if hasattr(sc.sequence_editor, "strips") else sc.sequence_editor.sequences.new_image("frames", os.path.join(src, files[0]), 1, 1)
for f in files[1:]:
    strip.elements.append(f)
# 26-11-2026: si los fotogramas se renderizaron al 67 % hay que ESCALARLOS al tamaño del vídeo (si no, quedan bordes negros)
_im = bpy.data.images.load(os.path.join(src, files[0])); iw, ih = _im.size; bpy.data.images.remove(_im)
if (iw, ih) != (w, h):
    strip.transform.scale_x = w / iw; strip.transform.scale_y = h / ih
sc.frame_start = 1; sc.frame_end = len(files)
r = sc.render
r.image_settings.media_type = 'VIDEO'; r.image_settings.file_format = 'FFMPEG'
r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'; r.ffmpeg.constant_rate_factor = calidad; r.ffmpeg.ffmpeg_preset = 'GOOD'
r.ffmpeg.audio_codec = 'NONE'
sc.view_settings.view_transform = 'Standard'
r.filepath = dst
bpy.ops.render.render(animation=True)
open(dst + ".done", "w").write(str(len(files)))
