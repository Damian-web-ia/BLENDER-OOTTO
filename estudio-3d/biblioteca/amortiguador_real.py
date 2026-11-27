# AMORTIGUADOR McPHERSON modelado por código (EKORUEDAS · 27-11-2026)
# Piezas separadas para el despiece: soporte, cuerpo, tubo de presión, aceite, pistón con válvulas y láminas,
# vástago cromado, fuelle, muelle, copela con su goma, tuerca y espárragos. Eje Z hacia arriba; origen en la base.
# Uso: AM = {"__name__": "am"}; exec(open(".../amortiguador_real.py", encoding="utf-8").read(), AM)
#      O = AM["construir_amortiguador"](coleccion, pref="AM")            # el del despiece (con interior)
#      AM["construir_amortiguador"](coleccion, pref="AN", interior=False) # el del inserto (nuevo)
#      AM["construir_amortiguador"](coleccion, pref="AG", interior=False, gastado=True)
import bpy, bmesh, math
from mathutils import Vector, Matrix

R_CUERPO = 0.027; Z_CUERPO = 0.30
R_INT = 0.0195
R_VAS = 0.0105; L_VAS = 0.30
Z_PIS = 0.19; H_PIS = 0.016; R_PIS = 0.0182
Z_PLATO = 0.17
Z_COPELA = Z_PIS + L_VAS            # 0.49: arriba del vástago
R_MUELLE = 0.062; R_ALAMBRE = 0.0068; VUELTAS = 6.2
Z_MUELLE0 = Z_PLATO + 0.004; Z_MUELLE1 = Z_COPELA - 0.036
L_MUELLE = Z_MUELLE1 - Z_MUELLE0
Z_ACEITE = (0.035, 0.262)
HUECOS = 6; R_HUECO = 0.0024; RH = 0.0115
Z_FUELLE0 = Z_CUERPO + 0.006


def _mat(nombre, col, metal=0.0, rough=0.5, emis=None, fuerza=0.0, coat=0.0):
    m = bpy.data.materials.get(nombre)
    if m: return m
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    for k in ("Coat Weight", "Clearcoat"):
        if k in b.inputs: b.inputs[k].default_value = coat; break
    if emis:
        b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = fuerza
    return m


def materiales():
    M = {}
    M["pintura"] = _mat("AM_Pintura", (0.018, 0.019, 0.022), 0.25, 0.42, coat=0.4)
    M["cromo"] = _mat("AM_Cromo", (0.88, 0.89, 0.91), 1.0, 0.05)
    M["acero"] = _mat("AM_Acero", (0.56, 0.57, 0.6), 1.0, 0.28)
    M["tubo"] = _mat("AM_TuboInt", (0.62, 0.63, 0.66), 1.0, 0.22)
    M["muelle"] = _mat("AM_Muelle", (0.9, 0.15, 0.02), 0.1, 0.32, coat=0.6)
    M["goma"] = _mat("AM_Goma", (0.011, 0.011, 0.012), 0.0, 0.7)
    M["hueco"] = _mat("AM_Hueco", (0.008, 0.008, 0.01), 0.0, 0.9)
    M["lamina"] = _mat("AM_Lamina", (0.42, 0.45, 0.52), 1.0, 0.18)
    M["chispa"] = _mat("AM_Flujo", (1.0, 0.85, 0.4), 0.0, 0.4, emis=(1.0, 0.82, 0.35), fuerza=9.0)
    M["sucio"] = _mat("AM_PinturaSucia", (0.045, 0.034, 0.024), 0.15, 0.75)
    M["fuga"] = _mat("AM_Fuga", (0.03, 0.018, 0.005), 0.0, 0.05, coat=1.0)
    M["corte"] = _mat("AM_Corte", (0.95, 0.3, 0.04), 0.0, 0.45, emis=(1.0, 0.35, 0.05), fuerza=0.6)
    M["aceite"] = aceite()
    return M


