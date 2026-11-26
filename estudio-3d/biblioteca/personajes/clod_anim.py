# CLOD v2 · FUNCIONES DE ANIMACIÓN.  Uso:  exec(open(ruta).read());  CL = ClodAnim()   (o ClodAnim("CLOD_v2"))
# Unidades de DISEÑO: Clod mide 1 (se multiplica por K = 0,32 m). Espacio del personaje: mira hacia -Y,
# +X = su izquierda, +Z = arriba. Lado "R" = derecho (en -X), "L" = izquierdo (en +X).
# Piezas rígidas (robot): nada se deforma. Brazos y piernas por IK; cabeza y cuerpo por rotación.
import bpy, math, random
from mathutils import Vector, Euler, Quaternion

_RC = math.radians

EXPR_CLOD = {   # ojos (shape keys de CLOD_Ojo_*), boca (shape keys de CLOD_Boca)
    "neutra":   ({}, {}),
    "contento": ({}, {}),                                     # base: ojos ovalados + sonrisa suave
    "feliz":    ({"feliz": 1}, {"grande": 0.8}),
    "risa":     ({"feliz": 1}, {"grande": 1}),
    "sorpresa": ({"ojo_grande": 1}, {"O": 1}),
    "susto":    ({"ojo_grande": 1}, {"plana": 0.6, "O": 0.5}),
    "enfado":   ({"enfado": 1}, {"plana": 1}),
    "triste":   ({"triste": 1}, {"triste_boca": 1}),
    "duda":     ({"triste": 0.35}, {"plana": 0.7}),
    "serio":    ({"enfado": 0.3}, {"plana": 1}),
}


