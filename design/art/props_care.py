"""Mini-game props, part A (docs/art.md 小遊戲的道具): teeth, washing, toilet, clothes, food, bed.

Every prop is a small pop-up-book picture (kit.py): a few cut-paper layers with thickness and a soft
shadow, soft colours, a little face where it is cute. Files are 100 x 100 unless `PROPS` says
otherwise; ~8 px on the right and bottom are left free for the shadow. `build()` writes them all to
app/assets/art/props/<id>.svg through kit.write_svg (it checks docs/art.md's rules).
"""
import math

import kit
from kit import (BLUSH, CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH,
                 PEACH_DK, PINK, PINK_DK, SKY, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, Shape, arc, blob, circle, cloud,
                 ellipse, heart, path, poly, rect, rrect, smooth, star)

OUT = kit.ART / "props"

# extra soft colours for this set
SKIN = "#F9D9C0"
SILVER = "#DCDFE6"
SILVER_DK = "#B4B9C6"
WATER = "#A6D6F0"
GLASS = "#DCEEF8"          # pale glass for the bedroom window (a real colour, NOT kit.SKY_TOKEN)
RED = "#F07C7C"
RICE = "#FFFDF6"
MELON = "#F58C9E"
ORANGE = "#F5A95E"
DENIM = "#8DB0DC"
MOUTH = "#9E4F60"
GUM = "#EE9BAA"
TOOTH = "#FFFFFF"
BROWN = "#A3785A"
BISCUIT = "#E6BC78"


def ctx(w, h):
    """A Ctx for a prop: small files get smaller depths/shadows so ~8 px of margin is enough."""
    return kit.Ctx(w, h, scale=.8 if min(w, h) <= 100 else 1.0)


def arc_pts(cx, cy, r, a0, a1, steps=12, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]


def wave(x0, x1, y, amp, waves, steps=6):
    """An open wavy line from x0 to x1 about y (for steam, water, fold lines)."""
    pts = []
    total = waves * steps
    for i in range(total + 1):
        t = i / total
        pts.append((x0 + (x1 - x0) * t, y + amp * math.sin(t * waves * 2 * math.pi)))
    return path(pts)


def steam(c, x, y0, y1, dx=0.0, col=PAPER, op=.6, w=3.0):
    """A wavy line of steam rising from (x, y0) to (x + dx, y1)."""
    pts = []
    steps = 8
    for i in range(steps + 1):
        t = i / steps
        pts.append((x + dx * t + 4 * math.sin(t * 2 * math.pi), y0 + (y1 - y0) * t))
    c.stroke(path(pts), col, w, op=op)


# ================================================================ a painter for shapes drawn at a
# scale / offset, solid (layers) or faint (printed on the plate)
class P:
    def __init__(self, c, s=1.0, dx=0.0, dy=0.0, faint=False):
        self.c, self.s, self.dx, self.dy, self.faint = c, s, dx, dy, faint

    def t(self, shape):
        return shape.scale(self.s).move(self.dx, self.dy)

    def layer(self, shape, col, depth=4.0, shadow=True):
        if self.faint:
            self.c.flat(self.t(shape), col, op=.42)
        else:
            self.c.layer(self.t(shape), col, depth=depth, shadow=shadow)

    def flat(self, shape, col, op=1.0, rule=None):
        self.c.flat(self.t(shape), col, op=op * (.42 if self.faint else 1), rule=rule)

    def stroke(self, shape, col=DARK, w=2.5, op=1.0):
        self.c.stroke(self.t(shape), col, w * self.s, op=op * (.42 if self.faint else 1))

    def face(self, cx, cy, size, mood="happy"):
        if not self.faint:
            self.c.face(self.dx + cx * self.s, self.dy + cy * self.s, size * self.s, mood)

    def dots(self, pts, r, col, op=1.0):
        self.c.dots([(self.dx + x * self.s, self.dy + y * self.s) for x, y in pts], r * self.s, col,
                    op * (.42 if self.faint else 1))


# ================================================================ teeth
def toothbrush(c):
    c.layer(rrect(50, 36, 18, 56, 9), MINT, depth=4)                       # handle
    c.layer(rrect(53, 26, 12, 14, 5), MINT_DK, depth=2, shadow=False)      # neck
    c.layer(rrect(46, 2, 24, 36, 10), kit.lt(MINT, .25), depth=4)          # head
    tufts = Shape()
    for i in range(5):                                                     # tufts of bristles
        tufts = tufts + rrect(28, 5 + i * 6.4, 20, 4.4, 2.2)
    c.layer(tufts, PAPER, depth=2, edge_col=kit.dk(PAPER, .25))
    c.layer(rrect(24, 10, 14, 9, 4.5), WATER, depth=2, shadow=False)       # a dab of paste
    c.face(59, 56, 4.5, "happy")
    c.flat(rrect(55, 78, 8, 4, 2), MINT_DK, op=.8)


def toothpaste(c):
    body = rrect(6, 40, 60, 34, 10, rtl=4, rbl=4)
    c.layer(body, LAVENDER, depth=4)
    c.flat(rrect(14, 54, 46, 8, 4), MINT)                                  # the stripe
    c.flat(rrect(14, 46, 30, 5, 2.5), PAPER, op=.8)
    for y in (46, 56, 66):                                                 # the crimped end
        c.stroke(path([(8, y), (13, y)]), kit.dk(LAVENDER, .25), 1.5)
    c.layer(rrect(64, 48, 14, 18, 4), PAPER, depth=3)                      # the cap
    # the squeeze of paste curling out of the cap
    curl = arc(76, 48, 10, 60, -160)
    c.stroke(curl.move(2, 3), kit.dk(PAPER, .28), 10)                      # the paste's edge
    c.stroke(curl, PAPER, 10)
    c.stroke(arc(76, 48, 10, 40, -120), MINT, 3)                          # its stripe
    c.face(36, 60, 4.5, "smile")


def cup(c):
    c.layer(poly([(16, 22), (76, 22), (68, 86), (24, 86)]), PINK, depth=4)
    c.flat(poly([(22, 28), (70, 28), (64, 80), (28, 80)]), kit.lt(PINK, .25), op=.6)
    c.layer(ellipse(46, 22, 30, 8), kit.lt(PINK, .15), depth=2, shadow=False)
    c.flat(ellipse(46, 22, 24, 5), kit.dk(PINK, .2))
    c.flat(star(46, 62, 9), PAPER)
    c.face(46, 44, 7, "happy")


