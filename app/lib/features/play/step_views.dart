import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/providers.dart';
import '../../core/scenes.dart';
import '../../core/steps.dart';

/// A step's picture: a prop, a scene thing, or one of the puppets.
class StepPic extends StatelessWidget {
  const StepPic(this.name, {super.key, this.mood = Mood.normal});

  final String name;
  final Mood mood;

  @override
  Widget build(BuildContext context) => switch (name) {
        '@avatar' || '@body' => Me(mood: mood),
        '@head' => ClipRect(child: Align(alignment: Alignment.topCenter, heightFactor: 0.62, child: Me(mood: mood))),
        '@buddy' => const MyBuddy(pose: 'happy'),
        _ => Art(ArtPath.of(name)),
      };
}

/// What every step view gets.
class StepHost {
  const StepHost({required this.ref, required this.onDone, required this.mood});

  final WidgetRef ref;
  final VoidCallback onDone;
  final Mood mood;

  void play(String sfx) => ref.read(soundsProvider).play(sfx);
  void say(String zh, {String? en}) => speak(ref, zh, en: en);
}

/// Tap each picture (docs/design.md: 拉窗簾、伸懶腰、漱口…).
class TapView extends StatefulWidget {
  const TapView({super.key, required this.step, required this.host});

  final TapStep step;
  final StepHost host;

  @override
  State<TapView> createState() => _TapViewState();
}

class _TapViewState extends State<TapView> {
  late final _done = List<bool>.filled(widget.step.props.length, false);
  var _wiggle = 0;

  void _tap(int i) {
    if (_done[i]) return;
    widget.host.play(widget.step.tapSfx);
    setState(() {
      _done[i] = true;
      _wiggle++;
    });
    if (_done.every((d) => d)) Future<void>.delayed(const Duration(milliseconds: 450), widget.host.onDone);
  }

  @override
  Widget build(BuildContext context) {
    final props = widget.step.props;
    final same = props.toSet().length == 1 && props.length > 1;
    return LayoutBuilder(builder: (context, box) {
      final n = same ? 1 : props.length;
      final size = math.min(box.maxWidth / (n > 2 ? 3.2 : (n == 2 ? 2.3 : 1.6)), box.maxHeight * 0.8);
      Widget pic(int i) {
        final name = _done[i] ? (widget.step.result ?? props[i]) : props[i];
        return Semantics(
          key: ValueKey('tap-$i'),
          container: true,
          button: true,
          label: name,
          excludeSemantics: true,
          onTap: () => _tap(i),
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTapDown: (_) => _tap(i),
            child: AnimatedScale(
              scale: _done[i] && widget.step.result == null ? 0.85 : 1,
              duration: const Duration(milliseconds: 250),
              child: Wiggle(
                trigger: _done[i] ? _wiggle : 0,
                child: Stack(alignment: Alignment.bottomRight, children: [
                  SizedBox(width: size, height: size, child: Bob(amount: _done[i] ? 0 : 3, phase: i * 0.2, child: StepPic(name, mood: widget.host.mood))),
                  if (_done[i] && widget.step.result == null) Padding(padding: EdgeInsets.all(size * 0.05), child: Icon(Icons.check_circle_rounded, size: size * 0.25, color: Paper.green)),
                ]),
              ),
            ),
          ),
        );
      }

      if (same) {
        // The same thing several times (three spoonfuls): one big picture and dots.
        final n = _done.where((d) => d).length;
        return Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          pic(n.clamp(0, props.length - 1)),
          const SizedBox(height: 12),
          FoundDots(count: props.length, done: n, color: Paper.coral),
        ]);
      }
      return Center(child: Wrap(spacing: 14, runSpacing: 14, alignment: WrapAlignment.center, children: [for (var i = 0; i < props.length; i++) pic(i)]));
    });
  }
}

/// Rub the dirt away (刷牙、洗手、擦桌子、掃地、挖沙).
class ScrubView extends StatefulWidget {
  const ScrubView({super.key, required this.step, required this.host});

  final ScrubStep step;
  final StepHost host;

  @override
  State<ScrubView> createState() => _ScrubViewState();
}

class _ScrubViewState extends State<ScrubView> {
  late final List<Offset> _dirt;
  late final List<bool> _gone;
  Offset? _finger;
  Offset? _last;
  var _rubbed = 0.0;
  var _done = false;
  DateTime _lastSfx = DateTime.fromMillisecondsSinceEpoch(0);

