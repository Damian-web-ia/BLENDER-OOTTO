# DESPIECE 3D DE LA BATERÍA (27-11-2026, para publicar el 28-11) · vertical 9:16, 30 fps, ~30,4 s
# Gancho de invierno: "¿A tu coche le cuesta arrancar cuando hace frío? Como a Clod por las mañanas."
# Clod tirita en el capó -> rayos X -> la batería sale volando -> se van la tapa y la pared de delante: 6 celdas ->
# el elemento de la celda 1 sube y abre sus placas (positivas marrones, negativas grises) -> vuelve al ácido ->
# burbujas y corriente que recorre las 6 celdas hasta el borne + (12 V) -> FRÍO: escarcha, todo va más lento ->
# Alex: síntomas -> inserto nueva frente a gastada (sulfato en los bornes) -> "duran entre 3 y 5 años" -> síguenos.
# Escena: abrir antes biblioteca\personajes\alex\alex_v2_rig.blend. Usa plantillas\despiece_base.py.
BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
NOMBRE = "bateria"; DD = BASE + r"\videos_3d\despiece_bateria"
_B = open(BASE + r"\plantillas\despiece_base.py", encoding="utf-8").read().split("# ==== PARTE 2 ====")
exec(_B[0])
R = math.radians

# ---------------------------------------------------------------- tiempos (salen de la voz)
XR0 = FW(0, 15) - 4                 # "Mira": rayos X al capó
EST = FW(0, 18)                     # "pasa": la batería sale disparada
B0 = FW(1, 0)                       # "La batería..."
F_ABRE = FW(1, 3) - 6               # "seis celdas": se van la tapa y la pared de delante
C0 = FW(1, 5)                       # "En cada una": el elemento sube y abre las placas
F_BANA = FW(1, 11)                  # "bañadas en ácido": vuelve a su celda
D0 = FW(1, 14)                      # "Al reaccionar": burbujas y corriente
E0 = FW(1, 22)                      # "Pero con frío": escarcha y todo más lento
A2 = FW(2, 0)                       # consejo de Alex
INS = FW(2, 12)                     # "aparece polvo blanco en los bornes": inserto nueva / gastada
A3 = FW(3, 0)                       # "Ojo: duran entre 3 y 5 años"
CTA = FL(3) + 10
FIN = CTA + 66
CORTES = [1, B0, C0, D0, E0, A2, INS, A3, CTA, FIN + 1]
EV = {"XR0": XR0, "F_ABRE": F_ABRE, "C0": C0, "F_BANA": F_BANA, "D0": D0, "E0": E0}

# ---------------------------------------------------------------- la batería
BT = {"__name__": "bt"}; exec(open(D_ + r"\bateria_real.py", encoding="utf-8").read(), BT)
CP = col_pieza("BATERIA")
O = BT["construir_bateria"](CP, MP, "BAT", interior=True, gastada=False)
RAIZ = O["raiz"]; RAIZ.rotation_mode = 'XYZ'
E_POS = Vector((-1.55, 0.42, 0.45)); ALTO = 0.21; ESC_P = 1.0
P = Vector((-1.30, -1.05, 0.66)); ROTP = (0, 0, R(-24))
for o in list(CD.all_objects): pass
vuelo(RAIZ, EST, B0 - 2, esc_coche=1.0, rot_coche=(0, 0, 0), alto_salida=0.42)
TAPA = O["tapa_grupo"]; FRENTE = O["frente"]; ELEM = O["elemento"]
kl(TAPA, 1, (0, 0, 0), (0, 0, 0)); kl(TAPA, F_ABRE, (0, 0, 0), (0, 0, 0))
kl(TAPA, F_ABRE + 8, (-0.01, 0.06, 0.16), (R(-12), 0, R(4))); kl(TAPA, F_ABRE + 18, (-0.06, 0.34, 0.42), (R(-38), R(6), R(14)))
vis(TAPA, 1, True); vis(TAPA, F_ABRE + 19, False)
kl(FRENTE, 1, (0, 0, 0), (0, 0, 0)); kl(FRENTE, F_ABRE + 3, (0, 0, 0), (0, 0, 0))
kl(FRENTE, F_ABRE + 18, (0.03, -0.38, -0.12), (R(55), 0, R(-18)))
vis(FRENTE, 1, True); vis(FRENTE, F_ABRE + 19, False)
# el elemento de la celda 1 sube, abre las placas y vuelve al ácido
kl(ELEM, 1, (0, 0, 0)); kl(ELEM, C0 + 2, (0, 0, 0)); kl(ELEM, C0 + 20, (0, 0, 0.17))
kl(ELEM, F_BANA - 4, (0, 0, 0.17)); kl(ELEM, FW(1, 13) + 6, (0, 0, 0))
for i, pl in enumerate(O["placas_e1"]):
    d = (i - (len(O["placas_e1"]) - 1) / 2) * 0.012
    kl(pl, 1, (0, 0, 0), (0, 0, 0)); kl(pl, C0 + 20, (0, 0, 0), (0, 0, 0))
    kl(pl, C0 + 34, (d, 0, 0), (0, 0, R(d * 140))); kl(pl, F_BANA - 6, (d, 0, 0), (0, 0, R(d * 140)))
    kl(pl, F_BANA + 6, (0, 0, 0), (0, 0, 0))
