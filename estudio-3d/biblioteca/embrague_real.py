# EMBRAGUE (monodisco en seco, volante rígido) por código · EKORUEDAS · 27-11-2026
# Medidas reales aproximadas de un turismo compacto: volante motor de unos 28 cm con corona dentada, disco de unos 22 cm.
# Origen en el centro de la cara del volante que va al motor; el eje Z va del motor hacia la caja de cambios.
# Capas (de abajo arriba): volante (con corona) -> disco (2 forros ranurados, chapa, cubo con 6 muelles de torsión y estrías)
#   -> maza: plato de presión (fundición, cara pulida), diafragma (cono con 18 dedos) y carcasa de chapa con 6 tornillos
#   -> collarín (cojinete de empuje).
# Grupos para animar (empties hijos de la raíz, giran en Z): "g_volante", "g_disco", "g_maza", "g_collarin".
# Dentro de la maza: "plato" (se separa al pisar), "diafragma" (forma 'pisado': los dedos bajan y el borde sube), "carcasa".
# Uso: EM = {"__name__": "em"}; exec(open(".../embrague_real.py", encoding="utf-8").read(), EM)
#      O = EM["construir_embrague"](coleccion, MP, "EMB")            # entero
#      O = EM["construir_embrague"](coleccion, MP, "EMN", solo_disco=True, gastado=0.0)   # solo el disco (inserto)
import bpy, bmesh, math
from mathutils import Vector, Matrix

R_VOL, H_VOL = 0.140, 0.028            # volante
R_COR0, R_COR1, N_DIENTES = 0.138, 0.148, 120
R_F0, R_F1, E_FORRO = 0.075, 0.110, 0.0035   # forros
Z_DIS0 = H_VOL                          # cara de abajo del disco
E_CHAPA = 0.0016
H_DISCO = 2 * E_FORRO + E_CHAPA         # 8,6 mm
Z_PLATO0 = Z_DIS0 + H_DISCO
H_PLATO = 0.015
Z_DIAF = Z_PLATO0 + H_PLATO + 0.004     # borde del diafragma
Z_COL0 = Z_DIAF + 0.020                 # collarín en reposo (separado de las puntas)


def _obj(nombre, bm, mats, col, padre, liso=True, angulo=35):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = liso
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(nombre, me); col.objects.link(o); o.parent = padre
    if liso:
        md = o.modifiers.new("aristas", 'EDGE_SPLIT'); md.split_angle = math.radians(angulo)
    return o

def _vacio(nombre, col, padre, loc=(0, 0, 0)):
    o = bpy.data.objects.new(nombre, None); col.objects.link(o); o.parent = padre; o.location = loc
    o.empty_display_size = 0.05; o.rotation_mode = 'XYZ'
    return o

def torno(bm, perfil, seg=96, mat=0):
    """Gira un perfil cerrado (r, z) alrededor de Z."""
    antes = set(bm.faces)
    vs = [bm.verts.new((r, 0, z)) for r, z in perfil]
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    res = bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.tau, steps=seg, use_merge=True)
    nuevas = [f for f in bm.faces if f not in antes]
    bmesh.ops.remove_doubles(bm, verts=list({v for f in nuevas for v in f.verts}), dist=1e-6)
    nuevas = [f for f in bm.faces if f not in antes]
    bmesh.ops.recalc_face_normals(bm, faces=nuevas)
    for f in nuevas: f.material_index = mat

def _caja(bm, centro, tam, rot_z=0.0, mat=0):
    """Caja (x, y, z) girada rot_z alrededor del eje Z del objeto (no del centro)."""
    r = bmesh.ops.create_cube(bm, size=1.0)
    M = Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Translation(Vector(centro)) @ Matrix.Diagonal((*tam, 1.0))
    bmesh.ops.transform(bm, matrix=M, verts=r["verts"])
    for f in {f for v in r["verts"] for f in v.link_faces}: f.material_index = mat
    return r["verts"]

def _cil(bm, c, r, z0, z1, seg=24, mat=0, eje=None):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
    for v in res["verts"]: v.co += Vector((0, 0, (z0 + z1) / 2))
    if eje is not None:                     # eje = matriz 4x4 aplicada después (para muelles tumbados)
        bmesh.ops.transform(bm, matrix=eje, verts=res["verts"])
    for v in res["verts"]: v.co += Vector((c[0], c[1], 0))
    for f in {f for v in res["verts"] for f in v.link_faces}: f.material_index = mat
    return res["verts"]

