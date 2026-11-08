"""The rewards of 小小生活家 (docs/art.md, 獎勵): app/assets/art/rewards/.

- sticker_<task>.svg, 200 x 200: a round sticker for every task (a white paper disc with a soft
  coloured rim and a tiny thickness, the task's picture inside, a small face), plus sticker_blank.svg
  (the empty dotted slot) and sticker_heart.svg (for dealing with a happening).
- chart.svg, 600 x 800: the sticker chart's board, a wooden frame with a cream sheet pinned on it and a
  ribbon with a star at the top; the app lays the stickers on the sheet.
- house_small.svg, 600 x 500: the whole house as a cut-paper doll's house, walls cut away. Every room's
  background is filled with the token #ROOM_<id> (living bedroom bathroom kitchen entrance balcony),
  exactly once each, so the app can brighten or dim rooms.
- height.svg, 100 x 600: the height chart, a tall strip with ten coloured marks and a giraffe on top.

    python3 -c "import rewards; rewards.build()"      # or: python3 build.py rewards
"""
import math

import kit
from kit import (BLUSH, CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH,
                 PEACH_DK, PINK, PINK_DK, SKY, WALL, WHITE, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, Shape, arc, circle,
                 ellipse, heart, path, poly, rect, rrect, star)

OUT = kit.ART / "rewards"
ROOM_IDS = ("living", "bedroom", "bathroom", "kitchen", "entrance", "balcony")


def room_token(room_id):
    return f"#ROOM_{room_id}"


# ================================================================ small shapes used in several pictures
def crescent(cx, cy, R, bulge=.62):
    """A moon: the right part of a circle of radius R, bitten by a circle from the left."""
    off = R * bulge                        # the biting circle's centre is off to the right
    r2 = math.hypot(off, R)
    half = math.degrees(math.atan2(R, off))
    outer = arc(cx, cy, R, -90, 90, 2)
    inner = arc(cx + off, cy, r2, 180 - half, 180 + half, 2)
    return Shape(outer.cmds + inner.cmds[1:] + [("Z",)])


def sparkle(cx, cy, r):
    """A four-pointed twinkle."""
    return star(cx, cy, r, r * .3, 4)


def toothbrush(c, cx, cy, deg, col, face=True):
    """A toothbrush, its middle at cx, cy, turned by deg (the head to the upper right)."""
    def t(s):
        return s.move(cx, cy).rotate(deg, cx, cy)
    c.layer(t(rrect(-64, -9, 100, 18, 9)), col, depth=4)                  # the handle
    c.layer(t(rrect(28, -11, 40, 22, 7)), kit.lt(col, .15), depth=4, shadow=False)   # the head
    c.layer(t(rrect(31, -26, 34, 17, 3)), CREAM, depth=2, shadow=False)   # the bristles
    for i in range(4):
        c.stroke(t(path([(36 + i * 8, -24), (36 + i * 8, -11)])), kit.dk(CREAM, .22), 1.8)
    if face:
        fx, fy = t(path([(-24, 0)])).cmds[0][1:]
        c.face(fx, fy, 6, "happy")


# ================================================================ stickers
S = 200
CX, CY, R = 96, 94, 84


def sticker(name, rim, draw):
    c = kit.Ctx(S, S)
    c.layer(circle(CX, CY, R), rim, depth=4)                               # the coloured rim
    c.layer(circle(CX, CY, R - 11), WHITE, depth=2, shadow=False, edge_col=kit.mix(rim, WHITE, .55))
    draw(c)
    kit.write_svg(OUT / f"sticker_{name}.svg", c.svg(), (S, S))


def pic_wake(c):
    for i in range(12):                                                    # rays
        a = i * 30
        c.layer(rrect(CX - 5, CY - 62, 10, 20, 5).rotate(a, CX, CY), kit.dk(YELLOW, .05), depth=2, shadow=False)
    c.layer(circle(CX, CY, 38), YELLOW, depth=4)
    c.face(CX, CY - 2, 11, "happy")


def pic_teeth(c):
    toothbrush(c, CX, CY + 6, -35, MINT_DK)
    for x, y, r in ((CX + 44, CY - 56, 11), (CX + 62, CY - 30, 6), (CX - 54, CY - 44, 7)):
        c.layer(sparkle(x, y, r), YELLOW, depth=2, shadow=False)


def pic_dress(c):
    x, y = CX, CY + 2
    shirt = poly([(x - 26, y - 44), (x - 9, y - 36), (x, y - 30), (x + 9, y - 36), (x + 26, y - 44), (x + 56, y - 20),
                  (x + 42, y - 2), (x + 30, y - 10), (x + 30, y + 46), (x - 30, y + 46), (x - 30, y - 10), (x - 42, y - 2),
                  (x - 56, y - 20)])
    c.layer(shirt, PINK, depth=4)
    c.stroke(arc(x, y - 44, 18, 20, 160), PINK_DK, 3)                      # the collar
    c.flat(rrect(x - 30, y + 36, 60, 10, 0), kit.lt(PINK, .3), op=.8)      # the hem
    c.face(x, y + 10, 9, "happy")


