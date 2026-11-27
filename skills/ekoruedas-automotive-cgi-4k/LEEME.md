# Skill: EKORUEDAS Automotive CGI 4K

| Qué | Detalle |
|---|---|
| **Qué es** | La skill maestra de calidad audiovisual que escribió Damián: estándar de CGI fotorrealista para todo lo mecánico (despieces, piezas, motores, frenos…). |
| **Fecha** | Guardada el 27-11-2026 (petición de Damián: "hagas una carpeta de skills y que también los modelos que hagas con estas skills los guardes también"). |
| **Archivo** | `SKILL.md`: el texto de Damián tal cual, con la cabecera para que Claude la cargue como skill. |
| **Modelos** | `modelos/`: cada pieza o escena hecha con esta skill, con su código y su LEEME. |
| **Copia en el PC** | `Escritorio\EKORUEDAS_ESTUDIO_3D\skills\ekoruedas-automotive-cgi-4k\` |

## Decisiones de Damián (27-11-2026, 17:47)
- **Calidad: el estándar completo de la skill.** 4K vertical 2160x3840, 60 fps, Cycles. Se aplica ya a los tres despieces de esta semana (batería, filtro de aceite, bujía), que se estaban renderizando en 1080x1920 a 30 fps con EEVEE: esos renders se pararon.
- **Logo: discreto al final.** Se usa el logo guardado en su cuenta de Ootto (`estudio-3d/marca/logo_ekoruedas.png`), pequeño, en una chapa oscura redonda con filo verde azulado (#00827C), bajo "¿QUÉ PIEZA DESMONTAMOS MAÑANA?". Sigue sin ir nombre del taller, teléfono ni web dentro del vídeo.
- **Tarea diaria de las 19:30:** sigue funcionando a la vez que la cola 4K (Damián lo eligió sabiendo que los dos trabajos se frenan y que la gráfica de 8 GB puede quedarse sin memoria). La cola reintenta sola si un render se cae.

## Cómo se hace el 4K60 con Cycles en su PC (RTX 5060, 8 GB)
- `estudio-3d/scripts/render_cycles_bg.py`: abre el .blend de siempre y, sin tocarlo, pone Cycles en la GPU (OptiX), 2160x3840, 60 fps (remapeo de tiempo x2: la animación hecha a 30 fps se evalúa en medios fotogramas), 64 muestras adaptativas, eliminador de ruido OIDN, árbol de luces, datos persistentes. Arregla el líquido para Cycles (sin subsuperficie ni brillo propio: transparente de verdad) y pone profundidad de campo enfocando con rayos lo que hay en el centro del cuadro (f/11 cerca, f/14 lejos, sin desenfoque en macro).
- 64 muestras con OIDN se ven igual que 128 (diferencia media < 1 de 255) y tardan la mitad: unos 26-45 s por fotograma en 4K. Cada vídeo (1.660-1.820 fotogramas) son unas 14-16 horas.
- `estudio-3d/scripts/cola_4k.py`: batería, filtro y bujía uno detrás de otro, reintento si se cae, y codificación a MP4 4K60 casi sin pérdida con `encode_bg.py` (fps y calidad nuevos).
- `estudio-3d/plantillas/montaje_despiece.py`: el diseño se sigue escribiendo en 1080x1920 y 30 fps, pero se dibuja a 2160x3840 y se compone a 60 fps (anclas interpoladas entre fotogramas, sin cruzar cortes). Salida H.264 "slow", CRF 18 con techo de 24 Mb/s.

## Pendiente
- **El vídeo de referencia** del punto 1 ("el vídeo adjunto") no llegó con la skill: falta que lo mande.
- **120 fps en cámara lenta** (punto 2, "cuando sea técnicamente viable"): de momento no; dobla otra vez el tiempo de render.
- **Personajes**: Alex y Clod son de estilo animación; la skill pide realismo para las piezas mecánicas, no cambia a los personajes.
- **Mañana en diseño:** Alex tiene la cara muy sonriente aunque la expresión sea "duda" o "enfado": revisar la intensidad de las formas de la boca al hablar.
