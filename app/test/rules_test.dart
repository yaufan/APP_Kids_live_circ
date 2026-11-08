import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:little_life/core/content.dart';
import 'package:little_life/core/day.dart';
import 'package:little_life/core/events.dart';
import 'package:little_life/core/game.dart';
import 'package:little_life/core/steps.dart';

/// The rules of the day (docs/design.md): the plan, the clock, what happens,
/// the little games and what is kept.
void main() {
  group('the plan for a day', () {
    test('a weekday has the fifteen things in order, a weekend its own day', () {
      final weekday = DayPlan.make(3);
      expect(weekday.tasks, Task.weekday);
      expect(weekday.tasks.first, Task.wake);
      expect(weekday.tasks.last, Task.sleep);
      expect(weekday.weekend, isFalse);
      final sunday = DayPlan.make(7);
      expect(sunday.tasks, Task.weekend);
      expect(sunday.weekend, isTrue);
      expect(sunday.tasks, contains(Task.market));
      expect(sunday.tasks, isNot(contains(Task.school)));
    });

    test('a parent can turn things off, and the free version keeps the four free ones', () {
      final noSchool = DayPlan.make(1, off: {Task.schoolGo, Task.school});
      expect(noSchool.tasks, isNot(contains(Task.school)));
      expect(noSchool.length, Task.weekday.length - 2);
      final free = DayPlan.make(1, full: false);
      expect(free.tasks, [Task.wake, Task.teeth, Task.breakfast, Task.dinner, Task.teethNight, Task.sleep]);
      for (final t in Task.optional) {
        expect(t.free, isFalse, reason: '${t.name} can be turned off, so it is not one of the free ones');
      }
      expect(Task.optional, isNot(contains(Task.wake)));
      expect(Task.optional, isNot(contains(Task.sleep)));
    });

    test('the clock ring: tasks in a row with the same picture share it, the hand goes round in order', () {
      final plan = DayPlan.make(1);
      expect(plan.groups.length, 12, reason: 'about a real clock face');
      final tidy = plan.indexOf(Task.tidy), chore = plan.indexOf(Task.chore);
      expect(plan.groupOf(tidy), plan.groupOf(chore), reason: 'both show the chore picture');
      expect(plan.groupOf(plan.indexOf(Task.teeth)), isNot(plan.groupOf(plan.indexOf(Task.dress))));
      var last = -1.0;
      for (var i = 0; i < plan.length; i++) {
        final t = plan.handTurn(i);
        expect(t, greaterThan(last), reason: 'task $i');
        expect(t, inInclusiveRange(0, 1));
        last = t;
        expect(plan.groups[plan.groupOf(i)].has(plan.taskAtTurn(t)), isTrue, reason: 'turning the hand to where it points lands on the same picture');
      }
      expect(plan.taskAtTurn(1.0), 0, reason: 'a full turn is the top again');
    });
  });

  group('what happens in a day', () {
    test('two to four things, never after going to school or at bedtime, each fitting its moment', () {
      for (var seed = 0; seed < 300; seed++) {
        final rnd = math.Random(seed);
        final weekday = 1 + rnd.nextInt(7);
        final weather = Weather.values[rnd.nextInt(Weather.values.length)];
        final plan = DayPlan.make(weekday);
        final sched = scheduleHappenings(plan, weather, rnd);
        expect(sched.length, inInclusiveRange(2, 4), reason: 'seed $seed');
        expect(sched.values.toSet().length, sched.length, reason: 'no happening twice in a day');
        for (final MapEntry(key: i, value: h) in sched.entries) {
          expect(i, lessThan(plan.length - 1), reason: 'nothing after bedtime');
          expect(plan[i], isNot(Task.schoolGo), reason: 'the child is away');
          if (h == Happening.classmate) expect(plan[i], Task.school);
          if (plan[i] == Task.school) expect(h, Happening.classmate, reason: 'at school only school things');
          if (h == Happening.garbage) expect([Task.dinner, Task.chore, Task.tidy], contains(plan[i]));
          if (h == Happening.sweaty) expect(weather, Weather.hot);
          if (h == Happening.cold) expect(weather, Weather.cold);
          if (h == Happening.rainLaundry || h == Happening.thunder) expect([Weather.rain, Weather.storm], contains(weather));
          if (h == Happening.blackout) expect(weather, Weather.storm);
        }
      }
    });

    test('over many days every happening comes up and the weather is mostly fine', () {
      final seen = <Happening>{};
      final weathers = <Weather, int>{};
      final rnd = math.Random(7);
      for (var d = 0; d < 400; d++) {
        final w = weatherFor(rnd);
        weathers[w] = (weathers[w] ?? 0) + 1;
        seen.addAll(scheduleHappenings(DayPlan.make(1 + d % 7), w, rnd).values);
      }
      expect(seen, containsAll(Happening.values));
      expect(weathers[Weather.sun]!, greaterThan(weathers[Weather.storm]! * 3));
      expect(weatherFor(math.Random(1), yesterday: Weather.storm), isNot(Weather.storm), reason: 'never two typhoon days running');
    });

    test('the chores take turns and the toys are their own task', () {
      var c = nextChore(null);
      final seen = <Chore>{};
      for (var i = 0; i < 7; i++) {
        seen.add(c);
        c = nextChore(c);
      }
      expect(seen.length, 7);
      expect(seen, isNot(contains(Chore.toys)));
    });
  });

  group('the little games', () {
    test('every task, chore and happening has steps that make sense at both ages', () {
      final rnd = math.Random(3);
      void check(String what, List<Step> steps) {
        expect(steps, isNotEmpty, reason: what);
        for (final s in steps) {
          expect(s.say, isNotEmpty, reason: what);
          switch (s) {
            case TapStep(:final props):
              expect(props, isNotEmpty, reason: what);
            case DragStep(:final items, :final slots):
              expect(slots, isNotEmpty, reason: what);
              final room = <String, int>{for (final sl in slots) sl.id: sl.capacity};
              for (final i in items) {
                final fits = slots.where((sl) => sl.takes(i)).toList();
                if (i.slot != null) {
                  expect(fits.map((sl) => sl.id), contains(i.slot), reason: '$what: ${i.prop} wants ${i.slot}');
                  room[i.slot!] = room[i.slot!]! - 1;
                } else if (fits.isNotEmpty) {
                  final free = fits.where((sl) => room[sl.id]! > 0).toList();
                  expect(free, isNotEmpty, reason: '$what: a free slot for ${i.prop}');
                  room[free.first.id] = room[free.first.id]! - 1;
                }
              }
              expect(room.values.every((n) => n >= 0), isTrue, reason: '$what: every item fits somewhere');
              expect(items.length, lessThanOrEqualTo(6), reason: '$what: not too many for small hands');
            case ChooseStep(:final options, :final good):
              expect(options.length, inInclusiveRange(2, 3), reason: what);
              expect(options.map((o) => o.prop).toSet(), containsAll(good), reason: what);
            case HoldStep(:final seconds, :final tooLong):
              expect(seconds, inInclusiveRange(1, 4), reason: what);
              if (tooLong != null) expect(tooLong, greaterThan(seconds));
            case ScrubStep(:final strokes):
              expect(strokes, inInclusiveRange(3, 14), reason: what);
          }
        }
      }

      for (final l in Level.values) {
        for (final t in Task.values) {
          for (final w in Weather.values) {
            check('${t.name} $l $w', planTask(t, level: l, weather: w, chore: Chore.wipe, rnd: rnd));
          }
        }
        for (final c in Chore.values) {
          check('${c.name} $l', planChore(c, level: l));
        }
        for (final h in Happening.values) {
          check('${h.name} $l', planHappening(h, level: l, rnd: rnd));
        }
      }
    });

    test('大 gets more steps than 小小, and the clothes follow the weather', () {
      final rnd = math.Random(1);
      int steps(Level l, Task t) => planTask(t, level: l, weather: Weather.sun, chore: Chore.wipe, rnd: rnd).length;
      expect(steps(Level.big, Task.wake), greaterThan(steps(Level.small, Task.wake)));
      expect(steps(Level.big, Task.breakfast), greaterThan(steps(Level.small, Task.breakfast)));
      expect(steps(Level.big, Task.dress), greaterThan(steps(Level.small, Task.dress)));
      final rainy = planTask(Task.dress, level: Level.small, weather: Weather.rain, chore: Chore.wipe, rnd: rnd).first as ChooseStep;
      expect(rainy.good, {'cloth_raincoat'});
      final coldDay = planTask(Task.dress, level: Level.small, weather: Weather.cold, chore: Chore.wipe, rnd: rnd).first as ChooseStep;
      expect(coldDay.good, {'cloth_jacket'});
      final out = planTask(Task.schoolGo, level: Level.small, weather: Weather.rain, chore: Chore.wipe, rnd: rnd).whereType<ChooseStep>().first;
      expect(out.good, {'umbrella'});
    });

    test('the shopping list is three things that are all on the shelf', () {
      for (var seed = 0; seed < 20; seed++) {
        final steps = planTask(Task.market, level: Level.small, weather: Weather.sun, chore: Chore.wipe, rnd: math.Random(seed));
        final shelf = steps.whereType<DragStep>().first;
        final wanted = shelf.slots.single.accepts!;
        expect(wanted.length, 3);
        expect(shelf.items.map((i) => i.prop).toSet(), containsAll(wanted));
        expect(shelf.items.length, 4, reason: '小小: one extra on the shelf');
      }
    });

    test('the props the steps ask for are a known, finite set', () {
      final props = allStepProps();
      expect(props.length, greaterThan(80));
      expect(props, containsAll(['toothbrush', 'mouth_big', 'plate', 'bin_trash', 'garbage_truck', 'table_hide']));
      expect(props.any((p) => p.startsWith('@')), isFalse);
    });
  });

  group('what is kept', () {
    final settings = const Settings(level: Level.big);

    Game fresh([int seed = 1]) => const Game(profile: Profile(name: '小明'), settings: Settings(level: Level.big)).beginDay(math.Random(seed));

    test('finishing a task gives a sticker and moves the hand to the next thing not done', () {
      var g = fresh();
      final plan = g.day!.plan(settings);
      expect(g.day!.index, 0);
      g = g.finish(plan[0]);
      expect(g.stickers[plan[0]], 1);
      expect(g.day!.index, 1);
      g = g.finish(plan[2]);
      expect(g.day!.index, 1, reason: 'the hand stays on the thing skipped over');
      g = g.finish(plan[1]);
      expect(g.day!.index, 3, reason: 'past the two already done');
      expect(g.stickerCount, 3);
    });

    test('the hand moving on by itself skips the task; turning the clock back un-skips it when done', () {
      var g = fresh();
      final plan = g.day!.plan(settings);
      g = g.skipCurrent();
      expect(g.day!.index, 1);
      expect(g.day!.skipped, {plan[0]});
      g = g.turnClock(0);
      expect(g.day!.index, 0);
      g = g.finish(plan[0]);
      expect(g.day!.skipped, isEmpty);
      g = g.turnClock(99);
      expect(g.day!.index, plan.length - 1);
      final atEnd = g.skipCurrent();
      expect(atEnd.day!.index, plan.length - 1, reason: 'bedtime is never skipped');
    });

    test('things happen after the task they are scheduled for, one at a time', () {
      for (var seed = 0; seed < 30; seed++) {
        var g = fresh(seed);
        final plan = g.day!.plan(settings);
        final sched = g.day!.happenings;
        expect(sched, isNotEmpty);
        final first = sched.keys.reduce(math.min);
        for (var i = 0; i <= first; i++) {
          expect(g.day!.active, isNull, reason: 'seed $seed task $i');
          g = g.finish(plan[i]);
        }
        expect(g.day!.active, sched[first]);
        final later = sched.keys.where((k) => k > first);
        if (later.isNotEmpty) {
          for (var i = first + 1; i <= later.first; i++) {
            g = g.finish(plan[i]);
          }
          expect(g.day!.active, sched[first], reason: 'the second waits while the first is not dealt with');
          g = g.dealtWith(sched[first]!);
          expect(g.day!.active, isNull);
          expect(g.day!.happened, {sched[first]});
        }
      }
    });

    test('a day with everything done earns a decoration; a week earns a height mark; the next day follows', () {
      var g = fresh();
      final plan = g.day!.plan(settings);
      for (final t in plan.tasks) {
        g = g.finish(t);
      }
      expect(g.dayOver, isTrue);
      g = g.endDay();
      expect(g.decos, 1);
      expect(g.daysDone, 1);
      expect(g.height, 0);
      expect(g.history.single.done, plan.tasks);
      expect(g.decosIn(Scene.living), 1);
      expect(g.decosIn(Scene.bedroom), 0);
      final monday = g.day!.weekday;
      g = g.beginDay(math.Random(2));
      expect(g.day!.weekday, Week.next(monday));
      expect(g.day!.index, 0);
      expect(g.day!.done, isEmpty);
      expect(g.dayOver, isFalse);
      // A day with something skipped earns no decoration.
      final plan2 = g.day!.plan(settings);
      for (final t in plan2.tasks.skip(1)) {
        g = g.finish(t);
      }
      g = g.endDay();
      expect(g.decos, 1);
      expect(g.history.length, 2);
      expect(g.history.last.skipped, [plan2.tasks.first]);
      for (var d = 2; d < 7; d++) {
        g = g.beginDay(math.Random(d)).endDay();
      }
      expect(g.daysDone, 7);
      expect(g.height, 1);
      expect(g.history.length, Game.historyKept);
    });

    test('a rest lasts an hour unless a parent lets play go on', () {
      final now = DateTime(2026, 11, 8, 10);
      final g = const Game().rest(now);
      expect(g.resting(now.add(const Duration(minutes: 59))), isTrue);
      expect(g.resting(now.add(const Duration(minutes: 61))), isFalse);
      expect(g.playOn().resting(now), isFalse);
    });

    test('what is kept comes back the same from the file, and a broken file is harmless', () {
      var g = fresh(5);
      final plan = g.day!.plan(settings);
      g = g.finish(plan[0]).finish(plan[1]).skipCurrent();
      g = g.copyWith(settings: g.settings.copyWith(off: {Task.bath, Task.wake}, minutes: 20, english: true), profile: const Profile(name: '阿寶', avatar: Avatar(hair: 3, skin: 2, shirt: 6), buddy: Buddy.duck), decos: 4, height: 1).rest(DateTime(2026, 11, 8, 10));
      final back = Game.fromJson(g.toJson());
      expect(Game.fromJson(back.toJson()).toJson(), back.toJson(), reason: 'stable once read back');
      expect(back.stickers, g.stickers);
      expect(back.day!.index, g.day!.index);
      expect(back.profile!.name, '阿寶');
      expect(back.profile!.avatar, const Avatar(hair: 3, skin: 2, shirt: 6));
      expect(back.profile!.buddy, Buddy.duck);
      expect(back.settings.off, {Task.bath}, reason: 'waking up cannot be turned off');
      expect(back.day!.done, g.day!.done);
      expect(back.day!.happenings, g.day!.happenings);
      expect(back.decos, 4);
      final broken = Game.fromJson({'profile': {'name': '   ', 'avatar': {'hair': 9}}, 'settings': {'minutes': 7, 'level': 'huge'}, 'day': {'weekday': 12, 'index': -3}, 'decos': 999, 'history': ['x', 3]});
      expect(broken.profile!.name, Profile.defaultName);
      expect(broken.profile!.avatar.hair, 1);
      expect(broken.settings.minutes, 15);
      expect(broken.settings.level, Level.small);
      expect(broken.day!.weekday, 1);
      expect(broken.day!.index, 0);
      expect(broken.decos, Game.maxDecos);
      expect(broken.history, isEmpty);
      expect(Game.fromJson(null).profile, isNull);
    });
  });
}
