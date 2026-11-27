# MAITE AAA · plan de trabajo

Damián (27-11-2026, 23:29–23:30): "Trabajaremos ahora mismo solamente para mejorar el diseño de esta chica" · "Me da igual cuántas horas o días te tome ... quiero que ese personaje quede impoluto".
Estándar: `skills/ekoruedas-aaa-character/SKILL.md` (su skill de ChatGPT, 23 puntos) + `skills/ekoruedas-automotive-cgi-4k/` para el render.
El vídeo de 30 h queda en espera hasta que Maite esté terminada.

## Punto de partida (comprobado el 27-11)
- Modelo de Tripo `maite_tripo.blend`: **una sola malla** de 9.664 vértices (rejilla de ~2 mm), textura 4K en atlas muy troceado, esqueleto Mixamo de 65 huesos con dedos. Sin cara animable: **ojos, cejas y dientes pintados**. Ropa pegada al cuerpo (no hay cuerpo debajo).
- PC: i9-12900KF, 32 GB de RAM, RTX 5060 8 GB, Blender 5.3. Rigify viene con Blender (sin instalar nada). QuadriFlow disponible. Wiggle Bones ya instalado.
- Hecho: trenza con 5 huesos propios y física de muelle con choques (`construir_maite_v2.py`, `maite_anim.py`), prueba `prueba_anim_v1.mp4`. Prueba de boca por deformación: **descartada** (estira los dientes pintados).

## Fases (cada una con pruebas renderizadas antes de pasar a la siguiente)
1. **Malla limpia y piezas separadas**: clasificar la malla por material (piel, pelo, trenza, camiseta, mono, puños, guantes, botas, funda, metal); retopología a quads más densa (cara más densa); texturas 4K re-horneadas desde Tripo; materiales por tejido.
2. **Cara de animación**: ojos 3D (esclera, iris, pupila, córnea con reflejos), párpados que cierran, boca abierta con dientes, encías y lengua, cejas que se mueven; shape keys con nombres ARKit (52) + visemas del español; huesos de mirada.
3. **Rig corporal**: Rigify (IK/FK, pole targets, foot roll, dedos curl/spread, twist bones), pesos revisados, correctivos en hombros, codos, rodillas y caderas.
4. **Pelo**: trenza (v1 hecha) mejorada, mechones sueltos, choques con hombro, cara y ropa.
5. **Ropa**: simulación de tela con pines (camiseta flexible, mono rígido y pesado, tirantes, bolsillos firmes), cuerpo de colisión oculto.
6. **Materiales y luz**: piel con subsurface, denim con trama y costuras, algodón, cuero de guantes y botas, metal de hebillas; luz de estudio AgX.
7. **Biblioteca de animación**: idles (varios), hablar, andar, correr, señalar, explicar, saludar, cruzar brazos, agacharse, sujetar herramientas y piezas, reír, sorpresa, enfado, pensar, gestos cómicos; lip sync desde el audio de Ootto.
8. **Pruebas obligatorias** (las 8 de la skill), hoja de personaje, turntable 360°, entrega (.blend maestro, FBX/GLB, documentación).

## Límites honestos
- Todo se hace por código en Blender (no hay escultor humano): cada forma se comprueba con renders y se corrige.
- La ropa venía fundida con el cuerpo: la tela simulada se apoya en un cuerpo de colisión creado por debajo.
- Nada se da por terminado sin vídeo o fotos verificadas.

## Estado
- 27-11 23:35 · Fase 0 hecha (inventario, fotos de referencia, prueba de trenza v1). Empieza la fase 1.
- 28-11 00:00 · **Fase 1 hecha**: malla soldada y con agujeros tapados, 9 materiales por tejido (piel con subsurface, pelo mate, camiseta, vaquero con sarga, puños, guantes, botas, funda, ojos/dientes), subdivisión aplicada (40.272 vértices) y otra al render. Fotos comparadas con el original: misma identidad, más suave.
- 28-11 01:00 · **Fase 2 en marcha** (`cara_maite.py`):
  - Ojos 3D: globo con iris avellana procedural (fibras, anillo límbico, pupila ajustable), córnea de cristal sin sombra, borde del párpado en dos pasos, huesos `Ojo_L/R` con seguimiento a `Mirada`.
  - Pintura vieja del ojo y del delineado repintada con el color de piel de alrededor; delineado 3D liso con rabito; 270 pestañas 3D por cara (arriba en dos filas y abajo).
  - Boca: abertura recortada por las curvas de los labios, cara interna del labio, dientes (24 piezas redondeadas en arco), encías, lengua y saco oscuro; nada de dentro asoma por la piel.
  - 52 shape keys con nombres ARKit (ojos 14, mandíbula 4, boca 23, cejas 5, mejillas 3, nariz 2, lengua 1) en la misma malla.
  - Pruebas: `prueba_cara.py` (estados de ojos y boca en primer plano).
