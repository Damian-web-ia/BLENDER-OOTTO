# characters.py - Claude (robot 30 cm) y Alex (mecánico) con rig FK por jerarquía de controles

# ================================================================= CLAUDE
def build_claude():
    root = empty("CLAUDE_Raiz", "CLAUDE"); root.scale = (0.15, 0.15, 0.15)  # ~32 cm de alto
    body = prim("sphere", "CLAUDE_Cuerpo", "CLAUDE", M["orange"], root, loc=(0, 0, 0.78), scale=(1, 0.85, 1.1), r=0.42, u=48, v=24)
    for i in range(6):
        b = prim("cube", f"CLAUDE_Simbolo{i}", "CLAUDE", M["led"], body, loc=(0, -0.425, 0.08), rot=(0, math.radians(i * 30), 0), scale=(0.045, 0.02, 0.32), smooth=False)
    hp = empty("CLAUDE_Cabeza", "CLAUDE", root, (0, 0, 1.25))
    head = prim("cube", "CLAUDE_CabezaMalla", "CLAUDE", M["orange"], hp, loc=(0, 0, 0.42), scale=(1.15, 0.85, 0.85), bevel=0.18, bseg=6)
    scr = prim("cube", "CLAUDE_Pantalla", "CLAUDE", M["screen"], hp, loc=(0, -0.37, 0.42), scale=(0.92, 0.12, 0.62), bevel=0.1, bseg=6)
    eyes = []
    for s in (-1, 1):
        e = prim("cyl", f"CLAUDE_Ojo{s}", "CLAUDE", M["led"], hp, loc=(s * 0.21, -0.44, 0.5), rot=(math.radians(90), 0, 0), scale=(1.15, 1, 1), r=0.11, d=0.02, seg=32)
        eyes.append(e)
    mouth = prim("torus", "CLAUDE_Boca", "CLAUDE", M["led"], hp, loc=(0, -0.44, 0.27), rot=(math.radians(90), 0, 0), scale=(1, 0.45, 1), R=0.12, rr=0.02)
    for s in (-1, 1):
        prim("cyl", f"CLAUDE_Auricular{s}", "CLAUDE", M["orange"], hp, loc=(s * 0.62, 0, 0.42), rot=(0, math.radians(90), 0), r=0.2, d=0.14)
        prim("torus", f"CLAUDE_AroAuricular{s}", "CLAUDE", M["dark"], hp, loc=(s * 0.69, 0, 0.42), rot=(0, math.radians(90), 0), R=0.15, rr=0.035)
    arms = {}
    for s in (-1, 1):
        sh = empty(f"CLAUDE_Hombro{s}", "CLAUDE", root, (s * 0.5, 0, 1.02))
        prim("cyl", f"CLAUDE_Brazo{s}", "CLAUDE", M["orange"], sh, loc=(0, 0, -0.22), r=0.09, d=0.45)
        prim("sphere", f"CLAUDE_Mano{s}", "CLAUDE", M["dark"], sh, loc=(0, 0, -0.48), r=0.11)
        arms[s] = sh
    legs = {}
    for s in (-1, 1):
        lg = empty(f"CLAUDE_Cadera{s}", "CLAUDE", root, (s * 0.2, 0, 0.45))
        prim("cyl", f"CLAUDE_Pierna{s}", "CLAUDE", M["dark"], lg, loc=(0, 0, -0.15), r=0.09, d=0.3)
        prim("cube", f"CLAUDE_Pie{s}", "CLAUDE", M["orange"], lg, loc=(0, -0.05, -0.37), scale=(0.22, 0.32, 0.14), bevel=0.05)
        legs[s] = lg
    return {"root": root, "head": hp, "eyes": eyes, "mouth": mouth, "arms": arms, "legs": legs}

