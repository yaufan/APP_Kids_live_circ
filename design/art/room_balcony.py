"""陽台 the balcony: outdoors, a railing in front of the sky (the background's sky is #SKY, recoloured by
the app), three plant pots, the laundry rack, the buddy's bowls, two bins and a watering can. Same
structure as room_living.py; boxes in scene pixels (600 x 800).

The avatar (308 x 400 on the stand box) covers about x 138-376 at head height (y 337-566) and
x 161-350 lower down, so the bins stay left of x 138, the rack, can and plants right of x 376, and the
bowls sit at the avatar's feet (below y 690).
"""
import math

import kit
from kit import (CORAL, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH, PEACH_DK,
                 PINK, PINK_DK, SKY_TOKEN, WALL, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, Shape, circle, cloud, ellipse,
                 heart, path, poly, rect, rrect)
import scene
from scene import Box, Deco, Thing

FLOOR_Y = 560
BLUE = "#9DC4EC"
BROWN_LEAF = kit.mix(LEAF_DK, WOOD_DK, .65)     # a wilted leaf


# ---------------------------------------------------------------- background
def draw_bg(c):
    c.flat(rect(0, 0, 600, FLOOR_Y + 20), SKY_TOKEN)                       # the sky (recoloured by the app)
    c.flat(cloud(120, 170, 150, 60), PAPER, op=.92)
    c.flat(cloud(420, 120, 120, 50), PAPER, op=.9)
    c.flat(cloud(300, 250, 90, 36), PAPER, op=.85)
    # far-away rooftops, then soft green hills, behind the railing
    sky = [(0, 500), (40, 500), (58, 468), (76, 500), (120, 500), (120, 484), (166, 484), (166, 500), (200, 500),
           (222, 456), (244, 500), (290, 500), (290, 478), (340, 478), (340, 500), (380, 500), (400, 466), (420, 500),
           (470, 500), (470, 486), (516, 486), (516, 500), (550, 500), (568, 472), (586, 500), (600, 500)]
    c.flat(poly(sky + [(600, FLOOR_Y), (0, FLOOR_Y)]), kit.lt(LAVENDER, .4))
    c.flat(ellipse(110, FLOOR_Y, 190, 50), kit.lt(MINT, .3))
    c.flat(ellipse(440, FLOOR_Y, 230, 62), kit.lt(MINT, .22))
    c.flat(ellipse(620, FLOOR_Y, 150, 40), kit.lt(MINT, .3))
    c.flat(rect(0, FLOOR_Y - 30, 600, 30), kit.lt(MINT, .22))
    # the balcony above (its underside) along the top edge
    c.layer(rrect(0, -12, 600, 48, 6), WALL, depth=6)
    # the floor: pale terracotta tiles with a kerb where the railing stands
    c.flat(rect(0, FLOOR_Y, 600, 800 - FLOOR_Y), kit.lt(PEACH, .3))
    lines = Shape()
    for i in range(1, 10):
        lines = lines + rect(i * 60 - 1, FLOOR_Y, 2, 240)
    for i in range(1, 4):
        lines = lines + rect(0, FLOOR_Y + i * 60 - 1, 600, 2)
    c.flat(lines, kit.dk(PEACH, .14), op=.6)
    c.flat(rect(0, FLOOR_Y, 600, 14), kit.SHADOW, op=.10)
    c.layer(rrect(0, FLOOR_Y - 12, 600, 16, 3), kit.lt(GREY, .35), depth=4, shadow=False)
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_railing(c, state):
    W, H = c.w - 10, c.h - 10      # 590 x 190
    posts = Shape()
    for i in range(12):
        posts = posts + rrect(26 + i * 49, 12, 10, H - 36, 4)
    c.layer(posts, PAPER, depth=3, shadow=False)
    for x in (0, W - 18):                                                  # the end posts
        c.layer(rrect(x, 0, 18, H - 8, 6), WOOD_DK, depth=5)
        c.flat(circle(x + 9, 8, 6), WOOD)
    c.layer(rrect(0, H - 26, W, 14, 5), WOOD_DK, depth=4)                  # the bottom rail
    c.layer(rrect(0, 2, W, 18, 7), WOOD, depth=5)                          # the top rail


def _shirt(c, x, y, w, h, col):
    sh = poly([(x + w * .26, y), (x + w * .74, y), (x + w, y + h * .3), (x + w * .82, y + h * .42),
               (x + w * .82, y + h), (x + w * .18, y + h), (x + w * .18, y + h * .42), (x, y + h * .3)])
    c.layer(sh, col, depth=3)
    c.flat(rrect(x + w * .36, y, w * .28, h * .1, 3), kit.dk(col, .25))


