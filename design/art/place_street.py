"""小街 the street outside the front door: the hub that leads to every other place.

Scene pixels are 600 x 800. The sky fills the top 440 px (#SKY, recoloured by the app) with paper
clouds; below it a far pavement, the road with a zebra crossing, the near pavement and the grass the
avatar stands on (stand box 204 x 400, feet at y 688, kept clear). The things are the doors to the
places: each is a small building front with a face and a big picture sign, laid out in two rows left
and right of the avatar (back row on the far pavement, front row on the near grass), the bus parked
in front of the avatar's feet. Every `draw_*(c, state)` paints into a kit.Ctx the size of the
thing's box and leaves ~10 px free on the right and bottom for the paper shadow.
"""
import math

import kit
from kit import (BLUSH, CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH,
                 PEACH_DK, PINK, PINK_DK, SKY_TOKEN, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, circle, cloud, ellipse, heart,
                 path, poly, rect, rrect, star)
import scene
from scene import Box, Deco, Thing

HORIZON = 440                 # where the sky ends and the far pavement begins
ROAD_Y, ROAD_H = 470, 86      # the road
WALK_Y = ROAD_Y + ROAD_H      # the near pavement (556 .. 612)
GRASS_Y = WALK_Y + 56

GRASS = kit.lt(LEAF, .30)
GRASS_DK = kit.lt(LEAF, .12)
WALK = "#EAE2D8"
ROAD = "#B9B3BC"
CLOUD_EDGE = "#E4DDD3"
RED = "#F26B60"
GREEN = "#8BD48F"
HOUSING = "#847A8F"


# ---------------------------------------------------------------- shared pieces
def draw_cloud(c, cx, cy, w, h):
    c.layer(cloud(cx, cy, w, h), PAPER, depth=3, edge_col=CLOUD_EDGE, shadow_op=.07)


def door(c, cx, bottom, w, h, col, face_col=DARK, mood="happy", knob=YELLOW):
    """A door with a round top, a knob and a little face: the welcoming face of every building."""
    c.layer(rrect(cx - w / 2, bottom - h, w, h, w / 2, rbl=0, rbr=0), col, depth=4)
    c.face(cx, bottom - h * .48, w * .17, mood, col=face_col)
    c.flat(circle(cx + w * .3, bottom - h * .3, w * .07), knob)


def window(c, x, y, w, h, frame=PAPER, r=6):
    """A framed window; the glass is the sky placeholder, so it goes dark with the evening."""
    c.layer(rrect(x, y, w, h, r), frame, depth=3, shadow=False)
    c.flat(rrect(x + 4, y + 4, w - 8, h - 8, max(2, r - 3)), SKY_TOKEN)
    c.flat(rrect(x + w / 2 - 1.5, y + 4, 3, h - 8, 1.5), frame)
    c.flat(rrect(x + 4, y + h / 2 - 1.5, w - 8, 3, 1.5), frame)


def little_tree(c, cx, bottom, s, crown=LEAF_DK):
    c.layer(rrect(cx - s * .09, bottom - s * .55, s * .18, s * .55, s * .06), WOOD_DK, depth=2, shadow=False)
    c.layer(circle(cx, bottom - s * .66, s * .36), crown, depth=2, shadow=False)


def little_slide(c, x, bottom, s):
    """A tiny slide for the park sign: a ladder, a platform and a chute."""
    c.stroke(path([(x + s * .2, bottom), (x + s * .2, bottom - s * .62)]), WOOD_DK, s * .09)
    for i in range(3):
        y = bottom - s * .15 - i * s * .16
        c.stroke(path([(x + s * .08, y), (x + s * .32, y)]), WOOD_DK, s * .07)
    chute = poly([(x + s * .14, bottom - s * .74), (x + s * .42, bottom - s * .74), (x + s * .98, bottom - s * .04),
                  (x + s * .98, bottom + s * .1), (x + s * .74, bottom + s * .1), (x + s * .14, bottom - s * .52)])
    c.layer(chute, CORAL, depth=2, shadow=False)


