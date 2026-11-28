# MAITE · herramientas de animación · EKORUEDAS · 27-11-2026
# Uso en una escena:
#   MA = {"__name__": "maite_anim"}; exec(open(".../maite_anim.py", encoding="utf-8").read(), MA)
#   M = MA["MaiteAnim"](bpy.data.objects["MAITE_rig"])
#   M.pose_reposo(1); M.brazo(40, "R", "explica"); M.mano(40, "R", "abierta"); M.cabeza(40, giro=10) ...
#   M.finalizar(1, 300)      # suaviza, añade respiración y vida a la cabeza, y hornea la trenza
# Todo queda en fotogramas clave (sin drivers): se renderiza igual en segundo plano.
# Direcciones en el MUNDO con Maite mirando a cámara (-y): x+ = su izquierda, z+ = arriba.
import bpy, math
from mathutils import Vector, Matrix, Quaternion, Euler

L, R = "Left", "Right"
def _lado(l): return L if l in ("L", "Left", "izq", "I") else R


class MaiteAnim:
    def __init__(self, arm):
        self.arm = arm; self.pb = arm.pose.bones; self.sc = bpy.context.scene
        for b in self.pb:                                # sólo el esqueleto (los pivotes del rig van en Euler con drivers)
            if b.name.startswith("mixamorig:") or b.name.startswith("Trenza"): b.rotation_mode = 'QUATERNION'
        self.trenza = [n for n in arm.get("trenza", "").split(",") if n]
        self._resp = []; self._vida = []

    # -------------------------------------------------------------- básicos
    def _upd(self, f=None):
        if f is not None: self.sc.frame_set(f)
        bpy.context.view_layer.update()

    def q(self, nombre, f, quat):
        b = self.pb.get(nombre)
        if not b: return
        b.rotation_quaternion = quat; b.keyframe_insert("rotation_quaternion", frame=f)

    def rot(self, nombre, f, x=0.0, y=0.0, z=0.0):
        """Giro local del hueso en grados."""
        self.q(nombre, f, Euler((math.radians(x), math.radians(y), math.radians(z)), 'XYZ').to_quaternion())

    def dirigir(self, nombre, d_mundo, f):
        """Apunta el hueso a una dirección del mundo y pone clave."""
        b = self.pb.get(nombre)
        if not b: return
        self._upd(f)
        d = (self.arm.matrix_world.inverted().to_3x3() @ Vector(d_mundo)).normalized()
        M_ = b.matrix.copy(); y = M_.col[1].xyz.normalized()
        qd = y.rotation_difference(d)
        b.matrix = Matrix.Translation(M_.translation) @ qd.to_matrix().to_4x4() @ M_.to_3x3().to_4x4()
        self._upd(); b.keyframe_insert("rotation_quaternion", frame=f)

    def reset(self, f, nombres):
        for n in nombres:
            if n in self.pb: self.q(n, f, Quaternion())

    # -------------------------------------------------------------- cuerpo
    ESPALDA = ("mixamorig:Spine", "mixamorig:Spine1", "mixamorig:Spine2")
    def torso(self, f, adelante=0.0, giro=0.0, lado=0.0):
        """Reparte el gesto entre las tres vértebras."""
        for n, k in zip(self.ESPALDA, (0.25, 0.35, 0.40)):
            self.rot(n, f, adelante * k, giro * k, lado * k)

    def cabeza(self, f, arriba=0.0, giro=0.0, ladeo=0.0):
        """Cuello 35 % y cabeza 65 %."""
        self.rot("mixamorig:Neck", f, -arriba * 0.35, giro * 0.35, ladeo * 0.35)
        self.rot("mixamorig:Head", f, -arriba * 0.65, giro * 0.65, ladeo * 0.65)

    def caderas(self, f, baja=0.0, lado=0.0, giro=0.0, inclina=0.0):
        """Desplaza las caderas (metros del mundo) y las gira. baja > 0 = flexiona las rodillas."""
        h = self.pb["mixamorig:Hips"]; s = self.arm.scale[0]
        h.location = Vector((lado / s, -baja / s, 0.0)); h.keyframe_insert("location", frame=f)
        self.rot("mixamorig:Hips", f, 0, giro, inclina)

    # brazo y antebrazo: direcciones para el lado DERECHO de ella (su derecha es x-); el izquierdo se refleja
    POSES_BRAZO = {
        "reposo":        ((-0.22, 0.04, -0.97), (-0.12, -0.22, -0.97)),
        "jarras":        ((-0.55, 0.30, -0.78), (0.55, -0.10, -0.83)),
        "explica":       ((-0.40, -0.25, -0.88), (-0.25, -0.88, 0.40)),
        "explica_alto":  ((-0.50, -0.35, -0.79), (-0.15, -0.80, 0.58)),
        "presenta":      ((-0.62, -0.40, -0.67), (-0.55, -0.82, -0.10)),
        "senala":        ((-0.92, -0.30, -0.25), (-0.95, -0.28, -0.12)),
        "senala_arriba": ((-0.55, -0.35, 0.76), (-0.40, -0.30, 0.86)),
        "barbilla":      ((-0.30, -0.45, -0.84), (0.35, -0.45, 0.82)),
        "saluda":        ((-0.85, 0.05, 0.25), (-0.15, 0.05, 0.99)),
        "cruzado":       ((-0.20, -0.30, -0.93), (0.85, -0.45, 0.25)),
        "agarra":        ((-0.30, -0.45, -0.84), (-0.10, -0.95, -0.30)),
    }
    def brazo(self, f, lado, pose="reposo", d_brazo=None, d_ante=None):
        l = _lado(lado)
        db, da = self.POSES_BRAZO.get(pose, self.POSES_BRAZO["reposo"])
        db = d_brazo or db; da = d_ante or da
        esp = (lambda v: (-v[0], v[1], v[2])) if l == L else (lambda v: tuple(v))
        self.dirigir(f"mixamorig:{l}Arm", esp(db), f)
        self.dirigir(f"mixamorig:{l}ForeArm", esp(da), f)

    MANOS = {   # curva de los dedos (grados) y pulgar
        "relajada": dict(i=14, m=18, a=22, p=26, pul=10, sep=4),
        "abierta":  dict(i=2, m=3, a=4, p=6, pul=-8, sep=9),
        "senala":   dict(i=0, m=75, a=82, p=88, pul=30, sep=2),
        "puno":     dict(i=85, m=88, a=90, p=92, pul=45, sep=0),
        "agarra":   dict(i=48, m=52, a=55, p=58, pul=28, sep=2),
        "empuna":   dict(i=72, m=76, a=78, p=80, pul=38, sep=0),     # empuña una barra (llave, herramienta)
        "pulgar":   dict(i=85, m=88, a=90, p=92, pul=-25, sep=0),
        "pinza":    dict(i=38, m=20, a=24, p=28, pul=34, sep=3),
        "tensa":    dict(i=-6, m=-4, a=-2, p=0, pul=-15, sep=12),
    }
    def mano(self, f, lado, forma="relajada", muneca=(0, 0, 0)):
        l = _lado(lado); c = self.MANOS.get(forma, self.MANOS["relajada"]); s = 1 if l == L else -1
        for dedo, k, abre in (("Index", "i", 1.0), ("Middle", "m", 0.3), ("Ring", "a", -0.4), ("Pinky", "p", -1.0)):
            for j in (1, 2, 3):
                ang = c[k] * (0.85 if j == 1 else 1.0 if j == 2 else 0.75) * s     # la mano derecha es espejo (si no, se doblan hacia atrás)
                self.rot(f"mixamorig:{l}Hand{dedo}{j}", f, ang, 0, (c["sep"] * abre * s) if j == 1 else 0)
        for j in (1, 2, 3):
            self.rot(f"mixamorig:{l}HandThumb{j}", f, 0, 0, c["pul"] * s * (0.6 if j == 1 else 0.4))
        self.rot(f"mixamorig:{l}Hand", f, *muneca)

    def hombros(self, f, sube=0.0):
        """sube > 0: encoge los hombros."""
        self.rot("mixamorig:LeftShoulder", f, 0, 0, -sube); self.rot("mixamorig:RightShoulder", f, 0, 0, sube)

    # -------------------------------------------------------------- caminar
    def _mover(self, nombre, f, desplaz_mundo):
        """Pone la 'location' del hueso para que quede desplazado esa cantidad (metros del mundo) desde su reposo.
        Vale para huesos cuyo padre está en reposo (los pies IK y Hips cuelgan de CTRL_raiz, que no se mueve)."""
        b = self.pb.get(nombre)
        if not b: return
        s = self.arm.scale[0]
        R_ = b.bone.matrix_local.to_3x3()
        b.location = (R_.inverted() @ (self.arm.matrix_world.to_3x3().normalized().inverted() @ Vector(desplaz_mundo))) / s
        b.keyframe_insert("location", frame=f)

    @staticmethod
    def _gira_x(v, grados):
        a = math.radians(grados); x, y, z = v
        return (x, y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a))

    def caminar(self, f0, pasos=6, zancada=0.30, frames_paso=14, altura_pie=0.045, adelante=(0.0, -1.0, 0.0),
                inicio=(0.0, 0.0, 0.0), brazos=True):
        """Paseo hacia delante con los pies plantados de verdad (IK). Se mueve CTRL_raiz (así lo demás —caderas, brazos,
        expresiones— sigue funcionando igual donde acabe) y los pies se compensan para quedarse quietos en el suelo:
        cada paso, un pie se despega de puntillas, viaja en arco y apoya de talón; la cadera baja al apoyar, se va
        hacia el pie de apoyo y gira; el pecho compensa; los brazos van en contrafase.
        inicio: dónde empieza (metros del mundo respecto a su sitio); el último paso junta los pies.
        Devuelve el último fotograma."""
        F = Vector(adelante).normalized(); T = frames_paso; I0 = Vector(inicio)
        lado_pie = {L: 1.0, R: -1.0}
        pos = {L: 0.0, R: 0.0}                  # avance de cada pie (metros, desde inicio)
        sw = [L, R]
        def raiz_en(f, av):
            self._mover("CTRL_raiz", f, tuple(I0 + F * av))
        def pie_en(l, f, av, alto=0.0, raiz_av=0.0):
            self._mover(f"IK_pie_{l[0]}", f, tuple(F * (av - raiz_av) + Vector((0, 0, alto))))
        raiz_en(f0, 0.0)
        for l in (L, R):
            pie_en(l, f0, 0.0); self.pb[f"IK_pie_{l[0]}"]["roll"] = 0.0; self.pb[f"IK_pie_{l[0]}"].keyframe_insert('["roll"]', frame=f0)
        for k in range(pasos):
            l = sw[k % 2]; o = sw[(k + 1) % 2]; fk = f0 + k * T
            ultimo = k == pasos - 1
            ini = pos[l]; destino = pos[o] if ultimo else pos[o] + zancada
            b = self.pb[f"IK_pie_{l[0]}"]
            for t, roll, alto in ((0.0, 0.55, 0.0), (0.25, 0.35, altura_pie * 0.7), (0.5, 0.05, altura_pie),
                                  (0.75, -0.15, altura_pie * 0.55), (1.0, -0.1, 0.0)):
                f = fk + int(round(t * T))
                av = ini + (destino - ini) * (3 * t * t - 2 * t ** 3)
                medio = (ini + (destino - ini) * t + pos[o]) / 2.0          # la raíz va a la mitad de los dos pies
                raiz_en(f, medio)
                pie_en(l, f, av, alto, medio)
                pie_en(o, f, pos[o], 0.0, medio)                            # el de apoyo, quieto en el suelo
                b["roll"] = roll; b.keyframe_insert('["roll"]', frame=f)
                fin_ = ultimo and t == 1.0
                bajo = 0.0 if fin_ else (0.016 if t in (0.0, 1.0) else 0.004 + 0.008 * abs(t - 0.5))
                lat = 0.0 if fin_ else lado_pie[o] * 0.012 * math.sin(math.pi * t)
                giro = 0.0 if fin_ else 5.0 * lado_pie[l] * (1 - 2 * t)
                self.caderas(f, baja=bajo, lado=lat, giro=giro, inclina=0.0 if fin_ else 2.5 * lado_pie[o] * math.sin(math.pi * t))
                self.torso(f, adelante=0.0 if fin_ else 5.0, giro=-giro * 1.1)
                self.cabeza(f, arriba=0.0 if fin_ else -3.0, giro=giro * 0.3)
                if brazos and t in (0.0, 0.5, 1.0):
                    a = 0.0 if fin_ else 16.0 * (1 - 2 * t)
                    db, da = self.POSES_BRAZO["reposo"]
                    for lb, sg in ((l, 1.0), (o, -1.0)):
                        self.brazo(f, lb, "reposo", d_brazo=self._gira_x(db, -a * sg), d_ante=self._gira_x(da, -a * sg * 1.4 - 8 * (a != 0)))
            b["roll"] = 0.0; b.keyframe_insert('["roll"]', frame=fk + T + 3)
            pos[l] = destino
        return f0 + pasos * T

    def pose_reposo(self, f):
        self.reset(f, [b.name for b in self.pb if not b.name.startswith("Trenza")])
        self.caderas(f)
        for l in (L, R): self.brazo(f, l, "reposo"); self.mano(f, l, "relajada")

    # -------------------------------------------------------------- capas que se suman al final
    def respirar(self, f0, f1, fuerza=1.0, segundos=4.0):
        self._resp.append((f0, f1, fuerza, segundos))

    def vida(self, f0, f1, fuerza=1.0):
        """Micro-movimientos de la cabeza (nadie está quieto del todo)."""
        self._vida.append((f0, f1, fuerza))

    def _capas(self):
        """Primero lee la postura de cada fotograma y después pone las claves (si no, cada clave nueva
        cambiaría lo que se lee en el fotograma siguiente)."""
        fps = self.sc.render.fps
        frames = sorted({f for a, b_, *_ in self._resp + self._vida for f in range(a, b_ + 1, 2)})
        if not frames: return
        huesos = ("mixamorig:Spine2", "mixamorig:LeftShoulder", "mixamorig:RightShoulder", "mixamorig:Head")
        base = {}
        for f in frames:
            self.sc.frame_set(f)
            base[f] = {h: self.pb[h].rotation_quaternion.copy() for h in huesos}
        for f in frames:
            extra = {h: Quaternion() for h in huesos}
            for f0, f1, fu, seg in self._resp:
                if f0 <= f <= f1:
                    t = (f - f0) / (seg * fps) * 2 * math.pi
                    extra["mixamorig:Spine2"] = extra["mixamorig:Spine2"] @ Euler((math.radians(-1.1 * fu * math.sin(t)), 0, 0)).to_quaternion()
                    a = math.radians(0.9 * fu * max(0.0, math.sin(t)))
                    extra["mixamorig:LeftShoulder"] = extra["mixamorig:LeftShoulder"] @ Euler((0, 0, -a)).to_quaternion()
                    extra["mixamorig:RightShoulder"] = extra["mixamorig:RightShoulder"] @ Euler((0, 0, a)).to_quaternion()
            for f0, f1, fu in self._vida:
                if f0 <= f <= f1:
                    t = f / fps
                    x = 0.9 * math.sin(t * 1.3) + 0.5 * math.sin(t * 2.9 + 1.1)
                    y = 1.1 * math.sin(t * 0.9 + 0.4) + 0.4 * math.sin(t * 2.3)
                    z = 0.6 * math.sin(t * 1.7 + 2.0)
                    extra["mixamorig:Head"] = extra["mixamorig:Head"] @ Euler((math.radians(x * fu), math.radians(y * fu), math.radians(z * fu))).to_quaternion()
            for h in huesos:
                if extra[h] != Quaternion():
                    self.pb[h].rotation_quaternion = base[f][h] @ extra[h]
                    self.pb[h].keyframe_insert("rotation_quaternion", frame=f)

    # -------------------------------------------------------------- suavizado y final
    def _fcurves(self):
        ad = self.arm.animation_data
        if not ad or not ad.action: return []
        a_ = ad.action
        try: return list(a_.fcurves)
        except Exception: return [fc for l in a_.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]

    def suavizar(self, tipo='BEZIER'):
        for fc in self._fcurves():
            for k in fc.keyframe_points:
                k.interpolation = tipo; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
            fc.update()

    def finalizar(self, f0, f1, trenza=True, **kw):
        self.suavizar()
        self._capas()
        if trenza and self.trenza: self.hornear_trenza(f0, f1, **kw)

    # -------------------------------------------------------------- trenza (muelle con choques)
    def hornear_trenza(self, f0, f1, rigidez=0.10, amort=0.88, gravedad=0.0006, previo=30, choques=True):
        """La trenza nace de la cabeza pero descansa sobre el hombro y el pecho: su reposo mezcla la postura de la
        cabeza (arriba) con la del pecho (abajo). Encima, un muelle amortiguado con algo de gravedad; unas esferas
        en el pecho y el hombro izquierdo impiden que se meta en el cuerpo."""
        arm = self.arm; sc = self.sc; PB = self.pb
        pbs = [PB[n] for n in self.trenza]
        g = arm.matrix_world.inverted().to_3x3() @ Vector((0, 0, -gravedad))
        for b in pbs: b.rotation_quaternion = Quaternion()
        sc.frame_set(f0); bpy.context.view_layer.update()
        H = PB["mixamorig:Head"].matrix.copy(); S = PB["mixamorig:Spine2"].matrix.copy()
        J = [pbs[0].head.copy()] + [b.tail.copy() for b in pbs]; n = len(J)
        offH = [H.inverted() @ x for x in J]; offS = [S.inverted() @ x for x in J]
        mezcla = [min(0.92, (k / (n - 1)) ** 0.7) for k in range(n)]
        Lg = [(J[k + 1] - J[k]).length for k in range(n - 1)]
        esf = []
        if choques:
            for nb in ("mixamorig:Spine2", "mixamorig:LeftShoulder"):
                bone = PB.get(nb)
                if not bone: continue
                Mb = bone.matrix.copy(); c0 = Mb @ Vector((0, bone.length * 0.5, 0))
                rad = min((x - c0).length for x in J[1:]) - 0.004
                if rad > 0.01: esf.append((nb, Mb.inverted() @ c0, rad))
        pos = [x.copy() for x in J]; ant = [x.copy() for x in J]

        def paso(f, guardar):
            sc.frame_set(f)
            for b in pbs: b.rotation_quaternion = Quaternion()
            bpy.context.view_layer.update()
            Hm = PB["mixamorig:Head"].matrix; Sm = PB["mixamorig:Spine2"].matrix
            rep = [(Hm @ offH[k]).lerp(Sm @ offS[k], mezcla[k]) for k in range(n)]
            pos[0] = rep[0].copy()
            cs = [(PB[nb].matrix @ c, r) for nb, c, r in esf]
            for k in range(1, n):
                v = (pos[k] - ant[k]) * amort; ant[k] = pos[k].copy()
                rg = rigidez * (1.0 - 0.35 * k / n)
                pos[k] = pos[k] + v + (rep[k] - pos[k]) * rg + g
            for _ in range(2):
                for k in range(1, n):
                    d = pos[k] - pos[k - 1]
                    if d.length > 1e-9: pos[k] = pos[k - 1] + d.normalized() * Lg[k - 1]
                    for c, r in cs:
                        e = pos[k] - c
                        if e.length < r: pos[k] = c + e.normalized() * r
            if not guardar: return
            for k, b in enumerate(pbs):
                M = b.matrix.copy(); cab = M.translation.copy(); y = M.col[1].xyz.normalized()
                qd = y.rotation_difference((pos[k + 1] - cab).normalized())
                b.matrix = Matrix.Translation(cab) @ qd.to_matrix().to_4x4() @ M.to_3x3().to_4x4()
                bpy.context.view_layer.update(); b.keyframe_insert("rotation_quaternion", frame=f)

        for _ in range(previo): paso(f0, False)
        for f in range(f0, f1 + 1): paso(f, True)
        print("TRENZA_HORNEADA", f0, f1, "esferas", [(e[0], round(e[2], 3)) for e in esf], flush=True)


