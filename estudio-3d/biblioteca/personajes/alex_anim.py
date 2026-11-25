# ALEX v2 · FUNCIONES DE ANIMACIÓN (exec() después de cargar alex_v2_rig.blend o su colección)
# Unidades: metros y grados, en el espacio del personaje (mira hacia -Y):
#   +X = izquierda del personaje, -Y = adelante, +Z = arriba.  Lado "R" = derecho, "L" = izquierdo.
# Todo se anima con fotogramas clave (curvas Bézier suaves). Brazos y piernas por IK.
import bpy, math, json
from mathutils import Vector, Quaternion, Euler, Matrix

R = math.radians
ALEX = bpy.data.objects.get("ALEX_v2")
PB = ALEX.pose.bones
S = ALEX.matrix_world.to_scale()[0] if ALEX.parent is None else 1.0
S = ALEX.scale[0]

def B(n): return PB["mixamorig:" + n]
def C(n): return bpy.data.objects["CTRL_" + n]

# posiciones de reposo de los controles (se guardan la primera vez)
if "reposo_ctrl" not in ALEX:
    ALEX["reposo_ctrl"] = json.dumps({o.name: list(o.location) for o in bpy.data.objects if o.name.startswith("CTRL_")})
REPOSO = {k: Vector(v) for k, v in json.loads(ALEX["reposo_ctrl"]).items()}

def _k(obj, f, path):
    obj.keyframe_insert(path, frame=f)

def _ctrl(nombre, f, off):
    o = C(nombre); o.location = REPOSO["CTRL_" + nombre] + Vector(off) / S; _k(o, f, "location")

def mano(lado, f, off=(0, 0, 0)):      _ctrl("mano_" + lado, f, off)
def codo(lado, f, off=(0, 0, 0)):      _ctrl("codo_" + lado, f, off)
def rodilla(lado, f, off=(0, 0, 0)):   _ctrl("rodilla_" + lado, f, off)
def pie(lado, f, off=(0, 0, 0), giro=(0, 0, 0)):
    _ctrl("pie_" + lado, f, off)
    o = C("pie_" + lado); base = o.get("rot0")
    if base is None: o["rot0"] = list(o.rotation_euler); base = o["rot0"]
    q = Euler((R(giro[0]), R(giro[1]), R(giro[2]))).to_quaternion() @ Euler(base).to_quaternion()
    o.rotation_euler = q.to_euler('XYZ'); _k(o, f, "rotation_euler")

def _rot_char(bone, f, rx=0, ry=0, rz=0, peso=1.0):
    """Gira un hueso alrededor de los ejes del personaje (grados)."""
    b = B(bone); b.rotation_mode = 'QUATERNION'
    rest = b.bone.matrix_local.to_quaternion()
    qc = Euler((R(rx * peso), R(ry * peso), R(rz * peso))).to_quaternion()
    b.rotation_quaternion = rest.inverted() @ qc @ rest
    _k(b, f, "rotation_quaternion")

def columna(f, adelante=0, lado=0, giro=0):
    """adelante>0 se inclina hacia delante; lado>0 hacia su izquierda; giro>0 gira el tronco a su izquierda."""
    for n, p in (("Spine", 0.3), ("Spine1", 0.35), ("Spine2", 0.35)):
        _rot_char(n, f, adelante, lado, giro, p)

def cabeza(f, asiente=0, inclina=0, gira=0):
    """asiente>0 baja la barbilla; inclina>0 hacia su izquierda; gira>0 mira a su izquierda."""
    _rot_char("Neck", f, asiente, inclina, gira, 0.4)
    _rot_char("Head", f, asiente, inclina, gira, 0.6)

