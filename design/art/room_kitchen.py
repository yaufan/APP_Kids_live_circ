"""廚房 the kitchen: fridge, round dining table (the app lays bowls on it), sink, stove, upper cupboard,
window and a little chair. Same structure as room_living.py; boxes in scene pixels (600 x 800).

The avatar (drawn by the app at z 50 in a 308 x 400 rect on the stand box) covers about x 138-376
at head height (y 337-566) and x 161-350 lower down, so the sink stays left of x 140 and the stove,
fridge and chair right of x 376; the cupboard, picture and window sit on the wall above the head.
"""
import math

import kit
from kit import (CORAL, CREAM, GREY, LAVENDER, LEAF, LEAF_DK, MINT, PAPER, PEACH, PEACH_DK, PINK, PINK_DK,
                 SKY_TOKEN, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, Shape, circle, ellipse, heart, path, poly, rect,
                 rrect, star)
import scene
from scene import Box, Deco, Thing

FLOOR_Y = 560
WALL_K = kit.lt(MINT, .62)          # pale mint wall
BLUE = "#9DC4EC"                    # water (a real colour, not the sky token)

# the window box, so the background's sky patch sits exactly behind the glass
WIN_CX, WIN_CY, WIN_W, WIN_H = 486, 185, 180, 150


# ---------------------------------------------------------------- background
def draw_bg(c):
    c.flat(rect(0, 0, 600, FLOOR_Y + 20), WALL_K)
    # the sky behind the window glass (the window's own glass is #SKY too; the app recolours both)
    gx, gy = WIN_CX - WIN_W / 2 + 14, WIN_CY - WIN_H / 2 + 24
    c.flat(rrect(gx - 4, gy - 4, WIN_W - 10 - 28 + 8, WIN_H - 10 - 50 + 8, 8), SKY_TOKEN)
    # the tiled splash-back: square paper tiles glued on the lower wall
    tiles = Shape()
    y0 = FLOOR_Y - 14 - 6 * 40
    for row in range(6):
        for col in range(15):
            tiles = tiles + rrect(col * 40 + 2, y0 + row * 40 + 2, 36, 36, 4)
    c.flat(tiles, PAPER, op=.85)
    # the floor: cream and mint check tiles
    c.flat(rect(0, FLOOR_Y, 600, 800 - FLOOR_Y), CREAM)
    checks = Shape()
    for row in range(4):
        for col in range(10):
            if (row + col) % 2 == 0:
                checks = checks + rect(col * 60, FLOOR_Y + row * 60, 60, 60)
    c.flat(checks, kit.lt(MINT, .35))
    lines = Shape()
    for i in range(1, 10):
        lines = lines + rect(i * 60 - 1, FLOOR_Y, 2, 240)
    for i in range(1, 4):
        lines = lines + rect(0, FLOOR_Y + i * 60 - 1, 600, 2)
    c.flat(lines, kit.dk(CREAM, .10), op=.7)
    # the wall standing up on the floor, and the skirting board
    c.flat(rect(0, FLOOR_Y, 600, 16), kit.SHADOW, op=.12)
    c.flat(rect(0, FLOOR_Y + 16, 600, 10), kit.SHADOW, op=.05)
    c.layer(rrect(0, FLOOR_Y - 14, 600, 18, 3), WOOD_DK, depth=4, shadow=False)
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_fridge(c, state):
    W, H = c.w - 10, c.h - 10      # 110 x 290
    for x in (12, W - 28):                                                 # feet
        c.layer(rrect(x, H - 12, 16, 12, 4), kit.dk(LAVENDER, .4), depth=2, shadow=False)
    c.layer(rrect(0, 0, W, H - 8, 16), LAVENDER, depth=6)                  # the body
    c.stroke(path([(8, 92), (W - 8, 92)]), kit.dk(LAVENDER, .28), 3)      # freezer / fridge split
    for y, h in ((30, 44), (108, 72)):                                     # handles
        c.layer(rrect(W - 22, y, 9, h, 4.5), PAPER, depth=2, shadow=False)
    # magnets on the freezer door, a child's drawing on the big door
    c.layer(heart(28, 44, 22), PINK_DK, depth=2, shadow=False)
    c.layer(star(62, 50, 12), YELLOW, depth=2, shadow=False)
    c.layer(rrect(16, 110, 50, 44, 3), PAPER, depth=2, shadow=False)
    c.flat(circle(54, 124, 6.5), YELLOW)
    c.flat(rrect(20, 141, 42, 9, 2), LEAF)
    c.flat(rrect(31, 128, 10, 15, 2), CORAL)
    c.flat(poly([(27, 130), (36, 120), (45, 130)]), CORAL)
    c.flat(circle(41, 109, 4), CORAL)                                      # the magnet holding it
    c.face(W / 2 - 5, 208, 10, "happy")


