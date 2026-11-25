# Plan de estilo 3D: EKORUEDAS

## Meta visual

Personajes con acabado de película de animación, como la imagen de referencia de Damián (`referencias/objetivo_estilo_01.png`):

- caras expresivas: cejas gruesas que actúan, párpados, ojos grandes con brillo, boca con forma;
- piel suave con subsurface, ropa con textura de tela, pelo con volumen y mechones;
- poses con intención: peso, curvas y asimetría, nada rígido;
- fondos de un solo color o taller desenfocado, luz suave y cálida con contraluz.

## Regla de gasto

1. Lo caro se hace **una sola vez** y se guarda en la `biblioteca/`: personajes, coche, taller y materiales.
2. Cada reel **carga** la biblioteca y solo escribe cámaras, textos y acción (unas 150 líneas en vez de 500).
3. El gasto extra va únicamente a **mejorar el diseño**: una mejora concreta por semana, apuntada abajo.
4. Si una mejora sale bien, se sube la versión de la biblioteca (v1 → v2…) y todos los reels siguientes la heredan.

## Fases

| Fase | Qué se mejora | Estado |
|---|---|---|
| v1 (25-11-2026) | Biblioteca base: Alex, Clod, coche compacto, ruedas nuevas/gastadas, taller, carretera mojada, textos con placa | hecho |
| v2 | Cara de Alex: párpados, cejas que se mueven por clave, ojos más grandes con brillo, boca con 3 formas | pendiente |
| v3 | Materiales: piel con subsurface, tela del uniforme, goma con relieve real (normal map procedural) | pendiente |
| v4 | Cuerpo de Alex con proporciones de dibujo animado (cabeza y manos más grandes, cintura, curvas) y rig con huesos | pendiente |
| v5 | Pelo con volumen (curvas de pelo o mechones modelados) e iluminación de estudio fija (clave cálida + contra) | pendiente |
| v6 | Clod v2: pantalla con expresiones animadas (texturas), brazos con codo, rebote al andar | pendiente |
| v7 | Fondos: taller desenfocado con profundidad de campo en primeros planos, y plano de color liso para portadas | pendiente |

## Cómo se decide qué mejorar

Cada domingo, en la actualización semanal:

1. Se leen las cifras de los últimos reels (vistas, retención, comentarios) en Ootto o vidIQ.
2. Se revisa `LECCIONES.md`.
3. Se elige **una** mejora de la tabla, la que más afecte a lo que el público ve en los primeros 3 segundos y en la portada.
