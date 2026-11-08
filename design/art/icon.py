"""小小生活家's app icon, in the pop-up book look of the rest of the art (kit.py: cut-paper layers with a
thickness and a soft shadow). The picture: the little paper house (pink walls, mint roof) with a big,
friendly round clock in front of it (a wooden rim, a small face, one coral hand), on a cream-yellow
paper background with faint polka dots.

    python3 icon.py preview OUT.png      # the icon big (512), as a phone cuts it (round, rounded square)
                                         # at 96 and 48 px, and at 48 px on a light and a dark home screen
    python3 icon.py export               # writes the Android and iOS icons into app/

export writes (the same files as the sibling apps' icon.py)
- Android, full square art: app/android/app/src/main/res/mipmap-{mdpi..xxxhdpi}/ic_launcher.png
  (48..192 px, opaque).
- Android adaptive icon (API 26+): mipmap-anydpi-v26/ic_launcher.xml, with
  drawable-{mdpi..xxxhdpi}/ic_launcher_foreground.png and ic_launcher_background.png (108 dp canvas;
  the whole subject stays inside the central 66 dp circle, the part every launcher mask shows).
- iOS: every PNG listed in app/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json, at its
  size, opaque (no alpha).

Everything is drawn in 200 x 200 units with kit.Ctx, rendered at 1024 px by Chromium (Node.js with
Playwright; one browser for all the pictures) and scaled down with Pillow. Deterministic: no randomness,
so the same script gives the same bytes. Scratch files go to /dev/shm and are deleted.
"""
import sys

sys.dont_write_bytecode = True      # no __pycache__ in design/art

import json  # noqa: E402
import math  # noqa: E402
import pathlib  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import kit  # noqa: E402
from kit import CORAL, DARK, MINT, PAPER, PINK, SKY, WOOD, WOOD_DK, WOOD_DEEP, YELLOW, circle, path, poly, rrect  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APP = ROOT / "app"
RES = APP / "android" / "app" / "src" / "main" / "res"
IOS = APP / "ios" / "Runner" / "Assets.xcassets" / "AppIcon.appiconset"
FONT = APP / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"

U = 200                              # drawing units across the icon
C = 1024                             # rendered size, scaled down from here
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
VIEW = 72 / 108                      # how much of the adaptive canvas a launcher shows
SAFE_R = .44 * U                     # the subject (shadows aside) stays within this radius of the middle, so
                                     # the adaptive foreground (VIEW times smaller) is inside the 66 dp circle

BG = "#FFE8A9"                       # cream-yellow paper
BG_DOT = "#F3D68C"
CLOCK_FACE = "#FFF9EC"


class View:
    """A kit.Ctx seen through a scale about the middle: the adaptive layers draw the same picture VIEW
    times smaller. All coordinates and sizes are in the icon's 200 units."""

    def __init__(self, c, view):
        self.c, self.v = c, view

    def s(self, shape):
        return shape.scale(self.v, U / 2, U / 2)

    def layer(self, shape, col, **kw):
        self.c.layer(self.s(shape), col, **kw)

    def flat(self, shape, col, **kw):
        self.c.flat(self.s(shape), col, **kw)

    def stroke(self, shape, col, w, **kw):
        self.c.stroke(self.s(shape), col, w, **kw)

    def face(self, x, y, size, mood="happy", **kw):
        px, py = U / 2 + (x - U / 2) * self.v, U / 2 + (y - U / 2) * self.v
        self.c.face(px, py, size * self.v, mood, **kw)


# ================================================================ the picture
def background(c, view):
    """Cream-yellow paper filling the whole square, faint polka dots placed from the middle."""
    c.flat(kit.rect(0, 0, U, U), BG)
    v = View(c, view)
    pts = []
    for row in range(9):
        for col in range(9):
            x = 12 + col * 22 + (11 if row % 2 else 0)
            y = 12 + row * 22
            if 0 < x < U and 0 < y < U:
                pts.append((x, y))
    for x, y in pts:
        v.flat(circle(x, y, 2.4), BG_DOT)


