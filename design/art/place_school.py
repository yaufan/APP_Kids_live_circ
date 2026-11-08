"""幼兒園 the kindergarten: a place outside the house (exit `back` goes to the street).

Also home of the helpers the other places share: `puppet()` draws a Q-version paper person (a big
round head, dot eyes, blush, a small body; 200 x 260 proportion) for the teacher, the classmates,
the cashier and the doctor; `window_bg()` draws a window with `#SKY` glass into a background;
`draw_fishbowl()` is the goldfish bowl the school and the clinic both hang up as a decoration.
"""
import math

import kit
from kit import (CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH,
                 PEACH_DK, PINK, PINK_DK, SKY_TOKEN, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, Shape, arc, circle, ellipse,
                 heart, path, poly, rect, rrect, star)
import scene
from scene import Box, Deco, Thing

FLOOR_Y = 560
SCHOOL_WALL = "#FFF3D4"
SCHOOL_FLOOR = "#E8C796"
BOARD = "#6E9C7E"          # the blackboard's green
CHALK = "#FFF6E6"
CHALK_YELLOW = "#FFE7A3"

# skins (light to dark) and hair colours
SKIN = ("#F9DCC3", "#EFC4A0", "#D9A277", "#B97A52")
HAIR_BROWN, HAIR_DARK, HAIR_BLONDE, HAIR_AUBURN = "#5A3A2A", "#3A2A24", "#D9A24A", "#8C4A2C"


# ---------------------------------------------------------------- shared helpers
def dome(cx, cy, r, fringe):
    """A cap of hair: the top half of a circle, closed along `fringe` (points from right to left)."""
    cmds = list(arc(cx, cy, r, 180, 360).cmds)
    for p in fringe:
        cmds.append(("L",) + tuple(p))
    cmds.append(("Z",))
    return Shape(cmds)


