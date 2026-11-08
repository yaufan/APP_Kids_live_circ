"""房間 the bedroom: a soft lilac wall with faint stars, the bed on the right (headboard against the
right wall, pillow at the head), the wardrobe on the left, the curtained window above the avatar.

Scene pixels are 600 x 800; the wall is the top 560 px and the floor the bottom 240 px. The avatar's
stand box (204 x 400, feet at y 688) is kept clear: the bed sits to its right, the wardrobe and the
little table with the storybook to its left. Each `draw_*(c, state)` paints into a kit.Ctx the size
of the thing's box and leaves ~10 px free on the right and bottom for the paper shadow.
"""
import math

import kit
from kit import (CORAL, CREAM, DARK, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH, PEACH_DK,
                 PINK, PINK_DK, SKY_TOKEN, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, circle, ellipse, heart, path, poly,
                 rect, rrect, star)
import scene
from scene import Box, Deco, Thing

FLOOR_Y = 560
WALL = kit.lt(LAVENDER, .5)        # a soft lilac wall, this room's own colour


def dome(cx, cy, rx, ry, steps=24):
    """The top half of an ellipse with a flat base (a mushroom cap, a hood)."""
    pts = [(cx + rx * math.cos(math.pi * i / steps), cy - ry * math.sin(math.pi * i / steps)) for i in range(steps + 1)]
    return poly(pts)


# ---------------------------------------------------------------- background
def draw_bg(c):
    # the wall: lilac paper with faint little stars
    c.flat(rect(0, 0, 600, FLOOR_Y + 20), WALL)
    for row in range(10):
        y = 30 + row * 54
        for col in range(11):
            x = 30 + col * 56 + (28 if row % 2 else 0)
            if x < 590 and y < FLOOR_Y - 30:
                c.flat(star(x, y, 6, 2.6), kit.dk(WALL, .08))
    # the sky behind the window (the curtain thing's glass is also #SKY; the app recolours both)
    c.flat(rrect(150, 100, 200, 150, 10), SKY_TOKEN)
    # the floor: the same warm wood as the living room
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
    # the page's side edges
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_curtain(c, state):
    W, H = c.w - 10, c.h - 12      # 210 x 188
    closed = state == "closed"
    c.layer(rrect(0, 4, W, 10, 5), WOOD_DEEP, depth=3)                     # curtain rod
    c.layer(rrect(6, 18, W - 12, 150, 14), WOOD, depth=5)                  # frame
    if not closed:
        c.flat(rrect(20, 32, W - 40, 122, 6), SKY_TOKEN)                   # glass (recoloured by the app)
        cl = ellipse(62, 112, 34, 14) + circle(52, 104, 16) + circle(74, 102, 18)
        c.flat(cl, PAPER, op=.92)                                          # a cloud
        c.layer(rrect(W / 2 - 5, 32, 10, 122, 4), kit.lt(WOOD, .12), depth=2, shadow=False)   # cross bars
        c.layer(rrect(20, 88, W - 40, 10, 4), kit.lt(WOOD, .12), depth=2, shadow=False)
        # curtains pulled to the sides, with a tie-back each
        left = poly([(6, 14), (62, 14), (58, 60), (50, 100), (46, 140), (52, 164), (6, 164)])
        dots = [(20 + j * 22, 36 + i * 26 + (8 if j else 0)) for i in range(5) for j in range(2)]
        for flip in (False, True):
            sh = left.flip(W / 2) if flip else left
            c.layer(sh, LAVENDER, depth=4)
            c.dots([((W - x) if flip else x, y) for x, y in dots], 3.2, PAPER)
            tx = (W - 50) if flip else 50
            c.layer(ellipse(tx, 118, 12, 7), LAVENDER_DK, depth=2, shadow=False)
    else:
        # the curtains drawn shut: two wavy panels meeting in the middle, the glass hidden
        c.flat(rrect(20, 32, W - 40, 122, 6), kit.dk(WOOD, .3))
        half = W / 2
        pan = poly([(6, 14), (half + 3, 14), (half - 4, 50), (half + 4, 90), (half - 3, 130), (half + 3, 164), (6, 164)])
        dots = [(20 + j * 24, 36 + i * 26 + (8 if j % 2 else 0)) for i in range(5) for j in range(4) if 20 + j * 24 < half - 10]
        for flip in (False, True):
            sh = pan.flip(W / 2) if flip else pan
            c.layer(sh, LAVENDER, depth=4)
            c.dots([((W - x) if flip else x, y) for x, y in dots], 3.2, PAPER)
            # the folds: soft darker stripes
            for k in range(2):
                fx = 28 + k * 30
                fx = (W - fx) if flip else fx
                c.stroke(path([(fx, 22), (fx + (3 if flip else -3), 160)]), kit.dk(LAVENDER, .12), 4, op=.6)
    c.layer(rrect(0, 164, W, 16, 6), WOOD_DK, depth=5)                     # the sill