# ====================================================================== CARA: expresiones, parpadeos, mirada y labios
# Pesos con los nombres de las shape keys de ARKit (las 52 están en MAITE_cuerpo). "Left" = izquierda de ELLA.
def _sim(d):
    """Copia los valores X Left/Right a los dos lados si solo se da uno con '*'."""
    out = {}
    for k, v in d.items():
        if k.endswith("*"):
            out[k[:-1] + "Left"] = v; out[k[:-1] + "Right"] = v
        else:
            out[k] = v
    return out

EXPRESIONES = {
    "neutra":            {},
    "alegria":           _sim({"mouthSmile*": 0.8, "cheekSquint*": 0.5, "eyeSquint*": 0.2, "browInnerUp": 0.2, "jawOpen": 0.10}),
    "sonrisa_natural":   _sim({"mouthSmile*": 0.5, "cheekSquint*": 0.25, "eyeSquint*": 0.15}),
    "sonrisa_asimetrica": {"mouthSmileLeft": 0.85, "mouthSmileRight": 0.20, "mouthDimpleLeft": 0.3, "cheekSquintLeft": 0.4, "eyeSquintLeft": 0.2},
    "risa":              _sim({"mouthSmile*": 1.0, "cheekSquint*": 0.8, "eyeSquint*": 0.6, "eyeBlink*": 0.25, "jawOpen": 0.55, "browInnerUp": 0.25}),
    "entusiasmo":        _sim({"mouthSmile*": 1.0, "cheekSquint*": 0.6, "eyeWide*": 0.4, "browOuterUp*": 0.5, "browInnerUp": 0.4, "jawOpen": 0.35}),
    "satisfaccion":      _sim({"mouthSmile*": 0.5, "eyeBlink*": 0.35, "mouthPress*": 0.3, "browInnerUp": 0.1}),
    "tristeza":          _sim({"mouthFrown*": 0.7, "eyeLookDown*": 0.3, "eyeBlink*": 0.15, "mouthShrugLower": 0.3, "browInnerUp": 0.8}),
    "sorpresa":          _sim({"eyeWide*": 1.0, "browOuterUp*": 0.8, "browInnerUp": 0.9, "jawOpen": 0.40, "mouthFunnel": 0.2}),
    "miedo":             _sim({"eyeWide*": 1.0, "mouthStretch*": 0.6, "mouthFrown*": 0.2, "browInnerUp": 1.0, "jawOpen": 0.25}),
    "enfado":            _sim({"browDown*": 1.0, "eyeSquint*": 0.4, "noseSneer*": 0.5, "mouthPress*": 0.5, "mouthFrown*": 0.4, "jawForward": 0.2}),
    "frustracion":       _sim({"browDown*": 0.7, "mouthPress*": 0.7, "noseSneer*": 0.3, "eyeSquint*": 0.3, "mouthFrown*": 0.4}),
    "preocupacion":      _sim({"browInnerUp": 0.9, "mouthStretch*": 0.3, "mouthPress*": 0.3, "eyeWide*": 0.2, "mouthFrown*": 0.3}),
    "nerviosismo":       _sim({"mouthSmile*": 0.3, "mouthStretch*": 0.4, "eyeWide*": 0.3, "browInnerUp": 0.6}),
    "confusion":         {"browDownLeft": 0.6, "browOuterUpRight": 0.7, "mouthLeft": 0.4, "mouthPressRight": 0.3, "eyeSquintLeft": 0.3},
    "incredulidad":      {"browOuterUpLeft": 0.8, "browDownRight": 0.4, "mouthPressLeft": 0.3, "mouthPressRight": 0.3, "mouthLeft": 0.3, "eyeSquintRight": 0.3},
    "curiosidad":        _sim({"browOuterUp*": 0.5, "eyeWide*": 0.3, "mouthSmile*": 0.2, "browInnerUp": 0.3}),
    "concentracion":     _sim({"browDown*": 0.5, "eyeSquint*": 0.5, "mouthPress*": 0.5, "mouthRollLower": 0.2}),
    "pensamiento":       {"eyeLookUpLeft": 0.6, "eyeLookUpRight": 0.6, "browDownLeft": 0.4, "browOuterUpRight": 0.3, "mouthPucker": 0.3, "mouthLeft": 0.3},
    "verguenza":         _sim({"mouthSmile*": 0.3, "eyeLookDown*": 0.6, "mouthPress*": 0.3, "browInnerUp": 0.4}),
    "cansancio":         _sim({"eyeBlink*": 0.45, "mouthFrown*": 0.2, "browInnerUp": 0.2, "jawOpen": 0.05}),
    "aburrimiento":      _sim({"eyeBlink*": 0.40, "mouthPress*": 0.2, "browDown*": 0.1, "mouthLeft": 0.2}),
    "sarcasmo":          {"mouthSmileLeft": 0.7, "mouthLeft": 0.3, "browOuterUpLeft": 0.6, "eyeSquintRight": 0.3, "cheekSquintLeft": 0.3},
    "ironia":            {"mouthSmileRight": 0.5, "browDownLeft": 0.3, "browOuterUpRight": 0.4, "eyeSquintLeft": 0.2},
    "comica":            _sim({"eyeWide*": 1.0, "browOuterUp*": 1.0, "mouthStretch*": 0.6, "browInnerUp": 0.8, "jawOpen": 0.7}),
    "guino":             {"eyeBlinkLeft": 1.0, "cheekSquintLeft": 0.5, "mouthSmileLeft": 0.7, "mouthSmileRight": 0.3, "browDownLeft": 0.2},
}

