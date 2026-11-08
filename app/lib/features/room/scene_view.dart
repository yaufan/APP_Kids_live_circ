import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/scenes.dart';

/// One scene filling the page (docs/art.md): the background, the things at
/// their boxes in z order, the decorations earned, the child's puppet at the
/// stand and the buddy beside it. A finger on it reports the thing under it.
class SceneView extends StatelessWidget {
  const SceneView({
    super.key,
    required this.data,
    required this.avatar,
    required this.buddy,
    this.states = const {},
    this.decos = 0,
    this.sky = Paper.sky,
    this.glow,
    this.glowAvatar = false,
    this.sign,
    this.mood = Mood.normal,
    this.pose = 'stand',
    this.buddyPose = 'stand',
    this.dim = 0,
    this.onTapThing,
    this.onTapAvatar,
    this.onTapBuddy,
    this.wiggle = const {},
  });

  final SceneData data;
  final Avatar avatar;
  final Buddy buddy;

  /// Which state each thing with states shows (missing: the first).
  final Map<String, String> states;
  final int decos;
  final Color sky;

  /// The thing to light up (the one to tap now).
  final String? glow;
  final bool glowAvatar;

  /// A little picture over the puppet's head (a happening's sign).
  final String? sign;
  final Mood mood;
  final String pose;
  final String buddyPose;

  /// 0 (day) to 1 (the house asleep).
  final double dim;
  final void Function(Thing t)? onTapThing;
  final VoidCallback? onTapAvatar;
  final VoidCallback? onTapBuddy;

  /// Things wiggling right now (tapped), by id → a counter.
  final Map<String, int> wiggle;

  static const sceneW = 600.0, sceneH = 800.0;

