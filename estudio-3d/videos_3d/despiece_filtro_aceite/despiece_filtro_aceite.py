# DESPIECE 3D DEL FILTRO DE ACEITE (27-11-2026, para publicar el 29-11) · vertical 9:16, 30 fps, ~27,7 s
# "¿Sabes dónde acaba toda la porquería de tu motor? No, Clod, en ti no. Aquí, en el filtro de aceite."
# Rayos X -> el filtro sale volando -> se parte por la mitad -> el aceite sucio entra por los agujeros (la goma antirretorno
# se levanta) -> atraviesa el papel plisado, que se queda la suciedad -> sale limpio por el centro (dorado) -> la goma
# antirretorno se cierra al parar el motor -> el papel se atasca (negro) -> se abre la válvula de derivación y la suciedad
# baja directa por la rosca, con luz roja -> inserto: papel nuevo frente a atascado -> "cambia también el filtro" -> síguenos.
BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
NOMBRE = "filtro"; DD = BASE + r"\videos_3d\despiece_filtro_aceite"
_B = open(BASE + r"\plantillas\despiece_base.py", encoding="utf-8").read().split("# ==== PARTE 2 ====")
exec(_B[0])
R = math.radians

# ---------------------------------------------------------------- tiempos
XR0 = FW(0, 14) - 4                 # "Aquí": rayos X
EST = FW(0, 17)                     # "filtro": sale volando
B0 = FW(1, 0)
F_CORTE = B0 + 8                    # se parte por la mitad
C0 = FW(1, 3)                       # "entra por estos agujeros"
D0 = FW(1, 7)                       # "atraviesa el papel plisado"
E0 = FW(1, 15)                      # "y sale limpio por el centro"
F0 = FW(1, 21)                      # "Esta goma es la válvula antirretorno"
F_PARA = FW(1, 27)                  # "deja aceite dentro": se para el motor
G0 = FW(2, 0)                       # "Pero si el filtro está atascado"
H0 = FW(2, 7)                       # "se abre la válvula de derivación"
I0 = FW(2, 18)                      # "directo al motor"
A2 = INS = FW(3, 0)                 # inserto: papel nuevo / atascado
A3 = FW(3, 8)                       # "cambia también el filtro"
CTA = FL(3) + 10
FIN = CTA + 66
CORTES = [1, B0, C0, D0, E0, F0, G0, H0, I0, A2, A3, CTA, FIN + 1]
EV = {"XR0": XR0, "F_CORTE": F_CORTE, "C0": C0, "D0": D0, "E0": E0, "F0": F0, "F_PARA": F_PARA, "G0": G0, "H0": H0, "I0": I0}

# ---------------------------------------------------------------- el filtro
FA = {"__name__": "fa"}; exec(open(D_ + r"\filtro_aceite_real.py", encoding="utf-8").read(), FA)
CP = col_pieza("FILTRO")
O = FA["construir_filtro"](CP, MP, "FIL", interior=True)
RAIZ = O["raiz"]; RAIZ.rotation_mode = 'XYZ'
E_POS = Vector((-1.50, 0.55, 0.40)); ALTO = 0.09; ESC_P = 2.4
P = Vector((-1.30, -1.05, 0.62)); ROTP = (0, 0, R(-24))
vuelo(RAIZ, EST, B0 - 2, esc_coche=1.0, rot_coche=(0, 0, 0), alto_salida=0.55)
# corte por la mitad: la mitad de delante sale volando
FRENTE = bpy.data.objects.new("FIL_Frente", None); CP.objects.link(FRENTE); FRENTE.parent = RAIZ
partir([O[k] for k in ("lata", "reborde", "placa", "cuello", "junta", "tapas", "papel", "tubo", "agujeros", "aceite_sucio", "aceite_limpio")],
       FRENTE, solo_fondo=("FIL_AceiteSucio", "FIL_AceiteLimpio", "FIL_Agujeros"), sin_tapa=("FIL_AceiteSucio", "FIL_AceiteLimpio", "FIL_Papel", "FIL_Agujeros"))
