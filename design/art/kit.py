"""Pop-up book drawing kit for 小小生活家 (立體書風).

Everything is cut paper. One picture = a few LAYERS; each layer is a flat shape in a soft colour,
with the paper's thickness (the same shape, a little darker, shifted down-right) and a soft shadow
(the same shape again, dark and see-through, shifted further) under it. No filters, no masks, no
CSS: only plain paths with fill / stroke / fill-opacity, so flutter_svg draws exactly what Chromium
draws (docs/art.md).

    import kit
    c = kit.Ctx(120, 100)                      # a file whose viewBox is 0 0 120 100
    c.layer(kit.rrect(8, 20, 100, 60, 14), kit.MINT)         # thickness + shadow + top
    c.layer(kit.ellipse(60, 30, 40, 18), kit.PINK, depth=3)
    c.flat(kit.circle(60, 30, 6), kit.CREAM)                 # printed on the paper, no thickness
    c.face(60, 50, 14, "happy")                              # two dot eyes, blush, smile
    kit.write_svg(path, c.svg())                             # checks the rules, then writes

Shapes (`Shape`) are lists of path commands in the file's own units; `+` unions them (they must not
need even-odd), `.move(dx, dy)`, `.scale(s)`, `.flip(cx)` make new shapes. Sizes: a thing's file is
drawn at the SCENE's pixel scale (a 120 x 100 box is a 120 x 100 viewBox), so `depth=4` looks the
same on every piece of furniture. Everything is deterministic: `rnd(key)` is a seeded generator.
"""
import colorsys
import hashlib
import math
import pathlib
import random
import re
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ART = ROOT / "app" / "assets" / "art"
SCENES_JSON = ROOT / "app" / "assets" / "scenes"

# ---------------------------------------------------------------- palette (soft paper colours)
PINK = "#F6BCC8"
PINK_DK = "#E98FA4"
MINT = "#A9DCCB"
MINT_DK = "#79C2AC"
CREAM = "#FFF1CF"
YELLOW = "#FFD981"
SKY = "#BFE3F5"        # a real colour; the SKY PLACEHOLDER the app recolours is `SKY_TOKEN`
SKY_TOKEN = "#SKY"
LAVENDER = "#D9CBF1"
LAVENDER_DK = "#B9A4E3"
PEACH = "#FFD2B3"
PEACH_DK = "#F5AE80"
CORAL = "#F4917E"
LEAF = "#9BCB7E"
LEAF_DK = "#6FA85C"
WOOD = "#DDB07A"       # light wood (floors, frames)
WOOD_DK = "#B98656"
WOOD_DEEP = "#8E6239"
PAPER = "#FFF8EA"      # white paper
WALL = "#F8EBD2"       # the living room wall
GREY = "#CFCBD6"
DARK = "#4A3B32"       # eyes, mouths, thin lines
BLUSH = "#F7A1B0"
WHITE = "#FFFFFF"
SHADOW = "#4A3B32"     # shadows are DARK with fill-opacity
WARM = "#3A2A20"       # darkening goes towards this (paper edges look warm, not grey)


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _hex(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in (r, g, b))


def mix(a, b, t):
    """Colour a moved t (0..1) of the way to colour b."""
    return _hex(*[x + (y - x) * t for x, y in zip(_rgb(a), _rgb(b))])


def lt(c, t):
    """Lighter."""
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    """Darker and warmer (a paper edge)."""
    return mix(c, WARM, t)


def tone(c, l=1.0, s=1.0, dh=0.0):
    """Scale lightness and saturation, shift hue (0..1)."""
    h, L, S = colorsys.rgb_to_hls(*[x / 255 for x in _rgb(c)])
    r, g, b = colorsys.hls_to_rgb((h + dh) % 1, max(0, min(1, L * l)), max(0, min(1, S * s)))
    return _hex(r * 255, g * 255, b * 255)


