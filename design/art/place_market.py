"""超市 the supermarket: a place outside the house (exit `back` goes to the street).

Pink wall, cream tiles, a big shelf of fruit, vegetables and milk, a child-sized cart with a face,
a cashier (a paper puppet behind a mint till), an open cooler, a hanging sign and a basket.
The puppet and the window come from place_school.py.
"""
import math

import kit
from kit import (CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH,
                 PEACH_DK, PINK, PINK_DK, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, Shape, arc, circle, cloud, ellipse, heart,
                 path, poly, rect, rrect, star)
import scene
from scene import Box, Deco, Thing
from place_school import FLOOR_Y, HAIR_BROWN, SKIN, puppet, window_bg

MARKET_WALL = "#FBDDE3"
MARKET_TILE = "#F4EBDB"
ORANGE = "#F7A24E"
CARROT = "#F28C3C"


# ---------------------------------------------------------------- small groceries (drawn flat on a shelf)
def apple(c, x, y, r=13, col=CORAL):
    c.layer(circle(x, y, r), col, depth=2, shadow=False)
    c.flat(circle(x - r * .35, y - r * .35, r * .22), PAPER, op=.6)
    c.stroke(path([(x, y - r + 2), (x, y - r - 5)]), WOOD_DEEP, 2.2)
    c.flat(ellipse(x + 6, y - r - 4, 6, 3).rotate(-30, x + 6, y - r - 4), LEAF)


def banana(c, x, y):
    c.stroke(arc(x, y - 20, 17, 30, 150), kit.dk(YELLOW, .3), 10)
    c.stroke(arc(x, y - 20, 17, 30, 150), YELLOW, 7)


def carrot(c, x, y, h=32):
    c.layer(poly([(x - 9, y - h), (x + 9, y - h), (x, y)]), CARROT, depth=2, shadow=False)
    c.stroke(path([(x - 4, y - h * .6), (x + 3, y - h * .6)]), kit.dk(CARROT, .25), 1.6)
    c.stroke(path([(x - 3, y - h * .35), (x + 2, y - h * .35)]), kit.dk(CARROT, .25), 1.6)
    for dx, ang in ((-6, -30), (0, 0), (6, 30)):
        c.flat(ellipse(x + dx, y - h - 7, 3.5, 8).rotate(ang, x + dx, y - h - 7), LEAF)


def milk(c, x, y, w=22, h=36, label=kit.SKY):
    body = rrect(x - w / 2, y - h + 10, w, h - 10, 3) + poly([(x - w / 2, y - h + 12), (x - w / 2 + 4, y - h), (x + w / 2 - 4, y - h), (x + w / 2, y - h + 12)])
    c.layer(body, PAPER, depth=2, shadow=False)
    c.flat(rrect(x - w / 2 + 3, y - h + 18, w - 6, 12, 2), label)
    c.flat(circle(x, y - h + 24, 3), PAPER)


def eggs(c, x, y, w=40):
    c.layer(rrect(x - w / 2, y - 16, w, 16, 5), PEACH, depth=2, shadow=False)
    c.dots([(x - w / 2 + 8 + i * (w - 16) / 2, y - 17) for i in range(3)], 6, PAPER)


