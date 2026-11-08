"""The child's paper puppet (docs/art.md avatar/): body_<pose>_<shirt>, head_<skin>, face_<mood>, hair_<n>.

Every file is viewBox 0 0 200 260 with the feet at the bottom edge; the app lays body, head, face
and hair over each other, so the pieces are drawn in the same coordinates. The head is a circle of
radius 66 centred at (100, 98) for `stand` and `sit` (the same place, so the stack works even
before the app reads layout.json); `lie` puts the body across the lower half with the head at the
left, centre (66, 190), the same radius (layout.json says so).

Chibi: the head (with hair) is about half the height; short arms and legs, round hands, little shoes.
The body files only vary by shirt, so hands are one neutral peach (the skin tones are in head_*).
"""
import json
import math

import kit
from kit import BLUSH, DARK, PAPER, WHITE, arc, circle, ellipse, heart, path, poly, rrect

OUT = kit.ART / "avatar"
W, H = 200, 260
HEAD = (100, 98, 66)                     # cx, cy, r for stand / sit
LIE_HEAD = (66, 190, 66)                 # the head when lying down (left, lower half)

SHIRTS = {1: "#F29088", 2: "#FFD46E", 3: "#A8D68E", 4: "#8DB9EA", 5: "#C3ADEB", 6: "#F6A8C3"}   # red yellow green blue purple pink
SKINS = {1: "#FBE4D1", 2: "#F3CFAD", 3: "#D9A273", 4: "#A26E40"}                              # light -> deep
HAND = "#E8BC94"                         # the hands, one tone for every skin (between 2 and 3)
PANTS = "#8FAED9"
PANTS_DK = kit.dk(PANTS, .3)
SHOE = "#8E6239"
HAIR = "#4B3426"
HAIR_EDGE = kit.dk(HAIR, .3)
SWEAT = "#8CCBEB"


def joined(*parts):
    """Open paths (arcs, polylines) joined end to end into one closed outline."""
    cmds = []
    for i, p in enumerate(parts):
        for c in p.cmds:
            if c[0] == "M":
                cmds.append(c if i == 0 else ("L", c[1], c[2]))
            elif c[0] != "Z":
                cmds.append(c)
    cmds.append(("Z",))
    return kit.Shape(cmds)


def ctx():
    return kit.Ctx(W, H)


# ---------------------------------------------------------------- body
def arm(c, px, py, deg, length, col, hand_r=10.5, edge=None):
    """A sleeve hanging from the shoulder pivot (px, py), rotated deg (positive = out to the left), with a round hand."""
    sleeve = rrect(-11, -6, 22, length + 6, 11).rotate(deg, 0, 0).move(px, py)
    c.layer(sleeve, col, depth=4, edge_col=edge)
    a = math.radians(deg)
    hx, hy = px - length * math.sin(a), py + length * math.cos(a)
    c.layer(circle(hx, hy, hand_r), HAND, depth=3, shadow=False)


def body_stand(c, shirt):
    sleeve = kit.dk(shirt, .07)
    arm(c, 68, 182, 28, 36, sleeve)
    arm(c, 132, 182, -28, 36, sleeve)
    c.layer(rrect(64, 224, 72, 26, 9), PANTS, depth=4)                       # shorts
    c.stroke(path([(100, 232), (100, 248)]), PANTS_DK, 2.5)
    c.layer(rrect(60, 168, 80, 62, 18), shirt, depth=5)                      # the shirt
    c.flat(heart(100, 204, 22), kit.lt(shirt, .5))                           # printed heart
    for x in (60, 104):                                                      # shoes
        c.layer(rrect(x, 242, 36, 14, 7), SHOE, depth=3)
        c.flat(rrect(x + 4, 245, 12, 5, 2.5), kit.lt(SHOE, .35))