def pic_breakfast(c):
    x, y = CX, CY + 8
    c.layer(rrect(x - 48, y - 4, 96, 48, 24, rtl=6, rtr=6), PEACH_DK, depth=4)   # the bowl
    c.layer(ellipse(x, y - 14, 42, 18), PAPER, depth=3, shadow=False)            # the rice
    c.layer(rrect(x - 52, y - 10, 104, 14, 7), PEACH, depth=3, shadow=False)     # the rim
    c.layer(ellipse(x + 8, y - 26, 24, 13), WHITE, depth=2, shadow=False)        # the egg
    c.flat(circle(x + 8, y - 27, 8), YELLOW)
    c.flat(circle(x + 10, y - 29, 2.5), WHITE, op=.8)
    c.stroke(path([(x - 42, y - 58), (x - 20, y - 22)]), WOOD_DK, 4)             # chopsticks
    c.stroke(path([(x - 30, y - 62), (x - 14, y - 24)]), WOOD_DK, 4)
    c.face(x, y + 20, 8, "happy")


def pic_schoolgo(c):
    x, y = CX, CY + 8
    for sx in (-22, 22):                                                   # the straps
        c.layer(rrect(x + sx - 7, y - 40, 14, 60, 7), LAVENDER_DK, depth=2, shadow=False)
    c.stroke(arc(x, y - 44, 18, 200, 340), kit.dk(CORAL, .2), 7)           # the handle
    c.layer(rrect(x - 40, y - 34, 80, 90, 18), CORAL, depth=5)             # the bag
    c.layer(rrect(x - 24, y + 14, 48, 32, 10), kit.lt(CORAL, .25), depth=3, shadow=False)   # the pocket
    c.layer(rrect(x - 40, y - 34, 80, 40, 18, rbl=10, rbr=10), kit.dk(CORAL, .08), depth=3, shadow=False)   # the flap
    c.layer(rrect(x - 8, y - 4, 16, 12, 4), YELLOW, depth=2, shadow=False)    # the buckle
    c.face(x, y - 16, 9, "happy")


def pic_school(c):
    x, y = CX, CY + 10
    c.layer(rrect(x - 52, y - 14, 104, 60, 6), PEACH, depth=4)             # the building
    c.layer(poly([(x - 62, y - 12), (x, y - 56), (x + 62, y - 12)]), CORAL, depth=4)   # the roof
    bell = ellipse(x, y - 30, 11, 10) + rrect(x - 13, y - 26, 26, 8, 3)    # the bell
    c.layer(bell, YELLOW, depth=2, shadow=False)
    c.flat(circle(x, y - 15, 3.5), kit.dk(YELLOW, .3))
    c.flat(rrect(x - 3, y - 44, 6, 8, 2), WOOD_DK)
    for wx in (x - 32, x + 32):                                            # windows
        c.layer(rrect(wx - 12, y - 4, 24, 20, 4), SKY, depth=2, shadow=False)
        c.stroke(path([(wx, y - 4), (wx, y + 16)]), WHITE, 2)
    c.layer(rrect(x - 13, y + 14, 26, 32, 6, rbl=0, rbr=0), WOOD_DK, depth=2, shadow=False)   # the door
    c.flat(circle(x + 6, y + 32, 2.5), YELLOW)
    c.face(x, y + 2, 7, "happy")


def hand(x, y, flip=False):
    """A chubby hand, fingers up, thumb to the right (or to the left when flipped)."""
    s = circle(x, y, 22)
    for i, (dx, ln) in enumerate(((-15, 22), (-5, 30), (6, 32), (16, 26))):
        s = s + rrect(x + dx - 6, y - ln - 8, 12, ln + 12, 6)
    s = s + ellipse(x + 26, y + 2, 9, 7).rotate(-30, x + 26, y + 2)
    return s.flip(x) if flip else s


def pic_home(c):
    x, y = CX, CY + 16
    c.layer(hand(x - 26, y, True), PEACH, depth=4)
    c.layer(hand(x + 26, y + 4), PEACH, depth=4)
    bubbles = ((x - 54, y - 52, 11), (x + 50, y - 58, 14), (x - 10, y - 66, 8), (x + 22, y - 44, 6), (x - 34, y - 26, 5),
               (x + 60, y - 24, 6))
    for bx, by, r in bubbles:
        c.layer(circle(bx, by, r), kit.lt(SKY, .25), depth=2, shadow=False, op=.95)
        c.flat(circle(bx - r * .35, by - r * .35, r * .25), WHITE)
    c.face(x + 50, y - 58, 5, "happy")


