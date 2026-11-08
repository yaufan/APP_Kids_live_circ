import 'dart:io';
import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:flutter/material.dart' hide Step;
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_life/app/app.dart';
import 'package:little_life/core/game.dart';
import 'package:little_life/core/providers.dart';
import 'package:little_life/core/sounds.dart';
import 'package:little_life/core/store.dart';
import 'package:little_life/core/voice.dart';
import 'package:little_life/features/play/play_screen.dart';
import 'package:little_life/features/play/step_views.dart';

final shotKey = GlobalKey();

/// The app on a phone screen, starting from [game].
class TestApp {
  TestApp(this.tester, this.store, this.sounds, this.voice);

  final WidgetTester tester;
  final MemoryStore store;
  final RecordingSounds sounds;
  final RecordingVoice voice;
  DateTime now = DateTime(2026, 11, 6, 10);

  ProviderContainer get container => ProviderScope.containerOf(tester.element(find.byType(LittleLifeApp)));
  Game get game => container.read(gameProvider);
  void change(Game Function(Game g) f) => container.read(gameProvider.notifier).change(f);

  static Future<TestApp> start(WidgetTester tester, {Game game = const Game(), Size size = const Size(1080, 2340), double ratio = 2.75, String at = '/', int seed = 1}) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = ratio;
    addTearDown(tester.view.reset);
    final store = MemoryStore();
    final app = TestApp(tester, store, RecordingSounds(), RecordingVoice());
    await tester.pumpWidget(RepaintBoundary(
      key: shotKey,
      child: ProviderScope(
        overrides: [
          storeProvider.overrideWithValue(store),
          savedGameProvider.overrideWithValue(game),
          randomProvider.overrideWithValue(math.Random(seed)),
          soundsProvider.overrideWithValue(app.sounds),
          voiceProvider.overrideWithValue(app.voice),
          clockProvider.overrideWithValue(() => app.now),
        ],
        child: const LittleLifeApp(),
      ),
    ));
    if (at != '/') app.go(at);
    await app.settle();
    return app;
  }

  void go(String location) => container.read(routerProvider).go(location);

  String get location => container.read(routerProvider).state.matchedLocation;

  /// Lets the pictures load and the screen move on [ms] milliseconds.
  Future<void> settle([int ms = 400]) async {
    for (var i = 0; i < 6; i++) {
      await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 20)));
      await tester.pump(Duration(milliseconds: ms ~/ 6));
    }
  }

  Future<void> tapLabel(String label, {int ms = 400}) async {
    await tester.tap(find.bySemanticsLabel(label).last);
    await settle(ms);
  }

  /// Scrolls a list until [label] shows, then taps it.
  Future<void> scrollTap(String label, {int ms = 400}) async {
    final f = find.bySemanticsLabel(label);
    if (f.evaluate().isEmpty || !tester.getRect(f.last).overlaps(Offset.zero & tester.view.physicalSize / tester.view.devicePixelRatio)) {
      await tester.scrollUntilVisible(f, 120, scrollable: find.byType(Scrollable).first);
      await settle(200);
    }
    await tapLabel(label, ms: ms);
  }

  Future<void> end() async {
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(milliseconds: 100));
  }
}

/// Real fonts for screenshots instead of the test font's boxes.
Future<void> loadFonts() async {
  final flutterRoot = Platform.environment['FLUTTER_ROOT'] ?? '/home/user/flutter';
  final fonts = {
    'MaterialIcons': ['$flutterRoot/bin/cache/artifacts/material_fonts/MaterialIcons-Regular.otf'],
    'Huninn': ['assets/fonts/jf-openhuninn-2.1.ttf'],
    'Roboto': ['assets/fonts/jf-openhuninn-2.1.ttf'],
  };
  for (final MapEntry(key: family, value: paths) in fonts.entries) {
    final loader = FontLoader(family);
    for (final path in paths.where((p) => File(p).existsSync())) {
      loader.addFont(File(path).readAsBytes().then(ByteData.sublistView));
    }
    await loader.load();
  }
}