def body_sit(c, shirt):
    sleeve = kit.dk(shirt, .07)
    # legs forward along the floor: short thighs splayed, the soles of the shoes facing us
    for sx, flip in ((56, 1), (104, -1)):
        leg = rrect(sx, 222, 40, 24, 11).rotate(-6 * flip, sx + 20, 222)
        c.layer(leg, PANTS, depth=4)
    for sx in (52, 112):
        c.layer(rrect(sx, 236, 36, 20, 10), SHOE, depth=3)
        c.flat(rrect(sx + 5, 240, 26, 12, 6), kit.lt(SHOE, .35))             # the sole
        c.flat(rrect(sx + 9, 244, 18, 4, 2), kit.lt(SHOE, .6), op=.7)
    arm(c, 68, 184, 40, 38, sleeve)                                          # hands resting on the floor
    arm(c, 132, 184, -40, 38, sleeve)
    c.layer(rrect(60, 168, 80, 64, 18), shirt, depth=5)
    c.flat(heart(100, 204, 22), kit.lt(shirt, .5))


def body_lie(c, shirt):
    """The standing body laid on its back across the lower half, head to the left: drawn upright in a
    local frame whose neck base is (0, 0), then turned 90 degrees anticlockwise and moved to the neck."""
    nx, ny = LIE_HEAD[0] + LIE_HEAD[2] - 14, LIE_HEAD[1]                     # the neck base, tucked under the chin
    sleeve = kit.dk(shirt, .07)

    def place(shape):
        return shape.rotate(-90, 0, 0).move(nx, ny)

    L = 72                                                                   # the body is a little shorter lying down
    for px, deg in ((-34, 14), (34, -14)):                                   # arms along the sides
        s = rrect(-10, -6, 20, 34, 10).rotate(deg, 0, 0).move(px, 12)
        c.layer(place(s), sleeve, depth=4)
        a = math.radians(deg)
        c.layer(place(circle(px - 28 * math.sin(a), 12 + 28 * math.cos(a), 9.5)), HAND, depth=3, shadow=False)
    c.layer(place(rrect(-32, L - 26, 64, 22, 8)), PANTS, depth=4)             # shorts
    c.stroke(place(path([(0, L - 18), (0, L - 6)])), PANTS_DK, 2.5)
    c.layer(place(rrect(-38, -2, 76, L - 22, 16)), shirt, depth=5)            # the shirt
    c.flat(place(heart(0, 24, 20)), kit.lt(shirt, .5))
    for x in (-36, 4):                                                       # shoes, soles to the right
        c.layer(place(rrect(x, L - 10, 32, 12, 6)), SHOE, depth=3)
        c.flat(place(rrect(x + 4, L - 7, 5, 6, 2.5)), kit.lt(SHOE, .35))


BODIES = {"stand": body_stand, "sit": body_sit, "lie": body_lie}


# ---------------------------------------------------------------- head (ears, neck; no features)
def head(c, skin, cx=HEAD[0], cy=HEAD[1], r=HEAD[2]):
    edge = kit.dk(skin, .28)
    c.layer(rrect(cx - 12, cy + r - 16, 24, 30, 9), kit.dk(skin, .12), depth=3, shadow=False)   # neck
    for ex in (cx - r + 2, cx + r - 2):                                                          # ears
        c.layer(circle(ex, cy + 2, 10), skin, depth=3, edge_col=edge)
        c.flat(circle(ex, cy + 3, 5), kit.dk(skin, .14))
    c.layer(circle(cx, cy, r), skin, depth=5, edge_col=edge)


# ---------------------------------------------------------------- faces
EYE_L, EYE_R, EYE_Y, EYE_R_ = 78, 122, 100, 6.5
MOUTH_Y = 126


def blush(c, op=.85):
    for x in (64, 136):
        c.flat(ellipse(x, 120, 11, 6.5), BLUSH, op=op)


def dot_eyes(c, r=EYE_R_, dy=0):
    for x in (EYE_L, EYE_R):
        c.flat(circle(x, EYE_Y + dy, r), DARK)
        c.flat(circle(x + r * .35, EYE_Y + dy - r * .35, r * .34), WHITE)


def happy_eyes(c):
    for x in (EYE_L, EYE_R):
        c.stroke(arc(x, EYE_Y + 4, 8, 200, 340), DARK, 4)


def closed_eyes(c, r=8, y=EYE_Y - 4):
    for x in (EYE_L, EYE_R):
        c.stroke(arc(x, y, r, 20, 160), DARK, 4)


def smile(c, r=9, w=3.5):
    c.stroke(arc(100, MOUTH_Y - r * .35, r, 25, 155), DARK, w)


def face_normal(c):
    dot_eyes(c)
    blush(c)
    smile(c)