def pic_park(c):
    x, y = CX, CY + 10
    # the ladder, on the left
    for lx in (x - 56, x - 40):
        c.stroke(path([(lx, y + 46), (lx, y - 40)]), WOOD_DK, 5)
    for i in range(5):
        c.stroke(path([(x - 56, y - 36 + i * 18), (x - 40, y - 36 + i * 18)]), WOOD_DK, 4)
    c.layer(rrect(x - 60, y - 50, 44, 12, 5), WOOD, depth=3)               # the platform
    # the slide: a wide chute from the platform down to the right
    chute = poly([(x - 22, y - 48), (x - 4, y - 48), (x + 20, y - 4), (x + 58, y + 34), (x + 58, y + 50), (x + 44, y + 50),
                  (x + 4, y + 10)])
    c.layer(chute, CORAL, depth=4)
    c.flat(poly([(x - 14, y - 44), (x - 8, y - 44), (x + 14, y - 2), (x + 48, y + 34), (x + 48, y + 44), (x + 40, y + 36),
                 (x, y - 2)]), kit.lt(CORAL, .3), op=.8)
    c.stroke(path([(x + 36, y + 50), (x + 36, y + 20)]), WOOD_DK, 5)      # the leg
    c.face(x + 20, y + 24, 6, "happy")


def pic_tidy(c):
    x, y = CX, CY + 10
    c.layer(circle(x - 30, y - 30, 16), CORAL, depth=3)                    # a ball
    c.flat(rrect(x - 46, y - 34, 32, 8, 4), YELLOW)
    c.layer(rrect(x - 10, y - 50, 28, 28, 4), LAVENDER_DK, depth=3)        # a block
    c.flat(circle(x + 4, y - 36, 5), PAPER)
    c.layer(star(x + 36, y - 30, 16), YELLOW, depth=3)                     # a star
    c.layer(rrect(x - 44, y - 12, 88, 56, 10), PEACH, depth=5)             # the box
    c.layer(rrect(x - 52, y - 24, 104, 20, 8), PEACH_DK, depth=4)          # the lid
    c.face(x, y + 16, 9, "happy")


def pic_chore(c):
    x, y = CX, CY
    c.layer(rrect(x - 7, y - 70, 14, 96, 7).rotate(22, x, y), WOOD, depth=3)     # the handle
    head = poly([(x - 10, y + 10), (x + 10, y + 10), (x + 34, y + 60), (x - 34, y + 60)]).rotate(22, x, y + 10)
    c.layer(head, YELLOW, depth=4)
    for i in range(5):
        c.stroke(path([(x - 22 + i * 11, y + 36), (x - 26 + i * 13, y + 58)]).rotate(22, x, y + 10), kit.dk(YELLOW, .2), 2)
    c.layer(rrect(x - 13, y + 6, 26, 12, 5).rotate(22, x, y + 10), CORAL, depth=2, shadow=False)   # the band
    c.dots([(x - 50, y + 56), (x - 60, y + 44), (x - 40, y + 66)], 3, GREY)
    c.face(x - 2, y + 34, 6, "happy")


def pic_dinner(c):
    x, y = CX, CY + 4
    c.layer(circle(x, y, 58), LAVENDER, depth=4)                           # the plate
    c.flat(circle(x, y, 46), WHITE)
    c.layer(ellipse(x - 20, y + 8, 22, 14), PAPER, depth=2, shadow=False)   # rice
    fish = ellipse(x + 16, y - 14, 24, 12) + poly([(x + 34, y - 14), (x + 46, y - 24), (x + 46, y - 4)])
    c.layer(fish, CORAL, depth=2, shadow=False)                            # a fish
    c.flat(circle(x + 6, y - 16, 2), DARK)
    c.layer(circle(x + 18, y + 18, 12) + circle(x + 30, y + 10, 9), LEAF, depth=2, shadow=False)   # greens
    c.face(x - 20, y + 6, 6, "happy")


def pic_bath(c):
    x, y = CX, CY + 14
    for fx in (x - 40, x + 30):
        c.layer(rrect(fx, y + 36, 14, 12, 5), WOOD_DK, depth=2, shadow=False)   # feet
    c.layer(rrect(x - 60, y - 12, 120, 56, 22, rtl=8, rtr=8), PAPER, depth=5)    # the tub
    c.flat(rrect(x - 50, y - 6, 100, 12, 6), SKY)                               # the water
    c.layer(rrect(x + 36, y - 44, 8, 36, 4), GREY, depth=2, shadow=False)        # the tap
    c.layer(rrect(x + 30, y - 46, 26, 10, 5), GREY, depth=2, shadow=False)
    for bx, by, r in ((x - 40, y - 28, 10), (x - 18, y - 42, 13), (x + 6, y - 24, 8), (x - 4, y - 60, 6), (x + 22, y - 52, 5)):
        c.layer(circle(bx, by, r), kit.lt(SKY, .3), depth=2, shadow=False, op=.95)
        c.flat(circle(bx - r * .35, by - r * .35, r * .25), WHITE)
    c.face(x - 6, y + 24, 8, "happy")


