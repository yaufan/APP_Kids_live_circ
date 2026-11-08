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
    2_客廳和時鐘.png   the home: the living room fills the screen under the clock (one room at a time), the clock says 刷牙,
                       the stairs and the 廁所 button glow; a strip of six room buttons at the bottom
    3_調時間.png       the clock enlarged: a finger drags the hand from 牙刷 to 碗
    4_刷牙.png         bathroom mini-game: brushing the big open mouth, bubbles as progress
    5_想上廁所.png     the random need: the child squirms, a water drop, footprints to the glowing stairs
    6_吃飯.png         kitchen: a plate with four slots, foods to drag in, the puppy's own bowl
    7_睡覺.png         bedroom at night: the blanket is pulled up; a small inset shows the whole house dark
    8_貼紙表.png       the good-habits sticker chart and the puppy's reward
    9_家長模式.png     parents' settings
    10_小街 11_幼兒園 12_超市 13_陽台家事 14_發生事情   the street, the kindergarten, the supermarket, chores, events
    contact_sheet.png  screens 1-14 small, with titles

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
WOOD = "#F3D9B0"         # light beech
WOOD2 = "#E9C28F"        # a bit darker beech
WALNUT = "#A97B5B"
PLY = "#FBEBCB"          # the clock face
RED = "#F2857A"
YEL = "#FFD86B"
ORA = "#FFB066"
TEAL = "#7FCFBF"
BLUE = "#8FC1EC"
NAVY = "#8DA4D8"
GRN = "#A6D98A"
PINK = "#F7A8C4"
LILAC = "#C8B3EA"
CREAM = "#FFF4DC"
WHITE = "#FBF7F0"
SKY = "#BFE3F5"
GREY = "#D8D2CC"
DARK = "#3B2A26"
CHEEK = "#FFA8B4"
SKINS = ["#FBE0CB", "#F0C8A4", "#D39B6E", "#9E6A48"]
HAIRS = ["#4A3732", "#8A5A3C", "#F0C04E", "#C2684A", "#D9D3D0"]
SHIRTS = [RED, YEL, GRN, BLUE, PINK, LILAC]
ROOM_WALL = {"bed": "#EEE3FA", "bath": "#DDF2F8", "living": "#FFF3D4", "kitchen": "#E2F4E0", "door": "#FDE6D6"}


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
    """A big round shiny eye."""
    o = f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{DARK}"/>'
    if glint:
        o += (f'<circle cx="{cx - r * .32:.2f}" cy="{cy - r * .32:.2f}" r="{r * .38:.2f}" fill="#FFFFFF"/>'
              f'<circle cx="{cx + r * .35:.2f}" cy="{cy + r * .35:.2f}" r="{r * .18:.2f}" fill="#FFFFFF" opacity=".9"/>')
    return o


def happy_eye(cx, cy, r):
    return stroke(f"M{cx - r:.2f},{cy + r * .3:.2f} Q{cx:.2f},{cy - r * 1.1:.2f} {cx + r:.2f},{cy + r * .3:.2f}", DARK, 2.4)


def sleep_eye(cx, cy, r):
    return stroke(f"M{cx - r:.2f},{cy - r * .2:.2f} Q{cx:.2f},{cy + r * .9:.2f} {cx + r:.2f},{cy - r * .2:.2f}", DARK, 2.2) + stroke(f"M{cx - r * .9:.2f},{cy + r * .5:.2f} l-1.5,2.5 M{cx:.2f},{cy + r * .75:.2f} l0,2.8 M{cx + r * .9:.2f},{cy + r * .5:.2f} l1.5,2.5", DARK, 1.4)


def smile(cx, cy, w, open_=False):
    if open_:
        d = f"M{cx - w:.2f},{cy:.2f} Q{cx:.2f},{cy + w * 1.7:.2f} {cx + w:.2f},{cy:.2f}Z"
        return f'<path d="{d}" fill="#C9546A"/>' + flat(E(cx, cy + w * 1.05, w * .55, w * .35), "#F08A9A")
    return stroke(f"M{cx - w:.2f},{cy:.2f} Q{cx:.2f},{cy + w:.2f} {cx + w:.2f},{cy:.2f}", DARK, 1.8)


def cheeks(cx, cy, dx, r):
    return f'<circle cx="{cx - dx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{CHEEK}" opacity=".75"/><circle cx="{cx + dx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{CHEEK}" opacity=".75"/>'


def face(cx, cy, s=1.0, mood="smile", cheek=True):
    """A tiny friendly face painted on a thing (the clock, the sun, the bowl...)."""
    o = []
    if mood == "sleepy":
        o.append(sleep_eye(cx - 5 * s, cy, 2.6 * s) + sleep_eye(cx + 5 * s, cy, 2.6 * s))
    elif mood == "happy":
        o.append(happy_eye(cx - 5 * s, cy, 2.4 * s) + happy_eye(cx + 5 * s, cy, 2.4 * s))
    else:
        o.append(eye(cx - 4.6 * s, cy, 1.9 * s) + eye(cx + 4.6 * s, cy, 1.9 * s))
    o.append(stroke(f"M{cx - 2.6 * s:.1f},{cy + 4 * s:.1f} Q{cx:.1f},{cy + 6.6 * s:.1f} {cx + 2.6 * s:.1f},{cy + 4 * s:.1f}", DARK, 1.5 * s))
    if cheek:
        o.append(cheeks(cx, cy + 3.5 * s, 8 * s, 2 * s))
    return "".join(o)


def sparkle(cx, cy, r, c=YEL, op=1.0):
    return (f'<path d="M{cx},{cy - r} Q{cx + r * .16},{cy - r * .16} {cx + r},{cy} Q{cx + r * .16},{cy + r * .16} {cx},{cy + r} '
            f'Q{cx - r * .16},{cy + r * .16} {cx - r},{cy} Q{cx - r * .16},{cy - r * .16} {cx},{cy - r}Z" fill="{c}" opacity="{op}"/>')


def heart(cx, cy, s, col=PINK, sh=0):
    return paint(heart_pts(cx, cy, s), col, sh=sh, grain=.06)


# ================================================================ CHARACTERS (drawn round (0, 0) = between the feet, about 100 units tall)
HEAD_Y = -64     # the centre of the doll's head


def doll_head(hair=0, skin=0, mood="smile", open_mouth=False, look=0.0):
    """The chibi head alone (centre at (0, HEAD_Y), radius 28)."""
    hc, sc = HAIRS[hair % len(HAIRS)], SKINS[skin % 4]
    hy = HEAD_Y
    o = [paint(E(0, hy, 28, 27), sc, bevel=1.4)]
    cap = E(0, hy - 3, 30, 29).intersection(sbox(-50, hy - 60, 50, hy - 9))
    bangs = U(E(-15, hy - 12, 11, 8), E(0, hy - 15, 12, 8), E(15, hy - 12, 11, 8)).intersection(sbox(-50, hy - 60, 50, hy - 6))
    style = hair % 4
    if style == 1:      # a little tuft on top
        cap = U(cap, E(2, hy - 34, 8, 6), E(-6, hy - 31, 6, 5))
    elif style == 2:    # a round bob down the sides
        cap = U(cap, E(-26, hy + 2, 8, 17), E(26, hy + 2, 8, 17))
    elif style == 3:    # pigtails
        cap = U(cap, E(-32, hy + 4, 9, 11), E(32, hy + 4, 9, 11))
    o.append(paint(U(cap, bangs), hc, grain=.08, bevel=.9))
    o.append(f'<ellipse cx="-10" cy="{hy - 22}" rx="7" ry="3" fill="#FFFFFF" opacity=".35" transform="rotate(-20 -10 {hy - 22})"/>')
    if style == 3:
        o.append(paint(E(-32, hy - 6, 5, 3.4), YEL, sh=0) + paint(E(32, hy - 6, 5, 3.4), YEL, sh=0))
    ex, ey = 10.5 + look, hy + 2
    if mood == "happy":
        o.append(happy_eye(-ex, ey, 4.2) + happy_eye(ex, ey, 4.2))
    elif mood == "sleep":
        o.append(sleep_eye(-ex, ey, 4.2) + sleep_eye(ex, ey, 4.2))
    else:
        o.append(eye(-ex, ey, 5.4) + eye(ex, ey, 5.4))
        if mood == "worry":
            o.append(stroke(f"M{-ex - 5},{ey - 11} L{-ex + 3},{ey - 9} M{ex + 5},{ey - 11} L{ex - 3},{ey - 9}", DARK, 1.6))
    o.append(cheeks(look, hy + 10, 17, 4.6))
    my = hy + 13
    if open_mouth:
        o.append(paint(E(look, my + 2, 7, 6), "#C9546A", sh=0) + flat(E(look, my + 4, 5, 2.5), "#F08A9A"))
    elif mood == "worry":
        o.append(stroke(f"M{look - 4},{my + 2} Q{look},{my - 1} {look + 4},{my + 2}", DARK, 1.8))
    elif mood == "sleep":
        o.append(stroke(f"M{look - 2.5},{my} Q{look},{my + 2} {look + 2.5},{my}", DARK, 1.6))
    elif mood == "happy":
        o.append(smile(look, my - 1, 4.5, open_=True))
    else:
        o.append(stroke(f"M{look - 3},{my} Q{look},{my + 3} {look + 3},{my}", DARK, 1.8))
    return "".join(o)


def peg_doll(hair=0, skin=0, shirt=0, mood="smile", arms=None, hold="", squirm=False, lying=False, open_mouth=False, look=0.0):
    """The child as a chibi wooden peg doll: a big round head on a short round body. arms: None = painted on,
    'up' = both lifted, 'brush' = the right one lifted, 'head' = hands on the head; hold = svg in the right hand."""
    hc, sc, tc = HAIRS[hair % len(HAIRS)], SKINS[skin % 4], SHIRTS[shirt % 6]
    o = []
    rot = 8 if squirm else 0
    body = P(crs([(-15, -42), (15, -42), (21, -22), (23, -4), (18, 0), (-18, 0), (-23, -4), (-21, -22)], 8))
    o.append(paint(body, tc))
    o.append(flat(body.intersection(sbox(-30, -13, 30, 10)), NAVY))           # painted trousers
    o.append(flat(body.intersection(sbox(-30, -4, 30, 10)), WALNUT))           # painted shoes
    o.append(flat(E(0, -12, 9, 2.4), darker(NAVY, .15)))
    o.append(stroke("M-7,-39 Q0,-33 7,-39", lighter(tc, .6), 2.2))             # collar
    o.append(heart(0, -27, 5, lighter(tc, .55)))                                # a little heart on the shirt
    if arms is None:
        for sgn in (-1, 1):
            o.append(flat(E(sgn * 18, -28, 5, 10, rot=sgn * 12).intersection(body.buffer(1)), darker(tc, .1)))
    else:
        for sgn in (-1, 1):
            up = (arms == "up") or (arms == "brush" and sgn == 1)
            if arms == "head":
                hx, hy = sgn * 20, HEAD_Y - 24
            else:
                a = -60 if up else 25
                hx, hy = sgn * 19 + sgn * 14 * math.cos(math.radians(a)), -36 + 15 * math.sin(math.radians(a))
            arm = LineString([(sgn * 17, -36), (hx, hy)]).buffer(5, cap_style=1)
            o.append(paint(arm, tc))
            o.append(paint(E(hx, hy, 6), sc))
            if sgn == 1 and hold:
                o.append(f'<g transform="translate({hx:.1f} {hy:.1f})">{hold}</g>')
    o.append(f'<g transform="rotate({rot} 0 -42)">' + doll_head(hair, skin, mood, open_mouth, look) + "</g>")
    return "".join(o)


