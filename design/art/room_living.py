"""客廳 the living room: the template every other room copies (room_<x>.py with SCENE = scene.Scene).

Scene pixels are 600 x 800; the wall is the top 560 px and the floor the bottom 240 px, so the
avatar (stand box 204 x 400, feet at y 688) stands in front of the furniture. Each `draw_*(c, state)`
paints into a kit.Ctx the size of the thing's box and leaves ~10 px free on the right and bottom for
the paper shadow. Furniture gets a small face (sofa, toy box, TV, lamp, plant pot).
"""
import math

import kit
from kit import (BLUSH, CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH,
                 PEACH_DK, PINK, PINK_DK, SKY_TOKEN, WALL, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, circle, ellipse, heart,
                 path, poly, rect, rrect, star)
import scene
from scene import Box, Deco, Thing

FLOOR_Y = 560


# ---------------------------------------------------------------- background
def draw_bg(c):
    # the wall: cream paper with faint polka dots
    c.flat(rect(0, 0, 600, FLOOR_Y + 20), WALL)
    pts = []
    for row in range(12):
        y = 28 + row * 46
        for col in range(14):
            x = 24 + col * 46 + (23 if row % 2 else 0)
            if x < 600 and y < FLOOR_Y - 20:
                pts.append((x, y))
    c.dots(pts, 4, kit.dk(WALL, .09))
    # the sky behind the window (the window's glass is also #SKY; the app recolours both)
    c.flat(rrect(50, 170, 200, 160, 10), SKY_TOKEN)
    # the floor: a sheet of warm wood lying flat, its top edge a paper edge, with plank lines
    c.flat(rect(0, FLOOR_Y, 600, 800 - FLOOR_Y), WOOD)
    for i in range(1, 8):
        x = i * 75 + 10
        c.stroke(path([(x, FLOOR_Y + 4), (x, 800)]), kit.dk(WOOD, .14), 3)
    for i in range(3):
        y = FLOOR_Y + 70 + i * 70
        c.stroke(path([(0, y), (600, y)]), kit.dk(WOOD, .10), 2.5)
    # the wall standing up on the floor: a dark band where they meet, and the skirting board
    c.flat(rect(0, FLOOR_Y, 600, 16), kit.SHADOW, op=.12)
    c.flat(rect(0, FLOOR_Y + 16, 600, 10), kit.SHADOW, op=.05)
    c.layer(rrect(0, FLOOR_Y - 14, 600, 18, 3), WOOD_DK, depth=4, shadow=False)
    # the page's side edges (the book's gutter and outer edge), very soft
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_window(c, state):
    W, H = c.w - 10, c.h - 12      # 210 x 188
    c.layer(rrect(0, 4, W, 10, 5), WOOD_DEEP, depth=3)                     # curtain rod
    c.layer(rrect(6, 18, W - 12, 150, 14), WOOD, depth=5)                  # frame
    c.flat(rrect(20, 32, W - 40, 122, 6), SKY_TOKEN)                       # glass (recoloured by the app)
    cl = ellipse(60, 110, 34, 14) + circle(50, 102, 16) + circle(72, 100, 18)
    c.flat(cl, PAPER, op=.92)                                              # a cloud
    c.layer(rrect(W / 2 - 5, 32, 10, 122, 4), kit.lt(WOOD, .12), depth=2, shadow=False)   # cross bars
    c.layer(rrect(20, 88, W - 40, 10, 4), kit.lt(WOOD, .12), depth=2, shadow=False)
    # curtains with white dots: the left one, then its mirror image about the window's middle
    left = poly([(6, 14), (62, 14), (58, 60), (50, 100), (46, 140), (52, 164), (6, 164)])
    left_dots = [(20 + j * 22, 36 + i * 26 + (8 if j else 0)) for i in range(5) for j in range(2)]
    for flip in (False, True):
        sh = left.flip(W / 2) if flip else left
        c.layer(sh, PINK, depth=4)
        c.dots([((W - x) if flip else x, y) for x, y in left_dots], 3.2, PAPER)
        tx = (W - 50) if flip else 50
        c.layer(ellipse(tx, 118, 12, 7), PINK_DK, depth=2, shadow=False)   # the tie-back
    c.layer(rrect(0, 164, W, 16, 6), WOOD_DK, depth=5)                     # the sill


