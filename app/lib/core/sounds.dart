import 'dart:async';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/widgets.dart';

import 'content.dart';

/// The music (design/sounds/make_sounds.py): one tune for each part of the
/// day, one for each place outside, and the quiet one for resting.
enum Music {
  morning('music_morning'),
  day('music_day'),
  afternoon('music_afternoon'),
  evening('music_evening'),
  night('music_night'),
  outside('music_outside'),
  school('music_school'),
  market('music_market'),
  clinic('music_clinic'),
  rest('music_rest');

  const Music(this.file);

  final String file;

  /// The tune for a scene, given the task of the moment.
  static Music of(Scene scene, Task? task) => switch (scene) {
        Scene.street || Scene.park => outside,
        Scene.school => school,
        Scene.market => market,
        Scene.clinic => clinic,
        _ => switch (task) {
            null || Task.wake || Task.teeth || Task.dress || Task.breakfast || Task.schoolGo => morning,
            Task.school || Task.market || Task.cook => day,
            Task.home || Task.park || Task.tidy || Task.chore || Task.nap => afternoon,
            Task.dinner || Task.bath || Task.teethNight => evening,
            Task.sleep => night,
          },
      };
}

/// Short sounds are named by their file in assets/sounds/ (tap, pop, yay,
/// brush, toilet_flush, `buddy_<kind>`…; design/sounds/README.md lists them).
abstract interface class Sounds {
  set music(bool on);
  set effects(bool on);

  void play(String sfx);

  /// [owner] (a screen) wants [music]; the one asked for last plays.
  void hold(Object owner, Music? music);

  void release(Object owner);
}

class MusicHolders {
  final _holders = <Object, Music?>{};

  void hold(Object owner, Music? music) {
    _holders.remove(owner);
    _holders[owner] = music;
  }

  void release(Object owner) => _holders.remove(owner);

  Music? get current => _holders.isEmpty ? null : _holders.values.last;
}

class SilentSounds implements Sounds {
  const SilentSounds();

  @override
  set music(bool on) {}

  @override
  set effects(bool on) {}

  @override
  void play(String sfx) {}

  @override
  void hold(Object owner, Music? music) {}

  @override
  void release(Object owner) {}
}

/// Remembers the sounds played (tests).
class RecordingSounds implements Sounds {
  final played = <String>[];
  final _holders = MusicHolders();

  Music? get music => _holders.current;

  @override
  set music(bool on) {}

  @override
  set effects(bool on) {}

  @override
  void play(String sfx) => played.add(sfx);

  @override
  void hold(Object owner, Music? music) => _holders.hold(owner, music);

  @override
  void release(Object owner) => _holders.release(owner);
}

/// Plays through audioplayers: a pool per sound, one looping player for the
/// music; quiet while the app is in the background.
class SystemSounds implements Sounds {
  SystemSounds() {
    _lifecycle = AppLifecycleListener(onHide: () => _setAway(true), onShow: () => _setAway(false));
  }

  static const _sfxVolume = 0.85, _musicVolume = 0.35;

  late final AppLifecycleListener _lifecycle;
  final _pools = <String, Future<AudioPool>>{};
  final _holders = MusicHolders();
  Future<void>? _setUp;
  AudioPlayer? _loop;
  Music? _playing;
  var _music = true, _effects = true, _away = false;

  @override
  set music(bool on) {
    _music = on;
    _update();
  }

  @override
  set effects(bool on) => _effects = on;

  void _setAway(bool away) {
    _away = away;
    _update();
  }

  Future<void> _ready() => _setUp ??= AudioPlayer.global.setAudioContext(
        AudioContextConfig(focus: AudioContextConfigFocus.mixWithOthers, respectSilence: true).build(),
      );

  @override
  void play(String sfx) {
    if (!_effects || _away || sfx.isEmpty) return;
    unawaited(_play(sfx));
  }

  Future<void> _play(String sfx) async {
    try {
      await _ready();
      final pool = await (_pools[sfx] ??= AudioPool.createFromAsset(path: 'sounds/$sfx.wav', maxPlayers: 4));
      await pool.start(volume: _sfxVolume);
    } catch (_) {
      _pools.remove(sfx);
    }
  }

  @override
  void hold(Object owner, Music? music) {
    _holders.hold(owner, music);
    _update();
  }

  @override
  void release(Object owner) {
    _holders.release(owner);
    _update();
  }

  void _update() {
    final wanted = !_music || _away ? null : _holders.current;
    if (wanted == _playing) return;
    _playing = wanted;
    unawaited(_switchTo(wanted));
  }

  Future<void> _switchTo(Music? music) async {
    try {
      await _ready();
      var loop = _loop;
      if (loop == null) {
        loop = _loop = AudioPlayer();
        await loop.setReleaseMode(ReleaseMode.loop);
      }
      await loop.stop();
      if (music == null || music != _playing) return;
      await loop.setVolume(_musicVolume);
      await loop.play(AssetSource('sounds/${music.file}.wav'));
    } catch (_) {}
  }

  void dispose() {
    _lifecycle.dispose();
    unawaited(_loop?.dispose());
  }
}