def draw_wardrobe(c, state):
    W, H = c.w - 10, c.h - 10      # 130 x 310
    for x in (10, W - 26):                                                 # feet
        c.layer(rrect(x, H - 14, 16, 14, 5), WOOD_DEEP, depth=2, shadow=False)
    c.layer(rrect(0, 28, W, H - 40, 10), WOOD, depth=6)                    # the body
    c.layer(rrect(-0, 10, W, 30, 10), WOOD_DK, depth=4)                    # the top board
    c.face(W / 2, 26, 7, "happy")
    for i in range(2):                                                     # two doors
        x = 8 + i * (W / 2 - 6)
        c.layer(rrect(x, 48, W / 2 - 10, H - 76, 8), kit.lt(WOOD, .2), depth=3, shadow=False)
        c.flat(rrect(x + 10, 60, W / 2 - 30, H - 100, 6), kit.lt(WOOD, .08), op=.8)   # the door panel
    for x in (W / 2 - 14, W / 2 + 14):                                     # the two handles
        c.layer(circle(x, H / 2 + 10, 6), CORAL, depth=2, shadow=False)
    c.flat(rrect(W / 2 - 2, 48, 4, H - 76, 2), kit.dk(WOOD, .22))         # the gap between the doors
    c.layer(heart(W / 2, 100, 20), PINK, depth=2, shadow=False)            # a heart sticker on the doors
    c.flat(heart(W / 2, 100, 20), PINK, op=1)
    c.flat(rrect(W / 2 - 2, 90, 4, 20, 2), kit.dk(WOOD, .22), op=.5)


def draw_bed(c, state):
    W, H = c.w - 10, c.h - 10      # 230 x 210
    for x in (14, W - 64):                                                 # legs
        c.layer(rrect(x, H - 20, 18, 20, 6), WOOD_DEEP, depth=2, shadow=False)
    c.layer(rrect(W - 56, 0, 56, 160, 18, rbl=6, rbr=6), WOOD, depth=6)    # the headboard (against the right wall)
    c.face(W - 28, 44, 7.5, "sleepy")
    c.layer(rrect(0, 44, 32, 124, 12, rbl=6, rbr=6), WOOD, depth=5)        # the footboard
    c.layer(rrect(14, 132, W - 52, 58, 10), WOOD_DK, depth=5)              # the bed base
    c.layer(rrect(18, 106, W - 60, 40, 12), PAPER, depth=4)                # the mattress / sheet
    c.layer(rrect(W - 124, 76, 74, 40, 16), PINK, depth=4)                 # the pillow
    c.flat(ellipse(W - 87, 92, 22, 8), kit.lt(PINK, .4), op=.8)
    # the blanket: mint with stars, tucked at the foot, folded back at the pillow
    blanket = poly([(24, 112), (W - 126, 112), (W - 118, 140), (W - 126, 168), (24, 168)])
    c.layer(blanket, MINT, depth=4)
    c.flat(rrect(24, 112, W - 150, 12, 5), kit.lt(MINT, .35))              # the folded edge
    for i in range(4):
        c.flat(star(50 + i * 34, 146, 8, 3.5), PAPER, op=.9)


def draw_nightlight(c, state):
    W, H = c.w - 10, c.h - 10      # 80 x 100
    on = state != "off"
    c.layer(rrect(0, H - 14, W, 12, 4), WOOD_DK, depth=4)                  # a little wall shelf
    if on:
        c.flat(ellipse(W / 2, 40, 40, 44), YELLOW, op=.3)                  # the glow
        c.flat(ellipse(W / 2, 40, 30, 34), YELLOW, op=.3)
    c.layer(rrect(W / 2 - 13, 40, 26, 48, 9), CREAM, depth=3)              # the stem
    c.face(W / 2, 62, 5, "happy" if on else "sleepy")
    cap = dome(W / 2, 42, 32, 34)
    c.layer(cap, YELLOW if on else kit.lt(LAVENDER, .15), depth=4)        # the cap
    c.dots([(W / 2 - 14, 24), (W / 2 + 10, 16), (W / 2 + 18, 32)], 4, PAPER, op=.9)
    if on:
        for ang in (-60, -20, 20, 60):                                     # little rays
            a = math.radians(-90 + ang)
            x0, y0 = W / 2 + math.cos(a) * 40, 42 + math.sin(a) * 40
            x1, y1 = W / 2 + math.cos(a) * 48, 42 + math.sin(a) * 48
            c.stroke(path([(x0, y0), (x1, y1)]), YELLOW, 3, op=.8)


