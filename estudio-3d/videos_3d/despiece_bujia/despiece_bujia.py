# DESPIECE 3D DE LA BUJÍA (27-11-2026, para publicar el 30-11) · vertical 9:16, 30 fps, ~29,9 s
# "¿Tu coche tiembla parado en el semáforo? La culpa puede ser de esta pieza tan pequeña. Clod, no la toques."
# El coche tiembla y Clod con él -> rayos X -> la bujía sale del capó y flota delante de Clod -> la toca: ¡calambrazo! ->
# estudio: la bujía entera (contador 12 V -> 40.000 V) -> se parte por la mitad: la corriente baja por el electrodo central
# dentro de la cerámica -> macro de los electrodos: salta la chispa -> bola de fuego -> el electrodo se gasta, hollín y
# chispa débil -> Alex: tirones, ralentí inestable, más consumo -> "los diésel no llevan bujías, llevan calentadores".
BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
NOMBRE = "bujia"; DD = BASE + r"\videos_3d\despiece_bujia"
_B = open(BASE + r"\plantillas\despiece_base.py", encoding="utf-8").read().split("# ==== PARTE 2 ====")
exec(_B[0])
R = math.radians

# ---------------------------------------------------------------- tiempos
XR0 = FW(0, 8)                      # "culpa": rayos X
EST = FW(0, 12)                     # "esta pieza": la bujía sale del capó
F_ZAP = FW(0, 19)                   # "toques": calambrazo
B0 = FW(1, 0)
C0 = FW(1, 13)                      # "Bajan por el electrodo central": se parte por la mitad
D0 = FW(1, 22)                      # "y saltan aquí": macro de los electrodos
E0 = FW(1, 29)                      # "Esa chispa enciende la gasolina": fuego
F0 = FW(2, 0)                       # "Con los kilómetros, el electrodo se gasta"
A2 = FW(2, 12)                      # "tirones...": Alex
INS = A3 = FW(3, 0)                 # sin inserto
CTA = FL(3) + 10
FIN = CTA + 66
F_OSCURO = B0 - 1
CORTES = [1, B0, C0, D0, E0, F0, A2, A3, CTA, FIN + 1]
EV = {"XR0": XR0, "F_ZAP": F_ZAP, "C0": C0, "D0": D0, "E0": E0, "F0": F0}

# ---------------------------------------------------------------- la bujía
BJ = {"__name__": "bj"}; exec(open(D_ + r"\bujia_real.py", encoding="utf-8").read(), BJ)
CP = col_pieza("BUJIA")
O = BJ["construir_bujia"](CP, MP, "BUJ")
RAIZ = O["raiz"]; RAIZ.rotation_mode = 'XYZ'; M_ = O["M"]
E_POS = Vector((-1.42, 0.80, 0.55)); ALTO = 0.09; ESC_P = 3.0
P = Vector((-1.30, -1.05, 0.66)); ROTP = (0, 0, R(-24))
FLOTA = Vector((-1.70, 0.44, 0.905))                     # delante de Clod (el terminal le queda a la altura de la mano)
kl(RAIZ, 1, E_POS, (0, 0, 0)); kl(RAIZ, EST, E_POS, (0, 0, 0))
kl(RAIZ, EST + 10, FLOTA + Vector((0.02, 0.0, 0.10)), (R(8), 0, R(40))); kl(RAIZ, EST + 22, FLOTA, (R(-4), 0, R(70)))
for k in range(6): kl(RAIZ, EST + 30 + k * 12, FLOTA + Vector((0, 0, 0.006 * (1 if k % 2 == 0 else -1))), (R(-4), 0, R(70 + 6 * k)))
kl(RAIZ, F_ZAP + 1, FLOTA, (R(-4), 0, R(110))); kl(RAIZ, F_ZAP + 8, FLOTA + Vector((0.05, -0.03, 0.03)), (R(25), R(-10), R(150)))
kl(RAIZ, B0 - 1, FLOTA + Vector((0.05, -0.03, 0.03)), (R(25), R(-10), R(150)))
kl(RAIZ, B0, P, ROTP)
ks(RAIZ, 1, 1.2); ks(RAIZ, B0 - 1, 1.2); ks(RAIZ, B0, ESC_P)
EXTRA_CONST = []
# corte por la mitad al empezar a bajar la corriente
FRENTE = bpy.data.objects.new("BUJ_Frente", None); CP.objects.link(FRENTE); FRENTE.parent = RAIZ
partir([O[k] for k in ("aislante", "electrodo", "cobre", "sello", "terminal", "casco", "hex", "rosca", "arandela")], FRENTE)
kl(FRENTE, 1, (0, 0, 0), (0, 0, 0)); kl(FRENTE, C0 + 1, (0, 0, 0), (0, 0, 0))
kl(FRENTE, C0 + 16, (0.012, -0.045, 0.010), (R(-25), R(15), R(30)))
vis(FRENTE, 1, True); vis(FRENTE, C0 + 17, False)
# la corriente baja por el centro
VOLT = BJ["voltaje"](CP, RAIZ, M_["voltaje"], C0 + 4, D0 + 6)
# chispas: la del calambrazo con Clod la pone gag_clod; aquí las de la bujía (fuertes y luego débiles)
LZ = luz("D_LuzChispa", 'POINT', MPm() @ Vector((0, -0.004, -0.0005)), MPm() @ Vector((0, 0, 0)), (0.6, 0.8, 1.0))
LZ.data.shadow_soft_size = 0.002
fuertes = [FW(1, 23) + k * 7 for k in range(4)] + [E0 + 2, FW(1, 32) + 2]
CHF = BJ["chispas"](CP, RAIZ, M_["arco"], (0, 0, -0.00005), (0, 0, -BJ["GAP"] + 0.00005), fuertes, pref="BUJ_Chispa", luz=LZ, energia=10.0)
FUEGO = BJ["bola_fuego"](CP, RAIZ, M_["fuego"], (0, 0, -0.007), [E0 + 4, FW(1, 32) + 4])
LF = luz("D_LuzFuego", 'POINT', MPm() @ Vector((0, -0.012, -0.007)), MPm() @ Vector((0, 0, 0)), (1.0, 0.55, 0.15))
kluz(LF, [(1, 0)] + [x for f in (E0 + 4, FW(1, 32) + 4) for x in ((f - 1, 0), (f + 4, 45), (f + 16, 0))])
debiles = [FW(2, 9) + 2, FW(2, 9) + 11, FW(2, 11) + 4]
LZ2 = luz("D_LuzChispaDebil", 'POINT', MPm() @ Vector((0, -0.004, -0.0008)), MPm() @ Vector((0, 0, 0)), (1.0, 0.5, 0.2))
CHD = BJ["chispas"](CP, RAIZ, M_["arco_debil"], (0, 0, 0.00050), (0, 0, -BJ["GAP"] - 0.00045), debiles, pref="BUJ_ChispaDebil", n=2,
                    amp=0.00045, grosor=0.00005, luz=LZ2, energia=2.5)
