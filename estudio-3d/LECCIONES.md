# Lecciones de los reels 3D

## 2026-11-25 · ¿Ruedas nuevas delante o detrás?

- **Luz quemada** en la primera prueba (clave 1500 W, suelo con barniz): se bajó la clave a 650 W y se oscureció el suelo. Punto de partida: clave 650 / relleno 180 / contra 600.
- **Texto blanco ilegible** sobre fondos claros: placa negra al 60 % detrás de cada título (`cam_plate`).
- **Textos dentro de la escena:** van colgados de la cámara a 0,4 m (siempre delante) y no a 3 m, donde los tapaban los personajes.
- **Clod se pierde en planos abiertos** (mide 32 cm): en planos de seguimiento, cámara baja (0,5 m) y a menos de 2 m.
- **Portada:** comprobar con `world_to_camera_view` que cada personaje cae dentro del cuadro antes de renderizar.
- **Revisión de Ootto:** 5 avisos por textos encima de cosas. El coche del inserto pisaba títulos y subtítulos, y el título del final tapaba la cara de Alex. Arreglos: cámara cenital más alta, subtítulos con caja oscura y el encuadre del final más abajo. **Regla:** antes del render, mirar cada plano con su texto puesto.
- **Velocidad:** EEVEE a 1080×1920 con 32 muestras va a unos 0,8 s por fotograma, así que 1000 fotogramas tardan unos 13 min.
- **Pendiente:** en los últimos 2 s la cabeza de Alex roza «CAMBIA LAS CUATRO» porque la cámara se acerca. Regla: con *push-in*, título más arriba o cámara quieta.
- **Publicación:** Ootto separa las publicaciones de Instagram al menos 30 min y vidIQ recomienda espaciar TikTok. Si el día ya tiene vídeo a las 19:00, el reel 3D sale a las 19:30 (IG/YT) y a las 20:00 (TikTok).

## 2026-11-26 · Alex v2 con Tripo
- La API de Tripo y la clave de prueba de Hyper3D no tenían créditos; la web de Tripo genera gratis pero **exportar requiere plan Pro**.
- Tripo pide **retopología** antes del rig cuando el modelo pasa del límite de polígonos (4,7 M triángulos → 10.000 cuadriláteros).
- Con pose A pegada al cuerpo avisa de que el rig puede salir mal; "intentar de todos modos" funcionó bien.
- Exportar en **FBX + Blender + esqueleto**: se descarga un .zip `tripo_convert_*.zip` en Descargas.
- En Blender, importar el FBX con `temp_override` de una vista 3D (si no, falla `mode_set`).
- **Brazos de Alex v2: usar IK, no rotaciones sueltas.** Rotar los huesos `mixamorig:RightArm/ForeArm` a mano dejó el brazo dislocado (hombro hundido, codo recto, muñeca doblada). Solución: restricción IK en `RightForeArm` (chain_count=2) con un empty de objetivo para la mano y otro de polo para el codo (pole_angle −135° en este rig, codo hacia fuera y abajo). Para saludar: codo a la altura del hombro y antebrazo vertical; el saludo se anima moviendo solo el objetivo de la mano de lado a lado. Ejemplo: `biblioteca\personajes\alex\alex_v2_saludo.blend`.
- Antes de renderizar, revisar siempre fotogramas de cerca (vista frontal, a 2,5 m) en los momentos de más movimiento.

