import 'dart:async';
import 'dart:collection';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/day.dart';
import '../../core/game.dart';
import '../../core/providers.dart';
import '../../core/scenes.dart';
import '../../core/sounds.dart';
import '../parent/parent_gate.dart';
import 'clock_view.dart';
import 'scene_view.dart';

/// The game's main page (docs/design.md 「家：一次一個房間」): the clock on
/// top, one scene filling the page, arrows and a strip of rooms to move,
/// the child's puppet and buddy. Tap a thing to hear its name; tap the
/// glowing thing to start what the clock says; deal with what happens.
class RoomScreen extends ConsumerStatefulWidget {
  const RoomScreen({super.key});

  @override
  ConsumerState<RoomScreen> createState() => _RoomScreenState();
}

class _RoomScreenState extends ConsumerState<RoomScreen> {
  late final Sounds _sounds;
  Timer? _tick;

  /// Seconds the hand has waited on the current task.
  var _waited = 0;
  Task? _said;
  Happening? _saidHappening;
  final _wiggle = <String, int>{};
  var _walking = false;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _tick = Timer.periodic(const Duration(seconds: 1), (_) => _second());
    WidgetsBinding.instance.addPostFrameCallback((_) => _announce(force: true));
  }

  @override
  void dispose() {
    _tick?.cancel();
    _sounds.release(this);
    super.dispose();
  }

  Game get _game => ref.read(gameProvider);

  /// The hand moves on by itself after a while (docs/design.md 「時鐘」).
  void _second() {
    if (!mounted) return;
    final g = _game;
    if (g.day == null || g.dayOver || ModalRoute.of(context)?.isCurrent != true) return;
    _waited++;
    final window = taskWindow(g.settings.level).inSeconds;
    if (_waited == window ~/ 2) _announce(force: true);
    if (_waited >= window) {
      _waited = 0;
      ref.read(gameProvider.notifier).change((g) => g.skipCurrent());
      _sounds.play('clock_tick');
    }
  }

  /// Says what to do now, when it changes (and again when asked).
  void _announce({bool force = false}) {
    final g = _game;
    final day = g.day;
    final name = g.profile?.name ?? Profile.defaultName;
    if (day == null) return;
    final h = day.active;
    if (h != null) {
      if (!force && _saidHappening == h) return;
      _saidHappening = h;
      _sounds.play(h == Happening.garbage ? 'garbage_truck' : _signSound(h));
      speak(ref, Strings.happening(name, h), en: h.en);
      return;
    }
    _saidHappening = null;
    final t = day.current(g.settings);
    if (t == null || (!force && _said == t)) return;
    _said = t;
    final here = ref.read(sceneProvider);
    speak(ref, here == t.scene ? '${Strings.nowDo(name, t)}${Strings.here(t)}' : '${Strings.nowDo(name, t)}${Strings.goTo(t.scene)}', en: t.en);
  }

  String _signSound(Happening h) => switch (h) {
        Happening.pee => 'drop',
        Happening.hungry || Happening.buddyHungry => 'tummy',
        Happening.sleepy => 'yawn',
        Happening.sneeze => 'sneeze',
        Happening.cold => 'shiver',
        Happening.sweaty => 'sweat',
        Happening.doorbell => 'doorbell',
        Happening.phone => 'phone_ring',
        Happening.thunder => 'thunder',
        Happening.earthquake => 'earthquake',
        Happening.rainLaundry => 'rain',
        Happening.mosquito => 'mosquito',
        Happening.blackout => 'light_off',
        Happening.spill => 'spill',
        _ => 'hint',
      };

  /// Where to go for what the clock says (a happening first).
  Scene? _targetScene(Game g) {
    final d = g.day;
    if (d == null) return null;
    final h = d.active;
    if (h != null) return h.scene ?? ref.read(sceneProvider);
    return d.current(g.settings)?.scene;
  }

  String? _targetThing(Game g) {
    final d = g.day;
    if (d == null) return null;
    final h = d.active;
    if (h != null) return h.target;
    final t = d.current(g.settings);
    if (t == null) return null;
    return t == Task.chore ? d.chore.target : t.target;
  }

  /// The next scene on the way from [from] to [to] (through the exits).
  static Scene? _nextHop(Map<Scene, SceneData> scenes, Scene from, Scene to) {
    if (from == to) return null;
    final prev = <Scene, Scene>{from: from};
    final queue = Queue<Scene>()..add(from);
    while (queue.isNotEmpty) {
      final s = queue.removeFirst();
      for (final n in _neighbours(scenes, s)) {
        if (prev.containsKey(n)) continue;
        prev[n] = s;
        if (n == to) {
          var at = to;
          while (prev[at] != from) {
            at = prev[at]!;
          }
          return at;
        }
        queue.add(n);
      }
    }
    return null;
  }

  static Iterable<Scene> _neighbours(Map<Scene, SceneData> scenes, Scene s) sync* {
    yield* scenes[s]?.exits.values ?? const [];
    if (s == Scene.street) yield* Scene.places;
    if (s == Scene.entrance) yield Scene.street;
  }

  void _go(Scene s) {
    if (_walking) return;
    final from = ref.read(sceneProvider);
    if (from == s) return;
    _sounds.play(s.home && from.home ? 'walk' : 'door');
    setState(() => _walking = true);
    Future<void>.delayed(const Duration(milliseconds: 350), () {
      if (!mounted) return;
      ref.read(sceneProvider.notifier).go(s);
      setState(() => _walking = false);
      _said = null;
      _announce();
    });
  }

  void _tapThing(Thing t, Game g, Scene here) {
    _sounds.play('tap');
    setState(() => _wiggle[t.id] = (_wiggle[t.id] ?? 0) + 1);
    final target = _targetThing(g);
    if (_targetScene(g) == here && target == t.id) {
      _start(g);
      return;
    }
    final place = Scene.values.asNameMap()[t.id];
    if (here == Scene.street && (place != null || t.id == 'home')) {
      _go(place ?? Scene.entrance);
      return;
    }
    // The stairs and the front door are the way through.
    final exits = ref.read(scenesProvider).asData?.value[here]?.exits ?? const {};
    if (t.id == 'stairs' && exits['up'] != null) {
      _go(exits['up']!);
      return;
    }
    if (t.id == 'door' && here == Scene.entrance) {
      _go(Scene.street);
      return;
    }
    speak(ref, t.zh, en: t.en);
  }

  void _start(Game g) {
    final d = g.day!;
    _waited = 0;
    final h = d.active;
    if (h != null) {
      context.push('/play/happening/${h.name}');
      return;
    }
    final t = d.current(g.settings);
    if (t != null) context.push('/play/task/${t.name}');
  }

  void _tapAvatar(Game g, Scene here, Map<Scene, SceneData> scenes) {
    final target = _targetScene(g);
    final d = g.day;
    if (d?.active != null && d!.active!.scene == null) {
      _start(g);
      return;
    }
    if (target != null && target != here && g.settings.level == Level.small) {
      // The little ones: the puppet walks there by itself.
      _sounds.play('walk');
      _go(target);
      return;
    }
    _sounds.play('pop');
    _announce(force: true);
  }

  Map<String, String> _states(Game g, Scene here) {
    final d = g.day!;
    final done = d.done;
    final evening = d.plan(g.settings).indexOf(Task.dinner) <= d.index && d.plan(g.settings).indexOf(Task.dinner) >= 0;
    return {
      'toybox': done.contains(Task.tidy) || here != Scene.living ? '' : 'full',
      'lamp': evening ? 'on' : 'off',
      'plant': d.active == Happening.plant ? 'wilt' : '',
      'plants': d.active == Happening.plant ? 'wilt' : '',
      'nightlight': done.contains(Task.sleep) ? 'off' : 'on',
      'curtain': done.contains(Task.wake) && !done.contains(Task.sleep) ? 'open' : 'closed',
      'toilet': 'closed',
      'rack': d.happened.contains(Happening.rainLaundry) || (d.chore == Chore.laundry && done.contains(Task.chore)) ? 'empty' : '',
    };
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final here = ref.watch(sceneProvider);
    final scenes = ref.watch(scenesProvider).asData?.value;
    final day = g.day;
    if (day == null || scenes == null) return const Scaffold(body: SizedBox());
    final plan = day.plan(g.settings);
    final task = day.current(g.settings);
    final data = scenes[here]!;
    _sounds.hold(this, Music.of(here, task));

    final target = _targetScene(g);
    final targetThing = _targetThing(g);
    final hop = target == null ? null : _nextHop(scenes, here, target);
    final hereIsTarget = target == here;
    final evening = task == Task.bath || task == Task.teethNight || task == Task.sleep || task == Task.dinner;
    final sky = skyColor(day.weather.name, evening: evening, night: g.dayOver);
    final name = g.profile?.name ?? Profile.defaultName;
    final active = day.active;

    String? exitGlow;
    if (hop != null) {
      for (final e in data.exits.entries) {
        if (e.value == hop) exitGlow = e.key;
      }
      if (here == Scene.entrance && hop == Scene.street) exitGlow = 'out';
    }
    // The way to go lights up: the thing to tap here, or the stairs / the
    // door on the way, or an arrow on the strip.
    final glowThing = hereIsTarget ? targetThing : (exitGlow == 'up' ? 'stairs' : (exitGlow == 'out' ? 'door' : null));

    Widget arrow(String key, IconData icon, Scene to, String label) {
      final lit = exitGlow == key;
      return Semantics(
        key: ValueKey('exit-$key'),
        container: true,
        button: true,
        label: '$label：${to.zh}',
        excludeSemantics: true,
        onTap: () => _go(to),
        child: Pressable(
          onTap: () => _go(to),
          sound: null,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 52,
            height: 60,
            decoration: BoxDecoration(
              color: lit ? Paper.glow : Paper.page,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Paper.edge, width: 1.5),
              boxShadow: lit ? [BoxShadow(color: Paper.gold.withValues(alpha: 0.6), blurRadius: 14)] : null,
            ),
            child: Icon(icon, size: 32, color: Paper.ink),
          ),
        ),
      );
    }

    final sceneView = SceneView(
      key: ValueKey('scene-${here.name}'),
      data: data,
      avatar: g.profile?.avatar ?? const Avatar(),
      buddy: g.profile?.buddy ?? Buddy.dog,
      states: _states(g, here),
      decos: g.decosIn(here),
      sky: sky,
      glow: glowThing,
      glowAvatar: active != null && active.scene == null,
      sign: active?.sign,
      mood: active?.mood ?? (g.dayOver ? Mood.sleepy : Mood.normal),
      pose: g.dayOver ? 'lie' : 'stand',
      buddyPose: g.dayOver ? 'sleep' : 'stand',
      dim: g.dayOver ? 1 : 0,
      wiggle: Map.of(_wiggle),
      onTapThing: (t) => _tapThing(t, g, here),
      onTapAvatar: () => _tapAvatar(g, here, scenes),
      onTapBuddy: () {
        _sounds.play(g.profile?.buddy.sound ?? 'buddy_dog');
        _announce(force: true);
      },
    );

    final stripScenes = here.home ? Scene.rooms : [Scene.living, Scene.street, ...Scene.places];
    final bubbleText = active != null ? Strings.happening(name, active) : (task == null ? '' : (hereIsTarget ? '${Strings.nowDo(name, task)}${Strings.here(task)}' : '${Strings.nowDo(name, task)}${Strings.goTo(task.scene)}'));

    return Scaffold(
      backgroundColor: Paper.page,
      body: SafeArea(
        child: Column(children: [
          // The clock bar.
          Padding(
            padding: const EdgeInsets.fromLTRB(10, 6, 10, 0),
            child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Semantics(
                key: const ValueKey('clock'),
                container: true,
                button: true,
                label: Strings.clockOpen,
                excludeSemantics: true,
                onTap: () => showClockSheet(context, ref),
                child: Pressable(
                  onTap: () {
                    _waited = 0;
                    showClockSheet(context, ref);
                  },
                  child: ClockView(plan: plan, index: day.index, done: day.done, size: 132),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Row(children: [
                    PaperCard(
                      radius: 16,
                      padding: const EdgeInsets.fromLTRB(8, 4, 10, 4),
                      child: Row(mainAxisSize: MainAxisSize.min, children: [
                        SizedBox(width: 28, height: 28, child: Art(ArtPath.clock('w_${day.weather.name}'))),
                        const SizedBox(width: 4),
                        Text(Week.zh[day.weekday], style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                      ]),
                    ),
                    const Spacer(),
                    RoundButton(label: Strings.stickers, icon: Icons.star_rounded, size: 46, color: Paper.gold, onTap: () => context.push('/stickers')),
                    const SizedBox(width: 6),
                    RoundButton(
                      label: Strings.parent,
                      icon: Icons.lock_outline_rounded,
                      size: 40,
                      onTap: () async {
                        if (await showParentGate(context) && context.mounted) context.push('/parent');
                      },
                    ),
                  ]),
                  const SizedBox(height: 6),
                  if (bubbleText.isNotEmpty)
                    SpeakBubble(
                      key: const ValueKey('bubble'),
                      text: bubbleText,
                      size: 15,
                      color: active != null ? Paper.coral : Paper.green,
                      onTap: () => _announce(force: true),
                    ),
                ]),
              ),
            ]),
          ),
          // The scene with the arrows over it.
          Expanded(
            child: Stack(children: [
              Positioned.fill(
                child: AnimatedOpacity(
                  opacity: _walking ? 0.0 : 1,
                  duration: const Duration(milliseconds: 300),
                  child: Padding(padding: const EdgeInsets.fromLTRB(4, 6, 4, 2), child: sceneView),
                ),
              ),
            ]),
          ),
          // The strip of rooms.
          Container(
            height: 78,
            padding: const EdgeInsets.fromLTRB(4, 6, 4, 8),
            decoration: const BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(color: Color(0x226B4F33), offset: Offset(0, -2), blurRadius: 8)]),
            child: Row(children: [
              // The left end: the way left, or down the stairs.
              if (data.exits['left'] case final s?)
                arrow('left', Icons.arrow_back_rounded, s, Strings.left)
              else if (data.exits['down'] case final s?)
                arrow('down', Icons.arrow_downward_rounded, s, Strings.stairsDown)
              else if (!here.home && here != Scene.street)
                arrow('back', Icons.arrow_back_rounded, Scene.street, Strings.toStreet)
              else
                const SizedBox(width: 52),
              for (final s in stripScenes)
                Expanded(
                  child: Center(
                    child: _StripIcon(
                      scene: s,
                      here: s == here,
                      lit: target != null && target != here && (s == target || (here.home ? !target.home && s == Scene.entrance : target.home && s == Scene.living)),
                      onTap: () => _go(here.home || s != Scene.living ? s : Scene.entrance),
                    ),
                  ),
                ),
              if (data.exits['right'] case final s?)
                arrow('right', Icons.arrow_forward_rounded, s, Strings.right)
              else if (data.exits['up'] case final s?)
                arrow('up', Icons.stairs_rounded, s, Strings.stairsUp)
              else if (data.exits['down'] case final s? when data.exits['left'] != null)
                arrow('down', Icons.arrow_downward_rounded, s, Strings.stairsDown)
              else if (here == Scene.entrance)
                arrow('out', Icons.door_front_door_rounded, Scene.street, Strings.outside)
              else
                const SizedBox(width: 52),
            ]),
          ),
        ]),
      ),
    );
  }
}