  /// How much of each side may be cut off to fill the page.
  static const crop = 0.06;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, box) {
      // Fill the height; a little of the sides may be cut off (nothing
      // to tap sits in the outer 6%).
      final scale = math.min(box.maxWidth / (sceneW * (1 - 2 * crop)), box.maxHeight / sceneH);
      final w = sceneW * scale, h = sceneH * scale;
      Rect rectOf(SceneBox b, {bool feet = false}) => Rect.fromLTWH(b.left * w, (feet ? b.standTop : b.top) * h, b.w * w, b.h * h);
      final stand = rectOf(data.stand, feet: true);
      // The puppet fits inside the stand box (docs/art.md: the things
      // keep out of it).
      final avatarW = math.min(stand.width, stand.height * 200 / 260), avatarH = avatarW * 260 / 200;
      final avatarRect = Rect.fromLTWH(stand.center.dx - avatarW / 2, stand.bottom - avatarH, avatarW, avatarH);
      final buddyBox = rectOf(data.buddy, feet: true);
      final buddySide = math.min(buddyBox.width, buddyBox.height) * 1.15;
      var buddyRect = Rect.fromLTWH(buddyBox.center.dx - buddySide / 2, buddyBox.bottom - buddySide, buddySide, buddySide);
      final things = [...data.things]..sort((a, b) => a.z.compareTo(b.z));
      // The buddy steps to the other side of the child when it would stand
      // in front of the thing to tap.
      final glowing = glow == null ? null : data.thing(glow!);
      if (glowing != null && buddyRect.overlaps(rectOf(glowing.box))) {
        final mirrored = 2 * stand.center.dx - buddyRect.center.dx;
        buddyRect = Rect.fromCenter(center: Offset(mirrored.clamp(buddySide / 2, w - buddySide / 2), buddyRect.center.dy), width: buddySide, height: buddySide);
      }
      final shownDecos = data.decos.take(decos.clamp(0, data.decos.length)).toList();

      Thing? hit(Offset p) {
        Thing? best;
        for (final t in things) {
          if (rectOf(t.box).contains(p) && (best == null || t.z >= best.z)) best = t;
        }
        return best;
      }

      final kids = <Widget>[
        Positioned.fill(
          child: Art(ArtPath.scene(data.scene, 'bg'), fit: BoxFit.fill, sky: sky),
        ),
        for (final d in shownDecos)
          Positioned.fromRect(
            rect: rectOf(d.box),
            child: Art(ArtPath.scene(data.scene, d.id), sky: sky),
          ),
      ];
      var avatarDrawn = false;
      void drawAvatar() {
        if (avatarDrawn) return;
        avatarDrawn = true;
        kids.addAll([
          if (glowAvatar) Positioned.fromRect(rect: avatarRect.inflate(avatarRect.width * 0.3), child: const Glow()),
          Positioned.fromRect(
            rect: buddyRect,
            child: Bob(amount: 2, phase: 0.3, child: Art(ArtPath.buddy(buddy, buddyPose))),
          ),
          Positioned.fromRect(
            key: const ValueKey('avatar'),
            rect: avatarRect,
            child: Bob(
              amount: 2,
              child: Puppet(avatar: avatar, pose: pose, mood: mood),
            ),
          ),
          if (sign != null)
            Positioned(
              left: avatarRect.center.dx + avatarRect.width * 0.25,
              top: avatarRect.top - avatarRect.width * 0.55,
              width: avatarRect.width * 0.6,
              height: avatarRect.width * 0.6,
              child: Bob(
                amount: 4,
                child: Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                    boxShadow: const [BoxShadow(color: Color(0x336B4F33), offset: Offset(0, 3), blurRadius: 6)],
                  ),
                  child: Art(ArtPath.of(sign!)),
                ),
              ),
            ),
        ]);
      }

      for (final t in things) {
        if (t.z >= 50) drawAvatar();
        final r = rectOf(t.box);
        final state = states[t.id] ?? t.states.first;
        Widget pic = Art(ArtPath.scene(data.scene, t.file(state)), sky: sky);
        if (wiggle[t.id] != null) pic = Wiggle(trigger: wiggle[t.id]!, child: pic);
        if (glow == t.id) {
          kids.add(Positioned.fromRect(rect: r.inflate(math.min(r.width, r.height) * 0.35), child: const Glow()));
          pic = Bob(amount: 5, child: pic);
        }
        kids.add(Positioned.fromRect(key: ValueKey('thing-${t.id}'), rect: r, child: pic));
      }
      drawAvatar();
      if (dim > 0) {
        kids.add(
          Positioned.fill(
            child: IgnorePointer(
              child: ColoredBox(color: Paper.night.withValues(alpha: 0.75 * dim)),
            ),
          ),
        );
      }

      Offset? down;
      return ClipRect(
        child: OverflowBox(
          alignment: Alignment.bottomCenter,
          minWidth: 0,
          maxWidth: w,
          minHeight: 0,
          maxHeight: h,
          child: SizedBox(
            width: w,
            height: h,
            child: Listener(
              behavior: HitTestBehavior.opaque,
              onPointerDown: (e) => down = e.localPosition,
              onPointerUp: (e) {
                final d = down;
                down = null;
                if (d == null || (e.localPosition - d).distance > 24) return;
                final p = e.localPosition;
                if (avatarRect.contains(p)) {
                  onTapAvatar?.call();
                  return;
                }
                if (glowing != null && rectOf(glowing.box).contains(p)) {
                  onTapThing?.call(glowing);
                  return;
                }
                // The buddy is small and often stands in front of furniture:
                // only its middle counts, the furniture gets the rest.
                final t = hit(p);
                if (buddyRect.deflate(buddyRect.width * 0.2).contains(p) || (t == null && buddyRect.contains(p))) {
                  onTapBuddy?.call();
                  return;
                }
                if (t != null) onTapThing?.call(t);
              },
              onPointerCancel: (_) => down = null,
              child: Stack(clipBehavior: Clip.none, children: kids),
            ),
          ),
        ),
      );
    },
  );
}

/// A soft yellow glow that pulses: the thing to tap now.
class Glow extends StatefulWidget {
  const Glow({super.key});

  @override
  State<Glow> createState() => _GlowState();
}

class _GlowState extends State<Glow> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 800))..repeat(reverse: true);

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => IgnorePointer(
    child: AnimatedBuilder(
      animation: _c,
      builder: (_, _) => DecoratedBox(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(
            colors: [
              Paper.glow.withValues(alpha: 0.8),
              Paper.glow.withValues(alpha: 0.35 + 0.25 * _c.value),
              Paper.glow.withValues(alpha: 0),
            ],
            stops: const [0.2, 0.6, 1],
          ),
        ),
      ),
    ),
  );
}