## 2026-11-26 (noche) · Alex con expresiones y Clod v2
- **Hombro con pico al subir el brazo:** la malla de Tripo tenía 7 vértices salidos junto al cuello y cortes bruscos de peso entre Shoulder, Arm y Neck. Se alisaron los picos (moviendo también todas las shape keys) y se suavizaron los pesos en una zona acotada. Medir antes de corregir: largo de aristas en pose contra reposo (`metrica_alex`).
- **Sonrisa que cerraba los ojos:** la forma de sonrisa subía el párpado inferior. Se anula el movimiento vertical cerca del ojo.
- **Encuadre vertical:** gestos amplios (manos a 0,45 m del eje) se salían por los lados en 9:16. Regla: manos a menos de 0,35 m del eje y comprobación automática de encuadre antes de cada render.
- **Clod por código mejor que con Tripo:** un robot de piezas rígidas no necesita pesos ni retopología y nunca se deforma mal. Tripo se queda para personajes orgánicos.
- **Pantalla LED:** con una sola tira de 32 columnas se hacen todas las formas (ojos, arcos, enfado, boca) como shape keys; el habla debe sumarse solo en vertical o deforma la expresión.
- **Pulgar arriba de Clod:** girar la muñeca buscando que el pulgar apunte a +Z (`orientar_pulgar`), no a ojo.
- **Pantalla negra:** el barniz fuerte hacía espejo y se veía gris; poco barniz y poco especular.
- **Copias base64 largas:** al pasar audio de Ootto al PC, comprobar con md5 por trozos; un fallo de copia dejó el audio con errores de CRC.
- **Diálogo entre dos:** montar la pista de voces una vez (con sus silencios) y animar cada boca con sus propios tiempos.
- **La vista previa de `look` con `frames` no usa el formato 9:16:** enseña más a los lados que el render final. Para los planos verticales, fiarse de `comprobar_encuadre()` (usa el formato real) o de un fotograma del render.

## 2026-11-26 (tarde) · Despiece 3D del neumático
- **Rayos X sin tocar cada material a mano:** un atributo de tipo *View Layer* llamado `xray` (propiedad de la escena animada de 0 a 1) mezcla cada material del coche con transparente + emisión azul en los bordes (Layer Weight). Los materiales compartidos con el taller (gomas, llantas) se copian antes para que el taller no se vuelva transparente.
- **Miles de trozos en una sola malla:** 2.160 cajitas sobre la superficie del neumático y una shape key `explota` con cada trozo ya desplazado y girado. Barato de renderizar y se puede invertir para que vuelvan.
- **Cortes de plano y desenfoque de movimiento:** con `motion_blur_position = 'START'` y claves constantes en el último fotograma de cada plano no se mezclan dos planos en un fotograma.
- **Booleanas con el cortador oculto:** ocultar el cilindro con `hide_set(True)` y `hide_render`, no con `hide_viewport` (si no, la booleana puede dejar de evaluarlo).
- **Personajes muy pequeños (Clod mide 0,26 m):** subirlo a algo (capó, neumático tumbado) para que salga grande en 9:16 y además da juego cómico.
- **Comprobar encuadres con renders rápidos de verdad** (30 %, 12 muestras, ~1 s por fotograma): `probar_fotogramas.py`. La vista `look` engaña en vertical.
- **Rótulos que siguen a las piezas:** las posiciones en pantalla se calculan evaluando las curvas de animación (`anclas.py`), sin mover la escena; luego el montaje dibuja los textos con PIL.

## 2026-11-26 (tarde, 2) · Despiece v2 realista (lo que pidió Damián)
- **No vale "algo circular que cambia de color".** Cada pieza se modela como es: carcasa = 900 hilos de poliéster que abrazan el talón; cinturones = cables de acero trenzados a ±24° (cruzados); talón = haz de 4x4 alambres con baño de latón + relleno de goma dura; banda con su dibujo; flancos con nervios y marcado en relieve (205/55 R16 91V, TUBELESS, RADIAL; nunca marcas).
- **Hilos y cables como tubos con UV** (`neumatico_real.malla_tubos`, todo con numpy, ~600.000 vértices en total, se construye en 2 s). El UV a lo largo del cable permite un relieve de trenzado realista.
- **Cables muy finos brillan con ruido** a resolución de reel: radio 0,7 mm, 300 por cinturón y rugosidad 0,48.
- **Referencia de estilo que le gusta a Damián:** el vídeo de la caja de cambios del Jesko (piezas metálicas con detalle, planos macro con desenfoque, fondo de estudio). Para piezas pequeñas (talón) subir el diafragma (f/7) o no se ve nada enfocado.
- **Sin brillos de colores para marcar la capa activa:** se marca con el plano macro, el rótulo y la línea al borde de la pieza.
- **Clod no habla** (decisión de Damián): solo hace gestos de fondo (encogerse de hombros, taparse la cara, señalar, decir que no con el dedo, saltar). Todas las voces son de Alex. Clod sobre el capó, a un lado de Alex para que no lo tape.
- **Cambiar la voz sin rehacer la animación:** `despiece_neumatico_v2.py` lee `voces_alex.json` (tiempos de cada palabra) y estira o encoge la línea de tiempo entera con una función por tramos sacada de palabras clave (cada clave de animación se mueve, con sus asas). Escribe `warp.json`, que usan el montaje y la mezcla de audio. Así una voz nueva solo cuesta generar las frases.
- **`reel_voice` admite voces que no son premium** (por ejemplo "Gonzalo"). Antes de decir "voz grave" o "voz aguda", medir el tono: Gonzalo ronda 142 Hz (no es grave), pero es la más expresiva; Carlos 102 Hz.
- **En el montaje no reutilizar `W` para dos cosas** (ancho de pantalla y función de tiempo): la función se llama `WP`.
- **Voces con el mismo nombre:** en Ootto hay dos "Gonzalo" (Panamá y España). Pedirla por nombre dio la de Panamá y a Damián le sonó latina. Pedir siempre la voz por su id (`reel_voice="cartesia-…"`) y comprobar el acento en `voice_list`. Damián quiere **español de España** para Alex.