def mouth_big(c):
    W, H = 400, 300
    outer = smooth([(22, 150), (70, 92), (130, 66), (196, 76), (262, 66), (322, 92), (370, 150),
                    (322, 222), (262, 256), (196, 266), (130, 256), (70, 222)], .9)
    inner = smooth([(50, 150), (96, 108), (150, 92), (196, 96), (242, 92), (296, 108), (342, 150),
                    (296, 206), (242, 232), (196, 238), (150, 232), (96, 206)], .9)
    c.layer(outer, CORAL, depth=6, shadow_op=.22)
    c.flat(inner, MOUTH)
    c.flat(ellipse(196, 208, 72, 38), PINK)                                # the tongue
    c.stroke(path([(196, 182), (196, 240)]), PINK_DK, 3)
    c.flat(ellipse(170, 206, 12, 6), kit.lt(PINK, .4), op=.7)
    xs = [86, 130, 174, 218, 262, 306]
    for x in xs:                                                           # bottom row
        yb = 232 - 0.0022 * (x - 196) ** 2
        c.layer(rrect(x - 18, yb - 34, 36, 34, 5, rtl=12, rtr=12), TOOTH, depth=3, shadow=False,
                edge_col="#D9D3CC")
    c.flat(smooth([(60, 150), (120, 128), (196, 122), (272, 128), (332, 150), (300, 168), (196, 160), (92, 168)], .9),
           GUM)                                                             # the top gum
    for x in xs:                                                           # top row
        yt = 96 + 0.0022 * (x - 196) ** 2
        c.layer(rrect(x - 20, yt, 40, 46, 5, rbl=14, rbr=14), TOOTH, depth=3, shadow=False, edge_col="#D9D3CC")
    c.flat(outer + inner, CORAL, rule="evenodd")                           # the lips over the tooth tops
    c.flat(ellipse(120, 92, 16, 6).rotate(-20, 120, 92), kit.lt(CORAL, .45), op=.6)   # glints on the lips
    c.flat(ellipse(272, 92, 16, 6).rotate(20, 272, 92), kit.lt(CORAL, .45), op=.6)
    c.flat(circle(44, 150, 5) + circle(348, 150, 5), kit.dk(CORAL, .25))   # mouth corners


def dirt(c):
    c.layer(blob(46, 46, 26, 22, lumps=8, wobble=.22, key="dirt"), "#9B8678", depth=2, shadow=False)
    c.flat(circle(72, 32, 6) + circle(22, 66, 5) + circle(70, 68, 4), "#9B8678")
    c.flat(circle(40, 40, 7), kit.lt("#9B8678", .2), op=.6)


def bubble(c):
    c.flat(circle(46, 46, 38), WATER, op=.4)
    c.stroke(circle(46, 46, 38), PAPER, 3, op=.9)
    c.flat(ellipse(32, 30, 11, 7).rotate(-40, 32, 30), PAPER, op=.9)
    c.flat(circle(26, 44, 3), PAPER, op=.8)
    c.stroke(arc(46, 46, 31, 20, 80), LAVENDER_DK, 4, op=.45)
    c.stroke(arc(46, 46, 31, 200, 230), PINK_DK, 3, op=.3)


def hands(c):
    def hand(flip):
        palm = rrect(30, 66, 62, 60, 24)
        for x, top in ((32, 30), (47, 20), (62, 24), (77, 34)):
            palm = palm + rrect(x, top, 13, 76 - top + 6, 6.5)
        palm = palm + ellipse(20, 90, 11, 22).rotate(32, 20, 90)
        return palm.flip(100) if flip else palm

    for flip in (False, True):
        sh = hand(flip)
        c.layer(sh, SKIN, depth=4, edge_col=kit.dk(SKIN, .28))
        lines = [arc(70, 80, 30, 110, 170), arc(60, 70, 36, 120, 165)]
        for ln in lines:
            c.stroke(ln.flip(100) if flip else ln, PINK_DK, 2, op=.35)
        tips = [(38.5, 36), (53.5, 26), (68.5, 30), (83.5, 40)]
        c.dots([((200 - x) if flip else x, y) for x, y in tips], 3.6, BLUSH, op=.5)


# ================================================================ washing and bathing
def soap(c):
    c.layer(rrect(44, 6, 26, 10, 4) + rrect(60, 8, 20, 7, 3), SILVER_DK, depth=2)      # the pump
    c.layer(rrect(50, 14, 14, 14, 3), SILVER, depth=2, shadow=False)                    # the neck
    c.layer(rrect(26, 26, 44, 62, 12), LAVENDER, depth=4)                               # the bottle
    c.flat(rrect(32, 42, 32, 30, 7), PAPER)                                             # the label
    c.flat(circle(42, 54, 6) + circle(52, 50, 4) + circle(50, 60, 3), WATER, op=.8)
    c.face(48, 80, 5, "smile")


def _tap(c, on):
    c.layer(rrect(8, 78, 40, 12, 5), SILVER_DK, depth=3)                                # the base
    c.layer(rrect(18, 36, 18, 44, 9), SILVER, depth=3)                                  # the pipe
    c.stroke(arc(48, 44, 22, 180, 360), kit.dk(SILVER, .28), 16)                        # thickness of the spout
    c.stroke(arc(46, 42, 22, 180, 360), SILVER, 14)                                     # the spout
    c.layer(rrect(60, 40, 16, 12, 4), SILVER, depth=2, shadow=False)
    c.layer(rrect(14, 24, 26, 8, 4) + rrect(23, 16, 8, 24, 4), MINT_DK if on else CORAL, depth=2)   # handle
    c.flat(circle(27, 28, 3), PAPER, op=.8)
    if on:
        c.flat(rrect(62, 52, 12, 32, 6), WATER, op=.9)                                  # the stream
        c.flat(rrect(65, 56, 3, 20, 1.5), PAPER, op=.7)
        c.flat(ellipse(68, 86, 16, 4), WATER, op=.8)                                    # the splash
        c.flat(circle(52, 80, 2.5) + circle(85, 78, 2.5) + circle(80, 70, 2), WATER)
    else:
        c.flat(ellipse(68, 60, 3, 4), WATER, op=.9)                                     # one drip


def tap_on(c):
    _tap(c, True)


def tap_off(c):
    _tap(c, False)


def towel(c):
    c.layer(rrect(10, 58, 74, 26, 9), kit.dk(PINK, .08), depth=4)          # the lower fold
    c.layer(rrect(8, 34, 76, 30, 10), PINK, depth=4)                       # the top fold
    c.flat(rrect(8, 46, 76, 6, 3), PAPER, op=.9)                           # a stripe
    c.dots([(14 + i * 10, 63) for i in range(8)], 2.2, PAPER, op=.8)       # fluffy edge
    c.dots([(16 + i * 10, 83) for i in range(7)], 2.2, PAPER, op=.8)
    c.face(46, 40, 5, "sleepy")