class ClodAnim:
    def __init__(self, nombre="CLOD_v2", K=0.32):
        self.arm = bpy.data.objects[nombre]; self.PB = self.arm.pose.bones; self.K = K
        sfx = nombre[len("CLOD_v2"):]            # por si hay varias copias (CLOD_v2.001 ...)
        self.sfx = sfx
        self.ctrl = {o.name.replace(sfx, "") if sfx else o.name: o for o in bpy.data.objects
                     if o.name.startswith("CTRLC_") and o.parent == self.arm}
        if "reposo_ctrl" not in self.arm:
            self.arm["reposo_ctrl"] = repr({k: tuple(o.location) for k, o in self.ctrl.items()})
        self.REP = {k: Vector(v) for k, v in eval(self.arm["reposo_ctrl"]).items()}
        def ob(n): return bpy.data.objects.get(n + sfx) or bpy.data.objects.get(n)
        self.ojos = [ob("CLOD_Ojo_R"), ob("CLOD_Ojo_L")]; self.bocaob = ob("CLOD_Boca")
        if "ojos_reposo" not in self.arm:
            self.arm["ojos_reposo"] = repr([tuple(o.location) for o in self.ojos])
        self.OJO0 = [Vector(v) for v in eval(self.arm["ojos_reposo"])]
        for pb in self.PB: pb.rotation_mode = 'XYZ'

    # -------------------------------------------------- utilidades
    def V(self, p): return Vector(p) * self.K
    def _k(self, obj, f, path): obj.keyframe_insert(path, frame=f)
    def _rot(self, hueso, f, rx=0, ry=0, rz=0, peso=1.0):
        """Gira un hueso alrededor de los ejes del personaje (grados)."""
        b = self.PB[hueso]; b.rotation_mode = 'QUATERNION'
        rest = b.bone.matrix_local.to_quaternion()
        qc = Euler((_RC(rx * peso), _RC(ry * peso), _RC(rz * peso))).to_quaternion()
        b.rotation_quaternion = rest.inverted() @ qc @ rest
        self._k(b, f, "rotation_quaternion")

    # -------------------------------------------------- cuerpo
    def cabeza(self, f, asiente=0, inclina=0, gira=0):
        """asiente>0 baja la cara; inclina>0 hacia su izquierda; gira>0 mira a su izquierda."""
        self._rot("cuello", f, asiente, inclina, gira, 0.3); self._rot("cabeza", f, asiente, inclina, gira, 0.7)
    def cuerpo(self, f, adelante=0, lado=0, giro=0):
        self._rot("cuerpo", f, adelante, lado, giro)
    def cadera(self, f, off=(0, 0, 0), giro=(0, 0, 0)):
        """Mueve la pelvis (unidades de diseño). Los pies se quedan por IK."""
        b = self.PB["cadera"]; rest = b.bone.matrix_local
        b.location = rest.to_3x3().inverted() @ self.V(off); self._k(b, f, "location")
        self._rot("cadera", f, *giro)
    def aplastar(self, f, s=1.0):
        """s<1 aplasta, s>1 estira (conserva el volumen). Afecta a cuerpo, cabeza y brazos (no a las piernas)."""
        b = self.PB["cuerpo"]; w = 1 / math.sqrt(s)
        b.scale = (w, s, w); self._k(b, f, "scale")
    def _loc_en(self, obj, f):
        """Posición clave de un control en el fotograma f (lee sus curvas)."""
        ad = obj.animation_data; v = list(obj.location)
        if ad and ad.action:
            try: curvas = list(ad.action.fcurves)
            except Exception: curvas = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
            for fc in curvas:
                if fc.data_path == "location": v[fc.array_index] = fc.evaluate(f)
        return Vector(v)
    def manos_siguen(self, f_ref, f, off=(0, 0, 0)):
        """Las manos conservan la pose que tenían en f_ref, desplazadas con el cuerpo (saltos, rebotes)."""
        for l in ("R", "L"):
            o = self.ctrl["CTRLC_mano_" + l]; o.location = self._loc_en(o, f_ref) + self.V(off); self._k(o, f, "location")
    def mover(self, f, pos=(0, 0, 0), giro_z=0):
        """Coloca a Clod en el mundo (metros) y su giro (grados)."""
        self.arm.location = pos; self.arm.rotation_euler = (0, 0, _RC(giro_z))
        self._k(self.arm, f, "location"); self._k(self.arm, f, "rotation_euler")

    # -------------------------------------------------- brazos y piernas
    def _abs(self, n, f, pos):
        o = self.ctrl["CTRLC_" + n]; o.location = self.V(pos); self._k(o, f, "location")
    def mano_en(self, lado, f, pos): self._abs("mano_" + lado, f, pos)
    def codo_hacia(self, lado, f, pos): self._abs("codo_" + lado, f, pos)
    def pie_en(self, lado, f, pos, giro=(0, 0, 0)):
        self._abs("pie_" + lado, f, pos)
        o = self.ctrl["CTRLC_pie_" + lado]; o.rotation_euler = tuple(_RC(a) for a in giro); self._k(o, f, "rotation_euler")
    def rodilla_hacia(self, lado, f, pos): self._abs("rodilla_" + lado, f, pos)
    def brazo_caido(self, lado, f):
        s = -1 if lado == "R" else 1
        self.mano_en(lado, f, (s * 0.252, -0.016, 0.27)); self.codo_hacia(lado, f, (s * 0.30, 0.45, 0.38))
        self.mano_giro(lado, f); self.pulgar(lado, f, 0)
    def mano_giro(self, lado, f, dobla=0, desvia=0, gira=0):
        b = self.PB["mano." + lado]; b.rotation_mode = 'XYZ'
        b.rotation_euler = (_RC(dobla), _RC(gira), _RC(desvia)); self._k(b, f, "rotation_euler")
    def pulgar(self, lado, f, abre=0.0):
        """abre 0 = pegado; 1 = estirado hacia fuera."""
        b = self.PB["pulgar." + lado]; b.rotation_mode = 'XYZ'; s = -1 if lado == "R" else 1
        b.rotation_euler = (_RC(-35 * abre), 0, _RC(s * 25 * abre)); self._k(b, f, "rotation_euler")
    def reposo(self, f):
        for l in ("R", "L"):
            s = -1 if l == "R" else 1
            self.brazo_caido(l, f); self.pie_en(l, f, (s * 0.115, 0.0, 0.07)); self.rodilla_hacia(l, f, (s * 0.115, -0.45, 0.19))
        self.cabeza(f); self.cuerpo(f); self.cadera(f); self.aplastar(f, 1.0)
        self.cara(f, "contento"); self.mirar(f)

    # -------------------------------------------------- pantalla LED
    def _sk(self, ob, nombre): return ob.data.shape_keys.key_blocks[nombre]
    def cara(self, f, expresion="contento", intensidad=1.0):
        ojos, boca = EXPR_CLOD[expresion]
        for o in self.ojos:
            for kb in o.data.shape_keys.key_blocks[1:]:
                if kb.name == "cerrado": continue
                kb.value = ojos.get(kb.name, 0.0) * intensidad; kb.keyframe_insert("value", frame=f)
        for kb in self.bocaob.data.shape_keys.key_blocks[1:]:
            if kb.name.endswith("_habla"): continue           # el habla va aparte (se suma a la expresión)
            kb.value = boca.get(kb.name, 0.0) * intensidad; kb.keyframe_insert("value", frame=f)
    def parpadeo(self, f, lado=None):
        for i, o in enumerate(self.ojos):
            if lado and ((lado == "R") != (i == 0)): continue
            kb = self._sk(o, "cerrado")
            for df, v in ((-1, 0), (1, 1), (2, 1), (4, 0)): kb.value = v; kb.keyframe_insert("value", frame=f + df)
    def parpadeos(self, f0, f1, cada=(60, 100), evitar=()):
        rnd = random.Random(11); f = f0 + rnd.randint(8, 30)
        while f < f1 - 5:
            if all(not (a - 6 <= f <= b + 6) for a, b in evitar): self.parpadeo(f)
            f += rnd.randint(*cada)
    def mirar(self, f, x=0.0, z=0.0):
        """Mueve los ojos LED por la pantalla (unidades de diseño; x>0 hacia su izquierda)."""
        for o, p0 in zip(self.ojos, self.OJO0):
            o.location = p0 + self.V((x, 0, z)); self._k(o, f, "location")
    def _boca_habla(self):
        kbs = self.bocaob.data.shape_keys.key_blocks
        for n in ("abierta", "O"):
            if n + "_habla" not in kbs:
                nk = self.bocaob.shape_key_add(name=n + "_habla", from_mix=False); nk.value = 0
                for i, d in enumerate(kbs[n].data): nk.data[i].co = d.co
        return kbs["abierta_habla"], kbs["O_habla"]
    def hablar(self, lineas, fps=30, desfase=0.0):
        """lineas: [{"at": seg, "words": [[texto, ini, fin], ...]}]. La boca LED se abre por sílabas."""
        ab, oo = self._boca_habla()
        for kb in (ab, oo): kb.value = 0; kb.keyframe_insert("value", frame=1)
        for ln in lineas:
            t0 = ln["at"] + desfase
            for i, w in enumerate(ln["words"]):
                txt, a, b = w[0].lower(), w[1], w[2]
                fa = int(round((t0 + a) * fps)) + 1; fb = max(int(round((t0 + b) * fps)) + 1, fa + 3)
                voc = max(1, sum(ch in "aeiouáéíóú" for ch in txt)); n = max(1, min(voc, (fb - fa) // 3))
                ab.value = 0.05; ab.keyframe_insert("value", frame=fa - 1)
                for k in range(n):
                    fk = fa + int((k + 0.5) * (fb - fa) / n)
                    ab.value = 0.5 + 0.5 * (((i + k) * 37) % 5) / 4; ab.keyframe_insert("value", frame=fk)
                    if k < n - 1: ab.value = 0.15; ab.keyframe_insert("value", frame=fa + int((k + 1) * (fb - fa) / n))
                ab.value = 0.05; ab.keyframe_insert("value", frame=fb)
                if any(c in txt for c in "ouóú"):
                    for fx, v in ((fa - 1, 0), ((fa + fb) // 2, 0.55), (fb + 1, 0)): oo.value = v; oo.keyframe_insert("value", frame=fx)
            fin = int(round((t0 + ln["words"][-1][2]) * fps)) + 1
            ab.value = 0; ab.keyframe_insert("value", frame=fin + 2)

    # -------------------------------------------------- gestos (devuelven el fotograma final)
    def saludo(self, lado, f0, ciclos=3, vel=6):
        s = -1 if lado == "R" else 1; f = f0
        self.mano_en(lado, f + 8, (s * 0.31, -0.06, 0.70)); self.codo_hacia(lado, f + 8, (s * 0.6, 0.3, 0.45))
        self.pulgar(lado, f + 8, 0.6); f += 8
        for i in range(ciclos):
            self.mano_en(lado, f + vel, (s * 0.22, -0.07, 0.71)); self.mano_en(lado, f + 2 * vel, (s * 0.33, -0.06, 0.70)); f += 2 * vel
        return f
    def pulgar_arriba(self, lado, f, dur=30):
        s = -1 if lado == "R" else 1
        self.mano_en(lado, f, (s * 0.17, -0.19, 0.44)); self.codo_hacia(lado, f, (s * 0.45, 0.25, 0.30))
        self.pulgar(lado, f, 1.0); self.mano_giro(lado, f, 0, 0, s * -20)
        self.mano_en(lado, f + 4, (s * 0.17, -0.20, 0.46)); self.mano_en(lado, f + dur, (s * 0.17, -0.19, 0.45))
        return f + dur
    def salto(self, f0, alto=0.25, aire=10):
        """Anticipación (se aplasta), salto con estiramiento, aterrizaje con rebote. Pies por IK; las manos acompañan."""
        f = f0
        def cuerpo_en(fx, dz, sq):
            self.cadera(fx, (0, 0, dz)); self.aplastar(fx, sq); self.manos_siguen(f0, fx, (0, 0, dz))
        cuerpo_en(f, 0, 1.0)
        f += 5; cuerpo_en(f, -0.06, 0.82)
        f += 4; cuerpo_en(f, 0.02, 1.15)
        for l in ("R", "L"):
            s = -1 if l == "R" else 1
            self.pie_en(l, f0, (s * 0.115, 0.0, 0.07)); self.pie_en(l, f, (s * 0.115, 0.0, 0.07))
        top = f + aire // 2
        for l in ("R", "L"):
            s = -1 if l == "R" else 1; self.pie_en(l, top, (s * 0.115, 0.0, 0.07 + alto))
        cuerpo_en(top, alto, 1.05)
        f = f + aire
        for l in ("R", "L"):
            s = -1 if l == "R" else 1; self.pie_en(l, f, (s * 0.115, 0.0, 0.07))
        cuerpo_en(f, 0.0, 1.1)
        f += 3; cuerpo_en(f, -0.05, 0.85)
        f += 5; cuerpo_en(f, 0.01, 1.04)
        f += 5; cuerpo_en(f, 0.0, 1.0)
        return f
    def rebote(self, f0, veces=2, alto=0.03, cada=7):
        """Saltitos de alegría sin despegar los pies (rodillas y cuerpo)."""
        f = f0
        for i in range(veces):
            self.cadera(f, (0, 0, -alto)); self.aplastar(f, 0.92); self.manos_siguen(f0, f, (0, 0, -alto))
            self.cadera(f + cada // 2, (0, 0, alto * 0.6)); self.aplastar(f + cada // 2, 1.06); self.manos_siguen(f0, f + cada // 2, (0, 0, alto * 0.6))
            f += cada
        self.cadera(f); self.aplastar(f, 1.0); self.manos_siguen(f0, f)
        return f
    def andar(self, f0, pasos=4, zancada=0.25, fp=8, giro_z=0, desde=None):
        """Pasitos de robot: avanza en el mundo (zancada en unidades de diseño) con rebote."""
        z = _RC(giro_z)
        pos0 = Vector(desde) if desde is not None else self.arm.location.copy()
        paso = Vector((-math.sin(z), -math.cos(z), 0)) * zancada * self.K
        f = f0
        self.mover(f, tuple(pos0), giro_z)
        for i in range(pasos):
            l = "R" if i % 2 == 0 else "L"; s = -1 if l == "R" else 1
            fm = f + fp // 2
            self.pie_en(l, f, (s * 0.115, 0.0, 0.07))
            self.pie_en(l, fm, (s * 0.115, -zancada * 0.5, 0.13)); self.cadera(fm, (s * -0.01, 0, 0.025)); self.aplastar(fm, 1.04)
            f += fp
            self.pie_en(l, f, (s * 0.115, 0.0, 0.07)); self.cadera(f, (0, 0, -0.01)); self.aplastar(f, 0.97)
            self.mover(f, tuple(pos0 + paso * (i + 1)), giro_z)
        self.cadera(f + 4); self.aplastar(f + 4, 1.0)
        return f

    def suavizar(self):
        for ob in [self.arm] + list(self.ctrl.values()) + self.ojos + [self.bocaob]:
            for idb in (ob, getattr(ob.data, "shape_keys", None)):
                ad = getattr(idb, "animation_data", None) if idb else None
                if not ad or not ad.action: continue
                try: curvas = list(ad.action.fcurves)
                except Exception: curvas = [fc for l in ad.action.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]
                for fc in curvas:
                    for k in fc.keyframe_points:
                        if k.interpolation == 'LINEAR': continue
                        k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
                    fc.update()
