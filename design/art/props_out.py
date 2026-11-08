"""Mini-game props, part B (school, toys and chores, park and street, market, clinic, happenings):
app/assets/art/props/<id>.svg, 100 x 100 unless docs/art.md says otherwise, transparent background.

Every prop is cut paper (kit.py): a few soft-coloured layers with thickness and a shadow, a small
face where it is cute. People are Q-version paper puppets (`puppet`): a big round head, dot eyes,
blush, a simple body. 100 x 100 files are drawn with `scale=0.7` so the depths and shadows stay
inside the ~8 px margin; the bigger files use the scene scale. Deterministic: no randomness.
"""
import math

import kit
from kit import (BLUSH, CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH,
                 PEACH_DK, PINK, PINK_DK, SKY, WHITE, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, arc, circle, ellipse, heart,
                 path, poly, rect, rrect, smooth, star)

OUT = kit.ART / "props"
SMALL_SCALE = 0.7

# a few colours the palette does not have
RED = "#E8706A"
BLUE = "#7FB3E6"
BLUE_DK = "#4F86C2"
GREEN = "#7DBE86"       # the post office / recycling green
HAIR = "#6B4A33"
HAIR_GREY = "#CFC6C9"
METAL = "#B9BCC9"
SAND = "#F5E3B5"
SKIN_2 = "#F2C9A6"
SKIN_3 = "#D9A57C"


def ctx(w, h):
    return kit.Ctx(w, h, scale=SMALL_SCALE if max(w, h) <= 120 else 1.0)


# ---------------------------------------------------------------- shape helpers
def drop_shape(cx, cy, r):
    """A teardrop: round bottom, pointed top."""
    k = kit.KAPPA
    top = cy - 1.7 * r
    return kit.Shape([
        ("M", cx, top),
        ("C", cx + r * .35, top + r * .6, cx + r, cy - r * .6, cx + r, cy),
        ("C", cx + r, cy + r * k, cx + r * k, cy + r, cx, cy + r),
        ("C", cx - r * k, cy + r, cx - r, cy + r * k, cx - r, cy),
        ("C", cx - r, cy - r * .6, cx - r * .35, top + r * .6, cx, top),
        ("Z",)])


def leaf(cx, cy, w, h, deg=0.0):
    """A pointed leaf (horizontal), rotated."""
    s = smooth([(cx - w / 2, cy), (cx - w * .15, cy - h / 2), (cx + w * .3, cy - h * .35), (cx + w / 2, cy),
                (cx + w * .3, cy + h * .35), (cx - w * .15, cy + h / 2)], .6)
    return s.rotate(deg, cx, cy) if deg else s


def paw(cx, cy, s):
    """A paw print about s wide."""
    sh = ellipse(cx, cy + s * .18, s * .32, s * .26)
    for i, (dx, dy) in enumerate(((-.36, -.16), (-.13, -.36), (.13, -.36), (.36, -.16))):
        sh = sh + circle(cx + dx * s, cy + dy * s, s * .12)
    return sh


def flower(cx, cy, r, petals=5):
    sh = kit.Shape()
    for i in range(petals):
        a = 2 * math.pi * i / petals - math.pi / 2
        sh = sh + circle(cx + r * .6 * math.cos(a), cy + r * .6 * math.sin(a), r * .42)
    return sh


def spiral(cx, cy, r0, r1, turns=2.0, steps=48):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return path(pts)


def sock_shape(x, y, s):
    """A sock about s tall: a cuff at the top-left, the foot pointing right."""
    return smooth([(x, y), (x + s * .36, y), (x + s * .36, y + s * .5), (x + s * .78, y + s * .66),
                   (x + s * .78, y + s * .9), (x + s * .5, y + s * .98), (x + s * .1, y + s * .78),
                   (x, y + s * .55)], .55)


def zigzag(x0, y, x1, amp, teeth):
    pts = [(x0, y)]
    for i in range(1, teeth * 2 + 1):
        pts.append((x0 + (x1 - x0) * i / (teeth * 2), y + (-amp if i % 2 else amp)))
    return path(pts)


def mug_arc(c, cx, cy, r, a0, a1, col, w):
    c.stroke(arc(cx, cy, r, a0, a1), col, w)


def sound_lines(c, cx, cy, r, side=1, col=DARK, w=2.5, n=2):
    """Two short arcs opening away from (cx, cy): "it makes a sound"."""
    for i in range(n):
        rr = r + i * r * .45
        if side > 0:
            c.stroke(arc(cx, cy, rr, -35, 35), col, w)
        else:
            c.stroke(arc(cx, cy, rr, 145, 215), col, w)


# ---------------------------------------------------------------- people: Q-version paper puppets (200 x 260)
def hair_cap(cx, cy, r, bang=-.26, scallops=4, puff=1.07):
    pts = []
    for i in range(9):
        a = math.radians(180 + 180 * i / 8)
        pts.append((cx + r * puff * math.cos(a), cy + r * puff * math.sin(a)))
    y0 = cy + r * bang
    for i in range(scallops + 1):
        t = i / scallops
        pts.append((cx + r * puff - 2 * r * puff * t, y0 + (r * .13 if i % 2 else 0)))
    return smooth(pts, .5)


def puppet(c, cx=96, ground=248, skin=PEACH, shirt=MINT, bottom=SKY, hair=HAIR, style="short", mood="happy",
           kid=False, dress=False, coat=None, apron=None, cap=None, glasses=False, shoes=WOOD_DEEP, face_size=13,
           legs=True):
    """A paper puppet standing with its feet at `ground`. style: short, bun, pigtails, bob, none.
    coat: a colour for a long open coat; apron: a colour for an apron; cap: a colour for a cap with a visor."""
    r = 48 if not kid else 50
    hy = 64 if not kid else 78
    torso_top = hy + r - 10
    torso_w = 104 if not kid else 92
    legs_top = ground - 56
    # pigtails and the bun's ribbon go behind the head
    if style == "pigtails":
        for sx in (-1, 1):
            c.layer(circle(cx + sx * r * 1.1, hy + r * .25, r * .34), hair, depth=4)
    if style == "bun":
        c.layer(circle(cx, hy - r * 1.02, r * .36), hair, depth=4)
    # legs and shoes
    if legs:
        for sx in (-1, 1):
            lx = cx + sx * 22
            c.layer(rrect(lx - 14, legs_top, 28, ground - legs_top - 6, 10), bottom if not dress else skin, depth=4)
            c.layer(ellipse(lx + sx * 2, ground - 7, 20, 9), shoes, depth=3)
    # the body
    if dress:
        body = poly([(cx - torso_w * .36, torso_top), (cx + torso_w * .36, torso_top),
                     (cx + torso_w * .58, legs_top + 14), (cx - torso_w * .58, legs_top + 14)])
        body = smooth([(cx - torso_w * .36, torso_top), (cx + torso_w * .36, torso_top),
                       (cx + torso_w * .58, legs_top + 10), (cx, legs_top + 16), (cx - torso_w * .58, legs_top + 10)], .3)
        c.layer(body, shirt, depth=5)
    else:
        c.layer(rrect(cx - torso_w / 2, torso_top, torso_w, legs_top - torso_top + 10, 22), shirt, depth=5)
    if coat:
        # an open coat: two long flaps with a collar showing the shirt in a V
        w = torso_w / 2 + 10
        c.layer(poly([(cx - w, torso_top - 2), (cx - 14, torso_top - 2), (cx - 4, torso_top + 40), (cx - 6, legs_top + 24),
                      (cx - w, legs_top + 24)]), coat, depth=4)
        c.layer(poly([(cx + 14, torso_top - 2), (cx + w, torso_top - 2), (cx + w, legs_top + 24), (cx + 6, legs_top + 24),
                      (cx + 4, torso_top + 40)]), coat, depth=4)
    if apron:
        aw = torso_w * .62
        c.layer(rrect(cx - aw / 2, torso_top + 16, aw, legs_top - torso_top + 4, 12), apron, depth=4)
        c.stroke(path([(cx - aw / 2 + 6, torso_top + 18), (cx - 10, torso_top - 4)]), kit.dk(apron, .3), 4)
        c.stroke(path([(cx + aw / 2 - 6, torso_top + 18), (cx + 10, torso_top - 4)]), kit.dk(apron, .3), 4)
        c.flat(rrect(cx - 16, torso_top + 52, 32, 22, 6), kit.lt(apron, .3))
    # arms and hands
    for sx in (-1, 1):
        ax = cx + sx * (torso_w / 2 + 2)
        c.layer(rrect(ax - 12, torso_top + 8, 24, 58, 12), coat or shirt, depth=4)
        c.layer(circle(ax, torso_top + 72, 13), skin, depth=3)
    # head
    c.layer(rrect(cx - 14, hy + r - 14, 28, 18, 8), skin, depth=0, shadow=False)        # neck
    c.layer(circle(cx, hy, r), skin, depth=5)
    for sx in (-1, 1):                                                                     # ears
        c.layer(circle(cx + sx * r * .98, hy + 4, r * .18), skin, depth=2, shadow=False)
    c.face(cx, hy + 6, face_size, mood)
    if style != "none":
        c.layer(hair_cap(cx, hy, r, puff=1.08 if style != "bob" else 1.12,
                         bang=-.26 if style != "bob" else -.3, scallops=4 if style != "short" else 5), hair, depth=4)
    if style == "bob":                                                                     # the sides come down
        for sx in (-1, 1):
            c.layer(rrect(cx + sx * r * 1.04 - 11, hy - 6, 22, r * .9, 10), hair, depth=3, shadow=False)
    if glasses:
        for sx in (-1, 1):
            c.stroke(circle(cx + sx * face_size, hy + 6, face_size * .75), DARK, 2.5)
        c.stroke(path([(cx - face_size * .25, hy + 4), (cx + face_size * .25, hy + 4)]), DARK, 2.5)
    if cap:
        c.layer(rrect(cx - r * 1.1, hy - r * 1.2, r * 2.2, r * .95, r * .6, rbl=4, rbr=4), cap, depth=4)
        c.layer(ellipse(cx + r * .3, hy - r * .25, r * .95, r * .16), kit.dk(cap, .18), depth=3, shadow=False)
    return hy, r, torso_top


