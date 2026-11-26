# REEL 26-11-2026 · ¿TE TIEMBLA EL VOLANTE A PARTIR DE 80? (equilibrado de ruedas) · 9:16, 30 fps, ~32,4 s
# Se ejecuta sobre una COPIA de alex_v2_rig.blend abierta. Carga taller_v2, Clod v2 y las funciones de animación.
# Voces (Alex = "Gonzalo"; Clod no habla). Inicio de cada frase (s): 0,20 · 4,30 · 10,70 · 17,60 · 26,40
# Textos y rótulos: se ponen en el montaje (Ootto), no aquí.
import bpy, math, json, os
from mathutils import Vector, Matrix, Euler
BASE = r"C:\Users\EKORUEDAS\Desktop\EKORUEDAS_ESTUDIO_3D"
D_ = BASE + r"\biblioteca"
TALLER = D_ + r"\taller_v2.py"; ANIM = D_ + r"\personajes\alex_anim.py"; ANIM_C = D_ + r"\personajes\clod_anim.py"
MODELO_C = D_ + r"\personajes\clod_v2.py"; CLOD_BLEND = D_ + r"\personajes\clod\clod_v2.blend"
VOCES = globals().get("VOCES_JSON")            # ruta a voces.json (la pone quien ejecuta)
sc = bpy.context.scene
R = math.radians
def F(t): return int(round(t * 30)) + 1
FIN = F(32.4)

# ---------------------------------------------------------------- taller, personajes y funciones
T_ = {"__name__": "taller"}; exec(open(TALLER, encoding="utf-8").read(), T_)
TT = T_["construir_taller"](); M = TT["M"]; COL = TT["col"]; T_["ajustes_render"](sc)
if "CLOD_v2" not in bpy.data.objects:
    with bpy.data.libraries.load(CLOD_BLEND, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c in ("CLOD_v2_personaje", "CLOD_v2_controles")]
    for c in dst.collections:
        if c.name not in sc.collection.children: sc.collection.children.link(c)
exec(open(ANIM, encoding="utf-8").read())
exec(open(ANIM_C, encoding="utf-8").read())
_m = {"__name__": "modelo"}; exec(open(MODELO_C, encoding="utf-8").read(), _m)
for n in ("Ciclorama",):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
caja, cilindro, mat, _obj = T_["caja"], T_["cilindro"], T_["mat"], T_["_obj"]
R_EXT, R_LL, ANCHO = T_["R_EXT"], T_["R_LLANTA"], T_["ANCHO"]
def col_nueva(n):
    c = bpy.data.collections.get(n)
    if c is None: c = bpy.data.collections.new(n); sc.collection.children.link(c)
    return c
CE = col_nueva("EQUILIBRADO")

# ================================================================ EQUILIBRADORA (la del taller, movida al primer plano)
EQ = bpy.data.objects["Equilibradora"]
EQ_POS = Vector((0.62, 0.30, 0.0)); EQ_GIRO = -70
EQ.location = EQ_POS; EQ.rotation_euler = (0, 0, R(EQ_GIRO))
for o in [o for o in bpy.data.objects if o.name.startswith("Equi_Rueda")]:
    bpy.data.objects.remove(o, do_unlink=True)
cap = bpy.data.objects.get("Equi_Capota")
if cap: cap.hide_render = True; cap.hide_set(True)          # capota levantada (fuera de cuadro)
# pantalla oscura con flechas naranjas (sin cifras)
pant = bpy.data.objects["Equi_Pantalla"]
pant.location = Vector(pant.location) + pant.rotation_euler.to_matrix() @ Vector((0, 0, 0.056))   # la pantalla estaba hundida en el panel
m_pant = mat("EQ_PantallaOscura", (0.01, 0.012, 0.016), rough=0.2, emis=0.4, ecol=(0.05, 0.12, 0.2))
pant.data.materials.clear(); pant.data.materials.append(m_pant)
m_fle = mat("EQ_FlechaNaranja", (1.0, 0.52, 0.0), rough=0.4, emis=5.0, ecol=(1.0, 0.52, 0.0))
def triangulo(nombre, cx, cy, ancho, alto, abajo=True):
    me = bpy.data.meshes.new(nombre)
    s = -1 if abajo else 1
    me.from_pydata([(cx - ancho / 2, cy - s * alto / 2, 0), (cx + ancho / 2, cy - s * alto / 2, 0), (cx, cy + s * alto / 2, 0)], [], [(0, 1, 2)])
    o = _obj(nombre, me, m_fle, CE, liso=False, padre=pant, loc=(0, 0, 0.0062)); return o
