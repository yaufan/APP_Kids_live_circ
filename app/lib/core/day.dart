import 'dart:math' as math;

import 'content.dart';

/// Today's plan: the things to do, in order, after the parent's switches,
/// and where each sits on the clock (docs/design.md 「時鐘」).
///
/// The clock is not a real clock: its ring is the day in order. Tasks in a
/// row that share a picture (刷牙 then 穿衣服 are different; 收玩具 then 做家事
/// both show the chore picture) share one position on the ring, so a
/// weekday has about twelve pictures like a real clock face.
class DayPlan {
  DayPlan._(this.weekday, this.tasks);

  /// The plan for [weekday] (1 Monday … 7 Sunday) with the tasks a parent
  /// turned [off] left out; without the [full] version only the free ones.
  factory DayPlan.make(int weekday, {Set<Task> off = const {}, bool full = true}) {
    final base = Week.weekend(weekday) ? Task.weekend : Task.weekday;
    final tasks = [for (final t in base) if (!off.contains(t) && (full || t.free)) t];
    return DayPlan._(weekday, tasks);
  }

  final int weekday;
  final List<Task> tasks;

  bool get weekend => Week.weekend(weekday);

  int get length => tasks.length;

  Task operator [](int i) => tasks[i];

  int indexOf(Task t) => tasks.indexOf(t);

  /// The ring's pictures: one per run of tasks with the same picture.
  late final List<ClockGroup> groups = _groups();

  List<ClockGroup> _groups() {
    final out = <ClockGroup>[];
    for (var i = 0; i < tasks.length; i++) {
      if (out.isNotEmpty && out.last.icon == tasks[i].icon && out.last.last == i - 1) {
        out[out.length - 1] = ClockGroup(out.last.icon, out.last.first, i);
      } else {
        out.add(ClockGroup(tasks[i].icon, i, i));
      }
    }
    return out;
  }

  /// Which picture [taskIndex] belongs to.
  int groupOf(int taskIndex) => groups.indexWhere((g) => g.has(taskIndex));

  /// Where a picture sits: turns from the top, clockwise, 0～1.
  double groupTurn(int group) => (group + 0.5) / groups.length;

  /// Where the hand points for [taskIndex]: at its picture, a little before
  /// or after it when the picture stands for more than one task.
  double handTurn(int taskIndex) {
    if (tasks.isEmpty) return 0;
    final gi = groupOf(taskIndex);
    final g = groups[gi];
    final within = g.count == 1 ? 0.0 : ((taskIndex - g.first) / (g.count - 1) - 0.5) * 0.5;
    return groupTurn(gi) + within / groups.length;
  }

  /// The task a turn of the hand lands on (the nearest picture's first task).
  int taskAtTurn(double turn) {
    if (tasks.isEmpty) return 0;
    final t = turn - turn.floorToDouble();
    final gi = (t * groups.length).floor().clamp(0, groups.length - 1);
    return groups[gi].first;
  }

  /// Degrees clockwise from the top for a turn.
  static double degrees(double turn) => turn * 360;

  /// Radians for painting (0 is to the right, as in dart:math).
  static double radians(double turn) => (turn - 0.25) * 2 * math.pi;
}

class ClockGroup {
  const ClockGroup(this.icon, this.first, this.last);

  final ClockIcon icon;
  final int first;
  final int last;

  int get count => last - first + 1;

  bool has(int i) => i >= first && i <= last;
}

/// The weather for a day: mostly sunny, sometimes the others, a typhoon day
/// rarely (and never two days running).
Weather weatherFor(math.Random rnd, {Weather? yesterday}) {
  final r = rnd.nextDouble();
  final w = r < 0.45
      ? Weather.sun
      : r < 0.65
          ? Weather.rain
          : r < 0.8
              ? Weather.cold
              : r < 0.93
                  ? Weather.hot
                  : Weather.storm;
  return w == Weather.storm && yesterday == Weather.storm ? Weather.sun : w;
}

/// The chore after [previous] (the toys are their own task, so they are
/// skipped here).
Chore nextChore(Chore? previous) {
  final list = [for (final c in Chore.values) if (c != Chore.toys) c];
  if (previous == null) return list.first;
  return list[(list.indexOf(previous) + 1) % list.length];
}

/// How long the hand waits on a task before moving on by itself: a day of
/// about fifteen tasks takes about ten minutes (docs/design.md 「時鐘」).
const taskWindow = Duration(seconds: 40);