def hairdryer(c):
    c.layer(rrect(24, 58, 18, 34, 8).rotate(-18, 33, 60), kit.dk(CORAL, .12), depth=4)    # the handle
    c.flat(rrect(26, 70, 6, 10, 3).rotate(-18, 33, 60), PAPER, op=.8)                     # the switch
    c.layer(rrect(10, 28, 56, 36, 18), CORAL, depth=4)                                    # the barrel
    c.layer(rrect(60, 36, 22, 20, 5), kit.dk(CORAL, .25), depth=3, shadow=False)          # the nozzle
    c.flat(circle(26, 46, 12), kit.dk(CORAL, .3))                                         # the air intake
    c.dots([(26 + 6 * math.cos(a), 46 + 6 * math.sin(a)) for a in [i * math.pi / 3 for i in range(6)]] + [(26, 46)],
           1.8, PAPER, op=.8)
    for y, w in ((38, 1), (46, 1), (54, 1)):                                              # warm air
        c.stroke(wave(84, 92, y, 1.5, 1), PEACH_DK, 2.2, op=.7)


def bathtub_full(c):
    c.layer(rrect(36, 170, 28, 18, 7), SILVER_DK, depth=2)                 # the feet
    c.layer(rrect(220, 170, 28, 18, 7), SILVER_DK, depth=2)
    c.layer(rrect(262, 60, 12, 56, 6), SILVER, depth=3)                    # the tap pipe
    c.stroke(arc(254, 58, 12, 180, 360), SILVER, 9)
    c.layer(rrect(12, 72, 264, 104, 34, rtl=12, rtr=12), PAPER, depth=6)   # the tub
    c.flat(ellipse(144, 78, 116, 16), WATER)                               # the water
    c.flat(ellipse(144, 78, 116, 16) + ellipse(144, 78, 100, 10), kit.lt(WATER, .3), op=.5, rule="evenodd")
    suds = cloud(90, 70, 90, 34, 4) + cloud(200, 72, 100, 36, 5)           # soap suds
    c.layer(suds, PAPER, depth=2, shadow=False)
    c.dots([(60, 62), (120, 58), (176, 60), (232, 64), (150, 50)], 4, PAPER, op=.9)
    c.flat(circle(150, 50, 4) + circle(60, 62, 4), WATER, op=.35)
    duck = ellipse(236, 56, 18, 11) + circle(248, 44, 10)                  # a rubber duck
    c.layer(duck, YELLOW, depth=2, shadow=False)
    c.flat(ellipse(259, 46, 5, 3), ORANGE)
    c.flat(circle(250, 42, 1.6), DARK)
    c.face(144, 130, 12, "happy")
    c.flat(rrect(40, 150, 208, 6, 3), kit.dk(PAPER, .08))                  # a seam


def lotion(c):
    c.layer(rrect(38, 10, 20, 18, 5), PEACH_DK, depth=3)                   # the flip cap
    c.flat(rrect(42, 10, 12, 4, 2), kit.dk(PEACH_DK, .2))
    c.layer(rrect(26, 26, 44, 62, 14), PEACH, depth=4)                     # the bottle
    c.flat(rrect(32, 42, 32, 30, 7), PAPER)                                # the label
    c.flat(heart(48, 54, 14), PINK)
    c.flat(ellipse(48, 48, 2.5, 3.5), WATER, op=.9)                        # a drop on the label
    c.face(48, 80, 5, "smile")


def _thermo(c, kind):
    fill = {"hot": RED, "warm": LEAF, "cold": "#86C4EE"}[kind]
    c.layer(rrect(38, 8, 16, 62, 8), PAPER, depth=3)                       # the tube
    c.layer(circle(46, 72, 17), PAPER, depth=4)                            # the bulb
    c.flat(circle(46, 72, 12), fill)
    level = {"hot": 18, "warm": 36, "cold": 52}[kind]
    c.flat(rrect(42, level, 8, 72 - level, 4), fill)                       # the column
    for y in range(18, 62, 8):                                             # tick marks
        c.stroke(path([(56, y), (60, y)]), kit.dk(PAPER, .3), 1.6)
    if kind == "hot":
        for x, dx in ((26, -3), (46, 2), (66, 4)):
            steam(c, x, 20 if x != 46 else 6, 2 if x != 46 else -4, dx, col=CORAL, op=.6, w=2.6)
        c.flat(ellipse(30, 44, 5, 2.5) + ellipse(62, 44, 5, 2.5), BLUSH, op=.8)
        c.face(46, 72, 4, "open")
    elif kind == "warm":
        c.face(46, 72, 4, "happy")
        c.flat(star(24, 30, 6), YELLOW)
        c.flat(star(70, 24, 5), YELLOW)
    else:
        c.face(46, 72, 4, "sleepy")
        for cx, cy, r in ((24, 30, 9), (72, 22, 7)):                       # snowflakes
            for i in range(3):
                a = math.radians(i * 60)
                c.stroke(path([(cx - r * math.cos(a), cy - r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))]),
                         "#86C4EE", 2)
            c.flat(circle(cx, cy, 2), PAPER)


def temp_hot(c):
    _thermo(c, "hot")


def temp_warm(c):
    _thermo(c, "warm")


def temp_cold(c):
    _thermo(c, "cold")


# ================================================================ toilet
def _toilet(c, open_):
    c.layer(rrect(24, 2, 48, 30, 8), PAPER, depth=4)                       # the tank
    c.flat(rrect(58, 6, 10, 5, 2.5), SILVER_DK)                            # the flush button
    c.face(48, 18, 6, "happy" if open_ else "smile")
    if open_:
        c.layer(rrect(18, 30, 60, 22, 10), PINK, depth=3)                  # the lid, up
        c.flat(heart(48, 41, 10), PAPER)
    c.layer(rrect(24, 62, 48, 28, 10, rtl=2, rtr=2), PAPER, depth=4)       # the pedestal
    c.layer(ellipse(48, 60, 34, 14), PAPER, depth=4)                       # the seat
    if open_:
        c.flat(ellipse(48, 60, 22, 8), WATER)                              # the water in the bowl
        c.flat(ellipse(44, 59, 6, 2.5), PAPER, op=.6)
    else:
        c.layer(ellipse(48, 56, 34, 14), PINK, depth=3, shadow=False)      # the lid, down
        c.flat(heart(48, 56, 12), PAPER)


def toilet_open(c):
    _toilet(c, True)


def toilet_closed(c):
    _toilet(c, False)


def paper(c):
    c.layer(rrect(14, 30, 60, 48, 6), PAPER, depth=4)                      # the roll, side
    c.layer(ellipse(44, 30, 30, 12), kit.lt(PAPER, .5), depth=2, shadow=False)   # the top
    c.flat(ellipse(44, 30, 11, 5), WOOD)                                   # the cardboard tube
    c.flat(ellipse(44, 31, 7, 3), WOOD_DK)
    c.layer(rrect(60, 60, 20, 30, 3), PAPER, depth=2)                      # the hanging sheet
    c.dots([(62 + i * 4, 74) for i in range(5)], 1.1, kit.dk(PAPER, .25))  # the perforation
    c.stroke(arc(44, 30, 30, 20, 160).scale(1, 44, 30, .4), kit.dk(PAPER, .1), 1.6)
    c.face(40, 56, 5, "smile")