def puppy(mood="smile", face=-1, sleep=False, hold="", wag=True):
    """The block-wood puppy, facing left (face=-1) or right. Feet at y = 0."""
    f = face
    body_c, spot_c, ear_c = "#F6E3C4", "#D3A273", "#C98F5E"
    o = []
    if sleep:
        o.append(paint(R(-24, -20, 48, 20, 10), body_c))
        hx = 22 * f
        o.append(paint(E(hx, -17, 17, 14), body_c, bevel=1.3))
        o.append(paint(E(hx + 13 * f, -14, 7, 11, rot=25 * f), ear_c))
        o.append(flat(E(hx + 7 * f, -12, 7, 5), "#FFF7EC") + flat(E(hx + 10 * f, -14, 2.6, 2.1), DARK))
        o.append(sleep_eye(hx - 2 * f, -21, 3.4))
        o.append(cheeks(hx, -14, 11, 2.6))
        o.append(flat(E(-22, -24, 7, 4, rot=-15), body_c))
        return "".join(o)
    for lx in (-16, 6):
        o.append(paint(R(lx, -12, 11, 12, 5), lighter(body_c, .2)))
    tail = LineString([(26 * -f, -24), (36 * -f, -38)]).buffer(4.2, cap_style=1)
    o.append(paint(tail, body_c))
    if wag:
        o.append(stroke(f"M{40 * -f},-44 q{-4 * -f},-6 {2 * -f},-9 M{44 * -f},-36 q{6 * -f},-3 {8 * -f},2", "#B9A58C", 1.4, op=.8))
    o.append(paint(R(-24, -34, 48, 26, 12), body_c))
    o.append(flat(E(6 * -f, -26, 9, 7), spot_c))
    o.append(paint(E(22 * f, -46, 20, 18), body_c, bevel=1.3))
    o.append(paint(E(37 * f, -38, 7, 13, rot=25 * f), ear_c))
    o.append(flat(E(30 * f, -42, 8, 6), "#FFF7EC") + flat(E(28 * f, -50, 8, 7), spot_c))
    o.append(flat(E(34 * f, -45, 3, 2.5), DARK))
    if mood == "happy":
        o.append(happy_eye(14 * f, -50, 3.4) + happy_eye(28 * f, -52, 2.4))
        o.append(flat(E(32 * f, -36, 3, 4), "#F08A9A"))
    else:
        o.append(eye(14 * f, -50, 4.2) + eye(29 * f, -51, 2.8))
    o.append(stroke(f"M{30 * f - 3},-38 Q{30 * f},-35 {30 * f + 3},-38", DARK, 1.5))
    o.append(cheeks(16 * f, -42, 7, 2.6))
    if hold:
        o.append(f'<g transform="translate({38 * f:.1f} -30)">{hold}</g>')
    return "".join(o)


def kitten():
    o = [paint(E(0, -14, 16, 14), "#C9C2B8", bevel=1.2)]
    for sgn in (-1, 1):
        o.append(paint(P([(sgn * 6, -24), (sgn * 15, -36), (sgn * 16, -20)]).buffer(1.5), "#C9C2B8"))
    o.append(flat(E(0, -9, 5, 3.5), "#FBEFDD") + flat(E(0, -11, 1.8, 1.4), "#E0828E"))
    o.append(eye(-6, -16, 3.2) + eye(6, -16, 3.2))
    o.append(stroke("M-9,-10 L-16,-12 M-9,-8 L-16,-7 M9,-10 L16,-12 M9,-8 L16,-7", DARK, 1.2))
    return "".join(o)


def bunny():
    o = [paint(E(0, -12, 15, 13), WHITE, bevel=1.2)]
    for sgn in (-1, 1):
        o.append(paint(E(sgn * 7, -34, 5, 13, rot=sgn * 8), WHITE))
        o.append(flat(E(sgn * 7, -34, 2.2, 8, rot=sgn * 8), "#F7C6D2"))
    o.append(eye(-6, -14, 3.2) + eye(6, -14, 3.2))
    o.append(flat(E(0, -9, 2, 1.5), "#E0828E") + stroke("M-3,-6 Q0,-4 3,-6", DARK, 1.3))
    o.append(cheeks(0, -8, 9, 2.6))
    return "".join(o)


def duck():
    o = [paint(E(0, -13, 15, 13), YEL, bevel=1.2)]
    o.append(paint(E(0, -6, 9, 4), ORA))
    o.append(flat(E(0, -27, 5, 4, rot=-20), YEL))
    o.append(eye(-6, -16, 3.2) + eye(6, -16, 3.2))
    o.append(cheeks(0, -10, 10, 2.4))
    return "".join(o)


BUDDIES = [("小狗", lambda: place(6, 4, .6, puppy, "smile", -1)), ("小貓", kitten), ("小兔", bunny), ("小鴨", duck)]


# ================================================================ ICONS (round (0, 0), about 30 units wide)
def i_sun(col=YEL, s=1.0):
    o = [stroke("".join(f"M{12 * s * math.cos(math.radians(a)):.1f},{12 * s * math.sin(math.radians(a)):.1f} "
                        f"L{17 * s * math.cos(math.radians(a)):.1f},{17 * s * math.sin(math.radians(a)):.1f} " for a in range(0, 360, 45)), ORA, 3 * s)]
    o.append(paint(E(0, 0, 10 * s), col))
    o.append(face(0, -1 * s, .55 * s, "happy"))
    return "".join(o)


def i_toothbrush(s=1.0):
    g = f'<g transform="rotate(-35) scale({s})">'
    return g + paint(R(-17, -4.5, 32, 9, 4.5), BLUE) + paint(R(8, -7, 11, 14, 4), WHITE) + stroke("M10,-4 V4 M13.5,-4 V4 M17,-4 V4", "#CFE5F3", 1.3) + '<g transform="rotate(35 -6 0)">' + face(-6, -.5, .42, cheek=False) + "</g></g>"


def i_bowl(s=1.0):
    g = f'<g transform="scale({s})">'
    bowl = E(0, 2, 15, 10).intersection(sbox(-20, 2, 20, 20))
    return g + paint(U(E(-3, -2, 7, 5), E(4, -3, 7, 5), E(0, 0, 10, 4)), WHITE) + paint(U(bowl, R(-15, -1, 30, 5, 2.5)), RED) + stroke("M-6,-14 L-2,-2 M8,-16 L5,-2", WALNUT, 2) + face(0, 7, .55) + "</g>"


def i_backpack(s=1.0):
    g = f'<g transform="scale({s})">'
    return (g + paint(R(-10, -17, 20, 8, 4), darker(GRN, .25)) + paint(R(-13, -13, 26, 30, 8), GRN) + paint(R(-9, 2, 18, 12, 4), lighter(GRN, .45))
            + stroke("M-7,-10 V-4 M7,-10 V-4", darker(GRN, .3), 2.4) + face(0, -4, .5) + "</g>")


def i_ball(s=1.0):
    g = f'<g transform="scale({s})">'
    return g + paint(E(0, 0, 14), RED) + flat(E(0, 0, 14).intersection(sbox(-20, -13, 20, -6)), WHITE) + flat(E(0, 0, 14).intersection(sbox(-20, 7, 20, 13)), WHITE) + face(0, -1, .6) + "</g>"


def i_moon(s=1.0):
    g = f'<g transform="scale({s})">'
    m = E(0, 0, 14).difference(E(6, -3, 11))
    return g + paint(m, YEL) + flat(star_g(3, 9, 6), YEL) + face(-6, 0, .5, "sleepy") + "</g>"


def i_drop(s=1.0, col=BLUE):
    d = P(crs([(0, -16), (9, -2), (10, 6), (0, 14), (-10, 6), (-9, -2)], 8))
    return paint(d.buffer(0), col, sh=2) + f'<ellipse cx="{-4 * s}" cy="{-3 * s}" rx="2" ry="3.5" fill="#FFFFFF" opacity=".7"/>' + face(0, 4, .5, "worry" if False else "smile", cheek=False)


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
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 6.5}" fill="none" stroke="{PINK}" stroke-width="5" opacity=".95"/>')
    ri = r * (.64 if labels else .72)
    for i, (name, fn) in enumerate(TASKS):
        a = math.radians(-90 + 60 * i)
        x, y = cx + ri * math.cos(a), cy + ri * math.sin(a)
        if i == hand and glow:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .3:.1f}" fill="{rg([(0, "#FFF4B0"), (.6, "#FFE26B", .9), (1, "#FFE26B", 0)])}"/>')
        o.append(place(x, y, (r / 95) * isize * (1.18 if i == hand else 1), fn))
        if labels:
            o.append(tx(x, y + r * .22 + 7, name, max(11, r * .11), INK))
        a2 = math.radians(-60 + 60 * i)
        o.append(f'<circle cx="{cx + r * .9 * math.cos(a2):.1f}" cy="{cy + r * .9 * math.sin(a2):.1f}" r="{max(2, r * .03):.1f}" fill="{WALNUT}" opacity=".6"/>')
    ang = -90 + 60 * hand if drag_to is None else drag_to
    a = math.radians(ang)
    L = r * .5
    hand_g = U(LineString([(cx, cy), (cx + L * math.cos(a), cy + L * math.sin(a))]).buffer(max(3, r * .05), cap_style=1),
               P([(cx + (L + r * .1) * math.cos(a), cy + (L + r * .1) * math.sin(a)),
                  (cx + (L - r * .06) * math.cos(a) + r * .09 * math.sin(a), cy + (L - r * .06) * math.sin(a) - r * .09 * math.cos(a)),
                  (cx + (L - r * .06) * math.cos(a) - r * .09 * math.sin(a), cy + (L - r * .06) * math.sin(a) + r * .09 * math.cos(a))]))
    o.append(face(cx, cy + r * .3, r / 60, "sleepy"))
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
    o.append(cat_cushion(-w * .22, -27, .9))
    return "".join(o)


def cat_cushion(cx, cy, s=1.0, col=YEL):
    g = U(E(cx, cy, 11 * s, 9 * s), P([(cx - 9 * s, cy - 5 * s), (cx - 10 * s, cy - 14 * s), (cx - 3 * s, cy - 8 * s)]), P([(cx + 9 * s, cy - 5 * s), (cx + 10 * s, cy - 14 * s), (cx + 3 * s, cy - 8 * s)]))
    return paint(soft(g, 1.2 * s), col, sh=1, grain=.06) + face(cx, cy - 1 * s, .55 * s)


def toybox(open_=True):
    o = [paint(R(-24, -26, 48, 26, 5), ORA)]
    o.append(flat(R(-20, -22, 40, 18, 3), lighter(ORA, .25)))
    o.append(face(0, -13, .7))
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
        o.append(f'<circle cx="{w * .25}" cy="{-h * .7}" r="{h * .17}" fill="{YEL}"/>' + face(w * .25, -h * .72, h * .02, "happy", cheek=False))
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
            for j in range(5):
                o.append(flat(E(sgn * (w / 2 - cw * (.3 + .35 * (j % 2))), -h * .85 + j * h * .18, 2.2, 2.2).intersection(cg), "#FFFFFF", 'opacity=".85"'))
        o.append(paint(R(-w / 2 - 10, -h - 10, w + 20, 6, 3), WALNUT))
    return "".join(o)


def bed(w=96, night=False, blanket=.55, sheet=BLUE):
    o = [paint(R(-w / 2, -44, 10, 44, 4), WOOD2) + paint(R(w / 2 - 10, -34, 10, 34, 4), WOOD2)]
    o.append(paint(R(-w / 2, -20, w, 14, 5), WOOD2))                             # frame
    o.append(paint(R(-w / 2 + 2, -30, w - 4, 12, 5), WHITE))                       # mattress
    o.append(paint(R(-w / 2 + 6, -38, 24, 12, 5), lighter(PINK, .5)))               # pillow
    bl = R(-w / 2 + 2 + (w - 4) * (1 - blanket), -34, (w - 4) * blanket, 16, 6)
    o.append(paint(bl, sheet, grain=.08))
    for i in range(3):
        o.append(flat(star_g(4, -w / 2 + 2 + (w - 4) * (1 - blanket) + 14 + i * 16, -26), lighter(sheet, .5)))
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
    o.append(heart(-8, -52, 4, RED) + flat(star_g(4, -8, -22), YEL) + face(0, -22, .6))
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


# ================================================================ ONE ROOM FILLS THE SCREEN (screens 2, 3, 5)
ROOM_STRIP = [("陽台", lambda: place(0, 10, .5, plant)), ("廚房", lambda: place(0, 13, .42, fridge)), ("客廳", lambda: place(0, 9, .3, sofa, 84, TEAL)),
              ("房間", lambda: place(0, 10, .32, bed, 96)), ("廁所", lambda: place(0, 12, .5, toilet)), ("門口", lambda: place(0, 14, .38, door))]


