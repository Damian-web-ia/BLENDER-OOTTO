# EKORUEDAS_ESTUDIO_3D

Estudio 3D de los reels diarios. Blender hace la imagen; Ootto pone el sonido y los subtítulos; ChatGPT da la idea y el guion. Esta misma carpeta está en GitHub (`Damian-web-ia/BLENDER-OOTTO`, carpeta `estudio-3d/`).

## Créditos de Ootto (desde el 26-11-2026): presupuesto diario
- Plan Self-serve de Ootto: 600 créditos al mes; se renueva el día 24 de cada mes.
- Damián dijo el 24-11 que le quedaban unos 200. Hasta el 24-12 hay 28 días: **como mucho unos 7 créditos al día**, dejando un 10 % de reserva.
- La animación 3D se hace en Blender, en su PC, y no gasta créditos. Ootto se usa solo para las voces (Alex = "Carlos", Clod = "Diego"), la música y los efectos del montaje.
- No usar `image_generate` ni `video_generate` de Ootto para los vídeos (regla de Jesko). Si algún día hace falta un clip de IA, pedir permiso y apuntar el gasto.
- Cada vídeo diario: voces (2-6 tomas) + montaje. Si un día no se gasta, el saldo pasa a los siguientes; nunca gastar más de 15 en un día sin preguntar.

## Formato que más gusta a Damián (26-11-2026): el DESPIECE 3D
- Se ve el coche por fuera, la cámara entra (rayos X: la carrocería se vuelve azul y transparente), se ve la pieza, se explica, **se rompe en miles de trozos** y se explica cada capa con rótulos. Alex explica, Clod pone el humor.
- Primer ejemplo completo: `videos_3d/despiece_neumatico/` (script de Blender, anclas de rótulos, montaje con subtítulos y mezcla de audio).
- Encaja con lo viral ahora (revelación/transformación en 3D en los primeros segundos, pregunta de gancho, rótulos grandes, efectos de sonido). Próximas piezas: pastillas y disco de freno, amortiguador, embrague, batería, filtro de aceite.

## Personajes v2 (desde el 26-11-2026): usarlos en todos los reels

Los reels nuevos usan **Alex v2** y **Clod v2**, no los de bloques de `biblioteca_ekoruedas.py` (que sigue sirviendo para el coche, las ruedas, el taller y la carretera).

- **Alex v2:** `biblioteca/personajes/alex/alex_v2_rig.blend` (en el PC). Se mete en la escena con `alex_cargar.py` y se anima con `alex_anim.py` (IK, manos, cara con expresiones, habla, músculos). Guía: `biblioteca/personajes/LEEME_ALEX_V2.md`.
- **Clod v2:** `biblioteca/personajes/clod/clod_v2.blend` (o se construye con `clod_v2.py`), animado con `clod_anim.py` (pantalla LED con caras, saludo, pulgar arriba, rebote, salto, habla). Guía: `biblioteca/personajes/LEEME_CLOD_V2.md`.
- **Ejemplo completo con los dos y diálogo:** `biblioteca/personajes/escena_alex_clod.py` (cómo anexar a Clod, voces de cada uno, 5 planos con cortes y `comprobar_encuadre()` antes de renderizar).
- Render: EEVEE 1080×1920 al 67 % con 48 muestras ≈ 1 s por fotograma en este PC.

| Carpeta | Qué hay |
|---|---|
| `biblioteca/` | `biblioteca_ekoruedas.py` (escenarios y personajes v1) y `biblioteca_ekoruedas_v1.blend`; `personajes/` con Alex v2 y Clod v2 |
| `plantillas/` | `plantilla_reel.py`: esqueleto del script diario (carga la biblioteca y escribe solo cámaras, textos y acción) |
| `scripts/` | `render_bg.py` (render en segundo plano) y `encode_bg.py` (fotogramas → mp4) |
| `referencias/` | Imágenes del estilo al que queremos llegar |
| `evolucion_videos/` (solo PC) y `videos/` (GitHub) | Demos de cada mejora de los personajes, con fecha |
| `PLAN_DE_ESTILO.md` | Meta visual, regla de gasto y fases de mejora |
| `LECCIONES.md` | Errores de cada reel y cómo se arreglaron (para no repetirlos) |

Cada reel tiene su propia carpeta en el escritorio, `CLAUDE VIDEOS\AAAA-MM-DD_TITULO`, y en GitHub, `reels-diarios/`.
