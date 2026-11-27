# TURBOCOMPRESOR REAL (EKORUEDAS · 27-11-2026) · skill "EKORUEDAS Automotive CGI 4K".
# Turbo pequeño de coche de calle (tamaño tipo GT17): todo en metros, eje del rotor = eje X local
# (+X = lado del compresor, -X = lado de la turbina), x = 0 en el centro de la carcasa central.
#   Rueda del compresor: aluminio, 6 álabes + 6 intermedios, inductor Ø38 mm / exductor Ø49 mm.
#   Rueda de la turbina: superaleación, 11 álabes, Ø45 mm a la entrada y Ø40 mm a la salida, soldada al eje.
#   Eje de acero Ø8 mm, dos casquillos flotantes de bronce, cojinete axial, carcasa central de fundición con
#   entrada de aceite arriba y retorno abajo, escudo térmico, carcasa del compresor (aluminio fundido) y de la turbina
#   (fundición resistente al calor) con sus caracolas, brida de salida de 5 espárragos, válvula de descarga (wastegate)
#   con palanca y actuador neumático.
# Las carcasas se construyen enteras y se parten por y = 0 (corte seccional): O["detras"] y O["delante"].
# Uso (dentro de Blender): G = {}; exec(open(ruta).read(), G); O = G["construir_turbo"](coleccion)
import bpy, bmesh, math
from mathutils import Vector, Matrix

TAU = 2 * math.pi
COMP_IND, COMP_EXD = 0.019, 0.0245          # radios del compresor (inductor / exductor)
TURB_IN, TURB_OUT = 0.0225, 0.0200          # radios de la turbina (entrada / salida)


# ------------------------------------------------------------------------------------------------ utilidades
def _malla(nombre, fn, col, liso=True, angulo=40):
    bm = bmesh.new(); fn(bm)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me); col.objects.link(o)
    if liso:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        try: me.set_sharp_from_angle(angle=math.radians(angulo))
        except Exception: pass
    return o


def _suavizar_angulo(o, angulo=40):
    try:
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angulo))
    except Exception:
        try: o.data.set_sharp_from_angle(angle=math.radians(angulo))
        except Exception: pass


def torno_x(bm, prof, seg=96, cerrar=False):
    """Revoluciona el perfil [(x, r)] alrededor del eje X. cerrar=True une el último punto con el primero."""
    angs = [TAU * i / seg for i in range(seg)]
    anillos = []
    for x, r in prof:
        if r < 1e-7: anillos.append([bm.verts.new((x, 0.0, 0.0))])
        else: anillos.append([bm.verts.new((x, r * math.cos(a), r * math.sin(a))) for a in angs])
    pares = list(zip(anillos, anillos[1:])) + ([(anillos[-1], anillos[0])] if cerrar else [])
    for ra, rb in pares:
        if len(ra) == 1 and len(rb) == 1: continue
        if len(ra) == 1:
            for j in range(seg): bm.faces.new((ra[0], rb[j], rb[(j + 1) % seg]))
        elif len(rb) == 1:
            for j in range(seg): bm.faces.new((ra[j], ra[(j + 1) % seg], rb[0]))
        else:
            for j in range(seg): bm.faces.new((ra[j], ra[(j + 1) % seg], rb[(j + 1) % seg], rb[j]))
    return anillos


def cilindro(bm, c, eje, r, largo, seg=48, r2=None):
    """Cilindro cerrado centrado en c a lo largo del vector unitario 'eje'."""
    e = Vector(eje).normalized(); q = e.to_track_quat('Z', 'Y')
    r2 = r if r2 is None else r2
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r2, depth=largo)
    M_ = Matrix.Translation(Vector(c)) @ q.to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=M_, verts=g["verts"])


def caja(bm, x0, x1, y0, y1, z0, z1):
    g = bmesh.ops.create_cube(bm, size=1.0)
    for v in g["verts"]:
        v.co = Vector((x0 if v.co.x < 0 else x1, y0 if v.co.y < 0 else y1, z0 if v.co.z < 0 else z1))


def _bisel(o, ancho, seg=3, angulo=35):
    m = o.modifiers.new("Bisel", "BEVEL"); m.width = ancho; m.segments = seg; m.limit_method = 'ANGLE'; m.angle_limit = math.radians(angulo)
    try: m.harden_normals = True
    except Exception: pass
    return m


def _grosor(o, g, offset=0.0):
    s = o.modifiers.new("Grosor", "SOLIDIFY"); s.thickness = g; s.offset = offset; s.use_even_offset = True; s.use_quality_normals = True
    return s