def _signo_hombro(lado):
    """Calcula (una vez) qué signo del eje X de la clavícula sube el hombro y cuál del Z lo adelanta."""
    key = "signo_hombro_" + lado
    if key in ALEX: return tuple(ALEX[key])
    L = "Left" if lado == "L" else "Right"; b = B(L + "Shoulder"); b.rotation_mode = 'XYZ'
    old = b.rotation_euler.copy(); arm_b = B(L + "Arm")
    def pos(): bpy.context.view_layer.update(); return ALEX.matrix_world @ arm_b.head
    b.rotation_euler = (0, 0, 0); p0 = pos()
    b.rotation_euler = (R(10), 0, 0); sx = 1 if pos().z > p0.z else -1
    b.rotation_euler = (0, 0, R(10)); sz = 1 if pos().y < p0.y else -1
    b.rotation_euler = old; ALEX[key] = [sx, sz]; return sx, sz

def hombro(lado, f, sube=0, adelante=0):
    """sube>0 levanta el hombro (encogerse); adelante>0 lo lleva hacia delante."""
    sx, sz = _signo_hombro(lado)
    b = B(("Left" if lado == "L" else "Right") + "Shoulder"); b.rotation_mode = 'XYZ'
    b.rotation_euler = (R(sx * sube), 0, R(sz * adelante)); _k(b, f, "rotation_euler")

def cadera(f, off=(0, 0, 0), giro=(0, 0, 0)):
    """Mueve y gira la pelvis (los pies se quedan quietos por IK)."""
    b = B("Hips"); rest = b.bone.matrix_local
    b.location = rest.to_3x3().inverted() @ (Vector(off) / S); _k(b, f, "location")
    _rot_char("Hips", f, *giro)

def mano_giro(lado, f, dobla=0, desvia=0, gira=0):
    """dobla>0 flexiona la muñeca hacia la palma; gira = pronación/supinación."""
    b = B(("Left" if lado == "L" else "Right") + "Hand"); b.rotation_mode = 'XYZ'
    s = 1 if lado == "R" else -1
    b.rotation_euler = (R(s * dobla), R(gira), R(desvia)); _k(b, f, "rotation_euler")

DEDOS = ("Index", "Middle", "Ring", "Pinky")
def dedos(lado, f, indice=0, medio=0, anular=0, menique=0, pulgar=0, abre_pulgar=0):
    """Valores 0..1 = de estirado a cerrado del todo."""
    L = "Left" if lado == "L" else "Right"; s = 1 if lado == "R" else -1
    for nombre, v in zip(DEDOS, (indice, medio, anular, menique)):
        for i, maxg in ((1, 70), (2, 95), (3, 70)):
            b = B(f"{L}Hand{nombre}{i}"); b.rotation_mode = 'XYZ'
            b.rotation_euler = (R(s * maxg * v), 0, 0); _k(b, f, "rotation_euler")
    for i, maxg in ((1, 25), (2, 40), (3, 45)):
        b = B(f"{L}HandThumb{i}"); b.rotation_mode = 'XYZ'
        b.rotation_euler = (R(s * maxg * pulgar), 0, R(s * abre_pulgar * 30 if i == 1 else 0)); _k(b, f, "rotation_euler")

POSES_MANO = {
    "relajada": dict(indice=0.25, medio=0.3, anular=0.35, menique=0.4, pulgar=0.2),
    "abierta":  dict(),
    "puño":     dict(indice=1, medio=1, anular=1, menique=1, pulgar=0.8),
    "señalar":  dict(indice=0, medio=1, anular=1, menique=1, pulgar=0.8),
    "pulgar":   dict(indice=1, medio=1, anular=1, menique=1, pulgar=0, abre_pulgar=-0.5),
    "ok":       dict(indice=0.7, medio=0.1, anular=0.15, menique=0.2, pulgar=0.7),
}
def mano_pose(lado, f, nombre):
    dedos(lado, f, **POSES_MANO[nombre])

def todo_reposo(f):
    """Pose natural de partida: brazos relajados a los lados, manos relajadas."""
    for l, s in (("R", 1), ("L", -1)):
        mano(l, f, (s * 0.10, 0.0, -0.06)); codo(l, f); pie(l, f); rodilla(l, f)
        mano_pose(l, f, "relajada"); mano_giro(l, f)
        hombro(l, f)
    columna(f); cabeza(f); cadera(f)