Future<void> shoot(WidgetTester tester, String device, String name) => tester.runAsync(() async {
      final boundary = shotKey.currentContext!.findRenderObject()! as RenderRepaintBoundary;
      final image = await boundary.toImage(pixelRatio: 2);
      final png = await image.toByteData(format: ui.ImageByteFormat.png);
      File('build/screenshots/$device/$name.png')
        ..createSync(recursive: true)
        ..writeAsBytesSync(png!.buffer.asUint8List());
    });

/// Plays every step of the little game on screen the way a finger would.
Future<void> playThrough(TestApp app, {int? shotAt, Future<void> Function(String)? shot, String? name}) async {
  var guard = 0;
  var stepNo = 0;
  while (find.byType(PlayScreen).evaluate().isNotEmpty && guard++ < 40) {
    await app.settle(400);
    if (shotAt == stepNo && shot != null) await shot(name!);
    stepNo++;
    await playThroughOnce(app);
  }
  // The sticker shows, then the room comes back.
  await app.settle(2000);
}

/// One step of the little game on screen.
Future<void> playThroughOnce(TestApp app) async {
  final tester = app.tester;
  {
    final tapView = find.byType(TapView);
    final scrub = find.byType(ScrubView);
    final drag = find.byType(DragView);
    final choose = find.byType(ChooseView);
    final hold = find.byType(HoldView);
    if (tapView.evaluate().isNotEmpty) {
      final step = tester.widget<TapView>(tapView.last).step;
      final same = step.props.toSet().length == 1 && step.props.length > 1;
      for (var i = 0; i < step.props.length; i++) {
        final key = find.byKey(ValueKey('tap-${same ? math.min(i, step.props.length - 1) : i}'));
        if (key.evaluate().isEmpty) break;
        await tester.tap(key.last);
        await app.settle(250);
      }
    } else if (scrub.evaluate().isNotEmpty) {
      final box = tester.getRect(scrub.last);
      final side = math.min(box.width, box.height);
      final origin = Offset(box.center.dx - side / 2, box.center.dy - side / 2);
      final g = await tester.startGesture(origin + Offset(side * 0.1, side * 0.2));
      for (var row = 0; row < 8; row++) {
        for (var col = 0; col <= 10; col++) {
          final x = row.isEven ? col / 10 : 1 - col / 10;
          await g.moveTo(origin + Offset(side * (0.08 + 0.84 * x), side * (0.15 + 0.7 * row / 7)));
          await tester.pump(const Duration(milliseconds: 16));
        }
      }
      await g.up();
      await app.settle(500);
    } else if (drag.evaluate().isNotEmpty) {
      final step = tester.widget<DragView>(drag.last).step;
      final filled = <String, int>{};
      for (var i = 0; i < step.items.length; i++) {
        final item = step.items[i];
        final slot = step.slots.where((s) => s.takes(item) && (filled[s.id] ?? 0) < s.capacity).firstOrNull;
        if (slot == null) continue;
        filled[slot.id] = (filled[slot.id] ?? 0) + 1;
        final from = find.byKey(ValueKey('item-$i'));
        final to = find.byKey(ValueKey('slot-${slot.id}'));
        if (from.evaluate().isEmpty || to.evaluate().isEmpty) continue;
        final g = await tester.startGesture(tester.getCenter(from.last));
        await tester.pump(const Duration(milliseconds: 30));
        await g.moveTo(tester.getCenter(to.last));
        await tester.pump(const Duration(milliseconds: 30));
        await g.up();
        await app.settle(250);
      }
      await app.settle(400);
    } else if (choose.evaluate().isNotEmpty) {
      final step = tester.widget<ChooseView>(choose.last).step;
      final i = step.options.indexWhere((o) => step.good.contains(o.prop));
      await tester.tap(find.byKey(ValueKey('choice-$i')).last);
      await app.settle(900);
    } else if (hold.evaluate().isNotEmpty) {
      final step = tester.widget<HoldView>(hold.last).step;
      final g = await tester.startGesture(tester.getCenter(find.byKey(const ValueKey('hold')).last));
      // The first frame only starts the clock; the next one moves it.
      await tester.pump(const Duration(milliseconds: 50));
      await tester.pump(Duration(milliseconds: step.seconds * 1000 + 200));
      await tester.pump(const Duration(milliseconds: 50));
      await g.up();
      await app.settle(600);
    } else {
      await app.settle(400);
    }
  }
}