def draw_sofa(c, state):
    W = c.w - 10      # 250 x 160
    c.layer(rrect(14, 0, W - 28, 92, 30), MINT, depth=5)                   # back
    c.face(W / 2, 40, 11, "happy")
    c.layer(rrect(30, 80, W - 60, 46, 16), kit.lt(MINT, .12), depth=4)     # seat
    c.layer(rrect(0, 50, 52, 76, 24), kit.lt(MINT, .06), depth=5)          # arms
    c.layer(rrect(W - 52, 50, 52, 76, 24), kit.lt(MINT, .06), depth=5)
    c.layer(heart(72, 98, 38), PINK, depth=3)                              # cushions
    c.layer(circle(W - 72, 100, 19), YELLOW, depth=3)
    c.face(W - 72, 100, 5, "smile")
    for x in (40, W - 60):                                                 # feet
        c.layer(rrect(x, 126, 20, 22, 8), WOOD_DEEP, depth=2, shadow=False)


def draw_toybox(c, state):
    W, H = c.w - 10, c.h - 10      # 110 x 90
    if state == "full":                                                    # toys peeking out
        c.layer(circle(28, 24, 16), CORAL, depth=3)
        c.flat(rrect(12, 20, 32, 8, 4), YELLOW)
        c.layer(rrect(50, 6, 26, 26, 4), LAVENDER_DK, depth=3)
        c.flat(circle(63, 19, 5), PAPER)
        c.layer(star(92, 22, 15), YELLOW, depth=3)
    c.layer(rrect(6, 36, W - 12, H - 36, 10), PEACH, depth=5)              # the box
    c.layer(rrect(0, 24, W, 20, 8), PEACH_DK, depth=4)                     # the lid
    c.face(W / 2, 64, 9, "happy")


def draw_phone(c, state):
    W, H = c.w - 10, c.h - 10      # 70 x 52
    c.layer(poly([(8, H), (W - 8, H), (W, 26), (0, 26)]), CORAL, depth=4)   # the body
    c.flat(circle(W / 2, 40, 9), CREAM)                                     # the dial
    c.dots([(W / 2 + 5.5 * math.cos(a), 40 + 5.5 * math.sin(a)) for a in [i * math.pi / 3 for i in range(6)]], 1.6, CORAL)
    c.layer(rrect(4, 16, 12, 14, 5), kit.dk(CORAL, .15), depth=2, shadow=False)        # the cradle
    c.layer(rrect(W - 16, 16, 12, 14, 5), kit.dk(CORAL, .15), depth=2, shadow=False)
    hs = rrect(2, 4, W - 4, 14, 7) + circle(10, 11, 10) + circle(W - 10, 11, 10)      # the handset
    c.layer(hs, kit.dk(CORAL, .06), depth=4)