  @override
  void initState() {
    super.initState();
    final rnd = math.Random(widget.step.strokes * 7 + widget.step.base.hashCode);
    final n = widget.step.strokes;
    _dirt = [for (var i = 0; i < n; i++) Offset(0.15 + rnd.nextDouble() * 0.7, 0.2 + rnd.nextDouble() * 0.6)];
    _gone = List.filled(n, false);
  }

  void _lift() {
    if (!mounted) return;
    setState(() {
      _finger = null;
      _last = null;
    });
  }

  void _move(Offset p, Size size) {
    if (_done || !mounted) return;
    final last = _last;
    _last = p;
    setState(() => _finger = p);
    if (last != null) _rubbed += (p - last).distance;
    final r = size.shortestSide * 0.11;
    var changed = false;
    for (var i = 0; i < _dirt.length; i++) {
      if (_gone[i]) continue;
      final d = Offset(_dirt[i].dx * size.width, _dirt[i].dy * size.height);
      if ((d - p).distance < r && _rubbed > i * size.shortestSide * 0.12) {
        _gone[i] = true;
        changed = true;
      }
    }
    final now = DateTime.now();
    if (widget.step.loopSfx != null && now.difference(_lastSfx).inMilliseconds > 450) {
      _lastSfx = now;
      widget.host.play(widget.step.loopSfx!);
    }
    if (changed) setState(() {});
    if (_gone.every((g) => g) && _rubbed > widget.step.strokes * size.shortestSide * 0.12) {
      _done = true;
      Future<void>.delayed(const Duration(milliseconds: 350), widget.host.onDone);
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final side = math.min(box.maxWidth, box.maxHeight);
        final size = Size(side, side);
        final dotSize = side * 0.14;
        final toolSize = side * 0.3;
        return Center(
          child: SizedBox(
            width: side,
            height: side,
            child: Listener(
              behavior: HitTestBehavior.opaque,
              onPointerDown: (e) {
                _last = null;
                _move(e.localPosition, size);
              },
              onPointerMove: (e) => _move(e.localPosition, size),
              onPointerUp: (_) => _lift(),
              onPointerCancel: (_) => _lift(),
              child: Stack(clipBehavior: Clip.none, children: [
                Positioned.fill(
                  child: Container(
                    decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.6), borderRadius: BorderRadius.circular(side * 0.08)),
                    padding: EdgeInsets.all(side * 0.06),
                    child: widget.step.base == null ? null : StepPic(widget.step.base!, mood: widget.host.mood),
                  ),
                ),
                for (var i = 0; i < _dirt.length; i++)
                  if (!_gone[i])
                    Positioned(
                      left: _dirt[i].dx * side - dotSize / 2,
                      top: _dirt[i].dy * side - dotSize / 2,
                      width: dotSize,
                      height: dotSize,
                      child: IgnorePointer(child: widget.step.dirt == null ? Container(decoration: BoxDecoration(color: Paper.coral.withValues(alpha: 0.5), shape: BoxShape.circle)) : StepPic(widget.step.dirt!)),
                    ),
                if (_done && widget.step.reveal != null)
                  Positioned(left: side * 0.3, top: side * 0.3, width: side * 0.4, height: side * 0.4, child: Bob(child: StepPic(widget.step.reveal!))),
                Positioned(
                  left: (_finger?.dx ?? side * 0.7) - toolSize / 2,
                  top: (_finger?.dy ?? side * 0.75) - toolSize * 0.8,
                  width: toolSize,
                  height: toolSize,
                  child: IgnorePointer(child: Transform.rotate(angle: _finger == null ? -0.3 : 0.2, child: StepPic(widget.step.tool))),
                ),
                if (!_done && _finger == null)
                  const Positioned(right: 8, bottom: 8, child: Icon(Icons.touch_app_rounded, size: 40, color: Paper.coral)),
              ]),
            ),
          ),
        );
      });
}

/// Drag each item to its slot (食物到盤子、玩具到箱子、衣服到身上).
class DragView extends StatefulWidget {
  const DragView({super.key, required this.step, required this.host});

  final DragStep step;
  final StepHost host;

  @override
  State<DragView> createState() => _DragViewState();
}

