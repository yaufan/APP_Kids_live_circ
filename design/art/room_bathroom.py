"""廁所 the bathroom: a wall of pale blue tiles, a checked floor, the sink with its round mirror on the
left, the bathtub against the back wall on the right with the toilet in front of it.

Scene pixels are 600 x 800; the wall is the top 560 px and the floor the bottom 240 px. The avatar's
stand box (204 x 400, feet at y 688) is kept clear: sink, mirror, cup and window on its left, tub,
toilet and towel on its right. Each `draw_*(c, state)` paints into a kit.Ctx the size of the thing's
box and leaves ~10 px free on the right and bottom for the paper shadow.
"""
import math

import kit
from kit import (CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, MINT, MINT_DK, PAPER, PEACH, PEACH_DK, PINK,
                 PINK_DK, SKY, SKY_TOKEN, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, circle, ellipse, heart, path, poly,
                 rect, ring, rrect, star)
import scene
from scene import Box, Deco, Thing

FLOOR_Y = 560
TILE = kit.lt(SKY, .45)            # a pale blue tile
GROUT = kit.lt(SKY, .15)           # the lines between the tiles (a little darker than the tiles)
FLOOR_A = kit.lt(MINT, .5)         # the floor's two check colours
FLOOR_B = CREAM
PORCELAIN = PAPER
WATER = kit.lt(SKY, .2)


def dome(cx, cy, rx, ry, steps=24):
    """The top half of an ellipse with a flat base."""
    pts = [(cx + rx * math.cos(math.pi * i / steps), cy - ry * math.sin(math.pi * i / steps)) for i in range(steps + 1)]
    return poly(pts)


def duck(c, x, y, s, col=YELLOW):
    """A little rubber duck facing right, about 2 s wide, its feet at y."""
    c.layer(ellipse(x, y - s * .45, s, s * .5), col, depth=3)                        # body
    c.layer(circle(x + s * .55, y - s * 1.05, s * .42), col, depth=3, shadow=False)  # head
    c.flat(poly([(x + s * .9, y - s * 1.1), (x + s * 1.3, y - s * 1.0), (x + s * .9, y - s * .9)]), PEACH_DK)  # beak
    c.flat(circle(x + s * .66, y - s * 1.15, s * .08), DARK)                          # eye
    c.flat(ellipse(x - s * .25, y - s * .55, s * .35, s * .18), kit.lt(col, .4), op=.8)   # the wing


# ---------------------------------------------------------------- background
def draw_bg(c):
    # the wall: pale blue tiles with soft grout lines (one layer of paper, printed squares)
    c.flat(rect(0, 0, 600, FLOOR_Y + 20), GROUT)
    size = 60
    for row in range(10):
        for col in range(10):
            x, y = col * size + 3, row * size + 3
            if y < FLOOR_Y - 20:
                c.flat(rrect(x, y, size - 6, min(size - 6, FLOOR_Y - 20 - y), 6), TILE)
    # the sky behind the little window (its glass is also #SKY; the app recolours both)
    c.flat(rrect(30, 65, 100, 90, 8), SKY_TOKEN)
    # the floor: a checked tile floor
    c.flat(rect(0, FLOOR_Y, 600, 800 - FLOOR_Y), FLOOR_A)
    for row in range(4):
        for col in range(10):
            if (row + col) % 2:
                c.flat(rect(col * 60, FLOOR_Y + row * 60, 60, 60), FLOOR_B)
    for i in range(1, 10):
        c.stroke(path([(i * 60, FLOOR_Y + 2), (i * 60, 800)]), kit.dk(FLOOR_A, .10), 2)
    for i in range(1, 4):
        c.stroke(path([(0, FLOOR_Y + i * 60), (600, FLOOR_Y + i * 60)]), kit.dk(FLOOR_A, .10), 2)
    # the wall standing up on the floor: a dark band where they meet, and a mint skirting board
    c.flat(rect(0, FLOOR_Y, 600, 16), kit.SHADOW, op=.12)
    c.flat(rect(0, FLOOR_Y + 16, 600, 10), kit.SHADOW, op=.05)
    c.layer(rrect(0, FLOOR_Y - 14, 600, 18, 3), MINT_DK, depth=4, shadow=False)
    # the page's side edges
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_window(c, state):
    W, H = c.w - 10, c.h - 10      # 110 x 100
    c.layer(rrect(0, 0, W, H - 8, 12), WOOD, depth=5)                      # frame
    c.flat(rrect(12, 12, W - 24, H - 32, 6), SKY_TOKEN)                    # glass (recoloured by the app)
    c.flat(ellipse(40, 54, 16, 7) + circle(34, 50, 8) + circle(46, 48, 9), PAPER, op=.92)   # a cloud
    c.layer(rrect(W / 2 - 4, 12, 8, H - 32, 3), kit.lt(WOOD, .12), depth=2, shadow=False)    # cross bars
    c.layer(rrect(12, H / 2 - 12, W - 24, 8, 3), kit.lt(WOOD, .12), depth=2, shadow=False)
    c.layer(rrect(-0, H - 16, W, 14, 5), WOOD_DK, depth=5)                 # the sill