def pic_teethnight(c):
    toothbrush(c, CX + 8, CY + 14, -35, LAVENDER_DK, face=False)
    c.layer(crescent(CX - 44, CY - 36, 26), YELLOW, depth=3)
    c.face(CX - 30, CY - 36, 4.5, "sleepy")
    for x, y, r in ((CX + 56, CY - 60, 7), (CX + 30, CY - 66, 4), (CX - 66, CY + 6, 4)):
        c.layer(sparkle(x, y, r), YELLOW, depth=2, shadow=False)


def pic_sleep(c):
    x, y = CX - 6, CY + 6
    c.layer(crescent(x, y, 54, .55), YELLOW, depth=5)
    # the sleeping cap on the moon's tip: a triangle and its band, built upright and turned 35 degrees
    bx, by, tilt = x + 6, y - 44, 35
    ux, uy = math.sin(math.radians(tilt)), -math.cos(math.radians(tilt))
    c.layer(poly([(bx - 26, by), (bx + 26, by), (bx, by - 56)]).rotate(tilt, bx, by), PINK_DK, depth=3)
    c.layer(rrect(bx - 28, by - 7, 56, 14, 7).rotate(tilt, bx, by), PINK, depth=2, shadow=False)
    c.layer(circle(bx + 58 * ux, by + 58 * uy, 9), PAPER, depth=2, shadow=False)   # its pompom
    c.face(x + 26, y + 6, 6, "sleepy")
    for sx, sy, r in ((x - 50, y - 50, 6), (x - 60, y + 20, 4), (x + 62, y + 40, 5)):
        c.layer(sparkle(sx, sy, r), YELLOW, depth=2, shadow=False)


def pic_market(c):
    x, y = CX + 4, CY + 12
    c.stroke(path([(x - 60, y - 40), (x - 46, y - 40), (x - 38, y + 10)]), WOOD_DK, 6)   # the handle
    c.flat(circle(x - 60, y - 40, 5), CORAL)
    # the fruit, behind the basket's rim
    c.layer(circle(x - 14, y - 24, 15), CORAL, depth=3)                     # an apple
    c.flat(ellipse(x - 8, y - 40, 6, 3).rotate(-30, x - 8, y - 40), LEAF_DK)
    c.layer(circle(x + 18, y - 22, 14), PEACH_DK, depth=3)                  # an orange
    c.stroke(arc(x + 6, y - 8, 36, 215, 300), YELLOW, 9)                    # a banana
    basket = poly([(x - 44, y - 14), (x + 44, y - 14), (x + 34, y + 30), (x - 34, y + 30)])
    c.layer(basket, MINT, depth=4)                                          # the basket
    for i in range(1, 4):
        c.stroke(path([(x - 44 + i * 22, y - 8), (x - 34 + i * 17, y + 26)]), kit.dk(MINT, .12), 2)
    c.stroke(path([(x - 42, y + 2), (x + 42, y + 2)]), kit.dk(MINT, .12), 2)
    c.stroke(path([(x - 40, y + 16), (x + 40, y + 16)]), kit.dk(MINT, .12), 2)
    for wx in (x - 24, x + 24):                                             # wheels
        c.layer(circle(wx, y + 42, 10), DARK, depth=2, shadow=False)
        c.flat(circle(wx, y + 42, 4), GREY)
    c.face(x, y + 10, 7, "happy", col=kit.dk(MINT_DK, .4))


def pic_cook(c):
    x, y = CX, CY + 14
    for sx in (-30, 0, 30):                                                 # steam
        c.stroke(path([(x + sx, y - 38), (x + sx - 5, y - 50), (x + sx + 5, y - 62), (x + sx, y - 72)]), GREY, 3.5, op=.8)
    c.layer(rrect(x - 66, y - 14, 20, 12, 6), LAVENDER_DK, depth=2, shadow=False)   # handles
    c.layer(rrect(x + 46, y - 14, 20, 12, 6), LAVENDER_DK, depth=2, shadow=False)
    c.layer(rrect(x - 48, y - 12, 96, 58, 14, rtl=4, rtr=4), LAVENDER, depth=5)     # the pot
    c.layer(rrect(x - 54, y - 30, 108, 20, 10), LAVENDER_DK, depth=4)                # the lid
    c.layer(circle(x, y - 32, 8), YELLOW, depth=2, shadow=False)                     # the knob
    c.face(x, y + 16, 9, "happy")


def pic_nap(c):
    x, y = CX, CY + 10
    pillow = rrect(x - 60, y - 30, 120, 60, 24).rotate(-8, x, y)
    c.layer(pillow, kit.lt(SKY, .2), depth=5)
    c.stroke(rrect(x - 48, y - 18, 96, 36, 16).rotate(-8, x, y), kit.dk(SKY, .18), 2, op=.7)
    c.dots([(x - 30, y - 8), (x + 26, y + 10), (x, y + 18), (x + 30, y - 16)], 3, WHITE, op=.9)
    for zx, zy, s, w in ((x + 30, y - 72, 14, 3.5), (x + 52, y - 56, 9, 2.6)):      # Z z
        c.stroke(path([(zx, zy), (zx + s, zy), (zx, zy + s), (zx + s, zy + s)]), DARK, w, op=.8)
    c.face(x - 4, y, 8, "sleepy")


