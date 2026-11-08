"""Design-stage sketches for 「小小生活家」 (a daily-routine game for 2-5 year olds).

    python3 make_mockups.py          # writes docs/mockups/*.png (needs Node.js + Playwright, and shapely)
    python3 make_mockups.py 4        # only one page: 0 = style page, 1..9 = a screen, c = contact sheet

Every picture is drawn here as SVG by code (no outside pictures, no emoji). render.js turns each page
into a PNG with Playwright's Chromium. shapely (pip install shapely) does the shape maths. The font is
jf open-huninn from a sibling app's checkout.

    0_畫風選擇.png     the same living room (the picture clock, the child and the puppy, a sofa, the toy
                       box, a window with the morning sun) in three styles:
                       A 木頭玩具屋風, B 立體書風, C 色鉛筆塗畫風
    1_取名選角色.png   first launch: the name box, hair / skin / shirt / buddy choices, the doll updates
    2_客廳和時鐘.png   the home: the dollhouse with five rooms, the clock says 刷牙, footprints to the bathroom
    3_調時間.png       the clock enlarged: a finger drags the hand from 牙刷 to 碗
    4_刷牙.png         bathroom mini-game: brushing the big open mouth, bubbles as progress
    5_想上廁所.png     the random need: the child squirms, a water drop, the way to the toilet lights up
    6_吃飯.png         kitchen: a plate with four slots, foods to drag in, the puppy's own bowl
    7_睡覺.png         bedroom at night: the blanket is pulled up, the rest of the house is dark
    8_貼紙表.png       the good-habits sticker chart and the puppy's reward
    9_家長模式.png     parents' settings
    contact_sheet.png  screens 1-9 small, with titles

Style A 「木頭玩具屋風」 (screens 1-9) is a wooden dollhouse. Every piece goes through one SVG filter
(wood_f): fractal noise stretched along the grain darkens and lightens the paint in streaks, a blurred
copy of the piece's own shape is lit from the top left so the edges look rounded like sanded blocks,
and the piece throws a soft shadow. Natural wood (the house frame, floors, the clock face) shows a lot
of grain; painted pieces show only a little through a thin coat of paint. The child is a wooden peg
doll with painted hair and clothes; the buddy is a little block animal.
Style B 「立體書風」: flat paper cut-outs with a visible paper edge and a cast shadow, standing on the
two tilted pages of an open book. Style C 「色鉛筆塗畫風」: coloured-pencil hatching on textured paper,
wobbly double outlines, soft edges.
"""
import hashlib
import math
import pathlib
import subprocess
import sys
import tempfile

from shapely.geometry import LineString, Polygon
from shapely.geometry import box as sbox
from shapely.ops import unary_union

HERE = pathlib.Path(__file__).resolve().parent
FONT = None
for _c in ("app_kids_falsecharge", "app_kids_maze", "app_kids_brainstorming", "app_kids_paint_for_learning_writing", "app_kids_card_game", "app_kids_cook"):
    _p = HERE.parents[2] / _c / "app" / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"
    if _p.exists():
        FONT = _p
        break
SCRATCH = pathlib.Path("/dev/shm") if pathlib.Path("/dev/shm").is_dir() else pathlib.Path(tempfile.gettempdir())
W, H = 390, 844

# ---------------------------------------------------------------- colours (style A: wood and paint)
INK = "#4A3728"          # words: dark walnut
SOFT = "#9A826E"
WOOD = "#E9C79A"         # light beech
WOOD2 = "#D9AF7A"        # a bit darker beech
WALNUT = "#8E5E3C"
PLY = "#F4E1BE"          # the clock face
RED = "#E8695A"
YEL = "#F7C748"
ORA = "#F49A3C"
TEAL = "#5BB5A2"
BLUE = "#6FA8DC"
NAVY = "#5F7FB8"
GRN = "#86C06A"
PINK = "#F08FAE"
LILAC = "#B59CD9"
CREAM = "#FFF4DC"
WHITE = "#FBF7F0"
SKY = "#BFE3F5"
GREY = "#C9C2B8"
DARK = "#3B2A26"
CHEEK = "#F5A3A3"
SKINS = ["#F6D4B8", "#EBBB92", "#C98F5E", "#8E5A3A"]
HAIRS = ["#3B2A26", "#7A4A2E", "#E8B33E", "#B3573A"]
SHIRTS = [RED, YEL, GRN, BLUE, PINK, LILAC]
ROOM_WALL = {"bed": "#E9DFF6", "bath": "#D8EEF6", "living": "#FFF0CC", "kitchen": "#DDEFD8", "door": "#FBE2CF"}


# ---------------------------------------------------------------- defs registry
class Defs:
    def __init__(self):
        self.d = {}

    def add(self, key, svg):
        self.d.setdefault(key, svg)
        return key

    def svg(self):
        return "<defs>" + "".join(self.d.values()) + "</defs>"


D = Defs()


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:10]


def _stops(stops):
    return "".join(f'<stop offset="{s[0]}" stop-color="{s[1]}"' + (f' stop-opacity="{s[2]}"' if len(s) > 2 else "") + "/>" for s in stops)