# desgaste: la punta se redondea, el hueco crece y la cerámica se llena de hollín
MASA = O["masa"]; kl(MASA, 1, (0, 0, 0)); kl(MASA, FW(2, 3), (0, 0, 0)); kl(MASA, FW(2, 6, True) + 8, (0, 0, -0.00045))
kp("hollin", 1, 0.0); kp("hollin", FW(2, 3), 0.0); kp("hollin", FW(2, 6, True) + 10, 1.0); kp("hollin", A2, 1.0)
# el electrodo central (ya partido) se desgasta: se acorta la mitad que queda
ELF = bpy.data.objects.get("BUJ_Electrodo_Fondo")
if ELF is not None:
    me = ELF.data; ELF.shape_key_add(name="Basis", from_mix=False); kb2 = ELF.shape_key_add(name="gastado", from_mix=False)
    for i, v in enumerate(me.vertices):
        if v.co.z < 0.0012:
            s = max(0.6, 1 - (0.0012 - v.co.z) / 0.0012 * 0.4)
            kb2.data[i].co = Vector((v.co.x * s, v.co.y * s, v.co.z + 0.0005))
    for f_, v in ((1, 0.0), (FW(2, 3), 0.0), (FW(2, 6, True) + 8, 1.0)): kb2.value = v; kb2.keyframe_insert("value", frame=f_)