def pic_heart(c):
    c.layer(heart(CX, CY + 8, 116), PINK_DK, depth=5)
    c.flat(ellipse(CX - 34, CY - 26, 11, 7).rotate(-35, CX - 34, CY - 26), WHITE, op=.7)
    c.face(CX, CY + 2, 11, "happy")


STICKERS = {
    "wake": (YELLOW, pic_wake), "teeth": (MINT, pic_teeth), "dress": (PINK, pic_dress),
    "breakfast": (PEACH, pic_breakfast), "schoolGo": (CORAL, pic_schoolgo), "school": (PEACH, pic_school),
    "home": (SKY, pic_home), "park": (LEAF, pic_park), "tidy": (PEACH, pic_tidy), "chore": (YELLOW, pic_chore),
    "dinner": (LAVENDER, pic_dinner), "bath": (SKY, pic_bath), "teethNight": (LAVENDER, pic_teethnight),
    "sleep": (LAVENDER, pic_sleep), "market": (MINT, pic_market), "cook": (LAVENDER, pic_cook), "nap": (SKY, pic_nap),
    "heart": (PINK, pic_heart),
}


def sticker_blank():
    """The empty slot: a faint disc with a dotted outline, no thickness."""
    c = kit.Ctx(S, S)
    c.flat(circle(CX, CY, R - 4), kit.lt(WALL, .4), op=.7)
    pts = [(CX + (R - 6) * math.cos(a), CY + (R - 6) * math.sin(a)) for a in [i * 2 * math.pi / 30 for i in range(30)]]
    c.dots(pts, 3.2, kit.mix(GREY, WOOD_DK, .3), op=.8)
    kit.write_svg(OUT / "sticker_blank.svg", c.svg(), (S, S))


# ================================================================ the chart board (600 x 800)
def chart():
    c = kit.Ctx(600, 800)
    c.layer(rrect(0, 0, 588, 786, 24), WOOD, depth=6)                      # the frame
    for i in range(1, 6):                                                  # faint plank lines
        c.stroke(path([(0, i * 131), (588, i * 131)]), kit.dk(WOOD, .1), 2.5, op=.6)
    c.flat(rrect(24, 24, 540, 738, 16), kit.dk(WOOD, .14))                 # the recessed board
    c.flat(rrect(24, 24, 540, 738, 16), kit.SHADOW, op=.06)
    c.layer(rrect(44, 112, 500, 630, 12), PAPER, depth=3)                  # the cream sheet
    for px, py in ((60, 128), (528, 128), (60, 726), (528, 726)):           # the pins
        c.layer(circle(px, py, 9), CORAL, depth=2, shadow_op=.25)
        c.flat(circle(px - 3, py - 3, 3), WHITE, op=.75)
    # the title ribbon: two tails, the band, a star in the middle
    for tail in (poly([(118, 54), (190, 54), (190, 94), (118, 94), (138, 74)]),
                 poly([(398, 54), (470, 54), (450, 74), (470, 94), (398, 94)])):
        c.layer(tail, PINK_DK, depth=4)
    c.layer(rrect(150, 42, 288, 60, 12), PINK, depth=5)
    c.flat(rrect(162, 52, 264, 40, 8), kit.lt(PINK, .3), op=.6)
    c.layer(star(294, 72, 24), YELLOW, depth=3)
    c.face(294, 72, 4.5, "smile")
    kit.write_svg(OUT / "chart.svg", c.svg(), (600, 800))


# ================================================================ the doll's house (600 x 500)
HOUSE_X0, HOUSE_X1 = 110, 580
UP_Y0, UP_Y1 = 130, 284          # the upper floor's rooms
GR_Y0, GR_Y1 = 296, 450          # the ground floor's rooms
WALL_T = 12


def room_rect(c, room_id, x0, y0, x1, y1):
    """A room's background: its token colour, once, and a soft shade along the top and left (the inside
    of the box)."""
    c.flat(rect(x0, y0, x1 - x0, y1 - y0), room_token(room_id))
    c.flat(rect(x0, y0, x1 - x0, 10), kit.SHADOW, op=.08)
    c.flat(rect(x0, y0, 8, y1 - y0), kit.SHADOW, op=.05)
    c.flat(rect(x0, y1 - 22, x1 - x0, 22), WOOD, op=.55)                   # the floor


def mini_face(c, x, y, s=3.2, mood="happy"):
    c.face(x, y, s, mood)