kl(FRENTE, 1, (0, 0, 0), (0, 0, 0)); kl(FRENTE, F_CORTE, (0, 0, 0), (0, 0, 0))
kl(FRENTE, F_CORTE + 16, (0.03, -0.11, -0.03), (R(-30), R(12), R(25)))
vis(FRENTE, 1, True); vis(FRENTE, F_CORTE + 17, False)
# antirretorno: se levanta con el aceite entrando y se cierra al parar el motor
kb = bpy.data.objects["FIL_Antirretorno"].data.shape_keys.key_blocks["abierta"]
for f_, v in ((1, 0.0), (C0 - 3, 0.0), (C0 + 5, 1.0), (F_PARA + 2, 1.0), (F_PARA + 10, 0.0), (G0 + 4, 0.0), (G0 + 12, 0.8)):
    kb.value = v; kb.keyframe_insert("value", frame=f_)
# suciedad que entra y se queda en el papel; aceite limpio que sale por el centro (se para con el motor)
GR = FA["granos_sucios"](CP, RAIZ, O["M"], O["angulos_agujeros"], C0 - 4, F_PARA, n=60)
GR2 = FA["granos_sucios"](CP, RAIZ, O["M"], O["angulos_agujeros"], G0, H0 + 10, n=30, semilla=11, pref="FIL2")
LI = FA["chispas_limpias"](CP, RAIZ, O["M"], E0 - 8, F_PARA + 2, n=26)
LI2 = FA["chispas_limpias"](CP, RAIZ, O["M"], G0 + 2, H0, n=10, semilla=9, pref="FIL3", periodo=70)
# atascado: el papel se pone negro; se abre la derivación y la suciedad baja directa
kp("sucio", 1, 0.0); kp("sucio", G0, 0.0); kp("sucio", FW(2, 5, True) + 8, 1.0); kp("sucio", A2, 1.0)
BY = O["bypass"]
kl(BY, 1, (0, 0, 0)); kl(BY, H0 - 2, (0, 0, 0)); kl(BY, H0 + 7, (0, 0, -0.0042))
CH = FA["chorro_bypass"](CP, RAIZ, O["M"], H0 + 6, A2, n=40)
ROJA = luz("D_LuzAlarma", 'POINT', MPm() @ Vector((0, -0.01, -0.02)), MPm() @ Vector((0, 0, 0)), (1.0, 0.15, 0.06))
kluz(ROJA, [(1, 0), (FW(2, 15) - 2, 0), (FW(2, 15) + 6, 60), (A2 - 1, 60), (A2, 0)])
ke(O["M"]["alarma"], 1, 6.0)

# ---------------------------------------------------------------- inserto: papel nuevo frente a atascado
COLI = col_pieza("FILTRO_INSERTO")
DQ = Vector((-0.50, -0.26, 0.14)).normalized(); RQ = Vector((-DQ.y, DQ.x, 0)).normalized()
ANG = math.atan2(DQ.y, DQ.x) + math.pi / 2
INS_DIST = 0.86
for clave, pref, lado, suc in (("AN", "FILN", -1, 0.0), ("AG", "FILG", 1, 1.0)):
    o2 = FA["construir_filtro"](COLI, MP, pref, solo_elemento=True, papel_sucio=suc)
    r_ = o2["raiz"]; r_.rotation_mode = 'XYZ'; r_.scale = (1.8, 1.8, 1.8); r_.rotation_euler = (0, 0, ANG)
    r_.location = Q + RQ * (0.072 * lado) - Vector((0, 0, 0.078))
    INSERTO[clave] = (r_, Vector((0.0, -FA["R_PAP1"], FA["Z_PAP1"] + 0.003)))