def _sock(c, x, y, col):
    sh = rrect(x, y, 16, 36, 6) + rrect(x, y + 24, 30, 14, 7)
    c.layer(sh, col, depth=3)
    c.flat(rrect(x, y, 16, 7, 3), PAPER, op=.85)
    c.flat(rrect(x + 3, y + 11, 10, 3, 1.5), PAPER, op=.7)


def _peg(c, x, y):
    c.layer(rrect(x - 3.5, y, 7, 14, 3), PINK_DK, depth=2, shadow=False)


def draw_rack(c, state):
    W, H = c.w - 10, c.h - 10      # 210 x 180
    empty = state == "empty"
    for x in (6, W - 16):                                                  # the uprights
        c.layer(rrect(x, 8, 10, H - 14, 4), WOOD_DK, depth=3)
    for x in (0, W - 44):                                                  # the feet
        c.layer(rrect(x, H - 10, 44, 10, 4), WOOD_DK, depth=3, shadow=False)
    c.layer(rrect(0, 8, W, 10, 4), WOOD, depth=4)                          # the top bar
    c.layer(rrect(0, 100, W, 8, 4), WOOD, depth=3)                         # the lower bar
    if not empty:
        _shirt(c, 22, 20, 58, 62, YELLOW)
        _peg(c, 51, 8)
        _sock(c, 92, 20, CORAL)
        _peg(c, 100, 8)
        _sock(c, 128, 20, BLUE)
        _peg(c, 136, 8)
        _shirt(c, 150, 22, 52, 56, MINT)
        _peg(c, 176, 8)
        c.layer(rrect(60, 102, 54, 40, 6), PINK, depth=3)                  # a towel over the lower bar
        c.flat(rrect(60, 122, 54, 5, 2), PAPER, op=.8)
    # the laundry basket at the foot: full of folded clothes once the rack is empty
    if empty:
        c.layer(rrect(W / 2 - 30, H - 50, 26, 16, 4), YELLOW, depth=2, shadow=False)
        c.layer(rrect(W / 2 + 2, H - 48, 26, 14, 4), MINT, depth=2, shadow=False)
        c.layer(rrect(W / 2 - 14, H - 56, 26, 12, 4), CORAL, depth=2, shadow=False)
    c.layer(poly([(W / 2 - 38, H - 42), (W / 2 + 38, H - 42), (W / 2 + 32, H - 4), (W / 2 - 32, H - 4)]), WOOD, depth=4)
    for i in range(1, 4):
        c.stroke(path([(W / 2 - 36 + i, H - 42 + i * 9), (W / 2 + 36 - i, H - 42 + i * 9)]), kit.dk(WOOD, .18), 1.6, op=.7)
    c.layer(rrect(W / 2 - 42, H - 46, 84, 9, 4), WOOD_DK, depth=3)


def _pot(c, x0, y, mood):
    c.layer(poly([(x0 + 4, y + 8), (x0 + 36, y + 8), (x0 + 32, y + 48), (x0 + 8, y + 48)]), PEACH_DK, depth=4)
    c.layer(rrect(x0, y, 40, 13, 6), PEACH, depth=3)
    c.face(x0 + 20, y + 28, 5, mood)


def draw_plants(c, state):
    W, H = c.w - 10, c.h - 10      # 130 x 140
    wilt = state == "wilt"
    py = H - 48
    # pot 1: a round bush with a pink flower
    x0 = 2
    c.layer(circle(x0 + 20, py - 18, 17) + circle(x0 + 8, py - 8, 11) + circle(x0 + 32, py - 8, 11), LEAF, depth=3, shadow=False)
    c.flat(circle(x0 + 20, py - 32, 6.5), PINK_DK)
    c.flat(circle(x0 + 20, py - 32, 2.5), YELLOW)
    _pot(c, x0, py, "happy")
    # pot 2: tall leaves (droopy and brown when wilted)
    x0 = 46
    base = (x0 + 20, py + 6)
    if wilt:
        # brown leaves flopping over the rim: each hangs from the base, bent down on its side
        for sx, ln in ((-1, 34), (1, 30), (-1, 22), (1, 40)):
            cx, cy = base[0] + sx * 14, base[1] - 6 + ln * .35
            c.layer(ellipse(cx, cy, 6, ln / 2).rotate(sx * 58, cx, cy), BROWN_LEAF, depth=3, shadow=False)
        c.layer(ellipse(base[0], base[1] - 10, 5, 9), BROWN_LEAF, depth=3, shadow=False)
    else:
        for ang, ln, wd in ((-32, 48, 8), (32, 48, 8), (-14, 56, 8), (14, 56, 8), (0, 40, 7)):
            a = math.radians(-90 + ang)
            cx, cy = base[0] + math.cos(a) * ln / 2, base[1] + math.sin(a) * ln / 2
            c.layer(ellipse(cx, cy, wd, ln / 2).rotate(ang, cx, cy), LEAF_DK, depth=3, shadow=False)
    _pot(c, x0, py, "sleepy" if wilt else "happy")
    # pot 3: a little flowering plant
    x0 = 90
    c.stroke(path([(x0 + 20, py + 4), (x0 + 20, py - 24)]), LEAF_DK, 3)
    c.layer(ellipse(x0 + 11, py - 8, 9, 5).rotate(-30, x0 + 11, py - 8), LEAF, depth=2, shadow=False)
    c.layer(ellipse(x0 + 29, py - 12, 9, 5).rotate(30, x0 + 29, py - 12), LEAF, depth=2, shadow=False)
    for a in range(5):
        t = math.radians(-90 + a * 72)
        c.flat(circle(x0 + 20 + 7 * math.cos(t), py - 30 + 7 * math.sin(t), 4.5), YELLOW)
    c.flat(circle(x0 + 20, py - 30, 4), CORAL)
    _pot(c, x0, py, "happy")


