"""公園 the park: a big lawn under the sky, with a slide, a swing, a sandbox, a tree and a bench.

Scene pixels are 600 x 800. The sky fills the top 440 px (#SKY, recoloured by the app) with paper
clouds; a far hedge stands along the horizon and the lawn fills the rest. The avatar stands in the
middle (stand box 204 x 400, feet at y 688, kept clear): the bench and the slide are on the left, the
tree and the swing on the right, and the sandbox sits in front of the avatar's feet. Every
`draw_*(c, state)` paints into a kit.Ctx the size of the thing's box and leaves ~10 px free on the
right and bottom for the paper shadow.
"""
import math

import kit
from kit import (BLUSH, CORAL, CREAM, DARK, GREY, LAVENDER, LAVENDER_DK, LEAF, LEAF_DK, MINT, MINT_DK, PAPER, PEACH,
                 PEACH_DK, PINK, PINK_DK, SKY_TOKEN, WOOD, WOOD_DEEP, WOOD_DK, YELLOW, circle, cloud, ellipse, heart,
                 path, poly, rect, rrect, star)
import scene
from scene import Box, Deco, Thing

HORIZON = 445

GRASS = kit.lt(LEAF, .30)
GRASS_DK = kit.lt(LEAF, .12)
SAND = "#F6E3BE"
CLOUD_EDGE = "#E4DDD3"
RED = "#F26B60"


# ---------------------------------------------------------------- shared pieces
def draw_cloud(c, cx, cy, w, h):
    c.layer(cloud(cx, cy, w, h), PAPER, depth=3, edge_col=CLOUD_EDGE, shadow_op=.07)


def daisy(c, x, y, r, col, centre=YELLOW):
    c.dots([(x + r * 1.4 * math.cos(a), y + r * 1.4 * math.sin(a)) for a in [k * 2 * math.pi / 5 for k in range(5)]], r, col)
    c.flat(circle(x, y, r * .8), centre)


# ---------------------------------------------------------------- background
def draw_bg(c):
    # the sky with paper clouds
    c.flat(rect(0, 0, 600, HORIZON + 10), SKY_TOKEN)
    draw_cloud(c, 110, 90, 160, 60)
    draw_cloud(c, 330, 150, 120, 46)
    draw_cloud(c, 560, 60, 110, 44)
    draw_cloud(c, 470, 250, 90, 36)
    # the far hedge: two rows of round bushes along the horizon, the back row paler
    far = kit.Shape()
    r = kit.rnd("park", "hedge-back")
    for i in range(16):
        x = -10 + i * 41 + r.uniform(-6, 6)
        far = far + circle(x, HORIZON - 10, 30 + r.uniform(-4, 8))
    c.layer(far, kit.lt(LEAF, .42), depth=3, shadow=False, edge_col=kit.lt(LEAF, .22))
    near = kit.Shape()
    r = kit.rnd("park", "hedge-front")
    for i in range(14):
        x = 10 + i * 46 + r.uniform(-6, 6)
        near = near + circle(x, HORIZON, 22 + r.uniform(-3, 6))
    c.layer(near, LEAF, depth=4, shadow=False)
    # the lawn, lying flat: lighter patches, a sandy path curving past the avatar's feet, daisies
    c.flat(rect(0, HORIZON, 600, 800 - HORIZON), GRASS)
    c.flat(rect(0, HORIZON + 2, 600, 8), kit.SHADOW, op=.08)
    r = kit.rnd("park", "grass")
    for i in range(10):
        x, y = r.uniform(30, 570), r.uniform(HORIZON + 40, 780)
        c.flat(ellipse(x, y, r.uniform(30, 50), r.uniform(8, 13)), GRASS_DK, op=.5)
    pts = [(x, 696 + 24 * math.sin(math.pi * (x + 60) / 320)) for x in range(-20, 640, 20)]
    c.stroke(path(pts), SAND, 30, op=.9)
    c.stroke(path(pts), kit.dk(SAND, .12), 30, op=.18)
    r = kit.rnd("park", "daisies")
    for i in range(26):
        x, y = r.uniform(16, 584), r.uniform(HORIZON + 24, 790)
        daisy(c, x, y, 2.8, (PAPER, PINK_DK, PAPER, LAVENDER)[i % 4], YELLOW)
    r = kit.rnd("park", "tufts")
    for i in range(18):
        x, y = r.uniform(20, 580), r.uniform(HORIZON + 30, 790)
        c.stroke(path([(x - 5, y + 4), (x - 2, y - 6)]), GRASS_DK, 2.2)
        c.stroke(path([(x + 1, y + 4), (x + 2, y - 7)]), GRASS_DK, 2.2)
        c.stroke(path([(x + 6, y + 4), (x + 8, y - 4)]), GRASS_DK, 2.2)
    # the page's side edges (the book's gutter and outer edge), very soft
    c.flat(rect(0, 0, 12, 800), kit.SHADOW, op=.06)
    c.flat(rect(588, 0, 12, 800), kit.SHADOW, op=.06)