def aceite():
    """Aceite ámbar translúcido; la propiedad de escena 'calor' (0-1) lo vuelve naranja y brillante."""
    m = bpy.data.materials.get("AM_Aceite")
    if m: return m
    m = bpy.data.materials.new("AM_Aceite"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'VIEW_LAYER'; at.attribute_name = "calor"
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (1.0, 0.62, 0.12, 1); mix.inputs[7].default_value = (1.0, 0.22, 0.03, 1)
    nt.links.new(at.outputs["Fac"], mix.inputs[0])
    fz = nt.nodes.new("ShaderNodeMath"); fz.operation = 'MULTIPLY_ADD'; fz.inputs[1].default_value = 5.0; fz.inputs[2].default_value = 1.6
    nt.links.new(at.outputs["Fac"], fz.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mix.outputs[2], em.inputs["Color"]); nt.links.new(fz.outputs[0], em.inputs["Strength"])
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.45
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    sh = nt.nodes.new("ShaderNodeMixShader")
    fac = nt.nodes.new("ShaderNodeMath"); fac.operation = 'MULTIPLY_ADD'; fac.inputs[1].default_value = 0.40; fac.inputs[2].default_value = 0.56
    nt.links.new(lw.outputs["Facing"], fac.inputs[0]); nt.links.new(fac.outputs[0], sh.inputs[0])
    nt.links.new(tr.outputs[0], sh.inputs[1]); nt.links.new(em.outputs[0], sh.inputs[2]); nt.links.new(sh.outputs[0], out.inputs["Surface"])
    for a, v in (("surface_render_method", 'BLENDED'), ("use_transparent_shadow", True), ("show_transparent_back", False)):
        try: setattr(m, a, v)
        except Exception: pass
    return m


def _obj(nombre, bm, mat, col, padre, liso=True, angulo=34):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = liso
    o = bpy.data.objects.new(nombre, me); col.objects.link(o)
    if mat: me.materials.append(mat)
    if padre: o.parent = padre
    if liso:
        md = o.modifiers.new("aristas", 'EDGE_SPLIT'); md.split_angle = math.radians(angulo)
    return o


def cil(nombre, r, z0, z1, mat, col, padre=None, seg=48, tapas=True, grosor=None, loc=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=tapas, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((loc[0], loc[1], (z0 + z1) / 2 + loc[2])))
    o = _obj(nombre, bm, mat, col, padre)
    if grosor:
        s = o.modifiers.new("grosor", 'SOLIDIFY'); s.thickness = grosor; s.offset = -1; s.use_even_offset = True
    return o


def torno(nombre, perfil, mat, col, padre=None, seg=48):
    """Pieza de revolución a partir de un perfil [(r, z), ...] (de abajo arriba)."""
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in perfil]
    for a, b in zip(vs, vs[1:]): bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], cent=(0, 0, 0), axis=(0, 0, 1), angle=math.tau, steps=seg, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _obj(nombre, bm, mat, col, padre)


def caja(nombre, centro, tam, mat, col, padre=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(tam), verts=bm.verts); bmesh.ops.translate(bm, vec=Vector(centro), verts=bm.verts)
    o = _obj(nombre, bm, mat, col, padre, liso=True, angulo=30)
    bv = o.modifiers.new("bisel", 'BEVEL'); bv.width = 0.0015; bv.segments = 2
    o.modifiers.move(o.modifiers.find("bisel"), 0)
    return o


