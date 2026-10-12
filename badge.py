"""Badge circolare "RUGBY PARMA - SINCE 1931" stile maglia da tifoso.

Testo bold condensato curvato su un cerchio, puntini ai lati, pallone ovale
al centro, finitura consumata (stampa vintage). Tutto convertito in tracciati,
quindi l'SVG si stampa senza bisogno del font.
"""
import math
import random
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely import affinity

FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
CX, CY = 500, 500


class FlatPen(BasePen):
    """Converte un glifo in poligoni (curve appiattite)."""
    def __init__(self, gs):
        super().__init__(gs)
        self.rings, self.cur = [], []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, a, b, c):
        p0 = self.cur[-1]
        for i in range(1, 13):
            t = i / 12; u = 1 - t
            self.cur.append((u**3*p0[0] + 3*u*u*t*a[0] + 3*u*t*t*b[0] + t**3*c[0],
                             u**3*p0[1] + 3*u*u*t*a[1] + 3*u*t*t*b[1] + t**3*c[1]))
    def _qCurveToOne(self, a, b):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; u = 1 - t
            self.cur.append((u*u*p0[0] + 2*u*t*a[0] + t*t*b[0], u*u*p0[1] + 2*u*t*a[1] + t*t*b[1]))
    def _closePath(self):
        if len(self.cur) > 2: self.rings.append(self.cur)
        self.cur = []
    _endPath = _closePath


font = TTFont(FONT)
GS = font.getGlyphSet()
CMAP = font.getBestCmap()
UPM = font["head"].unitsPerEm
CAP = font["OS/2"].sCapHeight


def glyph(ch):
    """(poligono del glifo in unita' font, avanzamento)"""
    name = CMAP[ord(ch)]
    pen = FlatPen(GS)
    GS[name].draw(pen)
    geom = Polygon()
    for r in pen.rings:   # regola even-odd: ogni anello inverte
        if len(r) > 2:
            geom = geom.symmetric_difference(Polygon(r).buffer(0))
    return geom, GS[name].width


def arc_text(text, cap_px, r_base, center_deg, top=True, squeeze=0.74, track=0.06):
    """Testo curvato. top=True: in alto, si legge in senso orario, base verso il centro.
    top=False: in basso, lettere dritte, testa verso il centro."""
    s = cap_px / CAP
    items, x = [], 0.0
    for i, ch in enumerate(text):
        g, adv = glyph(ch)
        items.append((g, x))
        x += adv * s * squeeze + (track * cap_px if i < len(text) - 1 else 0)
    total = x
    r_mid = r_base + (cap_px / 2 if top else -cap_px / 2)
    span = total / r_mid                       # radianti
    c = math.radians(center_deg)
    out = []
    for g, x0 in items:
        if g.is_empty:
            continue
        g = affinity.scale(g, s * squeeze, s, origin=(0, 0))
        g = affinity.translate(g, x0, 0).segmentize(4)
        def m(px, py):
            if top:
                phi = c - span / 2 + px / r_mid
                r = r_base + py
            else:
                phi = c + span / 2 - px / r_mid
                r = r_base - py
            return (CX + r * math.cos(phi), CY + r * math.sin(phi))
        polys = g.geoms if hasattr(g, "geoms") else [g]
        for p in polys:
            out.append(Polygon([m(*q) for q in p.exterior.coords],
                               [[m(*q) for q in h.coords] for h in p.interiors]).buffer(0))
    return unary_union(out)


def rugby_ball():
    """Pallone ovale inclinato, con cuciture e lacci (in negativo)."""
    ball = affinity.scale(Point(0, 0).buffer(1, quad_segs=64), 200, 124)
    cuts = []
    # cuciture dei pannelli: archi da punta a punta
    for k in (-0.52, 0.52):
        pts = [(x, k * 124 * math.sqrt(max(0, 1 - (x / 200) ** 2)) ** 0.9) for x in range(-186, 187, 4)]
        cuts.append(LineString(pts).buffer(3.2))
    # cucitura centrale con lacci
    cuts.append(LineString([(-70, 0), (70, 0)]).buffer(4.5, cap_style=1))
    for x in range(-56, 57, 22):
        cuts.append(LineString([(x, -16), (x, 16)]).buffer(4.5, cap_style=1))
    g = ball.difference(unary_union(cuts))
    g = affinity.rotate(g, -38, origin=(0, 0))
    return affinity.translate(g, CX, CY)


def wear(geom, seed=1931, n=1400):
    """Finitura consumata: tanti piccoli graffi e puntini che bucano la stampa."""
    rnd = random.Random(seed)
    minx, miny, maxx, maxy = geom.bounds
    holes = []
    for _ in range(n):
        x, y = rnd.uniform(minx, maxx), rnd.uniform(miny, maxy)
        if rnd.random() < 0.7:
            holes.append(Point(x, y).buffer(rnd.uniform(0.6, 2.4), quad_segs=4))
        else:
            a = rnd.uniform(0, math.pi)
            l = rnd.uniform(4, 16)
            holes.append(LineString([(x, y), (x + l * math.cos(a), y + l * math.sin(a))])
                         .buffer(rnd.uniform(0.4, 1.0)))
    # qualche macchia piu' grande, irregolare
    for _ in range(40):
        x, y = rnd.uniform(minx, maxx), rnd.uniform(miny, maxy)
        blob = unary_union([Point(x + rnd.gauss(0, 5), y + rnd.gauss(0, 5)).buffer(rnd.uniform(1, 3.5))
                            for _ in range(10)])
        holes.append(blob)
    return geom.difference(unary_union(holes))


def badge(worn=True):
    top = arc_text("RUGBY PARMA", 98, 318, -90, top=True, track=0.30)
    bottom = arc_text("SINCE 1931", 98, 416, 90, top=False, track=0.30)
    dots = unary_union([Point(CX + 385 * math.cos(math.radians(a)),
                              CY + 367 * math.sin(math.radians(a))).buffer(14) for a in (0, 180)])
    ring = unary_union([top, bottom, dots])
    ball = rugby_ball()
    if worn:
        ring, ball = wear(ring), wear(ball, seed=7, n=250)
    return ring, ball


def path_d(geom, f=1.0, ox=0, oy=0):
    polys = geom.geoms if hasattr(geom, "geoms") else [geom]
    d = []
    for p in polys:
        if p.is_empty:
            continue
        for ring in [p.exterior, *p.interiors]:
            d.append("M" + " L".join(f"{x * f + ox:.1f},{y * f + oy:.1f}" for x, y in ring.coords) + "Z")
    return " ".join(d)


def badge_svg(ring, ball, text_col="#fff", ball_col="#fff", bg=None):
    parts = [f'<path fill="{text_col}" fill-rule="evenodd" d="{path_d(ring)}"/>',
             f'<path fill="{ball_col}" fill-rule="evenodd" d="{path_d(ball)}"/>']
    bgrect = f'<rect width="1000" height="1000" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">'
            f'{bgrect}{"".join(parts)}</svg>')


if __name__ == "__main__":
    import cairosvg
    ring, ball = badge()
    variants = [
        ("badge-bianco", "#fff", "#fff", None),          # da stampare su maglia nera
        ("badge-bianco-anteprima", "#fff", "#fff", "#111"),
        ("badge-nero", "#000", "#000", None),            # da stampare su maglia chiara
    ]
    for name, tc, bc, bg in variants:
        svg = badge_svg(ring, ball, tc, bc, bg)
        open(f"{name}.svg", "w").write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=f"{name}.png", output_width=3000, output_height=3000)
    print("ok")
