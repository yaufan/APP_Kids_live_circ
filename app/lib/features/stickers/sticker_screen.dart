import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/game.dart';
import '../../core/providers.dart';
import '../../core/scenes.dart';

/// The sticker chart (docs/design.md 「獎勵」): today's things in a grid with
/// a sticker on each one done, the little house with the rooms decorated so
/// far, and the height chart.
class StickerScreen extends ConsumerWidget {
  const StickerScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final g = ref.watch(gameProvider);
    final day = g.day;
    final plan = day?.plan(g.settings);
    final name = g.profile?.name ?? Profile.defaultName;
    final done = day?.done ?? const <Task>{};
    final rooms = {for (final s in Scene.rooms) '#ROOM_${s.name}': g.decosIn(s) > 0 ? Paper.yellow : (g.decos > 0 ? Paper.page : Paper.edge)};
    return Scaffold(
      backgroundColor: Paper.page,
      body: Stack(children: [
        Positioned.fill(child: Art(ArtPath.reward('chart'), fit: BoxFit.cover)),
        SafeArea(
          child: Column(children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
              child: Row(children: [
                RoundButton(label: Strings.back, icon: Icons.arrow_back_rounded, size: 46, onTap: () => context.canPop() ? context.pop() : context.go('/')),
                const SizedBox(width: 10),
                Expanded(child: Pill(text: Strings.stickerTitle(name), color: Paper.gold, size: 20)),
              ]),
            ),
            Expanded(
              child: ListView(padding: const EdgeInsets.fromLTRB(20, 16, 20, 24), children: [
                if (plan != null) ...[
                  Text(Strings.todayCount(plan.tasks.where(done.contains).length, plan.length), style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 8),
                  GridView.count(
                    crossAxisCount: 4,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    mainAxisSpacing: 8,
                    crossAxisSpacing: 8,
                    children: [
                      for (final t in plan.tasks)
                        Semantics(
                          key: ValueKey('sticker-${t.name}'),
                          label: '${t.zh}${done.contains(t) ? ' 完成' : ''}',
                          child: Pressable(
                            onTap: () => speak(ref, t.zh, en: t.en),
                            child: Column(children: [
                              Expanded(child: done.contains(t) ? Bob(amount: 2, child: Art(ArtPath.reward(t.sticker))) : Opacity(opacity: 0.7, child: Art(ArtPath.reward('sticker_blank')))),
                              Text(t.zh, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, color: Paper.inkSoft)),
                            ]),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(Strings.totalCount(g.stickerCount), style: const TextStyle(fontSize: 16, color: Paper.inkSoft)),
                ],
                const SizedBox(height: 18),
                Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Expanded(
                    flex: 5,
                    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      AspectRatio(aspectRatio: 600 / 500, child: Art(ArtPath.reward('house_small'), tokens: rooms)),
                      const SizedBox(height: 4),
                      Text(Strings.decoLine(g.decos), style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
                    ]),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: Column(children: [
                      AspectRatio(
                        aspectRatio: 100 / 600 * 2.2,
                        child: Stack(children: [
                          Positioned.fill(child: Art(ArtPath.reward('height'))),
                          Positioned(
                            left: 0,
                            right: 0,
                            bottom: 20 + 18.0 * g.height,
                            child: SizedBox(height: 44, child: Me(mood: Mood.happy)),
                          ),
                        ]),
                      ),
                      Text(Strings.heightLine(g.height), textAlign: TextAlign.center, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
                    ]),
                  ),
                ]),
              ]),
            ),
          ]),
        ),
      ]),
    );
  }
}
