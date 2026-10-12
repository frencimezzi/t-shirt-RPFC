"""Genera la scritta "RUGBY PARMA 1931" in stile lettering tondo e incastrato.

Ogni lettera e' disegnata come scheletro (linee/curve) con tratto spesso,
le righe vengono composte in un quadrato e poi deformate in un cerchio
(mappatura quadrato -> disco). Le lettere che si sovrappongono vengono
separate da un sottile filo bianco, cosi' sembrano incastrate.
"""
import math
import sys
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

# ---------- curve helpers ----------
def spline(pts, n=24):
    """Catmull-Rom attraverso i punti."""
    if len(pts) < 3:
        return pts
    p = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)
                             for j in range(2)))
    out.append(pts[-1])
    return out

def arc(cx, cy, rx, ry, a0, a1, n=40):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

L = lambda *p: list(p)          # polilinea
S = lambda *p: spline(list(p))  # curva morbida

# ---------- glifi: (larghezza, [tratti]) in box alto 1, y verso il basso ----------
GLYPHS = {
    'R': (0.78, [L((0.14, 0.10), (0.13, 0.90)),
                 S((0.14, 0.12), (0.42, 0.10), (0.60, 0.26), (0.48, 0.46), (0.16, 0.52)),
                 S((0.30, 0.52), (0.46, 0.66), (0.56, 0.86), (0.70, 0.92), (0.82, 0.84))]),
    'U': (0.72, [S((0.13, 0.08), (0.12, 0.55), (0.22, 0.82), (0.38, 0.90), (0.54, 0.80),
                   (0.60, 0.55), (0.60, 0.08))]),
    'G': (0.82, [S((0.70, 0.24), (0.52, 0.11), (0.30, 0.13), (0.14, 0.35), (0.14, 0.62),
                   (0.30, 0.86), (0.54, 0.88), (0.70, 0.72), (0.70, 0.56)),
                 L((0.70, 0.56), (0.46, 0.56))]),
    'B': (0.72, [L((0.14, 0.10), (0.14, 0.90)),
                 S((0.14, 0.12), (0.44, 0.12), (0.56, 0.28), (0.44, 0.46), (0.16, 0.48)),
                 S((0.16, 0.48), (0.48, 0.50), (0.64, 0.68), (0.50, 0.88), (0.14, 0.88))]),
    'Y': (0.74, [S((0.12, 0.08), (0.12, 0.38), (0.26, 0.54), (0.46, 0.50), (0.60, 0.36)),
                 S((0.62, 0.06), (0.62, 0.60), (0.52, 0.80), (0.30, 0.84))]),
    'P': (0.72, [L((0.14, 0.10), (0.14, 0.92)),
                 S((0.14, 0.12), (0.46, 0.10), (0.62, 0.30), (0.48, 0.52), (0.16, 0.56))]),
    'A': (0.80, [L((0.08, 0.90), (0.40, 0.08), (0.72, 0.90)),
                 L((0.22, 0.62), (0.58, 0.62))]),
    'a': (0.78, [S((0.62, 0.40), (0.50, 0.26), (0.30, 0.30), (0.14, 0.55), (0.20, 0.84),
                   (0.42, 0.86), (0.60, 0.62)),
                 S((0.62, 0.28), (0.62, 0.70), (0.68, 0.88), (0.80, 0.86))]),
    'M': (1.02, [L((0.10, 0.90), (0.14, 0.10), (0.47, 0.62), (0.80, 0.10), (0.84, 0.90))]),
    '1': (0.66, [L((0.10, 0.32), (0.38, 0.08), (0.38, 0.84)),
                 S((0.10, 0.90), (0.36, 0.86), (0.60, 0.90))]),
    '9': (0.72, [arc(0.36, 0.33, 0.24, 0.23, 0, 360),
                 S((0.60, 0.30), (0.60, 0.62), (0.50, 0.84), (0.30, 0.92), (0.10, 0.84))]),
    '3': (0.72, [S((0.10, 0.18), (0.34, 0.08), (0.56, 0.16), (0.56, 0.36), (0.32, 0.48)),
                 S((0.32, 0.48), (0.60, 0.58), (0.62, 0.80), (0.40, 0.92), (0.08, 0.84))]),
}