def draw_table(c, state):
    W, H = c.w - 10, c.h - 10      # 270 x 170
    for x in (44, W - 60):                                                 # legs
        c.layer(rrect(x, 96, 16, H - 96, 6), WOOD_DK, depth=3)
    c.layer(rrect(52, 128, W - 104, 9, 4), WOOD_DK, depth=2, shadow=False)  # the bar
    c.layer(ellipse(W / 2, 80, W / 2, 60), WOOD_DK, depth=5)                # the thick apron
    c.layer(ellipse(W / 2, 70, W / 2, 60), WOOD, depth=4, shadow=False)     # the top, seen from above
    c.flat(ellipse(W / 2, 66, W / 2 - 20, 46), kit.lt(WOOD, .2), op=.85)


def draw_sink(c, state):
    W, H = c.w - 10, c.h - 10      # 130 x 240
    top = 80
    c.layer(rrect(4, top + 14, W - 8, H - top - 14, 10), MINT, depth=6)   # the cabinet
    dw = W / 2 - 16
    for i, x in enumerate((12, W / 2 + 4)):                                # two doors
        c.flat(rrect(x, top + 40, dw, H - top - 66, 6), kit.lt(MINT, .2))
        kx = x + dw - 10 if i == 0 else x + 10
        c.flat(circle(kx, top + 40 + (H - top - 66) / 2, 4), WOOD_DEEP)
    c.face(12 + dw / 2 - 3, top + 96, 7.5, "happy")
    c.layer(rrect(W - 36, top + 22, 22, 42, 5), PINK, depth=3)             # a towel over the door
    c.flat(rrect(W - 36, top + 42, 22, 5, 2), PAPER, op=.8)
    c.layer(rrect(0, top, W, 18, 6), CREAM, depth=5)                       # the counter top
    c.flat(rrect(14, top + 3, 74, 12, 5), kit.lt(GREY, .35))               # the basin
    c.flat(rrect(20, top + 6, 62, 6, 3), kit.lt(BLUE, .45))
    # the tap: a pipe rising at the right and curving over the basin
    pipe = path([(104, top + 2), (104, 44), (102, 36), (96, 31), (88, 30), (80, 33), (75, 40), (74, 50)])
    c.stroke(pipe.move(2.5, 3.5), kit.dk(GREY, .32), 9)
    c.stroke(pipe, GREY, 9)
    c.flat(ellipse(104, top + 2, 14, 5), kit.dk(GREY, .15))
    c.layer(rrect(108, 44, 18, 7, 3.5), PINK_DK, depth=2, shadow=False)    # the lever
    c.flat(poly([(74, 56), (70, 64), (78, 64)]) + circle(74, 65, 4.2), BLUE)   # a drop


def draw_stove(c, state):
    W, H = c.w - 10, c.h - 10      # 90 x 230
    top = 60
    for x in (8, W - 24):                                                  # feet
        c.layer(rrect(x, H - 10, 16, 10, 4), kit.dk(PEACH, .4), depth=2, shadow=False)
    c.layer(rrect(0, top + 8, W, H - top - 16, 10), PEACH, depth=6)        # the oven body
    for i in range(3):                                                     # knobs
        kx = 20 + i * 25
        c.flat(circle(kx, top + 24, 5.5), WOOD_DEEP)
        c.stroke(path([(kx, top + 20), (kx, top + 24)]), PAPER, 2)
    c.layer(rrect(10, top + 36, W - 20, 6, 3), PAPER, depth=2, shadow=False)   # the oven handle
    c.flat(rrect(12, top + 46, W - 24, 46, 8), kit.dk(PEACH, .55))         # the oven window
    c.flat(rrect(18, top + 52, 22, 7, 3.5), PAPER, op=.35)
    c.face(W / 2, top + 126, 7.5, "happy")
    c.layer(rrect(0, top - 6, W, 16, 5), kit.lt(GREY, .4), depth=4)        # the hob
    for bx in (24, W - 24):                                                # two burners
        c.flat(ellipse(bx, top + 1, 17, 5.5), kit.dk(GREY, .45), op=.9)
        c.flat(ellipse(bx, top + 1, 10, 3), kit.lt(GREY, .2), op=.8)
    # a pot on the right burner, with puffs of steam
    px = W - 24
    c.layer(rrect(px - 21, top - 38, 42, 36, 7, rtl=4, rtr=4), CORAL, depth=4)
    for hx in (px - 28, px + 19):
        c.layer(rrect(hx, top - 28, 9, 7, 3.5), kit.dk(CORAL, .2), depth=2, shadow=False)
    c.layer(ellipse(px, top - 38, 25, 7), kit.dk(CORAL, .1), depth=3)      # the lid
    c.flat(circle(px, top - 45, 4.5), WOOD_DEEP)
    c.flat(circle(px - 9, top - 60, 5) + circle(px - 3, top - 64, 6) + circle(px + 4, top - 59, 4.5), PAPER, op=.85)
    c.flat(circle(px + 6, top - 78, 4) + circle(px + 11, top - 74, 3.5), PAPER, op=.7)