def flush(c):
    c.layer(circle(46, 46, 38), WATER, depth=5)
    c.flat(circle(46, 46, 30), kit.lt(WATER, .25))
    pts = []
    for i in range(40):                                                    # a water swirl
        t = i / 39
        a = t * 3 * math.pi
        r = 3 + 21 * t
        pts.append((46 + r * math.cos(a), 46 + r * math.sin(a)))
    c.stroke(path(pts), PAPER, 5)
    c.stroke(path(pts[-4:]), PAPER, 5)
    c.flat(circle(46, 46, 3), PAPER)
    c.flat(ellipse(30, 26, 8, 4).rotate(-35, 30, 26), PAPER, op=.6)


# ================================================================ clothes
def _shirt_shape(long_sleeves=False, length=88):
    pts = [(28, 14), (38, 12), (46, 20), (54, 12), (64, 14), (82, 24), (90, 44), (72, 52), (70, length),
           (22, length), (20, 52), (2, 44), (10, 24)]
    if long_sleeves:
        pts = [(28, 14), (38, 12), (46, 20), (54, 12), (64, 14), (80, 22), (92, 60), (80, 66), (70, 50), (70, length),
               (22, length), (22, 50), (12, 66), (0, 60), (12, 22)]
    return poly(pts)


def cloth_tshirt(c):
    c.layer(_shirt_shape(), MINT, depth=4)
    c.stroke(arc(46, 12, 10, 10, 170), MINT_DK, 3)                         # the collar
    c.flat(star(46, 52, 13), YELLOW)
    c.flat(rrect(22, 44, 48, 3, 1.5), kit.lt(MINT, .3), op=.6)


def cloth_jacket(c):
    c.layer(_shirt_shape(True, 88), LAVENDER_DK, depth=4)
    c.flat(poly([(30, 12), (46, 20), (46, 32)]), kit.lt(LAVENDER_DK, .3))  # the collar
    c.flat(poly([(62, 12), (46, 20), (46, 32)]), kit.lt(LAVENDER_DK, .3))
    c.stroke(path([(46, 32), (46, 86)]), kit.dk(LAVENDER_DK, .3), 2.5)     # the zip
    c.dots([(46, 36 + i * 6) for i in range(9)], 1.1, PAPER)
    c.flat(rrect(26, 62, 14, 12, 3) + rrect(52, 62, 14, 12, 3), kit.dk(LAVENDER_DK, .12))   # pockets
    c.flat(rrect(22, 80, 48, 6, 2), kit.dk(LAVENDER_DK, .15))              # the hem band
    c.flat(rrect(2, 56, 12, 8, 3) + rrect(78, 56, 12, 8, 3), kit.dk(LAVENDER_DK, .15))      # the cuffs


def cloth_raincoat(c):
    body = poly([(30, 30), (62, 30), (82, 60), (84, 88), (8, 88), (10, 60)])
    c.layer(body + circle(46, 24, 20), YELLOW, depth=4)                    # coat and hood
    c.flat(ellipse(46, 26, 11, 13), kit.dk(YELLOW, .35))                   # the hood's dark inside
    c.stroke(path([(46, 44), (46, 86)]), kit.dk(YELLOW, .3), 2)
    c.dots([(46, 52), (46, 64), (46, 76)], 3, kit.dk(YELLOW, .4))          # toggles
    c.flat(rrect(12, 82, 72, 5, 2), kit.dk(YELLOW, .15))
    c.flat(rrect(18, 62, 14, 12, 3) + rrect(60, 62, 14, 12, 3), kit.dk(YELLOW, .15))   # pockets
    c.flat(ellipse(80, 12, 2.5, 4) + ellipse(90, 24, 2, 3.5) + ellipse(14, 10, 2.5, 4), WATER)   # raindrops


def cloth_shorts(c):
    sh = poly([(14, 20), (78, 20), (84, 66), (54, 66), (46, 44), (38, 66), (8, 66)])
    c.layer(sh, DENIM, depth=4)
    c.layer(rrect(14, 16, 64, 10, 4), kit.dk(DENIM, .2), depth=2, shadow=False)   # the waistband
    c.flat(rrect(42, 12, 8, 14, 3), CORAL)                                 # a button loop
    c.stroke(path([(12, 60), (34, 60)]), kit.lt(DENIM, .4), 2)             # the hems
    c.stroke(path([(58, 60), (80, 60)]), kit.lt(DENIM, .4), 2)
    c.flat(star(28, 40, 6), PAPER, op=.8)


def cloth_pants(c):
    sh = poly([(16, 14), (76, 14), (82, 90), (54, 90), (46, 44), (38, 90), (10, 90)])
    c.layer(sh, kit.dk(DENIM, .1), depth=4)
    c.layer(rrect(16, 10, 60, 10, 4), kit.dk(DENIM, .3), depth=2, shadow=False)   # the waistband
    c.flat(circle(46, 15, 3), CORAL)
    c.stroke(path([(14, 84), (34, 84)]), kit.lt(DENIM, .35), 2)            # the hems
    c.stroke(path([(58, 84), (78, 84)]), kit.lt(DENIM, .35), 2)
    c.flat(rrect(22, 26, 12, 10, 3) + rrect(58, 26, 12, 10, 3), kit.dk(DENIM, .25))   # pockets


def cloth_hat(c):
    c.layer(ellipse(48, 60, 42, 13), CORAL, depth=4)                       # the brim
    c.layer(rrect(26, 20, 44, 42, 16, rbl=4, rbr=4), kit.lt(CORAL, .1), depth=4)   # the crown
    c.flat(rrect(26, 50, 44, 8, 3), PAPER, op=.9)                          # the band
    fl = Shape()
    for i in range(5):                                                     # a little flower
        a = math.radians(i * 72 - 90)
        fl = fl + circle(66 + 6 * math.cos(a), 46 + 6 * math.sin(a), 4.5)
    c.layer(fl, PINK, depth=2, shadow=False)
    c.flat(circle(66, 46, 3.5), YELLOW)


def _boot(c, dx, col):
    sh = rrect(30 + dx, 10, 24, 56, 6, rbl=0, rbr=0) + rrect(8 + dx, 56, 46, 26, 12, rtr=2, rtl=12)
    c.layer(sh, col, depth=4)
    c.flat(rrect(30 + dx, 10, 24, 8, 4), kit.lt(col, .3))                  # the top band
    c.layer(rrect(6 + dx, 74, 50, 10, 5), PAPER, depth=2, shadow=False)    # the sole
    c.dots([(36 + dx, 30), (46 + dx, 42), (38 + dx, 52)], 2.2, PAPER, op=.9)


