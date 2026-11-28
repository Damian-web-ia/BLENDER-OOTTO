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
- 28-11 (mañana) · **Fase 2, limpieza de la cara**:
  - Halo alrededor de los ojos resuelto: no era la córnea (pruebas `diag_sin_cornea`, `diag_sin_globo`), eran (a) 65 caras que la clasificación por color había dejado con el material blanco de "ojos/dientes" y (b) el repintado por caras, que con caras de ~4 mm se ve a bloques. Ahora: esas caras pasan a piel y alrededor de ojos y boca la piel usa un **color limpio por vértice** (relleno armónico desde la piel sana) mezclado con una máscara suave; ahí se apagan también el mapa de normales y la rugosidad pintada (`piel_lisa`).
  - Prueba en **arcilla** (`MAITE_DIAG=arcilla`): el modelo de Tripo trae el párpado superior esculpido con un **pliegue del revés** (45 caras mirando hacia dentro a 10-14 mm sobre el ojo). Se relaja como membrana contra el globo (`alisar_parpados`).
  - Cejas: el detector sólo encontraba 11-13 vértices (miraba poco ancho y a poca altura); ahora las encuentra y las claves de ceja suben y bajan 5-6 mm. Sonrisa y mejillas con más recorrido.
  - Boca: centrada entre comisuras (los dientes estaban corridos 2 mm), dientes sin huecos, cierre real de labios para M/B/P (en reposo la boca de Maite está abierta con dientes).
  - Ojos: pupila negra con brillos nítidos (el globo ya no tiene especular, lo pone la córnea IOR 1,376); el borde del párpado se apoya en el globo (se quitó la banda clara de 2-3 mm); el pliegue del párpado de Tripo se relaja en el plano de la cara (estilo Tutte) y la profundidad se ajusta sobre el globo; pesos de párpado suavizados por la malla (cierra sin pliegue); pestañas de abajo sólo en la mitad de fuera; delineado sin rabito.
  - Piel: el mapa de normales de Tripo se apaga en la cara donde la textura es piel (dibujaba cejas y párpados en relieve); labios algo más rosados, rubor suave y sombra de orificios nasales en una imagen propia `MAITE_maquillaje` (pintada por posición 3D).
  - Mirada a 1 m (a 45 cm convergía y parecía bizca). Pruebas de cara con la mirada a cámara.
  - Diagnóstico: `MAITE_DIAG=arcilla` (forma) y `MAITE_DIAG=colores` (cada pieza de un color).
- 28-11 · **Fase 6 empezada** (`materiales_aaa.py`): pelo con menos pintura de Tripo, vetas finas que bajan desde la coronilla (coordenadas de reposo), brillo anisótropo; las caras de piel pintadas de pelo en el nacimiento del pelo pasan a pelo.
- 28-11 · **Arreglado un fallo gordo**: vértices de encías, lengua y saco quedaban en una esfera de 1 m (una "aleta" rosa detrás de Maite, sólo se veía en planos abiertos). Causa: bmesh reutiliza huecos al crear geometría y las referencias a BMVert no sobreviven a `subdivide_edges` ni a crear capas. Ahora las piezas se marcan en una capa de vértices y el montaje se para si alguna queda a más de 6 cm de la boca.
- 28-11 · **Fase 3 hecha** (`rig_maite.py`, prueba `prueba_rig.py`): CTRL_raiz; piernas con IK (pie inverso talón/punta/bola y propiedad `roll`), polos de rodilla; brazos FK con IK opcional (`ik_brazo_L/R`), polos de codo; hueso de giro del antebrazo (reparte la mitad del giro de la muñeca, pesos repartidos); control de dedos `MANO_dedos_L/R` (X cierra el puño, Z abre los dedos; derecha en espejo); suavizado correctivo en hombros, codos, muñecas, caderas, rodillas y tobillos; colecciones de huesos (Controles / Mecanismo / Deformación), formas y colores. Pruebas: reposo, sentadilla, paso con talón levantado, brazos arriba, puños con giro de muñeca, mano con IK delante del pecho.
  - Límite honesto: las manos de Tripo tienen pocas caras (dedos gruesos): al cerrar el puño se ven blandas. Mejorarlas exige retopología de manos.
- 28-11 · **Fase 4 (pelo) hecha en su parte principal** (`pelo_curvas.py`): ~146.000 hebras (Hair Curves, Principled Hair con melanina) tumbadas sobre la masa de pelo, desde la coronilla y a lo largo de la trenza; pegadas con "Deform Curves on Surface" (hizo falta `rest_position` en la superficie y un UV propio por casillas, porque el atlas de Tripo se solapa). Cejas con ~8.500 pelos cortos sobre la ceja pintada, que siguen a las claves de ceja. Caras "de pelo" fuera de cabeza y trenza (bordes de tirantes) pasan a cuero.
  - Pendiente de fase 4: mechones sueltos con física propia y choques de la trenza con hombro y ropa (hoy la trenza ya tiene muelles y choques con esferas).
- 28-11 · **Fase 5 (ropa) en marcha** (`ropa_maite.py`, prueba `prueba_tela.py`): mangas de la camiseta como tela (cáscara a 1,2 mm sobre el brazo, Armature → Cloth → Subsurf, pines que se aflojan hacia el puño, choque con el cuerpo); la manga original se encoge 3 mm y pasa a piel. Primer intento: las mangas se caían (masa 0,12 kg por vértice). Con 2,5 g y pines firmes, siguen a los brazos arriba, al saludo y al brazo estirado con caída natural.
- 28-11 · **Fase 8 (pruebas obligatorias) empezada** (`pruebas_maite.py`: expresiones, pelo, ropa, giro 360°, primer plano 4K). El primer plano 4K (2160×3840) sacó lo que a tamaño normal no se veía y se está corrigiendo:
  - Aro gris lila alrededor de los ojos: no era el color, era el **brillo del borde del párpado visto de canto** (Fresnel: de canto refleja como un espejo el entorno azulado). Ahora: sin barniz, brillo mínimo en la línea de agua y nada arriba; el borde de arriba es la línea de pestañas (oscura) y el de abajo rosado, con un atributo `borde_sup` calculado en reposo (sigue al parpadeo). La córnea pasa de esfera entera a **casquete sobre el iris**; la esclera brilla húmeda; sombra de contacto del párpado sobre el globo (nodos de geometría: distancia al párpado en cada fotograma).
  - Rayitas sueltas en el párpado: tiras de caras aplastadas y del revés que dejaba la relajación del párpado. Se quitan con parches de membrana (Tutte) por ojo con el borde fijo.
  - Pelos de ceja perdidos en la frente: manchas oscuras sueltas de la textura; ahora sólo crecen en las manchas grandes (la ceja).
  - Grietas claras en los labios: costuras de UV de la imagen de maquillaje; ahora la imagen sangra 8 píxeles por fuera de cada isla.
  - Piel de cera: poro fino (Voronoi de 0,55 mm en coordenadas de reposo, menos en labios), rugosidad con variación lenta, labios más brillantes y moteado de color muy leve (`piel_aaa`).
  - La primera tanda de vídeos falló al final: en Blender 5 el vídeo se elige con `media_type = 'VIDEO'` antes de `FFMPEG`. Corregido en `pruebas_maite.py` y `prueba_tela.py`.