# ---------------------------------------------------------------- background
def draw_bg(c):
    c.flat(rect(0, 0, 600, FLOOR_Y + 20), MARKET_WALL)
    for i in range(0, 600, 60):                                            # soft vertical stripes
        c.flat(rect(i, 0, 30, FLOOR_Y), kit.dk(MARKET_WALL, .04))
    window_bg(c, 24, 40, 172, 130)
    # the floor: cream tiles
    c.flat(rect(0, FLOOR_Y, 600, 800 - FLOOR_Y), MARKET_TILE)
    for i in range(1, 8):
        x = i * 80 - 20
        c.stroke(path([(x, FLOOR_Y + 4), (x, 800)]), kit.dk(MARKET_TILE, .10), 2.5)
    for i in range(3):
        y = FLOOR_Y + 60 + i * 70
        c.stroke(path([(0, y), (600, y)]), kit.dk(MARKET_TILE, .10), 2.5)
    c.flat(rect(0, FLOOR_Y, 600, 16), kit.SHADOW, op=.12)
    c.flat(rect(0, FLOOR_Y + 16, 600, 10), kit.SHADOW, op=.05)
    c.layer(rrect(0, FLOOR_Y - 14, 600, 18, 3), PINK_DK, depth=4, shadow=False)
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_shelf(c, state):
    W, H = c.w - 10, c.h - 10      # 200 x 290
    c.layer(rrect(0, 0, W, H, 10), WOOD, depth=5)                          # the case
    c.face(W / 2, 16, 7, "happy")
    rows = ((32, CREAM), (118, kit.lt(MINT, .45)), (204, kit.lt(kit.SKY, .4)))
    for y, col in rows:
        c.flat(rrect(8, y, W - 16, 78, 6), col)
    # fruit
    base = 32 + 72
    apple(c, 30, base - 13)
    apple(c, 66, base - 13)
    c.layer(circle(106, base - 12, 12), ORANGE, depth=2, shadow=False)
    c.flat(circle(102, base - 16, 3), PAPER, op=.6)
    c.flat(ellipse(110, base - 25, 5, 2.5).rotate(-20, 110, base - 25), LEAF)
    banana(c, 160, base - 6)
    # vegetables
    base = 118 + 72
    carrot(c, 30, base - 2)
    carrot(c, 62, base - 2)
    c.layer(cloud(112, base - 22, 40, 26, 3), LEAF_DK, depth=2, shadow=False)
    c.layer(rrect(106, base - 20, 12, 18, 4), kit.lt(LEAF, .3), depth=2, shadow=False)
    c.layer(circle(160, base - 14, 13), kit.dk(CORAL, .05), depth=2, shadow=False)     # a tomato
    c.flat(star(160, base - 26, 7, 3), LEAF_DK)
    c.flat(circle(155, base - 18, 3), PAPER, op=.6)
    # milk, eggs and bread
    base = 204 + 72
    milk(c, 28, base - 2)
    milk(c, 58, base - 2, label=PINK)
    eggs(c, 110, base - 2)
    c.layer(rrect(146, base - 26, 40, 24, 11), kit.lt(WOOD, .25), depth=2, shadow=False)   # a loaf
    for i in range(3):
        c.stroke(path([(152 + i * 11, base - 20), (158 + i * 11, base - 14)]), kit.dk(WOOD, .15), 2)
    for y in (104, 190, 276):                                              # the boards
        c.layer(rrect(4, y, W - 8, 8, 3), WOOD_DK, depth=3, shadow=False)


def draw_cart(c, state):
    W, H = c.w - 10, c.h - 10      # 150 x 140
    apple(c, 72, 50, 13)                                                   # peeking out
    c.stroke(path([(34, 56), (16, 22), (0, 22)]), GREY, 7)                 # the handle
    c.layer(poly([(30, 52), (140, 52), (128, 108), (42, 108)]), kit.lt(kit.SKY, .1), depth=5)   # the basket
    for i in range(1, 4):
        x0, x1 = 30 + 110 * i / 4, 42 + 86 * i / 4
        c.stroke(path([(x0, 56), (x1, 104)]), PAPER, 2, op=.55)
    c.stroke(path([(36, 80), (134, 80)]), PAPER, 2, op=.55)
    c.face(85, 84, 8, "happy")
    c.stroke(path([(44, 108), (48, 124)]), GREY, 5)                        # the frame and wheels
    c.stroke(path([(126, 108), (122, 124)]), GREY, 5)
    for x in (50, 122):
        c.layer(circle(x, 128, 11), DARK, depth=2, shadow=False)
        c.flat(circle(x, 128, 4.5), PAPER)


