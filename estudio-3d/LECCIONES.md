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
