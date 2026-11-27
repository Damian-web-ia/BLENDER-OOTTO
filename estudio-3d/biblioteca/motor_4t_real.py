# MOTOR DE 4 TIEMPOS EN CORTE (monocilíndrico de gasolina) · EKORUEDAS · 27-11-2026 · skill "Automotive CGI 4K"
# Medidas reales de un cilindro típico de turismo: diámetro 82 mm, carrera 86 mm, biela de 140 mm entre centros.
# Ejes: el cigüeñal gira alrededor de Y (la cámara mira a lo largo del cigüeñal y ve el corte), el cilindro sube por Z.
# θ = ángulo del cigüeñal (0 = punto muerto superior). Un ciclo = 720°: admisión 0-180, compresión 180-360,
# explosión 360-540, escape 540-720. El árbol de levas gira a la mitad (θ/2).
# Uso: MP = {...materiales_pro...}; exec(open(".../motor_4t_real.py").read(), G)
#      O = construir_motor(col, MP, BUJ)   (BUJ = diccionario con construir_bujia de bujia_real.py)
#      poner_angulo(O, theta_grados, f)  → pone pistón, biela, cigüeñal, levas y válvulas en el fotograma f (con clave)
import bpy, bmesh, math
from mathutils import Vector, Matrix

R_CIG = 0.043          # radio de la muñequilla (carrera / 2)
L_BIE = 0.140          # biela entre centros
BORE = 0.082
CUBIERTA = 0.214       # cara de arriba del bloque (junta de culata)
COMP_H = 0.030         # del bulón a la cabeza del pistón
LIFT = 0.0090          # alzada máxima de válvula
ANG_V = 20.0           # inclinación de las válvulas
ADM_X, ESC_X = -0.019, 0.019


def _obj(nombre, bm, mats, col, padre=None, liso=True, angulo=40):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = liso
    o = bpy.data.objects.new(nombre, me); col.objects.link(o)
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]): me.materials.append(m)
    if padre is not None: o.parent = padre
    if liso:
        try:
            md = o.modifiers.new("Suave", 'SMOOTH_BY_ANGLE'); md["Input_1"] = math.radians(angulo)
        except Exception:
            try: me.set_sharp_from_angle(angle=math.radians(angulo))
            except Exception: pass
    return o


def _bisel(o, ancho=0.0012, seg=2):
    b = o.modifiers.new("Bisel", 'BEVEL'); b.width = ancho; b.segments = seg; b.limit_method = 'ANGLE'
    b.angle_limit = math.radians(35); b.harden_normals = False
    return b


def torno(bm, perfil, seg=72):
    """Gira un perfil (r, z) alrededor de Z."""
    anillos = []
    for k in range(seg):
        a = 2 * math.pi * k / seg; c, s = math.cos(a), math.sin(a)
        anillos.append([bm.verts.new((r * c, r * s, z)) for r, z in perfil])
    n = len(perfil)
    for k in range(seg):
        A, B = anillos[k], anillos[(k + 1) % seg]
        for i in range(n - 1):
            vs = [A[i], B[i], B[i + 1], A[i + 1]]
            bm.faces.new(vs)
        bm.faces.new([A[n - 1], B[n - 1], B[0], A[0]])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def _girar(bm, eje_rot, grados, centro=(0, 0, 0)):
    bmesh.ops.rotate(bm, verts=bm.verts, cent=centro, matrix=Matrix.Rotation(math.radians(grados), 3, eje_rot))


def anillo_y(bm, rin, rout, t, seg=72, y0=0.0):
    """Anillo (o disco si rin=0) con eje Y, de grosor t, centrado en y0."""
    if rin > 0: perfil = [(rin, -t / 2), (rout, -t / 2), (rout, t / 2), (rin, t / 2)]
    else: perfil = [(0, -t / 2), (rout, -t / 2), (rout, t / 2), (0, t / 2)]
    b2 = bmesh.new(); torno(b2, perfil, seg); _girar(b2, 'X', 90)
    bmesh.ops.translate(b2, verts=b2.verts, vec=(0, y0, 0))
    me = bpy.data.meshes.new("tmp"); b2.to_mesh(me); b2.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)


