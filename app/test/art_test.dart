import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:little_life/core/content.dart';
import 'package:little_life/core/scenes.dart';
import 'package:little_life/core/steps.dart';

/// Every picture the program asks for exists (docs/art.md), and every scene
/// file has the things the program looks for.
void main() {
  bool has(String path) => File(path).existsSync();

  test('every prop the little games use is drawn', () {
    final missing = [for (final p in allStepProps()) if (!has(ArtPath.of(p))) p];
    expect(missing, isEmpty, reason: 'draw these in design/art/props_*.py or the scene');
  });

  test('the puppets, buddies, clock and rewards are all there', () {
    final missing = <String>[];
    for (final pose in ['stand', 'sit', 'lie']) {
      for (var s = 1; s <= Avatar.shirts; s++) {
        if (!has(ArtPath.avatarBody(pose, s))) missing.add('body_${pose}_$s');
      }
    }
    for (var k = 1; k <= Avatar.skins; k++) {
      if (!has(ArtPath.avatarHead(k))) missing.add('head_$k');
    }
    for (var h = 1; h <= Avatar.hairs; h++) {
      if (!has(ArtPath.avatarHair(h))) missing.add('hair_$h');
    }
    for (final m in Mood.values) {
      if (!has(ArtPath.avatarFace(m))) missing.add('face_${m.name}');
    }
    if (!has('assets/art/avatar/layout.json')) missing.add('layout.json');
    for (final b in Buddy.values) {
      for (final pose in ['stand', 'sleep', 'happy', 'eat']) {
        if (!has(ArtPath.buddy(b, pose))) missing.add('${b.name}_$pose');
      }
    }
    for (final n in ['face', 'hand', for (final i in ClockIcon.values) 't_${i.name}', for (final w in Weather.values) 'w_${w.name}']) {
      if (!has(ArtPath.clock(n))) missing.add('clock/$n');
    }
    for (final n in [for (final t in Task.values) t.sticker, 'sticker_blank', 'sticker_heart', 'chart', 'house_small', 'height']) {
      if (!has(ArtPath.reward(n))) missing.add('rewards/$n');
    }
    expect(missing, isEmpty);
  });

  test('every scene has its file, its exits, the things the program looks for and three decorations', () {
    final needed = {
      Scene.living: ['sofa', 'toybox', 'phone', 'window', 'stairs', 'lamp', 'rug', 'table', 'shelf', 'plant'],
      Scene.bedroom: ['bed', 'wardrobe', 'nightlight', 'curtain', 'book', 'height'],
      Scene.bathroom: ['sink', 'toilet', 'bathtub', 'towel', 'mirror'],
      Scene.kitchen: ['fridge', 'table', 'sink', 'stove'],
      Scene.entrance: ['door', 'shoerack', 'bag', 'umbrella'],
      Scene.balcony: ['plants', 'rack', 'bowl', 'bins'],
      Scene.street: ['home', 'park', 'school', 'market', 'clinic'],
      Scene.park: ['slide', 'swing', 'sandbox', 'ball'],
      Scene.school: ['cubby', 'teacher', 'classmate_1', 'classmate_2', 'mat'],
      Scene.market: ['shelf', 'cart', 'cashier'],
      Scene.clinic: ['doctor', 'desk', 'bed'],
    };
    for (final s in Scene.values) {
      final file = File('assets/scenes/${s.name}.json');
      expect(file.existsSync(), isTrue, reason: s.name);
      final data = SceneData.parse(s, file.readAsStringSync());
      expect(data.decos.length, 3, reason: s.name);
      for (final id in needed[s]!) {
        final t = data.thing(id);
        expect(t, isNotNull, reason: '${s.name}/$id');
        for (final st in t!.states) {
          expect(has(ArtPath.scene(s, t.file(st))), isTrue, reason: '${s.name}/${t.file(st)}');
        }
        expect(t.box.left, greaterThanOrEqualTo(-0.01), reason: '${s.name}/$id');
        expect(t.box.left + t.box.w, lessThanOrEqualTo(1.01), reason: '${s.name}/$id');
      }
      for (final d in data.decos) {
        expect(has(ArtPath.scene(s, d.id)), isTrue, reason: '${s.name}/${d.id}');
      }
      expect(has(ArtPath.scene(s, 'bg')), isTrue, reason: s.name);
      expect(File(ArtPath.scene(s, 'bg')).readAsStringSync(), contains('#SKY'), reason: '${s.name} bg has the sky placeholder');
      if (s.home) {
        expect(data.exits, isNotEmpty, reason: s.name);
      } else if (s != Scene.street) {
        expect(data.exits['back'], Scene.street, reason: s.name);
      }
    }
    // The targets of every task, chore and happening are things in their scenes.
    for (final t in Task.values) {
      if (t == Task.chore) continue;
      final data = SceneData.parse(t.scene, File('assets/scenes/${t.scene.name}.json').readAsStringSync());
      expect(data.thing(t.target), isNotNull, reason: '${t.name} → ${t.scene.name}/${t.target}');
    }
    for (final c in Chore.values) {
      final data = SceneData.parse(c.scene, File('assets/scenes/${c.scene.name}.json').readAsStringSync());
      expect(data.thing(c.target), isNotNull, reason: '${c.name} → ${c.scene.name}/${c.target}');
    }
    for (final h in Happening.values) {
      final s = h.scene;
      if (s == null) continue;
      final data = SceneData.parse(s, File('assets/scenes/${s.name}.json').readAsStringSync());
      expect(data.thing(h.target!), isNotNull, reason: '${h.name} → ${s.name}/${h.target}');
    }
  });

  test('the house is in order: the rooms join up as docs/design.md says', () {
    SceneData load(Scene s) => SceneData.parse(s, File('assets/scenes/${s.name}.json').readAsStringSync());
    expect(load(Scene.living).exits, {'left': Scene.kitchen, 'right': Scene.entrance, 'up': Scene.bedroom});
    expect(load(Scene.kitchen).exits['left'], Scene.balcony);
    expect(load(Scene.bedroom).exits['right'], Scene.bathroom);
    expect(load(Scene.bathroom).exits['down'], Scene.living);
    expect(load(Scene.entrance).exits['out'], Scene.street);
  });

  test('no picture uses what flutter_svg cannot draw, and none is too big', () {
    final bad = <String>[];
    for (final f in Directory('assets/art').listSync(recursive: true).whereType<File>()) {
      if (!f.path.endsWith('.svg')) continue;
      final text = f.readAsStringSync();
      if (f.lengthSync() > 70 * 1024) bad.add('${f.path} too big');
      for (final no in ['<filter', '<mask', '<style', 'style=', '<text', '<image', '<pattern', 'mix-blend']) {
        if (text.contains(no)) bad.add('${f.path} uses $no');
      }
      if (!text.trimRight().endsWith('</svg>')) bad.add('${f.path} is cut off');
    }
    expect(bad, isEmpty);
  });
}