def draw_cupboard(c, state):
    W, H = c.w - 10, c.h - 10      # 230 x 110
    c.layer(rrect(0, 0, W, H, 10), WOOD, depth=6)                          # the case
    dw = W / 2 - 14
    for i, x in enumerate((9, W / 2 + 5)):                                 # two little doors
        c.layer(rrect(x, 9, dw, H - 18, 7), kit.lt(WOOD, .3), depth=2, shadow=False)
        kx = x + dw - 12 if i == 0 else x + 12
        c.flat(circle(kx, H / 2, 4.5), WOOD_DEEP)
    c.flat(heart(9 + dw / 2 - 4, H / 2 + 2, 22), PINK)                     # printed on the left door
    c.face(W / 2 + 5 + dw / 2 + 4, H / 2, 8.5, "happy")                    # the right door smiles


def draw_window(c, state):
    W, H = c.w - 10, c.h - 10      # 170 x 140
    c.layer(rrect(0, 10, W, H - 24, 12), WOOD, depth=5)                    # frame
    c.flat(rrect(14, 24, W - 28, H - 50, 6), SKY_TOKEN)                    # glass (recoloured by the app)
    c.flat(ellipse(56, 74, 26, 10) + circle(48, 68, 12) + circle(64, 66, 14), PAPER, op=.92)
    c.layer(rrect(W / 2 - 4, 24, 8, H - 50, 3), kit.lt(WOOD, .12), depth=2, shadow=False)
    c.layer(rrect(14, 66, W - 28, 8, 3), kit.lt(WOOD, .12), depth=2, shadow=False)
    # a tiny curtain: a scalloped valance along the top
    val = rrect(4, 2, W - 8, 20, 6)
    for i in range(7):
        val = val + circle(4 + (W - 8) * (i + .5) / 7, 22, (W - 8) / 14)
    c.layer(val, YELLOW, depth=4)
    c.dots([(4 + (W - 8) * (i + .5) / 7, 14) for i in range(7)], 2.6, PAPER)
    c.layer(rrect(0, H - 14, W, 14, 5), WOOD_DK, depth=5)                  # the sill
    c.layer(rrect(W - 44, H - 30, 22, 18, 5), PEACH_DK, depth=3, shadow=False)   # a little herb pot
    c.layer(circle(W - 33, H - 36, 9) + circle(W - 41, H - 31, 6) + circle(W - 25, H - 31, 6), LEAF, depth=2, shadow=False)


def draw_chair(c, state):
    W, H = c.w - 10, c.h - 10      # 70 x 140
    c.layer(rrect(6, 0, W - 12, 64, 14), CORAL, depth=5)                   # the back
    c.flat(heart(W / 2, 32, 20), kit.lt(CORAL, .4))
    for x in (4, W - 14):                                                  # legs
        c.layer(rrect(x, 70, 10, H - 70, 4), WOOD_DK, depth=2)
    c.layer(rrect(8, 104, W - 16, 6, 3), WOOD_DK, depth=2, shadow=False)
    c.layer(rrect(0, 60, W, 18, 7), kit.lt(CORAL, .12), depth=5)           # the seat


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    W, H = c.w - 10, c.h - 10      # 80 x 50: a fruit basket (sits on the fridge)
    c.stroke(kit.arc(W / 2, 32, 28, 180, 360), WOOD_DK, 4)                 # the handle
    c.layer(circle(22, 26, 12), PEACH_DK, depth=3, shadow=False)           # an orange
    c.flat(ellipse(22, 14, 5, 2.5).rotate(-30, 22, 14), LEAF)
    c.layer(circle(44, 22, 13), CORAL, depth=3, shadow=False)              # an apple
    c.stroke(path([(44, 10), (46, 4)]), WOOD_DEEP, 2.5)
    c.flat(ellipse(50, 8, 6, 3).rotate(-25, 50, 8), LEAF_DK)
    c.layer(ellipse(64, 28, 10, 12), LEAF, depth=3, shadow=False)          # a pear
    c.layer(poly([(4, 30), (W - 4, 30), (W - 12, H), (12, H)]), WOOD_DK, depth=4)   # the basket
    for i in range(1, 4):
        c.stroke(path([(8 + i * 2, 36 + i * 4), (W - 8 - i * 2, 36 + i * 4)]), kit.dk(WOOD_DK, .2), 1.6, op=.7)
    c.layer(rrect(0, 26, W, 10, 5), WOOD, depth=3)                         # the rim


