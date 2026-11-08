"""Writes the pictures of 小小生活家 (kit.py: pop-up book paper layers) and checks them.

    python3 build.py living                      # one scene: app/assets/art/scenes/living/*.svg + scenes/living.json
    python3 build.py avatar                      # one plain module from the registry (its build())
    python3 build.py all                         # every scene and every registered module, then check
    python3 build.py check                       # only the checks: flutter_svg rules on every SVG under
                                                 # app/assets/art, every scene JSON (boxes 0-1, files for
                                                 # every thing/state/deco, viewBox aspect = box within 2 %)
    python3 build.py preview living OUT.png      # the room composed the way the app draws it (Chromium)
    python3 build.py preview living OUT.png lamp=off plant=wilt toybox=full nodecos nodoll
    python3 build.py fluttercheck [living|all]   # draw every file with the real flutter_svg (a throw-away
                                                 # Flutter project in /dev/shm, deleted afterwards) and
                                                 # with Chromium, and compare them

THE REGISTRY. Scenes are found by file name: any room_<x>.py or place_<x>.py here that defines
`SCENE = scene.Scene(...)` is built by `python3 build.py <x>` and by `all`. Other picture modules
(avatar.py, buddy.py, clock.py, rewards.py, props_<x>.py) are found the same way when they define a
`build()` function: list a new prefix or name in MODULES / MODULE_PREFIXES below and `all` picks it
up; `python3 build.py <module name>` runs its build() (the registry is just these two tuples).

Needs: Python 3 (no third-party packages for building), Node.js with Playwright (Chromium) for
preview and fluttercheck, numpy + Pillow for fluttercheck, Flutter at /home/user/flutter/bin (or
$FLUTTER) with flutter_svg already in the pub cache. Never run git from here: the main session commits.
"""
import sys

sys.dont_write_bytecode = True      # no __pycache__ in design/art

import importlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import pathlib  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402

import kit  # noqa: E402
import scene  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
SCRATCH = scene.SCRATCH

# ---------------------------------------------------------------- the registry
SCENE_PREFIXES = ("room_", "place_")                     # <prefix><name>.py with SCENE = scene.Scene(...)
MODULES = ("avatar", "buddy", "clock", "rewards")        # <name>.py with build()  (built when present)
MODULE_PREFIXES = ("props_",)                            # <prefix><x>.py with build()


def scene_modules():
    """{scene id: module name} for every room_/place_ file here."""
    out = {}
    for pre in SCENE_PREFIXES:
        for p in sorted(HERE.glob(f"{pre}*.py")):
            out[p.stem[len(pre):]] = p.stem
    return out


def plain_modules():
    out = [m for m in MODULES if (HERE / f"{m}.py").exists()]
    for pre in MODULE_PREFIXES:
        out += sorted(p.stem for p in HERE.glob(f"{pre}*.py"))
    return out


def load_scene(name):
    mods = scene_modules()
    if name not in mods:
        raise SystemExit(f"no scene {name!r} (scenes: {', '.join(sorted(mods)) or 'none'})")
    return importlib.import_module(mods[name]).SCENE


# ---------------------------------------------------------------- check
def check_all():
    n_svg = 0
    for p in sorted(kit.ART.rglob("*.svg")):
        kit.check_svg(str(p.relative_to(kit.ROOT)), p.read_text())
        n_svg += 1
    scenes = sorted(kit.SCENES_JSON.glob("*.json"))
    for j in scenes:
        scene.check_scene_files(j)
    ids = [json.loads(j.read_text())["id"] for j in scenes]
    print(f"check: {n_svg} SVG files are fine; {len(scenes)} scene(s) match their JSON: {', '.join(ids) or 'none'}")


# ---------------------------------------------------------------- flutter_svg against Chromium
DART_TEST = r"""
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/widgets.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('render svgs', (tester) async {
    final lines = File('list.txt').readAsLinesSync().where((l) => l.trim().isNotEmpty);
    final failed = <String>[];
    for (final line in lines) {
      final p = line.split('|');
      final w = int.parse(p[2]), h = int.parse(p[3]);
      await tester.runAsync(() async {
        try {
          final info = await vg.loadPicture(SvgStringLoader(File(p[0]).readAsStringSync()), null);
          final rec = ui.PictureRecorder();
          final c = Canvas(rec);
          c.scale(w / info.size.width, h / info.size.height);
          c.drawPicture(info.picture);
          final img = await rec.endRecording().toImage(w, h);
          final bytes = await img.toByteData(format: ui.ImageByteFormat.png);
          File(p[1]).writeAsBytesSync(bytes!.buffer.asUint8List());
          info.picture.dispose();
        } catch (e) {
          failed.add('${p[0]}: $e');
        }
      });
    }
    File('failed.txt').writeAsStringSync(failed.join('\n'));
  });
}
"""