FLECHAS = [triangulo("EQ_FlechaIzq", -0.09, 0.0, 0.05, 0.06, True), triangulo("EQ_FlechaDer", 0.09, 0.0, 0.05, 0.06, False)]
barra = caja("EQ_Barra", (0, -0.055, 0.0062), (0.30, 0.012, 0.001), m_fle, col=CE, padre=pant)
FLECHAS.append(barra)

# rueda de alta calidad en un pivote que gira (eje = Z local del pivote = eje de la máquina)
PIV = bpy.data.objects.new("EQ_Pivote", None); CE.objects.link(PIV); PIV.parent = EQ
PIV.location = (0.48, 0, 0.82); PIV.rotation_euler = (0, R(90), 0)
BAM = bpy.data.objects.new("EQ_Bamboleo", None); CE.objects.link(BAM); BAM.parent = PIV
GIR = bpy.data.objects.new("EQ_Giro", None); CE.objects.link(GIR); GIR.parent = BAM
RUEDA = T_["rueda"]("EQ_Rueda", (0, 0, 0), (0, 0, 0), detalle="alto", M=M, col=CE, padre=GIR)

# perfil de giro (grados por fotograma) y desequilibrio
def omega(t):
    def rampa(a, b, v0, v1):
        x = min(1.0, max(0.0, (t - a) / (b - a))); x = x * x * (3 - 2 * x); return v0 + (v1 - v0) * x
    if t < 4.2: return 0.0
    if t < 4.7: return rampa(4.2, 4.7, 0, 18)
    if t < 11.0: return 18.0
    if t < 12.2: return rampa(11.0, 12.2, 18, 0)
    if t < 14.35: return 0.0
    if t < 14.8: return rampa(14.35, 14.8, 0, 18)
    if t < 16.6: return 18.0
    if t < 17.4: return rampa(16.6, 17.4, 18, 0)
    return 0.0
TH = {}; th = 0.0
for f in range(1, FIN + 1):
    th += omega((f - 1) / 30.0); TH[f] = th
A_DES = 0.010; T_DES = 1.2          # desequilibrio exagerado para que se vea (m y grados)
for f in range(1, FIN + 1):
    t = (f - 1) / 30.0; w = omega(t) / 18.0
    a = A_DES * w * w if t < 12.3 else 0.0; tl = T_DES * w * w if t < 12.3 else 0.0
    q = R(TH[f])
    BAM.location = (a * math.cos(q), a * math.sin(q), 0); BAM.keyframe_insert("location", frame=f)
    BAM.rotation_euler = (R(tl) * math.sin(q), -R(tl) * math.cos(q), 0); BAM.keyframe_insert("rotation_euler", frame=f)
    GIR.rotation_euler = (0, 0, q); GIR.keyframe_insert("rotation_euler", frame=f)

# contrapeso adhesivo: 4 bloquecitos de acero (2,5 x 1,2 x 0,4 cm) en el borde interior de la llanta, arriba al parar
m_cp = mat("EQ_Contrapeso", (0.55, 0.56, 0.58), rough=0.4, metal=0.85)
m_cinta = mat("EQ_Cinta", (0.08, 0.08, 0.09), rough=0.7)
CP = bpy.data.objects.new("EQ_Contrapeso", None); CE.objects.link(CP); CP.parent = RUEDA
F_PARADA = F(12.3)
ang0 = R(180) - R(TH[F_PARADA])          # en el pivote, "arriba" del mundo es el ángulo 180°
R_CP = R_LL - 0.016; Z_CP = 0.068
CP.location = (0, 0, Z_CP); CP.rotation_euler = (0, 0, ang0)
for k in range(4):
    a = (k - 1.5) * 0.0265 / R_CP
    b = caja(f"EQ_CP_{k}", (R_CP * math.cos(a), R_CP * math.sin(a), 0), (0.004, 0.025, 0.012), m_cp, bisel=0.0012, col=CE, padre=CP)
    b.rotation_euler = (0, 0, a)
