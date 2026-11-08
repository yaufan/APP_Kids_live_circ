"""The clock (docs/art.md clock/): face.svg 300 x 300 (a wooden clock with a cream dial, 12 tick dots,
a small face at the bottom of the dial, no numerals), hand.svg 60 x 300 (one chunky coral hand
pointing up, pivot at (30, 150)), thirteen 100 x 100 time-of-day pictures t_<name> and five weather
pictures w_<name>, each with a small face.

The 100 x 100 pictures are drawn at scale .7 (they show at about half size on the dial), so their
paper thickness and shadows stay in proportion.
"""
import math

import kit
from kit import (CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PINK, PINK_DK,
                 WHITE, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, arc, circle, cloud, ellipse, path, poly, rrect, star)

OUT = kit.ART / "clock"
ORANGE = "#F7B84A"
BLUE = "#8CCBEB"
BLUE_DK = kit.dk(BLUE, .25)
SKIN = "#F2C9A6"
STORM = "#9A93B0"


def icon():
    return kit.Ctx(100, 100, scale=.7)


def drop(x, y, r):
    """A water drop with its point up, the round part centred at (x, y)."""
    return circle(x, y, r) + poly([(x, y - r * 2.1), (x - r * .92, y - r * .4), (x + r * .92, y - r * .4)])


def crescent(cx, cy, R, dx, dy, r):
    """The moon: circle (cx, cy, R) with the circle (cx+dx, cy+dy, r) taken out of it."""
    d = math.hypot(dx, dy)
    a = (d * d + R * R - r * r) / (2 * d)
    h = math.sqrt(max(R * R - a * a, 0))
    mx, my = cx + a * dx / d, cy + a * dy / d
    p1 = (mx + h * -dy / d, my + h * dx / d)
    p2 = (mx - h * -dy / d, my - h * dx / d)
    a1 = math.degrees(math.atan2(p1[1] - cy, p1[0] - cx))
    a2 = math.degrees(math.atan2(p2[1] - cy, p2[0] - cx))
    # the outer arc goes the long way round (away from the cut-out circle), clockwise
    if a2 < a1:
        a2 += 360
    outer = arc(cx, cy, R, a1, a2, 8)
    b1 = math.degrees(math.atan2(p2[1] - cy - dy, p2[0] - cx - dx))
    b2 = math.degrees(math.atan2(p1[1] - cy - dy, p1[0] - cx - dx))
    if b2 > b1:
        b2 -= 360
    inner = arc(cx + dx, cy + dy, r, b1, b2, 6)
    cmds = outer.cmds + [c for c in inner.cmds if c[0] != "M"] + [("Z",)]
    s = kit.Shape(cmds)
    xs = [c[1] for c in s.cmds if c[0] != "Z"]
    return s


def sun(c, cx, cy, r, col, ray_col, mood, rays=8, ray_len=13):
    for i in range(rays):
        a = 360 * i / rays
        ray = rrect(-3.5, -r - ray_len - 2, 7, ray_len + 2, 3.5).rotate(a, 0, 0).move(cx, cy)
        c.layer(ray, ray_col, depth=2, shadow=False)
    c.layer(circle(cx, cy, r), col, depth=4)
    c.face(cx, cy + 1, 8, mood)


# ---------------------------------------------------------------- the clock face and the hand
def face_svg():
    c = kit.Ctx(300, 300)
    cx = cy = 150
    c.layer(circle(cx, cy, 138), WOOD, depth=6)                                # the wooden body
    for r_, a0, a1 in ((128, 200, 290), (131, 20, 95), (124, 120, 150), (133, 310, 350)):   # grain
        c.stroke(arc(cx, cy, r_, a0, a1), kit.dk(WOOD, .12), 2.2, op=.8)
    c.flat(kit.ring(cx, cy, 121, 115), PINK, rule="evenodd")                    # a pink rim
    c.layer(circle(cx, cy, 114), CREAM, depth=3)                               # the paper dial
    g = kit.dk(CREAM, .07)
    for i, (yy, x0, x1) in enumerate(((70, 95, 205), (105, 55, 245), (195, 55, 245), (230, 95, 205))):
        c.stroke(path([(x0, yy), ((x0 + x1) / 2, yy + (3 if i % 2 else -3)), (x1, yy)]), g, 2)
    for i in range(12):                                                        # tick dots
        a = math.radians(-90 + 30 * i)
        rr = 5.5 if i % 3 == 0 else 4
        c.layer(circle(cx + 100 * math.cos(a), cy + 100 * math.sin(a), rr), WOOD_DK, depth=2, shadow=False)
    # the small face at the bottom of the dial
    for x in (136, 164):
        c.stroke(arc(x, 206, 7, 200, 340), DARK, 3.6)
    for x in (118, 182):
        c.flat(ellipse(x, 212, 9, 5.5), kit.BLUSH, op=.85)
    c.stroke(arc(150, 208, 7, 30, 150), DARK, 3)
    c.flat(circle(cx, cy, 6), kit.dk(CREAM, .25))                              # under the pivot
    kit.write_svg(OUT / "face.svg", c.svg(), (300, 300))