# ---------------------------------------------------------------- background
def draw_bg(c):
    # the sky: a big placeholder the app recolours for morning, noon and night, with paper clouds
    c.flat(rect(0, 0, 600, HORIZON + 10), SKY_TOKEN)
    draw_cloud(c, 120, 118, 170, 62)
    draw_cloud(c, 440, 72, 130, 50)
    draw_cloud(c, 540, 214, 104, 42)
    draw_cloud(c, 250, 232, 90, 38)
    # a far hedge of round bushes along the horizon, two rows of paper for depth
    far = kit.Shape()
    r = kit.rnd("street", "hedge-back")
    for i in range(16):
        x = -10 + i * 41 + r.uniform(-6, 6)
        far = far + circle(x, HORIZON - 4, 26 + r.uniform(-4, 6))
    c.layer(far, kit.lt(LEAF, .42), depth=3, shadow=False, edge_col=kit.lt(LEAF, .22))
    near = kit.Shape()
    r = kit.rnd("street", "hedge-front")
    for i in range(14):
        x = 10 + i * 46 + r.uniform(-6, 6)
        near = near + circle(x, HORIZON + 4, 20 + r.uniform(-3, 5))
    c.layer(near, LEAF, depth=3, shadow=False)
    # the far pavement: a strip of paper standing on the road, its kerb the paper's edge
    c.layer(rect(0, HORIZON, 600, ROAD_Y - HORIZON), WALK, depth=4, shadow=False, edge_col=kit.dk(WALK, .28))
    # the road, the dashed middle line, the zebra crossing by the traffic light
    c.flat(rect(0, ROAD_Y, 600, ROAD_H), ROAD)
    for x in range(14, 600, 50):
        c.flat(rrect(x, ROAD_Y + ROAD_H / 2 - 3, 26, 6, 3), YELLOW, op=.9)
    for i in range(6):
        c.flat(rrect(394 + i * 21, ROAD_Y + 6, 13, ROAD_H - 12, 4), PAPER, op=.95)
    c.flat(rect(0, ROAD_Y, 600, 8), kit.SHADOW, op=.10)
    # the near pavement with its kerb, then the grass the avatar stands on
    c.layer(rect(0, WALK_Y, 600, GRASS_Y - WALK_Y), WALK, depth=4, shadow=False, edge_col=kit.dk(WALK, .28))
    c.flat(rect(0, GRASS_Y, 600, 800 - GRASS_Y), GRASS)
    c.flat(rect(0, GRASS_Y, 600, 6), kit.SHADOW, op=.08)
    r = kit.rnd("street", "grass")
    for i in range(7):
        x, y = r.uniform(30, 570), r.uniform(GRASS_Y + 30, 780)
        c.flat(ellipse(x, y, r.uniform(26, 44), r.uniform(7, 11)), GRASS_DK, op=.55)
    r = kit.rnd("street", "flowers")
    for i in range(22):
        x, y = r.uniform(16, 584), r.uniform(GRASS_Y + 16, 790)
        col = (PINK_DK, PAPER, YELLOW)[i % 3]
        c.dots([(x + 4.2 * math.cos(a), y + 4.2 * math.sin(a)) for a in [k * 2 * math.pi / 5 for k in range(5)]], 3, col)
        c.flat(circle(x, y, 2.4), YELLOW if col != YELLOW else CORAL)
    # the page's side edges (the book's gutter and outer edge), very soft
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- the doors to the places
def draw_home(c, state):
    W, H = c.w - 10, c.h - 10      # 134 x 190: our house, cream walls and a red roof, a heart over the door
    c.layer(rrect(10, 74, W - 20, H - 74, 8), CREAM, depth=5)                          # the walls
    c.layer(poly([(0, 82), (W / 2, 6), (W, 82)]), CORAL, depth=5)                       # the roof
    c.layer(rrect(W - 44, 22, 16, 30, 3), kit.dk(CORAL, .2), depth=3, shadow=False)     # the chimney
    c.flat(ellipse(W - 36, 14, 9, 6), PAPER, op=.85)                                    # a puff of smoke
    c.flat(ellipse(W - 28, 6, 6, 4), PAPER, op=.7)
    c.layer(circle(W / 2, 108, 19), PAPER, depth=3)                                     # the sign: a heart
    c.flat(heart(W / 2, 110, 24), PINK_DK)
    window(c, 18, 96, 30, 30, frame=WOOD)
    window(c, W - 48, 96, 30, 30, frame=WOOD)
    door(c, W / 2, H, 46, 66, WOOD)
    for x in (16, W - 32):                                                              # flower pots by the door
        c.layer(rrect(x, H - 18, 16, 18, 4), PEACH_DK, depth=2, shadow=False)
        c.flat(circle(x + 8, H - 24, 7), LEAF)
        c.flat(circle(x + 8, H - 26, 3.5), PINK_DK)


