"""診所 the clinic: a place outside the house (exit `back` goes to the street).

Everything warm and not scary: a pale mint wall, soft tiles, a kind doctor puppet in a white coat
with a stethoscope, a desk with a thermometer and a jar of stickers, an examination bed with a mint
cover, a tooth poster with a face, a standing scale with a height rod and a little plant on the sill.
The puppet, the window and the fishbowl come from place_school.py; the balloons from place_market.py.
"""
import math

import kit
from kit import (CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH,
                 PEACH_DK, PINK, PINK_DK, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, Shape, arc, circle, ellipse, heart, path,
                 poly, rect, rrect, star)
import scene
from scene import Box, Deco, Thing
from place_school import FLOOR_Y, HAIR_DARK, SKIN, draw_fishbowl, puppet, window_bg
from place_market import draw_balloons

CLINIC_WALL = "#E6F3EC"
CLINIC_TILE = "#F3F1E8"
STEEL = "#D6DDE3"


# ---------------------------------------------------------------- background
def draw_bg(c):
    c.flat(rect(0, 0, 600, FLOOR_Y + 20), CLINIC_WALL)
    pts = []
    for row in range(10):
        y = 36 + row * 50
        for col in range(13):
            x = 26 + col * 48 + (24 if row % 2 else 0)
            if x < 590 and y < FLOOR_Y - 40:
                pts.append((x, y))
    for x, y in pts:                                                       # tiny plus signs, very soft
        c.flat(rrect(x - 4, y - 1.2, 8, 2.4, 1) + rrect(x - 1.2, y - 4, 2.4, 8, 1), kit.dk(CLINIC_WALL, .07))
    window_bg(c, 380, 110, 200, 176, frame=kit.lt(WOOD, .15))
    # the floor: pale tiles
    c.flat(rect(0, FLOOR_Y, 600, 800 - FLOOR_Y), CLINIC_TILE)
    for i in range(1, 8):
        x = i * 80 - 30
        c.stroke(path([(x, FLOOR_Y + 4), (x, 800)]), kit.dk(CLINIC_TILE, .09), 2.5)
    for i in range(3):
        y = FLOOR_Y + 56 + i * 72
        c.stroke(path([(0, y), (600, y)]), kit.dk(CLINIC_TILE, .09), 2.5)
    c.flat(rect(0, FLOOR_Y, 600, 16), kit.SHADOW, op=.12)
    c.flat(rect(0, FLOOR_Y + 16, 600, 10), kit.SHADOW, op=.05)
    c.layer(rrect(0, FLOOR_Y - 14, 600, 18, 3), MINT_DK, depth=4, shadow=False)
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_doctor(c, state):
    puppet(c, skin=SKIN[1], shirt=MINT, pants="#7F8EC9", hair="short", hair_col=HAIR_DARK, coat=True)


def draw_desk(c, state):
    W, H = c.w - 10, c.h - 10      # 160 x 140
    # the sticker jar: stars behind glass
    jx = 138
    for x, y, col in ((jx - 10, 18, YELLOW), (jx + 9, 14, PINK_DK), (jx - 1, 25, MINT_DK), (jx + 12, 25, YELLOW)):
        c.flat(star(x, y, 5.5), col)
    c.layer(rrect(jx - 20, 6, 40, 24, 8), kit.lt(kit.SKY, .4), depth=2, shadow=False, op=.55)
    c.layer(rrect(jx - 15, 0, 30, 9, 3), WOOD_DK, depth=2, shadow=False)
    # the thermometer
    th = rrect(66, 18, 54, 10, 5).rotate(-8, 93, 23)
    c.layer(th, PAPER, depth=2, shadow=False)
    c.stroke(path([(78, 22), (106, 18)]), MINT_DK, 2.2)
    c.layer(circle(66, 25, 6), CORAL, depth=2, shadow=False)
    # the desk: top, drawers with a face, legs
    for x in (22, W - 36):
        c.layer(rrect(x, 108, 14, 26, 5), WOOD_DK, depth=2)
    c.layer(rrect(14, 44, W - 28, 68, 8), kit.lt(WOOD, .15), depth=4)
    c.flat(rrect(26, 52, W - 52, 24, 5), kit.lt(WOOD, .4))
    c.flat(rrect(26, 82, W - 52, 24, 5), kit.lt(WOOD, .4))
    c.face(W / 2, 64, 6, "happy")
    c.layer(circle(W / 2, 94, 4), CORAL, depth=0, shadow=False)
    c.layer(rrect(0, 28, W, 18, 7), WOOD, depth=5)                          # the top


def draw_bed(c, state):
    W, H = c.w - 10, c.h - 10      # 210 x 140
    for x in (22, W - 36):                                                 # legs
        c.layer(rrect(x, 100, 14, 36, 5), STEEL, depth=2)
    c.layer(rrect(0, 20, 14, 94, 6), kit.lt(WOOD, .1), depth=4)            # the headboard
    c.layer(rrect(6, 76, W - 6, 34, 14), PAPER, depth=5)                   # the mattress
    c.layer(rrect(56, 66, W - 56, 36, 12, rbl=4, rbr=4), MINT, depth=4)    # the mint cover
    c.dots([(80 + i * 26, 84 + (4 if i % 2 else 0)) for i in range(5)], 3, PAPER, op=.9)
    c.flat(heart(W - 40, 90, 12), PINK)
    c.layer(rrect(14, 58, 50, 26, 11), kit.lt(LAVENDER, .3), depth=4)      # the pillow
    c.face(W / 2 + 20, 92, 6, "happy")
    c.layer(rrect(W * .52, 110, 44, 14, 5), kit.lt(WOOD, .1), depth=3)      # a little step


