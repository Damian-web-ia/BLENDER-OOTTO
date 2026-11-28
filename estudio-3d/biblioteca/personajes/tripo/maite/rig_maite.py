# RIG CORPORAL DE MAITE (fase 3) · EKORUEDAS · 28-11-2026
# Encima del esqueleto Mixamo (que sigue deformando la malla) se añade una capa de controles:
#   - CTRL_raiz en el suelo (padre de Hips: Hips hace de centro de gravedad).
#   - Piernas con IK (encendido por defecto): IK_pie_L/R, POLO_rodilla_L/R, pie inverso con TALÓN / PUNTA / BOLA
#     y propiedad "roll" (-1 talón ... 0 plano ... 0,5 sobre la bola ... 1 de puntillas).
#   - Brazos FK por defecto con IK disponible (propiedad ik_brazo_L/R 0..1): IK_mano_L/R, POLO_codo_L/R.
#   - Giro del antebrazo repartido (hueso GIRO_antebrazo_L/R que deforma la mitad de la muñeca): sin "caramelo".
#   - Dedos: control MANO_dedos_L/R (girar en X = cerrar el puño, en Z = abrir los dedos) sumado al FK de cada dedo.
#   - Suavizado correctivo en articulaciones (hombros, codos, muñecas, caderas, rodillas, tobillos).
#   - Colecciones de huesos (Controles / Mecanismo / Deformación), formas de control y colores.
# Uso: exec desde construir_maite_v2.py ->  RIG["montar_rig"](ARM, ME)
import bpy, math
import numpy as np
from mathutils import Vector, Matrix

P = "mixamorig:"
LADOS = (("Left", "L"), ("Right", "R"))
DEDOS = ("Index", "Middle", "Ring", "Pinky", "Thumb")


def _angulo_con_signo(v1, v2, normal):
    a = v1.angle(v2)
    return -a if v1.cross(v2).dot(normal) < 0 else a


def _angulo_polo(base, punta, polo):
    """Ángulo de polo de Blender para una cadena de 2 huesos (edit bones)."""
    n = (punta.tail - base.head).cross(polo - base.head)
    proy = n.cross(base.tail - base.head)
    return _angulo_con_signo(base.x_axis, proy, base.tail - base.head)


def _nuevo(eb, nombre, cabeza, cola, padre=None, roll=0.0, deforma=False):
    b = eb.get(nombre) or eb.new(nombre)
    b.head = Vector(cabeza); b.tail = Vector(cola); b.roll = roll; b.parent = padre; b.use_deform = deforma; b.use_connect = False
    return b


def _forma(nombre, tipo):
    """Mallas de las formas de control (ocultas)."""
    ob = bpy.data.objects.get(nombre)
    if ob: return ob
    me = bpy.data.meshes.new(nombre)
    if tipo == "circulo":
        n = 32; v = [(math.cos(2 * math.pi * k / n), 0.0, math.sin(2 * math.pi * k / n)) for k in range(n)]
        e = [(k, (k + 1) % n) for k in range(n)]
    elif tipo == "cuadrado":
        v = [(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)]; e = [(0, 1), (1, 2), (2, 3), (3, 0)]
    elif tipo == "rombo":
        v = [(0, 0, 1), (1, 0, 0), (0, 0, -1), (-1, 0, 0), (0, 1, 0), (0, -1, 0)]
        e = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3), (5, 0), (5, 1), (5, 2), (5, 3)]
    else:   # flecha (para el roll del pie y los dedos)
        v = [(0, 0, 0), (0, 1, 0), (-0.25, 0.75, 0), (0.25, 0.75, 0)]; e = [(0, 1), (1, 2), (1, 3)]
    me.from_pydata(v, e, []); me.update()
    ob = bpy.data.objects.new(nombre, me)
    col = bpy.data.collections.get("MAITE_formas") or bpy.data.collections.new("MAITE_formas")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    col.objects.link(ob); col.hide_render = True; col.hide_viewport = True
    return ob