CHROME_JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const lines = fs.readFileSync(process.argv[2], 'utf8').split('\n').filter(l => l.trim());
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 400, height: 400 }, deviceScaleFactor: 1 });
  for (const line of lines) {
    const [inp, out, w, h] = line.split('|');
    const svg = fs.readFileSync(inp);
    await page.setViewportSize({ width: +w, height: +h });
    await page.setContent(`<html><body style="margin:0;background:transparent"><img style="display:block;width:${w}px;height:${h}px" src="data:image/svg+xml;base64,${svg.toString('base64')}"></body></html>`);
    await page.waitForFunction(() => document.images[0].complete);
    await page.screenshot({ path: out, omitBackground: true });
  }
  await browser.close();
})();
"""


def _svg_files(which):
    if which == "all":
        return sorted(kit.ART.rglob("*.svg"))
    d = kit.ART / "scenes" / which
    if d.is_dir():
        return sorted(d.glob("*.svg"))
    d = kit.ART / which
    if d.is_dir():
        return sorted(d.rglob("*.svg"))
    raise SystemExit(f"nothing to check for {which!r}")


def fluttercheck(which="all", keep=False, px=400):
    """Draw every SVG with flutter_svg (the app's renderer) and with Chromium; report the files whose
    pictures differ. The sky token is replaced by a colour first, as the app does."""
    import numpy as np
    from PIL import Image
    files = _svg_files(which)
    if not files:
        raise SystemExit(f"nothing to check for {which!r}")
    flutter = pathlib.Path(os.environ.get("FLUTTER", "/home/user/flutter/bin")) / "flutter"
    work = pathlib.Path(tempfile.mkdtemp(prefix="svgcheck_", dir=SCRATCH))
    try:
        for sub in ("lib", "test", "out", "src"):
            (work / sub).mkdir()
        (work / "pubspec.yaml").write_text("name: svgcheck\npublish_to: 'none'\nversion: 0.0.1\nenvironment:\n  sdk: ^3.13.7\n"
                                           "dependencies:\n  flutter:\n    sdk: flutter\n  flutter_svg: ^2.3.0\n"
                                           "dev_dependencies:\n  flutter_test:\n    sdk: flutter\n")
        (work / "lib" / "main.dart").write_text("void main() {}\n")
        (work / "test" / "render_test.dart").write_text(DART_TEST)
        (work / "shot.js").write_text(CHROME_JS)
        fl, cr = [], []
        for i, f in enumerate(files):
            src = work / "src" / f"{i}.svg"
            src.write_text(f.read_text().replace(kit.SKY_TOKEN, scene.SKY_SAMPLE))
            vw, vh = kit.viewbox_of(f)
            s = px / max(vw, vh)
            w, h = max(8, round(vw * s)), max(8, round(vh * s))
            fl.append(f"{src}|{work / 'out' / f'{i}_f.png'}|{w}|{h}")
            cr.append(f"{src}|{work / 'out' / f'{i}_c.png'}|{w}|{h}")
        (work / "list.txt").write_text("\n".join(fl))
        (work / "crlist.txt").write_text("\n".join(cr))
        r = subprocess.run([str(flutter), "pub", "get", "--offline"], cwd=work, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-2000:], r.stderr[-2000:])
            raise SystemExit("flutter pub get --offline failed (is flutter_svg in the pub cache?)")
        r = subprocess.run([str(flutter), "test", "test/render_test.dart"], cwd=work, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-3000:], r.stderr[-3000:])
            raise SystemExit("flutter test failed")
        failed = (work / "failed.txt").read_text().strip()
        if failed:
            print("flutter_svg could not draw:\n" + failed)
        subprocess.run(["node", str(work / "shot.js"), str(work / "crlist.txt")], cwd=work, check=True)
        rows = []
        for i, f in enumerate(files):
            a = work / "out" / f"{i}_f.png"
            b = work / "out" / f"{i}_c.png"
            if not a.exists():
                rows.append((1.0, 1.0, f))
                continue
            A = np.asarray(Image.open(a).convert("RGBA")).astype(float)
            B = np.asarray(Image.open(b).convert("RGBA")).astype(float)

            def flat(X):   # over white
                al = X[..., 3:4] / 255
                return X[..., :3] * al + 255 * (1 - al)
            D = np.abs(flat(A) - flat(B)).max(axis=2)
            # single differing pixels are anti-aliasing; count pixels whose whole neighbourhood differs
            big = D > 60
            core = big[1:-1, 1:-1] & big[:-2, 1:-1] & big[2:, 1:-1] & big[1:-1, :-2] & big[1:-1, 2:]
            rows.append((core.mean(), D.mean() / 255, f))
        rows.sort(key=lambda r: (-r[0], -r[1]))
        bad = [r for r in rows if r[0] > .004]
        print(f"fluttercheck: {len(files)} files; worst:")
        for frac, mean, f in rows[:8]:
            print(f"  {frac * 100:6.2f}% solid differences, mean {mean * 100:.2f}%  {f.relative_to(kit.ROOT)}")
        if keep:
            print("kept", work)
        if bad or failed:
            raise SystemExit(f"{len(bad)} files draw differently in flutter_svg (more than 0.4% of the picture)")
        print("fluttercheck: flutter_svg draws every file like Chromium")
    finally:
        if not keep:
            shutil.rmtree(work, ignore_errors=True)


# ---------------------------------------------------------------- main
def main(argv):
    if not argv:
        print(__doc__)
        return
    cmd, rest = argv[0], argv[1:]
    scenes = scene_modules()
    if cmd == "all":
        for name in sorted(scenes):
            load_scene(name).build()
        for m in plain_modules():
            importlib.import_module(m).build()
        check_all()
    elif cmd == "check":
        check_all()
    elif cmd == "preview":
        if len(rest) < 2:
            raise SystemExit("preview <scene> OUT.png [thing=state ...] [nodecos] [nodoll]")
        states = dict(a.split("=", 1) for a in rest[2:] if "=" in a)
        scene.preview(load_scene(rest[0]), rest[1], states=states, decos="nodecos" not in rest, doll="nodoll" not in rest)
    elif cmd == "fluttercheck":
        fluttercheck(rest[0] if rest and not rest[0].startswith("--") else "all", keep="--keep" in rest)
    elif cmd in scenes:
        load_scene(cmd).build()
    elif cmd in plain_modules():
        importlib.import_module(cmd).build()
    else:
        raise SystemExit(f"unknown: {cmd} (scenes: {', '.join(sorted(scenes)) or 'none'}; modules: {', '.join(plain_modules()) or 'none'})")


if __name__ == "__main__":
    main(sys.argv[1:])
