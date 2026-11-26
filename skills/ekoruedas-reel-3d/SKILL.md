---
name: ekoruedas-reel-3d
description: Skill para idear, producir y publicar reels diarios de EkoRuedas en 3D con Blender, usando datos reales del canal, tendencias verificadas, voces de Ootto y animación de Alex y Clod. Mantiene las reglas editoriales, técnicas y de seguridad del canal, y aprende de las métricas de cada publicación.
---

# ekoruedas-reel-3d

## Propósito

Crear reels verticales diarios, informativos y con humor blanco para Instagram, YouTube Shorts y TikTok. Cada reel debe abrir con un gancho comprensible desde el primer segundo, explicar una sola idea con claridad y buscar retención y guardados.

Esta skill guía el proceso de principio a fin: analizar datos, entrevistar al responsable, elegir tema y tendencia, escribir el guion, planificar la animación, producir las voces, preparar Blender, montar, revisar, publicar y registrar las lecciones.

## 1. Reglas fijas del canal

### Formato y publicación

- Reel vertical **1080 × 1920**, **30 fps**, normalmente **30–40 s**.
- Gancho durante el primer segundo.
- Publicación diaria a las **19:00 Europe/Madrid**, en la fecha indicada por el responsable.
- Instagram y YouTube Shorts se programan desde Ootto; TikTok desde vidIQ, salvo que el responsable indique otra cosa.
- Público general; explicar sin presuponer conocimientos mecánicos.

### Identidad dentro del vídeo

Dentro del vídeo no se muestra:

- Logo.
- Nombre del taller.
- Teléfono.
- Web.

Esos datos solo pueden aparecer en el pie de texto y se deben copiar del bloque oficial guardado, nunca improvisar.

### Personajes

**Alex**

- Mecánico de unos 45 años, piel morena y barba corta canosa.
- Mono negro liso con ribetes naranjas.
- Serio, seco y claro; puede usar ironía contenida y una media sonrisa.
- Desde el 26-11-2026, Alex pone **todas las voces**, con voz **Diego** (España): `reel_voice="cartesia-399002e9-7f7d-42d4-a6a8-9b91bd809b9d"`. Pedirla siempre por este id: hay voces con el mismo nombre y otro acento (el "Gonzalo" de Panamá sonaba latino y Damián no lo quiere). Acento de España siempre.
- Animar la mandíbula según los tiempos de voz.
- Usar el rig de Alex v2 y las poses disponibles.
- Mantener respiración y cambios de peso continuos: Alex nunca queda completamente inmóvil.
- Anticipar los gestos: ojos y cabeza antes que brazo.
- En encuadre vertical, respetar la limitación de manos indicada en la producción del día y no cruzarlas delante de la cara.

**Clod**

- Robot naranja de 32 cm, rígido por piezas, pantalla negra con ojos LED blancos, auriculares naranjas y símbolo blanco en el pecho.
- Sin antena.
- **No habla nunca.**
- Comunica con expresiones LED y gestos: duda, sorpresa, susto, enfado, tristeza, risa, salto, saludo, pulgar arriba, encogerse o taparse la cara, entre otros recursos disponibles en Clod v2.
- Es torpe y gracioso, pero sus gags no deben promover acciones peligrosas ni avergonzar a personas.
- Mantener respiración y cambios de peso continuos.

### Producción visual

- Imagen y animación se producen únicamente en **Blender**; no utilizar imágenes o vídeo generados por IA.
- Todo se modela por código.
- El formato visual preferido es el **despiece 3D**: pieza visible por dentro, rótulos claros y macros realistas.
- Textos y rótulos se añaden en el montaje, no en Blender.
- No inventar datos técnicos, cifras, precios, intervalos ni especificaciones.
- Si un detalle no está confirmado por una fuente aceptada o por el responsable, no se afirma como hecho.

### Biblioteca disponible

Antes de modelar algo nuevo, revisar si ya existe:

- Alex v2, rig con IK de brazos y piernas, seis poses de mano, nueve expresiones, mandíbula sincronizable, caminar, agacharse, señalar, pulgar arriba y encogerse.
- Clod v2, piezas rígidas, caras LED y acciones disponibles.
- Coche compacto, ruedas nuevas y gastadas.
- Taller, carretera cenital mojada, estudio con ciclorama y banco de trabajo.
- Neumático realista por capas: carcasa, cinturones, talón y banda.
- Respiración y cambios de peso continuos incorporados a los personajes.

## 2. Flujo diario obligatorio

### Paso 0 — Mejora pequeña de biblioteca

Cada día se intenta una mejora pequeña de diseño o movimiento de Alex o Clod.

