# Construye una escena en segundo plano y la guarda: blender -b <base.blend> --python construir_bg.py -- <escena.py> <salida.blend>
import bpy, sys, traceback
argv = sys.argv[sys.argv.index("--") + 1:]
escena, salida = argv[0], argv[1]
g = {"__name__": "__main__"}
try:
    exec(open(escena, encoding="utf-8").read(), g)
    bpy.ops.wm.save_as_mainfile(filepath=salida)
    print("CONSTRUIDO", salida, g.get("result"))
except Exception:
    traceback.print_exc(); print("ERROR_CONSTRUIR")