def draw_mirror(c, state):
    W, H = c.w - 10, c.h - 10      # 110 x 110
    r = min(W, H) / 2
    c.layer(circle(r, r + 4, r), WOOD, depth=5)                            # the round wooden frame
    c.flat(circle(r, r + 4, r - 12), kit.lt(SKY, .3))                      # the glass
    c.stroke(path([(r - 26, r - 10), (r - 8, r - 28)]), PAPER, 5, op=.9)   # glints
    c.stroke(path([(r - 16, r + 4), (r + 2, r - 14)]), PAPER, 3, op=.8)
    c.layer(heart(r, 8, 18), PINK, depth=3, shadow=False)                  # a little bow on top
    c.flat(circle(r, 10, 4), PINK_DK)


def draw_sink(c, state):
    W, H = c.w - 10, c.h - 10      # 140 x 180
    # the tap: a bent pipe and a round knob on each side, standing at the back of the basin
    c.stroke(path([(W / 2, 40), (W / 2, 14), (W / 2 + 18, 14), (W / 2 + 18, 26)]), GREY, 8)
    c.stroke(path([(W / 2, 40), (W / 2, 14), (W / 2 + 18, 14), (W / 2 + 18, 26)]), kit.lt(GREY, .5), 3)
    for x, col in ((W / 2 - 30, SKY), (W / 2 + 30, CORAL)):
        c.layer(circle(x, 34, 8), col, depth=2, shadow=False)
    # the pedestal, then the basin on top of it
    c.layer(poly([(W / 2 - 28, 60), (W / 2 + 28, 60), (W / 2 + 34, H), (W / 2 - 34, H)]), PORCELAIN, depth=5)
    c.face(W / 2, 112, 7, "happy")
    c.layer(rrect(10, 44, W - 20, 36, 14, rbl=26, rbr=26), PORCELAIN, depth=5)   # the bowl
    c.layer(ellipse(W / 2, 44, W / 2 - 10, 11), kit.lt(SKY, .2), depth=2, shadow=False)   # the rim's inside
    c.flat(ellipse(W / 2, 46, W / 2 - 22, 6), WATER, op=.8)               # a little water
    c.flat(circle(W / 2 - 14, 46, 3) + circle(W / 2 - 4, 48, 2), PAPER, op=.9)


def draw_toothbrush_cup(c, state):
    W, H = c.w - 10, c.h - 10      # 34 x 50
    # two toothbrushes: a pink one and a mint one, with white bristles
    for x, col, lean in ((10, PINK_DK, -4), (24, MINT_DK, 4)):
        c.stroke(path([(x, 42), (x + lean, 6)]), col, 5)
        c.flat(rrect(x + lean - 4.5, 0, 9, 10, 3), PAPER)
        c.flat(rrect(x + lean - 3, 2, 6, 6, 1), col, op=.35)
    c.layer(rrect(2, 22, W - 4, H - 22, 6, rtl=3, rtr=3), YELLOW, depth=3)   # the cup
    c.layer(rrect(0, 20, W, 8, 4), kit.dk(YELLOW, .1), depth=2, shadow=False)
    c.face(W / 2, 40, 3.4, "smile")


