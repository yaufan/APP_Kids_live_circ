import 'dart:math' as math;

import 'content.dart';
import 'day.dart';

/// Which things just happen today, and after which task each one comes
/// (docs/design.md 「偶爾會發生的事」: two to four a day, fitting the weather
/// and the time of day).
Map<int, Happening> scheduleHappenings(DayPlan plan, Weather weather, math.Random rnd, {Level level = Level.small}) {
  if (plan.length < 3) return const {};
  final count = plan.length <= 6 ? 2 : 2 + rnd.nextInt(3);
  final schedule = <int, Happening>{};
  // After which tasks something may happen: not after the last (sleep ends
  // the day) and not after going to school (the child is away).
  final slots = [for (var i = 0; i < plan.length - 1; i++) if (plan[i] != Task.schoolGo) i]..shuffle(rnd);
  final pool = _pool(plan, weather, rnd);
  for (final i in slots) {
    if (schedule.length >= count || pool.isEmpty) break;
    final task = plan[i];
    final h = _pick(pool, task, rnd);
    if (h == null) continue;
    schedule[i] = h;
    pool.removeWhere((x) => x == h);
  }
  return schedule;
}

/// The happenings that fit today, likeliest first.
List<Happening> _pool(DayPlan plan, Weather weather, math.Random rnd) {
  final pool = <Happening>[
    Happening.pee, Happening.pee, // the likeliest
    Happening.hungry, Happening.thirsty, Happening.sleepy,
    Happening.doorbell, Happening.phone, Happening.share, Happening.angry, Happening.spill,
    Happening.buddyHungry, Happening.plant, Happening.mosquito, Happening.fall, Happening.sneeze,
    if (weather == Weather.hot) Happening.sweaty,
    if (weather == Weather.cold) Happening.cold,
    if (weather == Weather.rain || weather == Weather.storm) ...[Happening.rainLaundry, Happening.thunder],
    if (weather == Weather.storm) Happening.blackout,
    Happening.garbage,
    Happening.earthquake,
    if (plan.tasks.contains(Task.school)) Happening.classmate,
  ];
  pool.shuffle(rnd);
  return pool;
}

/// A happening that makes sense after [task] (the garbage truck comes in
/// the evening, a classmate cries at school, you are not sleepy at bedtime).
Happening? _pick(List<Happening> pool, Task task, math.Random rnd) {
  bool fits(Happening h) {
    if (h == Happening.classmate) return task == Task.school;
    if (task == Task.school) return false;
    return switch (h) {
      Happening.garbage => task == Task.dinner || task == Task.chore || task == Task.tidy,
      Happening.sleepy => task == Task.home || task == Task.park || task == Task.cook,
      Happening.hungry => task != Task.breakfast && task != Task.dinner && task != Task.cook && task != Task.home,
      Happening.earthquake || Happening.blackout => task != Task.park && task != Task.market,
      _ => true,
    };
  }
  for (final h in pool) {
    if (fits(h)) return h;
  }
  return null;
}
