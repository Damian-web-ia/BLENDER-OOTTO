# Alex v2 · personaje de animación

Modelo generado con Tripo (plan Pro) a partir de la hoja de personaje. Retopologizado a ~10.000 cuadriláteros, con esqueleto Mixamo de 65 huesos, textura 4K y rig de animación propio. El archivo `.blend` está en el PC (`EKORUEDAS_ESTUDIO_3D\biblioteca\personajes\alex\alex_v2_rig.blend`), y en GitHub está el código para rehacerlo.

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
| Deformación | Conserva el volumen; suavizado correctivo (solo cuerpo, grupo `CS_cuerpo`); como mucho 4 huesos por vértice; axilas corregidas; pesos de hombros y trapecio suavizados y picos del cuello alisados (`alex_pesos2.py`) |
| Cara | 18 formas (shape keys): cejas arriba/enfado/triste, párpados, ojos abiertos, sonrisa, boca triste, boca O y ancha, nariz arrugada (por lado). Expresiones listas: neutra, sonrisa, risa, pícaro, enfado, sorpresa, triste, duda, concentrado |
| Boca por dentro | Labios cortados, cavidad oscura, dientes de arriba y abajo y lengua, pegados a la cabeza y a la mandíbula |
| Músculos | Bíceps, tríceps, deltoides, pectoral y antebrazo se hinchan solos según la postura del brazo (drivers por distancias): al doblar el codo, al subir el brazo o al cruzarlo |

## Archivos

| Archivo | Para qué |
|---|---|
| `alex_rig.py` | Crea el rig sobre `alex_v2.blend` (solo una vez) |
| `alex_pesos.py` | Corrige los pesos de las axilas (solo una vez) |
| `alex_mandibula.py` | Añade la mandíbula (solo una vez) |
| `alex_cara.py`, `alex_cara2.py` | Crea las 18 formas de la cara y las retoca (sonrisa sin cerrar ojos, ojos abiertos más visibles) |
| `alex_musculos.py` | Formas y drivers de los músculos |
| `alex_pesos2.py` | Suaviza los pesos de hombros/trapecio y quita los picos de la malla junto al cuello |
| `alex_anim.py` | **Funciones de animación** que usa cada reel |
| `alex_cargar.py` | Mete a Alex v2 en cualquier escena: `cargar_alex_v2(pos, giro_z)` |
| `pruebas_poses.py`, `pruebas_poses2.py` | Bancos de posturas para revisar deformaciones |
| `demo_alex.py` … `demo_alex4.py` | Demostraciones completas (la 4: con voz, expresiones y 5 planos, con comprobación automática de encuadre) |
| `escena_alex_clod.py` | Escena con Alex y Clod hablando (diálogo, banco de trabajo, 5 planos) |

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
cara(f, "sonrisa"); parpadeos(1, f)         # expresiones y parpadeos
hablar(VOZ)                                  # boca por sílabas + forma de "o" (formato [{"at", "words": [[txt, ini, fin]]}])
respirar(1, f); suavizar()                   # siempre al final
```

Funciones sueltas para poses propias: `mano_en(lado, f, (x, y, z))`, `codo_hacia`, `pie_en`, `rodilla`, `cadera`, `columna`, `cabeza`, `hombro`, `mano_pose`, `orientar_mano`, `boca`, `cara(f, expresion, intensidad, **ajustes)`, `parpadeo(f, lado=None)`.

Coordenadas: metros, en el espacio del personaje (mira hacia −Y; +X es su izquierda). Medidas de referencia: hombros a (±0,19; 0,05; 1,36), barbilla a (0; −0,12; 1,49), mano en reposo a (±0,31; −0,03; 0,89).

## Reglas aprendidas

- No girar a mano los huesos del brazo: siempre IK.
- Al agacharse, las manos van por fuera de las rodillas.
- Revisar de cerca (cámara a unos 2,5 m) los fotogramas de más movimiento antes de renderizar.
- En vídeo vertical, los gestos van cerca del cuerpo: manos a menos de 0,35 m del eje y nunca delante de la cara. Cada demo termina con `comprobar_encuadre()` y no se renderiza si devuelve fallos.
- Puños y gestos aguantan hasta el corte de plano; si una mano baja, que baje en vertical (sale por abajo, no por un lado).
- La sonrisa no debe tocar el párpado inferior (los ojos parecían cerrados): retocado en `alex_cara2.py`.
