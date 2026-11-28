# Controles de la cara de Maitane

Este documento explica cómo se mueve la cara de Maitane. Es la "documentación de los controles" que pide el prompt de la cara (`skills/maitane-cara-aaa/PROMPT_CARA_MAITANE.md`).

- **Archivo**: `maite_v2.blend`. Durante las pruebas se usa la copia nueva, `maite_v2_nuevo.blend`.
- **Objetos**: la malla `MAITE_cuerpo` y el esqueleto `MAITE_rig`.

Todo lo de aquí se puede tocar a mano en Blender o desde Python con `maite_anim.py` (clase `MaiteAnim`).

## 1. Shape keys: 82 en total

Están en `MAITE_cuerpo`, en Propiedades del objeto → Datos de malla → Shape Keys. "Left" y "Right" son la izquierda y la derecha **de ella**.

### 52 de ARKit (estándar de Apple)

Valen para cualquier captura facial de iPhone y las acepta Unreal/Live Link Face.

| Zona | Claves |
|---|---|
| Ojos | eyeBlink, eyeLookDown, eyeLookIn, eyeLookOut, eyeLookUp, eyeSquint, eyeWide (Left/Right) |
| Mandíbula | jawForward, jawLeft, jawRight, jawOpen |
| Boca | mouthClose, mouthFunnel, mouthPucker, mouthLeft, mouthRight |
| Boca (por lado) | mouthSmile, mouthFrown, mouthDimple, mouthStretch, mouthPress, mouthLowerDown, mouthUpperUp (Left/Right) |
| Labios | mouthRollLower, mouthRollUpper, mouthShrugLower, mouthShrugUpper |
| Cejas | browDown (Left/Right), browInnerUp, browOuterUp (Left/Right) |
| Mejillas y nariz | cheekPuff, cheekSquint (Left/Right), noseSneer (Left/Right) |
| Lengua | tongueOut |

### 30 propias (control fino por zonas, estilo FACS)

| Zona | Claves |
|---|---|
| Cejas por partes | browInnerUpLeft/Right (solo el lado de dentro de una ceja), browOuterDownLeft/Right, browSqueezeLeft/Right (frunce hacia el centro) |
| Párpados por separado | eyeUpperLidUp/Down Left/Right, eyeLowerLidUp/Down Left/Right |
| Mejillas | cheekRaiseLeft/Right, cheekSuckLeft/Right |
| Nariz | nostrilFlareLeft/Right, noseWrinkle |
| Labios | upperLipRaise, lowerLipDepress, lipTightenLeft/Right |
| Mentón y mandíbula | chinRaise, jawClench |
| Lengua | tongueUp, tongueLeft, tongueRight |

### Cara de reposo

La base (todas las claves a 0) tiene:

- La boca cerrada.
- Los ojos algo abiertos.
- El arco de las cejas un poco alto.
- Una sonrisa muy leve.

Cada clave lleva solo lo que le falta para su pose completa. Por eso las 82 se pueden mezclar sin que nada se dispare.

## 2. Ojos

- **Mirada**: el hueso `Mirada` de `MAITE_rig` es el punto al que miran los dos ojos. Está a 1 m delante de la cara y es hijo de la cabeza.
  - Para mirar a un lado, mueve su posición: X positiva es su izquierda y Z positiva es arriba. 0,10 m son unos 6°.
  - En Python: `A.mirar(f, x, z)`.
- **Pupilas**: la propiedad `pupila` del esqueleto (Propiedades del objeto → Custom Properties).
  - 1 es normal, 0,6 contraídas y 1,4 dilatadas. Va de 0,5 a 1,6.
  - En Python: `A.pupila(f, valor)`.
- **Parpadeo**:
  - `A.parpadeo(f, doble=False, parcial=1.0)` hace un parpadeo de unos 0,2 s.
  - `A.parpadeos_auto(f0, f1, evitar=[(a, b)])` reparte parpadeos naturales cada 2–5 s y se salta los tramos indicados.
