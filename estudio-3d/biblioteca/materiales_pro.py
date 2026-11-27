# MATERIALES PRO (EKORUEDAS · 27-11-2026) · más realismo en EEVEE (Blender 5.3)
# Damián (27-11, 15:02): "el aceite parecía solamente un color, tiene que ser como algo líquido ... ve mejorando cómo se ve
# el metal, las piezas del coche ... las texturas ... si hace falta meter más píxeles, metemos más píxeles".
# Uso:  MP = {"__name__": "mp"}; exec(open(".../materiales_pro.py", encoding="utf-8").read(), MP)
#       MP["render_pro"](scene)                       # 100 %, raytracing, sombras finas, AgX
#       m = MP["aceite"]("MP_Aceite")                 # líquido de verdad: transparente, refracta, brilla, superficie viva
#       MP["burbujas"](coleccion, padre, r_max, z0, z1, n, f0, f1)   # burbujas que suben
#       MP["cromo"](), MP["acero"](), MP["pintura"](color), MP["goma"](), MP["corte"]() ...
#       MP["mejorar"](material_existente, tipo)       # cambia el árbol de nodos de un material ya puesto
# Nada de drivers (en el render de fondo no se ejecutan): lo que se mueve va con fotogramas clave y extrapolación lineal.
import bpy, bmesh, math
from mathutils import Vector


def _set(n, nombre, v):
    if nombre in n.inputs: n.inputs[nombre].default_value = v


def _nuevo(nombre):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.use_nodes = True; m.node_tree.nodes.clear()
    return m


def _salida(nt):
    o = nt.nodes.new("ShaderNodeOutputMaterial"); o.location = (900, 0); return o


def _bsdf(nt):
    b = nt.nodes.new("ShaderNodePrincipledBSDF"); b.location = (500, 0); return b


def _objeto(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-900, 0); return tc.outputs["Object"]