# ---------------------------------------------------------------- school
def p_bag_open(c):
    # straps behind, the open flap folded back above, the bag body, a pocket with a face
    c.layer(rrect(22, 2, 48, 30, 12), kit.lt(RED, .2), depth=3)                   # the flap, folded back
    for x in (24, 58):
        c.layer(rrect(x, 16, 10, 24, 5), kit.dk(RED, .25), depth=2)                # straps behind
    c.layer(rrect(14, 32, 64, 56, 14), RED, depth=5)
    c.flat(rrect(18, 30, 56, 20, 10), kit.dk(RED, .35))                            # the open mouth
    c.flat(rrect(22, 34, 48, 12, 6), kit.dk(RED, .6))
    c.layer(rrect(36, 20, 20, 22, 3), CREAM, depth=2)                              # the notebook peeking out
    c.flat(star(46, 30, 5), YELLOW)
    c.layer(rrect(28, 58, 36, 24, 9), kit.lt(RED, .2), depth=3)                    # the front pocket
    c.face(46, 69, 5.5, "happy")


def p_item_bottle(c):
    c.layer(rrect(36, 2, 20, 12, 5), MINT_DK, depth=3)                            # cap
    c.layer(rrect(30, 12, 32, 10, 4), MINT, depth=2, shadow=False)
    c.layer(rrect(26, 20, 40, 68, 14), SKY, depth=5)
    c.flat(rrect(30, 40, 32, 22, 6), PAPER)                                        # label
    c.flat(star(46, 51, 8), YELLOW)
    c.flat(rrect(31, 24, 6, 20, 3), WHITE, op=.6)                                  # shine


def p_item_hanky(c):
    sq = rrect(14, 24, 62, 58, 8)
    c.layer(sq, PINK, depth=5)
    c.dots([(26 + i * 16, 36 + j * 16 + (8 if i % 2 else 0)) for i in range(4) for j in range(3) if 36 + j * 16 + (8 if i % 2 else 0) < 78], 3, PAPER)
    c.layer(poly([(14, 24), (76, 24), (14, 76)]), kit.lt(PINK, .2), depth=3)      # the folded-over corner
    c.flat(heart(36, 46, 14), PINK_DK)


def p_item_book(c):
    c.layer(rrect(14, 12, 64, 76, 8), CREAM, depth=5)
    c.layer(rrect(14, 12, 12, 76, 5, rtr=0, rbr=0), WOOD_DK, depth=3, shadow=False)       # spine
    c.flat(rrect(36, 24, 34, 50, 6), kit.lt(CORAL, .4))
    c.flat(star(53, 44, 13), YELLOW)
    c.stroke(path([(42, 62), (64, 62)]), CORAL, 2.5)
    c.stroke(path([(42, 68), (58, 68)]), CORAL, 2.5)


def p_bus(c):
    # 300 x 200: a yellow kindergarten bus, side view, cab at the right with a face
    body = rrect(10, 40, 270, 120, 24)
    c.layer(body, YELLOW, depth=6)
    c.flat(rrect(10, 112, 270, 14, 4), kit.dk(YELLOW, .12))                       # the side stripe
    for i in range(3):                                                             # windows with little passengers
        x = 32 + i * 58
        c.layer(rrect(x, 54, 46, 44, 10), SKY, depth=3, shadow=False)
        c.layer(circle(x + 23, 92, 15), (PEACH, SKIN_2, SKIN_3)[i], depth=2, shadow=False)
        c.layer(hair_cap(x + 23, 92, 15, puff=1.05), (HAIR, kit.dk(HAIR, .3), kit.lt(HAIR, .2))[i], depth=0, shadow=False)
        c.face(x + 23, 94, 4, ("happy", "smile", "open")[i])
    c.layer(rrect(214, 50, 56, 50, 12), SKY, depth=3, shadow=False)                # windscreen
    c.face(240, 134, 11, "happy")                                                  # the bus's face on the bonnet
    c.layer(circle(272, 140, 9), CREAM, depth=2, shadow=False)                     # headlight
    c.layer(circle(14, 138, 7), RED, depth=2, shadow=False)                        # tail light
    for x in (70, 220):                                                            # wheels
        c.layer(circle(x, 162, 24), DARK, depth=4)
        c.flat(circle(x, 162, 11), GREY)
    c.layer(rrect(120, 28, 60, 16, 8), RED, depth=3)                               # the sign on the roof
    c.flat(star(150, 36, 6), PAPER)


def p_seatbelt(c):
    # a strap coming in from the top-left, the tongue going into the buckle, and "click" lines
    c.layer(poly([(2, 8), (16, 2), (40, 34), (28, 42)]), kit.dk(GREY, .5), depth=3)    # the strap
    c.layer(rrect(34, 30, 16, 26, 4).rotate(-36, 42, 43), METAL, depth=3)           # the tongue going in
    c.layer(rrect(22, 46, 62, 42, 10), kit.dk(GREY, .32), depth=5)                  # the buckle
    c.flat(rrect(30, 52, 46, 10, 5), kit.dk(GREY, .6))                              # the slot
    c.layer(circle(64, 74, 8), RED, depth=2, shadow=False)                          # the button
    c.flat(circle(61, 71, 2.6), WHITE, op=.7)
    for a in (-100, -60, -20):                                                      # click!
        ra = math.radians(a)
        x0, y0 = 72 + 12 * math.cos(ra), 40 + 12 * math.sin(ra)
        c.stroke(path([(x0, y0), (x0 + 9 * math.cos(ra), y0 + 9 * math.sin(ra))]), CORAL, 3)


def p_cubby(c, mark):
    c.layer(rrect(10, 14, 72, 74, 8), WOOD, depth=5)                               # the box
    c.flat(rrect(18, 22, 56, 58, 5), kit.dk(WOOD, .3))                             # the dark inside
    c.flat(rrect(18, 66, 56, 14, 3), kit.dk(WOOD, .18))                            # the shelf floor
    c.layer(rrect(32, 6, 28, 22, 6), PAPER, depth=3)                               # the name tag
    if mark == "star":
        c.flat(star(46, 17, 9), YELLOW)
    elif mark == "heart":
        c.flat(heart(46, 17, 15), PINK_DK)
    else:
        c.flat(flower(46, 17, 10), PINK)
        c.flat(circle(46, 17, 3.2), YELLOW)


def p_teacher(c):
    puppet(c, shirt=LAVENDER, bottom=LAVENDER_DK, style="bun", dress=True, mood="happy")
    c.flat(rrect(84, 110, 24, 8, 4), PINK_DK)                                       # a bow at the collar


def p_classmate_1(c):
    puppet(c, kid=True, shirt=MINT, bottom=BLUE, skin=SKIN_2, style="short", mood="happy")
    c.flat(star(96, 160, 10), YELLOW)


def p_classmate_2(c):
    puppet(c, kid=True, shirt=PINK, bottom=PINK_DK, style="pigtails", dress=True, mood="open")
    for sx in (-1, 1):
        c.flat(circle(96 + sx * 55, 90, 5), CORAL)                                 # hair ties


def p_mat(c):
    # 200 x 100: a nap mat lying flat with a pillow at the left end
    c.layer(rrect(6, 18, 180, 64, 14), MINT, depth=5)
    c.dots([(40 + i * 28, 36 + (12 if i % 2 else 0)) for i in range(5)], 3, PAPER)
    c.dots([(54 + i * 28, 66 - (12 if i % 2 else 0)) for i in range(4)], 3, PAPER)
    c.layer(rrect(14, 26, 54, 48, 12), PAPER, depth=4)                             # pillow
    c.face(41, 48, 6, "sleepy")


