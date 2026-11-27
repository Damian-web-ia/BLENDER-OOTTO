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

## 2026-11-26 · Reel diario «¿Te tiembla el volante a partir de 80?» (equilibrado)
- **ChatGPT corta las respuestas largas** porque gasta tokens pensando: la lista de preguntas llegó cortada (34 de 40) y la skill se quedó en la sección 8. Pedir más `max_tokens` (12.000-14.000 para prompt + skill) o pedir la skill en otra llamada; Claude completó lo que faltaba.
- **Bordes negros en el vídeo sin voz:** `encode_bg.py` no escalaba los fotogramas renderizados al 67 %. Arreglado (escala la tira al tamaño final); hoy se recortó en el montaje con `crop=724:1286:178:317`.
- **Pasar archivos del PC a Ootto sin carpeta conectada:** Blender sube el archivo con un PUT a la URL firmada de `request_user_media_upload` y luego `confirm_user_media`. Para GitHub hace falta la carpeta conectada.
- **Datos:** el gancho de síntoma (volante) es el que mejor funciona (1.621 vistas, 10,8x la mediana); el reel 3D con más tiempo de visionado (23 s de media) fue el de humor con Clod.


## 2026-11-27 · Reel diario «Despiece del embrague»
- **ChatGPT se quedó sin tokens pensando** en la llamada del prompt (7.000: salieron 171 caracteres). Con 16.000 y "piensa poco" escribió todo (5.224). Para el prompt + skill: pedir 14.000-16.000 desde el principio y la skill como secciones nuevas, no entera.
- **Estudio oscuro de verdad:** con una pieza grande (28 cm) la cámara se aleja y se veía el coche y el taller detrás. Se ocultan con claves (`hide_render`) el taller, el coche y Clod mientras la pieza está en el estudio y en el inserto; las luces del taller siguen bajas hasta A3.
- **Ojo al ocultar con claves:** poner interpolación constante solo en las curvas `hide_*`; si se cambia todo el `action` del objeto, la animación del esqueleto de Clod se queda a saltos.
- **Datos (IG 28 días):** el gancho práctico gana ("¿Solo cambias dos neumáticos?" 2.426 vistas y 18,7 s de media); el despiece del neumático 1.486 (6,5x la mediana); el de frenos 165 en IG pero 1.162 en YouTube Shorts.