# visemas del español (solo boca y mandíbula)
VISEMAS = {
    "a": {"jawOpen": 0.55, "mouthStretchLeft": 0.10, "mouthStretchRight": 0.10},
    "e": {"jawOpen": 0.32, "mouthStretchLeft": 0.35, "mouthStretchRight": 0.35, "mouthSmileLeft": 0.15, "mouthSmileRight": 0.15},
    "i": {"jawOpen": 0.16, "mouthStretchLeft": 0.50, "mouthStretchRight": 0.50, "mouthSmileLeft": 0.25, "mouthSmileRight": 0.25},
    "o": {"jawOpen": 0.40, "mouthFunnel": 0.75},
    "u": {"jawOpen": 0.14, "mouthPucker": 0.85},
    "mbp": {"jawOpen": 0.0, "mouthClose": 0.95, "mouthPressLeft": 0.25, "mouthPressRight": 0.25, "mouthRollLower": 0.15},
    "fv": {"jawOpen": 0.08, "mouthRollLower": 0.6, "mouthUpperUpLeft": 0.2, "mouthUpperUpRight": 0.2},
    "dental": {"jawOpen": 0.18, "mouthStretchLeft": 0.15, "mouthStretchRight": 0.15},
    "ch": {"jawOpen": 0.18, "mouthFunnel": 0.35},
    "kg": {"jawOpen": 0.24},
    "reposo": {},
}
_LETRA = {}
for ch_ in "aá": _LETRA[ch_] = "a"
for ch_ in "eé": _LETRA[ch_] = "e"
for ch_ in "iíy": _LETRA[ch_] = "i"
for ch_ in "oó": _LETRA[ch_] = "o"
for ch_ in "uúü": _LETRA[ch_] = "u"
for ch_ in "mbpv": _LETRA[ch_] = "mbp"
_LETRA["f"] = "fv"
for ch_ in "tdnlsrzcñx": _LETRA[ch_] = "dental"
for ch_ in "kgjqh": _LETRA[ch_] = "kg"
_TODAS = sorted({k for d in list(EXPRESIONES.values()) + list(VISEMAS.values()) for k in d} | {"eyeBlinkLeft", "eyeBlinkRight"})