class _DragViewState extends State<DragView> {
  /// Where each item went (slot id), or null while in the tray.
  late final List<String?> _placed = List.filled(widget.step.items.length, null);
  int? _held;
  Offset _at = Offset.zero;
  var _wiggle = 0;
  var _done = false;

  List<Rect> _slotRects(Size size, double slotSize) {
    final slots = widget.step.slots;
    final out = <Rect>[];
    final boardTop = size.height * 0.06;
    final boardH = size.height * 0.52;
    for (var i = 0; i < slots.length; i++) {
      final s = slots[i];
      final cx = s.x != null ? size.width * (0.15 + 0.7 * s.x!) : size.width * (i + 0.5) / slots.length;
      final cy = s.y != null ? boardTop + boardH * (0.1 + 0.8 * s.y!) : boardTop + boardH * 0.5;
      out.add(Rect.fromCenter(center: Offset(cx, cy), width: slotSize, height: slotSize));
    }
    return out;
  }

  Rect _trayRect(int i, Size size, double itemSize) {
    final items = widget.step.items;
    final perRow = math.min(items.length, (size.width / (itemSize * 1.1)).floor().clamp(1, 6));
    final rows = (items.length / perRow).ceil();
    final row = i ~/ perRow, col = i % perRow;
    final inRow = row == rows - 1 ? items.length - row * perRow : perRow;
    final left = (size.width - inRow * itemSize * 1.1) / 2 + col * itemSize * 1.1;
    final top = size.height - (rows - row) * itemSize * 1.05;
    return Rect.fromLTWH(left, top, itemSize, itemSize);
  }

  void _drop(Size size, double slotSize) {
    final i = _held;
    if (i == null || !mounted) return;
    _held = null;
    final item = widget.step.items[i];
    final rects = _slotRects(size, slotSize);
    for (var s = 0; s < rects.length; s++) {
      final slot = widget.step.slots[s];
      if (!rects[s].inflate(slotSize * 0.35).contains(_at)) continue;
      final inSlot = _placed.where((p) => p == slot.id).length;
      if (slot.takes(item) && inSlot < slot.capacity) {
        setState(() => _placed[i] = slot.id);
        widget.host.play(widget.step.dropSfx);
        if (widget.step.needed.every((n) => _placed[widget.step.items.indexOf(n)] != null) && !_done) {
          _done = true;
          Future<void>.delayed(const Duration(milliseconds: 400), widget.host.onDone);
        }
        return;
      }
      widget.host.play('wrong');
      widget.host.say(widget.step.wrong ?? Strings.bounce);
      setState(() => _wiggle++);
      return;
    }
    setState(() {});
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final size = Size(box.maxWidth, box.maxHeight);
        final slots = widget.step.slots;
        final slotSize = math.min(size.width / (slots.length + 0.6), size.height * 0.26).clamp(60.0, 170.0);
        final itemSize = math.min(size.width / (math.min(widget.step.items.length, 4) + 0.8), size.height * 0.2).clamp(54.0, 120.0);
        final rects = _slotRects(size, slotSize);
        final board = widget.step.board;
        final kids = <Widget>[
          if (board != null)
            Positioned(left: size.width * 0.1, top: size.height * 0.04, width: size.width * 0.8, height: size.height * 0.56, child: IgnorePointer(child: StepPic(board, mood: widget.host.mood))),
          for (var s = 0; s < slots.length; s++)
            Positioned.fromRect(
              key: ValueKey('slot-${slots[s].id}'),
              rect: rects[s],
              child: IgnorePointer(
                child: slots[s].prop != null
                    ? StepPic(slots[s].prop!)
                    : Container(
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.white.withValues(alpha: board == null ? 0.8 : 0.35),
                          border: Border.all(color: Paper.inkSoft.withValues(alpha: 0.5), width: 2.5),
                        ),
                      ),
              ),
            ),
        ];
        // Items in slots (stacked a little), then the tray, then the held one.
        final inSlot = <String, int>{};
        for (var i = 0; i < widget.step.items.length; i++) {
          final slotId = _placed[i];
          if (slotId == null || _held == i) continue;
          final s = slots.indexWhere((x) => x.id == slotId);
          final k = inSlot[slotId] = (inSlot[slotId] ?? 0) + 1;
          final r = rects[s];
          final sz = slotSize * (slots[s].prop == null && slots[s].capacity == 1 ? 0.8 : 0.55);
          kids.add(Positioned(
            left: r.center.dx - sz / 2 + (k - 1) * sz * 0.25 - (slots[s].capacity - 1) * sz * 0.12,
            top: r.center.dy - sz / 2 + (slots[s].prop != null ? sz * 0.15 : 0),
            width: sz,
            height: sz,
            child: IgnorePointer(child: StepPic(widget.step.items[i].prop)),
          ));
        }
        for (var i = 0; i < widget.step.items.length; i++) {
          if (_placed[i] != null || _held == i) continue;
          kids.add(Positioned.fromRect(
            key: ValueKey('item-$i'),
            rect: _trayRect(i, size, itemSize),
            child: Wiggle(trigger: _wiggle, child: Bob(amount: 2, phase: i * 0.15, child: StepPic(widget.step.items[i].prop))),
          ));
        }
        if (_held case final h?) {
          kids.add(Positioned(
            left: _at.dx - itemSize * 0.65,
            top: _at.dy - itemSize * 1.2,
            width: itemSize * 1.3,
            height: itemSize * 1.3,
            child: IgnorePointer(child: StepPic(widget.step.items[h].prop)),
          ));
        }
        return Listener(
          behavior: HitTestBehavior.opaque,
          onPointerDown: (e) {
            if (_done) return;
            for (var i = widget.step.items.length - 1; i >= 0; i--) {
              if (_placed[i] != null) continue;
              if (_trayRect(i, size, itemSize).inflate(8).contains(e.localPosition)) {
                widget.host.play('pop');
                final zh = widget.step.items[i].zh;
                if (zh != null) widget.host.say(zh);
                setState(() {
                  _held = i;
                  _at = e.localPosition;
                });
                return;
              }
            }
          },
          onPointerMove: (e) {
            if (_held != null) setState(() => _at = e.localPosition);
          },
          onPointerUp: (_) => _drop(size, slotSize),
          onPointerCancel: (_) => _drop(size, slotSize),
          child: Stack(clipBehavior: Clip.none, children: kids),
        );
      });
}

