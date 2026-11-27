# Plan de estilo 3D: EKORUEDAS

> **27-11-2026 (21:39), Damián:** "quiero que elimines el modelo 3D de Alex y quiero que hagas un modelo 3D mejor de Clod" y "desde ahora la chica sea la que pone la cara en ecorruedas". Alex queda retirado (lo de abajo sobre Alex es historia); la presentadora es Maite (Tripo) y Clod pasa a la versión 3.

## Meta visual

Personajes con acabado de película de animación 3D (estilo dibujo animado tipo Disney/Pixar o pictórico tipo Arcane, siempre con diseño propio: Alex y Clod no copian a ningún personaje existente), como la imagen de referencia de Damián (`referencias/objetivo_estilo_01.png`):

- caras expresivas: cejas gruesas que actúan, párpados, ojos grandes con brillo, boca con forma;
- piel suave con subsurface, ropa con textura de tela, pelo con volumen y mechones;
- poses con intención: peso, curvas y asimetría, nada rígido;
- fondos de un solo color o taller desenfocado, luz suave y cálida con contraluz.

## Regla de gasto

1. Lo caro se hace **una sola vez** y se guarda en la `biblioteca/`: personajes, coche, taller y materiales.
2. Cada reel **carga** la biblioteca y solo escribe cámaras, textos y acción (unas 150 líneas en vez de 500).
3. El gasto extra va únicamente a **mejorar el diseño**: **una mejora pequeña CADA DÍA** (pedido de Damián el 25-11-2026: "Quiero que esto sea diario, que cada dia vayas añadiendo a los personajes Alex y Cloude movimientos más realistas y un diseño más realista"). Un paso de la tabla de abajo por día, se prueba con un render de prueba antes y después y, si mejora, entra en la biblioteca.
4. Si una mejora sale bien, se sube la versión de la biblioteca (v1 → v2…) y todos los reels siguientes la heredan.

## Fases

| Fase | Qué se mejora | Estado |
|---|---|---|
| v1 (25-11-2026) | Biblioteca base: Alex, Clod, coche compacto, ruedas nuevas/gastadas, taller, carretera mojada, textos con placa | hecho |
| v2 | Cara de Alex: párpados, cejas que se mueven por clave, ojos más grandes con brillo, boca con 3 formas | hecho (26-11, Alex v2: 18 formas, boca con dientes y lengua) |
| v3 | Materiales: piel con subsurface, tela del uniforme, goma con relieve real (normal map procedural) | pendiente |
| v4 | Cuerpo de Alex con proporciones de dibujo animado (cabeza y manos más grandes, cintura, curvas) y rig con huesos | pendiente |
| v5 | Pelo con volumen (curvas de pelo o mechones modelados) e iluminación de estudio fija (clave cálida + contra) | pendiente |
| v6 | Clod v2: pantalla con expresiones animadas (texturas), brazos con codo, rebote al andar | hecho (26-11: pantalla LED con formas, IK, saltos con aplastar/estirar) |
| v7 | Fondos: taller desenfocado con profundidad de campo en primeros planos, y plano de color liso para portadas | pendiente |

## Cómo se decide qué mejorar

Cada día, antes de montar el reel (y el domingo se hace un repaso de la semana):

1. Se leen las cifras de los últimos reels (vistas, retención, comentarios) en Ootto o vidIQ.
2. Se revisa `LECCIONES.md`.
3. Se elige **una** mejora pequeña de la lista diaria: la siguiente pendiente o la que más afecte a lo que el público ve en los primeros 3 segundos y en la portada.

## Alex v2 (26-11-2026): modelo profesional disponible