def p_hands_clap(c):
    # two hands (palm, four fingers, a thumb) tilted towards each other, little motion lines where they meet
    def hand():
        sh = rrect(10, 46, 30, 36, 11)                                             # the palm
        for i, h in enumerate((22, 27, 25, 19)):
            sh = sh + rrect(11 + i * 7.2, 50 - h, 6.6, h + 6, 3.3)                 # fingers
        sh = sh + rrect(34, 54, 16, 9, 4.5).rotate(-50, 36, 58)                    # the thumb, towards the middle
        return sh.rotate(14, 25, 64)
    c.layer(hand(), PEACH, depth=4)
    c.layer(hand().flip(46), SKIN_2, depth=4)
    for dx in (-10, 0, 10):
        c.stroke(path([(46 + dx, 22), (46 + dx * 1.6, 10)]), CORAL, 2.5)
    c.stroke(path([(28, 30), (18, 24)]), CORAL, 2.5)
    c.stroke(path([(64, 30), (74, 24)]), CORAL, 2.5)


def p_footprint(c):
    for x in (14, 50):
        sh = ellipse(x + 14, 60, 13, 22) + circle(x + 10, 26, 6) + circle(x + 20, 24, 5) + circle(x + 27, 29, 4) \
            + circle(x + 31, 37, 3.5)
        sh = ellipse(x + 14, 62, 13, 20) + ellipse(x + 15, 42, 15, 12) + circle(x + 7, 24, 6) + circle(x + 17, 21, 5) \
            + circle(x + 25, 24, 4.2) + circle(x + 30, 31, 3.6)
        c.layer(sh if x < 40 else sh.flip(x + 16), SKIN_3, depth=3)


# ---------------------------------------------------------------- toys and chores
def car_shape(x, y, w):
    """A little side-view car body about w wide with its wheels' bottom at y."""
    h = w * .44
    body = rrect(x, y - h * .62, w, h * .62, h * .3)
    cab = rrect(x + w * .22, y - h, w * .5, h * .5, h * .22)
    return body + cab


def p_toy_car(c):
    c.layer(car_shape(8, 72, 76), CORAL, depth=5)
    c.flat(rrect(30, 42, 28, 16, 5), SKY)                                          # window
    c.face(46, 64, 6, "smile")
    for x in (26, 66):
        c.layer(circle(x, 74, 10), DARK, depth=3)
        c.flat(circle(x, 74, 4), GREY)
    c.flat(circle(81, 60, 3.5), CREAM)


def p_toy_block(c):
    blocks = ((28, 60, RED, "star"), (24, 34, YELLOW, "heart"), (30, 8, BLUE, "circle"))
    for x, y, col, mark in blocks:
        c.layer(rrect(x, y, 28, 28, 5), col, depth=5)
        if mark == "star":
            c.flat(star(x + 14, y + 14, 9), PAPER)
        elif mark == "heart":
            c.flat(heart(x + 14, y + 15, 15), PAPER)
        else:
            c.flat(circle(x + 14, y + 14, 7), PAPER)


def p_toy_doll(c):
    for sx in (-1, 1):
        c.layer(circle(46 + sx * 24, 34, 8), HAIR, depth=3)                        # pigtails
    c.layer(smooth([(30, 50), (62, 50), (74, 86), (46, 90), (18, 86)], .3), PINK, depth=4)     # dress
    c.dots([(38, 72), (54, 72), (46, 82)], 2.5, PAPER)
    for sx in (-1, 1):
        c.layer(circle(46 + sx * 26, 66, 6), PEACH, depth=2)                        # hands
    c.layer(circle(46, 32, 22), PEACH, depth=4)
    c.face(46, 36, 6, "happy")
    c.layer(hair_cap(46, 32, 22), HAIR, depth=3)
    c.flat(heart(46, 14, 8), CORAL)


def p_toy_ball(c):
    c.layer(circle(46, 48, 36), CORAL, depth=5)
    c.flat(ellipse(46, 48, 36, 13), PAPER)
    c.flat(ellipse(46, 48, 36, 7), SKY)
    c.flat(star(46, 48, 8), YELLOW)
    c.flat(ellipse(32, 30, 7, 4).rotate(-40, 32, 30), WHITE, op=.6)


def p_box(c, kind):
    # an open box with the toy's picture on the front
    c.layer(rrect(10, 30, 74, 58, 8), PEACH, depth=5)
    c.flat(rrect(16, 34, 62, 12, 5), kit.dk(PEACH, .4))                            # the opening
    c.layer(poly([(10, 30), (2, 14), (40, 14), (46, 30)]), kit.dk(PEACH, .1), depth=3, shadow=False)       # flaps
    c.layer(poly([(46, 30), (52, 14), (90, 14), (84, 30)]), kit.dk(PEACH, .16), depth=3, shadow=False)
    c.flat(rrect(22, 50, 50, 32, 6), PAPER)                                        # the picture label
    if kind == "car":
        c.flat(car_shape(28, 74, 38), CORAL)
        c.dots([(37, 75), (57, 75)], 4.5, DARK)
    elif kind == "block":
        c.flat(rrect(30, 66, 14, 14, 2), RED)
        c.flat(rrect(48, 66, 14, 14, 2), BLUE)
        c.flat(rrect(39, 54, 14, 13, 2), YELLOW)
    else:
        c.flat(circle(47, 62, 9), PEACH)
        c.flat(hair_cap(47, 62, 9), HAIR)
        c.flat(poly([(40, 70), (54, 70), (58, 80), (36, 80)]), PINK)
        c.dots([(44, 63), (50, 63)], 1.3, DARK)


def p_broom(c):
    c.layer(rrect(58, 2, 10, 58, 5).rotate(26, 63, 30), WOOD, depth=3)              # the handle
    head = poly([(34, 58), (60, 50), (78, 86), (42, 94)])
    c.layer(head, YELLOW, depth=4)
    c.layer(rrect(38, 50, 26, 10, 4).rotate(-14, 51, 55), WOOD_DK, depth=2, shadow=False)   # the band
    for i in range(4):
        t = (i + .5) / 4
        x0, y0 = 36 + (60 - 36) * t, 60 + (52 - 60) * t
        c.stroke(path([(x0, y0 + 6), (x0 + 14, y0 + 34)]), kit.dk(YELLOW, .25), 2)


def p_dustpan(c):
    # seen from the front: a back wall, a flat floor opening towards us, a handle going up at the back
    c.layer(rrect(60, 4, 12, 44, 6).rotate(18, 66, 26), BLUE, depth=3)              # handle
    c.layer(poly([(20, 42), (72, 42), (76, 58), (16, 58)]), kit.dk(SKY, .22), depth=4)     # the back wall
    c.layer(poly([(16, 58), (76, 58), (86, 84), (6, 84)]), SKY, depth=5)             # the floor
    c.flat(rrect(6, 82, 80, 5, 2), kit.dk(SKY, .25))                                # the thin front lip
    c.dots([(30, 70), (46, 66), (60, 74), (40, 78)], 2.6, WOOD_DK)                  # crumbs swept in
    c.face(46, 50, 4, "smile")


def p_shoe_rack(c):
    # 200 x 120: a wooden rack with two shelves, a few pairs of shoes
    for y in (56, 100):
        c.layer(rrect(8, y, 176, 12, 5), WOOD, depth=4)
    for x in (10, 170):
        c.layer(rrect(x, 10, 12, 102, 5), WOOD_DK, depth=3, shadow=False)
    shoes = ((28, 54, CORAL), (104, 54, SKY), (28, 98, LEAF), (104, 98, YELLOW))
    for x, y, col in shoes:
        for i in range(2):
            sx = x + i * 34
            c.layer(rrect(sx, y - 18, 30, 18, 7, rbr=4, rbl=4) + circle(sx + 9, y - 16, 9), col, depth=3)
            c.flat(circle(sx + 20, y - 12, 3), PAPER)
            c.flat(rrect(sx + 2, y - 5, 26, 4, 2), kit.dk(col, .25))


def p_sock(c, kind):
    sh = sock_shape(16, 10, 76)
    c.layer(sh, PAPER, depth=5)
    c.flat(rrect(16, 10, 28, 12, 4, rbl=0, rbr=0), GREY if kind != "stars" else YELLOW, op=.8)   # cuff
    if kind == "stripes":
        for y in (34, 48):
            c.flat(rrect(16, y, 27, 7, 1), RED)
        c.flat(poly([(44, 60), (74, 71), (74, 78), (40, 66)]), RED)
    elif kind == "dots":
        c.dots([(26, 34), (36, 44), (24, 52), (50, 62), (66, 72), (42, 72), (58, 82)], 3.6, BLUE)
    else:
        for x, y, r in ((29, 36, 6), (28, 56, 5), (48, 66, 6), (66, 76, 5)):
            c.flat(star(x, y, r), YELLOW)
    c.flat(ellipse(34, 60, 6, 3).rotate(-40, 34, 60), WHITE, op=.5)


def p_shirt_hanging(c):
    c.stroke(arc(46, 10, 6, 100, 360), WOOD_DEEP, 2.5)                              # hook
    c.stroke(path([(46, 16), (16, 36), (76, 36), (46, 16)]), WOOD_DEEP, 3.5)        # the hanger
    shirt = poly([(26, 40), (36, 32), (46, 36), (56, 32), (66, 40), (72, 54), (62, 58), (60, 86), (32, 86), (30, 58),
                  (20, 54)])
    c.layer(shirt, SKY, depth=5)
    c.flat(smooth([(36, 33), (46, 38), (56, 33), (50, 44), (42, 44)], .3), kit.dk(SKY, .2))      # the collar
    c.flat(heart(46, 64, 14), PINK_DK)


