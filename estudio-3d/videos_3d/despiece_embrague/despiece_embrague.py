# DESPIECE 3D DEL EMBRAGUE (27-11-2026, para publicar el 28-11 a las 19:00) · vertical 9:16, 30 fps, ~32,6 s
# "¿Tu coche sube de vueltas, pero no corre? Clod, quita el pie de ahí. El culpable está aquí: el embrague."
# Clod da golpecitos con el pie en el capó como si pisara un pedal -> rayos X al lado de la caja de cambios -> el embrague
# sale volando al estudio -> se separa en capas (volante, disco, maza, collarín) -> la maza aprieta el disco contra el volante
# y todo gira junto -> plano de lado sin la carcasa: el collarín empuja el diafragma, el plato se separa (hueco) y el disco
# se para mientras el volante sigue girando -> inserto: disco nuevo frente a gastado ("patina") -> Alex: síntomas
# (sube de vueltas, huele a quemado) -> "no lleves el pie apoyado en el pedal. ¿Verdad, Clod?" -> Clod, pillado otra vez.
BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
NOMBRE = "embrague"; DD = BASE + r"\videos_3d\despiece_embrague"
_B = open(BASE + r"\plantillas\despiece_base.py", encoding="utf-8").read().split("# ==== PARTE 2 ====")
exec(_B[0])
R = math.radians

# ---------------------------------------------------------------- tiempos (por palabra de la voz)
XR0 = FW(0, 15) - 3                 # "culpable": rayos X
EST = FW(0, 19)                     # "embrague": sale volando
B0 = FW(1, 0)                       # "El volante...": en el estudio, montado
F_DIS = FW(1, 7)                    # "disco": se separa en capas
F_MAZ = FW(1, 17)                   # "maza"
F_DIA = FW(1, 20)                   # "diafragma"
F_APR = FW(1, 21)                   # "aprieta": se junta todo
F_GIRO = FW(1, 27)                  # "así pasa el giro": gira junto (nuevo plano)
C0 = FW(2, 0)                       # "Al pisar el pedal": plano de lado, sin carcasa
F_COL = FW(2, 5)                    # "collarín"
F_EMP = FW(2, 6)                    # "empuja"
F_DIAF = FW(2, 8)                   # "diafragma"
F_SEP = FW(2, 10)                   # "la maza deja de apretar": hueco
F_DESC = FW(2, 16)                  # "el motor queda desconectado": el disco se para
A2 = INS = FW(2, 22)                # "Con los kilómetros": inserto nuevo / gastado
F_PAT = FW(2, 32)                   # "patina"
A3 = FW(3, 0)                       # Alex: síntomas
F_VER = FW(4, 9)                    # "¿Verdad, Clod?": corte a Clod, pillado
CTA = FL(4) + 10
FIN = CTA + 66
F_OSCURO = EST - 2
CORTES = [1, B0, F_GIRO, C0, A2, A3, F_VER, CTA, FIN + 1]
EV = {"XR0": XR0, "F_DIS": F_DIS, "F_MAZ": F_MAZ, "F_DIA": F_DIA, "F_APR": F_APR, "F_GIRO": F_GIRO, "C0": C0, "F_COL": F_COL,
      "F_EMP": F_EMP, "F_DIAF": F_DIAF, "F_SEP": F_SEP, "F_DESC": F_DESC, "F_PAT": F_PAT, "F_VER": F_VER}

# ---------------------------------------------------------------- el embrague
EM = {"__name__": "em"}; exec(open(D_ + r"\embrague_real.py", encoding="utf-8").read(), EM)
CP = col_pieza("EMBRAGUE")
O = EM["construir_embrague"](CP, MP, "EMB")
RAIZ = O["raiz"]; RAIZ.rotation_mode = 'XYZ'
GV, GD, GM, GC, GP = O["g_volante"], O["g_disco"], O["g_maza"], O["g_collarin"], O["g_plato"]
E_POS = Vector((-1.45, 0.36, 0.44)); ALTO = 0.12; ESC_P = 1.0
P = Vector((-1.30, -1.05, 0.56)); ROTP = (0, 0, R(-24))
vuelo(RAIZ, EST, B0 - 2, esc_coche=0.55, rot_coche=(R(-90), 0, 0), alto_salida=0.50)

