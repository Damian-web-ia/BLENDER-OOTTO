# EKORUEDAS_ESTUDIO_3D

Estudio 3D de EKORUEDAS: Blender hace la imagen (por código Python, en el PC del taller) y Ootto pone la voz y el sonido. Esta misma carpeta está en el PC (`Desktop\EKORUEDAS_ESTUDIO_3D`) y en GitHub (`estudio-3d/`).

**Limpieza del 27-11-2026:** Damián pidió borrar todos los vídeos anteriores y quedarse solo con los modelos. Los vídeos, escenas y renders viejos están en el historial de GitHub (commit `454db14`) y, en el PC, en `_papelera\videos_2026-11-27`.

## Qué queda

| Carpeta | Qué hay |
|---|---|
| `biblioteca/` | **Modelos de piezas** con medidas reales, cada uno en su archivo: `motor_4t_real.py`, `turbo_real.py` (+ `prueba_turbo.py`), `neumatico_real.py`, `freno_real.py`, `amortiguador_real.py`, `embrague_real.py`, `bateria_real.py`, `filtro_aceite_real.py`, `bujia_real.py`. Materiales: `materiales_pro.py`. Escenarios: `biblioteca_ekoruedas.py`, `taller_v2.py`. |
| `biblioteca/personajes/` | **Clod v3** (`clod_v3.py`, `clod_anim.py`, guía `LEEME_CLOD_V3.md`; en el PC `clod\clod_v3.blend`), **Maite** y los demás personajes de Tripo (`tripo/`: Maite, Lucía, Ane, Iker, Patxi), y Rulo (`rulo_canal_nuevo/`, reservado para el canal nuevo). |
| `plantillas/` | Herramientas de montaje: `montaje_despiece.py` (rótulos, subtítulos, logo final), `portada_despiece.py`, `despiece_base.py`, `plantilla_reel.py`. |
| `scripts/` | `render_cycles_bg.py` (render 4K 60 fps con Cycles), `encode_bg.py` (fotogramas → mp4), `prueba_frames.py` (fotogramas de prueba rápidos), `render_bg.py`, `construir_bg.py`. |
| `marca/` | Logo de EKORUEDAS. |
| `referencias/`, `disenos/` | Imágenes de estilo y los 8 diseños de vídeo. |
| `PLAN_DE_ESTILO.md`, `LECCIONES.md` | Meta visual y lo aprendido (para no repetir errores). |

## Personajes
- **Maite**: la cara de EKORUEDAS desde el 27-11-2026. Voz Renata (Ootto, español de España).
- **Clod v3**: robot naranja de 32 cm, ayudante. No habla.
- **Alex** y **Clod v2**: retirados (en la `_papelera` del PC y en el historial de GitHub).

## Estándar
Todo lo mecánico sigue la skill `skills/ekoruedas-automotive-cgi-4k/` (4K vertical 2160x3840, 60 fps, Cycles, despiece de cine).