def draw_stairs(c, state):
    W, H = c.w - 10, c.h - 10      # 100 x 350
    steps = 6
    rise, run = (H - 40) / steps, 15
    pts = [(0, H)]
    for i in range(steps):
        pts += [(i * run, H - (i + 1) * rise), ((i + 1) * run, H - (i + 1) * rise)]
    pts += [(W, H - steps * rise), (W, H)]
    c.layer(poly(pts), WOOD, depth=6)                                      # the staircase
    for i in range(steps):                                                 # light treads, dark risers
        y = H - (i + 1) * rise
        c.flat(rect(i * run, y + 10, W - i * run, 6), kit.dk(WOOD, .12), op=.7)
        c.flat(rrect(i * run, y, W - i * run, 9, 3, rbl=0, rbr=0), kit.lt(WOOD, .3))
    # the handrail: posts on every other step, a rail along the slope, a round knob at the bottom
    rail_h = 64
    for i in (0, 2, 4):
        px = i * run + 8
        py = H - (i + 1) * rise
        c.stroke(path([(px, py), (px, py - rail_h)]), WOOD_DEEP, 5)
    c.stroke(path([(8, H - rise - rail_h), (5 * run + 8, H - 6 * rise - rail_h)]), WOOD_DEEP, 9)
    c.flat(circle(8, H - rise - rail_h, 8), CORAL)
    c.flat(circle(5, H - rise - rail_h - 3, 3), PAPER, op=.7)


def draw_lamp(c, state):
    W, H = c.w - 8, c.h - 10      # 62 x 190
    on = state != "off"
    if on:
        c.flat(ellipse(W / 2, 30, 34, 52), CREAM, op=.55)                  # the glow
    shade = poly([(12, 0), (W - 12, 0), (W, 52), (0, 52)])
    c.layer(shade, YELLOW if on else kit.tone(YELLOW, l=.9, s=.35), depth=4)
    c.face(W / 2, 28, 6.5, "happy" if on else "sleepy")
    c.layer(rrect(W / 2 - 4, 52, 8, 118, 4), WOOD_DEEP, depth=2)           # stem
    c.layer(ellipse(W / 2, H - 12, 26, 10), WOOD_DK, depth=3)              # base


def draw_rug(c, state):
    W, H = c.w - 10, c.h - 10      # 290 x 90
    c.layer(ellipse(W / 2, H / 2, W / 2, H / 2), PINK, depth=2, shadow_op=.12)
    c.flat(ellipse(W / 2, H / 2, W / 2 - 24, H / 2 - 14), kit.lt(PINK, .35))
    c.dots([(W / 2 + (W / 2 - 12) * math.cos(a), H / 2 + (H / 2 - 7) * math.sin(a))
            for a in [i * 2 * math.pi / 16 for i in range(16)]], 3.5, PAPER)
    c.flat(heart(W / 2, H / 2, 26), PINK_DK)


def draw_table(c, state):
    W, H = c.w - 10, c.h - 10      # 150 x 70
    for x in (28, W - 40):                                                 # legs
        c.layer(rrect(x, 30, 12, H - 30, 5), WOOD_DK, depth=2)
    c.layer(rrect(34, 44, W - 68, 7, 3), WOOD_DK, depth=2, shadow=False)   # the bar
    c.layer(ellipse(W / 2, 22, W / 2, 20), WOOD, depth=5)                  # top
    c.flat(ellipse(W / 2, 20, W / 2 - 16, 11), kit.lt(WOOD, .18), op=.8)


def draw_shelf(c, state):
    W, H = c.w - 10, c.h - 10      # 100 x 130
    c.layer(rrect(0, 0, W, H, 8), WOOD, depth=5)                           # the case
    for y in (10, 70):                                                     # the two compartments
        c.flat(rrect(8, y, W - 16, 50, 5), kit.dk(WOOD, .18))
    books = [(14, 18, 12, 42, PINK), (28, 14, 12, 46, MINT), (42, 22, 12, 38, LAVENDER), (56, 16, 12, 44, YELLOW),
             (70, 24, 16, 36, CORAL)]
    for x, y, w, h, col in books:
        c.layer(rrect(x, y, w, h, 2), col, depth=2, shadow=False)
        c.flat(rrect(x + 3, y + 6, w - 6, 4, 2), PAPER, op=.8)
    c.layer(rrect(16, 84, 30, 30, 5), LAVENDER_DK, depth=3, shadow=False)  # a box and a ball
    c.flat(circle(31, 99, 6), PAPER)
    c.layer(circle(68, 100, 15), CORAL, depth=3, shadow=False)
    c.flat(rrect(53, 97, 30, 6, 3), YELLOW)
    c.layer(rrect(4, 60, W - 8, 8, 3), WOOD_DK, depth=2, shadow=False)     # the middle board