1. Elegir un cambio acotado: una transición, una expresión, una pose, un ajuste de peso o un detalle de diseño.
2. Guardar una prueba **antes/después**.
3. Revisar que el cambio no rompa rigs, escalas, materiales o animaciones ya existentes.
4. Si la mejora no pasa la prueba, no sustituir la versión estable. Registrar el fallo.
5. No dejar que una mejora experimental bloquee el reel del día.

### Paso 1 — Reunir información y entrevistar

Antes de proponer el reel, recopilar:

- Insights recientes de Instagram, YouTube y TikTok disponibles en Ootto.
- Vistas y mediana reciente, retención o tiempo medio, guardados y comentarios.
- Outliers: qué publicación superó claramente la mediana y qué tenía de particular.
- Tendencias actuales de vidIQ en España: temas, formatos y sonidos, con fecha de consulta.
- Temas ya publicados, programados o en producción.
- Fuentes técnicas autorizadas, si el tema necesita datos mecánicos.

Entrevistar al responsable con **30–40 preguntas numeradas**, agrupadas y concretas, cubriendo:

1. Objetivo y público.
2. Tendencias y ambiente.
3. Tema, síntoma, pieza y fuente.
4. Guion, humor y CTA.
5. Personajes y actuación.
6. Escenario, modelado, materiales, luces y cámaras.
7. Animación y tiempos.
8. Motor, resolución, fps y duración.
9. Voces, música, efectos y subtítulos.
10. Portada, pie, título, hashtags, publicación, métricas y riesgos.

Adaptar las preguntas a los datos ya disponibles: no volver a preguntar como incógnita algo que ya está fijado. Si, tras las respuestas, quedan decisiones imprescindibles sin resolver, hacer como máximo **10 preguntas adicionales**. No empezar a redactar el paquete final si falta una fuente técnica crítica, la fecha de publicación o una decisión necesaria para mantener la seguridad del gag.

### Paso 2 — Elegir tema con datos

Puntuar internamente las ideas según:

- **Gancho de síntoma reconocible**, preferiblemente en forma de pregunta.
- Rendimiento de temas y ganchos anteriores.
- Tendencia actual, indicando cuándo se consultó y en qué plataforma.
- Relevancia para conductores de Bizkaia y España.
- Potencial de explicación visual o despiece 3D.
- Diferencia frente a temas ya publicados o programados.
- Disponibilidad de fuente técnica autorizada.
- Posibilidad de explicarlo sin jerga ni datos inventados.

La mediana y los outliers guían la elección, pero no garantizan resultados. No presentar una tendencia como éxito seguro. Para cada propuesta final:

- Elegir una idea principal.
- Indicar **dos alternativas descartadas** y una razón concreta por cada una.
- Evitar repetir temas ya realizados, salvo que el responsable solicite expresamente una segunda parte.

### Paso 3 — Crear y guardar el paquete

Crear la carpeta del reel en GitHub:

```text
reels-diarios/AAAA-MM-DD_tema/
```

Usar la fecha de producción para la carpeta y registrar por separado la fecha y hora de publicación. Guardar como mínimo:

- Prompt de producción aprobado.
- Guion y tiempos de voz.
- Fuentes y datos permitidos.
- Notas de planos y animación.
- Resultados de revisiones.
- Métricas y lecciones después de publicar.

Guardar también el prompt y la skill utilizados, siguiendo la estructura existente del repositorio. No almacenar secretos, credenciales ni datos de acceso.

### Paso 4 — Voces primero

1. Preparar el guion final con todas las frases habladas por Alex.
2. Generar las voces en Ootto **antes de animar**.
3. Usar **Diego** para Alex, por su id (`cartesia-399002e9-7f7d-42d4-a6a8-9b91bd809b9d`).
4. No generar ni asignar ninguna voz a Clod.
5. Dividir la locución por frases para facilitar ajuste y edición.
6. Medir los tiempos por palabra y guardar el resultado en:

```text
data/voces.json
```

7. Ajustar la duración y los cortes de planos a las voces reales; no forzar una animación a un tiempo de voz imaginado.
8. Respetar el presupuesto diario de Ootto: **como máximo, aproximadamente siete créditos al día**. Priorizar pocas generaciones completas y cambios de texto antes de consumir créditos. Si se necesita una regeneración, identificar primero qué frase concreta falla.

### Paso 5 — Escena y animación en Blender

En el PC del taller:

1. Preparar el script diario para Blender 5.3.
2. Cargar:
   - `taller_v2.py`
   - Alex v2 mediante `alex_anim.py`
   - Clod v2 mediante `clod_anim.py`