def draw_bathtub(c, state):
    W, H = c.w - 10, c.h - 10      # 236 x 160
    for x in (24, W - 44):                                                 # the little feet
        c.layer(ellipse(x + 10, H - 6, 14, 7), WOOD_DK, depth=2, shadow=False)
    # the tub: a deep rounded dish, a flat rim of paper on top
    tub = rrect(6, 50, W - 12, H - 62, 16, rbl=44, rbr=44)
    c.layer(tub, PORCELAIN, depth=6)
    c.flat(rrect(18, 62, W - 36, 26, 10), kit.lt(SKY, .4), op=.7)         # a soft blue band
    c.face(W / 2, 104, 9, "happy")
    c.layer(rrect(0, 40, W, 22, 11), kit.lt(SKY, .2), depth=4)             # the rim
    c.flat(rrect(14, 44, W - 28, 12, 6), WATER)                            # the water inside
    # bubbles rising from the water
    for x, y, r in ((40, 36, 12), (62, 24, 9), (92, 32, 14), (116, 18, 8), (140, 30, 11), (176, 22, 13), (200, 36, 9)):
        c.layer(circle(x, y, r), PAPER, depth=2, shadow=False, op=.95)
        c.flat(circle(x - r * .3, y - r * .3, r * .3), kit.lt(SKY, .6))
    # the tap at the right end
    c.stroke(path([(W - 34, 44), (W - 34, 14), (W - 54, 14), (W - 54, 24)]), GREY, 8)
    c.stroke(path([(W - 34, 44), (W - 34, 14), (W - 54, 14), (W - 54, 24)]), kit.lt(GREY, .5), 3)
    c.layer(circle(W - 18, 26, 7), CORAL, depth=2, shadow=False)


def draw_toilet(c, state):
    W, H = c.w - 10, c.h - 10      # 110 x 140
    open_ = state == "open"
    LID = kit.lt(SKY, .1)
    # the base, then the bowl on it (the tank sits on the back of the bowl)
    c.layer(poly([(30, 108), (W - 30, 108), (W - 34, H), (34, H)]), PORCELAIN, depth=5)
    c.layer(rrect(0, 68, W, 46, 20, rbl=30, rbr=30), PORCELAIN, depth=5)   # the bowl
    c.flat(rrect(8, 94, W - 16, 9, 4.5), kit.lt(SKY, .4), op=.7)          # a soft blue band
    # the tank at the back, with the friendly face
    c.layer(rrect(W - 46, 0, 46, 74, 10), PORCELAIN, depth=5)
    c.layer(rrect(W - 50, 0, 50, 12, 6), LID, depth=3, shadow=False)      # the tank's lid
    c.flat(circle(W - 10, 6, 3.5), CORAL)                                  # the flush button
    c.face(W - 23, 40, 6.5, "open" if open_ else "happy")
    front = W - 52                                                         # the seat part of the bowl
    if open_:
        c.layer(rrect(W - 66, 2, 20, 70, 9), PORCELAIN, depth=4)          # the lid stands up against the tank
        c.flat(rrect(W - 61, 8, 10, 58, 5), LID)
        c.layer(ellipse(front / 2 + 2, 70, front / 2, 11), LID, depth=3, shadow=False)   # the seat ring
        c.flat(ellipse(front / 2 + 2, 71, front / 2 - 11, 5.5), SKY)                      # the water
        c.flat(circle(front / 2 - 8, 70, 2) + circle(front / 2 + 5, 72, 1.6), PAPER, op=.9)
    else:
        c.layer(rrect(2, 54, front, 20, 10), LID, depth=4)                 # the lid lying down
        c.flat(rrect(10, 59, front - 16, 5, 2.5), PAPER, op=.7)


def draw_towel(c, state):
    W, H = c.w - 10, c.h - 10      # 60 x 110
    c.layer(rrect(W / 2 - 10, 0, 20, 8, 4), WOOD_DK, depth=2)              # the hook's plate
    c.layer(circle(W / 2, 14, 5), WOOD_DEEP, depth=2, shadow=False)       # the hook
    # the towel hanging folded over the hook, with two stripes and a fringe
    towel = poly([(6, 12), (W - 6, 12), (W - 2, 40), (W - 4, H - 8), (4, H - 8), (2, 40)])
    c.layer(towel, PEACH, depth=4)
    c.flat(rrect(5, 46, W - 10, 8, 3), PINK_DK, op=.8)
    c.flat(rrect(5, 60, W - 10, 8, 3), PINK_DK, op=.8)
    c.dots([(10 + i * 8, H - 6) for i in range(6)], 2.2, PEACH_DK)
    c.face(W / 2, 84, 4, "smile")


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    W, H = c.w - 10, c.h - 10      # 190 x 70
    # three rubber-duck stickers in a row on the tiles
    for i, (s, col) in enumerate(((20, YELLOW), (24, YELLOW), (18, kit.lt(YELLOW, .2)))):
        duck(c, 30 + i * 66, H - 6, s, col)
    c.flat(heart(W - 14, 16, 10), PINK_DK)


