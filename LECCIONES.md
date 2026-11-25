# Lecciones aprendidas

Lo que ha funcionado y lo que ha fallado, día a día. La skill maestra se mejora con esto.

## 2026-11-25 · Vídeo del Jesko (Blender)
- Las cámaras no deben atravesar piezas: comprobar cada plano con un fotograma suelto antes del render completo.
- Los textos 3D siempre dentro del cuadro 1080x1920.
- Las rejillas con texto o logo necesitan UV (`bm.loops.layers.uv.new("UVMap")` y `calc_uvs=True`).
- Los paneles de luz del estudio, con `visible_camera=False` para que no tapen nada.
- Profundidad de campo (DOF) apagada en primeros planos.
- El render largo se lanza en segundo plano (`subprocess.Popen`, `creationflags=0x200`) para que Blender no se quede bloqueado.
- En Ootto, igualar el volumen de cada voz con `volumedetect` (con `loudnorm` las frases cortas quedaban bajas).