def draw_tv(c, state):
    W, H = c.w - 10, c.h - 10      # 100 x 75
    for x in (18, W - 34):
        c.layer(rrect(x, H - 12, 16, 12, 4), kit.dk(LAVENDER, .25), depth=2, shadow=False)
    c.layer(rrect(0, 0, W, H - 10, 12), LAVENDER, depth=5)
    c.flat(rrect(9, 8, W - 18, H - 28, 8), "#8E8AA6")                      # the screen, off
    c.flat(rrect(14, 12, 20, 8, 4), PAPER, op=.35)                         # a glint
    c.face(W / 2, H / 2 - 4, 9, "sleepy", col=PAPER, blush=BLUSH)
    c.flat(circle(W - 18, H - 16, 3), CORAL)                               # the little light


def draw_plant(c, state):
    W, H = c.w - 10, c.h - 10      # 80 x 120
    wilt = state == "wilt"
    leaf = kit.tone(LEAF, l=.95, s=.45) if wilt else LEAF
    leaf2 = kit.tone(LEAF_DK, l=1.0, s=.45) if wilt else LEAF_DK
    base = (W / 2, 76)
    if wilt:
        leaves = [(-70, 30, 14, leaf2), (70, 30, 14, leaf2), (-40, 26, 12, leaf), (40, 26, 12, leaf), (0, 18, 10, leaf)]
    else:
        leaves = [(-55, 34, 14, leaf2), (55, 34, 14, leaf2), (-25, 40, 12, leaf), (25, 40, 12, leaf), (0, 46, 11, leaf)]
    for ang, ln, wd, col in leaves:
        a = math.radians(-90 + ang)
        cx, cy = base[0] + math.cos(a) * ln / 2, base[1] + math.sin(a) * ln / 2
        if wilt:
            cy += ln * .35
        sh = ellipse(cx, cy, wd, ln / 2).rotate(ang + (ang * .6 if wilt else 0), cx, cy)
        c.layer(sh, col, depth=3, shadow=False)
        c.stroke(path([(cx, cy - ln / 2 + 6), (cx, cy + ln / 2 - 6)]).rotate(ang + (ang * .6 if wilt else 0), cx, cy),
                 kit.dk(col, .25), 1.6, op=.7)
    c.layer(poly([(14, 80), (W - 14, 80), (W - 18, H), (18, H)]), PEACH_DK, depth=4)   # the pot
    c.layer(rrect(8, 70, W - 16, 16, 7), PEACH, depth=3)
    c.face(W / 2, 100, 6.5, "sleepy" if wilt else "happy")


def draw_picture(c, state):
    W, H = c.w - 10, c.h - 10      # 100 x 80
    c.layer(rrect(0, 0, W, H, 8), WOOD, depth=5)
    c.flat(rrect(9, 9, W - 18, H - 18, 4), CREAM)
    c.flat(rrect(9, H - 26, W - 18, 17, 4, rtl=0, rtr=0), LEAF)              # the ground
    c.flat(circle(W - 28, 28, 10), YELLOW)                                   # the sun
    c.flat(circle(26, 26, 6) + circle(35, 23, 8) + circle(44, 27, 5), PAPER)  # a cloud
    c.layer(rrect(30, 36, 6, 22, 2), WOOD_DEEP, depth=0, shadow=False)        # a little tree
    c.layer(circle(33, 34, 12), LEAF_DK, depth=2, shadow=False)


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    W, H = c.w - 10, c.h - 10      # 80 x 70
    c.layer(rrect(0, 0, W, H, 10), PINK, depth=5)
    c.flat(rrect(8, 8, W - 16, H - 16, 5), PAPER)
    c.layer(heart(W / 2, H / 2 + 4, 34), CORAL, depth=2, shadow=False)
    c.flat(star(W - 20, 18, 6), YELLOW)
    c.flat(star(18, H - 18, 5), YELLOW)