def hand_svg():
    c = kit.Ctx(60, 300)
    px, py = 30, 150
    blade = rrect(px - 9, 44, 18, py - 44 + 9, 9)                              # up from the pivot
    weight = rrect(px - 4, py, 8, 26, 4) + circle(px, py + 30, 9)              # the little counterweight
    c.layer(blade + weight, CORAL, depth=4)
    c.flat(rrect(px - 3, 54, 6, 70, 3), kit.lt(CORAL, .35), op=.9)             # a light stripe
    c.layer(circle(px, py, 12), kit.dk(CORAL, .18), depth=3, shadow=False)     # the pivot cap
    c.flat(circle(px, py, 5), CREAM)
    kit.write_svg(OUT / "hand.svg", c.svg(), (60, 300))


# ---------------------------------------------------------------- the thirteen time pictures
def t_wake(c):
    sun(c, 48, 50, 25, YELLOW, ORANGE, "happy")


def t_teeth(c):
    cx, cy, deg = 50, 54, 32
    def put(s):
        return s.rotate(deg, cx, cy)
    c.layer(put(rrect(cx - 7, cy - 24, 14, 62, 7)), BLUE, depth=3)             # the handle
    c.layer(put(rrect(cx - 9, cy - 46, 18, 24, 5)), PAPER, depth=3)            # the head
    for i in range(3):                                                         # bristle lines
        yy = cy - 42 + i * 7
        c.stroke(put(path([(cx - 5, yy), (cx + 5, yy)])), GREY, 1.6)
    paste = ellipse(cx, cy - 50, 11, 5) + circle(cx + 6, cy - 53, 4)
    c.layer(put(paste), MINT, depth=2, shadow=False)                          # toothpaste
    c.face(cx + 7, cy + 14, 4.5, "smile")


def t_dress(c):
    shirt = poly([(16, 30), (36, 16), (44, 24), (50, 27), (56, 24), (64, 16), (84, 30), (74, 46), (67, 42),
                  (67, 82), (33, 82), (33, 42), (26, 46)])
    c.layer(shirt, CORAL, depth=4)
    c.flat(poly([(36, 16), (44, 24), (50, 27), (56, 24), (64, 16), (58, 15), (50, 20), (42, 15)]), kit.dk(CORAL, .15))
    c.face(50, 56, 7, "happy")


def t_meal(c):
    c.stroke(path([(76, 16), (58, 50)]), WOOD_DK, 3.2)                        # chopsticks
    c.stroke(path([(84, 20), (64, 52)]), WOOD_DK, 3.2)
    rice = ellipse(48, 46, 30, 11) + circle(36, 40, 9) + circle(50, 37, 10) + circle(62, 41, 8)
    c.layer(rice, PAPER, depth=3)
    bowl = rrect(16, 46, 64, 30, 6, 6, 6, 24, 24) + rrect(34, 74, 28, 8, 4)
    c.layer(bowl, CORAL, depth=4)
    c.flat(rrect(16, 46, 64, 6, 3), kit.dk(CORAL, .14))
    c.face(48, 62, 7, "happy")


def t_school(c):
    c.layer(rrect(30, 12, 10, 18, 5), LEAF_DK, depth=2, shadow=False)          # straps
    c.layer(rrect(60, 12, 10, 18, 5), LEAF_DK, depth=2, shadow=False)
    c.layer(rrect(22, 24, 56, 58, 13), LEAF, depth=4)                          # the bag
    c.layer(rrect(22, 20, 56, 20, 10), LEAF_DK, depth=3)                       # the flap
    c.flat(rrect(45, 34, 10, 6, 3), YELLOW)                                    # the clasp
    c.layer(rrect(34, 62, 32, 16, 6), kit.lt(LEAF, .25), depth=2, shadow=False)   # a pocket
    c.face(50, 50, 7, "happy")