def lg(stops, x1=0, y1=0, x2=0, y2=1, user=False):
    k = "lg" + _h(stops, x1, y1, x2, y2, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    D.add(k, f'<linearGradient id="{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{_stops(stops)}</linearGradient>')
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5, user=False):
    k = "rg" + _h(stops, cx, cy, r, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    D.add(k, f'<radialGradient id="{k}" cx="{cx}" cy="{cy}" r="{r}"{u}>{_stops(stops)}</radialGradient>')
    return f"url(#{k})"


def clip(d):
    k = "cp" + _h(d)
    D.add(k, f'<clipPath id="{k}"><path d="{d}"/></clipPath>')
    return f"url(#{k})"


def blur(sd):
    k = "bl" + str(sd).replace(".", "_")
    D.add(k, f'<filter id="{k}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return f"url(#{k})"


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mixc(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join(f"{round(ra[i] + (rb[i] - ra[i]) * t):02X}" for i in range(3))


def darker(c, t=.25):
    return mixc(c, "#000000", t)


def lighter(c, t=.35):
    return mixc(c, "#FFFFFF", t)


# ================================================================ GEOMETRY
def ellp(cx, cy, rx, ry=None, n=48, rot=0.0):
    ry = rx if ry is None else ry
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def crs(ctrl, n=10, closed=True):
    """Catmull-Rom spline through the control points, as a dense point list."""
    m = len(ctrl)
    out = []
    segs = m if closed else m - 1
    for i in range(segs):
        p0 = ctrl[(i - 1) % m] if closed else ctrl[max(i - 1, 0)]
        p1, p2 = ctrl[i], ctrl[(i + 1) % m]
        p3 = ctrl[(i + 2) % m] if closed else ctrl[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                   + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(tuple(ctrl[-1]))
    return out


def rrect(x, y, w, h, r, n=8):
    r = min(r, w / 2, h / 2)
    out = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def star_pts(R, r, cx=0.0, cy=0.0, n=5, rot=-90.0):
    out = []
    for i in range(2 * n):
        a = math.radians(rot + 180 * i / n)
        rr_ = R if i % 2 == 0 else r
        out.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)))
    return out


def soft(g, r):
    """Round the corners of a shape (convex ones, then concave ones)."""
    return g.buffer(-r, join_style=1).buffer(2 * r, join_style=1).buffer(-r, join_style=1)


def star_g(R, cx=0.0, cy=0.0, rot=-90.0, ratio=.5):
    return soft(Polygon(star_pts(R, R * ratio, cx, cy, 5, rot)), R * .12)


def heart_pts(cx, cy, s):
    out = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        out.append((cx + x * s / 16, cy + y * s / 16))
    return out


def tf(pts, dx=0.0, dy=0.0, rot=0.0, s=1.0, sx=None):
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    sx = s if sx is None else sx
    return [(x * sx * ca - y * s * sa + dx, x * sx * sa + y * s * ca + dy) for x, y in pts]


def G(x):
    if isinstance(x, (list, tuple)):
        return Polygon(x).buffer(0)
    return x


def dpts(pts, closed=True):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + ("Z" if closed else "")


def dgeom(g):
    polys = list(g.geoms) if hasattr(g, "geoms") else [g]
    out = []
    for p in polys:
        if p.is_empty or p.geom_type != "Polygon":
            continue
        for ring in (p.exterior, *p.interiors):
            out.append(dpts(list(ring.coords)[:-1]))
    return "".join(out)


def P(*a):
    return Polygon(a[0]) if len(a) == 1 else Polygon(a)


def R(x, y, w, h, r=4):
    return Polygon(rrect(x, y, w, h, r))


def E(cx, cy, rx, ry=None, rot=0.0):
    return Polygon(ellp(cx, cy, rx, ry, rot=rot))


def U(*gs):
    return unary_union([G(g) for g in gs])


# ================================================================ STYLE A: WOOD KIT
K = 1.0   # screen pixels per drawing unit of whatever is being drawn now (place() keeps it right)


def place(x, y, s, fn, *a, rot=0.0, **kw):
    """Draw fn(*a, **kw) moved to (x, y) and scaled by s; K follows so the grain and shadows keep their size."""
    global K
    old = K
    K = old * s
    try:
        inner = fn(*a, **kw)
    finally:
        K = old
    r = f" rotate({rot:.1f})" if rot else ""
    return f'<g transform="translate({x:.1f} {y:.1f}){r} scale({s:.4f})">{inner}</g>'


def wood_f(grain=.2, sh=1, m=.25, vert=False, bevel=1.0):
    """The wood filter at the current scale. grain: how much the streaks show (0 = none, .5 = raw wood).
    sh: 0 = no shadow, 1 = resting on the surface, 2 = lifted (buttons, cards), 3 = big page."""
    k = round(K, 3)
    key = "wd" + _h(k, grain, sh, m, vert, bevel)
    dy, sd, op = {0: (0, 0, 0), 1: (1.6, 1.4, .35), 2: (3.4, 3.4, .3), 3: (5, 6, .24)}[sh]
    fx, fy = (.28 * k, .012 * k) if vert else (.012 * k, .28 * k)
    shadow = ""
    merge = '<feMergeNode in="top"/>'
    if sh:
        shadow = (f'<feGaussianBlur in="SourceAlpha" stdDeviation="{sd / k:.3f}" result="sb"/>'
                  f'<feOffset in="sb" dx="{dy * .35 / k:.3f}" dy="{dy / k:.3f}" result="so"/>'
                  f'<feColorMatrix in="so" type="matrix" values="0 0 0 0 0.25  0 0 0 0 0.14  0 0 0 0 0.06  0 0 0 {op} 0" result="sh"/>')
        merge = '<feMergeNode in="sh"/>' + merge
    g1, g2 = grain, 1 - grain / 2
    D.add(key, f'<filter id="{key}" x="{-m}" y="{-m}" width="{1 + 2 * m}" height="{1 + 2.4 * m}" color-interpolation-filters="sRGB">'
               f'<feTurbulence type="fractalNoise" baseFrequency="{fx:.4f} {fy:.4f}" numOctaves="3" seed="7" result="n"/>'
               f'<feColorMatrix in="n" type="matrix" values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1" result="ng"/>'
               f'<feComposite in="SourceGraphic" in2="ng" operator="arithmetic" k1="{g1:.3f}" k2="{g2:.3f}" result="mot"/>'
               f'<feGaussianBlur in="SourceAlpha" stdDeviation="{2.4 * bevel / k:.3f}" result="ba"/>'
               f'<feDiffuseLighting in="ba" surfaceScale="{4.5 * bevel / k:.3f}" diffuseConstant="1" lighting-color="#ffffff" result="l">'
               f'<feDistantLight azimuth="235" elevation="58"/></feDiffuseLighting>'
               f'<feComposite in="mot" in2="l" operator="arithmetic" k1="0.86" k2="0.27" result="lit"/>'
               f'<feComposite in="lit" in2="SourceGraphic" operator="in" result="top"/>'
               f'{shadow}<feMerge>{merge}</feMerge></filter>')
    return f"url(#{key})"


def _margin(g):
    x0, y0, x1, y1 = g.bounds
    s = max(1e-3, min(x1 - x0, y1 - y0) * K)
    need = 10 / s
    for m in (.06, .12, .25, .5, 1.0, 2.0):
        if need <= m:
            return m
    return 3.0


def wood_piece(shape, col=WOOD, grain=.42, sh=1, vert=False, bevel=1.0, extra=""):
    """One wooden piece (natural wood by default: lots of grain)."""
    g = G(shape)
    if g.is_empty:
        return ""
    return f'<path d="{dgeom(g.simplify(.08 / K))}" fill="{col}" fill-rule="evenodd" filter="{wood_f(grain, sh, _margin(g), vert, bevel)}"{extra}/>'


def paint_wood(shape, col, sh=1, vert=False, bevel=1.0, grain=.13, extra=""):
    """A wooden piece under a thin coat of paint (just a little grain shows)."""
    return wood_piece(shape, col, grain, sh, vert, bevel, extra)


def flat_wood(shape, col, extra=""):
    """Painted-on detail (no body of its own): eyes, stripes, dots."""
    g = G(shape)
    return f'<path d="{dgeom(g)}" fill="{col}" fill-rule="evenodd"{extra}/>'


def stroke_wood(d, col, w, dash=None, op=1.0, cap="round"):
    k = K
    da = f' stroke-dasharray="{dash[0] / k:.2f} {dash[1] / k:.2f}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="{w / k:.2f}" stroke-linecap="{cap}" stroke-linejoin="round"{da}/>'


# ---------------------------------------------------------------- the other two styles, and the switch between them
STYLE = "wood"      # "wood" (A), "paper" (B) or "pencil" (C): what paint(), wood(), flat() and stroke() draw


def paper_f():
    k = round(K, 3)
    key = "pp" + _h(k)
    D.add(key, f'<filter id="{key}" x="-.1" y="-.1" width="1.2" height="1.2" color-interpolation-filters="sRGB">'
               f'<feTurbulence type="fractalNoise" baseFrequency="{.9 * k:.3f}" numOctaves="2" seed="5" result="n"/>'
               f'<feColorMatrix in="n" type="matrix" values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1" result="ng"/>'
               f'<feComposite in="SourceGraphic" in2="ng" operator="arithmetic" k1="0.16" k2="0.92" result="m"/>'
               f'<feComposite in="m" in2="SourceGraphic" operator="in"/></filter>')
    return f"url(#{key})"


def paper(shape, col, sh=1, extra=""):
    """A paper cut-out: a cast shadow, the paper's thickness (a darker copy just below), the fine paper surface."""
    g = G(shape)
    if g.is_empty:
        return ""
    d = dgeom(g.simplify(.08 / K))
    k = K
    o = ""
    if sh:
        dy = {1: 5, 2: 9, 3: 14}.get(sh, 5)
        o += f'<path d="{d}" fill="#3A2A22" fill-rule="evenodd" opacity=".3" transform="translate({dy * .45 / k:.2f} {dy / k:.2f})" filter="{blur(round(dy * .45 / k, 2))}"/>'
    o += f'<path d="{d}" fill="{darker(col, .32)}" fill-rule="evenodd" transform="translate(0 {2.6 / k:.2f})"/>'
    o += f'<path d="{d}" fill="{col}" fill-rule="evenodd" filter="{paper_f()}"{extra}/>'
    return o


def rough_f(scale=2.4):
    k = round(K, 3)
    key = "rf" + _h(k, scale)
    D.add(key, f'<filter id="{key}" x="-.2" y="-.2" width="1.4" height="1.4">'
               f'<feTurbulence type="fractalNoise" baseFrequency="{.045 * k:.4f}" numOctaves="2" seed="3" result="n"/>'
               f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{scale / k:.3f}" xChannelSelector="R" yChannelSelector="G"/></filter>')
    return f"url(#{key})"


def hatch(col, ang=38, gap=5.2):
    k = round(K, 3)
    key = "ht" + _h(col, ang, gap, k)
    g = gap / k
    D.add(key, f'<pattern id="{key}" width="{g:.3f}" height="{g * 3:.3f}" patternUnits="userSpaceOnUse" patternTransform="rotate({ang})">'
               f'<path d="M{g * .3:.3f},0 V{g * 3:.3f}" stroke="{col}" stroke-width="{1.7 / k:.3f}" stroke-opacity=".85" stroke-linecap="round"/>'
               f'<path d="M{g * .78:.3f},{g * .4:.3f} V{g * 2.6:.3f}" stroke="{col}" stroke-width="{1.0 / k:.3f}" stroke-opacity=".55" stroke-linecap="round"/></pattern>')
    return f"url(#{key})"


def pencil(shape, col, outline=True, extra=""):
    """Coloured pencil: a light base, hatched strokes over it, a wobbly double outline."""
    g = G(shape)
    if g.is_empty:
        return ""
    d = dgeom(g.simplify(.1 / K))
    k = K
    pc = darker(col, .18)
    o = f'<g filter="{rough_f()}"{extra}>'
    o += f'<path d="{d}" fill="{col}" fill-rule="evenodd" opacity=".42"/>'
    o += f'<path d="{d}" fill="{hatch(pc)}" fill-rule="evenodd"/>'
    o += f'<path d="{d}" fill="{hatch(pc, 128, 7.5)}" fill-rule="evenodd" opacity=".45"/>'
    if outline:
        oc = darker(col, .5)
        o += f'<path d="{d}" fill="none" stroke="{oc}" stroke-width="{1.5 / k:.2f}" stroke-linejoin="round" opacity=".85"/>'
        o += f'<path d="{d}" fill="none" stroke="{oc}" stroke-width="{.9 / k:.2f}" stroke-linejoin="round" opacity=".45" transform="translate({1.4 / k:.2f} {-1.1 / k:.2f})"/>'
    return o + "</g>"


def wood(shape, col=WOOD, grain=.42, sh=1, vert=False, bevel=1.0, extra=""):
    if STYLE == "paper":
        return paper(shape, col, sh, extra)
    if STYLE == "pencil":
        return pencil(shape, col, True, extra)
    return wood_piece(shape, col, grain, sh, vert, bevel, extra)


def paint(shape, col, sh=1, vert=False, bevel=1.0, grain=.13, extra=""):
    if STYLE == "paper":
        return paper(shape, col, sh, extra)
    if STYLE == "pencil":
        return pencil(shape, col, True, extra)
    return paint_wood(shape, col, sh, vert, bevel, grain, extra)


def flat(shape, col, extra=""):
    if STYLE == "pencil":
        return pencil(shape, col, False, extra)
    if STYLE == "paper":
        g = G(shape)
        return f'<path d="{dgeom(g)}" fill="{col}" fill-rule="evenodd" filter="{paper_f()}"{extra}/>'
    return flat_wood(shape, col, extra)


def stroke(d, col, w, dash=None, op=1.0, cap="round"):
    if STYLE == "pencil":
        k = K
        da = f' stroke-dasharray="{dash[0] / k:.2f} {dash[1] / k:.2f}"' if dash else ""
        return (f'<g filter="{rough_f(1.6)}"><path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op * .9:.2f}" stroke-width="{w / k:.2f}" stroke-linecap="{cap}" stroke-linejoin="round"{da}/>'
                f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op * .4:.2f}" stroke-width="{w * .6 / k:.2f}" stroke-linecap="{cap}" stroke-linejoin="round"{da} transform="translate({1.2 / k:.2f} {.9 / k:.2f})"/></g>')
    return stroke_wood(d, col, w, dash, op, cap)


def eye(cx, cy, r, glint=True):
    o = f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{DARK}"/>'
    if glint:
        o += f'<circle cx="{cx + r * .3:.2f}" cy="{cy - r * .32:.2f}" r="{r * .3:.2f}" fill="#FFFFFF"/>'
    return o


def happy_eye(cx, cy, r):
    return stroke(f"M{cx - r:.2f},{cy + r * .3:.2f} Q{cx:.2f},{cy - r * 1.1:.2f} {cx + r:.2f},{cy + r * .3:.2f}", DARK, 2.2)


def smile(cx, cy, w, open_=False):
    if open_:
        d = f"M{cx - w:.2f},{cy:.2f} Q{cx:.2f},{cy + w * 1.6:.2f} {cx + w:.2f},{cy:.2f}Z"
        return f'<path d="{d}" fill="#B5414F"/>'
    return stroke(f"M{cx - w:.2f},{cy:.2f} Q{cx:.2f},{cy + w:.2f} {cx + w:.2f},{cy:.2f}", DARK, 1.8)


def cheeks(cx, cy, dx, r):
    return f'<circle cx="{cx - dx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{CHEEK}" opacity=".7"/><circle cx="{cx + dx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{CHEEK}" opacity=".7"/>'


# ================================================================ CHARACTERS (drawn round (0, 0) = between the feet, about 100 units tall)
def peg_doll(hair=0, skin=0, shirt=0, mood="smile", arms=None, hold="", squirm=False, lying=False, open_mouth=False):
    """The child as a wooden peg doll. hair / skin / shirt pick from the lists; arms: None = painted on,
    'up' = both lifted, 'brush' = the right one lifted; hold = extra svg drawn in the right hand."""
    hc, sc, tc = HAIRS[hair % 4], SKINS[skin % 4], SHIRTS[shirt % 6]
    o = []
    rot = 8 if squirm else 0
    body = P(crs([(-14, -58), (14, -58), (19, -30), (21, -4), (16, 0), (-16, 0), (-21, -4), (-19, -30)], 8))
    o.append(paint(body, tc))
    o.append(flat(body.intersection(sbox(-30, -17, 30, 10)), NAVY))           # painted trousers
    o.append(flat(body.intersection(sbox(-30, -4, 30, 10)), WALNUT))           # painted shoes
    o.append(flat(E(0, -16, 8, 2.4), darker(NAVY, .2)))
    o.append(stroke("M-7,-54 Q0,-47 7,-54", lighter(tc, .6), 2.2))             # collar
    if arms is None:
        for sgn in (-1, 1):
            o.append(flat(E(sgn * 16, -40, 5, 11, rot=sgn * 10).intersection(body.buffer(1)), darker(tc, .12)))
    else:
        for sgn in (-1, 1):
            up = (arms == "up") or (arms == "brush" and sgn == 1)
            a = -55 if up else 20
            hx, hy = sgn * 24 + sgn * 10 * math.cos(math.radians(a)) * 1.1, -46 + 16 * math.sin(math.radians(a))
            arm = LineString([(sgn * 17, -48), (hx, hy)]).buffer(5, cap_style=1)
            o.append(paint(arm, tc))
            o.append(paint(E(hx, hy, 5.5), sc))
            if sgn == 1 and hold:
                o.append(f'<g transform="translate({hx:.1f} {hy:.1f})">{hold}</g>')
    o.append(f'<g transform="rotate({rot} 0 -58)">')
    o.append(paint(E(0, -78, 21, 22), sc, bevel=1.3))
    cap = E(0, -80, 23, 23).intersection(sbox(-40, -120, 40, -88))
    bangs = U(E(-12, -91, 9, 6), E(0, -93, 10, 6), E(12, -91, 9, 6)).intersection(sbox(-40, -120, 40, -84))
    style = hair % 4
    if style == 1:      # short with a bun / tuft
        cap = U(cap, E(0, -103, 7, 6))
    elif style == 2:    # bob: comes down the sides
        cap = U(cap, E(-19, -74, 6, 13), E(19, -74, 6, 13))
    elif style == 3:    # pigtails
        cap = U(cap, E(-24, -70, 7, 9), E(24, -70, 7, 9))
    o.append(paint(U(cap, bangs), hc, grain=.1, bevel=.8))
    if style == 3:
        o.append(flat(E(-24, -79, 4, 2.5), YEL) + flat(E(24, -79, 4, 2.5), YEL))
    if open_mouth:
        o.append(eye(-8, -80, 2.8) + eye(8, -80, 2.8))
    elif mood == "happy":
        o.append(happy_eye(-8, -80, 3.2) + happy_eye(8, -80, 3.2))
    elif mood == "sleep":
        o.append(stroke("M-11,-80 Q-8,-77 -5,-80 M5,-80 Q8,-77 11,-80", DARK, 2))
    elif mood == "worry":
        o.append(eye(-8, -80, 2.8) + eye(8, -80, 2.8))
        o.append(stroke("M-13,-88 L-5,-86 M13,-88 L5,-86", DARK, 1.6))
    else:
        o.append(eye(-8, -80, 2.8) + eye(8, -80, 2.8))
    o.append(cheeks(0, -72, 12, 3.4))
    if open_mouth:
        o.append(flat(E(0, -66, 8, 6), "#B5414F"))
        o.append(flat(E(0, -63, 7, 3), "#E8707F"))
    elif mood == "worry":
        o.append(stroke("M-4,-67 Q0,-70 4,-67", DARK, 1.8))
    elif mood == "sleep":
        o.append(stroke("M-3,-67 Q0,-65 3,-67", DARK, 1.6))
    else:
        o.append(smile(0, -69, 4.5, open_=mood == "happy"))
    o.append("</g>")
    return "".join(o)


def puppy(mood="smile", face=-1, sleep=False, hold=""):
    """The block-wood puppy, facing left (face=-1) or right. Feet at y = 0."""
    f = face
    o = []
    if sleep:
        o.append(paint(R(-22, -20, 44, 20, 9), "#F2DCB6"))
        o.append(paint(E(-22 * f * -1 if False else 20 * f, -16, 14, 12), "#F2DCB6", bevel=1.2))
        o.append(paint(E(20 * f + 10 * f, -14, 6, 8, rot=20 * f), "#C98F5E"))
        o.append(flat(E(20 * f + 5 * f, -12, 6, 4.5), "#FBEFDD"))
        o.append(flat(E(20 * f + 8 * f, -13, 2.2, 1.8), DARK))
        o.append(stroke(f"M{20 * f - 5},-19 Q{20 * f - 2},-17 {20 * f + 1},-19", DARK, 1.6))
        o.append(flat(E(-18, -24, 6, 4, rot=-10), "#D9AF7A"))
        return "".join(o)
    for lx in (-14, 8):
        o.append(paint(R(lx, -12, 10, 12, 4), "#E9CFA6"))
    o.append(paint(E(26 * -f, -26, 5, 9, rot=35 * f), "#E9CFA6"))        # tail
    o.append(paint(R(-22, -32, 44, 24, 10), "#F2DCB6"))
    o.append(flat(E(6 * -f, -24, 8, 6), "#C98F5E"))                         # a spot
    o.append(paint(E(24 * f, -42, 15, 13), "#F2DCB6", bevel=1.2))
    o.append(paint(E(36 * f, -36, 6, 9, rot=25 * f), "#C98F5E"))           # ear
    o.append(flat(E(28 * f, -36, 7, 5), "#FBEFDD"))                          # muzzle
    o.append(flat(E(31 * f, -38, 2.6, 2.2), DARK))                           # nose
    o.append(eye(20 * f, -45, 2.4) if mood != "happy" else happy_eye(20 * f, -45, 2.6))
    o.append(stroke(f"M{27 * f - 3},-33 Q{27 * f},-30 {27 * f + 3},-33", DARK, 1.5))
    if hold:
        o.append(f'<g transform="translate({34 * f:.1f} -30)">{hold}</g>')
    return "".join(o)


def kitten():
    o = [paint(E(0, -14, 16, 14), "#C9C2B8", bevel=1.2)]
    for sgn in (-1, 1):
        o.append(paint(P([(sgn * 6, -24), (sgn * 15, -36), (sgn * 16, -20)]).buffer(1.5), "#C9C2B8"))
    o.append(flat(E(0, -9, 5, 3.5), "#FBEFDD") + flat(E(0, -11, 1.8, 1.4), "#E0828E"))
    o.append(eye(-6, -16, 2.3) + eye(6, -16, 2.3))
    o.append(stroke("M-9,-10 L-16,-12 M-9,-8 L-16,-7 M9,-10 L16,-12 M9,-8 L16,-7", DARK, 1.2))
    return "".join(o)


def bunny():
    o = [paint(E(0, -12, 15, 13), WHITE, bevel=1.2)]
    for sgn in (-1, 1):
        o.append(paint(E(sgn * 7, -34, 5, 13, rot=sgn * 8), WHITE))
        o.append(flat(E(sgn * 7, -34, 2.2, 8, rot=sgn * 8), "#F7C6D2"))
    o.append(eye(-6, -14, 2.3) + eye(6, -14, 2.3))
    o.append(flat(E(0, -9, 2, 1.5), "#E0828E") + stroke("M-3,-6 Q0,-4 3,-6", DARK, 1.3))
    o.append(cheeks(0, -8, 9, 2.6))
    return "".join(o)


def duck():
    o = [paint(E(0, -13, 15, 13), YEL, bevel=1.2)]
    o.append(paint(E(0, -6, 9, 4), ORA))
    o.append(flat(E(0, -27, 5, 4, rot=-20), YEL))
    o.append(eye(-6, -16, 2.3) + eye(6, -16, 2.3))
    o.append(cheeks(0, -10, 10, 2.4))
    return "".join(o)


BUDDIES = [("小狗", lambda: place(0, 0, .9, puppy, "smile", -1)), ("小貓", kitten), ("小兔", bunny), ("小鴨", duck)]


# ================================================================ ICONS (round (0, 0), about 30 units wide)
def i_sun(col=YEL, s=1.0):
    o = [stroke("".join(f"M{12 * s * math.cos(math.radians(a)):.1f},{12 * s * math.sin(math.radians(a)):.1f} "
                        f"L{17 * s * math.cos(math.radians(a)):.1f},{17 * s * math.sin(math.radians(a)):.1f} " for a in range(0, 360, 45)), ORA, 3 * s)]
    o.append(paint(E(0, 0, 10 * s), col))
    return "".join(o)


def i_toothbrush(s=1.0):
    g = f'<g transform="rotate(-35) scale({s})">'
    return g + paint(R(-16, -3.5, 30, 7, 3.5), BLUE) + paint(R(8, -6, 10, 12, 3), WHITE) + stroke("M10,-4 V4 M13,-4 V4 M16,-4 V4", "#CFE5F3", 1.2) + "</g>"


def i_bowl(s=1.0):
    g = f'<g transform="scale({s})">'
    bowl = E(0, 2, 15, 10).intersection(sbox(-20, 2, 20, 20))
    return g + paint(U(E(-3, -2, 7, 5), E(4, -3, 7, 5), E(0, 0, 10, 4)), WHITE) + paint(U(bowl, R(-15, -1, 30, 5, 2.5)), RED) + stroke("M-6,-14 L-2,-2 M8,-16 L5,-2", WALNUT, 2) + "</g>"


def i_backpack(s=1.0):
    g = f'<g transform="scale({s})">'
    return (g + paint(R(-10, -17, 20, 8, 4), darker(GRN, .25)) + paint(R(-13, -13, 26, 30, 8), GRN) + paint(R(-9, 2, 18, 12, 4), lighter(GRN, .45))
            + stroke("M-7,-10 V-4 M7,-10 V-4", darker(GRN, .3), 2.4) + flat(E(0, -6, 2.2), YEL) + "</g>")


def i_ball(s=1.0):
    g = f'<g transform="scale({s})">'
    return g + paint(E(0, 0, 14), RED) + flat(E(0, 0, 14).intersection(sbox(-20, -4, 20, 4)), WHITE) + flat(star_g(4.5, 0, 0), YEL) + "</g>"


def i_moon(s=1.0):
    g = f'<g transform="scale({s})">'
    m = E(0, 0, 14).difference(E(6, -3, 11))
    return g + paint(m, YEL) + flat(star_g(3, 9, 6), YEL) + "</g>"


def i_drop(s=1.0, col=BLUE):
    d = P(crs([(0, -16), (9, -2), (10, 6), (0, 14), (-10, 6), (-9, -2)], 8))
    return paint(d.buffer(0), col, sh=2) + f'<ellipse cx="{-3.5 * s}" cy="{2 * s}" rx="2.2" ry="4" fill="#FFFFFF" opacity=".7"/>'


def i_toilet(s=1.0):
    g = f'<g transform="scale({s})">'
    return g + paint(R(-6, -16, 14, 14, 3), WHITE) + paint(E(-2, 4, 14, 8), WHITE) + flat(E(-2, 3, 9, 4.5), SKY) + "</g>"


def i_bath(s=1.0):
    g = f'<g transform="scale({s})">'
    return g + paint(U(E(0, -2, 16, 7).intersection(sbox(-20, -2, 20, 20)), R(-16, -4, 32, 4, 2)), WHITE) + flat(E(0, -3, 12, 2.5), SKY) + stroke("M-12,-10 V-16 Q-12,-19 -8,-19", GREY, 2) + "</g>"


def i_hands(s=1.0):
    g = f'<g transform="scale({s})">'
    return g + paint(U(E(-5, 2, 8, 10, rot=-15), R(-10, -14, 4, 12, 2), R(-5, -16, 4, 14, 2), R(0, -14, 4, 12, 2)), SKINS[0]) + flat(E(6, -2, 6, 7), SKY, 'opacity=".8"') + "</g>"


def i_shirt(s=1.0, col=PINK):
    g = f'<g transform="scale({s})">'
    t = P([(-14, -10), (-6, -14), (0, -11), (6, -14), (14, -10), (12, -3), (8, -4), (8, 12), (-8, 12), (-8, -4), (-12, -3)]).buffer(1.2, join_style=1)
    return g + paint(t, col) + "</g>"


def i_toybox(s=1.0):
    g = f'<g transform="scale({s})">'
    return g + paint(R(-14, -4, 28, 16, 3), ORA) + paint(R(-16, -10, 32, 7, 3), darker(ORA, .15)) + flat(E(-5, 4, 4), BLUE) + flat(star_g(4, 6, 4), YEL) + "</g>"


def i_book(s=1.0, col=TEAL):
    g = f'<g transform="scale({s})">'
    return g + paint(R(-12, -14, 24, 28, 3), col) + flat(R(-8, -10, 16, 20, 2), WHITE) + stroke("M-5,-5 H5 M-5,0 H5 M-5,5 H2", GREY, 1.4) + "</g>"


def i_star(s=1.0, col=YEL):
    return paint(star_g(14 * s), col, sh=2)


def i_flower(s=1.0):
    g = f'<g transform="scale({s})">'
    pet = U(*[E(9 * math.cos(math.radians(a)), 9 * math.sin(math.radians(a)), 6, 4.5, rot=a) for a in range(0, 360, 60)])
    return g + paint(pet, PINK) + flat(E(0, 0, 4.5), YEL) + "</g>"


def i_flowerpot(s=1.0):
    g = f'<g transform="scale({s})">'
    pot = P([(-11, 2), (11, 2), (8, 16), (-8, 16)]).buffer(1.5, join_style=1)
    return g + paint(LineString([(0, 2), (0, -8)]).buffer(1.6), GRN) + paint(E(-5, -4, 5, 2.5, rot=-30), GRN) + i_flower(.8).replace("<g transform=", '<g transform="translate(0 -14)"><g transform=', 1) + "</g>" + paint(pot, ORA) + paint(R(-13, 0, 26, 5, 2.5), darker(ORA, .12)) + "</g>"


def i_lock(cx, cy, col="#8A8F9C", s=1.0):
    return (stroke(f"M{cx - 5 * s:.1f},{cy - 1 * s:.1f} V{cy - 6 * s:.1f} A{5 * s},{5 * s} 0 0 1 {cx + 5 * s:.1f},{cy - 6 * s:.1f} V{cy - 1 * s:.1f}", col, 2.6 * s)
            + flat(R(cx - 8 * s, cy - 2 * s, 16 * s, 13 * s, 3 * s), col))


def i_speaker(cx, cy, col="#FFFFFF", s=1.0):
    g = P(tf([(-12, -5), (-6, -5), (2, -12), (2, 12), (-6, 5), (-12, 5)], cx - 2 * s, cy, s=s)).buffer(1.4 * s, join_style=1)
    w = (f"M{cx + 4.5 * s:.1f},{cy - 5 * s:.1f} A{8 * s},{8 * s} 0 0 1 {cx + 4.5 * s:.1f},{cy + 5 * s:.1f} "
         f"M{cx + 8.5 * s:.1f},{cy - 10 * s:.1f} A{14 * s},{14 * s} 0 0 1 {cx + 8.5 * s:.1f},{cy + 10 * s:.1f}")
    return flat(g, col) + stroke(w, col, 2.6 * s)


def i_home(cx, cy, col=RED, s=1.0):
    g = P(tf([(-14, 0), (0, -13), (14, 0), (10, 0), (10, 12), (-10, 12), (-10, 0)], cx, cy, s=s)).buffer(1.6 * s, join_style=1)
    return paint(g, col, sh=0) + flat(R(cx - 3.8 * s, cy + 3 * s, 7.6 * s, 9.5 * s, 3 * s), WHITE)


def i_check(cx, cy, s=1.0, col="#FFFFFF"):
    return stroke(f"M{cx - 7 * s:.1f},{cy:.1f} L{cx - 2 * s:.1f},{cy + 5.5 * s:.1f} L{cx + 8 * s:.1f},{cy - 6 * s:.1f}", col, 3.6 * s)


def i_arrow(cx, cy, s=1.0, col="#FFFFFF", rot=0.0):
    g = P(tf([(-11, -4), (2, -4), (2, -11), (13, 0), (2, 11), (2, 4), (-11, 4)], cx, cy, rot, s=s)).buffer(1.2 * s, join_style=1)
    return flat(g, col)


def finger(x, y, rot=-25.0):
    """A see-through grown-up fingertip pressing at (x, y)."""
    g = LineString([(0, 0), (0, 96)]).buffer(24, cap_style=1)
    d = dgeom(g)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot})">'
            f'<circle cx="0" cy="0" r="34" fill="#FFFFFF" opacity=".35"/>'
            f'<path d="{d}" fill="#FFE1CF" fill-opacity=".62" stroke="#D99D82" stroke-opacity=".55" stroke-width="2"/>'
            f'<path d="M-12,-8 Q0,-17 12,-8 L12,8 Q0,14 -12,8Z" fill="#FFFFFF" fill-opacity=".55"/>'
            f'<path d="M-16,10 Q-18,40 -14,64" stroke="#FFFFFF" stroke-opacity=".55" stroke-width="4" fill="none" stroke-linecap="round"/></g>')