def draw_deco_2(c, state):
    W, H = c.w - 10, c.h - 10      # 150 x 90
    c.layer(rrect(0, 6, W, 8, 4), WOOD_DK, depth=3)                        # the towel rail
    for x, col in ((8, PINK), (54, MINT), (100, LAVENDER)):               # three new towels
        c.layer(rrect(x, 10, 42, H - 14, 6), col, depth=4)
        c.flat(rrect(x + 4, 34, 34, 6, 3), PAPER, op=.8)
        c.flat(rrect(x + 4, 46, 34, 6, 3), PAPER, op=.8)
        c.dots([(x + 7 + k * 7, H - 4) for k in range(5)], 2, kit.dk(col, .25))
    for x in (4, W - 4):                                                   # the rail's brackets
        c.layer(circle(x, 10, 6), WOOD_DEEP, depth=2, shadow=False)


def draw_deco_3(c, state):
    W, H = c.w - 10, c.h - 10      # 140 x 200
    c.layer(rrect(0, 4, W, 8, 4), GREY, depth=3)                           # the curtain rod
    # a shower curtain gathered to one side: a wavy panel with rings along the rod
    pts = [(10, 14), (W - 10, 14), (W - 2, 60), (W - 8, 110), (W, 160), (W - 6, H - 6)]
    pts += [(W - 6 - i * 10, H - 6 + (6 if i % 2 else 0)) for i in range(1, int((W - 24) / 10))]
    pts += [(10, H - 6), (6, 160), (12, 110), (4, 60)]
    c.layer(poly(pts), MINT, depth=4)
    for k in range(4):                                                     # soft folds
        fx = 30 + k * 28
        c.stroke(path([(fx, 20), (fx + 4, H - 14)]), kit.dk(MINT, .10), 4, op=.6)
    for i in range(6):                                                     # little fish printed on it
        x, y = 26 + (i % 3) * 40, 60 + (i // 3) * 70 + (i % 2) * 14
        c.flat(ellipse(x, y, 11, 7), PAPER, op=.9)
        c.flat(poly([(x + 9, y), (x + 17, y - 7), (x + 17, y + 7)]), PAPER, op=.9)
        c.flat(circle(x - 4, y - 1.5, 1.5), MINT_DK)
    for i in range(7):                                                     # the rings
        c.flat(ring(14 + i * (W - 28) / 6, 8, 6, 3.5), WOOD_DEEP, rule="evenodd")


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "bathroom", "廁所", "bathroom",
    exits={"left": "bedroom", "down": "living"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(408, 688, 120, 160),
    bg=draw_bg,
    things=[
        Thing("window", "窗戶", "window", 80, 110, 120, 110, z=5, draw=draw_window),
        Thing("mirror", "鏡子", "mirror", 80, 330, 120, 120, z=6, draw=draw_mirror),
        Thing("towel", "毛巾", "towel", 560, 390, 70, 120, z=8, draw=draw_towel),
        Thing("bathtub", "浴缸", "bathtub", 473, 590, 246, 170, z=15, draw=draw_bathtub),
        Thing("sink", "洗手台", "sink", 85, 560, 150, 190, z=18, draw=draw_sink),
        Thing("toothbrush_cup", "牙刷杯", "toothbrush cup", 128, 492, 44, 60, z=19, draw=draw_toothbrush_cup),
        Thing("toilet", "馬桶", "toilet", 530, 715, 120, 150, z=25, draw=draw_toilet, states=("closed", "open")),
    ],
    decos=[
        Deco("deco_1", "小鴨貼紙", "duck stickers", 300, 95, 200, 80, draw=draw_deco_1),
        Deco("deco_2", "新毛巾", "new towels", 250, 220, 160, 100, draw=draw_deco_2),
        Deco("deco_3", "浴簾", "shower curtain", 430, 400, 150, 210, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
