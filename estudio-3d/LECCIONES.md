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