def draw_cashier(c, state):
    W, H = c.w - 10, c.h - 10      # 140 x 200
    puppet(c, skin=SKIN[1], shirt=YELLOW, hair="bob", hair_col=HAIR_BROWN, legs=False, u=.56, ox=14, oy=4)
    c.layer(rrect(0, 118, W, 76, 10), MINT, depth=5)                       # the counter
    c.flat(rrect(10, 136, W - 20, 48, 6), kit.lt(MINT, .25))
    c.layer(rrect(0, 112, W, 14, 6), MINT_DK, depth=3, shadow=False)
    c.layer(rrect(94, 76, 42, 40, 6), kit.lt(GREY, .45), depth=4)          # the till
    c.flat(rrect(100, 82, 30, 18, 3), kit.SKY)
    c.dots([(104 + i * 8, 108) for i in range(4)], 2.2, GREY)
    c.layer(rrect(10, 100, 24, 14, 6), CORAL, depth=3, shadow=False)        # the scanner, beeping
    c.flat(rrect(14, 104, 16, 5, 2), PAPER, op=.7)
    c.flat(star(12, 90, 6), YELLOW)
    c.stroke(path([(28, 92), (33, 86)]), YELLOW, 2.5)
    c.stroke(path([(20, 88), (20, 82)]), YELLOW, 2.5)


def draw_fridge(c, state):
    W, H = c.w - 10, c.h - 10      # 190 x 270
    c.layer(rrect(0, 0, W, H, 16), kit.lt(GREY, .5), depth=6)              # the cooler
    c.face(W / 2, 22, 8, "happy")
    c.flat(rrect(14, 46, W - 28, H - 62, 8), kit.lt(kit.SKY, .35))
    for i, y in enumerate((112, 182, 250)):                                # three shelves
        if i == 0:
            milk(c, 44, y - 2, 24, 40)
            milk(c, 78, y - 2, 24, 40)
            milk(c, 112, y - 2, 24, 40, label=PINK)
            milk(c, 146, y - 2, 24, 40)
        elif i == 1:
            for k, col in enumerate((PINK, LAVENDER, YELLOW, MINT)):
                x = 44 + k * 34
                c.layer(rrect(x - 13, y - 30, 26, 28, 6, rbl=9, rbr=9), col, depth=2, shadow=False)
                c.flat(rrect(x - 13, y - 30, 26, 7, 3), PAPER, op=.8)
        else:
            eggs(c, 50, y - 2, 46)
            eggs(c, 108, y - 2, 46)
            c.layer(rrect(144, y - 20, 30, 18, 6), kit.lt(WOOD, .3), depth=2, shadow=False)
        c.layer(rrect(14, y, W - 28, 7, 3), PAPER, depth=2, shadow=False)
    for x, y in ((30, 60), (W - 36, 70), (W - 30, 230)):                   # frost sparkles
        c.flat(star(x, y, 6, 2.4, 4), PAPER, op=.9)


def draw_sign(c, state):
    W, H = c.w - 10, c.h - 10      # 170 x 110
    for x in (44, W - 44):
        c.stroke(path([(x, 0), (x, 24)]), WOOD_DEEP, 3)
    c.layer(rrect(8, 22, W - 16, 80, 16), WOOD, depth=5)                  # the board
    c.flat(rrect(18, 32, W - 36, 60, 10), PAPER)
    apple(c, 56, 64, 20)
    banana(c, 118, 84)
    c.dots([(118 + dx, 50 + dy) for dx, dy in ((-7, 0), (0, -4), (7, 0), (-4, 7), (4, 7), (0, 14))], 4, LAVENDER_DK)


def draw_basket(c, state):
    W, H = c.w - 10, c.h - 10      # 90 x 60
    carrot(c, 32, 30, 26)
    c.stroke(arc(45, 28, 26, 190, 350), WOOD_DK, 5)                        # the handle
    c.layer(poly([(6, 26), (84, 26), (76, 58), (14, 58)]), MINT, depth=4)  # the basket
    for i in range(1, 4):
        c.stroke(path([(6 + 78 * i / 4, 28), (14 + 62 * i / 4, 56)]), PAPER, 1.8, op=.55)
    c.stroke(path([(10, 42), (80, 42)]), PAPER, 1.8, op=.55)
    c.layer(rrect(4, 22, 82, 8, 4), MINT_DK, depth=2, shadow=False)        # the rim


