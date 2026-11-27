# Personajes de Tripo (27-11-2026)

Damián (27-11, 16:47): "los puntos que tenemos en Tripo ... hay que gastarlos, así que haz personajes 3D que valgan la pena, que tengan más adelante un diseño, por ejemplo, el pelo que tenga movimiento, que tenga todo movimiento. Haz que solamente gasta los puntos que tenemos en Tripo".

Se gastan solo los créditos que ya tenía (no se compra nada). Cada personaje: generación HD con textura 4K, sin iluminación horneada y PBR (60), remallado a cuadriláteros de 10.000 caras (40), esqueleto automático humanoide tipo Mixamo (20). Exportado en FBX (preajuste Blender, texturas 4K, con esqueleto).

| Personaje | Qué es | Estado | En el PC (`Escritorio\EKORUEDAS_ESTUDIO_3D\biblioteca\personajes\tripo\`) |
|---|---|---|---|
| Lucía | Chica joven, coleta, plumífero amarillo | Importada; **pelo con movimiento probado** (`lucia/lucia_pelo_demo.mp4`) | `lucia\lucia_tripo.blend`, `lucia\lucia_pelo.blend` |
| Ane | Chica con melena negra larga, chupa de cuero, sudadera roja, llaves | Importada (una sola malla: el pelo va junto a la chupa negra, hay que separarlo antes de darle movimiento) | `ane\ane_tripo.blend` |
| Iker | Chaval aprendiz, pelo rizado, peto naranja y negro, llave inglesa | Importado | `iker\iker_tripo.blend` |
| Patxi | Abuelo con txapela, bigote blanco, chaqueta de punto | Importado | `patxi\patxi_tripo.blend` |
| Perro del taller | Perro mestizo pequeño, mancha en el ojo, pañuelo naranja | Generándose | — |
| Mecánica | Mujer mecánica de neumáticos, trenza larga, mono atado a la cintura | Generándose | — |

## Pelo con movimiento
- `pelo_dinamico.py`: lo que cuelga por debajo de la cabeza se reparte en mechones (agrupados alrededor de la cabeza), cada uno con una cadena de 3 huesos que nace de `mixamorig:Head`; los pesos pasan suavemente de la cabeza al mechón. Luego un muelle amortiguado (inercia, rebote, algo de gravedad) se hornea en fotogramas clave: se renderiza igual en segundo plano.
- `demo_pelo.py`: prueba de 5 s (gira la cadera, salta, niega con la cabeza). En Lucía la coleta y los mechones siguen sin romperse la malla.
- Próximo: separar el pelo en los personajes de una sola malla (Ane, Patxi, Iker) por color de textura y forma antes de ponerle los mechones; y la cola y las orejas del perro con el mismo muelle.

## Importar
`blender -b --factory-startup --python importar_tripo.py -- <zip de Tripo> <nombre> <carpeta>` → `<nombre>_tripo.blend` y `<nombre>_info.json` (huesos, mallas, alturas).
