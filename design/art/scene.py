"""Scenes for 小小生活家: one background plus separate things, placed by app/assets/scenes/<id>.json.

A scene module (room_<x>.py, place_<x>.py) builds one `Scene` and names it `SCENE`:

    import kit, scene
    def draw_sofa(c, state):        # c is a kit.Ctx whose viewBox is the thing's box in scene pixels
        c.layer(kit.rrect(0, 20, c.w - 10, c.h - 30, 18), kit.MINT)
        c.face(c.w / 2, 60, 12)
    SCENE = scene.Scene(
        "living", "客廳", "living room",
        exits={"left": "kitchen", "right": "entrance", "up": "bedroom"},
        stand=scene.Box(252, 688, 204, 400),        # centre x, BOTTOM y (feet), w, h  (scene pixels)
        buddy=scene.Box(408, 688, 120, 160),
        bg=draw_bg,                                   # draw_bg(c): c is a 600 x 800 Ctx
        things=[scene.Thing("sofa", "沙發", "sofa", 170, 610, 260, 170, z=10, draw=draw_sofa), ...],
        decos=[scene.Deco("deco_1", "牆上的畫", "picture", 460, 230, 90, 80, draw=draw_deco1), ...])

Boxes: `Thing(id, zh, en, cx, cy, w, h, z, draw, states=("",))` takes the CENTRE and size in scene
pixels (the scene is 600 x 800); the JSON gets them as fractions. The thing's SVG viewBox is
`0 0 w h`, so it fills its box exactly and 1 unit = 1 scene pixel: shadows that fall outside the box
are cut off, so leave ~10 px free on the right and bottom (`c.w - 10`, `c.h - 10`) for them.
`z`: higher is in front. The avatar and the buddy are drawn by the app at AVATAR_Z (50): every
thing must have z < AVATAR_Z or must not touch the stand box (build() checks). `states`: one file
per state, `<id>.svg` for "" and `<id>_<state>.svg` otherwise; draw(c, state) is told which.

`Scene.build()` writes app/assets/art/scenes/<id>/*.svg and app/assets/scenes/<id>.json;
`Scene.check()` re-checks the files on disk; `preview(scene, out_png)` composes the room with
Chromium the way the app draws it (sky filled in, a paper-doll stand-in on the stand box).
"""
import json
import pathlib
import subprocess
import tempfile

import kit

SCENE_W, SCENE_H = 600, 800
AVATAR_Z = 50
SKY_SAMPLE = "#BFE3F5"
SCRATCH = pathlib.Path("/dev/shm") if pathlib.Path("/dev/shm").is_dir() else pathlib.Path(tempfile.gettempdir())


class Box:
    """The stand / buddy box in scene pixels: centre x, BOTTOM y (the feet), width, height. In the JSON
    (docs/art.md's example: y 0.86, h 0.5) `x` is the centre and `y` is the bottom edge, where the
    feet are; the box reaches up from y by h."""

    def __init__(self, cx, bottom, w, h):
        self.cx, self.bottom, self.w, self.h = cx, bottom, w, h

    def json(self):
        return {"x": round(self.cx / SCENE_W, 4), "y": round(self.bottom / SCENE_H, 4),
                "w": round(self.w / SCENE_W, 4), "h": round(self.h / SCENE_H, 4)}

    def rect(self):
        return self.cx - self.w / 2, self.bottom - self.h, self.cx + self.w / 2, self.bottom


class Thing:
    """Something in the room that can be tapped and spoken. cx, cy = centre of its box, w, h = size,
    all in scene pixels. draw(c, state) paints it into a kit.Ctx of w x h."""

    def __init__(self, id, zh, en, cx, cy, w, h, z, draw, states=("",)):
        self.id, self.zh, self.en = id, zh, en
        self.cx, self.cy, self.w, self.h, self.z = cx, cy, w, h, z
        self.draw, self.states = draw, tuple(states)

    def rect(self):
        return self.cx - self.w / 2, self.cy - self.h / 2, self.cx + self.w / 2, self.cy + self.h / 2

    def json(self):
        j = {"id": self.id, "zh": self.zh, "en": self.en,
             "x": round(self.cx / SCENE_W, 4), "y": round(self.cy / SCENE_H, 4),
             "w": round(self.w / SCENE_W, 4), "h": round(self.h / SCENE_H, 4), "z": self.z}
        if self.states != ("",):
            j["states"] = list(self.states)
        return j

    def file(self, state=""):
        return f"{self.id}_{state}.svg" if state else f"{self.id}.svg"


class Deco(Thing):
    """A decoration the sticker chart gives (deco_1..3): no states, drawn behind the furniture."""

    def __init__(self, id, zh, en, cx, cy, w, h, draw, z=6):
        super().__init__(id, zh, en, cx, cy, w, h, z, draw)

    def json(self):
        return {"id": self.id, "zh": self.zh, "en": self.en,
                "x": round(self.cx / SCENE_W, 4), "y": round(self.cy / SCENE_H, 4),
                "w": round(self.w / SCENE_W, 4), "h": round(self.h / SCENE_H, 4)}


