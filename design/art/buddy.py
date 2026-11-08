"""The little buddy (docs/art.md buddy/): <kind>_<pose>.svg, viewBox 0 0 160 160.

kinds: dog (floppy ears, a spot), cat (pointy ears, whiskers), rabbit (long ears), duck (yellow,
orange bill). poses: stand, sleep (curled up, with z's), happy (jumping, ears up), eat (head down
at a bowl). Round, big-headed cut paper with dot eyes and blush. Drawn at the scene's scale (the
buddy box is 120 x 160 scene pixels), so depth 4-5 is right.
"""
import math

import kit
from kit import BLUSH, DARK, PAPER, PINK, PINK_DK, WHITE, arc, circle, ellipse, path, poly, rrect

OUT = kit.ART / "buddy"
S = 160

KINDS = {
    "dog": {"body": "#F1DABD", "mark": "#B98A5E", "nose": DARK},
    "cat": {"body": "#D9D3DF", "mark": "#B7AFC2", "nose": PINK_DK},
    "rabbit": {"body": "#FBF3E8", "mark": PINK, "nose": PINK_DK},
    "duck": {"body": "#FFD866", "mark": "#F5A24A", "nose": "#F5A24A"},
}
POSES = ("stand", "sleep", "happy", "eat")
ORANGE = "#F5A24A"
BOWL = kit.CORAL
ZZ = kit.LAVENDER_DK


# ---------------------------------------------------------------- small parts
def eyes(c, cx, cy, mood="open", gap=12, r=4.6):
    for x in (cx - gap, cx + gap):
        if mood == "closed":
            c.stroke(arc(x, cy - 2, 5.5, 20, 160), DARK, 3)
        elif mood == "happy":
            c.stroke(arc(x, cy + 2, 5.5, 200, 340), DARK, 3)
        else:
            c.flat(circle(x, cy, r), DARK)
            c.flat(circle(x + r * .35, cy - r * .35, r * .36), WHITE)


def cheeks(c, cx, cy, gap=21, op=.85):
    for x in (cx - gap, cx + gap):
        c.flat(ellipse(x, cy + 8, 7, 4.5), BLUSH, op=op)


def muzzle(c, cx, cy, nose_col, mood="smile", nose="dot"):
    """Nose + mouth for the furry buddies (the duck has a bill instead)."""
    ny = cy + 7
    if nose == "triangle":
        c.flat(poly([(cx - 4, ny - 2), (cx + 4, ny - 2), (cx, ny + 3)]), nose_col)
    else:
        c.flat(ellipse(cx, ny, 5, 3.6), nose_col)
        c.flat(circle(cx - 1.5, ny - 1, 1.3), WHITE, op=.8)
    if mood == "happy":
        m = kit.Shape(arc(cx, ny + 6, 8, 0, 180).cmds + [("Z",)])
        c.flat(m, DARK)
        c.flat(ellipse(cx, ny + 11, 4, 2.4), PINK_DK)
    elif mood == "sleep":
        c.flat(ellipse(cx, ny + 8, 2.2, 2.6), DARK)
    else:                                                   # a little w mouth
        c.stroke(arc(cx - 4, ny + 4, 4, 20, 160), DARK, 2.2)
        c.stroke(arc(cx + 4, ny + 4, 4, 20, 160), DARK, 2.2)


def bill(c, cx, cy, mood="smile"):
    by = cy + 9
    if mood == "happy":
        c.layer(ellipse(cx, by - 3, 13, 5), ORANGE, depth=2, shadow=False)
        c.layer(ellipse(cx, by + 5, 11, 5), kit.dk(ORANGE, .12), depth=2, shadow=False)
        c.flat(ellipse(cx, by + 1, 7, 3), PINK_DK)
    else:
        c.layer(ellipse(cx, by, 13, 6.5), ORANGE, depth=2, shadow=False)
        c.stroke(path([(cx - 8, by + .5), (cx + 8, by + .5)]), kit.dk(ORANGE, .3), 1.6)
        c.flat(circle(cx - 6, by - 2.5, 1.4), WHITE, op=.7)


def ground(c, cx, cy, rx, op=.14):
    c.flat(ellipse(cx, cy, rx, rx * .22), kit.SHADOW, op=op)


def zees(c, x, y):
    for i, s in enumerate((9, 13, 17)):
        xx, yy = x + i * 14, y - i * 18
        c.stroke(path([(xx, yy), (xx + s, yy), (xx, yy + s), (xx + s, yy + s)]), ZZ, 2.6 + i * .3)


