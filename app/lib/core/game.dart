import 'dart:math' as math;

import 'content.dart';
import 'day.dart';
import 'events.dart';

/// The child: name, puppet and buddy (docs/design.md 「取名字、選角色」).
class Profile {
  const Profile({this.name = '小寶', this.avatar = const Avatar(), this.buddy = Buddy.dog});

  final String name;
  final Avatar avatar;
  final Buddy buddy;

  static const defaultName = '小寶';
  static const maxName = 8;

  Profile copyWith({String? name, Avatar? avatar, Buddy? buddy}) => Profile(name: name ?? this.name, avatar: avatar ?? this.avatar, buddy: buddy ?? this.buddy);

  Map<String, dynamic> toJson() => {'name': name, 'avatar': avatar.toJson(), 'buddy': buddy.name};

  factory Profile.fromJson(Map<String, dynamic> j) {
    final n = j['name'];
    return Profile(
      name: n is String && n.trim().isNotEmpty ? n.trim().substring(0, math.min(n.trim().length, maxName)) : defaultName,
      avatar: Avatar.fromJson(j['avatar'] is Map ? (j['avatar'] as Map).cast<String, dynamic>() : null),
      buddy: Buddy.values.asNameMap()[j['buddy']] ?? Buddy.dog,
    );
  }
}

/// What a parent set (parent mode).
class Settings {
  const Settings({
    this.level = Level.small,
    this.minutes = 15,
    this.off = const {},
    this.english = false,
    this.music = true,
    this.sounds = true,
    this.voice = true,
    this.full = true,
  });

  final Level level;

  /// How long one sitting may be before a rest.
  final int minutes;

  /// Tasks turned off (no school, no bath…).
  final Set<Task> off;
  final bool english;
  final bool music;
  final bool sounds;
  final bool voice;

  /// The full version (everything); on while testing.
  final bool full;

  static const minuteChoices = [5, 10, 15, 20, 30];

  Settings copyWith({Level? level, int? minutes, Set<Task>? off, bool? english, bool? music, bool? sounds, bool? voice, bool? full}) => Settings(
        level: level ?? this.level,
        minutes: minutes ?? this.minutes,
        off: off ?? this.off,
        english: english ?? this.english,
        music: music ?? this.music,
        sounds: sounds ?? this.sounds,
        voice: voice ?? this.voice,
        full: full ?? this.full,
      );

  Map<String, dynamic> toJson() => {
        'level': level.name,
        'minutes': minutes,
        'off': [for (final t in off) t.name],
        'english': english,
        'music': music,
        'sounds': sounds,
        'voice': voice,
        'full': full,
      };

  factory Settings.fromJson(Map<String, dynamic> j) {
    final m = j['minutes'], off = j['off'];
    bool flag(String k, bool d) => j[k] is bool ? j[k] as bool : d;
    return Settings(
      level: Level.values.asNameMap()[j['level']] ?? Level.small,
      minutes: m is int && minuteChoices.contains(m) ? m : 15,
      off: {
        if (off is List)
          for (final n in off)
            if (Task.values.asNameMap()[n] case final t? when Task.optional.contains(t)) t,
      },
      english: flag('english', false),
      music: flag('music', true),
      sounds: flag('sounds', true),
      voice: flag('voice', true),
      full: flag('full', true),
    );
  }
}

/// Today: which day it is, the weather, the chore, where the clock's hand
/// is, what is done, and what has happened.
class Day {
  const Day({
    required this.weekday,
    required this.weather,
    required this.chore,
    required this.seed,
    this.index = 0,
    this.done = const {},
    this.skipped = const {},
    this.happenings = const {},
    this.happened = const {},
    this.active,
  });

  /// A fresh day after [previous] (null: the very first, a Monday).
  factory Day.next(math.Random rnd, Settings s, {Day? previous}) {
    final weekday = previous == null ? 1 : Week.next(previous.weekday);
    final weather = weatherFor(rnd, yesterday: previous?.weather);
    final chore = nextChore(previous?.chore);
    final seed = rnd.nextInt(1 << 30);
    final plan = DayPlan.make(weekday, off: s.off, full: s.full, weather: weather);
    return Day(weekday: weekday, weather: weather, chore: chore, seed: seed, happenings: scheduleHappenings(plan, weather, math.Random(seed), level: s.level));
  }

  final int weekday;
  final Weather weather;
  final Chore chore;

  /// Seeds the day's dice (the story, the shopping list).
  final int seed;

  /// The task the hand points at.
  final int index;
  final Set<Task> done;
  final Set<Task> skipped;

  /// What happens after which task (events.dart), and which already did.
  final Map<int, Happening> happenings;
  final Set<Happening> happened;

  /// A happening waiting to be dealt with.
  final Happening? active;

  DayPlan plan(Settings s) => DayPlan.make(weekday, off: s.off, full: s.full, weather: weather);

  Task? current(Settings s) {
    final p = plan(s);
    return p.length == 0 ? null : p[index.clamp(0, p.length - 1)];
  }

