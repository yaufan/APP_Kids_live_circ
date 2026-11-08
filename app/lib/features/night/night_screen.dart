import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/providers.dart';
import '../../core/scenes.dart';
import '../../core/sounds.dart';

/// Bedtime (docs/design.md 「睡覺」): the whole house goes dark room by room,
/// the stickers of the day, a decoration if everything was done. A tap
/// brings the next morning.
class NightScreen extends ConsumerStatefulWidget {
  const NightScreen({super.key});

  @override
  ConsumerState<NightScreen> createState() => _NightScreenState();
}

class _NightScreenState extends ConsumerState<NightScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(seconds: 4))..forward();
  late final Sounds _sounds;
  var _ended = false;
  var _all = false;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.night);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final g = ref.read(gameProvider);
      final d = g.day!;
      _all = d.plan(g.settings).tasks.every(d.done.contains);
      ref.read(gameProvider.notifier).change((g) => g.endDay());
      _ended = true;
      _sounds.play('night');
      speak(ref, _all ? '${Strings.goodNight}${Strings.allDone}' : Strings.goodNight);
      if (_all) Future<void>.delayed(const Duration(milliseconds: 1500), () => _sounds.play('deco'));
      setState(() {});
    });
  }

  @override
  void dispose() {
    _c.dispose();
    _sounds.release(this);
    super.dispose();
  }

  void _morning() {
    if (!_ended) return;
    ref.read(gameProvider.notifier).newDay();
    ref.read(sceneProvider.notifier).go(Scene.bedroom);
    _sounds.play('light_on');
    speak(ref, Strings.newDay);
    context.go('/');
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final rooms = Scene.rooms;
    return Scaffold(
      backgroundColor: Paper.night,
      body: Semantics(
        key: const ValueKey('night'),
        button: true,
        label: Strings.nightTap,
        excludeSemantics: true,
        onTap: _morning,
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: _morning,
          child: SafeArea(
            child: Column(children: [
              const Spacer(),
              const Text(Strings.nightTitle, style: TextStyle(fontSize: 30, fontWeight: FontWeight.w700, color: Color(0xFFFFE9A8))),
              const SizedBox(height: 16),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: AnimatedBuilder(
                  animation: _c,
                  builder: (_, _) {
                    // Rooms go dark one after another.
                    final tokens = <String, Color>{};
                    for (var i = 0; i < rooms.length; i++) {
                      final dark = _c.value > (i + 1) / (rooms.length + 1);
                      tokens['#ROOM_${rooms[i].name}'] = dark ? const Color(0xFF3A4080) : Paper.yellow;
                    }
                    return AspectRatio(aspectRatio: 600 / 500, child: Art(ArtPath.reward('house_small'), tokens: tokens));
                  },
                ),
              ),
              const SizedBox(height: 18),
              if (_ended)
                Wrap(spacing: 6, children: [
                  for (final t in (g.history.isEmpty ? const <Task>[] : g.history.last.done)) SizedBox(width: 40, height: 40, child: Art(ArtPath.reward(t.sticker))),
                ]),
              if (_ended && _all)
                Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: PaperCard(
                    padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
                    child: Row(mainAxisSize: MainAxisSize.min, children: [
                      const Icon(Icons.card_giftcard_rounded, color: Paper.coral),
                      const SizedBox(width: 8),
                      Text(Strings.decoLine(g.decos), style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
                    ]),
                  ),
                ),
              const Spacer(),
              const Text(Strings.nightTap, style: TextStyle(fontSize: 18, color: Color(0xFFB9BEE8))),
              const SizedBox(height: 28),
            ]),
          ),
        ),
      ),
    );
  }
}