def respirar(f0, f1, periodo=60, amplitud=2.0):
    """Respiración suave del pecho (sin tocar otras claves)."""
    b = B("Spine2"); b.rotation_mode = 'QUATERNION'
    rest = b.bone.matrix_local.to_quaternion()
    f = f0; up = False
    while f <= f1:
        a = amplitud if up else 0
        qc = Euler((R(-a), 0, 0)).to_quaternion()
        b.rotation_quaternion = rest.inverted() @ qc @ rest; _k(b, f, "rotation_quaternion")
        f += periodo // 2; up = not up

def suavizar():
    """Todas las curvas en Bézier con manejadores automáticos (movimientos fluidos)."""
    for ob in [ALEX] + [o for o in bpy.data.objects if o.name.startswith("CTRL_")]:
        ad = ob.animation_data
        if not ad or not ad.action: continue
        try: curves = list(ad.action.fcurves)
        except Exception:
            curves = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
        for fc in curves:
            for k in fc.keyframe_points:
                if k.interpolation == 'LINEAR': continue      # tramos lineales a propósito (pies apoyados, raíz)
                k.interpolation = 'BEZIER'; k.handle_left_type = 'AUTO_CLAMPED'; k.handle_right_type = 'AUTO_CLAMPED'
            fc.update()

# ======================================================================
# POSICIONES ABSOLUTAS (metros, espacio del personaje, origen entre los pies en el suelo)
# Referencias medidas en Alex v2 (1,75 m): hombro der. (-0.19, 0.05, 1.36), hombro izq. (0.19, 0.05, 1.36),
# barbilla ~ (0, -0.12, 1.60), pecho delante ~ (0, -0.20, 1.25), cadera der. lateral (-0.22, 0.0, 1.0).
def _abs(nombre, f, pos):
    o = C(nombre); o.location = Vector(pos) / S; _k(o, f, "location")
HOMBRO_AUTO = True
def mano_en(lado, f, pos):
    """Coloca la mano. Si la mano sube por encima del hombro, la clavícula acompaña (como en un cuerpo real)."""
    _abs("mano_" + lado, f, pos)
    if HOMBRO_AUTO:
        z = pos[2]; sube = max(0.0, min(1.0, (z - 1.30) / 0.55)) * 22
        hombro(lado, f, sube)
def codo_hacia(lado, f, pos): _abs("codo_" + lado, f, pos)
def pie_en(lado, f, pos, giro=(0, 0, 0)):
    _abs("pie_" + lado, f, pos)
    o = C("pie_" + lado); base = o.get("rot0")
    if base is None: o["rot0"] = list(o.rotation_euler); base = o["rot0"]
    q = Euler((R(giro[0]), R(giro[1]), R(giro[2]))).to_quaternion() @ Euler(base).to_quaternion()
    o.rotation_euler = q.to_euler('XYZ'); _k(o, f, "rotation_euler")

def _sx(lado): return -1 if lado == "R" else 1      # signo hacia fuera en X

def brazo_caido(lado, f):
    s = _sx(lado)
    mano_en(lado, f, (s * 0.31, -0.03, 0.89)); codo_hacia(lado, f, (s * 0.65, 0.45, 1.05))

# ---------------------------------------------------------------- gestos (devuelven el fotograma final)
def saludo(lado, f0, ciclos=3, vel=8):
    s = _sx(lado); f = f0
    brazo_caido(lado, f); f += 6
    mano_en(lado, f, (s * 0.30, -0.02, 0.85)); f += 14                       # anticipación
    codo_hacia(lado, f, (s * 0.95, 0.15, 1.05)); mano_pose(lado, f, "abierta"); mano_giro(lado, f)
    mano_en(lado, f, (s * 0.44, -0.08, 1.58)); f += 4
    mano_en(lado, f, (s * 0.43, -0.08, 1.56))
    for i in range(ciclos):
        f += vel; mano_en(lado, f, (s * 0.34, -0.08, 1.54)); mano_giro(lado, f, 0, 12 * s, 0)
        f += vel; mano_en(lado, f, (s * 0.52, -0.08, 1.54)); mano_giro(lado, f, 0, -12 * s, 0)
    f += vel; mano_en(lado, f, (s * 0.44, -0.08, 1.56)); mano_giro(lado, f)
    f += 18; brazo_caido(lado, f); mano_pose(lado, f, "relajada")
    f += 5; mano_en(lado, f, (s * 0.31, -0.03, 0.91))
    return f