def draw_park(c, state):
    W, H = c.w - 10, c.h - 10      # 134 x 190: the park gate: a hedge, a tree, two posts and an arch with the sign
    c.layer(circle(W - 36, 78, 32), LEAF_DK, depth=4, shadow=False)                     # a tree behind the hedge
    c.layer(rrect(W - 44, 100, 16, 50, 5), WOOD_DK, depth=2, shadow=False)
    c.layer(cloud(W / 2, 134, W - 24, 70, puffs=5), LEAF, depth=5)                      # the hedge
    c.face(W / 2 + 4, 132, 9, "happy")
    for x in (6, W - 30):                                                               # the gate posts
        c.layer(rrect(x, 54, 24, H - 54, 6), WOOD, depth=4)
        c.layer(rrect(x - 3, 48, 30, 12, 4), WOOD_DK, depth=3, shadow=False)
    c.layer(rrect(8, 148, W - 16, 8, 4), WOOD_DK, depth=2, shadow=False)                # the little fence
    for i in range(6):
        x = 22 + i * (W - 50) / 5
        c.layer(rrect(x - 5, 140, 10, H - 140, 5, rbl=1, rbr=1), PAPER, depth=2, shadow=False)
    c.layer(rrect(2, 10, W - 4, 48, 24, rbl=8, rbr=8), MINT_DK, depth=5)                # the arch
    c.flat(rrect(12, 18, W - 24, 32, 14), PAPER)                                        # the sign board
    little_tree(c, 40, 46, 30)
    little_slide(c, 62, 42, 46)
    c.flat(heart(W / 2 + 2, 6, 10), PINK_DK)                                            # a heart on the arch top


def draw_school(c, state):
    W, H = c.w - 10, c.h - 10      # 140 x 190: the yellow kindergarten with a bell and a sign of blocks
    c.layer(rrect(8, 74, W - 16, H - 74, 8), YELLOW, depth=5)                           # the walls
    c.layer(poly([(0, 84), (W / 2, 24), (W, 84)]), PEACH_DK, depth=5)                   # the roof
    c.flat(poly([(W / 2 - 16, 84), (W / 2 + 16, 84), (W / 2 + 10, 72), (W / 2 - 10, 72)]), kit.dk(PEACH_DK, .2))
    c.layer(rrect(W / 2 - 11, 4, 22, 22, 11, rbl=4, rbr=4), YELLOW, depth=3)             # the bell on the peak
    c.flat(circle(W / 2, 26, 3.5), WOOD_DEEP)
    c.flat(rrect(W / 2 - 2, 0, 4, 6, 2), WOOD_DEEP)
    c.face(W / 2, 96, 8, "happy")
    window(c, 16, 88, 28, 28, frame=PAPER)
    window(c, W - 44, 88, 28, 28, frame=PAPER)
    blocks = ((W / 2 - 34, PINK, "star"), (W / 2 - 10, MINT, "heart"), (W / 2 + 14, LAVENDER, "dot"))
    for x, col, mark in blocks:                                                         # the sign: three blocks
        c.layer(rrect(x, 112, 20, 20, 3), col, depth=3, shadow=False)
        if mark == "star":
            c.flat(star(x + 10, 122, 7), PAPER)
        elif mark == "heart":
            c.flat(heart(x + 10, 123, 11), PAPER)
        else:
            c.flat(circle(x + 10, 122, 5), PAPER)
    door(c, W / 2, H, 42, 54, CORAL, knob=PAPER)
    c.layer(rrect(W / 2 - 28, H - 4, 56, 4, 2), kit.dk(YELLOW, .25), depth=0, shadow=False)   # the step