/// Tap the right one (看天氣選衣服、哪盆枯了、水溫剛剛好).
class ChooseView extends StatefulWidget {
  const ChooseView({super.key, required this.step, required this.host});

  final ChooseStep step;
  final StepHost host;

  @override
  State<ChooseView> createState() => _ChooseViewState();
}

class _ChooseViewState extends State<ChooseView> {
  int? _picked;
  var _wiggle = 0;

  void _pick(int i) {
    if (_picked != null) return;
    final o = widget.step.options[i];
    if (widget.step.good.contains(o.prop)) {
      setState(() => _picked = i);
      widget.host.play('yay');
      widget.host.say(o.zh, en: o.en);
      Future<void>.delayed(const Duration(milliseconds: 600), widget.host.onDone);
      return;
    }
    widget.host.play('wrong');
    widget.host.say(widget.step.whyWrong?.call(o.prop) ?? Strings.bounce);
    setState(() => _wiggle++);
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final n = widget.step.options.length;
        final size = math.min(box.maxWidth / (n + 0.5), box.maxHeight * 0.7);
        return Center(
          child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            for (var i = 0; i < n; i++)
              Padding(
                padding: EdgeInsets.symmetric(horizontal: size * 0.08),
                child: Semantics(
                  key: ValueKey('choice-$i'),
                  container: true,
                  button: true,
                  label: widget.step.options[i].zh,
                  excludeSemantics: true,
                  onTap: () => _pick(i),
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTapDown: (_) => _pick(i),
                    child: Wiggle(
                      trigger: _wiggle,
                      child: AnimatedScale(
                        scale: _picked == i ? 1.15 : (_picked == null ? 1 : 0.8),
                        duration: const Duration(milliseconds: 250),
                        child: PaperCard(
                          ring: _picked == i ? Paper.green : null,
                          padding: EdgeInsets.all(size * 0.08),
                          child: Column(mainAxisSize: MainAxisSize.min, children: [
                            SizedBox(width: size * 0.7, height: size * 0.7, child: StepPic(widget.step.options[i].prop)),
                            Text(widget.step.options[i].zh, style: TextStyle(fontSize: (size * 0.14).clamp(14, 22), fontWeight: FontWeight.w700)),
                          ]),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ]),
        );
      });
}

/// Press and hold (坐馬桶、等紅燈、深呼吸、澆水剛剛好).
class HoldView extends StatefulWidget {
  const HoldView({super.key, required this.step, required this.host});

  final HoldStep step;
  final StepHost host;

  @override
  State<HoldView> createState() => _HoldViewState();
}

class _HoldViewState extends State<HoldView> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: Duration(seconds: widget.step.tooLong ?? widget.step.seconds))
    ..addListener(() {
      setState(() {});
      final step = widget.step;
      if (step.tooLong == null) {
        if (_c.value >= 1 && !_done) _finish();
      } else if (_c.isCompleted && !_done) {
        _tooMuch();
      }
    });
  Timer? _loop;
  var _done = false;

