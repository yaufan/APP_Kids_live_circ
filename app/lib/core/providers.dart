import 'dart:math' as math;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'content.dart';
import 'game.dart';
import 'sounds.dart';
import 'store.dart';
import 'voice.dart';

/// What time it is (tests and screenshots set it). Only the play-time limit
/// uses it: the game's own clock does not follow the phone's.
final clockProvider = Provider<DateTime Function()>((ref) => DateTime.now);

/// Dice (tests give a seeded one).
final randomProvider = Provider<math.Random>((ref) => math.Random());

final storeProvider = Provider<GameStore>((ref) => MemoryStore());
final savedGameProvider = Provider<Game>((ref) => const Game());
final soundsProvider = Provider<Sounds>((ref) => const SilentSounds());
final voiceProvider = Provider<Voice>((ref) => const SilentVoice());

/// The game; every change is saved straight away.
final gameProvider = NotifierProvider<GameNotifier, Game>(GameNotifier.new);

class GameNotifier extends Notifier<Game> {
  @override
  Game build() {
    final g = ref.read(savedGameProvider);
    // A day is always under way once the child exists; an app closed at
    // bedtime opens on the next morning.
    return g.profile != null && (g.day == null || g.dayOver) ? g.beginDay(ref.read(randomProvider)) : g;
  }

  void change(Game Function(Game g) f) {
    final next = f(state);
    if (identical(next, state)) return;
    state = next;
    ref.read(storeProvider).write(next.toJson());
  }

  void settings(Settings Function(Settings s) f) => change((g) => g.copyWith(settings: f(g.settings)));

  /// The first start, or a parent changing the child.
  void setProfile(Profile p) => change((g) => (g.copyWith(profile: p)).day == null ? g.copyWith(profile: p).beginDay(ref.read(randomProvider)) : g.copyWith(profile: p));

  /// Bedtime is over: the next morning.
  void newDay() => change((g) => g.beginDay(ref.read(randomProvider)));
}

/// The scene on screen (the living room at the start).
final sceneProvider = NotifierProvider<SceneNotifier, Scene>(SceneNotifier.new);

class SceneNotifier extends Notifier<Scene> {
  @override
  Scene build() => Scene.living;

  void go(Scene s) => state = s;
}

/// When this sitting started (reset when a parent lets play go on).
final sessionStartProvider = NotifierProvider<SessionStart, DateTime>(SessionStart.new);

class SessionStart extends Notifier<DateTime> {
  @override
  DateTime build() => ref.read(clockProvider)();

  void restart() => state = ref.read(clockProvider)();
}

/// Things said only once per app start (the welcome).
final onceProvider = Provider<Set<String>>((ref) => <String>{});