def _driver(pb_owner, ruta, indice, arm, var_bone, var_prop, expr):
    fc = pb_owner.driver_add(ruta, indice) if indice is not None else pb_owner.driver_add(ruta)
    d = fc.driver; d.type = 'SCRIPTED'
    for v in list(d.variables): d.variables.remove(v)
    v = d.variables.new(); v.name = "v"; v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'; v.targets[0].id = arm
    v.targets[0].data_path = f'pose.bones["{var_bone}"]["{var_prop}"]'
    d.expression = expr
    return fc


def montar_rig(arm, me):
    bpy.context.view_layer.objects.active = arm
    for o in bpy.context.view_layer.objects: o.select_set(False)
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    hips = eb[P + "Hips"]
    raiz = _nuevo(eb, "CTRL_raiz", (hips.head.x, hips.head.y, 0.0), (hips.head.x, hips.head.y - 0.22, 0.0))
    hips.parent = raiz; hips.use_connect = False
    signos_piv = {}; polos = {}
    for lado, l in LADOS:
        upleg, leg, foot = eb[P + lado + "UpLeg"], eb[P + lado + "Leg"], eb[P + lado + "Foot"]
        toe, toe_end = eb[P + lado + "ToeBase"], eb[P + lado + "Toe_End"]
        tob = foot.head.copy(); suelo = 0.004
        ik_pie = _nuevo(eb, f"IK_pie_{l}", (tob.x, tob.y, suelo), (tob.x, tob.y - 0.09, suelo), raiz)
        talon = _nuevo(eb, f"PIV_talon_{l}", (tob.x, tob.y + 0.028, suelo), (tob.x, tob.y + 0.028 - 0.03, suelo), ik_pie)
        pt = toe_end.tail.copy()
        punta = _nuevo(eb, f"PIV_punta_{l}", (pt.x, pt.y, suelo), (pt.x, pt.y - 0.03, suelo), talon)
        bo = toe.head.copy()
        bola = _nuevo(eb, f"PIV_bola_{l}", (bo.x, bo.y, bo.z), (bo.x, bo.y - 0.03, bo.z), punta)
        _nuevo(eb, f"IKT_tobillo_{l}", foot.head, foot.tail, bola, roll=foot.roll)
        _nuevo(eb, f"IKT_dedos_{l}", toe.head, toe.tail, punta, roll=toe.roll)
        polo = _nuevo(eb, f"POLO_rodilla_{l}", leg.head + Vector((0, -0.32, 0)), leg.head + Vector((0, -0.35, 0)), ik_pie)
        polos[f"pierna_{l}"] = _angulo_polo(upleg, leg, polo.head)
        for nm in ("talon", "punta", "bola"):
            signos_piv[f"PIV_{nm}_{l}"] = 1.0 if eb[f"PIV_{nm}_{l}"].x_axis.x > 0 else -1.0
        # brazos
        brazo, ante, mano = eb[P + lado + "Arm"], eb[P + lado + "ForeArm"], eb[P + lado + "Hand"]
        _nuevo(eb, f"IK_mano_{l}", mano.head, mano.tail, raiz, roll=mano.roll)
        pc = _nuevo(eb, f"POLO_codo_{l}", ante.head + Vector((0, 0.30, 0)), ante.head + Vector((0, 0.33, 0)), raiz)
        polos[f"brazo_{l}"] = _angulo_polo(brazo, ante, pc.head)
        _nuevo(eb, f"GIRO_antebrazo_{l}", ante.head.lerp(ante.tail, 0.5), ante.tail, ante, roll=ante.roll, deforma=True)
        # control de dedos sobre el dorso de la mano
        eje = (mano.tail - mano.head).normalized()
        dorso = mano.z_axis.normalized()
        c = mano.head.lerp(mano.tail, 0.4) + dorso * 0.035
        _nuevo(eb, f"MANO_dedos_{l}", c, c + eje * 0.04, mano, roll=mano.roll)
    bpy.ops.object.mode_set(mode='POSE')
    pb = arm.pose.bones
    # ---- propiedades
    def prop(bone, nombre, valor, mn, mx, desc):
        b = pb[bone]; b[nombre] = valor
        ui = b.id_properties_ui(nombre); ui.update(min=mn, max=mx, soft_min=mn, soft_max=mx, description=desc)
    for lado, l in LADOS:
        prop("CTRL_raiz", f"ik_pierna_{l}", 1.0, 0.0, 1.0, "1 = pierna con IK (pie fijo en el suelo), 0 = FK")
        prop("CTRL_raiz", f"ik_brazo_{l}", 0.0, 0.0, 1.0, "1 = mano con IK (sujeta objetos), 0 = FK")
        prop(f"IK_pie_{l}", "roll", 0.0, -1.0, 1.0, "-1 talón · 0 plano · 0,5 sobre la bola · 1 de puntillas")
    # ---- piernas
    for lado, l in LADOS:
        for nm in ("talon", "punta", "bola"): pb[f"PIV_{nm}_{l}"].rotation_mode = 'XYZ'
        leg = pb[P + lado + "Leg"]
        for c in [c for c in leg.constraints if c.name.startswith("IK_")]: leg.constraints.remove(c)
        ik = leg.constraints.new('IK'); ik.name = "IK_pierna"
        ik.target = arm; ik.subtarget = f"IKT_tobillo_{l}"; ik.pole_target = arm; ik.pole_subtarget = f"POLO_rodilla_{l}"
        ik.pole_angle = polos[f"pierna_{l}"]; ik.chain_count = 2; ik.use_tail = True
        _driver(ik, "influence", None, arm, "CTRL_raiz", f"ik_pierna_{l}", "v")
        for hueso, objetivo, nombre in ((P + lado + "Foot", f"IKT_tobillo_{l}", "IK_pie"), (P + lado + "ToeBase", f"IKT_dedos_{l}", "IK_dedos")):
            b = pb[hueso]
            for c in [c for c in b.constraints if c.name == nombre]: b.constraints.remove(c)
            cr = b.constraints.new('COPY_ROTATION'); cr.name = nombre; cr.target = arm; cr.subtarget = objetivo
            _driver(cr, "influence", None, arm, "CTRL_raiz", f"ik_pierna_{l}", "v")
        # roll del pie
        s = signos_piv
        _driver(pb[f"PIV_talon_{l}"], "rotation_euler", 0, arm, f"IK_pie_{l}", "roll", f"{s[f'PIV_talon_{l}']}*min(v,0)*0.75")
        _driver(pb[f"PIV_bola_{l}"], "rotation_euler", 0, arm, f"IK_pie_{l}", "roll", f"{s[f'PIV_bola_{l}']}*min(max(v,0),0.5)*2*0.55")
        _driver(pb[f"PIV_punta_{l}"], "rotation_euler", 0, arm, f"IK_pie_{l}", "roll", f"{s[f'PIV_punta_{l}']}*max(v-0.5,0)*2*0.6")
    # ---- brazos
    for lado, l in LADOS:
        ante = pb[P + lado + "ForeArm"]
        for c in [c for c in ante.constraints if c.name.startswith("IK_")]: ante.constraints.remove(c)
        ik = ante.constraints.new('IK'); ik.name = "IK_brazo"
        ik.target = arm; ik.subtarget = f"IK_mano_{l}"; ik.pole_target = arm; ik.pole_subtarget = f"POLO_codo_{l}"
        ik.pole_angle = polos[f"brazo_{l}"]; ik.chain_count = 2; ik.use_tail = True
        _driver(ik, "influence", None, arm, "CTRL_raiz", f"ik_brazo_{l}", "v")
        mano = pb[P + lado + "Hand"]
        for c in [c for c in mano.constraints if c.name == "IK_mano"]: mano.constraints.remove(c)
        cr = mano.constraints.new('COPY_ROTATION'); cr.name = "IK_mano"; cr.target = arm; cr.subtarget = f"IK_mano_{l}"
        _driver(cr, "influence", None, arm, "CTRL_raiz", f"ik_brazo_{l}", "v")
        # giro del antebrazo: la mitad del giro de la muñeca (eje Y local)
        g = pb[f"GIRO_antebrazo_{l}"]
        for c in list(g.constraints): g.constraints.remove(c)
        cg = g.constraints.new('COPY_ROTATION'); cg.name = "giro_muneca"; cg.target = arm; cg.subtarget = P + lado + "Hand"
        cg.use_x = False; cg.use_z = False; cg.use_y = True
        cg.target_space = 'LOCAL'; cg.owner_space = 'LOCAL'; cg.mix_mode = 'ADD'; cg.influence = 0.5
        # dedos: el control suma su giro (X: cerrar, Z: abrir) a cada falange
        reparto = {"Index": -1.0, "Middle": -0.35, "Ring": 0.4, "Pinky": 1.0, "Thumb": 0.0}
        for dedo in DEDOS:
            for k in (1, 2, 3):
                nb = P + lado + "Hand" + dedo + str(k)
                if nb not in pb: continue
                b = pb[nb]
                for c in [c for c in b.constraints if c.name == "dedos"]: b.constraints.remove(c)
                t = b.constraints.new('TRANSFORM'); t.name = "dedos"; t.target = arm; t.subtarget = f"MANO_dedos_{l}"
                t.map_from = 'ROTATION'; t.map_to = 'ROTATION'; t.target_space = 'LOCAL'; t.owner_space = 'LOCAL'
                t.mix_mode_rot = 'AFTER'
                f_curl = (0.55 if dedo == "Thumb" else 1.0) * (1.0 if k > 1 else 0.85) * (1.0 if l == "L" else -1.0)   # espejo
                t.from_min_x_rot, t.from_max_x_rot = -math.pi / 2, math.pi / 2
                t.to_min_x_rot, t.to_max_x_rot = -math.pi / 2 * f_curl, math.pi / 2 * f_curl
                t.map_to_x_from = 'X'
                f_ab = (reparto[dedo] if k == 1 else 0.0) * (1.0 if l == "L" else -1.0)
                t.from_min_z_rot, t.from_max_z_rot = -math.pi / 4, math.pi / 4
                t.to_min_z_rot, t.to_max_z_rot = -math.pi / 4 * f_ab, math.pi / 4 * f_ab
                t.map_to_z_from = 'Z'
                t.map_to_y_from = 'Y'; t.from_min_y_rot = t.from_max_y_rot = 0.0; t.to_min_y_rot = t.to_max_y_rot = 0.0
        pb[f"MANO_dedos_{l}"].rotation_mode = 'XYZ'
    # ---- formas, colecciones y colores
    formas = {"circulo": _forma("FORMA_circulo", "circulo"), "cuadrado": _forma("FORMA_cuadrado", "cuadrado"),
              "rombo": _forma("FORMA_rombo", "rombo"), "flecha": _forma("FORMA_flecha", "flecha")}
    cols = {}
    for nombre in ("Controles", "Mecanismo", "Deformacion"):
        cols[nombre] = arm.data.collections.get(nombre) or arm.data.collections.new(nombre)
    def asigna(nombre_hueso, col, forma=None, escala=1.0, paleta=None):
        b = arm.data.bones[nombre_hueso]; cols[col].assign(b)
        if forma: pb[nombre_hueso].custom_shape = formas[forma]; pb[nombre_hueso].custom_shape_scale_xyz = (escala, escala, escala)
        if paleta: pb[nombre_hueso].color.palette = paleta
    asigna("CTRL_raiz", "Controles", "cuadrado", 1.2, 'THEME09')
    asigna(P + "Hips", "Controles", "circulo", 2.2, 'THEME09')
    for lado, l in LADOS:
        pal = 'THEME01' if l == "L" else 'THEME04'
        asigna(f"IK_pie_{l}", "Controles", "cuadrado", 0.5, pal)
        asigna(f"IK_mano_{l}", "Controles", "circulo", 0.9, pal)
        asigna(f"POLO_rodilla_{l}", "Controles", "rombo", 0.3, pal)
        asigna(f"POLO_codo_{l}", "Controles", "rombo", 0.3, pal)
        asigna(f"MANO_dedos_{l}", "Controles", "flecha", 0.6, pal)
        for nm in (f"PIV_talon_{l}", f"PIV_punta_{l}", f"PIV_bola_{l}", f"IKT_tobillo_{l}", f"IKT_dedos_{l}"):
            asigna(nm, "Mecanismo")
        asigna(f"GIRO_antebrazo_{l}", "Deformacion")
    for b in arm.data.bones:
        if b.name.startswith(P) and not b.collections: cols["Deformacion"].assign(b)
    cols["Mecanismo"].is_visible = False
    bpy.ops.object.mode_set(mode='OBJECT')
    _pesos_giro(arm, me)
    _suavizado_articulaciones(arm, me)
    print("RIG listo: IK piernas (on) y brazos (off), roll de pie, giro de antebrazo, dedos, suavizado; polos",
          {k: round(math.degrees(v), 1) for k, v in polos.items()}, "signos", signos_piv, flush=True)


