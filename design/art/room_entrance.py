"""門口 the entrance hall: the big front door (the way out to the street), a low shoe rack, the school bag
and the bike helmet on hooks, an umbrella in its stand and the door mat. Same structure as
room_living.py; boxes in scene pixels (600 x 800).

The avatar (308 x 400 on the stand box) covers about x 138-376 at head height (y 337-566) and
x 161-350 lower down, so the shoe rack stays left of x 138, the door, mat and umbrella right of x 376,
and the hooks for the bag and helmet sit on the wall above the head (y < 320).
"""
import math

import kit
from kit import (CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT_DK, PAPER, PEACH, PEACH_DK,
                 PINK, PINK_DK, SKY_TOKEN, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, Shape, circle, ellipse, heart, path,
                 poly, rect, rrect, star)
import scene
from scene import Box, Deco, Thing

FLOOR_Y = 560
WALL_E = kit.lt(LAVENDER, .55)      # pale lavender wall with faint stripes
BLUE = "#9DC4EC"

# the door box, so the background's sky patch sits exactly behind its round window
DOOR_CX, DOOR_CY, DOOR_W, DOOR_H = 500, 400, 180, 400
DOOR_WIN_Y, DOOR_WIN_R = 84, 34


# ---------------------------------------------------------------- background
def draw_bg(c):
    c.flat(rect(0, 0, 600, FLOOR_Y + 20), WALL_E)
    stripes = Shape()
    for x in range(10, 600, 48):
        stripes = stripes + rect(x, 0, 22, FLOOR_Y)
    c.flat(stripes, kit.dk(WALL_E, .045))
    # the sky seen through the door's round window
    wx = DOOR_CX - DOOR_W / 2 + (DOOR_W - 10) / 2
    wy = DOOR_CY - DOOR_H / 2 + DOOR_WIN_Y
    c.flat(circle(wx, wy, DOOR_WIN_R + 3), SKY_TOKEN)
    # the floor: pale stone tiles
    c.flat(rect(0, FLOOR_Y, 600, 800 - FLOOR_Y), kit.lt(GREY, .5))
    lines = Shape()
    for i in range(1, 8):
        lines = lines + rect(i * 75 - 1, FLOOR_Y, 2, 240)
    for i in range(1, 4):
        lines = lines + rect(0, FLOOR_Y + i * 60 - 1, 600, 2)
    c.flat(lines, kit.dk(GREY, .12), op=.8)
    # the wall standing up on the floor, and the skirting board
    c.flat(rect(0, FLOOR_Y, 600, 16), kit.SHADOW, op=.12)
    c.flat(rect(0, FLOOR_Y + 16, 600, 10), kit.SHADOW, op=.05)
    c.layer(rrect(0, FLOOR_Y - 14, 600, 18, 3), WOOD_DK, depth=4, shadow=False)
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_door(c, state):
    W, H = c.w - 10, c.h - 10      # 170 x 390
    c.layer(rrect(0, 0, W, H, 14, rbl=0, rbr=0), WOOD_DK, depth=6)        # the frame
    c.layer(rrect(14, 14, W - 28, H - 14, 8, rbl=0, rbr=0), CORAL, depth=4, shadow=False)   # the door
    # the round window
    c.layer(circle(W / 2, DOOR_WIN_Y, DOOR_WIN_R + 8), PAPER, depth=3, shadow=False)
    c.flat(circle(W / 2, DOOR_WIN_Y, DOOR_WIN_R), SKY_TOKEN)
    c.stroke(path([(W / 2, DOOR_WIN_Y - DOOR_WIN_R), (W / 2, DOOR_WIN_Y + DOOR_WIN_R)]), PAPER, 4)
    c.stroke(path([(W / 2 - DOOR_WIN_R, DOOR_WIN_Y), (W / 2 + DOOR_WIN_R, DOOR_WIN_Y)]), PAPER, 4)
    # two panels; the upper one is the door's face
    c.flat(rrect(30, 150, W - 60, 82, 8), kit.lt(CORAL, .18))
    c.face(W / 2, 192, 12, "happy")
    c.flat(rrect(30, 272, W - 60, 96, 8), kit.lt(CORAL, .18))
    c.flat(heart(W / 2, 322, 30), kit.lt(CORAL, .45))
    # the knob
    c.layer(circle(W - 40, 252, 10), YELLOW, depth=3, shadow=False)
    c.flat(circle(W - 43, 249, 3), PAPER, op=.8)
    c.layer(rrect(0, H - 10, W, 10, 3), WOOD_DEEP, depth=3, shadow=False)   # the threshold


def _shoe(c, x, y, col):
    sh = rrect(x, y, 28, 14, 7) + rrect(x, y - 6, 13, 12, 5)
    c.layer(sh, col, depth=3, shadow=False)
    c.flat(rrect(x + 5, y + 7, 18, 3, 1.5), PAPER, op=.85)