def _ruido(nt, vec, escala, detalle=4.0, rugosidad=0.55, w_anim=None, dims='3D'):
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.noise_dimensions = '4D' if w_anim else dims
    nt.links.new(vec, nz.inputs["Vector"]); _set(nz, "Scale", escala); _set(nz, "Detail", detalle); _set(nz, "Roughness", rugosidad)
    if w_anim:
        # W animado con dos claves y extrapolación lineal (sin drivers)
        w = nz.inputs["W"]; w.default_value = 0.0; w.keyframe_insert("default_value", frame=1)
        w.default_value = w_anim; w.keyframe_insert("default_value", frame=101)
        ad = nt.animation_data
        if ad and ad.action:
            try: fcs = list(ad.action.fcurves)
            except Exception: fcs = [fc for l in ad.action.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
            for fc in fcs:
                if nz.name in fc.data_path:
                    fc.extrapolation = 'LINEAR'
                    for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    return nz


def _bump(nt, alto, fuerza, distancia=0.001, normal=None):
    b = nt.nodes.new("ShaderNodeBump"); _set(b, "Strength", fuerza); _set(b, "Distance", distancia)
    nt.links.new(alto, b.inputs["Height"])
    if normal is not None: nt.links.new(normal, b.inputs["Normal"])
    return b.outputs["Normal"]


def _rango(nt, fac, a, b):
    mp = nt.nodes.new("ShaderNodeMapRange"); nt.links.new(fac, mp.inputs["Value"])
    mp.inputs["To Min"].default_value = a; mp.inputs["To Max"].default_value = b
    return mp.outputs["Result"]


def _calor(nt, bsdf, color_frio=None, fuerza=6.0, prop="calor"):
    """La propiedad de escena 'calor' (0-1) enciende un brillo naranja (para frenos y amortiguadores)."""
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'VIEW_LAYER'; at.attribute_name = prop
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = fuerza
    nt.links.new(at.outputs["Fac"], mu.inputs[0]); nt.links.new(mu.outputs[0], bsdf.inputs["Emission Strength"])
    _set(bsdf, "Emission Color", (1.0, 0.32, 0.05, 1))
    return at


# ---------------------------------------------------------------------------------------------- LÍQUIDOS
def aceite(nombre="MP_Aceite", color=(0.78, 0.42, 0.05), calor=True, ondas=True):
    """Aceite de amortiguador / motor: transparente ámbar que refracta lo de detrás, brillo especular nítido,
    superficie con ondas lentas que se mueven solas y, con calor, se vuelve naranja incandescente."""
    m = _nuevo(nombre); nt = m.node_tree; out = _salida(nt); b = _bsdf(nt)
    _set(b, "Base Color", (*color, 1)); _set(b, "Roughness", 0.025); _set(b, "IOR", 1.47)
    _set(b, "Transmission Weight", 1.0); _set(b, "Specular IOR Level", 0.6)
    _set(b, "Coat Weight", 0.25); _set(b, "Coat Roughness", 0.02)
    if ondas:
        ob = _objeto(nt)
        nz = _ruido(nt, ob, 38.0, 3.0, 0.5, w_anim=1.6)
        nz2 = _ruido(nt, ob, 140.0, 2.0, 0.5, w_anim=4.0)
        ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'ADD'
        nt.links.new(nz.outputs["Fac"], ad.inputs[0]); nt.links.new(nz2.outputs["Fac"], ad.inputs[1])
        nt.links.new(_bump(nt, ad.outputs[0], 0.18, 0.002), b.inputs["Normal"])
    if calor:
        at = _calor(nt, b, fuerza=7.0)
        # con calor el tinte pasa de ámbar a naranja rojizo
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        nt.links.new(at.outputs["Fac"], mx.inputs[0]); mx.inputs[6].default_value = (*color, 1); mx.inputs[7].default_value = (1.0, 0.25, 0.04, 1)
        nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    for a, v in (("surface_render_method", 'DITHERED'), ("use_raytrace_refraction", True), ("use_transparent_shadow", True), ("thickness_mode", 'SPHERE')):
        try: setattr(m, a, v)
        except Exception: pass
    return m


def liquido_frenos(nombre="MP_LiquidoFrenos"):
    return aceite(nombre, color=(0.9, 0.72, 0.25), calor=False)


def burbuja(nombre="MP_Burbuja"):
    m = _nuevo(nombre); nt = m.node_tree; out = _salida(nt); b = _bsdf(nt)
    _set(b, "Base Color", (1, 1, 1, 1)); _set(b, "Roughness", 0.0); _set(b, "IOR", 1.05); _set(b, "Transmission Weight", 1.0)
    _set(b, "Specular IOR Level", 1.0); _set(b, "Emission Color", (1, 0.95, 0.85, 1)); _set(b, "Emission Strength", 0.15)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    for a, v in (("surface_render_method", 'DITHERED'), ("use_raytrace_refraction", True)):
        try: setattr(m, a, v)
        except Exception: pass
    return m


def burbujas(col, padre, r_max, z0, z1, n, f0, f1, nombre="MP_Burbuja", semilla=3, mitad_atras=False):
    """n burbujas de aire que suben despacio dentro de un cilindro (radio r_max, de z0 a z1) entre f0 y f1."""
    import random
    rnd = random.Random(semilla); mat = burbuja(); obs = []
    for i in range(n):
        r = rnd.uniform(0.0007, 0.0022)
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=r)
        me = bpy.data.meshes.new(f"{nombre}_{i}"); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        o = bpy.data.objects.new(f"{nombre}_{i}", me); col.objects.link(o); o.parent = padre; me.materials.append(mat)
        a = rnd.uniform(0, math.tau)
        if mitad_atras: a = rnd.uniform(0.15, math.pi - 0.15)
        rr = rnd.uniform(0.25, 0.92) * r_max
        x, y = rr * math.cos(a), rr * math.sin(a)
        vel = rnd.uniform(0.0003, 0.0011)             # metros por fotograma: suben despacio y se quedan arriba
        zi = z0 + rnd.uniform(0, 0.75) * (z1 - z0)
        f = f0
        while f <= f1:
            z = min(z1 - r, zi + (f - f0) * vel)
            o.location = (x + 0.0006 * math.sin(f * 0.3 + i), y + 0.0006 * math.cos(f * 0.27 + i), z); o.keyframe_insert("location", frame=f)
            f += 6
        obs.append(o)
    return obs


# ---------------------------------------------------------------------------------------------- METALES
def cromo(nombre="MP_Cromo", color=(0.93, 0.93, 0.94)):
    """Cromo pulido de vástago: espejo con micro rayas circulares (anisotropía) y leves manchas de rugosidad."""
    m = _nuevo(nombre); nt = m.node_tree; out = _salida(nt); b = _bsdf(nt); ob = _objeto(nt)
    _set(b, "Base Color", (*color, 1)); _set(b, "Metallic", 1.0); _set(b, "Anisotropic", 0.55)
    tg = nt.nodes.new("ShaderNodeTangent"); tg.direction_type = 'RADIAL'; tg.axis = 'Z'; nt.links.new(tg.outputs[0], b.inputs["Tangent"])
    nz = _ruido(nt, ob, 25.0, 6.0, 0.6); nt.links.new(_rango(nt, nz.outputs["Fac"], 0.035, 0.11), b.inputs["Roughness"])
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m