# ---------------------------------------------------------------- things
def draw_tree(c, state):
    W, H = c.w - 12, c.h - 12      # 220 x 288: a big round paper tree with a face on its trunk
    c.layer(rrect(W / 2 - 22, 160, 44, H - 160, 14, rtl=4, rtr=4), WOOD_DK, depth=5)   # the trunk
    c.layer(ellipse(W / 2, H - 4, 50, 10), WOOD_DK, depth=3, shadow=False)              # the roots
    c.face(W / 2, 218, 9, "happy")
    crown = circle(W / 2, 102, 98) + circle(W / 2 - 62, 136, 52) + circle(W / 2 + 62, 136, 52)
    c.layer(crown, LEAF_DK, depth=6)                                                    # the crown
    c.layer(circle(W / 2 - 30, 86, 50) + circle(W / 2 + 36, 104, 42), LEAF, depth=3, shadow=False)
    c.flat(ellipse(W / 2 - 30, 54, 30, 12).rotate(-18, W / 2 - 30, 54), kit.lt(LEAF, .3), op=.75)   # the light on top
    r = kit.rnd("park", "fruit")
    for i in range(7):
        a = 2 * math.pi * i / 7 + .4
        x, y = W / 2 + 70 * math.cos(a), 108 + 58 * math.sin(a)
        c.layer(circle(x, y, 8), RED, depth=2, shadow=False)                            # red fruit
        c.flat(circle(x - 2.5, y - 2.5, 2.4), PAPER, op=.7)


def draw_slide(c, state):
    W, H = c.w - 10, c.h - 10      # 134 x 220: ladder on the left, a face on the tower, the chute to the right
    c.layer(rrect(10, 40, 12, H - 40, 5), WOOD_DK, depth=3)                             # the ladder's rails
    c.layer(rrect(40, 40, 12, H - 40, 5), WOOD_DK, depth=3)
    for i in range(5):
        y = 70 + i * 28
        c.layer(rrect(6, y, 50, 9, 4), WOOD, depth=2, shadow=False)                     # the rungs
    c.layer(rrect(50, 20, 12, H - 20, 5), MINT_DK, depth=3)                             # the posts under the tower
    c.layer(rrect(W - 34, 150, 10, H - 150, 4), MINT_DK, depth=3)
    chute = poly([(44, 40), (84, 40), (W, H - 36), (W, H - 10), (W - 24, H - 10), (44, 78)])
    c.layer(chute, CORAL, depth=5)                                                      # the chute
    c.flat(poly([(50, 52), (78, 52), (W - 6, H - 30), (W - 20, H - 28), (50, 72)]), kit.lt(CORAL, .35), op=.6)
    c.layer(poly([(40, 30), (88, 30), (88, 46), (40, 46)]), kit.lt(MINT_DK, .15), depth=3)   # the side rail
    c.layer(rrect(0, 0, 88, 44, 16, rbl=4, rbr=4), MINT, depth=5)                        # the tower's hood
    c.face(44, 22, 9, "happy")
    c.flat(star(78, 8, 6), YELLOW)


def draw_swing(c, state):
    W, H = c.w - 10, c.h - 10      # 190 x 190: an A-frame with one seat on two ropes, a face on the top bar
    for lx in (10, W - 54):
        legs = poly([(lx, H), (lx + 14, H), (lx + 28, 22), (lx + 16, 22)]) + \
            poly([(lx + 30, H), (lx + 44, H), (lx + 28, 22), (lx + 16, 22)])
        c.layer(legs, WOOD_DK, depth=4)
        c.layer(ellipse(lx + 22, H - 4, 26, 6), kit.dk(GRASS, .15), depth=0, shadow=False)
    c.layer(rrect(0, 10, W, 18, 9), WOOD, depth=5)                                      # the top bar
    c.face(W / 2, 19, 6.5, "smile")
    sx = W / 2
    c.stroke(path([(sx - 22, 28), (sx - 22, 134)]), WOOD_DEEP, 3.5)                     # the ropes
    c.stroke(path([(sx + 22, 28), (sx + 22, 134)]), WOOD_DEEP, 3.5)
    c.layer(rrect(sx - 32, 130, 64, 16, 8), PINK, depth=4)                              # the seat
    c.flat(heart(sx, 138, 9), PINK_DK)