def puppet(c, skin=SKIN[0], shirt=CORAL, pants="#7F8EC9", hair="short", hair_col=HAIR_BROWN, wave=False,
           legs=True, mood="happy", glasses=False, tag=False, coat=False, u=None, ox=0.0, oy=0.0):
    """A Q-version paper person in a 200 x 260 frame (feet at 250), scaled by u (default: fit c.w) and
    moved by ox, oy. hair: short / bob / pony / curly / bun. wave: the right arm is up. coat: a white
    coat with a stethoscope (the doctor). tag: a name tag on the chest (the teacher)."""
    u = c.w / 200 if u is None else u

    def S(shape):
        return shape.scale(u).move(ox, oy)

    def P(x, y):
        return x * u + ox, y * u + oy

    skin_dk = kit.dk(skin, .3)
    top = PAPER if coat else shirt
    # hair behind the head (a ponytail)
    if hair == "pony":
        c.layer(S(ellipse(168, 118, 13, 26).rotate(-12, 168, 118)), hair_col, depth=3, shadow=False)
    # legs and shoes
    if legs:
        c.layer(S(rrect(62, 206, 76, 26, 9)), pants, depth=3)
        for x in (82, 118):
            c.flat(S(rrect(x - 10, 226, 20, 16, 6)), skin)
            c.layer(S(ellipse(x, 246, 16, 7)), "#6B5B63", depth=2, shadow=False)
    # body
    c.layer(S(rrect(58, 158, 84, 64, 18)), top, depth=4)
    if coat:
        c.flat(S(poly([(90, 158), (110, 158), (100, 186)])), shirt)                   # the shirt under it
        c.flat(S(poly([(90, 158), (100, 186), (82, 176)])), kit.dk(PAPER, .08))       # lapels
        c.flat(S(poly([(110, 158), (118, 176), (100, 186)])), kit.dk(PAPER, .08))
        c.stroke(S(path([(100, 186), (100, 222)])), kit.dk(PAPER, .14), 1.6 * u)
    # arms
    c.layer(S(rrect(40, 166, 22, 50, 11)), top, depth=3, shadow=False)                # left arm, down
    c.layer(S(circle(51, 216, 10)), skin, depth=2, shadow=False)
    if wave:
        arm = rrect(138, 120, 22, 56, 11).rotate(25, 149, 174)
        c.layer(S(arm), top, depth=3, shadow=False)
        hx, hy = 149 + 54 * math.sin(math.radians(25)), 174 - 54 * math.cos(math.radians(25))
        c.layer(S(circle(hx, hy, 11)), skin, depth=2, shadow=False)
    else:
        c.layer(S(rrect(138, 166, 22, 50, 11)), top, depth=3, shadow=False)
        c.layer(S(circle(149, 216, 10)), skin, depth=2, shadow=False)
    if coat:                                                                            # stethoscope
        c.stroke(S(path([(84, 162), (82, 184), (86, 200)])), GREY, 3 * u)
        c.stroke(S(arc(100, 154, 18, 10, 170)), GREY, 3 * u)
        c.layer(S(circle(88, 206, 8)), GREY, depth=2, shadow=False)
        c.flat(S(circle(88, 206, 4)), PAPER)
    if tag:
        c.layer(S(rrect(108, 176, 28, 18, 4)), PAPER, depth=2, shadow=False)
        c.flat(S(heart(122, 185, 9)), PINK_DK)
    # neck and head
    c.flat(S(rrect(88, 146, 24, 20, 6)), skin_dk)
    c.layer(S(circle(100, 92, 62)), skin, depth=5)
    for x in (38, 162):
        c.layer(S(circle(x, 98, 11)), skin, depth=2, shadow=False)
        c.flat(S(circle(x, 98, 5)), kit.mix(skin, PINK_DK, .35))
    # hair in front
    if hair == "short":
        fr = [(164, 92), (152, 66), (136, 78), (118, 62), (100, 74), (82, 62), (64, 78), (48, 66), (36, 92)]
        c.layer(S(dome(100, 92, 64, fr)), hair_col, depth=3, shadow=False)
    elif hair == "bob":
        fr = [(164, 92), (150, 72), (130, 70), (110, 74), (90, 70), (70, 74), (50, 72), (36, 92)]
        c.layer(S(dome(100, 92, 64, fr)), hair_col, depth=3, shadow=False)
        for x in (32, 148):
            c.layer(S(rrect(x, 80, 20, 62, 9)), hair_col, depth=3, shadow=False)
    elif hair == "pony":
        fr = [(164, 92), (148, 70), (124, 64), (100, 72), (76, 64), (52, 70), (36, 92)]
        c.layer(S(dome(100, 92, 64, fr)), hair_col, depth=3, shadow=False)
        c.flat(S(heart(166, 96, 13)), PINK_DK)                                          # a bow
    elif hair == "curly":
        sh = dome(100, 92, 60, [(160, 92), (40, 92)])
        for i in range(7):
            a = math.radians(180 + 30 * i)
            sh = sh + circle(100 + 58 * math.cos(a), 92 + 58 * math.sin(a), 15)
        c.layer(S(sh), hair_col, depth=3, shadow=False)
    elif hair == "bun":
        fr = [(164, 92), (146, 74), (122, 68), (100, 70), (78, 68), (54, 74), (36, 92)]
        c.layer(S(circle(100, 30, 17)), hair_col, depth=3, shadow=False)
        c.layer(S(dome(100, 92, 64, fr)), hair_col, depth=3, shadow=False)
    # face
    fx, fy = P(100, 98)
    c.face(fx, fy, 16 * u, mood)
    if glasses:
        for x in (84, 116):
            c.stroke(S(circle(x, 96, 13)), DARK, 2.4 * u)
        c.stroke(S(path([(97, 96), (103, 96)])), DARK, 2.4 * u)


def window_bg(c, x, y, w, h, frame=WOOD, cloud=True):
    """A window drawn into a background: frame, #SKY glass, a cloud, cross bars, a sill."""
    c.layer(rrect(x, y, w, h, 14), frame, depth=5)
    gx, gy, gw, gh = x + 14, y + 14, w - 28, h - 28
    c.flat(rrect(gx, gy, gw, gh, 6), SKY_TOKEN)
    if cloud:
        cx, cy = gx + gw * .32, gy + gh * .66
        c.flat(ellipse(cx, cy, gw * .17, gh * .09) + circle(cx - gw * .05, cy - gh * .06, gw * .08)
               + circle(cx + gw * .06, cy - gh * .08, gw * .09), PAPER, op=.92)
    c.layer(rrect(x + w / 2 - 5, gy, 10, gh, 4), kit.lt(frame, .12), depth=2, shadow=False)
    c.layer(rrect(gx, y + h / 2 - 5, gw, 10, 4), kit.lt(frame, .12), depth=2, shadow=False)
    c.layer(rrect(x - 8, y + h - 6, w + 16, 14, 6), kit.dk(frame, .2), depth=5)


