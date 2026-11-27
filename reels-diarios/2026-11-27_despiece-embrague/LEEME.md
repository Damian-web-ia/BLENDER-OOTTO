# Reel del 27-11-2026 · Despiece 3D del embrague

| Qué | Detalle |
|---|---|
| **Vídeo** | Reel vertical 1080x1920, 30 fps, unos 32 s. Despiece 3D del embrague (volante motor, disco, maza con diafragma y collarín) con Alex (voz Diego) y Clod (sin voz). |
| **Fecha de producción** | Viernes 27-11-2026 (tarea diaria de las 19:30). |
| **Se publica** | CAMBIO 27-11 21:25: Damián pidió rehacerlo en 4K60 Cycles y esperar a esa versión; se quitó la programación del sábado. Lo que estaba programado: sábado 28-11-2026 a las 19:00 (Madrid), público. Instagram + YouTube Shorts por Ootto (reel 63845, job `job_1e137ee506a4`, portada `media_41fda10781`, título "¿Tu embrague patina? Despiece del embrague en 3D"). TikTok por vidIQ (post `f64df7fa-f1a4-4ea8-be6d-476bc04020fd`, programado). |
| **Reel en Ootto** | https://mcp.ootto.ai/w/reel/acc_50544226d762-1e137ee506a4 |
| **Render** | Blender 5.3 EEVEE al 67 %, 48 muestras, 977 fotogramas: 20,5 min (unos 1,3 s por fotograma, con la cola 4K de Cycles a la vez) + 15,6 min para rehacer 432 fotogramas (arreglo de la esfera negra). Carpeta del PC: `Escritorio\\CLAUDE VIDEOS\\2026-11-27_DESPIECE-EMBRAGUE`. |
| **Mejora de hoy (Alex v3)** | Cara seria: la malla sonreía siempre; nueva expresión `seria` y neutra/duda/enfado/concentrado sin sonrisa. Antes/después: [`estudio-3d/referencias/evolucion/2026-11-27_alex-cara-seria.png`](../../estudio-3d/referencias/evolucion/2026-11-27_alex-cara-seria.png). |
| **Sonido** | Voz de Alex (Diego, 5 frases), música electronic-minimal con ducking, 43 efectos sintetizados; -14,2 LUFS, pico -0,5 dBFS. |
| **Idea** | Pieza propuesta por Claude a partir de las tendencias de vidIQ (un disco de embrague girando: 772.000 vistas en TikTok); ChatGPT la aceptó en la entrevista y escribió el prompt. Descartadas: correa de distribución (necesita el motor entero) y radiador/termostato (poco visual por dentro). |
| **Gancho** | "¿SUBE DE VUELTAS Y NO CORRE?" |
| **Chiste de Clod** | Está en el capó dando golpecitos con el pie como si pisara un pedal; Alex: "Clod, quita el pie de ahí". Al final, el consejo es "no lleves el pie apoyado en el pedal. ¿Verdad, Clod?" y lo pillan otra vez. |
| **Datos comprobados** | RACE ("¿Cómo saber si el embrague patina?", "Problemas con el embrague"), Mapfre (embrague gastado), Autofácil (componentes). Sin cifras de kilómetros (las fuentes no coinciden). |

## Archivos
| Archivo | Qué es |
|---|---|
| `prompt_2026-11-27.md` | Prompt de producción que escribió ChatGPT tras entrevistar a Claude, con la revisión de Claude. |
| `entrevista_2026-11-27.md` | Las preguntas de ChatGPT y las respuestas de Claude. |
| `data/voces.json` | Las 5 frases de Alex con el tiempo de cada palabra. |
| `scripts-blender/` | Copia del código de Blender del vídeo (el original está en `estudio-3d/videos_3d/despiece_embrague/`). |
| `portada/` | Portada vertical y cuadrada ("¿TU EMBRAGUE PATINA?"). |
| `video-sin-voz_2026-11-27.mp4` | Lo que sale de Blender. |
| `video-montado-sin-sonido_2026-11-27.mp4` | Con rótulos, subtítulos y cierre (el sonido se pone en Ootto). |