def face_happy(c):
    happy_eyes(c)
    blush(c)
    # a big open smile: a half disc with a tongue
    m = joined(arc(100, 124, 17, 0, 180))
    c.flat(m, DARK)
    c.flat(ellipse(100, 136, 8, 4.5), kit.PINK_DK)


def face_sleepy(c):
    closed_eyes(c)
    blush(c, .7)
    c.flat(ellipse(100, MOUTH_Y + 4, 4.5, 5.5), DARK)


def face_squirm(c):
    for x, d in ((EYE_L, 1), (EYE_R, -1)):                                   # brows pressed down
        c.stroke(path([(x - 11 * d, 84), (x + 9 * d, 90)]), DARK, 4)
    dot_eyes(c, 5.5, 1)
    blush(c)
    c.flat(ellipse(100, 128, 12, 4.5), kit.dk(BLUSH, .25))                   # the lip, bitten
    c.flat(rrect(94, 123, 12, 7, 2), WHITE)
    c.stroke(rrect(94, 123, 12, 7, 2), DARK, 1.6)
    c.stroke(path([(100, 123), (100, 130)]), DARK, 1.2)
    drop = circle(150, 86, 6.5) + poly([(150, 70), (144.5, 85), (155.5, 85)])
    c.layer(drop, SWEAT, depth=2, shadow=False, edge_col=kit.dk(SWEAT, .2))
    c.flat(circle(147.5, 85, 2), WHITE, op=.8)


def face_sad(c):
    for x, d in ((EYE_L, 1), (EYE_R, -1)):                                   # brows up in the middle
        c.stroke(path([(x - 11 * d, 90), (x + 8 * d, 83)]), DARK, 4)
    dot_eyes(c, 6)
    blush(c, .7)
    c.stroke(arc(100, 137, 9, 205, 335), DARK, 3.5)                         # a frown
    c.flat(ellipse(131, 115, 3, 5.5), SWEAT)                                 # a tear


def face_sick(c):
    for x in (EYE_L, EYE_R):                                                 # tired, half-closed eyes
        c.stroke(arc(x, 95, 7, 15, 165), DARK, 3.6)
        c.stroke(arc(x, 103, 5, 35, 145), DARK, 2, op=.35)
    blush(c, .55)
    c.layer(circle(100, 113, 6.5), kit.CORAL, depth=2, shadow=False)        # a red nose
    c.flat(circle(102, 111, 2), WHITE, op=.8)
    c.stroke(path([(90, 130), (95, 126.5), (100, 130), (105, 126.5), (110, 130)]), DARK, 3)


def face_mouth(c):
    dot_eyes(c)
    blush(c)
    c.flat(ellipse(100, 130, 23, 19), DARK)                                  # the open mouth
    c.flat(ellipse(100, 137, 12, 6), kit.PINK_DK)                            # tongue
    c.flat(rrect(81, 112, 38, 10, 3), WHITE)                                 # top teeth
    c.flat(rrect(85, 141, 30, 8, 3), WHITE)                                  # bottom teeth
    for x in (90, 100, 110):
        c.stroke(path([(x, 113), (x, 121)]), kit.GREY, 1.4)
    for x in (93, 100, 107):
        c.stroke(path([(x, 142), (x, 148)]), kit.GREY, 1.4)


FACES = {"normal": face_normal, "happy": face_happy, "sleepy": face_sleepy, "squirm": face_squirm,
         "sad": face_sad, "sick": face_sick, "mouth": face_mouth}


# ---------------------------------------------------------------- hair (dark brown)
HX, HY, HR = 100, 94, 70      # the hair cap sits a little above and outside the head


def cap(fringe_pts, left=(HX - HR, HY), right=(HX + HR, HY)):
    """Over the top from `left` round to `right`, then back along the fringe points (right to left)."""
    a0 = math.degrees(math.atan2(left[1] - HY, left[0] - HX))
    a1 = math.degrees(math.atan2(right[1] - HY, right[0] - HX))
    if a1 < a0:
        a1 += 360
    return joined(arc(HX, HY, HR, a0, a1, 6), path(list(fringe_pts)))


def fringe(y=84, bumps=4, amp=6, x0=HX - 56, x1=HX + 56):
    """Scalloped fringe points from right to left (the cap goes clockwise)."""
    pts = []
    for i in range(bumps * 2 + 1):
        t = i / (bumps * 2)
        x = x1 - (x1 - x0) * t
        pts.append((x, y + (amp if i % 2 else 0)))
    return pts


