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
import '../parent/parent_gate.dart';

/// The play time is up (docs/design.md 「每次玩多久」): the character sleeps,
/// the house is dark, and the child is sent to do it for real: 「換你去做了！」
/// Only a parent (through the gate) or an hour's wait lets play go on.
class RestScreen extends ConsumerStatefulWidget {
  const RestScreen({super.key});

  @override
  ConsumerState<RestScreen> createState() => _RestScreenState();
}

class _RestScreenState extends ConsumerState<RestScreen> {
  late final Sounds _sounds;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.rest);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _sounds.play('night');
      speak(ref, '${Strings.restTitle}，${Strings.restLine.replaceAll('\n', '')}');
    });
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  Future<void> _parent() async {
    if (!await showParentGate(context) || !mounted) return;
    ref.read(gameProvider.notifier).change((g) => g.playOn());
    ref.read(sessionStartProvider.notifier).restart();
    context.go('/');
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: Paper.night,
        body: Stack(children: [
          Positioned.fill(child: Art(ArtPath.scene(Scene.bedroom, 'bg'), fit: BoxFit.cover, sky: const Color(0xFF2B3470))),
          Positioned.fill(child: ColoredBox(color: Paper.night.withValues(alpha: 0.72))),
          const Positioned(top: 70, right: 40, child: Icon(Icons.nightlight_round, size: 64, color: Color(0xFFFFE9A8))),
          SafeArea(
            child: Column(children: [
              const Spacer(flex: 3),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: PaperCard(
                  padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
                  child: Column(mainAxisSize: MainAxisSize.min, children: [
                    const Text(Strings.restTitle, style: TextStyle(fontSize: 28, fontWeight: FontWeight.w700, color: Paper.ink)),
                    const SizedBox(height: 8),
                    const Text(Strings.restLine, textAlign: TextAlign.center, style: TextStyle(fontSize: 21, height: 1.5, color: Paper.ink)),
                  ]),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: 260,
                height: 170,
                child: Stack(children: [
                  const Positioned(left: 10, bottom: 0, width: 200, height: 160, child: Me(pose: 'lie', mood: Mood.sleepy)),
                  const Positioned(right: 0, bottom: 0, width: 70, height: 70, child: MyBuddy(pose: 'sleep')),
                  const Positioned(right: 30, top: 0, child: Text('z z z', style: TextStyle(fontFamily: PaperTheme.font, fontSize: 30, color: Color(0xFFFFE9A8), fontWeight: FontWeight.w700))),
                ]),
              ),
              const Spacer(flex: 2),
              Align(
                alignment: Alignment.bottomRight,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(0, 0, 18, 16),
                  child: Semantics(
                    container: true,
                    button: true,
                    label: Strings.parent,
                    excludeSemantics: true,
                    onTap: _parent,
                    child: GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: _parent,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.75), borderRadius: BorderRadius.circular(22)),
                        child: const Row(mainAxisSize: MainAxisSize.min, children: [
                          Icon(Icons.lock_outline_rounded, color: Paper.inkSoft, size: 20),
                          SizedBox(width: 6),
                          Text(Strings.parent, style: TextStyle(fontSize: 16, color: Paper.inkSoft)),
                        ]),
                      ),
                    ),
                  ),
                ),
              ),
            ]),
          ),
        ]),
      );
}
