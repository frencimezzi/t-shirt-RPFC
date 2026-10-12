"""Lettering "RUGBY PARMA 1931" disegnato a mano, lettera per lettera.

Nessun font: ogni lettera e' un tratto (scheletro) disegnato direttamente
nella composizione, con spessore che varia lungo il tratto come un pennarello.
Le lettere sono dimensionate e piegate una per una per riempire il cerchio;
dove si toccano le separa un filo bianco, e il bordo esterno viene rifilato
dal cerchio, cosi' la sagoma finale e' tonda.
"""
import math
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

CX, CY, RAD = 500, 500, 470   # cerchio finale
GAP = 10                      # filo bianco tra le lettere


def spline(pts, n=30):
    """Catmull-Rom che passa per tutti i punti."""
    if len(pts) < 3:
        return [tuple(p) for p in pts]
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3)
                             for j in range(2)))
    out.append(tuple(pts[-1]))
    return out


SKELETONS = []   # (linea, larghezza) di ogni tratto, per la texture


def stroke(pts, w, w_end=None, smooth=True):
    """Tratto a pennarello: larghezza w all'inizio, w_end alla fine,
    leggermente piu' gonfio a meta'."""
    w_end = w if w_end is None else w_end
    line = spline(pts) if smooth else [tuple(p) for p in pts]
    ls = LineString(line)
    SKELETONS.append((ls, (w + w_end) / 2))
    n = max(2, int(ls.length / 4))
    samp = [ls.interpolate(i / n, normalized=True) for i in range(n + 1)]
    parts = []
    for i in range(n):
        t = (i + 0.5) / n
        r = (w + (w_end - w) * t) / 2 * (1 + 0.06 * math.sin(math.pi * t))
        parts.append(LineString([samp[i], samp[i + 1]]).buffer(r, quad_segs=10))
    return unary_union(parts)


# ---------------------------------------------------------------------------
# Le lettere, in ordine di disegno (le ultime "tagliano" le prime).
# Coordinate in un quadrato 1000x1000, cerchio di raggio 470 al centro.
# Le parti che escono dal cerchio vengono rifilate.
# ---------------------------------------------------------------------------
def letters():
    L = {}
    # --- R gigante a sinistra, curva come il bordo (la "C" di Come) ---
    L['R'] = [
        stroke([(206, 150), (124, 280), (78, 420), (80, 560), (128, 690)], 92, 84),
        stroke([(204, 160), (276, 104), (346, 128), (364, 222), (318, 312), (206, 350), (104, 352)], 82, 78),
        stroke([(222, 354), (268, 430), (300, 530), (306, 650)], 80, 68),
    ]
    # --- "ugby" che scende lungo l'arco in alto ---
    L['U'] = [stroke([(426, 30), (420, 170), (432, 262), (472, 300), (516, 262), (526, 170), (524, 30)], 64, 64)]
    L['G'] = [
        stroke([(674, 112), (640, 66), (588, 70), (558, 136), (558, 236), (586, 302), (636, 314), (672, 280), (676, 222)], 60, 60),
        stroke([(680, 218), (622, 218)], 52, 46, smooth=False),
    ]
    L['B'] = [
        stroke([(726, 110), (720, 240), (726, 368)], 58, 58),
        stroke([(724, 126), (784, 116), (814, 158), (796, 214), (736, 236)], 54, 52),
        stroke([(736, 236), (812, 252), (836, 310), (796, 362), (730, 368)], 54, 54),
    ]
    L['y'] = [
        stroke([(846, 214), (844, 290), (868, 322), (904, 312)], 50, 50),
        stroke([(922, 190), (926, 340), (898, 400), (836, 426), (774, 420)], 56, 46),
    ]
    # --- "PaRMA" al centro ---
    L['P'] = [
        stroke([(392, 380), (384, 520), (392, 664)], 62, 58),
        stroke([(388, 394), (446, 380), (480, 424), (462, 488), (400, 506)], 56, 52),
    ]
    L['a'] = [  # minuscola, piccola e bassa come la "o" di Come
        stroke([(580, 500), (556, 470), (522, 476), (504, 538), (516, 604), (550, 622), (580, 588)], 48, 48),
        stroke([(588, 470), (586, 584), (596, 636), (622, 646)], 48, 42),
    ]
    L['R2'] = [
        stroke([(652, 470), (648, 580), (652, 676)], 52, 50),
        stroke([(650, 482), (700, 466), (732, 500), (718, 552), (666, 568)], 48, 46),
        stroke([(684, 568), (708, 616), (724, 670)], 48, 44),
    ]
    L['M'] = [stroke([(764, 676), (764, 520), (772, 470), (808, 560), (846, 470), (856, 520), (858, 676)],
                     48, 48, smooth=False)]
    L['A'] = [
        stroke([(884, 680), (916, 476), (940, 474), (990, 680)], 50, 50, smooth=False),
        stroke([(902, 610), (966, 610)], 40, 40, smooth=False),
    ]
    # --- "1931" grande in basso, rifilato dal cerchio ---
    L['1a'] = [
        stroke([(166, 768), (226, 708)], 62, 66, smooth=False),
        stroke([(232, 700), (236, 820), (256, 960)], 80, 88),
    ]
    L['9'] = [
        stroke([(448, 754), (428, 702), (380, 688), (334, 716), (326, 782), (362, 824), (418, 822), (448, 778)], 68, 68),
        stroke([(456, 712), (460, 836), (436, 924), (370, 966)], 74, 70),
    ]
    L['3'] = [
        stroke([(512, 724), (558, 684), (618, 688), (646, 736), (614, 788), (572, 800)], 66, 64),
        stroke([(572, 800), (640, 818), (664, 876), (634, 936), (570, 962), (508, 946)], 64, 68),
    ]
    L['1b'] = [
        stroke([(712, 756), (774, 700)], 60, 64, smooth=False),
        stroke([(782, 692), (786, 800), (780, 920)], 76, 82),
    ]
    return L