3. Cargar los activos existentes antes de modelar.
4. Crear por código las piezas nuevas estrictamente necesarias.
5. Usar **EEVEE**, **30 fps**, lienzo **1080 × 1920** y escala de render **67 %**, salvo que el responsable haya fijado un ajuste diferente.
6. Renderizar en segundo plano y guardar el resultado en la carpeta del día.
7. Comprobar encuadre antes del render completo con fotogramas sueltos:
   - Siluetas y caras legibles en móvil.
   - Manos dentro del encuadre y fuera de las caras.
   - Zona libre para subtítulos.
   - Sin cámara atravesando geometría.
   - Piezas y despiece comprensibles.
   - Sin parpadeo ni efecto estroboscópico.
8. Mantener respiración y cambios de peso de ambos personajes incluso en planos de explicación.
9. Animar anticipaciones y reacciones: mirada o cabeza primero; brazo después. Evitar movimientos instantáneos sin preparación.
10. No introducir rótulos, subtítulos, logos ni nombres dentro de la escena de Blender; se añaden en montaje.

### Paso 6 — Transferencia y montaje

Transferir los renders desde el PC del taller a Ootto. Verificar que el material transferido está completo y corresponde a la versión aprobada.

Montar con Ootto y ffmpeg:

- Voz de Alex según `data/voces.json`.
- Música rítmica suave, inicialmente alrededor de **0,2** de nivel, con ducking bajo la voz.
- **2–4 efectos** pertinentes; evitar saturar o tapar la voz.
- Subtítulos ASS con caja oscura.
- Mezcla final objetivo de **−14 LUFS**.
- Exportar un máster vertical a 1080 × 1920 y 30 fps, además de los formatos adicionales acordados.
- Revisar el archivo final completo con sonido, no solo la línea de tiempo del editor.

### Paso 7 — Publicación

Preparar:

- Portada vertical **1080 × 1920**.
- Recorte **1080 × 1080** para vista cuadrada, si está solicitado.
- Título de YouTube.
- Pie de texto.
- Hashtags.
- Hora local de publicación.

El pie puede incluir el bloque fijo oficial del taller. Si no se encuentra el texto oficial, dejar un marcador para que lo inserte el responsable; no inventar nombre, teléfono, web ni dirección.

Programar a las **19:00 Europe/Madrid** en la fecha confirmada:

- Instagram y YouTube Shorts desde Ootto.
- TikTok desde vidIQ.
- Confirmar que las publicaciones son públicas y que la portada, el título y el pie son los correctos.

### Paso 8 — Aprender de los resultados

Tras la publicación, recoger las métricas disponibles en el momento acordado y registrarlas en la carpeta del reel y en `LECCIONES.md`.

Como mínimo, revisar:

- Vistas frente a la mediana reciente del canal.
- Tiempo medio de visionado y retención disponible.
- Guardados.
- Comentarios.
- Rendimiento del gancho y posibles puntos de abandono.
- Diferencias entre plataformas.
- Si el resultado fue un outlier y qué rasgo observable pudo contribuir.

No atribuir causalidad a un único factor sin evidencia. Registrar observaciones concretas, por ejemplo: “el gancho de síntoma retuvo mejor que el arranque con personaje”, no “la música causó el éxito” sin datos que lo sostengan.

Actualizar los recuerdos del cerebro de Claude si ese mecanismo está disponible y dejar la lección verificable en `LECCIONES.md`. Mantener aprendizajes útiles, no opiniones aisladas ni información personal innecesaria.

## 3. Estructura del guion

Ajustar la duración al tema. Como referencia para un reel de alrededor de 35 segundos:

1. **Gancho, 0–3 s:** síntoma o pregunta reconocible desde el primer segundo.
2. **Explicación, aproximadamente 3–13 s:** una causa posible o principio mecánico en lenguaje llano.
3. **Despiece, aproximadamente 13–19 s:** mostrar qué pieza hace qué.
4. **Gag, aproximadamente 19–25 s:** un gag claro de Clod, sin voz.
5. **Consecuencia y consejo, aproximadamente 25–32 s:** solo si está respaldado por fuente autorizada.
6. **Cierre, aproximadamente 32–35 s:** consejo, guardar o comentar.

El esquema es flexible: manda la claridad del tema y el tiempo real de la voz.

### Criterios del guion

