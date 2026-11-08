import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/version.dart';
import '../../core/content.dart';
import '../../core/game.dart';
import '../../core/providers.dart';

/// Parent mode (after the gate): the child, the age, the play time, which
/// things a day has, sounds, the last days and ideas for doing it for real.
class ParentScreen extends ConsumerWidget {
  const ParentScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final g = ref.watch(gameProvider);
    final s = g.settings;
    final game = ref.read(gameProvider.notifier);
    final now = ref.read(clockProvider)();

    Widget section(String title, List<Widget> children) => Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Material(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(18, 14, 18, 12),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(title, style: const TextStyle(fontSize: 15, color: Paper.inkSoft, fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                ...children,
              ]),
            ),
          ),
        );

    Widget toggle(String label, bool value, void Function(bool)? set, {Key? key, String? note}) => SwitchListTile(
          key: key,
          contentPadding: EdgeInsets.zero,
          title: Text(label, style: const TextStyle(fontSize: 17)),
          subtitle: note == null ? null : Text(note, style: const TextStyle(fontSize: 13, color: Paper.inkSoft)),
          value: value,
          onChanged: set,
        );

    Widget chips<T>(List<T> values, T selected, String Function(T) label, void Function(T) pick, String keyOf) => Wrap(spacing: 8, runSpacing: 8, children: [
          for (final v in values)
            ChoiceChip(
              key: ValueKey('$keyOf-${v is Enum ? v.name : v}'),
              label: Text(label(v), style: const TextStyle(fontSize: 16)),
              selected: v == selected,
              onSelected: (_) => pick(v),
              selectedColor: const Color(0xFFFFE0B8),
              showCheckmark: false,
            ),
        ]);

    const note = TextStyle(fontSize: 14, height: 1.5, color: Paper.inkSoft);
    final skipped = <Task, int>{};
    for (final r in g.history) {
      for (final t in r.skipped) {
        skipped[t] = (skipped[t] ?? 0) + 1;
      }
    }
    final mostSkipped = skipped.entries.fold<MapEntry<Task, int>?>(null, (a, b) => a == null || b.value > a.value ? b : a);

    return Scaffold(
      backgroundColor: Paper.parentBg,
      appBar: AppBar(
        backgroundColor: Paper.parentBg,
        title: const Text(Strings.parentTitle),
        leading: IconButton(icon: const Icon(Icons.close_rounded), tooltip: Strings.back, onPressed: () => context.canPop() ? context.pop() : context.go('/')),
      ),
      body: ListView(padding: const EdgeInsets.fromLTRB(16, 8, 16, 32), children: [
        section(Strings.child, [
          Text('${Strings.changeName}：${g.profile?.name ?? Profile.defaultName}，${g.profile?.buddy.zh ?? ''}', style: const TextStyle(fontSize: 17)),
          const SizedBox(height: 8),
          OutlinedButton.icon(key: const ValueKey('re-setup'), onPressed: () => context.go('/setup'), icon: const Icon(Icons.face_rounded), label: const Text(Strings.changeLook)),
        ]),
        section(Strings.age, [
          chips(Level.values, s.level, Strings.levelLine, (v) => game.settings((x) => x.copyWith(level: v)), 'level'),
          const SizedBox(height: 10),
          const Text(Strings.ageNote, style: note),
        ]),
        section(Strings.playTime, [
          chips(Settings.minuteChoices, s.minutes, Strings.minutes, (v) => game.settings((x) => x.copyWith(minutes: v)), 'minutes'),
          const SizedBox(height: 10),
          const Text(Strings.playTimeNote, style: note),
          if (g.resting(now)) ...[
            const SizedBox(height: 10),
            const Text(Strings.resting, style: TextStyle(fontSize: 16)),
            const SizedBox(height: 6),
            FilledButton(
              key: const ValueKey('play-on'),
              onPressed: () {
                game.change((g) => g.playOn());
                ref.read(sessionStartProvider.notifier).restart();
                context.go('/');
              },
              child: const Text(Strings.playOn),
            ),
          ],
        ]),
        section(Strings.routines, [
          for (final t in Task.optional)
            toggle(t.zh, !s.off.contains(t), (on) => game.settings((x) => x.copyWith(off: on ? ({...x.off}..remove(t)) : {...x.off, t})), key: ValueKey('routine-${t.name}')),
          const SizedBox(height: 4),
          const Text(Strings.routinesNote, style: note),
        ]),
        section(Strings.sound, [
          toggle(Strings.music, s.music, (v) => game.settings((x) => x.copyWith(music: v)), key: const ValueKey('music')),
          toggle(Strings.effects, s.sounds, (v) => game.settings((x) => x.copyWith(sounds: v)), key: const ValueKey('effects')),
          toggle(Strings.voice, s.voice, (v) => game.settings((x) => x.copyWith(voice: v)), key: const ValueKey('voice')),
          toggle(Strings.english, s.english, (v) => game.settings((x) => x.copyWith(english: v)), key: const ValueKey('english')),
        ]),
        section(Strings.progress, [
          if (g.history.isEmpty) const Text(Strings.progressNone, style: note),
          for (final r in g.history.reversed)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Text(Strings.progressLine(r.weekday, r.done.length, r.done.length + r.skipped.length), style: const TextStyle(fontSize: 16)),
            ),
          if (mostSkipped != null) ...[
            const SizedBox(height: 4),
            Text(Strings.skippedMost(mostSkipped.key, mostSkipped.value), style: const TextStyle(fontSize: 15, color: Paper.coral, fontWeight: FontWeight.w700)),
          ],
          const SizedBox(height: 6),
          Text('${Strings.totalCount(g.stickerCount)}，${Strings.decoLine(g.decos)}', style: note),
        ]),
        section(Strings.together, [
          for (final t in Strings.tips)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Padding(padding: EdgeInsets.only(top: 3), child: Icon(Icons.favorite_rounded, size: 16, color: Paper.coral)),
                const SizedBox(width: 8),
                Expanded(child: Text(t, style: const TextStyle(fontSize: 16, height: 1.45))),
              ]),
            ),
        ]),
        section(Strings.fullVersion, [
          const Text(Strings.fullNote, style: note),
          toggle(Strings.fullSwitch, s.full, (v) => game.settings((x) => x.copyWith(full: v)), key: const ValueKey('full')),
        ]),
        section(Strings.about, [
          const Text(Strings.privacy, style: TextStyle(fontSize: 15, height: 1.5)),
          const SizedBox(height: 6),
          Text(Strings.version(appVersion), style: note),
        ]),
      ]),
    );
  }
}