def draw_bowl(c, state):
    W, H = c.w - 10, c.h - 10      # 100 x 40
    c.layer(rrect(0, 14, W, H - 14, 8), kit.lt(MINT, .15), depth=2, shadow_op=.12)   # a little mat
    paw = ellipse(W / 2, 30, 4.5, 3.5) + circle(W / 2 - 5.5, 24, 1.9) + circle(W / 2 - 1.8, 21.5, 1.9) \
        + circle(W / 2 + 1.8, 21.5, 1.9) + circle(W / 2 + 5.5, 24, 1.9)
    c.flat(paw, DARK, op=.4)
    c.layer(rrect(6, 10, 38, 22, 9, rtl=5, rtr=5), CORAL, depth=3)         # the food bowl
    c.flat(ellipse(25, 12, 15, 4), WOOD_DK)
    c.dots([(18, 11), (25, 10), (32, 12), (22, 13.5), (29, 13.5)], 1.8, WOOD_DEEP)
    c.layer(rrect(W - 44, 10, 38, 22, 9, rtl=5, rtr=5), BLUE, depth=3)     # the water bowl
    c.flat(ellipse(W - 25, 12, 15, 4), kit.lt(BLUE, .5))
    c.flat(ellipse(W - 30, 11.5, 4, 1.2), PAPER, op=.8)


def _bin(c, x, col, lid_col):
    c.layer(rrect(x + 4, 24, 48, 70, 8, rtl=4, rtr=4), col, depth=5)
    c.layer(rrect(x, 14, 56, 14, 6), lid_col, depth=4)
    c.layer(rrect(x + 20, 6, 16, 10, 4), kit.dk(lid_col, .15), depth=2, shadow=False)
    c.face(x + 28, 78, 6, "happy")


def draw_bins(c, state):
    W, H = c.w - 10, c.h - 10      # 120 x 100
    # the grey rubbish bin, with a little label
    _bin(c, 0, GREY, kit.dk(GREY, .18))
    c.flat(rrect(16, 42, 24, 18, 4), PAPER, op=.9)
    for i in range(3):
        c.flat(rect(20, 46 + i * 5, 16, 2), GREY)
    # the blue recycling bin, with the three arrows
    _bin(c, 64, BLUE, kit.dk(BLUE, .18))
    cx, cy, r = 92, 52, 10
    for a0 in (200, 320, 80):
        a1 = a0 + 100
        c.stroke(kit.arc(cx, cy, r, a0, a1), PAPER, 2.6)
        t = math.radians(a1)
        ex, ey = cx + r * math.cos(t), cy + r * math.sin(t)
        tx, ty = -math.sin(t), math.cos(t)
        nx, ny = math.cos(t), math.sin(t)
        c.flat(poly([(ex + tx * 5, ey + ty * 5), (ex + nx * 4, ey + ny * 4), (ex - nx * 4, ey - ny * 4)]), PAPER)