def senalar(lado, f0, dur=40, objetivo=(0, -2.0, 1.4)):
    s = _sx(lado); f = f0; brazo_caido(lado, f); f += 12
    dirv = (Vector(objetivo) - Vector((s * 0.19, 0.05, 1.36))).normalized()
    p = Vector((s * 0.19, 0.05, 1.36)) + dirv * 0.46
    mano_en(lado, f, p); codo_hacia(lado, f, (s * 0.7, 0.2, 0.8)); mano_pose(lado, f, "señalar"); mano_giro(lado, f, -10, 0, 0)
    f += 3; mano_en(lado, f, p + dirv * 0.01)
    f += dur; mano_en(lado, f, p)
    f += 14; brazo_caido(lado, f); mano_pose(lado, f, "relajada"); mano_giro(lado, f)
    return f

PALMA_SIGNO = {}
def calibrar_palma():
    """En reposo la palma mira hacia el muslo (hacia dentro): fija el signo de la normal."""
    for lado in ("R", "L"):
        L = "Left" if lado == "L" else "Right"; bpy.context.view_layer.update()
        hacia_dentro = Vector((1, 0, 0)) if lado == "R" else Vector((-1, 0, 0))
        hacia_dentro = (ALEX.matrix_world.to_3x3().normalized() @ hacia_dentro)
        PALMA_SIGNO[lado] = 1 if _palma(L, lado).dot(hacia_dentro) > 0 else -1

def pulgar_arriba(lado, f0, dur=30):
    s = _sx(lado); f = f0; brazo_caido(lado, f); f += 12
    mano_en(lado, f, (s * 0.22, -0.32, 1.22)); codo_hacia(lado, f, (s * 0.7, 0.1, 0.7))
    mano_pose(lado, f, "pulgar"); mano_giro(lado, f, 0, 0, 0)
    f += 4; mano_en(lado, f, (s * 0.22, -0.33, 1.25))
    f += dur; mano_en(lado, f, (s * 0.22, -0.32, 1.22))
    f += 14; brazo_caido(lado, f); mano_pose(lado, f, "relajada")
    return f

def encogerse(f0, dur=24):
    f = f0
    for l in ("R", "L"): brazo_caido(l, f); hombro(l, f)
    cabeza(f); f += 10
    for l in ("R", "L"):
        s = _sx(l); mano_en(l, f, (s * 0.42, -0.25, 1.05)); codo_hacia(l, f, (s * 0.7, 0.3, 0.8))
        mano_pose(l, f, "abierta"); hombro(l, f, 14)
    cabeza(f, 0, 10, 0); f += dur
    for l in ("R", "L"): hombro(l, f, 10)
    f += 14
    for l in ("R", "L"): brazo_caido(l, f); hombro(l, f); mano_pose(l, f, "relajada")
    cabeza(f)
    return f

def pensar(lado, f0, dur=40):
    s = _sx(lado); f = f0; brazo_caido(lado, f); f += 14
    mano_en(lado, f, (s * 0.04, -0.20, 1.45)); codo_hacia(lado, f, (s * 0.5, -0.3, 0.9))
    mano_pose(lado, f, "relajada"); cabeza(f, 6, 6 * -s, 0); columna(f, 4, 0, 0)
    f += dur; cabeza(f, 6, 8 * -s, 4 * -s)
    f += 14; brazo_caido(lado, f); cabeza(f); columna(f)
    return f

Y_PIE = 0.065   # y de reposo de los tobillos

def _lineal(obj, data_path_exacto, f0, f1, indice=None):
    ad = obj.animation_data
    if not ad or not ad.action: return
    try: curves = list(ad.action.fcurves)
    except Exception:
        curves = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
    for fc in curves:
        if fc.data_path == data_path_exacto and (indice is None or fc.array_index == indice):
            for k in fc.keyframe_points:
                if f0 <= k.co.x < f1: k.interpolation = 'LINEAR'

