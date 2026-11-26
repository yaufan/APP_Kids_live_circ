import 'package:flutter/widgets.dart';
import 'package:flutter_tts/flutter_tts.dart';

/// Reads out what the buddy says and the names of things, for children who
/// cannot read yet: Taiwanese Mandarin, then (if a parent turned it on) the
/// English words ("花, flower"). It uses the phone's own speech; parents
/// can turn it off.
abstract interface class Voice {
  /// Says [zh] in Mandarin, then [en] (if any) in English. Completes when
  /// the line has been said (or was cut off by a newer one or a stop).
  Future<void> say(String zh, {String? en});
  Future<void> stop();
}

/// Whether the app is out of sight (another app, the home screen, the
/// screen off): nothing is said then, and the room's clock waits.
bool get appHidden => switch (WidgetsBinding.instance.lifecycleState) {
      AppLifecycleState.hidden || AppLifecycleState.paused || AppLifecycleState.detached => true,
      _ => false,
    };

class SystemVoice implements Voice {
  SystemVoice() {
    // Out of sight, the line being said stops (the room does not go on
    // talking to an empty room).
    _life = AppLifecycleListener(onHide: stop);
  }

  late final AppLifecycleListener _life;
  FlutterTts? _tts;
  Future<FlutterTts>? _setUp;
  String? _language;

  /// Counts the lines asked for (and the stops): only the newest is said.
  var _turn = 0;

  /// The engine, set up once. Every line waits for the whole set-up, so a
  /// line asked for while the first one (the welcome) is still setting up
  /// is not cut off by the first one's late stop(): the newest line is the
  /// one that is said.
  Future<FlutterTts> _engine() => _setUp ??= () async {
        final tts = _tts = FlutterTts();
        await tts.awaitSpeakCompletion(true);
        await tts.setSpeechRate(0.45);
        await tts.setPitch(1.2);
        return tts;
      }();

  Future<void> _in(FlutterTts tts, String language) async {
    if (_language == language) return;
    _language = language;
    await tts.setLanguage(language);
  }

  @override
  Future<void> say(String zh, {String? en}) async {
    final turn = ++_turn;
    try {
      final tts = await _engine();
      if (turn != _turn) return;
      await tts.stop();
      if (zh.isNotEmpty) {
        await _in(tts, 'zh-TW');
        // A newer line, or a stop, while this one waited.
        if (turn != _turn) return;
        await tts.speak(zh);
      }
      if (en == null || en.isEmpty || turn != _turn) return;
      await _in(tts, 'en-US');
      if (turn != _turn) return;
      await tts.speak(en);
    } catch (_) {
      // No speech engine (tests, or a phone without one): the words on
      // screen and the pictures are enough.
    }
  }

  @override
  Future<void> stop() async {
    _turn++;
    try {
      await _tts?.stop();
    } catch (_) {}
  }

  void dispose() => _life.dispose();
}

class SilentVoice implements Voice {
  const SilentVoice();

  @override
  Future<void> say(String zh, {String? en}) async {}

  @override
  Future<void> stop() async {}
}

/// Remembers what was said, and how often it was stopped (tests). Lines
/// take no time unless a test holds them ([hold]).
class RecordingVoice implements Voice {
  final said = <String>[];
  var stops = 0;

  /// While set, a line is "being said" until the test completes it.
  Future<void>? hold;

  @override
  Future<void> say(String zh, {String? en}) async {
    said.add(en == null ? zh : '$zh|$en');
    final h = hold;
    if (h != null) await h;
  }

  @override
  Future<void> stop() async => stops++;
}