def p_peg(c):
    # a wooden clothes peg standing up, its spring in the middle
    # the two halves are apart at the top (where you squeeze) and meet at the bottom (the jaws)
    for sx, col in ((-1, WOOD), (1, kit.dk(WOOD, .1))):
        leg = poly([(46 + sx * 5, 6), (46 + sx * 21, 6), (46 + sx * 19, 44), (46 + sx * 15, 56), (46 + sx * 13, 90),
                    (46 + sx * 1, 90), (46 + sx * 1, 60), (46 + sx * 3, 46)])
        c.layer(leg, col, depth=4)
    c.flat(circle(46, 72, 3), kit.dk(WOOD, .35))                                    # the little hole between the jaws
    c.layer(rrect(30, 42, 32, 12, 6), METAL, depth=3)                               # the spring
    c.stroke(path([(36, 48), (56, 48)]), kit.dk(METAL, .3), 2.5)
    c.flat(circle(46, 48, 3.5), kit.dk(METAL, .3))


def p_basket(c):
    # a laundry basket with a shirt and a sock peeking out
    c.layer(rrect(18, 22, 44, 22, 10), SKY, depth=3)
    c.layer(sock_shape(50, 16, 30), PAPER, depth=3)
    c.flat(rrect(50, 16, 11, 5, 2), RED)
    body = poly([(10, 36), (84, 36), (76, 88), (18, 88)])
    c.layer(body, WOOD, depth=5)
    for i in range(4):
        y = 46 + i * 11
        c.stroke(path([(14, y), (80, y)]), kit.dk(WOOD, .18), 2.5)
    for x in (30, 47, 64):
        c.stroke(path([(x, 40), (x - 2, 84)]), kit.dk(WOOD, .18), 2.5)
    c.layer(rrect(6, 30, 82, 12, 6), WOOD_DK, depth=3)                              # the rim
    c.face(47, 66, 7, "smile")


def p_watering_can(c):
    c.layer(rrect(22, 36, 44, 50, 10), MINT, depth=5)                               # the body
    c.layer(rrect(28, 26, 32, 14, 6), MINT_DK, depth=3)                              # the neck
    c.stroke(arc(44, 36, 22, 180, 360), MINT_DK, 6)                                  # the top handle
    c.layer(poly([(62, 56), (84, 24), (92, 30), (72, 62)]), MINT, depth=3)            # the spout
    c.layer(circle(86, 24, 9), MINT_DK, depth=2, shadow=False)                       # the rose
    c.dots([(82, 22), (88, 20), (86, 27)], 1.3, DARK)
    for i, (x, y) in enumerate(((78, 44), (84, 54), (90, 48))):
        c.flat(drop_shape(x, y, 3), SKY)
    c.face(44, 62, 6, "happy")


def p_plant(c, wilt=False):
    pot = poly([(20, 56), (72, 56), (66, 88), (26, 88)])
    if not wilt:
        for x, y, a in ((46, 36, -90), (30, 44, -140), (62, 44, -40), (36, 26, -110), (56, 26, -70)):
            c.layer(leaf(x, y, 24, 12, a), LEAF if (x + y) % 3 else LEAF_DK, depth=3)
        c.stroke(path([(46, 56), (46, 34)]), LEAF_DK, 3)
    else:
        col = kit.mix(LEAF, WOOD_DK, .55)
        for x, y, a in ((26, 52, 30), (66, 52, 150), (34, 46, 60), (58, 46, 120), (46, 42, 90)):
            c.layer(leaf(x, y, 22, 10, a), col, depth=3)
        c.stroke(path([(46, 56), (46, 44)]), kit.dk(col, .2), 3)
    c.layer(pot, PEACH_DK if not wilt else kit.mix(PEACH_DK, GREY, .3), depth=5)
    c.layer(rrect(16, 50, 60, 12, 5), PEACH if not wilt else kit.mix(PEACH, GREY, .3), depth=3)
    c.face(46, 74, 6, "happy" if not wilt else "sleepy")


def p_kibble_bag(c):
    c.layer(rrect(18, 14, 56, 74, 10), PEACH, depth=5)
    c.layer(rrect(16, 10, 60, 14, 5), PEACH_DK, depth=3)                             # the folded top
    c.flat(rrect(26, 34, 40, 42, 8), PAPER)
    c.flat(paw(46, 56, 26), WOOD_DK)
    c.dots([(32, 40), (60, 40)], 2.4, CORAL)


def p_buddy_bowl(c):
    c.layer(poly([(10, 42), (82, 42), (74, 84), (18, 84)]), CORAL, depth=5)
    c.layer(ellipse(46, 42, 38, 11), kit.dk(CORAL, .35), depth=0, shadow=False)      # the inside, seen from above
    c.flat(ellipse(46, 42, 30, 7), WOOD_DK)                                           # kibble
    c.dots([(34, 41), (46, 44), (58, 41), (40, 46), (52, 46)], 2.2, kit.dk(WOOD_DK, .3))
    c.flat(paw(46, 64, 20), PAPER)


def p_trash_bag(c):
    col = kit.dk(GREY, .5)
    c.layer(smooth([(46, 18), (62, 26), (76, 40), (82, 66), (68, 88), (24, 88), (10, 66), (16, 40), (30, 26)], .5), col, depth=5)
    c.layer(poly([(34, 24), (46, 8), (58, 24), (54, 30), (38, 30)]), kit.lt(col, .1), depth=3)       # the knot
    c.flat(ellipse(32, 40, 8, 5).rotate(-30, 32, 40), WHITE, op=.18)
    c.face(46, 60, 7, "smile", blush=kit.lt(col, .35))


def p_recycle_paper(c):
    for i, col in enumerate((kit.lt(SKY, .5), CREAM, PAPER)):
        y = 30 + (2 - i) * 14
        c.layer(rrect(18 + i * 4, y - 20, 56, 40, 4).rotate((i - 1) * 6, 46, y), col, depth=3)
    for y in (18, 26, 34):
        c.stroke(path([(34, y), (64, y)]), GREY, 2.5)


def p_recycle_bottle(c):
    c.layer(rrect(38, 4, 16, 12, 3), BLUE_DK, depth=2)
    c.layer(smooth([(38, 16), (54, 16), (58, 30), (66, 40), (66, 84), (26, 84), (26, 40), (34, 30)], .35),
            kit.lt(SKY, .3), depth=4, op=.95)
    c.flat(rrect(30, 50, 32, 18, 4), BLUE)                                             # the label
    c.flat(rrect(31, 22, 6, 50, 3), WHITE, op=.55)


def p_recycle_food(c):
    c.layer(poly([(14, 40), (78, 40), (70, 88), (22, 88)]), LEAF, depth=5)
    c.layer(rrect(10, 34, 72, 12, 5), LEAF_DK, depth=3)
    # a banana peel and an apple core leaning out of the bucket
    ban = smooth([(16, 36), (18, 20), (28, 8), (42, 6), (46, 12), (34, 18), (28, 30), (30, 40)], .45)
    c.layer(ban, YELLOW, depth=3)
    c.flat(rrect(40, 5, 6, 5, 2), WOOD_DK)                                           # the stem
    c.layer(poly([(54, 12), (76, 12), (68, 24), (76, 38), (54, 38), (62, 24)]), PAPER, depth=3)   # the apple core
    c.flat(rrect(54, 8, 22, 7, 3), RED)
    c.flat(rrect(54, 36, 22, 6, 3), RED)
    c.dots([(65, 22), (65, 28)], 1.4, DARK)
    c.face(46, 64, 6, "smile")


def p_bin(c, col, kind):
    body = poly([(16, 32), (76, 32), (70, 86), (22, 86)])
    c.layer(body, col, depth=5)
    c.layer(rrect(10, 22, 72, 14, 6), kit.dk(col, .12), depth=3)                         # the lid
    c.layer(rrect(36, 14, 20, 10, 4), kit.dk(col, .2), depth=2, shadow=False)             # the handle
    c.flat(rrect(28, 46, 36, 30, 6), PAPER)
    if kind == "trash":
        c.flat(poly([(38, 54), (54, 54), (52, 70), (40, 70)]), kit.dk(GREY, .35))
        c.flat(rrect(36, 52, 20, 3, 1), kit.dk(GREY, .35))
    elif kind == "paper":
        c.flat(rrect(38, 52, 16, 20, 2), BLUE)
        for y in (57, 62, 67):
            c.stroke(path([(41, y), (51, y)]), PAPER, 1.6)
    elif kind == "bottle":
        c.flat(rrect(43, 50, 6, 5, 1), kit.dk(YELLOW, .4))
        c.flat(rrect(40, 55, 12, 17, 4), kit.dk(YELLOW, .4))
    else:
        c.flat(leaf(46, 62, 20, 12, -45), LEAF_DK)
        c.stroke(path([(40, 68), (52, 56)]), PAPER, 1.5)