# separación en capas (Z local: del motor hacia la caja) y vuelta a juntarse
EXP = {"disco": 0.075, "maza": 0.155, "col": 0.245}
for g in (GV, GD, GM, GC, GP): kl(g, 1, (0, 0, 0))
for g, dz, d0 in ((GD, EXP["disco"], 0), (GM, EXP["maza"], 3), (GC, EXP["col"], 6)):
    kl(g, F_DIS - 4 + d0, (0, 0, 0)); kl(g, F_DIS + 10 + d0, (0, 0, dz))
    kl(g, F_APR - 1, (0, 0, dz))
kl(GD, F_APR + 9, (0, 0, 0)); kl(GM, F_APR + 7, (0, 0, 0)); kl(GC, F_APR + 10, (0, 0, 0))
# la maza se inclina un poco al nombrarla (se le ve la cara del plato) y vuelve
GM.rotation_mode = 'XYZ'
for f_, rx in ((F_MAZ - 2, 0), (F_MAZ + 8, R(14)), (F_APR - 1, R(14)), (F_APR + 7, 0)):
    GM.rotation_euler[0] = rx; GM.keyframe_insert("rotation_euler", index=0, frame=f_)

# pedal pisado (plano de lado): collarín baja, diafragma se dobla, el plato se separa y el disco queda libre
kl(GC, F_COL - 2, (0, 0, 0)); kl(GC, F_EMP + 5, (0, 0, -0.0085)); kl(GC, F_DIAF + 6, (0, 0, -0.0205)); kl(GC, A2, (0, 0, -0.0205))
kb = O["diafragma"].data.shape_keys.key_blocks["pisado"]
for f_, v in ((1, 0.0), (F_EMP + 5, 0.0), (F_DIAF + 6, 1.0), (A2, 1.0)):
    kb.value = v; kb.keyframe_insert("value", frame=f_)
kl(GP, F_SEP - 4, (0, 0, 0)); kl(GP, F_SEP + 6, (0, 0, 0.0065))           # hueco exagerado para que se vea (en real, 1-2 mm)
kl(GD, F_SEP - 4, (0, 0, 0)); kl(GD, F_SEP + 6, (0, 0, 0.0025))
vis(O["carcasa"], 1, True); vis(O["carcasa"], C0, False)                  # sin carcasa en el plano de lado

# giro: volante y maza van con el motor; el disco, con la caja (se para al pisar)
W = 0.16                                                                 # rad por fotograma
def ang(f): return W * (f - F_GIRO)
for g in (GV, GM):
    EM["girar"](g, [(1, 0.0), (F_GIRO, 0.0), (A2, ang(A2))])
a_s = ang(F_SEP + 2)
EM["girar"](GD, [(1, 0.0), (F_GIRO, 0.0), (F_SEP + 2, a_s), (F_SEP + 10, a_s + W * 8 * 0.7), (F_SEP + 18, a_s + W * 8 * 1.1),
                 (F_DESC + 8, a_s + W * 8 * 1.35), (A2, a_s + W * 8 * 1.35)])
# la maza se inclinaba en X: el giro se suma en Z (claves en índice 2) sin tocar la X