def overlap(a, b):
    """Overlap area of two (x0, y0, x1, y1) rects."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return max(0.0, w) * max(0.0, h)


class Scene:
    def __init__(self, id, zh, en, exits, stand, buddy, bg, things, decos):
        self.id, self.zh, self.en, self.exits = id, zh, en, dict(exits)
        self.stand, self.buddy, self.bg = stand, buddy, bg
        self.things, self.decos = list(things), list(decos)
        if len(self.decos) != 3:
            raise SystemExit(f"{id}: docs/art.md wants 3 decos, got {len(self.decos)}")

    @property
    def art_dir(self):
        return kit.ART / "scenes" / self.id

    @property
    def json_path(self):
        return kit.SCENES_JSON / f"{self.id}.json"

    def json(self):
        return {"id": self.id, "zh": self.zh, "en": self.en, "exits": self.exits,
                "stand": self.stand.json(), "buddy": self.buddy.json(),
                "things": [t.json() for t in self.things], "decos": [d.json() for d in self.decos]}

    # ---- building
    def build(self):
        self.validate()
        self.art_dir.mkdir(parents=True, exist_ok=True)
        c = kit.Ctx(SCENE_W, SCENE_H)
        self.bg(c)
        text = c.svg()
        if kit.SKY_TOKEN not in text:
            raise SystemExit(f"{self.id}/bg.svg: the sky must be filled with {kit.SKY_TOKEN} (docs/art.md)")
        written = [kit.write_svg(self.art_dir / "bg.svg", text, (SCENE_W, SCENE_H)) and self.art_dir / "bg.svg"]
        for t in self.things + self.decos:
            for st in t.states:
                c = kit.Ctx(t.w, t.h)
                t.draw(c, st)
                p = self.art_dir / t.file(st)
                kit.write_svg(p, c.svg(), (t.w, t.h))
                written.append(p)
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(self.json(), ensure_ascii=False, indent=1) + "\n")
        written.append(self.json_path)
        self.check()
        print(f"{self.id}: {len(written) - 1} SVG files and {self.json_path.relative_to(kit.ROOT)}")
        return written

    def validate(self):
        """Boxes inside the scene, ids unique, nothing in front of the avatar covers the stand."""
        ids = [t.id for t in self.things + self.decos]
        if len(set(ids)) != len(ids):
            raise SystemExit(f"{self.id}: duplicate thing ids")
        for t in self.things + self.decos:
            x0, y0, x1, y1 = t.rect()
            if x0 < -0.01 or y0 < -0.01 or x1 > SCENE_W + .01 or y1 > SCENE_H + .01:
                raise SystemExit(f"{self.id}/{t.id}: box {x0:g},{y0:g}-{x1:g},{y1:g} leaves the 600 x 800 scene")
            if t.z >= AVATAR_Z and overlap(t.rect(), self.stand.rect()) > 0:
                raise SystemExit(f"{self.id}/{t.id}: z {t.z} is in front of the avatar and covers the stand box")
        for b, nm in ((self.stand, "stand"), (self.buddy, "buddy")):
            x0, y0, x1, y1 = b.rect()
            if x0 < 0 or y0 < 0 or x1 > SCENE_W or y1 > SCENE_H:
                raise SystemExit(f"{self.id}: {nm} box leaves the scene")

    def check(self):
        """Re-check the files on disk against the JSON (used by build.py check)."""
        check_scene_files(self.json_path)


def check_scene_files(json_path):
    """For one scene JSON: boxes inside 0-1, every thing/state/deco file exists and its viewBox
    aspect matches its box within 2 %, bg.svg is 600 x 800 and has the sky token."""
    j = json.loads(pathlib.Path(json_path).read_text())
    sid = j["id"]
    d = kit.ART / "scenes" / sid
    bg = d / "bg.svg"
    if not bg.exists():
        raise SystemExit(f"{sid}: bg.svg missing")
    if kit.viewbox_of(bg) != (SCENE_W, SCENE_H):
        raise SystemExit(f"{sid}/bg.svg: viewBox must be 0 0 600 800")
    if kit.SKY_TOKEN not in bg.read_text():
        raise SystemExit(f"{sid}/bg.svg: no {kit.SKY_TOKEN} sky placeholder")
    stand_rect = None
    for key in ("stand", "buddy"):      # x = centre, y = the feet (bottom edge), the box reaches up by h
        b = j[key]
        if not (0 <= b["x"] - b["w"] / 2 and b["x"] + b["w"] / 2 <= 1 and 0 <= b["y"] - b["h"] and b["y"] <= 1.0001):
            raise SystemExit(f"{sid}: {key} box leaves 0-1")
        if key == "stand":
            stand_rect = (b["x"] - b["w"] / 2, b["y"] - b["h"], b["x"] + b["w"] / 2, b["y"])
    for t in j["things"] + j["decos"]:
        if not (-1e-4 <= t["x"] - t["w"] / 2 and t["x"] + t["w"] / 2 <= 1.0001 and -1e-4 <= t["y"] - t["h"] / 2 and t["y"] + t["h"] / 2 <= 1.0001):
            raise SystemExit(f"{sid}/{t['id']}: box leaves 0-1")
        if "z" in t and t["z"] >= AVATAR_Z:
            if overlap((t["x"] - t["w"] / 2, t["y"] - t["h"] / 2, t["x"] + t["w"] / 2, t["y"] + t["h"] / 2), stand_rect) > 0:
                raise SystemExit(f"{sid}/{t['id']}: in front of the avatar and over the stand box")
        want = (t["w"] * SCENE_W) / (t["h"] * SCENE_H)
        for st in t.get("states", [""]):
            f = d / (f"{t['id']}_{st}.svg" if st else f"{t['id']}.svg")
            if not f.exists():
                raise SystemExit(f"{sid}: {f.name} missing")
            vw, vh = kit.viewbox_of(f)
            if abs(vw / vh - want) / want > 0.02:
                raise SystemExit(f"{sid}/{f.name}: viewBox aspect {vw / vh:.3f} but the box is {want:.3f}")
    return j


# ---------------------------------------------------------------- preview (Chromium)
SHOT_JS = """const { chromium } = require('playwright');
(async () => { const [inp, out, w, h, s] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +s });
  await p.goto('file://' + inp); await p.waitForTimeout(400);
  await p.screenshot({ path: out }); await b.close(); })();