def rnd(*key):
    """A seeded random generator: the same key always gives the same numbers."""
    h = hashlib.md5("|".join(map(str, key)).encode()).hexdigest()
    return random.Random(int(h[:12], 16))


# ---------------------------------------------------------------- numbers
def n(v):
    """A number, short: one decimal, no trailing .0, no -0."""
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    if s == "-0":
        s = "0"
    return s


# ---------------------------------------------------------------- shapes
KAPPA = 0.5522847498


class Shape:
    """Path commands: ('M', x, y) ('L', x, y) ('C', x1, y1, x2, y2, x, y) ('Z',). All shapes the kit
    makes wind clockwise on screen, so unions (`a + b`) fill with the default nonzero rule."""

    def __init__(self, cmds=None):
        self.cmds = list(cmds or [])

    def __add__(self, other):
        return Shape(self.cmds + other.cmds)

    def move(self, dx, dy):
        return self.map(lambda x, y: (x + dx, y + dy))

    def scale(self, s, cx=0.0, cy=0.0, sy=None):
        sy = s if sy is None else sy
        return self.map(lambda x, y: (cx + (x - cx) * s, cy + (y - cy) * sy))

    def flip(self, cx):
        """Mirror left-right about x = cx (winding is fixed afterwards)."""
        return self.map(lambda x, y: (2 * cx - x, y)).reverse()

    def rotate(self, deg, cx, cy):
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        return self.map(lambda x, y: (cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca))

    def map(self, f):
        out = []
        for c in self.cmds:
            if c[0] == "Z":
                out.append(c)
            else:
                pts = [f(c[i], c[i + 1]) for i in range(1, len(c), 2)]
                out.append((c[0],) + tuple(v for p in pts for v in p))
        return Shape(out)

    def reverse(self):
        """The same outline the other way round (one subpath at a time)."""
        out = []
        for sub in self.subpaths():
            pts = []   # (point, incoming control pair or None)
            cur = None
            for c in sub:
                if c[0] == "M":
                    cur = (c[1], c[2])
                    pts.append((cur, None))
                elif c[0] == "L":
                    cur = (c[1], c[2])
                    pts.append((cur, None))
                elif c[0] == "C":
                    cur = (c[5], c[6])
                    pts.append((cur, (c[1], c[2], c[3], c[4])))
            rev = pts[::-1]
            out.append(("M",) + rev[0][0])
            for i in range(1, len(rev)):
                p, _ = rev[i]
                _, ctrl = rev[i - 1]      # the control pair that led INTO rev[i-1] from rev[i]
                if ctrl is None:
                    out.append(("L",) + p)
                else:
                    out.append(("C", ctrl[2], ctrl[3], ctrl[0], ctrl[1]) + p)
            out.append(("Z",))
        return Shape(out)

    def subpaths(self):
        subs, cur = [], []
        for c in self.cmds:
            if c[0] == "M" and cur:
                subs.append(cur)
                cur = []
            cur.append(c)
        if cur:
            subs.append(cur)
        return subs

    def bbox(self):
        xs = [c[i] for c in self.cmds if c[0] != "Z" for i in range(1, len(c), 2)]
        ys = [c[i] for c in self.cmds if c[0] != "Z" for i in range(2, len(c), 2)]
        return min(xs), min(ys), max(xs), max(ys)

    def d(self, dx=0.0, dy=0.0):
        out = []
        for c in self.cmds:
            if c[0] == "Z":
                out.append("Z")
            else:
                nums = [n(c[i] + (dx if i % 2 else dy)) for i in range(1, len(c))]
                out.append(c[0] + " ".join(nums))
        return "".join(out)


def poly(points, close=True):
    """A polygon through points (any winding; it is made clockwise)."""
    pts = [tuple(p) for p in points]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:      # counter-clockwise on screen (y down) -> reverse
        pts = pts[::-1]
    cmds = [("M",) + pts[0]] + [("L",) + p for p in pts[1:]]
    if close:
        cmds.append(("Z",))
    return Shape(cmds)