# ---------------------------------------------------------------- the picture clock
TASKS = [("起床", i_sun), ("刷牙", i_toothbrush), ("吃飯", i_bowl), ("上學", i_backpack), ("出去玩", i_ball), ("睡覺", i_moon)]


def clock(cx, cy, r, hand=1, glow=True, labels=False, isize=1.0, drag_to=None):
    """The big picture clock: six task pictures round the rim, a wooden hand pointing at the one to do now."""
    o = [wood(E(cx, cy, r + 10), WOOD2, grain=.4, sh=2)]
    o.append(wood(E(cx, cy, r + 3), PLY, grain=.3, sh=0))
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 6.5}" fill="none" stroke="{RED}" stroke-width="5" opacity=".9"/>')
    ri = r * .72
    for i, (name, fn) in enumerate(TASKS):
        a = math.radians(-90 + 60 * i)
        x, y = cx + ri * math.cos(a), cy + ri * math.sin(a)
        if i == hand and glow:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .3:.1f}" fill="{rg([(0, "#FFF4B0"), (.6, "#FFE26B", .9), (1, "#FFE26B", 0)])}"/>')
        o.append(place(x, y, (r / 95) * isize * (1.18 if i == hand else 1), fn))
        if labels:
            o.append(tx(x, y + r * .31 + 6, name, max(11, r * .12), INK))
        a2 = math.radians(-60 + 60 * i)
        o.append(f'<circle cx="{cx + r * .9 * math.cos(a2):.1f}" cy="{cy + r * .9 * math.sin(a2):.1f}" r="{max(2, r * .03):.1f}" fill="{WALNUT}" opacity=".6"/>')
    ang = -90 + 60 * hand if drag_to is None else drag_to
    a = math.radians(ang)
    L = r * .5
    hand_g = U(LineString([(cx, cy), (cx + L * math.cos(a), cy + L * math.sin(a))]).buffer(max(3, r * .05), cap_style=1),
               P([(cx + (L + r * .1) * math.cos(a), cy + (L + r * .1) * math.sin(a)),
                  (cx + (L - r * .06) * math.cos(a) + r * .09 * math.sin(a), cy + (L - r * .06) * math.sin(a) - r * .09 * math.cos(a)),
                  (cx + (L - r * .06) * math.cos(a) - r * .09 * math.sin(a), cy + (L - r * .06) * math.sin(a) + r * .09 * math.cos(a))]))
    o.append(paint(hand_g, WALNUT, sh=2, grain=.3))
    o.append(paint(E(cx, cy, max(4, r * .07)), RED, sh=1))
    return "".join(o)


