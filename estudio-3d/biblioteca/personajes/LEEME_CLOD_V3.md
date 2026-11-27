# Clod v3 · robot de 32 cm (27-11-2026)

Damián, 27-11-2026 21:39: "quiero que hagas un modelo 3D mejor de Clod y que el Clod [de antes] se elimine". El Clod v2 queda retirado (historial de GitHub y `_papelera` del PC).

Mismo personaje: naranja, pantalla negra con ojos y boca LED, cascos naranjas, símbolo blanco en el pecho, **sin antena** y **sin voz**. Es el ayudante de Maite, que es la cara de EKORUEDAS.

## Qué tiene de nuevo
- Carcasa de plástico pintado con barniz y microtextura; tapa del pecho con ranura, junta lateral y núcleo oscuro.
- Fuelles de goma en cuello y piernas; rodillas, codos, hombros y caderas de grafito con ejes y tapas de acero.
- Cascos con almohadillas de piel, tapa de grafito, aro de luz verde azulado (#00827C de la marca), botón de acero y deslizadores; diadema acolchada.
- Pantalla de cristal con reflejos, marco con 4 tornillos Allen y LED de puntos (de lejos se ven como trazo continuo).
- Nuca con tapa, rejilla y 4 tornillos; espalda con 3 rejillas y 4 tornillos.
- Manos con palma, tres dedos y pulgar; muñequeras; botines con suela de goma y tacos.

## Construirlo
```
blender -b --factory-startup --python clod_v3.py -- <salida.blend>
```
En el PC: `EKORUEDAS_ESTUDIO_3D\biblioteca\personajes\clod\clod_v3.blend` (colecciones `CLOD_v3_personaje` y `CLOD_v3_controles`, esqueleto `CLOD_v3`).

## Animarlo
Igual que antes, con `clod_anim.py`: el esqueleto, los controles (`CTRLC_mano_R/L`, `CTRLC_codo_R/L`, `CTRLC_pie_R/L`, `CTRLC_rodilla_R/L`) y las caras LED (`CLOD_Ojo_R/L`, `CLOD_Boca` con las mismas formas) no cambian.

```python
exec(open(r"...\personajes\clod_anim.py", encoding="utf-8").read())
CL = ClodAnim()            # elige CLOD_v3 si está en la escena
CL.reposo(1); CL.mover(1, (x, y, z), giro_z); CL.cara(f, "feliz"); f = CL.saludo("R", f)
CL.parpadeos(1, FIN); CL.suavizar()
```

## Prueba antes / después
`prueba_clod_v3.py` saca 4 fotos (comparación con v2 si está, primer plano de la cara, espalda y saludo).
