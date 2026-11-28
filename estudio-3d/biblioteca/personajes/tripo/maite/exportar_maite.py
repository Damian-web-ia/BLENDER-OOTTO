# EXPORTAR A MAITE (entregables de la skill, punto 20) · EKORUEDAS · 28-11-2026
# Uso: blender -b --factory-startup --python exportar_maite.py -- <carpeta_estudio> <carpeta_salida>
# Deja: maite.fbx (malla + esqueleto + 52 shape keys ARKit, para Unity/Unreal/otros), maite.glb (web/AR, con shape keys)
# y maite_ficha.json (huesos de control, shape keys, materiales, medidas). El pelo de hebras (Hair Curves) no existe en
# FBX/GLB: en esos formatos va la masa de pelo de la malla; el .blend es el archivo completo de render.
import bpy, os, sys, json
argv = sys.argv[sys.argv.index("--") + 1:]
EST, OUT = argv[0], argv[1]
PM = os.path.join(EST, "biblioteca", "personajes", "tripo", "maite"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(PM, "maite_v2.blend"))
ARM = bpy.data.objects["MAITE_rig"]; ME = bpy.data.objects["MAITE_cuerpo"]
sel = [ARM, ME] + [o for o in bpy.data.objects if o.name.startswith(("MAITE_globo", "MAITE_cornea", "MAITE_manga"))]
for o in bpy.data.objects: o.select_set(o in sel)
bpy.context.view_layer.objects.active = ARM
ficha = {
    "nombre": "Maite (EKORUEDAS)", "altura_modelo_m": round(ME.dimensions.z, 3), "altura_real_m": 1.73,
    "vertices": len(ME.data.vertices), "caras": len(ME.data.polygons),
    "shape_keys": [k.name for k in ME.data.shape_keys.key_blocks][1:] if ME.data.shape_keys else [],
    "materiales": [m.name for m in ME.data.materials if m],
    "huesos_control": [b.name for b in ARM.data.bones if not b.name.startswith("mixamorig:")],
    "huesos_deformacion": len([b for b in ARM.data.bones if b.use_deform]),
    "propiedades_rig": {k: float(v) for k, v in ARM.pose.bones["CTRL_raiz"].items() if isinstance(v, (int, float))},
}
try:
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "maite.fbx"), use_selection=True, add_leaf_bones=False,
                             bake_anim=False, mesh_smooth_type='FACE', use_mesh_modifiers=False, path_mode='COPY', embed_textures=True)
    ficha["fbx"] = "maite.fbx"
except Exception as e:
    ficha["fbx_error"] = str(e)
try:
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "maite.glb"), export_format='GLB', use_selection=True,
                              export_morph=True, export_skins=True, export_animations=False, export_apply=False)
    ficha["glb"] = "maite.glb"
except Exception as e:
    ficha["glb_error"] = str(e)
json.dump(ficha, open(os.path.join(OUT, "maite_ficha.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("EXPORTAR_OK", {k: v for k, v in ficha.items() if k in ("fbx", "glb", "fbx_error", "glb_error")}, flush=True)