def draw_fishbowl(c, state):
    W, H = c.w - 10, c.h - 10      # 60 x 50
    cx, cy, r = W / 2, H / 2 + 4, W / 2 - 2
    c.layer(circle(cx, cy, r), kit.SKY, depth=3)                                       # the glass bowl
    c.flat(circle(cx, cy, r - 5), kit.lt(kit.SKY, .18))
    c.layer(ellipse(cx, cy - r + 4, r * .5, 4), GREY, depth=2, shadow=False)           # the rim
    c.flat(ellipse(cx - 2, cy + r - 6, r * .55, 4), "#E8C98F")                         # pebbles
    c.flat(ellipse(cx + 1, cy + 2, 8, 5.5), CORAL)                                      # the fish
    c.flat(poly([(cx + 8, cy + 2), (cx + 14, cy - 3), (cx + 14, cy + 7)]), CORAL)
    c.flat(circle(cx - 3, cy + 1, 1.3), DARK)
    c.dots([(cx - 8, cy - 8), (cx - 5, cy - 13)], 1.6, PAPER, op=.9)                   # bubbles
    c.flat(ellipse(cx - r * .45, cy - r * .35, 4, 6).rotate(30, cx - r * .45, cy - r * .35), PAPER, op=.6)


# ---------------------------------------------------------------- background
def draw_bg(c):
    # a pale yellow wall with a soft stripe of mint at child height
    c.flat(rect(0, 0, 600, FLOOR_Y + 20), SCHOOL_WALL)
    for row in range(10):
        y = 40 + row * 50
        for col in range(13):
            x = 30 + col * 48 + (24 if row % 2 else 0)
            if x < 590 and y < FLOOR_Y - 40:
                c.flat(star(x, y, 4.5), kit.dk(SCHOOL_WALL, .08))
    c.flat(rect(0, FLOOR_Y - 60, 600, 46), kit.lt(MINT, .55))
    window_bg(c, 372, 100, 196, 176)
    # the floor: light wood planks
    c.flat(rect(0, FLOOR_Y, 600, 800 - FLOOR_Y), SCHOOL_FLOOR)
    for i in range(1, 7):
        x = i * 86 + 20
        c.stroke(path([(x, FLOOR_Y + 4), (x, 800)]), kit.dk(SCHOOL_FLOOR, .13), 3)
    for i in range(3):
        y = FLOOR_Y + 60 + i * 80
        c.stroke(path([(0, y), (600, y)]), kit.dk(SCHOOL_FLOOR, .09), 2.5)
    c.flat(rect(0, FLOOR_Y, 600, 16), kit.SHADOW, op=.12)
    c.flat(rect(0, FLOOR_Y + 16, 600, 10), kit.SHADOW, op=.05)
    c.layer(rrect(0, FLOOR_Y - 14, 600, 18, 3), MINT_DK, depth=4, shadow=False)
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_blackboard(c, state):
    W, H = c.w - 10, c.h - 10      # 250 x 160
    c.layer(rrect(0, 0, W, H - 14, 12), WOOD, depth=5)                     # the frame
    c.flat(rrect(12, 12, W - 24, H - 38, 6), BOARD)
    # a chalk sun
    sx, sy = 52, 50
    c.stroke(circle(sx, sy, 15), CHALK_YELLOW, 3.5)
    for i in range(8):
        a = math.radians(i * 45)
        c.stroke(path([(sx + 21 * math.cos(a), sy + 21 * math.sin(a)), (sx + 29 * math.cos(a), sy + 29 * math.sin(a))]),
                 CHALK_YELLOW, 3.5)
    c.face(sx, sy, 5, "happy", col=CHALK, blush=PINK)
    # A B C in chalk
    x, y = 112, 40
    c.stroke(path([(x, y + 38), (x + 15, y), (x + 30, y + 38)]), CHALK, 4.5)
    c.stroke(path([(x + 7, y + 25), (x + 23, y + 25)]), CHALK, 4.5)
    x += 48
    c.stroke(path([(x, y), (x, y + 38)]), CHALK, 4.5)
    c.stroke(arc(x, y + 10, 10, -90, 90), CHALK, 4.5)
    c.stroke(arc(x, y + 28, 10, -90, 90), CHALK, 4.5)
    x += 42
    c.stroke(arc(x + 14, y + 19, 17, 40, 320), CHALK, 4.5)
    c.flat(heart(W - 40, H - 46, 12), PINK)                                  # a chalk heart
    # the chalk tray with two sticks of chalk
    c.layer(rrect(20, H - 22, W - 40, 12, 5), WOOD_DK, depth=4)
    c.layer(rrect(40, H - 26, 26, 7, 3), CHALK, depth=2, shadow=False)
    c.layer(rrect(74, H - 26, 26, 7, 3), PINK, depth=2, shadow=False)


