# EKORUEDAS_ESTUDIO_3D

Estudio 3D de los reels diarios. Blender hace la imagen; Ootto pone el sonido y los subtítulos; ChatGPT da la idea y el guion. Esta misma carpeta está en GitHub (`Damian-web-ia/BLENDER-OOTTO`, carpeta `estudio-3d/`).

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