def draw_bench(c, state):
    W, H = c.w - 10, c.h - 10      # 130 x 90: a wooden bench with a face on the backrest
    for x in (14, W - 26):                                                              # the legs
        c.layer(rrect(x, 54, 12, H - 54, 4), WOOD_DEEP, depth=2)
    c.layer(rrect(8, 54, W - 16, 7, 3), WOOD_DEEP, depth=2, shadow=False)
    c.layer(rrect(0, 8, W, 20, 10), WOOD, depth=4)                                      # the backrest
    c.face(W / 2, 18, 6, "happy")
    c.layer(rrect(0, 30, W, 10, 5), WOOD, depth=3, shadow=False)
    c.layer(rrect(4, 42, W - 8, 16, 8), WOOD, depth=4)                                  # the seat
    c.flat(rrect(12, 46, W - 24, 3, 1.5), kit.dk(WOOD, .18))


def draw_sandbox(c, state):
    W, H = c.w - 10, c.h - 10      # 190 x 98: a wooden frame seen a little from above, sand, a bucket and a shovel
    frame = poly([(20, 10), (W - 20, 10), (W, H - 12), (0, H - 12)])
    c.layer(frame, WOOD, depth=5)                                                       # the frame
    inner = poly([(34, 22), (W - 34, 22), (W - 16, H - 22), (16, H - 22)])
    c.flat(inner, SAND)                                                                 # the sand
    r = kit.rnd("park", "sand")
    c.dots([(r.uniform(40, W - 40), r.uniform(30, H - 30)) for _ in range(18)], 1.6, kit.dk(SAND, .18), op=.7)
    c.flat(ellipse(60, H - 34, 22, 7), kit.dk(SAND, .12), op=.6)                        # a little mound
    c.layer(rrect(44, 30, 34, 36, 6, rtl=3, rtr=3), CORAL, depth=4)                     # the bucket
    c.layer(rrect(40, 26, 42, 10, 5), kit.dk(CORAL, .12), depth=2, shadow=False)
    c.stroke(kit.arc(61, 30, 18, 200, 340), kit.dk(CORAL, .3), 3)                       # the handle
    c.face(61, 50, 5.5, "happy", col=PAPER, blush=kit.lt(CORAL, .3))
    shovel = rrect(W - 70, 32, 8, 42, 3).rotate(30, W - 66, 53) + \
        poly([(W - 80, 72), (W - 52, 72), (W - 56, 92), (W - 76, 92)]).rotate(30, W - 66, 53)
    c.layer(shovel, MINT_DK, depth=3)                                                   # the shovel
    c.flat(circle(W - 56, 36, 5).rotate(30, W - 66, 53), kit.dk(MINT_DK, .2))


def draw_ball(c, state):
    W, H = c.w - 10, c.h - 10      # 68 x 68: a red and white ball with a face
    R = W / 2
    c.layer(circle(R, R, R), RED, depth=4)
    c.flat(ellipse(R, R, R * .42, R), PAPER)                                            # the white band
    c.flat(circle(R - R * .45, R - R * .45, R * .16), PAPER, op=.7)                     # the shine
    c.face(R, R, 6, "happy", col=DARK)


def draw_flower(c, state):
    W, H = c.w - 10, c.h - 10      # 50 x 80: a clump of three flowers with faces
    for x, col in ((W / 2 - 15, PINK), (W / 2 + 15, LAVENDER), (W / 2, YELLOW)):
        top = 38 if x == W / 2 else 46
        c.stroke(path([(x, H), (x, top)]), LEAF_DK, 3.5)
    c.layer(ellipse(W / 2 - 18, H - 12, 10, 5).rotate(-30, W / 2 - 18, H - 12), LEAF, depth=2, shadow=False)
    c.layer(ellipse(W / 2 + 18, H - 14, 10, 5).rotate(30, W / 2 + 18, H - 14), LEAF, depth=2, shadow=False)
    for x, col, cy, r in ((W / 2 - 15, PINK, 44, 12), (W / 2 + 15, LAVENDER, 46, 12), (W / 2, YELLOW, 30, 14)):
        petals = kit.Shape()
        for k in range(6):
            a = k * math.pi / 3
            petals = petals + circle(x + r * .78 * math.cos(a), cy + r * .78 * math.sin(a), r * .5)
        c.layer(petals, col, depth=2, shadow=False)
        c.layer(circle(x, cy, r * .62), CREAM if col != YELLOW else PEACH, depth=0, shadow=False)
        c.face(x, cy, r * .3, "happy" if col == YELLOW else "smile")