# ---------------------------------------------------------------- inserto: disco nuevo frente a gastado
COLI = col_pieza("EMBRAGUE_INSERTO")
DQ = Vector((-0.50, -0.26, 0.14)).normalized(); RQ = Vector((-DQ.y, DQ.x, 0)).normalized()
INS_DIST = 1.25
for clave, pref, lado, gas in (("AN", "EMN", -1, 0.0), ("AG", "EMG", 1, 1.0)):
    o2 = EM["construir_embrague"](COLI, MP, pref, solo_disco=True, gastado=gas)
    r_ = o2["raiz"]; r_.rotation_mode = 'XYZ'; r_.scale = (0.78, 0.78, 0.78)
    r_.rotation_euler = DQ.to_track_quat("Z", "Y").to_euler()            # la cara del forro mira a la cámara
    r_.location = Q + RQ * (0.105 * lado) - Vector((0, 0, 0.02))
    INSERTO[clave] = (r_, Vector((0.0, -0.093, 0.0045)))
    if gas > 0:                                                           # el gastado gira despacio y "patina" (tiembla)
        EM["girar"](o2["g_disco"], [(1, 0.0), (INS, 0.0), (A3, R(40))])
    else:
        EM["girar"](o2["g_disco"], [(1, 0.0), (INS, 0.0), (A3, R(40))])
# humo fino en "patina" junto al disco gastado
LH = luz("D_LuzQuemado", 'POINT', Q + RQ * 0.105 + Vector((0, -0.05, 0.05)), Q + RQ * 0.105, (1.0, 0.45, 0.12))
kluz(LH, [(1, 0), (F_PAT - 2, 0), (F_PAT + 6, 18), (A3 - 1, 18), (A3, 0)])

# ---------------------------------------------------------------- planos de la pieza (coordenadas del embrague, Z hacia arriba)
cl(B0, (0.30, -0.80, 0.46), (0.0, 0.0, 0.07), 40); cl(F_DIS - 1, (0.27, -0.78, 0.44), (0.0, 0.0, 0.08), 40)
cl(F_DIS + 10, (0.34, -0.88, 0.56), (0.0, 0.0, 0.15), 40); cl(F_GIRO - 1, (0.18, -0.92, 0.54), (0.0, 0.0, 0.15), 40)
cl(F_GIRO, (0.42, -0.58, 0.14), (0.0, 0.0, 0.04), 40); cl(C0 - 1, (0.39, -0.60, 0.16), (0.0, 0.0, 0.04), 41)
cl(C0, (0.30, -0.80, 0.30), (0.0, 0.0, 0.05), 40); cl(F_SEP - 1, (0.26, -0.72, 0.25), (0.0, -0.02, 0.05), 40)
cl(F_SEP, (0.22, -0.62, 0.17), (0.0, -0.03, 0.045), 40); cl(A2 - 1, (0.24, -0.66, 0.18), (0.0, -0.03, 0.045), 40)
PUNTOS = {"volante": (GV, (0.0, -0.136, 0.012)),
          "corona": (GV, (0.0, -0.146, 0.012)),
          "disco": (GD, (0.0, -0.108, EM["Z_DIS0"] + 0.006)),
          "muelles": (GD, (0.0, -0.050, EM["Z_DIS0"] + 0.0043)),
          "maza": (GM, (0.0, -0.122, EM["Z_PLATO0"] + 0.020)),
          "diafragma": (GM, (0.0, -0.060, EM["Z_DIAF"] + 0.006)),
          "collarin": (GC, (0.0, -0.034, EM["Z_COL0"] + 0.014)),
          "hueco": (GP, (0.0, -0.100, EM["Z_PLATO0"] - 0.001)),
          "plato": (GP, (0.0, -0.110, EM["Z_PLATO0"] + 0.008))}

# ---------------------------------------------------------------- gestos
G = {"pregunta": FW(0, 0), "clod": FW(0, 8), "plano_clod": FW(0, 4), "mira": FW(0, 15), "sintomas": [], "ojo": FW(3, 8),
     "manos": FW(3, 11)}
