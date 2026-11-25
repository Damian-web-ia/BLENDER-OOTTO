# Ruedas nuevas: ¿delante o detrás? · reel 3D del 25-11-2026

| | |
|---|---|
| **Qué es** | Reel vertical 3D (Blender) con Alex y Clod: si solo cambias dos neumáticos, los nuevos van en el eje trasero, da igual la tracción. 33,5 s. |
| **Hecho el** | 25-11-2026 (tarea diaria de las 19:30, terminada a mano tras el corte por límite de uso) |
| **Idea** | Calendario de marca de Ootto para el 26-11 y tendencia de vidIQ (explicadores 3D de neumáticos). Tema elegido por Claude; guion final de ChatGPT. |
| **Dato comprobado** | [RACE](https://www.race.es/donde-poner-neumaticos-nuevos) y expertos de Michelin ([Motor16](https://www.motor16.com/noticias/expertos-michelin-donde-poner-neumaticos/)) |
| **Imagen** | Blender 5.3 EEVEE, 1080×1920, 1005 fotogramas, 32 muestras (~0,8 s por fotograma) |
| **Sonido** | Voces de Ootto (Carlos = Alex, Diego = Clod), música funk-groove con ducking, 4 efectos (ding, pop, frenazo, risa corta), -14 LUFS, subtítulos con palabras clave en #FF8400 |
| **Ootto** | job `job_50c4923d1f22` · [ver](https://mcp.ootto.ai/w/reel/acc_50544226d762-50c4923d1f22) |
| **Publicación** | Instagram y YouTube Shorts: 26-11-2026 a las **19:30** (Ootto lo movió de 19:00 porque a esa hora sale el vídeo de invierno) · TikTok (vidIQ): 26-11-2026 a las **20:00** (sugerencia de ritmo de vidIQ) · Público |

## Archivos
| Archivo | Qué es |
|---|---|
| `prompt_2026-11-25.md` | Prompt de producción que escribió ChatGPT tras entrevistar a Claude |
| `scripts-blender/build_ruedas.py` | Escena completa (taller, coche, inserto de carretera, personajes, cámaras, textos, acción) |
| `scripts-blender/portada_bg.py` | Pose y cámara de la portada |
| `scripts-blender/render_bg.py`, `encode_bg.py` | Render en segundo plano y paso a mp4 |
| `data/voces.json` | Tiempos de cada palabra de las 8 frases |
| `video-sin-voz_2026-11-25.mp4` | Salida de Blender sin sonido (v2, sin textos solapados) |
| `portada/` | Portada vertical 1080×1920 y recorte cuadrado 1080×1080 |

## Pendiente de mejorar
En los últimos 2 s la cabeza de Alex roza la línea «CAMBIA LAS CUATRO» (la cámara se acerca). Va apuntado en `estudio-3d/LECCIONES.md`.
