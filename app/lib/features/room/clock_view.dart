import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/day.dart';
import '../../core/providers.dart';
import '../../core/scenes.dart';
import 'scene_view.dart';

/// The clock (docs/design.md 「時鐘」): a wooden face, the day's pictures
/// round the rim in order, and a hand pointing at the one to do now. Big
/// and interactive, the child turns the hand or taps a picture to change
/// the time; the hand snaps to a picture.
class ClockView extends ConsumerStatefulWidget {
  const ClockView({super.key, required this.plan, required this.index, required this.done, this.size = 120, this.onPick});

  final DayPlan plan;
  final int index;
  final Set<Task> done;
  final double size;

  /// Called with the task picked (null: the clock only shows).
  final void Function(int index)? onPick;

  @override
  ConsumerState<ClockView> createState() => _ClockViewState();
}

class _ClockViewState extends ConsumerState<ClockView> {
  int? _dragGroup;

  int _groupAt(Offset p) {
    final c = Offset(widget.size / 2, widget.size / 2);
    final v = p - c;
    final turn = ((math.atan2(v.dy, v.dx) / (2 * math.pi)) + 0.25) % 1.0;
    return widget.plan.groupOf(widget.plan.taskAtTurn(turn < 0 ? turn + 1 : turn));
  }

  void _drag(Offset p, {bool end = false}) {
    if (widget.onPick == null) return;
    final g = _groupAt(p);
    if (g != _dragGroup) {
      _dragGroup = g;
      ref.read(soundsProvider).play('clock_tick');
      widget.onPick!(widget.plan.groups[g].first);
    }
    if (end) _dragGroup = null;
  }

  @override
  Widget build(BuildContext context) {
    final s = widget.size;
    final plan = widget.plan;
    final n = plan.groups.length;
    final iconSize = s * (n > 10 ? 0.16 : 0.19);
    final ring = s * 0.5 - iconSize * 0.62;
    final current = plan.length == 0 ? -1 : plan.groupOf(widget.index);
    final turn = plan.length == 0 ? 0.0 : plan.handTurn(widget.index);
    final clock = SizedBox(
      width: s,
      height: s,
      child: Stack(clipBehavior: Clip.none, children: [
        Positioned.fill(child: Art(ArtPath.clock('face'))),
        for (var g = 0; g < n; g++)
          Positioned(
            left: s / 2 + ring * math.cos(DayPlan.radians(plan.groupTurn(g))) - iconSize / 2,
            top: s / 2 + ring * math.sin(DayPlan.radians(plan.groupTurn(g))) - iconSize / 2,
            width: iconSize,
            height: iconSize,
            child: _RingIcon(
              icon: plan.groups[g].icon,
              current: g == current,
              done: plan.groups[g].first <= plan.groups[g].last && [for (var i = plan.groups[g].first; i <= plan.groups[g].last; i++) plan[i]].every(widget.done.contains),
              onTap: widget.onPick == null ? null : () => widget.onPick!(plan.groups[g].first),
            ),
          ),
        Positioned(
          left: s / 2 - s * 0.1,
          top: 0,
          width: s * 0.2,
          height: s,
          child: IgnorePointer(
            child: AnimatedRotation(
              turns: turn,
              duration: const Duration(milliseconds: 500),
              curve: Curves.easeOutBack,
              child: Art(ArtPath.clock('hand')),
            ),
          ),
        ),
      ]),
    );
    if (widget.onPick == null) return clock;
    return Listener(
      behavior: HitTestBehavior.opaque,
      onPointerDown: (e) => _drag(e.localPosition),
      onPointerMove: (e) => _drag(e.localPosition),
      onPointerUp: (e) => _drag(e.localPosition, end: true),
      onPointerCancel: (_) => _dragGroup = null,
      child: clock,
    );
  }
}

class _RingIcon extends StatelessWidget {
  const _RingIcon({required this.icon, required this.current, required this.done, this.onTap});

  final ClockIcon icon;
  final bool current;
  final bool done;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    Widget pic = Art(ArtPath.clock('t_${icon.name}'));
    if (current) pic = Bob(amount: 2, child: pic);
    return Semantics(
      container: true,
      button: onTap != null,
      label: '${Strings.clockOpen} ${icon.zh}',
      excludeSemantics: true,
      onTap: onTap,
      child: AnimatedScale(
        scale: current ? 1.25 : 1,
        duration: const Duration(milliseconds: 250),
        child: AnimatedOpacity(
          opacity: done && !current ? 0.45 : 1,
          duration: const Duration(milliseconds: 250),
          child: Stack(fit: StackFit.expand, children: [
            if (current) const Glow(),
            pic,
            if (done)
              const Align(
                alignment: Alignment.bottomRight,
                child: DecoratedBox(
                  decoration: BoxDecoration(color: Paper.green, shape: BoxShape.circle),
                  child: Padding(padding: EdgeInsets.all(1), child: Icon(Icons.check_rounded, size: 11, color: Colors.white)),
                ),
              ),
          ]),
        ),
      ),
    );
  }
}

/// The big clock the child turns (a sheet over the room).
Future<void> showClockSheet(BuildContext context, WidgetRef ref) {
  return showDialog<void>(
    context: context,
    barrierColor: Paper.night.withValues(alpha: 0.45),
    builder: (_) => const _ClockSheet(),
  );
}

class _ClockSheet extends ConsumerWidget {
  const _ClockSheet();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final g = ref.watch(gameProvider);
    final day = g.day!;
    final plan = day.plan(g.settings);
    final task = day.current(g.settings);
    final size = math.min(MediaQuery.sizeOf(context).width - 48, 400.0);
    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.all(16),
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        PaperCard(
          padding: const EdgeInsets.fromLTRB(18, 12, 18, 12),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            Art(ArtPath.clock('w_${day.weather.name}')),
            const SizedBox(width: 8),
            Flexible(child: Text('${Strings.dayLine(day.weekday, day.weather)}${Strings.weekendNote(day.weekday)}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700))),
          ]),
        ),
        const SizedBox(height: 14),
        ClockView(
          key: const ValueKey('big-clock'),
          plan: plan,
          index: day.index,
          done: day.done,
          size: size,
          onPick: (i) {
            ref.read(gameProvider.notifier).change((g) => g.turnClock(i));
            final t = plan[i];
            ref.read(soundsProvider).play('clock_set');
            speak(ref, Strings.clockSay(t), en: t.en);
          },
        ),
        const SizedBox(height: 14),
        if (task != null)
          SpeakBubble(
            key: const ValueKey('clock-say'),
            text: '${task.icon.zh}：${task.zh}',
            color: Paper.coral,
            onTap: () => speak(ref, Strings.clockSay(task), en: task.en),
          ),
        const SizedBox(height: 14),
        RoundButton(label: Strings.back, icon: Icons.check_rounded, color: Paper.green, size: 64, onTap: () => Navigator.of(context).pop()),
      ]),
    );
  }
}