# ---------------------------------------------------------------- planos de la pieza (coordenadas del filtro, x2,4 en el estudio)
cl(B0, (0.115, -0.165, 0.105), (0.0, 0.0, 0.045), 40); cl(C0 - 1, (0.10, -0.155, 0.10), (0.0, 0.0, 0.045), 41)
cl(C0, (0.030, -0.080, 0.024), (0.0, 0.012, 0.005), 40); cl(D0 - 1, (0.026, -0.074, 0.022), (0.0, 0.012, 0.005), 42)
cl(D0, (0.055, -0.092, 0.062), (0.0, 0.012, 0.044), 42); cl(E0 - 1, (0.045, -0.083, 0.058), (0.0, 0.012, 0.044), 44)
cl(E0, (0.020, -0.082, 0.046), (0.0, 0.004, 0.030), 44); cl(F0 - 1, (0.016, -0.075, 0.040), (0.0, 0.004, 0.024), 45)
cl(F0, (0.036, -0.062, 0.030), (0.0, 0.014, 0.006), 46); cl(G0 - 1, (0.032, -0.057, 0.027), (0.0, 0.014, 0.006), 47)
cl(G0, (0.105, -0.150, 0.095), (0.0, 0.0, 0.045), 40); cl(H0 - 1, (0.095, -0.140, 0.092), (0.0, 0.0, 0.048), 41)
cl(H0, (0.030, -0.072, 0.100), (0.0, 0.003, 0.074), 46); cl(I0 - 1, (0.026, -0.066, 0.094), (0.0, 0.003, 0.068), 47)
cl(I0, (0.050, -0.105, -0.032), (0.0, 0.004, 0.0), 40); cl(A2 - 1, (0.045, -0.095, -0.028), (0.0, 0.004, 0.0), 41)
PUNTOS = {"filtro": (RAIZ, (0.0, -FA["R_LATA"], 0.060)),
          "agujeros": (RAIZ, (0.0, 0.022, 0.0046)),
          "papel": (RAIZ, (0.012, 0.028, 0.050)),
          "suciedad": (RAIZ, (-0.014, 0.029, 0.035)),
          "limpio": (RAIZ, (0.0, 0.004, 0.030)),
          "antirretorno": (RAIZ, (0.012, 0.022, 0.0065)),
          "bypass": (RAIZ, (0.0, 0.0, FA["Z_TAPA_SUP"] + 0.002)),
          "salida": (RAIZ, (0.0, 0.0, -0.010))}

# ---------------------------------------------------------------- gestos
G = {"pregunta": FW(0, 0), "clod": FW(0, 10), "plano_clod": FW(0, 5), "mira": FW(0, 14), "sintomas": [], "ojo": A3, "manos": None}
def gag_clod(CL):
    fp = FW(0, 5)                                        # "porquería": se mira a sí mismo
    CL.cara(fp, "duda"); CL.cabeza(fp, 22, 0, 0); CL.mirar(fp, 0.0, -0.012)
    CL.mano_en("R", fp, (-0.05, -0.22, 0.55)); CL.codo_hacia("R", fp, (-0.45, 0.0, 0.50))
    fn = FW(0, 9)                                        # "No, Clod": ¿yo?
    CL.cara(fn, "sorpresa"); CL.cabeza(fn, -6, 0, 0); CL.mirar(fn, 0.0, 0.0)
    for l in ("R", "L"):
        CL.mano_en(l, fn, (SX(l) * 0.20, -0.24, 0.70)); CL.codo_hacia(l, fn, (SX(l) * 0.55, 0.0, 0.52))
    fa = FW(0, 12)                                       # "en ti no": alivio, se limpia la frente
    CL.cara(fa, "risa"); CL.brazo_caido("L", fa)
    CL.mano_en("R", fa + 3, (-0.06, -0.16, 0.86)); CL.codo_hacia("R", fa + 3, (-0.50, 0.0, 0.72))
    CL.aplastar(fa, 1.0); CL.aplastar(fa + 5, 0.92); CL.aplastar(fa + 12, 1.0)
    fq = FW(0, 14)                                       # "Aquí": mira al capó
    for l in ("R", "L"): CL.brazo_caido(l, fq)
    CL.cara(fq, "sorpresa"); CL.cabeza(fq, 26, 0, 0); CL.mirar(fq, 0.0, -0.012)

exec(_B[1])