def draw_market(c, state):
    W, H = c.w - 10, c.h - 10      # 108 x 180: a mint shop with a striped awning and an apple sign
    c.layer(rrect(4, 56, W - 8, H - 56, 6), MINT, depth=5)                              # the shop
    c.layer(rrect(W / 2 - 32, 8, 64, 46, 14), PAPER, depth=4)                           # the sign board
    c.layer(circle(W / 2, 32, 15), RED, depth=2, shadow=False)                          # the apple
    c.flat(circle(W / 2 - 5, 27, 3.5), PAPER, op=.6)
    c.stroke(path([(W / 2, 18), (W / 2 + 2, 11)]), WOOD_DEEP, 2.5)
    c.flat(ellipse(W / 2 + 8, 14, 6, 3.2).rotate(-30, W / 2 + 8, 14), LEAF)
    c.layer(rrect(0, 58, W, 24, 6), PAPER, depth=4)                                     # the awning
    for i in range(0, 8, 2):
        c.flat(rect(i * W / 8, 58, W / 8, 24), CORAL)
    for i in range(8):
        c.flat(circle(W / 16 + i * W / 8, 82, W / 16), CORAL if i % 2 == 0 else PAPER)
    c.layer(rrect(12, 96, W - 24, 42, 6), PAPER, depth=3, shadow=False)                 # the shop window
    c.flat(rrect(16, 100, W - 32, 34, 4), SKY_TOKEN)
    c.flat(rrect(16, 126, W - 32, 8, 2), WOOD)                                          # the display shelf
    c.flat(circle(30, 119, 7), RED)                                                     # fruit in the window
    c.flat(circle(W / 2, 119, 7), YELLOW)
    c.flat(circle(W - 30, 117, 4) + circle(W - 36, 122, 4) + circle(W - 24, 122, 4), LAVENDER_DK)
    door(c, W / 2, H, 36, 40, PEACH_DK)


def draw_clinic(c, state):
    W, H = c.w - 10, c.h - 10      # 106 x 180: a white clinic with a red cross on the roof and a bandage sign
    c.layer(rrect(2, 46, W - 4, H - 46, 8), PAPER, depth=5)                             # the building
    c.layer(rrect(0, 42, W, 14, 6), MINT, depth=4)                                      # the roof band
    cross = rrect(W / 2 - 6, 2, 12, 36, 4) + rrect(W / 2 - 18, 14, 36, 12, 4)
    c.layer(cross, RED, depth=4)                                                        # the red cross
    c.layer(rrect(W / 2 - 34, 66, 68, 36, 10), kit.lt(MINT, .45), depth=3, shadow=False)   # the sign: a bandage
    band = rrect(W / 2 - 24, 77, 48, 14, 7).rotate(-22, W / 2, 84)
    c.layer(band, PEACH, depth=2, shadow=False)
    c.flat(rrect(W / 2 - 7, 77, 14, 14, 2).rotate(-22, W / 2, 84), PAPER)
    c.dots([(W / 2 - 16, 82), (W / 2 - 15, 88), (W / 2 + 15, 80), (W / 2 + 16, 86)], 1.4, kit.dk(PEACH, .3))
    window(c, 12, 110, 26, 26, frame=MINT, r=5)
    window(c, W - 38, 110, 26, 26, frame=MINT, r=5)
    door(c, W / 2, H, 34, 44, MINT_DK, knob=PAPER)
    c.flat(heart(W / 2, 126, 9), PINK_DK)                                               # a small heart over the door


