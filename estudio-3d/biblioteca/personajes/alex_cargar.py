# Cargar ALEX v2 (rig completo) en cualquier escena: exec() y luego cargar_alex_v2(pos, giro_z_grados)
import bpy, math, os
ALEX_BLEND = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D\biblioteca\personajes\alex\alex_v2_rig.blend"
def cargar_alex_v2(pos=(0, 0, 0), giro_z=0.0, blend=ALEX_BLEND):
    if "ALEX_v2" in bpy.data.objects:
        a = bpy.data.objects["ALEX_v2"]
    else:
        with bpy.data.libraries.load(blend, link=False) as (src, dst):
            dst.collections = [c for c in src.collections if c == "ALEX_v2_personaje"]
        col = dst.collections[0]
        bpy.context.scene.collection.children.link(col)
        a = bpy.data.objects["ALEX_v2"]
    a.location = pos; a.rotation_euler = (0, 0, math.radians(giro_z))
    return a