def _tap(CL, f0, f1, cada=8):
    """Golpecitos con el pie derecho, como si pisara un pedal."""
    f = f0
    while f + cada <= f1:
        CL.pie_en("R", f, (-0.115, 0.0, 0.07)); CL.pie_en("R", f + cada // 2, (-0.115, -0.03, 0.13))
        CL.cabeza(f + cada // 2, 4, 0, 10); CL.cabeza(f + cada, -2, 0, 10)
        f += cada
    CL.pie_en("R", f, (-0.115, 0.0, 0.07))
    return f
def gag_clod(CL):
    CL.cara(1, "feliz")
    f = _tap(CL, 1, FW(0, 8) - 4)
    fn = FW(0, 8)                                       # "Clod": se queda con el pie en el aire
    CL.pie_en("R", fn - 2, (-0.115, -0.03, 0.13)); CL.pie_en("R", fn + 10, (-0.115, -0.03, 0.13))
    CL.cara(fn, "sorpresa"); CL.cabeza(fn, -8, 6, 18); CL.mirar(fn, 0.012, 0.004); CL.aplastar(fn, 1.0); CL.aplastar(fn + 3, 1.06); CL.aplastar(fn + 9, 1.0)
    fq = FW(0, 12)                                      # "el pie de ahí": lo baja despacio, culpable
    CL.pie_en("R", fq + 8, (-0.115, 0.0, 0.07)); CL.cara(fq, "triste"); CL.cabeza(fq + 4, 10, -6, 10)
    for l in ("R", "L"):
        CL.mano_en(l, fq + 6, (SX(l) * 0.06, 0.10, 0.52)); CL.codo_hacia(l, fq + 6, (SX(l) * 0.45, 0.20, 0.50))   # manos atrás
    fm = FW(0, 15)                                      # "El culpable": mira al capó
    for l in ("R", "L"): CL.brazo_caido(l, fm)
    CL.cara(fm, "sorpresa"); CL.cabeza(fm, 26, 0, 0); CL.mirar(fm, 0.0, -0.012)
def gag_consejo(CL):
    CL.reposo(A3 - 1); CL.cara(A3, "feliz")
    f = _tap(CL, A3, F_VER - 2, cada=8)                 # otra vez con el pie...
    CL.pie_en("R", F_VER - 1, (-0.115, -0.03, 0.13))
    fv = FW(4, 10)                                      # "Clod": pillado
    CL.pie_en("R", fv - 2, (-0.115, -0.03, 0.13)); CL.pie_en("R", fv + 2, (-0.115, 0.0, 0.07))
    CL.cara(fv, "susto"); CL.aplastar(fv, 1.0); CL.aplastar(fv + 3, 0.86); CL.aplastar(fv + 9, 1.03); CL.aplastar(fv + 14, 1.0)
    CL.cabeza(fv, -6, 0, 12); CL.mirar(fv, 0.012, 0.003)
    for l in ("R", "L"):
        CL.mano_en(l, fv + 6, (SX(l) * 0.06, 0.10, 0.52)); CL.codo_hacia(l, fv + 6, (SX(l) * 0.45, 0.20, 0.50))
    CL.cara(fv + 10, "triste"); CL.cabeza(fv + 12, 12, -8, 12)
    for l in ("R", "L"): CL.brazo_caido(l, CTA)

exec(_B[1])

# ---------------------------------------------------------------- después de la plantilla
# Alex v3: serio (la plantilla le pone sonrisa al principio, pícaro en la pregunta y sonrisa al mirar a Clod)
SERIO = {"BocaTriste_R": 0.95, "BocaTriste_L": 0.95}         # hablando, la boca abierta enseña la sonrisa de la malla: más compensación
for f_, ex, it in ((1, "seria", 1.0), (G["pregunta"], "duda", 0.7), (G["clod"], "enfado", 0.5), (FW(0, 13), "seria", 1.0), (B0 + 30, "seria", 1.0),
                   (A3, "seria", 1.0), (FW(3, 8), "duda", 0.8), (FW(4, 0), "seria", 1.0)):
    cara(f_, ex, it, **(SERIO if ex in ("seria", "duda") else {}))
cara(FW(4, 9), "picaro", 0.35)

# "huele a quemado": un dedo arriba a la altura del pecho (la plantilla llevaba la mano a la cara y la tapaba)
mano_en("R", G["ojo"], (-0.20, -0.36, 1.28)); codo_hacia("R", G["ojo"], (-0.55, 0.05, 1.0)); mano_pose("R", G["ojo"], "señalar")
orientar_mano("R", G["ojo"], dedos_hacia=(0, 0, 1), pulgar_hacia=(1, 0, 0))
mano_en("R", G["ojo"] + 12, (-0.20, -0.37, 1.31)); orientar_mano("R", G["ojo"] + 12, dedos_hacia=(0, 0, 1), pulgar_hacia=(1, 0, 0))
# estudio oscuro de verdad: el taller y el coche se ocultan mientras la pieza está en el estudio y en el inserto
_ocultos = [o for c in ("TALLER_v2", "COCHE", "CLOD_v2_personaje") if bpy.data.collections.get(c) for o in bpy.data.collections[c].all_objects]
for o in _ocultos:
    o.hide_render = o.hide_viewport = False
    for f_, h in ((1, False), (B0, True), (A3, False)):
        o.hide_render = o.hide_viewport = h; o.keyframe_insert("hide_render", frame=f_); o.keyframe_insert("hide_viewport", frame=f_)
    for fc in _curvas(o):
        if fc.data_path.startswith("hide_"):
            for k in fc.keyframe_points: k.interpolation = 'CONSTANT'
# luces de la pieza y del inserto más suaves (la pieza es grande y el metal se quemaba)
def _escala_luz(n, k_):
    o = bpy.data.objects.get(n)
    if not o: return
    for fc in _curvas(o.data):
        if fc.data_path == "energy":
            for kp_ in fc.keyframe_points: kp_.co[1] *= k_; kp_.handle_left[1] *= k_; kp_.handle_right[1] *= k_
# las luces del taller siguen bajas en el inserto (la plantilla las subía en A2 = INS y quemaban los discos)
for o in [x for x in bpy.data.objects if x.type == 'LIGHT' and not x.name.startswith("D_Luz")]:
    for fc in _curvas(o.data):
        if fc.data_path != "energy": continue
        kk = sorted(fc.keyframe_points, key=lambda k: k.co[0]); bajo = min(k.co[1] for k in kk); alto = max(k.co[1] for k in kk)
        for k in kk:
            if abs(k.co[0] - A2) < 0.5: k.co[1] = bajo; k.handle_left[1] = k.handle_right[1] = bajo
        o.data.energy = bajo; o.data.keyframe_insert("energy", frame=A3 - 1); o.data.energy = alto; o.data.keyframe_insert("energy", frame=A3)
for n, k_ in (("D_LuzClave", 0.55), ("D_LuzContra", 0.8), ("D_LuzArriba", 0.5), ("D_LuzInserto", 0.15), ("D_LuzInsertoContra", 0.35), ("D_LuzQuemado", 0.25)):
    _escala_luz(n, k_)
# corte a Clod en "¿Verdad, Clod?": la plantilla tenía a Alex de A3 a CTA-1
def _lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))
u = (F_VER - 1 - A3) / max(1, (CTA - 1 - A3))
ck(F_VER - 1, _lerp((-0.40, -2.05, 1.55), (-0.42, -1.92, 1.55), u), (-0.66, -0.58, 1.50), 35 + 2 * u)
ck(F_VER, (-1.40, -1.62, 1.14), (-1.52, 0.45, 0.93), 40); ck(CTA - 1, (-1.40, -1.55, 1.13), (-1.52, 0.45, 0.93), 41)
for idb in (cam, cam.data):
    for fc in _curvas(idb):
        for k in fc.keyframe_points:
            if int(round(k.co[0])) in (F_VER - 1, CTA - 1): k.interpolation = 'CONSTANT'
        fc.update()
sc.frame_set(1)
result = {"ok": True, "fin": FIN, "cortes": CORTES, "clod": list(CLOD_CAPO), "hit": bool(hit), "ev": EV}