# ---------------------------------------------------------------- the three decorations
def draw_deco_1(c, state):
    W, H = c.w - 10, c.h - 10      # 50 x 130: three balloons tied to the bench
    knot = (W / 2 + 6, H)
    for x, y, col in ((W / 2 - 12, 30, PINK), (W / 2 + 14, 22, YELLOW), (W / 2, 50, MINT)):
        c.stroke(path([(x, y + 26), knot]), DARK, 1.4)
    for x, y, col in ((W / 2 - 12, 30, PINK), (W / 2 + 14, 22, YELLOW), (W / 2, 50, MINT)):
        c.layer(ellipse(x, y, 15, 18), col, depth=3, shadow_op=.1)
        c.flat(poly([(x - 3, y + 17), (x + 3, y + 17), (x, y + 21)]), kit.dk(col, .25))
        c.flat(ellipse(x - 5, y - 7, 4, 6).rotate(-20, x - 5, y - 7), PAPER, op=.7)


def draw_deco_2(c, state):
    W, H = c.w - 10, c.h - 10      # 110 x 50: two little birds sitting on the tree
    for x, col, flip in ((28, LAVENDER_DK, False), (82, CORAL, True)):
        s = -1 if flip else 1
        body = ellipse(x, 30, 17, 13) + circle(x + s * 10, 18, 10)
        c.layer(body, col, depth=3, shadow_op=.1)
        c.flat(ellipse(x - s * 6, 30, 9, 5).rotate(-s * 25, x - s * 6, 30), kit.lt(col, .3))     # the wing
        c.flat(poly([(x + s * 19, 18), (x + s * 27, 21), (x + s * 19, 24)]), YELLOW)          # the beak
        c.flat(circle(x + s * 13, 16, 2.2), DARK)
        c.flat(circle(x + s * 13.8, 15.2, .8), PAPER)
        c.flat(ellipse(x + s * 9, 22, 3, 1.8), BLUSH, op=.8)
        for dx in (-3, 3):                                                                       # the feet
            c.stroke(path([(x + dx, 42), (x + dx, H)]), WOOD_DEEP, 1.6)


def draw_deco_3(c, state):
    W, H = c.w - 10, c.h - 10      # 66 x 120: a pinwheel stuck in the grass
    cx, cy = W / 2, 30
    c.layer(rrect(cx - 3, cy, 6, H - cy, 3), WOOD_DK, depth=2)                          # the stick
    cols = (PINK, YELLOW, MINT, LAVENDER)
    for k in range(4):
        a = math.radians(k * 90 + 20)
        sail = poly([(cx, cy), (cx + 26 * math.cos(a), cy + 26 * math.sin(a)),
                     (cx + 26 * math.cos(a + .9), cy + 26 * math.sin(a + .9))])
        c.layer(sail, cols[k], depth=2, shadow_op=.1)
    c.layer(circle(cx, cy, 5), CREAM, depth=0, shadow=False)
    c.flat(circle(cx, cy, 2), DARK)


# ---------------------------------------------------------------- the scene
SCENE = scene.Scene(
    "park", "公園", "park",
    exits={"back": "street"},
    stand=Box(252, 688, 204, 400),
    buddy=Box(402, 798, 96, 128),
    bg=draw_bg,
    things=[
        Thing("tree", "大樹", "tree", 480, 300, 232, 300, z=8, draw=draw_tree),
        Thing("bench", "長椅", "bench", 74, 515, 140, 100, z=10, draw=draw_bench),
        Thing("swing", "鞦韆", "swing", 464, 555, 200, 200, z=14, draw=draw_swing),
        Thing("slide", "溜滑梯", "slide", 76, 683, 144, 230, z=16, draw=draw_slide),
        Thing("sandbox", "沙坑", "sandbox", 252, 746, 200, 108, z=20, draw=draw_sandbox),
        Thing("ball", "球", "ball", 492, 751, 78, 78, z=22, draw=draw_ball),
        Thing("flower", "小花", "flowers", 566, 745, 60, 90, z=22, draw=draw_flower),
    ],
    decos=[
        Deco("deco_1", "氣球", "balloons", 118, 400, 60, 140, draw=draw_deco_1),
        Deco("deco_2", "小鳥", "birds", 480, 126, 120, 60, draw=draw_deco_2),
        Deco("deco_3", "風車", "pinwheel", 42, 395, 76, 130, draw=draw_deco_3),
    ])

if __name__ == "__main__":
    SCENE.build()