## 2026-11-26 (19:30) · Reel del equilibrado
- **Capa viva aditiva** (modificadores de curva tipo seno con `use_additive`): Alex cambia el peso y balancea la cabeza, Clod respira. No hace falta tocar cada gesto y se apaga con `activa=False` para comparar. Medido: cabeza de Alex 13 → 24 mm de movimiento en reposo; Clod 9 → 14 mm.
- **Neumático tumbado = agujero en el centro:** el rayo para subir a Clod a la pila atravesó el hueco. Poner una tabla encima de la pila.
- **La pantalla de la equilibradora del taller v2 estaba hundida en el panel** (no se veía): se sube 5,6 mm por su normal.
- **Dos personajes separados 1,4 m no caben en 9:16 de frente:** o se alinean en profundidad (cámara de lado) o se usa un objetivo corto (17-20 mm) en el plano general.
- **Rueda que gira:** 18° por fotograma con desenfoque de movimiento se lee bien; el desequilibrio se ve haciendo "saltar" el centro de la rueda 1 cm en cada vuelta.
- **Mañana en diseño:** Alex tiene la cara muy sonriente aunque la expresión sea "duda" o "enfado": revisar la intensidad de las formas de la boca al hablar.


## 2026-11-26 (noche) · Personaje de dibujos con pelo físico (Rulo)
- **Wiggle Bones 1.1.2** instalado desde extensions.blender.org (comprobado su sha256; sin permisos de red ni de archivos). Sirve para pelo, orejas, colas y ropa con rebote.
- **Hornear sin el operador del complemento:** se activa `scene.wiggle.enable`, se avanza fotograma a fotograma (25 de "preroll" para que el pelo ya esté asentado), se guarda `matrix_basis` de cada hueso de pelo y luego se apaga la simulación y se ponen las claves. Así el render en segundo plano no depende del complemento.
- **Mechones = tubo de 22 anillos + cadena de 3 huesos** (rigidez 520/380/260 de raíz a punta, amortiguación 1,2/0,9/0,7, gravedad 0,35). El contorno de cada mechón adelgaza hacia la punta con un grupo de vértices en el Solidify.
- **Brazos y piernas de goma:** huesos B-Bone de 8 segmentos con tiradores automáticos: el codo se curva solo, como en los dibujos clásicos.
- **Aspecto de dibujo en EEVEE:** Diffuse → Shader to RGB → rampa constante (sombra azulada) × color, y contorno con Solidify invertido + material negro con backface culling. Transformación de color "Standard" (AgX apaga los colores planos).
- **Franja gris en la frente:** era la sombra del casquete de pelo; se quita con `visible_shadow = False` en el casquete.
- **`mode_set` tras `read_homefile(use_empty=True)`** falla por contexto: usar `temp_override` con ventana, área y objeto activo.