def hair_1(c):          # short hair: a cap with a little fringe
    pts = ([(HX + 66, HY + 30), (HX + 58, HY + 32), (HX + 58, 92)] + fringe(84, 3, 7, HX - 54, HX + 54)
           + [(HX - 58, 92), (HX - 58, HY + 32), (HX - 66, HY + 30)])
    c.layer(cap(pts), HAIR, depth=5, edge_col=HAIR_EDGE)


def hair_2(c):          # bob with a straight fringe (妹妹頭): the cap and two side panels down to the cheeks
    pts = ([(HX + 68, HY + 56), (HX + 56, HY + 60), (HX + 50, 92)] + fringe(86, 3, 5, HX - 50, HX + 50)
           + [(HX - 50, 92), (HX - 56, HY + 60), (HX - 68, HY + 56)])
    c.layer(cap(pts, (HX - HR, HY + 20), (HX + HR, HY + 20)), HAIR, depth=5, edge_col=HAIR_EDGE)
    c.layer(rrect(HX - 14, HY - 52, 28, 7, 3.5), kit.PINK_DK, depth=2, shadow=False)        # a hair clip


def hair_3(c):          # ponytail: a swept fringe and a tail at the upper right with a yellow tie
    tail = ellipse(0, 0, 13, 32).rotate(-28, 0, 0).move(176, 92)
    c.layer(tail, HAIR, depth=5, edge_col=HAIR_EDGE)
    pts = [(HX + 68, HY + 10), (HX + 60, 84), (HX + 30, 78), (HX - 10, 86), (HX - 40, 80), (HX - 58, 86), (HX - 68, HY + 10)]
    c.layer(cap(pts), HAIR, depth=5, edge_col=HAIR_EDGE)
    c.layer(circle(162, 64, 8), kit.YELLOW, depth=2, shadow=False)


def hair_4(c):          # curly: puffs all round the cap and at the temples
    s = cap([(HX + 66, HY + 24), (HX + 56, 92)] + fringe(84, 4, 6, HX - 56, HX + 56) + [(HX - 56, 92), (HX - 66, HY + 24)])
    for i in range(9):
        a = math.radians(188 + 164 * i / 8)
        s = s + circle(HX + 62 * math.cos(a), HY + 62 * math.sin(a), 16)
    s = s + circle(HX - 60, HY + 24, 15) + circle(HX + 60, HY + 24, 15)
    for i in range(4):
        s = s + circle(HX - 42 + 28 * i, 90, 11)
    c.layer(s, HAIR, depth=5, edge_col=HAIR_EDGE)


HAIRS = {1: hair_1, 2: hair_2, 3: hair_3, 4: hair_4}


# ---------------------------------------------------------------- build
def build():
    files = 0
    for pose, fn in BODIES.items():
        for i, col in SHIRTS.items():
            c = ctx()
            fn(c, col)
            kit.write_svg(OUT / f"body_{pose}_{i}.svg", c.svg(), (W, H))
            files += 1
    for i, skin in SKINS.items():
        c = ctx()
        head(c, skin)
        kit.write_svg(OUT / f"head_{i}.svg", c.svg(), (W, H))
        files += 1
    for mood, fn in FACES.items():
        c = ctx()
        fn(c)
        kit.write_svg(OUT / f"face_{mood}.svg", c.svg(), (W, H))
        files += 1
    for i, fn in HAIRS.items():
        c = ctx()
        fn(c)
        kit.write_svg(OUT / f"hair_{i}.svg", c.svg(), (W, H))
        files += 1
    layout = {"head": {"stand": {"cx": HEAD[0], "cy": HEAD[1], "r": HEAD[2]},
                       "sit": {"cx": HEAD[0], "cy": HEAD[1], "r": HEAD[2]},
                       "lie": {"cx": LIE_HEAD[0], "cy": LIE_HEAD[1], "r": LIE_HEAD[2], "rotate": 0}}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "layout.json").write_text(json.dumps(layout, indent=2) + "\n")
    print(f"avatar: {files} SVG files + layout.json in {OUT.relative_to(kit.ROOT)}")


if __name__ == "__main__":
    build()
