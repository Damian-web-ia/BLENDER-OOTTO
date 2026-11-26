# Despiece 3D de los frenos

| | |
|---|---|
| **Qué es** | Vídeo vertical 9:16, 30 fps, 26,7 s. La rueda delantera del coche estalla, el freno sale flotando y se explica: líquido → pistón → pinza → pastillas → disco → calor → canales de ventilación. Consejo: si chirría o vibra el volante, revisar pastillas y discos (pastilla nueva frente a gastada). |
| **Voz** | Alex = Diego (España), por ID. Clod no habla: gestos de fondo (se agacha al pisar, el frenazo lo lanza, se tapa los oídos con el chirrido, tiembla con la vibración, pulgar arriba al final). |
| **Escena** | `despiece_frenos.py` (se ejecuta sobre `alex_v2_rig.blend` abierto; reutiliza el taller, el coche y los personajes del despiece del neumático) + `biblioteca/freno_real.py` (disco ventilado con 36 álabes, pinza flotante, pastillas, soporte, buje, latiguillo). |
| **Tiempos de voz** | `voces_frenos.json` (4 líneas: 0,25 · 4,55 · 17,45 · 23,15 s). |
| **Render** | `render_bg.py -- 67 48 render_v1` en el PC (unos 4,3 s por fotograma; 800 fotogramas). Fotogramas de prueba en `pruebas_1` a `pruebas_3`. |
| **Montaje** | `montaje_frenos.py`: gancho "¿QUÉ PASA AL FRENAR?", subtítulos palabra a palabra, rótulos de cada pieza con línea a su sitio (`anclas_frenos.json`), avisos "¿CHIRRÍA? / ¿VIBRA EL VOLANTE? / ¡NO LO DEJES!" y NUEVA / GASTADA. |
| **Sonido** | `mezcla_frenos.ogg`: voz, música electrónica minimal con ducking, efectos (estallido, chirrido sintetizado, vibración, aire por los canales, campanitas en cada rótulo), -14 LUFS. |
| **Vídeo final** | `estudio-3d/videos/2026-11-26_despiece_frenos_voz_diego.mp4` (26,7 s, -14,3 LUFS) y portada `2026-11-26_despiece_frenos_portada.jpg`. Copias en el PC: `CLAUDE VIDEOS` y `evolucion_videos`. |
| **Publicación** | Domingo 06-12-2026 a las 20:30 (Europe/Madrid). Instagram + YouTube por Ootto: reel 62696 (`media_c944ad73de`, portada `media_4156dda749`). TikTok por vidIQ: post `659aaba0-1e0c-4564-aa25-c677a31f9356`, programado. |

## Pie de publicación

¿Qué pasa dentro de la rueda cuando pisas el freno? 🛑 El líquido empuja el pistón, la pinza aprieta las pastillas contra el disco y ese roce convierte el movimiento en calor. Por eso muchos discos llevan canales por dentro: para enfriarse. Si al frenar chirría o te vibra el volante, que te revisen pastillas y discos.

Título de YouTube: "¿Qué pasa al frenar? Despiece de los frenos en 3D".
