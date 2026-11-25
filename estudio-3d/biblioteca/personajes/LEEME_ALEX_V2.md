# Alex v2 · personaje de animación

Modelo generado con Tripo (plan Pro) a partir de la hoja de personaje. Retopologizado a ~10.000 cuadriláteros, con esqueleto Mixamo de 65 huesos, textura 4K y rig de animación propio. El archivo `.blend` **solo está en el PC** (`EKORUEDAS_ESTUDIO_3D\biblioteca\personajes\alex\alex_v2_rig.blend`), porque el personaje se parece a una persona real. Aquí, en GitHub, está el código.

## Qué tiene el rig

| Parte | Cómo se controla |
|---|---|
| Brazos | IK con objetivo de mano (`CTRL_mano_R/L`) y polo de codo (`CTRL_codo_R/L`), con polos calibrados |
| Piernas | IK con objetivo de pie (`CTRL_pie_R/L`, que también gira el pie) y polo de rodilla (`CTRL_rodilla_R/L`) |
| Hombros | La clavícula sube sola cuando la mano pasa por encima del hombro, o a mano con `hombro()` |
| Columna, cuello y cabeza | Giros repartidos entre Spine, Spine1 y Spine2, y entre Neck y Head |
| Cadera | Se mueve y gira con los pies fijos en el suelo |
| Manos | Seis poses de dedos (relajada, abierta, puño, señalar, pulgar, ok) y orientación automática de la muñeca por objetivos (pulgar arriba, palma arriba…) |
| Boca | Hueso `Mandibula` (máximo 7°), sincronizado con los tiempos de voz con `hablar_alex()` |
| Deformación | Conserva el volumen; suavizado correctivo; como mucho 4 huesos por vértice; axilas corregidas para que el torso no se hunda al subir los brazos |

## Archivos

| Archivo | Para qué |
|---|---|
| `alex_rig.py` | Crea el rig sobre `alex_v2.blend` (solo una vez) |
| `alex_pesos.py` | Corrige los pesos de las axilas (solo una vez) |
| `alex_mandibula.py` | Añade la mandíbula (solo una vez) |
| `alex_anim.py` | **Funciones de animación** que usa cada reel |
| `alex_cargar.py` | Mete a Alex v2 en cualquier escena: `cargar_alex_v2(pos, giro_z)` |
| `pruebas_poses.py`, `pruebas_poses2.py` | Bancos de posturas para revisar deformaciones |
| `demo_alex.py`, `demo_alex2.py` | Demostraciones completas |

## Cómo animarlo en un reel

```python
exec(open(r"...\personajes\alex_cargar.py", encoding="utf-8").read())
cargar_alex_v2((2.5, -1.5, 0), giro_z=-30)
exec(open(r"...\personajes\alex_anim.py", encoding="utf-8").read())
todo_reposo(1); bpy.context.scene.frame_set(1); calibrar_palma()
f = andar(10, pasos=4, zancada=0.6)          # anda hacia delante (dirección a la que mira)
f = saludo("R", f)                           # devuelve el fotograma en el que termina
f = senalar("L", f, objetivo=(1.5, -2, 0.6)) # señala un punto (coordenadas del personaje)
f = agacharse(f, mano_lado="R")              # se agacha a mirar algo del suelo
f = pulgar_arriba("R", f)
f = encogerse(f)
hablar_alex(VOCES_DE_ALEX)                   # mueve la mandíbula con las palabras
respirar(1, f); suavizar()                   # siempre al final
```

Funciones sueltas para poses propias: `mano_en(lado, f, (x, y, z))`, `codo_hacia`, `pie_en`, `rodilla`, `cadera`, `columna`, `cabeza`, `hombro`, `mano_pose`, `orientar_mano`, `boca`.

Coordenadas: metros, en el espacio del personaje (mira hacia −Y; +X es su izquierda). Medidas de referencia: hombros a (±0,19; 0,05; 1,36), barbilla a (0; −0,12; 1,49), mano en reposo a (±0,31; −0,03; 0,89).

## Reglas aprendidas

- No girar a mano los huesos del brazo: siempre IK.
- Al agacharse, las manos van por fuera de las rodillas.
- Revisar de cerca (cámara a unos 2,5 m) los fotogramas de más movimiento antes de renderizar.
- Pendiente: párpados y cejas (el modelo no trae huesos de cara) y Clod v2.
