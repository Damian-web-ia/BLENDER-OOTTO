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
                k.interpolation = 'BEZIER'; k.handle_left_type = 'AUTO_CLAMPED'; k.handle_right_type = 'AUTO_CLAMPED'
            fc.update()