def _aplicar(o):
    bpy.context.view_layer.objects.active = o
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    o.select_set(True)
    for m in list(o.modifiers):
        try: bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception as e: print("NO APLICA", o.name, m.name, e); o.modifiers.remove(m)


def partir(o, mat_corte, col):
    """Corta el objeto por y = 0: devuelve (detrás = y>0, delante = y<0). Las caras de corte llevan el material de corte."""
    big = 2.0
    delante = o.copy(); delante.data = o.data.copy(); col.objects.link(delante); delante.name = o.name + "_Delante"
    for ob, op in ((o, 'DIFFERENCE'), (delante, 'INTERSECT')):
        c = _malla("TUR_Cortador", lambda bm: caja(bm, -big, big, -big, 0.0, -big, big), col, liso=False)
        c.data.materials.append(mat_corte); c.matrix_world = Matrix.Identity(4)
        b = ob.modifiers.new("Corte", 'BOOLEAN'); b.operation = op; b.object = c; b.solver = 'EXACT'
        try: b.material_mode = 'TRANSFER'
        except Exception: pass
        try: b.use_self = True
        except Exception: pass
        _aplicar(ob); bpy.data.objects.remove(c, do_unlink=True)
    o.name = o.name + "_Detras"
    return o, delante


# ------------------------------------------------------------------------------------------------ materiales
def _mat(nombre, color, metal=0.0, rugo=0.4, coat=0.0, ruido=0.0, escala=900.0, emis=None, fuerza=0.0, aniso=0.0, rug_var=0.12):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rugo
    if coat: b.inputs["Coat Weight"].default_value = coat
    if aniso: b.inputs["Anisotropic"].default_value = aniso
    if emis: b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = fuerza
    if ruido:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = escala; nz.inputs["Detail"].default_value = 10.0; nz.inputs["Roughness"].default_value = 0.62
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = ruido; bp.inputs["Distance"].default_value = 0.0003
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = max(0.02, rugo - rug_var); mr.inputs["To Max"].default_value = min(1.0, rugo + rug_var)
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    return m


def _mat_calor(nombre, color, rugo=0.62):
    """Fundición de la turbina: con el valor 'Calor' (0..1) pasa de gris oscuro a rojo cereza y naranja (cuerpo negro)."""
    m = _mat(nombre, color, metal=0.9, rugo=rugo, ruido=0.55, escala=1100)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    val = nt.nodes.new("ShaderNodeValue"); val.name = "Calor"; val.outputs[0].default_value = 0.0
    tmp = nt.nodes.new("ShaderNodeMapRange"); tmp.inputs["To Min"].default_value = 700.0; tmp.inputs["To Max"].default_value = 1250.0
    nt.links.new(val.outputs[0], tmp.inputs["Value"])
    bb = nt.nodes.new("ShaderNodeBlackbody"); nt.links.new(tmp.outputs["Result"], bb.inputs["Temperature"])
    st = nt.nodes.new("ShaderNodeMath"); st.operation = 'POWER'; st.inputs[1].default_value = 2.2; nt.links.new(val.outputs[0], st.inputs[0])
    st2 = nt.nodes.new("ShaderNodeMath"); st2.operation = 'MULTIPLY'; st2.inputs[1].default_value = 7.0; nt.links.new(st.outputs[0], st2.inputs[0])
    nt.links.new(bb.outputs["Color"], b.inputs["Emission Color"]); nt.links.new(st2.outputs[0], b.inputs["Emission Strength"])
    return m