- Empezar con un síntoma que el conductor pueda reconocer.
- Mantener una única idea central.
- Explicar en la misma frase cualquier palabra técnica necesaria.
- Evitar afirmaciones absolutas si la fuente solo habla de una posibilidad.
- No prometer diagnósticos remotos.
- Mantener el texto hablado dentro de la duración real del reel. Calcular con el audio generado, no solo con el número de palabras.
- El humor sirve a la explicación; no debe retrasar el gancho ni oscurecer el consejo.
- La CTA debe ser corta y pertinente: guardar, comentar o consultar a un profesional cuando corresponda.
- No incluir en voz ni texto datos del taller que solo pueden ir en el pie.

## 4. Fuentes y exactitud técnica

Antes de escribir una afirmación mecánica:

1. Registrar la fuente y el enlace exactos.
2. Extraer solo los datos necesarios para el reel.
3. Distinguir una causa posible de una causa segura.
4. No transformar una correlación o recomendación en una regla universal.
5. No inventar números, intervalos, costes, porcentajes, especificaciones ni promesas.
6. Si las fuentes se contradicen o no respaldan una afirmación, omitirla y pedir aclaración.
7. Evitar rótulos que impliquen una precisión que la explicación no tiene.
8. Revisar que portada, voz, subtítulos, caption y animación cuenten la misma historia.

## 5. Actuación creíble y seguridad

### Alex

- Mira al interlocutor o a cámara antes de comenzar el gesto.
- Usa gestos sencillos y económicos; no señalar continuamente.
- Mantiene postura viva con respiración y pequeños cambios de peso.
- Las expresiones deben acompañar la intención de la línea, sin sobreactuar.
- El humor de Alex se expresa con pausas breves, sequedad y una reacción precisa, no con crueldad.

### Clod

- Usar primero mirada/cabeza/pantalla LED; luego el cuerpo o el gesto.
- Preparar saltos, sustos o encogimientos con anticipación legible.
- En los gags de aplastar/estirar, respetar el estilo de squash and stretch de la biblioteca; no producir lesiones realistas.
- Darle una acción comprensible, una reacción y un remate visual.
- No asignarle palabras, voz, texto que parezca diálogo hablado ni sincronía de boca.
- No usarlo para ridiculizar conductores o clientes.

### Seguridad

- No representar como segura una conducta peligrosa con ruedas, elevadores, herramientas o maquinaria.
- No poner a Clod, a Alex ni a una persona en contacto con partes móviles.
- Si un gag utiliza una máquina, dejar claro visualmente cuándo está apagada o que el movimiento es una visualización separada.
- Evitar sustos de accidentes, burlas, lesiones gráficas o humor de mal gusto.
- La exageración mecánica debe leerse como visualización, no como instrucción de reparación.
- Comprobar cada plano por separado y como secuencia: una imagen aislada puede dar una impresión distinta a la intención del gag.

## 6. Cámara y composición vertical

- Diseñar primero para **9:16**; no encuadrar como un vídeo horizontal recortado.
- Mantener caras, pieza principal y gesto cómico dentro de la zona central segura.
- Reservar espacio para subtítulos, especialmente en la parte inferior.
- Evitar que elementos importantes queden bajo controles de interfaz de Instagram, TikTok o YouTube.
- Usar:
  - Primeros planos a la altura de los ojos para la explicación de Alex.
  - Macros lentos para piezas y despieces.
  - Planos algo más abiertos para que Clod se lea con claridad.
  - Movimientos cortos y deliberados; no mover cámara por adornar.
- No atravesar piezas ni ocultar la parte del componente que se está explicando.
- En rotación de ruedas, revisar desenfoque de movimiento y evitar parpadeo.
- Comprobar cada toma en una pantalla pequeña y en el recorte de portada solicitado.

## 7. Portada

- Debe funcionar sin audio y entenderse al primer vistazo.
- Mostrar a Alex y/o Clod con una emoción legible y coherente con el tema.
- Texto corto y grande; priorizar una pregunta o síntoma. Evitar frases largas.
- Usar el naranja **#FF8400** como color de énfasis y asegurar contraste con el fondo.
- No ocultar caras, gestos o pieza principal.
- Preparar los formatos acordados, normalmente 1080 × 1920 y recorte 1080 × 1080.
- Verificar el recorte cuadrado de forma real; no suponer que el centro de la portada vertical contiene todo lo importante.
- No poner nombre del taller, logo, teléfono o web en la portada del vídeo.

## 8. Sonido

