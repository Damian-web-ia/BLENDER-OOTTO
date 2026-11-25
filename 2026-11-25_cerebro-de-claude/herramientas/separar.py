"""
Separa la página del Cerebro de Claude (un solo index.html) en una carpeta ordenada.

Uso:
    python3 separar.py <index.html de entrada> <carpeta de salida> [recuerdos.json]

- <index.html de entrada>: la página completa tal como está publicada en Claude.
- <carpeta de salida>: se crea (o se sobrescribe) con css/, js/, un-solo-archivo/ e index.html.
- [recuerdos.json] (opcional): lista de recuerdos guardados por las tareas automáticas,
  cada uno como {"id": ..., "label": ..., "type": ..., "date": "MM-DD", "desc": ..., "rel": ...}.
  Se escriben en js/datos/recuerdos-automaticos.js para que la versión descargada
  también los muestre.
"""
import json, os, re, shutil, sys

# Nombres del mapa que chocan con los del cerebro: se renombran al separar en archivos.
RENOMBRAR = {'W': 'mW', 'H': 'mH', 'S': 'mS', 'PH': 'FASES', 'aim': 'mAim', 'ctl': 'mCtl', 'cv': 'mCv',
             'dpr': 'mDpr', 'drag': 'mDrag', 'last': 'mLast', 'open': 'abrirFicha', 'pulses': 'mPulses',
             'rotX': 'mRotX', 'rotY': 'mRotY', 'seed': 'mSeed', 'sel': 'mSel', 'size': 'mSize',
             'zoom': 'mZoom', '$': '$m', 'rnd': 'mRnd'}

CEREBRO = [  # (archivo, texto con el que empieza, descripción)
    ('js/datos/recuerdos.js', None, 'Datos del cerebro: colores de cada categoría (TY), nombres (LBL), los recuerdos (R) y las frases del guion (VOZ).'),
    ('js/cerebro/forma.js', 'const N=R.map', 'Forma del cerebro: convierte los recuerdos en neuronas, calcula la forma (hemisferios, lóbulos, cerebelo), coloca cada neurona en su zona y une cada una con sus 6 vecinas.'),
    ('js/cerebro/escena.js', "const cv=document.getElementById('c')", 'Escena 3D: lienzo, brillos, cámara y proyección, hilos que ondulan como pelo, impulsos y el bucle de animación.'),
    ('js/cerebro/interaccion.js', 'function pick(', 'Interacción: tocar neuronas, ficha del recuerdo, trazar camino, ratón y dedos, línea de tiempo, buscador, leyenda y botones.'),
    ('js/cerebro/sonido.js', '/* ---------- sonido', 'Sonido: notas en cada disparo y música ambiental de fondo siempre activa.'),
    ('js/cerebro/preguntale.js', '/* ---------- paneles', 'Pregúntale: Claude responde con los recuerdos, lee en voz alta y dicta (solo funciona dentro de Claude).'),
    ('js/cerebro/recuerdos-auto.js', '/* ---------- recuerdos guardados', 'Recuerdos automáticos: lee los recuerdos que Claude guarda cada noche en la base de datos (solo dentro de Claude).'),
    ('js/cerebro/modo-reel.js', '/* ---------- modo reel', 'Modo reel, atajos de teclado y arranque del cerebro.'),
]
MAPA = [
    ('js/mapa/fases.js', None, 'Datos del mapa: las 4 fases, sus colores y sus herramientas. Aquí se cambian textos y colores del mapa.'),
    ('js/mapa/galaxia.js', '/* fondo', 'Galaxia: nebulosas y estrellas del fondo, disco con brazos espirales, y posición de Claude, las fases y las herramientas en órbita.'),
    ('js/mapa/camara-e-impulsos.js', '/* proyección', 'Cámara 3D (proyección), curvas de los hilos y creación de impulsos.'),
    ('js/mapa/interaccion.js', '/* interacción', 'Interacción: arrastrar para girar, rueda para acercar, tocar una herramienta, ficha y botones de fase.'),
    ('js/mapa/dibujo.js', '/* bucle', 'Dibujo de cada fotograma: cielo, disco, órbita y cometa, hilos tipo pelo, impulsos, estrellas y nombres sin solaparse.'),
    ('js/pestanas.js', '/* pestañas', 'Pestañas: cambia entre Cerebro y Mapa del sistema y recuerda la última que abriste.'),
]
CSS = ['base', 'cabecera', 'controles', 'paneles', 'mapa', 'movil']
CSS_TXT = {'base': 'Base: variables de color, fondo, tipografía y reglas generales.',
           'cabecera': 'Cabecera: título y contadores (recuerdos, conexiones, días).',
           'controles': 'Controles: barra de herramientas, línea de tiempo, buscador y leyenda.',
           'paneles': 'Paneles: ficha del recuerdo, Cómo funciona, Pregúntale, avisos y modo reel.',
           'mapa': 'Pestañas y todo lo de la pestaña Mapa del sistema.',
           'movil': 'Adaptación a móvil y pantallas pequeñas (va al final para mandar sobre lo anterior).'}