def materiales():
    M = {}
    M["alu_fundido"] = _mat("TUR_AluminioFundido", (0.56, 0.57, 0.59), metal=1.0, rugo=0.48, ruido=0.55, escala=1500)
    M["alu_rueda"] = _mat("TUR_RuedaCompresor", (0.90, 0.91, 0.92), metal=1.0, rugo=0.13, ruido=0.05, escala=3200, aniso=0.45, rug_var=0.04)
    M["hierro"] = _mat("TUR_CarcasaCentral", (0.26, 0.26, 0.27), metal=1.0, rugo=0.58, ruido=0.6, escala=1200)
    M["turbina_fund"] = _mat_calor("TUR_CarcasaTurbina", (0.17, 0.16, 0.155))
    M["inconel"] = _mat("TUR_RuedaTurbina", (0.42, 0.41, 0.40), metal=1.0, rugo=0.32, ruido=0.25, escala=2600)
    M["acero"] = _mat("TUR_AceroEje", (0.80, 0.80, 0.82), metal=1.0, rugo=0.12, aniso=0.6, ruido=0.03, escala=4000, rug_var=0.03)
    M["bronce"] = _mat("TUR_Bronce", (0.80, 0.52, 0.28), metal=1.0, rugo=0.28, ruido=0.08, escala=3000)
    M["tornillo"] = _mat("TUR_Tornilleria", (0.62, 0.63, 0.66), metal=1.0, rugo=0.30, ruido=0.05, escala=3500)
    M["chapa"] = _mat("TUR_EscudoTermico", (0.55, 0.50, 0.45), metal=1.0, rugo=0.36, ruido=0.2, escala=2000)
    M["actuador"] = _mat("TUR_Actuador", (0.025, 0.026, 0.03), metal=0.6, rugo=0.38, coat=0.3, ruido=0.08, escala=1600)
    M["goma"] = _mat("TUR_Manguito", (0.02, 0.02, 0.022), rugo=0.75, ruido=0.25, escala=900)
    M["corte"] = _mat("TUR_Corte", (0.74, 0.75, 0.77), metal=1.0, rugo=0.36, aniso=0.5, ruido=0.06, escala=4000)
    M["aire"] = _mat("TUR_Aire", (0.3, 0.65, 1.0), emis=(0.25, 0.62, 1.0), fuerza=5.0)
    M["escape"] = _mat("TUR_GasEscape", (0.6, 0.4, 0.3), emis=(1.0, 0.42, 0.10), fuerza=6.0)
    M["aceite"] = _mat("TUR_Aceite", (0.95, 0.60, 0.15), rugo=0.08, coat=1.0, emis=(1.0, 0.55, 0.12), fuerza=0.6)
    return M


# ------------------------------------------------------------------------------------------------ ruedas con álabes
def _alabe(bm, hub, shroud, theta, ns=28, nt=7):
    """Superficie de un álabe: hub(s), shroud(s) -> (x, r); theta(s, t) -> ángulo. Devuelve la rejilla de vértices."""
    filas = []
    for i in range(ns + 1):
        s = i / ns; (xh, rh), (xs, rs) = hub(s), shroud(s); fila = []
        for j in range(nt + 1):
            t = j / nt; x = xh + (xs - xh) * t; r = rh + (rs - rh) * t; a = theta(s, t)
            fila.append(bm.verts.new((x, r * math.cos(a), r * math.sin(a))))
        filas.append(fila)
    for i in range(ns):
        for j in range(nt): bm.faces.new((filas[i][j], filas[i + 1][j], filas[i + 1][j + 1], filas[i][j + 1]))


def rueda_compresor(nombre, M, col):
    xb, xf = 0.0315, 0.0560                       # espalda (exductor) y morro (inductor)
    def hub(s):  return (xb + (xf - xb) * (1 - math.sin(math.pi * s / 2)), 0.0062 + (COMP_EXD - 0.0012 - 0.0062) * (1 - math.cos(math.pi * s / 2)))
    def shr(s):  return (xb + 0.0042 + (xf - xb - 0.0042) * (1 - math.sin(math.pi * s / 2)), COMP_IND + (COMP_EXD - COMP_IND) * (1 - math.cos(math.pi * s / 2)))
    def hacer(bm):
        # cubo: perfil de revolución (morro, curva del cubo y disco trasero)
        prof = [(xf + 0.0035, 0.0)]
        for i in range(0, 25):
            s = i / 24; x, r = hub(s); prof.append((x, r))
        prof += [(xb - 0.0002, COMP_EXD - 0.0012), (xb - 0.0030, COMP_EXD - 0.0030), (xb - 0.0036, 0.0080), (xb - 0.0036, 0.0)]
        prof[0] = (xf + 0.0035, 0.0); prof.insert(1, (xf + 0.0030, 0.0045))
        torno_x(bm, prof, seg=128)
    cubo = _malla(nombre + "_Cubo", hacer, col); cubo.data.materials.append(M["alu_rueda"]); _bisel(cubo, 0.0004, 2)
    def alabes(bm):
        for k in range(12):
            a0 = TAU * k / 12; entero = (k % 2 == 0)
            s0 = 0.0 if entero else 0.38
            def h2(s, s0=s0): return hub(s0 + (1 - s0) * s)
            def r2(s, s0=s0): return shr(s0 + (1 - s0) * s)
            def th(s, t, s0=s0, a0=a0):
                ss = s0 + (1 - s0) * s
                return a0 + 0.95 * (1 - ss) ** 2.2 * (0.55 + 0.45 * t) - 0.42 * ss ** 2      # giro a la entrada y álabe hacia atrás a la salida
            _alabe(bm, h2, r2, th, ns=30, nt=8)
    al = _malla(nombre + "_Alabes", alabes, col); al.data.materials.append(M["alu_rueda"])
    _grosor(al, 0.00075, 0.0); _bisel(al, 0.00018, 2, 50)
    return cubo, al