# ================================================================ FURNITURE (each piece drawn with its feet at y = 0, centred on x = 0)
def sofa(w=90, col=TEAL):
    o = [paint(R(-w / 2, -40, w, 30, 10), col)]
    o.append(paint(R(-w / 2 - 6, -22, w + 12, 18, 7), col))
    for sgn in (-1, 1):
        o.append(paint(R(sgn * (w / 2 - 2) - 8, -30, 16, 26, 7), darker(col, .12)))
    o.append(paint(R(-w / 2 + 16, -26, w / 2 - 20, 12, 4), lighter(col, .45)) + paint(R(4, -26, w / 2 - 20, 12, 4), lighter(col, .45)))
    o.append(paint(E(-w * .22, -34, 10, 8), YEL, sh=0))
    return "".join(o)


def toybox(open_=True):
    o = [paint(R(-24, -26, 48, 26, 5), ORA)]
    o.append(flat(R(-20, -22, 40, 18, 3), lighter(ORA, .25)))
    o.append(flat(star_g(6, 0, -13), WHITE))
    if open_:
        o.append(paint(E(-10, -30, 7), BLUE, sh=0) + paint(R(2, -36, 12, 10, 2), GRN, sh=0))
    o.append(paint(R(-27, -32, 54, 7, 3.5), darker(ORA, .15)))
    return "".join(o)


