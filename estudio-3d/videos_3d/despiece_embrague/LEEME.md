# Despiece 3D del embrague (27-11-2026, se publica el 28-11 a las 19:00)

Reel vertical 1080x1920, 30 fps, 32,6 s (977 fotogramas). Hecho en Blender (EEVEE) en el PC de Damián, con Alex (voz Diego) y Clod (sin voz).
Plan A del canal: despiece en 3D de una pieza del coche. Carpeta del día: `reels-diarios/2026-11-27_despiece-embrague/`.

| Qué | Dónde / detalle |
|---|---|
| **Idea** | De Claude a partir de vidIQ (un disco de embrague girando: 772.000 vistas en TikTok, 44,5x la mediana de esa cuenta); ChatGPT (gpt-6-luna) la aceptó en la entrevista y escribió el prompt. Descartadas: correa de distribución y radiador/termostato. |
| **Guion** | 5 frases de Alex: gancho con Clod ("quita el pie de ahí"), piezas, qué pasa al pisar el pedal, síntomas y consejo ("no lleves el pie apoyado en el pedal. ¿Verdad, Clod?"). `voces_embrague.json`. |
| **Datos comprobados** | RACE ("¿Cómo saber si el embrague patina?", "Problemas con el embrague"), Mapfre (embrague gastado), Autofácil (componentes). Sin cifras de kilómetros: las fuentes no coinciden (Mapfre 100.000-150.000 km de media; RACE hasta 400.000 km bien usado). |
| **Modelo** | `estudio-3d/biblioteca/embrague_real.py`: volante motor con corona de 120 dientes, disco con 2 forros ranurados, chapa, 6 muelles de torsión y cubo estriado, maza (plato de presión de fundición con cara pulida, diafragma de 18 dedos con forma "pisado", carcasa con 6 tornillos) y collarín. Disco nuevo / gastado (forro más fino, oscuro y cristalizado). |
| **Escena** | `despiece_embrague.py` sobre la plantilla común `plantillas/despiece_base.py` (se construye en segundo plano sobre `alex_v2_rig.blend` con `scripts/construir_bg.py`). Clod da golpecitos con el pie en el capó; rayos X; el embrague sale al estudio; se separa en capas; se junta y gira; plano sin carcasa: el collarín empuja el diafragma, el plato se separa y el disco se para mientras el volante sigue girando; inserto nuevo / gastado; Alex con los síntomas; Clod pillado otra vez con el pie. |
| **Novedades** | Estudio oscuro de verdad (taller, coche y Clod ocultos con claves mientras la pieza está en el estudio y en el inserto); explosión axial en lugar de corte; giro con claves lineales (el disco frena solo, el volante sigue); Alex v3 con cara seria. |
| **Montaje** | `montaje_embrague.json` con `plantillas/montaje_despiece.py` (ahora con palabras clave en naranja #FF8400). |
| **Sonido** | `mezcla_embrague.py` (en el espacio de Ootto): voz, música electronic-minimal a 0,18 con ducking, 43 efectos sintetizados (golpecitos, pitido, rayos X, golpe, clacs, zumbido del giro, clic, aire, roce, siseo, boing), -14,1 LUFS, pico -0,8 dBFS. |

## Versión 4K60 Cycles (pedida por Damián el 27-11 a las 21:15)
- `scripts/cola_4k_embrague.py` (en el PC): mismo .blend, Cycles OptiX, 2160x3840, 60 fps, 64 muestras + OIDN, reintenta si se cae y al final codifica `despiece_embrague_4k60.mp4`. Empezó a las 21:19.
- Ritmo medido: unos 60 s por fotograma compartiendo la gráfica con el render del motor de 4 tiempos. Son 1.954 fotogramas: unas 30-33 horas (domingo por la mañana-tarde). No llega a las 19:00 del sábado.
- Damián (27-11, 21:25): "Esperar al 4K". Se quitó la programación de la versión EEVEE del sábado 28-11 19:00: Ootto ya no tiene nada en cola (Instagram y YouTube) y el post de TikTok de vidIQ (`f64df7fa-…`) quedó como borrador sin publicar. La versión EEVEE se queda guardada (reel `job_1e137ee506a4` en Ootto).
- Cuando termine el 4K: montaje con `plantillas/montaje_despiece.py` (dibuja a 2160x3840 y compone a 60 fps) + la misma mezcla de sonido, entrega en Ootto y programación en Instagram, YouTube y TikTok.