def rrect(x, y, w, h, r=8.0, rtl=None, rtr=None, rbr=None, rbl=None):
    """A rounded rectangle; corner radii can differ."""
    r = min(r, w / 2, h / 2)
    a, b, c_, d = [min(v if v is not None else r, w / 2, h / 2) for v in (rtl, rtr, rbr, rbl)]
    k = KAPPA
    cmds = [("M", x + a, y), ("L", x + w - b, y)]
    if b:
        cmds.append(("C", x + w - b + b * k, y, x + w, y + b - b * k, x + w, y + b))
    cmds.append(("L", x + w, y + h - c_))
    if c_:
        cmds.append(("C", x + w, y + h - c_ + c_ * k, x + w - c_ + c_ * k, y + h, x + w - c_, y + h))
    cmds.append(("L", x + d, y + h))
    if d:
        cmds.append(("C", x + d - d * k, y + h, x, y + h - d + d * k, x, y + h - d))
    cmds.append(("L", x, y + a))
    if a:
        cmds.append(("C", x, y + a - a * k, x + a - a * k, y, x + a, y))
    cmds.append(("Z",))
    return Shape(cmds)


def rect(x, y, w, h):
    return rrect(x, y, w, h, 0)


def ellipse(cx, cy, rx, ry=None):
    ry = rx if ry is None else ry
    k = KAPPA
    return Shape([
        ("M", cx + rx, cy),
        ("C", cx + rx, cy + ry * k, cx + rx * k, cy + ry, cx, cy + ry),
        ("C", cx - rx * k, cy + ry, cx - rx, cy + ry * k, cx - rx, cy),
        ("C", cx - rx, cy - ry * k, cx - rx * k, cy - ry, cx, cy - ry),
        ("C", cx + rx * k, cy - ry, cx + rx, cy - ry * k, cx + rx, cy),
        ("Z",)])


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def smooth(points, tension=0.5):
    """A closed, smooth (Catmull-Rom) curve through points, clockwise."""
    pts = [tuple(p) for p in points]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:
        pts = pts[::-1]
    m = len(pts)
    cmds = [("M",) + pts[0]]
    for i in range(m):
        p0, p1, p2, p3 = pts[(i - 1) % m], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        cmds.append(("C",) + c1 + c2 + p2)
    cmds.append(("Z",))
    return Shape(cmds)


def blob(cx, cy, rx, ry=None, lumps=7, wobble=0.12, key="blob"):
    """A soft potato shape (a bush, a cushion, a cloud body): an ellipse with seeded bumps."""
    ry = rx if ry is None else ry
    r = rnd("blob", key, lumps)
    pts = []
    for i in range(lumps):
        a = 2 * math.pi * i / lumps
        f = 1 + r.uniform(-wobble, wobble)
        pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
    return smooth(pts, 0.9)


def cloud(cx, cy, w, h, puffs=4):
    """A cloud / bush: a flat base with round puffs on top (a union of shapes)."""
    s = rrect(cx - w / 2, cy - h * .1, w, h * .6, h * .3)
    for i in range(puffs):
        t = (i + .5) / puffs
        px = cx - w / 2 + w * t
        pr = h * (.42 if i % 2 == 0 else .34)
        s = s + circle(px, cy - h * .15 + (0 if i % 2 == 0 else h * .1), pr)
    return s


def star(cx, cy, R, r=None, points=5, rot=-90.0):
    r = R * .48 if r is None else r
    pts = []
    for i in range(points * 2):
        a = math.radians(rot + 180.0 * i / points)
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return poly(pts)


def heart(cx, cy, s):
    """A heart about s wide, centred on cx, cy."""
    w, h = s, s * .95
    x0, y0 = cx, cy - h * .3          # the notch
    return Shape([
        ("M", x0, y0),
        ("C", x0 + w * .1, y0 - h * .3, x0 + w * .5, y0 - h * .3, x0 + w * .5, y0 + h * .05),
        ("C", x0 + w * .5, y0 + h * .4, x0 + w * .15, y0 + h * .55, x0, y0 + h * .75),
        ("C", x0 - w * .15, y0 + h * .55, x0 - w * .5, y0 + h * .4, x0 - w * .5, y0 + h * .05),
        ("C", x0 - w * .5, y0 - h * .3, x0 - w * .1, y0 - h * .3, x0, y0),
        ("Z",)])


