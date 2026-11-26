# Render rápido de fotogramas sueltos con el encuadre real 9:16 (para revisar antes del render final).
# Uso (dentro de Blender): FOTOS = [..]; exec(open(este_fichero).read())
import bpy, os
sc = bpy.context.scene
_out = OUT_PRUEBAS
os.makedirs(_out, exist_ok=True)
_pct, _smp = sc.render.resolution_percentage, sc.eevee.taa_render_samples
sc.render.resolution_percentage = 30; sc.eevee.taa_render_samples = 12
for f in FOTOS:
    sc.frame_set(f); sc.render.filepath = os.path.join(_out, f"p_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
sc.render.resolution_percentage, sc.eevee.taa_render_samples = _pct, _smp