"""


def _img(src, x, y, w, h):
    return (f'<img src="file://{src}" style="position:absolute;left:{x:.1f}px;top:{y:.1f}px;'
            f'width:{w:.1f}px;height:{h:.1f}px">')


def _doll(stand, buddy):
    """A see-through paper-doll stand-in for the avatar and the buddy, so the preview shows what they cover."""
    x0, y0, x1, y1 = stand.rect()
    w, h = x1 - x0, y1 - y0
    c = kit.Ctx(w, h)
    c.flat(kit.rrect(w * .25, h * .42, w * .5, h * .56, w * .12), "#777777", op=.45)
    c.flat(kit.circle(w / 2, h * .26, w * .3), "#777777", op=.45)
    c.stroke(kit.rect(1, 1, w - 2, h - 2), "#555555", 2, op=.5)
    bx0, by0, bx1, by1 = buddy.rect()
    bw, bh = bx1 - bx0, by1 - by0
    b = kit.Ctx(bw, bh)
    b.flat(kit.ellipse(bw / 2, bh * .68, bw * .42, bh * .28), "#777777", op=.45)
    b.flat(kit.circle(bw * .7, bh * .3, bw * .22), "#777777", op=.45)
    b.stroke(kit.rect(1, 1, bw - 2, bh - 2), "#555555", 2, op=.5)
    return (x0, y0, w, h, c.svg()), (bx0, by0, bw, bh, b.svg())


def preview(scene, out_png, states=None, decos=True, doll=True, sky=SKY_SAMPLE, dpr=1):
    """Compose bg + things at their JSON boxes (z order, decos behind) into a 600 x 800 PNG the way
    the app draws it. states: {thing_id: state} to pick a state (default: the first)."""
    states = states or {}
    j = json.loads(scene.json_path.read_text())
    d = scene.art_dir
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        tmp = pathlib.Path(tmp)
        bg = (d / "bg.svg").read_text().replace(kit.SKY_TOKEN, sky)
        (tmp / "bg.svg").write_text(bg)
        items = [(0, 0, _img(tmp / "bg.svg", 0, 0, SCENE_W, SCENE_H))]
        order = 1
        for t in (j["decos"] if decos else []) + j["things"]:
            st = states.get(t["id"], t.get("states", [""])[0])
            f = d / (f"{t['id']}_{st}.svg" if st else f"{t['id']}.svg")
            text = f.read_text().replace(kit.SKY_TOKEN, sky)
            (tmp / f.name).write_text(text)
            x, y, w, h = t["x"] * SCENE_W, t["y"] * SCENE_H, t["w"] * SCENE_W, t["h"] * SCENE_H
            items.append((t.get("z", 6), order, _img(tmp / f.name, x - w / 2, y - h / 2, w, h)))
            order += 1
        if doll:
            for i, (x, y, w, h, svg) in enumerate(_doll(scene.stand, scene.buddy)):
                (tmp / f"doll{i}.svg").write_text(svg)
                items.append((AVATAR_Z, order + i, _img(tmp / f"doll{i}.svg", x, y, w, h)))
        items.sort(key=lambda it: (it[0], it[1]))
        html = (f'<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;background:#888">'
                f'<div style="position:relative;width:{SCENE_W}px;height:{SCENE_H}px;overflow:hidden">'
                + "".join(it[2] for it in items) + "</div></body></html>")
        (tmp / "page.html").write_text(html)
        (tmp / "shot.js").write_text(SHOT_JS)
        pathlib.Path(out_png).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["node", str(tmp / "shot.js"), str(tmp / "page.html"), str(out_png), str(SCENE_W), str(SCENE_H), str(dpr)],
                       check=True, cwd=tmp)
    print(out_png)
    return out_png