def path(points, closed=False):
    """An open polyline (for strokes) or closed polygon."""
    pts = [tuple(p) for p in points]
    cmds = [("M",) + pts[0]] + [("L",) + p for p in pts[1:]]
    if closed:
        cmds.append(("Z",))
    return Shape(cmds)


def arc(cx, cy, r, a0, a1, steps=None):
    """An open arc (degrees, clockwise on screen) made of cubic pieces, for smiles and the like."""
    span = a1 - a0
    steps = steps or max(1, int(abs(span) / 90) + 1)
    cmds = []
    for i in range(steps):
        t0 = math.radians(a0 + span * i / steps)
        t1 = math.radians(a0 + span * (i + 1) / steps)
        k = 4 / 3 * math.tan((t1 - t0) / 4)
        p0 = (cx + r * math.cos(t0), cy + r * math.sin(t0))
        p3 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
        p1 = (p0[0] - k * r * math.sin(t0), p0[1] + k * r * math.cos(t0))
        p2 = (p3[0] + k * r * math.sin(t1), p3[1] - k * r * math.cos(t1))
        if i == 0:
            cmds.append(("M",) + p0)
        cmds.append(("C",) + p1 + p2 + p3)
    return Shape(cmds)


def ring(cx, cy, r_out, r_in):
    """A ring (needs even-odd: pass rule='evenodd' to flat())."""
    return circle(cx, cy, r_out) + circle(cx, cy, r_in)