def room_strip(y=772, selected="客廳", glow=None, scale=1.0, cx=195, labels=True):
    """The row of little room buttons at the bottom: tap one to go there; the one to go to glows and bounces."""
    o = []
    gap = 60 * scale
    r = 22 * scale
    x0 = cx - 2.5 * gap
    for i, (name, fn) in enumerate(ROOM_STRIP):
        x = x0 + i * gap
        yy = y - (8 * scale if name == glow else 0)
        if name == glow:
            o.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r * 1.5:.1f}" fill="{rg([(0, "#FFF4B0"), (.55, "#FFE26B", .9), (1, "#FFE26B", 0)])}"/>')
        o.append(wbtn(x, yy, r, CREAM if name == selected else WHITE, sh=1 if name != glow else 2))
        o.append(place(x, yy, scale, fn))
        if name == selected:
            o.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r + 3.5 * scale:.1f}" fill="none" stroke="{TEAL}" stroke-width="{3.5 * scale:.1f}"/>')
        if name == glow:
            o.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r + 3.5 * scale:.1f}" fill="none" stroke="{YEL}" stroke-width="{3.5 * scale:.1f}"/>')
            o.append(sparkle(x + r * .9, yy - r * .95, 6 * scale, YEL) + sparkle(x - r * 1.05, yy - r * .5, 4 * scale, PINK))
        if labels:
            o.append(tx(x, yy + r + 14 * scale, name, 10.5 * scale, INK if name in (selected, glow) else SOFT))
    return "".join(o)


def edge_arrow(x, y, label, direction=-1):
    """A wooden tab at the screen's edge: tap to walk to the next room."""
    o = [paint(R(x - 22, y - 26, 44, 52, 14), WOOD2, sh=2)]
    o.append(i_arrow(x + direction * 2, y - 4, 1.0, WHITE, 180 if direction < 0 else 0))
    o.append(tx(x, y + 20, label, 11, INK))
    return "".join(o)


def living_room_big(x=10, y=236, w=370, h=530, sky="morning", rain=False, glow_stairs=False, dimmed=False):
    """The living room filling the screen: the frame, the wall, the furniture and the stairs on the right."""
    o = [wood(R(x, y, w, h, 16), WOOD, grain=.45, sh=3)]
    fy = y + h - 62
    o.append(f'<rect x="{x + 10}" y="{y + 10}" width="{w - 20}" height="{h - 20}" rx="10" fill="{ROOM_WALL["living"]}"/>')
    o.append(f'<rect x="{x + 10}" y="{y + 10}" width="{w - 20}" height="{h - 20}" rx="10" fill="#000" opacity=".05" filter="{wood_f(.5, 0, .02)}"/>')
    o.append(f'<rect x="{x + 10}" y="{fy}" width="{w - 20}" height="{h - 10 - (fy - y)}" fill="{WOOD2}" filter="{wood_f(.5, 0, .05)}"/>')
    o.append(stroke(f"M{x + 10},{fy + 16} H{x + w - 10} M{x + 10},{fy + 36} H{x + w - 10}", WALNUT, 1, op=.3))
    o.append(place(x + w * .5, fy - 2, 1.5, rug, 120, PINK))
    o.append(place(x + 96, y + 190, 1.5, window, 64, 50, sky, False, 0, rain))
    o.append(place(x + 238, y + 118, 1.25, picture_frame, LILAC))
    o.append(place(x + 302, y + 182, 1.2, lambda: paint(R(-16, -2, 32, 4, 2), WOOD2) + place(0, -2, 1.0, phone)))
    o.append(place(x + 130, fy, 1.5, sofa, 84, TEAL))
    o.append(place(x + 36, fy, 1.5, lamp))
    o.append(place(x + 54, fy, 1.2, toybox))
    o.append(place(x + 60, y + 92, 1.1, lambda: paint(R(-30, -2, 60, 5, 2.5), WOOD2) + place(-14, -2, .7, plant) + place(12, -2, .8, storybook)))
    o.append(heart(x + 300, y + 70, 7, PINK) + flat(star_g(7, x + 330, y + 96), YEL) + sparkle(x + 150, y + 60, 6, YEL))
    # the stairs up to 房間 and 廁所
    sx = x + w - 10 - 70
    if glow_stairs:
        o.append(f'<rect x="{sx - 8}" y="{fy - 82}" width="86" height="90" rx="12" fill="#FFE26B" opacity=".75" filter="{blur(8)}"/>')
    o.append(f'<rect x="{sx}" y="{y + 10}" width="70" height="{fy - y - 10}" fill="#000" opacity=".06"/>')
    o.append(place(sx, fy, 1.4, stairs, True, 5, 10))
    o.append(paint(R(sx + 66, fy - 110, 5, 110, 2.5), WOOD2, sh=0) + paint(R(sx - 2, fy - 90, 74, 5, 2.5), WOOD2, sh=0))
    o.append(tx(sx + 36, fy - 100, "上樓", 11, INK))
    if glow_stairs:
        o.append(place(sx + 34, fy - 130, 1.0, lambda: f'<circle r="16" fill="{YEL}" opacity=".95"/>' + i_arrow(0, 0, .8, "#FFFFFF", -90)))
    if dimmed:
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#2A1E16" opacity=".55"/>')
    return "".join(o)


def home_frame(hand=1, sky="morning"):
    o = [wallpaper()]
    o.append(lock_chip(14, 14) + sticker_btn(322, 30) + day_chip(14, 56, "星期三", "sun", 92))
    o.append(clock(195, 124, 92, hand=hand))
    return o


def screen_home():
    o = home_frame(1)
    fy = 236 + 530 - 62
    o.append(living_room_big(glow_stairs=True))
    o.append(place(168, fy, 2.2, peg_doll, 0, 0, 0, "smile", look=2))
    o.append(place(258, fy, 1.45, puppy, "smile", 1))
    o.append(say(130, 396, 206, 52, "小明，該刷牙囉！", "down", 190, 16))
    o.append(edge_arrow(30, 300, "廚房", -1) + edge_arrow(360, 300, "門口", 1))
    o.append(heart(236, 560, 8, PINK) + sparkle(112, 540, 7, YEL) + sparkle(322, 520, 6, PINK) + sparkle(292, 60, 7, YEL, .9))
    o.append(room_strip(790, "客廳", "廁所"))
    return page("".join(o), "#F6EEDF")


# ================================================================ SCREEN 3: turning the clock
def screen_clock():
    o = home_frame(1)
    fy = 236 + 530 - 62
    o.append(living_room_big())
    o.append(place(168, fy, 2.2, peg_doll, 0, 0, 0, "smile") + place(258, fy, 1.45, puppy, "smile", 1))
    o.append(room_strip(790, "客廳", None))
    o.append(f'<rect width="{W}" height="{H}" fill="#2A1E16" opacity=".55"/>')
    cx, cy, r = 195, 300, 150
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 30}" fill="#FFF3C4" opacity=".35" filter="{blur(14)}"/>')
    o.append(clock(cx, cy, r, hand=2, glow=True, labels=True, isize=1.05, drag_to=12))
    a0, a1 = math.radians(-30), math.radians(30)
    rr = r * .5 + 24
    o.append(f'<path d="M{cx + rr * math.cos(a0):.1f},{cy + rr * math.sin(a0):.1f} A{rr},{rr} 0 0 1 {cx + rr * math.cos(a1):.1f},{cy + rr * math.sin(a1):.1f}" '
             f'fill="none" stroke="{WHITE}" stroke-width="4" stroke-dasharray="6 7" stroke-linecap="round" opacity=".9"/>')
    o.append(i_arrow(cx + rr * math.cos(a1) - 2, cy + rr * math.sin(a1) + 10, .8, WHITE, 100))
    o.append(finger(cx + (r * .5 + 10) * math.cos(math.radians(12)), cy + (r * .5 + 10) * math.sin(math.radians(12)), -20))
    o.append(paint(R(60, 486, 270, 92, 20), WHITE, sh=2, grain=.05))
    o.append(place(118, 566, .72, window, 60, 46, "morning") + tx(118, 506, "早上", 12.5, SOFT))
    o.append(i_arrow(195, 536, 1.1, WOOD2))
    o.append(place(272, 566, .72, window, 60, 46, "noon") + tx(272, 506, "中午", 12.5, SOFT))
    o.append(say(40, 606, 310, 56, "要跳到吃早餐嗎？", "up", 195, 19))
    o.append(wbtn(140, 724, 36, GRN, i_check(140, 724, 1.5, "#FFFFFF")) + tx(140, 782, "好", 15, WHITE))
    o.append(wbtn(250, 724, 36, GREY, stroke("M238,712 L262,736 M262,712 L238,736", "#FFFFFF", 5)) + tx(250, 782, "不要", 15, WHITE))
    return page("".join(o), "#F6EEDF")


# ================================================================ SCREEN 5: "I need to pee!"
def screen_pee():
    o = home_frame(4, "noon")
    fy = 236 + 530 - 62
    o.append(living_room_big(sky="noon", glow_stairs=True))
    o.append(footprints([(214, fy - 6), (262, fy - 6), (300, fy - 10), (324, fy - 30), (350, fy - 56)], ORA, 7, 1.2, glow=True))
    o.append(place(150, fy, 2.2, peg_doll, 0, 0, 0, "worry", squirm=True))
    o.append(stroke("M72,596 Q62,612 72,628 M232,596 Q242,612 232,628", "#8A7A6A", 3))
    o.append(place(214, fy - 222, 1.9, i_drop, 1.0, BLUE))
    o.append(place(250, fy, 1.4, puppy, "smile", -1))
    o.append(say(120, 396, 176, 52, "我想尿尿！", "down", 170, 17))
    o.append(edge_arrow(30, 300, "廚房", -1) + edge_arrow(360, 300, "門口", 1))
    o.append(room_strip(790, "客廳", "廁所"))
    return page("".join(o), "#F6EEDF")


# ================================================================ SCREEN 1: name and character
def sign_title(cx, cy, text, w=None, size=24):
    w = w or size * len(text) + 50
    return wood(R(cx - w / 2, cy - 24, w, 48, 12), WOOD2, grain=.42, sh=2) + wtx(cx, cy + size * .36, text, size, darker(WOOD2, .5), col=WHITE)


def choice_ring(cx, cy, r):
    return f'<circle cx="{cx}" cy="{cy}" r="{r + 5}" fill="none" stroke="{YEL}" stroke-width="4"/>' + i_check(cx + r * .75, cy - r * .75, .55, "#FFFFFF").replace("<path", f'<circle cx="{cx + r * .75}" cy="{cy - r * .75}" r="9" fill="{GRN}"/><path', 1)


def screen_name():
    o = [wallpaper(base="#FBF1E2", col="#F2DFC0")]
    o.append(sign_title(195, 46, "你是誰呀？", 230, 24))
    # the name box
    o.append(wood(R(24, 84, 342, 54, 14), WOOD2, grain=.4, sh=2))
    o.append(f'<rect x="32" y="92" width="326" height="38" rx="10" fill="{WHITE}"/>')
    o.append(tx(48, 118, "小寶", 19, "#B9AE9F", "start") + '<rect x="92" y="100" width="2" height="22" fill="#4A3728"/>')
    o.append(tx(350, 117, "家長幫忙打名字", 12, SOFT, "end"))
    # the stage with the doll and the buddy
    o.append(wood(E(195, 342, 150, 16), WOOD2, grain=.45, sh=2))
    o.append(f'<circle cx="195" cy="236" r="110" fill="{rg([(0, "#FFF6DA", .9), (1, "#FFF6DA", 0)])}"/>')
    o.append(place(168, 338, 1.5, peg_doll, 0, 0, 0, "happy", "up"))
    o.append(place(262, 338, 1.0, puppy, "happy", -1))
    rows = [("髮型", 400, [(i, lambda i=i: doll_head(i, 0)) for i in range(4)], 0, 24, 64),
            ("膚色", 466, [(i, lambda i=i: paint(E(0, 0, 15), SKINS[i], sh=0)) for i in range(4)], 0, 24, 64),
            ("衣服", 532, [(i, lambda i=i: place(0, 0, .95, i_shirt, 1.0, SHIRTS[i])) for i in range(6)], 0, 22, 54)]
    for label, y, items, sel, r, gap in rows:
        o.append(tx(24, y - r - 10, label, 13, SOFT, "start"))
        n = len(items)
        x0 = 195 - (n - 1) * gap / 2
        for i, fn in items:
            x = x0 + i * gap
            o.append(wbtn(x, y, r, WHITE))
            if label == "髮型":
                o.append(place(x, y + 30, .48, fn))
            else:
                o.append(place(x, y, 1.0, fn))
            if i == sel:
                o.append(choice_ring(x, y, r))
    o.append(tx(24, 578, "小夥伴", 13, SOFT, "start"))
    for i, (name, fn) in enumerate(BUDDIES):
        x = 72 + i * 82
        o.append(wbtn(x, 626, 30, WHITE))
        o.append(place(x, 646, .9, fn))
        if i == 0:
            o.append(choice_ring(x, 626, 30))
        o.append(tx(x, 676, name, 12.5, INK))
    o.append(wpill(195, 752, 220, 64, GRN, "開始", 26, i_arrow(262, 752, 1.1, "#FFFFFF"), tdx=-18))
    return page("".join(o), "#FBF1E2")