/// One room on the strip at the bottom: a little picture of its main thing.
class _StripIcon extends StatelessWidget {
  const _StripIcon({required this.scene, required this.here, required this.lit, required this.onTap});

  final Scene scene;
  final bool here;
  final bool lit;
  final VoidCallback onTap;

  static String thingOf(Scene s) => switch (s) {
        Scene.living => 'sofa',
        Scene.bedroom => 'bed',
        Scene.bathroom => 'bathtub',
        Scene.kitchen => 'fridge',
        Scene.entrance => 'door',
        Scene.balcony => 'plants',
        Scene.street => 'home',
        Scene.park => 'slide',
        Scene.school => 'cubby',
        Scene.market => 'cart',
        Scene.clinic => 'doctor',
      };

  @override
  Widget build(BuildContext context) {
    Widget pic = Art(ArtPath.scene(scene, thingOf(scene)));
    if (lit) pic = Bob(amount: 3, child: pic);
    return Semantics(
      key: ValueKey('room-${scene.name}'),
      container: true,
      button: true,
      selected: here,
      label: scene.zh,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        sound: null,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: 54,
          height: 60,
          padding: const EdgeInsets.all(4),
          decoration: BoxDecoration(
            color: lit ? Paper.glow : (here ? Paper.page : Colors.white),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: here ? Paper.coral : Paper.edge, width: here ? 3 : 1.5),
            boxShadow: lit ? [BoxShadow(color: Paper.gold.withValues(alpha: 0.6), blurRadius: 14)] : null,
          ),
          child: pic,
        ),
      ),
    );
  }
}