def poligono_y(bm, pts_xz, t, y0=0.0):
    """Polígono en el plano XZ extruido a lo largo de Y (grosor t centrado en y0)."""
    b2 = bmesh.new()
    vs = [b2.verts.new((x, y0 - t / 2, z)) for x, z in pts_xz]
    f = b2.faces.new(vs)
    r = bmesh.ops.extrude_face_region(b2, geom=[f])
    nv = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(b2, verts=nv, vec=(0, t, 0))
    bmesh.ops.recalc_face_normals(b2, faces=b2.faces)
    me = bpy.data.meshes.new("tmp"); b2.to_mesh(me); b2.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)


def caja(bm, x0, x1, y0, y1, z0, z1):
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]:
        v.co = Vector(((x0 if v.co.x < 0 else x1), (y0 if v.co.y < 0 else y1), (z0 if v.co.z < 0 else z1)))


def cil_z(bm, r, z0, z1, seg=72, x=0.0, y=0.0):
    b2 = bmesh.new(); torno(b2, [(0, z0), (r, z0), (r, z1), (0, z1)], seg)
    bmesh.ops.translate(b2, verts=b2.verts, vec=(x, y, 0))
    me = bpy.data.meshes.new("tmp"); b2.to_mesh(me); b2.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)


def _malla(nombre, fn, col):
    bm = bmesh.new(); fn(bm); me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me); col.objects.link(o); return o


def _aplicar(o):
    """Aplica los modificadores (booleanas) sin operadores: malla nueva desde el objeto evaluado."""
    dg = bpy.context.evaluated_depsgraph_get(); oe = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(oe, preserve_all_data_layers=True, depsgraph=dg)
    viejo = o.data; o.modifiers.clear(); o.data = me
    if viejo.users == 0: bpy.data.meshes.remove(viejo)
    return o


def restar(o, cortadores, union=False):
    for c in cortadores:
        b = o.modifiers.new("B", 'BOOLEAN'); b.operation = 'UNION' if union else 'DIFFERENCE'; b.object = c; b.solver = 'EXACT'
        try: b.material_mode = 'TRANSFER'
        except Exception: pass
    _aplicar(o)
    for c in cortadores:
        if c.name in bpy.data.objects: bpy.data.objects.remove(c, do_unlink=True)
    return o


def tubo_curva(nombre, puntos, r, col):
    cu = bpy.data.curves.new(nombre, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 6
    cu.use_fill_caps = True; cu.resolution_u = 16
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(puntos) - 1)
    for p, co in zip(sp.bezier_points, puntos):
        p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(nombre, cu); col.objects.link(o)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), depsgraph=dg)
    bpy.data.objects.remove(o, do_unlink=True); bpy.data.curves.remove(cu)
    m = bpy.data.objects.new(nombre, me); col.objects.link(m); return m


def partir(o, mat_corte, col):
    """Corta el objeto por y=0: devuelve (detrás, delante). Las caras de corte llevan el material de corte."""
    big = 2.0
    def cubo(nm):
        c = _malla(nm, lambda bm: caja(bm, -big, big, -big, 0.0, -big, big), col); c.data.materials.append(mat_corte); return c
    delante = o.copy(); delante.data = o.data.copy(); col.objects.link(delante); delante.name = o.name + "_Delante"
    for ob, op in ((o, 'DIFFERENCE'), (delante, 'INTERSECT')):
        c = cubo("Cortador"); c.matrix_world = Matrix.Identity(4)
        b = ob.modifiers.new("Corte", 'BOOLEAN'); b.operation = op; b.object = c; b.solver = 'EXACT'
        try: b.material_mode = 'TRANSFER'
        except Exception: pass
        _aplicar(ob); bpy.data.objects.remove(c, do_unlink=True)
    o.name = o.name + "_Detras" if not o.name.endswith("_Detras") else o.name
    return o, delante


