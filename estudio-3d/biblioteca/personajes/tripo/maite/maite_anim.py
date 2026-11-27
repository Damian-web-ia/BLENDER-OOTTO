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
        for b in self.pb: b.rotation_mode = 'QUATERNION'
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
        "pulgar":   dict(i=85, m=88, a=90, p=92, pul=-25, sep=0),
        "pinza":    dict(i=38, m=20, a=24, p=28, pul=34, sep=3),
        "tensa":    dict(i=-6, m=-4, a=-2, p=0, pul=-15, sep=12),
    }
    def mano(self, f, lado, forma="relajada", muneca=(0, 0, 0)):
        l = _lado(lado); c = self.MANOS.get(forma, self.MANOS["relajada"]); s = 1 if l == L else -1
        for dedo, k, abre in (("Index", "i", 1.0), ("Middle", "m", 0.3), ("Ring", "a", -0.4), ("Pinky", "p", -1.0)):
            for j in (1, 2, 3):
                ang = c[k] * (0.85 if j == 1 else 1.0 if j == 2 else 0.75)
                self.rot(f"mixamorig:{l}Hand{dedo}{j}", f, ang, 0, (c["sep"] * abre * s) if j == 1 else 0)
        for j in (1, 2, 3):
            self.rot(f"mixamorig:{l}HandThumb{j}", f, 0, 0, c["pul"] * s * (0.6 if j == 1 else 0.4))
        self.rot(f"mixamorig:{l}Hand", f, *muneca)

    def hombros(self, f, sube=0.0):
        """sube > 0: encoge los hombros."""
        self.rot("mixamorig:LeftShoulder", f, 0, 0, -sube); self.rot("mixamorig:RightShoulder", f, 0, 0, sube)

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