def draw_deco_2(c, state):
    W, H = c.w - 10, c.h - 10      # 80 x 70: a little picture of a bowl of rice
    c.layer(rrect(0, 0, W, H, 8), WOOD, depth=5)
    c.flat(rrect(8, 8, W - 16, H - 16, 4), CREAM)
    c.flat(circle(34, 34, 7) + circle(42, 30, 9) + circle(51, 34, 7) + rrect(30, 32, 26, 8, 3), PAPER)   # rice
    c.layer(rrect(24, 38, 36, 18, 8, rtl=2, rtr=2), PINK_DK, depth=2, shadow=False)   # the bowl
    c.flat(rrect(32, 56, 20, 4, 2), kit.dk(PINK_DK, .2))
    c.stroke(path([(50, 42), (66, 16)]), WOOD_DEEP, 2.5)                   # chopsticks
    c.stroke(path([(56, 42), (70, 18)]), WOOD_DEEP, 2.5)
    c.flat(circle(24, 20, 2.5) + circle(27, 14, 2) + circle(23, 9, 1.6), GREY, op=.8)   # steam


def draw_deco_3(c, state):
    # 290 x 174: a new tablecloth. Decorations are drawn behind everything, so what shows is the
    # scalloped border peeking out round the table top and the hem hanging below its edge.
    W, H = c.w - 10, c.h - 10
    cx, cy, rx, ry = 150, 66, 144, 68
    cloth = ellipse(cx, cy, rx, ry) + rrect(cx - rx, cy, 2 * rx, 94, 30, rtl=0, rtr=0)
    for i in range(14):                                                    # scallops round the top edge
        a = math.pi + math.pi * (i + .5) / 14
        cloth = cloth + circle(cx + rx * math.cos(a), cy + ry * math.sin(a), 7)
    for i in range(13):                                                    # scallops along the hem
        cloth = cloth + circle(cx - rx + 2 * rx * (i + .5) / 13, cy + 94, 7)
    c.layer(cloth, PINK, depth=3)
    band = Shape()
    for i in range(13):
        band = band + circle(cx - rx + 2 * rx * (i + .5) / 13, cy + 84, 3)
    c.flat(band, PAPER)
    c.dots([(cx - rx + 14 + k * 22, cy + 70 - (6 if k % 2 else 0)) for k in range(13)], 2.6, kit.lt(PINK, .5))


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "kitchen", "廚房", "kitchen",
    exits={"left": "balcony", "right": "living"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(80, 720, 120, 160),
    bg=draw_bg,
    things=[
        Thing("cupboard", "櫥櫃", "cupboard", 150, 185, 240, 120, z=5, draw=draw_cupboard),
        Thing("window", "窗戶", "window", WIN_CX, WIN_CY, WIN_W, WIN_H, z=5, draw=draw_window),
        Thing("stove", "瓦斯爐", "stove", 426, 470, 100, 240, z=9, draw=draw_stove),
        Thing("sink", "洗碗槽", "sink", 72, 470, 140, 250, z=10, draw=draw_sink),
        Thing("fridge", "冰箱", "fridge", 536, 450, 120, 300, z=10, draw=draw_fridge),
        Thing("chair", "椅子", "chair", 515, 625, 80, 150, z=19, draw=draw_chair),
        Thing("table", "餐桌", "dining table", 410, 700, 280, 180, z=20, draw=draw_table),
    ],
    decos=[
        Deco("deco_1", "水果籃", "fruit basket", 536, 288, 90, 60, draw=draw_deco_1),
        Deco("deco_2", "牆上的小畫", "little picture", 328, 195, 90, 80, draw=draw_deco_2),
        Deco("deco_3", "新桌巾", "new tablecloth", 405, 708, 300, 184, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