def cloth_boots(c):
    _boot(c, 32, kit.dk(CORAL, .05))                                       # the back boot
    _boot(c, 0, CORAL)                                                      # the front boot


def _shoe(c, flip):
    body = poly([(6, 74), (8, 62), (16, 52), (30, 46), (46, 44), (58, 38), (70, 30), (82, 32), (88, 46), (88, 74)])
    sole = rrect(4, 70, 84, 14, 7)
    cap = poly([(6, 74), (8, 62), (16, 52), (30, 46), (40, 45), (42, 74)])            # the toe cap
    strap = rrect(44, 50, 30, 8, 4)
    tongue = rrect(54, 30, 20, 16, 7)
    f = (lambda s: s.flip(46)) if flip else (lambda s: s)
    c.layer(f(sole), PAPER, depth=3)
    c.layer(f(tongue), kit.dk(WATER, .1), depth=2, shadow=False)
    c.layer(f(body), WATER, depth=4)
    c.flat(f(cap), kit.lt(WATER, .35))
    c.flat(f(star(24, 60, 7)), PINK_DK)
    c.layer(f(strap), PINK, depth=2, shadow=False)
    c.flat(f(circle(68, 52, 2)), PAPER)
    c.stroke(f(path([(16, 82), (80, 82)])), kit.dk(PAPER, .2), 1.6)        # sole grip line


def cloth_shoes_l(c):
    _shoe(c, False)


def cloth_shoes_r(c):
    _shoe(c, True)


def button(c):
    c.layer(circle(46, 46, 36), CORAL, depth=4)
    c.flat(circle(46, 46, 27), kit.lt(CORAL, .2))
    c.stroke(path([(37, 37), (55, 55)]), PAPER, 3, op=.9)                  # the thread
    c.stroke(path([(55, 37), (37, 55)]), PAPER, 3, op=.9)
    c.dots([(37, 37), (55, 37), (37, 55), (55, 55)], 4.5, kit.dk(CORAL, .35))
    c.flat(ellipse(30, 28, 7, 4).rotate(-40, 30, 28), PAPER, op=.5)


def umbrella(c):
    top = arc_pts(46, 52, 40, 180, 360, 24)
    junctions = [86, 66, 46, 26, 6]
    bottom = []
    for i in range(4):
        bottom += arc_pts(junctions[i] - 10, 52, 10, 0, 180, 6)[1:]
    canopy = poly(top + bottom[:-1])
    c.layer(canopy, PINK, depth=4)

    def seam(jx):
        return [(46 + (jx - 46) * t, 12 + 40 * (t ** .55)) for t in [i / 8 for i in range(9)]]

    for k in (0, 2):                                                       # alternate panels
        a, b = junctions[k], junctions[k + 1]
        pts = seam(a) + arc_pts(a - 10, 52, 10, 0, 180, 6)[1:-1] + seam(b)[::-1]
        c.flat(poly(pts), PAPER)
    for jx in junctions[1:-1]:
        c.stroke(path(seam(jx)), PINK_DK, 1.6, op=.6)
    c.stroke(path([(46, 54), (46, 82)]), WOOD_DK, 4)                       # the handle
    c.stroke(arc(39, 82, 7, 0, 180), WOOD_DK, 4)
    c.flat(circle(46, 11, 3.5), PINK_DK)                                   # the tip
    c.face(46, 32, 6, "happy")


# ================================================================ food (drawn with a painter, so the
# plate can print them faintly in its sections)
def f_rice(p):
    p.layer(rrect(28, 52, 40, 30, 6, rbl=14, rbr=14), WATER, depth=3)      # the bowl
    p.layer(cloud(48, 48, 50, 24, 4), RICE, depth=2, shadow=False)         # the rice
    p.dots([(38, 44), (50, 40), (60, 46)], 1.6, kit.dk(RICE, .18), op=.9)
    p.flat(rrect(30, 62, 36, 4, 2), PAPER, op=.8)
    p.flat(rrect(38, 80, 20, 6, 3), kit.dk(WATER, .2))                     # the foot


def f_veg(p):
    p.layer(rrect(40, 54, 14, 32, 6), kit.lt(LEAF, .45), depth=3)          # the stem
    crown = circle(30, 44, 14) + circle(47, 32, 17) + circle(64, 44, 14) + circle(47, 50, 13)
    p.layer(crown, LEAF, depth=4)
    p.dots([(30, 40), (42, 28), (54, 30), (64, 42), (47, 46), (36, 50), (58, 52)], 3.2, LEAF_DK, op=.7)
    p.face(47, 40, 4, "happy")


def f_meat(p):
    bone = rrect(52, 64, 32, 9, 4.5).rotate(-38, 52, 64) + circle(78, 42, 6) + circle(84, 50, 6)
    p.layer(bone, PAPER, depth=3)
    meat = ellipse(40, 46, 26, 22).rotate(-32, 40, 46) + circle(28, 56, 14)
    p.layer(meat, PEACH_DK, depth=4)
    p.flat(ellipse(34, 40, 9, 5).rotate(-32, 34, 40), kit.lt(PEACH_DK, .35), op=.8)
    p.dots([(44, 56), (52, 44), (30, 46)], 1.8, kit.dk(PEACH_DK, .3), op=.6)


def f_fruit(p):
    r_out, r_in = 66, 56
    a0, a1 = 58, 122
    apex = (46, 14)
    rind = poly([apex] + arc_pts(apex[0], apex[1], r_out, a0, a1, 14))
    flesh = poly([apex] + arc_pts(apex[0], apex[1], r_in, a0 + 3, a1 - 3, 14))
    p.layer(rind, LEAF, depth=4)
    p.flat(poly([apex] + arc_pts(apex[0], apex[1], r_out - 5, a0 + 1.5, a1 - 1.5, 14)), PAPER)
    p.flat(flesh, MELON)
    for x, y in ((46, 40), (36, 56), (56, 56), (46, 64), (30, 42), (62, 42)):
        p.flat(ellipse(x, y, 1.8, 3), DARK)
    p.face(46, 50, 4, "happy")


def f_apple(p):
    body = circle(36, 52, 24) + circle(56, 52, 24) + rrect(24, 40, 44, 30, 8)
    p.layer(rrect(44, 14, 6, 16, 3).rotate(12, 47, 22), WOOD_DEEP, depth=2, shadow=False)   # the stem
    p.layer(ellipse(60, 24, 12, 6).rotate(-30, 60, 24), LEAF, depth=2, shadow=False)        # the leaf
    p.layer(body, RED, depth=4)
    p.flat(ellipse(32, 40, 7, 4).rotate(-35, 32, 40), PAPER, op=.55)
    p.face(46, 54, 7, "happy")