def rueda_turbina(nombre, M, col):
    xb, xo = -0.0460, -0.0650                     # espalda (entrada radial) y salida axial
    def hub(s):  return (xb + (xo - xb) * (1 - math.cos(math.pi * s / 2)), (TURB_IN - 0.0012) + (0.0072 - (TURB_IN - 0.0012)) * math.sin(math.pi * s / 2))
    def shr(s):  return (xb - 0.0062 + (xo - 0.0004 - (xb - 0.0062)) * (1 - math.cos(math.pi * s / 2)), TURB_IN + (TURB_OUT - TURB_IN) * math.sin(math.pi * s / 2))
    def hacer(bm):
        prof = [(xb + 0.0030, 0.0), (xb + 0.0030, 0.0060), (xb + 0.0012, TURB_IN - 0.0030), (xb, TURB_IN - 0.0012)]
        for i in range(1, 25):
            s = i / 24; x, r = hub(s); prof.append((x, r))
        prof += [(xo - 0.0040, 0.0050), (xo - 0.0046, 0.0)]
        torno_x(bm, prof, seg=128)
    cubo = _malla(nombre + "_Cubo", hacer, col); cubo.data.materials.append(M["inconel"]); _bisel(cubo, 0.0004, 2)
    def alabes(bm):
        for k in range(11):
            a0 = TAU * k / 11
            def th(s, t, a0=a0): return a0 - 0.75 * max(0.0, s - 0.35) ** 2.0 * (0.4 + 0.6 * t) / 0.42   # entrada radial recta, "cuchara" a la salida
            _alabe(bm, hub, shr, th, ns=30, nt=8)
    al = _malla(nombre + "_Alabes", alabes, col); al.data.materials.append(M["inconel"])
    _grosor(al, 0.0011, 0.0); _bisel(al, 0.0002, 2, 50)
    return cubo, al


# ------------------------------------------------------------------------------------------------ caracolas (volutas)
def caracola(bm, xv, r_in, rt0, rt1, giro0, vuelta=0.93, largo_salida=0.045, sentido=1, seg_c=40, n=120):
    """Tubo en espiral alrededor del eje X en el plano x = xv; sección que crece de rt0 a rt1 y sale recto por la tangente."""
    ejes = []
    tot = n + 12
    for i in range(tot + 1):
        if i <= n:
            u = i / n; phi = giro0 + sentido * TAU * vuelta * u; rt = rt0 + (rt1 - rt0) * u ** 0.85
            rc = r_in + rt
            c = Vector((xv, rc * math.cos(phi), rc * math.sin(phi))); rd = Vector((0, math.cos(phi), math.sin(phi)))
            ejes.append((c, rd, rt))
        else:
            c_end, rd_end, rt_end = ejes[n]
            phi_e = giro0 + sentido * TAU * vuelta
            tg = Vector((0, -math.sin(phi_e), math.cos(phi_e))) * sentido
            d = largo_salida * (i - n) / 12
            ejes.append((c_end + tg * d, rd_end, rt1))
    anillos = []
    for c, rd, rt in ejes:
        x_ = Vector((1, 0, 0))
        anillos.append([bm.verts.new(c + rt * (math.cos(TAU * j / seg_c) * rd + math.sin(TAU * j / seg_c) * x_)) for j in range(seg_c)])
    for ra, rb in zip(anillos, anillos[1:]):
        for j in range(seg_c): bm.faces.new((ra[j], ra[(j + 1) % seg_c], rb[(j + 1) % seg_c], rb[j]))
    cen = bm.verts.new(ejes[0][0])                 # la lengüeta (inicio) va cerrada
    for j in range(seg_c): bm.faces.new((anillos[0][(j + 1) % seg_c], anillos[0][j], cen))
    return ejes