def renombrar(s, i=0, stop=None):
    """Renombra identificadores del mapa sin tocar textos entre comillas ni propiedades (obj.x)."""
    res = []; n = len(s)
    while i < n:
        c = s[i]
        if stop == '}' and c == '}':
            return ''.join(res), i
        if c in '\'"':
            j = i + 1
            while s[j] != c:
                j += 2 if s[j] == '\\' else 1
            res.append(s[i:j + 1]); i = j + 1; continue
        if c == '`':
            res.append('`'); i += 1
            while s[i] != '`':
                if s[i] == '\\':
                    res.append(s[i:i + 2]); i += 2; continue
                if s[i] == '$' and s[i + 1] == '{':
                    res.append('${'); sub, i = renombrar(s, i + 2, '}'); res.append(sub + '}'); i += 1; continue
                res.append(s[i]); i += 1
            res.append('`'); i += 1; continue
        if c == '/' and i + 1 < n and s[i + 1] == '*':
            j = s.index('*/', i) + 2; res.append(s[i:j]); i = j; continue
        if c == '{' and stop == '}':
            sub, i = renombrar(s, i + 1, '}'); res.append('{' + sub + '}'); i += 1; continue
        m = re.match(r'[A-Za-z_$][\w$]*', s[i:])
        if m:
            w = m.group(0); prev = s[i - 1] if i else ''
            res.append(RENOMBRAR[w] if w in RENOMBRAR and (prev != '.' or s[i - 3:i] == '...') else w)
            i += len(w); continue
        res.append(c); i += 1
    return ''.join(res), i


def trocear(lineas, partes, salida):
    inicios = []
    for f, marca, _ in partes:
        if marca is None:
            inicios.append(0); continue
        k = next((k for k, l in enumerate(lineas) if l.lstrip().startswith(marca)), None)
        if k is None:
            raise SystemExit(f'No encuentro el inicio de {f} ("{marca}"). ¿Ha cambiado el código?')
        inicios.append(k)
    if inicios != sorted(inicios):
        raise SystemExit('Las secciones no están en el orden esperado.')
    for idx, (f, _, desc) in enumerate(partes):
        a = inicios[idx]; b = inicios[idx + 1] if idx + 1 < len(partes) else len(lineas)
        with open(os.path.join(salida, f), 'w', encoding='utf-8') as fh:
            fh.write('/* ' + desc + ' */\n' + '\n'.join(lineas[a:b]).strip('\n') + '\n')


