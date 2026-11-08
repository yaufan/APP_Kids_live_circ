import 'dart:convert';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../core/content.dart';
import '../core/providers.dart';
import '../core/scenes.dart';
import 'theme.dart';

/// A drawing from assets/art/ (nothing at all if it is missing).
class Art extends StatelessWidget {
  const Art(this.path, {super.key, this.fit = BoxFit.contain, this.sky, this.tokens});

  final String path;
  final BoxFit fit;

  /// Paints `#SKY` in the file with this colour (the sky in the windows).
  final Color? sky;

  /// Other placeholders to paint (`#ROOM_living` in the little house).
  final Map<String, Color>? tokens;

  @override
  Widget build(BuildContext context) {
    // Every scene picture may hold the sky placeholder (windows, doors):
    // paint it, or flutter_svg refuses the whole file.
    final map = <String, Color>{if (path.contains('/scenes/')) '#SKY': Paper.sky, '#SKY': ?sky, ...?tokens};
    if (map.isEmpty) {
      return SvgPicture.asset(path, fit: fit, excludeFromSemantics: true, errorBuilder: (_, _, _) => const SizedBox.expand());
    }
    return SvgPicture(TokenLoader(path, map), fit: fit, excludeFromSemantics: true, errorBuilder: (_, _, _) => const SizedBox.expand());
  }
}

/// Loads an SVG asset with its placeholder colours painted.
class TokenLoader extends SvgAssetLoader {
  const TokenLoader(super.assetName, this.tokens);

  final Map<String, Color> tokens;

  static String hex(Color c) => '#${(c.toARGB32() & 0xFFFFFF).toRadixString(16).padLeft(6, '0')}';

  @override
  String provideSvg(ByteData? message) {
    var text = message == null ? '' : utf8.decode(message.buffer.asUint8List(message.offsetInBytes, message.lengthInBytes), allowMalformed: true);
    for (final e in tokens.entries) {
      text = text.replaceAll(e.key, hex(e.value));
    }
    return text;
  }

  int get _tokensHash => Object.hashAll([for (final e in tokens.entries) e.key, for (final e in tokens.entries) e.value.toARGB32()]);

  @override
  SvgCacheKey cacheKey(BuildContext? context) => SvgCacheKey(keyData: Object.hash(assetName, _tokensHash), colorMapper: colorMapper, theme: getTheme(context));

  // The picture must reload when the colours change (the base class
  // compares the asset name only).
  @override
  bool operator ==(Object other) => other is TokenLoader && other.assetName == assetName && other._tokensHash == _tokensHash;

  @override
  int get hashCode => Object.hash(assetName, _tokensHash);
}

/// The child's paper puppet: body, head, face and hair laid over each
/// other (docs/art.md avatar/), 200×260 with the feet at the bottom.
class Puppet extends StatelessWidget {
  const Puppet({super.key, required this.avatar, this.pose = 'stand', this.mood = Mood.normal, this.flip = false});

  final Avatar avatar;
  final String pose;
  final Mood mood;
  final bool flip;

  /// Where the head sits in each pose (assets/art/avatar/layout.json; the
  /// head, face and hair files are drawn for `stand`). test/art_test.dart
  /// checks these agree with the file.
  static const headAt = {'stand': Offset(100, 98), 'sit': Offset(100, 98), 'lie': Offset(66, 190)};

  @override
  Widget build(BuildContext context) {
    final shift = headAt[pose]! - headAt['stand']!;
    return Transform.flip(
      flipX: flip,
      child: AspectRatio(
        aspectRatio: 200 / 260,
        child: LayoutBuilder(builder: (_, box) {
          final k = box.maxWidth / 200;
          final head = Transform.translate(
            offset: shift * k,
            child: Stack(fit: StackFit.expand, children: [
              Art(ArtPath.avatarHead(avatar.skin)),
              Art(ArtPath.avatarFace(mood)),
              Art(ArtPath.avatarHair(avatar.hair)),
            ]),
          );
          return Stack(fit: StackFit.expand, clipBehavior: Clip.none, children: [Art(ArtPath.avatarBody(pose, avatar.shirt)), head]);
        }),
      ),
    );
  }
}

/// The child's puppet as set up, in the pose and mood asked for.
class Me extends ConsumerWidget {
  const Me({super.key, this.pose = 'stand', this.mood = Mood.normal, this.flip = false});

  final String pose;
  final Mood mood;
  final bool flip;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final avatar = ref.watch(gameProvider.select((g) => g.profile?.avatar ?? const Avatar()));
    return Puppet(avatar: avatar, pose: pose, mood: mood, flip: flip);
  }
}