cin = caja("EQ_CP_Cinta", (R_CP + 0.0025, 0, 0), (0.0012, 0.108, 0.012), m_cinta, col=CE, padre=CP)
F_CP = F(13.80)
for f_, s_, dz in ((1, 0.0, 0.05), (F_CP - 6, 0.0, 0.05), (F_CP - 5, 1.0, 0.05), (F_CP, 1.0, -0.002), (F_CP + 2, 1.0, 0.0)):
    CP.scale = (s_, s_, s_); CP.location = (0, 0, Z_CP + dz)
    CP.keyframe_insert("scale", frame=f_); CP.keyframe_insert("location", frame=f_)
# flechas de la pantalla: encendidas mientras mide y apagadas al terminar
for o in FLECHAS:
    for f_, s_ in ((1, 0.0), (F(11.2), 0.0), (F(11.35), 1.0), (F(12.1), 1.0), (F(12.25), 0.0), (F(12.5), 1.0), (F(14.2), 1.0), (F(14.3), 0.0)):
        o.scale = (s_, s_, s_); o.keyframe_insert("scale", frame=f_)

def mundo(o, local=(0, 0, 0)):
    bpy.context.view_layer.update(); return o.matrix_world @ Vector(local)
sc.frame_set(1)
W = mundo(PIV)                                                  # centro de la rueda
EJE = (PIV.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()   # hacia fuera de la máquina

# pila de neumáticos para Clod (detrás, a la derecha de la máquina)
PILA_POS = Vector((1.40, -0.55, 0.0))
T_["pila_neumaticos"]("Pila_Clod", tuple(PILA_POS), 3, M, CE, giro=0.3)
TOP_PILA = 3.02 * ANCHO                                          # 3 neumáticos tumbados
TABLA = caja("Pila_Tabla", tuple(PILA_POS + Vector((0, 0, TOP_PILA + 0.0125))), (0.50, 0.46, 0.025), M["madera"], bisel=0.003, col=CE)
TABLA.rotation_euler = (0, 0, 0.3)

# ================================================================ LUCES
def luz(n, tipo, loc, mira, color, size=1.0):
    o = bpy.data.objects.get(n)
    if o is None:
        o = bpy.data.objects.new(n, bpy.data.lights.new(n, tipo)); CE.objects.link(o)
    o.location = loc; o.data.color = color
    if tipo == 'AREA': o.data.size = size
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o
L_CL = luz("EQ_LuzClave", 'AREA', (-1.3, -2.6, 2.7), (0.3, 0.0, 1.2), (1.0, 0.93, 0.85), 1.8); L_CL.data.energy = 420
L_CO = luz("EQ_LuzContra", 'AREA', (1.2, 2.4, 2.6), (0.5, 0.2, 1.2), (0.7, 0.82, 1.0), 1.5); L_CO.data.energy = 500
L_MA = luz("EQ_LuzMacro", 'SPOT', tuple(W + EJE * 1.0 + Vector((-0.5, 0, 0.9))), tuple(W), (1.0, 0.95, 0.88))
L_MA.data.spot_size = R(45); L_MA.data.spot_blend = 0.5
for f_, v in ((1, 0), (F(4.40) - 1, 0), (F(4.40), 650), (F(17.45) - 1, 650), (F(17.45), 0)):
    L_MA.data.energy = v; L_MA.data.keyframe_insert("energy", frame=f_)

# ================================================================ PERSONAJES
ALEX_POS = Vector((0.0, -0.55, 0)); ALEX_GIRO = 15
sk = MALLA.data.shape_keys
if sk.animation_data and sk.animation_data.action: sk.animation_data.action = None
for o in bpy.data.objects:
    if o.name.startswith("CTRL_") and o.animation_data: o.animation_data_clear()
ALEX.animation_data_clear()
ALEX.location = ALEX_POS; ALEX.rotation_euler = (0, 0, R(ALEX_GIRO))
CL = ClodAnim()
for ob in [CL.arm] + list(CL.ctrl.values()) + CL.ojos + [CL.bocaob]:
    ob.animation_data_clear()
    if getattr(ob.data, "shape_keys", None) and ob.data.shape_keys.animation_data: ob.data.shape_keys.animation_data_clear()
def SX(l): return -1 if l == "R" else 1
todo_reposo(1); sc.frame_set(1); calibrar_palma()
for l in ("R", "L"): brazo_caido(l, 1)
def en_alex(p):                       # punto del mundo -> coordenadas de Alex
    bpy.context.view_layer.update(); return tuple(ALEX.matrix_world.inverted() @ Vector(p))
RUEDA_A = en_alex(W)

# Clod de pie sobre la pila (altura medida con un rayo)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
hit, loc_h, *_ = sc.ray_cast(dg, PILA_POS + Vector((0, 0, 2.0)), Vector((0, 0, -1)))
CLOD_POS = (PILA_POS.x, PILA_POS.y, (loc_h.z if hit else TOP_PILA + 0.025) - 0.002)
CLOD_GIRO = -40
for o_ in bpy.data.objects:
    if o_.name.startswith("T2_LuzTecho"): o_.data.energy = 170
CL.reposo(1); CL.mover(1, CLOD_POS, CLOD_GIRO)

# ---------------------------------------------------------------- ALEX
cara(1, "duda", 0.7); cabeza(1, 2, 0, -12); columna(1, 2, 0, -8)         # mira a cámara
# "¿Te tiembla el volante...?": manos como si cogiera un volante que tiembla
cabeza(F(0.35), 0, 0, -12)
for l in ("R", "L"):
    mano_en(l, F(0.45), (SX(l) * 0.20, -0.20, 1.02)); mano_pose(l, F(0.45), "relajada")        # anticipación (baja)
    mano_en(l, F(0.75), (SX(l) * 0.19, -0.33, 1.17)); codo_hacia(l, F(0.75), (SX(l) * 0.60, 0.10, 0.85)); mano_pose(l, F(0.75), "puño")
t = 0.80; i = 0
while t < 1.95:
    for l in ("R", "L"): mano_en(l, F(t), (SX(l) * 0.19 + (0.012 if i % 2 else -0.012), -0.33, 1.17 + (0.008 if i % 2 else 0)))
    t += 0.1; i += 1
cara(F(0.9), "duda"); cabeza(F(1.2), -3, 4, -12)
# "Puede ser una rueda desequilibrada": suelta el volante y señala la rueda (la cabeza va antes que la mano)
cabeza(F(2.05), 0, 0, 20); cara(F(2.1), "concentrado", 0.6)
for l in ("R", "L"): brazo_caido(l, F(2.15)); mano_pose(l, F(2.15), "relajada")
fp = senalar("L", F(2.2), dur=40, objetivo=RUEDA_A)
cabeza(F(3.6), 4, 0, 10); cara(F(3.6), "neutra")
# macros (Alex fuera de cuadro): reposo con capa viva
for l in ("R", "L"): brazo_caido(l, F(5.0))
cabeza(F(5.0), 6, 0, 22)
# "Si un contrapeso se pierde o se estropea, vuelve el desequilibrio": explica mirando a la rueda
cabeza(F(17.45), 6, 0, 22); cara(F(17.45), "concentrado", 0.5)
mano_en("L", F(17.7), (0.24, -0.06, 0.95))                                  # anticipación
mano_en("L", F(18.0), (0.30, -0.30, 1.12)); codo_hacia("L", F(18.0), (0.70, 0.15, 0.85)); mano_pose("L", F(18.0), "abierta")
orientar_mano("L", F(18.0), palma_hacia=(0, 0, 1), dedos_hacia=(0.6, -1, 0))
mano_en("L", F(19.5), (0.31, -0.31, 1.13))
cabeza(F(20.2), 4, 3, 30)                                                   # mira hacia Clod (la cabeza antes que el cuerpo)
ALEX.rotation_euler = (0, 0, R(ALEX_GIRO)); ALEX.keyframe_insert("rotation_euler", frame=F(20.45))
ALEX.rotation_euler = (0, 0, R(48)); ALEX.keyframe_insert("rotation_euler", frame=F(21.0))
ALEX.rotation_euler = (0, 0, R(48)); ALEX.keyframe_insert("rotation_euler", frame=F(25.45))
ALEX.rotation_euler = (0, 0, R(4)); ALEX.keyframe_insert("rotation_euler", frame=F(25.95))
ALEX.rotation_euler = (0, 0, R(ALEX_GIRO)); ALEX.keyframe_insert("rotation_euler", frame=1)
cara(F(20.6), "duda", 0.6)
# "Clod, ni te acerques": mano de stop hacia Clod
cabeza(F(21.05), 2, 2, 12); cara(F(21.15), "enfado", 0.55); columna(F(21.2), 0, 0, 10)
mano_en("L", F(21.15), (0.25, -0.20, 1.05))
mano_en("L", F(21.40), (0.32, -0.30, 1.30)); codo_hacia("L", F(21.40), (0.70, 0.20, 1.00)); mano_pose("L", F(21.40), "abierta")
orientar_mano("L", F(21.40), palma_hacia=(0.6, -0.8, 0.0), dedos_hacia=(0, 0, 1))
mano_en("L", F(22.2), (0.32, -0.31, 1.31))
# "Un contrapeso pesa unos gramos": pinza pequeña con los dedos
mano_en("L", F(22.5), (0.20, -0.30, 1.18)); mano_pose("L", F(22.5), "ok"); orientar_mano("L", F(22.5), palma_hacia=(0, -1, 0.3), dedos_hacia=(0, 0, 1))
mano_en("L", F(23.6), (0.21, -0.31, 1.19)); cara(F(22.6), "neutra")
# "Tú, bastante más": palma hacia Clod, media sonrisa pícara
mano_en("L", F(24.0), (0.30, -0.28, 1.12)); mano_pose("L", F(24.0), "abierta")
orientar_mano("L", F(24.0), palma_hacia=(0, 0, 1), dedos_hacia=(0.7, -0.7, 0))
cara(F(24.2), "picaro", 0.8); cabeza(F(24.3), -2, 4, 10)
mano_en("L", F(25.2), (0.31, -0.29, 1.13)); brazo_caido("L", F(25.6)); mano_pose("L", F(25.6), "relajada")
# consejo final, a cámara
cabeza(F(25.9), 2, 0, -8); columna(F(25.9), 2, 0, -6); cara(F(26.0), "neutra")
cabeza(F(27.6), 6, 0, -10); cabeza(F(27.9), 0, 0, -10)                     # asiente en "profesional"
mano_en("R", F(28.3), (-0.20, -0.06, 0.98))                                 # anticipación
mano_en("R", F(28.6), (-0.16, -0.32, 1.18)); codo_hacia("R", F(28.6), (-0.70, 0.10, 0.80)); mano_pose("R", F(28.6), "señalar")
orientar_mano("R", F(28.6), dedos_hacia=(0.3, -1, 0.1))
mano_en("R", F(29.9), (-0.16, -0.33, 1.19))
brazo_caido("R", F(30.5)); mano_pose("R", F(30.5), "relajada")
cara(F(30.2), "sonrisa", 0.55); cabeza(F(30.4), 3, -3, -10)
cara(FIN, "sonrisa", 0.6); cabeza(FIN, 3, -3, -10)

# ---------------------------------------------------------------- CLOD (no habla: solo gestos y pantalla)
CL.cara(1, "contento"); CL.cabeza(1, -6, 0, 0); CL.mirar(1, -0.01, 0.0)
for l in ("R", "L"): CL.brazo_caido(l, 1)
# P2: duda mirando la rueda
CL.cara(F(2.3), "duda"); CL.cabeza(F(2.4), -2, 10, 8); CL.mirar(F(2.3), -0.02, -0.01)
CL.mano_en("R", F(2.6), (-0.12, -0.20, 0.52)); CL.codo_hacia("R", F(2.6), (-0.60, 0.20, 0.35)); CL.pulgar("R", F(2.6), 0.3)   # se rasca la "barbilla"
CL.mano_en("R", F(3.8), (-0.12, -0.205, 0.53)); CL.brazo_caido("R", F(4.3))
# P6: intenta hacer de contrapeso: se inclina hacia la rueda con los brazos estirados
CL.cara(F(17.6), "serio"); CL.cabeza(F(17.6), 4, 0, 6); CL.mirar(F(17.6), -0.015, -0.012)
CL.cuerpo(F(17.9), -4, 0, 0)                                               # anticipación (se echa atrás)
CL.mano_en("R", F(18.4), (-0.40, -0.06, 0.56)); CL.codo_hacia("R", F(18.4), (-0.45, 0.40, 0.45)); CL.pulgar("R", F(18.4), 0.8)
CL.mano_en("L", F(18.4), (-0.12, -0.30, 0.54)); CL.codo_hacia("L", F(18.4), (0.40, -0.10, 0.40)); CL.pulgar("L", F(18.4), 0.8)
CL.mano_en("R", F(20.9), (-0.41, -0.07, 0.55)); CL.mano_en("L", F(20.9), (-0.13, -0.31, 0.53))
CL.cuerpo(F(18.4), 4, -16, -10); CL.cuerpo(F(19.3), 4, -22, -10); CL.cuerpo(F(20.2), 4, -17, -10); CL.cuerpo(F(20.9), 4, -21, -10)
CL.cabeza(F(18.4), 6, -6, -20)
CL.rebote(F(19.0), veces=2, alto=0.02, cada=8)
# "Clod, ni te acerques": susto con aplastar y estirar, se echa atrás y encoge
CL.cara(F(21.25), "susto"); CL.cuerpo(F(21.30), -8, 0, 0)
CL.aplastar(F(21.22), 1.0); CL.aplastar(F(21.32), 1.15); CL.aplastar(F(21.50), 0.93); CL.aplastar(F(21.65), 1.0)
for l in ("R", "L"):
    CL.mano_en(l, F(21.35), (SX(l) * 0.27, -0.10, 0.64)); CL.codo_hacia(l, F(21.35), (SX(l) * 0.75, 0.15, 0.45)); CL.pulgar(l, F(21.35), 1.0)
    CL.mano_en(l, F(22.1), (SX(l) * 0.16, -0.20, 0.45)); CL.codo_hacia(l, F(22.1), (SX(l) * 0.55, 0.10, 0.35)); CL.pulgar(l, F(22.1), 0.2)
CL.cuerpo(F(22.1), 4, 0, 0); CL.cara(F(22.2), "triste", 0.6)
# "Un contrapeso pesa unos gramos" -> asiente; "Tú" -> se mira la tripa; "bastante más" -> se tapa la cara
CL.cabeza(F(22.6), 8, 0, 6); CL.cabeza(F(22.9), -2, 0, 6); CL.cabeza(F(23.2), 8, 0, 6); CL.cabeza(F(23.5), 0, 0, 6)
CL.cabeza(F(24.0), 22, 0, 0); CL.mirar(F(24.0), 0.0, -0.025); CL.cara(F(24.05), "sorpresa", 0.7)
for l in ("R", "L"):
    CL.mano_en(l, F(24.35), (SX(l) * 0.10, -0.26, 0.76)); CL.codo_hacia(l, F(24.35), (SX(l) * 0.55, 0.05, 0.55)); CL.pulgar(l, F(24.35), 0.0)
    CL.mano_en(l, F(26.4), (SX(l) * 0.10, -0.265, 0.77))
CL.cabeza(F(24.35), 6, 0, 0); CL.cara(F(24.4), "triste")
CL.aplastar(F(24.35), 1.0); CL.aplastar(F(24.5), 0.9); CL.aplastar(F(24.75), 1.0)
# consejo: se destapa, duda y al final pulgar arriba con saltito
for l in ("R", "L"): CL.brazo_caido(l, F(26.9))
CL.cara(F(26.9), "duda"); CL.cabeza(F(26.9), -4, -8, -6); CL.mirar(F(26.9), 0.01, 0.0)
CL.cara(F(28.5), "feliz"); CL.cabeza(F(28.6), -6, 0, -10)
fpul = CL.pulgar_arriba("R", F(28.6), dur=40)
CL.rebote(F(30.4), veces=2, alto=0.025, cada=7)
CL.cara(FIN, "feliz")

# ---------------------------------------------------------------- voces, parpadeos, respiración, suavizado, CAPA VIVA
VOZ = json.load(open(VOCES, encoding="utf-8")) if VOCES and os.path.exists(VOCES) else []
LINEAS = [{"at": 0, "words": [[w, v["at"] + a, v["at"] + b] for (w, (a, b)) in zip(v["words"].split(), v["w"])]} for v in VOZ if v.get("who") == "Alex"]
hablar(LINEAS)
parpadeos(1, FIN, evitar=(F(2.1), F(21.2), F(24.2)))
CL.parpadeos(1, FIN, cada=(55, 85), evitar=[(F(21.2), F(22.0)), (F(24.3), F(26.5))])
respirar(1, FIN, periodo=64, amplitud=1.5)
suavizar(); CL.suavizar()
ad = sk.animation_data
if ad and ad.action:
    try: cv = list(ad.action.fcurves)
    except Exception: cv = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
    for fc in cv:
        for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
        fc.update()
CAPA_VIVA = globals().get("CAPA_VIVA", True)
capa_viva(activa=CAPA_VIVA); CL.respirar(activa=CAPA_VIVA)
for o_ in (BAM, GIR):
    for fc in (o_.animation_data.action.fcurves if hasattr(o_.animation_data.action, "fcurves") else []):
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'

# ================================================================ CÁMARA: 9 planos
cam = bpy.data.objects.get("CAM")
if cam is None:
    cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam)