def draw_poster(c, state):
    W, H = c.w - 10, c.h - 10      # 160 x 190
    c.layer(rrect(0, 0, W, H, 12), kit.lt(WOOD, .1), depth=5)              # the frame
    c.flat(rrect(10, 10, W - 20, H - 20, 7), kit.lt(MINT, .55))
    # a shiny tooth with a face
    tooth = rrect(46, 44, 68, 64, 26) + ellipse(64, 118, 15, 24) + ellipse(96, 118, 15, 24) + rrect(60, 96, 40, 18, 2)
    c.layer(tooth, PAPER, depth=4)
    c.face(80, 78, 10, "happy")
    c.flat(ellipse(58, 56, 5, 9).rotate(30, 58, 56), kit.lt(kit.SKY, .4), op=.9)
    for x, y, r in ((34, 34, 8), (128, 48, 6), (124, 140, 7), (36, 136, 5)):
        c.flat(star(x, y, r), YELLOW)
    c.flat(heart(W / 2, H - 26, 14), PINK_DK)


def draw_scale(c, state):
    W, H = c.w - 10, c.h - 10      # 70 x 230
    c.layer(rrect(50, 0, 9, 204, 4), MINT_DK, depth=2)                     # the height rod
    for i in range(12):
        y = 14 + i * 16
        c.stroke(path([(50, y), (42 if i % 2 == 0 else 46, y)]), DARK, 1.8, op=.55)
    c.layer(rrect(26, 42, 34, 9, 4), CORAL, depth=2)                       # the sliding bar
    c.layer(rrect(0, 198, W, 26, 10), kit.lt(GREY, .35), depth=5)          # the base
    c.flat(rrect(8, 204, W - 16, 10, 4), kit.lt(GREY, .6))
    c.layer(circle(32, 188, 15), PAPER, depth=3)                           # the dial
    c.stroke(arc(32, 188, 10, 200, 340), GREY, 2)
    c.stroke(path([(32, 188), (32, 178)]), CORAL, 2.2)
    c.face(32, 192, 4.5, "smile")


def draw_plant(c, state):
    W, H = c.w - 10, c.h - 10      # 60 x 90
    base = (W / 2, 56)
    for ang, ln, wd, col in ((-55, 30, 11, LEAF_DK), (55, 30, 11, LEAF_DK), (-22, 36, 10, LEAF), (22, 36, 10, LEAF), (0, 42, 9, LEAF)):
        a = math.radians(-90 + ang)
        cx, cy = base[0] + math.cos(a) * ln / 2, base[1] + math.sin(a) * ln / 2
        c.layer(ellipse(cx, cy, wd, ln / 2).rotate(ang, cx, cy), col, depth=3, shadow=False)
    c.layer(poly([(12, 60), (W - 12, 60), (W - 16, H), (16, H)]), PEACH_DK, depth=4)
    c.layer(rrect(6, 52, W - 12, 14, 6), PEACH, depth=3)
    c.face(W / 2, 76, 5, "happy")


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    """The brave-sticker wall: a board full of star stickers."""
    W, H = c.w - 10, c.h - 10      # 140 x 140
    c.layer(rrect(0, 0, W, H, 12), PINK, depth=5)
    c.flat(rrect(9, 9, W - 18, H - 18, 7), PAPER)
    c.layer(rrect(W / 2 - 34, 2, 68, 18, 8), CORAL, depth=2, shadow=False)   # the ribbon
    c.flat(heart(W / 2, 11, 9), PAPER)
    cols = (YELLOW, PINK_DK, MINT_DK, LAVENDER_DK, CORAL)
    k = 0
    for row in range(3):
        for col in range(3):
            x, y = 36 + col * 34, 46 + row * 34
            c.layer(star(x, y, 12), cols[k % 5], depth=2, shadow=False)
            c.flat(circle(x - 3, y - 3, 2.2), PAPER, op=.7)
            k += 1


def draw_deco_2(c, state):
    draw_fishbowl(c, state)


def draw_deco_3(c, state):
    draw_balloons(c, state)


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "clinic", "診所", "clinic",
    exits={"back": "street"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(400, 790, 100, 130),
    bg=draw_bg,
    things=[
        Thing("poster", "海報", "poster", 300, 170, 170, 200, z=5, draw=draw_poster),
        Thing("plant", "盆栽", "plant", 520, 244, 70, 100, z=8, draw=draw_plant),
        Thing("desk", "桌子", "desk", 95, 508, 170, 150, z=10, draw=draw_desk),
        Thing("bed", "診療床", "examination bed", 480, 510, 220, 150, z=10, draw=draw_bed),
        Thing("scale", "體重計", "scale", 70, 660, 80, 240, z=15, draw=draw_scale),
        Thing("doctor", "醫生", "doctor", 525, 640, 150, 195, z=20, draw=draw_doctor),
    ],
    decos=[
        Deco("deco_1", "勇敢貼紙牆", "brave sticker wall", 95, 280, 150, 150, draw=draw_deco_1),
        Deco("deco_2", "小魚缸", "fishbowl", 40, 433, 70, 60, draw=draw_deco_2),
        Deco("deco_3", "氣球", "balloons", 60, 110, 110, 170, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
