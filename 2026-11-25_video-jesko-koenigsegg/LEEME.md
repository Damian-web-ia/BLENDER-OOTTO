# Vídeo "La caja de cambios imposible" (Koenigsegg Jesko) · 25-11-2026

Vídeo 3D vertical de 60 s (1080x1920, 1800 fotogramas) hecho por completo en Blender por código: Alex y Clod explican la caja de cambios LST del Koenigsegg Jesko (9 marchas, 7 embragues). El sonido (voces, música y efectos) se montó en Ootto.

## Archivos

| Archivo | Qué es |
|---|---|
| `video-sin-voz_v2-FINAL_2026-11-25.mp4` | **Versión buena**, sin sonido. Es la que se usó en Ootto. |
| `video-sin-voz_v1_2026-11-25.mp4` | Primera versión (tenía paneles de luz tapando textos). Se guarda como historial. |
| `guion/voces-y-tiempos_2026-11-25.json` | Texto de cada línea, voz y tiempos de cada palabra. |
| `guion/subtitulos_2026-11-25.srt` | Subtítulos. |
| `guion/licencias-de-recursos_2026-11-25.md` | De dónde sale cada recurso y su licencia (todo modelado por código). |
| `scripts-blender/build.py` | Monta la escena completa (llama a los demás). |
| `scripts-blender/models.py` | Modela el coche y la caja de cambios. |
| `scripts-blender/characters.py` | Construye a Alex y a Clod. **Se reutiliza en los reels diarios.** |
| `scripts-blender/animation.py` | Cámaras, planos y animación. |
| `scripts-blender/render_bg.py` | Renderiza en segundo plano a PNG. |
| `scripts-blender/encode_bg.py` | Junta los PNG en el MP4. |

## Estado

- Terminado con sonido en Ootto (reel `job_8969e44acb6f`), **sin publicar** todavía.
- Render 4K: parado en el fotograma 170 de 1800 (en el PC, carpeta `JESKO/render/frames_4k`).