def f_banana(p):
    a = arc(46, 10, 44, 35, 145)
    p.stroke(a.move(3, 4), kit.dk(YELLOW, .3), 18)                         # the edge
    p.stroke(a, YELLOW, 18)
    p.stroke(arc(46, 10, 44, 45, 135), kit.lt(YELLOW, .4), 3, op=.7)      # a ridge
    tips = [(46 + 44 * math.cos(math.radians(d)), 10 + 44 * math.sin(math.radians(d))) for d in (35, 145)]
    p.dots(tips, 4.5, WOOD_DEEP)
    p.face(46, 46, 6, "happy")


def f_carrot(p):
    for ang in (-28, 0, 28):                                               # the leaves
        p.layer(ellipse(46, 18, 6, 14).rotate(ang, 46, 30), LEAF, depth=2, shadow=False)
    root = smooth([(30, 32), (62, 32), (58, 58), (50, 82), (46, 88), (42, 82), (34, 58)], .6)
    p.layer(root, ORANGE, depth=4)
    for y in (46, 58, 70):
        p.stroke(path([(36 + (y - 46) * .2, y), (56 - (y - 46) * .2, y)]), kit.dk(ORANGE, .25), 2, op=.7)
    p.face(46, 42, 4, "smile")


def f_milk(p):
    p.layer(poly([(26, 34), (48, 16), (70, 34)]) + rrect(26, 30, 44, 60, 4), PAPER, depth=4)   # the carton
    p.flat(rrect(44, 12, 8, 6, 2), SILVER_DK)                              # the spout
    p.flat(rrect(26, 48, 44, 18, 2), WATER)                                # the blue band
    p.stroke(wave(28, 68, 52, 2, 2), PAPER, 2.2, op=.9)
    p.flat(poly([(40, 62), (50, 62), (48, 76), (42, 76)]) + ellipse(45, 62, 5, 2), PAPER)   # a glass of milk
    p.face(48, 78, 4, "smile")
    p.stroke(path([(26, 34), (70, 34)]), kit.dk(PAPER, .15), 1.5)


def f_egg(p):
    p.layer(blob(46, 52, 38, 30, lumps=7, wobble=.16, key="egg"), PAPER, depth=3)   # the white
    p.layer(circle(44, 50, 16), YELLOW, depth=2, shadow=False)             # the yolk
    p.flat(ellipse(38, 44, 5, 3).rotate(-30, 38, 44), PAPER, op=.6)
    p.face(44, 52, 4.5, "happy")


def f_fish(p):
    tail = poly([(66, 48), (88, 32), (84, 48), (88, 64)])
    p.layer(tail, kit.dk(WATER, .12), depth=3)
    p.layer(ellipse(44, 48, 30, 19), WATER, depth=4)                       # the body
    p.layer(ellipse(44, 30, 8, 5).rotate(-20, 44, 30), kit.dk(WATER, .12), depth=2, shadow=False)   # the fin
    for x in (46, 58):                                                     # scales
        p.stroke(arc(x, 48, 8, 300, 420), kit.dk(WATER, .2), 1.8, op=.7)
    p.flat(circle(28, 46, 3), DARK)                                        # the eye
    p.flat(circle(29, 45, 1), PAPER)
    p.stroke(arc(24, 50, 4, 20, 160), DARK, 1.6)                           # a smile
    p.flat(ellipse(30, 54, 4, 2), BLUSH, op=.8)


def spoon(p):
    p.layer(rrect(41, 34, 10, 56, 5), SILVER, depth=3)                     # the handle
    p.layer(ellipse(46, 24, 19, 14), SILVER, depth=3)                      # the bowl
    p.flat(ellipse(46, 24, 13, 9), kit.dk(SILVER, .12))
    p.flat(ellipse(40, 20, 4, 2.5).rotate(-30, 40, 20), PAPER, op=.8)


def bowl(p):
    p.layer(rrect(14, 36, 68, 44, 8, rtl=4, rtr=4, rbl=26, rbr=26), CORAL, depth=4)   # the bowl
    p.flat(rrect(14, 52, 68, 6, 3), PAPER, op=.9)                          # a stripe
    p.layer(ellipse(48, 36, 36, 10), kit.lt(CORAL, .2), depth=2, shadow=False)   # the rim
    p.flat(ellipse(48, 36, 30, 6), kit.dk(CORAL, .25))
    p.layer(rrect(34, 78, 28, 8, 4), kit.dk(CORAL, .1), depth=2, shadow=False)   # the foot
    p.face(48, 66, 5, "happy")


def chopsticks(p):
    for x, ang in ((38, -6), (58, 6)):
        st = rrect(x - 5, 6, 10, 82, 5, rbl=3, rbr=3).rotate(ang, x, 90)
        p.layer(st, WOOD, depth=3)
        p.flat(rrect(x - 4, 10, 8, 10, 2).rotate(ang, x, 90), PINK, op=.9)   # a coloured top
        p.flat(rrect(x - 4, 22, 8, 3, 1.5).rotate(ang, x, 90), PAPER, op=.8)


def _glass(p, full):
    outline = poly([(26, 14), (70, 14), (64, 86), (32, 86)])
    p.layer(outline, GLASS, depth=3, shadow=True)
    if full:
        water = poly([(28, 32), (68, 32), (64, 86), (32, 86)])
        p.flat(water, WATER, op=.9)
        p.flat(ellipse(48, 32, 20, 3), kit.lt(WATER, .3))
        p.dots([(40, 60), (54, 48)], 2.2, PAPER, op=.8)
    p.flat(poly([(32, 20), (38, 20), (36, 80), (34, 80)]), PAPER, op=.75)  # a glint
    p.stroke(outline, kit.dk(GLASS, .3), 2.2)
    p.flat(ellipse(48, 14, 22, 4), kit.dk(GLASS, .12), op=.9)              # the rim


def cup_water(p):
    _glass(p, False)


def cup_water_full(p):
    _glass(p, True)


def pot(p):
    for x, dx in ((30, -2), (50, 2), (68, 3)):                             # steam
        steam(p.c, x, 30, 6, dx, col=GREY, op=.55, w=3)
    p.layer(rrect(2, 46, 14, 10, 4) + rrect(80, 46, 14, 10, 4), kit.dk(CORAL, .2), depth=2)   # handles
    p.layer(rrect(12, 42, 72, 46, 10, rtl=3, rtr=3), CORAL, depth=4)       # the pot
    p.flat(rrect(12, 60, 72, 5, 2.5), PAPER, op=.8)
    lid = ellipse(44, 40, 38, 8).rotate(-9, 44, 40).move(0, -4)             # the lid, ajar
    p.layer(lid, kit.lt(CORAL, .15), depth=3)
    p.layer(circle(43, 28, 5), WOOD_DEEP, depth=2, shadow=False)           # the knob
    p.face(48, 76, 6, "happy")