def furnish_bedroom(c, x0, y1):
    # a bed with a pillow and a star blanket, a wardrobe, the height chart on the wall
    c.layer(rrect(x0 + 24, y1 - 64, 110, 36, 8), WOOD, depth=3, shadow=False)
    c.layer(rrect(x0 + 30, y1 - 70, 98, 22, 8), SKY, depth=2, shadow=False)
    c.layer(rrect(x0 + 36, y1 - 78, 30, 14, 6), PAPER, depth=2, shadow=False)
    c.dots([(x0 + 84, y1 - 60), (x0 + 108, y1 - 60)], 3, WHITE, op=.9)
    c.layer(rrect(x0 + 150, y1 - 110, 50, 86, 6), WOOD_DK, depth=3, shadow=False)
    c.stroke(path([(x0 + 175, y1 - 104), (x0 + 175, y1 - 30)]), kit.dk(WOOD_DK, .2), 2)
    c.layer(rrect(x0 + 8, y1 - 130, 10, 90, 3), kit.lt(WOOD, .3), depth=1, shadow=False)
    for i in range(5):
        c.flat(rect(x0 + 8, y1 - 124 + i * 18, 10, 3), (PINK_DK, CORAL, YELLOW, LEAF, MINT_DK)[i])
    mini_face(c, x0 + 51, y1 - 72, 2.6)


def furnish_bathroom(c, x0, y1):
    # a bathtub with bubbles, a toilet, a round mirror over a sink
    c.layer(rrect(x0 + 14, y1 - 60, 90, 36, 14, rtl=6, rtr=6), PAPER, depth=3, shadow=False)
    c.flat(rrect(x0 + 22, y1 - 56, 74, 8, 4), SKY)
    c.dots([(x0 + 40, y1 - 66), (x0 + 60, y1 - 72), (x0 + 80, y1 - 64)], 4, kit.lt(SKY, .3))
    c.layer(rrect(x0 + 130, y1 - 50, 30, 26, 10), PAPER, depth=3, shadow=False)
    c.layer(rrect(x0 + 134, y1 - 74, 22, 30, 5), PAPER, depth=2, shadow=False)
    c.layer(rrect(x0 + 176, y1 - 54, 34, 30, 6), PAPER, depth=3, shadow=False)
    c.layer(circle(x0 + 193, y1 - 92, 16), SKY, depth=2, shadow=False)
    c.stroke(circle(x0 + 193, y1 - 92, 16), WOOD, 3)
    mini_face(c, x0 + 59, y1 - 38, 2.6)


def furnish_kitchen(c, x0, y1):
    # a fridge with a face, a stove with a pot, a little table
    c.layer(rrect(x0 + 10, y1 - 108, 42, 84, 6), PAPER, depth=3, shadow=False)
    c.stroke(path([(x0 + 14, y1 - 72), (x0 + 48, y1 - 72)]), GREY, 2)
    c.flat(rrect(x0 + 44, y1 - 100, 4, 18, 2), GREY)
    mini_face(c, x0 + 31, y1 - 90, 2.6)
    c.layer(rrect(x0 + 62, y1 - 62, 40, 38, 5), GREY, depth=3, shadow=False)
    c.layer(rrect(x0 + 68, y1 - 72, 28, 12, 5), LAVENDER, depth=2, shadow=False)
    c.flat(circle(x0 + 82, y1 - 74, 3), YELLOW)
    c.layer(ellipse(x0 + 126, y1 - 56, 18, 6), WOOD, depth=3, shadow=False)
    c.stroke(path([(x0 + 126, y1 - 52), (x0 + 126, y1 - 26)]), WOOD_DK, 4)


def furnish_living(c, x0, x1, y1):
    # the sofa (with its face), a lamp, the TV on a shelf; the stairs are drawn by the caller
    c.layer(rrect(x0 + 16, y1 - 62, 70, 28, 10), MINT, depth=3, shadow=False)
    c.layer(rrect(x0 + 10, y1 - 48, 82, 22, 8), kit.lt(MINT, .1), depth=2, shadow=False)
    c.flat(heart(x0 + 34, y1 - 44, 12), PINK)
    mini_face(c, x0 + 60, y1 - 50, 2.8)
    c.layer(poly([(x0 + 102, y1 - 100), (x0 + 122, y1 - 100), (x0 + 126, y1 - 84), (x0 + 98, y1 - 84)]), YELLOW, depth=2, shadow=False)
    c.stroke(path([(x0 + 112, y1 - 84), (x0 + 112, y1 - 28)]), WOOD_DEEP, 3)
    c.flat(ellipse(x0 + 112, y1 - 27, 10, 3), WOOD_DK)
    c.layer(rrect(x0 + 28, y1 - 120, 40, 28, 6), LAVENDER, depth=2, shadow=False)
    c.flat(rrect(x0 + 32, y1 - 116, 32, 18, 3), "#8E8AA6")
    c.layer(rrect(x0 + 30, y1 - 92, 36, 6, 3), WOOD, depth=2, shadow=False)


