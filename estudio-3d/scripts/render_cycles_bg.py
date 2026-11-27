# Uso: blender -b escena.blend --python render_cycles_bg.py -- <carpeta> <muestras> [frames_salida_coma]
# 4K vertical 2160x3840, 60 fps (remapeo de tiempo x2), Cycles GPU OptiX, denoise OIDN.
import bpy, sys, os, time
argv = sys.argv[sys.argv.index("--") + 1:]
outdir, muestras = argv[0], int(argv[1])
lista = [int(x) for x in argv[2].split(",")] if len(argv) > 2 and argv[2] else None
os.makedirs(outdir, exist_ok=True)
# GPU
cp = bpy.context.preferences.addons["cycles"].preferences
cp.compute_device_type = "OPTIX"
cp.get_devices()
for d in cp.devices:
    d.use = (d.type == "OPTIX")
# Ajustes de materiales para Cycles (en EEVEE el líquido llevaba subsuperficie y brillo propio para no verse vacío;
# en Cycles la refracción es real y eso lo volvía lechoso): electrolito transparente de verdad.
for m in bpy.data.materials:
    if not m.use_nodes or not ("Electrolito" in m.name or "Aceite" in m.name): continue
    for n in m.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            for k, v in (("Subsurface Weight", 0.0), ("Emission Strength", 0.0), ("Transmission Weight", 1.0)):
                if k in n.inputs and not n.inputs[k].is_linked: n.inputs[k].default_value = v
            if "Electrolito" in m.name:
                n.inputs["Roughness"].default_value = 0.015
                if not n.inputs["Base Color"].is_linked: n.inputs["Base Color"].default_value = (0.93, 0.97, 1.0, 1)
sc = bpy.context.scene; r = sc.render; c = sc.cycles
fs0, fe0 = sc.frame_start, sc.frame_end

# ---- Profundidad de campo cinematográfica (skill 4K, punto 2): en cada fotograma se mide con rayos desde la cámara a qué
# distancia está lo que ocupa el centro del cuadro y se enfoca ahí. Con f/11 (cerca) y f/14 el fondo se suaviza en los planos cercanos de
# la pieza y los planos abiertos (Alex, Clod, taller) siguen nítidos. En macro (foco a menos de 12 cm) no hay desenfoque.
import statistics
from mathutils import Vector
def _dist_centro(sc, dg, cam):
    fr = cam.data.view_frame(scene=sc)                 # esquinas del cuadro en espacio de cámara
    tr, br_, bl, tl = fr
    mw = cam.matrix_world; o = mw.translation
    ds = []
    for u in (0.35, 0.5, 0.65):
        for v in (0.35, 0.5, 0.65):
            pl = bl + (br_ - bl) * u + (tl - bl) * v
            d = (mw.to_3x3() @ pl).normalized()
            org = o.copy(); rec = 0.0
            for _ in range(12):
                ok, loc, nor, idx, ob, mx = sc.ray_cast(dg, org, d)
                if not ok: break
                if ob is not None and (ob.hide_render or ob.original.hide_render or ob.type not in ("MESH", "CURVE", "SURFACE", "META", "FONT", "CURVES")):
                    rec += (loc - org).length + 1e-4; org = loc + d * 1e-4; continue
                ds.append(rec + (loc - org).length); break
    if not ds: return None
    ds.sort(); return ds[max(0, int(len(ds) * 0.3) - 1)]
def enfoque(sc, cortes):
    cams = [o for o in sc.objects if o.type == "CAMERA"]
    dg = bpy.context.evaluated_depsgraph_get()
    claves = []
    ult = 3.0
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
        cam = sc.camera
        d = _dist_centro(sc, dg, cam) if cam else None
        if d is None: d = ult
        ult = d
        claves.append((f, d))
    for cam in cams:
        cd = cam.data; cd.dof.use_dof = True; cd.dof.focus_object = None
        for f, d in claves:
            cd.dof.focus_distance = max(0.02, d); cd.dof.keyframe_insert("focus_distance", frame=f)
            cd.dof.aperture_fstop = (11.0 if d < 1.0 else 14.0) if d >= 0.12 else 400.0; cd.dof.keyframe_insert("aperture_fstop", frame=f)
        ad = cd.animation_data
        if ad and ad.action:
            try: fcs = list(ad.action.fcurves)
            except Exception: fcs = [fc for l in ad.action.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
            for fc in fcs:
                if not fc.data_path.startswith("dof."): continue
                for k in fc.keyframe_points:
                    k.interpolation = "CONSTANT" if (int(round(k.co[0])) + 1) in cortes else "LINEAR"
    return claves

_cortes = set()
try:
    import json as _j, glob as _g
    _an = _g.glob(os.path.join(os.path.dirname(bpy.data.filepath), 'anclas_*.json'))
    if _an: _cortes = set(_j.load(open(_an[0], encoding='utf-8')).get('cortes', []))
except Exception as _e:
    print('sin cortes', _e)
_t = time.time(); _cl = enfoque(sc, _cortes)
open(os.path.join(outdir, 'enfoque.txt'), 'w').write('%.0f s\n' % (time.time() - _t) + '\n'.join('%d %.3f' % x for x in _cl))
r.engine = "CYCLES"
c.device = "GPU"
r.resolution_x, r.resolution_y, r.resolution_percentage = 2160, 3840, 100
r.fps, r.fps_base = 60, 1.0
r.frame_map_old, r.frame_map_new = 100, 200
sc.frame_start, sc.frame_end = fs0 * 2, fe0 * 2
c.samples = muestras
c.use_adaptive_sampling = True
c.adaptive_threshold = 0.01
c.adaptive_min_samples = 16
c.use_denoising = True
c.denoiser = "OPENIMAGEDENOISE"
try:
    c.denoising_use_gpu = True
except Exception:
    pass
c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
c.denoising_prefilter = "ACCURATE"
c.use_light_tree = True
c.max_bounces = 12
c.diffuse_bounces = 4
c.glossy_bounces = 6
c.transmission_bounces = 12
c.volume_bounces = 2
c.transparent_max_bounces = 24
c.caustics_reflective = False
c.caustics_refractive = False
c.sample_clamp_indirect = 10.0
c.blur_glossy = 0.5
r.use_persistent_data = True
r.film_transparent = False
r.image_settings.media_type = "IMAGE"
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGB"
r.image_settings.color_depth = "8"
r.use_overwrite = False
r.use_placeholder = True
log = open(os.path.join(outdir, "tiempos.txt"), "a")
log.write("inicio %s frames %d-%d muestras %d\n" % (time.strftime("%H:%M:%S"), sc.frame_start, sc.frame_end, muestras)); log.flush()
if lista:
    for f in lista:
        t = time.time()
        sc.frame_set(f)
        r.filepath = os.path.join(outdir, "f_%04d.png" % f)
        bpy.ops.render.render(write_still=True)
        log.write("frame %d %.1f s\n" % (f, time.time() - t)); log.flush()
    log.write("PRUEBA_OK\n"); log.close()
else:
    r.filepath = os.path.join(outdir, "f_")
    t = time.time()
    bpy.ops.render.render(animation=True)
    log.write("fin %s total %.0f s\n" % (time.strftime("%H:%M:%S"), time.time() - t)); log.close()
    open(os.path.join(outdir, "DONE.txt"), "w").write("ok")