# ---------------------------------------------------------------- the SVG writer
class Ctx:
    """One SVG file being drawn. viewBox 0 0 w h; `layer` / `flat` / `stroke` / `face` add elements;
    `svg()` gives the text. `scale` (default 1) multiplies all depths and shadow offsets, for files
    drawn at a scale other than the scene's pixels (e.g. a 100 x 100 prop)."""

    def __init__(self, w, h, scale=1.0):
        self.w, self.h, self.scale = w, h, scale
        self.body = []
        self.defs = []
        self._grads = {}
        self._open = 0

    # ---- raw
    def add(self, text):
        self.body.append(text)

    def path_el(self, d, fill="none", stroke=None, sw=0.0, op=1.0, rule=None, cap="round", extra=""):
        a = [f'd="{d}"', f'fill="{fill}"']
        if rule:
            a.append(f'fill-rule="{rule}"')
        if stroke:
            a += [f'stroke="{stroke}"', f'stroke-width="{n(sw)}"', f'stroke-linecap="{cap}"', 'stroke-linejoin="round"']
        if op < 1:
            a.append(f'fill-opacity="{op:.2f}"' if fill != "none" else f'stroke-opacity="{op:.2f}"')
        if extra:
            a.append(extra)
        self.body.append("<path " + " ".join(a) + "/>")

    # ---- the pop-up pieces
    def shadow(self, shape, dx=None, dy=None, op=0.18, col=SHADOW):
        """A soft shadow under a piece of paper (dark, see-through, offset down-right)."""
        s = self.scale
        dx = 8 * s if dx is None else dx
        dy = 10 * s if dy is None else dy
        self.path_el(shape.d(dx, dy), col, op=op)

    def edge(self, shape, col, depth=4.0, dx=None, dy=None):
        """The paper's thickness: the same shape, darker, shifted down-right."""
        s = self.scale
        dx = depth * s * .75 if dx is None else dx
        dy = depth * s if dy is None else dy
        self.path_el(shape.d(dx, dy), col)

    def layer(self, shape, col, depth=5.0, shadow=True, edge_col=None, shadow_op=0.2, rule=None, op=1.0,
              highlight=False):
        """One cut-paper layer: shadow, thickness, then the top. depth in scene pixels (3-6 is right;
        0 gives a printed, flat piece). Returns the colour used for the edge."""
        edge_col = edge_col or dk(col, .32)
        if shadow:
            self.shadow(shape, op=shadow_op, dx=(depth + 4) * self.scale, dy=(depth + 6) * self.scale)
        if depth > 0:
            self.path_el(shape.d(depth * self.scale * .75, depth * self.scale), edge_col, rule=rule)
        self.path_el(shape.d(), col, op=op, rule=rule)
        if highlight:
            # a thin lighter sliver along the top-left: the light catching the paper's edge
            self.path_el(shape.d(-1.2 * self.scale, -1.2 * self.scale), lt(col, .35), op=.55, rule=rule)
            self.path_el(shape.d(), col, op=op, rule=rule)
        return edge_col

    def flat(self, shape, col, op=1.0, rule=None):
        """Printed on the paper: a flat fill with no thickness."""
        self.path_el(shape.d(), col, op=op, rule=rule)

    def stroke(self, shape, col=DARK, w=2.5, op=1.0, cap="round"):
        """An open or closed line."""
        self.path_el(shape.d(), "none", col, w * self.scale, op=op, cap=cap)

    def dots(self, points, r, col, op=1.0):
        s = Shape()
        for x, y in points:
            s = s + circle(x, y, r)
        self.flat(s, col, op)

    # ---- faces: two dot eyes, blush, a small smile
    def face(self, cx, cy, size, mood="happy", col=DARK, blush=BLUSH, eye_gap=1.0):
        """A small face for furniture and props. size = half the distance between the eyes (roughly).
        moods: happy (smile), smile (small), sleepy (closed eyes), open (o mouth), wink."""
        s = size * eye_gap
        ex = [cx - s, cx + s]
        er = size * .22
        if mood == "sleepy":
            for x in ex:
                self.stroke(arc(x, cy - er * .3, er * 1.5, 20, 160), col, er * .9)
        elif mood == "wink":
            self.flat(circle(ex[0], cy, er), col)
            self.stroke(arc(ex[1], cy - er * .3, er * 1.5, 20, 160), col, er * .9)
        else:
            for x in ex:
                self.flat(circle(x, cy, er), col)
                self.flat(circle(x + er * .35, cy - er * .35, er * .3), WHITE)
        # blush
        for x, side in ((ex[0] - size * .55, -1), (ex[1] + size * .55, 1)):
            self.flat(ellipse(x, cy + size * .35, size * .36, size * .22), blush, op=.8)
        my = cy + size * .45
        if mood == "open":
            self.flat(ellipse(cx, my + size * .1, size * .22, size * .28), col)
            self.flat(ellipse(cx, my + size * .22, size * .13, size * .1), BLUSH)
        elif mood == "smile":
            self.stroke(arc(cx, my - size * .2, size * .35, 30, 150), col, er * .8)
        else:   # happy
            self.stroke(arc(cx, my - size * .25, size * .5, 25, 155), col, er * .85)

    # ---- groups
    def begin(self, transform=None, op=None):
        a = ""
        if transform:
            a += f' transform="{transform}"'
        if op is not None:
            a += f' opacity="{op:.2f}"'
        self.body.append(f"<g{a}>")
        self._open += 1

    def end(self):
        self.body.append("</g>")
        self._open -= 1

    # ---- output
    def svg(self):
        if self._open:
            raise SystemExit("Ctx: a <g> was not closed")
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(self.w)} {n(self.h)}">'
                f'{defs}{"".join(self.body)}</svg>\n')


# ---------------------------------------------------------------- checks (docs/art.md: flutter_svg)
FORBIDDEN = ("<filter", "<mask", "<style", "style=", "class=", "<text", "<image", "<foreignObject", "<pattern",
             "mix-blend-mode", "mask=", "filter=", "vector-effect", "<symbol", "<marker", "@import", "<clipPath",
             "clip-path=")
_TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_NARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
DRAWN = {"path", "ellipse", "circle", "rect", "polygon", "polyline", "line", "use"}
MAX_KB = 70


def check_path(d):
    """ValueError unless d is path data flutter_svg reads (it drops the WHOLE picture over one bad
    path, where Chromium only skips that path)."""
    toks = _TOK.findall(d)
    if not toks or toks[0] not in "Mm":
        raise ValueError(f"path does not start with M: {d[:40]!r}")
    if len("".join(toks)) != len(re.sub(r"[\s,]", "", d)):
        raise ValueError(f"stray characters in path: {d[:60]!r}")
    i = 0
    while i < len(toks):
        cmd = toks[i]
        if not cmd.isalpha():
            raise ValueError(f"numbers without a command: {d[:60]!r}")
        i += 1
        k = _NARGS[cmd.upper()]
        j = i
        while j < len(toks) and not toks[j].isalpha():
            j += 1
        cnt = j - i
        if (k == 0 and cnt) or (k and (cnt == 0 or cnt % k)):
            raise ValueError(f"command {cmd} has {cnt} numbers: {d[:60]!r}")
        i = j


def check_svg(name, text, size=None):
    """docs/art.md's rules: no filter/mask/style/text/image/pattern/blend, every drawn element has
    fill or stroke, under 70 KB, well-formed XML ending in </svg>, viewBox 0 0 w h (= size if given),
    parseable path data. Returns the size in KB; SystemExit on a problem."""
    bad = [f for f in FORBIDDEN if f in text]
    if bad:
        raise SystemExit(f"{name}: uses {bad} (flutter_svg cannot draw these)")
    kb = len(text.encode()) / 1024
    if kb > MAX_KB:
        raise SystemExit(f"{name}: {kb:.0f} KB (keep under {MAX_KB} KB)")
    if not text.rstrip().endswith("</svg>"):
        raise SystemExit(f"{name}: does not end with </svg>")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise SystemExit(f"{name}: not well-formed XML: {e}")
    ns = "{http://www.w3.org/2000/svg}"
    if root.tag != f"{ns}svg":
        raise SystemExit(f"{name}: root is not <svg xmlns=...>")
    vb = root.get("viewBox")
    if not vb:
        raise SystemExit(f"{name}: no viewBox")
    vb = [float(v) for v in vb.split()]
    if vb[0] or vb[1]:
        raise SystemExit(f"{name}: viewBox must start at 0 0")
    if size and (abs(vb[2] - size[0]) > .01 or abs(vb[3] - size[1]) > .01):
        raise SystemExit(f"{name}: viewBox {vb[2]:g} x {vb[3]:g}, expected {size[0]:g} x {size[1]:g}")
    defs = root.find(f"{ns}defs")
    in_defs = {id(el) for el in defs.iter()} if defs is not None else set()
    for el in root.iter():
        tag = el.tag.replace(ns, "")
        d = el.get("d")
        if d is not None:
            try:
                check_path(d)
            except ValueError as e:
                raise SystemExit(f"{name}: {e}")
        if tag in DRAWN and id(el) not in in_defs and el.get("fill") is None and el.get("stroke") is None:
            raise SystemExit(f"{name}: a <{tag}> without fill/stroke")
        for a in ("fill", "stroke"):
            v = el.get(a)
            if v and v.startswith("url(#") and root.find(f".//*[@id='{v[5:-1]}']") is None:
                raise SystemExit(f"{name}: {a} points to a missing {v}")
    return kb


def viewbox_of(path):
    """(w, h) of an SVG file's viewBox."""
    vb = [float(v) for v in ET.parse(path).getroot().get("viewBox").split()]
    return vb[2], vb[3]


def write_svg(path, text, size=None):
    """Check, then write. Returns the size in KB."""
    path = pathlib.Path(path)
    name = str(path.relative_to(ROOT)) if ROOT in path.parents else str(path)
    kb = check_svg(name, text, size)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return kb