/// The buddy as set up, in a pose.
class MyBuddy extends ConsumerWidget {
  const MyBuddy({super.key, this.pose = 'stand'});

  final String pose;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final b = ref.watch(gameProvider.select((g) => g.profile?.buddy ?? Buddy.dog));
    return Art(ArtPath.buddy(b, pose));
  }
}

/// Shrinks a little while pressed and clicks.
class Pressable extends ConsumerStatefulWidget {
  const Pressable({super.key, required this.child, this.onTap, this.sound = 'tap'});

  final Widget child;
  final VoidCallback? onTap;
  final String? sound;

  @override
  ConsumerState<Pressable> createState() => _PressableState();
}

class _PressableState extends ConsumerState<Pressable> {
  var _down = false;

  @override
  Widget build(BuildContext context) {
    final enabled = widget.onTap != null;
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      excludeFromSemantics: true,
      onTapDown: enabled ? (_) => setState(() => _down = true) : null,
      onTapCancel: enabled ? () => setState(() => _down = false) : null,
      onTapUp: enabled ? (_) => setState(() => _down = false) : null,
      onTap: enabled
          ? () {
              final s = widget.sound;
              if (s != null) ref.read(soundsProvider).play(s);
              widget.onTap!();
            }
          : null,
      child: AnimatedScale(scale: _down ? 0.93 : 1, duration: const Duration(milliseconds: 90), child: widget.child),
    );
  }
}

/// A white card with a soft blue edge under it.
class PaperCard extends StatelessWidget {
  const PaperCard({super.key, this.child, this.padding = EdgeInsets.zero, this.color = Paper.card, this.ring, this.radius = 22});

  final Widget? child;
  final EdgeInsets padding;
  final Color color;
  final Color? ring;
  final double radius;

  @override
  Widget build(BuildContext context) => AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: padding,
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(radius),
          border: ring == null ? null : Border.all(color: ring!, width: 4),
          boxShadow: const [BoxShadow(color: Color(0x2E6B4F33), offset: Offset(0, 5), blurRadius: 12)],
        ),
        child: child,
      );
}

/// A round button with an icon.
class RoundButton extends StatelessWidget {
  const RoundButton({super.key, required this.label, required this.icon, this.onTap, this.size = 54, this.color, this.sound = 'tap', this.child});

  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final double size;

  /// Filled with this colour (white if not).
  final Color? color;
  final String? sound;

  /// Drawn instead of the icon.
  final Widget? child;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: true,
        label: label,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: sound,
          child: Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              color: color ?? Colors.white,
              shape: BoxShape.circle,
              boxShadow: const [BoxShadow(color: Color(0x336B4F33), offset: Offset(0, 4), blurRadius: 8)],
            ),
            child: child ?? Icon(icon, size: size * 0.52, color: color == null ? Paper.ink : Colors.white),
          ),
        ),
      );
}

/// A wide button with an icon and a word.
class WideButton extends StatelessWidget {
  const WideButton({super.key, required this.label, required this.icon, this.onTap, this.color = Paper.green, this.height = 62, this.sound = 'tap'});

  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final Color color;
  final double height;
  final String? sound;

  @override
  Widget build(BuildContext context) {
    final light = color == Colors.white;
    return Semantics(
      container: true,
      button: true,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        sound: sound,
        child: Container(
          height: height,
          padding: EdgeInsets.symmetric(horizontal: height * 0.45),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(height / 2),
            boxShadow: [BoxShadow(color: light ? const Color(0x336B4F33) : Color.lerp(color, Colors.black, 0.25)!, offset: const Offset(0, 5))],
          ),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            Icon(icon, size: height * 0.46, color: light ? Paper.green : Colors.white),
            const SizedBox(width: 10),
            Text(label, style: TextStyle(fontSize: height * 0.36, fontWeight: FontWeight.w700, color: light ? Paper.ink : Colors.white)),
          ]),
        ),
      ),
    );
  }
}

/// A pill with a game's name.
class Pill extends StatelessWidget {
  const Pill({super.key, required this.text, required this.color, this.size = 19});

  final String text;
  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) => Container(
        padding: EdgeInsets.symmetric(horizontal: size * 0.95, vertical: size * 0.32),
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(size * 2),
          boxShadow: [BoxShadow(color: Color.lerp(color, Colors.black, 0.2)!, offset: const Offset(0, 3))],
        ),
        child: Text(text, maxLines: 1, overflow: TextOverflow.fade, softWrap: false, style: TextStyle(fontSize: size, fontWeight: FontWeight.w700, color: Colors.white)),
      );
}