def p_garbage_truck(c):
    # 300 x 200: a yellow garbage truck, cab at the left with a face, the big box behind, music notes above
    c.layer(rrect(96, 44, 190, 112, 16), YELLOW, depth=6)                               # the box
    c.flat(rrect(96, 112, 190, 12, 4), kit.dk(YELLOW, .12))
    c.layer(rrect(270, 70, 20, 60, 8), kit.dk(YELLOW, .2), depth=3, shadow=False)        # the back door
    c.layer(rrect(10, 64, 92, 92, 18), YELLOW, depth=6)                                  # the cab
    c.layer(rrect(26, 72, 50, 30, 10), SKY, depth=3, shadow=False)                       # windscreen
    c.face(44, 124, 11, "happy")
    c.layer(circle(16, 140, 8), CREAM, depth=2, shadow=False)                             # headlight
    for x in (90, 244):                                                                   # wheels
        c.layer(circle(x, 160, 24), DARK, depth=4)
        c.flat(circle(x, 160, 11), GREY)
    c.layer(rrect(108, 60, 160, 44, 10), kit.lt(YELLOW, .3), depth=3, shadow=False)       # the sign panel
    c.flat(heart(188, 83, 24), PINK_DK)
    c.flat(leaf(150, 82, 22, 12, -30), LEAF_DK)
    c.flat(leaf(226, 82, 22, 12, 30), LEAF_DK)
    # the music
    for x, y, s in ((120, 30, 1.0), (170, 16, 1.2), (222, 28, 1.0)):
        c.flat(ellipse(x, y, 7 * s, 5 * s).rotate(-20, x, y), DARK)
        c.stroke(path([(x + 6 * s, y - 2), (x + 6 * s, y - 20 * s)]), DARK, 3)
        c.stroke(path([(x + 6 * s, y - 20 * s), (x + 14 * s, y - 15 * s)]), DARK, 3)


# ---------------------------------------------------------------- park and street
def p_traffic_light(c, green):
    c.layer(rrect(30, 20, 36, 10, 4), kit.dk(GREY, .55), depth=2, shadow=False)       # the hood
    c.layer(rrect(24, 6, 44, 82, 10), kit.dk(GREY, .5), depth=5)
    c.layer(rrect(44, 86, 4, 8, 1), kit.dk(GREY, .5), depth=0, shadow=False)
    red_on, green_on = not green, green
    c.flat(circle(46, 28, 15), RED if red_on else kit.mix(RED, kit.dk(GREY, .5), .75))
    c.flat(circle(46, 66, 15), GREEN if green_on else kit.mix(GREEN, kit.dk(GREY, .5), .75))
    if red_on:                                                                           # a standing figure
        c.flat(circle(46, 20, 3.5), PAPER)
        c.flat(rrect(42.5, 24, 7, 10, 2.5), PAPER)
        c.stroke(path([(44, 34), (44, 40)]), PAPER, 2)
        c.stroke(path([(48, 34), (48, 40)]), PAPER, 2)
        c.flat(ellipse(46, 28, 20, 7), kit.lt(RED, .5), op=.25)
    if green_on:                                                                         # a walking figure
        c.flat(circle(47, 58, 3.5), PAPER)
        c.flat(rrect(43.5, 62, 7, 9, 2.5), PAPER)
        c.stroke(path([(45, 70), (41, 78)]), PAPER, 2.2)
        c.stroke(path([(48, 70), (52, 77)]), PAPER, 2.2)
        c.stroke(path([(44, 64), (39, 69)]), PAPER, 2)
        c.stroke(path([(50, 64), (54, 68)]), PAPER, 2)
    c.flat(circle(40, 22, 2.5), WHITE, op=.5)


def p_slide(c):
    # 200 x 200: a ladder at the left up to a little platform, a slide coming down to the right
    c.layer(rrect(24, 70, 10, 118, 4), MINT_DK, depth=3)
    c.layer(rrect(54, 70, 10, 118, 4), MINT_DK, depth=3)
    for i in range(5):
        c.layer(rrect(22, 86 + i * 22, 44, 7, 3), MINT, depth=2, shadow=False)
    c.layer(rrect(18, 58, 70, 16, 6), MINT, depth=4)                                  # the platform
    slide = poly([(78, 58), (104, 58), (176, 164), (190, 180), (160, 184), (90, 100)])
    slide = smooth([(78, 56), (104, 56), (150, 128), (184, 170), (170, 186), (138, 170), (96, 112), (72, 72)], .25)
    c.layer(slide, CORAL, depth=6)
    c.flat(smooth([(88, 60), (98, 60), (142, 124), (170, 162), (164, 172), (136, 150), (90, 92), (82, 72)], .25),
           kit.lt(CORAL, .35))
    c.layer(rrect(150, 170, 44, 14, 6), kit.dk(CORAL, .2), depth=3)                   # the landing
    c.face(44, 66, 5, "smile")


def p_swing(c):
    # 200 x 200: an A-frame with two ropes and a seat
    for x0, x1 in ((18, 48), (182, 152)):
        c.layer(poly([(x0 - 6, 186), (x0 + 8, 186), (x1 + 6, 26), (x1 - 6, 26)]), WOOD_DK, depth=4)
    c.layer(rrect(36, 18, 128, 14, 7), WOOD, depth=4)                                  # the top bar
    for x in (74, 126):
        c.stroke(path([(x, 32), (x, 136)]), WOOD_DEEP, 4)
    c.layer(rrect(60, 134, 80, 18, 8), CORAL, depth=5)                                 # the seat
    c.face(100, 143, 5, "happy")


def p_sandbox(c):
    # 200 x 150: a wooden frame seen a bit from above, full of sand, with a bucket and a starfish
    frame = poly([(30, 30), (170, 30), (194, 124), (6, 124)])
    c.layer(frame, WOOD, depth=6)
    c.flat(poly([(44, 42), (156, 42), (176, 112), (24, 112)]), SAND)
    c.dots([(60, 60), (120, 54), (150, 96), (70, 100), (100, 80)], 2.5, kit.dk(SAND, .12))
    c.layer(poly([(120, 62), (148, 62), (144, 92), (124, 92)]), SKY, depth=4)          # bucket
    c.stroke(arc(134, 62, 13, 180, 360), BLUE_DK, 3)
    c.layer(star(72, 80, 16), CORAL, depth=3)
    c.face(72, 80, 3.5, "smile")


def p_shovel(c):
    c.layer(rrect(56, 2, 12, 48, 6).rotate(30, 62, 26), SKY, depth=3)
    c.layer(rrect(66, 0, 20, 10, 5).rotate(30, 76, 5), SKY, depth=2, shadow=False)    # the grip
    scoop = smooth([(16, 46), (52, 40), (62, 56), (56, 86), (24, 88), (10, 70)], .35)
    c.layer(scoop, CORAL, depth=5)
    c.flat(smooth([(24, 50), (50, 46), (56, 58), (50, 80), (28, 80), (18, 66)], .35), kit.dk(CORAL, .18))


def p_ball(c):
    c.layer(circle(46, 48, 36), PAPER, depth=5)
    for i, col in enumerate((PINK, SKY, YELLOW, MINT)):
        a0 = -90 + i * 90
        a1 = a0 + 45
        pts = [(46, 48)]
        for k in range(6):
            a = math.radians(a0 + (a1 - a0) * k / 5)
            pts.append((46 + 36 * math.cos(a), 48 + 36 * math.sin(a)))
        c.flat(poly(pts), col)
    c.flat(circle(46, 48, 6), WHITE)
    c.flat(ellipse(32, 30, 7, 4).rotate(-40, 32, 30), WHITE, op=.6)


def p_shell(c):
    sh = smooth([(46, 86), (14, 56), (18, 32), (46, 18), (74, 32), (78, 56)], .5)
    c.layer(sh, PEACH, depth=5)
    for a in (-60, -35, -10, 10, 35, 60):
        x1 = 46 + 50 * math.sin(math.radians(a))
        y1 = 82 - 54 * math.cos(math.radians(a))
        c.stroke(path([(46, 80), (x1, y1)]), PEACH_DK, 2.5)
    c.layer(rrect(38, 80, 16, 10, 4), PEACH_DK, depth=2, shadow=False)
    c.face(46, 48, 5, "smile")


# ---------------------------------------------------------------- market
def p_cart(c):
    # 200 x 200: a shopping cart, side view, a few things inside
    c.stroke(path([(20, 40), (36, 40), (62, 140)]), METAL, 7)                           # the handle bar
    c.layer(circle(20, 40, 8), RED, depth=2)
    basket = poly([(40, 60), (176, 60), (164, 140), (56, 140)])
    c.layer(basket, kit.lt(METAL, .4), depth=5)
    for i in range(4):
        y = 72 + i * 18
        c.stroke(path([(44 + i * 1.5, y), (172 - i * 1.5, y)]), METAL, 2.5)
    for x in (72, 104, 136):
        c.stroke(path([(x, 62), (x - 2, 138)]), METAL, 2.5)
    c.layer(rrect(36, 54, 144, 12, 6), METAL, depth=3)                                  # the rim
    c.layer(circle(80, 38, 16), RED, depth=3)                                           # an apple
    c.stroke(path([(80, 24), (82, 16)]), LEAF_DK, 3)
    c.layer(rrect(104, 22, 26, 36, 6), PAPER, depth=3)                                  # a milk carton
    c.flat(rrect(108, 36, 18, 10, 2), SKY)
    c.layer(rrect(136, 34, 30, 24, 5), YELLOW, depth=3)                                 # a box
    for x in (76, 150):                                                                 # wheels
        c.stroke(path([(x, 140), (x, 168)]), METAL, 5)
        c.layer(circle(x, 174, 12), DARK, depth=3)
        c.flat(circle(x, 174, 5), GREY)
    c.face(110, 110, 7, "happy")