def draw_shoerack(c, state):
    W, H = c.w - 10, c.h - 10      # 120 x 100
    for x in (0, W - 12):                                                  # the two sides
        c.layer(rrect(x, 0, 12, H, 5), WOOD_DK, depth=3)
    c.layer(rrect(0, 0, W, 12, 5), WOOD, depth=4)                          # the top board (a seat)
    c.layer(rrect(6, 48, W - 12, 9, 4), WOOD, depth=3)                     # the shelf
    c.layer(rrect(6, H - 14, W - 12, 9, 4), WOOD, depth=3)                 # the bottom shelf
    _shoe(c, 18, 34, CORAL)                                                # a red pair on the shelf
    _shoe(c, 50, 34, CORAL)
    _shoe(c, 34, 72, BLUE)                                                 # a blue pair below
    _shoe(c, 66, 72, BLUE)


def _hook(c, cx, top):
    c.layer(rrect(cx - 18, top, 36, 9, 4), WOOD_DK, depth=3, shadow=False)
    c.stroke(path([(cx, top + 9), (cx, top + 17)]), GREY, 3.5)
    c.flat(circle(cx, top + 18, 3), GREY)


def draw_bag(c, state):
    W, H = c.w - 10, c.h - 10      # 100 x 140
    _hook(c, W / 2, 0)
    c.stroke(kit.arc(W / 2, 40, 17, 180, 360).move(2, 3), kit.dk(YELLOW, .4), 6)   # the strap's thickness
    c.stroke(kit.arc(W / 2, 40, 17, 180, 360), kit.dk(YELLOW, .2), 6)     # the strap on the hook
    c.layer(rrect(14, 42, W - 28, 88, 18), YELLOW, depth=5)                # the bag
    c.layer(rrect(14, 42, W - 28, 38, 18, rbl=16, rbr=16), kit.dk(YELLOW, .1), depth=3)   # the flap
    c.flat(circle(W / 2, 78, 6), CORAL)                                    # the buckle
    c.layer(rrect(30, 96, W - 60, 28, 9), kit.dk(YELLOW, .08), depth=2, shadow=False)   # the pocket
    c.face(W / 2, 108, 6.5, "happy")


def draw_helmet(c, state):
    W, H = c.w - 10, c.h - 10      # 80 x 70
    _hook(c, W / 2, 0)
    c.stroke(kit.arc(W / 2, 32, 13, 180, 360), kit.dk(LAVENDER_DK, .35), 4)   # the strap over the hook
    pts = [(W / 2 + 34 * math.cos(a), 50 - 27 * math.sin(a)) for a in [math.pi * i / 30 for i in range(31)]]
    c.layer(poly(pts), LAVENDER_DK, depth=5)                               # the dome
    c.layer(rrect(W / 2 - 36, 48, 72, 11, 5.5), kit.dk(LAVENDER_DK, .18), depth=3, shadow=False)   # the rim
    for x in (W / 2 - 15, W / 2, W / 2 + 15):                              # vents
        c.flat(rrect(x - 3, 27, 6, 12, 3), kit.dk(LAVENDER_DK, .35))
    c.flat(star(W / 2 + 24, 42, 6), YELLOW)
    c.stroke(kit.arc(W / 2, 54, 20, 25, 155), kit.dk(LAVENDER_DK, .4), 3.5)   # the chin strap


def draw_umbrella(c, state):
    W, H = c.w - 10, c.h - 10      # 60 x 190
    # the umbrella: closed, handle up, tip down in the stand
    c.stroke(path([(W / 2, 36), (W / 2, 26)]), WOOD_DEEP, 4.5)
    c.stroke(kit.arc(W / 2 - 7, 26, 7, 0, -180), WOOD_DEEP, 4.5)          # the hooked handle
    c.stroke(path([(W / 2 - 14, 26), (W / 2 - 14, 32)]), WOOD_DEEP, 4.5)
    body = poly([(W / 2 - 11, 126), (W / 2 + 11, 126), (W / 2 + 3, 38), (W / 2 - 3, 38)])
    c.layer(body, PINK, depth=3)
    c.flat(poly([(W / 2 - 5, 126), (W / 2 + 1, 126), (W / 2, 40), (W / 2 - 1.5, 40)]), LAVENDER_DK)   # a fold
    c.flat(rrect(W / 2 - 7, 92, 14, 6, 3), PINK_DK)                       # the band
    c.flat(circle(W / 2 - 3, 95, 1.8), PAPER)
    # the stand
    c.layer(rrect(6, 118, W - 12, H - 118, 10), MINT_DK, depth=5)
    c.flat(rrect(6, 134, W - 12, 7, 3), kit.lt(MINT_DK, .3))
    c.flat(heart(W / 2, 162, 16), PAPER, op=.8)