def categoria_css(linea):
    t = linea.strip()
    if t.startswith('@media'): return 'movil'
    if re.match(r'(\.tabs|#m\b|#m\{|body\.map|body:not\(\.map\)|\.mapui|\.mlegend|\.mtasks|\.mcard|\.mhint)', t): return 'mapa'
    if re.match(r'\.(brand|stats|stat)\b', t): return 'cabecera'
    if re.match(r'(\.(tools|tb|dock|pill|dot|day|results|sw|legend|hint|row|field|go)\b|textarea|input)', t): return 'controles'
    if re.match(r'(\.(card|tag|links|acts|x|path|toast|how|tip|panel|ans|sugs|err|pov|exitreel|bar|sub)\b|kbd|#c\b|canvas|h2|h3)', t): return 'paneles'
    return 'base'


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    origen, salida = sys.argv[1], sys.argv[2]
    recuerdos = json.load(open(sys.argv[3], encoding='utf-8')) if len(sys.argv) > 3 else []
    html = open(origen, encoding='utf-8').read()
    for d in ['css', 'js/datos', 'js/cerebro', 'js/mapa', 'un-solo-archivo']:
        shutil.rmtree(os.path.join(salida, d), ignore_errors=True)
        os.makedirs(os.path.join(salida, d), exist_ok=True)
    css = re.search(r'<style>(.*?)</style>', html, re.S).group(1)
    js = re.findall(r'<script>(.*?)</script>', html, re.S)
    if len(js) != 2:
        raise SystemExit(f'Esperaba 2 bloques <script> (cerebro y mapa) y hay {len(js)}.')
    # cerebro: quitar el bloque { } que lo envuelve
    b = js[0].strip(); assert b[0] == '{' and b[-1] == '}', 'El código del cerebro no empieza por {'
    trocear(b[1:-1].strip('\n').split('\n'), CEREBRO, salida)
    # mapa: quitar { }, renombrar choques y trocear
    m = js[1].strip(); assert m[0] == '{' and m[-1] == '}', 'El código del mapa no empieza por {'
    m2, _ = renombrar(m[1:-1].strip('\n'))
    trocear(m2.split('\n'), MAPA, salida)
    # recuerdos automáticos (de la base de datos de Claude)
    filas = []
    for r in recuerdos:
        filas.append(json.dumps([r.get('id'), r.get('label', ''), r.get('type', 'dato'), r.get('date', '01-01'),
                                 r.get('desc', ''), [r['rel']] if r.get('rel') else []], ensure_ascii=False))
    with open(os.path.join(salida, 'js/datos/recuerdos-automaticos.js'), 'w', encoding='utf-8') as fh:
        fh.write('/* Recuerdos añadidos solos por las tareas de cada noche (copiados de la base de datos de Claude).\n'
                 '   Se añaden a la lista R antes de construir el cerebro. */\n'
                 '[\n' + ',\n'.join(filas) + '\n].forEach(r=>{if(!R.some(x=>x[0]===r[0])&&TY[r[2]])R.push(r);});\n')
    # css
    grupos = {g: [] for g in CSS}
    for l in css.split('\n'):
        if l.strip(): grupos[categoria_css(l)].append(l)
    for g in CSS:
        with open(os.path.join(salida, f'css/{g}.css'), 'w', encoding='utf-8') as fh:
            fh.write('/* ' + CSS_TXT[g] + ' */\n' + '\n'.join(grupos[g]) + '\n')
    # index.html
    scripts = [CEREBRO[0][0], 'js/datos/recuerdos-automaticos.js'] + [p[0] for p in CEREBRO[1:]] + [p[0] for p in MAPA]
    h = html.replace('<style>' + css + '</style>', '\n'.join(f'<link rel="stylesheet" href="css/{g}.css">' for g in CSS))
    h = h.replace('<script>' + js[0] + '</script>', '\n'.join(f'<script src="{s}"></script>' for s in scripts[:9]))
    h = h.replace('<script>' + js[1] + '</script>', '\n'.join(f'<script src="{s}"></script>' for s in scripts[9:]))
    open(os.path.join(salida, 'index.html'), 'w', encoding='utf-8').write(h)
    open(os.path.join(salida, 'un-solo-archivo/index.html'), 'w', encoding='utf-8').write(html)
    print('Hecho:', len(scripts), 'archivos JS,', len(CSS), 'CSS,', len(recuerdos), 'recuerdos automáticos.')


if __name__ == '__main__':
    main()