def window(w=60, h=56, sky="morning", curtains=False, drawn=0.0, rain=False):
    skies = {"morning": [(0, "#CDEBFA"), (1, "#F3FBFF")], "noon": [(0, "#9CD3F5"), (1, "#DFF3FF")],
             "evening": [(0, "#F8B58C"), (1, "#FFE2B0")], "night": [(0, "#2A3560"), (1, "#4A5A8A")]}[sky]
    o = [wood(R(-w / 2 - 6, -h - 6, w + 12, h + 12, 6), WOOD2, grain=.4, sh=1)]
    o.append(f'<rect x="{-w / 2}" y="{-h}" width="{w}" height="{h}" rx="3" fill="{lg(skies)}"/>')
    if sky in ("morning", "noon"):
        o.append(f'<circle cx="{w * .25}" cy="{-h * .7}" r="{h * .17}" fill="{YEL}"/>')
        o.append(f'<ellipse cx="{-w * .2}" cy="{-h * .42}" rx="{w * .2}" ry="{h * .1}" fill="#FFFFFF" opacity=".85"/>')
    elif sky == "evening":
        o.append(f'<circle cx="{w * .2}" cy="{-h * .3}" r="{h * .2}" fill="{ORA}"/>')
    else:
        o.append(f'<path d="{dgeom(E(w * .22, -h * .66, h * .16).difference(E(w * .3, -h * .72, h * .14)))}" fill="{YEL}"/>')
        for sx, sy in ((-.3, -.8), (-.1, -.55), (.1, -.85), (-.35, -.3)):
            o.append(f'<circle cx="{w * sx:.1f}" cy="{h * sy:.1f}" r="1.6" fill="#FFFFFF"/>')
    if rain:
        for i in range(7):
            o.append(stroke(f"M{-w / 2 + 6 + i * (w - 12) / 6:.1f},{-h + 8 + (i % 3) * 9:.1f} l-3,10", BLUE, 1.6))
    o.append(stroke(f"M0,{-h} V0 M{-w / 2},{-h / 2} H{w / 2}", WOOD2, 3))
    if curtains:
        cw = w * (.18 + .32 * drawn)
        for sgn in (-1, 1):
            cg = P(crs([(sgn * w / 2, -h - 2), (sgn * (w / 2 - cw), -h - 2), (sgn * (w / 2 - cw * .8), -h * .5), (sgn * (w / 2 - cw), 2), (sgn * w / 2, 2)], 6))
            o.append(paint(cg, PINK, sh=1, grain=.08))
            o.append(stroke(f"M{sgn * (w / 2 - cw * .3):.1f},{-h * .95} V-2", lighter(PINK, .4), 2))
        o.append(paint(R(-w / 2 - 10, -h - 10, w + 20, 6, 3), WALNUT))
    return "".join(o)


def bed(w=96, night=False, blanket=.55, sheet=BLUE):
    o = [paint(R(-w / 2, -44, 10, 44, 4), WOOD2) + paint(R(w / 2 - 10, -34, 10, 34, 4), WOOD2)]
    o.append(paint(R(-w / 2, -20, w, 14, 5), WOOD2))                             # frame
    o.append(paint(R(-w / 2 + 2, -30, w - 4, 12, 5), WHITE))                       # mattress
    o.append(paint(R(-w / 2 + 6, -38, 24, 12, 5), lighter(YEL, .5)))                # pillow
    bl = R(-w / 2 + 2 + (w - 4) * (1 - blanket), -34, (w - 4) * blanket, 16, 6)
    o.append(paint(bl, sheet, grain=.08))
    for i in range(3):
        o.append(flat(E(-w / 2 + 2 + (w - 4) * (1 - blanket) + 14 + i * 16, -26, 4, 4), lighter(sheet, .45)))
    return "".join(o)


def nightlight(on=True):
    o = [paint(R(-12, -22, 24, 22, 4), WOOD2)]
    if on:
        o.append(f'<circle cx="0" cy="-30" r="22" fill="{rg([(0, "#FFE9A8", .9), (1, "#FFE9A8", 0)])}"/>')
    o.append(paint(E(0, -30, 8, 9), YEL if on else GREY, sh=0))
    o.append(paint(R(-4, -24, 8, 4, 2), WALNUT, sh=0))
    return "".join(o)


def bookshelf():
    o = [paint(R(-20, -30, 40, 30, 3), WOOD2)]
    for i, c in enumerate((RED, GRN, BLUE, YEL)):
        o.append(paint(R(-16 + i * 8.5, -26 + (i % 2) * 3, 7, 22 - (i % 2) * 3, 1.5), c, sh=0))
    return "".join(o)


def wardrobe():
    o = [paint(R(-18, -60, 36, 60, 5), WOOD2)]
    o.append(stroke("M0,-56 V-4", WALNUT, 1.6) + flat(E(-4, -30, 1.8), WALNUT) + flat(E(4, -30, 1.8), WALNUT))
    return "".join(o)


