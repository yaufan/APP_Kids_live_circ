import 'dart:async';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart' hide Step;
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_life/app/app.dart';
import 'package:little_life/app/strings.dart';
import 'package:little_life/core/content.dart';
import 'package:little_life/core/game.dart';
import 'package:little_life/core/sounds.dart';
import 'package:little_life/core/voice.dart';
import 'package:little_life/features/parent/parent_gate.dart';
import 'package:little_life/features/play/play_screen.dart';
import 'package:little_life/features/play/step_views.dart';
import 'package:little_life/features/room/scene_view.dart';

import 'helpers.dart';

/// The screens as a child (and a parent) uses them: the chores, what is
/// said when, the app out of sight, the play time, the back key, the
/// parent pages, fingers.
void main() {
  const name = '小明';

  /// A day under way on [weekday] with nothing happening, the hand on [task].
  Game dayOn(int weekday, {Task task = Task.wake, Chore chore = Chore.table, Level level = Level.small, int minutes = 15, Weather weather = Weather.sun}) {
    final settings = Settings(level: level, minutes: minutes);
    final day = Day(weekday: weekday, weather: weather, chore: chore, seed: 7);
    return Game(profile: const Profile(name: name), settings: settings, day: day.copyWith(index: day.plan(settings).indexOf(task)));
  }

  group('幫忙做家事', () {
    for (final (i, chore) in [for (final c in Chore.values) if (c != Chore.toys) c].indexed) {
      final weekday = 1 + i % 5;
      testWidgets('${chore.zh} (${Week.zh[weekday]}): the room lights up, its thing glows, and it can be done', (tester) async {
        final app = await TestApp.start(tester, game: dayOn(weekday, task: Task.chore, chore: chore));
        expect(app.game.day!.current(app.game.settings), Task.chore);
        expect(app.game.day!.sceneOf(Task.chore), chore.scene);
        final bubble = '${Strings.nowDo(name, Task.chore)}${chore.scene == Scene.living ? Strings.here(Task.chore) : Strings.goTo(chore.scene)}';
        expect(find.text(bubble), findsOneWidget, reason: 'says where today\'s chore is');
        if (chore.scene != Scene.living) await app.tapLabel(chore.scene.zh, ms: 900);
        expect(find.byKey(ValueKey('scene-${chore.scene.name}')), findsOneWidget);
        expect(tester.widget<SceneView>(find.byType(SceneView)).glow, chore.target, reason: 'the thing to tap glows');
        await tester.tap(find.byKey(ValueKey('thing-${chore.target}')));
        await app.settle(700);
        expect(app.location, '/play/task/chore');
        await playThrough(app);
        expect(app.game.day!.done, contains(Task.chore));
        expect(app.location, '/');
        await app.end();
      });
    }

    testWidgets('小小: tapping the puppet walks to today\'s chore', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(3, task: Task.chore, chore: Chore.laundry));
      await tester.tap(find.byKey(const ValueKey('avatar')));
      await app.settle(900);
      expect(find.byKey(const ValueKey('scene-balcony')), findsOneWidget);
      await app.end();
    });
  });

  group('what is said, and when', () {
    testWidgets('back from a little game, the next thing is said straight away, after the praise', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      await app.tapLabel('房間', ms: 900);
      await tester.tap(find.byKey(const ValueKey('thing-bed')));
      await app.settle(700);
      app.voice.said.clear();
      await playThrough(app);
      expect(app.location, '/');
      final praise = app.voice.said.indexWhere((l) => l.contains(Strings.taskDone(Task.wake)));
      final next = app.voice.said.indexWhere((l) => l.startsWith(Strings.nowDo(name, Task.teeth)));
      expect(praise, greaterThanOrEqualTo(0));
      expect(next, greaterThan(praise), reason: 'brushing teeth is said at once, after the praise');
      await app.end();
    });

    testWidgets('the little game waits for the praise to be said before going back', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      await app.tapLabel('房間', ms: 900);
      await tester.tap(find.byKey(const ValueKey('thing-bed')));
      await app.settle(700);
      final slow = Completer<void>();
      var guard = 0;
      while (find.byType(PlayScreen).evaluate().isNotEmpty && !app.voice.said.any((l) => l.contains(Strings.taskDone(Task.wake))) && guard++ < 20) {
        // Lines are slow from the last step on.
        if (find.byType(TapView).evaluate().isNotEmpty && app.voice.hold == null) app.voice.hold = slow.future;
        await playThroughOnce(app);
        await app.settle(400);
      }
      expect(app.voice.said.last, contains(Strings.taskDone(Task.wake)));
      await app.settle(3000);
      expect(find.byType(PlayScreen), findsOneWidget, reason: 'the praise is still being said');
      slow.complete();
      app.voice.hold = null;
      await app.settle(1200);
      expect(app.location, '/');
      expect(find.byType(PlayScreen), findsNothing);
      await app.end();
    });

    testWidgets('something happening after a task is said (and sounded) at once', (tester) async {
      final start = dayOn(1);
      final app = await TestApp.start(tester, game: start.copyWith(day: Day(weekday: 1, weather: Weather.sun, chore: Chore.table, seed: 7, happenings: const {0: Happening.pee})));
      await app.tapLabel('房間', ms: 900);
      await tester.tap(find.byKey(const ValueKey('thing-bed')));
      await app.settle(700);
      app.voice.said.clear();
      app.sounds.played.clear();
      await playThrough(app);
      expect(app.game.day!.active, Happening.pee);
      expect(app.voice.said, contains(Strings.happening(name, Happening.pee)));
      expect(app.sounds.played, contains('drop'));
      await app.end();
    });

    testWidgets('when the hand moves on by itself, the next thing is said', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      app.voice.said.clear();
      await tester.pump(const Duration(seconds: 56));
      expect(app.game.day!.index, 1);
      expect(app.voice.said.last, startsWith(Strings.nowDo(name, Task.teeth)));
      await app.end();
    });

    testWidgets('out of sight the clock waits and nothing is said; back in sight it goes on', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      app.voice.said.clear();
      app.hide();
      for (var i = 0; i < 12; i++) {
        await tester.pump(const Duration(seconds: 10));
      }
      expect(app.game.day!.index, 0, reason: 'nothing skipped in the background');
      expect(app.game.day!.skipped, isEmpty);
      expect(app.voice.said, isEmpty, reason: 'no voice in the background');
      app.show();
      await tester.pump(const Duration(seconds: 56));
      expect(app.game.day!.index, 1);
      expect(app.voice.said, isNotEmpty);
      await app.end();
    });

    testWidgets('the phone voice: only the newest line asked for while it sets up, nothing after a stop', (tester) async {
      const channel = MethodChannel('flutter_tts');
      final calls = <String>[];
      final messenger = TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
      messenger.setMockMethodCallHandler(channel, (call) async {
        calls.add(call.method == 'speak' ? 'speak:${call.arguments}' : call.method);
        if (call.method == 'awaitSpeakCompletion') await Future<void>.delayed(const Duration(milliseconds: 80));
        return 1;
      });
      addTearDown(() => messenger.setMockMethodCallHandler(channel, null));
      await tester.runAsync(() async {
        final voice = SystemVoice();
        addTearDown(voice.dispose);
        final hello = voice.say('你好');
        await Future<void>.delayed(const Duration(milliseconds: 10));
        final next = voice.say('該起床囉');
        await Future.wait([hello, next]);
        expect([for (final c in calls) if (c.startsWith('speak:')) c], ['speak:該起床囉']);
        expect(calls.indexOf('setLanguage'), lessThan(calls.indexOf('speak:該起床囉')));
        calls.clear();
        final left = voice.say('刷牙');
        await voice.stop();
        await left;
        expect(calls.where((c) => c.startsWith('speak:')), isEmpty);
      });
    });
  });

  group('play time', () {
    Future<void> minutes(TestApp app, int m) async {
      for (var i = 0; i < m; i++) {
        app.now = app.now.add(const Duration(minutes: 1));
        await app.settle(2100);
      }
    }

    testWidgets('time in parent mode and at the gate is not play time', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      await minutes(app, 8);
      ParentPass.grant();
      app.go('/parent');
      await app.settle();
      await minutes(app, 4);
      app.go('/');
      await app.settle();
      await app.tapLabel(Strings.parent, ms: 800);
      expect(find.byType(ParentGatePage), findsOneWidget);
      await minutes(app, 4);
      await app.tapLabel(Strings.cancel, ms: 800);
      await minutes(app, 5);
      expect(app.location, '/', reason: '13 minutes played');
      await minutes(app, 3);
      expect(app.location, '/rest');
      await app.end();
    });

    testWidgets('out of sight is not play time, and no rest starts then; ten minutes away is a new sitting', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      await minutes(app, 10);
      app.hide();
      app.now = app.now.add(const Duration(minutes: 9));
      await app.settle(4000);
      expect(app.location, '/', reason: 'no rest while out of sight');
      app.show();
      await app.settle(2100);
      await minutes(app, 4);
      expect(app.location, '/', reason: '14 minutes played');
      app.hide();
      app.now = app.now.add(const Duration(minutes: 10));
      await app.settle(2100);
      app.show();
      await minutes(app, 14);
      expect(app.location, '/', reason: 'a new sitting');
      await minutes(app, 2);
      expect(app.location, '/rest');
      await app.end();
    });

    testWidgets('a phone clock moved back gives no extra time and does not end a rest early', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      await minutes(app, 10);
      app.now = app.now.subtract(const Duration(hours: 1));
      await app.settle(2100);
      await minutes(app, 6);
      expect(app.location, '/rest');
      app.now = app.now.subtract(const Duration(hours: 2));
      await app.settle(2100);
      expect(app.location, '/rest', reason: 'still resting');
      app.now = app.now.add(const Duration(minutes: 50));
      await app.settle(2100);
      expect(app.location, '/rest');
      app.now = app.now.add(const Duration(minutes: 11));
      await app.settle(4200);
      expect(app.location, '/', reason: 'an hour later');
      await app.end();
    });

    testWidgets('closed and opened again within ten minutes, the sitting goes on; later it starts afresh', (tester) async {
      var app = await TestApp.start(tester, game: dayOn(1));
      await minutes(app, 10);
      app.hide();
      final saved = Game.fromJson(app.store.saved);
      expect(saved.sitting!.played, closeTo(600, 5));
      final seen = app.now;
      await app.end();
      app.show();

      app = await TestApp.start(tester, game: saved, now: seen.add(const Duration(minutes: 3)));
      await app.settle(2100);
      await minutes(app, 4);
      expect(app.location, '/');
      await minutes(app, 2);
      expect(app.location, '/rest', reason: 'the same sitting went on');
      await app.end();

      app = await TestApp.start(tester, game: saved, now: seen.add(const Duration(minutes: 12)));
      await app.settle(2100);
      await minutes(app, 14);
      expect(app.location, '/', reason: 'closed long enough: a new sitting');
      await app.end();
    });

    testWidgets('a rest is kept when the app is closed, and a rest in the future starts now', (tester) async {
      var app = await TestApp.start(tester, game: dayOn(1).rest(DateTime(2026, 11, 6, 9, 40)));
      expect(app.location, '/rest');
      await app.end();
      app = await TestApp.start(tester, game: dayOn(1).rest(DateTime(2026, 11, 7, 10)));
      expect(app.location, '/rest', reason: 'the clock was moved back');
      await app.settle(2100);
      expect(app.game.restSince, app.now, reason: 'at most an hour from now');
      await app.end();
    });

    testWidgets('a little game being played is finished first, at most two minutes more', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      await minutes(app, 14);
      await app.tapLabel('房間', ms: 900);
      await tester.tap(find.byKey(const ValueKey('thing-bed')));
      await app.settle(700);
      await minutes(app, 1);
      expect(app.location, '/play/task/wake', reason: 'the game goes on');
      await playThrough(app);
      await app.settle(2100);
      expect(app.location, '/rest');
      expect(app.game.day!.done, contains(Task.wake), reason: 'it was finished');
      await app.end();
    });

    testWidgets('... but not for ever', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      await minutes(app, 14);
      await app.tapLabel('房間', ms: 900);
      await tester.tap(find.byKey(const ValueKey('thing-bed')));
      await app.settle(700);
      await minutes(app, 3);
      expect(app.location, '/rest');
      await app.end();
    });
  });

  group('the back key never closes the app', () {
    testWidgets('the room stays; a little game, the stickers and parent mode go back to the room', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      expect(await app.back(), isFalse);
      expect(app.location, '/');
      await app.tapLabel('房間', ms: 900);
      await tester.tap(find.byKey(const ValueKey('thing-bed')));
      await app.settle(700);
      expect(await app.back(), isFalse);
      expect(app.location, '/');
      expect(find.byType(PlayScreen), findsNothing);
      await app.tapLabel(Strings.stickers, ms: 800);
      expect(await app.back(), isFalse);
      expect(app.location, '/');
      await app.tapLabel(Strings.parent, ms: 800);
      expect(await app.back(), isFalse, reason: 'the gate');
      expect(find.byType(ParentGatePage), findsNothing);
      ParentPass.grant();
      app.container.read(routerProvider).push('/parent');
      await app.settle();
      expect(app.location, '/parent');
      expect(await app.back(), isFalse);
      expect(app.location, '/');
      await app.end();
    });

    testWidgets('the night, the rest and the first setup stay', (tester) async {
      var app = await TestApp.start(tester, game: dayOn(1));
      app.go('/night');
      await app.settle(900);
      expect(await app.back(), isFalse);
      expect(app.location, '/night');
      app.change((g) => g.rest(app.now));
      await app.settle(2100);
      expect(app.location, '/rest');
      expect(await app.back(), isFalse);
      expect(app.location, '/rest');
      await app.end();
      app = await TestApp.start(tester);
      expect(await app.back(), isFalse);
      expect(app.location, '/setup');
      await app.end();
    });
  });

  group('the parent pages', () {
    testWidgets('out of sight, the gate and parent mode close and the pass is used up', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      await app.tapLabel(Strings.parent, ms: 800);
      expect(find.byType(ParentGatePage), findsOneWidget);
      app.hide();
      await app.settle();
      app.show();
      await app.settle(1500);
      expect(find.byType(ParentGatePage), findsNothing);
      ParentPass.grant();
      app.go('/parent');
      await app.settle();
      app.hide();
      await app.settle();
      app.show();
      await app.settle();
      expect(app.location, '/');
      app.go('/parent');
      await app.settle();
      expect(app.location, '/', reason: 'the gate has to be answered again');
      await app.end();
    });

    testWidgets('they close after five minutes without a touch', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      ParentPass.grant();
      app.go('/parent');
      await app.settle();
      await tester.pump(const Duration(minutes: 4));
      await tester.tap(find.byKey(const ValueKey('level-big')));
      await tester.pump(const Duration(minutes: 4));
      expect(app.location, '/parent', reason: 'touched a minute ago... four, not five');
      await tester.pump(const Duration(minutes: 1, seconds: 5));
      await app.settle();
      expect(app.location, '/');
      await app.tapLabel(Strings.parent, ms: 800);
      await tester.pump(const Duration(minutes: 5, seconds: 5));
      await app.settle(1500);
      expect(find.byType(ParentGatePage), findsNothing);
      await app.end();
    });

    testWidgets('the gate\'s lock grows (1, 5, 15 minutes), is kept when the app is closed, and a right answer resets it', (tester) async {
      const digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
      int answer() {
        final q = RegExp(r'(\S) 加 (\S) 等於').firstMatch(tester.widgetList<Text>(find.textContaining('等於多少')).first.data!)!;
        return digits.indexOf(q.group(1)!) + digits.indexOf(q.group(2)!);
      }

      Future<void> wrongThree(TestApp app) async {
        for (var i = 0; i < 3; i++) {
          // Zeros are never the answer (it is 6 to 18): one per digit asked for.
          for (var d = '${answer()}'.length; d > 0; d--) {
            await tester.tap(find.byKey(const ValueKey('gate-key-0')).last);
            await tester.pump();
          }
          await app.settle(200);
        }
      }

      var app = await TestApp.start(tester, game: dayOn(1));
      await app.tapLabel(Strings.parent, ms: 800);
      await wrongThree(app);
      expect(app.game.gate.lockedNow(app.now), isTrue);
      expect(app.game.gate.leftAt(app.now), const Duration(minutes: 1));
      final saved = Game.fromJson(app.store.saved);
      await app.end();

      app = await TestApp.start(tester, game: saved);
      await app.tapLabel(Strings.parent, ms: 800);
      expect(find.textContaining('秒再試'), findsOneWidget, reason: 'still locked after closing the app');
      app.now = app.now.add(const Duration(minutes: 1, seconds: 1));
      await app.settle(1200);
      await wrongThree(app);
      expect(app.game.gate.leftAt(app.now), const Duration(minutes: 5));
      expect(find.textContaining('5 分鐘'), findsOneWidget);
      app.now = app.now.add(const Duration(minutes: 5, seconds: 1));
      await app.settle(1200);
      await wrongThree(app);
      expect(app.game.gate.leftAt(app.now), const Duration(minutes: 15));
      // A clock moved back does not make it last for ever.
      app.now = app.now.subtract(const Duration(days: 30));
      await app.settle(1200);
      expect(app.game.gate.leftAt(app.now), lessThanOrEqualTo(const Duration(minutes: 15)));
      app.now = app.now.add(const Duration(minutes: 15, seconds: 2));
      await app.settle(1200);
      expect(app.game.gate.lockedNow(app.now), isFalse);
      app.change((g) => g.copyWith(gate: g.gate.miss(app.now)));
      for (final d in '${answer()}'.split('')) {
        await tester.tap(find.byKey(ValueKey('gate-key-$d')).last);
        await tester.pump();
      }
      await app.settle(800);
      expect(app.game.gate.misses, 0);
      expect(app.game.gate.lockouts, 0, reason: 'a right answer starts it all again');
      await app.end();
    });
  });

  group('fingers', () {
    testWidgets('按住: a second finger neither restarts the hold nor doubles its sound', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      app.go('/play/happening/sleepy');
      await app.settle(700);
      await tester.tap(find.byKey(const ValueKey('tap-0')).last);
      await app.settle(900);
      expect(find.byType(HoldView), findsOneWidget);
      app.sounds.played.clear();
      final centre = tester.getCenter(find.byKey(const ValueKey('hold')).last);
      final one = await tester.startGesture(centre);
      await tester.pump(const Duration(milliseconds: 50));
      await tester.pump(const Duration(milliseconds: 1000));
      final two = await tester.startGesture(centre + const Offset(30, 0), pointer: 7);
      await tester.pump(const Duration(milliseconds: 600));
      await two.up();
      await tester.pump(const Duration(milliseconds: 600));
      await tester.pump(const Duration(milliseconds: 50));
      await one.up();
      await app.settle(600);
      final snores = app.sounds.played.where((s) => s == 'snore').length;
      expect(snores, lessThanOrEqualTo(3));
      await tester.pump(const Duration(seconds: 4));
      expect(app.sounds.played.where((s) => s == 'snore').length, snores, reason: 'the sound stops with the hold');
      await app.end();
    });

    testWidgets('拖: a second finger does not take or drop what the first one holds', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      app.go('/play/happening/cold');
      await app.settle(700);
      expect(find.byType(DragView), findsOneWidget);
      final one = await tester.startGesture(tester.getCenter(find.byKey(const ValueKey('item-0')).last));
      await tester.pump(const Duration(milliseconds: 30));
      final two = await tester.startGesture(const Offset(30, 300), pointer: 9);
      await tester.pump(const Duration(milliseconds: 30));
      await two.up();
      await tester.pump(const Duration(milliseconds: 30));
      await one.moveTo(tester.getCenter(find.byKey(const ValueKey('slot-body')).last));
      await tester.pump(const Duration(milliseconds: 30));
      await one.up();
      await app.settle(2500);
      expect(app.game.day!.happened, contains(Happening.cold), reason: 'the jacket went on');
      await app.end();
    });
  });

  group('small things', () {
    testWidgets('a double tap on the night brings one morning, not two', (tester) async {
      final app = await TestApp.start(tester, game: dayOn(1));
      app.go('/night');
      await app.settle(900);
      // Two taps before the page has gone.
      await tester.tap(find.byKey(const ValueKey('night')));
      await tester.tap(find.byKey(const ValueKey('night')));
      await app.settle(900);
      expect(app.game.day!.weekday, 2);
      await app.end();
    });

    test('the clock\'s note says the right thing about school', () {
      expect(Strings.weekendNote(4), '明天要上學。');
      expect(Strings.weekendNote(5), '明天不用上學！');
      expect(Strings.weekendNote(6), '今天不用上學！');
      expect(Strings.weekendNote(7), contains('明天要上學'));
      expect(Strings.weekendNote(2, Weather.storm), Strings.storm);
    });

    test('the sounds play on the media stream, take no audio focus, and mix on iOS', () {
      final c = SystemSounds.audioContext;
      expect(c.android.usageType, AndroidUsageType.game, reason: 'not the ringtone stream');
      expect(c.android.audioFocus, AndroidAudioFocus.none);
      expect(c.iOS.category, AVAudioSessionCategory.ambient);
    });
  });
}