def t_wash(c):
    for side, x in ((-1, 30), (1, 66)):
        hand = rrect(x - 12, 46, 24, 34, 11) + ellipse(x + side * 13, 62, 6, 9)
        c.layer(hand, SKIN, depth=3)
        for i in range(3):                                                     # finger gaps
            fx = x - 6 + i * 6
            c.stroke(path([(fx, 48), (fx, 58)]), kit.dk(SKIN, .18), 1.4)
    for (bx, by, br) in ((28, 30, 7), (74, 28, 8), (54, 40, 5)):
        c.layer(circle(bx, by, br), BLUE, depth=1, shadow=False, op=.75)
        c.flat(circle(bx - br * .35, by - br * .35, br * .3), WHITE, op=.9)
    c.layer(circle(49, 24, 13), BLUE, depth=2, shadow=False, op=.9)            # the big bubble
    c.flat(circle(44, 19, 3.5), WHITE, op=.9)
    c.face(49, 25, 5, "happy")


def t_play(c):
    c.layer(circle(48, 50, 30), CORAL, depth=4)
    c.flat(rrect(19.5, 42, 57, 16, 8), CREAM)                                  # the stripe
    c.flat(star(30, 30, 6), YELLOW)
    c.face(48, 50, 7, "happy")


def t_chore(c):
    c.layer(rrect(-4, -48, 8, 52, 4).rotate(25, 0, 0).move(44, 58), WOOD, depth=3)        # the handle
    c.layer(poly([(22, 86), (72, 86), (62, 54), (36, 54)]), "#F0CE7A", depth=4)          # the bristles
    for i in range(4):
        x0 = 36 + i * 8.5
        c.stroke(path([(x0 + (x0 - 49) * .15, 66), (x0 + (x0 - 49) * .5, 84)]), kit.dk("#F0CE7A", .15), 1.6)
    c.layer(rrect(33, 52, 32, 10, 5), CORAL, depth=2, shadow=False)            # the band
    c.face(48, 74, 6, "happy")


def t_bath(c):
    for x in (22, 70):                                                         # feet
        c.layer(rrect(x, 74, 10, 8, 4), WOOD_DK, depth=2, shadow=False)
    c.layer(rrect(12, 42, 76, 34, 8, 6, 6, 18, 18), PAPER, depth=4)            # the tub
    c.flat(ellipse(50, 44, 34, 6), BLUE)                                       # the water
    c.layer(rrect(78, 26, 6, 18, 3), GREY, depth=2, shadow=False)              # the tap
    c.layer(rrect(72, 24, 14, 6, 3), GREY, depth=2, shadow=False)
    for (bx, by, br) in ((30, 32, 6), (46, 26, 8), (60, 34, 5)):
        c.layer(circle(bx, by, br), BLUE, depth=1, shadow=False, op=.6)
        c.flat(circle(bx - br * .35, by - br * .35, br * .3), WHITE, op=.9)
    c.face(50, 60, 7, "happy")


def t_sleep(c):
    c.layer(crescent(44, 50, 30, 15, -9, 25), YELLOW, depth=4)
    c.layer(star(74, 26, 6), YELLOW, depth=2, shadow=False)
    c.layer(star(80, 58, 4), YELLOW, depth=1, shadow=False)
    c.face(34, 52, 6, "sleepy")


def t_market(c):
    c.stroke(path([(76, 36), (86, 18)]), "#8FB4E3", 4)                         # the handle
    c.layer(circle(87, 16, 4), CORAL, depth=1, shadow=False)
    c.layer(poly([(16, 32), (78, 32), (70, 66), (26, 66)]), "#8FB4E3", depth=4)   # the basket
    for yy in (44, 56):
        c.stroke(path([(22, yy), (72, yy)]), kit.dk("#8FB4E3", .2), 1.4, op=.8)
    for x in (36, 48, 60):
        c.stroke(path([(x, 36), (x, 62)]), kit.dk("#8FB4E3", .2), 1.4, op=.8)
    c.layer(rrect(16, 30, 62, 6, 3), kit.dk("#8FB4E3", .15), depth=2, shadow=False)
    for x in (32, 64):                                                         # wheels
        c.layer(circle(x, 76, 7), DARK, depth=2, shadow=False)
        c.flat(circle(x, 76, 2.5), GREY)
    c.face(48, 50, 7, "happy")