def subject(c, view):
    """The paper house behind, the big clock in front."""
    v = View(c, view)
    hx, roof_y, body_y = 100, 22, 64                    # the house: middle x, roof peak y, the walls' top
    v.layer(rrect(124, 34, 14, 36, 3), WOOD_DK, depth=3, shadow=False)                 # the chimney
    v.flat(rrect(121, 31, 20, 8, 3), WOOD_DEEP)
    v.layer(rrect(46, body_y, 108, 90, 8), PINK, depth=5)                              # the walls
    for wx in (62, 138):                                                               # two windows
        v.layer(rrect(wx - 11, 76, 22, 20, 4), SKY, depth=2, shadow=False)
        v.stroke(path([(wx, 76), (wx, 96)]), PAPER, 2)
        v.stroke(path([(wx - 11, 86), (wx + 11, 86)]), PAPER, 2)
    v.layer(poly([(32, body_y + 4), (hx, roof_y), (168, body_y + 4)]), MINT, depth=5)  # the roof
    v.flat(poly([(52, body_y - 4), (hx, roof_y + 12), (148, body_y - 4)]), kit.lt(MINT, .2), op=.6)
    v.layer(circle(hx, 50, 7), YELLOW, depth=2, shadow=False)                          # the attic window
    # the clock
    cx, cy, r = 100, 132, 50
    v.layer(circle(cx, cy, r), WOOD, depth=6)                                          # the wooden rim
    v.flat(circle(cx, cy, r - 9), CLOCK_FACE)
    for i in range(12):                                                                # the marks
        a = math.radians(i * 30 - 90)
        big = i % 3 == 0
        rr = r - 16
        v.flat(circle(cx + rr * math.cos(a), cy + rr * math.sin(a), 3.2 if big else 1.8), CORAL if big else WOOD_DK)
    v.face(cx, cy + 12, 8.5, "happy")                                                  # the face, low on the dial
    v.stroke(path([(cx, cy), (cx + 16, cy - 26)]), CORAL, 6.5)                         # the coral hand
    v.layer(circle(cx, cy, 5), CORAL, depth=2, shadow=False)                           # the pin
    v.flat(circle(cx - 1.5, cy - 1.5, 1.6), PAPER, op=.8)


def check_safe():
    """Every piece of the subject (without its shadow) is within SAFE_R of the middle."""
    far = [(100, 22), (32, 68), (168, 68), (138, 31), (46, 154), (154, 154)]      # roof, chimney, walls
    worst = max([math.hypot(x - U / 2, y - U / 2) for x, y in far] + [132 - 100 + 50])   # and the clock's bottom
    if worst > SAFE_R * 1.02:
        sys.exit(f"icon: the subject reaches {worst:.1f} units from the middle (keep within {SAFE_R:.1f})")


def doc(c, px):
    text = c.svg()
    return text.replace("<svg ", f'<svg width="{px}" height="{px}" ', 1)


def subject_svg(adaptive):
    c = kit.Ctx(U, U, scale=VIEW if adaptive else 1.0)
    subject(c, VIEW if adaptive else 1.0)
    return doc(c, C)


def background_svg(adaptive):
    c = kit.Ctx(U, U, scale=VIEW if adaptive else 1.0)
    background(c, VIEW if adaptive else 1.0)
    return doc(c, C)


# ================================================================ rendering
RENDER_JS = """
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  for (const [inp, out, px] of jobs) {
    for (let tries = 1; ; tries++) {          // a screenshot now and then fails while the machine is busy
      const page = await browser.newPage({ viewport: { width: px, height: px }, deviceScaleFactor: 1 });
      try {
        await page.goto('file://' + inp);
        await page.screenshot({ path: out, omitBackground: true });
        break;
      } catch (e) {
        if (tries >= 3) throw e;
      } finally {
        await page.close();
      }
    }
  }
  await browser.close();
})();
"""