# ---------------------------------------------------------------- the three decorations
def draw_balloons(c, state):
    W, H = c.w - 10, c.h - 10      # 110 x 160
    tie = (W / 2, H - 8)
    for cx, cy, col in ((28, 44, PINK), (62, 30, YELLOW), (88, 54, MINT)):
        c.stroke(path([(cx, cy + 26), tie]), DARK, 1.6, op=.7)
    for cx, cy, col in ((88, 54, MINT), (28, 44, PINK), (62, 30, YELLOW)):
        c.layer(ellipse(cx, cy, 20, 24), col, depth=3)
        c.flat(poly([(cx - 4, cy + 23), (cx + 4, cy + 23), (cx, cy + 28)]), kit.dk(col, .2))
        c.flat(ellipse(cx - 7, cy - 9, 4, 7).rotate(25, cx - 7, cy - 9), PAPER, op=.7)
    c.layer(star(tie[0], tie[1], 8), YELLOW, depth=2, shadow=False)


def draw_deco_2(c, state):
    W, H = c.w - 10, c.h - 10      # 140 x 80
    c.layer(rrect(0, 0, W, H, 12), WOOD, depth=5)
    c.flat(rrect(9, 9, W - 18, H - 18, 7), PAPER)
    # a carrot lying down, with a face
    cx, cy = 62, 42
    body = poly([(28, cy - 11), (28, cy + 11), (92, cy)])
    c.layer(body, CARROT, depth=2, shadow=False)
    c.face(52, cy, 4.5, "happy")
    for dy, ang in ((-7, -30), (0, 0), (7, 30)):
        c.flat(ellipse(20, cy + dy, 9, 3.5).rotate(ang, 20, cy + dy), LEAF)
    c.flat(heart(112, 30, 10), PINK_DK)
    c.flat(star(114, 54, 5), YELLOW)


def draw_deco_3(c, state):
    W, H = c.w - 10, c.h - 10      # 90 x 110
    for x in (22, 68):                                                     # wheels
        c.layer(circle(x, H - 10, 9), DARK, depth=2, shadow=False)
        c.flat(circle(x, H - 10, 3.5), PAPER)
    flowers = ((24, 32, PINK_DK), (45, 22, LAVENDER_DK), (66, 34, YELLOW))
    for fx, fy, col in flowers:
        c.stroke(path([(fx, fy + 10), (fx, 66)]), LEAF_DK, 3)
        c.flat(ellipse(fx + 6, fy + 24, 7, 3).rotate(-30, fx + 6, fy + 24), LEAF)
        c.layer(poly([(fx - 10, fy + 4), (fx + 10, fy + 4), (fx + 8, fy - 10), (fx + 3, fy - 2), (fx, fy - 12),
                      (fx - 3, fy - 2), (fx - 8, fy - 10)]), col, depth=2, shadow=False)     # a tulip
    c.layer(rrect(6, 60, W - 12, 34, 8), WOOD, depth=5)                    # the cart box
    c.flat(rrect(14, 68, W - 28, 18, 5), kit.lt(WOOD, .25))
    c.flat(heart(W / 2, 77, 10), PINK_DK)


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "market", "超市", "supermarket",
    exits={"back": "street"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(400, 790, 100, 130),
    bg=draw_bg,
    things=[
        Thing("sign", "招牌", "sign", 300, 110, 180, 120, z=5, draw=draw_sign),
        Thing("shelf", "貨架", "shelf", 110, 340, 210, 300, z=10, draw=draw_shelf),
        Thing("fridge", "冷藏櫃", "cooler", 480, 360, 200, 280, z=10, draw=draw_fridge),
        Thing("cashier", "收銀員", "cashier", 525, 615, 150, 210, z=15, draw=draw_cashier),
        Thing("cart", "推車", "shopping cart", 90, 650, 160, 150, z=20, draw=draw_cart),
        Thing("basket", "購物籃", "basket", 95, 765, 100, 70, z=25, draw=draw_basket),
    ],
    decos=[
        Deco("deco_1", "特價氣球", "balloons", 520, 120, 120, 170, draw=draw_balloons),
        Deco("deco_2", "新招牌", "carrot sign", 300, 230, 150, 90, draw=draw_deco_2),
        Deco("deco_3", "小花車", "flower cart", 400, 600, 100, 120, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