def draw_traffic_light(c, state):
    W, H = c.w - 10, c.h - 10      # 66 x 214: red on top, green below, each with a little face
    c.layer(rrect(W / 2 - 16, H - 14, 32, 14, 6), kit.dk(GREY, .3), depth=3)            # the base
    c.layer(rrect(W / 2 - 6, 92, 12, H - 100, 5), GREY, depth=3)                        # the pole
    c.layer(rrect(W / 2 - 25, 2, 50, 98, 16), HOUSING, depth=5)                         # the housing
    for cy, col, mood in ((28, RED, "sleepy"), (72, GREEN, "happy")):
        c.flat(ellipse(W / 2, cy - 19, 20, 5), kit.dk(HOUSING, .25))                     # the hood
        c.layer(circle(W / 2, cy, 16), col, depth=0, shadow=False)
        c.flat(circle(W / 2 - 6, cy - 6, 4), PAPER, op=.45)
        c.face(W / 2, cy + 1, 5.5, mood, col=DARK, blush=kit.lt(col, .3))


def draw_bus(c, state):
    W, H = c.w - 10, c.h - 10      # 190 x 98: the round yellow kindergarten bus, parked, with a face at the front
    body = rrect(2, 8, W - 4, 70, 22, rtr=34, rbr=30)
    c.layer(body, YELLOW, depth=5)
    c.flat(rrect(12, 8, W - 50, 10, 5), PAPER, op=.8)                                   # the roof stripe
    c.flat(rrect(6, 54, W - 46, 7, 3.5), MINT_DK)                                       # the side stripe
    for x in (16, 54):                                                                  # the windows
        c.layer(rrect(x, 22, 30, 26, 7), PAPER, depth=2, shadow=False)
        c.flat(rrect(x + 3, 25, 24, 20, 5), SKY_TOKEN)
    c.layer(rrect(94, 24, 28, 48, 7), kit.dk(YELLOW, .18), depth=2, shadow=False)        # the door
    c.flat(rrect(98, 28, 20, 18, 4), SKY_TOKEN)
    c.flat(rrect(107, 48, 2, 22, 1), kit.dk(YELLOW, .4))
    c.layer(rrect(132, 20, 44, 32, 10, rtr=20), PAPER, depth=2, shadow=False)           # the windscreen
    c.flat(rrect(135, 23, 38, 26, 8, rtr=17), SKY_TOKEN)
    c.face(154, 62, 7.5, "happy")
    c.layer(circle(W - 10, 64, 7), PAPER, depth=0, shadow=False)                        # the headlight
    c.flat(circle(W - 10, 64, 4), CREAM)
    c.layer(rrect(126, 72, W - 128, 8, 4), GREY, depth=2, shadow=False)                 # the bumper
    for x in (44, 138):                                                                 # the wheels
        c.layer(circle(x, 80, 15), "#5E4F47", depth=3, shadow_op=.15)
        c.flat(circle(x, 80, 7), GREY)
        c.flat(circle(x, 80, 2.5), kit.dk(GREY, .3))
    c.flat(circle(W - 36, 42, 2.6) + circle(W - 36, 50, 2.6), kit.dk(YELLOW, .4))       # the mirror hinge dots


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    W, H = c.w - 10, c.h - 10      # 46 x 134: a lamp post with a basket of flowers
    c.layer(ellipse(W / 2, H - 6, 16, 6), kit.dk(GREY, .3), depth=2, shadow=False)      # the foot
    c.layer(rrect(W / 2 - 4, 26, 8, H - 32, 4), kit.dk(GREY, .15), depth=2)              # the post
    c.layer(poly([(W / 2 - 14, 10), (W / 2 + 14, 10), (W / 2 + 10, 30), (W / 2 - 10, 30)]), CREAM, depth=3)   # the lamp
    c.flat(rrect(W / 2 - 16, 6, 32, 7, 3), kit.dk(GREY, .3))
    c.flat(circle(W / 2, 22, 5), YELLOW, op=.9)
    c.layer(rrect(W / 2 - 17, 62, 34, 18, 8, rtl=3, rtr=3), WOOD_DK, depth=3)           # the hanging basket
    c.stroke(path([(W / 2 - 14, 62), (W / 2, 48), (W / 2 + 14, 62)]), WOOD_DEEP, 1.8)
    for x, col in ((W / 2 - 12, PINK_DK), (W / 2, YELLOW), (W / 2 + 12, LAVENDER_DK)):
        c.flat(circle(x, 56, 6.5), LEAF)
        c.dots([(x + 4 * math.cos(a), 54 + 4 * math.sin(a)) for a in [k * 2 * math.pi / 5 for k in range(5)]], 3, col)
        c.flat(circle(x, 54, 2.2), CREAM)