def render_all(svgs):
    """{key: svg text} -> {key: RGBA image}, all drawn by one Chromium."""
    shm = "/dev/shm" if pathlib.Path("/dev/shm").is_dir() else None
    with tempfile.TemporaryDirectory(dir=shm, prefix="live_icon_") as tmp:
        tmp = pathlib.Path(tmp)
        jobs = []
        for i, (key, text) in enumerate(svgs.items()):
            src, out = tmp / f"{i}.svg", tmp / f"{i}.png"
            src.write_text(text)
            jobs.append([str(src), str(out), C])
        (tmp / "jobs.json").write_text(json.dumps(jobs))
        (tmp / "r.js").write_text(RENDER_JS)
        subprocess.run(["node", str(tmp / "r.js"), str(tmp / "jobs.json")], check=True, cwd=HERE)
        return {key: Image.open(tmp / f"{i}.png").convert("RGBA").copy() for i, key in enumerate(svgs)}


def art():
    """(full square art RGB, adaptive background RGB, adaptive foreground RGBA)."""
    check_safe()
    for key, text in (("fg", subject_svg(False)), ("afg", subject_svg(True)), ("bg", background_svg(False)),
                      ("abg", background_svg(True))):
        kit.check_svg(f"icon/{key}", text)
    im = render_all({"bg": background_svg(False), "fg": subject_svg(False),
                     "abg": background_svg(True), "afg": subject_svg(True)})
    full = Image.alpha_composite(im["bg"], im["fg"]).convert("RGB")
    return full, im["abg"].convert("RGB"), im["afg"]


def launcher_view(bg, fg):
    """The adaptive icon as a launcher shows it: both layers, the middle 72 dp of 108."""
    whole = Image.alpha_composite(bg.convert("RGBA"), fg).convert("RGB")
    k = C * 18 / 108
    return whole.crop((round(k), round(k), round(C - k), round(C - k)))


def resized(img, px):
    return img.resize((px, px), Image.LANCZOS)


def mask(kind, px):
    s = px * 4
    m = Image.new("L", (s, s), 0)
    dr = ImageDraw.Draw(m)
    if kind == "round":
        dr.ellipse((0, 0, s - 1, s - 1), fill=255)
    elif kind == "squircle":
        pts = []
        for i in range(720):
            t = 2 * math.pi * i / 720
            c, si = math.cos(t), math.sin(t)
            pts.append((s / 2 + s / 2 * math.copysign(abs(c) ** (2 / 5), c), s / 2 + s / 2 * math.copysign(abs(si) ** (2 / 5), si)))
        dr.polygon(pts, fill=255)
    else:                                       # iOS-like rounded square
        dr.rounded_rectangle((0, 0, s - 1, s - 1), radius=s * .225, fill=255)
    return m.resize((px, px), Image.LANCZOS)


# ================================================================ preview
SIBLINGS = (("畫畫小鎮", "APP_Kids_Paint"), ("字母寵物", "app_kids_paint_for_learning_writing"), ("動物小餐廳", "app_kids_cook"),
            ("小卡認天下", "app_kids_card_game"), ("想一想樂園", "app_kids_brainstorming"), ("眼尖尖", "app_kids_falsecharge"),
            ("迷宮小冒險", "app_kids_maze"))


def font(size):
    try:
        return ImageFont.truetype(str(FONT), size)
    except OSError:
        return ImageFont.load_default()


def siblings():
    out = []
    for zh, repo in SIBLINGS:
        p = ROOT.parent / repo / "app" / "android" / "app" / "src" / "main" / "res" / "mipmap-xxxhdpi" / "ic_launcher.png"
        if p.is_file():
            out.append((zh, Image.open(p).convert("RGB")))
    return out