def muelle(nombre, mat, col, padre):
    """Muelle helicoidal (curva con grosor) con las espiras de los extremos cerradas y planas. Origen abajo: escala Z = compresión."""
    cu = bpy.data.curves.new(nombre, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = R_ALAMBRE; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); n = 420
    sp.points.add(n - 1)
    paso_fin = 2 * R_ALAMBRE + 0.001
    activas = VUELTAS - 1.5
    alto_activo = L_MUELLE - 2 * paso_fin * 0.75 - 2 * R_ALAMBRE
    for i in range(n):
        t = i / (n - 1); vuelta = t * VUELTAS; a = vuelta * math.tau
        if vuelta < 0.75: z = R_ALAMBRE + paso_fin * vuelta
        elif vuelta > VUELTAS - 0.75: z = L_MUELLE - R_ALAMBRE - paso_fin * (VUELTAS - vuelta)
        else: z = R_ALAMBRE + paso_fin * 0.75 + alto_activo * (vuelta - 0.75) / activas
        sp.points[i].co = (R_MUELLE * math.cos(a), R_MUELLE * math.sin(a), z, 1)
    o = bpy.data.objects.new(nombre, cu); col.objects.link(o); cu.materials.append(mat)
    o.parent = padre; o.location = (0, 0, Z_MUELLE0)
    return o


def mancha_fuga(nombre, mat, col, padre, a0=-2.2, a1=-0.95, z0=0.07, z1=0.29):
    """Película de aceite sobre el cuerpo, con chorretones hacia abajo."""
    bm = bmesh.new(); r = R_CUERPO + 0.0007; na, nz = 18, 22
    filas = []
    for j in range(nz + 1):
        fila = []
        for i in range(na + 1):
            a = a0 + (a1 - a0) * i / na
            lim = z0 + 0.05 * (0.5 + 0.5 * math.sin(i * 1.9) * math.cos(i * 0.7))
            z = lim + (z1 - lim) * j / nz
            fila.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        filas.append(fila)
    for j in range(nz):
        for i in range(na): bm.faces.new((filas[j][i], filas[j][i + 1], filas[j + 1][i + 1], filas[j + 1][i]))
    o = _obj(nombre, bm, mat, col, padre)
    for k, (a, z) in enumerate(((-0.25, z0 - 0.004), (0.3, z0 + 0.012))):
        bm2 = bmesh.new(); bmesh.ops.create_uvsphere(bm2, u_segments=16, v_segments=10, radius=0.0042)
        bmesh.ops.scale(bm2, vec=Vector((0.8, 0.8, 1.5)), verts=bm2.verts)
        bmesh.ops.translate(bm2, vec=Vector(((r + 0.002) * math.cos(a), (r + 0.002) * math.sin(a), z)), verts=bm2.verts)
        _obj(f"{nombre}_Gota{k}", bm2, mat, col, padre)
    return o