def draw_height(c, state):
    W, H = c.w - 10, c.h - 10      # 50 x 350
    c.layer(rrect(8, 36, W - 16, H - 36, 6), CREAM, depth=4)               # the ruler
    for i in range(16):                                                    # marks, a long one every third
        y = 56 + i * 18
        long = i % 3 == 0
        c.stroke(path([(14, y), (14 + (16 if long else 8), y)]), kit.dk(CREAM, .5), 2.5)
        if long:
            c.flat(circle(W - 16, y, 3.5), (PINK_DK, MINT_DK, CORAL, LAVENDER_DK, YELLOW, LEAF_DK)[i // 3 % 6])
    # the flower on top: a tall stem up the ruler, leaves, petals and a smiling centre
    c.stroke(path([(W / 2, 40), (W / 2, 70)]), LEAF_DK, 3)
    c.layer(ellipse(W / 2 - 9, 60, 8, 4).rotate(-30, W / 2 - 9, 60), LEAF, depth=2, shadow=False)
    c.layer(ellipse(W / 2 + 9, 54, 8, 4).rotate(30, W / 2 + 9, 54), LEAF, depth=2, shadow=False)
    for k in range(6):
        a = math.radians(k * 60 - 90)
        c.layer(circle(W / 2 + math.cos(a) * 11, 22 + math.sin(a) * 11, 7), PINK, depth=2, shadow=False)
    c.layer(circle(W / 2, 22, 8), YELLOW, depth=2, shadow=False)
    c.face(W / 2, 21, 2.6, "smile")


def draw_rug(c, state):
    W, H = c.w - 10, c.h - 10      # 270 x 90
    c.layer(ellipse(W / 2, H / 2, W / 2, H / 2), MINT, depth=2, shadow_op=.12)
    c.flat(ellipse(W / 2, H / 2, W / 2 - 22, H / 2 - 13), kit.lt(MINT, .35))
    c.dots([(W / 2 + (W / 2 - 11) * math.cos(a), H / 2 + (H / 2 - 6) * math.sin(a))
            for a in [i * 2 * math.pi / 16 for i in range(16)]], 3.5, PAPER)
    c.flat(star(W / 2, H / 2, 20, 9), YELLOW)
    c.flat(star(W / 2 - 60, H / 2, 10, 4.5), PAPER)
    c.flat(star(W / 2 + 60, H / 2, 10, 4.5), PAPER)


def draw_book(c, state):
    W, H = c.w - 10, c.h - 10      # 120 x 100
    # the little table the storybook lies on
    for x in (22, W - 32):
        c.layer(rrect(x, 54, 10, H - 54, 4), WOOD_DK, depth=2)
    c.layer(rrect(26, 66, W - 52, 6, 3), WOOD_DK, depth=2, shadow=False)
    c.layer(ellipse(W / 2, 50, W / 2, 14), WOOD, depth=4)
    # the storybook: a thick cover, pages, a sun on the cover
    c.layer(rrect(20, 22, W - 40, 26, 4), PAPER, depth=3)                  # pages
    c.layer(rrect(16, 10, W - 32, 30, 6), CORAL, depth=4)                  # the cover
    c.flat(rrect(22, 14, 7, 22, 3), kit.dk(CORAL, .3))                      # the spine
    c.flat(circle(W / 2 - 2, 25, 9), YELLOW)
    c.face(W / 2 - 2, 24, 3, "smile")
    c.flat(rrect(W / 2 + 12, 18, 20, 4, 2), PAPER, op=.85)
    c.flat(rrect(W / 2 + 12, 26, 14, 4, 2), PAPER, op=.85)


def draw_toybox_small(c, state):
    W, H = c.w - 10, c.h - 10      # 100 x 80
    c.layer(circle(26, 22, 13), MINT_DK, depth=3)                          # a ball and a block peeking out
    c.flat(rrect(13, 19, 26, 6, 3), PAPER)
    c.layer(rrect(50, 8, 22, 22, 4), LAVENDER_DK, depth=3)
    c.flat(circle(61, 19, 4), PAPER)
    c.layer(rrect(6, 32, W - 12, H - 32, 10), PEACH, depth=5)              # the box
    c.layer(rrect(0, 22, W, 18, 8), PEACH_DK, depth=4)                     # the lid
    c.face(W / 2, 56, 8, "happy")


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    W, H = c.w - 10, c.h - 10      # 210 x 140
    c.layer(rrect(0, 0, W, 10, 5), WOOD_DK, depth=3)                       # the bar they hang from
    cols = (YELLOW, PINK, MINT, LAVENDER, YELLOW)
    for i in range(5):
        x = 22 + i * (W - 44) / 4
        ln = (60, 90, 110, 80, 50)[i]
        c.stroke(path([(x, 10), (x, ln)]), DARK, 1.8, op=.7)
        c.layer(star(x, ln + 14, 16, 7.5), cols[i], depth=3)
        c.face(x, ln + 13, 3.2, "smile")


def draw_deco_2(c, state):
    W, H = c.w - 10, c.h - 10      # 70 x 70
    # a new bedsheet folded over the foot of the bed: pink with hearts, its lower half hangs behind
    # the footboard (decorations are drawn behind the furniture)
    sheet = poly([(4, 10), (W - 6, 4), (W, 30), (W - 4, H), (6, H), (0, 34)])
    c.layer(sheet, PINK, depth=4)
    c.flat(poly([(4, 10), (W - 6, 4), (W - 4, 16), (6, 22)]), kit.lt(PINK, .4))   # the fold on top
    for x, y in ((18, 36), (40, 32), (28, 54), (50, 50)):
        c.flat(heart(x, y, 11), PAPER, op=.92)


def draw_deco_3(c, state):
    W, H = c.w - 10, c.h - 10      # 50 x 70
    c.layer(rrect(0, H - 10, W, 10, 4), WOOD_DK, depth=4)                  # a little wall shelf
    c.layer(rrect(12, 42, W - 24, 20, 6, rtl=3, rtr=3), CORAL, depth=3)    # the pot
    c.layer(rrect(9, 38, W - 18, 9, 4), kit.dk(CORAL, .12), depth=2, shadow=False)
    c.face(W / 2, 54, 3.4, "smile")
    for cx, cy, r, col in ((W / 2, 22, 11, LEAF), (W / 2 - 11, 30, 8, LEAF_DK), (W / 2 + 11, 30, 8, LEAF_DK)):
        c.layer(circle(cx, cy, r), col, depth=2, shadow=False)
    c.flat(star(W / 2, 16, 5, 2.2), YELLOW)                                 # a little flower


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "bedroom", "房間", "bedroom",
    exits={"down": "living", "right": "bathroom"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(408, 688, 120, 160),
    bg=draw_bg,
    things=[
        Thing("curtain", "窗簾", "curtain", 250, 180, 220, 200, z=5, draw=draw_curtain, states=("open", "closed")),
        Thing("height", "身高尺", "height chart", 566, 320, 60, 360, z=6, draw=draw_height),
        Thing("wardrobe", "衣櫃", "wardrobe", 80, 430, 140, 320, z=8, draw=draw_wardrobe),
        Thing("nightlight", "小夜燈", "night light", 420, 440, 90, 110, z=10, draw=draw_nightlight, states=("on", "off")),
        Thing("rug", "地毯", "rug", 250, 728, 280, 100, z=15, draw=draw_rug),
        Thing("bed", "床", "bed", 476, 630, 240, 220, z=20, draw=draw_bed),
        Thing("book", "故事書", "storybook", 75, 680, 130, 110, z=22, draw=draw_book),
        Thing("toybox_small", "小玩具箱", "little toy box", 540, 745, 110, 90, z=25, draw=draw_toybox_small),
    ],
    decos=[
        Deco("deco_1", "星星吊飾", "hanging stars", 440, 110, 220, 150, draw=draw_deco_1),
        Deco("deco_2", "新床單", "new bedsheet", 392, 560, 80, 80, draw=draw_deco_2),
        Deco("deco_3", "窗邊小盆栽", "little plant by the window", 395, 250, 60, 80, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