def _salida(nt): return [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]

def ferodo(nombre, gastado=0.0):
    """Forro de fricción: gris pardo mate con grano fino y vetas; 'gastado' lo oscurece y le da brillo de cristalizado."""
    m = bpy.data.materials.new(nombre); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0; nz.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 70.0; nz2.inputs["Detail"].default_value = 5.0
    nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(nz2.outputs["Fac"], cr.inputs[0])
    k = 1.0 - 0.55 * gastado
    cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = (0.16 * k, 0.125 * k, 0.095 * k, 1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (0.30 * k, 0.25 * k, 0.20 * k, 1)
    nt.links.new(cr.outputs[0], b.inputs["Base Color"])
    b.inputs["Metallic"].default_value = 0.05 + 0.15 * gastado
    rg = nt.nodes.new("ShaderNodeMapRange"); rg.clamp = True
    nt.links.new(nz.outputs["Fac"], rg.inputs["Value"])
    rg.inputs["To Min"].default_value = 0.72 - 0.42 * gastado; rg.inputs["To Max"].default_value = 0.9 - 0.4 * gastado
    nt.links.new(rg.outputs[0], b.inputs["Roughness"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.45 * (1 - 0.6 * gastado); bp.inputs["Distance"].default_value = 0.0003
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def materiales(MP, pref):
    return {"volante": MP["acero"](pref + "_MatVolante", (0.56, 0.57, 0.59), (0.14, 0.3)),
            "corona": MP["acero"](pref + "_MatCorona", (0.22, 0.22, 0.23), (0.3, 0.45), anillos=False),
            "cara": MP["acero"](pref + "_MatCaraPulida", (0.78, 0.78, 0.80), (0.06, 0.14)),
            "chapa": MP["acero"](pref + "_MatChapa", (0.48, 0.49, 0.5), (0.22, 0.38), anillos=False),
            "muelle": MP["pintura"](pref + "_MatMuelle", (0.12, 0.13, 0.15), rugo=0.3, barniz=0.5, metal=0.6),
            "plato": MP["fundicion"](pref + "_MatPlato", (0.30, 0.30, 0.31)),
            "diafragma": MP["acero"](pref + "_MatDiafragma", (0.16, 0.22, 0.34), (0.28, 0.42), anillos=False),
            "carcasa": MP["pintura"](pref + "_MatCarcasa", (0.035, 0.038, 0.042), rugo=0.45, barniz=0.25, metal=0.15),
            "tornillo": MP["acero"](pref + "_MatTornillo", (0.62, 0.6, 0.55), (0.2, 0.35), anillos=False),
            "collarin": MP["pintura"](pref + "_MatCollarin", (0.02, 0.02, 0.022), rugo=0.35, barniz=0.6),
            "rodamiento": MP["cromo"](pref + "_MatRodamiento")}

# --------------------------------------------------------------------------------------------- piezas
def _volante(col, padre, M, pref):
    bm = bmesh.new()
    # cuerpo: cara del motor abajo, cara de fricción arriba (anillo pulido), escalón en el centro para los tornillos
    torno(bm, [(0.022, 0.0), (R_VOL - 0.004, 0.0), (R_VOL, 0.004), (R_VOL, H_VOL - 0.003), (R_VOL - 0.003, H_VOL),
               (0.118, H_VOL), (0.118, H_VOL + 0.0006), (0.072, H_VOL + 0.0006), (0.072, H_VOL), (0.060, H_VOL - 0.004),
               (0.045, H_VOL - 0.010), (0.022, H_VOL - 0.010)], mat=0)
    for f in bm.faces:                                    # el anillo de fricción, con el material pulido
        c = f.calc_center_median()
        if abs(c.z - (H_VOL + 0.0006)) < 1e-4 and 0.07 < c.xy.length < 0.12: f.material_index = 2
    for k in range(6):                                    # tornillos del cigüeñal
        a = k * math.tau / 6 + 0.26
        _cil(bm, (0.034 * math.cos(a), 0.034 * math.sin(a)), 0.0055, H_VOL - 0.010, H_VOL - 0.004, 6, mat=3)
    for k in range(6):                                    # roscas para la carcasa
        a = k * math.tau / 6
        _cil(bm, (0.126 * math.cos(a), 0.126 * math.sin(a)), 0.0035, H_VOL - 0.001, H_VOL + 0.0004, 10, mat=3)
    o = _obj(pref + "_Volante", bm, [M["volante"], M["corona"], M["cara"], M["tornillo"]], col, padre)
    # corona dentada (el motor de arranque engrana aquí)
    bm = bmesh.new()
    torno(bm, [(R_COR0 - 0.002, 0.004), (R_COR0 + 0.001, 0.004), (R_COR0 + 0.001, 0.020), (R_COR0 - 0.002, 0.020)], seg=N_DIENTES)
    paso = math.tau / N_DIENTES
    for k in range(N_DIENTES):
        _caja(bm, (R_COR0 + 0.001 + (R_COR1 - R_COR0) / 2, 0, 0.012), (R_COR1 - R_COR0, 2 * math.pi * R_COR0 / N_DIENTES * 0.52, 0.016), k * paso)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    oc = _obj(pref + "_Corona", bm, [M["corona"]], col, padre, liso=False)
    return o, oc

def _disco(col, padre, M, MF, pref, gastado=0.0):
    piezas = {}
    e_f = E_FORRO * (1 - 0.6 * gastado)                  # forro gastado: más fino
    zc0 = Z_DIS0 + E_FORRO; zc1 = zc0 + E_CHAPA          # chapa en medio (la posición no cambia: el desgaste sale por las caras)
    # forros: 2 anillos con 16 ranuras radiales cada uno
    bm = bmesh.new(); n = 16; hueco = 0.0022
    for (z0, z1) in ((zc0 - e_f, zc0), (zc1, zc1 + e_f)):
        for k in range(n):
            a0 = k * math.tau / n + hueco / R_F0; a1 = (k + 1) * math.tau / n - hueco / R_F0
            seg = 8; vs = []
            for i in range(seg + 1):
                a = a0 + (a1 - a0) * i / seg
                for r in (R_F0, R_F1):
                    for z in (z0, z1): vs.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
            for i in range(seg):
                b0 = i * 4; b1 = (i + 1) * 4
                # vértices: 0 = r0 z0, 1 = r0 z1, 2 = r1 z0, 3 = r1 z1
                for (p, q) in ((0, 1), (1, 3), (3, 2), (2, 0)):
                    bm.faces.new((vs[b0 + p], vs[b1 + p], vs[b1 + q], vs[b0 + q]))
            bm.faces.new((vs[0], vs[1], vs[3], vs[2])); L = seg * 4
            bm.faces.new((vs[L + 0], vs[L + 2], vs[L + 3], vs[L + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    piezas["forros"] = _obj(pref + "_Forros", bm, [MF], col, padre, angulo=30)
    # chapa ondulada de soporte (anillo fino) + plato del cubo con ventanas
    bm = bmesh.new()
    torno(bm, [(0.050, zc0), (R_F1 - 0.002, zc0), (R_F1 - 0.002, zc1), (0.050, zc1)], seg=96)
    torno(bm, [(0.024, zc0 - 0.0035), (0.072, zc0 - 0.0035), (0.072, zc0 - 0.002), (0.024, zc0 - 0.002)], seg=72)
    torno(bm, [(0.024, zc1 + 0.002), (0.072, zc1 + 0.002), (0.072, zc1 + 0.0035), (0.024, zc1 + 0.0035)], seg=72)
    piezas["chapa"] = _obj(pref + "_Chapa", bm, [M["chapa"]], col, padre)
    # 6 muelles de torsión (hélice tumbada, tangente al giro) a 50 mm del centro
    bm = bmesh.new()
    for k in range(6):
        a = k * math.tau / 6 + math.pi / 6
        espiras, R_m, r_h, L = 6, 0.0072, 0.0012, 0.030
        pts = []
        for i in range(espiras * 16 + 1):
            t = i / 16 * math.tau
            pts.append(Vector((R_m * math.cos(t), -L / 2 + L * i / (espiras * 16), R_m * math.sin(t))))
        # tubo por la hélice: anillos de 6 lados
        anillos = []
        for i, p in enumerate(pts):
            tg = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            nrm = Vector((p.x, 0, p.z)).normalized(); bi = tg.cross(nrm).normalized(); nrm = bi.cross(tg).normalized()
            anillos.append([p + (nrm * math.cos(j * math.tau / 6) + bi * math.sin(j * math.tau / 6)) * r_h for j in range(6)])
        rot = Matrix.Rotation(a, 3, 'Z'); off = Vector((0.050 * math.cos(a), 0.050 * math.sin(a), (zc0 + zc1) / 2))
        vv = [[bm.verts.new(rot @ q + off) for q in an] for an in anillos]
        for i in range(len(vv) - 1):
            for j in range(6):
                bm.faces.new((vv[i][j], vv[i][(j + 1) % 6], vv[i + 1][(j + 1) % 6], vv[i + 1][j]))
    piezas["muelles"] = _obj(pref + "_Muelles", bm, [M["muelle"]], col, padre, angulo=60)
    # cubo estriado (entra en el eje de la caja)
    bm = bmesh.new()
    torno(bm, [(0.014, zc0 - 0.010), (0.024, zc0 - 0.010), (0.024, zc1 + 0.012), (0.014, zc1 + 0.012)], seg=40)
    for k in range(20):                                   # estrías por dentro
        _caja(bm, (0.0128, 0, (zc0 + zc1) / 2 + 0.001), (0.003, 0.0024, 0.022 + E_CHAPA), k * math.tau / 20)
    piezas["cubo"] = _obj(pref + "_Cubo", bm, [M["chapa"]], col, padre, angulo=40)
    return piezas

def _maza(col, padre, M, pref):
    piezas = {}
    # plato de presión: fundición, cara de abajo pulida; 3 orejetas para las lengüetas
    g_pl = _vacio(pref + "_Plato", col, padre)
    bm = bmesh.new()
    z0, z1 = Z_PLATO0, Z_PLATO0 + H_PLATO
    torno(bm, [(R_F0 - 0.002, z0), (R_F1 + 0.002, z0), (R_F1 + 0.004, z0 + 0.003), (R_F1 + 0.004, z1 - 0.004),
               (R_F1 - 0.004, z1), (0.098, z1), (0.098, z1 + 0.003), (0.092, z1 + 0.003), (0.092, z1), (R_F0 + 0.004, z1),
               (R_F0 - 0.002, z1 - 0.004)], seg=96)
    for f in bm.faces:
        if abs(f.calc_center_median().z - z0) < 1e-4: f.material_index = 1
    for k in range(3):
        _caja(bm, (R_F1 + 0.010, 0, z0 + 0.007), (0.014, 0.018, 0.008), k * math.tau / 3 + 0.3)
    piezas["plato"] = _obj(pref + "_PlatoPieza", bm, [M["plato"], M["cara"]], col, g_pl)
    # diafragma: anillo cónico + 18 dedos hacia el centro, con forma 'pisado'
    bm = bmesh.new()
    zr = Z_DIAF; zp = Z_DIAF + 0.009                      # borde abajo, puntas arriba (cono)
    torno(bm, [(0.084, zr + 0.0022), (0.106, zr - 0.0004), (0.106, zr + 0.0016), (0.084, zr + 0.0042)], seg=96)
    n = 18
    for k in range(n):
        a = k * math.tau / n
        # dedo: trapecio de 0,084 a 0,026 de radio, un poco más estrecho en la punta
        an0 = (math.tau / n) * 0.40                       # media anchura en el borde (deja ranuras entre dedos)
        an1 = 0.0036 / 0.026                              # punta de unos 7 mm
        def P(r, aa, z): return Vector((r * math.cos(aa), r * math.sin(aa), z))
        def zc(r): return zr + 0.0022 + (0.084 - r) / (0.084 - 0.026) * (zp - zr - 0.0022)
        vs = []
        for r, an in ((0.0845, an0), (0.026, an1)):
            for s in (-1, 1):
                for dz in (0.0, 0.0020): vs.append(bm.verts.new(P(r, a + s * an, zc(r) + dz)))
        q = lambda i, j, k_, l: bm.faces.new((vs[i], vs[j], vs[k_], vs[l]))
        q(0, 2, 3, 1); q(4, 5, 7, 6); q(0, 1, 5, 4); q(2, 6, 7, 3); q(1, 3, 7, 5); q(0, 4, 6, 2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    piezas["diafragma"] = od = _obj(pref + "_Diafragma", bm, [M["diafragma"]], col, padre, angulo=40)
    od.shape_key_add(name="Basis", from_mix=False); kb = od.shape_key_add(name="pisado", from_mix=False)
    # palanca sobre el apoyo (r = 0,095): los dedos bajan hasta casi el borde y el borde sube un poco
    for i, v in enumerate(od.data.vertices):
        r = v.co.xy.length
        if r < 0.095: dz = -(0.095 - r) / (0.095 - 0.026) * 0.012
        else: dz = (r - 0.095) / 0.011 * 0.0035
        kb.data[i].co = v.co + Vector((0, 0, dz))
    # carcasa de chapa estampada con 6 tornillos (se atornilla al volante)
    bm = bmesh.new()
    zt = Z_DIAF + 0.008
    torno(bm, [(0.116, Z_DIS0 + 0.0002), (0.134, Z_DIS0 + 0.0002), (0.134, Z_DIS0 + 0.0032), (0.121, Z_DIS0 + 0.0032),
               (0.121, zt - 0.004), (0.117, zt), (0.098, zt + 0.0004), (0.098, zt + 0.0034), (0.118, zt + 0.003),
               (0.124, zt - 0.004), (0.124, Z_DIS0 + 0.0045), (0.116, Z_DIS0 + 0.0045)], seg=96)
    # ventanas de ventilación: se marcan con cajas oscuras finas sobre la pared
    for k in range(6):
        a = k * math.tau / 6
        _cil(bm, (0.126 * math.cos(a), 0.126 * math.sin(a)), 0.0045, Z_DIS0 + 0.0032, Z_DIS0 + 0.0072, 6, mat=1)
    piezas["carcasa"] = _obj(pref + "_Carcasa", bm, [M["carcasa"], M["tornillo"]], col, padre, angulo=40)
    return piezas, g_pl

def _collarin(col, padre, M, pref):
    bm = bmesh.new(); z0 = Z_COL0
    torno(bm, [(0.020, z0 + 0.004), (0.034, z0 + 0.004), (0.034, z0 + 0.026), (0.020, z0 + 0.026)], seg=64, mat=0)
    torno(bm, [(0.020, z0), (0.031, z0), (0.031, z0 + 0.004), (0.020, z0 + 0.004)], seg=64, mat=1)    # pista que empuja
    torno(bm, [(0.034, z0 + 0.016), (0.044, z0 + 0.016), (0.044, z0 + 0.020), (0.034, z0 + 0.020)], seg=64, mat=0)   # pestaña
    return _obj(pref + "_Collarin", bm, [M["collarin"], M["rodamiento"]], col, padre)

def construir_embrague(col, MP, pref="EMB", solo_disco=False, gastado=0.0):
    M = materiales(MP, pref); MF = ferodo(pref + "_MatForro", gastado)
    raiz = _vacio(pref + "_Raiz", col, None)
    O = {"raiz": raiz, "M": M, "MF": MF}
    if solo_disco:
        g = _vacio(pref + "_GDisco", col, raiz, (0, 0, -Z_DIS0))
        O.update(_disco(col, g, M, MF, pref, gastado)); O["g_disco"] = g
        return O
    for n in ("g_volante", "g_disco", "g_maza", "g_collarin"):
        O[n] = _vacio(pref + "_G" + n[2:].capitalize(), col, raiz)
    O["volante"], O["corona"] = _volante(col, O["g_volante"], M, pref)
    O.update(_disco(col, O["g_disco"], M, MF, pref, gastado))
    pz, O["g_plato"] = _maza(col, O["g_maza"], M, pref); O.update(pz)
    O["collarin"] = _collarin(col, O["g_collarin"], M, pref)
    return O

def girar(o, claves):
    """Giro en Z con claves lineales: claves = [(fotograma, ángulo en radianes), ...]."""
    o.rotation_mode = 'XYZ'
    for f, a in claves:
        o.rotation_euler = (0, 0, a); o.keyframe_insert("rotation_euler", index=2, frame=f)
    ad = o.animation_data
    if ad and ad.action:
        try: cv = list(ad.action.fcurves)
        except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
        for fc in cv:
            if fc.data_path == "rotation_euler":
                for k in fc.keyframe_points: k.interpolation = 'LINEAR'