def construir_amortiguador(col, pref="AM", interior=True, gastado=False):
    M = materiales()
    O = {"M": M}
    raiz = bpy.data.objects.new(pref + "_Raiz", None); col.objects.link(raiz); O["raiz"] = raiz
    # cuerpo (todo lo que va fijo al soporte)
    cg = bpy.data.objects.new(pref + "_Cuerpo", None); col.objects.link(cg); cg.parent = raiz; O["cuerpo"] = cg
    pint = M["sucio"] if gastado else M["pintura"]
    e_ = R_CUERPO - 0.0022
    torno(pref + "_Tubo", [(e_, 0.012), (R_CUERPO, 0.012), (R_CUERPO, Z_CUERPO), (e_, Z_CUERPO), (e_, 0.012)], pint, col, cg)
    torno(pref + "_TapaAbajo", [(0.0, 0.0), (R_CUERPO - 0.004, 0.0), (R_CUERPO, 0.004), (R_CUERPO, 0.012), (0.0, 0.012)], pint, col, cg)
    torno(pref + "_TapaArriba", [(R_VAS + 0.0012, Z_CUERPO - 0.004), (R_CUERPO, Z_CUERPO - 0.004), (R_CUERPO, Z_CUERPO + 0.002),
                                 (R_CUERPO - 0.003, Z_CUERPO + 0.006), (R_VAS + 0.0012, Z_CUERPO + 0.006), (R_VAS + 0.0012, Z_CUERPO - 0.004)], M["acero"], col, cg)
    # plato inferior del muelle con su collarín
    torno(pref + "_Plato", [(R_CUERPO, Z_PLATO - 0.022), (R_CUERPO + 0.004, Z_PLATO - 0.022), (R_CUERPO + 0.004, Z_PLATO - 0.006),
                            (R_MUELLE + 0.014, Z_PLATO - 0.004), (R_MUELLE + 0.018, Z_PLATO + 0.004), (R_MUELLE + 0.012, Z_PLATO + 0.002),
                            (R_CUERPO + 0.002, Z_PLATO + 0.002), (R_CUERPO, Z_PLATO - 0.022)], pint, col, cg)
    # soporte inferior: abrazadera y orejas con dos tornillos (va a la mangueta)
    torno(pref + "_Abrazadera", [(R_CUERPO, 0.004), (R_CUERPO + 0.0035, 0.004), (R_CUERPO + 0.0035, 0.088), (R_CUERPO, 0.088), (R_CUERPO, 0.004)], pint, col, cg)
    for k, s in enumerate((-1, 1)):
        caja(f"{pref}_Oreja{k}", (R_CUERPO + 0.026, s * 0.021, 0.046), (0.052, 0.006, 0.084), pint, col, cg)
    for k, z in enumerate((0.022, 0.07)):
        t = cil(f"{pref}_Tornillo{k}", 0.0062, -0.032, 0.032, M["acero"], col, cg, seg=6)
        t.rotation_euler = (math.radians(90), 0, 0); t.location = (R_CUERPO + 0.034, 0, z)
        cil(f"{pref}_Cabeza{k}", 0.0095, 0.032, 0.039, M["acero"], col, t, seg=6)
    if gastado:
        mancha_fuga(pref + "_Fuga", M["fuga"], col, cg)
    # vástago y todo lo que sube y baja con él (grupo móvil: su Z local = -recorrido)
    vg = bpy.data.objects.new(pref + "_Vastago", None); col.objects.link(vg); vg.parent = raiz; O["vastago"] = vg
    cil(pref + "_Cromado", R_VAS, Z_PIS, Z_COPELA - 0.006, M["cromo"], col, vg, seg=40)
    # copela (goma + chapa + tuerca + espárragos) y plato superior
    cop = bpy.data.objects.new(pref + "_Copela", None); col.objects.link(cop); cop.parent = vg; O["copela"] = cop
    torno(pref + "_PlatoSup", [(R_VAS + 0.002, Z_COPELA - 0.038), (R_MUELLE + 0.016, Z_COPELA - 0.038), (R_MUELLE + 0.02, Z_COPELA - 0.032),
                               (R_MUELLE + 0.014, Z_COPELA - 0.031), (R_VAS + 0.002, Z_COPELA - 0.031)], M["acero"], col, cop)
    torno(pref + "_GomaCopela", [(R_VAS + 0.002, Z_COPELA - 0.031), (0.058, Z_COPELA - 0.031), (0.064, Z_COPELA - 0.022),
                                 (0.064, Z_COPELA - 0.012), (0.058, Z_COPELA - 0.006), (R_VAS + 0.002, Z_COPELA - 0.006)], M["goma"], col, cop)
    torno(pref + "_ChapaCopela", [(R_VAS + 0.003, Z_COPELA - 0.007), (0.074, Z_COPELA - 0.007), (0.076, Z_COPELA - 0.003),
                                  (0.07, Z_COPELA + 0.003), (R_VAS + 0.003, Z_COPELA + 0.004)], M["acero"], col, cop)
    cil(pref + "_Tuerca", 0.0125, Z_COPELA + 0.004, Z_COPELA + 0.016, M["acero"], col, cop, seg=6)
    for k in range(3):
        a = math.radians(90 + k * 120)
        cil(f"{pref}_Esparrago{k}", 0.0042, Z_COPELA - 0.004, Z_COPELA + 0.028, M["acero"], col, cop, seg=12, loc=(0.05 * math.cos(a), 0.05 * math.sin(a), 0))
    # muelle (cuelga del cuerpo; se escala en Z cuando el vástago baja)
    O["muelle"] = muelle(pref + "_Muelle", M["muelle"], col, cg)
    # fuelle guardapolvo (origen abajo: se escala en Z con el recorrido)
    pf = []
    alto_f = Z_COPELA - 0.04 - Z_FUELLE0
    for i in range(41):
        z = alto_f * i / 40; r = 0.0175 + 0.0035 * (0.5 + 0.5 * math.cos(i * math.pi / 2))
        pf.append((r, z))
    fu = torno(pref + "_Fuelle", pf, M["goma"], col, cg); fu.location = (0, 0, Z_FUELLE0); O["fuelle"] = fu
    if not interior:
        return O
    # ---- interior (solo en el del despiece)
    torno(pref + "_TuboPresion", [(R_INT - 0.0011, 0.016), (R_INT, 0.016), (R_INT, Z_CUERPO - 0.006), (R_INT - 0.0011, Z_CUERPO - 0.006), (R_INT - 0.0011, 0.016)], M["tubo"], col, cg)
    O["aceite_res"] = cil(pref + "_AceiteReserva", R_CUERPO - 0.0025, 0.014, 0.16, M["aceite"], col, cg, seg=40)
    O["aceite"] = cil(pref + "_Aceite", R_INT - 0.0012, Z_ACEITE[0], Z_ACEITE[1], M["aceite"], col, cg, seg=40)
    torno(pref + "_ValvulaPie", [(0.0, 0.016), (R_INT - 0.001, 0.016), (R_INT - 0.001, 0.026), (0.006, 0.03), (0.0, 0.03)], M["lamina"], col, cg)
    pis = bpy.data.objects.new(pref + "_Piston", None); col.objects.link(pis); pis.parent = vg; pis.location = (0, 0, Z_PIS); O["piston"] = pis
    cil(pref + "_PistonCuerpo", R_PIS, -H_PIS / 2, H_PIS / 2, M["acero"], col, pis, seg=48)
    cil(pref + "_Segmento", R_PIS + 0.0004, -0.003, 0.003, M["goma"], col, pis, seg=48)
    for k in range(HUECOS):
        a = k * math.tau / HUECOS
        cil(f"{pref}_Hueco{k}", R_HUECO, -H_PIS / 2 - 0.0004, H_PIS / 2 + 0.0004, M["hueco"], col, pis, seg=12, loc=(RH * math.cos(a), RH * math.sin(a), 0))
    for k, (r, dz) in enumerate(((0.0135, 0.0014), (0.0118, 0.0014), (0.0100, 0.0014))):
        z0 = H_PIS / 2 + k * dz
        cil(f"{pref}_Lamina{k}", r, z0, z0 + dz * 0.8, M["lamina"], col, pis, seg=40)
        cil(f"{pref}_LaminaB{k}", r, -z0 - dz * 0.8, -z0, M["lamina"], col, pis, seg=40)
    cil(pref + "_TuercaPiston", 0.0068, -H_PIS / 2 - 0.0085, -H_PIS / 2 - 0.0042, M["acero"], col, pis, seg=6)
    # chispas de aceite que pasan por las válvulas (se animan en la escena)
    fl = []
    for k in range(HUECOS):
        a = k * math.tau / HUECOS + 0.2
        for j in range(3):
            bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.0019)
            s = _obj(f"{pref}_Gota_{k}_{j}", bm, M["chispa"], col, pis)
            s.location = (RH * math.cos(a), RH * math.sin(a), -0.03); s["fase"] = j * 8 + k * 3
            fl.append(s)
    O["flujo"] = fl
    return O