# reacción: burbujas y corriente (con frío, más despacio)
F_FRIO = E0 + 10
BUR = BT["burbujas"](CP, RAIZ, O["M"], D0, A2 - 1, F_FRIO, lento=0.3, n=70)
CORR = BT["corriente"](CP, RAIZ, O["M"], BT["camino_corriente"](O), D0 + 4, A2 - 1, F_FRIO, lento=0.3, n=24, vueltas=36)
ke(O["M"]["chispa"], 1, 45.0); ke(O["M"]["chispa"], F_FRIO, 45.0); ke(O["M"]["chispa"], F_FRIO + 30, 7.0)
kp("frio", 1, 0.0); kp("frio", E0 + 4, 0.0); kp("frio", E0 + 44, 1.0); kp("frio", A2 - 1, 1.0); kp("frio", A2, 0.0)
PCb = P + Vector((0, 0, 0.10))
LF = luz("D_LuzFrio", 'AREA', PCb + Vector((-0.55, -0.55, 0.35)), PCb, (0.45, 0.70, 1.0), 0.8)
kluz(LF, [(1, 0), (E0 + 4, 0), (E0 + 34, 140), (A2 - 1, 140), (A2, 0)])

# ---------------------------------------------------------------- inserto: nueva frente a gastada (sulfato en los bornes)
COLI = col_pieza("BATERIA_INSERTO")
DQ = Vector((-0.50, -0.26, 0.14)).normalized(); RQ = Vector((-DQ.y, DQ.x, 0)).normalized()
ANG = math.atan2(DQ.y, DQ.x) + math.pi / 2
INS_DIST = 0.95
for clave, pref, lado, gast in (("AN", "BATN", -1, False), ("AG", "BATG", 1, True)):
    o2 = BT["construir_bateria"](COLI, MP, pref, interior=False, gastada=gast)
    r_ = o2["raiz"]; r_.rotation_mode = 'XYZ'; r_.scale = (0.45, 0.45, 0.45); r_.rotation_euler = (0, 0, ANG)
    r_.location = Q + RQ * (0.066 * lado) - Vector((0, 0, 0.034))
    INSERTO[clave] = (r_, Vector((o2["XB"][1], o2["XB"][2], BT["Z_BORNE1"] + 0.01)))

# ---------------------------------------------------------------- planos de la pieza (coordenadas de la batería)
cl(B0, (0.44, -0.66, 0.36), (0.0, 0.0, 0.10), 38); cl(C0 - 1, (0.36, -0.62, 0.36), (0.0, 0.0, 0.10), 39)
cl(C0, (-0.38, -0.36, 0.36), (-0.10, 0.0, 0.21), 40); cl(F_BANA - 2, (-0.35, -0.35, 0.33), (-0.10, 0.0, 0.19), 41)
cl(D0 - 1, (-0.33, -0.34, 0.26), (-0.09, 0.0, 0.13), 43)
cl(D0, (0.12, -0.44, 0.33), (0.03, 0.0, 0.13), 36); cl(E0 - 1, (0.16, -0.40, 0.32), (0.05, 0.0, 0.13), 38)
cl(E0, (0.31, -0.47, 0.24), (0.0, 0.0, 0.09), 38); cl(A2 - 1, (0.27, -0.43, 0.23), (0.0, 0.0, 0.09), 39)
XBN, XBP, YB = O["XB"]
PUNTOS = {"bateria": (RAIZ, (0.06, -BT["LY"] / 2, 0.15)),
          "placas": (O["placas_e1"][4], (BT["celda_x"](0)[0] + 0.02, -0.03, 0.08)),
          "acido": (RAIZ, tuple(O["celdas"][2] + Vector((0, -0.05, -0.05)))),
          "electricidad": (RAIZ, ((BT["celda_x"](2)[0] + BT["celda_x"](2)[1]) / 2, -BT["Y_PUENTE"], 0.15)),
          "voltios": (O["bornes"]["+"], (XBP, YB, BT["Z_BORNE1"])),
          "frio": (RAIZ, (BT["LX"] / 2, -0.03, 0.12))}
for k, c in enumerate(O["celdas"]): PUNTOS[f"c{k + 1}"] = (RAIZ, tuple(c + Vector((0, -0.06, 0.0))))

# ---------------------------------------------------------------- gestos
G = {"pregunta": FW(0, 1), "clod": FW(0, 11), "plano_clod": FW(0, 9), "mira": FW(0, 15), "sintomas": [FW(2, 5), FW(2, 9)], "ojo": FW(3, 0), "manos": FW(3, 13)}
def gag_clod(CL):
    f0 = FW(0, 9) - 6                                    # tirita de frío abrazándose (su plano empieza en "Como a Clod")
    CL.cara(f0, "triste")
    for l in ("R", "L"):
        CL.mano_en(l, f0, (-SX(l) * 0.12, -0.22, 0.55)); CL.codo_hacia(l, f0, (SX(l) * 0.45, -0.05, 0.50))
    for k in range(16): CL.cuerpo(f0 + k * 2, 0, (3 if k % 2 == 0 else -3), 0)
    CL.cuerpo(f0 + 34, 0, 0, 0)
    fcl = FW(0, 13)                                      # "por las mañanas": se estira medio dormido
    CL.cara(fcl, "duda"); CL.cabeza(fcl, 20, 6, 10); CL.aplastar(fcl, 1.0); CL.aplastar(fcl + 8, 0.93)
    for l in ("R", "L"):
        CL.mano_en(l, fcl + 6, (SX(l) * 0.28, -0.02, 0.88)); CL.codo_hacia(l, fcl + 6, (SX(l) * 0.55, 0.05, 0.62))
    fm = FW(0, 15)                                       # "Mira": se despierta y mira el capó
    for l in ("R", "L"): CL.brazo_caido(l, fm)
    CL.aplastar(fm, 1.0); CL.cara(fm, "sorpresa"); CL.cabeza(fm, 26, 0, 0); CL.mirar(fm, 0.0, -0.012)
def gag_consejo(CL):                                     # "aparece polvo blanco": se tapa la nariz (asco)
    pass

exec(_B[1])