# ------------------------------------------------------------------------------------------------ construcción
def construir_turbo(col):
    M = materiales(); O = {"M": M, "detras": [], "delante": [], "enteras": []}
    raiz = bpy.data.objects.new("TUR_Raiz", None); col.objects.link(raiz); raiz.empty_display_size = 0.08; O["raiz"] = raiz
    def P(o, padre=None): o.parent = padre or raiz; return o

    # ---- rotor: eje + rueda de la turbina + rueda del compresor + tuerca + collar axial (todo gira junto)
    rotor = bpy.data.objects.new("TUR_Rotor", None); col.objects.link(rotor); rotor.parent = raiz; O["rotor"] = rotor
    eje = _malla("TUR_Eje", lambda bm: torno_x(bm, [(-0.0475, 0.0), (-0.0475, 0.0040), (0.0175, 0.0040), (0.0180, 0.0036),
                                                         (0.0560, 0.0030), (0.0628, 0.0028), (0.0634, 0.0), ], seg=64), col)
    eje.data.materials.append(M["acero"]); P(eje, rotor); _bisel(eje, 0.0002, 2)
    cc, ca = rueda_compresor("TUR_RuedaCompresor", M, col); P(cc, rotor); P(ca, rotor)
    tc, ta = rueda_turbina("TUR_RuedaTurbina", M, col); P(tc, rotor); P(ta, rotor)
    tu = _malla("TUR_TuercaRueda", lambda bm: torno_x(bm, [(0.0592, 0.0), (0.0592, 0.0046), (0.0628, 0.0046), (0.0628, 0.0)], seg=6), col, liso=False)
    tu.data.materials.append(M["tornillo"]); P(tu, rotor); _bisel(tu, 0.0003, 2)
    co = _malla("TUR_CollarAxial", lambda bm: torno_x(bm, [(0.0192, 0.0040), (0.0192, 0.0085), (0.0222, 0.0085), (0.0222, 0.0040)], seg=64, cerrar=True), col)
    co.data.materials.append(M["acero"]); P(co, rotor); _bisel(co, 0.0002, 2)
    O["rueda_comp"] = (cc, ca); O["rueda_turb"] = (tc, ta); O["eje"] = eje

    # ---- piezas fijas que no se cortan: casquillos, cojinete axial, escudo térmico
    for k, xc in enumerate((-0.0215, 0.0045)):
        b_ = _malla(f"TUR_Casquillo{k}", lambda bm, xc=xc: torno_x(bm, [(xc - 0.005, 0.00405), (xc - 0.005, 0.0056), (xc + 0.005, 0.0056), (xc + 0.005, 0.00405)], seg=64, cerrar=True), col)
        b_.data.materials.append(M["bronce"]); P(b_); _bisel(b_, 0.0002, 2); O["enteras"].append(b_)
    ax = _malla("TUR_CojineteAxial", lambda bm: torno_x(bm, [(0.0164, 0.0045), (0.0164, 0.0125), (0.0190, 0.0125), (0.0190, 0.0045)], seg=64, cerrar=True), col)
    ax.data.materials.append(M["bronce"]); P(ax); _bisel(ax, 0.0002, 2); O["enteras"].append(ax)
    es = _malla("TUR_EscudoTermico", lambda bm: torno_x(bm, [(-0.0425, 0.0062), (-0.0432, 0.0200), (-0.0440, 0.0330)], seg=96), col)
    es.data.materials.append(M["chapa"]); _grosor(es, 0.0007); P(es)

    # ---- carcasa central (fundición): cuerpo de revolución con bridas, alojamiento de casquillos, entrada y retorno de aceite
    def chra(bm):
        torno_x(bm, [(-0.0420, 0.0058), (-0.0420, 0.0310), (-0.0360, 0.0310), (-0.0335, 0.0250), (0.0110, 0.0250),
                     (0.0140, 0.0310), (0.0225, 0.0310), (0.0225, 0.0135), (0.0160, 0.0135), (0.0160, 0.0058)], seg=128, cerrar=True)
    ch = _malla("TUR_CarcasaCentral", chra, col); ch.data.materials.append(M["hierro"]); P(ch); _bisel(ch, 0.0008, 3)
    def boss(bm):
        cilindro(bm, (-0.0080, 0, 0.0300), (0, 0, 1), 0.0085, 0.020, seg=64)
        caja(bm, -0.0200, 0.0040, -0.0080, 0.0080, 0.0390, 0.0440)
    bo = _malla("TUR_EntradaAceite", boss, col); bo.data.materials.append(M["hierro"]); P(bo); _bisel(bo, 0.0007, 3)
    def retorno(bm):
        cilindro(bm, (-0.0080, 0, -0.0300), (0, 0, 1), 0.0110, 0.020, seg=64)
        caja(bm, -0.0270, 0.0110, -0.0130, 0.0130, -0.0440, -0.0390)
    rt_ = _malla("TUR_RetornoAceite", retorno, col); rt_.data.materials.append(M["hierro"]); P(rt_); _bisel(rt_, 0.0007, 3)
    piezas_corte = [ch, bo, rt_]
    for k, xx in enumerate((-0.0160, 0.0000)):        # tornillos de la brida de aceite
        t_ = _malla(f"TUR_TornAceite{k}", lambda bm, xx=xx: cilindro(bm, (xx, 0, 0.0455), (0, 0, 1), 0.0028, 0.0030, seg=6), col, liso=False)
        t_.data.materials.append(M["tornillo"]); P(t_); _bisel(t_, 0.0003, 2); O["enteras"].append(t_)

    # ---- carcasa del compresor (aluminio fundido): boca de entrada, envolvente de la rueda, difusor, caracola y salida
    def envol_c(bm):
        prof = [(0.0880, 0.0245), (0.0880, 0.0215), (0.0620, 0.0200)]
        for i in range(0, 21):
            s = i / 20
            xs = 0.0315 + 0.0042 + (0.0560 - 0.0315 - 0.0042) * (1 - math.sin(math.pi * s / 2)) + 0.0006
            rs = COMP_IND + (COMP_EXD - COMP_IND) * (1 - math.cos(math.pi * s / 2)) + 0.0006
            prof.append((xs, rs))
        prof += [(0.0362, 0.0330)]
        torno_x(bm, prof, seg=128)
    ec = _malla("TUR_CarcasaCompresor", envol_c, col); ec.data.materials.append(M["alu_fundido"]); _grosor(ec, 0.0035, 0.0); P(ec)
    vc = _malla("TUR_CaracolaCompresor", lambda bm: caracola(bm, 0.0345, 0.0330, 0.0045, 0.0165, math.radians(95), 0.93, 0.050, 1), col)
    vc.data.materials.append(M["alu_fundido"]); _grosor(vc, 0.0030, 0.0); P(vc)
    bc = _malla("TUR_ContraplacaCompresor", lambda bm: torno_x(bm, [(0.0225, 0.0050), (0.0225, 0.0340), (0.0312, 0.0340), (0.0312, 0.0262), (0.0272, 0.0262), (0.0272, 0.0050)], seg=128, cerrar=True), col)
    bc.data.materials.append(M["alu_fundido"]); P(bc); _bisel(bc, 0.0006, 2)
    piezas_corte += [ec, vc, bc]
    lab = _malla("TUR_LabioEntrada", lambda bm: torno_x(bm, [(0.0860, 0.0245), (0.0860, 0.0262), (0.0890, 0.0262), (0.0890, 0.0245)], seg=128, cerrar=True), col)
    lab.data.materials.append(M["alu_fundido"]); P(lab); _bisel(lab, 0.0006, 3); piezas_corte.append(lab)

    # ---- carcasa de la turbina (fundición resistente al calor): envolvente, salida axial, caracola, brida de entrada y de salida
    def envol_t(bm):
        prof = [(-0.0440, 0.0310), (-0.0515, 0.0236)]
        for i in range(1, 21):
            s = i / 20
            xs = -0.0460 - 0.0062 + (-0.0650 - 0.0004 - (-0.0460 - 0.0062)) * (1 - math.cos(math.pi * s / 2)) - 0.0004
            rs = TURB_IN + (TURB_OUT - TURB_IN) * math.sin(math.pi * s / 2) + 0.0006
            prof.append((xs, rs))
        prof += [(-0.0800, 0.0225), (-0.0960, 0.0250)]
        torno_x(bm, prof, seg=128)
    et = _malla("TUR_CarcasaTurbina", envol_t, col); et.data.materials.append(M["turbina_fund"]); _grosor(et, 0.0045, 0.0); P(et)
    vt = _malla("TUR_CaracolaTurbina", lambda bm: caracola(bm, -0.0540, 0.0310, 0.0050, 0.0165, math.radians(-85), 0.93, 0.040, -1), col)
    vt.data.materials.append(M["turbina_fund"]); _grosor(vt, 0.0042, 0.0); P(vt)
    fs = _malla("TUR_BridaSalida", lambda bm: torno_x(bm, [(-0.1040, 0.0250), (-0.1040, 0.0430), (-0.0960, 0.0430), (-0.0960, 0.0250)], seg=128, cerrar=True), col)
    fs.data.materials.append(M["turbina_fund"]); P(fs); _bisel(fs, 0.0008, 3)
    piezas_corte += [et, vt, fs]
    # brida de entrada de escape al final de la salida recta de la caracola
    ce, rde, _ = (lambda e: e[-1])(caracola(bmesh.new(), -0.0540, 0.0310, 0.0050, 0.0165, math.radians(-85), 0.93, 0.040, -1))
    phi_e = math.radians(-85) - TAU * 0.93; tg = Vector((0, -math.sin(phi_e), math.cos(phi_e))) * -1
    def brida_in(bm):
        g = bmesh.ops.create_cube(bm, size=1.0)
        q = tg.to_track_quat('Z', 'X').to_matrix().to_4x4()
        bmesh.ops.scale(bm, vec=(0.060, 0.052, 0.008), verts=g["verts"])
        bmesh.ops.transform(bm, matrix=Matrix.Translation(ce) @ q, verts=g["verts"])
    fi = _malla("TUR_BridaEntrada", brida_in, col, liso=False); fi.data.materials.append(M["turbina_fund"]); P(fi); _bisel(fi, 0.0012, 3)
    _aplicar(fi)
    hueco = _malla("TUR_HuecoBrida", lambda bm: cilindro(bm, ce, tg, 0.0160, 0.030, seg=64), col)
    b_ = fi.modifiers.new("Hueco", 'BOOLEAN'); b_.operation = 'DIFFERENCE'; b_.object = hueco; b_.solver = 'EXACT'
    _aplicar(fi); bpy.data.objects.remove(hueco, do_unlink=True)
    for k in range(4):                                  # espárragos de la brida de entrada
        qq = tg.to_track_quat('Z', 'X').to_matrix()
        off = qq @ Vector(((-1 if k % 2 else 1) * 0.022, (-1 if k // 2 else 1) * 0.018, 0.0))
        e2 = _malla(f"TUR_EsparragoEntrada{k}", lambda bm, off=off: (cilindro(bm, ce + off + tg * 0.007, tg, 0.0022, 0.012, seg=24),
                                                                       cilindro(bm, ce + off + tg * 0.0055, tg, 0.0042, 0.0035, seg=6)), col, liso=False)
        e2.data.materials.append(M["tornillo"]); P(e2); _bisel(e2, 0.0003, 2); O["enteras"].append(e2)
    piezas_corte.append(fi)
    # espárragos y tuercas de la brida de salida (5)
    for k in range(5):
        a = TAU * k / 5 + 0.3; y, z = 0.0365 * math.cos(a), 0.0365 * math.sin(a)
        e_ = _malla(f"TUR_Esparrago{k}", lambda bm, y=y, z=z: (cilindro(bm, (-0.1075, y, z), (1, 0, 0), 0.0022, 0.013, seg=24),
                                                             cilindro(bm, (-0.1060, y, z), (1, 0, 0), 0.0042, 0.0040, seg=6)), col, liso=False)
        e_.data.materials.append(M["tornillo"]); P(e_); _bisel(e_, 0.0003, 2); O["enteras"].append(e_)
    # ---- válvula de descarga (wastegate): tapa, palanca, varilla y actuador neumático sobre el compresor
    wg_piv = Vector((-0.0760, 0.0000, 0.0330))
    def palanca(bm):
        cilindro(bm, (-0.0760, 0.0, 0.0285), (0, 0, 1), 0.0048, 0.0110, seg=32)          # resalte del eje de la válvula
        cilindro(bm, wg_piv, (0, 1, 0), 0.0035, 0.016, seg=32)
        caja(bm, -0.0790, -0.0730, 0.0070, 0.0100, 0.0330, 0.0600)
    pl = _malla("TUR_PalancaWastegate", palanca, col, liso=False); pl.data.materials.append(M["tornillo"]); P(pl); _bisel(pl, 0.0005, 2)
    tapa = _malla("TUR_TapaWastegate", lambda bm: cilindro(bm, (-0.0880, 0.0, 0.0120), (1, 0, 0), 0.0090, 0.0025, seg=48), col)
    tapa.data.materials.append(M["inconel"]); P(tapa); _bisel(tapa, 0.0003, 2)
    act_c = Vector((0.0300, 0.0085, 0.1000))
    def actuador(bm):
        cilindro(bm, act_c, (1, 0, 0), 0.0280, 0.030, seg=96)
        cilindro(bm, act_c, (1, 0, 0), 0.0300, 0.0040, seg=96)                                # pestaña engatillada del diafragma
        cilindro(bm, act_c + Vector((0.0190, 0, 0)), (1, 0, 0), 0.0040, 0.0120, seg=32)       # toma de presión
    ac = _malla("TUR_Actuador", actuador, col); ac.data.materials.append(M["actuador"]); P(ac); _bisel(ac, 0.0008, 3)
    so = _malla("TUR_SoporteActuador", lambda bm: caja(bm, 0.0180, 0.0420, 0.0055, 0.0115, 0.0600, 0.0760), col, liso=False)
    so.data.materials.append(M["tornillo"]); P(so); _bisel(so, 0.0005, 2)
    A_, B_ = Vector((act_c.x - 0.0150, 0.0085, act_c.z)), Vector((-0.0760, 0.0085, 0.0580))
    va = _malla("TUR_Varilla", lambda bm: cilindro(bm, (A_ + B_) / 2, B_ - A_, 0.0020, (B_ - A_).length, seg=24), col)
    va.data.materials.append(M["acero"]); P(va)
    O["wastegate"] = (pl, tapa, ac, va, so)
    for o_ in (pl, tapa, ac, va, so): O["enteras"].append(o_)
    mg = _malla("TUR_ManguitoPresion", lambda bm: cilindro(bm, (0.0660, 0.0085, 0.1000), (1, 0, 0), 0.0042, 0.0300, seg=32), col)
    mg.data.materials.append(M["goma"]); P(mg); O["enteras"].append(mg)

    # ---- aceite en los conductos (se ve en el corte)
    def aceite(bm):
        cilindro(bm, (-0.0080, 0, 0.0255), (0, 0, 1), 0.0022, 0.0380, seg=24)
        cilindro(bm, (-0.0080, 0, -0.0225), (0, 0, 1), 0.0060, 0.0300, seg=32)
    oil = _malla("TUR_AceiteConductos", aceite, col); oil.data.materials.append(M["aceite"]); P(oil); O["aceite"] = oil

    # ---- corte seccional de las carcasas (el aceite se corta igual y queda un pelo delante de la cara de corte)
    bpy.context.view_layer.update()
    oil_d, oil_f = partir(oil, M["aceite"], col); oil_d.location.y -= 0.0003; bpy.data.objects.remove(oil_f, do_unlink=True); O["aceite"] = oil_d
    for o_ in piezas_corte:
        det, dl = partir(o_, M["corte"], col)
        dl.parent = raiz; O["detras"].append(det); O["delante"].append(dl)
    es_det, es_del = partir(es, M["corte"], col); es_del.parent = raiz; O["detras"].append(es_det); O["delante"].append(es_del)

    # ---- anclas para rótulos (en el espacio de la raíz)
    O["anclas"] = {}
    for nm, loc in (("RUEDA_COMPRESOR", (0.046, -0.010, 0.012)), ("RUEDA_TURBINA", (-0.056, -0.010, 0.012)), ("EJE", (-0.010, -0.004, 0.0)),
                    ("COJINETES", (0.0045, -0.006, 0.0)), ("ACEITE", (-0.008, 0.0, 0.045)), ("CARCASA_CENTRAL", (-0.010, -0.025, -0.012)),
                    ("CARCASA_COMPRESOR", (0.036, -0.050, 0.030)), ("CARCASA_TURBINA", (-0.050, -0.050, 0.030)), ("WASTEGATE", (-0.076, 0.0, 0.050)),
                    ("ACTUADOR", (0.030, -0.020, 0.100)), ("ENTRADA_AIRE", (0.090, 0.0, 0.0)), ("SALIDA_AIRE", (0.033, -0.10, 0.03)),
                    ("ENTRADA_ESCAPE", (-0.050, 0.09, -0.02)), ("SALIDA_ESCAPE", (-0.104, 0.0, 0.0))):
        e = bpy.data.objects.new("ANC_" + nm, None); col.objects.link(e); e.parent = raiz; e.location = loc; e.empty_display_size = 0.006
        O["anclas"][nm] = e
    return O


def girar_rotor(O, f, angulo_grados):
    """Clave de giro del rotor (eje X local)."""
    r = O["rotor"]; r.rotation_mode = 'XYZ'; r.rotation_euler = (math.radians(angulo_grados), 0, 0); r.keyframe_insert("rotation_euler", frame=f, index=0)


def calor(O, f, valor):
    """0 = frío, 1 = al rojo. Pone clave en el material de la carcasa de la turbina."""
    n = O["M"]["turbina_fund"].node_tree.nodes["Calor"]; n.outputs[0].default_value = valor; n.outputs[0].keyframe_insert("default_value", frame=f)
