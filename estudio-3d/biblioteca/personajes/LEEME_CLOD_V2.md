# Clod v2 · robot de 32 cm

Robot naranja con pantalla negra y ojos y boca LED, cascos naranjas, símbolo blanco en el pecho y sin antena. Está hecho por código (`clod_v2.py`): son piezas rígidas pegadas a un esqueleto, así que no se deforma nunca.

## Construirlo

```
blender -b --factory-startup --python clod_v2.py -- <salida.blend>
```

En el PC: `EKORUEDAS_ESTUDIO_3D\biblioteca\personajes\clod\clod_v2.blend` (colecciones `CLOD_v2_personaje` y `CLOD_v2_controles`).

## Qué tiene

| Parte | Cómo se controla |
|---|---|
| Brazos | IK con `CTRLC_mano_R/L` y polo `CTRLC_codo_R/L` |
| Piernas | IK con `CTRLC_pie_R/L` (también gira el pie) y polo `CTRLC_rodilla_R/L` |
| Cuerpo, cuello, cabeza | Rotación en ejes del personaje |
| Pulgar | Hueso propio; `orientar_pulgar()` gira la muñeca para que apunte arriba |
| Pantalla | Ojos: `ojo_grande`, `feliz`, `cerrado`, `enfado`, `triste`. Boca: `abierta`, `O`, `plana`, `triste_boca`, `grande`. Habla: `abierta_habla` (solo abre en vertical) |
| Brillo LED | `brillo_led(escena)` añade un resplandor suave en el compositor |

## Animarlo

```python
exec(open(r"...\personajes\clod_anim.py", encoding="utf-8").read())
CL = ClodAnim()                     # o ClodAnim("CLOD_v2.001") si hay varias copias
CL.reposo(1)
CL.mover(1, (x, y, z), giro_z)      # dónde está y hacia dónde mira (metros, grados)
CL.cara(f, "feliz")                 # neutra, contento, feliz, risa, sorpresa, susto, enfado, triste, duda, serio
CL.mirar(f, x, z)                   # mueve los ojos por la pantalla
f = CL.saludo("R", f)
f = CL.pulgar_arriba("L", f)
f = CL.rebote(f, veces=2)           # saltitos sin despegar
f = CL.salto(f, alto=0.22)          # salto con anticipación, estiramiento y rebote
f = CL.andar(f, pasos=4)            # pasitos con balanceo
CL.hablar(VOZ)                      # [{"at": seg, "words": [[texto, ini, fin], ...]}]
CL.parpadeos(1, FIN); CL.suavizar() # siempre al final
```

Coordenadas en unidades de diseño (Clod mide 1; se multiplica por 0,32 m). Hombros a (±0,205; 0; 0,50), mano en reposo a (±0,252; −0,016; 0,27), cabeza centrada en z 0,80.

## Demos

- `demo_clod.py` → `CLAUDE VIDEOS\clod_v2_demo.mp4` (voz Diego, 4 planos).
- `escena_alex_clod.py` → `CLAUDE VIDEOS\alex_clod_escena.mp4` (diálogo con Alex).