def _pesos_giro(arm, me):
    """Reparte el peso del antebrazo: hacia la muñeca, una parte pasa al hueso de giro."""
    m = me.data; N = len(m.vertices)
    co = np.empty(N * 3); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    for lado, l in LADOS:
        gfa = me.vertex_groups.get(P + lado + "ForeArm")
        if gfa is None: continue
        gg = me.vertex_groups.get(f"GIRO_antebrazo_{l}") or me.vertex_groups.new(name=f"GIRO_antebrazo_{l}")
        b = arm.data.bones[P + lado + "ForeArm"]
        A = np.array(arm.matrix_world @ b.head_local); B = np.array(arm.matrix_world @ b.tail_local)
        ab = B - A; L2 = ab @ ab
        idx, w = [], []
        for v in m.vertices:
            for g in v.groups:
                if g.group == gfa.index and g.weight > 0.001:
                    idx.append(v.index); w.append(g.weight); break
        if not idx: continue
        idx = np.array(idx); w = np.array(w)
        t = np.clip(((co[idx] - A) @ ab) / L2, 0, 1)
        parte = w * np.clip((t - 0.25) / 0.65, 0, 1) ** 1.2 * 0.85
        for i, wi, pi in zip(idx, w, parte):
            if pi > 0.002:
                gg.add([int(i)], float(pi), 'REPLACE'); gfa.add([int(i)], float(wi - pi), 'REPLACE')
        print("RIG giro antebrazo", l, int((parte > 0.002).sum()), "vértices", flush=True)