def p_shelf(c):
    # 300 x 200: a market shelf with two rows of things
    c.layer(rrect(8, 10, 280, 176, 12), WOOD, depth=6)
    for y in (84, 160):
        c.layer(rrect(14, y, 268, 14, 5), WOOD_DK, depth=4, shadow=False)
    c.flat(rect(14, 18, 268, 66), kit.dk(WOOD, .12))
    c.flat(rect(14, 98, 268, 62), kit.dk(WOOD, .12))
    # top row: apples, bananas, a carrot bunch
    for x in (40, 68, 96):
        c.layer(circle(x, 66, 16), RED, depth=3)
        c.stroke(path([(x, 52), (x + 2, 44)]), LEAF_DK, 3)
    ban = smooth([(130, 50), (150, 38), (176, 42), (190, 58), (180, 72), (154, 72), (134, 64)], .4)
    c.layer(ban, YELLOW, depth=3)
    for x in (222, 250):
        c.layer(poly([(x - 10, 40), (x + 10, 40), (x, 82)]), PEACH_DK, depth=3)
        c.layer(leaf(x, 34, 10, 20, -90), LEAF, depth=2, shadow=False)
    # bottom row: milk cartons, boxes, a jar
    for i in range(3):
        x = 30 + i * 32
        c.layer(poly([(x, 112), (x + 24, 112), (x + 24, 158), (x, 158)]), PAPER, depth=3)
        c.flat(rrect(x + 4, 130, 16, 10, 2), SKY)
        c.flat(poly([(x, 112), (x + 12, 102), (x + 24, 112)]), kit.dk(PAPER, .1))
    for i, col in enumerate((PINK, LAVENDER, MINT)):
        x = 136 + i * 40
        c.layer(rrect(x, 116, 32, 42, 5), col, depth=3)
        c.flat(star(x + 16, 136, 9), PAPER)
    c.layer(rrect(262, 120, 18, 38, 6), kit.lt(CORAL, .2), depth=3)
    c.flat(rrect(264, 114, 14, 8, 3), WOOD_DK)


def p_cashier(c):
    # 200 x 260: a puppet in an apron behind a counter with a till
    puppet(c, cx=118, shirt=SKY, apron=PEACH, style="bob", mood="happy", legs=False)
    c.layer(rrect(4, 178, 186, 70, 10), WOOD, depth=5)                                  # the counter
    c.flat(rrect(4, 178, 186, 12, 5), kit.lt(WOOD, .3))
    c.layer(rrect(14, 136, 56, 44, 8), kit.dk(GREY, .3), depth=4)                       # the till
    c.flat(rrect(20, 142, 44, 16, 4), MINT)
    c.dots([(26 + i * 10, 168) for i in range(4)], 2.6, PAPER)
    c.dots([(26 + i * 10, 176) for i in range(4)], 2.6, PAPER)
    c.layer(rrect(60, 112, 10, 28, 4).rotate(-20, 65, 138), kit.dk(GREY, .3), depth=2, shadow=False)   # the display arm
    c.face(96, 214, 7, "smile")


def p_list(c):
    # 200 x 200: a shopping list card with a clip and three empty picture squares
    c.layer(rrect(24, 18, 152, 170, 14), PAPER, depth=6)
    c.layer(rrect(76, 6, 48, 24, 8), METAL, depth=3)                                   # the clip
    c.flat(rrect(86, 12, 28, 10, 5), kit.dk(METAL, .3))
    c.stroke(path([(44, 50), (156, 50)]), PINK_DK, 3)
    c.flat(heart(100, 42, 14), PINK_DK)
    for i in range(3):
        y = 62 + i * 40
        c.flat(rrect(44, y, 34, 32, 6), CREAM)
        c.stroke(rrect(44, y, 34, 32, 6), kit.dk(CREAM, .3), 2)
        c.flat(circle(94, y + 16, 3), GREY)
        c.flat(rrect(104, y + 10, 52, 12, 6), kit.lt(GREY, .4))


def p_bag_shop(c):
    c.stroke(arc(46, 26, 16, 180, 360), WOOD_DK, 3.5)                                   # the handle
    c.layer(rrect(14, 26, 64, 62, 6), kit.lt(WOOD, .25), depth=5)
    c.flat(rrect(14, 26, 64, 8, 3, rbl=0, rbr=0), kit.dk(WOOD, .1))
    c.flat(heart(46, 58, 24), CORAL)
    c.flat(ellipse(44, 52, 4, 2.5).rotate(-30, 44, 52), WHITE, op=.5)


# ---------------------------------------------------------------- clinic
def p_thermometer(c):
    body = rrect(20, 40, 66, 18, 9)
    tip = rrect(4, 43, 22, 12, 6)
    c.layer(tip.rotate(-30, 46, 49), METAL, depth=3)
    c.layer(body.rotate(-30, 46, 49), PAPER, depth=5)
    c.layer(rrect(50, 44, 22, 10, 3).rotate(-30, 46, 49), MINT, depth=0, shadow=False)   # the display
    c.flat(circle(78, 36, 3), CORAL)
    for i in range(3):
        x, y = 56 + i * 6, 47 - i * 3.5
        c.flat(rrect(x, y, 2.6, 5, 1).rotate(-30, x, y), DARK)


def p_stethoscope(c):
    # a Y: two ear tubes meet in the middle, one tube goes on to the round chest piece
    tube = kit.dk(GREY, .5)
    c.shadow(path([(26, 12), (26, 34), (42, 52), (50, 34), (50, 12)]), dx=4, dy=5)
    for sx in (-1, 1):
        c.stroke(path([(38 + sx * 12, 12), (38 + sx * 12, 32), (38 + sx * 4, 50), (38, 56)]), tube, 4.5)
    c.stroke(path([(38, 56), (40, 68), (52, 78), (64, 80)]), tube, 4.5)
    for sx in (-1, 1):
        c.layer(circle(38 + sx * 12, 12, 5), METAL, depth=2, shadow=False)              # the ear tips
    c.layer(circle(72, 78, 13), METAL, depth=4)                                          # the chest piece
    c.flat(circle(72, 78, 7), kit.lt(SKY, .3))
    c.face(72, 78, 2.6, "smile")


def p_syringe(c):
    # round and friendly: a chubby barrel, a short blunt tip, a smile
    c.layer(rrect(32, 2, 28, 8, 4), METAL, depth=2)                                     # the thumb rest
    c.layer(rrect(42, 8, 8, 16, 3), METAL, depth=2, shadow=False)                       # the rod
    c.layer(rrect(24, 22, 44, 8, 4), METAL, depth=3)                                    # the finger flange
    c.layer(rrect(30, 28, 32, 46, 9), PAPER, depth=5)                                   # the barrel
    c.flat(rrect(33, 48, 26, 24, 7), SKY)                                               # the medicine
    for y in (36, 42, 48, 54, 60):
        c.stroke(path([(34, y), (40 if y % 12 else 44, y)]), GREY, 1.8)
    c.layer(poly([(36, 74), (56, 74), (50, 82), (42, 82)]), METAL, depth=2, shadow=False)
    c.layer(circle(46, 86, 4), METAL, depth=2)                                           # a round, blunt tip
    c.flat(drop_shape(60, 86, 3), SKY)                                                   # a tiny drop
    c.face(46, 58, 4.5, "happy")


def p_medicine(c):
    c.layer(rrect(24, 8, 24, 12, 4), PINK_DK, depth=3)                                 # the cap
    c.layer(rrect(18, 18, 36, 70, 10), PINK, depth=5)
    c.flat(rrect(24, 38, 24, 30, 5), PAPER)
    c.flat(heart(36, 53, 14), CORAL)
    # a spoon leaning beside it
    sp = ellipse(72, 72, 12, 9) + rrect(68, 30, 8, 42, 4)
    c.layer(sp, METAL, depth=3)
    c.flat(ellipse(72, 72, 8, 5.5), PINK)


def p_doctor(c):
    puppet(c, shirt=SKY, bottom=kit.dk(GREY, .3), coat=PAPER, style="short", mood="happy", skin=SKIN_2)
    # the stethoscope round the neck
    c.stroke(path([(78, 108), (74, 150)]), kit.dk(GREY, .5), 4)
    c.stroke(path([(114, 108), (118, 150)]), kit.dk(GREY, .5), 4)
    c.stroke(path([(74, 150), (76, 160)]), kit.dk(GREY, .5), 4)
    c.layer(circle(76, 166, 9), METAL, depth=3)
    c.flat(circle(76, 166, 4), kit.lt(SKY, .3))
    c.flat(heart(122, 160, 10), CORAL)                                                  # a pocket badge