# ------------------------------------------------------------------------------------------------ MATERIALES
def _mat(nombre, color, metal=0.0, rugo=0.4, coat=0.0, ruido=0.0, escala_ruido=900.0, emis=None, fuerza=0.0, aniso=0.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rugo
    if coat: b.inputs["Coat Weight"].default_value = coat
    if aniso: b.inputs["Anisotropic"].default_value = aniso
    if emis: b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = fuerza
    if ruido:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = escala_ruido; nz.inputs["Detail"].default_value = 8.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        mp = nt.nodes.new("ShaderNodeMapRange"); mp.inputs["To Min"].default_value = rugo * 0.8; mp.inputs["To Max"].default_value = rugo * 1.25
        nt.links.new(nz.outputs["Fac"], mp.inputs["Value"]); nt.links.new(mp.outputs["Result"], b.inputs["Roughness"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = ruido; bp.inputs["Distance"].default_value = 0.0004
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def materiales(MP):
    M = {}
    M["alu"] = _mat("MOT_AluminioFundido", (0.42, 0.43, 0.45), metal=1.0, rugo=0.52, ruido=0.45, escala_ruido=1400)
    M["alu_pulido"] = _mat("MOT_AluminioPiston", (0.86, 0.86, 0.87), metal=1.0, rugo=0.22, ruido=0.12, escala_ruido=2400, aniso=0.3)
    M["hierro"] = MP["fundicion"]("MOT_Camisa", color=(0.30, 0.30, 0.31))
    M["acero"] = MP["acero"]("MOT_AceroForjado", color=(0.56, 0.57, 0.59), rugo=(0.18, 0.30), anillos=False)
    M["muñon"] = MP["cromo"]("MOT_Munones", color=(0.90, 0.90, 0.91))
    M["segmento"] = _mat("MOT_Segmentos", (0.20, 0.20, 0.21), metal=1.0, rugo=0.28)
    M["valvula"] = _mat("MOT_Valvula", (0.62, 0.62, 0.63), metal=1.0, rugo=0.24, ruido=0.1, escala_ruido=3000)
    M["muelle"] = _mat("MOT_Muelle", (0.08, 0.30, 0.55), metal=0.6, rugo=0.32, coat=0.4)   # muelles pintados de azul
    M["leva"] = MP["cromo"]("MOT_Levas", color=(0.84, 0.84, 0.86))
    M["junta"] = _mat("MOT_Junta", (0.20, 0.21, 0.22), metal=1.0, rugo=0.5)
    # cara de corte: aluminio mecanizado satinado (sin tinte cobrizo), con un filo frío muy suave
    m = _mat("MOT_Corte", (0.70, 0.71, 0.73), metal=1.0, rugo=0.40, aniso=0.5, ruido=0.08, escala_ruido=4000)
    M["corte"] = m
    M["refrig"] = MP["aceite"]("MOT_Refrigerante", color=(0.15, 0.75, 0.60), calor=False)
    M["aceite"] = MP["aceite"]("MOT_Aceite", color=(0.95, 0.62, 0.18), calor=False)
    M["polea"] = _mat("MOT_Polea", (0.10, 0.10, 0.11), metal=1.0, rugo=0.35, ruido=0.2, escala_ruido=1600)
    # gas de la cámara: transparente + emisión con color y fuerza animados
    m = bpy.data.materials.new("MOT_Mezcla"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.2, 0.55, 1.0, 1); em.inputs["Strength"].default_value = 2.0
    mix.inputs[0].default_value = 0.0
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs["Surface"])
    M["mezcla"] = m; M["_mezcla_nodos"] = (mix, em)
    M["chispa"] = _mat("MOT_Chispa", (0.6, 0.85, 1.0), emis=(0.55, 0.8, 1.0), fuerza=60.0)
    M["gas_adm"] = _mat("MOT_GasAdmision", (0.3, 0.65, 1.0), emis=(0.25, 0.6, 1.0), fuerza=6.0)
    M["gas_esc"] = _mat("MOT_GasEscape", (0.6, 0.55, 0.5), emis=(1.0, 0.45, 0.12), fuerza=3.0)
    return M


# ------------------------------------------------------------------------------------------------ PIEZAS
def _perfil_valvula(r_cab, largo):
    return [(0.0, 0.0), (r_cab, 0.0), (r_cab, 0.0015), (r_cab * 0.80, 0.0035), (0.0055, 0.010), (0.0034, 0.016),
            (0.0034, largo - 0.004), (0.0028, largo - 0.003), (0.0028, largo), (0.0, largo)]


def eje_valvula(lado):
    s = -1 if lado == "adm" else 1
    a = math.radians(ANG_V)
    return Vector((s * math.sin(a), 0, math.cos(a)))


def construir_motor(col, MP, BUJ=None):
    M = materiales(MP); O = {"M": M}
    raiz = bpy.data.objects.new("MOTOR", None); col.objects.link(raiz); raiz.empty_display_size = 0.2; O["raiz"] = raiz
    def P(o): o.parent = raiz; return o

    # ---------------- cigüeñal (gira alrededor de Y)
    cig = bpy.data.objects.new("MOT_Cigueñal", None); col.objects.link(cig); P(cig); O["cig"] = cig
    bm = bmesh.new()
    anillo_y(bm, 0, 0.026, 0.055, y0=-0.058); anillo_y(bm, 0, 0.026, 0.055, y0=0.058)       # apoyos de bancada
    anillo_y(bm, 0, 0.0215, 0.032)                                                          # muñequilla...
    bmesh.ops.translate(bm, verts=[v for v in bm.verts if abs(v.co.y) < 0.0165 and Vector((v.co.x, v.co.z)).length < 0.022], vec=(0, 0, R_CIG))
    o = _obj("MOT_Munones", bm, [M["muñon"]], col, cig); _bisel(o, 0.0008)
    pts = [(0.026 * math.sin(math.radians(a)), R_CIG + 0.026 * math.cos(math.radians(a))) for a in range(90, -91, -10)]
    pts += [(0.068 * math.sin(math.radians(a)), 0.068 * math.cos(math.radians(a))) for a in range(245, 114, -8)]
    bm = bmesh.new(); poligono_y(bm, pts, 0.014, y0=-0.023); poligono_y(bm, pts, 0.014, y0=0.023)
    o = _obj("MOT_Contrapesos", bm, [M["acero"]], col, cig, liso=False); _bisel(o, 0.0018, 3)
    # polea delantera y volante trasero
    bm = bmesh.new(); anillo_y(bm, 0, 0.050, 0.012, y0=-0.093); anillo_y(bm, 0, 0.030, 0.010, y0=-0.083)
    O["polea"] = o = _obj("MOT_Polea", bm, [M["polea"]], col, cig); _bisel(o, 0.0008)
    bm = bmesh.new(); anillo_y(bm, 0.0, 0.115, 0.014, y0=0.100, seg=128); anillo_y(bm, 0.0, 0.035, 0.016, y0=0.087)
    O["volante"] = o = _obj("MOT_Volante", bm, [M["polea"]], col, cig); _bisel(o, 0.0015)
    bm = bmesh.new()
    for k in range(96):                                                                     # corona dentada
        a = 2 * math.pi * k / 96; c, s = math.cos(a), math.sin(a)
        b2 = bmesh.new(); caja(b2, -0.0022, 0.0022, -0.008, 0.008, 0.115, 0.121)
        bmesh.ops.rotate(b2, verts=b2.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, 'Y'))
        bmesh.ops.translate(b2, verts=b2.verts, vec=(0, 0.100, 0))
        me = bpy.data.meshes.new("t"); b2.to_mesh(me); b2.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    _obj("MOT_Corona", bm, [M["acero"]], col, cig, liso=False)

    # ---------------- biela (origen en la muñequilla, sube por +Z hasta el bulón)
    bie = bpy.data.objects.new("MOT_BielaRaiz", None); col.objects.link(bie); P(bie); O["bie"] = bie
    bm = bmesh.new(); anillo_y(bm, 0.0225, 0.034, 0.022); anillo_y(bm, 0.0112, 0.0180, 0.020)
    bmesh.ops.translate(bm, verts=[v for v in bm.verts if Vector((v.co.x, v.co.z)).length < 0.0185 and Vector((v.co.x, v.co.z)).length > 0.011], vec=(0, 0, L_BIE))
    poligono_y(bm, [(-0.012, 0.030), (0.012, 0.030), (0.0075, L_BIE - 0.016), (-0.0075, L_BIE - 0.016)], 0.017)
    caja(bm, -0.046, -0.030, -0.009, 0.009, -0.006, 0.006); caja(bm, 0.030, 0.046, -0.009, 0.009, -0.006, 0.006)  # orejetas de los tornillos
    o = _obj("MOT_Biela", bm, [M["acero"]], col, bie); _bisel(o, 0.0012)
    bm = bmesh.new(); cil_z(bm, 0.0042, -0.020, 0.012, seg=24, x=-0.038); cil_z(bm, 0.0042, -0.020, 0.012, seg=24, x=0.038)
    _obj("MOT_TornillosBiela", bm, [M["muñon"]], col, bie)

    # ---------------- pistón (origen en el bulón)
    pis = bpy.data.objects.new("MOT_PistonRaiz", None); col.objects.link(pis); P(pis); O["pis"] = pis
    r = BORE / 2 - 0.0005
    pf = [(0.0, COMP_H - 0.0015), (0.018, COMP_H - 0.0028), (0.030, COMP_H), (r, COMP_H), (r, COMP_H - 0.0045),
          (r - 0.003, COMP_H - 0.0045), (r - 0.003, COMP_H - 0.0065), (r, COMP_H - 0.0065), (r, COMP_H - 0.0100),
          (r - 0.003, COMP_H - 0.0100), (r - 0.003, COMP_H - 0.0120), (r, COMP_H - 0.0120), (r, COMP_H - 0.0155),
          (r - 0.0035, COMP_H - 0.0155), (r - 0.0035, COMP_H - 0.0185), (r, COMP_H - 0.0185),
          (r, -0.026), (r - 0.0035, -0.026), (r - 0.0035, COMP_H - 0.009), (0.0, COMP_H - 0.009)]
    bm = bmesh.new(); torno(bm, pf, seg=96); O["piston"] = _obj("MOT_Piston", bm, [M["alu_pulido"]], col, pis)
    bm = bmesh.new()
    for zz, h in ((COMP_H - 0.0055, 0.0018), (COMP_H - 0.0110, 0.0018), (COMP_H - 0.0170, 0.0026)):
        b2 = bmesh.new(); torno(b2, [(r - 0.0028, zz - h / 2), (r + 0.0002, zz - h / 2), (r + 0.0002, zz + h / 2), (r - 0.0028, zz + h / 2)], seg=96)
        me = bpy.data.meshes.new("t"); b2.to_mesh(me); b2.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    _obj("MOT_Segmentos", bm, [M["segmento"]], col, pis)
    bm = bmesh.new(); anillo_y(bm, 0.0045, 0.0108, 0.066, seg=48); _obj("MOT_Bulon", bm, [M["muñon"]], col, pis)

    # ---------------- bloque, cárter, camisa, culata (macizos con huecos) → se parten por y = 0
    def bloque(bm): caja(bm, -0.075, 0.075, -0.066, 0.066, 0.040, CUBIERTA)
    blo = _malla("MOT_Bloque", bloque, col); blo.data.materials.append(M["alu"])
    c1 = _malla("c", lambda bm: cil_z(bm, 0.0465, 0.0, CUBIERTA + 0.01), col)
    c2 = _malla("c", lambda bm: torno(bm, [(0.051, 0.095), (0.061, 0.095), (0.061, 0.205), (0.051, 0.205)], 96), col)
    restar(blo, [c1, c2])
    car = _malla("MOT_Carter", lambda bm: caja(bm, -0.098, 0.098, -0.078, 0.078, -0.105, 0.040), col); car.data.materials.append(M["alu"])
    c1 = _malla("c", lambda bm: caja(bm, -0.082, 0.082, -0.064, 0.064, -0.090, 0.050), col)
    c2 = _malla("c", lambda bm: anillo_y(bm, 0, 0.027, 0.30), col)
    restar(car, [c1, c2])
    cam = _malla("MOT_Camisa", lambda bm: torno(bm, [(BORE / 2, 0.055), (0.0465, 0.055), (0.0465, CUBIERTA), (BORE / 2, CUBIERTA)], 96), col)
    cam.data.materials.append(M["hierro"])
    ref = _malla("MOT_Refrigerante", lambda bm: torno(bm, [(0.0512, 0.096), (0.0608, 0.096), (0.0608, 0.200), (0.0512, 0.200)], 96), col)
    ref.data.materials.append(M["refrig"])
    ace = _malla("MOT_AceiteCarter", lambda bm: caja(bm, -0.0815, 0.0815, -0.0635, 0.0635, -0.0895, -0.068), col)
    ace.data.materials.append(M["aceite"])
    jun = _malla("MOT_Junta", lambda bm: torno(bm, [(BORE / 2 + 0.001, CUBIERTA), (0.072, CUBIERTA), (0.072, CUBIERTA + 0.0016), (BORE / 2 + 0.001, CUBIERTA + 0.0016)], 96), col)
    jun.data.materials.append(M["junta"])
    # culata con cámara en tejado, conductos de admisión y escape, guías y hueco de la bujía
    zc = CUBIERTA + 0.0016
    cul = _malla("MOT_Culata", lambda bm: caja(bm, -0.088, 0.088, -0.066, 0.066, zc, zc + 0.052), col); cul.data.materials.append(M["alu"])
    def tejado(bm):
        pts = [(-BORE / 2, zc - 0.002), (BORE / 2, zc - 0.002), (BORE / 2 - 0.004, zc + 0.004), (0.0, zc + 0.016), (-BORE / 2 + 0.004, zc + 0.004)]
        poligono_y(bm, pts, BORE * 0.92)
    t1 = _malla("c", tejado, col); t2 = _malla("c", lambda bm: cil_z(bm, BORE / 2, zc - 0.002, zc + 0.006), col)
    cortes = [t1, t2]
    O["asiento"] = {}
    for lado, x in (("adm", ADM_X), ("esc", ESC_X)):
        e = eje_valvula(lado); s = -1 if lado == "adm" else 1
        asiento = Vector((x, 0, zc + 0.006)) ; O["asiento"][lado] = asiento
        rp = 0.0135 if lado == "adm" else 0.0120
        puntos = [asiento + e * 0.004, asiento + e * 0.024 + Vector((s * 0.008, 0, 0)), Vector((s * 0.062, 0, zc + 0.030)), Vector((s * 0.100, 0, zc + 0.028))]
        cortes.append(tubo_curva("c", puntos, rp, col))
        g0 = asiento + e * 0.03; g1 = asiento + e * 0.12
        cortes.append(tubo_curva("c", [g0, (g0 + g1) / 2, g1], 0.0042, col))
    cortes.append(_malla("c", lambda bm: cil_z(bm, 0.0072, zc + 0.008, 0.31), col))
    cortes.append(_malla("c", lambda bm: cil_z(bm, 0.0125, zc + 0.026, 0.31), col))           # pozo de la bujía
    restar(cul, cortes)
    # porta-levas abierto por arriba (se ve el árbol de levas dentro)
    zl = zc + 0.052
    por = _malla("MOT_PortaLevas", lambda bm: caja(bm, -0.088, 0.088, -0.066, 0.066, zl, zc + 0.140), col); por.data.materials.append(M["alu"])
    restar(por, [_malla("c", lambda bm: caja(bm, -0.076, 0.076, -0.058, 0.058, zl - 0.01, zc + 0.150), col)])
    piezas_corte = [blo, car, cam, ref, ace, jun, cul, por]
    O["detras"], O["delante"] = [], []
    for p in piezas_corte:
        d, f = partir(p, M["corte"], col); P(d); P(f); O["detras"].append(d); O["delante"].append(f)
        for ob in (d, f):
            for pl in ob.data.polygons: pl.use_smooth = True
            try: ob.data.set_sharp_from_angle(angle=math.radians(30))
            except Exception: pass
            _bisel(ob, 0.0008, 2)

    # ---------------- válvulas, muelles, levas
    O["valv"] = {}; O["leva"] = {}; O["muelle"] = {}
    for lado in ("adm", "esc"):
        e = eje_valvula(lado); a0 = O["asiento"][lado]
        rcab = 0.0165 if lado == "adm" else 0.0142; largo = 0.105
        raizv = bpy.data.objects.new(f"MOT_Valv_{lado}", None); col.objects.link(raizv); P(raizv)
        raizv.location = a0; raizv.rotation_mode = 'QUATERNION'; raizv.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(e)
        bm = bmesh.new(); torno(bm, _perfil_valvula(rcab, largo), seg=64)
        _obj(f"MOT_Valvula_{lado}", bm, [M["valvula"]], col, raizv)
        bm = bmesh.new(); torno(bm, [(0.0034, largo - 0.022), (0.0115, largo - 0.020), (0.0115, largo - 0.016), (0.0034, largo - 0.014)], 48)
        _obj(f"MOT_Platillo_{lado}", bm, [M["acero"]], col, raizv)
        O["valv"][lado] = raizv
        # muelle: hélice entre el apoyo en la culata y el platillo (se acorta con la alzada)
        cu = bpy.data.curves.new(f"MOT_Muelle_{lado}", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0016; cu.bevel_resolution = 4
        sp = cu.splines.new('POLY'); vueltas = 7.0; n = 180; sp.points.add(n - 1)
        for k in range(n):
            t = k / (n - 1); a = 2 * math.pi * vueltas * t
            sp.points[k].co = (0.0098 * math.cos(a), 0.0098 * math.sin(a), t, 1)
        mo = bpy.data.objects.new(f"MOT_Muelle_{lado}", cu); col.objects.link(mo); P(mo); cu.materials.append(M["muelle"])
        mo.rotation_mode = 'QUATERNION'; mo.rotation_quaternion = raizv.rotation_quaternion
        O["muelle"][lado] = (mo, a0 + e * 0.052, a0 + e * (largo - 0.020))
        # árbol de levas (eje Y) por encima de la cola de la válvula
        cen = a0 + e * (largo + 0.0165)
        lev = bpy.data.objects.new(f"MOT_Leva_{lado}", None); col.objects.link(lev); P(lev); lev.location = cen; O["leva"][lado] = lev
        pts = []
        for k in range(72):
            ang = 2 * math.pi * k / 72; d = abs(((ang + math.pi) % (2 * math.pi)) - math.pi)
            rr = 0.0160 + (LIFT * (0.5 + 0.5 * math.cos(d * math.pi / 1.4)) if d < 1.4 else 0.0)
            pts.append((rr * math.sin(ang), rr * math.cos(ang)))       # la punta de la leva mira a +Z local
        bm = bmesh.new(); poligono_y(bm, pts, 0.016); anillo_y(bm, 0, 0.012, 0.128)
        o = _obj(f"MOT_LevaPieza_{lado}", bm, [M["leva"]], col, lev, liso=True, angulo=60); _bisel(o, 0.0006)
        lev["eje"] = list(e)

    # ---------------- bujía en el centro del tejado
    if BUJ is not None:
        B = BUJ["construir_bujia"](col, MP, "MOT_BUJ")
        B["raiz"].location = (0, 0, zc + 0.012); P(B["raiz"]); O["bujia"] = B
        O["electrodo_punta"] = Vector((0, 0, zc + 0.012))

    # ---------------- gas de la cámara (cilindro entre la cabeza del pistón y el tejado)
    def medio_cil(bm):
        cil_z(bm, BORE / 2 - 0.0008, 0.0, 1.0, seg=96)
        r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_inner=True)
        bordes = [e for e in bm.edges if e.is_boundary]
        if bordes: bmesh.ops.holes_fill(bm, edges=bordes, sides=0)
    gas = _malla("MOT_Gas", medio_cil, col); gas.data.materials.append(M["mezcla"]); P(gas)     # gas cortado como el resto
    O["gas"] = gas
    try: gas.visible_shadow = False
    except Exception: pass

    # ---------------- anclas para rótulos
    O["anclas"] = {}
    for nm, padre, loc in (("PISTON", pis, (0, -0.042, 0.012)), ("BIELA", bie, (0, -0.012, 0.075)), ("CIGUENAL", cig, (0.0, -0.035, -0.040)),
                           ("VALV_ADM", O["valv"]["adm"], (0, 0, 0.06)), ("VALV_ESC", O["valv"]["esc"], (0, 0, 0.06)),
                           ("LEVAS", O["leva"]["adm"], (0, -0.02, 0)), ("CAMARA", raiz, (0, -0.02, zc + 0.008)),
                           ("BUJIA", raiz, (0, -0.01, zc + 0.05)), ("POLEA", cig, (0, -0.10, 0.03))):
        e = bpy.data.objects.new("ANC_" + nm, None); col.objects.link(e); e.parent = padre; e.location = loc; e.empty_display_size = 0.01
        O["anclas"][nm] = e
    return O


# ------------------------------------------------------------------------------------------------ CINEMÁTICA
def alzada(theta, lado):
    """Alzada de la válvula según el ángulo del cigüeñal (simplificada: admisión abre 0-200°, escape 520-720°)."""
    t = theta % 720.0
    a0, a1 = (-10.0, 200.0) if lado == "adm" else (510.0, 730.0)
    tt = t if lado == "adm" else t
    if lado == "adm" and t > 700: tt = t - 720
    if not (a0 <= tt <= a1): return 0.0
    u = (tt - a0) / (a1 - a0)
    return LIFT * math.sin(math.pi * u) ** 2


def piston_z(theta):
    th = math.radians(theta)
    return R_CIG * math.cos(th) + math.sqrt(L_BIE ** 2 - (R_CIG * math.sin(th)) ** 2)


def poner_angulo(O, theta, f, clave=True):
    th = math.radians(theta)
    px, pz = R_CIG * math.sin(th), R_CIG * math.cos(th)
    zp = piston_z(theta)
    O["cig"].rotation_euler = (0, th, 0)
    O["bie"].location = (px, 0, pz); O["bie"].rotation_euler = (0, -math.atan2(px, zp - pz) * 1.0, 0)
    O["pis"].location = (0, 0, zp)
    zc = CUBIERTA + 0.0016
    O["gas"].location = (0, 0, zp + COMP_H - 0.0005); O["gas"].scale = (1, 1, max(0.0005, (zc + 0.010) - (zp + COMP_H - 0.0005)))
    objs = [O["cig"], O["bie"], O["pis"], O["gas"]]
    for lado in ("adm", "esc"):
        e = Vector(O["leva"][lado]["eje"]); h = alzada(theta, lado)
        v = O["valv"][lado]; v.location = O["asiento"][lado] - e * h
        # la leva gira a la mitad; su punta apunta a la válvula en el centro de la apertura
        pico = 95.0 if lado == "adm" else 620.0
        ang_val = math.atan2(-e.x, -e.z)          # ángulo (alrededor de Y) en el que la punta mira hacia la válvula
        O["leva"][lado].rotation_euler = (0, ang_val + math.radians((theta - pico) / 2.0), 0)
        mo, base, tope = O["muelle"][lado]
        tope = tope - e * h
        mo.location = base; mo.scale = (1, 1, (tope - base).length)
        objs += [v, O["leva"][lado], mo]
    if clave:
        for o in objs:
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f) if o.rotation_mode != 'QUATERNION' else None
            o.keyframe_insert("scale", frame=f)
    return zp
