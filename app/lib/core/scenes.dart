import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'content.dart';

/// A box in a scene: 0～1 of the 600×800 picture. For things [y] is the
/// centre; for the stand and the buddy it is the feet (docs/art.md).
class SceneBox {
  const SceneBox(this.x, this.y, this.w, this.h);

  final double x, y, w, h;

  static SceneBox? from(dynamic j) {
    if (j is! Map) return null;
    double? d(String k) => j[k] is num ? (j[k] as num).toDouble() : null;
    final x = d('x'), y = d('y'), w = d('w'), h = d('h');
    if (x == null || y == null || w == null || h == null) return null;
    return SceneBox(x, y, w, h);
  }

  double get left => x - w / 2;
  double get top => y - h / 2;

  /// The feet box's top (its [y] is the bottom edge).
  double get standTop => y - h;
}

/// Something in a scene that can be tapped and named.
class Thing {
  const Thing({required this.id, required this.zh, required this.en, required this.box, required this.z, this.states = const ['']});

  final String id;
  final String zh;
  final String en;
  final SceneBox box;
  final int z;
  final List<String> states;

  /// Its picture in [state] (docs/art.md `<id>_<state>.svg`).
  String file(String state) => state.isEmpty ? id : '${id}_$state';
}

/// A scene as laid out in `assets/scenes/<id>.json`.
class SceneData {
  const SceneData({required this.scene, required this.exits, required this.stand, required this.buddy, required this.things, required this.decos});

  final Scene scene;

  /// left / right / up / down / out / back → scene.
  final Map<String, Scene> exits;
  final SceneBox stand;
  final SceneBox buddy;
  final List<Thing> things;
  final List<Thing> decos;

  Thing? thing(String id) {
    for (final t in things) {
      if (t.id == id) return t;
    }
    return null;
  }

  static SceneData parse(Scene scene, String text) {
    final j = jsonDecode(text) as Map<String, dynamic>;
    List<Thing> things(String k, {bool decos = false}) => [
          if (j[k] is List)
            for (final t in (j[k] as List).whereType<Map>())
              if (SceneBox.from(t) case final box?)
                Thing(
                  id: '${t['id']}',
                  zh: '${t['zh'] ?? ''}',
                  en: '${t['en'] ?? ''}',
                  box: box,
                  z: decos ? (t['z'] is int ? t['z'] as int : 6) : (t['z'] is int ? t['z'] as int : 10),
                  states: t['states'] is List ? [for (final s in t['states'] as List) '$s'] : const [''],
                ),
        ];
    final exits = <String, Scene>{};
    if (j['exits'] is Map) {
      for (final e in (j['exits'] as Map).entries) {
        final s = Scene.values.asNameMap()['${e.value}'];
        if (s != null) exits['${e.key}'] = s;
      }
    }
    return SceneData(
      scene: scene,
      exits: exits,
      stand: SceneBox.from(j['stand']) ?? const SceneBox(0.42, 0.86, 0.34, 0.5),
      buddy: SceneBox.from(j['buddy']) ?? const SceneBox(0.68, 0.86, 0.2, 0.2),
      things: things('things'),
      decos: things('decos', decos: true),
    );
  }
}

/// The scenes, read once from the assets.
final scenesProvider = FutureProvider<Map<Scene, SceneData>>((ref) async {
  final out = <Scene, SceneData>{};
  for (final s in Scene.values) {
    try {
      out[s] = SceneData.parse(s, await rootBundle.loadString('assets/scenes/${s.name}.json', cache: false));
    } catch (_) {
      // A scene without a file yet: an empty page.
      out[s] = SceneData(scene: s, exits: const {}, stand: const SceneBox(0.42, 0.86, 0.34, 0.5), buddy: const SceneBox(0.68, 0.86, 0.2, 0.2), things: const [], decos: const []);
    }
  }
  return out;
});

/// Where a picture lives (docs/art.md).
abstract final class ArtPath {
  static String scene(Scene s, String file) => 'assets/art/scenes/${s.name}/$file.svg';
  static String prop(String name) => 'assets/art/props/$name.svg';
  static String clock(String name) => 'assets/art/clock/$name.svg';
  static String reward(String name) => 'assets/art/rewards/$name.svg';
  static String buddy(Buddy b, String pose) => 'assets/art/buddy/${b.name}_$pose.svg';
  static String avatarBody(String pose, int shirt) => 'assets/art/avatar/body_${pose}_$shirt.svg';
  static String avatarHead(int skin) => 'assets/art/avatar/head_$skin.svg';
  static String avatarFace(Mood m) => 'assets/art/avatar/face_${m.name}.svg';
  static String avatarHair(int n) => 'assets/art/avatar/hair_$n.svg';

  /// A step's picture name (steps.dart): `scene/thing` or a prop.
  static String of(String name) {
    final slash = name.indexOf('/');
    if (slash > 0) {
      final s = Scene.values.asNameMap()[name.substring(0, slash)];
      if (s != null) return scene(s, name.substring(slash + 1));
    }
    return prop(name);
  }
}