def ruler():
    o = [paint(R(-5, -70, 10, 70, 2), YEL)]
    for i in range(7):
        o.append(stroke(f"M-3,{-64 + i * 10} H{1 if i % 2 else 3}", WALNUT, 1.2))
    o.append(flat(E(0, -34, 3), RED))
    return "".join(o)


def toilet():
    o = [paint(R(-6, -42, 16, 24, 3), WHITE)]
    o.append(paint(R(-14, -20, 30, 14, 6), WHITE) + paint(E(1, -20, 16, 7), lighter(SKY, .2)))
    o.append(flat(E(1, -20, 10, 4), SKY) + paint(R(-9, -8, 20, 8, 3), WHITE))
    o.append(flat(E(5, -38, 2.2), GREY))
    return "".join(o)


def sink(mirror=True):
    o = []
    if mirror:
        o.append(wood(R(-18, -76, 36, 30, 6), WOOD2, grain=.4) + f'<rect x="-14" y="-72" width="28" height="22" rx="4" fill="{lg([(0, "#E6F6FF"), (1, "#BFE0F2")])}"/>')
    o.append(paint(R(-14, -34, 28, 34, 4), WOOD2))
    o.append(paint(E(0, -34, 18, 7), WHITE) + flat(E(0, -34, 11, 3.5), SKY))
    o.append(stroke("M0,-40 V-46 Q0,-50 5,-50", GREY, 2.6))
    return "".join(o)


def bathtub():
    tub = U(E(0, -8, 30, 16).intersection(sbox(-40, -8, 40, 20)), R(-30, -12, 60, 6, 3))
    o = [paint(tub, WHITE)]
    o.append(flat(E(0, -10, 24, 4), SKY) + stroke("M-22,-18 V-30 Q-22,-36 -14,-36", GREY, 2.6))
    o.append(paint(R(-30, -8, 60, 8, 3), WHITE, sh=0))
    return "".join(o)


def towel(col=PINK):
    return paint(R(-12, -30, 4, 4, 2), WALNUT) + paint(R(-9, -28, 18, 22, 3), col, grain=.06) + stroke("M-6,-14 H6", lighter(col, .5), 2)


def fridge():
    o = [paint(R(-18, -64, 36, 64, 6), WHITE)]
    o.append(stroke("M-14,-40 H14", GREY, 1.6) + paint(R(10, -56, 3, 10, 1.5), GREY, sh=0) + paint(R(10, -34, 3, 14, 1.5), GREY, sh=0))
    o.append(flat(E(-8, -52, 3.5), RED) + flat(star_g(4, -8, -22), YEL))
    return "".join(o)


def table(w=90, chairs=True):
    o = []
    if chairs:
        for sgn in (-1, 1):
            o.append(paint(R(sgn * (w / 2 + 2) - 8, -28, 16, 28, 4), WOOD2) + paint(R(sgn * (w / 2 + 6) - 4, -46, 8, 22, 3), WOOD2))
    o.append(paint(R(-w / 2 + 8, -34, 8, 34, 3), WOOD2) + paint(R(w / 2 - 16, -34, 8, 34, 3), WOOD2))
    o.append(paint(R(-w / 2, -38, w, 8, 4), WOOD))
    return "".join(o)


def counter():
    o = [paint(R(-30, -34, 60, 34, 4), TEAL)]
    o.append(paint(R(-32, -38, 64, 6, 3), WOOD) + paint(E(10, -38, 12, 4), WHITE, sh=0) + stroke("M10,-42 V-48 Q10,-52 15,-52", GREY, 2.4))
    o.append(stroke("M-26,-28 V-6 M-10,-28 V-6", WHITE, 1.4) + flat(E(-18, -20, 1.6), WHITE))
    return "".join(o)


def bowl_set(x=0, y=0):
    return paint(E(x, y - 3, 7, 3.5).intersection(sbox(-99, y - 3, 99, 99)).union(R(x - 7, y - 4, 14, 2, 1)), WHITE, sh=0) + stroke(f"M{x + 9},{y - 12} V{y} M{x + 12},{y - 12} V{y}", WALNUT, 1.4)


def door(open_=False):
    o = [wood(R(-22, -72, 44, 72, 8).difference(R(-18, -68, 36, 68, 6)), WOOD2, grain=.4)]
    o.append(paint(R(-18, -68, 36, 68, 6), RED, grain=.1))
    o.append(flat(R(-12, -60, 24, 26, 4), darker(RED, .15)) + flat(R(-12, -28, 24, 22, 4), darker(RED, .15)))
    o.append(paint(E(11, -34, 3), YEL, sh=0))
    return "".join(o)


def shoe_cabinet():
    o = [paint(R(-28, -36, 56, 36, 4), WOOD2)]
    o.append(stroke("M-24,-18 H24", WALNUT, 1.4))
    for i, c in enumerate((RED, BLUE, PINK)):
        x = -18 + i * 17
        o.append(paint(E(x - 2, -28, 5, 3.5), c, sh=0) + paint(E(x + 5, -28, 5, 3.5), c, sh=0))
    o.append(paint(E(-12, -9, 5, 3.5), GRN, sh=0) + paint(E(-5, -9, 5, 3.5), GRN, sh=0))
    return "".join(o)


def backpack(col=GRN, s=1.0):
    return place(0, -14 * s, s, i_backpack)


def umbrella(col=YEL):
    o = [stroke("M0,-24 V2 Q0,8 5,6", WALNUT, 2.4)]
    o.append(paint(E(0, -22, 16, 14).intersection(sbox(-20, -40, 20, -22)), col))
    o.append(stroke("M-16,-22 Q-10,-18 -5,-22 Q0,-18 5,-22 Q10,-18 16,-22", darker(col, .2), 1.6))
    return "".join(o)


def helmet(col=BLUE):
    return paint(E(0, -8, 12, 11).intersection(sbox(-20, -40, 20, -6)), col) + flat(E(0, -8, 12, 11).intersection(sbox(-20, -40, 20, -12)).intersection(sbox(-20, -40, -3, 0)), lighter(col, .4)) + stroke("M-12,-7 H12", darker(col, .2), 2)


def railing(w=70):
    o = [paint(R(-w / 2, -30, w, 5, 2.5), WOOD2)]
    for i in range(5):
        o.append(paint(R(-w / 2 + 4 + i * (w - 12) / 4, -27, 4, 27, 2), WOOD2, sh=0))
    return "".join(o)


def plant(wilt=False, s=1.0):
    pot = P([(-11, -14), (11, -14), (8, 0), (-8, 0)]).buffer(1.5, join_style=1)
    o = []
    if wilt:
        o.append(paint(LineString([(0, -14), (3, -24), (12, -28)]).buffer(1.8), "#B9B07A"))
        o.append(paint(E(13, -28, 6, 3.5, rot=50), "#B9B07A") + paint(E(-6, -22, 6, 3.5, rot=-60), "#B9B07A"))
    else:
        o.append(paint(LineString([(0, -14), (0, -34)]).buffer(1.8), GRN))
        for x, y, r_ in ((-7, -28, -40), (7, -24, 40), (-6, -20, -20), (6, -32, 30)):
            o.append(paint(E(x, y, 7, 4, rot=r_), GRN))
        o.append(place(0, -38, .6, i_flower))
    o.append(paint(pot, ORA) + paint(R(-13, -16, 26, 5, 2.5), darker(ORA, .12)))
    return "".join(o)


def clothesline(w=120, items=None):
    o = [paint(R(-w / 2 - 3, -62, 6, 62, 3), WOOD2) + paint(R(w / 2 - 3, -62, 6, 62, 3), WOOD2)]
    o.append(stroke(f"M{-w / 2},-56 Q0,-50 {w / 2},-56", WALNUT, 2))
    for x, kind, col in (items or []):
        y = -53 + abs(x) * .05
        o.append(paint(R(x - 2, y - 3, 4, 8, 1.5), WOOD2, sh=0))
        if kind == "sock":
            sock = U(R(x - 6, y + 3, 12, 20, 4), E(x + 3, y + 22, 9, 6))
            o.append(paint(sock, col, grain=.06))
            o.append(flat(R(x - 6, y + 3, 12, 5, 2), lighter(col, .5)))
        elif kind == "shirt":
            o.append(place(x, y + 18, 1.0, i_shirt, 1.0, col))
        else:
            o.append(paint(R(x - 9, y + 3, 18, 14, 3), col, grain=.06))
    return "".join(o)


def pet_bowl(col=RED):
    return paint(U(E(0, -4, 13, 5).intersection(sbox(-20, -4, 20, 20)), R(-13, -6, 26, 4, 2)), col) + flat(E(0, -5, 9, 3), "#C98F5E")


def bins():
    return (paint(R(-26, -26, 20, 26, 4), GREY) + paint(R(-28, -30, 24, 6, 3), darker(GREY, .15))
            + paint(R(4, -26, 20, 26, 4), BLUE) + paint(R(2, -30, 24, 6, 3), darker(BLUE, .15))
            + stroke("M10,-14 l4,-4 l4,4 M18,-14 l-4,4 l-4,-4", WHITE, 1.4))


def rug(w=100, col=PINK):
    return paint(E(0, -3, w / 2, 7), col, sh=0, grain=.08) + flat(E(0, -3, w / 2 - 10, 4), lighter(col, .4))


def lamp():
    return paint(R(-2, -56, 4, 56, 2), WOOD2) + paint(E(0, -2, 10, 3), WOOD2) + paint(P([(-14, -58), (14, -58), (10, -78), (-10, -78)]).buffer(1.5, join_style=1), YEL)