def furnish_entrance(c, x0, y1):
    # the front door with a round window, a shoe rack, an umbrella
    c.layer(rrect(x0 + 60, y1 - 110, 40, 86, 6, rbl=0, rbr=0), WOOD_DK, depth=3, shadow=False)
    c.flat(circle(x0 + 80, y1 - 88, 8), SKY)
    c.flat(circle(x0 + 92, y1 - 66, 3), YELLOW)
    c.layer(rrect(x0 + 8, y1 - 56, 42, 32, 5), WOOD, depth=3, shadow=False)
    c.stroke(path([(x0 + 10, y1 - 40), (x0 + 48, y1 - 40)]), WOOD_DK, 2)
    c.dots([(x0 + 18, y1 - 47), (x0 + 30, y1 - 47), (x0 + 40, y1 - 47)], 3.5, CORAL)
    c.dots([(x0 + 18, y1 - 31), (x0 + 30, y1 - 31)], 3.5, LAVENDER_DK)
    c.stroke(path([(x0 + 26, y1 - 84), (x0 + 26, y1 - 64)]), WOOD_DEEP, 3)
    c.layer(ellipse(x0 + 26, y1 - 88, 14, 7), PINK_DK, depth=2, shadow=False)


def furnish_balcony(c, x0, y1):
    # the railing, a plant pot with a face, the buddy's bowl, a bin
    c.layer(poly([(x0 + 10, y1 - 62), (x0 + 26, y1 - 56), (x0 + 24, y1 - 32), (x0 + 12, y1 - 32)]), PEACH_DK, depth=2, shadow=False)
    c.layer(circle(x0 + 12, y1 - 72, 8) + circle(x0 + 24, y1 - 72, 8) + circle(x0 + 18, y1 - 82, 8), LEAF, depth=2, shadow=False)
    c.layer(rrect(x0 + 34, y1 - 36, 16, 8, 3), SKY, depth=2, shadow=False)
    c.layer(rrect(x0 + 58, y1 - 54, 20, 26, 4), LEAF_DK, depth=2, shadow=False)
    c.flat(rrect(x0 + 56, y1 - 58, 24, 6, 3), kit.dk(LEAF_DK, .2))
    for i in range(6):
        c.stroke(path([(x0 + 6 + i * 15, y1 - 24), (x0 + 6 + i * 15, y1 + 4)]), WOOD_DK, 3)
    c.layer(rrect(x0 - 2, y1 - 28, 90, 6, 3), WOOD_DK, depth=2, shadow=False)


def house_small():
    c = kit.Ctx(600, 500)
    # the sun, top left
    for i in range(8):
        c.layer(rrect(62 - 3, 14, 6, 14, 3).rotate(i * 45, 62, 58), kit.dk(YELLOW, .05), depth=1, shadow=False)
    c.layer(circle(62, 58, 26), YELLOW, depth=3)
    c.face(62, 56, 7, "happy")
    # the chimney and its smoke, behind the roof
    c.layer(rrect(470, 48, 36, 70, 4), PEACH_DK, depth=4, shadow=False)
    c.flat(rrect(466, 44, 44, 12, 4), kit.dk(PEACH_DK, .15))
    for sx, sy, r in ((494, 30, 9), (506, 16, 7), (520, 6, 5)):
        c.flat(circle(sx, sy, r), PAPER, op=.85)
    # the base board the house stands on
    c.layer(rrect(10, GR_Y1 + 4, 578, 18, 6), WOOD_DK, depth=5)
    # the house's back wall (pink paper), then the rooms cut into it
    c.layer(rrect(HOUSE_X0, UP_Y0 - 12, HOUSE_X1 - HOUSE_X0, GR_Y1 - UP_Y0 + 14, 8), PINK, depth=6)
    bed_x1, bath_x0 = 340, 352
    kit_x1, liv_x0, liv_x1, ent_x0 = 268, 280, 448, 460
    x0, x1 = HOUSE_X0 + WALL_T, HOUSE_X1 - WALL_T
    room_rect(c, "bedroom", x0, UP_Y0, bed_x1, UP_Y1)
    room_rect(c, "bathroom", bath_x0, UP_Y0, x1, UP_Y1)
    room_rect(c, "kitchen", x0, GR_Y0, kit_x1, GR_Y1)
    room_rect(c, "living", liv_x0, GR_Y0, liv_x1, GR_Y1)
    room_rect(c, "entrance", ent_x0, GR_Y0, x1, GR_Y1)
    furnish_bedroom(c, x0, UP_Y1)
    furnish_bathroom(c, bath_x0, UP_Y1)
    furnish_kitchen(c, x0, GR_Y1)
    furnish_living(c, liv_x0, liv_x1, GR_Y1)
    furnish_entrance(c, ent_x0, GR_Y1)
    # the stairs on the living room's right, up to the floor above
    steps, sx0, sy = 6, liv_x1 - 64, GR_Y1 - 22
    pts = [(sx0, sy)]
    for i in range(steps):
        pts += [(sx0 + i * 10, sy - (i + 1) * 20), (sx0 + (i + 1) * 10, sy - (i + 1) * 20)]
    pts += [(liv_x1, sy - steps * 20), (liv_x1, sy)]
    c.layer(poly(pts), WOOD, depth=3, shadow=False)
    c.stroke(path([(sx0 + 4, sy - 44), (sx0 + 54, sy - 144)]), WOOD_DEEP, 3)
    c.flat(circle(sx0 + 4, sy - 44, 4), CORAL)
    # the floor between the storeys and the inner walls (the thickness of the paper partitions)
    c.layer(rrect(x0, UP_Y1, x1 - x0, GR_Y0 - UP_Y1, 2), WOOD_DK, depth=2, shadow=False)
    c.layer(rrect(bed_x1, UP_Y0, bath_x0 - bed_x1, UP_Y1 - UP_Y0, 2), PINK_DK, depth=2, shadow=False)
    c.layer(rrect(kit_x1, GR_Y0, liv_x0 - kit_x1, GR_Y1 - GR_Y0, 2), PINK_DK, depth=2, shadow=False)
    c.layer(rrect(liv_x1, GR_Y0, ent_x0 - liv_x1, GR_Y1 - GR_Y0, 2), PINK_DK, depth=2, shadow=False)
    # the balcony, outside on the left: its own little floor and roof, the sky behind
    c.flat(rect(20, GR_Y0 + 60, HOUSE_X0 - 20, GR_Y1 - GR_Y0 - 60), room_token("balcony"))
    c.layer(rrect(16, GR_Y0 + 50, HOUSE_X0 - 14, 10, 4), MINT, depth=3)
    furnish_balcony(c, 24, GR_Y1 - 6)
    c.layer(rrect(14, GR_Y1 - 6, HOUSE_X0 - 10, 12, 4), WOOD, depth=3)
    # the roof, with a round attic window
    c.layer(poly([(96, UP_Y0 - 4), (345, 26), (586, UP_Y0 - 4)]), MINT, depth=6)
    c.flat(poly([(120, UP_Y0 - 14), (345, 40), (570, UP_Y0 - 14)]), kit.lt(MINT, .18), op=.6)
    c.layer(circle(345, 92, 16), SKY, depth=2, shadow=False)
    c.stroke(circle(345, 92, 16), WOOD, 3)
    c.stroke(path([(345, 76), (345, 108)]), WOOD, 2.5)
    c.stroke(path([(329, 92), (361, 92)]), WOOD, 2.5)
    text = c.svg()
    for rid in ROOM_IDS:
        if text.count(room_token(rid) + '"') != 1:
            raise SystemExit(f"house_small.svg: {room_token(rid)} must appear exactly once")
    kit.write_svg(OUT / "house_small.svg", text, (600, 500))