- **Microsacadas**: `A.mirada_viva(f0, f1, amplitud=0.026)` da pequeños saltos de la mirada cada 0,5–1,5 s, para que no parezca fija.

## 3. Biblioteca de expresiones: 45

Se usan con `A.expresion(f, "nombre", intensidad=1.0)`. La expresión se mezcla con la anterior según la distancia entre claves.

neutra, alegria, sonrisa_natural, sonrisa_asimetrica, risa, entusiasmo, satisfaccion, tristeza, sorpresa, miedo, enfado, frustracion, preocupacion, nerviosismo, confusion, incredulidad, curiosidad, concentracion, pensamiento, verguenza, cansancio, aburrimiento, sarcasmo, ironia, comica, guino, sonrisa_profesional, sonrisa_espontanea, felicidad, risa_suave, carcajada, seguridad, determinacion, orgullo, complicidad, sorpresa_leve, sorpresa_intensa, impaciencia, decepcion, desaprobacion, sospecha, explicando, pensamiento_profundo, ceja_izquierda, ceja_derecha.

Las expresiones son diccionarios de shape keys (`EXPRESIONES` en `maite_anim.py`). Para añadir una nueva basta una línea:

```python
EXPRESIONES["mi_gesto"] = {"browInnerUp": 0.6, "mouthSmileLeft": 0.4}
```

## 4. Microexpresiones

`A.microexpresiones(f0, f1, fuerza=1.0)` añade gestos de menos de medio segundo cada 1,4–3,5 s, por ejemplo:

- las aletas de la nariz,
- media ceja,
- una comisura que se tensa,
- una mejilla,
- la barbilla,
- el párpado de abajo.

Usan claves propias que ninguna expresión toca, así que se suman a cualquier expresión sin pisarla.

## 5. Labios: sincronización con el español de España

`A.hablar(palabras, f_inicio)` recibe las palabras con sus tiempos, por ejemplo `[{"text": "Hola", "start": 0.0, "end": 0.35}, …]`. Así las devuelve la voz generada.

Cada letra se reparte en el tiempo de su palabra (las vocales pesan más) y pone su visema:

| Visema | Letras |
|---|---|
| a | a, á |
| e | e, é |
| i | i, í, y |
| o | o, ó |
| u | u, ú, ü |
| mbp | m, b, p, v |
| fv | f |
| dental | t, d, n, l, s, r, z, c, ñ, x |
| ch | ch, ll |
| kg | k, g, j, q, h |
| reposo | final de cada palabra |

## 6. Cabeza, respiración y vida

- **Cabeza**: `A.cabeza(f, arriba, giro, ladeo)`, en grados. Se reparte entre el cuello (35 %) y la cabeza (65 %).
  - El modelo de Tripo traía la cabeza girada unos 12° a su izquierda y ladeada unos 3°.
  - `MaiteAnim` lo mide al empezar con la línea de los ojos (log: `CABEZA_CALIBRADA`) y lo corrige siempre. Así, `A.cabeza(f)` la deja de frente y derecha.
- **Respiración**: `A.respirar(f0, f1)`.
- **Micro-movimientos de la cabeza**: `A.vida(f0, f1)`.
- **Trenza**: `A.finalizar(f0, f1)` hornea la trenza (muelle con choques contra el pecho y el hombro) y suaviza todas las curvas. El muelle da el mismo movimiento a 24 o a 60 fps.

## 7. Pruebas y hojas

- **Hoja de referencia facial**: `hoja_cara.py`. Saca vistas, primeros planos, las expresiones y los visemas. Con `HOJA_SOLO=nombre1,nombre2` saca solo esas.
- **Demostración facial**: `pruebas_maite.py … demo_cara [carpeta_voz]`. Dura unos 43 s y es vertical 9:16.
  - Incluye las 13 pruebas del punto 13 del prompt.
  - `MAITE_FPS=60` la saca a 60 fps.
  - `MAITE_FOTOS="2,6.5,…"` saca fotos de control en esos segundos en vez del vídeo.