def draw_watering_can(c, state):
    W, H = c.w - 10, c.h - 10      # 70 x 70
    hd = kit.arc(30, 28, 14, 180, 360)
    c.stroke(hd.move(2.2, 3), kit.dk(MINT_DK, .32), 6)                     # the top handle
    c.stroke(hd, MINT_DK, 6)
    c.layer(poly([(48, 42), (62, 16), (69, 20), (53, 50)]), MINT_DK, depth=3)   # the spout
    c.layer(circle(66, 17, 6.5), kit.dk(MINT_DK, .12), depth=2, shadow=False)   # the rose
    c.dots([(64, 15), (68, 15), (66, 19)], 1.1, PAPER)
    c.layer(rrect(10, 26, 40, 40, 9), MINT_DK, depth=5)                    # the body
    c.flat(rrect(14, 30, 32, 5, 2.5), kit.lt(MINT_DK, .3))
    c.face(30, 50, 6.5, "happy")
    c.flat(poly([(60, 28), (57, 34), (63, 34)]) + circle(60, 35, 3), BLUE)   # a drop
    c.flat(circle(68, 34, 2), BLUE)


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    W, H = c.w - 10, c.h - 10      # 50 x 160: a wind chime hanging from the balcony above
    c.stroke(path([(W / 2, 0), (W / 2, 10)]), DARK, 2)
    c.layer(ellipse(W / 2, 14, 22, 9), WOOD, depth=3)                      # the top disc
    for x, ln, col in ((3, 64, PAPER), (14, 84, GREY), (29, 78, PAPER), (40, 58, GREY)):
        c.stroke(path([(x + 3.5, 20), (x + 3.5, 32)]), DARK, 1.4)
        c.layer(rrect(x, 32, 7, ln, 3.5), col, depth=2, shadow=False)
    c.stroke(path([(W / 2, 20), (W / 2, 122)]), DARK, 1.4)
    c.layer(circle(W / 2, 98, 6), WOOD_DK, depth=2, shadow=False)          # the clapper
    c.layer(rrect(W / 2 - 9, 120, 18, 32, 4), PINK, depth=2)               # the paper strip
    c.flat(heart(W / 2, 137, 11), PAPER)


def draw_deco_2(c, state):
    W, H = c.w - 10, c.h - 10      # 550 x 40: string lights looped along the railing
    half = W / 2

    def yy(x):
        return 4 + 20 * math.sin(math.pi * (x % half) / half)
    pts = [(x, yy(x)) for x in range(0, int(W) + 1, 10)]
    c.stroke(path(pts), DARK, 2.2)
    cols = [PINK, YELLOW, MINT, LAVENDER, CORAL]
    for i in range(12):
        x = W * (i + .5) / 12
        if abs((x % half) - 0) < 4:
            continue
        y = yy(x)
        c.layer(rrect(x - 3.5, y, 7, 6, 2), GREY, depth=2, shadow=False)
        c.layer(circle(x, y + 13, 7), cols[i % 5], depth=2)
        c.flat(circle(x - 2.4, y + 10.5, 2.2), PAPER, op=.8)


def draw_deco_3(c, state):
    W, H = c.w - 10, c.h - 10      # 70 x 80: a new flower pot hooked over the top rail
    c.layer(rrect(W / 2 - 16, 0, 32, 9, 3), WOOD_DEEP, depth=3, shadow=False)   # the bracket over the rail
    c.layer(rrect(W / 2 - 3, 8, 6, 32, 3), WOOD_DEEP, depth=2, shadow=False)
    for x, r, col in ((W / 2 - 17, 9, PINK_DK), (W / 2 + 17, 9, CORAL), (W / 2, 10, YELLOW)):
        c.layer(circle(x, 30 if x == W / 2 else 36, r), col, depth=2, shadow=False)
        c.flat(circle(x, 30 if x == W / 2 else 36, 3.2), PAPER)
    c.layer(ellipse(W / 2 - 10, 46, 9, 5).rotate(-25, W / 2 - 10, 46), LEAF, depth=2, shadow=False)
    c.layer(ellipse(W / 2 + 10, 46, 9, 5).rotate(25, W / 2 + 10, 46), LEAF, depth=2, shadow=False)
    c.layer(poly([(10, 50), (W - 10, 50), (W - 14, H), (14, H)]), LAVENDER, depth=4)   # the pot
    c.layer(rrect(6, 44, W - 12, 12, 5), LAVENDER_DK, depth=3)


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "balcony", "陽台", "balcony",
    exits={"right": "kitchen"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(135, 790, 100, 140),
    bg=draw_bg,
    things=[
        Thing("railing", "欄杆", "railing", 300, 470, 600, 200, z=3, draw=draw_railing),
        Thing("rack", "曬衣架", "laundry rack", 480, 485, 220, 190, z=10, draw=draw_rack, states=("", "empty")),
        Thing("plants", "盆栽", "plants", 525, 630, 140, 150, z=12, draw=draw_plants, states=("", "wilt")),
        Thing("watering_can", "澆水壺", "watering can", 410, 650, 80, 80, z=14, draw=draw_watering_can),
        Thing("bins", "垃圾桶", "bins", 65, 630, 130, 110, z=20, draw=draw_bins),
        Thing("bowl", "小夥伴的碗", "buddy's bowls", 250, 715, 110, 50, z=24, draw=draw_bowl),
    ],
    decos=[
        Deco("deco_1", "風鈴", "wind chime", 555, 130, 60, 170, draw=draw_deco_1),
        Deco("deco_2", "小燈串", "string lights", 300, 385, 560, 50, draw=draw_deco_2),
        Deco("deco_3", "新的花盆", "new flower pot", 90, 410, 80, 90, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