def p_sticker_brave(c):
    sh = circle(46, 46, 34)
    for i in range(12):
        a = 2 * math.pi * i / 12
        sh = sh + circle(46 + 34 * math.cos(a), 46 + 34 * math.sin(a), 6)
    c.layer(sh, YELLOW, depth=5)
    c.flat(circle(46, 46, 28), kit.lt(YELLOW, .5))
    c.flat(star(46, 44, 24), CORAL)
    c.flat(heart(46, 48, 14), PAPER)
    c.flat(heart(46, 48, 9), PINK_DK)


# ---------------------------------------------------------------- happenings
def p_drop(c):
    c.layer(drop_shape(46, 56, 28), SKY, depth=5)
    c.flat(ellipse(36, 44, 5, 9).rotate(20, 36, 44), WHITE, op=.6)
    c.face(46, 58, 7, "open")


def p_tummy(c):
    c.layer(ellipse(46, 50, 36, 32), PEACH, depth=5)
    c.flat(ellipse(46, 50, 30, 26), kit.lt(PEACH, .15))
    c.flat(ellipse(46, 66, 4, 5), kit.dk(PEACH, .3))                                    # the belly button
    c.stroke(spiral(46, 44, 2, 18, 2.2), kit.dk(PEACH, .45), 3)
    for x, y in ((80, 20), (86, 30)):
        c.flat(circle(x, y, 3.5), kit.dk(PEACH, .3))
    c.layer(rrect(10, 20, 72, 14, 6), SKY, depth=0, shadow=False)                        # the shirt hem above
    c.stroke(zigzag(12, 34, 80, 2, 8), kit.dk(SKY, .2), 1.5)


def p_yawn(c):
    def z(x, y, s):
        w = s
        return poly([(x, y), (x + w, y), (x + w, y + s * .22), (x + w * .38, y + s * .78), (x + w, y + s * .78),
                     (x + w, y + s), (x, y + s), (x, y + s * .78), (x + w * .62, y + s * .22), (x, y + s * .22)])
    c.layer(z(14, 30, 54), LAVENDER_DK, depth=5)
    c.layer(z(62, 12, 24), LAVENDER, depth=3)
    c.layer(z(74, 2, 12), LAVENDER, depth=2, shadow=False)
    c.flat(ellipse(32, 36, 6, 3).rotate(-30, 32, 36), WHITE, op=.5)


def p_sweat(c):
    for x, y, r in ((26, 40, 12), (60, 30, 9), (56, 70, 10)):
        c.layer(drop_shape(x, y, r), SKY, depth=4)
        c.flat(ellipse(x - r * .35, y - r * .4, r * .18, r * .32).rotate(20, x - r * .35, y - r * .4), WHITE, op=.6)


def p_shiver(c):
    cx, cy = 46, 46
    for i in range(6):
        a = math.radians(i * 60)
        x1, y1 = cx + 32 * math.cos(a), cy + 32 * math.sin(a)
        c.stroke(path([(cx, cy), (x1, y1)]), BLUE, 4)
        for t in (.55, .8):
            px, py = cx + 32 * t * math.cos(a), cy + 32 * t * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(50)
                c.stroke(path([(px, py), (px + 8 * math.cos(b), py + 8 * math.sin(b))]), BLUE, 3)
    c.layer(circle(cx, cy, 6), kit.lt(SKY, .4), depth=0, shadow=False)
    for x in (6, 86):                                                                    # the wobble lines
        c.stroke(zigzag(x - 4, 30, x + 4, 0, 1).rotate(90, x, 30), BLUE_DK, 2)
        c.stroke(path([(x - 3, 20), (x + 3, 26), (x - 3, 32), (x + 3, 38)]), BLUE_DK, 2)
        c.stroke(path([(x - 3, 52), (x + 3, 58), (x - 3, 64), (x + 3, 70)]), BLUE_DK, 2)


def p_tissue(c):
    c.layer(smooth([(28, 34), (34, 14), (44, 2), (52, 18), (62, 4), (70, 20), (66, 36)], .4), PAPER, depth=3)   # the tissue out
    c.layer(rrect(10, 30, 76, 56, 10), PINK, depth=5)
    c.flat(rrect(30, 28, 36, 10, 5), kit.dk(PINK, .3))                                  # the slot
    c.dots([(22, 50), (74, 50), (22, 74), (74, 74)], 4, PAPER)
    c.flat(heart(48, 64, 18), PAPER)


def p_bandage(c):
    strip = rrect(8, 36, 76, 24, 12).rotate(-30, 46, 48)
    c.layer(strip, PEACH, depth=5)
    c.flat(rrect(34, 38, 24, 20, 5).rotate(-30, 46, 48), kit.lt(PEACH, .4))            # the pad
    pts = []
    for i in range(3):
        for j in range(2):
            x, y = 18 + i * 6, 42 + j * 10
            pts.append((x, y))
            pts.append((92 - x, y))
    rot = kit.Shape()
    for x, y in pts:
        rot = rot + circle(x, y, 1.6)
    c.flat(rot.rotate(-30, 46, 48), kit.dk(PEACH, .25))


def p_mosquito(c):
    c.stroke(path([(36, 60), (24, 78)]), DARK, 2)                                       # legs
    c.stroke(path([(44, 62), (40, 82)]), DARK, 2)
    c.stroke(path([(52, 62), (60, 80)]), DARK, 2)
    c.layer(ellipse(32, 44, 8, 22).rotate(30, 32, 44), WHITE, depth=0, shadow=False, op=.75)   # wings
    c.layer(ellipse(58, 40, 8, 22).rotate(-20, 58, 40), WHITE, depth=0, shadow=False, op=.75)
    c.layer(ellipse(42, 60, 18, 10).rotate(20, 42, 60), kit.dk(GREY, .4), depth=4)       # body
    for i in range(3):
        c.flat(rrect(32 + i * 8, 56 + i * 2.5, 3, 8, 1.5).rotate(20, 33 + i * 8, 60), kit.lt(GREY, .2))
    c.layer(circle(64, 48, 11), kit.dk(GREY, .4), depth=4)                               # head
    c.stroke(path([(72, 54), (86, 68)]), DARK, 2.5)                                     # the nose
    c.face(66, 48, 3.2, "smile", blush=PINK_DK)
    c.stroke(path([(58, 40), (52, 30)]), DARK, 1.5)                                      # antennae
    c.stroke(path([(66, 38), (68, 28)]), DARK, 1.5)


def p_flashlight(c):
    c.flat(poly([(50, 42), (92, 8), (92, 66)]), kit.lt(YELLOW, .5), op=.7)               # the light cone
    c.flat(poly([(50, 42), (92, 22), (92, 52)]), kit.lt(YELLOW, .3), op=.6)
    body = rrect(8, 36, 44, 20, 8)
    head = rrect(44, 30, 14, 32, 5)
    c.layer(body.rotate(-20, 30, 46), kit.dk(GREY, .35), depth=4)
    c.layer(head.rotate(-20, 30, 46), kit.dk(GREY, .5), depth=4)
    c.layer(rrect(20, 34, 12, 6, 3).rotate(-20, 30, 46), CORAL, depth=0, shadow=False)   # the switch
    c.flat(circle(58, 36, 5), YELLOW)


def p_doorbell(c):
    c.layer(rrect(14, 14, 44, 68, 10), CREAM, depth=5)
    c.layer(circle(36, 48, 13), CORAL, depth=3)
    c.flat(circle(32, 44, 3.5), WHITE, op=.6)
    c.dots([(36, 24), (36, 72)], 2.2, GREY)
    sound_lines(c, 48, 48, 22, 1, CORAL, 3, 3)


def p_phone_ring(c):
    W, H = 70, 52
    ox, oy = 12, 32                                                                      # the phone sits here
    c.layer(poly([(8, H), (W - 8, H), (W, 26), (0, 26)]).move(ox, oy), RED, depth=4)
    c.flat(circle(W / 2 + ox, 40 + oy, 9), CREAM)
    c.dots([(W / 2 + ox + 5.5 * math.cos(a), 40 + oy + 5.5 * math.sin(a)) for a in [i * math.pi / 3 for i in range(6)]], 1.6, RED)
    c.layer(rrect(4, 16, 12, 14, 5).move(ox, oy), kit.dk(RED, .15), depth=2, shadow=False)
    c.layer(rrect(W - 16, 16, 12, 14, 5).move(ox, oy), kit.dk(RED, .15), depth=2, shadow=False)
    hs = rrect(2, 4, W - 4, 14, 7) + circle(10, 11, 10) + circle(W - 10, 11, 10)
    c.layer(hs.move(ox, oy - 6), kit.dk(RED, .06), depth=4)
    sound_lines(c, 18, 36, 12, -1, RED, 3, 2)
    sound_lines(c, 76, 36, 12, 1, RED, 3, 2)


def p_grandma(c):
    puppet(c, shirt=LAVENDER, bottom=PINK_DK, hair=HAIR_GREY, style="bun", dress=True, mood="happy", glasses=True,
           skin=SKIN_2)
    c.flat(heart(96, 150, 12), PINK_DK)