  bool get weekend => Week.weekend(weekday);

  Day copyWith({int? index, Set<Task>? done, Set<Task>? skipped, Set<Happening>? happened, Happening? active, bool clearActive = false}) => Day(
        weekday: weekday,
        weather: weather,
        chore: chore,
        seed: seed,
        index: index ?? this.index,
        done: done ?? this.done,
        skipped: skipped ?? this.skipped,
        happenings: happenings,
        happened: happened ?? this.happened,
        active: clearActive ? null : (active ?? this.active),
      );

  Map<String, dynamic> toJson() => {
        'weekday': weekday,
        'weather': weather.name,
        'chore': chore.name,
        'seed': seed,
        'index': index,
        'done': [for (final t in done) t.name],
        'skipped': [for (final t in skipped) t.name],
        'happenings': {for (final e in happenings.entries) '${e.key}': e.value.name},
        'happened': [for (final h in happened) h.name],
        if (active != null) 'active': active!.name,
      };

  static Day? fromJson(Map<String, dynamic>? j) {
    if (j == null) return null;
    final wd = j['weekday'], seed = j['seed'], idx = j['index'], hs = j['happenings'];
    Set<Task> tasks(String k) => {
          if (j[k] is List)
            for (final n in j[k] as List)
              ?Task.values.asNameMap()[n],
        };
    return Day(
      weekday: wd is int && wd >= 1 && wd <= 7 ? wd : 1,
      weather: Weather.values.asNameMap()[j['weather']] ?? Weather.sun,
      chore: Chore.values.asNameMap()[j['chore']] ?? Chore.table,
      seed: seed is int ? seed : 0,
      index: idx is int && idx >= 0 ? idx : 0,
      done: tasks('done'),
      skipped: tasks('skipped'),
      happenings: {
        if (hs is Map)
          for (final e in hs.entries)
            if (int.tryParse('${e.key}') case final i? when Happening.values.asNameMap()[e.value] != null) i: Happening.values.byName(e.value as String),
      },
      happened: {
        if (j['happened'] is List)
          for (final n in j['happened'] as List)
            ?Happening.values.asNameMap()[n],
      },
      active: Happening.values.asNameMap()[j['active']],
    );
  }
}

/// One finished day, for the parent's page (the last seven are kept).
class DayRecord {
  const DayRecord(this.weekday, this.done, this.skipped);

  final int weekday;
  final List<Task> done;
  final List<Task> skipped;

  Map<String, dynamic> toJson() => {'weekday': weekday, 'done': [for (final t in done) t.name], 'skipped': [for (final t in skipped) t.name]};

  static DayRecord? fromJson(dynamic j) {
    if (j is! Map) return null;
    final wd = j['weekday'];
    List<Task> tasks(String k) => [
          if (j[k] is List)
            for (final n in j[k] as List)
              ?Task.values.asNameMap()[n],
        ];
    return DayRecord(wd is int && wd >= 1 && wd <= 7 ? wd : 1, tasks('done'), tasks('skipped'));
  }
}

/// Everything kept on the phone: the child, the settings, today, the
/// stickers and decorations earned, the rest. One small file (store.dart).
class Game {
  const Game({
    this.profile,
    this.settings = const Settings(),
    this.day,
    this.stickers = const {},
    this.decos = 0,
    this.height = 0,
    this.daysDone = 0,
    this.history = const [],
    this.restSince,
  });

  /// Null until the first start (the setup page).
  final Profile? profile;
  final Settings settings;

  /// Today (null: a day has to begin).
  final Day? day;

  /// Stickers earned for each task, all time.
  final Map<Task, int> stickers;

  /// Decorations earned (a day with everything done gives one); they fill
  /// the rooms in order (docs/art.md `deco_<n>`).
  final int decos;

  /// Marks on the height chart (a week of days finished gives one).
  final int height;
  final int daysDone;
  final List<DayRecord> history;

  /// When the play time ran out (null: playing).
  final DateTime? restSince;

  static const restLength = Duration(hours: 1);
  static const maxDecos = 18;
  static const maxHeight = 10;
  static const historyKept = 7;

  bool resting(DateTime now) => restSince != null && now.difference(restSince!) < restLength;

  int get stickerCount => stickers.values.fold(0, (a, b) => a + b);

  /// Which decorations a scene shows: `deco_1` for the first one earned in
  /// each of the six rooms, in turn (living first).
  int decosIn(Scene scene) {
    final rooms = Scene.rooms;
    final i = rooms.indexOf(scene);
    if (i < 0) return 0;
    var n = 0;
    for (var d = 0; d < decos; d++) {
      if (d % rooms.length == i) n++;
    }
    return n;
  }

  Game copyWith({Profile? profile, Settings? settings, Day? day, Map<Task, int>? stickers, int? decos, int? height, int? daysDone, List<DayRecord>? history, DateTime? restSince, bool clearRest = false}) => Game(
        profile: profile ?? this.profile,
        settings: settings ?? this.settings,
        day: day ?? this.day,
        stickers: stickers ?? this.stickers,
        decos: decos ?? this.decos,
        height: height ?? this.height,
        daysDone: daysDone ?? this.daysDone,
        history: history ?? this.history,
        restSince: clearRest ? null : (restSince ?? this.restSince),
      );