def phone():
    return paint(R(-10, -18, 20, 18, 3), WOOD2) + paint(R(-7, -26, 14, 8, 3), RED) + stroke("M-8,-20 Q-8,-24 -4,-24", RED, 2)


def picture_frame(col=GRN):
    return wood(R(-14, -12, 28, 24, 3), WOOD2, grain=.4) + flat(R(-10, -8, 20, 16, 2), SKY) + flat(E(-3, 0, 6, 4).intersection(sbox(-20, -20, 20, 0)), col) + flat(E(5, -4, 2.5), YEL)


def stairs(up=True, n=4, step=10):
    o = []
    for i in range(n):
        x = i * step if up else -i * step
        o.append(paint(R(x, -(i + 1) * step, step + 4, (i + 1) * step, 2), WOOD2, sh=0 if i else 1))
    return "".join(o)


def footprints(pts, col=YEL, n=6, s=1.0, glow=False):
    """Little pairs of feet along a path."""
    ls = LineString(pts)
    o = []
    for i in range(n):
        t = (i + .5) / n
        p = ls.interpolate(t, normalized=True)
        q = ls.interpolate(min(1, t + .02), normalized=True)
        ang = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
        side = -1 if i % 2 else 1
        ox, oy = -math.sin(math.radians(ang)) * 4.5 * side * s, math.cos(math.radians(ang)) * 4.5 * side * s
        foot = U(E(0, 0, 3.2 * s, 4.6 * s), E(0, -5 * s, 2.4 * s, 1.8 * s), E(2.6 * s, -4.6 * s, 1.3 * s, 1.1 * s), E(-2.6 * s, -4.6 * s, 1.3 * s, 1.1 * s))
        g = f'<g transform="translate({p.x + ox:.1f} {p.y + oy:.1f}) rotate({ang + 90:.1f})">'
        if glow:
            o.append(g + f'<circle r="{10 * s}" fill="#FFF3A0" opacity=".85" filter="{blur(2)}"/></g>')
        o.append(g + f'<path d="{dgeom(foot.buffer(1.6 * s))}" fill="#FFFFFF" opacity=".85"/>' + flat_wood(foot, col) + "</g>")
    return "".join(o)


# ================================================================ THE DOLLHOUSE
HX, HW = 14, 362                      # outer x and width
ROOF_Y, EAVE_Y = 232, 292
SLAB = 8
ROOMS_Y = [(300, 456), (464, 620), (628, 784)]     # top of room, bottom of room for the three floors
ROOM_BOX = {"bed": (22, 300, 170, 156), "bath": (200, 300, 168, 156),
            "living": (22, 464, 264, 156), "balcony": (294, 464, 74, 156),
            "door": (22, 628, 170, 156), "kitchen": (200, 628, 168, 156)}
ROOM_NAME = {"bed": "房間", "bath": "廁所", "living": "客廳", "balcony": "陽台", "door": "門口", "kitchen": "廚房"}


def room_sign(x, y, name, size=11):
    w = size * len(name) + 14
    return paint(R(x, y, w, size + 8, 4), WOOD2, sh=1) + tx(x + w / 2, y + size + 2, name, size, INK)


def room_bed(x, y, w, h, night=False, big=False):
    o = [place(x + w * .74, y + 48, .7, window, 56, 46, "night" if night else "morning", True, .6 if night else .15)]
    o.append(place(x + w * .4, y + h, .85, bed, 96, night))
    o.append(place(x + w * .08, y + h, .8, nightlight, True))
    o.append(place(x + w * .9, y + h, .8, wardrobe))
    o.append(place(x + w * .9, y + h * .5, .7, bookshelf))
    o.append(place(x + w * .07, y + h * .6, .75, ruler))
    return "".join(o)


def room_bath(x, y, w, h, night=False):
    o = [place(x + w * .5, y + h, .85, sink, True)]
    o.append(place(x + w * .16, y + h, .9, toilet))
    o.append(place(x + w * .8, y + h, .8, bathtub))
    o.append(place(x + w * .9, y + h * .5, .75, towel, PINK))
    return "".join(o)


def room_living(x, y, w, h, sky="morning", rain=False, night=False):
    o = [place(x + w * .45, y + h - 2, .9, rug, 110, PINK)]
    o.append(place(x + w * .24, y + 50, .72, window, 64, 50, sky, False, 0, rain))
    o.append(place(x + w * .2, y + h, .85, sofa, 90, TEAL))
    o.append(place(x + w * .68, y + h, .8, toybox))
    o.append(place(x + w * .88, y + h * .3, .7, picture_frame, LILAC))
    o.append(place(x + w * .88, y + h * .62, .7, lambda: paint(R(-14, -2, 28, 4, 2), WOOD2) + place(0, -2, .9, phone)))
    o.append(place(x + w * .05, y + h, .8, lamp))
    return "".join(o)


def room_balcony(x, y, w, h, night=False, wilt=False):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{lg([(0, "#2A3560"), (1, "#4A5A8A")] if night else [(0, "#CDEBFA"), (1, "#EAF7FF")])}"/>']
    o.append(place(x + w * .5, y + 46, .55, clothesline, 110, [(-36, "sock", RED), (-10, "shirt", YEL), (20, "sock", BLUE), (40, "cloth", PINK)]))
    o.append(place(x + w * .22, y + h, .7, plant, wilt))
    o.append(place(x + w * .74, y + h, .6, bins))
    o.append(place(x + w * .5, y + h, .7, railing, 100))
    o.append(place(x + w * .5, y + h, .6, pet_bowl))
    return "".join(o)


def room_door(x, y, w, h, night=False):
    o = [place(x + w * .22, y + h, .85, door)]
    o.append(place(x + w * .68, y + h, .85, shoe_cabinet))
    o.append(place(x + w * .6, y + h * .22, .9, backpack, GRN, .9))
    o.append(place(x + w * .9, y + h * .62, .8, umbrella, YEL))
    o.append(place(x + w * .8, y + h * .3, .75, helmet, BLUE))
    o.append(place(x + w * .62, y + h * .08, .8, lambda: paint(R(-30, -2, 60, 4, 2), WOOD2)))
    return "".join(o)


def room_kitchen(x, y, w, h, night=False):
    o = [place(x + w * .12, y + h, .85, fridge)]
    o.append(place(x + w * .84, y + h, .8, counter))
    o.append(place(x + w * .47, y + h, .78, table, 80, True))
    o.append(place(x + w * .47, y + h - 30, .78, lambda: bowl_set(-14, 0) + bowl_set(12, 0)))
    return "".join(o)


ROOM_DRAW = {"bed": room_bed, "bath": room_bath, "living": room_living, "balcony": room_balcony, "door": room_door, "kitchen": room_kitchen}


def house(night=False, sky="morning", rain=False, dim=(), highlight=None, signs=True, wilt=False, lit=None):
    """The whole dollhouse, front open. dim: rooms drawn darker; highlight: a room with a glowing frame;
    lit: at night, the one room that still has its light on."""
    o = []
    # roof
    roof = P([(HX - 10, EAVE_Y), (W / 2, ROOF_Y), (HX + HW + 10, EAVE_Y)]).buffer(4, join_style=1)
    o.append(paint(roof, RED, sh=2, grain=.2))
    for i in range(4):
        yy = EAVE_Y - 8 - i * 12
        hw = (EAVE_Y - yy) / (EAVE_Y - ROOF_Y) * (HW / 2 + 10)
        o.append(stroke(f"M{W / 2 - hw:.1f},{yy} H{W / 2 + hw:.1f}", darker(RED, .2), 1.4, op=.6))
    o.append(paint(R(W / 2 + 70, ROOF_Y + 14, 18, 30, 3), WOOD2, sh=0))
    o.append(paint(R(W / 2 - 14, ROOF_Y + 18, 28, 20, 10), WHITE, sh=0) + flat(E(W / 2, ROOF_Y + 28, 6), SKY))
    # frame and slabs
    o.append(wood(R(HX, EAVE_Y - 2, HW, 790 - EAVE_Y + 10, 10), WOOD, grain=.45, sh=3))
    for key, (x, y, w, h) in ROOM_BOX.items():
        wall = ROOM_WALL.get(key, CREAM)
        if night and key != lit:
            wall = mixc(wall, "#1E2440", .72)
        elif key in dim:
            wall = mixc(wall, "#5A5048", .35)
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{wall}"/>')
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000" opacity=".05" filter="{wood_f(.5, 0, .02)}"/>')
        o.append(f'<rect x="{x}" y="{y + h - 12}" width="{w}" height="12" fill="{WOOD2}" filter="{wood_f(.5, 0, .05)}"/>')
        o.append(stroke(f"M{x},{y + h - 6} H{x + w}", WALNUT, .8, op=.35))
        inner = ROOM_DRAW[key](x, y, w, h - 12, night) if key not in ("balcony", "living") else (
            room_balcony(x, y, w, h - 12, night, wilt) if key == "balcony" else room_living(x, y, w, h - 12, sky, rain, night))
        if night and key != lit:
            inner = f'<g opacity=".55">{inner}</g>'
        elif key in dim:
            inner = f'<g opacity=".7">{inner}</g>'
        o.append(inner)
        if night and key != lit:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#1E2440" opacity=".45"/>')
        elif key in dim:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#5A5048" opacity=".22"/>')
    # stairs: in the living room up to the top floor, in the entrance up to the living room
    for key in ("living", "door"):
        x, y, w, h = ROOM_BOX[key]
        o.append(f'<rect x="{x + w - 56}" y="{y + h - 12}" width="50" height="12" fill="#5A4030" opacity="{.25 if not night else .5}"/>')
        o.append(place(x + w - 56, y + h - 12, 1.0, stairs, True, 4, 11))
    if signs:
        for key, (x, y, w, h) in ROOM_BOX.items():
            o.append(room_sign(x + 6, y + 6, ROOM_NAME[key], 10.5 if key == "balcony" else 11))
    if highlight:
        x, y, w, h = ROOM_BOX[highlight]
        o.append(f'<rect x="{x - 3}" y="{y - 3}" width="{w + 6}" height="{h + 6}" rx="8" fill="none" stroke="#FFE26B" stroke-width="9" opacity=".55" filter="{blur(3)}"/>')
        o.append(f'<rect x="{x - 2}" y="{y - 2}" width="{w + 4}" height="{h + 4}" rx="7" fill="none" stroke="{YEL}" stroke-width="4"/>')
    return "".join(o)