# ================================================================ SCREEN 4: brushing teeth
def tiles(x, y, w, h, base="#E4F3F9", line="#CFE6EF", size=36):
    k = "tl" + _h(base, line, size)
    D.add(k, f'<pattern id="{k}" width="{size}" height="{size}" patternUnits="userSpaceOnUse"><rect width="{size}" height="{size}" fill="{base}"/>'
             f'<rect x="1.5" y="1.5" width="{size - 3}" height="{size - 3}" rx="3" fill="none" stroke="{line}" stroke-width="2"/></pattern>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{k})"/>'


def toothbrush(L=120, col=BLUE, paste=True):
    o = [paint(R(-L / 2, -9, L, 18, 9), col)]
    o.append(paint(R(L / 2 - 34, -15, 34, 30, 7), WHITE))
    for i in range(4):
        o.append(stroke(f"M{L / 2 - 28 + i * 7.5},-10 V10", "#CFE5F3", 2.2))
    if paste:
        o.append(paint(E(L / 2 - 17, -20, 15, 6), "#BDEBD8", sh=0) + flat(E(L / 2 - 17, -20, 9, 2.4), "#F2FFFA"))
    return "".join(o)


def toothpaste():
    return paint(P([(-10, -34), (10, -34), (12, 0), (-12, 0)]).buffer(2, join_style=1), RED) + flat(R(-8, -22, 16, 10, 2), WHITE) + paint(R(-6, -44, 12, 10, 2), WHITE)


def cup(col=YEL):
    return paint(P([(-12, -32), (12, -32), (10, 0), (-10, 0)]).buffer(2, join_style=1), col) + flat(R(-12, -32, 24, 6, 2), lighter(col, .4))


def big_face(cx, cy, hair=0, skin=0, mouth_open=True):
    s = 2.6
    o = [f'<g transform="translate({cx} {cy}) scale({s})">']
    o.append(paint(E(0, 0, 40, 42), SKINS[skin], bevel=1.4))
    cap = E(0, -4, 43, 42).intersection(sbox(-60, -80, 60, -20))
    bangs = U(E(-22, -26, 15, 10), E(0, -30, 16, 10), E(22, -26, 15, 10)).intersection(sbox(-60, -80, 60, -14))
    o.append(paint(U(cap, bangs), HAIRS[hair], grain=.1))
    o.append(eye(-15, -8, 5) + eye(15, -8, 5))
    o.append(cheeks(0, 6, 26, 6))
    if mouth_open:
        o.append(paint(E(0, 24, 30, 20), "#C9546A", sh=0))
        o.append(flat(E(0, 34, 18, 7), "#F08A9A"))
        for i in range(6):
            x = -24 + i * 8.6
            o.append(paint(R(x, 8, 7.6, 11, 3), "#FFFFFF", sh=0))
            o.append(paint(R(x, 33, 7.6, 8, 3), "#FFFFFF", sh=0))
    o.append("</g>")
    return "".join(o)


def screen_brush():
    o = [tiles(0, 0, W, 760)]
    o.append(f'<rect x="0" y="760" width="{W}" height="84" fill="{WOOD2}" filter="{wood_f(.5, 0, .05)}"/>')
    o.append(topbar("刷刷刷，上面也要刷！", 1))
    o.append(progress_bubbles(195, 176, 6, 2, 10, 30))
    # the mirror and the puppy brushing beside it
    o.append(wood(R(28, 206, 96, 118, 10), WOOD2, grain=.4, sh=2) + f'<rect x="36" y="214" width="80" height="102" rx="7" fill="{lg([(0, "#F2FBFF"), (1, "#C9E6F3")])}"/>')
    o.append(stroke("M44,228 L58,222 M44,240 L68,228", "#FFFFFF", 3, op=.8))
    o.append(paint(R(10, 400, 100, 14, 6), WOOD2) + paint(R(20, 414, 10, 40, 4), WOOD2) + paint(R(90, 414, 10, 40, 4), WOOD2))
    o.append(place(66, 400, 1.0, puppy, "happy", 1, hold=place(14, -12, .34, toothbrush, 120, PINK, False, rot=-50)))
    # the big face and the brush
    o.append(big_face(225, 470, 0, 0))
    o.append(place(272, 530, .95, toothbrush, 120, BLUE, True, rot=210))
    o.append(bubbles(232, 476, 10, 4, 46, 11))
    o.append(bubbles(300, 440, 5, 9, 26, 7))
    o.append(finger(292, 542, -30))
    # the sink with the paste and the cup
    o.append(place(195, 790, 1.0, lambda: paint(E(0, -30, 150, 22), WHITE, sh=2) + flat(E(0, -30, 110, 12), SKY) + stroke("M0,-44 V-62 Q0,-70 10,-70", GREY, 5)))
    o.append(place(70, 762, 1.0, toothpaste))
    o.append(place(320, 762, 1.0, cup, YEL))
    return page("".join(o), "#E4F3F9")


# ================================================================ SCREEN 6: mealtime
def rice_ball():
    return paint(U(E(0, -8, 16, 11), E(-6, -14, 8, 7), E(6, -14, 8, 7)), WHITE) + flat(E(0, -4, 12, 5), WHITE)


def broccoli():
    return paint(R(-4, -10, 8, 12, 3), lighter(GRN, .3)) + paint(U(E(-9, -16, 8, 7), E(0, -20, 10, 8), E(9, -16, 8, 7)), darker(GRN, .18))


def drumstick():
    return paint(LineString([(6, -2), (16, -14)]).buffer(3.5), WHITE) + paint(E(16, -16, 5), WHITE) + paint(E(-4, 2, 15, 11, rot=-25), "#D98A4A") + flat(E(-8, -1, 5, 3, rot=-25), lighter("#D98A4A", .3))


def apple():
    return paint(U(E(-6, 0, 11, 11), E(6, 0, 11, 11), E(0, 3, 12, 10)), RED) + stroke("M0,-10 Q1,-16 4,-18", WALNUT, 2.4) + paint(E(5, -15, 5, 2.6, rot=-30), GRN, sh=0)


def spoon():
    return paint(U(E(0, -26, 8, 11), R(-2.5, -16, 5, 42, 2.5)), GREY) + flat(E(0, -26, 5, 7), lighter(GREY, .4))


def plate_slot(cx, cy, name, icon, filled=None):
    o = [f'<circle cx="{cx}" cy="{cy}" r="29" fill="{CREAM}" stroke="#D9B98A" stroke-width="2" stroke-dasharray="5 4"/>']
    if filled:
        o.append(place(cx, cy + 14, 1.2, filled))
    else:
        o.append(f'<g opacity=".4">{place(cx, cy + 10, .9, icon)}</g>')
    o.append(tx(cx, cy + 42, name, 12.5, SOFT))
    return "".join(o)


def screen_meal():
    o = [f'<rect width="{W}" height="{H}" fill="{ROOM_WALL["kitchen"]}"/>']
    o.append(f'<rect x="0" y="770" width="{W}" height="74" fill="{WOOD2}" filter="{wood_f(.5, 0, .05)}"/>')
    o.append(topbar("先放飯，再放青菜！", 2))
    o.append(place(62, 296, 1.25, fridge))
    o.append(place(326, 282, 1.05, window, 60, 48, "morning"))
    # the child behind the table
    o.append(place(195, 330, 1.1, peg_doll, 0, 0, 0, "smile", "up", open_mouth=True))
    # the table top seen from a little above
    o.append(wood(R(12, 300, 366, 330, 26), WOOD2, grain=.45, sh=3))
    o.append(f'<rect x="20" y="308" width="350" height="314" rx="22" fill="{WOOD}" opacity=".55"/>')
    o.append(paint(E(195, 462, 116, 110), WHITE, sh=2, grain=.04, bevel=1.5))
    o.append(f'<ellipse cx="195" cy="462" rx="104" ry="98" fill="none" stroke="{SKY}" stroke-width="3"/>')
    o.append(plate_slot(150, 418, "飯", rice_ball, rice_ball) + plate_slot(240, 418, "菜", broccoli) + plate_slot(150, 500, "肉", drumstick) + plate_slot(240, 500, "水果", apple))
    o.append(place(62, 596, 1.2, drumstick) + place(330, 596, 1.2, apple))
    o.append(place(300, 352, 1.2, broccoli) + finger(312, 358, -30))
    o.append(place(338, 500, 1.0, spoon, rot=20))
    o.append(progress_bubbles(195, 650, 4, 1, 9, 26).replace("#9CD3F5", "#FFD56B").replace("#CDEBFA", "#FFF0C2").replace("#7FB8DA", "#E0A832"))
    # the puppy with its own bowl
    o.append(place(70, 770, 1.0, puppy, "happy", 1))
    o.append(place(150, 770, 1.6, pet_bowl))
    o.append(heart(150, 722, 6, PINK) + sparkle(172, 712, 5, YEL))
    o.append(place(320, 770, 1.0, lambda: paint(R(-30, -30, 60, 10, 5), WOOD2) + paint(R(-24, -20, 10, 20, 4), WOOD2) + paint(R(14, -20, 10, 20, 4), WOOD2)))
    return page("".join(o), ROOM_WALL["kitchen"])


# ================================================================ SCREEN 7: bedtime
def mini_house(x, y, s, **kw):
    """The whole house drawn small inside a card, for the night inset."""
    return f'<g transform="translate({x} {y}) scale({s})">' + place(0, 0, 1.0, house, **kw) + "</g>"


def storybook():
    return paint(R(-16, -22, 32, 22, 3), TEAL) + flat(R(-12, -18, 24, 14, 2), WHITE) + flat(E(-4, -11, 5, 3.5), YEL) + flat(E(5, -13, 3), PINK)


def screen_sleep():
    night_wall = mixc(ROOM_WALL["bed"], "#2A3058", .55)
    o = [f'<rect width="{W}" height="{H}" fill="{night_wall}"/>']
    o.append(f'<rect x="0" y="600" width="{W}" height="244" fill="{darker(WOOD2, .45)}" filter="{wood_f(.5, 0, .05)}"/>')
    o.append(topbar("晚安，小明。", 5))
    o.append(place(300, 330, 1.3, window, 70, 60, "night", True, .5))
    o.append(f'<circle cx="70" cy="470" r="130" fill="{rg([(0, "#FFE9A8", .5), (1, "#FFE9A8", 0)])}"/>')
    o.append(paint(R(26, 530, 90, 70, 8), WOOD2))                                   # the bedside table
    o.append(place(52, 530, 1.4, nightlight, True))
    o.append(place(96, 530, 1.1, storybook, rot=-6))
    o.append(place(205, 600, 2.3, bed, 110, True, .68, BLUE))
    o.append(place(122, 570, 1.15, doll_head, 0, 0, "sleep"))
    o.append(finger(168, 528, -35))
    o.append(stroke("M150,506 Q168,500 186,508", WHITE, 3, (6, 6), .8) + i_arrow(142, 508, .7, WHITE, 180))
    o.append(place(296, 528, .95, puppy, "smile", -1, sleep=True))
    o.append(tx(322, 486, "z", 14, WHITE) + tx(334, 470, "Z", 18, WHITE))
    o.append(tx(150, 452, "z", 14, "#FFF6DA") + tx(162, 436, "Z", 18, "#FFF6DA"))
    o.append(sparkle(250, 240, 5, "#FFF6DA", .9) + sparkle(120, 300, 4, "#FFF6DA", .8) + sparkle(360, 420, 4, "#FFF6DA", .8))
    # the rest of the house is dark: a small card at the bottom right
    o.append(paint(R(222, 636, 156, 170, 12), "#1E2440", sh=2, grain=.05))
    o.append(f'<g clip-path="{clip(dpts(rrect(228, 642, 144, 150, 9)))}"><g transform="translate(253 596) scale(.24)">'
             + house(night=True, lit="bed", signs=False) + "</g></g>")
    o.append(tx(300, 824, "", 10))
    return page("".join(o), night_wall)


# ================================================================ SCREEN 8: the sticker chart
TODAY = [("起床", i_sun), ("刷牙", i_toothbrush), ("換衣服", i_shirt), ("吃早餐", i_bowl), ("上學", i_backpack), ("洗手", i_hands),
         ("吃午餐", i_bowl), ("睡午覺", i_moon), ("出去玩", i_ball), ("收玩具", i_toybox), ("洗澡", i_bath), ("睡覺", i_moon)]
DONE = {0: ("star", YEL, -12), 1: ("heart", PINK, 8), 3: ("flower", LILAC, -6)}


def sticker(kind, cx, cy, col, rot=0.0):
    o = [f'<g transform="rotate({rot} {cx} {cy})">', f'<circle cx="{cx}" cy="{cy}" r="27" fill="#FFFFFF" opacity=".95"/>']
    if kind == "star":
        o.append(paint(star_g(19, cx, cy), col, sh=1) + face(cx, cy + 1, .7))
    elif kind == "heart":
        o.append(paint(heart_pts(cx, cy + 2, 20), col, sh=1) + face(cx, cy - 1, .7))
    else:
        o.append(place(cx, cy, 2.0, i_flower) + face(cx, cy - 1, .5, cheek=False))
    o.append(sparkle(cx + 20, cy - 18, 5, YEL) + sparkle(cx - 22, cy + 14, 4, PINK))
    return "".join(o) + "</g>"


def screen_chart():
    o = [wallpaper(base="#FBF1E2", col="#F2DFC0")]
    o.append(home_btn(36, 44))
    o.append(sign_title(215, 46, "好習慣貼紙表", 236, 22))
    o.append(wood(R(20, 92, 350, 520, 18), WOOD2, grain=.42, sh=3))
    o.append(stroke("M34,106 H356", lighter(WOOD2, .5), 2, op=.6))
    cw, ch, gap = 106, 116, 8
    for i, (name, fn) in enumerate(TODAY):
        r_, c_ = divmod(i, 3)
        x, y = 29 + c_ * (cw + gap), 102 + r_ * (ch + gap)
        o.append(paint(R(x, y, cw, ch, 12), CREAM, sh=0, grain=.06))
        o.append(f'<g opacity=".{"95" if i in DONE else "45"}">{place(x + cw / 2, y + 46, 1.1, fn)}</g>')
        o.append(tx(x + cw / 2, y + ch - 14, name, 13, INK if i in DONE else SOFT))
        if i in DONE:
            kind, col, rot = DONE[i]
            o.append(sticker(kind, x + cw / 2, y + 46, col, rot))
        else:
            o.append(f'<circle cx="{x + cw / 2}" cy="{y + 46}" r="27" fill="none" stroke="#D9B98A" stroke-width="1.6" stroke-dasharray="4 3.5"/>')
    o.append(tx(195, 636, "今天貼了 3 張，加油！", 14, SOFT))
    # the puppy's reward
    o.append(place(70, 802, 1.1, puppy, "happy", 1, hold=place(2, -8, 1.0, i_flowerpot)))
    o.append(say(118, 686, 256, 74, "", "left", 740, speaker=False))
    o.append(tx(246, 716, "今天做完了，", 15, INK) + tx(246, 742, "小狗送你一盆小花！", 15, INK))
    o.append(heart(300, 650, 7, PINK) + sparkle(330, 660, 6, YEL) + sparkle(60, 660, 5, PINK))
    return page("".join(o), "#FBF1E2")


# ================================================================ SCREEN 9: parents' settings
P_BG, P_TXT, P_SUB, P_ACC = "#F6F2EC", "#3D3A40", "#8A8590", "#3FA58E"


def section(y, h, title=None):
    o = f'<rect x="16" y="{y}" width="358" height="{h}" rx="16" fill="#FFFFFF" stroke="#ECE6DE" stroke-width="1.2"/>'
    if title:
        o += tx(30, y + 24, title, 13.5, P_SUB, "start")
    return o


def segmented(y, labels, sel, x=30, w=330, h=34):
    n = len(labels)
    sw = w / n
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#EFECE7"/>'
    for i, lb in enumerate(labels):
        if i == sel:
            o += f'<rect x="{x + i * sw + 3:.1f}" y="{y + 3}" width="{sw - 6:.1f}" height="{h - 6}" rx="8" fill="{P_ACC}"/>'
        o += tx(x + i * sw + sw / 2, y + h / 2 + 5, lb, 14.5, "#FFFFFF" if i == sel else P_TXT)
    return o


def toggle(x, y, on, s=1.0):
    c = P_ACC if on else "#D7D3CD"
    kx = x + 30 * s if on else x + 12 * s
    return f'<rect x="{x}" y="{y}" width="{42 * s}" height="{24 * s}" rx="{12 * s}" fill="{c}"/><circle cx="{kx}" cy="{y + 12 * s}" r="{9 * s}" fill="#FFFFFF"/>'


def screen_parents():
    o = [f'<rect width="{W}" height="{H}" fill="{P_BG}"/>']
    o.append(tx(195, 44, "家長模式", 20, P_TXT))
    o.append('<circle cx="350" cy="38" r="18" fill="#E7E2DB"/>' + '<path d="M343,31 L357,45 M357,31 L343,45" stroke="#5C5864" stroke-width="2.4" stroke-linecap="round"/>')
    # name and character
    o.append(section(64, 78, "名字和角色"))
    o.append(f'<circle cx="56" cy="110" r="22" fill="#EFE8DF"/>' + place(56, 128, .42, lambda: peg_doll(0, 0, 0, "smile")))
    o.append(tx(92, 106, "小明", 17, P_TXT, "start") + tx(92, 126, "小狗跟著", 12.5, P_SUB, "start"))
    o.append(f'<rect x="222" y="94" width="64" height="30" rx="15" fill="#EFECE7"/>' + tx(254, 114, "改名字", 12.5, P_TXT))
    o.append(f'<rect x="292" y="94" width="68" height="30" rx="15" fill="#EFECE7"/>' + tx(326, 114, "改角色", 12.5, P_TXT))
    # age
    o.append(section(150, 76, "年齡"))
    o.append(segmented(180, ("2～3 歲（一次一件事）", "4～5 歲（自己找房間）"), 0, 30, 330, 34))
    # play time
    o.append(section(234, 76, "每次玩多久"))
    for i, m in enumerate((5, 10, 15, 20, 30)):
        x = 30 + i * 67
        sel = m == 15
        o.append(f'<rect x="{x}" y="264" width="61" height="32" rx="16" fill="{P_ACC if sel else "#FFFFFF"}" stroke="{P_ACC if sel else "#DCD6CE"}" stroke-width="1.5"/>')
        o.append(tx(x + 30.5, 285, f"{m} 分鐘", 13, "#FFFFFF" if sel else P_TXT))
    # real time
    o.append(section(318, 54))
    o.append(tx(30, 340, "時鐘跟著真的時間", 15, P_TXT, "start") + tx(30, 358, "開了以後，早上打開就是起床刷牙", 11.5, P_SUB, "start"))
    o.append(toggle(318, 333, False))
    # routines
    o.append(section(380, 232, "要哪些作息"))
    routines = [("起床", True), ("刷牙洗臉", True), ("換衣服", True), ("吃早餐", True), ("上學", False), ("回家洗手", True), ("吃點心喝水", True),
                ("出去玩", True), ("收玩具", True), ("幫忙做家事", True), ("吃晚餐", True), ("洗澡", True), ("刷牙上廁所", True), ("聽故事睡覺", True)]
    for i, (name, on) in enumerate(routines):
        c_, r_ = divmod(i, 7)
        x, y = 30 + c_ * 172, 404 + r_ * 28
        o.append(tx(x, y + 15, name, 13, P_TXT if on else P_SUB, "start"))
        o.append(toggle(x + 118, y + 2, on, .8))
    o.append(tx(30, 604, "沒有上幼兒園就關掉「上學」，那段會變成在家玩。", 11.5, P_SUB, "start"))
    # sound
    o.append(section(620, 100))
    o.append(tx(30, 648, "聲音和音樂", 14.5, P_TXT, "start") + toggle(318, 632, True))
    o.append(tx(30, 681, "念出來（國語）", 14.5, P_TXT, "start") + toggle(318, 665, True))
    o.append(tx(30, 710, "再說一次英文", 14.5, P_TXT, "start") + toggle(318, 694, False))
    o.append('<path d="M30,660 L360,660 M30,693 L360,693" stroke="#F0ECE6" stroke-width="1.2"/>')
    # today
    o.append(section(728, 104, "今天做完的事"))
    o.append(tx(360, 752, "3 / 12", 13, P_SUB, "end"))
    for i, (name, fn) in enumerate(TODAY):
        x = 40 + i * 28
        done = i in DONE
        o.append(f'<circle cx="{x}" cy="{782}" r="11" fill="{"#DDF3EC" if done else "#F1EEE9"}"/>')
        o.append(f'<g opacity="{1 if done else .35}">{place(x, 782, .55, fn)}</g>')
    o.append(tx(30, 820, "最常跳過：收玩具（這星期 3 次）", 12, P_SUB, "start"))
    return page("".join(o), P_BG)


# ================================================================ SCREEN 10: the little street
def small_house():
    o = [paint(R(-30, -46, 60, 46, 6), CREAM)]
    o.append(paint(P([(-38, -44), (0, -72), (38, -44)]).buffer(3, join_style=1), RED))
    o.append(paint(R(-8, -26, 16, 26, 4), WALNUT, sh=0) + flat(R(-24, -36, 12, 12, 3), SKY) + flat(R(12, -36, 12, 12, 3), SKY))
    return "".join(o)


def building(kind):
    o = []
    if kind == "park":
        o.append(paint(R(-44, -8, 88, 8, 3), GRN))
        for x in (-30, 26):
            o.append(paint(R(x - 4, -40, 8, 34, 3), WOOD2) + paint(U(E(x, -48, 16), E(x - 10, -40, 12), E(x + 10, -40, 12)), GRN))
        o.append(paint(P([(-6, -44), (6, -44), (26, -6), (14, -6)]).buffer(1.5, join_style=1), YEL) + paint(R(-10, -50, 10, 50, 3), WOOD2))
        o.append(heart(0, -58, 4, PINK))
    elif kind == "school":
        o.append(paint(R(-42, -56, 84, 56, 6), YEL))
        o.append(paint(P([(-48, -54), (0, -80), (48, -54)]).buffer(3, join_style=1), ORA))
        o.append(paint(R(-10, -30, 20, 30, 5), RED, sh=0))
        for x in (-30, 18):
            o.append(flat(R(x, -46, 14, 12, 3), SKY))
        o.append(place(0, -64, .45, i_sun) )
    elif kind == "shop":
        o.append(paint(R(-44, -56, 88, 56, 6), SKY))
        o.append(paint(R(-48, -62, 96, 10, 5), TEAL))
        for i in range(6):
            o.append(flat(R(-46 + i * 16, -48, 8, 10, 2), "#FFFFFF" if i % 2 else TEAL))
        o.append(flat(R(-30, -32, 60, 32, 4), "#FFFFFF") + place(0, -14, .6, cart_icon))
        o.append(place(0, -70, .5, apple))
    elif kind == "clinic":
        o.append(paint(R(-40, -56, 80, 56, 6), WHITE))
        o.append(paint(R(-8, -30, 16, 30, 4), SKY, sh=0) + flat(R(-30, -46, 14, 12, 3), SKY) + flat(R(16, -46, 14, 12, 3), SKY))
        o.append(paint(U(R(-5, -78, 10, 24, 2), R(-12, -71, 24, 10, 2)), RED))
    return "".join(o)


def cart_icon(col=GREY):
    return (stroke("M-16,-18 H-10 L-4,2 H12 L16,-10 H-8", darker(col, .35), 2.4) + paint(R(-8, -10, 22, 12, 3), BLUE, sh=0)
            + flat(E(-2, 6, 3), DARK) + flat(E(10, 6, 3), DARK))


def traffic_light(red=True):
    o = [paint(R(-3, -84, 6, 84, 3), GREY)]
    o.append(paint(R(-12, -118, 24, 40, 7), "#5A5A66"))
    o.append(f'<circle cx="0" cy="-108" r="7" fill="{"#FF5C5C" if red else "#6B3B3B"}"/>' + (f'<circle cx="0" cy="-108" r="12" fill="#FF5C5C" opacity=".35" filter="{blur(3)}"/>' if red else ""))
    o.append(f'<circle cx="0" cy="-88" r="7" fill="{"#3B6B45" if red else "#6CE07A"}"/>')
    return "".join(o)


def car(col=BLUE):
    o = [paint(E(-16, 0, 7), "#5A5A66", sh=0) + paint(E(16, 0, 7), "#5A5A66", sh=0)]
    o.append(paint(U(R(-28, -18, 56, 18, 6), R(-16, -30, 32, 16, 7)), col))
    o.append(flat(R(-12, -27, 11, 9, 3), SKY) + flat(R(2, -27, 11, 9, 3), SKY) + face(14, -9, .45, cheek=False))
    return "".join(o)


def screen_street():
    o = [f'<rect width="{W}" height="{H}" fill="#CDEBFA"/>']
    o.append(f'<rect x="0" y="236" width="{W}" height="608" fill="#CDE9B6"/>')
    for cx, cy, w in ((90, 200, 54), (330, 186, 44)):
        o.append(flat(U(E(cx - w * .3, cy + 4, w * .26), E(cx + w * .05, cy - 4, w * .32), E(cx + w * .36, cy + 5, w * .22), R(cx - w * .5, cy, w, w * .26, w * .13)), "#FFFFFF", 'opacity=".9"'))
    o.append(topbar("紅燈停，綠燈走！", 4))
    o.append(day_chip(16, 162, "星期三", "sun", 92))
    o.append(place(236, 186, 1.1, i_sun))
    # the far side: the places you can go
    o.append(f'<rect x="0" y="352" width="{W}" height="36" fill="#E6DED2"/>')
    places_ = [("公園", "park", 54), ("幼兒園", "school", 150), ("超市", "shop", 246), ("診所", "clinic", 340)]
    for name, kind, x in places_:
        o.append(place(x, 352, 1.0, building, kind))
        o.append(room_sign(x - (len(name) * 12 + 14) / 2, 360, name, 12))
    # the road
    o.append(f'<rect x="0" y="388" width="{W}" height="104" fill="#A9A4A8"/>')
    o.append(f'<path d="M0,440 H{W}" stroke="#FFF2C2" stroke-width="3" stroke-dasharray="18 14"/>')
    for i in range(6):
        o.append(f'<rect x="{150 + i * 14}" y="392" width="8" height="96" rx="2" fill="#FFFFFF" opacity=".9"/>')
    o.append(place(258, 492, 1.0, traffic_light, True))
    o.append(place(340, 488, 1.0, car, LILAC))
    # the near side: our house, the child waiting, the bus stop
    o.append(f'<rect x="0" y="492" width="{W}" height="36" fill="#E6DED2"/>')
    o.append(place(70, 690, 1.5, small_house))
    o.append(room_sign(40, 698, "我們家", 12))
    o.append(place(188, 600, 1.0, peg_doll, 0, 0, 0, "smile", "brush"))
    o.append(place(240, 600, .8, puppy, "smile", -1))
    o.append(f'<circle cx="214" cy="526" r="13" fill="#FFFFFF" opacity=".9"/>' + flat(E(214, 526, 8), "#FF5C5C") + tx(214, 531, "", 10))
    o.append(paint(R(300, 560, 70, 10, 5), WOOD2) + paint(R(306, 570, 8, 30, 3), WOOD2) + paint(R(356, 570, 8, 30, 3), WOOD2) + paint(R(300, 540, 70, 20, 6), YEL) + place(335, 550, .45, lambda: car(ORA)))
    o.append(room_sign(312, 606, "娃娃車", 11))
    for x, y in ((320, 700), (350, 760), (300, 800), (160, 790), (40, 560), (230, 740), (120, 820)):
        o.append(place(x, y, .55, i_flower))
    o.append(heart(286, 650, 6, PINK) + sparkle(340, 640, 5, YEL) + sparkle(140, 640, 5, PINK))
    return page("".join(o), "#CDEBFA")


# ================================================================ SCREEN 11: kindergarten
def task_strip(y, items, done, active):
    o = []
    n = len(items)
    gap = 68
    x0 = 195 - (n - 1) * gap / 2
    for i, (name, fn) in enumerate(items):
        x = x0 + i * gap
        if i < n - 1:
            o.append(i_arrow(x + gap / 2, y, .55, WOOD2))
        if i == active:
            o.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{rg([(0, "#FFF4B0"), (.6, "#FFE26B", .9), (1, "#FFE26B", 0)])}"/>')
        o.append(wbtn(x, y, 22, WHITE if i != active else CREAM, sh=1))
        o.append(f'<g opacity="{.5 if i > active else 1}">{place(x, y, .9, fn)}</g>')
        if i < done:
            o.append(f'<circle cx="{x + 16}" cy="{y - 16}" r="9" fill="{GRN}"/>' + i_check(x + 16, y - 16, .55))
        o.append(tx(x, y + 38, name, 11.5, INK if i <= active else SOFT))
    return "".join(o)


def i_wave(s=1.0):
    return place(0, 0, s, lambda: paint(U(E(0, 2, 7, 9), R(-9, -12, 4, 12, 2), R(-4, -15, 4, 15, 2), R(1, -14, 4, 14, 2), R(6, -10, 4, 10, 2)), SKINS[0]) + stroke("M12,-12 l4,-3 M13,-6 l5,0 M11,-16 l2,-4", WALNUT, 1.6))


def i_note(s=1.0):
    return place(0, 0, s, lambda: paint(E(-6, 8, 7, 5, rot=-20), LILAC) + paint(R(-1, -14, 4, 22, 2), LILAC) + paint(P([(1, -14), (12, -8), (12, -2), (1, -8)]), LILAC))


def i_cookie(s=1.0):
    return place(0, 0, s, lambda: paint(E(0, 0, 13), "#E0A96D") + "".join(flat(E(x, y, 2.2), WALNUT) for x, y in ((-5, -4), (4, -6), (6, 4), (-3, 6), (0, 0))))


def i_mat(s=1.0):
    return place(0, 0, s, lambda: paint(R(-14, -4, 28, 12, 5), BLUE) + paint(E(-10, -6, 7, 5), WHITE) + face(-10, -7, .4, "sleepy", False))


def cubby(x, y, mark, col, glow=False):
    o = []
    if glow:
        o.append(f'<rect x="{x - 8}" y="{y - 8}" width="60" height="60" rx="12" fill="#FFE26B" opacity=".8" filter="{blur(5)}"/>')
    o.append(paint(R(x, y, 44, 44, 6), WOOD2, sh=0))
    o.append(flat(R(x + 5, y + 5, 34, 34, 4), CREAM))
    if mark == "star":
        o.append(flat(star_g(9, x + 22, y + 22), col))
    elif mark == "heart":
        o.append(heart(x + 22, y + 24, 9, col))
    elif mark == "circle":
        o.append(flat(E(x + 22, y + 22, 9), col))
    elif mark == "tri":
        o.append(flat(P([(x + 22, y + 12), (x + 32, y + 30), (x + 12, y + 30)]).buffer(1.5, join_style=1), col))
    elif mark == "flower":
        o.append(place(x + 22, y + 22, .9, i_flower))
    else:
        o.append(flat(R(x + 14, y + 14, 16, 16, 3), col))
    return "".join(o)


def screen_school():
    wall = "#FFF2CF"
    o = [f'<rect width="{W}" height="{H}" fill="{wall}"/>']
    o.append(f'<rect x="0" y="640" width="{W}" height="204" fill="{WOOD2}" filter="{wood_f(.5, 0, .05)}"/>')
    o.append(topbar("老師早安！", 3))
    o.append(task_strip(196, [("書包", lambda: place(0, 0, .8, i_backpack)), ("早安", i_wave), ("唱歌", i_note), ("點心", i_cookie), ("午睡", i_mat)], 1, 1))
    # the cubbies
    o.append(wood(R(22, 270, 116, 166, 8), WOOD, grain=.42, sh=2))
    marks = [("star", YEL), ("heart", PINK), ("circle", BLUE), ("tri", GRN), ("flower", PINK), ("square", LILAC)]
    for i, (m, c) in enumerate(marks):
        r_, c_ = divmod(i, 2)
        o.append(cubby(30 + c_ * 52, 278 + r_ * 52, m, c, glow=(i == 0)))
    o.append(place(52, 262, .9, backpack, GRN, .9))
    # the teacher and two classmates
    o.append(place(214, 640, 1.3, peg_doll, 2, 1, 5, "happy", "brush"))
    o.append(f'<ellipse cx="200" cy="520" rx="9" ry="8" fill="none" stroke="{DARK}" stroke-width="1.6"/><ellipse cx="228" cy="520" rx="9" ry="8" fill="none" stroke="{DARK}" stroke-width="1.6"/><path d="M209,520 H219" stroke="{DARK}" stroke-width="1.6"/>')
    o.append(place(302, 640, .9, peg_doll, 1, 2, 3, "happy", "brush"))
    o.append(place(354, 640, .9, peg_doll, 3, 0, 4, "happy", "brush"))
    # the whiteboard, the snack table and the nap mats
    o.append(wood(R(160, 268, 150, 100, 8), WOOD2, grain=.4, sh=2) + flat(R(168, 276, 134, 84, 5), "#F7FBFF"))
    o.append(place(236, 330, .9, i_sun) + stroke("M180,350 Q200,330 220,350", GRN, 3) + heart(284, 300, 5, PINK) + stroke("M190,296 L198,292 L206,300", BLUE, 2.2))
    o.append(place(330, 476, .9, table, 86, False) + place(316, 442, .85, cup, PINK) + place(346, 442, .85, cup, BLUE) + place(331, 438, .9, i_cookie))
    o.append(room_sign(298, 482, "點心桌", 11))
    for i in range(3):
        o.append(paint(E(262 + i * 50, 736, 24, 9), (BLUE, PINK, GRN)[i]))
        o.append(paint(R(238 + i * 50, 696, 30, 40, 12), (BLUE, PINK, GRN)[i]) + face(253 + i * 50, 712, .5, "sleepy", False))
    o.append(room_sign(252, 750, "午睡的墊子", 11))
    # the child arriving with the puppy
    o.append(place(96, 640, 1.0, peg_doll, 0, 0, 0, "happy", "brush"))
    o.append(place(150, 640, .75, puppy, "happy", 1))
    o.append(heart(236, 470, 7, PINK) + sparkle(130, 480, 6, YEL) + sparkle(372, 400, 5, PINK))
    o.append(place(90, 760, 1.1, rug, 120, PINK))
    return page("".join(o), wall)


# ================================================================ SCREEN 12: supermarket
def carrot():
    return paint(P(crs([(-6, -6), (6, -6), (3, 22), (-3, 22)], 6)), ORA) + paint(U(E(-5, -12, 4, 7, rot=-25), E(4, -13, 4, 7, rot=20), E(0, -14, 3.5, 7)), GRN) + stroke("M-3,2 h4 M-2,10 h4", darker(ORA, .3), 1.4)


def banana():
    return paint(P(crs([(-18, 4), (-8, -8), (8, -10), (18, -2), (16, 4), (6, 0), (-6, 2), (-14, 8)], 6)), YEL)


def orange():
    return paint(E(0, 0, 11), ORA) + flat(E(2, -8, 4, 2.5, rot=-30), GRN)


def tomato():
    return paint(E(0, 2, 12, 10), RED) + flat(U(E(-4, -7, 4, 2.5, rot=-30), E(4, -7, 4, 2.5, rot=30)), GRN)


def milk():
    return paint(U(R(-10, -14, 20, 30, 3), P([(-10, -14), (0, -22), (10, -14)])), WHITE) + flat(R(-7, -4, 14, 12, 2), BLUE) + flat(E(0, 2, 4, 3), "#FFFFFF")


def eggs():
    return paint(R(-14, -8, 28, 14, 3), "#E9D9C0") + "".join(flat(E(-8 + i * 8, -10, 3.4, 4), WHITE) for i in range(3))


def shopping_list(x, y):
    o = [paint(R(x, y, 150, 64, 10), WHITE, sh=2, grain=.04)]
    o.append(paint(R(x + 60, y - 8, 30, 12, 4), YEL, sh=0))
    for i, fn in enumerate((apple, carrot, milk)):
        cx = x + 28 + i * 48
        o.append(f'<circle cx="{cx}" cy="{y + 34}" r="19" fill="{CREAM}"/>')
        o.append(place(cx, y + 34 + (2 if fn is apple else -2), .75, fn))
        if i == 0:
            o.append(f'<circle cx="{cx + 13}" cy="{y + 20}" r="8" fill="{GRN}"/>' + i_check(cx + 13, y + 20, .5))
    return "".join(o)


def cart():
    o = [paint(E(-14, 4, 7), "#5A5A66", sh=0) + paint(E(16, 4, 7), "#5A5A66", sh=0)]
    o.append(paint(P([(-30, -40), (26, -40), (20, -6), (-24, -6)]).buffer(2, join_style=1), BLUE))
    for i in range(4):
        o.append(stroke(f"M{-26 + i * 14},-38 L{-21 + i * 14},-8", lighter(BLUE, .5), 1.6))
    o.append(stroke("M26,-40 L36,-64 L48,-64", "#5A5A66", 3.4))
    return "".join(o)


def screen_shop():
    wall = "#FBE9EE"
    o = [f'<rect width="{W}" height="{H}" fill="{wall}"/>']
    o.append(f'<rect x="0" y="720" width="{W}" height="124" fill="#EFE4D6"/>')
    o.append(topbar("找找看，紅蘿蔔在哪裡？", 2))
    o.append(shopping_list(24, 170))
    o.append(tx(99, 166, "", 10))
    o.append(paint(R(196, 170, 170, 64, 10), "#FFFFFF", sh=1, grain=.04) + tx(281, 196, "買三樣：", 13, SOFT) + tx(281, 218, "蘋果 ✓、紅蘿蔔、牛奶", 12.5, INK))
    # the shelves
    o.append(wood(R(28, 254, 334, 300, 10), WOOD, grain=.42, sh=2))
    rows = [[("apple", apple), ("apple", apple), ("banana", banana), ("orange", orange), ("orange", orange)],
            [("carrot", carrot), ("carrot", carrot), ("broccoli", broccoli), ("tomato", tomato), ("tomato", tomato)],
            [("milk", milk), ("milk", milk), ("eggs", eggs), ("milk", milk), ("cookie", lambda: i_cookie(1.0))]]
    for r_, items in enumerate(rows):
        sy = 338 + r_ * 100
        o.append(f'<rect x="36" y="{sy - 72}" width="318" height="72" rx="6" fill="{("#FFF3D4", "#E2F4E0", "#DDF2F8")[r_]}"/>')
        o.append(paint(R(34, sy, 322, 10, 4), WOOD2, sh=1))
        for i, (name, fn) in enumerate(items):
            x = 68 + i * 64
            o.append(place(x, sy - 2 - (8 if name in ("apple", "orange", "tomato") else 20 if name == "carrot" else 14 if name == "milk" else 6), 1.15, fn))
            if name == "carrot" and i == 0:
                o.append(sparkle(x - 22, sy - 60, 7, YEL) + sparkle(x + 18, sy - 66, 5, PINK) + sparkle(x + 24, sy - 36, 4, YEL))
    # the cart with the child and the puppy, the cashier
    o.append(place(60, 720, .9, peg_doll, 0, 0, 0, "smile", "brush"))
    o.append(place(124, 720, 1.0, cart))
    o.append(place(118, 690, .9, apple))
    o.append(place(190, 720, .7, puppy, "happy", -1))
    o.append(paint(R(258, 650, 110, 70, 8), TEAL) + paint(R(252, 642, 122, 12, 6), WOOD2))
    o.append(paint(R(330, 616, 32, 26, 4), GREY) + flat(R(334, 620, 24, 10, 2), SKY))
    o.append(place(296, 646, .8, peg_doll, 1, 1, 1, "happy"))
    o.append(room_sign(270, 690, "結帳", 12))
    return page("".join(o), wall)


# ================================================================ SCREEN 13: chores on the balcony
def sock(col, stripes=False, s=1.0):
    g = U(R(-7, -20, 14, 26, 5), E(5, 6, 11, 7.5))
    o = [paint(g, col, grain=.06)]
    o.append(flat(R(-7, -20, 14, 6, 3), lighter(col, .5)))
    if stripes:
        o.append(flat(R(-7, -10, 14, 3, 1).intersection(g), "#FFFFFF") + flat(R(-7, -3, 14, 3, 1).intersection(g), "#FFFFFF"))
    return f'<g transform="scale({s})">' + "".join(o) + "</g>"


def basket():
    return paint(P([(-30, -28), (30, -28), (24, 0), (-24, 0)]).buffer(2, join_style=1), WOOD2) + stroke("M-24,-20 H24 M-22,-10 H22", WALNUT, 1.6, op=.5) + paint(R(-34, -32, 68, 8, 4), WOOD2)


def watering_can(col=BLUE):
    return (paint(R(-16, -26, 32, 26, 6), col) + paint(P([(14, -20), (34, -34), (36, -28), (16, -10)]).buffer(1.5, join_style=1), col)
            + paint(E(35, -32, 6, 4, rot=-40), darker(col, .2)) + stroke("M-14,-28 Q-4,-44 8,-28", col, 4) + face(-2, -14, .55))


def garbage_truck():
    o = [paint(E(-30, 0, 9), "#5A5A66", sh=0) + paint(E(26, 0, 9), "#5A5A66", sh=0)]
    o.append(paint(R(-50, -40, 66, 40, 8), YEL))
    o.append(paint(R(14, -34, 34, 34, 6), YEL) + flat(R(20, -30, 18, 12, 3), SKY))
    o.append(stroke("M-44,-20 H8", darker(YEL, .3), 2) + face(-18, -24, .6, "happy"))
    for i, (dx, dy) in enumerate(((-10, -62), (8, -72), (-28, -70))):
        o.append(paint(E(dx - 3, dy + 4, 4, 3, rot=-20), LILAC) + paint(R(dx, dy - 10, 2.4, 14, 1), LILAC))
    return "".join(o)


def screen_chores():
    o = [f'<rect width="{W}" height="{H}" fill="{lg([(0, "#BFE3F5"), (1, "#EAF7FF")])}"/>']
    o.append(topbar("幫忙收衣服，襪子要配對！", 4))
    for cx, cy, w in ((70, 220, 60), (300, 250, 50), (200, 700, 44)):
        o.append(flat(U(E(cx - w * .3, cy + 4, w * .26), E(cx + w * .05, cy - 4, w * .32), E(cx + w * .36, cy + 5, w * .22), R(cx - w * .5, cy, w, w * .26, w * .13)), "#FFFFFF", 'opacity=".9"'))
    # the clothes line
    o.append(place(60, 210, 1.5, i_sun))
    o.append(place(195, 400, 1.6, clothesline, 200, []))
    hang = [(-78, lambda: sock(RED, False)), (-44, lambda: sock(BLUE, True)), (-6, lambda: i_shirt(1.4, YEL)), (36, lambda: sock(GRN, False)), (74, lambda: sock(BLUE, True))]
    for dx, fn in hang:
        x = 195 + dx * 1.6
        y = 400 - 90 + abs(dx) * .08 * 1.6
        o.append(paint(R(x - 3, y - 4, 6, 12, 2), WOOD2, sh=0))
        o.append(place(x, y + 30 + (6 if dx == -6 else 0), 1.15, fn))
    # the sock being carried to its match in the basket
    o.append(stroke("M100,352 Q86,440 124,556", WHITE, 3.5, (7, 7), .9) + i_arrow(128, 564, .8, WHITE, 90))
    o.append(place(104, 466, 1.3, lambda: sock(GRN, False), rot=-14))
    o.append(finger(122, 484, -35))
    # the balcony floor and the things on it
    o.append(f'<rect x="0" y="596" width="{W}" height="80" fill="{WOOD2}" filter="{wood_f(.5, 0, .05)}"/>')
    o.append(place(195, 676, 1.0, railing, 400).replace('scale(1.0000)', 'scale(1.0000)'))
    o.append(place(48, 596, .85, bins))
    o.append(place(130, 596, 1.0, basket) + place(118, 580, .8, lambda: sock(GRN, False), rot=20) + place(142, 582, .8, lambda: sock(RED, False), rot=-15))
    o.append(place(215, 596, 1.2, pet_bowl) + place(270, 596, .9, puppy, "smile", -1))
    o.append(place(328, 596, 1.0, watering_can))
    o.append(place(364, 596, 1.0, plant, True) + place(372, 538, .8, i_drop, 1.0, BLUE))
    # the street below: the garbage truck is coming
    o.append(f'<rect x="0" y="676" width="{W}" height="168" fill="#B9B3B6"/>' + f'<path d="M0,770 H{W}" stroke="#FFF2C2" stroke-width="3" stroke-dasharray="18 14"/>')
    o.append(place(170, 800, 1.1, garbage_truck))
    o.append(tx(300, 740, "♪", 22, LILAC) + tx(330, 720, "♫", 26, PINK) + tx(272, 716, "♪", 18, YEL))
    return page("".join(o), "#BFE3F5")


# ================================================================ SCREEN 14: things that happen
def event_cell(x, y, w, h, text, inner, wall=None):
    o = [wood(R(x, y, w, h, 14), WOOD2, grain=.42, sh=2)]
    o.append(f'<rect x="{x + 7}" y="{y + 7}" width="{w - 14}" height="{h - 14}" rx="9" fill="{wall or ROOM_WALL["living"]}"/>')
    o.append(f'<rect x="{x + 7}" y="{y + h - 34}" width="{w - 14}" height="27" fill="{WOOD}" filter="{wood_f(.5, 0, .05)}"/>')
    o.append(inner(x + 7, y + 7, w - 14, h - 14 - 27))
    o.append(say(x + 10, y + 16, w - 20, 40, text, size=13.5, speaker=False))
    return "".join(o)


def ev_quake(x, y, w, h):
    fy = y + h
    o = [place(x + w / 2, fy, 1.7, table, 92, False)]
    o.append(place(x + w / 2 - 36, fy, .92, peg_doll, 0, 0, 0, "worry", "head"))
    o.append(place(x + w / 2 + 44, fy, .75, puppy, "smile", -1))
    lx = x + w * .5
    o.append(f'<g transform="rotate(20 {lx} {y})">' + stroke(f"M{lx},{y} V{y + 56}", WALNUT, 2.4) + paint(P([(lx - 22, y + 56), (lx + 22, y + 56), (lx + 14, y + 84), (lx - 14, y + 84)]).buffer(1.5, join_style=1), YEL) + "</g>")
    o.append(stroke(f"M{x + 24},{y + 70} l-8,12 M{x + 16},{y + 110} l-10,10 M{x + w - 22},{y + 120} l10,10 M{x + w - 30},{y + 70} l8,12", "#8A7A6A", 2.4))
    o.append(place(x + 40, y + 110, 1.1, picture_frame, GRN, rot=-18))
    return "".join(o)


def ev_doorbell(x, y, w, h):
    fy = y + h
    o = [place(x + 52, fy, 1.6, door)]
    o.append(place(x + 52, fy, .95, peg_doll, 4, 1, 5, "happy", "brush"))
    o.append(f'<ellipse cx="{x + 42}" cy="{fy - 59}" rx="9" ry="7" fill="none" stroke="{DARK}" stroke-width="1.6"/><ellipse cx="{x + 62}" cy="{fy - 59}" rx="9" ry="7" fill="none" stroke="{DARK}" stroke-width="1.6"/>')
    o.append(place(x + w - 48, fy, .95, peg_doll, 0, 0, 0, "happy", "brush"))
    o.append(place(x + w - 14, fy, .6, puppy, "happy", -1))
    o.append(paint(E(x + 104, fy - 124, 7), YEL, sh=0) + tx(x + 128, fy - 132, "叮咚", 14, ORA))
    o.append(heart(x + w - 24, fy - 130, 7, PINK) + heart(x + 98, fy - 150, 5, PINK))
    return "".join(o)


def band_aid(s=1.0):
    return f'<g transform="rotate(-30) scale({s})">' + paint(R(-18, -7, 36, 14, 7), "#F2CBA0") + flat(R(-7, -5, 14, 10, 2), lighter("#F2CBA0", .5)) + "".join(flat(E(-3 + i * 3, -1 + j * 3, .8), "#D9A273") for i in range(3) for j in range(2)) + "</g>"


def ev_fall(x, y, w, h):
    fy = y + h
    o = [place(x + w / 2 - 14, fy, 1.05, peg_doll, 0, 0, 0, "worry")]
    cx = x + w / 2 - 14
    o.append(flat(E(cx + 12, fy - 9, 5, 4), RED))
    o.append(flat(E(cx - 22, fy - 66, 2.6, 4.5), BLUE) + flat(E(cx + 20, fy - 66, 2.6, 4.5), BLUE))
    o.append(place(x + 34, fy, .7, puppy, "smile", 1))
    o.append(finger(cx + 60, fy - 70, 30) + place(cx + 54, fy - 76, 1.5, band_aid, 1.0))
    o.append(stroke(f"M{cx + 44},{fy - 50} Q{cx + 30},{fy - 30} {cx + 16},{fy - 14}", WHITE, 3, (5, 5), .9) + i_arrow(cx + 14, fy - 12, .6, WHITE, 130))
    o.append(place(x + w - 30, fy - 150, 1.0, i_drop, 1.0, BLUE) + tx(x + w - 30, fy - 170, "哎呀", 13, INK))
    return "".join(o)


def puzzle_piece(col, rot=0.0):
    g = U(R(-10, -10, 20, 20, 3), E(0, -12, 4.5), E(12, 0, 4.5)).difference(E(-10, 0, 4.5))
    return f'<g transform="rotate({rot})">' + paint(g, col) + "</g>"


def ev_angry(x, y, w, h):
    fy = y + h
    o = [place(x + w / 2 - 10, fy, 1.05, peg_doll, 0, 0, 0, "worry")]
    cx = x + w / 2 - 10
    o.append(f'<circle cx="{cx - 18}" cy="{fy - 100}" r="7" fill="{CHEEK}" opacity=".8"/><circle cx="{cx + 18}" cy="{fy - 100}" r="7" fill="{CHEEK}" opacity=".8"/>')
    o.append(stroke(f"M{cx + 40},{fy - 150} l6,-8 M{cx + 48},{fy - 140} l9,-3 M{cx + 50},{fy - 128} l9,3", RED, 2.4))
    for i, (dx, col, rot) in enumerate(((-64, RED, 20), (-40, YEL, -15), (44, GRN, 35), (66, BLUE, -25))):
        o.append(place(cx + dx, fy - 12, 1.15, puzzle_piece, col, rot))
    for i, lab in enumerate(("一", "二", "三")):
        bx, by = cx - 44 + i * 44, fy - 190 - (8 if i == 1 else 0)
        o.append(f'<circle cx="{bx}" cy="{by}" r="17" fill="#FFFFFF" opacity=".92" stroke="{SKY}" stroke-width="2"/>' + tx(bx, by + 6, lab, 15, INK))
    o.append(place(x + w - 24, fy, .65, puppy, "smile", -1))
    return "".join(o)


def screen_events():
    o = [wallpaper(base="#FBF1E2", col="#F2DFC0")]
    o.append(sign_title(195, 44, "偶爾會發生的事", 250, 22))
    cells = [("躲到桌子下！", ev_quake, None, "地震"), ("阿嬤你好！", ev_doorbell, ROOM_WALL["door"], "門鈴"),
             ("秀秀，貼 OK 繃", ev_fall, None, "跌倒"), ("深呼吸，一、二、三", ev_angry, ROOM_WALL["bed"], "生氣")]
    for i, (text, fn, wall, name) in enumerate(cells):
        r_, c_ = divmod(i, 2)
        x, y = 12 + c_ * 188, 86 + r_ * 376
        o.append(event_cell(x, y, 178, 340, text, fn, wall))
        o.append(room_sign(x + 8, y + 342, name, 12))
    return page("".join(o), "#FBF1E2")


# ================================================================ PAGE 0: THE SAME LIVING ROOM IN THREE STYLES
def living_scene(x, y, w=330, h=240):
    """The living room: the clock on the wall, the child and the puppy, the sofa, the toy box, the morning window.
    Drawn with whatever paint()/wood()/flat()/stroke() do for the current STYLE."""
    o = []
    fy = y + h - 40
    if STYLE == "paper":
        # the open book under the scene: two pages that tilt towards the spine
        o.append(f'<path d="M{x - 8},{y + h + 10} L{x + w / 2},{y + h + 34} L{x + w + 8},{y + h + 10} L{x + w + 8},{y + h - 50} L{x + w / 2},{y + h - 26} L{x - 8},{y + h - 50}Z" fill="#F6ECDC" stroke="#D9C8B0" stroke-width="1.5"/>')
        o.append(f'<path d="M{x - 8},{y + h + 10} L{x + w / 2},{y + h + 34} L{x + w + 8},{y + h + 10} l0,6 L{x + w / 2},{y + h + 40} L{x - 8},{y + h + 16}Z" fill="#E4D6C2"/>')
        o.append(f'<path d="M{x + w / 2},{y + h - 26} V{y + h + 34}" stroke="#D9C8B0" stroke-width="2"/>')
        o.append(f'<ellipse cx="{x + w / 2}" cy="{y + h - 6}" rx="{w * .48}" ry="12" fill="#3A2A22" opacity=".18" filter="{blur(6)}"/>')
        o.append(f'<g transform="translate({x + w / 2} {y + h}) skewX(-4) scale(1 .96) translate({-(x + w / 2)} {-(y + h)})">')
        o.append(f'<rect x="{x + 8}" y="{y - 8}" width="{w - 16}" height="{h - 10}" fill="{darker("#FFF3D4", .08)}"/>')
    wall, floor = ("#FFF3D4", WOOD) if STYLE != "pencil" else ("#FFF6DF", "#EBCB9A")
    o.append(wood(R(x, y, w, h, 14), WOOD2, grain=.42, sh=2))
    o.append(flat(R(x + 8, y + 8, w - 16, h - 16, 9), wall))
    o.append(flat(R(x + 8, fy, w - 16, h - 8 - (fy - y), 4), floor))
    o.append(room_strip(y + h - 14, "客廳", "廁所", .5, x + w / 2, labels=False))
    o.append(place(x + 86, y + 76, .95, window, 70, 54, "morning", True, .2))
    o.append(place(x + w - 74, y + 84, .68, clock, 0, 0, 56, 1, False))
    o.append(place(x + 72, fy, 1.05, sofa, 84, TEAL))
    o.append(place(x + w - 42, fy, .95, toybox))
    o.append(place(x + 14 + 14, fy, .9, lamp))
    o.append(place(x + w / 2 + 6, fy, 1.0, peg_doll, 0, 0, 0, "happy"))
    o.append(place(x + w / 2 + 70, fy, .85, puppy, "happy", -1))
    o.append(heart(x + w / 2 + 44, fy - 100, 6, PINK) + sparkle(x + w / 2 - 44, fy - 96, 6, YEL))
    if STYLE == "paper":
        o.append("</g>")
    return "".join(o)


def style_sheet():
    global STYLE
    ph = 1226
    o = [f'<rect width="{W}" height="{ph}" fill="#F7F2EA"/>']
    o.append(tx(195, 58, "選一個畫風", 30, INK))
    o.append(tx(195, 90, "同一個客廳，三種畫法", 16, SOFT))
    bands = [("A 木頭玩具屋風（建議）", "像木頭娃娃屋：圓角積木家具，有木紋和薄薄的漆。", "wood"),
             ("B 立體書風", "像翻開的立體書：紙片立起來，有紙的厚度和影子。", "paper"),
             ("C 色鉛筆塗畫風", "像小朋友用色鉛筆畫的：有筆觸和紙的紋路，軟軟的。", "pencil")]
    y = 116
    for title, desc, st in bands:
        h = 346
        if st == "wood":
            o.append(f'<rect x="12" y="{y - 4}" width="366" height="{h + 8}" rx="28" fill="#5DB86A"/>')
            o.append(f'<rect x="16" y="{y}" width="358" height="{h}" rx="24" fill="#FFFFFF"/>')
            o.append(f'<rect x="270" y="{y - 14}" width="92" height="30" rx="15" fill="#5DB86A"/>' + tx(316, y + 7, "我建議這個", 14, "#FFFFFF"))
        else:
            o.append(f'<rect x="16" y="{y + 4}" width="358" height="{h}" rx="24" fill="#E9DED3"/><rect x="16" y="{y}" width="358" height="{h}" rx="24" fill="#FFFFFF"/>')
        o.append(tx(34, y + 40, title, 22, INK, "start"))
        o.append(tx(34, y + 68, desc, 13.5, "#6E5C52", "start"))
        px, py = 30, y + 88
        STYLE = st
        if st == "pencil":
            k = "pap" + _h(py)
            D.add(k, f'<filter id="{k}" x="0" y="0" width="1" height="1"><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="3" seed="9" result="n"/>'
                     f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.38  0 0 0 0 0.3  0 0 0 0.22 0"/></filter>')
            o.append(f'<rect x="{px}" y="{py}" width="330" height="240" rx="14" fill="#FBF6EA"/><rect x="{px}" y="{py}" width="330" height="240" rx="14" fill="#000" filter="url(#{k})"/>')
        elif st == "paper":
            o.append(f'<rect x="{px}" y="{py}" width="330" height="240" rx="14" fill="#E8F1F5"/>')
        o.append(living_scene(px, py + (0 if st != "paper" else -6), 330, 240 - (0 if st != "paper" else 30)))
        STYLE = "wood"
        y += h + 22
    return page("".join(o), "#F7F2EA", W, ph), ph


# ================================================================ CONTACT SHEET AND MAIN
def contact_sheet(names):
    cw_, ch_, gap, m = 232, 502, 24, 30
    per = 5
    rows = (len(names) + per - 1) // per
    w = per * cw_ + (per - 1) * gap + 2 * m
    rowh = ch_ + 64
    h = rows * rowh + 40
    items = []
    for i, n in enumerate(names):
        r, c = divmod(i, per)
        k = min(per, len(names) - r * per)
        x = m + c * (cw_ + gap) + (per - k) * (cw_ + gap) / 2
        y = 28 + r * rowh
        items.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{cw_}px;text-align:center">'
                     f'<img src="file://{HERE / (n + ".png")}" style="width:{cw_}px;height:{ch_}px;border-radius:18px;box-shadow:0 6px 16px rgba(90,60,40,.2)">'
                     f'<div style="font:19px Huninn, sans-serif;color:{INK};margin-top:10px">{n.replace("_", " ")}</div></div>')
    css = f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }} * {{ margin:0; padding:0 }} body {{ width:{w}px; height:{h}px; background:#F7F1E8; position:relative }}"
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(items)}</body></html>', w, h


SCREENS = {"1_取名選角色": screen_name, "2_客廳和時鐘": screen_home, "3_調時間": screen_clock, "4_刷牙": screen_brush,
           "5_想上廁所": screen_pee, "6_吃飯": screen_meal, "7_睡覺": screen_sleep, "8_貼紙表": screen_chart, "9_家長模式": screen_parents,
           "10_小街": screen_street, "11_幼兒園": screen_school, "12_超市": screen_shop, "13_陽台家事": screen_chores, "14_發生事情": screen_events}


def main(only=None):
    global D
    if only in (None, "0"):
        D = Defs()
        html, ph = style_sheet()
        render(html, HERE / "0_畫風選擇.png", W, ph, 2)
        print("0_畫風選擇")
    for name, make in SCREENS.items():
        if only not in (None, name.split("_")[0]):
            continue
        D = Defs()
        render(make(), HERE / f"{name}.png", W, H, 2)
        print(name)
    if only in (None, "c"):
        html, w, h = contact_sheet(list(SCREENS))
        render(html, HERE / "contact_sheet.png", w, h, 1.25)
        print("contact_sheet")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