- Modelo generado con Tripo (plan Pro de Damián) a partir de la hoja de personaje de ChatGPT, retopologizado a ~10.000 cuadriláteros y con **esqueleto automático tipo Mixamo** (65 huesos con dedos: `mixamorig:Hips`, `Spine`, `Spine1`, `Spine2`, `Neck`, `Head`, `LeftArm`, `LeftForeArm`, `LeftHand`…). Textura 4K (color, normal, rugosidad).
- **Solo en el PC** (no en GitHub, porque se parece a una persona real): `EKORUEDAS_ESTUDIO_3D\biblioteca\personajes\alex\alex_v2.blend` (altura 1,75 m, pies en el suelo, mirando a -Y). Archivos originales de Tripo en la misma carpeta.
- Imagen de referencia: `referencias\evolucion\2026-11-26_alex_v2.png`.
- **Rig de animación terminado (26-11-2026, madrugada):** IK de brazos y piernas, clavícula automática, dedos con poses, orientación de muñeca por objetivos, mandíbula para hablar, axilas corregidas, andar con pies clavados al suelo. Documentación y uso en `biblioteca/personajes/LEEME_ALEX_V2.md`. Demo: `Escritorio\CLAUDE VIDEOS\alex_v2_demo2.mp4`.
- **Noche del 26-11:** cara con expresiones, boca por dentro, músculos que acompañan al brazo, hombros sin picos, demo 4 con voz (`CLAUDE VIDEOS\alex_v2_demo4.mp4`).
- **Clod v2 hecho (26-11):** robot construido por código (`clod_v2.py`), piezas rígidas (no se deforma nunca), pantalla LED con 6 formas de ojos y 6 de boca, IK en brazos y piernas, saltos con aplastar y estirar. Animación con `clod_anim.py`. Demo: `CLAUDE VIDEOS\clod_v2_demo.mp4`. Escena con los dos: `escena_alex_clod.py` → `CLAUDE VIDEOS\alex_clod_escena.mp4`.
- **Siguiente mejora diaria:** usar Alex v2 en el reel diario (cargarlo con `alex_cargar.py` y animarlo con `alex_anim.py`) en lugar del Alex de bloques. Después: párpados y cejas, y Clod v2.
- Siguiente personaje: **Clod v2** con el mismo método (hoja de personaje → Tripo → retopología → rig "Otro" o huesos a mano).

## Lista diaria de mejoras (en orden; se marca la fecha al hacerla)

Diseño:
1. Alex: párpados que se cierran de verdad y cejas animables por clave. ✔ 26-11
2. Alex: ojos más grandes con iris y brillo especular; mirada que sigue a la cámara o a Clod.
3. Alex: boca con 3 formas (cerrada, abierta, "o") ligadas a las voces. ✔ 26-11
4. Alex: proporciones de dibujo animado (cabeza un 15 % mayor, manos más grandes, hombros redondeados).
5. Piel con subsurface y rubor suave; nariz y orejas mejor formadas.
6. Uniforme con textura de tela y costuras (ribete naranja más fino).
7. Pelo y barba con volumen (mechones modelados).
8b. Alex: cara seria de verdad (la malla sonreía en reposo): expresión "seria" nueva y neutra/duda/enfado/concentrado sin sonrisa residual. ✔ 27-11 (`alex_anim.py` v3; antes/después en `referencias/evolucion/2026-11-27_alex-cara-seria.png`)
8. Clod: pantalla con expresiones (feliz, susto, preocupado, solemne) cambiadas por clave. ✔ 26-11
9. Clod: brazos con codo y manos de 3 dedos; rebote elástico al andar. (codo y rebote ✔ 26-11; faltan dedos)
10. Iluminación de estudio fija y cálida con contraluz de color (look Arcane: borde cálido y sombras frías).
11. Materiales pro en todas las piezas nuevas (aceite líquido, cromo, acero mecanizado, fundición, pintura con barniz, goma). ✔ 27-11 (biblioteca/materiales_pro.py)
12. Líquidos: menisco en la superficie libre, gotas que caen y salpicaduras cuando la pieza se abre.
13. Desgaste: bordes con la pintura gastada, polvo en las zonas bajas, óxido en tornillos de piezas viejas.
14. Neumático y freno (biblioteca) con los materiales pro: goma con micro grano, disco de fundición con marcas de pastilla.
11. Goma de neumático con relieve real y carrocería con reflejos de estudio.
12. Fondo del taller con profundidad (fondo desenfocado en primeros planos).

Movimiento:
1. Respiración y peso en los dos personajes (nunca quietos del todo). ✔ 26-11 (capa viva: `capa_viva()` en alex_anim.py y `CL.respirar()` en clod_anim.py; antes/después en `referencias/evolucion/2026-11-26_capa-viva.png` del PC)
2. Anticipación y rebote en cada gesto (antes de levantar el brazo, baja un poco).
3. Movimientos con curvas suaves (ease in/out) y gestos que se solapan (cabeza antes que brazo).
4. Ciclo de andar de Clod con balanceo y de Alex con peso.
5. Miradas: los ojos se mueven antes que la cabeza.
6. Reacciones exageradas de Clod (squash and stretch al asustarse o alegrarse). ✔ 26-11
7. Alex: tela de la camiseta que acompaña al pecho al respirar; pliegues en el codo al doblar.
8. Clod: andar con pasitos y balanceo usado en un reel real.
