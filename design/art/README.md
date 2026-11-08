# design/art：小小生活家的圖（立體書風）

Every picture is cut paper: a flat shape in a soft colour, the paper's **thickness** (same shape,
darker, shifted down-right) and a soft **shadow** (same shape, dark, see-through, shifted further).
No filters, masks, CSS, text or images: only `<path>` with `fill` / `stroke` / `fill-opacity`, so
flutter_svg draws what Chromium draws. The contract with the app is `docs/art.md`: read it first.

## Draw a layer
```python
import kit
c = kit.Ctx(120, 100)                                   # viewBox 0 0 120 100 (1 unit = 1 scene pixel)
c.layer(kit.rrect(0, 20, 110, 70, 16), kit.MINT)        # shadow + thickness + top (depth=5 default)
c.layer(kit.circle(55, 30, 18), kit.YELLOW, depth=3, shadow=False)
c.flat(kit.heart(55, 60, 20), kit.PINK_DK)               # printed on the paper, no thickness
c.stroke(kit.path([(10, 90), (100, 90)]), kit.DARK, 2.5) # a line
c.face(55, 55, 10, "happy")                              # dot eyes, blush, smile; sleepy / open / wink / smile
kit.write_svg(out_path, c.svg())                          # checks docs/art.md's rules, then writes
```
Shapes: `rrect ellipse circle poly smooth blob cloud star heart path arc ring`; combine with `+`
(union, all clockwise), `.move .scale .flip(cx) .rotate(deg, cx, cy)`. Colours: `PINK MINT CREAM
YELLOW SKY LAVENDER PEACH CORAL LEAF WOOD WOOD_DK WOOD_DEEP PAPER WALL GREY DARK BLUSH` and
`lt(c, t) dk(c, t) mix(a, b, t) tone(c, l, s, dh)`. Leave ~10 px free on the right and bottom of a
file for the shadow (it is cut off at the viewBox). Randomness only through `kit.rnd(key)`.

## A scene module (copy `room_living.py`)
`room_<x>.py` / `place_<x>.py` defines `SCENE = scene.Scene(id, zh, en, exits, stand, buddy, bg,
things, decos)`. Boxes are in **scene pixels** (600 x 800): `Thing(id, zh, en, cx, cy, w, h, z,
draw, states)` with the centre and size; `Box(cx, bottom, w, h)` for `stand` / `buddy` (feet at
`bottom`; in the JSON their `y` is that bottom edge, things' `y` is the centre). `draw(c, state)` gets a `kit.Ctx` of exactly `w x h`. The wall is the top 560 px, the
floor the bottom 240 px; the avatar stands at `Box(252, 688, 204, 400)`, drawn by the app at
z = 50, so keep every thing's `z` under 50 (or away from the stand box). `bg(c)` draws the 600 x
800 background and MUST fill the sky with `kit.SKY_TOKEN` (`#SKY`); window glass uses it too.
Exactly 3 `Deco`s per scene. `SCENE.build()` writes `app/assets/art/scenes/<id>/*.svg` and
`app/assets/scenes/<id>.json` (fractions 0-1, per docs/art.md) and checks them.

Other modules (`avatar.py`, `buddy.py`, `clock.py`, `rewards.py`, `props_<x>.py`) define `build()`
and are registered in `MODULES` / `MODULE_PREFIXES` at the top of `build.py`.

## Commands (run in this folder)
```
python3 build.py living                      # build one scene (any room_/place_ name)
python3 build.py all                         # everything, then check
python3 build.py check                       # rules on every SVG + every scene JSON vs its files
python3 build.py preview living OUT.png      # the room as the app draws it; add lamp=off plant=wilt
                                             # toybox=full to pick states, nodecos, nodoll
python3 build.py fluttercheck living         # real flutter_svg vs Chromium (~20 s; needs Flutter)
```
Look at the preview PNG (Read tool) after every change; iterate until it is clearly cut paper
(visible thickness and shadows), soft colours, faces on the furniture, big uncluttered shapes.

## Rules
- Do not run git here; the main session commits. Do not write outside `design/art/`,
  `app/assets/art/` and `app/assets/scenes/`.
- Output must be deterministic (build twice, get the same bytes). No `__pycache__` (build.py sets
  `sys.dont_write_bytecode`).
- Thing boxes stay inside the scene and must not sit in front of the avatar's stand box; `build()`
  and `check` refuse otherwise. Every file < 70 KB; `fluttercheck` must pass before handing over.
