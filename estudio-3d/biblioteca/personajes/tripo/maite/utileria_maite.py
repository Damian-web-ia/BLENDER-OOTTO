# UTILERÍA DE MAITE · piezas mecánicas que puede coger · EKORUEDAS · 28-11-2026
# Funciones (se cargan con exec desde las pruebas):
#   llave_cruz(nombre)            llave de cruz para tuercas de rueda (acero cromado, vasos hexagonales 17/19/21/23)
#   agarrar(arm, objeto, lado)    la pieza queda en la palma de esa mano (hija del hueso de la mano) y la mano la cierra
# Medidas a la escala del modelo (Maite mide 1 m en el archivo; real 1,73 m): una llave de 40 cm reales mide 0,23.
import bpy, bmesh, math
from mathutils import Vector, Matrix

ESCALA = 1.0 / 1.73


def _metal(nombre, color=(0.78, 0.78, 0.80), rug=0.18, anis=0.0):
    mt = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre); mt.use_nodes = True
    N = mt.node_tree.nodes; L = mt.node_tree.links; bs = N["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (*color, 1); bs.inputs["Metallic"].default_value = 1.0
    bs.inputs["Roughness"].default_value = rug; bs.inputs["Anisotropic"].default_value = anis
    # marcas de uso: rugosidad que varía un poco (no es un espejo perfecto)
    tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 180.0
    nz.inputs["Detail"].default_value = 6.0; L.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rug * 0.7; mr.inputs["To Max"].default_value = rug * 1.6
    L.new(nz.outputs["Fac"], mr.inputs["Value"]); L.new(mr.outputs["Result"], bs.inputs["Roughness"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.05; bp.inputs["Distance"].default_value = 0.0002
    L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], bs.inputs["Normal"])
    return mt


def llave_cruz(nombre="UTIL_llave_cruz"):
    """Dos barras cruzadas soldadas en el centro; en cada punta un vaso hexagonal hueco de distinta medida."""
    viejo = bpy.data.objects.get(nombre)
    if viejo: bpy.data.objects.remove(viejo)
    bm = bmesh.new()
    largo = 0.40 * ESCALA; r_barra = 0.0095 * ESCALA
    for eje in (Vector((1, 0, 0)), Vector((0, 1, 0))):
        rot = Vector((0, 0, 1)).rotation_difference(eje).to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=r_barra, radius2=r_barra, depth=largo, matrix=rot)
    # vasos hexagonales en las cuatro puntas (17, 19, 21, 23 mm entre caras)
    for k, (eje, mm) in enumerate(((Vector((1, 0, 0)), 17), (Vector((-1, 0, 0)), 19), (Vector((0, 1, 0)), 21), (Vector((0, -1, 0)), 23))):
        r_ext = (mm / 1000.0 / math.sqrt(3) + 0.0045) * ESCALA; prof = 0.045 * ESCALA
        centro = eje * (largo / 2 + prof / 2 - 0.004 * ESCALA)
        rot = Vector((0, 0, 1)).rotation_difference(eje).to_matrix().to_4x4()
        M = Matrix.Translation(centro) @ rot
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=r_ext, radius2=r_ext, depth=prof, matrix=M)
        # biselado suave de las aristas del vaso (que la luz las dibuje)
        ar = [e for e in bm.edges if all(v in r["verts"] for v in e.verts)]
        bmesh.ops.bevel(bm, geom=ar, offset=0.0012 * ESCALA, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(nombre, me); bpy.context.scene.collection.objects.link(ob)
    md = ob.modifiers.new("Bisel", 'BEVEL'); md.width = 0.0008 * ESCALA; md.segments = 2; md.limit_method = 'ANGLE'
    ob.modifiers.new("Suave", 'WEIGHTED_NORMAL')
    me.materials.append(_metal("UTIL_acero_cromado", (0.80, 0.80, 0.82), 0.16))
    ob["agarre_radio"] = r_barra; ob["agarre_eje"] = (1.0, 0.0, 0.0); ob["agarre_punto"] = (largo * 0.32, 0.0, 0.0)
    print("UTILERIA llave de cruz", round(largo, 3), "m (modelo)", flush=True)
    return ob


def agarrar(arm, ob, lado="R"):
    """Coloca la pieza en la palma: el punto de agarre en el centro de la palma y su eje cruzando la palma (de índice
    a meñique). Queda hija del hueso de la mano, así la sigue en todo (IK, FK, giros)."""
    l = "Right" if lado in ("R", "Right") else "Left"; P = "mixamorig:"
    bpy.context.view_layer.update()
    pb = arm.pose.bones
    def mundo(n, cola=False):
        b = pb[P + l + n]; return arm.matrix_world @ (b.tail if cola else b.head)
    # con la mano ya cerrada: el hueco del puño está entre la palma y las segundas falanges de los dedos
    mano = mundo("Hand"); ind1 = mundo("HandIndex1"); men1 = mundo("HandPinky1")
    f2 = [mundo(f"Hand{d}2") for d in ("Index", "Middle", "Ring", "Pinky")]
    palma = (mano * 0.30 + ind1 * 0.35 + men1 * 0.35)
    hueco = palma * 0.45 + (sum(f2, Vector()) / 4) * 0.55
    eje = (f2[0] - f2[3]).normalized()                     # de meñique a índice: el centro de la cruz sale por el meñique
    dedos = (mundo("HandMiddle1") - mano).normalized()
    y_ = (dedos - eje * dedos.dot(eje)).normalized(); z_ = eje.cross(y_)
    R_ = Matrix((eje, y_, z_)).transposed().to_4x4()
    punto = Vector(ob.get("agarre_punto", (0, 0, 0)))
    ob.matrix_world = Matrix.Translation(hueco) @ R_ @ Matrix.Translation(-punto)
    mw = ob.matrix_world.copy()
    ob.parent = arm; ob.parent_type = 'BONE'; ob.parent_bone = P + l + "Hand"
    bpy.context.view_layer.update(); ob.matrix_world = mw
    print("UTILERIA", ob.name, "en la mano", l, flush=True)
    return ob