def draw_mat(c, state):
    W, H = c.w - 10, c.h - 10      # 190 x 60
    c.layer(rrect(0, 8, W, H - 8, 10), WOOD_DK, depth=3, shadow_op=.12)
    c.flat(rrect(10, 16, W - 20, H - 24, 7), kit.lt(WOOD_DK, .22))
    c.flat(heart(W / 2, H / 2 + 6, 26), PINK)
    for x in (34, W - 34):
        c.flat(circle(x, H / 2 + 4, 5), YELLOW)
        c.flat(circle(x, H / 2 + 4, 2), PAPER)
    fr = Shape()
    for i in range(5):
        fr = fr + rect(16 + i * 4, 20, 1.6, H - 32) + rect(W - 18 - i * 4, 20, 1.6, H - 32)
    c.flat(fr, kit.dk(WOOD_DK, .2), op=.7)


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    W, H = c.w - 10, c.h - 10      # 150 x 60: a welcome sign with a heart, hanging on a string
    c.stroke(path([(22, 20), (W / 2, 2), (W - 22, 20)]), DARK, 2.2)
    c.layer(rrect(0, 18, W, H - 18, 10), WOOD, depth=5)
    c.flat(rrect(8, 26, W - 16, H - 34, 6), PAPER)
    c.layer(heart(W / 2, H / 2 + 12, 26), CORAL, depth=2, shadow=False)
    for x in (30, W - 30):
        c.flat(star(x, H / 2 + 8, 7), YELLOW)
    for x in (54, W - 54):
        c.flat(circle(x, H / 2 + 10, 3), PINK_DK)


def _key(c, x, y, col):
    c.flat(kit.ring(x, y, 7, 3.5), col, rule="evenodd")
    c.flat(rrect(x - 2.5, y + 5, 5, 22, 2), col)
    c.flat(rrect(x + 1, y + 18, 6, 3, 1), col)
    c.flat(rrect(x + 1, y + 23, 5, 3, 1), col)


def draw_deco_2(c, state):
    W, H = c.w - 10, c.h - 10      # 90 x 70: key hooks with keys
    c.layer(rrect(0, 0, W, 26, 8), WOOD, depth=5)
    c.flat(poly([(W / 2 - 9, 15), (W / 2, 6), (W / 2 + 9, 15)]), CORAL)   # a tiny house
    c.flat(rrect(W / 2 - 6, 14, 12, 8, 1.5), PAPER)
    for x in (16, W / 2, W - 16):
        c.flat(circle(x, 28, 3.2), GREY)
    _key(c, 16, 38, YELLOW)
    _key(c, W / 2, 38, GREY)
    c.stroke(path([(W - 16, 30), (W - 16, 44)]), DARK, 1.6)               # a heart key-ring
    c.layer(heart(W - 16, 54, 18), PINK_DK, depth=2, shadow=False)


def draw_deco_3(c, state):
    W, H = c.w - 10, c.h - 10      # 50 x 80: a little plant on the shoe rack
    base = (W / 2, 44)
    for ang, ln, wd, col in ((-55, 30, 9, LEAF_DK), (55, 30, 9, LEAF_DK), (-24, 36, 8, LEAF), (24, 36, 8, LEAF), (0, 40, 8, LEAF)):
        a = math.radians(-90 + ang)
        cx, cy = base[0] + math.cos(a) * ln / 2, base[1] + math.sin(a) * ln / 2
        c.layer(ellipse(cx, cy, wd, ln / 2).rotate(ang, cx, cy), col, depth=2, shadow=False)
    c.flat(circle(W / 2, 8, 4.5), PINK_DK)
    c.flat(circle(W / 2, 8, 1.8), YELLOW)
    c.layer(poly([(8, 48), (W - 8, 48), (W - 11, H), (11, H)]), PEACH_DK, depth=4)   # the pot
    c.layer(rrect(4, 42, W - 8, 11, 5), PEACH, depth=3)


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "entrance", "門口", "entrance",
    exits={"left": "living", "out": "street"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(470, 700, 110, 150),
    bg=draw_bg,
    things=[
        Thing("door", "大門", "front door", DOOR_CX, DOOR_CY, DOOR_W, DOOR_H, z=5, draw=draw_door),
        Thing("bag", "書包", "school bag", 70, 300, 110, 150, z=8, draw=draw_bag),
        Thing("helmet", "安全帽", "helmet", 190, 265, 90, 80, z=8, draw=draw_helmet),
        Thing("shoerack", "鞋架", "shoe rack", 70, 600, 130, 110, z=10, draw=draw_shoerack),
        Thing("mat", "地墊", "door mat", 500, 640, 200, 70, z=12, draw=draw_mat),
        Thing("umbrella", "雨傘", "umbrella", 395, 600, 70, 200, z=13, draw=draw_umbrella),
    ],
    decos=[
        Deco("deco_1", "歡迎牌", "welcome sign", 500, 150, 160, 70, draw=draw_deco_1),
        Deco("deco_2", "鑰匙掛鉤", "key hooks", 300, 220, 100, 80, draw=draw_deco_2),
        Deco("deco_3", "門邊盆栽", "little plant", 40, 515, 60, 90, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