def _suavizado_articulaciones(arm, me):
    """Grupo con peso alrededor de las articulaciones + modificador Corrective Smooth (no deja que se arruguen)."""
    m = me.data; N = len(m.vertices)
    co = np.empty(N * 3); m.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    puntos = []
    for lado, l in LADOS:
        for h, r in (("Arm", 0.06), ("ForeArm", 0.05), ("Hand", 0.035), ("UpLeg", 0.08), ("Leg", 0.065), ("Foot", 0.05)):
            b = arm.data.bones[P + lado + h]; puntos.append((np.array(arm.matrix_world @ b.head_local), r))
    w = np.zeros(N)
    for p, r in puntos:
        d = np.linalg.norm(co - p, axis=1)
        w = np.maximum(w, np.clip(1 - (d / r) ** 2, 0, 1))
    g = me.vertex_groups.get("suave_articulaciones") or me.vertex_groups.new(name="suave_articulaciones")
    sel = np.where(w > 0.01)[0]
    for i in sel: g.add([int(i)], float(w[i]), 'REPLACE')
    md = me.modifiers.get("Suavizado_articulaciones") or me.modifiers.new("Suavizado_articulaciones", 'CORRECTIVE_SMOOTH')
    md.vertex_group = g.name; md.iterations = 6; md.smooth_type = 'LENGTH_WEIGHTED'; md.rest_source = 'ORCO'; md.factor = 0.5
    md.use_pin_boundary = False
    # justo detrás del Armature
    idx_arm = next(i for i, x in enumerate(me.modifiers) if x.type == 'ARMATURE')
    me.modifiers.move(list(me.modifiers).index(md), idx_arm + 1)
    print("RIG suavizado de articulaciones:", len(sel), "vértices", flush=True)