/// A speech bubble with a speaker: tap to hear it again.
class SpeakBubble extends StatelessWidget {
  const SpeakBubble({super.key, required this.text, this.onTap, this.size = 20, this.color = Paper.green});

  final String text;
  final VoidCallback? onTap;
  final double size;
  final Color color;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: onTap != null,
        label: text,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: null,
          child: PaperCard(
            radius: 26,
            padding: const EdgeInsets.fromLTRB(10, 8, 18, 8),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Container(
                width: size * 1.7,
                height: size * 1.7,
                decoration: BoxDecoration(color: color, shape: BoxShape.circle),
                child: Icon(Icons.volume_up_rounded, color: Colors.white, size: size),
              ),
              const SizedBox(width: 10),
              Flexible(child: Text(text, style: TextStyle(fontSize: size, fontWeight: FontWeight.w700, color: Paper.ink, height: 1.3))),
            ]),
          ),
        ),
      );
}

/// Shakes its child side to side once each time [trigger] changes.
class Wiggle extends StatefulWidget {
  const Wiggle({super.key, required this.trigger, required this.child, this.amount = 0.08});

  final int trigger;
  final Widget child;
  final double amount;

  @override
  State<Wiggle> createState() => _WiggleState();
}

class _WiggleState extends State<Wiggle> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));

  @override
  void didUpdateWidget(Wiggle old) {
    super.didUpdateWidget(old);
    if (old.trigger != widget.trigger) _c.forward(from: 0);
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _c,
        builder: (_, child) {
          final t = _c.value;
          return Transform.rotate(angle: math.sin(t * math.pi * 4) * (1 - t) * widget.amount, child: child);
        },
        child: widget.child,
      );
}

/// A gentle bob up and down.
class Bob extends StatefulWidget {
  const Bob({super.key, required this.child, this.phase = 0, this.amount = 4});

  final Widget child;
  final double phase;
  final double amount;

  @override
  State<Bob> createState() => _BobState();
}

class _BobState extends State<Bob> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1800))..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _c,
        builder: (_, child) => Transform.translate(offset: Offset(0, math.sin((_c.value + widget.phase) * 2 * math.pi) * widget.amount), child: child),
        child: widget.child,
      );
}

/// Dots: [done] of [count] filled (found ones get a tick).
class FoundDots extends StatelessWidget {
  const FoundDots({super.key, required this.count, required this.done, this.color = Paper.green, this.size = 22});

  final int count;
  final int done;
  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(size)),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          for (var i = 0; i < count; i++)
            AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              margin: const EdgeInsets.symmetric(horizontal: 2.5),
              width: size,
              height: size,
              decoration: BoxDecoration(color: i < done ? color : const Color(0xFFEDE3D6), shape: BoxShape.circle),
              child: i < done ? Icon(Icons.check_rounded, size: size * 0.75, color: Colors.white) : null,
            ),
        ]),
      );
}

/// Up to three stars.
class Stars extends StatelessWidget {
  const Stars({super.key, required this.count, this.size = 18});

  final int count;
  final double size;

  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
        for (var i = 0; i < 3; i++) Icon(Icons.star_rounded, size: size, color: i < count ? Paper.gold : const Color(0xFFE9DFD2)),
      ]);
}

/// The page's soft sky.
class Sky extends StatelessWidget {
  const Sky({super.key, required this.top, required this.bottom, required this.child});

  final Color top;
  final Color bottom;
  final Widget child;

  @override
  Widget build(BuildContext context) => DecoratedBox(
        decoration: BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [top, bottom])),
        child: child,
      );
}


/// A round picture button (a prop as its face).
class PicButton extends StatelessWidget {
  const PicButton({super.key, required this.label, required this.art, this.onTap, this.size = 64, this.ring, this.sound = 'tap'});

  final String label;
  final String art;
  final VoidCallback? onTap;
  final double size;
  final Color? ring;
  final String? sound;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: true,
        label: label,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: sound,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: size,
            height: size,
            padding: EdgeInsets.all(size * 0.12),
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              border: ring == null ? null : Border.all(color: ring!, width: 4),
              boxShadow: const [BoxShadow(color: Color(0x336B4F33), offset: Offset(0, 4), blurRadius: 8)],
            ),
            child: Art(art),
          ),
        ),
      );
}

/// Says a line out loud (if the parent left the voice on), with the
/// English after it when that is on.
void speak(WidgetRef ref, String zh, {String? en}) {
  final s = ref.read(gameProvider).settings;
  if (!s.voice) return;
  ref.read(voiceProvider).say(zh, en: s.english ? en : null);
}