def home_screen(icons, dark, W):
    """A strip of a phone's home screen: icons (label, image) at 48 px, round, with their names."""
    H = 104
    top, bottom = ("#3A3550", "#1E1B2B") if dark else ("#F6EFE6", "#E3EEF8")
    strip = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(strip)
    for y in range(H):
        dr.line([(0, y), (W, y)], fill=kit.mix(top, bottom, y / (H - 1)))
    step = W / len(icons)
    f = font(13)
    for i, (label, im) in enumerate(icons):
        x = round(step * i + step / 2 - 24)
        strip.paste(resized(im, 48), (x, 18), mask("round", 48))
        tw = dr.textlength(label, font=f)
        dr.text((x + 24 - tw / 2, 74), label, font=f, fill="#FFFFFF" if dark else "#3B3550")
    return strip


def preview(out):
    full, abg, afg = art()
    view = launcher_view(abg, afg)
    pad, big = 24, 512
    W = pad * 2 + big + 40 + 420
    H = pad + big + pad + 104 * 2 + pad
    sheet = Image.new("RGB", (W, H), "#FFFFFF")
    dr = ImageDraw.Draw(sheet)
    sheet.paste(resized(full, big), (pad, pad))                                  # the full square art, big
    x, y = pad + big + 40, pad
    f = font(22)
    dr.text((x, y), "adaptive (round, squircle), full art: 96 / 48 px", font=f, fill="#3B3550")
    y += 40
    for kind, im, s in (("round", view, 96), ("squircle", view, 96), ("square", full, 96)):
        sheet.paste(resized(im, s), (x, y), mask(kind, s))
        x += s + 24
    x, y = pad + big + 40, pad + 40 + 96 + 24
    for kind, im, s in (("round", view, 48), ("squircle", view, 48), ("square", full, 48), ("round", view, 36)):
        sheet.paste(resized(im, s), (x, y + 48 - s), mask(kind, s))
        x += s + 24
    y = pad + big + pad
    icons = siblings() + [("小小生活家", view)]
    sheet.paste(home_screen(icons, False, W - 2 * pad), (pad, y))
    sheet.paste(home_screen(icons, True, W - 2 * pad), (pad, y + 104))
    sheet.save(out)
    print(out)


# ================================================================ export
ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
"""


def export():
    full, bg, fg = art()
    written = []
    for d, k in DENSITIES.items():
        mip = RES / f"mipmap-{d}"
        mip.mkdir(parents=True, exist_ok=True)
        resized(full, round(48 * k)).save(mip / "ic_launcher.png")
        dr = RES / f"drawable-{d}"
        dr.mkdir(parents=True, exist_ok=True)
        resized(fg, round(108 * k)).save(dr / "ic_launcher_foreground.png")
        resized(bg, round(108 * k)).save(dr / "ic_launcher_background.png")
        written += [mip / "ic_launcher.png", dr / "ic_launcher_foreground.png", dr / "ic_launcher_background.png"]
    anydpi = RES / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    (anydpi / "ic_launcher.xml").write_text(ADAPTIVE_XML)
    written.append(anydpi / "ic_launcher.xml")
    contents = json.loads((IOS / "Contents.json").read_text())
    sizes = {}
    for image in contents["images"]:
        if image.get("filename"):
            px = round(float(image["size"].split("x")[0]) * float(image["scale"].rstrip("x")))
            if sizes.setdefault(image["filename"], px) != px:
                sys.exit(f"{image['filename']} is listed at two sizes in Contents.json")
    for fname, px in sizes.items():
        resized(full, px).convert("RGB").save(IOS / fname)
        written.append(IOS / fname)
    manifest = (APP / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text()
    if 'android:icon="@mipmap/ic_launcher"' not in manifest:
        print("note: AndroidManifest.xml's android:icon is not @mipmap/ic_launcher")
    for p in written:
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "export":
        export()
    elif len(sys.argv) >= 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        print(__doc__)
