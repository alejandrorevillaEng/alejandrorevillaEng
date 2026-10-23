"""Genera las fichas de tecnologías del README (versión clara y oscura).

Los logotipos son los oficiales de Simple Icons (CC0) y, para C#, de Devicon (MIT);
no se dibujan a mano. Para añadir o quitar una tecnología, edita GRUPOS y ejecuta:

    python assets/generar.py
"""
import json
import pathlib
import re
import urllib.request

SIMPLE_ICONS = 'https://cdn.jsdelivr.net/npm/simple-icons@13.21.0'
DEVICON = 'https://cdn.jsdelivr.net/gh/devicons/devicon@v2.16.0/icons'
SALIDA = pathlib.Path(__file__).parent

# (nombre visible, icono) · icono: slug de Simple Icons o "devicon:carpeta/archivo|#color"
GRUPOS = {
    'lenguajes': [('Python', 'python'), ('Java', 'devicon:java/java-plain|#E76F00'), ('C', 'c'), ('C#', 'devicon:csharp/csharp-plain|#9B4F96'),
                  ('TypeScript', 'typescript'), ('JavaScript', 'javascript')],
    'datos': [('Oracle SQL', 'oracle'), ('PostgreSQL', 'postgresql'), ('MySQL', 'mysql')],
    'sistemas': [('Linux', 'linux'), ('Cisco', 'cisco'), ('Git', 'git'), ('GitHub', 'github'), ('Docker', 'docker'),
                 ('Claude', 'claude')],
}

TEMAS = {
    'claro': {'ficha': '#ffffff', 'borde': '#d0d7de', 'texto': '#57606a', 'tinta': '#1f2328'},
    'oscuro': {'ficha': '#161b22', 'borde': '#30363d', 'texto': '#9198a1', 'tinta': '#e6edf3'},
}

LADO, RADIO, LOGO, HUECO, ALTO_TEXTO = 56, 14, 28, 18, 24
FUENTE = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"


def bajar(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return r.read().decode('utf-8')


def luminancia(hex_color):
    c = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def slug(titulo):
    """Igual que titleToSlug de Simple Icons para los nombres que se usan aquí."""
    t = titulo.lower().replace('+', 'plus').replace('.', 'dot').replace('&', 'and')
    return re.sub(r'[^a-z0-9]', '', t)


COLORES = {i.get('slug') or slug(i['title']): '#' + i['hex']
           for i in json.loads(bajar(f'{SIMPLE_ICONS}/_data/simple-icons.json'))['icons']}


def icono(ref):
    """Devuelve (trazados, viewBox, color de marca)."""
    if ref.startswith('devicon:'):
        ruta, color = ref[len('devicon:'):].split('|')
        svg = bajar(f'{DEVICON}/{ruta}.svg')
        caja = re.search(r'viewBox="([^"]+)"', svg).group(1)
        return re.findall(r' d="([^"]+)"', svg), caja, color
    svg = bajar(f'{SIMPLE_ICONS}/icons/{ref}.svg')
    return re.findall(r' d="([^"]+)"', svg), '0 0 24 24', COLORES[ref]


def fila(items, tema):
    t = TEMAS[tema]
    ancho = len(items) * LADO + (len(items) - 1) * HUECO + 4
    partes = []
    for n, (nombre, ref) in enumerate(items):
        trazados, caja, color = icono(ref)
        if contraste(color, t['ficha']) < 2.2:        # logos negros en oscuro o claros en claro
            color = t['tinta']
        _, _, w, _ = (float(v) for v in caja.split())
        x = 2 + n * (LADO + HUECO)
        escala = LOGO / w
        off = (LADO - LOGO) / 2
        dibujo = ''.join(f'<path d="{d}"/>' for d in trazados)
        partes.append(
            f'<g transform="translate({x} 2)">'
            f'<rect width="{LADO}" height="{LADO}" rx="{RADIO}" fill="{t["ficha"]}" stroke="{t["borde"]}"/>'
            f'<g transform="translate({off} {off}) scale({escala:.4f})" fill="{color}">{dibujo}</g>'
            f'<text x="{LADO / 2}" y="{LADO + 18}" text-anchor="middle" fill="{t["texto"]}">{nombre}</text></g>')
    alto = LADO + ALTO_TEXTO + 4
    titulo = ', '.join(n for n, _ in items)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" '
            f'role="img" aria-label="{titulo}" font-family="{FUENTE}" font-size="11.5" font-weight="600">'
            f'<title>{titulo}</title>{"".join(partes)}</svg>\n')


if __name__ == '__main__':
    for grupo, items in GRUPOS.items():
        for tema in TEMAS:
            (SALIDA / f'{grupo}-{tema}.svg').write_text(fila(items, tema), encoding='utf-8')
            print(f'{grupo}-{tema}.svg')