def letter_shape(ch, x, y, sx, sy, r, rot=0.0):
    w, strokes = GLYPHS[ch]
    geoms = []
    for st in strokes:
        pts = [(x + px * sx, y + py * sy) for px, py in st]
        geoms.append(LineString(pts).buffer(r, cap_style=1, join_style=1, quad_segs=16))
    g = unary_union(geoms)
    if rot:
        g = affinity.rotate(g, rot, origin=(x + w * sx / 2, y + sy / 2))
    return g

# ---------- composizione ----------
# ogni riga: testo, y top, altezza, spaziatura (negativa = lettere che si incastrano)
ROWS = [
    # (text, top, height, tracking, per-letter (dy, scale, rot))
    ("RUGBY", -1.02, 0.70, -0.05, [(0.06, 1.00, -4), (0.0, 1.0, 2), (-0.02, 1.0, -2), (0.0, 1.0, 3), (0.04, 1.0, -3)]),
    ("PARMA", -0.32, 0.64, -0.05, [(0.02, 1.0, 3), (0.08, 0.92, -3), (0.0, 1.0, 2), (-0.02, 1.0, 0), (0.02, 1.0, 2)]),
    ("1931",   0.32, 0.70, -0.04, [(0.0, 1.0, -3), (0.0, 1.0, 3), (0.0, 1.0, -2), (0.0, 1.0, 3)]),
]
STROKE = 0.098   # raggio del tratto, relativo all'altezza della riga

def build_block():
    letters = []
    for text, top, h, track, mods in ROWS:
        ws = [GLYPHS[c][0] for c in text]
        total = sum(ws) + track * (len(text) - 1)
        sx = 2.0 / total          # la riga occupa tutta la larghezza del quadrato
        x = -1.0
        for c, w, (dy, sc, rot) in zip(text, ws, mods):
            letters.append(letter_shape(c, x, top + dy * h, sx * sc, h * sc,
                                        STROKE * h, rot))
            x += (w + track) * sx
    return letters

# ---------- deformazione quadrato -> cerchio ----------
def sq2disc(x, y, k=1.0):
    x = max(-1.2, min(1.2, x)); y = max(-1.2, min(1.2, y))
    u = x * math.sqrt(max(0.0, 1 - y * y / 2))
    v = y * math.sqrt(max(0.0, 1 - x * x / 2))
    return (x + (u - x) * k, y + (v - y) * k)

def warp(geom, k):
    geom = geom.segmentize(0.01)
    def wp(poly):
        ext = [sq2disc(x, y, k) for x, y in poly.exterior.coords]
        ints = [[sq2disc(x, y, k) for x, y in r.coords] for r in poly.interiors]
        return Polygon(ext, ints).buffer(0)
    if isinstance(geom, Polygon):
        return wp(geom)
    return unary_union([wp(p) for p in geom.geoms])

def compose(k=0.92, gap=0.028):
    shapes = [warp(g, k) for g in build_block()]
    art = Polygon()
    for s in shapes:   # le lettere successive "tagliano" quelle sotto con un filo bianco
        art = art.difference(s.buffer(gap, quad_segs=12)).union(s)
    return art

def to_svg(geom, size=1200, pad=0.08, fg="#000", bg="#fff"):
    minx, miny, maxx, maxy = geom.bounds
    span = max(maxx - minx, maxy - miny) * (1 + 2 * pad)
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    f = size / span
    T = lambda x, y: f"{(x - cx) * f + size / 2:.2f},{(y - cy) * f + size / 2:.2f}"
    polys = geom.geoms if hasattr(geom, "geoms") else [geom]
    d = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            d.append("M" + " L".join(T(x, y) for x, y in ring.coords) + "Z")
    bgrect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{size}" height="{size}">{bgrect}'
            f'<path fill="{fg}" fill-rule="evenodd" d="{" ".join(d)}"/></svg>')

if __name__ == "__main__":
    import cairosvg
    art = compose()
    for name, fg, bg in [("rugby-parma-1931", "#000", "#fff"),
                         ("rugby-parma-1931-negativo", "#fff", "#000"),
                         ("rugby-parma-1931-trasparente", "#000", None)]:
        svg = to_svg(art, fg=fg, bg=bg)
        open(f"{name}.svg", "w").write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=f"{name}.png",
                         output_width=2400, output_height=2400)
    print("ok")