# ---------------------------------------------------------------- ears per kind
def dog_ears(c, k, cx, cy, r, pose):
    up = pose == "happy"
    for side in (-1, 1):
        if up:
            e = ellipse(0, 0, 10, 22).rotate(-50 * side, 0, 0).move(cx + side * (r - 6), cy - r * .45)
        elif pose == "sleep":
            e = ellipse(0, 0, 10, 20).rotate(-15 * side, 0, 0).move(cx + side * (r - 4), cy + 6)
        else:
            e = ellipse(0, 0, 10, 21).rotate(-8 * side, 0, 0).move(cx + side * (r - 3), cy + 4)
        c.layer(e, k["mark"], depth=4)


def cat_ears(c, k, cx, cy, r, pose):
    for side in (-1, 1):
        bx = cx + side * r * .62
        tip = (cx + side * r * .95, cy - r * 1.25)
        e = poly([(bx - side * 14, cy - r * .55), tip, (bx + side * 12, cy - r * .2)])
        c.layer(e, k["body"], depth=4)
        inner = poly([(bx - side * 7, cy - r * .62), (tip[0] - side * 3, tip[1] + 9), (bx + side * 6, cy - r * .4)])
        c.flat(inner, PINK)


def rabbit_ears(c, k, cx, cy, r, pose):
    for side in (-1, 1):
        if pose == "sleep":
            deg, ox, oy = -70 * side, side * (r - 4), -r * .25
        elif pose == "happy":
            deg, ox, oy = -22 * side, side * (r * .45), -r - 10
        else:
            deg, ox, oy = -8 * side, side * (r * .4), -r - 8
        e = ellipse(0, 0, 9, 27).rotate(deg, 0, 0).move(cx + ox, cy + oy)
        c.layer(e, k["body"], depth=4)
        c.flat(ellipse(0, 0, 4.5, 17).rotate(deg, 0, 0).move(cx + ox, cy + oy), PINK)


def duck_tuft(c, k, cx, cy, r, pose):
    for i, (dx, dy, rr) in enumerate(((-7, -r - 1, 6), (1, -r - 6, 7), (9, -r - 2, 6))):
        c.layer(circle(cx + dx, cy + dy, rr), k["body"], depth=3, shadow=False)


EARS = {"dog": dog_ears, "cat": cat_ears, "rabbit": rabbit_ears, "duck": duck_tuft}


# ---------------------------------------------------------------- the four poses
def head(c, kind, k, cx, cy, r, pose, mood, eye_dy=0):
    EARS[kind](c, k, cx, cy, r, pose)
    c.layer(circle(cx, cy, r), k["body"], depth=5)
    if kind == "dog":                                                        # the eye patch
        c.flat(circle(cx + 11, cy - 3, 12), k["mark"], op=.55)
    if kind == "cat":                                                        # forehead stripes
        for dx in (-9, 0, 9):
            c.stroke(path([(cx + dx, cy - r + 3), (cx + dx * .6, cy - r + 12)]), k["mark"], 2.4)
    if kind == "rabbit":
        c.flat(ellipse(cx, cy - r * .35, 6, 4), PINK, op=.5)
    ey = cy - 2 + eye_dy
    eyes(c, cx, ey, "closed" if mood == "sleep" else "open")
    cheeks(c, cx, ey)
    if kind == "duck":
        bill(c, cx, ey, mood)
    else:
        muzzle(c, cx, ey, k["nose"], mood, "triangle" if kind in ("cat", "rabbit") else "dot")
    if kind == "cat":                                                        # whiskers
        for side in (-1, 1):
            for dy, deg in ((2, -8), (9, 6)):
                x0 = cx + side * 14
                a = math.radians(deg)
                c.stroke(path([(x0, ey + dy), (x0 + side * 20 * math.cos(a), ey + dy + 20 * math.sin(a))]), DARK, 1.8, op=.7)


def legs(c, k, pts, w=12, h=16):
    for x, y in pts:
        c.layer(rrect(x - w / 2, y, w, h, w / 2), k["body"], depth=3, shadow=False)


def duck_feet(c, pts):
    for x, y in pts:
        c.layer(poly([(x - 9, y + 8), (x + 9, y + 8), (x + 3, y - 2), (x - 3, y - 2)]), ORANGE, depth=2, shadow=False)


def tail(c, kind, k, x, y, deg, length=22):
    if kind == "duck":
        c.layer(poly([(x, y), (x + 14, y - 12), (x + 16, y + 2)]).rotate(deg, x, y), kit.dk(k["body"], .1), depth=3, shadow=False)
    elif kind == "rabbit":
        c.layer(circle(x, y, 8), PAPER, depth=3, shadow=False)
    elif kind == "cat":
        t = rrect(-5, -length, 10, length, 5).rotate(deg, 0, 0).move(x, y)
        c.layer(t, k["body"], depth=3, shadow=False)
        for i in range(2):
            p = (0, -length + 6 + i * 7)
            c.stroke(path([(-5, p[1]), (5, p[1])]).rotate(deg, 0, 0).move(x, y), k["mark"], 2.4)
    else:
        t = rrect(-5, -length, 10, length, 5).rotate(deg, 0, 0).move(x, y)
        c.layer(t, k["mark"], depth=3, shadow=False)