def compose(gap=GAP):
    disc = Point(CX, CY).buffer(RAD, quad_segs=128)
    art = Polygon()
    for name, parts in letters().items():
        g = unary_union(parts)
        art = art.difference(g.buffer(gap, quad_segs=12)).union(g)
    return art.intersection(disc)


def texture(seed=1931):
    """Righe sottili lungo i tratti, come un pennarello asciutto."""
    import random
    from shapely.ops import substring
    rnd = random.Random(seed)
    lines = []
    for ls, w in SKELETONS:
        for _ in range(int(w * 0.4)):
            off = rnd.uniform(-0.45, 0.45) * w
            try:
                c = ls.offset_curve(off)
            except Exception:
                continue
            if c.is_empty or c.geom_type != "LineString" or c.length < 10:
                continue
            a = rnd.uniform(0, 0.8)
            b = min(1, a + rnd.uniform(0.05, 0.5))
            seg = substring(c, a, b, normalized=True)
            if seg.length > 4:
                lines.append((seg, rnd.uniform(0.5, 1.5), rnd.uniform(0.3, 0.85)))
    return lines


def to_svg(geom, size=1000, fg="#000", bg="#fff", pad=20, grain=False):
    polys = geom.geoms if hasattr(geom, "geoms") else [geom]
    s = size / (1000 + 2 * pad)
    T = lambda x, y: f"{(x + pad) * s:.1f},{(y + pad) * s:.1f}"
    d = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            d.append("M" + " L".join(T(x, y) for x, y in ring.coords) + "Z")
    bgrect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    shape = f'<path fill="{fg}" fill-rule="evenodd" d="{" ".join(d)}"/>'
    tex = ""
    if grain:
        hole = bg or "#fff"
        segs = "".join(
            f'<polyline points="{" ".join(T(x, y) for x, y in seg.coords)}" '
            f'stroke-width="{sw * s:.2f}" stroke-opacity="{op:.2f}"/>'
            for seg, sw, op in texture())
        tex = (f'<clipPath id="c"><path fill-rule="evenodd" d="{" ".join(d)}"/></clipPath>'
               f'<g clip-path="url(#c)" fill="none" stroke="{hole}" stroke-linecap="round">{segs}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{size}" height="{size}">{bgrect}{shape}{tex}</svg>')


if __name__ == "__main__":
    import cairosvg
    art = compose()
    for name, fg, bg, grain in [("rugby-parma-1931", "#000", "#fff", True),
                                ("rugby-parma-1931-negativo", "#fff", "#000", True),
                                ("rugby-parma-1931-pulito", "#000", "#fff", False),
                                ("rugby-parma-1931-trasparente", "#000", None, False)]:
        svg = to_svg(art, fg=fg, bg=bg, grain=grain)
        open(f"{name}.svg", "w").write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=f"{name}.png",
                         output_width=2400, output_height=2400)
    print("ok")