def p_package(c):
    c.layer(rrect(12, 30, 70, 58, 6), kit.lt(WOOD, .2), depth=5)
    c.layer(poly([(12, 30), (6, 16), (44, 16), (46, 30)]), kit.lt(WOOD, .1), depth=3, shadow=False)
    c.layer(poly([(46, 30), (48, 16), (86, 16), (82, 30)]), kit.lt(WOOD, .05), depth=3, shadow=False)
    c.flat(rrect(42, 16, 8, 72, 2), kit.lt(WOOD, .45))                                 # the tape
    c.flat(heart(30, 62, 16), CORAL)
    c.flat(rrect(58, 54, 18, 12, 2), PAPER)                                             # the address label
    c.stroke(path([(61, 58), (72, 58)]), GREY, 1.5)
    c.stroke(path([(61, 62), (69, 62)]), GREY, 1.5)


def p_table_hide(c):
    # 300 x 200: a table from the side, a dark hiding space under it, a cushion on the floor underneath
    c.flat(rrect(40, 70, 220, 110, 8), kit.SHADOW, op=.1)                                # the shade under the table
    c.layer(rrect(10, 34, 280, 26, 10), WOOD, depth=6)                                   # the top
    c.flat(rrect(10, 34, 280, 8, 4, rbl=0, rbr=0), kit.lt(WOOD, .3))
    for x in (30, 246):
        c.layer(rrect(x, 58, 24, 128, 8), WOOD_DK, depth=4)
    c.layer(rrect(98, 138, 104, 46, 18), PINK, depth=5)                                  # the cushion
    c.dots([(124, 161), (150, 161), (176, 161)], 4, PAPER)
    c.face(150, 158, 6, "smile")
    c.face(150, 50, 5, "smile")


def p_breath(c, step):
    r = (20, 29, 38)[step - 1]
    c.layer(circle(44, 48, r), SKY, depth=4, op=.9)
    c.flat(circle(44, 48, r * .8), kit.lt(SKY, .35))
    c.flat(ellipse(44 - r * .4, 48 - r * .45, r * .16, r * .28).rotate(30, 44 - r * .4, 48 - r * .45), WHITE, op=.7)
    c.face(44, 50, r * .3, "sleepy")
    if step > 1:
        for a in (-110, -70):
            x0, y0 = 44 + (r + 6) * math.cos(math.radians(a)), 48 + (r + 6) * math.sin(math.radians(a))
            c.stroke(path([(x0, y0), (x0 + 6 * math.cos(math.radians(a)), y0 + 6 * math.sin(math.radians(a)))]), BLUE, 2.5)


def p_mailman(c):
    puppet(c, shirt=GREEN, bottom=kit.dk(GREEN, .3), style="short", mood="happy", cap=GREEN, skin=SKIN_2)
    # the mail bag across the body with an envelope
    c.stroke(path([(70, 110), (138, 168)]), kit.dk(WOOD, .2), 7)
    c.layer(rrect(118, 150, 56, 46, 8), WOOD, depth=4)
    c.flat(rrect(118, 150, 56, 12, 5, rbl=0, rbr=0), WOOD_DK)
    c.layer(rrect(128, 138, 36, 24, 3), PAPER, depth=2)
    c.stroke(path([(130, 140), (146, 152), (162, 140)]), GREY, 2)
    c.flat(circle(96, 36, 6), PAPER)                                                     # the cap badge


# ---------------------------------------------------------------- the list
PROPS = [
    # school
    ("bag_open", 100, 100, p_bag_open),
    ("item_bottle", 100, 100, p_item_bottle),
    ("item_hanky", 100, 100, p_item_hanky),
    ("item_book", 100, 100, p_item_book),
    ("bus", 300, 200, p_bus),
    ("seatbelt", 100, 100, p_seatbelt),
    ("cubby_1", 100, 100, lambda c: p_cubby(c, "star")),
    ("cubby_2", 100, 100, lambda c: p_cubby(c, "heart")),
    ("cubby_3", 100, 100, lambda c: p_cubby(c, "flower")),
    ("teacher", 200, 260, p_teacher),
    ("classmate_1", 200, 260, p_classmate_1),
    ("classmate_2", 200, 260, p_classmate_2),
    ("mat", 200, 100, p_mat),
    ("hands_clap", 100, 100, p_hands_clap),
    ("footprint", 100, 100, p_footprint),
    # toys and chores
    ("toy_car", 100, 100, p_toy_car),
    ("toy_block", 100, 100, p_toy_block),
    ("toy_doll", 100, 100, p_toy_doll),
    ("toy_ball", 100, 100, p_toy_ball),
    ("box_car", 100, 100, lambda c: p_box(c, "car")),
    ("box_block", 100, 100, lambda c: p_box(c, "block")),
    ("box_doll", 100, 100, lambda c: p_box(c, "doll")),
    ("broom", 100, 100, p_broom),
    ("dustpan", 100, 100, p_dustpan),
    ("shoe_rack", 200, 120, p_shoe_rack),
    ("sock_1_a", 100, 100, lambda c: p_sock(c, "stripes")),
    ("sock_1_b", 100, 100, lambda c: p_sock(c, "stripes")),
    ("sock_2_a", 100, 100, lambda c: p_sock(c, "dots")),
    ("sock_2_b", 100, 100, lambda c: p_sock(c, "dots")),
    ("sock_3_a", 100, 100, lambda c: p_sock(c, "stars")),
    ("sock_3_b", 100, 100, lambda c: p_sock(c, "stars")),
    ("shirt_hanging", 100, 100, p_shirt_hanging),
    ("peg", 100, 100, p_peg),
    ("basket", 100, 100, p_basket),
    ("watering_can", 100, 100, p_watering_can),
    ("plant", 100, 100, lambda c: p_plant(c, False)),
    ("plant_wilt", 100, 100, lambda c: p_plant(c, True)),
    ("kibble_bag", 100, 100, p_kibble_bag),
    ("buddy_bowl", 100, 100, p_buddy_bowl),
    ("trash_bag", 100, 100, p_trash_bag),
    ("recycle_paper", 100, 100, p_recycle_paper),
    ("recycle_bottle", 100, 100, p_recycle_bottle),
    ("recycle_food", 100, 100, p_recycle_food),
    ("bin_trash", 100, 100, lambda c: p_bin(c, GREY, "trash")),
    ("bin_paper", 100, 100, lambda c: p_bin(c, BLUE, "paper")),
    ("bin_bottle", 100, 100, lambda c: p_bin(c, YELLOW, "bottle")),
    ("bin_food", 100, 100, lambda c: p_bin(c, LEAF, "food")),
    ("garbage_truck", 300, 200, p_garbage_truck),
    # park and street
    ("traffic_light_red", 100, 100, lambda c: p_traffic_light(c, False)),
    ("traffic_light_green", 100, 100, lambda c: p_traffic_light(c, True)),
    ("slide", 200, 200, p_slide),
    ("swing", 200, 200, p_swing),
    ("sandbox", 200, 150, p_sandbox),
    ("shovel", 100, 100, p_shovel),
    ("ball", 100, 100, p_ball),
    ("shell", 100, 100, p_shell),
    # market
    ("cart", 200, 200, p_cart),
    ("shelf", 300, 200, p_shelf),
    ("cashier", 200, 260, p_cashier),
    ("list", 200, 200, p_list),
    ("bag_shop", 100, 100, p_bag_shop),
    # clinic
    ("thermometer", 100, 100, p_thermometer),
    ("stethoscope", 100, 100, p_stethoscope),
    ("syringe", 100, 100, p_syringe),
    ("medicine", 100, 100, p_medicine),
    ("doctor", 200, 260, p_doctor),
    ("sticker_brave", 100, 100, p_sticker_brave),
    # happenings
    ("drop", 100, 100, p_drop),
    ("tummy", 100, 100, p_tummy),
    ("yawn", 100, 100, p_yawn),
    ("sweat", 100, 100, p_sweat),
    ("shiver", 100, 100, p_shiver),
    ("tissue", 100, 100, p_tissue),
    ("bandage", 100, 100, p_bandage),
    ("mosquito", 100, 100, p_mosquito),
    ("flashlight", 100, 100, p_flashlight),
    ("doorbell", 100, 100, p_doorbell),
    ("phone_ring", 100, 100, p_phone_ring),
    ("grandma", 200, 260, p_grandma),
    ("package", 100, 100, p_package),
    ("table_hide", 300, 200, p_table_hide),
    ("breath_1", 100, 100, lambda c: p_breath(c, 1)),
    ("breath_2", 100, 100, lambda c: p_breath(c, 2)),
    ("breath_3", 100, 100, lambda c: p_breath(c, 3)),
    ("mailman", 200, 260, p_mailman),
]


def build():
    """Write every prop in PROPS to app/assets/art/props/<id>.svg."""
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, w, h, fn in PROPS:
        c = ctx(w, h)
        fn(c)
        total += kit.write_svg(OUT / f"{name}.svg", c.svg(), (w, h))
    print(f"props_out: {len(PROPS)} files, {total:.0f} KB")
    return [p[0] for p in PROPS]


if __name__ == "__main__":
    build()