# ================================================================ plate, table and messes
def plate(c):
    c.layer(circle(146, 146, 140), PAPER, depth=6, shadow_op=.22)
    c.flat(circle(146, 146, 126), kit.dk(PAPER, .05))
    r = 116
    cols = {(0, 0): RICE, (1, 0): kit.lt(LEAF, .62), (0, 1): kit.lt(PEACH_DK, .55), (1, 1): kit.lt(PINK, .32)}
    foods = {(0, 0): f_rice, (1, 0): f_veg, (0, 1): f_meat, (1, 1): f_fruit}
    for (ix, iy), col in cols.items():
        a0 = {(0, 0): 180, (1, 0): 270, (1, 1): 0, (0, 1): 90}[(ix, iy)]
        sector = poly([(146, 146)] + arc_pts(146, 146, r, a0, a0 + 90, 16))
        c.flat(sector, col)
        qx = 146 + (r * .5) * (1 if ix else -1)
        qy = 146 + (r * .5) * (1 if iy else -1)
        s = .9
        foods[(ix, iy)](P(c, s, qx - 48 * s, qy - 50 * s, faint=True))
    c.stroke(path([(146, 30), (146, 262)]), PAPER, 6)                      # the dividers
    c.stroke(path([(30, 146), (262, 146)]), PAPER, 6)
    c.flat(circle(146, 146, 126) + circle(146, 146, 116), kit.dk(PAPER, .05), rule="evenodd")   # the rim shade


def table_top(c):
    W, H = 290, 140
    c.layer(rrect(2, 2, W, H, 14), WOOD, depth=6)
    for i in (1, 2, 3):
        y = 2 + H * i / 4
        c.stroke(path([(10, y), (W - 8, y)]), kit.dk(WOOD, .14), 3)
    r = kit.rnd("table grain")
    for i in range(6):                                                     # a few grain lines
        x = 20 + i * 44 + r.uniform(-6, 6)
        y = 2 + H * (r.randrange(4) + .5) / 4
        c.stroke(arc(x, y, 12 + r.uniform(0, 8), 200, 340).scale(1, x, y, .5), kit.dk(WOOD, .12), 2, op=.7)
    c.flat(rrect(12, 8, W - 20, 6, 3), kit.lt(WOOD, .3), op=.5)


def stain(c):
    c.flat(blob(46, 50, 30, 22, lumps=8, wobble=.26, key="stain"), BROWN, op=.9)
    c.flat(circle(78, 36, 6) + circle(20, 70, 5) + circle(70, 72, 4) + circle(28, 30, 3.5), BROWN, op=.85)
    c.flat(ellipse(38, 44, 8, 4).rotate(-20, 38, 44), kit.lt(BROWN, .3), op=.6)


