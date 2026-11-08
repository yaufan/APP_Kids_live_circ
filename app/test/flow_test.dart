import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_life/core/content.dart';
import 'package:little_life/features/parent/parent_gate.dart';

import 'helpers.dart';

/// A whole day as a child would play it, on a phone and a tablet, with
/// screenshots in `build/screenshots/<device>/` (docs/design.md).
void main() {
  setUpAll(loadFonts);

  for (final MapEntry(key: device, value: (size, ratio)) in {'phone': (const Size(1080, 2340), 2.75), 'tablet': (const Size(1620, 2160), 2.0)}.entries) {
    testWidgets('a day in the life ($device)', (tester) async {
      final app = await TestApp.start(tester, size: size, ratio: ratio, seed: 3);
      Future<void> shot(String name) => shoot(tester, device, name);

      // Setup: a name, a look, a buddy.
      expect(app.location, '/setup');
      await tester.enterText(find.byKey(const ValueKey('name')), '小明');
      await app.scrollTap('頭髮 2');
      await app.scrollTap('衣服 4');
      await app.scrollTap('選一隻小夥伴 cat');
      await app.settle(600);
      await shot('01_setup');
      await app.scrollTap('開始過一天！', ms: 800);
      expect(app.location, '/');
      expect(app.game.profile!.name, '小明');
      expect(app.game.profile!.buddy, Buddy.cat);
      expect(app.game.day, isNotNull);
      await shot('02_living');

      // The clock says: wake up, in the bedroom. Go there and tap the bed.
      final plan = app.game.day!.plan(app.game.settings);
      expect(plan[0], Task.wake);
      await app.tapLabel('房間', ms: 900);
      await shot('03_bedroom');
      await tester.tap(find.byKey(const ValueKey('thing-bed')));
      await app.settle(700);
      expect(app.location, '/play/task/wake');
      await shot('04_play_wake');
      await playThrough(app, shotAt: 1, shot: shot, name: '05_play_wake_step');
      expect(app.game.day!.done, contains(Task.wake));
      expect(app.game.stickers[Task.wake], 1);
      expect(app.location, '/');

      // Brush teeth: through the door on the right to the bathroom.
      expect(app.game.day!.current(app.game.settings), Task.teeth);
      await app.tapLabel('往右：廁所', ms: 900);
      await tester.tap(find.byKey(const ValueKey('thing-sink')));
      await app.settle(700);
      expect(app.location, '/play/task/teeth');
      await playThrough(app, shotAt: 1, shot: shot, name: '06_play_teeth');
      expect(app.game.day!.done, contains(Task.teeth));

      // Tap a thing to hear its name.
      app.voice.said.clear();
      await tester.tap(find.byKey(const ValueKey('thing-bathtub')));
      await app.settle();
      expect(app.voice.said, contains('浴缸'));

      // The big clock: turn it to going to school.
      await app.tapLabel('時鐘：現在該做什麼？', ms: 800);
      await shot('07_clock');
      await tester.tap(find.bySemanticsLabel('時鐘：現在該做什麼？ 上學').last);
      await app.settle(600);
      expect(app.game.day!.current(app.game.settings), Task.schoolGo);
      await app.tapLabel('回去', ms: 600);
      expect(find.byKey(const ValueKey('big-clock')), findsNothing);

      // Something happens: 小明 needs the potty.
      app.change((g) => g.copyWith(day: g.day!.copyWith(active: Happening.pee, happened: {...g.day!.happened, ...Happening.values.where((h) => h != Happening.pee)})));
      await app.settle(800);
      await shot('08_happening_pee');
      await tester.tap(find.byKey(const ValueKey('thing-toilet')));
      await app.settle(700);
      expect(app.location, '/play/happening/pee');
      await shot('09_play_toilet');
      await playThrough(app);
      expect(app.game.day!.active, isNull);
      expect(app.game.day!.happened, contains(Happening.pee));

      // Out the front door to the street and the park, and home again.
      await app.tapLabel('下樓：客廳', ms: 900);
      await app.tapLabel('往右：門口', ms: 900);
      await shot('10_entrance');
      await tester.tap(find.byKey(const ValueKey('thing-door')));
      await app.settle(900);
      expect(find.byKey(const ValueKey('scene-street')), findsOneWidget);
      await shot('11_street');
      await tester.tap(find.byKey(const ValueKey('thing-park')));
      await app.settle(900);
      await shot('12_park');
      await app.tapLabel('小街', ms: 900);
      await tester.tap(find.byKey(const ValueKey('thing-school')));
      await app.settle(900);
      await shot('13_school');
      await app.tapLabel('客廳', ms: 900);
      expect(find.byKey(const ValueKey('scene-entrance')), findsOneWidget);
      await app.tapLabel('廚房', ms: 900);
      await shot('14_kitchen');
      await app.tapLabel('陽台', ms: 900);
      await shot('15_balcony');

      // The sticker chart.
      await app.tapLabel('貼紙表', ms: 900);
      expect(app.location, '/stickers');
      await shot('16_stickers');
      await app.tapLabel('回去', ms: 700);

      // Bedtime: turn the clock to sleep and do it; the house goes dark.
      app.change((g) => g.turnClock(plan.indexOf(Task.sleep)));
      await app.settle();
      await app.tapLabel('房間', ms: 900);
      await tester.tap(find.byKey(const ValueKey('thing-bed')));
      await app.settle(700);
      expect(app.location, '/play/task/sleep');
      await playThrough(app, shotAt: 3, shot: shot, name: '17_play_story');
      expect(app.location, '/night');
      await app.settle(2500);
      await shot('18_night');
      final weekday = app.game.day!.weekday;
      expect(app.game.daysDone, 1);
      expect(app.game.decos, 0, reason: 'not everything was done today');
      await tester.tap(find.byKey(const ValueKey('night')));
      await app.settle(900);
      expect(app.location, '/');
      expect(app.game.day!.weekday, Week.next(weekday));
      expect(app.game.day!.done, isEmpty);
      await shot('19_new_day');

      // Parent mode.
      ParentPass.grant();
      app.go('/parent');
      await app.settle(800);
      await shot('20_parent');
      await tester.tap(find.byKey(const ValueKey('level-big')));
      await app.settle();
      expect(app.game.settings.level, Level.big);
      await tester.tap(find.byKey(const ValueKey('routine-school')));
      await app.settle();
      expect(app.game.settings.off, contains(Task.school));
      app.go('/');
      await app.settle(600);

      // The play time runs out.
      app.now = app.now.add(const Duration(minutes: 16));
      await app.settle(2600);
      expect(app.location, '/rest');
      await shot('21_rest');
      await app.end();
    }, timeout: const Timeout(Duration(minutes: 12)));
  }
}

