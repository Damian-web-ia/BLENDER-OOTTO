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

## 2026-11-25 · Reel diario «¿Ruedas nuevas delante o detrás?»
- Detalle completo en `estudio-3d/LECCIONES.md`. Resumen: bajar la luz (clave 650 W); los textos van colgados de la cámara a 0,4 m y con placa oscura; los subtítulos con caja; en los insertos, cámara alta para que nada pise los títulos; comprobar la portada con `world_to_camera_view`.
- Al acercarse, la cámara del último plano metió la cabeza de Alex bajo el título: en planos con *push-in*, el título va un 10 % más arriba o la cámara no se acerca.
- Desde hoy, cada reel carga `estudio-3d/biblioteca/biblioteca_ekoruedas.py` en vez de reconstruirlo todo.