- Alex es la única voz (Ootto, `reel_voice="cartesia-399002e9-7f7d-42d4-a6a8-9b91bd809b9d"` = Diego, español de España, elegido por Damián el 26-11-2026 a las 20:21). Clod no habla: sus reacciones se oyen con efectos cortos.
- Voces primero, frase a frase, con la emoción del guion; los tiempos de cada palabra (`words`) van a `data/voces.json` y mandan sobre la animación.
- Música suave de `/work/audio/music_library` a ~0,2, con `sidechaincompress` bajo la voz.
- 2-4 efectos de `/work/audio/sfx` o `/work/project/public/sfx_pack`, cada uno ligado a una acción visible.
- Igualar el volumen de cada frase con `volumedetect` antes de mezclar; máster con `loudnorm` a -14 LUFS.

## 9. Subtítulos y rótulos

- Subtítulos ASS en bloques de 2-4 palabras, Noto Sans Display 72, caja oscura semitransparente (`BorderStyle 3`), palabras clave en naranja #FF8400.
- Rótulos (nombres de piezas, "+80 km/h"…) se dibujan en el montaje, no en Blender, con placa oscura y nunca encima de una cara.
- Si algo se mueve por la parte baja del plano, los subtítulos suben bajo los rótulos.
- Antes de entregar, mirar una hoja de fotogramas con textos puestos.

## 10. Publicación

- Ootto `reel_schedule`: día siguiente 19:00 Europe/Madrid, `platforms ["instagram","youtube"]`, `privacy "public"`, `ai_generated true`, portada propia, título de máx. 100 caracteres sin el nombre del taller, 5-8 etiquetas. Si Ootto lo mueve por coincidir con otro post, se acepta y se apunta.
- TikTok con vidIQ: `vidiq_video_upload` → `vidiq_social_post_draft_create` (público, comentarios sí, música aceptada, `isAiGenerated true`) → si hay `suggestedPublishAt`, se acepta → `vidiq_social_post_publish`.
- Nunca se quita ni se mueve un post ya programado.
- Damián (26-11-2026, 21:37): "a partir de ahora todo esté publicado en YouTube, Instagram y TikTok". Los tres, siempre, a la misma hora.
- YouTube: Ootto sube como máximo 3 vídeos al día por marca; si se pasa, lo deja en cola y dice a qué hora sube (se acepta y se apunta, nunca se vuelve a subir).
- Comprobar YouTube después de cada publicación: `own_media_list(platform="youtube")`. El 26-11 el reel de las ruedas se programó en Instagram + YouTube y a YouTube no llegó. Si falta, `reel_post(platform="youtube", title, tags, privacy "public")` con el mismo job.
- YouTube Shorts (26-11-2026): Damián quiere monetizar, así que todo va como Short. YouTube lo clasifica solo: vídeo vertical 9:16 (o cuadrado), de 3 minutos o menos y público. No hay casilla aparte ni hace falta #shorts. Comprobado en own_media_list(platform="youtube"): `short: true` en psIf9sMLZGk (frenos, 27 s) y x5FS1ogsBQw (caja de cambios, 61 s). Nunca subir en 16:9 ni como oculto o privado: esas vistas no cuentan para monetizar.
- Pie: 1-2 frases con el dato y su fuente + bloque fijo del taller + 4-6 hashtags (#ekoruedas #derio #bizkaia #taller + 1-2 del tema).

## 11. Comprobaciones antes de entregar

- Datos: cada cifra tiene fuente (RACE, DGT, fabricante) apuntada en el LEEME del día.
- Imagen: un fotograma por plano al 40 % revisado; encuadre comprobado con `comprobar_encuadre()` y `world_to_camera_view`; nada atraviesa piezas.
- Sonido: voces claras, música por debajo, -14 LUFS.
- Identidad: ni logo, ni nombre, ni teléfono, ni web dentro del vídeo.
- Archivos: carpeta del día completa en GitHub (LEEME, prompt, scripts, voces.json, vídeo sin voz, portadas), fila en el índice y lecciones escritas.

## 12. Aprender de los datos cada día

- Leer `account_insights` (últimos 10) y `own_reel_outliers`: comparar vistas y tiempo medio de visionado de los reels 3D con los demás y frente a la mediana.
- Sacar 1-3 conclusiones con números reales y usarlas en la entrevista y en el guion (tipo de gancho, duración, protagonismo de Clod, portada).
- Apuntar lo aprendido en `LECCIONES.md` (proceso) y en `estudio-3d/LECCIONES.md` (diseño 3D).

## 13. Referencia técnica

Todo el detalle técnico acumulado (bpy, cámaras, luces, render en segundo plano, montaje con ffmpeg, publicación) sigue en `historial/SKILL_2026-11-25.md` y en `estudio-3d/LEEME.md`, `estudio-3d/LECCIONES.md` y las guías de `estudio-3d/biblioteca/personajes/`. Esta skill no las sustituye: las ordena.