def crumbs(c):
    r = kit.rnd("crumbs")
    for i in range(8):
        x, y = 16 + (i % 4) * 20 + r.uniform(-5, 5), 24 + (i // 4) * 36 + r.uniform(-8, 8)
        s = r.uniform(3.5, 6.5)
        col = [BISCUIT, WOOD_DK, kit.dk(BISCUIT, .15)][i % 3]
        c.layer(blob(x, y, s, s * .8, lumps=5, wobble=.3, key=f"crumb{i}"), col, depth=1.5, shadow=False)


def rag(c):
    sh = smooth([(10, 14), (46, 10), (84, 16), (88, 50), (82, 84), (46, 88), (10, 82), (6, 48)], .5)
    c.layer(sh, WATER, depth=3)
    for i in range(4):                                                     # gingham squares
        for j in range(4):
            c.flat(rrect(16 + i * 18, 18 + j * 17, 9, 9, 2), PAPER, op=.75)
    c.layer(poly([(60, 14), (84, 16), (88, 44)]), kit.lt(WATER, .4), depth=2, shadow=False)   # a folded corner
    c.flat(circle(22, 66, 2.5) + circle(30, 74, 2), PAPER, op=.9)         # soapy drops


# ================================================================ bed
def blanket(c):
    sh = smooth([(8, 26), (30, 20), (52, 26), (74, 18), (90, 28), (86, 52), (90, 78), (70, 86), (48, 80), (26, 88),
                 (6, 76), (10, 52)], .5)
    c.layer(sh, LAVENDER, depth=4)
    c.dots([(24 + (i % 4) * 16, 36 + (i // 4) * 18 + (8 if (i % 4) % 2 else 0)) for i in range(12)], 2.6, PAPER, op=.8)
    c.stroke(path([(14, 56), (40, 64), (60, 50), (84, 60)]), kit.dk(LAVENDER, .22), 2.5, op=.6)   # creases
    c.stroke(path([(30, 74), (54, 70)]), kit.dk(LAVENDER, .22), 2.5, op=.6)
    fold = poly([(8, 26), (48, 22), (12, 54)])                            # the turned-over corner
    c.layer(fold, kit.lt(LAVENDER, .3), depth=2, shadow=False)
    c.stroke(path([(14, 54), (14, 70)]), kit.dk(LAVENDER, .22), 2.5, op=.6)


def blanket_folded(c):
    for i, (y, col) in enumerate(((60, kit.dk(LAVENDER, .12)), (44, kit.dk(LAVENDER, .05)), (28, LAVENDER))):
        c.layer(rrect(14, y, 68, 20, 7), col, depth=4, shadow=(i == 0))
        c.flat(rrect(14, y + 13, 68, 4, 2), PAPER, op=.5)                   # the fold edges
    c.flat(star(48, 38, 7), PAPER)
    c.face(30, 38, 4, "sleepy")


def _curtain(c, open_):
    W = 190
    c.layer(rrect(2, 10, W, 10, 5), WOOD_DEEP, depth=3)                    # the rod
    c.layer(rrect(10, 26, W - 16, 148, 12), WOOD, depth=5)                 # the frame
    c.flat(rrect(24, 40, W - 44, 120, 6), GLASS)                           # the glass (pale, no token)
    c.flat(ellipse(70, 130, 30, 12) + circle(60, 122, 14) + circle(80, 120, 16), PAPER, op=.9)   # a cloud
    c.flat(star(128, 70, 10), YELLOW, op=.9)
    c.layer(rrect(W / 2 - 5, 40, 10, 120, 4), kit.lt(WOOD, .12), depth=2, shadow=False)   # cross bars
    c.layer(rrect(24, 94, W - 44, 10, 4), kit.lt(WOOD, .12), depth=2, shadow=False)
    if open_:
        left = poly([(8, 22), (62, 22), (58, 70), (48, 110), (44, 150), (52, 172), (8, 172)])
        dots = [(22 + j * 20, 40 + i * 28 + (8 if j else 0)) for i in range(5) for j in range(2)]
    else:
        left = poly([(8, 22), (W / 2 + 4, 22), (W / 2 + 2, 172), (8, 172)])
        dots = [(22 + j * 22, 40 + i * 28 + (8 if j % 2 else 0)) for i in range(5) for j in range(4)]
    for flip in (False, True):
        sh = left.flip(W / 2 + 1) if flip else left
        c.layer(sh, PINK, depth=4)
        c.dots([((W + 2 - x) if flip else x, y) for x, y in dots if (not open_) or x < 56], 3.2, PAPER)
        if open_:
            tx = (W + 2 - 50) if flip else 50
            c.layer(ellipse(tx, 124, 12, 7), PINK_DK, depth=2, shadow=False)   # the tie-back
        else:
            for x in (26, 44, 62, 80):
                xx = (W + 2 - x) if flip else x
                c.stroke(path([(xx, 30), (xx, 166)]), kit.dk(PINK, .12), 2, op=.6)   # folds
    c.layer(rrect(2, 170, W, 16, 6), WOOD_DK, depth=5)                     # the sill


def curtain_open(c):
    _curtain(c, True)


def curtain_closed(c):
    _curtain(c, False)


def book_open(c):
    W, H = 190, 140
    cover = rrect(4, 14, W - 4, H - 22, 8)
    c.layer(cover, LAVENDER_DK, depth=5)
    left = poly([(14, 24), (W / 2 - 2, 32), (W / 2 - 2, H - 16), (14, H - 24)])
    right = poly([(W / 2 + 2, 32), (W - 10, 24), (W - 10, H - 24), (W / 2 + 2, H - 16)])
    c.layer(left, PAPER, depth=3, shadow=False)
    c.layer(right, PAPER, depth=3, shadow=False)
    c.flat(rect(W / 2 - 2, 30, 4, H - 46), kit.dk(LAVENDER_DK, .3))        # the gutter
    for i in range(5):                                                     # the story's lines
        y = 48 + i * 15
        c.stroke(path([(28, y + 2), (W / 2 - 16 - (18 if i == 4 else 0), y)]), GREY, 3.5)
    c.flat(rrect(W / 2 + 14, 38, W / 2 - 34, H - 66, 8), "#3F3F6E")       # the night picture
    c.flat(circle(W * .72, 72, 20), YELLOW)                                # a crescent moon
    c.flat(circle(W * .72 + 10, 66, 17), "#3F3F6E")
    c.flat(star(W / 2 + 30, 50, 5) + star(W - 34, 96, 4) + star(W / 2 + 36, 92, 3.5), YELLOW)
    c.face(W * .72 - 4, 74, 3.5, "sleepy")
    c.layer(rrect(W / 2 - 12, H - 22, 24, 10, 4), CORAL, depth=2, shadow=False)   # the ribbon
    c.flat(rrect(W / 2 - 2, 20, 4, 12, 2), kit.dk(LAVENDER_DK, .3))


def snack_plate(c):
    c.layer(ellipse(46, 60, 42, 17), PAPER, depth=4)
    c.flat(ellipse(46, 60, 42, 17) + ellipse(46, 60, 34, 12), kit.dk(PAPER, .06), rule="evenodd")

    def biscuit(cx, cy, r):
        sh = circle(cx, cy, r)
        for i in range(10):
            a = math.radians(i * 36)
            sh = sh + circle(cx + r * math.cos(a), cy + r * math.sin(a), r * .22)
        return sh

    c.layer(biscuit(32, 48, 14), BISCUIT, depth=3)
    c.dots([(26, 44), (36, 52), (34, 42), (28, 54)], 2, WOOD_DEEP)
    c.layer(biscuit(62, 50, 14), BISCUIT, depth=3)
    c.face(62, 50, 4.5, "happy")


# ================================================================ the list and build()
PROPS = {
    # teeth
    "toothbrush": (100, 100, toothbrush), "toothpaste": (100, 100, toothpaste), "cup": (100, 100, cup),
    "mouth_big": (400, 300, mouth_big), "dirt": (100, 100, dirt), "bubble": (100, 100, bubble),
    "hands": (200, 150, hands),
    # washing and bathing
    "soap": (100, 100, soap), "tap_on": (100, 100, tap_on), "tap_off": (100, 100, tap_off),
    "towel": (100, 100, towel), "hairdryer": (100, 100, hairdryer), "bathtub_full": (300, 200, bathtub_full),
    "lotion": (100, 100, lotion), "temp_hot": (100, 100, temp_hot), "temp_warm": (100, 100, temp_warm),
    "temp_cold": (100, 100, temp_cold),
    # toilet
    "toilet_open": (100, 100, toilet_open), "toilet_closed": (100, 100, toilet_closed),
    "paper": (100, 100, paper), "flush": (100, 100, flush),
    # clothes
    "cloth_tshirt": (100, 100, cloth_tshirt), "cloth_jacket": (100, 100, cloth_jacket),
    "cloth_raincoat": (100, 100, cloth_raincoat), "cloth_shorts": (100, 100, cloth_shorts),
    "cloth_pants": (100, 100, cloth_pants), "cloth_hat": (100, 100, cloth_hat), "cloth_boots": (100, 100, cloth_boots),
    "cloth_shoes_l": (100, 100, cloth_shoes_l), "cloth_shoes_r": (100, 100, cloth_shoes_r),
    "button": (100, 100, button), "umbrella": (100, 100, umbrella),
    # food
    "plate": (300, 300, plate), "table_top": (300, 150, table_top), "stain": (100, 100, stain),
    "crumbs": (100, 100, crumbs), "rag": (100, 100, rag),
    # bed
    "blanket": (100, 100, blanket), "blanket_folded": (100, 100, blanket_folded),
    "curtain_open": (200, 200, curtain_open), "curtain_closed": (200, 200, curtain_closed),
    "book_open": (200, 150, book_open), "snack_plate": (100, 100, snack_plate),
}
# food drawn through a painter (100 x 100 each)
FOODS = {
    "food_rice": f_rice, "food_veg": f_veg, "food_meat": f_meat, "food_fruit": f_fruit, "food_apple": f_apple,
    "food_banana": f_banana, "food_carrot": f_carrot, "food_milk": f_milk, "food_egg": f_egg, "food_fish": f_fish,
    "spoon": spoon, "bowl": bowl, "chopsticks": chopsticks, "cup_water": cup_water,
    "cup_water_full": cup_water_full, "pot": pot,
}


def all_props():
    out = dict(PROPS)
    for name, fn in FOODS.items():
        out[name] = (100, 100, (lambda f: (lambda c: f(P(c))))(fn))
    return out


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, (w, h, fn) in all_props().items():
        c = ctx(w, h)
        fn(c)
        kit.write_svg(OUT / f"{name}.svg", c.svg(), (w, h))
        total += 1
    print(f"props_care: {total} files in {OUT.relative_to(kit.ROOT)}")
    return total


if __name__ == "__main__":
    build()