# ================================================================ UI PIECES
def tx(x, y, s, size=16, color=INK, anchor="middle", extra="", weight=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{w} '
            f'font-family="Huninn, sans-serif" {extra}>{s}</text>')


def txo(x, y, s, size, color, ol="#FFFFFF", ow=6, anchor="middle"):
    return tx(x, y, s, size, color, anchor, f'stroke="{ol}" stroke-width="{ow}" stroke-linejoin="round" paint-order="stroke"')


def wtx(x, y, s, size, dark, anchor="middle", col="#FFFFFF"):
    return tx(x + .6, y + 1.6, s, size, dark, anchor, 'opacity=".5"') + tx(x, y, s, size, col, anchor)


def wallpaper(x=0, y=0, w=W, h=H, base="#F6EEDF", col="#E8D7BD"):
    k = "wp" + _h(base, col)
    D.add(k, f'<pattern id="{k}" width="28" height="28" patternUnits="userSpaceOnUse"><rect width="28" height="28" fill="{base}"/>'
             f'<circle cx="7" cy="7" r="2.2" fill="{col}"/><circle cx="21" cy="21" r="2.2" fill="{col}"/></pattern>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{k})"/>'


def shelf(y=800):
    return wood(R(-6, y, W + 12, 16, 4), WOOD2, grain=.45, sh=2) + wood(R(30, y + 16, 14, 30, 3), WOOD2, grain=.4, sh=1) + wood(R(W - 44, y + 16, 14, 30, 3), WOOD2, grain=.4, sh=1)


def wbtn(cx, cy, r, col, icon="", sh=2):
    return paint(E(cx, cy, r), col, sh=sh, bevel=1.3) + icon


def wpill(cx, cy, w, h, col, label="", size=19, icon="", tdx=0.0, sh=2):
    o = paint(R(cx - w / 2, cy - h / 2, w, h, h / 2), col, sh=sh, bevel=1.3) + icon
    if label:
        o += wtx(cx + tdx, cy + size * .36, label, size, darker(col, .45))
    return o


def bubble(x, y, w, h, side=None, at=0.0, fill=WHITE, r=18, tl=16, speaker=True):
    g = R(x, y, w, h, r)
    if side == "left":
        g = g.union(P([(x + 4, at - 11), (x - tl, at + 4), (x + 4, at + 11)]))
    elif side == "right":
        g = g.union(P([(x + w - 4, at - 11), (x + w + tl, at + 4), (x + w - 4, at + 11)]))
    elif side == "down":
        g = g.union(P([(at - 11, y + h - 4), (at + 3, y + h + tl), (at + 11, y + h - 4)]))
    elif side == "up":
        g = g.union(P([(at - 11, y + 4), (at + 3, y - tl), (at + 11, y + 4)]))
    o = paint(soft(g, 2), fill, sh=2, grain=.05, bevel=.8)
    if speaker:
        o += wbtn(x + 22, y + h / 2, 15, TEAL, i_speaker(x + 23, y + h / 2, "#FFFFFF", .7), sh=1)
    return o


def say(x, y, w, h, text, side=None, at=0.0, size=17, speaker=True):
    return bubble(x, y, w, h, side, at, speaker=speaker) + tx(x + w / 2 + (14 if speaker else 0), y + h / 2 + size * .36, text, size, INK)


def lock_chip(x=16, y=16):
    return paint(R(x, y, 74, 32, 16), "#EDE6DC", sh=1) + i_lock(x + 20, y + 16, "#8A8F9C", .85) + tx(x + 48, y + 22, "家長", 14, "#7E7A8C")


def day_chip(x, y, day="星期三", weather="sun", w=96):
    o = [paint(R(x, y, w, 32, 10), WHITE, sh=1)]
    o.append(place(x + 20, y + 16, .6, i_sun if weather == "sun" else lambda: paint(E(0, 0, 12, 8), GREY) + stroke("M-6,8 l-2,6 M2,8 l-2,6", BLUE, 2)))
    o.append(tx(x + 38, y + 21, day, 14, INK, "start"))
    return "".join(o)


def sticker_btn(x, y):
    return wpill(x, y, 100, 36, YEL, "貼紙表", 15, place(x - 30, y, .55, i_star, 1.0, RED), tdx=14)


def home_btn(cx=36, cy=42):
    return wbtn(cx, cy, 24, WHITE, i_home(cx, cy, RED, .95))


def topbar(text=None, hand=1, right=True):
    """The compact top of a mini-game screen: home, a small clock, the spoken instruction."""
    o = [home_btn(36, 44)]
    o.append(clock(338, 46, 30, hand, True, False, .7))
    if text:
        o.append(say(16, 96, 358, 54, text, "up", 338, 18))
    return "".join(o)


def progress_bubbles(cx, y, n, k, r=9, gap=26):
    o = []
    x0 = cx - (n - 1) * gap / 2
    for i in range(n):
        x = x0 + i * gap
        if i < k:
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{rg([(0, "#FFFFFF"), (.7, "#CDEBFA"), (1, "#9CD3F5")], .4, .4)}" stroke="#7FB8DA" stroke-width="1.6"/>'
                     f'<circle cx="{x - r * .35}" cy="{y - r * .35}" r="{r * .25}" fill="#FFFFFF"/>')
        else:
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#B9C7D0" stroke-width="1.6" stroke-dasharray="3 2.5"/>')
    return "".join(o)


def bubbles(cx, cy, n, seed, spread=40, rmax=9):
    import random
    rnd = random.Random(seed)
    o = []
    for _ in range(n):
        x, y, r = cx + rnd.uniform(-spread, spread), cy + rnd.uniform(-spread * .6, spread * .6), rnd.uniform(3, rmax)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#FFFFFF" fill-opacity=".55" stroke="#9CD3F5" stroke-width="1.2"/>'
                 f'<circle cx="{x - r * .35:.1f}" cy="{y - r * .35:.1f}" r="{r * .25:.1f}" fill="#FFFFFF"/>')
    return "".join(o)


def star_sticker(cx, cy, r=18, col=YEL, rot=0.0):
    return (f'<g transform="rotate({rot} {cx} {cy})">' + f'<circle cx="{cx}" cy="{cy}" r="{r + 6}" fill="#FFFFFF" opacity=".95"/>'
            + paint(star_g(r, cx, cy), col, sh=1) + f'<circle cx="{cx - r * .35}" cy="{cy - r * .25}" r="{r * .13}" fill="#FFFFFF" opacity=".8"/></g>')


def page(body, bg, w=W, h=H):
    css = (f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }}"
           f"* {{ margin: 0; padding: 0; }} body {{ width: {w}px; height: {h}px; overflow: hidden; background: {bg}; }}")
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{D.svg()}{body}</svg>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{svg}</body></html>'


def render(html, out, w, h, scale):
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        p = pathlib.Path(tmp) / "page.html"
        p.write_text(html)
        subprocess.run(["node", str(HERE / "render.js"), str(p), str(out), str(w), str(h), str(scale)], check=True)
    if pathlib.Path(out).stat().st_size > 450_000:
        from PIL import Image
        im = Image.open(out).convert("RGB")
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, kmeans=2, dither=Image.Dither.FLOYDSTEINBERG).save(out, optimize=True)


# ================================================================ SCREEN 2: the home and the clock
def screen_home():
    o = [wallpaper()]
    o.append(shelf(802))
    o.append(lock_chip(14, 14))
    o.append(sticker_btn(322, 30))
    o.append(day_chip(14, 56, "星期三", "sun", 92))
    o.append(clock(195, 124, 92, hand=1))
    o.append(house(sky="morning"))
    lx, ly, lw, lh = ROOM_BOX["living"]
    fy = ly + lh - 12
    o.append(footprints([(152, fy - 4), (226, fy - 4), (270, fy - 46), (276, ROOMS_Y[0][1] - 10), (248, ROOMS_Y[0][1] - 14)], ORA, 9, .9))
    o.append(place(118, fy, .82, peg_doll, 0, 0, 0, "smile"))
    o.append(place(170, fy, .7, puppy, "smile", -1))
    o.append(say(118, ly + 14, 162, 46, "小明，該刷牙囉！", "down", 140, 13.5))
    return page("".join(o), "#F6EEDF")


SCREENS = {"2_客廳和時鐘": screen_home}


def main(only=None):
    global D
    for name, make in SCREENS.items():
        if only not in (None, name.split("_")[0]):
            continue
        D = Defs()
        render(make(), HERE / f"{name}.png", W, H, 2)
        print(name)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