def _cara_metodos(cls):
    def _kb(self):
        me = bpy.data.objects.get("MAITE_cuerpo")
        return me.data.shape_keys.key_blocks if me and me.data.shape_keys else None
    def _key(self, nombre, f, v):
        kb = self._kb()
        if kb and nombre in kb:
            kb[nombre].value = max(0.0, min(1.0, v)); kb[nombre].keyframe_insert("value", frame=f)
    def expresion(self, f, nombre, intensidad=1.0, base=None):
        """Pone la expresión en el fotograma f (todas las claves de expresión: las que no usa, a 0)."""
        d = EXPRESIONES.get(nombre, {}); self._expr_actual = (nombre, intensidad)
        for k in _TODAS:
            if k in ("jawOpen",) or k.startswith("mouthStretch") or k.startswith("mouthFunnel") or k.startswith("mouthPucker"):
                pass
            self._key(k, f, d.get(k, 0.0) * intensidad)
    def parpadeo(self, f, doble=False, parcial=1.0):
        """Parpadeo natural de unos 0,2 s (cierra en 2-3 fotogramas, abre en 4-5)."""
        kb = self._kb()
        if not kb: return
        for lado in ("Left", "Right"):
            k = kb[f"eyeBlink{lado}"]
            self.sc.frame_set(f - 1); base = k.value
            for df, v in ((-1, base), (1, base + (1 - base) * 0.55 * parcial), (2, base + (1 - base) * parcial), (3, base + (1 - base) * parcial * 0.9), (7, base)):
                k.value = v; k.keyframe_insert("value", frame=f + df)
        if doble: self.parpadeo(f + 9, False, parcial * 0.85)
    def parpadeos_auto(self, f0, f1, semilla=11, evitar=()):
        import random
        rnd = random.Random(semilla); fps = self.sc.render.fps; f = f0 + rnd.randint(int(0.8 * fps), int(2.5 * fps))
        while f < f1 - 8:
            if not any(a <= f <= b for a, b in evitar):
                self.parpadeo(f, doble=rnd.random() < 0.12, parcial=1.0 if rnd.random() > 0.15 else 0.6)
            f += rnd.randint(int(2.0 * fps), int(5.0 * fps))
    def mirar(self, f, x=0.0, z=0.0, tiempo=None):
        """Mueve el hueso 'Mirada' (x + = su izquierda, z + = arriba, en metros del modelo; el objetivo está a 1 m:
        0,10 son unos 6 grados) y pone clave."""
        b = self.pb.get("Mirada")
        if not b: return
        b.location = Vector((x, z, 0.0)); b.keyframe_insert("location", frame=f)
    def mirada_viva(self, f0, f1, semilla=5, amplitud=0.026):
        """Microsacadas: la mirada salta un poco cada 0,5-1,5 s (así no parece fija)."""
        import random
        rnd = random.Random(semilla); fps = self.sc.render.fps; f = f0
        bx, bz = 0.0, 0.0
        while f < f1:
            x = bx + rnd.uniform(-amplitud, amplitud); z = bz + rnd.uniform(-amplitud * 0.6, amplitud * 0.6)
            self.mirar(f, x, z); self.mirar(f + 2, x, z)
            f += rnd.randint(int(0.5 * fps), int(1.5 * fps))
    def hablar(self, palabras, f_inicio=1, intensidad=1.0, fps=None):
        """Labios a partir de las palabras con tiempos (las de Ootto: [{'text','start','end'} en segundos]).
        Cada letra se reparte en el tiempo de su palabra (las vocales pesan más) y pone su visema."""
        fps = fps or self.sc.render.fps
        usados = sorted({k for d in VISEMAS.values() for k in d})
        def poner(f, vis, k_=1.0):
            d = VISEMAS[vis]
            for k in usados: self._key(k, f, d.get(k, 0.0) * intensidad * k_)
        ult = None
        for w in palabras:
            txt = "".join(c for c in w["text"].lower() if c.isalpha() or c in "áéíóúüñ")
            if not txt: continue
            t0, t1 = w["start"], w["end"]
            pesos = [1.6 if _LETRA.get(c, "") in "aeiou" else 1.0 for c in txt]
            tot = sum(pesos); t = t0
            for c, p_ in zip(txt, pesos):
                dur = (t1 - t0) * p_ / tot; vis = _LETRA.get(c)
                if vis and vis != "kg" or vis == "kg":
                    f = f_inicio + int(round((t + dur * 0.5) * fps))
                    if f != ult: poner(f, vis, 1.0 if vis in "aeiou" else 0.75); ult = f
                t += dur
            # al final de la palabra, la boca se relaja un poco
            f_fin = f_inicio + int(round(t1 * fps)) + 2
            if f_fin != ult: poner(f_fin, "reposo"); ult = f_fin
    for n_, fn_ in list(locals().items()):
        if callable(fn_) and not n_.startswith("__") and n_ not in ("cls",):
            setattr(cls, n_, fn_)
    return cls

_cara_metodos(MaiteAnim)
