import 'dart:math' as math;

import 'package:flutter/material.dart' hide Step;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/providers.dart';
import '../../core/scenes.dart';
import '../../core/sounds.dart';
import '../../core/steps.dart';
import 'step_views.dart';

/// One little game (docs/design.md 「小遊戲」): the steps of a task, a chore
/// or a happening, one at a time, each a tap/scrub/drag/choose/hold screen.
/// The buddy says what to do; the child's puppet watches with the right
/// face; dots show how far along. At the end a sticker (or a heart) and
/// back to the room.
class PlayScreen extends ConsumerStatefulWidget {
  const PlayScreen({super.key, this.task, this.happening}) : assert(task != null || happening != null);

  final Task? task;
  final Happening? happening;

  @override
  ConsumerState<PlayScreen> createState() => _PlayScreenState();
}

class _PlayScreenState extends ConsumerState<PlayScreen> {
  late final List<Step> _steps;
  late final Sounds _sounds;
  var _at = 0;
  var _finished = false;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    final g = ref.read(gameProvider);
    final day = g.day!;
    final rnd = math.Random(day.seed + day.index * 31 + (widget.task?.index ?? 0) + (widget.happening?.index ?? 0) * 7);
    _steps = widget.task != null
        ? planTask(widget.task!, level: g.settings.level, weather: day.weather, chore: day.chore, rnd: rnd)
        : planHappening(widget.happening!, level: g.settings.level, rnd: rnd);
    WidgetsBinding.instance.addPostFrameCallback((_) => _sayStep());
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  Step get _step => _steps[_at];

  void _sayStep() {
    if (!mounted || _finished) return;
    final s = _step;
    speak(ref, s.safety == null ? s.say : '${s.say}${s.safety}', en: s.en);
  }

  void _stepDone() {
    if (!mounted || _finished) return;
    _sounds.play(_step.sfx);
    if (_at + 1 < _steps.length) {
      setState(() => _at++);
      Future<void>.delayed(const Duration(milliseconds: 250), _sayStep);
      return;
    }
    _finish();
  }

  void _finish() {
    _finished = true;
    final game = ref.read(gameProvider.notifier);
    final t = widget.task;
    final h = widget.happening;
    if (t != null) {
      game.change((g) => g.finish(t));
      _sounds.play('sticker');
      speak(ref, '${Strings.praise[_steps.length % Strings.praise.length]}${Strings.taskDone(t)}');
    } else if (h != null) {
      game.change((g) => g.dealtWith(h));
      _sounds.play('yay');
      speak(ref, Strings.eventDone);
    }
    setState(() {});
    Future<void>.delayed(const Duration(milliseconds: 1600), () {
      if (!mounted) return;
      final g = ref.read(gameProvider);
      if (t != null && g.dayOver) {
        context.go('/night');
      } else if (context.canPop()) {
        context.pop();
      } else {
        context.go('/');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final Scene scene = widget.task?.scene ?? widget.happening?.scene ?? ref.read(sceneProvider);
    _sounds.hold(this, Music.of(scene, widget.task ?? g.day?.current(g.settings)));
    final step = _step;
    final host = StepHost(ref: ref, onDone: _stepDone, mood: step.mood);
    final title = widget.task?.zh ?? widget.happening!.zh;
    final sticker = widget.task?.sticker ?? 'sticker_heart';

    Widget view = switch (step) {
      TapStep() => TapView(key: ValueKey('step-$_at'), step: step, host: host),
      ScrubStep() => ScrubView(key: ValueKey('step-$_at'), step: step, host: host),
      DragStep() => DragView(key: ValueKey('step-$_at'), step: step, host: host),
      ChooseStep() => ChooseView(key: ValueKey('step-$_at'), step: step, host: host),
      HoldStep() => HoldView(key: ValueKey('step-$_at'), step: step, host: host),
    };

    return Scaffold(
      backgroundColor: Paper.page,
      body: Stack(children: [
        Positioned.fill(child: Opacity(opacity: 0.35, child: Art(ArtPath.scene(scene, 'bg'), fit: BoxFit.cover, sky: Paper.sky))),
        SafeArea(
          child: Column(children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
              child: Row(children: [
                RoundButton(label: Strings.stop, icon: Icons.close_rounded, size: 46, onTap: () => context.canPop() ? context.pop() : context.go('/')),
                const SizedBox(width: 10),
                Expanded(child: Pill(text: title, color: widget.task == null ? Paper.coral : Paper.green, size: 18)),
                const SizedBox(width: 10),
                FoundDots(count: _steps.length, done: _finished ? _steps.length : _at, color: Paper.green, size: 16),
              ]),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 10, 12, 0),
              child: Row(crossAxisAlignment: CrossAxisAlignment.end, children: [
                SizedBox(width: 74, height: 96, child: Me(mood: _finished ? Mood.happy : step.mood)),
                const SizedBox(width: 6),
                Expanded(
                  child: SpeakBubble(
                    key: ValueKey('say-$_at'),
                    text: _finished ? Strings.done : step.say,
                    size: 17,
                    color: Paper.coral,
                    onTap: _sayStep,
                  ),
                ),
              ]),
            ),
            if (step.safety != null)
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 6, 20, 0),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  const Icon(Icons.favorite_rounded, color: Paper.coral, size: 18),
                  const SizedBox(width: 6),
                  Flexible(child: Text(step.safety!, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Paper.coral))),
                ]),
              ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
                child: _finished
                    ? Center(child: SizedBox(width: 220, height: 220, child: Bob(amount: 6, child: Art(ArtPath.reward(sticker)))))
                    : AnimatedSwitcher(duration: const Duration(milliseconds: 300), child: view),
              ),
            ),
          ]),
        ),
      ]),
    );
  }
}