# ================================================================ the height chart (100 x 600)
def height():
    c = kit.Ctx(100, 600)
    giraffe = "#F5C96B"
    c.layer(rrect(38, 60, 24, 60, 8), giraffe, depth=2, shadow=False)        # the neck, behind the strip
    c.dots([(44, 76), (54, 92), (46, 106)], 3.5, PEACH_DK)
    c.layer(rrect(12, 72, 68, 516, 10), kit.lt(WOOD, .2), depth=5)          # the strip
    c.stroke(path([(28, 90), (28, 572)]), kit.dk(WOOD, .1), 2, op=.6)
    colours = (PINK_DK, CORAL, YELLOW, LEAF, MINT_DK, SKY, LAVENDER_DK, PINK_DK, CORAL, YELLOW)
    for i in range(10):
        y = 118 + i * 48
        c.layer(rrect(18, y - 5, 32, 10, 4), colours[i], depth=2, shadow=False)
        if i < 9:
            c.dots([(28, y + 24)], 2.5, kit.dk(WOOD, .2), op=.7)
    # the giraffe's head, peeking over the top
    for hx in (40, 60):                                                     # ossicones
        c.stroke(path([(hx, 34), (hx, 18)]), kit.dk(giraffe, .2), 4)
        c.flat(circle(hx, 16, 5), PEACH_DK)
    c.layer(ellipse(22, 44, 9, 6).rotate(-20, 22, 44), giraffe, depth=2, shadow=False)   # ears
    c.layer(ellipse(78, 44, 9, 6).rotate(20, 78, 44), giraffe, depth=2, shadow=False)
    c.layer(ellipse(50, 46, 28, 24), giraffe, depth=3)
    c.layer(ellipse(50, 58, 16, 10), kit.lt(giraffe, .3), depth=1, shadow=False)        # the muzzle
    c.dots([(44, 58), (56, 58)], 2, DARK)
    c.dots([(30, 36), (70, 36)], 3, PEACH_DK)
    c.face(50, 42, 7, "happy")
    kit.write_svg(OUT / "height.svg", c.svg(), (100, 600))


# ================================================================ build
def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (rim, draw) in STICKERS.items():
        sticker(name, rim, draw)
    sticker_blank()
    chart()
    house_small()
    height()
    n_files = len(STICKERS) + 4
    print(f"rewards: {n_files} files in {OUT.relative_to(kit.ROOT)}")


if __name__ == "__main__":
    build()
