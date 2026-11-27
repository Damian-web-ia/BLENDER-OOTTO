# BLENDER-OOTTO · Vídeos de EKORUEDAS

Aquí se guarda todo lo que hacemos para los vídeos de **EKORUEDAS** (taller de neumáticos y mecánica en Derio, Bizkaia): personajes 3D, proyectos de vídeo, reels diarios, la skill que los dirige y el Cerebro de Claude.

**Cómo están nombradas las carpetas:** `AAAA-MM-DD_qué-es`. La fecha es el día en que se hizo. Dentro de cada carpeta hay un `LEEME.md` que explica qué contiene.

## Índice

> **27-11-2026 · Limpieza:** Damián pidió borrar todos los vídeos anteriores y quedarse solo con los modelos, y quitó las tareas diarias. Los vídeos viejos siguen en el historial (commit `454db14`); lo publicado en redes no se ha tocado. El proyecto Jesko no se ha tocado.

| Carpeta | Fecha | Qué es | Estado |
|---|---|---|---|
| [`2026-11-24_personajes-3d/`](2026-11-24_personajes-3d/) | 24-11-2026 | Personajes 3D reutilizables (Clod, el robot) | Alex retirado el 27-11-2026 · ahora presenta Maite |
| [`2026-11-25_video-jesko-koenigsegg/`](2026-11-25_video-jesko-koenigsegg/) | 25-11-2026 | Vídeo 3D de 60 s: "La caja de cambios imposible" (Koenigsegg Jesko) | Terminado con sonido en Ootto · sin publicar · render 4K a medias |
| [`2026-11-25_cerebro-de-claude/`](2026-11-25_cerebro-de-claude/) | 25-11-2026 | Código de la página "Cerebro de Claude" (cerebro 3D + mapa del sistema) y su zip | Se actualiza solo cada domingo |
| [`estudio-3d/`](estudio-3d/) | desde 25-11-2026 | Modelos 3D de piezas y personajes (Maite, Clod v3), plantillas de montaje y scripts de render | Solo modelos y herramientas desde el 27-11-2026 |
| [`reels-diarios/`](reels-diarios/) | 26-11-2026 | Reels diarios | Vacía desde el 27-11-2026 (tareas diarias borradas) |
| [`skills/`](skills/) | desde 25-11-2026 | La skill maestra CGI 4K y la skill `ekoruedas-reel-3d` | Sin tarea diaria desde el 27-11-2026 |
| [`LECCIONES.md`](LECCIONES.md) | desde 25-11-2026 | Lo aprendido (qué falló y qué funcionó) | Se conserva |

## Cómo se hace cada vídeo

1. **Ideas:** vidIQ da las tendencias; ChatGPT (por Zapier) entrevista a Claude y escribe el prompt del día y la skill.
2. **Voces (Ootto):** Maite con la voz Renata (español de España). Clod no habla.
3. **Animación y portada (Blender):** en el PC del taller, por código Python, con la skill CGI 4K (2160x3840, 60 fps, Cycles).
4. **De PC a Ootto:** el vídeo sin voz se sube aquí y Ootto lo importa desde este repositorio.
5. **Sonido y publicación (Ootto y vidIQ):** música, efectos y subtítulos; se publica a las 19:00 en Instagram, YouTube y TikTok.

## Personajes

- **Maite** (desde el 27-11-2026, la cara de EKORUEDAS): mecánica con trenza larga, mono vaquero azul, guantes y botas. Explica cada pieza. Voz: Renata (Ootto, español de España). Modelo de Tripo en `estudio-3d/biblioteca/personajes/tripo/`.
- **Clod** (en pantalla, "Claude"): robot naranja pequeño, pantalla negra con ojos LED blancos, auriculares naranjas, símbolo blanco en el pecho, sin antena. Entusiasta, torpe y gracioso. **No habla.**
- **Alex** quedó retirado el 27-11-2026 a petición de Damián ("quiero que elimines el modelo 3D de Alex"). Sus archivos siguen en el historial de GitHub y en la `_papelera` del PC.

> El repositorio es público para que Ootto pueda importar los vídeos. No subir aquí nada privado (claves, contraseñas, datos de clientes).