def andar(f0, pasos=4, zancada=0.55, fp=15, levanta=0.10):
    """Camina hacia delante. El objeto ALEX_v2 avanza (movimiento de raíz) y los pies se quedan clavados
    en el suelo mientras apoyan. Devuelve el fotograma final."""
    L = zancada; f = f0
    fwd = (ALEX.matrix_world.to_3x3().normalized() @ Vector((0, -1, 0))).normalized()
    root0 = ALEX.location.copy(); avance = 0.0
    ALEX.keyframe_insert("location", frame=f)
    y = {"R": 0.0, "L": 0.0}
    for i in range(pasos):
        sw = "R" if i % 2 == 0 else "L"; st = "L" if sw == "R" else "R"
        a = L / 2 if (i == 0 or i == pasos - 1) else L
        y_sw_fin = -L / 2 if i < pasos - 1 else 0.0
        fm = f + fp // 2; f1 = f + fp
        # pie de apoyo: retrocede (en el espacio del personaje) lo mismo que avanza la raíz
        pie_en(st, f, (_sx(st) * 0.20, Y_PIE + y[st], 0.12)); pie_en(st, f1, (_sx(st) * 0.20, Y_PIE + y[st] + a, 0.12))
        # pie que avanza: sube en el medio
        pie_en(sw, f, (_sx(sw) * 0.20, Y_PIE + y[sw], 0.12))
        pie_en(sw, fm, (_sx(sw) * 0.20, Y_PIE + (y[sw] + y_sw_fin) / 2, 0.12 + levanta), (-12, 0, 0))
        pie_en(sw, f1, (_sx(sw) * 0.20, Y_PIE + y_sw_fin, 0.12), (6, 0, 0))
        y[st] += a; y[sw] = y_sw_fin
        # raíz
        avance += a; ALEX.location = root0 + fwd * (avance * 1.0); ALEX.keyframe_insert("location", frame=f1)
        # cadera: baja al apoyar, sube al pasar; gira un poco con el paso
        cadera(f, (0, 0, -0.025), (0, 0, 4 * _sx(sw))); cadera(fm, (0, 0, 0.012), (0, 0, 0))
        # brazos en oposición
        mano_en(st, fm, (_sx(st) * 0.30, -0.20, 0.93)); mano_en(sw, fm, (_sx(sw) * 0.30, 0.16, 0.91))
        codo_hacia(st, fm, (_sx(st) * 0.65, 0.45, 1.05)); codo_hacia(sw, fm, (_sx(sw) * 0.65, 0.45, 1.05))
        columna(fm, 3, 0, 4 * _sx(sw))
        f = f1
    cadera(f, (0, 0, 0), (0, 0, 0)); columna(f)
    for l in ("R", "L"): brazo_caido(l, f); pie_en(l, f + 5, (_sx(l) * 0.20, Y_PIE, 0.12))
    _lineal(ALEX, "location", f0, f)
    for l in ("R", "L"): _lineal(C("pie_" + l), "location", f0, f, indice=1)
    return f

# ======================================================================
# ORIENTAR LA MANO por objetivos (busca el giro de muñeca que mejor cumple las direcciones pedidas)
def _vec(L, a, b):
    return ((ALEX.matrix_world @ B(L + b).head) - (ALEX.matrix_world @ B(L + a).head)).normalized()

def _palma(L, lado):
    d = _vec(L, "Hand", "HandMiddle1"); a = _vec(L, "HandIndex1", "HandPinky1")
    n = d.cross(a).normalized()
    return n if lado == "R" else -n   # normal que sale de la palma (se calibra con PALMA_SIGNO)