  /// A day begins (the first one, or the morning after [endDay]).
  Game beginDay(math.Random rnd) => copyWith(day: Day.next(rnd, settings, previous: day));

  /// A task finished: a sticker, the hand moves on, and something may
  /// happen now.
  Game finish(Task t) {
    final d = day!;
    final plan = d.plan(settings);
    final i = plan.indexOf(t);
    final done = {...d.done, t};
    var next = d.copyWith(done: done, skipped: {...d.skipped}..remove(t), index: i == d.index || i < 0 ? _nextIndex(plan, d.index, done) : d.index);
    next = _maybeHappen(next, i);
    return copyWith(day: next, stickers: {...stickers, t: (stickers[t] ?? 0) + 1});
  }

  /// The hand waited long enough: the task is skipped and the hand moves on.
  Game skipCurrent() {
    final d = day!;
    final plan = d.plan(settings);
    if (plan.length == 0 || d.index >= plan.length - 1) return this;
    final t = plan[d.index];
    final skipped = d.done.contains(t) ? d.skipped : {...d.skipped, t};
    return copyWith(day: _maybeHappen(d.copyWith(skipped: skipped, index: d.index + 1), d.index));
  }

  /// The child turned the clock to [index].
  Game turnClock(int index) {
    final d = day!;
    final n = d.plan(settings).length;
    return copyWith(day: d.copyWith(index: n == 0 ? 0 : index.clamp(0, n - 1)));
  }

  Game dealtWith(Happening h) => copyWith(day: day!.copyWith(clearActive: true, happened: {...day!.happened, h}));

  /// Bedtime: the day is over. A day with everything done earns a room
  /// decoration; every seventh day a mark on the height chart.
  Game endDay() {
    final d = day!;
    final plan = d.plan(settings);
    final all = plan.tasks.every(d.done.contains);
    final days = daysDone + 1;
    return copyWith(
      decos: all && decos < maxDecos ? decos + 1 : decos,
      height: days % 7 == 0 && height < maxHeight ? height + 1 : height,
      daysDone: days,
      history: [...history.skip(math.max(0, history.length + 1 - historyKept)), DayRecord(d.weekday, [for (final t in plan.tasks) if (d.done.contains(t)) t], [for (final t in plan.tasks) if (!d.done.contains(t)) t])],
      day: d.copyWith(index: plan.length - 1, clearActive: true),
    );
  }

  bool get dayOver {
    final d = day;
    if (d == null) return false;
    final plan = d.plan(settings);
    return plan.length > 0 && d.done.contains(plan.tasks.last);
  }

  Game rest(DateTime now) => copyWith(restSince: now);

  Game playOn() => copyWith(clearRest: true);

  static int _nextIndex(DayPlan plan, int from, Set<Task> done) {
    for (var i = from + 1; i < plan.length; i++) {
      if (!done.contains(plan[i])) return i;
    }
    return plan.length - 1;
  }

  static Day _maybeHappen(Day d, int afterIndex) {
    final h = d.happenings[afterIndex];
    if (h == null || d.active != null || d.happened.contains(h)) return d;
    return d.copyWith(active: h);
  }

  Map<String, dynamic> toJson() => {
        'version': 1,
        if (profile != null) 'profile': profile!.toJson(),
        'settings': settings.toJson(),
        if (day != null) 'day': day!.toJson(),
        'stickers': {for (final e in stickers.entries) e.key.name: e.value},
        'decos': decos,
        'height': height,
        'daysDone': daysDone,
        'history': [for (final r in history) r.toJson()],
        if (restSince != null) 'restSince': restSince!.toIso8601String(),
      };

  factory Game.fromJson(Map<String, dynamic>? j) {
    if (j == null) return const Game();
    final st = j['stickers'], rest = j['restSince'];
    int count(String k, int max) {
      final v = j[k];
      return v is int && v >= 0 ? math.min(v, max) : 0;
    }

    return Game(
      profile: j['profile'] is Map ? Profile.fromJson((j['profile'] as Map).cast<String, dynamic>()) : null,
      settings: Settings.fromJson(j['settings'] is Map ? (j['settings'] as Map).cast<String, dynamic>() : const {}),
      day: Day.fromJson(j['day'] is Map ? (j['day'] as Map).cast<String, dynamic>() : null),
      stickers: {
        if (st is Map)
          for (final t in Task.values)
            if (st[t.name] is int && (st[t.name] as int) > 0) t: st[t.name] as int,
      },
      decos: count('decos', maxDecos),
      height: count('height', maxHeight),
      daysDone: count('daysDone', 1 << 20),
      history: [
        if (j['history'] is List)
          for (final r in (j['history'] as List)) ?DayRecord.fromJson(r),
      ],
      restSince: rest is String ? DateTime.tryParse(rest) : null,
    );
  }
}