  double get _need => widget.step.tooLong == null ? 1 : widget.step.seconds / widget.step.tooLong!;

  @override
  void dispose() {
    _loop?.cancel();
    _c.dispose();
    super.dispose();
  }

  void _down() {
    if (_done) return;
    _c.forward(from: 0);
    final sfx = widget.step.loopSfx;
    if (sfx != null) {
      widget.host.play(sfx);
      _loop = Timer.periodic(const Duration(milliseconds: 900), (_) => widget.host.play(sfx));
    }
  }

  void _up() {
    _loop?.cancel();
    if (_done) return;
    if (widget.step.tooLong != null && _c.value >= _need) {
      _finish();
      return;
    }
    _c.stop();
    _c.animateBack(0, duration: const Duration(milliseconds: 300));
  }

  void _tooMuch() {
    _loop?.cancel();
    _c.stop();
    widget.host.play('wrong');
    widget.host.say(widget.step.tooMuch ?? Strings.bounce);
    _c.animateBack(0, duration: const Duration(milliseconds: 500));
  }

  void _finish() {
    _done = true;
    _loop?.cancel();
    _c.stop();
    setState(() {});
    Future<void>.delayed(const Duration(milliseconds: 300), widget.host.onDone);
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final size = math.min(box.maxWidth * 0.7, box.maxHeight * 0.78);
        final enough = widget.step.tooLong != null && _c.value >= _need && !_done;
        return Center(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Semantics(
              key: const ValueKey('hold'),
              container: true,
              button: true,
              label: widget.step.prop,
              excludeSemantics: true,
              child: Listener(
                behavior: HitTestBehavior.opaque,
                onPointerDown: (_) => _down(),
                onPointerUp: (_) => _up(),
                onPointerCancel: (_) => _up(),
                child: SizedBox(
                  width: size,
                  height: size,
                  child: Stack(fit: StackFit.expand, children: [
                    CustomPaint(painter: _Ring(_c.value, _need, enough ? Paper.green : Paper.coral)),
                    Padding(
                      padding: EdgeInsets.all(size * 0.12),
                      child: AnimatedScale(
                        scale: _c.isAnimating || enough ? 1.06 : 1,
                        duration: const Duration(milliseconds: 200),
                        child: StepPic(_done && widget.step.result != null ? widget.step.result! : widget.step.prop, mood: widget.host.mood),
                      ),
                    ),
                  ]),
                ),
              ),
            ),
            const SizedBox(height: 10),
            Text(_done ? Strings.done : (enough ? Strings.letGo : Strings.holdOn), style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: Paper.inkSoft)),
          ]),
        );
      });
}

class _Ring extends CustomPainter {
  _Ring(this.t, this.need, this.color);

  final double t, need;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final r = size.shortestSide / 2 - 6;
    final c = size.center(Offset.zero);
    canvas.drawCircle(c, r, Paint()..color = Colors.white.withValues(alpha: 0.7));
    canvas.drawCircle(
        c,
        r,
        Paint()
          ..color = Paper.edge
          ..style = PaintingStyle.stroke
          ..strokeWidth = 10);
    canvas.drawArc(
        Rect.fromCircle(center: c, radius: r),
        -math.pi / 2,
        2 * math.pi * t,
        false,
        Paint()
          ..color = color
          ..style = PaintingStyle.stroke
          ..strokeCap = StrokeCap.round
          ..strokeWidth = 10);
    if (need < 1) {
      // The "just right" mark.
      final a = -math.pi / 2 + 2 * math.pi * need;
      canvas.drawCircle(c + Offset(math.cos(a), math.sin(a)) * r, 9, Paint()..color = Paper.green);
    }
  }

  @override
  bool shouldRepaint(_Ring old) => old.t != t || old.color != color || old.need != need;
}