def orientar_mano(lado, f, pulgar_hacia=None, dedos_hacia=None, palma_hacia=None, max_ang=110):
    """pulgar_hacia / dedos_hacia: direcciones en el espacio del MUNDO (p. ej. (0,0,1) = arriba).
    Ajusta la rotación de la muñeca en el fotograma f y la guarda como clave."""
    L = "Left" if lado == "L" else "Right"; h = B(L + "Hand"); h.rotation_mode = 'XYZ'
    bpy.context.scene.frame_set(f)
    def score():
        bpy.context.view_layer.update(); s_ = 0
        if pulgar_hacia: s_ += _vec(L, "HandThumb1", "HandThumb4").dot(Vector(pulgar_hacia).normalized())
        if dedos_hacia: s_ += _vec(L, "Hand", "HandMiddle1").dot(Vector(dedos_hacia).normalized())
        if palma_hacia: s_ += 1.5 * PALMA_SIGNO.get(lado, 1) * _palma(L, lado).dot(Vector(palma_hacia).normalized())
        return s_
    e = list(h.rotation_euler); best = score()
    for paso in (40, 20, 10, 5, 2):
        mejora = True
        while mejora:
            mejora = False
            for ax in range(3):
                for sg in (1, -1):
                    old = e[ax]; e[ax] = max(-R(max_ang), min(R(max_ang), old + sg * R(paso)))
                    h.rotation_euler = e; sc_ = score()
                    if sc_ > best + 1e-4: best = sc_; mejora = True
                    else: e[ax] = old; h.rotation_euler = e
    _k(h, f, "rotation_euler")
    return round(best, 3)

PALMA_SIGNO = {}
def calibrar_palma():
    """En reposo la palma mira hacia el muslo (hacia dentro): fija el signo de la normal."""
    for lado in ("R", "L"):
        L = "Left" if lado == "L" else "Right"; bpy.context.view_layer.update()
        hacia_dentro = Vector((1, 0, 0)) if lado == "R" else Vector((-1, 0, 0))
        hacia_dentro = (ALEX.matrix_world.to_3x3().normalized() @ hacia_dentro)
        PALMA_SIGNO[lado] = 1 if _palma(L, lado).dot(hacia_dentro) > 0 else -1

def pulgar_arriba(lado, f0, dur=30):
    s = _sx(lado); f = f0; brazo_caido(lado, f); f += 12
    mano_en(lado, f, (s * 0.24, -0.30, 1.18)); codo_hacia(lado, f, (s * 0.8, 0.1, 0.75)); mano_pose(lado, f, "pulgar")
    orientar_mano(lado, f, pulgar_hacia=(0, 0, 1), dedos_hacia=(-s * 0.6, -0.4, 0))
    f2 = f + 4; mano_en(lado, f2, (s * 0.24, -0.31, 1.21)); mano_pose(lado, f2, "pulgar")
    orientar_mano(lado, f2, pulgar_hacia=(0, 0, 1), dedos_hacia=(-s * 0.6, -0.4, 0))
    f = f2 + dur; mano_en(lado, f, (s * 0.24, -0.30, 1.18)); mano_pose(lado, f, "pulgar")
    orientar_mano(lado, f, pulgar_hacia=(0, 0, 1), dedos_hacia=(-s * 0.6, -0.4, 0))
    f += 14; brazo_caido(lado, f); mano_pose(lado, f, "relajada"); mano_giro(lado, f)
    return f

def encogerse(f0, dur=24):
    f = f0
    for l in ("R", "L"): brazo_caido(l, f); hombro(l, f); mano_giro(l, f)
    cabeza(f); f += 10
    for l in ("R", "L"):
        s = _sx(l); mano_en(l, f, (s * 0.45, -0.22, 1.02)); codo_hacia(l, f, (s * 0.7, 0.3, 0.8))
        mano_pose(l, f, "abierta"); hombro(l, f, 14)
        orientar_mano(l, f, palma_hacia=(0, 0, 1), dedos_hacia=(s * 0.5, -1, 0))
    cabeza(f, 0, 10, 0); f += dur
    for l in ("R", "L"):
        s = _sx(l); hombro(l, f, 10); mano_en(l, f, (s * 0.46, -0.22, 1.0)); mano_pose(l, f, "abierta")
        orientar_mano(l, f, palma_hacia=(0, 0, 1), dedos_hacia=(s * 0.5, -1, 0))
    f += 14
    for l in ("R", "L"): brazo_caido(l, f); hombro(l, f); mano_pose(l, f, "relajada"); mano_giro(l, f)
    cabeza(f)
    return f
