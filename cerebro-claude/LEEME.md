# Cerebro de Claude · EKORUEDAS

Página con dos pestañas: **Cerebro** (los recuerdos en un cerebro 3D) y **Mapa del sistema** (galaxia 3D con Claude en el centro).
Sin librerías: HTML, CSS y JavaScript con Canvas 2D y Web Audio. Para verla, doble clic en `index.html`.

## Estructura

```
cerebro-claude/
├── index.html                  ← la página: solo la estructura (HTML) y los enlaces a CSS y JS
│
├── css/                        ← DISEÑO (se cargan en este orden)
│   ├── base.css                colores, fondo, tipografía
│   ├── cabecera.css            título y contadores
│   ├── controles.css           botones, línea de tiempo, buscador, leyenda
│   ├── paneles.css             ficha del recuerdo, "Cómo funciona", Pregúntale, avisos
│   ├── mapa.css                pestañas y todo lo del Mapa del sistema
│   └── movil.css               ajustes para móvil (siempre el último)
│
├── js/                         ← FUNCIONAMIENTO (se cargan en este orden)
│   ├── datos/
│   │   ├── recuerdos.js        ★ LOS DATOS: categorías, colores y los recuerdos de partida
│   │   └── recuerdos-automaticos.js  los recuerdos que Claude añade solo cada noche (se actualiza cada semana)
│   │
│   ├── cerebro/                pestaña CEREBRO
│   │   ├── forma.js            forma del cerebro y conexiones entre neuronas
│   │   ├── escena.js           cámara 3D, hilos tipo pelo, impulsos y animación
│   │   ├── interaccion.js      tocar, buscar, línea de tiempo, leyenda, botones
│   │   ├── sonido.js           música de fondo y notas de los disparos
│   │   ├── preguntale.js       Claude responde y habla (solo dentro de Claude)
│   │   ├── recuerdos-auto.js   recuerdos que se añaden solos cada noche (solo dentro de Claude)
│   │   └── modo-reel.js        modo reel, teclado y arranque
│   │
│   ├── mapa/                   pestaña MAPA DEL SISTEMA
│   │   ├── fases.js            ★ LOS DATOS DEL MAPA: fases, colores y herramientas
│   │   ├── galaxia.js          nebulosas, estrellas, disco espiral y órbitas
│   │   ├── camara-e-impulsos.js  proyección 3D, curvas de los hilos e impulsos
│   │   ├── interaccion.js      girar, acercar, tocar, ficha y botones de fase
│   │   └── dibujo.js           lo que se pinta en cada fotograma
│   │
│   └── pestanas.js             cambia entre Cerebro y Mapa
│
├── un-solo-archivo/
│   └── index.html              todo lo anterior junto en un único archivo (para compartir)
│
├── herramientas/
│   └── separar.py              convierte la página publicada en esta carpeta ordenada
│
└── descargas/
    └── cerebro-claude.zip      toda esta carpeta comprimida, lista para descargar
```

★ = los archivos que tocarás normalmente.

## Qué tocar para cambiar algo

| Quiero cambiar… | Archivo |
|---|---|
| Añadir o editar recuerdos | `js/datos/recuerdos.js` (lista `R`) |
| Colores de las categorías del cerebro | `js/datos/recuerdos.js` (objeto `TY`) |
| Fases, herramientas o textos del mapa | `js/mapa/fases.js` (lista `FASES`) |
| La música | `js/cerebro/sonido.js` (acordes en `CH`, volumen en `out.gain`) |
| Velocidad de giro | `escena.js` (cerebro) o `dibujo.js` (mapa): busca `rotY+=dt*` |
| Colores del fondo o de la interfaz | `css/base.css` (variables `--bg`, `--or`…) |
| Cómo se ve en el móvil | `css/movil.css` |

## Importante

- Los archivos de `js/` comparten variables, así que **el orden de carga en `index.html` importa**: primero los datos, luego el cerebro, luego el mapa y al final las pestañas.
- Las variables del mapa llevan `m` delante (`mW`, `mRotY`…) para no chocar con las del cerebro.
- **Pregúntale** y los **recuerdos automáticos** solo funcionan en la página publicada en Claude. Fuera, el botón se oculta solo y se ven los recuerdos de `recuerdos.js`.

## Actualización automática cada semana

Cada domingo a las 11:41 una tarea de Claude:
1. descarga la página publicada en Claude y los recuerdos automáticos de la semana;
2. la vuelve a separar en esta carpeta con `herramientas/separar.py`;
3. regenera `descargas/cerebro-claude.zip`;
4. lo sube todo a este repositorio de GitHub.

Así esta carpeta y el zip siempre tienen la última versión del cerebro y del mapa.

Para hacerlo a mano:

```
python3 herramientas/separar.py un-solo-archivo/index.html . recuerdos.json
```