def draw_deco_2(c, state):
    W, H = c.w - 10, c.h - 10      # 60 x 70
    c.layer(rrect(0, H - 10, W, 10, 4), WOOD_DK, depth=4)                  # a little wall shelf
    c.layer(rrect(16, 40, W - 32, 22, 6, rtl=3, rtr=3), LAVENDER, depth=3)   # the pot
    c.layer(rrect(12, 36, W - 24, 10, 4), LAVENDER_DK, depth=2, shadow=False)
    for cx, cy, r, col in ((W / 2, 20, 13, LEAF), (W / 2 - 14, 28, 10, LEAF_DK), (W / 2 + 14, 28, 10, LEAF_DK)):
        c.layer(circle(cx, cy, r), col, depth=2, shadow=False)
    c.flat(circle(W / 2, 14, 4), PINK_DK)                                  # a flower


def draw_deco_3(c, state):
    W, H = c.w - 10, c.h - 10      # 430 x 60
    pts = [(x, 8 + 22 * math.sin(math.pi * x / W)) for x in range(0, int(W) + 1, 10)]
    c.stroke(path(pts), DARK, 2.5)
    cols = [PINK, YELLOW, MINT, LAVENDER, CORAL]
    for i in range(9):
        x = W * (i + 1) / 10
        y = 8 + 22 * math.sin(math.pi * x / W)
        c.layer(rrect(x - 4, y, 8, 8, 2), GREY, depth=2, shadow=False)     # the cap
        c.layer(circle(x, y + 17, 10), cols[i % 5], depth=3)
        c.flat(circle(x - 3, y + 13, 3), PAPER, op=.8)


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "living", "客廳", "living room",
    exits={"left": "kitchen", "right": "entrance", "up": "bedroom"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(408, 688, 120, 160),
    bg=draw_bg,
    things=[
        Thing("window", "窗戶", "window", 150, 250, 220, 200, z=5, draw=draw_window),
        Thing("picture", "牆上的畫", "picture", 345, 215, 110, 90, z=5, draw=draw_picture),
        Thing("stairs", "樓梯", "stairs", 545, 480, 110, 360, z=8, draw=draw_stairs),
        Thing("sofa", "沙發", "sofa", 175, 610, 260, 170, z=10, draw=draw_sofa),
        Thing("lamp", "檯燈", "lamp", 335, 540, 70, 200, z=11, draw=draw_lamp, states=("on", "off")),
        Thing("shelf", "書櫃", "bookshelf", 420, 500, 110, 140, z=12, draw=draw_shelf),
        Thing("tv", "電視", "TV", 420, 395, 110, 85, z=13, draw=draw_tv),
        Thing("rug", "地毯", "rug", 300, 720, 300, 100, z=15, draw=draw_rug),
        Thing("plant", "盆栽", "plant", 440, 640, 90, 130, z=18, draw=draw_plant, states=("", "wilt")),
        Thing("table", "小桌子", "little table", 120, 700, 160, 80, z=20, draw=draw_table),
        Thing("phone", "電話", "telephone", 120, 648, 80, 62, z=21, draw=draw_phone),
        Thing("toybox", "玩具箱", "toy box", 532, 690, 120, 100, z=22, draw=draw_toybox, states=("", "full")),
    ],
    decos=[
        Deco("deco_1", "牆上的畫", "picture", 460, 230, 90, 80, draw=draw_deco_1),
        Deco("deco_2", "窗邊盆栽", "plant by the window", 262, 330, 70, 80, draw=draw_deco_2),
        Deco("deco_3", "小燈串", "string lights", 300, 70, 440, 70, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
