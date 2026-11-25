# Uso: blender -b --factory-startup --python encode_bg.py -- <carpeta_frames> <salida.mp4> <ancho> <alto>
import bpy, sys, os
argv = sys.argv[sys.argv.index("--") + 1:]
src, dst, w, h = argv[0], argv[1], int(argv[2]), int(argv[3])
sc = bpy.context.scene
sc.render.fps = 30; sc.render.resolution_x = w; sc.render.resolution_y = h; sc.render.resolution_percentage = 100
files = sorted(f for f in os.listdir(src) if f.endswith(".png"))
sc.sequence_editor_create()
strip = sc.sequence_editor.strips.new_image("frames", os.path.join(src, files[0]), 1, 1) if hasattr(sc.sequence_editor, "strips") else sc.sequence_editor.sequences.new_image("frames", os.path.join(src, files[0]), 1, 1)
for f in files[1:]:
    strip.elements.append(f)
sc.frame_start = 1; sc.frame_end = len(files)
r = sc.render
r.image_settings.media_type = 'VIDEO'; r.image_settings.file_format = 'FFMPEG'
r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'; r.ffmpeg.constant_rate_factor = 'HIGH'; r.ffmpeg.ffmpeg_preset = 'GOOD'
r.ffmpeg.audio_codec = 'NONE'
sc.view_settings.view_transform = 'Standard'
r.filepath = dst
bpy.ops.render.render(animation=True)
open(dst + ".done", "w").write(str(len(files)))