# ---------------------------------------------------------------- planos de la pieza (coordenadas de la bujía, x3 en el estudio)
cl(B0, (0.100, -0.165, 0.085), (0.0, 0.0, 0.044), 40); cl(C0 - 1, (0.090, -0.155, 0.080), (0.0, 0.0, 0.044), 41)
cl(C0, (0.060, -0.180, 0.055), (0.0, 0.0, 0.042), 40); cl(D0 - 1, (0.052, -0.165, 0.048), (0.0, 0.0, 0.036), 41)
cl(D0, (0.0110, -0.0280, 0.0035), (0.0, 0.0, -0.0005), 45); cl(E0 - 1, (0.0098, -0.0255, 0.0030), (0.0, 0.0, -0.0005), 46)
cl(E0, (0.035, -0.085, 0.006), (0.0, 0.0, -0.004), 40); cl(F0 - 1, (0.032, -0.078, 0.005), (0.0, 0.0, -0.004), 41)
cl(F0, (0.0115, -0.0285, 0.0040), (0.0, 0.0, -0.0004), 45); cl(A2 - 1, (0.0102, -0.0260, 0.0036), (0.0, 0.0, -0.0004), 46)
CAMS_INTRO = [
    (XR0 + 6, (-1.38, -1.55, 1.14), (-1.48, 0.62, 0.84), 40),
    (EST - 1, (-1.39, -1.45, 1.12), (-1.48, 0.62, 0.84), 41)] + \
    [(EST + 1 + k * 2, (-1.39 + dx, -1.47, 1.12 + dz), (-1.48, 0.62, 0.86), 41) for k, (dx, dz) in enumerate(((0.010, -0.007), (-0.008, 0.008), (0.005, -0.004)))] + [
    (EST + 16, (-1.52, -0.42, 1.02), (-1.63, 0.53, 0.97), 40),
    (F_ZAP, (-1.53, -0.36, 1.02), (-1.63, 0.53, 0.97), 41),
    (F_ZAP + 2, (-1.525, -0.37, 1.025), (-1.63, 0.53, 0.97), 41), (F_ZAP + 4, (-1.535, -0.355, 1.015), (-1.63, 0.53, 0.97), 41),
    (B0 - 1, (-1.53, -0.34, 1.02), (-1.63, 0.53, 0.97), 42)]
PUNTOS = {"bujia": (RAIZ, (0.0, -0.0052, 0.062)),
          "electrodo": (RAIZ, (0.0, -0.0003, 0.012)),
          "ceramica": (RAIZ, (0.0, -0.0048, 0.020)),
          "electrodos": (RAIZ, (0.0, -0.0006, -0.00045)),
          "chispa": (RAIZ, (0.0, -0.0006, -0.0045)),
          "gastado": (RAIZ, (0.0, -0.0005, 0.0006))}

# ---------------------------------------------------------------- gestos
G = {"pregunta": FW(0, 1), "clod": FW(0, 16), "plano_clod": FW(0, 7), "mira": FW(0, 12),
     "sintomas": [FW(2, 12), FW(2, 13), FW(2, 16)], "ojo": FW(3, 1), "manos": FW(3, 11)}
def gag_clod(CL):
    ft = FW(0, 2)                                        # el coche tiembla y Clod con él
    for k in range(16):
        d = 0.0025 * (1 if k % 2 == 0 else -1)
        CAR.location = (d * 0.6, 0.8 + d * 0.3, abs(d) * 0.4); CAR.keyframe_insert("location", frame=ft + k * 2)
        CL.cuerpo(ft + k * 2, 0, (2.5 if k % 2 == 0 else -2.5), 0)
    CAR.location = (0, 0.8, 0); CAR.keyframe_insert("location", frame=ft + 32); CAR.keyframe_insert("location", frame=1)
    CL.cuerpo(ft + 32, 0, 0, 0); CL.cara(ft, "duda")
    fe = EST + 8                                         # la bujía sale delante de él
    CL.cara(fe, "sorpresa"); CL.cabeza(fe, -6, 0, -24); CL.mirar(fe, -0.010, 0.004)
    fc = FW(0, 16)                                       # "Clod": acerca el dedo
    CL.cara(fc, "feliz"); CL.mano_en("R", fc + 4, (-0.30, -0.30, 0.74)); CL.codo_hacia("R", fc + 4, (-0.55, 0.0, 0.60)); CL.pulgar("R", fc + 4, 0.2)
    CL.mano_en("R", F_ZAP - 1, (-0.34, -0.36, 0.76))
    CL.cara(F_ZAP + 1, "susto"); CL.aplastar(F_ZAP + 1, 1.15); CL.aplastar(F_ZAP + 4, 0.85); CL.aplastar(F_ZAP + 10, 1.0)
    CL.salto(F_ZAP + 2, alto=0.10, aire=8)
    CL.mano_en("R", F_ZAP + 3, (-0.20, -0.10, 0.62)); CL.codo_hacia("R", F_ZAP + 3, (-0.55, 0.05, 0.50))
    # calambrazo: rayo del terminal de la bujía a la mano de Clod
    sc.frame_set(F_ZAP); bpy.context.view_layer.update()
    mano = CL.ctrl.get("mano_R") or next(iter(CL.ctrl.values()))
    pm = mano.matrix_world.translation.copy(); pt = RAIZ.matrix_world @ Vector((0, 0, BJ["Z_TERM"]))
    LZ3 = luz("D_LuzZap", 'POINT', (pm + pt) / 2, pt, (0.6, 0.8, 1.0))
    BJ["chispas"](CD, None, M_["arco"], pt, pm, [F_ZAP - 1, F_ZAP + 1], pref="BUJ_Zap", n=2, amp=0.012, grosor=0.0012, luz=LZ3, energia=60.0)

exec(_B[1])