def draw_cubby(c, state):
    W, H = c.w - 10, c.h - 10      # 100 x 230
    c.layer(rrect(0, 0, W, H, 10), WOOD, depth=5)                          # the case
    c.face(W / 2, 17, 6.5, "happy")
    marks = (("star", YELLOW), ("heart", PINK_DK), ("flower", LAVENDER_DK))
    for i, (kind, col) in enumerate(marks):
        y = 34 + i * 64
        c.flat(rrect(8, y, W - 16, 56, 6), CREAM)
        c.flat(rrect(8, y + 46, W - 16, 10, 4, rtl=0, rtr=0), kit.dk(CREAM, .12))
        cx, cy = W / 2, y + 26
        if kind == "star":
            c.layer(star(cx, cy, 15), col, depth=2, shadow=False)
        elif kind == "heart":
            c.layer(heart(cx, cy + 2, 28), col, depth=2, shadow=False)
        else:
            sh = Shape()
            for k in range(5):
                a = math.radians(-90 + 72 * k)
                sh = sh + circle(cx + 9 * math.cos(a), cy + 9 * math.sin(a), 6.5)
            c.layer(sh, col, depth=2, shadow=False)
            c.flat(circle(cx, cy, 5), YELLOW)
        if i < 2:
            c.layer(rrect(4, y + 58, W - 8, 6, 3), WOOD_DK, depth=2, shadow=False)


def draw_teacher(c, state):
    puppet(c, skin=SKIN[1], shirt=LAVENDER, pants="#7A6CB0", hair="bun", hair_col=HAIR_BLONDE, wave=True,
           glasses=True, tag=True)


def draw_classmate_1(c, state):
    puppet(c, skin=SKIN[0], shirt=CORAL, pants="#7F8EC9", hair="short", hair_col=HAIR_DARK, wave=True)


def draw_classmate_2(c, state):
    puppet(c, skin=SKIN[2], shirt=MINT, pants="#D98BA3", hair="pony", hair_col=HAIR_AUBURN, mood="happy")


def draw_mat(c, state):
    W, H = c.w - 10, c.h - 10      # 170 x 60
    c.layer(rrect(0, 18, W, 40, 14), kit.lt(LAVENDER, .15), depth=3, shadow_op=.14)   # the mat
    c.flat(rrect(0, 44, W, 10, 4, rtl=0, rtr=0), kit.dk(LAVENDER, .06), op=.6)
    c.dots([(60 + i * 24, 36) for i in range(4)], 3.2, PAPER)
    c.layer(rrect(8, 10, 46, 30, 10), PINK, depth=3)                                    # the pillow
    c.flat(star(31, 25, 6), PAPER)


