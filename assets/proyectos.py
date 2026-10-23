"""Genera las tarjetas de proyecto del README (versión clara y oscura).

Cada tarjeta lleva una captura (assets/capturas/*.jpg, incrustada en el SVG), el nombre, una línea
de qué es y sus tecnologías. Para añadir un proyecto, pon su captura (800 x 330) en assets/capturas,
añádelo a PROYECTOS y ejecuta:

    python assets/proyectos.py
"""
import base64
import pathlib
from xml.sax.saxutils import escape

SALIDA = pathlib.Path(__file__).parent

# (archivo, nombre, descripción en dos líneas, tecnologías, etiqueta de estado)
PROYECTOS = [
    ('fructoscan', 'FructoScan',
     ['Escanea productos del súper y te dice si te', 'convienen con intolerancia a la fructosa.'],
     ['JavaScript', 'PWA', 'OCR', 'Tests y CI'], 'En producción'),
    ('aldea', 'La aldea',
     ['Mi portfolio jugable en pixel art: cada', 'vecino cuenta una parte de mi perfil.'],
     ['TypeScript', 'Phaser 3', 'Vite', 'Tiled'], 'Jugable'),
]

TEMAS = {
    'claro': {'tarjeta': '#ffffff', 'borde': '#d0d7de', 'titulo': '#1f2328', 'texto': '#57606a',
              'chip': '#f6f8fa', 'chip_borde': '#d0d7de', 'chip_texto': '#1f2328', 'estado': '#1a7f37', 'estado_bg': '#dafbe1'},
    'oscuro': {'tarjeta': '#161b22', 'borde': '#30363d', 'titulo': '#e6edf3', 'texto': '#9198a1',
               'chip': '#21262d', 'chip_borde': '#30363d', 'chip_texto': '#e6edf3', 'estado': '#3fb950', 'estado_bg': '#12261e'},
}
W, H, IMG_H, R = 400, 300, 165, 14
FUENTE = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"


def ancho_aprox(texto, tam):
    """Ancho aproximado para colocar las etiquetas (letra sans a ~0,56 em de media)."""
    return len(texto) * tam * 0.56


def tarjeta(archivo, nombre, lineas, tecnologias, estado, tema):
    t = TEMAS[tema]
    foto = base64.b64encode((SALIDA / 'capturas' / f'{archivo}.jpg').read_bytes()).decode()
    c = [f'<defs><clipPath id="arriba"><path d="M0 {IMG_H}V{R}Q0 0 {R} 0H{W - R}Q{W} 0 {W} {R}V{IMG_H}Z"/></clipPath></defs>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{R}" fill="{t["tarjeta"]}" stroke="{t["borde"]}"/>',
         f'<image href="data:image/jpeg;base64,{foto}" x="0" y="0" width="{W}" height="{IMG_H}" '
         f'preserveAspectRatio="xMidYMid slice" clip-path="url(#arriba)"/>',
         f'<path d="M0 {IMG_H}H{W}" stroke="{t["borde"]}"/>',
         f'<text x="20" y="{IMG_H + 34}" font-size="19" font-weight="700" fill="{t["titulo"]}">{escape(nombre)}</text>']
    ew = ancho_aprox(estado, 11) + 18
    c.append(f'<rect x="{W - 20 - ew:.0f}" y="{IMG_H + 19}" width="{ew:.0f}" height="20" rx="10" fill="{t["estado_bg"]}"/>'
             f'<text x="{W - 20 - ew / 2:.0f}" y="{IMG_H + 33}" font-size="11" font-weight="600" text-anchor="middle" '
             f'fill="{t["estado"]}">{escape(estado)}</text>')
    for i, linea in enumerate(lineas):
        c.append(f'<text x="20" y="{IMG_H + 58 + i * 19}" font-size="13.5" fill="{t["texto"]}">{escape(linea)}</text>')
    x = 20
    for tec in tecnologias:
        w = ancho_aprox(tec, 11.5) + 18
        c.append(f'<rect x="{x:.0f}" y="{H - 38}" width="{w:.0f}" height="22" rx="11" fill="{t["chip"]}" stroke="{t["chip_borde"]}"/>'
                 f'<text x="{x + w / 2:.0f}" y="{H - 23}" font-size="11.5" font-weight="600" text-anchor="middle" '
                 f'fill="{t["chip_texto"]}">{escape(tec)}</text>')
        x += w + 6
    titulo = f'{nombre}: {" ".join(lineas)} Tecnologías: {", ".join(tecnologias)}.'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{escape(titulo)}" font-family="{FUENTE}"><title>{escape(titulo)}</title>{"".join(c)}</svg>\n')


if __name__ == '__main__':
    for archivo, nombre, lineas, tecnologias, estado in PROYECTOS:
        for tema in TEMAS:
            destino = SALIDA / f'proyecto-{archivo}-{tema}.svg'
            destino.write_text(tarjeta(archivo, nombre, lineas, tecnologias, estado, tema), encoding='utf-8')
            print(destino.name, destino.stat().st_size // 1024, 'KB')