# ================================================================= ALEX
def build_alex():
    root = empty("ALEX_Raiz", "ALEX")
    pelvis = empty("ALEX_Pelvis", "ALEX", root, (0, 0, 0.95))
    for s in (-1, 1):
        hip = empty(f"ALEX_Cadera{s}", "ALEX", pelvis, (s * 0.11, 0, 0))
        prim("cyl", f"ALEX_Pierna{s}", "ALEX", M["uniform"], hip, loc=(0, 0, -0.45), r=0.085, d=0.88)
        prim("cube", f"ALEX_Bota{s}", "ALEX", M["boot"], hip, loc=(0, -0.05, -0.9), scale=(0.13, 0.28, 0.1), bevel=0.03)
    spine = empty("ALEX_Columna", "ALEX", pelvis, (0, 0, 0.02))
    torso = prim("cube", "ALEX_Torso", "ALEX", M["uniform"], spine, loc=(0, 0, 0.32), scale=(0.42, 0.24, 0.6), bevel=0.11, bseg=6)
    prim("cube", "ALEX_Cinturon", "ALEX", M["boot"], spine, loc=(0, 0, 0.04), scale=(0.425, 0.245, 0.06), bevel=0.05, bseg=3)
    prim("torus", "ALEX_Cuello_Ribete", "ALEX", M["piping"], spine, loc=(0, 0, 0.62), scale=(1.0, 0.85, 1.0), R=0.07, rr=0.016)
    for s in (-1, 1):
        prim("sphere", f"ALEX_Deltoide{s}", "ALEX", M["uniform"], spine, loc=(s * 0.205, 0, 0.55), r=0.07)
    # símbolo oficial en el pecho izquierdo (izquierda del personaje = +X mirando a -Y)
    lp = bpy.data.meshes.new("ALEX_Logo"); bm = bmesh.new(); bm.loops.layers.uv.new("UVMap"); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5, calc_uvs=True); bm.to_mesh(lp); bm.free()
    lg = new_obj("ALEX_LogoPecho", lp, "ALEX", M["logo"], spine, (0.1, -0.127, 0.46)); lg.rotation_euler = (math.radians(90), 0, 0); lg.scale = (0.1 * 1.28, 0.1, 1)
    neck = empty("ALEX_Cuello", "ALEX", spine, (0, 0, 0.585))
    prim("cyl", "ALEX_CuelloMalla", "ALEX", M["skin"], neck, loc=(0, 0, 0.05), r=0.058, d=0.12)
    head = empty("ALEX_Cabeza", "ALEX", neck, (0, 0, 0.1))
    prim("sphere", "ALEX_Craneo", "ALEX", M["skin"], head, loc=(0, 0, 0.13), scale=(0.92, 1.0, 1.15), r=0.115)
    prim("sphere", "ALEX_Pelo", "ALEX", M["hair"], head, loc=(0, 0.018, 0.2), scale=(0.97, 1.02, 0.72), r=0.122)
    prim("sphere", "ALEX_Barba", "ALEX", M["beard"], head, loc=(0, -0.012, 0.07), scale=(0.93, 0.96, 0.62), r=0.115)
    prim("sphere", "ALEX_Nariz", "ALEX", M["skin"], head, loc=(0, -0.118, 0.13), scale=(0.8, 1, 1.2), r=0.022)
    mouth = prim("sphere", "ALEX_Boca", "ALEX", M["mouth"], head, loc=(0, -0.113, 0.075), scale=(1.6, 0.5, 0.25), r=0.02)
    eyes = []
    for s in (-1, 1):
        e = empty(f"ALEX_Ojo{s}", "ALEX", head, (s * 0.042, -0.095, 0.16))
        prim("sphere", f"ALEX_OjoBlanco{s}", "ALEX", M["eyeW"], e, r=0.019)
        prim("sphere", f"ALEX_Iris{s}", "ALEX", M["iris"], e, loc=(0, -0.014, 0), r=0.0105)
        prim("cube", f"ALEX_Ceja{s}", "ALEX", M["hair"], head, loc=(s * 0.043, -0.108, 0.192), rot=(0, s * math.radians(-8), 0), scale=(0.042, 0.012, 0.01), bevel=0.003)
        prim("sphere", f"ALEX_Oreja{s}", "ALEX", M["skin"], head, loc=(s * 0.108, 0.0, 0.14), scale=(0.35, 0.6, 1), r=0.03)
        eyes.append(e)
    arms = {}
    for s in (-1, 1):
        sh = empty(f"ALEX_Hombro{s}", "ALEX", spine, (s * 0.25, 0, 0.55))
        prim("cyl", f"ALEX_BrazoSup{s}", "ALEX", M["uniform"], sh, loc=(0, 0, -0.15), r=0.058, d=0.32)
        el = empty(f"ALEX_Codo{s}", "ALEX", sh, (0, 0, -0.3))
        prim("cyl", f"ALEX_Antebrazo{s}", "ALEX", M["uniform"], el, loc=(0, 0, -0.14), r=0.05, d=0.3)
        hd = prim("sphere", f"ALEX_Mano{s}", "ALEX", M["skin"], el, loc=(0, 0, -0.32), scale=(0.8, 0.55, 1.1), r=0.05)
        sh.rotation_euler = (0, s * math.radians(8), 0)
        arms[s] = (sh, el)
    return {"root": root, "spine": spine, "head": head, "neck": neck, "eyes": eyes, "mouth": mouth, "arms": arms}

CL = build_claude()
AL = build_alex()