def draw_toyshelf(c, state):
    W, H = c.w - 10, c.h - 10      # 130 x 90
    c.layer(rrect(0, 0, W, H, 8), WOOD, depth=5)                           # the case
    c.face(W / 2, 12, 5.5, "happy")
    for x in (8, W / 2 + 4):
        c.flat(rrect(x, 24, W / 2 - 12, 52, 5), kit.dk(WOOD, .18))
    # blocks in a little pyramid
    blocks = [(14, 54, PINK), (36, 54, kit.SKY), (25, 34, YELLOW)]
    for x, y, col in blocks:
        c.layer(rrect(x, y, 20, 20, 3), col, depth=2, shadow=False)
    c.flat(circle(24, 64, 4), PAPER)
    c.flat(star(46, 64, 4.5), PAPER)
    c.flat(heart(35, 45, 8), PAPER)
    # a ball
    bx, by = W * .75 + 2, 56
    c.layer(circle(bx, by, 17), CORAL, depth=3, shadow=False)
    c.flat(rrect(bx - 17, by - 4, 34, 8, 4), YELLOW)
    c.flat(circle(bx - 6, by - 8, 3.5), PAPER, op=.7)
    c.layer(rrect(W / 2 - 3, 20, 6, 58, 3), WOOD_DK, depth=2, shadow=False)   # the divider


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    """Children's drawings pinned up: three sheets with crayon pictures."""
    W, H = c.w - 10, c.h - 10      # 170 x 80
    sheets = ((4, 10, -5, CORAL), (62, 6, 0, MINT_DK), (120, 12, 5, YELLOW))
    for x, y, ang, pin in sheets:
        cx, cy = x + 24, y + 30

        def R(sh):
            return sh.rotate(ang, cx, cy)

        c.layer(R(rrect(x, y, 48, 60, 4)), PAPER, depth=2)
        if pin is CORAL:                                                   # a house
            c.flat(R(rrect(x + 12, y + 30, 24, 20, 2)), YELLOW)
            c.flat(R(poly([(x + 8, y + 31), (x + 24, y + 14), (x + 40, y + 31)])), CORAL)
            c.flat(R(rrect(x + 20, y + 38, 8, 12, 2)), kit.SKY)
        elif pin is MINT_DK:                                               # a flower and the sun
            c.flat(R(circle(x + 36, y + 16, 7)), YELLOW)
            c.stroke(R(path([(x + 18, y + 52), (x + 18, y + 34)])), LEAF_DK, 2.5)
            for k in range(5):
                a = math.radians(-90 + 72 * k)
                c.flat(R(circle(x + 18 + 7 * math.cos(a), y + 30 + 7 * math.sin(a), 4.5)), PINK_DK)
            c.flat(R(circle(x + 18, y + 30, 3.5)), YELLOW)
        else:                                                              # a rainbow
            for r, col in ((20, CORAL), (15, YELLOW), (10, MINT_DK)):
                c.stroke(R(arc(x + 24, y + 44, r, 180, 360)), col, 4)
            c.flat(R(circle(x + 10, y + 46, 5) + circle(x + 16, y + 44, 6)), PAPER)
        c.layer(R(circle(cx, y + 4, 4.5)), pin, depth=2, shadow=False)     # the pin


def draw_deco_2(c, state):
    """A paper chain hung across the room."""
    W, H = c.w - 10, c.h - 10      # 470 x 60
    cols = [PINK, YELLOW, MINT, LAVENDER, CORAL, kit.SKY]
    n_links = 29
    for i in range(n_links):
        x = 8 + (W - 16) * i / (n_links - 1)
        y = 10 + 30 * math.sin(math.pi * (x - 8) / (W - 16))
        col = cols[i % 6]
        if i % 2 == 0:
            c.layer(ellipse(x, y, 11, 8) + ellipse(x, y, 7, 4), col, depth=2, shadow=False, rule="evenodd")
        else:
            c.layer(rrect(x - 3.5, y - 10, 7, 20, 3.5), col, depth=2, shadow=False)
    for x in (8, W - 8):
        c.layer(circle(x, 8, 4.5), GREY, depth=2, shadow=False)            # the pins


def draw_deco_3(c, state):
    draw_fishbowl(c, state)


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "school", "幼兒園", "kindergarten",
    exits={"back": "street"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(408, 688, 120, 160),
    bg=draw_bg,
    things=[
        Thing("blackboard", "黑板", "blackboard", 230, 180, 260, 170, z=5, draw=draw_blackboard),
        Thing("cubby", "小格子櫃", "cubbies", 65, 400, 110, 240, z=8, draw=draw_cubby),
        Thing("teacher", "老師", "teacher", 520, 560, 150, 195, z=12, draw=draw_teacher),
        Thing("mat", "午睡墊", "nap mat", 400, 755, 180, 70, z=18, draw=draw_mat),
        Thing("toyshelf", "玩具架", "toy shelf", 80, 735, 140, 100, z=22, draw=draw_toyshelf),
        Thing("classmate_1", "同學", "classmate", 85, 600, 120, 156, z=25, draw=draw_classmate_1),
        Thing("classmate_2", "同學", "classmate", 545, 700, 110, 143, z=30, draw=draw_classmate_2),
    ],
    decos=[
        Deco("deco_1", "小朋友的畫", "children's drawings", 470, 370, 180, 90, draw=draw_deco_1),
        Deco("deco_2", "彩色紙鍊", "paper chain", 300, 60, 480, 70, draw=draw_deco_2),
        Deco("deco_3", "金魚缸", "goldfish bowl", 65, 250, 70, 60, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