def acero(nombre="MP_Acero", color=(0.6, 0.61, 0.63), rugo=(0.16, 0.32), anillos=True):
    """Acero mecanizado (pistón, tuercas, chapas): anillos de torno finos, rugosidad variable, anisotropía circular."""
    m = _nuevo(nombre); nt = m.node_tree; out = _salida(nt); b = _bsdf(nt); ob = _objeto(nt)
    _set(b, "Base Color", (*color, 1)); _set(b, "Metallic", 1.0); _set(b, "Anisotropic", 0.4)
    tg = nt.nodes.new("ShaderNodeTangent"); tg.direction_type = 'RADIAL'; tg.axis = 'Z'; nt.links.new(tg.outputs[0], b.inputs["Tangent"])
    nz = _ruido(nt, ob, 60.0, 8.0, 0.65)
    alto = nz.outputs["Fac"]
    if anillos:
        sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(ob, sx.inputs[0])
        cx = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(sx.outputs[0], cx.inputs[0]); nt.links.new(sx.outputs[1], cx.inputs[1])
        wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'RINGS'; nt.links.new(cx.outputs[0], wv.inputs["Vector"])
        _set(wv, "Scale", 900.0); _set(wv, "Distortion", 2.0); _set(wv, "Detail", 3.0)
        mx = nt.nodes.new("ShaderNodeMath"); mx.operation = 'MULTIPLY_ADD'; mx.inputs[1].default_value = 0.4
        nt.links.new(wv.outputs["Fac"], mx.inputs[0]); nt.links.new(nz.outputs["Fac"], mx.inputs[2]); alto = mx.outputs[0]
    nt.links.new(_rango(nt, nz.outputs["Fac"], rugo[0], rugo[1]), b.inputs["Roughness"])
    nt.links.new(_bump(nt, alto, 0.08, 0.0004), b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m


def fundicion(nombre="MP_Fundicion", color=(0.32, 0.32, 0.33)):
    """Hierro fundido (discos, pinzas, manguetas): grano grueso, mate, con óxido leve en los poros."""
    m = _nuevo(nombre); nt = m.node_tree; out = _salida(nt); b = _bsdf(nt); ob = _objeto(nt)
    nz = _ruido(nt, ob, 400.0, 4.0, 0.7)
    ox = _ruido(nt, ob, 18.0, 5.0, 0.6)
    cr = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(ox.outputs["Fac"], cr.inputs[0])
    cr.color_ramp.elements[0].position = 0.55; cr.color_ramp.elements[0].color = (*color, 1)
    cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = (0.28, 0.14, 0.06, 1)
    nt.links.new(cr.outputs[0], b.inputs["Base Color"]); _set(b, "Metallic", 0.85)
    nt.links.new(_rango(nt, nz.outputs["Fac"], 0.38, 0.62), b.inputs["Roughness"])
    nt.links.new(_bump(nt, nz.outputs["Fac"], 0.25, 0.0006), b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m


# ---------------------------------------------------------------------------------------------- PINTURAS, GOMA, CORTE
def pintura(nombre="MP_Pintura", color=(0.018, 0.019, 0.022), rugo=0.38, barniz=0.7, piel_naranja=0.03, metal=0.0):
    """Pintura de pieza de coche (cataforesis negra, polvo de muelles...): base con 'piel de naranja' y barniz brillante."""
    m = _nuevo(nombre); nt = m.node_tree; out = _salida(nt); b = _bsdf(nt); ob = _objeto(nt)
    _set(b, "Base Color", (*color, 1)); _set(b, "Metallic", metal)
    nz = _ruido(nt, ob, 220.0, 3.0, 0.5)
    nt.links.new(_rango(nt, nz.outputs["Fac"], rugo - 0.06, rugo + 0.08), b.inputs["Roughness"])
    _set(b, "Coat Weight", barniz); _set(b, "Coat Roughness", 0.06)
    nb = _bump(nt, nz.outputs["Fac"], piel_naranja, 0.001)
    nt.links.new(nb, b.inputs["Coat Normal"]) if "Coat Normal" in b.inputs else None
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m


def pintura_sucia(nombre="MP_PinturaSucia", color=(0.15, 0.115, 0.075)):
    """Pieza vieja: polvo mate con manchas más oscuras."""
    m = _nuevo(nombre); nt = m.node_tree; out = _salida(nt); b = _bsdf(nt); ob = _objeto(nt)
    nz = _ruido(nt, ob, 30.0, 6.0, 0.7)
    cr = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(nz.outputs["Fac"], cr.inputs[0])
    cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = (color[0] * 0.45, color[1] * 0.45, color[2] * 0.45, 1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (*color, 1)
    nt.links.new(cr.outputs[0], b.inputs["Base Color"]); _set(b, "Roughness", 0.82); _set(b, "Metallic", 0.1)
    nt.links.new(_bump(nt, nz.outputs["Fac"], 0.2, 0.0008), b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m


def goma(nombre="MP_Goma", color=(0.012, 0.012, 0.013)):
    """Goma (fuelles, silentblocks, neumáticos): mate con un velo de polvo (sheen) y micro grano."""
    m = _nuevo(nombre); nt = m.node_tree; out = _salida(nt); b = _bsdf(nt); ob = _objeto(nt)
    _set(b, "Base Color", (*color, 1)); _set(b, "Sheen Weight", 0.35); _set(b, "Sheen Roughness", 0.6)
    nz = _ruido(nt, ob, 500.0, 2.0, 0.5)
    nt.links.new(_rango(nt, nz.outputs["Fac"], 0.62, 0.8), b.inputs["Roughness"])
    nt.links.new(_bump(nt, nz.outputs["Fac"], 0.12, 0.0004), b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m


def corte(nombre="MP_Corte"):
    """Cara de corte del despiece: metal recién cortado (brillo satinado y marcas de sierra) con un tinte cálido suave
    para que se distinga del resto sin parecer un plástico naranja."""
    m = _nuevo(nombre); nt = m.node_tree; out = _salida(nt); b = _bsdf(nt); ob = _objeto(nt)
    _set(b, "Base Color", (0.86, 0.6, 0.48, 1)); _set(b, "Metallic", 1.0); _set(b, "Anisotropic", 0.6)
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; nt.links.new(ob, wv.inputs["Vector"])
    _set(wv, "Scale", 400.0); _set(wv, "Distortion", 3.0)
    nt.links.new(_rango(nt, wv.outputs["Fac"], 0.18, 0.32), b.inputs["Roughness"])
    nt.links.new(_bump(nt, wv.outputs["Fac"], 0.05, 0.0003), b.inputs["Normal"])
    _set(b, "Emission Color", (1.0, 0.45, 0.15, 1)); _set(b, "Emission Strength", 0.08)
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m


# ---------------------------------------------------------------------------------------------- CAMBIAR MATERIALES YA PUESTOS
def mejorar(m_viejo, tipo, **kw):
    """Copia el árbol de un material pro en un material ya asignado (así no hay que tocar los objetos)."""
    fab = {"aceite": aceite, "cromo": cromo, "acero": acero, "fundicion": fundicion, "pintura": pintura,
           "pintura_sucia": pintura_sucia, "goma": goma, "corte": corte}[tipo]
    nuevo = fab("MP_tmp_" + m_viejo.name, **kw)
    for o in bpy.data.objects:
        if o.type in ('MESH', 'CURVE'):
            for s in o.material_slots:
                if s.material == m_viejo: s.material = nuevo
    return nuevo


# ---------------------------------------------------------------------------------------------- RENDER
def render_pro(sc, pct=100, muestras=64):
    """1080x1920 a resolución completa, raytracing (reflejos y refracción de verdad), sombras finas, AgX."""
    sc.render.resolution_percentage = pct
    e = sc.eevee
    for a, v in (("taa_render_samples", muestras), ("use_raytracing", True), ("ray_tracing_method", 'SCREEN'),
                 ("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8), ("shadow_resolution_scale", 1.0),
                 ("fast_gi_method", 'GLOBAL_ILLUMINATION'), ("use_fast_gi", True), ("volumetric_tile_size", '4')):
        try: setattr(e, a, v)
        except Exception: pass
    try:
        o = e.ray_tracing_options; o.resolution_scale = '1'; o.use_denoise = True; o.trace_max_roughness = 0.6
    except Exception: pass
    try: sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    sc.render.film_transparent = False
    return sc