def spot(c, kind, k, x, y, rx, ry):
    if kind == "dog":
        c.flat(ellipse(x, y, rx, ry), k["mark"])
    elif kind == "duck":
        c.layer(ellipse(x, y, rx, ry), kit.dk(k["body"], .08), depth=2, shadow=False)        # a wing


def pose_stand(c, kind, k):
    ground(c, 86, 142, 46)
    tail(c, kind, k, 128, 104, 35)
    if kind == "duck":
        duck_feet(c, ((76, 132), (104, 132)))
        c.layer(ellipse(92, 110, 36, 26), k["body"], depth=5)
        spot(c, kind, k, 104, 112, 16, 10)
    else:
        legs(c, k, ((66, 122), (84, 126), (104, 126), (118, 122)))
        c.layer(ellipse(92, 108, 40, 26), k["body"], depth=5)
        spot(c, kind, k, 112, 102, 13, 9)
    head(c, kind, k, 62, 72, 36, "stand", "smile")


def pose_sleep(c, kind, k):
    ground(c, 86, 146, 56)
    c.layer(ellipse(90, 114, 50, 28), k["body"], depth=5)                   # curled up
    if kind == "cat":
        c.stroke(arc(90, 118, 44, 20, 110), k["body"], 10)                  # the tail wrapped round the front
        c.stroke(arc(90, 118, 44, 60, 100), k["mark"], 10, op=.6)
    elif kind == "dog":
        c.stroke(arc(92, 120, 44, 30, 100), k["mark"], 10)
    elif kind == "duck":
        spot(c, kind, k, 104, 116, 18, 11)
    spot(c, "dog" if kind == "dog" else "", k, 112, 104, 13, 8)
    head(c, kind, k, 56, 100, 32, "sleep", "sleep")
    zees(c, 104, 60)


def pose_happy(c, kind, k):
    ground(c, 80, 148, 36, .1)
    for side in (-1, 1):                                                     # little motion lines
        x = 80 + side * 60
        for dy in (-10, 4, 18):
            c.stroke(path([(x - side * 4, 96 + dy), (x + side * 6, 92 + dy)]), kit.YELLOW, 3)
    tail(c, kind, k, 112, 92, 60, 20)
    if kind == "duck":
        duck_feet(c, ((70, 118), (94, 120)))
        c.layer(ellipse(84, 98, 30, 24), k["body"], depth=5)
        spot(c, kind, k, 96, 98, 14, 9)
    else:
        legs(c, k, ((64, 108), (80, 114), (98, 112), (108, 104)), 11, 14)
        c.layer(ellipse(84, 96, 32, 24), k["body"], depth=5)
        spot(c, kind, k, 100, 90, 12, 8)
    head(c, kind, k, 66, 58, 36, "happy", "happy")


def pose_eat(c, kind, k):
    ground(c, 86, 144, 54)
    tail(c, kind, k, 136, 96, 20, 24)
    if kind == "duck":
        duck_feet(c, ((88, 128), (114, 128)))
        c.layer(ellipse(104, 108, 34, 26), k["body"], depth=5)
        spot(c, kind, k, 114, 110, 15, 10)
    else:
        legs(c, k, ((80, 120), (96, 124), (114, 124), (128, 118)))
        c.layer(ellipse(104, 106, 38, 26), k["body"], depth=5)
        spot(c, kind, k, 122, 100, 13, 9)
    head(c, kind, k, 58, 92, 32, "eat", "smile", eye_dy=5)
    # the bowl, in front of the chin
    c.layer(rrect(18, 118, 56, 22, 10), BOWL, depth=4)
    c.layer(rrect(14, 114, 64, 10, 5), kit.dk(BOWL, .12), depth=3, shadow=False)
    c.dots([(30, 119), (44, 118), (58, 119), (37, 116), (51, 116)], 3.2, kit.WOOD_DK)
    c.face(46, 130, 5, "smile")


POSE_FN = {"stand": pose_stand, "sleep": pose_sleep, "happy": pose_happy, "eat": pose_eat}


def build():
    files = 0
    for kind, k in KINDS.items():
        for pose in POSES:
            c = kit.Ctx(S, S)
            POSE_FN[pose](c, kind, k)
            kit.write_svg(OUT / f"{kind}_{pose}.svg", c.svg(), (S, S))
            files += 1
    print(f"buddy: {files} SVG files in {OUT.relative_to(kit.ROOT)}")


if __name__ == "__main__":
    build()
