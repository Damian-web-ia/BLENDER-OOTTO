# ¿Te tiembla el volante a partir de 80? · reel 3D del 26-11-2026

| | |
|---|---|
| **Qué es** | Reel vertical 3D (Blender) de 32,4 s con Alex y Clod sobre el **equilibrado de ruedas**: por qué puede temblar el volante en autovía, cómo la equilibradora indica dónde va el contrapeso y el gag de Clod queriendo hacer de contrapeso. |
| **Hecho el** | 26-11-2026, tarea diaria de las 19:30 |
| **Idea** | Propuesta de Claude a partir de los datos: el mejor reel del canal empieza con un síntoma en el volante (alineación, 1.621 vistas, 10,8 veces la mediana de 150), y vidIQ mostraba explicadores animados de síntomas y mitos en tendencia. ChatGPT (gpt-6-luna) hizo 40 preguntas (la lista llegó cortada en la 34; Claude respondió todas), eligió la idea y escribió el prompt y la skill. Descartadas: "¿hay que apretar el botón del freno de mano?" (sin datos fiables hoy) y "¿cuándo cambiar las gomas?" (muy parecido a reels ya hechos). |
| **Datos comprobados** | RACE: [equilibrado de ruedas](https://www.race.es/equilibrado-de-ruedas) y [volante que vibra](https://www.race.es/volante-vibra) (vibración discontinua, más a partir de 80 km/h; contrapesos de unos gramos; equilibrar al cambiar neumáticos) |
| **Voz** | Alex = **Diego** (España, id cartesia-399002e9…), 5 frases, desde la versión 2 (26-11, 20:30). La versión 1 usó "Gonzalo", que resultó ser la voz de Panamá: Damián pidió acento de España. Cada frase de Diego se ajustó entre -6 % y +6 % a los tiempos de la animación. Clod no habla. |
| **Imagen** | Blender 5.3 EEVEE, 973 fotogramas, 1080×1920 al 67 % con 40 muestras, desenfoque de movimiento. Render en **unos 14 min** (19:54 → 20:08). Taller v2, equilibradora con pantalla de flechas, rueda realista que salta por desequilibrio y gira redonda con el contrapeso. |
| **Mejora del día** | Movimiento: **capa viva** (Alex cambia el peso de cadera a cadera y balancea la cabeza; Clod respira estirándose un poco). Es aditiva: no pisa los gestos. Medido en el mismo tramo: la cabeza de Alex se mueve 24 mm (antes 13) y la de Clod 14 mm (antes 9). Imagen antes/después en el PC: `EKORUEDAS_ESTUDIO_3D\referencias\evolucion\2026-11-26_capa-viva.png`. |
| **Sonido** | Voces igualadas, música funk-groove al 20 % con ducking, 4 efectos (arranque metálico de la máquina, clic del contrapeso, pop del susto de Clod, risa corta), -14,8 LUFS. Subtítulos con caja y palabras clave en #FF8400; rótulos "+80 km/h", "CONTRAPESO", "GIRA REDONDA", "GUÁRDALO". |
| **Ootto** | versión 2 (voz Diego): job `job_efdf10a2d734` · [ver el reel](https://mcp.ootto.ai/w/reel/acc_50544226d762-efdf10a2d734). Versión 1 (Gonzalo): `job_5c2f9c799356`, ya no se publica |
| **Publicación** | Instagram y YouTube Shorts (Ootto, versión 2): **27-11-2026 a las 19:00** · TikTok (vidIQ): versión 2 preparada para el 27-11 a las 19:00, pendiente del sí de Damián · Público · portada propia |

## Archivos
| Archivo | Qué es |
|---|---|
| `prompt_2026-11-26.md` | Prompt de producción de ChatGPT (revisado por Claude) |
| `data/voces.json` | Las 5 frases de Alex con el tiempo de cada palabra |
| `scripts-blender/build_equilibrado.py` | Escena completa: taller v2, equilibradora, rueda que gira y salta, contrapeso, pila con tabla para Clod, actuación de Alex y Clod, 9 planos y comprobación de encuadre |
| `scripts-blender/portada_bg.py` | Pose y cámara de la portada (Clod encima de la rueda, Alex con la mano de "¡para!") |
| `scripts-blender/hoja_prueba.py` | Hoja de fotogramas de prueba (se mira antes del render completo) |
| `scripts-blender/render_bg.py`, `encode_bg.py` | Render en segundo plano y paso a mp4 (encode_bg ya escala los fotogramas al 67 %) |
| `portada/texto_portada_2026-11-26.png` | Texto de la portada (se pone encima de la imagen de Blender) |

**Vídeo sin voz y portadas:** están en el PC, en `Escritorio\CLAUDE VIDEOS\2026-11-26_EQUILIBRADO-VOLANTE-TIEMBLA\render\video-sin-voz_2026-11-26.mp4` y `...\portada\`. Hoy no se han podido subir a GitHub porque la carpeta `CLAUDE VIDEOS` no estaba conectada a la tarea (la petición de acceso quedó esperando en el PC).