cam.animation_data_clear(); cam.data.animation_data_clear()
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.03
cam.data.dof.use_dof = False
def ck(f, loc, t, lens):
    cam.location = loc; cam.rotation_euler = (Vector(t) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
A_CAB = mundo(ALEX, (0, -0.05, 1.55))
CORTES = [1, F(2.18), F(4.40), F(10.55), F(12.45), F(14.33), F(17.45), F(21.18), F(25.60), FIN + 1]
PANT = mundo(pant); NPANT = (pant.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
LADO = Vector((EJE.y, -EJE.x, 0)).normalized()     # perpendicular al eje, en horizontal
if LADO.y > 0: LADO = -LADO
PLANOS = [
    # 1 gancho: Alex de cerca, acercándose
    [((0.10, -2.10, 1.55), (0.0, -0.55, 1.42), 40), ((0.10, -1.92, 1.55), (0.0, -0.55, 1.44), 40)],
    # 2 Alex, la equilibradora y Clod en la pila
    [((0.62, -3.70, 1.20), (0.62, -0.20, 0.92), 22), ((0.62, -3.55, 1.20), (0.62, -0.20, 0.93), 22)],
    # 3 macro: la rueda gira y salta (desequilibrio)
    [(tuple(W + EJE * 1.50 + LADO * 0.35 + Vector((0, 0, 0.25))), tuple(W), 38), (tuple(W + EJE * 1.38 - LADO * 0.12 + Vector((0, 0, 0.20))), tuple(W), 38)],
    # 4a pantalla con flechas
    [(tuple(PANT + NPANT * 0.72), tuple(PANT), 30), (tuple(PANT + NPANT * 0.66), tuple(PANT), 30)],
    # 4b la llanta parada: el contrapeso arriba
    [(tuple(W + EJE * 0.62 + Vector((0, 0, 0.24))), tuple(W + Vector((0, 0, 0.17))), 40), (tuple(W + EJE * 0.56 + Vector((0, 0, 0.24))), tuple(W + Vector((0, 0, 0.175))), 40)],
    # 5 gira redonda (plano algo más abierto)
    [(tuple(W + EJE * 1.70 + LADO * 0.70 + Vector((0, 0, 0.45))), tuple(W + Vector((0, 0, -0.05))), 30), (tuple(W + EJE * 1.62 + LADO * 0.45 + Vector((0, 0, 0.40))), tuple(W + Vector((0, 0, -0.05))), 30)],
    # 6 plano general bajo: Alex, máquina parada y Clod en la pila
    [((0.65, -3.60, 0.85), (0.65, -0.30, 0.95), 22), ((0.65, -3.45, 0.88), (0.65, -0.30, 0.96), 22)],
    # 7 los dos: Alex en primer término a la izquierda, Clod detrás a la derecha
    [((-1.30, -2.25, 1.30), (0.95, -0.45, 0.98), 24), ((-1.22, -2.15, 1.30), (0.95, -0.45, 0.99), 24)],
    # 8 cierre: los dos, acercándose
    [((0.62, -3.30, 1.25), (0.66, -0.40, 1.02), 22), ((0.62, -3.10, 1.27), (0.66, -0.40, 1.05), 22)],
]
for i, claves in enumerate(PLANOS):
    (p0, t0, l0), (p1, t1, l1) = claves
    ck(CORTES[i], p0, t0, l0); ck(CORTES[i + 1] - 1, p1, t1, l1)
def _curvas(idb):
    ad_ = getattr(idb, "animation_data", None)
    if not ad_ or not ad_.action: return []
    try: return list(ad_.action.fcurves)
    except Exception: return [fc for l in ad_.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
fin_plano = {c - 1 for c in CORTES[1:]}
for idb in (cam, cam.data):
    for fc in _curvas(idb):
        for k in fc.keyframe_points:
            k.interpolation = 'CONSTANT' if int(round(k.co[0])) in fin_plano else 'BEZIER'
            k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
        fc.update()
for o_ in (BAM, GIR):
    for fc in _curvas(o_):
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
        fc.update()

sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 67
sc.eevee.taa_render_samples = 48; sc.render.fps = 30; sc.frame_start, sc.frame_end = 1, FIN
try: sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45; sc.render.motion_blur_position = 'START'
except Exception: pass
sc.view_settings.exposure = -0.45
_m["brillo_led"](sc, umbral=6.0)

# ---------------------------------------------------------------- comprobación del encuadre por plano
def comprobar_encuadre(margen=0.012):
    from bpy_extras.object_utils import world_to_camera_view as w2c
    alex_pts = ["RightHandMiddle3", "LeftHandMiddle3"]
    clod_ob = [bpy.data.objects[n] for n in ("CLOD_Mano_R", "CLOD_Mano_L", "CLOD_Casco_R", "CLOD_Casco_L", "CLOD_Diadema")]
    quien = {0: ("A",), 1: ("A", "C"), 5: (), 2: (), 3: (), 4: (), 6: ("A", "C"), 7: ("A", "C"), 8: ("A", "C")}
    malos = []
    for f_ in range(sc.frame_start, sc.frame_end + 1, 2):
        plano = max(i for i, c in enumerate(CORTES[:-1]) if f_ >= c)
        if not quien[plano]: continue
        sc.frame_set(f_); pts = []
        if "A" in quien[plano]:
            mw = ALEX.matrix_world
            for b in alex_pts:
                w_ = mw @ PB["mixamorig:" + b].tail
                if w_.z > 1.02: pts.append(("A_" + b, w_))
            pts.append(("A_cabeza", mw @ (PB["mixamorig:Head"].tail + Vector((0, 0, 0.02)))))
        if "C" in quien[plano]:
            pts += [("C_" + o.name, o.matrix_world.translation) for o in clod_ob]
        for n, w_ in pts:
            c = w2c(sc, cam, w_)
            if c.x < margen or c.x > 1 - margen or c.y > 1 - margen or c.y < margen: malos.append((f_, plano + 1, n, round(c.x, 3), round(c.y, 3)))
    return malos
malos = comprobar_encuadre()
json.dump({"fin": FIN, "cortes": CORTES, "W": list(W), "eje": list(EJE), "clod": list(CLOD_POS)},
          open(os.path.join(os.path.dirname(bpy.data.filepath) or BASE, "escena_info.json"), "w"))
result = {"ok": True, "fin": FIN, "cortes": CORTES, "W": [round(x, 3) for x in W], "eje": [round(x, 3) for x in EJE],
          "clod": [round(x, 3) for x in CLOD_POS], "hit": bool(hit), "fuera": len(malos), "ejemplos": malos[:20]}
