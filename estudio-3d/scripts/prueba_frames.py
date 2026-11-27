# Fotogramas de prueba rápidos (Cycles, 34 %, 24 muestras). Uso: blender -b escena.blend --python prueba_frames.py -- <carpeta> <f1,f2,...>
import bpy, os, sys
argv = sys.argv[sys.argv.index("--") + 1:]; out = argv[0]; fr = [int(x) for x in argv[1].split(",")]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; c = sc.cycles
cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
for dv in cp.devices: dv.use = dv.type == "OPTIX"
for m in bpy.data.materials:
    if m.node_tree and ("Aceite" in m.name or "Refrigerante" in m.name):
        for n in m.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                for k, v in (("Subsurface Weight", 0.0), ("Emission Strength", 0.0), ("Transmission Weight", 1.0)):
                    if not n.inputs[k].is_linked: n.inputs[k].default_value = v
c.device = "GPU"; c.samples = 24; c.use_denoising = True; c.use_light_tree = True
sc.render.resolution_percentage = 34; sc.render.use_persistent_data = True
for f in fr:
    sc.frame_set(f); sc.render.filepath = os.path.join(out, "t_%04d.png" % f); bpy.ops.render.render(write_still=True)
print("PRUEBAS_OK")