def draw_deco_2(c, state):
    W, H = c.w - 10, c.h - 10      # 550 x 80: bunting across the sky
    pts = [(x, 6 + 30 * math.sin(math.pi * x / W)) for x in range(0, int(W) + 1, 10)]
    c.stroke(path(pts), DARK, 2.5)
    cols = [PINK, YELLOW, MINT, LAVENDER, CORAL, PAPER]
    for i in range(13):
        x = W * (i + .5) / 13
        y = 6 + 30 * math.sin(math.pi * x / W)
        flag = poly([(x - 15, y), (x + 15, y), (x, y + 34)])
        c.layer(flag, cols[i % 6], depth=2, shadow_op=.12)
        c.flat(circle(x, y + 12, 3.5), PAPER if cols[i % 6] != PAPER else PINK_DK)


def draw_deco_3(c, state):
    W, H = c.w - 10, c.h - 10      # 54 x 80: a red letter box on a post
    c.layer(rrect(W / 2 - 5, 44, 10, H - 44, 4), WOOD_DK, depth=2)                      # the post
    c.layer(rrect(2, 2, W - 4, 46, 16, rbl=6, rbr=6), RED, depth=4)                     # the box
    c.flat(rrect(10, 10, W - 20, 6, 3), kit.dk(RED, .35))                               # the slot
    c.layer(rrect(14, 20, W - 28, 16, 2), PAPER, depth=0, shadow=False)                 # a letter peeking out
    c.flat(heart(W / 2, 29, 8), PINK_DK)
    c.face(W / 2, 40, 4.5, "smile", col=PAPER, blush=kit.lt(RED, .3))


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "street", "小街", "street",
    exits={"back": "entrance"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(440, 598, 108, 144),
    bg=draw_bg,
    things=[
        Thing("park", "公園", "park", 76, 352, 144, 200, z=10, draw=draw_park),
        Thing("school", "幼兒園", "kindergarten", 434, 352, 150, 200, z=10, draw=draw_school),
        Thing("traffic_light", "紅綠燈", "traffic light", 556, 352, 76, 224, z=12, draw=draw_traffic_light),
        Thing("home", "我們家", "our home", 76, 690, 144, 200, z=20, draw=draw_home),
        Thing("market", "超市", "supermarket", 418, 700, 118, 190, z=20, draw=draw_market),
        Thing("clinic", "診所", "clinic", 538, 700, 116, 190, z=20, draw=draw_clinic),
        Thing("bus", "娃娃車", "school bus", 252, 746, 200, 108, z=24, draw=draw_bus),
    ],
    decos=[
        Deco("deco_1", "路燈上的花", "flowers on the lamp post", 118, 528, 56, 144, draw=draw_deco_1),
        Deco("deco_2", "彩旗", "bunting", 300, 70, 560, 90, draw=draw_deco_2),
        Deco("deco_3", "信箱", "letter box", 40, 556, 64, 90, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