def t_cook(c):
    for (x0, bulge) in ((40, -1), (54, 1)):                                    # steam
        c.stroke(path([(x0, 24), (x0 + 4 * bulge, 18), (x0, 12), (x0 + 4 * bulge, 6)]), GREY, 2.4, op=.8)
    c.layer(rrect(6, 46, 16, 8, 4), MINT_DK, depth=2, shadow=False)            # handles
    c.layer(rrect(78, 46, 16, 8, 4), MINT_DK, depth=2, shadow=False)
    c.layer(rrect(18, 40, 64, 40, 6, 6, 6, 14, 14), MINT_DK, depth=4)          # the pot
    c.layer(ellipse(50, 40, 36, 7), kit.lt(MINT_DK, .25), depth=3)             # the lid
    c.layer(circle(50, 32, 5), CORAL, depth=2, shadow=False)                   # the knob
    c.face(50, 62, 7, "happy")


def t_nap(c):
    c.layer(rrect(12, 30, 72, 42, 16), LAVENDER, depth=4)                      # the pillow
    for (x, y) in ((14, 32), (82, 32), (14, 70), (82, 70)):
        c.layer(circle(x, y, 5), LAVENDER_DK, depth=1, shadow=False)
    c.stroke(path([(22, 44), (30, 40), (38, 44)]), LAVENDER_DK, 1.6, op=.6)   # a soft crease
    c.face(48, 52, 7, "sleepy")
    for i, s in enumerate((5, 7)):
        xx, yy = 72 + i * 8, 20 - i * 10
        c.stroke(path([(xx, yy), (xx + s, yy), (xx, yy + s), (xx + s, yy + s)]), LAVENDER_DK, 1.8)


TIMES = {"wake": t_wake, "teeth": t_teeth, "dress": t_dress, "meal": t_meal, "school": t_school, "wash": t_wash,
         "play": t_play, "chore": t_chore, "bath": t_bath, "sleep": t_sleep, "market": t_market, "cook": t_cook,
         "nap": t_nap}


# ---------------------------------------------------------------- weather
def w_sun(c):
    sun(c, 48, 50, 25, YELLOW, ORANGE, "happy", rays=8, ray_len=13)


def w_rain(c):
    for (x, y) in ((30, 72), (50, 80), (70, 72)):
        c.layer(drop(x, y, 5.5), BLUE, depth=2, shadow=False)
    c.layer(cloud(48, 38, 66, 34), PAPER, depth=4)
    c.face(48, 42, 7, "smile")


def w_cold(c):
    cx, cy = 48, 50
    for i in range(6):
        a = 60 * i
        arm = path([(0, 0), (0, -30)]).rotate(a, 0, 0).move(cx, cy)
        c.stroke(arm, BLUE, 4.5)
        for t in (-18, -26):
            for side in (-1, 1):
                br = path([(0, t), (side * 7, t - 6)]).rotate(a, 0, 0).move(cx, cy)
                c.stroke(br, BLUE, 3)
    c.layer(circle(cx, cy, 12), PAPER, depth=2, shadow=False)
    c.face(cx, cy, 4.5, "happy")


def w_hot(c):
    sun(c, 46, 50, 25, ORANGE, kit.dk(ORANGE, .12), "sleepy", rays=10, ray_len=11)
    for (x, y) in ((76, 40), (80, 62)):
        c.layer(drop(x, y, 4.5), BLUE, depth=2, shadow=False)
        c.flat(circle(x - 1.5, y - 1, 1.3), WHITE, op=.8)


def w_storm(c):
    for (x, y) in ((26, 74), (54, 82)):
        c.layer(drop(x, y, 5), BLUE, depth=2, shadow=False)
    c.layer(cloud(50, 42, 72, 38), STORM, depth=4)
    pts = []
    for i in range(40):                                                        # the swirl
        t = i / 39
        a = t * 3.3 * math.pi
        r_ = 15 * (1 - t * .85)
        pts.append((64 + r_ * math.cos(a), 36 + r_ * math.sin(a)))
    c.stroke(path(pts), kit.lt(STORM, .4), 2.6)
    c.face(38, 44, 6, "open")


WEATHER = {"sun": w_sun, "rain": w_rain, "cold": w_cold, "hot": w_hot, "storm": w_storm}


# ---------------------------------------------------------------- build
def build():
    face_svg()
    hand_svg()
    files = 2
    for name, fn in TIMES.items():
        c = icon()
        fn(c)
        kit.write_svg(OUT / f"t_{name}.svg", c.svg(), (100, 100))
        files += 1
    for name, fn in WEATHER.items():
        c = icon()
        fn(c)
        kit.write_svg(OUT / f"w_{name}.svg", c.svg(), (100, 100))
        files += 1
    print(f"clock: {files} SVG files in {OUT.relative_to(kit.ROOT)}")


if __name__ == "__main__":
    build()
